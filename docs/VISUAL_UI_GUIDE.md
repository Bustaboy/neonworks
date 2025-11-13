# NeonWorks Visual UI Systems Guide

Complete guide to using all visual UI systems in the NeonWorks engine.

## Overview

NeonWorks provides a comprehensive suite of visual UI systems that allow you to manage every aspect of your game through intuitive interfaces. Everything can be controlled visually - no code editing required for most tasks!

## UI Systems

### 1. Game HUD (`GameHUD`)
**Location:** `engine/ui/game_hud.py`

The main in-game heads-up display that shows all essential gameplay information.

**Features:**
- **Performance Stats**: FPS, entity count, system count
- **Turn Information**: Current round, turn order, action points
- **Resource Display**: All resources with color-coded indicators
- **Survival Stats**: Health, hunger, thirst, energy bars
- **Building Info**: List of active buildings
- **Entity Inspector**: Detailed info about selected entities

**Keybind:** F10

**Usage:**
```python
from engine.ui.game_hud import GameHUD

hud = GameHUD(screen)
hud.render(world, fps=60.0)
hud.set_selected_entity(entity_id)
```

---

### 2. Building UI (`BuildingUI`)
**Location:** `engine/ui/building_ui.py`

Visual interface for placing and managing buildings in your game.

**Features:**
- **Building Catalog**: Browse all available buildings
- **Resource Requirements**: See costs with color-coded affordability
- **Visual Placement**: Real-time preview with validity checking
- **Production/Consumption**: See building stats
- **Building Definitions**: 8 pre-defined building types (house, farm, well, solar panel, storage, workshop, wall, turret)

**Keybind:** F3

**Pre-defined Buildings:**
- **House**: Basic shelter (cost: wood 50, stone 30)
- **Farm**: Food production (cost: wood 30, water 20)
- **Well**: Water production (cost: stone 40, metal 10)
- **Solar Panel**: Energy production (cost: metal 100, energy 20)
- **Storage**: Increases capacity (cost: wood 40, metal 20)
- **Workshop**: Metal processing (cost: wood 60, metal 80, stone 40)
- **Wall**: Defense (cost: stone 20)
- **Turret**: Automated defense (cost: metal 150, energy 50)

**Usage:**
```python
from engine.ui.building_ui import BuildingUI

building_ui = BuildingUI(screen, world)
building_ui.toggle()
building_ui.render(camera_offset=(0, 0))
```

---

### 3. Combat UI (`CombatUI`)
**Location:** `engine/ui/combat_ui.py`

Turn-based combat visualization with initiative order and abilities.

**Features:**
- **Initiative Bar**: Visual turn order with health bars
- **Ability Bar**: Combat abilities with action point costs
- **Combat Log**: Scrolling event log with color coding
- **Entity Health**: Real-time health display
- **6 Default Abilities**: Attack, Defend, Special, Heal, Move, Skip Turn

**Keybind:** F9

**Usage:**
```python
from engine.ui.combat_ui import CombatUI

combat_ui = CombatUI(screen, world)
combat_ui.render()
combat_ui.select_ability('attack')
combat_ui.use_ability('attack', target_entity_id)
```

---

### 4. Navmesh Editor (`NavmeshEditorUI`)
**Location:** `engine/ui/navmesh_editor_ui.py`

Visual editor for creating navigation meshes for pathfinding.

**Features:**
- **Paint Tools**: Walkable, Unwalkable, Erase modes
- **Brush Sizes**: 1-10 tile brushes
- **Auto-Generation**: Generate from existing map obstacles
- **Visual Feedback**: Color-coded tiles (green=walkable, red=unwalkable)
- **Save/Load**: Persist navmesh data to entities
- **Grid Overlay**: Toggle grid visibility

**Keybind:** F5

**Usage:**
```python
from engine.ui.navmesh_editor_ui import NavmeshEditorUI

navmesh_editor = NavmeshEditorUI(screen, world)
navmesh_editor.toggle()
navmesh_editor.paint_tile(grid_x, grid_y)
navmesh_editor.save_to_entity()
```

---

### 5. Level Builder (`LevelBuilderUI`)
**Location:** `engine/ui/level_builder_ui.py`

Complete visual level editor with tile painting and entity placement.

