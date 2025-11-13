"""
Comprehensive test suite for quest.py

Tests cover:
- Quest creation and initialization
- Objective types and completion
- Quest state transitions
- Reward distribution
- Prerequisites and unlocking
- Quest validation
"""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add game directory to path
game_dir = Path(__file__).parent.parent / "game"
sys.path.insert(0, str(game_dir))


class TestQuestInitialization:
    """Test quest creation and initialization."""

    def test_quest_creation_basic(self):
        """Test basic quest creation."""
        from quest import Quest, Rewards

        quest = Quest(
            quest_id="q001",
            title="Test Quest",
            description="A test quest",
            quest_type="main",
            objectives=[],
            rewards=Rewards(xp=100, credits=50),
            district="watson"
        )

        assert quest.quest_id == "q001"
        assert quest.title == "Test Quest"
        assert quest.quest_type == "main"
        assert quest.status == "available"
        assert quest.district == "watson"

    def test_quest_with_objectives(self):
        """Test quest with objectives."""
        from quest import Quest, Rewards, DefeatEnemies

        objectives = [DefeatEnemies("gang_grunt", count=5)]

        quest = Quest(
            quest_id="q002",
            title="Clear the Hideout",
            description="Defeat all gang members",
            quest_type="side",
            objectives=objectives,
            rewards=Rewards(xp=200),
            district="watson"
        )

        assert len(quest.objectives) == 1
        assert quest.objectives[0].objective_type == "defeat_enemies"

    def test_quest_with_prerequisites(self):
        """Test quest with prerequisites."""
        from quest import Quest, Rewards

        quest = Quest(
            quest_id="q003",
            title="Advanced Quest",
            description="Requires completing q001",
            quest_type="main",
            objectives=[],
            rewards=Rewards(xp=300),
            prerequisites=["q001", "q002"],
            district="city_center"
        )

        assert len(quest.prerequisites) == 2
        assert "q001" in quest.prerequisites


class TestQuestObjectives:
    """Test different objective types."""

    def test_defeat_enemies_objective(self):
        """Test defeat enemies objective."""
        from quest import DefeatEnemies

        obj = DefeatEnemies("gang_grunt", count=5)

        assert obj.enemy_type == "gang_grunt"
        assert obj.target_count == 5
        assert obj.current_count == 0
        assert obj.is_complete() is False

    def test_defeat_enemies_progress(self):
        """Test defeating enemies increments count."""
        from quest import DefeatEnemies

        obj = DefeatEnemies("gang_grunt", count=3)

        obj.update_progress("gang_grunt")
        assert obj.current_count == 1

        obj.update_progress("gang_grunt")
        assert obj.current_count == 2

        obj.update_progress("gang_grunt")
        assert obj.current_count == 3
        assert obj.is_complete() is True

    def test_defeat_enemies_wrong_type(self):
        """Test that wrong enemy type doesn't count."""
        from quest import DefeatEnemies

        obj = DefeatEnemies("gang_grunt", count=3)

        obj.update_progress("elite_soldier")
        assert obj.current_count == 0

    def test_go_to_location_objective(self):
        """Test go to location objective."""
        from quest import GoToLocation

        obj = GoToLocation("tyger_claw_hideout")

        assert obj.target_location == "tyger_claw_hideout"
        assert obj.is_complete() is False

        obj.update_progress("tyger_claw_hideout")
        assert obj.is_complete() is True

    def test_survive_combat_objective(self):
        """Test survive combat objective."""
        from quest import SurviveCombat

        obj = SurviveCombat(require_all_alive=True)

        assert obj.require_all_alive is True
        assert obj.is_complete() is False

        # Survive with all alive
        obj.update_progress(all_alive=True)
        assert obj.is_complete() is True

    def test_survive_combat_casualties_allowed(self):
        """Test survive combat with casualties allowed."""
        from quest import SurviveCombat

        obj = SurviveCombat(require_all_alive=False)

        # Survive with casualties
        obj.update_progress(all_alive=False)
        assert obj.is_complete() is True

    def test_collect_items_objective(self):
        """Test collect items objective."""
        from quest import CollectItems

        obj = CollectItems("data_shard", count=3)

        assert obj.item_type == "data_shard"
        assert obj.target_count == 3
        assert obj.current_count == 0

        obj.update_progress("data_shard", amount=2)
        assert obj.current_count == 2

        obj.update_progress("data_shard", amount=1)
        assert obj.current_count == 3
        assert obj.is_complete() is True


