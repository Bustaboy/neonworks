"""
Move Route Parameter Editor

Modal dialog for creating and editing movement command sequences.
Used for SET_MOVEMENT_ROUTE event commands.
"""

from typing import Dict, Any, Optional, List
import pygame


class MoveRouteParamEditor:
    """
    Visual editor for movement route sequences.

    Movement commands:
    - Directional: Move Down, Move Left, Move Right, Move Up
    - Diagonal: Move Lower Left, Move Lower Right, Move Upper Left, Move Upper Right
    - Random: Move Random, Move Toward Player, Move Away from Player
    - Actions: Turn Down, Turn Left, Turn Right, Turn Up, Turn Random, Turn Toward Player, Turn Away
    - Advanced: Jump, Wait, Switch ON/OFF, Change Speed, Change Frequency
    - Graphics: Change Graphic, Change Opacity, Change Blend Mode
    - Audio: Play SE
    - Script: Script
    """

    MOVE_COMMANDS = {
        "Directional": [
            ("Move Down", {"type": "move", "direction": 2}),
            ("Move Left", {"type": "move", "direction": 4}),
            ("Move Right", {"type": "move", "direction": 6}),
            ("Move Up", {"type": "move", "direction": 8}),
        ],
        "Diagonal": [
            ("Move Lower Left", {"type": "move", "direction": 1}),
            ("Move Lower Right", {"type": "move", "direction": 3}),
            ("Move Upper Left", {"type": "move", "direction": 7}),
            ("Move Upper Right", {"type": "move", "direction": 9}),
        ],
        "Random": [
            ("Move Random", {"type": "move_random"}),
            ("Move Toward Player", {"type": "move_toward_player"}),
            ("Move Away from Player", {"type": "move_away_player"}),
            ("Step Forward", {"type": "step_forward"}),
            ("Step Backward", {"type": "step_backward"}),
        ],
        "Turn": [
            ("Turn Down", {"type": "turn", "direction": 2}),
            ("Turn Left", {"type": "turn", "direction": 4}),
            ("Turn Right", {"type": "turn", "direction": 6}),
            ("Turn Up", {"type": "turn", "direction": 8}),
            ("Turn 90° Right", {"type": "turn_right_90"}),
            ("Turn 90° Left", {"type": "turn_left_90"}),
            ("Turn 180°", {"type": "turn_180"}),
            ("Turn Random", {"type": "turn_random"}),
            ("Turn Toward Player", {"type": "turn_toward_player"}),
            ("Turn Away from Player", {"type": "turn_away_player"}),
        ],
        "Jump": [
            ("Jump", {"type": "jump", "x": 0, "y": 0}),
        ],
        "Wait": [
            ("Wait", {"type": "wait", "duration": 10}),
        ],
        "Options": [
            ("Switch ON", {"type": "switch_on"}),
            ("Switch OFF", {"type": "switch_off"}),
            ("Change Speed", {"type": "change_speed", "speed": 4}),
            ("Change Frequency", {"type": "change_frequency", "frequency": 4}),
            ("Walk Animation ON", {"type": "walk_anime_on"}),
            ("Walk Animation OFF", {"type": "walk_anime_off"}),
            ("Step Animation ON", {"type": "step_anime_on"}),
            ("Step Animation OFF", {"type": "step_anime_off"}),
            ("Direction Fix ON", {"type": "direction_fix_on"}),
            ("Direction Fix OFF", {"type": "direction_fix_off"}),
            ("Through ON", {"type": "through_on"}),
            ("Through OFF", {"type": "through_off"}),
            ("Transparent ON", {"type": "transparent_on"}),
            ("Transparent OFF", {"type": "transparent_off"}),
        ],
        "Audio": [
            ("Play SE", {"type": "play_se", "name": ""}),
        ],
        "Script": [
            ("Script", {"type": "script", "code": ""}),
        ],
    }

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.visible = False
        self.result = None

        # Move route state
        self.commands: List[Dict[str, Any]] = []
        self.repeat = False
        self.skippable = False
        self.wait_for_completion = True

        # Selection state
        self.selected_command_index: Optional[int] = None

        # UI state
        self.scroll_offset = 0
        self.command_scroll = 0
        self.selected_category = "Directional"

        # Fonts
        self.font = pygame.font.Font(None, 20)
        self.title_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 18)

    def open(self, initial_route: Optional[Dict[str, Any]] = None) -> None:
        """
        Open the move route editor.

        Args:
            initial_route: Initial move route data with commands and options
        """
        self.visible = True
        self.result = None

        if initial_route:
            self.commands = list(initial_route.get("commands", []))
            self.repeat = initial_route.get("repeat", False)
            self.skippable = initial_route.get("skippable", False)
            self.wait_for_completion = initial_route.get("wait", True)
        else:
            self.commands = []
            self.repeat = False
            self.skippable = False
            self.wait_for_completion = True

        self.selected_command_index = None
        self.scroll_offset = 0
        self.command_scroll = 0

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
            elif event.key == pygame.K_DELETE:
                # Delete selected command
                if (
                    self.selected_command_index is not None
                    and 0 <= self.selected_command_index < len(self.commands)
                ):
                    del self.commands[self.selected_command_index]
                    self.selected_command_index = None

        return True

    def render(self) -> Optional[Dict[str, Any]]:
        """
        Render the move route editor.

        Returns:
            Result move route if dialog was closed with OK, None otherwise
        """
        if not self.visible:
            return self.result

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        # Dialog dimensions
        dialog_width = min(900, screen_width - 80)
        dialog_height = min(700, screen_height - 80)
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
        title_text = self.title_font.render("Move Route Editor", True, (255, 200, 0))
        self.screen.blit(title_text, (dialog_x + 20, dialog_y + 12))

        # Content area
        content_y = dialog_y + title_height + 15
        content_height = dialog_height - title_height - 130

        # Left panel: Command sequence
        sequence_width = 350
        self._render_sequence_panel(
            dialog_x + 10, content_y, sequence_width, content_height
        )

        # Right panel: Command palette
        palette_x = dialog_x + sequence_width + 20
        palette_width = dialog_width - sequence_width - 30
        self._render_palette_panel(palette_x, content_y, palette_width, content_height)

        # Options panel
        options_y = content_y + content_height + 10
        self._render_options_panel(dialog_x + 10, options_y, dialog_width - 20)

        # Bottom buttons
        self._render_bottom_buttons(
            dialog_x + dialog_width - 220,
            dialog_y + dialog_height - 60,
        )

        return None

    def _render_sequence_panel(self, x: int, y: int, width: int, height: int):
        """Render the command sequence panel."""
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
        title_text = self.font.render("Movement Sequence", True, (200, 200, 255))
        self.screen.blit(title_text, (x + 10, y + 10))

        # Command count
        count_text = self.small_font.render(
            f"{len(self.commands)} commands", True, (150, 150, 170)
        )
        self.screen.blit(count_text, (x + width - 100, y + 12))

        # Command list
        list_y = y + 40
        list_height = height - 90
        item_height = 35

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        if not self.commands:
            # Empty state
            empty_text = self.small_font.render(
                "No commands yet", True, (120, 120, 140)
            )
            self.screen.blit(empty_text, (x + width // 2 - 60, y + height // 2))
            empty_text2 = self.small_font.render(
                "Add commands from the palette →", True, (120, 120, 140)
            )
            self.screen.blit(empty_text2, (x + width // 2 - 105, y + height // 2 + 20))
        else:
            # Render commands
            for i, cmd in enumerate(self.commands):
                if i < self.command_scroll:
                    continue

                item_y = list_y + (i - self.command_scroll) * (item_height + 2)
                if item_y + item_height > list_y + list_height:
                    break

                is_selected = i == self.selected_command_index
                is_hover = (
                    x + 5 <= mouse_pos[0] <= x + width - 5
                    and item_y <= mouse_pos[1] <= item_y + item_height
                )

                # Item background
                if is_selected:
                    item_color = (70, 100, 160)
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

                # Command number
                num_text = self.small_font.render(f"{i + 1}.", True, (180, 180, 200))
                self.screen.blit(num_text, (x + 10, item_y + 9))

                # Command description
                cmd_desc = self._get_command_description(cmd)
                cmd_text = self.font.render(cmd_desc, True, (255, 255, 255))
                # Truncate if too long
                if cmd_text.get_width() > width - 60:
                    cmd_desc = cmd_desc[:30] + "..."
                    cmd_text = self.font.render(cmd_desc, True, (255, 255, 255))
                self.screen.blit(cmd_text, (x + 35, item_y + 8))

                # Handle click
                if is_hover and mouse_clicked:
                    self.selected_command_index = i

        # Control buttons
        btn_y = y + height - 45
        self._render_sequence_buttons(x + 5, btn_y, width - 10)

    def _render_palette_panel(self, x: int, y: int, width: int, height: int):
        """Render the command palette panel."""
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
        title_text = self.font.render("Command Palette", True, (200, 200, 255))
        self.screen.blit(title_text, (x + 10, y + 10))

        # Category tabs
        tab_y = y + 40
        self._render_category_tabs(x + 5, tab_y, width - 10)

        # Command list for selected category
        list_y = tab_y + 45
        list_height = height - 95
        self._render_command_list(x + 5, list_y, width - 10, list_height)

    def _render_category_tabs(self, x: int, y: int, width: int):
        """Render category selection tabs."""
        categories = list(self.MOVE_COMMANDS.keys())
        tab_width = 90
        tab_height = 30
        tab_spacing = 3

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        current_x = x
        for category in categories:
            if current_x + tab_width > x + width:
                break

            is_selected = category == self.selected_category
            is_hover = (
                current_x <= mouse_pos[0] <= current_x + tab_width
                and y <= mouse_pos[1] <= y + tab_height
            )

            # Tab background
            if is_selected:
                tab_color = (60, 80, 140)
            elif is_hover:
                tab_color = (50, 60, 100)
            else:
                tab_color = (40, 45, 70)

            pygame.draw.rect(
                self.screen,
                tab_color,
                (current_x, y, tab_width, tab_height),
                border_radius=4,
            )

            # Tab text
            tab_text = self.small_font.render(category, True, (255, 255, 255))
            text_rect = tab_text.get_rect(
                center=(current_x + tab_width // 2, y + tab_height // 2)
            )
            self.screen.blit(tab_text, text_rect)

            # Handle click
            if is_hover and mouse_clicked and not is_selected:
                self.selected_category = category

            current_x += tab_width + tab_spacing

    def _render_command_list(self, x: int, y: int, width: int, height: int):
        """Render the command list for the selected category."""
        commands = self.MOVE_COMMANDS.get(self.selected_category, [])
        item_height = 32
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        for i, (name, params) in enumerate(commands):
            item_y = y + i * (item_height + 2)
            if item_y + item_height > y + height:
                break

            is_hover = (
                x <= mouse_pos[0] <= x + width
                and item_y <= mouse_pos[1] <= item_y + item_height
            )

            # Item background
            item_color = (60, 80, 120) if is_hover else (40, 50, 75)

            pygame.draw.rect(
                self.screen,
                item_color,
                (x, item_y, width, item_height),
                border_radius=4,
            )

            # Command name
            name_text = self.font.render(name, True, (255, 255, 255))
            self.screen.blit(name_text, (x + 10, item_y + 6))

            # Handle click - add command to sequence
            if is_hover and mouse_clicked:
                self.add_command(dict(params))

    def _render_sequence_buttons(self, x: int, y: int, width: int):
        """Render control buttons for the sequence."""
        button_width = 75
        button_height = 35
        button_spacing = 5

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        buttons = [
            ("Clear", self.clear_commands),
            ("Move Up", self.move_command_up),
            ("Move Down", self.move_command_down),
            ("Delete", self.delete_command),
        ]

        current_x = x
        for label, action in buttons:
            if current_x + button_width > x + width:
                break

            is_hover = (
                current_x <= mouse_pos[0] <= current_x + button_width
                and y <= mouse_pos[1] <= y + button_height
            )

            btn_color = (80, 60, 60) if is_hover else (60, 40, 40)

            pygame.draw.rect(
                self.screen,
                btn_color,
                (current_x, y, button_width, button_height),
                border_radius=4,
            )

            btn_text = self.small_font.render(label, True, (255, 255, 255))
            text_rect = btn_text.get_rect(
                center=(current_x + button_width // 2, y + button_height // 2)
            )
            self.screen.blit(btn_text, text_rect)

            if is_hover and mouse_clicked:
                action()

            current_x += button_width + button_spacing

    def _render_options_panel(self, x: int, y: int, width: int):
        """Render the options panel."""
        height = 45
        pygame.draw.rect(
            self.screen,
            (25, 25, 38),
            (x, y, width, height),
            border_radius=6,
        )

        # Options checkboxes
        options = [
            ("Repeat", "repeat"),
            ("Skippable", "skippable"),
            ("Wait for Completion", "wait_for_completion"),
        ]

        checkbox_x = x + 15
        for i, (label, attr) in enumerate(options):
            current_x = checkbox_x + i * 200
            value = getattr(self, attr)
            new_value = self._render_checkbox(current_x, y + 12, label, value)
            setattr(self, attr, new_value)

    def _render_checkbox(self, x: int, y: int, label: str, checked: bool) -> bool:
        """Render a checkbox."""
        size = 20
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        is_hover = x <= mouse_pos[0] <= x + size and y <= mouse_pos[1] <= y + size

        # Checkbox box
        box_color = (80, 120, 180) if is_hover else (60, 80, 120)
        pygame.draw.rect(self.screen, (30, 30, 45), (x, y, size, size), border_radius=3)
        pygame.draw.rect(self.screen, box_color, (x, y, size, size), 2, border_radius=3)

        # Checkmark
        if checked:
            padding = 4
            pygame.draw.rect(
                self.screen,
                (100, 200, 100),
                (x + padding, y + padding, size - padding * 2, size - padding * 2),
                border_radius=2,
            )

        # Label
        label_text = self.font.render(label, True, (220, 220, 240))
        self.screen.blit(label_text, (x + size + 8, y - 2))

        # Handle click
        if is_hover and mouse_clicked:
            return not checked

        return checked

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

    def _get_command_description(self, command: Dict[str, Any]) -> str:
        """Get a human-readable description of a command."""
        cmd_type = command.get("type", "")

        if cmd_type == "move":
            direction = command.get("direction", 0)
            directions = {
                2: "Down",
                4: "Left",
                6: "Right",
                8: "Up",
                1: "Lower Left",
                3: "Lower Right",
                7: "Upper Left",
                9: "Upper Right",
            }
            return f"Move {directions.get(direction, '?')}"
        elif cmd_type == "turn":
            direction = command.get("direction", 0)
            directions = {2: "Down", 4: "Left", 6: "Right", 8: "Up"}
            return f"Turn {directions.get(direction, '?')}"
        elif cmd_type == "wait":
            duration = command.get("duration", 0)
            return f"Wait {duration} frames"
        elif cmd_type == "jump":
            x = command.get("x", 0)
            y = command.get("y", 0)
            return f"Jump ({x:+d}, {y:+d})"
        elif cmd_type == "change_speed":
            speed = command.get("speed", 4)
            return f"Speed: {speed}"
        elif cmd_type == "change_frequency":
            freq = command.get("frequency", 4)
            return f"Frequency: {freq}"
        elif cmd_type == "play_se":
            name = command.get("name", "")
            return f"Play SE: {name or '(none)'}"
        elif cmd_type == "script":
            return "Script"
        else:
            # Convert snake_case to Title Case
            return cmd_type.replace("_", " ").title()

    def add_command(self, command: Dict[str, Any]):
        """Add a command to the sequence."""
        if self.selected_command_index is not None:
            # Insert after selected
            self.commands.insert(self.selected_command_index + 1, command)
            self.selected_command_index += 1
        else:
            # Append to end
            self.commands.append(command)
            self.selected_command_index = len(self.commands) - 1

    def clear_commands(self):
        """Clear all commands."""
        self.commands = []
        self.selected_command_index = None

    def move_command_up(self):
        """Move selected command up in the sequence."""
        if self.selected_command_index is not None and self.selected_command_index > 0:
            idx = self.selected_command_index
            self.commands[idx], self.commands[idx - 1] = (
                self.commands[idx - 1],
                self.commands[idx],
            )
            self.selected_command_index = idx - 1

    def move_command_down(self):
        """Move selected command down in the sequence."""
        if (
            self.selected_command_index is not None
            and self.selected_command_index < len(self.commands) - 1
        ):
            idx = self.selected_command_index
            self.commands[idx], self.commands[idx + 1] = (
                self.commands[idx + 1],
                self.commands[idx],
            )
            self.selected_command_index = idx + 1

    def delete_command(self):
        """Delete the selected command."""
        if (
            self.selected_command_index is not None
            and 0 <= self.selected_command_index < len(self.commands)
        ):
            del self.commands[self.selected_command_index]
            self.selected_command_index = None

    def _confirm_selection(self):
        """Confirm the move route and close the dialog."""
        self.visible = False
        self.result = {
            "commands": self.commands,
            "repeat": self.repeat,
            "skippable": self.skippable,
            "wait": self.wait_for_completion,
        }

    def get_result(self) -> Optional[Dict[str, Any]]:
        """Get the result after the dialog is closed."""
        return self.result

    def is_visible(self) -> bool:
        """Check if the dialog is visible."""
        return self.visible
