"""
Comprehensive tests for Collision Detection System

Tests collision detection, spatial partitioning, and callbacks.
"""

import math

import pytest

from neonworks.core.ecs import Transform, World
from neonworks.physics.collision import (
    Collider,
    ColliderType,
    CollisionDetector,
    CollisionInfo,
    CollisionSystem,
    QuadTreeNode,
)


class TestCollider:
    """Test Collider component"""

    def test_collider_creation(self):
        """Test creating colliders"""
        collider = Collider(collider_type=ColliderType.AABB, width=50, height=30)

        assert collider.collider_type == ColliderType.AABB
        assert collider.width == 50
        assert collider.height == 30

    def test_aabb_bounds(self):
        """Test AABB bounds calculation"""
        transform = Transform(x=100, y=200)
        collider = Collider(collider_type=ColliderType.AABB, width=40, height=60)

        min_x, min_y, max_x, max_y = collider.get_bounds(transform)

        assert min_x == 80  # 100 - 20
        assert min_y == 170  # 200 - 30
        assert max_x == 120  # 100 + 20
        assert max_y == 230  # 200 + 30

    def test_aabb_bounds_with_offset(self):
        """Test AABB bounds with offset"""
        transform = Transform(x=100, y=100)
        collider = Collider(
            collider_type=ColliderType.AABB,
            width=20,
            height=20,
            offset_x=10,
            offset_y=5,
        )

        min_x, min_y, max_x, max_y = collider.get_bounds(transform)

        assert min_x == 100  # 100 + 10 - 10
        assert min_y == 95  # 100 + 5 - 10
        assert max_x == 120  # 100 + 10 + 10
        assert max_y == 115  # 100 + 5 + 10

    def test_circle_bounds(self):
        """Test circle bounds calculation"""
        transform = Transform(x=100, y=100)
        collider = Collider(collider_type=ColliderType.CIRCLE, radius=25)

        min_x, min_y, max_x, max_y = collider.get_bounds(transform)

        assert min_x == 75
        assert min_y == 75
        assert max_x == 125
        assert max_y == 125

    def test_point_bounds(self):
        """Test point bounds calculation"""
        transform = Transform(x=50, y=75)
        collider = Collider(collider_type=ColliderType.POINT)

        min_x, min_y, max_x, max_y = collider.get_bounds(transform)

        assert min_x == 50
        assert min_y == 75
        assert max_x == 50
        assert max_y == 75

    def test_get_center(self):
        """Test getting collider center"""
        transform = Transform(x=100, y=200)
        collider = Collider(offset_x=10, offset_y=-5)

        cx, cy = collider.get_center(transform)

        assert cx == 110
        assert cy == 195


class TestAABBCollision:
    """Test AABB collision detection"""

    def test_aabb_collision_overlap(self):
        """Test AABB collision when boxes overlap"""
        world = World()

        entity_a = world.create_entity()
        entity_a.add_component(Transform(x=0, y=0))
        entity_a.add_component(Collider(collider_type=ColliderType.AABB, width=40, height=40))

        entity_b = world.create_entity()
        entity_b.add_component(Transform(x=30, y=0))
        entity_b.add_component(Collider(collider_type=ColliderType.AABB, width=40, height=40))

        collision = CollisionDetector.check_collision(entity_a, entity_b)

        assert collision is not None
        assert collision.entity_a == entity_a
        assert collision.entity_b == entity_b
        assert collision.penetration > 0

    def test_aabb_no_collision(self):
        """Test AABB no collision when boxes don't overlap"""
        world = World()

        entity_a = world.create_entity()
        entity_a.add_component(Transform(x=0, y=0))
        entity_a.add_component(Collider(collider_type=ColliderType.AABB, width=20, height=20))

        entity_b = world.create_entity()
        entity_b.add_component(Transform(x=50, y=50))
        entity_b.add_component(Collider(collider_type=ColliderType.AABB, width=20, height=20))

        collision = CollisionDetector.check_collision(entity_a, entity_b)

        assert collision is None

    def test_aabb_collision_normal_horizontal(self):
        """Test AABB collision normal for horizontal collision"""
        world = World()

        entity_a = world.create_entity()
        entity_a.add_component(Transform(x=0, y=0))
        entity_a.add_component(Collider(collider_type=ColliderType.AABB, width=20, height=40))

        entity_b = world.create_entity()
        entity_b.add_component(Transform(x=15, y=0))
        entity_b.add_component(Collider(collider_type=ColliderType.AABB, width=20, height=40))

        collision = CollisionDetector.check_collision(entity_a, entity_b)

        assert collision is not None
        # Normal should point from A to B (positive x direction)
        assert collision.normal[0] == 1.0
        assert collision.normal[1] == 0.0

    def test_aabb_collision_normal_vertical(self):
        """Test AABB collision normal for vertical collision"""
        world = World()

        entity_a = world.create_entity()
        entity_a.add_component(Transform(x=0, y=0))
        entity_a.add_component(Collider(collider_type=ColliderType.AABB, width=40, height=20))

        entity_b = world.create_entity()
        entity_b.add_component(Transform(x=0, y=15))
        entity_b.add_component(Collider(collider_type=ColliderType.AABB, width=40, height=20))

        collision = CollisionDetector.check_collision(entity_a, entity_b)

        assert collision is not None
        # Normal should point from A to B (positive y direction)
        assert collision.normal[0] == 0.0
        assert collision.normal[1] == 1.0

    def test_aabb_exact_touch(self):
        """Test AABB collision when boxes exactly touch"""
        world = World()

        entity_a = world.create_entity()
        entity_a.add_component(Transform(x=0, y=0))
        entity_a.add_component(Collider(collider_type=ColliderType.AABB, width=20, height=20))

        entity_b = world.create_entity()
        entity_b.add_component(Transform(x=20, y=0))
        entity_b.add_component(Collider(collider_type=ColliderType.AABB, width=20, height=20))

        collision = CollisionDetector.check_collision(entity_a, entity_b)

        # Exact touch should not count as collision
        assert collision is None


