"""
Rigid Body Physics System

Physics simulation with forces, velocity, and collision response.
"""

from typing import Tuple, Optional
from dataclasses import dataclass, field
from engine.core.ecs import Component, Entity, World, Transform
from engine.physics.collision import Collider, CollisionInfo
import math


@dataclass
class RigidBody(Component):
    """Rigid body component for physics simulation"""

    # Linear motion
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    acceleration_x: float = 0.0
    acceleration_y: float = 0.0

    # Forces
    force_x: float = 0.0
    force_y: float = 0.0

    # Physical properties
    mass: float = 1.0
    drag: float = 0.0  # Air resistance (0 = no drag, higher = more drag)
    gravity_scale: float = 1.0  # Multiplier for gravity

    # Collision response
    restitution: float = 0.0  # Bounciness (0 = no bounce, 1 = perfect bounce)
    is_kinematic: bool = False  # If True, not affected by forces/gravity
    is_static: bool = False  # If True, doesn't move at all

    # Constraints
    freeze_position_x: bool = False
    freeze_position_y: bool = False
    freeze_rotation: bool = True  # For future rotation support

    def add_force(self, force_x: float, force_y: float):
        """Add force to the rigid body"""
        if not self.is_static and not self.is_kinematic:
            self.force_x += force_x
            self.force_y += force_y

    def add_impulse(self, impulse_x: float, impulse_y: float):
        """Add instant velocity change (impulse = force * dt)"""
        if not self.is_static:
            if self.mass > 0:
                self.velocity_x += impulse_x / self.mass
                self.velocity_y += impulse_y / self.mass

    def set_velocity(self, velocity_x: float, velocity_y: float):
        """Set velocity directly"""
        if not self.is_static:
            self.velocity_x = velocity_x
            self.velocity_y = velocity_y

    def get_speed(self) -> float:
        """Get current speed (magnitude of velocity)"""
        return math.sqrt(self.velocity_x ** 2 + self.velocity_y ** 2)

    def get_kinetic_energy(self) -> float:
        """Get kinetic energy (0.5 * m * v^2)"""
        speed = self.get_speed()
        return 0.5 * self.mass * speed * speed


@dataclass
class PhysicsSettings:
    """Global physics settings"""
    gravity_x: float = 0.0
    gravity_y: float = 9.81  # Pixels per second squared
    max_velocity: float = 1000.0  # Maximum velocity cap
    max_delta_time: float = 0.1  # Maximum allowed delta time (prevents instability)
    position_iterations: int = 3  # Iterations for collision resolution
    velocity_threshold: float = 0.01  # Minimum velocity to keep moving


