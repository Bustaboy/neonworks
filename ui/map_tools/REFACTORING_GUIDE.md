# Map Tools Settings Refactoring Guide

This guide documents the hard-coded values found in map tools and how to refactor them to use the centralized `settings.py` file.

## Overview

A centralized `settings.py` file has been created with all configuration values. This allows for:
- Easy customization without editing multiple files
- Consistent values across all tools
- Better maintainability
- User preferences support (future)

## Settings Module

**File**: `ui/map_tools/settings.py`

Contains:
- `ToolColors` - RGB colors for tools and cursors
- `RenderSettings` - Line widths, alphas, sizes
- `ToolLimits` - Maximum values and thresholds
- `DefaultStamps` - Pre-defined stamp patterns
- `KeyboardShortcuts` - Hotkey mappings
- `ConnectivityModes` - 4-way/8-way neighbor offsets
- `FontSettings` - Font sizes and names
- `MouseButtons` - Mouse button index constants

## Refactoring Checklist

### ✅ Already Centralized
- [x] Max undo history (100) - `ToolLimits.MAX_UNDO_HISTORY`
- [x] Max fill cells (10,000) - `ToolLimits.MAX_FILL_CELLS`
- [x] Default stamp patterns - `DefaultStamps.*`
- [x] 4-way/8-way connectivity - `ConnectivityModes.*`
- [x] Tool hotkey mappings - `KeyboardShortcuts.TOOL_HOTKEYS`

### 🔧 To Be Refactored

The following files contain hard-coded values that should use settings:

#### 1. `base.py`
**Hard-coded values:**
```python
Line 109: pygame.draw.rect(screen, (255, 255, 255), (screen_x, screen_y, tile_size, tile_size), 2)
```

**Refactor to:**
```python
from .settings import ToolColors, RenderSettings

pygame.draw.rect(
    screen,
    ToolColors.CURSOR_DEFAULT,
    (screen_x, screen_y, tile_size, tile_size),
    RenderSettings.CURSOR_OUTLINE_WIDTH
)
```

---

#### 2. `pencil_tool.py`
**Hard-coded values:**
```python
Line 25: super().__init__("Pencil", 1, (0, 150, 0))
Line 205: pygame.draw.rect(screen, (0, 255, 0), (screen_x, screen_y, tile_size, tile_size), 3)
Lines 210-211: Crosshair colors and sizes
```

**Refactor to:**
```python
from .settings import ToolColors, RenderSettings, get_tool_color

# In __init__:
super().__init__("Pencil", 1, get_tool_color("pencil"))

# In render_cursor:
pygame.draw.rect(
    screen,
    ToolColors.CURSOR_PENCIL,
    (screen_x, screen_y, tile_size, tile_size),
    RenderSettings.CURSOR_HIGHLIGHT_WIDTH
)

# Crosshair:
pygame.draw.line(
    screen,
    ToolColors.CURSOR_PENCIL,
    (center_x - RenderSettings.CROSSHAIR_SIZE, center_y),
    (center_x + RenderSettings.CROSSHAIR_SIZE, center_y),
    RenderSettings.CROSSHAIR_WIDTH
)
```

---

#### 3. `eraser_tool.py`
**Hard-coded values:**
```python
Line 23: super().__init__("Eraser", 2, (150, 0, 0))
Lines 113-128: Red color (255, 0, 0) used multiple times, line width 3, sizes 5
```

**Refactor to:**
```python
from .settings import ToolColors, RenderSettings, get_tool_color

# In __init__:
super().__init__("Eraser", 2, get_tool_color("eraser"))

# In render_cursor:
pygame.draw.rect(
    screen,
    ToolColors.CURSOR_ERASER,
    (screen_x, screen_y, tile_size, tile_size),
    RenderSettings.CURSOR_HIGHLIGHT_WIDTH
)
```

---

#### 4. `fill_tool.py`
**Hard-coded values:**
```python
Line 32: super().__init__("Fill", 3, (0, 150, 150))
Line 35: self.max_fill_cells = 10000
Lines 50-59: Connectivity offsets (4-way/8-way)
Lines 172-182: Cyan color (0, 255, 255), sizes, widths
```

**Refactor to:**
```python
from .settings import ToolColors, ToolLimits, ConnectivityModes, get_tool_color

# In __init__:
super().__init__("Fill", 3, get_tool_color("fill"))
self.max_fill_cells = ToolLimits.MAX_FILL_CELLS

# For connectivity:
neighbors = ConnectivityModes.EIGHT_WAY if self.use_8way else ConnectivityModes.FOUR_WAY

# In render_cursor:
pygame.draw.rect(
    screen,
    ToolColors.CURSOR_FILL,
    (screen_x, screen_y, tile_size, tile_size),
    RenderSettings.CURSOR_HIGHLIGHT_WIDTH
)
```

---

#### 5. `select_tool.py`
**Hard-coded values:**
```python
Line 32: super().__init__("Select", 4, (150, 150, 0))
Lines 275-280: Yellow (255, 255, 0) and magenta (255, 100, 255), width 2, alpha 50
Lines 291-296: Magic wand selection rendering
```

