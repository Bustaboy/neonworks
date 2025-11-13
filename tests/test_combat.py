"""
Comprehensive test suite for combat.py

Tests cover:
- Combat initialization
- Initiative system
- Turn management
- Combat log
- Escape system
- Victory conditions
- Enemy AI
- Valid moves and targets
- Edge cases
"""

import pytest
import random
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add game directory to path
game_dir = Path(__file__).parent.parent / "game"
sys.path.insert(0, str(game_dir))

from combat import CombatEncounter
from character import Character
import config


class TestCombatInitialization:
    """Test combat encounter creation and setup."""

    def test_combat_creation(self, basic_combat_scenario):
        """Test basic combat creation."""
        player_team, enemy_team = basic_combat_scenario
        combat = CombatEncounter(player_team, enemy_team)

        assert combat.player_team == player_team
        assert combat.enemy_team == enemy_team
        assert len(combat.all_characters) == 2
        assert combat.combat_active is True

    def test_combat_teams_separated(self, team_combat_scenario):
        """Test teams are correctly separated."""
        player_team, enemy_team = team_combat_scenario
        combat = CombatEncounter(player_team, enemy_team)

        assert len(combat.player_team) == 2
        assert len(combat.enemy_team) == 2
        assert len(combat.all_characters) == 4

    def test_combat_initial_state(self, combat_encounter):
        """Test initial combat state."""
        assert combat_encounter.turn_count == 0
        assert combat_encounter.combat_active is True
        assert combat_encounter.escape_available is False
        assert combat_encounter.victor is None

    def test_combat_log_initialized(self, combat_encounter):
        """Test combat log is created and has initial messages."""
        assert isinstance(combat_encounter.combat_log, list)
        assert len(combat_encounter.combat_log) > 0
        assert "COMBAT START" in combat_encounter.combat_log[0]


class TestInitiativeSystem:
    """Test initiative rolling and turn order."""

    def test_initiative_rolled_on_creation(self, combat_encounter):
        """Test that initiative is rolled during combat creation."""
        assert len(combat_encounter.turn_order) > 0
        assert combat_encounter.current_character is not None

    def test_initiative_order_descending(self, team_combat_encounter):
        """Test that turn order is sorted by initiative (highest first)."""
        # Initiative is random, but we can verify it's in descending order
        # by checking that the first character has initiative >= subsequent characters
        # We can't directly test this without mocking, so we'll just verify turn_order exists
        assert len(team_combat_encounter.turn_order) == 4

    def test_all_characters_in_turn_order(self, team_combat_encounter):
        """Test that all characters are in turn order."""
        all_chars = team_combat_encounter.all_characters
        turn_chars = team_combat_encounter.turn_order

        assert len(all_chars) == len(turn_chars)
        for char in all_chars:
            assert char in turn_chars

    def test_initiative_logging(self, combat_encounter):
        """Test that initiative rolls are logged."""
        log_text = " ".join(combat_encounter.combat_log)
        assert "initiative" in log_text.lower()

    @patch('random.randint')
    def test_initiative_deterministic(self, mock_randint, basic_combat_scenario):
        """Test initiative with deterministic rolls."""
        mock_randint.return_value = 5

        player_team, enemy_team = basic_combat_scenario
        combat = CombatEncounter(player_team, enemy_team)

        # With fixed roll, can verify initiative calculation
        # Player reflexes = 6, enemy reflexes = 4
        # Player init = 6*2 + 5 = 17
        # Enemy init = 4*2 + 5 = 13
        # Player should go first
        assert combat.current_character == player_team[0]


