"""
Neon Collapse - Save/Load System
Manages game state persistence with multiple save slots
"""

from typing import Dict, List, Any, Optional
import json
import os
from pathlib import Path
from datetime import datetime


# Constants
MAX_SAVE_SLOTS = 3
AUTOSAVE_FILENAME = "autosave.json"


# ============================================================================
# SAVE GAME MANAGER
# ============================================================================

class SaveGameManager:
    """Manages saving and loading game state."""

    def __init__(self, save_dir: str = "saves"):
        self.save_dir = Path(save_dir)
        self.save_slots = MAX_SAVE_SLOTS

        # Ensure save directory exists
        self.save_dir.mkdir(parents=True, exist_ok=True)

    def _get_save_path(self, slot: int) -> Path:
        """Get path to save file for slot."""
        if slot < 1 or slot > self.save_slots:
            raise ValueError(f"Invalid save slot: {slot}. Must be 1-{self.save_slots}")
        return self.save_dir / f"save_slot_{slot}.json"

    def _get_autosave_path(self) -> Path:
        """Get path to autosave file."""
        return self.save_dir / AUTOSAVE_FILENAME

    def save_game(
        self,
        slot: int,
        quest_manager=None,
        faction_manager=None,
        skill_xp_manager=None,
        inventory=None,
        world_map=None,
        cyberware_manager=None,
        playtime_seconds: int = 0
    ) -> bool:
        """
        Save current game state to specified slot.

        Returns:
            True if save successful, False otherwise
        """
        if slot < 1 or slot > self.save_slots:
            raise ValueError(f"Invalid save slot: {slot}")

        try:
            # Build save data
            save_data = {
                "metadata": {
                    "slot": slot,
                    "timestamp": datetime.now().isoformat(),
                    "playtime_seconds": playtime_seconds,
                    "completed_quests": 0,
                    "version": "1.0.0"
                }
            }

            # Save each system if provided
            if quest_manager:
                try:
                    save_data["quest_manager"] = quest_manager.to_dict()
                    # Count completed quests for metadata
                    if hasattr(quest_manager, 'quests') and quest_manager.quests:
                        save_data["metadata"]["completed_quests"] = len(
                            [q for q in quest_manager.quests.values() if hasattr(q, 'status') and q.status == "completed"]
                        )
                except (AttributeError, TypeError) as e:
                    print(f"Warning: Failed to save quest_manager: {e}")

            if faction_manager:
                try:
                    save_data["faction_manager"] = faction_manager.to_dict()
                except (AttributeError, TypeError) as e:
                    print(f"Warning: Failed to save faction_manager: {e}")

            if skill_xp_manager:
                try:
                    save_data["skill_xp_manager"] = skill_xp_manager.to_dict()
                except (AttributeError, TypeError) as e:
                    print(f"Warning: Failed to save skill_xp_manager: {e}")

            if inventory:
                try:
                    save_data["inventory"] = inventory.to_dict()
                except (AttributeError, TypeError) as e:
                    print(f"Warning: Failed to save inventory: {e}")

            if world_map:
                try:
                    save_data["world_map"] = world_map.to_dict()
                except (AttributeError, TypeError) as e:
                    print(f"Warning: Failed to save world_map: {e}")

            if cyberware_manager:
                try:
                    save_data["cyberware_manager"] = cyberware_manager.to_dict()
                except (AttributeError, TypeError) as e:
                    print(f"Warning: Failed to save cyberware_manager: {e}")

            # Write to file
            save_path = self._get_save_path(slot)
            with open(save_path, 'w') as f:
                json.dump(save_data, f, indent=2)

            return True

        except Exception as e:
            print(f"Error saving game: {e}")
            return False

    def load_game(self, slot: int) -> Optional[Dict[str, Any]]:
        """
        Load game state from specified slot.

        Returns:
            Dictionary containing game state, or None if load failed
        """
        if slot < 1 or slot > self.save_slots:
            raise ValueError(f"Invalid save slot: {slot}")

        try:
            save_path = self._get_save_path(slot)

            if not save_path.exists():
                return None

            with open(save_path, 'r') as f:
                save_data = json.load(f)

            return save_data

        except (json.JSONDecodeError, Exception) as e:
            print(f"Error loading game: {e}")
            return None

    def auto_save(
        self,
        quest_manager=None,
        faction_manager=None,
        skill_xp_manager=None,
        inventory=None,
        world_map=None,
        cyberware_manager=None,
        playtime_seconds: int = 0
    ) -> bool:
        """
        Create auto-save (separate from manual save slots).

        Returns:
            True if autosave successful, False otherwise
        """
        try:
            # Build save data (same as regular save)
            save_data = {
                "metadata": {
                    "type": "autosave",
                    "timestamp": datetime.now().isoformat(),
                    "playtime_seconds": playtime_seconds,
                    "completed_quests": 0,
                    "version": "1.0.0"
                }
            }

            # Save each system if provided
            if quest_manager:
                save_data["quest_manager"] = quest_manager.to_dict()
                save_data["metadata"]["completed_quests"] = len(
                    [q for q in quest_manager.quests.values() if q.status == "completed"]
                )

            if faction_manager:
                save_data["faction_manager"] = faction_manager.to_dict()

            if skill_xp_manager:
                save_data["skill_xp_manager"] = skill_xp_manager.to_dict()

            if inventory:
                save_data["inventory"] = inventory.to_dict()

            if world_map:
                save_data["world_map"] = world_map.to_dict()

            if cyberware_manager:
                save_data["cyberware_manager"] = cyberware_manager.to_dict()

            # Write to autosave file
            autosave_path = self._get_autosave_path()
            with open(autosave_path, 'w') as f:
                json.dump(save_data, f, indent=2)

            return True

        except Exception as e:
            print(f"Error creating autosave: {e}")
            return False

    def load_autosave(self) -> Optional[Dict[str, Any]]:
        """
        Load autosave.

        Returns:
            Dictionary containing game state, or None if load failed
        """
        try:
            autosave_path = self._get_autosave_path()

            if not autosave_path.exists():
                return None

            with open(autosave_path, 'r') as f:
                save_data = json.load(f)

            return save_data

        except (json.JSONDecodeError, Exception) as e:
            print(f"Error loading autosave: {e}")
            return None

    def has_save(self, slot: int) -> bool:
        """Check if save exists in specified slot."""
        if slot < 1 or slot > self.save_slots:
            return False

        save_path = self._get_save_path(slot)
        return save_path.exists()

    def has_autosave(self) -> bool:
        """Check if autosave exists."""
        autosave_path = self._get_autosave_path()
        return autosave_path.exists()

    def delete_save(self, slot: int) -> bool:
        """
        Delete save in specified slot.

        Returns:
            True if deleted, False if save didn't exist
        """
        if slot < 1 or slot > self.save_slots:
            return False

        save_path = self._get_save_path(slot)

        if not save_path.exists():
            return False

        try:
            save_path.unlink()
            return True
        except Exception as e:
            print(f"Error deleting save: {e}")
            return False

    def delete_autosave(self) -> bool:
        """
        Delete autosave.

        Returns:
            True if deleted, False if autosave didn't exist
        """
        autosave_path = self._get_autosave_path()

        if not autosave_path.exists():
            return False

        try:
            autosave_path.unlink()
            return True
        except Exception as e:
            print(f"Error deleting autosave: {e}")
            return False

    def get_save_metadata(self, slot: int) -> Optional[Dict[str, Any]]:
        """
        Get metadata for save in specified slot.

        Returns:
            Metadata dictionary, or None if save doesn't exist
        """
        save_data = self.load_game(slot)

        if save_data is None:
            return None

        return save_data.get("metadata", {})

    def list_saves(self) -> List[Dict[str, Any]]:
        """
        List all available saves with their metadata.

        Returns:
            List of dictionaries containing save metadata
        """
        saves = []

        for slot in range(1, self.save_slots + 1):
            if self.has_save(slot):
                metadata = self.get_save_metadata(slot)
                if metadata:
                    saves.append(metadata)

        return saves

    def validate_save(self, slot: int) -> bool:
        """
        Validate save file integrity.

        Returns:
            True if save is valid, False if corrupted/invalid
        """
        if slot < 1 or slot > self.save_slots:
            return False

        try:
            save_path = self._get_save_path(slot)

            if not save_path.exists():
                return False

            # Try to load and parse JSON
            with open(save_path, 'r') as f:
                save_data = json.load(f)

            # Check for required fields
            if "metadata" not in save_data:
                return False

            metadata = save_data["metadata"]

            # Validate metadata fields
            required_fields = ["timestamp", "version"]
            for field in required_fields:
                if field not in metadata:
                    return False

            return True

        except (json.JSONDecodeError, Exception) as e:
            return False

    def validate_autosave(self) -> bool:
        """
        Validate autosave file integrity.

        Returns:
            True if autosave is valid, False if corrupted/invalid
        """
        try:
            autosave_path = self._get_autosave_path()

            if not autosave_path.exists():
                return False

            # Try to load and parse JSON
            with open(autosave_path, 'r') as f:
                save_data = json.load(f)

            # Check for required fields
            if "metadata" not in save_data:
                return False

            return True

        except (json.JSONDecodeError, Exception):
            return False
