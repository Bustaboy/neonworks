"""
Comprehensive tests for project management module

Tests project configuration, project loading/saving, and project management.
"""

import json
import tempfile
from pathlib import Path

import pytest

from neonworks.core.project import (
    Project,
    ProjectConfig,
    ProjectManager,
    ProjectMetadata,
    ProjectPaths,
    ProjectSettings,
    get_current_project,
    get_project_manager,
    load_project,
)


# ===========================
# ProjectMetadata Tests
# ===========================


class TestProjectMetadata:
    """Test ProjectMetadata dataclass"""

    def test_metadata_creation(self):
        """Test creating ProjectMetadata"""
        metadata = ProjectMetadata(
            name="Test Game",
            version="1.0.0",
            description="A test game",
            author="Test Author",
        )

        assert metadata.name == "Test Game"
        assert metadata.version == "1.0.0"
        assert metadata.description == "A test game"
        assert metadata.author == "Test Author"
        assert metadata.engine_version == "0.1.0"  # Default

    def test_metadata_with_custom_engine_version(self):
        """Test creating ProjectMetadata with custom engine version"""
        metadata = ProjectMetadata(
            name="Test",
            version="1.0",
            description="Test",
            author="Test",
            engine_version="0.2.0",
        )

        assert metadata.engine_version == "0.2.0"

    def test_metadata_with_dates(self):
        """Test creating ProjectMetadata with dates"""
        metadata = ProjectMetadata(
            name="Test",
            version="1.0",
            description="Test",
            author="Test",
            created_date="2024-01-01",
            modified_date="2024-01-15",
        )

        assert metadata.created_date == "2024-01-01"
        assert metadata.modified_date == "2024-01-15"


# ===========================
# ProjectPaths Tests
# ===========================


class TestProjectPaths:
    """Test ProjectPaths dataclass"""

    def test_paths_default_values(self):
        """Test ProjectPaths default values"""
        paths = ProjectPaths()

        assert paths.assets == "assets"
        assert paths.levels == "levels"
        assert paths.scripts == "scripts"
        assert paths.saves == "saves"
        assert paths.config == "config"

    def test_paths_custom_values(self):
        """Test ProjectPaths with custom values"""
        paths = ProjectPaths(
            assets="my_assets",
            levels="my_levels",
            scripts="my_scripts",
            saves="my_saves",
            config="my_config",
        )

        assert paths.assets == "my_assets"
        assert paths.levels == "my_levels"
        assert paths.scripts == "my_scripts"
        assert paths.saves == "my_saves"
        assert paths.config == "my_config"


# ===========================
# ProjectSettings Tests
# ===========================


class TestProjectSettings:
    """Test ProjectSettings dataclass"""

    def test_settings_default_values(self):
        """Test ProjectSettings default values"""
        settings = ProjectSettings()

        # Display settings
        assert settings.window_title == "Game"
        assert settings.window_width == 1280
        assert settings.window_height == 720
        assert settings.fullscreen is False

        # Gameplay settings
        assert settings.tile_size == 32
        assert settings.grid_width == 100
        assert settings.grid_height == 100

        # Scene settings
        assert settings.initial_scene == "menu"
        assert settings.initial_level == ""

        # Feature flags
        assert settings.enable_base_building is False
        assert settings.enable_survival is False
        assert settings.enable_turn_based is False
        assert settings.enable_combat is False

    def test_settings_custom_values(self):
        """Test ProjectSettings with custom values"""
        settings = ProjectSettings(
            window_title="My Game",
            window_width=1920,
            window_height=1080,
            fullscreen=True,
            tile_size=64,
            enable_combat=True,
        )

        assert settings.window_title == "My Game"
        assert settings.window_width == 1920
        assert settings.window_height == 1080
        assert settings.fullscreen is True
        assert settings.tile_size == 64
        assert settings.enable_combat is True

    def test_settings_export_defaults(self):
        """Test ProjectSettings export defaults"""
        settings = ProjectSettings()

        assert settings.export_version == "1.0.0"
        assert settings.export_publisher == "Independent Developer"
        assert settings.export_description == ""
        assert settings.export_encrypt is False
        assert settings.export_compress is True
        assert settings.export_console is False


# ===========================
# ProjectConfig Tests
# ===========================


