"""
Tilemap System

Grid-based level rendering with multiple layers, tilesets, and efficient culling.
"""

import pygame
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from neonworks.core.ecs import Component
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
    """

    def __init__(self, width: int, height: int, tile_width: int, tile_height: int):
        """
        Create a new tilemap.

        Args:
            width: Width in tiles
            height: Height in tiles
            tile_width: Width of each tile in pixels
            tile_height: Height of each tile in pixels
        """
        self.width = width
        self.height = height
        self.tile_width = tile_width
        self.tile_height = tile_height

        # Layers (ordered from bottom to top)
        self.layers: List[TileLayer] = []

        # Tilesets
        self.tilesets: Dict[str, Tileset] = {}
        self.default_tileset: Optional[str] = None

        # Rendering cache
        self._render_cache_dirty = True

    def add_layer(self, layer: TileLayer) -> int:
        """Add a layer and return its index"""
        self.layers.append(layer)
        self._render_cache_dirty = True
        return len(self.layers) - 1

    def create_layer(self, name: str, fill_tile: int = 0) -> int:
        """Create and add a new layer"""
        layer = TileLayer(name=name, width=self.width, height=self.height)
        if fill_tile != 0:
            layer.fill(fill_tile)
        return self.add_layer(layer)

    def get_layer(self, index: int) -> Optional[TileLayer]:
        """Get layer by index"""
        if 0 <= index < len(self.layers):
            return self.layers[index]
        return None

    def get_layer_by_name(self, name: str) -> Optional[TileLayer]:
        """Get layer by name"""
        for layer in self.layers:
            if layer.name == name:
                return layer
        return None

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
    """

    def __init__(self, asset_manager: AssetManager):
        self.asset_manager = asset_manager
        self._stats = {
            'tiles_rendered': 0,
            'tiles_culled': 0
        }

    def render(self, screen: pygame.Surface, tilemap: Tilemap, camera: Camera):
        """
        Render a tilemap to the screen.

        Args:
            screen: Surface to render to
            tilemap: Tilemap to render
            camera: Camera for culling and positioning
        """
        self._stats['tiles_rendered'] = 0
        self._stats['tiles_culled'] = 0

        # Get default tileset
        tileset = tilemap.get_tileset()
        if not tileset:
            return

        # Load tileset if not already loaded
        if not tileset.tiles:
            tileset.load_tiles(self.asset_manager)

        # Calculate visible tile range
        camera_left = camera.x - camera.width / 2
        camera_top = camera.y - camera.height / 2
        camera_right = camera.x + camera.width / 2
        camera_bottom = camera.y + camera.height / 2

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
            end_tile_x = min(tilemap.width, int((layer_camera_left + camera.width) / tilemap.tile_width) + 2)
            end_tile_y = min(tilemap.height, int((layer_camera_top + camera.height) / tilemap.tile_height) + 2)

            # Render visible tiles
            for tile_y in range(start_tile_y, end_tile_y):
                for tile_x in range(start_tile_x, end_tile_x):
                    tile = layer.get_tile(tile_x, tile_y)
                    if not tile or tile.is_empty():
                        self._stats['tiles_culled'] += 1
                        continue

                    # Get tile sprite
                    tile_surface = tileset.tiles.get(tile.tile_id)
                    if not tile_surface:
                        self._stats['tiles_culled'] += 1
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
                    self._stats['tiles_rendered'] += 1

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


class TilemapBuilder:
    """Helper class for building tilemaps"""

    @staticmethod
    def create_simple_tilemap(width: int, height: int, tile_size: int = 32) -> Tilemap:
        """Create a simple single-layer tilemap"""
        tilemap = Tilemap(width, height, tile_size, tile_size)
        tilemap.create_layer("ground", fill_tile=0)
        return tilemap

    @staticmethod
    def create_layered_tilemap(width: int, height: int, tile_size: int = 32,
                               layer_names: List[str] = None) -> Tilemap:
        """Create a multi-layer tilemap"""
        if layer_names is None:
            layer_names = ["ground", "objects", "overlay"]

        tilemap = Tilemap(width, height, tile_size, tile_size)
        for name in layer_names:
            tilemap.create_layer(name)

        return tilemap

    @staticmethod
    def create_tileset_from_sheet(name: str, texture_path: str,
                                  tile_width: int, tile_height: int,
                                  columns: int, rows: int) -> Tileset:
        """Create a tileset from a sprite sheet"""
        tile_count = columns * rows
        return Tileset(
            name=name,
            texture_path=texture_path,
            tile_width=tile_width,
            tile_height=tile_height,
            columns=columns,
            tile_count=tile_count
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
