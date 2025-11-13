#!/usr/bin/env python3
"""
Neon Works License Manager CLI

Manage engine licenses, activate keys, check status, and generate test licenses.
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add engine to path
sys.path.insert(0, str(Path(__file__).parent))

from licensing.license_key import (
    LicenseKeyGenerator,
    LicenseTier,
    get_production_generator,
)
from licensing.license_validator import LicenseValidator, get_global_validator
from licensing.hardware_id import get_hardware_id, get_machine_info


def cmd_activate(args):
    """Activate a license key"""
    validator = get_global_validator()

    print("Activating Neon Works License...")
    print(f"License key: {args.key[:10]}...")

    if validator.save_license(args.key):
        print("\n✓ License activated successfully!")

        # Show license info
        info = validator.get_license_info()
        print(f"\nLicense Details:")
        print(f"  Tier: {info['tier']}")
        print(f"  Licensee: {info['licensee']}")
        print(f"  Status: {info['status']}")

        if info["expiry_date"] != "Perpetual":
            print(f"  Expires: {info['expiry_date']}")

        print(f"\nEnabled Features:")
        for feature, enabled in info["features"].items():
            status = "✓" if enabled else "✗"
            print(f"  {status} {feature.replace('_', ' ').title()}")

        return 0
    else:
        print("\n✗ License activation failed!")
        print("The license key is invalid or corrupted.")
        return 1


def cmd_status(args):
    """Show license status"""
    validator = get_global_validator()

    print("=" * 60)
    print("Neon Works Engine - License Status")
    print("=" * 60)

    info = validator.get_license_info()

    print(f"\nTier: {info['tier']}")
    print(f"Licensee: {info['licensee']}")
    print(f"Status: {info['status']}")

    if "email" in info:
        print(f"Email: {info['email']}")

    if "issue_date" in info:
        issue = datetime.fromisoformat(info["issue_date"])
        print(f"Issued: {issue.strftime('%Y-%m-%d')}")

    if "expiry_date" in info:
        print(f"Expires: {info['expiry_date']}")

    if "hardware_locked" in info and info["hardware_locked"]:
        print(f"Hardware Locked: Yes")

    print(f"\nEnabled Features:")
    for feature, enabled in info["features"].items():
        status = "✓" if enabled else "✗"
        feature_name = feature.replace("_", " ").title()
        print(f"  {status} {feature_name}")

    # Check if can export
    can_export, error = validator.validate_for_export()

    print(f"\nExport Status: {'✓ Ready' if can_export else '✗ Restricted'}")
    if error:
        print(f"\n{error}")

    print("\n" + "=" * 60)

    return 0


def cmd_deactivate(args):
    """Deactivate current license"""
    validator = get_global_validator()

    print("Deactivating Neon Works License...")

    if validator.deactivate():
        print("✓ License deactivated successfully!")
        print("\nYou can reactivate with: python license_cli.py activate YOUR-KEY")
        return 0
    else:
        print("✗ No license to deactivate")
        return 1


def cmd_hardware_id(args):
    """Show hardware ID"""
    hw_id = get_hardware_id()

    print("=" * 60)
    print("Hardware ID for License Binding")
    print("=" * 60)
    print(f"\nHardware ID: {hw_id}")
    print("\nProvide this ID when purchasing a hardware-locked license.")

    if args.verbose:
        print("\nDetailed Machine Information:")
        info = get_machine_info()
        for key, value in info.items():
            if key != "hardware_id":
                print(f"  {key}: {value}")

    print("=" * 60)

    return 0


def cmd_generate(args):
    """Generate a test license key (for development/testing)"""
    if not args.confirm:
        print("WARNING: This generates test licenses with a default secret key.")
        print(
            "For production use, implement proper license server with secure key storage."
        )
        print("\nAdd --confirm to generate test license.")
        return 1

    print("Generating test license...")

    # Parse tier
    tier_map = {
        "free": LicenseTier.FREE,
        "indie": LicenseTier.INDIE,
        "professional": LicenseTier.PROFESSIONAL,
    }
    tier = tier_map.get(args.tier.lower())

    if tier is None:
        print(f"Invalid tier: {args.tier}")
        print("Valid tiers: free, indie, professional")
        return 1

    # Get hardware ID if hardware-locked
    hardware_id = None
    if args.hardware_locked:
        hardware_id = get_hardware_id()
        print(f"Hardware ID: {hardware_id}")

    # Generate license
    generator = get_production_generator()

    encoded_key, license_data = generator.generate(
        tier=tier,
        licensee_name=args.name,
        licensee_email=args.email,
        duration_days=args.duration if args.duration > 0 else None,
        hardware_id=hardware_id,
        max_exports=args.max_exports if args.max_exports > 0 else None,
    )

    print("\n" + "=" * 60)
    print("Generated License Key")
    print("=" * 60)
    print(f"\nLicense Key:\n{encoded_key}")
    print(f"\nTier: {license_data.get_tier_name()}")
    print(f"Licensee: {license_data.licensee_name}")
    print(f"Email: {license_data.licensee_email}")

    if license_data.expiry_date:
        expiry = datetime.fromisoformat(license_data.expiry_date)
        print(f"Expires: {expiry.strftime('%Y-%m-%d')}")
    else:
        print(f"Expires: Never (Perpetual)")

    if license_data.hardware_id:
        print(f"Hardware Locked: Yes ({license_data.hardware_id[:16]}...)")
    else:
        print(f"Hardware Locked: No (Floating license)")

    if license_data.max_exports:
        print(f"Max Exports: {license_data.max_exports}")

    print("\n" + "=" * 60)
    print("\nTo activate this license, run:")
    print(f"python license_cli.py activate {encoded_key}")
    print("=" * 60)

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Neon Works License Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Activate a license
  python license_cli.py activate NWIN-AAAA-BBBB-CCCC-DDDD...

  # Check license status
  python license_cli.py status

  # Get hardware ID for hardware-locked licenses
  python license_cli.py hardware-id

  # Generate test license (development only)
  python license_cli.py generate --tier indie --name "John Doe" --email john@example.com --confirm
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Activate command
    activate_parser = subparsers.add_parser("activate", help="Activate a license key")
    activate_parser.add_argument("key", help="License key to activate")

    # Status command
    status_parser = subparsers.add_parser("status", help="Show license status")

    # Deactivate command
    deactivate_parser = subparsers.add_parser(
        "deactivate", help="Deactivate current license"
    )

    # Hardware ID command
    hwid_parser = subparsers.add_parser("hardware-id", help="Show hardware ID")
    hwid_parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show detailed info"
    )

    # Generate command (for testing)
    generate_parser = subparsers.add_parser(
        "generate", help="Generate test license (dev only)"
    )
    generate_parser.add_argument(
        "--tier",
        required=True,
        choices=["free", "indie", "professional"],
        help="License tier",
    )
    generate_parser.add_argument("--name", required=True, help="Licensee name")
    generate_parser.add_argument("--email", required=True, help="Licensee email")
    generate_parser.add_argument(
        "--duration",
        type=int,
        default=0,
        help="License duration in days (0 = perpetual)",
    )
    generate_parser.add_argument(
        "--hardware-locked", action="store_true", help="Lock to current hardware"
    )
    generate_parser.add_argument(
        "--max-exports", type=int, default=0, help="Maximum exports (0 = unlimited)"
    )
    generate_parser.add_argument(
        "--confirm", action="store_true", help="Confirm test license generation"
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 1

    # Execute command
    commands = {
        "activate": cmd_activate,
        "status": cmd_status,
        "deactivate": cmd_deactivate,
        "hardware-id": cmd_hardware_id,
        "generate": cmd_generate,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
