# Tutorial 4: Save/Load System

Learn to implement save/load functionality so players can persist their game progress.

## What You'll Learn

- Serializing game state
- Saving to JSON files
- Loading saved games
- Multiple save slots
- Auto-save functionality
- Save game metadata

## Prerequisites

- Completed [Tutorial 3: Creating UI](tutorial_03_creating_ui.md)
- OR any NeonWorks project you want to add saving to

## Overview

We'll implement a complete save/load system with:
- Manual save/load via menu
- Auto-save on quit
- Multiple save slots (3 slots)
- Save metadata (timestamp, playtime, location)

## Step 1: Save System Components

Create `scripts/save_components.py`:

```python
"""Save system components."""

from engine.core.ecs import Component
from dataclasses import dataclass, field
from typing import Dict, Any
from datetime import datetime

@dataclass
class SaveableData(Component):
    """Marks entity as saveable with custom data."""
    save_id: str = ""  # Unique identifier for loading
    custom_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GameProgress(Component):
    """Tracks overall game progress."""
    playtime: float = 0.0  # Seconds
    current_level: str = "main"
    checkpoints_reached: list = field(default_factory=list)
    achievements: list = field(default_factory=list)

@dataclass
class SaveMetadata:
    """Save file metadata."""
    slot: int
    timestamp: str
    playtime: float
    player_level: int
    location: str
    screenshot_path: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "slot": self.slot,
            "timestamp": self.timestamp,
            "playtime": self.playtime,
            "player_level": self.player_level,
            "location": self.location,
            "screenshot_path": self.screenshot_path
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SaveMetadata':
        return cls(**data)
```

## Step 2: Save Manager

Create `scripts/save_manager.py`:

```python
"""Save/load manager."""

import json
import os
from datetime import datetime
from typing import Optional, Dict, Any
from engine.core.ecs import World, Entity, Component, Transform
from engine.core.serialization import save_world, load_world
from save_components import SaveMetadata, GameProgress
from components import Player

class SaveManager:
    """Manages game saves."""

    def __init__(self, save_dir: str = "saves", max_slots: int = 3):
        self.save_dir = save_dir
        self.max_slots = max_slots
        os.makedirs(save_dir, exist_ok=True)

    def save_game(self, world: World, slot: int, description: str = ""):
        """Save game to slot."""
        if slot < 0 or slot >= self.max_slots:
            raise ValueError(f"Invalid slot {slot}")

        # Get game progress
        progress = self._get_game_progress(world)

        # Create metadata
        metadata = SaveMetadata(
            slot=slot,
            timestamp=datetime.now().isoformat(),
            playtime=progress.playtime if progress else 0.0,
            player_level=self._get_player_level(world),
            location=progress.current_level if progress else "unknown"
        )

        # Save world data
        world_file = os.path.join(self.save_dir, f"save_{slot}.json")
        save_world(world, world_file)

        # Save metadata
        meta_file = os.path.join(self.save_dir, f"save_{slot}_meta.json")
        with open(meta_file, 'w') as f:
            json.dump(metadata.to_dict(), f, indent=2)

        print(f"Game saved to slot {slot}")
        return True

    def load_game(self, slot: int) -> Optional[World]:
        """Load game from slot."""
        if slot < 0 or slot >= self.max_slots:
            raise ValueError(f"Invalid slot {slot}")

        world_file = os.path.join(self.save_dir, f"save_{slot}.json")

        if not os.path.exists(world_file):
            print(f"No save in slot {slot}")
            return None

        # Load world
        world = load_world(world_file)
        print(f"Game loaded from slot {slot}")
        return world

    def delete_save(self, slot: int):
        """Delete save slot."""
        world_file = os.path.join(self.save_dir, f"save_{slot}.json")
        meta_file = os.path.join(self.save_dir, f"save_{slot}_meta.json")

        if os.path.exists(world_file):
            os.remove(world_file)
        if os.path.exists(meta_file):
            os.remove(meta_file)

        print(f"Deleted save slot {slot}")

    def get_save_metadata(self, slot: int) -> Optional[SaveMetadata]:
        """Get metadata for save slot."""
        meta_file = os.path.join(self.save_dir, f"save_{slot}_meta.json")

        if not os.path.exists(meta_file):
            return None

        with open(meta_file, 'r') as f:
            data = json.load(f)

        return SaveMetadata.from_dict(data)

    def get_all_saves(self) -> Dict[int, SaveMetadata]:
        """Get metadata for all save slots."""
        saves = {}
        for slot in range(self.max_slots):
            metadata = self.get_save_metadata(slot)
            if metadata:
                saves[slot] = metadata
        return saves

    def save_exists(self, slot: int) -> bool:
        """Check if save exists in slot."""
        world_file = os.path.join(self.save_dir, f"save_{slot}.json")
        return os.path.exists(world_file)

    def get_latest_save_slot(self) -> Optional[int]:
        """Get most recent save slot."""
        saves = self.get_all_saves()
        if not saves:
            return None

        latest = max(saves.items(), key=lambda x: x[1].timestamp)
        return latest[0]

    def _get_game_progress(self, world: World) -> Optional[GameProgress]:
        """Get game progress component."""
        entities = world.get_entities_with_component(GameProgress)
        if entities:
            return entities[0].get_component(GameProgress)
        return None

    def _get_player_level(self, world: World) -> int:
        """Get player level (or score)."""
        players = world.get_entities_with_component(Player)
        if players:
            player = players[0].get_component(Player)
            return player.score // 100  # Example: level = score / 100
        return 1
```

