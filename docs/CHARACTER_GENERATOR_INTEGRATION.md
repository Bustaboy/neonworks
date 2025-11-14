# Character Generator Integration Guide

## Overview

The NeonWorks Character Generator is now fully integrated with the game engine's asset pipeline, database system, and level editor. This guide explains the complete workflow from character creation to placement in game levels.

## Features

### 1. **Asset Browser Integration**
- Generated characters are automatically copied to `assets/sprites/`
- Sprites appear in the asset browser immediately after export
- Auto-refresh ensures asset browser shows the latest exports

### 2. **Database Integration**
- **"Create Actor" button** in character generator
- Automatically creates an Actor entry in the database
- Links the generated sprite to the actor
- Opens database editor with the new actor selected

### 3. **AI-Powered Bio Generation** 🆕
- **Automatic character biography generation** based on appearance
- **Three importance levels** with appropriate bio length:
  - **NPC**: 1-2 sentences (40-80 words) - Quick descriptions
  - **Supporting**: 2-4 sentences (80-150 words) - Moderate detail
  - **Main Character**: 4-8 sentences (150-300 words) - Rich backstory
- **AI generation by default** for unique, contextual bios
- **Template fallback** option for consistent style
- **Manual editing** capability for custom touches
- Analyzes character appearance (armor, weapons, colors)
- Detects character type (warrior, mage, thief, etc.)
- Bios automatically added to Actor database entries

### 4. **Export History Tracking**
- All exports are logged with timestamp
- History saved to `exports/characters/export_history.json`
- Tracks character name, file paths, layer count, **bios**, and more
- Bio data preserved in export history for reference

### 5. **Batch Export**
- Export all character presets at once
- Processes all `.json` files in `presets/characters/`
- **Automatically generates bios** for all characters
- Creates sprites for all presets with one click
- NPCs use short bios, main characters get detailed ones

### 6. **Default Character Presets**
10 pre-configured character templates:
- **Warrior** - Heavy armor and longsword
- **Mage** - Wizard robes and staff
- **Thief** - Dark leather and daggers
- **Cleric** - White robes and mace
- **Archer** - Light armor and bow
- **Knight** - Shining armor with cape
- **Paladin** - Holy armor with aura
- **Assassin** - Shadow gear and twin blades
- **Bard** - Colorful attire and lute
- **Monk** - Simple robes and wraps

## Complete Workflow

### Step 1: Generate Character

1. Press **F8** to open the Character Generator
2. Select components from the palette:
   - Choose a **Body** type
   - Add **Hair**, **Eyes**, **Clothes**, etc.
   - Stack layers in the desired order
3. Customize colors with the **Color Tint** button
4. Use **AI description** for quick generation:
   ```
   "A brave knight with brown hair and blue armor"
   ```
5. Preview animations with the direction controls
6. **Set Character Importance** (NPC/Supporting/Main):
   - Select importance level in the preview panel
   - Determines bio length and detail
   - If bio already exists, changing importance requires confirmation
   - Prevents accidental loss of custom bio text
7. **Bio Generation**:
   - Click "Regenerate Bio" button to create bio
   - Switch between AI and Template modes
   - Click "Edit Bio" to manually customize
   - **User control**: Bios never regenerate automatically
   - **Safety**: Importance changes show confirmation dialog

### Step 2: Export to Assets

Click the **"Export PNG"** button:
- Saves to `exports/characters/<name>.png`
- **Automatically copies** to `assets/sprites/<name>.png`
- Adds entry to export history
- Refreshes asset browser

### Step 3: Create Database Actor

Click the **"Create Actor"** button:
- Exports character (if not already done)
- Creates new Actor entry in database
- Sets actor name to character name
- Links character sprite file
- Opens Database Editor with actor selected

### Step 4: Configure Actor in Database

The Database Editor (F6) opens automatically:
- Edit actor stats (HP, MP, Attack, Defense)
- Set initial level and max level
- Assign a class
- Add skills and equipment
- Save database when done

### Step 5: Place in Level Editor

1. Open **Level Builder** (F7)
2. Select **Entity tool**
3. Choose entity template (or use custom actor)
4. Click on map to place character
5. Characters use sprites from asset browser

## Keyboard Shortcuts

| Key | Function |
|-----|----------|
| F5  | Event Editor |
| F6  | Database Editor |
| F7  | Level Builder |
| F8  | **Character Generator** |
| F9  | Face Generator |
| ESC | Close active UI |

## Advanced Features

### Batch Export All Presets

To export all 10 default presets at once:

1. Open Character Generator (F8)
2. Click **"Batch Export"** button
3. All presets in `presets/characters/` are exported
4. Creates sprites for all characters
5. Copies all to asset browser

