"""
AI-Powered Character Generator

Extends the base CharacterGenerator with AI-powered character creation.
Integrates with NeonWorks' AI configuration system for LLM support.

Features:
- Natural language character descriptions
- LLM-powered component selection (when available)
- Intelligent color palette generation
- Character archetype understanding
- Fallback to enhanced rule-based generation

Example:
    >>> ai_gen = AICharacterGenerator()
    >>> character = ai_gen.generate_from_ai_description(
    ...     "A wise elderly wizard with flowing white robes and a gnarled staff"
    ... )
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from neonworks.engine.tools.character_generator import (
    CharacterGenerator,
    CharacterPreset,
    ColorTint,
    ComponentLayer,
    LayerType,
)

# Try to import AI config (may not be available in all contexts)
try:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from config.ai_config import AIConfig, get_ai_config

    AI_CONFIG_AVAILABLE = True
except ImportError:
    AI_CONFIG_AVAILABLE = False
    AIConfig = None


class CharacterArchetype:
    """Common RPG character archetypes with component preferences."""

    ARCHETYPES = {
        "warrior": {
            "description": "Strong melee combatant",
            "preferred_layers": {
                "torso": ["armor", "knight"],
                "weapon": ["sword", "axe"],
            },
            "color_palette": {
                "outfit": ColorTint(150, 150, 180),  # Steel grey
                "weapon": ColorTint(200, 200, 210),  # Metallic
            },
        },
        "knight": {
            "description": "Noble armored warrior",
            "preferred_layers": {
                "torso": ["knight_armor", "armor"],
                "weapon": ["sword"],
            },
            "color_palette": {
                "outfit": ColorTint(100, 100, 200),  # Blue/silver
                "weapon": ColorTint(220, 220, 230),
            },
        },
        "mage": {
            "description": "Magic user with robes",
            "preferred_layers": {
                "torso": ["mage_robe", "robe"],
                "weapon": ["staff"],
            },
            "color_palette": {
                "outfit": ColorTint(100, 50, 150),  # Purple
                "weapon": ColorTint(139, 90, 43),  # Brown wood
            },
        },
        "wizard": {
            "description": "Powerful spellcaster",
            "preferred_layers": {
                "torso": ["mage_robe", "robe"],
                "weapon": ["staff"],
                "head": ["hat", "wizard_hat"],
            },
            "color_palette": {
                "outfit": ColorTint(50, 50, 150),  # Dark blue
                "weapon": ColorTint(150, 100, 50),
                "head": ColorTint(50, 50, 150),
            },
        },
        "ranger": {
            "description": "Skilled archer",
            "preferred_layers": {
                "torso": ["peasant_clothes", "leather"],
                "weapon": ["bow"],
            },
            "color_palette": {
                "outfit": ColorTint(100, 130, 80),  # Forest green
                "weapon": ColorTint(150, 100, 50),  # Brown wood
            },
        },
        "peasant": {
            "description": "Common folk",
            "preferred_layers": {
                "torso": ["peasant_clothes", "clothes"],
            },
            "color_palette": {
                "outfit": ColorTint(150, 120, 80),  # Tan/brown
            },
        },
        "elf": {
            "description": "Graceful elven being",
            "preferred_layers": {
                "body": ["elf"],
                "hair": ["long", "ponytail"],
            },
            "color_palette": {
                "hair": ColorTint(255, 230, 150),  # Golden blonde
                "body": ColorTint(255, 240, 220),  # Fair skin
            },
        },
    }


class AICharacterGenerator(CharacterGenerator):
    """
    AI-powered character generator.

    Extends CharacterGenerator with LLM-based character creation.
    Automatically detects available AI capabilities and falls back
    to enhanced rule-based generation when needed.
    """

    def __init__(self, default_size: int = 32):
        """
        Initialize AI character generator.

        Args:
            default_size: Default sprite size
        """
        super().__init__(default_size)

        # Check AI availability
        self.ai_config = None
        self.llm_available = False

        if AI_CONFIG_AVAILABLE:
            try:
                self.ai_config = get_ai_config(auto_detect=False)
                self.llm_available = self.ai_config.llm_enabled
                if self.llm_available:
                    print("✓ AI character generation enabled (LLM available)")
                else:
                    print("○ AI character generation using enhanced rules (no LLM)")
            except Exception as e:
                print(f"○ AI config unavailable: {e}")
                self.llm_available = False
        else:
            print("○ AI character generation using enhanced rules (AI config not available)")

    def generate_from_ai_description(
        self, description: str, name: Optional[str] = None
    ) -> CharacterPreset:
        """
        Generate character from natural language description using AI.

        This method tries multiple approaches:
        1. LLM-based generation (if available)
        2. Archetype matching with NLP
        3. Enhanced keyword matching
        4. Fallback to randomization

        Args:
            description: Natural language character description
            name: Character name (auto-generated if None)

        Returns:
            Generated character preset

        Example:
            >>> char = ai_gen.generate_from_ai_description(
            ...     "A brave knight with brown hair and shining blue armor"
            ... )
        """
        print(f"\n🤖 AI Character Generator: {description}")

        # Try LLM generation if available
        if self.llm_available:
            try:
                return self._generate_with_llm(description, name)
            except Exception as e:
                print(f"  ⚠ LLM generation failed: {e}, falling back to rules")

        # Fallback to enhanced rule-based generation
        return self._generate_with_rules(description, name)

    def _generate_with_llm(self, description: str, name: Optional[str] = None) -> CharacterPreset:
        """
        Generate character using LLM.

        Note: This requires llama-cpp-python or similar LLM library.
        Currently serves as a template for integration.

        Args:
            description: Character description
            name: Character name

        Returns:
            Character preset
        """
        print("  → Using LLM generation")

        # Build context for LLM
        available_components = self.list_components()
        component_list = self._format_components_for_llm(available_components)

        # Create prompt for LLM
        prompt = f"""You are a character designer for an RPG game. Based on the description, select appropriate sprite components and colors.