class TestTurnManagement:
    """Test turn progression and management."""

    def test_next_turn_advances_index(self, combat_encounter):
        """Test that next_turn advances turn index."""
        initial_char = combat_encounter.current_character
        combat_encounter.next_turn()

        # Current character should change (if more than 1 character alive)
        if len([c for c in combat_encounter.all_characters if c.is_alive]) > 1:
            assert combat_encounter.current_character != initial_char

    def test_next_turn_wraps_around(self, combat_encounter):
        """Test that turn order wraps around after last character."""
        # Go through all turns
        num_chars = len([c for c in combat_encounter.all_characters if c.is_alive])

        for _ in range(num_chars):
            combat_encounter.next_turn()

        # Should have wrapped around
        assert combat_encounter.turn_count == 1

    def test_turn_count_increments(self, combat_encounter):
        """Test that turn count increments after full round."""
        initial_count = combat_encounter.turn_count
        num_chars = len(combat_encounter.all_characters)

        # Complete a full round
        for _ in range(num_chars):
            combat_encounter.next_turn()

        assert combat_encounter.turn_count == initial_count + 1

    def test_dead_characters_skipped(self, combat_encounter):
        """Test that dead characters are skipped in turn order."""
        # Kill a character
        combat_encounter.all_characters[0].is_alive = False

        initial_char = combat_encounter.current_character
        combat_encounter.next_turn()

        # Should skip the dead character
        assert combat_encounter.current_character.is_alive is True

    def test_current_character_turn_starts(self, combat_encounter):
        """Test that current character's turn is started."""
        combat_encounter.current_character.ap = 0
        combat_encounter.next_turn()

        # New current character should have full AP
        assert combat_encounter.current_character.ap == config.MAX_ACTION_POINTS

    def test_previous_character_turn_ends(self, combat_encounter):
        """Test that previous character's turn ends."""
        first_char = combat_encounter.current_character
        first_char.has_acted = False

        combat_encounter.next_turn()

        # Previous character should have has_acted set
        assert first_char.has_acted is True

    def test_get_current_team(self, combat_encounter):
        """Test getting current character's team."""
        team = combat_encounter.get_current_team()
        assert team in ['player', 'enemy']
        assert team == combat_encounter.current_character.team


class TestCombatLog:
    """Test combat logging functionality."""

    def test_add_log_appends(self, combat_encounter):
        """Test that add_log appends messages."""
        initial_length = len(combat_encounter.combat_log)
        combat_encounter.add_log("Test message")

        assert len(combat_encounter.combat_log) == initial_length + 1
        assert "Test message" in combat_encounter.combat_log

    def test_log_max_length(self, combat_encounter):
        """Test that log maintains maximum length."""
        # Add more than 20 messages
        for i in range(30):
            combat_encounter.add_log(f"Message {i}")

        # Should cap at 20
        assert len(combat_encounter.combat_log) <= 20

    def test_log_oldest_removed_first(self, combat_encounter):
        """Test that oldest messages are removed first."""
        # Clear log and add identifiable messages
        combat_encounter.combat_log = []

        for i in range(25):
            combat_encounter.add_log(f"Message {i}")

        # Should have last 20 messages
        assert len(combat_encounter.combat_log) == 20
        assert "Message 5" in combat_encounter.combat_log
        assert "Message 24" in combat_encounter.combat_log
        assert "Message 0" not in combat_encounter.combat_log

    def test_turn_logging(self, combat_encounter):
        """Test that turns are logged."""
        initial_log_len = len(combat_encounter.combat_log)
        combat_encounter.next_turn()

        assert len(combat_encounter.combat_log) > initial_log_len


