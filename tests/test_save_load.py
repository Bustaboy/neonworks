"""
Comprehensive test suite for save_load.py (Save/Load System)

Tests cover:
- Saving complete game state
- Loading game state
- Multiple save slots (3 slots)
- Auto-save functionality
- Save file validation
- Corruption detection
- Save metadata (timestamp, play time, progress)
- Integration with all game systems
"""

import pytest
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch
import sys

# Add game directory to path
game_dir = Path(__file__).parent.parent / "game"
sys.path.insert(0, str(game_dir))


class TestSaveGameCreation:
    """Test creating save games."""

    def test_create_save_manager(self):
        """Test creating save game manager."""
        from save_load import SaveGameManager

        manager = SaveGameManager()

        assert manager is not None
        assert manager.save_slots == 3

    def test_save_current_game(self, tmp_path):
        """Test saving current game state."""
        from save_load import SaveGameManager
        from quest import QuestManager
        from faction import FactionManager

        manager = SaveGameManager(save_dir=str(tmp_path))

        # Create game state
        quest_manager = QuestManager()
        faction_manager = FactionManager()

        # Save game to slot 1
        result = manager.save_game(
            slot=1,
            quest_manager=quest_manager,
            faction_manager=faction_manager
        )

        assert result is True
        assert manager.has_save(1)

    def test_save_file_created(self, tmp_path):
        """Test save file is actually created."""
        from save_load import SaveGameManager
        from quest import QuestManager

        manager = SaveGameManager(save_dir=str(tmp_path))
        quest_manager = QuestManager()

        manager.save_game(slot=1, quest_manager=quest_manager)

        # Check file exists
        save_file = tmp_path / "save_slot_1.json"
        assert save_file.exists()

    def test_save_multiple_slots(self, tmp_path):
        """Test saving to multiple slots."""
        from save_load import SaveGameManager
        from quest import QuestManager

        manager = SaveGameManager(save_dir=str(tmp_path))
        quest_manager = QuestManager()

        # Save to all 3 slots
        for slot in [1, 2, 3]:
            result = manager.save_game(slot=slot, quest_manager=quest_manager)
            assert result is True

        # All slots should have saves
        assert manager.has_save(1)
        assert manager.has_save(2)
        assert manager.has_save(3)

    def test_invalid_slot_number(self, tmp_path):
        """Test invalid slot numbers raise error."""
        from save_load import SaveGameManager
        from quest import QuestManager

        manager = SaveGameManager(save_dir=str(tmp_path))
        quest_manager = QuestManager()

        # Invalid slots
        with pytest.raises(ValueError):
            manager.save_game(slot=0, quest_manager=quest_manager)

        with pytest.raises(ValueError):
            manager.save_game(slot=4, quest_manager=quest_manager)


