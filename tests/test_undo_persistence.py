"""
Comprehensive tests for Undo History Persistence

Tests saving/loading undo history across sessions.
"""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from neonworks.core.undo_manager import Command, UndoManager
from neonworks.core.undo_persistence import (
    UndoHistoryPersistence,
    enable_auto_save,
    get_undo_persistence,
)


class DummyCommand(Command):
    """Test command for undo testing"""

    def __init__(self, value: int = 0):
        super().__init__()
        self.value = value
        self.executed_flag = False
        self.undone_flag = False

    def execute(self):
        """Execute command"""
        self.executed_flag = True
        self.executed = True
        return True

    def undo(self):
        """Undo command"""
        self.undone_flag = True
        return True

    def get_description(self):
        """Get command description"""
        return f"DummyCommand(value={self.value})"

    def serialize(self):
        """Serialize command"""
        return {"type": "DummyCommand", "value": self.value}

    @staticmethod
    def deserialize(data):
        """Deserialize command"""
        return DummyCommand(data.get("value", 0))


class TestUndoHistoryPersistenceInit:
    """Test UndoHistoryPersistence initialization"""

    def test_init_with_project_path(self, tmp_path):
        """Test creating persistence with project path"""
        project_dir = tmp_path / "my_project"
        project_dir.mkdir()

        persistence = UndoHistoryPersistence(str(project_dir))

        assert persistence.history_dir == project_dir / ".undo_history"
        assert persistence.history_dir.exists()

    def test_init_without_project_path(self):
        """Test creating persistence without project path"""
        persistence = UndoHistoryPersistence(None)

        # Should use home directory
        expected_dir = Path.home() / ".neonworks" / "undo_history"
        assert persistence.history_dir == expected_dir
        assert persistence.history_dir.exists()

    def test_init_creates_directory(self, tmp_path):
        """Test initialization creates history directory"""
        project_dir = tmp_path / "test_project"
        # Don't create project_dir, let persistence create it

        persistence = UndoHistoryPersistence(str(project_dir))

        assert persistence.history_dir.exists()


class TestSaveEditorHistory:
    """Test saving editor history"""

    def test_save_editor_history_success(self, tmp_path):
        """Test successfully saving editor history"""
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        persistence = UndoHistoryPersistence(str(project_dir))
        undo_manager = UndoManager()

        # Add some commands
        undo_manager.execute(DummyCommand(1))
        undo_manager.execute(DummyCommand(2))

        # Save history
        persistence.save_editor_history("test_editor", undo_manager)

        # Check file exists
        history_file = persistence.history_dir / "test_editor_history.json"
        assert history_file.exists()

    def test_save_editor_history_auto_save_disabled(self, tmp_path):
        """Test save with auto_save=False does nothing"""
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        persistence = UndoHistoryPersistence(str(project_dir))
        undo_manager = UndoManager()

        # Save with auto_save=False
        persistence.save_editor_history("test_editor", undo_manager, auto_save=False)

        # File should not exist
        history_file = persistence.history_dir / "test_editor_history.json"
        assert not history_file.exists()

    def test_save_editor_history_handles_errors(self, tmp_path, capsys):
        """Test save handles errors gracefully"""
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        persistence = UndoHistoryPersistence(str(project_dir))
        undo_manager = UndoManager()

        # Mock save_history to raise exception
        with patch.object(undo_manager, "save_history", side_effect=IOError("Mock error")):
            persistence.save_editor_history("test_editor", undo_manager)

        # Should print warning
        captured = capsys.readouterr()
        assert "Warning: Failed to save" in captured.out


