"""
AI Animation Demo

Demonstrates AI-powered animation generation using natural language.
Shows how to integrate the AI animator with the character generator system.
"""

import sys
from pathlib import Path

import pygame

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from neonworks.data.config_loader import ConfigLoader
from neonworks.editor.ai_animation_interpreter import AnimationInterpreter
from neonworks.editor.ai_animator import AIAnimator, AnimationType


def demo_basic_animation():
    """
    Demo 1: Generate basic animation from a sprite.
    """
    print("\n" + "=" * 60)
    print("DEMO 1: Basic Animation Generation")
    print("=" * 60)

    pygame.init()

    # Create animator
    animator = AIAnimator(model_type="local")

    # Load or create a test sprite
    test_sprite = pygame.Surface((32, 64), pygame.SRCALPHA)
    test_sprite.fill((100, 150, 200))  # Simple blue rectangle as placeholder

    # Generate walk animation
    walk_config = AnimationType.WALK
    print(f"\nGenerating '{walk_config.animation_type}' animation...")
    print(f"  Frames: {walk_config.frame_count}")
    print(f"  Duration: {walk_config.frame_duration}s per frame")
    print(f"  Style: {walk_config.style}")

    walk_frames = animator.generate_animation(test_sprite, walk_config)

    print(f"\n✓ Generated {len(walk_frames)} frames")

    # Export frames
    output_dir = Path("output/demo1_basic")
    animator.export_animation_frames(walk_frames, output_dir, "test_sprite", "walk")

    print(f"✓ Frames exported to: {output_dir}")


def demo_natural_language():
    """
    Demo 2: Generate animation using natural language description.
    """
    print("\n" + "=" * 60)
    print("DEMO 2: Natural Language Animation")
    print("=" * 60)

    pygame.init()

    # Create animator and interpreter
    animator = AIAnimator(model_type="local")
    interpreter = AnimationInterpreter(model_type="local")

    # Test sprite
    test_sprite = pygame.Surface((32, 64), pygame.SRCALPHA)
    pygame.draw.circle(test_sprite, (255, 100, 100), (16, 32), 15)  # Red circle

    # Natural language requests
    requests = [
        "Make the character walk slowly like they're tired",
        "Create an aggressive attack animation",
        "Sneaky walk for a rogue character",
        "Happy bouncy idle animation with 4 frames",
    ]

    for request in requests:
        print(f"\n--- Request: '{request}' ---")

        # Interpret request
        intent = interpreter.interpret_request(request)
        print(f"  Animation Type: {intent.animation_type}")
        print(f"  Style Modifiers: {', '.join(intent.style_modifiers)}")
        print(f"  Intensity: {intent.intensity:.2f}")
        print(f"  Speed Multiplier: {intent.speed_multiplier:.2f}")
        print(f"  Special Effects: {', '.join(intent.special_effects) or 'None'}")

        # Convert to config
        config = interpreter.intent_to_config(intent)

        # Generate animation
        frames = animator.generate_animation(test_sprite, config)
        print(f"  ✓ Generated {len(frames)} frames")


def demo_batch_generation():
    """
    Demo 3: Generate multiple animations at once.
    """
    print("\n" + "=" * 60)
    print("DEMO 3: Batch Animation Generation")
    print("=" * 60)

    pygame.init()

    animator = AIAnimator(model_type="local")

    # Test sprite
    test_sprite = pygame.Surface((32, 64), pygame.SRCALPHA)
    pygame.draw.rect(test_sprite, (100, 255, 100), (8, 8, 16, 48))  # Green rectangle

    # Generate multiple animations
    animation_types = ["idle", "walk", "run", "attack", "jump"]

    print(f"\nGenerating {len(animation_types)} animations...")

    animations = animator.generate_animation_batch(
        test_sprite, animation_types, component_id="demo_character"
    )

    print(f"\n✓ Generated animations:")
    for anim_type, frames in animations.items():
        print(f"  • {anim_type}: {len(frames)} frames")

    # Export all as sprite sheets
    for anim_type, frames in animations.items():
        output_path = Path(f"output/demo3_batch/{anim_type}_sheet.png")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        animator.export_sprite_sheet(frames, output_path, layout="horizontal")

    print(f"\n✓ Sprite sheets exported to: output/demo3_batch/")