class TestLoadGame:
    """Test loading saved games."""

    def test_load_saved_game(self, tmp_path):
        """Test loading a saved game."""
        from save_load import SaveGameManager
        from quest import QuestManager
        from faction import FactionManager

        manager = SaveGameManager(save_dir=str(tmp_path))

        # Create and modify game state
        quest_manager = QuestManager()
        faction_manager = FactionManager()

        quest = quest_manager.get_quest("main_1")
        quest_manager.activate_quest("main_1")

        faction_manager.adjust_rep("militech", 50)

        # Save
        manager.save_game(
            slot=1,
            quest_manager=quest_manager,
            faction_manager=faction_manager
        )

        # Load
        loaded_state = manager.load_game(slot=1)

        assert loaded_state is not None
        assert "quest_manager" in loaded_state
        assert "faction_manager" in loaded_state

    def test_load_preserves_quest_state(self, tmp_path):
        """Test loaded game preserves quest progress."""
        from save_load import SaveGameManager
        from quest import QuestManager

        manager = SaveGameManager(save_dir=str(tmp_path))

        # Create quest progress
        quest_manager = QuestManager()
        quest_manager.activate_quest("main_1")

        # Save
        manager.save_game(slot=1, quest_manager=quest_manager)

        # Load
        loaded_state = manager.load_game(slot=1)

        # Verify quest manager data is in save
        assert "quest_manager" in loaded_state
        assert "quests" in loaded_state["quest_manager"]

    def test_load_preserves_faction_state(self, tmp_path):
        """Test loaded game preserves faction reputation."""
        from save_load import SaveGameManager
        from faction import FactionManager

        manager = SaveGameManager(save_dir=str(tmp_path))

        # Create faction progress
        faction_manager = FactionManager()
        faction_manager.adjust_rep("militech", 75)
        faction_manager.adjust_rep("syndicate", -30)

        # Save
        manager.save_game(slot=1, faction_manager=faction_manager)

        # Load
        loaded_state = manager.load_game(slot=1)

        # Restore faction manager
        loaded_faction_manager = FactionManager.from_dict(loaded_state["faction_manager"])

        militech = loaded_faction_manager.get_faction("militech")
        assert militech.rep == 75
        assert militech.level == 1

        syndicate = loaded_faction_manager.get_faction("syndicate")
        assert syndicate.status == "hostile"

    def test_load_nonexistent_save(self, tmp_path):
        """Test loading nonexistent save returns None."""
        from save_load import SaveGameManager

        manager = SaveGameManager(save_dir=str(tmp_path))

        loaded = manager.load_game(slot=1)

        assert loaded is None

    def test_load_all_systems(self, tmp_path):
        """Test loading preserves all game systems."""
        from save_load import SaveGameManager
        from quest import QuestManager
        from faction import FactionManager
        from skill_xp import SkillXPManager
        from world_map import WorldMap

        manager = SaveGameManager(save_dir=str(tmp_path))

        # Create full game state
        quest_manager = QuestManager()
        faction_manager = FactionManager()
        skill_xp_manager = SkillXPManager()
        world_map = WorldMap()

        # Make changes
        quest_manager.activate_quest("main_1")
        faction_manager.adjust_rep("militech", 50)
        skill_xp_manager.gain_body_xp(100)

        # Save all systems
        manager.save_game(
            slot=1,
            quest_manager=quest_manager,
            faction_manager=faction_manager,
            skill_xp_manager=skill_xp_manager,
            world_map=world_map
        )

        # Load
        loaded_state = manager.load_game(slot=1)

        # Verify all systems present
        assert "quest_manager" in loaded_state
        assert "faction_manager" in loaded_state
        assert "skill_xp_manager" in loaded_state
        assert "world_map" in loaded_state


class TestSaveMetadata:
    """Test save file metadata."""

    def test_save_includes_metadata(self, tmp_path):
        """Test save includes metadata (timestamp, etc)."""
        from save_load import SaveGameManager
        from quest import QuestManager

        manager = SaveGameManager(save_dir=str(tmp_path))
        quest_manager = QuestManager()

        manager.save_game(slot=1, quest_manager=quest_manager)

        metadata = manager.get_save_metadata(slot=1)

        assert metadata is not None
        assert "timestamp" in metadata
        assert "slot" in metadata
        assert metadata["slot"] == 1

    def test_metadata_includes_playtime(self, tmp_path):
        """Test metadata includes playtime."""
        from save_load import SaveGameManager
        from quest import QuestManager

        manager = SaveGameManager(save_dir=str(tmp_path))
        quest_manager = QuestManager()

        manager.save_game(slot=1, quest_manager=quest_manager, playtime_seconds=3600)

        metadata = manager.get_save_metadata(slot=1)

        assert metadata["playtime_seconds"] == 3600

    def test_metadata_includes_progress(self, tmp_path):
        """Test metadata includes game progress."""
        from save_load import SaveGameManager
        from quest import QuestManager

        manager = SaveGameManager(save_dir=str(tmp_path))

        quest_manager = QuestManager()

        manager.save_game(slot=1, quest_manager=quest_manager)

        metadata = manager.get_save_metadata(slot=1)

        # Check that metadata tracks quest progress
        assert "completed_quests" in metadata
        assert isinstance(metadata["completed_quests"], int)

    def test_list_all_saves(self, tmp_path):
        """Test listing all available saves."""
        from save_load import SaveGameManager
        from quest import QuestManager

        manager = SaveGameManager(save_dir=str(tmp_path))
        quest_manager = QuestManager()

        # Create saves in slots 1 and 3
        manager.save_game(slot=1, quest_manager=quest_manager)
        manager.save_game(slot=3, quest_manager=quest_manager)

        saves = manager.list_saves()

        assert len(saves) == 2
        assert 1 in [s["slot"] for s in saves]
        assert 3 in [s["slot"] for s in saves]


