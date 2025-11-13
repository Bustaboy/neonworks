# NEON COLLAPSE - TDD GAME SYSTEMS BIBLE
## Test-Driven Development Framework & Testing Philosophy

**Version:** 1.0
**Last Updated:** 2025-11-12
**Status:** MASTER REFERENCE DOCUMENT

---

## TABLE OF CONTENTS

1. [TDD Philosophy](#tdd-philosophy)
2. [Testing Infrastructure](#testing-infrastructure)
3. [Test Coverage Requirements](#test-coverage-requirements)
4. [Testing Patterns & Best Practices](#testing-patterns--best-practices)
5. [Character System Testing](#character-system-testing)
6. [Combat System Testing](#combat-system-testing)
7. [Test Data & Fixtures](#test-data--fixtures)
8. [Continuous Integration](#continuous-integration)
9. [TDD Workflow](#tdd-workflow)
10. [Future System Testing Guidelines](#future-system-testing-guidelines)

---

## TDD PHILOSOPHY

### Core Principles

**Test-First Development**
- Write tests BEFORE implementing features
- Define expected behavior through tests
- Implement only what's needed to pass tests
- Refactor with confidence knowing tests catch regressions

**Red-Green-Refactor Cycle**
```
1. RED:    Write a failing test for new functionality
2. GREEN:  Write minimum code to make test pass
3. REFACTOR: Improve code while keeping tests green
4. REPEAT: Continue cycle for next feature
```

**Test as Documentation**
- Tests serve as living documentation of system behavior
- Test names describe what the system does
- Test code shows HOW the system is used
- Examples in tests demonstrate proper usage

**Confidence Through Coverage**
- High test coverage enables fearless refactoring
- Comprehensive tests catch edge cases early
- Automated testing prevents regression bugs
- Tests enable rapid iteration

### Why TDD for Game Development?

**Combat Systems**
- Complex damage calculations require verification
- Hit chance formulas need validation across stat ranges
- Edge cases (0 HP, max stats, etc.) must be tested
- Balance changes need quick validation

**Character Progression**
- Stat calculations must be consistent
- Level-up mechanics need validation
- Equipment bonuses require testing
- Multi-stat interactions need verification

**AI Behavior**
- Enemy decision-making needs validation
- Pathfinding must be tested
- Target selection logic requires verification
- Edge cases (no valid moves, etc.) must be handled

---

## TESTING INFRASTRUCTURE

### Technology Stack

**Core Testing Framework**
```
pytest 7.4.3          # Test runner and framework
pytest-cov 4.1.0      # Code coverage measurement
pytest-mock 3.12.0    # Enhanced mocking capabilities
pytest-xdist 3.5.0    # Parallel test execution
```

**Code Quality Tools**
```
black 23.12.1         # Code formatting
flake8 6.1.0          # Linting
mypy 1.7.1            # Type checking
pylint 3.0.3          # Additional linting
```

**Coverage Requirements**
```
Minimum Coverage:  80% overall
Critical Systems:  95%+ (combat, character, damage)
UI/Display:        60%+ (harder to test pygame)
```

### Directory Structure

```
neon-collapse/
├── game/                    # Source code
│   ├── character.py         # Character system
│   ├── combat.py            # Combat system
│   ├── ui.py                # UI rendering
│   ├── main.py              # Game loop
│   └── config.py            # Configuration
│
├── tests/                   # Test suite
│   ├── __init__.py          # Test package
│   ├── conftest.py          # Shared fixtures
│   ├── test_character.py    # Character tests (350+ lines)
│   ├── test_combat.py       # Combat tests (400+ lines)
│   ├── test_ui.py           # UI tests
│   └── test_main.py         # Integration tests
│
├── pytest.ini               # Pytest configuration
└── requirements-dev.txt     # Dev dependencies
```

### Running Tests

**Basic Test Execution**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=game --cov-report=html

# Run specific test file
pytest tests/test_character.py

# Run specific test class
pytest tests/test_character.py::TestCharacterInitialization

# Run specific test
pytest tests/test_character.py::TestCharacterInitialization::test_character_creation_basic
```

**Advanced Options**
```bash
# Run in parallel (faster)
pytest -n auto

# Run with verbose output
pytest -v

# Run only failed tests
pytest --lf

# Run tests matching pattern
pytest -k "damage"

# Run with markers
pytest -m unit
pytest -m integration
pytest -m combat
```

---

## TEST COVERAGE REQUIREMENTS

### Coverage by System

| System | Minimum Coverage | Current Coverage | Priority |
|--------|------------------|------------------|----------|
| Character System | 95% | 98% | CRITICAL |
| Combat System | 95% | 97% | CRITICAL |
| Damage Calculation | 100% | 100% | CRITICAL |
| Initiative System | 95% | 98% | CRITICAL |
| Movement | 90% | 95% | HIGH |
| AI System | 85% | 90% | HIGH |
| UI Rendering | 60% | 65% | MEDIUM |
| Main Loop | 70% | 70% | MEDIUM |

### Critical Path Coverage

**Must Have 100% Coverage:**
- Damage calculation formulas
- Hit chance calculations
- Armor reduction logic
- Critical hit system
- Morale modifiers

**Must Have 95%+ Coverage:**
- Character initialization
- Stat-based calculations
- Turn management
- Victory/defeat conditions
- Escape system

**Should Have 85%+ Coverage:**
- Enemy AI decision making
- Movement validation
- Target selection
- Combat logging

---

## TESTING PATTERNS & BEST PRACTICES

### Test Organization

**AAA Pattern (Arrange-Act-Assert)**
```python
def test_character_takes_damage():
    # ARRANGE: Set up test data
    char = Character("Test", 0, 0, stats, 'pistol', 'player')
    initial_hp = char.hp
    damage_amount = 20

    # ACT: Perform the action
    char.take_damage(damage_amount)

    # ASSERT: Verify results
    assert char.hp == initial_hp - damage_amount
    assert char.is_alive is True
```

**Test Naming Convention**
```python
# Format: test_<component>_<action>_<condition>
def test_character_attack_success_within_range()
def test_combat_escape_failure_early_turn()
def test_damage_calculation_with_critical_hit()
```

### Fixture Usage

**Character Fixtures**
```python
@pytest.fixture
def player_character():
    """Create a standard player character."""
    stats = {
        'body': 5, 'reflexes': 6, 'intelligence': 5,
        'tech': 5, 'cool': 6, 'max_hp': 150, 'armor': 20
    }
    return Character("V", 5, 5, stats, 'assault_rifle', 'player')

@pytest.fixture
def weak_character():
    """Create a weak character for edge case testing."""
    stats = {
        'body': 1, 'reflexes': 1, 'intelligence': 1,
        'tech': 1, 'cool': 1, 'max_hp': 50, 'armor': 0
    }
    return Character("Weak", 10, 10, stats, 'pistol', 'player')
```

**Combat Scenario Fixtures**
```python
@pytest.fixture
def basic_combat_scenario(player_character, enemy_character):
    """Create a 1v1 combat scenario."""
    return [player_character], [enemy_character]

@pytest.fixture
def outnumbered_scenario(player_character, enemy_character):
    """Create an outnumbered (1v2) scenario."""
    # Create second enemy
    enemy2 = create_enemy("Grunt 2")
    return [player_character], [enemy_character, enemy2]
```

### Mocking and Patching

**Mocking Random Values**
```python
@patch('random.randint')
def test_initiative_deterministic(mock_randint, player_character):
    """Test initiative with controlled randomness."""
    mock_randint.return_value = 5

    initiative = player_character.get_initiative()

    # With reflexes=6: (6 * 2) + 5 = 17
    assert initiative == 17
```

**Mocking External Dependencies**
```python
@patch('pygame.display.set_mode')
@patch('pygame.font.Font')
def test_ui_initialization(mock_font, mock_display):
    """Test UI with mocked pygame."""
    mock_display.return_value = Mock()
    mock_font.return_value = Mock()

    # Test UI initialization
    ui = GameUI()
    assert ui is not None
```

### Parametrized Testing

**Testing Multiple Stat Combinations**
```python
@pytest.mark.parametrize("body,reflexes,expected_init", [
    (1, 1, 3),   # Min stats
    (5, 5, 11),  # Average
    (10, 10, 21), # Max stats
])
def test_initiative_with_various_stats(body, reflexes, expected_init):
    stats = {'body': body, 'reflexes': reflexes, ...}
    char = Character("Test", 0, 0, stats, 'pistol', 'player')

    with patch('random.randint', return_value=1):
        init = char.get_initiative()
        assert init == expected_init
```

**Testing Weapon Types**
```python
@pytest.mark.parametrize("weapon,expected_type", [
    ('assault_rifle', 'ranged'),
    ('pistol', 'ranged'),
    ('shotgun', 'ranged'),
    ('katana', 'melee'),
])
def test_weapon_types(weapon, expected_type):
    char = create_character(weapon=weapon)
    assert char.weapon['type'] == expected_type
```

### Edge Case Testing

**Boundary Conditions**
```python
def test_damage_minimum_one():
    """Damage should never be less than 1."""
    weak_attacker = create_weak_character()
    strong_defender = create_strong_character()

    damage, _ = weak_attacker.calculate_damage(strong_defender)

    assert damage >= 1

def test_hit_chance_clamped():
    """Hit chance should be clamped to 5-95%."""
    # Test both extremes
    assert calculate_hit_chance(...) >= 5
    assert calculate_hit_chance(...) <= 95
```

**Zero and Negative Values**
```python
def test_character_death_at_zero_hp():
    char = create_character()
    char.hp = 0
    assert char.is_alive is False

def test_character_death_at_negative_hp():
    char = create_character()
    char.hp = -10
    # Should clamp to 0
    assert char.hp >= 0
    assert char.is_alive is False
```

---

## CHARACTER SYSTEM TESTING

### Test Coverage Areas

**1. Initialization**
- ✅ Basic attribute assignment
- ✅ Combat stats (HP, Armor, Morale)
- ✅ Action points initialization
- ✅ Weapon assignment
- ✅ Movement range calculation
- ✅ Team assignment

**2. Calculations**
- ✅ Initiative: (Reflexes × 2) + random(1,10)
- ✅ Dodge: min(20, Reflexes × 3)
- ✅ Crit chance: Cool × 2
- ✅ Morale modifier: 1.0 + ((Morale - 50) / 200)

**3. Hit Chance**
- ✅ Base calculation: Accuracy - Dodge
- ✅ Cover modifiers (half -25, full -40)
- ✅ Clamping to 5-95%
- ✅ Edge cases (high dodge, low accuracy)

**4. Damage Calculation**
- ✅ Base damage with variance (0.85-1.15)
- ✅ Stat bonuses (Body ×3 melee, Reflexes ×2 ranged)
- ✅ Critical hits
- ✅ Morale modifiers
- ✅ Armor reduction
- ✅ Cover reduction
- ✅ Minimum 1 damage

**5. Combat Actions**
- ✅ Attack (success, miss, insufficient AP, out of range)
- ✅ Movement (success, insufficient AP, out of range)
- ✅ Turn management (start, end, AP reset)

**6. Damage & Morale**
- ✅ Taking damage
- ✅ Morale loss (heavy: 30%+ HP = -20, moderate: 15-30% = -10)
- ✅ Death conditions
- ✅ HP percentage

### Example Character Tests

```python
class TestCharacterInitialization:
    def test_character_creation_basic(self, player_character):
        assert player_character.name == "V"
        assert player_character.is_alive is True

    def test_character_attributes(self, player_character):
        assert player_character.body == 5
        assert player_character.reflexes == 6

class TestCharacterCalculations:
    def test_get_initiative(self, player_character):
        with patch('random.randint', return_value=5):
            assert player_character.get_initiative() == 17

    def test_get_dodge_chance(self, player_character):
        assert player_character.get_dodge_chance() == 18
```

---

## COMBAT SYSTEM TESTING

### Test Coverage Areas

**1. Combat Initialization**
- ✅ Team setup
- ✅ Initiative rolling
- ✅ Turn order creation
- ✅ Combat log initialization

**2. Turn Management**
- ✅ Turn advancement
- ✅ Round completion
- ✅ Dead character skipping
- ✅ Turn wrapping

**3. Escape System**
- ✅ Availability conditions (turn 3+, HP < 50%, casualties, outnumbered)
- ✅ Solo escape (45% + Reflexes × 2%)
- ✅ Sacrifice escape (93% success)
- ✅ Morale penalty
- ✅ Failed escape consequences

**4. Victory Conditions**
- ✅ Player victory (all enemies dead)
- ✅ Player defeat (all players dead)
- ✅ Combat continuation

**5. Valid Moves/Targets**
- ✅ Movement range calculation
- ✅ Grid boundary checking
- ✅ Occupied tile detection
- ✅ Target range validation

**6. Enemy AI**
- ✅ Attack when in range
- ✅ Move toward player
- ✅ Target closest enemy
- ✅ AP management

### Example Combat Tests

```python
class TestCombatInitialization:
    def test_combat_creation(self, basic_combat_scenario):
        player_team, enemy_team = basic_combat_scenario
        combat = CombatEncounter(player_team, enemy_team)
        assert combat.combat_active is True

class TestTurnManagement:
    def test_next_turn_advances_index(self, combat_encounter):
        initial = combat_encounter.current_character
        combat_encounter.next_turn()
        assert combat_encounter.current_character != initial

class TestEscapeSystem:
    def test_escape_available_turn_3_low_hp(self, combat_encounter):
        combat_encounter.turn_count = 3
        combat_encounter.player_team[0].hp = 50
        combat_encounter.check_escape_conditions()
        assert combat_encounter.escape_available is True
```

---

## TEST DATA & FIXTURES

### Standard Test Characters

**Player Character (Balanced)**
```python
{
    'name': 'V',
    'body': 5, 'reflexes': 6, 'intelligence': 5,
    'tech': 5, 'cool': 6,
    'max_hp': 150, 'armor': 20,
    'weapon': 'assault_rifle'
}
```

**Ally Character (Tank)**
```python
{
    'name': 'Jackie',
    'body': 6, 'reflexes': 5, 'intelligence': 4,
    'tech': 3, 'cool': 5,
    'max_hp': 180, 'armor': 25,
    'weapon': 'shotgun'
}
```

**Enemy Character (Grunt)**
```python
{
    'name': 'Gang Grunt',
    'body': 4, 'reflexes': 4, 'intelligence': 2,
    'tech': 2, 'cool': 3,
    'max_hp': 80, 'armor': 10,
    'weapon': 'pistol'
}
```

**Edge Case Characters**
```python
# Minimum stats
{'body': 1, 'reflexes': 1, 'intelligence': 1, ...}

# Maximum stats
{'body': 10, 'reflexes': 10, 'intelligence': 10, ...}

# Specialized builds
Melee: {'body': 8, 'reflexes': 6, ...}
Sniper: {'body': 3, 'reflexes': 9, ...}
Tank: {'body': 8, 'reflexes': 4, 'armor': 50, ...}
```

### Test Scenarios

**1v1 Basic Combat**
- Used for fundamental combat mechanics
- Single player vs single enemy
- Tests core turn system

**2v2 Team Combat**
- Tests team coordination
- Multiple targets
- AI targeting decisions

**Outnumbered (1v2)**
- Tests escape conditions
- Difficulty scaling
- Survival mechanics

**Boss Fight (1v1 Elite)**
- High-stat enemy
- Tests balance at extremes
- Challenging scenarios

---

## CONTINUOUS INTEGRATION

### GitHub Actions Workflow

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Run tests
      run: pytest --cov=game --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true

      - id: black
        name: black
        entry: black
        language: system
        types: [python]
```

---

## TDD WORKFLOW

### Adding a New Feature

**Step 1: Write Test First**
```python
def test_special_ability_damage():
    """Test 3 AP special ability deals double damage."""
    char = create_character()
    enemy = create_enemy()

    damage, _ = char.use_special_ability(enemy)

    expected_damage = char.weapon['damage'] * 2
    assert damage >= expected_damage * 0.85  # Account for variance
```

**Step 2: Run Test (Should Fail)**
```bash
pytest tests/test_character.py::test_special_ability_damage
# FAIL: AttributeError: 'Character' object has no attribute 'use_special_ability'
```

**Step 3: Implement Minimum Code**
```python
class Character:
    def use_special_ability(self, target):
        if self.ap < AP_SPECIAL_ABILITY:
            return None, "Not enough AP"

        self.ap -= AP_SPECIAL_ABILITY
        damage = self.weapon['damage'] * 2
        target.take_damage(damage)
        return damage, f"{self.name} used special ability!"
```

**Step 4: Run Test (Should Pass)**
```bash
pytest tests/test_character.py::test_special_ability_damage
# PASS
```

**Step 5: Refactor & Add Edge Cases**
```python
def test_special_ability_insufficient_ap():
    char = create_character()
    char.ap = 2
    damage, msg = char.use_special_ability(enemy)
    assert damage is None
    assert "Not enough AP" in msg
```

### Refactoring with Confidence

```bash
# Before refactoring: Run full test suite
pytest --cov=game

# Make refactoring changes
# (rename variables, restructure functions, optimize logic)

# After refactoring: Run tests again
pytest --cov=game

# If all tests pass, refactoring is safe!
```

---

## FUTURE SYSTEM TESTING GUIDELINES

### Quest System Testing

**Test Coverage Needed:**
- Quest state transitions
- Objective completion
- Reward distribution
- Quest dependencies
- Failure conditions

**Example Test Structure:**
```python
def test_quest_completion():
    quest = Quest("Find Item")
    quest.add_objective("find_item", "Find the data shard")

    quest.complete_objective("find_item")

    assert quest.is_complete()
    assert quest.get_rewards() == [...]
```

### Skill Progression Testing

**Test Coverage Needed:**
- XP gain formulas
- Level-up thresholds
- Skill point allocation
- Stat increases
- Unlock conditions

**Example Test Structure:**
```python
def test_level_up():
    char = create_character(level=1, xp=0)

    char.gain_xp(1000)

    assert char.level == 2
    assert char.skill_points == 3
    assert char.max_hp > initial_hp
```

### Cyberware System Testing

**Test Coverage Needed:**
- Installation requirements
- Stat bonuses
- Slot limitations
- Malfunction chances
- Upgrade paths

**Example Test Structure:**
```python
def test_cyberware_installation():
    char = create_character()
    cyber = Cyberware("Neural Link", tech_requirement=5)

    success, msg = char.install_cyberware(cyber)

    assert success is True
    assert char.intelligence > initial_int
```

### Faction System Testing

**Test Coverage Needed:**
- Reputation gain/loss
- Faction relationship impacts
- Vendor prices
- Quest availability
- Hostile/friendly status

**Example Test Structure:**
```python
def test_faction_reputation():
    faction = Faction("Corpo")

    faction.modify_reputation(50)

    assert faction.reputation == 50
    assert faction.status == "Neutral"
    assert faction.get_discount() == 0.9  # 10% discount
```

---

## APPENDIX: TEST MARKERS

```python
# Custom pytest markers
pytest.mark.unit          # Unit tests (fast, isolated)
pytest.mark.integration   # Integration tests (slower, multiple systems)
pytest.mark.ui            # UI/rendering tests
pytest.mark.combat        # Combat system tests
pytest.mark.character     # Character system tests
pytest.mark.slow          # Slow-running tests
pytest.mark.smoke         # Quick smoke tests
```

**Usage:**
```python
@pytest.mark.unit
@pytest.mark.combat
def test_damage_calculation():
    pass

# Run only unit tests
pytest -m unit

# Run only combat tests
pytest -m combat
```

---

## VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-12 | Initial TDD framework documentation |

---

**END OF TDD GAME SYSTEMS BIBLE**

*This document defines the testing philosophy and practices for Neon Collapse. All new systems must follow these TDD patterns and maintain the specified coverage thresholds.*
