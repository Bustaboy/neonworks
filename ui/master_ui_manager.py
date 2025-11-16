"""
NeonWorks Master UI Manager - Unified UI System Management
Provides a single interface for managing all visual UI systems in NeonWorks.
"""

from typing import Any, Dict, Optional

import pygame

from ..audio.audio_manager import AudioManager
from ..core.ecs import World
from ..core.hotkey_manager import HotkeyContext, get_hotkey_manager
from ..core.state import StateManager
from ..input.input_manager import InputManager
from .event_editor_ui import EventEditorUI
from .database_manager_ui import DatabaseManagerUI
from .character_generator_ui import CharacterGeneratorUI
from .ai_animator_ui import AIAnimatorUI
from .ai_asset_editor import AIAssetEditor
from .ai_asset_inspector import AIAssetInspector
from .ai_assistant_panel import AIAssistantPanel
from .asset_browser_ui import AssetBrowserUI
from .autotile_editor_ui import AutotileEditorUI
from .building_ui import BuildingUI
from .combat_ui import CombatUI
from .debug_console_ui import DebugConsoleUI
from .game_hud import GameHUD
from .history_viewer_ui import HistoryViewerUI
from .level_builder_ui import LevelBuilderUI
from .map_manager_ui import MapManagerUI
from .navmesh_editor_ui import NavmeshEditorUI
from .project_manager_ui import ProjectManagerUI
from .quest_editor_ui import QuestEditorUI
from .settings_ui import SettingsUI
from .shortcuts_overlay_ui import ShortcutsOverlayUI
from .workspace_system import get_workspace_manager
from .workspace_toolbar import WorkspaceToolbar