class TestAutoSave:
    """Test auto-save functionality."""

    def test_autosave_creation(self, tmp_path):
        """Test creating auto-save."""
        from save_load import SaveGameManager
        from quest import QuestManager

        manager = SaveGameManager(save_dir=str(tmp_path))
        quest_manager = QuestManager()

        result = manager.auto_save(quest_manager=quest_manager)

        assert result is True
        assert manager.has_autosave()

    def test_autosave_separate_from_slots(self, tmp_path):
        """Test autosave doesn't use slot numbers."""
        from save_load import SaveGameManager
        from quest import QuestManager

        manager = SaveGameManager(save_dir=str(tmp_path))
        quest_manager = QuestManager()

        # Create autosave and regular save
        manager.auto_save(quest_manager=quest_manager)
        manager.save_game(slot=1, quest_manager=quest_manager)

        # Both should exist
        assert manager.has_autosave()
        assert manager.has_save(1)

    def test_load_autosave(self, tmp_path):
        """Test loading autosave."""
        from save_load import SaveGameManager
        from faction import FactionManager

        manager = SaveGameManager(save_dir=str(tmp_path))

        faction_manager = FactionManager()
        faction_manager.adjust_rep("militech", 100)

        # Auto-save
        manager.auto_save(faction_manager=faction_manager)

        # Load autosave
        loaded = manager.load_autosave()

        assert loaded is not None
        loaded_faction = FactionManager.from_dict(loaded["faction_manager"])
        assert loaded_faction.get_faction("militech").rep == 100


class TestSaveValidation:
    """Test save file validation and corruption detection."""

    def test_validate_good_save(self, tmp_path):
        """Test validating a good save file."""
        from save_load import SaveGameManager
        from quest import QuestManager

        manager = SaveGameManager(save_dir=str(tmp_path))
        quest_manager = QuestManager()

        manager.save_game(slot=1, quest_manager=quest_manager)

        is_valid = manager.validate_save(slot=1)

        assert is_valid is True

    def test_detect_corrupted_save(self, tmp_path):
        """Test detecting corrupted save file."""
        from save_load import SaveGameManager

        manager = SaveGameManager(save_dir=str(tmp_path))

        # Create corrupted save file
        save_file = tmp_path / "save_slot_1.json"
        save_file.write_text("{ corrupted json data {")

        is_valid = manager.validate_save(slot=1)

        assert is_valid is False

    def test_detect_missing_required_fields(self, tmp_path):
        """Test detecting save missing required fields."""
        from save_load import SaveGameManager

        manager = SaveGameManager(save_dir=str(tmp_path))

        # Create save with missing fields
        save_file = tmp_path / "save_slot_1.json"
        save_file.write_text('{"incomplete": "data"}')

        is_valid = manager.validate_save(slot=1)

        assert is_valid is False

    def test_safe_load_corrupted_save(self, tmp_path):
        """Test loading corrupted save returns None."""
        from save_load import SaveGameManager

        manager = SaveGameManager(save_dir=str(tmp_path))

        # Create corrupted save
        save_file = tmp_path / "save_slot_1.json"
        save_file.write_text("corrupted")

        loaded = manager.load_game(slot=1)

        assert loaded is None


class TestDeleteSave:
    """Test deleting save files."""

    def test_delete_save(self, tmp_path):
        """Test deleting a save file."""
        from save_load import SaveGameManager
        from quest import QuestManager

        manager = SaveGameManager(save_dir=str(tmp_path))
        quest_manager = QuestManager()

        # Create save
        manager.save_game(slot=1, quest_manager=quest_manager)
        assert manager.has_save(1)

        # Delete save
        result = manager.delete_save(slot=1)

        assert result is True
        assert not manager.has_save(1)

    def test_delete_nonexistent_save(self, tmp_path):
        """Test deleting nonexistent save returns False."""
        from save_load import SaveGameManager

        manager = SaveGameManager(save_dir=str(tmp_path))

        result = manager.delete_save(slot=1)

        assert result is False

    def test_delete_autosave(self, tmp_path):
        """Test deleting autosave."""
        from save_load import SaveGameManager
        from quest import QuestManager

        manager = SaveGameManager(save_dir=str(tmp_path))
        quest_manager = QuestManager()

        manager.auto_save(quest_manager=quest_manager)
        assert manager.has_autosave()

        result = manager.delete_autosave()

        assert result is True
        assert not manager.has_autosave()


