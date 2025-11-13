"""
Package Loader

Loads files from .nwdata packages at runtime.
Handles decompression and decryption.
"""

import zlib
from pathlib import Path
from typing import Optional, Dict, List

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

from .package_format import (
    PackageHeader, FileEntry, HEADER_SIZE, compute_data_hash
)


class PackageLoader:
    """Loads files from .nwdata packages"""

    def __init__(self, package_path: Path, password: Optional[str] = None):
        self.package_path = package_path
        self.password = password
        self.header: Optional[PackageHeader] = None
        self.file_index: Dict[str, FileEntry] = {}
        self._key: Optional[bytes] = None
        self._loaded = False

    def load_index(self):
        """Load package header and file index"""
        if self._loaded:
            return

        with open(self.package_path, 'rb') as f:
            # Read header
            header_data = f.read(HEADER_SIZE)
            self.header = PackageHeader.unpack(header_data)

            # Read salt if encrypted
            if self.header.is_encrypted:
                if not self.password:
                    raise ValueError("Password required for encrypted package")

                if not CRYPTO_AVAILABLE:
                    raise RuntimeError("Cryptography library not available for decryption")

                salt = f.read(32)
                self._prepare_decryption(salt)

            # Read file index
            f.seek(self.header.index_offset)
            index_size = self.header.data_offset - self.header.index_offset
            index_data = f.read(index_size)

            # Parse file entries
            offset = 0
            for _ in range(self.header.file_count):
                entry, bytes_read = FileEntry.unpack(index_data, offset)
                self.file_index[entry.filename] = entry
                offset = bytes_read

        self._loaded = True

    def _prepare_decryption(self, salt: bytes):
        """Prepare decryption key from password"""
        if not CRYPTO_AVAILABLE:
            raise RuntimeError("Cryptography library not available")

        # Derive key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        self._key = kdf.derive(self.password.encode('utf-8'))

    def list_files(self) -> List[str]:
        """List all files in package"""
        if not self._loaded:
            self.load_index()

        return list(self.file_index.keys())

    def has_file(self, filename: str) -> bool:
        """Check if file exists in package"""
        if not self._loaded:
            self.load_index()

        return filename in self.file_index

    def load_file(self, filename: str, verify_hash: bool = True) -> bytes:
        """
        Load a file from the package

        Args:
            filename: Relative path to file in package
            verify_hash: Verify file integrity with SHA-256 hash

        Returns:
            File contents as bytes

        Raises:
            FileNotFoundError: If file not in package
            ValueError: If hash verification fails
        """
        if not self._loaded:
            self.load_index()

        if filename not in self.file_index:
            raise FileNotFoundError(f"File not found in package: {filename}")

        entry = self.file_index[filename]

        # Read file data
        with open(self.package_path, 'rb') as f:
            f.seek(self.header.data_offset + entry.offset)
            file_data = f.read(entry.size)

        # Decrypt if needed
        if self.header.is_encrypted:
            file_data = self._decrypt_data(file_data)

        # Decompress if needed
        if self.header.is_compressed:
            file_data = zlib.decompress(file_data)

        # Verify hash
        if verify_hash:
            actual_hash = compute_data_hash(file_data)
            if actual_hash != entry.file_hash:
                raise ValueError(f"Hash verification failed for {filename}")

        return file_data

    def _decrypt_data(self, data: bytes) -> bytes:
        """Decrypt data using AES-256-GCM"""
        if not self._key:
            raise RuntimeError("Decryption not prepared")

        # Extract IV and ciphertext
        iv = data[:12]
        ciphertext = data[12:]

        # Decrypt
        aesgcm = AESGCM(self._key)
        try:
            plaintext = aesgcm.decrypt(iv, ciphertext, None)
        except Exception as e:
            raise ValueError(f"Decryption failed (wrong password?): {e}")

        return plaintext

    def extract_file(self, filename: str, output_path: Path, verify_hash: bool = True):
        """Extract a file from package to disk"""
        data = self.load_file(filename, verify_hash=verify_hash)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(data)

    def extract_all(self, output_dir: Path, verify_hash: bool = True):
        """Extract all files from package"""
        if not self._loaded:
            self.load_index()

        for filename in self.file_index:
            output_path = output_dir / filename
            self.extract_file(filename, output_path, verify_hash=verify_hash)

    def get_info(self) -> Dict:
        """Get package information"""
        if not self._loaded:
            self.load_index()

        return {
            'version': self.header.version,
            'file_count': self.header.file_count,
            'encrypted': self.header.is_encrypted,
            'compressed': self.header.is_compressed,
            'encryption_method': self.header.encryption_method,
            'compression_method': self.header.compression_method,
        }


# Global package loader instance for runtime use
_global_loader: Optional[PackageLoader] = None


def set_global_loader(loader: PackageLoader):
    """Set the global package loader for runtime use"""
    global _global_loader
    _global_loader = loader


def get_global_loader() -> Optional[PackageLoader]:
    """Get the global package loader"""
    return _global_loader


def is_running_from_package() -> bool:
    """Check if currently running from a package"""
    return _global_loader is not None
