"""
Master UI Manager

Manages all UI components including event editor, level builder, and other tools.
Handles keyboard shortcuts and UI state management.
"""

from typing import Any, Dict, Optional

import pygame

from neonworks.engine.ui.character_generator_ui import CharacterGeneratorUI
from neonworks.engine.ui.event_editor_ui import EventEditorUI
from neonworks.engine.ui.face_generator_ui import FaceGeneratorUI


class MasterUIManager:
    """
    Central UI manager for all editor tools.

    Keyboard Shortcuts:
    - F5: Open/Close Event Editor
    - F6: Open/Close Database Editor
    - F7: Open/Close Level Builder
    - F8: Open/Close Character Generator
    - F9: Open/Close Face Generator
    - ESC: Close active UI
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen

        # UI Components
        self.event_editor: Optional[EventEditorUI] = None
        self.level_builder = None  # Will be created later
        self.database_editor = None  # Will be lazy-loaded
        self.character_generator: Optional[CharacterGeneratorUI] = None
        self.face_generator: Optional[FaceGeneratorUI] = None

        # Active UI tracking
        self.active_ui: Optional[str] = None

        # Initialize UIs
        self._initialize_uis()

    def _initialize_uis(self):
        """Initialize all UI components."""
        # Event Editor
        self.event_editor = EventEditorUI(self.screen)

        # Character Generator
        self.character_generator = CharacterGeneratorUI(self.screen)

        # Face Generator (with character generator reference for color sync)
        self.face_generator = FaceGeneratorUI(self.screen, self.character_generator)

        # Database Editor will be lazy-loaded when needed
        # Level Builder will be created when needed
        # self.level_builder = LevelBuilderUI(self.screen)

    def _connect_ui_components(self):
        """Connect UI components for cross-referencing (called after lazy loading)."""
        # Set character generator UI references
        if self.character_generator:
            self.character_generator.set_ui_references(
                database_editor=self.database_editor,
                asset_browser=None,  # Will be set if asset browser is added
                level_builder=self.level_builder,
            )
            print("✓ Character generator UI components connected")

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
                self.toggle_database_editor()
                return True
            elif event.key == pygame.K_F7:
                self.toggle_level_builder()
                return True
            elif event.key == pygame.K_F8:
                self.toggle_character_generator()
                return True
            elif event.key == pygame.K_F9:
                self.toggle_face_generator()
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
        elif self.active_ui == "character_generator" and self.character_generator:
            return self.character_generator.handle_event(event)
        elif self.active_ui == "face_generator" and self.face_generator:
            return self.face_generator.handle_event(event)

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
        elif self.active_ui == "character_generator" and self.character_generator:
            self.character_generator.update(delta_time)
        elif self.active_ui == "face_generator" and self.face_generator:
            self.face_generator.update(delta_time)

    def render(self):
        """Render active UI components."""
        if self.active_ui == "event_editor" and self.event_editor:
            self.event_editor.render()
        elif self.active_ui == "level_builder" and self.level_builder:
            self.level_builder.render()
        elif self.active_ui == "database_editor" and self.database_editor:
            self.database_editor.render()
        elif self.active_ui == "character_generator" and self.character_generator:
            self.character_generator.render()
        elif self.active_ui == "face_generator" and self.face_generator:
            self.face_generator.render()

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
        # Lazy load database editor
        if not self.database_editor:
            try:
                from neonworks.engine.ui.database_editor_ui import DatabaseEditorUI

                self.database_editor = DatabaseEditorUI(self.screen)
                # Connect UI components after loading
                self._connect_ui_components()
            except ImportError as e:
                print(f"⚠ Database Editor failed to load: {e}")
                return

        self.database_editor.visible = True
        self.active_ui = "database_editor"
        print("🗄 Database Editor opened (F6 to close)")

    def close_database_editor(self):
        """Close the database editor."""
        if self.database_editor:
            self.database_editor.visible = False
        self.active_ui = None
        print("✓ Database Editor closed")

    def toggle_character_generator(self):
        """Toggle the character generator on/off."""
        if self.active_ui == "character_generator":
            self.close_character_generator()
        else:
            self.open_character_generator()

    def open_character_generator(self):
        """Open the character generator."""
        if not self.character_generator:
            self.character_generator = CharacterGeneratorUI(self.screen)

        self.character_generator.visible = True
        self.active_ui = "character_generator"
        print("🎨 Character Generator opened (F8 to close)")

    def close_character_generator(self):
        """Close the character generator."""
        if self.character_generator:
            self.character_generator.visible = False
        self.active_ui = None
        print("✓ Character Generator closed")

    def toggle_face_generator(self):
        """Toggle the face generator on/off."""
        if self.active_ui == "face_generator":
            self.close_face_generator()
        else:
            self.open_face_generator()

    def open_face_generator(self):
        """Open the face generator."""
        if not self.face_generator:
            self.face_generator = FaceGeneratorUI(self.screen, self.character_generator)

        self.face_generator.visible = True
        self.active_ui = "face_generator"
        print("😊 Face Generator opened (F9 to close)")

    def close_face_generator(self):
        """Close the face generator."""
        if self.face_generator:
            self.face_generator.visible = False
        self.active_ui = None
        print("✓ Face Generator closed")

    def close_active_ui(self):
        """Close whatever UI is currently active."""
        if self.active_ui == "event_editor":
            self.close_event_editor()
        elif self.active_ui == "level_builder":
            self.close_level_builder()
        elif self.active_ui == "database_editor":
            self.close_database_editor()
        elif self.active_ui == "character_generator":
            self.close_character_generator()
        elif self.active_ui == "face_generator":
            self.close_face_generator()

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
║  F6  - Database Editor (Manage game data)        ║
║  F7  - Level Builder (Create/Edit maps)          ║
║  F8  - Character Generator (Create characters)   ║
║  F9  - Face Generator (Create face portraits)    ║
║  ESC - Close active editor                       ║
╚═══════════════════════════════════════════════════╝
        """
        print(help_text)
