# NeonWorks Performance Optimization Guide

**Version:** 1.0.0
**Last Updated:** 2025-11-15
**Engine Version:** 0.1.0

---

## Table of Contents

1. [Overview](#overview)
2. [Performance Baseline](#performance-baseline)
3. [Monitoring Performance](#monitoring-performance)
4. [Optimization Best Practices](#optimization-best-practices)
5. [System-Specific Optimizations](#system-specific-optimizations)
6. [Profiling Tools](#profiling-tools)
7. [Common Performance Pitfalls](#common-performance-pitfalls)
8. [Troubleshooting](#troubleshooting)

---

## Overview

NeonWorks is designed for high performance out of the box. Baseline testing shows:

- **Rendering:** 385 FPS with 1,000 entities (6.4x target)
- **Database:** 5.75ms load time for 0.65MB files (173x faster than target)
- **Event System:** <1ms dispatch time for 100 handlers

**In most cases, no optimization is needed.** This guide covers monitoring performance and optimizing edge cases.

---

## Performance Baseline

### Rendering System
- **Target:** 60 FPS
- **Actual:** 385.1 FPS (1,000 entities)
- **Bottleneck Threshold:** >10,000 entities
- **Frame Budget:** ~16.67ms per frame

**Frame Time Breakdown:**
- `render_world`: ~2ms (90% of frame time)
- `clear`: ~0.2ms
- `display_flip`: <0.01ms

### Database System
- **Target:** <1000ms load time
- **Actual:** 5.75ms (0.65MB database)
- **Bottleneck Threshold:** >100MB databases
- **Operations:**
  - Load: ~6ms
  - Save: ~29ms
  - Query: <0.1ms

### Event System
- **Target:** Minimal overhead
- **Actual:** ~0.005ms per event with 100 handlers
- **Bottleneck Threshold:** >1,000 handlers per event
- **Scaling:** Linear with handler count

---

## Monitoring Performance

### Using the Performance Monitor

```python
from neonworks.utils import enable_performance_monitoring, get_performance_monitor

# Enable monitoring (call once at startup)
enable_performance_monitoring(target_fps=60.0, enable_warnings=True)

# In your game loop
monitor = get_performance_monitor()

# Wrap frame updates
monitor.begin_frame()

monitor.begin_update()
# ... update code ...
monitor.end_update()

monitor.begin_render()
# ... rendering code ...
monitor.end_render()

monitor.end_frame()

# Print stats periodically
if frame_count % 600 == 0:  # Every 10 seconds at 60 FPS
    monitor.print_stats()
```

### Tracking Custom Metrics

```python
from neonworks.utils import measure

# Profile specific functions
with measure("ai_pathfinding"):
    path = pathfinder.find_path(start, end)

# Get results
profiler = get_profiler()
profiler.print_report()
```

### Saving Performance Logs

```python
from pathlib import Path

monitor = get_performance_monitor()
monitor.save_log(Path("logs/performance.log"))
```

---

## Optimization Best Practices

### 1. Entity Management

**DO:**
```python
# Remove inactive entities
if not entity.active:
    world.remove_entity(entity)

# Use tags for quick filtering
entity.add_tag("enemy")
enemies = world.get_entities_with_tag("enemy")

# Batch entity operations
for entity in world.get_entities_with_component(Transform):
    # Process all transforms together
    pass
```

**DON'T:**
```python
# Don't iterate all entities every frame
for entity in world.entities:  # Slow for >1000 entities
    if entity.has_component(Enemy):
        process(entity)

# Don't create entities in hot loops
while True:
    entity = world.create_entity()  # Memory churn
```

### 2. Rendering Optimization

**DO:**
```python
# Use sprite batching (automatic in NeonWorks)
renderer.render_world(world)

# Cull off-screen entities
if not camera.is_visible(entity_position):
    continue

# Use appropriate layer counts (3-5 layers recommended)
entity.add_component(GridPosition(grid_x=x, grid_y=y, layer=0))
```

**DON'T:**
```python
# Don't render hidden entities
sprite.visible = False  # Good - skipped automatically

# Don't reload textures every frame
texture = asset_manager.load("sprite.png")  # Cached automatically

# Don't use >10 layers
GridPosition(grid_x=x, grid_y=y, layer=15)  # Excessive
```

### 3. Event System Best Practices

**DO:**
```python
# Subscribe once, use many times
event_manager.subscribe(EventType.DAMAGE_DEALT, on_damage)

# Use queued events for non-critical notifications
event_manager.emit(Event(EventType.COIN_COLLECTED, data={...}))
event_manager.process_events()  # Process in batch

# Limit handler count per event (<100 recommended)
```

**DON'T:**
```python
# Don't subscribe/unsubscribe frequently
def update():
    event_manager.subscribe(EventType.DAMAGE, handler)  # BAD
    event_manager.unsubscribe(EventType.DAMAGE, handler)  # BAD

# Don't emit events in tight loops
for i in range(10000):
    event_manager.emit(Event(...))  # Consider batching
```

### 4. Database Loading

**DO:**
```python
# Load databases at startup
config = ConfigLoader.load("config/items.json")

# Cache frequently accessed data
item_cache = {item["id"]: item for item in config["items"]}

# Use lazy loading for large assets
def get_item(item_id):
    if item_id not in cache:
        cache[item_id] = load_item(item_id)
    return cache[item_id]
```

**DON'T:**
```python
# Don't load files every frame
def update():
    config = ConfigLoader.load("config.json")  # VERY BAD

# Don't load entire databases for single items
all_items = load_all_items()
single_item = all_items[0]  # Wasteful
```

### 5. Memory Management

**DO:**
```python
# Reuse objects when possible
particle_pool = [Particle() for _ in range(100)]

# Clear unused assets
asset_manager.clear_unused()

# Track memory usage
monitor = get_performance_monitor()
stats = monitor.get_stats()
print(f"Memory: {stats.memory_used_mb:.1f} MB")
```

**DON'T:**
```python
# Don't create garbage in hot paths
def update():
    temp_list = []  # Creates garbage every frame
    temp_dict = {}  # Creates garbage every frame
```

---

## System-Specific Optimizations

### Rendering System

#### Spatial Culling
```python
# Only render entities in camera view
camera = renderer.camera
visible_entities = []

for entity in world.get_entities_with_component(Transform):
    pos = entity.get_component(Transform)
    if camera.is_point_visible(pos.x, pos.y):
        visible_entities.append(entity)

# Render only visible entities
for entity in visible_entities:
    renderer.render_entity(entity)
```

#### Layer Optimization
```python
# Use layers strategically:
# Layer 0: Ground tiles
# Layer 1: Objects and buildings
# Layer 2: Characters
# Layer 3: Effects
# Layer 4: UI overlays

entity.add_component(GridPosition(grid_x=x, grid_y=y, layer=1))
```

### ECS Query Optimization

```python
# Cache component queries
class MySystem(System):
    def __init__(self):
        self._cached_entities = []
        self._cache_dirty = True

    def update(self, dt, world):
        if self._cache_dirty:
            self._cached_entities = world.get_entities_with_component(Transform)
            self._cache_dirty = False

        for entity in self._cached_entities:
            # Process entities
            pass

    def mark_dirty(self):
        self._cache_dirty = True
```

### Pathfinding Optimization

```python
# Limit pathfinding frequency
class PathfindingCache:
    def __init__(self, cache_time=1.0):
        self.cache = {}
        self.cache_time = cache_time

    def get_path(self, start, end, current_time):
        cache_key = (start, end)

        if cache_key in self.cache:
            cached_path, timestamp = self.cache[cache_key]
            if current_time - timestamp < self.cache_time:
                return cached_path

        # Calculate new path
        path = pathfinder.find_path(start, end)
        self.cache[cache_key] = (path, current_time)
        return path
```

---

## Profiling Tools

### Built-in Profiler

```python
from neonworks.utils import PerformanceProfiler

profiler = PerformanceProfiler()

# Profile rendering
with profiler.measure("render_frame"):
    renderer.render_world(world)

# Profile function with decorator
@profiler.profile("calculate_damage")
def calculate_damage(attacker, defender):
    # ... damage calculation ...
    return damage

# Get results
profiler.print_report()
profiler.save_report("reports/profile.txt")
```

### Using cProfile

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Code to profile
game.run()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

### Profiling Scripts

NeonWorks includes profiling scripts in `scripts/`:

```bash
# Profile rendering
python scripts/profile_rendering.py

# Profile database operations
python scripts/profile_database.py

# Profile event system
python scripts/profile_events.py

# Run all profilers
python scripts/profile_all.py
```

---

## Common Performance Pitfalls

### 1. Unnecessary String Operations

**BAD:**
```python
# String concatenation in loops
result = ""
for i in range(10000):
    result += str(i)  # Creates new string every iteration
```

**GOOD:**
```python
# Use list join
parts = [str(i) for i in range(10000)]
result = "".join(parts)
```

### 2. Expensive Operations in Update Loop

**BAD:**
```python
def update(self, dt):
    # Recalculating every frame
    distance = ((player.x - enemy.x)**2 + (player.y - enemy.y)**2)**0.5

    # Sorting every frame
    entities.sort(key=lambda e: e.priority)

    # Loading files every frame
    config = load_config("settings.json")
```

**GOOD:**
```python
def update(self, dt):
    # Cache calculations
    if self._distance_dirty:
        self._distance = self._calculate_distance()
        self._distance_dirty = False

    # Sort only when needed
    if self._entities_changed:
        entities.sort(key=lambda e: e.priority)
        self._entities_changed = False

    # Load once
    if not hasattr(self, 'config'):
        self.config = load_config("settings.json")
```

### 3. Inefficient Collision Detection

**BAD:**
```python
# O(n²) collision check
for entity1 in entities:
    for entity2 in entities:
        if check_collision(entity1, entity2):
            handle_collision(entity1, entity2)
```

**GOOD:**
```python
# Use spatial partitioning (quadtree, grid)
grid = SpatialGrid(cell_size=64)

for entity in entities:
    grid.insert(entity)

for entity in entities:
    nearby = grid.get_nearby(entity)
    for other in nearby:
        if check_collision(entity, other):
            handle_collision(entity, other)
```

### 4. Memory Leaks

**BAD:**
```python
# Not clearing event handlers
class Enemy:
    def __init__(self):
        event_manager.subscribe(EventType.DAMAGE, self.on_damage)

    # Missing cleanup - handlers remain subscribed!
```

**GOOD:**
```python
class Enemy:
    def __init__(self):
        event_manager.subscribe(EventType.DAMAGE, self.on_damage)

    def destroy(self):
        event_manager.unsubscribe(EventType.DAMAGE, self.on_damage)
```

---

## Troubleshooting

### Low FPS (<60 FPS)

**Diagnosis:**
```python
monitor = get_performance_monitor()
stats = monitor.get_stats()

print(f"FPS: {stats.avg_fps}")
print(f"Update Time: {stats.avg_update_time_ms}ms")
print(f"Render Time: {stats.avg_render_time_ms}ms")
print(f"Entity Count: {stats.entity_count}")
```

**Solutions:**
1. **If render time is high (>10ms):**
   - Reduce entity count
   - Enable frustum culling
   - Reduce layer count
   - Profile with `scripts/profile_rendering.py`

2. **If update time is high (>10ms):**
   - Profile systems with `PerformanceProfiler`
   - Optimize pathfinding (reduce frequency, cache results)
   - Reduce entity updates per frame

3. **If both are normal:**
   - Check event processing time
   - Profile with `scripts/profile_events.py`

### High Memory Usage

**Diagnosis:**
```python
stats = monitor.get_stats()
print(f"Memory: {stats.memory_used_mb:.1f} MB ({stats.memory_percent:.1f}%)")
```

**Solutions:**
1. Clear unused assets: `asset_manager.clear_unused()`
2. Remove inactive entities: `world.remove_entity(entity)`
3. Unsubscribe unused event handlers
4. Profile memory with `memory_profiler`

### Stuttering / Frame Time Variance

**Diagnosis:**
```python
stats = monitor.get_stats()
print(f"Frame Time Variance: {stats.frame_time_variance:.2f}ms")
print(f"Dropped Frames: {stats.dropped_frames}")
```

**Solutions:**
1. Avoid loading files during gameplay
2. Pre-cache assets at level start
3. Limit garbage collection (use object pools)
4. Spread expensive operations across frames

### Slow Database Loads

**Diagnosis:**
```python
from neonworks.utils import measure

with measure("database_load"):
    config = ConfigLoader.load("large_database.json")

profiler = get_profiler()
profiler.print_report()
```

**Solutions:**
1. Split large databases into smaller files
2. Use lazy loading for optional content
3. Cache loaded data
4. Consider binary formats for >10MB databases

---

## Performance Checklist

### Before Release

- [ ] Profile all major features
- [ ] Test with maximum expected entity count
- [ ] Verify FPS ≥60 on target hardware
- [ ] Check memory usage under normal gameplay
- [ ] Test database load times
- [ ] Verify no memory leaks over extended play
- [ ] Profile on lowest-spec target hardware
- [ ] Test with maximum UI elements visible
- [ ] Verify save/load performance
- [ ] Check asset loading times

### During Development

- [ ] Enable performance monitoring in debug builds
- [ ] Review performance stats every session
- [ ] Profile before optimizing (measure first!)
- [ ] Use profiling scripts regularly
- [ ] Monitor frame time variance
- [ ] Track entity and event counts
- [ ] Review memory usage trends

---

## Additional Resources

- **Baseline Report:** `reports/PERFORMANCE_BASELINE.md`
- **Profiling Scripts:** `scripts/profile_*.py`
- **Performance Monitor:** `utils/performance_monitor.py`
- **Profiler Utilities:** `utils/profiler.py`

---

## Contact

For performance-related questions or issues:
- Check STATUS.md for known performance issues
- Submit issues at https://github.com/Bustaboy/neonworks/issues
- Review DEVELOPER_GUIDE.md for best practices
