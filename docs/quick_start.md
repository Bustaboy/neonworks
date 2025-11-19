# Quick Start: Your First RPG in 30 Minutes

**Version:** 1.0
**Last Updated:** 2025-11-15
**Difficulty:** Beginner
**Time Required:** 30 minutes

Welcome to the NeonWorks Quick Start guide! In just 30 minutes, you'll create a playable RPG with a hero, a town, NPCs, and your first quest.

---

## Table of Contents

1. [What We're Building](#what-were-building)
2. [Prerequisites](#prerequisites)
3. [Step 1: Create Your Project (3 minutes)](#step-1-create-your-project-3-minutes)
4. [Step 2: Set Up the Database (5 minutes)](#step-2-set-up-the-database-5-minutes)
5. [Step 3: Build Your First Map (10 minutes)](#step-3-build-your-first-map-10-minutes)
6. [Step 4: Add NPCs and Events (7 minutes)](#step-4-add-npcs-and-events-7-minutes)
7. [Step 5: Create a Simple Quest (5 minutes)](#step-5-create-a-simple-quest-5-minutes)
8. [Step 6: Test Your Game!](#step-6-test-your-game)
9. [Next Steps](#next-steps)
10. [Troubleshooting](#troubleshooting)

---

## What We're Building

By the end of this tutorial, you'll have created:

✅ **A small town map** with buildings and decorations
✅ **A player character** that can walk around
✅ **3 NPCs** with unique dialogues
✅ **1 treasure chest** with an item reward
✅ **A simple quest** - "Find the Lost Cat"
✅ **A playable demo** you can show to friends!

**Screenshot Placeholder: Final result showing town map with player, NPCs, and UI**
*[Screenshot should show: Overhead view of small town, player character in center, 2-3 NPCs visible, UI showing quest tracker]*

---

## Prerequisites

Before starting, make sure you have:

- ✅ NeonWorks installed ([Installation Guide](user_manual.md#installation--setup))
- ✅ Python 3.8+ running
- ✅ Basic understanding of file navigation
- ✅ 30 minutes of uninterrupted time

**Optional but helpful:**
- Downloaded free RPG assets from [Kenney.nl](https://kenney.nl) or [OpenGameArt.org](https://opengameart.org)
- Your favorite beverage ☕

---

## Step 1: Create Your Project (3 minutes)

### 1.1: Launch the Visual Launcher (primary path)

Open your terminal/command prompt and launch the UI:

```bash
cd /path/to/neonworks
python -m neonworks.launcher
# or use:
# ./launch_neonworks.sh  (macOS/Linux)
# launch_neonworks.bat   (Windows)
```

The NeonWorks launcher opens with a visual project list and template browser.

### 1.2: Create New Project from the UI

1. Click **"Create New Project"**
2. Fill in the details:
   - **Project Name:** `my_first_rpg`
   - **Display Name:** "My First RPG"
   - **Author:** Your name
   - **Description:** "A simple RPG demo"
   - **Template:** Choose **"Turn-Based RPG"** (or your preferred starter template)

3. Configure window settings:
   - **Width:** 1280
   - **Height:** 720
   - **Tile Size:** 32
   - **Target FPS:** 60

4. Click **"Create"**

NeonWorks creates your project folder structure and adds it to the launcher list.

### 1.3: Open in Editor

1. Select your project in the launcher list
2. Click **"Open in Editor"** (or double-click the project card)
3. The Level Builder opens automatically

**✅ Checkpoint:** You should see a blank grid with toolbar and properties panel.

**Time check:** 3 minutes ⏱️

### Alternative: create and open via CLI (advanced)

Prefer scripting? You can mirror the same setup from the command line:

```bash
# From repo root
python cli.py create my_first_rpg --template turn_based_rpg
python main.py my_first_rpg --editor  # opens editor mode directly
```

---

## Step 2: Set Up the Database (5 minutes)

The database defines your game's content: characters, items, enemies, and skills.

### 2.1: Open Database Editor

Press `Ctrl+D` or click **Tools → Database Editor**.

**Screenshot: Database Editor with tabs**
*[Screenshot should show: Database Editor window with tabs: Characters, Items, Enemies, Skills, Classes]*

### 2.2: Create the Player Character

1. Click the **Characters** tab
2. Click **"New Character"**
3. Fill in the details:

```
Name: Alex
Class: Hero
Level: 1

Stats:
HP: 100
MP: 20
Attack: 12
Defense: 8
Magic Attack: 6
Magic Defense: 6
Speed: 10

Equipment:
Weapon: (none - we'll add later)
Armor: Cloth Shirt
Accessory: (none)
```

4. **Sprite Settings:**
   - If you have a character sprite: Click **"Select Sprite"** → choose your image
   - If not: Leave default (we'll use a colored square for now)

5. Click **"Save Character"**

### 2.3: Create a Simple Item

1. Click the **Items** tab
2. Click **"New Item"**
3. Create a healing potion:

```
ID: potion_basic
Name: Healing Potion
Type: Consumable
Description: "Restores 50 HP"

Effect:
Effect Type: Recover HP
Value: 50
Target: Single Ally

Price: 50 gold
```

4. Click **"Save Item"**

### 2.4: Create the Quest Item (Lost Cat)

We'll create a key item for our quest:

1. Still in **Items** tab, click **"New Item"**
2. Create the cat item:

```
ID: lost_cat
Name: Fluffy the Cat
Type: Key Item
Description: "Mrs. Henderson's beloved cat"

Effect: None
Price: (Not for sale)
```

3. Click **"Save Item"**

**✅ Checkpoint:** You should have 1 character (Alex) and 2 items (Potion, Lost Cat) in your database.

**Time check:** 8 minutes total ⏱️

---

## Step 3: Build Your First Map (10 minutes)

Time to create your town!

### 3.1: Create a New Map

1. Press `F4` to open Level Builder (if not already open)
2. Click **File → New Map** or press `Ctrl+N`
3. Configure the map:

```
Map Name: hometown
Display Name: "Peaceful Village"
Width: 20 tiles
Height: 15 tiles
```

4. Click **"Create"**

You now have a blank 20×15 grid!

**Screenshot: Empty map grid in Level Builder**
*[Screenshot should show: 20×15 tile grid with grid lines visible, layer panel on right]*

### 3.2: Import or Select a Tileset

**If you have a tileset:**

1. Press `F7` to open Asset Browser
2. Click **"Import Assets"**
3. Select your tileset image (PNG format, 32×32 tiles)
4. Import as **"Tileset"**

**If you don't have assets:**

Don't worry! We'll use basic colored squares:

1. In Level Builder, click **"Use Basic Tileset"**
2. This creates simple colored tiles for testing

### 3.3: Paint the Ground Layer

Let's create grass terrain:

1. **Select the Ground layer** (in Layers panel on right)

2. **Choose the grass tile** from the tile palette (green tile)

3. **Select the Fill tool** (paint bucket icon)

4. **Click anywhere on the map** to fill with grass

**Screenshot: Map filled with grass tiles**
*[Screenshot should show: Grid completely filled with green grass tiles]*

Your map now has a grass floor!

### 3.4: Add Paths

Let's add some dirt paths:

1. **Choose the dirt/path tile** (brown tile)

2. **Select the Pencil tool** (pencil icon)

3. **Draw paths** like this:

```
Draw a horizontal path across the middle (row 7)
Draw a vertical path down the center (column 10)
They should intersect in the middle
```

**Screenshot: Map with cross-shaped path**
*[Screenshot should show: Grass map with brown dirt paths forming a cross or T-shape]*

### 3.5: Add Buildings

Now let's add some structures:

1. **Select the Objects layer**

2. **Choose wall/building tiles** from palette

3. **Use Rectangle tool** to draw 2-3 buildings:

```
Building 1 (House):
Position: (3, 3)
Size: 4×4 tiles

Building 2 (Shop):
Position: (14, 3)
Size: 4×3 tiles

Building 3 (Mayor's House):
Position: (8, 10)
Size: 5×4 tiles
```

**Screenshot: Map with buildings added**
*[Screenshot should show: Grass + paths + 3 simple rectangular buildings]*

### 3.6: Add Decorations

Make it feel alive with details:

1. **Select the Ground Detail layer**

2. Add decorations:
   - Flowers near buildings
   - Rocks along paths
   - Trees at map edges (top and bottom)

Don't overthink it - just make it look interesting!

### 3.7: Set Player Start Position

1. Click the **"Set Start Position"** button (flag icon)
2. Click on the map where the player should spawn
   - Good spot: Center of the map, on the path intersection

A flag marker appears showing the spawn point!

### 3.8: Save Your Map

Press `Ctrl+S` to save.

**✅ Checkpoint:** You should have a map with grass, paths, 3 buildings, and a player start position.

**Time check:** 18 minutes total ⏱️

---

## Step 4: Add NPCs and Events (7 minutes)

Let's bring the town to life with NPCs!

### 4.1: Create Your First NPC

1. **Click the "Place NPC" button** (person icon in toolbar)

2. **Click on the map** near Building 1 to place NPC

3. **Configure NPC in Properties panel:**

```
Name: Old Man
Sprite: (Use default or select custom)

Movement:
Type: Static (doesn't move)

Direction: Down (facing down)
```

4. **Add dialogue:**

Click **"Edit Event"** button in Properties panel.

The Event Editor opens!

**Screenshot: Event Editor showing dialogue event**
*[Screenshot should show: Event node editor with "Show Dialogue" node]*

5. **Create dialogue event:**

In the Event Editor:

1. Click **"Add Node"** → **"Show Dialogue"**
2. Fill in:

```
Speaker: Old Man
Text: "Welcome to Peaceful Village, traveler!
      Have you seen Mrs. Henderson's cat?
      She's been looking everywhere for it."
```

3. Click **"Save Event"**

Your first NPC is complete!

### 4.2: Create the Quest Giver (Mrs. Henderson)

1. **Place another NPC** near Building 2

2. **Configure:**

```
Name: Mrs. Henderson
Movement: Random Walk (wanders around)
Speed: Slow
```

3. **Add dialogue event:**

```
Speaker: Mrs. Henderson
Text: "Oh, thank goodness you're here!
      My cat Fluffy has run off somewhere.
      Could you help me find her?

      I think she's hiding near the old well
      at the edge of town."

Event Commands:
→ Start Quest: "Find the Lost Cat"
```

**How to add quest start:**

In Event Editor:

1. Add node: **"Show Dialogue"** (as above)
2. Add node: **"Start Quest"**
3. Select quest: "Find the Lost Cat" (we'll create this soon!)
4. Connect nodes: Dialogue → Start Quest
5. Save Event

### 4.3: Create a Merchant NPC

1. **Place NPC** in front of the Shop building

2. **Configure:**

```
Name: Shop Owner
Movement: Static
Direction: Down
```

3. **Add event:**

```
Event Type: Open Shop

Shop Inventory:
- Healing Potion (50g)
- Antidote (30g)
- Magic Water (100g)
```

**Screenshot: Shop event configuration**
*[Screenshot should show: Shop inventory editor with items and prices]*

### 4.4: Place a Treasure Chest

This is where the player finds the cat!

1. **Click "Place Object"** → **"Treasure Chest"**

2. **Place chest** at the edge of town (near bottom-left corner)

3. **Configure chest:**

```
Contents:
Item: Lost Cat (the key item we created)
Message: "You found Fluffy hiding in the bushes!"

One-time: Yes (can only open once)
```

**✅ Checkpoint:** You should have 3 NPCs and 1 treasure chest on your map.

**Time check:** 25 minutes total ⏱️

---

## Step 5: Create a Simple Quest (5 minutes)

Let's create the "Find the Lost Cat" quest!

### 5.1: Open Quest Editor

Press `F6` or click **Tools → Quest Editor**.

**Screenshot: Quest Editor interface**
*[Screenshot should show: Quest list on left, quest details on right, stages panel]*

### 5.2: Create the Quest

1. Click **"New Quest"**

2. Fill in quest details:

```
Quest ID: find_lost_cat
Name: "Find the Lost Cat"
Description: "Mrs. Henderson's cat Fluffy is missing.
             Find her and bring her back safely."

Type: Main Quest
Recommended Level: 1
```

### 5.3: Add Quest Stages

Quests have multiple stages. Let's add them:

**Stage 1: Talk to Mrs. Henderson**

```
Stage ID: talk_to_mrs_henderson
Description: "Speak with Mrs. Henderson"
Objective: "Find Mrs. Henderson in the village"

Completion Condition:
Type: Event Triggered
Event: mrs_henderson_dialogue_complete
```

**Stage 2: Find the Cat**

```
Stage ID: find_fluffy
Description: "Search for Fluffy"
Objective: "Look for Fluffy near the edge of town"

Completion Condition:
Type: Item Obtained
Item: lost_cat
```

**Stage 3: Return to Mrs. Henderson**

```
Stage ID: return_to_mrs_henderson
Description: "Return Fluffy to Mrs. Henderson"
Objective: "Bring Fluffy back to Mrs. Henderson"

Completion Condition:
Type: Talk to NPC
NPC: Mrs. Henderson
Required Item: lost_cat
```

### 5.4: Set Quest Rewards

```
Rewards (on quest completion):
Gold: 100
Experience: 50
Item: Healing Potion ×3
```

### 5.5: Save the Quest

Click **"Save Quest"** (`Ctrl+S`)

**✅ Checkpoint:** You've created a complete quest with 3 stages and rewards!

**Time check:** 30 minutes total ⏱️

---

## Step 6: Test Your Game!

### 6.1: Enter Play Mode

1. Click the **"Play"** button (▶️ icon) in toolbar
   - Or press `F10`

2. The game starts!

**What you should see:**

- Your character (Alex) appears at the spawn point
- The camera centers on the player
- UI shows HP/MP bars
- The town map is visible

**Screenshot: Game in play mode**
*[Screenshot should show: Game running, player character visible, UI elements present, town map rendered]*

### 6.2: Test Movement

Use **WASD** or **Arrow Keys** to move around.

- Walk around the map
- Check collision (can you walk through buildings? You shouldn't!)
- Explore the paths

### 6.3: Test NPCs

1. **Walk up to the Old Man**
2. Press `E` to interact
3. His dialogue should appear!

Do the same for other NPCs.

### 6.4: Test the Shop

1. Walk to the Shop Owner
2. Press `E` to interact
3. The shop menu should open
4. Try buying a potion (you start with some gold)

### 6.5: Test the Quest

**Complete the quest:**

1. Talk to **Mrs. Henderson** → Quest starts!
2. Check quest log (press `Q`) → "Find the Lost Cat" should be active
3. Walk to the **treasure chest** at map edge
4. Press `E` to open → Get "Lost Cat" item!
5. Return to **Mrs. Henderson**
6. Talk to her → Quest completes! You get rewards!

### 6.6: Check the Results

After completing the quest:

- Press `I` to open inventory → You should have 3 potions
- Check your gold → Should have +100
- Check experience → Should show +50 XP

**🎉 Congratulations! You've completed your first RPG!**

---

## Next Steps

You've built a functional RPG in 30 minutes! Here's what to do next:

### Immediate Next Steps

1. **Add more content:**
   - Create more NPCs with different dialogues
   - Add more quests
   - Build additional maps (forest, cave, castle)

2. **Improve your map:**
   - Add more decorations
   - Create interiors for buildings
   - Add map transitions (doors that lead inside)

3. **Add combat:**
   - Create enemies in the Database
   - Add encounter zones to your map
   - Design enemy groups and battles

### Learning Path

**Next tutorials to follow:**

1. **[Event Editor Guide](event_editor_guide.md)** - Master complex events and cutscenes
2. **[Map Editor Guide](map_editor_guide.md)** - Advanced mapping techniques
3. **[Database Guide](database_guide.md)** - Deep dive into game data
4. **[JRPG Systems](JRPG_SYSTEMS.md)** - Complete battle system tutorial

### Expanding Your Game

**Ideas for improvement:**

- **Multiple towns** - Create a world map with several locations
- **Dungeons** - Design multi-floor dungeons with puzzles
- **Boss battles** - Create challenging unique enemies
- **Party members** - Add companions who join the player
- **Equipment system** - Let players find and equip better gear
- **Magic skills** - Create spells and special abilities
- **Side quests** - Optional content for extra rewards

### Polish and Presentation

- **Custom sprites** - Replace placeholder graphics
- **Music and sound** - Add background music and sound effects
- **Polish UI** - Customize the interface appearance
- **Write story** - Flesh out the narrative and world
- **Playtest** - Have friends test and give feedback

---

## Troubleshooting

### Common Issues

**Problem: Can't see the player character**

**Solution:**
- Check player start position is set (flag icon should be visible)
- Verify character sprite is assigned in Database
- Make sure camera is following player

**Problem: Can't interact with NPCs**

**Solution:**
- Walk right up to the NPC (must be adjacent)
- Press `E` key (default interact key)
- Check NPC has an event assigned
- Verify NPC is on correct layer

**Problem: Map looks weird/tiles don't align**

**Solution:**
- Check tileset is 32×32 pixels per tile
- Verify map tile size matches tileset
- Try using "Basic Tileset" for testing

**Problem: Quest doesn't start**

**Solution:**
- Check Mrs. Henderson's dialogue has "Start Quest" event command
- Verify quest ID matches exactly
- Look in Debug Console (`F1`) for error messages

**Problem: Treasure chest is empty**

**Solution:**
- Open chest configuration (click chest, check Properties)
- Verify "Lost Cat" item is assigned
- Check item exists in Database

**Problem: Game is laggy/slow**

**Solution:**
- Reduce map size
- Lower target FPS in project settings
- Disable particle effects (Settings → Graphics)
- Close other programs running in background

### Getting Help

Still stuck? Try these:

1. **Debug Console (`F1`)** - Check for error messages
2. **User Manual** - Search [user_manual.md](user_manual.md)
3. **Example Projects** - Study `examples/simple_rpg/`
4. **Community** - Ask on Discord or forums

---

## Summary

### What You've Learned

In just 30 minutes, you:

✅ Created a new NeonWorks project
✅ Set up the database with characters and items
✅ Built a town map with buildings and decorations
✅ Added NPCs with dialogue
✅ Created a shop for buying items
✅ Designed a complete quest with multiple stages
✅ Tested your game and completed the quest

### Skills Acquired

- **Project creation** - Starting new games
- **Database management** - Creating characters and items
- **Map design** - Building levels with tilesets
- **Event system** - NPC dialogue and interactions
- **Quest design** - Multi-stage quest creation
- **Testing** - Playing and debugging your game

### Your Achievement

You've gone from zero to a playable RPG demo! This is a huge accomplishment. Most aspiring game developers never finish even a small project like this.

**What to do now:**

1. **Save your project** (`Ctrl+S` everywhere!)
2. **Take a screenshot** - Share your creation!
3. **Back up your files** - Copy project folder to safe location
4. **Take a break** - You've earned it!

When you're ready, continue with the advanced tutorials to expand your game into something even more amazing.

---

## Quick Reference Card

**Print this for easy reference!**

### Essential Shortcuts

```
F4  - Level Builder (map editor)
F5  - Event Editor
F6  - Quest Editor
F7  - Asset Browser
F8  - Project Manager
F10 - Play Game

Ctrl+S - Save
Ctrl+Z - Undo
Ctrl+Y - Redo

W/A/S/D - Move character
E - Interact
I - Inventory
Q - Quest Log
Escape - Menu/Cancel
```

### In-Game Controls

```
Movement: W, A, S, D or Arrow Keys
Interact: E
Inventory: I
Quest Log: Q
Menu: Escape
Debug Console: F1
```

### Map Editor Tools

```
Pencil - Draw single tiles
Brush - Paint with preview
Fill - Flood fill area
Rectangle - Draw rectangles
Eraser - Remove tiles
Eyedropper - Pick tile from map
```

---

## Congratulations! 🎉

You've completed the NeonWorks Quick Start tutorial!

You're now ready to create amazing RPGs. The only limit is your imagination!

**Share your creation:**
- Post screenshots on social media
- Share your project in the NeonWorks community
- Show friends and family what you made!

**Keep learning:**
- Try the other tutorials
- Experiment with features we didn't cover
- Study the example projects
- Join the community and learn from others

Happy game development! 🎮✨

---

**Version History:**

- **1.0** (2025-11-15) - Initial Quick Start guide

**Feedback:**

Found this helpful? Have suggestions? Let us know!

---

**NeonWorks Team**
Making game development accessible to everyone.
