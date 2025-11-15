"""
Character Generator Core

A modular character sprite generator with layer-based composition,
color tinting, sprite sheet support, and preset management.

Features:
- Layer-based character composition (body, hair, clothes, accessories)
- Color tinting for customization
- Multi-frame sprite sheet composition (walk, idle, attack animations)
- Support for 4/8-directional sprites
- JSON preset save/load
- Randomization
- Multiple output sizes (32x32, 48x48, 64x64)
- AI-friendly API for description-based generation

Example:
    >>> gen = CharacterGenerator()
    >>> gen.load_component_library("assets/character_components/")
    >>> character = gen.create_character({
    ...     "body": "human_male",
    ...     "hair": "short_brown",
    ...     "outfit": "knight_armor",
    ...     "weapon": "sword"
    ... })
    >>> gen.render_character(character, "output/knight.png")
"""

from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pygame
from PIL import Image


class LayerType(Enum):
    """Character component layer types in render order (bottom to top)."""

    BODY = 0  # Base body/skin
    BODY_DETAIL = 1  # Scars, tattoos
    UNDERWEAR = 2  # Base clothing layer
    LEGS = 3  # Pants, leg armor
    FEET = 4  # Shoes, boots
    TORSO = 5  # Shirt, chest armor
    BELT = 6  # Belt, waist accessories
    HANDS = 7  # Gloves, gauntlets
    CAPE = 8  # Cape, cloak (behind character)
    WEAPON_BACK = 9  # Weapon on back (sheathed)
    EYES = 10  # Eyes
    HAIR_BACK = 11  # Hair behind head
    HAIR_FRONT = 12  # Hair in front
    FACIAL_HAIR = 13  # Beard, mustache
    HEAD = 14  # Helmet, hat, crown
    NECK = 15  # Necklace, scarf
    WEAPON = 16  # Weapon in hand
    ACCESSORY = 17  # Misc accessories
    EFFECT = 18  # Special effects, aura


class Direction(Enum):
    """Sprite facing directions."""

    DOWN = 0  # South
    LEFT = 1  # West
    RIGHT = 2  # East
    UP = 3  # North
    DOWN_LEFT = 4
    DOWN_RIGHT = 5
    UP_LEFT = 6
    UP_RIGHT = 7


@dataclass
class ColorTint:
    """RGB color tint (0-255 per channel)."""

    r: int = 255
    g: int = 255
    b: int = 255
    a: int = 255  # Alpha/transparency

    def to_tuple(self) -> Tuple[int, int, int, int]:
        """Convert to RGBA tuple."""
        return (self.r, self.g, self.b, self.a)

    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary."""
        return {"r": self.r, "g": self.g, "b": self.b, "a": self.a}

    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> ColorTint:
        """Create from dictionary."""
        return cls(
            r=data.get("r", 255), g=data.get("g", 255), b=data.get("b", 255), a=data.get("a", 255)
        )

    @classmethod
    def from_hex(cls, hex_color: str) -> ColorTint:
        """Create from hex color string (#RRGGBB or #RRGGBBAA)."""
        hex_color = hex_color.lstrip("#")
        if len(hex_color) == 6:
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
            return cls(r, g, b, 255)
        elif len(hex_color) == 8:
            r, g, b, a = (
                int(hex_color[0:2], 16),
                int(hex_color[2:4], 16),
                int(hex_color[4:6], 16),
                int(hex_color[6:8], 16),
            )
            return cls(r, g, b, a)
        else:
            raise ValueError(f"Invalid hex color: {hex_color}")


@dataclass
class ComponentLayer:
    """A single component layer with optional color tint."""

    layer_type: LayerType
    component_id: str  # ID of the component (e.g., "hair_long_blonde")
    tint: Optional[ColorTint] = None
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "layer_type": self.layer_type.name,
            "component_id": self.component_id,
            "tint": self.tint.to_dict() if self.tint else None,
            "enabled": self.enabled,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ComponentLayer:
        """Create from dictionary."""
        return cls(
            layer_type=LayerType[data["layer_type"]],
            component_id=data["component_id"],
            tint=ColorTint.from_dict(data["tint"]) if data.get("tint") else None,
            enabled=data.get("enabled", True),
        )


@dataclass
class CharacterPreset:
    """A complete character definition with all layers."""

    name: str
    description: str = ""
    layers: List[ComponentLayer] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_layer(self, layer_type: LayerType) -> Optional[ComponentLayer]:
        """Get layer by type."""
        for layer in self.layers:
            if layer.layer_type == layer_type:
                return layer
        return None

    def add_layer(self, layer: ComponentLayer):
        """Add or replace a layer."""
        # Remove existing layer of same type
        self.layers = [l for l in self.layers if l.layer_type != layer.layer_type]
        self.layers.append(layer)
        # Sort by layer order
        self.layers.sort(key=lambda l: l.layer_type.value)

    def remove_layer(self, layer_type: LayerType):
        """Remove a layer."""
        self.layers = [l for l in self.layers if l.layer_type != layer_type]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "layers": [layer.to_dict() for layer in self.layers],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CharacterPreset:
        """Create from dictionary."""
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            layers=[ComponentLayer.from_dict(l) for l in data.get("layers", [])],
            metadata=data.get("metadata", {}),
        )


