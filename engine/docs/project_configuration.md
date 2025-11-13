# Project Configuration Guide

Learn how to configure your NeonWorks game project using `project.json`.

## Overview

Every NeonWorks game is a **project** with its own `project.json` configuration file. This file defines:
- Project metadata (name, version, author)
- Asset paths (where to find sprites, sounds, etc.)
- Game settings (window size, features enabled, etc.)
- Custom data (game-specific configuration)

## Project Structure

A typical NeonWorks project looks like this:

```
my_game/
├── project.json          # Project configuration
├── main.py              # Game entry point
├── assets/              # Game assets
│   ├── sprites/
│   ├── sounds/
│   └── music/
├── levels/              # Level definitions
├── scripts/             # Custom game code
│   └── game.py
├── config/              # Data definitions
│   ├── buildings.json
│   └── items.json
└── saves/               # Save game files
```

## project.json Structure

The `project.json` file has four main sections:

### 1. Metadata

Basic information about your project.

```json
{
  "metadata": {
    "name": "My Awesome Game",
    "version": "1.0.0",
    "description": "A thrilling adventure game built with NeonWorks",
    "author": "Your Name",
    "engine_version": "0.1.0",
    "created_date": "2025-11-13",
    "modified_date": "2025-11-13"
  }
}
```

**Fields**:
- `name` (string, required): Display name of your game
- `version` (string): Semantic version (e.g., "1.0.0")
- `description` (string): Brief description of your game
- `author` (string): Creator name or team
- `engine_version` (string): NeonWorks version requirement
- `created_date` (string): ISO date when project was created
- `modified_date` (string): ISO date of last modification

### 2. Paths

Define where the engine should look for different asset types.

```json
{
  "paths": {
    "assets": "assets",
    "levels": "levels",
    "scripts": "scripts",
    "saves": "saves",
    "config": "config"
  }
}
```

**Fields**:
- `assets` (string): Directory for sprites, sounds, music, etc.
- `levels` (string): Directory for level definition files
- `scripts` (string): Directory for custom Python scripts
- `saves` (string): Directory where save games are stored
- `config` (string): Directory for game data (items, buildings, etc.)

All paths are relative to the project root directory.

### 3. Settings

Core game configuration and feature toggles.

```json
{
  "settings": {
    "window": {
      "width": 1280,
      "height": 720,
      "title": "My Awesome Game",
      "fullscreen": false
    },
    "tile_size": 32,
    "grid_width": 100,
    "grid_height": 100,
    "target_fps": 60,
    "initial_scene": "menu",
    "initial_level": "level_1",
    "features_enabled": {
      "rendering": true,
      "physics": true,
      "audio": true,
      "turn_based": false,
      "survival": false,
      "base_building": false,
      "pathfinding": false
    },
    "definitions": {
      "buildings": "config/buildings.json",
      "items": "config/items.json",
      "characters": "config/characters.json",
      "quests": "config/quests.json"
    }
  }
}
```

#### Window Settings

- `width` (int): Window width in pixels (default: 800)
- `height` (int): Window height in pixels (default: 600)
- `title` (string): Window title bar text
- `fullscreen` (bool): Start in fullscreen mode (default: false)

#### Rendering Settings

- `tile_size` (int): Size of grid tiles in pixels (default: 32)
- `grid_width` (int): Number of tiles horizontally (for tilemaps)
- `grid_height` (int): Number of tiles vertically (for tilemaps)
- `target_fps` (int): Target frames per second (default: 60)

#### Game Flow

- `initial_scene` (string): First scene to load (e.g., "menu", "gameplay")
- `initial_level` (string): First level to load in gameplay

#### Features Enabled

Toggle major engine subsystems on/off to optimize performance:

- `rendering` (bool): Enable the rendering system
- `physics` (bool): Enable collision detection and physics
- `audio` (bool): Enable audio manager
- `turn_based` (bool): Enable turn-based combat system
- `survival` (bool): Enable survival mechanics (hunger, thirst, energy)
- `base_building` (bool): Enable base building system
- `pathfinding` (bool): Enable A* pathfinding

