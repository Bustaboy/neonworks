"""
Autotile Tool for Level Builder

Provides intelligent tile painting with automatic tile matching and neighbor updates.
"""

from typing import Optional, Tuple

import pygame

from neonworks.rendering.autotiles import AutotileManager, AutotileSet, get_autotile_manager
from neonworks.rendering.tilemap import Tile

from .map_tools import MapTool, ToolContext


class AutotileTool(MapTool):
    """
    Tool for painting autotiles with intelligent neighbor matching.

    This tool automatically selects the correct tile variant based on
    neighboring tiles and updates adjacent tiles for seamless transitions.
    """

    def __init__(self):
        """Initialize the autotile tool."""
        super().__init__("Autotile", hotkey=8, color=(100, 200, 255))
        self.cursor_type = "brush"

        self.autotile_manager = get_autotile_manager()
        self.current_autotile_set: Optional[AutotileSet] = None

        # Preview state
        self.preview_tile_id: Optional[int] = None
        self.preview_position: Optional[Tuple[int, int]] = None

    def set_autotile_set(self, autotile_set: AutotileSet):
        """
        Set the active autotile set for painting.

        Args:
            autotile_set: AutotileSet to use for painting
        """
        self.current_autotile_set = autotile_set

    def on_mouse_down(self, grid_x: int, grid_y: int, button: int, context: ToolContext) -> bool:
        """Handle mouse button press - paint autotile."""
        if not context.tilemap:
            return False

        if not self.current_autotile_set:
            return False

        layer = context.tilemap.get_layer(context.current_layer)
        if not layer:
            return False

        if button == 0:  # Left click - paint
            self.autotile_manager.paint_autotile(layer, grid_x, grid_y, self.current_autotile_set)
            return True
        elif button == 2:  # Right click - erase
            self.autotile_manager.erase_autotile(layer, grid_x, grid_y)
            return True

        return False

    def on_mouse_drag(self, grid_x: int, grid_y: int, button: int, context: ToolContext) -> bool:
        """Handle mouse drag - paint continuously."""
        if not context.tilemap:
            return False

        if not self.current_autotile_set:
            return False

        layer = context.tilemap.get_layer(context.current_layer)
        if not layer:
            return False

        if button == 0:  # Left click - paint
            self.autotile_manager.paint_autotile(layer, grid_x, grid_y, self.current_autotile_set)
            return True
        elif button == 2:  # Right click - erase
            self.autotile_manager.erase_autotile(layer, grid_x, grid_y)
            return True

        return False

    def on_mouse_up(self, grid_x: int, grid_y: int, button: int, context: ToolContext) -> bool:
        """Handle mouse button release."""
        # Clear preview
        self.preview_tile_id = None
        self.preview_position = None
        return False

    def on_mouse_move(self, grid_x: int, grid_y: int, context: ToolContext):
        """
        Handle mouse movement - update preview.

        Args:
            grid_x: Grid X coordinate
            grid_y: Grid Y coordinate
            context: Tool context
        """
        if not context.tilemap or not self.current_autotile_set:
            self.preview_tile_id = None
            self.preview_position = None
            return

        layer = context.tilemap.get_layer(context.current_layer)
        if not layer:
            return

        # Calculate preview tile
        self.preview_tile_id = self.autotile_manager.get_preview_tile(
            layer, grid_x, grid_y, self.current_autotile_set
        )
        self.preview_position = (grid_x, grid_y)

    def render_cursor(
        self,
        screen: pygame.Surface,
        grid_x: int,
        grid_y: int,
        tile_size: int,
        camera_offset: Tuple[int, int],
    ):
        """Render autotile preview cursor."""
        screen_x = grid_x * tile_size + camera_offset[0]
        screen_y = grid_y * tile_size + camera_offset[1]

        # Draw preview background
        preview_surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
        preview_surface.fill((100, 200, 255, 100))  # Semi-transparent blue
        screen.blit(preview_surface, (screen_x, screen_y))

        # Draw border
        pygame.draw.rect(screen, self.color, (screen_x, screen_y, tile_size, tile_size), 2)

        # TODO: Render preview tile sprite if tileset is available


class AutotileFillTool(MapTool):
    """
    Flood fill tool for autotiles.

    Fills an area with autotiles, automatically updating all tiles
    to create seamless transitions.
    """

    def __init__(self):
        """Initialize the autotile fill tool."""
        super().__init__("Autotile Fill", hotkey=0, color=(150, 220, 255))
        self.cursor_type = "fill"

        self.autotile_manager = get_autotile_manager()
        self.current_autotile_set: Optional[AutotileSet] = None

    def set_autotile_set(self, autotile_set: AutotileSet):
        """
        Set the active autotile set for filling.

        Args:
            autotile_set: AutotileSet to use for filling
        """
        self.current_autotile_set = autotile_set

    def on_mouse_down(self, grid_x: int, grid_y: int, button: int, context: ToolContext) -> bool:
        """Handle mouse button press - fill area with autotiles."""
        if not context.tilemap:
            return False

        if not self.current_autotile_set:
            return False

        if button != 0:  # Only left click
            return False

        layer = context.tilemap.get_layer(context.current_layer)
        if not layer:
            return False

        # Fill with autotiles
        self.autotile_manager.fill_with_autotile(layer, grid_x, grid_y, self.current_autotile_set)
        return True

    def on_mouse_drag(self, grid_x: int, grid_y: int, button: int, context: ToolContext) -> bool:
        """Handle mouse drag - no-op for fill tool."""
        return False

    def on_mouse_up(self, grid_x: int, grid_y: int, button: int, context: ToolContext) -> bool:
        """Handle mouse button release."""
        return False

    def render_cursor(
        self,
        screen: pygame.Surface,
        grid_x: int,
        grid_y: int,
        tile_size: int,
        camera_offset: Tuple[int, int],
    ):
        """Render fill cursor with fill icon."""
        screen_x = grid_x * tile_size + camera_offset[0]
        screen_y = grid_y * tile_size + camera_offset[1]

        # Draw fill icon background
        preview_surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
        preview_surface.fill((150, 220, 255, 100))
        screen.blit(preview_surface, (screen_x, screen_y))

        # Draw border
        pygame.draw.rect(screen, self.color, (screen_x, screen_y, tile_size, tile_size), 2)

        # Draw fill icon (simplified bucket)
        center_x = screen_x + tile_size // 2
        center_y = screen_y + tile_size // 2
        pygame.draw.circle(screen, self.color, (center_x, center_y), tile_size // 4, 2)
