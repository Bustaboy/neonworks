"""
Tests for the tileset manager system.

Author: NeonWorks Team
Version: 0.1.0
"""

import os
import tempfile
from pathlib import Path

import pygame
import pytest

from neonworks.data.tileset_manager import (
    TileMetadata,
    TilesetInfo,
    TilesetManager,
    reset_tileset_manager,
)


@pytest.fixture(scope="session")
def pygame_display():
    """Initialize pygame display for testing (headless mode)."""
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    yield screen
    pygame.quit()


@pytest.fixture
def temp_tileset_image(pygame_display):
    """Create a temporary tileset image for testing."""
    # Create a simple 2x2 tileset (64x64 pixels, 32x32 tiles)
    surface = pygame.Surface((64, 64))
    # Fill with different colors for each tile
    pygame.draw.rect(surface, (255, 0, 0), (0, 0, 32, 32))  # Red
    pygame.draw.rect(surface, (0, 255, 0), (32, 0, 32, 32))  # Green
    pygame.draw.rect(surface, (0, 0, 255), (0, 32, 32, 32))  # Blue
    pygame.draw.rect(surface, (255, 255, 0), (32, 32, 32, 32))  # Yellow

    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    pygame.image.save(surface, temp_file.name)
    temp_file.close()

    yield temp_file.name

    # Cleanup
    os.unlink(temp_file.name)


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup is handled by tempfile


@pytest.fixture
def tileset_manager(temp_project_dir):
    """Create a fresh tileset manager for each test."""
    reset_tileset_manager()
    manager = TilesetManager(temp_project_dir)
    yield manager
    reset_tileset_manager()


class TestTileMetadata:
    """Test suite for TileMetadata class."""

    def test_create_default_metadata(self):
        """Test creating metadata with default values."""
        metadata = TileMetadata(tile_id=0)

        assert metadata.tile_id == 0
        assert metadata.passable is True
        assert metadata.terrain_tags == []
        assert metadata.animation_frames == []
        assert metadata.animation_speed == 0.0
        assert metadata.name == ""
        assert metadata.custom_properties == {}

    def test_create_metadata_with_values(self):
        """Test creating metadata with custom values."""
        metadata = TileMetadata(
            tile_id=5,
            passable=False,
            terrain_tags=["water", "deep"],
            animation_frames=[5, 6, 7],
            animation_speed=8.0,
            name="Deep Water",
            custom_properties={"damage": 10},
        )

        assert metadata.tile_id == 5
        assert metadata.passable is False
        assert metadata.terrain_tags == ["water", "deep"]
        assert metadata.animation_frames == [5, 6, 7]
        assert metadata.animation_speed == 8.0
        assert metadata.name == "Deep Water"
        assert metadata.custom_properties == {"damage": 10}

    def test_metadata_to_dict(self):
        """Test serializing metadata to dictionary."""
        metadata = TileMetadata(
            tile_id=3, passable=False, terrain_tags=["grass"], name="Grass Tile"
        )

        data = metadata.to_dict()

        assert data["tile_id"] == 3
        assert data["passable"] is False
        assert data["terrain_tags"] == ["grass"]
        assert data["name"] == "Grass Tile"

    def test_metadata_from_dict(self):
        """Test deserializing metadata from dictionary."""
        data = {
            "tile_id": 10,
            "passable": False,
            "terrain_tags": ["lava"],
            "name": "Lava",
            "custom_properties": {"damage": 50},
        }

        metadata = TileMetadata.from_dict(data)

        assert metadata.tile_id == 10
        assert metadata.passable is False
        assert metadata.terrain_tags == ["lava"]
        assert metadata.name == "Lava"
        assert metadata.custom_properties == {"damage": 50}


