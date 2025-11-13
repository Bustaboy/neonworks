# NeonWorks Quick Start Guide

Get up and running with NeonWorks in under 5 minutes!

## Installation

### Step 1: Prerequisites

Make sure you have:
- **Python 3.8 or higher** (`python --version`)
- **pip** package manager (`pip --version`)

### Step 2: Install NeonWorks

```bash
# Clone or navigate to the NeonWorks repository
cd /path/to/neon-collapse

# Install in development mode (recommended for working with examples)
pip install -e engine/

# OR install with development tools (testing, linting, etc.)
pip install -e "engine/[dev]"
```

**What this does**:
- Installs NeonWorks as a Python package
- Installs dependencies (pygame, numpy)
- Makes the `engine` module available everywhere

**Verify installation**:
```bash
python -c "import engine; print('NeonWorks installed successfully!')"
```

## Run the Example Game

The fastest way to see NeonWorks in action:

```bash
# Navigate to the Simple RPG example
cd engine/examples/simple_rpg/

# Run the game
python main.py
```

**Controls**:
- WASD / Arrow Keys: Move
- SPACE: Attack / Start game
- ESC: Quit

**Goal**: Defeat 5 enemies to win!

## Create Your First Game

### Option 1: Use the Built-in Engine Launcher

```bash
# Create a new project
python -m engine.main create my_game

# Run your project
python -m engine.main my_game
```

### Option 2: Create From Scratch (Recommended for Learning)

#### 1. Create Project Structure

```bash
# Create your project directory
mkdir -p projects/my_game
cd projects/my_game
```

#### 2. Create project.json

Create `project.json`:

```json
{
  "metadata": {
    "name": "My Game",
    "version": "0.1.0",
    "author": "Your Name"
  },
  "paths": {
    "assets": "assets",
    "scripts": "scripts"
  },
  "settings": {
    "window": {
      "width": 800,
      "height": 600,
      "title": "My Game",
      "fullscreen": false
    },
    "tile_size": 32,
    "target_fps": 60,
    "features_enabled": {
      "rendering": true,
      "physics": true
    }
  }
}
```

#### 3. Create Game Script

Create `scripts/game.py`:

```python
"""Main game logic."""
from engine.core.ecs import World, Transform, Component
from dataclasses import dataclass
import pygame
import math

# Define custom component
@dataclass
class PlayerController(Component):
    speed: float = 200.0

# Create player entity
def setup_game(world: World):
    player = world.create_entity("player")
    player.add_component(Transform(x=400, y=300))
    player.add_component(PlayerController(speed=200.0))
    player.add_tag("player")
    print("Game ready! Use WASD to move.")
    return player

# Update function (called each frame)
def update_game(world: World, delta_time: float):
    players = world.get_entities_with_tag("player")
    if not players:
        return

    player = players[0]
    transform = player.get_component(Transform)
    controller = player.get_component(PlayerController)

    # Handle input
    keys = pygame.key.get_pressed()
    dx, dy = 0, 0

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        dx -= 1
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        dx += 1
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        dy -= 1
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        dy += 1

    # Update position
    if dx != 0 or dy != 0:
        length = math.sqrt(dx*dx + dy*dy)
        dx /= length
        dy /= length
        transform.x += dx * controller.speed * delta_time
        transform.y += dy * controller.speed * delta_time

# Render function
def render_game(screen: pygame.Surface, world: World):
    screen.fill((20, 20, 40))  # Dark blue background

    # Draw player
    players = world.get_entities_with_tag("player")
    if players:
        transform = players[0].get_component(Transform)
        pygame.draw.circle(screen, (0, 255, 0),
                         (int(transform.x), int(transform.y)), 16)
```

#### 4. Create Main Entry Point

Create `main.py`:

```python
#!/usr/bin/env python3
"""Main entry point."""
import pygame
import sys
import os

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from engine.core.ecs import World
from game import setup_game, update_game, render_game

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("My Game")
    clock = pygame.time.Clock()

    world = World()
    setup_game(world)

    running = True
    while running:
        delta_time = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        update_game(world, delta_time)
        render_game(screen, world)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
```

#### 5. Run Your Game!

```bash
python main.py
```

You should see a green circle that moves with WASD/arrow keys!

## What's Next?

### Learn the Basics

1. **[Getting Started Guide](engine/docs/getting_started.md)** - 5-minute tutorial
2. **[API Reference](engine/docs/api_reference.md)** - Complete API documentation
3. **[Creating Components](engine/docs/creating_components.md)** - Build custom components
4. **[Creating Systems](engine/docs/creating_systems.md)** - Implement game logic
5. **[Project Configuration](engine/docs/project_configuration.md)** - Configure your game

### Study the Example

The Simple RPG example (`engine/examples/simple_rpg/`) is a complete game showing:
- Player movement and combat
- AI enemies with state machines
- Health system and UI
- Multiple game screens
- Score tracking

