"""
Code Protection

Provides code obfuscation and compilation for IP protection.
Supports PyArmor obfuscation and Cython compilation.
"""

import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


class PyArmorObfuscator:
    """
    Obfuscate Python code using PyArmor.

    PyArmor makes reverse engineering very difficult while maintaining
    compatibility with standard Python environments.
    """

    def __init__(self):
        self.pyarmor_available = self._check_pyarmor()

    def _check_pyarmor(self) -> bool:
        """Check if PyArmor is available"""
        try:
            result = subprocess.run(["pyarmor", "--version"], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def obfuscate_directory(
        self,
        source_dir: Path,
        output_dir: Path,
        exclude_patterns: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Obfuscate all Python files in a directory.

        Args:
            source_dir: Source directory containing Python files
            output_dir: Output directory for obfuscated files
            exclude_patterns: File patterns to exclude (e.g., ['test_*.py', '__pycache__'])

        Returns:
            Dictionary with obfuscation results
        """
        if not self.pyarmor_available:
            raise RuntimeError(
                "PyArmor not available. Install with: pip install pyarmor\n"
                "Note: PyArmor requires a license for commercial use."
            )

        if exclude_patterns is None:
            exclude_patterns = ["__pycache__", "*.pyc", "test_*.py", "*_test.py"]

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Build PyArmor command
        cmd = [
            "pyarmor",
            "gen",
            "--output",
            str(output_dir),
            "--recursive",
        ]

        # Add exclusions
        for pattern in exclude_patterns:
            cmd.extend(["--exclude", pattern])

        # Add source directory
        cmd.append(str(source_dir))

        # Run PyArmor
        print(f"  Obfuscating with PyArmor...")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"PyArmor obfuscation failed:\n{result.stderr}")

        # Count obfuscated files
        obfuscated_files = list(output_dir.rglob("*.py"))

        return {
            "obfuscated_files": len(obfuscated_files),
            "output_dir": output_dir,
            "method": "pyarmor",
        }

    def obfuscate_files(self, files: List[Path], output_dir: Path) -> Dict[str, Any]:
        """
        Obfuscate specific Python files.

        Args:
            files: List of Python files to obfuscate
            output_dir: Output directory

        Returns:
            Dictionary with obfuscation results
        """
        if not self.pyarmor_available:
            raise RuntimeError("PyArmor not available")

        output_dir.mkdir(parents=True, exist_ok=True)

        # Obfuscate each file
        for file_path in files:
            cmd = ["pyarmor", "gen", "--output", str(output_dir), str(file_path)]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                raise RuntimeError(f"Failed to obfuscate {file_path}:\n{result.stderr}")

        return {
            "obfuscated_files": len(files),
            "output_dir": output_dir,
            "method": "pyarmor",
        }


class CythonCompiler:
    """
    Compile Python code to C extensions using Cython.

    Provides near-native performance and makes reverse engineering
    nearly impossible.
    """

    def __init__(self):
        self.cython_available = self._check_cython()

    def _check_cython(self) -> bool:
        """Check if Cython is available"""
        try:
            import Cython

            return True
        except ImportError:
            return False

    def compile_module(
        self, source_file: Path, output_dir: Path, optimize: bool = True
    ) -> Dict[str, Any]:
        """
        Compile a Python module to C extension.

        Args:
            source_file: Python source file
            output_dir: Output directory for compiled extension
            optimize: Enable optimizations

        Returns:
            Dictionary with compilation results
        """
        if not self.cython_available:
            raise RuntimeError("Cython not available. Install with: pip install cython")

        output_dir.mkdir(parents=True, exist_ok=True)

        # Create setup.py for this module
        setup_content = self._generate_setup_py(source_file, optimize)
        setup_file = output_dir / "setup.py"

        with open(setup_file, "w") as f:
            f.write(setup_content)

        # Copy source file to output directory
        target_file = output_dir / source_file.name
        shutil.copy(source_file, target_file)

        # Run Cython compilation
        cmd = ["python", str(setup_file), "build_ext", "--inplace"]

        result = subprocess.run(cmd, cwd=output_dir, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"Cython compilation failed:\n{result.stderr}")

        # Find compiled extension
        extensions = list(output_dir.glob("*.pyd")) + list(output_dir.glob("*.so"))

        return {
            "compiled_files": len(extensions),
            "output_dir": output_dir,
            "method": "cython",
            "extensions": [str(e) for e in extensions],
        }

    def _generate_setup_py(self, source_file: Path, optimize: bool) -> str:
        """Generate setup.py for Cython compilation"""
        module_name = source_file.stem

        compiler_directives = {}
        if optimize:
            compiler_directives = {
                "language_level": "3",
                "boundscheck": False,
                "wraparound": False,
                "initializedcheck": False,
                "nonecheck": False,
                "embedsignature": True,
            }

        return f"""
from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(
        "{source_file.name}",
        compiler_directives={compiler_directives},
        annotate=False
    )
)
"""


class CodeProtector:
    """
    Main code protection orchestrator.

    Applies appropriate protection based on license tier.
    """

    def __init__(self):
        self.pyarmor = PyArmorObfuscator()
        self.cython = CythonCompiler()

    def protect_engine(
        self, engine_dir: Path, output_dir: Path, protection_level: str = "obfuscate"
    ) -> Dict[str, Any]:
        """
        Protect engine code based on protection level.

        Args:
            engine_dir: Engine source directory
            output_dir: Output directory for protected code
            protection_level: 'none', 'obfuscate', or 'compile'

        Returns:
            Dictionary with protection results
        """
        if protection_level == "none":
            # Just copy files
            shutil.copytree(engine_dir, output_dir, dirs_exist_ok=True)
            return {
                "protection_level": "none",
                "method": "copy",
                "output_dir": output_dir,
            }

        elif protection_level == "obfuscate":
            # Use PyArmor
            if not self.pyarmor.pyarmor_available:
                print("⚠ PyArmor not available, copying source without obfuscation")
                shutil.copytree(engine_dir, output_dir, dirs_exist_ok=True)
                return {
                    "protection_level": "none",
                    "method": "copy (pyarmor unavailable)",
                    "output_dir": output_dir,
                }

            result = self.pyarmor.obfuscate_directory(engine_dir, output_dir)
            result["protection_level"] = "obfuscate"
            return result

        elif protection_level == "compile":
            # Use Cython for critical modules
            if not self.cython.cython_available:
                print("⚠ Cython not available, falling back to obfuscation")
                return self.protect_engine(engine_dir, output_dir, "obfuscate")

            # Identify critical modules to compile
            critical_modules = [
                "core/ecs.py",
                "core/project.py",
                "data/serialization.py",
                "licensing/license_validator.py",
            ]

            compiled_count = 0
            for module in critical_modules:
                module_path = engine_dir / module
                if module_path.exists():
                    try:
                        self.cython.compile_module(module_path, output_dir / module_path.parent)
                        compiled_count += 1
                    except Exception as e:
                        print(f"⚠ Failed to compile {module}: {e}")

            # Obfuscate the rest
            self.pyarmor.obfuscate_directory(engine_dir, output_dir)

            return {
                "protection_level": "compile",
                "method": "cython + pyarmor",
                "compiled_modules": compiled_count,
                "output_dir": output_dir,
            }

        else:
            raise ValueError(f"Unknown protection level: {protection_level}")


def get_protection_level_for_tier(tier: str) -> str:
    """
    Get appropriate protection level for license tier.

    Args:
        tier: License tier ('free', 'indie', 'professional')

    Returns:
        Protection level ('none', 'obfuscate', 'compile')
    """
    tier_protection = {"free": "none", "indie": "obfuscate", "professional": "compile"}

    return tier_protection.get(tier.lower(), "none")
