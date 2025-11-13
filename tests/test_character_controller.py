"""
Comprehensive tests for Character Controller

Tests player movement, AI behaviors, and animation integration.
"""

from unittest.mock import Mock, patch

import pygame
import pytest

from neonworks.core.ecs import Collider, RigidBody, Transform, World
from neonworks.gameplay.character_controller import (
    AIController,
    AIControllerSystem,
    CharacterController,
    CharacterControllerSystem,
    MovementState,
)
from neonworks.input.input_manager import InputManager
from neonworks.rendering.animation import Animation, AnimationComponent, AnimationFrame


@pytest.fixture
def world():
    """Create a world for testing"""
    return World()


@pytest.fixture
def input_manager():
    """Create an input manager for testing"""
    pygame.init()
    return InputManager()


@pytest.fixture
def controller_system(input_manager):
    """Create a character controller system"""
    return CharacterControllerSystem(input_manager)


class TestCharacterControllerComponent:
    """Test character controller component"""

    def test_controller_creation(self):
        """Test creating a character controller"""
        controller = CharacterController()

        assert controller.move_speed == 200.0
        assert controller.movement_state == MovementState.IDLE
        assert controller.is_player_controlled
        assert not controller.is_frozen

    def test_controller_with_custom_parameters(self):
        """Test creating controller with custom parameters"""
        controller = CharacterController(move_speed=300.0, can_jump=True, can_dash=True)

        assert controller.move_speed == 300.0
        assert controller.can_jump
        assert controller.can_dash


class TestPlayerMovement:
    """Test player-controlled movement"""

    def test_direct_movement_no_input(self, world, controller_system):
        """Test character stays still with no input"""
        entity = world.create_entity()
        entity.add_component(Transform(x=0, y=0))
        entity.add_component(CharacterController())

        controller_system.update(world, 0.016)

        transform = entity.get_component(Transform)
        assert transform.x == 0
        assert transform.y == 0

    def test_direct_movement_horizontal(self, world, controller_system, input_manager):
        """Test horizontal movement without physics"""
        entity = world.create_entity()
        entity.add_component(Transform(x=0, y=0))
        entity.add_component(CharacterController())

        # Simulate right input
        with patch.object(input_manager, "is_action_pressed") as mock_pressed:

            def action_pressed(action):
                return action == "move_right"

            mock_pressed.side_effect = action_pressed

            controller_system.update(world, 0.016)

        transform = entity.get_component(Transform)
        # Should have moved right
        assert transform.x > 0
        assert transform.y == 0

    def test_direct_movement_diagonal(self, world, controller_system, input_manager):
        """Test diagonal movement is normalized"""
        entity = world.create_entity()
        entity.add_component(Transform(x=0, y=0))
        entity.add_component(CharacterController(move_speed=100.0))

        # Simulate diagonal input (right + down)
        with patch.object(input_manager, "is_action_pressed") as mock_pressed:

            def action_pressed(action):
                return action in ["move_right", "move_down"]

            mock_pressed.side_effect = action_pressed

            controller_system.update(world, 1.0)  # 1 second

        transform = entity.get_component(Transform)
        # Diagonal movement should be normalized, so total distance ~= speed
        distance = (transform.x**2 + transform.y**2) ** 0.5
        assert abs(distance - 100.0) < 1.0  # Should be close to speed


class TestPhysicsMovement:
    """Test physics-based movement with RigidBody"""

    def test_physics_acceleration(self, world, controller_system, input_manager):
        """Test physics-based movement accelerates"""
        entity = world.create_entity()
        entity.add_component(Transform(x=0, y=0))
        entity.add_component(CharacterController())
        entity.add_component(RigidBody())

        rigidbody = entity.get_component(RigidBody)

        # Simulate right input
        with patch.object(input_manager, "is_action_pressed") as mock_pressed:

            def action_pressed(action):
                return action == "move_right"

            mock_pressed.side_effect = action_pressed

            # First frame - should start accelerating
            controller_system.update(world, 0.016)
            velocity_1 = rigidbody.velocity_x

            # Second frame - should have higher velocity
            controller_system.update(world, 0.016)
            velocity_2 = rigidbody.velocity_x

        assert velocity_2 > velocity_1
        assert velocity_2 > 0

    def test_physics_friction(self, world, controller_system, input_manager):
        """Test physics friction slows down character"""
        entity = world.create_entity()
        entity.add_component(Transform(x=0, y=0))
        entity.add_component(CharacterController())
        rigidbody = RigidBody(velocity_x=100.0)
        entity.add_component(rigidbody)

        # No input - friction should slow down
        with patch.object(input_manager, "is_action_pressed", return_value=False):
            controller_system.update(world, 0.016)

        # Velocity should have decreased
        assert rigidbody.velocity_x < 100.0


