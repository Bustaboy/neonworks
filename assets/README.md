# NeonWorks Asset Library

Welcome to the NeonWorks JRPG Engine asset library. This directory contains all game assets including graphics, audio, and their associated metadata.

## Quick Start

### Directory Structure

```
assets/
├── characters/          # Player and NPC sprites
├── enemies/            # Enemy and monster sprites
├── animations/         # Visual effects and skill animations
├── music/              # Background music tracks
├── sfx/                # Sound effects
├── tilesets/           # Map tiles and autotiles
├── icons/              # Item, skill, and status icons
├── ui/                 # User interface elements
├── faces/              # Character portrait images
├── backgrounds/        # Battle and menu backgrounds
├── asset_manifest.json # Central asset registry
├── ASSET_GUIDELINES.md # Detailed format and naming specifications
├── CREDITS.txt         # Asset attribution and licensing
└── README.md          # This file
```

## Asset Manifest System

The `asset_manifest.json` file serves as the central registry for all game assets. It provides:

- **Unique identification** for each asset
- **Metadata** including dimensions, format, and technical specifications
- **License tracking** for attribution compliance
- **Tag system** for easy asset discovery
- **Relationship mapping** between related assets (e.g., character sprites and face graphics)

### Why Use the Manifest?

1. **Centralized Management**: All asset information in one place
2. **Runtime Loading**: Engine can query and load assets dynamically
3. **License Compliance**: Track attribution requirements automatically
4. **Asset Validation**: Verify asset specifications before integration
5. **Search and Discovery**: Find assets by tags, type, or properties
6. **Documentation**: Self-documenting asset library

## Adding New Assets

### Step-by-Step Process

1. **Choose the Correct Directory**
   - Place your asset in the appropriate subdirectory
   - Follow the naming conventions in `ASSET_GUIDELINES.md`

2. **Register in Manifest**
   - Add an entry to `asset_manifest.json` under the correct asset type
   - Include all required metadata fields
   - Assign a unique ID
   - Add relevant tags

3. **Add Attribution**
   - If using third-party assets, add attribution to `CREDITS.txt`
   - Include license information and source URLs
   - Mark attribution requirements in the manifest

4. **Test the Asset**
   - Load the asset in the engine to verify it works correctly
   - Check dimensions, transparency, loop points, etc.
   - Ensure performance is acceptable

### Example: Adding a Character Sprite

```json
{
  "id": "hero_001",
  "name": "Hero Sprite",
  "file_path": "characters/hero_spritesheet.png",
  "format": "png",
  "dimensions": {
    "width": 192,
    "height": 256
  },
  "sprite_sheet": {
    "enabled": true,
    "frame_width": 32,
    "frame_height": 32,
    "frames": 48
  },
  "animations": {
    "idle": "anim_hero_idle",
    "walk": "anim_hero_walk",
    "run": "anim_hero_run",
    "attack": "anim_hero_attack"
  },
  "tags": ["player", "protagonist", "human"],
  "license": "CC-BY-4.0",
  "author": "Artist Name",
  "attribution_required": true,
  "notes": "Main character sprite with 4-directional movement"
}
```

## Asset Types and Usage

### Characters
- **Purpose**: Player characters, NPCs, and overworld sprites
- **Format**: PNG sprite sheets (32-bit with alpha)
- **Typical Size**: 32x32 or 48x48 per frame
- **Use Cases**: Map exploration, cutscenes, party members

### Enemies
- **Purpose**: Battle sprites for enemies and bosses
- **Format**: PNG (32-bit with alpha)
- **Typical Size**: 64x64 to 256x256 depending on enemy size
- **Use Cases**: Combat encounters, bestiary

### Animations
- **Purpose**: Visual effects for skills, magic, and environmental effects
- **Format**: PNG sprite sheets or animated sequences
- **Typical Size**: Variable, usually 64x64 to 256x256
- **Use Cases**: Battle effects, skill animations, environmental effects

### Music
- **Purpose**: Background music for various scenes
- **Format**: OGG Vorbis (preferred) or MP3
- **Typical Length**: 1-3 minutes with loop points
- **Use Cases**: Towns, battles, dungeons, cutscenes

### Sound Effects (SFX)
- **Purpose**: Short audio clips for actions and events
- **Format**: OGG Vorbis or WAV
- **Typical Length**: 0.1-2 seconds
- **Use Cases**: UI feedback, combat sounds, environmental ambience

### Tilesets
- **Purpose**: Building blocks for maps and environments
- **Format**: PNG with consistent tile dimensions
- **Typical Size**: 16x16 or 32x32 per tile
- **Use Cases**: Map creation, level design

### Icons
- **Purpose**: Small graphics for items, skills, and status effects
- **Format**: PNG (32-bit with alpha)
- **Typical Size**: 32x32 or 64x64 (square)
- **Use Cases**: Inventory, skill menus, status displays

### UI Elements
- **Purpose**: Interface components like windows, buttons, and cursors
- **Format**: PNG (32-bit with alpha)
- **Typical Size**: Variable, often using nine-patch scaling
- **Use Cases**: Menus, dialog boxes, HUD elements

### Faces
- **Purpose**: Character portraits for dialog and menus
- **Format**: PNG (32-bit with alpha)
- **Typical Size**: 96x96 or 128x128 (square)
- **Use Cases**: Dialog boxes, character selection, status screens

### Backgrounds
- **Purpose**: Scenic backdrops for battles and menus
- **Format**: PNG or JPG
- **Typical Size**: Match game resolution (e.g., 1280x720)
- **Use Cases**: Battle scenes, title screen, menu backgrounds, parallax scrolling

