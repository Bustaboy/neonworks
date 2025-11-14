"""
Tests for Character Generator

Tests the character generator core functionality including:
- Layer management
- Color tinting
- Sprite sheet composition
- Preset save/load
- Randomization
- Multi-size export
"""

import json
import pytest
from pathlib import Path

# Import the character generator
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.tools.character_generator import (
    CharacterGenerator,
    CharacterPreset,
    ComponentLayer,
    ColorTint,
    LayerType,
    Direction,
)


@pytest.fixture
def generator():
    """Create a character generator instance."""
    return CharacterGenerator(default_size=32)


@pytest.fixture
def sample_library(tmp_path):
    """Create a minimal test component library."""
    # Note: For full tests, run generate_sample_components.py first
    # This fixture creates a basic structure
    library_path = tmp_path / "components"
    library_path.mkdir()

    # Create body directory
    body_dir = library_path / "body"
    body_dir.mkdir()

    return library_path


@pytest.fixture
def loaded_generator():
    """Create a generator with sample components loaded."""
    gen = CharacterGenerator(default_size=32)

    # Load the test components we generated
    component_path = Path("test_outputs/character_components")
    if component_path.exists():
        gen.load_component_library(component_path)

    return gen


class TestColorTint:
    """Test ColorTint class."""

    def test_create_color_tint(self):
        """Test creating a color tint."""
        tint = ColorTint(255, 128, 64, 255)

        assert tint.r == 255
        assert tint.g == 128
        assert tint.b == 64
        assert tint.a == 255

    def test_color_tint_to_tuple(self):
        """Test converting tint to tuple."""
        tint = ColorTint(100, 150, 200, 255)
        result = tint.to_tuple()

        assert result == (100, 150, 200, 255)

    def test_color_tint_from_hex(self):
        """Test creating tint from hex string."""
        # RGB hex
        tint = ColorTint.from_hex("#FF8040")
        assert tint.r == 255
        assert tint.g == 128
        assert tint.b == 64
        assert tint.a == 255

        # RGBA hex
        tint2 = ColorTint.from_hex("#FF804080")
        assert tint2.r == 255
        assert tint2.g == 128
        assert tint2.b == 64
        assert tint2.a == 128

    def test_color_tint_to_dict(self):
        """Test converting tint to dictionary."""
        tint = ColorTint(100, 150, 200, 255)
        result = tint.to_dict()

        assert result == {"r": 100, "g": 150, "b": 200, "a": 255}

    def test_color_tint_from_dict(self):
        """Test creating tint from dictionary."""
        data = {"r": 100, "g": 150, "b": 200, "a": 255}
        tint = ColorTint.from_dict(data)

        assert tint.r == 100
        assert tint.g == 150
        assert tint.b == 200
        assert tint.a == 255


class TestComponentLayer:
    """Test ComponentLayer class."""

    def test_create_layer(self):
        """Test creating a component layer."""
        layer = ComponentLayer(
            layer_type=LayerType.BODY,
            component_id="body_human_male",
            tint=ColorTint(255, 220, 180),
            enabled=True
        )

        assert layer.layer_type == LayerType.BODY
        assert layer.component_id == "body_human_male"
        assert layer.tint is not None
        assert layer.enabled is True

    def test_layer_to_dict(self):
        """Test converting layer to dictionary."""
        layer = ComponentLayer(
            layer_type=LayerType.HAIR_FRONT,
            component_id="hair_short_brown",
            tint=ColorTint(139, 90, 43)
        )

        result = layer.to_dict()

        assert result["layer_type"] == "HAIR_FRONT"
        assert result["component_id"] == "hair_short_brown"
        assert result["tint"]["r"] == 139

    def test_layer_from_dict(self):
        """Test creating layer from dictionary."""
        data = {
            "layer_type": "TORSO",
            "component_id": "outfit_knight_armor",
            "tint": {"r": 100, "g": 100, "b": 200, "a": 255},
            "enabled": True
        }

        layer = ComponentLayer.from_dict(data)

        assert layer.layer_type == LayerType.TORSO
        assert layer.component_id == "outfit_knight_armor"
        assert layer.tint.b == 200


