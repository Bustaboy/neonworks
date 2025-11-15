"""
Tests for AI Layer Generator

Tests automatic layer generation for different game types.
"""

import pytest

from neonworks.data.map_layers import LayerType, ParallaxMode
from neonworks.editor.ai_layer_generator import AILayerGenerator
from neonworks.rendering.tilemap import Tilemap


class TestAILayerGenerator:
    """Test AI layer generation functions"""

    def test_generate_platformer_layers_basic(self):
        """Test generating basic platformer layers without parallax"""
        tilemap = Tilemap(50, 30, 32, 32, use_enhanced_layers=True)

        layer_ids = AILayerGenerator.generate_platformer_layers(
            tilemap, has_parallax=False, depth_layers=0
        )

        # Should have: Ground, Platforms, Decorations, Collision
        assert len(layer_ids) >= 4

        # Verify layers exist
        ground = tilemap.get_enhanced_layer_by_name("Ground")
        assert ground is not None
        assert ground.properties.layer_type == LayerType.STANDARD

        collision = tilemap.get_enhanced_layer_by_name("Collision")
        assert collision is not None
        assert collision.properties.layer_type == LayerType.COLLISION
        assert collision.properties.visible is False

    def test_generate_platformer_layers_with_parallax(self):
        """Test generating platformer with parallax backgrounds"""
        tilemap = Tilemap(50, 30, 32, 32, use_enhanced_layers=True)

        layer_ids = AILayerGenerator.generate_platformer_layers(
            tilemap, has_parallax=True, depth_layers=3
        )

        # Should have: 3 parallax BG + Ground + Platforms + Decorations + Foreground + Collision
        assert len(layer_ids) >= 8

        # Check for parallax layers
        sky = tilemap.get_enhanced_layer_by_name("Sky")
        assert sky is not None
        assert sky.properties.layer_type == LayerType.PARALLAX_BACKGROUND
        assert sky.properties.parallax_x < 1.0  # Background effect

        # Check foreground
        fg = tilemap.get_enhanced_layer_by_name("Foreground")
        assert fg is not None
        assert fg.properties.layer_type == LayerType.PARALLAX_FOREGROUND
        assert fg.properties.parallax_x > 1.0  # Foreground effect
        assert fg.properties.opacity < 1.0

    def test_generate_platformer_layers_depth_limit(self):
        """Test depth layers are limited correctly"""
        tilemap = Tilemap(50, 30, 32, 32, use_enhanced_layers=True)

        # Request more than available
        layer_ids = AILayerGenerator.generate_platformer_layers(
            tilemap, has_parallax=True, depth_layers=10
        )

        # Should not create more than 5 parallax backgrounds
        parallax_layers = [
            lid
            for lid in layer_ids
            if tilemap.get_enhanced_layer(lid)
            and tilemap.get_enhanced_layer(lid).properties.layer_type
            == LayerType.PARALLAX_BACKGROUND
        ]
        assert len(parallax_layers) <= 5

    def test_generate_rpg_layers_organized(self):
        """Test generating organized RPG layers with groups"""
        tilemap = Tilemap(100, 100, 32, 32, use_enhanced_layers=True)

        layer_ids = AILayerGenerator.generate_rpg_layers(tilemap, organized=True)

        # Should have multiple layers
        assert len(layer_ids) > 5

        # Check groups exist
        assert len(tilemap.layer_manager.groups) == 3  # Background, Objects, Overlay

        # Verify layers in groups
        floor = tilemap.get_enhanced_layer_by_name("Floor")
        assert floor is not None
        assert floor.parent_group_id is not None  # In Background group

        roof = tilemap.get_enhanced_layer_by_name("Roof")
        assert roof is not None
        assert roof.properties.opacity == 0.6

    def test_generate_rpg_layers_flat(self):
        """Test generating flat RPG layers without groups"""
        tilemap = Tilemap(100, 100, 32, 32, use_enhanced_layers=True)

        layer_ids = AILayerGenerator.generate_rpg_layers(tilemap, organized=False)

        # Should have layers but no groups
        assert len(layer_ids) > 5
        assert len(tilemap.layer_manager.groups) == 0

        # Verify layers exist at root
        floor = tilemap.get_enhanced_layer_by_name("Floor")
        assert floor is not None
        assert floor.parent_group_id is None  # At root

    def test_generate_space_shooter_layers(self):
        """Test generating space shooter with auto-scrolling stars"""
        tilemap = Tilemap(100, 50, 32, 32, use_enhanced_layers=True)

        layer_ids = AILayerGenerator.generate_space_shooter_layers(tilemap, star_layers=3)

        # Should have: 3 star layers + Game + Effects + UI Overlay
        assert len(layer_ids) >= 6

        # Check auto-scrolling star layers
        distant_stars = tilemap.get_enhanced_layer_by_name("Distant Stars")
        assert distant_stars is not None
        assert distant_stars.properties.parallax_mode == ParallaxMode.AUTO_SCROLL
        assert distant_stars.properties.auto_scroll_y < 0  # Scrolling up

        # Check game layer
        game = tilemap.get_enhanced_layer_by_name("Game")
        assert game is not None
        assert game.properties.layer_type == LayerType.STANDARD

        # Check UI overlay
        ui = tilemap.get_enhanced_layer_by_name("UI Overlay")
        assert ui is not None
        assert ui.properties.layer_type == LayerType.OVERLAY

    def test_generate_space_shooter_star_limit(self):
        """Test star layers are limited correctly"""
        tilemap = Tilemap(100, 50, 32, 32, use_enhanced_layers=True)

        layer_ids = AILayerGenerator.generate_space_shooter_layers(tilemap, star_layers=10)

        # Should not create more than 5 star layers
        star_layers = [
            lid
            for lid in layer_ids
            if tilemap.get_enhanced_layer(lid)
            and "Stars" in tilemap.get_enhanced_layer(lid).properties.name
        ]
        assert len(star_layers) <= 5

    def test_generate_strategy_layers_with_groups(self):
        """Test generating strategy game layers with groups"""
        tilemap = Tilemap(100, 100, 32, 32, use_enhanced_layers=True)

        layer_ids = AILayerGenerator.generate_strategy_layers(tilemap, use_groups=True)

        # Should have multiple layers and groups
        assert len(layer_ids) > 8
        assert len(tilemap.layer_manager.groups) == 3  # Terrain, Structures, Tactical

        # Check terrain layers
        ground = tilemap.get_enhanced_layer_by_name("Ground")
        assert ground is not None
        assert ground.parent_group_id is not None

        # Check tactical overlays
        fog = tilemap.get_enhanced_layer_by_name("Fog of War")
        assert fog is not None
        assert fog.properties.opacity == 0.7

        movement = tilemap.get_enhanced_layer_by_name("Movement Range")
        assert movement is not None
        assert movement.properties.opacity == 0.5

        # Check collision layer
        collision = tilemap.get_enhanced_layer_by_name("Collision")
        assert collision is not None
        assert collision.properties.layer_type == LayerType.COLLISION

    def test_generate_strategy_layers_flat(self):
        """Test generating strategy layers without groups"""
        tilemap = Tilemap(100, 100, 32, 32, use_enhanced_layers=True)

        layer_ids = AILayerGenerator.generate_strategy_layers(tilemap, use_groups=False)

        # Should have layers but no groups (except maybe one for collision)
        assert len(layer_ids) > 8

        # All layers should be at root
        ground = tilemap.get_enhanced_layer_by_name("Ground")
        assert ground is not None
        assert ground.parent_group_id is None

    def test_suggest_layer_optimization_legacy_warning(self):
        """Test optimization suggestions for legacy maps"""
        tilemap = Tilemap(50, 50, 32, 32, use_enhanced_layers=False)

        suggestions = AILayerGenerator.suggest_layer_optimization(tilemap)

        assert len(suggestions) > 0
        assert any("enhanced layer system" in s.lower() for s in suggestions)

    def test_suggest_layer_optimization_needs_groups(self):
        """Test suggestion to use groups for many layers"""
        tilemap = Tilemap(50, 50, 32, 32, use_enhanced_layers=True)

        # Create many layers without groups
        for i in range(10):
            tilemap.create_enhanced_layer(f"Layer {i}")

        suggestions = AILayerGenerator.suggest_layer_optimization(tilemap)

        # Should suggest using groups
        assert any("groups" in s.lower() for s in suggestions)

    def test_suggest_layer_optimization_invisible_layers(self):
        """Test suggestion about invisible layers"""
        tilemap = Tilemap(50, 50, 32, 32, use_enhanced_layers=True)

        # Create some invisible layers
        layer_id1 = tilemap.create_enhanced_layer("Visible Layer")
        layer_id2 = tilemap.create_enhanced_layer("Invisible Layer")
        layer_id3 = tilemap.create_enhanced_layer("Another Invisible")

        layer2 = tilemap.get_enhanced_layer(layer_id2)
        layer3 = tilemap.get_enhanced_layer(layer_id3)
        layer2.properties.visible = False
        layer3.properties.visible = False

        suggestions = AILayerGenerator.suggest_layer_optimization(tilemap)

        # Should mention invisible layers
        assert any("invisible" in s.lower() for s in suggestions)

    def test_suggest_layer_optimization_duplicate_names(self):
        """Test suggestion about duplicate layer names"""
        tilemap = Tilemap(50, 50, 32, 32, use_enhanced_layers=True)

        tilemap.create_enhanced_layer("Ground")
        tilemap.create_enhanced_layer("Ground")
        tilemap.create_enhanced_layer("Objects")

        suggestions = AILayerGenerator.suggest_layer_optimization(tilemap)

        # Should mention duplicate names
        assert any("duplicate" in s.lower() for s in suggestions)

    def test_suggest_layer_optimization_empty_layers(self):
        """Test suggestion about empty layers"""
        tilemap = Tilemap(10, 10, 32, 32, use_enhanced_layers=True)

        # Create empty layer
        layer_id = tilemap.create_enhanced_layer("Empty Layer")
        layer = tilemap.get_enhanced_layer(layer_id)
        # Layer is already empty by default

        suggestions = AILayerGenerator.suggest_layer_optimization(tilemap)

        # Should mention empty layers
        assert any("empty" in s.lower() for s in suggestions)

    def test_suggest_layer_optimization_parallax_without_autoscroll(self):
        """Test suggestion about parallax layers without auto-scroll"""
        tilemap = Tilemap(50, 50, 32, 32, use_enhanced_layers=True)

        # Create parallax layer without auto-scroll
        tilemap.create_parallax_background("Background", parallax_x=0.5, auto_scroll_x=0.0)

        suggestions = AILayerGenerator.suggest_layer_optimization(tilemap)

        # Should suggest auto-scroll
        assert any("auto-scroll" in s.lower() for s in suggestions)

    def test_suggest_layer_optimization_optimal(self):
        """Test suggestions when layer structure is optimal"""
        tilemap = Tilemap(50, 50, 32, 32, use_enhanced_layers=True)

        # Create a well-structured map with a few layers
        tilemap.create_enhanced_layer("Ground")
        tilemap.create_enhanced_layer("Objects")
        tilemap.create_enhanced_layer("Overlay")

        # Add some tiles so layers aren't empty
        for layer_id in tilemap.layer_manager.layers.keys():
            layer = tilemap.get_enhanced_layer(layer_id)
            layer.set_tile(0, 0, 1)

        suggestions = AILayerGenerator.suggest_layer_optimization(tilemap)

        # Should say it's optimized
        assert any("optimized" in s.lower() for s in suggestions)

    def test_all_generators_return_valid_ids(self):
        """Test that all generators return valid layer IDs"""
        tilemap = Tilemap(50, 50, 32, 32, use_enhanced_layers=True)

        # Test each generator
        generators = [
            lambda: AILayerGenerator.generate_platformer_layers(tilemap),
            lambda: AILayerGenerator.generate_rpg_layers(tilemap),
            lambda: AILayerGenerator.generate_space_shooter_layers(tilemap),
            lambda: AILayerGenerator.generate_strategy_layers(tilemap),
        ]

        for gen in generators:
            # Clear tilemap
            tilemap.layer_manager.layers.clear()
            tilemap.layer_manager.groups.clear()
            tilemap.layer_manager.root_ids.clear()

            layer_ids = gen()

            # All IDs should be valid
            for layer_id in layer_ids:
                layer = tilemap.get_enhanced_layer(layer_id)
                assert layer is not None
                assert layer.properties.layer_id == layer_id
