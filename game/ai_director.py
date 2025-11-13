"""
Neon Collapse - AI Director System
Manages dynamic difficulty adjustment and game pacing
"""

from typing import Dict, Any


# Constants
DIFFICULTY_LEVELS = ["easy", "normal", "hard", "extreme"]
PACING_STATES = ["calm", "exploration", "tension", "combat", "intense"]


# ============================================================================
# GAME STATE CLASS
# ============================================================================

class GameState:
    """Represents current game state for AI director."""

    def __init__(
        self,
        player_level: int,
        recent_deaths: int,
        recent_victories: int,
        time_since_combat: int,
        current_health_percentage: int
    ):
        self.player_level = player_level
        self.recent_deaths = recent_deaths
        self.recent_victories = recent_victories
        self.time_since_combat = time_since_combat
        self.current_health_percentage = current_health_percentage


# ============================================================================
# DIFFICULTY LEVEL CLASS
# ============================================================================

class DifficultyLevel:
    """Represents a difficulty level configuration."""

    def __init__(
        self,
        level_name: str,
        enemy_health_modifier: float,
        enemy_damage_modifier: float,
        loot_modifier: float
    ):
        self.level_name = level_name
        self.enemy_health_modifier = enemy_health_modifier
        self.enemy_damage_modifier = enemy_damage_modifier
        self.loot_modifier = loot_modifier


# Predefined difficulty configurations
DIFFICULTY_CONFIGS = {
    "easy": DifficultyLevel("easy", 0.8, 0.7, 1.2),
    "normal": DifficultyLevel("normal", 1.0, 1.0, 1.0),
    "hard": DifficultyLevel("hard", 1.3, 1.3, 0.9),
    "extreme": DifficultyLevel("extreme", 1.5, 1.5, 0.8)
}


# ============================================================================
# AI DIRECTOR CLASS
# ============================================================================

class AIDirector:
    """Manages dynamic difficulty and pacing."""

    def __init__(self, initial_difficulty: str = "normal"):
        # Validate difficulty
        if initial_difficulty not in DIFFICULTY_LEVELS:
            initial_difficulty = "normal"

        self.current_difficulty = initial_difficulty
        self.tension_level = 0  # 0-100
        self.victory_streak = 0
        self.death_streak = 0

    def adjust_difficulty(self, game_state: GameState):
        """
        Adjust difficulty based on player performance.

        Args:
            game_state: Current game state
        """
        # Calculate performance score
        performance = game_state.recent_victories - (game_state.recent_deaths * 2)

        # Adjust based on performance
        if performance > 3:
            # Player doing very well
            self._increase_tension(10)
            if self.tension_level > 70:
                self._increase_difficulty()

        elif performance < -2:
            # Player struggling
            self._decrease_tension(15)
            if self.tension_level < 20:
                self._decrease_difficulty()

    def _increase_difficulty(self):
        """Increase difficulty level."""
        current_index = DIFFICULTY_LEVELS.index(self.current_difficulty)
        if current_index < len(DIFFICULTY_LEVELS) - 1:
            self.current_difficulty = DIFFICULTY_LEVELS[current_index + 1]

    def _decrease_difficulty(self):
        """Decrease difficulty level."""
        current_index = DIFFICULTY_LEVELS.index(self.current_difficulty)
        if current_index > 0:
            self.current_difficulty = DIFFICULTY_LEVELS[current_index - 1]

    def _increase_tension(self, amount: int):
        """Increase tension level."""
        self.tension_level = min(100, self.tension_level + amount)

    def _decrease_tension(self, amount: int):
        """Decrease tension level."""
        self.tension_level = max(0, self.tension_level - amount)

    def recommend_pacing(self, time_since_combat: int) -> str:
        """
        Recommend pacing state.

        Args:
            time_since_combat: Seconds since last combat

        Returns:
            Recommended pacing state
        """
        if time_since_combat > 200:
            return "combat"
        elif time_since_combat > 100:
            return "tension"
        elif time_since_combat < 30:
            return "calm"
        else:
            return "exploration"

    def recommend_pacing_with_state(self, game_state: GameState) -> str:
        """
        Recommend pacing considering full game state.

        Args:
            game_state: Current game state

        Returns:
            Recommended pacing state
        """
        # Low health = calm/rest
        if game_state.current_health_percentage < 30:
            return "calm"

        # Recent deaths = exploration/recovery
        if game_state.recent_deaths > 2:
            return "exploration"

        # Otherwise use time-based
        return self.recommend_pacing(game_state.time_since_combat)

    def scale_encounter(
        self,
        base_enemies: int,
        base_difficulty: int
    ) -> Dict[str, Any]:
        """
        Scale an encounter based on current difficulty.

        Args:
            base_enemies: Base enemy count
            base_difficulty: Base difficulty level

        Returns:
            Scaled encounter parameters
        """
        config = DIFFICULTY_CONFIGS[self.current_difficulty]

        # Scale enemy count
        enemy_count = base_enemies
        if self.current_difficulty == "easy":
            enemy_count = max(1, base_enemies - 1)
        elif self.current_difficulty == "hard":
            enemy_count = base_enemies + 1
        elif self.current_difficulty == "extreme":
            enemy_count = base_enemies + 2

        # Scale difficulty
        difficulty = int(base_difficulty * config.enemy_damage_modifier)

        # Tension adds additional scaling
        if self.tension_level > 70:
            difficulty += 1

        return {
            "enemy_count": enemy_count,
            "difficulty": difficulty,
            "health_modifier": config.enemy_health_modifier,
            "loot_modifier": config.loot_modifier
        }

    def on_combat_victory(self):
        """Handle combat victory event."""
        self._increase_tension(15)
        self.victory_streak += 1
        self.death_streak = 0

    def on_player_death(self):
        """Handle player death event."""
        self._decrease_tension(20)
        self.death_streak += 1
        self.victory_streak = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "current_difficulty": self.current_difficulty,
            "tension_level": self.tension_level,
            "victory_streak": self.victory_streak,
            "death_streak": self.death_streak
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AIDirector':
        """Load from dictionary."""
        director = cls(initial_difficulty=data.get("current_difficulty", "normal"))
        director.tension_level = data.get("tension_level", 0)
        director.victory_streak = data.get("victory_streak", 0)
        director.death_streak = data.get("death_streak", 0)
        return director
