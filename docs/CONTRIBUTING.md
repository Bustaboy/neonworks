# Contributing to NeonWorks

## Code Formatting

This project uses [black](https://black.readthedocs.io/) for code formatting and [isort](https://pycqa.github.io/isort/) for import sorting.

### Before Committing

**Always run formatting before committing:**

```bash
# Option 1: Use the helper script
./scripts/format.sh

# Option 2: Run formatters directly
black . --exclude='\.git|__pycache__|\.pytest_cache'
isort . --skip .git --skip __pycache__ --skip .pytest_cache --profile black
```

### Pre-commit Hooks (Recommended)

Install pre-commit hooks to automatically format your code:

```bash
pip install pre-commit
pre-commit install
```

Once installed, black and isort will run automatically on every commit.

### CI Checks

Our CI pipeline runs the following checks:
- **Black formatting**: `black --check .`
- **Import sorting**: `isort --check-only .`
- **Linting**: `flake8` and `pylint`
- **Type checking**: `mypy`
- **Tests**: `pytest` with coverage

All checks must pass before a PR can be merged.

## Import Style

### Directory Structure

```
neonworks/
├── core/              # Core engine components
├── engine/            # Engine subsystems
│   └── core/          # Event interpreter, etc.
├── gameplay/          # Game logic
├── rendering/         # Rendering systems
└── tests/             # Test files
```

### Import Patterns

**Always use the `neonworks.` prefix for imports:**

```python
# ✅ Correct
from neonworks.core.events import EventManager
from neonworks.engine.core.event_interpreter import EventInterpreter

# ❌ Incorrect
from core.events import EventManager
from engine.core.event_interpreter import EventInterpreter
```

### Import Ordering

Imports must be sorted using isort with the black profile. The order is:

1. **Standard library imports** (alphabetically sorted)
2. **Third-party imports** (alphabetically sorted)
3. **Local imports** with `neonworks.` prefix (alphabetically sorted)

Within each import statement, names must be alphabetically sorted.

**Example:**
```python
# ✅ Correct
import logging
from dataclasses import dataclass
from typing import Dict, List

import pytest

from neonworks.core.events import Event, EventManager
from neonworks.engine.core.event_interpreter import (
    CommandExecutionError,
    EventInterpreter,
    InterpreterInstance,
)

# ❌ Incorrect (wrong order)
import pytest
from dataclasses import dataclass
import logging

from neonworks.engine.core.event_interpreter import (
    EventInterpreter,
    CommandExecutionError,
)
```

### Why?

The project uses a package structure where all modules are accessed through the `neonworks` namespace. This ensures:
- Consistent imports across the codebase
- Proper module resolution in tests
- Compatibility with both development and installed modes

## Adding New Directories

When adding a new package directory:

1. **Create `__init__.py`**:
```python
"""
Module documentation
"""

# Export public API
from neonworks.your_module.your_class import YourClass

__all__ = ["YourClass"]
```

2. **Update `.pre-commit-config.yaml`**:
Add your directory to the `files` regex patterns:
```yaml
files: ^(neonworks|core|gameplay|...|your_directory)/.*\.py$
```

3. **Update `pytest.ini`**:
Add coverage for your directory:
```ini
addopts =
    --cov=your_directory
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_event_interpreter.py

# Run with coverage
pytest --cov=. --cov-report=html
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Use the `neonworks.` import prefix
- Mock external dependencies

Example:
```python
from neonworks.core.events import EventManager
from neonworks.engine.core.event_interpreter import EventInterpreter

def test_interpreter():
    manager = EventManager()
    interpreter = EventInterpreter(game_state, manager)
    # ... test logic
```

## Common Issues

### Issue: `ModuleNotFoundError: No module named 'core'`

**Solution**: Update imports to use `neonworks.` prefix:
```python
from neonworks.core.events import EventManager  # ✅
```

### Issue: `black --check` fails in CI

**Solution**: Run formatting before committing:
```bash
./scripts/format.sh
```

### Issue: Import order incorrect

**Solution**: Run isort:
```bash
isort . --profile black
```

## Questions?

- Check existing code for examples
- Review documentation in `docs/`
- Open an issue on GitHub
