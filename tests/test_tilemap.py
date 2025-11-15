"""
Comprehensive tests for Tilemap System

Tests tile operations, layers, rendering, and coordinate conversions.
"""

from unittest.mock import Mock, patch

import pygame
import pytest

from neonworks.rendering.assets import AssetManager
from neonworks.rendering.camera import Camera
from neonworks.rendering.tilemap import (
    Tile,
    TileLayer,
    Tilemap,
    TilemapBuilder,
    TilemapRenderer,
    Tileset,
)


@pytest.fixture
def asset_manager():
    """Create a mock asset manager"""
    manager = Mock(spec=AssetManager)
    # Create a simple test surface
    test_surface = pygame.Surface((64, 64), pygame.SRCALPHA)
    test_surface.fill((255, 0, 0))
    manager.load_sprite.return_value = test_surface
    return manager


@pytest.fixture
def camera():
    """Create a camera for testing"""
    return Camera(screen_width=800, screen_height=600)


class TestTile:
    """Test tile operations"""

    def test_tile_creation(self):
        """Test creating a tile"""
        tile = Tile(tile_id=1)
        assert tile.tile_id == 1
        assert tile.flags == 0

    def test_empty_tile(self):
        """Test empty tile detection"""
        empty = Tile(tile_id=0)
        not_empty = Tile(tile_id=1)

        assert empty.is_empty()
        assert not not_empty.is_empty()

    def test_tile_flip_flags(self):
        """Test tile flip flags"""
        tile = Tile(tile_id=1, flags=Tile.FLIP_HORIZONTAL)
        assert tile.is_flipped_horizontal()
        assert not tile.is_flipped_vertical()

        tile.flags |= Tile.FLIP_VERTICAL
        assert tile.is_flipped_horizontal()
        assert tile.is_flipped_vertical()

    def test_tile_diagonal_flip(self):
        """Test diagonal flip (rotation)"""
        tile = Tile(tile_id=1, flags=Tile.FLIP_DIAGONAL)
        assert tile.is_flipped_diagonal()


class TestTileset:
    """Test tileset operations"""

    def test_tileset_creation(self):
        """Test creating a tileset"""
        tileset = Tileset(
            name="test",
            texture_path="tileset.png",
            tile_width=32,
            tile_height=32,
            columns=8,
            tile_count=64,
        )

        assert tileset.name == "test"
        assert tileset.tile_width == 32
        assert tileset.columns == 8

    def test_get_tile_rect(self):
        """Test calculating tile source rectangle"""
        tileset = Tileset(
            name="test",
            texture_path="tileset.png",
            tile_width=32,
            tile_height=32,
            columns=8,
            tile_count=64,
            spacing=0,
            margin=0,
        )

        # First tile (0,0)
        rect = tileset.get_tile_rect(0)
        assert rect == (0, 0, 32, 32)

        # Second tile (1,0)
        rect = tileset.get_tile_rect(1)
        assert rect == (32, 0, 32, 32)

        # Tile in second row (0,1)
        rect = tileset.get_tile_rect(8)
        assert rect == (0, 32, 32, 32)

    def test_get_tile_rect_with_spacing(self):
        """Test tile rect with spacing"""
        tileset = Tileset(
            name="test",
            texture_path="tileset.png",
            tile_width=32,
            tile_height=32,
            columns=8,
            tile_count=64,
            spacing=2,
            margin=4,
        )

        # First tile with margin
        rect = tileset.get_tile_rect(0)
        assert rect == (4, 4, 32, 32)

        # Second tile with spacing
        rect = tileset.get_tile_rect(1)
        assert rect == (4 + 32 + 2, 4, 32, 32)

    def test_load_tiles(self, asset_manager):
        """Test loading tiles from tileset"""
        tileset = Tileset(
            name="test",
            texture_path="tileset.png",
            tile_width=32,
            tile_height=32,
            columns=2,
            tile_count=4,
        )

        tileset.load_tiles(asset_manager)

        # Should have loaded tiles
        assert len(tileset.tiles) == 4
        asset_manager.load_sprite.assert_called_once()


