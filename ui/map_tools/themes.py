"""
Theme system for map tools.

Provides customizable color themes (light, dark, high contrast, custom).
Themes can be switched at runtime and saved to user preferences.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple


@dataclass
class Theme:
    """
    Defines a complete color theme for map tools.

    All colors are RGB tuples (r, g, b) with values 0-255.
    """

    name: str
    description: str

    # Tool button colors (for tool panel highlighting)
    tool_pencil: Tuple[int, int, int] = (0, 150, 0)
    tool_eraser: Tuple[int, int, int] = (150, 0, 0)
    tool_fill: Tuple[int, int, int] = (0, 150, 150)
    tool_select: Tuple[int, int, int] = (150, 150, 0)
    tool_shape: Tuple[int, int, int] = (200, 100, 200)
    tool_stamp: Tuple[int, int, int] = (100, 200, 100)
    tool_eyedropper: Tuple[int, int, int] = (255, 200, 0)

    # Cursor colors (for rendering tool cursors)
    cursor_default: Tuple[int, int, int] = (255, 255, 255)
    cursor_pencil: Tuple[int, int, int] = (0, 255, 0)
    cursor_eraser: Tuple[int, int, int] = (255, 0, 0)
    cursor_fill: Tuple[int, int, int] = (0, 255, 255)
    cursor_select_rect: Tuple[int, int, int] = (255, 255, 0)
    cursor_select_wand: Tuple[int, int, int] = (255, 100, 255)
    cursor_shape: Tuple[int, int, int] = (200, 100, 200)
    cursor_stamp: Tuple[int, int, int] = (100, 200, 100)
    cursor_eyedropper: Tuple[int, int, int] = (255, 200, 0)

    def to_dict(self) -> Dict:
        """Export theme to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "tool_pencil": list(self.tool_pencil),
            "tool_eraser": list(self.tool_eraser),
            "tool_fill": list(self.tool_fill),
            "tool_select": list(self.tool_select),
            "tool_shape": list(self.tool_shape),
            "tool_stamp": list(self.tool_stamp),
            "tool_eyedropper": list(self.tool_eyedropper),
            "cursor_default": list(self.cursor_default),
            "cursor_pencil": list(self.cursor_pencil),
            "cursor_eraser": list(self.cursor_eraser),
            "cursor_fill": list(self.cursor_fill),
            "cursor_select_rect": list(self.cursor_select_rect),
            "cursor_select_wand": list(self.cursor_select_wand),
            "cursor_shape": list(self.cursor_shape),
            "cursor_stamp": list(self.cursor_stamp),
            "cursor_eyedropper": list(self.cursor_eyedropper),
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Theme":
        """Create theme from dictionary (JSON deserialization)."""
        return cls(
            name=data["name"],
            description=data["description"],
            tool_pencil=tuple(data["tool_pencil"]),
            tool_eraser=tuple(data["tool_eraser"]),
            tool_fill=tuple(data["tool_fill"]),
            tool_select=tuple(data["tool_select"]),
            tool_shape=tuple(data["tool_shape"]),
            tool_stamp=tuple(data["tool_stamp"]),
            tool_eyedropper=tuple(data["tool_eyedropper"]),
            cursor_default=tuple(data["cursor_default"]),
            cursor_pencil=tuple(data["cursor_pencil"]),
            cursor_eraser=tuple(data["cursor_eraser"]),
            cursor_fill=tuple(data["cursor_fill"]),
            cursor_select_rect=tuple(data["cursor_select_rect"]),
            cursor_select_wand=tuple(data["cursor_select_wand"]),
            cursor_shape=tuple(data["cursor_shape"]),
            cursor_stamp=tuple(data["cursor_stamp"]),
            cursor_eyedropper=tuple(data["cursor_eyedropper"]),
        )


