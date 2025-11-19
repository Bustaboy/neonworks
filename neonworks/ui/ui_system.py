"""
UI System

Comprehensive UI system with widgets, layouts, and event handling.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple

import pygame


class Anchor(Enum):
    """UI anchor positions"""

    TOP_LEFT = "top_left"
    TOP_CENTER = "top_center"
    TOP_RIGHT = "top_right"
    CENTER_LEFT = "center_left"
    CENTER = "center"
    CENTER_RIGHT = "center_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_CENTER = "bottom_center"
    BOTTOM_RIGHT = "bottom_right"


@dataclass
class UIStyle:
    """Style properties for UI elements"""

    # Colors
    background_color: Tuple[int, int, int, int] = (50, 50, 50, 200)
    border_color: Tuple[int, int, int, int] = (150, 150, 150, 255)
    text_color: Tuple[int, int, int, int] = (255, 255, 255, 255)
    hover_color: Tuple[int, int, int, int] = (70, 70, 70, 200)
    active_color: Tuple[int, int, int, int] = (90, 90, 90, 200)
    disabled_color: Tuple[int, int, int, int] = (80, 80, 80, 150)

    # Sizing
    padding: int = 10
    margin: int = 5
    border_width: int = 2

    # Font
    font_name: Optional[str] = None
    font_size: int = 16


class UIWidget(ABC):
    """Base class for all UI widgets"""

    def __init__(self, x: int = 0, y: int = 0, width: int = 100, height: int = 30):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # State
        self.visible = True
        self.enabled = True
        self.hovered = False
        self.pressed = False

        # Layout
        self.anchor = Anchor.TOP_LEFT
        self.parent: Optional["UIContainer"] = None

        # Style
        self.style = UIStyle()

        # Tooltip
        self.tooltip: Optional[str] = None
        self.tooltip_delay: float = 0.5  # seconds

        # Events
        self.on_click: Optional[Callable[[], None]] = None
        self.on_hover_enter: Optional[Callable[[], None]] = None
        self.on_hover_exit: Optional[Callable[[], None]] = None

    def get_rect(self) -> pygame.Rect:
        """Get the widget's rectangle"""
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def contains_point(self, x: int, y: int) -> bool:
        """Check if point is inside widget"""
        rect = self.get_rect()
        return rect.collidepoint(x, y)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame event.

        Returns:
            True if event was handled (stops propagation)
        """
        if not self.visible or not self.enabled:
            return False

        if event.type == pygame.MOUSEMOTION:
            was_hovered = self.hovered
            self.hovered = self.contains_point(event.pos[0], event.pos[1])

            if self.hovered and not was_hovered and self.on_hover_enter:
                self.on_hover_enter()
            elif not self.hovered and was_hovered and self.on_hover_exit:
                self.on_hover_exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.contains_point(event.pos[0], event.pos[1]):
                    self.pressed = True
                    return True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.pressed and self.contains_point(event.pos[0], event.pos[1]):
                    if self.on_click:
                        self.on_click()
                    self.pressed = False
                    return True
                self.pressed = False

        return False

    @abstractmethod
    def render(self, screen: pygame.Surface):
        """Render the widget"""
        pass

    def update(self, delta_time: float):
        """Update widget (for animations, etc.)"""
        pass


class UILabel(UIWidget):
    """Text label widget"""

    def __init__(self, text: str = "", color: Optional[Tuple[int, int, int, int]] = None, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        if color is not None:
            self.style.text_color = color
        self.font: Optional[pygame.font.Font] = None
        self._cached_surface: Optional[pygame.Surface] = None
        self._cached_text = ""

    def set_text(self, text: str):
        """Update label text"""
        if self.text != text:
            self.text = text
            self._cached_surface = None

    def render(self, screen: pygame.Surface):
        if not self.visible:
            return

        # Initialize font if needed
        if self.font is None:
            self.font = pygame.font.Font(self.style.font_name, self.style.font_size)

        # Render text (with caching)
        if self._cached_surface is None or self._cached_text != self.text:
            self._cached_surface = self.font.render(self.text, True, self.style.text_color[:3])
            self._cached_text = self.text

        # Center text in widget
        text_rect = self._cached_surface.get_rect()
        text_rect.center = (self.x + self.width // 2, self.y + self.height // 2)

        screen.blit(self._cached_surface, text_rect)


class UIButton(UIWidget):
    """Clickable button widget"""

    def __init__(
        self,
        text: str = "Button",
        on_click: Optional[Callable[[], None]] = None,
        color: Optional[Tuple[int, int, int, int]] = None,
        text_color: Optional[Tuple[int, int, int, int]] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.text = text
        if on_click:
            self.on_click = on_click
        if color is not None:
            self.style.background_color = color
        if text_color is not None:
            self.style.text_color = text_color
        self.font: Optional[pygame.font.Font] = None

    def render(self, screen: pygame.Surface):
        if not self.visible:
            return

        rect = self.get_rect()

        # Determine background color
        if not self.enabled:
            bg_color = self.style.disabled_color
        elif self.pressed:
            bg_color = self.style.active_color
        elif self.hovered:
            bg_color = self.style.hover_color
        else:
            bg_color = self.style.background_color

        # Draw background
        pygame.draw.rect(screen, bg_color, rect)

        # Draw border
        pygame.draw.rect(screen, self.style.border_color, rect, self.style.border_width)

        # Draw text
        if self.font is None:
            self.font = pygame.font.Font(self.style.font_name, self.style.font_size)

        text_surface = self.font.render(self.text, True, self.style.text_color[:3])
        text_rect = text_surface.get_rect()
        text_rect.center = rect.center

        screen.blit(text_surface, text_rect)


class UIPanel(UIWidget):
    """Panel widget with background"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def render(self, screen: pygame.Surface):
        if not self.visible:
            return

        rect = self.get_rect()

        # Draw background
        if len(self.style.background_color) == 4:
            # Create surface with alpha for transparency
            surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(surface, self.style.background_color, surface.get_rect())
            screen.blit(surface, (self.x, self.y))
        else:
            pygame.draw.rect(screen, self.style.background_color, rect)

        # Draw border
        pygame.draw.rect(screen, self.style.border_color, rect, self.style.border_width)


