# Event Templates

This directory contains pre-configured event templates that can be used as starting points for common game events in NeonWorks.

> **Note:** These templates use the new NeonWorks Event Command format, designed specifically for the Event Editor (F5). This format is different from legacy templates and provides better integration with the visual event editing system.

## Available Templates

### 1. door_template.json
A simple door event with unlock mechanics and map transfer:
- **Icon**: 🚪
- **Color**: Brown (139, 69, 19)
- **Trigger**: Action Button
- **Features**:
  - Locked state by default
  - Requires key item to unlock
  - Transfers player to another map when opened
  - Uses self-switches to track open/closed state
  - Black screen fade transition

**Usage:**
1. Load this template in the Level Builder (F4)
2. Modify the target map, x, and y coordinates in the TRANSFER_PLAYER command
3. Optionally customize the lock message and key item ID
4. Place on your map

### 2. chest_template.json
A treasure chest that gives rewards with opened/closed states:
- **Icon**: 📦
- **Color**: Gold (255, 215, 0)
- **Trigger**: Action Button
- **Features**:
  - Gives gold and items to player
  - Plays sound effects
  - Shows as empty after opening
  - Uses self-switches to prevent re-opening
  - Two-page system (closed and opened states)

**Usage:**
1. Load this template in the Level Builder
2. Modify the item ID, gold amount, and messages
3. Optionally set the correct tile IDs for your tileset
4. Place on your map

### 3. npc_template.json
An interactive NPC with dialogue, quest system, and choices:
- **Icon**: 👤
- **Color**: Blue (100, 150, 255)
- **Trigger**: Action Button
- **Features**:
  - Multi-page dialogue system
  - Quest offering with player choices
  - Quest tracking using variables and switches
  - Reward system with gold and experience
  - Multiple conversation states
  - Conditional branches based on quest progress

**Usage:**
1. Load this template in the Level Builder
2. Customize the dialogue text and choices
3. Modify quest tracking switch/variable IDs
4. Set rewards (gold, EXP, items)
5. Optionally set character graphic to match your sprites
6. Place on your map

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
with open('engine/templates/events/npc_template.json', 'r') as f:
    template_data = json.load(f)

# Convert to GameEvent
event = level_builder._deserialize_events([template_data])[0]

# Set position
event.x = 10
event.y = 5

# Add to level
level_builder.events.append(event)
```

## Creating Your Own Templates

You can create your own templates by:

1. Creating an event in the Event Editor (F5)
2. Setting it up with the desired commands and settings
3. Saving the level using the Level Builder
4. Extracting the event JSON from the level file
5. Copying it to this directory with a descriptive name
6. Adding documentation in this README

### Template JSON Structure:

```json
{
  "id": 1,
  "name": "Event Name",
  "x": 5,
  "y": 10,
  "color": [100, 150, 255],
  "icon": "👤",
  "template_type": "npc",
  "pages": [
    {
      "trigger": "ACTION_BUTTON",
      "condition_switch1_valid": false,
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

### Using Self-Switches
- Use self-switches (A, B, C, D) for events that change state (like chests and doors)
- Self-switches are unique to each event instance
- Perfect for one-time events and state tracking

### Event Priority and Graphics
- Set `priority: 0` for events that should appear behind the player (floor items)
- Set `priority: 2` for events that should appear in front of the player (overhead signs)
- Use `direction_fix: true` for objects that shouldn't rotate

### Trigger Usage
- Use `ACTION_BUTTON` for interactive objects (NPCs, chests, signs)
- Use `PLAYER_TOUCH` for automatic events when player walks on them (traps, warps)
- Use `AUTORUN` for cutscenes that run when the map loads (with conditions)
- Use `PARALLEL` for events that run continuously in the background

### Quest and Variable Management
- Use switches for binary states (quest accepted/completed, door unlocked)
- Use variables for counters (enemies defeated, items collected)
- Document your switch/variable IDs to avoid conflicts
- Use consistent naming in event names (e.g., "Quest_Elder_001")

### Performance
- Avoid too many AUTORUN or PARALLEL events on the same map
- Use page conditions to disable events when not needed
- Keep command lists concise for frequently triggered events

## Integration with Event Editor

The Event Editor (F5) provides a visual interface for:
- Creating and managing events
- Adding commands from categorized palette
- Editing command parameters
- Managing multiple event pages
- Testing event flow

Happy event creation!
