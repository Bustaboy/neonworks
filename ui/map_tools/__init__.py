"""
Map editing tools for the level builder.

Provides a tool architecture for map editing operations including
pencil, eraser, fill, selection, shape, stamp, and eyedropper tools.
"""

from .base import MapTool, ToolContext, ToolManager
from .eraser_tool import EraserTool
from .eyedropper_tool import EyedropperTool
from .fill_tool import FillTool
from .pencil_tool import PencilTool
from .preferences import (
    apply_preferences,
    export_preferences,
    import_preferences,
    load_and_apply_preferences,
    load_preferences,
    save_preferences,
)
from .select_tool import SelectTool
from .settings import (
    ConnectivityModes,
    DefaultStamps,
    FontSettings,
    KeyboardShortcuts,
    MouseButtons,
    RenderSettings,
    ToolColors,
    ToolLimits,
    get_cursor_color,
    get_default_stamps,
    get_tool_color,
)
from .settings_panel import SettingsPanel
from .shape_tool import ShapeTool
from .stamp_tool import StampTool
from .themes import Theme, ThemeManager, get_theme_manager
from .undo_manager import UndoManager, UndoableAction

__all__ = [
    "MapTool",
    "ToolContext",
    "ToolManager",
    "PencilTool",
    "EraserTool",
    "FillTool",
    "SelectTool",
    "ShapeTool",
    "StampTool",
    "EyedropperTool",
    "UndoManager",
    "UndoableAction",
    # Settings
    "ToolColors",
    "RenderSettings",
    "ToolLimits",
    "DefaultStamps",
    "KeyboardShortcuts",
    "ConnectivityModes",
    "FontSettings",
    "MouseButtons",
    "get_tool_color",
    "get_cursor_color",
    "get_default_stamps",
    # Themes
    "Theme",
    "ThemeManager",
    "get_theme_manager",
    # Settings Panel
    "SettingsPanel",
    # Preferences
    "save_preferences",
    "load_preferences",
    "apply_preferences",
    "export_preferences",
    "import_preferences",
    "load_and_apply_preferences",
]