@dataclass
class ComponentSprite:
    """A sprite component with frames and directions."""

    component_id: str
    layer_type: LayerType
    surface: pygame.Surface  # Full sprite sheet
    frame_width: int
    frame_height: int
    num_frames: int = 1
    num_directions: int = 1  # 1, 4, or 8
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_frame(self, frame: int = 0, direction: Direction = Direction.DOWN) -> pygame.Surface:
        """
        Extract a single frame from the sprite sheet.

        Args:
            frame: Animation frame index (0 to num_frames-1)
            direction: Facing direction

        Returns:
            pygame.Surface of the specific frame
        """
        # Calculate position in sprite sheet
        # Layout: [direction][frame]
        # Each row = one direction, each column = one frame

        dir_index = direction.value
        if dir_index >= self.num_directions:
            dir_index = 0  # Fallback to first direction

        x = frame * self.frame_width
        y = dir_index * self.frame_height

        # Extract frame
        frame_surface = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
        frame_surface.blit(
            self.surface, (0, 0), pygame.Rect(x, y, self.frame_width, self.frame_height)
        )

        return frame_surface


class CharacterGenerator:
    """
    Character generator with layer-based composition.

    This generator loads component sprites organized by layer type,
    composes them with optional color tinting, and exports complete
    character sprite sheets.

    Component Library Structure:
        assets/character_components/
        ├── body/
        │   ├── human_male.png
        │   ├── human_female.png
        │   └── elf_male.png
        ├── hair/
        │   ├── short_brown.png
        │   ├── long_blonde.png
        │   └── ponytail_red.png
        ├── outfit/
        │   ├── knight_armor.png
        │   ├── mage_robe.png
        │   └── peasant_clothes.png
        └── weapon/
            ├── sword.png
            ├── staff.png
            └── bow.png

    Each sprite should be:
    - Transparent PNG
    - Organized as [direction rows][frame columns]
    - All components same size for proper alignment
    """

    def __init__(self, default_size: int = 32):
        """
        Initialize character generator.

        Args:
            default_size: Default sprite size (32, 48, or 64)
        """
        pygame.init()  # Ensure pygame is initialized

        self.default_size = default_size
        self.component_library: Dict[str, ComponentSprite] = {}
        self.presets: Dict[str, CharacterPreset] = {}

        # Default component metadata (maps layer type to available components)
        self.available_components: Dict[LayerType, List[str]] = {layer: [] for layer in LayerType}

    def load_component_library(self, library_path: Union[str, Path]):
        """
        Load all component sprites from a directory structure.

        Expected structure:
            library_path/
            ├── body/
            ├── hair/
            ├── outfit/
            └── ...

        Each subdirectory name should match a LayerType name (lowercase).
        Each file is a component sprite.

        Args:
            library_path: Path to component library root
        """
        library_path = Path(library_path)

        if not library_path.exists():
            print(f"Warning: Component library not found at {library_path}")
            return

        # Map directory names to LayerTypes (including friendly aliases)
        layer_map = {layer.name.lower(): layer for layer in LayerType}

        # Add friendly aliases for common directory names
        layer_map.update(
            {
                "hair": LayerType.HAIR_FRONT,  # Default to front hair
                "outfit": LayerType.TORSO,  # Outfit = torso clothing
                "armor": LayerType.TORSO,  # Armor = torso
                "clothes": LayerType.TORSO,
                "helmet": LayerType.HEAD,
                "hat": LayerType.HEAD,
                "shield": LayerType.ACCESSORY,
            }
        )

        loaded_count = 0

        for layer_dir in library_path.iterdir():
            if not layer_dir.is_dir():
                continue

            layer_name = layer_dir.name.lower()
            if layer_name not in layer_map:
                print(f"Warning: Unknown layer directory '{layer_name}'")
                continue

            layer_type = layer_map[layer_name]

            # Load all sprites in this layer directory
            for sprite_file in layer_dir.glob("*.png"):
                component_id = f"{layer_name}_{sprite_file.stem}"

                try:
                    surface = pygame.image.load(str(sprite_file))

                    # Auto-detect sprite sheet layout
                    # Default: assume single frame, single direction
                    # TODO: Read from metadata file if available
                    width = surface.get_width()
                    height = surface.get_height()

                    # Check for metadata JSON
                    meta_file = sprite_file.with_suffix(".json")
                    if meta_file.exists():
                        with open(meta_file) as f:
                            metadata = json.load(f)

                        num_frames = metadata.get("frames", 1)
                        num_directions = metadata.get("directions", 1)
                        frame_width = metadata.get("frame_width", width // num_frames)
                        frame_height = metadata.get("frame_height", height // num_directions)
                    else:
                        # Default: single frame, single direction
                        num_frames = 1
                        num_directions = 1
                        frame_width = width
                        frame_height = height
                        metadata = {}

                    component = ComponentSprite(
                        component_id=component_id,
                        layer_type=layer_type,
                        surface=surface,
                        frame_width=frame_width,
                        frame_height=frame_height,
                        num_frames=num_frames,
                        num_directions=num_directions,
                        metadata=metadata,
                    )

                    self.component_library[component_id] = component
                    self.available_components[layer_type].append(component_id)
                    loaded_count += 1

                except Exception as e:
                    print(f"Error loading {sprite_file}: {e}")

        print(f"Loaded {loaded_count} components from {library_path}")

    def create_character(
        self,
        components: Dict[str, str],
        tints: Optional[Dict[str, ColorTint]] = None,
        name: str = "Character",
    ) -> CharacterPreset:
        """
        Create a character preset from component selections.

        Args:
            components: Dict mapping layer type name to component ID
                       Example: {"body": "human_male", "hair": "short_brown"}
            tints: Optional color tints per layer
            name: Character name

        Returns:
            CharacterPreset ready to render

        Example:
            >>> char = gen.create_character({
            ...     "body": "body_human_male",
            ...     "hair": "hair_short_brown",
            ...     "torso": "outfit_knight_armor"
            ... }, tints={"hair": ColorTint(180, 100, 50)})
        """
        if tints is None:
            tints = {}

        # Friendly name mappings
        friendly_names = {
            "hair": LayerType.HAIR_FRONT,
            "outfit": LayerType.TORSO,
            "armor": LayerType.TORSO,
            "clothes": LayerType.TORSO,
            "helmet": LayerType.HEAD,
            "hat": LayerType.HEAD,
        }

        preset = CharacterPreset(name=name)

        for layer_name, component_id in components.items():
            # Convert layer name to LayerType
            layer_type = None

            # Try friendly name first
            if layer_name.lower() in friendly_names:
                layer_type = friendly_names[layer_name.lower()]
            else:
                # Try exact LayerType name
                try:
                    layer_type = LayerType[layer_name.upper()]
                except KeyError:
                    print(f"Warning: Unknown layer type '{layer_name}'")
                    continue

            # Check if component exists
            if component_id not in self.component_library:
                print(f"Warning: Component '{component_id}' not found")
                continue

            # Create layer
            tint = tints.get(layer_name)
            layer = ComponentLayer(
                layer_type=layer_type, component_id=component_id, tint=tint, enabled=True
            )

            preset.add_layer(layer)

        return preset

    def apply_color_tint(self, surface: pygame.Surface, tint: ColorTint) -> pygame.Surface:
        """
        Apply color tint to a surface.

        Uses multiply blend mode to tint the sprite while preserving
        alpha transparency.

        Args:
            surface: Original surface
            tint: Color tint to apply

        Returns:
            Tinted surface
        """
        # Create a copy
        tinted = surface.copy()

        # Create tint overlay
        overlay = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
        overlay.fill(tint.to_tuple())

        # Apply multiply blend (preserves transparency)
        # Formula: result = (surface * tint) / 255
        arr = pygame.surfarray.pixels3d(tinted)
        overlay_arr = pygame.surfarray.pixels3d(overlay)

        # Multiply and normalize
        arr[:] = (arr.astype(np.float32) * overlay_arr.astype(np.float32) / 255).astype(np.uint8)

        del arr  # Release pixel array lock
        del overlay_arr

        return tinted

    def compose_frame(
        self,
        preset: CharacterPreset,
        frame: int = 0,
        direction: Direction = Direction.DOWN,
        output_size: Optional[int] = None,
    ) -> pygame.Surface:
        """
        Compose a single frame from all layers.

        Args:
            preset: Character preset with layers
            frame: Animation frame index
            direction: Facing direction
            output_size: Output size (overrides default)

        Returns:
            Composed frame surface
        """
        size = output_size or self.default_size

        # Create output surface
        output = pygame.Surface((size, size), pygame.SRCALPHA)
        output.fill((0, 0, 0, 0))  # Transparent

        # Render layers in order (bottom to top)
        sorted_layers = sorted(preset.layers, key=lambda l: l.layer_type.value)

        for layer in sorted_layers:
            if not layer.enabled:
                continue

            component = self.component_library.get(layer.component_id)
            if not component:
                print(f"Warning: Component '{layer.component_id}' not found")
                continue

            # Get frame from component
            frame_surface = component.get_frame(frame, direction)

            # Apply color tint if specified
            if layer.tint:
                frame_surface = self.apply_color_tint(frame_surface, layer.tint)

            # Scale to output size if needed
            if frame_surface.get_width() != size or frame_surface.get_height() != size:
                frame_surface = pygame.transform.scale(frame_surface, (size, size))

            # Composite onto output
            output.blit(frame_surface, (0, 0))

        return output

    def render_sprite_sheet(
        self,
        preset: CharacterPreset,
        num_frames: int = 4,
        directions: Optional[List[Direction]] = None,
        output_size: Optional[int] = None,
    ) -> pygame.Surface:
        """
        Render a complete sprite sheet with multiple frames and directions.

        Layout: [direction rows][frame columns]

        Args:
            preset: Character preset
            num_frames: Number of animation frames
            directions: List of directions (default: 4-directional)
            output_size: Size of each frame

        Returns:
            Complete sprite sheet surface
        """
        if directions is None:
            directions = [Direction.DOWN, Direction.LEFT, Direction.RIGHT, Direction.UP]

        size = output_size or self.default_size

        # Calculate sheet dimensions
        sheet_width = size * num_frames
        sheet_height = size * len(directions)

        # Create sheet surface
        sheet = pygame.Surface((sheet_width, sheet_height), pygame.SRCALPHA)
        sheet.fill((0, 0, 0, 0))

        # Render each frame
        for dir_idx, direction in enumerate(directions):
            for frame_idx in range(num_frames):
                frame = self.compose_frame(preset, frame_idx, direction, size)

                x = frame_idx * size
                y = dir_idx * size

                sheet.blit(frame, (x, y))

        return sheet

    def render_character(
        self,
        preset: CharacterPreset,
        output_path: Union[str, Path],
        num_frames: int = 4,
        directions: Optional[List[Direction]] = None,
        output_size: Optional[int] = None,
    ):
        """
        Render and save a character sprite sheet.

        Args:
            preset: Character preset to render
            output_path: Where to save the sprite sheet
            num_frames: Number of animation frames
            directions: Directions to render
            output_size: Size of each frame
        """
        sheet = self.render_sprite_sheet(preset, num_frames, directions, output_size)

        # Save as PNG
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        pygame.image.save(sheet, str(output_path))
        print(f"Saved character sprite sheet to {output_path}")

        # Save preset JSON
        preset_path = output_path.with_suffix(".json")
        self.save_preset(preset, preset_path)

    def save_preset(self, preset: CharacterPreset, path: Union[str, Path]):
        """Save character preset to JSON."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            json.dump(preset.to_dict(), f, indent=2)

        print(f"Saved preset to {path}")

    def load_preset(self, path: Union[str, Path]) -> CharacterPreset:
        """Load character preset from JSON."""
        path = Path(path)

        with open(path, "r") as f:
            data = json.load(f)

        preset = CharacterPreset.from_dict(data)
        self.presets[preset.name] = preset

        print(f"Loaded preset '{preset.name}' from {path}")
        return preset

    def randomize_character(
        self, layer_types: Optional[List[LayerType]] = None, name: str = "Random Character"
    ) -> CharacterPreset:
        """
        Create a random character by selecting random components.

        Args:
            layer_types: Which layers to randomize (default: all with components)
            name: Character name

        Returns:
            Randomized character preset
        """
        if layer_types is None:
            # Use all layers that have components
            layer_types = [lt for lt in LayerType if self.available_components[lt]]

        preset = CharacterPreset(name=name, description="Randomly generated character")

        for layer_type in layer_types:
            available = self.available_components[layer_type]
            if not available:
                continue

            # Pick random component
            component_id = random.choice(available)

            # Random tint (50% chance)
            tint = None
            if random.random() < 0.5:
                tint = ColorTint(
                    r=random.randint(150, 255),
                    g=random.randint(150, 255),
                    b=random.randint(150, 255),
                    a=255,
                )

            layer = ComponentLayer(
                layer_type=layer_type, component_id=component_id, tint=tint, enabled=True
            )

            preset.add_layer(layer)

        return preset

    def generate_from_description(
        self, description: str, name: str = "Generated Character"
    ) -> CharacterPreset:
        """
        Generate a character from a text description.

        This is an AI-friendly API that interprets natural language
        descriptions and selects appropriate components.

        Args:
            description: Natural language character description
                        Example: "A knight with brown hair and blue armor"
            name: Character name

        Returns:
            Character preset

        Note:
            This is a simplified rule-based implementation.
            For true AI-powered generation, integrate with an LLM.
        """
        # Simple keyword matching
        # In production, use an LLM to interpret description

        desc_lower = description.lower()
        components = {}
        tints = {}

        # Body detection
        if "human" in desc_lower or "person" in desc_lower:
            if "male" in desc_lower or "knight" in desc_lower or "warrior" in desc_lower:
                components["body"] = "body_human_male"
            elif "female" in desc_lower:
                components["body"] = "body_human_female"
        elif "elf" in desc_lower:
            components["body"] = "body_elf_male"

        # Hair detection
        if "brown hair" in desc_lower or "brunette" in desc_lower:
            components["hair"] = "hair_short_brown"
            tints["hair"] = ColorTint(139, 90, 43)  # Brown
        elif "blonde" in desc_lower or "blond hair" in desc_lower:
            components["hair"] = "hair_long_blonde"
            tints["hair"] = ColorTint(255, 230, 150)  # Blonde
        elif "red hair" in desc_lower:
            components["hair"] = "hair_ponytail_red"
            tints["hair"] = ColorTint(200, 80, 60)  # Red

        # Outfit detection
        if "knight" in desc_lower or "armor" in desc_lower:
            components["torso"] = "outfit_knight_armor"
            if "blue" in desc_lower:
                tints["torso"] = ColorTint(100, 100, 200)  # Blue
            elif "red" in desc_lower:
                tints["torso"] = ColorTint(200, 80, 80)  # Red
        elif "mage" in desc_lower or "wizard" in desc_lower or "robe" in desc_lower:
            components["torso"] = "outfit_mage_robe"
        elif "peasant" in desc_lower or "farmer" in desc_lower:
            components["torso"] = "outfit_peasant_clothes"

        # Weapon detection
        if "sword" in desc_lower:
            components["weapon"] = "weapon_sword"
        elif "staff" in desc_lower:
            components["weapon"] = "weapon_staff"
        elif "bow" in desc_lower:
            components["weapon"] = "weapon_bow"

        # If no components matched, randomize
        if not components:
            return self.randomize_character(name=name)

        return self.create_character(components, tints, name)

    def list_components(self, layer_type: Optional[LayerType] = None) -> Dict[LayerType, List[str]]:
        """
        List available components.

        Args:
            layer_type: Specific layer to list (None = all)

        Returns:
            Dictionary of layer types and their components
        """
        if layer_type:
            return {layer_type: self.available_components[layer_type]}
        return self.available_components.copy()

    def export_multi_size(
        self,
        preset: CharacterPreset,
        output_dir: Union[str, Path],
        sizes: Optional[List[int]] = None,
        num_frames: int = 4,
        directions: Optional[List[Direction]] = None,
    ):
        """
        Export character at multiple sizes.

        Args:
            preset: Character preset
            output_dir: Output directory
            sizes: List of sizes to export (default: [32, 48, 64])
            num_frames: Number of frames
            directions: Directions to render
        """
        if sizes is None:
            sizes = [32, 48, 64]

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        for size in sizes:
            filename = f"{preset.name}_{size}x{size}.png"
            output_path = output_dir / filename

            self.render_character(
                preset, output_path, num_frames=num_frames, directions=directions, output_size=size
            )

            print(f"Exported {size}x{size} sprite sheet")


# Convenience functions


def quick_character(
    description: str,
    output_path: str,
    library_path: str = "assets/character_components/",
    size: int = 32,
) -> CharacterPreset:
    """
    Quick character generation from description.

    Args:
        description: Character description
        output_path: Where to save sprite sheet
        library_path: Component library path
        size: Output size

    Returns:
        Generated character preset

    Example:
        >>> char = quick_character(
        ...     "A knight with brown hair and blue armor",
        ...     "output/knight.png"
        ... )
    """
    gen = CharacterGenerator(default_size=size)
    gen.load_component_library(library_path)

    character = gen.generate_from_description(description)
    gen.render_character(character, output_path)

    return character


if __name__ == "__main__":
    # Example usage
    print("Character Generator - Example\n")

    # Create generator
    gen = CharacterGenerator(default_size=32)

    # In a real scenario, load component library:
    # gen.load_component_library("assets/character_components/")

    print("Character Generator initialized")
    print("\nAvailable features:")
    print("- Layer-based composition")
    print("- Color tinting")
    print("- Multi-frame sprite sheets")
    print("- 4/8-directional sprites")
    print("- JSON presets")
    print("- Randomization")
    print("- Multiple output sizes")
    print("- AI-friendly description API")

    # Example preset creation (without actual sprites)
    preset = CharacterPreset(name="Example Knight", description="A brave knight character")

    # Add some example layers
    preset.add_layer(
        ComponentLayer(
            layer_type=LayerType.BODY,
            component_id="body_human_male",
            tint=ColorTint(255, 220, 180),  # Skin tone
        )
    )

    preset.add_layer(
        ComponentLayer(
            layer_type=LayerType.HAIR,
            component_id="hair_short_brown",
            tint=ColorTint(139, 90, 43),  # Brown hair
        )
    )

    preset.add_layer(
        ComponentLayer(
            layer_type=LayerType.TORSO,
            component_id="outfit_knight_armor",
            tint=ColorTint(100, 100, 200),  # Blue armor
        )
    )

    # Save preset
    gen.save_preset(preset, "test_outputs/knight_preset.json")

    print("\nExample preset created and saved!")
