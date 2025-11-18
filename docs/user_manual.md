# NeonWorks User Manual

**Version:** 1.0
**Last Updated:** 2025-11-15
**Engine Version:** 0.1.0

Welcome to NeonWorks! This comprehensive user manual will guide you through creating amazing 2D RPGs, turn-based strategy games, and base-building adventures.

---

## Quick Start: New AI & Bible Tools

This section covers the new AI-assisted workflows and World Bible graph editor. For a deeper tour of the engine, see the sections below.

### AI Assistant Panel (Ctrl+Space)

- Open the **AI Assistant Panel** with **Ctrl+Space** from any editor workspace.
- Use the chat box to ask for help (e.g., “what can you do?” or “generate a starter town layout”).
- Quick action buttons:
  - **Generate Navmesh** – builds a high-level navigation plan for the current map.
  - **Write Quest** – proposes a short quest based on what’s visible on screen and any text you type.
  - **Describe Scene** – rewrites the current scene into a concise designer-friendly description.
- While an AI task is running, a small **“Working: …”** status appears in the panel header. Tasks run **one at a time** to respect VRAM and keep the editor responsive.
- You can add screenshots later for your team, e.g.:
  - `![AI Assistant Panel](assets/docs/ai_assistant_panel.png) <!-- TODO: capture screenshot -->`

### World Bible Graph Editor (Ctrl+D → World Bible tab)

- Open the **Database Manager** with **Ctrl+D** (or via its toolbar button), then select the **“World Bible”** tab.
- On the **left**, choose a node category (Characters, Locations, Quests, etc.).
- In the **middle list**, you can:
  - Click a node to select it as the **From** node.
  - Click the small arrow button to mark a node as the **To** node.
  - Press **“New Node”** to add a new entry of the current type (e.g., `character_3` with a placeholder name).
- On the **right**, you will see:
  - Basic node info (ID, type, name).
  - A list of outgoing relationships (e.g., `located_in → town_1`).
  - A **Relation** selector (cycles through labels like `related_to`, `located_in`, `member_of`, `gives_quest`, `uses_mechanic`).
  - An **“Add Relationship”** button that links the current **From** and **To** nodes and saves to `bible.json` in your project.
- The World Bible is stored as a graph and kept in sync via the **BibleManager**, so other tools can safely query it.

### AI-Approved Dialogue (in-game, Loremaster integration)

- During gameplay, some NPC lines may appear in a special **AI approval dialogue box** with three options:
  - **Accept (A)** – keep the proposed line and continue.
  - **Rewrite (R)** – ask the Loremaster to rewrite the line automatically.
  - **Guide (G)** – open a small text field where you can type guidance (tone, lore notes, etc.), then the Loremaster generates a new line based on that.
- Keyboard shortcuts:
  - **A** or **Enter** – Accept.
  - **R** – Rewrite.
  - **G** – Guide and open the guidance text box.
- The game only advances after you **Accept** a line, giving you full control over the final NPC dialogue.

You can add diagrams later for your team, e.g.:

- `![World Bible Graph View](assets/docs/world_bible_graph.png) <!-- TODO: draw nodes + edges diagram -->`
- `![Dialogue Approval Flow](assets/docs/dialogue_approval_flow.png) <!-- TODO: simple three-button flowchart -->`

## Table of Contents

