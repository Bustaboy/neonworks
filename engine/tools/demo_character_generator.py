"""
Character Generator Demo

Demonstrates the character generator capabilities:
- Creating characters from component selections
- Color tinting
- Multi-frame sprite sheets
- Preset save/load
- Randomization
- AI-friendly description API
- Multi-size export

Run this demo:
    python engine/tools/demo_character_generator.py
"""

from pathlib import Path
from engine.tools.character_generator import (
    CharacterGenerator,
    CharacterPreset,
    ComponentLayer,
    ColorTint,
    LayerType,
    Direction,
    quick_character,
)
from engine.tools.ai_character_generator import AICharacterGenerator, generate_ai_character


def demo_basic_character():
    """Demo: Create a basic character."""
    print("\n=== DEMO 1: Basic Character Creation ===\n")

    # Create generator
    gen = CharacterGenerator(default_size=32)

    # Load component library
    component_path = Path("../../test_outputs/character_components")
    if component_path.exists():
        gen.load_component_library(component_path)
        print(f"Loaded {len(gen.component_library)} components\n")
    else:
        print("Component library not found. Run generate_sample_components.py first.")
        return

    # Create a knight character
    knight = gen.create_character(
        components={
            "body": "body_human_male",
            "hair": "hair_short_brown",
            "outfit": "outfit_knight_armor",
            "weapon": "weapon_sword",
        },
        tints={"outfit": ColorTint(100, 100, 200)},  # Blue armor
        name="Sir Lancelot",
    )

    print(f"Created character: {knight.name}")
    print(f"Layers: {len(knight.layers)}")
    for layer in knight.layers:
        tint_info = f" (tinted {layer.tint.to_tuple()})" if layer.tint else ""
        print(f"  - {layer.layer_type.name}: {layer.component_id}{tint_info}")

    # Render sprite sheet
    output_path = Path("../../test_outputs/demo_knight.png")
    gen.render_character(knight, output_path, num_frames=4)

    print(f"\nSaved character to: {output_path}")


def demo_randomization():
    """Demo: Random character generation."""
    print("\n=== DEMO 2: Random Character Generation ===\n")

    gen = CharacterGenerator(default_size=32)

    component_path = Path("../../test_outputs/character_components")
    if not component_path.exists():
        print("Component library not found.")
        return

    gen.load_component_library(component_path)

    # Generate 3 random characters
    for i in range(3):
        character = gen.randomize_character(name=f"Random Character {i+1}")

        print(f"\n{character.name}:")
        for layer in character.layers:
            print(f"  - {layer.layer_type.name}: {layer.component_id}")

        # Save
        output_path = Path(f"../../test_outputs/demo_random_{i+1}.png")
        gen.render_character(character, output_path, num_frames=4)

    print("\nGenerated 3 random characters!")


def demo_preset_save_load():
    """Demo: Save and load presets."""
    print("\n=== DEMO 3: Preset Save/Load ===\n")

    gen = CharacterGenerator(default_size=32)

    component_path = Path("../../test_outputs/character_components")
    if not component_path.exists():
        print("Component library not found.")
        return

    gen.load_component_library(component_path)

    # Create a mage character
    mage = gen.create_character(
        components={
            "body": "body_human_female",
            "hair": "hair_long_blonde",
            "outfit": "outfit_mage_robe",
            "weapon": "weapon_staff",
        },
        tints={
            "outfit": ColorTint(100, 50, 150),  # Purple robe
            "weapon": ColorTint(150, 100, 50),  # Brown staff
        },
        name="Morgana the Wise",
    )

    # Save preset
    preset_path = Path("../../test_outputs/mage_preset.json")
    gen.save_preset(mage, preset_path)
    print(f"Saved preset to: {preset_path}")

    # Load preset
    loaded = gen.load_preset(preset_path)
    print(f"\nLoaded preset: {loaded.name}")
    print(f"Description: {loaded.description}")
    print(f"Layers: {len(loaded.layers)}")

    # Render loaded character
    output_path = Path("../../test_outputs/demo_mage.png")
    gen.render_character(loaded, output_path, num_frames=4)
    print(f"Rendered to: {output_path}")


def demo_multi_size_export():
    """Demo: Export at multiple sizes."""
    print("\n=== DEMO 4: Multi-Size Export ===\n")

    gen = CharacterGenerator(default_size=32)

    component_path = Path("../../test_outputs/character_components")
    if not component_path.exists():
        print("Component library not found.")
        return

    gen.load_component_library(component_path)

    # Create a character
    character = gen.create_character(
        components={
            "body": "body_elf_male",
            "hair": "hair_ponytail_red",
            "outfit": "outfit_peasant_clothes",
            "weapon": "weapon_bow",
        },
        name="Legolas",
    )

    # Export at multiple sizes
    output_dir = Path("../../test_outputs/demo_multi_size/")
    gen.export_multi_size(character, output_dir, sizes=[32, 48, 64], num_frames=4)

    print(f"Exported character at 3 sizes to: {output_dir}")
    print("  - 32x32")
    print("  - 48x48")
    print("  - 64x64")


