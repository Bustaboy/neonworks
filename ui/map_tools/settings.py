"""
Map Tools Settings

Central configuration file for all map editing tool constants.
This file contains all hard-coded values extracted from individual tools
for easier customization and maintenance.
"""

from typing import Dict, Tuple


# =============================================================================
# TOOL COLORS
# =============================================================================


class ToolColors:
    """RGB color definitions for tools and UI elements."""

    # Tool button colors (used in tool selection UI)
    PENCIL = (0, 150, 0)
    ERASER = (150, 0, 0)
    FILL = (0, 150, 150)
    SELECT = (150, 150, 0)
    SHAPE = (200, 100, 200)
    STAMP = (100, 200, 100)
    EYEDROPPER = (255, 200, 0)

    # Cursor colors (used for rendering tool cursors)
    CURSOR_PENCIL = (0, 255, 0)
    CURSOR_ERASER = (255, 0, 0)
    CURSOR_FILL = (0, 255, 255)
    CURSOR_SELECT_RECT = (255, 255, 0)
    CURSOR_SELECT_WAND = (255, 100, 255)
    CURSOR_SHAPE = (200, 100, 200)
    CURSOR_STAMP = (100, 200, 100)
    CURSOR_EYEDROPPER = (255, 200, 0)
    CURSOR_DEFAULT = (255, 255, 255)


# =============================================================================
# RENDERING SETTINGS
# =============================================================================


class RenderSettings:
    """Settings for rendering cursors, previews, and UI elements."""

    # Line widths
    CURSOR_OUTLINE_WIDTH = 2
    CURSOR_HIGHLIGHT_WIDTH = 3
    SELECTION_BOX_WIDTH = 2

    # Alpha values (0-255)
    SELECTION_OVERLAY_ALPHA = 50
    SHAPE_PREVIEW_ALPHA = 100
    STAMP_PREVIEW_ALPHA = 100

    # Cursor crosshair size
    CROSSHAIR_SIZE = 5
    CROSSHAIR_WIDTH = 2

    # Eyedropper icon size
    EYEDROPPER_CIRCLE_RADIUS = 5
    EYEDROPPER_LINE_LENGTH = 6


# =============================================================================
# TOOL LIMITS & THRESHOLDS
# =============================================================================


class ToolLimits:
    """Limits and thresholds for tool operations."""

    # Fill tool
    MAX_FILL_CELLS = 10000  # Maximum tiles to fill (safety limit)

    # Undo/redo
    MAX_UNDO_HISTORY = 100  # Maximum number of actions to keep in undo stack

    # Stamp tool
    MAX_STAMPS = 50  # Maximum number of custom stamps
    MIN_STAMP_SIZE = 1  # Minimum stamp size (tiles)
    MAX_STAMP_SIZE = 50  # Maximum stamp size (tiles)

    # Shape tool
    MIN_SHAPE_SIZE = 1  # Minimum shape size (tiles)
    MAX_SHAPE_SIZE = 1000  # Maximum shape size (tiles)


# =============================================================================
# DEFAULT STAMPS
# =============================================================================


class DefaultStamps:
    """Pre-defined stamp patterns."""

    # 2x2 Square
    SQUARE_2X2 = {
        "name": "2x2 Square",
        "width": 2,
        "height": 2,
        "tiles": [(0, 0), (1, 0), (0, 1), (1, 1)],
    }

    # 3x3 Square
    SQUARE_3X3 = {
        "name": "3x3 Square",
        "width": 3,
        "height": 3,
        "tiles": [
            (0, 0),
            (1, 0),
            (2, 0),
            (0, 1),
            (1, 1),
            (2, 1),
            (0, 2),
            (1, 2),
            (2, 2),
        ],
    }

    # Plus (+) pattern
    PLUS = {
        "name": "Plus",
        "width": 3,
        "height": 3,
        "tiles": [
            (1, 0),  # Top
            (0, 1),
            (1, 1),
            (2, 1),  # Middle row
            (1, 2),  # Bottom
        ],
    }

    # Diamond pattern
    DIAMOND = {
        "name": "Diamond",
        "width": 5,
        "height": 5,
        "tiles": [
            (2, 0),  # Top
            (1, 1),
            (2, 1),
            (3, 1),  # Row 2
            (0, 2),
            (1, 2),
            (2, 2),
            (3, 2),
            (4, 2),  # Middle row
            (1, 3),
            (2, 3),
            (3, 3),  # Row 4
            (2, 4),  # Bottom
        ],
    }


# =============================================================================
# KEYBOARD SHORTCUTS
# =============================================================================


class KeyboardShortcuts:
    """Keyboard shortcut definitions."""

    # Tool hotkeys (number keys 0-9)
    TOOL_HOTKEYS = {
        1: "pencil",
        2: "eraser",
        3: "fill",
        4: "select",
        5: "shape",
        6: "stamp",
        7: "eyedropper",
        8: "autotile",
        9: "ai_gen",
        0: "autotile_fill",
    }

    # Shape tool mode keys
    SHAPE_RECTANGLE = "1"
    SHAPE_CIRCLE = "2"
    SHAPE_LINE = "3"
    SHAPE_TOGGLE_FILL = "f"

    # Stamp tool transform keys
    STAMP_ROTATE = "r"
    STAMP_FLIP_H = "h"
    STAMP_FLIP_V = "v"