class MasterUIManager:
    """
    Master UI Manager that coordinates all visual UI systems.
    Provides a unified interface for managing and rendering all UIs.
    """

    def __init__(
        self,
        screen: pygame.Surface,
        world: World,
        state_manager: Optional[StateManager] = None,
        audio_manager: Optional[AudioManager] = None,
        input_manager: Optional[InputManager] = None,
        renderer=None,
    ):
        self.screen = screen
        self.world = world
        self.state_manager = state_manager
        self.audio_manager = audio_manager
        self.input_manager = input_manager
        self.renderer = renderer

        # Hotkey manager
        self.hotkey_manager = get_hotkey_manager()

        # Initialize all UI systems
        self.game_hud = GameHUD(screen)
        self.building_ui = BuildingUI(screen, world)
        self.combat_ui = CombatUI(screen, world)
        self.navmesh_editor = NavmeshEditorUI(screen, world)
        self.level_builder = LevelBuilderUI(screen, world)
        self.event_editor = EventEditorUI(world, renderer)
        self.database_editor = DatabaseManagerUI(world, renderer)
        self.character_generator = CharacterGeneratorUI(world, renderer)
        self.settings_ui = SettingsUI(screen, audio_manager, input_manager)
        self.project_manager = ProjectManagerUI(screen, state_manager)
        self.debug_console = DebugConsoleUI(screen, world)
        self.quest_editor = QuestEditorUI(screen)
        self.asset_browser = AssetBrowserUI(screen)
        self.autotile_editor = AutotileEditorUI(screen)
        self.ai_animator = AIAnimatorUI(world, renderer)
        self.map_manager = MapManagerUI(screen)
        self.shortcuts_overlay = ShortcutsOverlayUI(screen)

        # AI Assistant System
        self.ai_assistant = AIAssistantPanel(screen, world)
        self.ai_asset_inspector = AIAssetInspector(screen, world)
        self.ai_asset_editor = AIAssetEditor()

        # Connect level builder to event editor for event management
        self.level_builder.event_editor = self.event_editor

        # Workspace system and toolbar
        self.workspace_manager = get_workspace_manager()
        self.workspace_toolbar = WorkspaceToolbar(screen, master_ui_manager=self)

        # History viewers for each editor
        self.level_builder_history = HistoryViewerUI(screen, self.level_builder.undo_manager)
        self.navmesh_history = HistoryViewerUI(screen, self.navmesh_editor.undo_manager)

        # UI state
        self.current_mode = "game"  # 'game', 'editor', 'menu'
        self.current_editor = None  # Currently active editor
        self.previous_editor = None  # Previously active editor for transitions

        # Editor state management
        self.all_editors = {
            "event": self.event_editor,
            "database": self.database_editor,
            "character_gen": self.character_generator,
            "level": self.level_builder,
            "navmesh": self.navmesh_editor,
            "quest": self.quest_editor,
            "asset": self.asset_browser,
            "autotile": self.autotile_editor,
        }

        # Editor transitions
        self.transition_active = False
        self.transition_progress = 0.0  # 0.0 to 1.0
        self.transition_duration = 0.3  # seconds
        self.transition_from = None
        self.transition_to = None

        # Auto-save functionality
        self.auto_save_enabled = True
        self.auto_save_interval = 60.0  # seconds
        self.auto_save_timer = 0.0
        self.last_auto_save_time = 0.0

        # Status bar state
        self.status_message = "Ready"
        self.status_color = (200, 200, 200)
        self.current_tool = "None"

        # Key bindings (F5-F8 for main editors)
        # Note: These are kept for backward compatibility, but hotkey_manager is now preferred
        self.keybinds = {
            pygame.K_F1: self.toggle_debug_console,
            pygame.K_F2: self.toggle_settings,
            pygame.K_F3: self.toggle_building_ui,
            pygame.K_F4: self.toggle_level_builder,
            pygame.K_F5: self.toggle_event_editor,
            pygame.K_F6: self.toggle_database_editor,
            pygame.K_F7: self.toggle_character_generator,
            pygame.K_F8: self.toggle_quest_editor,
            pygame.K_F9: self.toggle_combat_ui,
            pygame.K_F10: self.toggle_game_hud,
            pygame.K_F11: self.toggle_autotile_editor,
            pygame.K_F12: self.toggle_navmesh_editor,
        }

        # Wire up hotkey manager callbacks
        self._setup_hotkey_callbacks()

    def _setup_hotkey_callbacks(self):
        """Wire up all hotkey manager callbacks."""
        # UI Editors
        self.hotkey_manager.set_callback("toggle_debug_console", self.toggle_debug_console)
        self.hotkey_manager.set_callback("toggle_settings", self.toggle_settings)
        self.hotkey_manager.set_callback("toggle_building_ui", self.toggle_building_ui)
        self.hotkey_manager.set_callback("toggle_level_builder", self.toggle_level_builder)
        self.hotkey_manager.set_callback("toggle_event_editor", self.toggle_event_editor)
        self.hotkey_manager.set_callback("toggle_database_editor", self.toggle_database_editor)
        self.hotkey_manager.set_callback("toggle_character_generator", self.toggle_character_generator)
        self.hotkey_manager.set_callback("toggle_quest_editor", self.toggle_quest_editor)
        self.hotkey_manager.set_callback("toggle_asset_browser", self.toggle_asset_browser)
        self.hotkey_manager.set_callback("toggle_project_manager", self.toggle_project_manager)
        self.hotkey_manager.set_callback("toggle_combat_ui", self.toggle_combat_ui)
        self.hotkey_manager.set_callback("toggle_game_hud", self.toggle_game_hud)
        self.hotkey_manager.set_callback("toggle_autotile_editor", self.toggle_autotile_editor)
        self.hotkey_manager.set_callback("toggle_navmesh_editor", self.toggle_navmesh_editor)

        # Special UI shortcuts
        self.hotkey_manager.set_callback("toggle_ai_animator", self.toggle_ai_animator)
        self.hotkey_manager.set_callback("toggle_map_manager", self.toggle_map_manager)
        self.hotkey_manager.set_callback("toggle_ai_assistant", self.toggle_ai_assistant)
        self.hotkey_manager.set_callback("toggle_history_viewer", self._toggle_active_history_viewer)
        self.hotkey_manager.set_callback("show_shortcuts_overlay", self.shortcuts_overlay.toggle)

        # Edit commands
        self.hotkey_manager.set_callback("undo", self._handle_undo)
        self.hotkey_manager.set_callback("redo", self._handle_redo)
        self.hotkey_manager.set_callback("redo_alt", self._handle_redo)

    def _toggle_active_history_viewer(self):
        """Toggle history viewer for the active editor."""
        if self.level_builder.visible:
            self.level_builder_history.toggle()
        elif self.navmesh_editor.visible:
            self.navmesh_history.toggle()

    def _handle_undo(self):
        """Handle undo action for active editor."""
        if self.level_builder.visible and hasattr(self.level_builder, "undo"):
            self.level_builder.undo()
        elif self.navmesh_editor.visible and hasattr(self.navmesh_editor, "undo"):
            self.navmesh_editor.undo()

    def _handle_redo(self):
        """Handle redo action for active editor."""
        if self.level_builder.visible and hasattr(self.level_builder, "redo"):
            self.level_builder.redo()
        elif self.navmesh_editor.visible and hasattr(self.navmesh_editor, "redo"):
            self.navmesh_editor.redo()

    def render(self, fps: float = 60.0, camera_offset: tuple = (0, 0)):
        """
        Render all active UI systems.
        """
        # Apply transition effect if active
        if self.transition_active:
            self._render_transition()

        # Render workspace toolbar first (at top)
        self.workspace_toolbar.render()

        # Always render game HUD if in game mode
        if self.current_mode == "game" and self.game_hud.visible:
            self.game_hud.render(self.world, fps)

        # Render combat UI if visible
        if self.combat_ui.visible:
            self.combat_ui.render()

        # Render building UI if visible
        if self.building_ui.visible:
            self.building_ui.render(camera_offset)

        # Render level builder if visible
        if self.level_builder.visible:
            self.level_builder.render(camera_offset)

        # Render navmesh editor if visible
        if self.navmesh_editor.visible:
            self.navmesh_editor.render(camera_offset)

        # Render quest editor if visible
        if self.quest_editor.visible:
            self.quest_editor.render()

        # Render event editor if visible
        if self.event_editor.visible:
            self.event_editor.render(self.screen)

        # Render database editor if visible
        if self.database_editor.visible:
            self.database_editor.render(self.screen)

        # Render character generator if visible
        if self.character_generator.visible:
            self.character_generator.render(self.screen)

        # Render asset browser if visible
        if self.asset_browser.visible:
            self.asset_browser.render()

        # Render AI Animator if visible
        if self.ai_animator.visible:
            self.ai_animator.render(self.screen)

        # Render project manager if visible
        if self.project_manager.visible:
            self.project_manager.render()

        # Render settings if visible
        if self.settings_ui.visible:
            self.settings_ui.render()

        # Render autotile editor if visible
        if self.autotile_editor.visible:
            self.autotile_editor.render(self.screen)

        # Render map manager if visible
        if self.map_manager.visible:
            self.map_manager.render()

        # Render AI Assistant Panel if visible
        if self.ai_assistant.visible:
            self.ai_assistant.render()

        # Render AI Asset Inspector if visible (shows entity properties)
        if self.ai_asset_inspector.visible:
            self.ai_asset_inspector.render(camera_offset, tile_size=32)

        # Render history viewers if visible
        if self.level_builder_history.visible:
            self.level_builder_history.render()

        if self.navmesh_history.visible:
            self.navmesh_history.render()

        # Always render debug console last (on top of everything)
        if self.debug_console.visible:
            self.debug_console.render(fps)

        # Render shortcuts overlay on top of everything
        if self.shortcuts_overlay.visible:
            self.shortcuts_overlay.render()

        # Render status bar at the bottom (on top of everything else)
        self._render_status_bar()

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events and route them to appropriate UI systems.
        Returns True if event was handled by UI.
        """
        # Update hotkey manager context based on current mode
        if self.current_mode == "game":
            if self.combat_ui.visible:
                self.hotkey_manager.set_context(HotkeyContext.COMBAT)
            elif self.building_ui.visible:
                self.hotkey_manager.set_context(HotkeyContext.BUILDING)
            else:
                self.hotkey_manager.set_context(HotkeyContext.GAME)
        elif self.current_mode == "editor":
            self.hotkey_manager.set_context(HotkeyContext.EDITOR)
        elif self.current_mode == "menu":
            self.hotkey_manager.set_context(HotkeyContext.MENU)

        # Shortcuts overlay gets highest priority
        if self.shortcuts_overlay.visible:
            if self.shortcuts_overlay.handle_event(event):
                return True

        # Workspace toolbar gets second priority
        if self.workspace_toolbar.handle_event(event):
            return True

        # Handle history viewer events first
        if self.level_builder_history.visible:
            if self.level_builder_history.handle_event(event):
                return True

        if self.navmesh_history.visible:
            if self.navmesh_history.handle_event(event):
                return True

        # Handle mouse wheel events
        if event.type == pygame.MOUSEWHEEL:
            # Settings UI scrolling
            if self.settings_ui.visible:
                self.settings_ui.handle_mouse_wheel(event.y)
                return True

        # Handle key presses
        if event.type == pygame.KEYDOWN:
            # Try hotkey manager first (handles all configured shortcuts)
            action = self.hotkey_manager.handle_event(event)
            if action:
                # Action was handled by hotkey manager
                return True

            # Legacy handling for backward compatibility
            ctrl_pressed = pygame.key.get_mods() & pygame.KMOD_CTRL
            shift_pressed = pygame.key.get_mods() & pygame.KMOD_SHIFT

            # Check for Shift+F7 (AI Animator) - fallback
            if event.key == pygame.K_F7 and shift_pressed:
                self.toggle_ai_animator()
                return True

            # Check for Ctrl+M (Map Manager) - fallback
            if event.key == pygame.K_m and ctrl_pressed:
                self.toggle_map_manager()
                return True

            # Check for Ctrl+Space (AI Assistant) - fallback
            if event.key == pygame.K_SPACE and ctrl_pressed:
                self.toggle_ai_assistant()
                return True

            # Ctrl+H: Toggle history viewer for active editor - fallback
            if ctrl_pressed and event.key == pygame.K_h:
                if self.level_builder.visible:
                    self.level_builder_history.toggle()
                    return True
                elif self.navmesh_editor.visible:
                    self.navmesh_history.toggle()
                    return True

            # Check for standard keybinds - fallback
            if event.key in self.keybinds:
                self.keybinds[event.key]()
                return True

            # Route to debug console if active
            if self.debug_console.visible:
                self.debug_console.handle_key_press(event.key)
                return True

            # Route to settings UI if active
            if self.settings_ui.visible:
                self.settings_ui.handle_key_press(event.key)
                return True

        # Handle text input
        if event.type == pygame.TEXTINPUT:
            if self.debug_console.visible:
                self.debug_console.handle_text_input(event.text)
                return True

            if self.asset_browser.visible:
                self.asset_browser.handle_text_input(event.text)
                return True

        # Route events to map manager if visible
        if self.map_manager.visible:
            if self.map_manager.handle_event(event):
                return True

        # Route events to autotile editor if visible
        if self.autotile_editor.visible:
            self.autotile_editor.handle_event(event)
            return True

        # Route events to event editor if visible
        if self.event_editor.visible:
            self.event_editor.handle_event(event)
            return True

        # Route events to database editor if visible
        if self.database_editor.visible:
            self.database_editor.handle_event(event)
            return True

        # Route events to character generator if visible
        if self.character_generator.visible:
            self.character_generator.handle_event(event)
            return True

        # Route events to AI Animator if visible
        if self.ai_animator.visible:
            self.ai_animator.handle_event(event)
            return True

        # Route events to AI Assistant Panel if visible
        if self.ai_assistant.visible:
            if self.ai_assistant.handle_event(event):
                return True

        # Route events to AI Asset Inspector if visible
        if self.ai_asset_inspector.visible:
            if self.ai_asset_inspector.handle_event(event):
                return True

        # Route events to navmesh editor if visible
        if self.navmesh_editor.visible:
            if self.navmesh_editor.handle_event(event):
                return True

        # Handle mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Get mouse position
                mouse_pos = pygame.mouse.get_pos()

                # Convert to grid position if needed
                # (This would depend on camera offset and tile size)
                grid_x = mouse_pos[0] // 32
                grid_y = mouse_pos[1] // 32

                # Route to active UI systems
                if self.building_ui.visible:
                    if self.building_ui.handle_click(grid_x, grid_y):
                        return True

                if self.level_builder.visible:
                    if self.level_builder.handle_click(grid_x, grid_y):
                        return True

                if self.combat_ui.visible:
                    # Check if clicking on an entity
                    # (This would require collision detection)
                    pass

                # Ctrl+Click for AI asset inspection
                mods = pygame.key.get_mods()
                if mods & pygame.KMOD_CTRL:
                    # Find entity at click position (convert to grid)
                    grid_x = mouse_pos[0] // 32  # TODO: Get tile_size from renderer
                    grid_y = mouse_pos[1] // 32

                    # Find entity at this grid position
                    from ..core.ecs import GridPosition

                    for entity in self.world.entities.values():
                        grid_pos = entity.get_component(GridPosition)
                        if grid_pos and grid_pos.x == grid_x and grid_pos.y == grid_y:
                            # Found entity - inspect it
                            self.ai_asset_inspector.select_entity(entity, (grid_x, grid_y))
                            # Open AI assistant if not visible
                            if not self.ai_assistant.visible:
                                self.ai_assistant.toggle()
                            return True

        return False

    def update(self, dt: float, mouse_pos: tuple, camera_offset: tuple):
        """
        Update UI systems that need per-frame updates.
        """
        # Update transitions
        if self.transition_active:
            self.transition_progress += dt / self.transition_duration
            if self.transition_progress >= 1.0:
                self.transition_progress = 1.0
                self.transition_active = False
                # Finalize transition
                if self.transition_from:
                    self.transition_from = None
                self.transition_to = None

        # Update auto-save timer
        if self.auto_save_enabled:
            self.auto_save_timer += dt
            if self.auto_save_timer >= self.auto_save_interval:
                self._perform_auto_save()
                self.auto_save_timer = 0.0

        # Update current editor tracking
        self._update_current_editor()

        # Update building placement preview
        if self.building_ui.visible and self.building_ui.placement_mode:
            grid_x = (mouse_pos[0] - camera_offset[0]) // self.building_ui.tile_size
            grid_y = (mouse_pos[1] - camera_offset[1]) // self.building_ui.tile_size
            self.building_ui.update_preview_position(grid_x, grid_y)

        # Update navmesh editor painting
        if self.navmesh_editor.visible and self.navmesh_editor.is_painting:
            grid_x = (mouse_pos[0] - camera_offset[0]) // self.navmesh_editor.tile_size
            grid_y = (mouse_pos[1] - camera_offset[1]) // self.navmesh_editor.tile_size
            self.navmesh_editor.continue_painting(grid_x, grid_y)

        # Update autotile editor
        if self.autotile_editor.visible:
            self.autotile_editor.update(dt)

        # Update database editor
        if self.database_editor.visible:
            self.database_editor.update(dt)

        # Update character generator
        if self.character_generator.visible:
            self.character_generator.update(dt)

        # Update AI Animator
        if self.ai_animator.visible:
            self.ai_animator.update(dt)

        # Update map manager
        if self.map_manager.visible:
            self.map_manager.update(dt)

        # Update AI Assistant (with vision context)
        if self.ai_assistant.visible:
            # Get tilemap from level builder if active
            tilemap = None
            if self.level_builder.visible and hasattr(self.level_builder, "tilemap"):
                tilemap = self.level_builder.tilemap

            self.ai_assistant.update(dt, tilemap, camera_offset)

    # Toggle methods for each UI system

    def toggle_game_hud(self):
        """Toggle game HUD visibility."""
        self.game_hud.toggle_visibility()

    def toggle_building_ui(self):
        """Toggle building UI."""
        self.building_ui.toggle()

    def toggle_combat_ui(self):
        """Toggle combat UI."""
        self.combat_ui.toggle_visibility()

    def toggle_level_builder(self):
        """Toggle level builder."""
        self.level_builder.toggle()

    def toggle_navmesh_editor(self):
        """Toggle navmesh editor."""
        self.navmesh_editor.toggle()

    def toggle_autotile_editor(self):
        """Toggle autotile editor."""
        self.autotile_editor.toggle()

    def toggle_ai_animator(self):
        """Toggle AI Animator."""
        self.ai_animator.toggle()

    def toggle_ai_assistant(self):
        """Toggle AI Assistant Panel."""
        self.ai_assistant.toggle()

    def toggle_quest_editor(self):
        """Toggle quest editor."""
        self.quest_editor.toggle()

    def toggle_event_editor(self):
        """Toggle event editor."""
        self._switch_editor("event", self.event_editor)

    def toggle_database_editor(self):
        """Toggle database editor."""
        self._switch_editor("database", self.database_editor)

    def toggle_character_generator(self):
        """Toggle character generator."""
        self._switch_editor("character_gen", self.character_generator)

    def toggle_asset_browser(self):
        """Toggle asset browser."""
        self.asset_browser.toggle()

    def toggle_project_manager(self):
        """Toggle project manager."""
        self.project_manager.toggle()

    def toggle_settings(self):
        """Toggle settings."""
        self.settings_ui.toggle()

    def toggle_debug_console(self):
        """Toggle debug console."""
        self.debug_console.toggle()

    def toggle_map_manager(self):
        """Toggle map manager."""
        self.map_manager.toggle()

    # Utility methods

    def set_mode(self, mode: str):
        """
        Set the current UI mode.
        Modes: 'game', 'editor', 'menu'
        """
        self.current_mode = mode

        # Configure UI visibility based on mode
        if mode == "game":
            self.game_hud.visible = True
            self.combat_ui.visible = True
            self.level_builder.visible = False
            self.navmesh_editor.visible = False
        elif mode == "editor":
            self.game_hud.visible = False
            self.combat_ui.visible = False
        elif mode == "menu":
            self.game_hud.visible = False
            self.combat_ui.visible = False

    def set_selected_entity(self, entity_id: Optional[int]):
        """Set the selected entity for inspection."""
        self.game_hud.set_selected_entity(entity_id)
        self.debug_console.selected_entity = entity_id

    def show_notification(
        self, message: str, duration: float = 3.0, color: tuple = (255, 255, 255)
    ):
        """
        Show a notification message.
        """
        # Add to debug console log
        self.debug_console.add_log(message, color)

        # Add to combat log if combat is active
        if self.combat_ui.visible:
            self.combat_ui.add_log(message, color)

    def get_keybind_help(self) -> str:
        """
        Get a help string showing all keybinds.
        Uses the hotkey manager to get current bindings.
        """
        help_text = "Keyboard Shortcuts:\n\n"
        help_text += "Press ? (Shift+/) to see the full shortcuts overlay\n\n"

        # Get shortcuts organized by category
        help_dict = self.hotkey_manager.get_help_text()

        # Show only UI and Editor categories in brief help
        for category in ["UI", "Editor", "File"]:
            if category in help_dict:
                help_text += f"{category}:\n"
                for shortcut, description in help_dict[category][:8]:  # Show first 8
                    help_text += f"  {shortcut:20} - {description}\n"
                help_text += "\n"

        help_text += "\nClick the toolbar at the top to access all tools visually!\n"
        help_text += "Press ? for complete keyboard shortcuts reference\n"
        return help_text

    def save_ui_state(self) -> Dict[str, Any]:
        """
        Save UI state for persistence.
        """
        return {
            "game_hud_visible": self.game_hud.visible,
            "current_mode": self.current_mode,
            "settings": self.settings_ui.settings,
        }

    def load_ui_state(self, state: Dict[str, Any]):
        """
        Load UI state from saved data.
        """
        if "game_hud_visible" in state:
            self.game_hud.visible = state["game_hud_visible"]

        if "current_mode" in state:
            self.set_mode(state["current_mode"])

        if "settings" in state:
            self.settings_ui.settings = state["settings"]

    # =========================================================================
    # Editor Management & Transitions
    # =========================================================================

    def _switch_editor(self, editor_name: str, editor_instance):
        """
        Switch to a specific editor with transition effect.

        Args:
            editor_name: Name of the editor
            editor_instance: The editor instance to switch to
        """
        # If editor is already visible, close it
        if editor_instance.visible:
            editor_instance.toggle()
            self.current_editor = None
            self.status_message = "Editor closed"
            return

        # Close current editor if any
        if self.current_editor and self.current_editor != editor_name:
            current_ed = self.all_editors.get(self.current_editor)
            if current_ed and current_ed.visible:
                current_ed.toggle()

        # Start transition
        self.transition_active = True
        self.transition_progress = 0.0
        self.transition_from = self.current_editor
        self.transition_to = editor_name

        # Open new editor
        editor_instance.toggle()
        self.previous_editor = self.current_editor
        self.current_editor = editor_name

        # Update status
        self._update_status_for_editor(editor_name)

    def _update_current_editor(self):
        """Update tracking of which editor is currently active."""
        for name, editor in self.all_editors.items():
            if editor.visible:
                if self.current_editor != name:
                    self.current_editor = name
                    self._update_status_for_editor(name)
                return

        # No editor visible
        if self.current_editor is not None:
            self.current_editor = None
            self.status_message = "Ready"
            self.current_tool = "None"

    def _update_status_for_editor(self, editor_name: str):
        """Update status bar for the given editor."""
        editor_info = {
            "event": ("Event Editor", "Event"),
            "database": ("Database Editor", "Database"),
            "character_gen": ("Character Generator", "Character"),
            "level": ("Level Builder", "Build"),
            "navmesh": ("Navmesh Editor", "Navmesh"),
            "quest": ("Quest Editor", "Quest"),
            "asset": ("Asset Browser", "Assets"),
            "autotile": ("Autotile Editor", "Autotile"),
        }

        if editor_name in editor_info:
            message, tool = editor_info[editor_name]
            self.status_message = f"{message} Active"
            self.current_tool = tool
            self.status_color = (100, 255, 100)
        else:
            self.status_message = "Ready"
            self.current_tool = "None"
            self.status_color = (200, 200, 200)

    def _render_transition(self):
        """Render transition effect between editors."""
        if not self.transition_active:
            return

        # Simple fade effect
        alpha = int(255 * abs(0.5 - self.transition_progress) * 2)
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(alpha)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

    def _render_status_bar(self):
        """Render status bar at the bottom of the screen showing current editor and tool."""
        # Status bar dimensions
        bar_height = 30
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        bar_y = screen_height - bar_height

        # Draw background
        pygame.draw.rect(
            self.screen,
            (40, 40, 45),
            (0, bar_y, screen_width, bar_height)
        )

        # Draw separator line
        pygame.draw.line(
            self.screen,
            (80, 80, 85),
            (0, bar_y),
            (screen_width, bar_y),
            2
        )

        # Render status text
        font = pygame.font.Font(None, 20)

        # Left side: Status message
        status_text = font.render(self.status_message, True, self.status_color)
        self.screen.blit(status_text, (10, bar_y + 7))

        # Center: Current editor
        if self.current_editor:
            editor_text = font.render(
                f"Editor: {self.current_editor.replace('_', ' ').title()}",
                True,
                (200, 200, 255)
            )
            editor_x = (screen_width - editor_text.get_width()) // 2
            self.screen.blit(editor_text, (editor_x, bar_y + 7))

        # Right side: Current tool + auto-save indicator
        tool_text = f"Tool: {self.current_tool}"
        if self.auto_save_enabled:
            time_until_save = int(self.auto_save_interval - self.auto_save_timer)
            tool_text += f" | Auto-save: {time_until_save}s"

        tool_surface = font.render(tool_text, True, (180, 180, 180))
        tool_x = screen_width - tool_surface.get_width() - 10
        self.screen.blit(tool_surface, (tool_x, bar_y + 7))

    def _perform_auto_save(self):
        """Perform auto-save for active editors."""
        saved_something = False

        # Save database editor if active and has changes
        if self.database_editor.visible and hasattr(self.database_editor, "has_unsaved_changes"):
            if self.database_editor.has_unsaved_changes:
                try:
                    if hasattr(self.database_editor.db, "save_to_file"):
                        self.database_editor.db.save_to_file(self.database_editor.database_path)
                        self.database_editor.has_unsaved_changes = False
                        saved_something = True
                except Exception as e:
                    print(f"Auto-save failed for database: {e}")

        # Save character generator if active
        if self.character_generator.visible and hasattr(self.character_generator, "current_preset"):
            try:
                # Character generator auto-save would go here
                # For now, just mark as attempted
                pass
            except Exception as e:
                print(f"Auto-save failed for character generator: {e}")

        # Save level builder if active
        if self.level_builder.visible and hasattr(self.level_builder, "save_current_level"):
            try:
                # Level builder auto-save would go here
                pass
            except Exception as e:
                print(f"Auto-save failed for level builder: {e}")

        # Update status if we saved
        if saved_something:
            self.status_message = "Auto-saved"
            self.status_color = (100, 255, 100)
            self.last_auto_save_time = pygame.time.get_ticks() / 1000.0
