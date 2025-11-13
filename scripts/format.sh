#!/bin/bash
# Format all Python files with black and isort
# Run this before committing to ensure CI passes

set -e

echo "🎨 Formatting Python files..."

# Run black
echo "Running black..."
black . --exclude='\.git|__pycache__|\.pytest_cache'

# Run isort
echo "Running isort..."
isort . --skip .git --skip __pycache__ --skip .pytest_cache --profile black

echo "✅ Formatting complete!"
echo ""
echo "💡 Tip: Install pre-commit hooks to format automatically:"
echo "   pre-commit install"
