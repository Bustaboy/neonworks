"""
Comprehensive tests for Asset Manager and Sprite Loading

Tests sprite loading, caching, sprite sheets, and transformations.
"""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pygame
import pytest

from neonworks.rendering.animation import (
    Animation,
    AnimationBuilder,
    AnimationComponent,
    AnimationFrame,
    AnimationSystem,
)
from neonworks.rendering.assets import AssetManager, SpriteSheet


@pytest.fixture
def asset_manager(tmp_path):
    """Create asset manager with temporary directory"""
    pygame.init()
    return AssetManager(base_path=tmp_path)


@pytest.fixture
def mock_sprite():
    """Create a mock pygame surface"""
    surface = pygame.Surface((32, 32))
    surface.fill((255, 0, 0))
    return surface


class TestAssetLoading:
    """Test basic asset loading"""

    def test_asset_manager_initialization(self, tmp_path):
        """Test asset manager initializes correctly"""
        manager = AssetManager(base_path=tmp_path)

        assert manager.base_path == tmp_path
        assert len(manager._sprites) == 0
        assert manager._missing_texture is not None

    def test_load_sprite_missing_file(self, asset_manager):
        """Test loading a sprite that doesn't exist returns placeholder"""
        sprite = asset_manager.load_sprite("nonexistent.png")

        # Should return placeholder (magenta checkerboard)
        assert sprite is not None
        assert sprite.get_width() == 32
        assert sprite.get_height() == 32

    @patch("pygame.image.load")
    def test_load_sprite_success(self, mock_load, asset_manager, mock_sprite, tmp_path):
        """Test successfully loading a sprite"""
        # Create a fake image file
        image_path = tmp_path / "test.png"
        image_path.touch()

        # Mock pygame.image.load to return our mock sprite
        mock_load.return_value = mock_sprite

        sprite = asset_manager.load_sprite("test.png")

        assert sprite is not None
        mock_load.assert_called_once()

    @patch("pygame.image.load")
    def test_sprite_caching(self, mock_load, asset_manager, mock_sprite, tmp_path):
        """Test that sprites are cached after first load"""
        image_path = tmp_path / "test.png"
        image_path.touch()

        mock_load.return_value = mock_sprite

        # Load sprite twice
        sprite1 = asset_manager.load_sprite("test.png")
        sprite2 = asset_manager.load_sprite("test.png")

        # Should only load once (second call uses cache)
        assert mock_load.call_count == 1
        assert sprite1 == sprite2

    @patch("pygame.image.load")
    def test_color_key_transparency(
        self, mock_load, asset_manager, mock_sprite, tmp_path
    ):
        """Test color key transparency"""
        image_path = tmp_path / "test.png"
        image_path.touch()

        mock_load.return_value = mock_sprite

        sprite = asset_manager.load_sprite("test.png", color_key=(255, 0, 255))

        assert sprite is not None
        mock_load.assert_called_once()


class TestSpriteSheets:
    """Test sprite sheet functionality"""

    def test_sprite_sheet_creation(self):
        """Test creating a sprite sheet"""
        surface = pygame.Surface((64, 64))
        sheet = SpriteSheet(surface, tile_width=32, tile_height=32)

        assert sheet.surface == surface
        assert sheet.tile_width == 32
        assert sheet.tile_height == 32

    def test_get_sprite_from_sheet(self):
        """Test extracting a sprite from a sheet"""
        # Create a surface with two different colored tiles
        surface = pygame.Surface((64, 32))
        surface.fill((255, 0, 0), rect=(0, 0, 32, 32))
        surface.fill((0, 255, 0), rect=(32, 0, 32, 32))

        sheet = SpriteSheet(surface, tile_width=32, tile_height=32)

        # Get first sprite (red)
        sprite1 = sheet.get_sprite(0, 0)
        assert sprite1.get_at((16, 16))[:3] == (255, 0, 0)

        # Get second sprite (green)
        sprite2 = sheet.get_sprite(1, 0)
        assert sprite2.get_at((16, 16))[:3] == (0, 255, 0)

    def test_get_sprite_by_index(self):
        """Test getting sprite by index"""
        surface = pygame.Surface((64, 64))  # 2x2 grid
        sheet = SpriteSheet(surface, tile_width=32, tile_height=32)

        # Index 0: (0, 0)
        sprite0 = sheet.get_sprite_by_index(0, columns=2)
        assert sprite0 is not None

        # Index 1: (1, 0)
        sprite1 = sheet.get_sprite_by_index(1, columns=2)
        assert sprite1 is not None

        # Index 2: (0, 1)
        sprite2 = sheet.get_sprite_by_index(2, columns=2)
        assert sprite2 is not None

    @patch("pygame.image.load")
    def test_load_sprite_sheet(self, mock_load, asset_manager, tmp_path):
        """Test loading a sprite sheet"""
        image_path = tmp_path / "sheet.png"
        image_path.touch()

        surface = pygame.Surface((64, 64))
        mock_load.return_value = surface

        sheet = asset_manager.load_sprite_sheet(
            "sheet.png", tile_width=32, tile_height=32
        )

        assert isinstance(sheet, SpriteSheet)
        assert sheet.tile_width == 32
        assert sheet.tile_height == 32


