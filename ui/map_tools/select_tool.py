"""
Selection tool with rectangle and magic wand selection.

Supports:
- Rectangle selection (drag to select)
- Magic wand selection (select contiguous same-type tiles)
- Copy/paste/cut operations
- All layers
"""

from collections import deque
from typing import Dict, List, Optional, Set, Tuple

import pygame

from ...rendering.tilemap import Tile
from .base import MapTool, ToolContext
from .settings import ConnectivityModes, RenderSettings, ToolColors, get_tool_color


class SelectTool(MapTool):
    """
    Selection tool for selecting rectangular regions and magic wand selection.

    Left click and drag: Rectangle selection
    Right click: Magic wand selection (selects contiguous same-type tiles)
    Ctrl+C: Copy selection
    Ctrl+X: Cut selection
    Ctrl+V: Paste selection
    """

    def __init__(self):
        super().__init__("Select", 4, get_tool_color("select"))
        self.cursor_type = "select"
        self.selection_start: Optional[Tuple[int, int]] = None
        self.selection_end: Optional[Tuple[int, int]] = None
        self.is_selecting = False
        self.selection_mode = "rectangle"  # "rectangle" or "magic_wand"
        self.magic_wand_selection: Set[Tuple[int, int]] = set()
        self.clipboard: Optional[Dict] = None  # Stores copied tiles

    def on_mouse_down(self, grid_x: int, grid_y: int, button: int, context: ToolContext) -> bool:
        if button == 0:  # Left click - Rectangle selection
            self.selection_mode = "rectangle"
            self.magic_wand_selection.clear()
            self.selection_start = (grid_x, grid_y)
            self.selection_end = (grid_x, grid_y)
            self.is_selecting = True
            return True
        elif button == 2:  # Right click - Magic wand selection
            self.selection_mode = "magic_wand"
            self.selection_start = None
            self.selection_end = None
            self.is_selecting = False
            return self._magic_wand_select(grid_x, grid_y, context)
        return False

    def on_mouse_drag(self, grid_x: int, grid_y: int, button: int, context: ToolContext) -> bool:
        if button != 0 or not self.is_selecting:
            return False

        self.selection_end = (grid_x, grid_y)
        return True

    def on_mouse_up(self, grid_x: int, grid_y: int, button: int, context: ToolContext) -> bool:
        if button != 0 or not self.is_selecting:
            return False

        self.selection_end = (grid_x, grid_y)
        self.is_selecting = False

        # Calculate selection bounds
        if self.selection_start and self.selection_end:
            min_x = min(self.selection_start[0], self.selection_end[0])
            max_x = max(self.selection_start[0], self.selection_end[0])
            min_y = min(self.selection_start[1], self.selection_end[1])
            max_y = max(self.selection_start[1], self.selection_end[1])

            width = max_x - min_x + 1
            height = max_y - min_y + 1
            print(f"Selected region: ({min_x}, {min_y}) to ({max_x}, {max_y}) [{width}x{height}]")

        return True

    def _magic_wand_select(self, start_x: int, start_y: int, context: ToolContext) -> bool:
        """
        Perform magic wand selection (select contiguous same-type tiles).

        Args:
            start_x: Starting grid X coordinate
            start_y: Starting grid Y coordinate
            context: Tool context

        Returns:
            True if selection was made
        """
        if not context.tilemap:
            return False

        # Check bounds
        if not (0 <= start_x < context.grid_width and 0 <= start_y < context.grid_height):
            return False

        # Get the tile type we're selecting
        target_tile = context.tilemap.get_tile(start_x, start_y, context.current_layer)
        target_type = target_tile.tile_type if target_tile else None

        # Clear previous magic wand selection
        self.magic_wand_selection.clear()

        # Perform BFS to find contiguous tiles
        visited: Set[Tuple[int, int]] = set()
        queue: deque = deque([(start_x, start_y)])
        visited.add((start_x, start_y))

        while queue:
            x, y = queue.popleft()

            # Check if this position has the target tile type
            current_tile = context.tilemap.get_tile(x, y, context.current_layer)
            current_type = current_tile.tile_type if current_tile else None

            if current_type != target_type:
                continue

            # Add to selection
            self.magic_wand_selection.add((x, y))

            # Add neighbors to queue (using 4-way connectivity)
            for dx, dy in ConnectivityModes.FOUR_WAY:
                nx, ny = x + dx, y + dy

                if (
                    0 <= nx < context.grid_width
                    and 0 <= ny < context.grid_height
                    and (nx, ny) not in visited
                ):
                    visited.add((nx, ny))
                    queue.append((nx, ny))

        print(f"Magic wand selected {len(self.magic_wand_selection)} tiles")
        return len(self.magic_wand_selection) > 0

    def get_selection_bounds(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Get the bounds of the current selection.

        Returns:
            Tuple of (min_x, min_y, max_x, max_y) or None if no selection
        """
        if self.selection_mode == "rectangle" and self.selection_start and self.selection_end:
            min_x = min(self.selection_start[0], self.selection_end[0])
            max_x = max(self.selection_start[0], self.selection_end[0])
            min_y = min(self.selection_start[1], self.selection_end[1])
            max_y = max(self.selection_start[1], self.selection_end[1])
            return (min_x, min_y, max_x, max_y)
        elif self.selection_mode == "magic_wand" and self.magic_wand_selection:
            coords = list(self.magic_wand_selection)
            min_x = min(x for x, y in coords)
            max_x = max(x for x, y in coords)
            min_y = min(y for x, y in coords)
            max_y = max(y for x, y in coords)
            return (min_x, min_y, max_x, max_y)
        return None

    def get_selected_tiles(self) -> Set[Tuple[int, int]]:
        """
        Get all selected tile coordinates.

        Returns:
            Set of (x, y) tuples
        """
        if self.selection_mode == "rectangle" and self.selection_start and self.selection_end:
            min_x = min(self.selection_start[0], self.selection_end[0])
            max_x = max(self.selection_start[0], self.selection_end[0])
            min_y = min(self.selection_start[1], self.selection_end[1])
            max_y = max(self.selection_start[1], self.selection_end[1])

            return {(x, y) for x in range(min_x, max_x + 1) for y in range(min_y, max_y + 1)}
        elif self.selection_mode == "magic_wand":
            return self.magic_wand_selection.copy()
        return set()

    def copy_selection(self, context: ToolContext):
        """Copy selected tiles to clipboard."""
        if not context.tilemap:
            return

        selected_tiles = self.get_selected_tiles()
        if not selected_tiles:
            print("No selection to copy")
            return

        # Store tiles in clipboard
        self.clipboard = {"tiles": {}, "layer": context.current_layer}

        for x, y in selected_tiles:
            tile = context.tilemap.get_tile(x, y, context.current_layer)
            if tile:
                self.clipboard["tiles"][(x, y)] = tile

        print(f"Copied {len(self.clipboard['tiles'])} tiles to clipboard")

    def cut_selection(self, context: ToolContext):
        """Cut selected tiles to clipboard."""
        if not context.tilemap:
            return

        # Copy first
        self.copy_selection(context)

        # Then delete
        selected_tiles = self.get_selected_tiles()
        for x, y in selected_tiles:
            context.tilemap.set_tile(x, y, context.current_layer, None)

        print(f"Cut {len(selected_tiles)} tiles to clipboard")

    def paste_selection(self, grid_x: int, grid_y: int, context: ToolContext):
        """Paste clipboard at the given position."""
        if not self.clipboard or not context.tilemap:
            print("Nothing to paste")
            return

        # Calculate offset
        tiles = self.clipboard["tiles"]
        if not tiles:
            return

        # Find min coords in clipboard
        coords = list(tiles.keys())
        min_x = min(x for x, y in coords)
        min_y = min(y for x, y in coords)

        # Paste with offset
        for (orig_x, orig_y), tile in tiles.items():
            offset_x = orig_x - min_x
            offset_y = orig_y - min_y
            new_x = grid_x + offset_x
            new_y = grid_y + offset_y

            if 0 <= new_x < context.grid_width and 0 <= new_y < context.grid_height:
                context.tilemap.set_tile(new_x, new_y, context.current_layer, tile)

        print(f"Pasted {len(tiles)} tiles at ({grid_x}, {grid_y})")

    def clear_selection(self):
        """Clear the current selection."""
        self.selection_start = None
        self.selection_end = None
        self.is_selecting = False
        self.magic_wand_selection.clear()

    def render_cursor(
        self,
        screen: pygame.Surface,
        grid_x: int,
        grid_y: int,
        tile_size: int,
        camera_offset: Tuple[int, int],
    ):
        """Render selection cursor and selection box."""
        # Render rectangle selection box if selecting
        if self.selection_mode == "rectangle" and self.selection_start and self.selection_end:
            min_x = min(self.selection_start[0], self.selection_end[0])
            max_x = max(self.selection_start[0], self.selection_end[0])
            min_y = min(self.selection_start[1], self.selection_end[1])
            max_y = max(self.selection_start[1], self.selection_end[1])

            screen_x = min_x * tile_size + camera_offset[0]
            screen_y = min_y * tile_size + camera_offset[1]
            width = (max_x - min_x + 1) * tile_size
            height = (max_y - min_y + 1) * tile_size

            # Draw selection box
            pygame.draw.rect(
                screen,
                ToolColors.CURSOR_SELECT_RECT,
                (screen_x, screen_y, width, height),
                RenderSettings.CURSOR_OUTLINE_WIDTH,
            )

            # Draw semi-transparent overlay
            overlay = pygame.Surface((width, height), pygame.SRCALPHA)
            overlay.fill((*ToolColors.CURSOR_SELECT_RECT, RenderSettings.SELECTION_OVERLAY_ALPHA))
            screen.blit(overlay, (screen_x, screen_y))

        # Render magic wand selection
        elif self.selection_mode == "magic_wand" and self.magic_wand_selection:
            for sel_x, sel_y in self.magic_wand_selection:
                screen_x = sel_x * tile_size + camera_offset[0]
                screen_y = sel_y * tile_size + camera_offset[1]

                # Draw selection box for each tile
                pygame.draw.rect(
                    screen,
                    ToolColors.CURSOR_SELECT_WAND,
                    (screen_x, screen_y, tile_size, tile_size),
                    RenderSettings.CURSOR_OUTLINE_WIDTH,
                )

                # Draw semi-transparent overlay
                overlay = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                overlay.fill((*ToolColors.CURSOR_SELECT_WAND, RenderSettings.SELECTION_OVERLAY_ALPHA))
                screen.blit(overlay, (screen_x, screen_y))

        # Draw cursor
        screen_x = grid_x * tile_size + camera_offset[0]
        screen_y = grid_y * tile_size + camera_offset[1]

        color = ToolColors.CURSOR_SELECT_RECT if self.selection_mode == "rectangle" else ToolColors.CURSOR_SELECT_WAND
        pygame.draw.rect(
            screen, color, (screen_x, screen_y, tile_size, tile_size), RenderSettings.CURSOR_OUTLINE_WIDTH
        )
