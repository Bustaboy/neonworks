"""
Tests for Enhanced Tilemap Integration

Tests the integration between enhanced layer system and tilemap rendering.
"""

from unittest.mock import Mock

import pygame
import pytest

from neonworks.data.map_layers import LayerType, ParallaxMode
from neonworks.rendering.assets import AssetManager
from neonworks.rendering.camera import Camera
from neonworks.rendering.tilemap import (
    Tilemap,
    TilemapBuilder,
    TilemapRenderer,
    Tileset,
)


@pytest.fixture
def asset_manager():
    """Create a mock asset manager"""
    manager = Mock(spec=AssetManager)
    test_surface = pygame.Surface((64, 64), pygame.SRCALPHA)
    test_surface.fill((255, 0, 0))
    manager.load_sprite.return_value = test_surface
    return manager


@pytest.fixture
def camera():
    """Create a camera for testing"""
    return Camera(screen_width=800, screen_height=600)


class TestEnhancedTilemap:
    """Test enhanced tilemap features"""

    def test_create_enhanced_tilemap_default(self):
        """Test creating enhanced tilemap uses new system by default"""
        tilemap = Tilemap(50, 50, 32, 32)

        assert tilemap.use_enhanced_layers
        assert hasattr(tilemap, "layer_manager")
        assert tilemap.layer_manager is not None

    def test_create_enhanced_layer(self):
        """Test creating enhanced layer"""
        tilemap = Tilemap(50, 50, 32, 32)

        layer_id = tilemap.create_enhanced_layer("Test Layer", opacity=0.8)

        assert layer_id is not None
        layer = tilemap.get_enhanced_layer(layer_id)
        assert layer is not None
        assert layer.properties.name == "Test Layer"
        assert layer.properties.opacity == 0.8

    def test_create_parallax_background(self):
        """Test creating parallax background layer"""
        tilemap = Tilemap(50, 50, 32, 32)

        layer_id = tilemap.create_parallax_background(
            "Sky", parallax_x=0.5, parallax_y=0.5, auto_scroll_x=10.0
        )

        layer = tilemap.get_enhanced_layer(layer_id)
        assert layer.properties.layer_type == LayerType.PARALLAX_BACKGROUND
        assert layer.properties.parallax_x == 0.5
        assert layer.properties.parallax_mode == ParallaxMode.AUTO_SCROLL
        assert layer.properties.auto_scroll_x == 10.0

    def test_remove_layer(self):
        """Test removing a layer"""
        tilemap = Tilemap(50, 50, 32, 32)

        layer_id = tilemap.create_enhanced_layer("To Remove")
        assert tilemap.get_enhanced_layer(layer_id) is not None

        result = tilemap.remove_layer(layer_id)

        assert result is True
        assert tilemap.get_enhanced_layer(layer_id) is None

    def test_reorder_layer(self):
        """Test reordering layers"""
        tilemap = Tilemap(50, 50, 32, 32)

        layer1_id = tilemap.create_enhanced_layer("Layer 1")
        layer2_id = tilemap.create_enhanced_layer("Layer 2")
        layer3_id = tilemap.create_enhanced_layer("Layer 3")

        # Move layer 3 to bottom
        tilemap.reorder_layer(layer3_id, 0)

        render_order = tilemap.layer_manager.get_render_order()
        assert render_order[0] == layer3_id
        assert render_order[1] == layer1_id
        assert render_order[2] == layer2_id

    def test_duplicate_layer(self):
        """Test duplicating a layer"""
        tilemap = Tilemap(10, 10, 32, 32)

        layer_id = tilemap.create_enhanced_layer("Original")
        layer = tilemap.get_enhanced_layer(layer_id)
        layer.set_tile(5, 5, 42)

        new_id = tilemap.duplicate_layer(layer_id, "Duplicate")

        assert new_id is not None
        new_layer = tilemap.get_enhanced_layer(new_id)
        assert new_layer.properties.name == "Duplicate"
        assert new_layer.get_tile(5, 5) == 42

    def test_merge_layers(self):
        """Test merging layers"""
        tilemap = Tilemap(10, 10, 32, 32)

        layer1_id = tilemap.create_enhanced_layer("Layer 1")
        layer2_id = tilemap.create_enhanced_layer("Layer 2")

        layer1 = tilemap.get_enhanced_layer(layer1_id)
        layer2 = tilemap.get_enhanced_layer(layer2_id)

        layer1.set_tile(0, 0, 1)
        layer1.set_tile(5, 5, 2)
        layer2.set_tile(5, 5, 3)
        layer2.set_tile(9, 9, 4)

        merged_id = tilemap.merge_layers([layer1_id, layer2_id], "Merged")

        merged = tilemap.get_enhanced_layer(merged_id)
        assert merged.get_tile(0, 0) == 1
        assert merged.get_tile(5, 5) == 3  # Layer 2 wins
        assert merged.get_tile(9, 9) == 4

    def test_create_layer_group(self):
        """Test creating layer group"""
        tilemap = Tilemap(50, 50, 32, 32)

        group_id = tilemap.create_layer_group("Background")

        assert group_id is not None
        group = tilemap.layer_manager.get_group(group_id)
        assert group.name == "Background"

    def test_get_enhanced_layer_by_name(self):
        """Test getting enhanced layer by name"""
        tilemap = Tilemap(50, 50, 32, 32)

        tilemap.create_enhanced_layer("Ground")
        tilemap.create_enhanced_layer("Objects")

        layer = tilemap.get_enhanced_layer_by_name("Objects")
        assert layer is not None
        assert layer.properties.name == "Objects"

    def test_update_auto_scroll(self):
        """Test tilemap update for auto-scroll"""
        tilemap = Tilemap(50, 50, 32, 32)

        layer_id = tilemap.create_parallax_background(
            "Clouds", auto_scroll_x=10.0, auto_scroll_y=5.0
        )

        layer = tilemap.get_enhanced_layer(layer_id)
        initial_offset = layer.get_effective_offset()

        tilemap.update(1.0)  # 1 second

        new_offset = layer.get_effective_offset()
        assert new_offset[0] == initial_offset[0] + 10.0
        assert new_offset[1] == initial_offset[1] + 5.0

    def test_get_layer_by_name_enhanced(self):
        """Test get_layer_by_name with enhanced layers"""
        tilemap = Tilemap(50, 50, 32, 32)

        tilemap.create_enhanced_layer("Test Layer")

        layer = tilemap.get_enhanced_layer_by_name("Test Layer")
        assert layer is not None
        assert layer.properties.name == "Test Layer"


