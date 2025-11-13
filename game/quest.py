"""
Neon Collapse - Quest System
Manages quests, objectives, and rewards
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field


# ============================================================================
# REWARDS
# ============================================================================

@dataclass
class Rewards:
    """Rewards for completing quests."""
    xp: int = 0
    credits: int = 0
    items: List[str] = field(default_factory=list)
    reputation: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert rewards to dictionary."""
        return {
            "xp": self.xp,
            "credits": self.credits,
            "items": self.items,
            "reputation": self.reputation
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Rewards':
        """Create rewards from dictionary."""
        return cls(
            xp=data.get("xp", 0),
            credits=data.get("credits", 0),
            items=data.get("items", []),
            reputation=data.get("reputation", {})
        )


# ============================================================================
# OBJECTIVES
# ============================================================================

class Objective:
    """Base class for quest objectives."""

    def __init__(self, objective_type: str):
        self.objective_type = objective_type
        self.completed = False

    def is_complete(self) -> bool:
        """Check if objective is complete."""
        return self.completed

    def update_progress(self, *args, **kwargs):
        """Update objective progress."""
        raise NotImplementedError

    def to_dict(self) -> Dict[str, Any]:
        """Convert objective to dictionary."""
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Objective':
        """Create objective from dictionary."""
        obj_type = data.get("type")

        if obj_type == "defeat_enemies":
            obj = DefeatEnemies(
                enemy_type=data["enemy_type"],
                count=data["target_count"]
            )
            obj.current_count = data.get("current_count", 0)
            return obj

        elif obj_type == "go_to_location":
            obj = GoToLocation(target_location=data["target_location"])
            obj.completed = data.get("completed", False)
            return obj

        elif obj_type == "survive_combat":
            obj = SurviveCombat(require_all_alive=data["require_all_alive"])
            obj.completed = data.get("completed", False)
            return obj

        elif obj_type == "collect_items":
            obj = CollectItems(
                item_type=data["item_type"],
                count=data["target_count"]
            )
            obj.current_count = data.get("current_count", 0)
            return obj

        else:
            raise ValueError(f"Unknown objective type: {obj_type}")


class DefeatEnemies(Objective):
    """Objective: Defeat X enemies of type Y."""

    def __init__(self, enemy_type: str, count: int):
        super().__init__("defeat_enemies")
        self.enemy_type = enemy_type
        self.target_count = count
        self.current_count = 0

    def update_progress(self, defeated_enemy_type: str, **kwargs):
        """Update progress when enemy is defeated."""
        if defeated_enemy_type == self.enemy_type:
            self.current_count += 1

            if self.current_count >= self.target_count:
                self.completed = True

    def is_complete(self) -> bool:
        """Check if enough enemies defeated."""
        return self.current_count >= self.target_count

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": "defeat_enemies",
            "enemy_type": self.enemy_type,
            "target_count": self.target_count,
            "current_count": self.current_count
        }


class GoToLocation(Objective):
    """Objective: Go to a specific location."""

    def __init__(self, target_location: str):
        super().__init__("go_to_location")
        self.target_location = target_location

    def update_progress(self, current_location: str, **kwargs):
        """Update progress when location is reached."""
        if current_location == self.target_location:
            self.completed = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": "go_to_location",
            "target_location": self.target_location,
            "completed": self.completed
        }


class SurviveCombat(Objective):
    """Objective: Survive a combat encounter."""

    def __init__(self, require_all_alive: bool = False):
        super().__init__("survive_combat")
        self.require_all_alive = require_all_alive

    def update_progress(self, all_alive: bool, **kwargs):
        """Update progress after combat."""
        if self.require_all_alive:
            if all_alive:
                self.completed = True
        else:
            # Just need to survive, casualties OK
            self.completed = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": "survive_combat",
            "require_all_alive": self.require_all_alive,
            "completed": self.completed
        }


class CollectItems(Objective):
    """Objective: Collect X items of type Y."""

    def __init__(self, item_type: str, count: int):
        super().__init__("collect_items")
        self.item_type = item_type
        self.target_count = count
        self.current_count = 0

    def update_progress(self, collected_item_type: str, amount: int = 1, **kwargs):
        """Update progress when items are collected."""
        if collected_item_type == self.item_type:
            self.current_count += amount

            if self.current_count >= self.target_count:
                self.completed = True

    def is_complete(self) -> bool:
        """Check if enough items collected."""
        return self.current_count >= self.target_count

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": "collect_items",
            "item_type": self.item_type,
            "target_count": self.target_count,
            "current_count": self.current_count
        }


# ============================================================================
# QUEST
# ============================================================================