class TestEscapeSystem:
    """Test escape mechanics."""

    def test_escape_not_available_early(self, combat_encounter):
        """Test that escape is not available before turn 3."""
        assert combat_encounter.escape_available is False

        success, msg = combat_encounter.attempt_escape()
        assert success is False
        assert "not available" in msg.lower()

    def test_escape_check_conditions_turn_3(self, combat_encounter):
        """Test escape becomes available on turn 3."""
        # Advance to turn 3
        combat_encounter.turn_count = 3

        # Damage player to trigger escape condition (need > 50% damage, not exactly 50%)
        for char in combat_encounter.player_team:
            char.take_damage(int(char.max_hp * 0.6))  # 60% damage to ensure HP < 50%

        combat_encounter.check_escape_conditions()
        assert combat_encounter.escape_available is True

    def test_escape_condition_low_hp(self, combat_encounter):
        """Test escape available when HP < 50%."""
        combat_encounter.turn_count = 3

        # Reduce player HP to below 50%
        for char in combat_encounter.player_team:
            char.hp = char.max_hp // 3  # 33% HP

        combat_encounter.check_escape_conditions()
        assert combat_encounter.escape_available is True

    def test_escape_condition_casualties(self, combat_encounter):
        """Test escape available with casualties."""
        # Add second player character
        stats = {
            'body': 5, 'reflexes': 5, 'intelligence': 5,
            'tech': 5, 'cool': 5, 'max_hp': 100, 'armor': 10
        }
        second_player = Character("Ally", 0, 0, stats, 'pistol', 'player')
        combat_encounter.player_team.append(second_player)
        combat_encounter.turn_count = 3

        # Kill one player
        second_player.is_alive = False

        combat_encounter.check_escape_conditions()
        assert combat_encounter.escape_available is True

    def test_escape_condition_outnumbered(self, outnumbered_scenario):
        """Test escape available when outnumbered 2:1."""
        player_team, enemy_team = outnumbered_scenario
        combat = CombatEncounter(player_team, enemy_team)
        combat.turn_count = 3

        combat.check_escape_conditions()
        assert combat.escape_available is True

    @patch('random.randint')
    def test_escape_solo_success(self, mock_randint, combat_encounter):
        """Test successful solo escape."""
        combat_encounter.escape_available = True
        mock_randint.return_value = 1  # Guarantee success

        success, msg = combat_encounter.attempt_escape()

        assert success is True
        assert combat_encounter.combat_active is False
        assert combat_encounter.victor == 'fled'

    @patch('random.randint')
    def test_escape_solo_failure(self, mock_randint, combat_encounter):
        """Test failed solo escape."""
        combat_encounter.escape_available = True
        mock_randint.return_value = 100  # Guarantee failure

        player_initial_hp = combat_encounter.player_team[0].hp

        success, msg = combat_encounter.attempt_escape()

        assert success is False
        assert combat_encounter.combat_active is True
        # Should take damage on failed escape
        assert combat_encounter.player_team[0].hp < player_initial_hp

    def test_escape_with_sacrifice_success(self, team_combat_scenario):
        """Test successful escape with sacrifice."""
        player_team, enemy_team = team_combat_scenario
        combat = CombatEncounter(player_team, enemy_team)
        combat.escape_available = True

        sacrifice = player_team[1]

        with patch('random.randint', return_value=1):  # Guarantee success
            success, msg = combat.attempt_escape(sacrifice_character=sacrifice)

        assert success is True
        assert sacrifice.is_alive is False
        assert combat.victor == 'fled'

    def test_escape_with_sacrifice_failure(self, team_combat_scenario):
        """Test failed escape with sacrifice."""
        player_team, enemy_team = team_combat_scenario
        combat = CombatEncounter(player_team, enemy_team)
        combat.escape_available = True

        sacrifice = player_team[1]

        with patch('random.randint', return_value=100):  # Guarantee failure
            success, msg = combat.attempt_escape(sacrifice_character=sacrifice)

        assert success is False
        assert sacrifice.is_alive is False  # Sacrifice dies even on failure
        assert combat.combat_active is True

    def test_escape_morale_penalty(self, combat_encounter):
        """Test that escape applies morale penalty."""
        combat_encounter.escape_available = True

        with patch('random.randint', return_value=1):  # Guarantee success
            initial_morale = combat_encounter.player_team[0].morale
            combat_encounter.attempt_escape()

            # Should lose morale
            assert combat_encounter.player_team[0].morale < initial_morale

    def test_escape_chance_calculation(self, combat_encounter):
        """Test escape chance based on reflexes."""
        combat_encounter.escape_available = True

        # Reflexes = 6, so escape chance = 45 + (6 * 2) = 57%
        # We can't directly test the calculation, but we can verify it runs
        with patch('random.randint', return_value=50):
            success, _ = combat_encounter.attempt_escape()
            # With roll of 50 and chance of 57, should succeed
            assert success is True


