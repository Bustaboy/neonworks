"""
User preferences save/load system for map tools.

Saves and loads user customizations to/from JSON file.
Stores:
- Selected theme
- Custom color overrides
- Limits and rendering settings
- Custom themes
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional


# Default preferences directory
PREFERENCES_DIR = Path.home() / ".neonworks"
PREFERENCES_FILE = PREFERENCES_DIR / "map_tools_prefs.json"


def get_preferences_path() -> Path:
    """
    Get the path to the preferences file.

    Returns:
        Path object for preferences file
    """
    return PREFERENCES_FILE


def ensure_preferences_dir():
    """Create preferences directory if it doesn't exist."""
    PREFERENCES_DIR.mkdir(parents=True, exist_ok=True)


def save_preferences(prefs: Dict) -> bool:
    """
    Save preferences to JSON file.

    Args:
        prefs: Dictionary of preferences to save

    Returns:
        True if saved successfully, False otherwise

    Example:
        >>> prefs = {
        ...     "theme": "dark",
        ...     "max_fill_cells": 5000,
        ...     "max_undo_history": 150,
        ... }
        >>> save_preferences(prefs)
        True
    """
    try:
        ensure_preferences_dir()

        with open(PREFERENCES_FILE, "w") as f:
            json.dump(prefs, f, indent=2)

        print(f"✓ Preferences saved to {PREFERENCES_FILE}")
        return True

    except Exception as e:
        print(f"✗ Failed to save preferences: {e}")
        return False


def load_preferences() -> Optional[Dict]:
    """
    Load preferences from JSON file.

    Returns:
        Dict of preferences or None if file doesn't exist/failed to load

    Example:
        >>> prefs = load_preferences()
        >>> if prefs:
        ...     print(f"Theme: {prefs.get('theme')}")
    """
    try:
        if not PREFERENCES_FILE.exists():
            print("ℹ No preferences file found, using defaults")
            return None

        with open(PREFERENCES_FILE, "r") as f:
            prefs = json.load(f)

        print(f"✓ Preferences loaded from {PREFERENCES_FILE}")
        return prefs

    except Exception as e:
        print(f"✗ Failed to load preferences: {e}")
        return None


def delete_preferences() -> bool:
    """
    Delete preferences file.

    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        if PREFERENCES_FILE.exists():
            PREFERENCES_FILE.unlink()
            print(f"✓ Preferences deleted from {PREFERENCES_FILE}")
            return True
        else:
            print("ℹ No preferences file to delete")
            return False

    except Exception as e:
        print(f"✗ Failed to delete preferences: {e}")
        return False


def export_preferences(output_path: str, prefs: Optional[Dict] = None) -> bool:
    """
    Export preferences to a specific file.

    Args:
        output_path: Path to export to
        prefs: Preferences dict (loads current if None)

    Returns:
        True if exported successfully, False otherwise
    """
    try:
        if prefs is None:
            prefs = load_preferences()
            if prefs is None:
                print("✗ No preferences to export")
                return False

        with open(output_path, "w") as f:
            json.dump(prefs, f, indent=2)

        print(f"✓ Preferences exported to {output_path}")
        return True

    except Exception as e:
        print(f"✗ Failed to export preferences: {e}")
        return False


def import_preferences(input_path: str) -> Optional[Dict]:
    """
    Import preferences from a specific file.

    Args:
        input_path: Path to import from

    Returns:
        Dict of preferences or None if failed
    """
    try:
        with open(input_path, "r") as f:
            prefs = json.load(f)

        # Validate required fields
        if not isinstance(prefs, dict):
            raise ValueError("Preferences file must contain a JSON object")

        print(f"✓ Preferences imported from {input_path}")
        return prefs

    except Exception as e:
        print(f"✗ Failed to import preferences: {e}")
        return None


def get_default_preferences() -> Dict:
    """
    Get default preferences.

    Returns:
        Dict with default preference values
    """
    return {
        "theme": "default",
        "max_fill_cells": 10000,
        "max_undo_history": 100,
        "cursor_width": 2,
        "selection_alpha": 50,
        "custom_themes": {},
    }


def merge_preferences(current: Dict, defaults: Dict) -> Dict:
    """
    Merge current preferences with defaults.

    Args:
        current: Current preferences dict
        defaults: Default preferences dict

    Returns:
        Merged dict with defaults for missing keys
    """
    merged = defaults.copy()
    merged.update(current)
    return merged


def validate_preferences(prefs: Dict) -> bool:
    """
    Validate preferences dictionary.

    Args:
        prefs: Preferences dict to validate

    Returns:
        True if valid, False otherwise
    """
    required_keys = ["theme", "max_fill_cells", "max_undo_history"]

    for key in required_keys:
        if key not in prefs:
            print(f"✗ Preferences missing required key: {key}")
            return False

    # Validate types and ranges
    if not isinstance(prefs["theme"], str):
        print("✗ 'theme' must be a string")
        return False

    if not isinstance(prefs["max_fill_cells"], int) or prefs["max_fill_cells"] < 100:
        print("✗ 'max_fill_cells' must be an integer >= 100")
        return False

    if not isinstance(prefs["max_undo_history"], int) or prefs["max_undo_history"] < 10:
        print("✗ 'max_undo_history' must be an integer >= 10")
        return False

    return True


def apply_preferences(prefs: Dict):
    """
    Apply preferences to settings and theme manager.

    Args:
        prefs: Preferences dict to apply
    """
    from . import settings
    from .themes import get_theme_manager

    # Apply theme
    theme_id = prefs.get("theme", "default")
    theme_manager = get_theme_manager()
    if theme_id in theme_manager.themes:
        theme_manager.set_theme(theme_id)

    # Apply limits
    if "max_fill_cells" in prefs:
        settings.ToolLimits.MAX_FILL_CELLS = prefs["max_fill_cells"]
    if "max_undo_history" in prefs:
        settings.ToolLimits.MAX_UNDO_HISTORY = prefs["max_undo_history"]

    # Apply rendering settings
    if "cursor_width" in prefs:
        settings.RenderSettings.CURSOR_OUTLINE_WIDTH = prefs["cursor_width"]
    if "selection_alpha" in prefs:
        settings.RenderSettings.SELECTION_OVERLAY_ALPHA = prefs["selection_alpha"]

    print("✓ Preferences applied to settings!")


def auto_save_on_change(prefs: Dict) -> bool:
    """
    Automatically save preferences when settings change.

    Args:
        prefs: Updated preferences dict

    Returns:
        True if saved successfully
    """
    return save_preferences(prefs)


def load_and_apply_preferences():
    """
    Load preferences and apply them immediately.

    This is typically called on application startup.
    """
    prefs = load_preferences()
    if prefs:
        if validate_preferences(prefs):
            # Merge with defaults to handle missing keys
            defaults = get_default_preferences()
            merged = merge_preferences(prefs, defaults)
            apply_preferences(merged)
        else:
            print("✗ Preferences file is invalid, using defaults")
    else:
        print("ℹ No preferences found, using defaults")
