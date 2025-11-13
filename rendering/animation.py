"""
Animation System

Sprite animation system with frame-by-frame playback.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import pygame

from neonworks.core.ecs import Component


@dataclass
class AnimationFrame:
    """Single frame of animation"""

    sprite: pygame.Surface
    duration: float  # Duration in seconds


@dataclass
class Animation:
    """Animation data"""

    name: str
    frames: List[AnimationFrame]
    loop: bool = True

    def get_total_duration(self) -> float:
        """Get total animation duration in seconds"""
        return sum(frame.duration for frame in self.frames)


@dataclass
class AnimationComponent(Component):
    """Component for animated sprites"""

    current_animation: Optional[str] = None
    animations: dict = None  # Dict[str, Animation]
    current_frame: int = 0
    time_in_frame: float = 0.0
    playing: bool = True
    speed: float = 1.0  # Playback speed multiplier

    def __post_init__(self):
        if self.animations is None:
            self.animations = {}

    def play(self, animation_name: str, restart: bool = True):
        """
        Play an animation.

        Args:
            animation_name: Name of the animation to play
            restart: Whether to restart animation if already playing
        """
        if animation_name not in self.animations:
            return

        if self.current_animation != animation_name or restart:
            self.current_animation = animation_name
            self.current_frame = 0
            self.time_in_frame = 0.0
            self.playing = True

    def stop(self):
        """Stop the current animation"""
        self.playing = False

    def pause(self):
        """Pause the current animation"""
        self.playing = False

    def resume(self):
        """Resume the current animation"""
        self.playing = True


class AnimationSystem:
    """System for updating animations"""

    def update_animation(
        self, anim_component: AnimationComponent, delta_time: float
    ) -> pygame.Surface:
        """
        Update animation and return current frame sprite.

        Args:
            anim_component: Animation component to update
            delta_time: Time since last frame in seconds

        Returns:
            Current frame sprite
        """
        if not anim_component.playing or not anim_component.current_animation:
            # Return first frame of current animation or None
            if anim_component.current_animation:
                animation = anim_component.animations.get(
                    anim_component.current_animation
                )
                if animation and animation.frames:
                    return animation.frames[0].sprite
            return None

        animation = anim_component.animations.get(anim_component.current_animation)
        if not animation or not animation.frames:
            return None

        # Update time
        anim_component.time_in_frame += delta_time * anim_component.speed

        # Get current frame
        current_frame_data = animation.frames[anim_component.current_frame]

        # Check if we should advance to next frame
        while anim_component.time_in_frame >= current_frame_data.duration:
            anim_component.time_in_frame -= current_frame_data.duration
            anim_component.current_frame += 1

            # Handle loop/end
            if anim_component.current_frame >= len(animation.frames):
                if animation.loop:
                    anim_component.current_frame = 0
                else:
                    # Animation finished, stay on last frame
                    anim_component.current_frame = len(animation.frames) - 1
                    anim_component.playing = False
                    break

            current_frame_data = animation.frames[anim_component.current_frame]

        return current_frame_data.sprite

    def play_animation(
        self,
        anim_component: AnimationComponent,
        animation_name: str,
        restart: bool = True,
    ):
        """
        Play an animation.

        Args:
            anim_component: Animation component
            animation_name: Name of animation to play
            restart: If True, restart animation from frame 0 even if already playing
        """
        if animation_name not in anim_component.animations:
            print(f"Warning: Animation '{animation_name}' not found")
            return

        if anim_component.current_animation != animation_name or restart:
            anim_component.current_animation = animation_name
            anim_component.current_frame = 0
            anim_component.time_in_frame = 0.0
            anim_component.playing = True

    def stop_animation(self, anim_component: AnimationComponent):
        """Stop the current animation"""
        anim_component.playing = False

    def pause_animation(self, anim_component: AnimationComponent):
        """Pause the current animation"""
        anim_component.playing = False

    def resume_animation(self, anim_component: AnimationComponent):
        """Resume the paused animation"""
        anim_component.playing = True

    def is_animation_finished(self, anim_component: AnimationComponent) -> bool:
        """Check if the current animation has finished (for non-looping animations)"""
        if not anim_component.current_animation:
            return True

        animation = anim_component.animations.get(anim_component.current_animation)
        if not animation or animation.loop:
            return False

        return (
            anim_component.current_frame >= len(animation.frames) - 1
            and not anim_component.playing
        )


class AnimationBuilder:
    """Helper class to build animations easily"""

    def __init__(self, name: str, loop: bool = True):
        self.name = name
        self.loop = loop
        self.frames: List[AnimationFrame] = []

    def add_frame(
        self, sprite: pygame.Surface, duration: float = 0.1
    ) -> "AnimationBuilder":
        """Add a frame to the animation"""
        self.frames.append(AnimationFrame(sprite, duration))
        return self

    def add_frames(
        self, sprites: List[pygame.Surface], duration: float = 0.1
    ) -> "AnimationBuilder":
        """Add multiple frames with the same duration"""
        for sprite in sprites:
            self.add_frame(sprite, duration)
        return self

    def add_frames_from_sheet(
        self, sprite_sheet, indices: List[int], columns: int, duration: float = 0.1
    ) -> "AnimationBuilder":
        """Add frames from a sprite sheet by indices"""
        for index in indices:
            sprite = sprite_sheet.get_sprite_by_index(index, columns)
            self.add_frame(sprite, duration)
        return self

    def build(self) -> Animation:
        """Build and return the animation"""
        return Animation(self.name, self.frames, self.loop)


def create_animation_from_sheet(
    name: str,
    sprite_sheet,
    frame_indices: List[int],
    columns: int,
    frame_duration: float = 0.1,
    loop: bool = True,
) -> Animation:
    """
    Convenience function to create an animation from a sprite sheet.

    Args:
        name: Animation name
        sprite_sheet: SpriteSheet object
        frame_indices: List of frame indices to use
        columns: Number of columns in the sprite sheet
        frame_duration: Duration of each frame in seconds
        loop: Whether animation should loop

    Returns:
        Animation object
    """
    return (
        AnimationBuilder(name, loop)
        .add_frames_from_sheet(sprite_sheet, frame_indices, columns, frame_duration)
        .build()
    )


# ========== Animation State Machine ==========


class TransitionConditionType(Enum):
    """Types of transition conditions"""

    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    ANIMATION_FINISHED = "animation_finished"
    TRIGGER = "trigger"


@dataclass
class TransitionCondition:
    """Condition for state transition"""

    condition_type: TransitionConditionType
    parameter_name: Optional[str] = None
    value: Any = None

    def evaluate(self, state_machine: "AnimationStateMachine") -> bool:
        """Evaluate if condition is met"""
        if self.condition_type == TransitionConditionType.TRIGGER:
            return state_machine.is_trigger_set(self.parameter_name)

        elif self.condition_type == TransitionConditionType.ANIMATION_FINISHED:
            return state_machine._is_current_animation_finished()

        elif self.parameter_name in state_machine.parameters:
            param_value = state_machine.parameters[self.parameter_name]

            if self.condition_type == TransitionConditionType.EQUALS:
                return param_value == self.value
            elif self.condition_type == TransitionConditionType.NOT_EQUALS:
                return param_value != self.value
            elif self.condition_type == TransitionConditionType.GREATER_THAN:
                return param_value > self.value
            elif self.condition_type == TransitionConditionType.LESS_THAN:
                return param_value < self.value

        return False


@dataclass
class StateTransition:
    """Transition between animation states"""

    from_state: str
    to_state: str
    conditions: List[TransitionCondition] = field(default_factory=list)
    transition_duration: float = 0.0  # Blend duration in seconds

    def can_transition(self, state_machine: "AnimationStateMachine") -> bool:
        """Check if all conditions are met for transition"""
        if not self.conditions:
            return True

        return all(condition.evaluate(state_machine) for condition in self.conditions)


@dataclass
class AnimationState:
    """State in the animation state machine"""

    name: str
    animation_name: str
    on_enter: Optional[Callable[[], None]] = None
    on_exit: Optional[Callable[[], None]] = None
    speed: float = 1.0
    loop: bool = True


class AnimationStateMachine(Component):
    """
    Animation state machine for complex animation control.

    Features:
    - State-based animation control
    - Conditional transitions
    - Parameters (bool, int, float, trigger)
    - State callbacks
    - Animation blending
    """

    def __init__(self):
        super().__init__()

        # States
        self.states: Dict[str, AnimationState] = {}
        self.current_state: Optional[str] = None
        self.previous_state: Optional[str] = None

        # Transitions
        self.transitions: List[StateTransition] = []

        # Parameters for transition conditions
        self.parameters: Dict[str, Any] = {}
        self._triggers: set = set()

        # Animation component reference
        self.animation_component: Optional[AnimationComponent] = None

        # Blending
        self._blend_progress = 0.0
        self._blend_duration = 0.0
        self._blending = False

    def add_state(self, state: AnimationState):
        """Add a state to the state machine"""
        self.states[state.name] = state

        # Set as default if first state
        if self.current_state is None:
            self.current_state = state.name

    def add_transition(self, transition: StateTransition):
        """Add a transition between states"""
        self.transitions.append(transition)

    def set_parameter(self, name: str, value: Any):
        """Set a parameter value"""
        self.parameters[name] = value

    def get_parameter(self, name: str, default: Any = None) -> Any:
        """Get a parameter value"""
        return self.parameters.get(name, default)

    def set_trigger(self, name: str):
        """Set a trigger (one-time condition)"""
        self._triggers.add(name)

    def is_trigger_set(self, name: str) -> bool:
        """Check if trigger is set"""
        return name in self._triggers

    def reset_trigger(self, name: str):
        """Reset a trigger"""
        self._triggers.discard(name)

    def reset_all_triggers(self):
        """Reset all triggers"""
        self._triggers.clear()

    def change_state(self, state_name: str, blend_duration: float = 0.0):
        """
        Manually change to a specific state.

        Args:
            state_name: Name of state to change to
            blend_duration: Duration of blend transition
        """
        if state_name not in self.states:
            print(f"Warning: State '{state_name}' not found")
            return

        if state_name == self.current_state:
            return

        self._transition_to_state(state_name, blend_duration)

    def _transition_to_state(self, state_name: str, blend_duration: float = 0.0):
        """Internal method to transition to a new state"""
        # Exit previous state
        if self.current_state:
            current = self.states[self.current_state]
            if current.on_exit:
                current.on_exit()

        self.previous_state = self.current_state
        self.current_state = state_name

        # Enter new state
        new_state = self.states[state_name]
        if new_state.on_enter:
            new_state.on_enter()

        # Play animation
        if self.animation_component:
            self.animation_component.play(new_state.animation_name)
            self.animation_component.speed = new_state.speed

        # Setup blending
        if blend_duration > 0:
            self._blending = True
            self._blend_duration = blend_duration
            self._blend_progress = 0.0

    def update(self, delta_time: float):
        """
        Update state machine.

        Args:
            delta_time: Time since last update in seconds
        """
        if not self.current_state:
            return

        # Update blending
        if self._blending:
            self._blend_progress += delta_time
            if self._blend_progress >= self._blend_duration:
                self._blending = False
                self._blend_progress = 0.0

        # Check transitions
        for transition in self.transitions:
            if transition.from_state == self.current_state:
                if transition.can_transition(self):
                    self._transition_to_state(
                        transition.to_state, transition.transition_duration
                    )
                    # Reset triggers after transition
                    self.reset_all_triggers()
                    break

    def _is_current_animation_finished(self) -> bool:
        """Check if current animation is finished"""
        if not self.animation_component or not self.current_state:
            return False

        state = self.states[self.current_state]
        if state.loop:
            return False

        animation = self.animation_component.animations.get(state.animation_name)
        if not animation:
            return False

        return (
            self.animation_component.current_frame >= len(animation.frames) - 1
            and not self.animation_component.playing
        )

    def get_current_state_name(self) -> Optional[str]:
        """Get name of current state"""
        return self.current_state

    def get_current_state(self) -> Optional[AnimationState]:
        """Get current state object"""
        if self.current_state:
            return self.states.get(self.current_state)
        return None

    def is_in_state(self, state_name: str) -> bool:
        """Check if currently in specified state"""
        return self.current_state == state_name

    @property
    def blend_progress(self) -> float:
        """Get current blend progress (0.0 to 1.0)"""
        if not self._blending or self._blend_duration == 0:
            return 1.0
        return min(1.0, self._blend_progress / self._blend_duration)


class AnimationStateMachineBuilder:
    """Helper class to build animation state machines"""

    def __init__(self):
        self.state_machine = AnimationStateMachine()

    def add_state(
        self,
        name: str,
        animation_name: str,
        loop: bool = True,
        speed: float = 1.0,
        on_enter: Optional[Callable] = None,
        on_exit: Optional[Callable] = None,
    ) -> "AnimationStateMachineBuilder":
        """Add a state"""
        state = AnimationState(
            name=name,
            animation_name=animation_name,
            loop=loop,
            speed=speed,
            on_enter=on_enter,
            on_exit=on_exit,
        )
        self.state_machine.add_state(state)
        return self

    def add_transition(
        self,
        from_state: str,
        to_state: str,
        conditions: Optional[List[TransitionCondition]] = None,
        transition_duration: float = 0.0,
    ) -> "AnimationStateMachineBuilder":
        """Add a transition"""
        transition = StateTransition(
            from_state=from_state,
            to_state=to_state,
            conditions=conditions or [],
            transition_duration=transition_duration,
        )
        self.state_machine.add_transition(transition)
        return self

    def add_parameter(
        self, name: str, default_value: Any
    ) -> "AnimationStateMachineBuilder":
        """Add a parameter with default value"""
        self.state_machine.set_parameter(name, default_value)
        return self

    def build(self) -> AnimationStateMachine:
        """Build and return the state machine"""
        return self.state_machine