class TestEnhancedRendering:
    """Test enhanced layer rendering"""

    def test_render_enhanced_tilemap(self, asset_manager, camera):
        """Test rendering enhanced tilemap"""
        renderer = TilemapRenderer(asset_manager)
        tilemap = Tilemap(10, 10, 32, 32)

        # Create tileset
        tileset = Tileset(
            name="tiles",
            texture_path="tileset.png",
            tile_width=32,
            tile_height=32,
            columns=2,
            tile_count=4,
        )
        tilemap.add_tileset(tileset)

        # Create layer with tiles
        layer_id = tilemap.create_enhanced_layer("Ground")
        layer = tilemap.get_enhanced_layer(layer_id)
        layer.fill(1)

        screen = pygame.Surface((800, 600))
        renderer.render(screen, tilemap, camera)

        stats = renderer.get_stats()
        assert stats["tiles_rendered"] > 0
        assert stats["layers_rendered"] == 1

    def test_render_invisible_enhanced_layer(self, asset_manager, camera):
        """Test invisible enhanced layers are not rendered"""
        renderer = TilemapRenderer(asset_manager)
        tilemap = Tilemap(10, 10, 32, 32)

        tileset = Tileset(
            name="tiles",
            texture_path="tileset.png",
            tile_width=32,
            tile_height=32,
            columns=2,
            tile_count=4,
        )
        tilemap.add_tileset(tileset)

        layer_id = tilemap.create_enhanced_layer("Ground")
        layer = tilemap.get_enhanced_layer(layer_id)
        layer.fill(1)
        layer.properties.visible = False

        screen = pygame.Surface((800, 600))
        renderer.render(screen, tilemap, camera)

        stats = renderer.get_stats()
        assert stats["tiles_rendered"] == 0
        assert stats["layers_rendered"] == 0

    def test_render_collision_layer_not_visible(self, asset_manager, camera):
        """Test collision layers are not rendered"""
        renderer = TilemapRenderer(asset_manager)
        tilemap = Tilemap(10, 10, 32, 32)

        tileset = Tileset(
            name="tiles",
            texture_path="tileset.png",
            tile_width=32,
            tile_height=32,
            columns=2,
            tile_count=4,
        )
        tilemap.add_tileset(tileset)

        layer_id = tilemap.create_enhanced_layer("Collision", layer_type=LayerType.COLLISION)
        layer = tilemap.get_enhanced_layer(layer_id)
        layer.fill(1)

        screen = pygame.Surface((800, 600))
        renderer.render(screen, tilemap, camera)

        stats = renderer.get_stats()
        assert stats["tiles_rendered"] == 0

    def test_render_multiple_enhanced_layers(self, asset_manager, camera):
        """Test rendering multiple enhanced layers"""
        renderer = TilemapRenderer(asset_manager)
        tilemap = Tilemap(10, 10, 32, 32)

        tileset = Tileset(
            name="tiles",
            texture_path="tileset.png",
            tile_width=32,
            tile_height=32,
            columns=2,
            tile_count=4,
        )
        tilemap.add_tileset(tileset)

        # Create multiple layers
        for i in range(3):
            layer_id = tilemap.create_enhanced_layer(f"Layer {i}")
            layer = tilemap.get_enhanced_layer(layer_id)
            layer.fill(1)

        screen = pygame.Surface((800, 600))
        renderer.render(screen, tilemap, camera)

        stats = renderer.get_stats()
        assert stats["layers_rendered"] == 3

    def test_render_with_opacity(self, asset_manager, camera):
        """Test rendering layer with opacity"""
        renderer = TilemapRenderer(asset_manager)
        tilemap = Tilemap(10, 10, 32, 32)

        tileset = Tileset(
            name="tiles",
            texture_path="tileset.png",
            tile_width=32,
            tile_height=32,
            columns=2,
            tile_count=4,
        )
        tilemap.add_tileset(tileset)

        layer_id = tilemap.create_enhanced_layer("Ground", opacity=0.5)
        layer = tilemap.get_enhanced_layer(layer_id)
        layer.fill(1)

        screen = pygame.Surface((800, 600))
        renderer.render(screen, tilemap, camera)

        stats = renderer.get_stats()
        assert stats["tiles_rendered"] > 0

    def test_render_with_auto_scroll(self, asset_manager, camera):
        """Test rendering auto-scroll layer"""
        renderer = TilemapRenderer(asset_manager)
        tilemap = Tilemap(10, 10, 32, 32)

        tileset = Tileset(
            name="tiles",
            texture_path="tileset.png",
            tile_width=32,
            tile_height=32,
            columns=2,
            tile_count=4,
        )
        tilemap.add_tileset(tileset)

        layer_id = tilemap.create_parallax_background("Sky", auto_scroll_x=10.0)
        layer = tilemap.get_enhanced_layer(layer_id)
        layer.fill(1)

        # Update to trigger scroll
        tilemap.update(1.0)

        screen = pygame.Surface((800, 600))
        renderer.render(screen, tilemap, camera)

        stats = renderer.get_stats()
        assert stats["tiles_rendered"] > 0


