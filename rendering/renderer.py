"""
2D Renderer

Grid-based 2D rendering system with pygame.
"""

from typing import Callable, Dict, List, Optional, Tuple

import pygame

from neonworks.core.ecs import Entity, GridPosition, Sprite, System, Transform, World
from neonworks.rendering.assets import AssetManager, get_asset_manager
from neonworks.rendering.camera import Camera


class Color:
    """Common colors"""

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 100, 255)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    GRAY = (128, 128, 128)
    DARK_GRAY = (64, 64, 64)
    LIGHT_GRAY = (192, 192, 192)


class Renderer:
    """2D renderer for grid-based games"""

    def __init__(
        self,
        width: int,
        height: int,
        tile_size: int = 32,
        asset_manager: Optional[AssetManager] = None,
    ):
        pygame.init()
        self.width = width
        self.height = height
        self.tile_size = tile_size

        # Create window
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Neon Works")

        # Camera
        self.camera = Camera(width, height, tile_size)

        # Asset manager
        self.asset_manager = asset_manager or get_asset_manager()

        # Rendering layers
        self.layers: Dict[int, List[Callable]] = {}

        # Font for text rendering
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 16)

        # Debug rendering
        self.show_grid = False
        self.show_debug_info = False

        # Sprite cache (sprite component texture -> loaded pygame surface)
        self._sprite_cache: Dict[str, pygame.Surface] = {}

    def clear(self, color: Tuple[int, int, int] = Color.BLACK):
        """Clear the screen"""
        self.screen.fill(color)

    def render_world(self, world: World):
        """Render all entities in the world"""
        # Get all entities with sprite components
        entities = world.get_entities_with_component(Sprite)

        # Sort by layer if they have GridPosition
        def get_layer(entity: Entity) -> int:
            grid_pos = entity.get_component(GridPosition)
            return grid_pos.layer if grid_pos else 0

        entities.sort(key=get_layer)

        # Render each entity
        for entity in entities:
            sprite = entity.get_component(Sprite)
            if not sprite.visible:
                continue

            # Try grid position first, then transform
            grid_pos = entity.get_component(GridPosition)
            if grid_pos:
                self.render_grid_sprite(grid_pos, sprite)
            else:
                transform = entity.get_component(Transform)
                if transform:
                    self.render_sprite(transform, sprite)

    def render_sprite(self, transform: Transform, sprite: Sprite):
        """Render a sprite at a world position"""
        # Convert world position to screen position
        screen_x, screen_y = self.camera.world_to_screen(transform.x, transform.y)

        # If sprite has a texture, load and render it
        if sprite.texture:
            surface = self._get_or_load_sprite(sprite.texture)

            # Scale if needed
            if (
                sprite.width != surface.get_width()
                or sprite.height != surface.get_height()
            ):
                surface = pygame.transform.scale(surface, (sprite.width, sprite.height))

            # Apply color tint if not white
            if sprite.color != (255, 255, 255, 255):
                # Create a colored overlay
                colored_surface = surface.copy()
                colored_surface.fill(
                    sprite.color[:3] + (0,), special_flags=pygame.BLEND_RGBA_MULT
                )
                surface = colored_surface

            # Draw the sprite
            sprite_rect = surface.get_rect(center=(screen_x, screen_y))
            self.screen.blit(surface, sprite_rect)
        else:
            # Fallback to colored rectangle if no texture
            rect = pygame.Rect(
                screen_x - sprite.width // 2,
                screen_y - sprite.height // 2,
                sprite.width,
                sprite.height,
            )
            pygame.draw.rect(self.screen, sprite.color, rect)

    def render_grid_sprite(self, grid_pos: GridPosition, sprite: Sprite):
        """Render a sprite at a grid position"""
        # Convert grid position to screen position
        screen_x, screen_y = self.camera.grid_to_screen(
            grid_pos.grid_x, grid_pos.grid_y
        )

        # If sprite has a texture, load and render it
        if sprite.texture:
            surface = self._get_or_load_sprite(sprite.texture)

            # Scale to tile size
            if (
                surface.get_width() != self.tile_size
                or surface.get_height() != self.tile_size
            ):
                surface = pygame.transform.scale(
                    surface, (self.tile_size, self.tile_size)
                )

            # Apply color tint if not white
            if sprite.color != (255, 255, 255, 255):
                colored_surface = surface.copy()
                colored_surface.fill(
                    sprite.color[:3] + (0,), special_flags=pygame.BLEND_RGBA_MULT
                )
                surface = colored_surface

            # Draw the sprite
            self.screen.blit(surface, (screen_x, screen_y))
        else:
            # Fallback to colored rectangle
            rect = pygame.Rect(screen_x, screen_y, self.tile_size, self.tile_size)
            pygame.draw.rect(self.screen, sprite.color, rect)

            # Draw border
            pygame.draw.rect(self.screen, Color.DARK_GRAY, rect, 1)

    def _get_or_load_sprite(self, texture_path: str) -> pygame.Surface:
        """Get sprite from cache or load it"""
        if texture_path not in self._sprite_cache:
            self._sprite_cache[texture_path] = self.asset_manager.load_sprite(
                texture_path
            )
        return self._sprite_cache[texture_path]

    def render_grid(self, grid_width: int, grid_height: int):
        """Render grid lines"""
        if not self.show_grid:
            return

        # Calculate visible grid range
        min_x, min_y = self.camera.screen_to_grid(0, 0)
        max_x, max_y = self.camera.screen_to_grid(self.width, self.height)

        # Clamp to grid bounds
        min_x = max(0, min_x - 1)
        min_y = max(0, min_y - 1)
        max_x = min(grid_width, max_x + 1)
        max_y = min(grid_height, max_y + 1)

        # Draw vertical lines
        for x in range(min_x, max_x + 1):
            screen_x, _ = self.camera.grid_to_screen(x, 0)
            pygame.draw.line(
                self.screen, Color.DARK_GRAY, (screen_x, 0), (screen_x, self.height)
            )

        # Draw horizontal lines
        for y in range(min_y, max_y + 1):
            _, screen_y = self.camera.grid_to_screen(0, y)
            pygame.draw.line(
                self.screen, Color.DARK_GRAY, (0, screen_y), (self.width, screen_y)
            )

    def render_text(
        self, text: str, x: int, y: int, color: Tuple[int, int, int] = Color.WHITE
    ):
        """Render text at screen position"""
        surface = self.font.render(text, True, color)
        self.screen.blit(surface, (x, y))

    def render_text_world(
        self,
        text: str,
        world_x: float,
        world_y: float,
        color: Tuple[int, int, int] = Color.WHITE,
    ):
        """Render text at world position"""
        screen_x, screen_y = self.camera.world_to_screen(world_x, world_y)
        self.render_text(text, screen_x, screen_y, color)

    def render_rect(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        color: Tuple[int, int, int],
        filled: bool = True,
    ):
        """Render a rectangle at screen position"""
        rect = pygame.Rect(x, y, width, height)
        if filled:
            pygame.draw.rect(self.screen, color, rect)
        else:
            pygame.draw.rect(self.screen, color, rect, 2)

    def render_circle(
        self,
        x: int,
        y: int,
        radius: int,
        color: Tuple[int, int, int],
        filled: bool = True,
    ):
        """Render a circle at screen position"""
        if filled:
            pygame.draw.circle(self.screen, color, (x, y), radius)
        else:
            pygame.draw.circle(self.screen, color, (x, y), radius, 2)

    def render_line(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color: Tuple[int, int, int],
        width: int = 1,
    ):
        """Render a line"""
        pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), width)

    def render_debug_info(self, fps: int, entity_count: int):
        """Render debug information"""
        if not self.show_debug_info:
            return

        y_offset = 10
        line_height = 20

        debug_info = [
            f"FPS: {fps}",
            f"Entities: {entity_count}",
            f"Camera: ({self.camera.x:.1f}, {self.camera.y:.1f}) Zoom: {self.camera.zoom:.2f}",
        ]

        for i, line in enumerate(debug_info):
            self.render_text(line, 10, y_offset + i * line_height, Color.YELLOW)

    def present(self):
        """Present the rendered frame"""
        pygame.display.flip()

    def set_title(self, title: str):
        """Set window title"""
        pygame.display.set_caption(title)


class RenderSystem(System):
    """System for rendering entities"""

    def __init__(self, renderer: Renderer):
        super().__init__()
        self.renderer = renderer
        self.priority = 1000  # Render last

    def update(self, world: World, delta_time: float):
        """Render the world"""
        self.renderer.clear()
        self.renderer.render_world(world)
        self.renderer.present()
