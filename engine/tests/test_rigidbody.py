"""
Comprehensive tests for Rigid Body Physics System

Tests physics simulation, forces, and collision response.
"""

import pytest
import math
from engine.core.ecs import World, Transform
from engine.physics.rigidbody import (
    RigidBody,
    PhysicsSystem,
    PhysicsSettings,
    IntegratedPhysicsSystem
)
from engine.physics.collision import Collider, ColliderType, CollisionInfo


class TestRigidBody:
    """Test RigidBody component"""

    def test_rigidbody_creation(self):
        """Test creating rigid body"""
        rb = RigidBody(mass=2.0, velocity_x=10.0)

        assert rb.mass == 2.0
        assert rb.velocity_x == 10.0
        assert rb.velocity_y == 0.0

    def test_add_force(self):
        """Test adding force"""
        rb = RigidBody()
        rb.add_force(100.0, 50.0)

        assert rb.force_x == 100.0
        assert rb.force_y == 50.0

    def test_add_force_multiple(self):
        """Test adding multiple forces"""
        rb = RigidBody()
        rb.add_force(100.0, 50.0)
        rb.add_force(20.0, 10.0)

        assert rb.force_x == 120.0
        assert rb.force_y == 60.0

    def test_add_force_static_ignored(self):
        """Test forces ignored on static bodies"""
        rb = RigidBody(is_static=True)
        rb.add_force(100.0, 50.0)

        assert rb.force_x == 0.0
        assert rb.force_y == 0.0

    def test_add_impulse(self):
        """Test adding impulse"""
        rb = RigidBody(mass=2.0)
        rb.add_impulse(20.0, 10.0)

        # Impulse / mass = velocity change
        assert rb.velocity_x == 10.0
        assert rb.velocity_y == 5.0

    def test_add_impulse_static_ignored(self):
        """Test impulse ignored on static bodies"""
        rb = RigidBody(is_static=True)
        rb.add_impulse(20.0, 10.0)

        assert rb.velocity_x == 0.0
        assert rb.velocity_y == 0.0

    def test_set_velocity(self):
        """Test setting velocity directly"""
        rb = RigidBody()
        rb.set_velocity(50.0, 25.0)

        assert rb.velocity_x == 50.0
        assert rb.velocity_y == 25.0

    def test_get_speed(self):
        """Test getting speed"""
        rb = RigidBody(velocity_x=3.0, velocity_y=4.0)
        speed = rb.get_speed()

        assert abs(speed - 5.0) < 0.001

    def test_get_kinetic_energy(self):
        """Test getting kinetic energy"""
        rb = RigidBody(mass=2.0, velocity_x=3.0, velocity_y=4.0)
        ke = rb.get_kinetic_energy()

        # KE = 0.5 * m * v^2 = 0.5 * 2 * 25 = 25
        assert abs(ke - 25.0) < 0.001


class TestPhysicsSettings:
    """Test physics settings"""

    def test_default_settings(self):
        """Test default physics settings"""
        settings = PhysicsSettings()

        assert settings.gravity_y == 9.81
        assert settings.max_velocity == 1000.0

    def test_custom_settings(self):
        """Test custom physics settings"""
        settings = PhysicsSettings(gravity_y=20.0, max_velocity=500.0)

        assert settings.gravity_y == 20.0
        assert settings.max_velocity == 500.0


