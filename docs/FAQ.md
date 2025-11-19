# NeonWorks FAQ (Frequently Asked Questions)

Common questions and answers to help you get the most out of NeonWorks.

## Getting Started

### Q: What is NeonWorks?
**A:** NeonWorks is a Python 2D game engine built on Pygame with an Entity Component System (ECS) architecture. It's designed for creating turn-based, survival, and action games with built-in systems for rendering, physics, audio, and more.

### Q: What Python version do I need?
**A:** Python 3.8 or higher is required. We recommend Python 3.10+ for best performance.

### Q: How do I install NeonWorks?
**A:** Clone the repository and run:
```bash
pip install -e .
```
Or with development tools:
```bash
pip install -e ".[dev]"
```

### Q: Can I use NeonWorks for commercial games?
**A:** Yes! Check the LICENSE file in the repository for specific terms.

## Entity Component System (ECS)

### Q: What is an Entity?
**A:** An Entity is a unique game object identified by an ID. It's a container for Components but has no behavior itself. Think of it as a "thing" in your game (player, enemy, item, UI element, etc.).

### Q: What is a Component?
**A:** Components are pure data containers attached to Entities. Examples: `Transform` (position), `Health` (HP values), `Sprite` (visual representation). Components have no logic.

### Q: What is a System?
**A:** Systems contain the game logic and operate on Entities with specific Components. For example, `MovementSystem` processes all Entities with `Transform` and `Velocity` components.

### Q: How do I create a custom Component?
**A:** Inherit from `Component` and use `@dataclass`:
```python
from neonworks.core.ecs import Component
from dataclasses import dataclass

@dataclass
class Inventory(Component):
    items: list = field(default_factory=list)
    max_slots: int = 20
```

### Q: How do I create a custom System?
**A:** Inherit from `System` and implement the `update` method:
```python
from neonworks.core.ecs import System, World

class InventorySystem(System):
    def update(self, world: World, delta_time: float):
        for entity in world.get_entities_with_component(Inventory):
            inventory = entity.get_component(Inventory)
            # Process inventory logic
```

### Q: Why is my System not running?
**A:** Check these common issues:
1. Did you add it to the World? `world.add_system(MySystem())`
2. Is the System enabled? `system.enabled = True`
3. Are there Entities with the required Components?
4. Check the System priority - lower numbers run first

### Q: How do I query Entities efficiently?
**A:** Use World's query methods:
- `world.get_entities_with_component(Transform)` - Single component
- `world.get_entities_with_components(Transform, Health)` - Multiple components
- `world.get_entities_with_tag("enemy")` - Tagged entities

These use indexed lookups for fast performance.

## Performance

### Q: My game is running slowly. How do I optimize it?
**A:** Follow these steps:
1. **Profile first**: Identify the bottleneck
2. **Reduce entity count**: Pool/reuse entities instead of creating/destroying
3. **Optimize Systems**: Process only entities that changed
4. **Use spatial partitioning**: Enable QuadTree for collision detection
5. **Disable unused features**: Turn off systems you don't need
6. **Cache component lookups**: Store references instead of calling `get_component()` repeatedly

### Q: How many entities can NeonWorks handle?
**A:** Depends on your hardware and game complexity, but generally:
- **Simple games**: 10,000+ entities at 60 FPS
- **Complex games**: 1,000-5,000 entities at 60 FPS
- Use entity pooling and spatial partitioning for best results

### Q: Should I use delta_time for everything?
**A:** Yes! Always multiply movement and time-based changes by `delta_time` to ensure consistent behavior regardless of frame rate:
```python
transform.x += velocity * delta_time  # Good
transform.x += velocity              # Bad - frame-dependent
```

## Events

### Q: How do I use the event system?
**A:** Events decouple your code:
```python
from neonworks.core.events import get_event_manager, EventType, Event

# Subscribe
def on_damage(event):
    print(f"Damage dealt: {event.data['amount']}")

get_event_manager().subscribe(EventType.DAMAGE_DEALT, on_damage)

# Emit
get_event_manager().emit(Event(EventType.DAMAGE_DEALT, {"amount": 10}))
```

