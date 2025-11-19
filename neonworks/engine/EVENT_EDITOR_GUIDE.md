# NeonWorks Event Editor - User Guide

## Overview

The NeonWorks Event Editor is a comprehensive visual tool for creating and managing game events. It includes:

- **Event Editor UI** - Visual interface for creating event commands
- **Level Builder** - Map editor for placing events
- **Event Data System** - Complete save/load functionality
- **Event Templates** - Pre-configured event examples

## Quick Start

### Running the Demo

```bash
python -m engine.demo_editor
```

This opens the event editor demo where you can:
- Press **F5** to open the Event Editor
- Press **F6** to open the Level Builder
- Press **F1** for help
- Press **ESC** to close/exit

### Running Tests

```bash
python -m engine.test_event_workflow
```

This runs the complete test suite verifying:
- Event creation
- Serialization
- Save/load
- Templates
- Conditions
- Complete workflow

## Architecture

### Components

```
engine/
├── ui/
│   ├── event_editor_ui.py        # Main event editor interface
│   ├── master_ui_manager.py      # UI coordination and shortcuts
│   ├── level_builder_ui.py       # Map editor with event placement
│   └── event_params/             # Parameter editors (text, conditions, etc.)
├── core/
│   ├── event_data.py             # Event data structures and serialization
│   └── event_interpreter.py      # Event command interpreter (runtime)
└── templates/
    └── events/                    # Pre-configured event templates
        ├── door_template.json
        ├── chest_template.json
        └── npc_template.json
```

## Keyboard Shortcuts

### Global Shortcuts
- **F1** - Show help
- **F5** - Toggle Event Editor
- **F6** - Toggle Level Builder
- **F7** - Toggle Database Editor (coming soon)
- **ESC** - Close active UI / Quit

### Event Editor
- **Arrow Keys** - Navigate command list
- **Delete** - Delete selected command
- **Insert** - Add new command
- **Ctrl+S** - Save event
- **Ctrl+O** - Open event

### Level Builder
- **Arrow Keys** - Move camera
- **E** - Create new event at cursor
- **Left Click** - Select event
- **Double Click** - Edit event
- **Right Click** - Delete event
- **Ctrl+S** - Save map
- **Ctrl+O** - Open map

## Event Structure

### GameEvent

A complete game event with:
- **id**: Unique identifier
- **name**: Display name
- **x, y**: Position on map
- **pages**: List of event pages (conditions + commands)

### EventPage

A single page of an event with:
- **Conditions**: When this page is active
  - Switch conditions (switch1, switch2)
  - Variable conditions
  - Self-switch conditions (A, B, C, D)
- **Graphic**: Visual appearance
  - Character sprite
  - Tile graphic
  - Direction and pattern
- **Movement**: How the event moves
  - Move type (fixed, random, approach, custom)
  - Speed and frequency
  - Movement route
- **Options**: Trigger and priority
  - Trigger: action_button, player_touch, event_touch, autorun, parallel
  - Priority: below_player, same_as_player, above_player
- **Commands**: List of event commands

## Event Commands

### Message Commands
- **SHOW_TEXT** - Display text message
- **SHOW_CHOICES** - Display choice menu
- **INPUT_NUMBER** - Get number from player

### Game Progression
- **CONTROL_SWITCHES** - Turn switches ON/OFF
- **CONTROL_VARIABLES** - Change variable values
- **CONTROL_SELF_SWITCH** - Change self-switch

### Flow Control
- **CONDITIONAL_BRANCH** - If/else logic
- **LOOP** - Repeat commands
- **BREAK_LOOP** - Exit loop
- **EXIT_EVENT** - Stop event processing
- **WAIT** - Pause execution
- **COMMENT** - Developer notes

### Party & Actors
- **CHANGE_GOLD** - Add/remove gold
- **CHANGE_ITEMS** - Add/remove items
- **CHANGE_PARTY** - Add/remove actors
- **CHANGE_HP** - Modify HP
- **CHANGE_MP** - Modify MP

### Map & Movement
- **TRANSFER_PLAYER** - Move to another map
- **SET_EVENT_LOCATION** - Move event
- **SET_MOVEMENT_ROUTE** - Define movement pattern

### Audio & Visual
- **PLAY_BGM** - Play background music
- **PLAY_SE** - Play sound effect
- **SHOW_ANIMATION** - Display animation
- **SHOW_PICTURE** - Display image

## Creating Events

### Method 1: Using Templates

```python
from neonworks.engine.core.event_data import create_door_event

# Create a door that transfers to another map
door = create_door_event(
    x=5, y=5,
    target_map="town",
    target_x=10,
    target_y=15
)
```

### Method 2: Using Event Manager

```python
from neonworks.engine.core.event_data import EventManager, EventTrigger

manager = EventManager()
event = manager.create_event("My Event", x=3, y=7)

# Configure the event
page = event.pages[0]
page.trigger = EventTrigger.ACTION_BUTTON
page.commands = [
    {
        "code": "SHOW_TEXT",
        "parameters": {"text": "Hello, world!"}
    }
]
```

### Method 3: Using Event Editor UI

1. Press **F5** to open Event Editor
2. Set event properties (name, position)
3. Add commands using the command palette
4. Configure command parameters
5. Save the event

