"""
Animation Script Parser

Parses complex animation scripts using LLM to generate multi-step animation sequences.
Enables natural language animation scripting like:

"Character walks to the door, pauses, opens it, walks through, and closes it behind them"
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import pygame

from neonworks.editor.ai_animation_interpreter import AnimationInterpreter
from neonworks.editor.ai_animator import AIAnimator, AnimationConfig


@dataclass
class AnimationAction:
    """Single action in an animation sequence"""

    action: str  # Action name (walk, turn, open_door, etc.)
    duration: int  # Number of frames
    prompt: str  # Description for generation
    speed: str = "normal"  # slow, normal, fast
    properties: Dict = None  # Additional properties

    def __post_init__(self):
        if self.properties is None:
            self.properties = {}


class AnimationScriptParser:
    """
    Parse natural language scripts into structured animation sequences.

    Uses a larger LLM (Llama 3.2 8B) for better understanding of complex
    multi-step animation sequences.
    """

    def __init__(self, use_large_llm: bool = True):
        """
        Initialize script parser.

        Args:
            use_large_llm: If True, tries to load Llama 3.2 8B for scripting.
                          If False or model not available, uses standard LLM.
        """
        self.llm = None
        self.use_large_llm = use_large_llm

        # Initialize standard interpreter for simple animations
        self.interpreter = AnimationInterpreter(model_type="local")

        # Try to load larger LLM for script parsing
        if use_large_llm:
            self._init_scripting_llm()

        print("[ScriptParser] Initialized")

    def _init_scripting_llm(self):
        """Initialize larger LLM for script parsing"""
        from pathlib import Path

        try:
            from llama_cpp import Llama
        except ImportError:
            print("[ScriptParser] llama-cpp-python not installed")
            return

        # Look for Llama 3.2 8B model
        models_dir = Path("models")
        model_path = models_dir / "llama-3.2-8b-q4.gguf"

        if not model_path.exists():
            print(f"[ScriptParser] Large LLM not found: {model_path}")
            print(
                "                Download with: python scripts/download_models.py --model llama-3.2-8b"
            )
            print("                Will use standard LLM for script parsing")
            return

        print(f"[ScriptParser] Loading Llama 3.2 8B from {model_path}...")

        try:
            self.llm = Llama(
                model_path=str(model_path),
                n_ctx=4096,  # Larger context for scripts
                n_threads=8,  # More threads for larger model
                n_gpu_layers=0,  # 0 for CPU, adjust if using GPU
                verbose=False,
            )
            print("[ScriptParser] Llama 3.2 8B loaded successfully!")

        except Exception as e:
            print(f"[ScriptParser] Failed to load model: {e}")
            self.llm = None

    def parse_script(
        self, script: str, character_context: Optional[Dict] = None
    ) -> List[AnimationAction]:
        """
        Parse animation script into structured actions.

        Args:
            script: Natural language script
            character_context: Optional character info for context

        Returns:
            List of AnimationAction objects

        Example:
            script = "Character walks to the door, pauses, opens it, walks through"
            actions = parser.parse_script(script)
            # Returns: [walk action, pause action, open_door action, walk action]
        """
        print(f"[ScriptParser] Parsing script...")

        # If we have the large LLM, use it
        if self.llm is not None:
            actions = self._parse_with_llm(script, character_context)
        else:
            # Fallback to simpler parsing
            actions = self._parse_simple(script, character_context)

        print(f"[ScriptParser] Found {len(actions)} actions")
        for i, action in enumerate(actions, 1):
            print(f"  {i}. {action.action} ({action.duration} frames): {action.prompt}")

        return actions

    def _parse_with_llm(self, script: str, context: Optional[Dict]) -> List[AnimationAction]:
        """Parse script using LLM"""

        prompt = self._build_script_prompt(script, context)

        try:
            response = self.llm(
                prompt,
                max_tokens=1000,
                temperature=0.3,
                top_p=0.9,
                repeat_penalty=1.1,
                stop=["</s>", "\n\n\n"],
                echo=False,
            )

            text = response["choices"][0]["text"].strip()

            # Parse JSON array from response
            actions = self._parse_actions_json(text)

            if actions:
                return actions
            else:
                print("[ScriptParser] LLM parse failed, using simple parser")
                return self._parse_simple(script, context)

        except Exception as e:
            print(f"[ScriptParser] LLM error: {e}")
            return self._parse_simple(script, context)

    def _parse_simple(self, script: str, context: Optional[Dict]) -> List[AnimationAction]:
        """
        Simple script parsing without LLM.

        Breaks script into sentences and creates basic actions.
        """
        # Split by common separators
        sentences = re.split(r"[,;.]\s*|and\s+then|then\s+", script)

        actions = []
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # Identify action type from keywords
            action_type = "idle"
            if any(word in sentence.lower() for word in ["walk", "walking", "moves"]):
                action_type = "walk"
            elif any(word in sentence.lower() for word in ["run", "running", "runs"]):
                action_type = "run"
            elif any(word in sentence.lower() for word in ["turn", "turns", "spins"]):
                action_type = "turn"
            elif any(word in sentence.lower() for word in ["jump", "jumps", "leaps"]):
                action_type = "jump"
            elif any(word in sentence.lower() for word in ["attack", "strikes", "hits"]):
                action_type = "attack"
            elif any(word in sentence.lower() for word in ["pause", "waits", "stops"]):
                action_type = "idle"
            elif any(word in sentence.lower() for word in ["open", "opens"]):
                action_type = "interact"
            elif any(word in sentence.lower() for word in ["cast", "casts", "magic"]):
                action_type = "cast_spell"

            # Determine duration
            duration = 8  # default
            if "slowly" in sentence.lower():
                duration = 12
            elif "quickly" in sentence.lower():
                duration = 6

            action = AnimationAction(
                action=action_type,
                duration=duration,
                prompt=sentence,
                speed="normal",
            )
            actions.append(action)

        return actions

    def _build_script_prompt(self, script: str, context: Optional[Dict]) -> str:
        """Build prompt for LLM script parsing"""

        context_str = ""
        if context:
            context_str = f"\n\nCharacter Context:\n{json.dumps(context, indent=2)}"

        prompt = f"""<|system|>
