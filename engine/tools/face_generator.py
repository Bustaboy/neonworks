"""
Face Generator Core

A modular face generator with component-based facial features,
expression support, and color synchronization with body sprites.

Features:
- Component-based facial features (eyes, nose, mouth, eyebrows, etc.)
- Expression presets (neutral, happy, sad, angry, surprised, etc.)
- Color synchronization with character sprites
- Multiple export sizes (96x96, 128x128, 256x256)
- Batch generation of all expressions
- JSON preset save/load

Example:
    >>> gen = FaceGenerator()
    >>> gen.load_component_library("assets/face_components/")
    >>> face = gen.create_face({
    ...     "base": "human_light",
    ...     "eyes": "round_brown",
    ...     "nose": "medium",
    ...     "mouth": "smile"
    ... })
    >>> gen.render_face(face, "output/face.png", expression=Expression.HAPPY)
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union

import pygame
import numpy as np


class FaceLayerType(Enum):
    """Face component layer types in render order (bottom to top)."""

    BASE = 0           # Face base/skin tone
    BLUSH = 1          # Cheek blush
    NOSE = 2           # Nose
    MOUTH = 3          # Mouth
    EYES = 4           # Eyes
    EYEBROWS = 5       # Eyebrows
    EYE_DETAIL = 6     # Eye highlights, pupils
    FACIAL_HAIR = 7    # Beard, mustache
    GLASSES = 8        # Glasses, monocle
    FACE_PAINT = 9     # Tattoos, scars, makeup
    ACCESSORY = 10     # Earrings, piercings
    EFFECT = 11        # Special effects (tears, sweat, etc.)


class Expression(Enum):
    """Face expressions."""

    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    SURPRISED = "surprised"
    SCARED = "scared"
    DISGUSTED = "disgusted"
    CONFUSED = "confused"
    WINK = "wink"
    EMBARRASSED = "embarrassed"


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
            r=data.get("r", 255),
            g=data.get("g", 255),
            b=data.get("b", 255),
            a=data.get("a", 255)
        )

    @classmethod
    def from_hex(cls, hex_color: str) -> ColorTint:
        """Create from hex color string (#RRGGBB or #RRGGBBAA)."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
            return cls(r, g, b, 255)
        elif len(hex_color) == 8:
            r, g, b, a = (int(hex_color[0:2], 16), int(hex_color[2:4], 16),
                         int(hex_color[4:6], 16), int(hex_color[6:8], 16))
            return cls(r, g, b, a)
        else:
            raise ValueError(f"Invalid hex color: {hex_color}")


@dataclass
class FaceLayer:
    """A single face component layer with optional color tint."""

    layer_type: FaceLayerType
    component_id: str
    tint: Optional[ColorTint] = None
    enabled: bool = True
    expression_offset: Dict[Expression, Tuple[int, int]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "layer_type": self.layer_type.name,
            "component_id": self.component_id,
            "tint": self.tint.to_dict() if self.tint else None,
            "enabled": self.enabled,
            "expression_offset": {
                expr.name: offset for expr, offset in self.expression_offset.items()
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> FaceLayer:
        """Create from dictionary."""
        expr_offsets = {}
        if "expression_offset" in data:
            expr_offsets = {
                Expression[k]: tuple(v) for k, v in data["expression_offset"].items()
            }

        return cls(
            layer_type=FaceLayerType[data["layer_type"]],
            component_id=data["component_id"],
            tint=ColorTint.from_dict(data["tint"]) if data.get("tint") else None,
            enabled=data.get("enabled", True),
            expression_offset=expr_offsets
        )


@dataclass
class FacePreset:
    """A complete face definition with all layers."""

    name: str
    description: str = ""
    layers: List[FaceLayer] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_layer(self, layer_type: FaceLayerType) -> Optional[FaceLayer]:
        """Get layer by type."""
        for layer in self.layers:
            if layer.layer_type == layer_type:
                return layer
        return None

    def add_layer(self, layer: FaceLayer):
        """Add or replace a layer."""
        # Remove existing layer of same type
        self.layers = [l for l in self.layers if l.layer_type != layer.layer_type]
        self.layers.append(layer)
        # Sort by layer order
        self.layers.sort(key=lambda l: l.layer_type.value)

    def remove_layer(self, layer_type: FaceLayerType):
        """Remove a layer."""
        self.layers = [l for l in self.layers if l.layer_type != layer_type]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "layers": [layer.to_dict() for layer in self.layers],
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> FacePreset:
        """Create from dictionary."""
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            layers=[FaceLayer.from_dict(l) for l in data.get("layers", [])],
            metadata=data.get("metadata", {})
        )


@dataclass
class FaceComponent:
    """A face component with expression variants."""

    component_id: str
    layer_type: FaceLayerType
    expressions: Dict[Expression, pygame.Surface]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_expression(self, expression: Expression = Expression.NEUTRAL) -> pygame.Surface:
        """
        Get the surface for a specific expression.

        Args:
            expression: Desired expression

        Returns:
            pygame.Surface for the expression (falls back to neutral)
        """
        if expression in self.expressions:
            return self.expressions[expression]
        # Fallback to neutral
        if Expression.NEUTRAL in self.expressions:
            return self.expressions[Expression.NEUTRAL]
        # Last resort: return any available expression
        if self.expressions:
            return next(iter(self.expressions.values()))
        # No expressions available
        raise ValueError(f"Component {self.component_id} has no expressions")


class FaceGenerator:
    """
    Face generator with component-based composition and expressions.

    Component Library Structure:
        assets/face_components/
        ├── base/
        │   ├── human_light.png
        │   ├── human_medium.png
        │   └── human_dark.png
        ├── eyes/
        │   ├── round_brown/
        │   │   ├── neutral.png
        │   │   ├── happy.png
        │   │   ├── sad.png
        │   │   └── angry.png
        │   └── almond_blue/
        │       ├── neutral.png
        │       └── ...
        ├── mouth/
        │   ├── smile/
        │   │   ├── neutral.png
        │   │   ├── happy.png
        │   │   └── sad.png
        │   └── ...
        └── ...

    Each component can have multiple expression variants.
    """

    def __init__(self, default_size: int = 128):
        """
        Initialize face generator.

        Args:
            default_size: Default face size (96, 128, or 256)
        """
        pygame.init()

        self.default_size = default_size
        self.component_library: Dict[str, FaceComponent] = {}
        self.presets: Dict[str, FacePreset] = {}

        # Available components by layer type
        self.available_components: Dict[FaceLayerType, List[str]] = {
            layer: [] for layer in FaceLayerType
        }

    def load_component_library(self, library_path: Union[str, Path]):
        """
        Load all face components from a directory structure.

        Expected structure:
            library_path/
            ├── base/
            ├── eyes/
            │   ├── round_brown/
            │   │   ├── neutral.png
            │   │   ├── happy.png
            │   │   └── ...
            ├── mouth/
            └── ...

        Args:
            library_path: Path to component library root
        """
        library_path = Path(library_path)

        if not library_path.exists():
            print(f"Warning: Face component library not found at {library_path}")
            return

        # Map directory names to FaceLayerTypes
        layer_map = {layer.name.lower(): layer for layer in FaceLayerType}

        loaded_count = 0

        for layer_dir in library_path.iterdir():
            if not layer_dir.is_dir():
                continue

            layer_name = layer_dir.name.lower()
            if layer_name not in layer_map:
                print(f"Warning: Unknown layer directory '{layer_name}'")
                continue

            layer_type = layer_map[layer_name]

            # Load components in this layer
            for comp_dir in layer_dir.iterdir():
                if comp_dir.is_file() and comp_dir.suffix == '.png':
                    # Single file component (no expressions)
                    component_id = f"{layer_name}_{comp_dir.stem}"
                    try:
                        surface = pygame.image.load(str(comp_dir))
                        component = FaceComponent(
                            component_id=component_id,
                            layer_type=layer_type,
                            expressions={Expression.NEUTRAL: surface}
                        )
                        self.component_library[component_id] = component
                        self.available_components[layer_type].append(component_id)
                        loaded_count += 1
                    except Exception as e:
                        print(f"Error loading {comp_dir}: {e}")

                elif comp_dir.is_dir():
                    # Directory with expression variants
                    component_id = f"{layer_name}_{comp_dir.name}"
                    expressions = {}

                    for expr_file in comp_dir.glob("*.png"):
                        expr_name = expr_file.stem.upper()
                        try:
                            expr = Expression[expr_name]
                            surface = pygame.image.load(str(expr_file))
                            expressions[expr] = surface
                        except KeyError:
                            print(f"Warning: Unknown expression '{expr_name}' in {expr_file}")
                        except Exception as e:
                            print(f"Error loading {expr_file}: {e}")

                    if expressions:
                        component = FaceComponent(
                            component_id=component_id,
                            layer_type=layer_type,
                            expressions=expressions
                        )
                        self.component_library[component_id] = component
                        self.available_components[layer_type].append(component_id)
                        loaded_count += 1

        print(f"Loaded {loaded_count} face components from {library_path}")

    def create_face(
        self,
        components: Dict[str, str],
        tints: Optional[Dict[str, ColorTint]] = None,
        name: str = "Face"
    ) -> FacePreset:
        """
        Create a face preset from component selections.

        Args:
            components: Dict mapping layer type name to component ID
            tints: Optional color tints per layer
            name: Face name

        Returns:
            FacePreset ready to render
        """
        if tints is None:
            tints = {}

        preset = FacePreset(name=name)

        for layer_name, component_id in components.items():
            # Convert layer name to FaceLayerType
            try:
                layer_type = FaceLayerType[layer_name.upper()]
            except KeyError:
                print(f"Warning: Unknown layer type '{layer_name}'")
                continue

            # Check if component exists
            if component_id not in self.component_library:
                print(f"Warning: Component '{component_id}' not found")
                continue

            # Create layer
            tint = tints.get(layer_name)
            layer = FaceLayer(
                layer_type=layer_type,
                component_id=component_id,
                tint=tint,
                enabled=True
            )

            preset.add_layer(layer)

        return preset

    def apply_color_tint(
        self,
        surface: pygame.Surface,
        tint: ColorTint
    ) -> pygame.Surface:
        """
        Apply color tint to a surface.

        Args:
            surface: Original surface
            tint: Color tint to apply

        Returns:
            Tinted surface
        """
        tinted = surface.copy()

        # Create tint overlay
        overlay = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
        overlay.fill(tint.to_tuple())

        # Apply multiply blend
        arr = pygame.surfarray.pixels3d(tinted)
        overlay_arr = pygame.surfarray.pixels3d(overlay)

        arr[:] = (arr.astype(np.float32) * overlay_arr.astype(np.float32) / 255).astype(np.uint8)

        del arr
        del overlay_arr

        return tinted

    def compose_face(
        self,
        preset: FacePreset,
        expression: Expression = Expression.NEUTRAL,
        output_size: Optional[int] = None
    ) -> pygame.Surface:
        """
        Compose a face from all layers with specified expression.

        Args:
            preset: Face preset with layers
            expression: Expression to render
            output_size: Output size (overrides default)

        Returns:
            Composed face surface
        """
        size = output_size or self.default_size

        # Create output surface
        output = pygame.Surface((size, size), pygame.SRCALPHA)
        output.fill((0, 0, 0, 0))

        # Render layers in order
        sorted_layers = sorted(preset.layers, key=lambda l: l.layer_type.value)

        for layer in sorted_layers:
            if not layer.enabled:
                continue

            component = self.component_library.get(layer.component_id)
            if not component:
                continue

            # Get expression surface
            try:
                expr_surface = component.get_expression(expression)
            except ValueError:
                continue

            # Apply color tint if specified
            if layer.tint:
                expr_surface = self.apply_color_tint(expr_surface, layer.tint)

            # Apply expression offset if specified
            offset_x, offset_y = layer.expression_offset.get(expression, (0, 0))

            # Scale to output size if needed
            if expr_surface.get_width() != size or expr_surface.get_height() != size:
                expr_surface = pygame.transform.scale(expr_surface, (size, size))

            # Composite onto output
            output.blit(expr_surface, (offset_x, offset_y))

        return output

    def render_all_expressions(
        self,
        preset: FacePreset,
        output_size: Optional[int] = None
    ) -> Dict[Expression, pygame.Surface]:
        """
        Render all expressions for a face.

        Args:
            preset: Face preset
            output_size: Size of each face

        Returns:
            Dictionary mapping expression to rendered surface
        """
        results = {}
        for expression in Expression:
            results[expression] = self.compose_face(preset, expression, output_size)
        return results

    def render_expression_sheet(
        self,
        preset: FacePreset,
        expressions: Optional[List[Expression]] = None,
        columns: int = 5,
        output_size: Optional[int] = None
    ) -> pygame.Surface:
        """
        Render a sheet with multiple expressions.

        Args:
            preset: Face preset
            expressions: List of expressions to render (default: all)
            columns: Number of columns in the sheet
            output_size: Size of each face

        Returns:
            Expression sheet surface
        """
        if expressions is None:
            expressions = list(Expression)

        size = output_size or self.default_size

        # Calculate sheet dimensions
        num_expressions = len(expressions)
        rows = (num_expressions + columns - 1) // columns
        sheet_width = size * columns
        sheet_height = size * rows

        # Create sheet surface
        sheet = pygame.Surface((sheet_width, sheet_height), pygame.SRCALPHA)
        sheet.fill((0, 0, 0, 0))

        # Render each expression
        for idx, expression in enumerate(expressions):
            row = idx // columns
            col = idx % columns

            face = self.compose_face(preset, expression, size)

            x = col * size
            y = row * size

            sheet.blit(face, (x, y))

        return sheet

    def render_face(
        self,
        preset: FacePreset,
        output_path: Union[str, Path],
        expression: Expression = Expression.NEUTRAL,
        output_size: Optional[int] = None
    ):
        """
        Render and save a single face expression.

        Args:
            preset: Face preset
            output_path: Where to save
            expression: Expression to render
            output_size: Face size
        """
        face = self.compose_face(preset, expression, output_size)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        pygame.image.save(face, str(output_path))
        print(f"Saved face to {output_path}")

    def batch_export_expressions(
        self,
        preset: FacePreset,
        output_dir: Union[str, Path],
        expressions: Optional[List[Expression]] = None,
        output_size: Optional[int] = None
    ):
        """
        Export all expressions as individual files.

        Args:
            preset: Face preset
            output_dir: Output directory
            expressions: Expressions to export (default: all)
            output_size: Face size
        """
        if expressions is None:
            expressions = list(Expression)

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        for expression in expressions:
            filename = f"{preset.name}_{expression.value}.png"
            output_path = output_dir / filename

            self.render_face(preset, output_path, expression, output_size)

        print(f"Exported {len(expressions)} expressions to {output_dir}")

    def save_preset(self, preset: FacePreset, path: Union[str, Path]):
        """Save face preset to JSON."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w') as f:
            json.dump(preset.to_dict(), f, indent=2)

        print(f"Saved preset to {path}")

    def load_preset(self, path: Union[str, Path]) -> FacePreset:
        """Load face preset from JSON."""
        path = Path(path)

        with open(path, 'r') as f:
            data = json.load(f)

        preset = FacePreset.from_dict(data)
        self.presets[preset.name] = preset

        print(f"Loaded preset '{preset.name}' from {path}")
        return preset

    def randomize_face(
        self,
        layer_types: Optional[List[FaceLayerType]] = None,
        name: str = "Random Face"
    ) -> FacePreset:
        """
        Create a random face.

        Args:
            layer_types: Which layers to randomize
            name: Face name

        Returns:
            Randomized face preset
        """
        if layer_types is None:
            layer_types = [lt for lt in FaceLayerType if self.available_components[lt]]

        preset = FacePreset(name=name, description="Randomly generated face")

        for layer_type in layer_types:
            available = self.available_components[layer_type]
            if not available:
                continue

            component_id = random.choice(available)

            # Random tint (30% chance)
            tint = None
            if random.random() < 0.3:
                tint = ColorTint(
                    r=random.randint(180, 255),
                    g=random.randint(180, 255),
                    b=random.randint(180, 255),
                    a=255
                )

            layer = FaceLayer(
                layer_type=layer_type,
                component_id=component_id,
                tint=tint,
                enabled=True
            )

            preset.add_layer(layer)

        return preset

    def list_components(
        self,
        layer_type: Optional[FaceLayerType] = None
    ) -> Dict[str, FaceComponent]:
        """
        List available components.

        Args:
            layer_type: Specific layer to list (None = all)

        Returns:
            Dictionary of component IDs to components
        """
        if layer_type:
            return {
                comp_id: comp for comp_id, comp in self.component_library.items()
                if comp.layer_type == layer_type
            }
        return self.component_library.copy()

    def sync_colors_from_character(
        self,
        preset: FacePreset,
        character_colors: Dict[str, ColorTint]
    ):
        """
        Synchronize face colors with character body colors.

        Args:
            preset: Face preset to update
            character_colors: Dict mapping feature names to colors
                             Example: {"skin": ColorTint(...), "hair": ColorTint(...)}
        """
        # Map character features to face layers
        mapping = {
            "skin": FaceLayerType.BASE,
            "hair": FaceLayerType.FACIAL_HAIR,
        }

        for feature_name, color in character_colors.items():
            if feature_name in mapping:
                layer_type = mapping[feature_name]
                layer = preset.get_layer(layer_type)
                if layer:
                    layer.tint = color
                    print(f"Synced {feature_name} color to face")


if __name__ == "__main__":
    print("Face Generator - Example\n")

    gen = FaceGenerator(default_size=128)

    print("Face Generator initialized")
    print("\nAvailable features:")
    print("- Component-based facial features")
    print("- Expression support (10 expressions)")
    print("- Color tinting")
    print("- Multiple export sizes")
    print("- Batch expression export")
    print("- Character color synchronization")

    # Example preset
    preset = FacePreset(
        name="Example Face",
        description="A friendly face"
    )

    print("\nExample preset created!")
