# NeonWorks Test Suite Documentation

**Version:** 1.0
**Last Updated:** 2025-11-15
**Test Coverage Target:** 85-90%

---

## Table of Contents

1. [Overview](#overview)
2. [Test Structure](#test-structure)
3. [Running Tests](#running-tests)
4. [Test Categories](#test-categories)
5. [Writing Tests](#writing-tests)
6. [Coverage Reports](#coverage-reports)
7. [Continuous Integration](#continuous-integration)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The NeonWorks test suite is a comprehensive testing framework designed to ensure the reliability, performance, and stability of the NeonWorks 2D game engine. The suite includes:

- **45+ existing test files** covering core functionality
- **New comprehensive tests** for ECS, events, performance, stress, and integration
- **9,400+ lines** of test code
- **Target coverage:** 85-90%
- **Multiple test categories:** unit, integration, performance, stress

### Test Philosophy

1. **Comprehensive Coverage:** Test all critical paths and edge cases
2. **Performance Validation:** Ensure performance meets benchmarks
3. **Stress Testing:** Validate stability under extreme loads
4. **Integration Testing:** Test cross-feature workflows
5. **Continuous Quality:** Run tests on every commit via CI/CD

---

## Test Structure

### Directory Layout

```
tests/
├── README.md                          # This file
├── conftest.py                        # Shared fixtures and pytest configuration
├── test_all.py                        # Test orchestrator script
│
├── Core System Tests (NEW)
│   ├── test_ecs.py                    # ECS (Entity-Component-System) tests
│   ├── test_events_core.py            # Event system tests
│
├── Specialized Test Suites (NEW)
│   ├── test_performance.py            # Performance benchmarks
│   ├── test_stress.py                 # Stress tests (memory/CPU)
│   ├── test_integration_workflows.py  # Cross-feature integration tests
│
├── Existing Tests (45 files)
│   ├── test_animation_state_machine.py
│   ├── test_asset_manager.py
│   ├── test_audio_manager.py
│   ├── test_autotiles.py
│   ├── test_base_building.py
│   ├── test_camera_enhancements.py
│   ├── test_character_controller.py
│   ├── test_character_generator.py
│   ├── test_ai_character_generator.py
│   ├── test_ai_layer_generator.py
│   ├── test_ai_tileset_generator.py
│   ├── test_cli.py
│   ├── test_collision.py
│   ├── test_combat.py
│   ├── test_data.py
│   ├── test_database_editor_ui.py
│   ├── test_editor.py
│   ├── test_event_commands.py
│   ├── test_event_integration.py
│   ├── test_event_interpreter.py
│   ├── test_event_triggers.py
│   ├── test_export.py
│   ├── test_game_loop.py
│   ├── test_hotkey_manager.py
│   ├── test_input_manager.py
│   ├── test_licensing.py
│   ├── test_magic_system.py
│   ├── test_map_importers.py
│   ├── test_map_layers.py
│   ├── test_map_manager.py
│   ├── test_optimized_renderer.py
│   ├── test_particles.py
│   ├── test_pathfinding.py
│   ├── test_project.py
│   ├── test_rigidbody.py
│   ├── test_scene.py
│   ├── test_serialization.py
│   ├── test_state.py
│   ├── test_survival_system.py
│   ├── test_systems.py
│   ├── test_tilemap.py
│   ├── test_tilemap_enhanced.py
│   ├── test_tileset_manager.py
│   ├── test_ui_system.py
│   ├── test_undo_manager.py
│   └── test_validation.py
```

### Key Files

| File | Purpose |
|------|---------|
| `conftest.py` | Shared pytest fixtures (world, entities, mock objects) |
| `test_all.py` | Orchestrator for running different test suites |
| `test_ecs.py` | Comprehensive ECS tests (Entity, Component, System, World) |
| `test_events_core.py` | Event system tests (EventManager, Event, EventType) |
| `test_performance.py` | Performance benchmarks (2000 DB entries, 500x500 maps) |
| `test_stress.py` | Stress tests (memory, CPU, concurrency) |
| `test_integration_workflows.py` | Cross-feature integration tests |

---

## Running Tests

### Quick Start

```bash
# Run all unit tests (default)
pytest tests/ -v

# Run specific test file
pytest tests/test_ecs.py -v

# Run tests with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test class
pytest tests/test_ecs.py::TestEntity -v

# Run specific test method
pytest tests/test_ecs.py::TestEntity::test_create_entity -v
```

### Using the Test Orchestrator

The `test_all.py` script provides a convenient way to run different test suites:

```bash
# Show test suite summary
python tests/test_all.py --summary

# Run unit tests only (default)
python tests/test_all.py

# Run integration tests
python tests/test_all.py --integration

# Run performance benchmarks
python tests/test_all.py --performance

# Run stress tests
python tests/test_all.py --stress

# Run full test suite (all tests)
python tests/test_all.py --full

# Run with coverage report
python tests/test_all.py --coverage

# Run specific test file
python tests/test_all.py --file tests/test_ecs.py

# Quiet output
python tests/test_all.py --quiet
```

### Using Pytest Markers

Tests are organized using pytest markers:

```bash
# Run only integration tests
pytest tests/ -v -m integration

# Run only performance tests
pytest tests/ -v -m performance

# Run only stress tests
pytest tests/ -v -m stress

# Run all except slow tests
pytest tests/ -v -m "not slow"

# Run unit tests (exclude integration, performance, stress)
pytest tests/ -v -m "not integration and not performance and not stress"
```

### Using Makefile

The project includes a Makefile with convenient test commands:

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Format code before testing
make format

# Lint code
make lint

# Full check (format, lint, test)
make format lint test
```

---

## Test Categories

### 1. Unit Tests

**Purpose:** Test individual components in isolation
**Speed:** Fast (< 5 minutes)
**Coverage:** 85-90% target
**Run frequency:** On every commit

**Examples:**
- `test_ecs.py` - ECS component tests
- `test_events_core.py` - Event system tests
- `test_collision.py` - Collision detection tests
- `test_pathfinding.py` - Pathfinding algorithm tests

**Running:**
```bash
pytest tests/ -v -m "not integration and not performance and not stress"
python tests/test_all.py  # default
```

### 2. Integration Tests

**Purpose:** Test cross-feature workflows
**Speed:** Medium (2-5 minutes)
**Coverage:** Critical workflows
**Run frequency:** On every PR

**Examples:**
- Complete combat encounter (ECS + Events + Combat)
- Building lifecycle (placement, completion, upgrade)
- Resource collection and consumption
- Map generation with entity placement
- Save/load world state

**Running:**
```bash
pytest tests/ -v -m integration
python tests/test_all.py --integration
```

### 3. Performance Tests

**Purpose:** Validate performance benchmarks
**Speed:** Medium (2-5 minutes)
**Benchmarks:**
- 2000+ database entries
- 500x500 tile maps
- Large entity counts (10,000+)
- Complex pathfinding

**Performance Targets:**
- Create 1000 entities: < 1.0s
- Query 5000 entities: < 100ms
- Update 1000 entities: < 50ms
- Create 2000 DB entries: < 2.0s
- Create 500x500 map: < 30s

**Running:**
```bash
pytest tests/ -v -m performance -s
python tests/test_all.py --performance
```

### 4. Stress Tests

**Purpose:** Test system stability under extreme loads
**Speed:** Slow (5-15 minutes)
**Tests:**
- Memory stress (10,000 entities)
- CPU stress (intensive queries/updates)
- Concurrent operations
- Sustained load (50+ iterations)

**Running:**
```bash
pytest tests/ -v -m stress -s
python tests/test_all.py --stress
```

---

## Writing Tests

### Test Structure

Follow this structure for new tests:

```python
"""
Module docstring describing test purpose.
"""

import pytest

from neonworks.core.ecs import Entity, World
from neonworks.core.events import EventManager


class TestMyFeature:
    """Test suite for MyFeature."""

    def test_basic_functionality(self):
        """Test basic functionality."""
        # Arrange
        world = World()
        entity = world.create_entity("Test")

        # Act
        entity.add_tag("test_tag")

        # Assert
        assert entity.has_tag("test_tag")

    def test_edge_case(self):
        """Test edge case scenario."""
        # Test implementation
        pass

    @pytest.mark.parametrize("input,expected", [
        (0, 0),
        (10, 10),
        (-5, -5),
    ])
    def test_with_parameters(self, input, expected):
        """Test with multiple parameter sets."""
        assert input == expected
```

### Using Fixtures

Fixtures are defined in `conftest.py` and can be used in any test:

```python
def test_with_fixtures(world, player_entity, enemy_entity):
    """Test using shared fixtures."""
    # world, player_entity, enemy_entity are automatically provided
    assert player_entity in world.entities
    assert enemy_entity in world.entities
```

**Available fixtures:**
- `world` - Empty World instance
- `event_manager` - EventManager instance
- `player_entity` - Player with Transform, Health, GridPosition
- `enemy_entity` - Enemy with Transform, Health
- `jrpg_player` - JRPG player with full stats
- `jrpg_enemy` - JRPG enemy with stats
- `building_entity` - Building with placement data
- `turn_actor` - Entity with turn-based combat components
- `physics_entity` - Entity with physics components
- `survival_entity` - Entity with survival stats
- `temp_dir` - Temporary directory for test files
- `temp_project_dir` - Temporary project structure
- `mock_renderer` - Mock renderer for UI tests
- `sample_entities` - Collection of diverse entities

### Marking Tests

Use pytest markers to categorize tests:

```python
@pytest.mark.integration
def test_integration_scenario():
    """Integration test."""
    pass

@pytest.mark.performance
def test_performance_benchmark():
    """Performance benchmark."""
    pass

@pytest.mark.stress
def test_stress_scenario():
    """Stress test."""
    pass

@pytest.mark.slow
def test_slow_operation():
    """Slow running test."""
    pass
```

### Best Practices

1. **Descriptive names:** Use clear, descriptive test names
2. **One assertion concept:** Test one thing per test method
3. **Arrange-Act-Assert:** Follow AAA pattern
4. **Use fixtures:** Reuse common setup via fixtures
5. **Parametrize:** Use `@pytest.mark.parametrize` for similar tests
6. **Docstrings:** Add docstrings to test classes and methods
7. **Mark tests:** Use markers for categorization
8. **Clean up:** Use fixtures for automatic cleanup

---

## Coverage Reports

### Generating Coverage Reports

```bash
# HTML report (recommended)
pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux

# Terminal report
pytest tests/ --cov=. --cov-report=term

# Terminal with missing lines
pytest tests/ --cov=. --cov-report=term-missing

# XML report (for CI)
pytest tests/ --cov=. --cov-report=xml

# Multiple reports
pytest tests/ --cov=. --cov-report=html --cov-report=term-missing --cov-report=xml
```

### Coverage Targets

| Module Type | Target Coverage |
|-------------|-----------------|
| Core (ECS, Events, Game Loop) | 90%+ |
| Systems (Combat, Pathfinding) | 85%+ |
| Rendering | 75%+ |
| UI | 70%+ |
| Overall | 85-90% |

### Viewing Coverage

After running tests with coverage:

```bash
# Open HTML report
cd htmlcov
python -m http.server 8000
# Navigate to http://localhost:8000

# Or directly open
open htmlcov/index.html
```

---

## Continuous Integration

### GitHub Actions Workflows

The project includes comprehensive CI workflows:

#### 1. `comprehensive-tests.yml` (NEW)

Complete test suite with multiple jobs:

- **Unit Tests:** Run on every push/PR
- **Integration Tests:** Run after unit tests pass
- **Performance Tests:** Run after unit tests pass
- **Stress Tests:** Run only on main/develop (optional)
- **Test Summary:** Aggregate results

**Features:**
- Parallel test execution
- Coverage reporting
- Artifact upload
- Conditional execution (stress tests)
- Manual trigger support

#### 2. `test.yml` (Existing)

Standard test workflow:
- Smoke tests (fast)
- Full test suite with coverage
- Codecov integration

### Triggering CI

CI runs automatically on:
- Push to `main`, `develop`, or `claude/*` branches
- Pull requests to `main` or `develop`
- Manual workflow dispatch

### Viewing CI Results

1. Go to repository **Actions** tab
2. Select workflow run
3. View job results and logs
4. Download artifacts (coverage reports, test results)

---

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem:** `ModuleNotFoundError: No module named 'neonworks'`

**Solution:**
```bash
# Install in editable mode
pip install -e .

# Or set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/ -v
```

#### 2. Pygame Errors

**Problem:** `pygame.error: No available video device`

**Solution:**
```bash
# Set SDL to use dummy video driver
export SDL_VIDEODRIVER=dummy
pytest tests/ -v

# Or use xvfb (Linux)
xvfb-run pytest tests/ -v
```

#### 3. Slow Tests

**Problem:** Tests take too long

**Solution:**
```bash
# Run only fast tests
pytest tests/ -v -m "not slow"

# Skip performance and stress tests
pytest tests/ -v -m "not performance and not stress"

# Run in parallel
pytest tests/ -v -n auto
```

#### 4. Coverage Not Generated

**Problem:** Coverage report empty or missing

**Solution:**
```bash
# Ensure pytest-cov is installed
pip install pytest-cov

# Run with explicit coverage
pytest tests/ --cov=neonworks --cov-report=html

# Check .coveragerc configuration
cat .coveragerc
```

#### 5. Test Failures in CI but Passes Locally

**Problem:** Tests fail in CI but work locally

**Solution:**
```bash
# Run tests with same Python version as CI
pyenv install 3.11
pyenv local 3.11

# Clear pytest cache
rm -rf .pytest_cache

# Install exact dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Debug Mode

Run tests in debug mode:

```bash
# Verbose output with full tracebacks
pytest tests/ -vv --tb=long

# Stop on first failure
pytest tests/ -x

# Drop into debugger on failure
pytest tests/ --pdb

# Show print statements
pytest tests/ -s

# Show local variables in tracebacks
pytest tests/ -l
```

---

## Test Metrics

### Current Status

- **Total test files:** 50+ (45 existing + 5 new)
- **Total test cases:** 500+ (estimated)
- **Lines of test code:** 9,400+
- **Coverage target:** 85-90%
- **Unit test speed:** < 5 minutes
- **Integration test speed:** 2-5 minutes
- **Performance test speed:** 2-5 minutes
- **Stress test speed:** 5-15 minutes
- **Full suite speed:** 15-30 minutes

### Performance Benchmarks

| Operation | Target | Typical |
|-----------|--------|---------|
| Create 1000 entities | < 1.0s | ~0.3s |
| Query 5000 entities | < 100ms | ~20ms |
| Update 1000 entities | < 50ms | ~10ms |
| Emit 1000 events | < 500ms | ~100ms |
| Create 2000 DB entries | < 2.0s | ~0.8s |
| Query 2000 DB entries | < 100ms | ~30ms |
| Create 500x500 map | < 30s | ~10s |
| Pathfinding on large map | < 1.0s | ~200ms |

---

## Contributing

### Adding New Tests

1. Identify test category (unit, integration, performance, stress)
2. Create test file or add to existing file
3. Follow naming conventions (`test_*.py`)
4. Use appropriate fixtures from `conftest.py`
5. Add pytest markers (`@pytest.mark.integration`, etc.)
6. Write descriptive docstrings
7. Run tests locally before committing
8. Ensure coverage doesn't decrease

### Test Review Checklist

- [ ] Test names are descriptive
- [ ] Tests follow AAA pattern (Arrange-Act-Assert)
- [ ] Fixtures are used appropriately
- [ ] Tests are marked correctly (integration, performance, etc.)
- [ ] Tests run successfully locally
- [ ] Coverage is maintained or improved
- [ ] Tests don't have flaky behavior
- [ ] Tests clean up after themselves

---

## Additional Resources

- **pytest Documentation:** https://docs.pytest.org/
- **pytest-cov Documentation:** https://pytest-cov.readthedocs.io/
- **Testing Best Practices:** See `DEVELOPER_GUIDE.md`
- **CI/CD Configuration:** See `.github/workflows/`

---

## Questions?

For questions about testing:
1. Check this README
2. See `DEVELOPER_GUIDE.md`
3. Review existing tests for examples
4. Check project issues on GitHub

---

**Last Updated:** 2025-11-15
**Maintainer:** NeonWorks Team
**Status:** Production Ready
