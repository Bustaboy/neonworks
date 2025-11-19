"""
Tilemap System

Grid-based level rendering with multiple layers, tilesets, and efficient culling.

This module provides backward compatibility with the old 3-layer system while
supporting the new enhanced layer system from data.map_layers.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

import pygame

from neonworks.core.ecs import Component
from neonworks.data.map_layers import (
    EnhancedTileLayer,
    LayerManager,
    LayerProperties,
    LayerType,
    ParallaxMode,
)
from neonworks.rendering.assets import AssetManager
from neonworks.rendering.camera import Camera


@dataclass
class Tile:
    """Represents a single tile in the tilemap"""

    tile_id: int = 0  # ID in the tileset (0 = empty)
    flags: int = 0  # Flip/rotation flags

    # Tile flags
    FLIP_HORIZONTAL = 0x01
    FLIP_VERTICAL = 0x02
    FLIP_DIAGONAL = 0x04  # 90-degree rotation

    def is_empty(self) -> bool:
        """Check if tile is empty"""
        return self.tile_id == 0

    def is_flipped_horizontal(self) -> bool:
        return (self.flags & self.FLIP_HORIZONTAL) != 0

    def is_flipped_vertical(self) -> bool:
        return (self.flags & self.FLIP_VERTICAL) != 0

    def is_flipped_diagonal(self) -> bool:
        return (self.flags & self.FLIP_DIAGONAL) != 0


@dataclass
class Tileset:
    """Tileset loaded from a sprite sheet"""

    name: str
    texture_path: str
    tile_width: int
    tile_height: int
    columns: int
    tile_count: int
    spacing: int = 0  # Space between tiles
    margin: int = 0  # Margin around tileset

    # Loaded sprites (tile_id -> pygame.Surface)
    tiles: Dict[int, pygame.Surface] = field(default_factory=dict)

    def get_tile_rect(self, tile_id: int) -> Tuple[int, int, int, int]:
        """Get source rectangle for a tile in the tileset"""
        if tile_id < 0 or tile_id >= self.tile_count:
            return (0, 0, 0, 0)

        col = tile_id % self.columns
        row = tile_id // self.columns

        x = self.margin + col * (self.tile_width + self.spacing)
        y = self.margin + row * (self.tile_height + self.spacing)

        return (x, y, self.tile_width, self.tile_height)

    def load_tiles(self, asset_manager: AssetManager):
        """Load all tiles from the tileset"""
        # Load the tileset image
        tileset_surface = asset_manager.load_sprite(self.texture_path)
        if not tileset_surface:
            return

        # Extract individual tiles
        for tile_id in range(self.tile_count):
            x, y, w, h = self.get_tile_rect(tile_id)
            tile_surface = pygame.Surface((w, h), pygame.SRCALPHA)
            tile_surface.blit(tileset_surface, (0, 0), (x, y, w, h))
            self.tiles[tile_id] = tile_surface


@dataclass
class TileLayer:
    """A single layer in the tilemap"""

    name: str
    width: int  # Width in tiles
    height: int  # Height in tiles
    tiles: List[List[Tile]] = field(default_factory=list)
    visible: bool = True
    opacity: float = 1.0
    offset_x: float = 0.0
    offset_y: float = 0.0
    parallax_x: float = 1.0  # Parallax scrolling multiplier
    parallax_y: float = 1.0

    def __post_init__(self):
        if not self.tiles:
            # Initialize empty tile grid
            self.tiles = [[Tile() for _ in range(self.width)] for _ in range(self.height)]

    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        """Get tile at grid position"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None

    def set_tile(self, x: int, y: int, tile: Tile):
        """Set tile at grid position"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[y][x] = tile

    def fill(self, tile_id: int):
        """Fill entire layer with a tile"""
        for y in range(self.height):
            for x in range(self.width):
                self.tiles[y][x] = Tile(tile_id=tile_id)

    def clear(self):
        """Clear layer (fill with empty tiles)"""
        self.fill(0)


class Tilemap(Component):
    """
    Tilemap component for grid-based levels.

    Supports multiple layers, tilesets, and efficient rendering.

    Now uses the enhanced LayerManager for advanced layer features while
    maintaining backward compatibility with the old 3-layer system.
    """

    def __init__(
        self,
        width: int,
        height: int,
        tile_width: Optional[int] = None,
        tile_height: Optional[int] = None,
        use_enhanced_layers: bool = True,
        tile_size: Optional[int] = None,
        layers: Optional[int] = None,
    ):
        """
        Create a new tilemap.

        Args:
            width: Width in tiles
            height: Height in tiles
            tile_width: Width of each tile in pixels
            tile_height: Height of each tile in pixels
            use_enhanced_layers: Use new LayerManager (recommended)
            tile_size: Optional uniform tile size (overrides tile_width/tile_height)
            layers: Optional backward-compatible layer count (ignored when using enhanced layers)
        """
        self.width = width
        self.height = height
        # Provide flexible sizing for legacy callers
        if tile_size is not None:
            tile_width = tile_width or tile_size
            tile_height = tile_height or tile_size
        self.tile_width = tile_width or 32
        self.tile_height = tile_height or 32

        # Backward compatibility: older code passed a layer count; the enhanced
        # LayerManager manages layers internally, so we accept and ignore.
        self.legacy_layer_count = layers

        # Layer system selection
        self.use_enhanced_layers = use_enhanced_layers

        if use_enhanced_layers:
            # NEW: Enhanced layer system
            self.layer_manager = LayerManager(width, height)
        else:
            # OLD: Legacy layer system (for backward compatibility)
            self.layers: List[TileLayer] = []

        # Tilesets
        self.tilesets: Dict[str, Tileset] = {}
        self.default_tileset: Optional[str] = None

        # Rendering cache
        self._render_cache_dirty = True

    # ===================================================================
    # Enhanced Layer System API (NEW)
    # ===================================================================

    def create_enhanced_layer(
        self,
        name: str = "New Layer",
        layer_type: LayerType = LayerType.STANDARD,
        parallax_x: float = 1.0,
        parallax_y: float = 1.0,
        opacity: float = 1.0,
        parent_group_id: Optional[str] = None,
    ) -> Optional[str]:
        """
        Create a new enhanced layer.

        Args:
            name: Layer name
            layer_type: Type of layer
            parallax_x: Horizontal parallax multiplier
            parallax_y: Vertical parallax multiplier
            opacity: Layer opacity (0.0 to 1.0)
            parent_group_id: Parent group ID (None for root)

        Returns:
            Layer ID, or None if not using enhanced layers
        """
        if not self.use_enhanced_layers:
            return None

        props = LayerProperties(
            name=name,
            layer_type=layer_type,
            parallax_x=parallax_x,
            parallax_y=parallax_y,
            opacity=opacity,
        )

        layer = self.layer_manager.create_layer(
            name=name, properties=props, parent_group_id=parent_group_id
        )

        self._render_cache_dirty = True
        return layer.properties.layer_id

    def create_parallax_background(
        self,
        name: str,
        parallax_x: float = 0.5,
        parallax_y: float = 0.5,
        auto_scroll_x: float = 0.0,
        auto_scroll_y: float = 0.0,
    ) -> Optional[str]:
        """
        Create a parallax background layer.

        Args:
            name: Layer name
            parallax_x: Horizontal parallax (< 1.0 for background effect)
            parallax_y: Vertical parallax (< 1.0 for background effect)
            auto_scroll_x: Auto-scroll speed X (pixels/second)
            auto_scroll_y: Auto-scroll speed Y (pixels/second)

        Returns:
            Layer ID, or None if not using enhanced layers
        """
        if not self.use_enhanced_layers:
            return None

        props = LayerProperties(
            name=name,
            layer_type=LayerType.PARALLAX_BACKGROUND,
            parallax_mode=(
                ParallaxMode.AUTO_SCROLL if auto_scroll_x or auto_scroll_y else ParallaxMode.MANUAL
            ),
            parallax_x=parallax_x,
            parallax_y=parallax_y,
            auto_scroll_x=auto_scroll_x,
            auto_scroll_y=auto_scroll_y,
        )

        layer = self.layer_manager.create_layer(name=name, properties=props)
        self._render_cache_dirty = True
        return layer.properties.layer_id

    def remove_layer(self, layer_id: str) -> bool:
        """
        Remove a layer by ID.

        Args:
            layer_id: Layer ID to remove

        Returns:
            True if removed, False otherwise
        """
        if not self.use_enhanced_layers:
            return False

        result = self.layer_manager.remove_layer(layer_id)
        if result:
            self._render_cache_dirty = True
        return result

    def reorder_layer(self, layer_id: str, new_index: int) -> bool:
        """
        Reorder a layer.

        Args:
            layer_id: Layer ID to reorder
            new_index: New index (0 = bottom)

        Returns:
            True if reordered, False otherwise
        """
        if not self.use_enhanced_layers:
            return False

        result = self.layer_manager.reorder_layer(layer_id, new_index)
        if result:
            self._render_cache_dirty = True
        return result

    def duplicate_layer(self, layer_id: str, new_name: Optional[str] = None) -> Optional[str]:
        """
        Duplicate a layer.

        Args:
            layer_id: Layer ID to duplicate
            new_name: Name for duplicate (auto-generated if None)

        Returns:
            New layer ID, or None if failed
        """
        if not self.use_enhanced_layers:
            return None

        new_id = self.layer_manager.duplicate_layer(layer_id, new_name)
        if new_id:
            self._render_cache_dirty = True
        return new_id

    def merge_layers(self, layer_ids: List[str], new_name: str = "Merged Layer") -> Optional[str]:
        """
        Merge multiple layers into one.

        Args:
            layer_ids: Layer IDs to merge (bottom to top order)
            new_name: Name for merged layer

        Returns:
            New merged layer ID, or None if failed
        """
        if not self.use_enhanced_layers:
            return None

        new_id = self.layer_manager.merge_layers(layer_ids, new_name)
        if new_id:
            self._render_cache_dirty = True
        return new_id

    def create_layer_group(
        self, name: str = "New Group", parent_group_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a layer group/folder.

        Args:
            name: Group name
            parent_group_id: Parent group ID (None for root)

        Returns:
            Group ID, or None if not using enhanced layers
        """
        if not self.use_enhanced_layers:
            return None

        group = self.layer_manager.create_group(name=name, parent_group_id=parent_group_id)
        return group.group_id

    def get_enhanced_layer(self, layer_id: str) -> Optional[EnhancedTileLayer]:
        """Get enhanced layer by ID"""
        if not self.use_enhanced_layers:
            return None
        return self.layer_manager.get_layer(layer_id)

    def get_enhanced_layer_by_name(self, name: str) -> Optional[EnhancedTileLayer]:
        """Get enhanced layer by name"""
        if not self.use_enhanced_layers:
            return None
        return self.layer_manager.get_layer_by_name(name)

    # ===================================================================
    # Legacy Layer System API (for backward compatibility)
    # ===================================================================

    def add_layer(self, layer: TileLayer) -> int:
        """Add a legacy layer and return its index"""
        if self.use_enhanced_layers:
            # Convert to enhanced layer
            props = LayerProperties(
                name=layer.name,
                visible=layer.visible,
                opacity=layer.opacity,
                offset_x=layer.offset_x,
                offset_y=layer.offset_y,
                parallax_x=layer.parallax_x,
                parallax_y=layer.parallax_y,
            )

            # Convert tiles to ID array
            tiles = [[tile.tile_id for tile in row] for row in layer.tiles]

            enhanced = EnhancedTileLayer(
                width=layer.width, height=layer.height, tiles=tiles, properties=props
            )

            self.layer_manager.layers[props.layer_id] = enhanced
            self.layer_manager.root_ids.append(props.layer_id)
            self._render_cache_dirty = True
            return len(self.layer_manager.root_ids) - 1
        else:
            self.layers.append(layer)
            self._render_cache_dirty = True
            return len(self.layers) - 1

    def create_layer(self, name: str, fill_tile: int = 0) -> int:
        """Create and add a new legacy layer"""
        layer = TileLayer(name=name, width=self.width, height=self.height)
        if fill_tile != 0:
            layer.fill(fill_tile)
        return self.add_layer(layer)

    def get_layer(self, index: int) -> Optional[TileLayer]:
        """Get legacy layer by index"""
        if self.use_enhanced_layers:
            # Convert enhanced layer to legacy
            render_order = self.layer_manager.get_render_order()
            if 0 <= index < len(render_order):
                layer_id = render_order[index]
                enhanced = self.layer_manager.get_layer(layer_id)
                if enhanced:
                    return self._enhanced_to_legacy(enhanced)
            return None
        else:
            if 0 <= index < len(self.layers):
                return self.layers[index]
            return None

    def get_layer_by_name(self, name: str) -> Optional[TileLayer]:
        """Get legacy layer by name"""
        if self.use_enhanced_layers:
            enhanced = self.layer_manager.get_layer_by_name(name)
            if enhanced:
                return self._enhanced_to_legacy(enhanced)
            return None
        else:
            for layer in self.layers:
                if layer.name == name:
                    return layer
            return None

    def _enhanced_to_legacy(self, enhanced: EnhancedTileLayer) -> TileLayer:
        """Convert enhanced layer to legacy TileLayer"""
        # Convert tile IDs to Tile objects
        tiles = [[Tile(tile_id=tid) for tid in row] for row in enhanced.tiles]

        return TileLayer(
            name=enhanced.properties.name,
            width=enhanced.width,
            height=enhanced.height,
            tiles=tiles,
            visible=enhanced.properties.visible,
            opacity=enhanced.properties.opacity,
            offset_x=enhanced.properties.offset_x,
            offset_y=enhanced.properties.offset_y,
            parallax_x=enhanced.properties.parallax_x,
            parallax_y=enhanced.properties.parallax_y,
        )

    # ===================================================================
    # Common API
    # ===================================================================

    def update(self, dt: float):
        """Update tilemap (auto-scroll layers, etc.)"""
        if self.use_enhanced_layers:
            self.layer_manager.update(dt)

    def add_tileset(self, tileset: Tileset):
        """Add a tileset"""
        self.tilesets[tileset.name] = tileset
        if self.default_tileset is None:
            self.default_tileset = tileset.name
        self._render_cache_dirty = True

    def get_tileset(self, name: Optional[str] = None) -> Optional[Tileset]:
        """Get tileset by name (or default if None)"""
        if name is None:
            name = self.default_tileset
        return self.tilesets.get(name) if name else None

    def world_to_tile(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """Convert world coordinates to tile coordinates"""
        tile_x = int(world_x // self.tile_width)
        tile_y = int(world_y // self.tile_height)
        return (tile_x, tile_y)

    def tile_to_world(self, tile_x: int, tile_y: int) -> Tuple[float, float]:
        """Convert tile coordinates to world coordinates (tile center)"""
        world_x = tile_x * self.tile_width + self.tile_width / 2
        world_y = tile_y * self.tile_height + self.tile_height / 2
        return (world_x, world_y)

    def is_valid_tile(self, tile_x: int, tile_y: int) -> bool:
        """Check if tile coordinates are valid"""
        return 0 <= tile_x < self.width and 0 <= tile_y < self.height


class TilemapRenderer:
    """
    Renders tilemaps efficiently with camera culling.

    Supports both legacy and enhanced layer systems.
    """

    def __init__(self, asset_manager: AssetManager):
        self.asset_manager = asset_manager
        self._stats = {"tiles_rendered": 0, "tiles_culled": 0, "layers_rendered": 0}

    def render(self, screen: pygame.Surface, tilemap: Tilemap, camera: Camera):
        """
        Render a tilemap to the screen.

        Args:
            screen: Surface to render to
            tilemap: Tilemap to render
            camera: Camera for culling and positioning
        """
        self._stats["tiles_rendered"] = 0
        self._stats["tiles_culled"] = 0
        self._stats["layers_rendered"] = 0

        # Get default tileset
        tileset = tilemap.get_tileset()
        if not tileset:
            return

        # Load tileset if not already loaded
        if not tileset.tiles:
            tileset.load_tiles(self.asset_manager)

        # Route to appropriate renderer
        if tilemap.use_enhanced_layers:
            self._render_enhanced(screen, tilemap, camera, tileset)
        else:
            self._render_legacy(screen, tilemap, camera, tileset)

    def _render_enhanced(
        self, screen: pygame.Surface, tilemap: Tilemap, camera: Camera, tileset: Tileset
    ):
        """Render using enhanced layer system"""
        # Get layers in render order
        layer_ids = tilemap.layer_manager.get_render_order()

        for layer_id in layer_ids:
            layer = tilemap.layer_manager.get_layer(layer_id)
            if not layer:
                continue

            # Skip invisible or locked collision layers
            if not layer.properties.visible:
                continue

            if layer.properties.layer_type == LayerType.COLLISION:
                continue  # Collision layers not rendered

            # Get effective offsets (including auto-scroll)
            offset_x, offset_y = layer.get_effective_offset()

            # Render the layer
            self._render_layer_enhanced(screen, tilemap, camera, tileset, layer, offset_x, offset_y)

            self._stats["layers_rendered"] += 1

    def _render_layer_enhanced(
        self,
        screen: pygame.Surface,
        tilemap: Tilemap,
        camera: Camera,
        tileset: Tileset,
        layer: EnhancedTileLayer,
        offset_x: float,
        offset_y: float,
    ):
        """Render a single enhanced layer"""
        # Calculate visible tile range
        camera_left = camera.x - camera.width / 2
        camera_top = camera.y - camera.height / 2

        # Apply parallax
        layer_camera_left = camera_left * layer.properties.parallax_x + offset_x
        layer_camera_top = camera_top * layer.properties.parallax_y + offset_y

        # Calculate tile range to render (with 1-tile buffer)
        start_tile_x = max(0, int(layer_camera_left / tilemap.tile_width) - 1)
        start_tile_y = max(0, int(layer_camera_top / tilemap.tile_height) - 1)
        end_tile_x = min(
            layer.width,
            int((layer_camera_left + camera.width) / tilemap.tile_width) + 2,
        )
        end_tile_y = min(
            layer.height,
            int((layer_camera_top + camera.height) / tilemap.tile_height) + 2,
        )

        # Render visible tiles
        for tile_y in range(start_tile_y, end_tile_y):
            for tile_x in range(start_tile_x, end_tile_x):
                tile_id = layer.get_tile(tile_x, tile_y)
                if tile_id == 0:  # Empty tile
                    self._stats["tiles_culled"] += 1
                    continue

                # Get tile sprite
                tile_surface = tileset.tiles.get(tile_id)
                if not tile_surface:
                    self._stats["tiles_culled"] += 1
                    continue

                # Calculate world position
                world_x = tile_x * tilemap.tile_width
                world_y = tile_y * tilemap.tile_height

                # Apply layer offset
                world_x = world_x - offset_x
                world_y = world_y - offset_y

                # Convert to screen coordinates
                screen_x, screen_y = camera.world_to_screen(world_x, world_y)

                # Apply layer opacity
                render_surface = tile_surface
                if layer.properties.opacity < 1.0:
                    render_surface = tile_surface.copy()
                    render_surface.set_alpha(int(layer.properties.opacity * 255))

                # Render tile
                screen.blit(render_surface, (screen_x, screen_y))
                self._stats["tiles_rendered"] += 1

    def _render_legacy(
        self, screen: pygame.Surface, tilemap: Tilemap, camera: Camera, tileset: Tileset
    ):
        """Render using legacy layer system"""
        camera_left = camera.x - camera.width / 2
        camera_top = camera.y - camera.height / 2

        # Render each layer
        for layer in tilemap.layers:
            if not layer.visible:
                continue

            # Apply parallax
            layer_camera_left = camera_left * layer.parallax_x + layer.offset_x
            layer_camera_top = camera_top * layer.parallax_y + layer.offset_y

            # Calculate tile range to render (with 1-tile buffer)
            start_tile_x = max(0, int(layer_camera_left / tilemap.tile_width) - 1)
            start_tile_y = max(0, int(layer_camera_top / tilemap.tile_height) - 1)
            end_tile_x = min(
                tilemap.width,
                int((layer_camera_left + camera.width) / tilemap.tile_width) + 2,
            )
            end_tile_y = min(
                tilemap.height,
                int((layer_camera_top + camera.height) / tilemap.tile_height) + 2,
            )

            # Render visible tiles
            for tile_y in range(start_tile_y, end_tile_y):
                for tile_x in range(start_tile_x, end_tile_x):
                    tile = layer.get_tile(tile_x, tile_y)
                    if not tile or tile.is_empty():
                        self._stats["tiles_culled"] += 1
                        continue

                    # Get tile sprite
                    tile_surface = tileset.tiles.get(tile.tile_id)
                    if not tile_surface:
                        self._stats["tiles_culled"] += 1
                        continue

                    # Calculate world position
                    world_x = tile_x * tilemap.tile_width
                    world_y = tile_y * tilemap.tile_height

                    # Apply parallax offset
                    world_x = world_x - layer.offset_x
                    world_y = world_y - layer.offset_y

                    # Convert to screen coordinates
                    screen_x, screen_y = camera.world_to_screen(world_x, world_y)

                    # Apply tile transformations
                    render_surface = tile_surface
                    if tile.flags != 0:
                        render_surface = self._apply_tile_transforms(tile_surface, tile)

                    # Apply layer opacity
                    if layer.opacity < 1.0:
                        render_surface = render_surface.copy()
                        render_surface.set_alpha(int(layer.opacity * 255))

                    # Render tile
                    screen.blit(render_surface, (screen_x, screen_y))
                    self._stats["tiles_rendered"] += 1

            self._stats["layers_rendered"] += 1

    def _apply_tile_transforms(self, surface: pygame.Surface, tile: Tile) -> pygame.Surface:
        """Apply flip/rotation transformations to a tile"""
        result = surface

        if tile.is_flipped_horizontal():
            result = pygame.transform.flip(result, True, False)

        if tile.is_flipped_vertical():
            result = pygame.transform.flip(result, False, True)

        if tile.is_flipped_diagonal():
            result = pygame.transform.rotate(result, 90)

        return result

    def get_stats(self) -> Dict[str, int]:
        """Get rendering statistics"""
        return self._stats.copy()


class OptimizedTilemapRenderer(TilemapRenderer):
    """
    Optimized tilemap renderer with advanced performance features.

    Features:
    - Chunk-based rendering (only visible chunks)
    - Layer texture caching (pre-rendered chunks)
    - Dirty rectangle optimization (only re-render changed areas)
    - Tile texture atlas for batch rendering
    - Improved frustum culling

    Designed for high-performance rendering of large maps (500x500+).
    """

    # Chunk configuration
    CHUNK_SIZE = 16  # 16x16 tiles per chunk

    def __init__(self, asset_manager: AssetManager, enable_caching: bool = True):
        """
        Initialize optimized renderer.

        Args:
            asset_manager: Asset manager for loading textures
            enable_caching: Enable chunk caching (recommended)
        """
        super().__init__(asset_manager)

        # Caching configuration
        self.enable_caching = enable_caching

        # Chunk cache: {(layer_id, chunk_x, chunk_y): pygame.Surface}
        self._chunk_cache: Dict[Tuple[str, int, int], pygame.Surface] = {}

        # Dirty chunks: {(layer_id, chunk_x, chunk_y)}
        self._dirty_chunks: Set[Tuple[str, int, int]] = set()

        # Texture atlas cache for batch rendering
        self._atlas_cache: Dict[str, pygame.Surface] = {}

        # Previous camera position for dirty detection
        self._prev_camera_x = 0.0
        self._prev_camera_y = 0.0
        self._prev_camera_zoom = 1.0

        # Enhanced statistics
        self._stats.update(
            {
                "chunks_rendered": 0,
                "chunks_cached": 0,
                "chunks_reused": 0,
                "cache_hits": 0,
                "cache_misses": 0,
            }
        )

    def invalidate_chunk(self, layer_id: str, chunk_x: int, chunk_y: int):
        """
        Mark a chunk as dirty (needs re-rendering).

        Args:
            layer_id: Layer ID
            chunk_x: Chunk X coordinate
            chunk_y: Chunk Y coordinate
        """
        chunk_key = (layer_id, chunk_x, chunk_y)
        self._dirty_chunks.add(chunk_key)

        # Remove from cache
        if chunk_key in self._chunk_cache:
            del self._chunk_cache[chunk_key]

    def invalidate_tile(self, layer_id: str, tile_x: int, tile_y: int):
        """
        Mark the chunk containing a tile as dirty.

        Args:
            layer_id: Layer ID
            tile_x: Tile X coordinate
            tile_y: Tile Y coordinate
        """
        chunk_x = tile_x // self.CHUNK_SIZE
        chunk_y = tile_y // self.CHUNK_SIZE
        self.invalidate_chunk(layer_id, chunk_x, chunk_y)

    def invalidate_layer(self, layer_id: str):
        """
        Invalidate all chunks in a layer.

        Args:
            layer_id: Layer ID
        """
        # Remove all chunks for this layer from cache
        keys_to_remove = [key for key in self._chunk_cache if key[0] == layer_id]
        for key in keys_to_remove:
            del self._chunk_cache[key]
            self._dirty_chunks.discard(key)

    def clear_cache(self):
        """Clear all cached chunks."""
        self._chunk_cache.clear()
        self._dirty_chunks.clear()
        self._atlas_cache.clear()

    def render(self, screen: pygame.Surface, tilemap: Tilemap, camera: Camera):
        """
        Render tilemap with optimizations.

        Args:
            screen: Surface to render to
            tilemap: Tilemap to render
            camera: Camera for culling and positioning
        """
        # Reset stats
        self._stats["tiles_rendered"] = 0
        self._stats["tiles_culled"] = 0
        self._stats["layers_rendered"] = 0
        self._stats["chunks_rendered"] = 0
        self._stats["chunks_cached"] = 0
        self._stats["chunks_reused"] = 0
        self._stats["cache_hits"] = 0
        self._stats["cache_misses"] = 0

        # Get default tileset
        tileset = tilemap.get_tileset()
        if not tileset:
            return

        # Load tileset if not already loaded
        if not tileset.tiles:
            tileset.load_tiles(self.asset_manager)

        # Create texture atlas if needed
        if self.enable_caching and tileset.name not in self._atlas_cache:
            self._create_texture_atlas(tileset)

        # Route to appropriate renderer
        if tilemap.use_enhanced_layers:
            self._render_enhanced_optimized(screen, tilemap, camera, tileset)
        else:
            self._render_legacy_optimized(screen, tilemap, camera, tileset)

        # Update previous camera state
        self._prev_camera_x = camera.x
        self._prev_camera_y = camera.y
        self._prev_camera_zoom = camera.zoom

    def _create_texture_atlas(self, tileset: Tileset):
        """
        Create a texture atlas from tileset for batch rendering.

        Args:
            tileset: Tileset to create atlas from
        """
        if not tileset.tiles:
            return

        # Calculate atlas size (power of 2 for efficiency)
        tiles_per_row = tileset.columns
        tiles_per_col = (tileset.tile_count + tiles_per_row - 1) // tiles_per_row

        atlas_width = tiles_per_row * tileset.tile_width
        atlas_height = tiles_per_col * tileset.tile_height

        # Create atlas surface
        atlas = pygame.Surface((atlas_width, atlas_height), pygame.SRCALPHA)

        # Blit all tiles into atlas
        for tile_id, tile_surface in tileset.tiles.items():
            col = tile_id % tiles_per_row
            row = tile_id // tiles_per_row
            x = col * tileset.tile_width
            y = row * tileset.tile_height
            atlas.blit(tile_surface, (x, y))

        self._atlas_cache[tileset.name] = atlas

    def _render_enhanced_optimized(
        self, screen: pygame.Surface, tilemap: Tilemap, camera: Camera, tileset: Tileset
    ):
        """Render using enhanced layer system with optimizations"""
        # Get layers in render order
        layer_ids = tilemap.layer_manager.get_render_order()

        for layer_id in layer_ids:
            layer = tilemap.layer_manager.get_layer(layer_id)
            if not layer:
                continue

            # Skip invisible or collision layers
            if not layer.properties.visible:
                continue

            if layer.properties.layer_type == LayerType.COLLISION:
                continue

            # Get effective offsets
            offset_x, offset_y = layer.get_effective_offset()

            # Render layer with chunk-based optimization
            self._render_layer_chunked(
                screen, tilemap, camera, tileset, layer, layer_id, offset_x, offset_y
            )

            self._stats["layers_rendered"] += 1

    def _render_layer_chunked(
        self,
        screen: pygame.Surface,
        tilemap: Tilemap,
        camera: Camera,
        tileset: Tileset,
        layer: EnhancedTileLayer,
        layer_id: str,
        offset_x: float,
        offset_y: float,
    ):
        """
        Render a layer using chunk-based optimization.

        Args:
            screen: Surface to render to
            tilemap: Tilemap being rendered
            camera: Camera for culling
            tileset: Tileset for tiles
            layer: Layer to render
            layer_id: Layer ID for caching
            offset_x: Layer X offset
            offset_y: Layer Y offset
        """
        # Calculate visible tile range (frustum culling)
        camera_left = camera.x - camera.width / 2
        camera_top = camera.y - camera.height / 2

        # Apply parallax
        layer_camera_left = camera_left * layer.properties.parallax_x + offset_x
        layer_camera_top = camera_top * layer.properties.parallax_y + offset_y

        # Calculate visible chunk range
        start_chunk_x = max(0, int(layer_camera_left / (tilemap.tile_width * self.CHUNK_SIZE)))
        start_chunk_y = max(0, int(layer_camera_top / (tilemap.tile_height * self.CHUNK_SIZE)))

        end_chunk_x = min(
            (layer.width + self.CHUNK_SIZE - 1) // self.CHUNK_SIZE,
            int((layer_camera_left + camera.width) / (tilemap.tile_width * self.CHUNK_SIZE)) + 1,
        )
        end_chunk_y = min(
            (layer.height + self.CHUNK_SIZE - 1) // self.CHUNK_SIZE,
            int((layer_camera_top + camera.height) / (tilemap.tile_height * self.CHUNK_SIZE)) + 1,
        )

        # Render visible chunks
        for chunk_y in range(start_chunk_y, end_chunk_y):
            for chunk_x in range(start_chunk_x, end_chunk_x):
                self._render_chunk(
                    screen,
                    tilemap,
                    camera,
                    tileset,
                    layer,
                    layer_id,
                    chunk_x,
                    chunk_y,
                    offset_x,
                    offset_y,
                )

    def _render_chunk(
        self,
        screen: pygame.Surface,
        tilemap: Tilemap,
        camera: Camera,
        tileset: Tileset,
        layer: EnhancedTileLayer,
        layer_id: str,
        chunk_x: int,
        chunk_y: int,
        offset_x: float,
        offset_y: float,
    ):
        """
        Render a single chunk with caching.

        Args:
            screen: Surface to render to
            tilemap: Tilemap being rendered
            camera: Camera for positioning
            tileset: Tileset for tiles
            layer: Layer being rendered
            layer_id: Layer ID for caching
            chunk_x: Chunk X coordinate
            chunk_y: Chunk Y coordinate
            offset_x: Layer X offset
            offset_y: Layer Y offset
        """
        chunk_key = (layer_id, chunk_x, chunk_y)

        # Check cache
        if self.enable_caching and chunk_key in self._chunk_cache:
            chunk_surface = self._chunk_cache[chunk_key]
            self._stats["cache_hits"] += 1
            self._stats["chunks_reused"] += 1
        else:
            # Render chunk to surface
            chunk_surface = self._render_chunk_to_surface(tilemap, tileset, layer, chunk_x, chunk_y)

            if chunk_surface is None:
                return  # Empty chunk

            # Cache the chunk
            if self.enable_caching:
                self._chunk_cache[chunk_key] = chunk_surface
                self._stats["chunks_cached"] += 1

            self._stats["cache_misses"] += 1

        # Calculate chunk world position
        chunk_world_x = chunk_x * self.CHUNK_SIZE * tilemap.tile_width - offset_x
        chunk_world_y = chunk_y * self.CHUNK_SIZE * tilemap.tile_height - offset_y

        # Convert to screen coordinates
        screen_x, screen_y = camera.world_to_screen(chunk_world_x, chunk_world_y)

        # Apply layer opacity if needed
        if layer.properties.opacity < 1.0:
            render_surface = chunk_surface.copy()
            render_surface.set_alpha(int(layer.properties.opacity * 255))
            screen.blit(render_surface, (screen_x, screen_y))
        else:
            screen.blit(chunk_surface, (screen_x, screen_y))

        self._stats["chunks_rendered"] += 1

    def _render_chunk_to_surface(
        self,
        tilemap: Tilemap,
        tileset: Tileset,
        layer: EnhancedTileLayer,
        chunk_x: int,
        chunk_y: int,
    ) -> Optional[pygame.Surface]:
        """
        Render a chunk to a surface for caching.

        Args:
            tilemap: Tilemap being rendered
            tileset: Tileset for tiles
            layer: Layer being rendered
            chunk_x: Chunk X coordinate
            chunk_y: Chunk Y coordinate

        Returns:
            Rendered chunk surface, or None if empty
        """
        # Calculate tile range for this chunk
        start_tile_x = chunk_x * self.CHUNK_SIZE
        start_tile_y = chunk_y * self.CHUNK_SIZE
        end_tile_x = min(start_tile_x + self.CHUNK_SIZE, layer.width)
        end_tile_y = min(start_tile_y + self.CHUNK_SIZE, layer.height)

        # Calculate chunk size in pixels
        chunk_pixel_width = (end_tile_x - start_tile_x) * tilemap.tile_width
        chunk_pixel_height = (end_tile_y - start_tile_y) * tilemap.tile_height

        # Check if chunk has any non-empty tiles
        has_tiles = False
        for tile_y in range(start_tile_y, end_tile_y):
            for tile_x in range(start_tile_x, end_tile_x):
                if layer.get_tile(tile_x, tile_y) != 0:
                    has_tiles = True
                    break
            if has_tiles:
                break

        if not has_tiles:
            self._stats["tiles_culled"] += (end_tile_x - start_tile_x) * (end_tile_y - start_tile_y)
            return None

        # Create chunk surface
        chunk_surface = pygame.Surface((chunk_pixel_width, chunk_pixel_height), pygame.SRCALPHA)

        # Render tiles to chunk surface
        for tile_y in range(start_tile_y, end_tile_y):
            for tile_x in range(start_tile_x, end_tile_x):
                tile_id = layer.get_tile(tile_x, tile_y)

                if tile_id == 0:  # Empty tile
                    self._stats["tiles_culled"] += 1
                    continue

                # Get tile surface
                tile_surface = tileset.tiles.get(tile_id)
                if not tile_surface:
                    self._stats["tiles_culled"] += 1
                    continue

                # Calculate position within chunk
                local_x = (tile_x - start_tile_x) * tilemap.tile_width
                local_y = (tile_y - start_tile_y) * tilemap.tile_height

                # Blit tile to chunk
                chunk_surface.blit(tile_surface, (local_x, local_y))
                self._stats["tiles_rendered"] += 1

        return chunk_surface

    def _render_legacy_optimized(
        self, screen: pygame.Surface, tilemap: Tilemap, camera: Camera, tileset: Tileset
    ):
        """Render using legacy layer system with optimizations"""
        camera_left = camera.x - camera.width / 2
        camera_top = camera.y - camera.height / 2

        # Render each layer
        for idx, layer in enumerate(tilemap.layers):
            if not layer.visible:
                continue

            # Generate layer ID for caching
            layer_id = f"legacy_{idx}_{layer.name}"

            # Apply parallax
            layer_camera_left = camera_left * layer.parallax_x + layer.offset_x
            layer_camera_top = camera_top * layer.parallax_y + layer.offset_y

            # Calculate visible chunk range
            start_chunk_x = max(0, int(layer_camera_left / (tilemap.tile_width * self.CHUNK_SIZE)))
            start_chunk_y = max(0, int(layer_camera_top / (tilemap.tile_height * self.CHUNK_SIZE)))

            end_chunk_x = min(
                (tilemap.width + self.CHUNK_SIZE - 1) // self.CHUNK_SIZE,
                int((layer_camera_left + camera.width) / (tilemap.tile_width * self.CHUNK_SIZE))
                + 1,
            )
            end_chunk_y = min(
                (tilemap.height + self.CHUNK_SIZE - 1) // self.CHUNK_SIZE,
                int((layer_camera_top + camera.height) / (tilemap.tile_height * self.CHUNK_SIZE))
                + 1,
            )

            # Render visible chunks
            for chunk_y in range(start_chunk_y, end_chunk_y):
                for chunk_x in range(start_chunk_x, end_chunk_x):
                    self._render_legacy_chunk(
                        screen,
                        tilemap,
                        camera,
                        tileset,
                        layer,
                        layer_id,
                        chunk_x,
                        chunk_y,
                        layer.offset_x,
                        layer.offset_y,
                    )

            self._stats["layers_rendered"] += 1

    def _render_legacy_chunk(
        self,
        screen: pygame.Surface,
        tilemap: Tilemap,
        camera: Camera,
        tileset: Tileset,
        layer: TileLayer,
        layer_id: str,
        chunk_x: int,
        chunk_y: int,
        offset_x: float,
        offset_y: float,
    ):
        """Render a legacy layer chunk with caching"""
        chunk_key = (layer_id, chunk_x, chunk_y)

        # Check cache
        if self.enable_caching and chunk_key in self._chunk_cache:
            chunk_surface = self._chunk_cache[chunk_key]
            self._stats["cache_hits"] += 1
            self._stats["chunks_reused"] += 1
        else:
            # Render chunk
            chunk_surface = self._render_legacy_chunk_to_surface(
                tilemap, tileset, layer, chunk_x, chunk_y
            )

            if chunk_surface is None:
                return

            # Cache the chunk
            if self.enable_caching:
                self._chunk_cache[chunk_key] = chunk_surface
                self._stats["chunks_cached"] += 1

            self._stats["cache_misses"] += 1

        # Calculate chunk world position
        chunk_world_x = chunk_x * self.CHUNK_SIZE * tilemap.tile_width - offset_x
        chunk_world_y = chunk_y * self.CHUNK_SIZE * tilemap.tile_height - offset_y

        # Convert to screen coordinates
        screen_x, screen_y = camera.world_to_screen(chunk_world_x, chunk_world_y)

        # Apply layer opacity
        if layer.opacity < 1.0:
            render_surface = chunk_surface.copy()
            render_surface.set_alpha(int(layer.opacity * 255))
            screen.blit(render_surface, (screen_x, screen_y))
        else:
            screen.blit(chunk_surface, (screen_x, screen_y))

        self._stats["chunks_rendered"] += 1

    def _render_legacy_chunk_to_surface(
        self,
        tilemap: Tilemap,
        tileset: Tileset,
        layer: TileLayer,
        chunk_x: int,
        chunk_y: int,
    ) -> Optional[pygame.Surface]:
        """Render a legacy chunk to surface"""
        # Calculate tile range
        start_tile_x = chunk_x * self.CHUNK_SIZE
        start_tile_y = chunk_y * self.CHUNK_SIZE
        end_tile_x = min(start_tile_x + self.CHUNK_SIZE, tilemap.width)
        end_tile_y = min(start_tile_y + self.CHUNK_SIZE, tilemap.height)

        # Calculate chunk size
        chunk_pixel_width = (end_tile_x - start_tile_x) * tilemap.tile_width
        chunk_pixel_height = (end_tile_y - start_tile_y) * tilemap.tile_height

        # Check if chunk has tiles
        has_tiles = False
        for tile_y in range(start_tile_y, end_tile_y):
            for tile_x in range(start_tile_x, end_tile_x):
                tile = layer.get_tile(tile_x, tile_y)
                if tile and not tile.is_empty():
                    has_tiles = True
                    break
            if has_tiles:
                break

        if not has_tiles:
            self._stats["tiles_culled"] += (end_tile_x - start_tile_x) * (end_tile_y - start_tile_y)
            return None

        # Create chunk surface
        chunk_surface = pygame.Surface((chunk_pixel_width, chunk_pixel_height), pygame.SRCALPHA)

        # Render tiles
        for tile_y in range(start_tile_y, end_tile_y):
            for tile_x in range(start_tile_x, end_tile_x):
                tile = layer.get_tile(tile_x, tile_y)

                if not tile or tile.is_empty():
                    self._stats["tiles_culled"] += 1
                    continue

                # Get tile surface
                tile_surface = tileset.tiles.get(tile.tile_id)
                if not tile_surface:
                    self._stats["tiles_culled"] += 1
                    continue

                # Apply transformations if needed
                render_surface = tile_surface
                if tile.flags != 0:
                    render_surface = self._apply_tile_transforms(tile_surface, tile)

                # Calculate position within chunk
                local_x = (tile_x - start_tile_x) * tilemap.tile_width
                local_y = (tile_y - start_tile_y) * tilemap.tile_height

                # Blit tile
                chunk_surface.blit(render_surface, (local_x, local_y))
                self._stats["tiles_rendered"] += 1

        return chunk_surface


class TilemapBuilder:
    """Helper class for building tilemaps"""

    @staticmethod
    def create_simple_tilemap(
        width: int, height: int, tile_size: int = 32, use_enhanced: bool = True
    ) -> Tilemap:
        """Create a simple single-layer tilemap"""
        tilemap = Tilemap(width, height, tile_size, tile_size, use_enhanced_layers=use_enhanced)

        if use_enhanced:
            tilemap.create_enhanced_layer("Ground")
        else:
            tilemap.create_layer("ground", fill_tile=0)

        return tilemap

    @staticmethod
    def create_layered_tilemap(
        width: int,
        height: int,
        tile_size: int = 32,
        layer_names: List[str] = None,
        use_enhanced: bool = True,
    ) -> Tilemap:
        """Create a multi-layer tilemap"""
        if layer_names is None:
            layer_names = ["Ground", "Objects", "Overlay"]

        tilemap = Tilemap(width, height, tile_size, tile_size, use_enhanced_layers=use_enhanced)

        if use_enhanced:
            for name in layer_names:
                tilemap.create_enhanced_layer(name)
        else:
            for name in layer_names:
                tilemap.create_layer(name)

        return tilemap

    @staticmethod
    def create_parallax_scene(width: int, height: int, tile_size: int = 32) -> Tilemap:
        """
        Create a tilemap with parallax background layers.

        Creates:
        - Far background (0.3x parallax)
        - Mid background (0.6x parallax)
        - Ground (1.0x parallax)
        - Objects (1.0x parallax)
        - Foreground (1.2x parallax)
        """
        tilemap = Tilemap(width, height, tile_size, tile_size, use_enhanced_layers=True)

        # Background layers with parallax
        tilemap.create_parallax_background("Far Background", parallax_x=0.3, parallax_y=0.3)
        tilemap.create_parallax_background("Mid Background", parallax_x=0.6, parallax_y=0.6)

        # Standard ground layers
        tilemap.create_enhanced_layer("Ground", layer_type=LayerType.STANDARD)
        tilemap.create_enhanced_layer("Objects", layer_type=LayerType.STANDARD)

        # Foreground with slight parallax
        props = LayerProperties(
            name="Foreground",
            layer_type=LayerType.PARALLAX_FOREGROUND,
            parallax_x=1.2,
            parallax_y=1.0,
            opacity=0.8,
        )
        tilemap.layer_manager.create_layer("Foreground", properties=props)

        return tilemap

    @staticmethod
    def migrate_legacy_tilemap(old_tilemap: Tilemap) -> Tilemap:
        """
        Migrate a legacy 3-layer tilemap to enhanced system.

        Args:
            old_tilemap: Old tilemap with legacy layers

        Returns:
            New tilemap with enhanced layers
        """
        if old_tilemap.use_enhanced_layers:
            return old_tilemap  # Already enhanced

        # Create new enhanced tilemap
        new_tilemap = Tilemap(
            old_tilemap.width,
            old_tilemap.height,
            old_tilemap.tile_width,
            old_tilemap.tile_height,
            use_enhanced_layers=True,
        )

        # Copy tilesets
        new_tilemap.tilesets = old_tilemap.tilesets.copy()
        new_tilemap.default_tileset = old_tilemap.default_tileset

        # Convert each layer
        for old_layer in old_tilemap.layers:
            props = LayerProperties(
                name=old_layer.name,
                visible=old_layer.visible,
                opacity=old_layer.opacity,
                offset_x=old_layer.offset_x,
                offset_y=old_layer.offset_y,
                parallax_x=old_layer.parallax_x,
                parallax_y=old_layer.parallax_y,
            )

            # Convert tile data
            tiles = [[tile.tile_id for tile in row] for row in old_layer.tiles]

            new_layer = EnhancedTileLayer(
                width=old_layer.width, height=old_layer.height, tiles=tiles, properties=props
            )

            new_tilemap.layer_manager.layers[props.layer_id] = new_layer
            new_tilemap.layer_manager.root_ids.append(props.layer_id)

        return new_tilemap

    @staticmethod
    def create_tileset_from_sheet(
        name: str,
        texture_path: str,
        tile_width: int,
        tile_height: int,
        columns: int,
        rows: int,
    ) -> Tileset:
        """Create a tileset from a sprite sheet"""
        tile_count = columns * rows
        return Tileset(
            name=name,
            texture_path=texture_path,
            tile_width=tile_width,
            tile_height=tile_height,
            columns=columns,
            tile_count=tile_count,
        )

    @staticmethod
    def fill_pattern(layer: TileLayer, pattern: List[List[int]]):
        """Fill layer with a repeating pattern"""
        pattern_height = len(pattern)
        pattern_width = len(pattern[0]) if pattern_height > 0 else 0

        if pattern_width == 0 or pattern_height == 0:
            return

        for y in range(layer.height):
            for x in range(layer.width):
                pattern_y = y % pattern_height
                pattern_x = x % pattern_width
                tile_id = pattern[pattern_y][pattern_x]
                layer.set_tile(x, y, Tile(tile_id=tile_id))

    @staticmethod
    def create_border(layer: TileLayer, border_tile: int, fill_tile: int = 0):
        """Create a border around the layer"""
        # Fill interior
        for y in range(1, layer.height - 1):
            for x in range(1, layer.width - 1):
                layer.set_tile(x, y, Tile(tile_id=fill_tile))

        # Create border
        for x in range(layer.width):
            layer.set_tile(x, 0, Tile(tile_id=border_tile))
            layer.set_tile(x, layer.height - 1, Tile(tile_id=border_tile))

        for y in range(layer.height):
            layer.set_tile(0, y, Tile(tile_id=border_tile))
            layer.set_tile(layer.width - 1, y, Tile(tile_id=border_tile))
