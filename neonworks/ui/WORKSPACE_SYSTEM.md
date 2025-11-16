# Workspace System Documentation

**Version:** 1.0
**Created:** 2025-11-15
**Status:** Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Workspaces](#workspaces)
4. [AI Context Integration](#ai-context-integration)
5. [Usage Guide](#usage-guide)
6. [Developer Guide](#developer-guide)

---

## Overview

The **Workspace System** provides a visual, organized way to access all NeonWorks tools and editors. It solves the "hidden tools" problem by making all editors discoverable through a visual toolbar interface.

### Key Features

- ✅ **4 organized workspaces** (Play, Level Editor, Content Creation, Settings & Debug)
- ✅ **Visual toolbar** with clickable buttons for all tools
- ✅ **AI context export** - AI assistant knows what workspace/tools are active
- ✅ **F-key shortcuts** still work for power users
- ✅ **Discoverable** - no need to memorize hotkeys
- ✅ **Industry-standard** design (inspired by Godot, Unity, Unreal)

---

## Architecture

### Core Components

```
ui/workspace_system.py       # Workspace definitions and AI context export
ui/workspace_toolbar.py      # Visual toolbar UI component
ui/master_ui_manager.py      # Integration point
~/.neonworks/ai_context.json # AI assistant context file (auto-generated)
```

### Class Diagram

```
WorkspaceManager (singleton)
├─ Workspace (Play)
│  ├─ ToolDefinition (Game HUD)
│  ├─ ToolDefinition (Combat)
│  └─ ToolDefinition (Building)
├─ Workspace (Level Editor)
│  ├─ ToolDefinition (Level Builder)
│  ├─ ToolDefinition (Autotile Editor)
│  ├─ ToolDefinition (Navmesh Editor)
│  └─ ToolDefinition (Event Editor)
├─ Workspace (Content Creation)
│  ├─ ToolDefinition (Asset Browser)
│  ├─ ToolDefinition (AI Animator) ← NEW!
│  └─ ToolDefinition (Quest Editor)
└─ Workspace (Settings & Debug)
   ├─ ToolDefinition (Settings)
   ├─ ToolDefinition (Debug Console)
   └─ ToolDefinition (Project Manager)
```

---

## Workspaces

### 🎮 Play Mode

**Purpose:** Play and test your game

| Tool | Hotkey | Description |
|------|--------|-------------|
| Game HUD | F10 | In-game heads-up display |
| Combat | F9 | Combat interface |
| Building | F3 | Building placement |

**Use Case:** Testing gameplay, combat, and building mechanics

---

### 🗺️ Level Editor

**Purpose:** Create and edit game levels

| Tool | Hotkey | Description |
|------|--------|-------------|
| Level Builder | F4 | Main tilemap editor |
| Autotile Editor | F11 | Configure autotiles |
| Navmesh Editor | F12 | Edit navigation mesh |
| Event Editor | F5 | Create map events |

**Use Case:** Building maps, placing tiles, setting up navigation and events

---

### 🎨 Content Creation

**Purpose:** Create assets and content

| Tool | Hotkey | Description |
|------|--------|-------------|
| Asset Browser | F7 | Manage game assets |
| **AI Animator** | **Shift+F7** | **AI-powered sprite animation** |
| Quest Editor | F6 | Create quests and dialogue |

**Use Case:** Managing sprites, creating animations, writing quests

**NEW:** AI Animator is now integrated! Access it via Shift+F7 or the Content Creation workspace.

---

### ⚙️ Settings & Debug

**Purpose:** Configure and debug

| Tool | Hotkey | Description |
|------|--------|-------------|
| Settings | F2 | Game and editor settings |
| Debug Console | F1 | Debug commands and logs |
| Project Manager | F8 | Manage projects |

**Use Case:** Debugging, configuration, project management

---

## AI Context Integration

### How It Works

The workspace system exports the current state to `~/.neonworks/ai_context.json` whenever:
- The workspace changes
- A tool is opened/closed
- The selection changes (entities, tiles, layers)

### AI Context File Format

```json
{
  "workspace": "level_editor",
  "mode": "editor",
  "active_tools": ["level_builder"],
  "visible_uis": ["level_builder"],
  "selected_entities": [],
  "current_layer": 0,
  "selected_tile": 42,
  "project_path": "/home/user/my_game",
  "timestamp": "2025-11-15T12:34:56",
  "metadata": {
    "brush_size": 1,
    "current_tool": "pencil"
  }
}
```

### Why This Matters

The AI assistant can now:
- **Give relevant suggestions** - knows you're in Level Editor vs Play Mode
- **Provide context-aware help** - understands what tools are active
- **Offer better code examples** - knows your current project state
- **Debug more effectively** - sees what entities/tiles are selected

### Example AI Usage

```python
# AI can read the context file
import json
from pathlib import Path

context_file = Path.home() / ".neonworks" / "ai_context.json"
with open(context_file) as f:
    context = json.load(f)

# Now AI knows:
# - User is in "level_editor" workspace
# - Level Builder is active
# - Currently on layer 0
# - Has tile 42 selected
# - Project is at /home/user/my_game

# AI can give better suggestions:
if context["workspace"] == "level_editor":
    # Suggest level editing commands
    print("Try using the Fill tool (F) to paint large areas!")
elif context["workspace"] == "content_creation":
    # Suggest asset creation commands
    print("Use AI Animator (Shift+F7) to create sprite animations!")
```

---

## Usage Guide

### For Users

#### Accessing the Toolbar

The workspace toolbar is **always visible at the top** of the screen.

```
┌──────────────────────────────────────────────────────────────┐
│ 🎮 PLAY  |  🗺️ LEVEL EDITOR  |  🎨 CONTENT  |  ⚙️ SETTINGS   │ ← Click to switch workspace
├──────────────────────────────────────────────────────────────┤
│ [🗺️ Level Builder] [🧩 Autotile] [🧭 Navmesh] [⚡ Events]    │ ← Click to open tool
└──────────────────────────────────────────────────────────────┘
```

#### Switching Workspaces

1. **Click a workspace tab** at the top
2. The toolbar shows tools for that workspace
3. AI context updates automatically

#### Opening Tools

1. **Click a tool button** in the toolbar
2. Or use the **F-key shortcut** shown on the button
3. Tool opens and becomes active

#### Collapsing the Toolbar

- Click the **▲/▼ button** in the top-right corner
- Toolbar collapses to just show workspace tabs
- Click again to expand

### For Developers

#### Initialization

The workspace system is automatically initialized in `MasterUIManager`:

```python
# ui/master_ui_manager.py
from .workspace_system import get_workspace_manager
from .workspace_toolbar import WorkspaceToolbar

class MasterUIManager:
    def __init__(self, screen, world, ...):
        # Workspace system
        self.workspace_manager = get_workspace_manager()
        self.workspace_toolbar = WorkspaceToolbar(screen, master_ui_manager=self)
```

#### Adding a New Tool

1. **Add to workspace definition** in `workspace_system.py`:

```python
def _initialize_workspaces(self):
    # ...
    content_workspace.add_tool(
        ToolDefinition(
            id="my_new_tool",
            name="My New Tool",
            description="Description of what it does",
            icon="🔧",
            hotkey="F13",
            toggle_method="toggle_my_new_tool",
        )
    )
```

2. **Add to MasterUIManager**:

```python
# ui/master_ui_manager.py
def __init__(self, ...):
    self.my_new_tool = MyNewToolUI(screen, world)

def toggle_my_new_tool(self):
    self.my_new_tool.toggle()

def render(self, ...):
    if self.my_new_tool.visible:
        self.my_new_tool.render()
```

3. **Update workspace_toolbar.py** UI mapping:

```python
def _is_tool_active(self, tool: ToolDefinition) -> bool:
    ui_map = {
        # ... existing mappings ...
        "my_new_tool": "my_new_tool",
    }
    # ...
```

Done! Your tool is now accessible through the visual toolbar.

---

## Developer Guide

### Creating a New Workspace

If you need to add a 5th workspace (e.g., "Testing & QA"):

1. **Add enum** in `workspace_system.py`:

```python
class WorkspaceType(Enum):
    # ... existing ...
    TESTING_QA = "testing_qa"
```

2. **Initialize workspace** in `_initialize_workspaces()`:

```python
testing_workspace = Workspace(
    type=WorkspaceType.TESTING_QA,
    name="Testing & QA",
    description="Test and validate your game",
    icon="🧪",
)
# Add tools...
self.workspaces[WorkspaceType.TESTING_QA] = testing_workspace
```

3. **Update `get_all_workspaces()`**:

```python
def get_all_workspaces(self) -> List[Workspace]:
    return [
        # ... existing ...
        self.workspaces[WorkspaceType.TESTING_QA],
    ]
```

### Updating AI Context

You can manually update the AI context from anywhere:

```python
from ui.workspace_system import get_workspace_manager

manager = get_workspace_manager()

# Update context with current state
manager.update_context(
    active_tools=["level_builder"],
    selected_entities=[1, 2, 3],
    current_layer=2,
    metadata={
        "brush_size": 3,
        "selected_tileset": "forest"
    }
)

# Context is automatically exported to ~/.neonworks/ai_context.json
```

### Reading AI Context

From Python code:

```python
from ui.workspace_system import get_workspace_manager

manager = get_workspace_manager()
context = manager.load_context()

if context:
    print(f"Current workspace: {context.workspace}")
    print(f"Active tools: {context.active_tools}")
```

From AI assistant:

```python
import json
from pathlib import Path

context_file = Path.home() / ".neonworks" / "ai_context.json"
with open(context_file) as f:
    context = json.load(f)

print(f"User is in: {context['workspace']}")
print(f"Tools active: {context['active_tools']}")
```

---

## API Reference

### WorkspaceManager

**Singleton** - Use `get_workspace_manager()` to access

#### Methods

```python
set_workspace(workspace_type: WorkspaceType)
    """Switch to a different workspace"""

get_current_workspace() -> Optional[Workspace]
    """Get the currently active workspace"""

get_workspace(workspace_type: WorkspaceType) -> Optional[Workspace]
    """Get workspace by type"""

get_all_workspaces() -> List[Workspace]
    """Get all workspaces in order"""

update_context(
    active_tools: Optional[List[str]] = None,
    visible_uis: Optional[List[str]] = None,
    selected_entities: Optional[List[int]] = None,
    current_layer: Optional[int] = None,
    selected_tile: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None
)
    """Update AI context and export to file"""

export_context()
    """Export current context to ~/.neonworks/ai_context.json"""

load_context() -> Optional[WorkspaceContext]
    """Load context from file"""

find_tool(tool_id: str) -> Optional[tuple[WorkspaceType, ToolDefinition]]
    """Find a tool by ID across all workspaces"""
```

### WorkspaceToolbar

**Visual UI Component**

#### Methods

```python
toggle_collapse()
    """Toggle collapsed state"""

get_height() -> int
    """Get current toolbar height"""

render()
    """Render the toolbar"""

handle_event(event: pygame.event.Event) -> bool
    """Handle input events. Returns True if handled"""
```

### ToolDefinition

**Dataclass** - Defines a tool in a workspace

```python
@dataclass
class ToolDefinition:
    id: str                      # Unique identifier
    name: str                    # Display name
    description: str             # User-friendly description
    icon: str                    # Emoji or icon
    hotkey: Optional[str]        # Keyboard shortcut
    toggle_method: Optional[str] # Method name on MasterUIManager
```

### WorkspaceContext

**Dataclass** - AI context state

```python
@dataclass
class WorkspaceContext:
    workspace: str                     # Current workspace ID
    mode: str                          # 'game', 'editor', or 'menu'
    active_tools: List[str]            # Active tool IDs
    visible_uis: List[str]             # Visible UI names
    selected_entities: List[int]       # Selected entity IDs
    current_layer: int                 # Current editing layer
    selected_tile: Optional[int]       # Selected tile ID
    project_path: Optional[str]        # Project directory
    timestamp: str                     # ISO 8601 timestamp
    metadata: Dict[str, Any]           # Additional data
```

---

## Best Practices

### For Tool Developers

1. **Always provide a toggle method** in MasterUIManager
2. **Use descriptive IDs** - e.g., "level_builder" not "lb"
3. **Pick appropriate icons** - use emojis that clearly represent the tool
4. **Update AI context** when your tool's state changes significantly
5. **Test with toolbar collapsed** - make sure your UI still works

### For AI Integration

1. **Read context before suggesting edits** - know what workspace the user is in
2. **Update context when making changes** - keep AI state in sync
3. **Use metadata for tool-specific state** - don't pollute top-level fields
4. **Handle missing context gracefully** - file may not exist yet

### For Users

1. **Use the toolbar for discovery** - hover to see descriptions
2. **Learn shortcuts for frequent tools** - shown on each button
3. **Collapse toolbar when working** - gives more screen space
4. **Switch workspaces for context** - helps organize your workflow

---

## Troubleshooting

### Toolbar not visible

```python
# Check if toolbar is enabled
master_ui_manager.workspace_toolbar.visible = True
```

### Tool not showing in toolbar

1. Check if tool is added to workspace definition
2. Verify `toggle_method` matches method in MasterUIManager
3. Check `_is_tool_active()` includes your tool's UI mapping

### AI context not updating

1. Check file permissions on `~/.neonworks/ai_context.json`
2. Verify `export_context()` is being called
3. Check for exceptions in console

### Hotkey conflicts

1. Use Shift/Ctrl modifiers for new tools
2. Document all hotkeys in this file
3. Update `get_keybind_help()` in MasterUIManager

---

## Future Enhancements

Potential improvements for future versions:

- [ ] **Customizable workspaces** - let users create their own
- [ ] **Tool favorites** - pin frequently used tools
- [ ] **Search/command palette** - Ctrl+P to search tools
- [ ] **Workspace presets** - save/load workspace layouts
- [ ] **Multi-monitor support** - dock toolbars on secondary displays
- [ ] **Touch/tablet support** - larger touch targets
- [ ] **Themes** - dark/light toolbar themes
- [ ] **Analytics** - track most-used tools for optimization

---

## Changelog

### Version 1.0 (2025-11-15)

- ✅ Initial workspace system implementation
- ✅ 4 default workspaces (Play, Level Editor, Content, Settings)
- ✅ Visual toolbar with 12 tools + AI Animator (13 total)
- ✅ AI context export to `~/.neonworks/ai_context.json`
- ✅ Full integration with MasterUIManager
- ✅ Collapse/expand functionality
- ✅ Hotkey hints on toolbar buttons
- ✅ Active tool visual feedback

---

## Credits

**Design Inspiration:**
- Godot Engine (workspace tabs)
- Unity Editor (menu bar + toolbar)
- Unreal Engine (multi-workspace layout)

**Implementation:** NeonWorks Team
**Documentation:** Claude Code Assistant

---

**Questions or issues?** Check CLAUDE.md or open an issue on GitHub.
