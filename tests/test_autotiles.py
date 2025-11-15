"""
Tests for the Autotile System

Tests autotile set creation, tile matching, neighbor updates, and the autotile manager.
"""

import pytest

from neonworks.rendering.autotiles import (
    CARDINAL_BOTTOM,
    CARDINAL_LEFT,
    CARDINAL_RIGHT,
    CARDINAL_TOP,
    NEIGHBOR_BOTTOM,
    NEIGHBOR_BOTTOM_LEFT,
    NEIGHBOR_BOTTOM_RIGHT,
    NEIGHBOR_LEFT,
    NEIGHBOR_RIGHT,
    NEIGHBOR_TOP,
    NEIGHBOR_TOP_LEFT,
    NEIGHBOR_TOP_RIGHT,
    AutotileFormat,
    AutotileManager,
    AutotileSet,
    get_autotile_manager,
    reset_autotile_manager,
)
from neonworks.rendering.tilemap import Tile, TileLayer


class TestAutotileSet:
    """Test suite for AutotileSet class."""

    def test_create_16_tile_autotile_set(self):
        """Test creating a 16-tile autotile set."""
        autotile_set = AutotileSet(
            name="Water",
            tileset_name="terrain",
            format=AutotileFormat.TILE_16,
            base_tile_id=0,
        )

        assert autotile_set.name == "Water"
        assert autotile_set.format == AutotileFormat.TILE_16
        assert autotile_set.base_tile_id == 0
        assert len(autotile_set.bitmask_to_tile) == 16

    def test_create_47_tile_autotile_set(self):
        """Test creating a 47-tile autotile set."""
        autotile_set = AutotileSet(
            name="Grass",
            tileset_name="terrain",
            format=AutotileFormat.TILE_47,
            base_tile_id=48,
        )

        assert autotile_set.name == "Grass"
        assert autotile_set.format == AutotileFormat.TILE_47
        assert autotile_set.base_tile_id == 48
        assert len(autotile_set.bitmask_to_tile) > 0

    def test_tile_ids_auto_populated(self):
        """Test that tile IDs are automatically populated."""
        autotile_set = AutotileSet(
            name="Wall",
            tileset_name="terrain",
            format=AutotileFormat.TILE_16,
            base_tile_id=16,
        )

        assert len(autotile_set.tile_ids) == 16
        assert 16 in autotile_set.tile_ids
        assert 31 in autotile_set.tile_ids

    def test_contains_tile(self):
        """Test checking if a tile belongs to the autotile set."""
        autotile_set = AutotileSet(
            name="Water",
            tileset_name="terrain",
            format=AutotileFormat.TILE_16,
            base_tile_id=1,
        )

        assert autotile_set.contains_tile(1)
        assert autotile_set.contains_tile(5)
        assert autotile_set.contains_tile(16)
        assert not autotile_set.contains_tile(0)
        assert not autotile_set.contains_tile(100)

    def test_get_tile_for_bitmask_isolated(self):
        """Test getting tile for isolated tile (no neighbors)."""
        autotile_set = AutotileSet(
            name="Water",
            tileset_name="terrain",
            format=AutotileFormat.TILE_16,
            base_tile_id=1,
        )

        # No neighbors = bitmask 0 = offset 0 = base_tile_id + 0
        tile_id = autotile_set.get_tile_for_bitmask(0)
        assert tile_id == 1

    def test_get_tile_for_bitmask_cardinal_directions(self):
        """Test getting tiles for cardinal direction connections."""
        autotile_set = AutotileSet(
            name="Water",
            tileset_name="terrain",
            format=AutotileFormat.TILE_16,
            base_tile_id=1,
        )

        # Top only
        tile_id = autotile_set.get_tile_for_bitmask(NEIGHBOR_TOP)
        assert tile_id == 5  # base_tile_id(1) + offset(4) for top

        # Left + Right (horizontal)
        tile_id = autotile_set.get_tile_for_bitmask(NEIGHBOR_LEFT | NEIGHBOR_RIGHT)
        assert tile_id == 4  # base_tile_id(1) + offset(3) for horizontal

        # All four directions (cross)
        tile_id = autotile_set.get_tile_for_bitmask(
            NEIGHBOR_TOP | NEIGHBOR_RIGHT | NEIGHBOR_BOTTOM | NEIGHBOR_LEFT
        )
        assert tile_id == 16  # base_tile_id(1) + offset(15) for full cross


