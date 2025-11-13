# Basic Game Template

A minimal NeonWorks template demonstrating core engine features.

## What's Included

This template provides a simple foundation for building 2D games:

- **Player Movement**: Arrow key controls with smooth movement
- **Entity-Component-System**: Clean ECS architecture
- **Basic Rendering**: Simple sprite rendering system
- **Game Loop**: Fixed timestep game loop

## Features

- Responsive keyboard input
- Component-based entity system
- Delta time-based movement
- Simple rendering pipeline

## Getting Started

### 1. Run the Game

```bash
neonworks run <your_project_name>
```

Or run directly:

```bash
cd <your_project_name>
python scripts/main.py
```

### 2. Controls

- **Arrow Keys**: Move the player
- **ESC**: Quit the game

### 3. Customize

The main game logic is in `scripts/main.py`. Here are some ideas to expand the game:

#### Add More Entities

```python
# Create an obstacle
obstacle = world.create_entity()
obstacle.add_component(Position(400, 300))
obstacle.add_component(Sprite(color=(255, 100, 100), size=64))
```

#### Add Collision Detection

Create a new collision system:

```python
class CollisionSystem(System):
    def update(self, world: World, delta_time: float):
        # Check for collisions between entities
        pass
```

#### Add Scoring

Create a score component and UI rendering:

```python
class Score(Component):
    def __init__(self):
        self.points = 0
```

#### Load Sprites from Files

Replace colored rectangles with actual images:

```python
class ImageSprite(Component):
    def __init__(self, image_path: str):
        self.image = pygame.image.load(image_path)
```

## Project Structure

```
your_project/
├── project.json          # Project configuration
├── README.md            # This file
├── scripts/
│   └── main.py          # Main game logic
├── assets/              # Images, sounds, etc.
├── levels/              # Level data files
├── config/              # Game configuration
└── saves/               # Save game files
```

## Next Steps

1. **Add Assets**: Place images in `assets/` and load them as sprites
2. **Create Levels**: Design levels and save them in `levels/`
3. **Add Systems**: Create new systems for game mechanics
4. **Enable Features**: Edit `project.json` to enable turn-based combat, building, etc.

## Documentation

- [NeonWorks Getting Started](../../../docs/getting_started.md)
- [ECS Architecture](../../../docs/core_concepts.md)
- [Project Configuration](../../../docs/project_configuration.md)
- [API Reference](../../../docs/api_reference.md)

## Example Expansions

### Add Enemies with AI

```python
class Enemy(Component):
    pass

class AISystem(System):
    def update(self, world: World, delta_time: float):
        for entity in world.get_entities_with_component(Enemy):
            # Add AI behavior
            pass
```

### Add Health System

```python
class Health(Component):
    def __init__(self, max_hp: int = 100):
        self.current = max_hp
        self.maximum = max_hp

class HealthSystem(System):
    def update(self, world: World, delta_time: float):
        for entity in world.get_entities_with_component(Health):
            health = entity.get_component(Health)
            if health.current <= 0:
                world.destroy_entity(entity)
```

## Tips

- Keep your game loop running at a consistent frame rate
- Use delta time for smooth, frame-rate-independent movement
- Organize code into separate component and system files as your game grows
- Test frequently and iterate quickly

Happy game development!