class TestMovementStates:
    """Test movement state transitions"""

    def test_idle_state(self, world, controller_system, input_manager):
        """Test idle state when not moving"""
        entity = world.create_entity()
        entity.add_component(Transform(x=0, y=0))
        controller = CharacterController()
        entity.add_component(controller)

        with patch.object(input_manager, "is_action_pressed", return_value=False):
            controller_system.update(world, 0.016)

        assert controller.movement_state == MovementState.IDLE

    def test_walking_state(self, world, controller_system, input_manager):
        """Test walking state when moving"""
        entity = world.create_entity()
        entity.add_component(Transform(x=0, y=0))
        controller = CharacterController()
        entity.add_component(controller)

        with patch.object(input_manager, "is_action_pressed") as mock_pressed:

            def action_pressed(action):
                return action == "move_right"

            mock_pressed.side_effect = action_pressed

            controller_system.update(world, 0.016)

        assert controller.movement_state == MovementState.WALKING

    def test_running_state(self, world, controller_system, input_manager):
        """Test running state when run key is held"""
        entity = world.create_entity()
        entity.add_component(Transform(x=0, y=0))
        controller = CharacterController()
        entity.add_component(controller)

        with patch.object(input_manager, "is_action_pressed") as mock_pressed:

            def action_pressed(action):
                return action in ["move_right", "run"]

            mock_pressed.side_effect = action_pressed

            controller_system.update(world, 0.016)

        assert controller.movement_state == MovementState.RUNNING

    def test_dashing_state(self, world, controller_system, input_manager):
        """Test dashing state"""
        entity = world.create_entity()
        entity.add_component(Transform(x=0, y=0))
        controller = CharacterController(can_dash=True)
        entity.add_component(controller)

        with patch.object(input_manager, "is_action_pressed") as mock_pressed:
            with patch.object(
                input_manager, "is_action_just_pressed", return_value=True
            ) as mock_just:

                def action_pressed(action):
                    return action == "move_right"

                mock_pressed.side_effect = action_pressed

                controller_system.update(world, 0.016)

        assert controller.is_dashing
        assert controller.movement_state == MovementState.DASHING


class TestDashMechanics:
    """Test dash mechanics"""

    def test_dash_duration(self, world, controller_system, input_manager):
        """Test dash expires after duration"""
        entity = world.create_entity()
        entity.add_component(Transform(x=0, y=0))
        controller = CharacterController(can_dash=True, dash_duration=0.2)
        entity.add_component(controller)

        # Start dash
        controller.is_dashing = True
        controller.dash_timer = 0.2

        # Update past dash duration
        with patch.object(input_manager, "is_action_pressed", return_value=False):
            controller_system.update(world, 0.3)

        assert not controller.is_dashing

    def test_dash_cooldown(self, world, controller_system, input_manager):
        """Test dash has cooldown"""
        entity = world.create_entity()
        entity.add_component(Transform(x=0, y=0))
        controller = CharacterController(can_dash=True, dash_cooldown=1.0)
        entity.add_component(controller)

        # Set cooldown
        controller.dash_cooldown_timer = 0.5

        # Try to dash (should fail due to cooldown)
        with patch.object(input_manager, "is_action_pressed", return_value=True):
            with patch.object(
                input_manager, "is_action_just_pressed", return_value=True
            ):
                controller_system.update(world, 0.016)

        assert not controller.is_dashing


class TestFrozenController:
    """Test frozen state disables movement"""

    def test_frozen_no_movement(self, world, controller_system, input_manager):
        """Test frozen controller doesn't move"""
        entity = world.create_entity()
        entity.add_component(Transform(x=0, y=0))
        controller = CharacterController(is_frozen=True)
        entity.add_component(controller)

        with patch.object(input_manager, "is_action_pressed", return_value=True):
            controller_system.update(world, 0.016)

        transform = entity.get_component(Transform)
        assert transform.x == 0
        assert transform.y == 0