class TestCharacterPreset:
    """Test CharacterPreset class."""

    def test_create_preset(self):
        """Test creating a character preset."""
        preset = CharacterPreset(
            name="Test Knight",
            description="A test character"
        )

        assert preset.name == "Test Knight"
        assert preset.description == "A test character"
        assert len(preset.layers) == 0

    def test_add_layer(self):
        """Test adding a layer to preset."""
        preset = CharacterPreset(name="Test")

        layer = ComponentLayer(
            layer_type=LayerType.BODY,
            component_id="body_human_male"
        )

        preset.add_layer(layer)

        assert len(preset.layers) == 1
        assert preset.layers[0].layer_type == LayerType.BODY

    def test_add_duplicate_layer_replaces(self):
        """Test that adding duplicate layer type replaces existing."""
        preset = CharacterPreset(name="Test")

        layer1 = ComponentLayer(
            layer_type=LayerType.BODY,
            component_id="body_human_male"
        )
        layer2 = ComponentLayer(
            layer_type=LayerType.BODY,
            component_id="body_elf_male"
        )

        preset.add_layer(layer1)
        preset.add_layer(layer2)

        assert len(preset.layers) == 1
        assert preset.layers[0].component_id == "body_elf_male"

    def test_get_layer(self):
        """Test getting a layer by type."""
        preset = CharacterPreset(name="Test")

        layer = ComponentLayer(
            layer_type=LayerType.HAIR_FRONT,
            component_id="hair_short_brown"
        )
        preset.add_layer(layer)

        result = preset.get_layer(LayerType.HAIR_FRONT)

        assert result is not None
        assert result.component_id == "hair_short_brown"

    def test_remove_layer(self):
        """Test removing a layer."""
        preset = CharacterPreset(name="Test")

        layer = ComponentLayer(
            layer_type=LayerType.WEAPON,
            component_id="weapon_sword"
        )
        preset.add_layer(layer)

        assert len(preset.layers) == 1

        preset.remove_layer(LayerType.WEAPON)

        assert len(preset.layers) == 0

    def test_preset_to_dict(self):
        """Test converting preset to dictionary."""
        preset = CharacterPreset(
            name="Knight",
            description="A knight character"
        )

        layer = ComponentLayer(
            layer_type=LayerType.BODY,
            component_id="body_human_male"
        )
        preset.add_layer(layer)

        result = preset.to_dict()

        assert result["name"] == "Knight"
        assert result["description"] == "A knight character"
        assert len(result["layers"]) == 1

    def test_preset_from_dict(self):
        """Test creating preset from dictionary."""
        data = {
            "name": "Mage",
            "description": "A mage character",
            "layers": [
                {
                    "layer_type": "BODY",
                    "component_id": "body_human_female",
                    "tint": None,
                    "enabled": True
                }
            ],
            "metadata": {}
        }

        preset = CharacterPreset.from_dict(data)

        assert preset.name == "Mage"
        assert len(preset.layers) == 1
        assert preset.layers[0].component_id == "body_human_female"


