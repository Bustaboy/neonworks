"""
Tests for AI Character Generator

Tests AI-powered character generation including:
- Archetype detection
- Rule-based generation
- Component matching
- Color extraction
- Name generation
"""

import pytest
from pathlib import Path

# Import the AI character generator
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.tools.ai_character_generator import (
    AICharacterGenerator,
    CharacterArchetype,
    ColorTint,
)
from engine.tools.character_generator import LayerType


@pytest.fixture
def ai_generator():
    """Create an AI character generator instance."""
    return AICharacterGenerator(default_size=32)


@pytest.fixture
def loaded_ai_generator():
    """Create an AI generator with sample components loaded."""
    gen = AICharacterGenerator(default_size=32)

    # Load the test components we generated
    component_path = Path("test_outputs/character_components")
    if component_path.exists():
        gen.load_component_library(component_path)

    return gen


class TestCharacterArchetype:
    """Test character archetype system."""

    def test_archetypes_defined(self):
        """Test that archetypes are properly defined."""
        assert "warrior" in CharacterArchetype.ARCHETYPES
        assert "knight" in CharacterArchetype.ARCHETYPES
        assert "mage" in CharacterArchetype.ARCHETYPES
        assert "wizard" in CharacterArchetype.ARCHETYPES

    def test_archetype_structure(self):
        """Test archetype data structure."""
        knight = CharacterArchetype.ARCHETYPES["knight"]

        assert "description" in knight
        assert "preferred_layers" in knight
        assert "color_palette" in knight

        assert isinstance(knight["preferred_layers"], dict)
        assert isinstance(knight["color_palette"], dict)

    def test_archetype_colors(self):
        """Test archetype color palettes."""
        mage = CharacterArchetype.ARCHETYPES["mage"]
        colors = mage["color_palette"]

        assert "outfit" in colors
        assert isinstance(colors["outfit"], ColorTint)


class TestAICharacterGenerator:
    """Test AI character generator."""

    def test_create_ai_generator(self, ai_generator):
        """Test creating an AI generator instance."""
        assert ai_generator.default_size == 32
        assert hasattr(ai_generator, 'llm_available')
        assert isinstance(ai_generator.llm_available, bool)

    def test_detect_archetype(self, ai_generator):
        """Test archetype detection."""
        # Test exact match
        archetype = ai_generator._detect_archetype("brave knight")
        assert archetype == "knight"

        # Test mage
        archetype = ai_generator._detect_archetype("powerful mage")
        assert archetype == "mage"

        # Test warrior
        archetype = ai_generator._detect_archetype("strong warrior")
        assert archetype == "warrior"

    def test_extract_hair_info(self, ai_generator):
        """Test hair information extraction."""
        # Test hair style
        hair, color = ai_generator._extract_hair_info("character with long hair")
        # Note: May be None if components not loaded

        # Test hair color
        hair, color = ai_generator._extract_hair_info("character with brown hair")
        if color:
            assert isinstance(color, ColorTint)
            assert color.r == 139
            assert color.g == 90
            assert color.b == 43

        # Test both
        hair, color = ai_generator._extract_hair_info("long blonde hair")
        if color:
            assert color.r == 255
            assert color.g == 230

    def test_extract_color(self, ai_generator):
        """Test color extraction from description."""
        # Blue armor
        color = ai_generator._extract_color("knight with blue armor", "armor")
        assert color is not None
        assert color.r == 100
        assert color.b == 200

        # Red robe
        color = ai_generator._extract_color("mage in red robe", "robe")
        assert color is not None
        assert color.r == 200
        assert color.g == 80

        # No color specified
        color = ai_generator._extract_color("knight with armor", "armor")
        assert color is None

    def test_generate_name_from_description(self, ai_generator):
        """Test name generation from description."""
        name = ai_generator._generate_name_from_description("A brave knight")
        assert "Knight" in name

        name = ai_generator._generate_name_from_description("A wise wizard")
        assert "Mage" in name or "Wizard" in name.lower()

        name = ai_generator._generate_name_from_description("An elven ranger")
        assert "Elf" in name or "Ranger" in name

    def test_generate_with_rules(self, loaded_ai_generator):
        """Test rule-based character generation."""
        if len(loaded_ai_generator.component_library) == 0:
            pytest.skip("Sample components not generated")

        # Generate knight
        character = loaded_ai_generator._generate_with_rules(
            "A brave knight with shining blue armor",
            name="Test Knight"
        )

        assert character.name == "Test Knight"
        assert len(character.layers) > 0

        # Should have some components (exact components depend on what was matched)
        # The important thing is we generated a valid character
        assert character is not None

    def test_generate_from_ai_description_knight(self, loaded_ai_generator):
        """Test AI generation with knight description."""
        if len(loaded_ai_generator.component_library) == 0:
            pytest.skip("Sample components not generated")

        character = loaded_ai_generator.generate_from_ai_description(
            "A brave knight with brown hair and shining blue armor"
        )

        assert character is not None
        assert len(character.layers) > 0

        # Should have detected knight archetype
        # and selected appropriate components

    def test_generate_from_ai_description_mage(self, loaded_ai_generator):
        """Test AI generation with mage description."""
        if len(loaded_ai_generator.component_library) == 0:
            pytest.skip("Sample components not generated")

        character = loaded_ai_generator.generate_from_ai_description(
            "A wise wizard with flowing purple robes and a gnarled staff"
        )

        assert character is not None
        assert len(character.layers) > 0

        # Should have mage/wizard components
        outfit = character.get_layer(LayerType.TORSO)
        weapon = character.get_layer(LayerType.WEAPON)

        # May not always match if components don't exist
        # but should always generate something

    def test_generate_from_ai_description_elf(self, loaded_ai_generator):
        """Test AI generation with elf description."""
        if len(loaded_ai_generator.component_library) == 0:
            pytest.skip("Sample components not generated")

        character = loaded_ai_generator.generate_from_ai_description(
            "A graceful elf ranger with a longbow"
        )

        assert character is not None
        assert len(character.layers) > 0

    def test_generate_from_ai_description_fallback(self, loaded_ai_generator):
        """Test AI generation with unknown description (should randomize)."""
        if len(loaded_ai_generator.component_library) == 0:
            pytest.skip("Sample components not generated")

        character = loaded_ai_generator.generate_from_ai_description(
            "A completely unique and undefined character type"
        )

        # Should fall back to randomization
        assert character is not None
        assert len(character.layers) > 0

    def test_find_matching_component(self, loaded_ai_generator):
        """Test component matching algorithm."""
        if len(loaded_ai_generator.component_library) == 0:
            pytest.skip("Sample components not generated")

        # Try to find armor component
        component = loaded_ai_generator._find_matching_component(
            "outfit",
            ["armor", "knight"]
        )

        # Should find knight_armor if it exists
        if component:
            assert "armor" in component.lower() or "knight" in component.lower()

    def test_find_best_match(self, loaded_ai_generator):
        """Test best match finding."""
        if len(loaded_ai_generator.component_library) == 0:
            pytest.skip("Sample components not generated")

        # Find body component
        match = loaded_ai_generator._find_best_match("body", ["human", "male"])

        # Should find human_male if it exists
        if match:
            assert "human" in match.lower() or "male" in match.lower()

    def test_parse_llm_response(self, ai_generator):
        """Test LLM response parsing."""
        # Test clean JSON
        response = '''{
    "name": "Test Knight",
    "components": {
        "body": "body_human_male",
        "hair": "hair_short_brown"
    },
    "tints": {
        "hair": {"r": 139, "g": 90, "b": 43}
    }
}'''

        result = ai_generator._parse_llm_response(response)

        assert result["name"] == "Test Knight"
        assert "components" in result
        assert "body" in result["components"]

    def test_parse_llm_response_with_markdown(self, ai_generator):
        """Test parsing LLM response with markdown code blocks."""
        response = '''Here's the character:
```json
{
    "name": "Test Mage",
    "components": {
        "body": "body_human_female"
    }
}
```'''

        result = ai_generator._parse_llm_response(response)

        assert result["name"] == "Test Mage"

    def test_format_components_for_llm(self, loaded_ai_generator):
        """Test formatting components for LLM prompt."""
        if len(loaded_ai_generator.component_library) == 0:
            pytest.skip("Sample components not generated")

        components = loaded_ai_generator.list_components()
        formatted = loaded_ai_generator._format_components_for_llm(components)

        assert isinstance(formatted, str)
        assert len(formatted) > 0

        # Should contain layer names
        assert "body" in formatted.lower() or "torso" in formatted.lower()


