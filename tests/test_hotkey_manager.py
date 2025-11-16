"""
Tests for the Hotkey Manager system.
"""

import json
import os
import tempfile
from unittest.mock import MagicMock, patch

import pygame
import pytest

from neonworks.core.hotkey_manager import (
    Hotkey,
    HotkeyContext,
    HotkeyManager,
    get_hotkey_manager,
    reset_hotkey_manager,
)


class TestHotkey:
    """Test Hotkey class."""

    def test_create_hotkey(self):
        """Test creating a hotkey."""
        hotkey = Hotkey(
            key=pygame.K_a,
            action="test_action",
            description="Test Action",
        )

        assert hotkey.key == pygame.K_a
        assert hotkey.action == "test_action"
        assert hotkey.description == "Test Action"
        assert hotkey.enabled is True
        assert hotkey.context == HotkeyContext.GLOBAL
        assert len(hotkey.modifiers) == 0

    def test_create_hotkey_with_modifiers(self):
        """Test creating a hotkey with modifiers."""
        hotkey = Hotkey(
            key=pygame.K_s,
            action="save",
            modifiers={"ctrl"},
            description="Save",
        )

        assert hotkey.key == pygame.K_s
        assert "ctrl" in hotkey.modifiers
        assert hotkey.action == "save"

    def test_hotkey_matches_simple(self):
        """Test hotkey matching without modifiers."""
        hotkey = Hotkey(key=pygame.K_a, action="test")

        assert hotkey.matches(pygame.K_a, ctrl=False, shift=False, alt=False)
        assert not hotkey.matches(pygame.K_b, ctrl=False, shift=False, alt=False)

    def test_hotkey_matches_with_ctrl(self):
        """Test hotkey matching with Ctrl modifier."""
        hotkey = Hotkey(key=pygame.K_s, action="save", modifiers={"ctrl"})

        assert hotkey.matches(pygame.K_s, ctrl=True, shift=False, alt=False)
        assert not hotkey.matches(pygame.K_s, ctrl=False, shift=False, alt=False)
        assert not hotkey.matches(pygame.K_s, ctrl=True, shift=True, alt=False)

    def test_hotkey_matches_with_multiple_modifiers(self):
        """Test hotkey matching with multiple modifiers."""
        hotkey = Hotkey(key=pygame.K_z, action="redo", modifiers={"ctrl", "shift"})

        assert hotkey.matches(pygame.K_z, ctrl=True, shift=True, alt=False)
        assert not hotkey.matches(pygame.K_z, ctrl=True, shift=False, alt=False)
        assert not hotkey.matches(pygame.K_z, ctrl=False, shift=True, alt=False)

    def test_hotkey_disabled(self):
        """Test that disabled hotkey doesn't match."""
        hotkey = Hotkey(key=pygame.K_a, action="test", enabled=False)

        assert not hotkey.matches(pygame.K_a, ctrl=False, shift=False, alt=False)

    def test_hotkey_display_name(self):
        """Test getting display name for hotkey."""
        hotkey1 = Hotkey(key=pygame.K_s, action="save")
        assert "S" in hotkey1.get_display_name()

        hotkey2 = Hotkey(key=pygame.K_s, action="save", modifiers={"ctrl"})
        display_name = hotkey2.get_display_name()
        assert "Ctrl" in display_name
        assert "S" in display_name

        hotkey3 = Hotkey(key=pygame.K_z, action="redo", modifiers={"ctrl", "shift"})
        display_name = hotkey3.get_display_name()
        assert "Ctrl" in display_name
        assert "Shift" in display_name
        assert "Z" in display_name

    def test_hotkey_serialization(self):
        """Test hotkey serialization and deserialization."""
        hotkey = Hotkey(
            key=pygame.K_s,
            action="save",
            modifiers={"ctrl"},
            context=HotkeyContext.EDITOR,
            description="Save Project",
            category="File",
        )

        # Serialize
        data = hotkey.to_dict()
        assert data["key"] == pygame.K_s
        assert data["action"] == "save"
        assert "ctrl" in data["modifiers"]
        assert data["context"] == "editor"
        assert data["description"] == "Save Project"
        assert data["category"] == "File"

        # Deserialize
        hotkey2 = Hotkey.from_dict(data)
        assert hotkey2.key == hotkey.key
        assert hotkey2.action == hotkey.action
        assert hotkey2.modifiers == hotkey.modifiers
        assert hotkey2.context == hotkey.context
        assert hotkey2.description == hotkey.description
        assert hotkey2.category == hotkey.category