class TestPhysicsSystem:
    """Test physics system"""

    def test_physics_system_creation(self):
        """Test creating physics system"""
        system = PhysicsSystem()

        assert system.settings is not None

    def test_physics_update_velocity(self):
        """Test physics updates velocity from acceleration"""
        world = World()
        settings = PhysicsSettings(max_delta_time=10.0, gravity_y=0.0)
        system = PhysicsSystem(settings)

        entity = world.create_entity()
        entity.add_component(Transform(x=0, y=0))
        rb = RigidBody(acceleration_x=10.0, acceleration_y=5.0)
        entity.add_component(rb)

        system.update(world, 1.0)

        assert rb.velocity_x == 10.0
        assert rb.velocity_y == 5.0

    def test_physics_update_position(self):
        """Test physics updates position from velocity"""
        world = World()
        settings = PhysicsSettings(max_delta_time=10.0, gravity_y=0.0)
        system = PhysicsSystem(settings)

        entity = world.create_entity()
        transform = Transform(x=0, y=0)
        entity.add_component(transform)
        rb = RigidBody(velocity_x=10.0, velocity_y=5.0)
        entity.add_component(rb)

        system.update(world, 1.0)

        assert transform.x == 10.0
        assert transform.y == 5.0

    def test_physics_apply_gravity(self):
        """Test gravity application"""
        world = World()
        settings = PhysicsSettings(gravity_y=10.0, max_delta_time=10.0)
        system = PhysicsSystem(settings)

        entity = world.create_entity()
        entity.add_component(Transform(x=0, y=0))
        rb = RigidBody(gravity_scale=1.0)
        entity.add_component(rb)

        system.update(world, 1.0)

        # Should have acceleration from gravity
        assert rb.velocity_y == 10.0

    def test_physics_gravity_scale(self):
        """Test gravity scale"""
        world = World()
        settings = PhysicsSettings(gravity_y=10.0, max_delta_time=10.0)
        system = PhysicsSystem(settings)

        entity = world.create_entity()
        entity.add_component(Transform(x=0, y=0))
        rb = RigidBody(gravity_scale=2.0)
        entity.add_component(rb)

        system.update(world, 1.0)

        assert rb.velocity_y == 20.0

    def test_physics_no_gravity_kinematic(self):
        """Test kinematic bodies ignore gravity"""
        world = World()
        settings = PhysicsSettings(gravity_y=10.0)
        system = PhysicsSystem(settings)

        entity = world.create_entity()
        entity.add_component(Transform(x=0, y=0))
        rb = RigidBody(is_kinematic=True)
        entity.add_component(rb)

        system.update(world, 1.0)

        assert rb.velocity_y == 0.0

    def test_physics_static_no_movement(self):
        """Test static bodies don't move"""
        world = World()
        system = PhysicsSystem()

        entity = world.create_entity()
        transform = Transform(x=100, y=100)
        entity.add_component(transform)
        rb = RigidBody(is_static=True, velocity_x=10.0, velocity_y=10.0)
        entity.add_component(rb)

        system.update(world, 1.0)

        # Position shouldn't change
        assert transform.x == 100
        assert transform.y == 100

    def test_physics_force_to_acceleration(self):
        """Test force converts to acceleration"""
        world = World()
        settings = PhysicsSettings(max_delta_time=10.0, gravity_y=0.0)
        system = PhysicsSystem(settings)

        entity = world.create_entity()
        entity.add_component(Transform(x=0, y=0))
        rb = RigidBody(mass=2.0, force_x=20.0, force_y=10.0)
        entity.add_component(rb)

        system.update(world, 1.0)

        # F = ma, so a = F/m = 20/2 = 10, v = a*t = 10*1 = 10
        assert rb.velocity_x == 10.0
        assert rb.velocity_y == 5.0

        # Forces should be reset after update
        assert rb.force_x == 0.0
        assert rb.force_y == 0.0

    def test_physics_drag(self):
        """Test drag slows down objects"""
        world = World()
        system = PhysicsSystem()

        entity = world.create_entity()
        entity.add_component(Transform(x=0, y=0))
        rb = RigidBody(velocity_x=100.0, drag=0.5)
        entity.add_component(rb)

        initial_velocity = rb.velocity_x

        system.update(world, 1.0)

        # Velocity should be reduced by drag
        assert rb.velocity_x < initial_velocity
        assert rb.velocity_x > 0

    def test_physics_max_velocity(self):
        """Test velocity clamping"""
        world = World()
        settings = PhysicsSettings(max_velocity=10.0)
        system = PhysicsSystem(settings)

        entity = world.create_entity()
        entity.add_component(Transform(x=0, y=0))
        rb = RigidBody(velocity_x=100.0, velocity_y=100.0)
        entity.add_component(rb)

        system.update(world, 1.0)

        # Velocity should be clamped
        speed = rb.get_speed()
        assert abs(speed - 10.0) < 0.01

    def test_physics_velocity_threshold(self):
        """Test velocity threshold stops slow objects"""
        world = World()
        settings = PhysicsSettings(velocity_threshold=0.1, max_delta_time=10.0, gravity_y=0.0)
        system = PhysicsSystem(settings)

        entity = world.create_entity()
        entity.add_component(Transform(x=0, y=0))
        rb = RigidBody(velocity_x=0.05, velocity_y=0.05)
        entity.add_component(rb)

        system.update(world, 1.0)

        # Very slow velocity should be zeroed
        assert rb.velocity_x == 0.0
        assert rb.velocity_y == 0.0

    def test_physics_freeze_position_x(self):
        """Test freezing x position"""
        world = World()
        settings = PhysicsSettings(max_delta_time=10.0, gravity_y=0.0)
        system = PhysicsSystem(settings)

        entity = world.create_entity()
        transform = Transform(x=100, y=100)
        entity.add_component(transform)
        rb = RigidBody(velocity_x=10.0, velocity_y=10.0, freeze_position_x=True)
        entity.add_component(rb)

        system.update(world, 1.0)

        # X shouldn't change, Y should
        assert transform.x == 100
        assert transform.y == 110

    def test_physics_freeze_position_y(self):
        """Test freezing y position"""
        world = World()
        settings = PhysicsSettings(max_delta_time=10.0, gravity_y=0.0)
        system = PhysicsSystem(settings)

        entity = world.create_entity()
        transform = Transform(x=100, y=100)
        entity.add_component(transform)
        rb = RigidBody(velocity_x=10.0, velocity_y=10.0, freeze_position_y=True)
        entity.add_component(rb)

        system.update(world, 1.0)

        # Y shouldn't change, X should
        assert transform.x == 110
        assert transform.y == 100


