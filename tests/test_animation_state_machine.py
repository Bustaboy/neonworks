"""
Comprehensive tests for Animation State Machine

Tests animation states, transitions, conditions, and blending.
"""

from unittest.mock import MagicMock, Mock

import pygame
import pytest

from neonworks.rendering.animation import (
    Animation,
    AnimationBuilder,
    AnimationComponent,
    AnimationFrame,
    AnimationState,
    AnimationStateMachine,
    AnimationStateMachineBuilder,
    AnimationSystem,
    StateTransition,
    TransitionCondition,
    TransitionConditionType,
)


@pytest.fixture
def screen():
    """Create a test screen surface"""
    pygame.init()
    return pygame.Surface((100, 100))


@pytest.fixture
def animation_component():
    """Create a test animation component"""
    # Create mock sprites
    sprite1 = pygame.Surface((32, 32))
    sprite2 = pygame.Surface((32, 32))
    sprite3 = pygame.Surface((32, 32))

    # Create animations
    idle_anim = Animation(
        "idle", [AnimationFrame(sprite1, 0.1), AnimationFrame(sprite2, 0.1)], loop=True
    )

    walk_anim = Animation(
        "walk",
        [
            AnimationFrame(sprite1, 0.08),
            AnimationFrame(sprite2, 0.08),
            AnimationFrame(sprite3, 0.08),
        ],
        loop=True,
    )

    jump_anim = Animation(
        "jump",
        [
            AnimationFrame(sprite1, 0.15),
            AnimationFrame(sprite2, 0.15),
            AnimationFrame(sprite3, 0.15),
        ],
        loop=False,
    )

    component = AnimationComponent()
    component.animations = {"idle": idle_anim, "walk": walk_anim, "jump": jump_anim}

    return component


class TestAnimationBasics:
    """Test basic animation functionality"""

    def test_animation_frame_creation(self, screen):
        """Test creating animation frame"""
        sprite = pygame.Surface((32, 32))
        frame = AnimationFrame(sprite, 0.1)

        assert frame.sprite == sprite
        assert frame.duration == 0.1

    def test_animation_creation(self, screen):
        """Test creating animation"""
        sprite = pygame.Surface((32, 32))
        frames = [AnimationFrame(sprite, 0.1) for _ in range(3)]
        anim = Animation("test", frames, loop=True)

        assert anim.name == "test"
        assert len(anim.frames) == 3
        assert anim.loop

    def test_animation_total_duration(self, screen):
        """Test calculating total animation duration"""
        sprite = pygame.Surface((32, 32))
        frames = [AnimationFrame(sprite, 0.1) for _ in range(5)]
        anim = Animation("test", frames)

        assert anim.get_total_duration() == 0.5

    def test_animation_component_play(self, animation_component):
        """Test playing animation"""
        animation_component.play("walk")

        assert animation_component.current_animation == "walk"
        assert animation_component.current_frame == 0
        assert animation_component.playing

    def test_animation_component_stop(self, animation_component):
        """Test stopping animation"""
        animation_component.play("walk")
        animation_component.stop()

        assert not animation_component.playing

    def test_animation_system_update(self, animation_component):
        """Test animation system updates frames"""
        system = AnimationSystem()
        animation_component.play("walk")

        sprite = system.update_animation(animation_component, 0.1)
        assert sprite is not None

    def test_animation_system_loop(self, animation_component):
        """Test animation loops correctly"""
        system = AnimationSystem()
        animation_component.play("idle")

        # Update past animation duration
        for _ in range(5):
            system.update_animation(animation_component, 0.15)

        # Should still be playing (looping)
        assert animation_component.playing

    def test_animation_system_no_loop(self, animation_component):
        """Test non-looping animation stops"""
        system = AnimationSystem()
        animation_component.play("jump")

        # Update past animation duration
        for _ in range(10):
            system.update_animation(animation_component, 0.2)

        # Should have stopped
        assert not animation_component.playing