class TestProjectConfig:
    """Test ProjectConfig dataclass"""

    def test_config_creation(self):
        """Test creating ProjectConfig"""
        metadata = ProjectMetadata(
            name="Test", version="1.0", description="Test", author="Test"
        )
        paths = ProjectPaths()
        settings = ProjectSettings()

        config = ProjectConfig(metadata=metadata, paths=paths, settings=settings)

        assert config.metadata is metadata
        assert config.paths is paths
        assert config.settings is settings
        assert config.custom_data == {}

    def test_config_to_dict(self):
        """Test converting ProjectConfig to dictionary"""
        metadata = ProjectMetadata(
            name="Test", version="1.0", description="Test", author="Test"
        )
        config = ProjectConfig(metadata=metadata)

        data = config.to_dict()

        assert "metadata" in data
        assert "paths" in data
        assert "settings" in data
        assert "custom_data" in data
        assert data["metadata"]["name"] == "Test"

    def test_config_from_dict(self):
        """Test creating ProjectConfig from dictionary"""
        data = {
            "metadata": {
                "name": "Test Game",
                "version": "1.0.0",
                "description": "A test game",
                "author": "Test Author",
            },
            "paths": {"assets": "my_assets"},
            "settings": {"window_width": 1920},
            "custom_data": {"my_key": "my_value"},
        }

        config = ProjectConfig.from_dict(data)

        assert config.metadata.name == "Test Game"
        assert config.paths.assets == "my_assets"
        assert config.settings.window_width == 1920
        assert config.custom_data == {"my_key": "my_value"}

    def test_config_from_dict_partial(self):
        """Test creating ProjectConfig from partial dictionary"""
        data = {
            "metadata": {
                "name": "Test",
                "version": "1.0",
                "description": "Test",
                "author": "Test",
            }
        }

        config = ProjectConfig.from_dict(data)

        # Should use defaults for missing sections
        assert config.paths.assets == "assets"
        assert config.settings.window_width == 1280


# ===========================
# Project Tests
# ===========================