class TestHotkeyManager:
    """Test HotkeyManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = HotkeyManager()
        # Clear default hotkeys for clean testing
        self.manager.hotkeys.clear()

    def test_register_hotkey(self):
        """Test registering a hotkey."""
        callback = MagicMock()
        hotkey = self.manager.register(
            key=pygame.K_a,
            action="test_action",
            callback=callback,
            description="Test",
        )

        assert hotkey in self.manager.hotkeys
        assert hotkey.action == "test_action"
        assert hotkey.callback == callback

    def test_unregister_hotkey(self):
        """Test unregistering a hotkey."""
        self.manager.register(
            key=pygame.K_a,
            action="test_action",
        )

        assert len(self.manager.hotkeys) == 1

        self.manager.unregister("test_action")

        assert len(self.manager.hotkeys) == 0

    def test_set_callback(self):
        """Test setting callback for a hotkey."""
        self.manager.register(key=pygame.K_a, action="test")

        callback = MagicMock()
        self.manager.set_callback("test", callback)

        hotkey = self.manager.get_hotkey("test")
        assert hotkey.callback == callback

    def test_set_context(self):
        """Test setting hotkey context."""
        self.manager.set_context(HotkeyContext.EDITOR)
        assert self.manager.current_context == HotkeyContext.EDITOR

        self.manager.set_context(HotkeyContext.GAME)
        assert self.manager.current_context == HotkeyContext.GAME

    def test_handle_event_simple(self):
        """Test handling a simple key event."""
        callback = MagicMock()
        self.manager.register(
            key=pygame.K_a,
            action="test_action",
            callback=callback,
        )

        # Create mock event
        event = MagicMock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_a

        # Mock modifier keys
        with patch("pygame.key.get_mods", return_value=0):
            action = self.manager.handle_event(event)

        assert action == "test_action"
        callback.assert_called_once()

    def test_handle_event_with_modifiers(self):
        """Test handling event with modifier keys."""
        callback = MagicMock()
        self.manager.register(
            key=pygame.K_s,
            action="save",
            callback=callback,
            modifiers={"ctrl"},
        )

        # Create mock event
        event = MagicMock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_s

        # Mock Ctrl key pressed
        with patch("pygame.key.get_mods", return_value=pygame.KMOD_CTRL):
            action = self.manager.handle_event(event)

        assert action == "save"
        callback.assert_called_once()

    def test_handle_event_wrong_modifiers(self):
        """Test that hotkey doesn't trigger with wrong modifiers."""
        callback = MagicMock()
        self.manager.register(
            key=pygame.K_s,
            action="save",
            callback=callback,
            modifiers={"ctrl"},
        )

        # Create mock event
        event = MagicMock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_s

        # No modifiers pressed
        with patch("pygame.key.get_mods", return_value=0):
            action = self.manager.handle_event(event)

        assert action is None
        callback.assert_not_called()

    def test_handle_event_context_filtering(self):
        """Test that context filtering works."""
        callback = MagicMock()
        self.manager.register(
            key=pygame.K_a,
            action="editor_action",
            callback=callback,
            context=HotkeyContext.EDITOR,
        )

        # Set to GAME context
        self.manager.set_context(HotkeyContext.GAME)

        # Create mock event
        event = MagicMock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_a

        with patch("pygame.key.get_mods", return_value=0):
            action = self.manager.handle_event(event)

        # Should not trigger in wrong context
        assert action is None
        callback.assert_not_called()

        # Set to EDITOR context
        self.manager.set_context(HotkeyContext.EDITOR)

        with patch("pygame.key.get_mods", return_value=0):
            action = self.manager.handle_event(event)

        # Should trigger in correct context
        assert action == "editor_action"
        callback.assert_called_once()

    def test_rebind_hotkey(self):
        """Test rebinding a hotkey to a new key."""
        self.manager.register(key=pygame.K_a, action="test")

        self.manager.rebind("test", pygame.K_b)

        hotkey = self.manager.get_hotkey("test")
        assert hotkey.key == pygame.K_b

    def test_rebind_with_new_modifiers(self):
        """Test rebinding with new modifiers."""
        self.manager.register(key=pygame.K_s, action="save", modifiers={"ctrl"})

        self.manager.rebind("save", pygame.K_s, {"ctrl", "shift"})

        hotkey = self.manager.get_hotkey("save")
        assert "ctrl" in hotkey.modifiers
        assert "shift" in hotkey.modifiers

    def test_get_hotkeys_by_category(self):
        """Test getting hotkeys by category."""
        self.manager.register(key=pygame.K_F1, action="debug", category="UI")
        self.manager.register(key=pygame.K_F2, action="settings", category="UI")
        self.manager.register(key=pygame.K_s, action="save", category="File")

        ui_hotkeys = self.manager.get_hotkeys_by_category("UI")
        assert len(ui_hotkeys) == 2

        file_hotkeys = self.manager.get_hotkeys_by_category("File")
        assert len(file_hotkeys) == 1

    def test_get_hotkeys_by_context(self):
        """Test getting hotkeys by context."""
        self.manager.register(key=pygame.K_a, action="game_action", context=HotkeyContext.GAME)
        self.manager.register(key=pygame.K_b, action="editor_action", context=HotkeyContext.EDITOR)
        self.manager.register(key=pygame.K_c, action="global_action", context=HotkeyContext.GLOBAL)

        game_hotkeys = self.manager.get_hotkeys_by_context(HotkeyContext.GAME)
        # Should include GLOBAL and GAME
        assert len(game_hotkeys) >= 2

        editor_hotkeys = self.manager.get_hotkeys_by_context(HotkeyContext.EDITOR)
        # Should include GLOBAL and EDITOR
        assert len(editor_hotkeys) >= 2

    def test_get_categories(self):
        """Test getting all categories."""
        self.manager.register(key=pygame.K_F1, action="debug", category="UI")
        self.manager.register(key=pygame.K_s, action="save", category="File")
        self.manager.register(key=pygame.K_z, action="undo", category="Editor")

        categories = self.manager.get_categories()
        assert "UI" in categories
        assert "File" in categories
        assert "Editor" in categories

    def test_conflict_detection(self):
        """Test that conflicts are detected."""
        self.manager.register(
            key=pygame.K_s, action="action1", modifiers={"ctrl"}, context=HotkeyContext.GLOBAL
        )

        # This should create a conflict
        self.manager.register(
            key=pygame.K_s, action="action2", modifiers={"ctrl"}, context=HotkeyContext.GAME
        )

        conflicts = self.manager.get_conflicts()
        assert len(conflicts) > 0

    def test_save_and_load_config(self):
        """Test saving and loading configuration."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            temp_file = f.name

        try:
            # Register some hotkeys
            self.manager.register(
                key=pygame.K_s,
                action="save",
                modifiers={"ctrl"},
                description="Save",
                category="File",
            )
            self.manager.register(
                key=pygame.K_o,
                action="open",
                modifiers={"ctrl"},
                description="Open",
                category="File",
            )

            # Save config
            self.manager.save_config(temp_file)

            # Create new manager and load
            manager2 = HotkeyManager()
            manager2.hotkeys.clear()  # Clear defaults
            manager2.load_config(temp_file)

            # Verify loaded
            assert len(manager2.hotkeys) == 2
            save_hotkey = manager2.get_hotkey("save")
            assert save_hotkey is not None
            assert save_hotkey.key == pygame.K_s
            assert "ctrl" in save_hotkey.modifiers

        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_reset_to_defaults(self):
        """Test resetting to default configuration."""
        # Add a custom hotkey
        self.manager.register(key=pygame.K_x, action="custom")
        custom_hotkey = self.manager.get_hotkey("custom")
        assert custom_hotkey is not None

        # Reset to defaults
        self.manager.reset_to_defaults()

        # Custom hotkey should be gone
        assert self.manager.get_hotkey("custom") is None

        # Should have some default hotkeys
        assert len(self.manager.hotkeys) > 0

    def test_get_help_text(self):
        """Test getting help text."""
        self.manager.register(
            key=pygame.K_F1,
            action="help",
            description="Show Help",
            category="Help",
        )

        help_dict = self.manager.get_help_text()
        assert "Help" in help_dict
        assert len(help_dict["Help"]) > 0

        # Check format
        shortcut, description = help_dict["Help"][0]
        assert isinstance(shortcut, str)
        assert isinstance(description, str)

    def test_disabled_manager(self):
        """Test that disabled manager doesn't handle events."""
        callback = MagicMock()
        self.manager.register(key=pygame.K_a, action="test", callback=callback)

        # Disable manager
        self.manager.enabled = False

        event = MagicMock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_a

        with patch("pygame.key.get_mods", return_value=0):
            action = self.manager.handle_event(event)

        assert action is None
        callback.assert_not_called()


