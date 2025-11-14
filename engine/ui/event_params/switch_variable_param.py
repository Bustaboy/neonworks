"""
Switch/Variable Parameter Editor

Modal dialog for selecting switches and variables with custom naming support.
"""

from typing import Any, Dict, Optional, Tuple

import pygame


class SwitchVariableParamEditor:
    """
    Picker for switches and variables.

    Supports:
    - Switch selection (1-999)
    - Variable selection (1-999)
    - Range selection (for batch operations)
    - Custom naming/descriptions
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.visible = False
        self.result = None

        # Picker mode: "switch" or "variable"
        self.mode = "switch"

        # Allow range selection
        self.allow_range = False

        # Selection state
        self.selected_id = 1
        self.range_end_id = None

        # Custom names for switches/variables (can be loaded from game data)
        self.switch_names: Dict[int, str] = {}
        self.variable_names: Dict[int, str] = {}

        # UI state
        self.scroll_offset = 0
        self.items_per_page = 15

        # Fonts
        self.font = pygame.font.Font(None, 22)
        self.title_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 18)

    def open(
        self,
        mode: str = "switch",
        initial_id: int = 1,
        allow_range: bool = False,
        range_end: Optional[int] = None,
    ) -> None:
        """
        Open the switch/variable picker.

        Args:
            mode: "switch" or "variable"
            initial_id: Initially selected ID
            allow_range: Allow range selection
            range_end: Initial range end ID (if allow_range is True)
        """
        self.visible = True
        self.result = None
        self.mode = mode
        self.allow_range = allow_range
        self.selected_id = initial_id
        self.range_end_id = range_end if allow_range else None
        self.scroll_offset = max(0, initial_id - 5)

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
            elif event.key == pygame.K_UP:
                self.selected_id = max(1, self.selected_id - 1)
                if self.selected_id < self.scroll_offset + 1:
                    self.scroll_offset = max(0, self.scroll_offset - 1)
            elif event.key == pygame.K_DOWN:
                self.selected_id = min(999, self.selected_id + 1)
                if self.selected_id > self.scroll_offset + self.items_per_page:
                    self.scroll_offset = min(999 - self.items_per_page, self.scroll_offset + 1)
            elif event.key == pygame.K_RETURN:
                # Confirm selection
                self._confirm_selection()
                return False
        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0:  # Scroll up
                self.scroll_offset = max(0, self.scroll_offset - 1)
            elif event.y < 0:  # Scroll down
                self.scroll_offset = min(999 - self.items_per_page, self.scroll_offset + 1)

        return True

    def render(self) -> Optional[Dict[str, Any]]:
        """
        Render the switch/variable picker.

        Returns:
            Result data if dialog was closed with OK, None otherwise
        """
        if not self.visible:
            return self.result

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        # Dialog dimensions
        dialog_width = min(600, screen_width - 100)
        dialog_height = min(700, screen_height - 100)
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
        title_text = f"Select {self.mode.title()}"
        title_surface = self.title_font.render(title_text, True, (255, 200, 0))
        self.screen.blit(title_surface, (dialog_x + 20, dialog_y + 12))

        # Info text
        info_text = "Use arrow keys or click to select"
        if self.allow_range:
            info_text += " (range selection enabled)"
        info_surface = self.small_font.render(info_text, True, (150, 150, 150))
        self.screen.blit(info_surface, (dialog_x + 20, dialog_y + title_height + 5))

        # List area
        list_y = dialog_y + title_height + 35
        list_height = dialog_height - title_height - 125

        self._render_list(dialog_x + 10, list_y, dialog_width - 20, list_height)

        # Range selector (if enabled)
        if self.allow_range:
            range_y = list_y + list_height + 10
            self._render_range_selector(dialog_x + 10, range_y, dialog_width - 20)

        # Bottom buttons
        self._render_bottom_buttons(
            dialog_x + dialog_width - 220,
            dialog_y + dialog_height - 60,
        )

        return None

    def _render_list(self, x: int, y: int, width: int, height: int):
        """Render the scrollable list of switches/variables."""
        # List background
        pygame.draw.rect(
            self.screen,
            (25, 25, 38),
            (x, y, width, height),
            border_radius=6,
        )
        pygame.draw.rect(
            self.screen,
            (60, 60, 80),
            (x, y, width, height),
            2,
            border_radius=6,
        )

        # Render items
        item_height = 40
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        names_dict = self.switch_names if self.mode == "switch" else self.variable_names

        for i in range(self.items_per_page):
            item_id = self.scroll_offset + i + 1
            if item_id > 999:
                break

            item_y = y + 5 + i * (item_height + 2)

            is_selected = item_id == self.selected_id
            is_in_range = (
                self.allow_range
                and self.range_end_id is not None
                and min(self.selected_id, self.range_end_id)
                <= item_id
                <= max(self.selected_id, self.range_end_id)
            )
            is_hover = (
                x + 5 <= mouse_pos[0] <= x + width - 5
                and item_y <= mouse_pos[1] <= item_y + item_height
            )

            # Item background
            if is_selected:
                item_color = (70, 100, 160)
            elif is_in_range:
                item_color = (50, 70, 110)
            elif is_hover:
                item_color = (50, 50, 75)
            else:
                item_color = (35, 35, 50)

            pygame.draw.rect(
                self.screen,
                item_color,
                (x + 5, item_y, width - 10, item_height),
                border_radius=4,
            )

            # Item ID
            id_text = self.font.render(f"#{item_id:03d}", True, (255, 200, 0))
            self.screen.blit(id_text, (x + 15, item_y + 10))

            # Item name/description
            name = names_dict.get(item_id, f"(Unnamed {self.mode.title()})")
            name_text = self.font.render(name, True, (220, 220, 240))
            # Truncate if too long
            if name_text.get_width() > width - 120:
                name = name[:30] + "..."
                name_text = self.font.render(name, True, (220, 220, 240))
            self.screen.blit(name_text, (x + 90, item_y + 10))

            # Handle click
            if is_hover and mouse_clicked:
                if self.allow_range and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    # Shift-click for range end
                    self.range_end_id = item_id
                else:
                    self.selected_id = item_id
                    if not self.allow_range:
                        self.range_end_id = None

        # Scroll indicators
        if self.scroll_offset > 0:
            arrow_text = self.font.render("▲", True, (200, 200, 200))
            self.screen.blit(arrow_text, (x + width - 30, y + 5))

        if self.scroll_offset + self.items_per_page < 999:
            arrow_text = self.font.render("▼", True, (200, 200, 200))
            self.screen.blit(arrow_text, (x + width - 30, y + height - 25))

    def _render_range_selector(self, x: int, y: int, width: int):
        """Render the range selector controls."""
        height = 45
        pygame.draw.rect(
            self.screen,
            (25, 25, 38),
            (x, y, width, height),
            border_radius=6,
        )

        # Range display
        label = self.font.render("Range:", True, (200, 200, 220))
        self.screen.blit(label, (x + 10, y + 12))

        if self.range_end_id is not None:
            start = min(self.selected_id, self.range_end_id)
            end = max(self.selected_id, self.range_end_id)
            range_text = f"{start:03d} - {end:03d} ({end - start + 1} items)"
        else:
            range_text = f"{self.selected_id:03d} (single)"

        range_surface = self.font.render(range_text, True, (255, 255, 255))
        self.screen.blit(range_surface, (x + 80, y + 12))

        # Clear range button
        if self.range_end_id is not None:
            btn_x = x + width - 110
            btn_width = 100
            btn_height = 30
            mouse_pos = pygame.mouse.get_pos()
            mouse_clicked = pygame.mouse.get_pressed()[0]

            is_hover = (
                btn_x <= mouse_pos[0] <= btn_x + btn_width
                and y + 7 <= mouse_pos[1] <= y + 7 + btn_height
            )

            btn_color = (120, 80, 80) if is_hover else (80, 50, 50)
            pygame.draw.rect(
                self.screen,
                btn_color,
                (btn_x, y + 7, btn_width, btn_height),
                border_radius=4,
            )

            btn_text = self.small_font.render("Clear Range", True, (255, 255, 255))
            btn_rect = btn_text.get_rect(center=(btn_x + btn_width // 2, y + 7 + btn_height // 2))
            self.screen.blit(btn_text, btn_rect)

            if is_hover and mouse_clicked:
                self.range_end_id = None

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
            self._confirm_selection()

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

    def _confirm_selection(self):
        """Confirm the current selection and close the dialog."""
        self.visible = False
        result = {
            "id": self.selected_id,
            "mode": self.mode,
        }

        if self.allow_range and self.range_end_id is not None:
            result["end_id"] = self.range_end_id

        self.result = result

    def set_names(self, names: Dict[int, str], mode: str = "switch"):
        """
        Set custom names for switches or variables.

        Args:
            names: Dictionary mapping ID to name
            mode: "switch" or "variable"
        """
        if mode == "switch":
            self.switch_names = names
        else:
            self.variable_names = names

    def get_result(self) -> Optional[Dict[str, Any]]:
        """Get the result after the dialog is closed."""
        return self.result

    def is_visible(self) -> bool:
        """Check if the dialog is visible."""
        return self.visible
