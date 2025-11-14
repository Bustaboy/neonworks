# NeonWorks Development Makefile

.PHONY: help format format-check lint test clean install

help:  ## Show this help message
	@echo "NeonWorks Development Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

format:  ## Auto-format code with black and isort
	@echo "🎨 Formatting code..."
	black .
	isort .
	@echo "✅ Formatting complete!"

format-check:  ## Check code formatting without modifying files
	@echo "🔍 Checking code formatting..."
	black --check .
	isort --check-only .
	@echo "✅ Format check complete!"

lint:  ## Run linters (flake8, pylint)
	@echo "🔎 Running linters..."
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude=.git,__pycache__,.pytest_cache
	@echo "✅ Linting complete!"

test:  ## Run tests with pytest
	@echo "🧪 Running tests..."
	pytest tests/ -v
	@echo "✅ Tests complete!"

test-cov:  ## Run tests with coverage report
	@echo "🧪 Running tests with coverage..."
	pytest tests/ --cov=. --cov-report=html --cov-report=term-missing -v
	@echo "✅ Coverage report generated in htmlcov/"

install:  ## Install development dependencies
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install
	@echo "✅ Installation complete!"

clean:  ## Clean build artifacts and caches
	@echo "🧹 Cleaning..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	@echo "✅ Cleanup complete!"

pre-commit:  ## Run pre-commit hooks on all files
	@echo "🔨 Running pre-commit hooks..."
	pre-commit run --all-files
	@echo "✅ Pre-commit complete!"

setup-hooks:  ## Install git hooks
	@echo "🔗 Setting up git hooks..."
	pre-commit install
	pre-commit install --hook-type commit-msg
	@echo "✅ Git hooks installed!"
