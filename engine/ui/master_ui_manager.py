"""
Master UI Manager

Manages all UI components including event editor, level builder, and other tools.
Handles keyboard shortcuts and UI state management.
"""

from typing import Any, Dict, Optional

import pygame

from neonworks.engine.ui.event_editor_ui import EventEditorUI


class MasterUIManager:
    """
    Central UI manager for all editor tools.

    Keyboard Shortcuts:
    - F5: Open/Close Event Editor
    - F6: Open/Close Level Builder
    - F7: Open/Close Database Editor
    - ESC: Close active UI
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen

        # UI Components
        self.event_editor: Optional[EventEditorUI] = None
        self.level_builder = None  # Will be created later
        self.database_editor = None  # Future feature

        # Active UI tracking
        self.active_ui: Optional[str] = None

        # Initialize UIs
        self._initialize_uis()

    def _initialize_uis(self):
        """Initialize all UI components."""
        # Event Editor
        self.event_editor = EventEditorUI(self.screen)

        # Level Builder will be created when needed
        # self.level_builder = LevelBuilderUI(self.screen)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events.

        Args:
            event: Pygame event

        Returns:
            True if event was handled by UI, False otherwise
        """
        # Handle keyboard shortcuts
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F5:
                self.toggle_event_editor()
                return True
            elif event.key == pygame.K_F6:
                self.toggle_level_builder()
                return True
            elif event.key == pygame.K_F7:
                self.toggle_database_editor()
                return True
            elif event.key == pygame.K_ESCAPE:
                if self.active_ui:
                    self.close_active_ui()
                    return True

        # Route events to active UI
        if self.active_ui == "event_editor" and self.event_editor:
            return self.event_editor.handle_event(event)
        elif self.active_ui == "level_builder" and self.level_builder:
            return self.level_builder.handle_event(event)
        elif self.active_ui == "database_editor" and self.database_editor:
            return self.database_editor.handle_event(event)

        return False

    def update(self, delta_time: float):
        """
        Update active UI components.

        Args:
            delta_time: Time since last frame in seconds
        """
        if self.active_ui == "event_editor" and self.event_editor:
            self.event_editor.update(delta_time)
        elif self.active_ui == "level_builder" and self.level_builder:
            self.level_builder.update(delta_time)
        elif self.active_ui == "database_editor" and self.database_editor:
            self.database_editor.update(delta_time)

    def render(self):
        """Render active UI components."""
        if self.active_ui == "event_editor" and self.event_editor:
            self.event_editor.render()
        elif self.active_ui == "level_builder" and self.level_builder:
            self.level_builder.render()
        elif self.active_ui == "database_editor" and self.database_editor:
            self.database_editor.render()

    # UI Toggle Methods

    def toggle_event_editor(self):
        """Toggle the event editor on/off."""
        if self.active_ui == "event_editor":
            self.close_event_editor()
        else:
            self.open_event_editor()

    def open_event_editor(self, event_data: Optional[Dict[str, Any]] = None):
        """
        Open the event editor.

        Args:
            event_data: Optional event data to edit
        """
        if not self.event_editor:
            self.event_editor = EventEditorUI(self.screen)

        if event_data:
            self.event_editor.load_event(event_data)

        self.active_ui = "event_editor"
        print("📝 Event Editor opened (F5 to close)")

    def close_event_editor(self) -> Optional[Dict[str, Any]]:
        """
        Close the event editor.

        Returns:
            Event data if saved, None if cancelled
        """
        result = None
        if self.event_editor:
            result = self.event_editor.get_current_event()

        self.active_ui = None
        print("✓ Event Editor closed")
        return result

    def toggle_level_builder(self):
        """Toggle the level builder on/off."""
        if self.active_ui == "level_builder":
            self.close_level_builder()
        else:
            self.open_level_builder()

    def open_level_builder(self):
        """Open the level builder."""
        # Lazy load level builder
        if not self.level_builder:
            try:
                from neonworks.engine.ui.level_builder_ui import LevelBuilderUI

                self.level_builder = LevelBuilderUI(self.screen)
            except ImportError:
                print("⚠ Level Builder not yet implemented")
                return

        self.active_ui = "level_builder"
        print("🗺 Level Builder opened (F6 to close)")

    def close_level_builder(self):
        """Close the level builder."""
        self.active_ui = None
        print("✓ Level Builder closed")

    def toggle_database_editor(self):
        """Toggle the database editor on/off."""
        if self.active_ui == "database_editor":
            self.close_database_editor()
        else:
            self.open_database_editor()

    def open_database_editor(self):
        """Open the database editor."""
        # Future feature
        print("⚠ Database Editor not yet implemented (coming soon!)")

    def close_database_editor(self):
        """Close the database editor."""
        self.active_ui = None
        print("✓ Database Editor closed")

    def close_active_ui(self):
        """Close whatever UI is currently active."""
        if self.active_ui == "event_editor":
            self.close_event_editor()
        elif self.active_ui == "level_builder":
            self.close_level_builder()
        elif self.active_ui == "database_editor":
            self.close_database_editor()

    # Query Methods

    def is_any_ui_active(self) -> bool:
        """Check if any UI is currently active."""
        return self.active_ui is not None

    def get_active_ui(self) -> Optional[str]:
        """Get the name of the currently active UI."""
        return self.active_ui

    # Help Methods

    def show_help(self):
        """Display help information about available shortcuts."""
        help_text = """
╔═══════════════════════════════════════════════════╗
║          NEONWORKS EDITOR - KEYBOARD SHORTCUTS    ║
╠═══════════════════════════════════════════════════╣
║  F5  - Event Editor (Create/Edit game events)    ║
║  F6  - Level Builder (Create/Edit maps)          ║
║  F7  - Database Editor (Manage game data)        ║
║  ESC - Close active editor                       ║
╚═══════════════════════════════════════════════════╝
        """
        print(help_text)
