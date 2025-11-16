"""
Tool Options Panel - Current tool settings editor

Displays and allows editing of settings for the currently active map tool:
- Brush size slider
- Tool-specific parameters
- Quick presets
- Color pickers
- Shape options
- Pattern selectors
"""

from typing import Any, Dict, Optional

import pygame

from neonworks.ui.map_tools.base import MapTool


class ToolOptionsPanel:
    """
    Panel for displaying and editing current tool settings.

    Features:
    - Dynamic UI based on active tool
    - Sliders for numeric values
    - Checkboxes for boolean options
    - Color pickers for color values
    - Dropdowns for enum values
    - Preset management
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int = 250,
        height: int = 300,
    ):
        """
        Initialize the tool options panel.

        Args:
            x: Panel X position
            y: Panel Y position
            width: Panel width
            height: Panel height
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # State
        self.visible = True
        self.active_tool: Optional[MapTool] = None
        self.tool_settings: Dict[str, Any] = {}

        # UI state
        self.scroll_offset = 0
        self.dragging_slider: Optional[str] = None
        self.hover_element: Optional[str] = None

        # Colors
        self.bg_color = (40, 40, 45)
        self.header_color = (50, 50, 55)
        self.control_bg_color = (60, 60, 65)
        self.control_hover_color = (70, 70, 75)
        self.slider_bg_color = (50, 50, 55)
        self.slider_fill_color = (100, 150, 255)
        self.text_color = (220, 220, 220)
        self.text_dim_color = (150, 150, 150)
        self.border_color = (80, 80, 85)

        # Fonts
        self.font = pygame.font.Font(None, 18)
        self.small_font = pygame.font.Font(None, 14)
        self.title_font = pygame.font.Font(None, 20)

        # Layout
        self.header_height = 35
        self.control_height = 30
        self.control_spacing = 10
        self.label_width = 100
        self.padding = 10

    def set_active_tool(self, tool: Optional[MapTool]):
        """
        Set the active tool to display options for.

        Args:
            tool: MapTool instance or None
        """
        self.active_tool = tool
        self.tool_settings = {}

        if tool:
            # Get tool-specific settings
            if hasattr(tool, "get_settings"):
                self.tool_settings = tool.get_settings()
            else:
                # Default settings for all tools
                self.tool_settings = {
                    "brush_size": getattr(tool, "brush_size", 1),
                }

    def toggle_visibility(self):
        """Toggle panel visibility."""
        self.visible = not self.visible

    def update(self, dt: float):
        """
        Update panel state.

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
        Render the tool options panel.

        Args:
            screen: Surface to render on
        """
        if not self.visible:
            return

        # Draw background
        pygame.draw.rect(screen, self.bg_color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, self.border_color, (self.x, self.y, self.width, self.height), 2)

        # Draw header
        self._draw_header(screen)

        # Draw tool options
        if self.active_tool:
            self._draw_tool_options(screen)
        else:
            self._draw_no_tool_message(screen)

    def _draw_header(self, screen: pygame.Surface):
        """Draw the panel header."""
        # Header background
        pygame.draw.rect(
            screen,
            self.header_color,
            (self.x, self.y, self.width, self.header_height),
        )

        # Title
        title = "Tool Options"
        if self.active_tool:
            title = f"{self.active_tool.name} Options"

        title_text = self.title_font.render(title, True, self.text_color)
        title_rect = title_text.get_rect(
            center=(self.x + self.width // 2, self.y + self.header_height // 2)
        )
        screen.blit(title_text, title_rect)

        # Close button
        close_x = self.x + self.width - 25
        close_y = self.y + 7
        close_rect = pygame.Rect(close_x, close_y, 20, 20)
        pygame.draw.rect(screen, (80, 80, 85), close_rect, border_radius=3)
        close_text = self.small_font.render("X", True, self.text_color)
        close_text_rect = close_text.get_rect(center=close_rect.center)
        screen.blit(close_text, close_text_rect)

    def _draw_no_tool_message(self, screen: pygame.Surface):
        """Draw message when no tool is selected."""
        message = "No tool selected"
        message_text = self.font.render(message, True, self.text_dim_color)
        message_rect = message_text.get_rect(
            center=(self.x + self.width // 2, self.y + self.header_height + 50)
        )
        screen.blit(message_text, message_rect)

    def _draw_tool_options(self, screen: pygame.Surface):
        """Draw tool-specific options."""
        current_y = self.y + self.header_height + self.padding

        # Draw each setting
        for setting_name, setting_value in self.tool_settings.items():
            current_y = self._draw_setting(screen, setting_name, setting_value, current_y)
            current_y += self.control_spacing

        # Draw presets section
        current_y += self.control_spacing
        current_y = self._draw_presets_section(screen, current_y)

    def _draw_setting(self, screen: pygame.Surface, name: str, value: Any, y: int) -> int:
        """
        Draw a single setting control.

        Args:
            screen: Surface to render on
            name: Setting name
            value: Setting value
            y: Y position to draw at

        Returns:
            Y position after drawing
        """
        # Label
        label = name.replace("_", " ").title()
        label_text = self.font.render(label, True, self.text_color)
        screen.blit(label_text, (self.x + self.padding, y + 5))

        # Value control based on type
        control_x = self.x + self.label_width + self.padding
        control_width = self.width - self.label_width - self.padding * 2

        if isinstance(value, bool):
            # Checkbox
            self._draw_checkbox(screen, name, value, control_x, y, control_width)
            return y + self.control_height

        elif isinstance(value, int) or isinstance(value, float):
            # Slider
            self._draw_slider(screen, name, value, control_x, y, control_width)
            return y + self.control_height

        elif isinstance(value, str):
            # Text input or dropdown
            self._draw_text_input(screen, name, value, control_x, y, control_width)
            return y + self.control_height

        elif isinstance(value, tuple) and len(value) == 3:
            # Color picker (RGB)
            self._draw_color_picker(screen, name, value, control_x, y, control_width)
            return y + self.control_height

        else:
            # Unknown type, just display value
            value_text = self.small_font.render(str(value), True, self.text_dim_color)
            screen.blit(value_text, (control_x, y + 5))
            return y + self.control_height

    def _draw_checkbox(
        self, screen: pygame.Surface, name: str, value: bool, x: int, y: int, width: int
    ):
        """Draw a checkbox control."""
        checkbox_size = 20
        checkbox_rect = pygame.Rect(x, y + 5, checkbox_size, checkbox_size)

        # Background
        bg_color = self.control_hover_color if self.hover_element == name else self.control_bg_color
        pygame.draw.rect(screen, bg_color, checkbox_rect, border_radius=3)
        pygame.draw.rect(screen, self.border_color, checkbox_rect, 1, border_radius=3)

        # Checkmark
        if value:
            pygame.draw.line(
                screen,
                self.slider_fill_color,
                (x + 4, y + 13),
                (x + 8, y + 17),
                2,
            )
            pygame.draw.line(
                screen,
                self.slider_fill_color,
                (x + 8, y + 17),
                (x + 16, y + 9),
                2,
            )

    def _draw_slider(
        self, screen: pygame.Surface, name: str, value: float, x: int, y: int, width: int
    ):
        """Draw a slider control."""
        slider_height = 20
        slider_y = y + 5

        # Slider background
        bg_color = self.control_hover_color if self.hover_element == name else self.slider_bg_color
        pygame.draw.rect(
            screen,
            bg_color,
            (x, slider_y, width, slider_height),
            border_radius=3,
        )

        # Slider fill (assume value is between 0-100 or 0-10 for brush size)
        max_value = 100
        if name == "brush_size":
            max_value = 20
        elif name == "opacity":
            max_value = 100

        fill_width = int((value / max_value) * width)
        pygame.draw.rect(
            screen,
            self.slider_fill_color,
            (x, slider_y, fill_width, slider_height),
            border_radius=3,
        )

        # Border
        pygame.draw.rect(
            screen,
            self.border_color,
            (x, slider_y, width, slider_height),
            1,
            border_radius=3,
        )

        # Value label
        value_str = f"{int(value)}"
        value_text = self.small_font.render(value_str, True, self.text_color)
        value_rect = value_text.get_rect(center=(x + width // 2, slider_y + slider_height // 2))
        screen.blit(value_text, value_rect)

    def _draw_text_input(
        self, screen: pygame.Surface, name: str, value: str, x: int, y: int, width: int
    ):
        """Draw a text input control."""
        input_height = 25
        input_y = y + 2

        # Background
        bg_color = self.control_hover_color if self.hover_element == name else self.control_bg_color
        pygame.draw.rect(
            screen,
            bg_color,
            (x, input_y, width, input_height),
            border_radius=3,
        )
        pygame.draw.rect(
            screen,
            self.border_color,
            (x, input_y, width, input_height),
            1,
            border_radius=3,
        )

        # Text
        text_surface = self.small_font.render(value[:20], True, self.text_color)
        screen.blit(text_surface, (x + 5, input_y + 5))

    def _draw_color_picker(
        self, screen: pygame.Surface, name: str, value: tuple, x: int, y: int, width: int
    ):
        """Draw a color picker control."""
        swatch_size = 25
        swatch_y = y + 2

        # Color swatch
        pygame.draw.rect(
            screen,
            value,
            (x, swatch_y, swatch_size, swatch_size),
            border_radius=3,
        )
        pygame.draw.rect(
            screen,
            self.border_color,
            (x, swatch_y, swatch_size, swatch_size),
            1,
            border_radius=3,
        )

        # RGB values
        rgb_text = f"RGB({value[0]}, {value[1]}, {value[2]})"
        rgb_surface = self.small_font.render(rgb_text, True, self.text_dim_color)
        screen.blit(rgb_surface, (x + swatch_size + 5, swatch_y + 5))

    def _draw_presets_section(self, screen: pygame.Surface, y: int) -> int:
        """Draw presets section."""
        # Section title
        title_text = self.font.render("Presets", True, self.text_color)
        screen.blit(title_text, (self.x + self.padding, y))
        y += 25

        # Preset buttons
        presets = ["Small", "Medium", "Large"]
        button_width = (self.width - self.padding * 2 - 10) // 3
        button_height = 25

        for i, preset in enumerate(presets):
            button_x = self.x + self.padding + i * (button_width + 5)
            button_rect = pygame.Rect(button_x, y, button_width, button_height)

            # Background
            bg_color = (
                self.control_hover_color
                if self.hover_element == f"preset_{preset}"
                else self.control_bg_color
            )
            pygame.draw.rect(screen, bg_color, button_rect, border_radius=3)
            pygame.draw.rect(screen, self.border_color, button_rect, 1, border_radius=3)

            # Text
            preset_text = self.small_font.render(preset, True, self.text_color)
            preset_rect = preset_text.get_rect(center=button_rect.center)
            screen.blit(preset_text, preset_rect)

        return y + button_height

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

            # Check close button
            close_x = self.x + self.width - 25
            close_y = self.y + 7
            if close_x <= mouse_x <= close_x + 20 and close_y <= mouse_y <= close_y + 20:
                self.toggle_visibility()
                return True

            # Check if click is on a control
            element = self._get_element_at_pos(mouse_x, mouse_y)
            if element:
                self._handle_element_click(element)
                return True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging_slider = None

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_slider:
                self._update_slider_value(event.pos[0])
                return True

        return False

    def _get_element_at_pos(self, x: int, y: int) -> Optional[str]:
        """Get the UI element at the given position."""
        if not (self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height):
            return None

        # Calculate which setting row the mouse is over
        current_y = self.y + self.header_height + self.padding

        for setting_name in self.tool_settings.keys():
            if current_y <= y <= current_y + self.control_height:
                return setting_name
            current_y += self.control_height + self.control_spacing

        return None

    def _handle_element_click(self, element: str):
        """Handle click on a UI element."""
        if element in self.tool_settings:
            value = self.tool_settings[element]

            if isinstance(value, bool):
                # Toggle checkbox
                self.tool_settings[element] = not value
                if self.active_tool and hasattr(self.active_tool, "set_setting"):
                    self.active_tool.set_setting(element, not value)

            elif isinstance(value, (int, float)):
                # Start dragging slider
                self.dragging_slider = element

    def _update_slider_value(self, mouse_x: int):
        """Update slider value based on mouse position."""
        if not self.dragging_slider:
            return

        control_x = self.x + self.label_width + self.padding
        control_width = self.width - self.label_width - self.padding * 2

        # Calculate new value
        relative_x = mouse_x - control_x
        percent = max(0, min(1, relative_x / control_width))

        # Determine max value based on setting name
        max_value = 100
        if self.dragging_slider == "brush_size":
            max_value = 20
        elif self.dragging_slider == "opacity":
            max_value = 100

        new_value = int(percent * max_value)

        # Update setting
        self.tool_settings[self.dragging_slider] = new_value
        if self.active_tool and hasattr(self.active_tool, "set_setting"):
            self.active_tool.set_setting(self.dragging_slider, new_value)
