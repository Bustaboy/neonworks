"""
NeonWorks Event Editor UI - Visual Event and Command Editing
Provides complete visual interface for creating and editing RPG-style events and commands.
"""

from typing import Any, Dict, List, Optional, Tuple

import pygame

from core.event_commands import (
    CommandType,
    EventCommand,
    EventPage,
    GameEvent,
    TriggerType,
)
from rendering.ui import UI


class EventEditorUI:
    """
    Visual editor for creating and managing game events and commands.

    Features three-panel layout:
    - Left panel: Event list showing all events in the current scene
    - Middle panel: Command list with indentation for nested commands
    - Right panel: Command palette with categorized commands
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.ui = UI(screen)

        self.visible = False

        # Event data
        self.events: List[GameEvent] = []
        self.current_event: Optional[GameEvent] = None
        self.current_page_index: int = 0

        # Command selection
        self.selected_command_index: Optional[int] = None
        self.hovered_command_index: Optional[int] = None

        # UI state
        self.event_list_scroll = 0
        self.command_list_scroll = 0
        self.palette_scroll = 0

        # Command categories for palette
        self.command_categories = {
            "Message": [
                CommandType.SHOW_TEXT,
                CommandType.SHOW_CHOICES,
                CommandType.INPUT_NUMBER,
            ],
            "Flow Control": [
                CommandType.CONDITIONAL_BRANCH,
                CommandType.LOOP,
                CommandType.BREAK_LOOP,
                CommandType.EXIT_EVENT,
                CommandType.LABEL,
                CommandType.JUMP_TO_LABEL,
                CommandType.COMMENT,
            ],
            "Game Progress": [
                CommandType.CONTROL_SWITCHES,
                CommandType.CONTROL_VARIABLES,
                CommandType.CONTROL_SELF_SWITCH,
                CommandType.CONTROL_TIMER,
            ],
            "Character": [
                CommandType.TRANSFER_PLAYER,
                CommandType.SET_MOVEMENT_ROUTE,
                CommandType.SHOW_ANIMATION,
                CommandType.SHOW_BALLOON,
                CommandType.ERASE_EVENT,
            ],
            "Screen Effects": [
                CommandType.FADEOUT_SCREEN,
                CommandType.FADEIN_SCREEN,
                CommandType.TINT_SCREEN,
                CommandType.FLASH_SCREEN,
                CommandType.SHAKE_SCREEN,
                CommandType.WAIT,
            ],
            "Picture/UI": [
                CommandType.SHOW_PICTURE,
                CommandType.MOVE_PICTURE,
                CommandType.ERASE_PICTURE,
            ],
            "Audio": [
                CommandType.PLAY_BGM,
                CommandType.FADEOUT_BGM,
                CommandType.PLAY_BGS,
                CommandType.FADEOUT_BGS,
                CommandType.PLAY_ME,
                CommandType.PLAY_SE,
            ],
            "Party/Actor": [
                CommandType.CHANGE_PARTY_MEMBER,
                CommandType.CHANGE_HP,
                CommandType.CHANGE_MP,
                CommandType.CHANGE_STATE,
                CommandType.RECOVER_ALL,
                CommandType.CHANGE_EXP,
                CommandType.CHANGE_LEVEL,
                CommandType.CHANGE_SKILLS,
            ],
            "Items": [
                CommandType.CHANGE_ITEMS,
                CommandType.CHANGE_WEAPONS,
                CommandType.CHANGE_ARMOR,
                CommandType.CHANGE_GOLD,
            ],
            "Advanced": [
                CommandType.SCRIPT,
                CommandType.PLUGIN_COMMAND,
            ],
        }

    def toggle(self):
        """Toggle event editor visibility."""
        self.visible = not self.visible

    def render(self):
        """Render the event editor UI."""
        if not self.visible:
            return

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        # Main panel (full screen with some padding)
        panel_width = screen_width - 40
        panel_height = screen_height - 40
        panel_x = 20
        panel_y = 20

        # Semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Main background panel
        pygame.draw.rect(
            self.screen,
            (20, 20, 30),
            (panel_x, panel_y, panel_width, panel_height),
            border_radius=8,
        )
        pygame.draw.rect(
            self.screen,
            (80, 80, 100),
            (panel_x, panel_y, panel_width, panel_height),
            2,
            border_radius=8,
        )

        # Title bar
        title_height = 50
        pygame.draw.rect(
            self.screen,
            (40, 40, 60),
            (panel_x, panel_y, panel_width, title_height),
            border_radius=8,
        )

        # Title text
        font = pygame.font.Font(None, 32)
        title_surface = font.render("Event Editor", True, (255, 200, 0))
        self.screen.blit(title_surface, (panel_x + 20, panel_y + 12))

        # Close button
        close_btn_x = panel_x + panel_width - 45
        close_btn_y = panel_y + 10
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]

        close_hover = (
            close_btn_x <= mouse_pos[0] <= close_btn_x + 35
            and close_btn_y <= mouse_pos[1] <= close_btn_y + 35
        )
        close_color = (200, 50, 50) if close_hover else (150, 0, 0)

        pygame.draw.rect(
            self.screen,
            close_color,
            (close_btn_x, close_btn_y, 35, 35),
            border_radius=4,
        )
        close_font = pygame.font.Font(None, 28)
        close_text = close_font.render("X", True, (255, 255, 255))
        self.screen.blit(close_text, (close_btn_x + 11, close_btn_y + 5))

        if close_hover and mouse_pressed:
            self.toggle()
            return

        # Content area (three panels)
        content_y = panel_y + title_height + 10
        content_height = panel_height - title_height - 20

        # Calculate panel widths
        event_list_width = 280
        command_palette_width = 300
        command_list_width = panel_width - event_list_width - command_palette_width - 40

        # Render three panels
        self._render_event_list(
            panel_x + 10, content_y, event_list_width, content_height
        )
        self._render_command_list(
            panel_x + event_list_width + 20,
            content_y,
            command_list_width,
            content_height,
        )
        self._render_command_palette(
            panel_x + event_list_width + command_list_width + 30,
            content_y,
            command_palette_width,
            content_height,
        )

    def _render_event_list(self, x: int, y: int, width: int, height: int):
        """Render the event list panel."""
        # Panel background
        pygame.draw.rect(
            self.screen, (30, 30, 45), (x, y, width, height), border_radius=6
        )
        pygame.draw.rect(
            self.screen, (60, 60, 80), (x, y, width, height), 2, border_radius=6
        )

        # Panel title
        font = pygame.font.Font(None, 22)
        title_surface = font.render("Events", True, (200, 200, 255))
        self.screen.blit(title_surface, (x + 10, y + 10))

        # New event button
        btn_y = y + 40
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]

        new_btn_hover = (
            x + 10 <= mouse_pos[0] <= x + width - 10
            and btn_y <= mouse_pos[1] <= btn_y + 35
        )
        new_btn_color = (0, 170, 0) if new_btn_hover else (0, 120, 0)

        pygame.draw.rect(
            self.screen,
            new_btn_color,
            (x + 10, btn_y, width - 20, 35),
            border_radius=4,
        )

        btn_font = pygame.font.Font(None, 20)
        btn_text = btn_font.render("+ New Event", True, (255, 255, 255))
        self.screen.blit(btn_text, (x + width // 2 - 50, btn_y + 8))

        if new_btn_hover and mouse_pressed:
            self.create_new_event()

        # Event list
        list_y = btn_y + 45
        list_height = height - 95
        item_height = 70

        # Scrollable event list
        visible_events = self.events[self.event_list_scroll :]
        current_y = list_y

        for i, event in enumerate(visible_events):
            if current_y + item_height > y + height - 10:
                break

            actual_index = i + self.event_list_scroll
            is_selected = self.current_event == event

            # Event item background
            item_color = (60, 60, 100) if is_selected else (40, 40, 60)
            pygame.draw.rect(
                self.screen,
                item_color,
                (x + 10, current_y, width - 20, item_height),
                border_radius=4,
            )

            # Event ID and name
            id_font = pygame.font.Font(None, 18)
            id_text = id_font.render(f"#{event.id:03d}", True, (255, 200, 0))
            self.screen.blit(id_text, (x + 15, current_y + 8))

            name_font = pygame.font.Font(None, 20)
            event_name = event.name if event.name else "Unnamed Event"
            name_text = name_font.render(event_name, True, (255, 255, 255))
            # Truncate if too long
            if name_text.get_width() > width - 40:
                event_name = event_name[:20] + "..."
                name_text = name_font.render(event_name, True, (255, 255, 255))
            self.screen.blit(name_text, (x + 15, current_y + 28))

            # Position info
            pos_font = pygame.font.Font(None, 16)
            pos_text = pos_font.render(
                f"Pos: ({event.x}, {event.y})", True, (180, 180, 200)
            )
            self.screen.blit(pos_text, (x + 15, current_y + 48))

            # Page count
            page_count_text = pos_font.render(
                f"Pages: {len(event.pages)}", True, (180, 180, 200)
            )
            self.screen.blit(page_count_text, (x + width - 85, current_y + 48))

            # Click to select
            if (
                x + 10 <= mouse_pos[0] <= x + width - 10
                and current_y <= mouse_pos[1] <= current_y + item_height
            ):
                if mouse_pressed:
                    self.current_event = event
                    self.current_page_index = 0
                    self.selected_command_index = None

            current_y += item_height + 5

        # Scroll indicators
        if self.event_list_scroll > 0:
            # Up arrow
            arrow_font = pygame.font.Font(None, 24)
            up_arrow = arrow_font.render("▲", True, (200, 200, 200))
            self.screen.blit(up_arrow, (x + width - 30, list_y - 5))

        if len(self.events) > len(visible_events) + self.event_list_scroll:
            # Down arrow
            arrow_font = pygame.font.Font(None, 24)
            down_arrow = arrow_font.render("▼", True, (200, 200, 200))
            self.screen.blit(down_arrow, (x + width - 30, y + height - 25))

    def _render_command_list(self, x: int, y: int, width: int, height: int):
        """Render the command list panel with indentation for nested commands."""
        # Panel background
        pygame.draw.rect(
            self.screen, (30, 30, 45), (x, y, width, height), border_radius=6
        )
        pygame.draw.rect(
            self.screen, (60, 60, 80), (x, y, width, height), 2, border_radius=6
        )

        # Panel title
        font = pygame.font.Font(None, 22)
        if self.current_event:
            title_text = f"Commands - {self.current_event.name[:15]}"
        else:
            title_text = "Commands"
        title_surface = font.render(title_text, True, (200, 200, 255))
        self.screen.blit(title_surface, (x + 10, y + 10))

        if not self.current_event:
            # Show placeholder
            placeholder_font = pygame.font.Font(None, 20)
            placeholder_text = placeholder_font.render(
                "Select an event to view commands", True, (150, 150, 150)
            )
            self.screen.blit(placeholder_text, (x + width // 2 - 130, y + height // 2))
            return

        # Page selector
        if len(self.current_event.pages) > 0:
            page_y = y + 40
            page_font = pygame.font.Font(None, 18)
            page_label = page_font.render("Page:", True, (180, 180, 200))
            self.screen.blit(page_label, (x + 10, page_y + 5))

            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()[0]

            # Page navigation buttons
            for i in range(min(len(self.current_event.pages), 5)):
                btn_x = x + 60 + i * 35
                btn_width = 30
                btn_height = 25

                is_current = i == self.current_page_index
                btn_hover = (
                    btn_x <= mouse_pos[0] <= btn_x + btn_width
                    and page_y <= mouse_pos[1] <= page_y + btn_height
                )

                if is_current:
                    btn_color = (0, 100, 200)
                elif btn_hover:
                    btn_color = (60, 60, 120)
                else:
                    btn_color = (40, 40, 80)

                pygame.draw.rect(
                    self.screen,
                    btn_color,
                    (btn_x, page_y, btn_width, btn_height),
                    border_radius=3,
                )

                btn_text = page_font.render(str(i + 1), True, (255, 255, 255))
                self.screen.blit(btn_text, (btn_x + 10, page_y + 4))

                if btn_hover and mouse_pressed and not is_current:
                    self.current_page_index = i
                    self.selected_command_index = None

            # Add page button
            if len(self.current_event.pages) < 5:
                add_btn_x = x + 60 + len(self.current_event.pages) * 35
                add_btn_width = 30
                add_btn_height = 25

                add_hover = (
                    add_btn_x <= mouse_pos[0] <= add_btn_x + add_btn_width
                    and page_y <= mouse_pos[1] <= page_y + add_btn_height
                )
                add_color = (0, 150, 0) if add_hover else (0, 100, 0)

                pygame.draw.rect(
                    self.screen,
                    add_color,
                    (add_btn_x, page_y, add_btn_width, add_btn_height),
                    border_radius=3,
                )

                add_text = page_font.render("+", True, (255, 255, 255))
                self.screen.blit(add_text, (add_btn_x + 9, page_y + 2))

                if add_hover and mouse_pressed:
                    self.add_page_to_event()

        # Command list
        list_y = y + 75
        list_height = height - 125

        if (
            self.current_page_index < len(self.current_event.pages)
            and len(self.current_event.pages) > 0
        ):
            current_page = self.current_event.pages[self.current_page_index]
            commands = current_page.commands

            # Add command button
            add_cmd_btn_y = y + height - 45
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()[0]

            add_hover = (
                x + 10 <= mouse_pos[0] <= x + width - 10
                and add_cmd_btn_y <= mouse_pos[1] <= add_cmd_btn_y + 35
            )
            add_color = (0, 120, 150) if add_hover else (0, 80, 120)

            pygame.draw.rect(
                self.screen,
                add_color,
                (x + 10, add_cmd_btn_y, width - 20, 35),
                border_radius=4,
            )

            btn_font = pygame.font.Font(None, 20)
            btn_text = btn_font.render("+ Add Command", True, (255, 255, 255))
            self.screen.blit(btn_text, (x + width // 2 - 65, add_cmd_btn_y + 8))

            # Render commands
            current_y = list_y
            item_height = 45
            indent_width = 20

            visible_commands = commands[self.command_list_scroll :]
            mouse_pos = pygame.mouse.get_pos()

            for i, command in enumerate(visible_commands):
                if current_y + item_height > add_cmd_btn_y - 5:
                    break

                actual_index = i + self.command_list_scroll
                is_selected = self.selected_command_index == actual_index
                is_hovered = (
                    x + 10 <= mouse_pos[0] <= x + width - 10
                    and current_y <= mouse_pos[1] <= current_y + item_height
                )

                # Calculate indentation
                indent = command.indent * indent_width

                # Command item background
                if is_selected:
                    item_color = (80, 80, 140)
                elif is_hovered:
                    item_color = (55, 55, 75)
                else:
                    item_color = (45, 45, 65)

                pygame.draw.rect(
                    self.screen,
                    item_color,
                    (x + 10 + indent, current_y, width - 20 - indent, item_height),
                    border_radius=4,
                )

                # Indent indicator (vertical line)
                if command.indent > 0:
                    for level in range(command.indent):
                        line_x = x + 15 + level * indent_width
                        pygame.draw.line(
                            self.screen,
                            (100, 100, 120),
                            (line_x, current_y),
                            (line_x, current_y + item_height),
                            2,
                        )

                # Command type
                cmd_font = pygame.font.Font(None, 18)
                cmd_type_text = command.command_type.name.replace("_", " ").title()
                cmd_text = cmd_font.render(cmd_type_text, True, (255, 220, 100))
                self.screen.blit(cmd_text, (x + 15 + indent, current_y + 6))

                # Command parameters preview
                param_font = pygame.font.Font(None, 16)
                param_preview = self._get_command_preview(command)
                if param_preview:
                    # Truncate if too long
                    max_width = width - 30 - indent
                    param_text = param_font.render(param_preview, True, (180, 180, 200))
                    if param_text.get_width() > max_width:
                        while (
                            len(param_preview) > 0
                            and param_text.get_width() > max_width
                        ):
                            param_preview = param_preview[:-1]
                        param_preview += "..."
                        param_text = param_font.render(
                            param_preview, True, (180, 180, 200)
                        )
                    self.screen.blit(param_text, (x + 15 + indent, current_y + 26))

                # Click to select
                if is_hovered and mouse_pressed:
                    self.selected_command_index = actual_index

                current_y += item_height + 3

            # Scroll indicators
            if self.command_list_scroll > 0:
                # Up arrow
                arrow_font = pygame.font.Font(None, 24)
                up_arrow = arrow_font.render("▲", True, (200, 200, 200))
                self.screen.blit(up_arrow, (x + width - 30, list_y - 5))

            if len(commands) > len(visible_commands) + self.command_list_scroll:
                # Down arrow
                arrow_font = pygame.font.Font(None, 24)
                down_arrow = arrow_font.render("▼", True, (200, 200, 200))
                self.screen.blit(down_arrow, (x + width - 30, add_cmd_btn_y - 30))
        else:
            # No pages yet
            no_page_font = pygame.font.Font(None, 18)
            no_page_text = no_page_font.render(
                "No pages. Click + to add a page.", True, (150, 150, 150)
            )
            self.screen.blit(no_page_text, (x + 20, list_y + 20))

    def _render_command_palette(self, x: int, y: int, width: int, height: int):
        """Render the command palette panel with categorized commands."""
        # Panel background
        pygame.draw.rect(
            self.screen, (30, 30, 45), (x, y, width, height), border_radius=6
        )
        pygame.draw.rect(
            self.screen, (60, 60, 80), (x, y, width, height), 2, border_radius=6
        )

        # Panel title
        font = pygame.font.Font(None, 22)
        title_surface = font.render("Command Palette", True, (200, 200, 255))
        self.screen.blit(title_surface, (x + 10, y + 10))

        # Scrollable command palette
        current_y = y + 45
        category_height = 30
        command_height = 32

        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]

        for category_name, command_types in self.command_categories.items():
            # Check if we're past the bottom
            if current_y > y + height - 10:
                break

            # Category header
            pygame.draw.rect(
                self.screen,
                (50, 50, 80),
                (x + 10, current_y, width - 20, category_height),
                border_radius=4,
            )

            cat_font = pygame.font.Font(None, 18)
            cat_text = cat_font.render(category_name, True, (220, 220, 255))
            self.screen.blit(cat_text, (x + 15, current_y + 8))

            current_y += category_height + 3

            # Category commands
            for cmd_type in command_types:
                if current_y + command_height > y + height - 10:
                    break

                # Command button
                is_hovered = (
                    x + 10 <= mouse_pos[0] <= x + width - 10
                    and current_y <= mouse_pos[1] <= current_y + command_height
                )

                cmd_color = (60, 80, 120) if is_hovered else (40, 50, 70)

                pygame.draw.rect(
                    self.screen,
                    cmd_color,
                    (x + 15, current_y, width - 30, command_height),
                    border_radius=3,
                )

                # Command name
                cmd_font = pygame.font.Font(None, 16)
                cmd_name = cmd_type.name.replace("_", " ").title()
                # Truncate if needed
                if len(cmd_name) > 25:
                    cmd_name = cmd_name[:22] + "..."
                cmd_text = cmd_font.render(cmd_name, True, (255, 255, 255))
                self.screen.blit(cmd_text, (x + 20, current_y + 8))

                # Click to add command
                if is_hovered and mouse_pressed:
                    self.add_command_to_current_page(cmd_type)

                current_y += command_height + 2

            current_y += 5  # Extra space between categories

        # Scroll hint
        if current_y > y + height:
            hint_font = pygame.font.Font(None, 14)
            hint_text = hint_font.render("Scroll for more...", True, (120, 120, 140))
            self.screen.blit(hint_text, (x + width - 110, y + height - 20))

    def _get_command_preview(self, command: EventCommand) -> str:
        """Get a preview string for a command's parameters."""
        cmd_type = command.command_type
        params = command.parameters

        # Generate previews based on command type
        if cmd_type == CommandType.SHOW_TEXT:
            text = params.get("text", "")
            return f'"{text[:30]}{"..." if len(text) > 30 else ""}"'
        elif cmd_type == CommandType.WAIT:
            duration = params.get("duration", 0)
            return f"{duration} frames ({duration / 60:.1f}s)"
        elif cmd_type == CommandType.CONTROL_SWITCHES:
            switch_id = params.get("switch_id", 1)
            value = "ON" if params.get("value", False) else "OFF"
            return f"Switch {switch_id} = {value}"
        elif cmd_type == CommandType.CONTROL_VARIABLES:
            var_id = params.get("variable_id", 1)
            operation = params.get("operation", "set")
            return f"Var {var_id} {operation}"
        elif cmd_type == CommandType.TRANSFER_PLAYER:
            x = params.get("x", 0)
            y = params.get("y", 0)
            map_id = params.get("map_id", 0)
            return f"Map {map_id} ({x}, {y})"
        elif cmd_type == CommandType.PLAY_BGM:
            name = params.get("name", "")
            return f'"{name}"'
        elif cmd_type == CommandType.PLAY_SE:
            name = params.get("name", "")
            return f'"{name}"'
        elif cmd_type == CommandType.COMMENT:
            return params.get("text", "")[:40]
        elif cmd_type == CommandType.LABEL:
            return f'"{params.get("name", "")}"'
        elif cmd_type == CommandType.JUMP_TO_LABEL:
            return f'→ "{params.get("label", "")}"'
        elif cmd_type == CommandType.CONDITIONAL_BRANCH:
            condition = params.get("condition_type", "")
            return f"If {condition}"
        else:
            # Generic parameter display
            if params:
                param_str = ", ".join(f"{k}: {v}" for k, v in list(params.items())[:2])
                return param_str[:40]
        return ""

    # Event management methods

    def create_new_event(self):
        """Create a new event."""
        new_id = max([e.id for e in self.events], default=0) + 1
        new_event = GameEvent(
            id=new_id,
            name=f"Event {new_id:03d}",
            x=0,
            y=0,
            pages=[],
        )
        # Add a default page
        default_page = EventPage(
            trigger=TriggerType.ACTION_BUTTON,
            commands=[],
        )
        new_event.pages.append(default_page)

        self.events.append(new_event)
        self.current_event = new_event
        self.current_page_index = 0
        self.selected_command_index = None

    def add_page_to_event(self):
        """Add a new page to the current event."""
        if not self.current_event:
            return

        new_page = EventPage(
            trigger=TriggerType.ACTION_BUTTON,
            commands=[],
        )
        self.current_event.pages.append(new_page)
        self.current_page_index = len(self.current_event.pages) - 1
        self.selected_command_index = None

    def add_command_to_current_page(self, command_type: CommandType):
        """Add a command to the current page."""
        if not self.current_event:
            return

        if self.current_page_index >= len(self.current_event.pages):
            return

        current_page = self.current_event.pages[self.current_page_index]

        # Create a new command with default parameters
        new_command = EventCommand(
            command_type=command_type,
            parameters=self._get_default_parameters(command_type),
            indent=0,
        )

        # If a command is selected, insert after it
        if self.selected_command_index is not None:
            insert_index = self.selected_command_index + 1
            # Match indent level of selected command
            if self.selected_command_index < len(current_page.commands):
                new_command.indent = current_page.commands[
                    self.selected_command_index
                ].indent
            current_page.commands.insert(insert_index, new_command)
            self.selected_command_index = insert_index
        else:
            # Add to end
            current_page.commands.append(new_command)
            self.selected_command_index = len(current_page.commands) - 1

    def _get_default_parameters(self, command_type: CommandType) -> Dict[str, Any]:
        """Get default parameters for a command type."""
        defaults = {
            CommandType.SHOW_TEXT: {
                "text": "New message",
                "face_name": None,
                "face_index": 0,
                "background": 0,
                "position": 2,
            },
            CommandType.SHOW_CHOICES: {
                "choices": ["Choice 1", "Choice 2"],
                "cancel_type": -1,
                "default_choice": 0,
            },
            CommandType.WAIT: {"duration": 60},
            CommandType.CONTROL_SWITCHES: {
                "switch_id": 1,
                "value": True,
                "end_id": None,
            },
            CommandType.CONTROL_VARIABLES: {
                "variable_id": 1,
                "operation": "set",
                "operand_type": "constant",
                "operand_value": 0,
                "end_id": None,
            },
            CommandType.TRANSFER_PLAYER: {
                "map_id": 0,
                "x": 0,
                "y": 0,
                "direction": 0,
                "fade_type": 0,
            },
            CommandType.PLAY_BGM: {
                "name": "bgm_001",
                "volume": 90,
                "pitch": 100,
                "pan": 0,
            },
            CommandType.PLAY_SE: {
                "name": "se_001",
                "volume": 90,
                "pitch": 100,
                "pan": 0,
            },
            CommandType.COMMENT: {"text": "Comment"},
            CommandType.LABEL: {"name": "label_1"},
            CommandType.JUMP_TO_LABEL: {"label": "label_1"},
            CommandType.CONDITIONAL_BRANCH: {
                "condition_type": "switch",
                "switch_id": 1,
            },
        }

        return defaults.get(command_type, {})

    def handle_scroll(self, event: pygame.event.Event):
        """Handle mouse wheel scrolling."""
        if not self.visible:
            return

        if event.type == pygame.MOUSEWHEEL:
            mouse_pos = pygame.mouse.get_pos()

            # Determine which panel to scroll based on mouse position
            # This is a simplified version - you'd want to properly detect panel bounds
            if event.y > 0:  # Scroll up
                if self.command_list_scroll > 0:
                    self.command_list_scroll -= 1
                elif self.event_list_scroll > 0:
                    self.event_list_scroll -= 1
            elif event.y < 0:  # Scroll down
                # Scroll down logic would check bounds
                pass

    def load_events_from_scene(self, events: List[GameEvent]):
        """Load events from a scene."""
        self.events = events
        if self.events:
            self.current_event = self.events[0]
            self.current_page_index = 0
        else:
            self.current_event = None
        self.selected_command_index = None
        self.event_list_scroll = 0
        self.command_list_scroll = 0

    def get_events(self) -> List[GameEvent]:
        """Get the current event list."""
        return self.events
