# NeonWorks

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/license-CC%20BY--NC--SA%204.0-green.svg)
![Code Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen.svg)
![Status](https://img.shields.io/badge/status-production%20ready-success.svg)
![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)

**A comprehensive, production-ready 2D game engine for turn-based strategy games, JRPGs, and base-building games with survival elements.**

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Examples](#-examples) • [Contributing](#-contributing)

</div>

---

## 📊 Project Stats

- **280+** Python files
- **50,000+** lines of production code
- **85%+** test coverage
- **30+** visual editor tools
- **4** built-in project templates
- **13** built-in ECS components
- **11+** specialized game systems

## 🎯 What is NeonWorks?

NeonWorks is a **comprehensive, project-based 2D game engine** built with Python and Pygame, designed for creating turn-based strategy games, JRPGs, and base-building games with survival elements.

Originally developed for *Neon Collapse*, NeonWorks is now a standalone, reusable engine that separates engine code from game content, allowing you to create multiple games with a single engine installation.

### 🎮 Project-Based Architecture

The engine is **completely separate** from game content, making it highly reusable:

- **Engine** (this repository) - Generic, reusable game engine with no game-specific code
- **Projects** (your game folders) - Individual game projects with their own assets, levels, and configuration
- **Project Files** (`project.json`) - Configuration files that link game content to the engine

This architecture allows you to:
- ✅ Create multiple games using the same engine
- ✅ Version control engine and game content separately
- ✅ Share projects without sharing the engine
- ✅ Iterate on game design without touching engine code
- ✅ Export standalone executables with encryption and licensing
- ✅ Use a Unity Hub-style visual launcher for project management

---

## ✨ Features

### 🎨 Visual Editor Tools (30+ Editors)

All editors accessible via **F-key hotkeys** and **Ctrl/Shift combos**:

| Hotkey | Editor | Description |
|--------|--------|-------------|
| **F1** | Debug Console | Real-time debugging and command execution |
| **F2** | Settings | Engine and project settings |
| **F3** | Building UI | Building placement and management |
| **F4** | Level Builder | Visual tile placement and level design |
| **F5** | Event Editor | Create and edit game events |
| **F6** | Database Editor | Game data database editor |
| **F7** | Character Generator | AI-assisted character creation |
| **F8** | Quest Editor | Quest and dialogue tree editor |
| **F9** | Combat UI | Turn-based combat interface |
| **F10** | Game HUD | In-game heads-up display |
| **F11** | Autotile Editor | Intelligent autotiling system |
| **Ctrl+M** | Map Manager | Multi-map project management |
| **Ctrl+E** | Event Editor | Visual event scripting |
| **Ctrl+D** | Database Manager | Game data database editor |
| **Ctrl+G** | Character Generator | AI-powered character creation |
| **Ctrl+Space** | AI Assistant | AI-powered development assistant |

> Note: The Asset Browser and Project Manager are accessible from the workspace toolbar rather than direct F-key shortcuts.

**Map Tools** (activated in Map Editor):
- **P** - Pencil Tool • **E** - Eraser Tool • **F** - Fill Tool
- **S** - Select Tool • **B** - Stamp Tool • **R** - Shape Tool
- **I** - Eyedropper Tool

See [docs/keyboard_shortcuts.md](docs/keyboard_shortcuts.md) for complete list.

### 🏗️ Core Engine Features

#### Entity Component System (ECS)
- Flexible, data-oriented architecture
- **13 built-in components**: Transform, GridPosition, Sprite, Health, Survival, Building, ResourceStorage, Navmesh, TurnActor, Collider, RigidBody, Movement, JRPGStats
- Easy custom component creation
- Efficient entity queries and filtering
- Tag-based entity organization

#### Game Loop & State Management
- Fixed timestep update (60 FPS) with variable rendering
- Deterministic physics and game logic
- Scene management with smooth transitions
- State machine for game states
- Event-driven architecture (pub/sub pattern)

#### Project System
- Load and manage multiple game projects
- JSON-based configuration
- Hot-reloading of assets and configs
- Save/load system with entity serialization
- Crash recovery and undo/redo system

### 🎮 Game Systems

#### JRPG Features
- **Battle System** - Complete ATB-style turn-based combat
- **Magic System** - Spell casting with MP management
- **Random Encounters** - Zone-based encounter system
- **Puzzle System** - Dungeon puzzles and mechanics
- **Boss AI** - Intelligent boss battle system
- **Character Stats** - HP, MP, Attack, Defense, Speed, Magic
- **Battle Transitions** - Smooth transitions to/from battle
- **Exploration** - Tile-based exploration with dialogue

See [JRPG_FEATURES.md](JRPG_FEATURES.md) for complete JRPG documentation.

#### Strategy & Base Building
- **Turn-Based Strategy** - Grid-based tactical combat with action points
- **Base Building** - Construction and upgrade system
- **Survival Mechanics** - Hunger, thirst, energy management
- **Resource Management** - Gathering, storage, and consumption
- **Zone System** - Multi-zone world management

#### AI & Pathfinding
- **A* Pathfinding** - Efficient grid-based pathfinding
- **Navmesh System** - Automatic navmesh generation
- **AI Behaviors** - Enemy AI with targeting and tactics
- **Procedural Generation** - AI-powered level generation

### 🎨 Rendering & Graphics

- **2D Tile-Based Renderer** - Efficient multi-layer rendering
- **Camera System** - Pan, zoom, entity following
- **Animation System** - Sprite-based animations
- **Particle Effects** - Combat and environmental effects
- **UI System** - ImGui-style immediate mode UI with widget framework
- **Theme System** - Customizable UI themes
- **Tilemap System** - Autotiling and tileset management
- **Layer Management** - Multi-layer editing with visibility controls

### 📦 Export & Distribution

- **Executable Bundler** - Create standalone executables with PyInstaller
- **Code Protection** - Bytecode compilation and encryption
- **Installer Builder** - Generate installation packages
- **License Validation** - Optional licensing system for commercial distribution
- **Asset Encryption** - Protect game assets from extraction
- **Package Format** - Custom encrypted package format

### 🤖 AI-Powered Tools

- **AI Level Builder** - Generate levels from text descriptions
- **AI Navmesh Generator** - Automatic navmesh generation
- **AI Quest Writer** - Generate quests and dialogue trees
- **AI Character Generator** - Create characters with AI assistance
- **AI Animator** - Animation generation and editing
- **AI Asset Tools** - Asset editing and enhancement

---

## 🚀 Quick Start

NeonWorks is designed to open through the **visual launcher** first. Use the launcher to browse, create, and open projects; drop to the CLI when you need scripting or automation.

### Prerequisites

```bash
# Python 3.10 or higher required
python --version

# Install dependencies
pip install -r requirements.txt

# (Optional) Install development tools
pip install -r requirements-dev.txt

# (Optional) Install pre-commit hooks
pre-commit install
```

### Using the Visual Launcher (Primary)

The easiest way to get started is with the **NeonWorks Launcher** - a visual project hub similar to Unity Hub.

```bash
# Start the launcher
python -m neonworks.launcher

# Or use the convenience scripts:
./launch_neonworks.sh        # Linux/Mac wrapper for `python -m neonworks.launcher`
launch_neonworks.bat         # Windows wrapper for `python -m neonworks.launcher`
```

**Launcher Features:**
- Visual project browser with project cards
- Create new projects from 4 built-in templates
- **Two clear actions per project:** Edit in Editor (default) or Run Game
- Double-click a project card to open the editor
- Recent projects tracking
- Template preview and selection

See [LAUNCHER_README.md](LAUNCHER_README.md) for detailed launcher documentation.

### Alternative: Command Line (advanced/scripting)

```bash
# Create a new project
python cli.py create my_game --template turn_based_rpg

# List available templates
python cli.py templates

# List all projects
python cli.py list

# Open a project in editor mode
python main.py my_game --editor

# Run a project in play mode
python main.py my_game --run

# Export a project to executable
python export_cli.py export my_game
```
### 📝 Available Templates

1. **Basic Game** - Minimal starter template
2. **Turn-Based RPG** - Grid-based tactical combat
3. **Base Builder** - Base building with survival mechanics
4. **JRPG Demo** - Complete JRPG with battles, magic, and encounters

---

## 🏗️ Architecture

### Directory Structure

```
neonworks/                    # Root package (use neonworks.* imports)
├── core/                     # Core engine systems (17 files, ~4,200 LOC)
│   ├── ecs.py               # Entity Component System - HEART OF ENGINE
│   ├── game_loop.py         # Fixed timestep game loop
│   ├── events.py            # Event system (pub/sub)
│   ├── state.py             # State machine
│   ├── scene.py             # Scene management
│   ├── project.py           # Project loading/management
│   ├── serialization.py     # Save/load system
│   ├── hotkey_manager.py    # Global hotkey system
│   ├── undo_manager.py      # Undo/redo for editors
│   └── crash_recovery.py    # Automatic crash recovery
│
├── rendering/               # Graphics systems (8 files, ~3,600 LOC)
│   ├── renderer.py          # 2D tile-based renderer
│   ├── camera.py            # Camera (pan, zoom, follow)
│   ├── ui.py                # UI rendering
│   ├── assets.py            # Asset loading/caching
│   ├── animation.py         # Animation system
│   └── tilemap.py           # Tilemap rendering
│
├── systems/                 # Game logic systems (11 files, ~5,000 LOC)
│   ├── turn_system.py       # Turn-based strategy
│   ├── base_building.py     # Building construction
│   ├── survival.py          # Hunger/thirst/energy
│   ├── pathfinding.py       # A* pathfinding
│   ├── jrpg_battle_system.py  # JRPG combat
│   ├── magic_system.py      # Spell casting
│   ├── random_encounters.py # Random battles
│   ├── puzzle_system.py     # Dungeon puzzles
│   └── boss_ai.py           # Boss battle AI
│
├── ui/                      # Visual editors (40+ files, ~15,000+ LOC)
│   ├── master_ui_manager.py # UI coordinator (F-key hotkeys)
│   ├── level_builder_ui.py  # Level editor (F4)
│   ├── quest_editor_ui.py   # Quest/dialogue editor (F6)
│   ├── asset_browser_ui.py  # Asset management (F7)
│   ├── map_tools/           # Map editing tools (21 files)
│   └── map_components/      # Map UI components
│
├── editor/                  # AI-powered tools (4 files, ~1,800 LOC)
│   ├── ai_navmesh.py        # AI navmesh generation
│   ├── ai_level_builder.py  # AI level generation
│   ├── ai_writer.py         # AI quest/dialogue writing
│   └── procedural_gen.py    # Procedural generation
│
├── export/                  # Build & packaging (7 files, ~2,100 LOC)
│   ├── exporter.py
│   ├── executable_bundler.py
│   ├── code_protection.py
│   └── package_format.py
│
├── engine/                  # Engine subsystems (separate namespace)
│   ├── core/                # Event interpreter
│   ├── data/                # Database management
│   └── tools/               # Character generator, importers
│
├── tests/                   # Comprehensive test suite (18 files, 9,400+ LOC)
├── docs/                    # Documentation (40+ files, 8,000+ LOC)
├── examples/                # Example projects (3 projects)
└── templates/               # Project templates (4 templates)
```

### Core Patterns

**Entity Component System**
```python
from neonworks.core.ecs import World, Entity, Transform, Health

# Create world
world = World()

# Create entity
player = world.create_entity("Player")

# Add components
player.add_component(Transform(x=0, y=0))
player.add_component(Health(hp=100, max_hp=100))
player.add_tag("player")

# Query entities
players = world.get_entities_with_tag("player")
entities_with_health = world.get_entities_with_component(Health)
```

**Event System**
```python
from neonworks.core.events import get_event_manager

events = get_event_manager()

# Subscribe to events
def on_player_died(data):
    print(f"Player {data['entity_id']} died!")

events.subscribe("player_died", on_player_died)

# Emit events
events.emit("player_died", {"entity_id": player.id})
```

---

## 📚 Documentation

### Core Documentation
- **[CLAUDE.md](CLAUDE.md)** - AI assistant development guide
- **[JRPG_FEATURES.md](JRPG_FEATURES.md)** - Complete JRPG system documentation
- **[LAUNCHER_README.md](LAUNCHER_README.md)** - Visual launcher guide

### Project Documentation (docs/project/)
- **[STATUS.md](docs/project/STATUS.md)** - Implementation status (50,000+ LOC analysis)
- **[DEVELOPER_GUIDE.md](docs/project/DEVELOPER_GUIDE.md)** - Development best practices
- **[FEATURE_CHECKLIST.md](docs/project/FEATURE_CHECKLIST.md)** - Feature implementation status
- **[CHANGELOG.md](docs/project/CHANGELOG.md)** - Version history
- **[KNOWN_ISSUES.md](docs/project/KNOWN_ISSUES.md)** - Known bugs and limitations

### Guides & Tutorials
- **[docs/getting_started.md](docs/getting_started.md)** - Getting started tutorial
- **[docs/keyboard_shortcuts.md](docs/keyboard_shortcuts.md)** - Complete keyboard shortcuts
- **[docs/map_editor_guide.md](docs/map_editor_guide.md)** - Map editor tutorial
- **[docs/RECIPES.md](docs/RECIPES.md)** - Common patterns and solutions
- **[docs/tutorials/](docs/tutorials/)** - Step-by-step tutorials

---

## 🎯 Examples

The engine includes several example projects demonstrating various features:

### Example Projects (examples/)
1. **simple_rpg/** - Basic RPG with exploration and combat
2. **jrpg_demo/** - Complete JRPG with battles, magic, and encounters
3. **visual_ui_demo.py** - UI system demonstration

### Running Examples
```bash
# Run the JRPG demo
python main.py jrpg_demo

# Run the simple RPG
python main.py simple_rpg

# Run the UI demo
python examples/visual_ui_demo.py
```

---

## 🛠️ Development

### Code Quality

We maintain high code quality standards:

- **Code Formatter:** Black (88 character line length)
- **Import Sorter:** isort (black-compatible profile)
- **Linter:** Flake8 (max line length: 127)
- **Type Checker:** MyPy (partial enforcement)
- **Test Coverage:** 85%+ target
- **Pre-commit Hooks:** Automatic formatting and linting

### Development Commands

```bash
# Using Makefile (recommended)
make help          # Show all commands
make format        # Auto-format with black & isort
make format-check  # Check formatting without changes
make lint          # Run flake8 linter
make test          # Run tests
make test-cov      # Run tests with coverage report
make clean         # Clean build artifacts
make install       # Install all dependencies

# Manual commands
pytest tests/ -v                           # Run tests
pytest tests/ --cov=. --cov-report=html   # Coverage report
black .                                    # Format code
isort .                                    # Sort imports
flake8 .                                   # Lint code
```

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
pytest tests/test_ecs.py -v

# Run tests in parallel
pytest tests/ -n auto
```

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Make** your changes following our code standards
4. **Add** tests for new functionality
5. **Run** quality checks: `make format && make lint && make test`
6. **Commit** with conventional commits: `git commit -m "feat: add amazing feature"`
7. **Push** to your fork: `git push origin feature/amazing-feature`
8. **Open** a Pull Request

### Contribution Guidelines

- Follow the code style (Black, isort)
- Add docstrings to all public functions
- Include type hints for function signatures
- Write tests for new features (aim for 85%+ coverage)
- Update documentation for user-facing changes
- Use conventional commit messages

See [CLAUDE.md](CLAUDE.md) for detailed development guidelines.

---

## 📋 Project Configuration

Each project has a `project.json` file:

```json
{
  "metadata": {
    "name": "My Awesome Game",
    "version": "1.0.0",
    "description": "A cool JRPG",
    "author": "Developer Name"
  },
  "settings": {
    "window_title": "My Awesome Game",
    "window_width": 1280,
    "window_height": 720,
    "tile_size": 32,
    "enable_base_building": false,
    "enable_survival": false,
    "enable_turn_based": true,
    "building_definitions": "config/buildings.json",
    "item_definitions": "config/items.json",
    "character_definitions": "config/characters.json"
  },
  "custom_data": {
    "theme": "fantasy",
    "difficulty_levels": ["easy", "normal", "hard"]
  }
}
```

---

## 📦 Dependencies

### Runtime Dependencies
- **pygame** 2.5.2 - Game development framework
- **numpy** ≥1.24.0 - Numerical computing
- **Pillow** ≥10.0.0 - Image processing
- **PyYAML** ≥6.0.3 - YAML parsing
- **cryptography** ≥46.0.0 - Encryption for export
- **pyinstaller** ≥6.0.0 - Executable bundling

### Development Dependencies
- **pytest** 7.4.3 - Testing framework
- **pytest-cov** 4.1.0 - Coverage reporting
- **black** 25.11.0 - Code formatting
- **isort** 7.0.0 - Import sorting
- **flake8** 7.3.0 - Linting
- **mypy** 1.7.1 - Type checking
- **pre-commit** 3.5.0 - Git hooks

See [requirements.txt](requirements.txt) and [requirements-dev.txt](requirements-dev.txt) for complete lists.

---

## 📜 License

This project is licensed under the **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0)**.

See [LICENSE](LICENSE) for full license text.

**In summary:**
- ✅ You can use, modify, and distribute this engine
- ✅ You must give appropriate credit
- ✅ You must distribute derivatives under the same license
- ❌ You cannot use it for commercial purposes without permission

For commercial licensing, please contact the maintainers.

---

## 🙏 Acknowledgments

- Built with [Pygame](https://www.pygame.org/)
- Inspired by classic JRPGs and turn-based strategy games
- Originally developed for *Neon Collapse*

---

## 📞 Support & Community

- **Documentation:** [docs/](docs/)
- **Issues:** [GitHub Issues](https://github.com/Bustaboy/neonworks/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Bustaboy/neonworks/discussions)

---

<div align="center">

**[⬆ Back to Top](#neonworks)**

Made with ❤️ by the NeonWorks Team

</div>
