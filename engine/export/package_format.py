"""
Neon Works Package Format (.nwdata)

Binary package format for distributing games with IP protection.

Format Specification:
===================

HEADER (64 bytes):
------------------
- Magic Number (4 bytes): "NWPK" (0x4E57504B)
- Format Version (2 bytes): uint16, currently 1
- Flags (2 bytes): uint16 bitfield
    - Bit 0: Encrypted (1 = encrypted, 0 = plain)
    - Bit 1: Compressed (1 = compressed, 0 = uncompressed)
    - Bits 2-15: Reserved for future use
- File Count (4 bytes): uint32, number of files in package
- Index Offset (8 bytes): uint64, byte offset to file index
- Data Offset (8 bytes): uint64, byte offset to file data section
- Encryption Method (1 byte): 0 = None, 1 = AES-256-GCM
- Compression Method (1 byte): 0 = None, 1 = zlib
- Reserved (34 bytes): Reserved for future use

FILE INDEX (variable):
---------------------
For each file:
- Filename Length (2 bytes): uint16
- Filename (variable): UTF-8 encoded string
- File Offset (8 bytes): uint64, offset from data section start
- File Size (8 bytes): uint64, size of file data
- Original Size (8 bytes): uint64, uncompressed size (0 if not compressed)
- File Hash (32 bytes): SHA-256 hash of original file content
- Flags (2 bytes): uint16 bitfield (reserved)

FILE DATA (variable):
--------------------
Raw file data (compressed and/or encrypted as per header flags)

ENCRYPTION DETAILS:
------------------
When encrypted (Flag bit 0 = 1):
- Algorithm: AES-256-GCM
- Key derivation: PBKDF2-HMAC-SHA256 with 100,000 iterations
- Each file has its own IV (prepended to file data, 12 bytes)
- Authentication tag (appended to file data, 16 bytes)
- Salt stored in package metadata (32 bytes after header)

COMPRESSION DETAILS:
-------------------
When compressed (Flag bit 1 = 1):
- Algorithm: zlib with default compression level
- Applied per-file before encryption
- Original size stored in index for decompression
"""

import struct
import hashlib
from typing import NamedTuple, Optional
from pathlib import Path


# Constants
MAGIC_NUMBER = b'NWPK'
FORMAT_VERSION = 1
HEADER_SIZE = 64

# Flag bits
FLAG_ENCRYPTED = 0x0001
FLAG_COMPRESSED = 0x0002

# Encryption/Compression methods
ENC_NONE = 0
ENC_AES256_GCM = 1
COMP_NONE = 0
COMP_ZLIB = 1


class PackageHeader(NamedTuple):
    """Package file header"""
    magic: bytes
    version: int
    flags: int
    file_count: int
    index_offset: int
    data_offset: int
    encryption_method: int
    compression_method: int

    @property
    def is_encrypted(self) -> bool:
        return bool(self.flags & FLAG_ENCRYPTED)

    @property
    def is_compressed(self) -> bool:
        return bool(self.flags & FLAG_COMPRESSED)

    def pack(self) -> bytes:
        """Pack header to bytes"""
        data = struct.pack(
            '<4sHHIQQBB34x',
            self.magic,
            self.version,
            self.flags,
            self.file_count,
            self.index_offset,
            self.data_offset,
            self.encryption_method,
            self.compression_method
        )
        assert len(data) == HEADER_SIZE
        return data

    @classmethod
    def unpack(cls, data: bytes) -> 'PackageHeader':
        """Unpack header from bytes"""
        if len(data) < HEADER_SIZE:
            raise ValueError(f"Invalid header size: {len(data)} (expected {HEADER_SIZE})")

        values = struct.unpack('<4sHHIQQBB34x', data[:HEADER_SIZE])

        magic = values[0]
        if magic != MAGIC_NUMBER:
            raise ValueError(f"Invalid magic number: {magic} (expected {MAGIC_NUMBER})")

        return cls(
            magic=magic,
            version=values[1],
            flags=values[2],
            file_count=values[3],
            index_offset=values[4],
            data_offset=values[5],
            encryption_method=values[6],
            compression_method=values[7]
        )


class FileEntry(NamedTuple):
    """File entry in package index"""
    filename: str
    offset: int
    size: int
    original_size: int
    file_hash: bytes
    flags: int

    def pack(self) -> bytes:
        """Pack file entry to bytes"""
        filename_bytes = self.filename.encode('utf-8')
        filename_len = len(filename_bytes)

        return struct.pack(
            f'<H{filename_len}sQQQ32sH',
            filename_len,
            filename_bytes,
            self.offset,
            self.size,
            self.original_size,
            self.file_hash,
            self.flags
        )

    @classmethod
    def unpack(cls, data: bytes, offset: int = 0) -> tuple['FileEntry', int]:
        """
        Unpack file entry from bytes

        Returns:
            Tuple of (FileEntry, bytes_consumed)
        """
        # Read filename length
        filename_len = struct.unpack('<H', data[offset:offset+2])[0]
        offset += 2

        # Read filename
        filename = data[offset:offset+filename_len].decode('utf-8')
        offset += filename_len

        # Read rest of entry
        values = struct.unpack('<QQQ32sH', data[offset:offset+58])
        offset += 58

        return cls(
            filename=filename,
            offset=values[0],
            size=values[1],
            original_size=values[2],
            file_hash=values[3],
            flags=values[4]
        ), offset


def compute_file_hash(file_path: Path) -> bytes:
    """Compute SHA-256 hash of file"""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.digest()


def compute_data_hash(data: bytes) -> bytes:
    """Compute SHA-256 hash of data"""
    return hashlib.sha256(data).digest()
