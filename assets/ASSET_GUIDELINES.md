# Asset Guidelines for NeonWorks JRPG Engine

## Overview

This document outlines the expected formats, naming conventions, and organization standards for all assets used in the NeonWorks JRPG Engine.

## Directory Structure

```
assets/
├── characters/      # Player characters, NPCs, and character sprites
├── enemies/         # Enemy sprites and battle graphics
├── animations/      # Effect animations, skill animations
├── music/          # Background music tracks
├── sfx/            # Sound effects
├── tilesets/       # Map tilesets and autotiles
├── icons/          # Item icons, skill icons, status icons
├── ui/             # UI elements, windows, buttons, cursors
├── faces/          # Character portraits and face graphics
├── backgrounds/    # Battle backgrounds, title screens, parallax layers
├── asset_manifest.json  # Central asset registry
├── CREDITS.txt     # Attribution and licensing information
└── README.md       # Asset system documentation
```

## Supported File Formats

### Images

| Type | Recommended Format | Alternative Formats | Notes |
|------|-------------------|---------------------|-------|
| Characters | PNG (32-bit) | - | Use transparency, power-of-2 dimensions preferred |
| Enemies | PNG (32-bit) | - | Use transparency for battle sprites |
| Animations | PNG (sprite sheet) | GIF (simple animations) | Prefer sprite sheets for performance |
| Tilesets | PNG (32-bit) | - | Must have consistent tile dimensions |
| Icons | PNG (32-bit) | SVG (for UI icons) | Square dimensions recommended (16x16, 32x32, 64x64) |
| UI Elements | PNG (32-bit) | - | Consider nine-patch for scalable elements |
| Faces | PNG (32-bit) | - | Consistent dimensions (e.g., 96x96, 128x128) |
| Backgrounds | PNG, JPG | - | PNG for effects/transparency, JPG for static scenes |

### Audio

| Type | Recommended Format | Alternative Formats | Notes |
|------|-------------------|---------------------|-------|
| Music | OGG Vorbis | MP3, WAV | OGG preferred for licensing and quality |
| SFX | OGG Vorbis, WAV | MP3 | WAV for short clips, OGG for longer effects |

**Audio Specifications:**
- Music: 44.1kHz or 48kHz, stereo, 128-192 kbps (OGG)
- SFX: 44.1kHz, mono or stereo, 96-128 kbps (OGG) or 16-bit (WAV)

## Naming Conventions

### General Rules

1. Use lowercase letters, numbers, and underscores only
2. No spaces or special characters (except underscores and hyphens)
3. Be descriptive but concise
4. Include type prefix where appropriate
5. Use leading zeros for numbered sequences (e.g., `001`, `002`)

### File Naming Patterns

#### Characters
```
{type}_{name}_{variant}.{ext}

Examples:
- player_hero_idle.png
- npc_merchant_male_01.png
- character_warrior_spritesheet.png
```

#### Enemies
```
{category}_{name}_{variant}.{ext}

Examples:
- enemy_slime_green.png
- boss_dragon_red.png
- monster_goblin_warrior.png
```

#### Animations
```
{effect_type}_{name}_{variant}.{ext}

Examples:
- anim_fire_explosion.png
- effect_heal_sparkle.png
- skill_slash_vertical.png
```

#### Music
```
bgm_{scene}_{mood}_{number}.{ext}

Examples:
- bgm_town_peaceful_01.ogg
- bgm_battle_boss.ogg
- bgm_dungeon_dark_02.ogg
```

#### Sound Effects
```
sfx_{category}_{action}_{variant}.{ext}

Examples:
- sfx_ui_click.ogg
- sfx_combat_sword_01.wav
- sfx_env_door_open.ogg
- sfx_magic_fire_cast.ogg
```

#### Tilesets
```
tileset_{theme}_{type}_{size}.{ext}

Examples:
- tileset_dungeon_stone_32x32.png
- tileset_outdoor_grass_16x16.png
- tileset_interior_castle_32x32.png
```

#### Icons
```
icon_{category}_{name}.{ext}

Examples:
- icon_item_potion_hp.png
- icon_skill_fireball.png
- icon_status_poison.png
- icon_weapon_sword_01.png
```

#### UI Elements
```
ui_{type}_{variant}.{ext}

Examples:
- ui_window_default.png
- ui_button_large.png
- ui_cursor_hand.png
- ui_panel_menu.png
```

#### Faces
```
face_{character}_{expression}.{ext}

Examples:
- face_hero_normal.png
- face_hero_happy.png
- face_merchant_surprised.png
```

