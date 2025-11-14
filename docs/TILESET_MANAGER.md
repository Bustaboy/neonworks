# Tileset Manager System

## Overview

The Tileset Manager System provides comprehensive support for loading, managing, and using tilesets in NeonWorks projects. It replaces the hardcoded 9-tile color palette with a dynamic, image-based tileset system that supports:

- Loading tileset images (PNG format)
- Automatic tile extraction and parsing
- Tile metadata (passability, terrain tags, animations)
- Recently used tiles tracking
- Favorites system
- Multiple tilesets per project
- Visual tileset picker UI component

## Architecture

The system consists of three main components:

### 1. TilesetManager (`neonworks/data/tileset_manager.py`)

Core manager class that handles:
- Loading and storing multiple tilesets
- Tile metadata management
- Recently used tiles tracking
- Favorites management
- Configuration persistence (save/load to JSON)

### 2. TilesetPickerUI (`neonworks/ui/tileset_picker_ui.py`)

Visual UI component that provides:
- Grid view of tileset tiles
- Tabs for tilesets, recent, and favorites
- Tile metadata display
- Mouse interaction (select, favorite)
- Scrolling for large tilesets

### 3. Level Builder Integration (`neonworks/ui/level_builder_ui.py`)

Integration with the level builder UI:
- Replaces hardcoded color palette
- Renders actual tile images
- Maintains backwards compatibility

## Quick Start

### Basic Usage

```python
import pygame
from neonworks.data.tileset_manager import TilesetManager

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))

# Create tileset manager
manager = TilesetManager(project_path="my_project")

# Add a tileset
manager.add_tileset(
    tileset_id="dungeon",
    name="Dungeon Tileset",
    image_path="assets/tilesets/dungeon.png",
    tile_width=32,
    tile_height=32,
    spacing=0,
    margin=0
)

# Load the tileset
manager.load_tileset("dungeon")

# Get a tile surface
tile_surface = manager.get_tile_surface("dungeon", 0)
screen.blit(tile_surface, (100, 100))
```

### Using the Tileset Picker UI

```python
from neonworks.ui.tileset_picker_ui import TilesetPickerUI

def on_tile_selected(tileset_id, tile_id):
    print(f"Selected tile {tile_id} from tileset {tileset_id}")

# Create picker UI
picker = TilesetPickerUI(
    x=500,
    y=50,
    width=300,
    height=500,
    tileset_manager=manager,
    on_tile_selected=on_tile_selected
)

# In your game loop
dt = clock.tick(60) / 1000.0
for event in pygame.event.get():
    picker.handle_event(event)

picker.update(dt)
picker.render(screen)
```

### Setting Tile Metadata

```python
# Set metadata for a tile
manager.set_tile_metadata(
    tileset_id="dungeon",
    tile_id=5,
    passable=False,
    terrain_tags=["wall", "stone"],
    name="Stone Wall"
)

# Get metadata
metadata = manager.get_tile_metadata("dungeon", 5)
print(f"Tile name: {metadata.name}")
print(f"Passable: {metadata.passable}")
print(f"Tags: {metadata.terrain_tags}")
```

### Recently Used Tiles

```python
# Add to recent tiles (automatically done when selecting in UI)
manager.add_to_recent("dungeon", 3)
manager.add_to_recent("dungeon", 7)

# Get recent tiles
recent = manager.get_recent_tiles(count=10)
for tileset_id, tile_id in recent:
    print(f"Recent: {tileset_id}:{tile_id}")
```

### Favorites System

```python
# Add to favorites
manager.add_to_favorites("dungeon", 10)

# Check if favorite
if manager.is_favorite("dungeon", 10):
    print("Tile 10 is favorited!")

# Remove from favorites
manager.remove_from_favorites("dungeon", 10)

# Get all favorites
favorites = manager.get_favorite_tiles()
```

### Save and Load Configuration

```python
# Save tileset configuration to file
manager.save_to_file("my_project/tilesets.json")

# Load configuration
manager.load_from_file("my_project/tilesets.json")
```

## Integration with Level Builder

