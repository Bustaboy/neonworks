"""
Map Properties Dialog - Map settings editor

Provides a dialog for editing map-wide settings:
- Map dimensions (width, height, resize)
- Tile size configuration
- Default properties (music, encounter rate)
- Tileset assignment
- Parallax background settings
- Wrap/loop settings
- Export settings
"""

from typing import Any, Callable, Dict, Optional

import pygame


class MapPropertiesDialog:
    """
    Dialog for editing map properties and settings.

    Features:
    - Map dimension editing with resize options
    - Tile size configuration
    - Background music selection
    - Encounter rate settings
    - Tileset management
    - Parallax and scrolling settings
    - Map metadata (name, description)
    """

    def __init__(
        self,
        on_apply: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_cancel: Optional[Callable[[], None]] = None,
    ):
        """
        Initialize the map properties dialog.

        Args:
            on_apply: Callback when properties are applied (properties_dict)
            on_cancel: Callback when dialog is cancelled
        """
        self.on_apply = on_apply
        self.on_cancel = on_cancel

        # Dialog state
        self.visible = False
        self.properties: Dict[str, Any] = {}

        # UI state
        self.active_tab = "general"  # general, tileset, gameplay, advanced
        self.focused_field: Optional[str] = None
        self.scroll_offset = 0

        # Dialog dimensions
        screen_info = pygame.display.Info()
        self.width = 600
        self.height = 500
        self.x = (screen_info.current_w - self.width) // 2
        self.y = (screen_info.current_h - self.height) // 2

        # Colors
        self.bg_color = (40, 40, 45)
        self.header_color = (50, 50, 55)
        self.tab_active_color = (70, 70, 80)
        self.tab_inactive_color = (50, 50, 55)
        self.field_bg_color = (60, 60, 65)
        self.field_focus_color = (70, 70, 75)
        self.button_color = (100, 150, 255)
        self.button_hover_color = (120, 170, 255)
        self.text_color = (220, 220, 220)
        self.text_dim_color = (150, 150, 150)
        self.border_color = (80, 80, 85)

        # Fonts
        self.font = pygame.font.Font(None, 18)
        self.small_font = pygame.font.Font(None, 14)
        self.title_font = pygame.font.Font(None, 24)

        # Layout
        self.header_height = 40
        self.tab_height = 35
        self.field_height = 30
        self.field_spacing = 10
        self.padding = 15
        self.label_width = 150

        # Hover state
        self.hover_element: Optional[str] = None

    def show(self, properties: Optional[Dict[str, Any]] = None):
        """
        Show the dialog with given properties.

        Args:
            properties: Initial property values
        """
        self.visible = True
        self.properties = properties or self._get_default_properties()

    def hide(self):
        """Hide the dialog."""
        self.visible = False

    def toggle(self):
        """Toggle dialog visibility."""
        if self.visible:
            self.hide()
        else:
            self.show()

    def _get_default_properties(self) -> Dict[str, Any]:
        """Get default map properties."""
        return {
            # General
            "name": "Untitled Map",
            "description": "",
            "width": 50,
            "height": 50,
            "tile_size": 32,
            # Tileset
            "tileset_id": None,
            "autotile_enabled": True,
            # Gameplay
            "bgm": None,
            "encounter_enabled": False,
            "encounter_rate": 30,
            "battleback": None,
            # Advanced
            "wrap_x": False,
            "wrap_y": False,
            "parallax_background": None,
            "parallax_scroll_x": 0.0,
            "parallax_scroll_y": 0.0,
        }

    def update(self, dt: float):
        """
        Update dialog state.

        Args:
            dt: Delta time in seconds
        """
        if not self.visible:
            return

        # Update hover state
        mouse_pos = pygame.mouse.get_pos()
        self.hover_element = self._get_element_at_pos(mouse_pos[0], mouse_pos[1])

    def render(self, screen: pygame.Surface):
        """
        Render the dialog.

        Args:
            screen: Surface to render on
        """
        if not self.visible:
            return

        # Darken background
        overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # Draw dialog background
        pygame.draw.rect(screen, self.bg_color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, self.border_color, (self.x, self.y, self.width, self.height), 2)

        # Draw header
        self._draw_header(screen)

        # Draw tabs
        self._draw_tabs(screen)

        # Draw content
        self._draw_content(screen)

        # Draw buttons
        self._draw_buttons(screen)

    def _draw_header(self, screen: pygame.Surface):
        """Draw the dialog header."""
        # Header background
        pygame.draw.rect(
            screen,
            self.header_color,
            (self.x, self.y, self.width, self.header_height),
        )

        # Title
        title_text = self.title_font.render("Map Properties", True, self.text_color)
        title_rect = title_text.get_rect(
            center=(self.x + self.width // 2, self.y + self.header_height // 2)
        )
        screen.blit(title_text, title_rect)

        # Close button
        close_x = self.x + self.width - 30
        close_y = self.y + 10
        close_rect = pygame.Rect(close_x, close_y, 20, 20)
        is_hover = self.hover_element == "close"
        close_color = self.button_hover_color if is_hover else (80, 80, 85)
        pygame.draw.rect(screen, close_color, close_rect, border_radius=3)
        close_text = self.small_font.render("X", True, self.text_color)
        close_text_rect = close_text.get_rect(center=close_rect.center)
        screen.blit(close_text, close_text_rect)

    def _draw_tabs(self, screen: pygame.Surface):
        """Draw the tab bar."""
        tabs = [
            ("general", "General"),
            ("tileset", "Tileset"),
            ("gameplay", "Gameplay"),
            ("advanced", "Advanced"),
        ]

        tab_width = self.width // len(tabs)
        tab_y = self.y + self.header_height

        for i, (tab_id, tab_name) in enumerate(tabs):
            tab_x = self.x + i * tab_width
            is_active = self.active_tab == tab_id
            is_hover = self.hover_element == f"tab_{tab_id}"

            # Tab background
            tab_color = self.tab_active_color if is_active else self.tab_inactive_color
            if is_hover and not is_active:
                tab_color = tuple(min(c + 10, 255) for c in tab_color)

            pygame.draw.rect(
                screen,
                tab_color,
                (tab_x, tab_y, tab_width, self.tab_height),
            )

            # Tab border
            pygame.draw.line(
                screen,
                self.border_color,
                (tab_x, tab_y),
                (tab_x, tab_y + self.tab_height),
            )

            # Tab text
            tab_text = self.font.render(tab_name, True, self.text_color)
            tab_text_rect = tab_text.get_rect(
                center=(tab_x + tab_width // 2, tab_y + self.tab_height // 2)
            )
            screen.blit(tab_text, tab_text_rect)

    def _draw_content(self, screen: pygame.Surface):
        """Draw the content area based on active tab."""
        content_y = self.y + self.header_height + self.tab_height + self.padding
        content_height = self.height - self.header_height - self.tab_height - 80

        # Draw content based on active tab
        if self.active_tab == "general":
            self._draw_general_tab(screen, content_y, content_height)
        elif self.active_tab == "tileset":
            self._draw_tileset_tab(screen, content_y, content_height)
        elif self.active_tab == "gameplay":
            self._draw_gameplay_tab(screen, content_y, content_height)
        elif self.active_tab == "advanced":
            self._draw_advanced_tab(screen, content_y, content_height)

    def _draw_general_tab(self, screen: pygame.Surface, y: int, height: int):
        """Draw general tab content."""
        fields = [
            ("name", "Map Name:", "text"),
            ("description", "Description:", "text"),
            ("width", "Width (tiles):", "number"),
            ("height", "Height (tiles):", "number"),
            ("tile_size", "Tile Size (px):", "number"),
        ]

        current_y = y
        for field_id, label, field_type in fields:
            current_y = self._draw_field(
                screen, field_id, label, self.properties.get(field_id), field_type, current_y
            )
            current_y += self.field_spacing

    def _draw_tileset_tab(self, screen: pygame.Surface, y: int, height: int):
        """Draw tileset tab content."""
        fields = [
            ("tileset_id", "Tileset:", "dropdown"),
            ("autotile_enabled", "Auto-tiling:", "checkbox"),
        ]

        current_y = y
        for field_id, label, field_type in fields:
            current_y = self._draw_field(
                screen, field_id, label, self.properties.get(field_id), field_type, current_y
            )
            current_y += self.field_spacing

    def _draw_gameplay_tab(self, screen: pygame.Surface, y: int, height: int):
        """Draw gameplay tab content."""
        fields = [
            ("bgm", "Background Music:", "dropdown"),
            ("encounter_enabled", "Random Encounters:", "checkbox"),
            ("encounter_rate", "Encounter Rate:", "number"),
            ("battleback", "Battle Background:", "dropdown"),
        ]

        current_y = y
        for field_id, label, field_type in fields:
            current_y = self._draw_field(
                screen, field_id, label, self.properties.get(field_id), field_type, current_y
            )
            current_y += self.field_spacing

    def _draw_advanced_tab(self, screen: pygame.Surface, y: int, height: int):
        """Draw advanced tab content."""
        fields = [
            ("wrap_x", "Wrap Horizontally:", "checkbox"),
            ("wrap_y", "Wrap Vertically:", "checkbox"),
            ("parallax_background", "Parallax BG:", "dropdown"),
            ("parallax_scroll_x", "Parallax Scroll X:", "number"),
            ("parallax_scroll_y", "Parallax Scroll Y:", "number"),
        ]

        current_y = y
        for field_id, label, field_type in fields:
            current_y = self._draw_field(
                screen, field_id, label, self.properties.get(field_id), field_type, current_y
            )
            current_y += self.field_spacing

    def _draw_field(
        self,
        screen: pygame.Surface,
        field_id: str,
        label: str,
        value: Any,
        field_type: str,
        y: int,
    ) -> int:
        """
        Draw a single field.

        Args:
            screen: Surface to render on
            field_id: Field identifier
            label: Field label text
            value: Field value
            field_type: Field type (text, number, checkbox, dropdown)
            y: Y position

        Returns:
            Y position after drawing
        """
        # Label
        label_text = self.font.render(label, True, self.text_color)
        screen.blit(label_text, (self.x + self.padding, y))

        # Field control
        field_x = self.x + self.label_width + self.padding
        field_width = self.width - self.label_width - self.padding * 2

        if field_type == "checkbox":
            self._draw_checkbox_field(screen, field_id, value, field_x, y)
        elif field_type == "number":
            self._draw_number_field(screen, field_id, value, field_x, y, field_width)
        elif field_type == "text":
            self._draw_text_field(screen, field_id, value, field_x, y, field_width)
        elif field_type == "dropdown":
            self._draw_dropdown_field(screen, field_id, value, field_x, y, field_width)

        return y + self.field_height

    def _draw_checkbox_field(
        self, screen: pygame.Surface, field_id: str, value: bool, x: int, y: int
    ):
        """Draw a checkbox field."""
        checkbox_size = 20
        checkbox_rect = pygame.Rect(x, y, checkbox_size, checkbox_size)

        is_hover = self.hover_element == f"field_{field_id}"
        bg_color = self.field_focus_color if is_hover else self.field_bg_color

        pygame.draw.rect(screen, bg_color, checkbox_rect, border_radius=3)
        pygame.draw.rect(screen, self.border_color, checkbox_rect, 1, border_radius=3)

        if value:
            pygame.draw.line(screen, self.button_color, (x + 4, y + 10), (x + 8, y + 14), 2)
            pygame.draw.line(screen, self.button_color, (x + 8, y + 14), (x + 16, y + 6), 2)

    def _draw_number_field(
        self, screen: pygame.Surface, field_id: str, value: Any, x: int, y: int, width: int
    ):
        """Draw a number input field."""
        is_focused = self.focused_field == field_id
        is_hover = self.hover_element == f"field_{field_id}"
        bg_color = self.field_focus_color if (is_focused or is_hover) else self.field_bg_color

        input_width = 100
        pygame.draw.rect(
            screen,
            bg_color,
            (x, y, input_width, self.field_height),
            border_radius=3,
        )
        pygame.draw.rect(
            screen,
            self.border_color,
            (x, y, input_width, self.field_height),
            1,
            border_radius=3,
        )

        value_text = self.font.render(
            str(value) if value is not None else "", True, self.text_color
        )
        screen.blit(value_text, (x + 5, y + 5))

    def _draw_text_field(
        self, screen: pygame.Surface, field_id: str, value: Any, x: int, y: int, width: int
    ):
        """Draw a text input field."""
        is_focused = self.focused_field == field_id
        is_hover = self.hover_element == f"field_{field_id}"
        bg_color = self.field_focus_color if (is_focused or is_hover) else self.field_bg_color

        pygame.draw.rect(
            screen,
            bg_color,
            (x, y, width, self.field_height),
            border_radius=3,
        )
        pygame.draw.rect(
            screen,
            self.border_color,
            (x, y, width, self.field_height),
            1,
            border_radius=3,
        )

        value_text = self.font.render(str(value) if value else "", True, self.text_color)
        screen.blit(value_text, (x + 5, y + 5))

    def _draw_dropdown_field(
        self, screen: pygame.Surface, field_id: str, value: Any, x: int, y: int, width: int
    ):
        """Draw a dropdown field."""
        is_hover = self.hover_element == f"field_{field_id}"
        bg_color = self.field_focus_color if is_hover else self.field_bg_color

        pygame.draw.rect(
            screen,
            bg_color,
            (x, y, width, self.field_height),
            border_radius=3,
        )
        pygame.draw.rect(
            screen,
            self.border_color,
            (x, y, width, self.field_height),
            1,
            border_radius=3,
        )

        value_text = self.font.render(str(value) if value else "None", True, self.text_color)
        screen.blit(value_text, (x + 5, y + 5))

        # Dropdown arrow
        arrow_x = x + width - 20
        arrow_y = y + self.field_height // 2
        pygame.draw.polygon(
            screen,
            self.text_dim_color,
            [
                (arrow_x, arrow_y - 3),
                (arrow_x + 8, arrow_y - 3),
                (arrow_x + 4, arrow_y + 3),
            ],
        )

    def _draw_buttons(self, screen: pygame.Surface):
        """Draw OK/Cancel buttons."""
        button_y = self.y + self.height - 50
        button_width = 100
        button_height = 35
        button_spacing = 10

        # OK button
        ok_x = self.x + self.width - button_width * 2 - button_spacing - self.padding
        is_ok_hover = self.hover_element == "button_ok"
        ok_color = self.button_hover_color if is_ok_hover else self.button_color

        ok_rect = pygame.Rect(ok_x, button_y, button_width, button_height)
        pygame.draw.rect(screen, ok_color, ok_rect, border_radius=5)

        ok_text = self.font.render("OK", True, (255, 255, 255))
        ok_text_rect = ok_text.get_rect(center=ok_rect.center)
        screen.blit(ok_text, ok_text_rect)

        # Cancel button
        cancel_x = self.x + self.width - button_width - self.padding
        is_cancel_hover = self.hover_element == "button_cancel"
        cancel_color = (120, 120, 130) if is_cancel_hover else (80, 80, 90)

        cancel_rect = pygame.Rect(cancel_x, button_y, button_width, button_height)
        pygame.draw.rect(screen, cancel_color, cancel_rect, border_radius=5)

        cancel_text = self.font.render("Cancel", True, (255, 255, 255))
        cancel_text_rect = cancel_text.get_rect(center=cancel_rect.center)
        screen.blit(cancel_text, cancel_text_rect)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle input events.

        Args:
            event: Pygame event

        Returns:
            True if event was handled, False otherwise
        """
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            element = self._get_element_at_pos(mouse_x, mouse_y)

            if element:
                self._handle_element_click(element)
                return True

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._handle_cancel()
                return True
            elif event.key == pygame.K_RETURN:
                self._handle_apply()
                return True

        return False

    def _get_element_at_pos(self, x: int, y: int) -> Optional[str]:
        """Get the UI element at the given position."""
        # Check if outside dialog
        if not (self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height):
            return None

        # Check close button
        close_x = self.x + self.width - 30
        close_y = self.y + 10
        if close_x <= x <= close_x + 20 and close_y <= y <= close_y + 20:
            return "close"

        # Check tabs
        tab_y = self.y + self.header_height
        if tab_y <= y <= tab_y + self.tab_height:
            tabs = ["general", "tileset", "gameplay", "advanced"]
            tab_width = self.width // len(tabs)
            tab_index = (x - self.x) // tab_width
            if 0 <= tab_index < len(tabs):
                return f"tab_{tabs[tab_index]}"

        # Check buttons
        button_y = self.y + self.height - 50
        button_height = 35
        button_width = 100

        ok_x = self.x + self.width - button_width * 2 - 10 - self.padding
        if ok_x <= x <= ok_x + button_width and button_y <= y <= button_y + button_height:
            return "button_ok"

        cancel_x = self.x + self.width - button_width - self.padding
        if cancel_x <= x <= cancel_x + button_width and button_y <= y <= button_y + button_height:
            return "button_cancel"

        return None

    def _handle_element_click(self, element: str):
        """Handle click on a UI element."""
        if element == "close" or element == "button_cancel":
            self._handle_cancel()
        elif element == "button_ok":
            self._handle_apply()
        elif element.startswith("tab_"):
            tab_id = element[4:]
            self.active_tab = tab_id

    def _handle_apply(self):
        """Handle apply button click."""
        if self.on_apply:
            self.on_apply(self.properties)
        self.hide()

    def _handle_cancel(self):
        """Handle cancel button click."""
        if self.on_cancel:
            self.on_cancel()
        self.hide()
