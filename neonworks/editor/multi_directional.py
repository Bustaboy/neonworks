"""
Multi-Directional Sprite Generator

Generate sprites facing different directions (4-way, 8-way) from a single
source sprite or text prompt. Supports both AI-powered and procedural methods.

Features:
- 4-way directional sprites (N, E, S, W)
- 8-way directional sprites (N, NE, E, SE, S, SW, W, NW)
- AI-powered generation from text prompts
- Flip/mirror-based generation for symmetrical characters
- Rotation-based generation for vehicles/objects
- Consistent character appearance across all directions

Hardware Requirements:
- CPU: Any (procedural methods)
- GPU: RTX 3060 / RX 6600 XT or better (AI methods, 6+ GB VRAM)

Author: NeonWorks Team
License: MIT
"""

from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageOps

# Optional AI imports
try:
    from editor.sd_sprite_generator import (
        DIFFUSERS_AVAILABLE,
        SDSpriteGenerator,
        SpriteGenerationConfig,
    )
except ImportError:
    DIFFUSERS_AVAILABLE = False


class Direction(Enum):
    """Cardinal and ordinal directions."""

    # Cardinal (4-way)
    NORTH = "north"
    EAST = "east"
    SOUTH = "south"
    WEST = "west"

    # Ordinal (8-way)
    NORTH_EAST = "north_east"
    SOUTH_EAST = "south_east"
    SOUTH_WEST = "south_west"
    NORTH_WEST = "north_west"

    @property
    def angle(self) -> float:
        """Get angle in degrees (0 = North, clockwise)."""
        angles = {
            Direction.NORTH: 0,
            Direction.NORTH_EAST: 45,
            Direction.EAST: 90,
            Direction.SOUTH_EAST: 135,
            Direction.SOUTH: 180,
            Direction.SOUTH_WEST: 225,
            Direction.WEST: 270,
            Direction.NORTH_WEST: 315,
        }
        return angles[self]

    @property
    def vector(self) -> Tuple[float, float]:
        """Get direction as normalized 2D vector (x, y)."""
        angle_rad = math.radians(self.angle)
        return (math.sin(angle_rad), -math.cos(angle_rad))

    @classmethod
    def cardinal_4(cls) -> List[Direction]:
        """Get 4 cardinal directions."""
        return [cls.NORTH, cls.EAST, cls.SOUTH, cls.WEST]

    @classmethod
    def full_8(cls) -> List[Direction]:
        """Get all 8 directions."""
        return [
            cls.NORTH,
            cls.NORTH_EAST,
            cls.EAST,
            cls.SOUTH_EAST,
            cls.SOUTH,
            cls.SOUTH_WEST,
            cls.WEST,
            cls.NORTH_WEST,
        ]