class ThemeManager:
    """
    Manages themes and theme switching.

    Provides built-in themes and supports custom user themes.
    """

    def __init__(self):
        """Initialize theme manager with built-in themes."""
        self.themes: Dict[str, Theme] = {}
        self.current_theme: Optional[Theme] = None
        self._load_builtin_themes()

    def _load_builtin_themes(self):
        """Load built-in theme presets."""
        from .theme_presets import get_builtin_themes

        builtin = get_builtin_themes()
        for theme_id, theme in builtin.items():
            self.themes[theme_id] = theme

        # Set default theme
        if "default" in self.themes:
            self.current_theme = self.themes["default"]

    def add_theme(self, theme_id: str, theme: Theme):
        """
        Add a custom theme.

        Args:
            theme_id: Unique identifier for the theme
            theme: Theme object
        """
        self.themes[theme_id] = theme

    def get_theme(self, theme_id: str) -> Optional[Theme]:
        """
        Get theme by ID.

        Args:
            theme_id: Theme identifier

        Returns:
            Theme object or None if not found
        """
        return self.themes.get(theme_id)

    def list_themes(self) -> Dict[str, str]:
        """
        List all available themes.

        Returns:
            Dict mapping theme_id to theme name
        """
        return {theme_id: theme.name for theme_id, theme in self.themes.items()}

    def set_theme(self, theme_id: str) -> bool:
        """
        Set the active theme.

        Args:
            theme_id: Theme identifier

        Returns:
            True if theme was set, False if theme not found
        """
        theme = self.themes.get(theme_id)
        if theme:
            self.current_theme = theme
            self._apply_theme(theme)
            print(f"✓ Applied theme: {theme.name}")
            return True
        return False

    def _apply_theme(self, theme: Theme):
        """
        Apply theme to settings module.

        Updates ToolColors class attributes with theme colors.

        Args:
            theme: Theme to apply
        """
        from . import settings

        # Update tool colors
        settings.ToolColors.PENCIL = theme.tool_pencil
        settings.ToolColors.ERASER = theme.tool_eraser
        settings.ToolColors.FILL = theme.tool_fill
        settings.ToolColors.SELECT = theme.tool_select
        settings.ToolColors.SHAPE = theme.tool_shape
        settings.ToolColors.STAMP = theme.tool_stamp
        settings.ToolColors.EYEDROPPER = theme.tool_eyedropper

        # Update cursor colors
        settings.ToolColors.CURSOR_DEFAULT = theme.cursor_default
        settings.ToolColors.CURSOR_PENCIL = theme.cursor_pencil
        settings.ToolColors.CURSOR_ERASER = theme.cursor_eraser
        settings.ToolColors.CURSOR_FILL = theme.cursor_fill
        settings.ToolColors.CURSOR_SELECT_RECT = theme.cursor_select_rect
        settings.ToolColors.CURSOR_SELECT_WAND = theme.cursor_select_wand
        settings.ToolColors.CURSOR_SHAPE = theme.cursor_shape
        settings.ToolColors.CURSOR_STAMP = theme.cursor_stamp
        settings.ToolColors.CURSOR_EYEDROPPER = theme.cursor_eyedropper

    def get_current_theme(self) -> Optional[Theme]:
        """
        Get the currently active theme.

        Returns:
            Current Theme object or None
        """
        return self.current_theme

    def create_custom_theme_from_current(self, name: str, description: str) -> Theme:
        """
        Create a custom theme based on current settings.

        Args:
            name: Name for the custom theme
            description: Theme description

        Returns:
            New Theme object with current settings
        """
        from . import settings

        return Theme(
            name=name,
            description=description,
            tool_pencil=settings.ToolColors.PENCIL,
            tool_eraser=settings.ToolColors.ERASER,
            tool_fill=settings.ToolColors.FILL,
            tool_select=settings.ToolColors.SELECT,
            tool_shape=settings.ToolColors.SHAPE,
            tool_stamp=settings.ToolColors.STAMP,
            tool_eyedropper=settings.ToolColors.EYEDROPPER,
            cursor_default=settings.ToolColors.CURSOR_DEFAULT,
            cursor_pencil=settings.ToolColors.CURSOR_PENCIL,
            cursor_eraser=settings.ToolColors.CURSOR_ERASER,
            cursor_fill=settings.ToolColors.CURSOR_FILL,
            cursor_select_rect=settings.ToolColors.CURSOR_SELECT_RECT,
            cursor_select_wand=settings.ToolColors.CURSOR_SELECT_WAND,
            cursor_shape=settings.ToolColors.CURSOR_SHAPE,
            cursor_stamp=settings.ToolColors.CURSOR_STAMP,
            cursor_eyedropper=settings.ToolColors.CURSOR_EYEDROPPER,
        )


# Global theme manager instance
_theme_manager: Optional[ThemeManager] = None


def get_theme_manager() -> ThemeManager:
    """
    Get the global theme manager instance (singleton).

    Returns:
        ThemeManager instance
    """
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager
