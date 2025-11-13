# Neon Collapse Project Template

**⚠️ IMPORTANT: This is a configuration template, not a complete working game.**

This directory provides an example project structure showing how to configure a game using the Neon Works engine. It contains sample configuration files but lacks the actual game implementation (assets, levels, scripts).

## What's Included

This template contains:
- ✅ `project.json` - Example project configuration with metadata and settings
- ✅ `config/buildings.json` - Sample building definitions
- ✅ This README documenting the expected structure

## What's Missing

To create a working game, you would need to add:
- ❌ **Assets**: Sprites, sounds, music, fonts (currently no `assets/` folder)
- ❌ **Levels**: Level definitions and maps (currently no `levels/` folder)
- ❌ **Scripts**: Custom game logic (currently no `scripts/` folder)
- ❌ **Complete Config**: All game data files (only `buildings.json` exists as an example)

## Using This Template

Use this as a reference when creating your own game project:

1. **Copy the structure** to create your own project folder
2. **Customize project.json** with your game's metadata and settings
3. **Add your assets** in an `assets/` folder
4. **Create configuration files** in `config/` (items, characters, quests, etc.)
5. **Build levels** using the engine's level editor or JSON files
6. **Write custom scripts** if needed in `scripts/`

## Expected Project Structure

A complete game project should have this structure:

```
projects/your_game/
├── project.json          # Project configuration (THIS EXISTS)
├── assets/              # Game assets (YOU NEED TO CREATE THIS)
│   ├── sprites/        # Character and object sprites
│   ├── tiles/          # Tile graphics
│   ├── ui/             # UI elements
│   ├── sounds/         # Sound effects
│   └── music/          # Background music
├── levels/             # Level files (YOU NEED TO CREATE THIS)
│   ├── tutorial.json
│   ├── mission_01.json
│   └── ...
├── config/             # Game configuration (PARTIALLY EXISTS)
│   ├── buildings.json  # Building definitions (example included)
│   ├── items.json      # Item definitions (you create)
│   ├── characters.json # Character templates (you create)
│   └── quests.json     # Quest definitions (you create)
├── scripts/            # Custom game scripts (YOU NEED TO CREATE THIS)
├── saves/              # Save game files (auto-generated)
└── README.md           # This file
```

## Configuration Reference

### project.json

The `project.json` file contains:

- **Metadata**: Name, version, author, description
- **Paths**: Where to find assets, levels, config files
- **Settings**: Window size, tile size, grid dimensions, enabled features
- **Custom Data**: Game-specific data like difficulty levels, themes, etc.

See the included `project.json` for a complete example.

### config/buildings.json

Example building definitions showing:
- Construction costs and time
- Resource production/consumption
- Storage capacity
- Upgrade paths

Extend this pattern to create `items.json`, `characters.json`, `quests.json`, etc.

## Creating Your Own Game

1. **Read the Engine Documentation**: See `/engine/README.md` for detailed information
2. **Study this template**: Understand the configuration structure
3. **Create a new project folder**: Copy this structure to `projects/your_game/`
4. **Add your content**: Assets, levels, configuration, scripts
5. **Test iteratively**: Run your game frequently to catch issues early

## Development Workflow

Once you have a complete project:

```bash
# Run your game
python -m engine.main your_game

# Open the level editor
python -m engine.editor your_game

# Run tests
pytest engine/tests/
```

## Benefits of Project-Based Architecture

This separation allows you to:

1. ✅ Version control game content independently from the engine
2. ✅ Share projects with others who have the engine installed
3. ✅ Create multiple games using the same engine
4. ✅ Iterate on game design without touching engine code
5. ✅ Swap between projects easily

## Example: Building a Simple Game

1. **Copy this template**: `cp -r projects/neon_collapse projects/my_game`
2. **Edit project.json**: Update name, description, settings
3. **Add a tileset**: Create `assets/tiles/grass.png`, `water.png`, etc.
4. **Create a level**: Use JSON or the level editor
5. **Test**: `python -m engine.main my_game`

## Need Help?

- **Engine Documentation**: `/engine/README.md`
- **API Reference**: See inline docstrings in engine source code
- **Architecture Docs**: `/ARCHITECTURE_SUMMARY.md`
- **Developer Guide**: `/DEVELOPER_GUIDE.md`

## Credits

- **Template**: Neon Works Engine Team
- **Engine**: Neon Works v0.1.0
