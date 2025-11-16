# NeonWorks Launcher

A standalone visual launcher application for managing NeonWorks game projects.

## Overview

The NeonWorks Launcher provides a user-friendly, graphical interface for managing your game projects - similar to Unity Hub or Godot's project manager. No more command-line operations required!

## Features

### Project Browser
- **Visual project cards** with project information
- **Project metadata** display (name, version, description, last modified)
- **Template information** showing which template was used
- **Double-click to open** projects instantly
- **Recent projects tracking** for quick access

### New Project Creation
- **Visual template selection** with descriptions
- **Project name input** with validation
- **4 built-in templates**:
  - **Basic Game** - Minimal template with player movement
  - **Turn-Based RPG** - Combat system and character progression
  - **Base Builder** - Building system and resource management
  - **JRPG Demo** - Complete JRPG with battle system, magic, and exploration

### Project Management
- **Refresh projects** to scan for new projects
- **Launch projects** directly into the editor
- **Automatic project tracking** - recently opened projects are remembered

## How to Use

### Starting the Launcher

```bash
# From the neonworks directory
python launcher.py
```

The launcher window will open with your project browser.

### Creating a New Project

1. **Click "New Project"** button (or press `Ctrl+N`)
2. **Enter a project name** (letters, numbers, hyphens, underscores only)
3. **Select a template** by clicking on one of the template cards
4. **Click "Create Project"**

Your project will be created in the `projects/` directory with all necessary files and structure.

### Opening a Project

**Method 1: Double-click**
- Double-click any project card to launch it immediately

**Method 2: Select and Open**
1. Click once to select a project (card will highlight in blue)
2. Click the "Open Project" button

### Keyboard Shortcuts

- `Ctrl+N` - Create new project
- `Esc` - Go back / Exit launcher
- `Enter` - Confirm text input

## What Happens When You Launch a Project?

When you open a project, the launcher:
1. Adds the project to your recent projects list
2. Launches the project using `main.py`
3. Opens the full NeonWorks editor with all F-key tools available

The launcher remains open so you can quickly switch between projects.

## Project Templates

### Basic Game
Perfect for starting from scratch. Includes:
- Basic window setup
- Player entity with movement
- Minimal rendering system
- No game-specific features enabled

### Turn-Based RPG
For tactical games. Includes:
- Turn-based combat system
- Character stats and progression
- Combat UI
- Menu system

### Base Builder
For construction/management games. Includes:
- Building placement system
- Resource management
- Survival mechanics (hunger, thirst, energy)
- Larger grid size for building

### JRPG Demo
Complete JRPG framework. Includes:
- Turn-based JRPG battle system
- Magic/spell system
- Random encounters
- Exploration system
- Battle transitions
- Party management

## Recent Projects

The launcher automatically tracks your recently opened projects and stores them in `.recent_projects.json`. The 10 most recent projects are remembered.

## Troubleshooting

### "No projects found"
- Make sure you're running from the correct directory
- Check that `projects/` directory exists
- Try clicking "Refresh Projects"

### Project won't launch
- Verify the project's `project.json` file is valid
- Check console output for error messages
- Make sure pygame is installed (`pip install pygame`)

### Can't create project with certain name
- Project names must contain only letters, numbers, hyphens, and underscores
- Project name cannot be empty
- A project with that name may already exist

## UI Guide

### Main View
```
┌─────────────────────────────────────────────┐
│              NeonWorks                      │
│       2D Game Engine - Project Launcher     │
├─────────────────────────────────────────────┤
│  [New Project] [Open Project] [Refresh]    │
├─────────────────────────────────────────────┤
│  Your Projects                              │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ My Awesome Game          v0.1.0     │   │
│  │ A Turn-Based RPG project            │   │
│  │ Modified: 2025-11-15 10:30         │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ Space Adventure         v1.0.0      │   │
│  │ A JRPG Demo project                 │   │
│  │ Modified: 2025-11-14 15:20         │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

### New Project View
```
┌─────────────────────────────────────────────┐
│         Create New Project                  │
├─────────────────────────────────────────────┤
│                                             │
│  Project Name:                              │
│  [________________________]                 │
│                                             │
│  Select Template:                           │
│  ┌──────────────┐  ┌──────────────┐        │
│  │ Basic Game   │  │ Turn-Based   │        │
│  │ Minimal...   │  │ RPG Combat...│        │
│  └──────────────┘  └──────────────┘        │
│  ┌──────────────┐  ┌──────────────┐        │
│  │ Base Builder │  │ JRPG Demo    │        │
│  │ Building...  │  │ Complete...  │        │
│  └──────────────┘  └──────────────┘        │
│                                             │
│  [Create Project]        [Cancel]           │
└─────────────────────────────────────────────┘
```

## Integration with NeonWorks

The launcher integrates seamlessly with the rest of NeonWorks:

- **Projects** created in the launcher work with the CLI (`python cli.py run <project>`)
- **Projects** created via CLI appear in the launcher
- **All project data** is stored in standard `project.json` format
- **Launches** into the full editor with all F-key tools (F1-F12)

## Future Enhancements

Planned features for future versions:
- Project thumbnails/screenshots
- Project deletion from UI
- Project settings editor
- Project export/import
- Search and filter projects
- Project templates customization
- Project duplication
- Asset browser preview
- Recent files within projects

---

**Version:** 1.0.0
**Last Updated:** 2025-11-15
**Author:** NeonWorks Team
