"""
NeonWorks Hotkey Manager - Comprehensive Keyboard Shortcut System
Manages all keyboard shortcuts with context-sensitive support and configuration.
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

import pygame


class HotkeyContext(Enum):
    """Context in which a hotkey is active."""

    GLOBAL = "global"  # Active in all contexts
    GAME = "game"  # Active during gameplay
    EDITOR = "editor"  # Active in editor mode
    MENU = "menu"  # Active in menus/UI
    COMBAT = "combat"  # Active during combat
    BUILDING = "building"  # Active in building mode
    DIALOGUE = "dialogue"  # Active during dialogue


@dataclass
class Hotkey:
    """
    Represents a keyboard shortcut.

    Attributes:
        key: Primary pygame key code
        modifiers: Set of modifier keys (CTRL, SHIFT, ALT)
        action: Action identifier
        callback: Function to call when triggered
        context: Context in which this hotkey is active
        description: Human-readable description
        category: Category for grouping in UI
        enabled: Whether this hotkey is active
    """

    key: int
    action: str
    callback: Optional[Callable] = None
    modifiers: Set[str] = field(default_factory=set)
    context: HotkeyContext = HotkeyContext.GLOBAL
    description: str = ""
    category: str = "General"
    enabled: bool = True

    def matches(
        self, key: int, ctrl: bool = False, shift: bool = False, alt: bool = False
    ) -> bool:
        """
        Check if this hotkey matches the given key combination.

        Args:
            key: Pygame key code
            ctrl: Whether Ctrl is pressed
            shift: Whether Shift is pressed
            alt: Whether Alt is pressed

        Returns:
            True if matches, False otherwise
        """
        if not self.enabled or self.key != key:
            return False

        # Check modifiers
        has_ctrl = "ctrl" in self.modifiers
        has_shift = "shift" in self.modifiers
        has_alt = "alt" in self.modifiers

        return has_ctrl == ctrl and has_shift == shift and has_alt == alt

    def get_display_name(self) -> str:
        """
        Get a human-readable display name for this hotkey.

        Returns:
            Display name like "Ctrl+Shift+S"
        """
        parts = []

        if "ctrl" in self.modifiers:
            parts.append("Ctrl")
        if "shift" in self.modifiers:
            parts.append("Shift")
        if "alt" in self.modifiers:
            parts.append("Alt")

        # Get key name
        key_name = pygame.key.name(self.key).upper()
        parts.append(key_name)

        return "+".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "key": self.key,
            "modifiers": list(self.modifiers),
            "action": self.action,
            "context": self.context.value,
            "description": self.description,
            "category": self.category,
            "enabled": self.enabled,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], callback: Optional[Callable] = None) -> "Hotkey":
        """Deserialize from dictionary."""
        return cls(
            key=data["key"],
            action=data["action"],
            callback=callback,
            modifiers=set(data.get("modifiers", [])),
            context=HotkeyContext(data.get("context", "global")),
            description=data.get("description", ""),
            category=data.get("category", "General"),
            enabled=data.get("enabled", True),
        )


class HotkeyManager:
    """
    Manages all keyboard shortcuts in the application.

    Features:
    - Context-sensitive shortcuts
    - Modifier key support (Ctrl, Shift, Alt)
    - Customizable bindings
    - Conflict detection
    - Save/load configuration
    - Shortcuts overlay
    """

    def __init__(self):
        """Initialize the hotkey manager."""
        self.hotkeys: List[Hotkey] = []
        self.current_context: HotkeyContext = HotkeyContext.GAME
        self.enabled = True
        self.config_file = "hotkeys.json"

        # Track conflicts
        self.conflicts: List[Tuple[Hotkey, Hotkey]] = []

        # Register default hotkeys
        self._register_default_hotkeys()

    def _register_default_hotkeys(self):
        """Register all default keyboard shortcuts."""
        # UI Editors (F1-F12)
        self.register(
            pygame.K_F1,
            "toggle_debug_console",
            description="Toggle Debug Console",
            category="UI",
        )
        self.register(
            pygame.K_F2,
            "toggle_settings",
            description="Toggle Settings",
            category="UI",
        )
        self.register(
            pygame.K_F3,
            "toggle_building_ui",
            description="Toggle Building UI",
            category="UI",
            context=HotkeyContext.GAME,
        )
        self.register(
            pygame.K_F4,
            "toggle_level_builder",
            description="Toggle Level Builder",
            category="UI",
            context=HotkeyContext.EDITOR,
        )
        self.register(
            pygame.K_F5,
            "toggle_event_editor",
            description="Toggle Event Editor",
            category="UI",
            context=HotkeyContext.EDITOR,
        )
        self.register(
            pygame.K_F6,
            "toggle_database_editor",
            description="Toggle Database Editor",
            category="UI",
            context=HotkeyContext.EDITOR,
        )
        self.register(
            pygame.K_F7,
            "toggle_character_generator",
            description="Toggle Character Generator",
            category="UI",
            context=HotkeyContext.EDITOR,
        )
        self.register(
            pygame.K_F8,
            "toggle_quest_editor",
            description="Toggle Quest Editor",
            category="UI",
            context=HotkeyContext.EDITOR,
        )
        self.register(
            pygame.K_F9,
            "toggle_combat_ui",
            description="Toggle Combat UI",
            category="UI",
            context=HotkeyContext.GAME,
        )
        self.register(
            pygame.K_F10,
            "toggle_game_hud",
            description="Toggle Game HUD",
            category="UI",
            context=HotkeyContext.GAME,
        )
        self.register(
            pygame.K_F11,
            "toggle_autotile_editor",
            description="Toggle Autotile Editor",
            category="UI",
            context=HotkeyContext.EDITOR,
        )
        self.register(
            pygame.K_F12,
            "toggle_navmesh_editor",
            description="Toggle Navmesh Editor",
            category="UI",
            context=HotkeyContext.EDITOR,
        )

        # Special UI shortcuts
        self.register(
            pygame.K_F7,
            "toggle_ai_animator",
            modifiers={"shift"},
            description="Toggle AI Animator",
            category="UI",
            context=HotkeyContext.EDITOR,
        )
        self.register(
            pygame.K_m,
            "toggle_map_manager",
            modifiers={"ctrl"},
            description="Toggle Map Manager",
            category="UI",
            context=HotkeyContext.EDITOR,
        )
        self.register(
            pygame.K_SPACE,
            "toggle_ai_assistant",
            modifiers={"ctrl"},
            description="Toggle AI Assistant",
            category="UI",
        )
        self.register(
            pygame.K_h,
            "toggle_history_viewer",
            modifiers={"ctrl"},
            description="Toggle History Viewer",
            category="Editor",
            context=HotkeyContext.EDITOR,
        )
        self.register(
            pygame.K_SLASH,
            "show_shortcuts_overlay",
            modifiers={"shift"},  # Shift+/ = ?
            description="Show Keyboard Shortcuts",
            category="Help",
        )

        # Edit commands
        self.register(
            pygame.K_z,
            "undo",
            modifiers={"ctrl"},
            description="Undo",
            category="Editor",
            context=HotkeyContext.EDITOR,
        )
        self.register(
            pygame.K_y,
            "redo",
            modifiers={"ctrl"},
            description="Redo",
            category="Editor",
            context=HotkeyContext.EDITOR,
        )
        self.register(
            pygame.K_z,
            "redo_alt",
            modifiers={"ctrl", "shift"},
            description="Redo (alternative)",
            category="Editor",
            context=HotkeyContext.EDITOR,
        )
        self.register(
            pygame.K_s,
            "save_project",
            modifiers={"ctrl"},
            description="Save Project",
            category="File",
        )
        self.register(
            pygame.K_s,
            "save_project_as",
            modifiers={"ctrl", "shift"},
            description="Save Project As",
            category="File",
        )
        self.register(
            pygame.K_o,
            "open_project",
            modifiers={"ctrl"},
            description="Open Project",
            category="File",
        )
        self.register(
            pygame.K_n,
            "new_project",
            modifiers={"ctrl"},
            description="New Project",
            category="File",
        )

        # Gameplay controls
        self.register(
            pygame.K_w,
            "move_up",
            description="Move Up",
            category="Movement",
            context=HotkeyContext.GAME,
        )
        self.register(
            pygame.K_s,
            "move_down",
            description="Move Down",
            category="Movement",
            context=HotkeyContext.GAME,
        )
        self.register(
            pygame.K_a,
            "move_left",
            description="Move Left",
            category="Movement",
            context=HotkeyContext.GAME,
        )
        self.register(
            pygame.K_d,
            "move_right",
            description="Move Right",
            category="Movement",
            context=HotkeyContext.GAME,
        )
        self.register(
            pygame.K_e,
            "interact",
            description="Interact",
            category="Actions",
            context=HotkeyContext.GAME,
        )
        self.register(
            pygame.K_SPACE,
            "attack",
            description="Attack/Confirm",
            category="Actions",
            context=HotkeyContext.GAME,
        )
        self.register(
            pygame.K_ESCAPE,
            "menu",
            description="Menu/Cancel",
            category="Actions",
        )
        self.register(
            pygame.K_i,
            "inventory",
            description="Open Inventory",
            category="UI",
            context=HotkeyContext.GAME,
        )
        self.register(
            pygame.K_b,
            "build",
            description="Build Mode",
            category="Actions",
            context=HotkeyContext.BUILDING,
        )
        self.register(
            pygame.K_TAB,
            "character_stats",
            description="Character Stats",
            category="UI",
            context=HotkeyContext.GAME,
        )

        # Camera controls
        self.register(
            pygame.K_UP,
            "camera_up",
            description="Move Camera Up",
            category="Camera",
        )
        self.register(
            pygame.K_DOWN,
            "camera_down",
            description="Move Camera Down",
            category="Camera",
        )
        self.register(
            pygame.K_LEFT,
            "camera_left",
            description="Move Camera Left",
            category="Camera",
        )
        self.register(
            pygame.K_RIGHT,
            "camera_right",
            description="Move Camera Right",
            category="Camera",
        )
        self.register(
            pygame.K_EQUALS,
            "zoom_in",
            description="Zoom In",
            category="Camera",
        )
        self.register(
            pygame.K_MINUS,
            "zoom_out",
            description="Zoom Out",
            category="Camera",
        )
        self.register(
            pygame.K_0,
            "reset_camera",
            description="Reset Camera",
            category="Camera",
        )

        # Quick save/load
        self.register(
            pygame.K_F5,
            "quick_save",
            modifiers={"ctrl"},
            description="Quick Save",
            category="File",
            context=HotkeyContext.GAME,
        )
        self.register(
            pygame.K_F9,
            "quick_load",
            modifiers={"ctrl"},
            description="Quick Load",
            category="File",
            context=HotkeyContext.GAME,
        )

        # Debug shortcuts
        self.register(
            pygame.K_F3,
            "toggle_debug_overlay",
            modifiers={"ctrl"},
            description="Toggle Debug Overlay",
            category="Debug",
        )
        self.register(
            pygame.K_g,
            "toggle_grid",
            modifiers={"ctrl"},
            description="Toggle Grid",
            category="Debug",
        )
        self.register(
            pygame.K_c,
            "toggle_collision_debug",
            modifiers={"ctrl"},
            description="Toggle Collision Debug",
            category="Debug",
        )

    def register(
        self,
        key: int,
        action: str,
        callback: Optional[Callable] = None,
        modifiers: Optional[Set[str]] = None,
        context: HotkeyContext = HotkeyContext.GLOBAL,
        description: str = "",
        category: str = "General",
        enabled: bool = True,
    ) -> Hotkey:
        """
        Register a new hotkey.

        Args:
            key: Pygame key code
            action: Action identifier
            callback: Function to call when triggered
            modifiers: Set of modifier keys ("ctrl", "shift", "alt")
            context: Context in which this hotkey is active
            description: Human-readable description
            category: Category for grouping
            enabled: Whether this hotkey is active

        Returns:
            The created Hotkey object
        """
        hotkey = Hotkey(
            key=key,
            action=action,
            callback=callback,
            modifiers=modifiers or set(),
            context=context,
            description=description,
            category=category,
            enabled=enabled,
        )

        self.hotkeys.append(hotkey)
        self._check_conflicts(hotkey)
        return hotkey

    def unregister(self, action: str):
        """
        Unregister a hotkey by action name.

        Args:
            action: Action identifier
        """
        self.hotkeys = [h for h in self.hotkeys if h.action != action]

    def set_callback(self, action: str, callback: Callable):
        """
        Set the callback for a hotkey action.

        Args:
            action: Action identifier
            callback: Function to call when triggered
        """
        for hotkey in self.hotkeys:
            if hotkey.action == action:
                hotkey.callback = callback

    def set_context(self, context: HotkeyContext):
        """
        Set the current context.

        Args:
            context: New context
        """
        self.current_context = context

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """
        Handle a pygame event and trigger appropriate hotkeys.

        Args:
            event: Pygame event

        Returns:
            Action name if a hotkey was triggered, None otherwise
        """
        if not self.enabled or event.type != pygame.KEYDOWN:
            return None

        # Get modifier states
        mods = pygame.key.get_mods()
        ctrl = bool(mods & pygame.KMOD_CTRL)
        shift = bool(mods & pygame.KMOD_SHIFT)
        alt = bool(mods & pygame.KMOD_ALT)

        # Find matching hotkey
        for hotkey in self.hotkeys:
            # Check context
            if hotkey.context not in (HotkeyContext.GLOBAL, self.current_context):
                continue

            # Check if key matches
            if hotkey.matches(event.key, ctrl, shift, alt):
                # Trigger callback if set
                if hotkey.callback:
                    hotkey.callback()

                return hotkey.action

        return None

    def rebind(self, action: str, new_key: int, new_modifiers: Optional[Set[str]] = None):
        """
        Rebind a hotkey to a new key combination.

        Args:
            action: Action to rebind
            new_key: New pygame key code
            new_modifiers: New set of modifiers
        """
        for hotkey in self.hotkeys:
            if hotkey.action == action:
                hotkey.key = new_key
                if new_modifiers is not None:
                    hotkey.modifiers = new_modifiers
                self._check_conflicts(hotkey)
                break

    def get_hotkey(self, action: str) -> Optional[Hotkey]:
        """
        Get a hotkey by action name.

        Args:
            action: Action identifier

        Returns:
            Hotkey object or None if not found
        """
        for hotkey in self.hotkeys:
            if hotkey.action == action:
                return hotkey
        return None

    def get_hotkeys_by_category(self, category: str) -> List[Hotkey]:
        """
        Get all hotkeys in a category.

        Args:
            category: Category name

        Returns:
            List of hotkeys in the category
        """
        return [h for h in self.hotkeys if h.category == category]

    def get_hotkeys_by_context(self, context: HotkeyContext) -> List[Hotkey]:
        """
        Get all hotkeys for a context.

        Args:
            context: Context to filter by

        Returns:
            List of hotkeys for the context
        """
        return [h for h in self.hotkeys if h.context in (HotkeyContext.GLOBAL, context)]

    def get_categories(self) -> List[str]:
        """
        Get all unique categories.

        Returns:
            List of category names
        """
        return sorted(set(h.category for h in self.hotkeys))

    def _check_conflicts(self, new_hotkey: Hotkey):
        """
        Check for conflicts with existing hotkeys.

        Args:
            new_hotkey: Hotkey to check
        """
        for hotkey in self.hotkeys:
            if hotkey == new_hotkey:
                continue

            # Check if they would conflict
            if (
                hotkey.key == new_hotkey.key
                and hotkey.modifiers == new_hotkey.modifiers
                and hotkey.context in (HotkeyContext.GLOBAL, new_hotkey.context)
            ):
                # Found a conflict
                if (hotkey, new_hotkey) not in self.conflicts and (
                    new_hotkey,
                    hotkey,
                ) not in self.conflicts:
                    self.conflicts.append((hotkey, new_hotkey))

    def get_conflicts(self) -> List[Tuple[Hotkey, Hotkey]]:
        """
        Get all conflicting hotkeys.

        Returns:
            List of conflicting hotkey pairs
        """
        return self.conflicts

    def save_config(self, filepath: Optional[str] = None):
        """
        Save hotkey configuration to file.

        Args:
            filepath: Path to save to (defaults to self.config_file)
        """
        filepath = filepath or self.config_file

        data = {
            "hotkeys": [h.to_dict() for h in self.hotkeys],
            "current_context": self.current_context.value,
        }

        try:
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)
            print(f"Hotkey configuration saved to {filepath}")
        except Exception as e:
            print(f"Failed to save hotkey configuration: {e}")

    def load_config(self, filepath: Optional[str] = None):
        """
        Load hotkey configuration from file.

        Args:
            filepath: Path to load from (defaults to self.config_file)
        """
        filepath = filepath or self.config_file

        try:
            with open(filepath, "r") as f:
                data = json.load(f)

            # Clear existing hotkeys
            callbacks = {h.action: h.callback for h in self.hotkeys if h.callback}
            self.hotkeys.clear()

            # Load hotkeys
            for hotkey_data in data.get("hotkeys", []):
                action = hotkey_data["action"]
                callback = callbacks.get(action)
                hotkey = Hotkey.from_dict(hotkey_data, callback)
                self.hotkeys.append(hotkey)

            # Load context
            context_value = data.get("current_context", "global")
            self.current_context = HotkeyContext(context_value)

            print(f"Hotkey configuration loaded from {filepath}")
        except FileNotFoundError:
            print(f"No hotkey configuration found at {filepath}, using defaults")
        except Exception as e:
            print(f"Failed to load hotkey configuration: {e}")

    def reset_to_defaults(self):
        """Reset all hotkeys to default configuration."""
        self.hotkeys.clear()
        self.conflicts.clear()
        self._register_default_hotkeys()

    def get_help_text(self) -> Dict[str, List[Tuple[str, str]]]:
        """
        Get help text organized by category.

        Returns:
            Dictionary mapping category names to list of (shortcut, description) tuples
        """
        help_dict: Dict[str, List[Tuple[str, str]]] = {}

        for hotkey in self.hotkeys:
            if not hotkey.enabled:
                continue

            category = hotkey.category
            if category not in help_dict:
                help_dict[category] = []

            help_dict[category].append((hotkey.get_display_name(), hotkey.description))

        # Sort each category's shortcuts
        for category in help_dict:
            help_dict[category].sort(key=lambda x: x[0])

        return help_dict


# Global hotkey manager instance
_hotkey_manager: Optional[HotkeyManager] = None


def get_hotkey_manager() -> HotkeyManager:
    """
    Get the global hotkey manager instance.

    Returns:
        HotkeyManager instance
    """
    global _hotkey_manager
    if _hotkey_manager is None:
        _hotkey_manager = HotkeyManager()
    return _hotkey_manager


def reset_hotkey_manager():
    """Reset the global hotkey manager instance."""
    global _hotkey_manager
    _hotkey_manager = None