**Read the code**:
- `scripts/components.py` - Custom components
- `scripts/systems.py` - Custom systems
- `scripts/game.py` - Game setup and rendering
- `README.md` - Complete walkthrough

### Explore Features

NeonWorks includes:

#### Core Systems
- **ECS Architecture** - Flexible entity-component-system
- **Event System** - Decoupled communication
- **State Management** - Game states and scenes
- **Save/Load** - Automatic serialization

#### Built-in Components
- Transform, GridPosition, Sprite
- Health, Survival
- Collider, RigidBody
- TurnActor, Building, ResourceStorage

#### Built-in Systems
- **Turn-Based Combat** - Initiative-based turns
- **Survival System** - Hunger, thirst, energy
- **Building System** - Base building with upgrades
- **Pathfinding** - A* navigation
- **Collision Detection** - With spatial partitioning

#### Rendering
- Sprite rendering with layers
- Camera system (pan, zoom, follow)
- Animation system
- Particle effects
- Tilemap support
- UI widgets (Button, Label, Panel, etc.)

#### Other Features
- **Input Management** - Action mapping, buffering
- **Audio Management** - Sound and music playback
- **Asset Management** - Loading and caching
- **Project System** - Multi-game support

## Troubleshooting

### "ModuleNotFoundError: No module named 'engine'"

**Problem**: NeonWorks not installed or not in Python path.

**Solution**:
```bash
# Make sure you're in the neon-collapse directory
cd /path/to/neon-collapse

# Install in development mode
pip install -e engine/

# Verify
python -c "import engine; print('Success!')"
```

### "pygame not found"

**Problem**: Pygame not installed.

**Solution**:
```bash
pip install pygame
# Or reinstall NeonWorks which will install dependencies
pip install -e engine/
```

### "Permission denied" when installing

**Problem**: Need admin/sudo permissions.

**Solution**:
```bash
# Install for current user only
pip install --user -e engine/
```

### Example game doesn't run

**Problem**: Wrong directory or missing files.

**Solution**:
```bash
# Make sure you're in the example directory
cd /path/to/neon-collapse/engine/examples/simple_rpg/

# Check files exist
ls -la
# Should see: main.py, project.json, scripts/

# Run
python main.py
```

### Black screen or crashes

**Problem**: Missing configuration or syntax error.

**Solution**:
1. Check console for error messages
2. Verify `project.json` is valid JSON (use [jsonlint.com](https://jsonlint.com))
3. Make sure all required fields are present in `project.json`
4. Check Python version: `python --version` (need 3.8+)

## Getting Help

- **Documentation**: See `engine/docs/` for complete guides
- **Examples**: See `engine/examples/` for working code
- **Issues**: Report bugs on GitHub
- **Community**: Join discussions on Discord/Forum

## Quick Reference

### Common Commands

```bash
# Install NeonWorks
pip install -e engine/

# Run example game
cd engine/examples/simple_rpg/ && python main.py

# Create new project directory
mkdir -p projects/my_game

# Run tests
pytest engine/tests/

# Format code
black engine/

# Lint code
flake8 engine/
```

### Import Patterns

```python
# Core ECS
from engine.core.ecs import World, Entity, Component, System, Transform

# Built-in components
from engine.core.ecs import Health, Sprite, Collider, RigidBody

# Events
from engine.core.events import EventManager, Event, EventType

# Rendering
from engine.rendering.renderer import Renderer
from engine.rendering.camera import Camera
from engine.rendering.assets import AssetManager

# Input
from engine.input.input_manager import InputManager

# Audio
from engine.audio.audio_manager import AudioManager

# Project
from engine.core.project import ProjectManager

# Game loop
from engine.core.game_loop import GameEngine, EngineConfig
```

### Entity Patterns

```python
# Create entity
entity = world.create_entity("my_entity")

# Add components
entity.add_component(Transform(x=100, y=200))
entity.add_component(Health(current=100, maximum=100))

# Chain components
entity.add_component(Transform(x=100, y=200)) \
      .add_component(Health(current=100, maximum=100)) \
      .add_tag("player")

# Query entities
for entity in world.get_entities_with_component(Health):
    health = entity.get_component(Health)
    # ...

# Multiple components
for entity in world.get_entities_with_components(Transform, Sprite):
    transform = entity.get_component(Transform)
    sprite = entity.get_component(Sprite)
    # ...

# By tag
players = world.get_entities_with_tag("player")
```

### System Pattern

```python
from engine.core.ecs import System, World

class MySystem(System):
    def __init__(self):
        super().__init__()
        self.priority = 10  # Lower runs first

    def update(self, world: World, delta_time: float):
        # Process entities
        for entity in world.get_entities_with_component(MyComponent):
            # Game logic here
            pass
```

## Next Steps

You're ready to build your game! Start with:

1. ✅ Run the example game
2. ✅ Read the Getting Started guide
3. ✅ Create a simple project
4. ✅ Study the API reference
5. ✅ Build your first complete game!

Happy game development! 🎮
