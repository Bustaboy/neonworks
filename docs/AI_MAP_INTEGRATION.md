# AI Map Integration Guide

**Version:** 1.0
**Last Updated:** 2025-11-15
**Purpose:** Complete guide to AI-powered map management in NeonWorks

---

## Table of Contents

1. [Overview](#overview)
2. [Natural Language Map Commands](#natural-language-map-commands)
3. [Procedural Map Generation](#procedural-map-generation)
4. [Integration Points](#integration-points)
5. [Examples](#examples)
6. [Advanced Usage](#advanced-usage)

---

## Overview

The NeonWorks map manager is fully integrated with AI systems, enabling:

- ✨ **Natural language map management** - Create, organize, and manage maps conversationally
- 🎲 **AI-powered procedural generation** - Generate dungeons, wilderness, and arenas
- 🤖 **Intelligent organization** - AI suggests folder structures based on map names
- 📋 **Context-aware assistance** - AI understands your current map and provides relevant help

### Activation

Open the AI Assistant Panel with **Ctrl+Space** to access all AI map features.

---

## Natural Language Map Commands

### Create Maps

**Command:** `"Create map NAME WIDTHxHEIGHT"`

```
User: "Create map Town 50x50"
AI: ✨ Created new map 'Town' (50x50)!

    Switch to it with: 'switch to map Town'
```

**With Folder Organization:**

```
User: "Create map DarkCrypt 60x40 in dungeons"
AI: ✨ Created new map 'DarkCrypt' (60x40)!
    📁 Organized in folder: dungeons

    Switch to it with: 'switch to map DarkCrypt'
```

---

### List Maps

**Command:** `"List maps"`

```
User: "List maps"
AI: 📋 Available Maps (8 total):

    Root:
      🗺️  TestMap
      🗺️  Town

    📁 dungeons:
      🗺️  DarkCrypt
      🗺️  OldCastle

    📁 wilderness:
      🗺️  Forest_542
      🗺️  Plains_218

    Switch to a map with: 'switch to map NAME'
```

---

### Switch Maps

**Command:** `"Switch to map NAME"`

```
User: "Switch to map DarkCrypt"
AI: 🗺️  Switched to map 'DarkCrypt'!

    The map will load in the level editor.
```

---

### Map Information

**Command:** `"Info about map NAME"`

```
User: "Info about map DarkCrypt"
AI: 📋 Map Info: DarkCrypt

    📏 Size: 60x40
    🎨 Tile Size: 32px
    📝 Description: Procedurally generated interior map
    📁 Folder: dungeons
    🏷️  Tags: dungeon, dark, procedural

    🎨 Layers: 3
    🖼️  Tileset: DungeonTiles

    🔗 Connections: 2
      → TownSquare
      → SecretChamber

    📅 Created: 2025-11-15
    📅 Modified: 2025-11-15
```

---

### Duplicate Maps

**Command:** `"Duplicate map SOURCE as TARGET"`

```
User: "Duplicate map DarkCrypt as DarkCrypt_Hard"
AI: 📑 Duplicated 'DarkCrypt' → 'DarkCrypt_Hard'!

    Switch to it with: 'switch to map DarkCrypt_Hard'
```

---

### Rename Maps

**Command:** `"Rename map OLD to NEW"`

```
User: "Rename map TestMap to MainHub"
AI: ✏️  Renamed map 'TestMap' → 'MainHub'.
```

---

### Delete Maps

**Command:** `"Delete map NAME"`

```
User: "Delete map OldMap"
AI: 🗑️  Deleted map 'OldMap'.
```

---

### Organize Maps (AI Suggestions)

**Command:** `"Organize maps"`

```
User: "Organize maps"
AI: 🤖 AI Map Organization Suggestions:

      📁 Town → towns
      📁 DarkCastle → castles
      📁 Forest_542 → wilderness
      📁 Arena_PvP → battle

    💡 Apply suggestions with:
      'organize map NAME into FOLDER'
```

The AI analyzes map names and suggests appropriate folders based on keywords:

- **towns**: "town", "village", "city"
- **dungeons**: "dungeon", "cave", "crypt", "catacomb"
- **wilderness**: "forest", "wild", "jungle", "plains"
- **castles**: "castle", "palace", "fort"
- **battle**: "battle", "arena", "pvp"

---

## Procedural Map Generation

### Generate Interior Maps (Dungeons)

**Command:** `"Generate interior map WIDTHxHEIGHT"`

```
User: "Generate interior map 50x50"
AI: ✨ Generated interior map 'Dungeon_472' (50x50)!
    📁 Saved to: dungeons

    🎲 Procedurally generated with random seed
    🚀 Ready to edit! Say 'switch to map Dungeon_472' to load it
```

**Named Dungeons:**

```
User: "Generate dungeon DarkCrypt 60x40"
AI: ✨ Generated interior map 'DarkCrypt' (60x40)!
    📁 Saved to: dungeons

    🎲 Procedurally generated with random seed
    🚀 Ready to edit! Say 'switch to map DarkCrypt' to load it
```

**Features:**
- Rooms connected by corridors
- Cover positions
- Spawn points
- Obstacles and terrain variation

---

### Generate Exterior Maps (Wilderness)

**Command:** `"Generate exterior map WIDTHxHEIGHT"`

```
User: "Generate exterior map 80x60"
AI: ✨ Generated exterior map 'Forest_789' (80x60)!
    📁 Saved to: wilderness

    🎲 Procedurally generated with random seed
    🚀 Ready to edit! Say 'switch to map Forest_789' to load it
```

**Features:**
- Natural terrain using noise-like algorithms
- Open areas and dense regions
- Water, rough terrain, obstacles
- Organic feel

---

### Generate Competitive Maps (PvP)

**Command:** `"Generate competitive map WIDTHxHEIGHT"`

```
User: "Generate competitive map 60x60"
AI: ✨ Generated competitive map 'Arena_234' (60x60)!
    📁 Saved to: battle

    🎲 Procedurally generated with random seed
    🚀 Ready to edit! Say 'switch to map Arena_234' to load it
```

**Features:**
- Symmetrical layout for fairness
- Balanced spawn points
- Strategic cover positions
- Resource node placement

---

### Generation Help

**Command:** `"Generate map"` (without parameters)

```
User: "Generate map"
AI: 🎲 **PROCEDURAL MAP GENERATION**

    Generate maps automatically! Try:

    **Basic:**
    • "Generate interior map 50x50" - Random dungeon
    • "Generate exterior map 80x60" - Outdoor map
    • "Generate competitive map 60x60" - PvP arena

    **Named:**
    • "Generate dungeon Crypt 60x40" - Named dungeon
    • "Generate map Town 50x50" - Custom name

    **Types:**
    • **interior** - Rooms + corridors (dungeons)
    • **exterior** - Natural terrain (forests, plains)
    • **competitive** - Symmetrical PvP maps

    All maps are saved automatically to appropriate folders!
```

---

## Integration Points

### AI Assistant Panel

The AI Assistant Panel (`Ctrl+Space`) is the primary interface for all map commands.

**Architecture:**
```python
# In ui/ai_assistant_panel.py
def _generate_ai_response(self, user_message: str) -> str:
    # MAP COMMANDS - Processed first
    from neonworks.data.ai_map_integration import get_ai_map_commands

    ai_map_commands = get_ai_map_commands()
    map_response = ai_map_commands.process_command(user_message)
    if map_response is not None:
        return map_response

    # PROCEDURAL GENERATION
    if "generate" in message_lower and "map" in message_lower:
        return self._handle_procedural_generation(user_message)

    # Other commands...
```

---

### Map Manager (`data/ai_map_integration.py`)

Two main classes provide AI functionality:

#### AIMapCommands

Handles all natural language map operations:

```python
from neonworks.data.ai_map_integration import get_ai_map_commands

ai_commands = get_ai_map_commands()
response = ai_commands.process_command("Create map Town 50x50")
print(response)  # ✨ Created new map 'Town' (50x50)!
```

#### ProceduralMapIntegration

Handles procedural map generation:

```python
from neonworks.data.ai_map_integration import get_procedural_integration

proc_gen = get_procedural_integration()
map_data = proc_gen.generate_and_save_map(
    map_name="DarkDungeon",
    map_type="interior",
    width=60,
    height=40,
    seed=12345,  # Optional: for reproducible generation
    folder="dungeons"
)
```

---

## Examples

### Complete Workflow: Creating a Game World

```
# 1. Create hub area
User: "Create map TownHub 50x50 in towns"
AI: ✨ Created new map 'TownHub' (50x50)!
    📁 Organized in folder: towns

# 2. Generate surrounding dungeons
User: "Generate dungeon SouthCrypt 60x40"
AI: ✨ Generated interior map 'SouthCrypt' (60x40)!
    📁 Saved to: dungeons

User: "Generate dungeon NorthCave 55x35"
AI: ✨ Generated interior map 'NorthCave' (55x35)!
    📁 Saved to: dungeons

# 3. Generate wilderness areas
User: "Generate exterior map 80x60"
AI: ✨ Generated exterior map 'Forest_543' (80x60)!
    📁 Saved to: wilderness

# 4. Create PvP arena
User: "Generate competitive map ArenaMain 60x60"
AI: ✨ Generated competitive map 'ArenaMain' (60x60)!
    📁 Saved to: battle

# 5. Check organization
User: "List maps"
AI: 📋 Available Maps (5 total):

    📁 towns:
      🗺️  TownHub

    📁 dungeons:
      🗺️  SouthCrypt
      🗺️  NorthCave

    📁 wilderness:
      🗺️  Forest_543

    📁 battle:
      🗺️  ArenaMain

# 6. Get info about a map
User: "Info about map SouthCrypt"
AI: 📋 Map Info: SouthCrypt
    📏 Size: 60x40
    📝 Description: Procedurally generated interior map
    📁 Folder: dungeons
    🎲 Procedurally generated with random seed

# 7. Make variations
User: "Duplicate map SouthCrypt as SouthCrypt_Hard"
AI: 📑 Duplicated 'SouthCrypt' → 'SouthCrypt_Hard'!
```

---

### Testing and Iteration

```
# Generate multiple variations quickly
User: "Generate dungeon Test1 40x30"
AI: ✨ Generated interior map 'Test1' (40x30)!

User: "Generate dungeon Test2 40x30"
AI: ✨ Generated interior map 'Test2' (40x30)!

User: "Generate dungeon Test3 40x30"
AI: ✨ Generated interior map 'Test3' (40x30)!

# Check results
User: "List maps"
AI: 📁 dungeons:
      🗺️  Test1
      🗺️  Test2
      🗺️  Test3

# Keep the best, delete others
User: "Delete map Test1"
AI: 🗑️  Deleted map 'Test1'.

User: "Delete map Test3"
AI: 🗑️  Deleted map 'Test3'.

User: "Rename map Test2 to FinalDungeon"
AI: ✏️  Renamed map 'Test2' → 'FinalDungeon'.
```

---

## Advanced Usage

### Procedural Generation Configuration

Maps are generated with configurable parameters stored in metadata:

```json
{
  "metadata": {
    "generated": true,
    "generation_type": "interior",
    "seed": 12345,
    "config": {
      "width": 60,
      "height": 40,
      "min_rooms": 3,
      "max_rooms": 8,
      "min_room_size": 4,
      "max_room_size": 10,
      "open_area_density": 0.7,
      "obstacle_density": 0.15,
      "add_cover": true,
      "add_resources": true
    },
    "spawn_points": [[15, 20], [45, 30]],
    "generation_time": "2025-11-15T10:30:00"
  }
}
```

### Regenerating Maps

Since generation config and seed are saved, you can regenerate maps programmatically:

```python
from neonworks.data.map_manager import get_map_manager

map_manager = get_map_manager()
map_data = map_manager.load_map("DarkDungeon")

# Extract generation params
seed = map_data.properties.custom_properties.get("seed")
config = map_data.properties.custom_properties.get("config")

# Regenerate with same params = identical result
# Or change params for variations
```

### Custom Tile Mappings

By default, procedural terrain maps to these tile IDs:
- `.` (floor) → tile 0
- `#` (wall) → tile 1
- `~` (rough) → tile 2
- `≈` (water) → tile 3
- `C` (cover) → tile 4
- `X` (obstacle) → tile 5

To use custom tilesets:

```python
from neonworks.data.ai_map_integration import get_procedural_integration

custom_mapping = {
    ".": 10,  # Your floor tile ID
    "#": 20,  # Your wall tile ID
    "~": 30,  # Your rough terrain ID
    "≈": 40,  # Your water ID
    "C": 50,  # Your cover object ID
    "X": 60,  # Your obstacle ID
}

proc_gen = get_procedural_integration()
map_data = proc_gen.generate_and_save_map(
    map_name="CustomTileMap",
    map_type="interior",
    width=50,
    height=50,
    tile_mapping=custom_mapping
)
```

---

## Help Commands

### Get Help Anytime

```
User: "help"
AI: I can help you build levels! Try commands like:

    **MAP MANAGEMENT:**
    • "Create map Town 50x50" - Create new map
    • "List maps" - Show all maps
    • ...

User: "help maps"
AI: 🗺️  AI MAP COMMANDS:

    **Create & Manage:**
    • "Create map Town 50x50" - Create new map
    • "Create map Dungeon 60x40 in dungeons" - Create in folder
    • "Duplicate map Town as Town2" - Copy a map
    • ...

User: "generate map"
AI: 🎲 **PROCEDURAL MAP GENERATION**

    Generate maps automatically! Try:
    ...
```

---

## Tips & Best Practices

1. **Use Descriptive Names**: The AI uses map names to suggest organization
   - ✅ `ForestPath`, `DarkCrypt`, `TownSquare`
   - ❌ `Map1`, `Test`, `Untitled`

2. **Leverage Folders**: Organize early and often
   - Create maps with folder paths: `"Create map NAME WxH in FOLDER"`
   - Use AI suggestions: `"Organize maps"`

3. **Generate in Batches**: Quickly create variations
   - Generate multiple maps
   - Switch between them to compare
   - Keep the best, delete the rest

4. **Save Generation Seeds**: For reproducible results
   - Check map metadata for the seed value
   - Use same seed = identical map

5. **Iterate with Duplication**: Build on successful designs
   - Duplicate a good map
   - Make variations (harder enemies, different layout)
   - Save as template for future use

---

## Future Enhancements

Planned AI integrations:

- **AI Level Builder Integration**: "Add spawn points to this map"
- **AI Writer Integration**: "Generate a quest for this dungeon"
- **Smart Connections**: "Connect TownHub to all dungeons"
- **Balance Analysis**: "Is this map balanced for 4 players?"
- **Automatic Tilesets**: "Apply forest tileset to all wilderness maps"

---

**Last Updated:** 2025-11-15
**Questions?** Say "help maps" in the AI Assistant Panel (Ctrl+Space)!