class TestQuestStateTransitions:
    """Test quest state changes."""

    def test_activate_quest(self):
        """Test activating an available quest."""
        from quest import Quest, Rewards

        quest = Quest(
            quest_id="q001",
            title="Test",
            description="Test",
            quest_type="main",
            objectives=[],
            rewards=Rewards(xp=100),
            district="watson"
        )

        assert quest.status == "available"

        quest.activate()
        assert quest.status == "active"

    def test_cannot_activate_completed_quest(self):
        """Test that completed quests can't be reactivated."""
        from quest import Quest, Rewards

        quest = Quest(
            quest_id="q001",
            title="Test",
            description="Test",
            quest_type="main",
            objectives=[],
            rewards=Rewards(xp=100),
            district="watson"
        )

        quest.activate()
        quest.complete()

        assert quest.status == "completed"

        # Try to activate again
        result = quest.activate()
        assert result is False
        assert quest.status == "completed"

    def test_complete_quest(self):
        """Test completing a quest."""
        from quest import Quest, Rewards

        quest = Quest(
            quest_id="q001",
            title="Test",
            description="Test",
            quest_type="main",
            objectives=[],
            rewards=Rewards(xp=100),
            district="watson"
        )

        quest.activate()
        quest.complete()

        assert quest.status == "completed"

    def test_fail_quest(self):
        """Test failing a quest."""
        from quest import Quest, Rewards

        quest = Quest(
            quest_id="q001",
            title="Test",
            description="Test",
            quest_type="main",
            objectives=[],
            rewards=Rewards(xp=100),
            district="watson"
        )

        quest.activate()
        quest.fail()

        assert quest.status == "failed"

    def test_check_completion_all_objectives(self):
        """Test quest auto-completes when all objectives done."""
        from quest import Quest, Rewards, DefeatEnemies

        obj = DefeatEnemies("grunt", count=2)

        quest = Quest(
            quest_id="q001",
            title="Test",
            description="Test",
            quest_type="main",
            objectives=[obj],
            rewards=Rewards(xp=100),
            district="watson"
        )

        quest.activate()

        # Complete objectives
        obj.update_progress("grunt")
        obj.update_progress("grunt")

        # Check if quest ready to complete
        assert quest.all_objectives_complete() is True


class TestQuestRewards:
    """Test reward distribution."""

    def test_rewards_creation(self):
        """Test creating rewards."""
        from quest import Rewards

        rewards = Rewards(
            xp=500,
            credits=1000,
            items=["medkit", "assault_rifle"],
            reputation={"fixers": 10, "corpo": -5}
        )

        assert rewards.xp == 500
        assert rewards.credits == 1000
        assert len(rewards.items) == 2
        assert rewards.reputation["fixers"] == 10

    def test_rewards_default_values(self):
        """Test rewards with default values."""
        from quest import Rewards

        rewards = Rewards(xp=100)

        assert rewards.xp == 100
        assert rewards.credits == 0
        assert rewards.items == []
        assert rewards.reputation == {}

    def test_get_rewards(self):
        """Test retrieving rewards from quest."""
        from quest import Quest, Rewards

        rewards = Rewards(xp=500, credits=1000)

        quest = Quest(
            quest_id="q001",
            title="Test",
            description="Test",
            quest_type="main",
            objectives=[],
            rewards=rewards,
            district="watson"
        )

        quest_rewards = quest.get_rewards()
        assert quest_rewards.xp == 500
        assert quest_rewards.credits == 1000