**Tip**: Disable features you don't use to improve performance and reduce memory usage.

#### Definitions

Paths to JSON files defining game data:

- `buildings`: Building types and templates
- `items`: Item definitions and properties
- `characters`: Character stats and abilities
- `quests`: Quest definitions and objectives

### 4. Custom Data

Store game-specific configuration that doesn't fit elsewhere.

```json
{
  "custom_data": {
    "game_mode": "campaign",
    "difficulty_levels": ["easy", "normal", "hard", "extreme"],
    "default_difficulty": "normal",
    "theme": "cyberpunk",
    "color_scheme": {
      "primary": "#00FFFF",
      "secondary": "#FF00FF",
      "accent": "#00FF00",
      "background": "#0A0A1A",
      "ui_background": "#1A1A2E"
    },
    "player_stats": {
      "starting_health": 100,
      "starting_energy": 50,
      "starting_resources": {
        "metal": 100,
        "energy": 50
      }
    },
    "world_generation": {
      "seed": 12345,
      "biomes": ["desert", "forest", "urban"],
      "enemy_spawn_rate": 0.1
    }
  }
}
```

**Custom data can contain anything you want!** This section is freeform JSON that you can access in your game code.

## Complete Example

Here's a complete `project.json` for a cyberpunk turn-based strategy game:

```json
{
  "metadata": {
    "name": "Neon Collapse",
    "version": "1.0.0",
    "description": "A cyberpunk turn-based strategy game with base building and survival mechanics",
    "author": "Neon Collapse Team",
    "engine_version": "0.1.0",
    "created_date": "2025-11-12",
    "modified_date": "2025-11-13"
  },
  "paths": {
    "assets": "assets",
    "levels": "levels",
    "scripts": "scripts",
    "saves": "saves",
    "config": "config"
  },
  "settings": {
    "window": {
      "width": 1280,
      "height": 720,
      "title": "Neon Collapse",
      "fullscreen": false
    },
    "tile_size": 32,
    "grid_width": 100,
    "grid_height": 100,
    "target_fps": 60,
    "initial_scene": "menu",
    "initial_level": "tutorial",
    "features_enabled": {
      "rendering": true,
      "physics": true,
      "audio": true,
      "turn_based": true,
      "survival": true,
      "base_building": true,
      "pathfinding": true
    },
    "definitions": {
      "buildings": "config/buildings.json",
      "items": "config/items.json",
      "characters": "config/characters.json",
      "quests": "config/quests.json"
    }
  },
  "custom_data": {
    "game_mode": "campaign",
    "difficulty_levels": ["easy", "normal", "hard", "extreme"],
    "default_difficulty": "normal",
    "theme": "cyberpunk",
    "color_scheme": {
      "primary": "#00FFFF",
      "secondary": "#FF00FF",
      "accent": "#00FF00",
      "background": "#0A0A1A",
      "ui_background": "#1A1A2E"
    }
  }
}
```

## Loading Project Configuration in Code

### Using ProjectManager

The easiest way to load your project:

```python
from engine.core.project import ProjectManager

# Load project by name (looks in projects/ directory)
project = ProjectManager.load_project("my_game")

# Access configuration
print(f"Game: {project.config.metadata.name}")
print(f"Version: {project.config.metadata.version}")
print(f"Window Size: {project.config.settings.window.width}x{project.config.settings.window.height}")

# Access custom data
theme = project.config.custom_data.get("theme", "default")
difficulty = project.config.custom_data.get("default_difficulty", "normal")
```

### Accessing Settings

```python
# Window settings
window_settings = project.config.settings.window
screen = pygame.display.set_mode((window_settings.width, window_settings.height))
pygame.display.set_caption(window_settings.title)

# Check if feature is enabled
if project.config.settings.features_enabled.get("turn_based", False):
    world.add_system(TurnSystem())

if project.config.settings.features_enabled.get("survival", False):
    world.add_system(SurvivalSystem())
```