## Step 3: Auto-Save System

Create `scripts/autosave_system.py`:

```python
"""Auto-save system."""

from engine.core.ecs import System, World
from save_manager import SaveManager

class AutoSaveSystem(System):
    """Automatically saves game periodically."""

    def __init__(self, save_manager: SaveManager, interval: float = 300.0):
        """
        Args:
            save_manager: Save manager instance
            interval: Auto-save interval in seconds (default: 5 minutes)
        """
        super().__init__()
        self.save_manager = save_manager
        self.interval = interval
        self.timer = 0.0
        self.auto_save_slot = 0  # Use slot 0 for auto-save
        self.priority = 200  # Run late

    def update(self, world: World, delta_time: float):
        """Update auto-save timer."""
        self.timer += delta_time

        if self.timer >= self.interval:
            self.perform_autosave(world)
            self.timer = 0.0

    def perform_autosave(self, world: World):
        """Perform auto-save."""
        try:
            self.save_manager.save_game(world, self.auto_save_slot, "Auto-save")
            print("Auto-saved!")
        except Exception as e:
            print(f"Auto-save failed: {e}")

class PlaytimeTrackerSystem(System):
    """Tracks total playtime."""

    def __init__(self):
        super().__init__()
        self.priority = 1

    def update(self, world: World, delta_time: float):
        """Update playtime."""
        from save_components import GameProgress

        progress_entities = world.get_entities_with_component(GameProgress)
        if progress_entities:
            progress = progress_entities[0].get_component(GameProgress)
            progress.playtime += delta_time
```

## Step 4: Save/Load UI

Add to `scripts/ui_systems.py`:

```python
# Add to ScreenManager class:

def show_save_menu(self):
    """Show save slot selection."""
    from save_manager import SaveManager

    self._clear_ui()

    # Title
    title = self.world.create_entity()
    title.add_component(UIElement(layer=10))
    title.add_component(Text(
        x=400, y=80,
        text="Save Game",
        font_size=48,
        centered=True
    ))

    # Save slots
    save_manager = SaveManager()

    for slot in range(3):
        y_pos = 150 + (slot * 100)

        # Check if save exists
        metadata = save_manager.get_save_metadata(slot)

        if metadata:
            # Existing save
            button_text = f"Slot {slot + 1}: {metadata.location}"
            subtext = f"Level {metadata.player_level} - {metadata.timestamp[:10]}"
        else:
            # Empty slot
            button_text = f"Slot {slot + 1}: Empty"
            subtext = "Click to save"

        # Save button
        btn = self.world.create_entity()
        btn.add_component(UIElement(layer=10))
        btn.add_component(Button(
            x=200, y=y_pos,
            width=400, height=70,
            text=button_text,
            on_click=lambda s=slot: self._save_to_slot(s)
        ))

        # Subtext
        if metadata:
            sub = self.world.create_entity()
            sub.add_component(UIElement(layer=10))
            sub.add_component(Text(
                x=220, y=y_pos + 40,
                text=subtext,
                font_size=20,
                color=(180, 180, 180)
            ))

    # Back button
    back_btn = self.world.create_entity()
    back_btn.add_component(UIElement(layer=10))
    back_btn.add_component(Button(
        x=300, y=500,
        width=200, height=50,
        text="Back",
        on_click=self.show_pause_menu
    ))

def show_load_menu(self):
    """Show load slot selection."""
    from save_manager import SaveManager

    self._clear_ui()

    # Title
    title = self.world.create_entity()
    title.add_component(UIElement(layer=10))
    title.add_component(Text(
        x=400, y=80,
        text="Load Game",
        font_size=48,
        centered=True
    ))

    save_manager = SaveManager()

    for slot in range(3):
        y_pos = 150 + (slot * 100)
        metadata = save_manager.get_save_metadata(slot)

        if metadata:
            button_text = f"Slot {slot + 1}: {metadata.location}"
            subtext = f"Level {metadata.player_level} - {metadata.timestamp[:10]}"

            # Load button
            btn = self.world.create_entity()
            btn.add_component(UIElement(layer=10))
            btn.add_component(Button(
                x=200, y=y_pos,
                width=400, height=70,
                text=button_text,
                on_click=lambda s=slot: self._load_from_slot(s)
            ))

            # Subtext
            sub = self.world.create_entity()
            sub.add_component(UIElement(layer=10))
            sub.add_component(Text(
                x=220, y=y_pos + 40,
                text=subtext,
                font_size=20,
                color=(180, 180, 180)
            ))
        else:
            # Empty slot indicator
            empty = self.world.create_entity()
            empty.add_component(UIElement(layer=10))
            empty.add_component(Text(
                x=400, y=y_pos + 20,
                text=f"Slot {slot + 1}: Empty",
                font_size=32,
                color=(100, 100, 100),
                centered=True
            ))

    # Back button
    back_btn = self.world.create_entity()
    back_btn.add_component(UIElement(layer=10))
    back_btn.add_component(Button(
        x=300, y=500,
        width=200, height=50,
        text="Back",
        on_click=self.show_main_menu
    ))

def _save_to_slot(self, slot: int):
    """Save game to slot."""
    from save_manager import SaveManager

    save_manager = SaveManager()
    save_manager.save_game(self.world, slot)
    self.show_pause_menu()

def _load_from_slot(self, slot: int):
    """Load game from slot."""
    from save_manager import SaveManager

    save_manager = SaveManager()
    loaded_world = save_manager.load_game(slot)

    if loaded_world:
        # Replace current world
        # This requires storing world reference
        self.game_state.current_screen = "playing"
        print("Game loaded successfully!")
        # Note: Full implementation requires world swapping
    else:
        print("Failed to load game")
```

