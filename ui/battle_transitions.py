"""
Battle Transition Effects

Visual effects for transitioning between exploration and battle.
"""

import pygame
import math
import random
from typing import Optional, Callable
from enum import Enum


class TransitionType(Enum):
    """Types of battle transitions"""

    FADE = "fade"
    SWIRL = "swirl"
    SHATTER = "shatter"
    WAVE = "wave"
    FLASH = "flash"
    ZOOM = "zoom"


class BattleTransition:
    """
    Base class for battle transition effects.

    Transitions play when entering or exiting battle.
    """

    def __init__(self, screen_width: int, screen_height: int, duration: float = 1.0):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.duration = duration
        self.timer = 0.0
        self.is_complete = False
        self.is_active = False

        # Callbacks
        self.on_complete: Optional[Callable] = None

    def start(self):
        """Start the transition"""
        self.is_active = True
        self.is_complete = False
        self.timer = 0.0

    def update(self, delta_time: float):
        """Update transition"""
        if not self.is_active:
            return

        self.timer += delta_time

        if self.timer >= self.duration:
            self.timer = self.duration
            self.is_complete = True
            self.is_active = False

            if self.on_complete:
                self.on_complete()

    def get_progress(self) -> float:
        """Get transition progress (0.0 to 1.0)"""
        if self.duration <= 0:
            return 1.0
        return min(self.timer / self.duration, 1.0)

    def render(self, screen: pygame.Surface):
        """Render transition effect (override in subclasses)"""
        pass


class FadeTransition(BattleTransition):
    """Fade to black transition"""

    def __init__(self, screen_width: int, screen_height: int, duration: float = 0.5):
        super().__init__(screen_width, screen_height, duration)
        self.fade_surface = pygame.Surface((screen_width, screen_height))
        self.fade_surface.fill((0, 0, 0))

    def render(self, screen: pygame.Surface):
        """Render fade effect"""
        if not self.is_active:
            return

        progress = self.get_progress()
        alpha = int(255 * progress)
        self.fade_surface.set_alpha(alpha)
        screen.blit(self.fade_surface, (0, 0))


class FlashTransition(BattleTransition):
    """Flash transition effect"""

    def __init__(self, screen_width: int, screen_height: int, duration: float = 0.3):
        super().__init__(screen_width, screen_height, duration)
        self.flash_surface = pygame.Surface((screen_width, screen_height))
        self.flash_surface.fill((255, 255, 255))

    def render(self, screen: pygame.Surface):
        """Render flash effect"""
        if not self.is_active:
            return

        progress = self.get_progress()

        # Flash quickly then fade out
        if progress < 0.2:
            alpha = 255
        else:
            alpha = int(255 * (1.0 - (progress - 0.2) / 0.8))

        self.flash_surface.set_alpha(alpha)
        screen.blit(self.flash_surface, (0, 0))


class SwirlTransition(BattleTransition):
    """Swirl/spiral transition effect"""

    def __init__(self, screen_width: int, screen_height: int, duration: float = 1.0):
        super().__init__(screen_width, screen_height, duration)
        self.swirl_surface = pygame.Surface(
            (screen_width, screen_height), pygame.SRCALPHA
        )

    def render(self, screen: pygame.Surface):
        """Render swirl effect"""
        if not self.is_active:
            return

        self.swirl_surface.fill((0, 0, 0, 0))
        progress = self.get_progress()

        center_x = self.screen_width // 2
        center_y = self.screen_height // 2

        # Draw expanding spiral
        max_radius = math.sqrt(center_x**2 + center_y**2) * 1.5
        radius = max_radius * progress

        segments = 64
        points = []

        for i in range(segments + 1):
            angle = (i / segments) * math.pi * 4 * progress  # 2 full rotations
            r = (i / segments) * radius
            x = center_x + r * math.cos(angle)
            y = center_y + r * math.sin(angle)
            points.append((int(x), int(y)))

        if len(points) > 1:
            pygame.draw.lines(self.swirl_surface, (0, 0, 0, 255), False, points, 3)

        # Fill with black
        alpha = int(255 * progress)
        black_surface = pygame.Surface((self.screen_width, self.screen_height))
        black_surface.fill((0, 0, 0))
        black_surface.set_alpha(alpha)

        screen.blit(black_surface, (0, 0))
        screen.blit(self.swirl_surface, (0, 0))


class ShatterTransition(BattleTransition):
    """Screen shatter effect"""

    def __init__(self, screen_width: int, screen_height: int, duration: float = 0.8):
        super().__init__(screen_width, screen_height, duration)

        # Create shatter pieces
        self.pieces = []
        piece_size = 40
        cols = screen_width // piece_size + 1
        rows = screen_height // piece_size + 1

        for row in range(rows):
            for col in range(cols):
                piece = {
                    "x": col * piece_size,
                    "y": row * piece_size,
                    "size": piece_size,
                    "vx": random.uniform(-200, 200),
                    "vy": random.uniform(-100, -300),
                    "rotation": random.uniform(-180, 180),
                    "rotation_speed": random.uniform(-360, 360),
                }
                self.pieces.append(piece)

    def update(self, delta_time: float):
        """Update shatter pieces"""
        super().update(delta_time)

        if not self.is_active:
            return

        # Update piece positions
        for piece in self.pieces:
            piece["x"] += piece["vx"] * delta_time
            piece["y"] += piece["vy"] * delta_time
            piece["vy"] += 500 * delta_time  # Gravity
            piece["rotation"] += piece["rotation_speed"] * delta_time

    def render(self, screen: pygame.Surface):
        """Render shatter effect"""
        if not self.is_active:
            return

        progress = self.get_progress()

        # Draw black background growing
        alpha = int(255 * progress)
        bg_surface = pygame.Surface((self.screen_width, self.screen_height))
        bg_surface.fill((0, 0, 0))
        bg_surface.set_alpha(alpha)
        screen.blit(bg_surface, (0, 0))

        # Draw falling pieces (as simple rectangles)
        for piece in self.pieces:
            if progress < 0.7:  # Only show pieces early in transition
                rect = pygame.Rect(
                    int(piece["x"]), int(piece["y"]), piece["size"], piece["size"]
                )
                # Simple white rectangles for shards
                pygame.draw.rect(screen, (255, 255, 255), rect, 2)


