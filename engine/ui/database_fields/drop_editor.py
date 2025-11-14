"""
Drop Editor

Item drop table editor with probability management.
Used for configuring enemy loot drops, treasure chests, and random rewards.
"""

from typing import List, Optional

import pygame

from neonworks.engine.data.database_schema import DropItem


class DropEditor:
    """
    Visual editor for item drop tables.

    Features:
    - Add/remove drop entries
    - Configure drop rates (probability sliders)
    - Item type selection (Item, Weapon, Armor)
    - Item ID picker with preview
    - Visual probability indicators
    - Total drop rate calculation
    - Preset common/uncommon/rare rates

    Drop kinds:
    - 1: Regular Item
    - 2: Weapon
    - 3: Armor
    """

    KIND_NAMES = {
        1: "Item",
        2: "Weapon",
        3: "Armor",
    }

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.visible = False
        self.result = None

        # Current drop table
        self.drops: List[DropItem] = []

        # UI state
        self.selected_index: Optional[int] = None
        self.scroll_offset = 0
        self.active_input_field: Optional[tuple] = None  # (index, field_name)
        self.input_text = ""
        self.dragging_slider: Optional[int] = None

        # Fonts
        self.font = pygame.font.Font(None, 22)
        self.title_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 18)

        # Rarity presets
        self.rarity_presets = {
            "Common": 1.0,
            "Uncommon": 0.5,
            "Rare": 0.25,
            "Very Rare": 0.1,
            "Ultra Rare": 0.01,
        }

    def open(self, initial_drops: Optional[List[DropItem]] = None) -> None:
        """
        Open the drop editor.

        Args:
            initial_drops: Initial drop table, or None for empty
        """
        self.visible = True
        self.result = None
        self.selected_index = None
        self.scroll_offset = 0
        self.active_input_field = None
        self.input_text = ""
        self.dragging_slider = None

        if initial_drops:
            # Create copies of drop items
            self.drops = [
                DropItem(kind=d.kind, item_id=d.item_id, drop_rate=d.drop_rate)
                for d in initial_drops
            ]
        else:
            self.drops = []

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
            elif event.key == pygame.K_RETURN and self.active_input_field:
                self._apply_input()
                return True
            elif event.key == pygame.K_BACKSPACE and self.active_input_field:
                self.input_text = self.input_text[:-1]
                return True
            elif event.unicode and event.unicode.isprintable() and self.active_input_field:
                # Only allow numbers for item_id
                if event.unicode.isdigit():
                    self.input_text += event.unicode
                return True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self.dragging_slider = None

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging_slider = None

        elif event.type == pygame.MOUSEWHEEL:
            # Scroll drop list
            if event.y > 0:
                self.scroll_offset = max(0, self.scroll_offset - 1)
            else:
                self.scroll_offset = min(len(self.drops) - 1, self.scroll_offset + 1)

        return True

    def render(self) -> Optional[List[DropItem]]:
        """
        Render the drop editor.

        Returns:
            Drop table if dialog was closed with OK, None otherwise
        """
        if not self.visible:
            return self.result

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        # Dialog dimensions
        dialog_width = min(900, screen_width - 100)
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

        # Add new drop button
        add_btn_y = dialog_y + 70
        self._render_add_button(dialog_x + 20, add_btn_y, dialog_width - 40)

        # Drop list
        list_y = add_btn_y + 50
        list_height = dialog_height - 220
        self._render_drop_list(dialog_x + 20, list_y, dialog_width - 40, list_height)

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

        title_text = self.title_font.render("Drop Table Editor", True, (100, 200, 255))
        self.screen.blit(title_text, (x + 20, y + 12))

        # Drop count and total rate
        total_rate = sum(d.drop_rate for d in self.drops)
        info_text = self.small_font.render(
            f"{len(self.drops)} drops | Total rate: {total_rate:.2%}",
            True,
            (180, 180, 200)
        )
        self.screen.blit(info_text, (x + width - 250, y + 18))

    def _render_add_button(self, x: int, y: int, width: int):
        """Render add new drop button."""
        button_height = 40
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        is_hover = (
            x <= mouse_pos[0] <= x + width
            and y <= mouse_pos[1] <= y + button_height
        )
        btn_color = (0, 170, 0) if is_hover else (0, 120, 0)

        pygame.draw.rect(
            self.screen,
            btn_color,
            (x, y, width, button_height),
            border_radius=6,
        )

        btn_text = self.font.render("+ Add New Drop", True, (255, 255, 255))
        text_rect = btn_text.get_rect(center=(x + width // 2, y + button_height // 2))
        self.screen.blit(btn_text, text_rect)

        if is_hover and mouse_clicked:
            self._add_drop()

    def _render_drop_list(self, x: int, y: int, width: int, height: int):
        """Render the list of drops."""
        if not self.drops:
            # Empty message
            empty_text = self.font.render("No drops configured", True, (150, 150, 150))
            self.screen.blit(empty_text, (x + width // 2 - 100, y + height // 2))
            return

        # List background
        pygame.draw.rect(
            self.screen,
            (25, 25, 40),
            (x, y, width, height),
            border_radius=6,
        )

        current_y = y + 10
        item_height = 120
        mouse_pos = pygame.mouse.get_pos()

        visible_drops = self.drops[self.scroll_offset:]

        for i, drop in enumerate(visible_drops):
            if current_y + item_height > y + height - 10:
                break

            actual_index = i + self.scroll_offset
            is_selected = self.selected_index == actual_index

            self._render_drop_item(
                x + 10,
                current_y,
                width - 20,
                item_height - 10,
                actual_index,
                drop,
                is_selected,
                mouse_pos
            )

            current_y += item_height

        # Scroll indicators
        if self.scroll_offset > 0:
            arrow = self.font.render("▲", True, (200, 200, 200))
            self.screen.blit(arrow, (x + width - 30, y + 5))

        if len(self.drops) > len(visible_drops) + self.scroll_offset:
            arrow = self.font.render("▼", True, (200, 200, 200))
            self.screen.blit(arrow, (x + width - 30, y + height - 25))

    def _render_drop_item(
        self,
        x: int, y: int, width: int, height: int,
        index: int, drop: DropItem, is_selected: bool,
        mouse_pos: tuple
    ):
        """Render a single drop item."""
        # Background
        bg_color = (45, 60, 90) if is_selected else (35, 40, 55)
        pygame.draw.rect(
            self.screen,
            bg_color,
            (x, y, width, height),
            border_radius=6,
        )

        # Kind selector
        kind_y = y + 10
        self._render_kind_selector(x + 10, kind_y, index, drop, mouse_pos)

        # Item ID input
        id_y = kind_y + 35
        self._render_item_id_input(x + 10, id_y, 150, index, drop, mouse_pos)

        # Drop rate slider
        rate_y = id_y + 40
        self._render_rate_slider(x + 10, rate_y, width - 120, index, drop, mouse_pos)

        # Delete button
        self._render_delete_button(x + width - 100, y + height // 2 - 15, 90, 30, index, mouse_pos)

        # Rarity presets
        presets_x = x + width - 100
        presets_y = y + 10
        self._render_rarity_presets(presets_x, presets_y, index, mouse_pos)

    def _render_kind_selector(self, x: int, y: int, index: int, drop: DropItem, mouse_pos: tuple):
        """Render item kind selector buttons."""
        button_width = 70
        button_height = 26
        button_spacing = 8

        mouse_clicked = pygame.mouse.get_pressed()[0]

        for kind, name in self.KIND_NAMES.items():
            btn_x = x + (kind - 1) * (button_width + button_spacing)

            is_selected = drop.kind == kind
            is_hover = (
                btn_x <= mouse_pos[0] <= btn_x + button_width
                and y <= mouse_pos[1] <= y + button_height
            )

            # Button background
            if is_selected:
                btn_color = (80, 120, 200)
            elif is_hover:
                btn_color = (50, 70, 110)
            else:
                btn_color = (40, 50, 80)

            pygame.draw.rect(
                self.screen,
                btn_color,
                (btn_x, y, button_width, button_height),
                border_radius=4,
            )

            # Button text
            btn_text = self.small_font.render(name, True, (255, 255, 255))
            text_rect = btn_text.get_rect(
                center=(btn_x + button_width // 2, y + button_height // 2)
            )
            self.screen.blit(btn_text, text_rect)

            # Handle click
            if is_hover and mouse_clicked:
                drop.kind = kind

    def _render_item_id_input(
        self, x: int, y: int, width: int, index: int, drop: DropItem, mouse_pos: tuple
    ):
        """Render item ID input field."""
        # Label
        label = self.small_font.render("Item ID:", True, (180, 180, 200))
        self.screen.blit(label, (x, y))

        # Input box
        input_y = y + 18
        input_height = 28
        mouse_clicked = pygame.mouse.get_pressed()[0]

        is_active = self.active_input_field == (index, "item_id")
        box_color = (70, 80, 120) if is_active else (50, 50, 70)

        pygame.draw.rect(
            self.screen,
            box_color,
            (x, input_y, width, input_height),
            border_radius=3,
        )

        # Display value
        display_value = self.input_text if is_active else str(drop.item_id)
        value_surf = self.font.render(display_value, True, (255, 255, 255))
        self.screen.blit(value_surf, (x + 8, input_y + 4))

        # Handle click
        if (
            x <= mouse_pos[0] <= x + width
            and input_y <= mouse_pos[1] <= input_y + input_height
            and mouse_clicked
        ):
            self.active_input_field = (index, "item_id")
            self.input_text = str(drop.item_id)

    def _render_rate_slider(
        self, x: int, y: int, width: int, index: int, drop: DropItem, mouse_pos: tuple
    ):
        """Render drop rate slider."""
        # Label
        label = self.small_font.render(
            f"Drop Rate: {drop.drop_rate:.1%}",
            True,
            (180, 180, 200)
        )
        self.screen.blit(label, (x, y))

        # Slider
        slider_y = y + 20
        slider_height = 20

        # Background
        pygame.draw.rect(
            self.screen,
            (40, 40, 60),
            (x, slider_y, width, slider_height),
            border_radius=10,
        )

        # Fill
        fill_width = int(width * drop.drop_rate)
        # Color based on rarity
        if drop.drop_rate >= 0.5:
            fill_color = (100, 200, 100)  # Common - green
        elif drop.drop_rate >= 0.25:
            fill_color = (100, 150, 255)  # Uncommon - blue
        elif drop.drop_rate >= 0.1:
            fill_color = (200, 100, 255)  # Rare - purple
        else:
            fill_color = (255, 200, 0)  # Very rare - gold

        pygame.draw.rect(
            self.screen,
            fill_color,
            (x, slider_y, fill_width, slider_height),
            border_radius=10,
        )

        # Handle
        handle_x = x + fill_width
        handle_radius = 12
        pygame.draw.circle(
            self.screen,
            (255, 255, 255),
            (handle_x, slider_y + slider_height // 2),
            handle_radius,
        )

        # Handle interaction
        if pygame.mouse.get_pressed()[0]:
            if (
                x <= mouse_pos[0] <= x + width
                and slider_y - 10 <= mouse_pos[1] <= slider_y + slider_height + 10
            ):
                self.dragging_slider = index
                # Update rate based on mouse position
                new_rate = max(0.0, min(1.0, (mouse_pos[0] - x) / width))
                drop.drop_rate = round(new_rate, 3)

    def _render_rarity_presets(self, x: int, y: int, index: int, mouse_pos: tuple):
        """Render quick rarity preset buttons (vertical)."""
        button_width = 90
        button_height = 18
        button_spacing = 2

        mouse_clicked = pygame.mouse.get_pressed()[0]
        current_y = y

        for rarity_name, rate in self.rarity_presets.items():
            is_hover = (
                x <= mouse_pos[0] <= x + button_width
                and current_y <= mouse_pos[1] <= current_y + button_height
            )

            btn_color = (50, 70, 100) if is_hover else (35, 45, 70)

            pygame.draw.rect(
                self.screen,
                btn_color,
                (x, current_y, button_width, button_height),
                border_radius=3,
            )

            # Button text
            btn_text = self.small_font.render(
                f"{rarity_name[:6]} {rate:.0%}",
                True,
                (220, 220, 240)
            )
            text_x = x + button_width // 2 - btn_text.get_width() // 2
            self.screen.blit(btn_text, (text_x, current_y + 2))

            # Handle click
            if is_hover and mouse_clicked:
                self.drops[index].drop_rate = rate

            current_y += button_height + button_spacing

    def _render_delete_button(self, x: int, y: int, width: int, height: int, index: int, mouse_pos: tuple):
        """Render delete button for drop item."""
        mouse_clicked = pygame.mouse.get_pressed()[0]

        is_hover = (
            x <= mouse_pos[0] <= x + width
            and y <= mouse_pos[1] <= y + height
        )

        btn_color = (200, 50, 50) if is_hover else (150, 30, 30)

        pygame.draw.rect(
            self.screen,
            btn_color,
            (x, y, width, height),
            border_radius=4,
        )

        btn_text = self.small_font.render("Delete", True, (255, 255, 255))
        text_rect = btn_text.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(btn_text, text_rect)

        if is_hover and mouse_clicked:
            self._delete_drop(index)

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
            self.result = self.drops.copy()

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

    def _add_drop(self):
        """Add a new drop to the table."""
        new_drop = DropItem(kind=1, item_id=1, drop_rate=1.0)
        self.drops.append(new_drop)
        self.selected_index = len(self.drops) - 1

    def _delete_drop(self, index: int):
        """Delete a drop from the table."""
        if 0 <= index < len(self.drops):
            self.drops.pop(index)
            if self.selected_index == index:
                self.selected_index = None
            elif self.selected_index is not None and self.selected_index > index:
                self.selected_index -= 1

    def _apply_input(self):
        """Apply the current input to the active field."""
        if not self.active_input_field or not self.input_text:
            self.active_input_field = None
            return

        index, field_name = self.active_input_field

        try:
            if field_name == "item_id" and 0 <= index < len(self.drops):
                self.drops[index].item_id = int(self.input_text)
        except ValueError:
            pass  # Invalid input, ignore

        self.active_input_field = None
        self.input_text = ""

    def get_result(self) -> Optional[List[DropItem]]:
        """Get the result after the dialog is closed."""
        return self.result

    def is_visible(self) -> bool:
        """Check if the dialog is visible."""
        return self.visible
