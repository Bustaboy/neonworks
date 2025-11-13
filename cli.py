#!/usr/bin/env python3
"""
NeonWorks CLI Tool

Command-line interface for managing NeonWorks game projects.

Commands:
    create <project_name>   - Create a new project from a template
    run <project_name>      - Run a project
    validate <project_name> - Validate project configuration
    list                    - List all projects
    templates               - List available templates

Usage:
    neonworks create my_game
    neonworks run my_game
    neonworks validate my_game
"""

import sys
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
import shutil

# Add engine to path if running as script
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

# Import only what we need to avoid pygame dependency
# These imports are safe because they don't depend on pygame
import importlib.util


def lazy_import_project_module():
    """Lazily import project module to avoid pygame dependency"""
    spec = importlib.util.spec_from_file_location(
        "engine.core.project", Path(__file__).parent / "core" / "project.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["engine.core.project"] = module
    spec.loader.exec_module(module)
    return module


def lazy_import_validation_module():
    """Lazily import validation module"""
    spec = importlib.util.spec_from_file_location(
        "engine.core.validation", Path(__file__).parent / "core" / "validation.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["engine.core.validation"] = module
    spec.loader.exec_module(module)
    return module


# Delay imports until needed
ProjectManager = None
ProjectMetadata = None
ProjectSettings = None
Project = None
validate_project_config = None
ValidationError = None


# Template configurations
TEMPLATES = {
    "basic_game": {
        "name": "Basic Game",
        "description": "Minimal template with player movement and basic rendering",
        "settings": {
            "window_title": "My Game",
            "window_width": 1280,
            "window_height": 720,
            "tile_size": 32,
            "grid_width": 40,
            "grid_height": 30,
            "initial_scene": "gameplay",
            "enable_base_building": False,
            "enable_survival": False,
            "enable_turn_based": False,
            "enable_combat": False,
        },
    },
    "turn_based_rpg": {
        "name": "Turn-Based RPG",
        "description": "Template with turn-based combat system and character progression",
        "settings": {
            "window_title": "Turn-Based RPG",
            "window_width": 1280,
            "window_height": 720,
            "tile_size": 32,
            "grid_width": 40,
            "grid_height": 30,
            "initial_scene": "menu",
            "enable_base_building": False,
            "enable_survival": False,
            "enable_turn_based": True,
            "enable_combat": True,
        },
    },
    "base_builder": {
        "name": "Base Builder",
        "description": "Template with building system and resource management",
        "settings": {
            "window_title": "Base Builder",
            "window_width": 1600,
            "window_height": 900,
            "tile_size": 32,
            "grid_width": 50,
            "grid_height": 40,
            "initial_scene": "gameplay",
            "enable_base_building": True,
            "enable_survival": True,
            "enable_turn_based": False,
            "enable_combat": False,
            "building_definitions": "config/buildings.json",
            "item_definitions": "config/items.json",
        },
    },
}


class NeonWorksCLI:
    """NeonWorks command-line interface"""

    def __init__(self):
        # Load required modules
        self._load_modules()

        self.engine_root = Path(__file__).parent
        self.projects_root = self.engine_root.parent / "projects"
        self.templates_root = self.engine_root / "templates"
        self.project_manager = self.ProjectManager(str(self.projects_root))

    def _load_modules(self):
        """Load required modules lazily"""
        global ProjectManager, ProjectMetadata, ProjectSettings, Project
        global validate_project_config, ValidationError

        if ProjectManager is None:
            project_module = lazy_import_project_module()
            ProjectManager = project_module.ProjectManager
            ProjectMetadata = project_module.ProjectMetadata
            ProjectSettings = project_module.ProjectSettings
            Project = project_module.Project

            # Store in instance for use
            self.ProjectManager = ProjectManager
            self.ProjectMetadata = ProjectMetadata
            self.ProjectSettings = ProjectSettings
            self.Project = Project

        if validate_project_config is None:
            validation_module = lazy_import_validation_module()
            validate_project_config = validation_module.validate_project_config
            ValidationError = validation_module.ValidationError

            # Store in instance for use
            self.validate_project_config = validate_project_config
            self.ValidationError = ValidationError

    def create_project(
        self,
        project_name: str,
        template: str = "basic_game",
        author: str = "Developer",
        description: str = "",
    ) -> bool:
        """Create a new project from a template"""

        # Validate project name
        if (
            not project_name
            or not project_name.replace("_", "").replace("-", "").isalnum()
        ):
            print("❌ Error: Invalid project name!")
            print(
                "   Project names should contain only letters, numbers, hyphens, and underscores."
            )
            return False

        # Check if project already exists
        project_dir = self.projects_root / project_name
        if project_dir.exists():
            print(f"❌ Error: Project '{project_name}' already exists!")
            print(f"   Location: {project_dir}")
            return False

        # Validate template
        if template not in TEMPLATES:
            print(f"❌ Error: Unknown template '{template}'")
            print(f"\n📦 Available templates:")
            for tmpl_name, tmpl_info in TEMPLATES.items():
                print(f"   • {tmpl_name}: {tmpl_info['description']}")
            return False

        template_info = TEMPLATES[template]

        print(f"🎮 Creating new project: {project_name}")
        print(f"   Template: {template_info['name']}")
        print(f"   Location: {project_dir}")

        try:
            # Create metadata
            metadata = self.ProjectMetadata(
                name=project_name,
                version="0.1.0",
                description=description or f"A {template_info['name']} project",
                author=author,
                engine_version="0.1.0",
                created_date=datetime.now().isoformat(),
                modified_date=datetime.now().isoformat(),
            )

            # Create settings from template
            settings = self.ProjectSettings(**template_info["settings"])
            settings.window_title = project_name.replace("_", " ").title()

            # Create project
            project = self.project_manager.create_project(
                project_name, metadata, settings
            )

            if not project:
                print("❌ Error: Failed to create project")
                return False

            # Copy template files if they exist
            template_dir = self.templates_root / template
            if template_dir.exists():
                print(f"   📋 Copying template files...")
                self._copy_template_files(template_dir, project_dir)
            else:
                print(
                    f"   ⚠️  Warning: Template directory not found, creating minimal structure"
                )
                self._create_minimal_structure(project, template)

            print(f"\n✅ Project created successfully!")
            print(f"\n📚 Next steps:")
            print(f"   1. cd {project_dir}")
            print(f"   2. Edit scripts/main.py to customize your game")
            print(f"   3. Run: neonworks run {project_name}")
            print(f"\n💡 See the template README for more information:")
            print(f"   cat {project_dir}/README.md")

            return True

        except Exception as e:
            print(f"❌ Error creating project: {e}")
            import traceback

            traceback.print_exc()
            return False

    def _copy_template_files(self, template_dir: Path, project_dir: Path):
        """Copy template files to project directory"""
        # Copy all files except project.json (which is already created)
        for item in template_dir.rglob("*"):
            if item.is_file() and item.name != "project.json":
                rel_path = item.relative_to(template_dir)
                dest = project_dir / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest)
                print(f"      ✓ {rel_path}")

    def _create_minimal_structure(self, project: Project, template: str):
        """Create minimal project structure"""
        # Create a basic main script
        scripts_dir = project.scripts_dir
        main_file = scripts_dir / "main.py"

        main_content = f'''"""
Main game script for {project.config.metadata.name}

This is the entry point for your game logic.
"""

import pygame
from engine.core.ecs import World
from engine.core.game_loop import GameEngine


def main():
    """Main game function"""
    print("Starting {project.config.metadata.name}...")

    # Initialize pygame
    pygame.init()

    # Create game engine
    engine = GameEngine()
    world = engine.world

    # TODO: Add your game initialization here
    # - Create entities
    # - Add components
    # - Register systems

    print("Game initialized! Press Ctrl+C to quit.")

    # Start game loop
    try:
        engine.start()
    except KeyboardInterrupt:
        print("\\nGame stopped by user")
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
'''

        main_file.write_text(main_content)

        # Create README
        readme = project.root_dir / "README.md"
        readme_content = f"""# {project.config.metadata.name}

{project.config.metadata.description}

## Template: {TEMPLATES[template]["name"]}

{TEMPLATES[template]["description"]}

## Getting Started

1. Edit `scripts/main.py` to add your game logic
2. Add assets to `assets/` directory
3. Run the game:
   ```bash
   neonworks run {project.config.metadata.name}
   ```

## Project Structure

- `scripts/` - Game scripts and logic
- `assets/` - Images, sounds, and other game assets
- `levels/` - Level data files
- `config/` - Configuration files
- `saves/` - Save game files
- `project.json` - Project configuration

## Documentation

See the NeonWorks documentation for more information:
- docs/getting_started.md
- docs/project_configuration.md
- docs/core_concepts.md

## Features Enabled

"""

        # List enabled features
        settings = project.config.settings
        features = [
            ("Turn-based system", settings.enable_turn_based),
            ("Combat system", settings.enable_combat),
            ("Base building", settings.enable_base_building),
            ("Survival mechanics", settings.enable_survival),
        ]

        for feature, enabled in features:
            status = "✓" if enabled else "✗"
            readme_content += f"- [{status}] {feature}\n"

        readme.write_text(readme_content)

    def run_project(self, project_name: str) -> bool:
        """Run a project"""
        print(f"🚀 Running project: {project_name}")

        # Load project to verify it exists
        project = self.project_manager.load_project(project_name)
        if not project:
            print(f"\n💡 Tip: Create a new project with:")
            print(f"   neonworks create {project_name}")
            return False

        # Run the project using the main engine module
        import subprocess

        engine_main = self.engine_root / "main.py"

        try:
            # Run as subprocess to properly handle pygame
            result = subprocess.run(
                [sys.executable, "-m", "engine.main", project_name],
                cwd=self.engine_root.parent,
                check=False,
            )

            return result.returncode == 0

        except KeyboardInterrupt:
            print("\n👋 Game stopped by user")
            return True
        except Exception as e:
            print(f"❌ Error running project: {e}")
            import traceback

            traceback.print_exc()
            return False

    def validate_project(self, project_name: str) -> bool:
        """Validate a project's configuration"""
        print(f"🔍 Validating project: {project_name}")

        project_dir = self.projects_root / project_name
        config_file = project_dir / "project.json"

        if not config_file.exists():
            print(f"❌ Error: Project configuration not found!")
            print(f"   Expected: {config_file}")
            return False

        try:
            # Load and parse JSON
            with open(config_file, "r") as f:
                config_data = json.load(f)

            print("   ✓ Valid JSON format")

            # Validate structure
            errors = self.validate_project_config(config_data)

            if errors:
                print(f"\n❌ Validation failed with {len(errors)} error(s):")
                for i, error in enumerate(errors, 1):
                    print(f"   {i}. {error}")
                return False

            print("   ✓ Valid project structure")
            print("   ✓ All required fields present")

            # Load as project to check paths
            project = self.Project(project_dir)
            if not project.load():
                print("❌ Error: Failed to load project")
                return False

            print("   ✓ Project loads successfully")

            # Check for common issues
            warnings = []

            # Check for missing directories
            if not project.assets_dir.exists():
                warnings.append(f"Assets directory not found: {project.assets_dir}")

            if not project.scripts_dir.exists():
                warnings.append(f"Scripts directory not found: {project.scripts_dir}")

            # Check for missing initial scene script
            if project.config.settings.initial_scene:
                scene_script = (
                    project.scripts_dir / f"{project.config.settings.initial_scene}.py"
                )
                if (
                    not scene_script.exists()
                    and not (project.scripts_dir / "main.py").exists()
                ):
                    warnings.append(f"Initial scene script not found: {scene_script}")

            if warnings:
                print(f"\n⚠️  {len(warnings)} warning(s):")
                for warning in warnings:
                    print(f"   • {warning}")

            print("\n✅ Project configuration is valid!")
            return True

        except json.JSONDecodeError as e:
            print(f"❌ Error: Invalid JSON format!")
            print(f"   {e}")
            return False
        except self.ValidationError as e:
            print(f"❌ Validation error: {e}")
            return False
        except Exception as e:
            print(f"❌ Error validating project: {e}")
            import traceback

            traceback.print_exc()
            return False

    def list_projects(self) -> bool:
        """List all available projects"""
        projects = self.project_manager.list_projects()

        print("📁 Available projects:")
        print()

        if not projects:
            print("   (No projects found)")
            print()
            print("💡 Create a new project with:")
            print("   neonworks create <project_name>")
            return True

        for project_name in projects:
            project = self.project_manager.load_project(project_name)
            if project:
                print(f"   • {project_name}")
                print(f"     {project.config.metadata.description}")
                print(f"     Version: {project.config.metadata.version}")
                print()

        print(f"Total: {len(projects)} project(s)")
        return True

    def list_templates(self) -> bool:
        """List available project templates"""
        print("📦 Available templates:")
        print()

        for template_name, template_info in TEMPLATES.items():
            print(f"   • {template_name}")
            print(f"     {template_info['description']}")

            # Show key features
            features = []
            settings = template_info["settings"]
            if settings.get("enable_turn_based"):
                features.append("turn-based")
            if settings.get("enable_combat"):
                features.append("combat")
            if settings.get("enable_base_building"):
                features.append("base building")
            if settings.get("enable_survival"):
                features.append("survival")

            if features:
                print(f"     Features: {', '.join(features)}")
            print()

        print("💡 Create a project from a template:")
        print("   neonworks create <project_name> --template <template_name>")
        return True


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="NeonWorks Game Engine - Project Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  neonworks create my_game                        # Create a basic game
  neonworks create my_rpg --template turn_based_rpg  # Create from template
  neonworks run my_game                           # Run a project
  neonworks validate my_game                      # Validate project config
  neonworks list                                  # List all projects
  neonworks templates                             # List templates

For more information, see the documentation at docs/cli_tools.md
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Create command
    create_parser = subparsers.add_parser(
        "create",
        help="Create a new project",
        description="Create a new game project from a template",
    )
    create_parser.add_argument("project_name", help="Name of the project to create")
    create_parser.add_argument(
        "--template",
        "-t",
        default="basic_game",
        choices=list(TEMPLATES.keys()),
        help="Template to use (default: basic_game)",
    )
    create_parser.add_argument(
        "--author", "-a", default="Developer", help="Author name (default: Developer)"
    )
    create_parser.add_argument(
        "--description", "-d", default="", help="Project description"
    )

    # Run command
    run_parser = subparsers.add_parser(
        "run", help="Run a project", description="Run a game project"
    )
    run_parser.add_argument("project_name", help="Name of the project to run")

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate project configuration",
        description="Validate a project's configuration file",
    )
    validate_parser.add_argument("project_name", help="Name of the project to validate")

    # List command
    list_parser = subparsers.add_parser(
        "list", help="List all projects", description="List all available game projects"
    )

    # Templates command
    templates_parser = subparsers.add_parser(
        "templates",
        help="List available templates",
        description="List all available project templates",
    )

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Create CLI instance
    cli = NeonWorksCLI()

    # Execute command
    try:
        if args.command == "create":
            success = cli.create_project(
                args.project_name, args.template, args.author, args.description
            )
        elif args.command == "run":
            success = cli.run_project(args.project_name)
        elif args.command == "validate":
            success = cli.validate_project(args.project_name)
        elif args.command == "list":
            success = cli.list_projects()
        elif args.command == "templates":
            success = cli.list_templates()
        else:
            parser.print_help()
            return 1

        return 0 if success else 1

    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