class WaveTransition(BattleTransition):
    """Wave wipe transition"""

    def __init__(self, screen_width: int, screen_height: int, duration: float = 0.6):
        super().__init__(screen_width, screen_height, duration)
        self.wave_surface = pygame.Surface(
            (screen_width, screen_height), pygame.SRCALPHA
        )

    def render(self, screen: pygame.Surface):
        """Render wave effect"""
        if not self.is_active:
            return

        self.wave_surface.fill((0, 0, 0, 0))
        progress = self.get_progress()

        # Horizontal wave
        wave_x = int(self.screen_width * progress)
        wave_amplitude = 30
        wave_frequency = 5

        points = []
        for y in range(0, self.screen_height, 5):
            wave_offset = wave_amplitude * math.sin(
                (y / self.screen_height) * wave_frequency * math.pi
            )
            x = wave_x + wave_offset
            points.append((int(x), y))

        # Fill left side of wave with black
        if len(points) > 1:
            left_points = [(0, 0), (0, self.screen_height)] + list(reversed(points))
            pygame.draw.polygon(self.wave_surface, (0, 0, 0, 255), left_points)

        screen.blit(self.wave_surface, (0, 0))


class ZoomTransition(BattleTransition):
    """Zoom in/out transition"""

    def __init__(self, screen_width: int, screen_height: int, duration: float = 0.5):
        super().__init__(screen_width, screen_height, duration)

    def render(self, screen: pygame.Surface):
        """Render zoom effect"""
        if not self.is_active:
            return

        progress = self.get_progress()

        # Create zoom effect by drawing expanding/contracting rectangles
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2

        # Zoom in (screen shrinks to center)
        scale = 1.0 - progress
        if scale > 0.1:
            zoom_width = int(self.screen_width * scale)
            zoom_height = int(self.screen_height * scale)
            zoom_x = center_x - zoom_width // 2
            zoom_y = center_y - zoom_height // 2

            # Black overlay
            overlay = pygame.Surface((self.screen_width, self.screen_height))
            overlay.fill((0, 0, 0))
            pygame.draw.rect(
                overlay, (255, 255, 255), (zoom_x, zoom_y, zoom_width, zoom_height)
            )
            overlay.set_colorkey((255, 255, 255))
            screen.blit(overlay, (0, 0))


class BattleTransitionManager:
    """
    Manages battle transition effects.

    Provides easy access to different transition types.
    """

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.current_transition: Optional[BattleTransition] = None

    def start_transition(
        self,
        transition_type: TransitionType,
        duration: Optional[float] = None,
        on_complete: Optional[Callable] = None,
    ):
        """Start a transition effect"""

        # Create appropriate transition
        if transition_type == TransitionType.FADE:
            self.current_transition = FadeTransition(
                self.screen_width, self.screen_height, duration or 0.5
            )
        elif transition_type == TransitionType.FLASH:
            self.current_transition = FlashTransition(
                self.screen_width, self.screen_height, duration or 0.3
            )
        elif transition_type == TransitionType.SWIRL:
            self.current_transition = SwirlTransition(
                self.screen_width, self.screen_height, duration or 1.0
            )
        elif transition_type == TransitionType.SHATTER:
            self.current_transition = ShatterTransition(
                self.screen_width, self.screen_height, duration or 0.8
            )
        elif transition_type == TransitionType.WAVE:
            self.current_transition = WaveTransition(
                self.screen_width, self.screen_height, duration or 0.6
            )
        elif transition_type == TransitionType.ZOOM:
            self.current_transition = ZoomTransition(
                self.screen_width, self.screen_height, duration or 0.5
            )
        else:
            # Default to fade
            self.current_transition = FadeTransition(
                self.screen_width, self.screen_height, duration or 0.5
            )

        if self.current_transition:
            self.current_transition.on_complete = on_complete
            self.current_transition.start()

    def update(self, delta_time: float):
        """Update current transition"""
        if self.current_transition and self.current_transition.is_active:
            self.current_transition.update(delta_time)

    def render(self, screen: pygame.Surface):
        """Render current transition"""
        if self.current_transition:
            self.current_transition.render(screen)

    def is_transitioning(self) -> bool:
        """Check if a transition is active"""
        return self.current_transition is not None and self.current_transition.is_active

    def is_complete(self) -> bool:
        """Check if current transition is complete"""
        return (
            self.current_transition is not None and self.current_transition.is_complete
        )
