# Map Editor Guide - Advanced Mapping

**Version:** 1.0
**Last Updated:** 2025-11-15
**Difficulty:** Beginner to Advanced

Master the NeonWorks Level Builder and create immersive, professional game worlds!

---

## Table of Contents

1. [Introduction](#introduction)
2. [Level Builder Interface](#level-builder-interface)
3. [Map Creation Basics](#map-creation-basics)
4. [Layer System](#layer-system)
5. [Tileset Management](#tileset-management)
6. [Painting Techniques](#painting-techniques)
7. [Autotiling System](#autotiling-system)
8. [Object Placement](#object-placement)
9. [Collision and Pathfinding](#collision-and-pathfinding)
10. [Map Properties](#map-properties)
11. [Multi-Map Projects](#multi-map-projects)
12. [Advanced Techniques](#advanced-techniques)
13. [Optimization](#optimization)
14. [Troubleshooting](#troubleshooting)

---

## Introduction

### What is the Level Builder?

The **Level Builder** (also called Map Editor) is NeonWorks' primary tool for designing game levels, dungeons, towns, and world maps.

**Screenshot: Level Builder showing a complete town map**
*[Screenshot should show: Full interface with finished town map, multiple layers visible, tileset palette]*

### Key Features

✅ **Visual tile painting** - See changes in real-time
✅ **18-layer system** - Complex depth and parallax
✅ **Autotiling** - Walls and terrains connect automatically
✅ **Collision editing** - Visual collision layer editing
✅ **Object placement** - NPCs, events, spawn points
✅ **Navmesh generation** - AI-powered pathfinding setup
✅ **Multi-map management** - Manage entire game world
✅ **Tileset manager** - Import, organize, and configure tilesets
✅ **Undo/Redo** - Full history (1000 actions)

---

## Level Builder Interface

**Screenshot: Level Builder interface with all panels labeled**
*[Screenshot should show: Canvas (center), tileset palette (left), layers panel (right), toolbar (top), properties (bottom-right)]*

### Main Areas

**1. Canvas (Center)**
- Visual representation of your map
- **Pan:** Middle-mouse drag or Arrow Keys
- **Zoom:** Mouse wheel or `+`/`-` keys
- **Grid toggle:** `Ctrl+G`

**2. Tileset Palette (Left)**
- Available tiles from current tileset
- Click to select tile
- Right-click for tile properties
- Multi-select: Ctrl+Click or drag rectangle

**3. Layers Panel (Right)**
- All map layers listed
- Toggle visibility (eye icon)
- Lock layers (lock icon)
- Opacity slider per layer
- Drag to reorder

**4. Toolbar (Top)**
| Tool | Icon | Function | Shortcut |
|------|------|----------|----------|
| Select | ↖️ | Select objects/areas | `V` |
| Pencil | ✏️ | Draw single tiles | `B` |
| Brush | 🖌️ | Paint with preview | `P` |
| Fill | 🪣 | Flood fill | `G` |
| Rectangle | ⬜ | Draw filled rectangle | `R` |
| Eraser | 🧹 | Remove tiles | `E` |
| Eyedropper | 💧 | Pick tile from map | `I` |

**5. Properties Panel (Bottom-Right)**
- Map settings
- Selected object properties
- Brush configuration
- Layer settings

**6. Minimap (Bottom-Left)**
- Overview of entire map
- Click to navigate
- Shows viewport rectangle

---

## Map Creation Basics

### Creating a New Map

1. **Open Level Builder** (`F4`)
2. **Click File → New Map** (or `Ctrl+N`)
3. **Configure map settings:**

```
Map Name: town_peaceful
Display Name: "Peaceful Village"

Dimensions:
Width: 30 tiles
Height: 20 tiles

Tile Size: 32 pixels
(Can't be changed after creation!)

Default Tileset: town_exterior
```

4. **Click Create**

**Blank map appears** with grid!

**Screenshot: New blank map with grid visible**
*[Screenshot should show: Empty grid, layers panel showing default layers]*

### Map Size Guidelines

**Small Maps (10×10 to 20×15):**
- Single rooms
- Small dungeons
- Indoor areas
- Quick encounters

**Medium Maps (20×15 to 40×30):**
- Town areas
- Dungeon floors
- Forest clearings
- Battle arenas

**Large Maps (40×30 to 100×80):**
- Full towns
- Large dungeons
- Outdoor regions
- World map sections

**Very Large (100+ tiles):**
- Open world areas
- Be careful - can affect performance!

### Tile Size

**Common sizes:**
- **16×16** - Retro, classic RPG style
- **32×32** - Standard, recommended
- **48×48** - Detailed, larger characters
- **64×64** - HD, high detail

**Recommendation:** Use **32×32** for most projects.

---

## Layer System

### Understanding Layers

Layers stack **bottom to top** like sheets of paper. Each has a **Z-order** (depth).

**Screenshot: Layers panel showing all standard layers**
*[Screenshot should show: Layer list with names, visibility toggles, lock icons, opacity sliders]*

### Standard Layer Setup

**18-Layer System:**

```
Layer 18: Sky/Atmosphere (z=18)
Layer 17: Weather Effects (z=17)
Layer 16: Above Everything (z=16)
Layer 15: Ceiling/Roof (z=15)
Layer 14: Above Character High (z=14)
Layer 13: Above Character (z=13)
Layer 12: Character Layer (z=12) [Characters render here]
Layer 11: Object High (z=11)
Layer 10: Objects (z=10)
Layer 9: Object Base (z=9)
Layer 8: Walls High (z=8)
Layer 7: Walls (z=7)
Layer 6: Wall Base (z=6)
Layer 5: Ground Detail High (z=5)
Layer 4: Ground Detail (z=4)
Layer 3: Ground Detail Low (z=3)
Layer 2: Ground (z=2)
Layer 1: Ground Shadow (z=1)
Layer 0: Background (z=0)
```

### Layer Usage Guide

**Background (Layer 0):**
- Base color or pattern
- Rarely used (usually transparent)
- Example: Void color under bridges

**Ground Shadow (Layer 1):**
- Ambient occlusion
- Soft shadows under objects
- Example: Shadow beneath trees

**Ground (Layer 2):**
- Main terrain
- Grass, dirt, stone floors
- Most of your painting happens here

**Ground Detail (Layers 3-5):**
- Flowers, cracks, puddles
- Small decorative elements
- Path details, patterns

**Walls (Layers 6-8):**
- Wall tiles
- Cliffs, barriers
- Building exteriors
- Autotiling typically used

**Objects (Layers 9-11):**
- Furniture, decorations
- Trees, rocks, signs
- Interactive objects

**Character Layer (12):**
- **Special: This is where characters render**
- Don't paint tiles here!
- Anything above layer 12 appears in front of characters

**Above Character (13-14):**
- Tree tops, roof edges
- Bridges player walks under
- Archways

**Ceiling/Roof (15):**
- Indoor ceilings
- Overhead decorations

**Above Everything (16):**
- UI elements on map
- Special effects

**Weather (17):**
- Rain, snow overlays
- Fog effects

**Sky (18):**
- Sky gradient
- Parallax background

### Working with Layers

**Selecting a Layer:**
1. Click layer name in Layers panel
2. **Active layer** highlighted in blue

**Toggle Visibility:**
- Click eye icon (👁️) next to layer
- Hidden layers don't render but are still saved

**Lock Layer:**
- Click lock icon (🔒)
- Locked layers can't be edited
- Prevents accidental changes

**Adjust Opacity:**
- Drag opacity slider (0-100%)
- Useful for seeing layers beneath while editing

**Reorder Layers:**
- Drag layer name up/down
- Changes rendering order

---

## Tileset Management

### Importing a Tileset

1. **Press `F7`** to open Asset Browser
2. **Click "Import Assets"**
3. **Select tileset image** (PNG)
4. **Configure:**

```
Name: town_exterior
Type: Tileset
Tile Size: 32×32 (must match map tile size!)

Transparency:
Color: Magenta (#FF00FF) or Alpha channel

Margin: 0 pixels
Spacing: 0 pixels
(Adjust if tileset has borders or gaps)
```

5. **Click Import**

**Screenshot: Tileset import dialog**
*[Screenshot should show: Tileset preview, tile size settings, transparency options]*

### Tileset Properties

**Good tileset format:**
```
Image: town_tileset.png
Format: PNG with transparency
Size: 256×256 pixels (or larger)
Grid: 32×32 tiles (8 tiles × 8 tiles)
Layout: Organized by type (grass together, walls together)
```

**Tileset organization:**
```
Row 1: Grass variations
Row 2: Dirt/paths
Row 3: Water/sand
Row 4: Walls (top)
Row 5: Walls (middle)
Row 6: Walls (bottom)
Row 7: Objects (trees, rocks)
Row 8: Buildings/structures
```

### Tileset Manager

**Open Tileset Manager:**
- Click **Tools → Tileset Manager** (or `Ctrl+T`)

**Screenshot: Tileset Manager interface**
*[Screenshot should show: List of tilesets, preview window, properties panel]*

**Features:**
- **Preview all tilesets** in project
- **Edit tileset properties** (name, tile size)
- **Set autotile configurations**
- **Manage collision templates**
- **Import/Export tilesets**

### Multiple Tilesets

**Use different tilesets per layer:**

```
Layer 2 (Ground): grass_tileset.png
Layer 7 (Walls): stone_walls.png
Layer 10 (Objects): furniture.png
```

**To change layer tileset:**
1. Select layer
2. Properties panel → Tileset dropdown
3. Choose tileset

---

## Painting Techniques

### Basic Painting

**Pencil Tool (B):**
- Click to place single tile
- Hold and drag to draw
- Precise, tile-by-tile control

**Brush Tool (P):**
- Shows preview before placing
- Can set brush size (1×1 to 10×10)
- Soft edges option (blends with existing tiles)

**Fill Tool (G):**
- Click to flood-fill contiguous area
- Similar tiles replaced
- Be careful - can fill entire map!

**Rectangle Tool (R):**
- Click and drag to draw rectangle
- Filled with selected tile
- Hold Shift for square (equal width/height)

**Eraser Tool (E):**
- Removes tiles from current layer
- Leaves transparency
- Can set eraser size

**Eyedropper Tool (I):**
- Click tile on map to select it in palette
- Quick way to reuse tiles
- Copies tile from current layer

### Selection and Copying

**Select Tool (V):**
- Click and drag to select area
- Selected area highlighted

**Copy selection:**
- Select area with Select tool
- `Ctrl+C` to copy
- `Ctrl+V` to paste
- Move pasted selection and click to place

**Cut selection:**
- Select area
- `Ctrl+X` to cut (removes and copies)
- Paste elsewhere

### Brush Settings

**Brush Size:**
```
1×1: Single tile
3×3: Small brush (good for details)
5×5: Medium brush
10×10: Large brush (fills quickly)
```

**Brush Shape:**
- **Square:** Fill entire brush area
- **Circle:** Round brush edges
- **Diamond:** Diagonal corners cut

**Brush Opacity:**
- 100%: Fully opaque
- 50%: Blend with existing layer
- 25%: Subtle overlay

---

## Autotiling System

### What is Autotiling?

**Autotiling** automatically selects the correct tile variant based on surrounding tiles. Perfect for walls, cliffs, water edges!

**Screenshot: Autotile before/after comparison**
*[Screenshot should show: Manual tile placement (left) vs autotile result (right)*

### Configuring Autotiles

1. **Open Autotile Editor** (`F11`)
2. **Select tileset**
3. **Click "New Autotile Set"**
4. **Configure:**

```
Autotile Set: stone_walls
Type: RPG Maker VX (47-tile)
Tileset: stone_walls.png

Behavior:
- Connect to similar tiles: Yes
- Corner smoothing: Yes
- Inner corners: Yes
```

5. **Map tile template** (which tiles are which variants)
6. **Save autotile configuration**

### Autotile Types

**RPG Maker VX (47-tile):**
- Industry standard
- Full corners, edges, interiors
- Most versatile

**Simplified (16-tile):**
- 4 corners, 4 edges, 4 side combos, 4 interior
- Easier to create
- Less variety

**Custom:**
- Define your own tile relationships
- Advanced users

### Using Autotiles

**Once configured:**

1. **Select autotile-enabled layer**
2. **Choose autotile group** from palette
3. **Paint normally** with Brush or Pencil
4. **Tiles auto-connect!**

**Example: Painting a wall**
```
Before autotile:
[Single wall tile repeated]

After autotile:
[Top edge tiles on top row]
[Middle tiles in middle]
[Bottom edge on bottom]
[Corners automatically placed]
```

**Screenshot: Autotile painting in action**
*[Screenshot should show: User painting, tiles automatically connecting]*

### Autotile Troubleshooting

**Problem: Tiles don't connect**

**Solution:**
- Verify autotile configuration is correct
- Check tile template mapping
- Ensure using autotile-enabled layer

**Problem: Wrong tiles appear**

**Solution:**
- Check tile template (might be mapped wrong)
- Verify tileset hasn't changed
- Reconfigure autotile set

---

## Object Placement

### Types of Objects

**NPCs:**
- Characters player can interact with
- Have dialogue, shops, quests
- Can move (static, random walk, patrol)

**Events:**
- Treasure chests
- Doors/transitions
- Cutscene triggers
- Interactive objects

**Spawn Points:**
- Player start position
- Enemy spawn locations
- Respawn points

**Zone Triggers:**
- Encounter zones (random battles)
- Area triggers (events on enter/exit)
- Safe zones, no-magic zones

### Placing an NPC

1. **Click "Place NPC" tool** (👤 icon)
2. **Click on map** where NPC should be
3. **Configure in Properties panel:**

```
Name: Shopkeeper
Sprite: npc_merchant.png
Direction: Down (facing down)

Movement:
Type: Static (doesn't move)
Speed: N/A

Event:
On Interact → Open Shop "general_store"
```

4. **NPC appears on map!**

**Screenshot: NPC placement with properties panel**
*[Screenshot should show: NPC placed on map, properties visible on right]*

### Placing Event Objects

**Treasure Chest:**

1. **Click "Place Object" → Treasure Chest**
2. **Click on map**
3. **Configure:**

```
Contents:
- Gold: 100
- Item: Healing Potion ×3

One-Time: Yes
Self Switch: A (prevents re-opening)
```

**Door/Transfer:**

1. **Place door sprite** (from tileset)
2. **Click "Place Event"**
3. **Position on door tile**
4. **Configure:**

```
Event Type: Transfer
Trigger: On Touch (or On Interact)

Transfer To:
Map: town_inn_interior
Position: X=5, Y=10 (inside the inn)
Direction: Down

Transition: Fade (or None for seamless)
```

### Spawn Points

**Player Start:**

1. **Click "Set Start Position" tool** (🚩)
2. **Click on map**
3. **Flag icon appears** showing spawn point

**Enemy Spawn Zone:**

1. **Click "Encounter Zone" tool**
2. **Click and drag** to draw rectangle
3. **Configure:**

```
Enemy Group: forest_monsters
Encounter Rate: 30 steps (average)
Disable Switch: 15 (can turn off encounters)
```

**Screenshot: Encounter zone drawn on map**
*[Screenshot should show: Semi-transparent rectangle showing encounter area]*

---

## Collision and Pathfinding

### Collision Layer

The **Collision Layer** defines where characters can walk.

**Screenshot: Collision layer view**
*[Screenshot should show: Map with red X's showing impassable tiles, green showing passable]*

### Editing Collision

1. **Click "Edit Collision" tool** (🚧)
2. **Map shows collision data:**
   - **Green tiles:** Passable (can walk)
   - **Red X:** Impassable (blocked)
   - **Blue arrow:** One-way passage

3. **Paint collision:**
   - Click tile to toggle passable/impassable
   - Brush tool works for large areas
   - Fill tool for quick setup

### Auto-Collision

**Automatically set collision from tiles:**

1. **Tools → Auto-Generate Collision**
2. **Choose method:**
   - **From tileset:** Use tileset's collision data
   - **From layer:** Tiles on wall layers = impassable
   - **Smart detect:** Analyze tile graphics

3. **Click Generate**
4. **Review and manually adjust**

### Directional Passage

**Allow movement in specific directions:**

```
One-Way Door:
- Can enter from North
- Cannot exit back North
- Forces player forward
```

**Cliff/Ledge:**
```
- Can move Down (jump off)
- Cannot move Up (can't climb)
```

**To set:**
1. Select tile in collision editor
2. Click "Directional Passage"
3. Choose allowed directions
4. Click Apply

### Navmesh for AI

**Navmesh** helps AI characters pathfind.

**Open Navmesh Editor:**
- Press `F12` or **Tools → Navmesh Editor**

**Screenshot: Navmesh editor showing pathfinding grid**
*[Screenshot should show: Map with navmesh overlay, walkable areas highlighted]*

**Generate navmesh:**

1. **Click "Generate Navmesh"**
2. **AI analyzes map:**
   - Reads collision layer
   - Identifies walkable areas
   - Creates navigation graph

3. **Review:**
   - Green areas = AI can path here
   - Red areas = Blocked
   - Blue lines = Connections

4. **Manually adjust** if needed
5. **Save navmesh**

**Use navmesh:**
- NPCs automatically use navmesh for pathfinding
- Event "Move Character" uses navmesh
- Ensures AI doesn't get stuck!

---

## Map Properties

### Global Map Settings

**Access:** Properties panel (when no object selected)

**Settings:**

```
General:
- Map ID: town_peaceful_001
- Display Name: "Peaceful Village"
- Dimensions: 30×20 tiles

Background:
- Color: Sky blue (#87CEEB)
- Parallax Image: clouds_parallax.png
- Scroll Speed: 0.5 (slower than camera)

Music:
- BGM: town_theme.ogg
- Volume: 80%
- Fade In: 1 second

Ambient Sound:
- Wind: gentle_wind.wav (loop)
- Volume: 30%

Encounter:
- Enabled: No (safe town)

Weather:
- Effect: None (or Rain, Snow, Fog)
- Intensity: 50%
```

**Screenshot: Map properties panel**
*[Screenshot should show: Properties panel with all map settings visible]*

### Region System

**Regions** divide map into areas for different behaviors.

**Use cases:**
- Different random encounters per region
- Area-specific music
- Zone-based weather
- Restricted areas

**Creating regions:**

1. **Enable Region Layer** (hidden by default)
2. **Paint with region IDs** (1-255)
3. **Configure region properties:**

```
Region 1: Town Center
- Encounters: Disabled
- Music: town_theme.ogg

Region 2: Forest Edge
- Encounters: Enabled (forest_monsters)
- Music: forest_ambient.ogg

Region 3: River
- Special: Water terrain
```

---

## Multi-Map Projects

### Map Organization

**Use Map Manager:**
- Press `Ctrl+M` or **Tools → Map Manager**

**Screenshot: Map Manager showing map tree**
*[Screenshot should show: Hierarchical map list, folders, map thumbnails]*

### Organizing Maps

**Create map folders:**

```
World/
├── Towns/
│   ├── town_peaceful
│   ├── town_capital
│   └── town_port
├── Dungeons/
│   ├── cave_forest
│   ├── temple_ancient
│   └── castle_demon
├── Interiors/
│   ├── inn_interior
│   ├── shop_general
│   └── house_mayor
└── World Map/
    └── overworld
```

**Benefits:**
- Easy navigation
- Logical structure
- Quick map switching

### Map Connections

**Link maps with transfer events:**

```
Town Map → Inn Exterior
- Door event at X=15, Y=8
- Transfers to: inn_interior at X=5, Y=10

Inn Interior → Town Map
- Exit event at X=5, Y=11
- Transfers to: town_peaceful at X=15, Y=9
```

**Seamless transitions:**
- Use "None" transition for instant
- Use "Fade" for indoor/outdoor
- Use "Slide" for same level areas

### World Map System

**Overworld map:**

```
Large map (200×150 tiles)
Shows towns, dungeons, landmarks

Town Icons:
- Click to enter town
- Or use automatic transfers

Scaling:
- 1 tile on world map = 1 full town
```

---

## Advanced Techniques

### Parallax Mapping

**Create depth with multiple scrolling backgrounds:**

**Sky layer:**
```
Parallax: clouds.png
Scroll Speed: 0.3× camera speed
Effect: Distant, slow-moving clouds
```

**Mountain layer:**
```
Parallax: mountains.png
Scroll Speed: 0.6× camera speed
Effect: Mid-distance mountains
```

**Foreground layer:**
```
Parallax: fog.png
Scroll Speed: 1.2× camera speed
Effect: Close fog moving faster than player
```

**Screenshot: Parallax layers showing depth**
*[Screenshot should show: Multiple parallax layers creating depth effect]*

### Lighting and Shadows

**Light sources:**

1. **Place light object**
2. **Configure:**

```
Type: Point Light
Radius: 5 tiles
Color: Warm yellow (#FFD700)
Intensity: 80%
Flicker: Slight (for torch)
```

**Global lighting:**

```
Ambient Light:
- Color: Cool blue (#4A5A7A)
- Intensity: 40%
- Effect: Nighttime ambience

Directional Light:
- Angle: 45° (top-left)
- Color: White
- Shadows: Enabled
```

### Animated Tiles

**Tiles that animate:**

```
Water Tiles:
- Frames: 4
- Speed: 300ms per frame
- Loop: Yes

Torch Flame:
- Frames: 6
- Speed: 100ms per frame
- Loop: Yes

Magic Portal:
- Frames: 8
- Speed: 150ms per frame
- Glow: Yes
```

**Setup:**

1. **Tileset Manager → Animations**
2. **Select base tile**
3. **Add animation frames**
4. **Set timing**
5. **Tiles animate automatically on map!**

### Dynamic Maps

**Maps that change during gameplay:**

**Example: Bridge Construction**

```
Map State: before_bridge
- Water tiles at X=10-15, Y=20
- Event: "Build Bridge Quest"

After quest complete:
- Event: Change Map Tiles
  Layer: Ground
  Area: X=10-15, Y=20
  New Tiles: Bridge tiles
- Player can now cross!
```

**Example: Seasons**

```
Spring Map: flowers, green grass
Summer Map: bright, lush
Autumn Map: orange, falling leaves
Winter Map: snow, bare trees

Switch map based on in-game season
```

---

## Optimization

### Performance Tips

**1. Limit map size:**
- Very large maps (200×200+) can slow down
- Split into multiple smaller maps if possible

**2. Reduce layer count:**
- Only use layers you need
- Empty layers still take processing time

**3. Optimize tilesets:**
- Combine small tilesets into atlases
- Use PNG compression
- Limit tileset size to 1024×1024 or smaller

**4. Minimize objects:**
- 100+ NPCs on one map can lag
- Use events sparingly
- Remove unused events

**5. LOD (Level of Detail):**
- Detailed tiles for close-up areas
- Simpler tiles for distant backgrounds

### Memory Management

**Asset streaming:**
```
Settings → Map Loading:
- Preload: Adjacent maps (1 map in each direction)
- Unload: Maps 2+ steps away
- Cache: Recently visited maps (5 maps)
```

**Reduces memory usage for large games!**

---

## Troubleshooting

### Common Issues

**Problem: Tiles look wrong/distorted**

**Solution:**
- Verify tileset tile size matches map tile size (both 32×32)
- Check for margin/spacing settings in tileset import
- Ensure tileset image hasn't been corrupted

**Problem: Collision doesn't work**

**Solution:**
- Check collision layer is enabled
- Verify collision data was saved
- Ensure character has Collider component
- Look for gaps in collision (use Fill tool to check)

**Problem: Autotiles not connecting**

**Solution:**
- Verify autotile configuration
- Check tile template mapping is correct
- Ensure using correct layer (autotile-enabled)
- Reconfigure autotile set if needed

**Problem: Map won't save**

**Solution:**
- Check file permissions
- Verify disk space
- Look for validation errors
- Try "Save As" with new name

**Problem: Transfer event doesn't work**

**Solution:**
- Verify target map exists
- Check target coordinates are valid (not outside map)
- Ensure transfer event has correct trigger (On Touch or On Interact)
- Look in Debug Console for errors

---

## Summary

You've mastered:

✅ **Level Builder interface** - Tools and workflow
✅ **Map creation** - Size, settings, and structure
✅ **Layer system** - 18-layer depth management
✅ **Tileset management** - Import, configure, use
✅ **Painting techniques** - All tools and methods
✅ **Autotiling** - Automatic tile connections
✅ **Object placement** - NPCs, events, spawns
✅ **Collision & pathfinding** - Walkability and AI navigation
✅ **Map properties** - BGM, weather, regions
✅ **Multi-map projects** - Organization and connections
✅ **Advanced techniques** - Parallax, lighting, animation
✅ **Optimization** - Performance and memory

## Next Steps

**Practice projects:**

1. **Small town** - 20×15 map with 5 buildings, NPCs, shops
2. **Dungeon floor** - 40×30 with rooms, corridors, treasures
3. **Forest map** - Trees, paths, hidden areas, encounters
4. **Multi-floor building** - 3 connected maps (ground, 2F, roof)
5. **World map** - Large-scale map connecting areas

**Further reading:**

- [Event Editor Guide](event_editor_guide.md) - Add interactivity to maps
- [Quick Start](quick_start.md) - Build a complete game
- [User Manual](user_manual.md) - Overall workflow
- [ENHANCED_LAYER_SYSTEM.md](ENHANCED_LAYER_SYSTEM.md) - Technical layer details
- [MAP_RENDERING_OPTIMIZATION.md](MAP_RENDERING_OPTIMIZATION.md) - Advanced optimization

---

**Happy mapping! 🗺️✨**

---

**Version History:**

- **1.0** (2025-11-15) - Initial comprehensive map editor guide

---

**NeonWorks Team**
Building worlds, one tile at a time.