#### Backgrounds
```
bg_{scene}_{variant}.{ext}

Examples:
- bg_battle_forest.png
- bg_title_screen.jpg
- bg_menu_stars.png
- bg_parallax_mountains_layer1.png
```

## Sprite Sheet Specifications

### Character Sprite Sheets

**Standard Layout:**
- Frame size: 32x32 pixels (or 48x48 for larger characters)
- Layout: 4 rows (directions) × 12 columns (frames)
  - Row 1: Down/South
  - Row 2: Left/West
  - Row 3: Right/East
  - Row 4: Up/North
- Each direction typically has 3 frames for idle + 3 frames per animation state

**Alternative RPG Maker MV/MZ Format:**
- Frame size: 48x48 pixels
- Layout: 4 rows × 3 columns (idle + walk frames)
- Compatible with standard RPG Maker resources

### Animation Sprite Sheets

- Arrange frames left to right, single row preferred
- Include metadata: frame count, frame duration, loop setting
- Power-of-2 texture dimensions for optimal performance (e.g., 512x128, 1024x256)

## Asset Dimensions

### Recommended Sizes

| Asset Type | Standard Size | Notes |
|-----------|---------------|-------|
| Character Tiles | 32x32, 48x48 | Match tileset size |
| Enemy Sprites | 64x64 to 256x256 | Scale based on enemy size/importance |
| Map Tiles | 16x16, 32x32, 48x48 | Consistent per map/tileset |
| Icons | 32x32, 64x64 | Square, power-of-2 preferred |
| Face Graphics | 96x96, 128x128 | Square dimensions |
| UI Buttons | Variable | Use nine-patch for scalability |
| Battle Backgrounds | 800x600, 1280x720 | Match game resolution |

## Performance Considerations

1. **Texture Atlases**: Combine small assets into sprite sheets to reduce draw calls
2. **Power-of-2 Dimensions**: Use 16, 32, 64, 128, 256, 512, 1024, 2048 for optimal GPU performance
3. **Compression**: Use PNG compression; avoid BMP or uncompressed formats
4. **Audio Loop Points**: Set precise loop points for seamless music playback
5. **File Size**: Keep individual files under 2MB; use compression for larger assets

## Color Depth and Transparency

- **Characters/Enemies/Animations**: 32-bit PNG with alpha channel
- **Tilesets**: 32-bit PNG if transparency needed, 24-bit if opaque
- **Backgrounds**: 24-bit PNG or JPG (no transparency needed)
- **UI Elements**: 32-bit PNG with alpha channel for effects

## Asset Manifest Integration

All assets should be registered in `asset_manifest.json` with:
- Unique ID
- Display name
- File path (relative to assets/)
- Technical specifications (dimensions, format, etc.)
- Licensing information
- Tags for searchability

See `asset_manifest.json` for the complete metadata schema and examples.

## Quality Standards

### Visual Assets

1. **Consistency**: Maintain consistent art style across all assets
2. **Resolution**: High enough for target display, but optimized for performance
3. **Color Palette**: Use consistent color schemes and palettes
4. **Anti-aliasing**: Use appropriate anti-aliasing for smooth edges
5. **Transparency**: Clean alpha channels without fringing

### Audio Assets

1. **Normalization**: Normalize volume levels across all audio files
2. **Clipping**: Ensure no audio clipping or distortion
3. **Loop Points**: Test loop points for seamless transitions
4. **Format**: Use lossy compression appropriately for file size vs. quality

## Version Control

- Use git-lfs for large binary assets (recommended for files > 1MB)
- Include only source-ready assets; keep working files (.psd, .flp, etc.) separate
- Tag asset versions in commits when making significant updates

## Testing Checklist

Before adding assets to the manifest:

- [ ] File follows naming conventions
- [ ] Dimensions match specifications
- [ ] Format is correct and optimized
- [ ] Transparency is clean (if applicable)
- [ ] Audio loops correctly (if applicable)
- [ ] Asset loads in engine without errors
- [ ] Licensing information is documented
- [ ] Attribution added to CREDITS.txt
- [ ] Entry added to asset_manifest.json

## Additional Resources

- RPG Maker format specifications: https://rpgmaker.net/
- OpenGameArt.org for compatible assets: https://opengameart.org/
- GDQuest asset guidelines: https://www.gdquest.com/
- Texture packing tools: TexturePacker, ShoeBox

## Questions or Suggestions?

If you have questions about asset formats or suggestions for improving these guidelines, please open an issue in the project repository.
