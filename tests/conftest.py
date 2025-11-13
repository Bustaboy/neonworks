"""
Pytest configuration and shared fixtures for Neon Collapse tests.

This module provides reusable fixtures for:
- Character creation and setup
- Combat scenarios
- UI components
- Mock pygame objects
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock
from typing import List

# Add game directory to Python path
game_dir = Path(__file__).parent.parent / "game"
sys.path.insert(0, str(game_dir))

import config
from character import Character
from combat import CombatEncounter


# ============================================================================
# CHARACTER FIXTURES
# ============================================================================

@pytest.fixture
def player_character():
    """Create a standard player character."""
    stats = {
        'body': 5,
        'reflexes': 6,
        'intelligence': 5,
        'tech': 5,
        'cool': 6,
        'max_hp': 150,
        'armor': 20
    }
    return Character(
        name="V",
        x=5,
        y=5,
        stats=stats,
        weapon='assault_rifle',
        team='player'
    )

@pytest.fixture
def ally_character():
    """Create an ally character."""
    stats = {
        'body': 6,
        'reflexes': 5,
        'intelligence': 4,
        'tech': 3,
        'cool': 5,
        'max_hp': 180,
        'armor': 25
    }
    return Character(
        name="Jackie",
        x=6,
        y=5,
        stats=stats,
        weapon='shotgun',
        team='player'
    )

@pytest.fixture
def enemy_character():
    """Create a standard enemy character."""
    stats = {
        'body': 4,
        'reflexes': 4,
        'intelligence': 2,
        'tech': 2,
        'cool': 3,
        'max_hp': 80,
        'armor': 10
    }
    return Character(
        name="Gang Grunt",
        x=15,
        y=5,
        stats=stats,
        weapon='pistol',
        team='enemy'
    )

@pytest.fixture
def elite_enemy():
    """Create an elite enemy character."""
    stats = {
        'body': 6,
        'reflexes': 6,
        'intelligence': 4,
        'tech': 4,
        'cool': 6,
        'max_hp': 150,
        'armor': 20
    }
    return Character(
        name="Gang Elite",
        x=16,
        y=6,
        stats=stats,
        weapon='assault_rifle',
        team='enemy'
    )

@pytest.fixture
def weak_character():
    """Create a weak character for testing edge cases."""
    stats = {
        'body': 1,
        'reflexes': 1,
        'intelligence': 1,
        'tech': 1,
        'cool': 1,
        'max_hp': 50,
        'armor': 0
    }
    return Character(
        name="Weakling",
        x=10,
        y=10,
        stats=stats,
        weapon='pistol',
        team='player'
    )

@pytest.fixture
def strong_character():
    """Create a strong character for testing edge cases."""
    stats = {
        'body': 10,
        'reflexes': 10,
        'intelligence': 10,
        'tech': 10,
        'cool': 10,
        'max_hp': 300,
        'armor': 50
    }
    return Character(
        name="Tank",
        x=10,
        y=10,
        stats=stats,
        weapon='katana',
        team='player'
    )

@pytest.fixture
def melee_character():
    """Create a melee-focused character."""
    stats = {
        'body': 8,
        'reflexes': 6,
        'intelligence': 3,
        'tech': 3,
        'cool': 5,
        'max_hp': 200,
        'armor': 30
    }
    return Character(
        name="Melee Fighter",
        x=10,
        y=10,
        stats=stats,
        weapon='katana',
        team='player'
    )


# ============================================================================
# COMBAT FIXTURES
# ============================================================================

@pytest.fixture
def basic_combat_scenario(player_character, enemy_character):
    """Create a basic 1v1 combat scenario."""
    player_team = [player_character]
    enemy_team = [enemy_character]
    return player_team, enemy_team

@pytest.fixture
def team_combat_scenario(player_character, ally_character, enemy_character, elite_enemy):
    """Create a 2v2 team combat scenario."""
    player_team = [player_character, ally_character]
    enemy_team = [enemy_character, elite_enemy]
    return player_team, enemy_team

@pytest.fixture
def outnumbered_scenario(player_character, enemy_character):
    """Create an outnumbered scenario (1v2)."""
    player_team = [player_character]

    # Create second enemy
    stats = {
        'body': 4,
        'reflexes': 4,
        'intelligence': 2,
        'tech': 2,
        'cool': 3,
        'max_hp': 80,
        'armor': 10
    }
    enemy2 = Character(
        name="Gang Grunt 2",
        x=14,
        y=6,
        stats=stats,
        weapon='pistol',
        team='enemy'
    )

    enemy_team = [enemy_character, enemy2]
    return player_team, enemy_team

@pytest.fixture
def combat_encounter(basic_combat_scenario):
    """Create a combat encounter with basic scenario."""
    player_team, enemy_team = basic_combat_scenario
    return CombatEncounter(player_team, enemy_team)

@pytest.fixture
def team_combat_encounter(team_combat_scenario):
    """Create a combat encounter with team scenario."""
    player_team, enemy_team = team_combat_scenario
    return CombatEncounter(player_team, enemy_team)


# ============================================================================
# PYGAME/UI FIXTURES
# ============================================================================

@pytest.fixture
def mock_pygame():
    """Create mock pygame objects for UI testing."""
    mock = MagicMock()
    mock.display.set_mode.return_value = Mock()
    mock.font.Font.return_value = Mock()
    mock.time.Clock.return_value = Mock()
    mock.event.get.return_value = []
    mock.QUIT = 256
    mock.MOUSEBUTTONDOWN = 1025
    mock.KEYDOWN = 768
    mock.K_SPACE = 32
    mock.K_e = 101
    return mock

@pytest.fixture
def mock_screen():
    """Create a mock pygame screen surface."""
    screen = Mock()
    screen.fill = Mock()
    screen.blit = Mock()
    screen.get_width.return_value = config.SCREEN_WIDTH
    screen.get_height.return_value = config.SCREEN_HEIGHT
    return screen

@pytest.fixture
def mock_font():
    """Create a mock pygame font."""
    font = Mock()
    text_surface = Mock()
    text_surface.get_rect.return_value = Mock(x=0, y=0, width=100, height=20)
    font.render.return_value = text_surface
    return font


# ============================================================================
# UTILITY FIXTURES
# ============================================================================

@pytest.fixture
def grid_positions():
    """Provide common grid positions for testing."""
    return {
        'center': (config.GRID_WIDTH // 2, config.GRID_HEIGHT // 2),
        'top_left': (0, 0),
        'top_right': (config.GRID_WIDTH - 1, 0),
        'bottom_left': (0, config.GRID_HEIGHT - 1),
        'bottom_right': (config.GRID_WIDTH - 1, config.GRID_HEIGHT - 1),
    }

@pytest.fixture
def combat_log():
    """Create an empty combat log."""
    return []

@pytest.fixture(autouse=True)
def reset_random_seed():
    """Reset random seed before each test for reproducibility."""
    import random
    random.seed(42)
    yield
    random.seed()  # Reset after test


# ============================================================================
# PARAMETRIZE HELPERS
# ============================================================================

def generate_stat_combinations():
    """Generate test parameter combinations for different stat values."""
    return [
        (1, 1, 1, 1, 1),  # Minimum stats
        (5, 5, 5, 5, 5),  # Average stats
        (10, 10, 10, 10, 10),  # Maximum stats
        (10, 1, 1, 1, 1),  # High body only
        (1, 10, 1, 1, 1),  # High reflexes only
        (1, 1, 10, 1, 1),  # High intelligence only
        (1, 1, 1, 10, 1),  # High tech only
        (1, 1, 1, 1, 10),  # High cool only
    ]

def generate_weapon_types():
    """Generate test parameters for different weapon types."""
    return [
        ("Assault Rifle", 25, 8, 75, 10),
        ("Pistol", 20, 6, 80, 5),
        ("Shotgun", 40, 4, 70, 5),
        ("Katana", 30, 1, 85, 15),
    ]


# ============================================================================
# SESSION-WIDE FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def game_config():
    """Provide game configuration for testing."""
    return {
        'screen_width': config.SCREEN_WIDTH,
        'screen_height': config.SCREEN_HEIGHT,
        'grid_width': config.GRID_WIDTH,
        'grid_height': config.GRID_HEIGHT,
        'tile_size': config.TILE_SIZE,
        'max_ap': config.MAX_AP,
        'move_ap_cost': config.MOVE_AP_COST,
    }
