# NeonWorks RPG Maker Feature Parity Implementation Guide

## Overview
You are tasked with implementing 4 major features to bring NeonWorks closer to RPG Maker's feature set. These features will transform NeonWorks from a code-heavy game engine into a more accessible visual game creation suite.

## Architecture Requirements

### Technology Stack
- **UI Framework**: Continue using Pygame for consistency with existing editors
- **Data Format**: JSON for serialization (maintain compatibility)
- **Asset Format**: PNG for images, OGG for audio (cross-platform support)
- **Code Organization**: Follow existing pattern in `/engine/ui/` for editors

### Integration Points
- All editors accessible via Master UI Manager (`engine/ui/master_ui_manager.py`)
- Use F-key shortcuts (F5-F8 available)
- Follow existing immediate-mode GUI pattern
- Integrate with existing EventManager, AssetManager, and ECS systems

---

## Feature 1: Visual Event Editor

### Goal
Create a drag-and-drop visual event editor similar to RPG Maker's event system, eliminating the need to code game logic.

### Requirements

#### Core Functionality
1. **Event Page System**
   - Visual list of all events in current map/scene
   - Create/edit/delete events
   - Name, position, and graphic assignment
   - Event pages with conditions (switches, variables, items)

2. **Command Palette**
   - Categorized command library:
     - **Message**: Show text, show choices, input number
     - **Game Progression**: Control switches, control variables, control timer
     - **Flow Control**: Conditional branch, loop, break loop, exit event processing, common event
     - **Party**: Change gold, change items, change equipment, change HP/MP
     - **Actor**: Change name, change class, change skills, change level
     - **Movement**: Transfer player, set move route, vehicle operations
     - **Character**: Show/hide picture, move picture, tint screen, flash screen
     - **Screen Effects**: Fade in/out, weather effects, shake screen
     - **Audio**: Play BGM, play BGS, play ME, play SE, stop audio
     - **Scene Control**: Open menu, save, load game, return to title
     - **System**: Change tileset, change battle background, change window skin
     - **Battle**: Encounter enemy, win/lose processing, escape processing
     - **Advanced**: Script call, comment, label, jump to label

3. **Visual Event Builder**
   - Drag commands from palette to event list
   - Indent/outdent for conditional blocks
   - Visual tree structure showing flow control
   - Double-click to edit command parameters
   - Copy/paste/delete commands
   - Move commands up/down

4. **Parameter Editors**
   - Context-specific parameter windows for each command type
   - Variable/switch pickers with search/filter
   - Actor/item/skill selection from database
   - Text editor with variable insertion
   - Move route editor with visual preview

5. **Event Triggers**
   - Action button (player presses confirm)
   - Player touch (player walks into event)
   - Event touch (event walks into player)
   - Autorun (runs continuously)
   - Parallel process (runs in background)

### Implementation Steps

1. **Create Event Data Structure** (`engine/core/event_commands.py`)
   ```python
   class EventCommand:
       command_type: str  # "show_text", "conditional_branch", etc.
       parameters: dict   # Command-specific parameters
       indent: int        # For flow control nesting

   class GameEvent:
       id: str
       name: str
       position: tuple
       graphic: str
       pages: List[EventPage]

   class EventPage:
       conditions: dict   # switches, variables, items
       graphic: str
       trigger: str       # "action", "player_touch", etc.
       commands: List[EventCommand]
   ```

2. **Build Command Interpreter** (`engine/core/event_interpreter.py`)
   - Execute event command list sequentially
   - Handle flow control (branches, loops, jumps)
   - Manage wait states for animations/movements
   - Support parallel event execution
   - Integration with existing EventManager

