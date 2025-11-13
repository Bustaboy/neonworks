"""
Event Editor UI Demo

Demonstrates the Event Editor UI for creating and managing RPG-style events.
"""

import pygame

from core.event_commands import (
    CommandType,
    EventCommand,
    EventPage,
    GameEvent,
    ShowTextCommand,
    TriggerType,
    WaitCommand,
)
from engine.ui.event_editor_ui import EventEditorUI


def create_sample_events():
    """Create some sample events for demonstration."""
    events = []

    # Event 1: Simple NPC dialogue
    event1 = GameEvent(id=1, name="Village Elder", x=5, y=3)
    page1 = EventPage(trigger=TriggerType.ACTION_BUTTON)
    page1.commands = [
        ShowTextCommand("Welcome to our village, traveler!"),
        ShowTextCommand("We've been expecting you."),
        WaitCommand(60),
        EventCommand(
            command_type=CommandType.CONTROL_SWITCHES,
            parameters={"switch_id": 1, "value": True},
        ),
    ]
    event1.pages.append(page1)
    events.append(event1)

    # Event 2: Treasure chest
    event2 = GameEvent(id=2, name="Treasure Chest", x=10, y=8)
    page2 = EventPage(trigger=TriggerType.ACTION_BUTTON)
    page2.commands = [
        ShowTextCommand("You found a treasure chest!"),
        EventCommand(
            command_type=CommandType.CONTROL_VARIABLES,
            parameters={
                "variable_id": 1,
                "operation": "add",
                "operand_type": "constant",
                "operand_value": 100,
            },
        ),
        ShowTextCommand("You obtained 100 gold!"),
        EventCommand(
            command_type=CommandType.CONTROL_SELF_SWITCH,
            parameters={"switch": "A", "value": True},
        ),
    ]
    event2.pages.append(page2)

    # Second page for opened chest
    page2_opened = EventPage(
        trigger=TriggerType.ACTION_BUTTON,
        condition_self_switch_valid=True,
        condition_self_switch_ch="A",
    )
    page2_opened.commands = [
        ShowTextCommand("The chest is empty."),
    ]
    event2.pages.append(page2_opened)
    events.append(event2)

    # Event 3: Conditional event with branches
    event3 = GameEvent(id=3, name="Guard", x=7, y=5)
    page3 = EventPage(trigger=TriggerType.ACTION_BUTTON)
    page3.commands = [
        ShowTextCommand("Halt! Who goes there?"),
        EventCommand(
            command_type=CommandType.CONDITIONAL_BRANCH,
            parameters={"condition_type": "switch", "switch_id": 1},
            indent=0,
        ),
        ShowTextCommand("Ah, you're the one we're expecting. Pass through."),
        EventCommand(
            command_type=CommandType.LABEL,
            parameters={"name": "end"},
            indent=0,
        ),
    ]
    # Add an else branch (would normally have indent management)
    event3.pages.append(page3)
    events.append(event3)

    # Event 4: Shop keeper with multiple pages
    event4 = GameEvent(id=4, name="Shop Keeper", x=12, y=10)
    page4 = EventPage(trigger=TriggerType.ACTION_BUTTON)
    page4.commands = [
        ShowTextCommand("Welcome to my shop!"),
        EventCommand(
            command_type=CommandType.SHOW_CHOICES,
            parameters={
                "choices": ["Buy", "Sell", "Leave"],
                "cancel_type": 2,
                "default_choice": 0,
            },
        ),
    ]
    event4.pages.append(page4)
    events.append(event4)

    # Event 5: Autorun event
    event5 = GameEvent(id=5, name="Cutscene Trigger", x=15, y=12)
    page5 = EventPage(
        trigger=TriggerType.AUTORUN,
        condition_switch1_valid=True,
        condition_switch1_id=5,
    )
    page5.commands = [
        EventCommand(
            command_type=CommandType.FADEOUT_SCREEN, parameters={"duration": 60}
        ),
        WaitCommand(60),
        ShowTextCommand("A cutscene begins..."),
        EventCommand(
            command_type=CommandType.FADEIN_SCREEN, parameters={"duration": 60}
        ),
        EventCommand(
            command_type=CommandType.CONTROL_SWITCHES,
            parameters={"switch_id": 5, "value": False},
        ),
    ]
    event5.pages.append(page5)
    events.append(event5)

    return events


def main():
    """Run the event editor demo."""
    pygame.init()

    # Create display
    screen_width = 1400
    screen_height = 900
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Event Editor Demo - NeonWorks")

    # Create event editor
    event_editor = EventEditorUI(screen)

    # Load sample events
    sample_events = create_sample_events()
    event_editor.load_events_from_scene(sample_events)

    # Open the editor by default
    event_editor.toggle()

    # Main loop
    clock = pygame.time.Clock()
    running = True

    print("Event Editor Demo")
    print("================")
    print("Controls:")
    print("  ESC - Toggle Event Editor")
    print("  Click events to select and edit")
    print("  Click command types in palette to add commands")
    print("  Use page buttons to switch between event pages")
    print()

    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if event_editor.visible:
                        event_editor.toggle()
                    else:
                        event_editor.toggle()
            elif event.type == pygame.MOUSEWHEEL:
                event_editor.handle_scroll(event)

        # Clear screen
        screen.fill((40, 40, 50))

        # Draw some background text when editor is not visible
        if not event_editor.visible:
            font = pygame.font.Font(None, 48)
            text = font.render("Press ESC to open Event Editor", True, (150, 150, 150))
            text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2))
            screen.blit(text, text_rect)

            # Show event count
            count_font = pygame.font.Font(None, 24)
            count_text = count_font.render(
                f"Loaded {len(event_editor.events)} events",
                True,
                (120, 120, 120),
            )
            count_rect = count_text.get_rect(
                center=(screen_width // 2, screen_height // 2 + 60)
            )
            screen.blit(count_text, count_rect)

        # Render event editor
        event_editor.render()

        # Update display
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

    # Print final event state
    print("\nFinal Event State:")
    print("==================")
    for event in event_editor.get_events():
        print(f"\nEvent #{event.id}: {event.name}")
        print(f"  Position: ({event.x}, {event.y})")
        print(f"  Pages: {len(event.pages)}")
        for i, page in enumerate(event.pages):
            print(f"  Page {i + 1}: {len(page.commands)} commands")


if __name__ == "__main__":
    main()
