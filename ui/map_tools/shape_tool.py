"""
Shape tool for drawing geometric shapes.

Supports:
- Rectangle (outline and filled)
- Circle (outline and filled)
- Line drawing
- All layers
- Undo/redo
"""

from typing import List, Optional, Set, Tuple

import pygame

from ...rendering.tilemap import Tile
from .base import MapTool, ToolContext
from .settings import RenderSettings, ToolColors, get_tool_color
from .undo_manager import BatchTileChangeAction


class ShapeTool(MapTool):
    """
    Shape tool for drawing geometric shapes.

    Left click and drag: Draw shape
    Keys 1-3: Switch shape type (1=rectangle, 2=circle, 3=line)
    Key F: Toggle fill mode
    """

    def __init__(self):
        super().__init__("Shape", 5, get_tool_color("shape"))
        self.cursor_type = "shape"
        self.shape_start: Optional[Tuple[int, int]] = None
        self.shape_end: Optional[Tuple[int, int]] = None
        self.is_drawing = False
        self.shape_type = "rectangle"  # "rectangle", "circle", "line"
        self.fill_mode = False  # False = outline, True = filled

    def on_mouse_down(self, grid_x: int, grid_y: int, button: int, context: ToolContext) -> bool:
        if button != 0:  # Left click only
            return False

        self.shape_start = (grid_x, grid_y)
        self.shape_end = (grid_x, grid_y)
        self.is_drawing = True
        return True

    def on_mouse_drag(self, grid_x: int, grid_y: int, button: int, context: ToolContext) -> bool:
        if button != 0 or not self.is_drawing:
            return False

        self.shape_end = (grid_x, grid_y)
        return True

    def on_mouse_up(self, grid_x: int, grid_y: int, button: int, context: ToolContext) -> bool:
        if button != 0 or not self.is_drawing:
            return False

        self.shape_end = (grid_x, grid_y)
        self.is_drawing = False

        # Draw the shape
        if self.shape_start and self.shape_end:
            return self._draw_shape(context)

        return False

    def set_shape_type(self, shape_type: str):
        """
        Set the shape type.

        Args:
            shape_type: "rectangle", "circle", or "line"
        """
        if shape_type in ("rectangle", "circle", "line"):
            self.shape_type = shape_type
            print(f"Shape type: {shape_type}")

    def toggle_fill_mode(self):
        """Toggle between outline and filled mode."""
        self.fill_mode = not self.fill_mode
        mode = "filled" if self.fill_mode else "outline"
        print(f"Fill mode: {mode}")

    def _draw_shape(self, context: ToolContext) -> bool:
        """
        Draw the current shape.

        Args:
            context: Tool context

        Returns:
            True if shape was drawn
        """
        if (
            not context.tilemap
            or not context.selected_tile
            or not self.shape_start
            or not self.shape_end
        ):
            return False

        # Get tile data
        tile_data = context.tile_palette.get(context.selected_tile)
        if not tile_data:
            return False

        # Get shape coordinates
        if self.shape_type == "rectangle":
            coords = self._get_rectangle_coords()
        elif self.shape_type == "circle":
            coords = self._get_circle_coords()
        elif self.shape_type == "line":
            coords = self._get_line_coords()
        else:
            return False

        # Filter coordinates to valid grid positions
        valid_coords = [
            (x, y)
            for x, y in coords
            if 0 <= x < context.grid_width and 0 <= y < context.grid_height
        ]

        if not valid_coords:
            return False

        # Create new tile
        new_tile = Tile(tile_type=context.selected_tile, walkable=tile_data["walkable"])

        # Record changes for undo
        changes = []
        for x, y in valid_coords:
            old_tile = context.tilemap.get_tile(x, y, context.current_layer)
            changes.append((x, y, context.current_layer, old_tile, new_tile))
            context.tilemap.set_tile(x, y, context.current_layer, new_tile)

        # Record undo action
        if changes and context.undo_manager:
            action = BatchTileChangeAction(context.tilemap, changes)
            context.undo_manager.record_action(action)

        mode = "filled" if self.fill_mode else "outline"
        print(f"Drew {mode} {self.shape_type} with {len(valid_coords)} tiles")
        return True

    def _get_rectangle_coords(self) -> Set[Tuple[int, int]]:
        """Get coordinates for rectangle shape."""
        if not self.shape_start or not self.shape_end:
            return set()

        min_x = min(self.shape_start[0], self.shape_end[0])
        max_x = max(self.shape_start[0], self.shape_end[0])
        min_y = min(self.shape_start[1], self.shape_end[1])
        max_y = max(self.shape_start[1], self.shape_end[1])

        coords = set()

        if self.fill_mode:
            # Filled rectangle
            for x in range(min_x, max_x + 1):
                for y in range(min_y, max_y + 1):
                    coords.add((x, y))
        else:
            # Outline rectangle
            for x in range(min_x, max_x + 1):
                coords.add((x, min_y))  # Top edge
                coords.add((x, max_y))  # Bottom edge
            for y in range(min_y, max_y + 1):
                coords.add((min_x, y))  # Left edge
                coords.add((max_x, y))  # Right edge

        return coords

    def _get_circle_coords(self) -> Set[Tuple[int, int]]:
        """Get coordinates for circle shape using Bresenham's algorithm."""
        if not self.shape_start or not self.shape_end:
            return set()

        # Calculate radius from start to end point
        dx = abs(self.shape_end[0] - self.shape_start[0])
        dy = abs(self.shape_end[1] - self.shape_start[1])
        radius = max(dx, dy)

        center_x, center_y = self.shape_start

        coords = set()

        if self.fill_mode:
            # Filled circle
            for x in range(center_x - radius, center_x + radius + 1):
                for y in range(center_y - radius, center_y + radius + 1):
                    dist_sq = (x - center_x) ** 2 + (y - center_y) ** 2
                    if dist_sq <= radius**2:
                        coords.add((x, y))
        else:
            # Outline circle using Bresenham's algorithm
            coords = self._bresenham_circle(center_x, center_y, radius)

        return coords

    def _bresenham_circle(self, cx: int, cy: int, radius: int) -> Set[Tuple[int, int]]:
        """
        Bresenham's circle algorithm for drawing circle outline.

        Args:
            cx: Center X coordinate
            cy: Center Y coordinate
            radius: Circle radius

        Returns:
            Set of (x, y) coordinates
        """
        coords = set()
        x = 0
        y = radius
        d = 3 - 2 * radius

        # Add all 8 octants
        def add_circle_points(cx, cy, x, y):
            coords.add((cx + x, cy + y))
            coords.add((cx - x, cy + y))
            coords.add((cx + x, cy - y))
            coords.add((cx - x, cy - y))
            coords.add((cx + y, cy + x))
            coords.add((cx - y, cy + x))
            coords.add((cx + y, cy - x))
            coords.add((cx - y, cy - x))

        add_circle_points(cx, cy, x, y)

        while y >= x:
            x += 1
            if d > 0:
                y -= 1
                d = d + 4 * (x - y) + 10
            else:
                d = d + 4 * x + 6
            add_circle_points(cx, cy, x, y)

        return coords

    def _get_line_coords(self) -> Set[Tuple[int, int]]:
        """Get coordinates for line shape using Bresenham's algorithm."""
        if not self.shape_start or not self.shape_end:
            return set()

        return self._bresenham_line(
            self.shape_start[0], self.shape_start[1], self.shape_end[0], self.shape_end[1]
        )

    def _bresenham_line(self, x0: int, y0: int, x1: int, y1: int) -> Set[Tuple[int, int]]:
        """
        Bresenham's line algorithm for drawing lines.

        Args:
            x0: Start X coordinate
            y0: Start Y coordinate
            x1: End X coordinate
            y1: End Y coordinate

        Returns:
            Set of (x, y) coordinates
        """
        coords = set()

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        x, y = x0, y0

        while True:
            coords.add((x, y))

            if x == x1 and y == y1:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

        return coords

    def render_cursor(
        self,
        screen: pygame.Surface,
        grid_x: int,
        grid_y: int,
        tile_size: int,
        camera_offset: Tuple[int, int],
    ):
        """Render shape tool cursor and preview."""
        # Render shape preview if drawing
        if self.is_drawing and self.shape_start and self.shape_end:
            # Get preview coordinates
            if self.shape_type == "rectangle":
                coords = self._get_rectangle_coords()
            elif self.shape_type == "circle":
                coords = self._get_circle_coords()
            elif self.shape_type == "line":
                coords = self._get_line_coords()
            else:
                coords = set()

            # Draw preview
            for x, y in coords:
                screen_x = x * tile_size + camera_offset[0]
                screen_y = y * tile_size + camera_offset[1]

                # Draw semi-transparent preview
                preview_surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                preview_surface.fill((*ToolColors.CURSOR_SHAPE, RenderSettings.SHAPE_PREVIEW_ALPHA))
                screen.blit(preview_surface, (screen_x, screen_y))

                # Draw outline
                pygame.draw.rect(
                    screen,
                    ToolColors.CURSOR_SHAPE,
                    (screen_x, screen_y, tile_size, tile_size),
                    RenderSettings.CURSOR_OUTLINE_WIDTH,
                )

        # Draw cursor
        screen_x = grid_x * tile_size + camera_offset[0]
        screen_y = grid_y * tile_size + camera_offset[1]

        pygame.draw.rect(
            screen,
            ToolColors.CURSOR_SHAPE,
            (screen_x, screen_y, tile_size, tile_size),
            RenderSettings.CURSOR_OUTLINE_WIDTH,
        )

        # Draw shape type indicator
        font = pygame.font.Font(None, 16)
        shape_initial = self.shape_type[0].upper()  # R, C, or L
        mode_initial = "F" if self.fill_mode else "O"  # F or O
        text = f"{shape_initial}{mode_initial}"
        text_surface = font.render(text, True, ToolColors.CURSOR_SHAPE)
        screen.blit(text_surface, (screen_x + 2, screen_y + 2))