class TestAutotileManager:
    """Test suite for AutotileManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        reset_autotile_manager()
        self.manager = get_autotile_manager()

        # Create test autotile set
        # Use base_tile_id=1 to avoid conflict with empty tiles (tile_id=0)
        self.water_autotile = AutotileSet(
            name="Water",
            tileset_name="terrain",
            format=AutotileFormat.TILE_16,
            base_tile_id=1,
        )
        self.manager.register_autotile_set(self.water_autotile)

        # Create test layer
        self.layer = TileLayer(name="ground", width=10, height=10)

    def test_register_autotile_set(self):
        """Test registering an autotile set."""
        wall_autotile = AutotileSet(
            name="Wall",
            tileset_name="terrain",
            format=AutotileFormat.TILE_16,
            base_tile_id=16,
        )

        self.manager.register_autotile_set(wall_autotile)

        assert "Wall" in self.manager.autotile_sets
        assert self.manager.autotile_sets["Wall"] == wall_autotile

    def test_get_autotile_set(self):
        """Test getting an autotile set by name."""
        autotile_set = self.manager.get_autotile_set("Water")

        assert autotile_set is not None
        assert autotile_set.name == "Water"

    def test_get_autotile_for_tile(self):
        """Test getting the autotile set for a tile ID."""
        autotile_set = self.manager.get_autotile_for_tile(5)

        assert autotile_set is not None
        assert autotile_set.name == "Water"

        # Tile not in any autotile set
        autotile_set = self.manager.get_autotile_for_tile(100)
        assert autotile_set is None

    def test_is_autotile(self):
        """Test checking if a tile is an autotile."""
        assert self.manager.is_autotile(1)  # base_tile_id
        assert self.manager.is_autotile(16)  # base_tile_id + 15
        assert not self.manager.is_autotile(0)  # empty tile
        assert not self.manager.is_autotile(100)

    def test_calculate_bitmask_isolated(self):
        """Test calculating bitmask for isolated tile."""
        # Empty layer - no neighbors
        bitmask = self.manager.calculate_bitmask(self.layer, 5, 5, self.water_autotile)

        assert bitmask == 0

    def test_calculate_bitmask_with_neighbors(self):
        """Test calculating bitmask with neighboring tiles."""
        # Place water tiles (use tile IDs from water autotile set)
        self.layer.set_tile(5, 5, Tile(tile_id=1))  # Center (base_tile_id)
        self.layer.set_tile(5, 4, Tile(tile_id=2))  # Top
        self.layer.set_tile(6, 5, Tile(tile_id=3))  # Right

        bitmask = self.manager.calculate_bitmask(self.layer, 5, 5, self.water_autotile)

        # Should have top and right neighbors
        assert bitmask & NEIGHBOR_TOP
        assert bitmask & NEIGHBOR_RIGHT
        assert not (bitmask & NEIGHBOR_LEFT)
        assert not (bitmask & NEIGHBOR_BOTTOM)

    def test_calculate_bitmask_all_neighbors(self):
        """Test calculating bitmask with all 8 neighbors."""
        # Place water tiles in 3x3 grid (use tile IDs from water autotile set)
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                self.layer.set_tile(5 + dx, 5 + dy, Tile(tile_id=1))  # base_tile_id

        bitmask = self.manager.calculate_bitmask(self.layer, 5, 5, self.water_autotile)

        # Should have all 8 neighbors
        assert bitmask & NEIGHBOR_TOP
        assert bitmask & NEIGHBOR_RIGHT
        assert bitmask & NEIGHBOR_BOTTOM
        assert bitmask & NEIGHBOR_LEFT
        assert bitmask & (1 << 1)  # Top-right
        assert bitmask & (1 << 3)  # Bottom-right
        assert bitmask & (1 << 5)  # Bottom-left
        assert bitmask & (1 << 7)  # Top-left

    def test_paint_autotile_isolated(self):
        """Test painting an isolated autotile."""
        self.manager.paint_autotile(self.layer, 5, 5, self.water_autotile)

        tile = self.layer.get_tile(5, 5)
        assert tile is not None
        assert tile.tile_id == 1  # Isolated tile (base_tile_id + offset 0)

    def test_paint_autotile_with_neighbors(self):
        """Test painting autotiles that connect."""
        # Paint first tile
        self.manager.paint_autotile(self.layer, 5, 5, self.water_autotile)

        # Paint adjacent tile - both should update
        self.manager.paint_autotile(self.layer, 6, 5, self.water_autotile)

        tile1 = self.layer.get_tile(5, 5)
        tile2 = self.layer.get_tile(6, 5)

        # Both tiles should have been updated to connect
        assert tile1.tile_id != 1  # Not isolated anymore (should be > base_tile_id)
        assert tile2.tile_id != 1  # Not isolated anymore

    def test_erase_autotile(self):
        """Test erasing an autotile and updating neighbors."""
        # Paint a 3x3 area
        for y in range(4, 7):
            for x in range(4, 7):
                self.manager.paint_autotile(self.layer, x, y, self.water_autotile)

        # Erase center tile
        self.manager.erase_autotile(self.layer, 5, 5)

        # Center should be empty
        center_tile = self.layer.get_tile(5, 5)
        assert center_tile.tile_id == 0

        # Adjacent tiles should have been updated
        top_tile = self.layer.get_tile(5, 4)
        assert top_tile.tile_id != 15  # No longer has bottom neighbor

    def test_get_preview_tile(self):
        """Test getting a preview of what tile would be placed."""
        # Paint some tiles (use tile IDs from water autotile set)
        self.layer.set_tile(5, 4, Tile(tile_id=1))  # Top (base_tile_id)
        self.layer.set_tile(6, 5, Tile(tile_id=1))  # Right

        # Get preview without actually placing
        preview_tile_id = self.manager.get_preview_tile(self.layer, 5, 5, self.water_autotile)

        # Should show the tile that would be placed (not isolated)
        assert preview_tile_id != 1  # Not isolated tile

        # Original position should still be empty
        tile = self.layer.get_tile(5, 5)
        assert tile.tile_id == 0

    def test_fill_with_autotile(self):
        """Test flood filling with autotiles."""
        # Fill should replace all connected tiles with same ID
        self.layer.fill(50)  # Fill with tile ID 50

        # Fill from center
        self.manager.fill_with_autotile(self.layer, 5, 5, self.water_autotile)

        # All tiles should now be water autotiles
        for y in range(self.layer.height):
            for x in range(self.layer.width):
                tile = self.layer.get_tile(x, y)
                assert tile.tile_id in self.water_autotile.tile_ids

    def test_update_adjacent_tiles(self):
        """Test updating adjacent tiles after placing a tile."""
        # Paint initial tile (use tile ID from water autotile set)
        self.layer.set_tile(5, 5, Tile(tile_id=1))  # base_tile_id

        # Paint adjacent tile
        self.layer.set_tile(6, 5, Tile(tile_id=1))

        # Update adjacent tiles
        self.manager.update_adjacent_tiles(self.layer, 6, 5)

        # Both tiles should be updated
        tile1 = self.layer.get_tile(5, 5)
        tile2 = self.layer.get_tile(6, 5)

        # Tiles should connect horizontally (tile_id should be different from isolated)
        assert tile1.tile_id != 1  # Not isolated
        assert tile2.tile_id != 1  # Not isolated


class TestAutotileBitmasks:
    """Test bitmask calculations and tile matching."""

    def test_cardinal_bitmasks(self):
        """Test cardinal direction bitmasks."""
        assert CARDINAL_TOP == 1
        assert CARDINAL_RIGHT == 2
        assert CARDINAL_BOTTOM == 4
        assert CARDINAL_LEFT == 8

    def test_neighbor_bitmasks(self):
        """Test 8-neighbor bitmasks."""
        assert NEIGHBOR_TOP == 1
        assert NEIGHBOR_TOP_RIGHT == 2
        assert NEIGHBOR_RIGHT == 4
        assert NEIGHBOR_BOTTOM_RIGHT == 8
        assert NEIGHBOR_BOTTOM == 16
        assert NEIGHBOR_BOTTOM_LEFT == 32
        assert NEIGHBOR_LEFT == 64
        assert NEIGHBOR_TOP_LEFT == 128

    def test_16_tile_mapping_completeness(self):
        """Test that 16-tile mapping covers all cardinal combinations."""
        autotile_set = AutotileSet(
            name="Test",
            tileset_name="terrain",
            format=AutotileFormat.TILE_16,
            base_tile_id=1,
        )

        # All 16 combinations of 4 cardinal directions should be mapped
        for i in range(16):
            tile_id = autotile_set.get_tile_for_bitmask(i)
            assert 1 <= tile_id <= 16  # base_tile_id + offset (0-15)


class TestAutotileEdgeCases:
    """Test edge cases and error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        reset_autotile_manager()
        self.manager = get_autotile_manager()

        # Use base_tile_id=1 to avoid conflict with empty tiles (tile_id=0)
        self.water_autotile = AutotileSet(
            name="Water",
            tileset_name="terrain",
            format=AutotileFormat.TILE_16,
            base_tile_id=1,
        )
        self.manager.register_autotile_set(self.water_autotile)

        self.layer = TileLayer(name="ground", width=10, height=10)

    def test_paint_at_boundary(self):
        """Test painting autotiles at layer boundaries."""
        # Paint at corners and edges
        self.manager.paint_autotile(self.layer, 0, 0, self.water_autotile)
        self.manager.paint_autotile(self.layer, 9, 9, self.water_autotile)
        self.manager.paint_autotile(self.layer, 0, 9, self.water_autotile)
        self.manager.paint_autotile(self.layer, 9, 0, self.water_autotile)

        # Should not crash - isolated tiles at boundaries
        assert self.layer.get_tile(0, 0).tile_id == 1  # base_tile_id (isolated)
        assert self.layer.get_tile(9, 9).tile_id == 1

    def test_calculate_bitmask_at_boundary(self):
        """Test calculating bitmask at layer boundaries."""
        # Should handle out-of-bounds neighbors gracefully
        bitmask = self.manager.calculate_bitmask(self.layer, 0, 0, self.water_autotile)
        assert bitmask == 0

    def test_empty_layer(self):
        """Test operations on empty layer."""
        # Should not crash
        self.manager.update_adjacent_tiles(self.layer, 5, 5)

        tile = self.layer.get_tile(5, 5)
        assert tile.tile_id == 0

    def test_multiple_autotile_sets(self):
        """Test managing multiple autotile sets."""
        wall_autotile = AutotileSet(
            name="Wall",
            tileset_name="terrain",
            format=AutotileFormat.TILE_16,
            base_tile_id=16,
        )
        self.manager.register_autotile_set(wall_autotile)

        # Paint water and walls next to each other
        self.manager.paint_autotile(self.layer, 5, 5, self.water_autotile)
        self.manager.paint_autotile(self.layer, 6, 5, wall_autotile)

        water_tile = self.layer.get_tile(5, 5)
        wall_tile = self.layer.get_tile(6, 5)

        # Should not connect (different autotile sets)
        assert water_tile.tile_id in self.water_autotile.tile_ids
        assert wall_tile.tile_id in wall_autotile.tile_ids


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