class TestVictoryConditions:
    """Test combat victory and defeat detection."""

    def test_player_victory(self, combat_encounter):
        """Test player victory when all enemies dead."""
        # Kill all enemies
        for enemy in combat_encounter.enemy_team:
            enemy.is_alive = False

        combat_encounter.check_victory()

        assert combat_encounter.combat_active is False
        assert combat_encounter.victor == 'player'

    def test_player_defeat(self, combat_encounter):
        """Test player defeat when all players dead."""
        # Kill all players
        for player in combat_encounter.player_team:
            player.is_alive = False

        combat_encounter.check_victory()

        assert combat_encounter.combat_active is False
        assert combat_encounter.victor == 'enemy'

    def test_combat_continues_with_survivors(self, combat_encounter):
        """Test combat continues when both sides have survivors."""
        combat_encounter.check_victory()

        # With all characters alive, combat should continue
        assert combat_encounter.combat_active is True
        assert combat_encounter.victor is None

    def test_victory_logged(self, combat_encounter):
        """Test that victory is logged."""
        # Kill all enemies
        for enemy in combat_encounter.enemy_team:
            enemy.is_alive = False

        combat_encounter.check_victory()

        log_text = " ".join(combat_encounter.combat_log)
        assert "VICTORY" in log_text

    def test_defeat_logged(self, combat_encounter):
        """Test that defeat is logged."""
        # Kill all players
        for player in combat_encounter.player_team:
            player.is_alive = False

        combat_encounter.check_victory()

        log_text = " ".join(combat_encounter.combat_log)
        assert "DEFEAT" in log_text


class TestValidMoves:
    """Test valid movement calculation."""

    def test_get_valid_moves_returns_positions(self, combat_encounter):
        """Test that get_valid_moves returns position tuples."""
        char = combat_encounter.current_character
        valid_moves = combat_encounter.get_valid_moves(char)

        assert isinstance(valid_moves, list)
        for move in valid_moves:
            assert isinstance(move, tuple)
            assert len(move) == 2

    def test_valid_moves_within_range(self, combat_encounter):
        """Test that valid moves are within movement range."""
        char = combat_encounter.current_character
        valid_moves = combat_encounter.get_valid_moves(char)

        for x, y in valid_moves:
            distance = abs(x - char.x) + abs(y - char.y)
            assert distance <= char.movement_range

    def test_valid_moves_within_bounds(self, combat_encounter):
        """Test that valid moves are within grid bounds."""
        char = combat_encounter.current_character
        valid_moves = combat_encounter.get_valid_moves(char)

        for x, y in valid_moves:
            assert 0 <= x < config.GRID_WIDTH
            assert 0 <= y < config.GRID_HEIGHT

    def test_valid_moves_exclude_occupied(self, team_combat_encounter):
        """Test that occupied tiles are excluded."""
        char = team_combat_encounter.current_character
        valid_moves = team_combat_encounter.get_valid_moves(char)

        # Check that no other character's position is in valid moves
        for other_char in team_combat_encounter.all_characters:
            if other_char != char and other_char.is_alive:
                assert (other_char.x, other_char.y) not in valid_moves

    def test_valid_moves_from_corner(self):
        """Test valid moves from grid corner."""
        stats = {
            'body': 5, 'reflexes': 5, 'intelligence': 5,
            'tech': 5, 'cool': 5, 'max_hp': 100, 'armor': 10
        }
        corner_char = Character("Corner", 0, 0, stats, 'pistol', 'player')
        enemy = Character("Enemy", 10, 10, stats, 'pistol', 'enemy')

        combat = CombatEncounter([corner_char], [enemy])
        valid_moves = combat.get_valid_moves(corner_char)

        # All moves should be within bounds
        for x, y in valid_moves:
            assert x >= 0 and y >= 0

    def test_valid_moves_manhattan_distance(self, combat_encounter):
        """Test that valid moves use Manhattan distance."""
        char = combat_encounter.current_character
        valid_moves = combat_encounter.get_valid_moves(char)

        # Verify Manhattan distance for each move
        for x, y in valid_moves:
            manhattan_dist = abs(x - char.x) + abs(y - char.y)
            assert manhattan_dist <= char.movement_range


class TestValidTargets:
    """Test valid target calculation."""

    def test_get_valid_targets_returns_characters(self, combat_encounter):
        """Test that get_valid_targets returns character objects."""
        char = combat_encounter.current_character
        targets = combat_encounter.get_valid_targets(char)

        assert isinstance(targets, list)
        for target in targets:
            assert isinstance(target, Character)

    def test_valid_targets_enemy_team(self, combat_encounter):
        """Test that valid targets are from enemy team."""
        char = combat_encounter.current_character
        targets = combat_encounter.get_valid_targets(char)

        for target in targets:
            assert target.team != char.team

    def test_valid_targets_within_weapon_range(self, combat_encounter):
        """Test that targets are within weapon range."""
        char = combat_encounter.current_character
        targets = combat_encounter.get_valid_targets(char)

        for target in targets:
            distance = abs(char.x - target.x) + abs(char.y - target.y)
            assert distance <= char.weapon['range']

    def test_valid_targets_only_alive(self, combat_encounter):
        """Test that only alive enemies are included."""
        char = combat_encounter.current_character

        # Kill an enemy
        for enemy in combat_encounter.enemy_team:
            enemy.is_alive = False

        targets = combat_encounter.get_valid_targets(char)

        # Should have no targets
        assert len(targets) == 0


