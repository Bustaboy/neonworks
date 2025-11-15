# Base Builder Demo - Complete Sample Project

**Version:** 1.0.0
**Engine:** NeonWorks 0.1.0
**Type:** Base-Building Game with Resource Management and Combat
**Status:** Complete & Playable

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Features Demonstrated](#features-demonstrated)
3. [Getting Started](#getting-started)
4. [Game Content](#game-content)
5. [Maps & Locations](#maps--locations)
6. [Database Entries](#database-entries)
7. [Characters & Classes](#characters--classes)
8. [Events & Tutorials](#events--tutorials)
9. [Customization Guide](#customization-guide)
10. [Technical Details](#technical-details)

---

## 📖 Overview

The **Base Builder Demo** is a complete, immediately playable sample project that showcases all major features of the NeonWorks engine. It demonstrates:

- ✅ Complete database system (items, skills, weapons, armors, enemies, classes, actors)
- ✅ Event system with branching dialogues and conditional logic
- ✅ Multiple interconnected maps with spawn points and transitions
- ✅ Tutorial system integrated into gameplay
- ✅ Resource gathering and crafting mechanics
- ✅ Character recruitment system
- ✅ Combat encounters (random and boss battles)
- ✅ Quest progression with rewards
- ✅ Background music and sound effects
- ✅ Custom characters with unique abilities

This project serves as both a playable game and a learning resource for developers using NeonWorks.

---

## 🎮 Features Demonstrated

### Core Engine Features

| Feature | Implementation | File Reference |
|---------|---------------|----------------|
| **Database System** | 10 items, 5 skills, 5 weapons, 5 armors, 5 enemies, 4 classes, 4 actors | `data/database.json` |
| **Event Commands** | 50+ event commands across all maps | `assets/maps/*.json` |
| **Map System** | 5 interconnected maps with varied terrain | `assets/maps/*.json` |
| **Character System** | 4 recruitable characters with unique classes | `data/database.json:actors` |
| **Combat System** | Random encounters and boss battle | `assets/maps/ruins.json` |
| **Resource System** | Gathering, crafting, and inventory management | Event: `open_crafting` |
| **Audio System** | 7 music tracks, 7 sound effects | `assets/music/`, `assets/sfx/` |
| **Progression System** | Switches, variables, self-switches for state tracking | All event files |

### Gameplay Features

- **Resource Gathering**: Wood, Stone, Food, Iron Ore
- **Crafting System**: Iron Bars, Tools
- **Character Recruitment**: 4 unique NPCs to recruit
- **Exploration**: 5 distinct areas to discover
- **Boss Battle**: Ancient Guardian with special rewards
- **Territory Expansion**: Claim new lands for building
- **Shop System**: Buy and sell resources
- **Storage System**: Manage inventory and resources

---

## 🚀 Getting Started

### Installation

1. **Ensure NeonWorks is installed**:
   ```bash
   cd /path/to/neonworks
   pip install -r requirements.txt
   ```

2. **Copy this template** (if creating a new project):
   ```bash
   cp -r templates/base_builder my_game
   cd my_game
   ```

3. **Run the game**:
   ```bash
   python main.py base_builder
   ```

   Or if you copied it:
   ```bash
   python main.py my_game
   ```

### First Steps in the Game

1. **Talk to the Tutorial Guide** (center of Home Base)
   - Learn basic controls and game objectives
   - Get overview of features

2. **Recruit NPCs**:
   - **Marcus** (Builder) - Unlocks Quick Build skill
   - **Sarah** (Guard) - Provides base defense
   - **Jake** (Scout) - Reveals the Ancient Ruins
   - **Merchant** - Buy/sell resources

3. **Gather Resources**:
   - **Forest** (northwest exit) - Wood, Food
   - **Mountains** (northeast exit) - Stone, Iron Ore

4. **Craft Items**:
   - Use the Crafting Bench in Home Base
   - Smelt Iron Ore → Iron Bars
   - Craft Iron Bars → Tools

5. **Explore the Ruins**:
   - Recruit Jake to unlock access
   - Defeat the Ancient Guardian boss
   - Claim the Ancient Relic reward

---

## 🗺️ Maps & Locations

### 1. Home Base (`home_base.json`)

**Size:** 30x20 tiles | **Music:** peaceful_town.mp3

**Key Features:**
- Tutorial Guide NPC (teaches game basics)
- 4 Recruitable NPCs (Marcus, Sarah, Jake, Merchant)
- Storage Chest, Crafting Bench, Campfire, Town Sign
- Exits to Forest, Mountains, and Ruins

**NPCs:**
- **Tutorial Guide** @ (15, 15) - Static, provides tutorials
- **Marcus** @ (10, 10) - Static, recruitable builder
- **Sarah** @ (20, 10) - Patrol behavior, recruitable guard
- **Jake** @ (5, 5) - Wander behavior, recruitable scout
- **Resource Merchant** @ (12, 8) - Static, shop access

### 2. Forest (`forest.json`)

**Size:** 25x25 tiles | **Music:** forest_ambience.mp3

**Resources:**
- 2 Wood Piles (5x Wood each)
- 1 Berry Bush (3x Food)
- 1 Hidden Chest (3x Health Potion, 100 Gold)

**Encounters:** Wild Boar (50%), Goblin Raider (30%)

### 3. Mountains (`mountains.json`)

**Size:** 25x25 tiles | **Music:** mountain_wind.mp3

**Resources:**
- 2 Stone Deposits (4x Stone each)
- 2 Iron Veins (3x Iron Ore each)

**Encounters:** Rock Golem (60%), Bandit Scout (40%)

### 4. Ancient Ruins (`ruins.json`)

**Size:** 20x20 tiles | **Music:** ruins_mystery.mp3

**Features:**
- Boss Battle: Ancient Guardian
- Final Treasure: Ancient Relic
- Unlock Condition: Recruit Jake

### 5. Open Plains (`plains.json`)

**Size:** 30x30 tiles | **Music:** grasslands.mp3

**Features:**
- Territory expansion system
- Light random encounters

---

## 💾 Database Entries

### Items (10 Total)

| ID | Name | Type | Price | Effect |
|----|------|------|-------|--------|
| 1 | Wood | Key | 5g | Building material |
| 2 | Stone | Key | 10g | Building material |
| 3 | Food | Consumable | 3g | Restore 20 HP |
| 4 | Iron Ore | Key | 15g | Smelting material |
| 5 | Iron Bar | Key | 30g | Advanced crafting |
| 6 | Tools | Key | 100g | Boost efficiency |
| 101 | Health Potion | Consumable | 50g | Restore 50 HP |
| 102 | Energy Drink | Consumable | 80g | Restore 30 MP |
| 103 | Antidote | Consumable | 40g | Cure poison |
| 201 | Ancient Relic | Key | N/A | Quest item |

### Skills (5 Total)

| ID | Name | MP | Effect |
|----|------|-----|--------|
| 1 | Quick Build | 10 | Speed up construction 50% |
| 2 | Gather Resources | 15 | Double gathering for 30s |
| 3 | Defend Base | 20 | Increase building defense |
| 4 | Repair | 12 | Restore 100 HP |
| 5 | Scout Area | 8 | Reveal fog of war |

### Enemies (5 Total)

| ID | Name | HP | ATK | Location |
|----|------|----|----|----------|
| 1 | Wild Boar | 60 | 20 | Forest, Plains |
| 2 | Bandit Scout | 80 | 25 | Mountains, Plains |
| 3 | Rock Golem | 150 | 30 | Mountains |
| 4 | Goblin Raider | 70 | 18 | Forest |
| 5 | Ancient Guardian | 300 | 45 | Ruins (Boss) |

### Classes (4 Total)

| ID | Name | Specialty | Key Skills |
|----|------|-----------|------------|
| 1 | Worker | All-around | Gather, Repair, Quick Build |
| 2 | Builder | Construction | Quick Build, Repair, Defend |
| 3 | Guard | Combat | Defend Base, Repair |
| 4 | Scout | Exploration | Scout Area, Gather |

---

## 🎯 Events & Tutorials

All events include tutorial comments explaining their purpose:

### Tutorial System

**Event:** `tutorial_start`
- Basic controls (Arrow keys, Z/Enter, X/Esc)
- F-key editors (F4-F8)
- Game objectives

### Character Recruitment

- **Marcus** (Builder): Always available, adds Quick Build skill
- **Sarah** (Guard): Patrols base, enhances defense
- **Jake** (Scout): Unlocks Ancient Ruins access

### Crafting System

**Recipes:**
- Iron Bar: 2x Iron Ore → 1x Iron Bar
- Tools: 1x Iron Bar → 1x Tools

### Boss Battle

**Ancient Guardian:**
- Trigger: Step on (10, 10) in ruins
- Stats: 300 HP, 45 ATK
- Rewards: Ancient Relic, 1000 Gold, 5x Energy Drink

---

## 🎨 Customization Guide

### Adding New Items

Edit `data/database.json`:

```json
{
  "id": 300,
  "name": "My New Item",
  "icon_index": 10,
  "description": "A custom item",
  "note": "Tutorial: How to use this item",
  "item_type": "regular",
  "price": 100,
  "effects": []
}
```

### Creating Events

Basic event structure:

```json
{
  "id": "my_event",
  "trigger": "action_button",
  "name": "My Event",
  "note": "TUTORIAL: What this teaches",
  "pages": [
    {
      "commands": [
        {
          "code": "show_text",
          "parameters": {"text": "Hello!"}
        }
      ]
    }
  ]
}
```

### Adding NPCs

```json
{
  "id": "my_npc",
  "x": 15,
  "y": 10,
  "sprite": "characters/my_sprite.png",
  "behavior": "static",
  "event_id": "talk_to_npc"
}
```

---

## 🔧 Technical Details

### File Structure

```
base_builder/
├── project.json              # Project configuration
├── README.md                 # This file
├── data/
│   └── database.json         # All game data
├── assets/
│   ├── maps/                 # 5 map files
│   ├── tilesets/             # Terrain graphics
│   ├── characters/           # NPC sprites
│   ├── music/                # 7 BGM tracks
│   └── sfx/                  # 7 sound effects
└── scripts/
    └── (optional custom scripts)
```

### Game Switches

| Switch | Purpose |
|--------|---------|
| `tutorial_completed` | Tutorial finished |
| `ruins_unlocked` | Ruins accessible |
| `guardian_defeated` | Boss defeated |
| `plains_claimed` | Territory claimed |

### Starting Resources

- Wood: 100
- Stone: 50
- Food: 30
- Iron Ore: 10

---

## 🎓 Learning Objectives

This project teaches:

1. **Database Design** - Item categorization, skill creation, enemy balancing
2. **Event Scripting** - Conditional branches, switch management, crafting logic
3. **Map Design** - Multiple zones, spawn points, triggers, encounters
4. **Player Progression** - Tutorials, recruitment, resource→crafting→rewards
5. **Audio Integration** - Map music, event SFX, transitions

---

## 🚀 Next Steps

### Immediate Enhancements

1. Replace placeholder assets (tilesets, sprites, audio)
2. Expand content (more maps, NPCs, quests)
3. Add features (day/night, weather, building construction)

### Visual Editors

- **F4** - Level Builder: Edit maps visually
- **F5** - Navmesh Editor: Adjust pathfinding
- **F6** - Quest Editor: Create quest chains
- **F7** - Asset Browser: Manage assets

### Export & Share

```bash
python export_cli.py export base_builder
```

---

## 💡 Tips & Tricks

**For Players:**
- Recruit everyone before dangerous areas
- Gather resources early
- Save health potions for boss
- Explore thoroughly for hidden treasures

**For Developers:**
- Use event notes for documentation
- Test state management thoroughly
- Balance progression carefully
- Provide feedback for all actions

---

## 📚 Resources

- **Main README:** `/README.md`
- **Developer Guide:** `/DEVELOPER_GUIDE.md`
- **Engine Status:** `/STATUS.md`
- **CLAUDE.md:** `/CLAUDE.md`

---

## ✨ Credits

**Created by:** NeonWorks Team
**Engine:** NeonWorks 0.1.0
**License:** Same as NeonWorks

---

**Happy Building! 🏗️**

*Complete game in pure JSON - no coding required!*
