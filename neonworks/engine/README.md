# Engine Subsystems Directory

This directory contains specialized engine subsystems and tools that are part of the NeonWorks engine but organized separately for modularity.

## Directory Structure

```
engine/
├── core/              # Event system components
│   ├── event_data.py        # Event data structures
│   └── event_interpreter.py # Event command interpreter
│
├── data/              # Database management
│   ├── database_manager.py  # Database management system
│   ├── database_schema.py   # Database schema definitions
│   └── character_parts.json # Character generator data
│
├── tools/             # Content creation tools
│   ├── character_generator.py    # Character generation system
│   ├── ai_character_generator.py # AI-powered character gen
│   ├── face_generator.py         # Face sprite generator
│   └── map_importers.py          # Map import utilities
│
├── ui/                # Specialized UI components
│   ├── event_editor_ui.py        # Event editor interface
│   ├── database_editor_ui.py     # Database editor
│   ├── character_generator_ui.py # Character gen UI
│   └── face_generator_ui.py      # Face gen UI
│
└── templates/         # Event templates
    └── events/        # Event command templates
```

## Purpose

This directory is separate from the main engine modules (`/core`, `/rendering`, etc.) because:

1. **Modularity** - These are complete subsystems with their own core, data, tools, and UI
2. **Optional Features** - Projects may not need all these tools
3. **Clear Organization** - Keeps specialized tools separate from core engine functionality
4. **Import Path** - Accessed via `neonworks.engine.*` namespace

## Usage

```python
# Import event system
from neonworks.engine.core.event_interpreter import EventInterpreter
from neonworks.engine.core.event_data import EventCommand

# Import database tools
from neonworks.engine.data.database_manager import DatabaseManager

# Import character generator
from neonworks.engine.tools.character_generator import CharacterGenerator
```

## See Also

- `/core` - Core ECS, game loop, and state management
- `/ui` - Main editor UI components
- `/tools` - Deprecated tool location (being migrated)