class TestTilemapBuilder:
    """Test tilemap builder with enhanced layers"""

    def test_create_simple_tilemap_enhanced(self):
        """Test creating simple enhanced tilemap"""
        tilemap = TilemapBuilder.create_simple_tilemap(20, 15, use_enhanced=True)

        assert tilemap.use_enhanced_layers
        assert len(tilemap.layer_manager.layers) == 1

        ground = tilemap.get_enhanced_layer_by_name("Ground")
        assert ground is not None

    def test_create_layered_tilemap_enhanced(self):
        """Test creating layered enhanced tilemap"""
        layer_names = ["Ground", "Objects", "Overlay"]
        tilemap = TilemapBuilder.create_layered_tilemap(
            10, 10, layer_names=layer_names, use_enhanced=True
        )

        assert tilemap.use_enhanced_layers
        assert len(tilemap.layer_manager.layers) == 3

        for name in layer_names:
            layer = tilemap.get_enhanced_layer_by_name(name)
            assert layer is not None

    def test_create_parallax_scene(self):
        """Test creating parallax scene"""
        tilemap = TilemapBuilder.create_parallax_scene(50, 50)

        assert tilemap.use_enhanced_layers
        assert len(tilemap.layer_manager.layers) >= 5

        # Check for parallax layers
        far_bg = tilemap.get_enhanced_layer_by_name("Far Background")
        assert far_bg is not None
        assert far_bg.properties.parallax_x == 0.3

        # Check for foreground
        fg = tilemap.get_enhanced_layer_by_name("Foreground")
        assert fg is not None
        assert fg.properties.layer_type == LayerType.PARALLAX_FOREGROUND
        assert fg.properties.parallax_x == 1.2


class TestEnhancedLayerOperations:
    """Test enhanced layer operations on tilemap"""

    def test_enhanced_layer_operations(self):
        tilemap = Tilemap(10, 10, 32, 32)
        layer_id = tilemap.create_enhanced_layer("Test")
        assert layer_id is not None
        assert tilemap.reorder_layer(layer_id, 0) is True
        assert tilemap.duplicate_layer(layer_id) is not None
        assert tilemap.remove_layer(layer_id) is True

