"""
Enhanced Map Layer System

Provides advanced layer management for tilemaps including:
- Unlimited dynamic layers (add/remove/reorder)
- Layer properties (name, opacity, locked, visible)
- Layer groups/folders for organization
- Parallax background layer types
- Layer merge functionality
- Backward compatibility with 3-layer maps
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import uuid4


class LayerType(Enum):
    """Type of layer"""

    STANDARD = "standard"  # Normal tile layer
    PARALLAX_BACKGROUND = "parallax_background"  # Auto-scrolling background
    PARALLAX_FOREGROUND = "parallax_foreground"  # Auto-scrolling foreground
    COLLISION = "collision"  # Collision-only layer (not rendered)
    OVERLAY = "overlay"  # Always-on-top overlay


class ParallaxMode(Enum):
    """Parallax scrolling mode"""

    NONE = "none"  # No parallax
    MANUAL = "manual"  # Manual parallax_x/parallax_y values
    AUTO_SCROLL = "auto_scroll"  # Automatic scrolling
    PERSPECTIVE = "perspective"  # Perspective-based parallax


@dataclass
class LayerProperties:
    """Properties for a map layer"""

    # Core properties
    name: str = "New Layer"
    visible: bool = True
    locked: bool = False
    opacity: float = 1.0  # 0.0 to 1.0

    # Positioning
    offset_x: float = 0.0
    offset_y: float = 0.0
    z_index: int = 0  # For custom ordering

    # Parallax
    parallax_mode: ParallaxMode = ParallaxMode.MANUAL
    parallax_x: float = 1.0
    parallax_y: float = 1.0
    auto_scroll_x: float = 0.0  # Pixels per second
    auto_scroll_y: float = 0.0

    # Layer type
    layer_type: LayerType = LayerType.STANDARD

    # Metadata
    layer_id: str = field(default_factory=lambda: str(uuid4()))
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "name": self.name,
            "visible": self.visible,
            "locked": self.locked,
            "opacity": self.opacity,
            "offset_x": self.offset_x,
            "offset_y": self.offset_y,
            "z_index": self.z_index,
            "parallax_mode": self.parallax_mode.value,
            "parallax_x": self.parallax_x,
            "parallax_y": self.parallax_y,
            "auto_scroll_x": self.auto_scroll_x,
            "auto_scroll_y": self.auto_scroll_y,
            "layer_type": self.layer_type.value,
            "layer_id": self.layer_id,
            "tags": self.tags.copy(),
            "metadata": self.metadata.copy(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> LayerProperties:
        """Create from dictionary"""
        data = data.copy()
        if "parallax_mode" in data:
            data["parallax_mode"] = ParallaxMode(data["parallax_mode"])
        if "layer_type" in data:
            data["layer_type"] = LayerType(data["layer_type"])
        return cls(**data)


@dataclass
class EnhancedTileLayer:
    """
    Enhanced tile layer with advanced features.

    This extends the basic TileLayer concept with:
    - Rich properties (locking, metadata, etc.)
    - Dynamic management (can be added/removed)
    - Group membership
    - Advanced parallax modes
    """

    # Dimensions
    width: int
    height: int

    # Tile data (2D array of tile IDs, 0 = empty)
    tiles: List[List[int]] = field(default_factory=list)

    # Layer properties
    properties: LayerProperties = field(default_factory=LayerProperties)

    # Parent group (if any)
    parent_group_id: Optional[str] = None

    # Auto-scroll state
    _scroll_offset_x: float = 0.0
    _scroll_offset_y: float = 0.0

    def __post_init__(self):
        """Initialize tile data if not provided"""
        if not self.tiles:
            self.tiles = [[0 for _ in range(self.width)] for _ in range(self.height)]

    def get_tile(self, x: int, y: int) -> int:
        """Get tile ID at position"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return 0

    def set_tile(self, x: int, y: int, tile_id: int):
        """Set tile ID at position"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[y][x] = tile_id

    def fill(self, tile_id: int):
        """Fill entire layer with a tile"""
        for y in range(self.height):
            for x in range(self.width):
                self.tiles[y][x] = tile_id

    def clear(self):
        """Clear layer (fill with empty tiles)"""
        self.fill(0)

    def resize(self, new_width: int, new_height: int, fill_tile: int = 0):
        """Resize layer, preserving existing tiles where possible"""
        new_tiles = [[fill_tile for _ in range(new_width)] for _ in range(new_height)]

        # Copy existing tiles
        for y in range(min(self.height, new_height)):
            for x in range(min(self.width, new_width)):
                new_tiles[y][x] = self.tiles[y][x]

        self.tiles = new_tiles
        self.width = new_width
        self.height = new_height

    def update_auto_scroll(self, dt: float):
        """Update auto-scroll offset"""
        if self.properties.parallax_mode == ParallaxMode.AUTO_SCROLL:
            self._scroll_offset_x += self.properties.auto_scroll_x * dt
            self._scroll_offset_y += self.properties.auto_scroll_y * dt

    def get_effective_offset(self) -> Tuple[float, float]:
        """Get effective offset including auto-scroll"""
        return (
            self.properties.offset_x + self._scroll_offset_x,
            self.properties.offset_y + self._scroll_offset_y,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "width": self.width,
            "height": self.height,
            "tiles": [row.copy() for row in self.tiles],
            "properties": self.properties.to_dict(),
            "parent_group_id": self.parent_group_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EnhancedTileLayer:
        """Create from dictionary"""
        properties = LayerProperties.from_dict(data.get("properties", {}))
        return cls(
            width=data["width"],
            height=data["height"],
            tiles=data.get("tiles", []),
            properties=properties,
            parent_group_id=data.get("parent_group_id"),
        )


@dataclass
class LayerGroup:
    """
    Group/folder for organizing layers.

    Groups can contain layers and other groups, forming a tree structure.
    """

    # Group properties
    name: str = "New Group"
    group_id: str = field(default_factory=lambda: str(uuid4()))
    visible: bool = True
    locked: bool = False
    expanded: bool = True  # UI state

    # Hierarchy
    parent_group_id: Optional[str] = None
    child_ids: List[str] = field(default_factory=list)  # Layer or group IDs

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_child(self, child_id: str):
        """Add a child layer or group"""
        if child_id not in self.child_ids:
            self.child_ids.append(child_id)

    def remove_child(self, child_id: str):
        """Remove a child layer or group"""
        if child_id in self.child_ids:
            self.child_ids.remove(child_id)

    def reorder_child(self, child_id: str, new_index: int):
        """Reorder a child within this group"""
        if child_id in self.child_ids:
            self.child_ids.remove(child_id)
            new_index = max(0, min(new_index, len(self.child_ids)))
            self.child_ids.insert(new_index, child_id)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "name": self.name,
            "group_id": self.group_id,
            "visible": self.visible,
            "locked": self.locked,
            "expanded": self.expanded,
            "parent_group_id": self.parent_group_id,
            "child_ids": self.child_ids.copy(),
            "metadata": self.metadata.copy(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> LayerGroup:
        """Create from dictionary"""
        return cls(**data)


class LayerManager:
    """
    Manages layers and groups for a tilemap.

    Provides:
    - Dynamic layer add/remove/reorder
    - Layer grouping/folders
    - Layer operations (merge, duplicate, etc.)
    - Backward compatibility with 3-layer maps
    """

    def __init__(self, width: int, height: int):
        """
        Initialize layer manager.

        Args:
            width: Map width in tiles
            height: Map height in tiles
        """
        self.width = width
        self.height = height

        # Storage
        self.layers: Dict[str, EnhancedTileLayer] = {}
        self.groups: Dict[str, LayerGroup] = {}

        # Root-level layer/group IDs (in render order, bottom to top)
        self.root_ids: List[str] = []

        # Version for backward compatibility
        self.version: int = 2  # Version 1 = old 3-layer, Version 2 = enhanced

    def create_layer(
        self,
        name: str = "New Layer",
        properties: Optional[LayerProperties] = None,
        parent_group_id: Optional[str] = None,
        insert_index: Optional[int] = None,
    ) -> EnhancedTileLayer:
        """
        Create and add a new layer.

        Args:
            name: Layer name
            properties: Layer properties (creates default if None)
            parent_group_id: Parent group ID (None for root)
            insert_index: Index to insert at (None for end)

        Returns:
            Created layer
        """
        if properties is None:
            properties = LayerProperties(name=name)
        else:
            properties.name = name

        layer = EnhancedTileLayer(
            width=self.width,
            height=self.height,
            properties=properties,
            parent_group_id=parent_group_id,
        )

        self.layers[properties.layer_id] = layer

        # Add to hierarchy
        if parent_group_id and parent_group_id in self.groups:
            self.groups[parent_group_id].add_child(properties.layer_id)
        else:
            if insert_index is None:
                self.root_ids.append(properties.layer_id)
            else:
                insert_index = max(0, min(insert_index, len(self.root_ids)))
                self.root_ids.insert(insert_index, properties.layer_id)

        return layer

    def create_group(
        self,
        name: str = "New Group",
        parent_group_id: Optional[str] = None,
        insert_index: Optional[int] = None,
    ) -> LayerGroup:
        """
        Create and add a new group.

        Args:
            name: Group name
            parent_group_id: Parent group ID (None for root)
            insert_index: Index to insert at (None for end)

        Returns:
            Created group
        """
        group = LayerGroup(name=name, parent_group_id=parent_group_id)
        self.groups[group.group_id] = group

        # Add to hierarchy
        if parent_group_id and parent_group_id in self.groups:
            self.groups[parent_group_id].add_child(group.group_id)
        else:
            if insert_index is None:
                self.root_ids.append(group.group_id)
            else:
                insert_index = max(0, min(insert_index, len(self.root_ids)))
                self.root_ids.insert(insert_index, group.group_id)

        return group

    def remove_layer(self, layer_id: str) -> bool:
        """
        Remove a layer.

        Args:
            layer_id: Layer ID to remove

        Returns:
            True if removed, False if not found
        """
        if layer_id not in self.layers:
            return False

        layer = self.layers[layer_id]

        # Remove from parent
        if layer.parent_group_id and layer.parent_group_id in self.groups:
            self.groups[layer.parent_group_id].remove_child(layer_id)
        elif layer_id in self.root_ids:
            self.root_ids.remove(layer_id)

        # Remove layer
        del self.layers[layer_id]
        return True

    def remove_group(self, group_id: str, remove_children: bool = False) -> bool:
        """
        Remove a group.

        Args:
            group_id: Group ID to remove
            remove_children: If True, remove all children; if False, move to parent

        Returns:
            True if removed, False if not found
        """
        if group_id not in self.groups:
            return False

        group = self.groups[group_id]

        # Handle children
        if remove_children:
            # Remove all children recursively
            for child_id in group.child_ids.copy():
                if child_id in self.layers:
                    self.remove_layer(child_id)
                elif child_id in self.groups:
                    self.remove_group(child_id, remove_children=True)
        else:
            # Move children to parent
            for child_id in group.child_ids:
                if child_id in self.layers:
                    self.layers[child_id].parent_group_id = group.parent_group_id
                elif child_id in self.groups:
                    self.groups[child_id].parent_group_id = group.parent_group_id

                # Add to parent's child list
                if group.parent_group_id and group.parent_group_id in self.groups:
                    self.groups[group.parent_group_id].add_child(child_id)
                else:
                    self.root_ids.append(child_id)

        # Remove from parent
        if group.parent_group_id and group.parent_group_id in self.groups:
            self.groups[group.parent_group_id].remove_child(group_id)
        elif group_id in self.root_ids:
            self.root_ids.remove(group_id)

        # Remove group
        del self.groups[group_id]
        return True

    def get_layer(self, layer_id: str) -> Optional[EnhancedTileLayer]:
        """Get layer by ID"""
        return self.layers.get(layer_id)

    def get_group(self, group_id: str) -> Optional[LayerGroup]:
        """Get group by ID"""
        return self.groups.get(group_id)

    def get_layer_by_name(self, name: str) -> Optional[EnhancedTileLayer]:
        """Get first layer with matching name"""
        for layer in self.layers.values():
            if layer.properties.name == name:
                return layer
        return None

    def reorder_layer(self, layer_id: str, new_index: int) -> bool:
        """
        Reorder a layer within its parent.

        Args:
            layer_id: Layer ID to reorder
            new_index: New index (0 = bottom, higher = top)

        Returns:
            True if reordered, False if not found
        """
        if layer_id not in self.layers:
            return False

        layer = self.layers[layer_id]

        if layer.parent_group_id and layer.parent_group_id in self.groups:
            self.groups[layer.parent_group_id].reorder_child(layer_id, new_index)
        elif layer_id in self.root_ids:
            self.root_ids.remove(layer_id)
            new_index = max(0, min(new_index, len(self.root_ids)))
            self.root_ids.insert(new_index, layer_id)

        return True

    def move_layer_to_group(self, layer_id: str, new_parent_group_id: Optional[str]) -> bool:
        """
        Move a layer to a different group.

        Args:
            layer_id: Layer ID to move
            new_parent_group_id: New parent group ID (None for root)

        Returns:
            True if moved, False if not found
        """
        if layer_id not in self.layers:
            return False

        layer = self.layers[layer_id]

        # Remove from old parent
        if layer.parent_group_id and layer.parent_group_id in self.groups:
            self.groups[layer.parent_group_id].remove_child(layer_id)
        elif layer_id in self.root_ids:
            self.root_ids.remove(layer_id)

        # Add to new parent
        layer.parent_group_id = new_parent_group_id
        if new_parent_group_id and new_parent_group_id in self.groups:
            self.groups[new_parent_group_id].add_child(layer_id)
        else:
            self.root_ids.append(layer_id)

        return True

    def duplicate_layer(self, layer_id: str, new_name: Optional[str] = None) -> Optional[str]:
        """
        Duplicate a layer.

        Args:
            layer_id: Layer ID to duplicate
            new_name: Name for duplicate (auto-generated if None)

        Returns:
            New layer ID, or None if source not found
        """
        if layer_id not in self.layers:
            return None

        source = self.layers[layer_id]

        # Create new properties
        new_props = LayerProperties(**source.properties.to_dict())
        new_props.layer_id = str(uuid4())
        if new_name:
            new_props.name = new_name
        else:
            new_props.name = f"{source.properties.name} Copy"

        # Create new layer
        new_layer = EnhancedTileLayer(
            width=source.width,
            height=source.height,
            tiles=[row.copy() for row in source.tiles],
            properties=new_props,
            parent_group_id=source.parent_group_id,
        )

        self.layers[new_props.layer_id] = new_layer

        # Add to hierarchy (after source)
        if source.parent_group_id and source.parent_group_id in self.groups:
            group = self.groups[source.parent_group_id]
            insert_idx = group.child_ids.index(layer_id) + 1
            group.child_ids.insert(insert_idx, new_props.layer_id)
        else:
            insert_idx = self.root_ids.index(layer_id) + 1
            self.root_ids.insert(insert_idx, new_props.layer_id)

        return new_props.layer_id

    def merge_layers(self, layer_ids: List[str], new_name: str = "Merged Layer") -> Optional[str]:
        """
        Merge multiple layers into one.

        Non-empty tiles from higher layers override lower layers.

        Args:
            layer_ids: Layer IDs to merge (bottom to top order)
            new_name: Name for merged layer

        Returns:
            New merged layer ID, or None if no valid layers
        """
        if not layer_ids:
            return None

        # Filter valid layers
        valid_layers = [self.layers[lid] for lid in layer_ids if lid in self.layers]
        if not valid_layers:
            return None

        # Create merged layer
        merged_props = LayerProperties(name=new_name)
        merged_layer = EnhancedTileLayer(
            width=self.width, height=self.height, properties=merged_props
        )

        # Merge tiles (bottom to top)
        for layer in valid_layers:
            for y in range(min(layer.height, self.height)):
                for x in range(min(layer.width, self.width)):
                    tile_id = layer.get_tile(x, y)
                    if tile_id != 0:  # Non-empty tile
                        merged_layer.set_tile(x, y, tile_id)

        # Add to manager
        self.layers[merged_props.layer_id] = merged_layer
        self.root_ids.append(merged_props.layer_id)

        return merged_props.layer_id

    def get_render_order(self) -> List[str]:
        """
        Get all layer IDs in render order (bottom to top).

        Respects group hierarchy and visibility.

        Returns:
            List of layer IDs in render order
        """
        result = []

        def traverse(item_ids: List[str]):
            for item_id in item_ids:
                if item_id in self.layers:
                    result.append(item_id)
                elif item_id in self.groups:
                    group = self.groups[item_id]
                    if group.visible:
                        traverse(group.child_ids)

        traverse(self.root_ids)
        return result

    def update(self, dt: float):
        """
        Update all layers (auto-scroll, etc.).

        Args:
            dt: Delta time in seconds
        """
        for layer in self.layers.values():
            layer.update_auto_scroll(dt)

    def resize_all_layers(self, new_width: int, new_height: int, fill_tile: int = 0):
        """
        Resize all layers to new dimensions.

        Args:
            new_width: New width in tiles
            new_height: New height in tiles
            fill_tile: Tile ID to use for new areas
        """
        for layer in self.layers.values():
            layer.resize(new_width, new_height, fill_tile)

        self.width = new_width
        self.height = new_height

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "version": self.version,
            "width": self.width,
            "height": self.height,
            "layers": {lid: layer.to_dict() for lid, layer in self.layers.items()},
            "groups": {gid: group.to_dict() for gid, group in self.groups.items()},
            "root_ids": self.root_ids.copy(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> LayerManager:
        """Create from dictionary"""
        version = data.get("version", 1)
        manager = cls(width=data["width"], height=data["height"])
        manager.version = version

        # Load layers
        for layer_data in data.get("layers", {}).values():
            layer = EnhancedTileLayer.from_dict(layer_data)
            manager.layers[layer.properties.layer_id] = layer

        # Load groups
        for group_data in data.get("groups", {}).values():
            group = LayerGroup.from_dict(group_data)
            manager.groups[group.group_id] = group

        # Load hierarchy
        manager.root_ids = data.get("root_ids", [])

        return manager

    @classmethod
    def from_legacy_layers(
        cls, width: int, height: int, layer_data: List[List[List[int]]]
    ) -> LayerManager:
        """
        Create from legacy 3-layer format.

        Args:
            width: Map width in tiles
            height: Map height in tiles
            layer_data: List of 3 tile arrays (ground, objects, overlay)

        Returns:
            LayerManager with converted layers
        """
        manager = cls(width, height)
        manager.version = 1  # Mark as converted from legacy

        layer_names = ["Ground", "Objects", "Overlay"]

        for i, tiles in enumerate(layer_data[:3]):  # Max 3 layers
            props = LayerProperties(name=layer_names[i])
            layer = EnhancedTileLayer(width=width, height=height, tiles=tiles, properties=props)
            manager.layers[props.layer_id] = layer
            manager.root_ids.append(props.layer_id)

        return manager
