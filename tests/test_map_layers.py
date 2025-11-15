"""
Tests for Enhanced Map Layer System

Tests all features of the enhanced layer system including:
- Layer creation, removal, and reordering
- Layer properties (name, opacity, locked, visible)
- Layer groups/folders
- Parallax backgrounds
- Layer merging
- Backward compatibility
"""

import pytest

from neonworks.data.map_layers import (
    EnhancedTileLayer,
    LayerGroup,
    LayerManager,
    LayerProperties,
    LayerType,
    ParallaxMode,
)


class TestLayerProperties:
    """Test layer properties"""

    def test_create_default_properties(self):
        """Test creating default layer properties"""
        props = LayerProperties()

        assert props.name == "New Layer"
        assert props.visible is True
        assert props.locked is False
        assert props.opacity == 1.0
        assert props.layer_type == LayerType.STANDARD
        assert props.parallax_mode == ParallaxMode.MANUAL
        assert props.layer_id is not None

    def test_create_custom_properties(self):
        """Test creating custom layer properties"""
        props = LayerProperties(
            name="Background",
            visible=False,
            locked=True,
            opacity=0.5,
            layer_type=LayerType.PARALLAX_BACKGROUND,
        )

        assert props.name == "Background"
        assert props.visible is False
        assert props.locked is True
        assert props.opacity == 0.5
        assert props.layer_type == LayerType.PARALLAX_BACKGROUND

    def test_properties_serialization(self):
        """Test properties to_dict and from_dict"""
        props = LayerProperties(
            name="Test Layer",
            opacity=0.8,
            parallax_x=0.5,
            auto_scroll_x=10.0,
            layer_type=LayerType.PARALLAX_BACKGROUND,
            parallax_mode=ParallaxMode.AUTO_SCROLL,
        )

        data = props.to_dict()
        restored = LayerProperties.from_dict(data)

        assert restored.name == props.name
        assert restored.opacity == props.opacity
        assert restored.parallax_x == props.parallax_x
        assert restored.auto_scroll_x == props.auto_scroll_x
        assert restored.layer_type == props.layer_type
        assert restored.parallax_mode == props.parallax_mode


class TestEnhancedTileLayer:
    """Test enhanced tile layer"""

    def test_create_layer(self):
        """Test creating a layer"""
        layer = EnhancedTileLayer(width=10, height=10)

        assert layer.width == 10
        assert layer.height == 10
        assert len(layer.tiles) == 10
        assert len(layer.tiles[0]) == 10
        assert layer.get_tile(0, 0) == 0

    def test_get_set_tile(self):
        """Test getting and setting tiles"""
        layer = EnhancedTileLayer(width=10, height=10)

        layer.set_tile(5, 5, 42)
        assert layer.get_tile(5, 5) == 42

        # Out of bounds
        assert layer.get_tile(-1, 0) == 0
        assert layer.get_tile(0, -1) == 0
        assert layer.get_tile(100, 100) == 0

    def test_fill_layer(self):
        """Test filling layer with tile"""
        layer = EnhancedTileLayer(width=10, height=10)
        layer.fill(7)

        for y in range(10):
            for x in range(10):
                assert layer.get_tile(x, y) == 7

    def test_clear_layer(self):
        """Test clearing layer"""
        layer = EnhancedTileLayer(width=10, height=10)
        layer.fill(7)
        layer.clear()

        for y in range(10):
            for x in range(10):
                assert layer.get_tile(x, y) == 0

    def test_resize_layer(self):
        """Test resizing layer"""
        layer = EnhancedTileLayer(width=5, height=5)
        layer.set_tile(2, 2, 42)

        layer.resize(10, 10, fill_tile=99)

        assert layer.width == 10
        assert layer.height == 10
        assert layer.get_tile(2, 2) == 42  # Preserved
        assert layer.get_tile(9, 9) == 99  # New area filled

    def test_auto_scroll_update(self):
        """Test auto-scroll update"""
        props = LayerProperties(
            parallax_mode=ParallaxMode.AUTO_SCROLL, auto_scroll_x=10.0, auto_scroll_y=5.0
        )
        layer = EnhancedTileLayer(width=10, height=10, properties=props)

        layer.update_auto_scroll(1.0)  # 1 second
        offset_x, offset_y = layer.get_effective_offset()

        assert offset_x == 10.0
        assert offset_y == 5.0

    def test_layer_serialization(self):
        """Test layer to_dict and from_dict"""
        props = LayerProperties(name="Test Layer", opacity=0.8)
        layer = EnhancedTileLayer(width=5, height=5, properties=props)
        layer.set_tile(2, 2, 42)

        data = layer.to_dict()
        restored = EnhancedTileLayer.from_dict(data)

        assert restored.width == layer.width
        assert restored.height == layer.height
        assert restored.get_tile(2, 2) == 42
        assert restored.properties.name == "Test Layer"
        assert restored.properties.opacity == 0.8


