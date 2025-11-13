# Neon Collapse Repository

This repository contains two separate, independent projects:

1. **[Neon Works](engine/README.md)** - A reusable, project-based 2D game engine (ECS architecture)
2. **[Neon Collapse](game/README.md)** - A standalone cyberpunk combat prototype (Pygame, NOT using the engine)

**IMPORTANT:** The `/game` folder is a separate combat prototype that does NOT use the Neon Works engine. It's a standalone Pygame implementation developed independently.

---

## 📁 Repository Structure

```
neon-collapse/
├── engine/                    # 🎮 NEON WORKS ENGINE (Reusable ECS-based engine)
│   ├── requirements.txt       # Engine runtime dependencies
│   ├── requirements-dev.txt   # Engine development dependencies
│   ├── pytest.ini             # Engine test configuration
│   ├── mypy.ini               # Engine type checking configuration
│   ├── setup.py               # Engine package setup
│   ├── README.md              # Engine documentation
│   ├── core/                  # Core engine systems (ECS, game loop, events)
│   ├── rendering/             # Rendering systems
│   ├── systems/               # Game systems
│   ├── editor/                # AI-assisted editor tools
│   └── tests/                 # Engine tests
│
├── game/                      # 🎯 NEON COLLAPSE GAME (Standalone Pygame prototype)
│   ├── requirements.txt       # Game dependencies
│   ├── README.md              # Game documentation
│   ├── main.py                # Game entry point
│   ├── combat.py              # Combat system
│   ├── character.py           # Character classes
│   ├── ui.py                  # Rendering
│   └── config.py              # Game constants
│
├── tests/                     # Game tests
├── projects/                  # Engine project templates
│   └── neon_collapse/         # Example project config (template only, no implementation)
├── bibles/                    # Game design documents
│
├── requirements-dev.txt       # Shared development tools (testing, linting)
├── pytest.ini                 # Game test configuration
├── mypy.ini                   # Game type checking configuration
└── README.md                  # This file
```

---

## 🎮 Neon Works Game Engine

A comprehensive, **project-based** 2D game engine for turn-based strategy games with base building and survival elements.

Originally developed for Neon Collapse, Neon Works is now a standalone, reusable engine for creating your own games.

### Key Features
- ✅ **Entity Component System** (ECS) for flexible game object management
- ✅ **Project-Based Architecture** - Engine is completely separate from game content
- ✅ **Turn-Based Strategy** - Grid-based tactical gameplay
- ✅ **Base Building** - Construction and upgrade systems
- ✅ **Survival Mechanics** - Hunger, thirst, energy management
- ✅ **Pathfinding** - A* pathfinding with navmesh support
- ✅ **AI-Assisted Tools** - Navmesh generation, level building, quest writing

### Quick Start

```bash
# Install engine dependencies
cd engine
pip install -r requirements-dev.txt

# Run engine tests
pytest

# See full documentation
cat README.md
```

**[📖 Full Engine Documentation →](engine/README.md)**

---

## 🌃 Neon Collapse Game

A standalone cyberpunk combat prototype with turn-based tactical gameplay. This is a separate Pygame implementation that does NOT use the Neon Works engine.

