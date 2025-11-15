"""
Generate Sample Character Generator Art Assets

Creates placeholder sprite assets for the character generator system
using procedural generation. These serve as examples and placeholders
until actual art assets are created.

Generates assets matching the structure in neonworks/data/character_parts.json:
- Bodies (base_body, knight, mage, rogue)
- Hair (short, long, mohawk, bun)
- Clothing (tunic, robe, armor, cape)
- Accessories (helmet, amulet, cape, wings)
- Weapons (sword, staff, bow, dagger)
- Faces (human, elf, orc, demon)

Author: NeonWorks Team
License: MIT
"""

from __future__ import annotations

import os
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from PIL import Image, ImageDraw, ImageFilter


# Standard sprite size for character generator
SPRITE_SIZE = (64, 64)
MASK_SIZE = (64, 64)


class ProceduralSpriteGenerator:
    """Generate procedural placeholder sprites."""

    def __init__(self, size: Tuple[int, int] = SPRITE_SIZE):
        """
        Initialize sprite generator.

        Args:
            size: Sprite size (width, height)
        """
        self.size = size

    def create_base_body(self, style: str = "male") -> Tuple[Image.Image, Image.Image]:
        """
        Create base body sprite and mask.

        Args:
            style: Body style (male, female, athletic, stocky)

        Returns:
            (sprite, mask) tuple
        """
        sprite = Image.new("RGBA", self.size, (0, 0, 0, 0))
        mask = Image.new("L", self.size, 0)

        draw_sprite = ImageDraw.Draw(sprite)
        draw_mask = ImageDraw.Draw(mask)

        # Base skin color (will be recolored via mask)
        skin_color = (200, 180, 160, 255)

        # Body proportions based on style
        if style == "male":
            # Head
            head_y = 12
            head_size = 14
            # Torso
            torso_y = head_y + head_size
            torso_width = 20
            torso_height = 20
            # Legs
            leg_y = torso_y + torso_height
            leg_width = 8
            leg_height = 16

        elif style == "female":
            head_y = 12
            head_size = 12
            torso_y = head_y + head_size
            torso_width = 16
            torso_height = 18
            leg_y = torso_y + torso_height
            leg_width = 7
            leg_height = 18

        else:  # Default
            head_y = 12
            head_size = 13
            torso_y = head_y + head_size
            torso_width = 18
            torso_height = 19
            leg_y = torso_y + torso_height
            leg_width = 8
            leg_height = 17

        cx = self.size[0] // 2

        # Draw head
        head_box = [cx - head_size // 2, head_y, cx + head_size // 2, head_y + head_size]
        draw_sprite.ellipse(head_box, fill=skin_color)
        draw_mask.ellipse(head_box, fill=255)

        # Draw neck
        neck_width = head_size // 3
        neck_height = 3
        neck_box = [
            cx - neck_width // 2,
            head_y + head_size - 2,
            cx + neck_width // 2,
            head_y + head_size + neck_height,
        ]
        draw_sprite.rectangle(neck_box, fill=skin_color)
        draw_mask.rectangle(neck_box, fill=255)

        # Draw torso
        torso_box = [cx - torso_width // 2, torso_y, cx + torso_width // 2, torso_y + torso_height]
        draw_sprite.rectangle(torso_box, fill=skin_color)
        draw_mask.rectangle(torso_box, fill=255)

        # Draw arms
        arm_width = 5
        arm_height = torso_height + 4
        # Left arm
        left_arm_box = [
            cx - torso_width // 2 - arm_width,
            torso_y + 2,
            cx - torso_width // 2,
            torso_y + 2 + arm_height,
        ]
        draw_sprite.rectangle(left_arm_box, fill=skin_color)
        draw_mask.rectangle(left_arm_box, fill=255)

        # Right arm
        right_arm_box = [
            cx + torso_width // 2,
            torso_y + 2,
            cx + torso_width // 2 + arm_width,
            torso_y + 2 + arm_height,
        ]
        draw_sprite.rectangle(right_arm_box, fill=skin_color)
        draw_mask.rectangle(right_arm_box, fill=255)

        # Draw legs
        # Left leg
        left_leg_box = [cx - leg_width - 1, leg_y, cx - 1, leg_y + leg_height]
        draw_sprite.rectangle(left_leg_box, fill=skin_color)
        draw_mask.rectangle(left_leg_box, fill=255)

        # Right leg
        right_leg_box = [cx + 1, leg_y, cx + leg_width + 1, leg_y + leg_height]
        draw_sprite.rectangle(right_leg_box, fill=skin_color)
        draw_mask.rectangle(right_leg_box, fill=255)

        return sprite, mask

    def create_hair(self, style: str = "short") -> Tuple[Image.Image, Image.Image]:
        """
        Create hair sprite and mask.

        Args:
            style: Hair style (short, long, mohawk, bun, ponytail)

        Returns:
            (sprite, mask) tuple
        """
        sprite = Image.new("RGBA", self.size, (0, 0, 0, 0))
        mask = Image.new("L", self.size, 0)

        draw_sprite = ImageDraw.Draw(sprite)
        draw_mask = ImageDraw.Draw(mask)

        hair_color = (100, 60, 20, 255)  # Brown (will be recolored)
        cx = self.size[0] // 2
        head_y = 12
        head_size = 14

        if style == "short":
            # Simple cap covering top of head
            hair_box = [cx - head_size // 2, head_y, cx + head_size // 2, head_y + head_size // 2]
            draw_sprite.ellipse(hair_box, fill=hair_color)
            draw_mask.ellipse(hair_box, fill=255)

        elif style == "long":
            # Top part
            hair_top = [cx - head_size // 2, head_y, cx + head_size // 2, head_y + head_size // 2]
            draw_sprite.ellipse(hair_top, fill=hair_color)
            draw_mask.ellipse(hair_top, fill=255)

            # Long flowing part
            hair_long = [
                cx - head_size // 2 - 2,
                head_y + head_size // 2,
                cx + head_size // 2 + 2,
                head_y + head_size + 15,
            ]
            draw_sprite.rectangle(hair_long, fill=hair_color)
            draw_mask.rectangle(hair_long, fill=255)

        elif style == "mohawk":
            # Center strip
            mohawk_width = 8
            mohawk_height = 18
            mohawk_box = [
                cx - mohawk_width // 2,
                head_y - 4,
                cx + mohawk_width // 2,
                head_y + mohawk_height,
            ]
            draw_sprite.rectangle(mohawk_box, fill=hair_color)
            draw_mask.rectangle(mohawk_box, fill=255)

        elif style == "bun":
            # Base hair
            hair_base = [cx - head_size // 2, head_y, cx + head_size // 2, head_y + head_size // 2]
            draw_sprite.ellipse(hair_base, fill=hair_color)
            draw_mask.ellipse(hair_base, fill=255)

            # Bun on top
            bun_size = 8
            bun_box = [cx - bun_size // 2, head_y - bun_size, cx + bun_size // 2, head_y]
            draw_sprite.ellipse(bun_box, fill=hair_color)
            draw_mask.ellipse(bun_box, fill=255)

        else:  # Default: short
            hair_box = [cx - head_size // 2, head_y, cx + head_size // 2, head_y + head_size // 2]
            draw_sprite.ellipse(hair_box, fill=hair_color)
            draw_mask.ellipse(hair_box, fill=255)

        return sprite, mask

    def create_clothing(self, style: str = "tunic") -> Tuple[Image.Image, Image.Image]:
        """
        Create clothing sprite and mask.

        Args:
            style: Clothing style (tunic, robe, armor, dress)

        Returns:
            (sprite, mask) tuple
        """
        sprite = Image.new("RGBA", self.size, (0, 0, 0, 0))
        mask = Image.new("L", self.size, 0)

        draw_sprite = ImageDraw.Draw(sprite)
        draw_mask = ImageDraw.Draw(mask)

        cloth_color = (80, 100, 150, 255)  # Blue (will be recolored)
        cx = self.size[0] // 2

        if style == "tunic":
            # Simple shirt
            torso_box = [cx - 10, 26, cx + 10, 46]
            draw_sprite.rectangle(torso_box, fill=cloth_color)
            draw_mask.rectangle(torso_box, fill=255)

            # Sleeves
            sleeve_left = [cx - 15, 28, cx - 10, 40]
            sleeve_right = [cx + 10, 28, cx + 15, 40]
            draw_sprite.rectangle(sleeve_left, fill=cloth_color)
            draw_sprite.rectangle(sleeve_right, fill=cloth_color)
            draw_mask.rectangle(sleeve_left, fill=255)
            draw_mask.rectangle(sleeve_right, fill=255)

        elif style == "robe":
            # Long flowing robe
            robe_box = [cx - 12, 26, cx + 12, 60]
            draw_sprite.rectangle(robe_box, fill=cloth_color)
            draw_mask.rectangle(robe_box, fill=255)

            # Wide sleeves
            sleeve_left = [cx - 18, 26, cx - 12, 50]
            sleeve_right = [cx + 12, 26, cx + 18, 50]
            draw_sprite.rectangle(sleeve_left, fill=cloth_color)
            draw_sprite.rectangle(sleeve_right, fill=cloth_color)
            draw_mask.rectangle(sleeve_left, fill=255)
            draw_mask.rectangle(sleeve_right, fill=255)

        elif style == "armor":
            # Chest plate
            chest_box = [cx - 11, 26, cx + 11, 42]
            draw_sprite.rectangle(chest_box, fill=(150, 150, 160, 255))  # Metal
            draw_mask.rectangle(chest_box, fill=255)

            # Shoulder plates
            shoulder_left = [cx - 16, 26, cx - 11, 34]
            shoulder_right = [cx + 11, 26, cx + 16, 34]
            draw_sprite.rectangle(shoulder_left, fill=(150, 150, 160, 255))
            draw_sprite.rectangle(shoulder_right, fill=(150, 150, 160, 255))
            draw_mask.rectangle(shoulder_left, fill=255)
            draw_mask.rectangle(shoulder_right, fill=255)

        else:  # Default: tunic
            torso_box = [cx - 10, 26, cx + 10, 46]
            draw_sprite.rectangle(torso_box, fill=cloth_color)
            draw_mask.rectangle(torso_box, fill=255)

        return sprite, mask

    def create_weapon(self, style: str = "sword") -> Tuple[Image.Image, Image.Image]:
        """
        Create weapon sprite and mask.

        Args:
            style: Weapon style (sword, staff, bow, dagger, axe)

        Returns:
            (sprite, mask) tuple
        """
        sprite = Image.new("RGBA", self.size, (0, 0, 0, 0))
        mask = Image.new("L", self.size, 0)

        draw_sprite = ImageDraw.Draw(sprite)
        draw_mask = ImageDraw.Draw(mask)

        cx = self.size[0] // 2

        if style == "sword":
            # Blade
            blade_color = (180, 180, 200, 255)
            blade_box = [cx + 12, 30, cx + 15, 55]
            draw_sprite.rectangle(blade_box, fill=blade_color)
            draw_mask.rectangle(blade_box, fill=255)

            # Hilt
            hilt_color = (120, 80, 40, 255)
            hilt_box = [cx + 10, 52, cx + 17, 58]
            draw_sprite.rectangle(hilt_box, fill=hilt_color)
            draw_mask.rectangle(hilt_box, fill=255)

        elif style == "staff":
            # Wooden staff
            wood_color = (120, 80, 40, 255)
            staff_box = [cx + 12, 20, cx + 15, 62]
            draw_sprite.rectangle(staff_box, fill=wood_color)
            draw_mask.rectangle(staff_box, fill=255)

            # Orb on top
            orb_color = (100, 100, 255, 255)
            orb_box = [cx + 9, 16, cx + 18, 25]
            draw_sprite.ellipse(orb_box, fill=orb_color)
            draw_mask.ellipse(orb_box, fill=255)

        elif style == "bow":
            # Bow arc
            bow_color = (120, 80, 40, 255)
            # Simple arc representation
            draw_sprite.arc([cx + 8, 25, cx + 20, 55], 270, 90, fill=bow_color, width=2)
            # String
            draw_sprite.line([(cx + 14, 25), (cx + 14, 55)], fill=(220, 220, 220, 255), width=1)

        elif style == "dagger":
            # Short blade
            blade_color = (180, 180, 200, 255)
            blade_box = [cx + 12, 40, cx + 14, 55]
            draw_sprite.rectangle(blade_box, fill=blade_color)
            draw_mask.rectangle(blade_box, fill=255)

            # Handle
            handle_color = (80, 60, 40, 255)
            handle_box = [cx + 11, 52, cx + 15, 58]
            draw_sprite.rectangle(handle_box, fill=handle_color)
            draw_mask.rectangle(handle_box, fill=255)

        else:  # Default: sword
            blade_box = [cx + 12, 30, cx + 15, 55]
            draw_sprite.rectangle(blade_box, fill=(180, 180, 200, 255))
            draw_mask.rectangle(blade_box, fill=255)

        return sprite, mask

    def create_face(self, style: str = "human") -> Tuple[Image.Image, Image.Image]:
        """
        Create face sprite and mask.

        Args:
            style: Face style (human, elf, orc, demon, cat)

        Returns:
            (sprite, mask) tuple
        """
        sprite = Image.new("RGBA", self.size, (0, 0, 0, 0))
        mask = Image.new("L", self.size, 0)

        draw_sprite = ImageDraw.Draw(sprite)

        cx = self.size[0] // 2
        head_y = 12

        # Eyes
        eye_color = (50, 50, 50, 255)
        left_eye = [cx - 5, head_y + 7, cx - 3, head_y + 9]
        right_eye = [cx + 3, head_y + 7, cx + 5, head_y + 9]
        draw_sprite.ellipse(left_eye, fill=eye_color)
        draw_sprite.ellipse(right_eye, fill=eye_color)

        # Mouth
        mouth_y = head_y + 13
        draw_sprite.arc([cx - 4, mouth_y - 2, cx + 4, mouth_y + 2], 0, 180, fill=eye_color, width=1)

        if style == "elf":
            # Pointed ears
            ear_color = (200, 180, 160, 255)
            # Left ear
            draw_sprite.polygon(
                [(cx - 9, head_y + 8), (cx - 12, head_y + 4), (cx - 9, head_y + 10)], fill=ear_color
            )
            # Right ear
            draw_sprite.polygon(
                [(cx + 9, head_y + 8), (cx + 12, head_y + 4), (cx + 9, head_y + 10)], fill=ear_color
            )

        elif style == "orc":
            # Tusks
            tusk_color = (220, 220, 200, 255)
            # Left tusk
            draw_sprite.rectangle([cx - 6, mouth_y, cx - 4, mouth_y + 4], fill=tusk_color)
            # Right tusk
            draw_sprite.rectangle([cx + 4, mouth_y, cx + 6, mouth_y + 4], fill=tusk_color)

        return sprite, mask


def generate_character_assets(output_dir: str | Path):
    """
    Generate complete set of character generator assets.

    Args:
        output_dir: Base output directory (assets/character_generator/)
    """
    output_dir = Path(output_dir)
    generator = ProceduralSpriteGenerator()

    print("Generating character generator assets...\n")

    # Bodies
    print("Generating bodies...")
    bodies_dir = output_dir / "bodies"
    bodies_mask_dir = output_dir / "masks" / "bodies"
    bodies_dir.mkdir(parents=True, exist_ok=True)
    bodies_mask_dir.mkdir(parents=True, exist_ok=True)

    for style in ["male", "female"]:
        sprite, mask = generator.create_base_body(style)
        sprite.save(bodies_dir / f"base_body_{style}.png")
        mask.save(bodies_mask_dir / f"base_body_{style}_mask.png")

    # Hair
    print("Generating hair...")
    hair_dir = output_dir / "hair"
    hair_mask_dir = output_dir / "masks" / "hair"
    hair_dir.mkdir(parents=True, exist_ok=True)
    hair_mask_dir.mkdir(parents=True, exist_ok=True)

    for style in ["short", "long", "mohawk", "bun"]:
        sprite, mask = generator.create_hair(style)
        sprite.save(hair_dir / f"hair_{style}.png")
        mask.save(hair_mask_dir / f"hair_{style}_mask.png")

    # Clothing
    print("Generating clothing...")
    clothing_dir = output_dir / "clothing"
    clothing_mask_dir = output_dir / "masks" / "clothing"
    clothing_dir.mkdir(parents=True, exist_ok=True)
    clothing_mask_dir.mkdir(parents=True, exist_ok=True)

    for style in ["tunic", "robe", "armor"]:
        sprite, mask = generator.create_clothing(style)
        sprite.save(clothing_dir / f"clothing_{style}.png")
        mask.save(clothing_mask_dir / f"clothing_{style}_mask.png")

    # Weapons
    print("Generating weapons...")
    weapons_dir = output_dir / "weapons"
    weapons_mask_dir = output_dir / "masks" / "weapons"
    weapons_dir.mkdir(parents=True, exist_ok=True)
    weapons_mask_dir.mkdir(parents=True, exist_ok=True)

    for style in ["sword", "staff", "bow", "dagger"]:
        sprite, mask = generator.create_weapon(style)
        sprite.save(weapons_dir / f"weapon_{style}.png")
        mask.save(weapons_mask_dir / f"weapon_{style}_mask.png")

    # Faces
    print("Generating faces...")
    faces_dir = output_dir / "faces"
    faces_dir.mkdir(parents=True, exist_ok=True)

    for style in ["human", "elf", "orc"]:
        sprite, mask = generator.create_face(style)
        sprite.save(faces_dir / f"face_{style}.png")

    # Create README
    readme_path = output_dir / "README.md"
    with open(readme_path, "w") as f:
        f.write(
            """# Character Generator Assets

This directory contains procedurally generated placeholder sprites for the
character generator system.

## Directory Structure

- `bodies/` - Base character bodies (male, female)
- `hair/` - Hair styles (short, long, mohawk, bun)
- `clothing/` - Clothing items (tunic, robe, armor)
- `weapons/` - Weapons (sword, staff, bow, dagger)
- `faces/` - Facial features (human, elf, orc)
- `masks/` - Grayscale masks for color customization

## Usage

These are placeholder assets. Replace them with your own art while maintaining:
- 64x64 pixel size
- PNG format with transparency
- Matching masks in `masks/` subdirectories

## Color Customization

Masks are grayscale images where white pixels (255) are recolored and black
pixels (0) are left unchanged. This allows flexible color customization while
preserving details.

Generated by: generate_character_assets.py
"""
        )

    print(f"\nAsset generation complete!")
    print(f"Generated assets in: {output_dir}")
    print(f"- Bodies: 2 sprites")
    print(f"- Hair: 4 sprites")
    print(f"- Clothing: 3 sprites")
    print(f"- Weapons: 4 sprites")
    print(f"- Faces: 3 sprites")
    print(f"Total: 16 sprites + masks")


if __name__ == "__main__":
    # Generate assets
    output_dir = Path(__file__).parent.parent / "assets" / "character_generator"
    generate_character_assets(output_dir)

    print("\nAssets ready for use with the character generator system!")
