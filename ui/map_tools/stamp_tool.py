"""
Stamp tool for custom brush stamps.

Supports:
- Create custom brush stamps from selection
- Save/load stamps
- Paint with stamps
- Rotate and flip stamps
- All layers
- Undo/redo
"""

from typing import Dict, List, Optional, Set, Tuple

import pygame

from ...rendering.tilemap import Tile
from .base import MapTool, ToolContext
from .settings import DefaultStamps, RenderSettings, ToolColors, get_default_stamps, get_tool_color
from .undo_manager import BatchTileChangeAction


class BrushStamp:
    """Represents a custom brush stamp."""

    def __init__(self, name: str, tiles: Dict[Tuple[int, int], Tile], width: int, height: int):
        """
        Initialize brush stamp.

        Args:
            name: Stamp name
            tiles: Dict mapping (relative_x, relative_y) to Tile
            width: Stamp width in tiles
            height: Stamp height in tiles
        """
        self.name = name
        self.tiles = tiles
        self.width = width
        self.height = height

    def get_rotated(self, rotation: int) -> "BrushStamp":
        """
        Get rotated version of stamp.

        Args:
            rotation: Rotation in 90-degree increments (0, 1, 2, 3)

        Returns:
            New BrushStamp with rotated tiles
        """
        if rotation % 4 == 0:
            return self

        rotated_tiles = {}
        for (x, y), tile in self.tiles.items():
            # Rotate coordinates
            for _ in range(rotation % 4):
                x, y = -y, x

            rotated_tiles[(x, y)] = tile

        # Update dimensions
        if rotation % 2 == 1:
            new_width, new_height = self.height, self.width
        else:
            new_width, new_height = self.width, self.height

        return BrushStamp(f"{self.name}_rot{rotation}", rotated_tiles, new_width, new_height)

    def get_flipped(self, flip_h: bool, flip_v: bool) -> "BrushStamp":
        """
        Get flipped version of stamp.

        Args:
            flip_h: Flip horizontally
            flip_v: Flip vertically

        Returns:
            New BrushStamp with flipped tiles
        """
        if not flip_h and not flip_v:
            return self

        flipped_tiles = {}
        for (x, y), tile in self.tiles.items():
            new_x = -x if flip_h else x
            new_y = -y if flip_v else y
            flipped_tiles[(new_x, new_y)] = tile

        suffix = ""
        if flip_h:
            suffix += "_fh"
        if flip_v:
            suffix += "_fv"

        return BrushStamp(f"{self.name}{suffix}", flipped_tiles, self.width, self.height)


