"""
NeonWorks Master UI Manager - Unified UI System Management
Provides a single interface for managing all visual UI systems in NeonWorks.
"""

from typing import Any, Dict, Optional

import pygame

from ..audio.audio_manager import AudioManager
from ..core.ecs import World
from ..core.state import StateManager
from ..engine.ui.event_editor_ui import EventEditorUI
from ..input.input_manager import InputManager
from .asset_browser_ui import AssetBrowserUI
from .autotile_editor_ui import AutotileEditorUI
from .building_ui import BuildingUI
from .combat_ui import CombatUI
from .debug_console_ui import DebugConsoleUI
from .game_hud import GameHUD
from .level_builder_ui import LevelBuilderUI
from .navmesh_editor_ui import NavmeshEditorUI
from .project_manager_ui import ProjectManagerUI
from .quest_editor_ui import QuestEditorUI
from .settings_ui import SettingsUI


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
    ):
        self.screen = screen
        self.world = world
        self.state_manager = state_manager
        self.audio_manager = audio_manager
        self.input_manager = input_manager

        # Initialize all UI systems
        self.game_hud = GameHUD(screen)
        self.building_ui = BuildingUI(screen, world)
        self.combat_ui = CombatUI(screen, world)
        self.navmesh_editor = NavmeshEditorUI(screen, world)
        self.level_builder = LevelBuilderUI(screen, world)
        self.event_editor = EventEditorUI(screen)
        self.settings_ui = SettingsUI(screen, audio_manager, input_manager)
        self.project_manager = ProjectManagerUI(screen, state_manager)
        self.debug_console = DebugConsoleUI(screen, world)
        self.quest_editor = QuestEditorUI(screen)
        self.asset_browser = AssetBrowserUI(screen)
        self.autotile_editor = AutotileEditorUI(screen)

        # Connect level builder to event editor for event management
        self.level_builder.event_editor = self.event_editor

        # UI state
        self.current_mode = "game"  # 'game', 'editor', 'menu'

        # Key bindings
        self.keybinds = {
            pygame.K_F1: self.toggle_debug_console,
            pygame.K_F2: self.toggle_settings,
            pygame.K_F3: self.toggle_building_ui,
            pygame.K_F4: self.toggle_level_builder,
            pygame.K_F5: self.toggle_event_editor,
            pygame.K_F6: self.toggle_quest_editor,
            pygame.K_F7: self.toggle_asset_browser,
            pygame.K_F8: self.toggle_project_manager,
            pygame.K_F9: self.toggle_combat_ui,
            pygame.K_F10: self.toggle_game_hud,
            pygame.K_F11: self.toggle_autotile_editor,
            pygame.K_F12: self.toggle_navmesh_editor,
        }

    def render(self, fps: float = 60.0, camera_offset: tuple = (0, 0)):
        """
        Render all active UI systems.
        """
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
            self.event_editor.render()

        # Render asset browser if visible
        if self.asset_browser.visible:
            self.asset_browser.render()

        # Render project manager if visible
        if self.project_manager.visible:
            self.project_manager.render()

        # Render settings if visible
        if self.settings_ui.visible:
            self.settings_ui.render()

        # Render autotile editor if visible
        if self.autotile_editor.visible:
            self.autotile_editor.render(self.screen)

        # Always render debug console last (on top of everything)
        if self.debug_console.visible:
            self.debug_console.render(fps)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events and route them to appropriate UI systems.
        Returns True if event was handled by UI.
        """
        # Handle key presses
        if event.type == pygame.KEYDOWN:
            # Check for keybinds
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

        # Route events to autotile editor if visible
        if self.autotile_editor.visible:
            self.autotile_editor.handle_event(event)
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

        return False

    def update(self, dt: float, mouse_pos: tuple, camera_offset: tuple):
        """
        Update UI systems that need per-frame updates.
        """
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

    def toggle_quest_editor(self):
        """Toggle quest editor."""
        self.quest_editor.toggle()

    def toggle_event_editor(self):
        """Toggle event editor."""
        self.event_editor.toggle()

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
        """
        help_text = "UI Keybinds:\n"
        help_text += "F1 - Debug Console\n"
        help_text += "F2 - Settings\n"
        help_text += "F3 - Building UI\n"
        help_text += "F4 - Level Builder\n"
        help_text += "F5 - Event Editor\n"
        help_text += "F6 - Quest Editor\n"
        help_text += "F7 - Asset Browser\n"
        help_text += "F8 - Project Manager\n"
        help_text += "F9 - Combat UI\n"
        help_text += "F10 - Toggle HUD\n"
        help_text += "F11 - Autotile Editor\n"
        help_text += "F12 - Navmesh Editor\n"
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
