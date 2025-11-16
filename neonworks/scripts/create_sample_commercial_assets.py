"""
Create Sample Commercial-Use Assets

Generates additional sample assets demonstrating proper tagging,
genre classification, and commercial-use licensing (CC0).

All generated assets are CC0 (Public Domain) - safe for commercial use.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pygame

# Initialize Pygame
pygame.init()


def create_fantasy_character(filename: str, color: tuple, size: int = 32):
    """Create a simple fantasy character sprite."""
    surface = pygame.Surface((size, size), pygame.SRCALPHA)

    # Body (main color)
    pygame.draw.circle(surface, color, (size // 2, size // 2), size // 3)

    # Head (lighter)
    head_color = tuple(min(c + 40, 255) for c in color)
    pygame.draw.circle(surface, head_color, (size // 2, size // 4), size // 5)

    # Eyes
    eye_color = (0, 0, 0)
    pygame.draw.circle(surface, eye_color, (size // 2 - 3, size // 4), 2)
    pygame.draw.circle(surface, eye_color, (size // 2 + 3, size // 4), 2)

    # Weapon (small line)
    weapon_color = (150, 150, 150)
    pygame.draw.line(surface, weapon_color, (size - 5, size // 2 - 5), (size - 5, size // 2 + 8), 2)

    pygame.image.save(surface, filename)
    print(f"✓ Created: {filename}")


def create_enemy_sprite(filename: str, enemy_type: str, size: int = 48):
    """Create a simple enemy sprite."""
    surface = pygame.Surface((size, size), pygame.SRCALPHA)

    if enemy_type == "goblin":
        # Green goblin
        body_color = (80, 150, 80)
        pygame.draw.ellipse(surface, body_color, (10, 15, size - 20, size - 20))
        # Eyes (red)
        pygame.draw.circle(surface, (200, 50, 50), (size // 2 - 5, size // 2 - 5), 3)
        pygame.draw.circle(surface, (200, 50, 50), (size // 2 + 5, size // 2 - 5), 3)

    elif enemy_type == "skeleton":
        # White skeleton
        bone_color = (230, 230, 230)
        # Skull
        pygame.draw.circle(surface, bone_color, (size // 2, size // 3), 10)
        # Eye sockets (black)
        pygame.draw.circle(surface, (0, 0, 0), (size // 2 - 4, size // 3), 2)
        pygame.draw.circle(surface, (0, 0, 0), (size // 2 + 4, size // 3), 2)
        # Ribcage
        for i in range(3):
            y = size // 2 + i * 4
            pygame.draw.line(surface, bone_color, (size // 2 - 8, y), (size // 2 + 8, y), 2)

    elif enemy_type == "dragon":
        # Red dragon (larger)
        dragon_color = (180, 50, 50)
        # Body
        pygame.draw.ellipse(surface, dragon_color, (5, 10, size - 10, size - 15))
        # Wings
        wing_color = (150, 40, 40)
        pygame.draw.polygon(
            surface, wing_color, [(5, size // 2), (0, size // 3), (10, size // 2 - 5)]
        )
        pygame.draw.polygon(
            surface,
            wing_color,
            [(size - 5, size // 2), (size, size // 3), (size - 10, size // 2 - 5)],
        )
        # Eye
        pygame.draw.circle(surface, (255, 200, 0), (size // 2, size // 3), 4)

    pygame.image.save(surface, filename)
    print(f"✓ Created: {filename}")


def create_tileset_sample(filename: str, theme: str, tile_size: int = 32):
    """Create a simple tileset sample."""
    # 4x4 tileset = 128x128
    cols, rows = 4, 4
    surface = pygame.Surface((tile_size * cols, tile_size * rows), pygame.SRCALPHA)

    if theme == "dungeon":
        colors = [
            (60, 60, 70),  # Dark stone floor
            (50, 50, 60),  # Darker stone
            (70, 60, 50),  # Brown stone
            (80, 70, 60),  # Lighter stone
        ]
    elif theme == "grass":
        colors = [
            (80, 150, 80),  # Grass 1
            (70, 140, 70),  # Grass 2
            (90, 160, 90),  # Grass 3
            (100, 170, 100),  # Grass 4
        ]
    elif theme == "cave":
        colors = [
            (40, 40, 50),  # Dark rock
            (35, 35, 45),  # Darker rock
            (45, 45, 55),  # Medium rock
            (50, 50, 60),  # Lighter rock
        ]
    else:
        colors = [(100, 100, 100)] * 4

    # Fill tiles with colors
    tile_idx = 0
    for row in range(rows):
        for col in range(cols):
            x = col * tile_size
            y = row * tile_size
            color = colors[tile_idx % len(colors)]

            # Fill tile
            pygame.draw.rect(surface, color, (x, y, tile_size, tile_size))

            # Add border for visibility
            border_color = tuple(max(c - 20, 0) for c in color)
            pygame.draw.rect(surface, border_color, (x, y, tile_size, tile_size), 1)

            # Add texture (dots)
            for _ in range(3):
                dot_x = x + (tile_size // 4) + (_ * 8)
                dot_y = y + (tile_size // 2)
                dot_color = tuple(min(c + 10, 255) for c in color)
                pygame.draw.circle(surface, dot_color, (dot_x, dot_y), 1)

            tile_idx += 1

    pygame.image.save(surface, filename)
    print(f"✓ Created: {filename}")


def create_icon(filename: str, icon_type: str, size: int = 32):
    """Create a simple icon."""
    surface = pygame.Surface((size, size), pygame.SRCALPHA)

    if icon_type == "shield":
        # Blue shield
        shield_color = (80, 120, 200)
        points = [
            (size // 2, size - 4),  # Bottom point
            (4, size // 3),  # Left side
            (4, size // 5),  # Top left
            (size // 2, 4),  # Top center
            (size - 4, size // 5),  # Top right
            (size - 4, size // 3),  # Right side
        ]
        pygame.draw.polygon(surface, shield_color, points)
        # Highlight
        pygame.draw.circle(surface, (150, 180, 230), (size // 2, size // 3), 4)

    elif icon_type == "magic_book":
        # Purple book
        book_color = (150, 80, 200)
        pygame.draw.rect(surface, book_color, (8, 6, size - 16, size - 12))
        # Pages (white)
        pygame.draw.rect(surface, (230, 230, 230), (10, 8, size - 20, size - 16))
        # Magic symbol (star)
        star_color = (255, 200, 50)
        pygame.draw.circle(surface, star_color, (size // 2, size // 2), 5)

    elif icon_type == "bow":
        # Brown bow
        bow_color = (150, 100, 60)
        # Bow curve
        pygame.draw.arc(surface, bow_color, (8, 4, size - 16, size - 8), 0, 3.14, 3)
        # String
        pygame.draw.line(surface, (200, 200, 200), (12, 8), (12, size - 8), 1)

    pygame.image.save(surface, filename)
    print(f"✓ Created: {filename}")


def create_ui_element(filename: str, ui_type: str, width: int = 96, height: int = 32):
    """Create a simple UI element."""
    surface = pygame.Surface((width, height), pygame.SRCALPHA)

    if ui_type == "panel":
        # Semi-transparent dark panel
        panel_color = (40, 40, 50, 200)
        pygame.draw.rect(surface, panel_color, (0, 0, width, height))
        # Border
        border_color = (100, 100, 120, 255)
        pygame.draw.rect(surface, border_color, (0, 0, width, height), 2)

    elif ui_type == "button_green":
        # Green button
        button_color = (80, 180, 80)
        pygame.draw.rect(surface, button_color, (0, 0, width, height), border_radius=4)
        # Highlight
        highlight_color = (120, 220, 120)
        pygame.draw.rect(surface, highlight_color, (4, 4, width - 8, height // 2), border_radius=2)
        # Border
        pygame.draw.rect(surface, (60, 140, 60), (0, 0, width, height), 2, border_radius=4)

    pygame.image.save(surface, filename)
    print(f"✓ Created: {filename}")


def create_background(filename: str, bg_type: str, width: int = 320, height: int = 240):
    """Create a simple background."""
    surface = pygame.Surface((width, height))

    if bg_type == "forest":
        # Green forest gradient
        for y in range(height):
            green = 100 + int((y / height) * 80)
            color = (40, green, 40)
            pygame.draw.line(surface, color, (0, y), (width, y))
        # Tree silhouettes
        for x in range(0, width, 60):
            tree_color = (30, 60, 30)
            pygame.draw.circle(surface, tree_color, (x + 30, height - 40), 25)

    elif bg_type == "cave":
        # Dark cave gradient
        for y in range(height):
            darkness = 30 + int((y / height) * 40)
            color = (darkness, darkness, darkness + 10)
            pygame.draw.line(surface, color, (0, y), (width, y))

    elif bg_type == "sky":
        # Blue sky gradient
        for y in range(height):
            blue = 180 - int((y / height) * 80)
            color = (100, 150, blue)
            pygame.draw.line(surface, color, (0, y), (width, y))

    pygame.image.save(surface, filename)
    print(f"✓ Created: {filename}")


def main():
    """Generate all sample assets."""
    print("Creating sample commercial-use assets...")
    print("All assets are CC0 (Public Domain) - safe for commercial use\n")

    # Get project root
    project_root = Path(__file__).parent.parent
    assets_dir = project_root / "assets"

    # Create additional characters (fantasy party members)
    chars_dir = assets_dir / "characters"
    chars_dir.mkdir(parents=True, exist_ok=True)

    print("Creating characters...")
    create_fantasy_character(str(chars_dir / "hero_warrior.png"), (180, 80, 80), 32)  # Red warrior
    create_fantasy_character(str(chars_dir / "hero_mage.png"), (80, 80, 180), 32)  # Blue mage
    create_fantasy_character(str(chars_dir / "hero_rogue.png"), (80, 180, 80), 32)  # Green rogue
    create_fantasy_character(
        str(chars_dir / "hero_cleric.png"), (220, 220, 120), 32
    )  # Yellow cleric

    # Create enemies
    enemies_dir = assets_dir / "enemies"
    enemies_dir.mkdir(parents=True, exist_ok=True)

    print("\nCreating enemies...")
    create_enemy_sprite(str(enemies_dir / "enemy_goblin.png"), "goblin", 48)
    create_enemy_sprite(str(enemies_dir / "enemy_skeleton.png"), "skeleton", 48)
    create_enemy_sprite(str(enemies_dir / "boss_dragon.png"), "dragon", 64)

    # Create tilesets
    tilesets_dir = assets_dir / "tilesets"
    tilesets_dir.mkdir(parents=True, exist_ok=True)

    print("\nCreating tilesets...")
    create_tileset_sample(str(tilesets_dir / "tileset_dungeon.png"), "dungeon", 32)
    create_tileset_sample(str(tilesets_dir / "tileset_grass.png"), "grass", 32)
    create_tileset_sample(str(tilesets_dir / "tileset_cave.png"), "cave", 32)

    # Create icons
    icons_dir = assets_dir / "icons"
    icons_dir.mkdir(parents=True, exist_ok=True)

    print("\nCreating icons...")
    create_icon(str(icons_dir / "icon_shield.png"), "shield", 32)
    create_icon(str(icons_dir / "icon_magic_book.png"), "magic_book", 32)
    create_icon(str(icons_dir / "icon_bow.png"), "bow", 32)

    # Create UI elements
    ui_dir = assets_dir / "ui"
    ui_dir.mkdir(parents=True, exist_ok=True)

    print("\nCreating UI elements...")
    create_ui_element(str(ui_dir / "ui_panel.png"), "panel", 200, 150)
    create_ui_element(str(ui_dir / "ui_button_green.png"), "button_green", 96, 32)

    # Create backgrounds
    backgrounds_dir = assets_dir / "backgrounds"
    backgrounds_dir.mkdir(parents=True, exist_ok=True)

    print("\nCreating backgrounds...")
    create_background(str(backgrounds_dir / "bg_forest.png"), "forest", 320, 240)
    create_background(str(backgrounds_dir / "bg_cave.png"), "cave", 320, 240)
    create_background(str(backgrounds_dir / "bg_sky.png"), "sky", 320, 240)

    print("\n" + "=" * 50)
    print("✓ All sample assets created successfully!")
    print("=" * 50)
    print("\nAssets created:")
    print("  - 4 character sprites (warrior, mage, rogue, cleric)")
    print("  - 3 enemy sprites (goblin, skeleton, dragon boss)")
    print("  - 3 tilesets (dungeon, grass, cave)")
    print("  - 3 icons (shield, magic book, bow)")
    print("  - 2 UI elements (panel, button)")
    print("  - 3 backgrounds (forest, cave, sky)")
    print("\nAll assets are CC0 (Public Domain)")
    print("Next step: Update asset_manifest.json with these entries")


if __name__ == "__main__":
    main()