class PhysicsSystem:
    """System for physics simulation"""

    def __init__(self, settings: Optional[PhysicsSettings] = None):
        self.settings = settings or PhysicsSettings()

    def update(self, world: World, delta_time: float):
        """
        Update physics for all entities.

        Args:
            world: Game world
            delta_time: Time step in seconds
        """
        # Clamp delta_time to prevent physics explosions
        delta_time = min(delta_time, self.settings.max_delta_time)

        # Update all rigid bodies
        for entity in world._entities.values():
            rigidbody = entity.get_component(RigidBody)
            transform = entity.get_component(Transform)

            if rigidbody and transform:
                self._update_rigidbody(rigidbody, transform, delta_time)

    def _update_rigidbody(self, rigidbody: RigidBody, transform: Transform,
                          delta_time: float):
        """Update a single rigid body"""
        if rigidbody.is_static:
            return

        # Apply gravity
        if not rigidbody.is_kinematic and rigidbody.gravity_scale != 0:
            rigidbody.acceleration_y += (self.settings.gravity_y *
                                        rigidbody.gravity_scale)

        # Apply forces (F = ma, so a = F/m)
        if not rigidbody.is_kinematic and rigidbody.mass > 0:
            rigidbody.acceleration_x += rigidbody.force_x / rigidbody.mass
            rigidbody.acceleration_y += rigidbody.force_y / rigidbody.mass

        # Update velocity from acceleration
        rigidbody.velocity_x += rigidbody.acceleration_x * delta_time
        rigidbody.velocity_y += rigidbody.acceleration_y * delta_time

        # Apply drag
        if rigidbody.drag > 0:
            drag_factor = max(0, 1.0 - rigidbody.drag * delta_time)
            rigidbody.velocity_x *= drag_factor
            rigidbody.velocity_y *= drag_factor

        # Clamp velocity
        speed = rigidbody.get_speed()
        if speed > self.settings.max_velocity:
            scale = self.settings.max_velocity / speed
            rigidbody.velocity_x *= scale
            rigidbody.velocity_y *= scale

        # Apply velocity threshold (stop very slow objects)
        if abs(rigidbody.velocity_x) < self.settings.velocity_threshold:
            rigidbody.velocity_x = 0
        if abs(rigidbody.velocity_y) < self.settings.velocity_threshold:
            rigidbody.velocity_y = 0

        # Update position from velocity
        if not rigidbody.freeze_position_x:
            transform.x += rigidbody.velocity_x * delta_time
        if not rigidbody.freeze_position_y:
            transform.y += rigidbody.velocity_y * delta_time

        # Reset forces and acceleration for next frame
        rigidbody.force_x = 0
        rigidbody.force_y = 0
        rigidbody.acceleration_x = 0
        rigidbody.acceleration_y = 0

    def apply_collision_response(self, entity_a: Entity, entity_b: Entity,
                                 collision_info: CollisionInfo):
        """
        Apply physics response to a collision.

        Args:
            entity_a: First entity
            entity_b: Second entity
            collision_info: Collision information
        """
        rigidbody_a = entity_a.get_component(RigidBody)
        rigidbody_b = entity_b.get_component(RigidBody)
        transform_a = entity_a.get_component(Transform)
        transform_b = entity_b.get_component(Transform)
        collider_a = entity_a.get_component(Collider)
        collider_b = entity_b.get_component(Collider)

        if not all([transform_a, transform_b]):
            return

        # If both are triggers, no physical response
        if collider_a and collider_b and collider_a.is_trigger and collider_b.is_trigger:
            return

        normal_x, normal_y = collision_info.normal
        penetration = collision_info.penetration

        # Determine which bodies can move
        a_can_move = rigidbody_a and not rigidbody_a.is_static
        b_can_move = rigidbody_b and not rigidbody_b.is_static

        if not a_can_move and not b_can_move:
            return

        # Positional correction (separate overlapping objects)
        correction_percent = 0.8  # How much of the penetration to correct
        correction = penetration * correction_percent

        if a_can_move and b_can_move:
            # Both can move - split correction
            mass_sum = rigidbody_a.mass + rigidbody_b.mass
            a_ratio = rigidbody_b.mass / mass_sum if mass_sum > 0 else 0.5
            b_ratio = rigidbody_a.mass / mass_sum if mass_sum > 0 else 0.5

            if not rigidbody_a.freeze_position_x:
                transform_a.x -= normal_x * correction * a_ratio
            if not rigidbody_a.freeze_position_y:
                transform_a.y -= normal_y * correction * a_ratio
            if not rigidbody_b.freeze_position_x:
                transform_b.x += normal_x * correction * b_ratio
            if not rigidbody_b.freeze_position_y:
                transform_b.y += normal_y * correction * b_ratio
        elif a_can_move:
            # Only A can move
            if not rigidbody_a.freeze_position_x:
                transform_a.x -= normal_x * correction
            if not rigidbody_a.freeze_position_y:
                transform_a.y -= normal_y * correction
        else:
            # Only B can move
            if not rigidbody_b.freeze_position_x:
                transform_b.x += normal_x * correction
            if not rigidbody_b.freeze_position_y:
                transform_b.y += normal_y * correction

        # Velocity correction (bounce/friction)
        if rigidbody_a and rigidbody_b:
            self._resolve_collision_velocity(
                rigidbody_a, rigidbody_b, normal_x, normal_y
            )
        elif rigidbody_a:
            # Collision with static object
            self._resolve_static_collision_velocity(
                rigidbody_a, normal_x, normal_y, rigidbody_a.restitution
            )
        elif rigidbody_b:
            # Collision with static object (reversed normal)
            self._resolve_static_collision_velocity(
                rigidbody_b, -normal_x, -normal_y, rigidbody_b.restitution
            )

    def _resolve_collision_velocity(self, rigidbody_a: RigidBody,
                                    rigidbody_b: RigidBody,
                                    normal_x: float, normal_y: float):
        """Resolve velocity after collision between two dynamic objects"""
        # Relative velocity
        rel_vel_x = rigidbody_b.velocity_x - rigidbody_a.velocity_x
        rel_vel_y = rigidbody_b.velocity_y - rigidbody_a.velocity_y

        # Velocity along normal
        vel_along_normal = rel_vel_x * normal_x + rel_vel_y * normal_y

        # Don't resolve if velocities are separating (positive relative velocity)
        if vel_along_normal > 0:
            return

        # Calculate restitution (bounciness)
        restitution = min(rigidbody_a.restitution, rigidbody_b.restitution)

        # Calculate impulse scalar
        impulse_scalar = -(1 + restitution) * vel_along_normal

        if rigidbody_a.mass > 0 and rigidbody_b.mass > 0:
            impulse_scalar /= (1.0 / rigidbody_a.mass + 1.0 / rigidbody_b.mass)

        # Apply impulse
        impulse_x = impulse_scalar * normal_x
        impulse_y = impulse_scalar * normal_y

        if not rigidbody_a.is_static and not rigidbody_a.is_kinematic:
            rigidbody_a.velocity_x -= impulse_x / rigidbody_a.mass
            rigidbody_a.velocity_y -= impulse_y / rigidbody_a.mass

        if not rigidbody_b.is_static and not rigidbody_b.is_kinematic:
            rigidbody_b.velocity_x += impulse_x / rigidbody_b.mass
            rigidbody_b.velocity_y += impulse_y / rigidbody_b.mass

    def _resolve_static_collision_velocity(self, rigidbody: RigidBody,
                                          normal_x: float, normal_y: float,
                                          restitution: float):
        """Resolve velocity after collision with static object"""
        # Velocity along normal (from object towards static)
        vel_along_normal = (rigidbody.velocity_x * normal_x +
                          rigidbody.velocity_y * normal_y)

        # Don't resolve if velocity is separating (away from static object)
        # Negative vel_along_normal means moving away from collision
        if vel_along_normal < 0:
            return

        # Remove velocity component along normal and add bounce
        rigidbody.velocity_x -= (1 + restitution) * vel_along_normal * normal_x
        rigidbody.velocity_y -= (1 + restitution) * vel_along_normal * normal_y