class TestLoadEditorHistory:
    """Test loading editor history"""

    def test_load_editor_history_success(self, tmp_path, capsys):
        """Test successfully loading editor history"""
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        persistence = UndoHistoryPersistence(str(project_dir))

        # Create and save history
        undo_manager1 = UndoManager()
        undo_manager1.execute(DummyCommand(42))
        undo_manager1.execute(DummyCommand(99))
        persistence.save_editor_history("test_editor", undo_manager1)

        # Load into new manager
        undo_manager2 = UndoManager()
        persistence.load_editor_history("test_editor", undo_manager2)

        # Check that load was attempted (metadata loaded)
        captured = capsys.readouterr()
        assert "Loaded test_editor undo history" in captured.out
        assert "Loaded history metadata" in captured.out

        # Check statistics were restored
        assert undo_manager2.total_commands_executed == 2

    def test_load_editor_history_auto_load_disabled(self, tmp_path):
        """Test load with auto_load=False does nothing"""
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        persistence = UndoHistoryPersistence(str(project_dir))

        # Create history file
        undo_manager1 = UndoManager()
        undo_manager1.execute(DummyCommand(42))
        persistence.save_editor_history("test_editor", undo_manager1)

        # Load with auto_load=False
        undo_manager2 = UndoManager()
        persistence.load_editor_history("test_editor", undo_manager2, auto_load=False)

        # History should not be loaded
        assert len(undo_manager2.undo_stack) == 0

    def test_load_editor_history_file_not_found(self, tmp_path, capsys):
        """Test loading when history file doesn't exist"""
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        persistence = UndoHistoryPersistence(str(project_dir))
        undo_manager = UndoManager()

        # Try to load non-existent history
        persistence.load_editor_history("nonexistent_editor", undo_manager)

        # Should print message
        captured = capsys.readouterr()
        assert "No saved history found" in captured.out

    def test_load_editor_history_handles_errors(self, tmp_path, capsys):
        """Test load handles errors gracefully"""
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        persistence = UndoHistoryPersistence(str(project_dir))
        undo_manager = UndoManager()

        # Create invalid JSON file
        history_file = persistence.history_dir / "test_editor_history.json"
        with open(history_file, "w") as f:
            f.write("invalid json{")

        # Try to load
        persistence.load_editor_history("test_editor", undo_manager)

        # Should print warning
        captured = capsys.readouterr()
        assert "Warning: Failed to load" in captured.out


class TestClearEditorHistory:
    """Test clearing editor history"""

    def test_clear_editor_history_success(self, tmp_path):
        """Test successfully clearing editor history"""
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        persistence = UndoHistoryPersistence(str(project_dir))

        # Create history
        undo_manager = UndoManager()
        undo_manager.execute(DummyCommand(1))
        persistence.save_editor_history("test_editor", undo_manager)

        # Clear history
        persistence.clear_editor_history("test_editor")

        # File should be deleted
        history_file = persistence.history_dir / "test_editor_history.json"
        assert not history_file.exists()

    def test_clear_editor_history_nonexistent(self, tmp_path):
        """Test clearing non-existent history (should not error)"""
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        persistence = UndoHistoryPersistence(str(project_dir))

        # Clear non-existent history (should not crash)
        persistence.clear_editor_history("nonexistent_editor")


class TestGetHistoryInfo:
    """Test getting history information"""

    def test_get_history_info_success(self, tmp_path):
        """Test getting history info for existing file"""
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        persistence = UndoHistoryPersistence(str(project_dir))

        # Create history
        undo_manager = UndoManager()
        undo_manager.execute(DummyCommand(1))
        undo_manager.execute(DummyCommand(2))
        undo_manager.execute(DummyCommand(3))
        persistence.save_editor_history("test_editor", undo_manager)

        # Get info
        info = persistence.get_history_info("test_editor")

        assert info is not None
        assert "file" in info
        assert "size_kb" in info
        assert "version" in info
        assert "timestamp" in info
        assert info["undo_count"] == 3
        assert info["redo_count"] == 0

    def test_get_history_info_nonexistent(self, tmp_path):
        """Test getting info for non-existent history"""
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        persistence = UndoHistoryPersistence(str(project_dir))

        # Get info for non-existent editor
        info = persistence.get_history_info("nonexistent_editor")

        assert info is None

    def test_get_history_info_handles_errors(self, tmp_path, capsys):
        """Test get_history_info handles errors"""
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        persistence = UndoHistoryPersistence(str(project_dir))

        # Create invalid JSON file
        history_file = persistence.history_dir / "test_editor_history.json"
        with open(history_file, "w") as f:
            f.write("invalid json{")

        # Try to get info
        info = persistence.get_history_info("test_editor")

        assert info is None
        captured = capsys.readouterr()
        assert "Warning: Failed to read" in captured.out


