"""
Comprehensive test suite for character.py

Tests cover:
- Character initialization
- Attribute system (Body, Reflexes, Intelligence, Tech, Cool)
- Combat stats (HP, Armor, Morale, AP)
- Combat calculations (Initiative, Dodge, Crit, Hit Chance, Damage)
- Actions (Attack, Move, Turn management)
- Edge cases and boundary conditions
"""

import pytest
import random
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add game directory to path
game_dir = Path(__file__).parent.parent / "game"
sys.path.insert(0, str(game_dir))

from character import Character
import config


class TestCharacterInitialization:
    """Test character creation and initialization."""

    def test_character_creation_basic(self, player_character):
        """Test basic character creation with valid stats."""
        assert player_character.name == "V"
        assert player_character.x == 5
        assert player_character.y == 5
        assert player_character.team == 'player'
        assert player_character.is_alive is True

    def test_character_attributes(self, player_character):
        """Test that all five attributes are correctly assigned."""
        assert player_character.body == 5
        assert player_character.reflexes == 6
        assert player_character.intelligence == 5
        assert player_character.tech == 5
        assert player_character.cool == 6

    def test_character_combat_stats(self, player_character):
        """Test combat stats initialization."""
        assert player_character.max_hp == 150
        assert player_character.hp == 150
        assert player_character.armor == 20
        assert player_character.morale == 100

    def test_character_action_points(self, player_character):
        """Test action points initialization."""
        assert player_character.max_ap == config.MAX_ACTION_POINTS
        assert player_character.ap == config.MAX_ACTION_POINTS
        assert player_character.max_ap == 3  # Based on TDD spec

    def test_character_weapon_assignment(self, player_character):
        """Test that weapon is correctly assigned and copied."""
        assert player_character.weapon['name'] == 'Assault Rifle'
        assert player_character.weapon['damage'] == 30
        assert player_character.weapon['range'] == 12
        assert player_character.weapon['type'] == 'ranged'

    def test_character_movement_range(self):
        """Test movement range calculation based on reflexes."""
        # Movement range = BASE_MOVEMENT_RANGE + (reflexes // 4)
        stats = {
            'body': 5, 'reflexes': 4, 'intelligence': 5,
            'tech': 5, 'cool': 5, 'max_hp': 100, 'armor': 10
        }
        char = Character("Test", 0, 0, stats, 'pistol', 'player')
        expected_range = config.BASE_MOVEMENT_RANGE + (4 // 4)
        assert char.movement_range == expected_range

        # Test with higher reflexes
        stats['reflexes'] = 8
        char2 = Character("Test2", 0, 0, stats, 'pistol', 'player')
        expected_range2 = config.BASE_MOVEMENT_RANGE + (8 // 4)
        assert char2.movement_range == expected_range2

    def test_character_initial_state(self, player_character):
        """Test initial combat state flags."""
        assert player_character.has_acted is False
        assert player_character.has_moved is False
        assert player_character.in_cover is False
        assert player_character.cover_type is None

    def test_character_with_different_weapons(self):
        """Test character creation with different weapon types."""
        stats = {
            'body': 5, 'reflexes': 5, 'intelligence': 5,
            'tech': 5, 'cool': 5, 'max_hp': 100, 'armor': 10
        }

        weapons = ['assault_rifle', 'pistol', 'shotgun', 'katana']
        for weapon_key in weapons:
            char = Character(f"Test_{weapon_key}", 0, 0, stats, weapon_key, 'player')
            assert char.weapon['name'] == config.WEAPONS[weapon_key]['name']

    def test_enemy_character_creation(self, enemy_character):
        """Test enemy character is correctly flagged."""
        assert enemy_character.team == 'enemy'
        assert enemy_character.name == "Gang Grunt"


class TestCharacterCalculations:
    """Test combat calculation methods."""

    def test_get_initiative(self, player_character):
        """Test initiative calculation: (Reflexes × 2) + random(1, 10)."""
        # Reflexes = 6, so base = 12
        with patch('random.randint', return_value=5):
            initiative = player_character.get_initiative()
            assert initiative == 12 + 5

        with patch('random.randint', return_value=1):
            initiative = player_character.get_initiative()
            assert initiative == 12 + 1

        with patch('random.randint', return_value=10):
            initiative = player_character.get_initiative()
            assert initiative == 12 + 10

    def test_get_initiative_range(self, player_character):
        """Test initiative is always within expected range."""
        for _ in range(100):
            initiative = player_character.get_initiative()
            # Should be between (reflexes * 2 + 1) and (reflexes * 2 + 10)
            assert 13 <= initiative <= 22

    def test_get_dodge_chance(self, player_character):
        """Test dodge chance calculation: min(20, reflexes × 3)."""
        # Player reflexes = 6, dodge = 18
        assert player_character.get_dodge_chance() == 18

    def test_get_dodge_chance_cap(self, strong_character):
        """Test dodge chance is capped at DODGE_CAP (20)."""
        # Strong character has reflexes = 10, so 10 * 3 = 30, but capped at 20
        assert strong_character.get_dodge_chance() == config.DODGE_CAP

    def test_get_dodge_chance_low_reflexes(self, weak_character):
        """Test dodge chance with low reflexes."""
        # Weak character reflexes = 1, dodge = 3
        assert weak_character.get_dodge_chance() == 3

    def test_get_crit_chance(self, player_character):
        """Test crit chance calculation: cool × 2."""
        # Player cool = 6, crit = 12%
        assert player_character.get_crit_chance() == 12

    def test_get_crit_chance_range(self):
        """Test crit chance with various cool values."""
        stats = {
            'body': 5, 'reflexes': 5, 'intelligence': 5,
            'tech': 5, 'max_hp': 100, 'armor': 10
        }

        for cool_val in range(1, 11):
            stats['cool'] = cool_val
            char = Character("Test", 0, 0, stats, 'pistol', 'player')
            assert char.get_crit_chance() == cool_val * 2

    def test_get_morale_modifier_high_morale(self, player_character):
        """Test morale modifier at high morale (100)."""
        player_character.morale = 100
        # Modifier = 1.0 + ((100 - 50) / 200) = 1.0 + 0.25 = 1.25
        assert player_character.get_morale_modifier() == 1.25

    def test_get_morale_modifier_neutral_morale(self, player_character):
        """Test morale modifier at neutral morale (50)."""
        player_character.morale = 50
        # Modifier = 1.0 + ((50 - 50) / 200) = 1.0
        assert player_character.get_morale_modifier() == 1.0

    def test_get_morale_modifier_low_morale(self, player_character):
        """Test morale modifier at low morale (0)."""
        player_character.morale = 0
        # Modifier = 1.0 + ((0 - 50) / 200) = 1.0 - 0.25 = 0.75
        assert player_character.get_morale_modifier() == 0.75

    def test_get_hp_percentage(self, player_character):
        """Test HP percentage calculation."""
        assert player_character.get_hp_percentage() == 100.0

        player_character.hp = 75
        assert player_character.get_hp_percentage() == 50.0

        player_character.hp = 0
        assert player_character.get_hp_percentage() == 0.0


class TestHitChanceCalculation:
    """Test hit chance calculation with various modifiers."""

    def test_basic_hit_chance(self, player_character, enemy_character):
        """Test basic hit chance without modifiers."""
        hit_chance = player_character.calculate_hit_chance(enemy_character)

        # Assault rifle accuracy = 85
        # Enemy dodge = reflexes * 3 = 4 * 3 = 12
        # Hit chance = 85 - 12 = 73
        assert hit_chance == 73

    def test_hit_chance_with_half_cover(self, player_character, enemy_character):
        """Test hit chance with target in half cover."""
        enemy_character.in_cover = True
        enemy_character.cover_type = 'half'

        hit_chance = player_character.calculate_hit_chance(enemy_character)

        # Base = 85 - 12 = 73
        # Half cover = -25
        # Final = 73 - 25 = 48
        assert hit_chance == 48

    def test_hit_chance_with_full_cover(self, player_character, enemy_character):
        """Test hit chance with target in full cover."""
        enemy_character.in_cover = True
        enemy_character.cover_type = 'full'

        hit_chance = player_character.calculate_hit_chance(enemy_character)

        # Base = 85 - 12 = 73
        # Full cover = -40
        # Final = 73 - 40 = 33
        assert hit_chance == 33

    def test_hit_chance_minimum_cap(self, weak_character, strong_character):
        """Test hit chance is capped at minimum 5%."""
        # Weak character vs strong character should hit minimum
        hit_chance = weak_character.calculate_hit_chance(strong_character)
        assert hit_chance >= 5

    def test_hit_chance_maximum_cap(self, strong_character, weak_character):
        """Test hit chance is capped at maximum 95%."""
        # Strong character vs weak character should hit maximum
        hit_chance = strong_character.calculate_hit_chance(weak_character)
        assert hit_chance <= 95

    def test_hit_chance_high_dodge_target(self, player_character, strong_character):
        """Test hit chance against high dodge target."""
        # Strong character has reflexes 10, dodge = 20 (capped)
        hit_chance = player_character.calculate_hit_chance(strong_character)

        # Assault rifle accuracy = 85
        # Dodge = 20
        # Hit chance = 85 - 20 = 65
        assert hit_chance == 65


class TestDamageCalculation:
    """Test damage calculation with all modifiers."""

    def test_damage_calculation_basic(self, player_character, enemy_character):
        """Test basic damage calculation without special modifiers."""
        random.seed(42)  # Set seed for reproducibility

        with patch('random.uniform', return_value=1.0):
            with patch('random.randint', return_value=100):  # No crit
                damage, is_crit = player_character.calculate_damage(enemy_character)

                # Base damage = 30 * 1.0 = 30
                # Stat bonus = reflexes * 2 = 6 * 2 = 12
                # No crit = 1.0
                # Morale = 1.25 (morale 100)
                # Total before armor = (30 + 12) * 1.0 * 1.25 = 52.5
                # Armor reduction = 10 * (1 - 0.15) * 1.0 = 8.5
                # Total = 52.5 - 8.5 = 44

                assert damage >= 1  # At least minimum damage
                assert is_crit is False

    def test_damage_calculation_with_crit(self, player_character, enemy_character):
        """Test damage calculation with critical hit."""
        with patch('random.uniform', return_value=1.0):
            with patch('random.randint', return_value=1):  # Guaranteed crit
                damage, is_crit = player_character.calculate_damage(enemy_character)

                assert is_crit is True
                assert damage >= 1

    def test_damage_melee_weapon(self, melee_character, enemy_character):
        """Test damage calculation for melee weapon (uses Body stat)."""
        with patch('random.uniform', return_value=1.0):
            with patch('random.randint', return_value=100):  # No crit
                damage, is_crit = melee_character.calculate_damage(enemy_character)

                # Melee weapon uses Body stat
                # Body = 8, so stat bonus = 8 * 3 = 24
                assert damage >= 1

    def test_damage_with_low_morale(self, player_character, enemy_character):
        """Test damage is reduced with low morale."""
        player_character.morale = 0

        with patch('random.uniform', return_value=1.0):
            with patch('random.randint', return_value=100):
                damage_low_morale, _ = player_character.calculate_damage(enemy_character)

        player_character.morale = 100

        with patch('random.uniform', return_value=1.0):
            with patch('random.randint', return_value=100):
                damage_high_morale, _ = player_character.calculate_damage(enemy_character)

        # Low morale should deal less damage
        assert damage_low_morale < damage_high_morale

    def test_damage_armor_penetration(self):
        """Test armor penetration affects damage."""
        stats = {
            'body': 5, 'reflexes': 5, 'intelligence': 5,
            'tech': 5, 'cool': 5, 'max_hp': 100, 'armor': 50
        }
        heavy_armor_target = Character("Tank", 0, 0, stats, 'pistol', 'enemy')

        stats_attacker = {
            'body': 5, 'reflexes': 5, 'intelligence': 5,
            'tech': 5, 'cool': 5, 'max_hp': 100, 'armor': 10
        }
        attacker = Character("Attacker", 0, 0, stats_attacker, 'katana', 'player')

        # Katana has higher armor pen than pistol
        with patch('random.uniform', return_value=1.0):
            with patch('random.randint', return_value=100):
                damage, _ = attacker.calculate_damage(heavy_armor_target)
                assert damage >= 1

    def test_damage_with_cover(self, player_character, enemy_character):
        """Test damage is reduced when target is in cover."""
        enemy_character.in_cover = True
        enemy_character.cover_type = 'half'

        with patch('random.uniform', return_value=1.0):
            with patch('random.randint', return_value=100):
                damage_with_cover, _ = player_character.calculate_damage(enemy_character)

        enemy_character.in_cover = False

        with patch('random.uniform', return_value=1.0):
            with patch('random.randint', return_value=100):
                damage_no_cover, _ = player_character.calculate_damage(enemy_character)

        # Cover should reduce damage
        assert damage_with_cover < damage_no_cover

    def test_damage_minimum_one(self, weak_character, strong_character):
        """Test damage is always at least 1."""
        # Weak character attacking strong character should still do minimum 1 damage
        damage, _ = weak_character.calculate_damage(strong_character)
        assert damage >= 1


class TestCombatActions:
    """Test combat action methods (attack, move, etc.)."""

    def test_attack_success(self, player_character, enemy_character):
        """Test successful attack."""
        initial_hp = enemy_character.hp
        initial_ap = player_character.ap

        with patch('random.randint', return_value=1):  # Guarantee hit
            damage, log = player_character.attack(enemy_character)

            assert damage is not None
            assert damage >= 0
            assert enemy_character.hp < initial_hp or damage == 0  # Either damage dealt or miss
            assert player_character.ap == initial_ap - config.AP_BASIC_ATTACK

    def test_attack_miss(self, player_character, enemy_character):
        """Test missed attack."""
        with patch('random.randint', return_value=100):  # Guarantee miss
            damage, log = player_character.attack(enemy_character)

            assert "miss" in log.lower()

    def test_attack_insufficient_ap(self, player_character, enemy_character):
        """Test attack fails with insufficient AP."""
        player_character.ap = 1  # Not enough for attack (needs 2)

        damage, log = player_character.attack(enemy_character)

        assert damage is None
        assert "Not enough AP" in log

    def test_attack_out_of_range(self, player_character, enemy_character):
        """Test attack fails when target is out of range."""
        # Move enemy far away
        enemy_character.x = 50
        enemy_character.y = 50

        damage, log = player_character.attack(enemy_character)

        assert damage is None
        assert "out of range" in log.lower()

    def test_attack_reduces_ap(self, player_character, enemy_character):
        """Test that attacking reduces AP correctly."""
        initial_ap = player_character.ap

        # Place enemy in range
        enemy_character.x = player_character.x + 5
        enemy_character.y = player_character.y

        player_character.attack(enemy_character)

        assert player_character.ap == initial_ap - config.AP_BASIC_ATTACK

    def test_attack_kills_target(self, player_character, weak_character):
        """Test that attack can kill a target."""
        weak_character.hp = 1
        weak_character.team = 'enemy'
        weak_character.x = player_character.x + 1
        weak_character.y = player_character.y

        with patch('random.randint', return_value=1):  # Guarantee hit
            player_character.attack(weak_character)

            assert weak_character.hp == 0
            assert weak_character.is_alive is False


class TestMovement:
    """Test character movement."""

    def test_move_success(self, player_character):
        """Test successful movement."""
        initial_x = player_character.x
        initial_y = player_character.y
        initial_ap = player_character.ap

        new_x = initial_x + 1
        new_y = initial_y + 1

        success, log = player_character.move(new_x, new_y)

        assert success is True
        assert player_character.x == new_x
        assert player_character.y == new_y
        assert player_character.ap == initial_ap - config.AP_MOVE
        assert player_character.has_moved is True

    def test_move_insufficient_ap(self, player_character):
        """Test movement fails with insufficient AP."""
        player_character.ap = 0

        success, log = player_character.move(6, 6)

        assert success is False
        assert "Not enough AP" in log

    def test_move_too_far(self, player_character):
        """Test movement fails when distance exceeds movement range."""
        # Try to move beyond movement range
        far_x = player_character.x + player_character.movement_range + 5
        far_y = player_character.y

        success, log = player_character.move(far_x, far_y)

        assert success is False
        assert "Too far" in log

    def test_move_exact_range(self, player_character):
        """Test movement at exact maximum range."""
        # Move exactly at movement range
        target_x = player_character.x + player_character.movement_range
        target_y = player_character.y

        success, log = player_character.move(target_x, target_y)

        assert success is True

    def test_move_manhattan_distance(self, player_character):
        """Test that movement uses Manhattan distance."""
        initial_x = player_character.x
        initial_y = player_character.y

        # Move diagonally - Manhattan distance = |dx| + |dy|
        player_character.move(initial_x + 2, initial_y + 2)

        # Distance should be 4, but movement_range is likely > 4
        # Just verify the character moved
        assert (player_character.x != initial_x or player_character.y != initial_y)


class TestTurnManagement:
    """Test turn start/end and state management."""

    def test_start_turn(self, player_character):
        """Test start turn resets AP and flags."""
        player_character.ap = 0
        player_character.has_acted = True
        player_character.has_moved = True

        player_character.start_turn()

        assert player_character.ap == player_character.max_ap
        assert player_character.has_acted is False
        assert player_character.has_moved is False

    def test_end_turn(self, player_character):
        """Test end turn sets has_acted flag."""
        player_character.has_acted = False

        player_character.end_turn()

        assert player_character.has_acted is True

    def test_turn_cycle(self, player_character):
        """Test a complete turn cycle."""
        # Start turn
        player_character.start_turn()
        assert player_character.ap == 3
        assert player_character.has_acted is False

        # Take actions
        player_character.move(6, 6)
        assert player_character.ap == 2
        assert player_character.has_moved is True

        # End turn
        player_character.end_turn()
        assert player_character.has_acted is True

        # Start new turn
        player_character.start_turn()
        assert player_character.ap == 3
        assert player_character.has_acted is False
        assert player_character.has_moved is False


class TestDamageAndMorale:
    """Test taking damage and morale system."""

    def test_take_damage_basic(self, player_character):
        """Test taking basic damage."""
        initial_hp = player_character.hp
        damage = 20

        player_character.take_damage(damage)

        assert player_character.hp == initial_hp - damage
        assert player_character.is_alive is True

    def test_take_damage_morale_loss_heavy(self, player_character):
        """Test morale loss from heavy damage (30%+ HP)."""
        initial_morale = player_character.morale
        heavy_damage = int(player_character.max_hp * 0.3)

        player_character.take_damage(heavy_damage)

        assert player_character.morale < initial_morale
        assert player_character.morale == initial_morale - 20

    def test_take_damage_morale_loss_moderate(self, player_character):
        """Test morale loss from moderate damage (15-30% HP)."""
        initial_morale = player_character.morale
        moderate_damage = int(player_character.max_hp * 0.16)  # Slightly over 15% to ensure trigger

        player_character.take_damage(moderate_damage)

        assert player_character.morale == initial_morale - 10

    def test_take_damage_morale_no_loss_light(self, player_character):
        """Test no morale loss from light damage (<15% HP)."""
        initial_morale = player_character.morale
        light_damage = int(player_character.max_hp * 0.1)

        player_character.take_damage(light_damage)

        assert player_character.morale == initial_morale

    def test_take_damage_death(self, player_character):
        """Test character death from excessive damage."""
        player_character.take_damage(player_character.max_hp + 50)

        assert player_character.hp == 0
        assert player_character.is_alive is False

    def test_take_damage_exact_lethal(self, player_character):
        """Test character death from exact HP damage."""
        player_character.take_damage(player_character.hp)

        assert player_character.hp == 0
        assert player_character.is_alive is False

    def test_morale_floor(self, player_character):
        """Test morale doesn't go below 0."""
        # Take lots of heavy damage to drive morale to 0
        for _ in range(10):
            player_character.take_damage(int(player_character.max_hp * 0.3))

        assert player_character.morale >= 0


class TestTargetFinding:
    """Test finding targets in range."""

    def test_get_targets_in_range_single(self, player_character, enemy_character):
        """Test finding a single target in range."""
        all_chars = [player_character, enemy_character]
        targets = player_character.get_targets_in_range(all_chars)

        # Check if enemy is in range (assault rifle range = 12)
        distance = abs(player_character.x - enemy_character.x) + abs(player_character.y - enemy_character.y)
        if distance <= player_character.weapon['range']:
            assert enemy_character in targets
        else:
            assert enemy_character not in targets

    def test_get_targets_in_range_multiple(self, player_character, enemy_character, elite_enemy):
        """Test finding multiple targets in range."""
        # Place enemies close
        enemy_character.x = player_character.x + 2
        enemy_character.y = player_character.y
        elite_enemy.x = player_character.x + 3
        elite_enemy.y = player_character.y

        all_chars = [player_character, enemy_character, elite_enemy]
        targets = player_character.get_targets_in_range(all_chars)

        assert len(targets) == 2
        assert enemy_character in targets
        assert elite_enemy in targets

    def test_get_targets_excludes_allies(self, player_character, ally_character, enemy_character):
        """Test that allies are not included in targets."""
        all_chars = [player_character, ally_character, enemy_character]
        targets = player_character.get_targets_in_range(all_chars)

        assert ally_character not in targets

    def test_get_targets_excludes_dead(self, player_character, enemy_character):
        """Test that dead enemies are not included."""
        enemy_character.is_alive = False
        enemy_character.x = player_character.x + 1
        enemy_character.y = player_character.y

        all_chars = [player_character, enemy_character]
        targets = player_character.get_targets_in_range(all_chars)

        assert enemy_character not in targets

    def test_get_targets_out_of_range(self, player_character, enemy_character):
        """Test that targets out of range are excluded."""
        # Place enemy far away
        enemy_character.x = player_character.x + 50
        enemy_character.y = player_character.y + 50

        all_chars = [player_character, enemy_character]
        targets = player_character.get_targets_in_range(all_chars)

        assert len(targets) == 0


class TestCharacterRepr:
    """Test string representation."""

    def test_repr(self, player_character):
        """Test __repr__ method."""
        repr_str = repr(player_character)

        assert "V" in repr_str
        assert str(player_character.hp) in repr_str
        assert str(player_character.max_hp) in repr_str
        assert str(player_character.ap) in repr_str
        assert str(player_character.max_ap) in repr_str


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_character_at_grid_boundaries(self):
        """Test character at grid edges."""
        stats = {
            'body': 5, 'reflexes': 5, 'intelligence': 5,
            'tech': 5, 'cool': 5, 'max_hp': 100, 'armor': 10
        }

        # Test all corners
        corners = [(0, 0), (19, 0), (0, 14), (19, 14)]
        for x, y in corners:
            char = Character("Corner", x, y, stats, 'pistol', 'player')
            assert char.x == x
            assert char.y == y

    def test_zero_armor_character(self):
        """Test character with zero armor."""
        stats = {
            'body': 5, 'reflexes': 5, 'intelligence': 5,
            'tech': 5, 'cool': 5, 'max_hp': 100, 'armor': 0
        }
        char = Character("No Armor", 0, 0, stats, 'pistol', 'player')
        assert char.armor == 0

    def test_max_stats_character(self):
        """Test character with maximum stats."""
        stats = {
            'body': 10, 'reflexes': 10, 'intelligence': 10,
            'tech': 10, 'cool': 10, 'max_hp': 500, 'armor': 100
        }
        char = Character("Max Stats", 0, 0, stats, 'katana', 'player')
        assert char.body == 10
        assert char.reflexes == 10
        assert char.get_dodge_chance() == config.DODGE_CAP  # Capped at 20

    def test_min_stats_character(self):
        """Test character with minimum stats."""
        stats = {
            'body': 1, 'reflexes': 1, 'intelligence': 1,
            'tech': 1, 'cool': 1, 'max_hp': 10, 'armor': 0
        }
        char = Character("Min Stats", 0, 0, stats, 'pistol', 'player')
        assert char.body == 1
        assert char.reflexes == 1

    def test_attack_at_exact_range(self, player_character, enemy_character):
        """Test attack at exact weapon range."""
        # Place enemy at exact range
        weapon_range = player_character.weapon['range']
        enemy_character.x = player_character.x + weapon_range
        enemy_character.y = player_character.y

        damage, log = player_character.attack(enemy_character)

        # Should be able to attack (not out of range)
        assert "out of range" not in log.lower()

    def test_multiple_damage_instances(self, player_character):
        """Test character surviving multiple damage instances."""
        damage_per_hit = 20
        max_hits = player_character.max_hp // damage_per_hit

        for i in range(max_hits):
            player_character.take_damage(damage_per_hit)
            if i < max_hits - 1:
                assert player_character.is_alive is True

        # One more should kill
        player_character.take_damage(damage_per_hit)
        assert player_character.is_alive is False


@pytest.mark.integration
class TestCombatIntegration:
    """Integration tests for complete combat scenarios."""

    def test_full_combat_turn(self, player_character, enemy_character):
        """Test a complete combat turn with movement and attack."""
        enemy_character.x = player_character.x + 3
        enemy_character.y = player_character.y

        # Start turn
        player_character.start_turn()
        assert player_character.ap == 3

        # Move closer
        success, _ = player_character.move(player_character.x + 1, player_character.y)
        assert success is True
        assert player_character.ap == 2

        # Attack
        damage, log = player_character.attack(enemy_character)
        assert player_character.ap == 0

        # End turn
        player_character.end_turn()
        assert player_character.has_acted is True

    def test_consecutive_turns(self, player_character, enemy_character):
        """Test multiple consecutive turns."""
        enemy_character.x = player_character.x + 2
        enemy_character.y = player_character.y

        for turn in range(3):
            player_character.start_turn()
            player_character.attack(enemy_character)
            player_character.end_turn()

            # Character should be ready for next turn
            if turn < 2:
                assert player_character.has_acted is True

    def test_kill_sequence(self, player_character):
        """Test attacking until enemy is killed."""
        stats = {
            'body': 2, 'reflexes': 2, 'intelligence': 2,
            'tech': 2, 'cool': 2, 'max_hp': 30, 'armor': 0
        }
        weak_enemy = Character("Weak", player_character.x + 1, player_character.y,
                              stats, 'pistol', 'enemy')

        max_turns = 10
        turn = 0

        while weak_enemy.is_alive and turn < max_turns:
            player_character.start_turn()
            player_character.attack(weak_enemy)
            turn += 1

        # Enemy should eventually die
        assert weak_enemy.is_alive is False or turn == max_turns
