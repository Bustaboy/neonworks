# Common Pitfalls in NeonWorks

Learn from these common mistakes to save time and frustration. This guide covers frequent issues developers encounter and how to avoid them.

## Table of Contents
- [Entity Component System Pitfalls](#entity-component-system-pitfalls)
- [Performance Pitfalls](#performance-pitfalls)
- [Event System Pitfalls](#event-system-pitfalls)
- [Rendering Pitfalls](#rendering-pitfalls)
- [Physics Pitfalls](#physics-pitfalls)
- [Data Management Pitfalls](#data-management-pitfalls)
- [Architecture Pitfalls](#architecture-pitfalls)

---

## Entity Component System Pitfalls

### ❌ Pitfall #1: Storing Logic in Components

**Bad:**
```python
@dataclass
class Enemy(Component):
    health: int = 100

    def take_damage(self, amount: int):
        self.health -= amount
        if self.health <= 0:
            self.die()
```

**Why it's bad:** Components should be pure data. Adding methods breaks the ECS pattern and makes the code harder to test and maintain.

**Good:**
```python
@dataclass
class Enemy(Component):
    health: int = 100
    max_health: int = 100

class EnemySystem(System):
    def apply_damage(self, entity: Entity, amount: int):
        enemy = entity.get_component(Enemy)
        enemy.health -= amount
        if enemy.health <= 0:
            self.handle_death(entity)
```

**Why it's good:** Logic lives in Systems where it can be tested, disabled, and reordered easily.

---

### ❌ Pitfall #2: Not Checking if Components Exist

**Bad:**
```python
def update(self, world: World, delta_time: float):
    for entity in world.get_entities():
        transform = entity.get_component(Transform)
        transform.x += 10  # CRASH if entity has no Transform!
```

**Why it's bad:** `get_component()` returns `None` if the component doesn't exist, causing AttributeError.

**Good:**
```python
def update(self, world: World, delta_time: float):
    # Option 1: Query for entities with required components
    for entity in world.get_entities_with_components(Transform, Velocity):
        transform = entity.get_component(Transform)
        velocity = entity.get_component(Velocity)
        transform.x += velocity.x * delta_time

    # Option 2: Check before accessing
    for entity in world.get_entities():
        transform = entity.get_component(Transform)
        if transform:
            transform.x += 10
```

**Why it's good:** Prevents crashes and processes only relevant entities efficiently.

---

### ❌ Pitfall #3: Modifying Entity Components During Iteration

**Bad:**
```python
def update(self, world: World, delta_time: float):
    for entity in world.get_entities_with_component(Bullet):
        if should_explode(entity):
            world.remove_entity(entity.id)  # Modifies collection during iteration!
```

**Why it's bad:** Modifying a collection while iterating over it can cause crashes or skip entities.

**Good:**
```python
def update(self, world: World, delta_time: float):
    entities_to_remove = []

    for entity in world.get_entities_with_component(Bullet):
        if should_explode(entity):
            entities_to_remove.append(entity.id)

    for entity_id in entities_to_remove:
        world.remove_entity(entity_id)
```

**Why it's good:** Collects operations first, applies them after iteration completes.

---

### ❌ Pitfall #4: Forgetting to Add Systems to World

**Bad:**
```python
# Creating system but never adding it
movement_system = MovementSystem()

# Game loop runs but nothing happens!
world.update(delta_time)
```

**Why it's bad:** Systems must be added to the World to execute.

**Good:**
```python
movement_system = MovementSystem()
world.add_system(movement_system)  # Don't forget this!

world.update(delta_time)
```

**Why it's good:** System will now execute during world updates.

---

### ❌ Pitfall #5: Creating Too Many Small Components

**Bad:**
```python
@dataclass
class PositionX(Component):
    x: float = 0.0

@dataclass
class PositionY(Component):
    y: float = 0.0

@dataclass
class Rotation(Component):
    rotation: float = 0.0
```

**Why it's bad:** Excessive granularity makes queries complex and hurts performance. You'll need to query for 3 components instead of 1.

**Good:**
```python
@dataclass
class Transform(Component):
    x: float = 0.0
    y: float = 0.0
    rotation: float = 0.0
    scale_x: float = 1.0
    scale_y: float = 1.0
```

**Why it's good:** Groups related data logically. Easier to query and manage.

---

## Performance Pitfalls

### ❌ Pitfall #6: Not Using delta_time

**Bad:**
```python
def update(self, world: World, delta_time: float):
    for entity in world.get_entities_with_component(Transform):
        transform = entity.get_component(Transform)
        transform.x += 5  # Moves 5 pixels per frame - frame-dependent!
```

**Why it's bad:** Movement speed depends on frame rate. 60 FPS = 300 pixels/sec, 30 FPS = 150 pixels/sec.

**Good:**
```python
def update(self, world: World, delta_time: float):
    for entity in world.get_entities_with_components(Transform, Velocity):
        transform = entity.get_component(Transform)
        velocity = entity.get_component(Velocity)
        transform.x += velocity.x * delta_time  # Frame-independent!
```

**Why it's good:** Consistent behavior regardless of frame rate.

---

### ❌ Pitfall #7: Calling get_component() Repeatedly

**Bad:**
```python
def update(self, world: World, delta_time: float):
    for entity in world.get_entities():
        if entity.get_component(Transform):  # Call 1
            x = entity.get_component(Transform).x  # Call 2
            y = entity.get_component(Transform).y  # Call 3
            # Do something with x, y
```

**Why it's bad:** Dictionary lookups on every access. Wasteful in hot loops.

**Good:**
```python
def update(self, world: World, delta_time: float):
    for entity in world.get_entities_with_component(Transform):
        transform = entity.get_component(Transform)  # Call once
        x = transform.x
        y = transform.y
        # Do something with x, y
```

**Why it's good:** Cache the component reference. Much faster.

---

### ❌ Pitfall #8: Creating/Destroying Entities Every Frame

**Bad:**
```python
def update(self, world: World, delta_time: float):
    # Spawn particles
    for i in range(100):
        particle = world.create_entity()  # Allocates memory
        particle.add_component(Particle(lifetime=1.0))

    # Remove dead particles
    for entity in world.get_entities_with_component(Particle):
        particle = entity.get_component(Particle)
        if particle.lifetime <= 0:
            world.remove_entity(entity.id)  # Deallocates memory
```

**Why it's bad:** Constant allocation/deallocation causes garbage collection pauses and fragmentation.

**Good:**
```python
class ParticlePoolSystem(System):
    def __init__(self):
        self.particle_pool = []  # Reusable entities

    def spawn_particle(self, world: World, x: float, y: float):
        # Reuse inactive particle
        for entity in self.particle_pool:
            particle = entity.get_component(Particle)
            if not particle.active:
                particle.active = True
                particle.lifetime = 1.0
                transform = entity.get_component(Transform)
                transform.x = x
                transform.y = y
                return entity

        # Create new one if pool empty
        entity = world.create_entity()
        entity.add_component(Transform(x=x, y=y))
        entity.add_component(Particle(lifetime=1.0, active=True))
        self.particle_pool.append(entity)
        return entity

    def update(self, world: World, delta_time: float):
        for entity in self.particle_pool:
            particle = entity.get_component(Particle)
            if particle.active:
                particle.lifetime -= delta_time
                if particle.lifetime <= 0:
                    particle.active = False  # Deactivate, don't destroy
```

**Why it's good:** Object pooling eliminates allocation overhead. Huge performance gain for particles, bullets, etc.

---

### ❌ Pitfall #9: No Spatial Partitioning for Collision Detection

**Bad:**
```python
def update(self, world: World, delta_time: float):
    entities = world.get_entities_with_component(Collider)
    # O(n²) complexity - checks every pair!
    for i, entity_a in enumerate(entities):
        for entity_b in entities[i+1:]:
            if check_collision(entity_a, entity_b):
                handle_collision(entity_a, entity_b)
```

**Why it's bad:** 1000 entities = 500,000 collision checks per frame. Extremely slow.

**Good:**
```python
class SpatialHashGrid:
    def __init__(self, cell_size: int = 64):
        self.cell_size = cell_size
        self.grid = {}

    def insert(self, entity: Entity):
        transform = entity.get_component(Transform)
        cell_x = int(transform.x // self.cell_size)
        cell_y = int(transform.y // self.cell_size)

        if (cell_x, cell_y) not in self.grid:
            self.grid[(cell_x, cell_y)] = []
        self.grid[(cell_x, cell_y)].append(entity)

    def get_nearby(self, entity: Entity):
        transform = entity.get_component(Transform)
        cell_x = int(transform.x // self.cell_size)
        cell_y = int(transform.y // self.cell_size)

        nearby = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                cell = (cell_x + dx, cell_y + dy)
                if cell in self.grid:
                    nearby.extend(self.grid[cell])
        return nearby

class CollisionSystem(System):
    def __init__(self):
        self.spatial_grid = SpatialHashGrid()

    def update(self, world: World, delta_time: float):
        # Rebuild grid each frame
        self.spatial_grid.grid.clear()
        for entity in world.get_entities_with_component(Collider):
            self.spatial_grid.insert(entity)

        # Only check nearby entities
        for entity in world.get_entities_with_component(Collider):
            for other in self.spatial_grid.get_nearby(entity):
                if entity.id != other.id:
                    if check_collision(entity, other):
                        handle_collision(entity, other)
```

**Why it's good:** Only checks entities in nearby grid cells. 1000 entities might only check ~10 neighbors each = 10,000 checks instead of 500,000!

---

## Event System Pitfalls

### ❌ Pitfall #10: Not Processing Events

**Bad:**
```python
def game_loop():
    while running:
        # Update systems
        world.update(delta_time)

        # Events are emitted but never processed!
        # Event handlers never get called

        render()
```

**Why it's bad:** Events queue up but handlers never execute.

**Good:**
```python
def game_loop():
    event_manager = get_event_manager()

    while running:
        # Update systems (may emit events)
        world.update(delta_time)

        # Process queued events
        event_manager.process_events()

        render()
```

**Why it's good:** Events are dispatched to handlers each frame.

---

### ❌ Pitfall #11: Creating Circular Event Dependencies

**Bad:**
```python
def on_damage(event):
    # Taking damage causes healing?
    emit_event(EventType.HEAL, {"amount": 5})

def on_heal(event):
    # Healing causes damage?
    emit_event(EventType.DAMAGE_DEALT, {"amount": 10})

# Subscribe both
event_manager.subscribe(EventType.DAMAGE_DEALT, on_damage)
event_manager.subscribe(EventType.HEAL, on_heal)

# Emit damage -> Infinite loop!
emit_event(EventType.DAMAGE_DEALT, {"amount": 50})
```

**Why it's bad:** Circular event chains cause infinite loops or stack overflow.

**Good:**
```python
def on_damage(event):
    entity_id = event.data["entity_id"]
    entity = world.get_entity(entity_id)
    health = entity.get_component(Health)
    health.current -= event.data["amount"]
    # Don't emit more events - handle it directly

def on_heal(event):
    entity_id = event.data["entity_id"]
    entity = world.get_entity(entity_id)
    health = entity.get_component(Health)
    health.current = min(health.current + event.data["amount"], health.maximum)
    # Don't emit more events
```

**Why it's good:** Events trigger final actions, not more events. Clear data flow.

---

### ❌ Pitfall #12: Storing Entity References in Event Data

**Bad:**
```python
emit_event(EventType.UNIT_DIED, {"entity": entity})  # Stores object reference!
```

**Why it's bad:** If the entity is destroyed before event processing, you have a dangling reference. Also makes serialization impossible.

**Good:**
```python
emit_event(EventType.UNIT_DIED, {"entity_id": entity.id})  # Store ID

def on_unit_died(event):
    entity_id = event.data["entity_id"]
    entity = world.get_entity(entity_id)
    if entity:  # Check if still exists
        # Handle death
```

**Why it's good:** Store entity IDs, not references. Safely handle destroyed entities.

---

## Rendering Pitfalls

### ❌ Pitfall #13: Not Culling Off-Screen Entities

**Bad:**
```python
def render(self, world: World, screen):
    # Render ALL entities, even off-screen ones
    for entity in world.get_entities_with_components(Transform, Sprite):
        transform = entity.get_component(Transform)
        sprite = entity.get_component(Sprite)
        self.draw_sprite(screen, sprite, transform.x, transform.y)
```

**Why it's bad:** Wastes time rendering entities the player can't see.

**Good:**
```python
def render(self, world: World, screen, camera):
    camera_rect = camera.get_viewport()

    for entity in world.get_entities_with_components(Transform, Sprite):
        transform = entity.get_component(Transform)
        sprite = entity.get_component(Sprite)

        # Check if entity is in camera view
        entity_rect = pygame.Rect(transform.x, transform.y, sprite.width, sprite.height)
        if camera_rect.colliderect(entity_rect):
            screen_x = transform.x - camera.x
            screen_y = transform.y - camera.y
            self.draw_sprite(screen, sprite, screen_x, screen_y)
```

**Why it's good:** Only renders visible entities. Huge performance boost for large levels.

---

### ❌ Pitfall #14: Loading Textures Every Frame

**Bad:**
```python
def render_sprite(self, screen, sprite, x, y):
    # Loading from disk every frame!
    texture = pygame.image.load(sprite.texture)
    screen.blit(texture, (x, y))
```

**Why it's bad:** Disk I/O every frame = 1-2 FPS instead of 60 FPS.

**Good:**
```python
class TextureCache:
    def __init__(self):
        self._cache = {}

    def get(self, path: str):
        if path not in self._cache:
            self._cache[path] = pygame.image.load(path)
        return self._cache[path]

texture_cache = TextureCache()

def render_sprite(self, screen, sprite, x, y):
    texture = texture_cache.get(sprite.texture)  # Cached!
    screen.blit(texture, (x, y))
```

**Why it's good:** Load once, reuse forever. Essential for performance.

---

## Physics Pitfalls

### ❌ Pitfall #15: Tunneling (Fast Objects Passing Through Walls)

**Bad:**
```python
# Bullet moving at 1000 pixels/sec
# Wall is 10 pixels thick
# At 60 FPS: bullet moves 16.6 pixels per frame
# Bullet teleports through wall!
```

**Why it's bad:** Discrete collision detection checks position each frame. Fast objects skip over thin obstacles.

**Good:**
```python
class BulletSystem(System):
    def update(self, world: World, delta_time: float):
        for entity in world.get_entities_with_components(Bullet, Transform, Velocity):
            transform = entity.get_component(Transform)
            velocity = entity.get_component(Velocity)

            # Raycast from current position to next position
            start = (transform.x, transform.y)
            end = (transform.x + velocity.x * delta_time,
                   transform.y + velocity.y * delta_time)

            hit = self.raycast(world, start, end)
            if hit:
                self.handle_bullet_hit(entity, hit)
            else:
                transform.x = end[0]
                transform.y = end[1]
```

**Why it's good:** Continuous collision detection catches fast-moving objects.

---

## Data Management Pitfalls

### ❌ Pitfall #16: Not Using Dataclasses for Components

**Bad:**
```python
class Health(Component):
    def __init__(self, current=100, maximum=100):
        self.current = current
        self.maximum = maximum
```

**Why it's bad:** More boilerplate, no type hints, harder to serialize.

**Good:**
```python
from dataclasses import dataclass

@dataclass
class Health(Component):
    current: float = 100.0
    maximum: float = 100.0
```

**Why it's good:** Less code, type safety, automatic `__repr__`, works with serialization.

---

### ❌ Pitfall #17: Mutable Default Arguments

**Bad:**
```python
@dataclass
class Inventory(Component):
    items: list = []  # DANGER! Shared between ALL instances!
```

**Why it's bad:** All Inventory components share the same list. Adding item to one adds to all!

**Good:**
```python
from dataclasses import dataclass, field

@dataclass
class Inventory(Component):
    items: list = field(default_factory=list)  # Each instance gets new list
```

**Why it's good:** Each component has its own list.

---

## Architecture Pitfalls

### ❌ Pitfall #18: Systems Depending on Execution Order

**Bad:**
```python
class MovementSystem(System):
    def update(self, world, dt):
        # Reads velocity, updates position
        pass

class PhysicsSystem(System):
    def update(self, world, dt):
        # Updates velocity based on forces
        pass

# If PhysicsSystem runs after MovementSystem,
# velocity changes won't apply until next frame!
```

**Why it's bad:** Implicit dependencies on system order lead to bugs and lag.

**Good:**
```python
class PhysicsSystem(System):
    def __init__(self):
        super().__init__()
        self.priority = 10  # Runs first

class MovementSystem(System):
    def __init__(self):
        super().__init__()
        self.priority = 20  # Runs after physics

# Or make dependencies explicit in documentation
```

**Why it's good:** Explicit priorities make execution order clear and predictable.

---

### ❌ Pitfall #19: Global State Instead of Components

**Bad:**
```python
# Global variables
player_health = 100
player_position = (0, 0)
enemy_count = 5

def update_game():
    global player_health, player_position
    # Modify globals
```

**Why it's bad:** Hard to save/load, can't have multiple instances, not testable, breaks ECS.

**Good:**
```python
# Everything is an entity/component
player = world.create_entity()
player.add_component(Health(current=100))
player.add_component(Transform(x=0, y=0))
player.add_tag("player")

# Game state is just querying the world
enemies = world.get_entities_with_tag("enemy")
enemy_count = len(enemies)
```

**Why it's good:** Follows ECS, easily serializable, testable, flexible.

---

### ❌ Pitfall #20: Overusing Tags

**Bad:**
```python
entity.add_tag("enemy")
entity.add_tag("flying")
entity.add_tag("boss")
entity.add_tag("fire_type")
entity.add_tag("phase_2")
entity.add_tag("can_teleport")
# ... 20 more tags
```

**Why it's bad:** Tags are for broad categories. Too many tags = should be components with data.

**Good:**
```python
# Use tags for broad categories
entity.add_tag("enemy")
entity.add_tag("boss")

# Use components for properties with data
entity.add_component(Flying(altitude=100, speed=50))
entity.add_component(ElementalType(element="fire", resistance=0.8))
entity.add_component(BossPhase(current_phase=2, total_phases=3))
entity.add_component(TeleportAbility(cooldown=5.0, range=200))
```

**Why it's good:** Tags for queries, components for data. Clear separation.

---

## Summary: Best Practices

✅ **DO:**
- Keep components as pure data
- Check components exist before accessing
- Use `delta_time` for time-based calculations
- Cache component references in hot loops
- Use object pooling for frequently created/destroyed entities
- Process events in your game loop
- Use spatial partitioning for collision detection
- Cull off-screen entities before rendering
- Cache loaded assets
- Use `field(default_factory=...)` for mutable defaults
- Set system priorities explicitly
- Store entity IDs, not references

❌ **DON'T:**
- Add methods to components
- Modify collections during iteration
- Create circular event dependencies
- Load assets every frame
- Use discrete collision for fast-moving objects
- Rely on implicit system execution order
- Use global variables for game state
- Overuse tags instead of components

Following these practices will save you hours of debugging and help you build performant, maintainable games with NeonWorks!
