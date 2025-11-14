"""
Map editing tools for the level builder.

Provides a tool architecture for map editing operations including
pencil, eraser, fill, and selection tools.
"""

from abc import ABC, abstractmethod
from collections import deque
from typing import Dict, List, Optional, Set, Tuple

import pygame

from ..core.ecs import (
    GridPosition,
    Health,
    ResourceStorage,
    Sprite,
    Survival,
    Transform,
    TurnActor,
    World,
)
from ..core.event_commands import EventCommand, EventPage, GameEvent, TriggerType
from ..rendering.tilemap import Tile, Tilemap


class MapTool(ABC):
    """
    Base class for map editing tools.

    Defines the interface that all map tools must implement.
    Each tool handles mouse events and performs specific editing operations.
    """

    def __init__(self, name: str, hotkey: int, color: Tuple[int, int, int]):
        """
        Initialize the map tool.

        Args:
            name: Display name of the tool
            hotkey: Keyboard key number (1-9) for quick selection
            color: RGB color for tool button highlighting
        """
        self.name = name
        self.hotkey = hotkey
        self.color = color
        self.cursor_type = "default"

    @abstractmethod
    def on_mouse_down(self, grid_x: int, grid_y: int, button: int, context: "ToolContext") -> bool:
        """
        Handle mouse button press.

        Args:
            grid_x: Grid X coordinate
            grid_y: Grid Y coordinate
            button: Mouse button (0=left, 2=right)
            context: Tool context with tilemap, world, etc.

        Returns:
            True if the tool handled the event, False otherwise
        """
        pass

    @abstractmethod
    def on_mouse_drag(self, grid_x: int, grid_y: int, button: int, context: "ToolContext") -> bool:
        """
        Handle mouse drag (mouse move while button pressed).

        Args:
            grid_x: Grid X coordinate
            grid_y: Grid Y coordinate
            button: Mouse button being held
            context: Tool context with tilemap, world, etc.

        Returns:
            True if the tool handled the event, False otherwise
        """
        pass

    @abstractmethod
    def on_mouse_up(self, grid_x: int, grid_y: int, button: int, context: "ToolContext") -> bool:
        """
        Handle mouse button release.

        Args:
            grid_x: Grid X coordinate
            grid_y: Grid Y coordinate
            button: Mouse button released
            context: Tool context with tilemap, world, etc.

        Returns:
            True if the tool handled the event, False otherwise
        """
        pass

    def render_cursor(
        self,
        screen: pygame.Surface,
        grid_x: int,
        grid_y: int,
        tile_size: int,
        camera_offset: Tuple[int, int],
    ):
        """
        Render custom cursor for this tool.

        Args:
            screen: Surface to render to
            grid_x: Grid X coordinate of cursor
            grid_y: Grid Y coordinate of cursor
            tile_size: Size of one tile in pixels
            camera_offset: Camera offset (x, y)
        """
        # Default: draw a simple outline
        screen_x = grid_x * tile_size + camera_offset[0]
        screen_y = grid_y * tile_size + camera_offset[1]

        pygame.draw.rect(screen, (255, 255, 255), (screen_x, screen_y, tile_size, tile_size), 2)


class ToolContext:
    """
    Context object providing access to editor state for tools.

    Tools receive this context when handling events, allowing them
    to modify the tilemap, world, events, etc.
    """

    def __init__(
        self,
        tilemap: Optional[Tilemap],
        world: World,
        events: List[GameEvent],
        tile_palette: Dict,
        entity_templates: Dict,
        event_templates: Dict,
        current_layer: int,
        selected_tile: Optional[str],
        selected_entity_type: Optional[str],
        selected_event_template: Optional[str],
        grid_width: int,
        grid_height: int,
        tile_size: int,
        event_editor=None,
    ):
        """Initialize tool context with editor state."""
        self.tilemap = tilemap
        self.world = world
        self.events = events
        self.tile_palette = tile_palette
        self.entity_templates = entity_templates
        self.event_templates = event_templates
        self.current_layer = current_layer
        self.selected_tile = selected_tile
        self.selected_entity_type = selected_entity_type
        self.selected_event_template = selected_event_template
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.tile_size = tile_size
        self.event_editor = event_editor


class PencilTool(MapTool):
    """
    Pencil tool for painting tiles, entities, and events.

    Left click paints the selected tile/entity/event.
    Supports drag painting for tiles.
    """

    def __init__(self):
        super().__init__("Pencil", 1, (0, 150, 0))
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

        tile = Tile(tile_type=context.selected_tile, walkable=tile_data["walkable"])
        context.tilemap.set_tile(grid_x, grid_y, context.current_layer, tile)
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
        pygame.draw.rect(screen, (0, 255, 0), (screen_x, screen_y, tile_size, tile_size), 3)

        # Draw crosshair
        center_x = screen_x + tile_size // 2
        center_y = screen_y + tile_size // 2
        pygame.draw.line(screen, (0, 255, 0), (center_x - 5, center_y), (center_x + 5, center_y), 2)
        pygame.draw.line(screen, (0, 255, 0), (center_x, center_y - 5), (center_x, center_y + 5), 2)