**Features:**
- **Tile Palette**: 9 pre-defined tile types
- **Entity Templates**: 5 entity types with auto-component setup
- **Multi-Layer Support**: 3 layers (Ground, Objects, Overlay)
- **Tool Modes**: Tile, Entity, Erase, Select
- **Grid View**: Visual grid overlay

**Keybind:** F4

**Tile Types:**
- Grass, Dirt, Stone, Water, Sand, Lava, Wall, Floor, Void

**Entity Templates:**
- Player, Enemy, Chest, Tree, Rock

**Usage:**
```python
from engine.ui.level_builder_ui import LevelBuilderUI

level_builder = LevelBuilderUI(screen, world)
level_builder.toggle()
level_builder.paint_tile(grid_x, grid_y)
level_builder.place_entity(grid_x, grid_y)
```

---

### 6. Settings UI (`SettingsUI`)
**Location:** `engine/ui/settings_ui.py`

Comprehensive settings panel for all game configuration.

**Features:**
- **4 Settings Tabs**: Audio, Graphics, Input, Gameplay
- **Audio Settings**: Master/Music/SFX volume sliders, mute toggle
- **Graphics Settings**: Fullscreen, VSync, FPS display, particle density, screen shake
- **Input Settings**: Mouse sensitivity, Y-axis inversion, key rebinding
- **Gameplay Settings**: Difficulty levels, auto-save, tutorial toggle
- **Persistent Storage**: Save/load settings from JSON

**Keybind:** F2

**Usage:**
```python
from engine.ui.settings_ui import SettingsUI

settings_ui = SettingsUI(screen, audio_manager, input_manager)
settings_ui.toggle()
settings_ui.save_settings()
settings_ui.load_settings()
```

---

### 7. Project Manager (`ProjectManagerUI`)
**Location:** `engine/ui/project_manager_ui.py`

Visual project and scene management system.

**Features:**
- **3 Views**: Projects, Scenes, Saves
- **Project Creation**: Multiple templates (blank, platformer, RPG, survival)
- **Scene Management**: Create, load, delete scenes
- **Save Management**: Browse and load save files
- **Project Metadata**: Track modification times, paths

**Keybind:** F8

**Usage:**
```python
from engine.ui.project_manager_ui import ProjectManagerUI

project_manager = ProjectManagerUI(screen, state_manager)
project_manager.toggle()
project_manager.create_project("MyGame", "rpg")
```

---

### 8. Debug Console (`DebugConsoleUI`)
**Location:** `engine/ui/debug_console_ui.py`

Powerful debug console with entity inspector and commands.

**Features:**
- **Command System**: 12 built-in commands
- **Entity Inspector**: Real-time component viewing
- **Performance Overlay**: FPS tracking, entity/system counts
- **Command History**: Up/down arrow navigation
- **Color-Coded Output**: Visual feedback for messages
- **Debug Toggles**: Colliders, grid, navmesh, entity IDs

**Keybind:** F1

**Commands:**
- `help` - Show available commands
- `clear` - Clear console output
- `list_entities` - List all entities
- `inspect <id>` - Inspect entity
- `spawn` - Spawn new entity
- `destroy <id>` - Destroy entity
- `tp <id> <x> <y>` - Teleport entity
- `give <id> <resource> <amount>` - Give resources
- `heal <id> [amount]` - Heal entity
- `toggle <option>` - Toggle visualizations
- `save` - Save game
- `load` - Load game

**Usage:**
```python
from engine.ui.debug_console_ui import DebugConsoleUI

debug_console = DebugConsoleUI(screen, world)
debug_console.toggle()
debug_console.execute_command("inspect 1")
```

---

### 9. Quest Editor (`QuestEditorUI`)
**Location:** `engine/ui/quest_editor_ui.py`

Visual editor for creating quests and dialogue trees.

**Features:**
- **2 Modes**: Quest Editor and Dialogue Editor
- **Quest Creation**: Name, description, objectives, rewards
- **Dialogue Trees**: Visual node-based dialogue system
- **Quest Status**: Draft, active, complete states
- **Save/Load**: Persist quests and dialogues to files

**Keybind:** F6

**Usage:**
```python
from engine.ui.quest_editor_ui import QuestEditorUI

quest_editor = QuestEditorUI(screen)
quest_editor.toggle()
quest_editor.create_new_quest()
```

---

### 10. Asset Browser (`AssetBrowserUI`)
**Location:** `engine/ui/asset_browser_ui.py`

Visual asset manager for all game resources.