@dataclass
class DirectionalSpriteSet:
    """Container for multi-directional sprite set."""

    sprites: Dict[Direction, Image.Image]
    metadata: Dict[str, Any]

    def get(self, direction: Direction) -> Optional[Image.Image]:
        """Get sprite for direction."""
        return self.sprites.get(direction)

    def save(self, output_dir: str | Path, prefix: str = "sprite"):
        """
        Save all sprites to directory.

        Args:
            output_dir: Directory to save sprites
            prefix: Filename prefix
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        for direction, sprite in self.sprites.items():
            filename = f"{prefix}_{direction.value}.png"
            sprite.save(output_dir / filename)

        # Save metadata
        metadata_path = output_dir / f"{prefix}_metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(self.metadata, f, indent=2)

        print(f"Saved {len(self.sprites)} directional sprites to {output_dir}")

    def save_sprite_sheet(self, output_path: str | Path, layout: str = "horizontal") -> Image.Image:
        """
        Save sprites as a sprite sheet.

        Args:
            output_path: Output file path
            layout: Layout (horizontal, vertical, grid)

        Returns:
            Sprite sheet image
        """
        if not self.sprites:
            raise ValueError("No sprites to save")

        # Get sprite size (assume all same size)
        first_sprite = next(iter(self.sprites.values()))
        sprite_width, sprite_height = first_sprite.size
        num_sprites = len(self.sprites)

        # Determine sheet dimensions
        if layout == "horizontal":
            sheet_width = sprite_width * num_sprites
            sheet_height = sprite_height
            cols = num_sprites
            rows = 1
        elif layout == "vertical":
            sheet_width = sprite_width
            sheet_height = sprite_height * num_sprites
            cols = 1
            rows = num_sprites
        elif layout == "grid":
            cols = int(math.ceil(math.sqrt(num_sprites)))
            rows = int(math.ceil(num_sprites / cols))
            sheet_width = sprite_width * cols
            sheet_height = sprite_height * rows
        else:
            raise ValueError(f"Unknown layout: {layout}")

        # Create sprite sheet
        sheet = Image.new("RGBA", (sheet_width, sheet_height), (0, 0, 0, 0))

        # Paste sprites
        directions = Direction.full_8() if num_sprites == 8 else Direction.cardinal_4()

        for i, direction in enumerate(directions):
            if direction not in self.sprites:
                continue

            sprite = self.sprites[direction]

            if layout == "horizontal":
                x = i * sprite_width
                y = 0
            elif layout == "vertical":
                x = 0
                y = i * sprite_height
            else:  # grid
                col = i % cols
                row = i // cols
                x = col * sprite_width
                y = row * sprite_height

            sheet.paste(sprite, (x, y), sprite if sprite.mode == "RGBA" else None)

        # Save
        sheet.save(output_path)
        print(f"Saved sprite sheet to {output_path}")
        return sheet


@dataclass
class DirectionalConfig:
    """Configuration for directional sprite generation."""

    source_sprite: Optional[Image.Image] = None
    text_prompt: Optional[str] = None

    # Directional settings
    num_directions: int = 4  # 4 or 8
    front_direction: Direction = Direction.SOUTH

    # Generation method
    method: str = "auto"  # auto, ai, flip, rotate

    # Flip/mirror settings
    symmetric: bool = True  # Character is left-right symmetric
    flip_directions: List[Tuple[Direction, Direction]] = None  # Which to flip

    # AI generation settings
    ai_config: Optional[SpriteGenerationConfig] = None
    consistency_seed: bool = True  # Use consistent seed for similar appearance

    # Post-processing
    resize_to: Optional[Tuple[int, int]] = None
    remove_background: bool = False

    def __post_init__(self):
        """Initialize default flip pairs."""
        if self.flip_directions is None:
            # Default: flip West from East, NW from NE, SW from SE
            self.flip_directions = [
                (Direction.EAST, Direction.WEST),
                (Direction.NORTH_EAST, Direction.NORTH_WEST),
                (Direction.SOUTH_EAST, Direction.SOUTH_WEST),
            ]


class MultiDirectionalGenerator:
    """
    Generate sprites in multiple directions.

    Supports procedural methods (flip/rotate) and AI-powered generation
    for consistent multi-directional sprite sets.
    """

    def __init__(self, use_ai: bool = True):
        """
        Initialize multi-directional generator.

        Args:
            use_ai: Enable AI-powered generation if available
        """
        self.use_ai = use_ai and DIFFUSERS_AVAILABLE
        self.sd_generator = None

        if self.use_ai:
            try:
                self.sd_generator = SDSpriteGenerator()
                print("AI-powered directional generation enabled")
            except Exception as e:
                print(f"Could not initialize AI generator: {e}")
                print("Will use procedural methods only")
                self.use_ai = False

    def generate(self, config: DirectionalConfig) -> DirectionalSpriteSet:
        """
        Generate multi-directional sprite set.

        Args:
            config: Directional generation configuration

        Returns:
            Set of directional sprites
        """
        # Determine directions to generate
        directions = Direction.full_8() if config.num_directions == 8 else Direction.cardinal_4()

        # Select method
        method = config.method
        if method == "auto":
            if config.text_prompt and self.use_ai:
                method = "ai"
            elif config.source_sprite and config.symmetric:
                method = "flip"
            elif config.source_sprite:
                method = "rotate"
            else:
                raise ValueError("Must provide either source_sprite or text_prompt")

        print(f"Generating {config.num_directions}-way sprites using {method} method")

        # Generate sprites
        if method == "ai":
            sprites = self._generate_ai(config, directions)
        elif method == "flip":
            sprites = self._generate_flip(config, directions)
        elif method == "rotate":
            sprites = self._generate_rotate(config, directions)
        else:
            raise ValueError(f"Unknown method: {method}")

        # Create sprite set
        sprite_set = DirectionalSpriteSet(
            sprites=sprites,
            metadata={
                "num_directions": config.num_directions,
                "method": method,
                "front_direction": config.front_direction.value,
                "symmetric": config.symmetric,
            },
        )

        print(f"Generated {len(sprites)} directional sprites")
        return sprite_set

    def _generate_ai(
        self, config: DirectionalConfig, directions: List[Direction]
    ) -> Dict[Direction, Image.Image]:
        """Generate sprites using AI for each direction."""
        if not self.sd_generator:
            raise ValueError("AI generator not available")

        if not config.text_prompt:
            raise ValueError("text_prompt required for AI generation")

        sprites = {}

        # Base configuration
        if config.ai_config is None:
            ai_config = SpriteGenerationConfig(
                prompt=config.text_prompt,
                width=64,
                height=64,
                sprite_style="pixel-art",
                num_images=1,
            )
        else:
            ai_config = config.ai_config

        # Base seed for consistency
        base_seed = ai_config.seed or 42

        # Direction keywords
        direction_keywords = {
            Direction.NORTH: "back view, facing away, rear view",
            Direction.SOUTH: "front view, facing forward, frontal view",
            Direction.EAST: "side view, facing right, right side",
            Direction.WEST: "side view, facing left, left side",
            Direction.NORTH_EAST: "three-quarter back view, facing back-right",
            Direction.NORTH_WEST: "three-quarter back view, facing back-left",
            Direction.SOUTH_EAST: "three-quarter front view, facing front-right",
            Direction.SOUTH_WEST: "three-quarter front view, facing front-left",
        }

        for i, direction in enumerate(directions):
            print(f"Generating {direction.value} sprite...")

            # Modify prompt with direction
            dir_keywords = direction_keywords.get(direction, "")
            directional_prompt = f"{config.text_prompt}, {dir_keywords}"

            ai_config.prompt = directional_prompt

            # Use consistent seed offset for each direction
            if config.consistency_seed:
                ai_config.seed = base_seed + i

            # Generate
            generated = self.sd_generator.generate(ai_config)
            sprites[direction] = generated[0].image

        return sprites

    def _generate_flip(
        self, config: DirectionalConfig, directions: List[Direction]
    ) -> Dict[Direction, Image.Image]:
        """
        Generate sprites by flipping source sprite.

        Works well for symmetric characters (humanoids, etc.).
        """
        if config.source_sprite is None:
            raise ValueError("source_sprite required for flip generation")

        sprites = {}

        # Use source for front direction
        sprites[config.front_direction] = config.source_sprite.copy()

        # Generate other directions
        # For a typical character with SOUTH as front:
        # - SOUTH: original (facing forward)
        # - NORTH: original (back view - need different sprite ideally)
        # - EAST: original facing right
        # - WEST: flip EAST horizontally

        if config.num_directions == 4:
            # 4-way: Use source for all, flip for WEST
            sprites[Direction.SOUTH] = config.source_sprite.copy()
            sprites[Direction.NORTH] = config.source_sprite.copy()  # Back view
            sprites[Direction.EAST] = config.source_sprite.copy()

            # Flip for WEST
            sprites[Direction.WEST] = ImageOps.mirror(sprites[Direction.EAST])

        else:  # 8-way
            # Generate cardinal first
            sprites[Direction.SOUTH] = config.source_sprite.copy()
            sprites[Direction.NORTH] = config.source_sprite.copy()
            sprites[Direction.EAST] = config.source_sprite.copy()
            sprites[Direction.WEST] = ImageOps.mirror(sprites[Direction.EAST])

            # Generate ordinal by flipping
            sprites[Direction.SOUTH_EAST] = config.source_sprite.copy()
            sprites[Direction.SOUTH_WEST] = ImageOps.mirror(sprites[Direction.SOUTH_EAST])
            sprites[Direction.NORTH_EAST] = config.source_sprite.copy()
            sprites[Direction.NORTH_WEST] = ImageOps.mirror(sprites[Direction.NORTH_EAST])

        # Apply custom flips if specified
        for source_dir, target_dir in config.flip_directions:
            if source_dir in sprites:
                sprites[target_dir] = ImageOps.mirror(sprites[source_dir])

        # Filter to requested directions
        sprites = {d: sprites[d] for d in directions if d in sprites}

        return sprites

    def _generate_rotate(
        self, config: DirectionalConfig, directions: List[Direction]
    ) -> Dict[Direction, Image.Image]:
        """
        Generate sprites by rotating source sprite.

        Works well for vehicles, projectiles, symmetrical objects.
        """
        if config.source_sprite is None:
            raise ValueError("source_sprite required for rotate generation")

        sprites = {}

        # Get rotation angle for front direction
        front_angle = config.front_direction.angle

        for direction in directions:
            # Calculate rotation angle
            target_angle = direction.angle
            rotation = (target_angle - front_angle) % 360

            # Rotate sprite
            rotated = config.source_sprite.rotate(
                -rotation, resample=Image.BICUBIC, expand=False  # PIL rotates counter-clockwise
            )

            sprites[direction] = rotated

        return sprites

    def generate_animation_set(
        self, config: DirectionalConfig, animation_frames: List[Image.Image], output_dir: str | Path
    ) -> Dict[Direction, List[Image.Image]]:
        """
        Generate multi-directional sprites for an animation sequence.

        Args:
            config: Directional configuration
            animation_frames: List of animation frames (assumed to be front-facing)
            output_dir: Directory to save results

        Returns:
            Dictionary mapping directions to frame lists
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        directions = Direction.full_8() if config.num_directions == 8 else Direction.cardinal_4()

        animation_set = {d: [] for d in directions}

        # Process each frame
        for frame_idx, frame in enumerate(animation_frames):
            print(f"Processing frame {frame_idx + 1}/{len(animation_frames)}")

            # Generate directional sprites for this frame
            frame_config = DirectionalConfig(
                source_sprite=frame,
                num_directions=config.num_directions,
                front_direction=config.front_direction,
                method=config.method,
                symmetric=config.symmetric,
            )

            sprite_set = self.generate(frame_config)

            # Add to animation set
            for direction in directions:
                if direction in sprite_set.sprites:
                    animation_set[direction].append(sprite_set.sprites[direction])

            # Save frame set
            sprite_set.save(output_dir / f"frame_{frame_idx:02d}", prefix="sprite")

        print(
            f"Generated {config.num_directions}-way animation with {len(animation_frames)} frames"
        )
        return animation_set

    def cleanup(self):
        """Free resources."""
        if self.sd_generator:
            self.sd_generator.cleanup()