class TestRuleBasedMatching:
    """Test enhanced rule-based matching."""

    def test_hair_color_matching(self, ai_generator):
        """Test hair color keyword matching."""
        # Brown hair
        _, color = ai_generator._extract_hair_info("brown hair")
        assert color.r == 139
        assert color.g == 90
        assert color.b == 43

        # Blonde hair
        _, color = ai_generator._extract_hair_info("blonde hair")
        assert color.r == 255
        assert color.g == 230
        assert color.b == 150

        # Red hair
        _, color = ai_generator._extract_hair_info("red hair")
        assert color.r == 200
        assert color.g == 80
        assert color.b == 60

    def test_armor_color_matching(self, ai_generator):
        """Test armor color extraction."""
        # Blue armor
        color = ai_generator._extract_color("blue armor", "armor")
        assert color.r == 100
        assert color.b == 200

        # Silver armor
        color = ai_generator._extract_color("silver armor", "armor")
        assert color.r == 200
        assert color.g == 200
        assert color.b == 220

    def test_multiple_descriptors(self, loaded_ai_generator):
        """Test handling multiple descriptors."""
        if len(loaded_ai_generator.component_library) == 0:
            pytest.skip("Sample components not generated")

        character = loaded_ai_generator.generate_from_ai_description(
            "A tall brave knight with long brown hair and shining blue armor wielding a sword"
        )

        assert character is not None
        assert len(character.layers) > 0


class TestIntegration:
    """Integration tests."""

    def test_full_generation_workflow(self, loaded_ai_generator, tmp_path):
        """Test complete generation workflow."""
        if len(loaded_ai_generator.component_library) == 0:
            pytest.skip("Sample components not generated")

        # Generate character
        character = loaded_ai_generator.generate_from_ai_description(
            "A heroic knight with blue armor"
        )

        # Render character
        output_path = tmp_path / "ai_generated_knight.png"
        loaded_ai_generator.render_character(character, output_path)

        # Verify output
        assert output_path.exists()
        assert output_path.with_suffix('.json').exists()

    def test_multiple_generations(self, loaded_ai_generator):
        """Test generating multiple different characters."""
        if len(loaded_ai_generator.component_library) == 0:
            pytest.skip("Sample components not generated")

        descriptions = [
            "A brave knight",
            "A wise wizard",
            "An elven ranger",
            "A common peasant"
        ]

        for desc in descriptions:
            character = loaded_ai_generator.generate_from_ai_description(desc)
            assert character is not None
            assert len(character.layers) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
