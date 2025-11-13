#!/usr/bin/env python3
"""
Simple test script for export system
Tests basic functionality without encryption (avoids cryptography issues)
"""

import sys
import tempfile
import shutil
from pathlib import Path

# Add engine to path
sys.path.insert(0, str(Path(__file__).parent / 'engine'))

from export.package_builder import PackageBuilder, PackageConfig
from export.package_loader import PackageLoader


def test_basic_package():
    """Test building and loading a basic package"""
    print("=" * 60)
    print("Testing Basic Package Build and Load")
    print("=" * 60)

    # Create temp directories
    temp_dir = Path(tempfile.mkdtemp())
    project_dir = temp_dir / 'test_project'
    project_dir.mkdir()

    try:
        # Create test files
        print("\n1. Creating test project...")
        (project_dir / 'project.json').write_text('{"name": "Test Game", "version": "1.0"}')
        (project_dir / 'config').mkdir()
        (project_dir / 'config' / 'settings.json').write_text('{"setting": "value"}')
        (project_dir / 'assets').mkdir()
        (project_dir / 'assets' / 'test.txt').write_text('Test asset data')
        print("   ✓ Created 3 test files")

        # Build package (no encryption)
        print("\n2. Building package (compressed, no encryption)...")
        config = PackageConfig(
            compress=True,
            encrypt=False
        )

        builder = PackageBuilder(config)
        builder.add_directory(project_dir)

        package_path = temp_dir / 'test.nwdata'
        stats = builder.build(package_path)

        print(f"   ✓ Package created: {package_path}")
        print(f"   ✓ Files: {stats['file_count']}")
        print(f"   ✓ Original size: {stats['original_size']:,} bytes")
        print(f"   ✓ Package size: {stats['package_size']:,} bytes")
        print(f"   ✓ Compression ratio: {stats['compression_ratio']:.1f}%")

        # Load package
        print("\n3. Loading package...")
        loader = PackageLoader(package_path)
        loader.load_index()

        files = loader.list_files()
        print(f"   ✓ Found {len(files)} files in package:")
        for f in files:
            print(f"      - {f}")

        # Load and verify file
        print("\n4. Loading file from package...")
        data = loader.load_file('project.json')
        content = data.decode('utf-8')
        print(f"   ✓ Loaded project.json: {content}")

        # Verify content
        assert 'Test Game' in content
        print("   ✓ Content verification passed")

        # Test extraction
        print("\n5. Extracting all files...")
        extract_dir = temp_dir / 'extracted'
        loader.extract_all(extract_dir)

        extracted_files = list(extract_dir.rglob('*'))
        print(f"   ✓ Extracted {len([f for f in extracted_files if f.is_file()])} files")

        # Verify extracted content
        extracted_project = extract_dir / 'project.json'
        assert extracted_project.exists()
        assert 'Test Game' in extracted_project.read_text()
        print("   ✓ Extraction verification passed")

        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Cleanup
        shutil.rmtree(temp_dir)


def test_neon_collapse_export():
    """Test exporting the actual neon_collapse project"""
    print("\n" + "=" * 60)
    print("Testing Neon Collapse Project Export")
    print("=" * 60)

    project_path = Path('/home/user/neon-collapse/projects/neon_collapse')
    if not project_path.exists():
        print("   ⚠ Neon Collapse project not found, skipping")
        return True

    temp_dir = Path(tempfile.mkdtemp())

    try:
        print("\n1. Building package for neon_collapse...")
        config = PackageConfig(
            compress=True,
            encrypt=False
        )

        builder = PackageBuilder(config)
        builder.add_directory(project_path)

        package_path = temp_dir / 'neon_collapse.nwdata'
        stats = builder.build(package_path)

        print(f"   ✓ Package created: {package_path}")
        print(f"   ✓ Files: {stats['file_count']}")
        print(f"   ✓ Original size: {stats['original_size'] / 1024:.2f} KB")
        print(f"   ✓ Package size: {stats['package_size'] / 1024:.2f} KB")
        print(f"   ✓ Compression: {stats['compression_ratio']:.1f}%")

        print("\n2. Verifying package can be loaded...")
        loader = PackageLoader(package_path)
        loader.load_index()

        files = loader.list_files()
        print(f"   ✓ Package contains {len(files)} files")

        # Try to load project.json
        if 'project.json' in files:
            data = loader.load_file('project.json')
            print(f"   ✓ Successfully loaded project.json ({len(data)} bytes)")
        else:
            print("   ℹ project.json not in package root")

        print("\n" + "=" * 60)
        print("✓ NEON COLLAPSE EXPORT TEST PASSED")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        shutil.rmtree(temp_dir)


if __name__ == '__main__':
    success = True

    # Test 1: Basic functionality
    if not test_basic_package():
        success = False

    # Test 2: Real project
    if not test_neon_collapse_export():
        success = False

    sys.exit(0 if success else 1)