class TestQuestPrerequisites:
    """Test quest prerequisites and unlocking."""

    def test_check_prerequisites_met(self):
        """Test checking if prerequisites are met."""
        from quest import Quest, Rewards

        quest = Quest(
            quest_id="q003",
            title="Advanced",
            description="Test",
            quest_type="main",
            objectives=[],
            rewards=Rewards(xp=100),
            prerequisites=["q001", "q002"],
            district="watson"
        )

        completed = ["q001", "q002"]
        assert quest.check_prerequisites(completed) is True

    def test_check_prerequisites_not_met(self):
        """Test prerequisites not met."""
        from quest import Quest, Rewards

        quest = Quest(
            quest_id="q003",
            title="Advanced",
            description="Test",
            quest_type="main",
            objectives=[],
            rewards=Rewards(xp=100),
            prerequisites=["q001", "q002"],
            district="watson"
        )

        completed = ["q001"]  # Missing q002
        assert quest.check_prerequisites(completed) is False

    def test_no_prerequisites(self):
        """Test quest with no prerequisites."""
        from quest import Quest, Rewards

        quest = Quest(
            quest_id="q001",
            title="Starter",
            description="Test",
            quest_type="main",
            objectives=[],
            rewards=Rewards(xp=100),
            district="watson"
        )

        assert quest.check_prerequisites([]) is True


class TestQuestManager:
    """Test quest management system."""

    def test_quest_manager_creation(self):
        """Test creating quest manager."""
        from quest import QuestManager

        manager = QuestManager()

        assert manager is not None
        assert len(manager.quests) == 0
        assert len(manager.active_quests) == 0
        assert len(manager.completed_quests) == 0

    def test_add_quest(self):
        """Test adding quest to manager."""
        from quest import QuestManager, Quest, Rewards

        manager = QuestManager()

        quest = Quest(
            quest_id="q001",
            title="Test",
            description="Test",
            quest_type="main",
            objectives=[],
            rewards=Rewards(xp=100),
            district="watson"
        )

        manager.add_quest(quest)
        assert len(manager.quests) == 1
        assert "q001" in manager.quests

    def test_activate_quest_via_manager(self):
        """Test activating quest through manager."""
        from quest import QuestManager, Quest, Rewards

        manager = QuestManager()

        quest = Quest(
            quest_id="q001",
            title="Test",
            description="Test",
            quest_type="main",
            objectives=[],
            rewards=Rewards(xp=100),
            district="watson"
        )

        manager.add_quest(quest)
        manager.activate_quest("q001")

        assert len(manager.active_quests) == 1
        assert quest.status == "active"

    def test_complete_quest_via_manager(self):
        """Test completing quest through manager."""
        from quest import QuestManager, Quest, Rewards

        manager = QuestManager()

        quest = Quest(
            quest_id="q001",
            title="Test",
            description="Test",
            quest_type="main",
            objectives=[],
            rewards=Rewards(xp=100),
            district="watson"
        )

        manager.add_quest(quest)
        manager.activate_quest("q001")
        rewards = manager.complete_quest("q001")

        assert len(manager.active_quests) == 0
        assert len(manager.completed_quests) == 1
        assert quest.status == "completed"
        assert rewards.xp == 100

    def test_get_available_quests(self):
        """Test getting available quests."""
        from quest import QuestManager, Quest, Rewards

        manager = QuestManager()

        q1 = Quest("q001", "Test 1", "Test", "main", [], Rewards(xp=100), district="watson")
        q2 = Quest("q002", "Test 2", "Test", "side", [], Rewards(xp=100), district="watson")
        q3 = Quest("q003", "Test 3", "Test", "main", [], Rewards(xp=100),
                   prerequisites=["q001"], district="watson")

        manager.add_quest(q1)
        manager.add_quest(q2)
        manager.add_quest(q3)

        # Before completing q001
        available = manager.get_available_quests()
        assert len(available) == 2  # q1, q2 (q3 locked)

        # After completing q001
        manager.activate_quest("q001")
        manager.complete_quest("q001")

        available = manager.get_available_quests()
        assert len(available) == 2  # q2, q3 (q1 completed)


