"""
Tests for the AI tileset generator system.

Author: NeonWorks Team
Version: 0.1.0
"""

import os
import tempfile

import pygame
import pytest

from neonworks.data.tileset_manager import (
    TilesetManager,
    reset_tileset_manager,
)
from neonworks.editor.ai_tileset_generator import (
    AITilesetGenerator,
    reset_ai_tileset_generator,
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
def temp_project_dir():
    """Create a temporary project directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir


@pytest.fixture
def tileset_manager(temp_project_dir):
    """Create a fresh tileset manager for each test."""
    reset_tileset_manager()
    manager = TilesetManager(temp_project_dir)
    yield manager
    reset_tileset_manager()


@pytest.fixture
def ai_generator(tileset_manager, pygame_display):
    """Create AI tileset generator."""
    reset_ai_tileset_generator()
    generator = AITilesetGenerator(tileset_manager)
    yield generator
    reset_ai_tileset_generator()


class TestAITilesetGenerator:
    """Test suite for AI tileset generator."""

    def test_create_generator(self, ai_generator):
        """Test creating an AI tileset generator."""
        assert ai_generator is not None
        assert ai_generator.tile_size == 32

    def test_terrain_types_defined(self, ai_generator):
        """Test that terrain types are defined."""
        assert len(AITilesetGenerator.TERRAIN_TYPES) > 0
        assert "grass" in AITilesetGenerator.TERRAIN_TYPES
        assert "water" in AITilesetGenerator.TERRAIN_TYPES
        assert "stone" in AITilesetGenerator.TERRAIN_TYPES

    def test_generate_single_terrain_tileset(self, ai_generator):
        """Test generating a tileset with a single terrain type."""
        tileset_surface, metadata = ai_generator.generate_procedural_tileset(
            terrain_types=["grass"],
            tiles_per_type=4,
            tile_size=32,
            include_variations=True,
        )

        assert tileset_surface is not None
        assert tileset_surface.get_width() > 0
        assert tileset_surface.get_height() > 0
        assert len(metadata) == 4  # 4 tiles for grass

        # Check metadata
        for tile_id, tile_meta in metadata.items():
            assert tile_meta.tile_id == tile_id
            assert "grass" in tile_meta.terrain_tags
            assert tile_meta.passable is True  # Grass is passable

    def test_generate_multiple_terrain_tileset(self, ai_generator):
        """Test generating a tileset with multiple terrain types."""
        terrain_types = ["grass", "dirt", "stone", "water"]
        tiles_per_type = 3

        tileset_surface, metadata = ai_generator.generate_procedural_tileset(
            terrain_types=terrain_types,
            tiles_per_type=tiles_per_type,
            tile_size=32,
            include_variations=True,
        )

        assert tileset_surface is not None
        total_tiles = len(terrain_types) * tiles_per_type
        assert len(metadata) == total_tiles

        # Check that each terrain type is represented
        terrain_counts = {}
        for tile_meta in metadata.values():
            for tag in tile_meta.terrain_tags:
                if tag in terrain_types:
                    terrain_counts[tag] = terrain_counts.get(tag, 0) + 1

        for terrain in terrain_types:
            assert terrain in terrain_counts
            assert terrain_counts[terrain] == tiles_per_type

    def test_generate_tileset_custom_size(self, ai_generator):
        """Test generating a tileset with custom tile size."""
        tileset_surface, metadata = ai_generator.generate_procedural_tileset(
            terrain_types=["grass"],
            tiles_per_type=2,
            tile_size=64,
            include_variations=True,
        )

        assert tileset_surface is not None
        # With 2 tiles and 8 columns, it should be at least 128 pixels wide
        assert tileset_surface.get_width() >= 128
        assert ai_generator.tile_size == 64

    def test_generate_tileset_without_variations(self, ai_generator):
        """Test generating a tileset without visual variations."""
        tileset_surface, metadata = ai_generator.generate_procedural_tileset(
            terrain_types=["grass"],
            tiles_per_type=2,
            tile_size=32,
            include_variations=False,
        )

        assert tileset_surface is not None
        assert len(metadata) == 2

    def test_passability_for_different_terrains(self, ai_generator):
        """Test that passability is set correctly for different terrain types."""
        tileset_surface, metadata = ai_generator.generate_procedural_tileset(
            terrain_types=["grass", "water", "wall"],
            tiles_per_type=2,
            tile_size=32,
        )

        # Count passable and non-passable tiles
        passable_count = sum(1 for m in metadata.values() if m.passable)
        non_passable_count = sum(1 for m in metadata.values() if not m.passable)

        # Grass is passable (2 tiles), water and wall are not (4 tiles total)
        assert passable_count == 2
        assert non_passable_count == 4

    def test_get_average_color(self, ai_generator, pygame_display):
        """Test getting average color of a surface."""
        surface = pygame.Surface((32, 32))
        surface.fill((100, 150, 200))

        avg_color = ai_generator._get_average_color(surface)

        assert avg_color == (100, 150, 200)

    def test_get_brightness(self, ai_generator):
        """Test calculating brightness of colors."""
        # Black
        assert ai_generator._get_brightness((0, 0, 0)) == 0

        # White
        assert ai_generator._get_brightness((255, 255, 255)) == 255

        # Gray
        brightness = ai_generator._get_brightness((128, 128, 128))
        assert 100 < brightness < 150

    def test_get_dominant_color_channel(self, ai_generator):
        """Test determining dominant color channel."""
        assert ai_generator._get_dominant_color_channel((255, 0, 0)) == "red"
        assert ai_generator._get_dominant_color_channel((0, 255, 0)) == "green"
        assert ai_generator._get_dominant_color_channel((0, 0, 255)) == "blue"
        assert ai_generator._get_dominant_color_channel((128, 128, 128)) == "balanced"

    def test_classify_terrain_by_color(self, ai_generator):
        """Test classifying terrain based on color."""
        # Blue water
        terrain, passable = ai_generator._classify_terrain_by_color((100, 150, 255), 180, "blue")
        assert terrain == "water"
        assert passable is False

        # Green grass
        terrain, passable = ai_generator._classify_terrain_by_color((100, 200, 50), 150, "green")
        assert terrain == "grass"
        assert passable is True

        # Red lava
        terrain, passable = ai_generator._classify_terrain_by_color((255, 100, 0), 180, "red")
        assert terrain == "lava"
        assert passable is False

    def test_has_color_variation(self, ai_generator, pygame_display):
        """Test detecting color variation in a surface."""
        # Solid color surface
        solid_surface = pygame.Surface((32, 32))
        solid_surface.fill((100, 100, 100))
        assert ai_generator._has_color_variation(solid_surface) is False

        # Variable color surface
        varied_surface = pygame.Surface((32, 32))
        varied_surface.fill((100, 100, 100))
        pygame.draw.rect(varied_surface, (200, 200, 200), (0, 0, 16, 16))
        pygame.draw.rect(varied_surface, (50, 50, 50), (16, 16, 16, 16))
        assert ai_generator._has_color_variation(varied_surface) is True

    def test_auto_tag_tileset(self, ai_generator, tileset_manager, pygame_display):
        """Test auto-tagging a tileset with AI."""
        # Generate a test tileset first
        tileset_surface, _ = ai_generator.generate_procedural_tileset(
            terrain_types=["grass", "water"],
            tiles_per_type=2,
            tile_size=32,
        )

        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        temp_file.close()  # Close the file so pygame can write to it
        pygame.image.save(tileset_surface, temp_file.name)

        # Add to tileset manager
        tileset_manager.add_tileset(
            tileset_id="test_tileset",
            name="Test Tileset",
            image_path=temp_file.name,
            tile_width=32,
            tile_height=32,
        )
        tileset_manager.load_tileset("test_tileset")

        # Auto-tag
        metadata = ai_generator.auto_tag_tileset("test_tileset")

        assert len(metadata) > 0
        for tile_id, tile_meta in metadata.items():
            assert tile_meta.tile_id == tile_id
            assert len(tile_meta.terrain_tags) > 0
            assert tile_meta.name != ""

        # Cleanup
        os.unlink(temp_file.name)

    def test_auto_tag_nonexistent_tileset_fails(self, ai_generator):
        """Test that auto-tagging a non-existent tileset raises an error."""
        with pytest.raises(ValueError):
            ai_generator.auto_tag_tileset("nonexistent")

    def test_create_autotiling_rules(self, ai_generator):
        """Test creating autotiling rules for a terrain type."""
        rules = ai_generator.create_autotiling_rules(tileset_id="test_tileset", terrain_tag="grass")

        assert rules is not None
        assert rules["terrain_tag"] == "grass"
        assert rules["tileset_id"] == "test_tileset"
        assert "rules" in rules
        assert len(rules["rules"]) > 0

    def test_suggest_tile_variations(self, ai_generator, tileset_manager, pygame_display):
        """Test generating variations of a tile."""
        # Generate a test tileset first
        tileset_surface, _ = ai_generator.generate_procedural_tileset(
            terrain_types=["grass"],
            tiles_per_type=1,
            tile_size=32,
        )

        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        temp_file.close()  # Close the file so pygame can write to it
        pygame.image.save(tileset_surface, temp_file.name)

        # Add to tileset manager
        tileset_manager.add_tileset(
            tileset_id="test_tileset",
            name="Test Tileset",
            image_path=temp_file.name,
            tile_width=32,
            tile_height=32,
        )
        tileset_manager.load_tileset("test_tileset")

        # Generate variations
        variations = ai_generator.suggest_tile_variations(
            tileset_id="test_tileset", tile_id=0, count=3
        )

        assert len(variations) == 3
        for variation in variations:
            assert variation is not None
            assert variation.get_width() == 32
            assert variation.get_height() == 32

        # Cleanup
        os.unlink(temp_file.name)

    def test_suggest_variations_nonexistent_tileset_fails(self, ai_generator):
        """Test that suggesting variations for non-existent tileset fails."""
        with pytest.raises(ValueError):
            ai_generator.suggest_tile_variations(tileset_id="nonexistent", tile_id=0, count=3)

    def test_unknown_terrain_type_warning(self, ai_generator):
        """Test that unknown terrain types are handled gracefully."""
        # This should not crash, just skip the unknown terrain
        tileset_surface, metadata = ai_generator.generate_procedural_tileset(
            terrain_types=["grass", "unknown_terrain", "water"],
            tiles_per_type=2,
            tile_size=32,
        )

        assert tileset_surface is not None
        # Should have tiles only for known terrains (grass and water)
        # Unknown terrain should be skipped
        assert len(metadata) <= 4  # 2 known terrains * 2 tiles each

    def test_singleton_pattern(self):
        """Test that the AI generator uses singleton pattern."""
        from neonworks.editor.ai_tileset_generator import get_ai_tileset_generator

        reset_ai_tileset_generator()

        gen1 = get_ai_tileset_generator()
        gen2 = get_ai_tileset_generator()

        assert gen1 is gen2

        reset_ai_tileset_generator()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])