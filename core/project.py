"""
Project System

Manages game projects with their own assets, scripts, and configuration.
This allows the engine to be completely reusable for different games.
"""

import json
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class ProjectMetadata:
    """Project metadata"""
    name: str
    version: str
    description: str
    author: str
    engine_version: str = "0.1.0"
    created_date: str = ""
    modified_date: str = ""


@dataclass
class ProjectPaths:
    """Project directory paths"""
    assets: str = "assets"
    levels: str = "levels"
    scripts: str = "scripts"
    saves: str = "saves"
    config: str = "config"


@dataclass
class ProjectSettings:
    """Project-specific settings"""
    # Display
    window_title: str = "Game"
    window_width: int = 1280
    window_height: int = 720
    fullscreen: bool = False

    # Gameplay
    tile_size: int = 32
    grid_width: int = 100
    grid_height: int = 100

    # Starting scene
    initial_scene: str = "menu"
    initial_level: str = ""

    # Features
    enable_base_building: bool = False
    enable_survival: bool = False
    enable_turn_based: bool = False
    enable_combat: bool = False

    # Custom game data files
    building_definitions: str = ""
    item_definitions: str = ""
    character_definitions: str = ""
    quest_definitions: str = ""

    # Export settings
    export_version: str = "1.0.0"
    export_publisher: str = "Independent Developer"
    export_description: str = ""
    export_icon: str = ""  # Path relative to project
    export_license: str = ""  # Path relative to project
    export_readme: str = ""  # Path relative to project
    export_encrypt: bool = False
    export_compress: bool = True
    export_console: bool = False  # Show console window in exported builds


@dataclass
class ProjectConfig:
    """Complete project configuration"""
    metadata: ProjectMetadata
    paths: ProjectPaths = field(default_factory=ProjectPaths)
    settings: ProjectSettings = field(default_factory=ProjectSettings)
    custom_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "metadata": asdict(self.metadata),
            "paths": asdict(self.paths),
            "settings": asdict(self.settings),
            "custom_data": self.custom_data
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectConfig':
        """Create from dictionary"""
        return cls(
            metadata=ProjectMetadata(**data.get("metadata", {})),
            paths=ProjectPaths(**data.get("paths", {})),
            settings=ProjectSettings(**data.get("settings", {})),
            custom_data=data.get("custom_data", {})
        )


