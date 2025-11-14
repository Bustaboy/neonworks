"""
AI-powered tileset generator and manager for NeonWorks engine.

Provides AI capabilities for:
- Procedural tileset generation
- Automatic metadata tagging (passability, terrain types)
- Tile variation generation
- Autotiling rules creation
- Tileset organization and categorization

Author: NeonWorks Team
Version: 0.1.0
"""

from __future__ import annotations

import random
from typing import Dict, List, Optional, Tuple

import pygame

from neonworks.data.tileset_manager import TilesetManager, TileMetadata


class AITilesetGenerator:
    """
    AI-powered tileset generator and analyzer.

    Generates tilesets procedurally and provides intelligent
    tile analysis and categorization.
    """

    # Terrain type definitions with visual characteristics
    TERRAIN_TYPES = {
        "grass": {
            "base_colors": [(100, 200, 50), (80, 180, 40), (120, 220, 60)],
            "passable": True,
            "variants": ["plain", "flowers", "tall"],
            "tags": ["grass", "ground", "natural"],
        },
        "dirt": {
            "base_colors": [(139, 90, 43), (120, 75, 35), (155, 100, 50)],
            "passable": True,
            "variants": ["plain", "rocky", "cracked"],
            "tags": ["dirt", "ground", "natural"],
        },
        "stone": {
            "base_colors": [(128, 128, 128), (110, 110, 110), (145, 145, 145)],
            "passable": True,
            "variants": ["smooth", "rough", "cobblestone"],
            "tags": ["stone", "ground", "hard"],
        },
        "water": {
            "base_colors": [(100, 150, 255), (80, 130, 235), (120, 170, 255)],
            "passable": False,
            "variants": ["calm", "wavy", "deep"],
            "tags": ["water", "liquid", "hazard"],
        },
        "sand": {
            "base_colors": [(255, 220, 150), (240, 210, 140), (255, 230, 160)],
            "passable": True,
            "variants": ["fine", "coarse", "dune"],
            "tags": ["sand", "ground", "natural"],
        },
        "lava": {
            "base_colors": [(255, 100, 0), (255, 80, 0), (255, 120, 20)],
            "passable": False,
            "variants": ["flowing", "bubbling", "solidified"],
            "tags": ["lava", "liquid", "hazard", "damage"],
        },
        "ice": {
            "base_colors": [(200, 230, 255), (180, 220, 250), (220, 240, 255)],
            "passable": True,
            "variants": ["smooth", "cracked", "snow"],
            "tags": ["ice", "ground", "slippery"],
        },
        "wall": {
            "base_colors": [(80, 80, 80), (60, 60, 60), (100, 100, 100)],
            "passable": False,
            "variants": ["brick", "stone", "metal"],
            "tags": ["wall", "obstacle", "solid"],
        },
        "floor": {
            "base_colors": [(200, 200, 200), (190, 190, 190), (210, 210, 210)],
            "passable": True,
            "variants": ["tile", "wood", "marble"],
            "tags": ["floor", "ground", "indoor"],
        },
        "wood": {
            "base_colors": [(139, 90, 43), (120, 75, 35), (155, 100, 50)],
            "passable": False,
            "variants": ["planks", "logs", "bark"],
            "tags": ["wood", "natural", "obstacle"],
        },
    }

    def __init__(self, tileset_manager: Optional[TilesetManager] = None):
        """
        Initialize AI tileset generator.

        Args:
            tileset_manager: TilesetManager instance to work with
        """
        self.tileset_manager = tileset_manager
        self.tile_size = 32

    def generate_procedural_tileset(
        self,
        terrain_types: List[str],
        tiles_per_type: int = 4,
        tile_size: int = 32,
        include_variations: bool = True,
    ) -> Tuple[pygame.Surface, Dict[int, TileMetadata]]:
        """
        Generate a procedural tileset with specified terrain types.

        Args:
            terrain_types: List of terrain type names to generate
            tiles_per_type: Number of tile variations per terrain type
            tile_size: Size of each tile in pixels
            include_variations: Whether to generate visual variations

        Returns:
            Tuple of (tileset_surface, metadata_dict)
        """
        self.tile_size = tile_size

        # Calculate tileset dimensions
        total_tiles = len(terrain_types) * tiles_per_type
        columns = 8  # 8 tiles per row
        rows = (total_tiles + columns - 1) // columns

        # Create tileset surface
        tileset_width = columns * tile_size
        tileset_height = rows * tile_size
        tileset_surface = pygame.Surface((tileset_width, tileset_height))
        tileset_surface.fill((0, 0, 0, 0))  # Transparent background

        metadata = {}
        tile_id = 0

        for terrain_type in terrain_types:
            if terrain_type not in self.TERRAIN_TYPES:
                print(f"Warning: Unknown terrain type '{terrain_type}', skipping")
                continue

            terrain_def = self.TERRAIN_TYPES[terrain_type]

            for i in range(tiles_per_type):
                # Calculate tile position
                col = tile_id % columns
                row = tile_id // columns
                x = col * tile_size
                y = row * tile_size

                # Generate tile
                tile_surface = self._generate_tile(
                    terrain_type, terrain_def, i, tile_size, include_variations
                )

                # Blit to tileset
                tileset_surface.blit(tile_surface, (x, y))

                # Create metadata
                variant_name = (
                    terrain_def["variants"][i % len(terrain_def["variants"])]
                    if include_variations
                    else "plain"
                )

                metadata[tile_id] = TileMetadata(
                    tile_id=tile_id,
                    passable=terrain_def["passable"],
                    terrain_tags=terrain_def["tags"] + [variant_name],
                    name=f"{terrain_type.capitalize()} ({variant_name})",
                )

                tile_id += 1

        return tileset_surface, metadata

    def _generate_tile(
        self,
        terrain_type: str,
        terrain_def: Dict,
        variation_index: int,
        tile_size: int,
        include_variations: bool,
    ) -> pygame.Surface:
        """
        Generate a single tile with procedural patterns.

        Args:
            terrain_type: Type of terrain
            terrain_def: Terrain definition dict
            variation_index: Which variation to generate
            tile_size: Size in pixels
            include_variations: Whether to add visual variations

        Returns:
            Generated tile surface
        """
        tile = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)

        # Get base color (cycle through color variations)
        base_color = terrain_def["base_colors"][
            variation_index % len(terrain_def["base_colors"])
        ]

        # Fill with base color
        tile.fill(base_color)

        if include_variations:
            # Add procedural details based on terrain type
            if terrain_type == "grass":
                self._add_grass_details(tile, base_color, tile_size)
            elif terrain_type == "water":
                self._add_water_details(tile, base_color, tile_size)
            elif terrain_type == "stone":
                self._add_stone_details(tile, base_color, tile_size)
            elif terrain_type == "dirt":
                self._add_dirt_details(tile, base_color, tile_size)
            elif terrain_type == "sand":
                self._add_sand_details(tile, base_color, tile_size)
            elif terrain_type == "lava":
                self._add_lava_details(tile, base_color, tile_size)
            elif terrain_type == "wall":
                self._add_wall_details(tile, base_color, tile_size)
            elif terrain_type == "floor":
                self._add_floor_details(tile, base_color, tile_size)

            # Add random noise for texture
            self._add_noise(tile, base_color, tile_size, intensity=0.1)

        return tile

    def _add_grass_details(
        self, surface: pygame.Surface, base_color: Tuple[int, int, int], size: int
    ):
        """Add grass-specific details (blades, flowers)."""
        # Add darker grass blades
        blade_color = (
            max(0, base_color[0] - 30),
            max(0, base_color[1] - 20),
            max(0, base_color[2] - 10),
        )

        for _ in range(random.randint(3, 6)):
            x = random.randint(0, size - 2)
            y = random.randint(0, size - 4)
            pygame.draw.line(surface, blade_color, (x, y + 3), (x, y), 1)

    def _add_water_details(
        self, surface: pygame.Surface, base_color: Tuple[int, int, int], size: int
    ):
        """Add water-specific details (waves, reflections)."""
        # Add lighter wave highlights
        wave_color = (
            min(255, base_color[0] + 40),
            min(255, base_color[1] + 40),
            min(255, base_color[2] + 40),
        )

        for i in range(2):
            y = size // 3 * (i + 1)
            pygame.draw.line(
                surface, wave_color, (0, y), (size, y + random.randint(-2, 2)), 1
            )

    def _add_stone_details(
        self, surface: pygame.Surface, base_color: Tuple[int, int, int], size: int
    ):
        """Add stone-specific details (cracks, edges)."""
        # Add darker cracks
        crack_color = (
            max(0, base_color[0] - 40),
            max(0, base_color[1] - 40),
            max(0, base_color[2] - 40),
        )

        # Random cracks
        for _ in range(random.randint(1, 3)):
            x1 = random.randint(0, size)
            y1 = random.randint(0, size)
            x2 = x1 + random.randint(-size // 4, size // 4)
            y2 = y1 + random.randint(-size // 4, size // 4)
            pygame.draw.line(surface, crack_color, (x1, y1), (x2, y2), 1)

    def _add_dirt_details(
        self, surface: pygame.Surface, base_color: Tuple[int, int, int], size: int
    ):
        """Add dirt-specific details (pebbles, variation)."""
        # Add small pebbles
        pebble_color = (
            min(255, base_color[0] + 20),
            min(255, base_color[1] + 20),
            min(255, base_color[2] + 20),
        )

        for _ in range(random.randint(2, 5)):
            x = random.randint(2, size - 2)
            y = random.randint(2, size - 2)
            pygame.draw.circle(surface, pebble_color, (x, y), 1)

    def _add_sand_details(
        self, surface: pygame.Surface, base_color: Tuple[int, int, int], size: int
    ):
        """Add sand-specific details (ripples, grains)."""
        # Add subtle ripples
        ripple_color = (
            max(0, base_color[0] - 15),
            max(0, base_color[1] - 15),
            max(0, base_color[2] - 15),
        )

        for i in range(3):
            y = size // 4 * (i + 1)
            pygame.draw.line(surface, ripple_color, (0, y), (size, y), 1)

    def _add_lava_details(
        self, surface: pygame.Surface, base_color: Tuple[int, int, int], size: int
    ):
        """Add lava-specific details (bubbles, glow)."""
        # Add bright spots (bubbles)
        bright_color = (255, min(255, base_color[1] + 80), min(255, base_color[2] + 40))

        for _ in range(random.randint(1, 3)):
            x = random.randint(2, size - 2)
            y = random.randint(2, size - 2)
            pygame.draw.circle(surface, bright_color, (x, y), 2)

    def _add_wall_details(
        self, surface: pygame.Surface, base_color: Tuple[int, int, int], size: int
    ):
        """Add wall-specific details (bricks, mortar)."""
        # Draw brick pattern
        mortar_color = (
            max(0, base_color[0] - 30),
            max(0, base_color[1] - 30),
            max(0, base_color[2] - 30),
        )

        # Horizontal lines
        for y in [size // 3, 2 * size // 3]:
            pygame.draw.line(surface, mortar_color, (0, y), (size, y), 2)

        # Vertical lines (staggered)
        for i, y_range in enumerate([(0, size // 3), (size // 3, 2 * size // 3)]):
            offset = (size // 2) if i % 2 else 0
            pygame.draw.line(surface, mortar_color, (offset, y_range[0]), (offset, y_range[1]), 2)

    def _add_floor_details(
        self, surface: pygame.Surface, base_color: Tuple[int, int, int], size: int
    ):
        """Add floor-specific details (tiles, planks)."""
        # Draw tile borders
        border_color = (
            max(0, base_color[0] - 20),
            max(0, base_color[1] - 20),
            max(0, base_color[2] - 20),
        )

        pygame.draw.rect(surface, border_color, (0, 0, size, size), 1)

    def _add_noise(
        self,
        surface: pygame.Surface,
        base_color: Tuple[int, int, int],
        size: int,
        intensity: float = 0.1,
    ):
        """Add random noise for texture."""
        for _ in range(int(size * size * intensity)):
            x = random.randint(0, size - 1)
            y = random.randint(0, size - 1)
            variation = random.randint(-10, 10)
            noise_color = (
                max(0, min(255, base_color[0] + variation)),
                max(0, min(255, base_color[1] + variation)),
                max(0, min(255, base_color[2] + variation)),
            )
            surface.set_at((x, y), noise_color)

    def auto_tag_tileset(
        self, tileset_id: str, analyze_colors: bool = True, analyze_patterns: bool = True
    ) -> Dict[int, TileMetadata]:
        """
        Automatically analyze and tag tiles in a tileset.

        Uses AI pattern recognition to determine:
        - Passability (based on color brightness and patterns)
        - Terrain types (based on color analysis)
        - Suitable tags

        Args:
            tileset_id: ID of tileset to analyze
            analyze_colors: Whether to analyze color composition
            analyze_patterns: Whether to analyze visual patterns

        Returns:
            Dictionary of tile_id -> TileMetadata with AI-generated tags
        """
        if not self.tileset_manager:
            raise ValueError("TilesetManager not set")

        tileset = self.tileset_manager.get_tileset(tileset_id)
        if not tileset:
            raise ValueError(f"Tileset '{tileset_id}' not found")

        # Ensure tileset is loaded
        if not tileset.tiles:
            self.tileset_manager.load_tileset(tileset_id)

        metadata = {}

        for tile_id, tile_surface in tileset.tiles.items():
            # Analyze tile
            tags = []
            passable = True
            terrain_type = "unknown"

            if analyze_colors:
                avg_color = self._get_average_color(tile_surface)
                brightness = self._get_brightness(avg_color)
                dominant_channel = self._get_dominant_color_channel(avg_color)

                # Determine terrain type and passability based on color
                terrain_type, passable = self._classify_terrain_by_color(
                    avg_color, brightness, dominant_channel
                )
                tags.append(terrain_type)

                # Add brightness-based tags
                if brightness < 100:
                    tags.append("dark")
                elif brightness > 200:
                    tags.append("bright")

            if analyze_patterns:
                # Analyze visual patterns
                has_variation = self._has_color_variation(tile_surface)
                if has_variation:
                    tags.append("textured")
                else:
                    tags.append("solid")

            # Create metadata
            metadata[tile_id] = TileMetadata(
                tile_id=tile_id,
                passable=passable,
                terrain_tags=tags,
                name=f"{terrain_type.capitalize()} Tile {tile_id}",
            )

        return metadata

    def _get_average_color(self, surface: pygame.Surface) -> Tuple[int, int, int]:
        """Calculate average color of a surface."""
        width, height = surface.get_size()
        total_r, total_g, total_b = 0, 0, 0
        pixel_count = 0

        for x in range(width):
            for y in range(height):
                color = surface.get_at((x, y))
                if color[3] > 0:  # Skip transparent pixels
                    total_r += color[0]
                    total_g += color[1]
                    total_b += color[2]
                    pixel_count += 1

        if pixel_count == 0:
            return (0, 0, 0)

        return (
            total_r // pixel_count,
            total_g // pixel_count,
            total_b // pixel_count,
        )

    def _get_brightness(self, color: Tuple[int, int, int]) -> int:
        """Calculate perceived brightness of a color."""
        # Use perceived luminance formula
        return int(0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2])

    def _get_dominant_color_channel(self, color: Tuple[int, int, int]) -> str:
        """Determine which color channel is dominant."""
        r, g, b = color
        if r > g and r > b:
            return "red"
        elif g > r and g > b:
            return "green"
        elif b > r and b > g:
            return "blue"
        else:
            return "balanced"

    def _classify_terrain_by_color(
        self, avg_color: Tuple[int, int, int], brightness: int, dominant: str
    ) -> Tuple[str, bool]:
        """
        Classify terrain type based on color analysis.

        Returns:
            Tuple of (terrain_type, passable)
        """
        r, g, b = avg_color

        # Water: Blue dominant, medium-high brightness
        if dominant == "blue" and brightness > 100:
            return ("water", False)

        # Grass: Green dominant, medium brightness
        if dominant == "green" and 80 < brightness < 200:
            return ("grass", True)

        # Lava: Red dominant, high brightness
        if dominant == "red" and brightness > 150:
            return ("lava", False)

        # Stone/Wall: Low saturation, low-medium brightness
        saturation = max(r, g, b) - min(r, g, b)
        if saturation < 30 and brightness < 150:
            return ("stone", False)

        # Dirt/Ground: Balanced, medium-low brightness
        if dominant == "balanced" and 60 < brightness < 140:
            return ("dirt", True)

        # Sand: High brightness, yellow-ish
        if r > 200 and g > 180 and b < 180:
            return ("sand", True)

        # Default: floor (passable)
        return ("floor", True)

    def _has_color_variation(self, surface: pygame.Surface) -> bool:
        """Check if a surface has significant color variation."""
        width, height = surface.get_size()
        colors = []

        # Sample some pixels
        sample_points = [
            (width // 4, height // 4),
            (3 * width // 4, height // 4),
            (width // 4, 3 * height // 4),
            (3 * width // 4, 3 * height // 4),
            (width // 2, height // 2),
        ]

        for x, y in sample_points:
            if x < width and y < height:
                colors.append(surface.get_at((x, y))[:3])

        if not colors:
            return False

        # Calculate variation
        avg_variation = 0
        for i in range(len(colors) - 1):
            c1 = colors[i]
            c2 = colors[i + 1]
            variation = abs(c1[0] - c2[0]) + abs(c1[1] - c2[1]) + abs(c1[2] - c2[2])
            avg_variation += variation

        avg_variation /= len(colors) - 1
        return avg_variation > 20  # Threshold for "has variation"

    def create_autotiling_rules(self, tileset_id: str, terrain_tag: str) -> Dict:
        """
        Generate autotiling rules for a terrain type.

        Autotiling automatically selects the correct tile based on
        neighboring tiles.

        Args:
            tileset_id: Tileset containing the tiles
            terrain_tag: Terrain tag to create rules for

        Returns:
            Dictionary of autotiling rules
        """
        # This is a simplified autotiling system
        # In a full implementation, this would analyze tile patterns
        # and create Wang tiles or blob autotiling rules

        rules = {
            "terrain_tag": terrain_tag,
            "tileset_id": tileset_id,
            "rules": {
                # Pattern: "N,NE,E,SE,S,SW,W,NW" where 1 = same terrain, 0 = different
                "11111111": "center_all",  # Surrounded by same terrain
                "11101110": "top_edge",
                "01110111": "right_edge",
                "01011101": "bottom_edge",
                "11011011": "left_edge",
                "11001100": "top_right_corner",
                "00110011": "bottom_right_corner",
                "00001101": "bottom_left_corner",
                "11010100": "top_left_corner",
            },
        }

        return rules

    def suggest_tile_variations(
        self, tileset_id: str, tile_id: int, count: int = 3
    ) -> List[pygame.Surface]:
        """
        Generate variations of a tile using AI.

        Args:
            tileset_id: Tileset containing the original tile
            tile_id: ID of tile to create variations for
            count: Number of variations to generate

        Returns:
            List of tile surface variations
        """
        if not self.tileset_manager:
            raise ValueError("TilesetManager not set")

        # Get original tile
        original_tile = self.tileset_manager.get_tile_surface(tileset_id, tile_id)
        if not original_tile:
            raise ValueError(f"Tile {tile_id} not found in tileset {tileset_id}")

        variations = []
        size = original_tile.get_size()

        for i in range(count):
            # Create variation by adjusting colors and adding noise
            variation = original_tile.copy()

            # Adjust hue slightly
            hue_shift = random.randint(-10, 10)
            for x in range(size[0]):
                for y in range(size[1]):
                    color = variation.get_at((x, y))
                    if color[3] > 0:  # Not transparent
                        new_color = (
                            max(0, min(255, color[0] + hue_shift)),
                            max(0, min(255, color[1] + hue_shift)),
                            max(0, min(255, color[2] + hue_shift)),
                            color[3],
                        )
                        variation.set_at((x, y), new_color)

            # Add some noise
            self._add_noise(variation, (128, 128, 128), size[0], 0.05)

            variations.append(variation)

        return variations


# Singleton instance
_ai_tileset_generator: Optional[AITilesetGenerator] = None


def get_ai_tileset_generator(
    tileset_manager: Optional[TilesetManager] = None,
) -> AITilesetGenerator:
    """
    Get the global AI tileset generator instance.

    Args:
        tileset_manager: TilesetManager to use (only on first call)

    Returns:
        AITilesetGenerator singleton
    """
    global _ai_tileset_generator
    if _ai_tileset_generator is None:
        _ai_tileset_generator = AITilesetGenerator(tileset_manager)
    elif tileset_manager is not None and _ai_tileset_generator.tileset_manager is None:
        _ai_tileset_generator.tileset_manager = tileset_manager
    return _ai_tileset_generator


def reset_ai_tileset_generator():
    """Reset the global AI tileset generator (useful for testing)."""
    global _ai_tileset_generator
    _ai_tileset_generator = None