def demo_character_generator_integration():
    """
    Demo 4: Integrate with character generator components.
    """
    print("\n" + "=" * 60)
    print("DEMO 4: Character Generator Integration")
    print("=" * 60)

    pygame.init()

    animator = AIAnimator(model_type="local")
    interpreter = AnimationInterpreter(model_type="local")

    # Load character parts schema
    try:
        parts = ConfigLoader.load("engine/data/character_parts.json")
        print("✓ Loaded character parts schema")
    except FileNotFoundError:
        print("❌ Character parts schema not found")
        return

    # Simulate a character component (in real use, would load actual sprite)
    component_data = parts["components"]["bodies"]["knight_body_male"]

    print(f"\nComponent: {component_data['name']}")
    print(f"  Category: {component_data['category']}")
    print(f"  Layer: {component_data['layer']} (z: {component_data['z_order']})")
    print(f"  Animations: {', '.join(component_data['animations'])}")

    # Create placeholder sprite (in real use, would load from asset_path)
    sprite_size = (component_data["size"]["width"], component_data["size"]["height"])
    component_sprite = pygame.Surface(sprite_size, pygame.SRCALPHA)
    component_sprite.fill((150, 100, 80))  # Brown for knight body

    # Generate animations for this component
    print(f"\nGenerating animations for {component_data['id']}...")

    for anim_type in component_data["animations"]:
        # Get suggestion for this animation
        sprite_info = {"type": "character", "class": "warrior"}
        suggestions = interpreter.suggest_animations(sprite_info)

        # Generate animation
        config = AnimationType.get_by_name(anim_type)
        if config:
            frames = animator.generate_animation(
                component_sprite, config, component_id=component_data["id"]
            )

            # Export with proper naming convention: {component_id}_{animation}_{frame}.png
            output_dir = Path(f"output/demo4_character_gen/{component_data['id']}")
            animator.export_animation_frames(frames, output_dir, component_data["id"], anim_type)

            print(f"  ✓ {anim_type}: {len(frames)} frames")

    print(f"\n✓ Component animations exported!")


def demo_refinement():
    """
    Demo 5: Refine animations based on user feedback.
    """
    print("\n" + "=" * 60)
    print("DEMO 5: Animation Refinement")
    print("=" * 60)

    pygame.init()

    animator = AIAnimator(model_type="local")
    interpreter = AnimationInterpreter(model_type="local")

    # Test sprite
    test_sprite = pygame.Surface((32, 64), pygame.SRCALPHA)
    test_sprite.fill((255, 200, 100))  # Orange

    # Initial request
    initial_request = "walking animation"
    print(f"\nInitial Request: '{initial_request}'")

    intent = interpreter.interpret_request(initial_request)
    config = interpreter.intent_to_config(intent)
    frames = animator.generate_animation(test_sprite, config)

    print(f"  Initial parameters:")
    print(f"    Intensity: {intent.intensity:.2f}")
    print(f"    Speed: {intent.speed_multiplier:.2f}")
    print(f"  ✓ Generated {len(frames)} frames")

    # Refinement iterations
    refinements = ["make it slower", "more intense", "add a bounce"]

    for i, refinement in enumerate(refinements, 1):
        print(f"\n--- Refinement {i}: '{refinement}' ---")

        intent = interpreter.refine_intent(intent, refinement)
        config = interpreter.intent_to_config(intent)
        frames = animator.generate_animation(test_sprite, config)

        print(f"  Updated parameters:")
        print(f"    Intensity: {intent.intensity:.2f}")
        print(f"    Speed: {intent.speed_multiplier:.2f}")
        print(f"    Style: {', '.join(intent.style_modifiers)}")
        print(f"  ✓ Regenerated {len(frames)} frames")


def demo_suggestions():
    """
    Demo 6: Get animation suggestions based on sprite type.
    """
    print("\n" + "=" * 60)
    print("DEMO 6: Animation Suggestions")
    print("=" * 60)

    interpreter = AnimationInterpreter(model_type="local")

    # Different sprite types
    sprite_types = [
        {"type": "character", "class": "warrior"},
        {"type": "character", "class": "mage"},
        {"type": "character", "class": "rogue"},
        {"type": "enemy", "class": "boss"},
        {"type": "npc", "class": "merchant"},
    ]

    for sprite_info in sprite_types:
        print(f"\nSprite: {sprite_info['type']} - {sprite_info['class']}")
        suggestions = interpreter.suggest_animations(sprite_info)

        print(f"  Suggested animations:")
        for anim_name, description in suggestions[:5]:  # Show top 5
            print(f"    • {anim_name}: {description}")


def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print("  AI ANIMATION SYSTEM DEMOS")
    print("=" * 70)
    print("\nThese demos showcase the AI-powered animation generation system.")
    print("They work with placeholder sprites since actual art assets are pending.")
    print("\nNote: Currently using procedural fallback animations.")
    print("      Integrate actual AI models for production use.")
    print("=" * 70)

    # Create output directory
    Path("output").mkdir(exist_ok=True)

    # Run demos
    try:
        demo_basic_animation()
        demo_natural_language()
        demo_batch_generation()
        demo_character_generator_integration()
        demo_refinement()
        demo_suggestions()

        print("\n" + "=" * 70)
        print("  ✓ ALL DEMOS COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print("\nCheck the 'output/' directory for generated animations.")
        print("See docs/AI_ANIMATOR.md for full documentation.")

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
