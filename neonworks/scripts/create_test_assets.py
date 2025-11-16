#!/usr/bin/env python3
"""
Create sample test assets for the asset library.

This script generates simple placeholder graphics for testing
the asset management system.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import pygame
sys.path.insert(0, str(Path(__file__).parent.parent))

import pygame

# Initialize pygame
pygame.init()


def create_character_sprite(output_path: Path):
    """Create a simple character sprite."""
    # Create a 32x32 sprite with a simple character design
    surface = pygame.Surface((32, 32), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))

    # Head
    pygame.draw.circle(surface, (255, 200, 150), (16, 10), 6)

    # Body
    pygame.draw.rect(surface, (100, 150, 255), (12, 16, 8, 10))

    # Legs
    pygame.draw.rect(surface, (50, 50, 100), (12, 26, 3, 6))
    pygame.draw.rect(surface, (50, 50, 100), (17, 26, 3, 6))

    pygame.image.save(surface, str(output_path))
    print(f"✓ Created: {output_path}")


def create_enemy_sprite(output_path: Path):
    """Create a simple enemy sprite."""
    # Create a 48x48 enemy sprite
    surface = pygame.Surface((48, 48), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))

    # Monster body (blob shape)
    pygame.draw.circle(surface, (150, 50, 150), (24, 28), 16)
    pygame.draw.circle(surface, (100, 30, 100), (24, 28), 12)

    # Eyes
    pygame.draw.circle(surface, (255, 0, 0), (18, 22), 4)
    pygame.draw.circle(surface, (255, 0, 0), (30, 22), 4)
    pygame.draw.circle(surface, (0, 0, 0), (18, 22), 2)
    pygame.draw.circle(surface, (0, 0, 0), (30, 22), 2)

    pygame.image.save(surface, str(output_path))
    print(f"✓ Created: {output_path}")


def create_tileset(output_path: Path):
    """Create a simple tileset."""
    # Create a 128x64 tileset with 4x2 tiles (32x32 each)
    surface = pygame.Surface((128, 64), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))

    tiles = [
        (100, 200, 100),  # Grass
        (150, 100, 50),  # Dirt
        (100, 100, 100),  # Stone
        (50, 50, 200),  # Water
        (200, 200, 100),  # Sand
        (150, 150, 150),  # Wall
        (100, 50, 50),  # Wood
        (200, 100, 50),  # Lava
    ]

    for i, color in enumerate(tiles):
        x = (i % 4) * 32
        y = (i // 4) * 32
        pygame.draw.rect(surface, color, (x, y, 32, 32))
        pygame.draw.rect(surface, (0, 0, 0), (x, y, 32, 32), 1)

    pygame.image.save(surface, str(output_path))
    print(f"✓ Created: {output_path}")


def create_icon(output_path: Path, icon_type: str):
    """Create a simple icon."""
    surface = pygame.Surface((32, 32), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))

    if icon_type == "sword":
        # Sword icon
        pygame.draw.rect(surface, (150, 150, 150), (14, 8, 4, 16))
        pygame.draw.rect(surface, (200, 180, 100), (12, 24, 8, 4))
        pygame.draw.polygon(surface, (150, 150, 150), [(12, 8), (20, 8), (16, 4)])
    elif icon_type == "potion":
        # Potion icon
        pygame.draw.rect(surface, (100, 200, 255), (12, 16, 8, 12))
        pygame.draw.rect(surface, (150, 100, 50), (14, 12, 4, 4))
        pygame.draw.circle(surface, (150, 230, 255), (16, 20), 2)

    pygame.image.save(surface, str(output_path))
    print(f"✓ Created: {output_path}")


def create_background(output_path: Path):
    """Create a simple background."""
    # Create a 320x240 background
    surface = pygame.Surface((320, 240))

    # Gradient sky
    for y in range(240):
        color_intensity = int(100 + (y / 240) * 100)
        pygame.draw.line(
            surface,
            (50, 50, color_intensity),
            (0, y),
            (320, y),
        )

    # Ground
    pygame.draw.rect(surface, (100, 150, 50), (0, 160, 320, 80))

    # Simple clouds
    pygame.draw.circle(surface, (255, 255, 255, 128), (60, 50), 20)
    pygame.draw.circle(surface, (255, 255, 255, 128), (80, 50), 25)
    pygame.draw.circle(surface, (255, 255, 255, 128), (100, 50), 20)

    pygame.image.save(surface, str(output_path))
    print(f"✓ Created: {output_path}")


def create_ui_element(output_path: Path):
    """Create a simple UI element (button)."""
    surface = pygame.Surface((96, 32), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))

    # Button background
    pygame.draw.rect(surface, (80, 80, 120), (0, 0, 96, 32), border_radius=4)
    pygame.draw.rect(surface, (120, 120, 160), (2, 2, 92, 28), border_radius=4)
    pygame.draw.rect(surface, (100, 100, 140), (0, 0, 96, 32), 2, border_radius=4)

    pygame.image.save(surface, str(output_path))
    print(f"✓ Created: {output_path}")


def create_face_portrait(output_path: Path):
    """Create a simple character face portrait."""
    surface = pygame.Surface((64, 64), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))

    # Face
    pygame.draw.circle(surface, (255, 200, 150), (32, 32), 24)

    # Eyes
    pygame.draw.circle(surface, (50, 50, 100), (24, 28), 4)
    pygame.draw.circle(surface, (50, 50, 100), (40, 28), 4)

    # Smile
    pygame.draw.arc(surface, (100, 50, 50), (20, 28, 24, 16), 3.14, 2 * 3.14, 2)

    pygame.image.save(surface, str(output_path))
    print(f"✓ Created: {output_path}")


def create_animation_sprite(output_path: Path):
    """Create a simple animation sprite sheet."""
    # 4 frames of a spinning effect
    surface = pygame.Surface((128, 32), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))

    colors = [
        (255, 100, 100),
        (255, 200, 100),
        (100, 255, 100),
        (100, 100, 255),
    ]

    for i in range(4):
        x = i * 32
        # Draw rotating effect
        for j in range(8):
            angle = (j / 8) * 2 * 3.14159 + (i / 4) * 3.14159
            import math

            px = int(16 + x + 10 * math.cos(angle))
            py = int(16 + 10 * math.sin(angle))
            pygame.draw.circle(surface, colors[i], (px, py), 3)

    pygame.image.save(surface, str(output_path))
    print(f"✓ Created: {output_path}")


def main():
    """Create all test assets."""
    # Get assets directory
    assets_dir = Path(__file__).parent.parent / "assets"

    print("Creating test assets...")
    print(f"Assets directory: {assets_dir}")

    # Create sample assets
    create_character_sprite(assets_dir / "characters" / "test_hero.png")
    create_enemy_sprite(assets_dir / "enemies" / "test_slime.png")
    create_tileset(assets_dir / "tilesets" / "test_basic_tiles.png")
    create_icon(assets_dir / "icons" / "test_sword_icon.png", "sword")
    create_icon(assets_dir / "icons" / "test_potion_icon.png", "potion")
    create_background(assets_dir / "backgrounds" / "test_battle_bg.png")
    create_ui_element(assets_dir / "ui" / "test_button.png")
    create_face_portrait(assets_dir / "faces" / "test_hero_face.png")
    create_animation_sprite(assets_dir / "animations" / "test_sparkle.png")

    print("\n✓ All test assets created successfully!")
    print("\nNext: Update assets/asset_manifest.json to register these assets.")


if __name__ == "__main__":
    main()