Description: "{description}"

Available components:
{component_list}

Respond ONLY with valid JSON in this exact format:
{{
    "name": "Character Name",
    "components": {{
        "body": "component_id",
        "hair": "component_id",
        "outfit": "component_id",
        "weapon": "component_id"
    }},
    "tints": {{
        "hair": {{"r": 139, "g": 90, "b": 43}},
        "outfit": {{"r": 100, "g": 100, "b": 200}}
    }}
}}

Use only component IDs from the available list above. Choose colors that match the description.
"""

        try:
            # Call LLM (this would require llama-cpp-python or similar)
            # For now, this is a placeholder showing the integration point
            llm_response = self._call_llm(prompt)

            # Parse LLM response
            config = self._parse_llm_response(llm_response)

            # Create character from LLM selections
            components = config.get("components", {})
            tints_data = config.get("tints", {})
            tints = {k: ColorTint(**v) for k, v in tints_data.items()}
            char_name = name or config.get("name", "AI Character")

            return self.create_character(components, tints, char_name)

        except Exception as e:
            print(f"  ⚠ LLM call failed: {e}")
            raise

    def _call_llm(self, prompt: str) -> str:
        """
        Call LLM with prompt.

        This is the integration point for actual LLM calls.
        Can be extended to support:
        - llama-cpp-python
        - OpenAI API
        - Anthropic API
        - Local transformers

        Args:
            prompt: LLM prompt

        Returns:
            LLM response text

        Raises:
            NotImplementedError: If LLM library not available
        """
        # Try llama-cpp-python
        try:
            from llama_cpp import Llama

            if not self.ai_config or not self.ai_config.llm_model_path:
                raise ValueError("No LLM model path configured")

            llm = Llama(
                model_path=self.ai_config.llm_model_path,
                n_ctx=self.ai_config.llm_n_ctx,
                n_threads=self.ai_config.llm_n_threads,
                n_gpu_layers=self.ai_config.llm_n_gpu_layers,
            )

            output = llm(
                prompt, max_tokens=512, temperature=0.7, stop=["```", "\n\n\n"], echo=False
            )

            return output["choices"][0]["text"]

        except ImportError:
            # Fallback: Try OpenAI API
            try:
                import openai

                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=512,
                    temperature=0.7,
                )

                return response.choices[0].message.content

            except ImportError:
                raise NotImplementedError(
                    "No LLM library available. Install llama-cpp-python or openai:\n"
                    "  pip install llama-cpp-python\n"
                    "  OR\n"
                    "  pip install openai"
                )

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM JSON response.

        Handles common LLM output issues:
        - Markdown code blocks
        - Extra text before/after JSON
        - Malformed JSON

        Args:
            response: Raw LLM response

        Returns:
            Parsed configuration dict
        """
        # Remove markdown code blocks
        response = re.sub(r"```json\s*", "", response)
        response = re.sub(r"```\s*", "", response)

        # Try to find JSON in response (match nested braces)
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            response = json_match.group(0)

        # Strip whitespace
        response = response.strip()

        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            print(f"  ⚠ Failed to parse LLM JSON: {e}")
            print(f"  Response was: {response[:200]}")
            raise

    def _format_components_for_llm(self, components: Dict[LayerType, List[str]]) -> str:
        """
        Format component list for LLM prompt.

        Args:
            components: Available components by layer

        Returns:
            Formatted string for LLM
        """
        lines = []
        for layer_type, component_list in components.items():
            if component_list:
                layer_name = layer_type.name.lower()
                comp_ids = ", ".join(component_list)
                lines.append(f"  {layer_name}: {comp_ids}")

        return "\n".join(lines)

    def _generate_with_rules(self, description: str, name: Optional[str] = None) -> CharacterPreset:
        """
        Generate character using enhanced rule-based matching.

        Uses:
        - Archetype detection
        - Keyword matching
        - Color inference
        - Component preferences

        Args:
            description: Character description
            name: Character name

        Returns:
            Character preset
        """
        print("  → Using enhanced rule-based generation")

        desc_lower = description.lower()
        components = {}
        tints = {}

        # Detect archetype
        archetype = self._detect_archetype(desc_lower)
        if archetype:
            print(f"  → Detected archetype: {archetype}")
            arch_data = CharacterArchetype.ARCHETYPES[archetype]

            # Apply archetype preferences
            for layer, preferred in arch_data["preferred_layers"].items():
                component = self._find_matching_component(layer, preferred)
                if component:
                    components[layer] = component

            # Apply archetype colors
            tints.update(arch_data.get("color_palette", {}))

        # Enhanced keyword matching for body type
        if "elf" in desc_lower or "elven" in desc_lower:
            components["body"] = self._find_best_match("body", ["elf"])
        elif "human" in desc_lower or "man" in desc_lower or "woman" in desc_lower:
            if "female" in desc_lower or "woman" in desc_lower:
                components["body"] = self._find_best_match("body", ["female", "human"])
            else:
                components["body"] = self._find_best_match("body", ["male", "human"])

        # Enhanced hair matching with colors
        hair_match, hair_color = self._extract_hair_info(desc_lower)
        if hair_match:
            components["hair"] = hair_match
            if hair_color:
                tints["hair"] = hair_color

        # Enhanced outfit matching
        outfit_keywords = {
            "armor": ["armor", "knight"],
            "robe": ["robe", "mage"],
            "clothes": ["clothes", "peasant", "simple"],
        }

        for outfit_type, keywords in outfit_keywords.items():
            if any(kw in desc_lower for kw in keywords):
                match = self._find_best_match("outfit", [outfit_type])
                if match:
                    components["outfit"] = match
                    # Infer armor color from description
                    color = self._extract_color(desc_lower, "armor")
                    if color:
                        tints["outfit"] = color
                break

        # Enhanced weapon matching
        weapon_keywords = ["sword", "staff", "bow", "axe", "dagger"]
        for weapon in weapon_keywords:
            if weapon in desc_lower:
                match = self._find_best_match("weapon", [weapon])
                if match:
                    components["weapon"] = match
                break

        # If no components matched, use randomization
        if not components:
            print("  → No matches found, using randomization")
            return self.randomize_character(name=name or "Random Character")

        # Generate character name if not provided
        if not name:
            name = self._generate_name_from_description(description)

        print(f"  → Selected components: {list(components.keys())}")
        return self.create_character(components, tints, name)

    def _detect_archetype(self, description: str) -> Optional[str]:
        """Detect character archetype from description."""
        for archetype, data in CharacterArchetype.ARCHETYPES.items():
            if archetype in description:
                return archetype

        # Check description words
        for archetype, data in CharacterArchetype.ARCHETYPES.items():
            desc_words = data["description"].lower().split()
            if any(word in description for word in desc_words):
                return archetype

        return None

    def _find_matching_component(self, layer: str, preferred: List[str]) -> Optional[str]:
        """Find best matching component for layer."""
        # Try friendly name first
        friendly_map = {
            "hair": LayerType.HAIR_FRONT,
            "outfit": LayerType.TORSO,
            "armor": LayerType.TORSO,
            "clothes": LayerType.TORSO,
            "helmet": LayerType.HEAD,
            "hat": LayerType.HEAD,
        }

        layer_type = friendly_map.get(layer.lower())
        if not layer_type:
            # Try exact LayerType name
            try:
                layer_type = LayerType[layer.upper()]
            except KeyError:
                return None

        available = self.available_components.get(layer_type, [])

        for pref in preferred:
            for comp in available:
                if pref in comp.lower():
                    return comp

        return available[0] if available else None

    def _find_best_match(self, layer: str, keywords: List[str]) -> Optional[str]:
        """Find best component match for keywords."""
        return self._find_matching_component(layer, keywords)

    def _extract_hair_info(self, description: str) -> Tuple[Optional[str], Optional[ColorTint]]:
        """Extract hair style and color from description."""
        hair_component = None
        hair_color = None

        # Hair styles
        if "long" in description:
            hair_component = self._find_best_match("hair", ["long"])
        elif "short" in description:
            hair_component = self._find_best_match("hair", ["short"])
        elif "ponytail" in description:
            hair_component = self._find_best_match("hair", ["ponytail"])

        # Hair colors
        color_map = {
            "brown": ColorTint(139, 90, 43),
            "blonde": ColorTint(255, 230, 150),
            "blond": ColorTint(255, 230, 150),
            "red": ColorTint(200, 80, 60),
            "black": ColorTint(30, 30, 30),
            "white": ColorTint(240, 240, 240),
            "grey": ColorTint(150, 150, 150),
            "gray": ColorTint(150, 150, 150),
        }

        for color_name, tint in color_map.items():
            if f"{color_name} hair" in description:
                hair_color = tint
                break

        return hair_component, hair_color

    def _extract_color(self, description: str, item: str) -> Optional[ColorTint]:
        """Extract color for specific item from description."""
        color_map = {
            "blue": ColorTint(100, 100, 200),
            "red": ColorTint(200, 80, 80),
            "green": ColorTint(80, 200, 80),
            "purple": ColorTint(150, 80, 200),
            "gold": ColorTint(200, 180, 80),
            "silver": ColorTint(200, 200, 220),
            "black": ColorTint(50, 50, 50),
            "white": ColorTint(240, 240, 240),
        }

        # Look for "blue armor", "red robe", etc.
        for color_name, tint in color_map.items():
            if f"{color_name} {item}" in description:
                return tint

        return None

    def _generate_name_from_description(self, description: str) -> str:
        """Generate character name from description."""
        # Look for titles/descriptors
        if "knight" in description.lower():
            return "Noble Knight"
        elif "wizard" in description.lower() or "mage" in description.lower():
            return "Wise Mage"
        elif "warrior" in description.lower():
            return "Brave Warrior"
        elif "ranger" in description.lower():
            return "Swift Ranger"
        elif "elf" in description.lower():
            return "Elven Wanderer"
        else:
            return "Generated Character"


