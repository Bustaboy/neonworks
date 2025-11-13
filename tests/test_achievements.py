"""
Tests for Achievement System
Tests tracking player accomplishments, unlocking achievements, and rewards
"""

import pytest
from game.achievements import (
    Achievement,
    AchievementManager,
    AchievementProgress,
    ACHIEVEMENT_CATEGORIES,
    ACHIEVEMENT_TIERS
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def basic_achievement():
    """Create a basic achievement."""
    return Achievement(
        achievement_id="ach_first_kill",
        name="First Blood",
        description="Defeat your first enemy",
        category="combat",
        tier="bronze",
        requirement_type="kills",
        requirement_value=1,
        reward_credits=100,
        reward_xp=50
    )


@pytest.fixture
def progress_achievement():
    """Create a progress-based achievement."""
    return Achievement(
        achievement_id="ach_veteran",
        name="Veteran",
        description="Defeat 100 enemies",
        category="combat",
        tier="gold",
        requirement_type="kills",
        requirement_value=100,
        reward_credits=5000,
        reward_xp=1000
    )


@pytest.fixture
def achievement_manager():
    """Create an achievement manager."""
    return AchievementManager()


# ============================================================================
# TEST ACHIEVEMENT CREATION
# ============================================================================

class TestAchievementCreation:
    """Test achievement initialization."""

    def test_achievement_creation(self, basic_achievement):
        """Test creating an achievement."""
        assert basic_achievement.achievement_id == "ach_first_kill"
        assert basic_achievement.name == "First Blood"
        assert basic_achievement.tier == "bronze"
        assert basic_achievement.requirement_value == 1

    def test_achievement_categories_valid(self):
        """Test all achievement categories are valid."""
        for category in ACHIEVEMENT_CATEGORIES:
            ach = Achievement(
                achievement_id=f"ach_{category}",
                name=f"Test {category}",
                description="Test",
                category=category,
                tier="bronze",
                requirement_type="test",
                requirement_value=1
            )
            assert ach.category == category

    def test_achievement_tiers_valid(self):
        """Test all achievement tiers are valid."""
        for tier in ACHIEVEMENT_TIERS:
            ach = Achievement(
                achievement_id=f"ach_{tier}",
                name=f"Test {tier}",
                description="Test",
                category="general",
                tier=tier,
                requirement_type="test",
                requirement_value=1
            )
            assert ach.tier == tier


# ============================================================================
# TEST ACHIEVEMENT PROGRESS
# ============================================================================

class TestAchievementProgress:
    """Test achievement progress tracking."""

    def test_unlock_achievement(self, achievement_manager, basic_achievement):
        """Test unlocking an achievement."""
        achievement_manager.add_achievement(basic_achievement)
        achievement_manager.track_progress("kills", 1)

        assert achievement_manager.is_unlocked("ach_first_kill") is True

    def test_progress_tracking(self, achievement_manager, progress_achievement):
        """Test tracking progress toward achievement."""
        achievement_manager.add_achievement(progress_achievement)

        achievement_manager.track_progress("kills", 50)
        progress = achievement_manager.get_progress("ach_veteran")

        assert progress.current == 50
        assert progress.required == 100
        assert progress.percentage == 50.0

    def test_cannot_unlock_twice(self, achievement_manager, basic_achievement):
        """Test achievement can only be unlocked once."""
        achievement_manager.add_achievement(basic_achievement)
        achievement_manager.track_progress("kills", 1)
        achievement_manager.track_progress("kills", 10)  # Extra progress

        unlocked = achievement_manager.get_unlocked_achievements()
        assert len(unlocked) == 1

    def test_get_rewards_on_unlock(self, achievement_manager, basic_achievement):
        """Test receiving rewards when unlocking."""
        achievement_manager.add_achievement(basic_achievement)
        result = achievement_manager.track_progress("kills", 1)

        assert result["newly_unlocked"] == ["ach_first_kill"]
        assert result["rewards"]["credits"] == 100
        assert result["rewards"]["xp"] == 50


# ============================================================================
# TEST ACHIEVEMENT MANAGER
# ============================================================================

class TestAchievementManager:
    """Test achievement manager operations."""

    def test_add_achievement(self, achievement_manager, basic_achievement):
        """Test adding achievement."""
        achievement_manager.add_achievement(basic_achievement)

        assert len(achievement_manager.get_all_achievements()) == 1

    def test_get_achievements_by_category(
        self,
        achievement_manager,
        basic_achievement,
        progress_achievement
    ):
        """Test filtering achievements by category."""
        achievement_manager.add_achievement(basic_achievement)
        achievement_manager.add_achievement(progress_achievement)

        combat_achievements = achievement_manager.get_achievements_by_category("combat")

        assert len(combat_achievements) == 2

    def test_get_achievements_by_tier(self, achievement_manager, basic_achievement):
        """Test filtering achievements by tier."""
        achievement_manager.add_achievement(basic_achievement)

        bronze_achievements = achievement_manager.get_achievements_by_tier("bronze")

        assert len(bronze_achievements) == 1

    def test_get_completion_percentage(self, achievement_manager, basic_achievement):
        """Test calculating overall completion percentage."""
        achievement_manager.add_achievement(basic_achievement)
        achievement_manager.track_progress("kills", 1)

        percentage = achievement_manager.get_completion_percentage()

        assert percentage == 100.0


# ============================================================================
# TEST SERIALIZATION
# ============================================================================

class TestAchievementSerialization:
    """Test achievement serialization."""

    def test_achievement_serialization(self, basic_achievement):
        """Test achievement to_dict and from_dict."""
        data = basic_achievement.to_dict()
        restored = Achievement.from_dict(data)

        assert restored.achievement_id == basic_achievement.achievement_id
        assert restored.requirement_value == basic_achievement.requirement_value

    def test_achievement_manager_serialization(
        self,
        achievement_manager,
        basic_achievement
    ):
        """Test achievement manager serialization."""
        achievement_manager.add_achievement(basic_achievement)
        achievement_manager.track_progress("kills", 1)

        data = achievement_manager.to_dict()
        restored = AchievementManager.from_dict(data)

        assert restored.is_unlocked("ach_first_kill") is True
        assert len(restored.get_unlocked_achievements()) == 1


# ============================================================================
# TEST EDGE CASES
# ============================================================================

class TestAchievementEdgeCases:
    """Test edge cases."""

    def test_track_unknown_achievement_type(self, achievement_manager):
        """Test tracking progress for unknown type."""
        result = achievement_manager.track_progress("unknown_type", 1)

        assert result["newly_unlocked"] == []

    def test_negative_progress(self, achievement_manager, basic_achievement):
        """Test cannot track negative progress."""
        achievement_manager.add_achievement(basic_achievement)
        achievement_manager.track_progress("kills", -1)

        assert achievement_manager.is_unlocked("ach_first_kill") is False
