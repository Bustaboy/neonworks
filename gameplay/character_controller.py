"""
Character Controller

Player and NPC movement control with physics and animation integration.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple

from neonworks.core.ecs import (
    Collider,
    Component,
    Entity,
    RigidBody,
    System,
    Transform,
    World,
)
from neonworks.input.input_manager import InputManager
from neonworks.rendering.animation import AnimationComponent


class MovementState(Enum):
    """Character movement states"""

    IDLE = "idle"
    WALKING = "walking"
    RUNNING = "running"
    JUMPING = "jumping"
    FALLING = "falling"
    DASHING = "dashing"


@dataclass
class CharacterController(Component):
    """
    Character controller component for player and NPC movement.

    Handles movement input, collision response, and state management.
    """

    # Movement parameters
    move_speed: float = 200.0  # Pixels per second
    run_speed: float = 400.0
    acceleration: float = 1500.0  # How quickly speed changes
    friction: float = 800.0  # How quickly character stops

    # Jump parameters (for platformers)
    can_jump: bool = False
    jump_force: float = 500.0
    gravity: float = 1500.0

    # Dash parameters
    can_dash: bool = False
    dash_speed: float = 800.0
    dash_duration: float = 0.2
    dash_cooldown: float = 1.0

    # State
    movement_state: MovementState = MovementState.IDLE
    facing_direction: Tuple[float, float] = (1.0, 0.0)  # Direction character is facing
    is_grounded: bool = True
    is_dashing: bool = False

    # Internal timers
    dash_timer: float = 0.0
    dash_cooldown_timer: float = 0.0

    # Control flags
    is_player_controlled: bool = True
    is_frozen: bool = False  # Disables all movement

    # Input configuration (for rebindable controls)
    input_move_left: str = "move_left"
    input_move_right: str = "move_right"
    input_move_up: str = "move_up"
    input_move_down: str = "move_down"
    input_run: str = "run"
    input_jump: str = "jump"
    input_dash: str = "dash"


class CharacterControllerSystem(System):
    """
    System that updates character controllers.

    Handles input processing, movement, and animation state updates.
    """

    def __init__(self, input_manager: Optional[InputManager] = None):
        super().__init__()
        self.input_manager = input_manager
        self.priority = 5  # Run before collision resolution

    def update(self, world: World, delta_time: float):
        """Update all character controllers"""
        for entity in world.get_entities_with_component(CharacterController):
            controller = entity.get_component(CharacterController)
            transform = entity.get_component(Transform)
            rigidbody = entity.get_component(RigidBody)

            if not transform or not controller:
                continue

            # Skip if frozen
            if controller.is_frozen:
                continue

            # Update timers
            self._update_timers(controller, delta_time)

            # Get movement input
            move_direction = self._get_movement_input(controller, entity)

            # Apply movement
            if rigidbody:
                self._apply_movement_with_physics(
                    controller, rigidbody, move_direction, delta_time
                )
            else:
                self._apply_movement_direct(
                    controller, transform, move_direction, delta_time
                )

            # Update movement state
            self._update_movement_state(controller, rigidbody, move_direction)

            # Update animations
            self._update_animations(controller, entity)

    def _update_timers(self, controller: CharacterController, delta_time: float):
        """Update internal timers"""
        if controller.is_dashing:
            controller.dash_timer -= delta_time
            if controller.dash_timer <= 0:
                controller.is_dashing = False

        if controller.dash_cooldown_timer > 0:
            controller.dash_cooldown_timer -= delta_time

    def _get_movement_input(
        self, controller: CharacterController, entity: Entity
    ) -> Tuple[float, float]:
        """
        Get movement direction from input.

        Returns:
            (x, y) direction vector (not normalized)
        """
        if not controller.is_player_controlled or not self.input_manager:
            return (0.0, 0.0)

        # Get input axes
        horizontal = 0.0
        vertical = 0.0

        # Horizontal movement
        if self.input_manager.is_action_pressed(controller.input_move_left):
            horizontal -= 1.0
        if self.input_manager.is_action_pressed(controller.input_move_right):
            horizontal += 1.0

        # Vertical movement (for top-down games)
        if self.input_manager.is_action_pressed(controller.input_move_up):
            vertical -= 1.0
        if self.input_manager.is_action_pressed(controller.input_move_down):
            vertical += 1.0

        # Handle dash
        if controller.can_dash and self.input_manager.is_action_just_pressed(
            controller.input_dash
        ):
            if controller.dash_cooldown_timer <= 0 and (
                horizontal != 0 or vertical != 0
            ):
                controller.is_dashing = True
                controller.dash_timer = controller.dash_duration
                controller.dash_cooldown_timer = controller.dash_cooldown

        # Handle jump
        if controller.can_jump and controller.is_grounded:
            if self.input_manager.is_action_just_pressed(controller.input_jump):
                # Jump is handled by applying velocity, done in apply_movement
                pass

        return (horizontal, vertical)

    def _apply_movement_with_physics(
        self,
        controller: CharacterController,
        rigidbody: RigidBody,
        move_direction: Tuple[float, float],
        delta_time: float,
    ):
        """Apply movement using physics/rigidbody"""
        horizontal, vertical = move_direction

        # Determine target speed
        if controller.is_dashing:
            target_speed = controller.dash_speed
        elif self.input_manager and self.input_manager.is_action_pressed(
            controller.input_run
        ):
            target_speed = controller.run_speed
        else:
            target_speed = controller.move_speed

        # Calculate target velocity
        target_velocity_x = horizontal * target_speed
        target_velocity_y = vertical * target_speed

        # Apply acceleration/friction
        if horizontal != 0:
            # Accelerate
            accel = controller.acceleration * delta_time
            if rigidbody.velocity_x < target_velocity_x:
                rigidbody.velocity_x = min(
                    rigidbody.velocity_x + accel, target_velocity_x
                )
            else:
                rigidbody.velocity_x = max(
                    rigidbody.velocity_x - accel, target_velocity_x
                )
        else:
            # Apply friction
            friction = controller.friction * delta_time
            if abs(rigidbody.velocity_x) < friction:
                rigidbody.velocity_x = 0
            elif rigidbody.velocity_x > 0:
                rigidbody.velocity_x -= friction
            else:
                rigidbody.velocity_x += friction

        # Vertical movement (for top-down) or gravity (for platformer)
        if controller.can_jump:
            # Platformer mode: apply gravity
            if not controller.is_grounded:
                rigidbody.velocity_y += controller.gravity * delta_time

            # Handle jump
            if controller.is_grounded and self.input_manager:
                if self.input_manager.is_action_just_pressed(controller.input_jump):
                    rigidbody.velocity_y = -controller.jump_force
                    controller.is_grounded = False
        else:
            # Top-down mode: same logic for vertical
            if vertical != 0:
                accel = controller.acceleration * delta_time
                if rigidbody.velocity_y < target_velocity_y:
                    rigidbody.velocity_y = min(
                        rigidbody.velocity_y + accel, target_velocity_y
                    )
                else:
                    rigidbody.velocity_y = max(
                        rigidbody.velocity_y - accel, target_velocity_y
                    )
            else:
                friction = controller.friction * delta_time
                if abs(rigidbody.velocity_y) < friction:
                    rigidbody.velocity_y = 0
                elif rigidbody.velocity_y > 0:
                    rigidbody.velocity_y -= friction
                else:
                    rigidbody.velocity_y += friction

        # Update facing direction
        if horizontal != 0 or vertical != 0:
            controller.facing_direction = (horizontal, vertical)

    def _apply_movement_direct(
        self,
        controller: CharacterController,
        transform: Transform,
        move_direction: Tuple[float, float],
        delta_time: float,
    ):
        """Apply movement directly to transform (no physics)"""
        horizontal, vertical = move_direction

        if horizontal == 0 and vertical == 0:
            return

        # Determine speed
        if controller.is_dashing:
            speed = controller.dash_speed
        elif self.input_manager and self.input_manager.is_action_pressed(
            controller.input_run
        ):
            speed = controller.run_speed
        else:
            speed = controller.move_speed

        # Normalize diagonal movement
        length = (horizontal * horizontal + vertical * vertical) ** 0.5
        if length > 0:
            horizontal /= length
            vertical /= length

        # Apply movement
        transform.x += horizontal * speed * delta_time
        transform.y += vertical * speed * delta_time

        # Update facing direction
        controller.facing_direction = (horizontal, vertical)

    def _update_movement_state(
        self,
        controller: CharacterController,
        rigidbody: Optional[RigidBody],
        move_direction: Tuple[float, float],
    ):
        """Update the character's movement state"""
        horizontal, vertical = move_direction

        # Check if moving
        is_moving = horizontal != 0 or vertical != 0

        if rigidbody:
            # Use velocity to determine state
            speed = (rigidbody.velocity_x**2 + rigidbody.velocity_y**2) ** 0.5
            is_moving = speed > 10.0  # Small threshold

        # Update state
        if controller.is_dashing:
            controller.movement_state = MovementState.DASHING
        elif controller.can_jump:
            # Platformer states
            if not controller.is_grounded:
                if rigidbody and rigidbody.velocity_y > 0:
                    controller.movement_state = MovementState.FALLING
                else:
                    controller.movement_state = MovementState.JUMPING
            elif is_moving:
                if self.input_manager and self.input_manager.is_action_pressed("run"):
                    controller.movement_state = MovementState.RUNNING
                else:
                    controller.movement_state = MovementState.WALKING
            else:
                controller.movement_state = MovementState.IDLE
        else:
            # Top-down states
            if is_moving:
                if self.input_manager and self.input_manager.is_action_pressed("run"):
                    controller.movement_state = MovementState.RUNNING
                else:
                    controller.movement_state = MovementState.WALKING
            else:
                controller.movement_state = MovementState.IDLE

    def _update_animations(self, controller: CharacterController, entity: Entity):
        """Update animation based on movement state"""
        anim_component = entity.get_component(AnimationComponent)
        if not anim_component:
            return

        # Map movement state to animation name
        animation_map = {
            MovementState.IDLE: "idle",
            MovementState.WALKING: "walk",
            MovementState.RUNNING: "run",
            MovementState.JUMPING: "jump",
            MovementState.FALLING: "fall",
            MovementState.DASHING: "dash",
        }

        target_animation = animation_map.get(controller.movement_state, "idle")

        # Only change if different
        if anim_component.current_animation != target_animation:
            # Check if animation exists before playing
            if target_animation in anim_component.animations:
                anim_component.play(target_animation)


