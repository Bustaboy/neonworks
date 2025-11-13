"""
Project Exporter

Main orchestrator for exporting game projects.
Coordinates package building, executable bundling, and installer creation.
Includes license validation and tier-based feature enforcement.
"""

import sys
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass

from .package_builder import PackageBuilder, PackageConfig
from .executable_bundler import ExecutableBundler, BundleConfig, create_launcher_script
from .installer_builder import InstallerBuilder, InstallerConfig

# Import licensing system
try:
    from engine.licensing.license_validator import get_global_validator
    from engine.licensing.license_key import LicenseTier

    LICENSING_AVAILABLE = True
except ImportError:
    LICENSING_AVAILABLE = False
    LicenseTier = None


@dataclass
class ExportConfig:
    """Complete export configuration"""

    # Project info
    project_path: Path
    output_dir: Path

    # App metadata
    app_name: str
    version: str
    publisher: str = "Unknown"
    description: str = ""

    # Package options
    compress: bool = True
    encrypt: bool = False
    password: Optional[str] = None

    # Executable options
    create_executable: bool = True
    console: bool = False
    onefile: bool = True
    icon_path: Optional[Path] = None

    # Installer options
    create_installer: bool = True
    license_file: Optional[Path] = None
    readme_file: Optional[Path] = None
    create_desktop_shortcut: bool = True
    create_start_menu_shortcut: bool = True

    # Platform
    target_platform: Optional[str] = None  # None = current platform

    def __post_init__(self):
        if self.target_platform is None:
            self.target_platform = self._detect_platform()

    @staticmethod
    def _detect_platform() -> str:
        """Detect current platform"""
        if sys.platform == "win32":
            return "windows"
        elif sys.platform == "darwin":
            return "mac"
        else:
            return "linux"


