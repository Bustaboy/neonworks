#!/usr/bin/env python3
"""
Neon Works Export CLI

Command-line tool for exporting game projects.
"""

import argparse
import sys
from getpass import getpass
from pathlib import Path

from export.exporter import ExportConfig, ProjectExporter


def main():
    parser = argparse.ArgumentParser(
        description="Export Neon Works game projects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export with all defaults (package + exe + installer)
  python export_cli.py my_game --version 1.0.0

  # Export with encryption
  python export_cli.py my_game --version 1.0.0 --encrypt

  # Package only (no executable)
  python export_cli.py my_game --package-only

  # Custom output directory
  python export_cli.py my_game --version 1.0.0 --output dist/my_game

  # Full control
  python export_cli.py my_game \\
    --version 1.0.0 \\
    --publisher "My Studio" \\
    --description "An awesome game" \\
    --encrypt \\
    --icon assets/icon.ico \\
    --output exports/v1.0
        """,
    )

    parser.add_argument(
        "project", help="Path to project directory (e.g., projects/my_game)"
    )

    parser.add_argument(
        "--version", "-v", default="1.0.0", help="Game version (default: 1.0.0)"
    )

    parser.add_argument(
        "--output", "-o", help="Output directory (default: exports/<project_name>)"
    )

    parser.add_argument(
        "--publisher",
        "-p",
        default="Independent Developer",
        help="Publisher name for installer",
    )

    parser.add_argument("--description", "-d", default="", help="Game description")

    # Package options
    package_group = parser.add_argument_group("Package Options")
    package_group.add_argument(
        "--no-compress", action="store_true", help="Disable compression"
    )

    package_group.add_argument(
        "--encrypt", action="store_true", help="Encrypt package for IP protection"
    )

    package_group.add_argument(
        "--password", help="Encryption password (will prompt if not provided)"
    )

    # Executable options
    exe_group = parser.add_argument_group("Executable Options")
    exe_group.add_argument(
        "--no-executable", action="store_true", help="Skip executable creation"
    )

    exe_group.add_argument(
        "--package-only",
        action="store_true",
        help="Only create .nwdata package (no exe or installer)",
    )

    exe_group.add_argument(
        "--console",
        action="store_true",
        help="Show console window (useful for debugging)",
    )

    exe_group.add_argument(
        "--onedir",
        action="store_true",
        help="Create directory bundle instead of single file",
    )

    exe_group.add_argument(
        "--icon", type=Path, help="Path to icon file (.ico for Windows, .icns for Mac)"
    )

    # Installer options
    installer_group = parser.add_argument_group("Installer Options")
    installer_group.add_argument(
        "--no-installer", action="store_true", help="Skip installer creation"
    )

    installer_group.add_argument("--license", type=Path, help="Path to license file")

    installer_group.add_argument("--readme", type=Path, help="Path to readme file")

    installer_group.add_argument(
        "--no-desktop-shortcut",
        action="store_true",
        help="Don't create desktop shortcut",
    )

    installer_group.add_argument(
        "--no-start-menu", action="store_true", help="Don't create start menu shortcut"
    )

    args = parser.parse_args()

    # Resolve project path
    project_path = Path(args.project)
    if not project_path.exists():
        print(f"Error: Project directory not found: {project_path}")
        return 1

    # Load project config to get app name
    project_config_file = project_path / "project.json"
    if not project_config_file.exists():
        print(f"Error: Not a valid project (missing project.json): {project_path}")
        return 1

    import json

    with open(project_config_file) as f:
        project_config = json.load(f)

    app_name = project_config.get("metadata", {}).get("name", project_path.name)

    # Resolve output path
    if args.output:
        output_dir = Path(args.output)
    else:
        output_dir = Path("exports") / project_path.name

    # Handle encryption password
    password = None
    if args.encrypt:
        if args.password:
            password = args.password
        else:
            password = getpass("Enter encryption password: ")
            password_confirm = getpass("Confirm password: ")
            if password != password_confirm:
                print("Error: Passwords don't match")
                return 1

    # Create export config
    config = ExportConfig(
        project_path=project_path,
        output_dir=output_dir,
        app_name=app_name,
        version=args.version,
        publisher=args.publisher,
        description=args.description,
        compress=not args.no_compress,
        encrypt=args.encrypt,
        password=password,
        create_executable=not (args.no_executable or args.package_only),
        console=args.console,
        onefile=not args.onedir,
        icon_path=args.icon,
        create_installer=not (args.no_installer or args.package_only),
        license_file=args.license,
        readme_file=args.readme,
        create_desktop_shortcut=not args.no_desktop_shortcut,
        create_start_menu_shortcut=not args.no_start_menu,
    )

    # Run export
    try:
        exporter = ProjectExporter(config)

        if args.package_only:
            results = exporter.export_package_only()
        else:
            results = exporter.export()

        return 0

    except Exception as e:
        print(f"\nError during export: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