@dataclass
class AIController(Component):
    """
    AI controller for NPCs.

    Works with CharacterController to provide autonomous movement.
    """

    # AI behavior type
    behavior: str = "wander"  # wander, patrol, chase, flee, idle

    # Wander parameters
    wander_radius: float = 200.0
    wander_change_time: float = 2.0
    wander_timer: float = 0.0
    wander_target: Tuple[float, float] = (0.0, 0.0)

    # Patrol parameters
    patrol_points: list = field(default_factory=list)
    patrol_index: int = 0
    patrol_loop: bool = True

    # Chase/flee parameters
    target_entity: Optional[Entity] = None
    chase_range: float = 300.0
    flee_range: float = 200.0

    # Speed override (None = use CharacterController's speed)
    ai_move_speed: Optional[float] = None


class AIControllerSystem(System):
    """System that updates AI controllers"""

    def __init__(self):
        super().__init__()
        self.priority = 4  # Run before character controller

    def update(self, world: World, delta_time: float):
        """Update all AI controllers"""
        for entity in world.get_entities_with_component(AIController):
            ai = entity.get_component(AIController)
            controller = entity.get_component(CharacterController)
            transform = entity.get_component(Transform)

            if not ai or not controller or not transform:
                continue

            # AI shouldn't be player-controlled
            controller.is_player_controlled = False

            # Update AI behavior
            if ai.behavior == "wander":
                self._update_wander(ai, controller, transform, delta_time)
            elif ai.behavior == "patrol":
                self._update_patrol(ai, controller, transform, delta_time)
            elif ai.behavior == "chase":
                self._update_chase(ai, controller, transform, delta_time)
            elif ai.behavior == "flee":
                self._update_flee(ai, controller, transform, delta_time)
            # idle behavior = do nothing

    def _update_wander(
        self,
        ai: AIController,
        controller: CharacterController,
        transform: Transform,
        delta_time: float,
    ):
        """Random wandering behavior"""
        import random

        ai.wander_timer -= delta_time

        if ai.wander_timer <= 0:
            # Choose new random target
            angle = random.uniform(0, 2 * 3.14159)
            distance = random.uniform(50, ai.wander_radius)
            ai.wander_target = (
                transform.x + distance * (angle**0.5),  # Simplified random direction
                transform.y + distance * ((1 - angle / 6.28) ** 0.5),
            )
            ai.wander_timer = ai.wander_change_time

        # Move towards target
        self._move_towards(controller, transform, ai.wander_target, ai.ai_move_speed)

    def _update_patrol(
        self,
        ai: AIController,
        controller: CharacterController,
        transform: Transform,
        delta_time: float,
    ):
        """Patrol between waypoints"""
        if not ai.patrol_points or len(ai.patrol_points) == 0:
            return

        # Get current patrol point
        target = ai.patrol_points[ai.patrol_index]

        # Check if reached
        dx = target[0] - transform.x
        dy = target[1] - transform.y
        distance = (dx * dx + dy * dy) ** 0.5

        if distance < 10:  # Reached waypoint
            # Move to next point
            ai.patrol_index += 1
            if ai.patrol_index >= len(ai.patrol_points):
                if ai.patrol_loop:
                    ai.patrol_index = 0
                else:
                    ai.patrol_index = len(ai.patrol_points) - 1
                    # Could reverse here instead

        # Move towards current point
        self._move_towards(controller, transform, target, ai.ai_move_speed)

    def _update_chase(
        self,
        ai: AIController,
        controller: CharacterController,
        transform: Transform,
        delta_time: float,
    ):
        """Chase target entity"""
        if not ai.target_entity:
            return

        target_transform = ai.target_entity.get_component(Transform)
        if not target_transform:
            return

        # Check distance
        dx = target_transform.x - transform.x
        dy = target_transform.y - transform.y
        distance = (dx * dx + dy * dy) ** 0.5

        if distance > ai.chase_range:
            # Too far, stop
            return

        # Move towards target
        self._move_towards(
            controller,
            transform,
            (target_transform.x, target_transform.y),
            ai.ai_move_speed,
        )

    def _update_flee(
        self,
        ai: AIController,
        controller: CharacterController,
        transform: Transform,
        delta_time: float,
    ):
        """Flee from target entity"""
        if not ai.target_entity:
            return

        target_transform = ai.target_entity.get_component(Transform)
        if not target_transform:
            return

        # Check distance
        dx = target_transform.x - transform.x
        dy = target_transform.y - transform.y
        distance = (dx * dx + dy * dy) ** 0.5

        if distance > ai.flee_range:
            # Safe distance, stop
            return

        # Move away from target
        flee_point = (transform.x - dx, transform.y - dy)
        self._move_towards(controller, transform, flee_point, ai.ai_move_speed)

    def _move_towards(
        self,
        controller: CharacterController,
        transform: Transform,
        target: Tuple[float, float],
        speed_override: Optional[float],
    ):
        """Helper to set movement direction towards target"""
        dx = target[0] - transform.x
        dy = target[1] - transform.y
        distance = (dx * dx + dy * dy) ** 0.5

        if distance < 1.0:
            controller.facing_direction = (0.0, 0.0)
            return

        # Normalize direction
        controller.facing_direction = (dx / distance, dy / distance)

        # Override speed if specified
        if speed_override is not None:
            controller.move_speed = speed_override
