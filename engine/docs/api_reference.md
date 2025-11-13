# NeonWorks API Reference

Complete reference for NeonWorks core classes and APIs.

## Table of Contents

1. [Entity Component System (ECS)](#entity-component-system-ecs)
   - [Entity](#entity)
   - [Component](#component)
   - [System](#system)
   - [World](#world)
2. [Built-in Components](#built-in-components)
3. [Game Engine](#game-engine)
4. [Events](#events)
5. [Rendering](#rendering)
6. [Input](#input)
7. [Audio](#audio)
8. [Project Management](#project-management)

---

## Entity Component System (ECS)

Located in: `engine/core/ecs.py`

The ECS architecture separates data (Components) from logic (Systems) and containers (Entities).

### Entity

**Description**: A container for components, identified by a unique UUID. Entities represent game objects.

**Constructor**:
```python
Entity(entity_id: Optional[str] = None)
```

**Attributes**:
- `id: str` - Unique identifier (UUID)
- `active: bool` - Whether the entity is active
- `tags: Set[str]` - Set of string tags for categorization

**Methods**:

#### add_component(component: Component) → Entity
Add a component to this entity. Returns self for method chaining.

```python
entity = world.create_entity("player")
entity.add_component(Transform(x=100, y=200))
      .add_component(Health(current=100, maximum=100))
      .add_component(Sprite(texture="player.png"))
```

#### remove_component(component_type: Type[Component]) → Entity
Remove a component from this entity.

```python
entity.remove_component(Health)
```

#### get_component(component_type: Type[Component]) → Optional[Component]
Get a component of the specified type.

```python
transform = entity.get_component(Transform)
if transform:
    transform.x += 10
```

#### has_component(component_type: Type[Component]) → bool
Check if entity has a specific component.

```python
if entity.has_component(Health):
    damage_entity(entity)
```

#### has_components(*component_types: Type[Component]) → bool
Check if entity has all specified components.

```python
if entity.has_components(Transform, Sprite, Health):
    # Entity is a visible, damageable object
    render_health_bar(entity)
```

#### add_tag(tag: str) → Entity
Add a tag to this entity for grouping/categorization.

```python
entity.add_tag("enemy").add_tag("flying")
```

#### remove_tag(tag: str) → Entity
Remove a tag from this entity.

```python
entity.remove_tag("flying")
```

#### has_tag(tag: str) → bool
Check if entity has a specific tag.

```python
if entity.has_tag("enemy"):
    apply_ai_behavior(entity)
```

---

### Component

**Description**: Base class for all components. Components are pure data containers.

**Usage**: Create custom components using dataclasses:

```python
from dataclasses import dataclass
from engine.core.ecs import Component

@dataclass
class Velocity(Component):
    dx: float = 0.0
    dy: float = 0.0
    max_speed: float = 100.0

@dataclass
class PlayerController(Component):
    speed: float = 200.0
    jump_force: float = 500.0
```

**Best Practices**:
- Keep components simple and focused on data
- Use dataclasses for automatic `__init__`, `__repr__`, etc.
- Provide sensible defaults
- Don't put logic in components (use Systems instead)

---

### System

**Description**: Abstract base class for systems. Systems contain logic that processes entities with specific components.

**Constructor**:
```python
System()
```

**Attributes**:
- `enabled: bool` - Whether this system is active (default: True)
- `priority: int` - Execution order (lower numbers run first, default: 0)

**Methods**:

#### update(world: World, delta_time: float) [ABSTRACT]
Called every frame. Implement your game logic here.

```python
from engine.core.ecs import System, World

class MovementSystem(System):
    def __init__(self):
        super().__init__()
        self.priority = 10  # Run early in the frame

    def update(self, world: World, delta_time: float):
        # Get all entities with Transform and Velocity components
        for entity in world.get_entities_with_components(Transform, Velocity):
            transform = entity.get_component(Transform)
            velocity = entity.get_component(Velocity)

            # Update position based on velocity
            transform.x += velocity.dx * delta_time
            transform.y += velocity.dy * delta_time
```

#### on_entity_added(entity: Entity)
Called when an entity is added to the world. Override to cache entity references.

```python
def on_entity_added(self, entity: Entity):
    if entity.has_component(PlayerController):
        self.player_entity = entity
```

#### on_entity_removed(entity: Entity)
Called when an entity is removed from the world. Override to clean up references.

```python
def on_entity_removed(self, entity: Entity):
    if entity == self.player_entity:
        self.player_entity = None
```

---

### World

**Description**: Manages all entities and systems. The central container for your game state.

**Constructor**:
```python
World()
```

**Entity Management**:

#### create_entity(entity_id: Optional[str] = None) → Entity
Create and add a new entity to the world.

```python
world = World()
player = world.create_entity("player")
enemy = world.create_entity()  # Auto-generated UUID
```

#### add_entity(entity: Entity) → World
Add an existing entity to the world.

```python
entity = Entity("custom_id")
entity.add_component(Transform())
world.add_entity(entity)
```

#### remove_entity(entity_id: str) → World
Remove an entity from the world.

```python
world.remove_entity(enemy.id)
```

#### get_entity(entity_id: str) → Optional[Entity]
Get an entity by its ID.

```python
player = world.get_entity("player")
```

#### get_entities() → List[Entity]
Get all entities in the world.

```python
all_entities = world.get_entities()
print(f"Total entities: {len(all_entities)}")
```

**Querying Entities** (Optimized with indexing):

#### get_entities_with_component(component_type: Type[Component]) → List[Entity]
Get all entities that have a specific component. **O(1) lookup thanks to indexing**.

```python
# Get all entities with health
for entity in world.get_entities_with_component(Health):
    health = entity.get_component(Health)
    print(f"Entity {entity.id} has {health.current}/{health.maximum} HP")
```

#### get_entities_with_components(*component_types: Type[Component]) → List[Entity]
Get all entities that have ALL specified components. **O(k) where k = number of component types**.

```python
# Get all visible, moving entities
for entity in world.get_entities_with_components(Transform, Sprite, Velocity):
    # Render and update
    pass
```

#### get_entities_with_tag(tag: str) → List[Entity]
Get all entities with a specific tag. **O(1) lookup thanks to indexing**.

```python
# Get all enemies
enemies = world.get_entities_with_tag("enemy")

# Get all interactive objects
interactables = world.get_entities_with_tag("interactable")
```

**System Management**:

#### add_system(system: System) → World
Add a system to the world. Systems are sorted by priority after adding.

```python
world.add_system(MovementSystem())
world.add_system(RenderSystem())
world.add_system(CollisionSystem())
```

#### remove_system(system: System) → World
Remove a system from the world.

```python
world.remove_system(my_system)
```

#### update(delta_time: float)
Update all enabled systems in priority order.

```python
# Game loop
while running:
    delta_time = clock.tick(60) / 1000.0
    world.update(delta_time)
```

#### clear()
Remove all entities and systems.

```python
world.clear()  # Reset the world
```

---

## Built-in Components

NeonWorks provides 11 built-in components for common game features.

### Transform
Position, rotation, and scale in 2D space.

```python
@dataclass
class Transform(Component):
    x: float = 0.0
    y: float = 0.0
    rotation: float = 0.0  # Degrees
    scale_x: float = 1.0
    scale_y: float = 1.0
```

**Usage**:
```python
entity.add_component(Transform(x=400, y=300, rotation=45))
```

### GridPosition
Grid-based position for tile-based games.

```python
@dataclass
class GridPosition(Component):
    grid_x: int = 0
    grid_y: int = 0
    layer: int = 0  # For multi-layer maps
```

**Usage**:
```python
tile.add_component(GridPosition(grid_x=10, grid_y=5, layer=1))
```

### Sprite
Visual representation with texture and color.

```python
@dataclass
class Sprite(Component):
    texture: str = ""
    width: int = 32
    height: int = 32
    color: tuple = (255, 255, 255, 255)  # RGBA
    visible: bool = True
```

**Usage**:
```python
entity.add_component(Sprite(texture="player.png", width=64, height=64))
```

### Health
Health points for combat and survival.

```python
@dataclass
class Health(Component):
    current: float = 100.0
    maximum: float = 100.0
    regeneration: float = 0.0  # HP per second
```

**Usage**:
```python
player.add_component(Health(current=100, maximum=100, regeneration=1.0))

# Take damage
health = entity.get_component(Health)
health.current -= 25
if health.current <= 0:
    entity.add_tag("dead")
```

### Survival
Survival needs (hunger, thirst, energy).

```python
@dataclass
class Survival(Component):
    hunger: float = 100.0  # 0 = starving, 100 = full
    thirst: float = 100.0  # 0 = dehydrated, 100 = hydrated
    energy: float = 100.0  # 0 = exhausted, 100 = well-rested
    hunger_rate: float = 1.0  # Points per turn
    thirst_rate: float = 1.5
    energy_rate: float = 0.5
```

### Building
For base-building games.

```python
@dataclass
class Building(Component):
    building_type: str = ""
    construction_progress: float = 0.0  # 0.0 to 1.0
    is_constructed: bool = False
    level: int = 1
    max_level: int = 3
```

### ResourceStorage
Store and manage resources.

```python
@dataclass
class ResourceStorage(Component):
    resources: Dict[str, float] = field(default_factory=dict)
    capacity: Dict[str, float] = field(default_factory=dict)

    def add_resource(self, resource_type: str, amount: float) -> float
    def remove_resource(self, resource_type: str, amount: float) -> float
```

**Usage**:
```python
storage = ResourceStorage()
storage.capacity = {"metal": 1000, "energy": 500}
storage.add_resource("metal", 250)

overflow = storage.add_resource("metal", 900)  # Returns 150 (overflow)
```

### Navmesh
Navigation mesh for pathfinding.

```python
@dataclass
class Navmesh(Component):
    walkable_cells: Set[tuple] = field(default_factory=set)
    cost_multipliers: Dict[tuple, float] = field(default_factory=dict)

    def is_walkable(self, x: int, y: int) -> bool
    def get_cost(self, x: int, y: int) -> float
```

### TurnActor
For turn-based game systems.

```python
@dataclass
class TurnActor(Component):
    action_points: int = 2
    max_action_points: int = 2
    initiative: int = 10
    has_acted: bool = False
```

### Collider
Collision box for physics.

```python
@dataclass
class Collider(Component):
    width: float = 32.0
    height: float = 32.0
    offset_x: float = 0.0
    offset_y: float = 0.0
    is_trigger: bool = False
    layer: int = 0  # 0-31
    mask: int = 0xFFFFFFFF  # Which layers to collide with
```

### RigidBody
Physics body for movement.

```python
@dataclass
class RigidBody(Component):
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    mass: float = 1.0
    friction: float = 0.1
    is_static: bool = False
    gravity_scale: float = 0.0  # Usually 0 for top-down games
```

---

## Game Engine

Located in: `engine/core/game_loop.py`

### GameEngine

Fixed-timestep game loop engine.

**Constructor**:
```python
GameEngine(config: EngineConfig)
```

**EngineConfig**:
```python
@dataclass
class EngineConfig:
    target_fps: int = 60
    max_frame_time: float = 0.25  # Maximum delta_time to prevent spiral of death
    enable_vsync: bool = False
```

**Methods**:
- `run()` - Start the game loop
- `stop()` - Stop the game loop
- `get_fps() → float` - Get current FPS
- `get_frame_time() → float` - Get average frame time in ms

**Usage**:
```python
from engine.core.game_loop import GameEngine, EngineConfig

config = EngineConfig(target_fps=60, max_frame_time=0.25)
engine = GameEngine(config)

# Set up your game
# ...

engine.run()
```

---

## Events

Located in: `engine/core/events.py`

Event system for decoupled communication between systems.

### EventManager (Singleton)

**Methods**:

#### subscribe(event_type: EventType, callback: Callable)
Subscribe to an event type.

```python
from engine.core.events import EventManager, EventType

def on_player_death(event):
    print(f"Player died! Score: {event.data.get('score')}")

EventManager.subscribe(EventType.ENTITY_DIED, on_player_death)
```

#### unsubscribe(event_type: EventType, callback: Callable)
Unsubscribe from an event type.

```python
EventManager.unsubscribe(EventType.ENTITY_DIED, on_player_death)
```

#### emit(event: Event)
Emit an event to all subscribers.

```python
from engine.core.events import Event, EventType

event = Event(
    type=EventType.ENTITY_DIED,
    data={"entity_id": player.id, "score": 1000}
)
EventManager.emit(event)
```

**Built-in Event Types**:
- `TURN_START`, `TURN_END`
- `UNIT_DIED`, `ENTITY_DIED`
- `RESOURCE_CHANGED`
- `BUILDING_CONSTRUCTED`, `BUILDING_UPGRADED`
- `COLLISION_ENTER`, `COLLISION_EXIT`
- `GAME_STARTED`, `GAME_PAUSED`, `GAME_OVER`
- `LEVEL_LOADED`
- Custom events: `EventType.CUSTOM`

---

## Rendering

Located in: `engine/rendering/`

### Renderer

**Constructor**:
```python
Renderer(screen: pygame.Surface, tile_size: int = 32)
```

**Methods**:
- `render(world: World, camera: Camera)` - Render all entities
- `render_entity(entity: Entity, camera: Camera)` - Render a single entity
- `set_background_color(color: tuple)` - Set clear color

### Camera

**Constructor**:
```python
Camera(width: int, height: int)
```

**Methods**:
- `set_position(x: float, y: float)` - Set camera position
- `follow(target: Entity, lerp_factor: float)` - Follow an entity smoothly
- `zoom(factor: float)` - Set zoom level (1.0 = normal)
- `world_to_screen(x: float, y: float) → tuple` - Convert world to screen coordinates
- `screen_to_world(x: float, y: float) → tuple` - Convert screen to world coordinates

### AssetManager (Singleton)

**Methods**:
- `load_image(path: str) → pygame.Surface` - Load and cache image
- `load_sound(path: str) → pygame.mixer.Sound` - Load and cache sound
- `load_music(path: str)` - Load music file
- `clear_cache()` - Clear all cached assets

---

## Input

Located in: `engine/input/input_manager.py`

### InputManager (Singleton)

**Methods**:
- `is_action_pressed(action: str) → bool` - Action pressed this frame
- `is_action_held(action: str) → bool` - Action held down
- `is_action_released(action: str) → bool` - Action released this frame
- `get_mouse_position() → tuple` - Get mouse (x, y) in screen space
- `update()` - Call once per frame to process input

**Default Actions**:
- Movement: `move_up`, `move_down`, `move_left`, `move_right`
- UI: `confirm`, `cancel`
- Combat: `attack`, `ability_1`, `ability_2`, `ability_3`, `ability_4`

**Usage**:
```python
from engine.input.input_manager import InputManager

if InputManager.is_action_pressed("attack"):
    player_attack()

if InputManager.is_action_held("move_right"):
    player.velocity_x = speed
```

---

## Audio

Located in: `engine/audio/audio_manager.py`

### AudioManager (Singleton)

**Methods**:
- `play_sound(sound_id: str, volume: float = 1.0)` - Play sound effect
- `play_music(music_id: str, volume: float = 1.0, loop: bool = True)` - Play music
- `stop_sound(sound_id: str)` - Stop sound
- `stop_music()` - Stop music
- `set_master_volume(volume: float)` - Set master volume (0.0-1.0)
- `set_music_volume(volume: float)` - Set music volume
- `set_sfx_volume(volume: float)` - Set SFX volume

**Usage**:
```python
from engine.audio.audio_manager import AudioManager

AudioManager.play_sound("explosion", volume=0.8)
AudioManager.play_music("background_music", loop=True)
AudioManager.set_master_volume(0.7)
```

---

## Project Management

Located in: `engine/core/project.py`

### ProjectManager (Singleton)

**Methods**:
- `load_project(project_name: str) → Project` - Load project by name
- `get_project(project_name: str) → Optional[Project]` - Get cached project
- `get_current_project() → Optional[Project]` - Get currently active project

**Project Structure**:
```python
@dataclass
class Project:
    name: str
    root_path: str
    config: ProjectConfig
```

**Usage**:
```python
from engine.core.project import ProjectManager

project = ProjectManager.load_project("my_game")
print(f"Loaded: {project.config.metadata.name}")
print(f"Version: {project.config.metadata.version}")
```

---

## Next Steps

- [Creating Custom Components](creating_components.md)
- [Creating Custom Systems](creating_systems.md)
- [Project Configuration](project_configuration.md)
- [Example: Simple RPG](../examples/simple_rpg/README.md)