class Quest:
    """Represents a quest with objectives and rewards."""

    def __init__(
        self,
        quest_id: str,
        title: str,
        description: str,
        quest_type: str,
        objectives: List[Objective],
        rewards: Rewards,
        district: str,
        prerequisites: Optional[List[str]] = None
    ):
        self.quest_id = quest_id
        self.title = title
        self.description = description
        self.quest_type = quest_type  # 'main', 'side', 'contract'
        self.objectives = objectives
        self.rewards = rewards
        self.district = district
        self.prerequisites = prerequisites or []
        self.status = "available"  # 'available', 'active', 'completed', 'failed'

    def activate(self) -> bool:
        """Activate the quest."""
        if self.status == "available":
            self.status = "active"
            return True
        return False

    def complete(self):
        """Mark quest as completed."""
        self.status = "completed"

    def fail(self):
        """Mark quest as failed."""
        self.status = "failed"

    def all_objectives_complete(self) -> bool:
        """Check if all objectives are complete."""
        return all(obj.is_complete() for obj in self.objectives)

    def get_rewards(self) -> Rewards:
        """Get quest rewards."""
        return self.rewards

    def check_prerequisites(self, completed_quests: List[str]) -> bool:
        """Check if prerequisites are met."""
        if not self.prerequisites:
            return True

        return all(prereq in completed_quests for prereq in self.prerequisites)

    def to_dict(self) -> Dict[str, Any]:
        """Convert quest to dictionary for saving."""
        return {
            "quest_id": self.quest_id,
            "title": self.title,
            "description": self.description,
            "quest_type": self.quest_type,
            "objectives": [obj.to_dict() for obj in self.objectives],
            "rewards": self.rewards.to_dict(),
            "status": self.status,
            "district": self.district,
            "prerequisites": self.prerequisites
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Quest':
        """Create quest from dictionary."""
        # Reconstruct objectives
        objectives = [Objective.from_dict(obj_data) for obj_data in data["objectives"]]

        # Reconstruct rewards
        rewards = Rewards.from_dict(data["rewards"])

        # Create quest
        quest = cls(
            quest_id=data["quest_id"],
            title=data["title"],
            description=data["description"],
            quest_type=data["quest_type"],
            objectives=objectives,
            rewards=rewards,
            district=data["district"],
            prerequisites=data.get("prerequisites", [])
        )

        # Restore status
        quest.status = data.get("status", "available")

        return quest


# ============================================================================
# QUEST MANAGER
# ============================================================================

class QuestManager:
    """Manages all quests in the game."""

    def __init__(self):
        self.quests: Dict[str, Quest] = {}
        self.active_quests: List[str] = []
        self.completed_quests: List[str] = []

    def add_quest(self, quest: Quest):
        """Add a quest to the manager."""
        self.quests[quest.quest_id] = quest

    def activate_quest(self, quest_id: str) -> bool:
        """Activate a quest."""
        if quest_id not in self.quests:
            return False

        quest = self.quests[quest_id]

        if quest.activate():
            self.active_quests.append(quest_id)
            return True

        return False

    def complete_quest(self, quest_id: str) -> Optional[Rewards]:
        """Complete a quest and return rewards."""
        if quest_id not in self.quests:
            return None

        quest = self.quests[quest_id]

        if quest_id in self.active_quests:
            self.active_quests.remove(quest_id)

        quest.complete()
        self.completed_quests.append(quest_id)

        return quest.get_rewards()

    def fail_quest(self, quest_id: str):
        """Fail a quest."""
        if quest_id not in self.quests:
            return

        quest = self.quests[quest_id]

        if quest_id in self.active_quests:
            self.active_quests.remove(quest_id)

        quest.fail()

    def get_available_quests(self) -> List[Quest]:
        """Get all available quests (prerequisites met, not completed)."""
        available = []

        for quest in self.quests.values():
            if quest.status == "available":
                if quest.check_prerequisites(self.completed_quests):
                    available.append(quest)

        return available

    def get_active_quests(self) -> List[Quest]:
        """Get all active quests."""
        return [self.quests[quest_id] for quest_id in self.active_quests if quest_id in self.quests]

    def get_quest(self, quest_id: str) -> Optional[Quest]:
        """Get a specific quest by ID."""
        return self.quests.get(quest_id)

    def to_dict(self) -> Dict[str, Any]:
        """Convert quest manager to dictionary."""
        return {
            "quests": {qid: q.to_dict() for qid, q in self.quests.items()},
            "active_quests": self.active_quests,
            "completed_quests": self.completed_quests
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QuestManager':
        """Create quest manager from dictionary."""
        manager = cls()

        # Restore quests
        for quest_data in data["quests"].values():
            quest = Quest.from_dict(quest_data)
            manager.quests[quest.quest_id] = quest

        # Restore state
        manager.active_quests = data.get("active_quests", [])
        manager.completed_quests = data.get("completed_quests", [])

        return manager