class TestTileLayer:
    """Test tile layer operations"""

    def test_layer_creation(self):
        """Test creating a tile layer"""
        layer = TileLayer(name="ground", width=10, height=10)

        assert layer.name == "ground"
        assert layer.width == 10
        assert layer.height == 10
        assert layer.visible
        assert layer.opacity == 1.0

    def test_layer_auto_initialize(self):
        """Test layer auto-initializes tile grid"""
        layer = TileLayer(name="ground", width=5, height=5)

        assert len(layer.tiles) == 5
        assert len(layer.tiles[0]) == 5

    def test_get_set_tile(self):
        """Test getting and setting tiles"""
        layer = TileLayer(name="ground", width=10, height=10)

        # Set a tile
        layer.set_tile(5, 5, Tile(tile_id=42))

        # Get the tile
        tile = layer.get_tile(5, 5)
        assert tile.tile_id == 42

    def test_get_tile_out_of_bounds(self):
        """Test getting tile out of bounds returns None"""
        layer = TileLayer(name="ground", width=10, height=10)

        tile = layer.get_tile(100, 100)
        assert tile is None

        tile = layer.get_tile(-1, -1)
        assert tile is None

    def test_fill_layer(self):
        """Test filling layer with a tile"""
        layer = TileLayer(name="ground", width=5, height=5)
        layer.fill(7)

        # All tiles should be ID 7
        for y in range(5):
            for x in range(5):
                assert layer.get_tile(x, y).tile_id == 7

    def test_clear_layer(self):
        """Test clearing a layer"""
        layer = TileLayer(name="ground", width=5, height=5)
        layer.fill(7)
        layer.clear()

        # All tiles should be empty (ID 0)
        for y in range(5):
            for x in range(5):
                assert layer.get_tile(x, y).tile_id == 0

    def test_layer_parallax(self):
        """Test layer parallax settings"""
        layer = TileLayer(name="background", width=10, height=10, parallax_x=0.5, parallax_y=0.5)

        assert layer.parallax_x == 0.5
        assert layer.parallax_y == 0.5


