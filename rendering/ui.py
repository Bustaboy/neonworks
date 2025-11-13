"""
UI System

Immediate mode UI system for game and editor interfaces.
"""

from typing import Tuple, Optional, Callable, List
from dataclasses import dataclass
from enum import Enum, auto
import pygame


class UIState(Enum):
    """UI element states"""
    NORMAL = auto()
    HOVER = auto()
    ACTIVE = auto()
    DISABLED = auto()


@dataclass
class UIStyle:
    """UI styling configuration"""
    # Colors
    primary_color: Tuple[int, int, int] = (0, 120, 255)
    secondary_color: Tuple[int, int, int] = (50, 50, 70)
    background_color: Tuple[int, int, int] = (20, 20, 30)
    text_color: Tuple[int, int, int] = (255, 255, 255)
    border_color: Tuple[int, int, int] = (80, 80, 100)
    hover_color: Tuple[int, int, int] = (0, 150, 255)
    active_color: Tuple[int, int, int] = (0, 100, 200)
    disabled_color: Tuple[int, int, int] = (60, 60, 70)

    # Sizes
    font_size: int = 16
    padding: int = 8
    border_width: int = 2
    button_height: int = 36

    # Effects
    corner_radius: int = 4
    shadow_offset: int = 2


class UI:
    """Immediate mode UI system"""

    def __init__(self, screen: pygame.Surface, style: Optional[UIStyle] = None):
        self.screen = screen
        self.style = style or UIStyle()

        # Fonts
        pygame.font.init()
        self.font = pygame.font.Font(None, self.style.font_size)
        self.title_font = pygame.font.Font(None, self.style.font_size * 2)

        # Input state
        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_down = False
        self.mouse_clicked = False

        # UI state
        self.hot_item = None  # Item under mouse
        self.active_item = None  # Item being interacted with

    def update_input(self, mouse_pos: Tuple[int, int], mouse_down: bool, mouse_clicked: bool):
        """Update input state"""
        self.mouse_x, self.mouse_y = mouse_pos
        self.mouse_down = mouse_down
        self.mouse_clicked = mouse_clicked

    def begin_frame(self):
        """Begin UI frame"""
        self.hot_item = None

    def end_frame(self):
        """End UI frame"""
        if not self.mouse_down:
            self.active_item = None

    def _is_inside(self, x: int, y: int, width: int, height: int) -> bool:
        """Check if mouse is inside rectangle"""
        return (x <= self.mouse_x <= x + width and
                y <= self.mouse_y <= y + height)

    def button(self, x: int, y: int, width: int, height: int,
               text: str, id_: str) -> bool:
        """Render a button and return True if clicked"""
        is_inside = self._is_inside(x, y, width, height)

        if is_inside:
            self.hot_item = id_

        # Determine state
        state = UIState.NORMAL
        if self.active_item == id_:
            state = UIState.ACTIVE
        elif self.hot_item == id_:
            state = UIState.HOVER

        # Get color based on state
        if state == UIState.ACTIVE:
            bg_color = self.style.active_color
        elif state == UIState.HOVER:
            bg_color = self.style.hover_color
        else:
            bg_color = self.style.primary_color

        # Draw button
        pygame.draw.rect(self.screen, bg_color,
                        (x, y, width, height),
                        border_radius=self.style.corner_radius)
        pygame.draw.rect(self.screen, self.style.border_color,
                        (x, y, width, height),
                        self.style.border_width,
                        border_radius=self.style.corner_radius)

        # Draw text
        text_surface = self.font.render(text, True, self.style.text_color)
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(text_surface, text_rect)

        # Handle click
        clicked = False
        if is_inside and self.mouse_down:
            self.active_item = id_
        if is_inside and self.mouse_clicked and self.active_item == id_:
            clicked = True

        return clicked

    def label(self, x: int, y: int, text: str, color: Optional[Tuple[int, int, int]] = None):
        """Render a text label"""
        color = color or self.style.text_color
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))

    def title(self, x: int, y: int, text: str, color: Optional[Tuple[int, int, int]] = None):
        """Render a title"""
        color = color or self.style.text_color
        text_surface = self.title_font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))

    def panel(self, x: int, y: int, width: int, height: int,
              title: Optional[str] = None):
        """Render a panel with optional title"""
        # Draw panel background
        pygame.draw.rect(self.screen, self.style.background_color,
                        (x, y, width, height),
                        border_radius=self.style.corner_radius)
        pygame.draw.rect(self.screen, self.style.border_color,
                        (x, y, width, height),
                        self.style.border_width,
                        border_radius=self.style.corner_radius)

        # Draw title bar if provided
        if title:
            title_height = 30
            pygame.draw.rect(self.screen, self.style.secondary_color,
                           (x, y, width, title_height),
                           border_radius=self.style.corner_radius)
            self.label(x + self.style.padding, y + 8, title)

    def slider(self, x: int, y: int, width: int, height: int,
               value: float, min_val: float, max_val: float,
               id_: str) -> float:
        """Render a slider and return current value"""
        is_inside = self._is_inside(x, y, width, height)

        if is_inside:
            self.hot_item = id_

        # Handle dragging
        if is_inside and self.mouse_down:
            self.active_item = id_

        if self.active_item == id_ and self.mouse_down:
            # Calculate new value from mouse position
            normalized = (self.mouse_x - x) / width
            normalized = max(0.0, min(1.0, normalized))
            value = min_val + normalized * (max_val - min_val)

        # Draw slider track
        pygame.draw.rect(self.screen, self.style.secondary_color,
                        (x, y + height // 3, width, height // 3),
                        border_radius=self.style.corner_radius)

        # Draw slider thumb
        normalized = (value - min_val) / (max_val - min_val)
        thumb_x = x + int(normalized * width)
        thumb_color = self.style.active_color if self.active_item == id_ else self.style.primary_color
        pygame.draw.circle(self.screen, thumb_color,
                          (thumb_x, y + height // 2), height // 2)

        return value

    def checkbox(self, x: int, y: int, size: int, checked: bool,
                 label: str, id_: str) -> bool:
        """Render a checkbox and return new state"""
        is_inside = self._is_inside(x, y, size, size)

        if is_inside:
            self.hot_item = id_

        # Determine color
        color = self.style.hover_color if self.hot_item == id_ else self.style.primary_color

        # Draw checkbox
        pygame.draw.rect(self.screen, self.style.background_color,
                        (x, y, size, size),
                        border_radius=2)
        pygame.draw.rect(self.screen, color,
                        (x, y, size, size),
                        self.style.border_width,
                        border_radius=2)

        # Draw checkmark if checked
        if checked:
            padding = size // 4
            pygame.draw.rect(self.screen, color,
                           (x + padding, y + padding,
                            size - padding * 2, size - padding * 2),
                           border_radius=2)

        # Draw label
        self.label(x + size + 8, y + (size - self.style.font_size) // 2, label)

        # Handle click
        if is_inside and self.mouse_clicked:
            checked = not checked

        return checked

    def progress_bar(self, x: int, y: int, width: int, height: int,
                     progress: float, text: Optional[str] = None):
        """Render a progress bar"""
        # Draw background
        pygame.draw.rect(self.screen, self.style.secondary_color,
                        (x, y, width, height),
                        border_radius=self.style.corner_radius)

        # Draw progress
        progress = max(0.0, min(1.0, progress))
        progress_width = int(width * progress)
        if progress_width > 0:
            pygame.draw.rect(self.screen, self.style.primary_color,
                           (x, y, progress_width, height),
                           border_radius=self.style.corner_radius)

        # Draw border
        pygame.draw.rect(self.screen, self.style.border_color,
                        (x, y, width, height),
                        self.style.border_width,
                        border_radius=self.style.corner_radius)

        # Draw text
        if text:
            text_surface = self.font.render(text, True, self.style.text_color)
            text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
            self.screen.blit(text_surface, text_rect)

    def text_input(self, x: int, y: int, width: int, height: int,
                   text: str, id_: str) -> str:
        """Render a text input field (simplified)"""
        is_inside = self._is_inside(x, y, width, height)

        if is_inside:
            self.hot_item = id_

        # Determine color
        color = self.style.hover_color if self.hot_item == id_ else self.style.secondary_color

        # Draw input box
        pygame.draw.rect(self.screen, color,
                        (x, y, width, height),
                        border_radius=self.style.corner_radius)
        pygame.draw.rect(self.screen, self.style.border_color,
                        (x, y, width, height),
                        self.style.border_width,
                        border_radius=self.style.corner_radius)

        # Draw text
        if text:
            text_surface = self.font.render(text, True, self.style.text_color)
            self.screen.blit(text_surface, (x + self.style.padding, y + height // 2 - 8))

        # Note: Actual text input handling would require keyboard events
        return text

    def tooltip(self, x: int, y: int, text: str):
        """Render a tooltip"""
        text_surface = self.font.render(text, True, self.style.text_color)
        width = text_surface.get_width() + self.style.padding * 2
        height = text_surface.get_height() + self.style.padding * 2

        # Draw background
        pygame.draw.rect(self.screen, self.style.background_color,
                        (x, y, width, height),
                        border_radius=self.style.corner_radius)
        pygame.draw.rect(self.screen, self.style.border_color,
                        (x, y, width, height),
                        1,
                        border_radius=self.style.corner_radius)

        # Draw text
        self.screen.blit(text_surface, (x + self.style.padding, y + self.style.padding))


class HUD:
    """Heads-up display for gameplay"""

    def __init__(self, ui: UI):
        self.ui = ui

    def render_health_bar(self, x: int, y: int, current: float, maximum: float):
        """Render a health bar"""
        width = 200
        height = 24
        progress = current / maximum if maximum > 0 else 0

        # Determine color based on health
        if progress > 0.7:
            color = (0, 255, 0)  # Green
        elif progress > 0.3:
            color = (255, 255, 0)  # Yellow
        else:
            color = (255, 0, 0)  # Red

        # Draw bar background
        pygame.draw.rect(self.ui.screen, (40, 40, 40), (x, y, width, height))

        # Draw health
        progress_width = int(width * progress)
        if progress_width > 0:
            pygame.draw.rect(self.ui.screen, color, (x, y, progress_width, height))

        # Draw border
        pygame.draw.rect(self.ui.screen, (100, 100, 100), (x, y, width, height), 2)

        # Draw text
        text = f"{int(current)}/{int(maximum)}"
        self.ui.label(x + width // 2 - 20, y + 5, text)

    def render_resource(self, x: int, y: int, icon: str, amount: float, capacity: Optional[float] = None):
        """Render a resource display"""
        text = f"{icon} {int(amount)}"
        if capacity:
            text += f"/{int(capacity)}"
        self.ui.label(x, y, text)

    def render_turn_info(self, x: int, y: int, turn: int, action_points: int):
        """Render turn information"""
        self.ui.label(x, y, f"Turn: {turn}")
        self.ui.label(x, y + 20, f"AP: {action_points}")