### Q: Should I use events or direct system communication?
**A:**
- **Events**: When multiple systems need to react to something, or for loose coupling
- **Direct communication**: When one system needs specific data from another

Use events for game-wide notifications (damage, level up, item collected), direct calls for targeted queries.

### Q: Are events processed immediately?
**A:** By default, events are queued and processed by calling `event_manager.process_events()`. Use `emit_immediate()` if you need instant processing.

## Project Structure

### Q: How do I organize my game project?
**A:** Recommended structure:
```
my_game/
├── project.json          # Project configuration
├── main.py              # Entry point
├── assets/              # Art, audio, fonts
│   ├── sprites/
│   ├── sounds/
│   └── fonts/
├── scripts/             # Game logic
│   ├── game.py          # Main game setup
│   ├── components.py    # Custom components
│   └── systems.py       # Custom systems
├── levels/              # Level data (JSON)
└── saves/               # Save files
```

### Q: How do I reference assets?
**A:** Use paths relative to your project root:
```python
sprite = Sprite(texture="assets/sprites/player.png")
```
The engine uses the `paths.assets` value from `project.json`.

### Q: Can I have multiple projects?
**A:** Yes! Create separate directories under `projects/` and load them with:
```python
project = project_manager.load_project("my_game_name")
```

## Rendering

### Q: How do I add a sprite to an entity?
**A:** Add a `Transform` and `Sprite` component:
```python
entity.add_component(Transform(x=100, y=100))
entity.add_component(Sprite(texture="assets/player.png", width=32, height=32))
```

### Q: My sprites aren't rendering. What's wrong?
**A:** Check:
1. Is the Renderer system added to the world?
2. Does the entity have both `Transform` and `Sprite` components?
3. Is the texture path correct relative to project root?
4. Is `sprite.visible = True`?
5. Is the entity within camera bounds?

### Q: How do I create animations?
**A:** Use the `AnimatedSprite` component:
```python
from engine.rendering.animation import AnimatedSprite, Animation

anim = AnimatedSprite()
anim.add_animation("walk", Animation(
    frames=["walk1.png", "walk2.png", "walk3.png"],
    frame_duration=0.1
))
anim.play("walk")
entity.add_component(anim)
```

### Q: How do I implement a camera?
**A:** Use the `Camera` class in the Renderer:
```python
from engine.rendering.camera import Camera

camera = Camera(width=800, height=600)
camera.follow(player_entity)  # Camera follows player
renderer.set_camera(camera)
```

## Physics & Collision

### Q: How do I add collision detection?
**A:** Add `Collider` component and use the `CollisionSystem`:
```python
entity.add_component(Collider(width=32, height=32))
world.add_system(CollisionSystem())
```

### Q: How do I make an entity move with physics?
**A:** Add `RigidBody` component:
```python
entity.add_component(RigidBody(velocity_x=100, velocity_y=0, mass=1.0))
world.add_system(PhysicsSystem())
```

### Q: How do I detect collision between specific entities?
**A:** Use collision layers or tags:
```python
# Set collision layers
player_collider = Collider(layer=1, mask=0b10)  # Collides with layer 1
enemy_collider = Collider(layer=2, mask=0b01)   # Collides with layer 0

# Or use tags
player.add_tag("player")
enemy.add_tag("enemy")
```

## Turn-Based Games

### Q: How do I implement turn-based gameplay?
**A:** Use the `TurnSystem`:
```python
from engine.systems.turn_system import TurnSystem

# Add TurnActor component to entities
entity.add_component(TurnActor(action_points=2, initiative=10))

# Add turn system
world.add_system(TurnSystem())
```

### Q: How do I determine turn order?
**A:** The `TurnSystem` sorts entities by their `initiative` value (higher goes first). You can customize this:
```python
turn_system = TurnSystem()
turn_system.set_sort_key(lambda entity: entity.get_component(TurnActor).initiative)
```