class TestOverwriteSave:
    """Test overwriting existing saves."""

    def test_overwrite_existing_save(self, tmp_path):
        """Test overwriting an existing save."""
        from save_load import SaveGameManager
        from faction import FactionManager

        manager = SaveGameManager(save_dir=str(tmp_path))

        # Create initial save
        faction_manager_v1 = FactionManager()
        faction_manager_v1.adjust_rep("militech", 50)
        manager.save_game(slot=1, faction_manager=faction_manager_v1)

        # Overwrite with new state
        faction_manager_v2 = FactionManager()
        faction_manager_v2.adjust_rep("militech", 100)
        manager.save_game(slot=1, faction_manager=faction_manager_v2)

        # Load should get newest version
        loaded = manager.load_game(slot=1)
        loaded_faction = FactionManager.from_dict(loaded["faction_manager"])

        assert loaded_faction.get_faction("militech").rep == 100

    def test_autosave_overwrites_previous(self, tmp_path):
        """Test autosave overwrites previous autosave."""
        from save_load import SaveGameManager
        from skill_xp import SkillXPManager

        manager = SaveGameManager(save_dir=str(tmp_path))

        # First autosave
        skill_xp_v1 = SkillXPManager()
        skill_xp_v1.gain_body_xp(20)
        manager.auto_save(skill_xp_manager=skill_xp_v1)

        # Second autosave (different from first)
        skill_xp_v2 = SkillXPManager()
        skill_xp_v2.gain_body_xp(40)
        manager.auto_save(skill_xp_manager=skill_xp_v2)

        # Load should get newest (40 XP, not 20)
        loaded = manager.load_autosave()
        loaded_skill = SkillXPManager.from_dict(loaded["skill_xp_manager"])

        assert loaded_skill.get_attribute_xp("body") == 40


class TestEdgeCases:
    """Test edge cases."""

    def test_empty_save_directory(self, tmp_path):
        """Test manager works with empty save directory."""
        from save_load import SaveGameManager

        manager = SaveGameManager(save_dir=str(tmp_path))

        saves = manager.list_saves()

        assert len(saves) == 0

    def test_save_with_no_systems(self, tmp_path):
        """Test saving with no game systems provided."""
        from save_load import SaveGameManager

        manager = SaveGameManager(save_dir=str(tmp_path))

        # Save with no systems (should still create save with metadata)
        result = manager.save_game(slot=1)

        assert result is True
        assert manager.has_save(1)

    def test_save_directory_creation(self, tmp_path):
        """Test save directory is created if missing."""
        from save_load import SaveGameManager
        from quest import QuestManager

        # Use non-existent subdirectory
        save_dir = tmp_path / "saves"
        assert not save_dir.exists()

        manager = SaveGameManager(save_dir=str(save_dir))
        quest_manager = QuestManager()

        manager.save_game(slot=1, quest_manager=quest_manager)

        # Directory should be created
        assert save_dir.exists()
        assert manager.has_save(1)


class TestErrorHandling:
    """Test error handling in save/load operations."""

    def test_save_with_broken_quest_manager(self, tmp_path):
        """Test saving with quest manager that raises AttributeError."""
        from save_load import SaveGameManager

        class BrokenQuestManager:
            """Quest manager that fails to serialize."""
            def to_dict(self):
                raise AttributeError("Broken!")

        manager = SaveGameManager(save_dir=str(tmp_path))
        broken_qm = BrokenQuestManager()

        # Should handle error gracefully and still save
        result = manager.save_game(slot=1, quest_manager=broken_qm)

        assert result is True

    def test_save_with_broken_faction_manager(self, tmp_path):
        """Test saving with faction manager that raises TypeError."""
        from save_load import SaveGameManager

        class BrokenFactionManager:
            def to_dict(self):
                raise TypeError("Cannot serialize!")

        manager = SaveGameManager(save_dir=str(tmp_path))
        broken_fm = BrokenFactionManager()

        result = manager.save_game(slot=1, faction_manager=broken_fm)

        assert result is True

    def test_save_with_broken_skill_xp_manager(self, tmp_path):
        """Test saving with skill_xp_manager that fails."""
        from save_load import SaveGameManager

        class BrokenSkillXPManager:
            def to_dict(self):
                raise AttributeError("Failed!")

        manager = SaveGameManager(save_dir=str(tmp_path))

        result = manager.save_game(slot=1, skill_xp_manager=BrokenSkillXPManager())

        assert result is True

    def test_save_with_broken_inventory(self, tmp_path):
        """Test saving with inventory that raises exception."""
        from save_load import SaveGameManager

        class BrokenInventory:
            def to_dict(self):
                raise TypeError("Error!")

        manager = SaveGameManager(save_dir=str(tmp_path))

        result = manager.save_game(slot=1, inventory=BrokenInventory())

        assert result is True

    def test_save_with_broken_world_map(self, tmp_path):
        """Test saving with world map that fails to serialize."""
        from save_load import SaveGameManager

        class BrokenWorldMap:
            def to_dict(self):
                raise AttributeError("Map error!")

        manager = SaveGameManager(save_dir=str(tmp_path))

        result = manager.save_game(slot=1, world_map=BrokenWorldMap())

        assert result is True

    def test_save_with_broken_cyberware_manager(self, tmp_path):
        """Test saving with cyberware manager that fails."""
        from save_load import SaveGameManager

        class BrokenCyberwareManager:
            def to_dict(self):
                raise TypeError("Cyber error!")

        manager = SaveGameManager(save_dir=str(tmp_path))

        result = manager.save_game(slot=1, cyberware_manager=BrokenCyberwareManager())

        assert result is True