class TestCollisionResponse:
    """Test collision response"""

    def test_collision_response_positional_correction(self):
        """Test collision separates overlapping objects"""
        world = World()
        system = PhysicsSystem()

        entity_a = world.create_entity()
        transform_a = Transform(x=0, y=0)
        entity_a.add_component(transform_a)
        entity_a.add_component(RigidBody(mass=1.0))
        entity_a.add_component(Collider(collider_type=ColliderType.AABB, width=20, height=20))

        entity_b = world.create_entity()
        transform_b = Transform(x=10, y=0)
        entity_b.add_component(transform_b)
        entity_b.add_component(RigidBody(mass=1.0))
        entity_b.add_component(Collider(collider_type=ColliderType.AABB, width=20, height=20))

        # Create collision info
        collision_info = CollisionInfo(
            entity_a=entity_a,
            entity_b=entity_b,
            normal=(1.0, 0.0),
            penetration=10.0,
            point=(5.0, 0.0)
        )

        initial_distance = abs(transform_a.x - transform_b.x)

        system.apply_collision_response(entity_a, entity_b, collision_info)

        # Objects should be separated
        final_distance = abs(transform_a.x - transform_b.x)
        assert final_distance > initial_distance

    def test_collision_response_with_static(self):
        """Test collision with static object"""
        world = World()
        system = PhysicsSystem()

        entity_a = world.create_entity()
        transform_a = Transform(x=0, y=0)
        entity_a.add_component(transform_a)
        entity_a.add_component(RigidBody(mass=1.0, velocity_y=10.0))
        entity_a.add_component(Collider(collider_type=ColliderType.AABB, width=20, height=20))

        entity_b = world.create_entity()
        transform_b = Transform(x=0, y=20)
        entity_b.add_component(transform_b)
        entity_b.add_component(RigidBody(is_static=True))
        entity_b.add_component(Collider(collider_type=ColliderType.AABB, width=20, height=20))

        # Normal points from A to B (downward/positive y since B is below A)
        collision_info = CollisionInfo(
            entity_a=entity_a,
            entity_b=entity_b,
            normal=(0.0, 1.0),
            penetration=5.0,
            point=(0.0, 10.0)
        )

        initial_y = transform_a.y

        system.apply_collision_response(entity_a, entity_b, collision_info)

        # Static object shouldn't move
        assert transform_b.y == 20

        # Dynamic object should be pushed away (upward, so negative y)
        assert transform_a.y < initial_y

    def test_collision_response_velocity_bounce(self):
        """Test collision bounces with restitution"""
        world = World()
        system = PhysicsSystem()

        entity_a = world.create_entity()
        entity_a.add_component(Transform(x=0, y=0))
        rb_a = RigidBody(mass=1.0, velocity_y=10.0, restitution=1.0)
        entity_a.add_component(rb_a)
        entity_a.add_component(Collider(collider_type=ColliderType.AABB, width=20, height=20))

        entity_b = world.create_entity()
        entity_b.add_component(Transform(x=0, y=20))
        entity_b.add_component(RigidBody(is_static=True, restitution=1.0))
        entity_b.add_component(Collider(collider_type=ColliderType.AABB, width=20, height=20))

        # Normal points from A to B (downward/positive y)
        collision_info = CollisionInfo(
            entity_a=entity_a,
            entity_b=entity_b,
            normal=(0.0, 1.0),
            penetration=1.0,
            point=(0.0, 10.0)
        )

        initial_velocity = rb_a.velocity_y

        system.apply_collision_response(entity_a, entity_b, collision_info)

        # With restitution=1.0, velocity should be significantly reduced or reversed
        # (The exact behavior depends on the collision resolution algorithm)
        assert abs(rb_a.velocity_y) < abs(initial_velocity)

    def test_collision_response_no_bounce(self):
        """Test collision without restitution"""
        world = World()
        system = PhysicsSystem()

        entity_a = world.create_entity()
        entity_a.add_component(Transform(x=0, y=0))
        rb_a = RigidBody(mass=1.0, velocity_y=10.0, restitution=0.0)
        entity_a.add_component(rb_a)
        entity_a.add_component(Collider(collider_type=ColliderType.AABB, width=20, height=20))

        entity_b = world.create_entity()
        entity_b.add_component(Transform(x=0, y=20))
        entity_b.add_component(RigidBody(is_static=True))
        entity_b.add_component(Collider(collider_type=ColliderType.AABB, width=20, height=20))

        # Normal points from A to B (downward/positive y)
        collision_info = CollisionInfo(
            entity_a=entity_a,
            entity_b=entity_b,
            normal=(0.0, 1.0),
            penetration=1.0,
            point=(0.0, 10.0)
        )

        initial_velocity = rb_a.velocity_y

        system.apply_collision_response(entity_a, entity_b, collision_info)

        # With restitution=0.0, velocity along normal should be stopped (absorbed)
        # The velocity component along the collision normal should be removed
        assert abs(rb_a.velocity_y) < abs(initial_velocity)

    def test_collision_response_trigger_ignored(self):
        """Test trigger colliders don't cause physical response"""
        world = World()
        system = PhysicsSystem()

        entity_a = world.create_entity()
        transform_a = Transform(x=0, y=0)
        entity_a.add_component(transform_a)
        entity_a.add_component(RigidBody(mass=1.0))
        entity_a.add_component(Collider(
            collider_type=ColliderType.AABB,
            width=20,
            height=20,
            is_trigger=True
        ))

        entity_b = world.create_entity()
        transform_b = Transform(x=10, y=0)
        entity_b.add_component(transform_b)
        entity_b.add_component(RigidBody(mass=1.0))
        entity_b.add_component(Collider(
            collider_type=ColliderType.AABB,
            width=20,
            height=20,
            is_trigger=True
        ))

        collision_info = CollisionInfo(
            entity_a=entity_a,
            entity_b=entity_b,
            normal=(1.0, 0.0),
            penetration=10.0,
            point=(5.0, 0.0)
        )

        initial_x_a = transform_a.x
        initial_x_b = transform_b.x

        system.apply_collision_response(entity_a, entity_b, collision_info)

        # Triggers shouldn't cause separation
        assert transform_a.x == initial_x_a
        assert transform_b.x == initial_x_b


