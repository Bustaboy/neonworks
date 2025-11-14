#!/usr/bin/env python3
"""
Test Animation Scripting

Tests the animation scripting system that parses complex animation sequences.
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pygame

from editor.animation_script_parser import (
    AnimationScriptParser,
    AnimationSequenceGenerator,
)
from editor.ai_animator import AIAnimator


def test_script_parsing():
    """Test parsing of animation scripts"""

    print("\n" + "=" * 70)
    print("  ANIMATION SCRIPTING TEST")
    print("=" * 70)

    # Initialize parser
    print("\nInitializing AnimationScriptParser...")
    parser = AnimationScriptParser(use_large_llm=True)

    # Test scripts
    test_scripts = [
        # Simple script
        "Character walks to the door",
        # Medium script
        "Character walks to the door and opens it",
        # Complex script
        """
        Character walks slowly to the door,
        pauses and looks around nervously,
        opens the door carefully,
        walks through the doorway,
        turns back to close the door
        """,
        # Very complex script
        """
        Hero runs towards the enemy,
        jumps over an obstacle,
        lands and immediately attacks,
        enemy gets hurt and staggers back,
        hero prepares for another strike
        """,
    ]

    print(f"\nTesting {len(test_scripts)} animation scripts...\n")

    for i, script in enumerate(test_scripts, 1):
        print(f"\n{'=' * 70}")
        print(f"Script {i}/{len(test_scripts)}")
        print(f"{'=' * 70}")
        print(f"\n{script.strip()}\n")
        print(f"{'─' * 70}")

        # Parse script
        actions = parser.parse_script(
            script, character_context={"type": "character", "class": "warrior"}
        )

        # Display results
        print(f"\nParsed into {len(actions)} actions:")
        for j, action in enumerate(actions, 1):
            print(f"\n  Action {j}:")
            print(f"    Type: {action.action}")
            print(f"    Duration: {action.duration} frames")
            print(f"    Prompt: {action.prompt}")
            print(f"    Speed: {action.speed}")

        total_frames = sum(action.duration for action in actions)
        total_seconds = total_frames / 8  # Assuming 8 FPS
        print(f"\n  Total: {total_frames} frames (~{total_seconds:.1f} seconds at 8 FPS)")

    # Check if using large LLM
    print("\n" + "=" * 70)
    if parser.llm is not None:
        print("  ✓ Animation Scripting: ACTIVE (Llama 3.2 8B)")
    else:
        print("  ⚠ Animation Scripting: SIMPLE PARSER")
        print("    For better results, download Llama 3.2 8B:")
        print("    python scripts/download_models.py --model llama-3.2-8b")
    print("=" * 70)


def test_sequence_generation():
    """Test full sequence generation from script"""

    print("\n" + "=" * 70)
    print("  SEQUENCE GENERATION TEST")
    print("=" * 70)

    # Initialize pygame
    pygame.init()

    # Create test sprite
    print("\nCreating test sprite...")
    test_sprite = pygame.Surface((32, 64), pygame.SRCALPHA)
    pygame.draw.circle(test_sprite, (100, 150, 200), (16, 32), 12)

    # Initialize animator and generator
    print("Initializing animator and sequence generator...")
    animator = AIAnimator(model_type="procedural")  # Use procedural for testing
    generator = AnimationSequenceGenerator(animator)

    # Test script
    script = """
    Character walks to the door,
    pauses,
    opens the door,
    walks through
    """

    print(f"\nGenerating animation sequence from script:")
    print(f"{script}\n")

    # Generate sequence
    frames = generator.generate_from_script(
        script,
        test_sprite,
        character_context={"type": "character", "class": "rogue"},
        use_ai=False,  # Use procedural for testing
    )

    print(f"\n✓ Generated {len(frames)} total frames")

    # Export (optional)
    output_dir = Path("output/test_scripting")
    if len(frames) > 0:
        print(f"\nExporting frames to {output_dir}...")
        output_dir.mkdir(parents=True, exist_ok=True)

        animator.export_animation_frames(
            frames, output_dir, "scripted_test", "sequence"
        )

        print(f"✓ Exported frames to: {output_dir}")

        # Also export as sprite sheet
        sheet_path = output_dir / "sequence_sheet.png"
        animator.export_sprite_sheet(frames, sheet_path, layout="horizontal")
        print(f"✓ Exported sprite sheet: {sheet_path}")

    pygame.quit()


if __name__ == "__main__":
    # Run tests
    test_script_parsing()
    print("\n")
    test_sequence_generation()

    print("\n" + "=" * 70)
    print("  ALL TESTS COMPLETED")
    print("=" * 70)
