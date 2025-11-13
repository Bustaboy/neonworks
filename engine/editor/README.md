# NeonWorks Editor Tools

This directory contains AI-powered editor tools for the NeonWorks game engine.

## Overview

The editor tools provide automated assistance for game development tasks such as level design, content creation, and navigation mesh generation.

## Available Tools

### 1. AI Level Builder (`ai_level_builder.py`)

Automatically generates game levels using AI techniques.

**Features:**
- Procedural level generation
- Template-based level creation
- Constraint-based design
- Multiple generation algorithms

**Use Cases:**
- Quickly prototype level layouts
- Generate placeholder levels for testing
- Create variations of existing levels
- Accelerate level design workflow

**Example Usage:**
```python
from engine.editor.ai_level_builder import AILevelBuilder

builder = AILevelBuilder()
level = builder.generate_level(
    width=50,
    height=50,
    theme="dungeon",
    difficulty=5
)
```

### 2. AI Navigation Mesh Generator (`ai_navmesh.py`)

Automatically generates navigation meshes for pathfinding.

**Features:**
- Automatic walkable area detection
- Obstacle avoidance setup
- Navigation graph generation
- Integration with pathfinding system

**Use Cases:**
- Generate nav meshes from level geometry
- Update pathfinding data when levels change
- Optimize AI movement paths
- Debug pathfinding issues

**Example Usage:**
```python
from engine.editor.ai_navmesh import AINavMeshGenerator

generator = AINavMeshGenerator()
navmesh = generator.generate_from_tilemap(tilemap, walkable_tiles)
```

### 3. AI Writer (`ai_writer.py`)

AI-assisted content generation for game writing.

**Features:**
- Dialogue generation
- Quest description writing
- Character backstory creation
- Item descriptions

**Use Cases:**
- Generate placeholder text during development
- Create variation in dialogue
- Brainstorm quest ideas
- Fill in item descriptions

**Example Usage:**
```python
from engine.editor.ai_writer import AIWriter

writer = AIWriter()
dialogue = writer.generate_dialogue(
    character="Merchant",
    tone="friendly",
    context="greeting_player"
)
```

### 4. Procedural Generation (`procedural_gen.py`)

General-purpose procedural content generation.

**Features:**
- Random map generation
- Dungeon generation algorithms
- Room and corridor placement
- Terrain generation
- Feature placement (chests, enemies, etc.)

**Use Cases:**
- Create roguelike dungeons
- Generate exploration maps
- Create varied terrain
- Populate levels with content

**Example Usage:**
```python
from engine.editor.procedural_gen import ProceduralGenerator

gen = ProceduralGenerator()
dungeon = gen.generate_dungeon(
    size=(40, 40),
    room_count=8,
    difficulty=3
)
```

## Integration with Projects

### Using Editor Tools in Your Game

1. **Import the tools** in your project scripts:
```python
from engine.editor.procedural_gen import ProceduralGenerator
```

2. **Generate content** at runtime or during development:
```python
# Runtime generation
level = generator.generate_level()

# Save for later use
with open("levels/generated_level.json", "w") as f:
    json.dump(level.to_dict(), f)
```

3. **Customize generation** with your own parameters:
```python
custom_params = {
    "theme": "forest",
    "enemy_density": 0.3,
    "treasure_chance": 0.1
}
level = generator.generate_level(**custom_params)
```

## Development Workflow

### Level Design Workflow

1. **Generate Base Layout**
   ```python
   level = ai_level_builder.generate_layout(50, 50)
   ```

2. **Generate Navigation Mesh**
   ```python
   navmesh = ai_navmesh.generate_from_level(level)
   ```

3. **Add Procedural Content**
   ```python
   procedural_gen.populate_level(level, enemy_count=10)
   ```

4. **Manual Refinement**
   - Load generated level in your editor
   - Tweak specific areas
   - Add custom elements

5. **Save Final Level**
   ```python
   level.save("levels/my_level.json")
   ```

## Configuration

Editor tools can be configured through project settings:

```json
{
  "editor": {
    "level_builder": {
      "default_width": 50,
      "default_height": 50,
      "default_theme": "dungeon"
    },
    "procedural_gen": {
      "seed": null,
      "deterministic": false
    }
  }
}
```

## Tool Comparison

| Tool | Purpose | Output | Speed | Customization |
|------|---------|--------|-------|---------------|
| AI Level Builder | Complete levels | Full level data | Medium | High |
| AI NavMesh | Navigation data | Navigation mesh | Fast | Medium |
| AI Writer | Text content | Strings/dialogue | Fast | Medium |
| Procedural Gen | Random content | Maps/dungeons | Fast | High |

## Best Practices

### When to Use Each Tool

**AI Level Builder:**
- Need complete, playable levels quickly
- Want coherent level design
- Building template-based content

**AI NavMesh:**
- After creating/modifying level geometry
- When pathfinding isn't working correctly
- Optimizing AI movement

**AI Writer:**
- Need placeholder text
- Generating variations
- Brainstorming content ideas

**Procedural Gen:**
- Creating roguelike content
- Need infinite variety
- Rapid prototyping

### Performance Considerations

- **Generation Time**: Run expensive generation during development or loading screens
- **Caching**: Cache generated content when possible
- **Incremental Updates**: Regenerate only changed sections
- **Quality vs Speed**: Balance generation quality with performance needs

### Version Control

- **Save Generated Content**: Commit generated levels to version control
- **Track Seeds**: Save random seeds for reproducible generation
- **Separate Tools**: Keep editor tools separate from runtime code

## Extending the Tools

### Creating Custom Generators

```python
from engine.editor.procedural_gen import ProceduralGenerator

class MyCustomGenerator(ProceduralGenerator):
    def generate_custom_level(self, params):
        # Your custom generation logic
        pass
```

### Adding New Features

1. Create a new tool file in `/engine/editor/`
2. Implement generation logic
3. Add documentation to this README
4. Create example usage in `/examples/`

## Troubleshooting

### Common Issues

**Generation is too slow:**
- Reduce level size
- Simplify generation parameters
- Use caching

**Generated content is not suitable:**
- Adjust generation parameters
- Try different algorithms
- Post-process the output

**Navigation mesh has gaps:**
- Check walkable tile definitions
- Verify level geometry
- Adjust navmesh parameters

## Future Development

Planned improvements for editor tools:

- [ ] Visual level editor UI
- [ ] Real-time preview
- [ ] Undo/redo support
- [ ] Collaborative editing
- [ ] Asset validation tools
- [ ] Performance profiling
- [ ] Integration with version control

## API Reference

For detailed API documentation, see the docstrings in each module:

- `ai_level_builder.py` - Level generation functions
- `ai_navmesh.py` - Navigation mesh generation
- `ai_writer.py` - Content writing assistance
- `procedural_gen.py` - Procedural content generation

## Examples

See `/engine/examples/` for complete examples using these tools.

## Support

For issues or questions about editor tools:
- Check the documentation
- Review example code
- Report bugs on GitHub
- Ask in community forums

---

**Note**: The editor tools are designed to assist development, not replace human creativity. Use them as starting points and customize the output to fit your game's needs.
