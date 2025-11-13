"""
Scene Management System

Manages game scenes/states with transitions and effects.
"""

from typing import Optional, List, Callable, Dict, Any
from enum import Enum
from abc import ABC, abstractmethod
import pygame


class SceneState(Enum):
    """Scene lifecycle states"""
    LOADING = "loading"
    ACTIVE = "active"
    PAUSED = "paused"
    TRANSITIONING_OUT = "transitioning_out"
    TRANSITIONING_IN = "transitioning_in"
    INACTIVE = "inactive"


class TransitionType(Enum):
    """Types of scene transitions"""
    NONE = "none"
    FADE = "fade"
    SLIDE_LEFT = "slide_left"
    SLIDE_RIGHT = "slide_right"
    SLIDE_UP = "slide_up"
    SLIDE_DOWN = "slide_down"
    DISSOLVE = "dissolve"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"


class Scene(ABC):
    """Base class for all scenes"""

    def __init__(self, name: str):
        self.name = name
        self.state = SceneState.INACTIVE
        self.manager: Optional['SceneManager'] = None
        self.transition_progress = 0.0
        self.data: Dict[str, Any] = {}

    @abstractmethod
    def on_enter(self, data: Optional[Dict[str, Any]] = None):
        """Called when scene becomes active"""
        pass

    @abstractmethod
    def on_exit(self):
        """Called when scene is deactivated"""
        pass

    @abstractmethod
    def update(self, delta_time: float):
        """Update scene logic"""
        pass

    @abstractmethod
    def render(self, screen: pygame.Surface):
        """Render scene"""
        pass

    def on_pause(self):
        """Called when scene is paused"""
        self.state = SceneState.PAUSED

    def on_resume(self):
        """Called when scene is resumed"""
        self.state = SceneState.ACTIVE

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame event.

        Returns:
            True if event was handled, False otherwise
        """
        return False

    def change_scene(self, scene_name: str, transition: TransitionType = TransitionType.FADE,
                     duration: float = 0.5, data: Optional[Dict[str, Any]] = None):
        """Request scene change through manager"""
        if self.manager:
            self.manager.change_scene(scene_name, transition, duration, data)

    def push_scene(self, scene_name: str, transition: TransitionType = TransitionType.FADE,
                   duration: float = 0.5, data: Optional[Dict[str, Any]] = None):
        """Push new scene on stack"""
        if self.manager:
            self.manager.push_scene(scene_name, transition, duration, data)

    def pop_scene(self, transition: TransitionType = TransitionType.FADE, duration: float = 0.5):
        """Pop current scene from stack"""
        if self.manager:
            self.manager.pop_scene(transition, duration)


class SceneTransition:
    """Manages transition effects between scenes"""

    def __init__(self, transition_type: TransitionType, duration: float,
                 screen_width: int, screen_height: int):
        self.type = transition_type
        self.duration = duration
        self.elapsed = 0.0
        self.screen_width = screen_width
        self.screen_height = screen_height
        # Mark complete immediately if zero duration
        self.is_complete = (duration <= 0)

    @property
    def progress(self) -> float:
        """Get transition progress (0.0 to 1.0)"""
        if self.duration <= 0:
            return 1.0
        return min(1.0, self.elapsed / self.duration)

    def update(self, delta_time: float):
        """Update transition"""
        self.elapsed += delta_time
        if self.elapsed >= self.duration:
            self.is_complete = True

    def apply(self, screen: pygame.Surface, old_surface: Optional[pygame.Surface],
              new_surface: pygame.Surface):
        """
        Apply transition effect.

        Args:
            screen: Target screen
            old_surface: Previous scene render (optional)
            new_surface: New scene render
        """
        if self.type == TransitionType.NONE:
            screen.blit(new_surface, (0, 0))

        elif self.type == TransitionType.FADE:
            self._apply_fade(screen, old_surface, new_surface)

        elif self.type == TransitionType.SLIDE_LEFT:
            self._apply_slide(screen, old_surface, new_surface, -1, 0)

        elif self.type == TransitionType.SLIDE_RIGHT:
            self._apply_slide(screen, old_surface, new_surface, 1, 0)

        elif self.type == TransitionType.SLIDE_UP:
            self._apply_slide(screen, old_surface, new_surface, 0, -1)

        elif self.type == TransitionType.SLIDE_DOWN:
            self._apply_slide(screen, old_surface, new_surface, 0, 1)

        elif self.type == TransitionType.DISSOLVE:
            self._apply_dissolve(screen, old_surface, new_surface)

        elif self.type == TransitionType.ZOOM_IN:
            self._apply_zoom(screen, new_surface, zoom_in=True)

        elif self.type == TransitionType.ZOOM_OUT:
            self._apply_zoom(screen, new_surface, zoom_in=False)

    def _apply_fade(self, screen: pygame.Surface, old_surface: Optional[pygame.Surface],
                    new_surface: pygame.Surface):
        """Apply fade transition"""
        if old_surface:
            screen.blit(old_surface, (0, 0))

        # Fade in new surface
        alpha = int(self.progress * 255)
        temp = new_surface.copy()
        temp.set_alpha(alpha)
        screen.blit(temp, (0, 0))

    def _apply_slide(self, screen: pygame.Surface, old_surface: Optional[pygame.Surface],
                     new_surface: pygame.Surface, dx: int, dy: int):
        """Apply slide transition"""
        offset_x = int(dx * self.screen_width * (1.0 - self.progress))
        offset_y = int(dy * self.screen_height * (1.0 - self.progress))

        # Draw old surface sliding out
        if old_surface:
            old_offset_x = -int(dx * self.screen_width * self.progress)
            old_offset_y = -int(dy * self.screen_height * self.progress)
            screen.blit(old_surface, (old_offset_x, old_offset_y))

        # Draw new surface sliding in
        screen.blit(new_surface, (offset_x, offset_y))

    def _apply_dissolve(self, screen: pygame.Surface, old_surface: Optional[pygame.Surface],
                        new_surface: pygame.Surface):
        """Apply dissolve transition (similar to fade but with checkerboard pattern)"""
        if old_surface:
            screen.blit(old_surface, (0, 0))

        # Create dissolve mask based on progress
        temp = new_surface.copy()
        alpha = int(self.progress * 255)
        temp.set_alpha(alpha)
        screen.blit(temp, (0, 0))

    def _apply_zoom(self, screen: pygame.Surface, new_surface: pygame.Surface, zoom_in: bool):
        """Apply zoom transition"""
        if zoom_in:
            scale = self.progress
        else:
            scale = 1.0 + (1.0 - self.progress)

        if scale <= 0:
            scale = 0.01

        # Scale surface
        new_width = int(self.screen_width * scale)
        new_height = int(self.screen_height * scale)

        if new_width > 0 and new_height > 0:
            scaled = pygame.transform.scale(new_surface, (new_width, new_height))

            # Center on screen
            x = (self.screen_width - new_width) // 2
            y = (self.screen_height - new_height) // 2

            screen.fill((0, 0, 0))
            screen.blit(scaled, (x, y))


class SceneManager:
    """Manages scene lifecycle and transitions"""

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Scene registry
        self.scenes: Dict[str, Scene] = {}

        # Scene stack (for push/pop)
        self.scene_stack: List[Scene] = []

        # Current scene
        self.current_scene: Optional[Scene] = None
        self.next_scene: Optional[Scene] = None
        self.next_scene_data: Optional[Dict[str, Any]] = None

        # Transition state
        self.transition: Optional[SceneTransition] = None
        self.old_surface: Optional[pygame.Surface] = None
        self.new_surface: Optional[pygame.Surface] = None
        self._is_popping = False  # Track if we're in a pop operation

        # Performance
        self.render_cache_enabled = True

    def register_scene(self, scene: Scene):
        """Register a scene"""
        scene.manager = self
        self.scenes[scene.name] = scene

    def unregister_scene(self, scene_name: str):
        """Unregister a scene"""
        if scene_name in self.scenes:
            scene = self.scenes[scene_name]
            scene.manager = None
            del self.scenes[scene_name]

    def get_scene(self, scene_name: str) -> Optional[Scene]:
        """Get registered scene by name"""
        return self.scenes.get(scene_name)

    def change_scene(self, scene_name: str, transition: TransitionType = TransitionType.FADE,
                     duration: float = 0.5, data: Optional[Dict[str, Any]] = None):
        """
        Change to a different scene.

        Args:
            scene_name: Name of scene to change to
            transition: Transition effect
            duration: Transition duration in seconds
            data: Optional data to pass to new scene
        """
        if scene_name not in self.scenes:
            raise ValueError(f"Scene '{scene_name}' not registered")

        self.next_scene = self.scenes[scene_name]
        self.next_scene_data = data

        # Start transition
        if duration > 0 and transition != TransitionType.NONE:
            self.transition = SceneTransition(transition, duration,
                                            self.screen_width, self.screen_height)

            # Cache old scene render
            if self.current_scene and self.render_cache_enabled:
                self.old_surface = pygame.Surface((self.screen_width, self.screen_height))
                self.current_scene.render(self.old_surface)

            if self.current_scene:
                self.current_scene.state = SceneState.TRANSITIONING_OUT
        else:
            # Instant change
            self._complete_scene_change()

    def push_scene(self, scene_name: str, transition: TransitionType = TransitionType.FADE,
                   duration: float = 0.5, data: Optional[Dict[str, Any]] = None):
        """
        Push new scene onto stack (pauses current scene).

        Args:
            scene_name: Name of scene to push
            transition: Transition effect
            duration: Transition duration in seconds
            data: Optional data to pass to new scene
        """
        if scene_name not in self.scenes:
            raise ValueError(f"Scene '{scene_name}' not registered")

        # Pause current scene
        if self.current_scene:
            self.current_scene.on_pause()
            self.scene_stack.append(self.current_scene)

        # Change to new scene
        self.change_scene(scene_name, transition, duration, data)

    def pop_scene(self, transition: TransitionType = TransitionType.FADE, duration: float = 0.5):
        """
        Pop current scene and return to previous scene.

        Args:
            transition: Transition effect
            duration: Transition duration in seconds
        """
        if not self.scene_stack:
            raise RuntimeError("No scenes to pop")

        previous_scene = self.scene_stack.pop()

        # Change to previous scene
        self.next_scene = previous_scene
        self.next_scene_data = None
        self._is_popping = True  # Mark that we're popping

        # Start transition
        if duration > 0 and transition != TransitionType.NONE:
            self.transition = SceneTransition(transition, duration,
                                            self.screen_width, self.screen_height)

            # Cache old scene render
            if self.current_scene and self.render_cache_enabled:
                self.old_surface = pygame.Surface((self.screen_width, self.screen_height))
                self.current_scene.render(self.old_surface)

            if self.current_scene:
                self.current_scene.state = SceneState.TRANSITIONING_OUT
        else:
            # Instant change
            self._complete_scene_pop()

    def _complete_scene_change(self):
        """Complete scene change"""
        # Exit old scene
        if self.current_scene:
            self.current_scene.on_exit()
            self.current_scene.state = SceneState.INACTIVE

        # Enter new scene
        self.current_scene = self.next_scene
        self.current_scene.state = SceneState.ACTIVE
        self.current_scene.on_enter(self.next_scene_data)

        self.next_scene = None
        self.next_scene_data = None
        self.old_surface = None

    def _complete_scene_pop(self):
        """Complete scene pop"""
        # Exit old scene
        if self.current_scene:
            self.current_scene.on_exit()
            self.current_scene.state = SceneState.INACTIVE

        # Resume previous scene
        self.current_scene = self.next_scene
        self.current_scene.state = SceneState.ACTIVE
        self.current_scene.on_resume()

        self.next_scene = None
        self.old_surface = None

    def update(self, delta_time: float):
        """Update current scene and transitions"""
        # Update transition
        if self.transition:
            self.transition.update(delta_time)

            if self.transition.is_complete:
                self.transition = None
                if self._is_popping:
                    # This was a pop operation
                    self._is_popping = False
                    self._complete_scene_pop()
                else:
                    self._complete_scene_change()

        # Update current scene
        if self.current_scene and self.current_scene.state == SceneState.ACTIVE:
            self.current_scene.update(delta_time)

    def render(self, screen: pygame.Surface):
        """Render current scene with transitions"""
        if self.transition:
            # Render new scene to buffer
            if self.next_scene:
                self.new_surface = pygame.Surface((self.screen_width, self.screen_height))
                self.next_scene.render(self.new_surface)
            else:
                self.new_surface = pygame.Surface((self.screen_width, self.screen_height))
                self.new_surface.fill((0, 0, 0))

            # Apply transition
            self.transition.apply(screen, self.old_surface, self.new_surface)
        elif self.current_scene:
            # Normal render
            self.current_scene.render(screen)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame event.

        Returns:
            True if event was handled, False otherwise
        """
        if self.current_scene and self.current_scene.state == SceneState.ACTIVE:
            return self.current_scene.handle_event(event)
        return False

    def get_stack_size(self) -> int:
        """Get size of scene stack"""
        return len(self.scene_stack)

    def clear_stack(self):
        """Clear scene stack"""
        self.scene_stack.clear()

    def is_transitioning(self) -> bool:
        """Check if currently transitioning"""
        return self.transition is not None
