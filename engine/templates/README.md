# NeonWorks Project Templates

This directory contains starter templates for creating games with the NeonWorks engine.

## Available Templates

### 1. Basic Game (`basic_game`)

A minimal template for learning the engine basics.

**Features:**
- Player movement with keyboard controls
- Simple rendering
- Basic ECS architecture
- Delta time-based movement

**Best for:**
- Learning the engine
- Simple arcade games
- Rapid prototyping
- Custom game types

**Get started:**
```bash
neonworks create my_game --template basic_game
```

### 2. Turn-Based RPG (`turn_based_rpg`)

A template for turn-based combat games.

**Features:**
- Turn-based combat system
- Character stats (HP, Attack, Defense, Speed)
- Enemy AI
- Battle states and screens
- Damage calculation
- Battle log

**Best for:**
- Turn-based RPGs
- Tactical games
- Card battle games
- Strategy games with combat

**Get started:**
```bash
neonworks create my_rpg --template turn_based_rpg
```

### 3. Base Builder (`base_builder`)

A template for base building and resource management games.

**Features:**
- Grid-based building placement
- Resource management (wood, stone, food)
- Production and consumption systems
- Camera controls
- Building types with different functions
- Real-time resource updates

**Best for:**
- Base building games
- City builders
- Resource management games
- Survival games
- Tower defense games

**Get started:**
```bash
neonworks create my_base --template base_builder
```

## Using Templates

### Create a New Project

```bash
# Using CLI
neonworks create <project_name> --template <template_name>

# Examples
neonworks create my_game --template basic_game
neonworks create fantasy_rpg --template turn_based_rpg
neonworks create colony_sim --template base_builder
```

### List Available Templates

```bash
neonworks templates
```

### Run Your Project

```bash
neonworks run <project_name>
```

## Template Structure

Each template includes:

- **scripts/main.py** - Main game logic and entry point
- **README.md** - Template-specific documentation and customization ideas
- **config/** - Configuration files (building definitions, etc.)
- Standard project directories (assets, levels, saves, config)

## Customizing Templates

All templates are designed to be customized and extended:

1. **Modify existing code** in `scripts/main.py`
2. **Add new systems** for custom mechanics
3. **Create new components** for entity data
4. **Add assets** in the `assets/` directory
5. **Configure settings** in `project.json`

## Template Features Comparison

| Feature | Basic Game | Turn-Based RPG | Base Builder |
|---------|------------|----------------|--------------|
| Player Movement | ✓ | ✗ | ✗ |
| Real-time Action | ✓ | ✗ | ✓ |
| Turn-based System | ✗ | ✓ | ✗ |
| Combat | ✗ | ✓ | ✗ |
| Building System | ✗ | ✗ | ✓ |
| Resource Management | ✗ | ✗ | ✓ |
| Grid-based | ✗ | ✗ | ✓ |
| Camera Controls | ✗ | ✗ | ✓ |
| Complexity | Low | Medium | Medium-High |

## Combining Features

You can combine features from multiple templates:

1. Start with one template
2. Reference code from other templates
3. Copy components and systems you need
4. Enable features in `project.json`

Example - Adding combat to a base builder:
```json
{
  "settings": {
    "enable_base_building": true,
    "enable_combat": true,
    "enable_turn_based": true
  }
}
```

## Next Steps

After creating a project from a template:

1. **Read the template README** - Each template has specific customization guides
2. **Run the game** - See it in action and understand the code
3. **Experiment** - Make small changes and see what happens
4. **Add features** - Follow the customization ideas in the README
5. **Add assets** - Replace placeholder graphics with your own
6. **Build your game** - Use the template as a foundation

## Documentation

- [Getting Started Guide](../../docs/getting_started.md)
- [Project Configuration](../../docs/project_configuration.md)
- [ECS Architecture](../../docs/core_concepts.md)
- [CLI Tools](../../docs/cli_tools.md)

## Contributing Templates

Want to add your own template?

1. Create a new directory in `engine/templates/`
2. Include `scripts/main.py` and `README.md`
3. Add configuration to `engine/cli.py` TEMPLATES dictionary
4. Document features and customization options
5. Test thoroughly
6. Submit a pull request

## Support

For help with templates:
- Check template README files
- Read the NeonWorks documentation
- Report issues on GitHub
- Ask in community forums

Happy game development!
