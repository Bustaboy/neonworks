"""
Guardrail: prevent new usages of legacy layer APIs.

This test fails if source files (excluding tests/docs/examples) contain
`tilemap.layers` or passing `layers=` into `Tilemap(...)`.
"""

from pathlib import Path
import re

# Directories to scan for violations
ROOT = Path(__file__).resolve().parents[1]
SRC_DIRS = ["neonworks"]

# Skip patterns (relative paths)
SKIP_DIR_NAMES = {"tests", "docs", "examples", "scripts", "__pycache__"}

# Patterns to flag
PATTERNS = [
    re.compile(r"tilemap\.layers"),
    re.compile(r"Tilemap\([^\n]*layers\s*="),
]


def iter_source_files():
    """Yield python source files under SRC_DIRS excluding skipped dirs."""
    for src in SRC_DIRS:
        base = ROOT / src
        for path in base.rglob("*.py"):
            if any(part in SKIP_DIR_NAMES for part in path.parts):
                continue
            yield path


def test_no_legacy_layer_apis():
    """Ensure no new legacy layer API usages are added."""
    violations = []

    for path in iter_source_files():
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue

        for pattern in PATTERNS:
            for match in pattern.finditer(text):
                violations.append(f"{path}:{match.start()}:{match.group(0)}")

    assert not violations, (
        "Legacy layer APIs found (use enhanced layers and get_layer_count instead):\n"
        + "\n".join(violations)
    )