This is useful for quickly populating your game with NPC sprites.

### Bio Generation System

The bio generator analyzes character appearance and creates contextually appropriate biographies:

**Importance Levels:**

1. **NPC (40-80 words)**
   - Quick, one-line description
   - Focus on role and appearance
   - Example: "Marcus is a battle-hardened warrior clad in heavy plate armor, wielding a longsword with practiced ease."

2. **Supporting Character (80-150 words)**
   - 2-4 sentence description
   - Includes personality hints
   - Background suggestion
   - Example: "Captain Elena is a veteran warrior whose plate armor bears the scars of countless battles. Wielding a longsword, she has proven her worth time and again. Rumors speak of a difficult past that forged her into who she is today. Those who know her speak of unwavering determination."

3. **Main Character (150-300 words)**
   - Rich, detailed backstory
   - Personality and motivations
   - Multiple paragraphs
   - Character arc hints
   - Example: Full multi-paragraph backstory with origin, development, and current state

**AI vs Templates:**

- **AI Mode** (Default): Generates unique bios analyzing:
  - Armor type (heavy/light/robes)
  - Weapon choice
  - Color scheme
  - Layer composition
  - Character type detected from name

- **Template Mode**: Uses consistent templates with variables:
  - More predictable output
  - Faster generation
  - Good for batch operations
  - Easier to maintain style consistency

**Manual Editing:**

1. Click "Edit Bio" button after generation
2. Modify text in editor
3. Save changes (marked as manual override)
4. Original still preserved in history

**Data Loss Prevention System:**

The character generator includes comprehensive protections against accidental data loss:

**1. Bio Regeneration Protection:**
When changing a character's importance level after a bio exists:
```
Bio Regeneration Required
Changing importance from NPC to MAIN will require regenerating the bio.
This will overwrite your current bio.
[Yes, Regenerate]  [No, Keep Bio]
```

**2. Load Preset Protection:**
When loading a preset while you have unsaved work:
```
Load Preset Warning
You have unsaved changes.
Loading 'Warrior.json' will replace your current character.
[Load Anyway]  [Cancel]
```

**3. Randomize Protection:**
When randomizing with existing character data:
```
Randomize Warning
You have unsaved changes.
Randomizing will replace your current character.
[Randomize]  [Cancel]
```

**4. Clear All Protection:**
When clearing character with existing layers:
```
Clear All Warning
This will remove all layers and data.
This action cannot be undone.
[Clear All]  [Cancel]
```

**5. Component Replacement Warning:**
When adding a component to a layer that already has one:
```
Replace Component?
Layer TORSO already has: 'leather_vest'
Replace with 'plate_armor'?
[Replace]  [Cancel]
```

All destructive operations require explicit confirmation, preventing accidental data loss.

**Manual Bio Regeneration:**

Use the "Regenerate Bio" button to manually trigger bio generation:
- Always available when character has layers
- Safe to use - you're explicitly requesting regeneration
- Respects current importance level
- Respects AI/Template mode setting

### Export History

View export history at:
```
exports/characters/export_history.json
```

Each entry contains:
```json
{
  "character_name": "Warrior",
  "export_path": "exports/characters/Warrior.png",
  "assets_path": "assets/sprites/Warrior.png",
  "timestamp": "2025-11-14T10:30:00",
  "preset_file": "presets/characters/Warrior.json",
  "layers_count": 6,
  "importance": "npc",
  "has_bio": true,
  "bio": {
    "description": "Marcus is a battle-hardened warrior...",
    "note": "NPC: Marcus is a battle-hardened warrior..."
  }
}
```

### Creating Custom Presets

1. Generate a character in the Character Generator
2. Click **"Save Preset"**
3. Preset saved to `presets/characters/<name>.json`
4. Use **"Load Preset"** to reload later
5. Include in batch exports automatically

## File Structure

```
neonworks/
├── assets/
│   └── sprites/               # Exported character sprites (auto-copied)
│       ├── Warrior.png
│       ├── Mage.png
│       └── ...
│
├── exports/
│   └── characters/            # Export directory
│       ├── export_history.json
│       ├── Warrior.png
│       └── ...
│
├── presets/
│   └── characters/            # Character presets
│       ├── warrior.json
│       ├── mage.json
│       ├── thief.json
│       ├── cleric.json
│       ├── archer.json
│       ├── knight.json
│       ├── paladin.json
│       ├── assassin.json
│       ├── bard.json
│       └── monk.json
│
└── data/
    └── database.json          # Game database (actors, items, etc.)
```

## Integration Architecture

### Component Connections