class TestAnimationStateMachine:
    """Test animation state machine"""

    def test_state_machine_creation(self):
        """Test creating state machine"""
        state_machine = AnimationStateMachine()

        assert len(state_machine.states) == 0
        assert state_machine.current_state is None

    def test_add_state(self):
        """Test adding state"""
        state_machine = AnimationStateMachine()
        state = AnimationState("idle", "idle_anim")

        state_machine.add_state(state)

        assert "idle" in state_machine.states
        assert state_machine.current_state == "idle"  # First state becomes current

    def test_add_multiple_states(self):
        """Test adding multiple states"""
        state_machine = AnimationStateMachine()

        state_machine.add_state(AnimationState("idle", "idle_anim"))
        state_machine.add_state(AnimationState("walk", "walk_anim"))
        state_machine.add_state(AnimationState("run", "run_anim"))

        assert len(state_machine.states) == 3
        assert state_machine.current_state == "idle"

    def test_change_state(self, animation_component):
        """Test changing state"""
        state_machine = AnimationStateMachine()
        state_machine.animation_component = animation_component

        state_machine.add_state(AnimationState("idle", "idle"))
        state_machine.add_state(AnimationState("walk", "walk"))

        state_machine.change_state("walk")

        assert state_machine.current_state == "walk"
        assert animation_component.current_animation == "walk"

    def test_change_state_nonexistent(self, animation_component):
        """Test changing to non-existent state"""
        state_machine = AnimationStateMachine()
        state_machine.animation_component = animation_component
        state_machine.add_state(AnimationState("idle", "idle"))

        state_machine.change_state("nonexistent")

        # Should stay in current state
        assert state_machine.current_state == "idle"

    def test_state_callbacks(self, animation_component):
        """Test state entry/exit callbacks"""
        state_machine = AnimationStateMachine()
        state_machine.animation_component = animation_component

        enter_called = []
        exit_called = []

        state1 = AnimationState(
            "idle",
            "idle",
            on_enter=lambda: enter_called.append("idle"),
            on_exit=lambda: exit_called.append("idle"),
        )
        state2 = AnimationState(
            "walk",
            "walk",
            on_enter=lambda: enter_called.append("walk"),
            on_exit=lambda: exit_called.append("walk"),
        )

        state_machine.add_state(state1)
        state_machine.add_state(state2)

        state_machine.change_state("walk")

        assert "idle" in exit_called
        assert "walk" in enter_called

    def test_parameters(self):
        """Test setting and getting parameters"""
        state_machine = AnimationStateMachine()

        state_machine.set_parameter("speed", 5.0)
        state_machine.set_parameter("grounded", True)

        assert state_machine.get_parameter("speed") == 5.0
        assert state_machine.get_parameter("grounded") == True

    def test_triggers(self):
        """Test trigger system"""
        state_machine = AnimationStateMachine()

        state_machine.set_trigger("jump")

        assert state_machine.is_trigger_set("jump")

        state_machine.reset_trigger("jump")

        assert not state_machine.is_trigger_set("jump")

    def test_reset_all_triggers(self):
        """Test resetting all triggers"""
        state_machine = AnimationStateMachine()

        state_machine.set_trigger("jump")
        state_machine.set_trigger("attack")

        state_machine.reset_all_triggers()

        assert not state_machine.is_trigger_set("jump")
        assert not state_machine.is_trigger_set("attack")


