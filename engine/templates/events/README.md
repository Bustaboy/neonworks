# Event Templates

This directory contains pre-configured event templates that can be used as starting points for common game events.

## Available Templates

### door_template.json
A simple door/transfer event that moves the player to another map.

**Features:**
- Action button trigger
- Shows a message when activated
- Transfers player to another map
- Black screen fade transition

**Usage:**
1. Load this template
2. Modify the target map, x, and y coordinates
3. Optionally customize the message
4. Place on your map

### chest_template.json
A treasure chest event with two pages (closed and opened states).

**Features:**
- Page 1 (Closed): Shows message, gives item, plays sound effect
- Page 2 (Opened): Empty chest that does nothing
- Uses self-switch "A" to track opened state
- Different graphics for closed/opened states (tile IDs 80/81)

**Usage:**
1. Load this template
2. Modify the item ID and message
3. Set the correct tile IDs for your tileset
4. Place on your map

### npc_template.json
A talking NPC with random movement and choices.

**Features:**
- Random movement pattern
- Dialogue with player choices
- Conditional branches based on choice
- Character graphic (People1 spritesheet)

**Usage:**
1. Load this template
2. Customize the dialogue text
3. Modify or add choice branches
4. Set the character graphic to match your sprites
5. Place on your map

## Creating Your Own Templates

You can create your own templates by:

1. Creating an event in the Event Editor
2. Setting it up with the desired commands and settings
3. Exporting it using the Level Builder (Ctrl+S)
4. Copying the JSON to this directory
5. Adding documentation in this README

## Template Format

All templates follow this structure:

```json
{
  "id": 0,              // Will be assigned when placed
  "name": "Event Name",
  "x": 0,               // Will be set when placed
  "y": 0,
  "pages": [            // Array of event pages
    {
      "conditions": {   // Page activation conditions
        ...
      },
      "graphic": {      // Visual appearance
        ...
      },
      "movement": {     // Movement settings
        ...
      },
      "options": {      // Trigger and priority
        ...
      },
      "commands": [     // Event commands
        ...
      ]
    }
  ]
}
```

## Tips

- Use self-switches (A, B, C, D) for events that change state (like chests)
- Set `direction_fix: true` for objects that shouldn't rotate
- Use `priority: 0` for events that should appear behind the player
- Use `priority: 2` for events that should appear in front of the player
- Use `trigger: "player_touch"` for automatic events when player walks on them
- Use `trigger: "autorun"` for cutscenes that run when the map loads