class TestProject:
    """Test Project class"""

    def test_project_initialization(self, tmp_path):
        """Test Project initialization"""
        project = Project(tmp_path)

        assert project.project_path == tmp_path
        assert project.config is None
        assert project._loaded is False

    def test_project_load_missing_file(self, tmp_path, capsys):
        """Test loading project with missing project.json"""
        project = Project(tmp_path)
        result = project.load()

        assert result is False
        captured = capsys.readouterr()
        assert "Project file not found" in captured.out

    def test_project_load_invalid_json(self, tmp_path, capsys):
        """Test loading project with invalid JSON"""
        project_file = tmp_path / "project.json"
        project_file.write_text("{ invalid json }")

        project = Project(tmp_path)
        result = project.load()

        assert result is False
        captured = capsys.readouterr()
        assert "Invalid JSON" in captured.out

    def test_project_load_valid_config(self, tmp_path, capsys):
        """Test loading project with valid configuration"""
        config_data = {
            "metadata": {
                "name": "Test Game",
                "version": "1.0.0",
                "description": "A test game",
                "author": "Test Author",
            },
            "paths": {
                "assets": "assets",
                "levels": "levels",
                "scripts": "scripts",
                "saves": "saves",
                "config": "config",
            },
            "settings": {
                "window_width": 1280,
                "window_height": 720,
            },
        }

        project_file = tmp_path / "project.json"
        project_file.write_text(json.dumps(config_data))

        project = Project(tmp_path)
        result = project.load()

        assert result is True
        assert project._loaded is True
        assert project.config is not None
        assert project.config.metadata.name == "Test Game"

        captured = capsys.readouterr()
        assert "Loaded project: Test Game" in captured.out

    def test_project_load_creates_directories(self, tmp_path):
        """Test loading project creates necessary directories"""
        config_data = {
            "metadata": {
                "name": "Test",
                "version": "1.0",
                "description": "Test",
                "author": "Test",
            },
            "paths": {},
            "settings": {},
        }

        project_file = tmp_path / "project.json"
        project_file.write_text(json.dumps(config_data))

        project = Project(tmp_path)
        project.load()

        # Check directories were created
        assert (tmp_path / "assets").exists()
        assert (tmp_path / "levels").exists()
        assert (tmp_path / "scripts").exists()
        assert (tmp_path / "saves").exists()
        assert (tmp_path / "config").exists()

    def test_project_load_invalid_config(self, tmp_path, capsys):
        """Test loading project with invalid configuration"""
        config_data = {
            "metadata": {},  # Missing required fields
            "paths": {},
            "settings": {},
        }

        project_file = tmp_path / "project.json"
        project_file.write_text(json.dumps(config_data))

        project = Project(tmp_path)
        result = project.load()

        assert result is False
        captured = capsys.readouterr()
        assert "Invalid project configuration" in captured.out or "Missing" in captured.out

    def test_project_save(self, tmp_path):
        """Test saving project configuration"""
        metadata = ProjectMetadata(
            name="Test", version="1.0", description="Test", author="Test"
        )
        config = ProjectConfig(metadata=metadata)

        project = Project(tmp_path)
        project.config = config

        result = project.save()

        assert result is True
        assert (tmp_path / "project.json").exists()

        # Verify saved content
        with open(tmp_path / "project.json", "r") as f:
            saved_data = json.load(f)

        assert saved_data["metadata"]["name"] == "Test"

    def test_project_save_no_config(self, tmp_path):
        """Test saving project without config"""
        project = Project(tmp_path)
        result = project.save()

        assert result is False

    def test_project_get_asset_path(self, tmp_path):
        """Test getting asset path"""
        config_data = {
            "metadata": {
                "name": "Test",
                "version": "1.0",
                "description": "Test",
                "author": "Test",
            },
            "paths": {},
            "settings": {},
        }

        project_file = tmp_path / "project.json"
        project_file.write_text(json.dumps(config_data))

        project = Project(tmp_path)
        project.load()

        asset_path = project.get_asset_path("sprites/player.png")
        assert asset_path == tmp_path / "assets" / "sprites/player.png"

    def test_project_get_level_path(self, tmp_path):
        """Test getting level path"""
        config_data = {
            "metadata": {
                "name": "Test",
                "version": "1.0",
                "description": "Test",
                "author": "Test",
            },
            "paths": {},
            "settings": {},
        }

        project_file = tmp_path / "project.json"
        project_file.write_text(json.dumps(config_data))

        project = Project(tmp_path)
        project.load()

        level_path = project.get_level_path("level1")
        assert level_path == tmp_path / "levels" / "level1.json"

    def test_project_get_save_path(self, tmp_path):
        """Test getting save file path"""
        config_data = {
            "metadata": {
                "name": "Test",
                "version": "1.0",
                "description": "Test",
                "author": "Test",
            },
            "paths": {},
            "settings": {},
        }

        project_file = tmp_path / "project.json"
        project_file.write_text(json.dumps(config_data))

        project = Project(tmp_path)
        project.load()

        save_path = project.get_save_path("save1")
        assert save_path == tmp_path / "saves" / "save1.json"

    def test_project_get_config_path(self, tmp_path):
        """Test getting config file path"""
        config_data = {
            "metadata": {
                "name": "Test",
                "version": "1.0",
                "description": "Test",
                "author": "Test",
            },
            "paths": {},
            "settings": {},
        }

        project_file = tmp_path / "project.json"
        project_file.write_text(json.dumps(config_data))

        project = Project(tmp_path)
        project.load()

        config_path = project.get_config_path("settings")
        assert config_path == tmp_path / "config" / "settings.json"

    def test_project_list_levels(self, tmp_path):
        """Test listing available levels"""
        config_data = {
            "metadata": {
                "name": "Test",
                "version": "1.0",
                "description": "Test",
                "author": "Test",
            },
            "paths": {},
            "settings": {},
        }

        project_file = tmp_path / "project.json"
        project_file.write_text(json.dumps(config_data))

        project = Project(tmp_path)
        project.load()

        # Create some level files
        levels_dir = tmp_path / "levels"
        (levels_dir / "level1.json").write_text("{}")
        (levels_dir / "level2.json").write_text("{}")
        (levels_dir / "bonus.json").write_text("{}")

        levels = project.list_levels()

        assert len(levels) == 3
        assert "level1" in levels
        assert "level2" in levels
        assert "bonus" in levels

    def test_project_list_levels_empty(self, tmp_path):
        """Test listing levels when none exist"""
        config_data = {
            "metadata": {
                "name": "Test",
                "version": "1.0",
                "description": "Test",
                "author": "Test",
            },
            "paths": {},
            "settings": {},
        }

        project_file = tmp_path / "project.json"
        project_file.write_text(json.dumps(config_data))

        project = Project(tmp_path)
        project.load()

        levels = project.list_levels()
        assert levels == []

    def test_project_list_saves(self, tmp_path):
        """Test listing save files"""
        config_data = {
            "metadata": {
                "name": "Test",
                "version": "1.0",
                "description": "Test",
                "author": "Test",
            },
            "paths": {},
            "settings": {},
        }

        project_file = tmp_path / "project.json"
        project_file.write_text(json.dumps(config_data))

        project = Project(tmp_path)
        project.load()

        # Create some save files
        saves_dir = tmp_path / "saves"
        (saves_dir / "save1.json").write_text("{}")
        (saves_dir / "save2.json").write_text("{}")
        (saves_dir / "autosave.json").write_text("{}")

        saves = project.list_saves()

        assert len(saves) == 3
        assert "save1" in saves
        assert "save2" in saves
        assert "autosave" in saves


