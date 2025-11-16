"""
Tileset management system for NeonWorks engine.

This module provides comprehensive tileset management including:
- Loading and parsing tileset images (PNG)
- Tile metadata (passability, terrain tags, animations)
- Recently used tiles tracking
- Favorites system
- Multi-tileset support per project

Author: NeonWorks Team
Version: 0.1.0
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import pygame

from neonworks.rendering.assets import AssetManager


@dataclass
class TileMetadata:
    """
    Metadata for a single tile in a tileset.

    Attributes:
        tile_id: Unique identifier (index in tileset)
        passable: Whether entities can walk through this tile
        terrain_tags: List of terrain type tags (grass, water, lava, etc.)
        animation_frames: List of tile_ids for animation sequence
        animation_speed: Frames per second for animation
        name: Human-readable name for the tile
        custom_properties: User-defined key-value properties
    """

    tile_id: int
    passable: bool = True
    terrain_tags: List[str] = field(default_factory=list)
    animation_frames: List[int] = field(default_factory=list)
    animation_speed: float = 0.0
    name: str = ""
    custom_properties: Dict[str, any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "tile_id": self.tile_id,
            "passable": self.passable,
            "terrain_tags": self.terrain_tags,
            "animation_frames": self.animation_frames,
            "animation_speed": self.animation_speed,
            "name": self.name,
            "custom_properties": self.custom_properties,
        }

    @staticmethod
    def from_dict(data: Dict) -> TileMetadata:
        """Create TileMetadata from dictionary."""
        return TileMetadata(
            tile_id=data.get("tile_id", 0),
            passable=data.get("passable", True),
            terrain_tags=data.get("terrain_tags", []),
            animation_frames=data.get("animation_frames", []),
            animation_speed=data.get("animation_speed", 0.0),
            name=data.get("name", ""),
            custom_properties=data.get("custom_properties", {}),
        )


@dataclass
class TilesetInfo:
    """
    Information about a loaded tileset.

    Attributes:
        tileset_id: Unique identifier for this tileset
        name: Display name
        image_path: Path to tileset image file (relative to project)
        tile_width: Width of each tile in pixels
        tile_height: Height of each tile in pixels
        columns: Number of tile columns in the image
        rows: Number of tile rows in the image
        spacing: Spacing between tiles in pixels
        margin: Margin around tileset edges in pixels
        tile_count: Total number of tiles
        metadata: Tile metadata indexed by tile_id
        surface: Loaded pygame surface (None until loaded)
        tiles: Extracted tile surfaces indexed by tile_id
    """

    tileset_id: str
    name: str
    image_path: str
    tile_width: int = 32
    tile_height: int = 32
    columns: int = 1
    rows: int = 1
    spacing: int = 0
    margin: int = 0
    tile_count: int = 1
    metadata: Dict[int, TileMetadata] = field(default_factory=dict)
    surface: Optional[pygame.Surface] = None
    tiles: Dict[int, pygame.Surface] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization (excludes surfaces)."""
        return {
            "tileset_id": self.tileset_id,
            "name": self.name,
            "image_path": self.image_path,
            "tile_width": self.tile_width,
            "tile_height": self.tile_height,
            "columns": self.columns,
            "rows": self.rows,
            "spacing": self.spacing,
            "margin": self.margin,
            "tile_count": self.tile_count,
            "metadata": {tile_id: meta.to_dict() for tile_id, meta in self.metadata.items()},
        }

    @staticmethod
    def from_dict(data: Dict) -> TilesetInfo:
        """Create TilesetInfo from dictionary."""
        metadata = {
            int(tile_id): TileMetadata.from_dict(meta_data)
            for tile_id, meta_data in data.get("metadata", {}).items()
        }

        return TilesetInfo(
            tileset_id=data.get("tileset_id", ""),
            name=data.get("name", "Unnamed Tileset"),
            image_path=data.get("image_path", ""),
            tile_width=data.get("tile_width", 32),
            tile_height=data.get("tile_height", 32),
            columns=data.get("columns", 1),
            rows=data.get("rows", 1),
            spacing=data.get("spacing", 0),
            margin=data.get("margin", 0),
            tile_count=data.get("tile_count", 1),
            metadata=metadata,
        )

    def get_tile_metadata(self, tile_id: int) -> TileMetadata:
        """
        Get metadata for a tile, creating default if not exists.

        Args:
            tile_id: Tile identifier

        Returns:
            TileMetadata for the tile
        """
        if tile_id not in self.metadata:
            self.metadata[tile_id] = TileMetadata(tile_id=tile_id)
        return self.metadata[tile_id]

    def is_tile_passable(self, tile_id: int) -> bool:
        """
        Check if a tile is passable.

        Args:
            tile_id: Tile identifier

        Returns:
            True if passable, False otherwise
        """
        if tile_id not in self.metadata:
            return True  # Default to passable
        return self.metadata[tile_id].passable

    def get_tile_terrain_tags(self, tile_id: int) -> List[str]:
        """
        Get terrain tags for a tile.

        Args:
            tile_id: Tile identifier

        Returns:
            List of terrain tag strings
        """
        if tile_id not in self.metadata:
            return []
        return self.metadata[tile_id].terrain_tags


