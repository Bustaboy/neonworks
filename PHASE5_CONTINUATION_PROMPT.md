# Neon Collapse Game Engine - Phase 5 Continuation Prompt

## Context
This is a continuation prompt for completing the Neon Collapse custom game engine implementation.

**Current Status:**
- **Branch:** `claude/custom-game-engine-011CV4ZDMtMd4GbDDVGcyooq`
- **Total Tests:** 566 passing
- **Last Commit:** `feat(phase5.1): Add navigation and pathfinding system`

## Completed Phases

### Phase 1-3: Core Engine (Completed Previously)
- ✅ ECS Architecture (World, Entity, Component, System)
- ✅ Rendering System (Sprites, Particles, UI)
- ✅ Audio System (Spatial audio, music, sound effects)
- ✅ Animation System (State machines, tweening)
- ✅ Scene Management (Transitions, stack-based)
- ✅ Serialization (Save/load game state)

### Phase 4: Game Systems (Completed)
- ✅ **4.1:** Collision Detection (38 tests)
  - AABB, Circle, Point colliders
  - QuadTree spatial partitioning
  - Layer masking
  - Collision callbacks (enter, stay, exit)

- ✅ **4.2:** Rigid Body Physics (32 tests)
  - Forces, velocity, acceleration
  - Mass, drag, gravity
  - Collision response with restitution
  - Static, kinematic, dynamic bodies
  - Position freeze constraints

- ✅ **4.3:** Input Management (22 tests)
  - Keyboard and mouse input
  - Action mapping (rebindable controls)
  - Axis input
  - Text input mode

- ✅ **4.4:** Game Loop & Timing (15 tests)
  - Fixed timestep update (1/60s)
  - Variable render rate
  - FPS tracking
  - Performance stats

### Phase 5: Advanced Systems (Partially Complete)
- ✅ **5.1:** Navigation & Pathfinding (41 tests)
  - A* pathfinding algorithm
  - NavigationGrid with costs
  - Multiple heuristics (Manhattan, Euclidean, Diagonal, Chebyshev)
  - Path smoothing
  - PathfindingSystem with caching

## Tasks to Complete

### Phase 5.2: AI System (Behavior Trees & Steering)

**Behavior Tree System:**
```python
# Required components:
- BehaviorNode (base class)
- Status enum (SUCCESS, FAILURE, RUNNING)
- Blackboard (shared state dictionary)

# Composite Nodes:
- Sequence (execute children until one fails)
- Selector (execute children until one succeeds)
- Parallel (execute all children simultaneously)

# Decorator Nodes:
- Inverter (invert child result)
- Repeater (repeat child N times or until failure)
- SuccessDecorator (always return success)
- FailureDecorator (always return failure)
- UntilSuccess (repeat until success)
- Limiter (limit executions per period)

# Leaf Nodes:
- Action (executable action node)
- Condition (boolean check node)
- Wait (delay node)

# Example usage:
tree = Sequence([
    Condition(lambda bb: bb.get('has_target')),
    Selector([
        Sequence([
            Condition(lambda bb: bb.get('in_range')),
            Action(lambda bb: attack(bb))
        ]),
        Action(lambda bb: move_to_target(bb))
    ])
])
```

**Steering Behaviors:**
```python
# Required steering behaviors:
- Seek (move toward target)
- Flee (move away from target)
- Arrive (seek with deceleration)
- Wander (random movement)
- Pursue (seek predicted position)
- Evade (flee predicted position)
- ObstacleAvoidance (avoid static obstacles)
- PathFollowing (follow waypoint path)
- Separation (maintain distance from neighbors)
- Alignment (match neighbor velocities)
- Cohesion (move toward group center)

# SteeringBehavior component:
- weight: float (behavior priority)
- max_speed: float
- max_force: float
- arrival_radius: float
- slow_radius: float

# SteeringSystem:
- calculate_steering() -> Vec2
- apply_behaviors(entity, behaviors) -> Vec2
- combine_weighted(forces) -> Vec2
```

**Test Requirements:**
- 25-35 tests for behavior trees
- 15-25 tests for steering behaviors
- Test all node types and combinations
- Test blackboard state management
- Test steering force calculations
- Test flocking behaviors

---

### Phase 5.3: Camera System

**Camera Features:**
```python
# Camera2D component:
- position: Vec2
- zoom: float (default 1.0)
- rotation: float
- viewport_width/height: int
- bounds: Optional[Rect]

# Follow modes:
- None (manual control)
- Smooth (lerp interpolation)
- SnapToTarget (instant)
- DeadzoneFollow (only move when outside deadzone)

# Camera effects:
- Shake (trauma-based screen shake)
- Zoom transitions
- Position transitions
- Rotation

# CameraSystem methods:
- update(target_pos, delta_time)
- screen_to_world(screen_pos) -> world_pos
- world_to_screen(world_pos) -> screen_pos
- shake(intensity, duration)
- zoom_to(target_zoom, duration)
- move_to(target_pos, duration)
- set_bounds(min_x, min_y, max_x, max_y)
```

**Test Requirements:**
- 20-30 tests
- Test all follow modes
- Test coordinate conversions
- Test camera bounds
- Test shake effects
- Test zoom/transitions

---

### Phase 5.4: Tilemap System

**Tilemap Features:**
```python
# Tilemap component:
- tile_width/height: int
- map_width/height: int (in tiles)
- tiles: List[List[int]] (tile IDs)
- tileset_texture: str
- collision_layer: List[List[bool]]

# Tileset class:
- texture_path: str
- tile_width/height: int
- margin: int
- spacing: int
- tiles_per_row: int
- get_tile_rect(tile_id) -> Rect

# TilemapSystem:
- render(tilemap, camera)
- get_tile(x, y) -> int
- set_tile(x, y, tile_id)
- world_to_tile(world_x, world_y) -> (tile_x, tile_y)
- tile_to_world(tile_x, tile_y) -> (world_x, world_y)
- is_walkable(tile_x, tile_y) -> bool
- get_collision_layer() -> NavigationGrid

# Auto-tiling (optional):
- calculate_autotile(x, y, ruleset)
- update_adjacent_tiles(x, y)
```

