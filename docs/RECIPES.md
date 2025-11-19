# NeonWorks Code Recipes

Ready-to-use code snippets for common game development tasks. Copy, paste, and customize for your game!

## Table of Contents
- [Health Bar](#health-bar)
- [Inventory System](#inventory-system)
- [Save/Load System](#saveload-system)
- [Dialogue System](#dialogue-system)
- [Pathfinding](#pathfinding)
- [Camera Controls](#camera-controls)
- [Particle Effects](#particle-effects)
- [UI Menus](#ui-menus)
- [Audio Manager](#audio-manager)
- [Combat System](#combat-system)

---

## Health Bar

Display a visual health bar above entities.

### Components

```python
from neonworks.core.ecs import Component
from dataclasses import dataclass

@dataclass
class Health(Component):
    """Health component"""
    current: float = 100.0
    maximum: float = 100.0

    @property
    def percentage(self) -> float:
        return self.current / self.maximum if self.maximum > 0 else 0

@dataclass
class HealthBar(Component):
    """Visual health bar display"""
    width: int = 50
    height: int = 5
    offset_y: int = -10  # Pixels above entity
    background_color: tuple = (60, 60, 60)
    health_color: tuple = (0, 255, 0)
    low_health_color: tuple = (255, 0, 0)
    low_health_threshold: float = 0.3  # Red below 30%
```

### System

```python
import pygame
from neonworks.core.ecs import System, World, Transform

class HealthBarRenderSystem(System):
    """Renders health bars above entities"""

    def __init__(self, screen: pygame.Surface):
        super().__init__()
        self.screen = screen
        self.priority = 100  # Render after sprites

    def update(self, world: World, delta_time: float):
        for entity in world.get_entities_with_components(Transform, Health, HealthBar):
            transform = entity.get_component(Transform)
            health = entity.get_component(Health)
            health_bar = entity.get_component(HealthBar)

            # Calculate position
            x = int(transform.x - health_bar.width // 2)
            y = int(transform.y + health_bar.offset_y)

            # Draw background
            bg_rect = pygame.Rect(x, y, health_bar.width, health_bar.height)
            pygame.draw.rect(self.screen, health_bar.background_color, bg_rect)

            # Draw health
            health_width = int(health_bar.width * health.percentage)
            if health_width > 0:
                health_rect = pygame.Rect(x, y, health_width, health_bar.height)
                color = (health_bar.low_health_color if health.percentage < health_bar.low_health_threshold
                        else health_bar.health_color)
                pygame.draw.rect(self.screen, color, health_rect)

            # Draw border
            pygame.draw.rect(self.screen, (255, 255, 255), bg_rect, 1)
```

### Usage

```python
# Create entity with health bar
enemy = world.create_entity()
enemy.add_component(Transform(x=400, y=300))
enemy.add_component(Health(current=75, maximum=100))
enemy.add_component(HealthBar())

# Add render system
world.add_system(HealthBarRenderSystem(screen))
```

---

## Inventory System

Full-featured inventory with item management.

### Components

```python
from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class Item:
    """Represents an inventory item"""
    id: str
    name: str
    description: str
    icon: str  # Path to icon image
    stackable: bool = True
    max_stack: int = 99
    value: int = 0  # Gold/currency value

@dataclass
class ItemStack:
    """A stack of items"""
    item: Item
    quantity: int = 1

    def add(self, amount: int) -> int:
        """Add items, return overflow"""
        max_add = self.item.max_stack - self.quantity
        actual_add = min(amount, max_add)
        self.quantity += actual_add
        return amount - actual_add

    def remove(self, amount: int) -> int:
        """Remove items, return amount removed"""
        actual_remove = min(amount, self.quantity)
        self.quantity -= actual_remove
        return actual_remove

@dataclass
class Inventory(Component):
    """Inventory component"""
    slots: Dict[int, ItemStack] = field(default_factory=dict)
    max_slots: int = 20
    gold: int = 0

    def add_item(self, item: Item, quantity: int = 1) -> int:
        """Add item, return amount that didn't fit"""
        remaining = quantity

        # Try to stack with existing items
        if item.stackable:
            for slot_index, stack in self.slots.items():
                if stack.item.id == item.id:
                    overflow = stack.add(remaining)
                    remaining = overflow
                    if remaining == 0:
                        return 0

        # Find empty slots
        while remaining > 0:
            empty_slot = self._find_empty_slot()
            if empty_slot is None:
                return remaining  # No space

            stack_size = min(remaining, item.max_stack)
            self.slots[empty_slot] = ItemStack(item, stack_size)
            remaining -= stack_size

        return 0

    def remove_item(self, item_id: str, quantity: int = 1) -> int:
        """Remove item, return amount removed"""
        removed = 0

        for slot_index in list(self.slots.keys()):
            stack = self.slots[slot_index]
            if stack.item.id == item_id:
                amount = stack.remove(quantity - removed)
                removed += amount

                if stack.quantity <= 0:
                    del self.slots[slot_index]

                if removed >= quantity:
                    break

        return removed

    def has_item(self, item_id: str, quantity: int = 1) -> bool:
        """Check if inventory has item"""
        total = sum(stack.quantity for stack in self.slots.values()
                   if stack.item.id == item_id)
        return total >= quantity

    def get_item_count(self, item_id: str) -> int:
        """Get total quantity of item"""
        return sum(stack.quantity for stack in self.slots.values()
                  if stack.item.id == item_id)

    def _find_empty_slot(self) -> Optional[int]:
        """Find first empty slot"""
        for i in range(self.max_slots):
            if i not in self.slots:
                return i
        return None

    @property
    def is_full(self) -> bool:
        return len(self.slots) >= self.max_slots
```

### System

```python
from neonworks.core.events import EventManager, Event, EventType

class InventorySystem(System):
    """Manages inventory operations and events"""

    def __init__(self, event_manager: EventManager):
        super().__init__()
        self.event_manager = event_manager

    def update(self, world: World, delta_time: float):
        # Process inventory events
        pass  # Add custom logic here

    def pickup_item(self, entity: Entity, item: Item, quantity: int = 1):
        """Pickup item into entity's inventory"""
        inventory = entity.get_component(Inventory)
        if not inventory:
            return False

        overflow = inventory.add_item(item, quantity)
        picked_up = quantity - overflow

        if picked_up > 0:
            self.event_manager.emit(Event(EventType.RESOURCE_COLLECTED, {
                "entity_id": entity.id,
                "item_id": item.id,
                "quantity": picked_up
            }))
            return True
        return False

    def drop_item(self, entity: Entity, item_id: str, quantity: int = 1):
        """Drop item from inventory"""
        inventory = entity.get_component(Inventory)
        if not inventory:
            return False

        removed = inventory.remove_item(item_id, quantity)
        if removed > 0:
            # Create item entity in world
            # (Implementation depends on your game)
            return True
        return False
```

### Usage

```python
# Define items
health_potion = Item(
    id="health_potion",
    name="Health Potion",
    description="Restores 50 HP",
    icon="assets/items/health_potion.png",
    stackable=True,
    max_stack=20,
    value=50
)

# Add inventory to player
player.add_component(Inventory(max_slots=20, gold=100))

# Add system
inventory_system = InventorySystem(get_event_manager())
world.add_system(inventory_system)

# Pickup item
inventory_system.pickup_item(player, health_potion, 5)

# Check inventory
inventory = player.get_component(Inventory)
if inventory.has_item("health_potion", 1):
    print(f"You have {inventory.get_item_count('health_potion')} potions")
```

---

## Save/Load System

Complete save/load functionality with multiple save slots.

### Implementation

```python
from neonworks.core.serialization import save_world, load_world
from neonworks.core.ecs import World
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

class SaveGame:
    """Represents a save game file"""

    def __init__(self, slot: int, save_dir: str = "saves"):
        self.slot = slot
        self.save_dir = save_dir
        self.file_path = os.path.join(save_dir, f"save_slot_{slot}.json")
        self.metadata_path = os.path.join(save_dir, f"save_slot_{slot}_meta.json")

    def save(self, world: World, metadata: Dict[str, Any] = None):
        """Save world and metadata"""
        os.makedirs(self.save_dir, exist_ok=True)

        # Save world data
        save_world(world, self.file_path)

        # Save metadata
        meta = metadata or {}
        meta.update({
            "slot": self.slot,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        })

        with open(self.metadata_path, 'w') as f:
            json.dump(meta, f, indent=2)

    def load(self) -> Optional[World]:
        """Load world from save file"""
        if not self.exists():
            return None

        return load_world(self.file_path)

    def get_metadata(self) -> Optional[Dict[str, Any]]:
        """Get save metadata without loading full save"""
        if not os.path.exists(self.metadata_path):
            return None

        with open(self.metadata_path, 'r') as f:
            return json.load(f)

    def exists(self) -> bool:
        """Check if save file exists"""
        return os.path.exists(self.file_path)

    def delete(self):
        """Delete save file"""
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
        if os.path.exists(self.metadata_path):
            os.remove(self.metadata_path)

class SaveManager:
    """Manages multiple save slots"""

    def __init__(self, max_slots: int = 3, save_dir: str = "saves"):
        self.max_slots = max_slots
        self.save_dir = save_dir

    def save(self, slot: int, world: World, metadata: Dict[str, Any] = None):
        """Save to specific slot"""
        if slot < 0 or slot >= self.max_slots:
            raise ValueError(f"Invalid slot {slot}, must be 0-{self.max_slots-1}")

        save_game = SaveGame(slot, self.save_dir)
        save_game.save(world, metadata)

    def load(self, slot: int) -> Optional[World]:
        """Load from specific slot"""
        if slot < 0 or slot >= self.max_slots:
            raise ValueError(f"Invalid slot {slot}, must be 0-{self.max_slots-1}")

        save_game = SaveGame(slot, self.save_dir)
        return save_game.load()

    def delete(self, slot: int):
        """Delete save slot"""
        save_game = SaveGame(slot, self.save_dir)
        save_game.delete()

    def get_all_saves(self) -> Dict[int, Dict[str, Any]]:
        """Get metadata for all save slots"""
        saves = {}
        for slot in range(self.max_slots):
            save_game = SaveGame(slot, self.save_dir)
            if save_game.exists():
                saves[slot] = save_game.get_metadata()
        return saves

    def get_latest_save(self) -> Optional[int]:
        """Get slot number of most recent save"""
        saves = self.get_all_saves()
        if not saves:
            return None

        latest_slot = max(saves.keys(), key=lambda s: saves[s]["timestamp"])
        return latest_slot
```

### Usage

```python
# Create save manager
save_manager = SaveManager(max_slots=3, save_dir="saves")

# Save game
metadata = {
    "player_name": "Hero",
    "level": 5,
    "location": "Forest",
    "playtime": 3600  # seconds
}
save_manager.save(slot=0, world=world, metadata=metadata)

# Load game
loaded_world = save_manager.load(slot=0)
if loaded_world:
    world = loaded_world
    print("Game loaded!")

# List all saves
saves = save_manager.get_all_saves()
for slot, meta in saves.items():
    print(f"Slot {slot}: {meta['player_name']}, Level {meta['level']}")

# Load most recent save
latest_slot = save_manager.get_latest_save()
if latest_slot is not None:
    world = save_manager.load(latest_slot)

# Quick save (auto-save slot)
save_manager.save(slot=0, world=world, metadata={"autosave": True})
```

---

## Dialogue System

RPG-style dialogue with choices and branching.

### Components & Data Structures

```python
from dataclasses import dataclass, field
from typing import List, Optional, Callable

@dataclass
class DialogueLine:
    """A single line of dialogue"""
    speaker: str  # Character name
    text: str
    choices: List['DialogueChoice'] = field(default_factory=list)
    next_id: Optional[str] = None  # ID of next line (if no choices)
    on_show: Optional[Callable] = None  # Callback when shown

@dataclass
class DialogueChoice:
    """A dialogue choice"""
    text: str
    next_id: str  # ID of dialogue line this leads to
    condition: Optional[Callable] = None  # Check if choice available
    on_select: Optional[Callable] = None  # Callback when selected

@dataclass
class Dialogue:
    """Complete dialogue tree"""
    id: str
    lines: Dict[str, DialogueLine] = field(default_factory=dict)
    start_id: str = "start"

    def add_line(self, line_id: str, line: DialogueLine):
        self.lines[line_id] = line

    def get_line(self, line_id: str) -> Optional[DialogueLine]:
        return self.lines.get(line_id)

@dataclass
class DialogueState(Component):
    """Active dialogue state"""
    dialogue: Optional[Dialogue] = None
    current_line_id: Optional[str] = None
    is_active: bool = False
    speaker_entity_id: Optional[str] = None

    def start(self, dialogue: Dialogue, speaker_entity_id: str = None):
        """Start a dialogue"""
        self.dialogue = dialogue
        self.current_line_id = dialogue.start_id
        self.is_active = True
        self.speaker_entity_id = speaker_entity_id

    def advance(self, choice_index: int = None):
        """Advance to next line"""
        if not self.is_active or not self.dialogue:
            return

        current_line = self.dialogue.get_line(self.current_line_id)
        if not current_line:
            self.end()
            return

        # Handle choices
        if current_line.choices:
            if choice_index is not None and 0 <= choice_index < len(current_line.choices):
                choice = current_line.choices[choice_index]

                # Execute callback
                if choice.on_select:
                    choice.on_select()

                self.current_line_id = choice.next_id
            else:
                return  # Waiting for choice
        else:
            # No choices, auto-advance
            self.current_line_id = current_line.next_id

        # Check if dialogue ended
        if self.current_line_id is None:
            self.end()

    def end(self):
        """End dialogue"""
        self.is_active = False
        self.dialogue = None
        self.current_line_id = None
        self.speaker_entity_id = None

    def get_current_line(self) -> Optional[DialogueLine]:
        """Get current dialogue line"""
        if self.dialogue and self.current_line_id:
            return self.dialogue.get_line(self.current_line_id)
        return None
```

### System

```python
import pygame

class DialogueSystem(System):
    """Manages dialogue flow"""

    def __init__(self):
        super().__init__()
        self.priority = 5

    def update(self, world: World, delta_time: float):
        # Handle input for active dialogues
        for entity in world.get_entities_with_component(DialogueState):
            dialogue_state = entity.get_component(DialogueState)

            if dialogue_state.is_active:
                self._handle_dialogue_input(dialogue_state)

    def _handle_dialogue_input(self, dialogue_state: DialogueState):
        """Handle keyboard input for dialogue"""
        keys = pygame.key.get_pressed()

        current_line = dialogue_state.get_current_line()
        if not current_line:
            return

        # If there are choices, handle number keys
        if current_line.choices:
            for i in range(min(len(current_line.choices), 9)):
                if pygame.key.get_pressed()[pygame.K_1 + i]:
                    dialogue_state.advance(choice_index=i)
                    break
        # Otherwise, spacebar/enter advances
        elif keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
            dialogue_state.advance()
```

### Rendering

```python
class DialogueRenderSystem(System):
    """Renders dialogue UI"""

    def __init__(self, screen: pygame.Surface, font: pygame.font.Font):
        super().__init__()
        self.screen = screen
        self.font = font
        self.priority = 200  # Render on top

    def update(self, world: World, delta_time: float):
        for entity in world.get_entities_with_component(DialogueState):
            dialogue_state = entity.get_component(DialogueState)

            if dialogue_state.is_active:
                self._render_dialogue(dialogue_state)

    def _render_dialogue(self, dialogue_state: DialogueState):
        """Render dialogue box"""
        current_line = dialogue_state.get_current_line()
        if not current_line:
            return

        # Draw dialogue box
        box_rect = pygame.Rect(50, 400, 700, 150)
        pygame.draw.rect(self.screen, (20, 20, 40), box_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), box_rect, 2)

        # Draw speaker name
        speaker_text = self.font.render(current_line.speaker, True, (255, 200, 0))
        self.screen.blit(speaker_text, (60, 410))

        # Draw dialogue text
        text_surface = self.font.render(current_line.text, True, (255, 255, 255))
        self.screen.blit(text_surface, (60, 440))

        # Draw choices
        if current_line.choices:
            y_offset = 480
            for i, choice in enumerate(current_line.choices):
                # Check if choice is available
                if choice.condition and not choice.condition():
                    continue

                choice_text = f"{i+1}. {choice.text}"
                choice_surface = self.font.render(choice_text, True, (200, 200, 200))
                self.screen.blit(choice_surface, (70, y_offset))
                y_offset += 25
        else:
            # Show "Press SPACE to continue"
            hint_text = self.font.render("Press SPACE to continue", True, (150, 150, 150))
            self.screen.blit(hint_text, (500, 520))
```

### Usage

```python
# Create dialogue
dialogue = Dialogue(id="shopkeeper_greeting")

def give_gold():
    # Award player 10 gold
    pass

dialogue.add_line("start", DialogueLine(
    speaker="Shopkeeper",
    text="Welcome to my shop! What brings you here?",
    choices=[
        DialogueChoice("I'd like to buy something", next_id="shop"),
        DialogueChoice("Just looking around", next_id="browse"),
        DialogueChoice("Do you have any quests?", next_id="quest")
    ]
))

dialogue.add_line("shop", DialogueLine(
    speaker="Shopkeeper",
    text="Take a look at my wares!",
    next_id=None  # Ends dialogue
))

dialogue.add_line("quest", DialogueLine(
    speaker="Shopkeeper",
    text="Actually, yes! Here's 10 gold as a reward.",
    on_show=give_gold,
    next_id="end"
))

# Add dialogue state to UI entity
ui_entity = world.create_entity()
dialogue_state = DialogueState()
dialogue_state.start(dialogue, speaker_entity_id=shopkeeper.id)
ui_entity.add_component(dialogue_state)

# Add systems
world.add_system(DialogueSystem())
world.add_system(DialogueRenderSystem(screen, font))
```

---

## Pathfinding

A* pathfinding with navmesh support.

```python
import heapq
from typing import List, Tuple, Set, Optional
from neonworks.core.ecs import Navmesh, GridPosition, Component
from dataclasses import dataclass, field

@dataclass
class PathFollower(Component):
    """Component for entities that follow paths"""
    path: List[Tuple[int, int]] = field(default_factory=list)
    current_waypoint: int = 0
    speed: float = 2.0  # Grid cells per second
    reached_destination: bool = True

def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
    """Manhattan distance heuristic"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def find_path(navmesh: Navmesh, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
    """A* pathfinding algorithm"""

    if not navmesh.is_walkable(*start) or not navmesh.is_walkable(*goal):
        return None

    # Priority queue: (f_score, counter, position, path)
    counter = 0
    open_set = [(0, counter, start, [start])]
    visited: Set[Tuple[int, int]] = set()

    while open_set:
        f_score, _, current, path = heapq.heappop(open_set)

        if current == goal:
            return path

        if current in visited:
            continue

        visited.add(current)

        # Check neighbors (4-directional)
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            neighbor = (current[0] + dx, current[1] + dy)

            if neighbor in visited:
                continue

            if not navmesh.is_walkable(*neighbor):
                continue

            # Calculate scores
            g_score = len(path)  # Distance from start
            h_score = heuristic(neighbor, goal)
            f_score = g_score + h_score + navmesh.get_cost(*neighbor)

            new_path = path + [neighbor]
            counter += 1
            heapq.heappush(open_set, (f_score, counter, neighbor, new_path))

    return None  # No path found

class PathfindingSystem(System):
    """Updates entities following paths"""

    def __init__(self, navmesh: Navmesh):
        super().__init__()
        self.navmesh = navmesh
        self.priority = 15

    def update(self, world: World, delta_time: float):
        for entity in world.get_entities_with_components(GridPosition, PathFollower):
            grid_pos = entity.get_component(GridPosition)
            path_follower = entity.get_component(PathFollower)

            if path_follower.reached_destination:
                continue

            if not path_follower.path:
                path_follower.reached_destination = True
                continue

            # Get current target waypoint
            if path_follower.current_waypoint >= len(path_follower.path):
                path_follower.reached_destination = True
                continue

            target = path_follower.path[path_follower.current_waypoint]

            # Check if reached waypoint
            if (grid_pos.grid_x, grid_pos.grid_y) == target:
                path_follower.current_waypoint += 1
                if path_follower.current_waypoint >= len(path_follower.path):
                    path_follower.reached_destination = True
            else:
                # Move towards waypoint (instant grid movement)
                # For smooth movement, interpolate Transform component
                grid_pos.grid_x = target[0]
                grid_pos.grid_y = target[1]

    def request_path(self, entity: Entity, goal: Tuple[int, int]):
        """Request a path for an entity"""
        grid_pos = entity.get_component(GridPosition)
        path_follower = entity.get_component(PathFollower)

        if not grid_pos or not path_follower:
            return

        start = (grid_pos.grid_x, grid_pos.grid_y)
        path = find_path(self.navmesh, start, goal)

        if path:
            path_follower.path = path
            path_follower.current_waypoint = 1  # Skip first (current position)
            path_follower.reached_destination = False
```

### Usage

```python
# Create navmesh
navmesh = Navmesh()
for x in range(20):
    for y in range(20):
        if not is_wall(x, y):  # Your logic
            navmesh.walkable_cells.add((x, y))

# Create entity with pathfinding
enemy = world.create_entity()
enemy.add_component(GridPosition(grid_x=0, grid_y=0))
enemy.add_component(PathFollower())

# Add system
pathfinding_system = PathfindingSystem(navmesh)
world.add_system(pathfinding_system)

# Request path to player
player_grid = player.get_component(GridPosition)
pathfinding_system.request_path(enemy, (player_grid.grid_x, player_grid.grid_y))
```

---

## Camera Controls

Smooth camera with follow, zoom, and shake effects.

```python
from dataclasses import dataclass
import pygame
import math
import random

@dataclass
class Camera(Component):
    """Camera component"""
    x: float = 0.0
    y: float = 0.0
    width: int = 800
    height: int = 600
    zoom: float = 1.0

    # Follow settings
    follow_target_id: Optional[str] = None
    follow_smoothing: float = 5.0  # Higher = less smooth
    follow_offset_x: float = 0.0
    follow_offset_y: float = 0.0

    # Bounds
    min_x: Optional[float] = None
    max_x: Optional[float] = None
    min_y: Optional[float] = None
    max_y: Optional[float] = None

    # Shake
    shake_intensity: float = 0.0
    shake_duration: float = 0.0
    shake_offset_x: float = 0.0
    shake_offset_y: float = 0.0

    def world_to_screen(self, world_x: float, world_y: float) -> Tuple[float, float]:
        """Convert world coordinates to screen coordinates"""
        screen_x = (world_x - self.x + self.shake_offset_x) * self.zoom + self.width / 2
        screen_y = (world_y - self.y + self.shake_offset_y) * self.zoom + self.height / 2
        return screen_x, screen_y

    def screen_to_world(self, screen_x: float, screen_y: float) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates"""
        world_x = (screen_x - self.width / 2) / self.zoom + self.x - self.shake_offset_x
        world_y = (screen_y - self.height / 2) / self.zoom + self.y - self.shake_offset_y
        return world_x, world_y

    def get_viewport_rect(self) -> pygame.Rect:
        """Get world-space rectangle of visible area"""
        half_width = (self.width / 2) / self.zoom
        half_height = (self.height / 2) / self.zoom
        return pygame.Rect(
            self.x - half_width,
            self.y - half_height,
            self.width / self.zoom,
            self.height / self.zoom
        )

class CameraSystem(System):
    """Updates camera position and effects"""

    def __init__(self):
        super().__init__()
        self.priority = 5

    def update(self, world: World, delta_time: float):
        for entity in world.get_entities_with_component(Camera):
            camera = entity.get_component(Camera)

            # Update follow
            if camera.follow_target_id:
                self._update_follow(world, camera, delta_time)

            # Update shake
            if camera.shake_duration > 0:
                self._update_shake(camera, delta_time)

            # Apply bounds
            self._apply_bounds(camera)

    def _update_follow(self, world: World, camera: Camera, delta_time: float):
        """Smooth camera follow"""
        target = world.get_entity(camera.follow_target_id)
        if not target:
            camera.follow_target_id = None
            return

        transform = target.get_component(Transform)
        if not transform:
            return

        # Calculate target position
        target_x = transform.x + camera.follow_offset_x
        target_y = transform.y + camera.follow_offset_y

        # Smooth interpolation
        lerp_speed = camera.follow_smoothing * delta_time
        camera.x += (target_x - camera.x) * lerp_speed
        camera.y += (target_y - camera.y) * lerp_speed

    def _update_shake(self, camera: Camera, delta_time: float):
        """Update camera shake effect"""
        camera.shake_duration -= delta_time

        if camera.shake_duration <= 0:
            camera.shake_offset_x = 0
            camera.shake_offset_y = 0
            camera.shake_intensity = 0
        else:
            # Random shake offset
            angle = random.uniform(0, math.pi * 2)
            camera.shake_offset_x = math.cos(angle) * camera.shake_intensity
            camera.shake_offset_y = math.sin(angle) * camera.shake_intensity

    def _apply_bounds(self, camera: Camera):
        """Keep camera within bounds"""
        if camera.min_x is not None:
            camera.x = max(camera.x, camera.min_x)
        if camera.max_x is not None:
            camera.x = min(camera.x, camera.max_x)
        if camera.min_y is not None:
            camera.y = max(camera.y, camera.min_y)
        if camera.max_y is not None:
            camera.y = min(camera.y, camera.max_y)

    def shake_camera(self, camera: Camera, intensity: float, duration: float):
        """Trigger camera shake"""
        camera.shake_intensity = intensity
        camera.shake_duration = duration
```

### Usage

```python
# Create camera entity
camera_entity = world.create_entity()
camera = Camera(width=800, height=600)
camera.follow_target_id = player.id  # Follow player
camera.follow_smoothing = 5.0
camera.min_x = 0
camera.max_x = 2000
camera.min_y = 0
camera.max_y = 1500
camera_entity.add_component(camera)

# Add system
camera_system = CameraSystem()
world.add_system(camera_system)

# Shake camera on explosion
camera_system.shake_camera(camera, intensity=10, duration=0.5)

# Zoom in/out
camera.zoom = 1.5  # 150% zoom

# Convert coordinates
world_x, world_y = camera.screen_to_world(mouse_x, mouse_y)
screen_x, screen_y = camera.world_to_screen(entity_x, entity_y)
```

---

## Particle Effects

Reusable particle system for explosions, trails, etc.

```python
from dataclasses import dataclass
import random
import math

@dataclass
class Particle(Component):
    """Single particle"""
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    lifetime: float = 1.0
    max_lifetime: float = 1.0
    size: float = 5.0
    color: Tuple[int, int, int, int] = (255, 255, 255, 255)
    fade: bool = True
    gravity: float = 0.0
    active: bool = True

@dataclass
class ParticleEmitter(Component):
    """Emits particles"""
    emit_rate: float = 10.0  # Particles per second
    emit_timer: float = 0.0
    particle_lifetime: float = 1.0
    particle_speed: Tuple[float, float] = (50.0, 100.0)  # Min, max
    particle_size: Tuple[float, float] = (2.0, 5.0)  # Min, max
    particle_color: Tuple[int, int, int, int] = (255, 255, 255, 255)
    emit_angle: float = 0.0  # Radians
    emit_spread: float = math.pi * 2  # Full circle
    gravity: float = 0.0
    max_particles: int = 100
    one_shot: bool = False  # Emit once then stop
    active: bool = True

class ParticleSystem(System):
    """Manages particle lifecycle"""

    def __init__(self):
        super().__init__()
        self.priority = 20
        self.particle_pool = []

    def update(self, world: World, delta_time: float):
        # Update existing particles
        self._update_particles(world, delta_time)

        # Emit new particles
        self._update_emitters(world, delta_time)

    def _update_particles(self, world: World, delta_time: float):
        """Update particle positions and lifetime"""
        for entity in world.get_entities_with_components(Transform, Particle):
            transform = entity.get_component(Transform)
            particle = entity.get_component(Particle)

            if not particle.active:
                continue

            # Update lifetime
            particle.lifetime -= delta_time
            if particle.lifetime <= 0:
                particle.active = False
                continue

            # Update position
            transform.x += particle.velocity_x * delta_time
            transform.y += particle.velocity_y * delta_time

            # Apply gravity
            particle.velocity_y += particle.gravity * delta_time

            # Update fade
            if particle.fade:
                alpha = int(255 * (particle.lifetime / particle.max_lifetime))
                particle.color = (*particle.color[:3], alpha)

    def _update_emitters(self, world: World, delta_time: float):
        """Emit particles from emitters"""
        for entity in world.get_entities_with_components(Transform, ParticleEmitter):
            transform = entity.get_component(Transform)
            emitter = entity.get_component(ParticleEmitter)

            if not emitter.active:
                continue

            emitter.emit_timer += delta_time
            particles_to_emit = int(emitter.emit_timer * emitter.emit_rate)
            emitter.emit_timer -= particles_to_emit / emitter.emit_rate

            # Count active particles from this emitter
            active_count = len([e for e in self.particle_pool
                              if e.get_component(Particle).active])

            for _ in range(particles_to_emit):
                if active_count >= emitter.max_particles:
                    break

                self._emit_particle(world, transform, emitter)
                active_count += 1

            if emitter.one_shot and particles_to_emit > 0:
                emitter.active = False

    def _emit_particle(self, world: World, transform: Transform, emitter: ParticleEmitter):
        """Emit a single particle"""
        # Get or create particle entity
        particle_entity = self._get_pooled_particle(world)

        # Set position
        particle_transform = particle_entity.get_component(Transform)
        particle_transform.x = transform.x
        particle_transform.y = transform.y

        # Set properties
        particle = particle_entity.get_component(Particle)
        particle.active = True

        # Random speed
        speed = random.uniform(*emitter.particle_speed)

        # Random angle within spread
        angle = emitter.emit_angle + random.uniform(-emitter.emit_spread/2, emitter.emit_spread/2)
        particle.velocity_x = math.cos(angle) * speed
        particle.velocity_y = math.sin(angle) * speed

        # Random size
        particle.size = random.uniform(*emitter.particle_size)

        # Other properties
        particle.lifetime = emitter.particle_lifetime
        particle.max_lifetime = emitter.particle_lifetime
        particle.color = emitter.particle_color
        particle.gravity = emitter.gravity

    def _get_pooled_particle(self, world: World) -> Entity:
        """Get inactive particle from pool or create new one"""
        for entity in self.particle_pool:
            particle = entity.get_component(Particle)
            if not particle.active:
                return entity

        # Create new particle
        entity = world.create_entity()
        entity.add_component(Transform())
        entity.add_component(Particle())
        self.particle_pool.append(entity)
        return entity

class ParticleRenderSystem(System):
    """Renders particles"""

    def __init__(self, screen: pygame.Surface):
        super().__init__()
        self.screen = screen
        self.priority = 90

    def update(self, world: World, delta_time: float):
        for entity in world.get_entities_with_components(Transform, Particle):
            transform = entity.get_component(Transform)
            particle = entity.get_component(Particle)

            if not particle.active:
                continue

            # Draw circle
            pygame.draw.circle(
                self.screen,
                particle.color[:3],
                (int(transform.x), int(transform.y)),
                int(particle.size)
            )
```

### Usage

```python
# Create explosion emitter
explosion = world.create_entity()
explosion.add_component(Transform(x=400, y=300))
explosion.add_component(ParticleEmitter(
    emit_rate=200,
    particle_lifetime=0.5,
    particle_speed=(100, 200),
    particle_size=(3, 8),
    particle_color=(255, 128, 0, 255),  # Orange
    emit_spread=math.pi * 2,  # All directions
    gravity=200,
    max_particles=50,
    one_shot=True  # Emit once
))

# Create continuous fire trail
trail = world.create_entity()
trail.add_component(Transform(x=player_x, y=player_y))
trail.add_component(ParticleEmitter(
    emit_rate=30,
    particle_lifetime=0.3,
    particle_speed=(10, 30),
    particle_size=(2, 4),
    particle_color=(255, 100, 0, 255),
    emit_angle=math.pi,  # Behind
    emit_spread=math.pi / 4,
    gravity=0,
    max_particles=100,
    one_shot=False  # Continuous
))

# Add systems
particle_system = ParticleSystem()
world.add_system(particle_system)
world.add_system(ParticleRenderSystem(screen))
```

---

## Combat System

Turn-based combat with damage calculation.

```python
from neonworks.core.events import get_event_manager, EventType, Event
from dataclasses import dataclass
from typing import Optional
import random

@dataclass
class CombatStats(Component):
    """Combat statistics"""
    attack: int = 10
    defense: int = 5
    accuracy: float = 0.9  # 90% hit chance
    critical_chance: float = 0.1  # 10% crit chance
    critical_multiplier: float = 2.0

@dataclass
class CombatAction(Component):
    """Pending combat action"""
    action_type: str = "attack"  # attack, defend, skill, item
    target_id: Optional[str] = None
    skill_id: Optional[str] = None
    item_id: Optional[str] = None

class CombatSystem(System):
    """Handles combat resolution"""

    def __init__(self):
        super().__init__()
        self.event_manager = get_event_manager()
        self.priority = 30

    def execute_action(self, attacker: Entity, target: Entity, action: CombatAction):
        """Execute a combat action"""
        if action.action_type == "attack":
            self._execute_attack(attacker, target)
        elif action.action_type == "defend":
            self._execute_defend(attacker)
        # Add more action types as needed

    def _execute_attack(self, attacker: Entity, target: Entity):
        """Execute basic attack"""
        attacker_stats = attacker.get_component(CombatStats)
        target_health = target.get_component(Health)
        target_stats = target.get_component(CombatStats)

        if not all([attacker_stats, target_health, target_stats]):
            return

        # Hit check
        hit_roll = random.random()
        if hit_roll > attacker_stats.accuracy:
            self._emit_combat_event("miss", attacker.id, target.id, 0)
            return

        # Calculate base damage
        damage = max(1, attacker_stats.attack - target_stats.defense // 2)

        # Critical hit check
        crit_roll = random.random()
        is_critical = crit_roll < attacker_stats.critical_chance
        if is_critical:
            damage = int(damage * attacker_stats.critical_multiplier)

        # Apply damage
        target_health.current -= damage
        target_health.current = max(0, target_health.current)

        # Emit events
        self._emit_combat_event(
            "critical" if is_critical else "hit",
            attacker.id,
            target.id,
            damage
        )

        if target_health.current <= 0:
            self.event_manager.emit(Event(EventType.UNIT_DIED, {
                "entity_id": target.id,
                "killer_id": attacker.id
            }))

    def _execute_defend(self, defender: Entity):
        """Execute defend action"""
        stats = defender.get_component(CombatStats)
        if stats:
            # Temporarily boost defense (remove next turn)
            stats.defense = int(stats.defense * 1.5)

    def _emit_combat_event(self, result: str, attacker_id: str, target_id: str, damage: int):
        """Emit combat result event"""
        self.event_manager.emit(Event(EventType.DAMAGE_DEALT, {
            "result": result,
            "attacker_id": attacker_id,
            "target_id": target_id,
            "damage": damage
        }))
```

### Usage

```python
# Create combatants
player = world.create_entity()
player.add_component(Health(current=100, maximum=100))
player.add_component(CombatStats(attack=15, defense=8, accuracy=0.9))
player.add_tag("player")

enemy = world.create_entity()
enemy.add_component(Health(current=50, maximum=50))
enemy.add_component(CombatStats(attack=10, defense=5, accuracy=0.8))
enemy.add_tag("enemy")

# Add combat system
combat_system = CombatSystem()
world.add_system(combat_system)

# Execute attack
action = CombatAction(action_type="attack", target_id=enemy.id)
combat_system.execute_action(player, enemy, action)
```

---

These recipes provide complete, working implementations of common game features. Copy and customize them for your NeonWorks game!

For more examples, see:
- [Tutorial Series](tutorials/) - Step-by-step guides
- [Example Projects](../examples/) - Complete games
- [API Reference](api_reference.md) - Full class documentation