class TilesetManager:
    """
    Manages multiple tilesets for a project.

    Provides functionality for:
    - Loading and parsing tileset images
    - Managing tile metadata
    - Tracking recently used tiles
    - Managing favorite tiles
    - Persisting tileset configuration
    """

    def __init__(self, project_path: Optional[str] = None):
        """
        Initialize the tileset manager.

        Args:
            project_path: Path to project directory (for relative paths)
        """
        self.project_path = project_path or os.getcwd()
        self.tilesets: Dict[str, TilesetInfo] = {}
        self.active_tileset_id: Optional[str] = None
        self.recently_used: List[Tuple[str, int]] = []  # (tileset_id, tile_id)
        self.favorites: Set[Tuple[str, int]] = set()  # (tileset_id, tile_id)
        self.max_recent_tiles: int = 20

    def add_tileset(
        self,
        tileset_id: str,
        name: str,
        image_path: str,
        tile_width: int = 32,
        tile_height: int = 32,
        spacing: int = 0,
        margin: int = 0,
    ) -> TilesetInfo:
        """
        Add a new tileset to the manager.

        Args:
            tileset_id: Unique identifier for the tileset
            name: Display name
            image_path: Path to tileset image (relative to project)
            tile_width: Width of each tile in pixels
            tile_height: Height of each tile in pixels
            spacing: Spacing between tiles in pixels
            margin: Margin around tileset edges in pixels

        Returns:
            Created TilesetInfo object

        Raises:
            ValueError: If tileset_id already exists
            FileNotFoundError: If image file doesn't exist
        """
        if tileset_id in self.tilesets:
            raise ValueError(f"Tileset '{tileset_id}' already exists")

        # Convert to absolute path for validation
        if not os.path.isabs(image_path):
            full_path = os.path.join(self.project_path, image_path)
        else:
            full_path = image_path

        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Tileset image not found: {full_path}")

        tileset = TilesetInfo(
            tileset_id=tileset_id,
            name=name,
            image_path=image_path,
            tile_width=tile_width,
            tile_height=tile_height,
            spacing=spacing,
            margin=margin,
        )

        self.tilesets[tileset_id] = tileset

        # Set as active if it's the first tileset
        if self.active_tileset_id is None:
            self.active_tileset_id = tileset_id

        return tileset

    def remove_tileset(self, tileset_id: str) -> bool:
        """
        Remove a tileset from the manager.

        Args:
            tileset_id: Tileset to remove

        Returns:
            True if removed, False if not found
        """
        if tileset_id not in self.tilesets:
            return False

        del self.tilesets[tileset_id]

        # Clean up references
        self.recently_used = [
            (ts_id, tile_id) for ts_id, tile_id in self.recently_used if ts_id != tileset_id
        ]
        self.favorites = {
            (ts_id, tile_id) for ts_id, tile_id in self.favorites if ts_id != tileset_id
        }

        # Update active tileset if removed
        if self.active_tileset_id == tileset_id:
            self.active_tileset_id = next(iter(self.tilesets.keys())) if self.tilesets else None

        return True

    def load_tileset(self, tileset_id: str) -> bool:
        """
        Load tileset image and parse into individual tiles.

        Args:
            tileset_id: Tileset to load

        Returns:
            True if loaded successfully, False otherwise
        """
        if tileset_id not in self.tilesets:
            print(f"Warning: Tileset '{tileset_id}' not found")
            return False

        tileset = self.tilesets[tileset_id]

        # Get absolute path
        if not os.path.isabs(tileset.image_path):
            full_path = os.path.join(self.project_path, tileset.image_path)
        else:
            full_path = tileset.image_path

        try:
            # Load the tileset image
            tileset.surface = pygame.image.load(full_path).convert_alpha()

            # Calculate tileset dimensions
            surface_width = tileset.surface.get_width()
            surface_height = tileset.surface.get_height()

            # Calculate columns and rows
            available_width = surface_width - (2 * tileset.margin)
            available_height = surface_height - (2 * tileset.margin)

            tileset.columns = (available_width + tileset.spacing) // (
                tileset.tile_width + tileset.spacing
            )
            tileset.rows = (available_height + tileset.spacing) // (
                tileset.tile_height + tileset.spacing
            )

            tileset.tile_count = tileset.columns * tileset.rows

            # Extract individual tiles
            tileset.tiles.clear()
            tile_id = 0

            for row in range(tileset.rows):
                for col in range(tileset.columns):
                    # Calculate tile position
                    x = tileset.margin + col * (tileset.tile_width + tileset.spacing)
                    y = tileset.margin + row * (tileset.tile_height + tileset.spacing)

                    # Extract tile surface
                    tile_surface = pygame.Surface(
                        (tileset.tile_width, tileset.tile_height), pygame.SRCALPHA
                    )
                    tile_surface.blit(
                        tileset.surface, (0, 0), (x, y, tileset.tile_width, tileset.tile_height)
                    )

                    tileset.tiles[tile_id] = tile_surface
                    tile_id += 1

            print(
                f"Loaded tileset '{tileset.name}': "
                f"{tileset.columns}x{tileset.rows} = {tileset.tile_count} tiles"
            )
            return True

        except Exception as e:
            print(f"Error loading tileset '{tileset_id}': {e}")
            return False

    def get_tileset(self, tileset_id: str) -> Optional[TilesetInfo]:
        """
        Get tileset information.

        Args:
            tileset_id: Tileset identifier

        Returns:
            TilesetInfo or None if not found
        """
        return self.tilesets.get(tileset_id)

    def get_active_tileset(self) -> Optional[TilesetInfo]:
        """
        Get the currently active tileset.

        Returns:
            Active TilesetInfo or None if no active tileset
        """
        if self.active_tileset_id is None:
            return None
        return self.tilesets.get(self.active_tileset_id)

    def set_active_tileset(self, tileset_id: str) -> bool:
        """
        Set the active tileset.

        Args:
            tileset_id: Tileset to make active

        Returns:
            True if set successfully, False if tileset not found
        """
        if tileset_id not in self.tilesets:
            return False
        self.active_tileset_id = tileset_id
        return True

    def get_tile_surface(self, tileset_id: str, tile_id: int) -> Optional[pygame.Surface]:
        """
        Get a tile surface from a tileset.

        Args:
            tileset_id: Tileset identifier
            tile_id: Tile identifier

        Returns:
            Pygame Surface or None if not found
        """
        tileset = self.tilesets.get(tileset_id)
        if tileset is None:
            return None

        # Load tileset if not already loaded
        if not tileset.tiles:
            self.load_tileset(tileset_id)

        return tileset.tiles.get(tile_id)

    def add_to_recent(self, tileset_id: str, tile_id: int):
        """
        Add a tile to recently used list.

        Args:
            tileset_id: Tileset identifier
            tile_id: Tile identifier
        """
        tile_ref = (tileset_id, tile_id)

        # Remove if already in list
        if tile_ref in self.recently_used:
            self.recently_used.remove(tile_ref)

        # Add to front
        self.recently_used.insert(0, tile_ref)

        # Trim to max size
        if len(self.recently_used) > self.max_recent_tiles:
            self.recently_used = self.recently_used[: self.max_recent_tiles]

    def get_recent_tiles(self, count: Optional[int] = None) -> List[Tuple[str, int]]:
        """
        Get recently used tiles.

        Args:
            count: Maximum number of tiles to return (None for all)

        Returns:
            List of (tileset_id, tile_id) tuples
        """
        if count is None:
            return self.recently_used.copy()
        return self.recently_used[:count]

    def add_to_favorites(self, tileset_id: str, tile_id: int):
        """
        Add a tile to favorites.

        Args:
            tileset_id: Tileset identifier
            tile_id: Tile identifier
        """
        self.favorites.add((tileset_id, tile_id))

    def remove_from_favorites(self, tileset_id: str, tile_id: int):
        """
        Remove a tile from favorites.

        Args:
            tileset_id: Tileset identifier
            tile_id: Tile identifier
        """
        tile_ref = (tileset_id, tile_id)
        if tile_ref in self.favorites:
            self.favorites.remove(tile_ref)

    def is_favorite(self, tileset_id: str, tile_id: int) -> bool:
        """
        Check if a tile is in favorites.

        Args:
            tileset_id: Tileset identifier
            tile_id: Tile identifier

        Returns:
            True if in favorites, False otherwise
        """
        return (tileset_id, tile_id) in self.favorites

    def get_favorite_tiles(self) -> List[Tuple[str, int]]:
        """
        Get all favorite tiles.

        Returns:
            List of (tileset_id, tile_id) tuples
        """
        return list(self.favorites)

    def set_tile_metadata(
        self,
        tileset_id: str,
        tile_id: int,
        passable: Optional[bool] = None,
        terrain_tags: Optional[List[str]] = None,
        name: Optional[str] = None,
        custom_properties: Optional[Dict] = None,
    ):
        """
        Set metadata for a tile.

        Args:
            tileset_id: Tileset identifier
            tile_id: Tile identifier
            passable: Passability flag
            terrain_tags: Terrain type tags
            name: Tile name
            custom_properties: Custom key-value properties
        """
        tileset = self.tilesets.get(tileset_id)
        if tileset is None:
            return

        metadata = tileset.get_tile_metadata(tile_id)

        if passable is not None:
            metadata.passable = passable
        if terrain_tags is not None:
            metadata.terrain_tags = terrain_tags
        if name is not None:
            metadata.name = name
        if custom_properties is not None:
            metadata.custom_properties.update(custom_properties)

    def get_tile_metadata(self, tileset_id: str, tile_id: int) -> Optional[TileMetadata]:
        """
        Get metadata for a tile.

        Args:
            tileset_id: Tileset identifier
            tile_id: Tile identifier

        Returns:
            TileMetadata or None if tileset not found
        """
        tileset = self.tilesets.get(tileset_id)
        if tileset is None:
            return None
        return tileset.get_tile_metadata(tile_id)

    def save_to_file(self, filepath: str):
        """
        Save tileset configuration to JSON file.

        Args:
            filepath: Path to save file
        """
        data = {
            "active_tileset_id": self.active_tileset_id,
            "max_recent_tiles": self.max_recent_tiles,
            "tilesets": {
                tileset_id: tileset.to_dict() for tileset_id, tileset in self.tilesets.items()
            },
            "recently_used": [
                {"tileset_id": ts_id, "tile_id": tile_id} for ts_id, tile_id in self.recently_used
            ],
            "favorites": [
                {"tileset_id": ts_id, "tile_id": tile_id} for ts_id, tile_id in self.favorites
            ],
        }

        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def load_from_file(self, filepath: str) -> bool:
        """
        Load tileset configuration from JSON file.

        Args:
            filepath: Path to load file

        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            with open(filepath, "r") as f:
                data = json.load(f)

            self.active_tileset_id = data.get("active_tileset_id")
            self.max_recent_tiles = data.get("max_recent_tiles", 20)

            # Load tilesets
            self.tilesets.clear()
            for tileset_id, tileset_data in data.get("tilesets", {}).items():
                tileset = TilesetInfo.from_dict(tileset_data)
                self.tilesets[tileset_id] = tileset

            # Load recently used
            self.recently_used = [
                (item["tileset_id"], item["tile_id"]) for item in data.get("recently_used", [])
            ]

            # Load favorites
            self.favorites = {
                (item["tileset_id"], item["tile_id"]) for item in data.get("favorites", [])
            }

            return True

        except Exception as e:
            print(f"Error loading tileset configuration: {e}")
            return False

    def create_default_tileset(
        self, image_path: str, name: str = "Default Tileset"
    ) -> Optional[TilesetInfo]:
        """
        Create a default tileset with automatic configuration.

        Args:
            image_path: Path to tileset image
            name: Display name for tileset

        Returns:
            Created TilesetInfo or None on error
        """
        try:
            tileset_id = f"tileset_{len(self.tilesets)}"
            tileset = self.add_tileset(
                tileset_id=tileset_id,
                name=name,
                image_path=image_path,
            )
            self.load_tileset(tileset_id)
            return tileset
        except Exception as e:
            print(f"Error creating default tileset: {e}")
            return None


# Global singleton instance
_tileset_manager: Optional[TilesetManager] = None


def get_tileset_manager(project_path: Optional[str] = None) -> TilesetManager:
    """
    Get the global tileset manager instance.

    Args:
        project_path: Path to project directory (only used on first call)

    Returns:
        TilesetManager singleton
    """
    global _tileset_manager
    if _tileset_manager is None:
        _tileset_manager = TilesetManager(project_path)
    return _tileset_manager


def reset_tileset_manager():
    """Reset the global tileset manager (useful for testing)."""
    global _tileset_manager
    _tileset_manager = None
