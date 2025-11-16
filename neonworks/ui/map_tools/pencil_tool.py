"""
Pencil tool for painting tiles, entities, and events.
"""

from typing import Optional, Tuple

import pygame

from ...core.ecs import (
    GridPosition,
    Health,
    ResourceStorage,
    Sprite,
    Survival,
    Transform,
    TurnActor,
)
from ...core.event_commands import EventPage, GameEvent
from ...rendering.tilemap import Tile
from .base import MapTool, ToolContext
from .settings import RenderSettings, ToolColors, get_tool_color
from .undo_manager import TileChangeAction


class PencilTool(MapTool):
    """
    Pencil tool for painting tiles, entities, and events.

    Left click paints the selected tile/entity/event.
    Supports drag painting for tiles.
    """

    def __init__(self):
        super().__init__("Pencil", 1, get_tool_color("pencil"))
        self.cursor_type = "pencil"
        self.last_painted_pos: Optional[Tuple[int, int]] = None

    def on_mouse_down(self, grid_x: int, grid_y: int, button: int, context: ToolContext) -> bool:
        if button != 0:  # Left click only
            return False

        self.last_painted_pos = (grid_x, grid_y)
        return self._paint(grid_x, grid_y, context)

    def on_mouse_drag(self, grid_x: int, grid_y: int, button: int, context: ToolContext) -> bool:
        if button != 0:  # Left click only
            return False

        # Avoid painting the same position twice
        if self.last_painted_pos == (grid_x, grid_y):
            return True

        self.last_painted_pos = (grid_x, grid_y)
        return self._paint(grid_x, grid_y, context)

    def on_mouse_up(self, grid_x: int, grid_y: int, button: int, context: ToolContext) -> bool:
        self.last_painted_pos = None
        return False

    def _paint(self, grid_x: int, grid_y: int, context: ToolContext) -> bool:
        """Paint at the given position based on selected item."""
        # Check bounds
        if not (0 <= grid_x < context.grid_width and 0 <= grid_y < context.grid_height):
            return False

        # Paint tile if tile is selected
        if context.selected_tile:
            return self._paint_tile(grid_x, grid_y, context)

        # Paint entity if entity type is selected
        elif context.selected_entity_type:
            return self._paint_entity(grid_x, grid_y, context)

        # Paint event if event template is selected
        elif context.selected_event_template:
            return self._paint_event(grid_x, grid_y, context)

        return False

    def _paint_tile(self, grid_x: int, grid_y: int, context: ToolContext) -> bool:
        """Paint a tile at the given position."""
        if not context.tilemap or not context.selected_tile:
            return False

        tile_data = context.tile_palette.get(context.selected_tile)
        if not tile_data:
            return False

        # Get old tile for undo
        old_tile = context.tilemap.get_tile(grid_x, grid_y, context.current_layer)

        # Create new tile
        new_tile = Tile(tile_type=context.selected_tile, walkable=tile_data["walkable"])

        # Set tile
        context.tilemap.set_tile(grid_x, grid_y, context.current_layer, new_tile)

        # Record undo action
        if context.undo_manager:
            action = TileChangeAction(
                context.tilemap, grid_x, grid_y, context.current_layer, old_tile, new_tile
            )
            context.undo_manager.record_action(action)

        return True

    def _paint_entity(self, grid_x: int, grid_y: int, context: ToolContext) -> bool:
        """Paint an entity at the given position."""
        if not context.selected_entity_type:
            return False

        template = context.entity_templates.get(context.selected_entity_type)
        if not template:
            return False

        # Create entity
        entity_id = context.world.create_entity()

        # Add transform
        context.world.add_component(
            entity_id, Transform(x=grid_x * context.tile_size, y=grid_y * context.tile_size)
        )

        # Add grid position
        context.world.add_component(entity_id, GridPosition(grid_x, grid_y))

        # Add sprite
        context.world.add_component(
            entity_id,
            Sprite(asset_id=f"entity_{context.selected_entity_type}", color=template["color"]),
        )

        # Add components based on template
        if "Health" in template["components"]:
            context.world.add_component(entity_id, Health(current=100, maximum=100))

        if "Survival" in template["components"]:
            context.world.add_component(entity_id, Survival())

        if "TurnActor" in template["components"]:
            context.world.add_component(entity_id, TurnActor(initiative=10))

        if "ResourceStorage" in template["components"]:
            context.world.add_component(entity_id, ResourceStorage(capacity=50))

        # Add tags
        for tag in template["tags"]:
            context.world.tag_entity(entity_id, tag)

        print(f"Placed {template['name']} at ({grid_x}, {grid_y})")
        return True

    def _paint_event(self, grid_x: int, grid_y: int, context: ToolContext) -> bool:
        """Paint an event at the given position."""
        if not context.selected_event_template:
            return False

        # Check if event already exists at this position
        for existing_event in context.events:
            if existing_event.x == grid_x and existing_event.y == grid_y:
                print(f"Event already exists at ({grid_x}, {grid_y})")
                return False

        template = context.event_templates.get(context.selected_event_template)
        if not template:
            return False

        # Generate new event ID
        new_id = max([e.id for e in context.events], default=0) + 1

        # Create event with default page
        new_event = GameEvent(
            id=new_id,
            name=f"{template['name']} {new_id:03d}",
            x=grid_x,
            y=grid_y,
            pages=[],
        )

        # Add metadata for rendering
        new_event.color = template["color"]
        new_event.icon = template["icon"]
        new_event.template_type = context.selected_event_template

        # Add a default page
        default_page = EventPage(
            trigger=template["trigger"],
            commands=[],
        )
        new_event.pages.append(default_page)

        context.events.append(new_event)
        print(f"Placed {template['name']} at ({grid_x}, {grid_y}) with ID #{new_id}")

        # Sync events to event editor if available
        if context.event_editor:
            context.event_editor.load_events_from_scene(context.events)

        return True

    def render_cursor(
        self,
        screen: pygame.Surface,
        grid_x: int,
        grid_y: int,
        tile_size: int,
        camera_offset: Tuple[int, int],
    ):
        """Render pencil cursor."""
        screen_x = grid_x * tile_size + camera_offset[0]
        screen_y = grid_y * tile_size + camera_offset[1]

        # Draw green outline
        pygame.draw.rect(
            screen,
            ToolColors.CURSOR_PENCIL,
            (screen_x, screen_y, tile_size, tile_size),
            RenderSettings.CURSOR_HIGHLIGHT_WIDTH,
        )

        # Draw crosshair
        center_x = screen_x + tile_size // 2
        center_y = screen_y + tile_size // 2
        pygame.draw.line(
            screen,
            ToolColors.CURSOR_PENCIL,
            (center_x - RenderSettings.CROSSHAIR_SIZE, center_y),
            (center_x + RenderSettings.CROSSHAIR_SIZE, center_y),
            RenderSettings.CROSSHAIR_WIDTH,
        )
        pygame.draw.line(
            screen,
            ToolColors.CURSOR_PENCIL,
            (center_x, center_y - RenderSettings.CROSSHAIR_SIZE),
            (center_x, center_y + RenderSettings.CROSSHAIR_SIZE),
            RenderSettings.CROSSHAIR_WIDTH,
        )
