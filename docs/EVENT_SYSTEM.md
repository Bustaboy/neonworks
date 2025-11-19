# NeonWorks Event System

Complete guide to the event-driven architecture in NeonWorks.

## Table of Contents
- [Overview](#overview)
- [Core Concepts](#core-concepts)
- [Event Types](#event-types)
- [Creating and Emitting Events](#creating-and-emitting-events)
- [Subscribing to Events](#subscribing-to-events)
- [Event Processing](#event-processing)
- [Best Practices](#best-practices)
- [Common Patterns](#common-patterns)
- [Examples](#examples)

---

## Overview

The NeonWorks event system provides decoupled communication between different parts of your game. Instead of Systems directly calling each other, they emit events that other Systems can listen to.

### Why Use Events?

**Without Events (Tight Coupling):**
```python
class DamageSystem(System):
    def __init__(self, ui_system, audio_system, achievement_system):
        self.ui_system = ui_system
        self.audio_system = audio_system
        self.achievement_system = achievement_system

    def apply_damage(self, entity, amount):
        # Apply damage
        health = entity.get_component(Health)
        health.current -= amount

        # Manually notify other systems
        self.ui_system.show_damage_text(amount)
        self.audio_system.play_sound("hit")
        self.achievement_system.check_damage_dealt(amount)
```

**With Events (Loose Coupling):**
```python
class DamageSystem(System):
    def __init__(self):
        self.event_manager = get_event_manager()

    def apply_damage(self, entity, amount):
        # Apply damage
        health = entity.get_component(Health)
        health.current -= amount

        # Emit event - others can react independently
        self.event_manager.emit(Event(EventType.DAMAGE_DEALT, {
            "entity_id": entity.id,
            "amount": amount
        }))
```

### Benefits

✅ **Decoupling**: Systems don't need to know about each other
✅ **Scalability**: Easy to add new reactions without modifying existing code
✅ **Testability**: Test systems in isolation
✅ **Flexibility**: Enable/disable features by subscribing/unsubscribing
✅ **Debugging**: Log all events to understand game flow

---

## Core Concepts

### EventType

`EventType` is an enum defining all possible event types in your game:

```python
from neonworks.core.events import EventType

# Built-in event types
EventType.DAMAGE_DEALT
EventType.UNIT_DIED
EventType.TURN_START
EventType.BUILDING_COMPLETED
# ... and many more
```

### Event

An `Event` is a data class containing:
- `event_type`: The type of event (from EventType enum)
- `data`: Dictionary of event-specific data

```python
from neonworks.core.events import Event, EventType

event = Event(
    event_type=EventType.DAMAGE_DEALT,
    data={
        "attacker_id": "player_1",
        "target_id": "enemy_5",
        "amount": 25
    }
)
```

### EventManager

The `EventManager` handles:
- Subscribing handlers to event types
- Emitting events
- Queuing events
- Dispatching events to subscribers

```python
from neonworks.core.events import get_event_manager

event_manager = get_event_manager()
```

---

## Event Types

NeonWorks includes built-in event types organized by category:

### Turn-Based Events

```python
EventType.TURN_START        # New turn begins
EventType.TURN_END          # Turn ends
EventType.ACTION_PERFORMED  # Entity performs action
```

### Combat Events

```python
EventType.COMBAT_START      # Combat begins
EventType.COMBAT_END        # Combat ends
EventType.DAMAGE_DEALT      # Damage applied
EventType.UNIT_DIED         # Entity died
```

### Building Events

```python
EventType.BUILDING_PLACED     # Building placed
EventType.BUILDING_COMPLETED  # Construction finished
EventType.BUILDING_UPGRADED   # Building upgraded
EventType.BUILDING_DESTROYED  # Building destroyed
```

### Survival Events

```python
EventType.HUNGER_CRITICAL   # Hunger critically low
EventType.THIRST_CRITICAL   # Thirst critically low
EventType.ENERGY_DEPLETED   # Energy depleted
```

### Resource Events

```python
EventType.RESOURCE_COLLECTED  # Resource gathered
EventType.RESOURCE_CONSUMED   # Resource used
EventType.RESOURCE_DEPLETED   # Resource fully depleted
```

### UI Events

```python
EventType.UI_BUTTON_CLICKED    # Button clicked
EventType.UI_TILE_SELECTED     # Tile selected
EventType.UI_ENTITY_SELECTED   # Entity selected
```

### Game State Events

```python
EventType.GAME_PAUSED   # Game paused
EventType.GAME_RESUMED  # Game resumed
EventType.GAME_SAVED    # Game saved
EventType.GAME_LOADED   # Game loaded
```

### Custom Event Types

Extend EventType for your game:

```python
from neonworks.core.events import EventType
from enum import auto

class CustomEventType(EventType):
    # Your custom events
    QUEST_COMPLETED = auto()
    SKILL_LEARNED = auto()
    SHOP_OPENED = auto()
    DIALOGUE_STARTED = auto()
```

---

## Creating and Emitting Events

### Basic Emission

```python
from neonworks.core.events import get_event_manager, Event, EventType

event_manager = get_event_manager()

# Emit event
event_manager.emit(Event(EventType.DAMAGE_DEALT, {
    "entity_id": entity.id,
    "amount": 50
}))
```

### Convenience Function

```python
from neonworks.core.events import emit_event, EventType

# Shorter syntax
emit_event(EventType.DAMAGE_DEALT, {
    "entity_id": entity.id,
    "amount": 50
})
```

### Immediate vs Queued

By default, events are **queued** and processed later:

```python
# Queued (default)
event_manager.emit(Event(EventType.DAMAGE_DEALT, data))

# Called later
event_manager.process_events()
```

For immediate processing:

```python
# Processes immediately
event_manager.emit_immediate(Event(EventType.DAMAGE_DEALT, data))
```

### When to Use Immediate vs Queued

**Use Queued (default):**
- Normal gameplay events
- Non-critical updates
- Events that can wait until end of frame

**Use Immediate:**
- Critical game state changes
- Events that must execute synchronously
- Debugging/logging
- Events emitted during event processing

---

## Subscribing to Events

### Basic Subscription

```python
from neonworks.core.events import get_event_manager, EventType, Event

def on_damage_dealt(event: Event):
    """Handler function"""
    print(f"Damage dealt: {event.data['amount']}")

event_manager = get_event_manager()
event_manager.subscribe(EventType.DAMAGE_DEALT, on_damage_dealt)
```

### In Systems

```python
class AudioSystem(System):
    def __init__(self):
        super().__init__()
        self.event_manager = get_event_manager()

        # Subscribe in __init__
        self.event_manager.subscribe(EventType.DAMAGE_DEALT, self.on_damage)
        self.event_manager.subscribe(EventType.UNIT_DIED, self.on_death)

    def on_damage(self, event: Event):
        """Play hit sound"""
        self.play_sound("hit")

    def on_death(self, event: Event):
        """Play death sound"""
        self.play_sound("death")

    def update(self, world: World, delta_time: float):
        # Regular system update
        pass
```

### Unsubscribing

```python
# Store reference to handler
def my_handler(event):
    pass

# Subscribe
event_manager.subscribe(EventType.DAMAGE_DEALT, my_handler)

# Unsubscribe later
event_manager.unsubscribe(EventType.DAMAGE_DEALT, my_handler)
```

### Multiple Handlers

Multiple handlers can subscribe to the same event:

```python
def play_sound(event):
    pass

def show_damage_text(event):
    pass

def update_statistics(event):
    pass

# All will be called when event is emitted
event_manager.subscribe(EventType.DAMAGE_DEALT, play_sound)
event_manager.subscribe(EventType.DAMAGE_DEALT, show_damage_text)
event_manager.subscribe(EventType.DAMAGE_DEALT, update_statistics)
```

---

## Event Processing

### The Event Queue

Events are queued when emitted (unless using `emit_immediate`):

```python
# These events are queued
emit_event(EventType.DAMAGE_DEALT, {...})
emit_event(EventType.UNIT_DIED, {...})
emit_event(EventType.TURN_END, {...})

# Nothing happens yet...

# Process all queued events
event_manager.process_events()
```

### Processing in Game Loop

**Recommended pattern:**

```python
def game_loop():
    event_manager = get_event_manager()
    clock = pygame.time.Clock()

    while running:
        # 1. Handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 2. Update systems (may emit events)
        delta_time = clock.tick(60) / 1000.0
        world.update(delta_time)

        # 3. Process queued events
        event_manager.process_events()

        # 4. Render
        render(world, screen)
        pygame.display.flip()
```

### Immediate Mode

For synchronous event processing:

```python
event_manager.set_immediate_mode(True)

# Events now process immediately
emit_event(EventType.DAMAGE_DEALT, {...})  # Handlers called right away

event_manager.set_immediate_mode(False)  # Back to queued
```

---

## Best Practices

### ✅ DO: Use Events for Cross-System Communication

```python
# Good: Decouple systems with events
class CombatSystem(System):
    def apply_damage(self, entity, amount):
        emit_event(EventType.DAMAGE_DEALT, {
            "entity_id": entity.id,
            "amount": amount
        })

class AchievementSystem(System):
    def __init__(self):
        get_event_manager().subscribe(EventType.DAMAGE_DEALT, self.on_damage)

    def on_damage(self, event):
        self.total_damage += event.data["amount"]
```

### ✅ DO: Include All Necessary Data in Events

```python
# Good: Complete information
emit_event(EventType.DAMAGE_DEALT, {
    "entity_id": entity.id,
    "attacker_id": attacker.id,
    "amount": damage,
    "is_critical": True,
    "damage_type": "fire"
})
```

### ✅ DO: Store Entity IDs, Not References

```python
# Good: Store ID
emit_event(EventType.UNIT_DIED, {"entity_id": entity.id})

# Bad: Store reference
emit_event(EventType.UNIT_DIED, {"entity": entity})  # May be invalid later!
```

### ✅ DO: Handle Missing Data Gracefully

```python
def on_damage(event: Event):
    entity_id = event.data.get("entity_id")
    if not entity_id:
        return  # Invalid event

    entity = world.get_entity(entity_id)
    if not entity:
        return  # Entity no longer exists
```

### ❌ DON'T: Create Circular Event Dependencies

```python
# Bad: Circular dependency
def on_damage(event):
    emit_event(EventType.HEAL, {...})  # Emits heal

def on_heal(event):
    emit_event(EventType.DAMAGE_DEALT, {...})  # Emits damage - infinite loop!
```

### ❌ DON'T: Forget to Process Events

```python
# Bad: Events never dispatched
def game_loop():
    while running:
        world.update(delta_time)
        # Missing: event_manager.process_events()
        render()
```

### ❌ DON'T: Do Heavy Work in Event Handlers

```python
# Bad: Expensive operation in handler
def on_damage(event):
    # Recalculates entire navmesh on every damage event!
    rebuild_navmesh()

# Good: Set flag, do work in system update
class NavmeshSystem(System):
    def __init__(self):
        self.needs_rebuild = False
        get_event_manager().subscribe(EventType.BUILDING_DESTROYED, self.mark_dirty)

    def mark_dirty(self, event):
        self.needs_rebuild = True

    def update(self, world, delta_time):
        if self.needs_rebuild:
            rebuild_navmesh()
            self.needs_rebuild = False
```

---

## Common Patterns

### Pattern 1: Achievement System

```python
class AchievementSystem(System):
    def __init__(self):
        super().__init__()
        self.stats = {
            "total_damage": 0,
            "enemies_killed": 0,
            "distance_traveled": 0
        }
        self.achievements = []

        # Subscribe to relevant events
        em = get_event_manager()
        em.subscribe(EventType.DAMAGE_DEALT, self.on_damage)
        em.subscribe(EventType.UNIT_DIED, self.on_unit_died)

    def on_damage(self, event: Event):
        self.stats["total_damage"] += event.data["amount"]
        self.check_achievement("deal_1000_damage", self.stats["total_damage"] >= 1000)

    def on_unit_died(self, event: Event):
        # Check if enemy died
        entity = world.get_entity(event.data["entity_id"])
        if entity and entity.has_tag("enemy"):
            self.stats["enemies_killed"] += 1
            self.check_achievement("kill_50_enemies", self.stats["enemies_killed"] >= 50)

    def check_achievement(self, achievement_id: str, unlocked: bool):
        if unlocked and achievement_id not in self.achievements:
            self.achievements.append(achievement_id)
            emit_event(EventType.ACHIEVEMENT_UNLOCKED, {"id": achievement_id})
```

### Pattern 2: Damage Numbers UI

```python
class DamageNumbersSystem(System):
    def __init__(self, world: World):
        super().__init__()
        self.world = world
        get_event_manager().subscribe(EventType.DAMAGE_DEALT, self.on_damage)

    def on_damage(self, event: Event):
        entity_id = event.data.get("entity_id")
        amount = event.data.get("amount", 0)

        entity = self.world.get_entity(entity_id)
        if not entity:
            return

        transform = entity.get_component(Transform)
        if not transform:
            return

        # Create floating damage text
        text_entity = self.world.create_entity()
        text_entity.add_component(Transform(x=transform.x, y=transform.y - 20))
        text_entity.add_component(FloatingText(
            text=str(amount),
            color=(255, 0, 0),
            lifetime=1.0,
            velocity_y=-50
        ))
```

### Pattern 3: Quest System

```python
class Quest:
    def __init__(self, quest_id: str):
        self.id = quest_id
        self.completed = False
        self.objectives = {}

class QuestSystem(System):
    def __init__(self):
        super().__init__()
        self.active_quests = []

        # Subscribe to events that advance quests
        em = get_event_manager()
        em.subscribe(EventType.UNIT_DIED, self.on_unit_died)
        em.subscribe(EventType.RESOURCE_COLLECTED, self.on_resource_collected)
        em.subscribe(EventType.BUILDING_COMPLETED, self.on_building_completed)

    def on_unit_died(self, event: Event):
        entity_id = event.data["entity_id"]
        # Check all quests for "kill X enemies" objectives
        for quest in self.active_quests:
            if "kill_enemies" in quest.objectives:
                quest.objectives["kill_enemies"] += 1
                self.check_quest_completion(quest)

    def on_resource_collected(self, event: Event):
        resource_type = event.data["resource_type"]
        amount = event.data["amount"]
        # Check all quests for "collect X resources" objectives
        for quest in self.active_quests:
            if f"collect_{resource_type}" in quest.objectives:
                quest.objectives[f"collect_{resource_type}"] += amount
                self.check_quest_completion(quest)

    def check_quest_completion(self, quest: Quest):
        # Check if all objectives met
        if self.all_objectives_complete(quest):
            quest.completed = True
            emit_event(EventType.QUEST_COMPLETED, {"quest_id": quest.id})
```

### Pattern 4: Combat Log

```python
class CombatLogSystem(System):
    def __init__(self):
        super().__init__()
        self.log = []

        em = get_event_manager()
        em.subscribe(EventType.DAMAGE_DEALT, self.log_damage)
        em.subscribe(EventType.UNIT_DIED, self.log_death)
        em.subscribe(EventType.TURN_START, self.log_turn_start)

    def log_damage(self, event: Event):
        attacker_id = event.data.get("attacker_id", "Unknown")
        target_id = event.data.get("target_id", "Unknown")
        amount = event.data.get("amount", 0)

        message = f"{attacker_id} dealt {amount} damage to {target_id}"
        self.log.append(message)
        print(message)

    def log_death(self, event: Event):
        entity_id = event.data["entity_id"]
        message = f"{entity_id} has died!"
        self.log.append(message)
        print(message)

    def log_turn_start(self, event: Event):
        turn_number = event.data.get("turn", 0)
        message = f"--- Turn {turn_number} ---"
        self.log.append(message)
        print(message)
```

### Pattern 5: Tutorial System

```python
class TutorialSystem(System):
    def __init__(self):
        super().__init__()
        self.shown_tutorials = set()

        em = get_event_manager()
        em.subscribe(EventType.DAMAGE_DEALT, self.on_damage)
        em.subscribe(EventType.RESOURCE_COLLECTED, self.on_resource_collected)
        em.subscribe(EventType.BUILDING_PLACED, self.on_building_placed)

    def show_tutorial(self, tutorial_id: str, message: str):
        if tutorial_id not in self.shown_tutorials:
            self.shown_tutorials.add(tutorial_id)
            emit_event(EventType.SHOW_TUTORIAL, {
                "id": tutorial_id,
                "message": message
            })

    def on_damage(self, event: Event):
        self.show_tutorial("combat_basics", "You dealt damage! Attack enemies to survive.")

    def on_resource_collected(self, event: Event):
        self.show_tutorial("gathering", "Resources can be used to craft and build.")

    def on_building_placed(self, event: Event):
        self.show_tutorial("building", "Buildings provide shelter and resources.")
```

---

## Examples

### Complete Example: Damage System with Events

```python
from neonworks.core.ecs import System, World, Entity, Component
from neonworks.core.events import get_event_manager, Event, EventType
from dataclasses import dataclass

@dataclass
class Health(Component):
    current: float = 100.0
    maximum: float = 100.0

@dataclass
class CombatStats(Component):
    attack: int = 10
    defense: int = 5

class DamageSystem(System):
    """Applies damage and emits events"""

    def __init__(self):
        super().__init__()
        self.event_manager = get_event_manager()

    def deal_damage(self, attacker: Entity, target: Entity, base_damage: int):
        """Deal damage from attacker to target"""
        # Get components
        attacker_stats = attacker.get_component(CombatStats)
        target_health = target.get_component(Health)
        target_stats = target.get_component(CombatStats)

        if not all([attacker_stats, target_health, target_stats]):
            return

        # Calculate damage
        damage = max(1, base_damage + attacker_stats.attack - target_stats.defense)

        # Apply damage
        target_health.current -= damage
        target_health.current = max(0, target_health.current)

        # Emit damage event
        self.event_manager.emit(Event(EventType.DAMAGE_DEALT, {
            "attacker_id": attacker.id,
            "target_id": target.id,
            "amount": damage
        }))

        # Check for death
        if target_health.current <= 0:
            self.event_manager.emit(Event(EventType.UNIT_DIED, {
                "entity_id": target.id,
                "killer_id": attacker.id
            }))

class AudioSystem(System):
    """Reacts to events with sound effects"""

    def __init__(self):
        super().__init__()
        em = get_event_manager()
        em.subscribe(EventType.DAMAGE_DEALT, self.on_damage)
        em.subscribe(EventType.UNIT_DIED, self.on_death)

    def on_damage(self, event: Event):
        print(f"[AUDIO] Playing 'hit' sound")
        # self.audio_manager.play("hit")

    def on_death(self, event: Event):
        print(f"[AUDIO] Playing 'death' sound")
        # self.audio_manager.play("death")

    def update(self, world: World, delta_time: float):
        pass

class UISystem(System):
    """Reacts to events with UI updates"""

    def __init__(self):
        super().__init__()
        em = get_event_manager()
        em.subscribe(EventType.DAMAGE_DEALT, self.on_damage)

    def on_damage(self, event: Event):
        amount = event.data["amount"]
        target_id = event.data["target_id"]
        print(f"[UI] Showing damage text: -{amount} on {target_id}")
        # self.create_damage_number(target_id, amount)

    def update(self, world: World, delta_time: float):
        pass

# Setup
world = World()
event_manager = get_event_manager()

# Create entities
player = world.create_entity()
player.add_component(Health(current=100, maximum=100))
player.add_component(CombatStats(attack=15, defense=5))

enemy = world.create_entity()
enemy.add_component(Health(current=50, maximum=50))
enemy.add_component(CombatStats(attack=10, defense=3))

# Add systems
damage_system = DamageSystem()
audio_system = AudioSystem()
ui_system = UISystem()

world.add_system(damage_system)
world.add_system(audio_system)
world.add_system(ui_system)

# Simulate combat
damage_system.deal_damage(player, enemy, base_damage=20)
event_manager.process_events()
# Output:
# [UI] Showing damage text: -32 on <enemy_id>
# [AUDIO] Playing 'hit' sound

damage_system.deal_damage(player, enemy, base_damage=25)
event_manager.process_events()
# Output:
# [UI] Showing damage text: -37 on <enemy_id>
# [AUDIO] Playing 'hit' sound
# [AUDIO] Playing 'death' sound
```

---

## Summary

The NeonWorks event system provides:

✅ **Decoupled architecture** - Systems don't depend on each other
✅ **Scalability** - Easy to add new behaviors
✅ **Flexibility** - Subscribe/unsubscribe handlers dynamically
✅ **Debuggability** - Log events to understand game flow

### Key Takeaways

1. **Use events for cross-system communication**
2. **Store entity IDs, not references**
3. **Process events in your game loop**
4. **Avoid circular dependencies**
5. **Keep handlers lightweight**
6. **Include all necessary data in events**

For more information, see:
- [API Reference](api_reference.md) - EventManager API
- [Creating Systems](creating_systems.md) - System best practices
- [Common Pitfalls](COMMON_PITFALLS.md) - Event system gotchas
