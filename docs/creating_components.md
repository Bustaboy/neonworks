# Creating Custom Components

Learn how to create custom components for your NeonWorks game.

## What Are Components?

In the Entity Component System (ECS) architecture:
- **Components** are pure data containers
- They have no logic or behavior
- They describe **what** an entity is, not **what it does**

Think of components as labels or properties you attach to entities:
- A `Transform` component says "this entity has a position"
- A `Health` component says "this entity can take damage"
- A `PlayerController` component says "this entity is controlled by the player"

## Built-in Components

NeonWorks provides 11 built-in components (see [API Reference](api_reference.md#built-in-components)):

- `Transform` - Position, rotation, scale
- `GridPosition` - Grid-based position
- `Sprite` - Visual representation
- `Health` - HP and regeneration
- `Survival` - Hunger, thirst, energy
- `Building` - Base building data
- `ResourceStorage` - Resource inventory
- `Navmesh` - Pathfinding data
- `TurnActor` - Turn-based combat data
- `Collider` - Collision box
- `RigidBody` - Physics properties

Use these when possible before creating custom components!

## Creating a Simple Component

Components are created using Python `dataclasses`:

```python
from dataclasses import dataclass
from neonworks.core.ecs import Component

@dataclass
class Velocity(Component):
    """Velocity for moving entities."""
    dx: float = 0.0  # Horizontal velocity
    dy: float = 0.0  # Vertical velocity
```

**Key points**:
1. Inherit from `Component`
2. Use `@dataclass` decorator (automatically generates `__init__`, `__repr__`, etc.)
3. Define fields with type hints
4. Provide default values
5. Add a docstring describing the component's purpose

## Using Your Component

```python
from neonworks.core.ecs import World, Transform

# Create world and entity
world = World()
player = world.create_entity("player")

# Add built-in and custom components
player.add_component(Transform(x=100, y=200))
player.add_component(Velocity(dx=50.0, dy=0.0))

# Access components in a system
for entity in world.get_entities_with_components(Transform, Velocity):
    transform = entity.get_component(Transform)
    velocity = entity.get_component(Velocity)

    # Update position based on velocity
    transform.x += velocity.dx * delta_time
    transform.y += velocity.dy * delta_time
```

## Component Design Patterns

### 1. Flag Components (Markers)

Components don't need data! Use empty components as flags:

```python
@dataclass
class PlayerControlled(Component):
    """Marks an entity as player-controlled."""
    pass

@dataclass
class Enemy(Component):
    """Marks an entity as an enemy."""
    pass

@dataclass
class Interactable(Component):
    """Marks an entity as interactable by the player."""
    pass
```

**Usage**:
```python
# Add marker
player.add_component(PlayerControlled())

# Check in system
for entity in world.get_entities_with_component(Enemy):
    # Process all enemies
    ai_behavior(entity)

# Or use tags for simple flags
player.add_tag("player")
enemy.add_tag("enemy")
```

**When to use components vs tags**:
- **Tags**: Simple string labels, lightweight, no data
- **Components**: Need data or want type safety

### 2. State Components

Store entity state that changes over time:

```python
@dataclass
class Hunger(Component):
    """Hunger level for survival games."""
    current: float = 100.0  # 0 = starving, 100 = full
    max_value: float = 100.0
    decay_rate: float = 1.0  # Points per second

@dataclass
class Stamina(Component):
    """Stamina for actions."""
    current: float = 100.0
    max_value: float = 100.0
    regen_rate: float = 10.0  # Points per second
```

### 3. Configuration Components

Store configuration that doesn't change often:

```python
@dataclass
class MovementConfig(Component):
    """Movement configuration."""
    walk_speed: float = 100.0
    run_speed: float = 200.0
    acceleration: float = 500.0
    friction: float = 0.8

@dataclass
class CombatStats(Component):
    """Combat statistics."""
    attack_power: int = 10
    defense: int = 5
    critical_chance: float = 0.1  # 10%
    critical_multiplier: float = 2.0
```

### 4. Collection Components

Store lists or dictionaries:

```python
from typing import List, Dict
from dataclasses import field

@dataclass
class Inventory(Component):
    """Item inventory."""
    items: List[str] = field(default_factory=list)
    max_capacity: int = 20

    def add_item(self, item: str) -> bool:
        """Add item if there's space."""
        if len(self.items) < self.max_capacity:
            self.items.append(item)
            return True
        return False

    def remove_item(self, item: str) -> bool:
        """Remove item if it exists."""
        if item in self.items:
            self.items.remove(item)
            return True
        return False

@dataclass
class StatusEffects(Component):
    """Active status effects."""
    effects: Dict[str, float] = field(default_factory=dict)  # effect_name -> duration

    def add_effect(self, effect_name: str, duration: float):
        """Add or refresh status effect."""
        self.effects[effect_name] = duration

    def update(self, delta_time: float):
        """Decrease effect durations."""
        expired = []
        for effect, duration in self.effects.items():
            self.effects[effect] -= delta_time
            if self.effects[effect] <= 0:
                expired.append(effect)

        for effect in expired:
            del self.effects[effect]
```

**Important**: When using mutable defaults (list, dict, set), always use `field(default_factory=...)` to avoid sharing data between instances!

### 5. Reference Components

Store references to other entities or objects:

```python
from typing import Optional

@dataclass
class Targeting(Component):
    """Targeting information for combat."""
    target_entity_id: Optional[str] = None
    max_range: float = 100.0

@dataclass
class Parent(Component):
    """Parent-child relationship."""
    parent_entity_id: str = ""

@dataclass
class Weapon(Component):
    """Currently equipped weapon."""
    weapon_entity_id: Optional[str] = None
    damage_bonus: int = 0
```

## Advanced Component Examples

### Example 1: AI Component

```python
from enum import Enum
from typing import Optional, List

class AIState(Enum):
    IDLE = "idle"
    PATROL = "patrol"
    CHASE = "chase"
    ATTACK = "attack"
    FLEE = "flee"

@dataclass
class AIController(Component):
    """AI behavior controller."""
    state: AIState = AIState.IDLE
    detection_range: float = 200.0
    attack_range: float = 50.0
    patrol_points: List[tuple] = field(default_factory=list)
    current_patrol_index: int = 0
    target_entity_id: Optional[str] = None
    aggression: float = 0.5  # 0 = passive, 1 = aggressive
```

### Example 2: Animation Component

```python
@dataclass
class AnimationState(Component):
    """Animation state machine."""
    current_animation: str = "idle"
    frame_index: int = 0
    frame_time: float = 0.0
    frame_duration: float = 0.1  # Seconds per frame
    loop: bool = True
    animations: Dict[str, List[str]] = field(default_factory=dict)  # name -> frame paths

    def set_animation(self, animation_name: str):
        """Change animation if different."""
        if animation_name != self.current_animation:
            self.current_animation = animation_name
            self.frame_index = 0
            self.frame_time = 0.0
```

### Example 3: Quest Component

```python
from typing import Dict, Set

@dataclass
class QuestProgress(Component):
    """Track quest progress."""
    active_quests: Set[str] = field(default_factory=set)  # Quest IDs
    completed_quests: Set[str] = field(default_factory=set)
    quest_objectives: Dict[str, Dict[str, int]] = field(default_factory=dict)  # quest_id -> {objective: progress}

    def start_quest(self, quest_id: str, objectives: Dict[str, int]):
        """Start a new quest."""
        self.active_quests.add(quest_id)
        self.quest_objectives[quest_id] = objectives.copy()

    def complete_quest(self, quest_id: str):
        """Mark quest as completed."""
        if quest_id in self.active_quests:
            self.active_quests.remove(quest_id)
            self.completed_quests.add(quest_id)
            if quest_id in self.quest_objectives:
                del self.quest_objectives[quest_id]
```

### Example 4: Dialogue Component

```python
@dataclass
class DialogueState(Component):
    """NPC dialogue state."""
    dialogue_tree_id: str = ""
    current_node: str = "start"
    conversation_history: List[str] = field(default_factory=list)
    relationship: int = 0  # -100 to 100
    flags: Set[str] = field(default_factory=set)  # Dialogue flags (e.g., "quest_accepted")

    def set_flag(self, flag: str):
        """Set a dialogue flag."""
        self.flags.add(flag)

    def has_flag(self, flag: str) -> bool:
        """Check if dialogue flag is set."""
        return flag in self.flags
```

## Component Organization

### File Structure

Organize components by category:

```
my_game/
└── scripts/
    └── components/
        ├── __init__.py
        ├── movement.py       # Velocity, MovementConfig
        ├── combat.py         # CombatStats, Weapon, Armor
        ├── ai.py            # AIController, AIState
        ├── animation.py     # AnimationState
        ├── quest.py         # QuestProgress
        └── dialogue.py      # DialogueState
```

**components/__init__.py**:
```python
"""Custom game components."""

from .movement import Velocity, MovementConfig
from .combat import CombatStats, Weapon, Armor
from .ai import AIController, AIState
from .animation import AnimationState
from .quest import QuestProgress
from .dialogue import DialogueState

__all__ = [
    'Velocity', 'MovementConfig',
    'CombatStats', 'Weapon', 'Armor',
    'AIController', 'AIState',
    'AnimationState',
    'QuestProgress',
    'DialogueState',
]
```

**Usage**:
```python
from scripts.components import Velocity, CombatStats, AIController

entity.add_component(Velocity(dx=100, dy=0))
entity.add_component(CombatStats(attack_power=15))
entity.add_component(AIController(detection_range=300))
```

## Best Practices

### 1. Keep Components Simple

**Good** ✅:
```python
@dataclass
class Health(Component):
    current: float = 100.0
    maximum: float = 100.0
```

**Bad** ❌:
```python
@dataclass
class Health(Component):
    current: float = 100.0
    maximum: float = 100.0

    def take_damage(self, amount: float):  # Don't put logic in components!
        self.current -= amount
        if self.current <= 0:
            self.die()
```

**Why?** Logic belongs in Systems, not Components. Keep components as pure data.

### 2. Use Type Hints

**Good** ✅:
```python
@dataclass
class Inventory(Component):
    items: List[str] = field(default_factory=list)
    gold: int = 0
    max_weight: float = 50.0
```

**Bad** ❌:
```python
@dataclass
class Inventory(Component):
    items = []  # No type hint, shared between instances!
    gold = 0
    max_weight = 50.0
```

### 3. Provide Defaults

**Good** ✅:
```python
@dataclass
class MovementConfig(Component):
    speed: float = 100.0
    jump_force: float = 500.0
```

**Bad** ❌:
```python
@dataclass
class MovementConfig(Component):
    speed: float  # No default, must always be specified
    jump_force: float
```

### 4. Use Descriptive Names

**Good** ✅:
```python
@dataclass
class PlayerController(Component):
    movement_speed: float = 200.0
    jump_height: float = 100.0
```

**Bad** ❌:
```python
@dataclass
class PC(Component):  # Unclear abbreviation
    spd: float = 200.0  # Unclear abbreviation
    jh: float = 100.0
```

### 5. Document Your Components

**Good** ✅:
```python
@dataclass
class Stamina(Component):
    """
    Stamina for performing actions.

    Stamina regenerates over time and is consumed by actions like
    running, jumping, and attacking. When stamina reaches zero,
    the entity is exhausted and cannot perform stamina-based actions.
    """
    current: float = 100.0  # Current stamina points
    max_value: float = 100.0  # Maximum stamina
    regen_rate: float = 10.0  # Points per second
    exhaustion_threshold: float = 0.0  # Stamina level for exhaustion
```

### 6. Avoid Component Coupling

**Good** ✅:
```python
# Independent components
@dataclass
class Health(Component):
    current: float = 100.0
    maximum: float = 100.0

@dataclass
class Shield(Component):
    current: float = 50.0
    maximum: float = 50.0
    recharge_rate: float = 5.0

# System handles interaction
class DamageSystem(System):
    def apply_damage(self, entity: Entity, amount: float):
        shield = entity.get_component(Shield)
        if shield and shield.current > 0:
            shield.current -= amount
        else:
            health = entity.get_component(Health)
            if health:
                health.current -= amount
```

**Bad** ❌:
```python
# Tightly coupled components
@dataclass
class Health(Component):
    current: float = 100.0
    maximum: float = 100.0
    shield_amount: float = 50.0  # Don't mix concerns!
    shield_recharge: float = 5.0
```

## Common Pitfalls

### Pitfall 1: Mutable Default Arguments

**Problem**:
```python
@dataclass
class Inventory(Component):
    items: List[str] = []  # ❌ Shared between ALL instances!
```

**Solution**:
```python
@dataclass
class Inventory(Component):
    items: List[str] = field(default_factory=list)  # ✅ Each instance gets its own list
```

### Pitfall 2: Logic in Components

**Problem**:
```python
@dataclass
class Health(Component):
    current: float = 100.0

    def take_damage(self, amount: float):  # ❌ Logic in component
        self.current -= amount
```

**Solution**:
```python
# Component: Pure data
@dataclass
class Health(Component):
    current: float = 100.0
    maximum: float = 100.0

# System: Logic
class DamageSystem(System):
    def apply_damage(self, entity: Entity, amount: float):  # ✅ Logic in system
        health = entity.get_component(Health)
        if health:
            health.current -= amount
            if health.current <= 0:
                self.handle_death(entity)
```

### Pitfall 3: Too Many Components on One Entity

**Problem**: Entity with 15+ components becomes hard to manage.

**Solution**: Group related data:

```python
# Instead of: Speed, MaxSpeed, Acceleration, Friction, JumpForce...
# Use a single config component:
@dataclass
class MovementConfig(Component):
    walk_speed: float = 100.0
    run_speed: float = 200.0
    acceleration: float = 500.0
    friction: float = 0.8
    jump_force: float = 500.0
```

## Testing Components

```python
import pytest
from scripts.components import Velocity, Inventory

def test_velocity_component():
    """Test velocity component."""
    vel = Velocity(dx=50.0, dy=100.0)
    assert vel.dx == 50.0
    assert vel.dy == 100.0

def test_inventory_component():
    """Test inventory component."""
    inv = Inventory(max_capacity=10)

    # Test adding items
    assert inv.add_item("sword") == True
    assert len(inv.items) == 1

    # Test capacity
    for i in range(9):
        inv.add_item(f"item_{i}")
    assert inv.add_item("extra") == False  # Should fail (full)

    # Test removing items
    assert inv.remove_item("sword") == True
    assert len(inv.items) == 9

def test_inventory_instances_independent():
    """Test that inventory instances don't share data."""
    inv1 = Inventory()
    inv2 = Inventory()

    inv1.add_item("sword")

    assert len(inv1.items) == 1
    assert len(inv2.items) == 0  # Should be independent
```

## Next Steps

- [Creating Systems](creating_systems.md) - Implement logic that uses your components
- [API Reference](api_reference.md) - Complete component API
- [Example: Simple RPG](../examples/simple_rpg/README.md) - See components in action