def demo_description_based():
    """Demo: Generate from text description."""
    print("\n=== DEMO 5: AI-Friendly Description API ===\n")

    gen = CharacterGenerator(default_size=32)

    component_path = Path("../../test_outputs/character_components")
    if not component_path.exists():
        print("Component library not found.")
        return

    gen.load_component_library(component_path)

    # Generate from description
    descriptions = [
        "A brave knight with brown hair and blue armor",
        "An elf mage with blonde hair and a purple robe",
        "A peasant with red hair and a bow",
    ]

    for i, desc in enumerate(descriptions):
        print(f'\nDescription: "{desc}"')

        character = gen.generate_from_description(desc, name=f"Character {i+1}")

        print(f"Generated: {character.name}")
        print(f"Layers: {len(character.layers)}")
        for layer in character.layers:
            print(f"  - {layer.layer_type.name}: {layer.component_id}")

        # Render
        output_path = Path(f"../../test_outputs/demo_described_{i+1}.png")
        gen.render_character(character, output_path, num_frames=4)


def demo_color_variations():
    """Demo: Create color variations of the same character."""
    print("\n=== DEMO 6: Color Variations ===\n")

    gen = CharacterGenerator(default_size=32)

    component_path = Path("../../test_outputs/character_components")
    if not component_path.exists():
        print("Component library not found.")
        return

    gen.load_component_library(component_path)

    # Base character
    base_components = {
        "body": "body_human_male",
        "hair": "hair_short_brown",
        "outfit": "outfit_knight_armor",
    }

    # Different color schemes
    color_schemes = [
        ("Red Knight", ColorTint(200, 80, 80)),
        ("Blue Knight", ColorTint(80, 80, 200)),
        ("Green Knight", ColorTint(80, 200, 80)),
        ("Gold Knight", ColorTint(200, 180, 80)),
    ]

    print("Creating color variations:\n")

    for name, armor_tint in color_schemes:
        character = gen.create_character(
            components=base_components, tints={"outfit": armor_tint}, name=name
        )

        print(f"{name}: armor tint {armor_tint.to_tuple()}")

        output_path = Path(f"../../test_outputs/demo_{name.lower().replace(' ', '_')}.png")
        gen.render_character(character, output_path, num_frames=4)

    print(f"\nCreated {len(color_schemes)} color variations!")


def demo_list_components():
    """Demo: List available components."""
    print("\n=== DEMO 7: List Available Components ===\n")

    gen = CharacterGenerator(default_size=32)

    component_path = Path("../../test_outputs/character_components")
    if not component_path.exists():
        print("Component library not found.")
        return

    gen.load_component_library(component_path)

    # List all components
    components = gen.list_components()

    print("Available components by layer:\n")

    for layer_type, component_list in components.items():
        if component_list:
            print(f"{layer_type.name}:")
            for comp_id in component_list:
                print(f"  - {comp_id}")
            print()


def demo_ai_generation():
    """Demo: AI-powered character generation."""
    print("\n=== DEMO 8: AI-Powered Character Generation ===\n")

    ai_gen = AICharacterGenerator(default_size=32)

    component_path = Path("../../test_outputs/character_components")
    if not component_path.exists():
        print("Component library not found.")
        return

    ai_gen.load_component_library(component_path)

    # Test descriptions with different archetypes
    descriptions = [
        "A brave knight with shining blue armor",
        "A wise wizard with flowing purple robes and a gnarled staff",
        "A skilled elven ranger with a longbow",
        "A simple peasant farmer",
        "A fierce warrior with red armor and a sword",
    ]

    print("Generating characters from natural language descriptions:\n")

    for i, desc in enumerate(descriptions):
        print(f'\n{i+1}. "{desc}"')
        print("-" * 60)

        character = ai_gen.generate_from_ai_description(desc)

        print(f"   Name: {character.name}")
        print(f"   Layers: {len(character.layers)}")
        for layer in character.layers:
            tint_str = f" (tinted)" if layer.tint else ""
            print(f"     • {layer.layer_type.name}: {layer.component_id}{tint_str}")

        # Save
        output_path = Path(f"../../test_outputs/demo_ai_{i+1}.png")
        ai_gen.render_character(character, output_path, num_frames=4)
        print(f"   Saved: {output_path.name}")

    print(f"\n✓ Generated {len(descriptions)} characters from AI descriptions!")


def main():
    """Run all demos."""
    print("=" * 60)
    print("CHARACTER GENERATOR DEMO")
    print("=" * 60)

    # Check if sample components exist
    component_path = Path("../../test_outputs/character_components")
    if not component_path.exists():
        print("\nSample components not found!")
        print("Please run: python engine/tools/generate_sample_components.py")
        print(f"Looking for: {component_path.absolute()}")
        return

    # Run demos
    demo_list_components()
    demo_basic_character()
    demo_randomization()
    demo_preset_save_load()
    demo_multi_size_export()
    demo_description_based()
    demo_color_variations()
    demo_ai_generation()  # NEW: AI-powered generation

    print("\n" + "=" * 60)
    print("DEMO COMPLETE!")
    print("=" * 60)
    print("\nCheck test_outputs/ directory for generated character sprites!")
    print("\nFeatures demonstrated:")
    print("  ✓ Manual component selection")
    print("  ✓ Randomization")
    print("  ✓ Preset save/load")
    print("  ✓ Multi-size export")
    print("  ✓ Description-based generation")
    print("  ✓ Color variations")
    print("  ✓ AI-powered generation (NEW!)")


if __name__ == "__main__":
    main()
