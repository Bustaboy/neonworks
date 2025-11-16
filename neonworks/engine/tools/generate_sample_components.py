"""
Generate Sample Component Sprites

Creates simple geometric sample sprites for testing the character generator.
These are placeholder sprites demonstrating the layer system.

Run this script to generate test assets:
    python engine/tools/generate_sample_components.py
"""

import json
from pathlib import Path

import pygame


def create_body_sprite(width: int, height: int, skin_color: tuple) -> pygame.Surface:
    """Create a simple body sprite (circle/oval)."""
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))

    # Draw oval body
    center_x = width // 2
    center_y = height // 2
    radius_x = width // 3
    radius_y = height // 2 - 2

    pygame.draw.ellipse(
        surface, skin_color, (center_x - radius_x, center_y - radius_y, radius_x * 2, radius_y * 2)
    )

    # Draw head (circle)
    head_radius = width // 4
    pygame.draw.circle(surface, skin_color, (center_x, center_y - radius_y), head_radius)

    return surface


def create_hair_sprite(width: int, height: int, hair_color: tuple, style: str) -> pygame.Surface:
    """Create a simple hair sprite."""
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))

    center_x = width // 2
    center_y = height // 2
    head_radius = width // 4

    if style == "short":
        # Short hair - small cap on top of head
        pygame.draw.circle(surface, hair_color, (center_x, center_y - height // 3), head_radius)
    elif style == "long":
        # Long hair - larger area
        pygame.draw.ellipse(
            surface,
            hair_color,
            (
                center_x - head_radius - 2,
                center_y - height // 2,
                (head_radius + 2) * 2,
                height // 2 + 5,
            ),
        )
    elif style == "ponytail":
        # Ponytail - cap + tail
        pygame.draw.circle(surface, hair_color, (center_x, center_y - height // 3), head_radius)
        pygame.draw.rect(surface, hair_color, (center_x - 2, center_y - height // 3, 4, 8))

    return surface


def create_outfit_sprite(width: int, height: int, outfit_type: str, color: tuple) -> pygame.Surface:
    """Create a simple outfit sprite."""
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))

    center_x = width // 2
    center_y = height // 2

    if outfit_type == "armor":
        # Armor - rectangle with details
        pygame.draw.rect(
            surface, color, (center_x - width // 4, center_y - 2, width // 2, height // 3)
        )
        # Add shoulder plates
        pygame.draw.rect(surface, color, (center_x - width // 3, center_y - 5, 6, 6))
        pygame.draw.rect(surface, color, (center_x + width // 4, center_y - 5, 6, 6))

    elif outfit_type == "robe":
        # Robe - triangle shape
        points = [
            (center_x, center_y - 5),
            (center_x - width // 3, center_y + height // 4),
            (center_x + width // 3, center_y + height // 4),
        ]
        pygame.draw.polygon(surface, color, points)

    elif outfit_type == "clothes":
        # Simple clothes - basic rectangle
        pygame.draw.rect(
            surface, color, (center_x - width // 5, center_y, width // 2 + 2, height // 4)
        )

    return surface


def create_weapon_sprite(width: int, height: int, weapon_type: str, color: tuple) -> pygame.Surface:
    """Create a simple weapon sprite."""
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))

    center_x = width // 2
    center_y = height // 2

    if weapon_type == "sword":
        # Sword - vertical line with cross guard
        pygame.draw.rect(surface, color, (center_x + width // 4 - 1, center_y - 8, 2, 12))
        pygame.draw.rect(surface, color, (center_x + width // 4 - 3, center_y - 8, 6, 2))

    elif weapon_type == "staff":
        # Staff - long vertical line
        pygame.draw.rect(surface, color, (center_x + width // 4, center_y - 12, 2, 16))
        # Gem on top
        pygame.draw.circle(surface, (100, 100, 255), (center_x + width // 4 + 1, center_y - 12), 2)

    elif weapon_type == "bow":
        # Bow - arc shape
        pygame.draw.arc(surface, color, (center_x + width // 5, center_y - 8, 8, 14), 0.5, 2.64, 2)

    return surface


def create_multi_frame_sprite(
    base_surface: pygame.Surface, num_frames: int, num_directions: int
) -> pygame.Surface:
    """
    Create a multi-frame sprite sheet from a base sprite.

    For animation, we'll create slight variations of the base sprite.
    """
    frame_width = base_surface.get_width()
    frame_height = base_surface.get_height()

    sheet_width = frame_width * num_frames
    sheet_height = frame_height * num_directions

    sheet = pygame.Surface((sheet_width, sheet_height), pygame.SRCALPHA)
    sheet.fill((0, 0, 0, 0))

    for direction in range(num_directions):
        for frame in range(num_frames):
            # For now, just copy the same sprite
            # In a real implementation, you'd vary the sprite per frame
            x = frame * frame_width
            y = direction * frame_height

            # Create slight variation (shift pixels slightly for animation effect)
            frame_surface = base_surface.copy()
            if frame == 1:
                # Shift up slightly
                frame_surface.scroll(0, -1)
            elif frame == 3:
                # Shift down slightly
                frame_surface.scroll(0, 1)

            sheet.blit(frame_surface, (x, y))

    return sheet


def generate_sample_components(output_dir: str = "test_outputs/character_components"):
    """
    Generate a complete set of sample component sprites.

    Creates components for:
    - Body (human_male, human_female, elf_male)
    - Hair (short_brown, long_blonde, ponytail_red)
    - Outfit (knight_armor, mage_robe, peasant_clothes)
    - Weapon (sword, staff, bow)
    """
    pygame.init()

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"Generating sample components in {output_path}...")

    # Configuration
    sprite_size = 32
    num_frames = 4
    num_directions = 4  # Down, Left, Right, Up

    components = []

    # === BODY COMPONENTS ===
    body_dir = output_path / "body"
    body_dir.mkdir(exist_ok=True)

    body_variants = [
        ("human_male", (255, 220, 180)),  # Light skin
        ("human_female", (255, 200, 170)),  # Light skin
        ("elf_male", (220, 255, 220)),  # Greenish tint
    ]

    for name, color in body_variants:
        base = create_body_sprite(sprite_size, sprite_size, color)
        sheet = create_multi_frame_sprite(base, num_frames, num_directions)

        filename = body_dir / f"{name}.png"
        pygame.image.save(sheet, str(filename))

        # Save metadata
        metadata = {
            "frames": num_frames,
            "directions": num_directions,
            "frame_width": sprite_size,
            "frame_height": sprite_size,
        }
        with open(filename.with_suffix(".json"), "w") as f:
            json.dump(metadata, f, indent=2)

        components.append(f"body/{name}")
        print(f"  Created {name}")

    # === HAIR COMPONENTS ===
    hair_dir = output_path / "hair"
    hair_dir.mkdir(exist_ok=True)

    hair_variants = [
        ("short_brown", (139, 90, 43), "short"),
        ("long_blonde", (255, 230, 150), "long"),
        ("ponytail_red", (200, 80, 60), "ponytail"),
    ]

    for name, color, style in hair_variants:
        base = create_hair_sprite(sprite_size, sprite_size, color, style)
        sheet = create_multi_frame_sprite(base, num_frames, num_directions)

        filename = hair_dir / f"{name}.png"
        pygame.image.save(sheet, str(filename))

        # Save metadata
        metadata = {
            "frames": num_frames,
            "directions": num_directions,
            "frame_width": sprite_size,
            "frame_height": sprite_size,
        }
        with open(filename.with_suffix(".json"), "w") as f:
            json.dump(metadata, f, indent=2)

        components.append(f"hair/{name}")
        print(f"  Created {name}")

    # === OUTFIT COMPONENTS ===
    outfit_dir = output_path / "outfit"
    outfit_dir.mkdir(exist_ok=True)

    outfit_variants = [
        ("knight_armor", (150, 150, 180), "armor"),
        ("mage_robe", (100, 50, 150), "robe"),
        ("peasant_clothes", (150, 120, 80), "clothes"),
    ]

    for name, color, outfit_type in outfit_variants:
        base = create_outfit_sprite(sprite_size, sprite_size, outfit_type, color)
        sheet = create_multi_frame_sprite(base, num_frames, num_directions)

        filename = outfit_dir / f"{name}.png"
        pygame.image.save(sheet, str(filename))

        # Save metadata
        metadata = {
            "frames": num_frames,
            "directions": num_directions,
            "frame_width": sprite_size,
            "frame_height": sprite_size,
        }
        with open(filename.with_suffix(".json"), "w") as f:
            json.dump(metadata, f, indent=2)

        components.append(f"outfit/{name}")
        print(f"  Created {name}")

    # === WEAPON COMPONENTS ===
    weapon_dir = output_path / "weapon"
    weapon_dir.mkdir(exist_ok=True)

    weapon_variants = [
        ("sword", (200, 200, 200), "sword"),
        ("staff", (139, 90, 43), "staff"),
        ("bow", (150, 100, 50), "bow"),
    ]

    for name, color, weapon_type in weapon_variants:
        base = create_weapon_sprite(sprite_size, sprite_size, weapon_type, color)
        sheet = create_multi_frame_sprite(base, num_frames, num_directions)

        filename = weapon_dir / f"{name}.png"
        pygame.image.save(sheet, str(filename))

        # Save metadata
        metadata = {
            "frames": num_frames,
            "directions": num_directions,
            "frame_width": sprite_size,
            "frame_height": sprite_size,
        }
        with open(filename.with_suffix(".json"), "w") as f:
            json.dump(metadata, f, indent=2)

        components.append(f"weapon/{name}")
        print(f"  Created {name}")

    # === SUMMARY ===
    print(f"\nGenerated {len(components)} component sprites:")
    for comp in components:
        print(f"  - {comp}")

    print(f"\nAll components saved to: {output_path}")
    print("\nYou can now use CharacterGenerator with this component library!")

    pygame.quit()


if __name__ == "__main__":
    generate_sample_components()
