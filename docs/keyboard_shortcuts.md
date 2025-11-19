# NeonWorks Keyboard Shortcuts

**Version:** 1.0
**Last Updated:** 2025-11-15

This document provides a comprehensive reference of all keyboard shortcuts available in NeonWorks.

## Quick Access

- **Press `?` (Shift+/)** to show the interactive shortcuts overlay at any time
- **Press `F2`** to open Settings and customize key bindings in the Shortcuts tab

---

## Table of Contents

1. [General Shortcuts](#general-shortcuts)
2. [UI Editors](#ui-editors)
3. [File Operations](#file-operations)
4. [Editor Commands](#editor-commands)
5. [Gameplay Controls](#gameplay-controls)
6. [Camera Controls](#camera-controls)
7. [Debug Shortcuts](#debug-shortcuts)
8. [Context-Sensitive Shortcuts](#context-sensitive-shortcuts)
9. [Customizing Shortcuts](#customizing-shortcuts)

---

## General Shortcuts

These shortcuts work in all contexts unless specified otherwise.

| Shortcut | Action | Description |
|----------|--------|-------------|
| `?` (Shift+/) | Show Shortcuts Overlay | Display the interactive shortcuts help overlay |
| `F1` | Debug Console | Toggle the debug console for logging and commands |
| `F2` | Settings | Open the settings menu |
| `Escape` | Menu/Cancel | Open menu or cancel current action |
| `Ctrl+Space` | AI Assistant | Toggle the AI assistant panel |

---

## UI Editors

Access visual editors for game development. Most are accessed via function keys (F1-F12).

| Shortcut | Editor | Context | Description |
|----------|--------|---------|-------------|
| `F1` | Debug Console | All | View logs, errors, and execute debug commands |
| `F2` | Settings | All | Configure audio, graphics, input, shortcuts, and gameplay |
| `F3` | Building UI | Game | Build and place structures in-game |
| `F4` | Level Builder | Editor | Design levels and maps visually |
| `F5` | Event Editor | Editor | Create and edit game events |
| `F6` | Database Editor | Editor | Edit game data tables |
| `F7` | Character Generator | Editor | Generate and edit characters |
| `Shift+F7` | AI Animator | Editor | AI-powered animation editor |
| `F8` | Quest Editor | Editor | Design quests and dialogue trees |
| `F9` | Combat UI | Game | View combat interface and controls |
| `F10` | Game HUD | Game | Toggle the in-game heads-up display |
| `F11` | Autotile Editor | Editor | Edit autotile configurations |
| `F12` | Navmesh Editor | Editor | Edit navigation meshes for pathfinding |
| `Ctrl+M` | Map Manager | Editor | Manage multiple maps and transitions |
| `Ctrl+H` | History Viewer | Editor | View undo/redo history for active editor |

> The Asset Browser and Project Manager are available from the workspace toolbar in the editor UI rather than direct F-key shortcuts.

---

## File Operations

Manage project files and saves.

| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl+N` | New Project | Create a new game project |
| `Ctrl+O` | Open Project | Open an existing project |
| `Ctrl+S` | Save Project | Save the current project |
| `Ctrl+Shift+S` | Save Project As | Save project with a new name |
| `Ctrl+F5` | Quick Save | Quick save (in game mode) |
| `Ctrl+F9` | Quick Load | Quick load (in game mode) |

---

## Editor Commands

These shortcuts are active when using editor tools (Level Builder, Navmesh Editor, etc.).

| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl+Z` | Undo | Undo the last action |
| `Ctrl+Y` | Redo | Redo the previously undone action |
| `Ctrl+Shift+Z` | Redo (Alt) | Alternative redo shortcut |
| `Ctrl+H` | History Viewer | Show undo/redo history for current editor |
| `Ctrl+G` | Toggle Grid | Show/hide the grid overlay |

---

## Gameplay Controls

Active during gameplay (game mode).

### Movement

| Shortcut | Action | Description |
|----------|--------|-------------|
| `W` | Move Up | Move character up |
| `S` | Move Down | Move character down |
| `A` | Move Left | Move character left |
| `D` | Move Right | Move character right |
| `Arrow Keys` | Camera Movement | Move camera in the corresponding direction |

### Actions

| Shortcut | Action | Description |
|----------|--------|-------------|
| `E` | Interact | Interact with objects/NPCs |
| `Space` | Attack/Confirm | Attack or confirm selection |
| `I` | Inventory | Open inventory |
| `Tab` | Character Stats | View character statistics |
| `B` | Build Mode | Enter building mode (when available) |

---

## Camera Controls

Control camera position and zoom.

| Shortcut | Action | Description |
|----------|--------|-------------|
| `Up Arrow` | Camera Up | Move camera up |
| `Down Arrow` | Camera Down | Move camera down |
| `Left Arrow` | Camera Left | Move camera left |
| `Right Arrow` | Camera Right | Move camera right |
| `+` / `=` | Zoom In | Zoom camera in |
| `-` | Zoom Out | Zoom camera out |
| `0` | Reset Camera | Reset camera to default position |

---

## Debug Shortcuts

Advanced shortcuts for debugging and development.

| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl+F3` | Toggle Debug Overlay | Show/hide debug information overlay |
| `Ctrl+G` | Toggle Grid | Show/hide the grid |
| `Ctrl+C` | Toggle Collision Debug | Show/hide collision boundaries |

---

## Context-Sensitive Shortcuts

Some shortcuts behave differently depending on the current context:

### Global Context
- Available in all modes
- Examples: `F1` (Debug Console), `F2` (Settings), `F8` (Project Manager)

### Game Context
- Active during gameplay
- Examples: `W`/`A`/`S`/`D` (Movement), `E` (Interact), `I` (Inventory)
- Includes: `F3` (Building UI), `F9` (Combat UI), `F10` (HUD)

### Editor Context
- Active when using editor tools
- Examples: `Ctrl+Z` (Undo), `Ctrl+Y` (Redo), `Ctrl+H` (History)
- Includes: `F4` (Level Builder), `F5` (Event Editor), `F6` (Quest Editor), `F7` (Asset Browser), `F11` (Autotile), `F12` (Navmesh)

### Combat Context
- Active during combat encounters
- Inherits game controls with combat-specific additions

### Building Context
- Active in building mode
- Inherits game controls with building-specific additions

---

## Customizing Shortcuts

You can customize all keyboard shortcuts to your preference:

### Via Settings UI

1. Press `F2` to open Settings
2. Click the **Shortcuts** tab
3. Click on any shortcut button you want to change
4. Press the new key combination (including modifiers like Ctrl, Shift, Alt)
5. Click **Save & Close** or **Apply** to save your changes

### Filtering Shortcuts

In the Settings > Shortcuts tab, you can filter shortcuts by category:
- **All** - Show all shortcuts
- **UI** - UI editor shortcuts
- **Editor** - Editor-specific commands
- **File** - File operations
- **Movement** - Movement controls
- **Actions** - Gameplay actions
- **Camera** - Camera controls

### Reset to Defaults

If you want to restore all shortcuts to their default values:
1. Open Settings (`F2`)
2. Go to the **Shortcuts** tab
3. Click **Reset All** button
4. Confirm and save

### Configuration Files

Keyboard shortcuts are saved in:
- **User settings:** `hotkeys.json` in your project directory
- **Default config:** Built into `core/hotkey_manager.py`

The `hotkeys.json` file structure:
```json
{
  "hotkeys": [
    {
      "key": 282,
      "modifiers": [],
      "action": "toggle_debug_console",
      "context": "global",
      "description": "Toggle Debug Console",
      "category": "UI",
      "enabled": true
    }
  ],
  "current_context": "global"
}
```

---

## Modifier Keys

Shortcuts can use modifier keys for combinations:

- **Ctrl** - Control key
- **Shift** - Shift key
- **Alt** - Alt/Option key

### Examples
- `Ctrl+S` - Hold Ctrl and press S
- `Shift+F7` - Hold Shift and press F7
- `Ctrl+Shift+Z` - Hold Ctrl and Shift, then press Z

---

## Shortcuts by Category

### UI (User Interface)
- `F1` - Debug Console
- `F2` - Settings
- `F3` - Building UI
- `F4` - Level Builder
- `F5` - Event Editor
- `F6` - Quest Editor
- `F7` - Asset Browser
- `Shift+F7` - AI Animator
- `F8` - Project Manager
- `F9` - Combat UI
- `F10` - Game HUD
- `F11` - Autotile Editor
- `F12` - Navmesh Editor
- `Ctrl+M` - Map Manager
- `Ctrl+Space` - AI Assistant
- `I` - Inventory
- `Tab` - Character Stats

### File Operations
- `Ctrl+N` - New Project
- `Ctrl+O` - Open Project
- `Ctrl+S` - Save Project
- `Ctrl+Shift+S` - Save Project As
- `Ctrl+F5` - Quick Save
- `Ctrl+F9` - Quick Load

### Editor Commands
- `Ctrl+Z` - Undo
- `Ctrl+Y` - Redo
- `Ctrl+Shift+Z` - Redo (Alternative)
- `Ctrl+H` - History Viewer
- `Ctrl+G` - Toggle Grid

### Movement
- `W` - Move Up
- `S` - Move Down
- `A` - Move Left
- `D` - Move Right

### Actions
- `E` - Interact
- `Space` - Attack/Confirm
- `Escape` - Menu/Cancel
- `B` - Build Mode

### Camera
- `Up Arrow` - Camera Up
- `Down Arrow` - Camera Down
- `Left Arrow` - Camera Left
- `Right Arrow` - Camera Right
- `+`/`=` - Zoom In
- `-` - Zoom Out
- `0` - Reset Camera

### Debug
- `Ctrl+F3` - Toggle Debug Overlay
- `Ctrl+G` - Toggle Grid
- `Ctrl+C` - Toggle Collision Debug

### Help
- `?` (Shift+/) - Show Shortcuts Overlay

---

## Tips and Best Practices

### Learning Shortcuts
1. **Start with essentials**: Learn F1 (Debug), F2 (Settings), and ? (Help) first
2. **Use the overlay**: Press `?` to see all shortcuts organized by category
3. **Practice in editor**: The editor mode has the most shortcuts to learn
4. **Customize as needed**: Adjust shortcuts to match your workflow

### Avoiding Conflicts
- The hotkey manager automatically detects conflicts
- Check Settings > Shortcuts for any warnings
- Context-sensitive shortcuts prevent most conflicts (same key, different contexts)

### Workflow Optimization
- **Editors**: Use F4-F7, F11-F12 for quick editor access
- **Testing**: Use Ctrl+F5 for quick save before testing
- **Debugging**: Keep F1 (Debug Console) handy for logs
- **Iteration**: Use Ctrl+Z/Ctrl+Y frequently when designing

---

## Troubleshooting

### Shortcut Not Working
1. Check if another UI has focus (close overlays/modals)
2. Verify the shortcut in Settings > Shortcuts tab
3. Check if context is correct (editor vs game mode)
4. Look for conflicts in the shortcuts list

### Lost Custom Shortcuts
1. Check `hotkeys.json` file in project directory
2. Use **Reset to Defaults** if file is corrupted
3. Reconfigure shortcuts and save again

### Keyboard Layout Issues
- NeonWorks uses pygame key codes (hardware-based)
- Some layouts may have different physical key positions
- Customize shortcuts to match your keyboard layout

---

## Developer Notes

For developers extending NeonWorks:

### Adding New Shortcuts

In your code:
```python
from neonworks.core.hotkey_manager import get_hotkey_manager, HotkeyContext

# Get hotkey manager
hotkey_manager = get_hotkey_manager()

# Register a new shortcut
hotkey_manager.register(
    key=pygame.K_t,
    action="my_custom_action",
    callback=my_callback_function,
    modifiers={"ctrl"},
    context=HotkeyContext.EDITOR,
    description="My Custom Tool",
    category="Custom Tools"
)
```

### Context Management

Set context based on game state:
```python
# In game mode
hotkey_manager.set_context(HotkeyContext.GAME)

# In editor mode
hotkey_manager.set_context(HotkeyContext.EDITOR)

# In combat
hotkey_manager.set_context(HotkeyContext.COMBAT)
```

### Event Handling

Let the hotkey manager handle events:
```python
def handle_event(self, event):
    if event.type == pygame.KEYDOWN:
        action = hotkey_manager.handle_event(event)
        if action:
            # Hotkey was triggered
            return True
    return False
```

---

## Quick Reference Card

**Print this section for quick reference!**

### Most Used Shortcuts
```
?           - Show shortcuts overlay
F1          - Debug console
F2          - Settings
F4          - Level builder
Ctrl+S      - Save project
Ctrl+Z      - Undo
Ctrl+Y      - Redo
W/A/S/D     - Movement
E           - Interact
Space       - Attack/Confirm
Escape      - Menu/Cancel
```

### Editor Essentials
```
F4          - Level builder
F5          - Event editor
F6          - Quest editor
F7          - Asset browser
F12         - Navmesh editor
Ctrl+H      - History viewer
Ctrl+M      - Map manager
```

### Quick Access
```
Ctrl+N      - New project
Ctrl+O      - Open project
Ctrl+F5     - Quick save (game)
Ctrl+Space  - AI assistant
```

---

## Additional Resources

- **CLAUDE.md** - Development guidelines and architecture
- **README.md** - Project overview and getting started
- **STATUS.md** - Current implementation status
- **DEVELOPER_GUIDE.md** - Development best practices

For questions or issues with keyboard shortcuts:
1. Check the interactive overlay (`?`)
2. Review Settings > Shortcuts tab
3. Consult this documentation
4. Check `hotkeys.json` configuration file

---

**Last Updated:** 2025-11-15
**NeonWorks Version:** 0.1.0
**Maintained by:** NeonWorks Team