class IntegratedPhysicsSystem:
    """
    Combined physics and collision system.

    Handles both physics simulation and collision detection/response.
    """

    def __init__(self, world_bounds: Optional[Tuple[float, float, float, float]] = None,
                 physics_settings: Optional[PhysicsSettings] = None):
        from engine.physics.collision import CollisionSystem

        self.physics_system = PhysicsSystem(physics_settings)
        self.collision_system = CollisionSystem(world_bounds)

        # Track collisions for physics response
        self._collision_pairs: set = set()

    def update(self, world: World, delta_time: float):
        """
        Update physics and collision detection.

        Args:
            world: Game world
            delta_time: Time step in seconds
        """
        # Update physics first
        self.physics_system.update(world, delta_time)

        # Then detect and resolve collisions
        self._detect_and_resolve_collisions(world)

    def _detect_and_resolve_collisions(self, world: World):
        """Detect collisions and apply physics responses"""
        from engine.physics.collision import CollisionDetector, Collider

        # Get all entities with colliders
        entities_with_colliders = []
        for entity in world._entities.values():
            if entity.get_component(Collider) and entity.get_component(Transform):
                entities_with_colliders.append(entity)

        # Check collisions and apply responses
        for i, entity_a in enumerate(entities_with_colliders):
            for entity_b in entities_with_colliders[i + 1:]:
                collision_info = CollisionDetector.check_collision(entity_a, entity_b)

                if collision_info:
                    collider_a = entity_a.get_component(Collider)
                    collider_b = entity_b.get_component(Collider)

                    # Apply physics response if neither is a trigger
                    if not (collider_a.is_trigger or collider_b.is_trigger):
                        self.physics_system.apply_collision_response(
                            entity_a, entity_b, collision_info
                        )
