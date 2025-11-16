"""
Map Components - Modular UI components for map editor

This package provides reusable UI components for the map editor:
- TilesetPickerUI: Visual tile selection palette (from tileset_picker_ui)
- LayerPanelUI: Layer list with controls (from layer_panel_ui)
- MinimapUI: Overview minimap with click-to-navigate
- ToolOptionsPanel: Current tool settings panel
- MapPropertiesDialog: Map settings editor dialog

Import these components to build a comprehensive map editing interface.
"""

from .map_properties import MapPropertiesDialog

# Import components from this package
from .minimap import MinimapUI
from .tool_options import ToolOptionsPanel

# Re-export existing components from parent ui directory
# These were already implemented and are being consolidated here
try:
    from ..tileset_picker_ui import TilesetPickerUI
except ImportError:
    # Fallback if import path changes
    from neonworks.ui.tileset_picker_ui import TilesetPickerUI

try:
    from ..layer_panel_ui import LayerPanelUI
except ImportError:
    # Fallback if import path changes
    from neonworks.ui.layer_panel_ui import LayerPanelUI


__all__ = [
    "TilesetPickerUI",
    "LayerPanelUI",
    "MinimapUI",
    "ToolOptionsPanel",
    "MapPropertiesDialog",
]

__version__ = "0.1.0"