class TestQuestIntegration:
    """Integration tests for complete quest flows."""

    def test_complete_quest_flow(self):
        """Test complete quest from start to finish."""
        from quest import Quest, Rewards, DefeatEnemies, QuestManager

        # Create quest
        obj = DefeatEnemies("gang_grunt", count=3)

        quest = Quest(
            quest_id="q001",
            title="Clear Hideout",
            description="Defeat 3 gang members",
            quest_type="main",
            objectives=[obj],
            rewards=Rewards(xp=500, credits=1000),
            district="watson"
        )

        # Manage via QuestManager
        manager = QuestManager()
        manager.add_quest(quest)
        manager.activate_quest("q001")

        # Complete objectives
        obj.update_progress("gang_grunt")
        obj.update_progress("gang_grunt")
        obj.update_progress("gang_grunt")

        # Complete quest
        assert quest.all_objectives_complete() is True
        rewards = manager.complete_quest("q001")

        assert rewards.xp == 500
        assert rewards.credits == 1000
        assert quest.status == "completed"

    def test_multiple_objectives_quest(self):
        """Test quest with multiple objectives."""
        from quest import Quest, Rewards, DefeatEnemies, GoToLocation

        obj1 = DefeatEnemies("gang_grunt", count=2)
        obj2 = GoToLocation("hideout")

        quest = Quest(
            quest_id="q001",
            title="Raid Hideout",
            description="Go to hideout and defeat enemies",
            quest_type="main",
            objectives=[obj1, obj2],
            rewards=Rewards(xp=500),
            district="watson"
        )

        quest.activate()

        # Complete first objective
        obj1.update_progress("gang_grunt")
        obj1.update_progress("gang_grunt")
        assert obj1.is_complete() is True
        assert quest.all_objectives_complete() is False  # Still need obj2

        # Complete second objective
        obj2.update_progress("hideout")
        assert obj2.is_complete() is True
        assert quest.all_objectives_complete() is True


@pytest.mark.integration
class TestQuestPersistence:
    """Test quest serialization for save/load."""

    def test_quest_to_dict(self):
        """Test converting quest to dictionary."""
        from quest import Quest, Rewards, DefeatEnemies

        obj = DefeatEnemies("grunt", count=5)

        quest = Quest(
            quest_id="q001",
            title="Test",
            description="Test quest",
            quest_type="main",
            objectives=[obj],
            rewards=Rewards(xp=100, credits=50),
            district="watson"
        )

        quest_dict = quest.to_dict()

        assert quest_dict["quest_id"] == "q001"
        assert quest_dict["title"] == "Test"
        assert quest_dict["status"] == "available"
        assert len(quest_dict["objectives"]) == 1

    def test_quest_from_dict(self):
        """Test loading quest from dictionary."""
        from quest import Quest

        quest_data = {
            "quest_id": "q001",
            "title": "Test",
            "description": "Test quest",
            "quest_type": "main",
            "objectives": [
                {
                    "type": "defeat_enemies",
                    "enemy_type": "grunt",
                    "target_count": 5,
                    "current_count": 2
                }
            ],
            "rewards": {
                "xp": 100,
                "credits": 50,
                "items": [],
                "reputation": {}
            },
            "status": "active",
            "district": "watson",
            "prerequisites": []
        }

        quest = Quest.from_dict(quest_data)

        assert quest.quest_id == "q001"
        assert quest.status == "active"
        assert len(quest.objectives) == 1
        assert quest.objectives[0].current_count == 2


class TestObjectiveBaseMethods:
    """Test base Objective class methods."""

    def test_objective_update_progress_not_implemented(self):
        """Test that base Objective.update_progress raises NotImplementedError."""
        from quest import Objective

        obj = Objective("test")

        with pytest.raises(NotImplementedError):
            obj.update_progress()

    def test_objective_to_dict_not_implemented(self):
        """Test that base Objective.to_dict raises NotImplementedError."""
        from quest import Objective

        obj = Objective("test")

        with pytest.raises(NotImplementedError):
            obj.to_dict()