class ProjectExporter:
    """Main project exporter"""

    def __init__(self, config: ExportConfig):
        self.config = config
        self.results: Dict[str, Any] = {}

    def export(self) -> Dict[str, Any]:
        """
        Run the complete export pipeline

        Returns:
            Dictionary with export results and paths
        """
        print(f"Exporting project: {self.config.app_name}")
        print(f"Target platform: {self.config.target_platform}")
        print("-" * 60)

        # Validate license
        if LICENSING_AVAILABLE:
            validator = get_global_validator()
            can_export, error_msg = validator.validate_for_export()

            if not can_export:
                print("\n" + "=" * 60)
                print("LICENSE VALIDATION FAILED")
                print("=" * 60)
                print(f"\n{error_msg}\n")
                print("=" * 60)

                # Check if free tier - allow but with warnings
                tier = validator.get_tier()
                if tier == LicenseTier.FREE:
                    print("\n⚠ Proceeding with FREE tier export...")
                    print("⚠ Exported games will include attribution watermark")
                    print("⚠ Commercial use requires a paid license\n")

                    response = input("Continue with free tier export? (y/N): ")
                    if response.lower() != "y":
                        print("\nExport cancelled.")
                        return {"error": "Export cancelled by user"}
                else:
                    raise RuntimeError("License validation failed")

            # Show license info
            license_info = validator.get_license_info()
            print(f"\nLicense: {license_info['tier']}")
            print(f"Licensee: {license_info['licensee']}")

            # Get available features
            features = validator.get_features()
            self.results["license_tier"] = validator.get_tier().value
            self.results["license_features"] = features
        else:
            print("\n⚠ Licensing system not available - proceeding without validation")
            self.results["license_tier"] = "unknown"
            self.results["license_features"] = {}

        # Create output directory
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

        # Step 1: Build package
        print("\n[1/3] Building package...")
        package_result = self._build_package()
        self.results["package"] = package_result
        print(f"  ✓ Package created: {package_result['path']}")
        print(f"  ✓ Files: {package_result['file_count']}")
        print(f"  ✓ Size: {package_result['package_size'] / 1024 / 1024:.2f} MB")
        print(f"  ✓ Compression: {package_result['compression_ratio']:.1f}%")

        # Step 2: Build executable (if requested)
        if self.config.create_executable:
            print("\n[2/3] Building executable...")
            try:
                exe_result = self._build_executable(package_result["path"])
                self.results["executable"] = exe_result
                print(f"  ✓ Executable created: {exe_result['executable_path']}")
                print(f"  ✓ Size: {exe_result['executable_size'] / 1024 / 1024:.2f} MB")
            except Exception as e:
                print(f"  ✗ Executable build failed: {e}")
                self.results["executable"] = {"error": str(e)}
                return self.results
        else:
            print("\n[2/3] Skipping executable build")
            self.results["executable"] = None

        # Step 3: Build installer (if requested)
        if self.config.create_installer and self.results["executable"]:
            print("\n[3/3] Building installer...")
            try:
                installer_result = self._build_installer(
                    self.results["executable"]["executable_path"]
                )
                self.results["installer"] = installer_result
                if "installer_path" in installer_result:
                    print(
                        f"  ✓ Installer created: {installer_result['installer_path']}"
                    )
                elif "script_path" in installer_result:
                    print(
                        f"  ✓ Installer script created: {installer_result['script_path']}"
                    )
                    print(f"  ℹ {installer_result.get('note', '')}")
                elif "instructions" in installer_result:
                    print(f"  ℹ Manual steps required for this platform")
            except Exception as e:
                print(f"  ✗ Installer build failed: {e}")
                self.results["installer"] = {"error": str(e)}
        else:
            print("\n[3/3] Skipping installer build")
            self.results["installer"] = None

        print("\n" + "=" * 60)
        print("Export complete!")
        print(f"Output directory: {self.config.output_dir}")
        print("=" * 60)

        return self.results

    def _build_package(self) -> Dict[str, Any]:
        """Build .nwdata package"""
        package_config = PackageConfig(
            compress=self.config.compress,
            encrypt=self.config.encrypt,
            password=self.config.password,
        )

        builder = PackageBuilder(package_config)

        # Add project files
        builder.add_directory(self.config.project_path)

        # Build package
        package_filename = f"{self.config.app_name.lower().replace(' ', '_')}.nwdata"
        package_path = self.config.output_dir / package_filename

        stats = builder.build(package_path)

        return {"path": package_path, "filename": package_filename, **stats}

    def _build_executable(self, package_path: Path) -> Dict[str, Any]:
        """Build standalone executable"""
        # Create launcher script
        launcher_content = create_launcher_script(
            self.config.app_name, package_path.name, self.config.password
        )

        launcher_path = self.config.output_dir / "launcher.py"
        with open(launcher_path, "w") as f:
            f.write(launcher_content)

        # Configure bundler
        bundle_config = BundleConfig(
            app_name=self.config.app_name,
            icon_path=self.config.icon_path,
            console=self.config.console,
            onefile=self.config.onefile,
            hidden_imports=[
                "engine.export.package_loader",
                "engine.data.config_loader",
                "pygame",
                "yaml",
                "numpy",
                "PIL",
            ],
        )

        bundler = ExecutableBundler(bundle_config)

        # Build executable
        result = bundler.bundle(
            launcher_path, package_path, self.config.output_dir / "bundle"
        )

        return result

    def _build_installer(self, executable_path: Path) -> Dict[str, Any]:
        """Build installer"""
        installer_config = InstallerConfig(
            app_name=self.config.app_name,
            version=self.config.version,
            publisher=self.config.publisher,
            description=self.config.description,
            icon_path=self.config.icon_path,
            license_file=self.config.license_file,
            readme_file=self.config.readme_file,
            create_desktop_shortcut=self.config.create_desktop_shortcut,
            create_start_menu_shortcut=self.config.create_start_menu_shortcut,
        )

        installer_builder = InstallerBuilder(installer_config)

        result = installer_builder.build_for_platform(
            self.config.target_platform,
            executable_path,
            self.config.output_dir / "installer",
        )

        return result

    def export_package_only(self) -> Dict[str, Any]:
        """Export only the .nwdata package (no executable)"""
        print(f"Building package for: {self.config.app_name}")
        package_result = self._build_package()
        print(f"Package created: {package_result['path']}")
        return {"package": package_result}


def quick_export(
    project_path: Path,
    output_dir: Path,
    app_name: str,
    version: str = "1.0.0",
    encrypt: bool = False,
    password: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Quick export with sensible defaults

    Args:
        project_path: Path to project directory
        output_dir: Output directory
        app_name: Application name
        version: Version string
        encrypt: Enable encryption
        password: Password for encryption

    Returns:
        Export results dictionary
    """
    config = ExportConfig(
        project_path=project_path,
        output_dir=output_dir,
        app_name=app_name,
        version=version,
        encrypt=encrypt,
        password=password,
    )

    exporter = ProjectExporter(config)
    return exporter.export()
