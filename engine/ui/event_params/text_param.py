"""
Text Parameter Editor

Modal dialog for editing text with variable syntax support.
Supports \v[n] for variable references, \n[actor_id] for actor names, etc.
"""

from typing import Dict, Any, Optional, Tuple
import pygame


class TextParamEditor:
    """
    Text editor with support for RPG Maker-style escape sequences:
    - \\v[n] - Insert variable n's value
    - \\n[n] - Insert actor n's name
    - \\c[n] - Change text color to n
    - \\g - Show gold window
    - \\. - Wait 1/4 second
    - \\| - Wait 1 second
    - \\! - Wait for button input
    - \\> - Display remaining text instantly
    - \\< - Cancel instant display
    - \\^ - Don't wait for input after message
    """

    def __init__(self, screen: pygame.Surface, initial_text: str = ""):
        self.screen = screen
        self.text = initial_text
        self.cursor_pos = len(initial_text)
        self.visible = False
        self.result = None

        # UI state
        self.scroll_offset = 0
        self.selection_start = None
        self.selection_end = None

        # Font
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 32)

        # Quick insert buttons for common escape codes
        self.escape_codes = [
            ("Variable", "\\v[1]"),
            ("Actor Name", "\\n[1]"),
            ("Color", "\\c[0]"),
            ("Gold", "\\g"),
            ("Wait 1/4s", "\\."),
            ("Wait 1s", "\\|"),
            ("Wait Input", "\\!"),
            ("Instant", "\\>"),
            ("Cancel Instant", "\\<"),
            ("No Wait", "\\^"),
        ]

    def open(self, initial_text: str = "") -> Optional[str]:
        """
        Open the text editor dialog.

        Args:
            initial_text: Initial text content

        Returns:
            Edited text if confirmed, None if cancelled
        """
        self.text = initial_text
        self.cursor_pos = len(initial_text)
        self.visible = True
        self.result = None
        self.scroll_offset = 0
        self.selection_start = None
        self.selection_end = None
        return None

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events.

        Args:
            event: Pygame event

        Returns:
            True if editor is still open, False if closed
        """
        if not self.visible:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Cancel
                self.visible = False
                self.result = None
                return False
            elif event.key == pygame.K_RETURN and pygame.key.get_mods() & pygame.KMOD_CTRL:
                # Confirm with Ctrl+Enter
                self.visible = False
                self.result = self.text
                return False
            elif event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
            elif event.key == pygame.K_DELETE:
                if self.cursor_pos < len(self.text):
                    self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos + 1:]
            elif event.key == pygame.K_LEFT:
                self.cursor_pos = max(0, self.cursor_pos - 1)
            elif event.key == pygame.K_RIGHT:
                self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
            elif event.key == pygame.K_HOME:
                self.cursor_pos = 0
            elif event.key == pygame.K_END:
                self.cursor_pos = len(self.text)
            elif event.key == pygame.K_RETURN:
                # Insert newline
                self.text = self.text[:self.cursor_pos] + "\n" + self.text[self.cursor_pos:]
                self.cursor_pos += 1
            elif event.unicode and event.unicode.isprintable():
                # Insert character
                self.text = self.text[:self.cursor_pos] + event.unicode + self.text[self.cursor_pos:]
                self.cursor_pos += 1

        return True

    def render(self) -> Optional[str]:
        """
        Render the text editor dialog.

        Returns:
            Result text if dialog was closed with OK, None otherwise
        """
        if not self.visible:
            return self.result

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        # Dialog dimensions
        dialog_width = min(800, screen_width - 100)
        dialog_height = min(600, screen_height - 100)
        dialog_x = (screen_width - dialog_width) // 2
        dialog_y = (screen_height - dialog_height) // 2

        # Semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Dialog background
        pygame.draw.rect(
            self.screen,
            (30, 30, 45),
            (dialog_x, dialog_y, dialog_width, dialog_height),
            border_radius=8,
        )
        pygame.draw.rect(
            self.screen,
            (80, 80, 100),
            (dialog_x, dialog_y, dialog_width, dialog_height),
            2,
            border_radius=8,
        )

        # Title bar
        title_height = 50
        pygame.draw.rect(
            self.screen,
            (40, 40, 60),
            (dialog_x, dialog_y, dialog_width, title_height),
            border_radius=8,
        )
        title_text = self.title_font.render("Text Editor", True, (255, 200, 0))
        self.screen.blit(title_text, (dialog_x + 20, dialog_y + 12))

        # Help text
        help_font = pygame.font.Font(None, 18)
        help_text = help_font.render("Ctrl+Enter to confirm, Esc to cancel", True, (150, 150, 150))
        self.screen.blit(help_text, (dialog_x + dialog_width - 280, dialog_y + 18))

        # Text input area
        input_y = dialog_y + title_height + 20
        input_height = dialog_height - title_height - 150
        input_padding = 15

        pygame.draw.rect(
            self.screen,
            (20, 20, 30),
            (dialog_x + 10, input_y, dialog_width - 20, input_height),
            border_radius=6,
        )
        pygame.draw.rect(
            self.screen,
            (60, 60, 80),
            (dialog_x + 10, input_y, dialog_width - 20, input_height),
            2,
            border_radius=6,
        )

        # Render text content with cursor
        self._render_text_content(
            dialog_x + 10 + input_padding,
            input_y + input_padding,
            dialog_width - 20 - input_padding * 2,
            input_height - input_padding * 2,
        )

        # Escape code quick insert buttons
        button_y = input_y + input_height + 20
        self._render_escape_buttons(dialog_x + 10, button_y, dialog_width - 20)

        # Bottom buttons (OK/Cancel)
        self._render_bottom_buttons(
            dialog_x + dialog_width - 220,
            dialog_y + dialog_height - 50,
        )

        return None

    def _render_text_content(self, x: int, y: int, width: int, height: int):
        """Render the text content with cursor."""
        line_height = 26
        lines = self.text.split("\n")

        # Calculate cursor line and column
        cursor_line = 0
        cursor_col = 0
        char_count = 0

        for i, line in enumerate(lines):
            if char_count + len(line) >= self.cursor_pos:
                cursor_line = i
                cursor_col = self.cursor_pos - char_count
                break
            char_count += len(line) + 1  # +1 for newline

        # Render lines
        current_y = y
        for i, line in enumerate(lines):
            if current_y + line_height > y + height:
                break

            # Render line text
            if line:
                text_surface = self.font.render(line, True, (255, 255, 255))
                # Truncate if too wide
                if text_surface.get_width() > width:
                    # Simple truncation - could be improved with horizontal scrolling
                    truncated_line = line[:int(len(line) * width / text_surface.get_width())]
                    text_surface = self.font.render(truncated_line + "...", True, (255, 255, 255))
                self.screen.blit(text_surface, (x, current_y))

            # Render cursor on the current line
            if i == cursor_line:
                cursor_x = x
                if cursor_col > 0:
                    text_before_cursor = line[:cursor_col]
                    cursor_x += self.font.size(text_before_cursor)[0]

                # Blinking cursor
                if pygame.time.get_ticks() % 1000 < 500:
                    pygame.draw.rect(
                        self.screen,
                        (255, 200, 0),
                        (cursor_x, current_y, 2, line_height - 2),
                    )

            current_y += line_height

    def _render_escape_buttons(self, x: int, y: int, width: int):
        """Render quick insert buttons for escape codes."""
        button_width = 120
        button_height = 28
        button_spacing = 8
        buttons_per_row = width // (button_width + button_spacing)

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        for i, (label, code) in enumerate(self.escape_codes):
            row = i // buttons_per_row
            col = i % buttons_per_row

            btn_x = x + col * (button_width + button_spacing)
            btn_y = y + row * (button_height + button_spacing)

            # Check hover
            is_hover = (
                btn_x <= mouse_pos[0] <= btn_x + button_width
                and btn_y <= mouse_pos[1] <= btn_y + button_height
            )

            btn_color = (60, 80, 120) if is_hover else (40, 50, 80)

            pygame.draw.rect(
                self.screen,
                btn_color,
                (btn_x, btn_y, button_width, button_height),
                border_radius=4,
            )

            # Button text
            btn_font = pygame.font.Font(None, 18)
            btn_text = btn_font.render(label, True, (255, 255, 255))
            text_rect = btn_text.get_rect(center=(btn_x + button_width // 2, btn_y + button_height // 2))
            self.screen.blit(btn_text, text_rect)

            # Handle click
            if is_hover and mouse_clicked:
                self.insert_code(code)

    def _render_bottom_buttons(self, x: int, y: int):
        """Render OK and Cancel buttons."""
        button_width = 100
        button_height = 40
        button_spacing = 10

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        # OK button
        ok_hover = (
            x <= mouse_pos[0] <= x + button_width
            and y <= mouse_pos[1] <= y + button_height
        )
        ok_color = (0, 150, 0) if ok_hover else (0, 120, 0)

        pygame.draw.rect(
            self.screen,
            ok_color,
            (x, y, button_width, button_height),
            border_radius=6,
        )

        ok_text = self.font.render("OK", True, (255, 255, 255))
        ok_rect = ok_text.get_rect(center=(x + button_width // 2, y + button_height // 2))
        self.screen.blit(ok_text, ok_rect)

        if ok_hover and mouse_clicked:
            self.visible = False
            self.result = self.text

        # Cancel button
        cancel_x = x + button_width + button_spacing
        cancel_hover = (
            cancel_x <= mouse_pos[0] <= cancel_x + button_width
            and y <= mouse_pos[1] <= y + button_height
        )
        cancel_color = (150, 50, 50) if cancel_hover else (120, 30, 30)

        pygame.draw.rect(
            self.screen,
            cancel_color,
            (cancel_x, y, button_width, button_height),
            border_radius=6,
        )

        cancel_text = self.font.render("Cancel", True, (255, 255, 255))
        cancel_rect = cancel_text.get_rect(center=(cancel_x + button_width // 2, y + button_height // 2))
        self.screen.blit(cancel_text, cancel_rect)

        if cancel_hover and mouse_clicked:
            self.visible = False
            self.result = None

    def insert_code(self, code: str):
        """Insert an escape code at the cursor position."""
        self.text = self.text[:self.cursor_pos] + code + self.text[self.cursor_pos:]
        self.cursor_pos += len(code)

    def get_result(self) -> Optional[str]:
        """Get the result after the dialog is closed."""
        return self.result

    def is_visible(self) -> bool:
        """Check if the dialog is visible."""
        return self.visible