You are an animation sequence parser. Break down natural language animation scripts into structured action sequences.

Available action types:
- walk: Walking movement
- run: Running movement
- idle: Standing still
- turn: Turning/rotating
- jump: Jumping
- attack: Attack action
- cast_spell: Casting magic
- interact: Interacting with objects (opening doors, picking up items, etc.)
- hurt: Taking damage
- death: Death animation

<|user|>
Parse this animation script into a JSON array of actions:

"{script}"{context_str}

Return ONLY a valid JSON array in this exact format:
[
  {{
    "action": "walk",
    "duration": 12,
    "prompt": "character walking towards the door",
    "speed": "normal",
    "properties": {{"direction": "forward"}}
  }},
  {{
    "action": "idle",
    "duration": 4,
    "prompt": "character pausing at the door",
    "speed": "normal",
    "properties": {{}}
  }},
  {{
    "action": "interact",
    "duration": 8,
    "prompt": "character opening the door",
    "speed": "normal",
    "properties": {{"object": "door"}}
  }}
]

Consider:
- Breaking complex actions into simple steps
- Choosing appropriate durations (typical: 6-12 frames)
- Using descriptive prompts for each action
- Slow actions: 12-16 frames, Fast actions: 4-6 frames

<|assistant|>
["""

        return prompt

    def _parse_actions_json(self, text: str) -> Optional[List[AnimationAction]]:
        """Parse JSON array of actions from LLM response"""

        # Find JSON array
        array_match = re.search(r"\[.*\]", text, re.DOTALL)

        if not array_match:
            return None

        json_str = array_match.group(0)

        try:
            data = json.loads(json_str)

            if not isinstance(data, list):
                return None

            actions = []
            for item in data:
                # Validate required fields
                if "action" not in item or "duration" not in item:
                    continue

                # Set defaults
                item.setdefault("prompt", item["action"])
                item.setdefault("speed", "normal")
                item.setdefault("properties", {})

                action = AnimationAction(**item)
                actions.append(action)

            return actions if actions else None

        except (json.JSONDecodeError, TypeError, ValueError) as e:
            print(f"[ScriptParser] JSON parse error: {e}")
            return None


class AnimationSequenceGenerator:
    """
    Generate complete animation sequences from parsed scripts.

    Coordinates with AnimationInterpreter and AIAnimator to create
    frame-by-frame animations from script actions.
    """

    def __init__(self, animator: AIAnimator):
        """
        Initialize sequence generator.

        Args:
            animator: AIAnimator instance for generating frames
        """
        self.animator = animator
        self.interpreter = AnimationInterpreter(model_type="local")

    def generate_from_script(
        self,
        script: str,
        source_sprite: pygame.Surface,
        character_context: Optional[Dict] = None,
        use_ai: bool = False,
    ) -> List[pygame.Surface]:
        """
        Generate complete animation sequence from script.

        Args:
            script: Natural language animation script
            source_sprite: Source character sprite
            character_context: Optional character information
            use_ai: Whether to use AI generation (vs procedural)

        Returns:
            List of all animation frames in sequence
        """
        # Parse script
        parser = AnimationScriptParser(use_large_llm=True)
        actions = parser.parse_script(script, character_context)

        if not actions:
            print("[SequenceGen] No actions parsed")
            return []

        # Generate animation for each action
        all_frames = []

        for i, action in enumerate(actions, 1):
            print(f"\n[SequenceGen] Generating action {i}/{len(actions)}: {action.action}")

            # Convert action to animation intent
            intent = self.interpreter.interpret_request(action.prompt, context=character_context)

            # Convert intent to config
            config = self.interpreter.intent_to_config(intent)

            # Override duration if specified
            if action.duration:
                config.frame_count = action.duration

            # Generate frames
            frames = self.animator.generate_animation(
                source_sprite, config, component_id=None, use_ai=use_ai
            )

            all_frames.extend(frames)

            # Add transition frames if not last action
            if i < len(actions):
                # Add 2 transition frames between actions
                transition = self._create_transition(frames[-1], 2)
                all_frames.extend(transition)

        print(f"\n[SequenceGen] Generated {len(all_frames)} total frames")
        return all_frames

    def _create_transition(
        self, last_frame: pygame.Surface, num_frames: int
    ) -> List[pygame.Surface]:
        """Create simple transition frames between actions"""
        # For now, just hold the last frame
        return [last_frame.copy() for _ in range(num_frames)]


# Example usage
if __name__ == "__main__":
    import sys

    # Initialize pygame
    pygame.init()

    # Create test sprite
    test_sprite = pygame.Surface((32, 64), pygame.SRCALPHA)
    pygame.draw.circle(test_sprite, (100, 150, 200), (16, 32), 12)

    # Initialize animator
    animator = AIAnimator(model_type="procedural")

    # Create sequence generator
    generator = AnimationSequenceGenerator(animator)

    # Test script
    script = """
    Character walks slowly to the door,
    pauses and looks around,
    opens the door carefully,
    walks through the doorway,
    turns back,
    closes the door
    """

    print("\n" + "=" * 70)
    print("  ANIMATION SCRIPT PARSER TEST")
    print("=" * 70)

    # Generate sequence
    frames = generator.generate_from_script(
        script, test_sprite, character_context={"type": "character", "class": "rogue"}
    )

    print(f"\n✓ Generated animation sequence with {len(frames)} frames")
    print("\nTo export:")
    print("  animator.export_animation_frames(frames, Path('output'), 'scripted', 'sequence')")
    print("  animator.export_sprite_sheet(frames, Path('output/scripted_sequence.png'))")