**Test Requirements:**
- 20-30 tests
- Test tile get/set operations
- Test coordinate conversions
- Test collision layer integration
- Test tileset rendering calculations
- Test auto-tiling (if implemented)

---

### Phase 5.5: Lighting System

**Lighting Features:**
```python
# Light2D component:
- light_type: LightType (POINT, SPOT, DIRECTIONAL)
- color: Tuple[int, int, int]
- intensity: float (0.0-1.0)
- radius: float
- angle: float (for spotlights)
- cast_shadows: bool
- layer_mask: int

# AmbientLight:
- color: Tuple[int, int, int]
- intensity: float

# LightingSystem:
- ambient_light: AmbientLight
- lights: List[Light2D]
- render_lights(surface, camera)
- calculate_lighting(position) -> color
- raycast_shadow(light_pos, target_pos) -> bool
- create_light_surface() -> Surface
- apply_lighting_blend(surface)

# Fog of War:
- FogOfWar component
- explored_tiles: Set[Tuple[int, int]]
- visible_tiles: Set[Tuple[int, int]]
- update_visibility(observer_pos, view_radius)
- render_fog(surface)
```

**Test Requirements:**
- 20-25 tests
- Test light creation and properties
- Test lighting calculations
- Test shadow raycasting
- Test fog of war visibility
- Test light blending

---

## Implementation Guidelines

### General Requirements:
1. **Test-Driven:** Write tests for each feature
2. **Run Tests:** Execute `pytest engine/tests/test_*.py -v` after each implementation
3. **Keep Tests Passing:** All 566 existing tests must remain passing
4. **Commit Frequently:** Commit after each sub-phase with descriptive messages
5. **Push When Done:** Push all commits to `claude/custom-game-engine-011CV4ZDMtMd4GbDDVGcyooq`

### Code Standards:
- Use type hints
- Write comprehensive docstrings
- Follow existing code patterns
- Use dataclasses where appropriate
- Keep functions focused and testable
- Use ECS patterns (Component-based design)

### Testing Standards:
- Aim for 20-35 tests per sub-phase
- Test edge cases
- Test error conditions
- Test integration with existing systems
- Use descriptive test names
- Group tests in classes by functionality

### File Structure:
```
engine/
├── ai/
│   ├── __init__.py
│   ├── pathfinding.py ✅
│   ├── behavior_tree.py (Phase 5.2)
│   └── steering.py (Phase 5.2)
├── rendering/
│   ├── camera.py (Phase 5.3)
│   ├── tilemap.py (Phase 5.4)
│   └── lighting.py (Phase 5.5)
└── tests/
    ├── test_pathfinding.py ✅
    ├── test_behavior_tree.py (Phase 5.2)
    ├── test_steering.py (Phase 5.2)
    ├── test_camera.py (Phase 5.3)
    ├── test_tilemap.py (Phase 5.4)
    └── test_lighting.py (Phase 5.5)
```

---

## Example Command Sequence

```bash
# Phase 5.2: AI System
python -m pytest engine/tests/test_behavior_tree.py -v
python -m pytest engine/tests/test_steering.py -v
git add -A && git commit -m "feat(phase5.2): Add behavior trees and steering behaviors"

# Phase 5.3: Camera System
python -m pytest engine/tests/test_camera.py -v
git add -A && git commit -m "feat(phase5.3): Add 2D camera system with effects"

# Phase 5.4: Tilemap System
python -m pytest engine/tests/test_tilemap.py -v
git add -A && git commit -m "feat(phase5.4): Add tilemap rendering and collision"

# Phase 5.5: Lighting System
python -m pytest engine/tests/test_lighting.py -v
git add -A && git commit -m "feat(phase5.5): Add 2D lighting system - PHASE 5 COMPLETE"

# Final verification
python -m pytest engine/tests/ -v | tail -20
git push -u origin claude/custom-game-engine-011CV4ZDMtMd4GbDDVGcyooq
```

---

## Success Criteria

### Phase 5 Complete When:
- [ ] All 4 sub-phases implemented (5.2, 5.3, 5.4, 5.5)
- [ ] 80-120 new tests added (total: ~650-680 tests)
- [ ] All tests passing
- [ ] All commits pushed to branch
- [ ] Working tree clean (no untracked files)

### Expected Final State:
- **Total Tests:** ~650-680 passing
- **Lines of Code:** ~15,000-18,000 (engine only)
- **Commits:** 4-5 new commits for Phase 5.2-5.5
- **Branch:** Up-to-date with all changes pushed

---

## Quick Start

```bash
# Clone and checkout branch
git checkout claude/custom-game-engine-011CV4ZDMtMd4GbDDVGcyooq

# Verify current state
python -m pytest engine/tests/ -v | grep "passed"
# Should show: 566 passed

# Start with Phase 5.2
touch engine/ai/behavior_tree.py
touch engine/ai/steering.py
touch engine/tests/test_behavior_tree.py
touch engine/tests/test_steering.py

# Implement, test, commit, and continue...
```

---

## Notes

- **Integration:** Systems should integrate with existing ECS architecture
- **Performance:** Consider performance for large numbers of entities
- **Documentation:** Update docstrings and comments
- **Examples:** Consider adding example usage in test files
- **Compatibility:** Maintain pygame compatibility
- **Git:** Keep commits atomic and well-described

Good luck! 🎮🚀
