#!/usr/bin/env python3
"""
Test LLM Integration

Tests the LLM-powered natural language interpretation for animations.
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from editor.ai_animation_interpreter import AnimationInterpreter


def test_llm_interpretation():
    """Test LLM interpretation of animation requests"""

    print("\n" + "=" * 70)
    print("  LLM INTEGRATION TEST")
    print("=" * 70)

    # Initialize interpreter with LLM
    print("\nInitializing AnimationInterpreter with LLM...")
    interpreter = AnimationInterpreter(model_type="local")

    # Test cases
    test_requests = [
        # Simple requests
        "walk",
        "run fast",
        "idle animation",
        # Medium complexity
        "walk slowly",
        "aggressive attack",
        "sneaky movement",
        # Complex requests
        "Make character walk slowly like they're tired",
        "Create an aggressive attack animation",
        "Sneaky walk for a rogue character",
        "Happy bouncy idle animation with 4 frames",
        "Tired walk with 8 frames and a glow effect",
        # Edge cases
        "run very fast",
        "sad slow walk",
        "energetic jumping with 6 frames",
    ]

    print(f"\nTesting {len(test_requests)} animation requests...\n")

    results = []
    for i, request in enumerate(test_requests, 1):
        print(f"\n{'─' * 70}")
        print(f"Test {i}/{len(test_requests)}: '{request}'")
        print(f"{'─' * 70}")

        # Interpret request
        intent = interpreter.interpret_request(request)

        # Display results
        print(f"\n  Animation Type: {intent.animation_type}")
        print(f"  Style Modifiers: {', '.join(intent.style_modifiers) if intent.style_modifiers else 'None'}")
        print(f"  Intensity: {intent.intensity:.2f}")
        print(f"  Speed Multiplier: {intent.speed_multiplier:.2f}")
        print(f"  Special Effects: {', '.join(intent.special_effects) if intent.special_effects else 'None'}")
        print(f"  Frame Count: {intent.frame_count if intent.frame_count else 'Default'}")
        print(f"  Confidence: {intent.confidence:.2f}")

        # Check if reasonable
        is_valid = (
            intent.animation_type in [
                "idle",
                "walk",
                "run",
                "attack",
                "cast_spell",
                "jump",
                "hurt",
                "death",
            ]
            and 0.0 <= intent.intensity <= 1.0
            and 0.1 <= intent.speed_multiplier <= 3.0
        )

        status = "✓ VALID" if is_valid else "✗ INVALID"
        print(f"\n  Status: {status}")

        results.append(
            {
                "request": request,
                "intent": intent,
                "valid": is_valid,
            }
        )

    # Summary
    print("\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)

    valid_count = sum(1 for r in results if r["valid"])
    print(f"\n  Total Tests: {len(results)}")
    print(f"  Valid Results: {valid_count}/{len(results)}")
    print(f"  Success Rate: {valid_count/len(results)*100:.1f}%")

    # Check if using LLM or fallback
    if hasattr(interpreter, "llm") and interpreter.llm is not None:
        print(f"\n  ✓ LLM Integration: ACTIVE")
    else:
        print(f"\n  ⚠ LLM Integration: FALLBACK (rule-based)")
        print(f"    Download models with: python scripts/download_models.py --recommended")

    print("\n" + "=" * 70)

    # Return success if > 80% valid
    return valid_count / len(results) >= 0.8


if __name__ == "__main__":
    success = test_llm_interpretation()
    sys.exit(0 if success else 1)