class TestSpriteTransformations:
    """Test sprite transformation functions"""

    def test_scale_sprite(self, asset_manager):
        """Test scaling a sprite"""
        original = pygame.Surface((32, 32))
        scaled = asset_manager.scale_sprite(original, 2.0)

        assert scaled.get_width() == 64
        assert scaled.get_height() == 64

    def test_rotate_sprite(self, asset_manager):
        """Test rotating a sprite"""
        original = pygame.Surface((32, 32))
        rotated = asset_manager.rotate_sprite(original, 90)

        # Rotated sprite should exist (size may change due to rotation)
        assert rotated is not None

    def test_flip_sprite_horizontal(self, asset_manager):
        """Test flipping sprite horizontally"""
        original = pygame.Surface((32, 32))
        original.fill((255, 0, 0), rect=(0, 0, 16, 32))  # Left half red

        flipped = asset_manager.flip_sprite(original, flip_x=True)

        # After flip, right half should be red
        assert flipped.get_at((24, 16))[:3] == (255, 0, 0)

    def test_flip_sprite_vertical(self, asset_manager):
        """Test flipping sprite vertically"""
        original = pygame.Surface((32, 32))
        original.fill((0, 255, 0), rect=(0, 0, 32, 16))  # Top half green

        flipped = asset_manager.flip_sprite(original, flip_y=True)

        # After flip, bottom half should be green
        assert flipped.get_at((16, 24))[:3] == (0, 255, 0)


class TestCacheManagement:
    """Test asset cache management"""

    @patch("pygame.image.load")
    def test_clear_cache(self, mock_load, asset_manager, mock_sprite, tmp_path):
        """Test clearing the asset cache"""
        image_path = tmp_path / "test.png"
        image_path.touch()

        mock_load.return_value = mock_sprite

        # Load a sprite
        asset_manager.load_sprite("test.png")

        assert len(asset_manager._sprites) > 0

        # Clear cache
        asset_manager.clear_cache()

        assert len(asset_manager._sprites) == 0

    @patch("pygame.image.load")
    def test_memory_usage_tracking(self, mock_load, asset_manager, tmp_path):
        """Test memory usage tracking"""
        image_path = tmp_path / "test.png"
        image_path.touch()

        surface = pygame.Surface((32, 32))
        mock_load.return_value = surface

        # Load a sprite
        asset_manager.load_sprite("test.png")

        # Check memory usage
        memory = asset_manager.get_memory_usage()
        assert memory > 0

    @patch("pygame.image.load")
    def test_cache_info(self, mock_load, asset_manager, tmp_path):
        """Test getting cache information"""
        image_path = tmp_path / "test.png"
        image_path.touch()

        surface = pygame.Surface((32, 32))
        mock_load.return_value = surface

        asset_manager.load_sprite("test.png")

        info = asset_manager.get_cache_info()

        assert "sprites" in info
        assert "memory_bytes" in info
        assert info["sprites"] == 1

    @patch("pygame.image.load")
    def test_has_sprite(self, mock_load, asset_manager, mock_sprite, tmp_path):
        """Test checking if sprite is in cache"""
        image_path = tmp_path / "test.png"
        image_path.touch()

        mock_load.return_value = mock_sprite

        assert not asset_manager.has_sprite("test.png")

        asset_manager.load_sprite("test.png")

        assert asset_manager.has_sprite("test.png")

    @patch("pygame.image.load")
    def test_remove_sprite(self, mock_load, asset_manager, mock_sprite, tmp_path):
        """Test removing a sprite from cache"""
        image_path = tmp_path / "test.png"
        image_path.touch()

        mock_load.return_value = mock_sprite

        asset_manager.load_sprite("test.png")
        assert asset_manager.has_sprite("test.png")

        asset_manager.remove_sprite("test.png")
        assert not asset_manager.has_sprite("test.png")