## Step 5: Update Main Menu

Add save/load buttons to main menu in `_create_main_menu()`:

```python
def _create_main_menu(self):
    """Create main menu with save/load options."""
    # ... existing title code ...

    # Start button
    start_btn = self.world.create_entity()
    start_btn.add_component(UIElement(layer=1))
    start_btn.add_component(Button(
        x=300, y=250,
        width=200, height=50,
        text="New Game",
        on_click=lambda: [self.start_game(), self._create_game()]
    ))

    # Load button
    load_btn = self.world.create_entity()
    load_btn.add_component(UIElement(layer=1))
    load_btn.add_component(Button(
        x=300, y=320,
        width=200, height=50,
        text="Load Game",
        on_click=self.show_load_menu
    ))

    # Quit button
    quit_btn = self.world.create_entity()
    quit_btn.add_component(UIElement(layer=1))
    quit_btn.add_component(Button(
        x=300, y=390,
        width=200, height=50,
        text="Quit",
        on_click=lambda: pygame.event.post(pygame.event.Event(pygame.QUIT))
    ))
```

## Step 6: Add Auto-Save on Quit

Update `main.py`:

```python
def main():
    """Main with auto-save."""
    pygame.init()

    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Coin Collector")

    world = World()

    # ... existing setup ...

    # Add auto-save system
    from save_manager import SaveManager
    from autosave_system import AutoSaveSystem, PlaytimeTrackerSystem

    save_manager = SaveManager()
    world.add_system(PlaytimeTrackerSystem())
    world.add_system(AutoSaveSystem(save_manager, interval=60.0))  # Auto-save every minute

    # ... game loop ...

    # On quit, perform final auto-save
    print("Saving game before quit...")
    try:
        save_manager.save_game(world, slot=0)
        print("Game saved!")
    except:
        print("Failed to save game")

    pygame.quit()
```

## Testing

```bash
python main.py
```

Try:
1. Play for a bit, collect coins
2. Press ESC → Save Game
3. Quit and restart
4. Load your save!

## Key Concepts

### Serialization

NeonWorks automatically serializes:
- All entities
- All components
- Component data

Systems are recreated on load.

### Save Metadata

Separate metadata file stores:
- Timestamp
- Playtime
- Player level
- Location

Fast to read without loading full save.

### Auto-Save

Periodic auto-save prevents data loss:
- Every N minutes
- On game quit
- On checkpoint reached

## Challenges

### Easy
1. Change auto-save interval
2. Add "Continue" button (loads latest save)
3. Show save time in load menu

### Medium
1. **Quick save**: Press F5 to save instantly
2. **Save confirmation**: "Save successful!" message
3. **Delete saves**: Add delete button to load menu
4. **Cloud saves**: Upload to server

### Hard
1. **Save compression**: Compress save files
2. **Save encryption**: Encrypt save data
3. **Save versioning**: Handle old save formats
4. **Incremental saves**: Only save changed data

## Summary

✅ `save_world()` and `load_world()` for persistence
✅ Multiple save slots for flexibility
✅ Metadata for quick save info
✅ Auto-save prevents data loss
✅ UI integration for player control

Congratulations! You've completed the tutorial series! 🎉

## Next Steps

Explore more advanced topics:
- [Code Recipes](../RECIPES.md) - Copy-paste solutions
- [Event System Guide](../EVENT_SYSTEM.md) - Event-driven architecture
- [Example Projects](../../examples/) - Complete games
- [Common Pitfalls](../COMMON_PITFALLS.md) - Avoid mistakes

Keep building amazing games with NeonWorks! 🎮✨