class TestTransitions:
    """Test state transitions"""

    def test_transition_creation(self):
        """Test creating transition"""
        transition = StateTransition("idle", "walk")

        assert transition.from_state == "idle"
        assert transition.to_state == "walk"
        assert len(transition.conditions) == 0

    def test_transition_with_conditions(self):
        """Test transition with conditions"""
        condition = TransitionCondition(TransitionConditionType.GREATER_THAN, "speed", 0.5)
        transition = StateTransition("idle", "walk", [condition])

        assert len(transition.conditions) == 1

    def test_add_transition(self):
        """Test adding transition to state machine"""
        state_machine = AnimationStateMachine()
        state_machine.add_state(AnimationState("idle", "idle"))
        state_machine.add_state(AnimationState("walk", "walk"))

        transition = StateTransition("idle", "walk")
        state_machine.add_transition(transition)

        assert len(state_machine.transitions) == 1

    def test_automatic_transition_trigger(self, animation_component):
        """Test automatic transition with trigger condition"""
        state_machine = AnimationStateMachine()
        state_machine.animation_component = animation_component

        state_machine.add_state(AnimationState("idle", "idle"))
        state_machine.add_state(AnimationState("jump", "jump"))

        condition = TransitionCondition(TransitionConditionType.TRIGGER, "jump_trigger")
        transition = StateTransition("idle", "jump", [condition])
        state_machine.add_transition(transition)

        # Set trigger
        state_machine.set_trigger("jump_trigger")

        # Update should transition
        state_machine.update(0.016)

        assert state_machine.current_state == "jump"

    def test_automatic_transition_equals(self, animation_component):
        """Test automatic transition with equals condition"""
        state_machine = AnimationStateMachine()
        state_machine.animation_component = animation_component

        state_machine.add_state(AnimationState("idle", "idle"))
        state_machine.add_state(AnimationState("walk", "walk"))

        condition = TransitionCondition(TransitionConditionType.EQUALS, "state", "walking")
        transition = StateTransition("idle", "walk", [condition])
        state_machine.add_transition(transition)

        # Set parameter
        state_machine.set_parameter("state", "walking")

        # Update should transition
        state_machine.update(0.016)

        assert state_machine.current_state == "walk"

    def test_automatic_transition_greater_than(self, animation_component):
        """Test automatic transition with greater than condition"""
        state_machine = AnimationStateMachine()
        state_machine.animation_component = animation_component

        state_machine.add_state(AnimationState("idle", "idle"))
        state_machine.add_state(AnimationState("run", "walk"))

        condition = TransitionCondition(TransitionConditionType.GREATER_THAN, "speed", 5.0)
        transition = StateTransition("idle", "run", [condition])
        state_machine.add_transition(transition)

        # Set parameter
        state_machine.set_parameter("speed", 10.0)

        # Update should transition
        state_machine.update(0.016)

        assert state_machine.current_state == "run"

    def test_automatic_transition_less_than(self, animation_component):
        """Test automatic transition with less than condition"""
        state_machine = AnimationStateMachine()
        state_machine.animation_component = animation_component

        state_machine.add_state(AnimationState("run", "walk"))
        state_machine.add_state(AnimationState("idle", "idle"))

        condition = TransitionCondition(TransitionConditionType.LESS_THAN, "speed", 1.0)
        transition = StateTransition("run", "idle", [condition])
        state_machine.add_transition(transition)

        # Set parameter
        state_machine.set_parameter("speed", 0.5)

        # Update should transition
        state_machine.update(0.016)

        assert state_machine.current_state == "idle"

    def test_transition_multiple_conditions(self, animation_component):
        """Test transition with multiple conditions (all must be true)"""
        state_machine = AnimationStateMachine()
        state_machine.animation_component = animation_component

        state_machine.add_state(AnimationState("idle", "idle"))
        state_machine.add_state(AnimationState("attack", "walk"))

        conditions = [
            TransitionCondition(TransitionConditionType.TRIGGER, "attack_trigger"),
            TransitionCondition(TransitionConditionType.EQUALS, "can_attack", True),
        ]
        transition = StateTransition("idle", "attack", conditions)
        state_machine.add_transition(transition)

        # Set only one condition
        state_machine.set_trigger("attack_trigger")
        state_machine.update(0.016)

        # Should not transition (need both conditions)
        assert state_machine.current_state == "idle"

        # Set both conditions
        state_machine.set_trigger("attack_trigger")
        state_machine.set_parameter("can_attack", True)
        state_machine.update(0.016)

        # Should transition
        assert state_machine.current_state == "attack"

    def test_transition_animation_finished(self, animation_component):
        """Test transition on animation finished"""
        state_machine = AnimationStateMachine()
        state_machine.animation_component = animation_component

        state_machine.add_state(AnimationState("jump", "jump", loop=False))
        state_machine.add_state(AnimationState("idle", "idle"))

        condition = TransitionCondition(TransitionConditionType.ANIMATION_FINISHED)
        transition = StateTransition("jump", "idle", [condition])
        state_machine.add_transition(transition)

        # Finish the animation
        animation_component.play("jump")
        animation_component.current_frame = 2  # Last frame
        animation_component.playing = False

        # Update should transition
        state_machine.update(0.016)

        assert state_machine.current_state == "idle"


class TestBlending:
    """Test animation blending"""

    def test_blending_initialization(self, animation_component):
        """Test blending is initialized correctly"""
        state_machine = AnimationStateMachine()
        state_machine.animation_component = animation_component

        state_machine.add_state(AnimationState("idle", "idle"))
        state_machine.add_state(AnimationState("walk", "walk"))

        state_machine.change_state("walk", blend_duration=1.0)

        assert state_machine._blending
        assert state_machine._blend_duration == 1.0
        assert state_machine._blend_progress == 0.0

    def test_blending_progress(self, animation_component):
        """Test blending progress updates"""
        state_machine = AnimationStateMachine()
        state_machine.animation_component = animation_component

        state_machine.add_state(AnimationState("idle", "idle"))
        state_machine.add_state(AnimationState("walk", "walk"))

        state_machine.change_state("walk", blend_duration=1.0)

        state_machine.update(0.5)

        assert state_machine.blend_progress == 0.5

    def test_blending_completion(self, animation_component):
        """Test blending completes"""
        state_machine = AnimationStateMachine()
        state_machine.animation_component = animation_component

        state_machine.add_state(AnimationState("idle", "idle"))
        state_machine.add_state(AnimationState("walk", "walk"))

        state_machine.change_state("walk", blend_duration=0.5)

        state_machine.update(1.0)

        assert not state_machine._blending
        assert state_machine.blend_progress == 1.0