class UIContainer(UIWidget):
    """Container that holds other widgets"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.children: List[UIWidget] = []

    def add_child(self, widget: UIWidget):
        """Add a child widget"""
        widget.parent = self
        self.children.append(widget)

    def remove_child(self, widget: UIWidget):
        """Remove a child widget"""
        if widget in self.children:
            widget.parent = None
            self.children.remove(widget)

    def clear_children(self):
        """Remove all children"""
        for child in self.children:
            child.parent = None
        self.children.clear()

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle event, propagate to children"""
        if not self.visible or not self.enabled:
            return False

        # Check children first (reverse order for top-to-bottom)
        for child in reversed(self.children):
            if child.handle_event(event):
                return True

        # Handle self
        return super().handle_event(event)

    def render(self, screen: pygame.Surface):
        if not self.visible:
            return

        # Render self (if it's a panel-like container)
        rect = self.get_rect()
        if len(self.style.background_color) == 4:
            surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(surface, self.style.background_color, surface.get_rect())
            screen.blit(surface, (self.x, self.y))

        # Render children
        for child in self.children:
            child.render(screen)

    def update(self, delta_time: float):
        """Update children"""
        for child in self.children:
            child.update(delta_time)


class UIManager:
    """Manages UI widgets and handles events"""

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.root = UIContainer(x=0, y=0, width=screen_width, height=screen_height)
        self.root.style.background_color = (0, 0, 0, 0)  # Transparent
        self.tooltip_manager = TooltipManager()

    def add_widget(self, widget: UIWidget):
        """Add widget to root"""
        self.root.add_child(widget)

    def remove_widget(self, widget: UIWidget):
        """Remove widget from root"""
        self.root.remove_child(widget)

    def clear(self):
        """Remove all widgets"""
        self.root.clear_children()

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame event.

        Returns:
            True if event was handled by UI
        """
        return self.root.handle_event(event)

    def update(self, delta_time: float):
        """Update all widgets"""
        self.root.update(delta_time)

        # Update tooltips
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.tooltip_manager.update(delta_time, self.root.children, mouse_x, mouse_y)

    def render(self, screen: pygame.Surface):
        """Render all widgets"""
        self.root.render(screen)

        # Render tooltips on top
        self.tooltip_manager.render(screen)

    def apply_anchor(self, widget: UIWidget, anchor: Anchor):
        """Apply anchor positioning to widget"""
        if anchor == Anchor.TOP_LEFT:
            pass  # Already at 0,0 relative
        elif anchor == Anchor.TOP_CENTER:
            widget.x = (self.screen_width - widget.width) // 2
        elif anchor == Anchor.TOP_RIGHT:
            widget.x = self.screen_width - widget.width
        elif anchor == Anchor.CENTER_LEFT:
            widget.y = (self.screen_height - widget.height) // 2
        elif anchor == Anchor.CENTER:
            widget.x = (self.screen_width - widget.width) // 2
            widget.y = (self.screen_height - widget.height) // 2
        elif anchor == Anchor.CENTER_RIGHT:
            widget.x = self.screen_width - widget.width
            widget.y = (self.screen_height - widget.height) // 2
        elif anchor == Anchor.BOTTOM_LEFT:
            widget.y = self.screen_height - widget.height
        elif anchor == Anchor.BOTTOM_CENTER:
            widget.x = (self.screen_width - widget.width) // 2
            widget.y = self.screen_height - widget.height
        elif anchor == Anchor.BOTTOM_RIGHT:
            widget.x = self.screen_width - widget.width
            widget.y = self.screen_height - widget.height


class UIBuilder:
    """Helper for building UI layouts"""

    @staticmethod
    def create_button(
        text: str,
        x: int,
        y: int,
        width: int = 120,
        height: int = 40,
        on_click: Optional[Callable[[], None]] = None,
        tooltip: Optional[str] = None,
    ) -> UIButton:
        """Create a button with standard style"""
        button = UIButton(text=text, x=x, y=y, width=width, height=height)
        if on_click:
            button.on_click = on_click
        if tooltip:
            button.tooltip = tooltip
        return button

    @staticmethod
    def create_label(
        text: str, x: int, y: int, width: int = 200, height: int = 30, tooltip: Optional[str] = None
    ) -> UILabel:
        """Create a label"""
        label = UILabel(text=text, x=x, y=y, width=width, height=height)
        if tooltip:
            label.tooltip = tooltip
        return label

    @staticmethod
    def create_panel(
        x: int, y: int, width: int, height: int, tooltip: Optional[str] = None
    ) -> UIPanel:
        """Create a panel"""
        panel = UIPanel(x=x, y=y, width=width, height=height)
        if tooltip:
            panel.tooltip = tooltip
        return panel

    @staticmethod
    def create_vertical_layout(x: int, y: int, spacing: int = 10) -> "VerticalLayout":
        """Create a vertical layout container"""
        return VerticalLayout(x=x, y=y, spacing=spacing)

    @staticmethod
    def create_horizontal_layout(x: int, y: int, spacing: int = 10) -> "HorizontalLayout":
        """Create a horizontal layout container"""
        return HorizontalLayout(x=x, y=y, spacing=spacing)


class VerticalLayout(UIContainer):
    """Container that arranges children vertically"""

    def __init__(self, spacing: int = 10, **kwargs):
        super().__init__(**kwargs)
        self.spacing = spacing

    def add_child(self, widget: UIWidget):
        """Add child and update layout"""
        super().add_child(widget)
        self.update_layout()

    def update_layout(self):
        """Update positions of all children"""
        current_y = self.y
        max_width = 0

        for child in self.children:
            child.x = self.x
            child.y = current_y
            current_y += child.height + self.spacing
            max_width = max(max_width, child.width)

        # Update container size
        self.width = max_width
        self.height = current_y - self.y - self.spacing if self.children else 0


class HorizontalLayout(UIContainer):
    """Container that arranges children horizontally"""

    def __init__(self, spacing: int = 10, **kwargs):
        super().__init__(**kwargs)
        self.spacing = spacing

    def add_child(self, widget: UIWidget):
        """Add child and update layout"""
        super().add_child(widget)
        self.update_layout()

    def update_layout(self):
        """Update positions of all children"""
        current_x = self.x
        max_height = 0

        for child in self.children:
            child.x = current_x
            child.y = self.y
            current_x += child.width + self.spacing
            max_height = max(max_height, child.height)

        # Update container size
        self.width = current_x - self.x - self.spacing if self.children else 0
        self.height = max_height


class Tooltip:
    """Tooltip widget that displays helpful information"""

    def __init__(self):
        self.text: Optional[str] = None
        self.widget: Optional[UIWidget] = None
        self.hover_time: float = 0.0
        self.visible: bool = False
        self.x: int = 0
        self.y: int = 0
        self.padding: int = 8
        self.font: Optional[pygame.font.Font] = None
        self.bg_color: Tuple[int, int, int, int] = (40, 40, 40, 240)
        self.text_color: Tuple[int, int, int] = (255, 255, 255)
        self.border_color: Tuple[int, int, int] = (180, 180, 180)
        self.max_width: int = 300

    def show(self, widget: UIWidget, mouse_x: int, mouse_y: int):
        """Show tooltip for widget"""
        if widget.tooltip:
            self.text = widget.tooltip
            self.widget = widget
            self.x = mouse_x + 15  # Offset from cursor
            self.y = mouse_y + 15
            self.visible = True
            self.hover_time = 0.0

    def hide(self):
        """Hide tooltip"""
        self.visible = False
        self.text = None
        self.widget = None
        self.hover_time = 0.0

    def update(self, dt: float, mouse_x: int, mouse_y: int):
        """Update tooltip position and visibility"""
        if self.visible and self.widget:
            # Update position to follow mouse
            self.x = mouse_x + 15
            self.y = mouse_y + 15

    def render(self, screen: pygame.Surface):
        """Render tooltip"""
        if not self.visible or not self.text:
            return

        # Initialize font if needed
        if self.font is None:
            self.font = pygame.font.Font(None, 16)

        # Wrap text for multi-line tooltips
        words = self.text.split(" ")
        lines = []
        current_line = []
        current_width = 0

        for word in words:
            word_surface = self.font.render(word + " ", True, self.text_color)
            word_width = word_surface.get_width()

            if current_width + word_width > self.max_width and current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_width = word_width
            else:
                current_line.append(word)
                current_width += word_width

        if current_line:
            lines.append(" ".join(current_line))

        # Render text lines
        text_surfaces = [self.font.render(line, True, self.text_color) for line in lines]

        # Calculate tooltip size
        max_text_width = max(surf.get_width() for surf in text_surfaces) if text_surfaces else 0
        total_height = (
            sum(surf.get_height() for surf in text_surfaces) + (len(text_surfaces) - 1) * 2
        )

        width = max_text_width + self.padding * 2
        height = total_height + self.padding * 2

        # Adjust position if tooltip goes off screen
        screen_width, screen_height = screen.get_size()
        x, y = self.x, self.y

        if x + width > screen_width:
            x = screen_width - width - 5
        if y + height > screen_height:
            y = screen_height - height - 5

        # Create surface with alpha
        tooltip_surface = pygame.Surface((width, height), pygame.SRCALPHA)

        # Draw background
        pygame.draw.rect(tooltip_surface, self.bg_color, tooltip_surface.get_rect())

        # Draw border
        pygame.draw.rect(tooltip_surface, self.border_color, tooltip_surface.get_rect(), 1)

        # Blit text
        current_y = self.padding
        for text_surf in text_surfaces:
            tooltip_surface.blit(text_surf, (self.padding, current_y))
            current_y += text_surf.get_height() + 2

        # Blit tooltip to screen
        screen.blit(tooltip_surface, (x, y))


class LoadingIndicator:
    """Loading indicator widget with spinner and progress"""

    def __init__(self, x: int = 0, y: int = 0):
        self.x = x
        self.y = y
        self.visible: bool = False
        self.text: str = "Loading..."
        self.progress: float = 0.0  # 0.0 to 1.0
        self.show_spinner: bool = True
        self.show_progress_bar: bool = False
        self.spinner_angle: float = 0.0
        self.font: Optional[pygame.font.Font] = None
        self.bg_color: Tuple[int, int, int, int] = (30, 30, 30, 220)
        self.text_color: Tuple[int, int, int] = (255, 255, 255)
        self.spinner_color: Tuple[int, int, int] = (100, 200, 255)
        self.progress_bg_color: Tuple[int, int, int] = (60, 60, 60)
        self.progress_fill_color: Tuple[int, int, int] = (100, 200, 100)
        self.width: int = 300
        self.height: int = 100

    def show(self, text: str = "Loading...", show_progress: bool = False):
        """Show loading indicator"""
        self.visible = True
        self.text = text
        self.show_progress_bar = show_progress
        self.progress = 0.0
        self.spinner_angle = 0.0

    def hide(self):
        """Hide loading indicator"""
        self.visible = False

    def set_progress(self, progress: float):
        """Set progress (0.0 to 1.0)"""
        self.progress = max(0.0, min(1.0, progress))

    def update(self, dt: float):
        """Update loading animation"""
        if self.visible and self.show_spinner:
            self.spinner_angle += dt * 360  # One rotation per second
            if self.spinner_angle >= 360:
                self.spinner_angle -= 360

    def render(self, screen: pygame.Surface):
        """Render loading indicator"""
        if not self.visible:
            return

        # Initialize font if needed
        if self.font is None:
            self.font = pygame.font.Font(None, 20)

        # Center on screen
        screen_width, screen_height = screen.get_size()
        x = (screen_width - self.width) // 2
        y = (screen_height - self.height) // 2

        # Create surface with alpha
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Draw background
        pygame.draw.rect(surface, self.bg_color, surface.get_rect(), border_radius=10)

        # Draw border
        pygame.draw.rect(surface, (100, 100, 100), surface.get_rect(), 2, border_radius=10)

        # Draw text
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect()
        text_rect.centerx = self.width // 2
        text_rect.y = 20
        surface.blit(text_surf, text_rect)

        # Draw spinner
        if self.show_spinner:
            center_x = self.width // 2
            center_y = self.height // 2 + 10
            radius = 15

            # Draw spinning arc
            import math

            num_segments = 20
            for i in range(num_segments):
                angle_start = math.radians(self.spinner_angle + i * (360 / num_segments))
                angle_end = math.radians(self.spinner_angle + (i + 1) * (360 / num_segments))

                # Fade effect
                alpha = int(255 * (i / num_segments))
                color = (*self.spinner_color[:3], alpha)

                start_x = center_x + radius * math.cos(angle_start)
                start_y = center_y + radius * math.sin(angle_start)
                end_x = center_x + radius * math.cos(angle_end)
                end_y = center_y + radius * math.sin(angle_end)

                pygame.draw.line(surface, color, (start_x, start_y), (end_x, end_y), 3)

        # Draw progress bar
        if self.show_progress_bar:
            bar_width = self.width - 40
            bar_height = 20
            bar_x = 20
            bar_y = self.height - bar_height - 15

            # Background
            pygame.draw.rect(
                surface,
                self.progress_bg_color,
                (bar_x, bar_y, bar_width, bar_height),
                border_radius=5,
            )

            # Fill
            fill_width = int(bar_width * self.progress)
            if fill_width > 0:
                pygame.draw.rect(
                    surface,
                    self.progress_fill_color,
                    (bar_x, bar_y, fill_width, bar_height),
                    border_radius=5,
                )

            # Border
            pygame.draw.rect(
                surface, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), 1, border_radius=5
            )

            # Percentage text
            percent_text = f"{int(self.progress * 100)}%"
            percent_surf = self.font.render(percent_text, True, self.text_color)
            percent_rect = percent_surf.get_rect()
            percent_rect.center = (bar_x + bar_width // 2, bar_y + bar_height // 2)
            surface.blit(percent_surf, percent_rect)

        # Blit to screen
        screen.blit(surface, (x, y))


class TooltipManager:
    """Manages tooltip display for all widgets"""

    def __init__(self):
        self.tooltip = Tooltip()
        self.current_widget: Optional[UIWidget] = None
        self.hover_start_time: float = 0.0

    def update(self, dt: float, widgets: List[UIWidget], mouse_x: int, mouse_y: int):
        """Update tooltip state"""
        # Find hovered widget with tooltip
        hovered_widget = None
        for widget in self._flatten_widgets(widgets):
            if widget.visible and widget.tooltip and widget.hovered:
                hovered_widget = widget
                break

        # Handle tooltip showing/hiding
        if hovered_widget:
            if hovered_widget != self.current_widget:
                # New widget hovered
                self.current_widget = hovered_widget
                self.hover_start_time = 0.0
                self.tooltip.hide()
            else:
                # Same widget, accumulate time
                self.hover_start_time += dt

                # Show tooltip after delay
                if (
                    self.hover_start_time >= hovered_widget.tooltip_delay
                    and not self.tooltip.visible
                ):
                    self.tooltip.show(hovered_widget, mouse_x, mouse_y)
                elif self.tooltip.visible:
                    self.tooltip.update(dt, mouse_x, mouse_y)
        else:
            # No hovered widget
            if self.current_widget:
                self.tooltip.hide()
                self.current_widget = None
                self.hover_start_time = 0.0

    def render(self, screen: pygame.Surface):
        """Render active tooltip"""
        self.tooltip.render(screen)

    def _flatten_widgets(self, widgets: List[UIWidget]) -> List[UIWidget]:
        """Flatten widget tree into list"""
        result = []
        for widget in widgets:
            result.append(widget)
            if isinstance(widget, UIContainer):
                result.extend(self._flatten_widgets(widget.children))
        return result


class KeyboardNavigator:
    """Handles keyboard navigation for accessibility"""

    def __init__(self):
        self.focused_widget: Optional[UIWidget] = None
        self.focusable_widgets: List[UIWidget] = []
        self.focus_index: int = -1
        self.enabled: bool = True
        self.highlight_color: Tuple[int, int, int] = (100, 200, 255)
        self.highlight_width: int = 3

    def set_focusable_widgets(self, widgets: List[UIWidget]):
        """
        Set list of widgets that can receive keyboard focus.

        Args:
            widgets: List of focusable widgets
        """
        self.focusable_widgets = [w for w in widgets if w.visible and w.enabled]
        if self.focused_widget not in self.focusable_widgets:
            self.focused_widget = None
            self.focus_index = -1

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle keyboard navigation events.

        Args:
            event: Pygame event

        Returns:
            True if event was handled
        """
        if not self.enabled or not self.focusable_widgets:
            return False

        if event.type == pygame.KEYDOWN:
            # Tab: Move focus forward
            if event.key == pygame.K_TAB:
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    # Shift+Tab: Move focus backward
                    self.focus_previous()
                else:
                    # Tab: Move focus forward
                    self.focus_next()
                return True

            # Enter/Space: Activate focused widget
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.focused_widget and self.focused_widget.on_click:
                    self.focused_widget.on_click()
                    return True

            # Arrow keys: Navigate in 2D
            elif event.key == pygame.K_UP:
                self.focus_up()
                return True
            elif event.key == pygame.K_DOWN:
                self.focus_down()
                return True
            elif event.key == pygame.K_LEFT:
                self.focus_previous()
                return True
            elif event.key == pygame.K_RIGHT:
                self.focus_next()
                return True

        return False

    def focus_next(self):
        """Move focus to next widget"""
        if not self.focusable_widgets:
            return

        self.focus_index = (self.focus_index + 1) % len(self.focusable_widgets)
        self.focused_widget = self.focusable_widgets[self.focus_index]

    def focus_previous(self):
        """Move focus to previous widget"""
        if not self.focusable_widgets:
            return

        self.focus_index = (self.focus_index - 1) % len(self.focusable_widgets)
        self.focused_widget = self.focusable_widgets[self.focus_index]

    def focus_up(self):
        """Move focus to widget above"""
        if not self.focused_widget or not self.focusable_widgets:
            return

        current_rect = self.focused_widget.get_rect()
        candidates = []

        # Find widgets above current
        for widget in self.focusable_widgets:
            if widget == self.focused_widget:
                continue

            rect = widget.get_rect()
            # Widget is above if its bottom is above current top
            if rect.bottom <= current_rect.top:
                # Calculate distance (prefer widgets directly above)
                dx = abs(rect.centerx - current_rect.centerx)
                dy = current_rect.top - rect.bottom
                distance = dx + dy * 2  # Weight vertical distance more
                candidates.append((distance, widget))

        # Focus on closest widget above
        if candidates:
            candidates.sort()
            self.focused_widget = candidates[0][1]
            self.focus_index = self.focusable_widgets.index(self.focused_widget)

    def focus_down(self):
        """Move focus to widget below"""
        if not self.focused_widget or not self.focusable_widgets:
            return

        current_rect = self.focused_widget.get_rect()
        candidates = []

        # Find widgets below current
        for widget in self.focusable_widgets:
            if widget == self.focused_widget:
                continue

            rect = widget.get_rect()
            # Widget is below if its top is below current bottom
            if rect.top >= current_rect.bottom:
                # Calculate distance (prefer widgets directly below)
                dx = abs(rect.centerx - current_rect.centerx)
                dy = rect.top - current_rect.bottom
                distance = dx + dy * 2  # Weight vertical distance more
                candidates.append((distance, widget))

        # Focus on closest widget below
        if candidates:
            candidates.sort()
            self.focused_widget = candidates[0][1]
            self.focus_index = self.focusable_widgets.index(self.focused_widget)

    def render_focus(self, screen: pygame.Surface):
        """
        Render focus indicator around focused widget.

        Args:
            screen: Surface to render to
        """
        if not self.enabled or not self.focused_widget or not self.focused_widget.visible:
            return

        rect = self.focused_widget.get_rect()

        # Draw highlight border
        pygame.draw.rect(screen, self.highlight_color, rect, self.highlight_width)

        # Draw corner indicators for better visibility
        corner_size = 8
        corners = [
            (rect.left, rect.top),  # Top-left
            (rect.right - corner_size, rect.top),  # Top-right
            (rect.left, rect.bottom - corner_size),  # Bottom-left
            (rect.right - corner_size, rect.bottom - corner_size),  # Bottom-right
        ]

        for x, y in corners:
            pygame.draw.rect(
                screen, self.highlight_color, (x, y, corner_size, corner_size), self.highlight_width
            )


