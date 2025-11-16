"""
Test script for the Database Editor UI

This script creates a simple Pygame window and initializes the database editor
to test the UI functionality.

Controls:
- F6: Toggle Database Editor
- ESC: Close Database Editor
- Mouse: Navigate and interact with UI

The database editor provides:
1. Category selection (Actors, Items, Skills, etc.)
2. Entry list with search functionality
3. Detail editor for modifying entry fields
4. CRUD operations (Create, Read, Update, Delete, Duplicate)
"""

import sys
from pathlib import Path

import pygame

from neonworks.engine.ui.database_editor_ui import DatabaseEditorUI

# Add parent directory to path so we can import neonworks modules
sys.path.insert(0, str(Path(__file__).parent))


def main():
    """Main test function."""
    # Initialize Pygame
    pygame.init()

    # Create window
    screen_width = 1280
    screen_height = 720
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Database Editor Test - Press F6 to open")

    # Create database editor
    db_editor = DatabaseEditorUI(screen, database_path=Path("data/test_database.json"))

    # Clock for frame rate
    clock = pygame.time.Clock()
    running = True

    print("=" * 60)
    print("Database Editor Test")
    print("=" * 60)
    print("Controls:")
    print("  F6  - Toggle Database Editor")
    print("  ESC - Close Database Editor (when open)")
    print("  Mouse - Navigate and interact")
    print()
    print("Press F6 to open the Database Editor!")
    print("=" * 60)

    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Handle keyboard
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F6:
                    db_editor.toggle()
                    if db_editor.visible:
                        print("\n🗄 Database Editor opened!")
                        print("  - Select a category on the left")
                        print("  - Click 'New Entry' to create entries")
                        print("  - Click entries to edit them")
                        print("  - Press F6 or ESC to close")
                    else:
                        print("✓ Database Editor closed")
                elif event.key == pygame.K_ESCAPE and db_editor.visible:
                    db_editor.toggle()
                    print("✓ Database Editor closed")

            # Pass events to database editor
            if db_editor.visible:
                db_editor.handle_event(event)

        # Update
        delta_time = clock.tick(60) / 1000.0  # 60 FPS
        db_editor.update(delta_time)

        # Render
        screen.fill((40, 40, 50))  # Dark background

        # Draw instructions if editor is closed
        if not db_editor.visible:
            font = pygame.font.Font(None, 36)
            title = font.render("Database Editor Test", True, (200, 200, 255))
            screen.blit(
                title,
                (screen_width // 2 - title.get_width() // 2, screen_height // 2 - 60),
            )

            inst_font = pygame.font.Font(None, 24)
            instructions = [
                "Press F6 to open the Database Editor",
                "",
                "The Database Editor allows you to:",
                "• Create, edit, and delete database entries",
                "• Manage Actors, Items, Skills, Enemies, and more",
                "• Search and filter entries",
                "• Duplicate existing entries",
            ]

            y_offset = screen_height // 2
            for line in instructions:
                text = inst_font.render(line, True, (180, 180, 200))
                screen.blit(text, (screen_width // 2 - text.get_width() // 2, y_offset))
                y_offset += 30

        # Render database editor
        db_editor.render()

        # Update display
        pygame.display.flip()

    # Cleanup
    pygame.quit()
    print("\n✓ Test completed")


if __name__ == "__main__":
    main()
