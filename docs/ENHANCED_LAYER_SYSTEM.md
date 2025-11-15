# Enhanced Layer System Guide

**Version:** 2.0
**Author:** NeonWorks Team
**Last Updated:** 2025-11-15

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Layer Properties](#layer-properties)
4. [Layer Types](#layer-types)
5. [Layer Management](#layer-management)
6. [Layer Groups](#layer-groups)
7. [Parallax Backgrounds](#parallax-backgrounds)
8. [Advanced Features](#advanced-features)
9. [Backward Compatibility](#backward-compatibility)
10. [Best Practices](#best-practices)
11. [API Reference](#api-reference)

---

## Overview

The Enhanced Layer System provides advanced layer management for NeonWorks tilemaps with:

- **Unlimited layers**: Add/remove layers dynamically
- **Rich properties**: Name, opacity, visibility, locking, z-index
- **Layer groups**: Organize layers into folders
- **Parallax backgrounds**: Multiple parallax modes including auto-scroll
- **Layer operations**: Merge, duplicate, reorder
- **Backward compatibility**: Works with existing 3-layer maps

### Architecture

```
LayerManager
├── EnhancedTileLayer (multiple)
│   ├── LayerProperties (name, opacity, visible, locked, etc.)
│   └── Tile data (2D array)
└── LayerGroup (folders for organization)
    └── Child layers/groups
```

---

## Quick Start

### Creating a Simple Tilemap

```python
from neonworks.rendering.tilemap import Tilemap, TilemapBuilder

# Create tilemap with enhanced layers (default)
tilemap = Tilemap(width=50, height=50, tile_width=32, tile_height=32)

# Add layers
ground_id = tilemap.create_enhanced_layer("Ground")
objects_id = tilemap.create_enhanced_layer("Objects")
overlay_id = tilemap.create_enhanced_layer("Overlay", opacity=0.5)

# Get and modify layers
ground = tilemap.get_enhanced_layer(ground_id)
ground.set_tile(10, 10, tile_id=5)
```

### Using the Builder

```python
# Create standard 3-layer tilemap
tilemap = TilemapBuilder.create_layered_tilemap(
    width=50,
    height=50,
    tile_size=32,
    layer_names=["Ground", "Objects", "Overlay"]
)

# Create parallax scene
parallax_map = TilemapBuilder.create_parallax_scene(
    width=50,
    height=50,
    tile_size=32
)
```

---

## Layer Properties

Each layer has extensive properties for customization:

### Core Properties

```python
from neonworks.data.map_layers import LayerProperties, LayerType

props = LayerProperties(
    name="My Layer",           # Display name
    visible=True,              # Visibility
    locked=False,              # Locked (not editable)
    opacity=1.0,               # 0.0 to 1.0
    z_index=0,                 # Custom ordering
)
```

### Positioning

```python
props = LayerProperties(
    offset_x=0.0,              # Horizontal offset in pixels
    offset_y=0.0,              # Vertical offset in pixels
)
```

### Parallax

```python
from neonworks.data.map_layers import ParallaxMode

props = LayerProperties(
    parallax_mode=ParallaxMode.MANUAL,
    parallax_x=1.0,            # Horizontal parallax multiplier
    parallax_y=1.0,            # Vertical parallax multiplier
    auto_scroll_x=0.0,         # Auto-scroll speed (pixels/second)
    auto_scroll_y=0.0,
)
```

### Metadata

```python
props = LayerProperties(
    tags=["background", "sky"],
    metadata={"author": "Artist Name", "version": "1.0"}
)
```

---

## Layer Types

The system supports multiple layer types:

### LayerType.STANDARD

Normal tile layer for ground, objects, etc.

```python
tilemap.create_enhanced_layer(
    "Ground",
    layer_type=LayerType.STANDARD
)
```

### LayerType.PARALLAX_BACKGROUND

Background layer with parallax scrolling.

```python
tilemap.create_parallax_background(
    "Sky",
    parallax_x=0.5,
    parallax_y=0.5
)
```

### LayerType.PARALLAX_FOREGROUND

Foreground layer with parallax effect.

```python
from neonworks.data.map_layers import LayerProperties, LayerType

props = LayerProperties(
    name="Foreground",
    layer_type=LayerType.PARALLAX_FOREGROUND,
    parallax_x=1.2,
    parallax_y=1.0,
    opacity=0.7
)
tilemap.layer_manager.create_layer("Foreground", properties=props)
```

### LayerType.COLLISION

Collision-only layer (not rendered).

```python
props = LayerProperties(
    name="Collision",
    layer_type=LayerType.COLLISION
)
collision_layer = tilemap.layer_manager.create_layer("Collision", properties=props)
```

### LayerType.OVERLAY

Always-on-top overlay layer.

```python
props = LayerProperties(
    name="UI Overlay",
    layer_type=LayerType.OVERLAY
)
overlay = tilemap.layer_manager.create_layer("UI Overlay", properties=props)
```

---

## Layer Management

### Creating Layers

```python
# Simple creation
layer_id = tilemap.create_enhanced_layer("New Layer")

# With properties
from neonworks.data.map_layers import LayerProperties, LayerType

props = LayerProperties(
    name="Background",
    layer_type=LayerType.PARALLAX_BACKGROUND,
    opacity=0.8,
    parallax_x=0.5,
    parallax_y=0.5
)
layer_id = tilemap.layer_manager.create_layer(properties=props)
```

### Removing Layers

```python
# Remove by ID
tilemap.remove_layer(layer_id)
```

### Reordering Layers

```python
# Move layer to specific index (0 = bottom, higher = top)
tilemap.reorder_layer(layer_id, new_index=2)
```

### Duplicating Layers

```python
# Duplicate with auto-generated name
new_id = tilemap.duplicate_layer(layer_id)

# Duplicate with custom name
new_id = tilemap.duplicate_layer(layer_id, "Ground Copy")
```

### Merging Layers

```python
# Merge multiple layers (bottom to top order)
# Non-empty tiles from upper layers override lower layers
merged_id = tilemap.merge_layers(
    [layer1_id, layer2_id, layer3_id],
    new_name="Merged Layer"
)
```

### Getting Layers

```python
# By ID
layer = tilemap.get_enhanced_layer(layer_id)

# By name
layer = tilemap.get_enhanced_layer_by_name("Ground")

# Get all layers in render order
layer_ids = tilemap.layer_manager.get_render_order()
```

---

## Layer Groups

Organize layers into folders for better management.

### Creating Groups

```python
# Create root-level group
group_id = tilemap.create_layer_group("Background Layers")

# Create nested group
sub_group_id = tilemap.create_layer_group(
    "Sky Layers",
    parent_group_id=group_id
)
```

### Adding Layers to Groups

```python
# Create layer in group
layer_id = tilemap.create_enhanced_layer(
    "Sky",
    parent_group_id=group_id
)

# Move existing layer to group
tilemap.layer_manager.move_layer_to_group(layer_id, group_id)
```

### Group Operations

```python
# Get group
group = tilemap.layer_manager.get_group(group_id)

# Set group visibility (affects all children)
group.visible = False

# Remove group and keep children
tilemap.layer_manager.remove_group(group_id, remove_children=False)

# Remove group and all children
tilemap.layer_manager.remove_group(group_id, remove_children=True)
```

### Example Hierarchy

```python
# Create organized layer structure
bg_group = tilemap.create_layer_group("Background")
sky = tilemap.create_enhanced_layer("Sky", parent_group_id=bg_group)
mountains = tilemap.create_enhanced_layer("Mountains", parent_group_id=bg_group)

fg_group = tilemap.create_layer_group("Foreground")
trees = tilemap.create_enhanced_layer("Trees", parent_group_id=fg_group)
grass = tilemap.create_enhanced_layer("Grass", parent_group_id=fg_group)

# Result:
# - Background (group)
#   - Sky
#   - Mountains
# - Foreground (group)
#   - Trees
#   - Grass
```

---

## Parallax Backgrounds

Create depth with parallax scrolling layers.

### Manual Parallax

```python
# Create background that scrolls at 50% speed
bg_id = tilemap.create_parallax_background(
    "Distant Mountains",
    parallax_x=0.5,
    parallax_y=0.5
)
```

### Auto-Scrolling Backgrounds

```python
# Create auto-scrolling clouds
clouds_id = tilemap.create_parallax_background(
    "Clouds",
    parallax_x=0.6,
    parallax_y=1.0,
    auto_scroll_x=20.0,  # Scroll 20 pixels/second right
    auto_scroll_y=0.0
)
```

### Multi-Layer Parallax Scene

```python
from neonworks.rendering.tilemap import TilemapBuilder

# Creates pre-configured parallax scene with 5 layers
tilemap = TilemapBuilder.create_parallax_scene(50, 50, tile_size=32)

# Layers created:
# - Far Background (0.3x parallax)
# - Mid Background (0.6x parallax)
# - Ground (1.0x parallax)
# - Objects (1.0x parallax)
# - Foreground (1.2x parallax, 80% opacity)
```

### Updating Auto-Scroll

```python
# In your game loop
def update(dt):
    tilemap.update(dt)  # Updates all auto-scroll layers
```

---

## Advanced Features

### Custom Parallax Modes

```python
from neonworks.data.map_layers import LayerProperties, ParallaxMode

props = LayerProperties(
    parallax_mode=ParallaxMode.AUTO_SCROLL,
    auto_scroll_x=10.0,
    auto_scroll_y=-5.0  # Scroll up
)
```

Available modes:
- `ParallaxMode.NONE` - No parallax
- `ParallaxMode.MANUAL` - Manual multipliers
- `ParallaxMode.AUTO_SCROLL` - Automatic scrolling
- `ParallaxMode.PERSPECTIVE` - Perspective-based (future)

### Layer Locking

```python
# Prevent layer from being edited
layer = tilemap.get_enhanced_layer(layer_id)
layer.properties.locked = True

# Check before editing
if not layer.properties.locked:
    layer.set_tile(x, y, tile_id)
```

### Layer Tags

```python
# Tag layers for batch operations
props = LayerProperties(
    name="Trees",
    tags=["foliage", "parallax", "background"]
)

# Find layers by tag (custom implementation)
def get_layers_with_tag(tilemap, tag):
    return [
        layer for layer in tilemap.layer_manager.layers.values()
        if tag in layer.properties.tags
    ]
```

### Serialization

```python
# Save to dict
data = tilemap.layer_manager.to_dict()

# Save to JSON
import json
with open("map_layers.json", "w") as f:
    json.dump(data, f, indent=2)

# Load from dict
from neonworks.data.map_layers import LayerManager
manager = LayerManager.from_dict(data)

# Load from JSON
with open("map_layers.json", "r") as f:
    data = json.load(f)
    manager = LayerManager.from_dict(data)
```

---

## Backward Compatibility

### Legacy 3-Layer Maps

The system maintains full backward compatibility with old 3-layer maps.

#### Using Legacy Mode

```python
# Create tilemap in legacy mode
tilemap = Tilemap(
    width=50,
    height=50,
    tile_width=32,
    tile_height=32,
    use_enhanced_layers=False  # Legacy mode
)

# Use old API
tilemap.create_layer("ground")
tilemap.create_layer("objects")
tilemap.create_layer("overlay")
```

#### Migrating Legacy Maps

```python
from neonworks.rendering.tilemap import TilemapBuilder

# Migrate old tilemap to enhanced system
old_tilemap = ...  # Load legacy tilemap
new_tilemap = TilemapBuilder.migrate_legacy_tilemap(old_tilemap)

# Now has enhanced features
layer_id = new_tilemap.create_enhanced_layer("New Layer")
```

#### Converting from Legacy Data

```python
from neonworks.data.map_layers import LayerManager

# Legacy 3-layer format (list of 2D arrays)
legacy_data = [
    [[1, 2, 3], [4, 5, 6]],  # Ground
    [[7, 8, 9], [0, 0, 0]],  # Objects
    [[0, 0, 0], [10, 11, 12]]  # Overlay
]

# Convert to enhanced system
manager = LayerManager.from_legacy_layers(
    width=3,
    height=2,
    layer_data=legacy_data
)

# Access converted layers
ground = manager.get_layer_by_name("Ground")
objects = manager.get_layer_by_name("Objects")
overlay = manager.get_layer_by_name("Overlay")
```

---

## Best Practices

### Layer Organization

1. **Use groups** for complex scenes:
   ```python
   bg_group = tilemap.create_layer_group("Background")
   main_group = tilemap.create_layer_group("Main")
   fg_group = tilemap.create_layer_group("Foreground")
   ```

2. **Name layers descriptively**:
   ```python
   tilemap.create_enhanced_layer("Ground - Grass")
   tilemap.create_enhanced_layer("Objects - Trees")
   tilemap.create_enhanced_layer("Overlay - Fog")
   ```

3. **Use tags for categorization**:
   ```python
   props = LayerProperties(
       name="Trees",
       tags=["environment", "nature", "background"]
   )
   ```

### Performance

1. **Use collision layers** for non-visual data:
   ```python
   props = LayerProperties(
       name="Collision",
       layer_type=LayerType.COLLISION  # Not rendered
   )
   ```

2. **Limit auto-scroll layers**: Auto-scroll updates every frame.

3. **Group static layers**: Non-changing layers can share rendering optimizations.

### Parallax Guidelines

1. **Distance = slower scroll**:
   - Far background: 0.2 - 0.4x
   - Mid background: 0.5 - 0.7x
   - Near background: 0.8 - 0.9x
   - Ground: 1.0x
   - Foreground: 1.1 - 1.3x

2. **Layer opacity for depth**:
   ```python
   far_bg = LayerProperties(parallax_x=0.3, opacity=0.6)
   mid_bg = LayerProperties(parallax_x=0.6, opacity=0.8)
   ```

### Memory Management

1. **Remove unused layers**:
   ```python
   tilemap.remove_layer(unused_layer_id)
   ```

2. **Merge similar layers**:
   ```python
   merged = tilemap.merge_layers([layer1_id, layer2_id])
   tilemap.remove_layer(layer1_id)
   tilemap.remove_layer(layer2_id)
   ```

---

## API Reference

### Tilemap Methods

```python
# Layer creation
create_enhanced_layer(name, layer_type, parallax_x, parallax_y, opacity, parent_group_id) -> str
create_parallax_background(name, parallax_x, parallax_y, auto_scroll_x, auto_scroll_y) -> str

# Layer operations
remove_layer(layer_id) -> bool
reorder_layer(layer_id, new_index) -> bool
duplicate_layer(layer_id, new_name) -> str
merge_layers(layer_ids, new_name) -> str

# Layer access
get_enhanced_layer(layer_id) -> EnhancedTileLayer
get_enhanced_layer_by_name(name) -> EnhancedTileLayer

# Group operations
create_layer_group(name, parent_group_id) -> str

# Update
update(dt) -> None
```

### LayerManager Methods

```python
# Layer management
create_layer(name, properties, parent_group_id, insert_index) -> EnhancedTileLayer
remove_layer(layer_id) -> bool
get_layer(layer_id) -> EnhancedTileLayer
get_layer_by_name(name) -> EnhancedTileLayer
reorder_layer(layer_id, new_index) -> bool
move_layer_to_group(layer_id, new_parent_group_id) -> bool
duplicate_layer(layer_id, new_name) -> str
merge_layers(layer_ids, new_name) -> str

# Group management
create_group(name, parent_group_id, insert_index) -> LayerGroup
remove_group(group_id, remove_children) -> bool
get_group(group_id) -> LayerGroup

# Rendering
get_render_order() -> List[str]

# Utilities
update(dt) -> None
resize_all_layers(new_width, new_height, fill_tile) -> None

# Serialization
to_dict() -> Dict
from_dict(data) -> LayerManager
from_legacy_layers(width, height, layer_data) -> LayerManager
```

### EnhancedTileLayer Methods

```python
# Tile operations
get_tile(x, y) -> int
set_tile(x, y, tile_id) -> None
fill(tile_id) -> None
clear() -> None
resize(new_width, new_height, fill_tile) -> None

# Auto-scroll
update_auto_scroll(dt) -> None
get_effective_offset() -> Tuple[float, float]

# Serialization
to_dict() -> Dict
from_dict(data) -> EnhancedTileLayer
```

---

## Examples

### Example 1: Simple Platformer

```python
from neonworks.rendering.tilemap import Tilemap

# Create map
tilemap = Tilemap(100, 30, 32, 32)

# Background
sky = tilemap.create_parallax_background("Sky", 0.3, 0.3)
clouds = tilemap.create_parallax_background("Clouds", 0.5, 0.5, auto_scroll_x=10.0)
mountains = tilemap.create_parallax_background("Mountains", 0.7, 0.7)

# Main layers
ground = tilemap.create_enhanced_layer("Ground")
objects = tilemap.create_enhanced_layer("Objects")

# Foreground
foreground = tilemap.create_enhanced_layer("Foreground", opacity=0.5)
```

### Example 2: Top-Down RPG

```python
# Create organized structure
tilemap = Tilemap(100, 100, 32, 32)

# Background group
bg = tilemap.create_layer_group("Background")
floor = tilemap.create_enhanced_layer("Floor", parent_group_id=bg)
carpet = tilemap.create_enhanced_layer("Carpet", parent_group_id=bg)

# Objects group
obj = tilemap.create_layer_group("Objects")
furniture = tilemap.create_enhanced_layer("Furniture", parent_group_id=obj)
decorations = tilemap.create_enhanced_layer("Decorations", parent_group_id=obj)

# Overlay
roof = tilemap.create_enhanced_layer("Roof", opacity=0.6)
```

### Example 3: Auto-Scrolling Background

```python
# Space shooter with scrolling starfield
tilemap = Tilemap(100, 50, 32, 32)

# Multiple scrolling layers for depth
far_stars = tilemap.create_parallax_background(
    "Far Stars",
    parallax_x=0.2,
    parallax_y=1.0,
    auto_scroll_y=-5.0  # Scroll up slowly
)

near_stars = tilemap.create_parallax_background(
    "Near Stars",
    parallax_x=0.5,
    parallax_y=1.0,
    auto_scroll_y=-15.0  # Scroll up faster
)

# Game layer
game = tilemap.create_enhanced_layer("Game")

# Update in game loop
def update(dt):
    tilemap.update(dt)  # Updates auto-scroll
```

---

## Migration Checklist

When migrating from the old system to enhanced layers:

- [ ] Set `use_enhanced_layers=True` in Tilemap constructor
- [ ] Replace `create_layer()` with `create_enhanced_layer()`
- [ ] Replace `get_layer(index)` with `get_enhanced_layer(layer_id)`
- [ ] Update layer access to use layer IDs instead of indices
- [ ] Convert tile data from Tile objects to int arrays (if needed)
- [ ] Test rendering and layer visibility
- [ ] Update save/load code for new serialization format
- [ ] Add groups for better organization (optional)
- [ ] Consider adding parallax backgrounds (optional)

---

## Troubleshooting

### Layers not rendering

Check:
1. Layer visibility: `layer.properties.visible = True`
2. Layer opacity: `layer.properties.opacity > 0.0`
3. Layer type: Collision layers don't render
4. Tileset loaded: `tileset.load_tiles(asset_manager)`

### Auto-scroll not working

Ensure:
1. `parallax_mode` set to `ParallaxMode.AUTO_SCROLL`
2. `auto_scroll_x` or `auto_scroll_y` is non-zero
3. `tilemap.update(dt)` called every frame

### Layer order wrong

Use:
```python
# Check current order
order = tilemap.layer_manager.get_render_order()
print([tilemap.get_enhanced_layer(lid).properties.name for lid in order])

# Reorder
tilemap.reorder_layer(layer_id, new_index)
```

---

## Future Enhancements

Planned features for future versions:

- Perspective parallax mode
- Layer blending modes
- Animated tile support per-layer
- Layer effects (blur, tint, etc.)
- Multi-tileset support per layer
- Layer templates/presets

---

**Questions? Issues?** Check the [NeonWorks documentation](https://github.com/Bustaboy/neonworks) or open an issue.
