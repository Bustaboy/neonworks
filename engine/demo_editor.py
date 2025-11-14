"""
NeonWorks Event Editor Demo

Standalone demo application to test the event editor and level builder.

Usage:
    python -m engine.demo_editor

Controls:
    F5 - Toggle Event Editor
    F6 - Toggle Level Builder
    F1 - Show Help
    ESC - Close active UI / Quit
"""

import sys
from pathlib import Path

import pygame

from engine.ui.master_ui_manager import MasterUIManager


class EditorDemo:
    """Demo application for testing the event editor."""

    def __init__(self):
        print("🎮 NeonWorks Event Editor Demo")
        print("=" * 50)

        # Initialize Pygame
        pygame.init()

        # Setup display
        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("NeonWorks Event Editor - Press F1 for Help")

        # Setup clock
        self.clock = pygame.time.Clock()
        self.target_fps = 60

        # UI Manager
        self.ui_manager = MasterUIManager(self.screen)

        # Running flag
        self.running = True

        # Show initial help
        self.ui_manager.show_help()
        print("\n✓ Demo initialized. Press F1 anytime to show help again.")

    def run(self):
        """Main game loop."""
        while self.running:
            delta_time = self.clock.tick(self.target_fps) / 1000.0

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break

                # F1 for help
                if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
                    self.ui_manager.show_help()
                    continue

                # ESC to quit if no UI is active
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if not self.ui_manager.is_any_ui_active():
                        print("\n👋 Exiting demo...")
                        self.running = False
                        break

                # Let UI manager handle the event
                self.ui_manager.handle_event(event)

            # Update
            self.ui_manager.update(delta_time)

            # Render
            self.screen.fill((20, 20, 30))  # Dark background

            # Draw background pattern if no UI is active
            if not self.ui_manager.is_any_ui_active():
                self._draw_background()

            # Render UI
            self.ui_manager.render()

            # Update display
            pygame.display.flip()

        # Cleanup
        pygame.quit()
        print("✓ Demo closed successfully")

    def _draw_background(self):
        """Draw a simple background when no UI is active."""
        # Draw centered text
        font = pygame.font.Font(None, 48)
        title = font.render("NeonWorks Event Editor", True, (100, 150, 255))
        title_rect = title.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 - 50)
        )
        self.screen.blit(title, title_rect)

        # Instructions
        font_small = pygame.font.Font(None, 24)
        instructions = [
            "Press F5 to open Event Editor",
            "Press F6 to open Level Builder",
            "Press F1 for Help",
            "Press ESC to Exit",
        ]

        y = self.screen_height // 2 + 20
        for instruction in instructions:
            text = font_small.render(instruction, True, (180, 180, 200))
            text_rect = text.get_rect(center=(self.screen_width // 2, y))
            self.screen.blit(text, text_rect)
            y += 35


def main():
    """Entry point for the demo."""
    try:
        demo = EditorDemo()
        demo.run()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