## Saving and Loading

### Save Events to File

```python
from neonworks.engine.core.event_data import EventManager
from pathlib import Path

manager = EventManager()
# ... create events ...

# Save to JSON
manager.save_to_file(Path("data/maps/my_map.json"))
```

### Load Events from File

```python
manager = EventManager()
manager.load_from_file(Path("data/maps/my_map.json"))

# Access loaded events
for event in manager.events.values():
    print(f"Loaded: {event.name} at ({event.x}, {event.y})")
```

## Event Templates

Pre-configured templates are available in `engine/templates/events/`:

### Door Template (`door_template.json`)
- Transfers player to another map
- Action button trigger
- Customizable destination

### Chest Template (`chest_template.json`)
- Two pages (closed/opened)
- Gives item to player
- Plays sound effect
- Uses self-switch to track state

### NPC Template (`npc_template.json`)
- Random movement
- Dialogue with choices
- Conditional responses

## Advanced Features

### Conditional Pages

Events can have multiple pages with different conditions:

```python
from neonworks.engine.core.event_data import GameEvent, EventPage

event = GameEvent(name="Conditional Event")

# Page 1: Before quest
page1 = event.pages[0]
page1.commands = [
    {"code": "SHOW_TEXT", "parameters": {"text": "Please help me!"}}
]

# Page 2: After quest (switch 10 ON)
page2 = EventPage()
page2.switch1_valid = True
page2.switch1_id = 10
page2.commands = [
    {"code": "SHOW_TEXT", "parameters": {"text": "Thank you!"}}
]
event.pages.append(page2)
```

The active page is determined at runtime by checking conditions in order.

### Movement Routes

Define custom movement patterns:

```python
page.move_route = {
    "commands": [
        {"type": "move", "direction": 2},  # Down
        {"type": "move", "direction": 6},  # Right
        {"type": "wait", "duration": 30},
        {"type": "turn", "direction": 8},  # Face up
    ],
    "repeat": True,
    "skippable": False
}
```

### Event Sprites

Events are automatically visualized on the map:

- **Blue** - Action button trigger
- **Orange** - Player touch trigger
- **Red** - Autorun trigger
- **Green** - Parallel trigger
- **Yellow** - Event touch trigger

## Integration with Game

### In Your Game Loop

```python
from engine.ui.master_ui_manager import MasterUIManager
import pygame

# Initialize
screen = pygame.display.set_mode((1280, 720))
ui_manager = MasterUIManager(screen)

# Game loop
while running:
    for event in pygame.event.get():
        # Let UI handle events first
        if ui_manager.handle_event(event):
            continue
        # Handle game events...

    # Update
    ui_manager.update(delta_time)

    # Render game...

    # Render UI on top
    ui_manager.render()

    pygame.display.flip()
```

### Loading Map Events

```python
from neonworks.engine.core.event_data import EventManager

def load_map(map_name: str):
    manager = EventManager()
    manager.load_from_file(f"data/maps/{map_name}.json")

    # Create event instances for the interpreter
    for event in manager.events.values():
        # Spawn event on map at (event.x, event.y)
        # Initialize with event.pages[0] (or get_active_page())
        pass
```

## File Formats

### Event JSON Structure

```json
{
  "events": [
    {
      "id": 1,
      "name": "Event Name",
      "x": 5,
      "y": 10,
      "pages": [
        {
          "conditions": { ... },
          "graphic": { ... },
          "movement": { ... },
          "options": {
            "trigger": "action_button",
            "priority": 1
          },
          "commands": [
            {
              "code": "SHOW_TEXT",
              "parameters": {
                "text": "Hello!"
              }
            }
          ]
        }
      ]
    }
  ],
  "next_id": 2
}
```

## Troubleshooting

### Events Not Loading
- Check file path is correct
- Verify JSON is valid
- Ensure `data/` directory exists

### UI Not Responding
- Check if correct keyboard shortcuts are used
- Verify pygame is properly initialized
- Check console for error messages

### Events Not Appearing on Map
- Verify event coordinates are within map bounds
- Check that event has valid graphic settings
- Ensure camera position includes event location

## Performance Tips

1. **Use Self-Switches** - More efficient than regular switches for event-specific state
2. **Limit Parallel Events** - These run every frame; use sparingly
3. **Optimize Movement Routes** - Keep routes simple and short
4. **Cache Event Sprites** - Reuse EventSprite instances when possible

## Next Steps

1. **Try the Demo** - Run `python -m engine.demo_editor`
2. **Read Templates** - Study the example events in `engine/templates/events/`
3. **Run Tests** - Verify everything works with `python -m engine.test_event_workflow`
4. **Build Your Game** - Integrate the event system into your project

## API Reference

See the docstrings in:
- `engine/core/event_data.py` - Data structures
- `engine/ui/event_editor_ui.py` - Editor interface
- `engine/ui/level_builder_ui.py` - Map editor

## Support

- Check the code examples in `engine/test_event_workflow.py`
- Review template events in `engine/templates/events/`
- Read inline documentation in source files

---

**Version**: 1.0.0
**Last Updated**: 2025-11-14
**Status**: ✅ All features implemented and tested