class TestCircleCollision:
    """Test circle collision detection"""

    def test_circle_collision_overlap(self):
        """Test circle collision when circles overlap"""
        world = World()

        entity_a = world.create_entity()
        entity_a.add_component(Transform(x=0, y=0))
        entity_a.add_component(Collider(collider_type=ColliderType.CIRCLE, radius=15))

        entity_b = world.create_entity()
        entity_b.add_component(Transform(x=20, y=0))
        entity_b.add_component(Collider(collider_type=ColliderType.CIRCLE, radius=15))

        collision = CollisionDetector.check_collision(entity_a, entity_b)

        assert collision is not None
        assert collision.penetration > 0

    def test_circle_no_collision(self):
        """Test circle no collision when circles don't overlap"""
        world = World()

        entity_a = world.create_entity()
        entity_a.add_component(Transform(x=0, y=0))
        entity_a.add_component(Collider(collider_type=ColliderType.CIRCLE, radius=10))

        entity_b = world.create_entity()
        entity_b.add_component(Transform(x=50, y=0))
        entity_b.add_component(Collider(collider_type=ColliderType.CIRCLE, radius=10))

        collision = CollisionDetector.check_collision(entity_a, entity_b)

        assert collision is None

    def test_circle_collision_normal(self):
        """Test circle collision normal calculation"""
        world = World()

        entity_a = world.create_entity()
        entity_a.add_component(Transform(x=0, y=0))
        entity_a.add_component(Collider(collider_type=ColliderType.CIRCLE, radius=10))

        entity_b = world.create_entity()
        entity_b.add_component(Transform(x=15, y=0))
        entity_b.add_component(Collider(collider_type=ColliderType.CIRCLE, radius=10))

        collision = CollisionDetector.check_collision(entity_a, entity_b)

        assert collision is not None
        # Normal should point from A to B (positive x direction)
        assert abs(collision.normal[0] - 1.0) < 0.001
        assert abs(collision.normal[1]) < 0.001

    def test_circle_exact_touch(self):
        """Test circle collision when circles exactly touch"""
        world = World()

        entity_a = world.create_entity()
        entity_a.add_component(Transform(x=0, y=0))
        entity_a.add_component(Collider(collider_type=ColliderType.CIRCLE, radius=10))

        entity_b = world.create_entity()
        entity_b.add_component(Transform(x=20, y=0))
        entity_b.add_component(Collider(collider_type=ColliderType.CIRCLE, radius=10))

        collision = CollisionDetector.check_collision(entity_a, entity_b)

        # Exact touch should not count as collision
        assert collision is None

    def test_circle_same_position(self):
        """Test circle collision when circles are at same position"""
        world = World()

        entity_a = world.create_entity()
        entity_a.add_component(Transform(x=0, y=0))
        entity_a.add_component(Collider(collider_type=ColliderType.CIRCLE, radius=10))

        entity_b = world.create_entity()
        entity_b.add_component(Transform(x=0, y=0))
        entity_b.add_component(Collider(collider_type=ColliderType.CIRCLE, radius=10))

        collision = CollisionDetector.check_collision(entity_a, entity_b)

        assert collision is not None
        assert collision.penetration == 20  # Full overlap


