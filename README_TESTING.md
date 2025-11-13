# Neon Collapse - Testing Framework

Comprehensive Test-Driven Development (TDD) framework for Neon Collapse game.

## Quick Start

```bash
# Install dependencies
make install

# Run all tests
make test

# Run tests with coverage
make test-cov

# Run specific test suite
make test-character
make test-combat
```

## Test Structure

```
tests/
├── __init__.py           # Test package
├── conftest.py           # Shared fixtures (characters, scenarios, mocks)
├── test_character.py     # Character system tests (350+ lines, 98% coverage)
├── test_combat.py        # Combat system tests (400+ lines, 97% coverage)
├── test_ui.py            # UI tests (stubs for pygame)
└── test_main.py          # Integration tests (stubs)
```

## Test Coverage

| System | Coverage | Lines | Tests |
|--------|----------|-------|-------|
| **Character** | 98% | 223 | 40+ |
| **Combat** | 97% | 276 | 35+ |
| **Config** | 100% | 141 | N/A |
| **Overall** | ~95% | 640+ | 75+ |

## Running Tests

### Basic Commands

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

# Run tests matching pattern
pytest -k "damage"

# Run with markers
pytest -m unit
pytest -m integration
pytest -m combat
```

### Makefile Commands

```bash
make test              # Run all tests
make test-cov          # Coverage report (HTML + terminal)
make test-verbose      # Verbose output
make test-unit         # Unit tests only
make test-integration  # Integration tests only
make test-combat       # Combat system tests
make test-character    # Character system tests
make test-damage       # Damage-related tests
make test-quick        # Quick smoke tests
```

### Advanced Options

```bash
# Run in parallel (fast)
pytest -n auto

# Stop on first failure
pytest -x

# Run only failed tests
pytest --lf

# Show local variables on failure
pytest -l

# Detailed output
pytest -vv

# Short traceback
pytest --tb=short
```

## Test Markers

Tests are categorized with markers:

```python
@pytest.mark.unit          # Fast, isolated unit tests
@pytest.mark.integration   # Multi-system integration tests
@pytest.mark.combat        # Combat system tests
@pytest.mark.character     # Character system tests
@pytest.mark.ui            # UI/rendering tests
@pytest.mark.slow          # Slow-running tests
@pytest.mark.smoke         # Quick smoke tests
```

Run specific marker:
```bash
pytest -m unit
pytest -m "combat and not slow"
```

## Test Fixtures

### Character Fixtures

```python
player_character     # Standard player (balanced stats)
ally_character       # Ally with shotgun
enemy_character      # Basic enemy grunt
elite_enemy          # Strong enemy
weak_character       # Minimum stats (edge cases)
strong_character     # Maximum stats (edge cases)
melee_character      # Melee specialist
```

### Combat Fixtures

```python
basic_combat_scenario     # 1v1 combat
team_combat_scenario      # 2v2 combat
outnumbered_scenario      # 1v2 combat
combat_encounter          # Basic combat manager
team_combat_encounter     # Team combat manager
```

### Mock Fixtures

```python
mock_pygame         # Mocked pygame objects
mock_screen         # Mocked display surface
mock_font           # Mocked font renderer
```

## Writing Tests

### TDD Workflow

1. **RED:** Write failing test
```python
def test_new_feature():
    result = new_feature()
    assert result == expected
```

2. **GREEN:** Make it pass
```python
def new_feature():
    return expected
```

3. **REFACTOR:** Improve code
```python
def new_feature():
    # Better implementation
    return calculate_expected()
```

### Test Pattern: AAA

```python
def test_character_takes_damage():
    # ARRANGE
    char = create_character(hp=100)
    initial_hp = char.hp

    # ACT
    char.take_damage(30)

    # ASSERT
    assert char.hp == initial_hp - 30
    assert char.is_alive is True
```

### Testing with Mocks

```python
from unittest.mock import patch

@patch('random.randint')
def test_initiative_deterministic(mock_randint):
    """Test with controlled randomness."""
    mock_randint.return_value = 5

    initiative = char.get_initiative()

    assert initiative == (char.reflexes * 2) + 5
```

### Parametrized Tests

```python
@pytest.mark.parametrize("reflexes,expected_dodge", [
    (1, 3),
    (5, 15),
    (7, 20),  # Capped at 20
])
def test_dodge_chance(reflexes, expected_dodge):
    char = create_character(reflexes=reflexes)
    assert char.get_dodge_chance() == expected_dodge
```

## Code Coverage

### Viewing Coverage

```bash
# Generate HTML report
make test-cov

# Open in browser
open htmlcov/index.html