The Level Builder UI now supports both the new tileset system and legacy color-based tiles for backwards compatibility.

### Using in Level Builder

```python
from neonworks.ui.level_builder_ui import LevelBuilderUI

# Create level builder
level_builder = LevelBuilderUI(
    screen=screen,
    world=world,
    project_path="my_project"
)

# Add a tileset
level_builder.add_tileset(
    tileset_id="terrain",
    name="Terrain Tileset",
    image_path="assets/tilesets/terrain.png"
)

# Toggle tileset picker visibility
level_builder.toggle_tileset_picker()

# Enable/disable tileset picker mode
level_builder.use_tileset_picker = True  # Use new system
level_builder.use_tileset_picker = False  # Use legacy color tiles
```

## Tileset Image Requirements

### Image Format
- **Format**: PNG (recommended for transparency)
- **Color depth**: 24-bit RGB or 32-bit RGBA

### Tile Layout
Tilesets should be organized in a grid layout:

```
[margin][tile][spacing][tile][spacing][tile]...[margin]
```

Example with 32x32 tiles, no spacing, no margin:
```
┌────────┬────────┬────────┬────────┐
│ Tile 0 │ Tile 1 │ Tile 2 │ Tile 3 │
├────────┼────────┼────────┼────────┤
│ Tile 4 │ Tile 5 │ Tile 6 │ Tile 7 │
├────────┼────────┼────────┼────────┤
│ Tile 8 │ Tile 9 │Tile 10 │Tile 11 │
└────────┴────────┴────────┴────────┘
```

### Parameters

- **tile_width**: Width of each tile in pixels (default: 32)
- **tile_height**: Height of each tile in pixels (default: 32)
- **spacing**: Pixels between tiles (default: 0)
- **margin**: Pixels around the edge of the tileset (default: 0)

## Tile Metadata Schema

### TileMetadata Class

```python
@dataclass
class TileMetadata:
    tile_id: int                          # Unique identifier in tileset
    passable: bool = True                 # Can entities walk through?
    terrain_tags: List[str] = []          # Terrain type tags
    animation_frames: List[int] = []      # Frame IDs for animation
    animation_speed: float = 0.0          # FPS for animation
    name: str = ""                        # Human-readable name
    custom_properties: Dict[str, any] = {}  # Custom key-value data
```

### Terrain Tags

Common terrain tags:
- `grass`, `dirt`, `stone`, `sand`
- `water`, `deep_water`, `shallow_water`
- `lava`, `ice`, `snow`
- `wall`, `floor`, `door`
- `ladder`, `stairs`

### Custom Properties

You can add any custom data to tiles:

```python
manager.set_tile_metadata(
    tileset_id="terrain",
    tile_id=15,
    custom_properties={
        "damage": 10,           # Damage dealt per turn
        "sound": "splash.wav",  # Sound effect when stepping
        "cost": 2               # Movement cost multiplier
    }
)

# Access custom properties
metadata = manager.get_tile_metadata("terrain", 15)
damage = metadata.custom_properties.get("damage", 0)
```

## UI Keyboard Shortcuts

When tileset picker is visible:

- **Left Click**: Select tile
- **Right Click**: Toggle favorite
- **Mouse Wheel**: Scroll tileset view
- **Tab Buttons**: Switch between Tileset/Recent/Favorites views

## File Format

Configuration is saved as JSON:

```json
{
  "active_tileset_id": "dungeon",
  "max_recent_tiles": 20,
  "tilesets": {
    "dungeon": {
      "tileset_id": "dungeon",
      "name": "Dungeon Tileset",
      "image_path": "assets/tilesets/dungeon.png",
      "tile_width": 32,
      "tile_height": 32,
      "columns": 16,
      "rows": 16,
      "spacing": 0,
      "margin": 0,
      "tile_count": 256,
      "metadata": {
        "0": {
          "tile_id": 0,
          "passable": false,
          "terrain_tags": ["wall"],
          "name": "Stone Wall"
        }
      }
    }
  },
  "recently_used": [
    {"tileset_id": "dungeon", "tile_id": 5},
    {"tileset_id": "dungeon", "tile_id": 3}
  ],
  "favorites": [
    {"tileset_id": "dungeon", "tile_id": 10}
  ]
}
```

