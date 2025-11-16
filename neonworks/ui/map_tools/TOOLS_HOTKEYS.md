# Map Tools Hotkey Reference

Complete reference for all map editing tool hotkeys in the NeonWorks Level Builder.

## Tool Hotkey Assignments

| Key | Tool | Description | File |
|-----|------|-------------|------|
| **1** | Pencil | Paint tiles, entities, events | `pencil_tool.py` |
| **2** | Eraser | Erase tiles, entities, events | `eraser_tool.py` |
| **3** | Fill | Flood fill with 4-way/8-way modes | `fill_tool.py` |
| **4** | Select | Rectangle & magic wand selection | `select_tool.py` |
| **5** | Shape | Draw rectangles, circles, lines | `shape_tool.py` |
| **6** | Stamp | Paint with custom brush patterns | `stamp_tool.py` |
| **7** | Eyedropper | Pick tiles from map | `eyedropper_tool.py` |
| **8** | Autotile | Smart tile matching | `autotile_tool.py` |
| **9** | AI Gen | AI-powered level generation | `ai_generator_tool.py` |
| **0** | Autotile Fill | Flood fill with autotiles | `autotile_tool.py` |

## Keyboard Shortcuts

### Global Shortcuts
- **Ctrl+Z**: Undo last action
- **Ctrl+Y** or **Ctrl+Shift+Z**: Redo last undone action
- **Ctrl+C**: Copy selection (Select tool only)
- **Ctrl+X**: Cut selection (Select tool only)
- **Ctrl+V**: Paste selection (Select tool only)
- **C**: Toggle AI chat (when AI Gen tool active)

### Tool-Specific Shortcuts

#### Fill Tool (3)
- **Right Click**: Toggle 4-way/8-way connectivity mode

#### Select Tool (4)
- **Left Click + Drag**: Rectangle selection
- **Right Click**: Magic wand selection (contiguous tiles)

#### Shape Tool (5)
- **1**: Switch to Rectangle mode
- **2**: Switch to Circle mode
- **3**: Switch to Line mode
- **F**: Toggle fill mode (outline/filled)

#### Stamp Tool (6)
- **1-9**: Switch between stamp presets
- **R**: Rotate stamp 90° clockwise
- **H**: Flip horizontally
- **V**: Flip vertically

#### Eyedropper Tool (7)
- **Left Click**: Pick tile from current layer
- **Right Click**: Pick tile from any layer

## Quick Reference

### Basic Editing Workflow
1. Press **1** for Pencil tool
2. Select a tile from palette
3. Click or drag to paint
4. Press **Ctrl+Z** to undo mistakes

### Advanced Workflow
1. Press **9** for AI Gen tool
2. Chat: "Create an RPG town"
3. AI generates complete level
4. Press **5** for Shape tool to add custom elements
5. Press **6** for Stamp tool to add patterns
6. Press **7** to pick existing tiles
7. Press **Ctrl+Z** / **Ctrl+Y** to undo/redo

### Selection & Editing
1. Press **4** for Select tool
2. **Left click + drag** for rectangle selection
3. **Right click** for magic wand selection
4. **Ctrl+C** to copy
5. **Ctrl+V** to paste
6. Switch to another tool to edit

### Terrain Filling
1. Press **3** for Fill tool
2. **Right click** to toggle 4-way/8-way mode
3. **Left click** on area to fill
4. **Ctrl+Z** to undo if needed

## Tool Registration Order

Tools are registered in `level_builder_ui.py`:

```python
# Basic tools (1-4)
self.tool_manager.register_tool("pencil", PencilTool())        # Hotkey 1
self.tool_manager.register_tool("eraser", EraserTool())        # Hotkey 2
self.tool_manager.register_tool("fill", FillTool())            # Hotkey 3
self.tool_manager.register_tool("select", SelectTool())        # Hotkey 4

# Advanced tools (5-7)
self.tool_manager.register_tool("shape", ShapeTool())          # Hotkey 5
self.tool_manager.register_tool("stamp", StampTool())          # Hotkey 6
self.tool_manager.register_tool("eyedropper", EyedropperTool()) # Hotkey 7

# Special tools (8-0)
self.tool_manager.register_tool("autotile", self.autotile_tool)     # Hotkey 8
self.tool_manager.register_tool("ai_gen", AIGeneratorTool())        # Hotkey 9
self.tool_manager.register_tool("autotile_fill", self.autotile_fill_tool) # Hotkey 0
```

## Conflict Resolution History

### Version 1.0 (2025-11-15)
- **Initial Assignment**: All basic tools (1-4) assigned correctly
- **Conflict 1**: AI Gen and Shape both used hotkey 5
  - **Resolution**: Moved AI Gen from 5 → 9
- **Conflict 2**: Stamp and Autotile both used hotkey 6
  - **Resolution**: Moved Autotile from 6 → 8
- **Conflict 3**: Eyedropper and AutotileFill both used hotkey 7
  - **Resolution**: Moved AutotileFill from 7 → 0

### Final Assignment
All 10 tools now have unique hotkeys (0-9) with no conflicts.

## Notes

- Number keys 0-9 are all assigned
- Additional tools would need letter keys or modifier combinations
- F-keys (F1-F12) are reserved for UI panel toggles
- Tool hotkeys are global within the Level Builder
- Hotkeys only work when Level Builder is visible

## See Also

- [README.md](README.md) - Complete tool documentation
- [level_builder_ui.py](../level_builder_ui.py) - Tool registration
- [base.py](base.py) - MapTool base class