# =============================================================================
# CONNECTIVITY MODES
# =============================================================================


class ConnectivityModes:
    """Connectivity modes for flood fill and selection tools."""

    # 4-way connectivity (cardinal directions only)
    FOUR_WAY = [
        (0, 1),  # Down
        (0, -1),  # Up
        (1, 0),  # Right
        (-1, 0),  # Left
    ]

    # 8-way connectivity (includes diagonals)
    EIGHT_WAY = [
        (0, 1),
        (0, -1),
        (1, 0),
        (-1, 0),  # Cardinal
        (1, 1),
        (1, -1),
        (-1, 1),
        (-1, -1),  # Diagonal
    ]


# =============================================================================
# FONT SETTINGS
# =============================================================================


class FontSettings:
    """Font settings for text rendering in tools."""

    # Font sizes
    SMALL_FONT_SIZE = 14
    MEDIUM_FONT_SIZE = 16
    LARGE_FONT_SIZE = 20

    # Font names (None = default pygame font)
    DEFAULT_FONT = None


# =============================================================================
# MOUSE BUTTON MAPPINGS
# =============================================================================


class MouseButtons:
    """Mouse button index mappings."""

    LEFT = 0
    MIDDLE = 1
    RIGHT = 2


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_tool_color(tool_name: str) -> Tuple[int, int, int]:
    """
    Get the color for a specific tool.

    Args:
        tool_name: Name of the tool

    Returns:
        RGB color tuple
    """
    tool_colors = {
        "pencil": ToolColors.PENCIL,
        "eraser": ToolColors.ERASER,
        "fill": ToolColors.FILL,
        "select": ToolColors.SELECT,
        "shape": ToolColors.SHAPE,
        "stamp": ToolColors.STAMP,
        "eyedropper": ToolColors.EYEDROPPER,
    }
    return tool_colors.get(tool_name, ToolColors.CURSOR_DEFAULT)


def get_cursor_color(tool_name: str) -> Tuple[int, int, int]:
    """
    Get the cursor color for a specific tool.

    Args:
        tool_name: Name of the tool

    Returns:
        RGB color tuple
    """
    cursor_colors = {
        "pencil": ToolColors.CURSOR_PENCIL,
        "eraser": ToolColors.CURSOR_ERASER,
        "fill": ToolColors.CURSOR_FILL,
        "select": ToolColors.CURSOR_SELECT_RECT,
        "shape": ToolColors.CURSOR_SHAPE,
        "stamp": ToolColors.CURSOR_STAMP,
        "eyedropper": ToolColors.CURSOR_EYEDROPPER,
    }
    return cursor_colors.get(tool_name, ToolColors.CURSOR_DEFAULT)


def get_default_stamps() -> Dict:
    """
    Get all default stamp definitions.

    Returns:
        Dict mapping stamp names to stamp definitions
    """
    return {
        "2x2_square": DefaultStamps.SQUARE_2X2,
        "3x3_square": DefaultStamps.SQUARE_3X3,
        "plus": DefaultStamps.PLUS,
        "diamond": DefaultStamps.DIAMOND,
    }


# =============================================================================
# CONFIGURATION VALIDATION
# =============================================================================


def validate_settings():
    """Validate all settings for correctness."""
    errors = []

    # Validate colors (must be RGB tuples)
    for attr_name in dir(ToolColors):
        if not attr_name.startswith("_"):
            color = getattr(ToolColors, attr_name)
            if not isinstance(color, tuple) or len(color) != 3:
                errors.append(f"ToolColors.{attr_name} must be RGB tuple")
            elif not all(0 <= c <= 255 for c in color):
                errors.append(f"ToolColors.{attr_name} values must be 0-255")

    # Validate limits (must be positive)
    for attr_name in dir(ToolLimits):
        if not attr_name.startswith("_"):
            limit = getattr(ToolLimits, attr_name)
            if not isinstance(limit, int) or limit <= 0:
                errors.append(f"ToolLimits.{attr_name} must be positive integer")

    # Validate alpha values (must be 0-255)
    if not (0 <= RenderSettings.SELECTION_OVERLAY_ALPHA <= 255):
        errors.append("RenderSettings.SELECTION_OVERLAY_ALPHA must be 0-255")
    if not (0 <= RenderSettings.SHAPE_PREVIEW_ALPHA <= 255):
        errors.append("RenderSettings.SHAPE_PREVIEW_ALPHA must be 0-255")
    if not (0 <= RenderSettings.STAMP_PREVIEW_ALPHA <= 255):
        errors.append("RenderSettings.STAMP_PREVIEW_ALPHA must be 0-255")

    return errors


# Run validation on import
_validation_errors = validate_settings()
if _validation_errors:
    print("Warning: Map tools settings validation errors:")
    for error in _validation_errors:
        print(f"  - {error}")
