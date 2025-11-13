"""
Installer Builder

Generates installers for different platforms:
- Windows: Inno Setup script
- Mac: .dmg creation script
- Linux: AppImage creation script
"""

import subprocess
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class InstallerConfig:
    """Configuration for installer generation"""

    app_name: str
    version: str
    publisher: str
    description: str
    icon_path: Optional[Path] = None
    license_file: Optional[Path] = None
    readme_file: Optional[Path] = None
    create_desktop_shortcut: bool = True
    create_start_menu_shortcut: bool = True
    app_id: Optional[str] = None  # GUID for Windows

    def __post_init__(self):
        if self.app_id is None:
            # Generate a deterministic GUID from app name
            namespace = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")
            self.app_id = str(uuid.uuid5(namespace, self.app_name))


class WindowsInstallerBuilder:
    """Builds Windows installers using Inno Setup"""

    def __init__(self, config: InstallerConfig):
        self.config = config

    def generate_script(
        self,
        executable_path: Path,
        output_dir: Path,
        additional_files: Optional[List[Tuple[Path, str]]] = None,
    ) -> Path:
        """
        Generate Inno Setup script

        Args:
            executable_path: Path to the .exe file or distribution folder
            output_dir: Where to write the .iss script
            additional_files: List of (source_path, dest_subdir) tuples

        Returns:
            Path to generated .iss script
        """
        if additional_files is None:
            additional_files = []

        script_content = self._generate_iss_content(
            executable_path, output_dir, additional_files
        )

        script_path = output_dir / f"{self.config.app_name}_setup.iss"
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)

        return script_path

    def build_installer(
        self, script_path: Path, output_dir: Path, iscc_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Build installer from Inno Setup script

        Args:
            script_path: Path to .iss script
            output_dir: Output directory for installer
            iscc_path: Optional path to Inno Setup Compiler (iscc.exe)

        Returns:
            Dictionary with installer information
        """
        # Find Inno Setup Compiler
        if iscc_path is None:
            iscc_path = self._find_iscc()

        if iscc_path is None or not iscc_path.exists():
            raise RuntimeError(
                "Inno Setup Compiler not found. Please install Inno Setup from:\n"
                "https://jrsoftware.org/isdl.php\n"
                "Or specify the path to iscc.exe with iscc_path parameter"
            )

        # Run compiler
        cmd = [str(iscc_path), str(script_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"Inno Setup compilation failed:\n{result.stderr}")

        # Find generated installer
        installer_name = f"{self.config.app_name}_{self.config.version}_setup.exe"
        installer_path = output_dir / installer_name

        if not installer_path.exists():
            raise RuntimeError(f"Installer not found at: {installer_path}")

        return {
            "installer_path": installer_path,
            "installer_size": installer_path.stat().st_size,
            "platform": "windows",
        }

    def _find_iscc(self) -> Optional[Path]:
        """Try to find Inno Setup Compiler"""
        # Common installation paths
        possible_paths = [
            Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"),
            Path(r"C:\Program Files\Inno Setup 6\ISCC.exe"),
            Path(r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe"),
            Path(r"C:\Program Files\Inno Setup 5\ISCC.exe"),
        ]

        for path in possible_paths:
            if path.exists():
                return path

        return None

    def _generate_iss_content(
        self,
        executable_path: Path,
        output_dir: Path,
        additional_files: Optional[List[Tuple[Path, str]]],
    ) -> str:
        """Generate Inno Setup script content"""
        # Determine if we're bundling a single file or directory
        is_onefile = executable_path.is_file()

        # Icon setup
        icon_lines = ""
        if self.config.icon_path and self.config.icon_path.exists():
            icon_lines = f"""SetupIconFile={self.config.icon_path}
UninstallDisplayIcon={{app}}\\{executable_path.name}"""

        # License file
        license_line = ""
        if self.config.license_file and self.config.license_file.exists():
            license_line = f"LicenseFile={self.config.license_file}"

        # README file
        readme_line = ""
        if self.config.readme_file and self.config.readme_file.exists():
            readme_line = f"InfoBeforeFile={self.config.readme_file}"

        # Files section
        files_section = ""
        if is_onefile:
            files_section = (
                f'Source: "{executable_path}"; DestDir: "{{app}}"; Flags: ignoreversion'
            )
        else:
            files_section = f'Source: "{executable_path}\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs'

        # Additional files
        additional_files_section = ""
        for src_path, dest_subdir in additional_files:
            dest = "{app}" if not dest_subdir else f"{{app}}\\{dest_subdir}"
            additional_files_section += (
                f'\nSource: "{src_path}"; DestDir: "{dest}"; Flags: ignoreversion'
            )

        # Icons section
        icons_section = ""
        if self.config.create_start_menu_shortcut:
            icons_section += f'\nName: "{{autoprograms}}\\{self.config.app_name}"; Filename: "{{app}}\\{executable_path.name if is_onefile else executable_path.name + ".exe"}"'

        if self.config.create_desktop_shortcut:
            icons_section += f'\nName: "{{autodesktop}}\\{self.config.app_name}"; Filename: "{{app}}\\{executable_path.name if is_onefile else executable_path.name + ".exe"}"; Tasks: desktopicon'

        script = f"""; Script generated by Neon Works Export System

[Setup]
AppId={{{{{self.config.app_id}}}}}
AppName={self.config.app_name}
AppVersion={self.config.version}
AppPublisher={self.config.publisher}
AppPublisherURL=
AppSupportURL=
AppUpdatesURL=
DefaultDirName={{autopf}}\\{self.config.app_name}
DefaultGroupName={self.config.app_name}
AllowNoIcons=yes
{license_line}
{readme_line}
OutputDir={output_dir}
OutputBaseFilename={self.config.app_name}_{self.config.version}_setup
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
{icon_lines}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked

[Files]
{files_section}{additional_files_section}

[Icons]{icons_section}

[Run]
Filename: "{{app}}\\{executable_path.name if is_onefile else executable_path.name + '.exe'}"; Description: "{{cm:LaunchProgram,{self.config.app_name}}}"; Flags: nowait postinstall skipifsilent
"""
        return script


class MacInstallerBuilder:
    """Builds Mac .dmg installers"""

    def __init__(self, config: InstallerConfig):
        self.config = config

    def create_dmg(self, app_bundle: Path, output_path: Path) -> Dict[str, Any]:
        """
        Create .dmg from .app bundle

        Args:
            app_bundle: Path to .app bundle
            output_path: Output path for .dmg

        Returns:
            Dictionary with installer information
        """
        # This requires create-dmg tool on macOS
        # For now, provide instructions
        instructions = f"""
To create a .dmg for Mac, use the create-dmg tool:

1. Install create-dmg:
   brew install create-dmg

2. Run:
   create-dmg \\
     --volname "{self.config.app_name}" \\
     --window-pos 200 120 \\
     --window-size 800 400 \\
     --icon-size 100 \\
     --app-drop-link 600 185 \\
     "{output_path}" \\
     "{app_bundle}"

Alternatively, use hdiutil (built into macOS):
   hdiutil create -volname "{self.config.app_name}" -srcfolder "{app_bundle}" -ov -format UDZO "{output_path}"
"""
        return {"instructions": instructions, "platform": "mac"}


class LinuxInstallerBuilder:
    """Builds Linux AppImage installers"""

    def __init__(self, config: InstallerConfig):
        self.config = config

    def create_appimage(
        self, executable_path: Path, output_path: Path
    ) -> Dict[str, Any]:
        """
        Create AppImage from executable

        Args:
            executable_path: Path to executable
            output_path: Output path for AppImage

        Returns:
            Dictionary with installer information
        """
        # This requires appimagetool
        instructions = f"""
To create an AppImage for Linux, use appimagetool:

1. Download appimagetool:
   wget "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
   chmod a+x appimagetool-x86_64.AppImage

2. Create AppDir structure:
   mkdir -p MyApp.AppDir/usr/bin
   cp {executable_path} MyApp.AppDir/usr/bin/

3. Create .desktop file in MyApp.AppDir/

4. Run:
   ./appimagetool-x86_64.AppImage MyApp.AppDir {output_path}

For more information: https://docs.appimage.org/
"""
        return {"instructions": instructions, "platform": "linux"}


class InstallerBuilder:
    """Main installer builder that delegates to platform-specific builders"""

    def __init__(self, config: InstallerConfig):
        self.config = config
        self.windows_builder = WindowsInstallerBuilder(config)
        self.mac_builder = MacInstallerBuilder(config)
        self.linux_builder = LinuxInstallerBuilder(config)

    def build_for_platform(
        self, platform: str, executable_path: Path, output_dir: Path, **kwargs
    ) -> Dict[str, Any]:
        """
        Build installer for specified platform

        Args:
            platform: 'windows', 'mac', or 'linux'
            executable_path: Path to executable/bundle
            output_dir: Output directory
            **kwargs: Platform-specific options

        Returns:
            Dictionary with installer information
        """
        platform = platform.lower()

        if platform == "windows":
            script_path = self.windows_builder.generate_script(
                executable_path, output_dir, kwargs.get("additional_files", [])
            )
            return {
                "script_path": script_path,
                "platform": "windows",
                "note": "Run this script with Inno Setup Compiler to create installer",
            }

        elif platform == "mac":
            return self.mac_builder.create_dmg(executable_path, output_dir)

        elif platform == "linux":
            return self.linux_builder.create_appimage(executable_path, output_dir)

        else:
            raise ValueError(f"Unsupported platform: {platform}")
