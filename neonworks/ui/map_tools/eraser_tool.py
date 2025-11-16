"""
Eraser tool for removing tiles, entities, and events.
"""

from typing import Optional, Tuple

import pygame

from ...core.ecs import GridPosition
from .base import MapTool, ToolContext
from .settings import RenderSettings, ToolColors, get_tool_color
from .undo_manager import TileChangeAction


class EraserTool(MapTool):
    """
    Eraser tool for removing tiles, entities, and events.

    Left click erases tile/entity/event at the position.
    Supports drag erasing.
    """

    def __init__(self):
        super().__init__("Eraser", 2, get_tool_color("eraser"))
        self.cursor_type = "eraser"
        self.last_erased_pos: Optional[Tuple[int, int]] = None

    def on_mouse_down(self, grid_x: int, grid_y: int, button: int, context: ToolContext) -> bool:
        if button != 0:  # Left click only
            return False

        self.last_erased_pos = (grid_x, grid_y)
        return self._erase(grid_x, grid_y, context)

    def on_mouse_drag(self, grid_x: int, grid_y: int, button: int, context: ToolContext) -> bool:
        if button != 0:  # Left click only
            return False

        # Avoid erasing the same position twice
        if self.last_erased_pos == (grid_x, grid_y):
            return True

        self.last_erased_pos = (grid_x, grid_y)
        return self._erase(grid_x, grid_y, context)

    def on_mouse_up(self, grid_x: int, grid_y: int, button: int, context: ToolContext) -> bool:
        self.last_erased_pos = None
        return False

    def _erase(self, grid_x: int, grid_y: int, context: ToolContext) -> bool:
        """Erase tile, entity, or event at the given position."""
        # Check bounds
        if not (0 <= grid_x < context.grid_width and 0 <= grid_y < context.grid_height):
            return False

        erased_something = False

        # Erase tile from tilemap
        if context.tilemap:
            old_tile = context.tilemap.get_tile(grid_x, grid_y, context.current_layer)
            if old_tile:
                context.tilemap.set_tile(grid_x, grid_y, context.current_layer, None)

                # Record undo action
                if context.undo_manager:
                    action = TileChangeAction(
                        context.tilemap, grid_x, grid_y, context.current_layer, old_tile, None
                    )
                    context.undo_manager.record_action(action)

                erased_something = True

        # Erase entities at this position
        to_remove = []
        for entity_id in context.world.entities:
            grid_pos = context.world.get_component(entity_id, GridPosition)
            if grid_pos and grid_pos.grid_x == grid_x and grid_pos.grid_y == grid_y:
                to_remove.append(entity_id)

        for entity_id in to_remove:
            context.world.remove_entity(entity_id)
            erased_something = True

        # Erase events at this position
        events_to_remove = []
        for event in context.events:
            if event.x == grid_x and event.y == grid_y:
                events_to_remove.append(event)

        for event in events_to_remove:
            context.events.remove(event)
            print(f"Erased event #{event.id} at ({grid_x}, {grid_y})")
            erased_something = True

        # Sync events to event editor if available
        if context.event_editor and events_to_remove:
            context.event_editor.load_events_from_scene(context.events)

        return erased_something

    def render_cursor(
        self,
        screen: pygame.Surface,
        grid_x: int,
        grid_y: int,
        tile_size: int,
        camera_offset: Tuple[int, int],
    ):
        """Render eraser cursor."""
        screen_x = grid_x * tile_size + camera_offset[0]
        screen_y = grid_y * tile_size + camera_offset[1]

        # Draw red outline
        pygame.draw.rect(
            screen,
            ToolColors.CURSOR_ERASER,
            (screen_x, screen_y, tile_size, tile_size),
            RenderSettings.CURSOR_HIGHLIGHT_WIDTH,
        )

        # Draw X
        pygame.draw.line(
            screen,
            ToolColors.CURSOR_ERASER,
            (screen_x + RenderSettings.CROSSHAIR_SIZE, screen_y + RenderSettings.CROSSHAIR_SIZE),
            (
                screen_x + tile_size - RenderSettings.CROSSHAIR_SIZE,
                screen_y + tile_size - RenderSettings.CROSSHAIR_SIZE,
            ),
            RenderSettings.CROSSHAIR_WIDTH,
        )
        pygame.draw.line(
            screen,
            ToolColors.CURSOR_ERASER,
            (
                screen_x + tile_size - RenderSettings.CROSSHAIR_SIZE,
                screen_y + RenderSettings.CROSSHAIR_SIZE,
            ),
            (
                screen_x + RenderSettings.CROSSHAIR_SIZE,
                screen_y + tile_size - RenderSettings.CROSSHAIR_SIZE,
            ),
            RenderSettings.CROSSHAIR_WIDTH,
        )