class Project:
    """Represents a game project"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.config: Optional[ProjectConfig] = None
        self._loaded = False

        # Absolute paths
        self.root_dir: Optional[Path] = None
        self.assets_dir: Optional[Path] = None
        self.levels_dir: Optional[Path] = None
        self.scripts_dir: Optional[Path] = None
        self.saves_dir: Optional[Path] = None
        self.config_dir: Optional[Path] = None

    def load(self) -> bool:
        """Load the project"""
        config_file = self.project_path / "project.json"

        if not config_file.exists():
            print(f"❌ Error: Project file not found!")
            print(f"   Expected location: {config_file}")
            print(f"\n💡 Troubleshooting:")
            print(f"   1. Verify the project directory exists: {self.project_path}")
            print(f"   2. Ensure project.json is in the project root")
            print(f"   3. Create a new project with: neonworks create <project_name>")
            return False

        try:
            with open(config_file, 'r') as f:
                data = json.load(f)

        except json.JSONDecodeError as e:
            print(f"❌ Error: Invalid JSON in project.json!")
            print(f"   {e}")
            print(f"\n💡 Fix:")
            print(f"   1. Check for syntax errors in {config_file}")
            print(f"   2. Validate JSON at jsonlint.com")
            print(f"   3. Run: neonworks validate <project_name>")
            return False
        except Exception as e:
            print(f"❌ Error: Could not read project.json!")
            print(f"   {e}")
            print(f"\n💡 Check:")
            print(f"   • File permissions")
            print(f"   • File is not corrupted")
            return False

        # Validate configuration
        try:
            from engine.core.validation import validate_project_config

            errors = validate_project_config(data)
            if errors:
                print(f"❌ Error: Invalid project configuration!")
                print(f"\n📋 Validation errors:")
                for i, error in enumerate(errors, 1):
                    print(f"   {i}. {error}")
                print(f"\n💡 Fix these errors and try again.")
                print(f"   See docs/project_configuration.md for help.")
                return False

        except ImportError:
            # Validation module not available, skip validation
            pass

        try:
            self.config = ProjectConfig.from_dict(data)
            self.root_dir = self.project_path

            # Set up directory paths
            self.assets_dir = self.root_dir / self.config.paths.assets
            self.levels_dir = self.root_dir / self.config.paths.levels
            self.scripts_dir = self.root_dir / self.config.paths.scripts
            self.saves_dir = self.root_dir / self.config.paths.saves
            self.config_dir = self.root_dir / self.config.paths.config

            # Create directories if they don't exist
            self._ensure_directories()

            self._loaded = True
            print(f"✅ Loaded project: {self.config.metadata.name} v{self.config.metadata.version}")
            return True

        except KeyError as e:
            print(f"❌ Error: Missing required field in project.json!")
            print(f"   Missing: {e}")
            print(f"\n💡 Required sections:")
            print(f"   • metadata (name, version, description, author)")
            print(f"   • paths (assets, levels, scripts, saves, config)")
            print(f"   • settings (window_width, window_height, etc.)")
            print(f"\n   See docs/project_configuration.md for complete structure.")
            return False
        except TypeError as e:
            print(f"❌ Error: Invalid data type in project.json!")
            print(f"   {e}")
            print(f"\n💡 Check that all values have the correct type:")
            print(f"   • Strings should be in quotes")
            print(f"   • Numbers should not be in quotes")
            print(f"   • Booleans should be true/false (lowercase)")
            return False
        except Exception as e:
            print(f"❌ Error loading project configuration!")
            print(f"   {e}")
            import traceback
            traceback.print_exc()
            return False

    def save(self) -> bool:
        """Save the project configuration"""
        if not self.config:
            return False

        config_file = self.project_path / "project.json"

        try:
            with open(config_file, 'w') as f:
                json.dump(self.config.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving project: {e}")
            return False

    def _ensure_directories(self):
        """Ensure all project directories exist"""
        directories = [
            self.assets_dir,
            self.levels_dir,
            self.scripts_dir,
            self.saves_dir,
            self.config_dir,
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def get_asset_path(self, relative_path: str) -> Path:
        """Get full path to an asset"""
        return self.assets_dir / relative_path

    def get_level_path(self, level_name: str) -> Path:
        """Get full path to a level"""
        return self.levels_dir / f"{level_name}.json"

    def get_save_path(self, save_name: str) -> Path:
        """Get full path to a save file"""
        return self.saves_dir / f"{save_name}.json"

    def get_config_path(self, config_name: str) -> Path:
        """Get full path to a config file"""
        return self.config_dir / f"{config_name}.json"

    def list_levels(self) -> List[str]:
        """List all available levels"""
        if not self.levels_dir.exists():
            return []

        levels = []
        for file in self.levels_dir.glob("*.json"):
            levels.append(file.stem)
        return sorted(levels)

    def list_saves(self) -> List[str]:
        """List all save files"""
        if not self.saves_dir.exists():
            return []

        saves = []
        for file in self.saves_dir.glob("*.json"):
            saves.append(file.stem)
        return sorted(saves)


class ProjectManager:
    """Manages game projects"""

    def __init__(self, projects_root: str = "projects"):
        self.projects_root = Path(projects_root)
        self.current_project: Optional[Project] = None

    def create_project(self, project_name: str, metadata: ProjectMetadata,
                      settings: Optional[ProjectSettings] = None) -> Optional[Project]:
        """Create a new project"""
        # Validate project name
        if not project_name:
            print(f"❌ Error: Project name cannot be empty!")
            return None

        if not project_name.replace("_", "").replace("-", "").isalnum():
            print(f"❌ Error: Invalid project name '{project_name}'!")
            print(f"   Project names should only contain:")
            print(f"   • Letters (a-z, A-Z)")
            print(f"   • Numbers (0-9)")
            print(f"   • Hyphens (-)")
            print(f"   • Underscores (_)")
            return None

        project_dir = self.projects_root / project_name

        if project_dir.exists():
            print(f"❌ Error: Project '{project_name}' already exists!")
            print(f"   Location: {project_dir}")
            print(f"\n💡 Options:")
            print(f"   1. Choose a different project name")
            print(f"   2. Delete the existing project")
            print(f"   3. Load the existing project: neonworks run {project_name}")
            return None

        try:
            # Create project directory
            project_dir.mkdir(parents=True, exist_ok=True)

            # Create config
            config = ProjectConfig(
                metadata=metadata,
                settings=settings or ProjectSettings()
            )

            # Create project
            project = Project(project_dir)
            project.config = config
            project.root_dir = project_dir

            # Set up directory paths before ensuring they exist
            project.assets_dir = project.root_dir / project.config.paths.assets
            project.levels_dir = project.root_dir / project.config.paths.levels
            project.scripts_dir = project.root_dir / project.config.paths.scripts
            project.saves_dir = project.root_dir / project.config.paths.saves
            project.config_dir = project.root_dir / project.config.paths.config

            # Save project file
            if not project.save():
                print(f"❌ Error: Failed to save project configuration!")
                print(f"   Check file permissions for: {project_dir}")
                return None

            # Create directory structure
            project._ensure_directories()

            return project

        except PermissionError:
            print(f"❌ Error: Permission denied creating project!")
            print(f"   Cannot write to: {project_dir}")
            print(f"\n💡 Fix:")
            print(f"   • Check directory permissions")
            print(f"   • Try running with appropriate permissions")
            return None
        except Exception as e:
            print(f"❌ Error creating project!")
            print(f"   {e}")
            import traceback
            traceback.print_exc()
            return None

    def load_project(self, project_name: str) -> Optional[Project]:
        """Load a project by name"""
        if not project_name:
            print(f"❌ Error: Project name cannot be empty!")
            return None

        project_dir = self.projects_root / project_name

        if not project_dir.exists():
            print(f"❌ Error: Project '{project_name}' not found!")
            print(f"   Expected location: {project_dir}")
            print(f"\n💡 Available projects:")

            available = self.list_projects()
            if available:
                for proj in available:
                    print(f"   • {proj}")
            else:
                print(f"   (No projects found)")
                print(f"\n   Create a new project with:")
                print(f"   neonworks create {project_name}")

            return None

        if not project_dir.is_dir():
            print(f"❌ Error: Project path is not a directory!")
            print(f"   Path: {project_dir}")
            return None

        project = Project(project_dir)
        if project.load():
            self.current_project = project
            return project

        print(f"\n💡 Project exists but failed to load.")
        print(f"   Run: neonworks validate {project_name}")
        return None

    def list_projects(self) -> List[str]:
        """List all available projects"""
        if not self.projects_root.exists():
            return []

        projects = []
        for item in self.projects_root.iterdir():
            if item.is_dir() and (item / "project.json").exists():
                projects.append(item.name)
        return sorted(projects)

    def get_current_project(self) -> Optional[Project]:
        """Get the currently loaded project"""
        return self.current_project


# Global project manager instance
_global_project_manager = None


def get_project_manager() -> ProjectManager:
    """Get the global project manager"""
    global _global_project_manager
    if _global_project_manager is None:
        _global_project_manager = ProjectManager()
    return _global_project_manager


def load_project(project_name: str) -> Optional[Project]:
    """Convenience function to load a project"""
    return get_project_manager().load_project(project_name)


def get_current_project() -> Optional[Project]:
    """Convenience function to get current project"""
    return get_project_manager().get_current_project()
