# NeonWorks Engine Dependencies

This document provides a comprehensive overview of all Python dependencies required for the NeonWorks Game Engine.

## Table of Contents
- [Runtime Dependencies](#runtime-dependencies)
- [Development Dependencies](#development-dependencies)
- [Optional Dependencies](#optional-dependencies)
- [Installation](#installation)
- [Dependency Usage Analysis](#dependency-usage-analysis)
- [Python Version Requirements](#python-version-requirements)

---

## Runtime Dependencies

These packages are required to run the NeonWorks engine and games built with it.

### Core Dependencies

#### pygame (2.5.2)
- **Purpose**: Core rendering engine, input handling, and audio playback
- **Usage**: Used in 47+ files across the engine
- **Key Systems**:
  - Rendering (sprites, surfaces, display)
  - Input (keyboard, mouse, gamepad)
  - Audio (mixer, sound playback)
  - Event handling
- **Website**: https://www.pygame.org/

#### numpy (≥1.24.0)
- **Purpose**: High-performance numerical computing for math-heavy operations
- **Usage**: Used in 3 critical performance-sensitive modules
- **Key Systems**:
  - `ai/pathfinding.py` - A* pathfinding optimization
  - `physics/collision.py` - Collision detection with spatial partitioning
  - `rendering/particles.py` - Batch particle system updates
- **Website**: https://numpy.org/

#### Pillow (≥10.0.0)
- **Purpose**: Image processing and asset pipeline management
- **Usage**: Used in asset pipeline module
- **Key Systems**:
  - `rendering/asset_pipeline.py` - Texture atlases, format conversions, optimization
- **Features**:
  - Texture atlas generation
  - Image format conversions
  - Image effects and filters
  - Sprite sheet extraction
- **Website**: https://pillow.readthedocs.io/

#### PyYAML (≥6.0.1)
- **Purpose**: YAML configuration file support for readable game data
- **Usage**: Used in data loading module
- **Key Systems**:
  - `data/config_loader.py` - Game configuration and data files
- **Features**:
  - Game settings and configuration
  - Level data
  - Entity definitions
- **Website**: https://pyyaml.org/

### Export System Dependencies

#### cryptography (≥41.0.0)
- **Purpose**: Encryption for packaged games (IP protection)
- **Usage**: Used in 2 export modules
- **Key Systems**:
  - `export/package_builder.py` - Package encryption
  - `export/package_loader.py` - Package decryption
- **Features**:
  - AES-256-GCM encryption
  - PBKDF2 key derivation
  - Secure game asset packaging
- **Website**: https://cryptography.io/

#### pyinstaller (≥6.0.0)
- **Purpose**: Executable bundling for standalone game distribution
- **Usage**: Used in executable bundler module
- **Key Systems**:
  - `export/executable_bundler.py` - Python to executable conversion
- **Features**:
  - Windows .exe creation
  - macOS .app bundles
  - Linux binaries
  - Dependency bundling
- **Website**: https://pyinstaller.org/

---

## Development Dependencies

These packages are used for development, testing, and code quality assurance.

### Testing Framework

#### pytest (7.4.3)
- **Purpose**: Primary testing framework
- **Usage**: 17 test modules
- **Website**: https://pytest.org/

#### pytest-cov (4.1.0)
- **Purpose**: Test coverage measurement
- **Website**: https://pytest-cov.readthedocs.io/

#### pytest-mock (3.12.0)
- **Purpose**: Mocking and stubbing for tests
- **Website**: https://pytest-mock.readthedocs.io/

#### pytest-xdist (3.5.0)
- **Purpose**: Parallel test execution
- **Website**: https://pytest-xdist.readthedocs.io/

#### pytest-pygame (0.0.2)
- **Purpose**: Pygame-specific testing utilities
- **Website**: https://pypi.org/project/pytest-pygame/

#### pytest-timeout (2.2.0)
- **Purpose**: Test timeout management
- **Website**: https://github.com/pytest-dev/pytest-timeout

### Code Quality Tools

#### black (23.12.1)
- **Purpose**: Code formatter (PEP 8 compliant)
- **Website**: https://black.readthedocs.io/

#### flake8 (6.1.0)
- **Purpose**: Style guide enforcement and linting
- **Website**: https://flake8.pycqa.org/

#### mypy (1.7.1)
- **Purpose**: Static type checking
- **Website**: https://mypy.readthedocs.io/

#### pylint (3.0.3)
- **Purpose**: Comprehensive code analysis
- **Website**: https://pylint.pycqa.org/

#### isort (5.13.2)
- **Purpose**: Import statement organization
- **Website**: https://pycqa.github.io/isort/

### Additional Development Tools

#### coverage (7.3.4)
- **Purpose**: Code coverage measurement
- **Website**: https://coverage.readthedocs.io/

#### coverage-badge (1.1.0)
- **Purpose**: Generate coverage badges for documentation
- **Website**: https://github.com/dbrgn/coverage-badge

#### faker (21.0.0)
- **Purpose**: Test data generation
- **Website**: https://faker.readthedocs.io/

#### sphinx (7.2.6)
- **Purpose**: Documentation generation
- **Website**: https://www.sphinx-doc.org/

#### sphinx-rtd-theme (2.0.0)
- **Purpose**: ReadTheDocs theme for Sphinx
- **Website**: https://sphinx-rtd-theme.readthedocs.io/

#### pre-commit (3.6.0)
- **Purpose**: Git hook framework for code quality checks
- **Website**: https://pre-commit.com/

#### tox (4.11.4)
- **Purpose**: Testing automation across environments
- **Website**: https://tox.wiki/

---

## Optional Dependencies

These dependencies provide additional features but are not required for basic engine functionality.

### Cython (≥3.0.0)
- **Purpose**: Code compilation for maximum performance and IP protection
- **Usage**: Professional tier feature
- **Key Systems**:
  - `export/code_protection.py` - Optional Cython compilation
- **Status**: Commented out in requirements.txt
- **Note**: Requires separate commercial license
- **Website**: https://cython.org/

### PyArmor (≥8.0.0)
- **Purpose**: Advanced code obfuscation for engine IP protection
- **Usage**: Enterprise tier feature (commented in requirements.txt)
- **Status**: Requires separate license
- **Note**: Not actively used in current codebase
- **Website**: https://pyarmor.readthedocs.io/

---

## Installation

### Quick Install (Runtime Only)

Install only the packages needed to run games:

```bash
pip install -r requirements.txt
```

### Development Install

Install all development tools:

```bash
pip install -r requirements-dev.txt
```

This automatically includes runtime dependencies via `-r requirements.txt`.

### Package Install

Install NeonWorks as a Python package:

```bash
pip install -e .
```

This installs the engine in editable mode with all runtime dependencies.

### Development Package Install

Install with development extras:

```bash
pip install -e ".[dev]"
```

---

## Dependency Usage Analysis

### Import Distribution

The following shows how many files use each major dependency:

| Package | Files | Critical | Purpose |
|---------|-------|----------|---------|
| pygame | 47 | Yes | Core engine functionality |
| numpy | 3 | Performance | Math-heavy optimizations |
| Pillow | 1 | No | Asset pipeline only |
| PyYAML | 1 | No | Config loading only |
| cryptography | 2 | No | Export system only |
| pyinstaller | 1 | No | Export system only |
| pytest | 17 | Dev only | Testing framework |

### Module Dependencies by System

#### Core Engine (Always Required)
- pygame
- numpy (performance-critical paths only)

#### Asset Pipeline (Optional but Recommended)
- Pillow

#### Configuration System (Optional)
- PyYAML

#### Export System (Distribution Only)
- cryptography
- pyinstaller

### Minimal Installation

For a minimal engine installation that supports basic game development:

```bash
pip install pygame>=2.5.2 numpy>=1.24.0
```

This provides:
- Core rendering
- Input handling
- Audio
- Physics
- AI pathfinding
- Combat systems

**Note**: Pillow and PyYAML are highly recommended for full functionality.

---

## Python Version Requirements

### Supported Versions
- Python 3.8+
- Python 3.9
- Python 3.10
- Python 3.11

### Recommended Version
Python 3.10 or 3.11 for best performance and compatibility.

### Version-Specific Notes

#### Python 3.8
- Minimum supported version
- All features tested and working

#### Python 3.9+
- Improved performance for math operations (benefits numpy usage)
- Better typing support (helpful for development)

#### Python 3.11
- Significant performance improvements (up to 25% faster)
- Recommended for production games

---

## Dependency Health

All dependencies are actively maintained and regularly updated:

| Package | Status | Last Major Update |
|---------|--------|-------------------|
| pygame | ✅ Active | 2.5.x (2023) |
| numpy | ✅ Active | 1.24+ (2023) |
| Pillow | ✅ Active | 10.x (2023) |
| PyYAML | ✅ Active | 6.x (2023) |
| cryptography | ✅ Active | 41.x (2023) |
| pyinstaller | ✅ Active | 6.x (2023) |

---

## Known Issues and Limitations

### pygame
- Audio mixer has limited format support on some platforms
- MacOS may require SDL2 framework installation
- Wayland support on Linux is experimental

### pyinstaller
- Some antivirus software may flag executables as false positives
- Large bundle sizes (can be mitigated with UPX compression)
- Code signing required for macOS distribution

### Pillow
- Some advanced image formats require additional system libraries
- WebP support may need manual compilation on older systems

---

## Security Considerations

### Cryptography
- Uses industry-standard AES-256-GCM encryption
- PBKDF2 with 100,000 iterations for key derivation
- Regular security updates - keep this package updated

### PyInstaller
- Bundled executables can be decompiled - use with code protection
- Consider code signing for distribution

---

## Troubleshooting

### Common Installation Issues

#### pygame won't install
```bash
# Linux: Install SDL development libraries
sudo apt-get install python3-dev libsdl2-dev libsdl2-mixer-dev

# macOS: Install via Homebrew
brew install sdl2 sdl2_mixer
```

#### numpy installation fails
```bash
# Install with pre-built wheels
pip install --only-binary :all: numpy
```

#### Pillow missing image format support
```bash
# Linux: Install image libraries
sudo apt-get install libjpeg-dev zlib1g-dev libpng-dev
```

---

## Contributing

When adding new dependencies:

1. Add to `requirements.txt` (runtime) or `requirements-dev.txt` (development)
2. Update this DEPENDENCIES.md file
3. Pin versions for runtime dependencies
4. Use minimum versions (≥) for flexibility where appropriate
5. Document the purpose and usage in this file
6. Ensure licenses are compatible with the project

---

## License Compatibility

All runtime dependencies use permissive licenses compatible with commercial use:

- pygame: LGPL 2.1+
- numpy: BSD License
- Pillow: HPND License
- PyYAML: MIT License
- cryptography: Apache 2.0 / BSD
- pyinstaller: GPL with exception (distributed apps can use any license)

---

## Support

For dependency-related issues:

1. Check the [Known Issues](#known-issues-and-limitations) section
2. Consult the [Troubleshooting](#troubleshooting) guide
3. Review the official documentation for each package
4. Open an issue in the NeonWorks repository

---

**Last Updated**: 2025-11-13
**NeonWorks Version**: 0.1.0