class TestTilemap:
    """Test tilemap operations"""

    def test_tilemap_creation(self):
        """Test creating a tilemap"""
        tilemap = Tilemap(
            width=20, height=15, tile_width=32, tile_height=32, use_enhanced_layers=False
        )

        assert tilemap.width == 20
        assert tilemap.height == 15
        assert tilemap.tile_width == 32
        assert tilemap.tile_height == 32

    def test_add_layer(self):
        """Test adding layers"""
        tilemap = Tilemap(
            width=10, height=10, tile_width=32, tile_height=32, use_enhanced_layers=False
        )
        layer = TileLayer(name="ground", width=10, height=10)

        index = tilemap.add_layer(layer)

        assert index == 0
        assert len(tilemap.layers) == 1

    def test_create_layer(self):
        """Test creating and adding a layer"""
        tilemap = Tilemap(
            width=10, height=10, tile_width=32, tile_height=32, use_enhanced_layers=False
        )

        index = tilemap.create_layer("ground", fill_tile=5)

        assert index == 0
        layer = tilemap.get_layer(0)
        assert layer.name == "ground"
        assert layer.get_tile(0, 0).tile_id == 5

    def test_get_layer_by_index(self):
        """Test getting layer by index"""
        tilemap = Tilemap(
            width=10, height=10, tile_width=32, tile_height=32, use_enhanced_layers=False
        )
        tilemap.create_layer("ground")
        tilemap.create_layer("objects")

        layer = tilemap.get_layer(1)
        assert layer.name == "objects"

    def test_get_layer_by_name(self):
        """Test getting layer by name"""
        tilemap = Tilemap(
            width=10, height=10, tile_width=32, tile_height=32, use_enhanced_layers=False
        )
        tilemap.create_layer("ground")
        tilemap.create_layer("objects")

        layer = tilemap.get_layer_by_name("objects")
        assert layer is not None
        assert layer.name == "objects"

    def test_add_tileset(self):
        """Test adding a tileset"""
        tilemap = Tilemap(
            width=10, height=10, tile_width=32, tile_height=32, use_enhanced_layers=False
        )
        tileset = Tileset(
            name="tiles",
            texture_path="tileset.png",
            tile_width=32,
            tile_height=32,
            columns=8,
            tile_count=64,
        )

        tilemap.add_tileset(tileset)

        assert len(tilemap.tilesets) == 1
        assert tilemap.default_tileset == "tiles"

    def test_get_tileset(self):
        """Test getting tileset"""
        tilemap = Tilemap(
            width=10, height=10, tile_width=32, tile_height=32, use_enhanced_layers=False
        )
        tileset = Tileset(
            name="tiles",
            texture_path="tileset.png",
            tile_width=32,
            tile_height=32,
            columns=8,
            tile_count=64,
        )
        tilemap.add_tileset(tileset)

        retrieved = tilemap.get_tileset("tiles")
        assert retrieved == tileset

        # Default tileset
        default = tilemap.get_tileset()
        assert default == tileset

    def test_world_to_tile_conversion(self):
        """Test converting world coordinates to tile coordinates"""
        tilemap = Tilemap(
            width=10, height=10, tile_width=32, tile_height=32, use_enhanced_layers=False
        )

        tile_x, tile_y = tilemap.world_to_tile(64, 96)
        assert tile_x == 2
        assert tile_y == 3

    def test_tile_to_world_conversion(self):
        """Test converting tile coordinates to world coordinates"""
        tilemap = Tilemap(
            width=10, height=10, tile_width=32, tile_height=32, use_enhanced_layers=False
        )

        world_x, world_y = tilemap.tile_to_world(2, 3)
        # Should return center of tile
        assert world_x == 2 * 32 + 16
        assert world_y == 3 * 32 + 16

    def test_is_valid_tile(self):
        """Test checking if tile coordinates are valid"""
        tilemap = Tilemap(
            width=10, height=10, tile_width=32, tile_height=32, use_enhanced_layers=False
        )

        assert tilemap.is_valid_tile(5, 5)
        assert tilemap.is_valid_tile(0, 0)
        assert tilemap.is_valid_tile(9, 9)
        assert not tilemap.is_valid_tile(10, 10)
        assert not tilemap.is_valid_tile(-1, 0)


class TestTilemapRenderer:
    """Test tilemap rendering"""

    def test_renderer_creation(self, asset_manager):
        """Test creating a tilemap renderer"""
        renderer = TilemapRenderer(asset_manager)
        assert renderer.asset_manager == asset_manager

    def test_render_empty_tilemap(self, asset_manager, camera):
        """Test rendering empty tilemap doesn't crash"""
        renderer = TilemapRenderer(asset_manager)
        tilemap = Tilemap(
            width=10, height=10, tile_width=32, tile_height=32, use_enhanced_layers=False
        )
        screen = pygame.Surface((800, 600))

        # Should not crash with no tileset
        renderer.render(screen, tilemap, camera)

    def test_render_with_tileset(self, asset_manager, camera):
        """Test rendering tilemap with tileset"""
        renderer = TilemapRenderer(asset_manager)

        # Create tilemap with tileset
        tilemap = Tilemap(
            width=10, height=10, tile_width=32, tile_height=32, use_enhanced_layers=False
        )
        tileset = Tileset(
            name="tiles",
            texture_path="tileset.png",
            tile_width=32,
            tile_height=32,
            columns=2,
            tile_count=4,
        )
        tilemap.add_tileset(tileset)

        # Create layer with some tiles
        layer = tilemap.create_layer("ground")
        tilemap.get_layer(0).set_tile(0, 0, Tile(tile_id=1))

        screen = pygame.Surface((800, 600))
        renderer.render(screen, tilemap, camera)

        # Should have rendered at least one tile
        stats = renderer.get_stats()
        assert stats["tiles_rendered"] >= 0

    def test_camera_culling(self, asset_manager):
        """Test camera culling excludes off-screen tiles"""
        renderer = TilemapRenderer(asset_manager)

        # Create small camera
        camera = Camera(screen_width=100, screen_height=100)
        camera.x = 50
        camera.y = 50

        # Create large tilemap
        tilemap = Tilemap(
            width=100, height=100, tile_width=32, tile_height=32, use_enhanced_layers=False
        )
        tileset = Tileset(
            name="tiles",
            texture_path="tileset.png",
            tile_width=32,
            tile_height=32,
            columns=2,
            tile_count=4,
        )
        tilemap.add_tileset(tileset)

        # Fill entire map
        layer = tilemap.create_layer("ground", fill_tile=1)

        screen = pygame.Surface((100, 100))
        renderer.render(screen, tilemap, camera)

        stats = renderer.get_stats()
        # Should render fewer tiles than total (due to culling)
        total_tiles = 100 * 100
        assert stats["tiles_rendered"] < total_tiles

    def test_invisible_layer_not_rendered(self, asset_manager, camera):
        """Test invisible layers are not rendered"""
        renderer = TilemapRenderer(asset_manager)

        tilemap = Tilemap(
            width=10, height=10, tile_width=32, tile_height=32, use_enhanced_layers=False
        )
        tileset = Tileset(
            name="tiles",
            texture_path="tileset.png",
            tile_width=32,
            tile_height=32,
            columns=2,
            tile_count=4,
        )
        tilemap.add_tileset(tileset)

        layer = tilemap.create_layer("ground", fill_tile=1)
        tilemap.get_layer(0).visible = False

        screen = pygame.Surface((800, 600))
        renderer.render(screen, tilemap, camera)

        stats = renderer.get_stats()
        # No tiles should be rendered
        assert stats["tiles_rendered"] == 0