class TestGlobalHotkeyManager:
    """Test global hotkey manager functions."""

    def test_get_hotkey_manager(self):
        """Test getting global hotkey manager."""
        manager1 = get_hotkey_manager()
        manager2 = get_hotkey_manager()

        # Should be same instance
        assert manager1 is manager2

    def test_reset_hotkey_manager(self):
        """Test resetting global hotkey manager."""
        manager1 = get_hotkey_manager()
        reset_hotkey_manager()
        manager2 = get_hotkey_manager()

        # Should be different instances
        assert manager1 is not manager2


class TestHotkeyIntegration:
    """Integration tests for hotkey system."""

    def test_complete_workflow(self):
        """Test a complete hotkey workflow."""
        manager = HotkeyManager()
        manager.hotkeys.clear()

        # Register callbacks
        save_called = {"value": False}
        open_called = {"value": False}

        def save_callback():
            save_called["value"] = True

        def open_callback():
            open_called["value"] = True

        # Register hotkeys
        manager.register(key=pygame.K_s, action="save", callback=save_callback, modifiers={"ctrl"})
        manager.register(key=pygame.K_o, action="open", callback=open_callback, modifiers={"ctrl"})

        # Simulate Ctrl+S
        event = MagicMock()
        event.type = pygame.KEYDOWN
        event.key = pygame.K_s

        with patch("pygame.key.get_mods", return_value=pygame.KMOD_CTRL):
            action = manager.handle_event(event)

        assert action == "save"
        assert save_called["value"] is True
        assert open_called["value"] is False

        # Reset
        save_called["value"] = False
        open_called["value"] = False

        # Simulate Ctrl+O
        event.key = pygame.K_o

        with patch("pygame.key.get_mods", return_value=pygame.KMOD_CTRL):
            action = manager.handle_event(event)

        assert action == "open"
        assert save_called["value"] is False
        assert open_called["value"] is True