# ===========================
# ProjectManager Tests
# ===========================


class TestProjectManager:
    """Test ProjectManager class"""

    def test_project_manager_initialization(self, tmp_path):
        """Test ProjectManager initialization"""
        manager = ProjectManager(tmp_path)

        assert manager.projects_root == tmp_path
        assert manager.current_project is None

    def test_create_project(self, tmp_path, capsys):
        """Test creating a new project"""
        manager = ProjectManager(tmp_path)
        metadata = ProjectMetadata(
            name="Test Game", version="1.0.0", description="Test", author="Test"
        )

        project = manager.create_project("test_game", metadata)

        assert project is not None
        assert (tmp_path / "test_game").exists()
        assert (tmp_path / "test_game" / "project.json").exists()
        assert project.config.metadata.name == "Test Game"

    def test_create_project_with_settings(self, tmp_path):
        """Test creating project with custom settings"""
        manager = ProjectManager(tmp_path)
        metadata = ProjectMetadata(
            name="Test", version="1.0", description="Test", author="Test"
        )
        settings = ProjectSettings(window_width=1920, enable_combat=True)

        project = manager.create_project("test_game", metadata, settings)

        assert project is not None
        assert project.config.settings.window_width == 1920
        assert project.config.settings.enable_combat is True

    def test_create_project_empty_name(self, tmp_path, capsys):
        """Test creating project with empty name"""
        manager = ProjectManager(tmp_path)
        metadata = ProjectMetadata(
            name="Test", version="1.0", description="Test", author="Test"
        )

        project = manager.create_project("", metadata)

        assert project is None
        captured = capsys.readouterr()
        assert "Project name cannot be empty" in captured.out

    def test_create_project_invalid_name(self, tmp_path, capsys):
        """Test creating project with invalid name"""
        manager = ProjectManager(tmp_path)
        metadata = ProjectMetadata(
            name="Test", version="1.0", description="Test", author="Test"
        )

        project = manager.create_project("test game!", metadata)

        assert project is None
        captured = capsys.readouterr()
        assert "Invalid project name" in captured.out

    def test_create_project_valid_names(self, tmp_path):
        """Test creating projects with various valid names"""
        manager = ProjectManager(tmp_path)
        metadata = ProjectMetadata(
            name="Test", version="1.0", description="Test", author="Test"
        )

        valid_names = ["test", "test_game", "test-game", "test123", "TEST"]

        for name in valid_names:
            project = manager.create_project(name, metadata)
            assert project is not None, f"Valid name {name} rejected"

    def test_create_project_already_exists(self, tmp_path, capsys):
        """Test creating project that already exists"""
        manager = ProjectManager(tmp_path)
        metadata = ProjectMetadata(
            name="Test", version="1.0", description="Test", author="Test"
        )

        # Create first time
        project1 = manager.create_project("test_game", metadata)
        assert project1 is not None

        # Try to create again
        project2 = manager.create_project("test_game", metadata)
        assert project2 is None

        captured = capsys.readouterr()
        assert "already exists" in captured.out

    def test_load_project(self, tmp_path):
        """Test loading an existing project"""
        manager = ProjectManager(tmp_path)
        metadata = ProjectMetadata(
            name="Test Game", version="1.0", description="Test", author="Test"
        )

        # Create project
        manager.create_project("test_game", metadata)

        # Load it
        project = manager.load_project("test_game")

        assert project is not None
        assert project.config.metadata.name == "Test Game"
        assert manager.current_project is project

    def test_load_project_empty_name(self, tmp_path, capsys):
        """Test loading project with empty name"""
        manager = ProjectManager(tmp_path)

        project = manager.load_project("")

        assert project is None
        captured = capsys.readouterr()
        assert "Project name cannot be empty" in captured.out

    def test_load_project_not_found(self, tmp_path, capsys):
        """Test loading non-existent project"""
        manager = ProjectManager(tmp_path)

        project = manager.load_project("nonexistent")

        assert project is None
        captured = capsys.readouterr()
        assert "not found" in captured.out

    def test_load_project_not_directory(self, tmp_path, capsys):
        """Test loading project where path is not a directory"""
        manager = ProjectManager(tmp_path)

        # Create a file instead of directory
        (tmp_path / "not_a_dir").write_text("test")

        project = manager.load_project("not_a_dir")

        assert project is None
        captured = capsys.readouterr()
        assert "not a directory" in captured.out

    def test_list_projects(self, tmp_path):
        """Test listing all projects"""
        manager = ProjectManager(tmp_path)
        metadata = ProjectMetadata(
            name="Test", version="1.0", description="Test", author="Test"
        )

        # Create multiple projects
        manager.create_project("game1", metadata)
        manager.create_project("game2", metadata)
        manager.create_project("game3", metadata)

        projects = manager.list_projects()

        assert len(projects) == 3
        assert "game1" in projects
        assert "game2" in projects
        assert "game3" in projects

    def test_list_projects_empty(self, tmp_path):
        """Test listing projects when none exist"""
        manager = ProjectManager(tmp_path)

        projects = manager.list_projects()

        assert projects == []

    def test_list_projects_no_directory(self, tmp_path):
        """Test listing projects when projects root doesn't exist"""
        manager = ProjectManager(tmp_path / "nonexistent")

        projects = manager.list_projects()

        assert projects == []

    def test_list_projects_ignores_invalid(self, tmp_path):
        """Test listing projects ignores directories without project.json"""
        manager = ProjectManager(tmp_path)
        metadata = ProjectMetadata(
            name="Test", version="1.0", description="Test", author="Test"
        )

        # Create valid project
        manager.create_project("valid_game", metadata)

        # Create invalid directory (no project.json)
        (tmp_path / "invalid_dir").mkdir()

        # Create file (not directory)
        (tmp_path / "not_a_dir").write_text("test")

        projects = manager.list_projects()

        assert len(projects) == 1
        assert "valid_game" in projects

    def test_get_current_project(self, tmp_path):
        """Test getting current project"""
        manager = ProjectManager(tmp_path)
        metadata = ProjectMetadata(
            name="Test", version="1.0", description="Test", author="Test"
        )

        manager.create_project("test_game", metadata)
        manager.load_project("test_game")

        current = manager.get_current_project()

        assert current is not None
        assert current is manager.current_project


