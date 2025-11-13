"""
Asset Pipeline Utilities

Image processing and optimization tools using Pillow (PIL).
Provides texture atlas generation, format conversion, and asset optimization.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pygame
from PIL import Image, ImageDraw, ImageFilter


@dataclass
class AtlasRegion:
    """Region in a texture atlas"""

    name: str
    x: int
    y: int
    width: int
    height: int

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
        }


class TextureAtlasBuilder:
    """
    Build texture atlases from multiple images.
    Combines multiple small textures into a single large texture for better performance.
    """

    def __init__(self, max_size: int = 2048, padding: int = 2):
        """
        Initialize atlas builder.

        Args:
            max_size: Maximum atlas size (width and height)
            padding: Padding between textures in pixels
        """
        self.max_size = max_size
        self.padding = padding
        self.images: List[Tuple[str, Image.Image]] = []

    def add_image(self, name: str, image_path: str):
        """Add image to atlas"""
        img = Image.open(image_path)
        self.images.append((name, img.convert("RGBA")))

    def add_pil_image(self, name: str, image: Image.Image):
        """Add PIL Image object to atlas"""
        self.images.append((name, image.convert("RGBA")))

    def build(self) -> Tuple[Image.Image, List[AtlasRegion]]:
        """
        Build texture atlas.

        Returns:
            Tuple of (atlas image, list of regions)
        """
        if not self.images:
            raise ValueError("No images added to atlas")

        # Sort images by height (descending) for better packing
        sorted_images = sorted(self.images, key=lambda x: x[1].height, reverse=True)

        # Simple shelf packing algorithm
        atlas_width = self.max_size
        atlas_height = self.max_size

        # Create atlas image
        atlas = Image.new("RGBA", (atlas_width, atlas_height), (0, 0, 0, 0))
        regions = []

        # Track current position
        current_x = self.padding
        current_y = self.padding
        row_height = 0

        for name, img in sorted_images:
            img_width, img_height = img.size

            # Check if we need to move to next row
            if current_x + img_width + self.padding > atlas_width:
                current_x = self.padding
                current_y += row_height + self.padding
                row_height = 0

            # Check if we have space
            if current_y + img_height + self.padding > atlas_height:
                raise ValueError(
                    f"Atlas size {self.max_size}x{self.max_size} too small for all images"
                )

            # Paste image
            atlas.paste(img, (current_x, current_y))

            # Add region
            regions.append(
                AtlasRegion(
                    name=name,
                    x=current_x,
                    y=current_y,
                    width=img_width,
                    height=img_height,
                )
            )

            # Update position
            current_x += img_width + self.padding
            row_height = max(row_height, img_height)

        return atlas, regions

    def build_and_save(self, output_path: str, metadata_path: Optional[str] = None):
        """
        Build atlas and save to file.

        Args:
            output_path: Path to save atlas image
            metadata_path: Path to save metadata JSON (optional)
        """
        atlas, regions = self.build()

        # Save atlas image
        atlas.save(output_path, optimize=True)

        # Save metadata if requested
        if metadata_path:
            metadata = {
                "atlas": output_path,
                "size": {"width": atlas.width, "height": atlas.height},
                "regions": [region.to_dict() for region in regions],
            }
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)

        return atlas, regions


class ImageOptimizer:
    """Optimize images for game use"""

    @staticmethod
    def optimize_for_game(
        input_path: str,
        output_path: str,
        max_size: Optional[Tuple[int, int]] = None,
        quality: int = 95,
    ) -> Image.Image:
        """
        Optimize image for game use.

        Args:
            input_path: Input image path
            output_path: Output image path
            max_size: Maximum size (width, height), None for no resizing
            quality: JPEG quality (1-100)

        Returns:
            Optimized PIL Image
        """
        img = Image.open(input_path)

        # Resize if needed
        if max_size:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Convert to appropriate format
        if img.mode in ("RGBA", "LA", "P"):
            # Has transparency - save as PNG
            img.save(output_path, "PNG", optimize=True)
        else:
            # No transparency - can use JPEG
            if output_path.lower().endswith(".jpg") or output_path.lower().endswith(
                ".jpeg"
            ):
                img.convert("RGB").save(
                    output_path, "JPEG", quality=quality, optimize=True
                )
            else:
                img.save(output_path, "PNG", optimize=True)

        return img

    @staticmethod
    def create_mipmaps(image: Image.Image, levels: int = 3) -> List[Image.Image]:
        """
        Generate mipmap levels for an image.

        Args:
            image: Source image
            levels: Number of mipmap levels to generate

        Returns:
            List of images at different resolutions
        """
        mipmaps = [image]
        current = image

        for _ in range(levels):
            width, height = current.size
            if width <= 1 or height <= 1:
                break

            new_size = (max(1, width // 2), max(1, height // 2))
            current = current.resize(new_size, Image.Resampling.LANCZOS)
            mipmaps.append(current)

        return mipmaps


class ImageEffects:
    """Apply effects to images"""

    @staticmethod
    def create_outline(
        image: Image.Image,
        outline_color: Tuple[int, int, int, int] = (0, 0, 0, 255),
        thickness: int = 1,
    ) -> Image.Image:
        """
        Create an outline around non-transparent pixels.

        Args:
            image: Source image with alpha channel
            outline_color: Color of outline (RGBA)
            thickness: Outline thickness in pixels

        Returns:
            Image with outline
        """
        img = image.convert("RGBA")

        # Create outline mask
        alpha = img.split()[3]
        outline_mask = alpha.filter(ImageFilter.MaxFilter(thickness * 2 + 1))

        # Create outline layer
        outline_layer = Image.new("RGBA", img.size, outline_color)

        # Create result
        result = Image.new("RGBA", img.size, (0, 0, 0, 0))
        result.paste(outline_layer, mask=outline_mask)
        result.paste(img, mask=alpha)

        return result

    @staticmethod
    def tint_image(image: Image.Image, color: Tuple[int, int, int]) -> Image.Image:
        """
        Tint image with a color.

        Args:
            image: Source image
            color: RGB color to tint with

        Returns:
            Tinted image
        """
        img = image.convert("RGBA")

        # Create tint layer
        tint_layer = Image.new("RGB", img.size, color)

        # Blend with original
        result = Image.blend(img.convert("RGB"), tint_layer, 0.3)

        # Restore alpha channel
        result.putalpha(img.split()[3])

        return result

    @staticmethod
    def apply_shadow(
        image: Image.Image,
        offset: Tuple[int, int] = (2, 2),
        blur_radius: int = 2,
        shadow_color: Tuple[int, int, int, int] = (0, 0, 0, 128),
    ) -> Image.Image:
        """
        Add drop shadow to image.

        Args:
            image: Source image
            offset: Shadow offset (x, y)
            blur_radius: Shadow blur radius
            shadow_color: Shadow color (RGBA)

        Returns:
            Image with shadow
        """
        img = image.convert("RGBA")

        # Create shadow layer
        shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        alpha = img.split()[3]

        # Create shadow
        shadow_layer = Image.new("RGBA", img.size, shadow_color)
        shadow.paste(shadow_layer, mask=alpha)

        # Blur shadow
        shadow = shadow.filter(ImageFilter.GaussianBlur(blur_radius))

        # Create result with padding for offset
        result_size = (
            img.size[0] + abs(offset[0]) + blur_radius * 2,
            img.size[1] + abs(offset[1]) + blur_radius * 2,
        )
        result = Image.new("RGBA", result_size, (0, 0, 0, 0))

        # Paste shadow with offset
        shadow_pos = (blur_radius + max(0, offset[0]), blur_radius + max(0, offset[1]))
        result.paste(shadow, shadow_pos, shadow)

        # Paste original image
        img_pos = (blur_radius + max(0, -offset[0]), blur_radius + max(0, -offset[1]))
        result.paste(img, img_pos, img)

        return result


class SpriteSheetExtractor:
    """Extract individual sprites from sprite sheets"""

    @staticmethod
    def extract_grid(
        image_path: str,
        tile_width: int,
        tile_height: int,
        columns: int,
        rows: int,
        spacing: int = 0,
        margin: int = 0,
    ) -> List[Image.Image]:
        """
        Extract sprites from a grid-based sprite sheet.

        Args:
            image_path: Path to sprite sheet
            tile_width: Width of each tile
            tile_height: Height of each tile
            columns: Number of columns
            rows: Number of rows
            spacing: Space between tiles
            margin: Margin around the sprite sheet

        Returns:
            List of sprite images
        """
        img = Image.open(image_path).convert("RGBA")
        sprites = []

        for row in range(rows):
            for col in range(columns):
                x = margin + col * (tile_width + spacing)
                y = margin + row * (tile_height + spacing)

                sprite = img.crop((x, y, x + tile_width, y + tile_height))
                sprites.append(sprite)

        return sprites

    @staticmethod
    def save_sprites(
        sprites: List[Image.Image], output_dir: str, prefix: str = "sprite"
    ):
        """
        Save extracted sprites to individual files.

        Args:
            sprites: List of sprite images
            output_dir: Output directory
            prefix: Filename prefix
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        for i, sprite in enumerate(sprites):
            filename = output_path / f"{prefix}_{i:04d}.png"
            sprite.save(filename, "PNG", optimize=True)


class PygameConverter:
    """Convert between PIL Images and Pygame Surfaces"""

    @staticmethod
    def pil_to_pygame(pil_image: Image.Image) -> pygame.Surface:
        """Convert PIL Image to Pygame Surface"""
        mode = pil_image.mode
        size = pil_image.size
        data = pil_image.tobytes()

        if mode == "RGBA":
            surface = pygame.image.fromstring(data, size, mode)
        elif mode == "RGB":
            surface = pygame.image.fromstring(data, size, mode)
        else:
            # Convert to RGBA first
            pil_image = pil_image.convert("RGBA")
            data = pil_image.tobytes()
            surface = pygame.image.fromstring(data, size, "RGBA")

        return surface

    @staticmethod
    def pygame_to_pil(pygame_surface: pygame.Surface) -> Image.Image:
        """Convert Pygame Surface to PIL Image"""
        size = pygame_surface.get_size()
        mode = "RGBA" if pygame_surface.get_flags() & pygame.SRCALPHA else "RGB"
        data = pygame.image.tostring(pygame_surface, mode)

        return Image.frombytes(mode, size, data)
