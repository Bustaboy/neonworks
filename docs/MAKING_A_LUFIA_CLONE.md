# Making a Lufia-Style JRPG with NeonWorks

**Version:** 2.0
**Engine Version:** 0.1.0
**Last Updated:** 2025-11-16

Step-by-step guide to creating a classic JRPG like Lufia using the NeonWorks engine with its comprehensive visual editor suite.

## Table of Contents

1. [Project Setup](#project-setup)
2. [Using the Visual Launcher](#using-the-visual-launcher)
3. [Using the Visual Editors](#using-the-visual-editors)
4. [Creating Your First Town](#creating-your-first-town)
5. [Using the Map Editor](#using-the-map-editor)
6. [Creating the Database](#creating-the-database)
7. [Adding Party Members](#adding-party-members)
8. [Setting Up Combat](#setting-up-combat)
9. [Creating Events and Dialogue](#creating-events-and-dialogue)
10. [Creating a Dungeon](#creating-a-dungeon)
11. [Implementing Puzzles](#implementing-puzzles)
12. [Adding Boss Battles](#adding-boss-battles)
13. [World Map and Travel](#world-map-and-travel)
14. [Equipment and Shops](#equipment-and-shops)
15. [Polishing Your Game](#polishing-your-game)
16. [Advanced Features](#advanced-features)

---

## Project Setup

### Prerequisites

Make sure you have NeonWorks installed:

```bash
# Clone the repository
git clone https://github.com/Bustaboy/neonworks.git
cd neonworks

# Install dependencies
pip install -r requirements.txt
```

### Quick Start with the Visual Launcher

**Recommended Approach:** Use the visual launcher (Unity Hub-style) to create your project:

```bash
# Start the visual launcher
python launcher.py

# Or use convenience scripts
./launch_neonworks.sh        # Linux/Mac
launch_neonworks.bat         # Windows
```

Then:
1. Click **"Create New Project"**
2. Select **"Turn-Based RPG"** template
3. Name it **"Lufia Clone"**
4. Click **"Create"**

The launcher will automatically create the complete project structure with all necessary files!

### Manual Setup (Alternative)

If you prefer manual setup:

```bash
# Create project using CLI
python cli.py create-project lufia_clone --template turn_based_rpg
cd projects/lufia_clone
```

### Project Configuration

Your project.json will be automatically created with sensible defaults:

```json
{
  "metadata": {
    "name": "Lufia Clone",
    "version": "1.0.0",
    "description": "A classic JRPG inspired by Lufia",
    "author": "Your Name",
    "engine_version": "0.1.0"
  },
  "paths": {
    "assets": "assets",
    "maps": "assets/maps",
    "scripts": "scripts",
    "saves": "saves"
  },
  "settings": {
    "window_title": "Lufia Clone",
    "window_width": 800,
    "window_height": 600,
    "tile_size": 32,
    "enable_jrpg_mode": true,
    "battle_style": "jrpg",
    "encounter_rate": 25.0,
    "initial_zone": "starting_town"
  }
}
```

### 3. Create Directory Structure

```
lufia_clone/
├── project.json
├── assets/
│   ├── maps/
│   ├── sprites/
│   │   ├── characters/
│   │   ├── enemies/
│   │   ├── tilesets/
│   │   └── ui/
│   ├── sounds/
│   └── music/
├── scripts/
│   └── game.py
└── saves/
```

---

## Using the Visual Launcher

NeonWorks features a **Unity Hub-style visual launcher** that makes project management easy.

### Launcher Features

- **Visual Project Browser** - Browse all your projects with project cards
- **Recent Projects** - Quick access to recently opened projects
- **Template Selection** - Choose from 4 built-in templates:
  - Basic Game
  - Turn-Based RPG ⭐ (Recommended for Lufia clone)
  - Base Builder
  - JRPG Demo
- **One-Click Launch** - Launch directly into editor mode

### Using the Launcher

1. **Start the launcher:**
   ```bash
   python launcher.py
   ```

2. **Create new project:**
   - Click "Create New Project"
   - Select "Turn-Based RPG" template
   - Enter project name
   - Click "Create"

3. **Open existing project:**
   - Click on project card in browser
   - Or select from recent projects list

4. **Launch into editor:**
   - Select your project
   - Click "Launch"
   - Engine starts with all visual editors available

See [LAUNCHER_README.md](../LAUNCHER_README.md) for detailed documentation.

---

## Using the Visual Editors

NeonWorks includes **30+ visual editors** accessible via hotkeys. You don't need to write JSON files manually!

### Essential Editors for JRPG Development

| Hotkey | Editor | Purpose |
|--------|--------|---------|
| **F4** | **Level Builder** | Design maps, place tiles, create layouts |
| **Ctrl+M** | **Map Manager** | Manage multiple maps, switch between them |
| **Ctrl+L** | **Layer Panel** | Manage map layers (ground, objects, overhead) |
| **Ctrl+T** | **Tileset Picker** | Select tilesets and tiles |
| **F11** | **Autotile Editor** | Configure autotiling for walls, water, etc. |
| **Ctrl+E** | **Event Editor** | Create NPCs, dialogues, triggers |
| **Ctrl+D** | **Database Manager** | Define characters, enemies, items, skills |
| **Ctrl+G** | **Character Generator** | Generate character sprites and stats |
| **F6** | **Quest Editor** | Create quests and dialogue trees |
| **F5** | **Navmesh Editor** | Define walkable areas |
| **F7** | **Asset Browser** | Manage all project assets |
| **F2** | **Settings** | Configure project settings |

### Map Editing Tools (When in Map Editor)

| Key | Tool | Purpose |
|-----|------|---------|
| **P** | Pencil Tool | Draw individual tiles |
| **E** | Eraser Tool | Erase tiles |
| **F** | Fill Tool | Bucket fill areas |
| **S** | Select Tool | Select regions |
| **B** | Stamp Tool | Stamp/clone tile patterns |
| **R** | Shape Tool | Draw rectangles, circles |
| **I** | Eyedropper | Pick tiles from map |

### Additional Tools

| Hotkey | Editor | Purpose |
|--------|--------|---------|
| **F1** | Debug Console | View logs, run commands |
| **F8** | Project Manager | Manage project files |
| **Ctrl+H** | History Viewer | View undo/redo history |
| **Ctrl+Space** | AI Assistant | AI-powered assistance |
| **Shift+F7** | AI Animator | AI animation generation |
| **Ctrl+Shift+K** | Shortcuts Overlay | View all keyboard shortcuts |

### Workspace System

NeonWorks includes a workspace management system:

- Save custom layouts
- Arrange editor panels
- Create tool presets
- Quick workspace switching

See [ui/WORKSPACE_SYSTEM.md](../ui/WORKSPACE_SYSTEM.md) for details.

---

## Creating Your First Town

### Using the Visual Map Editor (Recommended)

Instead of writing JSON manually, use the visual editors:

#### 1. Open Map Manager (Ctrl+M)

1. Press **Ctrl+M** to open Map Manager
2. Click **"Create New Map"**
3. Enter map details:
   - Name: "Alekia Village"
   - Width: 30 tiles
   - Height: 20 tiles
   - Tile Size: 32 pixels
4. Click **"Create"**

#### 2. Select Tileset (Ctrl+T)

1. Press **Ctrl+T** to open Tileset Picker
2. Click **"Add Tileset"**
3. Browse to `assets/sprites/tilesets/town.png`
4. Configure:
   - Tile Width: 32
   - Tile Height: 32
   - Columns: 10
5. Click **"Load Tileset"**

#### 3. Create Layers (Ctrl+L)

1. Press **Ctrl+L** to open Layer Panel
2. Create three layers:
   - **"ground"** - Base ground tiles
   - **"buildings"** - Buildings and obstacles
   - **"overhead"** - Trees, roofs (rendered above player)
3. Set ground layer as active

#### 4. Draw the Map (F4)

1. Press **F4** to open Level Builder
2. Select ground layer
3. Use **Pencil Tool (P)** to draw grass tiles
4. Use **Fill Tool (F)** to fill large areas
5. Switch to buildings layer
6. Draw building walls and roofs
7. Use **Stamp Tool (B)** to copy/paste building patterns
8. Use **Shape Tool (R)** for rectangular buildings

#### 5. Configure Map Properties

In the Map Manager (Ctrl+M), set:
- Background Music: "music/town_theme.mp3"
- Encounter Rate: 0.0 (no battles in town)
- Default Spawn Point: (15, 18)

### Manual Map Creation (Alternative)

If you prefer to work with JSON directly, create `assets/maps/starting_town.json`:

```json
{
  "name": "Alekia Village",
  "width": 30,
  "height": 20,
  "tile_size": 32,
  "background_music": "music/town_theme.mp3",
  "encounter_rate": 0.0,
  "spawn_points": [
    {
      "name": "default",
      "x": 15,
      "y": 18,
      "direction": "UP"
    },
    {
      "name": "from_world_map",
      "x": 15,
      "y": 19,
      "direction": "UP"
    },
    {
      "name": "player_house",
      "x": 5,
      "y": 5,
      "direction": "DOWN"
    }
  ],
  "tilemap": {
    "tilesets": [
      {
        "name": "town",
        "image": "assets/sprites/tilesets/town.png",
        "tile_width": 32,
        "tile_height": 32,
        "columns": 10,
        "tile_count": 100
      }
    ],
    "layers": [
      {
        "name": "ground",
        "visible": true,
        "data": "..."
      },
      {
        "name": "buildings",
        "visible": true,
        "data": "..."
      },
      {
        "name": "overhead",
        "visible": true,
        "data": "..."
      }
    ]
  },
  "collision": {
    "layer": "buildings",
    "blocked_tiles": [10, 11, 12, 13, 14, 15, 20, 21, 22]
  },
  "npcs": [
    {
      "x": 15,
      "y": 10,
      "sprite": "assets/sprites/characters/guard.png",
      "behavior": "static",
      "dialogue_id": "guard_intro",
      "can_talk": true
    },
    {
      "x": 8,
      "y": 12,
      "sprite": "assets/sprites/characters/villager.png",
      "behavior": "wander",
      "wander_radius": 3,
      "dialogue_id": "villager_greeting"
    },
    {
      "x": 20,
      "y": 8,
      "sprite": "assets/sprites/characters/shopkeeper.png",
      "behavior": "static",
      "dialogue_id": "shop_greeting"
    }
  ],
  "objects": [
    {
      "x": 12,
      "y": 14,
      "sprite": "assets/sprites/objects/sign.png",
      "is_solid": false,
      "can_interact": true,
      "interaction_type": "examine",
      "dialogue_id": "town_sign"
    }
  ],
  "triggers": [
    {
      "x": 15,
      "y": 20,
      "target_zone": "world_map",
      "target_spawn": "alekia_exit",
      "transition_type": "fade"
    },
    {
      "x": 5,
      "y": 6,
      "target_zone": "player_house",
      "target_spawn": "default",
      "transition_type": "instant"
    }
  ]
}
```

---

## Using the Map Editor

The Map Editor is one of the most powerful tools in NeonWorks. Here's a detailed workflow:

### Creating Your Town Layout

#### Step 1: Plan Your Town

Before opening the editor, sketch out:
- Town entrances/exits
- Building locations (houses, shops, inn)
- NPC positions
- Important landmarks (fountain, statue, well)
- Trigger zones (transitions to other maps)

#### Step 2: Layer Strategy

Use layers effectively:
1. **Ground Layer** - Base terrain (grass, dirt paths, stones)
2. **Buildings Layer** - Walls, doors, fences (set collision here)
3. **Details Layer** - Flowers, signs, small decorations
4. **Overhead Layer** - Tree foliage, roof overhangs

#### Step 3: Drawing Workflow

1. **Fill ground layer** with base terrain using Fill Tool (F)
2. **Draw paths** using Pencil Tool (P) or Shape Tool (R)
3. **Place buildings** using Stamp Tool (B) for repeated patterns
4. **Add details** like flowers, barrels, signs
5. **Configure collision** by marking solid tiles in buildings layer

#### Step 4: Configure Autotiling (F11)

1. Press **F11** to open Autotile Editor
2. Configure autotile rules for:
   - Water edges
   - Cliff edges
   - Building walls
   - Fence connections
3. The editor will automatically connect tiles based on neighbors

### Map Editor Tips

- **Grid Snapping**: Hold Shift while drawing to snap to grid
- **Multi-Select**: Hold Ctrl and drag to select multiple tiles
- **Copy/Paste**: Ctrl+C to copy, Ctrl+V to paste selections
- **Undo/Redo**: Ctrl+Z to undo, Ctrl+Y to redo (persistent across sessions!)
- **Minimap**: View entire map at once for better overview
- **Zoom**: Mouse wheel to zoom in/out
- **Pan**: Middle mouse button to pan camera

See [docs/map_editor_guide.md](map_editor_guide.md) for complete tutorial.

---

## Creating the Database

The Database Manager (Ctrl+D) is where you define all game data: characters, enemies, items, skills, and more.

### Setting Up Your JRPG Database

#### 1. Open Database Manager (Ctrl+D)

Press **Ctrl+D** to open the Database Manager.

#### 2. Create Character Classes

1. Switch to **"Classes"** tab
2. Click **"New Class"**
3. Define classes:
   - **Hero** - Balanced stats, can use swords
   - **Mage** - High magic, low defense
   - **Warrior** - High HP/attack, low magic
   - **Priest** - High magic defense, healing spells

For each class, configure:
- Base stats (HP, MP, Attack, Defense, etc.)
- Stat growth per level
- Equipment restrictions
- Learnable skills

#### 3. Create Characters

1. Switch to **"Characters"** tab
2. Click **"New Character"**
3. Create Maxim (Hero):
   - Name: "Maxim"
   - Class: Hero
   - Initial Level: 1
   - Portrait: `assets/sprites/portraits/maxim.png`
   - Sprite: `assets/sprites/characters/hero.png`
   - Starting Skills: ["Attack", "Defend"]
   - Stat Distribution: Balanced

4. Repeat for party members:
   - **Selan** (Mage) - High magic attack
   - **Guy** (Warrior) - High physical attack
   - **Artea** (Priest) - Healing specialist

#### 4. Create Enemies

1. Switch to **"Enemies"** tab
2. Click **"New Enemy"**
3. Create basic enemies:

**Slime:**
- HP: 20
- MP: 0
- Attack: 5
- Defense: 3
- Speed: 4
- EXP: 5
- Gold: 3
- Weak to: Fire
- Sprite: `assets/sprites/enemies/slime.png`

**Goblin:**
- HP: 35
- MP: 5
- Attack: 8
- Defense: 5
- Speed: 6
- EXP: 10
- Gold: 7
- Weak to: Lightning
- Skills: ["Slash"]

#### 5. Create Skills/Spells

1. Switch to **"Skills"** tab
2. Click **"New Skill"**

Create basic spells:

**Fire:**
- Type: Magic
- Element: Fire
- MP Cost: 8
- Power: 30
- Target: Single Enemy
- Animation: Fire burst effect

**Heal:**
- Type: Magic
- Element: Light
- MP Cost: 5
- Power: 30 (healing)
- Target: Single Ally
- Animation: Sparkle effect

**Ice Storm:**
- Type: Magic
- Element: Ice
- MP Cost: 15
- Power: 50
- Target: All Enemies
- Animation: Ice shard rain

#### 6. Create Items

1. Switch to **"Items"** tab
2. Create consumables:

**Potion:**
- Type: Consumable
- Effect: Restore 50 HP
- Target: Single Ally
- Price: 10 Gold
- Can use in battle: Yes

**Hi-Potion:**
- Type: Consumable
- Effect: Restore 150 HP
- Price: 50 Gold

**Magic Water:**
- Type: Consumable
- Effect: Restore 30 MP
- Price: 40 Gold

3. Create equipment:

**Bronze Sword:**
- Type: Weapon
- Attack: +10
- Equip: Hero, Warrior
- Price: 100 Gold

**Leather Armor:**
- Type: Armor
- Defense: +8
- Equip: All
- Price: 80 Gold

### Database Manager Features

- **Import/Export** - Share database across projects
- **Bulk Edit** - Edit multiple entries at once
- **Formula Editor** - Create custom stat calculation formulas
- **Preview** - Preview how characters/enemies will look in battle
- **Search** - Quickly find entries by name or property

---

## Creating Events and Dialogue

The Event Editor (Ctrl+E) lets you create NPCs, dialogue trees, and scripted events visually.

### Creating Your First NPC

#### 1. Open Event Editor (Ctrl+E)

1. Open the map in Map Manager (Ctrl+M)
2. Press **Ctrl+E** to open Event Editor
3. Click **"New Event"** or click on map where you want NPC

#### 2. Configure NPC Appearance

- **Name**: "Town Guard"
- **Sprite**: `assets/sprites/characters/guard.png`
- **Position**: (15, 10)
- **Facing**: Down
- **Movement**: Static
- **Through**: No (blocks player)

#### 3. Create Dialogue

Click **"Edit Dialogue"** to open the dialogue tree editor:

1. **Add greeting node:**
   ```
   "Welcome to Alekia Village, traveler!"
   ```

2. **Add choice node:**
   ```
   "Can I help you?"
   → "Where is the inn?" → [Show inn location on map]
   → "Any trouble lately?" → [Quest hook dialogue]
   → "No thanks." → [End dialogue]
   ```

3. **Add conditional dialogue:**
   - If quest "Find Lost Cat" active:
     ```
     "Did you find Mrs. Henderson's cat yet?"
     ```
   - If quest completed:
     ```
     "Thanks for finding that cat!"
     ```

#### 4. Add Event Commands

Events can execute commands when triggered:

**Event Page 1** (Before quest):
```
Trigger: Action Button
Commands:
  - Show Text: "Welcome to Alekia Village!"
  - Show Choices: ["Where's the inn?", "Goodbye"]
    → Choice 0: Show Text: "The inn is north of here."
    → Choice 1: End
```

**Event Page 2** (During quest):
```
Condition: Quest "Find Lost Cat" active
Trigger: Action Button
Commands:
  - Show Text: "Any luck finding that cat?"
```

**Event Page 3** (Quest complete):
```
Condition: Quest "Find Lost Cat" complete
Trigger: Player Touch
Commands:
  - Show Text: "Thanks again for your help!"
```

### Event Editor Features

- **Visual Node Editor** - Drag-and-drop dialogue flow
- **Event Pages** - Multiple conditional states per NPC
- **Command Library** - 50+ built-in commands:
  - Show Text
  - Show Choices
  - Transfer Player
  - Start Battle
  - Change Gold
  - Change Items
  - Play Sound
  - Show Animation
  - Conditional Branch
  - Set Variable
  - Control Switches
- **Preview Mode** - Test events in-editor
- **Copy/Paste Events** - Reuse event logic
- **Event Templates** - Pre-made event patterns

### Creating Shops

Use the Event Editor to create shops:

1. Create NPC shopkeeper
2. Add dialogue: "Welcome to my shop!"
3. Add command: **"Open Shop"**
4. Configure shop inventory:
   - Potion (10 Gold)
   - Hi-Potion (50 Gold)
   - Magic Water (40 Gold)
   - Bronze Sword (100 Gold)
   - Leather Armor (80 Gold)
5. Set buy/sell ratio (default 50% sell price)

### Creating Inns

1. Create NPC innkeeper
2. Add dialogue: "Rest here for 10 Gold?"
3. Add choice command:
   - Yes → Charge 10 Gold → Heal Party → Play jingle → Show Text: "Have a good night!"
   - No → End

---

### 2. Create the Main Game Script

Create `scripts/game.py`:

```python
import pygame
from neonworks.core.ecs import World
from neonworks.core.events import get_event_manager
from neonworks.input.input_manager import InputManager
from neonworks.rendering.renderer import Renderer
from neonworks.rendering.camera import Camera
from neonworks.systems.exploration import ExplorationSystem
from neonworks.systems.zone_system import ZoneSystem
from neonworks.systems.jrpg_battle_system import JRPGBattleSystem
from neonworks.systems.magic_system import MagicSystem
from neonworks.systems.random_encounters import RandomEncounterSystem
from neonworks.systems.puzzle_system import PuzzleSystem
from neonworks.systems.boss_ai import BossAISystem

class LufiaGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Lufia Clone")

        # Core systems
        self.world = World()
        self.event_manager = EventManager()
        self.input_manager = InputManager()
        self.camera = Camera(800, 600)
        self.renderer = Renderer(800, 600, 32, self.camera)

        # JRPG systems
        self.exploration_system = ExplorationSystem(
            self.input_manager,
            self.event_manager
        )
        self.zone_system = ZoneSystem(self.event_manager, "assets")
        self.battle_system = JRPGBattleSystem(self.event_manager)
        self.magic_system = MagicSystem(self.event_manager)
        self.encounter_system = RandomEncounterSystem(self.event_manager)
        self.puzzle_system = PuzzleSystem(self.event_manager)
        self.boss_ai_system = BossAISystem(self.event_manager)

        # Add systems to world
        self.world.add_system(self.exploration_system)
        self.world.add_system(self.zone_system)
        self.world.add_system(self.battle_system)
        self.world.add_system(self.magic_system)
        self.world.add_system(self.encounter_system)
        self.world.add_system(self.puzzle_system)
        self.world.add_system(self.boss_ai_system)

        # Create player
        self.player = self.create_player()

        # Load starting zone
        self.zone_system.load_zone(self.world, "starting_town", "default")

        # Game state
        self.running = True
        self.clock = pygame.time.Clock()

    def create_player(self):
        """Create player character"""
        from neonworks.core.ecs import Transform, GridPosition, Sprite
        from neonworks.gameplay.movement import Movement, Direction, AnimationState
        from neonworks.gameplay.combat import Health
        from neonworks.gameplay.jrpg_combat import (
            JRPGStats, MagicPoints, SpellList, PartyMember
        )

        player = self.world.create_entity()
        player.add_tag("player")

        # Position
        player.add_component(Transform(x=15*32, y=18*32))
        player.add_component(GridPosition(grid_x=15, grid_y=18))

        # Visual
        player.add_component(Sprite(
            texture="assets/sprites/characters/hero.png",
            width=32,
            height=32
        ))

        # Movement
        player.add_component(Movement(speed=4.0, facing=Direction.DOWN))
        player.add_component(AnimationState(
            current_state="idle",
            current_direction=Direction.DOWN
        ))

        # Combat
        player.add_component(Health(max_hp=100, hp=100))
        player.add_component(MagicPoints(max_mp=30, current_mp=30))
        player.add_component(JRPGStats(
            level=1,
            attack=10,
            defense=8,
            magic_attack=8,
            magic_defense=7,
            speed=10,
            luck=5
        ))

        # Magic
        player.add_component(SpellList(learned_spells=["heal"]))

        # Party
        player.add_component(PartyMember(
            character_id="hero",
            character_name="Maxim",
            character_class="hero",
            party_index=0,
            is_active=True
        ))

        return player

    def run(self):
        """Main game loop"""
        while self.running:
            delta_time = self.clock.tick(60) / 1000.0

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.input_manager.process_event(event)

            # Update
            self.input_manager.update(delta_time)
            self.world.update(delta_time)
            self.event_manager.process_events()

            # Render
            self.screen.fill((0, 0, 0))
            self.renderer.render_world(self.world)
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    game = LufiaGame()
    game.run()
```

---

## Adding Party Members

### Using the Character Generator (Ctrl+G)

NeonWorks includes an AI-powered Character Generator that can create complete character definitions including stats, skills, and even generate sprite concepts!

#### 1. Open Character Generator (Ctrl+G)

Press **Ctrl+G** to open the Character Generator.

#### 2. Generate Characters

For each party member:

**Maxim (Hero):**
1. Click **"New Character"**
2. Enter name: "Maxim"
3. Select archetype: "Balanced Hero"
4. AI will suggest:
   - Base stats distribution
   - Starting equipment
   - Skill progression
   - Sprite style recommendations
5. Customize as needed
6. Click **"Generate"**

**Selan (Mage):**
1. New Character → "Selan"
2. Archetype: "Offensive Mage"
3. AI suggests:
   - High Magic Attack, low Defense
   - Fire/Ice/Lightning spell progression
   - Staff weapon proficiency
4. Adjust stat ratios to your preference
5. Generate

**Guy (Warrior):**
1. New Character → "Guy"
2. Archetype: "Tank Warrior"
3. AI suggests:
   - High HP and Defense
   - Sword/Axe skills
   - Physical damage focus
4. Generate

**Artea (Priest):**
1. New Character → "Artea"
2. Archetype: "Healer/Support"
3. AI suggests:
   - High Magic Defense
   - Healing and buff spells
   - Support skill progression
4. Generate

#### 3. Export to Database

After generating characters:
1. Click **"Export to Database"**
2. Characters are automatically added to the Database Manager
3. You can further edit them in Database Manager (Ctrl+D)

#### 4. Generate Sprite Concepts (Optional)

The Character Generator can create sprite mockups:
1. Select character
2. Click **"Generate Sprite Concept"**
3. AI creates a pixelart-style concept based on character description
4. Export as template for your pixel artist
5. Or use built-in sprite from templates

### Manual Character Creation

If you prefer to code characters manually:

```python
def create_party_member(self, character_data):
    """Create a party member entity"""
    member = self.world.create_entity()
    member.add_tag("party_member")

    # Position (same as player initially)
    member.add_component(Transform())
    member.add_component(GridPosition())

    # Visual
    member.add_component(Sprite(
        texture=character_data["sprite"],
        width=32,
        height=32
    ))

    # Combat stats
    member.add_component(Health(
        max_hp=character_data["hp"],
        hp=character_data["hp"]
    ))
    member.add_component(MagicPoints(
        max_mp=character_data["mp"],
        current_mp=character_data["mp"]
    ))
    member.add_component(JRPGStats(
        level=character_data["level"],
        attack=character_data["attack"],
        defense=character_data["defense"],
        magic_attack=character_data["magic_attack"],
        magic_defense=character_data["magic_defense"],
        speed=character_data["speed"]
    ))

    # Spells
    member.add_component(SpellList(
        learned_spells=character_data["spells"]
    ))

    # Party info
    member.add_component(PartyMember(
        character_id=character_data["id"],
        character_name=character_data["name"],
        character_class=character_data["class"],
        party_index=character_data["index"]
    ))

    return member

# Example party members (like Lufia characters)
party_members = [
    {
        "id": "selan",
        "name": "Selan",
        "class": "mage",
        "level": 1,
        "hp": 80,
        "mp": 50,
        "attack": 7,
        "defense": 6,
        "magic_attack": 15,
        "magic_defense": 12,
        "speed": 12,
        "spells": ["fire", "ice", "heal"],
        "sprite": "assets/sprites/characters/selan.png",
        "index": 1
    },
    {
        "id": "guy",
        "name": "Guy",
        "class": "warrior",
        "level": 1,
        "hp": 120,
        "mp": 10,
        "attack": 15,
        "defense": 12,
        "magic_attack": 5,
        "magic_defense": 6,
        "speed": 8,
        "spells": [],
        "sprite": "assets/sprites/characters/guy.png",
        "index": 2
    },
    {
        "id": "artea",
        "name": "Artea",
        "class": "priest",
        "level": 1,
        "hp": 90,
        "mp": 60,
        "attack": 8,
        "defense": 7,
        "magic_attack": 12,
        "magic_defense": 15,
        "speed": 11,
        "spells": ["heal", "cure", "protect"],
        "sprite": "assets/sprites/characters/artea.png",
        "index": 3
    }
]

# Create party
for member_data in party_members:
    self.create_party_member(member_data)
```

---

## Setting Up Combat

### Creating Enemies

```python
def create_enemy(world, enemy_id, level):
    """Create an enemy entity"""
    from neonworks.core.ecs import Sprite
    from neonworks.gameplay.jrpg_combat import (
        EnemyData, ElementalResistances, BattleRewards, BattleAI
    )

    enemy = world.create_entity()
    enemy.add_tag("enemy")

    enemy_templates = {
        "slime": {
            "name": "Slime",
            "sprite": "assets/sprites/enemies/slime.png",
            "hp": 20,
            "mp": 0,
            "attack": 5,
            "defense": 3,
            "magic_attack": 2,
            "magic_defense": 2,
            "speed": 4,
            "exp": 5,
            "gold": 3,
            "weak_to": ElementType.FIRE
        },
        "goblin": {
            "name": "Goblin",
            "sprite": "assets/sprites/enemies/goblin.png",
            "hp": 35,
            "mp": 5,
            "attack": 8,
            "defense": 5,
            "magic_attack": 3,
            "magic_defense": 4,
            "speed": 6,
            "exp": 10,
            "gold": 7,
            "weak_to": ElementType.LIGHTNING
        },
        # Add more enemies...
    }

    template = enemy_templates.get(enemy_id)
    if not template:
        return None

    # Visual
    enemy.add_component(Sprite(
        texture=template["sprite"],
        width=48,
        height=48
    ))

    # Combat
    enemy.add_component(Health(
        max_hp=template["hp"] + level * 5,
        hp=template["hp"] + level * 5
    ))
    enemy.add_component(MagicPoints(
        max_mp=template["mp"],
        current_mp=template["mp"]
    ))
    enemy.add_component(JRPGStats(
        level=level,
        attack=template["attack"] + level,
        defense=template["defense"] + level // 2,
        magic_attack=template["magic_attack"],
        magic_defense=template["magic_defense"],
        speed=template["speed"]
    ))

    # Resistances
    resistances = {}
    if "weak_to" in template:
        resistances[template["weak_to"]] = 1.5
    enemy.add_component(ElementalResistances(resistances=resistances))

    # AI
    enemy.add_component(BattleAI(ai_type="basic"))

    # Rewards
    enemy.add_component(BattleRewards(
        experience=template["exp"] * level,
        gold=template["gold"] * level,
        items=[
            {"item_id": "potion", "chance": 20.0, "quantity": 1}
        ]
    ))

    # Enemy data
    enemy.add_component(EnemyData(
        enemy_id=enemy_id,
        enemy_name=template["name"],
        enemy_type="normal"
    ))

    return enemy
```

---

## Creating a Dungeon

### Dungeon Map Example

Create `assets/maps/ancient_cave.json`:

```json
{
  "name": "Ancient Cave",
  "width": 40,
  "height": 30,
  "encounter_rate": 35.0,
  "encounter_table": "cave_encounters",
  "background_music": "music/dungeon_theme.mp3",
  "spawn_points": [
    {
      "name": "entrance",
      "x": 2,
      "y": 2,
      "direction": "RIGHT"
    },
    {
      "name": "boss_room",
      "x": 38,
      "y": 28,
      "direction": "UP"
    }
  ],
  "tilemap": {
    "tilesets": [
      {
        "name": "cave",
        "image": "assets/sprites/tilesets/cave.png",
        "tile_width": 32,
        "tile_height": 32,
        "columns": 10,
        "tile_count": 100
      }
    ],
    "layers": [
      {
        "name": "floor",
        "data": "..."
      },
      {
        "name": "walls",
        "data": "..."
      }
    ]
  },
  "collision": {
    "layer": "walls",
    "blocked_tiles": [1, 2, 3, 4, 5, 6, 7, 8, 9]
  }
}
```

---

## Implementing Puzzles

### Four-Switch Puzzle Example

```python
def create_four_switch_puzzle(world):
    """
    Classic Lufia-style puzzle: Four switches must be in correct positions.
    """
    from neonworks.gameplay.puzzle_objects import Switch, Door, PuzzleController

    # Create switches
    switch_positions = [(5, 5), (15, 5), (5, 15), (15, 15)]
    switch_entities = []

    for i, (x, y) in enumerate(switch_positions):
        switch = world.create_entity()
        switch.add_component(GridPosition(grid_x=x, grid_y=y))
        switch.add_component(Switch(
            switch_type="toggle",
            target_ids=[f"puzzle_controller"]
        ))
        switch_entities.append(switch)

    # Create door
    door = world.create_entity()
    door.add_component(GridPosition(grid_x=20, grid_y=10))
    door.add_component(Door(is_locked=True, requires_switch=True))
    door.add_component(Collider2D(is_solid=True))

    # Create puzzle controller
    controller = world.create_entity()
    controller.add_component(PuzzleController(
        puzzle_id="four_switch_puzzle",
        puzzle_type="switch_combination",
        required_switches=[e.id for e in switch_entities],
        required_states=[True, False, True, True],  # The solution!
        reward_target_ids=[door.id]
    ))

    return controller
```

### Block and Plate Puzzle

```python
def create_block_puzzle(world):
    """Push blocks onto pressure plates to open doors"""
    from neonworks.gameplay.puzzle_objects import PushableBlock, PressurePlate, Door

    # Create pressure plates
    plate1 = world.create_entity()
    plate1.add_component(GridPosition(grid_x=10, grid_y=10))
    plate1.add_component(PressurePlate(
        required_weight=1,
        target_ids=["door1"]
    ))

    plate2 = world.create_entity()
    plate2.add_component(GridPosition(grid_x=15, grid_y=10))
    plate2.add_component(PressurePlate(
        required_weight=1,
        target_ids=["door2"]
    ))

    # Create pushable blocks
    block1 = world.create_entity()
    block1.add_component(GridPosition(grid_x=8, grid_y=8))
    block1.add_component(PushableBlock(weight=1))
    block1.add_component(Sprite(texture="assets/sprites/objects/block.png"))

    block2 = world.create_entity()
    block2.add_component(GridPosition(grid_x=17, grid_y=8))
    block2.add_component(PushableBlock(weight=1))

    # Create doors
    door1 = world.create_entity()
    door1.add_component(GridPosition(grid_x=10, grid_y=15))
    door1.add_component(Door(is_locked=True))

    door2 = world.create_entity()
    door2.add_component(GridPosition(grid_x=15, grid_y=15))
    door2.add_component(Door(is_locked=True))
```

---

## Adding Boss Battles

### Creating a Dungeon Boss

```python
from neonworks.systems.boss_ai import create_boss_entity, BOSS_TEMPLATES

def setup_boss_encounter(world, boss_id="skeleton_king"):
    """Setup a boss encounter"""
    # Create boss
    boss = create_boss_entity(
        world,
        boss_template=BOSS_TEMPLATES[boss_id],
        level=10
    )

    # Position in boss room
    boss.add_component(GridPosition(grid_x=20, grid_y=15))

    # Register with boss AI system
    boss_ai_system = world.get_system(BossAISystem)
    if boss_ai_system:
        boss_ai_system.register_boss(boss)

    return boss
```

### Scripted Boss Battle

```python
def trigger_boss_battle(world, player, boss):
    """Trigger a boss battle with cutscene"""
    from neonworks.systems.jrpg_battle_system import JRPGBattleSystem

    # Get party
    party = world.get_entities_with_tag("party_member")
    party_list = [player] + [m for m in party if m.has_component(PartyMember)]

    # Get battle system
    battle_system = world.get_system(JRPGBattleSystem)

    # Play boss intro dialogue
    event_manager.emit(Event(
        EventType.CUSTOM,
        {
            "type": "dialogue",
            "text": "You dare challenge the Skeleton King?",
            "speaker": "Skeleton King"
        }
    ))

    # Start boss battle
    battle_system.start_battle(
        world,
        party=party_list[:4],  # Max 4 party members
        enemies=[boss],
        can_escape=False,
        is_boss=True
    )
```

---

## World Map and Travel

### Creating an Overworld

```json
{
  "name": "World Map",
  "width": 100,
  "height": 100,
  "encounter_rate": 25.0,
  "encounter_table": "overworld",
  "background_music": "music/overworld_theme.mp3",
  "spawn_points": [
    {
      "name": "alekia_exit",
      "x": 50,
      "y": 60,
      "direction": "DOWN"
    }
  ],
  "triggers": [
    {
      "x": 50,
      "y": 60,
      "target_zone": "alekia_village",
      "target_spawn": "from_world_map"
    },
    {
      "x": 30,
      "y": 40,
      "target_zone": "ancient_cave",
      "target_spawn": "entrance"
    }
  ]
}
```

---

## Equipment and Shops

### Equipment System (TODO)

This would integrate with the existing inventory system. Basic structure:

```python
class EquipmentSlot(Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    SHIELD = "shield"
    ACCESSORY = "accessory"

@dataclass
class Equipment(Component):
    equipped: Dict[EquipmentSlot, Optional[str]] = field(default_factory=dict)
```

---

## Polishing Your Game

### Adding Polish

1. **Save/Load System**: Use NeonWorks' built-in serialization
2. **Music and Sound**: Add BGM for towns, dungeons, battles
3. **Battle Animations**: Add spell effects and attack animations
4. **UI Polish**: Create custom battle UI, menus
5. **Particle Effects**: Victory sparkles, spell effects
6. **Screen Transitions**: Fade in/out for zone changes

### Balancing

- **Enemy Stats**: Scale with level appropriately
- **Encounter Rate**: 20-30 for overworld, 35-45 for dungeons
- **Spell Costs**: Low (5MP), Medium (15MP), High (30MP), Ultimate (50MP+)
- **Boss HP**: 3-5x normal enemy HP for that area

---

## Complete Example: First Hour of Gameplay

1. Start in Alekia Village
2. Talk to NPCs to learn about the threat
3. Form party (recruit Selan)
4. Enter first dungeon (Ancient Cave)
5. Solve basic puzzles
6. Face random encounters
7. Defeat first boss (Skeleton King)
8. Return to town for rewards
9. Unlock world map
10. Travel to next location

---

## Next Steps

- Add more towns and dungeons
- Create unique bosses for each dungeon
- Implement character progression (leveling, stat growth)
- Add equipment and inventory system
- Create story events and cutscenes
- Design endgame content

---

## Advanced Features

NeonWorks includes many advanced features to enhance your JRPG development workflow.

### AI-Powered Tools

#### AI Assistant (Ctrl+Space)

The AI Assistant can help with:
- **Code Generation** - Generate scripts, systems, components
- **Asset Creation** - Suggest asset names and organization
- **Balance Advice** - Recommend stat distributions
- **Bug Fixing** - Analyze and suggest fixes for issues
- **Documentation** - Generate documentation for your game

**Example Usage:**
1. Press **Ctrl+Space** to open AI Assistant
2. Ask: "Balance the stats for a level 10 boss"
3. AI suggests HP, Attack, Defense values
4. Apply suggestions to Database

#### AI Animator (Shift+F7)

Create animations without manual sprite work:
1. Open AI Animator
2. Upload character base sprite
3. Select animation type (walk, attack, cast, hurt, death)
4. AI generates frame-by-frame animation
5. Export as sprite sheet
6. Use in your game

#### AI Asset Tools

- **AI Asset Editor** - Edit sprites with AI assistance
- **AI Asset Inspector** - Analyze asset usage and optimization
- **AI Tileset Generator** - Generate tileset variations
- **AI Vision Context** - Understand sprite layouts visually

### Undo/Redo System (Ctrl+Z / Ctrl+Y)

NeonWorks features a **persistent undo/redo system** that:
- Saves across sessions (survives crashes!)
- Unlimited undo history
- Works in all editors
- Visual history viewer (Ctrl+H)

**History Viewer Features:**
- Browse full undo history
- Jump to any previous state
- Branch history (create alternate timelines)
- Search through changes
- Annotate important states

### Crash Recovery

If the editor crashes:
1. Restart NeonWorks
2. You'll see: "Recover from crash?"
3. Click "Yes" to restore your work
4. All unsaved changes are restored!

Auto-saves occur:
- Every 5 minutes (configurable)
- Before running tests
- Before major operations
- When switching maps

### Asset Management

#### Asset Browser (F7)

Organize all project assets:
- **Smart Folders** - Auto-categorize by type
- **Tags** - Tag assets for quick finding
- **Search** - Full-text search across assets
- **Preview** - Preview images, sounds, maps
- **Bulk Operations** - Rename, move, delete multiple assets
- **Import Wizard** - Import external assets with metadata
- **Asset Pipeline** - Automatic processing (resize, optimize)

#### Asset Library

Access built-in asset library:
- 1000+ free sprites
- 500+ sound effects
- 100+ music tracks
- 50+ tilesets
- Pre-made character templates
- Enemy sprites
- UI elements

### Quest Editor (F6)

Create complex quest systems:

**Quest Types:**
- **Main Quests** - Story progression
- **Side Quests** - Optional content
- **Repeatable Quests** - Daily/weekly quests
- **Collection Quests** - Gather items
- **Defeat Quests** - Kill X enemies
- **Escort Quests** - Protect NPCs
- **Delivery Quests** - Transport items

**Quest Features:**
- Visual quest graph editor
- Multiple objectives per quest
- Branching outcomes
- Quest chains
- Prerequisites and dependencies
- Reward configuration
- Journal integration
- Quest markers on map

### Debugging Tools

#### Debug Console (F1)

Powerful debugging features:
- **Command Line** - Execute Python commands live
- **Variable Inspector** - Inspect game state
- **Entity Browser** - Browse all entities
- **Component Viewer** - View component values
- **Event Log** - See all events in real-time
- **Performance Monitor** - FPS, memory, CPU usage
- **Profiler** - Find performance bottlenecks

**Useful Commands:**
```python
# Teleport player
player.position = (100, 100)

# Give items
inventory.add("potion", 99)

# Change stats
player.hp = 9999

# Start battle
start_battle(["slime", "goblin"])

# Toggle god mode
god_mode = True
```

#### Combat UI (F9)

Test battles in isolation:
- Select party composition
- Choose enemies
- Configure battle settings
- Run battle simulation
- View detailed combat log
- Analyze damage calculations
- Test AI behavior

### Workspace System

Save custom layouts for different tasks:

**Pre-configured Workspaces:**
1. **Map Design** - Map editor + tileset + layers
2. **Event Scripting** - Event editor + database + quest editor
3. **Combat Balancing** - Database + combat UI + debug console
4. **Asset Management** - Asset browser + asset editor
5. **Full Production** - All panels visible

**Custom Workspaces:**
1. Arrange panels as you like
2. Click **"Save Workspace"**
3. Name it (e.g., "Boss Design")
4. Quick-switch with toolbar dropdown

### Testing & Playtesting

#### Playtest Mode

Test your game without leaving the editor:
1. Click **"Playtest"** in toolbar
2. Game launches in window alongside editor
3. Make changes in editor
4. Click **"Reload"** to see changes instantly
5. No need to restart!

#### Automated Testing

Run automated tests:
- **Unit Tests** - Test individual systems
- **Integration Tests** - Test system interactions
- **Balance Tests** - Verify stat distributions
- **Content Tests** - Ensure all maps/events work

### Localization (Future Feature)

Prepare for multiple languages:
- String table editor
- Export/import translation files
- Test different languages in-editor
- Font support for various scripts

### Export & Distribution

#### Export Project (Ctrl+Shift+E)

Export your game as:
- **Standalone Executable** (Windows/Linux/Mac)
- **Encrypted Package** - Protect assets
- **Steam-ready Build** - With achievements, cloud saves
- **Web Build** - Play in browser
- **Mobile Build** - Android/iOS (future)

#### Package Builder

Configure your build:
- Icon and splash screen
- Version information
- Required DLLs
- Data compression
- Encryption strength
- License validation

#### Installer Builder

Create installers:
- Windows MSI installer
- Linux .deb package
- Mac .dmg
- Auto-updater integration
- Custom EULA
- Registry settings

### Performance Optimization

#### Built-in Profiler

Identify bottlenecks:
- System performance breakdown
- Render time analysis
- Memory usage tracking
- Entity count monitoring
- Asset loading times

**Optimization Tips:**
- Use object pooling for particles
- Enable layer caching
- Optimize tileset sizes
- Batch sprite rendering
- Use compressed audio

### Community Features

#### Share Your Project

Export project for sharing:
- Export as template
- Share on NeonWorks community
- Include custom systems
- Publish to asset store

#### Import Community Content

Browse community contributions:
- Character packs
- Enemy templates
- Map templates
- System extensions
- Custom editors

---

## Tips for Lufia-Style Games

### Capturing the Lufia Feel

1. **Exploration** - Make exploration rewarding with hidden chests and secrets
2. **Puzzles** - Every dungeon should have unique puzzle mechanics
3. **Boss Variety** - Each boss needs unique attack patterns
4. **Character Growth** - Meaningful stat progression and skill learning
5. **Story Pacing** - Balance combat, exploration, and story beats

### Recommended Settings

```json
{
  "encounter_rate": 25.0,
  "battle_difficulty": "moderate",
  "save_points": "towns_and_dungeons",
  "exp_curve": "moderate",
  "gold_multiplier": 1.0,
  "item_drop_rate": 20.0
}
```

### Battle Balance

**Early Game (Levels 1-10):**
- Encounters: 2-3 enemies
- Boss HP: 200-500
- Damage: 5-15 per hit

**Mid Game (Levels 10-20):**
- Encounters: 3-4 enemies
- Boss HP: 1000-2000
- Damage: 20-40 per hit

**Late Game (Levels 20-30):**
- Encounters: 4-5 enemies
- Boss HP: 3000-5000
- Damage: 50-100 per hit

**Final Boss:**
- HP: 8000-10000
- Multiple forms
- Unique mechanics
- All elements required

### Dungeon Design

1. **Length**: 15-30 minutes per dungeon
2. **Puzzles**: 2-3 unique puzzles per dungeon
3. **Treasures**: 5-10 chests per dungeon
4. **Boss**: One boss at the end
5. **Save Point**: Before boss room

---

## Keyboard Shortcuts Reference

### Essential Shortcuts

| Shortcut | Action |
|----------|--------|
| **Ctrl+S** | Save project |
| **Ctrl+Shift+S** | Save all |
| **Ctrl+Z** | Undo |
| **Ctrl+Y** | Redo |
| **Ctrl+C** | Copy |
| **Ctrl+V** | Paste |
| **Ctrl+X** | Cut |
| **Delete** | Delete selection |
| **Space** | Play/Pause |
| **F5** | Run game |
| **Shift+F5** | Stop game |

### View All Shortcuts

Press **Ctrl+Shift+K** to open the Shortcuts Overlay showing all available keyboard shortcuts.

---

## Next Steps

Now that you understand all the tools available, you can:

1. **Create your first town** using the Map Editor
2. **Populate the database** with characters, enemies, items
3. **Add NPCs and dialogue** with the Event Editor
4. **Build your first dungeon** with puzzles and encounters
5. **Design a boss battle** using the boss AI system
6. **Create a world map** connecting all locations
7. **Add quests** using the Quest Editor
8. **Balance the game** using the Combat UI
9. **Test thoroughly** with the Debug Console
10. **Export your game** and share it!

---

## Additional Resources

- **[JRPG_FEATURES.md](../JRPG_FEATURES.md)** - Complete JRPG system reference
- **[DEVELOPER_GUIDE.md](project/DEVELOPER_GUIDE.md)** - Development best practices
- **[docs/map_editor_guide.md](map_editor_guide.md)** - Map editor tutorial
- **[docs/keyboard_shortcuts.md](keyboard_shortcuts.md)** - All keyboard shortcuts
- **[ui/WORKSPACE_SYSTEM.md](../ui/WORKSPACE_SYSTEM.md)** - Workspace guide
- **[LAUNCHER_README.md](../LAUNCHER_README.md)** - Launcher documentation
- **[engine/README.md](../engine/README.md)** - Engine subsystems guide

---

**Happy Game Making! May your Lufia clone be legendary!** 🎮✨
