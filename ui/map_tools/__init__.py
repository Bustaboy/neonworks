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
from .shape_tool import ShapeTool
from .stamp_tool import StampTool
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
]