class TestTilesetInfo:
    """Test suite for TilesetInfo class."""

    def test_create_tileset_info(self):
        """Test creating a TilesetInfo object."""
        tileset = TilesetInfo(
            tileset_id="test_tileset",
            name="Test Tileset",
            image_path="assets/tileset.png",
            tile_width=16,
            tile_height=16,
            columns=8,
            rows=8,
        )

        assert tileset.tileset_id == "test_tileset"
        assert tileset.name == "Test Tileset"
        assert tileset.image_path == "assets/tileset.png"
        assert tileset.tile_width == 16
        assert tileset.tile_height == 16
        assert tileset.columns == 8
        assert tileset.rows == 8

    def test_get_tile_metadata(self):
        """Test getting metadata for a tile."""
        tileset = TilesetInfo(tileset_id="test", name="Test", image_path="test.png")

        # Should create default metadata if not exists
        metadata = tileset.get_tile_metadata(5)
        assert metadata.tile_id == 5
        assert metadata.passable is True

    def test_is_tile_passable(self):
        """Test checking if a tile is passable."""
        tileset = TilesetInfo(tileset_id="test", name="Test", image_path="test.png")

        # Default tiles should be passable
        assert tileset.is_tile_passable(0) is True

        # Set a tile as non-passable
        tileset.metadata[1] = TileMetadata(tile_id=1, passable=False)
        assert tileset.is_tile_passable(1) is False

    def test_get_tile_terrain_tags(self):
        """Test getting terrain tags for a tile."""
        tileset = TilesetInfo(tileset_id="test", name="Test", image_path="test.png")

        # Default tiles should have no tags
        assert tileset.get_tile_terrain_tags(0) == []

        # Set terrain tags
        tileset.metadata[2] = TileMetadata(tile_id=2, terrain_tags=["water", "deep"])
        assert tileset.get_tile_terrain_tags(2) == ["water", "deep"]

    def test_tileset_to_dict(self):
        """Test serializing tileset to dictionary."""
        tileset = TilesetInfo(
            tileset_id="test_tileset",
            name="Test Tileset",
            image_path="assets/tileset.png",
            tile_width=32,
            tile_height=32,
        )
        tileset.metadata[0] = TileMetadata(tile_id=0, passable=False)

        data = tileset.to_dict()

        assert data["tileset_id"] == "test_tileset"
        assert data["name"] == "Test Tileset"
        assert data["image_path"] == "assets/tileset.png"
        assert 0 in data["metadata"]

    def test_tileset_from_dict(self):
        """Test deserializing tileset from dictionary."""
        data = {
            "tileset_id": "test_tileset",
            "name": "Test Tileset",
            "image_path": "assets/tileset.png",
            "tile_width": 32,
            "tile_height": 32,
            "metadata": {"0": {"tile_id": 0, "passable": False, "name": "Wall"}},
        }

        tileset = TilesetInfo.from_dict(data)

        assert tileset.tileset_id == "test_tileset"
        assert tileset.name == "Test Tileset"
        assert 0 in tileset.metadata
        assert tileset.metadata[0].passable is False