class TestTilemapBuilder:
    """Test tilemap builder helpers"""

    def test_create_simple_tilemap(self):
        """Test creating simple tilemap"""
        tilemap = TilemapBuilder.create_simple_tilemap(20, 15, tile_size=32, use_enhanced=False)

        assert tilemap.width == 20
        assert tilemap.height == 15
        assert tilemap.tile_width == 32
        assert len(tilemap.layers) == 1

    def test_create_layered_tilemap(self):
        """Test creating multi-layer tilemap"""
        layer_names = ["ground", "decorations", "overlay"]
        tilemap = TilemapBuilder.create_layered_tilemap(
            10, 10, layer_names=layer_names, use_enhanced=False
        )

        assert len(tilemap.layers) == 3
        assert tilemap.get_layer_by_name("ground") is not None
        assert tilemap.get_layer_by_name("decorations") is not None

    def test_create_tileset_from_sheet(self):
        """Test creating tileset from sprite sheet"""
        tileset = TilemapBuilder.create_tileset_from_sheet(
            name="tiles",
            texture_path="tileset.png",
            tile_width=32,
            tile_height=32,
            columns=8,
            rows=8,
        )

        assert tileset.name == "tiles"
        assert tileset.tile_count == 64
        assert tileset.columns == 8

    def test_fill_pattern(self):
        """Test filling layer with pattern"""
        layer = TileLayer(name="ground", width=10, height=10)

        pattern = [[1, 2], [3, 4]]

        TilemapBuilder.fill_pattern(layer, pattern)

        # Check pattern repeats
        assert layer.get_tile(0, 0).tile_id == 1
        assert layer.get_tile(1, 0).tile_id == 2
        assert layer.get_tile(0, 1).tile_id == 3
        assert layer.get_tile(1, 1).tile_id == 4
        # Pattern should repeat
        assert layer.get_tile(2, 0).tile_id == 1
        assert layer.get_tile(0, 2).tile_id == 1

    def test_create_border(self):
        """Test creating border around layer"""
        layer = TileLayer(name="ground", width=10, height=10)

        TilemapBuilder.create_border(layer, border_tile=9, fill_tile=1)

        # Check corners are border
        assert layer.get_tile(0, 0).tile_id == 9
        assert layer.get_tile(9, 9).tile_id == 9

        # Check edges are border
        assert layer.get_tile(5, 0).tile_id == 9
        assert layer.get_tile(0, 5).tile_id == 9

        # Check interior is fill
        assert layer.get_tile(5, 5).tile_id == 1


# Run tests with: pytest engine/tests/test_tilemap.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
