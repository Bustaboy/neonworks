"""
Condition Parameter Editor

Visual conditional builder for creating complex conditional branches.
Supports various condition types: switches, variables, actors, items, etc.
"""

from typing import Dict, Any, Optional, List
import pygame


class ConditionParamEditor:
    """
    Visual builder for conditional branch conditions.

    Condition types:
    - Switch: Check if a switch is ON/OFF
    - Variable: Compare a variable value
    - Self Switch: Check event's self switch
    - Timer: Check timer value
    - Actor: Check actor state (in party, HP, MP, state, skill, weapon, armor)
    - Enemy: Check enemy state (in battle)
    - Character: Check character position/direction
    - Gold: Check party gold amount
    - Item: Check item possession
    - Weapon: Check weapon possession
    - Armor: Check armor possession
    - Button: Check button press
    - Script: Custom script evaluation
    """

    CONDITION_TYPES = [
        "Switch",
        "Variable",
        "Self Switch",
        "Timer",
        "Actor",
        "Gold",
        "Item",
        "Weapon",
        "Armor",
        "Button",
        "Script",
    ]

    COMPARISON_OPERATORS = ["==", "!=", ">", ">=", "<", "<="]

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.visible = False
        self.result = None

        # Condition state
        self.condition_type = "Switch"
        self.parameters = {
            "switch_id": 1,
            "switch_value": True,
        }

        # UI state
        self.selected_type_index = 0
        self.scroll_offset = 0

        # Fonts
        self.font = pygame.font.Font(None, 22)
        self.title_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 18)

    def open(self, initial_condition: Optional[Dict[str, Any]] = None) -> None:
        """
        Open the condition editor dialog.

        Args:
            initial_condition: Initial condition data
        """
        self.visible = True
        self.result = None

        if initial_condition:
            self.condition_type = initial_condition.get("condition_type", "Switch")
            self.parameters = dict(initial_condition)
            self.parameters.pop("condition_type", None)
            self.selected_type_index = self.CONDITION_TYPES.index(self.condition_type)
        else:
            self.condition_type = "Switch"
            self.parameters = {"switch_id": 1, "switch_value": True}
            self.selected_type_index = 0

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

        return True

    def render(self) -> Optional[Dict[str, Any]]:
        """
        Render the condition editor dialog.

        Returns:
            Result condition if dialog was closed with OK, None otherwise
        """
        if not self.visible:
            return self.result

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        # Dialog dimensions
        dialog_width = min(700, screen_width - 100)
        dialog_height = min(500, screen_height - 100)
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
        title_text = self.title_font.render("Condition Builder", True, (255, 200, 0))
        self.screen.blit(title_text, (dialog_x + 20, dialog_y + 12))

        # Content area
        content_y = dialog_y + title_height + 20
        content_height = dialog_height - title_height - 90

        # Left panel: Condition types
        type_panel_width = 180
        self._render_type_panel(
            dialog_x + 10, content_y, type_panel_width, content_height
        )

        # Right panel: Condition parameters
        param_panel_x = dialog_x + type_panel_width + 20
        param_panel_width = dialog_width - type_panel_width - 30
        self._render_parameter_panel(
            param_panel_x, content_y, param_panel_width, content_height
        )

        # Bottom buttons
        self._render_bottom_buttons(
            dialog_x + dialog_width - 220,
            dialog_y + dialog_height - 60,
        )

        return None

    def _render_type_panel(self, x: int, y: int, width: int, height: int):
        """Render the condition type selection panel."""
        # Panel background
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

        # Panel title
        title_text = self.font.render("Condition Type", True, (200, 200, 255))
        self.screen.blit(title_text, (x + 10, y + 10))

        # Type list
        item_height = 35
        list_y = y + 45
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        for i, cond_type in enumerate(self.CONDITION_TYPES):
            item_y = list_y + i * (item_height + 3)

            if item_y + item_height > y + height - 5:
                break

            is_selected = i == self.selected_type_index
            is_hover = (
                x + 5 <= mouse_pos[0] <= x + width - 5
                and item_y <= mouse_pos[1] <= item_y + item_height
            )

            # Item background
            if is_selected:
                item_color = (60, 80, 140)
            elif is_hover:
                item_color = (50, 50, 70)
            else:
                item_color = (35, 35, 50)

            pygame.draw.rect(
                self.screen,
                item_color,
                (x + 5, item_y, width - 10, item_height),
                border_radius=4,
            )

            # Item text
            text_surface = self.font.render(cond_type, True, (255, 255, 255))
            self.screen.blit(text_surface, (x + 12, item_y + 8))

            # Handle click
            if is_hover and mouse_clicked:
                self.selected_type_index = i
                self.condition_type = cond_type
                self._reset_parameters_for_type()

    def _render_parameter_panel(self, x: int, y: int, width: int, height: int):
        """Render the condition parameter configuration panel."""
        # Panel background
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

        # Panel title
        title_text = self.font.render("Parameters", True, (200, 200, 255))
        self.screen.blit(title_text, (x + 10, y + 10))

        # Render parameters based on condition type
        param_y = y + 50
        if self.condition_type == "Switch":
            self._render_switch_params(x + 15, param_y, width - 30)
        elif self.condition_type == "Variable":
            self._render_variable_params(x + 15, param_y, width - 30)
        elif self.condition_type == "Self Switch":
            self._render_self_switch_params(x + 15, param_y, width - 30)
        elif self.condition_type == "Timer":
            self._render_timer_params(x + 15, param_y, width - 30)
        elif self.condition_type == "Actor":
            self._render_actor_params(x + 15, param_y, width - 30)
        elif self.condition_type == "Gold":
            self._render_gold_params(x + 15, param_y, width - 30)
        elif self.condition_type == "Item":
            self._render_item_params(x + 15, param_y, width - 30)
        elif self.condition_type == "Weapon":
            self._render_weapon_params(x + 15, param_y, width - 30)
        elif self.condition_type == "Armor":
            self._render_armor_params(x + 15, param_y, width - 30)
        elif self.condition_type == "Button":
            self._render_button_params(x + 15, param_y, width - 30)
        elif self.condition_type == "Script":
            self._render_script_params(x + 15, param_y, width - 30)

    def _render_switch_params(self, x: int, y: int, width: int):
        """Render parameters for Switch condition."""
        # Switch ID
        label = self.font.render("Switch ID:", True, (200, 200, 220))
        self.screen.blit(label, (x, y))

        switch_id = self.parameters.get("switch_id", 1)
        self._render_number_input(x + 150, y, 80, switch_id, "switch_id")

        # Switch value (ON/OFF)
        y += 50
        label = self.font.render("Expected Value:", True, (200, 200, 220))
        self.screen.blit(label, (x, y))

        switch_value = self.parameters.get("switch_value", True)
        self._render_toggle_button(
            x + 150, y, 100, 35, switch_value, "switch_value", "ON", "OFF"
        )

    def _render_variable_params(self, x: int, y: int, width: int):
        """Render parameters for Variable condition."""
        # Variable ID
        label = self.font.render("Variable ID:", True, (200, 200, 220))
        self.screen.blit(label, (x, y))

        var_id = self.parameters.get("variable_id", 1)
        self._render_number_input(x + 150, y, 80, var_id, "variable_id")

        # Comparison operator
        y += 50
        label = self.font.render("Operator:", True, (200, 200, 220))
        self.screen.blit(label, (x, y))

        operator = self.parameters.get("operator", "==")
        self._render_dropdown(
            x + 150, y, 80, operator, self.COMPARISON_OPERATORS, "operator"
        )

        # Value
        y += 50
        label = self.font.render("Value:", True, (200, 200, 220))
        self.screen.blit(label, (x, y))

        value = self.parameters.get("value", 0)
        self._render_number_input(x + 150, y, 80, value, "value")

    def _render_self_switch_params(self, x: int, y: int, width: int):
        """Render parameters for Self Switch condition."""
        # Self switch letter
        label = self.font.render("Self Switch:", True, (200, 200, 220))
        self.screen.blit(label, (x, y))

        switch_ch = self.parameters.get("self_switch_ch", "A")
        self._render_dropdown(
            x + 150, y, 80, switch_ch, ["A", "B", "C", "D"], "self_switch_ch"
        )

        # Value
        y += 50
        label = self.font.render("Expected Value:", True, (200, 200, 220))
        self.screen.blit(label, (x, y))

        value = self.parameters.get("value", True)
        self._render_toggle_button(x + 150, y, 100, 35, value, "value", "ON", "OFF")

    def _render_timer_params(self, x: int, y: int, width: int):
        """Render parameters for Timer condition."""
        # Comparison
        label = self.font.render("Timer:", True, (200, 200, 220))
        self.screen.blit(label, (x, y))

        operator = self.parameters.get("operator", ">=")
        self._render_dropdown(x + 150, y, 80, operator, [">=", "<="], "operator")

        # Time in seconds
        y += 50
        label = self.font.render("Seconds:", True, (200, 200, 220))
        self.screen.blit(label, (x, y))

        seconds = self.parameters.get("seconds", 0)
        self._render_number_input(x + 150, y, 80, seconds, "seconds")

    def _render_actor_params(self, x: int, y: int, width: int):
        """Render parameters for Actor condition."""
        # Actor ID
        label = self.font.render("Actor ID:", True, (200, 200, 220))
        self.screen.blit(label, (x, y))

        actor_id = self.parameters.get("actor_id", 1)
        self._render_number_input(x + 150, y, 80, actor_id, "actor_id")

        # Condition type
        y += 50
        label = self.font.render("Check:", True, (200, 200, 220))
        self.screen.blit(label, (x, y))

        check_type = self.parameters.get("check_type", "in_party")
        options = ["in_party", "has_skill", "has_weapon", "has_armor", "has_state"]
        self._render_dropdown(x + 150, y, 150, check_type, options, "check_type")

    def _render_gold_params(self, x: int, y: int, width: int):
        """Render parameters for Gold condition."""
        # Operator
        label = self.font.render("Party Gold:", True, (200, 200, 220))
        self.screen.blit(label, (x, y))

        operator = self.parameters.get("operator", ">=")
        self._render_dropdown(
            x + 150, y, 80, operator, self.COMPARISON_OPERATORS, "operator"
        )

        # Amount
        y += 50
        label = self.font.render("Amount:", True, (200, 200, 220))
        self.screen.blit(label, (x, y))

        amount = self.parameters.get("amount", 100)
        self._render_number_input(x + 150, y, 100, amount, "amount")

    def _render_item_params(self, x: int, y: int, width: int):
        """Render parameters for Item condition."""
        label = self.font.render("Item ID:", True, (200, 200, 220))
        self.screen.blit(label, (x, y))

        item_id = self.parameters.get("item_id", 1)
        self._render_number_input(x + 150, y, 80, item_id, "item_id")

    def _render_weapon_params(self, x: int, y: int, width: int):
        """Render parameters for Weapon condition."""
        label = self.font.render("Weapon ID:", True, (200, 200, 220))
        self.screen.blit(label, (x, y))

        weapon_id = self.parameters.get("weapon_id", 1)
        self._render_number_input(x + 150, y, 80, weapon_id, "weapon_id")

    def _render_armor_params(self, x: int, y: int, width: int):
        """Render parameters for Armor condition."""
        label = self.font.render("Armor ID:", True, (200, 200, 220))
        self.screen.blit(label, (x, y))

        armor_id = self.parameters.get("armor_id", 1)
        self._render_number_input(x + 150, y, 80, armor_id, "armor_id")

    def _render_button_params(self, x: int, y: int, width: int):
        """Render parameters for Button condition."""
        label = self.font.render("Button:", True, (200, 200, 220))
        self.screen.blit(label, (x, y))

        button = self.parameters.get("button", "OK")
        buttons = ["OK", "Cancel", "Shift", "Down", "Left", "Right", "Up"]
        self._render_dropdown(x + 150, y, 120, button, buttons, "button")

    def _render_script_params(self, x: int, y: int, width: int):
        """Render parameters for Script condition."""
        label = self.font.render("Script Expression:", True, (200, 200, 220))
        self.screen.blit(label, (x, y))

        y += 30
        script = self.parameters.get("script", "")
        # Simple text display - could be expanded to full text editor
        script_text = self.small_font.render(
            script or "(click to edit)", True, (180, 180, 200)
        )
        self.screen.blit(script_text, (x, y))

    def _render_number_input(
        self, x: int, y: int, width: int, value: int, param_name: str
    ):
        """Render a simple number input field."""
        height = 35
        mouse_pos = pygame.mouse.get_pos()
        is_hover = x <= mouse_pos[0] <= x + width and y <= mouse_pos[1] <= y + height

        color = (50, 50, 80) if is_hover else (35, 35, 55)
        pygame.draw.rect(self.screen, color, (x, y, width, height), border_radius=4)
        pygame.draw.rect(
            self.screen, (80, 80, 100), (x, y, width, height), 2, border_radius=4
        )

        value_text = self.font.render(str(value), True, (255, 255, 255))
        text_rect = value_text.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(value_text, text_rect)

        # Simple increment/decrement with arrow buttons
        arrow_size = 15
        up_rect = pygame.Rect(x + width - arrow_size - 5, y + 3, arrow_size, arrow_size)
        down_rect = pygame.Rect(
            x + width - arrow_size - 5,
            y + height - arrow_size - 3,
            arrow_size,
            arrow_size,
        )

        # Up arrow
        pygame.draw.polygon(
            self.screen,
            (100, 150, 200),
            [
                (up_rect.centerx, up_rect.top),
                (up_rect.left, up_rect.bottom),
                (up_rect.right, up_rect.bottom),
            ],
        )

        # Down arrow
        pygame.draw.polygon(
            self.screen,
            (100, 150, 200),
            [
                (down_rect.centerx, down_rect.bottom),
                (down_rect.left, down_rect.top),
                (down_rect.right, down_rect.top),
            ],
        )

        if pygame.mouse.get_pressed()[0]:
            if up_rect.collidepoint(mouse_pos):
                self.parameters[param_name] = value + 1
            elif down_rect.collidepoint(mouse_pos):
                self.parameters[param_name] = max(0, value - 1)

    def _render_toggle_button(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        value: bool,
        param_name: str,
        true_label: str,
        false_label: str,
    ):
        """Render a toggle button."""
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        is_hover = x <= mouse_pos[0] <= x + width and y <= mouse_pos[1] <= y + height

        color = (60, 120, 60) if value else (120, 60, 60)
        if is_hover:
            color = tuple(min(c + 20, 255) for c in color)

        pygame.draw.rect(self.screen, color, (x, y, width, height), border_radius=4)

        label = true_label if value else false_label
        text = self.font.render(label, True, (255, 255, 255))
        text_rect = text.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(text, text_rect)

        if is_hover and mouse_clicked:
            self.parameters[param_name] = not value

    def _render_dropdown(
        self,
        x: int,
        y: int,
        width: int,
        value: str,
        options: List[str],
        param_name: str,
    ):
        """Render a simple dropdown (button that cycles through options)."""
        height = 35
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        is_hover = x <= mouse_pos[0] <= x + width and y <= mouse_pos[1] <= y + height

        color = (50, 70, 110) if is_hover else (40, 50, 80)
        pygame.draw.rect(self.screen, color, (x, y, width, height), border_radius=4)
        pygame.draw.rect(
            self.screen, (80, 80, 100), (x, y, width, height), 2, border_radius=4
        )

        text = self.font.render(str(value), True, (255, 255, 255))
        text_rect = text.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(text, text_rect)

        # Arrow indicator
        arrow_text = self.small_font.render("▼", True, (150, 150, 150))
        self.screen.blit(arrow_text, (x + width - 20, y + 10))

        if is_hover and mouse_clicked:
            # Cycle to next option
            current_index = options.index(value) if value in options else 0
            next_index = (current_index + 1) % len(options)
            self.parameters[param_name] = options[next_index]

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
        ok_rect = ok_text.get_rect(
            center=(x + button_width // 2, y + button_height // 2)
        )
        self.screen.blit(ok_text, ok_rect)

        if ok_hover and mouse_clicked:
            self.visible = False
            self.result = {"condition_type": self.condition_type, **self.parameters}

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

    def _reset_parameters_for_type(self):
        """Reset parameters when condition type changes."""
        if self.condition_type == "Switch":
            self.parameters = {"switch_id": 1, "switch_value": True}
        elif self.condition_type == "Variable":
            self.parameters = {"variable_id": 1, "operator": "==", "value": 0}
        elif self.condition_type == "Self Switch":
            self.parameters = {"self_switch_ch": "A", "value": True}
        elif self.condition_type == "Timer":
            self.parameters = {"operator": ">=", "seconds": 0}
        elif self.condition_type == "Actor":
            self.parameters = {"actor_id": 1, "check_type": "in_party"}
        elif self.condition_type == "Gold":
            self.parameters = {"operator": ">=", "amount": 100}
        elif self.condition_type == "Item":
            self.parameters = {"item_id": 1}
        elif self.condition_type == "Weapon":
            self.parameters = {"weapon_id": 1}
        elif self.condition_type == "Armor":
            self.parameters = {"armor_id": 1}
        elif self.condition_type == "Button":
            self.parameters = {"button": "OK"}
        elif self.condition_type == "Script":
            self.parameters = {"script": ""}

    def get_result(self) -> Optional[Dict[str, Any]]:
        """Get the result after the dialog is closed."""
        return self.result

    def is_visible(self) -> bool:
        """Check if the dialog is visible."""
        return self.visible