## Best Practices

### Organization

1. **One tileset per theme**: Create separate tilesets for dungeons, outdoor, interior, etc.
2. **Consistent tile size**: Use the same tile size within a project (typically 16x16, 32x32, or 64x64)
3. **Logical tile ordering**: Group similar tiles together in the tileset image

### Performance

1. **Pre-load tilesets**: Load tilesets during initialization, not during gameplay
2. **Limit tileset size**: Very large tilesets (>1024x1024) may impact performance
3. **Use appropriate image sizes**: Don't use 4K images for 32x32 tiles

### Metadata

1. **Set passability**: Always set the `passable` flag for walkability
2. **Use terrain tags**: Tag tiles for game logic (water damage, lava, etc.)
3. **Name important tiles**: Give names to special tiles for easier identification

## Migration from Legacy System

If you have existing projects using the hardcoded color palette:

```python
# Keep legacy mode enabled
level_builder.use_tileset_picker = False

# Or create a compatibility tileset
manager = TilesetManager()
# Create colored tile images programmatically
# Map old tile_type strings to new tile_ids
```

## API Reference

### TilesetManager

| Method | Description |
|--------|-------------|
| `add_tileset(...)` | Add a new tileset |
| `remove_tileset(tileset_id)` | Remove a tileset |
| `load_tileset(tileset_id)` | Load tileset image and parse tiles |
| `get_tileset(tileset_id)` | Get TilesetInfo object |
| `get_active_tileset()` | Get currently active tileset |
| `set_active_tileset(tileset_id)` | Set active tileset |
| `get_tile_surface(tileset_id, tile_id)` | Get tile as pygame Surface |
| `add_to_recent(tileset_id, tile_id)` | Add to recently used |
| `get_recent_tiles(count)` | Get recently used tiles |
| `add_to_favorites(tileset_id, tile_id)` | Add to favorites |
| `remove_from_favorites(tileset_id, tile_id)` | Remove from favorites |
| `is_favorite(tileset_id, tile_id)` | Check if favorited |
| `get_favorite_tiles()` | Get all favorites |
| `set_tile_metadata(...)` | Set metadata for a tile |
| `get_tile_metadata(tileset_id, tile_id)` | Get tile metadata |
| `save_to_file(filepath)` | Save configuration to JSON |
| `load_from_file(filepath)` | Load configuration from JSON |

### TilesetPickerUI

| Method | Description |
|--------|-------------|
| `update(dt)` | Update picker state |
| `render(screen)` | Render picker UI |
| `handle_event(event)` | Handle input events |
| `get_selected_tile()` | Get selected (tileset_id, tile_id) |
| `set_selected_tile(tileset_id, tile_id)` | Set selected tile |
| `toggle_visibility()` | Toggle picker visibility |
| `show()` | Show picker |
| `hide()` | Hide picker |

## Examples

See `tests/test_tileset_manager.py` for comprehensive usage examples.

## Troubleshooting

### Tiles not rendering
- Ensure pygame display is initialized before loading tilesets
- Check that image path is correct (relative to project_path)
- Verify tile dimensions match the tileset image

### Tileset not found
- Check that tileset was added with `add_tileset()`
- Verify tileset_id matches exactly (case-sensitive)

### Performance issues
- Reduce tileset image size
- Limit number of loaded tilesets
- Use appropriate tile sizes for your game

## AI-Powered Features

### AI Tileset Generator

The AI Tileset Generator provides intelligent tileset creation and management:

```python
from neonworks.editor.ai_tileset_generator import AITilesetGenerator

# Create AI generator
ai_gen = AITilesetGenerator(tileset_manager)

# Generate a procedural tileset
tileset_surface, metadata = ai_gen.generate_procedural_tileset(
    terrain_types=["grass", "dirt", "stone", "water"],
    tiles_per_type=4,
    tile_size=32,
    include_variations=True
)

# Save the generated tileset
import pygame
pygame.image.save(tileset_surface, "generated_tileset.png")
```

