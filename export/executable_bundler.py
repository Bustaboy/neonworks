"""
Executable Bundler

Bundles games as standalone executables using PyInstaller.
Embeds the .nwdata package and creates platform-specific executables.
"""

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class BundleConfig:
    """Configuration for executable bundling"""

    app_name: str
    icon_path: Optional[Path] = None
    console: bool = False  # Show console window
    onefile: bool = True  # Create single executable file
    include_packages: List[str] = None
    include_files: List[tuple[str, str]] = None
    hidden_imports: List[str] = None
    upx: bool = True  # Use UPX compression
    strip: bool = True  # Strip debug symbols

    def __post_init__(self):
        if self.include_packages is None:
            self.include_packages = []
        if self.include_files is None:
            self.include_files = []
        if self.hidden_imports is None:
            self.hidden_imports = []


class ExecutableBundler:
    """Bundles games as standalone executables"""

    def __init__(self, config: BundleConfig):
        self.config = config

    def bundle(
        self,
        launcher_script: Path,
        package_file: Path,
        output_dir: Path,
        spec_file: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """
        Bundle the game as a standalone executable

        Args:
            launcher_script: Path to the launcher Python script
            package_file: Path to the .nwdata package file
            output_dir: Output directory for executable
            spec_file: Optional PyInstaller spec file

        Returns:
            Dictionary with bundle information
        """
        # Verify PyInstaller is available
        try:
            import PyInstaller
        except ImportError:
            raise RuntimeError(
                "PyInstaller not available. Install with: pip install pyinstaller"
            )

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Build PyInstaller command
        if spec_file and spec_file.exists():
            # Use existing spec file
            cmd = self._build_spec_command(spec_file, output_dir)
        else:
            # Generate command from config
            cmd = self._build_command(launcher_script, package_file, output_dir)

        # Run PyInstaller
        print(f"Running PyInstaller: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"PyInstaller failed:\n{result.stderr}")

        # Find the generated executable
        if self.config.onefile:
            exe_name = self._get_exe_name()
            exe_path = output_dir / "dist" / exe_name
        else:
            exe_path = output_dir / "dist" / self.config.app_name

        if not exe_path.exists():
            raise RuntimeError(f"Executable not found at expected path: {exe_path}")

        # Get executable size
        if exe_path.is_file():
            exe_size = exe_path.stat().st_size
        else:
            # Directory bundle
            exe_size = sum(f.stat().st_size for f in exe_path.rglob("*") if f.is_file())

        return {
            "executable_path": exe_path,
            "executable_size": exe_size,
            "onefile": self.config.onefile,
            "platform": sys.platform,
        }

    def _build_command(
        self, launcher_script: Path, package_file: Path, output_dir: Path
    ) -> List[str]:
        """Build PyInstaller command"""
        cmd = [
            sys.executable,
            "-m",
            "PyInstaller",
            str(launcher_script),
            "--name",
            self.config.app_name,
            "--workpath",
            str(output_dir / "build"),
            "--distpath",
            str(output_dir / "dist"),
            "--specpath",
            str(output_dir),
        ]

        # One file or directory bundle
        if self.config.onefile:
            cmd.append("--onefile")
        else:
            cmd.append("--onedir")

        # Console window
        if not self.config.console:
            cmd.append("--windowed")
        else:
            cmd.append("--console")

        # Icon
        if self.config.icon_path and self.config.icon_path.exists():
            cmd.extend(["--icon", str(self.config.icon_path)])

        # Include package file
        cmd.extend(["--add-data", f"{package_file}{os.pathsep}."])

        # Include additional files
        for src, dst in self.config.include_files:
            cmd.extend(["--add-data", f"{src}{os.pathsep}{dst}"])

        # Hidden imports
        for imp in self.config.hidden_imports:
            cmd.extend(["--hidden-import", imp])

        # UPX compression
        if self.config.upx:
            cmd.append("--upx-dir=upx")
        else:
            cmd.append("--noupx")

        # Strip symbols
        if self.config.strip:
            cmd.append("--strip")

        # Clean build
        cmd.append("--clean")

        return cmd

    def _build_spec_command(self, spec_file: Path, output_dir: Path) -> List[str]:
        """Build PyInstaller command from spec file"""
        return [
            sys.executable,
            "-m",
            "PyInstaller",
            str(spec_file),
            "--distpath",
            str(output_dir / "dist"),
            "--workpath",
            str(output_dir / "build"),
            "--clean",
        ]

    def _get_exe_name(self) -> str:
        """Get executable name for current platform"""
        if sys.platform == "win32":
            return f"{self.config.app_name}.exe"
        else:
            return self.config.app_name

    def generate_spec_file(
        self, launcher_script: Path, package_file: Path, output_path: Path
    ) -> Path:
        """
        Generate a PyInstaller spec file

        This allows users to customize the build process

        Args:
            launcher_script: Path to launcher script
            package_file: Path to .nwdata package
            output_path: Where to write the spec file

        Returns:
            Path to generated spec file
        """
        spec_content = self._generate_spec_content(launcher_script, package_file)

        with open(output_path, "w") as f:
            f.write(spec_content)

        return output_path

    def _generate_spec_content(self, launcher_script: Path, package_file: Path) -> str:
        """Generate PyInstaller spec file content"""
        # Build data files list
        datas = [f"('{package_file}', '.')"]
        for src, dst in self.config.include_files:
            datas.append(f"('{src}', '{dst}')")

        datas_str = ",\n                 ".join(datas)

        # Build hidden imports
        hiddenimports_str = ", ".join(f"'{imp}'" for imp in self.config.hidden_imports)

        # Icon line
        icon_line = (
            f"icon='{self.config.icon_path}',"
            if self.config.icon_path
            else "icon=None,"
        )

        spec_template = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{launcher_script}'],
    pathex=[],
    binaries=[],
    datas=[{datas_str}],
    hiddenimports=[{hiddenimports_str}],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    {'a.binaries,' if self.config.onefile else ''}
    {'a.zipfiles,' if self.config.onefile else ''}
    {'a.datas,' if self.config.onefile else ''}
    [],
    name='{self.config.app_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip={str(self.config.strip)},
    upx={str(self.config.upx)},
    upx_exclude=[],
    runtime_tmpdir=None,
    console={str(self.config.console)},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    {icon_line}
)

{'' if self.config.onefile else f'''
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip={str(self.config.strip)},
    upx={str(self.config.upx)},
    upx_exclude=[],
    name='{self.config.app_name}',
)
'''}
"""
        return spec_template


def create_launcher_script(
    project_name: str, package_filename: str, password: Optional[str] = None
) -> str:
    """
    Generate launcher script content

    This script loads the .nwdata package and starts the game

    Args:
        project_name: Name of the project
        package_filename: Name of the .nwdata file
        password: Optional password for encrypted packages

    Returns:
        Launcher script content as string
    """
    password_line = (
        f"    password = '{password}'" if password else "    password = None"
    )

    launcher = f"""#!/usr/bin/env python3
\"\"\"
{project_name} Launcher

This is the main entry point for the packaged game.
It loads the .nwdata package and starts the game.
\"\"\"

import sys
import os
from pathlib import Path

def main():
    # Determine package path
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        base_path = Path(sys._MEIPASS)
    else:
        # Running as script
        base_path = Path(__file__).parent

    package_path = base_path / '{package_filename}'

    if not package_path.exists():
        print(f"ERROR: Package file not found: {{package_path}}")
        input("Press Enter to exit...")
        sys.exit(1)

    # Load package
    try:
        from neonworks.export.package_loader import PackageLoader, set_global_loader

{password_line}

        loader = PackageLoader(package_path, password=password)
        loader.load_index()
        set_global_loader(loader)

        print(f"Loaded package: {{package_path.name}}")
        print(f"Files: {{len(loader.list_files())}}")

    except Exception as e:
        print(f"ERROR loading package: {{e}}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)

    # Start game
    try:
        # Import and run the game
        # Adjust this import based on your engine structure
        from neonworks.main import main as game_main
        game_main()

    except Exception as e:
        print(f"ERROR starting game: {{e}}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == '__main__':
    main()
"""
    return launcher