[![Tests](https://img.shields.io/badge/tests-880%20passing-brightgreen)](https://github.com/Bustaboy/neon-collapse)
[![Coverage](https://img.shields.io/badge/coverage-78%25-yellow)](./htmlcov/index.html)
[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/)
[![Code Quality](https://img.shields.io/badge/grade-A--brightgreen)](./CODE_QUALITY_REPORT.md)

### Key Features
- **Turn-Based Combat** - Initiative system, action points, cover mechanics
- **Character Progression** - Skills, XP, attributes, cyberware upgrades
- **Faction System** - Reputation, alliances, and consequences
- **Quest System** - Dynamic objectives with multiple solution paths
- **Crafting & Economy** - Loot, vendors, item management
- **Stealth & Hacking** - Alternative approaches to challenges
- **District Building** - Establish and defend your territory
- **Dynamic Difficulty** - AI Director adjusts challenge to player skill

### Quick Start

```bash
# Install game dependencies
pip install -r requirements-dev.txt

# Run the game
cd game && python main.py

# Run game tests
pytest tests/

# See full documentation
cat game/README.md
```

**[📖 Full Game Documentation →](game/README.md)**

---

## 🚀 Getting Started

### For Game Players

```bash
# Clone and run the Neon Collapse game
git clone https://github.com/Bustaboy/neon-collapse.git
cd neon-collapse
pip install -r requirements-dev.txt
cd game && python main.py
```

### For Engine Users

```bash
# Install the engine
cd engine
pip install -r requirements-dev.txt

# Run tests to verify the engine works
pytest tests/

# Note: The example project (projects/neon_collapse/) is a template
# with configuration files only. See "Creating a New Game Project"
# in engine/README.md for how to build a complete game.
```

### For Developers

```bash
# Install all dependencies for both engine and game
pip install -r requirements-dev.txt

# Run all tests
pytest tests/           # Game tests
pytest engine/tests/    # Engine tests

# Code quality checks
make lint              # Run flake8 and pylint
make typecheck         # Run mypy type checking
make format            # Format code with black/isort
```

---

## 📚 Documentation

### Project Documentation
- **[Engine README](engine/README.md)** - Complete engine documentation
- **[Game README](game/README.md)** - Complete game documentation
- **[Developer Guide](DEVELOPER_GUIDE.md)** - Best practices and code standards
- **[Testing Guide](README_TESTING.md)** - Testing patterns and strategies

### Technical Documentation
- **[Architecture Summary](ARCHITECTURE_SUMMARY.md)** - Engine design patterns
- **[Codebase Analysis](CODEBASE_ANALYSIS.md)** - Detailed code analysis
- **[Code Quality Report](CODE_QUALITY_REPORT.md)** - Metrics and analysis
- **[System Interactions](SYSTEM_INTERACTIONS.md)** - How systems communicate
- **[Changelog](CHANGELOG.md)** - Version history and changes

### Game Design Documents (in `bibles/`)
- `06-TDD-GAME-SYSTEMS-BIBLE.md` - System specifications
- `07-TECHNICAL-ARCHITECTURE-BIBLE.md` - Architecture overview
- `08-GAME-MECHANICS-BIBLE.md` - Game mechanics
- `09-TESTING-BIBLE-TDD-PATTERNS.md` - TDD patterns
- `10-GAME-SYSTEMS-IMPLEMENTATION-PLAN.md` - Implementation roadmap

---

## 🧪 Testing

### Test Suite Status

**Game Tests:**
- **880 tests passing** (98.7% pass rate)
- **78% code coverage** (target: 90%)
- Execution time: ~3.5 seconds

**Engine Tests:**
- Comprehensive unit tests for all engine systems
- Integration tests for system interactions

### Running Tests

```bash
# Game tests
pytest tests/
pytest tests/ --cov=game --cov-report=html

# Engine tests
cd engine && pytest tests/
cd engine && pytest tests/ --cov=engine --cov-report=html

# All tests
pytest tests/ engine/tests/
```

---

## 🛠️ Development Commands

```bash
# Testing
make test              # Run game tests
make test-cov          # Run tests with coverage
make test-combat       # Run combat tests
make test-character    # Run character tests

# Code Quality
make lint              # Run flake8 and pylint
make typecheck         # Run mypy type checking
make format            # Format code with black/isort
make check             # Run all quality checks

# Utilities
make clean             # Remove generated files
make run               # Run the game
```

---

## 📊 Project Status

**Current Version:** 0.2.0
**Status:** ✅ Production Ready
**Test Coverage:** 78% (target: 90%)
**Grade:** A-

### Completed Phases
- ✅ Phase 1: Core Framework (Game Loop, World Map, Inventory)
- ✅ Phase 2: Character & Quest Systems
- ✅ Phase 3: Combat & Stealth
- ✅ Phase 4: Advanced Systems (Crafting, Companions, Districts)
- ✅ Phase 5: Polish & Meta Systems (Achievements, AI Director, Save/Load)
- ✅ Code Quality Improvements (Bug fixes, Refactoring, Type Safety)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow code standards (see [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md))
4. Write tests for new features
5. Ensure all tests pass (`make test`)
6. Run quality checks (`make check`)
7. Commit changes (`git commit -m 'feat: Add amazing feature'`)
8. Push to branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

### Code Standards
- Use explicit imports (no `from module import *`)
- Keep function complexity < 10
- Add type hints to all public functions
- Write tests for new functionality
- Maintain or improve code coverage
- Follow PEP 8 style guide

---

## 📝 License

MIT License - Feel free to use this engine for your own projects!

---

## 🙏 Acknowledgments

- Built with Python and pygame
- Testing with pytest
- Type checking with mypy
- Code quality with flake8 and pylint
- Inspired by classic turn-based strategy games
- AI-assisted tools for modern game development

---

## 📧 Contact

- GitHub: [@Bustaboy](https://github.com/Bustaboy)
- Project: [neon-collapse](https://github.com/Bustaboy/neon-collapse)
- Issues: [Report a bug](https://github.com/Bustaboy/neon-collapse/issues)

---

<div align="center">

**Made with ❤️ using Neon Works**

[Engine Docs](engine/README.md) • [Game Docs](game/README.md) • [Contributing](#contributing)

</div>