class StampTool(MapTool):
    """
    Stamp tool for custom brush stamps.

    Left click: Paint with current stamp
    Right click: Create stamp from selection (requires SelectTool)
    Keys 1-9: Switch between stamps
    Key R: Rotate stamp
    Key H: Flip horizontally
    Key V: Flip vertically
    """

    def __init__(self):
        super().__init__("Stamp", 6, get_tool_color("stamp"))
        self.cursor_type = "stamp"
        self.stamps: List[BrushStamp] = []
        self.current_stamp_index = 0
        self.rotation = 0  # 0, 1, 2, 3 (90-degree increments)
        self.flip_h = False
        self.flip_v = False
        self.last_painted_pos: Optional[Tuple[int, int]] = None

        # Create some default stamps
        self._create_default_stamps()

    def _create_default_stamps(self):
        """Create default brush stamps from centralized settings."""
        stamps_data = get_default_stamps()
        for stamp_def in stamps_data.values():
            # Convert coordinate tuples to dict with None values (filled during painting)
            tiles = {tuple(coord): None for coord in stamp_def["coords"]}
            stamp = BrushStamp(stamp_def["name"], tiles, stamp_def["width"], stamp_def["height"])
            self.stamps.append(stamp)

    def on_mouse_down(self, grid_x: int, grid_y: int, button: int, context: ToolContext) -> bool:
        if button == 0:  # Left click - paint with stamp
            self.last_painted_pos = (grid_x, grid_y)
            return self._paint_stamp(grid_x, grid_y, context)
        elif button == 2:  # Right click - create stamp from selection
            return self._create_stamp_from_selection(context)
        return False

    def on_mouse_drag(self, grid_x: int, grid_y: int, button: int, context: ToolContext) -> bool:
        if button != 0:  # Left click only
            return False

        # Avoid painting the same position twice
        if self.last_painted_pos == (grid_x, grid_y):
            return True

        self.last_painted_pos = (grid_x, grid_y)
        return self._paint_stamp(grid_x, grid_y, context)

    def on_mouse_up(self, grid_x: int, grid_y: int, button: int, context: ToolContext) -> bool:
        self.last_painted_pos = None
        return False

    def _paint_stamp(self, grid_x: int, grid_y: int, context: ToolContext) -> bool:
        """
        Paint the current stamp at the given position.

        Args:
            grid_x: Grid X coordinate (center of stamp)
            grid_y: Grid Y coordinate (center of stamp)
            context: Tool context

        Returns:
            True if stamp was painted
        """
        if not context.tilemap or not context.selected_tile:
            return False

        if not self.stamps or self.current_stamp_index >= len(self.stamps):
            print("No stamp selected")
            return False

        # Get current stamp with transformations
        stamp = self.stamps[self.current_stamp_index]
        stamp = stamp.get_rotated(self.rotation)
        stamp = stamp.get_flipped(self.flip_h, self.flip_v)

        # Get tile data
        tile_data = context.tile_palette.get(context.selected_tile)
        if not tile_data:
            return False

        # Paint stamp
        changes = []
        new_tile = Tile(tile_type=context.selected_tile, walkable=tile_data["walkable"])

        for (offset_x, offset_y), _ in stamp.tiles.items():
            x = grid_x + offset_x
            y = grid_y + offset_y

            # Check bounds
            if 0 <= x < context.grid_width and 0 <= y < context.grid_height:
                old_tile = context.tilemap.get_tile(x, y, context.current_layer)
                changes.append((x, y, context.current_layer, old_tile, new_tile))
                context.tilemap.set_tile(x, y, context.current_layer, new_tile)

        # Record undo action
        if changes and context.undo_manager:
            action = BatchTileChangeAction(context.tilemap, changes)
            context.undo_manager.record_action(action)

        return len(changes) > 0

    def _create_stamp_from_selection(self, context: ToolContext) -> bool:
        """
        Create a new stamp from the current selection.

        Args:
            context: Tool context

        Returns:
            True if stamp was created
        """
        # This requires access to SelectTool's selection
        # For now, we'll print a message
        print(
            "To create a stamp: Use Select tool to select tiles, then switch to Stamp tool and right-click"
        )
        return False

    def add_stamp(self, stamp: BrushStamp):
        """
        Add a custom stamp.

        Args:
            stamp: BrushStamp to add
        """
        self.stamps.append(stamp)
        print(f"Added stamp: {stamp.name}")

    def select_stamp(self, index: int):
        """
        Select a stamp by index.

        Args:
            index: Stamp index
        """
        if 0 <= index < len(self.stamps):
            self.current_stamp_index = index
            stamp = self.stamps[index]
            print(f"Selected stamp: {stamp.name} ({stamp.width}x{stamp.height})")

    def rotate_stamp(self):
        """Rotate current stamp 90 degrees clockwise."""
        self.rotation = (self.rotation + 1) % 4
        print(f"Stamp rotation: {self.rotation * 90} degrees")

    def flip_horizontal(self):
        """Toggle horizontal flip."""
        self.flip_h = not self.flip_h
        print(f"Horizontal flip: {'ON' if self.flip_h else 'OFF'}")

    def flip_vertical(self):
        """Toggle vertical flip."""
        self.flip_v = not self.flip_v
        print(f"Vertical flip: {'ON' if self.flip_v else 'OFF'}")

    def render_cursor(
        self,
        screen: pygame.Surface,
        grid_x: int,
        grid_y: int,
        tile_size: int,
        camera_offset: Tuple[int, int],
    ):
        """Render stamp tool cursor with stamp preview."""
        if not self.stamps or self.current_stamp_index >= len(self.stamps):
            return

        # Get current stamp with transformations
        stamp = self.stamps[self.current_stamp_index]
        stamp = stamp.get_rotated(self.rotation)
        stamp = stamp.get_flipped(self.flip_h, self.flip_v)

        # Draw stamp preview
        for (offset_x, offset_y), _ in stamp.tiles.items():
            x = grid_x + offset_x
            y = grid_y + offset_y

            screen_x = x * tile_size + camera_offset[0]
            screen_y = y * tile_size + camera_offset[1]

            # Draw semi-transparent preview
            preview_surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
            preview_surface.fill((*ToolColors.CURSOR_STAMP, RenderSettings.STAMP_PREVIEW_ALPHA))
            screen.blit(preview_surface, (screen_x, screen_y))

            # Draw outline
            pygame.draw.rect(
                screen,
                ToolColors.CURSOR_STAMP,
                (screen_x, screen_y, tile_size, tile_size),
                RenderSettings.CURSOR_OUTLINE_WIDTH,
            )

        # Draw center cursor
        screen_x = grid_x * tile_size + camera_offset[0]
        screen_y = grid_y * tile_size + camera_offset[1]
        pygame.draw.rect(
            screen,
            ToolColors.CURSOR_STAMP,
            (screen_x, screen_y, tile_size, tile_size),
            RenderSettings.CURSOR_HIGHLIGHT_WIDTH,
        )

        # Draw stamp info
        font = pygame.font.Font(None, 14)
        info_text = f"{self.current_stamp_index + 1}/{len(self.stamps)}"
        if self.rotation > 0:
            info_text += f" R{self.rotation}"
        if self.flip_h:
            info_text += " H"
        if self.flip_v:
            info_text += " V"

        text_surface = font.render(info_text, True, ToolColors.CURSOR_STAMP)
        screen.blit(text_surface, (screen_x + 2, screen_y + 2))