class EraserTool(MapTool):
    """
    Eraser tool for removing tiles, entities, and events.

    Left click erases tile/entity/event at the position.
    Supports drag erasing.
    """

    def __init__(self):
        super().__init__("Eraser", 2, (150, 0, 0))
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
            tile = context.tilemap.get_tile(grid_x, grid_y, context.current_layer)
            if tile:
                context.tilemap.set_tile(grid_x, grid_y, context.current_layer, None)
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
        pygame.draw.rect(screen, (255, 0, 0), (screen_x, screen_y, tile_size, tile_size), 3)

        # Draw X
        pygame.draw.line(
            screen,
            (255, 0, 0),
            (screen_x + 5, screen_y + 5),
            (screen_x + tile_size - 5, screen_y + tile_size - 5),
            2,
        )
        pygame.draw.line(
            screen,
            (255, 0, 0),
            (screen_x + tile_size - 5, screen_y + 5),
            (screen_x + 5, screen_y + tile_size - 5),
            2,
        )


class FillTool(MapTool):
    """
    Fill tool for flood filling tiles.

    Left click fills contiguous region of same tile type with selected tile.
    Only works for tiles, not entities or events.
    """

    def __init__(self):
        super().__init__("Fill", 3, (0, 150, 150))
        self.cursor_type = "fill"

    def on_mouse_down(self, grid_x: int, grid_y: int, button: int, context: ToolContext) -> bool:
        if button != 0:  # Left click only
            return False

        return self._flood_fill(grid_x, grid_y, context)

    def on_mouse_drag(self, grid_x: int, grid_y: int, button: int, context: ToolContext) -> bool:
        # Fill tool doesn't support dragging
        return False

    def on_mouse_up(self, grid_x: int, grid_y: int, button: int, context: ToolContext) -> bool:
        return False

    def _flood_fill(self, start_x: int, start_y: int, context: ToolContext) -> bool:
        """Perform flood fill starting from the given position."""
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

        # Perform flood fill using BFS
        tile_data = context.tile_palette.get(new_tile_type)
        if not tile_data:
            return False

        new_tile = Tile(tile_type=new_tile_type, walkable=tile_data["walkable"])

        visited: Set[Tuple[int, int]] = set()
        queue: deque = deque([(start_x, start_y)])
        visited.add((start_x, start_y))
        fill_count = 0

        while queue:
            x, y = queue.popleft()

            # Check if this position has the original tile type
            current_tile = context.tilemap.get_tile(x, y, context.current_layer)
            current_type = current_tile.tile_type if current_tile else None

            if current_type != original_type:
                continue

            # Fill this position
            context.tilemap.set_tile(x, y, context.current_layer, new_tile)
            fill_count += 1

            # Add neighbors to queue
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy

                if (
                    0 <= nx < context.grid_width
                    and 0 <= ny < context.grid_height
                    and (nx, ny) not in visited
                ):
                    visited.add((nx, ny))
                    queue.append((nx, ny))

        print(f"Filled {fill_count} tiles with {new_tile_type}")
        return fill_count > 0

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
        pygame.draw.circle(
            screen,
            (0, 255, 255),
            (screen_x + tile_size // 2, screen_y + tile_size // 2),
            tile_size // 4,
            2,
        )


class SelectTool(MapTool):
    """
    Selection tool for selecting rectangular regions.

    Left click and drag to select a region.
    Selected region can be copied, cut, or transformed (future).
    """

    def __init__(self):
        super().__init__("Select", 4, (150, 150, 0))
        self.cursor_type = "select"
        self.selection_start: Optional[Tuple[int, int]] = None
        self.selection_end: Optional[Tuple[int, int]] = None
        self.is_selecting = False

    def on_mouse_down(self, grid_x: int, grid_y: int, button: int, context: ToolContext) -> bool:
        if button != 0:  # Left click only
            return False

        self.selection_start = (grid_x, grid_y)
        self.selection_end = (grid_x, grid_y)
        self.is_selecting = True
        return True

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

    def get_selection_bounds(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Get the bounds of the current selection.

        Returns:
            Tuple of (min_x, min_y, max_x, max_y) or None if no selection
        """
        if not self.selection_start or not self.selection_end:
            return None

        min_x = min(self.selection_start[0], self.selection_end[0])
        max_x = max(self.selection_start[0], self.selection_end[0])
        min_y = min(self.selection_start[1], self.selection_end[1])
        max_y = max(self.selection_start[1], self.selection_end[1])

        return (min_x, min_y, max_x, max_y)

    def clear_selection(self):
        """Clear the current selection."""
        self.selection_start = None
        self.selection_end = None
        self.is_selecting = False

    def render_cursor(
        self,
        screen: pygame.Surface,
        grid_x: int,
        grid_y: int,
        tile_size: int,
        camera_offset: Tuple[int, int],
    ):
        """Render selection cursor and selection box."""
        # Render current selection box if selecting
        if self.selection_start and self.selection_end:
            min_x = min(self.selection_start[0], self.selection_end[0])
            max_x = max(self.selection_start[0], self.selection_end[0])
            min_y = min(self.selection_start[1], self.selection_end[1])
            max_y = max(self.selection_start[1], self.selection_end[1])

            screen_x = min_x * tile_size + camera_offset[0]
            screen_y = min_y * tile_size + camera_offset[1]
            width = (max_x - min_x + 1) * tile_size
            height = (max_y - min_y + 1) * tile_size

            # Draw selection box
            pygame.draw.rect(screen, (255, 255, 0), (screen_x, screen_y, width, height), 2)

            # Draw semi-transparent overlay
            overlay = pygame.Surface((width, height), pygame.SRCALPHA)
            overlay.fill((255, 255, 0, 50))
            screen.blit(overlay, (screen_x, screen_y))

        # Draw cursor
        screen_x = grid_x * tile_size + camera_offset[0]
        screen_y = grid_y * tile_size + camera_offset[1]

        pygame.draw.rect(screen, (255, 255, 0), (screen_x, screen_y, tile_size, tile_size), 2)


class ToolManager:
    """
    Manages map editing tools and tool switching.

    Handles tool registration, switching between tools,
    and dispatching mouse events to the active tool.
    """

    def __init__(self):
        """Initialize the tool manager."""
        self.tools: Dict[str, MapTool] = {}
        self.active_tool: Optional[MapTool] = None
        self.tool_order: List[str] = []

    def register_tool(self, tool_id: str, tool: MapTool):
        """
        Register a tool with the manager.

        Args:
            tool_id: Unique identifier for the tool
            tool: MapTool instance to register
        """
        self.tools[tool_id] = tool
        self.tool_order.append(tool_id)

        # Set first tool as active if no active tool
        if self.active_tool is None:
            self.active_tool = tool

    def set_active_tool(self, tool_id: str) -> bool:
        """
        Set the active tool by ID.

        Args:
            tool_id: ID of the tool to activate

        Returns:
            True if tool was activated, False if tool not found
        """
        if tool_id in self.tools:
            self.active_tool = self.tools[tool_id]
            print(f"Switched to {self.active_tool.name} tool")
            return True
        return False

    def get_active_tool(self) -> Optional[MapTool]:
        """Get the currently active tool."""
        return self.active_tool

    def get_tool_by_hotkey(self, hotkey: int) -> Optional[MapTool]:
        """
        Get tool by its hotkey number.

        Args:
            hotkey: Hotkey number (1-9)

        Returns:
            MapTool instance or None if not found
        """
        for tool in self.tools.values():
            if tool.hotkey == hotkey:
                return tool
        return None

    def handle_mouse_down(
        self, grid_x: int, grid_y: int, button: int, context: ToolContext
    ) -> bool:
        """
        Handle mouse down event with active tool.

        Args:
            grid_x: Grid X coordinate
            grid_y: Grid Y coordinate
            button: Mouse button pressed
            context: Tool context

        Returns:
            True if event was handled, False otherwise
        """
        if self.active_tool:
            return self.active_tool.on_mouse_down(grid_x, grid_y, button, context)
        return False

    def handle_mouse_drag(
        self, grid_x: int, grid_y: int, button: int, context: ToolContext
    ) -> bool:
        """
        Handle mouse drag event with active tool.

        Args:
            grid_x: Grid X coordinate
            grid_y: Grid Y coordinate
            button: Mouse button being held
            context: Tool context

        Returns:
            True if event was handled, False otherwise
        """
        if self.active_tool:
            return self.active_tool.on_mouse_drag(grid_x, grid_y, button, context)
        return False

    def handle_mouse_up(self, grid_x: int, grid_y: int, button: int, context: ToolContext) -> bool:
        """
        Handle mouse up event with active tool.

        Args:
            grid_x: Grid X coordinate
            grid_y: Grid Y coordinate
            button: Mouse button released
            context: Tool context

        Returns:
            True if event was handled, False otherwise
        """
        if self.active_tool:
            return self.active_tool.on_mouse_up(grid_x, grid_y, button, context)
        return False

    def render_cursor(
        self,
        screen: pygame.Surface,
        grid_x: int,
        grid_y: int,
        tile_size: int,
        camera_offset: Tuple[int, int],
    ):
        """
        Render cursor for active tool.

        Args:
            screen: Surface to render to
            grid_x: Grid X coordinate
            grid_y: Grid Y coordinate
            tile_size: Size of one tile in pixels
            camera_offset: Camera offset (x, y)
        """
        if self.active_tool:
            self.active_tool.render_cursor(screen, grid_x, grid_y, tile_size, camera_offset)