**Refactor to:**
```python
from .settings import ToolColors, RenderSettings, get_tool_color

# In __init__:
super().__init__("Select", 4, get_tool_color("select"))

# In render_cursor:
color = ToolColors.CURSOR_SELECT_RECT if self.selection_mode == "rectangle" else ToolColors.CURSOR_SELECT_WAND

overlay.fill((
    *color,
    RenderSettings.SELECTION_OVERLAY_ALPHA
))
```

---

#### 6. `shape_tool.py`
**Hard-coded values:**
```python
Line 31: super().__init__("Shape", 5, (200, 100, 200))
Lines 285-301: Purple color (200, 100, 200), alpha 100, sizes
```

**Refactor to:**
```python
from .settings import ToolColors, RenderSettings, get_tool_color

# In __init__:
super().__init__("Shape", 5, get_tool_color("shape"))

# In render_cursor:
preview_surface.fill((
    *ToolColors.CURSOR_SHAPE,
    RenderSettings.SHAPE_PREVIEW_ALPHA
))
```

---

#### 7. `stamp_tool.py`
**Hard-coded values:**
```python
Line 120: super().__init__("Stamp", 6, (100, 200, 100))
Lines 120-143: Default stamp patterns (hardcoded coordinates)
Lines 293-317: Green color (100, 200, 100), alpha 100
```

**Refactor to:**
```python
from .settings import ToolColors, RenderSettings, DefaultStamps, get_tool_color, get_default_stamps

# In __init__:
super().__init__("Stamp", 6, get_tool_color("stamp"))
self._create_default_stamps()

# Use centralized stamps:
def _create_default_stamps(self):
    stamps = get_default_stamps()
    for stamp_id, stamp_def in stamps.items():
        # Create BrushStamp from definition
        ...

# In render_cursor:
preview_surface.fill((
    *ToolColors.CURSOR_STAMP,
    RenderSettings.STAMP_PREVIEW_ALPHA
))
```

---

#### 8. `eyedropper_tool.py`
**Hard-coded values:**
```python
Line 27: super().__init__("Eyedropper", 7, (255, 200, 0))
Lines 136-152: Orange color (255, 200, 0), sizes 5, 2, 3, 8
```

**Refactor to:**
```python
from .settings import ToolColors, RenderSettings, get_tool_color

# In __init__:
super().__init__("Eyedropper", 7, get_tool_color("eyedropper"))

# In render_cursor:
pygame.draw.circle(
    screen,
    ToolColors.CURSOR_EYEDROPPER,
    (center_x, center_y + 3),
    RenderSettings.EYEDROPPER_CIRCLE_RADIUS,
    RenderSettings.CURSOR_OUTLINE_WIDTH
)
```

---

#### 9. `undo_manager.py`
**Hard-coded values:**
```python
Line 99: def __init__(self, max_history: int = 100)
```

**Refactor to:**
```python
from .settings import ToolLimits

def __init__(self, max_history: int = ToolLimits.MAX_UNDO_HISTORY):
    ...
```

---

## Migration Steps

### Phase 1: Import Settings (Safe)
1. Add `from .settings import ...` to each tool file
2. No behavior changes yet
3. Test that imports work

### Phase 2: Replace Hard-coded Colors
1. Replace RGB tuples with `ToolColors.*` constants
2. Replace button colors with `get_tool_color()`
3. Replace cursor colors with `ToolColors.CURSOR_*`
4. Test visual appearance

### Phase 3: Replace Limits and Sizes
1. Replace max values with `ToolLimits.*`
2. Replace line widths with `RenderSettings.*`
3. Replace alpha values with `RenderSettings.*`
4. Test functionality

### Phase 4: Replace Connectivity and Patterns
1. Replace neighbor offsets with `ConnectivityModes.*`
2. Replace default stamps with `DefaultStamps.*`
3. Test fill and stamp tools

### Phase 5: User Preferences (Future)
1. Add settings UI panel
2. Allow users to customize colors, limits, etc.
3. Save/load preferences to file
4. Hot-reload settings

## Testing Checklist

After refactoring each file:
- [ ] Tool still appears in tool panel
- [ ] Tool color is correct
- [ ] Cursor renders correctly
- [ ] Tool functionality unchanged
- [ ] No import errors
- [ ] No visual regressions

## Benefits

✅ **Easy Customization**: Change colors/limits in one place
✅ **Consistency**: All tools use same values
✅ **Maintainability**: Clear organization of constants
✅ **User Preferences**: Future support for user customization
✅ **Theme Support**: Easy to add light/dark themes
✅ **Validation**: Settings are validated on import

## Future Enhancements

- [ ] Settings UI panel for in-game customization
- [ ] Save/load user preferences
- [ ] Multiple color themes (light, dark, high contrast)
- [ ] Per-tool settings (e.g., different fill limits per layer)
- [ ] Export/import settings presets
- [ ] Settings migration for updates

## Notes

- The `settings.py` file includes validation to catch errors
- All settings have docstrings explaining their purpose
- Helper functions (`get_tool_color`, etc.) simplify common tasks
- Settings are organized by category for easy navigation

---

**Status**: Settings file created, refactoring not yet applied to individual tools
**Reason**: Preserving working code; refactoring can be done incrementally
**Priority**: Low (nice to have, not blocking)