class TestAABBCircleCollision:
    """Test AABB vs Circle collision detection"""

    def test_aabb_circle_collision(self):
        """Test AABB vs Circle collision"""
        world = World()

        entity_a = world.create_entity()
        entity_a.add_component(Transform(x=0, y=0))
        entity_a.add_component(Collider(collider_type=ColliderType.AABB, width=20, height=20))

        entity_b = world.create_entity()
        entity_b.add_component(Transform(x=15, y=0))
        entity_b.add_component(Collider(collider_type=ColliderType.CIRCLE, radius=10))

        collision = CollisionDetector.check_collision(entity_a, entity_b)

        assert collision is not None

    def test_aabb_circle_no_collision(self):
        """Test AABB vs Circle no collision"""
        world = World()

        entity_a = world.create_entity()
        entity_a.add_component(Transform(x=0, y=0))
        entity_a.add_component(Collider(collider_type=ColliderType.AABB, width=20, height=20))

        entity_b = world.create_entity()
        entity_b.add_component(Transform(x=50, y=50))
        entity_b.add_component(Collider(collider_type=ColliderType.CIRCLE, radius=10))

        collision = CollisionDetector.check_collision(entity_a, entity_b)

        assert collision is None

    def test_circle_aabb_collision_swapped(self):
        """Test Circle vs AABB collision (swapped order)"""
        world = World()

        entity_a = world.create_entity()
        entity_a.add_component(Transform(x=0, y=0))
        entity_a.add_component(Collider(collider_type=ColliderType.CIRCLE, radius=10))

        entity_b = world.create_entity()
        entity_b.add_component(Transform(x=15, y=0))
        entity_b.add_component(Collider(collider_type=ColliderType.AABB, width=20, height=20))

        collision = CollisionDetector.check_collision(entity_a, entity_b)

        assert collision is not None

    def test_circle_inside_aabb(self):
        """Test circle completely inside AABB"""
        world = World()

        entity_a = world.create_entity()
        entity_a.add_component(Transform(x=0, y=0))
        entity_a.add_component(Collider(collider_type=ColliderType.AABB, width=100, height=100))

        entity_b = world.create_entity()
        entity_b.add_component(Transform(x=0, y=0))
        entity_b.add_component(Collider(collider_type=ColliderType.CIRCLE, radius=10))

        collision = CollisionDetector.check_collision(entity_a, entity_b)

        assert collision is not None
        assert collision.penetration > 0


class TestPointCollision:
    """Test point collision detection"""

    def test_point_in_aabb(self):
        """Test point inside AABB"""
        world = World()

        entity_a = world.create_entity()
        entity_a.add_component(Transform(x=50, y=50))
        entity_a.add_component(Collider(collider_type=ColliderType.POINT))

        entity_b = world.create_entity()
        entity_b.add_component(Transform(x=50, y=50))
        entity_b.add_component(Collider(collider_type=ColliderType.AABB, width=40, height=40))

        collision = CollisionDetector.check_collision(entity_a, entity_b)

        assert collision is not None

    def test_point_outside_aabb(self):
        """Test point outside AABB"""
        world = World()

        entity_a = world.create_entity()
        entity_a.add_component(Transform(x=100, y=100))
        entity_a.add_component(Collider(collider_type=ColliderType.POINT))

        entity_b = world.create_entity()
        entity_b.add_component(Transform(x=50, y=50))
        entity_b.add_component(Collider(collider_type=ColliderType.AABB, width=20, height=20))

        collision = CollisionDetector.check_collision(entity_a, entity_b)

        assert collision is None

    def test_point_in_circle(self):
        """Test point inside circle"""
        world = World()

        entity_a = world.create_entity()
        entity_a.add_component(Transform(x=5, y=0))
        entity_a.add_component(Collider(collider_type=ColliderType.POINT))

        entity_b = world.create_entity()
        entity_b.add_component(Transform(x=0, y=0))
        entity_b.add_component(Collider(collider_type=ColliderType.CIRCLE, radius=10))

        collision = CollisionDetector.check_collision(entity_a, entity_b)

        assert collision is not None

    def test_point_outside_circle(self):
        """Test point outside circle"""
        world = World()

        entity_a = world.create_entity()
        entity_a.add_component(Transform(x=20, y=0))
        entity_a.add_component(Collider(collider_type=ColliderType.POINT))

        entity_b = world.create_entity()
        entity_b.add_component(Transform(x=0, y=0))
        entity_b.add_component(Collider(collider_type=ColliderType.CIRCLE, radius=10))

        collision = CollisionDetector.check_collision(entity_a, entity_b)

        assert collision is None