class TestObjectiveDeserialization:
    """Test objective deserialization from dict."""

    def test_deserialize_defeat_enemies(self):
        """Test deserializing DefeatEnemies objective."""
        from quest import Objective

        data = {
            "type": "defeat_enemies",
            "enemy_type": "gang_grunt",
            "target_count": 5,
            "current_count": 2
        }

        obj = Objective.from_dict(data)

        assert obj.objective_type == "defeat_enemies"
        assert obj.current_count == 2

    def test_deserialize_go_to_location(self):
        """Test deserializing GoToLocation objective."""
        from quest import Objective

        data = {
            "type": "go_to_location",
            "target_location": "watson_hideout",
            "completed": True
        }

        obj = Objective.from_dict(data)

        assert obj.objective_type == "go_to_location"
        assert obj.completed is True

    def test_deserialize_survive_combat(self):
        """Test deserializing SurviveCombat objective."""
        from quest import Objective

        data = {
            "type": "survive_combat",
            "require_all_alive": True,
            "completed": False
        }

        obj = Objective.from_dict(data)

        assert obj.objective_type == "survive_combat"
        assert obj.completed is False

    def test_deserialize_collect_items(self):
        """Test deserializing CollectItems objective."""
        from quest import Objective

        data = {
            "type": "collect_items",
            "item_type": "tech_parts",
            "target_count": 10,
            "current_count": 5
        }

        obj = Objective.from_dict(data)

        assert obj.objective_type == "collect_items"
        assert obj.current_count == 5

    def test_deserialize_unknown_type(self):
        """Test deserializing unknown objective type raises error."""
        from quest import Objective

        data = {
            "type": "unknown_type",
            "some": "data"
        }

        with pytest.raises(ValueError, match="Unknown objective type"):
            Objective.from_dict(data)


class TestQuestManagerEdgeCases:
    """Test QuestManager edge cases."""

    def test_activate_quest_not_available(self):
        """Test activating quest that's not available."""
        from quest import QuestManager, Quest, DefeatEnemies, Rewards

        manager = QuestManager()
        quest = Quest(
            quest_id="q1",
            title="Quest",
            description="Desc",
            quest_type="main",
            objectives=[DefeatEnemies("grunt", 5)],
            rewards=Rewards(xp=100),
            district="watson"
        )

        manager.add_quest(quest)
        quest.status = "completed"  # Not available

        result = manager.activate_quest("q1")

        assert result is False

    def test_complete_quest_via_manager(self):
        """Test completing quest through manager."""
        from quest import QuestManager, Quest, DefeatEnemies, Rewards

        manager = QuestManager()
        quest = Quest(
            quest_id="q1",
            title="Quest",
            description="Desc",
            quest_type="main",
            objectives=[DefeatEnemies("grunt", 5)],
            rewards=Rewards(xp=100),
            district="watson"
        )

        manager.add_quest(quest)
        manager.activate_quest("q1")

        # Complete objective
        quest.objectives[0].current_count = 5
        quest.objectives[0].completed = True

        # Complete quest
        manager.complete_quest("q1")

        assert quest.status == "completed"



class TestQuestSerialization:
    """Test quest and quest manager serialization."""

    def test_quest_manager_serialization_round_trip(self):
        """Test serializing and deserializing quest manager."""
        from quest import QuestManager, Quest, DefeatEnemies, Rewards

        manager = QuestManager()
        quest = Quest(
            quest_id="q1",
            title="Test Quest",
            description="Test",
            quest_type="main",
            objectives=[DefeatEnemies("grunt", 5)],
            rewards=Rewards(xp=100, credits=50),
            district="watson"
        )

        manager.add_quest(quest)
        manager.activate_quest("q1")

        # Serialize
        data = manager.to_dict()

        # Deserialize
        manager2 = QuestManager.from_dict(data)

        assert "q1" in manager2.quests
        assert "q1" in manager2.active_quests


class TestRewardsSerialization:
    """Test Rewards serialization."""

    def test_rewards_to_dict(self):
        """Test Rewards serialization."""
        from quest import Rewards

        rewards = Rewards(xp=100, credits=50, items=["item1"], reputation={"corp": 10})

        data = rewards.to_dict()

        assert data["xp"] == 100
        assert data["credits"] == 50
        assert "item1" in data["items"]

    def test_rewards_from_dict(self):
        """Test Rewards deserialization."""
        from quest import Rewards

        data = {
            "xp": 200,
            "credits": 75,
            "items": ["item2", "item3"],
            "reputation": {"gang": -5}
        }

        rewards = Rewards.from_dict(data)

        assert rewards.xp == 200
        assert rewards.credits == 75
        assert len(rewards.items) == 2
