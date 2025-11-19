# NeonWorks Documentation

Welcome to the NeonWorks game engine documentation!

## Quick Links

### Getting Started
- **[Getting Started Guide](getting_started.md)** - Launcher-first onboarding and quick tutorial
- **[LAUNCHER_README.md](../LAUNCHER_README.md)** - Visual launcher walkthrough (recommended entry point)
- **[QUICKSTART.md](../../QUICKSTART.md)** - Installation and setup (includes CLI alternative)

### Core Documentation
- **[API Reference](api_reference.md)** - Complete API documentation for all core classes
- **[Creating Components](creating_components.md)** - Guide to building custom game components
- **[Creating Systems](creating_systems.md)** - Guide to implementing custom game logic
- **[Project Configuration](project_configuration.md)** - How to configure project.json

### Examples
- **[Simple RPG](../examples/simple_rpg/README.md)** - Complete working game with code walkthrough

## What is NeonWorks?

NeonWorks is a Python 2D game engine built on Pygame featuring:

- **Entity Component System (ECS)** - Flexible, composition-based architecture
- **Project-based workflow** - Build multiple games with one engine
- **Built-in systems** - Turn-based combat, survival, base building, pathfinding
- **Complete rendering** - Sprites, animations, tilemaps, particles, UI
- **Save/load** - Automatic serialization
- **Event system** - Decoupled communication

## Documentation Structure

### For Beginners

1. **[Getting Started](getting_started.md)** - Start here! Quick tutorial
2. **[Simple RPG Example](../examples/simple_rpg/README.md)** - Working game to study
3. **[Creating Components](creating_components.md)** - Add custom data
4. **[Creating Systems](creating_systems.md)** - Add custom logic

### For Reference

- **[API Reference](api_reference.md)** - Detailed API for all classes
- **[Project Configuration](project_configuration.md)** - All project.json options

## Core Concepts

### Entity Component System (ECS)

NeonWorks uses ECS architecture where:

- **Entities** are containers (game objects)
- **Components** are data (position, health, etc.)
- **Systems** are logic (movement, combat, etc.)

```python
# Create entity
player = world.create_entity("player")

# Add components (data)
player.add_component(Transform(x=100, y=200))
player.add_component(Health(current=100, maximum=100))

# Add system (logic)
world.add_system(MovementSystem())

# Update (processes all systems and entities)
world.update(delta_time)
```

### Components

Components are pure data containers:

```python
from dataclasses import dataclass
from neonworks.core.ecs import Component

@dataclass
class Velocity(Component):
    dx: float = 0.0  # Horizontal velocity
    dy: float = 0.0  # Vertical velocity
```

See [Creating Components](creating_components.md) for details.

### Systems

Systems contain game logic:

```python
from neonworks.core.ecs import System, World

class MovementSystem(System):
    def update(self, world: World, delta_time: float):
        # Query entities with Transform and Velocity
        for entity in world.get_entities_with_components(Transform, Velocity):
            transform = entity.get_component(Transform)
            velocity = entity.get_component(Velocity)

            # Update position
            transform.x += velocity.dx * delta_time
            transform.y += velocity.dy * delta_time
```

See [Creating Systems](creating_systems.md) for details.

## Built-in Features

### Components
- `Transform` - Position, rotation, scale
- `GridPosition` - Grid-based positioning
- `Sprite` - Visual representation
- `Health` - HP and regeneration
- `Survival` - Hunger, thirst, energy
- `Building` - Base building
- `ResourceStorage` - Resource management
- `Navmesh` - Pathfinding data
- `TurnActor` - Turn-based combat
- `Collider` - Collision detection
- `RigidBody` - Physics

### Systems
- **TurnSystem** - Turn-based combat with initiative
- **SurvivalSystem** - Hunger/thirst/energy management
- **BuildingSystem** - Base building with upgrades
- **PathfindingSystem** - A* pathfinding

### Rendering
- Sprite rendering with layers
- Camera (pan, zoom, follow)
- Animation system
- Particle effects
- Tilemap support
- UI widgets (buttons, labels, panels, etc.)

### Other
- **Event system** - Decoupled communication
- **Input management** - Action mapping
- **Audio management** - Sound and music
- **Asset management** - Loading and caching
- **Save/load** - Automatic serialization

## Common Patterns

### Query Entities

```python
# Single component
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
enemies = world.get_entities_with_tag("enemy")
```

### Frame-Rate Independent Movement

Always multiply by `delta_time`:

```python
def update(self, world: World, delta_time: float):
    transform.x += velocity.dx * delta_time  # Correct
    transform.y += velocity.dy * delta_time
```

### Entity Factory Pattern

Create reusable entity creation functions:

```python
def create_player(world: World, x: float, y: float) -> Entity:
    player = world.create_entity("player")
    player.add_component(Transform(x=x, y=y))
    player.add_component(Health(current=100, maximum=100))
    player.add_component(Sprite(texture="player.png"))
    player.add_tag("player")
    return player
```

## Help and Support

- **Documentation Issues**: Check this docs folder
- **Code Examples**: See `examples/` directory
- **Bug Reports**: Submit on GitHub
- **Questions**: Discord/Forum community

## Contributing

Want to improve these docs? Contributions welcome!

1. Fork the repository
2. Make your improvements
3. Submit a pull request

---

Happy game development! 🎮
