#!/usr/bin/env python3
"""
Test script for licensing system

Tests license generation, validation, hardware ID, and export blocking.
"""

import sys
import tempfile
import shutil
from pathlib import Path

# Add engine to path
sys.path.insert(0, str(Path(__file__).parent / 'engine'))

from licensing.license_key import LicenseKeyGenerator, LicenseTier, get_production_generator
from licensing.hardware_id import get_hardware_id, get_machine_info
from licensing.license_validator import LicenseValidator


def test_hardware_id():
    """Test hardware ID generation"""
    print("=" * 60)
    print("Test 1: Hardware ID Generation")
    print("=" * 60)

    hw_id = get_hardware_id()
    print(f"Hardware ID: {hw_id}")
    print(f"Length: {len(hw_id)} characters")

    # Should be consistent across calls
    hw_id2 = get_hardware_id()
    assert hw_id == hw_id2, "Hardware ID should be consistent"
    print("✓ Hardware ID is consistent across calls")

    # Get machine info
    info = get_machine_info()
    print(f"\nMachine Info:")
    for key, value in info.items():
        print(f"  {key}: {value}")

    print("\n✓ Test passed!\n")
    return True


def test_license_generation():
    """Test license key generation and validation"""
    print("=" * 60)
    print("Test 2: License Key Generation")
    print("=" * 60)

    generator = get_production_generator()

    # Generate licenses for each tier
    tiers = [
        (LicenseTier.FREE, "Free User"),
        (LicenseTier.INDIE, "Indie Developer"),
        (LicenseTier.PROFESSIONAL, "Pro Studio")
    ]

    for tier, name in tiers:
        print(f"\nGenerating {tier.value} license...")

        key, license_data = generator.generate(
            tier=tier,
            licensee_name=name,
            licensee_email=f"{name.lower().replace(' ', '.')}@example.com",
            duration_days=None  # Perpetual
        )

        print(f"  Key: {key[:40]}...")
        print(f"  Tier: {license_data.get_tier_name()}")
        print(f"  Licensee: {license_data.licensee_name}")

        # Validate the key
        validated = generator.validate(key)
        assert validated is not None, f"Failed to validate {tier.value} key"
        assert validated.tier == tier, "Tier mismatch"
        assert validated.licensee_name == name, "Name mismatch"

        print(f"  ✓ Validation successful")

    print("\n✓ All license tiers tested successfully!\n")
    return True


def test_hardware_locked_license():
    """Test hardware-locked license generation"""
    print("=" * 60)
    print("Test 3: Hardware-Locked License")
    print("=" * 60)

    generator = get_production_generator()
    hw_id = get_hardware_id()

    print(f"Hardware ID: {hw_id}")

    # Generate hardware-locked license
    key, license_data = generator.generate(
        tier=LicenseTier.INDIE,
        licensee_name="Test User",
        licensee_email="test@example.com",
        hardware_id=hw_id
    )

    print(f"\nGenerated hardware-locked license:")
    print(f"  Key: {key[:40]}...")
    print(f"  Hardware ID: {license_data.hardware_id[:16]}...")

    # Validate
    validated = generator.validate(key)
    assert validated is not None, "Validation failed"
    assert validated.is_hardware_locked(), "Should be hardware locked"
    assert validated.hardware_id == hw_id, "Hardware ID mismatch"

    print("  ✓ Hardware-locked license validated")

    print("\n✓ Test passed!\n")
    return True


def test_license_expiry():
    """Test license expiration"""
    print("=" * 60)
    print("Test 4: License Expiration")
    print("=" * 60)

    generator = get_production_generator()

    # Generate license with 30-day expiry
    key, license_data = generator.generate(
        tier=LicenseTier.INDIE,
        licensee_name="Trial User",
        licensee_email="trial@example.com",
        duration_days=30
    )

    print(f"Generated 30-day trial license")
    print(f"  Issue date: {license_data.issue_date}")
    print(f"  Expiry date: {license_data.expiry_date}")
    print(f"  Is expired: {license_data.is_expired()}")

    assert not license_data.is_expired(), "Should not be expired yet"
    print("  ✓ License is active")

    # Generate expired license (negative days)
    key_expired, license_expired = generator.generate(
        tier=LicenseTier.INDIE,
        licensee_name="Expired User",
        licensee_email="expired@example.com",
        duration_days=-1  # Yesterday
    )

    assert license_expired.is_expired(), "Should be expired"
    print("  ✓ Expired license detected correctly")

    print("\n✓ Test passed!\n")
    return True


def test_license_validator():
    """Test license validator with file operations"""
    print("=" * 60)
    print("Test 5: License Validator")
    print("=" * 60)

    # Create temp license file
    temp_dir = Path(tempfile.mkdtemp())
    license_file = temp_dir / 'test_license.key'

    try:
        validator = LicenseValidator(license_file)

        # Initially no license
        license = validator.get_license()
        assert license is None, "Should have no license initially"
        print("✓ No license found initially")

        # Generate and save a license
        generator = get_production_generator()
        key, license_data = generator.generate(
            tier=LicenseTier.INDIE,
            licensee_name="Test Developer",
            licensee_email="dev@example.com"
        )

        success = validator.save_license(key)
        assert success, "Failed to save license"
        print("✓ License saved successfully")

        # Load the license
        loaded = validator.get_license()
        assert loaded is not None, "Failed to load license"
        assert loaded.tier == LicenseTier.INDIE, "Tier mismatch"
        print("✓ License loaded successfully")

        # Check validation for export
        can_export, error_msg = validator.validate_for_export()
        assert can_export, f"Should be able to export: {error_msg}"
        print("✓ Export validation passed")

        # Get features
        features = validator.get_features()
        assert features['code_obfuscation'], "Indie should have obfuscation"
        assert features['commercial_use'], "Indie should allow commercial use"
        assert not features['cython_compilation'], "Indie shouldn't have Cython"
        print("✓ Feature flags correct for Indie tier")

        # Deactivate license
        validator.deactivate()
        license_after = validator.get_license()
        assert license_after is None, "License should be deactivated"
        print("✓ License deactivated successfully")

        print("\n✓ Test passed!\n")
        return True

    finally:
        shutil.rmtree(temp_dir)


def test_free_tier_export():
    """Test that free tier allows export with warnings"""
    print("=" * 60)
    print("Test 6: Free Tier Export Validation")
    print("=" * 60)

    temp_dir = Path(tempfile.mkdtemp())
    license_file = temp_dir / 'no_license.key'

    try:
        validator = LicenseValidator(license_file)

        # No license = free tier
        tier = validator.get_tier()
        assert tier == LicenseTier.FREE, "Should be free tier"
        print("✓ Free tier detected")

        # Check features
        features = validator.get_features()
        assert not features['remove_watermark'], "Free tier should have watermark"
        assert not features['commercial_use'], "Free tier no commercial use"
        print("✓ Free tier features correct")

        # Export validation should fail but with specific message
        can_export, error_msg = validator.validate_for_export()
        assert not can_export, "Free tier should show warning"
        assert "attribution watermark" in error_msg.lower(), "Should mention watermark"
        print("✓ Free tier export warning shown")

        print("\n✓ Test passed!\n")
        return True

    finally:
        shutil.rmtree(temp_dir)


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("NEON WORKS LICENSING SYSTEM TESTS")
    print("=" * 60 + "\n")

    tests = [
        test_hardware_id,
        test_license_generation,
        test_hardware_locked_license,
        test_license_expiry,
        test_license_validator,
        test_free_tier_export
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("=" * 60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
