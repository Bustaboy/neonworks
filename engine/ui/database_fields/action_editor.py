"""
Action Editor

Enemy AI action pattern editor.
Configures enemy behavior in battle with condition-based skill selection.
"""

from typing import Dict, List, Optional

import pygame


class ActionEditor:
    """
    Editor for enemy AI action patterns.

    Features:
    - Add/remove action patterns
    - Skill ID selection
    - Condition configuration (HP%, MP%, state, turn)
    - Priority/rating system
    - Action probability weights

    Action structure:
    {
        "skill_id": int,         # Skill to use
        "condition_type": int,   # 0=always, 1=turn, 2=hp%, 3=mp%, 4=state, 5=party level, 6=switch
        "condition_param1": int, # First condition parameter
        "condition_param2": int, # Second condition parameter
        "rating": int,           # Priority rating (1-10)
    }

    Condition types:
    - 0: Always (no conditions)
    - 1: Turn X (turn number)
    - 2: HP X% ~ Y% (HP percentage range)
    - 3: MP X% ~ Y% (MP percentage range)
    - 4: Has State X (state ID)
    - 5: Party Level >= X
    - 6: Switch X is ON
    """

    CONDITION_TYPES = {
        0: "Always",
        1: "Turn #",
        2: "HP %",
        3: "MP %",
        4: "Has State",
        5: "Party Lv >=",
        6: "Switch ON",
    }

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.visible = False
        self.result = None

        # Current action patterns
        self.actions: List[Dict] = []

        # UI state
        self.selected_index: Optional[int] = None
        self.scroll_offset = 0
        self.active_input_field: Optional[tuple] = None  # (index, field_name)
        self.input_text = ""

        # Fonts
        self.font = pygame.font.Font(None, 22)
        self.title_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 18)

    def open(self, initial_actions: Optional[List[Dict]] = None) -> None:
        """
        Open the action editor.

        Args:
            initial_actions: Initial action patterns, or None for empty
        """
        self.visible = True
        self.result = None
        self.selected_index = None
        self.scroll_offset = 0
        self.active_input_field = None
        self.input_text = ""

        if initial_actions:
            # Create copies of actions
            self.actions = [action.copy() for action in initial_actions]
        else:
            self.actions = []

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
                # Only allow numbers for numeric fields
                if event.unicode.isdigit():
                    self.input_text += event.unicode
                return True

        elif event.type == pygame.MOUSEWHEEL:
            # Scroll action list
            if event.y > 0:
                self.scroll_offset = max(0, self.scroll_offset - 1)
            else:
                self.scroll_offset = min(max(0, len(self.actions) - 3), self.scroll_offset + 1)

        return True

    def render(self) -> Optional[List[Dict]]:
        """
        Render the action editor.

        Returns:
            Action list if dialog was closed with OK, None otherwise
        """
        if not self.visible:
            return self.result

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        # Dialog dimensions
        dialog_width = min(950, screen_width - 100)
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

        # Add new action button
        add_btn_y = dialog_y + 70
        self._render_add_button(dialog_x + 20, add_btn_y, dialog_width - 40)

        # Action list
        list_y = add_btn_y + 50
        list_height = dialog_height - 220
        self._render_action_list(dialog_x + 20, list_y, dialog_width - 40, list_height)

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

        title_text = self.title_font.render("Enemy AI Actions", True, (100, 200, 255))
        self.screen.blit(title_text, (x + 20, y + 12))

        # Action count
        info_text = self.small_font.render(
            f"{len(self.actions)} action patterns configured",
            True,
            (180, 180, 200)
        )
        self.screen.blit(info_text, (x + width - 270, y + 18))

    def _render_add_button(self, x: int, y: int, width: int):
        """Render add new action button."""
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

        btn_text = self.font.render("+ Add New Action", True, (255, 255, 255))
        text_rect = btn_text.get_rect(center=(x + width // 2, y + button_height // 2))
        self.screen.blit(btn_text, text_rect)

        if is_hover and mouse_clicked:
            self._add_action()

    def _render_action_list(self, x: int, y: int, width: int, height: int):
        """Render the list of actions."""
        if not self.actions:
            # Empty message
            empty_text = self.font.render("No actions configured", True, (150, 150, 150))
            self.screen.blit(empty_text, (x + width // 2 - 110, y + height // 2))
            return

        # List background
        pygame.draw.rect(
            self.screen,
            (25, 25, 40),
            (x, y, width, height),
            border_radius=6,
        )

        current_y = y + 10
        item_height = 160
        mouse_pos = pygame.mouse.get_pos()

        visible_actions = self.actions[self.scroll_offset:]

        for i, action in enumerate(visible_actions):
            if current_y + item_height > y + height - 10:
                break

            actual_index = i + self.scroll_offset
            is_selected = self.selected_index == actual_index

            self._render_action_item(
                x + 10,
                current_y,
                width - 20,
                item_height - 10,
                actual_index,
                action,
                is_selected,
                mouse_pos
            )

            current_y += item_height

        # Scroll indicators
        if self.scroll_offset > 0:
            arrow = self.font.render("▲", True, (200, 200, 200))
            self.screen.blit(arrow, (x + width - 30, y + 5))

        if len(self.actions) > len(visible_actions) + self.scroll_offset:
            arrow = self.font.render("▼", True, (200, 200, 200))
            self.screen.blit(arrow, (x + width - 30, y + height - 25))

    def _render_action_item(
        self,
        x: int, y: int, width: int, height: int,
        index: int, action: Dict, is_selected: bool,
        mouse_pos: tuple
    ):
        """Render a single action item."""
        # Background
        bg_color = (45, 60, 90) if is_selected else (35, 40, 55)
        pygame.draw.rect(
            self.screen,
            bg_color,
            (x, y, width, height),
            border_radius=6,
        )

        # Header: Action # and rating
        header_y = y + 8
        header_text = self.font.render(
            f"Action #{index + 1}  |  Priority: {action.get('rating', 5)}",
            True,
            (255, 200, 0)
        )
        self.screen.blit(header_text, (x + 10, header_y))

        # Skill ID
        skill_y = header_y + 30
        self._render_number_input(
            x + 10, skill_y, 120,
            index, "skill_id", "Skill ID",
            action.get("skill_id", 1),
            mouse_pos
        )

        # Rating
        self._render_number_input(
            x + 140, skill_y, 100,
            index, "rating", "Rating",
            action.get("rating", 5),
            mouse_pos
        )

        # Condition type selector
        cond_y = skill_y + 55
        self._render_condition_type(x + 10, cond_y, index, action, mouse_pos)

        # Condition parameters
        params_y = cond_y + 35
        self._render_condition_params(x + 10, params_y, index, action, mouse_pos)

        # Delete button
        self._render_delete_button(
            x + width - 90,
            y + height // 2 - 15,
            80, 30,
            index,
            mouse_pos
        )

    def _render_number_input(
        self, x: int, y: int, width: int,
        index: int, field_name: str, label: str,
        value: int, mouse_pos: tuple
    ):
        """Render a number input field."""
        # Label
        label_surf = self.small_font.render(label, True, (180, 180, 200))
        self.screen.blit(label_surf, (x, y))

        # Input box
        input_y = y + 18
        input_height = 26
        mouse_clicked = pygame.mouse.get_pressed()[0]

        is_active = self.active_input_field == (index, field_name)
        box_color = (70, 80, 120) if is_active else (50, 50, 70)

        pygame.draw.rect(
            self.screen,
            box_color,
            (x, input_y, width, input_height),
            border_radius=3,
        )

        # Display value
        display_value = self.input_text if is_active else str(value)
        value_surf = self.font.render(display_value, True, (255, 255, 255))
        self.screen.blit(value_surf, (x + 8, input_y + 3))

        # Handle click
        if (
            x <= mouse_pos[0] <= x + width
            and input_y <= mouse_pos[1] <= input_y + input_height
            and mouse_clicked
        ):
            self.active_input_field = (index, field_name)
            self.input_text = str(value)

    def _render_condition_type(self, x: int, y: int, index: int, action: Dict, mouse_pos: tuple):
        """Render condition type selector."""
        # Label
        label = self.small_font.render("Condition:", True, (180, 180, 200))
        self.screen.blit(label, (x, y))

        # Type buttons
        button_y = y + 18
        button_width = 80
        button_height = 24
        button_spacing = 5

        mouse_clicked = pygame.mouse.get_pressed()[0]
        current_type = action.get("condition_type", 0)

        for i, (cond_type, cond_name) in enumerate(self.CONDITION_TYPES.items()):
            if i >= 4:  # Show only first 4 inline
                break

            btn_x = x + i * (button_width + button_spacing)

            is_selected = current_type == cond_type
            is_hover = (
                btn_x <= mouse_pos[0] <= btn_x + button_width
                and button_y <= mouse_pos[1] <= button_y + button_height
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
                (btn_x, button_y, button_width, button_height),
                border_radius=4,
            )

            # Button text
            btn_text = self.small_font.render(cond_name[:8], True, (255, 255, 255))
            text_rect = btn_text.get_rect(
                center=(btn_x + button_width // 2, button_y + button_height // 2)
            )
            self.screen.blit(btn_text, text_rect)

            # Handle click
            if is_hover and mouse_clicked:
                action["condition_type"] = cond_type

    def _render_condition_params(self, x: int, y: int, index: int, action: Dict, mouse_pos: tuple):
        """Render condition parameter inputs."""
        cond_type = action.get("condition_type", 0)

        # Different parameters based on condition type
        if cond_type == 0:  # Always
            help_text = self.small_font.render("(No parameters needed)", True, (120, 120, 140))
            self.screen.blit(help_text, (x, y))

        elif cond_type == 1:  # Turn
            self._render_number_input(
                x, y, 100,
                index, "condition_param1", "Turn #",
                action.get("condition_param1", 1),
                mouse_pos
            )

        elif cond_type == 2 or cond_type == 3:  # HP% or MP%
            self._render_number_input(
                x, y, 80,
                index, "condition_param1", "Min %",
                action.get("condition_param1", 0),
                mouse_pos
            )
            self._render_number_input(
                x + 90, y, 80,
                index, "condition_param2", "Max %",
                action.get("condition_param2", 100),
                mouse_pos
            )

        elif cond_type == 4:  # State
            self._render_number_input(
                x, y, 120,
                index, "condition_param1", "State ID",
                action.get("condition_param1", 1),
                mouse_pos
            )

        elif cond_type == 5:  # Party level
            self._render_number_input(
                x, y, 120,
                index, "condition_param1", "Min Level",
                action.get("condition_param1", 1),
                mouse_pos
            )

        elif cond_type == 6:  # Switch
            self._render_number_input(
                x, y, 120,
                index, "condition_param1", "Switch ID",
                action.get("condition_param1", 1),
                mouse_pos
            )

    def _render_delete_button(
        self, x: int, y: int, width: int, height: int,
        index: int, mouse_pos: tuple
    ):
        """Render delete button for action."""
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
            self._delete_action(index)

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
            self.result = [action.copy() for action in self.actions]

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

    def _add_action(self):
        """Add a new action to the list."""
        new_action = {
            "skill_id": 1,
            "condition_type": 0,
            "condition_param1": 0,
            "condition_param2": 0,
            "rating": 5,
        }
        self.actions.append(new_action)
        self.selected_index = len(self.actions) - 1

    def _delete_action(self, index: int):
        """Delete an action from the list."""
        if 0 <= index < len(self.actions):
            self.actions.pop(index)
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
            if 0 <= index < len(self.actions):
                self.actions[index][field_name] = int(self.input_text)
        except ValueError:
            pass  # Invalid input, ignore

        self.active_input_field = None
        self.input_text = ""

    def get_result(self) -> Optional[List[Dict]]:
        """Get the result after the dialog is closed."""
        return self.result

    def is_visible(self) -> bool:
        """Check if the dialog is visible."""
        return self.visible
