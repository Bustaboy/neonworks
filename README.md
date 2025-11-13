# Neon Works

A comprehensive, **project-based** 2D game engine for turn-based strategy games with base building and survival elements.

Originally developed for Neon Collapse, Neon Works is now a standalone, reusable engine for creating your own games.

## 🎮 Project-Based Architecture

The engine is **completely separate** from game content, making it reusable for multiple games:

- **Engine** (this repository) - Generic, reusable game engine with no game-specific code
- **Projects** (your game folders) - Individual game projects with their own assets, levels, and configuration
- **Project Files** (`project.json`) - Configuration files that link game content to the engine

This architecture allows you to:
- ✅ Create multiple games using the same engine
- ✅ Version control engine and game content separately
- ✅ Share projects without sharing the engine
- ✅ Iterate on game design without touching engine code

## Features

### Core Engine
- **Entity Component System (ECS)** - Flexible entity management
- **Game Loop** - Fixed timestep update with variable rendering
- **State Management** - Scene system with transitions
- **Event System** - Decoupled communication between systems
- **Project System** - Load and manage game projects with configuration files

### Editor Tools
- **Level Designer** - Visual tile placement, prop editing, terrain painting
- **Navmesh Editor** - Automatic and manual navmesh generation with visualization
- **Character Importer** - Import and configure character assets
- **Asset Browser** - Manage all game assets in one place

### Game Systems
- **Turn-Based Strategy** - Grid-based tactical combat
- **Base Building** - Construct and upgrade buildings
- **Survival Mechanics** - Hunger, thirst, energy, health management
- **Resource Management** - Gather, store, and consume resources
- **AI System** - Pathfinding with A* on navmesh
- **Combat System** - Flexible combat mechanics for turn-based games

### Rendering
- **2D Grid Renderer** - Tile-based rendering with layers
- **UI System** - ImGui-style immediate mode UI
- **Camera System** - Pan, zoom, focus on entities
- **Particle System** - Effects for combat and events

## Architecture

```
neonworks/
├── core/               # Core engine systems
│   ├── ecs.py         # Entity Component System
│   ├── game_loop.py   # Main game loop
│   ├── events.py      # Event system
│   └── state.py       # State management
├── editor/            # Editor tools
│   ├── ai_level_builder.py  # AI level generation
│   ├── ai_navmesh.py        # AI navmesh generation
│   ├── ai_writer.py         # AI quest/dialogue writing
│   └── procedural_gen.py    # Procedural generation
├── rendering/         # Rendering systems
│   ├── renderer.py    # Main 2D renderer
│   ├── camera.py      # Camera system
│   ├── ui.py          # UI rendering
│   └── particles.py   # Particle effects
├── systems/           # Game systems
│   ├── turn_system.py       # Turn-based mechanics
│   ├── base_building.py     # Base construction
│   ├── survival.py          # Survival mechanics
│   └── pathfinding.py       # A* pathfinding
├── data/              # Data management
│   ├── serialization.py     # Entity serialization
│   └── config_loader.py     # Config file loading
└── ui/                # Advanced UI systems
    ├── ui_system.py         # Widget framework
    ├── master_ui_manager.py # UI coordination
    └── [various UI modules] # Specialized UI components
```

## Quick Start

### Running Tests
```bash
# Run engine tests
pytest tests/
```

### Using the Editor Tools

The engine includes editor tools for level design, navmesh editing, and asset management. These tools are available once you create a complete game project (see below).

### Creating a New Game Project
```python
from engine.core.project import ProjectManager, ProjectMetadata, ProjectSettings

# Create project manager
pm = ProjectManager()

# Define project metadata
metadata = ProjectMetadata(
    name="My Awesome Game",
    version="1.0.0",
    description="A cool strategy game",
    author="Your Name"
)

# Define project settings
settings = ProjectSettings(
    window_title="My Awesome Game",
    window_width=1280,
    window_height=720,
    tile_size=32,
    enable_base_building=True,
    enable_turn_based=True
)

# Create the project
project = pm.create_project("my_game", metadata, settings)
```

### Running Tests
```bash
pytest tests/
```

## Example Projects

The engine includes example projects in the `examples/` directory demonstrating various features and usage patterns. Check out `examples/simple_rpg/` for a basic RPG example and `examples/visual_ui_demo.py` for a UI demonstration.

## Project Configuration

Each project has a `project.json` file that defines:

```json
{
  "metadata": {
    "name": "Game Name",
    "version": "1.0.0",
    "description": "Game description",
    "author": "Your Name"
  },
  "settings": {
    "window_title": "Game Title",
    "window_width": 1280,
    "window_height": 720,
    "tile_size": 32,
    "enable_base_building": true,
    "enable_survival": true,
    "enable_turn_based": true,
    "building_definitions": "config/buildings.json",
    "item_definitions": "config/items.json"
  },
  "custom_data": {
    "theme": "cyberpunk",
    "difficulty_levels": ["easy", "normal", "hard"]
  }
}
```

## Using the Engine for Your Own Game

1. **Create a new project folder** with your game name
2. **Add a `project.json`** file with your game settings
3. **Add your assets** in the `assets/` folder
4. **Define game data** in `config/` (buildings, items, characters, etc.)
5. **Create levels** using the level editor
6. **Run your game** with `python main.py your_project_name`

The engine handles all the heavy lifting - you just provide the content!

## Documentation

For detailed information about the engine:
- Check the [docs/](docs/) directory for comprehensive guides
- See [docs/getting_started.md](docs/getting_started.md) for a tutorial
- Browse [docs/api_reference.md](docs/api_reference.md) for API documentation
- Read [docs/creating_components.md](docs/creating_components.md) and [docs/creating_systems.md](docs/creating_systems.md) for custom development
- Check [docs/RECIPES.md](docs/RECIPES.md) for common patterns and solutions

For API reference and code examples, see the inline docstrings in the source code.