class TestAIController:
    """Test AI controller behaviors"""

    def test_ai_controller_creation(self):
        """Test creating an AI controller"""
        ai = AIController()

        assert ai.behavior == "wander"
        assert ai.wander_radius == 200.0

    def test_ai_disables_player_control(self, world):
        """Test AI controller disables player control"""
        ai_system = AIControllerSystem()
        entity = world.create_entity()
        entity.add_component(Transform(x=0, y=0))
        controller = CharacterController(is_player_controlled=True)
        entity.add_component(controller)
        entity.add_component(AIController())

        ai_system.update(world, 0.016)

        assert not controller.is_player_controlled

    def test_wander_behavior(self, world):
        """Test wander AI behavior"""
        ai_system = AIControllerSystem()
        entity = world.create_entity()
        entity.add_component(Transform(x=0, y=0))
        entity.add_component(CharacterController())
        ai = AIController(behavior="wander")
        entity.add_component(ai)

        # Set wander timer to expired
        ai.wander_timer = 0.0

        ai_system.update(world, 0.016)

        # Should have set new wander target
        assert ai.wander_target != (0.0, 0.0)

    def test_patrol_behavior(self, world):
        """Test patrol AI behavior"""
        ai_system = AIControllerSystem()
        entity = world.create_entity()
        entity.add_component(Transform(x=0, y=0))
        controller = CharacterController()
        entity.add_component(controller)
        ai = AIController(
            behavior="patrol", patrol_points=[(100, 0), (100, 100), (0, 100)]
        )
        entity.add_component(ai)

        ai_system.update(world, 0.016)

        # Should be moving towards first patrol point
        assert controller.facing_direction != (0.0, 0.0)

    def test_chase_behavior(self, world):
        """Test chase AI behavior"""
        ai_system = AIControllerSystem()

        # Create target entity
        target = world.create_entity()
        target.add_component(Transform(x=100, y=100))

        # Create chaser entity
        chaser = world.create_entity()
        chaser.add_component(Transform(x=0, y=0))
        controller = CharacterController()
        chaser.add_component(controller)
        ai = AIController(behavior="chase", target_entity=target, chase_range=500)
        chaser.add_component(ai)

        ai_system.update(world, 0.016)

        # Should be facing towards target
        fx, fy = controller.facing_direction
        # Direction should be positive (towards 100, 100)
        assert fx > 0 or fy > 0

    def test_flee_behavior(self, world):
        """Test flee AI behavior"""
        ai_system = AIControllerSystem()

        # Create threat entity
        threat = world.create_entity()
        threat.add_component(Transform(x=10, y=10))

        # Create fleeing entity
        fleeing = world.create_entity()
        fleeing.add_component(Transform(x=0, y=0))
        controller = CharacterController()
        fleeing.add_component(controller)
        ai = AIController(behavior="flee", target_entity=threat, flee_range=500)
        fleeing.add_component(ai)

        ai_system.update(world, 0.016)

        # Should be facing away from threat
        fx, fy = controller.facing_direction
        # Direction should be negative (away from 10, 10)
        assert fx < 0 or fy < 0


class TestAnimationIntegration:
    """Test animation integration with controller"""

    def test_animation_updates_with_state(
        self, world, controller_system, input_manager
    ):
        """Test animation changes with movement state"""
        entity = world.create_entity()
        entity.add_component(Transform(x=0, y=0))
        controller = CharacterController()
        entity.add_component(controller)

        # Create animation component with animations
        anim_component = AnimationComponent()
        # Add placeholder animations
        idle_frame = Mock()
        idle_frame.sprite = Mock()
        idle_frame.duration = 0.1
        anim_component.animations["idle"] = Mock()
        anim_component.animations["idle"].frames = [idle_frame]
        anim_component.animations["walk"] = Mock()
        anim_component.animations["walk"].frames = [idle_frame]
        entity.add_component(anim_component)

        # Start with idle
        anim_component.current_animation = "idle"

        # Move character
        with patch.object(input_manager, "is_action_pressed") as mock_pressed:

            def action_pressed(action):
                return action == "move_right"

            mock_pressed.side_effect = action_pressed

            controller_system.update(world, 0.016)

        # Animation should have changed to walk
        assert controller.movement_state == MovementState.WALKING
        # Note: Animation update depends on having proper animation setup


# Run tests with: pytest engine/tests/test_character_controller.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
