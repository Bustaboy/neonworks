"""
Asset Loading System

Load and cache sprites, textures, and other game assets.
"""

from typing import Dict, Optional, Tuple
from pathlib import Path
import pygame
from dataclasses import dataclass


@dataclass
class SpriteSheet:
    """Sprite sheet data"""

    surface: pygame.Surface
    tile_width: int
    tile_height: int

    def get_sprite(self, x: int, y: int) -> pygame.Surface:
        """Get a sprite from the sheet at grid position (x, y)"""
        rect = pygame.Rect(
            x * self.tile_width, y * self.tile_height, self.tile_width, self.tile_height
        )
        sprite = pygame.Surface((self.tile_width, self.tile_height), pygame.SRCALPHA)
        sprite.blit(self.surface, (0, 0), rect)
        return sprite

    def get_sprite_by_index(self, index: int, columns: int) -> pygame.Surface:
        """Get a sprite by its index in the sheet"""
        x = index % columns
        y = index // columns
        return self.get_sprite(x, y)


class AssetManager:
    """
    Manages loading and caching of game assets.

    Features:
    - Sprite/texture loading with caching
    - Sprite sheet support
    - Color key transparency
    - Asset preloading
    - Memory management
    """

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize asset manager.

        Args:
            base_path: Base path for asset loading. Defaults to 'assets/'
        """
        self.base_path = Path(base_path) if base_path else Path("assets")

        # Asset caches
        self._sprites: Dict[str, pygame.Surface] = {}
        self._sprite_sheets: Dict[str, SpriteSheet] = {}
        self._sounds: Dict[str, pygame.mixer.Sound] = {}

        # Asset info
        self._asset_sizes: Dict[str, int] = {}  # Track memory usage

        # Placeholder surfaces for missing assets
        self._create_placeholders()

    def _create_placeholders(self):
        """Create placeholder graphics for missing assets"""
        # Missing texture placeholder (magenta and black checkerboard)
        self._missing_texture = pygame.Surface((32, 32))
        for y in range(32):
            for x in range(32):
                color = (255, 0, 255) if (x // 8 + y // 8) % 2 == 0 else (0, 0, 0)
                self._missing_texture.set_at((x, y), color)

    # ========== Sprite Loading ==========

    def load_sprite(
        self,
        path: str,
        color_key: Optional[Tuple[int, int, int]] = None,
        alpha: bool = True,
    ) -> pygame.Surface:
        """
        Load a sprite from file.

        Args:
            path: Path to sprite file relative to base_path
            color_key: Color to treat as transparent (e.g., (255, 0, 255) for magenta)
            alpha: Whether to convert with alpha channel

        Returns:
            Loaded sprite surface
        """
        # Check cache
        cache_key = f"{path}_{color_key}_{alpha}"
        if cache_key in self._sprites:
            return self._sprites[cache_key]

        full_path = self.base_path / path

        try:
            # Load the image
            if alpha:
                sprite = pygame.image.load(str(full_path)).convert_alpha()
            else:
                sprite = pygame.image.load(str(full_path)).convert()

            # Apply color key if specified
            if color_key:
                sprite.set_colorkey(color_key)

            # Cache the sprite
            self._sprites[cache_key] = sprite
            self._asset_sizes[cache_key] = (
                sprite.get_width() * sprite.get_height() * 4
            )  # Rough size estimate

            print(f"✓ Loaded sprite: {path}")
            return sprite

        except (pygame.error, FileNotFoundError) as e:
            print(f"✗ Failed to load sprite '{path}': {e}")
            print(f"  Using placeholder texture")
            # Cache the placeholder to avoid repeated load attempts
            placeholder = self._missing_texture.copy()
            self._sprites[cache_key] = placeholder
            self._asset_sizes[cache_key] = 32 * 32 * 4
            return placeholder

    def load_sprite_sheet(
        self,
        path: str,
        tile_width: int,
        tile_height: int,
        color_key: Optional[Tuple[int, int, int]] = None,
    ) -> SpriteSheet:
        """
        Load a sprite sheet.

        Args:
            path: Path to sprite sheet file
            tile_width: Width of each tile in pixels
            tile_height: Height of each tile in pixels
            color_key: Color to treat as transparent

        Returns:
            SpriteSheet object
        """
        # Check cache
        cache_key = f"{path}_{tile_width}_{tile_height}_{color_key}"
        if cache_key in self._sprite_sheets:
            return self._sprite_sheets[cache_key]

        full_path = self.base_path / path

        try:
            # Load the sheet
            surface = pygame.image.load(str(full_path)).convert_alpha()

            # Apply color key if specified
            if color_key:
                surface.set_colorkey(color_key)

            # Create sprite sheet
            sheet = SpriteSheet(surface, tile_width, tile_height)

            # Cache it
            self._sprite_sheets[cache_key] = sheet
            self._asset_sizes[cache_key] = (
                surface.get_width() * surface.get_height() * 4
            )

            print(f"✓ Loaded sprite sheet: {path} ({tile_width}x{tile_height})")
            return sheet

        except (pygame.error, FileNotFoundError) as e:
            print(f"✗ Failed to load sprite sheet '{path}': {e}")
            # Return a placeholder sheet
            placeholder_surface = pygame.Surface((tile_width, tile_height))
            placeholder_surface.fill((255, 0, 255))
            return SpriteSheet(placeholder_surface, tile_width, tile_height)

    def scale_sprite(self, sprite: pygame.Surface, scale: float) -> pygame.Surface:
        """
        Scale a sprite by a factor.

        Args:
            sprite: Sprite to scale
            scale: Scale factor (1.0 = no change, 2.0 = double size)

        Returns:
            Scaled sprite
        """
        new_width = int(sprite.get_width() * scale)
        new_height = int(sprite.get_height() * scale)
        return pygame.transform.scale(sprite, (new_width, new_height))

    def rotate_sprite(self, sprite: pygame.Surface, angle: float) -> pygame.Surface:
        """
        Rotate a sprite.

        Args:
            sprite: Sprite to rotate
            angle: Angle in degrees (positive = counter-clockwise)

        Returns:
            Rotated sprite
        """
        return pygame.transform.rotate(sprite, angle)

    def flip_sprite(
        self, sprite: pygame.Surface, flip_x: bool = False, flip_y: bool = False
    ) -> pygame.Surface:
        """
        Flip a sprite horizontally and/or vertically.

        Args:
            sprite: Sprite to flip
            flip_x: Flip horizontally
            flip_y: Flip vertically

        Returns:
            Flipped sprite
        """
        return pygame.transform.flip(sprite, flip_x, flip_y)

    # ========== Batch Loading ==========

    def preload_sprites(self, paths: list):
        """
        Preload a list of sprites.

        Useful for loading screens to load all assets upfront.
        """
        total = len(paths)
        for i, path in enumerate(paths):
            self.load_sprite(path)
            if (i + 1) % 10 == 0 or i == total - 1:
                print(f"Preloading assets: {i+1}/{total}")

    # ========== Cache Management ==========

    def clear_cache(self):
        """Clear all cached assets"""
        self._sprites.clear()
        self._sprite_sheets.clear()
        self._sounds.clear()
        self._asset_sizes.clear()
        print("Asset cache cleared")

    def get_memory_usage(self) -> int:
        """Get approximate memory usage of cached assets in bytes"""
        return sum(self._asset_sizes.values())

    def get_cache_info(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            "sprites": len(self._sprites),
            "sprite_sheets": len(self._sprite_sheets),
            "sounds": len(self._sounds),
            "memory_bytes": self.get_memory_usage(),
            "memory_mb": self.get_memory_usage() / (1024 * 1024),
        }

    # ========== Utility ==========

    def has_sprite(self, path: str) -> bool:
        """Check if a sprite is in the cache"""
        return any(path in key for key in self._sprites.keys())

    def remove_sprite(self, path: str):
        """Remove a sprite from the cache"""
        to_remove = [key for key in self._sprites.keys() if path in key]
        for key in to_remove:
            del self._sprites[key]
            if key in self._asset_sizes:
                del self._asset_sizes[key]


# Global asset manager instance
_global_asset_manager: Optional[AssetManager] = None


def get_asset_manager(base_path: Optional[Path] = None) -> AssetManager:
    """Get or create the global asset manager"""
    global _global_asset_manager
    if _global_asset_manager is None:
        _global_asset_manager = AssetManager(base_path)
    return _global_asset_manager


def set_asset_manager(manager: AssetManager):
    """Set the global asset manager"""
    global _global_asset_manager
    _global_asset_manager = manager
