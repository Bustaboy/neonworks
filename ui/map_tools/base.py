"""
Base classes for map editing tools.

Defines the core interfaces and context for map tools.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

import pygame

from ...core.ecs import World
from ...core.event_commands import GameEvent
from ...rendering.tilemap import Tilemap
from .settings import RenderSettings, ToolColors


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

        pygame.draw.rect(
            screen,
            ToolColors.CURSOR_DEFAULT,
            (screen_x, screen_y, tile_size, tile_size),
            RenderSettings.CURSOR_OUTLINE_WIDTH,
        )


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
        undo_manager=None,
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
        self.undo_manager = undo_manager


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
