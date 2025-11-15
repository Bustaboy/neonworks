"""
Formula Editor

Damage formula editor with syntax help and validation.
Supports creating complex damage formulas using actor/enemy stats and variables.
"""

from typing import List, Optional

import pygame


class FormulaEditor:
    """
    Formula editor with syntax highlighting and helper buttons.

    Supported formula syntax:
    - a.atk, a.def, a.mat, a.mdf, a.agi, a.luk - Attacker stats
    - b.atk, b.def, b.mat, b.mdf, b.agi, b.luk - Target stats
    - a.hp, a.mp, a.level - Attacker attributes
    - b.hp, b.mp, b.level - Target attributes
    - v[n] - Game variable n
    - Math operations: +, -, *, /, %, ^, ( )
    - Functions: max(), min(), abs(), floor(), ceil()

    Examples:
    - "a.atk * 4 - b.def * 2" - Physical damage formula
    - "a.mat * 3 + a.level * 2" - Magic damage scaling with level
    - "max(a.atk - b.def, 0) * 4" - Damage with minimum 0
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.visible = False
        self.result = None

        # Formula text
        self.formula = ""
        self.cursor_pos = 0

        # UI state
        self.scroll_offset = 0
        self.validation_message = ""

        # Fonts
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 18)
        self.code_font = pygame.font.Font(None, 22)

        # Quick insert buttons for common formula elements
        self.formula_elements = [
            (
                "Attacker",
                [
                    ("a.atk", "Attack Power"),
                    ("a.def", "Defense"),
                    ("a.mat", "Magic Attack"),
                    ("a.mdf", "Magic Defense"),
                    ("a.agi", "Agility"),
                    ("a.luk", "Luck"),
                    ("a.hp", "Current HP"),
                    ("a.mp", "Current MP"),
                    ("a.level", "Level"),
                ],
            ),
            (
                "Target",
                [
                    ("b.atk", "Attack Power"),
                    ("b.def", "Defense"),
                    ("b.mat", "Magic Attack"),
                    ("b.mdf", "Magic Defense"),
                    ("b.agi", "Agility"),
                    ("b.luk", "Luck"),
                    ("b.hp", "Current HP"),
                    ("b.mp", "Current MP"),
                    ("b.level", "Level"),
                ],
            ),
            (
                "Functions",
                [
                    ("max(", "Maximum value"),
                    ("min(", "Minimum value"),
                    ("abs(", "Absolute value"),
                    ("floor(", "Round down"),
                    ("ceil(", "Round up"),
                ],
            ),
            (
                "Templates",
                [
                    ("a.atk * 4 - b.def * 2", "Physical"),
                    ("a.mat * 3 - b.mdf * 2", "Magical"),
                    ("a.atk * 2 + a.level", "Level scaling"),
                    ("max(a.atk - b.def, 0) * 4", "Min 0 damage"),
                ],
            ),
        ]

    def open(self, initial_formula: str = "") -> None:
        """
        Open the formula editor.

        Args:
            initial_formula: Formula to edit, or empty for new
        """
        self.visible = True
        self.result = None
        self.formula = initial_formula
        self.cursor_pos = len(initial_formula)
        self.scroll_offset = 0
        self.validation_message = ""
        self._validate_formula()

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
                self.visible = False
                self.result = None
                return False
            elif event.key == pygame.K_RETURN and pygame.key.get_mods() & pygame.KMOD_CTRL:
                # Confirm with Ctrl+Enter
                if self._validate_formula():
                    self.visible = False
                    self.result = self.formula
                return False
            elif event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.formula = (
                        self.formula[: self.cursor_pos - 1] + self.formula[self.cursor_pos :]
                    )
                    self.cursor_pos -= 1
                    self._validate_formula()
            elif event.key == pygame.K_DELETE:
                if self.cursor_pos < len(self.formula):
                    self.formula = (
                        self.formula[: self.cursor_pos] + self.formula[self.cursor_pos + 1 :]
                    )
                    self._validate_formula()
            elif event.key == pygame.K_LEFT:
                self.cursor_pos = max(0, self.cursor_pos - 1)
            elif event.key == pygame.K_RIGHT:
                self.cursor_pos = min(len(self.formula), self.cursor_pos + 1)
            elif event.key == pygame.K_HOME:
                self.cursor_pos = 0
            elif event.key == pygame.K_END:
                self.cursor_pos = len(self.formula)
            elif event.unicode and event.unicode.isprintable():
                # Insert character
                self.formula = (
                    self.formula[: self.cursor_pos]
                    + event.unicode
                    + self.formula[self.cursor_pos :]
                )
                self.cursor_pos += 1
                self._validate_formula()

        return True

    def render(self) -> Optional[str]:
        """
        Render the formula editor.

        Returns:
            Formula string if dialog was closed with OK, None otherwise
        """
        if not self.visible:
            return self.result

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        # Dialog dimensions
        dialog_width = min(1000, screen_width - 100)
        dialog_height = min(750, screen_height - 100)
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
        self._render_title_bar(dialog_x, dialog_y, dialog_width)

        # Formula input area
        input_y = dialog_y + 70
        self._render_formula_input(dialog_x + 20, input_y, dialog_width - 40)

        # Validation message
        validation_y = input_y + 120
        self._render_validation(dialog_x + 20, validation_y, dialog_width - 40)

        # Helper buttons
        helpers_y = validation_y + 50
        self._render_helper_buttons(dialog_x + 20, helpers_y, dialog_width - 40)

        # Bottom buttons
        self._render_bottom_buttons(
            dialog_x + dialog_width - 220,
            dialog_y + dialog_height - 60,
        )

        return None

    def _render_title_bar(self, x: int, y: int, width: int):
        """Render the title bar."""
        title_height = 50
        pygame.draw.rect(
            self.screen,
            (40, 40, 60),
            (x, y, width, title_height),
            border_radius=8,
        )

        title_text = self.title_font.render("Damage Formula Editor", True, (100, 200, 255))
        self.screen.blit(title_text, (x + 20, y + 12))

        # Help text
        help_text = self.small_font.render(
            "Ctrl+Enter to confirm | a=attacker, b=target", True, (150, 150, 150)
        )
        self.screen.blit(help_text, (x + width - 320, y + 18))

    def _render_formula_input(self, x: int, y: int, width: int):
        """Render the formula input text box."""
        # Label
        label = self.font.render("Formula:", True, (200, 200, 255))
        self.screen.blit(label, (x, y))

        # Input box
        input_y = y + 30
        input_height = 80
        pygame.draw.rect(
            self.screen,
            (20, 20, 35),
            (x, input_y, width, input_height),
            border_radius=6,
        )
        pygame.draw.rect(
            self.screen,
            (80, 100, 150),
            (x, input_y, width, input_height),
            2,
            border_radius=6,
        )

        # Formula text with syntax coloring
        self._render_formula_text(x + 10, input_y + 10, width - 20, input_height - 20)

    def _render_formula_text(self, x: int, y: int, width: int, height: int):
        """Render formula text with basic syntax highlighting."""
        if not self.formula:
            # Placeholder text
            placeholder = self.small_font.render(
                "Enter damage formula (e.g., a.atk * 4 - b.def * 2)", True, (120, 120, 140)
            )
            self.screen.blit(placeholder, (x, y + 5))
            return

        # Simple rendering - could be enhanced with syntax highlighting
        formula_surf = self.code_font.render(self.formula, True, (255, 255, 255))

        # Truncate if too wide
        if formula_surf.get_width() > width:
            # Show end of formula if cursor is at end
            if self.cursor_pos >= len(self.formula) - 10:
                # Calculate how much to offset
                offset = formula_surf.get_width() - width + 20
                self.screen.blit(formula_surf, (x - offset, y + 5))
            else:
                # Clip to width
                clip_rect = pygame.Rect(0, 0, width, formula_surf.get_height())
                self.screen.blit(formula_surf, (x, y + 5), clip_rect)
        else:
            self.screen.blit(formula_surf, (x, y + 5))

        # Render cursor
        if pygame.time.get_ticks() % 1000 < 500:
            # Calculate cursor position
            text_before_cursor = self.formula[: self.cursor_pos]
            cursor_x_offset = self.code_font.size(text_before_cursor)[0]

            # Adjust if scrolled
            if formula_surf.get_width() > width and self.cursor_pos >= len(self.formula) - 10:
                offset = formula_surf.get_width() - width + 20
                cursor_x_offset -= offset

            cursor_x = x + cursor_x_offset
            pygame.draw.rect(
                self.screen,
                (255, 200, 0),
                (cursor_x, y + 5, 2, 24),
            )

    def _render_validation(self, x: int, y: int, width: int):
        """Render validation status."""
        if not self.validation_message:
            return

        # Validation box
        box_height = 30
        is_valid = "Valid" in self.validation_message
        box_color = (20, 60, 20) if is_valid else (60, 20, 20)

        pygame.draw.rect(
            self.screen,
            box_color,
            (x, y, width, box_height),
            border_radius=4,
        )

        # Message text
        text_color = (100, 255, 100) if is_valid else (255, 100, 100)
        msg_surf = self.small_font.render(self.validation_message, True, text_color)
        self.screen.blit(msg_surf, (x + 10, y + 7))

    def _render_helper_buttons(self, x: int, y: int, width: int):
        """Render helper buttons for quick insertion."""
        # Section title
        title = self.font.render("Quick Insert", True, (200, 200, 255))
        self.screen.blit(title, (x, y))

        current_y = y + 30
        button_width = 110
        button_height = 28
        button_spacing = 6

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        for category_name, elements in self.formula_elements:
            # Category label
            cat_label = self.small_font.render(category_name, True, (180, 180, 200))
            self.screen.blit(cat_label, (x, current_y))
            current_y += 22

            # Buttons
            buttons_per_row = (width - 20) // (button_width + button_spacing)
            for i, (code, tooltip) in enumerate(elements):
                col = i % buttons_per_row
                row = i // buttons_per_row

                btn_x = x + col * (button_width + button_spacing)
                btn_y = current_y + row * (button_height + button_spacing)

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
                btn_text = self.small_font.render(code[:12], True, (255, 255, 255))
                text_rect = btn_text.get_rect(
                    center=(btn_x + button_width // 2, btn_y + button_height // 2)
                )
                self.screen.blit(btn_text, text_rect)

                # Handle click
                if is_hover and mouse_clicked:
                    self._insert_code(code)

                # Tooltip on hover
                if is_hover:
                    self._render_tooltip(mouse_pos[0], mouse_pos[1] - 30, tooltip)

            # Calculate rows for spacing
            rows = (len(elements) + buttons_per_row - 1) // buttons_per_row
            current_y += rows * (button_height + button_spacing) + 15

    def _render_tooltip(self, x: int, y: int, text: str):
        """Render a tooltip."""
        tooltip_width = 150
        tooltip_height = 25

        pygame.draw.rect(
            self.screen,
            (40, 40, 60),
            (x, y, tooltip_width, tooltip_height),
            border_radius=4,
        )

        tooltip_surf = self.small_font.render(text, True, (255, 255, 200))
        self.screen.blit(tooltip_surf, (x + 5, y + 5))

    def _render_bottom_buttons(self, x: int, y: int):
        """Render OK and Cancel buttons."""
        button_width = 100
        button_height = 40
        button_spacing = 10

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        # OK button
        ok_hover = x <= mouse_pos[0] <= x + button_width and y <= mouse_pos[1] <= y + button_height
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
            if self._validate_formula():
                self.visible = False
                self.result = self.formula

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
        cancel_rect = cancel_text.get_rect(
            center=(cancel_x + button_width // 2, y + button_height // 2)
        )
        self.screen.blit(cancel_text, cancel_rect)

        if cancel_hover and mouse_clicked:
            self.visible = False
            self.result = None

    def _insert_code(self, code: str):
        """Insert code at cursor position."""
        self.formula = self.formula[: self.cursor_pos] + code + self.formula[self.cursor_pos :]
        self.cursor_pos += len(code)
        self._validate_formula()

    def _validate_formula(self) -> bool:
        """
        Validate the formula syntax.

        Returns:
            True if valid, False otherwise
        """
        if not self.formula:
            self.validation_message = ""
            return False

        # Basic syntax checking
        # Check for balanced parentheses
        open_count = self.formula.count("(")
        close_count = self.formula.count(")")

        if open_count != close_count:
            self.validation_message = "Error: Unbalanced parentheses"
            return False

        # Check for valid characters (allow letters, numbers, operators, dots, parentheses)
        valid_chars = set(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+-*/%.^()[] ,"
        )
        if not all(c in valid_chars for c in self.formula):
            self.validation_message = "Error: Invalid characters in formula"
            return False

        # Check for common patterns
        if ".." in self.formula or "//" in self.formula or "**" in self.formula:
            self.validation_message = "Error: Invalid operator sequence"
            return False

        self.validation_message = "✓ Valid formula syntax"
        return True

    def get_result(self) -> Optional[str]:
        """Get the result after the dialog is closed."""
        return self.result

    def is_visible(self) -> bool:
        """Check if the dialog is visible."""
        return self.visible