# ===========================
# Global Functions Tests
# ===========================


class TestGlobalFunctions:
    """Test global convenience functions"""

    def test_get_project_manager(self):
        """Test getting global project manager"""
        manager1 = get_project_manager()
        manager2 = get_project_manager()

        # Should return same instance
        assert manager1 is manager2

    def test_load_project_function(self, tmp_path):
        """Test load_project convenience function"""
        # Create a project using manager
        manager = ProjectManager(tmp_path)
        metadata = ProjectMetadata(
            name="Test", version="1.0", description="Test", author="Test"
        )
        manager.create_project("test_game", metadata)

        # Update global manager to use our test directory
        import neonworks.core.project as project_module

        project_module._global_project_manager = manager

        # Load using convenience function
        project = load_project("test_game")

        assert project is not None
        assert project.config.metadata.name == "Test"

    def test_get_current_project_function(self, tmp_path):
        """Test get_current_project convenience function"""
        manager = ProjectManager(tmp_path)
        metadata = ProjectMetadata(
            name="Test", version="1.0", description="Test", author="Test"
        )
        manager.create_project("test_game", metadata)
        manager.load_project("test_game")

        # Update global manager
        import neonworks.core.project as project_module

        project_module._global_project_manager = manager

        # Get current using convenience function
        current = get_current_project()

        assert current is not None
        assert current is manager.current_project
