# Code Formatting Guide

This project uses automated code formatting to maintain consistent style across the codebase.

## Tools Used

- **[Black](https://black.readthedocs.io/)** - The uncompromising Python code formatter
- **[isort](https://pycqa.github.io/isort/)** - Import statement organizer
- **[flake8](https://flake8.pycqa.org/)** - Style guide enforcement

## Configuration

All formatting configuration is centralized in `pyproject.toml`:
- Line length: 100 characters
- Target Python version: 3.11
- isort profile: black (for compatibility)

## Automated Formatting Options

### 1. Pre-commit Hooks (Recommended) ⭐

**Automatically formats code before every commit.**

```bash
# Install pre-commit hooks
make setup-hooks

# Or manually:
pre-commit install
```

Now every time you run `git commit`, code will be automatically formatted!

To run manually on all files:
```bash
make pre-commit
# Or: pre-commit run --all-files
```

### 2. Makefile Commands (Quick & Easy)

```bash
# Auto-format all code
make format

# Check formatting without modifying files
make format-check

# Run linters
make lint

# See all available commands
make help
```

### 3. GitHub Actions (CI Automation)

**Auto-formats code on push and creates a commit.**

The workflow `.github/workflows/auto-format.yml` runs on:
- Push to `develop` and `claude/*` branches
- Manual trigger via GitHub Actions UI

If formatting issues are found, it automatically:
1. Formats the code
2. Commits the changes
3. Pushes back to the branch

### 4. Editor Integration

#### VSCode

**Auto-format on save!**

1. Install recommended extensions:
   - Python (ms-python.python)
   - Black Formatter (ms-python.black-formatter)
   - isort (ms-python.isort)

2. Settings are already configured in `.vscode/settings.json`

3. Open the project in VSCode and accept the recommended extensions

**Usage:**
- Code formats automatically when you save (Ctrl+S / Cmd+S)
- Imports organize automatically on save
- Linting errors show in real-time

#### PyCharm / IntelliJ IDEA

1. **Install black plugin:**
   - File → Settings → Plugins → Search "BlackConnect"

2. **Configure black:**
   - File → Settings → Tools → Black
   - Check "Run Black on save"

3. **Configure isort:**
   - File → Settings → Tools → External Tools
   - Add isort with args: `--profile black $FilePath$`

4. **Format on save:**
   - File → Settings → Actions on Save
   - Enable "Reformat code" and "Optimize imports"

### 5. Manual Commands

```bash
# Format with black
black .

# Sort imports with isort
isort .

# Check without modifying
black --check .
isort --check-only .

# Format specific file/directory
black path/to/file.py
isort path/to/directory/
```

## What Gets Formatted?

The formatters target these directories:
- `neonworks/`
- `core/`
- `gameplay/`
- `rendering/`
- `systems/`
- `export/`
- `data/`
- `ui/`
- `tests/`
- `engine/`
- `examples/`

Excluded:
- `.git/`
- `__pycache__/`
- `.pytest_cache/`
- Virtual environments
- Build artifacts

## Formatting Rules

### Black

- Line length: 100 characters
- Double quotes for strings
- Trailing commas in multi-line structures
- No manual line breaks that conflict with Black's style

### isort

- Imports grouped by: Future, Stdlib, Third-party, First-party, Local
- Compatible with Black's formatting
- Alphabetical sorting within groups
- One import per line

### flake8

- Critical errors only in CI (syntax errors, undefined names)
- Advisory warnings for style issues
- Max line length: 127 (allows some flexibility beyond Black's 100)

## Troubleshooting

### Pre-commit hook fails

```bash
# Update hooks to latest versions
pre-commit autoupdate

# Clean cache and retry
pre-commit clean
pre-commit install --install-hooks
```

### VSCode not formatting

1. Check Python interpreter is selected (bottom-right)
2. Verify Black extension is installed
3. Check Output → Python → Formatting for errors
4. Reload window: Ctrl+Shift+P → "Developer: Reload Window"

### Conflicts between tools

This shouldn't happen as isort is configured with `--profile black`. If you see conflicts:

1. Update tools to latest versions:
   ```bash
   pip install --upgrade black isort
   ```

2. Clear caches:
   ```bash
   make clean
   ```

## Best Practices

1. **Enable pre-commit hooks** - Prevents formatting issues from reaching CI
2. **Use editor integration** - Get instant feedback while coding
3. **Don't fight the formatter** - Trust Black's decisions
4. **Format before reviewing** - Makes diffs cleaner
5. **Run `make format` before pushing** - Final safety check

## CI Integration

### GitHub Actions Workflow

- ✅ **Auto-format workflow** - Automatically fixes formatting
- ⚠️ **Test workflow** - Checks formatting (advisory only)

Both workflows use the same versions specified in `requirements-dev.txt`:
- black==25.11.0
- isort==7.0.0
- flake8==7.3.0

### Pre-commit in CI

The test workflow runs the same pre-commit hooks locally and in CI for consistency.

## Quick Reference

| Task | Command |
|------|---------|
| Format all code | `make format` |
| Check formatting | `make format-check` |
| Run linters | `make lint` |
| Run tests | `make test` |
| Install hooks | `make setup-hooks` |
| Clean caches | `make clean` |
| Format one file | `black file.py` |
| Sort imports | `isort .` |

## Additional Resources

- [Black Documentation](https://black.readthedocs.io/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [flake8 Documentation](https://flake8.pycqa.org/)
- [pre-commit Documentation](https://pre-commit.com/)

---

**Pro Tip:** Set up pre-commit hooks once and forget about formatting forever! 🎉