```
Character Generator UI
    ↓
    ├─→ Export System
    │   ├─→ exports/characters/
    │   ├─→ assets/sprites/ (auto-copy)
    │   └─→ export_history.json
    │
    ├─→ Database Editor
    │   ├─→ Create Actor
    │   ├─→ Set sprite reference
    │   └─→ data/database.json
    │
    └─→ Asset Browser
        ├─→ Auto-refresh
        └─→ Display new sprites
```

### Master UI Manager

The `MasterUIManager` connects all components:

```python
# In engine initialization
from neonworks.engine.ui.master_ui_manager import MasterUIManager

ui_manager = MasterUIManager(screen)

# Components are auto-connected:
# - Character Generator → Database Editor
# - Character Generator → Asset Browser
# - Character Generator → Level Builder
```

## API Reference

### CharacterGeneratorUI Methods

```python
# Set UI component references
character_gen.set_ui_references(
    database_editor=db_editor,
    asset_browser=asset_browser,
    level_builder=level_builder
)

# Export character
character_gen._export_character()
# → Exports to exports/characters/
# → Copies to assets/sprites/
# → Updates export history
# → Refreshes asset browser

# Create actor from character
character_gen._create_actor_from_character()
# → Exports if needed
# → Creates Actor in database
# → Opens database editor

# Batch export all presets
character_gen._batch_export_characters()
# → Exports all presets/characters/*.json
# → Creates sprites for all
```

### Export History Structure

```python
{
    "character_name": str,
    "export_path": str,
    "assets_path": str,
    "timestamp": str,  # ISO 8601 format
    "preset_file": str,
    "layers_count": int
}
```

## Troubleshooting

### Character not appearing in Asset Browser
- Check that export succeeded (look for ✓ message)
- Verify file exists in `assets/sprites/`
- Press **Refresh** button in asset browser
- Restart asset browser (F7 close, F7 open)

### Database Editor not opening
- Check that database path exists: `data/database.json`
- Ensure database editor is imported correctly
- Check console for error messages

### Batch export fails
- Verify presets exist in `presets/characters/`
- Check preset JSON syntax is valid
- Ensure component IDs in presets exist

### Export history not saving
- Check write permissions on `exports/characters/`
- Verify JSON syntax in export_history.json
- Check disk space

## Best Practices

1. **Name characters descriptively**
   - Use names like "Guard_Male_01" instead of "Character1"
   - Helps identify sprites in asset browser

2. **Save presets before exporting**
   - Easier to modify later
   - Can re-export with changes
   - Included in batch exports

3. **Use batch export for NPC populations**
   - Create presets for all NPC types
   - Batch export to generate all sprites
   - Consistent style across characters

4. **Track exports with history**
   - Review `export_history.json` periodically
   - Identify which characters need updates
   - Maintain version control

5. **Test workflow end-to-end**
   - Generate → Export → Create Actor → Place
   - Verify sprite displays correctly in-game
   - Check database links are correct

## Example: Complete Character Creation

Here's a complete example of creating and using a character:

```python
# 1. Generate character (or use preset)
# Press F8, select "Load Preset", choose "warrior.json"

# 2. Customize if desired
# - Change hair color
# - Add accessories
# - Modify weapon

# 3. Export
# Click "Export PNG"
# → exports/characters/Warrior.png
# → assets/sprites/Warrior.png

# 4. Create Actor
# Click "Create Actor"
# → Database Editor opens
# → Actor "Warrior" created with ID 1

# 5. Configure Actor
# - Set initial level: 5
# - Set max level: 99
# - Assign class: "Fighter"
# - Add skills: "Slash", "Guard"

# 6. Save Database
# Click "Save" in Database Editor
# → data/database.json updated

# 7. Place in Level
# Press F7 for Level Builder
# - Select Entity tool
# - Choose "Warrior" from actor list
# - Click on map to place
# → Warrior sprite appears on map

# 8. Test in game
# Run game, verify character appears with correct sprite
```

## Future Enhancements

Planned features for future releases:

- [ ] Visual preset picker in UI
- [ ] Animation preview in asset browser
- [ ] Bulk actor creation from presets
- [ ] Character template importer
- [ ] Sprite sheet format options
- [ ] Equipment preview system
- [ ] Character comparison view
- [ ] Export to multiple sizes

## Support

For issues or questions:
- Check `/home/user/neonworks/STATUS.md`
- Review `/home/user/neonworks/CLAUDE.md`
- See code at `/home/user/neonworks/engine/ui/character_generator_ui.py`

---

**Last Updated:** 2025-11-14
**Version:** 1.0
**Engine Version:** 0.1.0
