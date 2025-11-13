"""
Custom components for Simple RPG example.

This file demonstrates how to create custom components for your game.
Components are pure data containers with no logic.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict
from enum import Enum
from neonworks.core.ecs import Component


# ============================================================================
# Movement Components
# ============================================================================


@dataclass
class Velocity(Component):
    """
    Velocity component for moving entities.

    This component stores the current velocity of an entity.
    The MovementSystem uses this to update entity positions each frame.
    """

    dx: float = 0.0  # Horizontal velocity (pixels per second)
    dy: float = 0.0  # Vertical velocity (pixels per second)
    max_speed: float = 200.0  # Maximum movement speed


@dataclass
class PlayerController(Component):
    """
    Marks an entity as player-controlled.

    This is a configuration component that stores player-specific settings.
    The PlayerInputSystem looks for entities with this component.
    """

    speed: float = 200.0  # Movement speed in pixels per second
    attack_cooldown: float = 0.0  # Time until next attack is allowed


# ============================================================================
# Combat Components
# ============================================================================


@dataclass
class CombatStats(Component):
    """
    Combat statistics for entities that can fight.

    Stores attack damage and attack range. Used by the CombatSystem
    to calculate damage when entities attack each other.
    """

    attack_damage: int = 10  # Damage dealt per attack
    attack_range: float = 50.0  # Maximum distance for attacks
    attack_cooldown_duration: float = 1.0  # Seconds between attacks


# ============================================================================
# AI Components
# ============================================================================


class AIState(Enum):
    """AI state machine states."""

    IDLE = "idle"
    PATROL = "patrol"
    CHASE = "chase"
    ATTACK = "attack"


@dataclass
class AIController(Component):
    """
    AI behavior controller for enemy entities.

    This component defines how an enemy behaves. The AISystem reads this
    component and implements the state machine logic.

    State transitions:
    - IDLE -> CHASE: When player enters detection_range
    - CHASE -> ATTACK: When player enters attack_range
    - ATTACK -> CHASE: When player leaves attack_range
    - CHASE -> IDLE: When player leaves detection_range
    """

    state: AIState = AIState.IDLE
    detection_range: float = 200.0  # Distance at which enemy detects player
    movement_speed: float = 100.0  # How fast enemy moves when chasing
    target_entity_id: Optional[str] = (
        None  # ID of entity being targeted (usually player)
    )


# ============================================================================
# UI Components
# ============================================================================


@dataclass
class UIHealthBar(Component):
    """
    UI component for rendering a health bar above an entity.

    The UISystem looks for entities with both Health and UIHealthBar
    components and draws a health bar above them.
    """

    width: int = 40  # Width of health bar in pixels
    height: int = 4  # Height of health bar in pixels
    offset_y: int = -30  # Vertical offset from entity position
    show: bool = True  # Whether to show the health bar


# ============================================================================
# Game State Components
# ============================================================================


@dataclass
class GameStats(Component):
    """
    Tracks player game statistics.

    This component is attached to the player entity and tracks progress
    throughout the game.
    """

    enemies_defeated: int = 0  # Number of enemies killed
    score: int = 0  # Current score
    game_time: float = 0.0  # Time played in seconds


# ============================================================================
# Screen Management
# ============================================================================


class GameScreen(Enum):
    """Available game screens."""

    MENU = "menu"
    GAMEPLAY = "gameplay"
    GAME_OVER = "game_over"
    VICTORY = "victory"


@dataclass
class ScreenState(Component):
    """
    Tracks the current game screen.

    This component should be attached to a singleton entity that manages
    the current screen state.
    """

    current_screen: GameScreen = GameScreen.MENU
    previous_screen: Optional[GameScreen] = None

    def change_screen(self, new_screen: GameScreen):
        """Change to a new screen."""
        self.previous_screen = self.current_screen
        self.current_screen = new_screen
