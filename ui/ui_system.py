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

    def __init__(self, text: str = "", **kwargs):
        super().__init__(**kwargs)
        self.text = text
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
            self._cached_surface = self.font.render(
                self.text, True, self.style.text_color[:3]
            )
            self._cached_text = self.text

        # Center text in widget
        text_rect = self._cached_surface.get_rect()
        text_rect.center = (self.x + self.width // 2, self.y + self.height // 2)

        screen.blit(self._cached_surface, text_rect)


class UIButton(UIWidget):
    """Clickable button widget"""

    def __init__(self, text: str = "Button", **kwargs):
        super().__init__(**kwargs)
        self.text = text
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

    def render(self, screen: pygame.Surface):
        """Render all widgets"""
        self.root.render(screen)

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
    ) -> UIButton:
        """Create a button with standard style"""
        button = UIButton(text=text, x=x, y=y, width=width, height=height)
        if on_click:
            button.on_click = on_click
        return button

    @staticmethod
    def create_label(
        text: str, x: int, y: int, width: int = 200, height: int = 30
    ) -> UILabel:
        """Create a label"""
        return UILabel(text=text, x=x, y=y, width=width, height=height)

    @staticmethod
    def create_panel(x: int, y: int, width: int, height: int) -> UIPanel:
        """Create a panel"""
        return UIPanel(x=x, y=y, width=width, height=height)

    @staticmethod
    def create_vertical_layout(x: int, y: int, spacing: int = 10) -> "VerticalLayout":
        """Create a vertical layout container"""
        return VerticalLayout(x=x, y=y, spacing=spacing)

    @staticmethod
    def create_horizontal_layout(
        x: int, y: int, spacing: int = 10
    ) -> "HorizontalLayout":
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