class TestLayerMasking:
    """Test collision layer masking"""

    def test_layer_mask_allows_collision(self):
        """Test collision allowed by layer mask"""
        world = World()

        entity_a = world.create_entity()
        entity_a.add_component(Transform(x=0, y=0))
        entity_a.add_component(
            Collider(
                collider_type=ColliderType.AABB,
                width=20,
                height=20,
                layer=0,
                mask=0b1,  # Can collide with layer 0
            )
        )

        entity_b = world.create_entity()
        entity_b.add_component(Transform(x=0, y=0))
        entity_b.add_component(
            Collider(collider_type=ColliderType.AABB, width=20, height=20, layer=0)
        )

        collision = CollisionDetector.check_collision(entity_a, entity_b)

        assert collision is not None

    def test_layer_mask_blocks_collision(self):
        """Test collision blocked by layer mask"""
        world = World()

        entity_a = world.create_entity()
        entity_a.add_component(Transform(x=0, y=0))
        entity_a.add_component(
            Collider(
                collider_type=ColliderType.AABB,
                width=20,
                height=20,
                layer=0,
                mask=0b10,  # Can only collide with layer 1
            )
        )

        entity_b = world.create_entity()
        entity_b.add_component(Transform(x=0, y=0))
        entity_b.add_component(
            Collider(
                collider_type=ColliderType.AABB,
                width=20,
                height=20,
                layer=0,  # On layer 0
            )
        )

        collision = CollisionDetector.check_collision(entity_a, entity_b)

        assert collision is None


class TestQuadTree:
    """Test QuadTree spatial partitioning"""

    def test_quadtree_creation(self):
        """Test creating QuadTree"""
        quadtree = QuadTreeNode((0, 0, 100, 100))

        assert quadtree.bounds == (0, 0, 100, 100)
        assert len(quadtree.entities) == 0
        assert quadtree.children is None

    def test_quadtree_insert(self):
        """Test inserting entity into QuadTree"""
        world = World()
        quadtree = QuadTreeNode((0, 0, 100, 100))

        entity = world.create_entity()
        entity.add_component(Transform(x=50, y=50))
        entity.add_component(Collider(collider_type=ColliderType.AABB, width=10, height=10))

        transform = entity.get_component(Transform)
        collider = entity.get_component(Collider)

        result = quadtree.insert(entity, transform, collider)

        assert result is True
        assert entity in quadtree.entities

    def test_quadtree_subdivide(self):
        """Test QuadTree subdivision"""
        world = World()
        quadtree = QuadTreeNode((0, 0, 100, 100), max_entities=2)

        # Add entities to trigger subdivision
        for i in range(3):
            entity = world.create_entity()
            entity.add_component(Transform(x=10 + i * 5, y=10 + i * 5))
            entity.add_component(Collider(collider_type=ColliderType.AABB, width=5, height=5))

            transform = entity.get_component(Transform)
            collider = entity.get_component(Collider)
            quadtree.insert(entity, transform, collider)

        # Should have subdivided
        assert quadtree.children is not None
        assert len(quadtree.children) == 4

    def test_quadtree_query(self):
        """Test querying QuadTree"""
        world = World()
        quadtree = QuadTreeNode((0, 0, 100, 100))

        entity1 = world.create_entity()
        entity1.add_component(Transform(x=25, y=25))
        entity1.add_component(Collider(collider_type=ColliderType.AABB, width=10, height=10))

        entity2 = world.create_entity()
        entity2.add_component(Transform(x=75, y=75))
        entity2.add_component(Collider(collider_type=ColliderType.AABB, width=10, height=10))

        quadtree.insert(entity1, entity1.get_component(Transform), entity1.get_component(Collider))
        quadtree.insert(entity2, entity2.get_component(Transform), entity2.get_component(Collider))

        # Query top-left quadrant
        results = quadtree.query((0, 0, 50, 50))

        assert entity1 in results
        assert entity2 not in results

    def test_quadtree_query_all(self):
        """Test querying entire QuadTree"""
        world = World()
        quadtree = QuadTreeNode((0, 0, 100, 100))

        entities = []
        for i in range(5):
            entity = world.create_entity()
            entity.add_component(Transform(x=i * 20, y=i * 20))
            entity.add_component(Collider(collider_type=ColliderType.AABB, width=5, height=5))
            quadtree.insert(entity, entity.get_component(Transform), entity.get_component(Collider))
            entities.append(entity)

        # Query entire bounds
        results = quadtree.query((0, 0, 100, 100))

        assert len(results) == 5
        for entity in entities:
            assert entity in results