### Auto-Tag Existing Tilesets

Automatically analyze and tag tiles using AI:

```python
# Analyze tileset and generate metadata
metadata = ai_gen.auto_tag_tileset(
    tileset_id="my_tileset",
    analyze_colors=True,
    analyze_patterns=True
)

# Apply generated metadata
for tile_id, tile_meta in metadata.items():
    manager.set_tile_metadata(
        tileset_id="my_tileset",
        tile_id=tile_id,
        passable=tile_meta.passable,
        terrain_tags=tile_meta.terrain_tags,
        name=tile_meta.name
    )
```

### AI Tileset Panel UI

The AI Tileset Panel provides a visual interface for AI features:

```python
from neonworks.ui.ai_tileset_ui import AITilesetPanel

# Create AI panel
ai_panel = AITilesetPanel(
    x=500,
    y=400,
    width=300,
    height=370,
    tileset_manager=manager,
    on_tileset_generated=lambda ts_id: print(f"Generated: {ts_id}")
)

# In your game loop
ai_panel.update(dt)
ai_panel.render(screen)
ai_panel.handle_event(event)
```

### Features:
- **Generate Tileset**: Create new tilesets with selected terrain types
- **Auto-Tag**: Automatically analyze and tag active tileset
- **Create Variations**: Generate variations of selected tiles
- **Terrain Selection**: Choose which terrain types to include

### Supported Terrain Types:
- Grass (green, passable)
- Dirt (brown, passable)
- Stone (gray, passable)
- Water (blue, non-passable)
- Sand (yellow, passable)
- Lava (red/orange, non-passable)
- Ice (light blue, passable, slippery)
- Wall (dark gray, non-passable)
- Floor (light gray, passable)
- Wood (brown, non-passable)

### Tile Variations

Generate variations of existing tiles:

```python
# Generate 3 variations of a tile
variations = ai_gen.suggest_tile_variations(
    tileset_id="my_tileset",
    tile_id=5,
    count=3
)

# Each variation is a pygame Surface
for i, variation in enumerate(variations):
    pygame.image.save(variation, f"tile_5_variant_{i}.png")
```

### Autotiling Rules

Create autotiling rules for seamless terrain blending:

```python
# Create autotiling rules for grass terrain
rules = ai_gen.create_autotiling_rules(
    tileset_id="terrain_tileset",
    terrain_tag="grass"
)

# Rules dictionary contains pattern-based tile selection
# Useful for implementing Wang tiles or blob autotiling
```

## Integration Example

Complete example using AI features with Level Builder:

```python
from neonworks.ui.level_builder_ui import LevelBuilderUI
from neonworks.editor.ai_tileset_generator import get_ai_tileset_generator

# Create level builder
level_builder = LevelBuilderUI(screen, world, project_path="my_game")

# Get AI generator
ai_gen = get_ai_tileset_generator(level_builder.tileset_manager)

# Generate a tileset with AI
tileset_surface, metadata = ai_gen.generate_procedural_tileset(
    terrain_types=["grass", "dirt", "water"],
    tiles_per_type=4,
    tile_size=32
)

# Save and add to project
pygame.image.save(tileset_surface, "my_game/assets/ai_terrain.png")
level_builder.add_tileset(
    tileset_id="ai_terrain",
    name="AI Generated Terrain",
    image_path="assets/ai_terrain.png"
)

# Apply AI-generated metadata
tileset = level_builder.tileset_manager.get_tileset("ai_terrain")
tileset.metadata = metadata
```

## Future Enhancements

Planned features for future versions:
- Enhanced AI terrain generation with neural networks
- Advanced autotiling with Wang tiles and Blob patterns
- Import from Tiled/LDtk formats
- Export tileset metadata to standard formats
- AI-powered tile animation generation
- Style transfer for tileset generation

---

**Version**: 0.2.0
**Last Updated**: 2025-11-14
**Maintainer**: NeonWorks Team
