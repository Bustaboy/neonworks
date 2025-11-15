"""
Built-in theme presets for map tools.

Provides ready-to-use color themes:
- Default: Original vibrant colors
- Dark: Dark theme with muted colors
- Light: Light theme with darker tool colors
- High Contrast: Maximum contrast for accessibility
"""

from typing import Dict

from .themes import Theme


def get_builtin_themes() -> Dict[str, Theme]:
    """
    Get all built-in theme presets.

    Returns:
        Dict mapping theme_id to Theme object
    """
    return {
        "default": get_default_theme(),
        "dark": get_dark_theme(),
        "light": get_light_theme(),
        "high_contrast": get_high_contrast_theme(),
    }


def get_default_theme() -> Theme:
    """
    Get the default theme (original colors).

    Bright, vibrant colors optimized for dark backgrounds.
    """
    return Theme(
        name="Default",
        description="Original vibrant colors for dark backgrounds",
        # Tool colors (button highlights)
        tool_pencil=(0, 150, 0),
        tool_eraser=(150, 0, 0),
        tool_fill=(0, 150, 150),
        tool_select=(150, 150, 0),
        tool_shape=(200, 100, 200),
        tool_stamp=(100, 200, 100),
        tool_eyedropper=(255, 200, 0),
        # Cursor colors (brighter for visibility)
        cursor_default=(255, 255, 255),
        cursor_pencil=(0, 255, 0),
        cursor_eraser=(255, 0, 0),
        cursor_fill=(0, 255, 255),
        cursor_select_rect=(255, 255, 0),
        cursor_select_wand=(255, 100, 255),
        cursor_shape=(200, 100, 200),
        cursor_stamp=(100, 200, 100),
        cursor_eyedropper=(255, 200, 0),
    )


def get_dark_theme() -> Theme:
    """
    Get the dark theme.

    Muted, darker colors for dark mode interfaces.
    Reduces eye strain in low-light environments.
    """
    return Theme(
        name="Dark",
        description="Muted colors for dark mode, reduces eye strain",
        # Tool colors (darker, muted)
        tool_pencil=(0, 100, 0),
        tool_eraser=(100, 0, 0),
        tool_fill=(0, 100, 100),
        tool_select=(100, 100, 0),
        tool_shape=(150, 50, 150),
        tool_stamp=(50, 150, 50),
        tool_eyedropper=(200, 150, 0),
        # Cursor colors (medium brightness)
        cursor_default=(200, 200, 200),
        cursor_pencil=(0, 200, 0),
        cursor_eraser=(200, 0, 0),
        cursor_fill=(0, 200, 200),
        cursor_select_rect=(200, 200, 0),
        cursor_select_wand=(200, 50, 200),
        cursor_shape=(150, 50, 150),
        cursor_stamp=(50, 150, 50),
        cursor_eyedropper=(200, 150, 0),
    )


def get_light_theme() -> Theme:
    """
    Get the light theme.

    Darker colors optimized for light backgrounds.
    Good for well-lit environments.
    """
    return Theme(
        name="Light",
        description="Darker colors for light backgrounds",
        # Tool colors (darker for visibility on light background)
        tool_pencil=(0, 100, 0),
        tool_eraser=(150, 0, 0),
        tool_fill=(0, 100, 100),
        tool_select=(100, 100, 0),
        tool_shape=(150, 50, 150),
        tool_stamp=(50, 150, 50),
        tool_eyedropper=(200, 120, 0),
        # Cursor colors (dark for light background)
        cursor_default=(50, 50, 50),
        cursor_pencil=(0, 150, 0),
        cursor_eraser=(200, 0, 0),
        cursor_fill=(0, 150, 150),
        cursor_select_rect=(150, 150, 0),
        cursor_select_wand=(150, 50, 150),
        cursor_shape=(120, 40, 120),
        cursor_stamp=(40, 120, 40),
        cursor_eyedropper=(180, 100, 0),
    )


def get_high_contrast_theme() -> Theme:
    """
    Get the high contrast theme.

    Maximum contrast for accessibility.
    Pure colors for users with visual impairments.
    """
    return Theme(
        name="High Contrast",
        description="Maximum contrast for accessibility",
        # Tool colors (pure saturated colors)
        tool_pencil=(0, 255, 0),
        tool_eraser=(255, 0, 0),
        tool_fill=(0, 255, 255),
        tool_select=(255, 255, 0),
        tool_shape=(255, 0, 255),
        tool_stamp=(0, 255, 0),
        tool_eyedropper=(255, 150, 0),
        # Cursor colors (pure bright colors)
        cursor_default=(255, 255, 255),
        cursor_pencil=(0, 255, 0),
        cursor_eraser=(255, 0, 0),
        cursor_fill=(0, 255, 255),
        cursor_select_rect=(255, 255, 0),
        cursor_select_wand=(255, 0, 255),
        cursor_shape=(255, 0, 255),
        cursor_stamp=(0, 255, 0),
        cursor_eyedropper=(255, 150, 0),
    )


def create_custom_theme(
    name: str,
    description: str,
    tool_colors: Dict[str, tuple],
    cursor_colors: Dict[str, tuple],
) -> Theme:
    """
    Create a custom theme from color dictionaries.

    Args:
        name: Theme name
        description: Theme description
        tool_colors: Dict mapping tool names to RGB tuples
        cursor_colors: Dict mapping cursor types to RGB tuples

    Returns:
        Custom Theme object

    Example:
        >>> theme = create_custom_theme(
        ...     "My Theme",
        ...     "Custom colors",
        ...     tool_colors={
        ...         "pencil": (50, 150, 50),
        ...         "eraser": (150, 50, 50),
        ...         # ... other tools
        ...     },
        ...     cursor_colors={
        ...         "default": (255, 255, 255),
        ...         "pencil": (100, 200, 100),
        ...         # ... other cursors
        ...     }
        ... )
    """
    # Start with default theme values
    default = get_default_theme()

    return Theme(
        name=name,
        description=description,
        # Tool colors (use provided or fall back to default)
        tool_pencil=tool_colors.get("pencil", default.tool_pencil),
        tool_eraser=tool_colors.get("eraser", default.tool_eraser),
        tool_fill=tool_colors.get("fill", default.tool_fill),
        tool_select=tool_colors.get("select", default.tool_select),
        tool_shape=tool_colors.get("shape", default.tool_shape),
        tool_stamp=tool_colors.get("stamp", default.tool_stamp),
        tool_eyedropper=tool_colors.get("eyedropper", default.tool_eyedropper),
        # Cursor colors (use provided or fall back to default)
        cursor_default=cursor_colors.get("default", default.cursor_default),
        cursor_pencil=cursor_colors.get("pencil", default.cursor_pencil),
        cursor_eraser=cursor_colors.get("eraser", default.cursor_eraser),
        cursor_fill=cursor_colors.get("fill", default.cursor_fill),
        cursor_select_rect=cursor_colors.get("select_rect", default.cursor_select_rect),
        cursor_select_wand=cursor_colors.get("select_wand", default.cursor_select_wand),
        cursor_shape=cursor_colors.get("shape", default.cursor_shape),
        cursor_stamp=cursor_colors.get("stamp", default.cursor_stamp),
        cursor_eyedropper=cursor_colors.get("eyedropper", default.cursor_eyedropper),
    )
