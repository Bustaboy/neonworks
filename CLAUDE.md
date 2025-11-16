# CLAUDE.md - AI Assistant Guide for NeonWorks

**Version:** 1.1
**Last Updated:** 2025-11-16
**Engine Version:** 0.1.0
**Purpose:** Guide for AI assistants working on the NeonWorks 2D game engine

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture & Structure](#2-architecture--structure)
3. [Development Workflow](#3-development-workflow)
4. [Code Standards & Conventions](#4-code-standards--conventions)
5. [Testing Strategy](#5-testing-strategy)
6. [Common Tasks & Patterns](#6-common-tasks--patterns)
7. [Critical Information](#7-critical-information)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Project Overview

### What is NeonWorks?

NeonWorks is a **comprehensive, project-based 2D game engine** built with Python and Pygame, designed for creating turn-based strategy games, JRPGs, and base-building games with survival elements. The project is under active development, with new features continually being designed and added.

**Note:** The codebase uses two main package namespaces:
- `neonworks.*` - Core engine systems (ECS, rendering, systems, UI)
- `neonworks.engine.*` - Specialized subsystems (event interpreter, database, character generator)

See [engine/README.md](engine/README.md) for details on the engine subsystems.

**Key Characteristics:**
- **280+ Python files**, ~50,000+ lines of production code
- **Entity Component System (ECS)** architecture
- **Project-based** design (engine separate from game content)
- **Visual editor tools** (30+ UI editors with F-key hotkeys)
- **Complete JRPG framework** (battle system, magic, encounters, puzzles)
- **Export pipeline** (standalone executables, encryption, licensing)
- **Visual launcher** (Unity Hub-style project manager)
- **Production-ready** status with comprehensive testing

### Project Philosophy

1. **Separation of Concerns**: Engine code is completely separate from game content
2. **Data-Driven**: Game behavior defined through JSON configuration files
3. **Reusability**: One engine, multiple game projects
4. **Developer Experience**: Rich visual tools for non-programmers
5. **Quality**: 85%+ test coverage, type hints, comprehensive docs

---

## 2. Architecture & Structure

### 2.1 Directory Organization

```
neonworks/                    # Root directory (note: NOT "engine/")
├── config/                  # Configuration files
│   └── ai_config.py         # Auto-configuration for AI hardware
│
├── core/                     # Core engine systems (17 files, ~4,200 LOC)
│   ├── ecs.py               # Entity Component System - HEART OF ENGINE
│   ├── game_loop.py         # Fixed timestep game loop
│   ├── events.py            # Event system (pub/sub)
│   ├── state.py             # State machine
│   ├── scene.py             # Scene management
│   ├── project.py           # Project loading/management
│   ├── serialization.py     # Save/load system
│   ├── validation.py        # Data validation
│   ├── event_commands.py    # Event command system
│   ├── event_triggers.py    # Event trigger system
│   ├── hotkey_manager.py    # Global hotkey management system
│   ├── undo_manager.py      # Undo/redo system for editors
│   ├── undo_persistence.py  # Undo history persistence
│   ├── crash_recovery.py    # Automatic crash recovery
│   ├── error_handler.py     # Global error handling
│   └── command_registry.py  # Command pattern registry
│
├── rendering/               # Graphics & visual systems (9 files, ~4,000 LOC)
│   ├── renderer.py          # 2D tile-based renderer
│   ├── camera.py            # Camera (pan, zoom, follow)
│   ├── ui.py                # UI rendering
│   ├── assets.py            # Asset loading/caching
│   ├── asset_pipeline.py    # Asset processing
│   ├── animation.py         # Animation system
│   ├── tilemap.py           # Tilemap rendering
│   ├── autotiles.py         # Autotile system for seamless tiles
│   └── particles.py         # Particle effects
│
├── systems/                 # Game logic systems (11 files, ~5,000 LOC)
│   ├── turn_system.py       # Turn-based strategy
│   ├── base_building.py     # Building construction
│   ├── survival.py          # Hunger/thirst/energy
│   ├── pathfinding.py       # A* pathfinding
│   ├── exploration.py       # Tile-based exploration
│   ├── jrpg_battle_system.py  # JRPG combat
│   ├── magic_system.py      # Spell casting
│   ├── random_encounters.py # Random battles
│   ├── puzzle_system.py     # Dungeon puzzles
│   ├── boss_ai.py           # Boss battle AI
│   └── zone_system.py       # Zone management
│
├── ui/                      # Visual editor tools (40+ files, ~15,000+ LOC)
│   ├── master_ui_manager.py # UI coordinator (F1-F12 hotkeys)
│   ├── asset_browser_ui.py  # Asset management (F7)
│   ├── level_builder_ui.py  # Level editor (F4)
│   ├── map_manager_ui.py    # Map management (Ctrl+M)
│   ├── navmesh_editor_ui.py # Navmesh editor (F5)
│   ├── quest_editor_ui.py   # Quest/dialogue editor (F6)
│   ├── project_manager_ui.py # Project management (F8)
│   ├── settings_ui.py       # Settings (F2)
│   ├── debug_console_ui.py  # Debug console (F1)
│   ├── game_hud.py          # In-game HUD (F10)
│   ├── combat_ui.py         # Combat interface (F9)
│   ├── building_ui.py       # Building placement (F3)
│   ├── jrpg_battle_ui.py    # JRPG battle UI
│   ├── magic_menu_ui.py     # Magic spell menu
│   ├── exploration_ui.py    # Exploration dialogue
│   ├── battle_transitions.py # Battle transitions
│   ├── ui_system.py         # Widget framework
│   ├── workspace_system.py  # Workspace/layout management
│   ├── workspace_toolbar.py # Toolbar system
│   ├── shortcuts_overlay_ui.py # Keyboard shortcuts overlay
│   ├── themes.py            # Theme system
│   ├── layer_panel_ui.py    # Layer management panel
│   ├── history_viewer_ui.py # Undo/redo history viewer
│   ├── tileset_picker_ui.py # Tileset selection UI
│   ├── autotile_editor_ui.py # Autotile editor
│   ├── autotile_tool.py     # Autotile tools
│   ├── event_editor_ui.py   # Event editor
│   ├── database_manager_ui.py # Database editor
│   ├── character_generator_ui.py # Character generator
│   ├── ai_animator_ui.py    # AI animation tool
│   ├── ai_assistant_panel.py # AI assistant panel
│   ├── ai_generator_tool.py # AI generation tools
│   ├── ai_vision_context.py # AI vision integration
│   ├── ai_asset_editor.py   # AI asset editing
│   ├── ai_asset_inspector.py # AI asset inspection
│   ├── ai_tileset_ui.py     # AI tileset tools
│   ├── map_tools/           # Map editing tools (21+ files)
│   │   ├── pencil_tool.py   # Pencil drawing tool
│   │   ├── eraser_tool.py   # Eraser tool
│   │   ├── fill_tool.py     # Bucket fill tool
│   │   ├── select_tool.py   # Selection tool
│   │   ├── stamp_tool.py    # Stamp/clone tool
│   │   ├── shape_tool.py    # Shape drawing tool
│   │   ├── eyedropper_tool.py # Color picker tool
│   │   ├── settings_panel.py # Tool settings panel
│   │   ├── themes.py        # Theming for map tools
│   │   └── undo_manager.py  # Undo/redo for map tools
│   └── map_components/      # Map UI components (4 files)
│       ├── minimap.py       # Minimap widget
│       ├── map_properties.py # Map properties panel
│       └── tool_options.py  # Tool options panel
│
├── gameplay/                # Game-specific systems (4 files, ~2,000 LOC)
│   ├── character_controller.py # Player character state
│   ├── jrpg_combat.py       # JRPG combat logic
│   ├── movement.py          # Grid-based movement
│   └── puzzle_objects.py    # Components for dungeon puzzles
│
├── editor/                  # AI & procedural generation tools (12+ files, ~4,000+ LOC)
│   ├── sd_sprite_generator.py # Stable Diffusion sprite generator
│   ├── ai_tileset_generator.py # AI-powered tileset generation
│   ├── ai_layer_generator.py  # AI map layer generation
│   ├── ai_animator.py         # AI-assisted animation tools
│   ├── ai_animation_interpreter.py # Interprets AI animation scripts
│   ├── ai_navmesh.py          # AI navmesh generation
│   ├── ai_level_builder.py    # AI level generation
│   ├── ai_writer.py           # AI quest/dialogue writing
│   ├── style_transfer.py      # Asset style transfer tools
│   ├── procedural_gen.py      # Procedural content generation
│   ├── physics_animation.py   # Physics-based animation
│   └── animation_script_parser.py # Parses animation scripts
│
├── export/                  # Build & packaging (7 files, ~2,100 LOC)
│   ├── exporter.py
│   ├── package_builder.py
│   ├── executable_bundler.py
│   ├── installer_builder.py
│   ├── code_protection.py
│   ├── package_format.py
│   └── package_loader.py
│
├── licensing/               # License validation (3 files, ~650 LOC)
│   ├── license_key.py       # License key structure
│   ├── hardware_id.py       # Generates hardware identifiers
│   └── license_validator.py # Validates license keys
│
├── physics/                 # Collision & rigidbody (3 files, ~900 LOC)
│   ├── collision.py         # Collision detection system
│   └── rigidbody.py         # Rigidbody physics
│
├── input/                   # Input management (2 files, ~400 LOC)
│   └── input_manager.py     # Handles keyboard/mouse/gamepad
│
├── audio/                   # Audio playback (2 files, ~700 LOC)
│   └── audio_manager.py     # Manages music and sound effects
│
├── ai/                      # AI systems (8+ files, ~2,000+ LOC)
│   ├── pathfinding.py       # A* pathfinding
│   └── backends/            # Pluggable AI backends
│       ├── llm_backend.py   # LLM backend ABC
│       ├── image_backend.py # Image backend ABC
│       ├── openai_backend.py # OpenAI API integration
│       ├── anthropic_backend.py # Anthropic API integration
│       ├── llama_cpp_backend.py # Llama.cpp local inference
│       └── diffusers_backend.py # Diffusers local inference
│
├── data/                    # Data management (6 files, ~2,800 LOC)
│   ├── config_loader.py     # JSON config loading
│   ├── serialization.py     # Save/load utilities
│   ├── map_layers.py        # Layer management system
│   ├── tileset_manager.py   # Tileset management
│   ├── map_manager.py       # Map management system
│   └── ai_map_integration.py # AI-powered map commands & procedural gen
│
├── tests/                   # Test suite (18 files, 9,400+ LOC)
│   └── test_*.py            # Comprehensive tests
│
├── examples/                # Example projects (3 projects)
│   ├── simple_rpg/
│   ├── jrpg_demo/
│   └── visual_ui_demo.py
│
├── templates/               # Project templates (3 templates)
│   ├── basic_game/
│   ├── turn_based_rpg/
│   └── base_builder/
│
├── engine/                  # Engine subsystems (separate namespace)
│   ├── core/                # Event interpreter & event data
│   ├── data/                # Database management system
│   ├── tools/               # Character generator, map importers
│   ├── ui/                  # Specialized UIs (event, database, char gen)
│   └── templates/           # Event command templates
│
├── docs/                    # Documentation (~8,000+ LOC)
│   └── project/             # Project documentation (moved from root)
│       ├── STATUS.md        # Implementation status
│       ├── DEVELOPER_GUIDE.md
│       ├── CHANGELOG.md
│       └── ...              # Additional project docs
│
├── scripts/                 # Utility scripts & benchmarks
├── utils/                   # Common utilities (3 files, ~300 LOC)
│   ├── profiler.py          # Code profiling tools
│   └── performance_monitor.py # Performance monitoring
│
├── examples/                # Example projects & demos
└── backups/                 # Backup directory

# Entry points
├── launcher.py              # Visual launcher (Unity Hub-style)
├── launch_neonworks.sh      # Launcher script (Linux/Mac)
├── launch_neonworks.bat     # Launcher script (Windows)
├── main.py                  # Game launcher
├── cli.py                   # CLI interface
├── export_cli.py            # Export CLI
├── license_cli.py           # License CLI
├── setup.py                 # Package setup
├── pyproject.toml           # Build config
├── requirements.txt         # Dependencies
├── requirements-dev.txt     # Dev dependencies
├── Makefile                 # Development commands
└── .pre-commit-config.yaml  # Pre-commit hooks
```

### 2.2 Core Architecture Patterns

#### Entity Component System (ECS)

**File:** `core/ecs.py:1-351`

**Key Classes:**
- `Entity` - Container with components and tags
- `Component` - Pure data containers (base class)
- `System` - Logic processors (base class)
- `World` - Entity and system manager

**Built-in Components (13):**
```python
Transform(position, rotation, scale)      # Spatial position
GridPosition(x, y)                         # Grid-based position
Sprite(texture, visible, flip_x, flip_y)  # Visual representation
Health(hp, max_hp)                         # Health points
Survival(hunger, thirst, energy)           # Survival stats
Building(type, placed_at, level)           # Building data
ResourceStorage(resources)                 # Resource inventory
Navmesh(walkable_cells)                    # Navigation data
TurnActor(ap, initiative)                  # Turn-based data
Collider(shape, width, height)             # Collision
RigidBody(velocity, acceleration, mass)    # Physics
Movement(speed, direction, anim_state)     # Movement
JRPGStats(hp, mp, attack, defense, ...)    # JRPG stats
```

**Usage Pattern:**
```python
# Create entity
world = World()
entity = world.create_entity("Player")

# Add components
entity.add_component(Transform(x=0, y=0))
entity.add_component(GridPosition(x=5, y=5))
entity.add_component(JRPGStats(hp=100, mp=50, level=1))
entity.add_tag("player")

# Query entities
players = world.get_entities_with_tag("player")
entities_with_health = world.get_entities_with_component(Health)
```

#### Game Loop

**File:** `core/game_loop.py:1-225`

**Pattern:** Fixed timestep with variable rendering

```
Main Loop:
├─ Fixed Update (0+ times/frame at 60Hz)
│  ├─ Process input
│  ├─ Update physics
│  └─ Update game logic
│
├─ Render (once per frame)
│  ├─ Clear screen
│  ├─ Render world
│  └─ Render UI
│
└─ FPS limiting
```

**Benefits:** Deterministic physics, smooth rendering, network-friendly

#### Event System

**File:** `core/events.py:1-153`

**Pattern:** Publisher-subscriber (observer)

```python
from neonworks.core.events import get_event_manager

events = get_event_manager()

# Subscribe
def on_player_died(data):
    print(f"Player {data['entity_id']} died!")

events.subscribe("player_died", on_player_died)

# Emit
events.emit("player_died", {"entity_id": player.id})
```

---

## 3. Development Workflow

### 3.1 Setup & Installation

```bash
# Clone repository
git clone https://github.com/Bustaboy/neonworks.git
cd neonworks

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests to verify setup
pytest tests/ -v
```

### 3.2 Common Commands

```bash
# Using Makefile (recommended)
make help          # Show all commands
make format        # Auto-format with black & isort
make format-check  # Check formatting without changes
make lint          # Run flake8 linter
make test          # Run tests
make test-cov      # Run tests with coverage
make clean         # Clean build artifacts
make install       # Install all dependencies

# Manual commands
pytest tests/ -v                           # Run tests
pytest tests/ --cov=. --cov-report=html   # Coverage report
black .                                    # Format code
isort .                                    # Sort imports
flake8 . --exclude=.git,__pycache__       # Lint code

# Running the engine
python main.py <project_name>              # Launch game
python cli.py create-project <name>        # Create project
python export_cli.py export <project>      # Export project
```

### 3.3 Git Workflow

**Branch Naming:**
```
feature/add-new-system
bugfix/fix-collision-detection
refactor/simplify-ecs
docs/update-architecture
test/add-coverage-for-rendering
```

**Commit Messages (Conventional Commits):**
```
feat: Add visual event editor with node canvas
fix: Correct navmesh generation for large buildings
refactor: Simplify ECS component query system
docs: Update CLAUDE.md with new conventions
test: Add tests for JRPG battle system
style: Apply black formatting to ui/ directory
```

**Pre-commit Checklist:**
- [ ] All tests pass (`make test`)
- [ ] Code is formatted (`make format`)
- [ ] No lint errors (`make lint`)
- [ ] New functions have docstrings
- [ ] New code has tests (aim for 85%+ coverage)

### 3.4 Development Branch

**Current Development Branch:**
```
claude/claude-md-mi1dk2gcjszbi0hi-01LsdSqUG3TJMGgMk9fHrAD8
```

**Important:**
- Always develop on feature branches starting with `claude/`
- Branch name MUST match the session ID for push to succeed
- Commit frequently with clear messages
- Push with: `git push -u origin <branch-name>`
- Create PR when ready for review

### 3.5 Using the Visual Launcher

**Starting the Launcher:**
```bash
# Recommended - Visual launcher (Unity Hub-style)
python launcher.py

# Or use convenience scripts
./launch_neonworks.sh        # Linux/Mac
launch_neonworks.bat         # Windows
```

**Launcher Features:**
- Visual project browser with project cards
- One-click project creation from templates
- Recent projects tracking
- Quick launch into editor mode
- Template selection (4 built-in templates)

See [LAUNCHER_README.md](LAUNCHER_README.md) for detailed documentation.

---

## 4. Code Standards & Conventions

### 4.1 Python Style Guide

**Formatter:** Black (line length: 88 characters)
**Import Sorter:** isort (black-compatible profile)
**Linter:** Flake8 (max line length: 127)
**Type Checker:** MyPy (partial enforcement)

### 4.2 Import Structure

**CRITICAL: Use `neonworks.*` namespace (NOT `engine.*`)**

```python
# ✅ CORRECT - Use neonworks.*
from neonworks.core.ecs import Entity, Component, System, World
from neonworks.rendering.renderer import Renderer
from neonworks.systems.jrpg_battle_system import JRPGBattleSystem
from neonworks.ui.master_ui_manager import MasterUIManager

# ❌ WRONG - Do NOT use engine.*
from engine.core.ecs import World  # DEPRECATED - Will not work!
```

**Import Order (isort):**
```python
# 1. Future imports
from __future__ import annotations

# 2. Standard library
import os
import sys
from typing import Dict, List, Optional

# 3. Third-party
import pygame
import numpy as np

# 4. First-party (neonworks)
from neonworks.core.ecs import World
from neonworks.rendering.renderer import Renderer

# 5. Local/relative (rare, avoid if possible)
from .utils import helper_function
```

**DO:**
- Use explicit imports: `from config import MAX_HP, BASE_DAMAGE`
- Group related imports: `from typing import Dict, List, Optional`
- Import only what you need

**DON'T:**
- Star imports: `from config import *`
- Relative imports beyond parent: `from ../../module import X`
- Circular imports (use TYPE_CHECKING if needed)

### 4.3 Naming Conventions

```python
# Classes: PascalCase
class TurnSystem(System):
    pass

class JRPGStats(Component):
    pass

# Functions/methods: snake_case
def calculate_damage(attacker, defender):
    pass

def get_entities_with_tag(tag: str):
    pass

# Constants: UPPER_SNAKE_CASE
MAX_ACTION_POINTS = 10
GRID_WIDTH = 32
BASE_MOVEMENT_RANGE = 5

# Private methods: _leading_underscore
def _internal_helper(self):
    pass

# Variables: snake_case
player_health = 100
enemy_count = 5
```

### 4.4 Documentation Standards

**Docstring Style:** Google-style docstrings

```python
def check_dialogue_requirements(
    self,
    option: DialogueOption,
    player_stats: Dict[str, int],
    player_inventory: Optional[Dict[str, int]] = None,
    faction_reps: Optional[Dict[str, int]] = None
) -> bool:
    """
    Check if a dialogue option is available to the player.

    Validates all requirements (skills, attributes, items, faction rep)
    before allowing the player to select this dialogue option.

    Args:
        option: Dialogue option to check
        player_stats: Player attributes and skills dict
        player_inventory: Player inventory with item counts
        faction_reps: Faction reputation scores

    Returns:
        True if all requirements are met, False otherwise

    Example:
        >>> option = DialogueOption(requirement_type="skill",
        ...                          required_skill="persuasion",
        ...                          required_value=5)
        >>> check_dialogue_requirements(option, {"persuasion": 7})
        True
    """
    if not option.requirement_type:
        return True

    # Implementation...
```

### 4.5 Type Hints

**DO:** Add type hints to all function signatures

```python
from typing import Dict, List, Optional, Tuple, Any

def add_item(self, item: Item, quantity: int = 1) -> bool:
    """Add item to inventory."""
    pass

def get_active_quests(self) -> List[Quest]:
    """Get all active quests."""
    pass

def find_path(
    self,
    start: Tuple[int, int],
    end: Tuple[int, int]
) -> Optional[List[Tuple[int, int]]]:
    """Find path from start to end."""
    pass
```

### 4.6 Error Handling

**DO:** Handle errors gracefully

```python
# Validate inputs early
def process_entity(self, entity_id: str) -> Optional[Entity]:
    if not entity_id:
        raise ValueError("entity_id cannot be empty")

    entity = self.world.get_entity(entity_id)
    if not entity:
        return None

    return entity

# Catch specific exceptions
try:
    save_data = quest_manager.to_dict()
except (AttributeError, TypeError) as e:
    print(f"Warning: Failed to save quest_manager: {e}")
    save_data = {}

# Use context managers
with open("save_file.json", "r") as f:
    data = json.load(f)
```

### 4.7 Function Complexity

**Target:** Cyclomatic complexity < 10

**DO:** Break complex functions into helpers

```python
# ✅ GOOD - Simple, focused functions
def enemy_ai_turn(self, enemy: Entity):
    """Execute enemy AI turn."""
    if not self._has_valid_targets():
        return

    if not self._ai_try_attack(enemy):
        self._ai_try_move(enemy)

    if enemy.ap == 0:
        self.next_turn()

def _ai_try_attack(self, enemy: Entity) -> bool:
    """Try to attack if targets in range."""
    targets = self.get_valid_targets(enemy)
    if not targets or enemy.ap < AP_BASIC_ATTACK:
        return False

    target = self._find_closest_target(enemy, targets)
    self._execute_attack(enemy, target)
    return True
```

**DON'T:** Write monolithic functions

```python
# ❌ BAD - Too complex, hard to test
def enemy_ai_turn(self, enemy):
    """Execute enemy AI turn with complex nested logic."""
    targets = [c for c in self.player_team if c.is_alive]
    if targets and enemy.ap >= AP_BASIC_ATTACK:
        distances = []
        for target in targets:
            dx = abs(enemy.x - target.x)
            dy = abs(enemy.y - target.y)
            distances.append((dx + dy, target))
        distances.sort()
        target = distances[0][1]
        if self.is_in_range(enemy, target):
            damage = enemy.attack(target)
            # ... 50 more lines ...
```

---

## 5. Testing Strategy

### 5.1 Test Organization

```
tests/
├── conftest.py              # Shared fixtures
├── test_ecs.py              # ECS tests
├── test_collision.py        # Collision tests
├── test_combat.py           # Combat tests
├── test_scene.py            # Scene tests
├── test_pathfinding.py      # Pathfinding tests
├── test_ui_system.py        # UI tests
└── ...                      # 17 total test files
```

### 5.2 Testing Conventions

**File naming:** `test_<module_name>.py`
**Class naming:** `TestClassName`
**Function naming:** `test_descriptive_name_of_what_is_tested`

```python
import pytest
from neonworks.core.ecs import World, Entity, Transform

class TestECS:
    """Test suite for Entity Component System."""

    def test_create_entity_with_name(self):
        """Test creating an entity with a name."""
        world = World()
        entity = world.create_entity("Player")

        assert entity is not None
        assert entity.name == "Player"

    def test_add_component_to_entity(self):
        """Test adding a component to an entity."""
        world = World()
        entity = world.create_entity("Test")
        transform = Transform(x=10, y=20)

        entity.add_component(transform)

        assert entity.has_component(Transform)
        assert entity.get_component(Transform).x == 10

    @pytest.mark.parametrize("x,y,expected", [
        (0, 0, True),
        (-10, -10, True),
        (1000, 1000, True),
    ])
    def test_transform_at_various_positions(self, x, y, expected):
        """Test transform component at boundary positions."""
        transform = Transform(x=x, y=y)
        assert (transform.x == x and transform.y == y) == expected
```

### 5.3 Test Coverage Goals

**Target:** 85-90% overall coverage

**Check coverage:**
```bash
# Generate HTML report
make test-cov

# View report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux

# Terminal report
pytest tests/ --cov=. --cov-report=term-missing
```

### 5.4 Fixtures

**Common fixtures** (`tests/conftest.py`):

```python
import pytest
from neonworks.core.ecs import World

@pytest.fixture
def world():
    """Create a fresh World instance for testing."""
    return World()

@pytest.fixture
def player_entity(world):
    """Create a basic player entity."""
    entity = world.create_entity("Player")
    entity.add_component(Transform(x=0, y=0))
    entity.add_component(Health(hp=100, max_hp=100))
    entity.add_tag("player")
    return entity
```

**Usage:**
```python
def test_player_takes_damage(player_entity):
    """Test player health decreases when damaged."""
    health = player_entity.get_component(Health)
    initial_hp = health.hp

    health.hp -= 25

    assert health.hp == initial_hp - 25
    assert health.hp < health.max_hp
```

---

## 6. Common Tasks & Patterns

### 6.1 Creating a New System

```python
# File: systems/my_new_system.py
from neonworks.core.ecs import System, World
from neonworks.core.events import get_event_manager

class MyNewSystem(System):
    """
    System that does something specific.

    This system processes entities with ComponentX and ComponentY,
    updating their state based on game rules.
    """

    def __init__(self):
        """Initialize the system."""
        super().__init__()
        self.event_manager = get_event_manager()

    def update(self, dt: float, world: World):
        """
        Update system logic.

        Args:
            dt: Delta time in seconds since last update
            world: World instance containing all entities
        """
        # Get relevant entities
        entities = world.get_entities_with_component(ComponentX)

        for entity in entities:
            component = entity.get_component(ComponentX)
            # Update logic here
            component.value += dt

            # Emit events if needed
            if component.value > threshold:
                self.event_manager.emit("threshold_reached", {
                    "entity_id": entity.id
                })
```

**Register system:**
```python
# In game initialization
from neonworks.systems.my_new_system import MyNewSystem

world = World()
my_system = MyNewSystem()
world.add_system(my_system)
```

### 6.2 Creating a New Component

```python
# File: core/ecs.py (or custom component file)
from dataclasses import dataclass
from neonworks.core.ecs import Component

@dataclass
class MyComponent(Component):
    """
    Component that stores custom data.

    Attributes:
        value: Primary value
        enabled: Whether component is active
        metadata: Additional data
    """
    value: float = 0.0
    enabled: bool = True
    metadata: dict = None

    def __post_init__(self):
        """Initialize metadata if not provided."""
        if self.metadata is None:
            self.metadata = {}
```

**Usage:**
```python
entity = world.create_entity("CustomEntity")
entity.add_component(MyComponent(value=100.0, enabled=True))
```

### 6.3 Creating a UI Editor

**Pattern:** Inherit from base UI class and integrate with `MasterUIManager`

```python
# File: ui/my_editor_ui.py
import pygame
from neonworks.ui.ui_system import Panel, Button, Label

class MyEditorUI:
    """
    Visual editor for [purpose].

    Hotkey: F11 (add to MasterUIManager)
    """

    def __init__(self, world, renderer):
        """Initialize editor UI."""
        self.world = world
        self.renderer = renderer
        self.visible = False

        # Create UI elements
        self.panel = Panel(x=100, y=100, width=600, height=400)
        self.title = Label(text="My Editor", x=120, y=120)
        self.close_btn = Button(
            text="Close",
            x=650,
            y=120,
            on_click=self.close
        )

    def update(self, dt: float):
        """Update editor logic."""
        if not self.visible:
            return

        # Update UI elements
        self.panel.update(dt)
        self.close_btn.update(dt)

    def render(self, screen: pygame.Surface):
        """Render editor UI."""
        if not self.visible:
            return

        self.panel.render(screen)
        self.title.render(screen)
        self.close_btn.render(screen)

    def handle_event(self, event: pygame.event.Event):
        """Handle input events."""
        if not self.visible:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close()

        self.close_btn.handle_event(event)

    def toggle(self):
        """Toggle visibility."""
        self.visible = not self.visible

    def close(self):
        """Close editor."""
        self.visible = False
```

**Add to MasterUIManager:**
```python
# File: ui/master_ui_manager.py
from neonworks.ui.my_editor_ui import MyEditorUI

class MasterUIManager:
    def __init__(self, world, renderer):
        # ... existing code ...
        self.my_editor = MyEditorUI(world, renderer)

    def handle_event(self, event):
        # ... existing code ...
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                self.my_editor.toggle()

        self.my_editor.handle_event(event)
```

### 6.4 Loading/Saving Data

**Save game:**
```python
from neonworks.core.project import get_project_manager

manager = get_project_manager()

# Collect game state
save_data = {
    "player": {
        "position": [player.x, player.y],
        "stats": player.stats.to_dict(),
        "inventory": player.inventory.to_dict()
    },
    "world_state": {
        "flags": game_flags,
        "quests": quest_manager.to_dict()
    },
    "entities": [e.serialize() for e in world.entities]
}

# Save to file
manager.save_game("save_slot_1", save_data)
```

**Load game:**
```python
# Load from file
save_data = manager.load_game("save_slot_1")

# Restore state
player.x, player.y = save_data["player"]["position"]
player.stats.from_dict(save_data["player"]["stats"])
quest_manager.from_dict(save_data["world_state"]["quests"])

# Restore entities
for entity_data in save_data["entities"]:
    entity = Entity.deserialize(entity_data)
    world.add_entity(entity)
```

### 6.5 Configuration Files

**Project structure** (`project.json`):
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
  }
}
```

**Loading config:**
```python
from neonworks.data.config_loader import load_config

config = load_config("config/items.json")
items = config.get("items", [])

for item_data in items:
    item = Item.from_dict(item_data)
    item_database.add(item)
```

---

## 7. Critical Information

### 7.1 Namespace Migration (IMPORTANT!)

**The package was migrated from `engine.*` to `neonworks.*` on 2025-11-13.**

All imports MUST use the `neonworks.*` namespace:

```python
# ✅ CORRECT
from neonworks.core.ecs import World
from neonworks.rendering.renderer import Renderer
from neonworks.systems.jrpg_battle_system import JRPGBattleSystem

# ❌ WRONG - Will cause ImportError
from engine.core.ecs import World
from engine.rendering.renderer import Renderer
```

**If you see `engine.*` imports in any file:**
1. It's a bug that needs fixing
2. Replace with `neonworks.*`
3. Test that imports work

### 7.2 Package Entry Point

**setup.py configuration:**
```python
entry_points={
    "console_scripts": [
        "neonworks=neonworks.cli:main",  # CORRECT
        # NOT: "neonworks=engine.cli:main"  # WRONG
    ],
}
```

### 7.3 Known Issues & TODOs

**11 TODO items exist in the codebase:**

| File | Line | Issue |
|------|------|-------|
| `main.py` | 118 | Building definitions not loaded from file |
| `cli.py` | 286 | Game initialization placeholder |
| `editor/ai_navmesh.py` | 124 | Multi-tile building support incomplete |
| `systems/zone_system.py` | 159 | Transition effect timing not implemented |
| `ui/exploration_ui.py` | 78, 357 | Portrait loading and party status missing |
| `ui/level_builder_ui.py` | 435, 440 | Save/load not implemented |
| `ui/magic_menu_ui.py` | 270 | Spell cast trigger not implemented |
| `ui/jrpg_battle_ui.py` | 357 | Target selection navigation incomplete |

**When working near these areas:**
- Check for TODO comments
- Consider implementing the missing feature
- Update tests if you fix a TODO

### 7.4 MasterUIManager Hotkeys

**All visual editors are accessed via function keys (F1-F12) or modifier combos:**

| Key | Editor | Mode | File |
|-----|--------|------|------|
| F1 | Debug Console | All | `ui/debug_console_ui.py` |
| F2 | Settings | All | `ui/settings_ui.py` |
| F3 | Building UI | Game | `ui/building_ui.py` |
| F4 | Level Builder | Editor | `ui/level_builder_ui.py` |
| F5 | Navmesh Editor | Editor | `ui/navmesh_editor_ui.py` |
| F6 | Quest Editor | Editor | `ui/quest_editor_ui.py` |
| F7 | Asset Browser | Editor | `ui/asset_browser_ui.py` |
| F8 | Project Manager | All | `ui/project_manager_ui.py` |
| F9 | Combat UI | Game | `ui/combat_ui.py` |
| F10 | Toggle HUD | Game | `ui/game_hud.py` |
| F11 | Autotile Editor | Editor | `ui/autotile_editor_ui.py` |
| F12 | Navmesh Editor | Editor | `ui/navmesh_editor_ui.py` |
| Ctrl+M | Map Manager | Editor | `ui/map_manager_ui.py` |
| Ctrl+L | Layer Panel | Editor | `ui/layer_panel_ui.py` |
| Ctrl+H | History Viewer | Editor | `ui/history_viewer_ui.py` |
| Ctrl+T | Tileset Picker | Editor | `ui/tileset_picker_ui.py` |
| Ctrl+E | Event Editor | Editor | `ui/event_editor_ui.py` |
| Ctrl+D | Database Manager | Editor | `ui/database_manager_ui.py` |
| Ctrl+G | Character Generator | Editor | `ui/character_generator_ui.py` |
| Shift+F7 | AI Animator | Editor | `ui/ai_animator_ui.py` |
| Ctrl+Space | AI Assistant | All | `ui/ai_assistant_panel.py` |
| Ctrl+Shift+K | Shortcuts Overlay | All | `ui/shortcuts_overlay_ui.py` |

**Map Tools (activated when in Map Editor):**
- **P** - Pencil Tool (`ui/map_tools/pencil_tool.py`)
- **E** - Eraser Tool (`ui/map_tools/eraser_tool.py`)
- **F** - Fill Tool (`ui/map_tools/fill_tool.py`)
- **S** - Select Tool (`ui/map_tools/select_tool.py`)
- **B** - Stamp Tool (`ui/map_tools/stamp_tool.py`)
- **R** - Shape Tool (`ui/map_tools/shape_tool.py`)
- **I** - Eyedropper Tool (`ui/map_tools/eyedropper_tool.py`)

**When adding new editors:**
- Add to `MasterUIManager.__init__()`
- Add hotkey handling in `MasterUIManager.handle_event()`
- Document in this file and README
- Update keyboard_shortcuts.md in docs/

### 7.5 Dependencies

**Runtime dependencies** (`requirements.txt`):
```
pygame==2.5.2
numpy>=1.24.0
Pillow>=10.0.0
PyYAML>=6.0.3
cryptography>=46.0.0
pyinstaller>=6.0.0
```

**Development dependencies** (`requirements-dev.txt`):
```
pytest==7.4.3
pytest-cov==4.1.0
pytest-mock==3.12.0
pytest-xdist==3.5.0        # Parallel test execution
pytest-timeout==2.2.0
black==25.11.0
isort==7.0.0
flake8==7.3.0
mypy==1.7.1
pylint==4.0.3
coverage==7.3.4
pre-commit==3.5.0
sphinx==7.1.2              # Documentation generation
faker==21.0.0              # Test data generation
```

**Installing dependencies:**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 7.6 Pre-commit Hooks

**Configured hooks** (`.pre-commit-config.yaml`):
1. **black** - Code formatting
2. **isort** - Import sorting
3. **flake8** - Linting
4. **trailing-whitespace** - Remove trailing spaces
5. **end-of-file-fixer** - Ensure newline at EOF
6. **check-yaml** - Validate YAML files
7. **check-json** - Validate JSON files
8. **pytest** - Run tests on commit
9. **pytest-cov** - Check coverage on push

**Installing hooks:**
```bash
pre-commit install
pre-commit install --hook-type commit-msg
```

**Running manually:**
```bash
pre-commit run --all-files
```

---

## 8. Troubleshooting

### 8.1 Import Errors

**Problem:** `ModuleNotFoundError: No module named 'engine'`

**Solution:**
```bash
# The namespace is 'neonworks', not 'engine'
# Update imports:
sed -i 's/from engine\./from neonworks./g' file.py
```

**Problem:** `ImportError: cannot import name 'GameLoop'`

**Solution:**
```python
# GameLoop doesn't exist, use GameEngine instead
from neonworks.core.game_loop import GameEngine, EngineConfig
```

### 8.2 Test Failures

**Problem:** Tests fail with import errors

**Solution:**
```bash
# Ensure you're in project root
cd /path/to/neonworks

# Explicitly set PYTHONPATH
PYTHONPATH=. pytest tests/ -v

# Or install in editable mode
pip install -e .
```

**Problem:** Tests fail due to missing Pygame

**Solution:**
```bash
# Install Pygame
pip install pygame==2.5.2

# If that fails, try system packages (Linux)
sudo apt-get install python3-pygame
```

### 8.3 Formatting Issues

**Problem:** Pre-commit hook fails on formatting

**Solution:**
```bash
# Auto-fix formatting
make format

# Or manually
black .
isort .

# Verify
make format-check
```

### 8.4 Coverage Issues

**Problem:** Coverage too low

**Solution:**
```bash
# Generate detailed report
pytest tests/ --cov=. --cov-report=html --cov-report=term-missing

# Open HTML report to see missing lines
open htmlcov/index.html

# Focus on uncovered lines shown in red
```

### 8.5 Git Push Failures

**Problem:** `git push` fails with 403 error

**Solution:**
```bash
# Branch must start with 'claude/' and match session ID
# Correct format:
git checkout -b claude/feature-name-<session-id>
git push -u origin claude/feature-name-<session-id>

# Check current branch
git branch --show-current
```

### 8.6 Type Checking Errors

**Problem:** MyPy reports type errors

**Solution:**
```bash
# Run mypy with config
mypy . --config-file=mypy.ini

# Check specific file
mypy systems/my_system.py --config-file=mypy.ini

# Note: Type checking is not strictly enforced
# Focus on fixing obvious issues, ignore overly strict warnings
```

---

## Quick Reference Card

### Essential Commands
```bash
make test          # Run all tests
make format        # Format code
make lint          # Lint code
make test-cov      # Coverage report
python main.py     # Launch game
```

### Essential Imports
```python
# Core
from neonworks.core.ecs import Entity, Component, System, World
from neonworks.core.events import get_event_manager
from neonworks.core.project import get_project_manager

# Rendering
from neonworks.rendering.renderer import Renderer
from neonworks.rendering.camera import Camera
from neonworks.rendering.assets import get_asset_manager

# Systems
from neonworks.systems.jrpg_battle_system import JRPGBattleSystem
from neonworks.systems.pathfinding import Pathfinding

# UI
from neonworks.ui.master_ui_manager import MasterUIManager
from neonworks.ui.ui_system import Panel, Button, Label
```

### Key Files to Remember
```
core/ecs.py                    # ECS implementation
core/game_loop.py              # Main game loop
ui/master_ui_manager.py        # UI coordinator (F1-F10)
systems/jrpg_battle_system.py  # JRPG combat
README.md                      # Project overview
STATUS.md                      # Current status & issues
DEVELOPER_GUIDE.md             # Developer best practices
```

### Coverage Targets
- Overall: 85-90%
- Core modules: 90%+
- UI modules: 70%+
- Systems: 85%+

### Code Quality Targets
- Cyclomatic complexity: < 10
- Function length: < 50 lines
- Line length: 88 chars (black)
- Type hints: Required for public APIs

---

## When Making Changes

### Adding a New Feature
1. ✅ Read relevant documentation (STATUS.md, DEVELOPER_GUIDE.md)
2. ✅ Create feature branch: `claude/feature-name-<session-id>`
3. ✅ Write tests FIRST (TDD approach recommended)
4. ✅ Implement feature following code standards
5. ✅ Add docstrings and type hints
6. ✅ Run tests: `make test`
7. ✅ Format code: `make format`
8. ✅ Lint code: `make lint`
9. ✅ Commit with conventional message
10. ✅ Push and create PR

### Fixing a Bug
1. ✅ Write a failing test that reproduces the bug
2. ✅ Fix the bug
3. ✅ Verify test passes
4. ✅ Check for similar bugs in related code
5. ✅ Update documentation if needed
6. ✅ Commit with `fix:` prefix

### Refactoring
1. ✅ Ensure tests exist and pass
2. ✅ Make small, incremental changes
3. ✅ Run tests after each change
4. ✅ Keep test coverage at same level or higher
5. ✅ Update docstrings if behavior changes
6. ✅ Commit with `refactor:` prefix

### Updating Documentation
1. ✅ Update this file (CLAUDE.md) for AI-relevant changes
2. ✅ Update README.md for user-facing changes
3. ✅ Update docs/project/STATUS.md if fixing TODOs or known issues
4. ✅ Update docs/project/DEVELOPER_GUIDE.md for workflow changes
5. ✅ Commit with `docs:` prefix

---

## Additional Resources

### Core Documentation
- **README.md** - Project overview and quick start
- **CLAUDE.md** - AI assistant guide (this file)
- **JRPG_FEATURES.md** - JRPG system documentation

### Project Documentation (docs/project/)
- **STATUS.md** - Current implementation status (50,000+ LOC analysis)
- **DEVELOPER_GUIDE.md** - Development best practices and standards
- **NEONWORKS_ENGINE_OVERVIEW.md** - Comprehensive architecture overview
- **LAUNCHER_README.md** - Visual launcher documentation
- **FEATURE_CHECKLIST.md** - Complete feature implementation status
- **IMPLEMENTATION_SUMMARY.md** - Implementation summaries
- **CHANGELOG.md** - Version history and changes
- **KNOWN_ISSUES.md** - Known bugs and limitations
- **DEPENDENCIES.md** - Dependency documentation
- **FORMATTING.md** - Code formatting guide
- **IMPORT_FIXES.md** - Import migration documentation
- **ASSET_LIBRARY_UPDATE.md** - Asset library documentation

### Testing & Quality (docs/project/)
- **TEST_RESULTS.md** - Test execution results
- **E2E_TEST_RESULTS.md** - End-to-end test results
- **COVERAGE_SUMMARY.md** - Test coverage reports
- **TEST_SUITE_ADDITIONS.md** - Test suite documentation

### Guides & Tutorials
- **docs/** - Full documentation directory (40+ files)
- **docs/getting_started.md** - Getting started guide
- **docs/keyboard_shortcuts.md** - Complete keyboard shortcuts
- **docs/map_editor_guide.md** - Map editor tutorial
- **docs/RECIPES.md** - Common patterns and solutions
- **docs/tutorials/** - Step-by-step tutorials
- **ui/map_tools/README.md** - Map tools documentation
- **ui/WORKSPACE_SYSTEM.md** - Workspace system guide

### Examples & Templates
- **examples/** - Example projects and demos (3 projects)
- **templates/** - Project templates (4 templates)

---

**Last Updated:** 2025-11-16
**Maintainer:** NeonWorks Team
**Status:** Production Ready
**Version:** 1.1
**Questions?** Check docs/project/STATUS.md or docs/project/DEVELOPER_GUIDE.md

---

## Repository Organization

As of Version 1.1, the repository has been reorganized for better clarity:

- **Root** - Only essential files (README.md, CLAUDE.md, JRPG_FEATURES.md, setup files)
- **docs/project/** - All project documentation (moved from root)
- **engine/** - Specialized engine subsystems (event interpreter, database, character gen)
- **scripts/** - Utility scripts and benchmarks
- **examples/** - Demo files and example projects
- **tests/** - All test files

This organization reduces root directory clutter and groups related files logically.

