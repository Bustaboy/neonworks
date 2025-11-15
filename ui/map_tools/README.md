# Map Tools

Advanced map editing tools for the NeonWorks Level Builder.

## Overview

The map tools system provides a comprehensive set of tools for editing tilemaps, including:

- **Basic Tools**: Pencil, Eraser
- **Advanced Tools**: Fill, Select, Shape, Stamp, Eyedropper
- **Undo/Redo System**: Full support for all operations
- **Layer Support**: All tools work across all tilemap layers

## Tools

### 1. Pencil Tool (Hotkey: 1)
**File**: `pencil_tool.py`

Paint tiles, entities, and events on the map.

**Features**:
- Left click to paint
- Drag to paint continuously
- Works with selected tile, entity, or event template
- Supports undo/redo

**Usage**:
- Select a tile from the palette
- Click on the map to paint
- Drag to paint multiple tiles

---

### 2. Eraser Tool (Hotkey: 2)
**File**: `eraser_tool.py`

Remove tiles, entities, and events from the map.

**Features**:
- Left click to erase
- Drag to erase continuously
- Erases from current layer
- Supports undo/redo

**Usage**:
- Click on a tile to erase it
- Drag to erase multiple tiles

---

### 3. Fill Tool (Hotkey: 3)
**File**: `fill_tool.py`

Advanced flood fill with multiple connectivity modes.

**Features**:
- 4-way connectivity (default)
- 8-way connectivity (includes diagonals)
- Safety limit (10,000 tiles max)
- Supports undo/redo
- Works on current layer

**Controls**:
- **Left click**: Flood fill with selected tile
- **Right click**: Toggle 4-way/8-way connectivity mode

**Usage**:
1. Select a tile from the palette
2. Left click on an area to fill
3. Right click to toggle connectivity mode

---

### 4. Select Tool (Hotkey: 4)
**File**: `select_tool.py`

Rectangle and magic wand selection with copy/paste support.

**Features**:
- Rectangle selection (drag to select)
- Magic wand selection (selects contiguous same-type tiles)
- Copy/cut/paste operations
- Works on current layer

**Controls**:
- **Left click + drag**: Rectangle selection
- **Right click**: Magic wand selection
- **Ctrl+C**: Copy selection
- **Ctrl+X**: Cut selection
- **Ctrl+V**: Paste selection

**Usage**:
1. Left click and drag to select a rectangular area
2. OR right click to select all connected tiles of the same type
3. Use Ctrl+C to copy, Ctrl+X to cut
4. Use Ctrl+V to paste at cursor position

---

### 5. Shape Tool (Hotkey: 5)
**File**: `shape_tool.py`

Draw geometric shapes (rectangles, circles, lines).