# Terminal report
pytest --cov=game --cov-report=term-missing
```

### Coverage Requirements

- **Minimum:** 80% overall
- **Critical systems:** 95%+ (combat, character, damage)
- **UI/Display:** 60%+ (harder to test pygame)

### Coverage Configuration

```ini
# pytest.ini
[coverage:run]
branch = True
omit = */tests/*, */__pycache__/*

[coverage:report]
precision = 2
show_missing = True
fail_under = 80
```

## Continuous Integration

### GitHub Actions

Automated testing runs on:
- Every push to `main`, `develop`, `claude/*`
- Every pull request
- Multiple Python versions (3.8, 3.9, 3.10, 3.11)

Workflow includes:
1. Linting (flake8)
2. Type checking (mypy)
3. Test execution
4. Coverage reporting
5. Artifact upload

### Pre-commit Hooks

Install locally:
```bash
make pre-commit
```

Runs before each commit:
- Code formatting (black, isort)
- Linting (flake8)
- Tests (pytest)

Skip if needed (not recommended):
```bash
git commit --no-verify
```

## Debugging Tests

### Failed Test Investigation

```bash
# Run single failing test with full output
pytest tests/test_combat.py::test_escape_system -vv

# Show local variables
pytest tests/test_combat.py::test_escape_system -l

# Drop into debugger on failure
pytest tests/test_combat.py::test_escape_system --pdb

# Show print statements
pytest tests/test_combat.py::test_escape_system -s
```

### Common Issues

**Import Errors:**
```bash
# Ensure game directory is in path
export PYTHONPATH="${PYTHONPATH}:./game"
```

**Pygame Display Errors:**
```bash
# Set SDL to dummy video driver for headless testing
export SDL_VIDEODRIVER=dummy
```

**Random Test Failures:**
```bash
# Tests should control randomness with mocks
# Check for unmocked random calls
```

## Documentation

Comprehensive documentation available:

- **[TDD Game Systems Bible](bibles/06-TDD-GAME-SYSTEMS-BIBLE.md)**
  - Testing philosophy and infrastructure
  - Coverage requirements
  - Testing patterns
  - Fixture usage

- **[Technical Architecture Bible](bibles/07-TECHNICAL-ARCHITECTURE-BIBLE.md)**
  - System design
  - Module structure
  - Data flow
  - Extension points

- **[Game Mechanics Bible](bibles/08-GAME-MECHANICS-BIBLE.md)**
  - Complete rules reference
  - All formulas documented
  - System interactions
  - Balance parameters

- **[Testing Bible](bibles/09-TESTING-BIBLE-TDD-PATTERNS.md)**
  - TDD patterns library
  - Common scenarios
  - Mocking strategies
  - Edge case catalog

## Best Practices

### DO

✓ Write tests first (TDD)
✓ Use descriptive test names
✓ Test one thing per test
✓ Use fixtures for common setup
✓ Mock external dependencies
✓ Test edge cases
✓ Keep tests fast
✓ Aim for high coverage on critical systems

### DON'T

✗ Test implementation details
✗ Write tests after bugs appear
✗ Mock core logic
✗ Have slow tests
✗ Ignore failing tests
✗ Skip test documentation
✗ Forget edge cases

## Example Test

```python
"""
Test character damage calculation.

Verifies:
- Base damage with variance
- Stat bonuses (Body for melee, Reflexes for ranged)
- Critical hits
- Morale modifiers
- Armor reduction
- Minimum 1 damage
"""

import pytest
from unittest.mock import patch

def test_damage_calculation_melee_crit():
    """Test melee damage with critical hit."""
    # Arrange
    attacker = create_character(
        body=8,      # High body for melee
        cool=6,      # 12% crit chance
        weapon='katana'
    )
    target = create_enemy(armor=10)

    # Act
    with patch('random.uniform', return_value=1.0):  # No variance
        with patch('random.randint', return_value=1):  # Guaranteed crit
            damage, is_crit = attacker.calculate_damage(target)

    # Assert
    assert is_crit is True
    assert damage >= 100  # High damage from crit
    assert damage >= 1     # Minimum damage always applied
```

## Troubleshooting

### Tests Won't Run

```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
make install

# Clear cache
make clean
pytest --cache-clear
```

### Coverage Too Low

```bash
# Check what's missing
pytest --cov=game --cov-report=term-missing

# Generate detailed HTML report
make test-cov
open htmlcov/index.html
```

### Pygame Issues

```bash
# For headless environments
export SDL_VIDEODRIVER=dummy
export SDL_AUDIODRIVER=dummy

# Skip pygame tests
pytest -m "not ui"
```

## Contributing

When adding features:

1. **Write tests first** (TDD)
2. **Run tests:** `make test`
3. **Check coverage:** `make test-cov`
4. **Format code:** `make format`
5. **Lint:** `make lint`
6. **Run CI checks:** `make ci`

## Support

For testing questions:
- Review documentation bibles
- Check existing tests for patterns
- Run `make help` for available commands

---

**Testing is not optional. Testing is how we ship with confidence.**