class TestAnimation:
    """Test animation system"""

    def test_animation_frame_creation(self):
        """Test creating animation frames"""
        sprite = pygame.Surface((32, 32))
        frame = AnimationFrame(sprite, duration=0.1)

        assert frame.sprite == sprite
        assert frame.duration == 0.1

    def test_animation_creation(self):
        """Test creating an animation"""
        sprite1 = pygame.Surface((32, 32))
        sprite2 = pygame.Surface((32, 32))

        frames = [AnimationFrame(sprite1, 0.1), AnimationFrame(sprite2, 0.1)]

        animation = Animation("walk", frames, loop=True)

        assert animation.name == "walk"
        assert len(animation.frames) == 2
        assert animation.loop is True

    def test_animation_total_duration(self):
        """Test calculating total animation duration"""
        sprite = pygame.Surface((32, 32))
        frames = [
            AnimationFrame(sprite, 0.1),
            AnimationFrame(sprite, 0.2),
            AnimationFrame(sprite, 0.1),
        ]

        animation = Animation("test", frames)

        assert animation.get_total_duration() == 0.4

    def test_animation_component(self):
        """Test animation component"""
        component = AnimationComponent()

        assert component.current_animation is None
        assert component.animations == {}
        assert component.current_frame == 0
        assert component.playing is True

    def test_animation_system_update(self):
        """Test animation system updates frames"""
        system = AnimationSystem()

        sprite1 = pygame.Surface((32, 32))
        sprite2 = pygame.Surface((32, 32))

        frames = [AnimationFrame(sprite1, 0.1), AnimationFrame(sprite2, 0.1)]

        animation = Animation("test", frames, loop=True)

        component = AnimationComponent()
        component.animations["test"] = animation
        component.current_animation = "test"

        # First frame
        current_sprite = system.update_animation(component, 0.05)
        assert component.current_frame == 0

        # Should advance to next frame
        current_sprite = system.update_animation(component, 0.06)
        assert component.current_frame == 1

        # Should loop back to first frame
        current_sprite = system.update_animation(component, 0.11)
        assert component.current_frame == 0

    def test_animation_builder(self):
        """Test animation builder helper"""
        sprite1 = pygame.Surface((32, 32))
        sprite2 = pygame.Surface((32, 32))

        animation = (
            AnimationBuilder("walk", loop=True)
            .add_frame(sprite1, 0.1)
            .add_frame(sprite2, 0.1)
            .build()
        )

        assert animation.name == "walk"
        assert len(animation.frames) == 2
        assert animation.loop is True

    def test_play_animation(self):
        """Test playing an animation"""
        system = AnimationSystem()

        sprite = pygame.Surface((32, 32))
        frames = [AnimationFrame(sprite, 0.1)]
        animation = Animation("idle", frames)

        component = AnimationComponent()
        component.animations["idle"] = animation

        system.play_animation(component, "idle")

        assert component.current_animation == "idle"
        assert component.current_frame == 0
        assert component.playing is True

    def test_pause_resume_animation(self):
        """Test pausing and resuming animation"""
        system = AnimationSystem()

        sprite = pygame.Surface((32, 32))
        frames = [AnimationFrame(sprite, 0.1)]
        animation = Animation("test", frames)

        component = AnimationComponent()
        component.animations["test"] = animation
        component.current_animation = "test"

        system.pause_animation(component)
        assert component.playing is False

        system.resume_animation(component)
        assert component.playing is True


# Run tests with: pytest engine/tests/test_asset_manager.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