class TestListAllHistories:
    """Test listing all histories"""

    def test_list_all_histories_empty(self, tmp_path):
        """Test listing when no histories exist"""
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        persistence = UndoHistoryPersistence(str(project_dir))

        histories = persistence.list_all_histories()

        assert histories == []

    def test_list_all_histories_multiple(self, tmp_path):
        """Test listing multiple histories"""
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        persistence = UndoHistoryPersistence(str(project_dir))

        # Create multiple histories
        for editor_name in ["editor1", "editor2", "editor3"]:
            undo_manager = UndoManager()
            undo_manager.execute(DummyCommand(1))
            persistence.save_editor_history(editor_name, undo_manager)

        # List histories
        histories = persistence.list_all_histories()

        assert len(histories) == 3
        editor_names = [name for name, info in histories]
        assert "editor1" in editor_names
        assert "editor2" in editor_names
        assert "editor3" in editor_names

    def test_list_all_histories_skips_invalid(self, tmp_path):
        """Test listing skips invalid history files"""
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        persistence = UndoHistoryPersistence(str(project_dir))

        # Create valid history
        undo_manager = UndoManager()
        undo_manager.execute(DummyCommand(1))
        persistence.save_editor_history("editor1", undo_manager)

        # Create invalid history file
        invalid_file = persistence.history_dir / "editor2_history.json"
        with open(invalid_file, "w") as f:
            f.write("invalid json{")

        # List histories (should skip invalid)
        histories = persistence.list_all_histories()

        assert len(histories) == 1
        assert histories[0][0] == "editor1"


class TestGlobalPersistence:
    """Test global persistence instance"""

    def test_get_undo_persistence_creates_instance(self):
        """Test get_undo_persistence creates global instance"""
        # Reset global instance
        import neonworks.core.undo_persistence as module

        module._undo_persistence = None

        # Get instance
        persistence1 = get_undo_persistence()

        assert persistence1 is not None

        # Get again, should be same instance
        persistence2 = get_undo_persistence()

        assert persistence1 is persistence2

    def test_get_undo_persistence_with_project_path(self, tmp_path):
        """Test get_undo_persistence with custom project path"""
        # Reset global instance
        import neonworks.core.undo_persistence as module

        module._undo_persistence = None

        project_dir = tmp_path / "test_project"
        project_dir.mkdir()

        # Get instance with project path
        persistence = get_undo_persistence(str(project_dir))

        assert persistence.history_dir == project_dir / ".undo_history"


class TestEnableAutoSave:
    """Test automatic saving functionality"""

    def test_enable_auto_save_basic(self, tmp_path):
        """Test enabling auto-save"""
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        # Reset global instance
        import neonworks.core.undo_persistence as module

        module._undo_persistence = UndoHistoryPersistence(str(project_dir))

        undo_manager = UndoManager()

        # Enable auto-save
        enable_auto_save("test_editor", undo_manager, interval=60.0)

        # Execute commands (10 commands should trigger save)
        for i in range(10):
            undo_manager.execute(DummyCommand(i))

        # History should be saved
        persistence = get_undo_persistence()
        history_file = persistence.history_dir / "test_editor_history.json"
        assert history_file.exists()

    def test_enable_auto_save_saves_every_10_commands(self, tmp_path):
        """Test auto-save saves every 10 commands"""
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        # Reset global instance
        import neonworks.core.undo_persistence as module

        module._undo_persistence = UndoHistoryPersistence(str(project_dir))

        undo_manager = UndoManager()

        # Enable auto-save
        enable_auto_save("test_editor", undo_manager)

        # Execute 9 commands (should not save yet)
        for i in range(9):
            undo_manager.execute(DummyCommand(i))

        persistence = get_undo_persistence()
        history_file = persistence.history_dir / "test_editor_history.json"
        assert not history_file.exists()

        # Execute 10th command (should trigger save)
        undo_manager.execute(DummyCommand(9))
        assert history_file.exists()


class TestIntegration:
    """Integration tests for undo persistence"""

    def test_full_persistence_workflow(self, tmp_path):
        """Test complete save/load workflow"""
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        persistence = UndoHistoryPersistence(str(project_dir))

        # Session 1: Create and save history
        undo_manager1 = UndoManager()
        undo_manager1.execute(DummyCommand(1))
        undo_manager1.execute(DummyCommand(2))
        undo_manager1.execute(DummyCommand(3))
        undo_manager1.undo()  # Undo last command
        persistence.save_editor_history("level_builder", undo_manager1)

        # Verify file was created with correct data
        info = persistence.get_history_info("level_builder")
        assert info is not None
        assert info["undo_count"] == 2  # 3 executed, 1 undone
        assert info["redo_count"] == 1  # 1 undone

        # Session 2: Load history in new manager
        undo_manager2 = UndoManager()
        persistence.load_editor_history("level_builder", undo_manager2)

        # Verify statistics were restored
        assert undo_manager2.total_commands_executed == 3
        assert undo_manager2.total_undos == 1

        # Clear history
        persistence.clear_editor_history("level_builder")
        assert persistence.get_history_info("level_builder") is None


# Run tests with: pytest tests/test_undo_persistence.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
