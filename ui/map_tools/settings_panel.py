"""
Settings panel UI for map tools customization.

Provides visual interface for:
- Theme selection
- Color customization
- Limits and rendering settings adjustment
- Preferences save/load
"""

from typing import Optional

import pygame

from . import settings
from .themes import get_theme_manager


class SettingsPanel:
    """
    Visual settings panel for map tools customization.

    Allows users to switch themes, customize colors and limits,
    and save/load preferences.
    """

    def __init__(self, x: int = 100, y: int = 100, width: int = 600, height: int = 500):
        """
        Initialize settings panel.

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
        self.visible = False

        # Theme manager
        self.theme_manager = get_theme_manager()

        # UI state
        self.selected_theme_id = "default"
        self.show_advanced = False  # Show color pickers
        self.modified = False  # Track if settings were modified

        # Fonts
        self.title_font = pygame.font.Font(None, 28)
        self.label_font = pygame.font.Font(None, 20)
        self.small_font = pygame.font.Font(None, 16)

        # Colors
        self.bg_color = (40, 40, 40)
        self.panel_color = (30, 30, 30)
        self.text_color = (220, 220, 220)
        self.button_color = (60, 60, 60)
        self.button_hover_color = (80, 80, 80)
        self.button_active_color = (100, 100, 100)

        # Button rects (will be set in _layout)
        self.close_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.apply_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.reset_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.save_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.load_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.advanced_btn_rect = pygame.Rect(0, 0, 0, 0)

        # Theme dropdown
        self.theme_dropdown_rect = pygame.Rect(0, 0, 0, 0)
        self.theme_dropdown_open = False

        # Sliders (for limits and rendering settings)
        self.sliders = {}
        self._init_sliders()

        # Layout UI elements
        self._layout()

    def _init_sliders(self):
        """Initialize sliders for numeric settings."""
        self.sliders = {
            "max_fill_cells": {
                "label": "Max Fill Cells",
                "value": settings.ToolLimits.MAX_FILL_CELLS,
                "min": 100,
                "max": 50000,
                "rect": pygame.Rect(0, 0, 0, 0),
            },
            "max_undo_history": {
                "label": "Max Undo History",
                "value": settings.ToolLimits.MAX_UNDO_HISTORY,
                "min": 10,
                "max": 500,
                "rect": pygame.Rect(0, 0, 0, 0),
            },
            "cursor_width": {
                "label": "Cursor Width",
                "value": settings.RenderSettings.CURSOR_OUTLINE_WIDTH,
                "min": 1,
                "max": 5,
                "rect": pygame.Rect(0, 0, 0, 0),
            },
            "selection_alpha": {
                "label": "Selection Alpha",
                "value": settings.RenderSettings.SELECTION_OVERLAY_ALPHA,
                "min": 10,
                "max": 200,
                "rect": pygame.Rect(0, 0, 0, 0),
            },
        }

    def _layout(self):
        """Calculate positions of UI elements."""
        # Buttons at bottom
        btn_width = 100
        btn_height = 30
        btn_spacing = 10
        btn_y = self.y + self.height - btn_height - 20

        self.close_btn_rect = pygame.Rect(
            self.x + self.width - btn_width - 20, btn_y, btn_width, btn_height
        )
        self.apply_btn_rect = pygame.Rect(
            self.close_btn_rect.x - btn_width - btn_spacing,
            btn_y,
            btn_width,
            btn_height,
        )
        self.reset_btn_rect = pygame.Rect(
            self.apply_btn_rect.x - btn_width - btn_spacing,
            btn_y,
            btn_width,
            btn_height,
        )

        # Save/Load buttons at top right
        self.save_btn_rect = pygame.Rect(
            self.x + self.width - btn_width - 20, self.y + 50, btn_width, btn_height
        )
        self.load_btn_rect = pygame.Rect(
            self.save_btn_rect.x - btn_width - btn_spacing,
            self.y + 50,
            btn_width,
            btn_height,
        )

        # Advanced toggle
        self.advanced_btn_rect = pygame.Rect(self.x + 20, self.y + 90, 150, btn_height)

        # Theme dropdown
        self.theme_dropdown_rect = pygame.Rect(self.x + 20, self.y + 50, 200, btn_height)

        # Sliders layout (below theme dropdown)
        slider_y = self.y + 140
        slider_width = 300
        slider_height = 20
        slider_spacing = 60

        for i, slider_id in enumerate(self.sliders.keys()):
            self.sliders[slider_id]["rect"] = pygame.Rect(
                self.x + 20, slider_y + i * slider_spacing, slider_width, slider_height
            )

    def toggle(self):
        """Toggle panel visibility."""
        self.visible = not self.visible

    def show(self):
        """Show the panel."""
        self.visible = True

    def hide(self):
        """Hide the panel."""
        self.visible = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle input events.

        Args:
            event: Pygame event

        Returns:
            True if event was handled
        """
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos

            # Close button
            if self.close_btn_rect.collidepoint(mouse_pos):
                self.hide()
                return True

            # Apply button
            if self.apply_btn_rect.collidepoint(mouse_pos):
                self._apply_settings()
                return True

            # Reset button
            if self.reset_btn_rect.collidepoint(mouse_pos):
                self._reset_settings()
                return True

            # Save button
            if self.save_btn_rect.collidepoint(mouse_pos):
                self._save_preferences()
                return True

            # Load button
            if self.load_btn_rect.collidepoint(mouse_pos):
                self._load_preferences()
                return True

            # Advanced toggle
            if self.advanced_btn_rect.collidepoint(mouse_pos):
                self.show_advanced = not self.show_advanced
                return True

            # Theme dropdown
            if self.theme_dropdown_rect.collidepoint(mouse_pos):
                self.theme_dropdown_open = not self.theme_dropdown_open
                return True

            # Theme selection
            if self.theme_dropdown_open:
                themes = list(self.theme_manager.list_themes().keys())
                dropdown_y = self.theme_dropdown_rect.y + self.theme_dropdown_rect.height
                for i, theme_id in enumerate(themes):
                    item_rect = pygame.Rect(
                        self.theme_dropdown_rect.x,
                        dropdown_y + i * 30,
                        self.theme_dropdown_rect.width,
                        30,
                    )
                    if item_rect.collidepoint(mouse_pos):
                        self.selected_theme_id = theme_id
                        self.theme_manager.set_theme(theme_id)
                        self.theme_dropdown_open = False
                        self.modified = True
                        return True

            # Sliders
            for slider_id, slider_data in self.sliders.items():
                rect = slider_data["rect"]
                if rect.collidepoint(mouse_pos):
                    # Calculate value from click position
                    relative_x = mouse_pos[0] - rect.x
                    ratio = max(0, min(1, relative_x / rect.width))
                    min_val = slider_data["min"]
                    max_val = slider_data["max"]
                    new_value = int(min_val + ratio * (max_val - min_val))
                    slider_data["value"] = new_value
                    self.modified = True
                    return True

        return False

    def _apply_settings(self):
        """Apply current settings to ToolLimits and RenderSettings."""
        settings.ToolLimits.MAX_FILL_CELLS = self.sliders["max_fill_cells"]["value"]
        settings.ToolLimits.MAX_UNDO_HISTORY = self.sliders["max_undo_history"]["value"]
        settings.RenderSettings.CURSOR_OUTLINE_WIDTH = self.sliders["cursor_width"]["value"]
        settings.RenderSettings.SELECTION_OVERLAY_ALPHA = self.sliders["selection_alpha"]["value"]

        print("✓ Settings applied!")
        self.modified = False

    def _reset_settings(self):
        """Reset settings to defaults."""
        self.theme_manager.set_theme("default")
        self.selected_theme_id = "default"
        self._init_sliders()
        self._apply_settings()
        print("✓ Settings reset to defaults!")

    def _save_preferences(self):
        """Save current settings to preferences file."""
        from .preferences import save_preferences

        prefs = {
            "theme": self.selected_theme_id,
            "max_fill_cells": self.sliders["max_fill_cells"]["value"],
            "max_undo_history": self.sliders["max_undo_history"]["value"],
            "cursor_width": self.sliders["cursor_width"]["value"],
            "selection_alpha": self.sliders["selection_alpha"]["value"],
        }

        if save_preferences(prefs):
            print("✓ Preferences saved!")
        else:
            print("✗ Failed to save preferences")

    def _load_preferences(self):
        """Load settings from preferences file."""
        from .preferences import load_preferences

        prefs = load_preferences()
        if prefs:
            # Apply theme
            theme_id = prefs.get("theme", "default")
            if theme_id in self.theme_manager.themes:
                self.selected_theme_id = theme_id
                self.theme_manager.set_theme(theme_id)

            # Apply slider values
            if "max_fill_cells" in prefs:
                self.sliders["max_fill_cells"]["value"] = prefs["max_fill_cells"]
            if "max_undo_history" in prefs:
                self.sliders["max_undo_history"]["value"] = prefs["max_undo_history"]
            if "cursor_width" in prefs:
                self.sliders["cursor_width"]["value"] = prefs["cursor_width"]
            if "selection_alpha" in prefs:
                self.sliders["selection_alpha"]["value"] = prefs["selection_alpha"]

            self._apply_settings()
            print("✓ Preferences loaded!")
        else:
            print("✗ No preferences file found")

    def render(self, screen: pygame.Surface):
        """
        Render the settings panel.

        Args:
            screen: Surface to render to
        """
        if not self.visible:
            return

        # Draw semi-transparent backdrop
        backdrop = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        backdrop.fill((0, 0, 0, 150))
        screen.blit(backdrop, (0, 0))

        # Draw panel background
        pygame.draw.rect(screen, self.bg_color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, (80, 80, 80), (self.x, self.y, self.width, self.height), 2)

        # Title
        title_text = self.title_font.render("Map Tools Settings", True, self.text_color)
        screen.blit(title_text, (self.x + 20, self.y + 10))

        # Theme selector label
        theme_label = self.label_font.render("Theme:", True, self.text_color)
        screen.blit(theme_label, (self.x + 20, self.y + 25))

        # Theme dropdown
        self._render_button(screen, self.theme_dropdown_rect, self.selected_theme_id.title())

        # Theme dropdown menu (if open)
        if self.theme_dropdown_open:
            themes = list(self.theme_manager.list_themes().keys())
            dropdown_y = self.theme_dropdown_rect.y + self.theme_dropdown_rect.height
            for i, theme_id in enumerate(themes):
                item_rect = pygame.Rect(
                    self.theme_dropdown_rect.x,
                    dropdown_y + i * 30,
                    self.theme_dropdown_rect.width,
                    30,
                )
                pygame.draw.rect(screen, self.button_color, item_rect)
                pygame.draw.rect(screen, (100, 100, 100), item_rect, 1)
                text = self.small_font.render(theme_id.title(), True, self.text_color)
                screen.blit(text, (item_rect.x + 10, item_rect.y + 8))

        # Save/Load buttons
        self._render_button(screen, self.save_btn_rect, "Save")
        self._render_button(screen, self.load_btn_rect, "Load")

        # Advanced toggle
        adv_text = "Hide Advanced" if self.show_advanced else "Show Advanced"
        self._render_button(screen, self.advanced_btn_rect, adv_text)

        # Sliders
        for slider_id, slider_data in self.sliders.items():
            self._render_slider(screen, slider_data)

        # Bottom buttons
        self._render_button(screen, self.reset_btn_rect, "Reset")
        self._render_button(screen, self.apply_btn_rect, "Apply")
        self._render_button(screen, self.close_btn_rect, "Close")

        # Modified indicator
        if self.modified:
            mod_text = self.small_font.render("* Unsaved changes", True, (255, 200, 0))
            screen.blit(mod_text, (self.x + 20, self.reset_btn_rect.y - 30))

    def _render_button(self, screen: pygame.Surface, rect: pygame.Rect, text: str):
        """Render a button."""
        mouse_pos = pygame.mouse.get_pos()
        is_hover = rect.collidepoint(mouse_pos)

        color = self.button_hover_color if is_hover else self.button_color
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, (100, 100, 100), rect, 1)

        text_surface = self.small_font.render(text, True, self.text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)

    def _render_slider(self, screen: pygame.Surface, slider_data: dict):
        """Render a slider with label and value."""
        rect = slider_data["rect"]
        label = slider_data["label"]
        value = slider_data["value"]
        min_val = slider_data["min"]
        max_val = slider_data["max"]

        # Label
        label_text = self.label_font.render(f"{label}:", True, self.text_color)
        screen.blit(label_text, (rect.x, rect.y - 25))

        # Value
        value_text = self.small_font.render(str(value), True, self.text_color)
        screen.blit(value_text, (rect.x + rect.width + 10, rect.y))

        # Slider track
        pygame.draw.rect(screen, (60, 60, 60), rect)
        pygame.draw.rect(screen, (100, 100, 100), rect, 1)

        # Slider fill
        ratio = (value - min_val) / (max_val - min_val)
        fill_width = int(rect.width * ratio)
        fill_rect = pygame.Rect(rect.x, rect.y, fill_width, rect.height)
        pygame.draw.rect(screen, (80, 150, 80), fill_rect)

        # Slider handle
        handle_x = rect.x + fill_width
        handle_rect = pygame.Rect(handle_x - 5, rect.y - 3, 10, rect.height + 6)
        pygame.draw.rect(screen, (150, 150, 150), handle_rect)
        pygame.draw.rect(screen, (200, 200, 200), handle_rect, 1)
