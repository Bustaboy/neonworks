"""
Undo History Persistence

Provides utilities for saving and loading undo history across sessions.
"""

import json
import os
from pathlib import Path
from typing import Optional

from .undo_manager import UndoManager


class UndoHistoryPersistence:
    """
    Manages persistence of undo history to disk.

    Automatically saves and loads undo history for editors.
    """

    def __init__(self, project_path: Optional[str] = None):
        """
        Initialize undo history persistence.

        Args:
            project_path: Path to project directory (defaults to .neonworks_history)
        """
        if project_path:
            self.history_dir = Path(project_path) / ".undo_history"
        else:
            self.history_dir = Path.home() / ".neonworks" / "undo_history"

        # Create directory if it doesn't exist
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def save_editor_history(
        self, editor_name: str, undo_manager: UndoManager, auto_save: bool = True
    ):
        """
        Save undo history for a specific editor.

        Args:
            editor_name: Name of the editor (e.g., "level_builder", "navmesh_editor")
            undo_manager: UndoManager instance to save
            auto_save: Whether to save automatically (default: True)
        """
        if not auto_save:
            return

        history_file = self.history_dir / f"{editor_name}_history.json"

        try:
            undo_manager.save_history(str(history_file))
            print(f"Saved {editor_name} undo history to {history_file}")
        except Exception as e:
            print(f"Warning: Failed to save {editor_name} undo history: {e}")

    def load_editor_history(
        self, editor_name: str, undo_manager: UndoManager, auto_load: bool = True
    ):
        """
        Load undo history for a specific editor.

        Args:
            editor_name: Name of the editor
            undo_manager: UndoManager instance to load into
            auto_load: Whether to load automatically (default: True)
        """
        if not auto_load:
            return

        history_file = self.history_dir / f"{editor_name}_history.json"

        if not history_file.exists():
            print(f"No saved history found for {editor_name}")
            return

        try:
            undo_manager.load_history(str(history_file))
            print(f"Loaded {editor_name} undo history from {history_file}")
        except Exception as e:
            print(f"Warning: Failed to load {editor_name} undo history: {e}")

    def clear_editor_history(self, editor_name: str):
        """
        Clear saved undo history for a specific editor.

        Args:
            editor_name: Name of the editor
        """
        history_file = self.history_dir / f"{editor_name}_history.json"

        if history_file.exists():
            history_file.unlink()
            print(f"Cleared {editor_name} undo history")

    def get_history_info(self, editor_name: str) -> Optional[dict]:
        """
        Get information about saved history.

        Args:
            editor_name: Name of the editor

        Returns:
            Dictionary with history info or None if no history exists
        """
        history_file = self.history_dir / f"{editor_name}_history.json"

        if not history_file.exists():
            return None

        try:
            with open(history_file, "r") as f:
                data = json.load(f)

            return {
                "file": str(history_file),
                "size_kb": history_file.stat().st_size / 1024,
                "version": data.get("version"),
                "timestamp": data.get("timestamp"),
                "undo_count": len(data.get("undo_stack", [])),
                "redo_count": len(data.get("redo_stack", [])),
                "statistics": data.get("statistics", {}),
            }
        except Exception as e:
            print(f"Warning: Failed to read {editor_name} history info: {e}")
            return None

    def list_all_histories(self) -> list:
        """
        List all saved undo histories.

        Returns:
            List of (editor_name, info_dict) tuples
        """
        histories = []

        for history_file in self.history_dir.glob("*_history.json"):
            editor_name = history_file.stem.replace("_history", "")
            info = self.get_history_info(editor_name)
            if info:
                histories.append((editor_name, info))

        return histories


# Global persistence instance
_undo_persistence = None


def get_undo_persistence(project_path: Optional[str] = None) -> UndoHistoryPersistence:
    """
    Get the global undo persistence instance.

    Args:
        project_path: Optional project path (only used on first call)

    Returns:
        Global UndoHistoryPersistence instance
    """
    global _undo_persistence
    if _undo_persistence is None:
        _undo_persistence = UndoHistoryPersistence(project_path)
    return _undo_persistence


def enable_auto_save(editor_name: str, undo_manager: UndoManager, interval: float = 60.0):
    """
    Enable automatic saving of undo history.

    Args:
        editor_name: Name of the editor
        undo_manager: UndoManager instance
        interval: Save interval in seconds (default: 60)

    Note: This is a simple implementation. In a real application,
    you would use a timer or background thread for automatic saving.
    """
    persistence = get_undo_persistence()

    # Simple implementation: save on every N commands
    # In a real implementation, use a timer-based approach
    original_execute = undo_manager.execute

    command_counter = [0]  # Use list to allow modification in closure

    def execute_with_autosave(command):
        result = original_execute(command)
        command_counter[0] += 1

        # Save every 10 commands (simple heuristic)
        if command_counter[0] >= 10:
            persistence.save_editor_history(editor_name, undo_manager)
            command_counter[0] = 0

        return result

    undo_manager.execute = execute_with_autosave