**Features:**
- **5 Asset Categories**: Sprites, Sounds, Music, Fonts, Data
- **2 View Modes**: Grid view and list view
- **Search Functionality**: Filter assets by name
- **Preview System**: Visual previews for supported formats
- **Asset Details**: Type, size, dimensions, path
- **File Management**: Use, delete assets

**Keybind:** F7

**Usage:**
```python
from engine.ui.asset_browser_ui import AssetBrowserUI

asset_browser = AssetBrowserUI(screen, asset_manager)
asset_browser.toggle()
asset_browser.refresh_assets()
```

---

## Master UI Manager

### `MasterUIManager`
**Location:** `engine/ui/master_ui_manager.py`

Unified manager that coordinates all UI systems.

**Features:**
- **Single Interface**: Manage all UIs from one place
- **Event Routing**: Automatically route events to active UIs
- **Keybind Management**: F1-F10 hotkeys for all systems
- **Mode Management**: Game, Editor, Menu modes
- **State Persistence**: Save/load UI state

**Usage:**
```python
from engine.ui.master_ui_manager import MasterUIManager

ui_manager = MasterUIManager(screen, world, state_manager, audio_manager, input_manager)

# In game loop
ui_manager.render(fps, camera_offset)
ui_manager.handle_event(event)
ui_manager.update(dt, mouse_pos, camera_offset)

# Toggle UIs
ui_manager.toggle_debug_console()
ui_manager.toggle_building_ui()
```

---

## Quick Start Example

```python
import pygame
from engine.core.ecs import World
from engine.ui.master_ui_manager import MasterUIManager

# Initialize
pygame.init()
screen = pygame.display.set_mode((1280, 720))
world = World()

# Create UI manager
ui_manager = MasterUIManager(screen, world)

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    dt = clock.tick(60) / 1000.0

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        ui_manager.handle_event(event)

    # Update
    world.update(dt)
    ui_manager.update(dt, pygame.mouse.get_pos(), (0, 0))

    # Render
    screen.fill((20, 20, 30))
    ui_manager.render(clock.get_fps(), (0, 0))
    pygame.display.flip()

pygame.quit()
```

---

## Complete Demo

Run the complete visual UI demo:

```bash
python engine/examples/visual_ui_demo.py
```

This demo showcases all UI systems with:
- Pre-configured entities (player, enemies, buildings)
- All UI systems accessible via F1-F10
- Interactive examples of each system
- On-screen help and instructions

---

## Keybind Reference

| Key | UI System |
|-----|-----------|
| F1  | Debug Console |
| F2  | Settings |
| F3  | Building UI |
| F4  | Level Builder |
| F5  | Navmesh Editor |
| F6  | Quest Editor |
| F7  | Asset Browser |
| F8  | Project Manager |
| F9  | Combat UI |
| F10 | Toggle HUD |

---

## Customization

All UI systems can be customized:

1. **Colors**: Modify color tuples in each UI class
2. **Layouts**: Adjust panel positions and sizes
3. **Content**: Add your own buildings, abilities, tiles, etc.
4. **Keybinds**: Change keybinds in `MasterUIManager`

Example - Add a custom building:

```python
building_ui.building_definitions['castle'] = {
    'name': 'Castle',
    'cost': {'stone': 500, 'wood': 300},
    'production': {},
    'consumption': {},
    'description': 'Mighty fortress',
    'color': (100, 100, 100),
    'size': (5, 5),
}
```

---

## Best Practices

1. **Use MasterUIManager**: It handles coordination between all systems
2. **Check Visibility**: UIs only process input when visible
3. **Camera Offset**: Pass camera offset for correct world-space rendering
4. **Event Handling**: Let UI manager handle events first
5. **State Management**: Use save/load methods for persistence

---

## Troubleshooting

**Q: UI not showing?**
- Check visibility with `ui.visible`
- Ensure render is called in game loop
- Verify screen size is adequate

**Q: Mouse clicks not working?**
- UI manager must process events via `handle_event()`
- Check if another UI is capturing input

**Q: Performance issues?**
- Only render visible UIs
- Limit entity inspector updates
- Use appropriate FPS cap

---

## Next Steps

1. Explore the visual UI demo
2. Integrate UIs into your game
3. Customize UI colors and layouts
4. Add your own content (buildings, abilities, etc.)
5. Create editor tools for your specific game needs

For more information, see the main NeonWorks documentation.