class TestQuestManagerWithoutQuests:
    """Test quest manager edge cases."""

    def test_quest_manager_without_quests_attribute(self, tmp_path):
        """Test quest manager without quests attribute."""
        from save_load import SaveGameManager

        class QuestManagerNoQuests:
            def to_dict(self):
                return {"quests": {}}

        manager = SaveGameManager(save_dir=str(tmp_path))
        qm = QuestManagerNoQuests()

        result = manager.save_game(slot=1, quest_manager=qm)

        assert result is True

    def test_quest_manager_with_none_quests(self, tmp_path):
        """Test quest manager with None quests."""
        from save_load import SaveGameManager

        class QuestManagerNoneQuests:
            quests = None
            def to_dict(self):
                return {"quests": {}}

        manager = SaveGameManager(save_dir=str(tmp_path))

        result = manager.save_game(slot=1, quest_manager=QuestManagerNoneQuests())

        assert result is True


class TestLoadErrors:
    """Test error handling during load operations."""

    def test_load_nonexistent_slot(self, tmp_path):
        """Test loading from slot that doesn't exist."""
        from save_load import SaveGameManager
        import pytest

        manager = SaveGameManager(save_dir=str(tmp_path))

        with pytest.raises(ValueError, match="Invalid save slot"):
            manager.load_game(slot=99)

    def test_load_corrupted_json(self, tmp_path):
        """Test loading corrupted save file."""
        from save_load import SaveGameManager
        import json

        manager = SaveGameManager(save_dir=str(tmp_path))

        # Create corrupted save file
        save_path = tmp_path / "save_slot_1.json"
        with open(save_path, 'w') as f:
            f.write("{ invalid json }")

        result = manager.load_game(slot=1)

        assert result is None

    def test_load_autosave_not_exists(self, tmp_path):
        """Test loading autosave when it doesn't exist."""
        from save_load import SaveGameManager

        manager = SaveGameManager(save_dir=str(tmp_path))

        result = manager.load_autosave()

        assert result is None


class TestDeleteOperations:
    """Test delete operations."""

    def test_delete_nonexistent_save(self, tmp_path):
        """Test deleting save that doesn't exist."""
        from save_load import SaveGameManager

        manager = SaveGameManager(save_dir=str(tmp_path))

        result = manager.delete_save(slot=99)

        assert result is False

    def test_delete_autosave_not_exists(self, tmp_path):
        """Test deleting autosave when it doesn't exist."""
        from save_load import SaveGameManager

        manager = SaveGameManager(save_dir=str(tmp_path))

        result = manager.delete_autosave()

        assert result is False


class TestSaveMetadata:
    """Test save metadata functionality."""

    def test_get_save_metadata_nonexistent(self, tmp_path):
        """Test getting metadata for nonexistent save."""
        from save_load import SaveGameManager
        import pytest

        manager = SaveGameManager(save_dir=str(tmp_path))

        with pytest.raises(ValueError, match="Invalid save slot"):
            manager.get_save_metadata(slot=99)

    def test_get_save_metadata_corrupted(self, tmp_path):
        """Test getting metadata from corrupted save."""
        from save_load import SaveGameManager

        manager = SaveGameManager(save_dir=str(tmp_path))

        # Create corrupted file
        save_path = tmp_path / "save_slot_1.json"
        with open(save_path, 'w') as f:
            f.write("corrupted")

        metadata = manager.get_save_metadata(slot=1)

        assert metadata is None
