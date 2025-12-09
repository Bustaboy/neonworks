"""
Autotile System for NeonWorks Engine

Provides intelligent tile matching for creating seamless terrain transitions.
Supports both 47-tile and 16-tile autotile formats with 8-neighbor checking.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

import pygame

from neonworks.data.map_layers import EnhancedTileLayer
from neonworks.rendering.tilemap import Tilemap


class AutotileFormat(Enum):
    """Autotile format types"""

    TILE_47 = "47-tile"  # RPG Maker-style 47-tile autotile
    TILE_16 = "16-tile"  # Simplified 16-tile autotile (blob pattern)


# Bitmask values for 8 neighbors (clockwise from top)
NEIGHBOR_TOP = 1 << 0  # 1
NEIGHBOR_TOP_RIGHT = 1 << 1  # 2
NEIGHBOR_RIGHT = 1 << 2  # 4
NEIGHBOR_BOTTOM_RIGHT = 1 << 3  # 8
NEIGHBOR_BOTTOM = 1 << 4  # 16
NEIGHBOR_BOTTOM_LEFT = 1 << 5  # 32
NEIGHBOR_LEFT = 1 << 6  # 64
NEIGHBOR_TOP_LEFT = 1 << 7  # 128

# Export diagonal neighbor constants
__all__ = [
    "AutotileFormat",
    "AutotileSet",
    "AutotileManager",
    "get_autotile_manager",
    "reset_autotile_manager",
    "NEIGHBOR_TOP",
    "NEIGHBOR_TOP_RIGHT",
    "NEIGHBOR_RIGHT",
    "NEIGHBOR_BOTTOM_RIGHT",
    "NEIGHBOR_BOTTOM",
    "NEIGHBOR_BOTTOM_LEFT",
    "NEIGHBOR_LEFT",
    "NEIGHBOR_TOP_LEFT",
    "CARDINAL_TOP",
    "CARDINAL_RIGHT",
    "CARDINAL_BOTTOM",
    "CARDINAL_LEFT",
]

# Cardinal directions (used for 16-tile simplified format)
CARDINAL_TOP = 1 << 0  # 1
CARDINAL_RIGHT = 1 << 1  # 2
CARDINAL_BOTTOM = 1 << 2  # 4
CARDINAL_LEFT = 1 << 3  # 8


@dataclass
class AutotileSet:
    """
    Defines an autotile set with tile matching rules.

    An autotile set is a collection of tile variants that automatically
    connect to each other based on neighboring tiles.
    """

    name: str
    tileset_name: str  # Name of the tileset this autotile belongs to
    format: AutotileFormat
    base_tile_id: int  # Starting tile ID in the tileset
    tile_ids: Set[int] = field(default_factory=set)  # All tile IDs in this autotile set

    # Mapping from bitmask to tile ID offset from base_tile_id
    bitmask_to_tile: Dict[int, int] = field(default_factory=dict)

    # Optional: Custom matching rules
    match_same_type: bool = True  # Only match with tiles from same autotile set
    match_tile_ids: Set[int] = field(default_factory=set)  # Additional tile IDs to match with

    def __post_init__(self):
        """Initialize bitmask mapping based on format."""
        if not self.bitmask_to_tile:
            if self.format == AutotileFormat.TILE_47:
                self.bitmask_to_tile = self._create_47_tile_mapping()
            elif self.format == AutotileFormat.TILE_16:
                self.bitmask_to_tile = self._create_16_tile_mapping()

        # Auto-populate tile_ids if not provided
        if not self.tile_ids:
            max_offset = max(self.bitmask_to_tile.values()) if self.bitmask_to_tile else 0
            self.tile_ids = {self.base_tile_id + i for i in range(max_offset + 1)}

    def _create_47_tile_mapping(self) -> Dict[int, int]:
        """
        Create 47-tile autotile mapping (RPG Maker style).

        This is a comprehensive autotile format with all possible
        combinations of cardinal and diagonal neighbors.
        """
        mapping = {}

        # The 47-tile format has specific tile positions for each bitmask
        # Here's a simplified mapping - in production, this would be more complete

        # Basic patterns (cardinal directions only)
        mapping[0] = 0  # Isolated tile
        mapping[CARDINAL_TOP] = 1
        mapping[CARDINAL_RIGHT] = 2
        mapping[CARDINAL_BOTTOM] = 3
        mapping[CARDINAL_LEFT] = 4
        mapping[CARDINAL_TOP | CARDINAL_RIGHT] = 5
        mapping[CARDINAL_RIGHT | CARDINAL_BOTTOM] = 6
        mapping[CARDINAL_BOTTOM | CARDINAL_LEFT] = 7
        mapping[CARDINAL_LEFT | CARDINAL_TOP] = 8
        mapping[CARDINAL_TOP | CARDINAL_BOTTOM] = 9
        mapping[CARDINAL_LEFT | CARDINAL_RIGHT] = 10
        mapping[CARDINAL_TOP | CARDINAL_RIGHT | CARDINAL_BOTTOM] = 11
        mapping[CARDINAL_RIGHT | CARDINAL_BOTTOM | CARDINAL_LEFT] = 12
        mapping[CARDINAL_BOTTOM | CARDINAL_LEFT | CARDINAL_TOP] = 13
        mapping[CARDINAL_LEFT | CARDINAL_TOP | CARDINAL_RIGHT] = 14
        mapping[CARDINAL_TOP | CARDINAL_RIGHT | CARDINAL_BOTTOM | CARDINAL_LEFT] = 15

        # Corner variations (with diagonal neighbors)
        # Tiles 16-46 would be corner variations
        # For now, we'll use a simplified approach

        return mapping

    def _create_16_tile_mapping(self) -> Dict[int, int]:
        """
        Create 16-tile blob autotile mapping.

        This is a simplified autotile format using only cardinal directions.
        Common in indie games and simpler tile-based systems.

        Tile layout (4x4 grid):
        0  1  2  3
        4  5  6  7
        8  9  10 11
        12 13 14 15
        """
        mapping = {}

        # Row 0: No connections, single edge connections
        mapping[0] = 0  # No connections (isolated)
        mapping[CARDINAL_LEFT] = 1  # Left only
        mapping[CARDINAL_RIGHT] = 2  # Right only
        mapping[CARDINAL_LEFT | CARDINAL_RIGHT] = 3  # Left + Right (horizontal)

        # Row 1: Top edge variations
        mapping[CARDINAL_TOP] = 4  # Top only
        mapping[CARDINAL_TOP | CARDINAL_LEFT] = 5  # Top + Left (corner)
        mapping[CARDINAL_TOP | CARDINAL_RIGHT] = 6  # Top + Right (corner)
        mapping[CARDINAL_TOP | CARDINAL_LEFT | CARDINAL_RIGHT] = 7  # Top + sides (T-junction)

        # Row 2: Bottom edge variations
        mapping[CARDINAL_BOTTOM] = 8  # Bottom only
        mapping[CARDINAL_BOTTOM | CARDINAL_LEFT] = 9  # Bottom + Left (corner)
        mapping[CARDINAL_BOTTOM | CARDINAL_RIGHT] = 10  # Bottom + Right (corner)
        mapping[CARDINAL_BOTTOM | CARDINAL_LEFT | CARDINAL_RIGHT] = 11  # Bottom + sides

        # Row 3: Vertical and cross patterns
        mapping[CARDINAL_TOP | CARDINAL_BOTTOM] = 12  # Vertical connection
        mapping[CARDINAL_TOP | CARDINAL_BOTTOM | CARDINAL_LEFT] = 13  # T-junction left
        mapping[CARDINAL_TOP | CARDINAL_BOTTOM | CARDINAL_RIGHT] = 14  # T-junction right
        mapping[CARDINAL_TOP | CARDINAL_RIGHT | CARDINAL_BOTTOM | CARDINAL_LEFT] = 15  # Full cross

        return mapping

    def get_tile_for_bitmask(self, bitmask: int) -> int:
        """
        Get the tile ID for a given neighbor bitmask.

        Args:
            bitmask: Bitmask representing neighbor configuration

        Returns:
            Tile ID from the tileset
        """
        # For 16-tile format, convert 8-neighbor bitmask to 4-cardinal bitmask
        if self.format == AutotileFormat.TILE_16:
            cardinal_mask = 0
            if bitmask & NEIGHBOR_TOP:
                cardinal_mask |= CARDINAL_TOP
            if bitmask & NEIGHBOR_RIGHT:
                cardinal_mask |= CARDINAL_RIGHT
            if bitmask & NEIGHBOR_BOTTOM:
                cardinal_mask |= CARDINAL_BOTTOM
            if bitmask & NEIGHBOR_LEFT:
                cardinal_mask |= CARDINAL_LEFT
            bitmask = cardinal_mask

        # Look up tile offset
        offset = self.bitmask_to_tile.get(bitmask, 0)
        return self.base_tile_id + offset

    def contains_tile(self, tile_id: int) -> bool:
        """Check if a tile ID belongs to this autotile set."""
        return tile_id in self.tile_ids


class AutotileManager:
    """
    Manages autotile sets and handles tile matching logic.

    This manager coordinates autotile operations including:
    - Registering autotile sets
    - Calculating neighbor bitmasks
    - Updating tiles based on neighbors
    - Auto-updating adjacent tiles when painting
    """

    def __init__(self):
        """Initialize the autotile manager."""
        self.autotile_sets: Dict[str, AutotileSet] = {}
        self.tile_to_autotile: Dict[int, str] = {}  # Map tile_id to autotile set name

    def register_autotile_set(self, autotile_set: AutotileSet):
        """
        Register an autotile set.

        Args:
            autotile_set: AutotileSet to register
        """
        self.autotile_sets[autotile_set.name] = autotile_set

        # Update reverse mapping
        for tile_id in autotile_set.tile_ids:
            self.tile_to_autotile[tile_id] = autotile_set.name

    def get_autotile_set(self, name: str) -> Optional[AutotileSet]:
        """Get autotile set by name."""
        return self.autotile_sets.get(name)

    def get_autotile_for_tile(self, tile_id: int) -> Optional[AutotileSet]:
        """Get the autotile set that contains a given tile ID."""
        autotile_name = self.tile_to_autotile.get(tile_id)
        if autotile_name:
            return self.autotile_sets.get(autotile_name)
        return None

    def is_autotile(self, tile_id: int) -> bool:
        """Check if a tile ID belongs to an autotile set."""
        return tile_id in self.tile_to_autotile

    def calculate_bitmask(
        self,
        layer: EnhancedTileLayer,
        x: int,
        y: int,
        autotile_set: AutotileSet,
    ) -> int:
        """
        Calculate neighbor bitmask for a tile position.

        Args:
            layer: Tile layer to check
            x: Tile X coordinate
            y: Tile Y coordinate
            autotile_set: Autotile set to match against

        Returns:
            Bitmask representing which neighbors match
        """
        bitmask = 0

        # 8 neighbor offsets (clockwise from top)
        neighbors = [
            (0, -1),  # Top
            (1, -1),  # Top-Right
            (1, 0),  # Right
            (1, 1),  # Bottom-Right
            (0, 1),  # Bottom
            (-1, 1),  # Bottom-Left
            (-1, 0),  # Left
            (-1, -1),  # Top-Left
        ]

        for i, (dx, dy) in enumerate(neighbors):
            nx, ny = x + dx, y + dy

            # Check bounds
            if 0 <= nx < layer.width and 0 <= ny < layer.height:
                neighbor_id = layer.get_tile(nx, ny)
                if neighbor_id and self._tiles_match(neighbor_id, autotile_set):
                    bitmask |= 1 << i

        return bitmask

    def _tiles_match(self, tile_id: int, autotile_set: AutotileSet) -> bool:
        """
        Check if a tile matches with the autotile set.

        Args:
            tile_id: Tile ID to check
            autotile_set: Autotile set to match against

        Returns:
            True if tiles should connect
        """
        # Check if tile belongs to the autotile set first
        # (tile_id=0 can be valid if it's part of an autotile set)
        if autotile_set.contains_tile(tile_id):
            return True

        # Check custom match rules
        if tile_id in autotile_set.match_tile_ids:
            return True

        # Tile doesn't match
        return False

    def get_autotile_for_position(
        self,
        layer: EnhancedTileLayer,
        x: int,
        y: int,
        autotile_set: AutotileSet,
    ) -> int:
        """
        Get the correct autotile variant for a position.

        Args:
            layer: Tile layer
            x: Tile X coordinate
            y: Tile Y coordinate
            autotile_set: Autotile set to use

        Returns:
            Tile ID for the correct autotile variant
        """
        bitmask = self.calculate_bitmask(layer, x, y, autotile_set)
        return autotile_set.get_tile_for_bitmask(bitmask)

    def update_tile(
        self,
        layer: EnhancedTileLayer,
        x: int,
        y: int,
        autotile_set: AutotileSet,
    ):
        """
        Update a tile to use the correct autotile variant.

        Args:
            layer: Tile layer to update
            x: Tile X coordinate
            y: Tile Y coordinate
            autotile_set: Autotile set to use
        """
        tile_id = self.get_autotile_for_position(layer, x, y, autotile_set)
        layer.set_tile(x, y, tile_id)

    def update_adjacent_tiles(
        self,
        layer: EnhancedTileLayer,
        x: int,
        y: int,
    ):
        """
        Update adjacent tiles after placing a new tile.

        This ensures seamless transitions when painting autotiles.

        Args:
            layer: Tile layer to update
            x: Tile X coordinate of newly placed tile
            y: Tile Y coordinate of newly placed tile
        """
        # Get the tile at this position
        center_tile_id = layer.get_tile(x, y)
        if not center_tile_id:
            return

        # Get autotile set for the center tile
        autotile_set = self.get_autotile_for_tile(center_tile_id)
        if not autotile_set:
            return

        # Update the center tile itself
        self.update_tile(layer, x, y, autotile_set)

        # Update 8 neighbors
        neighbors = [
            (0, -1),  # Top
            (1, -1),  # Top-Right
            (1, 0),  # Right
            (1, 1),  # Bottom-Right
            (0, 1),  # Bottom
            (-1, 1),  # Bottom-Left
            (-1, 0),  # Left
            (-1, -1),  # Top-Left
        ]

        for dx, dy in neighbors:
            nx, ny = x + dx, y + dy

            if 0 <= nx < layer.width and 0 <= ny < layer.height:
                neighbor_id = layer.get_tile(nx, ny)

                if neighbor_id:
                    neighbor_autotile = self.get_autotile_for_tile(neighbor_id)

                    if neighbor_autotile:
                        # Update neighbor tile
                        self.update_tile(layer, nx, ny, neighbor_autotile)

    def paint_autotile(
        self,
        layer: EnhancedTileLayer,
        x: int,
        y: int,
        autotile_set: AutotileSet,
    ):
        """
        Paint an autotile at a position and update adjacent tiles.

        Args:
            layer: Tile layer to paint on
            x: Tile X coordinate
            y: Tile Y coordinate
            autotile_set: Autotile set to paint with
        """
        # Place the base tile (it will be updated based on neighbors)
        layer.set_tile(x, y, autotile_set.base_tile_id)

        # Update this tile and all adjacent tiles
        self.update_adjacent_tiles(layer, x, y)

    def erase_autotile(
        self,
        layer: EnhancedTileLayer,
        x: int,
        y: int,
    ):
        """
        Erase a tile and update adjacent autotiles.

        Args:
            layer: Tile layer to erase from
            x: Tile X coordinate
            y: Tile Y coordinate
        """
        # Erase the tile
        layer.set_tile(x, y, 0)

        # Update adjacent tiles
        neighbors = [
            (0, -1),  # Top
            (1, 0),  # Right
            (0, 1),  # Bottom
            (-1, 0),  # Left
            (1, -1),  # Top-Right
            (1, 1),  # Bottom-Right
            (-1, 1),  # Bottom-Left
            (-1, -1),  # Top-Left
        ]

        for dx, dy in neighbors:
            nx, ny = x + dx, y + dy

            if 0 <= nx < layer.width and 0 <= ny < layer.height:
                neighbor_id = layer.get_tile(nx, ny)

                if neighbor_id:
                    autotile_set = self.get_autotile_for_tile(neighbor_id)

                    if autotile_set:
                        self.update_tile(layer, nx, ny, autotile_set)

    def get_preview_tile(
        self,
        layer: EnhancedTileLayer,
        x: int,
        y: int,
        autotile_set: AutotileSet,
    ) -> int:
        """
        Get a preview of what tile would be placed without actually placing it.

        Args:
            layer: Tile layer
            x: Tile X coordinate
            y: Tile Y coordinate
            autotile_set: Autotile set to preview

        Returns:
            Tile ID that would be placed
        """
        # Temporarily set the tile
        original_tile = layer.get_tile(x, y)
        layer.set_tile(x, y, autotile_set.base_tile_id)

        # Calculate what it would be
        preview_tile_id = self.get_autotile_for_position(layer, x, y, autotile_set)

        # Restore original tile
        layer.set_tile(x, y, original_tile or 0)

        return preview_tile_id

    def fill_with_autotile(
        self,
        layer: EnhancedTileLayer,
        start_x: int,
        start_y: int,
        autotile_set: AutotileSet,
    ):
        """
        Flood fill an area with autotiles.

        Args:
            layer: Tile layer to fill
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            autotile_set: Autotile set to fill with
        """
        # Get the tile to replace
        start_tile_id = layer.get_tile(start_x, start_y)
        if start_tile_id is None:
            return

        target_tile_id = start_tile_id

        # Don't fill if already this autotile
        if autotile_set.contains_tile(target_tile_id):
            return

        # Flood fill algorithm
        filled_positions = set()
        queue = [(start_x, start_y)]

        while queue:
            x, y = queue.pop(0)

            if (x, y) in filled_positions:
                continue

            if not (0 <= x < layer.width and 0 <= y < layer.height):
                continue

            tile_id = layer.get_tile(x, y)
            if tile_id is None or tile_id != target_tile_id:
                continue

            # Fill this position
            layer.set_tile(x, y, autotile_set.base_tile_id)
            filled_positions.add((x, y))

            # Add neighbors to queue
            queue.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])

        # Update all filled tiles and their neighbors
        for x, y in filled_positions:
            self.update_adjacent_tiles(layer, x, y)


# Global autotile manager instance
_autotile_manager: Optional[AutotileManager] = None


def get_autotile_manager() -> AutotileManager:
    """Get the global autotile manager instance."""
    global _autotile_manager
    if _autotile_manager is None:
        _autotile_manager = AutotileManager()
    return _autotile_manager


def reset_autotile_manager():
    """Reset the global autotile manager (useful for testing)."""
    global _autotile_manager
    _autotile_manager = None