### Loading Data Definitions

```python
import json
import os

# Get path to buildings definition file
buildings_path = os.path.join(
    project.root_path,
    project.config.settings.definitions.get("buildings", "")
)

# Load buildings data
with open(buildings_path, 'r') as f:
    buildings_data = json.load(f)
```

## Minimal Configuration

The absolute minimum `project.json` needed:

```json
{
  "metadata": {
    "name": "My Game",
    "version": "0.1.0"
  },
  "paths": {
    "assets": "assets",
    "levels": "levels",
    "scripts": "scripts",
    "saves": "saves",
    "config": "config"
  },
  "settings": {
    "window": {
      "width": 800,
      "height": 600,
      "title": "My Game"
    },
    "features_enabled": {
      "rendering": true
    }
  }
}
```

All other settings will use default values.

## Advanced: Dynamic Configuration

You can modify configuration at runtime:

```python
# Load project
project = ProjectManager.load_project("my_game")

# Override window size for fullscreen
project.config.settings.window.width = 1920
project.config.settings.window.height = 1080
project.config.settings.window.fullscreen = True

# Enable additional features
project.config.settings.features_enabled["physics"] = True

# Add custom runtime data
project.config.custom_data["session_id"] = "xyz123"
```

## Best Practices

### 1. Use Semantic Versioning
Version your game as `MAJOR.MINOR.PATCH`:
- `MAJOR`: Incompatible changes
- `MINOR`: New features, backwards compatible
- `PATCH`: Bug fixes

### 2. Document Custom Data
Add comments in your README explaining custom_data fields:

```markdown
## Custom Configuration

- `theme`: Visual theme ("cyberpunk", "fantasy", "scifi")
- `difficulty_levels`: Available difficulty settings
- `color_scheme`: UI color palette in hex format
```

### 3. Separate Concerns
Use `definitions` files for data that changes frequently:
- `config/buildings.json` - Building types
- `config/items.json` - Item database
- `config/enemies.json` - Enemy stats

This keeps `project.json` focused on structure and settings.

### 4. Version Your Configuration
When making breaking changes, update `engine_version`:

```json
{
  "metadata": {
    "engine_version": "0.2.0"
  }
}
```

Check this in your game code to ensure compatibility.

### 5. Use Feature Flags
Disable unused systems to improve performance:

```json
{
  "settings": {
    "features_enabled": {
      "turn_based": false,      // Disable if real-time game
      "survival": false,         // Disable if no survival mechanics
      "base_building": false,    // Disable if no building system
      "pathfinding": false       // Disable if enemies don't need pathfinding
    }
  }
}
```

## Troubleshooting

### "Project not found"

**Problem**: `ProjectManager.load_project("my_game")` fails.

**Solution**: Ensure your project directory is in `projects/my_game/` relative to the engine root.

### "Missing required field"

**Problem**: Error loading `project.json`.

**Solution**: Ensure you have at minimum `metadata.name`, `metadata.version`, `paths`, and `settings.window`.

### "Invalid JSON syntax"

**Problem**: JSON parsing error.

**Solution**: Validate your JSON at [jsonlint.com](https://jsonlint.com). Common issues:
- Trailing commas: `{"a": 1,}` ❌ → `{"a": 1}` ✅
- Single quotes: `{'a': 1}` ❌ → `{"a": 1}` ✅
- Comments: JSON doesn't support comments

### Custom data not accessible

**Problem**: `project.config.custom_data.get("my_key")` returns None.

**Solution**: Remember `custom_data` is a dictionary. Use `.get()` for safe access:

```python
# Safe access with default
theme = project.config.custom_data.get("theme", "default")

# Check if key exists
if "theme" in project.config.custom_data:
    theme = project.config.custom_data["theme"]
```

## Next Steps

- [Creating Components](creating_components.md) - Build custom game data
- [Creating Systems](creating_systems.md) - Implement custom game logic
- [Getting Started](getting_started.md) - Build your first game
- [API Reference](api_reference.md) - Complete API documentation