## Working with the Engine

### Loading Assets Programmatically

The NeonWorks engine can load assets directly from the manifest:

```python
from engine.asset_loader import AssetLoader

# Initialize the asset loader
loader = AssetLoader('assets/asset_manifest.json')

# Load a specific asset by ID
hero_sprite = loader.load_asset('hero_001')

# Query assets by tag
fire_animations = loader.find_by_tag('fire')

# Get all assets of a type
all_music = loader.get_assets_by_type('music')

# Validate asset before loading
if loader.validate_asset('hero_001'):
    hero_sprite = loader.load_asset('hero_001')
```

### Asset Caching

The engine automatically caches loaded assets to improve performance:

- Images are cached in GPU memory when possible
- Audio files are preloaded for frequently used sounds
- Tilesets are cached for quick map rendering
- Cache can be cleared manually when needed

## Best Practices

### Organization

1. **Keep related assets together**: Group character sprites with their animations
2. **Use consistent naming**: Follow the conventions in `ASSET_GUIDELINES.md`
3. **Maintain the manifest**: Update it whenever you add, remove, or modify assets
4. **Document everything**: Add notes to manifest entries for context

### Performance

1. **Optimize file sizes**: Compress images appropriately
2. **Use sprite sheets**: Combine small images to reduce draw calls
3. **Set audio loop points**: Ensure seamless music playback
4. **Power-of-2 textures**: Use 16, 32, 64, 128, 256, 512, 1024, 2048 dimensions when possible

### Legal Compliance

1. **Track licenses**: Record every asset's license in the manifest
2. **Maintain CREDITS.txt**: Keep attribution information up to date
3. **Respect restrictions**: Follow license terms (commercial use, derivatives, etc.)
4. **Include attribution**: Display credits in your game when required

### Version Control

1. **Use git-lfs**: For large binary files (>1MB)
2. **Commit related changes together**: Asset + manifest entry + credits
3. **Write clear commit messages**: Describe what assets were added/changed
4. **Avoid committing working files**: Keep .psd, .flp, etc. in a separate directory

## Quality Checklist

Before finalizing any asset:

- [ ] File follows naming conventions
- [ ] Correct directory placement
- [ ] Manifest entry is complete and accurate
- [ ] License and attribution documented in CREDITS.txt
- [ ] Asset loads correctly in the engine
- [ ] Performance is acceptable (file size, render time)
- [ ] Visual quality meets project standards
- [ ] Audio levels are normalized (for audio assets)
- [ ] Transparency is clean (for image assets with alpha)
- [ ] Sprite sheet layout matches specifications (if applicable)

## Finding Assets

### Free and Open Source Assets

- **OpenGameArt.org**: Large collection of CC-licensed game assets
- **itch.io**: Many free and paid asset packs
- **Kenney.nl**: High-quality CC0 asset packs
- **FreeSVG.org**: Vector graphics for UI elements
- **Freesound.org**: Community-sourced sound effects
- **Free Music Archive**: CC-licensed music tracks

### Asset Creation Tools

- **Graphics**: GIMP, Krita, Aseprite (pixel art), Inkscape (vector)
- **Audio**: Audacity, LMMS, Bfxr (sound effects)
- **Sprite Sheets**: TexturePacker, ShoeBox, Aseprite

## Troubleshooting

### Asset Won't Load

1. Check file path in manifest matches actual file location
2. Verify file format is supported
3. Ensure file isn't corrupted
4. Check file permissions
5. Review engine logs for specific error messages

### Performance Issues

1. Reduce file sizes (compress images, use OGG for audio)
2. Use sprite sheets instead of individual files
3. Enable asset caching in engine settings
4. Optimize sprite sheet layouts
5. Consider reducing asset dimensions

### Licensing Questions

1. Read the license file or website carefully
2. Check if commercial use is allowed
3. Verify if attribution is required
4. Confirm if derivatives/modifications are permitted
5. When in doubt, contact the original creator

## Integration with Editor

The NeonWorks editor provides a visual interface for:

- **Browsing assets**: View all assets by type with thumbnails
- **Preview**: See and hear assets before using them
- **Import wizard**: Guided asset import with automatic manifest creation
- **Batch operations**: Import multiple assets at once
- **Validation**: Check asset specifications against requirements
- **License management**: Track and display attribution requirements

Access the asset manager from the editor's main menu: **Tools → Asset Manager**

## Future Enhancements

Planned improvements to the asset system:

- [ ] Automatic thumbnail generation
- [ ] Asset version tracking and history
- [ ] Integrated asset download from free sources
- [ ] Visual manifest editor
- [ ] Asset dependency graph
- [ ] Automated format conversion
- [ ] Asset usage tracking (which assets are used in which scenes)
- [ ] Export tool for creating redistributable asset packs

## Contributing Assets

If you create assets for the NeonWorks community:

1. Ensure you have the right to share them
2. Choose an appropriate open license (CC-BY, CC0, etc.)
3. Include source files when possible
4. Document usage in a README
5. Add example manifest entries
6. Consider sharing on OpenGameArt.org or itch.io

## Support

For questions or issues with the asset system:

- Check `ASSET_GUIDELINES.md` for detailed specifications
- Review `asset_manifest.json` for schema and examples
- Open an issue in the GitHub repository
- Consult the NeonWorks documentation

## License

The asset library structure and manifest system are part of the NeonWorks JRPG Engine.
Individual assets have their own licenses as specified in `CREDITS.txt` and `asset_manifest.json`.

---

**Last Updated**: 2025-11-14
**Version**: 1.0.0
**Maintained by**: NeonWorks Development Team
