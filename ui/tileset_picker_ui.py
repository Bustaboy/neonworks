"""
Visual tileset picker UI component for NeonWorks engine.

Provides a visual interface for selecting tiles from loaded tilesets with:
- Grid view of tileset tiles
- Tabs for multiple tilesets
- Recently used tiles section
- Favorites section
- Tile metadata display (passability, terrain tags)
- Search and filter capabilities

Author: NeonWorks Team
Version: 0.1.0
"""

from __future__ import annotations

from typing import Callable, Optional, Tuple

import pygame

from neonworks.data.tileset_manager import TilesetManager, TilesetInfo


class TilesetPickerUI:
    """
    Visual tileset picker UI component.

    Displays tilesets in a scrollable grid with tabs, recently used,
    and favorites sections.
    """

    # UI Colors
    BG_COLOR = (40, 40, 45)
    PANEL_BG_COLOR = (50, 50, 55)
    BORDER_COLOR = (70, 70, 75)
    SELECTED_COLOR = (100, 150, 255)
    HOVER_COLOR = (80, 80, 90)
    TEXT_COLOR = (220, 220, 220)
    ACCENT_COLOR = (100, 150, 255)
    FAVORITE_COLOR = (255, 215, 0)
    TAB_ACTIVE_COLOR = (70, 70, 80)
    TAB_INACTIVE_COLOR = (50, 50, 55)

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        tileset_manager: TilesetManager,
        on_tile_selected: Optional[Callable[[str, int], None]] = None,
    ):
        """
        Initialize the tileset picker UI.

        Args:
            x: X position
            y: Y position
            width: Width of the picker
            height: Height of the picker
            tileset_manager: TilesetManager instance
            on_tile_selected: Callback when tile is selected (tileset_id, tile_id)
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.tileset_manager = tileset_manager
        self.on_tile_selected = on_tile_selected

        # UI State
        self.visible = True
        self.active_tab = "tileset"  # tileset, recent, favorites
        self.selected_tileset_id: Optional[str] = None
        self.selected_tile_id: Optional[int] = None
        self.hover_tile_id: Optional[int] = None
        self.scroll_offset = 0
        self.max_scroll = 0

        # Layout
        self.tab_height = 30
        self.tile_padding = 2
        self.tiles_per_row = 8
        self.tile_display_size = (self.width - 20) // self.tiles_per_row - self.tile_padding * 2

        # Font
        pygame.font.init()
        self.font = pygame.font.Font(None, 20)
        self.small_font = pygame.font.Font(None, 16)

        # Cache
        self.tile_positions = {}  # (tileset_id, tile_id) -> (x, y, w, h)

    def update(self, dt: float):
        """
        Update picker state.

        Args:
            dt: Delta time in seconds
        """
        if not self.visible:
            return

        # Update max scroll based on content
        self._calculate_scroll_bounds()

    def render(self, screen: pygame.Surface):
        """
        Render the tileset picker.

        Args:
            screen: Pygame surface to render on
        """
        if not self.visible:
            return

        # Draw background panel
        pygame.draw.rect(screen, self.PANEL_BG_COLOR, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, self.BORDER_COLOR, (self.x, self.y, self.width, self.height), 2)

        # Draw tabs
        self._render_tabs(screen)

        # Draw content based on active tab
        content_y = self.y + self.tab_height + 5
        content_height = self.height - self.tab_height - 10

        if self.active_tab == "tileset":
            self._render_tileset_view(screen, content_y, content_height)
        elif self.active_tab == "recent":
            self._render_recent_view(screen, content_y, content_height)
        elif self.active_tab == "favorites":
            self._render_favorites_view(screen, content_y, content_height)

        # Draw metadata panel at bottom
        self._render_metadata_panel(screen)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle input events.

        Args:
            event: Pygame event

        Returns:
            True if event was handled, False otherwise
        """
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            # Check tab clicks
            if self._handle_tab_click(mouse_pos):
                return True

            # Check tile clicks
            if event.button == 1:  # Left click
                if self._handle_tile_click(mouse_pos):
                    return True
            elif event.button == 3:  # Right click (favorite toggle)
                if self._handle_favorite_toggle(mouse_pos):
                    return True

        elif event.type == pygame.MOUSEMOTION:
            self._update_hover(event.pos)

        elif event.type == pygame.MOUSEWHEEL:
            # Scroll the tileset view
            self.scroll_offset -= event.y * 30
            self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))
            return True

        return False

    def _render_tabs(self, screen: pygame.Surface):
        """Render tab buttons."""
        tabs = [
            ("tileset", "Tileset"),
            ("recent", "Recent"),
            ("favorites", "Favorites"),
        ]

        tab_width = self.width // len(tabs)

        for i, (tab_id, tab_name) in enumerate(tabs):
            tab_x = self.x + i * tab_width
            tab_y = self.y
            tab_rect = (tab_x, tab_y, tab_width, self.tab_height)

            # Draw tab background
            color = self.TAB_ACTIVE_COLOR if self.active_tab == tab_id else self.TAB_INACTIVE_COLOR
            pygame.draw.rect(screen, color, tab_rect)
            pygame.draw.rect(screen, self.BORDER_COLOR, tab_rect, 1)

            # Draw tab text
            text = self.font.render(tab_name, True, self.TEXT_COLOR)
            text_rect = text.get_rect(center=(tab_x + tab_width // 2, tab_y + self.tab_height // 2))
            screen.blit(text, text_rect)

    def _render_tileset_view(self, screen: pygame.Surface, content_y: int, content_height: int):
        """Render the main tileset grid view."""
        # Draw tileset selector if multiple tilesets
        if len(self.tileset_manager.tilesets) > 1:
            self._render_tileset_selector(screen, content_y)
            content_y += 35
            content_height -= 35

        # Get active tileset
        active_tileset = self.tileset_manager.get_active_tileset()
        if active_tileset is None:
            self._render_no_tileset_message(screen, content_y, content_height)
            return

        # Ensure tileset is loaded
        if not active_tileset.tiles:
            self.tileset_manager.load_tileset(active_tileset.tileset_id)

        # Render tiles in grid
        self._render_tile_grid(
            screen,
            content_y,
            content_height,
            active_tileset.tileset_id,
            list(active_tileset.tiles.keys()),
        )

    def _render_recent_view(self, screen: pygame.Surface, content_y: int, content_height: int):
        """Render recently used tiles."""
        recent_tiles = self.tileset_manager.get_recent_tiles()

        if not recent_tiles:
            text = self.font.render("No recently used tiles", True, self.TEXT_COLOR)
            text_rect = text.get_rect(
                center=(self.x + self.width // 2, content_y + content_height // 2)
            )
            screen.blit(text, text_rect)
            return

        # Render tiles from all tilesets
        self._render_mixed_tile_grid(screen, content_y, content_height, recent_tiles)

    def _render_favorites_view(self, screen: pygame.Surface, content_y: int, content_height: int):
        """Render favorite tiles."""
        favorite_tiles = self.tileset_manager.get_favorite_tiles()

        if not favorite_tiles:
            text = self.font.render("No favorite tiles", True, self.TEXT_COLOR)
            text_rect = text.get_rect(
                center=(self.x + self.width // 2, content_y + content_height // 2)
            )
            screen.blit(text, text_rect)
            return

        # Render tiles from all tilesets
        self._render_mixed_tile_grid(screen, content_y, content_height, favorite_tiles)

    def _render_tile_grid(
        self,
        screen: pygame.Surface,
        content_y: int,
        content_height: int,
        tileset_id: str,
        tile_ids: list,
    ):
        """Render a grid of tiles from a single tileset."""
        self.tile_positions.clear()

        start_x = self.x + 10
        current_x = start_x
        current_y = content_y - self.scroll_offset

        for i, tile_id in enumerate(tile_ids):
            # Calculate position
            if i > 0 and i % self.tiles_per_row == 0:
                current_x = start_x
                current_y += self.tile_display_size + self.tile_padding * 2

            # Skip if not visible
            if current_y + self.tile_display_size < content_y:
                current_x += self.tile_display_size + self.tile_padding * 2
                continue
            if current_y > content_y + content_height:
                break

            # Get tile surface
            tile_surface = self.tileset_manager.get_tile_surface(tileset_id, tile_id)
            if tile_surface is None:
                current_x += self.tile_display_size + self.tile_padding * 2
                continue

            # Draw tile background
            tile_rect = (
                current_x,
                current_y,
                self.tile_display_size,
                self.tile_display_size,
            )
            self.tile_positions[(tileset_id, tile_id)] = tile_rect

            # Determine background color
            bg_color = self.PANEL_BG_COLOR
            if self.selected_tileset_id == tileset_id and self.selected_tile_id == tile_id:
                bg_color = self.SELECTED_COLOR
            elif self.hover_tile_id == tile_id:
                bg_color = self.HOVER_COLOR

            pygame.draw.rect(screen, bg_color, tile_rect)

            # Scale and draw tile
            scaled_tile = pygame.transform.scale(
                tile_surface, (self.tile_display_size - 4, self.tile_display_size - 4)
            )
            screen.blit(scaled_tile, (current_x + 2, current_y + 2))

            # Draw border
            border_color = (
                self.SELECTED_COLOR
                if self.selected_tileset_id == tileset_id and self.selected_tile_id == tile_id
                else self.BORDER_COLOR
            )
            pygame.draw.rect(screen, border_color, tile_rect, 2)

            # Draw favorite star
            if self.tileset_manager.is_favorite(tileset_id, tile_id):
                pygame.draw.circle(
                    screen,
                    self.FAVORITE_COLOR,
                    (current_x + self.tile_display_size - 8, current_y + 8),
                    4,
                )

            current_x += self.tile_display_size + self.tile_padding * 2

    def _render_mixed_tile_grid(
        self,
        screen: pygame.Surface,
        content_y: int,
        content_height: int,
        tiles: list,
    ):
        """Render a grid of tiles from multiple tilesets."""
        self.tile_positions.clear()

        start_x = self.x + 10
        current_x = start_x
        current_y = content_y - self.scroll_offset

        for i, (tileset_id, tile_id) in enumerate(tiles):
            # Calculate position
            if i > 0 and i % self.tiles_per_row == 0:
                current_x = start_x
                current_y += self.tile_display_size + self.tile_padding * 2

            # Skip if not visible
            if current_y + self.tile_display_size < content_y:
                current_x += self.tile_display_size + self.tile_padding * 2
                continue
            if current_y > content_y + content_height:
                break

            # Get tile surface
            tile_surface = self.tileset_manager.get_tile_surface(tileset_id, tile_id)
            if tile_surface is None:
                current_x += self.tile_display_size + self.tile_padding * 2
                continue

            # Draw tile (same as _render_tile_grid)
            tile_rect = (
                current_x,
                current_y,
                self.tile_display_size,
                self.tile_display_size,
            )
            self.tile_positions[(tileset_id, tile_id)] = tile_rect

            bg_color = self.PANEL_BG_COLOR
            if self.selected_tileset_id == tileset_id and self.selected_tile_id == tile_id:
                bg_color = self.SELECTED_COLOR
            elif self.hover_tile_id == tile_id:
                bg_color = self.HOVER_COLOR

            pygame.draw.rect(screen, bg_color, tile_rect)

            scaled_tile = pygame.transform.scale(
                tile_surface, (self.tile_display_size - 4, self.tile_display_size - 4)
            )
            screen.blit(scaled_tile, (current_x + 2, current_y + 2))

            border_color = (
                self.SELECTED_COLOR
                if self.selected_tileset_id == tileset_id and self.selected_tile_id == tile_id
                else self.BORDER_COLOR
            )
            pygame.draw.rect(screen, border_color, tile_rect, 2)

            if self.tileset_manager.is_favorite(tileset_id, tile_id):
                pygame.draw.circle(
                    screen,
                    self.FAVORITE_COLOR,
                    (current_x + self.tile_display_size - 8, current_y + 8),
                    4,
                )

            current_x += self.tile_display_size + self.tile_padding * 2

    def _render_tileset_selector(self, screen: pygame.Surface, y: int):
        """Render dropdown for selecting active tileset."""
        active_tileset = self.tileset_manager.get_active_tileset()
        text = active_tileset.name if active_tileset else "No tileset selected"

        # Draw selector box
        selector_rect = (self.x + 10, y, self.width - 20, 25)
        pygame.draw.rect(screen, self.PANEL_BG_COLOR, selector_rect)
        pygame.draw.rect(screen, self.BORDER_COLOR, selector_rect, 1)

        # Draw text
        text_surface = self.font.render(text, True, self.TEXT_COLOR)
        screen.blit(text_surface, (self.x + 15, y + 5))

        # Draw dropdown arrow
        arrow_x = self.x + self.width - 25
        arrow_y = y + 12
        pygame.draw.polygon(
            screen,
            self.TEXT_COLOR,
            [(arrow_x, arrow_y - 3), (arrow_x - 5, arrow_y + 3), (arrow_x + 5, arrow_y + 3)],
        )

    def _render_no_tileset_message(
        self, screen: pygame.Surface, content_y: int, content_height: int
    ):
        """Render message when no tileset is available."""
        text1 = self.font.render("No tileset loaded", True, self.TEXT_COLOR)
        text2 = self.small_font.render("Add a tileset to begin", True, self.TEXT_COLOR)

        text1_rect = text1.get_rect(
            center=(self.x + self.width // 2, content_y + content_height // 2 - 15)
        )
        text2_rect = text2.get_rect(
            center=(self.x + self.width // 2, content_y + content_height // 2 + 15)
        )

        screen.blit(text1, text1_rect)
        screen.blit(text2, text2_rect)

    def _render_metadata_panel(self, screen: pygame.Surface):
        """Render tile metadata panel at bottom."""
        if self.selected_tileset_id is None or self.selected_tile_id is None:
            return

        panel_height = 60
        panel_y = self.y + self.height - panel_height
        panel_rect = (self.x, panel_y, self.width, panel_height)

        # Draw panel background
        pygame.draw.rect(screen, self.BG_COLOR, panel_rect)
        pygame.draw.line(
            screen,
            self.BORDER_COLOR,
            (self.x, panel_y),
            (self.x + self.width, panel_y),
            2,
        )

        # Get metadata
        metadata = self.tileset_manager.get_tile_metadata(
            self.selected_tileset_id, self.selected_tile_id
        )
        if metadata is None:
            return

        # Draw metadata text
        y_offset = panel_y + 5

        # Tile ID
        text = self.small_font.render(f"Tile ID: {self.selected_tile_id}", True, self.TEXT_COLOR)
        screen.blit(text, (self.x + 10, y_offset))
        y_offset += 18

        # Passability
        passable_text = "Passable" if metadata.passable else "Blocked"
        passable_color = (100, 255, 100) if metadata.passable else (255, 100, 100)
        text = self.small_font.render(passable_text, True, passable_color)
        screen.blit(text, (self.x + 10, y_offset))

        # Terrain tags
        if metadata.terrain_tags:
            tags_text = ", ".join(metadata.terrain_tags[:3])
            text = self.small_font.render(f"Tags: {tags_text}", True, self.TEXT_COLOR)
            screen.blit(text, (self.x + 100, y_offset))

    def _handle_tab_click(self, mouse_pos: Tuple[int, int]) -> bool:
        """Handle tab button clicks."""
        mx, my = mouse_pos

        if not (self.x <= mx <= self.x + self.width and self.y <= my <= self.y + self.tab_height):
            return False

        tabs = ["tileset", "recent", "favorites"]
        tab_width = self.width // len(tabs)
        tab_index = (mx - self.x) // tab_width

        if 0 <= tab_index < len(tabs):
            self.active_tab = tabs[tab_index]
            self.scroll_offset = 0
            return True

        return False

    def _handle_tile_click(self, mouse_pos: Tuple[int, int]) -> bool:
        """Handle tile selection clicks."""
        for (tileset_id, tile_id), rect in self.tile_positions.items():
            if (
                rect[0] <= mouse_pos[0] <= rect[0] + rect[2]
                and rect[1] <= mouse_pos[1] <= rect[1] + rect[3]
            ):
                self.selected_tileset_id = tileset_id
                self.selected_tile_id = tile_id

                # Add to recent
                self.tileset_manager.add_to_recent(tileset_id, tile_id)

                # Set as active tileset
                self.tileset_manager.set_active_tileset(tileset_id)

                # Call callback
                if self.on_tile_selected:
                    self.on_tile_selected(tileset_id, tile_id)

                return True

        return False

    def _handle_favorite_toggle(self, mouse_pos: Tuple[int, int]) -> bool:
        """Handle right-click to toggle favorite."""
        for (tileset_id, tile_id), rect in self.tile_positions.items():
            if (
                rect[0] <= mouse_pos[0] <= rect[0] + rect[2]
                and rect[1] <= mouse_pos[1] <= rect[1] + rect[3]
            ):
                if self.tileset_manager.is_favorite(tileset_id, tile_id):
                    self.tileset_manager.remove_from_favorites(tileset_id, tile_id)
                else:
                    self.tileset_manager.add_to_favorites(tileset_id, tile_id)
                return True

        return False

    def _update_hover(self, mouse_pos: Tuple[int, int]):
        """Update hover state based on mouse position."""
        self.hover_tile_id = None

        for (tileset_id, tile_id), rect in self.tile_positions.items():
            if (
                rect[0] <= mouse_pos[0] <= rect[0] + rect[2]
                and rect[1] <= mouse_pos[1] <= rect[1] + rect[3]
            ):
                self.hover_tile_id = tile_id
                break

    def _calculate_scroll_bounds(self):
        """Calculate maximum scroll offset based on content."""
        active_tileset = self.tileset_manager.get_active_tileset()
        if active_tileset is None:
            self.max_scroll = 0
            return

        if self.active_tab == "tileset":
            total_tiles = active_tileset.tile_count
        elif self.active_tab == "recent":
            total_tiles = len(self.tileset_manager.get_recent_tiles())
        else:  # favorites
            total_tiles = len(self.tileset_manager.get_favorite_tiles())

        rows = (total_tiles + self.tiles_per_row - 1) // self.tiles_per_row
        total_height = rows * (self.tile_display_size + self.tile_padding * 2)
        content_height = self.height - self.tab_height - 70  # Account for metadata panel

        self.max_scroll = max(0, total_height - content_height)

    def get_selected_tile(self) -> Optional[Tuple[str, int]]:
        """
        Get the currently selected tile.

        Returns:
            (tileset_id, tile_id) tuple or None if no selection
        """
        if self.selected_tileset_id is None or self.selected_tile_id is None:
            return None
        return (self.selected_tileset_id, self.selected_tile_id)

    def set_selected_tile(self, tileset_id: str, tile_id: int):
        """
        Set the selected tile.

        Args:
            tileset_id: Tileset identifier
            tile_id: Tile identifier
        """
        self.selected_tileset_id = tileset_id
        self.selected_tile_id = tile_id
        self.tileset_manager.set_active_tileset(tileset_id)

    def toggle_visibility(self):
        """Toggle picker visibility."""
        self.visible = not self.visible

    def show(self):
        """Show the picker."""
        self.visible = True

    def hide(self):
        """Hide the picker."""
        self.visible = False