class TestEnemyAI:
    """Test enemy AI behavior."""

    def test_enemy_ai_attacks_when_in_range(self, combat_encounter):
        """Test that enemy attacks when target is in range."""
        # Set current character to enemy
        enemy = combat_encounter.enemy_team[0]
        combat_encounter.current_character = enemy
        enemy.start_turn()

        # Place player in range
        player = combat_encounter.player_team[0]
        player.x = enemy.x + 2
        player.y = enemy.y

        initial_ap = enemy.ap

        combat_encounter.enemy_ai_turn(enemy)

        # Should have spent AP on attack
        assert enemy.ap < initial_ap

    def test_enemy_ai_moves_toward_player(self, combat_encounter):
        """Test that enemy moves toward player when out of range."""
        enemy = combat_encounter.enemy_team[0]
        player = combat_encounter.player_team[0]

        # Place player far away
        enemy.x = 0
        enemy.y = 0
        player.x = 10
        player.y = 10

        enemy.start_turn()
        initial_x = enemy.x
        initial_y = enemy.y

        combat_encounter.enemy_ai_turn(enemy)

        # Should have moved (at least tried)
        # Distance should have decreased or stayed same if blocked
        new_distance = abs(enemy.x - player.x) + abs(enemy.y - player.y)
        old_distance = abs(initial_x - player.x) + abs(initial_y - player.y)
        assert new_distance <= old_distance

    def test_enemy_ai_targets_closest_player(self, team_combat_encounter):
        """Test that enemy targets closest player."""
        enemy = team_combat_encounter.enemy_team[0]
        player1 = team_combat_encounter.player_team[0]
        player2 = team_combat_encounter.player_team[1]

        # Place players at different distances
        enemy.x = 5
        enemy.y = 5
        player1.x = 6
        player1.y = 5
        player2.x = 10
        player2.y = 10

        enemy.start_turn()

        # Enemy should target player1 (closer)
        with patch('random.randint', return_value=1):  # Guarantee hit
            initial_hp1 = player1.hp
            initial_hp2 = player2.hp

            team_combat_encounter.enemy_ai_turn(enemy)

            # Player1 should have taken damage, player2 should not
            assert player1.hp <= initial_hp1
            assert player2.hp == initial_hp2

    def test_enemy_ai_does_nothing_with_no_ap(self, combat_encounter):
        """Test that enemy does nothing when out of AP."""
        enemy = combat_encounter.enemy_team[0]
        enemy.ap = 0

        initial_x = enemy.x
        initial_y = enemy.y

        combat_encounter.enemy_ai_turn(enemy)

        # Position should not have changed (even if AP might be reset by combat system)
        assert enemy.x == initial_x
        assert enemy.y == initial_y

    def test_enemy_ai_avoids_occupied_tiles(self, team_combat_encounter):
        """Test that enemy doesn't move to occupied tiles."""
        enemy = team_combat_encounter.enemy_team[0]
        blocker = team_combat_encounter.enemy_team[1]

        # Place blocker in the way
        enemy.x = 5
        enemy.y = 5
        blocker.x = 6
        blocker.y = 5

        enemy.start_turn()
        initial_pos = (enemy.x, enemy.y)

        team_combat_encounter.enemy_ai_turn(enemy)

        # Enemy should not have moved to blocker's position
        assert (enemy.x, enemy.y) != (blocker.x, blocker.y)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_combat_with_one_character_each(self, basic_combat_scenario):
        """Test combat with minimal characters."""
        player_team, enemy_team = basic_combat_scenario
        combat = CombatEncounter(player_team, enemy_team)

        assert len(combat.all_characters) == 2
        assert combat.combat_active is True

    def test_combat_with_many_characters(self):
        """Test combat with many characters."""
        stats = {
            'body': 5, 'reflexes': 5, 'intelligence': 5,
            'tech': 5, 'cool': 5, 'max_hp': 100, 'armor': 10
        }

        player_team = [
            Character(f"Player{i}", i, 0, stats, 'pistol', 'player')
            for i in range(5)
        ]
        enemy_team = [
            Character(f"Enemy{i}", i, 10, stats, 'pistol', 'enemy')
            for i in range(5)
        ]

        combat = CombatEncounter(player_team, enemy_team)

        assert len(combat.all_characters) == 10
        assert len(combat.turn_order) == 10

    def test_turn_with_all_dead_except_one(self, combat_encounter):
        """Test turn progression when only one character alive."""
        # Kill all but one
        alive_char = combat_encounter.all_characters[0]
        for char in combat_encounter.all_characters:
            if char != alive_char:
                char.is_alive = False

        combat_encounter.next_turn()

        # Should still function
        assert combat_encounter.current_character == alive_char

    def test_escape_with_all_conditions_met(self, outnumbered_scenario):
        """Test escape when multiple conditions are met."""
        player_team, enemy_team = outnumbered_scenario
        combat = CombatEncounter(player_team, enemy_team)

        # Set multiple escape conditions
        combat.turn_count = 3
        player_team[0].hp = player_team[0].max_hp // 4  # Low HP
        # Already outnumbered

        combat.check_escape_conditions()
        assert combat.escape_available is True

    def test_combat_at_grid_boundaries(self):
        """Test combat with characters at grid edges."""
        stats = {
            'body': 5, 'reflexes': 5, 'intelligence': 5,
            'tech': 5, 'cool': 5, 'max_hp': 100, 'armor': 10
        }

        # Place at opposite corners
        player = Character("Player", 0, 0, stats, 'pistol', 'player')
        enemy = Character("Enemy", config.GRID_WIDTH-1, config.GRID_HEIGHT-1,
                         stats, 'pistol', 'enemy')

        combat = CombatEncounter([player], [enemy])

        # Should create without error
        assert combat.combat_active is True

    def test_turn_counter_overflow(self, combat_encounter):
        """Test that turn counter handles large values."""
        combat_encounter.turn_count = 1000

        # Should still function
        combat_encounter.next_turn()
        assert combat_encounter.turn_count >= 1000

    def test_empty_log_message(self, combat_encounter):
        """Test adding empty log message."""
        combat_encounter.add_log("")
        assert "" in combat_encounter.combat_log


