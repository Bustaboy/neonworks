.PHONY: help install test test-cov test-verbose lint format clean run docs

# Default target
help:
	@echo "Neon Collapse - Development Commands"
	@echo "===================================="
	@echo ""
	@echo "Setup:"
	@echo "  make install         Install all dependencies"
	@echo "  make install-dev     Install dev dependencies only"
	@echo ""
	@echo "Testing:"
	@echo "  make test            Run all tests"
	@echo "  make test-cov        Run tests with coverage report"
	@echo "  make test-verbose    Run tests with verbose output"
	@echo "  make test-unit       Run unit tests only"
	@echo "  make test-integration Run integration tests only"
	@echo "  make test-combat     Run combat system tests"
	@echo "  make test-character  Run character system tests"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint            Run all linters"
	@echo "  make format          Format code with black and isort"
	@echo "  make typecheck       Run mypy type checking"
	@echo ""
	@echo "Running:"
	@echo "  make run             Run the game"
	@echo "  make clean           Clean up generated files"
	@echo ""
	@echo "CI/CD:"
	@echo "  make ci              Run all CI checks locally"
	@echo "  make pre-commit      Install pre-commit hooks"

# Installation
install:
	pip install -r game/requirements.txt
	pip install -r requirements-dev.txt

install-dev:
	pip install -r requirements-dev.txt

# Testing
test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=game --cov-report=html --cov-report=term-missing --cov-report=xml
	@echo ""
	@echo "Coverage report generated in htmlcov/index.html"

test-verbose:
	pytest tests/ -vv --tb=long

test-unit:
	pytest tests/ -m unit -v

test-integration:
	pytest tests/ -m integration -v

test-combat:
	pytest tests/test_combat.py -v

test-character:
	pytest tests/test_character.py -v

test-ui:
	pytest tests/test_ui.py -v

test-main:
	pytest tests/test_main.py -v

# Quick smoke test
test-quick:
	pytest tests/ -m smoke -v

# Test specific functionality
test-damage:
	pytest tests/ -k damage -v

test-initiative:
	pytest tests/ -k initiative -v

test-escape:
	pytest tests/ -k escape -v

# Code Quality
lint:
	@echo "Running flake8..."
	flake8 game tests --max-line-length=127 --ignore=E203,W503
	@echo ""
	@echo "Running pylint..."
	pylint game --disable=C0111,R0913,R0902,R0903,R0801 || true

format:
	@echo "Formatting with black..."
	black game tests
	@echo ""
	@echo "Sorting imports with isort..."
	isort game tests

typecheck:
	mypy game --config-file=mypy.ini

# Combined quality check
check: format lint typecheck test-cov

# Run the game
run:
	cd game && python main.py

# Clean up
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov coverage.xml

# CI/CD
ci: format lint typecheck test-cov
	@echo ""
	@echo "✓ All CI checks passed!"

pre-commit:
	pre-commit install
	@echo "Pre-commit hooks installed!"

# Documentation
docs:
	@echo "Opening documentation bibles..."
	@echo ""
	@echo "Available documentation:"
	@echo "  - bibles/06-TDD-GAME-SYSTEMS-BIBLE.md"
	@echo "  - bibles/07-TECHNICAL-ARCHITECTURE-BIBLE.md"
	@echo "  - bibles/08-GAME-MECHANICS-BIBLE.md"
	@echo "  - bibles/09-TESTING-BIBLE-TDD-PATTERNS.md"

# Coverage badge (requires coverage-badge)
badge:
	coverage-badge -o coverage.svg -f

# Watch mode (requires pytest-watch)
watch:
	ptw tests/ -- --tb=short

# Parallel testing (requires pytest-xdist)
test-parallel:
	pytest tests/ -n auto -v