class TestStateMachineBuilder:
    """Test animation state machine builder"""

    def test_builder_creation(self):
        """Test creating builder"""
        builder = AnimationStateMachineBuilder()

        assert builder.state_machine is not None

    def test_builder_add_state(self):
        """Test builder add state"""
        builder = AnimationStateMachineBuilder()

        builder.add_state("idle", "idle_anim")

        assert "idle" in builder.state_machine.states

    def test_builder_add_transition(self):
        """Test builder add transition"""
        builder = AnimationStateMachineBuilder()

        builder.add_state("idle", "idle_anim")
        builder.add_state("walk", "walk_anim")
        builder.add_transition("idle", "walk")

        assert len(builder.state_machine.transitions) == 1

    def test_builder_add_parameter(self):
        """Test builder add parameter"""
        builder = AnimationStateMachineBuilder()

        builder.add_parameter("speed", 0.0)

        assert builder.state_machine.get_parameter("speed") == 0.0

    def test_builder_fluent_interface(self):
        """Test builder fluent interface"""
        builder = (
            AnimationStateMachineBuilder()
            .add_state("idle", "idle_anim")
            .add_state("walk", "walk_anim")
            .add_transition("idle", "walk")
            .add_parameter("speed", 0.0)
        )

        state_machine = builder.build()

        assert len(state_machine.states) == 2
        assert len(state_machine.transitions) == 1


class TestStateMachineIntegration:
    """Integration tests for animation state machine"""

    def test_full_character_state_machine(self, animation_component):
        """Test complete character state machine"""
        state_machine = (
            AnimationStateMachineBuilder()
            .add_state("idle", "idle", loop=True)
            .add_state("walk", "walk", loop=True)
            .add_state("jump", "jump", loop=False)
            .add_parameter("speed", 0.0)
            .add_parameter("grounded", True)
            .add_transition(
                "idle",
                "walk",
                [TransitionCondition(TransitionConditionType.GREATER_THAN, "speed", 0.1)],
            )
            .add_transition(
                "walk",
                "idle",
                [TransitionCondition(TransitionConditionType.LESS_THAN, "speed", 0.1)],
            )
            .add_transition(
                "idle",
                "jump",
                [
                    TransitionCondition(TransitionConditionType.TRIGGER, "jump_trigger"),
                    TransitionCondition(TransitionConditionType.EQUALS, "grounded", True),
                ],
            )
            .add_transition(
                "jump",
                "idle",
                [TransitionCondition(TransitionConditionType.ANIMATION_FINISHED)],
            )
            .build()
        )

        state_machine.animation_component = animation_component

        # Start in idle
        assert state_machine.current_state == "idle"

        # Start walking
        state_machine.set_parameter("speed", 5.0)
        state_machine.update(0.016)
        assert state_machine.current_state == "walk"

        # Stop walking
        state_machine.set_parameter("speed", 0.0)
        state_machine.update(0.016)
        assert state_machine.current_state == "idle"

        # Jump
        state_machine.set_trigger("jump_trigger")
        state_machine.update(0.016)
        assert state_machine.current_state == "jump"

        # Finish jump
        animation_component.current_frame = 2
        animation_component.playing = False
        state_machine.update(0.016)
        assert state_machine.current_state == "idle"

    def test_state_machine_with_callbacks(self, animation_component):
        """Test state machine with entry/exit callbacks"""
        events = []

        state_machine = AnimationStateMachine()
        state_machine.animation_component = animation_component

        state_machine.add_state(
            AnimationState(
                "idle",
                "idle",
                on_enter=lambda: events.append("enter_idle"),
                on_exit=lambda: events.append("exit_idle"),
            )
        )
        state_machine.add_state(
            AnimationState(
                "walk",
                "walk",
                on_enter=lambda: events.append("enter_walk"),
                on_exit=lambda: events.append("exit_walk"),
            )
        )

        state_machine.change_state("walk")

        assert "exit_idle" in events
        assert "enter_walk" in events

    def test_get_current_state_info(self):
        """Test getting current state information"""
        state_machine = AnimationStateMachine()

        state_machine.add_state(AnimationState("idle", "idle_anim"))
        state_machine.add_state(AnimationState("walk", "walk_anim"))

        state_machine.change_state("walk")

        assert state_machine.get_current_state_name() == "walk"
        assert state_machine.get_current_state().animation_name == "walk_anim"
        assert state_machine.is_in_state("walk")
        assert not state_machine.is_in_state("idle")


# Run tests with: pytest engine/tests/test_animation_state_machine.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