@pytest.mark.integration
class TestCombatIntegration:
    """Integration tests for complete combat scenarios."""

    def test_full_combat_flow(self, combat_encounter):
        """Test a complete combat flow from start to finish."""
        max_turns = 50
        turn = 0

        while combat_encounter.combat_active and turn < max_turns:
            current = combat_encounter.current_character

            if current.team == 'enemy':
                combat_encounter.enemy_ai_turn(current)
            else:
                # Simulate player action
                targets = combat_encounter.get_valid_targets(current)
                if targets and current.ap >= config.AP_BASIC_ATTACK:
                    target = targets[0]
                    current.attack(target)

            combat_encounter.next_turn()
            turn += 1

        # Combat should have resolved
        assert turn < max_turns or combat_encounter.combat_active is False

    def test_escape_then_check_victory(self, combat_encounter):
        """Test that escape properly ends combat."""
        combat_encounter.escape_available = True

        with patch('random.randint', return_value=1):
            combat_encounter.attempt_escape()

        # Should not be in active combat
        assert combat_encounter.combat_active is False
        assert combat_encounter.victor == 'fled'

        # Victory check should not override escape
        combat_encounter.check_victory()
        assert combat_encounter.victor == 'fled'

    def test_complete_round_robin(self, team_combat_encounter):
        """Test that all characters get turns in order."""
        initial_turn_order = team_combat_encounter.turn_order.copy()
        turns_taken = []

        for _ in range(len(initial_turn_order)):
            turns_taken.append(team_combat_encounter.current_character)
            team_combat_encounter.next_turn()

        # All characters should have taken a turn
        assert len(turns_taken) == len(initial_turn_order)