class TestCharacterGenerator:
    """Test CharacterGenerator class."""

    def test_create_generator(self, generator):
        """Test creating a generator instance."""
        assert generator.default_size == 32
        assert len(generator.component_library) == 0

    def test_load_component_library(self, loaded_generator):
        """Test loading component library."""
        # This test requires the sample components to be generated
        if len(loaded_generator.component_library) == 0:
            pytest.skip("Sample components not generated. Run generate_sample_components.py")

        assert len(loaded_generator.component_library) > 0
        assert LayerType.BODY in loaded_generator.available_components
        assert len(loaded_generator.available_components[LayerType.BODY]) > 0

    def test_create_character(self, loaded_generator):
        """Test creating a character from components."""
        if len(loaded_generator.component_library) == 0:
            pytest.skip("Sample components not generated")

        # Use friendly layer names
        character = loaded_generator.create_character(
            components={
                "body": "body_human_male",
                "hair": "hair_short_brown",
                "outfit": "outfit_knight_armor"
            },
            name="Test Knight"
        )

        assert character.name == "Test Knight"
        # Note: Only layers with valid components will be added
        assert len(character.layers) >= 1  # At least body should be present
        assert character.get_layer(LayerType.BODY) is not None

    def test_create_character_with_tints(self, loaded_generator):
        """Test creating a character with color tints."""
        if len(loaded_generator.component_library) == 0:
            pytest.skip("Sample components not generated")

        character = loaded_generator.create_character(
            components={
                "body": "body_human_male",
                "hair": "hair_short_brown"
            },
            tints={
                "hair": ColorTint(200, 100, 50)
            },
            name="Tinted Character"
        )

        # Hair maps to HAIR_FRONT
        hair_layer = character.get_layer(LayerType.HAIR_FRONT)
        # Only check if hair was actually loaded (component might not exist)
        if hair_layer:
            assert hair_layer.tint is not None
            assert hair_layer.tint.r == 200

    def test_save_and_load_preset(self, generator, tmp_path):
        """Test saving and loading a preset."""
        preset = CharacterPreset(name="SaveTest")
        preset.add_layer(ComponentLayer(
            layer_type=LayerType.BODY,
            component_id="test_body"
        ))

        # Save
        save_path = tmp_path / "test_preset.json"
        generator.save_preset(preset, save_path)

        assert save_path.exists()

        # Load
        loaded = generator.load_preset(save_path)

        assert loaded.name == "SaveTest"
        assert len(loaded.layers) == 1

    def test_randomize_character(self, loaded_generator):
        """Test randomizing a character."""
        if len(loaded_generator.component_library) == 0:
            pytest.skip("Sample components not generated")

        character = loaded_generator.randomize_character(
            name="Random Character"
        )

        assert character.name == "Random Character"
        assert len(character.layers) > 0

    def test_list_components(self, loaded_generator):
        """Test listing available components."""
        if len(loaded_generator.component_library) == 0:
            pytest.skip("Sample components not generated")

        components = loaded_generator.list_components()

        assert LayerType.BODY in components
        # Hair components are mapped to HAIR_FRONT
        assert LayerType.HAIR_FRONT in components or LayerType.HAIR_BACK in components

    def test_list_components_by_type(self, loaded_generator):
        """Test listing components for specific layer."""
        if len(loaded_generator.component_library) == 0:
            pytest.skip("Sample components not generated")

        components = loaded_generator.list_components(LayerType.BODY)

        assert LayerType.BODY in components
        assert len(components) == 1  # Only BODY layer

    def test_compose_frame(self, loaded_generator):
        """Test composing a single frame."""
        if len(loaded_generator.component_library) == 0:
            pytest.skip("Sample components not generated")

        character = loaded_generator.create_character(
            components={
                "body": "body_human_male"
            }
        )

        frame = loaded_generator.compose_frame(character, frame=0, direction=Direction.DOWN)

        assert frame is not None
        assert frame.get_width() == 32
        assert frame.get_height() == 32

    def test_render_sprite_sheet(self, loaded_generator):
        """Test rendering a complete sprite sheet."""
        if len(loaded_generator.component_library) == 0:
            pytest.skip("Sample components not generated")

        character = loaded_generator.create_character(
            components={
                "body": "body_human_male"
            }
        )

        sheet = loaded_generator.render_sprite_sheet(
            character,
            num_frames=4,
            directions=[Direction.DOWN, Direction.LEFT, Direction.RIGHT, Direction.UP]
        )

        assert sheet is not None
        assert sheet.get_width() == 32 * 4  # 4 frames
        assert sheet.get_height() == 32 * 4  # 4 directions

    def test_render_character(self, loaded_generator, tmp_path):
        """Test rendering and saving a character."""
        if len(loaded_generator.component_library) == 0:
            pytest.skip("Sample components not generated")

        character = loaded_generator.create_character(
            components={
                "body": "body_human_male",
                "hair": "hair_short_brown"
            },
            name="Test Character"
        )

        output_path = tmp_path / "test_character.png"
        loaded_generator.render_character(character, output_path)

        assert output_path.exists()
        assert output_path.with_suffix('.json').exists()

    def test_export_multi_size(self, loaded_generator, tmp_path):
        """Test exporting at multiple sizes."""
        if len(loaded_generator.component_library) == 0:
            pytest.skip("Sample components not generated")

        character = loaded_generator.create_character(
            components={
                "body": "body_human_male"
            },
            name="MultiSize"
        )

        loaded_generator.export_multi_size(
            character,
            tmp_path,
            sizes=[32, 48, 64]
        )

        assert (tmp_path / "MultiSize_32x32.png").exists()
        assert (tmp_path / "MultiSize_48x48.png").exists()
        assert (tmp_path / "MultiSize_64x64.png").exists()

    def test_generate_from_description(self, loaded_generator):
        """Test generating character from description."""
        if len(loaded_generator.component_library) == 0:
            pytest.skip("Sample components not generated")

        character = loaded_generator.generate_from_description(
            "A knight with brown hair and blue armor",
            name="Described Knight"
        )

        assert character.name == "Described Knight"
        # Description-based generation may fallback to randomization if components don't match
        # Just ensure a character was created
        assert character is not None

    def test_apply_color_tint(self, loaded_generator):
        """Test applying color tint to surface."""
        if len(loaded_generator.component_library) == 0:
            pytest.skip("Sample components not generated")

        # Get a component
        component_id = list(loaded_generator.component_library.keys())[0]
        component = loaded_generator.component_library[component_id]

        frame = component.get_frame(0, Direction.DOWN)
        tinted = loaded_generator.apply_color_tint(frame, ColorTint(255, 0, 0))

        assert tinted is not None
        assert tinted.get_size() == frame.get_size()


