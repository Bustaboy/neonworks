"""
Workspace Toolbar UI Component

Visual toolbar for workspace switching and tool access.
Provides the main navigation interface for the NeonWorks editor.
"""

from typing import Callable, Dict, Optional, Tuple

import pygame

from .workspace_system import (
    ToolDefinition,
    Workspace,
    WorkspaceManager,
    WorkspaceType,
    get_workspace_manager,
)


class WorkspaceToolbar:
    """
    Visual workspace toolbar with tabs and tool buttons.

    Renders at the top of the screen with:
    - Workspace tabs (Play, Level Editor, Content Creation, Settings)
    - Tool buttons for active workspace
    - Visual feedback for active workspace and tools
    """

    def __init__(self, screen: pygame.Surface, master_ui_manager=None):
        """
        Initialize workspace toolbar.

        Args:
            screen: Pygame surface to render to
            master_ui_manager: Reference to MasterUIManager for tool toggling
        """
        self.screen = screen
        self.master_ui_manager = master_ui_manager
        self.workspace_manager = get_workspace_manager()

        # UI State
        self.visible = True
        self.collapsed = False
        self.height = 120  # Full height (tabs + tools)
        self.collapsed_height = 40  # Just tabs

        # Styling
        self.bg_color = (25, 25, 35, 240)
        self.tab_bg_color = (40, 40, 50)
        self.tab_active_color = (60, 60, 80)
        self.tab_hover_color = (50, 50, 65)
        self.tool_bg_color = (45, 45, 60)
        self.tool_hover_color = (65, 65, 85)
        self.tool_active_color = (80, 120, 180)
        self.text_color = (220, 220, 220)
        self.text_active_color = (255, 255, 255)

        # Layout
        self.tab_height = 40
        self.tool_height = 80
        self.padding = 10
        self.tab_padding = 5

        # Fonts
        try:
            self.tab_font = pygame.font.Font(None, 24)
            self.tool_font = pygame.font.Font(None, 18)
            self.icon_font = pygame.font.Font(None, 36)
        except:
            self.tab_font = pygame.font.SysFont("Arial", 24)
            self.tool_font = pygame.font.SysFont("Arial", 18)
            self.icon_font = pygame.font.SysFont("Arial", 36)

        # Interaction state
        self.hovered_tab: Optional[WorkspaceType] = None
        self.hovered_tool: Optional[str] = None

        # Initialize to Play workspace
        if self.workspace_manager.current_workspace is None:
            self.workspace_manager.set_workspace(WorkspaceType.PLAY)

    def toggle_collapse(self):
        """Toggle collapsed state"""
        self.collapsed = not self.collapsed

    def get_height(self) -> int:
        """Get current toolbar height"""
        if not self.visible:
            return 0
        return self.collapsed_height if self.collapsed else self.height

    def render(self):
        """Render the workspace toolbar"""
        if not self.visible:
            return

        screen_width = self.screen.get_width()
        current_height = self.get_height()

        # Background panel
        toolbar_surface = pygame.Surface((screen_width, current_height), pygame.SRCALPHA)
        toolbar_surface.fill(self.bg_color)
        self.screen.blit(toolbar_surface, (0, 0))

        # Render workspace tabs
        self._render_workspace_tabs(screen_width)

        # Render tool buttons if not collapsed
        if not self.collapsed:
            self._render_tool_buttons(screen_width)

        # Render collapse toggle
        self._render_collapse_toggle(screen_width)

    def _render_workspace_tabs(self, screen_width: int):
        """Render workspace selection tabs"""
        workspaces = self.workspace_manager.get_all_workspaces()
        current_workspace = self.workspace_manager.get_current_workspace()

        tab_width = min(200, (screen_width - self.padding * 2) // len(workspaces))
        x = self.padding

        for workspace in workspaces:
            is_active = current_workspace and workspace.type == current_workspace.type
            is_hovered = self.hovered_tab == workspace.type

            # Determine tab color
            if is_active:
                bg_color = self.tab_active_color
                text_color = self.text_active_color
            elif is_hovered:
                bg_color = self.tab_hover_color
                text_color = self.text_color
            else:
                bg_color = self.tab_bg_color
                text_color = self.text_color

            # Draw tab background
            tab_rect = pygame.Rect(x, self.tab_padding, tab_width - 10, self.tab_height - 10)
            pygame.draw.rect(self.screen, bg_color, tab_rect, border_radius=5)

            # Active tab indicator (bottom border)
            if is_active:
                indicator_rect = pygame.Rect(x, tab_rect.bottom - 3, tab_width - 10, 3)
                pygame.draw.rect(self.screen, self.tool_active_color, indicator_rect)

            # Draw icon and text
            icon_text = self.icon_font.render(workspace.icon, True, text_color)
            name_text = self.tab_font.render(workspace.name, True, text_color)

            # Center icon and text
            icon_x = x + (tab_width - icon_text.get_width()) // 2
            text_x = x + (tab_width - name_text.get_width()) // 2

            self.screen.blit(icon_text, (icon_x - 15, tab_rect.y + 2))
            self.screen.blit(name_text, (text_x + 15, tab_rect.y + 8))

            x += tab_width

    def _render_tool_buttons(self, screen_width: int):
        """Render tool buttons for current workspace"""
        current_workspace = self.workspace_manager.get_current_workspace()
        if not current_workspace:
            return

        tools = current_workspace.tools
        if not tools:
            return

        # Calculate button layout
        button_width = 140
        button_height = 65
        button_spacing = 10
        y = self.tab_height + 5

        x = self.padding
        for tool in tools:
            is_hovered = self.hovered_tool == tool.id

            # Check if tool is currently active (UI is visible)
            is_active = self._is_tool_active(tool)

            # Determine button color
            if is_active:
                bg_color = self.tool_active_color
                text_color = self.text_active_color
            elif is_hovered:
                bg_color = self.tool_hover_color
                text_color = self.text_active_color
            else:
                bg_color = self.tool_bg_color
                text_color = self.text_color

            # Draw button background
            button_rect = pygame.Rect(x, y, button_width, button_height)
            pygame.draw.rect(self.screen, bg_color, button_rect, border_radius=5)

            # Draw icon
            icon_text = self.icon_font.render(tool.icon, True, text_color)
            icon_x = x + (button_width - icon_text.get_width()) // 2
            self.screen.blit(icon_text, (icon_x, y + 5))

            # Draw tool name
            name_text = self.tool_font.render(tool.name, True, text_color)
            name_x = x + (button_width - name_text.get_width()) // 2
            self.screen.blit(name_text, (name_x, y + 40))

            # Draw hotkey hint if available
            if tool.hotkey:
                hotkey_font = pygame.font.Font(None, 14)
                hotkey_text = hotkey_font.render(tool.hotkey, True, (150, 150, 150))
                hotkey_x = x + (button_width - hotkey_text.get_width()) // 2
                self.screen.blit(hotkey_text, (hotkey_x, y + button_height - 15))

            x += button_width + button_spacing

            # Wrap to next row if needed
            if x + button_width > screen_width - self.padding:
                x = self.padding
                y += button_height + button_spacing

    def _render_collapse_toggle(self, screen_width: int):
        """Render collapse/expand toggle button"""
        toggle_size = 30
        toggle_x = screen_width - toggle_size - 10
        toggle_y = 5

        toggle_rect = pygame.Rect(toggle_x, toggle_y, toggle_size, toggle_size)
        pygame.draw.rect(self.screen, self.tool_bg_color, toggle_rect, border_radius=3)

        # Draw arrow
        arrow = "▲" if not self.collapsed else "▼"
        arrow_text = self.tool_font.render(arrow, True, self.text_color)
        arrow_x = toggle_x + (toggle_size - arrow_text.get_width()) // 2
        arrow_y = toggle_y + (toggle_size - arrow_text.get_height()) // 2
        self.screen.blit(arrow_text, (arrow_x, arrow_y))

    def _is_tool_active(self, tool: ToolDefinition) -> bool:
        """Check if a tool's UI is currently visible"""
        if not self.master_ui_manager:
            return False

        # Map tool IDs to UI visibility properties
        ui_map = {
            "game_hud": "game_hud",
            "combat_ui": "combat_ui",
            "building_ui": "building_ui",
            "level_builder": "level_builder",
            "autotile_editor": "autotile_editor",
            "navmesh_editor": "navmesh_editor",
            "event_editor": "event_editor",
            "asset_browser": "asset_browser",
            "ai_animator": "ai_animator",
            "quest_editor": "quest_editor",
            "settings": "settings_ui",
            "debug_console": "debug_console",
            "project_manager": "project_manager",
        }

        ui_name = ui_map.get(tool.id)
        if not ui_name:
            return False

        ui_obj = getattr(self.master_ui_manager, ui_name, None)
        if ui_obj:
            return getattr(ui_obj, "visible", False)

        return False

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle input events.

        Returns:
            True if event was handled
        """
        if not self.visible:
            return False

        if event.type == pygame.MOUSEMOTION:
            self._update_hover_state(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                return self._handle_click(event.pos)

        return False

    def _update_hover_state(self, mouse_pos: Tuple[int, int]):
        """Update hover state based on mouse position"""
        mx, my = mouse_pos

        # Check workspace tabs
        if my < self.tab_height:
            workspaces = self.workspace_manager.get_all_workspaces()
            screen_width = self.screen.get_width()
            tab_width = min(200, (screen_width - self.padding * 2) // len(workspaces))

            self.hovered_tab = None
            x = self.padding
            for workspace in workspaces:
                if x <= mx < x + tab_width - 10:
                    self.hovered_tab = workspace.type
                    break
                x += tab_width
        else:
            self.hovered_tab = None

        # Check tool buttons
        if not self.collapsed and my > self.tab_height:
            current_workspace = self.workspace_manager.get_current_workspace()
            if current_workspace:
                button_width = 140
                button_height = 65
                button_spacing = 10
                y = self.tab_height + 5

                self.hovered_tool = None
                x = self.padding
                for tool in current_workspace.tools:
                    button_rect = pygame.Rect(x, y, button_width, button_height)
                    if button_rect.collidepoint(mx, my):
                        self.hovered_tool = tool.id
                        break

                    x += button_width + button_spacing
                    if x + button_width > self.screen.get_width() - self.padding:
                        x = self.padding
                        y += button_height + button_spacing
        else:
            self.hovered_tool = None

    def _handle_click(self, mouse_pos: Tuple[int, int]) -> bool:
        """Handle mouse click"""
        mx, my = mouse_pos

        # Check collapse toggle
        toggle_size = 30
        toggle_x = self.screen.get_width() - toggle_size - 10
        toggle_y = 5
        toggle_rect = pygame.Rect(toggle_x, toggle_y, toggle_size, toggle_size)
        if toggle_rect.collidepoint(mx, my):
            self.toggle_collapse()
            return True

        # Check workspace tabs
        if self.hovered_tab:
            self.workspace_manager.set_workspace(self.hovered_tab)
            return True

        # Check tool buttons
        if self.hovered_tool and self.master_ui_manager:
            # Find the tool and call its toggle method
            current_workspace = self.workspace_manager.get_current_workspace()
            if current_workspace:
                tool = current_workspace.get_tool(self.hovered_tool)
                if tool and tool.toggle_method:
                    toggle_fn = getattr(self.master_ui_manager, tool.toggle_method, None)
                    if toggle_fn:
                        toggle_fn()

                        # Update AI context with active tools
                        self._update_ai_context()
                        return True

        return False

    def _update_ai_context(self):
        """Update AI context with currently visible UIs"""
        if not self.master_ui_manager:
            return

        visible_uis = []
        active_tools = []

        # Check all UIs
        ui_components = [
            ("game_hud", "game_hud"),
            ("combat_ui", "combat_ui"),
            ("building_ui", "building_ui"),
            ("level_builder", "level_builder"),
            ("autotile_editor", "autotile_editor"),
            ("navmesh_editor", "navmesh_editor"),
            ("event_editor", "event_editor"),
            ("asset_browser", "asset_browser"),
            ("ai_animator", "ai_animator"),
            ("quest_editor", "quest_editor"),
            ("settings_ui", "settings"),
            ("debug_console", "debug_console"),
            ("project_manager", "project_manager"),
        ]

        for ui_attr, tool_id in ui_components:
            ui_obj = getattr(self.master_ui_manager, ui_attr, None)
            if ui_obj and getattr(ui_obj, "visible", False):
                visible_uis.append(ui_attr)
                active_tools.append(tool_id)

        # Update workspace manager context
        self.workspace_manager.update_context(
            active_tools=active_tools,
            visible_uis=visible_uis,
        )
