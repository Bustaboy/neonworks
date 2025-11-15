"""
Layer Panel UI - Enhanced Layer Management Interface

Provides visual interface for managing the enhanced layer system:
- Layer list with hierarchy
- Add/remove/reorder layers
- Layer properties (opacity, visibility, locked)
- Layer groups/folders
- Parallax configuration
- Layer merging
"""

from typing import Callable, List, Optional, Tuple

import pygame

from neonworks.data.map_layers import LayerGroup, LayerManager, LayerProperties, LayerType
from neonworks.rendering.tilemap import Tilemap


class LayerPanelUI:
    """
    Visual panel for managing enhanced layers.

    Features:
    - Hierarchical layer tree view
    - Drag-and-drop reordering
    - Context menus for layer operations
    - Property editing
    - Group management
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int = 250,
        height: int = 400,
        on_layer_selected: Optional[Callable[[str], None]] = None,
    ):
        """
        Initialize layer panel.

        Args:
            x: Panel X position
            y: Panel Y position
            width: Panel width
            height: Panel height
            on_layer_selected: Callback when layer is selected
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True

        # Callbacks
        self.on_layer_selected = on_layer_selected

        # State
        self.tilemap: Optional[Tilemap] = None
        self.selected_layer_id: Optional[str] = None
        self.hovered_layer_id: Optional[str] = None
        self.dragging_layer_id: Optional[str] = None

        # UI state
        self.scroll_offset = 0
        self.expanded_groups = set()  # Group IDs that are expanded
        self.show_context_menu = False
        self.context_menu_pos = (0, 0)
        self.editing_property: Optional[str] = None

        # Colors
        self.bg_color = (40, 40, 45)
        self.header_color = (50, 50, 55)
        self.layer_color = (60, 60, 65)
        self.layer_hover_color = (70, 70, 75)
        self.layer_selected_color = (80, 120, 160)
        self.group_color = (55, 55, 60)
        self.text_color = (220, 220, 220)
        self.text_dim_color = (150, 150, 150)
        self.border_color = (80, 80, 85)

        # Fonts
        self.font = pygame.font.Font(None, 18)
        self.small_font = pygame.font.Font(None, 14)

        # Layout
        self.header_height = 30
        self.layer_height = 24
        self.indent_width = 20
        self.button_size = 20

    def set_tilemap(self, tilemap: Tilemap):
        """Set the tilemap to manage"""
        self.tilemap = tilemap
        self.selected_layer_id = None

    def update(self, dt: float):
        """Update panel state"""
        pass

    def render(self, screen: pygame.Surface):
        """Render the layer panel"""
        if not self.visible or not self.tilemap:
            return

        if not self.tilemap.use_enhanced_layers:
            self._render_legacy_warning(screen)
            return

        # Draw background
        pygame.draw.rect(screen, self.bg_color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, self.border_color, (self.x, self.y, self.width, self.height), 2)

        # Draw header
        self._render_header(screen)

        # Draw layer list
        self._render_layer_list(screen)

        # Draw context menu if open
        if self.show_context_menu:
            self._render_context_menu(screen)

    def _render_legacy_warning(self, screen: pygame.Surface):
        """Render warning when using legacy layer system"""
        pygame.draw.rect(screen, self.bg_color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, self.border_color, (self.x, self.y, self.width, self.height), 2)

        text = self.font.render("Enhanced Layers", True, self.text_color)
        screen.blit(text, (self.x + 10, self.y + 10))

        warning = self.small_font.render("Legacy mode active", True, (255, 150, 0))
        screen.blit(warning, (self.x + 10, self.y + 40))

        help_text = [
            "This tilemap uses the",
            "old 3-layer system.",
            "",
            "To use enhanced layers,",
            "create a new tilemap with",
            "use_enhanced_layers=True",
        ]

        y_pos = self.y + 70
        for line in help_text:
            text = self.small_font.render(line, True, self.text_dim_color)
            screen.blit(text, (self.x + 10, y_pos))
            y_pos += 18

    def _render_header(self, screen: pygame.Surface):
        """Render panel header with controls"""
        header_rect = pygame.Rect(self.x, self.y, self.width, self.header_height)
        pygame.draw.rect(screen, self.header_color, header_rect)

        # Title
        title = self.font.render("Layers", True, self.text_color)
        screen.blit(title, (self.x + 10, self.y + 6))

        # Add layer button
        add_button_x = self.x + self.width - 90
        add_rect = pygame.Rect(add_button_x, self.y + 5, 40, 20)
        pygame.draw.rect(screen, self.layer_color, add_rect)
        pygame.draw.rect(screen, self.border_color, add_rect, 1)
        add_text = self.small_font.render("+ Layer", True, self.text_color)
        screen.blit(add_text, (add_button_x + 4, self.y + 8))
        self.add_layer_button = add_rect

        # Add group button
        group_button_x = self.x + self.width - 45
        group_rect = pygame.Rect(group_button_x, self.y + 5, 40, 20)
        pygame.draw.rect(screen, self.layer_color, group_rect)
        pygame.draw.rect(screen, self.border_color, group_rect, 1)
        group_text = self.small_font.render("+ Group", True, self.text_color)
        screen.blit(group_text, (group_button_x + 2, self.y + 8))
        self.add_group_button = group_rect

    def _render_layer_list(self, screen: pygame.Surface):
        """Render hierarchical layer list"""
        list_y = self.y + self.header_height
        list_height = self.height - self.header_height

        # Clip to list area
        clip_rect = pygame.Rect(self.x, list_y, self.width, list_height)
        screen.set_clip(clip_rect)

        y_pos = list_y - self.scroll_offset

        # Render layers in reverse order (top layer first in list)
        root_ids = list(reversed(self.tilemap.layer_manager.root_ids))

        for item_id in root_ids:
            y_pos = self._render_layer_or_group(screen, item_id, y_pos, 0)

        screen.set_clip(None)

    def _render_layer_or_group(
        self, screen: pygame.Surface, item_id: str, y_pos: int, indent_level: int
    ) -> int:
        """
        Render a layer or group at the given position.

        Returns the new y position after rendering.
        """
        manager = self.tilemap.layer_manager

        # Check if it's a group
        if item_id in manager.groups:
            return self._render_group(screen, item_id, y_pos, indent_level)
        elif item_id in manager.layers:
            return self._render_layer(screen, item_id, y_pos, indent_level)

        return y_pos

    def _render_group(
        self, screen: pygame.Surface, group_id: str, y_pos: int, indent_level: int
    ) -> int:
        """Render a layer group"""
        group = self.tilemap.layer_manager.get_group(group_id)
        if not group:
            return y_pos

        is_expanded = group_id in self.expanded_groups
        is_hovered = group_id == self.hovered_layer_id

        # Background
        item_rect = pygame.Rect(
            self.x + indent_level * self.indent_width,
            y_pos,
            self.width - indent_level * self.indent_width,
            self.layer_height,
        )

        color = self.group_color
        if is_hovered:
            color = self.layer_hover_color

        pygame.draw.rect(screen, color, item_rect)

        # Expansion triangle
        triangle_x = self.x + indent_level * self.indent_width + 5
        triangle_y = y_pos + self.layer_height // 2
        triangle_size = 6

        if is_expanded:
            # Down arrow
            points = [
                (triangle_x, triangle_y - 3),
                (triangle_x + triangle_size, triangle_y - 3),
                (triangle_x + triangle_size // 2, triangle_y + 3),
            ]
        else:
            # Right arrow
            points = [
                (triangle_x, triangle_y - 3),
                (triangle_x + 6, triangle_y),
                (triangle_x, triangle_y + 3),
            ]

        pygame.draw.polygon(screen, self.text_color, points)

        # Group name
        name_x = triangle_x + 12
        name_text = self.font.render(f"📁 {group.name}", True, self.text_color)
        screen.blit(name_text, (name_x, y_pos + 4))

        # Visibility toggle
        vis_x = self.x + self.width - 25
        vis_icon = "👁" if group.visible else "⚫"
        vis_text = self.small_font.render(vis_icon, True, self.text_color)
        screen.blit(vis_text, (vis_x, y_pos + 4))

        y_pos += self.layer_height

        # Render children if expanded
        if is_expanded:
            # Render in reverse order (top child first)
            for child_id in reversed(group.child_ids):
                y_pos = self._render_layer_or_group(screen, child_id, y_pos, indent_level + 1)

        return y_pos

    def _render_layer(
        self, screen: pygame.Surface, layer_id: str, y_pos: int, indent_level: int
    ) -> int:
        """Render a single layer"""
        layer = self.tilemap.layer_manager.get_layer(layer_id)
        if not layer:
            return y_pos

        is_selected = layer_id == self.selected_layer_id
        is_hovered = layer_id == self.hovered_layer_id

        # Background
        item_rect = pygame.Rect(
            self.x + indent_level * self.indent_width,
            y_pos,
            self.width - indent_level * self.indent_width,
            self.layer_height,
        )

        color = self.layer_color
        if is_selected:
            color = self.layer_selected_color
        elif is_hovered:
            color = self.layer_hover_color

        pygame.draw.rect(screen, color, item_rect)

        # Layer icon based on type
        icon_x = self.x + indent_level * self.indent_width + 8
        icon = self._get_layer_icon(layer.properties.layer_type)
        icon_text = self.small_font.render(icon, True, self.text_color)
        screen.blit(icon_text, (icon_x, y_pos + 4))

        # Layer name
        name_x = icon_x + 18
        text_color = self.text_color if layer.properties.visible else self.text_dim_color
        name_text = self.font.render(layer.properties.name, True, text_color)
        screen.blit(name_text, (name_x, y_pos + 4))

        # Locked icon
        if layer.properties.locked:
            lock_x = self.x + self.width - 45
            lock_text = self.small_font.render("🔒", True, self.text_color)
            screen.blit(lock_text, (lock_x, y_pos + 4))

        # Visibility toggle
        vis_x = self.x + self.width - 25
        vis_icon = "👁" if layer.properties.visible else "⚫"
        vis_text = self.small_font.render(vis_icon, True, self.text_color)
        screen.blit(vis_text, (vis_x, y_pos + 4))

        # Opacity indicator (if not fully opaque)
        if layer.properties.opacity < 1.0:
            opacity_x = name_x + name_text.get_width() + 5
            opacity_pct = int(layer.properties.opacity * 100)
            opacity_text = self.small_font.render(f"{opacity_pct}%", True, self.text_dim_color)
            screen.blit(opacity_text, (opacity_x, y_pos + 6))

        return y_pos + self.layer_height

    def _get_layer_icon(self, layer_type: LayerType) -> str:
        """Get icon for layer type"""
        icons = {
            LayerType.STANDARD: "📄",
            LayerType.PARALLAX_BACKGROUND: "🌄",
            LayerType.PARALLAX_FOREGROUND: "🎬",
            LayerType.COLLISION: "⚠️",
            LayerType.OVERLAY: "🎨",
        }
        return icons.get(layer_type, "📄")

    def _render_context_menu(self, screen: pygame.Surface):
        """Render right-click context menu"""
        menu_width = 150
        menu_items = [
            "Duplicate",
            "Delete",
            "---",
            "Move Up",
            "Move Down",
            "---",
            "Properties",
        ]

        menu_height = len(menu_items) * 22 + 10
        menu_x, menu_y = self.context_menu_pos

        # Background
        pygame.draw.rect(screen, self.bg_color, (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(screen, self.border_color, (menu_x, menu_y, menu_width, menu_height), 2)

        # Menu items
        y_pos = menu_y + 5
        for item in menu_items:
            if item == "---":
                # Separator
                pygame.draw.line(
                    screen,
                    self.border_color,
                    (menu_x + 5, y_pos + 10),
                    (menu_x + menu_width - 5, y_pos + 10),
                )
                y_pos += 22
                continue

            # Menu item
            mouse_pos = pygame.mouse.get_pos()
            item_rect = pygame.Rect(menu_x + 5, y_pos, menu_width - 10, 20)

            if item_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, self.layer_hover_color, item_rect)

            text = self.small_font.render(item, True, self.text_color)
            screen.blit(text, (menu_x + 10, y_pos + 3))

            y_pos += 22

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle input events.

        Returns True if event was consumed.
        """
        if not self.visible or not self.tilemap:
            return False

        if not self.tilemap.use_enhanced_layers:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            return self._handle_mouse_down(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            return self._handle_mouse_up(event)
        elif event.type == pygame.MOUSEMOTION:
            return self._handle_mouse_motion(event)
        elif event.type == pygame.MOUSEWHEEL:
            return self._handle_mouse_wheel(event)

        return False

    def _handle_mouse_down(self, event: pygame.event.Event) -> bool:
        """Handle mouse button down"""
        mouse_pos = event.pos

        # Check if click is in panel
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        if not panel_rect.collidepoint(mouse_pos):
            return False

        # Check header buttons
        if hasattr(self, "add_layer_button") and self.add_layer_button.collidepoint(mouse_pos):
            self._add_new_layer()
            return True

        if hasattr(self, "add_group_button") and self.add_group_button.collidepoint(mouse_pos):
            self._add_new_group()
            return True

        # Check layer list clicks
        if event.button == 1:  # Left click
            clicked_id = self._get_item_at_pos(mouse_pos)
            if clicked_id:
                # Check if clicked on visibility toggle
                if self._is_click_on_visibility(mouse_pos, clicked_id):
                    self._toggle_visibility(clicked_id)
                    return True

                # Check if clicked on group expansion
                if clicked_id in self.tilemap.layer_manager.groups:
                    if self._is_click_on_expansion(mouse_pos, clicked_id):
                        self._toggle_group_expansion(clicked_id)
                        return True

                # Select layer/group
                self.selected_layer_id = clicked_id
                if self.on_layer_selected and clicked_id in self.tilemap.layer_manager.layers:
                    self.on_layer_selected(clicked_id)
                return True

        elif event.button == 3:  # Right click
            clicked_id = self._get_item_at_pos(mouse_pos)
            if clicked_id:
                self.selected_layer_id = clicked_id
                self.show_context_menu = True
                self.context_menu_pos = mouse_pos
                return True

        return True  # Consume event even if not handled

    def _handle_mouse_up(self, event: pygame.event.Event) -> bool:
        """Handle mouse button up"""
        if self.show_context_menu and event.button == 1:
            # Handle context menu click
            if self._handle_context_menu_click(event.pos):
                self.show_context_menu = False
                return True
            self.show_context_menu = False

        return False

    def _handle_mouse_motion(self, event: pygame.event.Event) -> bool:
        """Handle mouse motion"""
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        if panel_rect.collidepoint(event.pos):
            self.hovered_layer_id = self._get_item_at_pos(event.pos)
            return True

        self.hovered_layer_id = None
        return False

    def _handle_mouse_wheel(self, event: pygame.event.Event) -> bool:
        """Handle mouse wheel scroll"""
        mouse_pos = pygame.mouse.get_pos()
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)

        if panel_rect.collidepoint(mouse_pos):
            self.scroll_offset -= event.y * 20
            self.scroll_offset = max(0, self.scroll_offset)
            return True

        return False

    def _get_item_at_pos(self, pos: Tuple[int, int]) -> Optional[str]:
        """Get layer/group ID at mouse position"""
        # TODO: Implement hit testing based on rendered positions
        # For now, simplified version
        return None

    def _is_click_on_visibility(self, pos: Tuple[int, int], item_id: str) -> bool:
        """Check if click was on visibility toggle"""
        # TODO: Implement based on rendered positions
        return False

    def _is_click_on_expansion(self, pos: Tuple[int, int], group_id: str) -> bool:
        """Check if click was on group expansion triangle"""
        # TODO: Implement based on rendered positions
        return False

    def _handle_context_menu_click(self, pos: Tuple[int, int]) -> bool:
        """Handle click on context menu item"""
        # TODO: Implement menu item detection and actions
        return False

    def _toggle_visibility(self, item_id: str):
        """Toggle visibility of layer or group"""
        manager = self.tilemap.layer_manager

        if item_id in manager.layers:
            layer = manager.get_layer(item_id)
            layer.properties.visible = not layer.properties.visible
        elif item_id in manager.groups:
            group = manager.get_group(item_id)
            group.visible = not group.visible

    def _toggle_group_expansion(self, group_id: str):
        """Toggle group expanded/collapsed state"""
        if group_id in self.expanded_groups:
            self.expanded_groups.remove(group_id)
        else:
            self.expanded_groups.add(group_id)

    def _add_new_layer(self):
        """Add a new layer"""
        if not self.tilemap:
            return

        layer_count = len(self.tilemap.layer_manager.layers)
        layer_id = self.tilemap.create_enhanced_layer(f"Layer {layer_count + 1}")

        if layer_id:
            self.selected_layer_id = layer_id
            if self.on_layer_selected:
                self.on_layer_selected(layer_id)

    def _add_new_group(self):
        """Add a new group"""
        if not self.tilemap:
            return

        group_count = len(self.tilemap.layer_manager.groups)
        group_id = self.tilemap.create_layer_group(f"Group {group_count + 1}")

        if group_id:
            self.expanded_groups.add(group_id)

    def toggle_visibility(self):
        """Toggle panel visibility"""
        self.visible = not self.visible
