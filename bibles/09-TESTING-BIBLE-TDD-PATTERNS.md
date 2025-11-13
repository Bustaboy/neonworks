# NEON COLLAPSE - TESTING BIBLE
## TDD Patterns, Examples & Best Practices for Developers

**Version:** 1.0
**Last Updated:** 2025-11-12
**Status:** MASTER REFERENCE DOCUMENT

---

## TABLE OF CONTENTS

1. [TDD Fundamentals](#tdd-fundamentals)
2. [Test-First Workflow](#test-first-workflow)
3. [Testing Patterns Library](#testing-patterns-library)
4. [Common Testing Scenarios](#common-testing-scenarios)
5. [Mocking and Stubbing](#mocking-and-stubbing)
6. [Test Data Management](#test-data-management)
7. [Edge Case Catalog](#edge-case-catalog)
8. [Integration Testing](#integration-testing)
9. [Debugging Failed Tests](#debugging-failed-tests)
10. [Performance Testing](#performance-testing)

---

## TDD FUNDAMENTALS

### The Red-Green-Refactor Cycle

**RED:** Write a failing test
```python
def test_character_gains_xp():
    """Character should gain XP from defeating enemies."""
    char = create_character(level=1, xp=0)
    enemy = create_enemy(level=3)

    char.defeat_enemy(enemy)

    assert char.xp == 150  # level 3 enemy = 150 XP
```

**GREEN:** Make it pass with minimum code
```python
class Character:
    def defeat_enemy(self, enemy):
        xp_gained = enemy.level * 50
        self.xp += xp_gained
```

**REFACTOR:** Improve without changing behavior
```python
class Character:
    XP_PER_LEVEL = 50

    def defeat_enemy(self, enemy):
        """Gain XP based on defeated enemy level."""
        xp_gained = self.calculate_xp_reward(enemy)
        self.gain_xp(xp_gained)

    def calculate_xp_reward(self, enemy):
        """Calculate XP reward for defeating enemy."""
        return enemy.level * self.XP_PER_LEVEL

    def gain_xp(self, amount):
        """Add XP and check for level up."""
        self.xp += amount
        self.check_level_up()
```

### Why TDD Works for Games

**Complex Calculations**
```python
# Without tests: How do you know this works?
damage = (base + stat_bonus) * crit * morale - armor

# With tests: You verify every step
def test_damage_with_all_modifiers():
    # Test with known inputs → verify output
    assert calculate_damage(...) == expected_damage
```

**Regression Prevention**
```python
# Fix a bug, add a test
def test_negative_hp_clamped_to_zero():
    """Bug #42: HP was going negative."""
    char.hp = 5
    char.take_damage(10)
    assert char.hp == 0  # Not -5!
```

**Living Documentation**
```python
# Tests explain HOW the system works
def test_morale_affects_damage():
    """High morale (100) gives +25% damage.
       Low morale (0) gives -25% damage."""
    # Test demonstrates the mechanic
```

---

## TEST-FIRST WORKFLOW

### Step-by-Step: Adding a New Feature

**Example: Add "Special Attack" ability**

**1. Write Acceptance Criteria**
```
Feature: Special Attack
- Costs 3 AP (all action points)
- Deals 2× weapon damage
- Cannot be used if AP < 3
- Bypasses armor
- Logs special attack message
```

**2. Write Test Cases**
```python
def test_special_attack_deals_double_damage():
    """Special attack deals 2× normal weapon damage."""
    attacker = create_character(weapon='pistol')  # 25 damage
    target = create_enemy()

    with patch('random.uniform', return_value=1.0):  # No variance
        with patch('random.randint', return_value=100):  # No crit
            damage, _ = attacker.special_attack(target)

            # Normal: 25, Special: 50 (before other modifiers)
            assert damage >= 50

def test_special_attack_costs_3_ap():
    """Special attack should cost 3 AP."""
    char = create_character()
    initial_ap = char.ap

    char.special_attack(create_enemy())

    assert char.ap == initial_ap - 3

def test_special_attack_insufficient_ap():
    """Cannot use special attack with less than 3 AP."""
    char = create_character()
    char.ap = 2

    result, msg = char.special_attack(create_enemy())

    assert result is None
    assert "Not enough AP" in msg

def test_special_attack_bypasses_armor():
    """Special attack ignores armor."""
    attacker = create_character()
    target = create_enemy(armor=100)  # Heavy armor

    with patch_damage_randomness():
        damage, _ = attacker.special_attack(target)

        # Should deal full damage despite 100 armor
        assert damage > 40  # Not reduced by armor
```

**3. Run Tests (Should Fail)**
```bash
$ pytest tests/test_character.py::test_special_attack_deals_double_damage
FAILED: AttributeError: 'Character' object has no attribute 'special_attack'
```

**4. Implement Feature**
```python
class Character:
    def special_attack(self, target):
        """Execute special attack costing 3 AP."""
        # Check AP
        if self.ap < AP_SPECIAL_ABILITY:
            return None, "Not enough AP for special attack!"

        # Spend AP
        self.ap -= AP_SPECIAL_ABILITY

        # Calculate damage (2× base, bypass armor)
        hit_chance = self.calculate_hit_chance(target)
        roll = random.randint(1, 100)

        if roll <= hit_chance:
            # Hit! Calculate damage
            base_dmg = self.weapon['damage'] * 2  # DOUBLE DAMAGE
            variance = random.uniform(DAMAGE_VARIANCE_MIN, DAMAGE_VARIANCE_MAX)
            base_dmg *= variance

            # Apply stat bonus
            if self.weapon['type'] == 'melee':
                stat_bonus = self.body * 3
            else:
                stat_bonus = self.reflexes * 2

            # Check crit
            crit_roll = random.randint(1, 100)
            if crit_roll <= self.get_crit_chance():
                crit_mult = self.weapon['crit_multiplier']
                is_crit = True
            else:
                crit_mult = 1.0
                is_crit = False

            # Morale
            morale_mod = self.get_morale_modifier()

            # Total damage (NO ARMOR!)
            total = (base_dmg + stat_bonus) * crit_mult * morale_mod
            total = max(1, int(total))

            # Apply damage
            target.take_damage(total)

            crit_text = " CRITICAL!" if is_crit else ""
            return total, f"{self.name} SPECIAL ATTACK on {target.name} for {total}{crit_text}!"

        else:
            return 0, f"{self.name} special attack missed!"
```

**5. Run Tests (Should Pass)**
```bash
$ pytest tests/test_character.py -k special_attack
============================== 4 passed in 0.15s ==============================
```

**6. Refactor**
```python
def special_attack(self, target):
    """Execute special attack costing 3 AP."""
    if not self._has_sufficient_ap(AP_SPECIAL_ABILITY):
        return None, "Not enough AP for special attack!"

    self._spend_ap(AP_SPECIAL_ABILITY)

    damage, hit = self._execute_special_attack(target)

    return self._format_attack_result(damage, hit, special=True)
```

---

## TESTING PATTERNS LIBRARY

### Pattern: Testing Randomness

**Problem:** Random values make tests unpredictable

**Solution:** Mock random functions

```python
from unittest.mock import patch

@patch('random.randint')
def test_initiative_with_known_roll(mock_randint):
    """Test initiative with controlled randomness."""
    mock_randint.return_value = 5  # Fixed d10 roll

    char = create_character(reflexes=6)
    initiative = char.get_initiative()

    # (6 × 2) + 5 = 17
    assert initiative == 17
    mock_randint.assert_called_once_with(1, 10)
```

**Multiple Random Calls:**
```python
@patch('random.randint')
@patch('random.uniform')
def test_damage_with_crit(mock_uniform, mock_randint):
    """Test damage calculation with controlled randomness."""
    mock_uniform.return_value = 1.0  # No variance
    mock_randint.side_effect = [5, 1]  # [crit roll, hit roll]

    damage, is_crit = char.calculate_damage(target)

    assert is_crit is True  # Roll of 1 <= crit chance
```

### Pattern: Testing State Changes

**Problem:** Need to verify state before and after

**Solution:** Capture initial state

```python
def test_taking_damage_reduces_hp():
    """Taking damage should reduce HP."""
    char = create_character(hp=100)
    initial_hp = char.hp

    char.take_damage(30)

    assert char.hp == initial_hp - 30
    assert char.is_alive is True

def test_taking_lethal_damage_kills_character():
    """Taking damage >= HP should kill character."""
    char = create_character(hp=50)

    char.take_damage(60)

    assert char.hp == 0
    assert char.is_alive is False
```

### Pattern: Testing Edge Cases

**Problem:** Normal tests don't cover boundaries

**Solution:** Explicit edge case tests

```python
def test_damage_minimum_one():
    """Damage should never be less than 1."""
    weak_attacker = create_character(body=1, reflexes=1)
    strong_defender = create_character(armor=100)

    damage, _ = weak_attacker.calculate_damage(strong_defender)

    assert damage >= 1

def test_hit_chance_capped_at_95():
    """Hit chance should never exceed 95%."""
    perfect_attacker = create_character()
    perfect_attacker.weapon['accuracy'] = 150
    helpless_target = create_character(reflexes=1)

    hit_chance = perfect_attacker.calculate_hit_chance(helpless_target)

    assert hit_chance <= 95

def test_dodge_capped_at_20():
    """Dodge chance should be capped at 20%."""
    agile_char = create_character(reflexes=10)

    dodge = agile_char.get_dodge_chance()

    assert dodge == 20  # Not 30
```

### Pattern: Parametrized Testing

**Problem:** Need to test same logic with different inputs

**Solution:** Use `@pytest.mark.parametrize`

```python
@pytest.mark.parametrize("reflexes,expected_dodge", [
    (1, 3),
    (3, 9),
    (5, 15),
    (7, 20),  # Capped
    (10, 20), # Capped
])
def test_dodge_chance_formula(reflexes, expected_dodge):
    """Test dodge chance for various reflexes values."""
    char = create_character(reflexes=reflexes)

    dodge = char.get_dodge_chance()

    assert dodge == expected_dodge

@pytest.mark.parametrize("weapon,expected_type", [
    ('assault_rifle', 'ranged'),
    ('pistol', 'ranged'),
    ('shotgun', 'ranged'),
    ('katana', 'melee'),
])
def test_weapon_types(weapon, expected_type):
    """Test weapon type classification."""
    char = create_character(weapon=weapon)

    assert char.weapon['type'] == expected_type
```

### Pattern: Testing Formulas

**Problem:** Complex math needs verification

**Solution:** Test with known inputs/outputs

```python
def test_morale_modifier_calculation():
    """Test morale modifier formula at key values."""
    char = create_character()

    # High morale (100)
    char.morale = 100
    assert char.get_morale_modifier() == 1.25

    # Neutral morale (50)
    char.morale = 50
    assert char.get_morale_modifier() == 1.0

    # Low morale (0)
    char.morale = 0
    assert char.get_morale_modifier() == 0.75

def test_movement_range_formula():
    """Test movement range calculation."""
    # BASE = 4, Bonus = Reflexes ÷ 4

    char = create_character(reflexes=0)
    assert char.movement_range == 4  # 4 + 0

    char.reflexes = 4
    assert char.movement_range == 5  # 4 + 1

    char.reflexes = 8
    assert char.movement_range == 6  # 4 + 2
```

### Pattern: Testing Side Effects

**Problem:** Action has multiple effects

**Solution:** Assert all effects

```python
def test_attack_has_all_effects():
    """Attack should: reduce AP, deal damage, log message."""
    attacker = create_character(ap=3)
    target = create_enemy(hp=100)

    initial_ap = attacker.ap
    initial_hp = target.hp

    with patch('random.randint', return_value=1):  # Guarantee hit
        damage, log_msg = attacker.attack(target)

        # Effect 1: AP reduced
        assert attacker.ap == initial_ap - AP_BASIC_ATTACK

        # Effect 2: Target took damage
        assert target.hp < initial_hp

        # Effect 3: Message logged
        assert attacker.name in log_msg
        assert target.name in log_msg
        assert str(damage) in log_msg
```

---

## COMMON TESTING SCENARIOS

### Scenario: New Character Stat

**Adding "Luck" stat that affects crit chance:**

```python
# TEST 1: Initialization
def test_character_has_luck_stat():
    """Character should have luck attribute."""
    stats = {
        'body': 5, 'reflexes': 5, 'intelligence': 5,
        'tech': 5, 'cool': 5, 'luck': 7,  # NEW STAT
        'max_hp': 100, 'armor': 10
    }
    char = Character("Test", 0, 0, stats, 'pistol', 'player')

    assert hasattr(char, 'luck')
    assert char.luck == 7

# TEST 2: Affects crit chance
def test_luck_increases_crit_chance():
    """Luck should increase critical hit chance."""
    char = create_character(cool=5, luck=3)

    # New formula: (Cool × 2) + Luck
    crit_chance = char.get_crit_chance()

    assert crit_chance == 13  # (5 × 2) + 3

# TEST 3: Edge cases
def test_high_luck_doesnt_break_crit():
    """High luck shouldn't make crit chance > 100%."""
    char = create_character(cool=10, luck=100)

    crit_chance = char.get_crit_chance()

    assert crit_chance <= 100
```

### Scenario: New Combat Action

**Adding "Aim" action (1 AP, +20% hit chance next attack):**

```python
# TEST 1: Basic functionality
def test_aim_action_costs_1_ap():
    """Aim action should cost 1 AP."""
    char = create_character()
    initial_ap = char.ap

    char.aim()

    assert char.ap == initial_ap - 1

def test_aim_sets_aiming_flag():
    """Aim should set 'is_aiming' flag."""
    char = create_character()

    char.aim()

    assert char.is_aiming is True

# TEST 2: Affects next attack
def test_aiming_increases_hit_chance():
    """Being aimed should increase hit chance by 20%."""
    attacker = create_character()
    target = create_enemy()

    base_hit = attacker.calculate_hit_chance(target)

    attacker.aim()
    aimed_hit = attacker.calculate_hit_chance(target)

    assert aimed_hit == base_hit + 20

# TEST 3: Resets after attack
def test_aiming_resets_after_attack():
    """Aiming flag should reset after attacking."""
    char = create_character()
    char.aim()

    char.attack(create_enemy())

    assert char.is_aiming is False

# TEST 4: Edge cases
def test_cannot_aim_without_ap():
    """Cannot aim if not enough AP."""
    char = create_character()
    char.ap = 0

    result = char.aim()

    assert result is False
```

### Scenario: System Integration

**Testing combat encounter with new mechanics:**

```python
@pytest.mark.integration
def test_full_combat_with_special_attacks():
    """Test complete combat using special attacks."""
    player = create_character(weapon='katana')
    enemy = create_enemy()

    combat = CombatEncounter([player], [enemy])

    # Turn 1: Move + Attack
    player.move(enemy.x - 1, enemy.y)
    player.attack(enemy)
    combat.next_turn()

    # Turn 2: Special attack
    enemy_hp_before = enemy.hp
    player.special_attack(enemy)

    # Verify special attack effects
    assert enemy.hp < enemy_hp_before
    assert player.ap == 0  # Used all 3 AP

    combat.check_victory()
```

---

## MOCKING AND STUBBING

### When to Mock

**Mock External Dependencies:**
```python
# Mock file I/O
@patch('builtins.open', mock_open(read_data='{"level": 5}'))
def test_load_save_file():
    char = load_character('save.json')
    assert char.level == 5

# Mock network calls
@patch('requests.get')
def test_fetch_leaderboard(mock_get):
    mock_get.return_value.json.return_value = [{'name': 'Player1', 'score': 1000}]

    leaderboard = fetch_leaderboard()

    assert leaderboard[0]['name'] == 'Player1'
```

**Mock Randomness:**
```python
@patch('random.choice')
def test_loot_drop(mock_choice):
    """Test loot drop with controlled randomness."""
    mock_choice.return_value = 'rare_item'

    loot = enemy.drop_loot()

    assert loot == 'rare_item'
```

**Mock Time:**
```python
@patch('time.time')
def test_buff_duration(mock_time):
    """Test buff expires after duration."""
    mock_time.side_effect = [0, 5, 11]  # Start, check, expired

    char.apply_buff('strength', duration=10)

    assert char.has_buff('strength') is True  # t=5
    mock_time.return_value = 11
    assert char.has_buff('strength') is False  # t=11 (expired)
```

### What NOT to Mock

**Don't Mock Core Logic:**
```python
# BAD: Mocking the thing you're testing
@patch('character.Character.calculate_damage')
def test_damage_calculation(mock_damage):
    mock_damage.return_value = 50

    damage = char.calculate_damage(target)

    assert damage == 50  # This tests nothing!

# GOOD: Test actual implementation
def test_damage_calculation():
    char = create_character(reflexes=6)
    target = create_enemy(armor=10)

    with patch_randomness():
        damage = char.calculate_damage(target)

    # Assert based on formula
    assert 40 <= damage <= 60  # Expected range
```

---

## TEST DATA MANAGEMENT

### Fixture Organization

**Character Fixtures:**
```python
# conftest.py
@pytest.fixture
def standard_player():
    """Balanced player character."""
    return create_character(
        body=5, reflexes=6, cool=6,
        hp=150, armor=20, weapon='assault_rifle'
    )

@pytest.fixture
def melee_specialist():
    """Melee-focused character."""
    return create_character(
        body=9, reflexes=6, cool=7,
        hp=200, armor=30, weapon='katana'
    )

@pytest.fixture
def glass_cannon():
    """High damage, low defense."""
    return create_character(
        body=3, reflexes=10, cool=8,
        hp=80, armor=5, weapon='pistol'
    )

# Use in tests
def test_melee_damage(melee_specialist):
    """Melee specialist should deal high damage."""
    target = create_enemy()

    damage, _ = melee_specialist.calculate_damage(target)

    assert damage >= 50
```

### Test Data Builders

**Builder Pattern:**
```python
class CharacterBuilder:
    """Fluent builder for test characters."""

    def __init__(self):
        self.stats = {
            'body': 5, 'reflexes': 5, 'intelligence': 5,
            'tech': 5, 'cool': 5, 'max_hp': 100, 'armor': 10
        }
        self.weapon = 'pistol'
        self.position = (0, 0)

    def with_high_body(self):
        self.stats['body'] = 10
        return self

    def with_low_reflexes(self):
        self.stats['reflexes'] = 1
        return self

    def with_weapon(self, weapon):
        self.weapon = weapon
        return self

    def at_position(self, x, y):
        self.position = (x, y)
        return self

    def build(self):
        return Character("Test", *self.position, self.stats, self.weapon, 'player')

# Usage
def test_with_builder():
    char = (CharacterBuilder()
            .with_high_body()
            .with_weapon('katana')
            .at_position(5, 5)
            .build())

    assert char.body == 10
    assert char.weapon['name'] == 'Katana'
```

---

## EDGE CASE CATALOG

### Numerical Edge Cases

```python
# Zero values
def test_zero_damage():
    char = create_character()
    char.weapon['damage'] = 0
    # Should still deal at least 1 damage

def test_zero_armor():
    char = create_character(armor=0)
    # Should take full damage

# Negative values
def test_negative_hp_clamped():
    char = create_character(hp=10)
    char.take_damage(50)
    assert char.hp == 0  # Not -40

# Maximum values
def test_max_stats():
    char = create_character(body=10, reflexes=10, cool=10)
    # Should still function correctly

# Minimum values
def test_min_stats():
    char = create_character(body=1, reflexes=1, cool=1)
    # Should still function correctly
```

### Boundary Conditions

```python
# Exact values
def test_damage_exactly_equals_hp():
    char = create_character(hp=50)
    char.take_damage(50)
    assert char.hp == 0
    assert char.is_alive is False

def test_hit_chance_exactly_95():
    # Test clamping at exact boundary
    hit_chance = calculate_hit_chance(...)
    # Ensure doesn't exceed 95

# Off-by-one
def test_movement_at_exact_range():
    char = create_character()
    max_range = char.movement_range

    # Should succeed at exact range
    success, _ = char.move(char.x + max_range, char.y)
    assert success is True

def test_movement_one_beyond_range():
    char = create_character()
    max_range = char.movement_range

    # Should fail one beyond range
    success, _ = char.move(char.x + max_range + 1, char.y)
    assert success is False
```

### State Transitions

```python
# Alive → Dead
def test_character_death_transition():
    char = create_character(hp=50)

    char.take_damage(50)

    assert char.hp == 0
    assert char.is_alive is False

# Full AP → No AP
def test_spending_all_ap():
    char = create_character()
    char.ap = 3

    char.special_attack(target)

    assert char.ap == 0

# Combat Start → Combat End
def test_combat_victory_transition():
    combat = create_combat()

    for enemy in combat.enemy_team:
        enemy.hp = 0
        enemy.is_alive = False

    combat.check_victory()

    assert combat.combat_active is False
    assert combat.victor == 'player'
```

---

## INTEGRATION TESTING

### Full Combat Scenario

```python
@pytest.mark.integration
def test_complete_combat_scenario():
    """Test a complete combat from start to finish."""
    # Setup
    player = create_character()
    ally = create_character()
    enemy1 = create_enemy()
    enemy2 = create_enemy()

    combat = CombatEncounter([player, ally], [enemy1, enemy2])

    # Verify initialization
    assert combat.combat_active is True
    assert len(combat.turn_order) == 4

    # Simulate combat
    max_turns = 20
    turns = 0

    while combat.combat_active and turns < max_turns:
        current = combat.current_character

        if current.team == 'player':
            # Player turn: move and attack
            targets = combat.get_valid_targets(current)
            if targets and current.ap >= 2:
                current.attack(targets[0])
        else:
            # Enemy AI turn
            combat.enemy_ai_turn(current)

        combat.next_turn()
        turns += 1

    # Verify outcome
    assert combat.combat_active is False
    assert combat.victor in ['player', 'enemy']
    assert turns < max_turns  # Didn't timeout
```

---

**END OF TESTING BIBLE**

*This document provides TDD patterns and practices for developing Neon Collapse. Use these patterns when adding new features or systems.*
