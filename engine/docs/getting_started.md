# Getting Started with NeonWorks

Welcome to NeonWorks! This 5-minute quickstart will get you from zero to a running game.

## What is NeonWorks?

NeonWorks is a Python 2D game engine built on Pygame, featuring:
- **Entity Component System (ECS)** architecture for flexible game design
- **Project-based workflow** - build multiple games with one engine
- **Built-in systems** for turn-based combat, survival mechanics, base building, pathfinding
- **Complete rendering pipeline** with sprites, animations, tilemaps, particles, and UI
- **Save/load system** with automatic serialization
- **Event-driven architecture** for decoupled game logic

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install NeonWorks

```bash
# Clone or download the NeonWorks repository
cd /path/to/neon-collapse

# Install in development mode
pip install -e engine/

# Or install with dev tools
pip install -e "engine/[dev]"
```

This installs NeonWorks and its dependencies (pygame, numpy).

## Your First Game in 5 Minutes

### 1. Create a New Project

```bash
# Create project directory
mkdir -p projects/my_first_game
cd projects/my_first_game
```

### 2. Create project.json

Create `project.json` with minimal configuration:

```json
{
    "metadata": {
        "name": "My First Game",
        "version": "0.1.0",
        "author": "Your Name",
        "description": "My first NeonWorks game"
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
            "title": "My First Game",
            "fullscreen": false
        },
        "tile_size": 32,
        "target_fps": 60,
        "features_enabled": {
            "rendering": true,
            "physics": true,
            "audio": true,
            "turn_based": false,
            "survival": false,
            "base_building": false
        }
    }
}
```

### 3. Create Your Game Script

Create `scripts/game.py`:

```python
from engine.core.ecs import World, Entity, Component, System
from engine.core.game_loop import GameEngine
from engine.core.events import EventManager, EventType
from engine.rendering.renderer import Renderer
from dataclasses import dataclass
import pygame

# Define a custom component for player control
@dataclass
class PlayerController(Component):
    """Component that marks an entity as player-controlled."""
    speed: float = 200.0  # pixels per second

# Define a system to handle player movement
class PlayerMovementSystem(System):
    """System that moves the player based on keyboard input."""

    def __init__(self):
        super().__init__(priority=10)

    def update(self, world: World, delta_time: float):
        # Get all entities with PlayerController and Transform components
        for entity in world.get_entities_with_components(PlayerController, Transform):
            player = entity.get_component(PlayerController)
            transform = entity.get_component(Transform)

            # Check keyboard input
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
                # Normalize diagonal movement
                import math
                length = math.sqrt(dx*dx + dy*dy)
                dx /= length
                dy /= length

                transform.x += dx * player.speed * delta_time
                transform.y += dy * player.speed * delta_time

# Import Transform component (built-in)
from engine.core.ecs import Transform

def setup_game(world: World, renderer: Renderer):
    """Set up the initial game state."""

    # Create the player entity
    player = world.create_entity("player")
    player.add_component(Transform(x=400, y=300))  # Center of 800x600 screen
    player.add_component(PlayerController(speed=200.0))

    # If you have a sprite, you can add it:
    # from engine.rendering.renderer import Sprite
    # player.add_component(Sprite(image_path="assets/player.png"))

    # Add the player movement system
    world.add_system(PlayerMovementSystem())

    print("Game setup complete! Use WASD or arrow keys to move.")
```

### 4. Create the Main Entry Point

Create `main.py`:

```python
#!/usr/bin/env python3
"""Main entry point for My First Game."""

from engine.core.project import ProjectManager
from engine.core.game_loop import GameEngine, EngineConfig
from engine.rendering.renderer import Renderer
from engine.core.ecs import World
import pygame
import sys
import os

# Add scripts to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from game import setup_game

def main():
    # Initialize Pygame
    pygame.init()

    # Load project configuration
    project_manager = ProjectManager()
    project = project_manager.load_project("my_first_game")

    # Create engine configuration
    config = EngineConfig(
        target_fps=project.config.settings.target_fps,
        max_frame_time=0.25,
        enable_vsync=False
    )

    # Create game engine
    engine = GameEngine(config)

    # Create renderer
    window_settings = project.config.settings.window
    screen = pygame.display.set_mode((window_settings.width, window_settings.height))
    pygame.display.set_caption(window_settings.title)
    renderer = Renderer(screen, tile_size=project.config.settings.tile_size)

    # Create world
    world = World()

    # Set up the game
    setup_game(world, renderer)

    # Game loop
    running = True
    clock = pygame.time.Clock()

    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Update
        delta_time = clock.tick(config.target_fps) / 1000.0  # Convert to seconds
        world.update(delta_time)

        # Render
        screen.fill((20, 20, 40))  # Dark blue background

        # Draw entities (if they have sprites)
        from engine.core.ecs import Transform
        for entity in world.get_entities_with_component(Transform):
            transform = entity.get_component(Transform)
            # Draw a simple circle for the player
            pygame.draw.circle(screen, (0, 255, 0),
                             (int(transform.x), int(transform.y)), 16)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
```

### 5. Run Your Game!

```bash
# Make sure you're in the project directory
cd /path/to/neon-collapse/projects/my_first_game

# Run the game
python main.py
```

You should see a window with a green circle that moves with WASD or arrow keys!

## What You Just Built

In just a few minutes, you created a NeonWorks game with:

1. **Entity Component System**: The player is an Entity with Transform and PlayerController components
2. **Custom System**: PlayerMovementSystem processes input and updates position
3. **Project Configuration**: project.json defines your game settings
4. **Game Loop**: Handles update/render cycle at 60 FPS

## Next Steps

Now that you have a basic game running, explore:

- **[API Reference](api_reference.md)** - Deep dive into core classes
- **[Creating Components](creating_components.md)** - Build custom components for your game
- **[Creating Systems](creating_systems.md)** - Implement custom game logic
- **[Project Configuration](project_configuration.md)** - Advanced project settings
- **[Example: Simple RPG](../examples/simple_rpg/README.md)** - Complete working game with combat, UI, and multiple screens

## Common Issues

### "Module not found: engine"
Make sure you installed NeonWorks: `pip install -e engine/`

### "Project not found"
The ProjectManager looks for projects in the `projects/` directory relative to the engine root. Make sure your project directory is in the right location.

### "Black screen"
If you see a black screen, your entities might be rendering outside the visible area. Check that Transform coordinates are within your window dimensions (default 800x600).

### Performance issues
- Reduce target_fps in project.json
- Disable features you're not using in features_enabled
- Use spatial partitioning for collision detection (enable QuadTree)

## Tips for Success

1. **Start Simple**: Begin with basic movement and add features incrementally
2. **Use the Event System**: Decouple your code with events (see api_reference.md)
3. **Leverage Built-in Components**: Transform, Sprite, Health, etc. save you time
4. **Study the Example**: The Simple RPG example shows best practices
5. **Enable Only What You Need**: Turn off unused features in project.json for better performance

Happy game development with NeonWorks!
