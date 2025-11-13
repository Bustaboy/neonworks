"""
Tests for export system
"""

import shutil
import tempfile
from pathlib import Path

import pytest

from neonworks.export.exporter import ExportConfig, ProjectExporter
from neonworks.export.package_builder import PackageBuilder, PackageConfig
from neonworks.export.package_format import (
    FORMAT_VERSION,
    MAGIC_NUMBER,
    FileEntry,
    PackageHeader,
)
from neonworks.export.package_loader import PackageLoader


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    temp = Path(tempfile.mkdtemp())
    yield temp
    shutil.rmtree(temp)


@pytest.fixture
def test_project(temp_dir):
    """Create a test project"""
    project_dir = temp_dir / "test_project"
    project_dir.mkdir()

    # Create project structure
    (project_dir / "assets").mkdir()
    (project_dir / "config").mkdir()

    # Create some test files
    (project_dir / "project.json").write_text('{"name": "Test Game"}')
    (project_dir / "config" / "settings.json").write_text('{"setting": "value"}')
    (project_dir / "assets" / "image.txt").write_text("fake image data")

    return project_dir


class TestPackageFormat:
    """Test package format specification"""

    def test_header_pack_unpack(self):
        """Test header serialization"""
        header = PackageHeader(
            magic=MAGIC_NUMBER,
            version=FORMAT_VERSION,
            flags=0,
            file_count=10,
            index_offset=1000,
            data_offset=2000,
            encryption_method=0,
            compression_method=1,
        )

        packed = header.pack()
        assert len(packed) == 64

        unpacked = PackageHeader.unpack(packed)
        assert unpacked.magic == MAGIC_NUMBER
        assert unpacked.version == FORMAT_VERSION
        assert unpacked.file_count == 10
        assert unpacked.index_offset == 1000
        assert unpacked.data_offset == 2000

    def test_file_entry_pack_unpack(self):
        """Test file entry serialization"""
        entry = FileEntry(
            filename="test/file.txt",
            offset=100,
            size=200,
            original_size=300,
            file_hash=b"0" * 32,
            flags=0,
        )

        packed = entry.pack()
        unpacked, bytes_consumed = FileEntry.unpack(packed, 0)

        assert unpacked.filename == entry.filename
        assert unpacked.offset == entry.offset
        assert unpacked.size == entry.size
        assert unpacked.original_size == entry.original_size
        assert unpacked.file_hash == entry.file_hash


class TestPackageBuilder:
    """Test package building"""

    def test_build_unencrypted_package(self, test_project, temp_dir):
        """Test building a basic unencrypted package"""
        config = PackageConfig(compress=True, encrypt=False)

        builder = PackageBuilder(config)
        builder.add_directory(test_project)

        output_path = temp_dir / "test.nwdata"
        stats = builder.build(output_path)

        assert output_path.exists()
        assert stats["file_count"] == 3
        assert stats["compressed"] is True
        assert stats["encrypted"] is False

    def test_build_encrypted_package(self, test_project, temp_dir):
        """Test building an encrypted package"""
        config = PackageConfig(
            compress=True, encrypt=True, password="test_password_123"
        )

        builder = PackageBuilder(config)
        builder.add_directory(test_project)

        output_path = temp_dir / "test_encrypted.nwdata"
        stats = builder.build(output_path)

        assert output_path.exists()
        assert stats["encrypted"] is True

    def test_compression_reduces_size(self, test_project, temp_dir):
        """Test that compression actually reduces size"""
        # Create a file with compressible data
        (test_project / "compressible.txt").write_text("A" * 10000)

        # Build without compression
        config_no_comp = PackageConfig(compress=False, encrypt=False)
        builder_no_comp = PackageBuilder(config_no_comp)
        builder_no_comp.add_directory(test_project)
        output_no_comp = temp_dir / "no_comp.nwdata"
        stats_no_comp = builder_no_comp.build(output_no_comp)

        # Build with compression
        config_comp = PackageConfig(compress=True, encrypt=False)
        builder_comp = PackageBuilder(config_comp)
        builder_comp.add_directory(test_project)
        output_comp = temp_dir / "comp.nwdata"
        stats_comp = builder_comp.build(output_comp)

        # Compressed should be smaller
        assert stats_comp["package_size"] < stats_no_comp["package_size"]


class TestPackageLoader:
    """Test package loading"""

    def test_load_unencrypted_package(self, test_project, temp_dir):
        """Test loading files from unencrypted package"""
        # Build package
        config = PackageConfig(compress=True, encrypt=False)
        builder = PackageBuilder(config)
        builder.add_directory(test_project)
        package_path = temp_dir / "test.nwdata"
        builder.build(package_path)

        # Load package
        loader = PackageLoader(package_path)
        loader.load_index()

        # Test file listing
        files = loader.list_files()
        assert "project.json" in files
        assert "config/settings.json" in files

        # Test file loading
        data = loader.load_file("project.json")
        assert b"Test Game" in data

    def test_load_encrypted_package(self, test_project, temp_dir):
        """Test loading files from encrypted package"""
        password = "secure_password_456"

        # Build package
        config = PackageConfig(compress=True, encrypt=True, password=password)
        builder = PackageBuilder(config)
        builder.add_directory(test_project)
        package_path = temp_dir / "encrypted.nwdata"
        builder.build(package_path)

        # Load with correct password
        loader = PackageLoader(package_path, password=password)
        loader.load_index()

        data = loader.load_file("project.json")
        assert b"Test Game" in data

    def test_wrong_password_fails(self, test_project, temp_dir):
        """Test that wrong password fails decryption"""
        password = "correct_password"

        # Build package
        config = PackageConfig(compress=True, encrypt=True, password=password)
        builder = PackageBuilder(config)
        builder.add_directory(test_project)
        package_path = temp_dir / "encrypted.nwdata"
        builder.build(package_path)

        # Try to load with wrong password
        loader = PackageLoader(package_path, password="wrong_password")
        loader.load_index()

        with pytest.raises(ValueError, match="Decryption failed"):
            loader.load_file("project.json")

    def test_extract_all(self, test_project, temp_dir):
        """Test extracting all files from package"""
        # Build package
        config = PackageConfig(compress=True, encrypt=False)
        builder = PackageBuilder(config)
        builder.add_directory(test_project)
        package_path = temp_dir / "test.nwdata"
        builder.build(package_path)

        # Extract all
        extract_dir = temp_dir / "extracted"
        loader = PackageLoader(package_path)
        loader.extract_all(extract_dir)

        # Verify files
        assert (extract_dir / "project.json").exists()
        assert (extract_dir / "config" / "settings.json").exists()


class TestProjectExporter:
    """Test complete export pipeline"""

    def test_export_package_only(self, test_project, temp_dir):
        """Test exporting package only"""
        config = ExportConfig(
            project_path=test_project,
            output_dir=temp_dir / "export",
            app_name="TestGame",
            version="1.0.0",
            create_executable=False,
            create_installer=False,
        )

        exporter = ProjectExporter(config)
        results = exporter.export()

        assert "package" in results
        assert results["package"]["path"].exists()
        assert results["package"]["file_count"] == 3

    def test_export_with_encryption(self, test_project, temp_dir):
        """Test exporting with encryption"""
        config = ExportConfig(
            project_path=test_project,
            output_dir=temp_dir / "export",
            app_name="TestGame",
            version="1.0.0",
            encrypt=True,
            password="test123",
            create_executable=False,
            create_installer=False,
        )

        exporter = ProjectExporter(config)
        results = exporter.export()

        assert results["package"]["encrypted"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