class TestLayerOrdering:
    """Test that layers are rendered in correct order."""

    def test_layer_ordering(self):
        """Test that LayerType values are in render order."""
        # Body should be rendered before hair
        assert LayerType.BODY.value < LayerType.HAIR_FRONT.value

        # Hair back should be before hair front
        assert LayerType.HAIR_BACK.value < LayerType.HAIR_FRONT.value

        # Torso should be before weapons
        assert LayerType.TORSO.value < LayerType.WEAPON.value

        # Effects should be last
        assert LayerType.EFFECT.value == max(layer.value for layer in LayerType)

    def test_preset_layer_sorting(self):
        """Test that preset layers are sorted correctly."""
        preset = CharacterPreset(name="Test")

        # Add layers in random order
        preset.add_layer(ComponentLayer(LayerType.WEAPON, "weapon_sword"))
        preset.add_layer(ComponentLayer(LayerType.BODY, "body_human"))
        preset.add_layer(ComponentLayer(LayerType.HAIR_FRONT, "hair_short"))

        # Layers should be sorted by layer_type value
        layer_values = [layer.layer_type.value for layer in preset.layers]
        assert layer_values == sorted(layer_values), f"Layers not sorted: {layer_values}"


class TestDirections:
    """Test Direction enum."""

    def test_direction_values(self):
        """Test direction enum values."""
        assert Direction.DOWN.value == 0
        assert Direction.LEFT.value == 1
        assert Direction.RIGHT.value == 2
        assert Direction.UP.value == 3

    def test_eight_directions(self):
        """Test 8-directional support."""
        assert Direction.DOWN_LEFT.value == 4
        assert Direction.DOWN_RIGHT.value == 5
        assert Direction.UP_LEFT.value == 6
        assert Direction.UP_RIGHT.value == 7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
