"""
Eyedropper tool for picking tiles from the map.

Supports:
- Pick tile from any layer
- Copy tile properties
- Quick switch back to previous tool
"""

from typing import Optional, Tuple

import pygame

from .base import MapTool, ToolContext
from .settings import RenderSettings, ToolColors, get_tool_color


class EyedropperTool(MapTool):
    """
    Eyedropper tool for picking tiles from the map.

    Left click: Pick tile from current layer
    Right click: Pick tile from any layer (searches all layers)
    Shift+Click: Pick tile and switch back to previous tool
    """

    def __init__(self):
        super().__init__("Eyedropper", 7, get_tool_color("eyedropper"))
        self.cursor_type = "eyedropper"
        self.previous_tool: Optional[str] = None
        self.picked_layer: Optional[int] = None

    def on_mouse_down(self, grid_x: int, grid_y: int, button: int, context: ToolContext) -> bool:
        if button == 0:  # Left click - pick from current layer
            return self._pick_tile(grid_x, grid_y, context, current_layer_only=True)
        elif button == 2:  # Right click - pick from any layer
            return self._pick_tile(grid_x, grid_y, context, current_layer_only=False)
        return False

    def on_mouse_drag(self, grid_x: int, grid_y: int, button: int, context: ToolContext) -> bool:
        # Eyedropper doesn't support dragging
        return False

    def on_mouse_up(self, grid_x: int, grid_y: int, button: int, context: ToolContext) -> bool:
        return False

    def _pick_tile(self, grid_x: int, grid_y: int, context: ToolContext, current_layer_only: bool) -> bool:
        """
        Pick a tile from the map.

        Args:
            grid_x: Grid X coordinate
            grid_y: Grid Y coordinate
            context: Tool context
            current_layer_only: If True, only pick from current layer

        Returns:
            True if a tile was picked
        """
        if not context.tilemap:
            return False

        # Check bounds
        if not (0 <= grid_x < context.grid_width and 0 <= grid_y < context.grid_height):
            return False

        picked_tile = None
        picked_layer = None

        if current_layer_only:
            # Pick from current layer only
            tile = context.tilemap.get_tile(grid_x, grid_y, context.current_layer)
            if tile:
                picked_tile = tile
                picked_layer = context.current_layer
        else:
            # Pick from any layer (search from top to bottom)
            for layer in range(context.tilemap.layers - 1, -1, -1):
                tile = context.tilemap.get_tile(grid_x, grid_y, layer)
                if tile:
                    picked_tile = tile
                    picked_layer = layer
                    break

        if picked_tile:
            # Update selected tile in context
            # Note: This requires the level builder UI to have a way to update selected_tile
            # For now, we'll just print the picked tile type
            self.picked_layer = picked_layer
            layer_info = f" on layer {picked_layer}" if picked_layer is not None else ""
            print(f"Picked tile: {picked_tile.tile_type}{layer_info}")

            # Attempt to update the selected tile
            # This is a hack - ideally we'd have a callback to the level builder UI
            # But for now we'll try to set it directly on the context
            if hasattr(context, "_editor_ref"):
                context._editor_ref.selected_tile = picked_tile.tile_type
                context._editor_ref.selected_tileset_id = getattr(picked_tile, "tileset_id", None)
                context._editor_ref.selected_tile_id = getattr(picked_tile, "tile_id", None)

            return True
        else:
            print(f"No tile at ({grid_x}, {grid_y})")
            return False

    def set_previous_tool(self, tool_id: str):
        """
        Set the previous tool for quick switching.

        Args:
            tool_id: ID of the previous tool
        """
        self.previous_tool = tool_id

    def get_previous_tool(self) -> Optional[str]:
        """
        Get the previous tool ID.

        Returns:
            Previous tool ID or None
        """
        return self.previous_tool

    def render_cursor(
        self,
        screen: pygame.Surface,
        grid_x: int,
        grid_y: int,
        tile_size: int,
        camera_offset: Tuple[int, int],
    ):
        """Render eyedropper cursor."""
        screen_x = grid_x * tile_size + camera_offset[0]
        screen_y = grid_y * tile_size + camera_offset[1]

        # Draw orange outline
        pygame.draw.rect(
            screen,
            ToolColors.CURSOR_EYEDROPPER,
            (screen_x, screen_y, tile_size, tile_size),
            RenderSettings.CURSOR_HIGHLIGHT_WIDTH,
        )

        # Draw eyedropper icon (simplified pipette)
        center_x = screen_x + tile_size // 2
        center_y = screen_y + tile_size // 2

        # Draw dropper body
        pygame.draw.circle(
            screen,
            ToolColors.CURSOR_EYEDROPPER,
            (center_x, center_y + 3),
            RenderSettings.EYEDROPPER_CIRCLE_RADIUS,
            RenderSettings.CURSOR_OUTLINE_WIDTH,
        )

        # Draw dropper tip
        pygame.draw.line(
            screen,
            ToolColors.CURSOR_EYEDROPPER,
            (center_x, center_y - 2),
            (center_x, center_y - 8),
            RenderSettings.CURSOR_OUTLINE_WIDTH,
        )

        # Draw picked layer indicator if available
        if self.picked_layer is not None:
            font = pygame.font.Font(None, 14)
            layer_text = f"L{self.picked_layer}"
            text_surface = font.render(layer_text, True, ToolColors.CURSOR_EYEDROPPER)
            screen.blit(text_surface, (screen_x + 2, screen_y + tile_size - 14))
