"""
AI Animation Interpreter

Uses LLM to interpret natural language animation requests and convert them
into structured animation parameters that the AI animator can execute.
"""

import json
import re
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple

from neonworks.editor.ai_animator import AnimationConfig


@dataclass
class AnimationIntent:
    """Parsed animation intent from user request"""

    animation_type: str  # Base animation (walk, run, attack, etc.)
    style_modifiers: List[str]  # Style descriptors (sneaky, aggressive, tired, etc.)
    intensity: float  # 0.0 to 1.0
    speed_multiplier: float  # Speed adjustment
    special_effects: List[str]  # Special effects to apply
    frame_count: Optional[int] = None  # Override default frame count
    confidence: float = 1.0  # How confident the interpretation is


class AnimationInterpreter:
    """
    Interprets natural language animation requests using LLM.

    This class acts as the "brain" that understands what the user wants
    and translates it into parameters the animation generator can use.
    """

    def __init__(self, model_type: str = "local"):
        """
        Initialize animation interpreter.

        Args:
            model_type: 'local' for local LLM, 'api' for cloud API, 'hybrid'
        """
        self.model_type = model_type

        # Animation keyword mappings
        self.animation_keywords = {
            # Movement
            "walk": ["walk", "walking", "stroll", "pace"],
            "run": ["run", "running", "sprint", "dash", "jog"],
            "idle": ["idle", "stand", "standing", "wait", "rest"],
            "jump": ["jump", "jumping", "leap", "hop", "bounce"],
            # Combat
            "attack": [
                "attack",
                "attacking",
                "strike",
                "hit",
                "slash",
                "swing",
                "punch",
            ],
            "cast_spell": [
                "cast",
                "casting",
                "spell",
                "magic",
                "conjure",
                "summon",
            ],
            "hurt": ["hurt", "hit", "damage", "injured", "wounded"],
            "death": ["death", "die", "dying", "dead", "collapse", "fall"],
        }

        # Style modifiers that affect animation parameters
        self.style_modifiers = {
            # Speed related
            "slow": {"speed_multiplier": 0.5, "intensity": 0.4},
            "fast": {"speed_multiplier": 1.5, "intensity": 0.9},
            "quick": {"speed_multiplier": 1.3, "intensity": 0.8},
            "sluggish": {"speed_multiplier": 0.6, "intensity": 0.3},
            # Energy related
            "tired": {"intensity": 0.4, "style": "smooth"},
            "energetic": {"intensity": 0.9, "style": "bouncy"},
            "weak": {"intensity": 0.3, "style": "smooth"},
            "powerful": {"intensity": 1.0, "style": "snappy"},
            "aggressive": {"intensity": 1.0, "speed_multiplier": 1.2},
            # Style related
            "sneaky": {"intensity": 0.5, "style": "smooth", "speed_multiplier": 0.8},
            "confident": {"intensity": 0.7, "style": "smooth"},
            "scared": {"intensity": 0.6, "style": "snappy", "speed_multiplier": 1.3},
            "happy": {"intensity": 0.8, "style": "bouncy"},
            "sad": {"intensity": 0.4, "style": "smooth", "speed_multiplier": 0.7},
            "angry": {"intensity": 0.9, "style": "snappy"},
            "calm": {"intensity": 0.5, "style": "smooth"},
            # Movement style
            "smooth": {"style": "smooth"},
            "snappy": {"style": "snappy"},
            "bouncy": {"style": "bouncy"},
            "fluid": {"style": "smooth", "intensity": 0.7},
            "jerky": {"style": "snappy", "intensity": 0.8},
        }

        # TODO: Initialize LLM model
        # Options:
        # 1. Local: GPT4All, Llama.cpp, ONNX models
        # 2. API: OpenAI, Anthropic, Cohere
        # 3. Hybrid: Simple queries local, complex queries API

    def interpret_request(
        self, user_request: str, context: Optional[Dict] = None
    ) -> AnimationIntent:
        """
        Interpret natural language animation request.

        Args:
            user_request: User's description of desired animation
            context: Optional context (sprite type, current animations, etc.)

        Returns:
            AnimationIntent with parsed parameters

        Examples:
            "Make the character walk slowly like they're tired"
            -> AnimationIntent(animation_type="walk", style_modifiers=["slow", "tired"],
                              intensity=0.4, speed_multiplier=0.5)

            "Create an aggressive attack animation"
            -> AnimationIntent(animation_type="attack", style_modifiers=["aggressive"],
                              intensity=1.0, speed_multiplier=1.2)
        """
        print(f"[Interpreter] Processing request: '{user_request}'")

        if self.model_type == "local":
            return self._interpret_local(user_request, context)
        elif self.model_type == "api":
            return self._interpret_api(user_request, context)
        else:  # hybrid
            return self._interpret_hybrid(user_request, context)

    def _interpret_local(
        self, user_request: str, context: Optional[Dict] = None
    ) -> AnimationIntent:
        """
        Interpret using local pattern matching and heuristics.

        This is a rule-based fallback that works without an LLM.
        It's fast but less flexible than true LLM understanding.
        """
        user_request_lower = user_request.lower()

        # 1. Identify base animation type
        animation_type = self._identify_animation_type(user_request_lower)

        # 2. Extract style modifiers
        style_modifiers = self._extract_style_modifiers(user_request_lower)

        # 3. Calculate derived parameters
        intensity, speed_multiplier, style = self._calculate_parameters(
            style_modifiers
        )

        # 4. Detect special effects
        special_effects = self._detect_special_effects(user_request_lower)

        # 5. Extract frame count if specified
        frame_count = self._extract_frame_count(user_request_lower)

        intent = AnimationIntent(
            animation_type=animation_type,
            style_modifiers=style_modifiers,
            intensity=intensity,
            speed_multiplier=speed_multiplier,
            special_effects=special_effects,
            frame_count=frame_count,
            confidence=0.8,  # Rule-based has moderate confidence
        )

        print(f"[Interpreter] Parsed intent: {intent}")
        return intent

    def _interpret_api(
        self, user_request: str, context: Optional[Dict] = None
    ) -> AnimationIntent:
        """
        Interpret using LLM API (OpenAI, Anthropic, etc.).

        TODO: Implement LLM API integration
        - Send request to LLM with structured prompt
        - Parse JSON response into AnimationIntent
        - Handle API errors gracefully
        """
        # Construct LLM prompt
        prompt = self._build_llm_prompt(user_request, context)

        # TODO: Call LLM API
        # response = call_llm_api(prompt)
        # intent = self._parse_llm_response(response)

        # For now, fallback to local interpretation
        return self._interpret_local(user_request, context)

    def _interpret_hybrid(
        self, user_request: str, context: Optional[Dict] = None
    ) -> AnimationIntent:
        """
        Use local interpretation for simple requests, API for complex ones.
        """
        # Check if request is simple (single animation type, no modifiers)
        is_simple = self._is_simple_request(user_request)

        if is_simple:
            return self._interpret_local(user_request, context)
        else:
            return self._interpret_api(user_request, context)

    def _identify_animation_type(self, text: str) -> str:
        """Identify base animation type from text"""
        for anim_type, keywords in self.animation_keywords.items():
            if any(keyword in text for keyword in keywords):
                return anim_type

        # Default to idle if no match
        return "idle"

    def _extract_style_modifiers(self, text: str) -> List[str]:
        """Extract style modifier words from text"""
        found_modifiers = []

        for modifier in self.style_modifiers.keys():
            if modifier in text:
                found_modifiers.append(modifier)

        return found_modifiers

    def _calculate_parameters(
        self, style_modifiers: List[str]
    ) -> Tuple[float, float, str]:
        """
        Calculate animation parameters from style modifiers.

        Returns:
            (intensity, speed_multiplier, style)
        """
        # Start with defaults
        intensity = 0.7
        speed_multiplier = 1.0
        style = "smooth"

        # Apply modifiers
        for modifier in style_modifiers:
            if modifier in self.style_modifiers:
                params = self.style_modifiers[modifier]

                if "intensity" in params:
                    intensity = params["intensity"]
                if "speed_multiplier" in params:
                    speed_multiplier *= params["speed_multiplier"]
                if "style" in params:
                    style = params["style"]

        # Clamp values
        intensity = max(0.0, min(1.0, intensity))
        speed_multiplier = max(0.1, min(3.0, speed_multiplier))

        return intensity, speed_multiplier, style

    def _detect_special_effects(self, text: str) -> List[str]:
        """Detect special effects mentioned in text"""
        effects = []

        effect_keywords = {
            "glow": ["glow", "glowing", "shine", "shining"],
            "blur": ["blur", "motion blur", "trail"],
            "flash": ["flash", "flashing", "blink"],
            "shake": ["shake", "shaking", "tremble"],
            "fade": ["fade", "fading", "disappear"],
            "particles": ["particles", "sparkles", "stars", "dust"],
        }

        for effect, keywords in effect_keywords.items():
            if any(keyword in text for keyword in keywords):
                effects.append(effect)

        return effects

    def _extract_frame_count(self, text: str) -> Optional[int]:
        """Extract frame count from text if specified"""
        # Look for patterns like "4 frames", "8 frame", "with 6 frames"
        pattern = r"(\d+)\s*frames?"
        match = re.search(pattern, text)

        if match:
            return int(match.group(1))

        return None

    def _is_simple_request(self, text: str) -> bool:
        """Check if request is simple enough for local processing"""
        # Simple if: single animation type, <= 2 modifiers, < 20 words
        word_count = len(text.split())
        modifier_count = sum(
            1 for mod in self.style_modifiers.keys() if mod in text.lower()
        )

        return word_count < 20 and modifier_count <= 2

    def _build_llm_prompt(
        self, user_request: str, context: Optional[Dict] = None
    ) -> str:
        """
        Build structured prompt for LLM.

        Returns a prompt that asks the LLM to return JSON with animation parameters.
        """
        prompt = f"""You are an animation specialist AI. Parse the user's animation request and return structured parameters.

User Request: "{user_request}"

Available animation types: {', '.join(self.animation_keywords.keys())}

Respond with JSON in this exact format:
{{
    "animation_type": "walk",  // One of the available types
    "style_modifiers": ["slow", "tired"],  // Descriptive style words
    "intensity": 0.5,  // 0.0 to 1.0, how pronounced the animation is
    "speed_multiplier": 0.8,  // Speed adjustment (1.0 is normal)
    "special_effects": ["blur"],  // Any special effects to apply
    "frame_count": 6,  // Number of frames (null for default)
    "confidence": 0.95  // How confident you are in this interpretation
}}

Consider the mood, energy level, and style implied by the user's words.
"""

        if context:
            prompt += f"\n\nAdditional Context:\n{json.dumps(context, indent=2)}"

        return prompt

    def _parse_llm_response(self, response: str) -> AnimationIntent:
        """Parse LLM JSON response into AnimationIntent"""
        try:
            data = json.loads(response)
            return AnimationIntent(**data)
        except (json.JSONDecodeError, TypeError) as e:
            print(f"[Interpreter] Error parsing LLM response: {e}")
            # Fallback to default
            return AnimationIntent(
                animation_type="idle",
                style_modifiers=[],
                intensity=0.7,
                speed_multiplier=1.0,
                special_effects=[],
                confidence=0.3,
            )

    def suggest_animations(self, sprite_info: Dict) -> List[Tuple[str, str]]:
        """
        Suggest appropriate animations based on sprite characteristics.

        Args:
            sprite_info: Dictionary with sprite metadata (type, class, etc.)

        Returns:
            List of (animation_name, description) tuples
        """
        suggestions = []

        sprite_type = sprite_info.get("type", "character")
        sprite_class = sprite_info.get("class", "warrior")

        # Base suggestions for all sprites
        suggestions.extend(
            [
                ("idle", "Standing idle animation"),
                ("walk", "Basic walking cycle"),
            ]
        )

        # Class-specific suggestions
        if sprite_class in ["warrior", "knight", "fighter"]:
            suggestions.extend(
                [
                    ("aggressive attack", "Powerful melee strike"),
                    ("defensive idle", "Ready stance with shield"),
                    ("run", "Combat charge"),
                ]
            )
        elif sprite_class in ["mage", "wizard", "sorcerer"]:
            suggestions.extend(
                [
                    ("cast spell", "Spellcasting animation"),
                    ("slow walk", "Mystical, flowing walk"),
                    ("idle with glow", "Standing with magical aura"),
                ]
            )
        elif sprite_class in ["rogue", "thief", "assassin"]:
            suggestions.extend(
                [
                    ("sneaky walk", "Stealthy movement"),
                    ("quick attack", "Fast strike animation"),
                    ("dodge", "Evasive movement"),
                ]
            )

        # Type-specific suggestions
        if sprite_type == "enemy":
            suggestions.append(("death", "Defeat animation"))
        elif sprite_type == "npc":
            suggestions.append(("wave", "Greeting animation"))

        return suggestions

    def refine_intent(
        self, intent: AnimationIntent, user_feedback: str
    ) -> AnimationIntent:
        """
        Refine animation intent based on user feedback.

        Args:
            intent: Original intent
            user_feedback: User's refinement request ("make it slower", "more intense", etc.)

        Returns:
            Refined AnimationIntent
        """
        feedback_lower = user_feedback.lower()

        # Speed adjustments
        if any(word in feedback_lower for word in ["slower", "slow down"]):
            intent.speed_multiplier *= 0.7
        elif any(word in feedback_lower for word in ["faster", "speed up"]):
            intent.speed_multiplier *= 1.3

        # Intensity adjustments
        if any(
            word in feedback_lower
            for word in ["more intense", "stronger", "more pronounced"]
        ):
            intent.intensity = min(1.0, intent.intensity * 1.3)
        elif any(
            word in feedback_lower for word in ["less intense", "subtler", "gentler"]
        ):
            intent.intensity = max(0.1, intent.intensity * 0.7)

        # Style changes
        if "smoother" in feedback_lower:
            intent.style_modifiers.append("smooth")
        elif "snappier" in feedback_lower:
            intent.style_modifiers.append("snappy")
        elif "bouncier" in feedback_lower:
            intent.style_modifiers.append("bouncy")

        return intent

    def intent_to_config(self, intent: AnimationIntent) -> AnimationConfig:
        """
        Convert AnimationIntent to AnimationConfig for the animator.

        Args:
            intent: Parsed animation intent

        Returns:
            AnimationConfig ready for animation generation
        """
        # Get base config for animation type
        from neonworks.editor.ai_animator import AnimationType

        base_config = AnimationType.get_by_name(intent.animation_type)

        if not base_config:
            # Create default config
            base_config = AnimationConfig(
                animation_type=intent.animation_type,
                frame_count=6,
                frame_duration=0.15,
                loop=True,
                style="smooth",
                intensity=0.7,
            )

        # Apply modifiers from intent
        config = AnimationConfig(
            animation_type=intent.animation_type,
            frame_count=intent.frame_count or base_config.frame_count,
            frame_duration=base_config.frame_duration / intent.speed_multiplier,
            loop=base_config.loop,
            style=self._derive_style(intent.style_modifiers) or base_config.style,
            intensity=intent.intensity,
        )

        return config

    def _derive_style(self, style_modifiers: List[str]) -> Optional[str]:
        """Derive animation style from modifiers"""
        style_map = {"smooth": "smooth", "snappy": "snappy", "bouncy": "bouncy"}

        for modifier in style_modifiers:
            if modifier in style_map:
                return style_map[modifier]

        # Check in style_modifiers dict
        for modifier in style_modifiers:
            if modifier in self.style_modifiers:
                style = self.style_modifiers[modifier].get("style")
                if style:
                    return style

        return None


# Example usage
if __name__ == "__main__":
    interpreter = AnimationInterpreter(model_type="local")

    # Test various requests
    test_requests = [
        "Make the character walk slowly like they're tired",
        "Create an aggressive attack animation",
        "Sneaky walk for a rogue character",
        "Happy bouncy idle animation",
        "Fast running animation with 8 frames",
        "Powerful spellcasting with a glow effect",
    ]

    for request in test_requests:
        print(f"\n{'='*60}")
        intent = interpreter.interpret_request(request)
        print(f"Request: {request}")
        print(f"Intent: {intent}")

        # Convert to config
        config = interpreter.intent_to_config(intent)
        print(f"Config: {config}")
