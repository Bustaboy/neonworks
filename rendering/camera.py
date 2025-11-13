"""
Camera System

2D camera with pan, zoom, entity tracking, shake, bounds, and effects.
"""

from typing import Tuple, Optional, List
from enum import Enum
import random
import math
from neonworks.core.ecs import Entity, Transform, GridPosition


class EaseType(Enum):
    """Easing functions for smooth camera movement"""

    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"


class Camera:
    """2D camera for grid-based games with advanced features"""

    def __init__(self, screen_width: int, screen_height: int, tile_size: int = 32):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.tile_size = tile_size

        # Camera position (world coordinates)
        self.x = 0.0
        self.y = 0.0

        # Camera zoom (1.0 = normal, 2.0 = 2x zoom)
        self.zoom = 1.0
        self.min_zoom = 0.25
        self.max_zoom = 4.0

        # Camera tracking
        self.tracking_entity: Optional[Entity] = None
        self.tracking_entities: List[Entity] = []  # Multi-target tracking
        self.tracking_offset_x = 0.0
        self.tracking_offset_y = 0.0

        # Camera smoothing
        self.smoothing = 0.1  # 0 = instant, 1 = very smooth
        self.target_x = 0.0
        self.target_y = 0.0
        self.target_zoom = 1.0

        # Camera bounds (world coordinates)
        self.bounds_enabled = False
        self.bounds_min_x = 0.0
        self.bounds_min_y = 0.0
        self.bounds_max_x = 0.0
        self.bounds_max_y = 0.0

        # Camera shake
        self.shake_intensity = 0.0
        self.shake_duration = 0.0
        self.shake_decay = 1.0  # Multiplier per second
        self.shake_frequency = 30.0  # Hz
        self.shake_offset_x = 0.0
        self.shake_offset_y = 0.0

        # Deadzone tracking
        self.deadzone_enabled = False
        self.deadzone_width = 0.0
        self.deadzone_height = 0.0

        # Look-ahead (camera leads in direction of movement)
        self.lookahead_enabled = False
        self.lookahead_distance = 50.0
        self.lookahead_smoothing = 0.5

    @property
    def width(self) -> int:
        """Get camera viewport width"""
        return self.screen_width

    @property
    def height(self) -> int:
        """Get camera viewport height"""
        return self.screen_height

    def update(self, delta_time: float):
        """Update camera (smoothing, tracking, shake, bounds)"""
        # Update shake
        if self.shake_duration > 0:
            self.shake_duration -= delta_time
            if self.shake_duration <= 0:
                self.shake_duration = 0
                self.shake_intensity = 0
                self.shake_offset_x = 0
                self.shake_offset_y = 0
            else:
                # Decay shake intensity over time
                self.shake_intensity *= pow(self.shake_decay, delta_time)

                # Apply shake with noise
                angle = random.uniform(0, 2 * math.pi)
                self.shake_offset_x = math.cos(angle) * self.shake_intensity
                self.shake_offset_y = math.sin(angle) * self.shake_intensity

        # Update multi-target tracking
        if self.tracking_entities:
            # Calculate average position of all tracked entities
            total_x = 0.0
            total_y = 0.0
            count = 0

            for entity in self.tracking_entities:
                if not entity.active:
                    continue

                grid_pos = entity.get_component(GridPosition)
                if grid_pos:
                    world_x = grid_pos.grid_x * self.tile_size + self.tile_size / 2
                    world_y = grid_pos.grid_y * self.tile_size + self.tile_size / 2
                else:
                    transform = entity.get_component(Transform)
                    if not transform:
                        continue
                    world_x = transform.x
                    world_y = transform.y

                total_x += world_x
                total_y += world_y
                count += 1

            if count > 0:
                avg_x = total_x / count
                avg_y = total_y / count
                self.target_x = avg_x + self.tracking_offset_x
                self.target_y = avg_y + self.tracking_offset_y

        # Update single entity tracking
        elif self.tracking_entity and self.tracking_entity.active:
            grid_pos = self.tracking_entity.get_component(GridPosition)
            if grid_pos:
                world_x = grid_pos.grid_x * self.tile_size + self.tile_size / 2
                world_y = grid_pos.grid_y * self.tile_size + self.tile_size / 2
            else:
                transform = self.tracking_entity.get_component(Transform)
                if transform:
                    world_x = transform.x
                    world_y = transform.y
                else:
                    world_x, world_y = self.target_x, self.target_y

            # Apply deadzone
            if self.deadzone_enabled:
                dx = world_x - self.x
                dy = world_y - self.y

                # Only move camera if entity is outside deadzone
                if abs(dx) > self.deadzone_width / 2:
                    self.target_x = world_x + self.tracking_offset_x
                if abs(dy) > self.deadzone_height / 2:
                    self.target_y = world_y + self.tracking_offset_y
            else:
                self.target_x = world_x + self.tracking_offset_x
                self.target_y = world_y + self.tracking_offset_y

        # Apply bounds
        if self.bounds_enabled:
            # Calculate camera edges in world space
            half_view_width = (self.screen_width / 2) / self.zoom
            half_view_height = (self.screen_height / 2) / self.zoom

            # Clamp target position
            self.target_x = max(
                self.bounds_min_x + half_view_width,
                min(self.bounds_max_x - half_view_width, self.target_x),
            )
            self.target_y = max(
                self.bounds_min_y + half_view_height,
                min(self.bounds_max_y - half_view_height, self.target_y),
            )

        # Apply smoothing
        if self.smoothing > 0:
            smooth_factor = 1.0 - pow(self.smoothing, delta_time * 60)
            self.x += (self.target_x - self.x) * smooth_factor
            self.y += (self.target_y - self.y) * smooth_factor
            self.zoom += (self.target_zoom - self.zoom) * smooth_factor
        else:
            self.x = self.target_x
            self.y = self.target_y
            self.zoom = self.target_zoom

    def world_to_screen(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates (with shake)"""
        screen_x = (
            world_x - self.x - self.shake_offset_x
        ) * self.zoom + self.screen_width / 2
        screen_y = (
            world_y - self.y - self.shake_offset_y
        ) * self.zoom + self.screen_height / 2
        return int(screen_x), int(screen_y)

    def screen_to_world(self, screen_x: int, screen_y: int) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates"""
        world_x = (screen_x - self.screen_width / 2) / self.zoom + self.x
        world_y = (screen_y - self.screen_height / 2) / self.zoom + self.y
        return world_x, world_y

    def grid_to_screen(self, grid_x: int, grid_y: int) -> Tuple[int, int]:
        """Convert grid coordinates to screen coordinates"""
        world_x = grid_x * self.tile_size
        world_y = grid_y * self.tile_size
        return self.world_to_screen(world_x, world_y)

    def screen_to_grid(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        """Convert screen coordinates to grid coordinates"""
        world_x, world_y = self.screen_to_world(screen_x, screen_y)
        grid_x = int(world_x / self.tile_size)
        grid_y = int(world_y / self.tile_size)
        return grid_x, grid_y

    def move(self, dx: float, dy: float):
        """Move camera by delta"""
        self.target_x += dx
        self.target_y += dy

    def move_to(self, x: float, y: float):
        """Move camera to position"""
        self.target_x = x
        self.target_y = y

    def set_zoom(self, zoom: float):
        """Set camera zoom"""
        self.target_zoom = max(self.min_zoom, min(self.max_zoom, zoom))

    def zoom_in(self, amount: float = 0.1):
        """Zoom in"""
        self.set_zoom(self.target_zoom + amount)

    def zoom_out(self, amount: float = 0.1):
        """Zoom out"""
        self.set_zoom(self.target_zoom - amount)

    def track_entity(
        self, entity: Entity, offset_x: float = 0.0, offset_y: float = 0.0
    ):
        """Start tracking an entity"""
        self.tracking_entity = entity
        self.tracking_offset_x = offset_x
        self.tracking_offset_y = offset_y

    def stop_tracking(self):
        """Stop tracking entity"""
        self.tracking_entity = None

    def center_on_grid(self, grid_x: int, grid_y: int):
        """Center camera on a grid position"""
        world_x = grid_x * self.tile_size + self.tile_size / 2
        world_y = grid_y * self.tile_size + self.tile_size / 2
        self.move_to(world_x, world_y)

    def get_visible_grid_bounds(self) -> Tuple[int, int, int, int]:
        """Get the visible grid bounds (min_x, min_y, max_x, max_y)"""
        min_x, min_y = self.screen_to_grid(0, 0)
        max_x, max_y = self.screen_to_grid(self.screen_width, self.screen_height)
        return min_x, min_y, max_x + 1, max_y + 1

    # Camera shake
    def shake(self, intensity: float, duration: float, decay: float = 0.9):
        """
        Apply camera shake effect.

        Args:
            intensity: Shake intensity in pixels
            duration: Duration in seconds
            decay: Decay multiplier per second (0-1, lower = faster decay)
        """
        self.shake_intensity = intensity
        self.shake_duration = duration
        self.shake_decay = decay

    def stop_shake(self):
        """Stop camera shake immediately"""
        self.shake_intensity = 0
        self.shake_duration = 0
        self.shake_offset_x = 0
        self.shake_offset_y = 0

    # Camera bounds
    def set_bounds(self, min_x: float, min_y: float, max_x: float, max_y: float):
        """
        Set camera bounds in world coordinates.

        Camera will be constrained to stay within these bounds.
        """
        self.bounds_enabled = True
        self.bounds_min_x = min_x
        self.bounds_min_y = min_y
        self.bounds_max_x = max_x
        self.bounds_max_y = max_y

    def set_bounds_from_grid(self, grid_width: int, grid_height: int):
        """Set camera bounds from grid size"""
        self.set_bounds(0, 0, grid_width * self.tile_size, grid_height * self.tile_size)

    def disable_bounds(self):
        """Disable camera bounds"""
        self.bounds_enabled = False

    # Multi-target tracking
    def track_entities(
        self, entities: List[Entity], offset_x: float = 0.0, offset_y: float = 0.0
    ):
        """
        Track multiple entities (camera centers on average position).

        Args:
            entities: List of entities to track
            offset_x: X offset from center
            offset_y: Y offset from center
        """
        self.tracking_entities = entities
        self.tracking_entity = None  # Disable single tracking
        self.tracking_offset_x = offset_x
        self.tracking_offset_y = offset_y

    def add_tracking_entity(self, entity: Entity):
        """Add entity to multi-target tracking"""
        if entity not in self.tracking_entities:
            self.tracking_entities.append(entity)
        self.tracking_entity = None

    def remove_tracking_entity(self, entity: Entity):
        """Remove entity from multi-target tracking"""
        if entity in self.tracking_entities:
            self.tracking_entities.remove(entity)

    def clear_tracking(self):
        """Clear all tracking"""
        self.tracking_entity = None
        self.tracking_entities.clear()

    # Deadzone
    def set_deadzone(self, width: float, height: float):
        """
        Set deadzone for camera tracking.

        Camera only moves when tracked entity leaves the deadzone.

        Args:
            width: Deadzone width in world units
            height: Deadzone height in world units
        """
        self.deadzone_enabled = True
        self.deadzone_width = width
        self.deadzone_height = height

    def disable_deadzone(self):
        """Disable deadzone"""
        self.deadzone_enabled = False

    # Advanced movement
    def move_to_smooth(self, x: float, y: float, smoothing: Optional[float] = None):
        """
        Move camera to position with custom smoothing.

        Args:
            x: Target X position
            y: Target Y position
            smoothing: Custom smoothing (uses camera smoothing if None)
        """
        self.target_x = x
        self.target_y = y

        if smoothing is not None:
            old_smoothing = self.smoothing
            self.smoothing = smoothing
            # Smoothing will be applied in update()
            # Note: You may want to restore old smoothing later

    def snap_to_position(self, x: float, y: float):
        """Instantly snap camera to position (no smoothing)"""
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y

    def snap_to_entity(self, entity: Entity):
        """Instantly snap camera to entity position"""
        grid_pos = entity.get_component(GridPosition)
        if grid_pos:
            world_x = grid_pos.grid_x * self.tile_size + self.tile_size / 2
            world_y = grid_pos.grid_y * self.tile_size + self.tile_size / 2
        else:
            transform = entity.get_component(Transform)
            if not transform:
                return
            world_x = transform.x
            world_y = transform.y

        self.snap_to_position(world_x, world_y)

    def zoom_to(self, zoom: float, smoothing: Optional[float] = None):
        """
        Zoom to specific level with optional custom smoothing.

        Args:
            zoom: Target zoom level
            smoothing: Custom smoothing (uses camera smoothing if None)
        """
        self.set_zoom(zoom)

        if smoothing is not None:
            old_smoothing = self.smoothing
            self.smoothing = smoothing

    def reset_zoom(self):
        """Reset zoom to 1.0"""
        self.set_zoom(1.0)

    # Utility
    def is_point_visible(self, world_x: float, world_y: float) -> bool:
        """Check if a world point is visible in the camera"""
        screen_x, screen_y = self.world_to_screen(world_x, world_y)
        return (
            0 <= screen_x <= self.screen_width and 0 <= screen_y <= self.screen_height
        )

    def is_rect_visible(
        self, world_x: float, world_y: float, width: float, height: float
    ) -> bool:
        """Check if a world rectangle is visible (at least partially)"""
        # Check if any corner is visible
        corners = [
            (world_x, world_y),
            (world_x + width, world_y),
            (world_x, world_y + height),
            (world_x + width, world_y + height),
        ]

        for cx, cy in corners:
            if self.is_point_visible(cx, cy):
                return True

        return False