class TestLayerGroup:
    """Test layer groups"""

    def test_create_group(self):
        """Test creating a group"""
        group = LayerGroup(name="Background Layers")

        assert group.name == "Background Layers"
        assert group.visible is True
        assert group.locked is False
        assert group.expanded is True
        assert len(group.child_ids) == 0

    def test_add_remove_children(self):
        """Test adding and removing children"""
        group = LayerGroup()

        group.add_child("layer1")
        group.add_child("layer2")

        assert len(group.child_ids) == 2
        assert "layer1" in group.child_ids
        assert "layer2" in group.child_ids

        group.remove_child("layer1")
        assert len(group.child_ids) == 1
        assert "layer1" not in group.child_ids

    def test_reorder_children(self):
        """Test reordering children"""
        group = LayerGroup()
        group.add_child("layer1")
        group.add_child("layer2")
        group.add_child("layer3")

        group.reorder_child("layer3", 0)

        assert group.child_ids[0] == "layer3"
        assert group.child_ids[1] == "layer1"
        assert group.child_ids[2] == "layer2"


class TestLayerManager:
    """Test layer manager"""

    def test_create_manager(self):
        """Test creating a layer manager"""
        manager = LayerManager(width=20, height=15)

        assert manager.width == 20
        assert manager.height == 15
        assert len(manager.layers) == 0
        assert len(manager.groups) == 0

    def test_create_layer(self):
        """Test creating a layer"""
        manager = LayerManager(width=10, height=10)
        layer = manager.create_layer("Ground")

        assert len(manager.layers) == 1
        assert layer.properties.name == "Ground"
        assert layer.properties.layer_id in manager.layers
        assert layer.properties.layer_id in manager.root_ids

    def test_create_multiple_layers(self):
        """Test creating multiple layers"""
        manager = LayerManager(width=10, height=10)

        layer1 = manager.create_layer("Ground")
        layer2 = manager.create_layer("Objects")
        layer3 = manager.create_layer("Overlay")

        assert len(manager.layers) == 3
        assert len(manager.root_ids) == 3
        assert manager.root_ids[0] == layer1.properties.layer_id
        assert manager.root_ids[1] == layer2.properties.layer_id
        assert manager.root_ids[2] == layer3.properties.layer_id

    def test_remove_layer(self):
        """Test removing a layer"""
        manager = LayerManager(width=10, height=10)
        layer = manager.create_layer("Ground")
        layer_id = layer.properties.layer_id

        assert manager.remove_layer(layer_id) is True
        assert len(manager.layers) == 0
        assert layer_id not in manager.root_ids

    def test_get_layer_by_id(self):
        """Test getting layer by ID"""
        manager = LayerManager(width=10, height=10)
        layer = manager.create_layer("Ground")

        retrieved = manager.get_layer(layer.properties.layer_id)
        assert retrieved is layer

    def test_get_layer_by_name(self):
        """Test getting layer by name"""
        manager = LayerManager(width=10, height=10)
        manager.create_layer("Ground")
        manager.create_layer("Objects")

        layer = manager.get_layer_by_name("Objects")
        assert layer is not None
        assert layer.properties.name == "Objects"

    def test_reorder_layer(self):
        """Test reordering layers"""
        manager = LayerManager(width=10, height=10)

        layer1 = manager.create_layer("Layer1")
        layer2 = manager.create_layer("Layer2")
        layer3 = manager.create_layer("Layer3")

        # Move layer3 to bottom
        manager.reorder_layer(layer3.properties.layer_id, 0)

        assert manager.root_ids[0] == layer3.properties.layer_id
        assert manager.root_ids[1] == layer1.properties.layer_id
        assert manager.root_ids[2] == layer2.properties.layer_id

    def test_duplicate_layer(self):
        """Test duplicating a layer"""
        manager = LayerManager(width=10, height=10)
        layer = manager.create_layer("Ground")
        layer.set_tile(5, 5, 42)

        new_id = manager.duplicate_layer(layer.properties.layer_id)

        assert new_id is not None
        assert len(manager.layers) == 2

        new_layer = manager.get_layer(new_id)
        assert new_layer.properties.name == "Ground Copy"
        assert new_layer.get_tile(5, 5) == 42

    def test_merge_layers(self):
        """Test merging layers"""
        manager = LayerManager(width=10, height=10)

        layer1 = manager.create_layer("Layer1")
        layer1.set_tile(0, 0, 1)
        layer1.set_tile(5, 5, 2)

        layer2 = manager.create_layer("Layer2")
        layer2.set_tile(5, 5, 3)  # Overwrites layer1
        layer2.set_tile(9, 9, 4)

        merged_id = manager.merge_layers(
            [layer1.properties.layer_id, layer2.properties.layer_id], "Merged"
        )

        assert merged_id is not None
        merged = manager.get_layer(merged_id)

        assert merged.get_tile(0, 0) == 1
        assert merged.get_tile(5, 5) == 3  # Layer2 wins
        assert merged.get_tile(9, 9) == 4

    def test_create_group(self):
        """Test creating a group"""
        manager = LayerManager(width=10, height=10)
        group = manager.create_group("Background")

        assert len(manager.groups) == 1
        assert group.group_id in manager.groups
        assert group.group_id in manager.root_ids

    def test_layer_in_group(self):
        """Test creating layer in group"""
        manager = LayerManager(width=10, height=10)
        group = manager.create_group("Background")
        layer = manager.create_layer("Sky", parent_group_id=group.group_id)

        assert layer.parent_group_id == group.group_id
        assert layer.properties.layer_id in group.child_ids
        assert layer.properties.layer_id not in manager.root_ids

    def test_move_layer_to_group(self):
        """Test moving layer to group"""
        manager = LayerManager(width=10, height=10)

        layer = manager.create_layer("Ground")
        group = manager.create_group("Terrain")

        manager.move_layer_to_group(layer.properties.layer_id, group.group_id)

        assert layer.parent_group_id == group.group_id
        assert layer.properties.layer_id in group.child_ids
        assert layer.properties.layer_id not in manager.root_ids

    def test_get_render_order(self):
        """Test getting render order"""
        manager = LayerManager(width=10, height=10)

        # Create structure:
        # - Background Group
        #   - Sky
        #   - Mountains
        # - Ground
        # - Objects

        bg_group = manager.create_group("Background")
        sky = manager.create_layer("Sky", parent_group_id=bg_group.group_id)
        mountains = manager.create_layer("Mountains", parent_group_id=bg_group.group_id)
        ground = manager.create_layer("Ground")
        objects = manager.create_layer("Objects")

        render_order = manager.get_render_order()

        assert len(render_order) == 4
        assert render_order[0] == sky.properties.layer_id
        assert render_order[1] == mountains.properties.layer_id
        assert render_order[2] == ground.properties.layer_id
        assert render_order[3] == objects.properties.layer_id

    def test_remove_group_keep_children(self):
        """Test removing group and keeping children"""
        manager = LayerManager(width=10, height=10)

        group = manager.create_group("Background")
        layer = manager.create_layer("Sky", parent_group_id=group.group_id)

        manager.remove_group(group.group_id, remove_children=False)

        assert group.group_id not in manager.groups
        assert layer.properties.layer_id in manager.layers
        assert layer.parent_group_id is None
        assert layer.properties.layer_id in manager.root_ids

    def test_remove_group_with_children(self):
        """Test removing group and its children"""
        manager = LayerManager(width=10, height=10)

        group = manager.create_group("Background")
        layer = manager.create_layer("Sky", parent_group_id=group.group_id)

        manager.remove_group(group.group_id, remove_children=True)

        assert group.group_id not in manager.groups
        assert layer.properties.layer_id not in manager.layers

    def test_update_auto_scroll(self):
        """Test updating auto-scroll layers"""
        manager = LayerManager(width=10, height=10)

        props = LayerProperties(
            parallax_mode=ParallaxMode.AUTO_SCROLL, auto_scroll_x=10.0, auto_scroll_y=5.0
        )
        layer = manager.create_layer("Scrolling", properties=props)

        manager.update(1.0)  # 1 second

        offset_x, offset_y = layer.get_effective_offset()
        assert offset_x == 10.0
        assert offset_y == 5.0

    def test_resize_all_layers(self):
        """Test resizing all layers"""
        manager = LayerManager(width=5, height=5)

        layer1 = manager.create_layer("Layer1")
        layer2 = manager.create_layer("Layer2")

        layer1.set_tile(2, 2, 42)

        manager.resize_all_layers(10, 10, fill_tile=99)

        assert manager.width == 10
        assert manager.height == 10
        assert layer1.width == 10
        assert layer1.height == 10
        assert layer2.width == 10
        assert layer2.height == 10
        assert layer1.get_tile(2, 2) == 42
        assert layer1.get_tile(9, 9) == 99

    def test_manager_serialization(self):
        """Test manager to_dict and from_dict"""
        manager = LayerManager(width=10, height=10)

        group = manager.create_group("Background")
        layer1 = manager.create_layer("Sky", parent_group_id=group.group_id)
        layer2 = manager.create_layer("Ground")

        layer1.set_tile(5, 5, 42)
        layer2.set_tile(3, 3, 99)

        data = manager.to_dict()
        restored = LayerManager.from_dict(data)

        assert restored.width == manager.width
        assert restored.height == manager.height
        assert len(restored.layers) == 2
        assert len(restored.groups) == 1

        restored_layer1 = restored.get_layer_by_name("Sky")
        assert restored_layer1.get_tile(5, 5) == 42

    def test_legacy_conversion(self):
        """Test converting from legacy 3-layer format"""
        legacy_data = [
            [[1, 2], [3, 4]],  # Ground
            [[5, 6], [7, 8]],  # Objects
            [[9, 0], [0, 10]],  # Overlay
        ]

        manager = LayerManager.from_legacy_layers(2, 2, legacy_data)

        assert manager.width == 2
        assert manager.height == 2
        assert len(manager.layers) == 3

        ground = manager.get_layer_by_name("Ground")
        objects = manager.get_layer_by_name("Objects")
        overlay = manager.get_layer_by_name("Overlay")

        assert ground.get_tile(0, 0) == 1
        assert objects.get_tile(1, 1) == 8
        assert overlay.get_tile(0, 0) == 9


class TestLayerTypes:
    """Test different layer types"""

    def test_standard_layer(self):
        """Test standard layer type"""
        props = LayerProperties(layer_type=LayerType.STANDARD)
        assert props.layer_type == LayerType.STANDARD

    def test_parallax_background_layer(self):
        """Test parallax background layer type"""
        props = LayerProperties(
            layer_type=LayerType.PARALLAX_BACKGROUND,
            parallax_x=0.5,
            parallax_y=0.5,
        )
        assert props.layer_type == LayerType.PARALLAX_BACKGROUND
        assert props.parallax_x == 0.5

    def test_collision_layer(self):
        """Test collision layer type"""
        props = LayerProperties(layer_type=LayerType.COLLISION)
        assert props.layer_type == LayerType.COLLISION

    def test_overlay_layer(self):
        """Test overlay layer type"""
        props = LayerProperties(layer_type=LayerType.OVERLAY)
        assert props.layer_type == LayerType.OVERLAY
