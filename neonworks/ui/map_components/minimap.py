"""
Minimap Component - Overview minimap with click-to-navigate functionality

Provides a bird's-eye view of the entire map with:
- Real-time minimap rendering
- Click-to-navigate to map location
- Viewport indicator showing current view
- Zoom controls
- Toggle visibility
- Entity and event markers
"""

from typing import Optional, Tuple

import pygame

from neonworks.core.ecs import World
from neonworks.rendering.tilemap import Tilemap


class MinimapUI:
    """
    Minimap overlay that displays the entire map and allows click-to-navigate.

    Features:
    - Renders entire map at reduced scale
    - Shows current viewport as a rectangle
    - Click to navigate to any location
    - Displays entities and events as colored dots
    - Zoom in/out controls
    - Toggle grid display
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int = 200,
        height: int = 200,
        on_navigate: Optional[callable] = None,
    ):
        """
        Initialize the minimap.

        Args:
            x: X position on screen
            y: Y position on screen
            width: Minimap width in pixels
            height: Minimap height in pixels
            on_navigate: Callback when user clicks to navigate (grid_x, grid_y)
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.on_navigate = on_navigate

        # State
        self.visible = True
        self.show_grid = False
        self.show_entities = True
        self.show_events = True
        self.zoom_level = 1.0

        # References
        self.tilemap: Optional[Tilemap] = None
        self.world: Optional[World] = None

        # Viewport tracking
        self.viewport_x = 0
        self.viewport_y = 0
        self.viewport_width = 0
        self.viewport_height = 0

        # UI state
        self.dragging = False
        self.hover_pos: Optional[Tuple[int, int]] = None

        # Colors
        self.bg_color = (30, 30, 35)
        self.border_color = (80, 80, 85)
        self.viewport_color = (255, 255, 0, 100)
        self.grid_color = (60, 60, 65)
        self.entity_color = (0, 200, 255)
        self.event_color = (255, 100, 200)

        # Fonts
        self.font = pygame.font.Font(None, 14)

        # Surface cache
        self.minimap_surface: Optional[pygame.Surface] = None
        self.needs_redraw = True

    def set_tilemap(self, tilemap: Tilemap):
        """
        Set the tilemap to display.

        Args:
            tilemap: Tilemap instance to render
        """
        self.tilemap = tilemap
        self.needs_redraw = True

    def set_world(self, world: World):
        """
        Set the world for entity display.

        Args:
            world: World instance containing entities
        """
        self.world = world
        self.needs_redraw = True

    def set_viewport(self, x: int, y: int, width: int, height: int):
        """
        Update the viewport indicator position.

        Args:
            x: Viewport X position in grid coordinates
            y: Viewport Y position in grid coordinates
            width: Viewport width in grid cells
            height: Viewport height in grid cells
        """
        self.viewport_x = x
        self.viewport_y = y
        self.viewport_width = width
        self.viewport_height = height

    def toggle_visibility(self):
        """Toggle minimap visibility."""
        self.visible = not self.visible

    def toggle_grid(self):
        """Toggle grid display."""
        self.show_grid = not self.show_grid
        self.needs_redraw = True

    def toggle_entities(self):
        """Toggle entity markers."""
        self.show_entities = not self.show_entities
        self.needs_redraw = True

    def toggle_events(self):
        """Toggle event markers."""
        self.show_events = not self.show_events
        self.needs_redraw = True

    def zoom_in(self):
        """Increase zoom level."""
        self.zoom_level = min(self.zoom_level + 0.25, 3.0)
        self.needs_redraw = True

    def zoom_out(self):
        """Decrease zoom level."""
        self.zoom_level = max(self.zoom_level - 0.25, 0.25)
        self.needs_redraw = True

    def update(self, dt: float):
        """
        Update minimap state.

        Args:
            dt: Delta time in seconds
        """
        if not self.visible:
            return

        # Update hover position
        mouse_pos = pygame.mouse.get_pos()
        if self._is_point_inside(mouse_pos[0], mouse_pos[1]):
            self.hover_pos = self._screen_to_grid(mouse_pos[0], mouse_pos[1])
        else:
            self.hover_pos = None

    def render(self, screen: pygame.Surface):
        """
        Render the minimap.

        Args:
            screen: Surface to render on
        """
        if not self.visible or not self.tilemap:
            return

        # Redraw minimap if needed
        if self.needs_redraw:
            self._redraw_minimap()
            self.needs_redraw = False

        # Draw background
        pygame.draw.rect(screen, self.bg_color, (self.x, self.y, self.width, self.height))

        # Draw minimap surface
        if self.minimap_surface:
            screen.blit(self.minimap_surface, (self.x, self.y))

        # Draw viewport indicator
        self._draw_viewport(screen)

        # Draw hover indicator
        if self.hover_pos:
            self._draw_hover_indicator(screen)

        # Draw border
        pygame.draw.rect(screen, self.border_color, (self.x, self.y, self.width, self.height), 2)

        # Draw controls
        self._draw_controls(screen)

    def _redraw_minimap(self):
        """Redraw the minimap surface."""
        if not self.tilemap:
            return

        # Create surface
        self.minimap_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.minimap_surface.fill(self.bg_color)

        # Calculate scale
        scale_x = self.width / (self.tilemap.width * self.zoom_level)
        scale_y = self.height / (self.tilemap.height * self.zoom_level)
        scale = min(scale_x, scale_y)

        # Draw tiles
        if hasattr(self.tilemap, "get_layer_count"):
            layer_count = self.tilemap.get_layer_count()  # type: ignore[attr-defined]
        else:
            layer_count = 0

        for layer in range(layer_count):
            alpha = 255 if layer == 0 else 180
            for y in range(self.tilemap.height):
                for x in range(self.tilemap.width):
                    tile = self.tilemap.get_tile(x, y, layer)
                    if tile:
                        # Calculate pixel position
                        px = int(x * scale)
                        py = int(y * scale)
                        pw = max(1, int(scale))
                        ph = max(1, int(scale))

                        # Get tile color (simplified)
                        color = self._get_tile_color(tile)
                        color_with_alpha = (*color, alpha)

                        # Draw tile pixel
                        pygame.draw.rect(
                            self.minimap_surface,
                            color_with_alpha,
                            (px, py, pw, ph),
                        )

        # Draw grid if enabled
        if self.show_grid:
            self._draw_grid_on_surface(self.minimap_surface, scale)

        # Draw entities
        if self.show_entities and self.world:
            self._draw_entities_on_surface(self.minimap_surface, scale)

    def _get_tile_color(self, tile) -> Tuple[int, int, int]:
        """
        Get color for a tile.

        Args:
            tile: Tile instance

        Returns:
            RGB color tuple
        """
        # Default color based on walkability
        if hasattr(tile, "walkable"):
            if tile.walkable:
                return (100, 200, 100)  # Green for walkable
            else:
                return (100, 100, 150)  # Blue for non-walkable

        # Default gray
        return (128, 128, 128)

    def _draw_grid_on_surface(self, surface: pygame.Surface, scale: float):
        """Draw grid lines on the minimap surface."""
        if not self.tilemap:
            return

        grid_color = (*self.grid_color, 100)

        # Draw vertical lines
        for x in range(0, self.tilemap.width + 1, 5):
            px = int(x * scale)
            pygame.draw.line(surface, grid_color, (px, 0), (px, self.height), 1)

        # Draw horizontal lines
        for y in range(0, self.tilemap.height + 1, 5):
            py = int(y * scale)
            pygame.draw.line(surface, grid_color, (0, py), (self.width, py), 1)

    def _draw_entities_on_surface(self, surface: pygame.Surface, scale: float):
        """Draw entity markers on the minimap surface."""
        if not self.world:
            return

        from neonworks.core.ecs import GridPosition

        for entity in self.world.entities:
            if entity.has_component(GridPosition):
                grid_pos = entity.get_component(GridPosition)
                px = int(grid_pos.x * scale)
                py = int(grid_pos.y * scale)

                # Draw entity dot
                pygame.draw.circle(surface, self.entity_color, (px, py), 2)

    def _draw_viewport(self, screen: pygame.Surface):
        """Draw the viewport indicator rectangle."""
        if not self.tilemap:
            return

        scale_x = self.width / (self.tilemap.width * self.zoom_level)
        scale_y = self.height / (self.tilemap.height * self.zoom_level)
        scale = min(scale_x, scale_y)

        vp_x = self.x + int(self.viewport_x * scale)
        vp_y = self.y + int(self.viewport_y * scale)
        vp_w = int(self.viewport_width * scale)
        vp_h = int(self.viewport_height * scale)

        # Draw semi-transparent viewport rectangle
        viewport_surface = pygame.Surface((vp_w, vp_h), pygame.SRCALPHA)
        viewport_surface.fill(self.viewport_color)
        screen.blit(viewport_surface, (vp_x, vp_y))

        # Draw viewport border
        pygame.draw.rect(screen, (255, 255, 0), (vp_x, vp_y, vp_w, vp_h), 1)

    def _draw_hover_indicator(self, screen: pygame.Surface):
        """Draw hover indicator at mouse position."""
        if not self.hover_pos or not self.tilemap:
            return

        scale_x = self.width / (self.tilemap.width * self.zoom_level)
        scale_y = self.height / (self.tilemap.height * self.zoom_level)
        scale = min(scale_x, scale_y)

        hx = self.x + int(self.hover_pos[0] * scale)
        hy = self.y + int(self.hover_pos[1] * scale)

        # Draw crosshair
        pygame.draw.line(screen, (255, 255, 255), (hx - 5, hy), (hx + 5, hy), 1)
        pygame.draw.line(screen, (255, 255, 255), (hx, hy - 5), (hx, hy + 5), 1)

    def _draw_controls(self, screen: pygame.Surface):
        """Draw minimap controls (zoom buttons, etc.)."""
        button_y = self.y + self.height + 5
        button_size = 20
        button_spacing = 5

        # Zoom in button
        zoom_in_rect = pygame.Rect(self.x, button_y, button_size, button_size)
        pygame.draw.rect(screen, (60, 60, 65), zoom_in_rect)
        pygame.draw.rect(screen, self.border_color, zoom_in_rect, 1)
        plus_text = self.font.render("+", True, (220, 220, 220))
        screen.blit(plus_text, (self.x + 6, button_y + 2))

        # Zoom out button
        zoom_out_rect = pygame.Rect(
            self.x + button_size + button_spacing, button_y, button_size, button_size
        )
        pygame.draw.rect(screen, (60, 60, 65), zoom_out_rect)
        pygame.draw.rect(screen, self.border_color, zoom_out_rect, 1)
        minus_text = self.font.render("-", True, (220, 220, 220))
        screen.blit(minus_text, (self.x + button_size + button_spacing + 7, button_y + 2))

        # Grid toggle button
        grid_button_rect = pygame.Rect(
            self.x + (button_size + button_spacing) * 2, button_y, button_size, button_size
        )
        grid_color = (100, 150, 255) if self.show_grid else (60, 60, 65)
        pygame.draw.rect(screen, grid_color, grid_button_rect)
        pygame.draw.rect(screen, self.border_color, grid_button_rect, 1)
        grid_text = self.font.render("G", True, (220, 220, 220))
        screen.blit(grid_text, (self.x + (button_size + button_spacing) * 2 + 5, button_y + 2))

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle input events.

        Args:
            event: Pygame event

        Returns:
            True if event was handled, False otherwise
        """
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos

            # Check zoom buttons
            button_y = self.y + self.height + 5
            button_size = 20
            button_spacing = 5

            # Zoom in button
            if (
                self.x <= mouse_x <= self.x + button_size
                and button_y <= mouse_y <= button_y + button_size
            ):
                self.zoom_in()
                return True

            # Zoom out button
            if (
                self.x + button_size + button_spacing
                <= mouse_x
                <= self.x + (button_size + button_spacing) * 2
                and button_y <= mouse_y <= button_y + button_size
            ):
                self.zoom_out()
                return True

            # Grid toggle button
            if (
                self.x + (button_size + button_spacing) * 2
                <= mouse_x
                <= self.x + (button_size + button_spacing) * 3
                and button_y <= mouse_y <= button_y + button_size
            ):
                self.toggle_grid()
                return True

            # Check if click is on minimap
            if self._is_point_inside(mouse_x, mouse_y):
                grid_pos = self._screen_to_grid(mouse_x, mouse_y)
                if grid_pos and self.on_navigate:
                    self.on_navigate(grid_pos[0], grid_pos[1])
                    return True

        return False

    def _is_point_inside(self, x: int, y: int) -> bool:
        """Check if a point is inside the minimap bounds."""
        return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height

    def _screen_to_grid(self, screen_x: int, screen_y: int) -> Optional[Tuple[int, int]]:
        """
        Convert screen coordinates to grid coordinates.

        Args:
            screen_x: Screen X coordinate
            screen_y: Screen Y coordinate

        Returns:
            (grid_x, grid_y) or None if outside bounds
        """
        if not self.tilemap:
            return None

        # Convert to minimap-local coordinates
        local_x = screen_x - self.x
        local_y = screen_y - self.y

        # Calculate scale
        scale_x = self.width / (self.tilemap.width * self.zoom_level)
        scale_y = self.height / (self.tilemap.height * self.zoom_level)
        scale = min(scale_x, scale_y)

        # Convert to grid coordinates
        grid_x = int(local_x / scale)
        grid_y = int(local_y / scale)

        # Validate bounds
        if 0 <= grid_x < self.tilemap.width and 0 <= grid_y < self.tilemap.height:
            return (grid_x, grid_y)

        return None