3. **Create Visual Editor UI** (`engine/ui/event_editor_ui.py`)
   - Left panel: Event list (all events in scene)
   - Center panel: Command list (selected event's commands)
   - Right panel: Command palette (available commands)
   - Bottom panel: Parameter editor (selected command)
   - Use existing Pygame UI patterns from quest_editor_ui.py

4. **Build Parameter Windows** (`engine/ui/event_params/`)
   - `text_param.py` - Text editor with \v[n] variable syntax
   - `condition_param.py` - Visual conditional builder
   - `move_route_param.py` - Movement command sequencer
   - `switch_variable_param.py` - Switch/variable picker
   - `database_param.py` - Actor/item/skill picker

5. **Map Integration** (`engine/ui/level_builder_ui.py`)
   - Add "Event Mode" to level builder
   - Click to place event on map
   - Double-click event to open event editor
   - Visual event sprite preview on map
   - Event coordinate synchronization

6. **Testing Requirements**
   - Create sample events: door, chest, NPC dialogue
   - Test all command types execute correctly
   - Verify flow control (branches, loops work)
   - Test parallel events don't block
   - Save/load event data to JSON

### File Structure
```
engine/
├── core/
│   ├── event_commands.py      # Command data structures
│   ├── event_interpreter.py   # Command execution engine
│   └── event_triggers.py      # Trigger detection system
├── ui/
│   ├── event_editor_ui.py     # Main event editor
│   └── event_params/          # Parameter editing windows
│       ├── text_param.py
│       ├── condition_param.py
│       ├── move_route_param.py
│       └── database_param.py
└── templates/
    └── events/
        ├── door_event.json
        ├── chest_event.json
        └── npc_event.json
```

---

## Feature 2: Visual Database Manager

### Goal
Create a GUI database editor for managing game data (items, skills, enemies, actors, classes, etc.) without editing JSON files.

### Requirements

#### Core Functionality
1. **Database Categories**
   - Actors (playable characters)
   - Classes (character job/class system)
   - Skills (abilities/magic)
   - Items (consumables, key items)
   - Weapons (equippable attack items)
   - Armor (equippable defense items)
   - Enemies (battle opponents)
   - Troops (enemy formations)
   - States (status effects)
   - Animations (visual effects)
   - Tilesets (map tile collections)
   - Common Events (reusable event scripts)

2. **List View**
   - Left panel: Category selection
   - Center panel: Entry list (ID, name, icon preview)
   - Search/filter functionality
   - Sort by ID, name, type
   - Pagination for large datasets (2000+ entries)

3. **Detail Editor**
   - Right panel: Selected entry details
   - Context-specific fields for each category:
     - **Items**: name, description, icon, price, consumable, effects, scope
     - **Skills**: name, description, icon, cost, damage formula, effects, animation
     - **Enemies**: name, graphic, stats (HP, MP, ATK, DEF, etc.), exp, gold, drops
     - **Actors**: name, nickname, class, initial level, face/character graphic
   - Field validation (numbers, ranges, required fields)
   - Preview panel for graphics/animations

4. **Batch Operations**
   - Duplicate entry
   - Delete entry (with confirmation)
   - Import/export CSV
   - Bulk edit (change category for multiple items)
   - Maximum entries: configurable (default 2000 per category)

5. **Integration Features**
   - Asset browser integration (pick icons, graphics)
   - Formula editor for damage calculations
   - Effect builder (visual effect selection)
   - Tag system for categorization

### Implementation Steps

1. **Create Database Schema** (`engine/data/database_schema.py`)
   ```python
   class DatabaseEntry:
       id: int
       name: str

   class Item(DatabaseEntry):
       description: str
       icon_index: int
       price: int
       consumable: bool
       effects: List[Effect]
       scope: str  # "none", "one_enemy", "all_enemies", "one_ally", etc.

   class Skill(DatabaseEntry):
       description: str
       icon_index: int
       mp_cost: int
       tp_cost: int
       damage_formula: str
       effects: List[Effect]
       animation_id: int

   class Enemy(DatabaseEntry):
       graphic: str
       stats: dict  # hp, mp, atk, def, mat, mdf, agi, luk
       exp: int
       gold: int
       drops: List[Drop]
       actions: List[EnemyAction]
   ```

2. **Build Database Manager** (`engine/data/database_manager.py`)
   - CRUD operations (Create, Read, Update, Delete)
   - JSON serialization/deserialization
   - Data validation and constraints
   - ID management (auto-increment, gaps handling)
   - Batch operations support

3. **Create Editor UI** (`engine/ui/database_editor_ui.py`)
   - Three-panel layout (category, list, details)
   - Category tabs or tree view
   - Entry list with search/filter
   - Detail form with field types:
     - Text input (name, description)
     - Number input (price, stats)
     - Dropdown (scope, category)
     - Checkbox (consumable, equippable)
     - Asset picker (icon, graphic, animation)
     - List editor (effects, drops, actions)

4. **Build Field Editors** (`engine/ui/database_fields/`)
   - `effect_editor.py` - Visual effect builder
   - `formula_editor.py` - Damage formula with syntax help
   - `stat_editor.py` - Stat distribution sliders
   - `drop_editor.py` - Item drop table with probabilities
   - `action_editor.py` - Enemy AI action patterns

5. **Data Migration**
   - Convert existing JSON files to new schema
   - Create default entries for all categories
   - Maintain backward compatibility
   - Auto-backup before edits

6. **Testing Requirements**
   - Create 100+ items to test performance
   - Test search/filter with large datasets
   - Verify JSON serialization preserves data
   - Test formula editor with edge cases
   - Validate cross-references (skill uses animation ID)

### File Structure
```
engine/
├── data/
│   ├── database_schema.py     # Data class definitions
│   ├── database_manager.py    # CRUD operations
│   └── validators.py          # Field validation
├── ui/
│   ├── database_editor_ui.py  # Main database editor
│   └── database_fields/       # Specialized field editors
│       ├── effect_editor.py
│       ├── formula_editor.py
│       ├── stat_editor.py
│       └── drop_editor.py
└── templates/
    └── base_builder/
        └── config/
            ├── actors.json
            ├── classes.json
            ├── skills.json
            ├── items.json
            ├── weapons.json
            ├── armor.json
            ├── enemies.json
            ├── troops.json
            └── states.json
```

---

## Feature 3: Asset Library

### Goal
Include a comprehensive default asset library so users can create games immediately without external assets.

### Requirements

#### Asset Categories & Quantities

1. **Character Sprites** (44+ sets)
   - 8-directional walk cycles (or 4-directional)
   - 3-frame animation per direction
   - Multiple character types:
     - Heroes (warrior, mage, thief, cleric) - 4 sets
     - NPCs (villagers, merchants, guards) - 20 sets
     - Monsters (humanoid form) - 10 sets
     - Animals (dog, cat, bird, etc.) - 10 sets
   - Size: 32x32 or 48x48 sprite sheets
   - Format: PNG with transparency

2. **Enemy Graphics** (105+ enemies)
   - Front-view battle graphics
   - Multiple categories:
     - Slimes/Blobs - 5 variations
     - Animals (wolf, bear, snake, bat, etc.) - 15 enemies
     - Undead (skeleton, zombie, ghost, etc.) - 15 enemies
     - Humans (bandit, knight, assassin, etc.) - 10 enemies
     - Demons (imp, demon, devil, etc.) - 10 enemies
     - Dragons (wyrm, drake, dragon, ancient dragon) - 5 enemies
     - Elementals (fire, water, earth, air) - 4 enemies
     - Plants (carnivorous plant, treant, etc.) - 5 enemies
     - Insects (giant spider, scorpion, etc.) - 6 enemies
     - Bosses (unique designs) - 10 enemies
     - Misc (golems, mimics, etc.) - 20 enemies
   - Size: 64x64 to 256x256
   - Format: PNG with transparency

3. **Battle Animations** (120+ effects)
   - Physical attacks (slash, thrust, blow) - 10 animations
   - Magic effects:
     - Fire (fireball, inferno, explosion) - 8 animations
     - Ice (ice shard, blizzard, freeze) - 8 animations
     - Lightning (spark, bolt, storm) - 8 animations
     - Water (splash, wave, tsunami) - 6 animations
     - Earth (rock, quake, avalanche) - 6 animations
     - Wind (gust, tornado, cyclone) - 6 animations
     - Light (shine, beam, holy) - 8 animations
     - Dark (shadow, curse, void) - 8 animations
   - Status effects (poison, sleep, confuse, etc.) - 12 animations
   - Healing (cure, revive, regen) - 6 animations
   - Buffs/Debuffs (power up, shield, weaken) - 10 animations
   - Special effects (teleport, summon, transform) - 24 animations
   - Sprite sheet format: 5 frames, 192x192 per frame

4. **Music Tracks** (48+ tracks)
   - Town themes - 4 tracks
   - Dungeon themes - 4 tracks
   - Battle themes - 6 tracks (normal, boss, final boss)
   - World map themes - 3 tracks
   - Event themes (victory, game over, inn) - 6 tracks
   - Emotional themes (sad, happy, tense, mysterious) - 10 tracks
   - Atmospheric (cave, forest, castle, etc.) - 10 tracks
   - Misc (title screen, credits, cutscene) - 5 tracks
   - Format: OGG, loop-ready
   - Duration: 1-3 minutes each

5. **Sound Effects** (345+ SFX)
   - UI sounds (cursor, select, cancel, buzzer) - 10 SFX
   - Battle sounds:
     - Physical attacks (slash, punch, arrow) - 15 SFX
     - Magic casts (fire, ice, lightning, etc.) - 20 SFX
     - Damage (hit, critical, evade) - 10 SFX
   - Character sounds (jump, land, footsteps) - 20 SFX
   - Environment:
     - Doors (open, close, locked, unlock) - 8 SFX
     - Chests (open, item get) - 4 SFX
     - Switches/levers - 5 SFX
     - Water (splash, swim) - 5 SFX
     - Fire (crackle, extinguish) - 3 SFX
   - Items (potion, equip, use) - 15 SFX
   - Animals (dog bark, cat meow, bird chirp, etc.) - 20 SFX
   - Monsters (roar, growl, screech) - 30 SFX
   - Magic ambient (charge, release, sparkle) - 25 SFX
   - Atmospheric (wind, rain, thunder, bell) - 30 SFX
   - System (save, level up, shop) - 15 SFX
   - Misc (explosion, collapse, teleport, etc.) - 155 SFX
   - Format: OGG or WAV, short duration (0.1-3 seconds)

6. **Tilesets** (15+ sets)
   - Grass/outdoor tiles - 1 set (200+ tiles)
   - Cave/dungeon tiles - 1 set (150+ tiles)
   - Castle/interior tiles - 1 set (200+ tiles)
   - Desert tiles - 1 set (100+ tiles)
   - Snow/ice tiles - 1 set (100+ tiles)
   - Swamp tiles - 1 set (100+ tiles)
   - Town tiles - 1 set (200+ tiles)
   - Forest tiles - 1 set (150+ tiles)
   - Beach/water tiles - 1 set (100+ tiles)
   - Sci-fi tiles - 1 set (150+ tiles)
   - Modern tiles - 1 set (150+ tiles)
   - Horror tiles - 1 set (100+ tiles)
   - Autotile support (water, walls, cliffs)
   - Size: 32x32 per tile
   - Format: PNG tileset images

7. **Icons** (500+ icons)
   - Items (potions, keys, gems, etc.) - 100 icons
   - Weapons (swords, axes, bows, staffs, etc.) - 100 icons
   - Armor (helmets, shields, armor, accessories) - 80 icons
   - Skills (magic, abilities, special moves) - 100 icons
   - Status effects (poison, sleep, buff, debuff) - 40 icons
   - UI elements (cursor, markers, arrows) - 30 icons
   - Misc (quest, achievement, currency) - 50 icons
   - Size: 32x32 or 24x24
   - Format: PNG icon sheet

8. **UI Elements**
   - Window skins (medieval, modern, sci-fi) - 3 skins
   - Button sets - 3 sets
   - Health/mana bars - 5 styles
   - Cursors/pointers - 10 variations
   - Borders/frames - 10 sets
   - Format: PNG with 9-slice support

9. **Faces/Portraits**
   - Character portraits matching sprite sets - 44+ faces
   - Multiple expressions per character (neutral, happy, sad, angry) - 4 per character
   - Size: 96x96 or 128x128
   - Format: PNG

10. **Parallax Backgrounds**
    - Sky variations (day, sunset, night, cloudy) - 8 images
    - Space/stars - 3 images
    - Clouds (various layers) - 5 images
    - Mountains/hills - 5 images
    - Size: 1920x1080 or tileable
    - Format: PNG

#### Asset Sources

**Option A: Create Original Assets**
- Hire pixel artists to create original assets
- Commission music composers
- Full creative control and licensing
- Most expensive option

**Option B: Use Public Domain Assets**
- OpenGameArt.org - CC0/Public domain assets
- Kenney.nl - Free game assets
- FreeSFX - Public domain sound effects
- Incompetech - Royalty-free music
- Must verify licenses allow redistribution

**Option C: Hybrid Approach** (RECOMMENDED)
- Create essential/unique assets (character generator parts)
- Source high-quality public domain assets
- Commission specific missing pieces
- Properly attribute in credits.txt

### Implementation Steps

1. **Create Asset Directory Structure**
   ```
   assets/
   ├── characters/
   │   ├── heroes/
   │   ├── npcs/
   │   ├── monsters/
   │   └── animals/
   ├── enemies/
   │   ├── slimes/
   │   ├── animals/
   │   ├── undead/
   │   ├── demons/
   │   └── bosses/
   ├── animations/
   │   ├── physical/
   │   ├── magic/
   │   │   ├── fire/
   │   │   ├── ice/
   │   │   └── lightning/
   │   ├── status/
   │   └── special/
   ├── music/
   │   ├── town/
   │   ├── battle/
   │   ├── dungeon/
   │   └── event/
   ├── sfx/
   │   ├── ui/
   │   ├── battle/
   │   ├── environment/
   │   └── magic/
   ├── tilesets/
   │   ├── outdoor/
   │   ├── indoor/
   │   ├── dungeon/
   │   └── autotiles/
   ├── icons/
   │   ├── items/
   │   ├── weapons/
   │   ├── skills/
   │   └── states/
   ├── faces/
   ├── ui/
   │   ├── windowskins/
   │   ├── buttons/
   │   └── cursors/
   └── backgrounds/
   ```

2. **Asset Collection & Curation**
   - Research and download CC0/public domain assets
   - Organize by category
   - Rename files consistently (hero_01.png, enemy_slime_01.png)
   - Create asset manifest (asset_list.json) with metadata
   - Test all assets load correctly

3. **Create Asset Metadata** (`assets/asset_manifest.json`)
   ```json
   {
     "characters": [
       {
         "id": "hero_warrior",
         "file": "characters/heroes/warrior.png",
         "sheet_layout": "8dir_3frame",
         "tile_size": [32, 32],
         "author": "Artist Name",
         "license": "CC0"
       }
     ],
     "music": [
       {
         "id": "bgm_town_01",
         "file": "music/town/peaceful_village.ogg",
         "loop_start": 0,
         "loop_end": 120.5,
         "author": "Composer Name",
         "license": "CC-BY 3.0"
       }
     ]
   }
   ```

4. **Update Asset Manager** (`engine/rendering/assets.py`)
   - Add asset manifest loader
   - Create asset category helpers
   - Add preview thumbnail generation
   - Implement lazy loading for performance
   - Remove magenta placeholder (use actual assets)

5. **Create Sample Projects**
   - Update base_builder template to use new assets
   - Create example maps using tilesets
   - Add example characters with animations
   - Include sample battle animations
   - Background music in sample scenes

6. **Documentation**
   - Create CREDITS.txt with all asset attributions
   - Document asset usage guidelines
   - Create asset quick reference guide
   - Tutorial on importing custom assets

7. **Testing Requirements**
   - Verify all assets load without errors
   - Test audio playback (music loops correctly)
   - Confirm animations display properly
   - Check tileset autotile behavior
   - Performance test with all assets loaded

### File Structure
```
assets/
├── asset_manifest.json        # Complete asset database
├── CREDITS.txt               # Asset attributions
└── [category folders]/       # Organized asset files

engine/
└── rendering/
    └── assets.py             # Updated asset manager

docs/
└── asset_guide.md            # Asset usage documentation
```

---

## Feature 4: Character Generator

### Goal
Create a visual character generator tool for creating custom character sprites from component parts.

### Requirements

#### Core Functionality

1. **Component System**
   - Body base (male, female, child, muscular, slim) - 5 bases
   - Skin tones - 8 variations
   - Hairstyles (short, long, ponytail, bald, etc.) - 20 styles
   - Hair colors - 12 colors
   - Eyes (normal, angry, happy, closed, etc.) - 10 styles
   - Eye colors - 8 colors
   - Mouths (smile, frown, neutral, etc.) - 8 styles
   - Facial hair (beard, mustache, goatee, etc.) - 10 styles
   - Clothing:
     - Tops (shirt, armor, robe, dress, etc.) - 20 options
     - Bottoms (pants, skirt, shorts, etc.) - 15 options
     - Shoes (boots, sandals, barefoot, etc.) - 10 options
   - Accessories:
     - Hats/helmets - 15 options
     - Capes/cloaks - 8 options
     - Gloves - 5 options
     - Jewelry - 10 options
   - Weapons (held in hand):
     - Swords - 10 types
     - Axes/hammers - 8 types
     - Staves - 6 types
     - Bows - 4 types
     - None

2. **Layer System**
   - Components render in layers (base -> skin -> clothing -> hair -> accessories)
   - Each layer has color customization
   - Toggle visibility per layer
   - Z-order control for advanced users

3. **Animation Preview**
   - Real-time preview of generated sprite
   - Animate walk cycles (4 or 8 directions)
   - Preview all frames
   - Zoom controls
   - Grid overlay option

4. **Export Functionality**
   - Export as sprite sheet (all directions/frames)
   - Export individual frames
   - Export as multiple sizes (32x32, 48x48, 64x64)
   - Save character template (JSON) for re-editing
   - Filename customization

5. **Preset System**
   - Save custom presets
   - Load presets
   - Include 10+ default presets (warrior, mage, villager, etc.)
   - Randomize button (generate random character)
   - Share presets (export/import JSON)

6. **Face Generator**
   - Generate matching portrait/face from same components
   - Multiple expressions (neutral, happy, sad, angry, surprised)
   - Export faces separately (96x96)
   - Match sprite color scheme

### Implementation Steps

1. **Create Component Assets** (`assets/character_generator/`)
   - Design layered component system
   - Create base bodies in all animation frames
   - Design modular clothing/hair that fits all frames
   - Ensure components align across frames
   - Use transparent PNGs for layering
   - Organize by type (body, hair, clothing, etc.)

2. **Build Generator Data** (`engine/data/character_parts.json`)
   ```json
   {
     "bodies": [
       {
         "id": "body_male_normal",
         "name": "Male",
         "sprite_sheet": "character_generator/bodies/male.png",
         "frames": 12,
         "colorable": false
       }
     ],
     "hair": [
       {
         "id": "hair_short_01",
         "name": "Short",
         "sprite_sheet": "character_generator/hair/short_01.png",
         "frames": 12,
         "colorable": true,
         "default_color": [139, 69, 19]
       }
     ]
   }
   ```

3. **Create Generator Engine** (`engine/tools/character_generator.py`)
   ```python
   class CharacterGenerator:
       def __init__(self):
           self.layers = []  # List of (component_id, color, visible)

       def add_layer(self, component_id, color=None, z_index=0):
           # Add component to layer stack

       def render_frame(self, direction, frame_index):
           # Composite all visible layers for a single frame
           # Apply color tints
           # Return pygame Surface

       def render_spritesheet(self):
           # Render all frames into sprite sheet

       def export(self, filepath, size=32):
           # Save sprite sheet to file

       def save_preset(self, name, filepath):
           # Save current configuration to JSON

       def load_preset(self, filepath):
           # Load configuration from JSON
   ```

4. **Build Generator UI** (`engine/ui/character_generator_ui.py`)
   - Left panel: Component categories (tabs or tree)
   - Center panel: Component selection (thumbnail grid)
   - Right panel: Preview window with animation
   - Bottom panel: Color pickers, export button
   - Layer list showing active components
   - Drag-and-drop layer reordering
   - Random button for quick generation

5. **Component Editor Tools**
   - Color picker with HSV sliders
   - Preset color palettes (skin tones, hair colors, etc.)
   - Layer visibility toggles
   - Animation speed control for preview
   - Direction selector (N, NE, E, SE, S, SW, W, NW)

6. **Face Generator** (`engine/ui/face_generator_ui.py`)
   - Similar component system but for faces
   - Expression selector
   - Match colors from body generator
   - Export with character or separately

7. **Integration**
   - Add to Master UI Manager (F8 key)
   - Link to Asset Browser (generated sprites appear)
   - Link to Database Editor (assign to actors)
   - Link to Level Builder (place on map)

8. **Testing Requirements**
   - Generate 50+ unique characters
   - Test all component combinations
   - Verify animation frames align correctly
   - Test color customization
   - Verify export at all sizes
   - Test preset save/load
   - Check performance with many layers

### File Structure
```
assets/
└── character_generator/
    ├── bodies/
    ├── hair/
    ├── clothing/
    │   ├── tops/
    │   ├── bottoms/
    │   └── shoes/
    ├── accessories/
    │   ├── hats/
    │   ├── capes/
    │   └── jewelry/
    ├── faces/
    │   ├── eyes/
    │   ├── mouths/
    │   └── facial_hair/
    └── weapons/

engine/
├── data/
│   └── character_parts.json    # Component definitions
├── tools/
│   └── character_generator.py  # Generator engine
└── ui/
    ├── character_generator_ui.py  # Main UI
    └── face_generator_ui.py       # Face generator UI

presets/
└── characters/
    ├── warrior.json
    ├── mage.json
    └── villager.json
```

---

## Feature 5: Enhanced Visual Map Painting Tool

### Goal
Polish the existing map editor to match RPG Maker's user-friendliness and feature set.

### Current State Analysis
- Existing tool: `/home/user/neonworks/engine/ui/level_builder_ui.py`
- Has: Basic tile painting, 3 layers, entity placement, grid
- Missing: Advanced features and polish

### Enhancements Needed

#### 1. Tile Selection Improvements
- **Current**: 9 hardcoded tile types
- **New**: Load from tileset images
  - Visual tileset palette showing actual graphics
  - Scroll through large tilesets
  - Tile preview on hover
  - Recently used tiles quick bar
  - Favorite tiles system

#### 2. Autotile System
- **Feature**: Tiles that auto-connect (walls, water, cliffs)
- **Implementation**:
  - 47-tile autotile format (or 16-tile simplified)
  - Auto-detect adjacent tiles
  - Update neighbors when painting
  - Support multiple autotile sets
  - Preview autotile result before placing

#### 3. Brush Tools
- **Current**: Single tile painting
- **New**:
  - Pencil (single tile)
  - Rectangle fill
  - Circle/ellipse fill
  - Fill bucket (flood fill same tile)
  - Line tool
  - Custom brush shapes (loaded from file)
  - Brush size selector (1x1 to 9x9)

#### 4. Selection Tools
- **Rectangle select**: Select region of tiles
- **Magic wand**: Select contiguous same tiles
- **Copy/paste**: Copy selection and paste elsewhere
- **Cut**: Remove and copy selection
- **Stamp**: Store selection as reusable stamp
- **Transform**: Flip horizontal/vertical, rotate

#### 5. Layer Enhancements
- **Current**: 3 fixed layers
- **New**:
  - Add/remove unlimited layers
  - Rename layers
  - Opacity control per layer
  - Lock layer (prevent editing)
  - Merge layers
  - Layer groups/folders
  - Background image layer (parallax)

#### 6. Map Properties
- **Map size**: Visual editor to resize (add/remove rows/columns)
- **Tileset selection**: Choose from available tilesets
- **Music**: Assign BGM to map
- **Battle background**: For random encounters
- **Encounter rate**: Configure random battles
- **Parallax background**: Scrolling background image
- **Map name**: Display name
- **Notes**: Developer notes

#### 7. Event Integration
- **Visual event placement**: See event sprites on map
- **Event quick-edit**: Right-click event to edit
- **Event copy/paste**: Duplicate events
- **Event templates**: Quick-place common events (door, chest, NPC)
- **Show event triggers**: Visual indicator of trigger area

#### 8. View Controls
- **Current**: Basic camera offset
- **New**:
  - Zoom levels (50%, 100%, 200%, 400%)
  - Minimap showing full map overview
  - Quick navigation (click minimap to jump)
  - Grid snap toggle
  - Ruler guides
  - Onion skin (show other layers dimmed)

#### 9. Tileset Passability Editor
- **Feature**: Mark tiles as passable/impassable
- **Implementation**:
  - Visual overlay (red=blocked, green=passable)
  - Paint passability like tiles
  - Four-directional passability (block N/S/E/W separately)
  - Ladder/bush/counter flags
  - Save to tileset metadata

#### 10. Undo/Redo System
- **Current**: None
- **New**:
  - Unlimited undo/redo (Ctrl+Z, Ctrl+Y)
  - Command history viewer
  - Memory-efficient snapshots
  - Undo across sessions (save history)

#### 11. Multi-Map Management
- **Map list panel**: Show all maps in project
- **Map tree**: Organize maps in folders
- **Quick switch**: Switch between open maps
- **Map linking**: Teleport visualization between maps
- **Batch operations**: Export all maps, batch resize

#### 12. Keyboard Shortcuts
- Arrow keys: Pan camera
- Ctrl+C/V/X: Copy/paste/cut
- Shift+Click: Rectangle selection
- Alt+Click: Eyedropper (pick tile under cursor)
- Space+Drag: Pan camera
- Number keys: Switch tools (1=pencil, 2=fill, etc.)
- Ctrl+Z/Y: Undo/redo
- Delete: Erase selection
- Tab: Cycle layers
- F: Fill bucket
- B: Brush tool
- E: Eraser
- S: Select tool

#### 13. Performance Optimizations
- **Current**: Renders entire map every frame
- **New**:
  - Chunk-based rendering (only visible tiles)
  - Layer caching (pre-render layers to texture)
  - Dirty rectangle optimization
  - Tile texture atlas (batch rendering)
  - Handle maps up to 500x500 smoothly

#### 14. Import/Export Features
- **Export map as image**: PNG screenshot of entire map
- **Import from Tiled**: Load TMX files (Tiled map editor format)
- **Export to Tiled**: Save as TMX for external editing
- **Import tileset**: Add new tilesets from image
- **Export tileset**: Extract used tiles to new tileset

#### 15. User Experience Polish
- **Tooltips**: Hover help for all buttons/tools
- **Status bar**: Show current tile, coordinates, layer
- **Context menus**: Right-click for quick actions
- **Tool options panel**: Show settings for active tool
- **Recent files**: Quick-open recent maps
- **Auto-save**: Periodic automatic saving
- **Crash recovery**: Recover unsaved work

### Implementation Steps

1. **Refactor Existing Code** (`engine/ui/level_builder_ui.py`)
   - Separate concerns: Rendering, input, tool logic
   - Create tool system architecture:
     ```python
     class MapTool:
         def on_mouse_down(self, pos): pass
         def on_mouse_drag(self, pos): pass
         def on_mouse_up(self, pos): pass
         def render(self, surface): pass

     class PencilTool(MapTool): ...
     class FillTool(MapTool): ...
     class SelectTool(MapTool): ...
     ```

2. **Implement Autotile System** (`engine/rendering/autotiles.py`)
   - Load autotile templates
   - Tile matching algorithm (check 8 neighbors)
   - Update affected tiles when painting
   - Render autotile composite

3. **Add Tileset Manager** (`engine/data/tileset_manager.py`)
   - Load tileset images
   - Parse tileset metadata (passability, autotiles, etc.)
   - Tile picker UI component
   - Tileset editor for passability

4. **Implement Undo System** (`engine/core/undo_manager.py`)
   - Command pattern for all edit operations
   - Memory-efficient state storage
   - History stack management
   - Integration with all tools

5. **Enhanced Layer System** (`engine/data/map_layers.py`)
   - Dynamic layer creation/deletion
   - Layer property storage
   - Layer compositing for rendering
   - Layer serialization to JSON

6. **Advanced Tools** (`engine/ui/map_tools/`)
   - `pencil_tool.py` - Brush painting
   - `fill_tool.py` - Flood fill
   - `select_tool.py` - Rectangle/magic wand selection
   - `shape_tool.py` - Rectangle/circle/line drawing
   - `eyedropper_tool.py` - Color/tile picker
   - `stamp_tool.py` - Custom brush stamps

7. **UI Components** (`engine/ui/map_components/`)
   - `tileset_picker.py` - Visual tileset selection
   - `layer_panel.py` - Layer list with controls
   - `map_properties.py` - Map settings editor
   - `minimap.py` - Overview minimap
   - `tool_options.py` - Current tool settings

8. **Map Manager** (`engine/data/map_manager.py`)
   - Multi-map support
   - Map tree organization
   - Map linking/teleports
   - Batch operations

9. **Performance** (`engine/rendering/map_renderer.py`)
   - Implement chunk-based rendering
   - Layer texture caching
   - Frustum culling (only render visible area)
   - GPU-accelerated tile rendering

10. **Import/Export** (`engine/tools/map_importers.py`)
    - TMX parser (Tiled format)
    - Image exporter
    - Tileset importer
    - Format converters

11. **Testing Requirements**
    - Create large map (500x500) and test performance
    - Test all tools on all layer types
    - Verify autotiles connect correctly
    - Test undo/redo with 100+ operations
    - Test copy/paste across maps
    - Verify save/load preserves all data

### File Structure
```
engine/
├── rendering/
│   ├── autotiles.py          # Autotile system
│   └── map_renderer.py       # Optimized renderer
├── data/
│   ├── tileset_manager.py    # Tileset loading/management
│   ├── map_layers.py         # Layer system
│   └── map_manager.py        # Multi-map management
├── core/
│   └── undo_manager.py       # Undo/redo system
├── ui/
│   ├── level_builder_ui.py   # Main map editor (refactored)
│   ├── map_tools/            # Tool implementations
│   │   ├── pencil_tool.py
│   │   ├── fill_tool.py
│   │   ├── select_tool.py
│   │   └── stamp_tool.py
│   └── map_components/       # UI components
│       ├── tileset_picker.py
│       ├── layer_panel.py
│       ├── minimap.py
│       └── tool_options.py
└── tools/
    └── map_importers.py      # Import/export functionality
```

---

## Implementation Priority & Timeline

### Phase 1: Foundation (Weeks 1-2)
1. Asset Library collection and organization
2. Database schema design and manager implementation
3. Event command data structures

### Phase 2: Core Features (Weeks 3-6)
1. Visual Database Manager (most important for game design)
2. Character Generator component system
3. Map Editor enhancements (autotiles, tools)

### Phase 3: Advanced Features (Weeks 7-10)
1. Visual Event Editor (most complex)
2. Character Generator UI
3. Map Editor polish (undo, performance)

### Phase 4: Integration & Polish (Weeks 11-12)
1. Cross-feature integration (event editor → database → map)
2. Documentation and tutorials
3. Sample project using all features
4. Bug fixes and performance optimization

---

## Testing Strategy

### Unit Tests
- Database CRUD operations
- Event command interpreter
- Character generator compositing
- Autotile algorithm
- Undo/redo system

### Integration Tests
- Database ↔ Event Editor (select item from database in event)
- Character Generator → Asset Library → Database
- Map Editor ↔ Event Editor (place events on map)
- Save/load entire project with all features

### User Acceptance Tests
- Create simple RPG from scratch using only NeonWorks
- Import RPG Maker project (if compatible)
- Performance test with 2000+ database entries
- Stress test with 500x500 map
- Verify all 345+ sound effects play

---

## Success Criteria

### Feature Parity Checklist
- ✅ Can create events without coding
- ✅ Can manage 2000+ items/skills/enemies via GUI
- ✅ Includes 44+ character sets, 105+ enemies, 120+ animations, 48+ music tracks, 345+ SFX
- ✅ Can generate custom character sprites visually
- ✅ Map editor supports autotiles, advanced tools, unlimited layers

### Quality Metrics
- Database editor handles 2000+ entries with <1s load time
- Map editor runs at 60 FPS with 500x500 map
- Event editor supports 1000+ commands per event
- Character generator exports sprite in <2s
- All features accessible via keyboard shortcuts
- Comprehensive documentation with tutorials

### User Experience Goals
- New users can create playable game in <2 hours
- No JSON editing required for basic game creation
- All features discoverable through UI (tooltips, menus)
- Professional appearance matching or exceeding RPG Maker

---

## Notes for Implementation

### Code Style
- Follow existing NeonWorks patterns
- Use type hints for all functions
- Document all public APIs
- Keep files under 500 lines (split large modules)
- Write unit tests for core logic

### Performance Considerations
- Lazy load assets (don't load all 345 SFX at startup)
- Use texture atlases for tile rendering
- Cache rendered frames in character generator
- Implement object pooling for frequently created objects
- Profile regularly to catch performance regressions

### Accessibility
- Keyboard shortcuts for all major features
- Tooltips explaining all UI elements
- Undo/redo for all destructive operations
- Auto-save to prevent data loss
- Clear error messages with suggestions

### Extensibility
- Plugin system for custom event commands
- Custom tool API for map editor
- Asset pack format for distributing additional assets
- Template system for character generator parts
- Scripting support for advanced users

---

## Final Deliverables

1. **Code**
   - All features implemented and tested
   - Integrated into NeonWorks engine
   - Clean, documented, maintainable code

2. **Assets**
   - Complete asset library with manifest
   - Properly licensed and attributed
   - Organized and named consistently

3. **Documentation**
   - User manual for each feature
   - Tutorial: "Create your first RPG"
   - API documentation for extensibility
   - Asset usage guide

4. **Sample Project**
   - Small playable RPG demonstrating all features
   - Commented events showing best practices
   - Uses included asset library

5. **Tools**
   - Character generator with 10+ presets
   - Database editor with sample data
   - Event editor with common event templates
   - Enhanced map editor with multiple tilesets

---

**END OF IMPLEMENTATION PROMPT**

When implementing, tackle one feature at a time, test thoroughly, and integrate before moving to the next. Prioritize the Database Manager and Asset Library first, as they provide the most immediate value and are dependencies for other features.