**Features**:
- Rectangle drawing
- Circle drawing (Bresenham's algorithm)
- Line drawing (Bresenham's algorithm)
- Outline and filled modes
- Real-time preview
- Supports undo/redo

**Controls**:
- **Left click + drag**: Draw shape
- **Keys 1-3**: Switch shape type (1=rectangle, 2=circle, 3=line)
- **Key F**: Toggle fill mode

**Usage**:
1. Select a tile from the palette
2. Click and drag to define the shape
3. Release to draw
4. Use number keys to switch shape types
5. Press F to toggle between outline and filled modes

**Shape Types**:
- **Rectangle (1)**: Draw axis-aligned rectangles
- **Circle (2)**: Draw circles with radius from start to end point
- **Line (3)**: Draw straight lines

---

### 6. Stamp Tool (Hotkey: 6)
**File**: `stamp_tool.py`

Paint with custom brush stamps.

**Features**:
- Multiple pre-defined stamps (2x2, 3x3, plus, diamond)
- Custom stamp creation (from selection)
- Rotate and flip stamps
- Real-time preview
- Supports undo/redo

**Controls**:
- **Left click**: Paint with current stamp
- **Drag**: Paint continuously
- **Right click**: Create stamp from selection (future)
- **Keys 1-9**: Switch between stamps
- **Key R**: Rotate stamp 90° clockwise
- **Key H**: Flip horizontally
- **Key V**: Flip vertically

**Pre-defined Stamps**:
1. **2x2 Square**: Small square stamp
2. **3x3 Square**: Medium square stamp
3. **Plus (+)**: Cross pattern
4. **Diamond**: Diamond pattern (5x5)

**Usage**:
1. Select a tile from the palette
2. Use number keys to select a stamp
3. Click to paint the stamp pattern
4. Use R, H, V keys to transform the stamp

---

### 7. Eyedropper Tool (Hotkey: 7)
**File**: `eyedropper_tool.py`

Pick tiles from the map to use as the current selection.

**Features**:
- Pick from current layer
- Pick from any layer (searches top to bottom)
- Shows picked layer
- Quick tool switching

**Controls**:
- **Left click**: Pick tile from current layer
- **Right click**: Pick tile from any layer
- **Shift + Click**: Pick and switch back to previous tool (future)

**Usage**:
1. Click on a tile to pick it
2. The selected tile becomes the current tile
3. Switch back to pencil/fill/shape tool to use the picked tile

---

## Undo/Redo System

**File**: `undo_manager.py`

Comprehensive undo/redo system supporting all map operations.

**Features**:
- Multi-level undo (100 actions by default)
- Multi-level redo
- Batch operations (e.g., flood fill)
- Action descriptions

**Controls**:
- **Ctrl+Z**: Undo last action
- **Ctrl+Y** or **Ctrl+Shift+Z**: Redo last undone action

**Supported Operations**:
- Single tile changes
- Batch tile changes (fill, shape, stamp)
- Entity creation/deletion (future)

---

## Architecture

### Base Classes

**File**: `base.py`

#### MapTool
Abstract base class for all map tools.

**Methods**:
- `on_mouse_down(grid_x, grid_y, button, context)`: Handle mouse press
- `on_mouse_drag(grid_x, grid_y, button, context)`: Handle mouse drag
- `on_mouse_up(grid_x, grid_y, button, context)`: Handle mouse release
- `render_cursor(screen, grid_x, grid_y, tile_size, camera_offset)`: Render tool cursor

#### ToolContext
Provides access to editor state for tools.

**Properties**:
- `tilemap`: Current tilemap
- `world`: ECS world
- `events`: Event list
- `tile_palette`: Available tiles
- `current_layer`: Active layer
- `selected_tile`: Selected tile type
- `undo_manager`: Undo/redo manager
- And more...

#### ToolManager
Manages tool registration and switching.

**Methods**:
- `register_tool(tool_id, tool)`: Register a tool
- `set_active_tool(tool_id)`: Switch to a tool
- `get_active_tool()`: Get current tool
- `get_tool_by_hotkey(hotkey)`: Get tool by hotkey

---

## Integration

### Level Builder Integration

The map tools are integrated into the Level Builder UI (`level_builder_ui.py`):

```python
from neonworks.ui.map_tools import (
    EraserTool,
    EyedropperTool,
    FillTool,
    PencilTool,
    SelectTool,
    ShapeTool,
    StampTool,
    ToolManager,
    UndoManager,
)

# In __init__:
self.tool_manager = ToolManager()
self.undo_manager = UndoManager(max_history=100)
self._initialize_tools()

# Tool registration:
def _initialize_tools(self):
    self.tool_manager.register_tool("pencil", PencilTool())
    self.tool_manager.register_tool("eraser", EraserTool())
    self.tool_manager.register_tool("fill", FillTool())
    self.tool_manager.register_tool("select", SelectTool())
    self.tool_manager.register_tool("shape", ShapeTool())
    self.tool_manager.register_tool("stamp", StampTool())
    self.tool_manager.register_tool("eyedropper", EyedropperTool())
```

---

## Extending the System

### Creating a New Tool

1. Create a new file in `ui/map_tools/`
2. Inherit from `MapTool`
3. Implement required methods:
   - `on_mouse_down()`
   - `on_mouse_drag()`
   - `on_mouse_up()`
   - `render_cursor()`
4. Add to `__init__.py`
5. Register in Level Builder UI

**Example**:

```python
from .base import MapTool, ToolContext
import pygame

class MyCustomTool(MapTool):
    def __init__(self):
        super().__init__("My Tool", 8, (255, 0, 255))

    def on_mouse_down(self, grid_x, grid_y, button, context):
        # Your logic here
        return True

    def on_mouse_drag(self, grid_x, grid_y, button, context):
        return False

    def on_mouse_up(self, grid_x, grid_y, button, context):
        return False

    def render_cursor(self, screen, grid_x, grid_y, tile_size, camera_offset):
        # Custom cursor rendering
        pass
```

### Creating Custom Undo Actions

```python
from .undo_manager import UndoableAction

class MyCustomAction(UndoableAction):
    def __init__(self, data):
        self.data = data
        self.old_state = save_current_state()

    def undo(self):
        restore_state(self.old_state)

    def redo(self):
        apply_action(self.data)

    def get_description(self):
        return "My custom action"

# Use it:
action = MyCustomAction(my_data)
context.undo_manager.record_action(action)
```

---

## Testing

All tools support:
- ✅ Multiple layers
- ✅ Undo/redo
- ✅ Real-time preview
- ✅ Keyboard shortcuts
- ✅ Mouse drag operations

---

## Future Enhancements

- [ ] Custom stamp creation from selection
- [ ] Entity undo/redo support
- [ ] Transform operations (rotate, flip selection)
- [ ] Pattern fill tool
- [ ] Gradient tool
- [ ] Randomize tool
- [ ] Auto-tile aware tools
- [ ] Brush size support for pencil/eraser
- [ ] Layer merge/split operations

---

## Credits

Developed for NeonWorks 2D Game Engine
Version: 0.1.0
Date: 2025-11-15
