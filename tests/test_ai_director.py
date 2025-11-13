"""
Tests for AI Director System
Tests dynamic difficulty adjustment and game pacing
"""

import pytest
from game.ai_director import (
    AIDirector,
    DifficultyLevel,
    GameState,
    DIFFICULTY_LEVELS,
    PACING_STATES
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def ai_director():
    """Create an AI director."""
    return AIDirector()


@pytest.fixture
def game_state():
    """Create a game state."""
    return GameState(
        player_level=5,
        recent_deaths=0,
        recent_victories=3,
        time_since_combat=120,
        current_health_percentage=80
    )


# ============================================================================
# TEST AI DIRECTOR CREATION
# ============================================================================

class TestAIDirectorCreation:
    """Test AI director initialization."""

    def test_ai_director_creation(self, ai_director):
        """Test creating an AI director."""
        assert ai_director.current_difficulty == "normal"
        assert ai_director.tension_level == 0

    def test_difficulty_levels_valid(self):
        """Test all difficulty levels are valid."""
        for level in DIFFICULTY_LEVELS:
            director = AIDirector(initial_difficulty=level)
            assert director.current_difficulty == level


# ============================================================================
# TEST DIFFICULTY ADJUSTMENT
# ============================================================================

class TestDifficultyAdjustment:
    """Test dynamic difficulty adjustment."""

    def test_increase_difficulty_on_success(self, ai_director, game_state):
        """Test difficulty increases after player victories."""
        game_state.recent_victories = 5
        game_state.recent_deaths = 0

        ai_director.adjust_difficulty(game_state)

        assert ai_director.tension_level > 0

    def test_decrease_difficulty_on_failure(self, ai_director, game_state):
        """Test difficulty decreases after player deaths."""
        game_state.recent_deaths = 3
        game_state.recent_victories = 0

        ai_director.adjust_difficulty(game_state)

        # Tension should decrease or difficulty should lower
        assert ai_director.current_difficulty in ["easy", "normal"]

    def test_maintain_difficulty_balanced(self, ai_director, game_state):
        """Test difficulty maintains when balanced."""
        game_state.recent_victories = 2
        game_state.recent_deaths = 1

        initial_difficulty = ai_director.current_difficulty
        ai_director.adjust_difficulty(game_state)

        assert ai_director.current_difficulty == initial_difficulty


# ============================================================================
# TEST PACING
# ============================================================================

class TestPacing:
    """Test game pacing control."""

    def test_recommend_combat_after_downtime(self, ai_director):
        """Test recommends combat after long downtime."""
        recommendation = ai_director.recommend_pacing(time_since_combat=300)

        assert recommendation in ["combat", "intense"]

    def test_recommend_rest_after_combat(self, ai_director):
        """Test recommends rest after recent combat."""
        recommendation = ai_director.recommend_pacing(time_since_combat=10)

        assert recommendation in ["exploration", "calm"]

    def test_pacing_considers_player_health(self, ai_director, game_state):
        """Test pacing considers player health."""
        game_state.current_health_percentage = 20  # Low health

        recommendation = ai_director.recommend_pacing_with_state(game_state)

        # Should recommend calm/rest when low health
        assert recommendation in ["calm", "exploration"]


# ============================================================================
# TEST ENCOUNTER SCALING
# ============================================================================

class TestEncounterScaling:
    """Test encounter difficulty scaling."""

    def test_scale_encounter_easy(self, ai_director):
        """Test scaling encounter for easy difficulty."""
        ai_director.current_difficulty = "easy"

        scaled = ai_director.scale_encounter(
            base_enemies=3,
            base_difficulty=5
        )

        assert scaled["enemy_count"] < 3 or scaled["difficulty"] < 5

    def test_scale_encounter_hard(self, ai_director):
        """Test scaling encounter for hard difficulty."""
        ai_director.current_difficulty = "hard"

        scaled = ai_director.scale_encounter(
            base_enemies=3,
            base_difficulty=5
        )

        assert scaled["enemy_count"] >= 3 or scaled["difficulty"] > 5

    def test_scale_encounter_tension(self, ai_director):
        """Test high tension increases encounter difficulty."""
        ai_director.tension_level = 80

        scaled = ai_director.scale_encounter(
            base_enemies=2,
            base_difficulty=3
        )

        assert scaled["difficulty"] > 3


# ============================================================================
# TEST TENSION SYSTEM
# ============================================================================

class TestTensionSystem:
    """Test tension tracking."""

    def test_tension_increases_on_victory(self, ai_director):
        """Test tension increases after victories."""
        initial_tension = ai_director.tension_level

        ai_director.on_combat_victory()

        assert ai_director.tension_level > initial_tension

    def test_tension_decreases_on_death(self, ai_director):
        """Test tension decreases after deaths."""
        ai_director.tension_level = 50

        ai_director.on_player_death()

        assert ai_director.tension_level < 50

    def test_tension_capped_at_100(self, ai_director):
        """Test tension cannot exceed 100."""
        ai_director.tension_level = 95

        for _ in range(10):
            ai_director.on_combat_victory()

        assert ai_director.tension_level <= 100


# ============================================================================
# TEST SERIALIZATION
# ============================================================================

class TestAIDirectorSerialization:
    """Test AI director serialization."""

    def test_ai_director_serialization(self, ai_director):
        """Test AI director to_dict and from_dict."""
        ai_director.tension_level = 50
        ai_director.current_difficulty = "hard"

        data = ai_director.to_dict()
        restored = AIDirector.from_dict(data)

        assert restored.tension_level == 50
        assert restored.current_difficulty == "hard"


# ============================================================================
# TEST EDGE CASES
# ============================================================================

class TestAIDirectorEdgeCases:
    """Test edge cases."""

    def test_negative_tension(self, ai_director):
        """Test tension cannot go negative."""
        ai_director.tension_level = 5

        for _ in range(10):
            ai_director.on_player_death()

        assert ai_director.tension_level >= 0

    def test_invalid_difficulty_defaults(self):
        """Test invalid difficulty defaults to normal."""
        director = AIDirector(initial_difficulty="invalid")

        assert director.current_difficulty == "normal"
