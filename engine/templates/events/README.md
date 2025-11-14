# Event Templates

This directory contains sample event templates for NeonWorks game development.

## Available Templates

### 1. Door (door.json)
A simple door event with unlock mechanics:
- **Icon**: 🚪
- **Color**: Brown (139, 69, 19)
- **Trigger**: Action Button
- **Features**:
  - Locked state by default
  - Requires key item to unlock
  - Transfers player to another map when opened
  - Uses self-switches to track open/closed state

### 2. Treasure Chest (chest.json)
A treasure chest that gives rewards:
- **Icon**: 📦
- **Color**: Gold (255, 215, 0)
- **Trigger**: Action Button
- **Features**:
  - Gives gold and items to player
  - Plays sound effects
  - Shows as empty after opening
  - Uses self-switches to prevent re-opening

### 3. Village Elder NPC (npc.json)
An interactive NPC with dialogue and quest:
- **Icon**: 👤
- **Color**: Blue (100, 150, 255)
- **Trigger**: Action Button
- **Features**:
  - Multi-page dialogue system
  - Quest offering with choices
  - Quest tracking using variables and switches
  - Reward system with gold and experience
  - Multiple conversation states

## How to Use Templates

### In Level Builder UI:

1. Open the Level Builder (F4)
2. Select the "Event" tool from the tool panel
3. Choose an event type from the Event Palette:
   - NPC
   - Door
   - Chest
   - Sign
   - Trigger
4. Click on the map to place the event
5. Press F5 to open the Event Editor
6. Select your placed event from the event list
7. Add and customize commands as needed
8. Save your level to preserve event data

### Loading Template Files:

To load a template into your level:

```python
import json
from core.event_commands import GameEvent, EventPage, EventCommand, CommandType, TriggerType

# Load template
with open('engine/templates/events/npc.json', 'r') as f:
    template_data = json.load(f)

# Convert to GameEvent
event = level_builder._deserialize_events([template_data])[0]

# Set position
event.x = 10
event.y = 5

# Add to level
level_builder.events.append(event)
```

### Creating Custom Templates:

Create a new JSON file with the following structure:

```json
{
  "name": "My Custom Event",
  "description": "Description of what this event does",
  "template_type": "custom",
  "color": [255, 0, 0],
  "icon": "⭐",
  "pages": [
    {
      "trigger": "ACTION_BUTTON",
      "commands": [
        {
          "command_type": "SHOW_TEXT",
          "parameters": {
            "text": "Hello, world!",
            "face_name": null,
            "face_index": 0,
            "background": 0,
            "position": 2
          },
          "indent": 0
        }
      ]
    }
  ]
}
```

## Command Types

Available command types for events:

### Message Commands
- `SHOW_TEXT`: Display dialogue
- `SHOW_CHOICES`: Display choice menu
- `INPUT_NUMBER`: Get numeric input

### Flow Control
- `CONDITIONAL_BRANCH`: If/else branching
- `LOOP`: Repeat commands
- `BREAK_LOOP`: Exit loop
- `EXIT_EVENT`: Stop event execution
- `LABEL`: Define jump target
- `JUMP_TO_LABEL`: Jump to label
- `COMMENT`: Documentation

### Game Progress
- `CONTROL_SWITCHES`: Set/clear switches
- `CONTROL_VARIABLES`: Modify variables
- `CONTROL_SELF_SWITCH`: Event-specific switches
- `CONTROL_TIMER`: Manage timers

### Character Control
- `TRANSFER_PLAYER`: Move player to location
- `SET_MOVEMENT_ROUTE`: Animate movement
- `SHOW_ANIMATION`: Play animation
- `SHOW_BALLOON`: Show emotion icon
- `ERASE_EVENT`: Remove event temporarily

### Screen Effects
- `FADEOUT_SCREEN`: Fade to black
- `FADEIN_SCREEN`: Fade in from black
- `TINT_SCREEN`: Color tint effect
- `FLASH_SCREEN`: Flash effect
- `SHAKE_SCREEN`: Screen shake
- `WAIT`: Pause execution

### Audio Commands
- `PLAY_BGM`: Play background music
- `FADEOUT_BGM`: Fade out music
- `PLAY_BGS`: Play background sound
- `FADEOUT_BGS`: Fade out background sound
- `PLAY_ME`: Play music effect
- `PLAY_SE`: Play sound effect

### Items & Party
- `CHANGE_GOLD`: Add/remove gold
- `CHANGE_ITEMS`: Add/remove items
- `CHANGE_PARTY_MEMBER`: Add/remove party members
- `CHANGE_HP`: Modify HP
- `CHANGE_MP`: Modify MP
- `CHANGE_EXP`: Modify experience
- `CHANGE_LEVEL`: Modify level

## Trigger Types

- `ACTION_BUTTON`: Activated when player presses action button (Space/Enter)
- `PLAYER_TOUCH`: Activated when player walks onto event
- `EVENT_TOUCH`: Activated when event touches player
- `AUTORUN`: Runs automatically every frame
- `PARALLEL`: Runs in parallel with other events

## Tips

1. **Use Self-Switches**: Perfect for one-time events like chests and doors
2. **Organize with Comments**: Add COMMENT commands to document complex logic
3. **Test Incrementally**: Add commands gradually and test frequently
4. **Use Variables for Tracking**: Track quest progress, scores, counters
5. **Indent Nested Commands**: Properly indent conditional branches and loops

## Integration with Event Editor

The Event Editor (F5) provides a visual interface for:
- Creating and managing events
- Adding commands from categorized palette
- Editing command parameters
- Managing multiple event pages
- Testing event flow

Happy event creation!
