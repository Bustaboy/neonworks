"""
Neon Collapse - Achievement System
Tracks player accomplishments and unlocks rewards
"""

from typing import Dict, List, Any, Optional


# Constants
ACHIEVEMENT_CATEGORIES = ["combat", "exploration", "social", "hacking", "crafting", "general"]
ACHIEVEMENT_TIERS = ["bronze", "silver", "gold", "platinum"]


# ============================================================================
# ACHIEVEMENT PROGRESS CLASS
# ============================================================================

class AchievementProgress:
    """Tracks progress toward an achievement."""

    def __init__(self, current: int, required: int):
        self.current = current
        self.required = required

    @property
    def percentage(self) -> float:
        """Get completion percentage."""
        if self.required == 0:
            return 100.0
        return (self.current / self.required) * 100.0

    def is_complete(self) -> bool:
        """Check if progress is complete."""
        return self.current >= self.required


# ============================================================================
# ACHIEVEMENT CLASS
# ============================================================================

class Achievement:
    """Represents a player achievement."""

    def __init__(
        self,
        achievement_id: str,
        name: str,
        description: str,
        category: str,
        tier: str,
        requirement_type: str,
        requirement_value: int,
        reward_credits: int = 0,
        reward_xp: int = 0
    ):
        if category not in ACHIEVEMENT_CATEGORIES:
            raise ValueError(f"Invalid category: {category}")
        if tier not in ACHIEVEMENT_TIERS:
            raise ValueError(f"Invalid tier: {tier}")

        self.achievement_id = achievement_id
        self.name = name
        self.description = description
        self.category = category
        self.tier = tier
        self.requirement_type = requirement_type
        self.requirement_value = requirement_value
        self.reward_credits = reward_credits
        self.reward_xp = reward_xp

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "achievement_id": self.achievement_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "tier": self.tier,
            "requirement_type": self.requirement_type,
            "requirement_value": self.requirement_value,
            "reward_credits": self.reward_credits,
            "reward_xp": self.reward_xp
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Achievement':
        """Load from dictionary."""
        return cls(
            achievement_id=data["achievement_id"],
            name=data["name"],
            description=data["description"],
            category=data["category"],
            tier=data["tier"],
            requirement_type=data["requirement_type"],
            requirement_value=data["requirement_value"],
            reward_credits=data.get("reward_credits", 0),
            reward_xp=data.get("reward_xp", 0)
        )


# ============================================================================
# ACHIEVEMENT MANAGER CLASS
# ============================================================================

class AchievementManager:
    """Manages achievements and tracking."""

    def __init__(self):
        self.achievements: Dict[str, Achievement] = {}
        self.unlocked: List[str] = []
        self.progress: Dict[str, int] = {}  # requirement_type -> current_value

    def add_achievement(self, achievement: Achievement):
        """Add an achievement."""
        self.achievements[achievement.achievement_id] = achievement

    def get_all_achievements(self) -> List[Achievement]:
        """Get all achievements."""
        return list(self.achievements.values())

    def get_achievements_by_category(self, category: str) -> List[Achievement]:
        """Get achievements by category."""
        return [
            ach for ach in self.achievements.values()
            if ach.category == category
        ]

    def get_achievements_by_tier(self, tier: str) -> List[Achievement]:
        """Get achievements by tier."""
        return [
            ach for ach in self.achievements.values()
            if ach.tier == tier
        ]

    def is_unlocked(self, achievement_id: str) -> bool:
        """Check if achievement is unlocked."""
        return achievement_id in self.unlocked

    def get_unlocked_achievements(self) -> List[Achievement]:
        """Get all unlocked achievements."""
        return [
            self.achievements[ach_id]
            for ach_id in self.unlocked
            if ach_id in self.achievements
        ]

    def get_progress(self, achievement_id: str) -> AchievementProgress:
        """Get progress toward an achievement."""
        if achievement_id not in self.achievements:
            return AchievementProgress(0, 1)

        achievement = self.achievements[achievement_id]
        current = self.progress.get(achievement.requirement_type, 0)

        return AchievementProgress(current, achievement.requirement_value)

    def track_progress(
        self,
        requirement_type: str,
        value: int
    ) -> Dict[str, Any]:
        """
        Track progress and check for unlocks.

        Args:
            requirement_type: Type of progress (kills, quests, etc.)
            value: Progress amount

        Returns:
            Dict with newly unlocked achievements and rewards
        """
        # Ignore negative progress
        if value < 0:
            return {"newly_unlocked": [], "rewards": {"credits": 0, "xp": 0}}

        # Update progress
        if requirement_type not in self.progress:
            self.progress[requirement_type] = 0

        self.progress[requirement_type] += value

        # Check for unlocks
        newly_unlocked = []
        total_credits = 0
        total_xp = 0

        for achievement in self.achievements.values():
            # Skip if already unlocked
            if achievement.achievement_id in self.unlocked:
                continue

            # Skip if wrong requirement type
            if achievement.requirement_type != requirement_type:
                continue

            # Check if requirement met
            current = self.progress.get(requirement_type, 0)
            if current >= achievement.requirement_value:
                self.unlocked.append(achievement.achievement_id)
                newly_unlocked.append(achievement.achievement_id)
                total_credits += achievement.reward_credits
                total_xp += achievement.reward_xp

        return {
            "newly_unlocked": newly_unlocked,
            "rewards": {
                "credits": total_credits,
                "xp": total_xp
            }
        }

    def get_completion_percentage(self) -> float:
        """Get overall achievement completion percentage."""
        if not self.achievements:
            return 0.0

        return (len(self.unlocked) / len(self.achievements)) * 100.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "achievements": {
                ach_id: ach.to_dict()
                for ach_id, ach in self.achievements.items()
            },
            "unlocked": self.unlocked.copy(),
            "progress": self.progress.copy()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AchievementManager':
        """Load from dictionary."""
        manager = cls()

        # Restore achievements
        for ach_data in data.get("achievements", {}).values():
            achievement = Achievement.from_dict(ach_data)
            manager.achievements[achievement.achievement_id] = achievement

        # Restore unlocked
        manager.unlocked = data.get("unlocked", [])

        # Restore progress
        manager.progress = data.get("progress", {})

        return manager
