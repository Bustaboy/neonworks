"""
Demo script for testing specialized field editors.

This script demonstrates the usage of all five specialized field editors:
- EffectEditor: Visual effect builder
- FormulaEditor: Damage formula editor
- StatEditor: Stat distribution with sliders
- DropEditor: Item drop table editor
- ActionEditor: Enemy AI action patterns

Run this script to test the editors interactively.
"""

import sys

import pygame

from neonworks.engine.data.database_schema import DropItem, Effect, EffectType
from neonworks.engine.ui.database_fields import (
    ActionEditor,
    DropEditor,
    EffectEditor,
    FormulaEditor,
    StatEditor,
)


def main():
    """Main demo function."""
    # Initialize Pygame
    pygame.init()

    # Create window
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Field Editors Demo")

    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 32)
    small_font = pygame.font.Font(None, 24)

    # Create editors
    effect_editor = EffectEditor(screen)
    formula_editor = FormulaEditor(screen)
    stat_editor = StatEditor(screen)
    drop_editor = DropEditor(screen)
    action_editor = ActionEditor(screen)

    # Demo state
    current_editor = None
    demo_results = {
        "effect": None,
        "formula": None,
        "stats": None,
        "drops": None,
        "actions": None,
    }

    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Check if any editor is open
            if effect_editor.is_visible():
                effect_editor.handle_event(event)
                result = effect_editor.render()
                if result is not None:
                    demo_results["effect"] = result
                    print(f"Effect configured: {result.effect_type.value}")
            elif formula_editor.is_visible():
                formula_editor.handle_event(event)
                result = formula_editor.render()
                if result is not None:
                    demo_results["formula"] = result
                    print(f"Formula set: {result}")
            elif stat_editor.is_visible():
                stat_editor.handle_event(event)
                result = stat_editor.render()
                if result is not None:
                    demo_results["stats"] = result
                    print(f"Stats configured: {result}")
            elif drop_editor.is_visible():
                drop_editor.handle_event(event)
                result = drop_editor.render()
                if result is not None:
                    demo_results["drops"] = result
                    print(f"Drops configured: {len(result)} items")
            elif action_editor.is_visible():
                action_editor.handle_event(event)
                result = action_editor.render()
                if result is not None:
                    demo_results["actions"] = result
                    print(f"Actions configured: {len(result)} patterns")
            else:
                # Main menu input
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        # Open effect editor
                        sample_effect = Effect(
                            effect_type=EffectType.DAMAGE_HP,
                            value1=100.0,
                            value2=20.0,
                        )
                        effect_editor.open(sample_effect)
                    elif event.key == pygame.K_2:
                        # Open formula editor
                        formula_editor.open("a.atk * 4 - b.def * 2")
                    elif event.key == pygame.K_3:
                        # Open stat editor
                        sample_stats = {
                            "HP": 100,
                            "MP": 50,
                            "ATK": 15,
                            "DEF": 15,
                            "MAT": 15,
                            "MDF": 15,
                            "AGI": 15,
                            "LUK": 10,
                        }
                        stat_editor.open(sample_stats, use_point_pool=False)
                    elif event.key == pygame.K_4:
                        # Open drop editor
                        sample_drops = [
                            DropItem(kind=1, item_id=1, drop_rate=1.0),
                            DropItem(kind=2, item_id=5, drop_rate=0.5),
                        ]
                        drop_editor.open(sample_drops)
                    elif event.key == pygame.K_5:
                        # Open action editor
                        sample_actions = [
                            {
                                "skill_id": 1,
                                "condition_type": 0,
                                "condition_param1": 0,
                                "condition_param2": 0,
                                "rating": 5,
                            }
                        ]
                        action_editor.open(sample_actions)
                    elif event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                        running = False

        # Render
        screen.fill((20, 20, 30))

        # Render editors if open
        if effect_editor.is_visible():
            effect_editor.render()
        elif formula_editor.is_visible():
            formula_editor.render()
        elif stat_editor.is_visible():
            stat_editor.render()
        elif drop_editor.is_visible():
            drop_editor.render()
        elif action_editor.is_visible():
            action_editor.render()
        else:
            # Main menu
            title = font.render("Field Editors Demo", True, (100, 200, 255))
            screen.blit(title, (screen.get_width() // 2 - 150, 50))

            instructions = [
                "Press a number to open an editor:",
                "",
                "1 - Effect Editor (Visual effect builder)",
                "2 - Formula Editor (Damage formula editor)",
                "3 - Stat Editor (Stat distribution with sliders)",
                "4 - Drop Editor (Item drop table editor)",
                "5 - Action Editor (Enemy AI action patterns)",
                "",
                "Q or ESC - Quit",
            ]

            y = 150
            for instruction in instructions:
                text = small_font.render(instruction, True, (220, 220, 240))
                screen.blit(text, (100, y))
                y += 35

            # Show current results
            results_y = y + 30
            results_title = small_font.render("Current Results:", True, (200, 200, 255))
            screen.blit(results_title, (100, results_y))

            results_y += 40
            for key, value in demo_results.items():
                if value is not None:
                    if key == "effect":
                        result_text = f"{key.title()}: {value.effect_type.value}"
                    elif key == "formula":
                        result_text = f"{key.title()}: {value[:40]}..."
                    elif key == "stats":
                        result_text = f"{key.title()}: {len(value)} stats set"
                    elif key == "drops":
                        result_text = f"{key.title()}: {len(value)} items"
                    elif key == "actions":
                        result_text = f"{key.title()}: {len(value)} patterns"
                    else:
                        result_text = f"{key.title()}: Set"

                    text = small_font.render(result_text, True, (100, 255, 100))
                else:
                    text = small_font.render(f"{key.title()}: Not set", True, (150, 150, 150))

                screen.blit(text, (120, results_y))
                results_y += 30

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    print("\nDemo completed!")
    print("\nFinal results:")
    for key, value in demo_results.items():
        if value is not None:
            print(f"  {key.title()}: Configured")
        else:
            print(f"  {key.title()}: Not configured")


if __name__ == "__main__":
    main()
