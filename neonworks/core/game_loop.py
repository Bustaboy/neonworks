"""
Game Loop

Main game engine with fixed timestep update and variable rendering.
"""

import time
from typing import Optional

import pygame

from neonworks.audio.audio_manager import AudioManager
from neonworks.core.ecs import World
from neonworks.core.events import EventManager, get_event_manager
from neonworks.core.state import StateManager
from neonworks.input.input_manager import InputManager


class GameEngine:
    """
    Main game engine with fixed timestep update.

    Uses the "fix your timestep" pattern for consistent gameplay
    regardless of frame rate.

    Integrates input, audio, collision, and rendering systems.
    """

    def __init__(self, target_fps: int = 60, fixed_timestep: float = 1.0 / 60.0):
        self.target_fps = target_fps
        self.fixed_timestep = fixed_timestep
        self.running = False
        self.ui_manager = None
        self._camera_offset_provider = None

        # Initialize pygame
        pygame.init()

        # Core systems
        self.world = World()
        self.event_manager = get_event_manager()
        self.state_manager = StateManager()

        # New integrated systems
        self.input_manager = InputManager()
        self.audio_manager = AudioManager()

        # Timing
        self._last_time = 0.0
        self._accumulator = 0.0
        self._frame_count = 0
        self._fps_timer = 0.0
        self._current_fps = 0

        # Performance stats
        self.stats = {
            "fps": 0,
            "frame_time": 0.0,
            "update_time": 0.0,
            "render_time": 0.0,
            "entity_count": 0,
            "audio_playing": 0,
        }

    def start(self):
        """Start the game engine"""
        self.running = True
        self._last_time = time.time()
        self.run()

    def stop(self):
        """Stop the game engine"""
        self.running = False

    def run(self):
        """Main game loop"""
        while self.running:
            frame_start = time.time()
            current_time = time.time()
            frame_time = current_time - self._last_time
            self._last_time = current_time

            # Accumulate time
            self._accumulator += frame_time

            # Fixed timestep updates
            update_start = time.time()
            updates = 0
            max_updates = 5  # Prevent spiral of death

            while self._accumulator >= self.fixed_timestep and updates < max_updates:
                self._fixed_update(self.fixed_timestep)
                self._accumulator -= self.fixed_timestep
                updates += 1

            self.stats["update_time"] = time.time() - update_start

            # Variable timestep rendering
            render_start = time.time()
            self._render()
            self.stats["render_time"] = time.time() - render_start

            # Update FPS counter
            self._update_fps(frame_time)

            # Update stats
            self.stats["frame_time"] = time.time() - frame_start
            self.stats["entity_count"] = len(self.world.get_entities())
            self.stats["audio_playing"] = self.audio_manager.get_cache_info()["playing_sounds"]

            # Frame limiting
            frame_duration = time.time() - frame_start
            target_frame_time = 1.0 / self.target_fps
            if frame_duration < target_frame_time:
                time.sleep(target_frame_time - frame_duration)

    def _fixed_update(self, delta_time: float):
        """Fixed timestep update"""
        # Process pygame events
        for event in pygame.event.get():
            # Route events through UI manager first; if handled, skip engine handling.
            if self.ui_manager and self.ui_manager.handle_event(event):
                continue

            if event.type == pygame.QUIT:
                self.running = False

            # Pass event to input manager
            self.input_manager.process_event(event)

        # Process engine events
        self.event_manager.process_events()

        # Update input manager
        self.input_manager.update(delta_time)

        # Update audio manager
        self.audio_manager.update()

        # Update UI manager before states so UI state stays responsive
        if self.ui_manager:
            self.ui_manager.update(
                delta_time, pygame.mouse.get_pos(), self._get_camera_offset()
            )

        # Update state manager (which updates current state)
        self.state_manager.update(delta_time)

        # Update world systems (includes collision, etc.)
        self.world.update(delta_time)

    def _render(self):
        """Variable timestep rendering"""
        # Render current state
        self.state_manager.render()

        # Render UI overlays
        if self.ui_manager:
            self.ui_manager.render(
                fps=self.get_fps(), camera_offset=self._get_camera_offset()
            )

    def _update_fps(self, frame_time: float):
        """Update FPS counter"""
        self._frame_count += 1
        self._fps_timer += frame_time

        if self._fps_timer >= 1.0:
            self._current_fps = self._frame_count
            self.stats["fps"] = self._current_fps
            self._frame_count = 0
            self._fps_timer = 0.0

    def get_fps(self) -> int:
        """Get current FPS"""
        return self._current_fps

    def get_stats(self) -> dict:
        """Get performance statistics"""
        return self.stats.copy()

    def attach_ui_manager(self, ui_manager, camera_offset_provider=None):
        """
        Attach a UI manager so the engine can dispatch events and render overlays.

        Args:
            ui_manager: Instance with handle_event/update/render methods.
            camera_offset_provider: Callable returning (x, y) offset for UI tools.
        """
        self.ui_manager = ui_manager
        self._camera_offset_provider = camera_offset_provider

    def _get_camera_offset(self):
        """Return camera offset if provided by caller, else origin."""
        if callable(self._camera_offset_provider):
            try:
                return self._camera_offset_provider()
            except Exception:
                return (0, 0)
        return (0, 0)


class EngineConfig:
    """Engine configuration"""

    def __init__(self):
        # Display
        self.window_width = 1280
        self.window_height = 720
        self.fullscreen = False
        self.vsync = True

        # Performance
        self.target_fps = 60
        self.fixed_timestep = 1.0 / 60.0

        # Grid
        self.tile_size = 32
        self.grid_width = 100
        self.grid_height = 100

        # Rendering
        self.enable_particles = True
        self.enable_shadows = False
        self.render_navmesh = False

        # Editor
        self.editor_grid_visible = True
        self.editor_snap_to_grid = True

        # Debug
        self.show_fps = True
        self.show_debug_info = False
        self.show_collision_boxes = False

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "window_width": self.window_width,
            "window_height": self.window_height,
            "fullscreen": self.fullscreen,
            "vsync": self.vsync,
            "target_fps": self.target_fps,
            "fixed_timestep": self.fixed_timestep,
            "tile_size": self.tile_size,
            "grid_width": self.grid_width,
            "grid_height": self.grid_height,
            "enable_particles": self.enable_particles,
            "enable_shadows": self.enable_shadows,
            "render_navmesh": self.render_navmesh,
            "editor_grid_visible": self.editor_grid_visible,
            "editor_snap_to_grid": self.editor_snap_to_grid,
            "show_fps": self.show_fps,
            "show_debug_info": self.show_debug_info,
            "show_collision_boxes": self.show_collision_boxes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EngineConfig":
        """Create from dictionary"""
        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config
