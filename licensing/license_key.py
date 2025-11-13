"""
License Key Management

Generate and parse license keys for Neon Works engine.
Supports multiple license tiers and hardware binding.
"""

import hashlib
import hmac
import secrets
import base64
import json
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict, field


class LicenseTier(Enum):
    """License tier levels"""
    FREE = "free"
    INDIE = "indie"
    PROFESSIONAL = "professional"


@dataclass
class LicenseKey:
    """
    License key data structure

    Format: NWXX-AAAA-BBBB-CCCC-DDDD
    - NW: Neon Works prefix
    - XX: Version/tier code
    - Rest: Encoded license data + checksum
    """
    tier: LicenseTier
    licensee_name: str
    licensee_email: str
    issue_date: str
    expiry_date: Optional[str] = None  # None = perpetual
    hardware_id: Optional[str] = None  # None = floating license
    max_exports: Optional[int] = None  # None = unlimited
    custom_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['tier'] = self.tier.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LicenseKey':
        """Create from dictionary"""
        data['tier'] = LicenseTier(data['tier'])
        return cls(**data)

    def is_expired(self) -> bool:
        """Check if license has expired"""
        if self.expiry_date is None:
            return False

        expiry = datetime.fromisoformat(self.expiry_date)
        return datetime.now() > expiry

    def is_hardware_locked(self) -> bool:
        """Check if license is locked to specific hardware"""
        return self.hardware_id is not None

    def get_tier_name(self) -> str:
        """Get human-readable tier name"""
        return {
            LicenseTier.FREE: "Free (Open Source)",
            LicenseTier.INDIE: "Indie License",
            LicenseTier.PROFESSIONAL: "Professional License"
        }[self.tier]


class LicenseKeyGenerator:
    """Generate and validate license keys"""

    def __init__(self, secret_key: Optional[str] = None):
        """
        Initialize license key generator.

        Args:
            secret_key: Secret key for HMAC signing (keep this secret!)
                       If None, generates a random key (for testing only)
        """
        if secret_key is None:
            # For production, this should be a fixed secret stored securely
            secret_key = secrets.token_hex(32)

        self.secret_key = secret_key.encode('utf-8')

    def generate(
        self,
        tier: LicenseTier,
        licensee_name: str,
        licensee_email: str,
        duration_days: Optional[int] = None,
        hardware_id: Optional[str] = None,
        max_exports: Optional[int] = None,
        custom_data: Optional[Dict[str, Any]] = None
    ) -> tuple[str, LicenseKey]:
        """
        Generate a license key.

        Args:
            tier: License tier
            licensee_name: Name of licensee
            licensee_email: Email of licensee
            duration_days: License duration in days (None = perpetual)
            hardware_id: Hardware ID to lock to (None = floating)
            max_exports: Maximum number of exports (None = unlimited)
            custom_data: Additional custom data

        Returns:
            Tuple of (encoded_key, license_object)
        """
        issue_date = datetime.now().isoformat()

        if duration_days is not None:
            expiry_date = (datetime.now() + timedelta(days=duration_days)).isoformat()
        else:
            expiry_date = None

        license_data = LicenseKey(
            tier=tier,
            licensee_name=licensee_name,
            licensee_email=licensee_email,
            issue_date=issue_date,
            expiry_date=expiry_date,
            hardware_id=hardware_id,
            max_exports=max_exports,
            custom_data=custom_data or {}
        )

        # Encode license data
        encoded_key = self._encode_license(license_data)

        return encoded_key, license_data

    def validate(self, encoded_key: str) -> Optional[LicenseKey]:
        """
        Validate and decode a license key.

        Args:
            encoded_key: The encoded license key string

        Returns:
            LicenseKey object if valid, None if invalid
        """
        try:
            return self._decode_license(encoded_key)
        except Exception:
            return None

    def _encode_license(self, license_data: LicenseKey) -> str:
        """Encode license data into key string"""
        # Convert to JSON
        data_dict = license_data.to_dict()
        data_json = json.dumps(data_dict, separators=(',', ':'))
        data_bytes = data_json.encode('utf-8')

        # Create HMAC signature
        signature = hmac.new(
            self.secret_key,
            data_bytes,
            hashlib.sha256
        ).digest()[:16]  # Use first 16 bytes

        # Combine data + signature
        combined = data_bytes + signature

        # Base64 encode
        encoded = base64.urlsafe_b64encode(combined).decode('ascii')

        # Format as license key: NWXX-AAAA-BBBB-CCCC-DDDD...
        tier_code = {
            LicenseTier.FREE: 'FR',
            LicenseTier.INDIE: 'IN',
            LicenseTier.PROFESSIONAL: 'PR'
        }[license_data.tier]

        # Split into chunks of 4 characters
        chunks = ['NW' + tier_code]
        for i in range(0, len(encoded), 4):
            chunks.append(encoded[i:i+4])

        return '-'.join(chunks)

    def _decode_license(self, encoded_key: str) -> LicenseKey:
        """Decode license key string into license data"""
        # Remove dashes and prefix
        key_without_dashes = encoded_key.replace('-', '')

        if not key_without_dashes.startswith('NW'):
            raise ValueError("Invalid license key format")

        # Extract tier code
        tier_code = key_without_dashes[2:4]
        tier_map = {
            'FR': LicenseTier.FREE,
            'IN': LicenseTier.INDIE,
            'PR': LicenseTier.PROFESSIONAL
        }

        if tier_code not in tier_map:
            raise ValueError("Invalid license tier")

        # Get encoded data (skip NW and tier code)
        encoded_data = key_without_dashes[4:]

        # Base64 decode with proper padding
        try:
            # Add correct padding
            padding_needed = (4 - len(encoded_data) % 4) % 4
            encoded_data_padded = encoded_data + ('=' * padding_needed)
            combined = base64.urlsafe_b64decode(encoded_data_padded)
        except Exception as e:
            raise ValueError(f"Invalid license key encoding: {e}")

        # Split data and signature
        if len(combined) < 16:
            raise ValueError("Invalid license key length")

        data_bytes = combined[:-16]
        signature = combined[-16:]

        # Verify signature
        expected_signature = hmac.new(
            self.secret_key,
            data_bytes,
            hashlib.sha256
        ).digest()[:16]

        if not hmac.compare_digest(signature, expected_signature):
            raise ValueError("Invalid license key signature")

        # Parse JSON data
        try:
            data_json = data_bytes.decode('utf-8')
            data_dict = json.loads(data_json)
        except Exception:
            raise ValueError("Invalid license key data")

        # Create license object
        license_data = LicenseKey.from_dict(data_dict)

        # Verify tier matches
        if license_data.tier != tier_map[tier_code]:
            raise ValueError("License tier mismatch")

        return license_data


# Production secret key - KEEP THIS SECRET!
# In production, this should be stored in environment variable or secure config
PRODUCTION_SECRET_KEY = "NEON_WORKS_LICENSE_SECRET_KEY_2024_CHANGE_THIS_IN_PRODUCTION"


def get_production_generator() -> LicenseKeyGenerator:
    """Get the production license key generator"""
    return LicenseKeyGenerator(PRODUCTION_SECRET_KEY)