# Convenience function
def generate_ai_character(
    description: str,
    output_path: Optional[str] = None,
    library_path: str = "assets/character_components/",
    size: int = 32,
) -> CharacterPreset:
    """
    Quick AI character generation from description.

    Args:
        description: Natural language character description
        output_path: Where to save sprite sheet (optional)
        library_path: Component library path
        size: Output size

    Returns:
        Generated character preset

    Example:
        >>> char = generate_ai_character(
        ...     "A mysterious wizard with flowing purple robes",
        ...     "output/wizard.png"
        ... )
    """
    gen = AICharacterGenerator(default_size=size)
    gen.load_component_library(library_path)

    character = gen.generate_from_ai_description(description)

    if output_path:
        gen.render_character(character, output_path)

    return character


if __name__ == "__main__":
    print("AI Character Generator - Example\n")

    gen = AICharacterGenerator(default_size=32)

    # Show configuration
    print(f"LLM Available: {gen.llm_available}")

    print("\nExample character descriptions:")
    print("1. 'A brave knight with brown hair and shining blue armor'")
    print("2. 'An elderly wizard with white hair and flowing purple robes'")
    print("3. 'A skilled elven ranger with a longbow'")
    print("4. 'A peasant farmer with simple clothes'")

    print("\nAI Character Generator ready!")
    print("Load component library and call generate_from_ai_description()")