class TestTilesetManager:
    """Test suite for TilesetManager class."""

    def test_create_manager(self, tileset_manager):
        """Test creating a tileset manager."""
        assert tileset_manager is not None
        assert len(tileset_manager.tilesets) == 0
        assert tileset_manager.active_tileset_id is None

    def test_add_tileset(self, tileset_manager, temp_tileset_image):
        """Test adding a tileset to the manager."""
        tileset = tileset_manager.add_tileset(
            tileset_id="test_tileset",
            name="Test Tileset",
            image_path=temp_tileset_image,
            tile_width=32,
            tile_height=32,
        )

        assert tileset is not None
        assert tileset_manager.active_tileset_id == "test_tileset"
        assert "test_tileset" in tileset_manager.tilesets

    def test_add_duplicate_tileset_fails(self, tileset_manager, temp_tileset_image):
        """Test that adding a duplicate tileset raises an error."""
        tileset_manager.add_tileset(
            tileset_id="test_tileset",
            name="Test Tileset",
            image_path=temp_tileset_image,
        )

        with pytest.raises(ValueError):
            tileset_manager.add_tileset(
                tileset_id="test_tileset",
                name="Duplicate",
                image_path=temp_tileset_image,
            )

    def test_add_tileset_nonexistent_file_fails(self, tileset_manager):
        """Test that adding a tileset with a non-existent file raises an error."""
        with pytest.raises(FileNotFoundError):
            tileset_manager.add_tileset(
                tileset_id="test_tileset",
                name="Test Tileset",
                image_path="nonexistent.png",
            )

    def test_remove_tileset(self, tileset_manager, temp_tileset_image):
        """Test removing a tileset from the manager."""
        tileset_manager.add_tileset(
            tileset_id="test_tileset",
            name="Test Tileset",
            image_path=temp_tileset_image,
        )

        result = tileset_manager.remove_tileset("test_tileset")

        assert result is True
        assert "test_tileset" not in tileset_manager.tilesets
        assert tileset_manager.active_tileset_id is None

    def test_remove_nonexistent_tileset(self, tileset_manager):
        """Test removing a tileset that doesn't exist."""
        result = tileset_manager.remove_tileset("nonexistent")
        assert result is False

    def test_load_tileset(self, tileset_manager, temp_tileset_image):
        """Test loading a tileset image and parsing tiles."""
        tileset_manager.add_tileset(
            tileset_id="test_tileset",
            name="Test Tileset",
            image_path=temp_tileset_image,
            tile_width=32,
            tile_height=32,
        )

        result = tileset_manager.load_tileset("test_tileset")

        assert result is True
        tileset = tileset_manager.get_tileset("test_tileset")
        assert tileset.surface is not None
        assert len(tileset.tiles) == 4  # 2x2 tileset
        assert tileset.columns == 2
        assert tileset.rows == 2

    def test_get_tileset(self, tileset_manager, temp_tileset_image):
        """Test getting a tileset by ID."""
        tileset_manager.add_tileset(
            tileset_id="test_tileset",
            name="Test Tileset",
            image_path=temp_tileset_image,
        )

        tileset = tileset_manager.get_tileset("test_tileset")

        assert tileset is not None
        assert tileset.tileset_id == "test_tileset"

    def test_get_nonexistent_tileset(self, tileset_manager):
        """Test getting a tileset that doesn't exist."""
        tileset = tileset_manager.get_tileset("nonexistent")
        assert tileset is None

    def test_get_active_tileset(self, tileset_manager, temp_tileset_image):
        """Test getting the active tileset."""
        tileset_manager.add_tileset(
            tileset_id="test_tileset",
            name="Test Tileset",
            image_path=temp_tileset_image,
        )

        active = tileset_manager.get_active_tileset()

        assert active is not None
        assert active.tileset_id == "test_tileset"

    def test_set_active_tileset(self, tileset_manager, temp_tileset_image):
        """Test setting the active tileset."""
        tileset_manager.add_tileset(
            tileset_id="tileset1",
            name="Tileset 1",
            image_path=temp_tileset_image,
        )
        tileset_manager.add_tileset(
            tileset_id="tileset2",
            name="Tileset 2",
            image_path=temp_tileset_image,
        )

        result = tileset_manager.set_active_tileset("tileset2")

        assert result is True
        assert tileset_manager.active_tileset_id == "tileset2"

    def test_get_tile_surface(self, tileset_manager, temp_tileset_image):
        """Test getting a tile surface from a tileset."""
        tileset_manager.add_tileset(
            tileset_id="test_tileset",
            name="Test Tileset",
            image_path=temp_tileset_image,
            tile_width=32,
            tile_height=32,
        )

        tile_surface = tileset_manager.get_tile_surface("test_tileset", 0)

        assert tile_surface is not None
        assert tile_surface.get_width() == 32
        assert tile_surface.get_height() == 32

    def test_recently_used_tiles(self, tileset_manager, temp_tileset_image):
        """Test recently used tiles tracking."""
        tileset_manager.add_tileset(
            tileset_id="test_tileset",
            name="Test Tileset",
            image_path=temp_tileset_image,
        )

        # Add some tiles to recent
        tileset_manager.add_to_recent("test_tileset", 0)
        tileset_manager.add_to_recent("test_tileset", 1)
        tileset_manager.add_to_recent("test_tileset", 2)

        recent = tileset_manager.get_recent_tiles()

        assert len(recent) == 3
        assert recent[0] == ("test_tileset", 2)  # Most recent first
        assert recent[1] == ("test_tileset", 1)
        assert recent[2] == ("test_tileset", 0)

    def test_recently_used_tiles_limit(self, tileset_manager, temp_tileset_image):
        """Test that recently used tiles respects max limit."""
        tileset_manager.add_tileset(
            tileset_id="test_tileset",
            name="Test Tileset",
            image_path=temp_tileset_image,
        )
        tileset_manager.max_recent_tiles = 5

        # Add more tiles than the limit
        for i in range(10):
            tileset_manager.add_to_recent("test_tileset", i)

        recent = tileset_manager.get_recent_tiles()

        assert len(recent) == 5  # Should be limited to max_recent_tiles

    def test_favorite_tiles(self, tileset_manager, temp_tileset_image):
        """Test favorite tiles functionality."""
        tileset_manager.add_tileset(
            tileset_id="test_tileset",
            name="Test Tileset",
            image_path=temp_tileset_image,
        )

        # Add favorites
        tileset_manager.add_to_favorites("test_tileset", 0)
        tileset_manager.add_to_favorites("test_tileset", 2)

        favorites = tileset_manager.get_favorite_tiles()

        assert len(favorites) == 2
        assert ("test_tileset", 0) in favorites
        assert ("test_tileset", 2) in favorites

    def test_remove_favorite(self, tileset_manager, temp_tileset_image):
        """Test removing a tile from favorites."""
        tileset_manager.add_tileset(
            tileset_id="test_tileset",
            name="Test Tileset",
            image_path=temp_tileset_image,
        )

        tileset_manager.add_to_favorites("test_tileset", 0)
        tileset_manager.remove_from_favorites("test_tileset", 0)

        favorites = tileset_manager.get_favorite_tiles()
        assert len(favorites) == 0

    def test_is_favorite(self, tileset_manager, temp_tileset_image):
        """Test checking if a tile is favorited."""
        tileset_manager.add_tileset(
            tileset_id="test_tileset",
            name="Test Tileset",
            image_path=temp_tileset_image,
        )

        tileset_manager.add_to_favorites("test_tileset", 0)

        assert tileset_manager.is_favorite("test_tileset", 0) is True
        assert tileset_manager.is_favorite("test_tileset", 1) is False

    def test_set_tile_metadata(self, tileset_manager, temp_tileset_image):
        """Test setting metadata for a tile."""
        tileset_manager.add_tileset(
            tileset_id="test_tileset",
            name="Test Tileset",
            image_path=temp_tileset_image,
        )

        tileset_manager.set_tile_metadata(
            tileset_id="test_tileset",
            tile_id=0,
            passable=False,
            terrain_tags=["wall"],
            name="Wall Tile",
        )

        metadata = tileset_manager.get_tile_metadata("test_tileset", 0)

        assert metadata.passable is False
        assert metadata.terrain_tags == ["wall"]
        assert metadata.name == "Wall Tile"

    def test_save_and_load_configuration(
        self, tileset_manager, temp_tileset_image, temp_project_dir
    ):
        """Test saving and loading tileset configuration."""
        # Setup tilesets
        tileset_manager.add_tileset(
            tileset_id="test_tileset",
            name="Test Tileset",
            image_path=temp_tileset_image,
        )
        tileset_manager.add_to_favorites("test_tileset", 0)
        tileset_manager.add_to_recent("test_tileset", 1)
        tileset_manager.set_tile_metadata("test_tileset", 0, passable=False, terrain_tags=["wall"])

        # Save configuration
        config_path = os.path.join(temp_project_dir, "tilesets.json")
        tileset_manager.save_to_file(config_path)

        # Create new manager and load configuration
        reset_tileset_manager()
        new_manager = TilesetManager(temp_project_dir)
        result = new_manager.load_from_file(config_path)

        assert result is True
        assert "test_tileset" in new_manager.tilesets
        assert new_manager.is_favorite("test_tileset", 0) is True
        assert len(new_manager.get_recent_tiles()) > 0

        # Check metadata was preserved
        tileset = new_manager.get_tileset("test_tileset")
        assert 0 in tileset.metadata
        assert tileset.metadata[0].passable is False

    def test_create_default_tileset(self, tileset_manager, temp_tileset_image):
        """Test creating a default tileset with automatic configuration."""
        tileset = tileset_manager.create_default_tileset(
            image_path=temp_tileset_image, name="Auto Tileset"
        )

        assert tileset is not None
        assert tileset.name == "Auto Tileset"
        assert len(tileset.tiles) == 4  # 2x2 tileset loaded automatically


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