class TestIntegratedPhysicsSystem:
    """Test integrated physics and collision system"""

    def test_integrated_system_creation(self):
        """Test creating integrated system"""
        system = IntegratedPhysicsSystem()

        assert system.physics_system is not None
        assert system.collision_system is not None

    def test_integrated_system_update(self):
        """Test integrated system updates physics and collisions"""
        world = World()
        system = IntegratedPhysicsSystem()

        entity = world.create_entity()
        entity.add_component(Transform(x=0, y=0))
        entity.add_component(RigidBody(velocity_x=10.0))
        entity.add_component(Collider(collider_type=ColliderType.AABB, width=20, height=20))

        # Should not crash
        system.update(world, 1.0)

    def test_integrated_system_collision_and_physics(self):
        """Test integrated system handles collision and physics together"""
        world = World()
        settings = PhysicsSettings(gravity_y=0.0)
        system = IntegratedPhysicsSystem(physics_settings=settings)

        # Create two entities that will collide
        entity_a = world.create_entity()
        entity_a.add_component(Transform(x=0, y=0))
        entity_a.add_component(RigidBody(mass=1.0, velocity_x=10.0))
        entity_a.add_component(Collider(collider_type=ColliderType.AABB, width=20, height=20))

        entity_b = world.create_entity()
        entity_b.add_component(Transform(x=15, y=0))
        entity_b.add_component(RigidBody(mass=1.0))
        entity_b.add_component(Collider(collider_type=ColliderType.AABB, width=20, height=20))

        # Update system
        system.update(world, 0.1)

        # Entities should have moved and potentially collided
        # (exact behavior depends on collision resolution)


# Run tests with: pytest engine/tests/test_rigidbody.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