class UITextInput(UIWidget):
    """Basic text input field used across legacy UIs."""

    def __init__(self, text: str = "", placeholder: str = "", **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.placeholder = placeholder
        self.font: Optional[pygame.font.Font] = None

    def set_text(self, text: str):
        """Update the input text."""
        self.text = text

    def get_text(self) -> str:
        """Return current text."""
        return self.text

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle typing and focus."""
        if not self.visible or not self.enabled:
            return False

        consumed = super().handle_event(event)
        if consumed:
            return True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                return True
            elif event.unicode and event.key != pygame.K_RETURN:
                self.text += event.unicode
                return True
        return False

    def render(self, screen: pygame.Surface):
        if not self.visible:
            return

        rect = self.get_rect()

        # Draw background
        pygame.draw.rect(screen, self.style.background_color, rect)
        pygame.draw.rect(screen, self.style.border_color, rect, 1)

        # Prepare font
        if self.font is None:
            self.font = pygame.font.Font(self.style.font_name, self.style.font_size)

        # Choose text/placeholder
        display_text = self.text if self.text else self.placeholder
        color = self.style.text_color[:3] if self.text else (150, 150, 150)

        text_surface = self.font.render(display_text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midleft = (self.x + self.style.padding, self.y + self.height // 2)
        screen.blit(text_surface, text_rect)


# Compatibility aliases for legacy imports
Button = UIButton
Label = UILabel
Panel = UIPanel
TextInput = UITextInput
