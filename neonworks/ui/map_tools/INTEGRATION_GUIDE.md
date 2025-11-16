# Map Tools Settings Integration Guide

This guide shows how to integrate the new settings system, theme system, and settings UI panel with your Level Builder.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Adding Settings Panel to Level Builder](#adding-settings-panel)
3. [Loading Preferences on Startup](#loading-preferences)
4. [Adding Theme Switching](#theme-switching)
5. [Customizing the Settings Panel](#customization)
6. [Complete Integration Example](#complete-example)

---

## Quick Start

### Minimum Integration (3 Lines of Code)

```python
from ui.map_tools import SettingsPanel, load_and_apply_preferences

# In your Level Builder __init__:
self.settings_panel = SettingsPanel()
load_and_apply_preferences()  # Load user preferences

# In your Level Builder render method:
self.settings_panel.render(screen)
```

### Add Hotkey (F11)

```python
# In your Level Builder handle_event method:
if event.type == pygame.KEYDOWN:
    if event.key == pygame.K_F11:
        self.settings_panel.toggle()
```

That's it! Users can now press **F11** to open settings, change themes, adjust limits, and save preferences.

---

## Adding Settings Panel to Level Builder

### Step 1: Import SettingsPanel

```python
# In ui/level_builder_ui.py
from .map_tools import SettingsPanel, load_and_apply_preferences
```

### Step 2: Initialize in __init__

```python
class LevelBuilderUI:
    def __init__(self, world, renderer):
        self.world = world
        self.renderer = renderer

        # ... existing initialization ...

        # Add settings panel
        self.settings_panel = SettingsPanel(
            x=100,      # Panel X position
            y=100,      # Panel Y position
            width=600,  # Panel width
            height=500  # Panel height
        )

        # Load user preferences on startup
        load_and_apply_preferences()
```

### Step 3: Handle Events

```python
def handle_event(self, event):
    """Handle pygame events."""

    # Let settings panel handle events first (when visible)
    if self.settings_panel.handle_event(event):
        return True

    # Existing event handling
    if event.type == pygame.KEYDOWN:
        # F11 to toggle settings panel
        if event.key == pygame.K_F11:
            self.settings_panel.toggle()
            return True

        # ... rest of your keyboard handling ...

    # ... rest of your event handling ...
    return False
```

### Step 4: Render

```python
def render(self, screen):
    """Render level builder UI."""

    # Render your existing UI first
    # ... your tilemap, tools, etc ...

    # Render settings panel last (so it appears on top)
    self.settings_panel.render(screen)
```

---

## Loading Preferences on Startup

The preferences system automatically loads user settings from `~/.neonworks/map_tools_prefs.json`.

### Basic Usage

```python
from ui.map_tools import load_and_apply_preferences

# In your application startup (main.py or Level Builder __init__)
load_and_apply_preferences()
```

This will:
- Load saved theme
- Apply custom limits (max fill cells, undo history)
- Apply rendering settings (cursor width, alpha values)
- Fall back to defaults if no preferences file exists

### Manual Control

```python
from ui.map_tools import load_preferences, apply_preferences

# Load preferences without applying
prefs = load_preferences()

if prefs:
    # Check or modify preferences before applying
    if prefs.get("theme") == "high_contrast":
        # Do something special for high contrast mode
        pass

    # Apply preferences
    apply_preferences(prefs)
```

---

## Theme Switching

### Programmatic Theme Switching

```python
from ui.map_tools import get_theme_manager

# Get theme manager
theme_manager = get_theme_manager()

# List available themes
themes = theme_manager.list_themes()
# Returns: {"default": "Default", "dark": "Dark", "light": "Light", "high_contrast": "High Contrast"}

# Switch theme
theme_manager.set_theme("dark")

# Get current theme
current = theme_manager.get_current_theme()
print(f"Current theme: {current.name}")
```

### Creating Custom Themes

```python
from ui.map_tools import Theme, get_theme_manager

# Create custom theme
my_theme = Theme(
    name="My Theme",
    description="Custom colors for my workflow",
    # Tool button colors
    tool_pencil=(50, 200, 50),
    tool_eraser=(200, 50, 50),
    # Cursor colors
    cursor_pencil=(100, 255, 100),
    cursor_eraser=(255, 100, 100),
    # ... customize all colors ...
)

# Add to theme manager
theme_manager = get_theme_manager()
theme_manager.add_theme("my_theme", my_theme)

# Switch to custom theme
theme_manager.set_theme("my_theme")
```

---

## Customization

### Customizing Panel Position

```python
# Create panel at specific position
self.settings_panel = SettingsPanel(
    x=200,       # 200px from left
    y=50,        # 50px from top
    width=700,   # Wider panel
    height=600   # Taller panel
)
```

### Customizing Panel Colors

```python
# After creating panel, customize colors
self.settings_panel.bg_color = (50, 50, 50)          # Background
self.settings_panel.panel_color = (40, 40, 40)       # Panel background
self.settings_panel.text_color = (255, 255, 255)     # Text
self.settings_panel.button_color = (70, 70, 70)      # Button
self.settings_panel.button_hover_color = (90, 90, 90)  # Button hover
```

### Adding More Sliders

You can extend the settings panel to include more sliders for custom settings:

```python
# After creating panel, add custom slider
self.settings_panel.sliders["custom_setting"] = {
    "label": "My Custom Setting",
    "value": 50,
    "min": 0,
    "max": 100,
    "rect": pygame.Rect(0, 0, 0, 0),  # Will be positioned by layout
}
```

---

## Complete Example

Here's a complete integration example:

```python
# ui/level_builder_ui.py
import pygame
from .map_tools import (
    SettingsPanel,
    load_and_apply_preferences,
    get_theme_manager,
)

class LevelBuilderUI:
    def __init__(self, world, renderer):
        """Initialize Level Builder UI."""
        self.world = world
        self.renderer = renderer
        self.visible = True

        # Existing components
        self.tool_manager = ToolManager()
        self.undo_manager = UndoManager()
        # ... register tools ...

        # Settings panel
        self.settings_panel = SettingsPanel(x=100, y=100, width=600, height=500)

        # Load user preferences (theme, limits, etc.)
        load_and_apply_preferences()

        print("✓ Level Builder initialized with settings panel")

    def handle_event(self, event):
        """Handle pygame events."""
        if not self.visible:
            return False

        # Settings panel handles events first (when visible)
        if self.settings_panel.handle_event(event):
            return True

        # Keyboard shortcuts
        if event.type == pygame.KEYDOWN:
            # F11: Toggle settings panel
            if event.key == pygame.K_F11:
                self.settings_panel.toggle()
                return True

            # Ctrl+S: Quick save preferences
            if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                from .map_tools import save_preferences
                prefs = {
                    "theme": get_theme_manager().current_theme.name,
                    "max_fill_cells": ToolLimits.MAX_FILL_CELLS,
                    # ... gather current settings ...
                }
                save_preferences(prefs)
                return True

            # ... your other keyboard shortcuts ...

        # ... rest of your event handling ...
        return False

    def update(self, dt):
        """Update level builder logic."""
        # Your update logic here
        pass

    def render(self, screen):
        """Render level builder UI."""
        if not self.visible:
            return

        # Render tilemap
        # self.tilemap.render(screen, camera_offset)

        # Render tools
        # self.tool_manager.render_cursor(...)

        # Render UI elements
        # ...

        # Render settings panel (always last, so it's on top)
        self.settings_panel.render(screen)
```

---

## Features Overview

### Settings Panel UI

**Theme Selector:**
- Dropdown with 4 built-in themes
- Live preview when selected
- Saves to preferences

**Sliders:**
- Max Fill Cells (100 - 50,000)
- Max Undo History (10 - 500)
- Cursor Width (1 - 5px)
- Selection Alpha (10 - 200)

**Buttons:**
- **Apply** - Apply settings without saving
- **Reset** - Reset to defaults
- **Save** - Save to preferences file
- **Load** - Load from preferences file
- **Close** - Close panel

**Indicators:**
- "* Unsaved changes" when modified
- Theme name in dropdown
- Slider values next to sliders

### Built-in Themes

1. **Default** - Original vibrant colors for dark backgrounds
2. **Dark** - Muted colors for dark mode, reduces eye strain
3. **Light** - Darker colors optimized for light backgrounds
4. **High Contrast** - Maximum contrast for accessibility

### Preferences File

**Location:** `~/.neonworks/map_tools_prefs.json`

**Format:**
```json
{
  "theme": "dark",
  "max_fill_cells": 5000,
  "max_undo_history": 150,
  "cursor_width": 2,
  "selection_alpha": 50,
  "custom_themes": {}
}
```

---

## Hotkey Recommendations

Since MasterUIManager uses F1-F10, we recommend:

- **F11** - Settings Panel (as shown in this guide)
- **Ctrl+S** - Quick save preferences
- **Ctrl+Shift+T** - Cycle themes (if you add this feature)

---

## Troubleshooting

### Settings panel doesn't appear

**Check:**
1. Is `panel.visible` set to True? Call `panel.show()` or `panel.toggle()`
2. Is panel rendered AFTER other UI (so it's on top)?
3. Check panel position - is it within screen bounds?

### Preferences don't save

**Check:**
1. Does `~/.neonworks` directory exist? (auto-created on first save)
2. Check file permissions
3. Look for error messages in console

### Theme doesn't apply

**Check:**
1. Is theme ID valid? Call `theme_manager.list_themes()` to see available themes
2. Did you call `set_theme()` after loading?
3. Check console for error messages

---

## Next Steps

1. **Add settings button to your UI toolbar** - Instead of just F11, add a visual button
2. **Add theme preview thumbnails** - Show small color swatches in theme dropdown
3. **Add more custom sliders** - Extend panel with your own settings
4. **Add undo/redo buttons** - Integrate with the UndoManager
5. **Add preset import/export** - Let users share their settings

---

## API Reference

### SettingsPanel

```python
class SettingsPanel:
    def __init__(self, x=100, y=100, width=600, height=500)
    def toggle()           # Toggle visibility
    def show()             # Show panel
    def hide()             # Hide panel
    def handle_event(event) -> bool  # Handle pygame event
    def render(screen)     # Render panel
```

### Preferences Functions

```python
save_preferences(prefs: Dict) -> bool
load_preferences() -> Optional[Dict]
apply_preferences(prefs: Dict)
export_preferences(output_path: str) -> bool
import_preferences(input_path: str) -> Optional[Dict]
load_and_apply_preferences()  # Convenience function
```

### Theme Manager

```python
theme_manager = get_theme_manager()
theme_manager.list_themes() -> Dict[str, str]
theme_manager.set_theme(theme_id: str) -> bool
theme_manager.get_theme(theme_id: str) -> Optional[Theme]
theme_manager.get_current_theme() -> Optional[Theme]
theme_manager.add_theme(theme_id: str, theme: Theme)
```

---

**Status:** Ready for integration
**Tested:** All syntax validated
**Documentation:** Complete

For questions or issues, see `REFACTORING_GUIDE.md` and source code docstrings.
