"""
Fill tool with advanced flood fill algorithm.

Supports:
- Basic flood fill (4-way connectivity)
- 8-way connectivity flood fill
- Contiguous fill (same tile type)
- All layers
- Undo/redo
"""

from collections import deque
from typing import Optional, Set, Tuple

import pygame

from ...rendering.tilemap import Tile
from .base import MapTool, ToolContext
from .undo_manager import BatchTileChangeAction


class FillTool(MapTool):
    """
    Fill tool for flood filling tiles.

    Left click fills contiguous region of same tile type with selected tile.
    Right click to toggle 4-way/8-way connectivity.
    Only works for tiles, not entities or events.
    """

    def __init__(self):
        super().__init__("Fill", 3, (0, 150, 150))
        self.cursor_type = "fill"
        self.use_8way = False  # Toggle between 4-way and 8-way connectivity
        self.max_fill_cells = 10000  # Safety limit to prevent infinite fills

    def on_mouse_down(self, grid_x: int, grid_y: int, button: int, context: ToolContext) -> bool:
        if button == 0:  # Left click - flood fill
            return self._flood_fill(grid_x, grid_y, context)
        elif button == 2:  # Right click - toggle 4-way/8-way
            self.use_8way = not self.use_8way
            mode = "8-way" if self.use_8way else "4-way"
            print(f"Fill mode: {mode} connectivity")
            return True
        return False

    def on_mouse_drag(self, grid_x: int, grid_y: int, button: int, context: ToolContext) -> bool:
        # Fill tool doesn't support dragging
        return False

    def on_mouse_up(self, grid_x: int, grid_y: int, button: int, context: ToolContext) -> bool:
        return False

    def _flood_fill(self, start_x: int, start_y: int, context: ToolContext) -> bool:
        """
        Perform flood fill starting from the given position.

        Uses BFS (Breadth-First Search) for efficient filling.
        Supports both 4-way and 8-way connectivity.

        Args:
            start_x: Starting grid X coordinate
            start_y: Starting grid Y coordinate
            context: Tool context

        Returns:
            True if tiles were filled, False otherwise
        """
        if not context.tilemap or not context.selected_tile:
            return False

        # Check bounds
        if not (0 <= start_x < context.grid_width and 0 <= start_y < context.grid_height):
            return False

        # Get the tile type we're replacing
        original_tile = context.tilemap.get_tile(start_x, start_y, context.current_layer)
        original_type = original_tile.tile_type if original_tile else None

        # Get the new tile type
        new_tile_type = context.selected_tile

        # Don't fill if already the same type
        if original_type == new_tile_type:
            return False

        # Get tile data for new tile
        tile_data = context.tile_palette.get(new_tile_type)
        if not tile_data:
            return False

        # Perform flood fill using BFS
        changes = []
        visited: Set[Tuple[int, int]] = set()
        queue: deque = deque([(start_x, start_y)])
        visited.add((start_x, start_y))

        # Define neighbor offsets based on connectivity mode
        if self.use_8way:
            # 8-way connectivity (includes diagonals)
            neighbors = [
                (0, 1),
                (0, -1),
                (1, 0),
                (-1, 0),  # Cardinal directions
                (1, 1),
                (1, -1),
                (-1, 1),
                (-1, -1),  # Diagonal directions
            ]
        else:
            # 4-way connectivity (cardinal directions only)
            neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        while queue and len(changes) < self.max_fill_cells:
            x, y = queue.popleft()

            # Check if this position has the original tile type
            current_tile = context.tilemap.get_tile(x, y, context.current_layer)
            current_type = current_tile.tile_type if current_tile else None

            if current_type != original_type:
                continue

            # Create new tile
            new_tile = Tile(tile_type=new_tile_type, walkable=tile_data["walkable"])

            # Record change for undo
            changes.append((x, y, context.current_layer, current_tile, new_tile))

            # Fill this position
            context.tilemap.set_tile(x, y, context.current_layer, new_tile)

            # Add neighbors to queue
            for dx, dy in neighbors:
                nx, ny = x + dx, y + dy

                if (
                    0 <= nx < context.grid_width
                    and 0 <= ny < context.grid_height
                    and (nx, ny) not in visited
                ):
                    visited.add((nx, ny))
                    queue.append((nx, ny))

        # Record undo action if changes were made
        if changes and context.undo_manager:
            action = BatchTileChangeAction(context.tilemap, changes)
            context.undo_manager.record_action(action)

        if len(changes) >= self.max_fill_cells:
            print(f"Warning: Fill limited to {self.max_fill_cells} tiles (safety limit)")
        else:
            mode = "8-way" if self.use_8way else "4-way"
            print(f"Filled {len(changes)} tiles with {new_tile_type} ({mode} mode)")

        return len(changes) > 0

    def render_cursor(
        self,
        screen: pygame.Surface,
        grid_x: int,
        grid_y: int,
        tile_size: int,
        camera_offset: Tuple[int, int],
    ):
        """Render fill cursor."""
        screen_x = grid_x * tile_size + camera_offset[0]
        screen_y = grid_y * tile_size + camera_offset[1]

        # Draw cyan outline
        pygame.draw.rect(screen, (0, 255, 255), (screen_x, screen_y, tile_size, tile_size), 3)

        # Draw fill icon (paint bucket)
        center_x = screen_x + tile_size // 2
        center_y = screen_y + tile_size // 2
        pygame.draw.circle(screen, (0, 255, 255), (center_x, center_y), tile_size // 4, 2)

        # Draw mode indicator (4 or 8)
        mode_text = "8" if self.use_8way else "4"
        font = pygame.font.Font(None, 20)
        text_surface = font.render(mode_text, True, (0, 255, 255))
        text_rect = text_surface.get_rect(center=(center_x, center_y))
        screen.blit(text_surface, text_rect)
