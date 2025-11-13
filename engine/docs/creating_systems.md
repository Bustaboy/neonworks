# Creating Custom Systems

Learn how to create custom game logic systems for your NeonWorks game.

## What Are Systems?

In the Entity Component System (ECS) architecture:
- **Systems** contain game logic and behavior
- They process entities that have specific components
- They describe **what entities do**, not **what they are**

Think of systems as the "verbs" of your game:
- A `MovementSystem` makes entities move
- A `RenderSystem` draws entities to the screen
- A `CombatSystem` handles damage and attacks

## System Basics

### Creating a Simple System

All systems inherit from `System` and implement the `update` method:

```python
from engine.core.ecs import System, World, Transform

class MovementSystem(System):
    """Moves entities based on their velocity."""

    def __init__(self):
        super().__init__()
        self.priority = 10  # Lower numbers run first

    def update(self, world: World, delta_time: float):
        """Called every frame."""
        # Query entities with both Transform and Velocity components
        for entity in world.get_entities_with_components(Transform, Velocity):
            transform = entity.get_component(Transform)
            velocity = entity.get_component(Velocity)

            # Update position based on velocity and time
            transform.x += velocity.dx * delta_time
            transform.y += velocity.dy * delta_time
```

**Key concepts**:
1. `__init__`: Set up system state and priority
2. `update`: Called every frame with `delta_time` (seconds since last frame)
3. `world.get_entities_with_components()`: Query entities with specific components
4. Systems should be stateless when possible (don't store entity references unnecessarily)

### Adding Systems to the World

```python
from engine.core.ecs import World

world = World()

# Add systems (they run in priority order)
world.add_system(MovementSystem())      # priority: 10
world.add_system(PhysicsSystem())       # priority: 20
world.add_system(RenderSystem())        # priority: 100

# Update all systems
while running:
    delta_time = clock.tick(60) / 1000.0
    world.update(delta_time)  # Calls update() on all systems
```

## System Priority

Systems execute in **priority order** (lowest first):

```python
class InputSystem(System):
    def __init__(self):
        super().__init__()
        self.priority = 0  # Runs first

class MovementSystem(System):
    def __init__(self):
        super().__init__()
        self.priority = 10  # Runs second

class PhysicsSystem(System):
    def __init__(self):
        super().__init__()
        self.priority = 20  # Runs third

class RenderSystem(System):
    def __init__(self):
        super().__init__()
        self.priority = 100  # Runs last
```

**Typical priority ranges**:
- `-100 to -50`: Core systems (turn management, state machines)
- `0 to 50`: Input and AI
- `50 to 100`: Game logic (movement, combat, etc.)
- `100 to 200`: Rendering and effects

## Querying Entities

### Single Component Query

```python
def update(self, world: World, delta_time: float):
    # Get all entities with Health component
    for entity in world.get_entities_with_component(Health):
        health = entity.get_component(Health)

        # Apply health regeneration
        if health.regeneration > 0:
            health.current = min(health.current + health.regeneration * delta_time,
                                health.maximum)
```

### Multiple Component Query

```python
def update(self, world: World, delta_time: float):
    # Get entities with Transform, Sprite, AND Velocity
    for entity in world.get_entities_with_components(Transform, Sprite, Velocity):
        transform = entity.get_component(Transform)
        velocity = entity.get_component(Velocity)

        # Update position
        transform.x += velocity.dx * delta_time
        transform.y += velocity.dy * delta_time
```

### Tag-Based Query

```python
def update(self, world: World, delta_time: float):
    # Get all entities tagged as "enemy"
    for entity in world.get_entities_with_tag("enemy"):
        # Apply AI behavior
        self.update_ai(entity, delta_time)

    # Get the player entity
    players = world.get_entities_with_tag("player")
    if players:
        player = players[0]
        # Do something with player
```

### Conditional Query

```python
def update(self, world: World, delta_time: float):
    # Get all entities with Health
    for entity in world.get_entities_with_component(Health):
        health = entity.get_component(Health)

        # Only process entities with low health
        if health.current < health.maximum * 0.25:
            # Apply critical health effects
            self.apply_low_health_effect(entity)
```

## System Patterns

### 1. Input Processing System

Handle player input:

```python
import pygame
from engine.core.ecs import System, World, Transform

class PlayerInputSystem(System):
    """Process player keyboard input."""

    def __init__(self):
        super().__init__()
        self.priority = 0  # Run first

    def update(self, world: World, delta_time: float):
        # Get player entity (assuming only one)
        players = world.get_entities_with_tag("player")
        if not players:
            return

        player = players[0]
        if not player.has_component(PlayerController):
            return

        controller = player.get_component(PlayerController)
        transform = player.get_component(Transform)

        # Get keyboard state
        keys = pygame.key.get_pressed()

        # Calculate movement direction
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1

        # Normalize diagonal movement
        if dx != 0 or dy != 0:
            import math
            length = math.sqrt(dx*dx + dy*dy)
            dx /= length
            dy /= length

            # Update position
            transform.x += dx * controller.speed * delta_time
            transform.y += dy * controller.speed * delta_time
```

### 2. Timer/Cooldown System

Track time-based effects:

```python
from engine.core.ecs import System, World

class CooldownSystem(System):
    """Update ability cooldowns."""

    def __init__(self):
        super().__init__()
        self.priority = 5

    def update(self, world: World, delta_time: float):
        for entity in world.get_entities_with_component(AbilityCooldowns):
            cooldowns = entity.get_component(AbilityCooldowns)

            # Decrease all cooldown timers
            for ability_name in list(cooldowns.cooldowns.keys()):
                cooldowns.cooldowns[ability_name] -= delta_time

                # Remove expired cooldowns
                if cooldowns.cooldowns[ability_name] <= 0:
                    del cooldowns.cooldowns[ability_name]
```

### 3. State Machine System

Manage entity state transitions:

```python
from engine.core.ecs import System, World
from enum import Enum

class AIState(Enum):
    IDLE = "idle"
    PATROL = "patrol"
    CHASE = "chase"
    ATTACK = "attack"

class AISystem(System):
    """AI state machine."""

    def __init__(self):
        super().__init__()
        self.priority = 10

    def update(self, world: World, delta_time: float):
        # Get player position for AI to track
        player = self._get_player(world)
        if not player:
            return

        player_transform = player.get_component(Transform)

        # Update each AI entity
        for entity in world.get_entities_with_component(AIController):
            ai = entity.get_component(AIController)
            transform = entity.get_component(Transform)

            # Calculate distance to player
            distance = self._distance(transform, player_transform)

            # State machine transitions
            if ai.state == AIState.IDLE:
                if distance < ai.detection_range:
                    ai.state = AIState.CHASE

            elif ai.state == AIState.CHASE:
                if distance > ai.detection_range * 1.5:
                    ai.state = AIState.IDLE
                elif distance < ai.attack_range:
                    ai.state = AIState.ATTACK

            elif ai.state == AIState.ATTACK:
                if distance > ai.attack_range * 1.2:
                    ai.state = AIState.CHASE

            # Execute state behavior
            if ai.state == AIState.IDLE:
                self._idle_behavior(entity, delta_time)
            elif ai.state == AIState.CHASE:
                self._chase_behavior(entity, player_transform, delta_time)
            elif ai.state == AIState.ATTACK:
                self._attack_behavior(entity, player, delta_time)

    def _get_player(self, world: World):
        players = world.get_entities_with_tag("player")
        return players[0] if players else None

    def _distance(self, transform1, transform2):
        import math
        dx = transform2.x - transform1.x
        dy = transform2.y - transform1.y
        return math.sqrt(dx*dx + dy*dy)

    def _idle_behavior(self, entity, delta_time):
        # Stand still
        pass

    def _chase_behavior(self, entity, target_transform, delta_time):
        # Move towards player
        ai = entity.get_component(AIController)
        transform = entity.get_component(Transform)

        dx = target_transform.x - transform.x
        dy = target_transform.y - transform.y

        # Normalize
        import math
        length = math.sqrt(dx*dx + dy*dy)
        if length > 0:
            dx /= length
            dy /= length

            # Move
            speed = 100.0  # AI movement speed
            transform.x += dx * speed * delta_time
            transform.y += dy * speed * delta_time

    def _attack_behavior(self, entity, target, delta_time):
        # Perform attack (simplified)
        ai = entity.get_component(AIController)
        if not hasattr(ai, 'attack_cooldown'):
            ai.attack_cooldown = 0

        ai.attack_cooldown -= delta_time
        if ai.attack_cooldown <= 0:
            # Apply damage
            target_health = target.get_component(Health)
            if target_health:
                target_health.current -= 10

            ai.attack_cooldown = 1.0  # 1 second between attacks
```

### 4. Cleanup System

Remove dead/expired entities:

```python
from engine.core.ecs import System, World

class CleanupSystem(System):
    """Remove dead entities."""

    def __init__(self):
        super().__init__()
        self.priority = 90  # Run late, after combat

    def update(self, world: World, delta_time: float):
        entities_to_remove = []

        # Find entities to remove
        for entity in world.get_entities_with_component(Health):
            health = entity.get_component(Health)
            if health.current <= 0:
                entities_to_remove.append(entity.id)

        # Remove dead entities
        for entity_id in entities_to_remove:
            world.remove_entity(entity_id)
```

### 5. Event-Based System

Use events for communication:

```python
from engine.core.ecs import System, World
from engine.core.events import EventManager, Event, EventType

class DamageSystem(System):
    """Handle damage events."""

    def __init__(self):
        super().__init__()
        self.priority = 50

        # Subscribe to damage events
        EventManager.subscribe(EventType.ENTITY_DAMAGED, self.on_damage)

    def update(self, world: World, delta_time: float):
        # This system is event-driven, no per-frame logic needed
        pass

    def on_damage(self, event: Event):
        """Handle damage event."""
        entity_id = event.data.get("entity_id")
        damage = event.data.get("damage", 0)
        damage_type = event.data.get("type", "physical")

        # Find entity in world and apply damage
        # (You'd need access to world here - see below for solution)
        print(f"Entity {entity_id} took {damage} {damage_type} damage")
```

**Better approach**: Store world reference:

```python
class DamageSystem(System):
    """Handle damage events."""

    def __init__(self):
        super().__init__()
        self.priority = 50
        self.world = None  # Will be set when added to world

    def update(self, world: World, delta_time: float):
        # Store world reference on first update
        if self.world is None:
            self.world = world

        # Process damage queue (populated by events)
        for entity_id, damage in self.damage_queue:
            entity = world.get_entity(entity_id)
            if entity and entity.has_component(Health):
                health = entity.get_component(Health)
                health.current -= damage

        self.damage_queue.clear()

    def apply_damage(self, entity_id: str, damage: float):
        """Queue damage to be applied next update."""
        if not hasattr(self, 'damage_queue'):
            self.damage_queue = []
        self.damage_queue.append((entity_id, damage))
```

## Advanced System Examples

### Example 1: Animation System

```python
from engine.core.ecs import System, World, Sprite

class AnimationSystem(System):
    """Update sprite animations."""

    def __init__(self):
        super().__init__()
        self.priority = 50

    def update(self, world: World, delta_time: float):
        for entity in world.get_entities_with_components(Sprite, AnimationState):
            sprite = entity.get_component(Sprite)
            animation = entity.get_component(AnimationState)

            # Update frame timer
            animation.frame_time += delta_time

            # Check if it's time to advance frame
            if animation.frame_time >= animation.frame_duration:
                animation.frame_time = 0.0

                # Get current animation frames
                frames = animation.animations.get(animation.current_animation, [])
                if frames:
                    # Advance to next frame
                    animation.frame_index += 1

                    # Loop or clamp
                    if animation.loop:
                        animation.frame_index %= len(frames)
                    else:
                        animation.frame_index = min(animation.frame_index, len(frames) - 1)

                    # Update sprite texture
                    sprite.texture = frames[animation.frame_index]
```

### Example 2: Collision Detection System

```python
from engine.core.ecs import System, World, Transform, Collider

class CollisionSystem(System):
    """Detect and resolve collisions."""

    def __init__(self):
        super().__init__()
        self.priority = 30

    def update(self, world: World, delta_time: float):
        # Get all entities with colliders
        collider_entities = world.get_entities_with_components(Transform, Collider)

        # Check all pairs (naive O(n²) approach - use spatial partitioning for better performance)
        for i, entity_a in enumerate(collider_entities):
            for entity_b in collider_entities[i+1:]:
                if self._check_collision(entity_a, entity_b):
                    self._handle_collision(entity_a, entity_b)

    def _check_collision(self, entity_a, entity_b):
        """AABB collision detection."""
        transform_a = entity_a.get_component(Transform)
        collider_a = entity_a.get_component(Collider)

        transform_b = entity_b.get_component(Transform)
        collider_b = entity_b.get_component(Collider)

        # Calculate bounding boxes
        left_a = transform_a.x + collider_a.offset_x - collider_a.width / 2
        right_a = left_a + collider_a.width
        top_a = transform_a.y + collider_a.offset_y - collider_a.height / 2
        bottom_a = top_a + collider_a.height

        left_b = transform_b.x + collider_b.offset_x - collider_b.width / 2
        right_b = left_b + collider_b.width
        top_b = transform_b.y + collider_b.offset_y - collider_b.height / 2
        bottom_b = top_b + collider_b.height

        # Check overlap
        return (left_a < right_b and right_a > left_b and
                top_a < bottom_b and bottom_a > top_b)

    def _handle_collision(self, entity_a, entity_b):
        """Handle collision response."""
        # Emit collision event
        EventManager.emit(Event(
            EventType.COLLISION_ENTER,
            {
                "entity_a": entity_a.id,
                "entity_b": entity_b.id
            }
        ))

        # Simple collision resolution (push apart)
        # ... implementation details
```

### Example 3: Quest System

```python
from engine.core.ecs import System, World
from engine.core.events import EventManager, Event, EventType

class QuestSystem(System):
    """Manage quest progression."""

    def __init__(self):
        super().__init__()
        self.priority = 40

        # Subscribe to game events
        EventManager.subscribe(EventType.ENTITY_DIED, self.on_entity_died)
        EventManager.subscribe(EventType.ITEM_COLLECTED, self.on_item_collected)

    def update(self, world: World, delta_time: float):
        # Check quest completion conditions
        for entity in world.get_entities_with_component(QuestProgress):
            quest_progress = entity.get_component(QuestProgress)

            for quest_id in list(quest_progress.active_quests):
                if self._is_quest_complete(quest_progress, quest_id):
                    quest_progress.complete_quest(quest_id)

                    # Emit quest completed event
                    EventManager.emit(Event(
                        EventType.QUEST_COMPLETED,
                        {"quest_id": quest_id, "entity_id": entity.id}
                    ))

    def on_entity_died(self, event: Event):
        """Update kill quests."""
        entity_id = event.data.get("entity_id")
        entity_type = event.data.get("entity_type", "unknown")

        # Update quest objectives for all players
        for entity in self.world.get_entities_with_component(QuestProgress):
            quest_progress = entity.get_component(QuestProgress)

            for quest_id, objectives in quest_progress.quest_objectives.items():
                # Check if quest has a "kill X enemies" objective
                objective_key = f"kill_{entity_type}"
                if objective_key in objectives:
                    objectives[objective_key] += 1

    def on_item_collected(self, event: Event):
        """Update collection quests."""
        item_type = event.data.get("item_type")
        collector_id = event.data.get("collector_id")

        entity = self.world.get_entity(collector_id)
        if entity and entity.has_component(QuestProgress):
            quest_progress = entity.get_component(QuestProgress)

            for quest_id, objectives in quest_progress.quest_objectives.items():
                objective_key = f"collect_{item_type}"
                if objective_key in objectives:
                    objectives[objective_key] += 1

    def _is_quest_complete(self, quest_progress, quest_id):
        """Check if all objectives are met."""
        objectives = quest_progress.quest_objectives.get(quest_id, {})

        # Load quest requirements (would come from data file)
        requirements = self._get_quest_requirements(quest_id)

        for objective, required in requirements.items():
            current = objectives.get(objective, 0)
            if current < required:
                return False

        return True

    def _get_quest_requirements(self, quest_id):
        """Load quest requirements from data."""
        # Placeholder - would load from JSON
        return {
            "kill_goblin": 10,
            "collect_gold": 100
        }
```

## System Lifecycle Hooks

Systems have optional lifecycle methods:

```python
class MySystem(System):
    """Example system with lifecycle hooks."""

    def __init__(self):
        super().__init__()
        self.priority = 10
        self.tracked_entities = []

    def on_entity_added(self, entity):
        """Called when an entity is added to the world."""
        # Cache entities with specific components
        if entity.has_component(MyComponent):
            self.tracked_entities.append(entity)

    def on_entity_removed(self, entity):
        """Called when an entity is removed from the world."""
        # Clean up cached references
        if entity in self.tracked_entities:
            self.tracked_entities.remove(entity)

    def update(self, world: World, delta_time: float):
        """Called every frame."""
        # Process tracked entities
        for entity in self.tracked_entities:
            # ... process entity
            pass
```

## Testing Systems

```python
import pytest
from engine.core.ecs import World, Transform
from scripts.systems import MovementSystem
from scripts.components import Velocity

def test_movement_system():
    """Test that MovementSystem updates entity positions."""
    # Setup
    world = World()
    system = MovementSystem()
    world.add_system(system)

    # Create entity
    entity = world.create_entity()
    entity.add_component(Transform(x=0, y=0))
    entity.add_component(Velocity(dx=100, dy=50))

    # Update for 1 second
    world.update(1.0)

    # Assert
    transform = entity.get_component(Transform)
    assert transform.x == 100.0
    assert transform.y == 50.0

def test_collision_system():
    """Test collision detection."""
    world = World()
    system = CollisionSystem()
    world.add_system(system)

    # Create two overlapping entities
    entity_a = world.create_entity()
    entity_a.add_component(Transform(x=0, y=0))
    entity_a.add_component(Collider(width=32, height=32))

    entity_b = world.create_entity()
    entity_b.add_component(Transform(x=16, y=16))  # Overlaps with entity_a
    entity_b.add_component(Collider(width=32, height=32))

    # Track collision events
    collision_detected = []

    def on_collision(event):
        collision_detected.append(event)

    EventManager.subscribe(EventType.COLLISION_ENTER, on_collision)

    # Update
    world.update(0.016)

    # Assert
    assert len(collision_detected) == 1
    assert collision_detected[0].data["entity_a"] in [entity_a.id, entity_b.id]
```

## Best Practices

### 1. Single Responsibility

Each system should do one thing well:

**Good** ✅:
```python
class MovementSystem(System):        # Handles movement
class CollisionSystem(System):       # Handles collisions
class AnimationSystem(System):       # Handles animations
```

**Bad** ❌:
```python
class GameplaySystem(System):        # Does everything!
    # Movement, collision, animation, AI, combat, etc.
```

### 2. Use Delta Time

Always scale movement/changes by `delta_time`:

**Good** ✅:
```python
transform.x += velocity.dx * delta_time  # Frame-rate independent
```

**Bad** ❌:
```python
transform.x += velocity.dx  # Depends on frame rate!
```

### 3. Query Efficiently

Cache queries when possible:

**Good** ✅:
```python
class RenderSystem(System):
    def update(self, world: World, delta_time: float):
        # Query once per frame
        entities = world.get_entities_with_components(Transform, Sprite)
        for entity in entities:
            self.render(entity)
```

**Bad** ❌:
```python
class RenderSystem(System):
    def update(self, world: World, delta_time: float):
        for entity in world.get_entities():
            # Querying for each entity is slow!
            if entity.has_components(Transform, Sprite):
                self.render(entity)
```

### 4. Avoid Tight Coupling

Use events for system-to-system communication:

**Good** ✅:
```python
# CombatSystem emits event
EventManager.emit(Event(EventType.ENTITY_DIED, {"entity_id": entity.id}))

# QuestSystem listens for event
EventManager.subscribe(EventType.ENTITY_DIED, self.on_entity_died)
```

**Bad** ❌:
```python
# CombatSystem directly calls QuestSystem
self.quest_system.on_entity_died(entity)  # Tight coupling!
```

### 5. Document System Behavior

```python
class AISystem(System):
    """
    AI behavior system for enemy entities.

    Manages AI state machines (IDLE, PATROL, CHASE, ATTACK) and
    transitions based on player distance. Requires Transform and
    AIController components.

    Priority: 10 (runs after input, before physics)

    Events Emitted:
    - AI_STATE_CHANGED: When AI state transitions
    - ENTITY_ATTACKED: When AI entity performs attack

    Events Listened:
    - None

    Performance: O(n) where n = number of AI entities
    """
```

## Common Pitfalls

### Pitfall 1: Storing Stale Entity References

**Problem**:
```python
class MySystem(System):
    def __init__(self):
        super().__init__()
        self.player = None  # Stale reference!

    def update(self, world: World, delta_time: float):
        if not self.player:
            self.player = world.get_entities_with_tag("player")[0]

        # What if player entity was removed?
        transform = self.player.get_component(Transform)  # Crash!
```

**Solution**:
```python
class MySystem(System):
    def update(self, world: World, delta_time: float):
        # Query every frame (it's fast with indexing)
        players = world.get_entities_with_tag("player")
        if not players:
            return

        player = players[0]
        transform = player.get_component(Transform)  # Safe
```

### Pitfall 2: Modifying Queries During Iteration

**Problem**:
```python
def update(self, world: World, delta_time: float):
    for entity in world.get_entities_with_component(Health):
        health = entity.get_component(Health)
        if health.current <= 0:
            world.remove_entity(entity.id)  # Modifying during iteration!
```

**Solution**:
```python
def update(self, world: World, delta_time: float):
    to_remove = []

    for entity in world.get_entities_with_component(Health):
        health = entity.get_component(Health)
        if health.current <= 0:
            to_remove.append(entity.id)

    # Remove after iteration
    for entity_id in to_remove:
        world.remove_entity(entity_id)
```

### Pitfall 3: Frame-Rate Dependent Logic

**Problem**:
```python
def update(self, world: World, delta_time: float):
    velocity.dx += 5  # Adds 5 every frame (300 at 60fps, 150 at 30fps!)
```

**Solution**:
```python
def update(self, world: World, delta_time: float):
    velocity.dx += 500 * delta_time  # Adds 500 per second (consistent)
```

## Next Steps

- [API Reference](api_reference.md) - Complete System API
- [Creating Components](creating_components.md) - Build components for your systems
- [Example: Simple RPG](../examples/simple_rpg/README.md) - See complete systems in action
- [Project Configuration](project_configuration.md) - Configure which systems to enable
