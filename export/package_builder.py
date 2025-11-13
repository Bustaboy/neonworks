"""
Package Builder

Builds .nwdata packages from game projects.
Handles compression, encryption, and file packaging.
"""

import os
import secrets
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

from .package_format import (COMP_NONE, COMP_ZLIB, ENC_AES256_GCM, ENC_NONE,
                             FLAG_COMPRESSED, FLAG_ENCRYPTED, FORMAT_VERSION,
                             HEADER_SIZE, MAGIC_NUMBER, FileEntry,
                             PackageHeader, compute_data_hash,
                             compute_file_hash)


@dataclass
class PackageConfig:
    """Configuration for package building"""

    compress: bool = True
    encrypt: bool = False
    password: Optional[str] = None
    exclude_patterns: List[str] = None

    def __post_init__(self):
        if self.exclude_patterns is None:
            self.exclude_patterns = [
                "__pycache__",
                "*.pyc",
                ".git",
                ".gitignore",
                "*.tmp",
                ".DS_Store",
            ]

        if self.encrypt and not self.password:
            raise ValueError("Password required for encryption")

        if self.encrypt and not CRYPTO_AVAILABLE:
            raise RuntimeError(
                "Encryption requested but cryptography library not available. "
                "Install with: pip install cryptography"
            )


class PackageBuilder:
    """Builds .nwdata packages from project directories"""

    def __init__(self, config: PackageConfig):
        self.config = config
        self.files: List[tuple[str, Path]] = []
        self._salt: Optional[bytes] = None
        self._key: Optional[bytes] = None

    def add_file(self, relative_path: str, file_path: Path):
        """Add a file to the package"""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        self.files.append((relative_path, file_path))

    def add_directory(self, directory: Path, base_path: Optional[Path] = None):
        """Recursively add all files from a directory"""
        if base_path is None:
            base_path = directory

        for item in directory.rglob("*"):
            if item.is_file() and not self._should_exclude(item):
                relative_path = str(item.relative_to(base_path))
                # Normalize path separators to forward slashes
                relative_path = relative_path.replace(os.sep, "/")
                self.add_file(relative_path, item)

    def _should_exclude(self, path: Path) -> bool:
        """Check if file should be excluded based on patterns"""
        import fnmatch

        path_str = str(path)

        for pattern in self.config.exclude_patterns:
            if fnmatch.fnmatch(path_str, f"*{pattern}*"):
                return True
            if fnmatch.fnmatch(path.name, pattern):
                return True

        return False

    def build(self, output_path: Path) -> Dict[str, Any]:
        """
        Build the package file

        Returns:
            Dictionary with build statistics
        """
        if not self.files:
            raise ValueError("No files added to package")

        # Prepare encryption if needed
        if self.config.encrypt:
            self._prepare_encryption()

        # Build package
        with open(output_path, "wb") as f:
            # Reserve space for header
            f.write(b"\x00" * HEADER_SIZE)

            # Write salt if encrypted
            if self.config.encrypt:
                f.write(self._salt)

            # Calculate where index starts
            index_offset = f.tell()

            # Build file index and collect file data
            file_entries = []
            file_data_list = []
            total_original_size = 0
            total_compressed_size = 0

            for relative_path, file_path in self.files:
                # Read file
                with open(file_path, "rb") as file_f:
                    file_data = file_f.read()

                original_size = len(file_data)
                total_original_size += original_size
                file_hash = compute_data_hash(file_data)

                # Compress if needed
                compressed_size = original_size
                if self.config.compress:
                    file_data = zlib.compress(file_data)
                    compressed_size = len(file_data)

                # Encrypt if needed
                if self.config.encrypt:
                    file_data = self._encrypt_data(file_data)
                    compressed_size = len(file_data)  # Update size after encryption

                total_compressed_size += compressed_size

                # Create file entry
                entry = FileEntry(
                    filename=relative_path,
                    offset=0,  # Will be calculated later
                    size=compressed_size,
                    original_size=original_size,
                    file_hash=file_hash,
                    flags=0,
                )

                file_entries.append(entry)
                file_data_list.append(file_data)

            # Write file index
            index_data = b""
            for entry in file_entries:
                index_data += entry.pack()

            f.write(index_data)
            data_offset = f.tell()

            # Write file data and update offsets
            current_offset = 0
            updated_entries = []

            for entry, file_data in zip(file_entries, file_data_list):
                f.write(file_data)

                # Update entry with correct offset
                updated_entry = FileEntry(
                    filename=entry.filename,
                    offset=current_offset,
                    size=entry.size,
                    original_size=entry.original_size,
                    file_hash=entry.file_hash,
                    flags=entry.flags,
                )
                updated_entries.append(updated_entry)
                current_offset += len(file_data)

            # Create header
            flags = 0
            if self.config.compress:
                flags |= FLAG_COMPRESSED
            if self.config.encrypt:
                flags |= FLAG_ENCRYPTED

            header = PackageHeader(
                magic=MAGIC_NUMBER,
                version=FORMAT_VERSION,
                flags=flags,
                file_count=len(self.files),
                index_offset=index_offset,
                data_offset=data_offset,
                encryption_method=ENC_AES256_GCM if self.config.encrypt else ENC_NONE,
                compression_method=COMP_ZLIB if self.config.compress else COMP_NONE,
            )

            # Go back and write header
            f.seek(0)
            f.write(header.pack())

            # Go back and rewrite index with correct offsets
            f.seek(index_offset)
            for entry in updated_entries:
                f.write(entry.pack())

        # Calculate compression ratio
        compression_ratio = (
            (1 - total_compressed_size / total_original_size) * 100
            if total_original_size > 0
            else 0
        )

        return {
            "file_count": len(self.files),
            "original_size": total_original_size,
            "package_size": total_compressed_size,
            "compression_ratio": compression_ratio,
            "encrypted": self.config.encrypt,
            "compressed": self.config.compress,
        }

    def _prepare_encryption(self):
        """Prepare encryption key from password"""
        if not CRYPTO_AVAILABLE:
            raise RuntimeError("Cryptography library not available")

        # Generate random salt
        self._salt = secrets.token_bytes(32)

        # Derive key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self._salt,
            iterations=100000,
        )
        self._key = kdf.derive(self.config.password.encode("utf-8"))

    def _encrypt_data(self, data: bytes) -> bytes:
        """Encrypt data using AES-256-GCM"""
        if not self._key:
            raise RuntimeError("Encryption not prepared")

        # Generate random IV
        iv = secrets.token_bytes(12)

        # Encrypt
        aesgcm = AESGCM(self._key)
        ciphertext = aesgcm.encrypt(iv, data, None)

        # Return IV + ciphertext (ciphertext includes auth tag)
        return iv + ciphertext


def build_package(
    project_path: Path,
    output_path: Path,
    compress: bool = True,
    encrypt: bool = False,
    password: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convenience function to build a package

    Args:
        project_path: Path to project directory
        output_path: Output .nwdata file path
        compress: Enable compression
        encrypt: Enable encryption
        password: Password for encryption (required if encrypt=True)

    Returns:
        Build statistics dictionary
    """
    config = PackageConfig(compress=compress, encrypt=encrypt, password=password)

    builder = PackageBuilder(config)
    builder.add_directory(project_path)

    return builder.build(output_path)