class TestCollisionSystem:
    """Test collision system"""

    def test_collision_system_creation(self):
        """Test creating collision system"""
        system = CollisionSystem()

        assert system.world_bounds is not None

    def test_collision_system_update(self):
        """Test updating collision system"""
        world = World()
        system = CollisionSystem()

        entity_a = world.create_entity()
        entity_a.add_component(Transform(x=0, y=0))
        entity_a.add_component(Collider(collider_type=ColliderType.AABB, width=20, height=20))

        entity_b = world.create_entity()
        entity_b.add_component(Transform(x=10, y=0))
        entity_b.add_component(Collider(collider_type=ColliderType.AABB, width=20, height=20))

        # Should not crash
        system.update(world)

    def test_collision_callbacks_enter(self):
        """Test collision enter callback"""
        world = World()
        system = CollisionSystem()

        callback_called = []

        def on_collision(other_entity, collision_info):
            callback_called.append(other_entity)

        entity_a = world.create_entity()
        entity_a.add_component(Transform(x=0, y=0))
        entity_a.add_component(
            Collider(
                collider_type=ColliderType.AABB,
                width=20,
                height=20,
                on_collision_enter=on_collision,
            )
        )

        entity_b = world.create_entity()
        entity_b.add_component(Transform(x=10, y=0))
        entity_b.add_component(Collider(collider_type=ColliderType.AABB, width=20, height=20))

        system.update(world)

        assert len(callback_called) == 1
        assert callback_called[0] == entity_b

    def test_collision_callbacks_stay(self):
        """Test collision stay callback"""
        world = World()
        system = CollisionSystem()

        stay_count = []

        def on_collision_stay(other_entity, collision_info):
            stay_count.append(1)

        entity_a = world.create_entity()
        entity_a.add_component(Transform(x=0, y=0))
        entity_a.add_component(
            Collider(
                collider_type=ColliderType.AABB,
                width=20,
                height=20,
                on_collision_stay=on_collision_stay,
            )
        )

        entity_b = world.create_entity()
        entity_b.add_component(Transform(x=10, y=0))
        entity_b.add_component(Collider(collider_type=ColliderType.AABB, width=20, height=20))

        # First update - enter
        system.update(world)
        assert len(stay_count) == 0

        # Second update - stay
        system.update(world)
        assert len(stay_count) == 1

    def test_collision_callbacks_exit(self):
        """Test collision exit callback"""
        world = World()
        system = CollisionSystem()

        exit_called = []

        def on_collision_exit(other_entity):
            exit_called.append(other_entity)

        entity_a = world.create_entity()
        transform_a = Transform(x=0, y=0)
        entity_a.add_component(transform_a)
        entity_a.add_component(
            Collider(
                collider_type=ColliderType.AABB,
                width=20,
                height=20,
                on_collision_exit=on_collision_exit,
            )
        )

        entity_b = world.create_entity()
        entity_b.add_component(Transform(x=10, y=0))
        entity_b.add_component(Collider(collider_type=ColliderType.AABB, width=20, height=20))

        # First update - enter collision
        system.update(world)
        assert len(exit_called) == 0

        # Move entity_a away
        transform_a.x = 100

        # Second update - exit collision
        system.update(world)
        assert len(exit_called) == 1
        assert exit_called[0] == entity_b

    def test_collision_system_with_spatial_partitioning(self):
        """Test collision system with spatial partitioning enabled"""
        world = World()
        system = CollisionSystem(world_bounds=(0, 0, 1000, 1000))
        system.use_spatial_partitioning = True

        # Add many entities to trigger spatial partitioning
        for i in range(15):
            entity = world.create_entity()
            entity.add_component(Transform(x=i * 50, y=i * 50))
            entity.add_component(Collider(collider_type=ColliderType.AABB, width=20, height=20))

        # Should not crash
        system.update(world)

    def test_collision_system_without_spatial_partitioning(self):
        """Test collision system without spatial partitioning"""
        world = World()
        system = CollisionSystem()
        system.use_spatial_partitioning = False

        entity_a = world.create_entity()
        entity_a.add_component(Transform(x=0, y=0))
        entity_a.add_component(Collider(collider_type=ColliderType.AABB, width=20, height=20))

        entity_b = world.create_entity()
        entity_b.add_component(Transform(x=10, y=0))
        entity_b.add_component(Collider(collider_type=ColliderType.AABB, width=20, height=20))

        # Should not crash
        system.update(world)


# Run tests with: pytest engine/tests/test_collision.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
