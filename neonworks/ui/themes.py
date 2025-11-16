"""
UI Theme System

Provides consistent colors, fonts, and spacing across all UI elements.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Tuple


class ThemePreset(Enum):
    """Available theme presets"""

    DARK = "dark"
    LIGHT = "light"
    BLUE = "blue"
    GREEN = "green"
    PURPLE = "purple"
    HIGH_CONTRAST = "high_contrast"


@dataclass
class ColorPalette:
    """Color palette for UI theme"""

    # Primary colors
    primary: Tuple[int, int, int] = (100, 150, 255)
    primary_hover: Tuple[int, int, int] = (120, 170, 255)
    primary_active: Tuple[int, int, int] = (80, 130, 235)

    # Secondary colors
    secondary: Tuple[int, int, int] = (150, 150, 150)
    secondary_hover: Tuple[int, int, int] = (170, 170, 170)
    secondary_active: Tuple[int, int, int] = (130, 130, 130)

    # Background colors
    background: Tuple[int, int, int, int] = (40, 40, 45, 230)
    background_light: Tuple[int, int, int, int] = (50, 50, 55, 230)
    background_dark: Tuple[int, int, int, int] = (30, 30, 35, 230)

    # Surface colors (panels, cards)
    surface: Tuple[int, int, int, int] = (50, 50, 55, 240)
    surface_hover: Tuple[int, int, int, int] = (60, 60, 65, 240)
    surface_active: Tuple[int, int, int, int] = (70, 70, 75, 240)

    # Text colors
    text_primary: Tuple[int, int, int] = (255, 255, 255)
    text_secondary: Tuple[int, int, int] = (200, 200, 200)
    text_disabled: Tuple[int, int, int] = (120, 120, 120)
    text_hint: Tuple[int, int, int] = (150, 150, 150)

    # Border colors
    border: Tuple[int, int, int] = (100, 100, 105)
    border_focus: Tuple[int, int, int] = (100, 150, 255)
    border_error: Tuple[int, int, int] = (255, 80, 80)

    # Status colors
    success: Tuple[int, int, int] = (80, 200, 120)
    warning: Tuple[int, int, int] = (255, 180, 60)
    error: Tuple[int, int, int] = (255, 80, 80)
    info: Tuple[int, int, int] = (100, 180, 255)

    # Special colors
    highlight: Tuple[int, int, int] = (100, 200, 255)
    selection: Tuple[int, int, int, int] = (100, 150, 255, 100)
    overlay: Tuple[int, int, int, int] = (0, 0, 0, 150)


@dataclass
class Spacing:
    """Spacing constants for consistent layout"""

    # Base spacing unit (in pixels)
    unit: int = 8

    # Common spacing values
    xs: int = 4  # 0.5 units
    sm: int = 8  # 1 unit
    md: int = 16  # 2 units
    lg: int = 24  # 3 units
    xl: int = 32  # 4 units
    xxl: int = 48  # 6 units

    # Padding
    padding_xs: int = 4
    padding_sm: int = 8
    padding_md: int = 12
    padding_lg: int = 16
    padding_xl: int = 24

    # Margins
    margin_xs: int = 4
    margin_sm: int = 8
    margin_md: int = 12
    margin_lg: int = 16
    margin_xl: int = 24


@dataclass
class Typography:
    """Typography settings"""

    # Font families
    font_family: str = None  # None uses pygame default
    font_family_mono: str = None  # Monospace font

    # Font sizes
    font_size_xs: int = 12
    font_size_sm: int = 14
    font_size_md: int = 16
    font_size_lg: int = 18
    font_size_xl: int = 20
    font_size_xxl: int = 24

    # Heading sizes
    heading_1: int = 32
    heading_2: int = 28
    heading_3: int = 24
    heading_4: int = 20
    heading_5: int = 18
    heading_6: int = 16

    # Line height multiplier
    line_height: float = 1.4


@dataclass
class BorderRadius:
    """Border radius for rounded corners"""

    none: int = 0
    sm: int = 4
    md: int = 8
    lg: int = 12
    xl: int = 16
    full: int = 9999  # Circular


@dataclass
class Shadows:
    """Shadow effects (currently just stored, not used in pygame)"""

    sm: str = "0 1px 2px rgba(0,0,0,0.05)"
    md: str = "0 4px 6px rgba(0,0,0,0.1)"
    lg: str = "0 10px 15px rgba(0,0,0,0.15)"
    xl: str = "0 20px 25px rgba(0,0,0,0.2)"


class UITheme:
    """Complete UI theme with colors, spacing, and typography"""

    def __init__(
        self,
        name: str = "Default",
        colors: Optional[ColorPalette] = None,
        spacing: Optional[Spacing] = None,
        typography: Optional[Typography] = None,
        border_radius: Optional[BorderRadius] = None,
    ):
        self.name = name
        self.colors = colors or ColorPalette()
        self.spacing = spacing or Spacing()
        self.typography = typography or Typography()
        self.border_radius = border_radius or BorderRadius()
        self.shadows = Shadows()

    def apply_to_style(self, style):
        """
        Apply theme to a UIStyle object.

        Args:
            style: UIStyle object to modify
        """
        # Apply colors
        style.background_color = self.colors.surface
        style.border_color = self.colors.border
        style.text_color = self.colors.text_primary
        style.hover_color = self.colors.surface_hover
        style.active_color = self.colors.surface_active
        style.disabled_color = (*self.colors.background_dark[:3], 150)

        # Apply spacing
        style.padding = self.spacing.padding_md
        style.margin = self.spacing.margin_sm
        style.border_width = 2

        # Apply typography
        style.font_size = self.typography.font_size_md
        style.font_name = self.typography.font_family


class ThemeManager:
    """Manages UI themes"""

    def __init__(self):
        self.themes: Dict[str, UITheme] = {}
        self.current_theme: UITheme = None

        # Register default themes
        self._register_default_themes()

    def _register_default_themes(self):
        """Register built-in themes"""

        # Dark theme (default)
        dark = UITheme(
            name="Dark",
            colors=ColorPalette(
                primary=(100, 150, 255),
                background=(40, 40, 45, 230),
                surface=(50, 50, 55, 240),
                text_primary=(255, 255, 255),
            ),
        )
        self.register_theme("dark", dark)

        # Light theme
        light_colors = ColorPalette(
            primary=(60, 100, 200),
            primary_hover=(80, 120, 220),
            primary_active=(40, 80, 180),
            background=(240, 240, 245, 230),
            background_light=(250, 250, 255, 230),
            background_dark=(230, 230, 235, 230),
            surface=(250, 250, 255, 240),
            surface_hover=(240, 240, 250, 240),
            surface_active=(230, 230, 245, 240),
            text_primary=(30, 30, 30),
            text_secondary=(60, 60, 60),
            text_disabled=(150, 150, 150),
            border=(180, 180, 185),
        )
        light = UITheme(name="Light", colors=light_colors)
        self.register_theme("light", light)

        # Blue theme
        blue_colors = ColorPalette(
            primary=(80, 160, 255),
            primary_hover=(100, 180, 255),
            primary_active=(60, 140, 235),
            background=(30, 40, 60, 230),
            surface=(40, 50, 70, 240),
            surface_hover=(50, 60, 80, 240),
            highlight=(120, 200, 255),
        )
        blue = UITheme(name="Blue", colors=blue_colors)
        self.register_theme("blue", blue)

        # Green theme
        green_colors = ColorPalette(
            primary=(80, 200, 120),
            primary_hover=(100, 220, 140),
            primary_active=(60, 180, 100),
            background=(30, 45, 35, 230),
            surface=(40, 55, 45, 240),
            surface_hover=(50, 65, 55, 240),
            highlight=(100, 220, 140),
        )
        green = UITheme(name="Green", colors=green_colors)
        self.register_theme("green", green)

        # Purple theme
        purple_colors = ColorPalette(
            primary=(150, 100, 255),
            primary_hover=(170, 120, 255),
            primary_active=(130, 80, 235),
            background=(40, 30, 60, 230),
            surface=(50, 40, 70, 240),
            surface_hover=(60, 50, 80, 240),
            highlight=(180, 120, 255),
        )
        purple = UITheme(name="Purple", colors=purple_colors)
        self.register_theme("purple", purple)

        # High contrast theme
        high_contrast_colors = ColorPalette(
            primary=(255, 255, 0),
            primary_hover=(255, 255, 100),
            primary_active=(200, 200, 0),
            background=(0, 0, 0, 255),
            surface=(20, 20, 20, 255),
            surface_hover=(40, 40, 40, 255),
            text_primary=(255, 255, 255),
            border=(255, 255, 255),
            border_focus=(255, 255, 0),
        )
        high_contrast = UITheme(name="High Contrast", colors=high_contrast_colors)
        self.register_theme("high_contrast", high_contrast)

        # Set default theme
        self.current_theme = dark

    def register_theme(self, name: str, theme: UITheme):
        """
        Register a theme.

        Args:
            name: Theme identifier
            theme: UITheme instance
        """
        self.themes[name] = theme

    def set_theme(self, name: str):
        """
        Set the active theme.

        Args:
            name: Theme name to activate
        """
        if name in self.themes:
            self.current_theme = self.themes[name]
            print(f"Theme changed to: {self.current_theme.name}")
        else:
            print(f"Warning: Theme '{name}' not found")

    def get_theme(self, name: str) -> Optional[UITheme]:
        """
        Get theme by name.

        Args:
            name: Theme name

        Returns:
            UITheme or None if not found
        """
        return self.themes.get(name)

    def get_current_theme(self) -> UITheme:
        """Get the currently active theme"""
        return self.current_theme

    def list_themes(self) -> list:
        """Get list of available theme names"""
        return list(self.themes.keys())


# Singleton instance
_theme_manager: Optional[ThemeManager] = None


def get_theme_manager() -> ThemeManager:
    """Get global theme manager instance"""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager


def get_current_theme() -> UITheme:
    """Get the current UI theme"""
    return get_theme_manager().get_current_theme()


def set_theme(name: str):
    """
    Set the active theme.

    Args:
        name: Theme name (dark, light, blue, green, purple, high_contrast)
    """
    get_theme_manager().set_theme(name)
