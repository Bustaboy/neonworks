# Neon Collapse - Developer Guide

Welcome to the Neon Collapse development guide! This document covers best practices, code standards, and development workflows.

## Table of Contents

- [Getting Started](#getting-started)
- [Code Standards](#code-standards)
- [Testing Guidelines](#testing-guidelines)
- [Development Workflow](#development-workflow)
- [Architecture Overview](#architecture-overview)
- [Common Patterns](#common-patterns)
- [Troubleshooting](#troubleshooting)

---

## Getting Started

### Prerequisites

- Python 3.11+
- pip package manager
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/Bustaboy/neon-collapse.git
cd neon-collapse

# Install dependencies
make install-dev

# Run tests to verify setup
make test

# Check code quality
make lint
make typecheck
```

### Quick Commands

```bash
make test          # Run all tests
make test-cov      # Run tests with coverage
make lint          # Run linters
make typecheck     # Run type checking
make format        # Format code
make run           # Run the game
```

---

## Code Standards

### Import Guidelines

**✅ DO: Use explicit imports**

```python
from config import (
    MAX_ACTION_POINTS,
    DODGE_CAP,
    BASE_MOVEMENT_RANGE
)
```

**❌ DON'T: Use star imports**

```python
from config import *  # BAD - unclear what's imported
```

**Why?**
- Better IDE autocomplete and type hints
- Clear dependencies
- Prevents namespace pollution
- PEP 8 compliant

### Function Complexity

**Target: Complexity < 10**

**✅ DO: Break complex functions into helpers**

```python
def enemy_ai_turn(self, enemy):
    """Simple AI for enemy turns"""
    player_alive = [c for c in self.player_team if c.is_alive]
    if not player_alive:
        return

    # Try attack first, then move
    if not self._ai_try_attack(enemy):
        self._ai_try_move(enemy, player_alive)

    if enemy.ap == 0:
        self.next_turn()

def _ai_try_attack(self, enemy):
    """Try to attack if targets in range."""
    targets = self.get_valid_targets(enemy)
    if targets and enemy.ap >= AP_BASIC_ATTACK:
        target = self._find_closest_character(enemy, targets)
        if target:
            damage, log = enemy.attack(target)
            self.add_log(log)
            return True
    return False
```

**Key Principles:**
- One function = one responsibility
- Extract helper methods (use `_` prefix for private)
- Aim for < 10 lines per function
- Use descriptive names

### Type Hints

**✅ DO: Add type hints to function signatures**

```python
def add_item(self, item: Item, quantity: int = 1) -> bool:
    """Add an item to inventory."""
    pass

def get_active_quests(self) -> List[Quest]:
    """Get all active quests."""
    pass
```

**Key Guidelines:**
- Always type hint parameters
- Always type hint return values
- Use `Optional[T]` for nullable types
- Import types from `typing` module

### Error Handling

**✅ DO: Handle errors gracefully**

```python
if quest_manager:
    try:
        save_data["quest_manager"] = quest_manager.to_dict()
    except (AttributeError, TypeError) as e:
        print(f"Warning: Failed to save quest_manager: {e}")
```

**✅ DO: Validate inputs**

```python
def __init__(self, player_team, enemy_team):
    if not player_team and not enemy_team:
        raise ValueError("Cannot initialize combat with no characters")
```

### Documentation

**✅ DO: Document all public functions**

```python
def check_option_available(
    self,
    option: DialogueOption,
    player_stats: Dict[str, int],
    player_inventory: Optional[Dict[str, int]] = None,
    faction_reps: Optional[Dict[str, int]] = None
) -> bool:
    """
    Check if dialogue option is available to player.

    Args:
        option: Dialogue option to check
        player_stats: Player attributes/skills
        player_inventory: Player inventory
        faction_reps: Faction reputations

    Returns:
        True if option is available
    """
```

---

## Testing Guidelines

### Test Structure

Tests are organized by module in the `tests/` directory:

```
tests/
  ├── conftest.py          # Shared fixtures
  ├── test_combat.py       # Combat system tests
  ├── test_character.py    # Character tests
  ├── test_quest.py        # Quest system tests
  └── ...
```

### Writing Tests

**✅ DO: Use descriptive test names**

```python
def test_escape_notification_shows_when_conditions_met():
    """Test that escape notification appears when HP critical."""
    pass

def test_dialogue_requirement_handles_missing_skill():
    """Test requirement checking with missing skill key."""
    pass
```

**✅ DO: Test edge cases**

```python
class TestEdgeCases:
    def test_character_at_grid_boundaries(self):
        """Test character movement at grid edges."""

    def test_zero_armor_character(self):
        """Test damage calculation with 0 armor."""

    def test_empty_quest_objectives(self):
        """Test quest with no objectives."""
```

### Test Categories

Use pytest markers to categorize tests:

```python
@pytest.mark.unit
def test_damage_calculation():
    """Unit test for damage calculation."""
    pass

@pytest.mark.integration
def test_full_combat_sequence():
    """Integration test for complete combat."""
    pass

@pytest.mark.slow
def test_large_scale_simulation():
    """Test that takes significant time."""
    pass
```

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific category
make test-unit
make test-integration

# Run specific test file
pytest tests/test_combat.py -v

# Run tests matching pattern
pytest -k "escape" -v
```

### Coverage Goals

**Target: 85-90% overall coverage**

Current coverage by module:
- ✅ character.py: 96%
- ✅ faction.py: 97%
- ✅ hacking.py: 93%
- ⚠️ inventory.py: 70% (needs improvement)
- ⚠️ quest.py: 77% (needs improvement)
- ⚠️ save_load.py: 73% (needs improvement)

Focus areas for improvement:
1. Error handling paths
2. Edge cases
3. Integration between systems

---

## Development Workflow

### 1. Branch Naming

```
feature/add-hacking-minigame
bugfix/escape-notification-logic
refactor/reduce-combat-complexity
docs/update-developer-guide
```

### 2. Commit Messages

Follow conventional commits:

```
feat: Add neural interface hacking minigame
fix: Escape notification now shows correctly
refactor: Break down enemy_ai_turn complexity
docs: Add developer guide for code standards
test: Add coverage for inventory edge cases
```

### 3. Development Cycle

```bash
# 1. Create branch
git checkout -b feature/my-feature

# 2. Make changes
# ... write code ...

# 3. Run tests frequently
make test

# 4. Check code quality
make lint
make typecheck

# 5. Format code
make format

# 6. Commit changes
git add .
git commit -m "feat: Add new feature"

# 7. Push and create PR
git push origin feature/my-feature
```

### 4. Pre-commit Checklist

Before committing, ensure:

- [ ] All tests pass (`make test`)
- [ ] No lint errors (`make lint`)
- [ ] Type checking passes (`make typecheck`)
- [ ] Code is formatted (`make format`)
- [ ] New functions have docstrings
- [ ] New code has tests
- [ ] Coverage hasn't decreased

---

## Architecture Overview

### System Layers

```
┌─────────────────────────────────────┐
│         UI Layer (main.py, ui.py)   │
│         - User Interface            │
│         - Input handling            │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│      Game Systems Layer             │
│  - Combat    - Quests               │
│  - Dialogue  - Factions             │
│  - Crafting  - World Map            │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│      Core Layer                     │
│  - Character  - Inventory           │
│  - Status     - Skills/XP           │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│      Data Layer                     │
│  - Save/Load  - Configuration       │
└─────────────────────────────────────┘
```

### Key Design Patterns

#### Strategy Pattern
Used in dialogue requirements checking:

```python
requirement_checks = {
    "skill": lambda: self._check_skill_requirement(...),
    "attribute": lambda: self._check_attribute_requirement(...),
    "item": lambda: self._check_item_requirement(...),
}
check_func = requirement_checks.get(option.requirement_type)
```

#### Factory Pattern
Used in quest objective creation:

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'Objective':
    obj_type = data.get("type")
    if obj_type == "defeat_enemies":
        return DefeatEnemies(...)
    elif obj_type == "go_to_location":
        return GoToLocation(...)
```

#### Observer Pattern
Used in quest progression:

```python
def update_progress(self, **kwargs):
    """Update objective progress based on game events."""
    if self.objective_type == "defeat_enemies":
        if kwargs.get("enemy_type") == self.enemy_type:
            self.current_count += 1
```

---

## Common Patterns

### Configuration Management

All game constants in `config.py`:

```python
# Import what you need
from config import (
    MAX_ACTION_POINTS,
    GRID_WIDTH,
    GRID_HEIGHT
)

# Use in code
if character.ap >= MAX_ACTION_POINTS:
    # ...
```

### Error Handling Pattern

```python
try:
    # Risky operation
    result = manager.to_dict()
except (AttributeError, TypeError) as e:
    # Log warning, continue gracefully
    print(f"Warning: Operation failed: {e}")
    # Return safe default or None
    return None
```

### Validation Pattern

```python
def process_data(self, data):
    # Validate early
    if not data:
        raise ValueError("Data cannot be empty")

    required_key = data.get("required_field")
    if required_key is None:
        return False  # or raise

    # Process validated data
    self._do_work(required_key)
```

### Data Transformation Pattern

```python
# Use dict comprehensions for clarity
rewards = {
    tier: config
    for tier, config in REWARD_TIERS.items()
    if level >= tier
}

# Use list comprehensions
active_quests = [
    self.quests[qid]
    for qid in self.active_quests
    if qid in self.quests  # Guard against missing IDs
]
```

---

## Troubleshooting

### Tests Failing

```bash
# Run verbose mode to see details
pytest tests/ -vv --tb=long

# Run specific failing test
pytest tests/test_combat.py::test_escape_notification -vv

# Check if it's a fixture issue
pytest tests/ --setup-show
```

### Type Checking Errors

```bash
# Run mypy with full output
mypy game/ --config-file=mypy.ini --show-traceback

# Check specific file
mypy game/combat.py --config-file=mypy.ini
```

### Import Errors

```bash
# Ensure you're running from project root
pwd  # Should show .../neon-collapse

# Check Python path
python -c "import sys; print(sys.path)"

# Try running tests with explicit path
PYTHONPATH=. pytest tests/
```

### Coverage Issues

```bash
# Generate HTML coverage report
make test-cov

# Open report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux

# Check specific module
pytest tests/test_inventory.py --cov=game.inventory --cov-report=term-missing
```

---

## Additional Resources

- **Game Design Docs**: `bibles/` directory
- **Testing Patterns**: `bibles/09-TESTING-BIBLE-TDD-PATTERNS.md`
- **Architecture**: `bibles/07-TECHNICAL-ARCHITECTURE-BIBLE.md`
- **Changelog**: `CHANGELOG.md`
- **Coverage Report**: `htmlcov/index.html` (after running `make test-cov`)

---

## Questions?

If you encounter issues:
1. Check this guide
2. Review test files for examples
3. Check the bible documents
4. Ask in team chat
5. Create an issue on GitHub

Happy coding! 🚀