# Convenience functions


def generate_4way_sprites(
    source: Image.Image | str | Path, method: str = "flip", output_dir: Optional[str | Path] = None
) -> DirectionalSpriteSet:
    """
    Quick 4-way sprite generation.

    Args:
        source: Source sprite or path
        method: Generation method (flip, rotate)
        output_dir: Directory to save (optional)

    Returns:
        4-directional sprite set
    """
    # Load image if path
    if isinstance(source, (str, Path)):
        source = Image.open(source)

    # Generate
    generator = MultiDirectionalGenerator(use_ai=False)
    config = DirectionalConfig(
        source_sprite=source,
        num_directions=4,
        method=method,
    )

    sprite_set = generator.generate(config)

    # Save if requested
    if output_dir:
        sprite_set.save(output_dir)

    return sprite_set


def generate_8way_sprites(
    source: Image.Image | str | Path, method: str = "flip", output_dir: Optional[str | Path] = None
) -> DirectionalSpriteSet:
    """
    Quick 8-way sprite generation.

    Args:
        source: Source sprite or path
        method: Generation method (flip, rotate)
        output_dir: Directory to save (optional)

    Returns:
        8-directional sprite set
    """
    # Load image if path
    if isinstance(source, (str, Path)):
        source = Image.open(source)

    # Generate
    generator = MultiDirectionalGenerator(use_ai=False)
    config = DirectionalConfig(
        source_sprite=source,
        num_directions=8,
        method=method,
    )

    sprite_set = generator.generate(config)

    # Save if requested
    if output_dir:
        sprite_set.save(output_dir)

    return sprite_set


if __name__ == "__main__":
    print("Multi-Directional Sprite Generator - Example Usage\n")

    # Create test sprite (circle with arrow pointing down for front)
    test_sprite = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(test_sprite)

    # Draw circle (body)
    draw.ellipse([16, 16, 48, 48], fill=(100, 150, 200, 255))

    # Draw arrow (direction indicator)
    draw.polygon([32, 48, 26, 36, 38, 36], fill=(255, 255, 255, 255))

    # Generate 4-way sprites using rotation
    print("Generating 4-way sprites using rotation...")
    sprite_set_4 = generate_4way_sprites(test_sprite, method="rotate", output_dir="test_4way")

    # Generate 8-way sprites using rotation
    print("\nGenerating 8-way sprites using rotation...")
    sprite_set_8 = generate_8way_sprites(test_sprite, method="rotate", output_dir="test_8way")

    # Create sprite sheets
    sprite_set_4.save_sprite_sheet("test_4way_sheet.png", layout="horizontal")
    sprite_set_8.save_sprite_sheet("test_8way_sheet.png", layout="grid")

    print("\nExample complete!")
