"""
License Validator

Validates licenses at export time and enforces tier restrictions.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from .hardware_id import get_hardware_id, validate_hardware_id
from .license_key import (
    LicenseKey,
    LicenseKeyGenerator,
    LicenseTier,
    get_production_generator,
)


class LicenseValidator:
    """
    Validates licenses and enforces restrictions.

    Checks license files, validates keys, and enforces tier-specific limits.
    """

    def __init__(self, license_file: Optional[Path] = None):
        """
        Initialize validator.

        Args:
            license_file: Path to license file (default: ~/.neonworks/license.key)
        """
        if license_file is None:
            license_file = self._get_default_license_path()

        self.license_file = license_file
        self.generator = get_production_generator()
        self._cached_license: Optional[LicenseKey] = None

    def _get_default_license_path(self) -> Path:
        """Get default license file path"""
        if os.name == "nt":  # Windows
            base = Path(os.environ.get("APPDATA", Path.home()))
        else:  # Unix-like
            base = Path.home()

        license_dir = base / ".neonworks"
        license_dir.mkdir(parents=True, exist_ok=True)

        return license_dir / "license.key"

    def load_license(self) -> Optional[LicenseKey]:
        """
        Load and validate license from file.

        Returns:
            LicenseKey if valid, None if no license or invalid
        """
        if not self.license_file.exists():
            return None

        try:
            with open(self.license_file, "r") as f:
                encoded_key = f.read().strip()

            license_key = self.generator.validate(encoded_key)

            if license_key is None:
                return None

            # Cache for future calls
            self._cached_license = license_key
            return license_key

        except Exception:
            return None

    def save_license(self, encoded_key: str) -> bool:
        """
        Save license key to file.

        Args:
            encoded_key: Encoded license key string

        Returns:
            True if saved successfully
        """
        try:
            # Validate before saving
            license_key = self.generator.validate(encoded_key)
            if license_key is None:
                return False

            # Save to file
            self.license_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.license_file, "w") as f:
                f.write(encoded_key)

            self._cached_license = license_key
            return True

        except Exception as e:
            # For debugging - print error
            print(f"Error saving license: {e}")
            import traceback

            traceback.print_exc()
            return False

    def get_license(self) -> Optional[LicenseKey]:
        """
        Get current license (from cache or file).

        Returns:
            LicenseKey if valid, None otherwise
        """
        if self._cached_license is not None:
            return self._cached_license

        return self.load_license()

    def validate_for_export(self) -> tuple[bool, Optional[str]]:
        """
        Validate license for game export.

        Returns:
            Tuple of (is_valid, error_message)
            - (True, None) if export allowed
            - (False, reason) if export not allowed
        """
        license_key = self.get_license()

        # No license = Free tier only
        if license_key is None:
            return False, (
                "No license found. Free tier requires attribution watermark.\n"
                "Purchase a license at https://neonworks.dev/pricing to remove watermark.\n"
                "Or activate your license with: python -m neonworks.license activate YOUR-KEY"
            )

        # Check if expired
        if license_key.is_expired():
            expiry = datetime.fromisoformat(license_key.expiry_date)
            return (
                False,
                f"License expired on {expiry.strftime('%Y-%m-%d')}. Please renew your license.",
            )

        # Check hardware lock
        if license_key.is_hardware_locked():
            current_hw_id = get_hardware_id()
            if not validate_hardware_id(license_key.hardware_id):
                return False, (
                    f"License is locked to different hardware.\n"
                    f"Current hardware ID: {current_hw_id[:16]}...\n"
                    f"Licensed hardware ID: {license_key.hardware_id[:16]}...\n"
                    f"Contact support to transfer license."
                )

        # Check export limits
        if license_key.max_exports is not None:
            # TODO: Track export count
            # For now, just warn
            pass

        return True, None

    def get_tier(self) -> LicenseTier:
        """
        Get current license tier.

        Returns:
            LicenseTier (FREE if no valid license)
        """
        license_key = self.get_license()

        if license_key is None:
            return LicenseTier.FREE

        if license_key.is_expired():
            return LicenseTier.FREE

        return license_key.tier

    def get_features(self) -> Dict[str, bool]:
        """
        Get available features for current license tier.

        Returns:
            Dictionary of feature flags
        """
        tier = self.get_tier()

        if tier == LicenseTier.FREE:
            return {
                "export_games": True,
                "remove_watermark": False,
                "code_obfuscation": False,
                "cython_compilation": False,
                "commercial_use": False,
                "priority_support": False,
                "white_label": False,
            }

        elif tier == LicenseTier.INDIE:
            return {
                "export_games": True,
                "remove_watermark": True,
                "code_obfuscation": True,
                "cython_compilation": False,
                "commercial_use": True,
                "priority_support": False,
                "white_label": False,
            }

        elif tier == LicenseTier.PROFESSIONAL:
            return {
                "export_games": True,
                "remove_watermark": True,
                "code_obfuscation": True,
                "cython_compilation": True,
                "commercial_use": True,
                "priority_support": True,
                "white_label": True,
            }

        return {}

    def get_license_info(self) -> Dict[str, Any]:
        """
        Get human-readable license information.

        Returns:
            Dictionary with license details
        """
        license_key = self.get_license()

        if license_key is None:
            return {
                "tier": "Free (Open Source)",
                "licensee": "Unlicensed",
                "status": "No license",
                "features": self.get_features(),
            }

        status = "Active"
        if license_key.is_expired():
            status = "Expired"

        info = {
            "tier": license_key.get_tier_name(),
            "licensee": license_key.licensee_name,
            "email": license_key.licensee_email,
            "status": status,
            "issue_date": license_key.issue_date,
            "expiry_date": license_key.expiry_date or "Perpetual",
            "hardware_locked": license_key.is_hardware_locked(),
            "features": self.get_features(),
        }

        return info

    def deactivate(self) -> bool:
        """
        Deactivate (remove) current license.

        Returns:
            True if deactivated successfully
        """
        try:
            if self.license_file.exists():
                self.license_file.unlink()
            self._cached_license = None
            return True
        except Exception:
            return False


# Global validator instance
_global_validator: Optional[LicenseValidator] = None


def get_global_validator() -> LicenseValidator:
    """Get the global license validator instance"""
    global _global_validator
    if _global_validator is None:
        _global_validator = LicenseValidator()
    return _global_validator