## Audio

### Q: How do I play sounds?
**A:** Use the AudioManager:
```python
from engine.audio.manager import AudioManager

audio = AudioManager()
audio.load_sound("hit", "assets/sounds/hit.wav")
audio.play_sound("hit")
```

### Q: How do I play background music?
**A:**
```python
audio.load_music("assets/music/background.mp3")
audio.play_music(loops=-1)  # Loop forever
```

## Save/Load System

### Q: How do I save game state?
**A:** Use the serialization system:
```python
from neonworks.core.serialization import save_world, load_world

# Save
save_world(world, "saves/savegame.json")

# Load
world = load_world("saves/savegame.json")
```

### Q: What gets saved automatically?
**A:** All entities, components, and their data. Systems are recreated on load.

### Q: How do I save custom data?
**A:** Make sure your custom components are registered:
```python
from neonworks.core.serialization import register_component

register_component(MyCustomComponent)
```

## Debugging

### Q: How do I debug my game?
**A:** Use these techniques:
1. **Print debugging**: Add prints in Systems
2. **Visual debugging**: Draw debug info with Renderer
3. **Entity inspector**: Print entity components
4. **Event logging**: Log all events
5. **Breakpoints**: Use Python debugger (`import pdb; pdb.set_trace()`)

### Q: How do I see all entities and their components?
**A:**
```python
for entity in world.get_entities():
    print(f"Entity {entity.id}:")
    for comp_type, comp in entity._components.items():
        print(f"  {comp_type.__name__}: {comp}")
```

### Q: My events aren't firing. What's wrong?
**A:** Check:
1. Did you subscribe to the event? `event_manager.subscribe(EventType.X, handler)`
2. Is the event being emitted? Add print statement
3. Are you calling `process_events()` in your game loop?
4. Is the event handler function signature correct? `def handler(event: Event)`

## Common Errors

### Q: "AttributeError: 'NoneType' object has no attribute 'x'"
**A:** You're accessing a Component that doesn't exist. Always check:
```python
transform = entity.get_component(Transform)
if transform:
    # Safe to use transform.x
```

### Q: "KeyError: entity_id"
**A:** The entity was removed from the world. Store entity IDs, not entity references, or check if entity exists:
```python
entity = world.get_entity(entity_id)
if entity:
    # Entity still exists
```

### Q: "ModuleNotFoundError: No module named 'engine'"
**A:** Install NeonWorks: `pip install -e .`

### Q: Game loop hangs or freezes
**A:** You have an infinite loop in a System. Make sure all loops in `update()` methods can complete in one frame.

## Advanced Topics

### Q: Can I create multiplayer games with NeonWorks?
**A:** NeonWorks focuses on single-player, but you can add networking:
1. Serialize World state for syncing
2. Use Python networking libraries (socket, asyncio)
3. Implement client-server or peer-to-peer architecture
4. Handle latency compensation and prediction

### Q: How do I implement pathfinding?
**A:** Use the built-in `Navmesh` component and pathfinding utilities:
```python
from engine.ai.pathfinding import find_path, create_navmesh

navmesh = create_navmesh(tilemap)
path = find_path(navmesh, start=(0,0), goal=(10,10))
```

### Q: Can I extend the engine?
**A:** Absolutely! NeonWorks is designed to be extended:
- Create custom Components
- Write custom Systems
- Add new event types
- Integrate third-party libraries
- Modify core systems (fork the repository)

### Q: How do I integrate with external tools?
**A:** NeonWorks supports:
- **Tiled Map Editor**: Import `.tmx` files
- **TexturePacker**: Load sprite sheets
- **External editors**: JSON-based level format
- **Version control**: All files are text-based (JSON)

## Still Have Questions?

- Check the [API Reference](api_reference.md) for detailed class documentation
- Study the [Example Projects](../examples/) for working implementations
- Read the [Creating Components](creating_components.md) and [Creating Systems](creating_systems.md) guides
- Join the community discussions (check README for links)