1. [Introduction](#introduction)
2. [Installation & Setup](#installation--setup)
3. [Understanding NeonWorks](#understanding-neonworks)
4. [Your First Project](#your-first-project)
5. [The Editor Interface](#the-editor-interface)
6. [Creating Your Game](#creating-your-game)
7. [Working with Assets](#working-with-assets)
8. [Building Levels](#building-levels)
9. [Creating Characters](#creating-characters)
10. [Designing Gameplay](#designing-gameplay)
11. [Testing & Debugging](#testing--debugging)
12. [Exporting Your Game](#exporting-your-game)
13. [Advanced Topics](#advanced-topics)
14. [Troubleshooting](#troubleshooting)
15. [Additional Resources](#additional-resources)

---

## Introduction

### What is NeonWorks?

NeonWorks is a powerful, project-based 2D game engine designed specifically for creating:

- **JRPGs** (Japanese-style Role-Playing Games)
- **Turn-based Strategy Games**
- **Base-Building Games with Survival Elements**
- **Exploration-based Adventures**

Built on Python and Pygame, NeonWorks provides everything you need to bring your game ideas to life without writing code.

### Who is NeonWorks For?

- **Game Designers** who want to focus on creativity without programming
- **Indie Developers** looking for a complete, production-ready engine
- **Hobbyists** creating their dream RPG
- **Educators** teaching game design concepts
- **Programmers** who want a solid foundation to build upon

### What Makes NeonWorks Special?

✅ **Visual Tools** - 17 integrated editors accessible with function keys
✅ **No Programming Required** - Create complete games using visual editors
✅ **Production Ready** - Export standalone executables for Windows, Mac, Linux
✅ **JRPG Framework** - Complete battle system, magic, encounters, and more
✅ **AI-Powered Tools** - AI-assisted map generation, quest writing, and animation
✅ **Open Source** - Free to use, modify, and extend

---

## Installation & Setup

### System Requirements

**Minimum:**
- **OS:** Windows 10, macOS 10.14, or Ubuntu 20.04
- **Python:** 3.8 or higher
- **RAM:** 4 GB
- **Storage:** 500 MB for engine + space for your projects
- **Display:** 1280x720 resolution

**Recommended:**
- **Python:** 3.10 or higher
- **RAM:** 8 GB or more
- **Display:** 1920x1080 or higher

### Installing Python

If you don't have Python installed:

**Windows:**
1. Download Python from [python.org](https://python.org)
2. Run the installer
3. ✅ **Check "Add Python to PATH"**
4. Complete installation

**macOS:**
```bash
# Using Homebrew
brew install python@3.10
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.10 python3-pip

# Fedora
sudo dnf install python3.10
```

### Installing NeonWorks

1. **Clone or download NeonWorks:**
```bash
git clone https://github.com/Bustaboy/neonworks.git
cd neonworks
```

2. **Install dependencies:**
```bash
# Core dependencies
pip install -r requirements.txt

# Optional: Development tools
pip install -r requirements-dev.txt
```

3. **Verify installation:**
```bash
python main.py --help
```

You should see the NeonWorks help menu!

### First Launch

Launch the Project Manager to create your first project:

```bash
python main.py
```

Or press `F8` once the engine is running to open the Project Manager.

---

## Understanding NeonWorks

### The Project-Based Workflow

NeonWorks uses a **project-based** approach. Think of it like this:

- **The Engine** = NeonWorks (the tool you downloaded)
- **Your Project** = Your specific game (RPG, strategy game, etc.)
- **Templates** = Pre-configured starting points for different game types

**One engine, unlimited games!**

### Project Structure

When you create a project, NeonWorks generates this structure:

```
my_awesome_rpg/
├── project.json          # Project configuration
├── assets/               # Images, sounds, music
│   ├── sprites/
│   ├── tilesets/
│   ├── audio/
│   └── ui/
├── maps/                 # Game maps and levels
├── config/               # Game data (items, characters, etc.)
│   ├── items.json
│   ├── characters.json
│   ├── enemies.json
│   └── skills.json
├── events/               # Event scripts and triggers
├── saves/                # Player save files
└── exports/              # Exported game builds
```

### The Entity Component System (ECS)

NeonWorks uses an **Entity Component System** architecture. Don't worry if this sounds technical - you'll rarely need to think about it!

**Simple explanation:**
- **Entity** = A game object (player, enemy, item, building)
- **Component** = Data about that object (position, health, sprite)
- **System** = Logic that processes objects (movement, combat)

**For users:** The visual editors handle all of this automatically!

### The Event System

Events let different parts of your game communicate:

- Player defeats enemy → Trigger quest completion
- Player enters area → Start cutscene
- Building completed → Unlock new options

You'll create events visually using the Event Editor (`F5`).

---

## Your First Project

### Creating a New Project

1. **Launch NeonWorks:**
```bash
python main.py
```

2. **Open Project Manager:**
   - Press `F8` or click **Project Manager** in the menu

3. **Click "Create New Project"**

4. **Choose a template:**
   - **Basic Game** - Blank slate for any game type
   - **Turn-Based RPG** - Pre-configured JRPG setup
   - **Base Builder** - Base-building with survival mechanics

5. **Configure your project:**
   - **Name:** "My First RPG"
   - **Author:** Your name
   - **Description:** "An epic adventure!"
   - **Window Size:** 1280x720 (recommended)
   - **Tile Size:** 32 pixels (standard)

6. **Click "Create"**

NeonWorks will generate your project structure!

### Understanding Your New Project

**Screenshot: Project Manager showing new project structure**
*[Screenshot should show: Project list on left, project details on right, "Open in Editor" button]*

Your project includes:

- **Sample map** - A starter level to explore
- **Test character** - A simple player character
- **Basic configuration** - Settings you can customize
- **Empty folders** - Ready for your assets

### Opening Your Project

1. In Project Manager, select your project
2. Click **"Open in Editor"**
3. The Level Builder (`F4`) opens automatically

**You're now in the editor!**

---

## The Editor Interface

### Editor Modes

NeonWorks has two main modes:

**Editor Mode** - Create and design your game
- Access with `F4` (Level Builder)
- All visual editors available
- No gameplay running

**Game Mode** - Play and test your game
- Click **"Play"** button or press `F10`
- Test gameplay, combat, mechanics
- Press `Escape` to return to editor

### The Main Interface

**Screenshot: Main editor interface with labeled sections**
*[Screenshot should show: Menu bar, toolbar, viewport, properties panel, status bar]*

**Key Areas:**

1. **Menu Bar** (Top)
   - File, Edit, View, Tools, Help

2. **Toolbar** (Below menu)
   - Quick access to common tools
   - Play/Pause/Stop buttons

3. **Viewport** (Center)
   - Visual representation of your game
   - Click and drag to pan
   - Scroll wheel to zoom

4. **Properties Panel** (Right)
   - Edit selected object properties
   - Configure component settings

5. **Status Bar** (Bottom)
   - Current tool, mouse position, tips

### Essential Keyboard Shortcuts

**Quick Reference:**

| Shortcut | Function |
|----------|----------|
| `?` | Show shortcuts overlay |
| `F1` | Debug Console |
| `F2` | Settings |
| `F4` | Level Builder |
| `F5` | Event Editor |
| `F6` | Quest Editor |
| `F7` | Asset Browser |
| `F8` | Project Manager |
| `Ctrl+S` | Save |
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |
| `Escape` | Close current editor/menu |

**Tip:** Press `?` anytime to see all shortcuts!

### The Editor Toolbar

**Screenshot: Toolbar with icons labeled**
*[Screenshot should show: Each toolbar icon with label]*

From left to right:

- **New** - Create new map/object
- **Open** - Open existing map
- **Save** - Save current work
- **Undo/Redo** - Undo or redo actions
- **Play** - Test your game
- **Stop** - Return to editor
- **Grid** - Toggle grid display

---

## Creating Your Game

### Step 1: Plan Your Game

Before diving in, answer these questions:

**Game Concept:**
- What type of game? (JRPG, strategy, adventure)
- What's the core gameplay loop?
- How long will the game be?

**Story:**
- Basic plot in 2-3 sentences
- Main character(s)
- Key locations

**Gameplay:**
- How does the player progress?
- What challenges will they face?
- What makes it fun?

**Scope:**
- How much content? (5 hours? 20 hours?)
- Solo developer or team?
- Timeline? (Months? Years?)

**Start small!** Even a 1-hour game is an accomplishment.

### Step 2: Gather Assets

You'll need visual and audio assets:

**Graphics:**
- **Character sprites** (32x32 or 32x64 pixels)
- **Tileset** (terrain, walls, objects)
- **UI elements** (buttons, windows, icons)
- **Effects** (particles, animations)

**Audio:**
- **Music** (background music for areas)
- **Sound effects** (footsteps, attacks, interactions)
- **Ambience** (wind, water, town chatter)

**Where to find assets:**

**Free Resources:**
- [OpenGameArt.org](https://opengameart.org) - Free game assets
- [itch.io](https://itch.io/game-assets/free) - Free and paid assets
- [Kenney.nl](https://kenney.nl) - High-quality free assets

**Asset Packs:**
- Search "RPG tileset" or "character sprites" on itch.io
- Consider commissioning custom art if you have budget

**Creating Your Own:**
- **Pixel Art:** Aseprite, Piskel, GraphicsGale
- **Sound Effects:** Audacity, Bfxr, ChipTone
- **Music:** Bosca Ceoil, BeepBox

See [Asset Collection Guide](asset_collection_guide.md) for detailed guidance.

### Step 3: Set Up Your Database

The **Database** defines your game's items, characters, skills, and more.

Press `Ctrl+D` to open the Database Editor.

See [Database Guide](database_guide.md) for complete instructions.

**Quick setup:**

1. **Characters** - Define player characters and party members
2. **Enemies** - Create monsters and bosses
3. **Items** - Potions, equipment, key items
4. **Skills** - Spells, abilities, techniques
5. **Classes** - Character jobs/professions (optional)

### Step 4: Create Your First Map

Maps are the playable areas of your game.

See [Map Editor Guide](map_editor_guide.md) for detailed instructions.

**Quick start:**

1. Press `F4` to open Level Builder
2. Click **New Map**
3. Set map size (20x15 is good for starters)
4. Choose tileset from Asset Browser (`F7`)
5. Paint terrain, walls, decorations
6. Add player start position
7. Save your map (`Ctrl+S`)

### Step 5: Add Events and Interactions

Events bring your game to life!

Press `F5` to open the Event Editor.

See [Event Editor Guide](event_editor_guide.md) for tutorials.

**Common events:**

- **NPC dialogues** - Talking to townspeople
- **Treasure chests** - Finding items
- **Doors and transitions** - Moving between maps
- **Cutscenes** - Story moments
- **Triggers** - Starting battles or quests

### Step 6: Create Quests

Quests give players goals and structure.

Press `F6` to open the Quest Editor.

**Basic quest structure:**

1. **Quest Title** - "The Missing Sword"
2. **Description** - Quest objectives
3. **Stages** - Step-by-step progression
4. **Rewards** - Items, gold, experience
5. **Requirements** - What's needed to start/complete

### Step 7: Test Your Game

Testing is crucial!

**How to test:**

1. Click **Play** button (or press `F10`)
2. Play through your game
3. Look for:
   - Broken events or triggers
   - Typos in dialogue
   - Balance issues (too hard/easy)
   - Bugs or glitches

4. Press `Escape` to return to editor
5. Make fixes
6. Repeat!

**Use the Debug Console (`F1`) to:**
- Monitor errors
- Check variable values
- Teleport around the map
- Give yourself items for testing

---

## Working with Assets

### Importing Assets

1. **Open Asset Browser** (`F7`)

2. **Click "Import Assets"**

3. **Select files:**
   - Drag & drop into window
   - Or browse and select

4. **Choose asset type:**
   - Sprite
   - Tileset
   - Audio
   - UI Element

5. **Configure import settings:**
   - Asset name
   - Category/tags
   - Transparency color (for sprites)

6. **Click "Import"**

Assets are copied to your project's `assets/` folder and cataloged.

### Organizing Assets

**Screenshot: Asset Browser showing folder structure**
*[Screenshot should show: Folder tree on left, asset thumbnails on right, filter options]*

**Best practices:**

- **Use folders:** Group related assets
  - `assets/characters/player/`
  - `assets/characters/npcs/`
  - `assets/characters/enemies/`

- **Naming conventions:**
  - `character_warrior_idle_01.png`
  - `tile_grass_01.png`
  - `sfx_sword_slash.wav`

- **Tag everything:** Add searchable tags
  - "player", "weapon", "fire"

- **Document sources:** Note where assets came from (licensing!)

### Working with Tilesets

**Tilesets** are grids of tiles used to build maps.

**Screenshot: Tileset in editor with grid overlay**
*[Screenshot should show: Tileset image with 32x32 grid, individual tiles highlighted]*

**Tileset requirements:**

- Each tile is 32x32 pixels (or your project's tile size)
- Organized in a grid
- PNG format with transparency
- Power-of-two dimensions recommended (256x256, 512x512)

**Using autotiles:**

Autotiles automatically connect tiles (walls, water, cliffs).

Press `F11` to open Autotile Editor.

See [Map Editor Guide](map_editor_guide.md) for autotile configuration.

### Character Sprites

Characters need sprites for animation and direction.

**Standard sprite sheet layout:**

```
Row 1: Walk Down  (frames 1, 2, 3, 4)
Row 2: Walk Left  (frames 1, 2, 3, 4)
Row 3: Walk Right (frames 1, 2, 3, 4)
Row 4: Walk Up    (frames 1, 2, 3, 4)
```

**Screenshot: Character sprite sheet showing 4-direction walking animation**
*[Screenshot should show: 4x4 grid of character frames, each frame labeled]*

**Specifications:**

- **Frame size:** 32x64 pixels (or your character size)
- **Format:** PNG with transparency
- **Animations supported:**
  - Walk (4-8 frames per direction)
  - Idle (1-4 frames)
  - Attack (3-6 frames)
  - Cast spell (3-6 frames)
  - Victory pose (1 frame)

See [Character Generator Guide](character_generator_guide.md) for creating custom characters.

---

## Building Levels

### Map Design Principles

**Good maps have:**

1. **Clear goals** - Player knows what to do
2. **Interesting layout** - Not just empty rectangles
3. **Visual variety** - Different areas feel distinct
4. **Appropriate challenge** - Difficulty curve
5. **Rewards for exploration** - Hidden treasures, secrets

**Common mistakes:**

❌ Too large with nothing to do
❌ Confusing layout (player gets lost)
❌ No landmarks or visual distinctions
❌ Too many random encounters
❌ Dead-end paths with no reward

### Layer System

NeonWorks uses **layers** to organize map elements.

**Screenshot: Layer panel showing different map layers**
*[Screenshot should show: Layer list with visibility toggles, layer names, lock icons]*

**Standard layers:**

1. **Ground** (z=0) - Terrain, floors, grass
2. **Ground Detail** (z=1) - Flowers, paths, shadows
3. **Objects** (z=2) - Furniture, rocks, decorations
4. **Walls** (z=3) - Walls, cliffs, barriers
5. **Above Character** (z=4) - Roofs, tree tops
6. **Sky** (z=5) - Clouds, weather effects

**Layer controls:**

- **Eye icon** - Show/hide layer
- **Lock icon** - Prevent editing layer
- **Opacity slider** - Adjust visibility for editing

### Painting Tiles

**Screenshot: Level Builder with tile palette and map**
*[Screenshot should show: Tile selection panel, brush tools, map being painted]*

**Tools:**

- **Pencil** - Paint single tile
- **Brush** - Paint with preview
- **Fill** - Flood fill area
- **Rectangle** - Draw filled rectangle
- **Eraser** - Remove tiles

**Brush settings:**

- **Size:** 1x1 to 10x10
- **Shape:** Square, circle
- **Pattern:** Random variations

**Workflow:**

1. Select layer
2. Choose tileset from Asset Browser
3. Pick tile from palette
4. Select tool (pencil, brush, fill)
5. Click/drag to paint
6. Use `Ctrl+Z` to undo mistakes

### Placing Objects and NPCs

**Objects** are interactive elements: chests, doors, signs, NPCs.

**To place an object:**

1. Click **Objects** tab in toolbar
2. Choose object type:
   - NPC
   - Treasure chest
   - Door/entrance
   - Sign
   - Custom event object

3. Click on map to place
4. Configure properties in Properties Panel

**Screenshot: Properties panel for an NPC**
*[Screenshot should show: NPC properties like name, sprite, dialogue, movement pattern]*

**NPC properties:**

- **Name** - NPC identifier
- **Sprite** - Visual appearance
- **Movement Pattern:**
  - Static (doesn't move)
  - Random walk
  - Patrol route
  - Follow player
- **Dialogue** - What they say
- **Event trigger** - What happens on interaction

### Map Connections

Connect maps together for seamless world navigation.

**Transfer events:**

1. Place a **Transfer Event** on the map edge (or door)
2. Configure transfer:
   - **Target map** - Which map to go to
   - **Target position** - Where player appears (X, Y)
   - **Transition** - Fade, slide, none

**Screenshot: Transfer event configuration dialog**
*[Screenshot should show: Map dropdown, position selector, transition options]*

### Setting Spawn Points

**Player Start Position:**

1. Click **Set Player Start** tool
2. Click location on map
3. A marker appears showing spawn point

**Enemy Spawn Zones:**

For random encounters:

1. Select **Encounter Zone** tool
2. Draw rectangle on map
3. Set encounter properties:
   - **Enemy groups** - What can appear
   - **Encounter rate** - Steps between battles
   - **Disable switch** - Turn off encounters with event

---

## Creating Characters

NeonWorks includes a powerful **Character Generator** for visual customization.

Press `Shift+C` to open the Character Generator.

See [Character Generator Guide](character_generator_guide.md) for complete instructions.

### Character Components

Build characters from modular parts:

**Base Components:**
- **Body** - Base shape, skin tone
- **Eyes** - Eye shape, color
- **Hair** - Hairstyle, color
- **Facial Features** - Scars, markings, beards

**Clothing:**
- **Shirts/Tops**
- **Pants/Bottoms**
- **Shoes**
- **Accessories** - Hats, glasses, jewelry

**Equipment:**
- **Weapons** - Swords, staves, bows
- **Armor** - Visible equipment changes
- **Shields**

### Character Creation Workflow

**Screenshot: Character Generator interface**
*[Screenshot should show: Preview window, component selection, color customization, export button]*

**Steps:**

1. **Choose base body:**
   - Gender
   - Body type
   - Skin tone

2. **Add features:**
   - Hair (style and color)
   - Eyes (shape and color)
   - Facial features

3. **Dress character:**
   - Select clothing
   - Customize colors
   - Add accessories

4. **Equip items:**
   - Weapon (shows in hand)
   - Armor (visual changes)

5. **Export sprite:**
   - Choose export size
   - Select animations to include
   - Click **Export Character**

Your character sprite is now ready to use!

### Creating NPCs

Use the Character Generator to create diverse NPCs:

**Townspeople:**
- Varied clothing colors
- Different hairstyles and ages
- Appropriate occupational clothing

**Shopkeepers:**
- Aprons or work clothes
- Unique hair/accessories to stand out

**Guards:**
- Armor and weapons
- Uniform colors/style

**Tips:**
- Create 5-10 base NPC templates
- Recolor for variety
- Mix and match for uniqueness

---

## Designing Gameplay

### Combat System

NeonWorks includes a complete **JRPG-style battle system**.

**Battle Flow:**

1. **Encounter triggered** - Random or event-based
2. **Battle transition** - Screen effect
3. **Turn order calculated** - Based on initiative/speed
4. **Player turn:**
   - Attack
   - Skills/Magic
   - Items
   - Defend
   - Run
5. **Enemy turn** - AI-controlled
6. **Repeat until victory or defeat**
7. **Results screen** - Experience, gold, items

**Screenshot: Battle UI during combat**
*[Screenshot should show: Enemy positions, party HP/MP, command menu, battle background]*

### Configuring Battles

**Enemy groups** define what enemies appear together:

```json
{
  "id": "forest_encounter_1",
  "enemies": [
    { "id": "slime", "position": [100, 200] },
    { "id": "slime", "position": [200, 200] },
    { "id": "goblin", "position": [150, 180] }
  ],
  "background": "forest_battle_bg.png",
  "music": "battle_normal.ogg"
}
```

**Configure in Database Editor:**

1. Press `Ctrl+D` for Database
2. Go to **Enemy Groups** tab
3. Click **New Group**
4. Add enemies and set positions
5. Choose background and music

### Magic and Skills

**Skills** include attacks, spells, buffs, and special abilities.

**Skill properties:**

- **Name** - "Fire Blast"
- **Type** - Physical, Magic, Support
- **Target** - Single, All, Self
- **Cost** - MP or HP
- **Power** - Damage/healing amount
- **Effect** - Burn, Poison, Stun, etc.
- **Animation** - Visual effect

**Example spell:**

```json
{
  "id": "fire_blast",
  "name": "Fire Blast",
  "type": "magic",
  "element": "fire",
  "target": "single_enemy",
  "mp_cost": 12,
  "power": 50,
  "effect": {
    "type": "burn",
    "chance": 30,
    "duration": 3
  },
  "animation": "fire_explosion"
}
```

### Items and Equipment

**Item types:**

- **Consumables** - Potions, food, stat boosts
- **Key Items** - Quest items, plot devices
- **Weapons** - Equippable, increase attack
- **Armor** - Equippable, increase defense
- **Accessories** - Equippable, special effects

**Equipment stats:**

```json
{
  "id": "iron_sword",
  "name": "Iron Sword",
  "type": "weapon",
  "subtype": "sword",
  "attack": 15,
  "price": 250,
  "description": "A sturdy iron blade.",
  "equip_requirements": {
    "class": ["warrior", "knight"]
  }
}
```

### Balancing Your Game

**Difficulty curve:**

Early game:
- Enemies: 1-2 per group
- Damage: 5-10 HP per hit
- Player HP: 50-80
- Healing items easily available

Mid game:
- Enemies: 2-4 per group
- Damage: 15-30 HP per hit
- Player HP: 150-250
- Strategic skill use required

Late game:
- Enemies: 3-6 per group, bosses
- Damage: 40-80 HP per hit
- Player HP: 300-500
- Full party strategy needed

**Balancing tips:**

- Playtest frequently
- Watch for difficulty spikes
- Give players options (grinding, equipment, skills)
- Boss fights should be challenging but fair
- Don't make healing too scarce or too plentiful

---

## Testing & Debugging

### The Debug Console

Press `F1` to open the Debug Console.

**Screenshot: Debug Console showing log messages**
*[Screenshot should show: Console window with colored log entries, command input field]*

**Console features:**

- **Log messages** - Info, warnings, errors
- **Command input** - Execute debug commands
- **Filters** - Show only specific message types
- **Copy/export** - Save logs for bug reports

**Useful debug commands:**

```
# Teleport to position
teleport 100 150

# Give item to player
give_item potion 5

# Set variable
set_variable quest_stage 3

# Toggle collision display
show_collision

# Set player health
set_hp 999

# List all active events
list_events

# Clear all enemies
clear_enemies
```

### Common Issues

**Problem: Character falls through floor**

**Solution:**
- Check that ground layer has tiles
- Verify collision layer is set correctly
- Ensure character has Collider component

**Problem: NPC dialogue doesn't trigger**

**Solution:**
- Check NPC has dialogue event assigned
- Verify event trigger type (on interact, on touch)
- Check if conditional requirements are blocking it

**Problem: Map transition doesn't work**

**Solution:**
- Verify transfer event target map exists
- Check target coordinates are valid
- Ensure player can reach transfer tile

**Problem: Battle won't start**

**Solution:**
- Check encounter zone is on correct layer
- Verify enemy group exists in database
- Ensure encounter rate is not 0
- Check if encounters are disabled by switch

**Problem: Items don't appear in inventory**

**Solution:**
- Verify item exists in database
- Check give_item event command syntax
- Ensure inventory is not full (if limit set)

### Playtesting Checklist

Before releasing your game, test:

**Functionality:**
- ✅ All maps accessible
- ✅ All events trigger correctly
- ✅ Combat works (all enemy types)
- ✅ Items and equipment function
- ✅ Quests can be completed
- ✅ No soft-lock scenarios

**Balance:**
- ✅ Difficulty curve is smooth
- ✅ Economy is balanced (gold, items)
- ✅ Character progression feels good
- ✅ Boss fights are challenging but beatable

**Polish:**
- ✅ No typos in dialogue
- ✅ Music and sound effects work
- ✅ Animations play correctly
- ✅ UI is readable and responsive
- ✅ No graphical glitches

**Performance:**
- ✅ Game runs at 60 FPS
- ✅ No lag during battles
- ✅ Loading times are reasonable
- ✅ No crashes or freezes

---

## Exporting Your Game

### Preparing for Export

Before exporting:

1. **Final playthrough** - Complete the game start to finish
2. **Check all assets** - Ensure licensing allows distribution
3. **Review credits** - List asset creators and contributors
4. **Test on different systems** - Windows, Mac, Linux if possible
5. **Create game icon** - 256x256 PNG icon for your game

### Export Process

1. **Open Project Manager** (`F8`)
2. **Select your project**
3. **Click "Export Game"**

**Screenshot: Export dialog with options**
*[Screenshot should show: Platform selection, export options, output directory selection]*

**Export options:**

- **Target Platform:**
  - Windows (.exe)
  - macOS (.app)
  - Linux (.AppImage)
  - All platforms

- **Build Mode:**
  - Debug (larger, includes logs)
  - Release (optimized, smaller)

- **Include Assets:**
  - ✅ Encrypt assets (prevents modification)
  - ✅ Include editor (allows modding)
  - ✅ Include source code

- **Packaging:**
  - Single executable
  - Folder with data files
  - Installer (Windows only)

4. **Click "Export"**

NeonWorks will bundle your game!

### Distribution

**Where to publish:**

- **itch.io** - Indie game platform, easy to use
- **Steam** - Requires Steamworks SDK integration
- **Game Jolt** - Free hosting for indie games
- **Your website** - Direct downloads

**Creating a game page:**

You'll need:
- **Screenshots** - 5-10 images of gameplay
- **Trailer video** - 30-60 seconds (optional but recommended)
- **Description** - What the game is about
- **Features list** - Key selling points
- **System requirements** - From this manual
- **Genre tags** - JRPG, RPG, Turn-Based, etc.

**Pricing:**

- **Free** - Build audience, get feedback
- **Pay what you want** - Let players decide
- **Fixed price** - $2-$15 for indie RPGs

### Licensing and Legal

**Important considerations:**

- **Asset licenses** - Verify you have rights to distribute
- **Engine license** - NeonWorks is open source (check LICENSE file)
- **Game ownership** - You own games you create
- **Trademarks** - Don't use copyrighted game names/characters

**Recommended:**
- Include credits.txt with asset attributions
- Add LICENSE file stating your game's license
- Consider Creative Commons for free games

---

## Advanced Topics

### Scripting with Python

While NeonWorks is designed for visual editing, you can extend it with Python scripts.

**Custom systems:**

```python
# scripts/custom_weather_system.py
from neonworks.core.ecs import System, World

class WeatherSystem(System):
    """Custom weather effects system."""

    def __init__(self):
        super().__init__()
        self.current_weather = "clear"

    def update(self, world: World, delta_time: float):
        # Weather logic here
        if self.current_weather == "rain":
            # Spawn rain particles
            pass
```

See [Creating Systems](creating_systems.md) for more details.

### Custom Components

Create data containers for unique gameplay mechanics:

```python
# scripts/custom_components.py
from dataclasses import dataclass
from neonworks.core.ecs import Component

@dataclass
class FarmingData(Component):
    """Component for farming mechanics."""
    crop_type: str = ""
    growth_stage: int = 0
    days_planted: int = 0
    water_level: int = 100
```

### Plugin System

Extend NeonWorks with plugins:

```
my_project/
├── plugins/
│   ├── day_night_cycle/
│   │   ├── __init__.py
│   │   ├── system.py
│   │   └── config.json
│   └── crafting_system/
│       ├── __init__.py
│       └── recipes.json
```

Plugins can add:
- New systems and components
- Editor tools
- Asset processors
- Export formats

### Modding Support

Allow players to mod your game:

1. **Export with editor included**
2. **Document your data formats**
3. **Provide modding tools**
4. **Create example mods**
5. **Host a modding community**

---

## Troubleshooting

### Performance Issues

**Symptoms:** Low FPS, stuttering, lag

**Solutions:**

1. **Reduce particle effects** - Limit max particles
2. **Optimize maps** - Smaller maps load faster
3. **Limit entities** - Don't spawn hundreds of NPCs
4. **Use sprite atlases** - Combine small images
5. **Lower target FPS** - 30 FPS may be acceptable
6. **Disable unused features** - Turn off systems you don't need

### Installation Problems

**"Module not found: pygame"**

```bash
pip install pygame==2.5.2
```

**"Permission denied"**

```bash
# Use --user flag
pip install --user -r requirements.txt
```

**"Python not found"**

- Ensure Python is in PATH
- Try `python3` instead of `python`
- Reinstall Python with "Add to PATH" checked

### Importing Assets

**"Asset failed to import"**

- Check file format (PNG for images, OGG for audio)
- Verify file isn't corrupted
- Check file permissions
- Try smaller file size

**"Transparency not working"**

- Use PNG format (not JPG)
- Ensure alpha channel exists
- Check transparency color setting

### Maps and Levels

**"Can't place tiles"**

- Verify layer is not locked
- Check tileset is loaded
- Ensure you're in edit mode (not play mode)

**"Player can walk through walls"**

- Check collision layer
- Verify wall tiles have collision enabled
- Ensure collision system is active

### Saving and Loading

**"Save file not found"**

- Check saves/ directory exists
- Verify project path is correct
- Don't move project folder after saving

**"Save file corrupted"**

- Restore from backup (saves/backups/)
- Check JSON syntax if manually edited
- Use in-game save, not manual file edits

### Getting Help

**Resources:**

- **Documentation** - Check docs/ folder
- **Examples** - Study example projects
- **Debug Console** - Read error messages
- **Community Forum** - Ask questions
- **GitHub Issues** - Report bugs

**Reporting bugs:**

Include:
1. NeonWorks version
2. Operating system
3. Steps to reproduce
4. Expected vs actual behavior
5. Debug console output
6. Screenshots if applicable

---

## Additional Resources

### Documentation

- **[Quick Start Guide](quick_start.md)** - Your first RPG in 30 minutes
- **[Event Editor Guide](event_editor_guide.md)** - Event system tutorial
- **[Database Guide](database_guide.md)** - Database management
- **[Character Generator Guide](character_generator_guide.md)** - Character creation
- **[Map Editor Guide](map_editor_guide.md)** - Advanced mapping
- **[Keyboard Shortcuts](keyboard_shortcuts.md)** - Complete shortcut reference

### Tutorials

- **[Making a Lufia Clone](MAKING_A_LUFIA_CLONE.md)** - Complete JRPG tutorial
- **[JRPG Systems Guide](JRPG_SYSTEMS.md)** - Battle system deep dive
- **[Event System](EVENT_SYSTEM.md)** - Event programming
- **[Recipes](RECIPES.md)** - Common patterns and solutions

### Community

- **GitHub Repository** - Source code and issues
- **Discord Server** - Chat with developers
- **Forums** - Discussion and help
- **Showcase** - Share your games!

### Asset Resources

**Graphics:**
- [OpenGameArt.org](https://opengameart.org)
- [itch.io Asset Packs](https://itch.io/game-assets)
- [Kenney.nl](https://kenney.nl)

**Audio:**
- [FreeSFX](https://freesfx.co.uk)
- [Incompetech Music](https://incompetech.com/music)
- [OpenGameArt Audio](https://opengameart.org/art-search-advanced?keys=&field_art_type_tid%5B%5D=13)

**Tools:**
- **Aseprite** - Pixel art editor
- **Tiled** - Map editor (can export to NeonWorks)
- **Audacity** - Audio editing
- **Bfxr** - Sound effect generator

---

## Conclusion

You now have a comprehensive understanding of NeonWorks!

**Next steps:**

1. **Start small** - Create a simple 1-map demo
2. **Experiment** - Try different features and tools
3. **Learn by doing** - Follow the Quick Start guide
4. **Join the community** - Share your progress!
5. **Have fun** - Game development is a creative journey!

**Remember:**
- Every great game started with a single map
- Iteration is key - make it work, then make it better
- Don't be afraid to ask for help
- Your unique vision is what makes your game special

**Happy game making!**

---

**Version History:**

- **1.0** (2025-11-15) - Initial comprehensive user manual

**Contributing:**

Found an error or want to improve this manual? Contributions welcome!

---

**NeonWorks Team**
Building tools for your creativity.
