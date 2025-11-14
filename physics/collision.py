"""
Collision Detection System

Comprehensive collision detection with spatial partitioning.
Optimized with NumPy for improved performance.
"""

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, List, Optional, Set, Tuple

import numpy as np

from neonworks.core.ecs import Component, Entity, Transform, World


class ColliderType(Enum):
    """Types of colliders"""

    AABB = "aabb"  # Axis-Aligned Bounding Box
    CIRCLE = "circle"
    POINT = "point"


@dataclass
class CollisionInfo:
    """Information about a collision"""

    entity_a: Entity
    entity_b: Entity
    normal: Tuple[float, float] = (0.0, 0.0)  # Collision normal
    penetration: float = 0.0  # Penetration depth
    point: Tuple[float, float] = (0.0, 0.0)  # Contact point


@dataclass
class Collider(Component):
    """Base collider component"""

    collider_type: ColliderType = ColliderType.AABB

    # AABB properties
    width: float = 0.0
    height: float = 0.0

    # Circle properties
    radius: float = 0.0

    # Offset from entity position
    offset_x: float = 0.0
    offset_y: float = 0.0

    # Collision layers and mask
    layer: int = 0  # Which layer this collider is on
    mask: int = 0xFFFFFFFF  # Which layers this collider can collide with

    # Trigger vs solid
    is_trigger: bool = False  # Triggers don't cause physical response

    # Callbacks
    on_collision_enter: Optional[Callable[[Entity, CollisionInfo], None]] = None
    on_collision_stay: Optional[Callable[[Entity, CollisionInfo], None]] = None
    on_collision_exit: Optional[Callable[[Entity], None]] = None

    def get_bounds(self, transform: Transform) -> Tuple[float, float, float, float]:
        """
        Get collider bounds (min_x, min_y, max_x, max_y).

        Args:
            transform: Entity transform

        Returns:
            Tuple of (min_x, min_y, max_x, max_y)
        """
        x = transform.x + self.offset_x
        y = transform.y + self.offset_y

        if self.collider_type == ColliderType.AABB:
            half_w = self.width / 2
            half_h = self.height / 2
            return (x - half_w, y - half_h, x + half_w, y + half_h)
        elif self.collider_type == ColliderType.CIRCLE:
            return (x - self.radius, y - self.radius, x + self.radius, y + self.radius)
        else:  # POINT
            return (x, y, x, y)

    def get_center(self, transform: Transform) -> Tuple[float, float]:
        """Get collider center position"""
        return (transform.x + self.offset_x, transform.y + self.offset_y)


class CollisionDetector:
    """Collision detection algorithms"""

    @staticmethod
    def check_collision(entity_a: Entity, entity_b: Entity) -> Optional[CollisionInfo]:
        """
        Check collision between two entities.

        Args:
            entity_a: First entity
            entity_b: Second entity

        Returns:
            CollisionInfo if collision detected, None otherwise
        """
        collider_a = entity_a.get_component(Collider)
        collider_b = entity_b.get_component(Collider)
        transform_a = entity_a.get_component(Transform)
        transform_b = entity_b.get_component(Transform)

        if not all([collider_a, collider_b, transform_a, transform_b]):
            return None

        # Check layer mask
        if not (collider_a.mask & (1 << collider_b.layer)):
            return None

        # Dispatch to appropriate collision check
        if (
            collider_a.collider_type == ColliderType.AABB
            and collider_b.collider_type == ColliderType.AABB
        ):
            return CollisionDetector._check_aabb_aabb(
                entity_a, entity_b, collider_a, collider_b, transform_a, transform_b
            )
        elif (
            collider_a.collider_type == ColliderType.CIRCLE
            and collider_b.collider_type == ColliderType.CIRCLE
        ):
            return CollisionDetector._check_circle_circle(
                entity_a, entity_b, collider_a, collider_b, transform_a, transform_b
            )
        elif (
            collider_a.collider_type == ColliderType.AABB
            and collider_b.collider_type == ColliderType.CIRCLE
        ) or (
            collider_a.collider_type == ColliderType.CIRCLE
            and collider_b.collider_type == ColliderType.AABB
        ):
            return CollisionDetector._check_aabb_circle(
                entity_a, entity_b, collider_a, collider_b, transform_a, transform_b
            )
        elif (
            collider_a.collider_type == ColliderType.POINT
            or collider_b.collider_type == ColliderType.POINT
        ):
            return CollisionDetector._check_point_collision(
                entity_a, entity_b, collider_a, collider_b, transform_a, transform_b
            )

        return None

    @staticmethod
    def _check_aabb_aabb(
        entity_a: Entity,
        entity_b: Entity,
        collider_a: Collider,
        collider_b: Collider,
        transform_a: Transform,
        transform_b: Transform,
    ) -> Optional[CollisionInfo]:
        """AABB vs AABB collision detection"""
        min_ax, min_ay, max_ax, max_ay = collider_a.get_bounds(transform_a)
        min_bx, min_by, max_bx, max_by = collider_b.get_bounds(transform_b)

        # Check overlap
        if max_ax < min_bx or min_ax > max_bx or max_ay < min_by or min_ay > max_by:
            return None

        # Calculate penetration
        overlap_x = min(max_ax, max_bx) - max(min_ax, min_bx)
        overlap_y = min(max_ay, max_by) - max(min_ay, min_by)

        # Find minimum penetration axis
        if overlap_x < overlap_y:
            normal_x = 1.0 if transform_a.x < transform_b.x else -1.0
            normal_y = 0.0
            penetration = overlap_x
        else:
            normal_x = 0.0
            normal_y = 1.0 if transform_a.y < transform_b.y else -1.0
            penetration = overlap_y

        # No collision if penetration is zero or negative (exact touch)
        if penetration <= 0:
            return None

        # Contact point (center of overlap)
        contact_x = (max(min_ax, min_bx) + min(max_ax, max_bx)) / 2
        contact_y = (max(min_ay, min_by) + min(max_ay, max_by)) / 2

        return CollisionInfo(
            entity_a=entity_a,
            entity_b=entity_b,
            normal=(normal_x, normal_y),
            penetration=penetration,
            point=(contact_x, contact_y),
        )

    @staticmethod
    def _check_circle_circle(
        entity_a: Entity,
        entity_b: Entity,
        collider_a: Collider,
        collider_b: Collider,
        transform_a: Transform,
        transform_b: Transform,
    ) -> Optional[CollisionInfo]:
        """Circle vs Circle collision detection - optimized with NumPy"""
        center_ax, center_ay = collider_a.get_center(transform_a)
        center_bx, center_by = collider_b.get_center(transform_b)

        # Distance between centers (using NumPy for faster calculation)
        dx = center_bx - center_ax
        dy = center_by - center_ay
        distance = float(np.sqrt(dx * dx + dy * dy))

        # Check overlap
        combined_radius = collider_a.radius + collider_b.radius
        if distance >= combined_radius:
            return None

        # Avoid division by zero
        if distance == 0:
            # Circles are at same position - full overlap
            normal_x = 1.0
            normal_y = 0.0
            penetration = combined_radius
        else:
            # Normal from A to B
            normal_x = dx / distance
            normal_y = dy / distance

            # Penetration depth
            penetration = combined_radius - distance

        # Contact point
        contact_x = center_ax + normal_x * collider_a.radius
        contact_y = center_ay + normal_y * collider_a.radius

        return CollisionInfo(
            entity_a=entity_a,
            entity_b=entity_b,
            normal=(normal_x, normal_y),
            penetration=penetration,
            point=(contact_x, contact_y),
        )

    @staticmethod
    def _check_aabb_circle(
        entity_a: Entity,
        entity_b: Entity,
        collider_a: Collider,
        collider_b: Collider,
        transform_a: Transform,
        transform_b: Transform,
    ) -> Optional[CollisionInfo]:
        """AABB vs Circle collision detection"""
        # Ensure A is AABB and B is Circle
        if collider_a.collider_type == ColliderType.CIRCLE:
            entity_a, entity_b = entity_b, entity_a
            collider_a, collider_b = collider_b, collider_a
            transform_a, transform_b = transform_b, transform_a

        min_ax, min_ay, max_ax, max_ay = collider_a.get_bounds(transform_a)
        center_bx, center_by = collider_b.get_center(transform_b)

        # Find closest point on AABB to circle center
        closest_x = max(min_ax, min(center_bx, max_ax))
        closest_y = max(min_ay, min(center_by, max_ay))

        # Distance from circle center to closest point (using NumPy)
        dx = center_bx - closest_x
        dy = center_by - closest_y
        distance = float(np.sqrt(dx * dx + dy * dy))

        # Check collision
        if distance >= collider_b.radius:
            return None

        # Calculate normal and penetration
        if distance == 0:
            # Circle center is inside AABB
            # Use distance to edges to determine normal
            dist_left = center_bx - min_ax
            dist_right = max_ax - center_bx
            dist_top = center_by - min_ay
            dist_bottom = max_ay - center_by

            min_dist = min(dist_left, dist_right, dist_top, dist_bottom)

            if min_dist == dist_left:
                normal_x, normal_y = -1.0, 0.0
            elif min_dist == dist_right:
                normal_x, normal_y = 1.0, 0.0
            elif min_dist == dist_top:
                normal_x, normal_y = 0.0, -1.0
            else:
                normal_x, normal_y = 0.0, 1.0

            penetration = collider_b.radius + min_dist
        else:
            normal_x = dx / distance
            normal_y = dy / distance
            penetration = collider_b.radius - distance

        return CollisionInfo(
            entity_a=entity_a,
            entity_b=entity_b,
            normal=(normal_x, normal_y),
            penetration=penetration,
            point=(closest_x, closest_y),
        )

    @staticmethod
    def _check_point_collision(
        entity_a: Entity,
        entity_b: Entity,
        collider_a: Collider,
        collider_b: Collider,
        transform_a: Transform,
        transform_b: Transform,
    ) -> Optional[CollisionInfo]:
        """Point collision detection"""
        # Ensure A is the point
        if collider_b.collider_type == ColliderType.POINT:
            entity_a, entity_b = entity_b, entity_a
            collider_a, collider_b = collider_b, collider_a
            transform_a, transform_b = transform_b, transform_a

        point_x, point_y = collider_a.get_center(transform_a)

        if collider_b.collider_type == ColliderType.AABB:
            min_bx, min_by, max_bx, max_by = collider_b.get_bounds(transform_b)
            if min_bx <= point_x <= max_bx and min_by <= point_y <= max_by:
                return CollisionInfo(
                    entity_a=entity_a,
                    entity_b=entity_b,
                    normal=(0.0, -1.0),  # Default normal
                    penetration=0.0,
                    point=(point_x, point_y),
                )
        elif collider_b.collider_type == ColliderType.CIRCLE:
            center_bx, center_by = collider_b.get_center(transform_b)
            dx = point_x - center_bx
            dy = point_y - center_by
            distance = float(np.sqrt(dx * dx + dy * dy))

            if distance <= collider_b.radius:
                if distance == 0:
                    normal = (0.0, -1.0)
                else:
                    normal = (dx / distance, dy / distance)

                return CollisionInfo(
                    entity_a=entity_a,
                    entity_b=entity_b,
                    normal=normal,
                    penetration=0.0,
                    point=(point_x, point_y),
                )

        return None


@dataclass
class QuadTreeNode:
    """Node in a QuadTree for spatial partitioning"""

    bounds: Tuple[float, float, float, float]  # (min_x, min_y, max_x, max_y)
    entities: List[Entity] = field(default_factory=list)
    children: Optional[List["QuadTreeNode"]] = None
    max_entities: int = 4
    max_depth: int = 5
    depth: int = 0

    def insert(self, entity: Entity, transform: Transform, collider: Collider) -> bool:
        """Insert entity into QuadTree"""
        # Check if entity bounds intersect this node
        entity_bounds = collider.get_bounds(transform)
        if not self._intersects(entity_bounds):
            return False

        # If we have children, try to insert into them
        if self.children:
            for child in self.children:
                child.insert(entity, transform, collider)
            return True

        # Add to this node
        self.entities.append(entity)

        # Subdivide if necessary
        if len(self.entities) > self.max_entities and self.depth < self.max_depth:
            self._subdivide()

        return True

    def _subdivide(self):
        """Split this node into 4 children"""
        min_x, min_y, max_x, max_y = self.bounds
        mid_x = (min_x + max_x) / 2
        mid_y = (min_y + max_y) / 2

        self.children = [
            QuadTreeNode(
                (min_x, min_y, mid_x, mid_y),
                max_depth=self.max_depth,
                depth=self.depth + 1,
            ),  # Top-left
            QuadTreeNode(
                (mid_x, min_y, max_x, mid_y),
                max_depth=self.max_depth,
                depth=self.depth + 1,
            ),  # Top-right
            QuadTreeNode(
                (min_x, mid_y, mid_x, max_y),
                max_depth=self.max_depth,
                depth=self.depth + 1,
            ),  # Bottom-left
            QuadTreeNode(
                (mid_x, mid_y, max_x, max_y),
                max_depth=self.max_depth,
                depth=self.depth + 1,
            ),  # Bottom-right
        ]

        # Move entities to children
        for entity in self.entities:
            transform = entity.get_component(Transform)
            collider = entity.get_component(Collider)
            if transform and collider:
                for child in self.children:
                    child.insert(entity, transform, collider)

        self.entities = []

    def query(self, bounds: Tuple[float, float, float, float]) -> Set[Entity]:
        """Query entities within bounds"""
        result = set()

        if not self._intersects(bounds):
            return result

        # Add entities from this node that actually intersect query bounds
        for entity in self.entities:
            transform = entity.get_component(Transform)
            collider = entity.get_component(Collider)
            if transform and collider:
                entity_bounds = collider.get_bounds(transform)
                # Check if entity bounds intersect query bounds
                min_x, min_y, max_x, max_y = entity_bounds
                query_min_x, query_min_y, query_max_x, query_max_y = bounds
                if not (
                    max_x < query_min_x
                    or min_x > query_max_x
                    or max_y < query_min_y
                    or min_y > query_max_y
                ):
                    result.add(entity)

        # Query children
        if self.children:
            for child in self.children:
                result.update(child.query(bounds))

        return result

    def _intersects(self, bounds: Tuple[float, float, float, float]) -> bool:
        """Check if bounds intersect this node"""
        min_x, min_y, max_x, max_y = self.bounds
        other_min_x, other_min_y, other_max_x, other_max_y = bounds

        return not (
            max_x < other_min_x or min_x > other_max_x or max_y < other_min_y or min_y > other_max_y
        )


class CollisionSystem:
    """System for detecting and responding to collisions"""

    def __init__(self, world_bounds: Optional[Tuple[float, float, float, float]] = None):
        """
        Initialize collision system.

        Args:
            world_bounds: Bounds for spatial partitioning (min_x, min_y, max_x, max_y)
        """
        self.world_bounds = world_bounds or (0, 0, 1000, 1000)
        self.use_spatial_partitioning = True

        # Track collisions from previous frame
        self._previous_collisions: Set[Tuple[int, int]] = set()

    def update(self, world: World):
        """
        Update collision detection for all entities.

        Args:
            world: Game world
        """
        # Get all entities with colliders
        entities_with_colliders = []
        for entity in world._entities.values():
            if entity.get_component(Collider) and entity.get_component(Transform):
                entities_with_colliders.append(entity)

        # Build spatial partitioning structure if enabled
        if self.use_spatial_partitioning and len(entities_with_colliders) > 10:
            quadtree = QuadTreeNode(self.world_bounds)
            for entity in entities_with_colliders:
                transform = entity.get_component(Transform)
                collider = entity.get_component(Collider)
                quadtree.insert(entity, transform, collider)
        else:
            quadtree = None

        # Track current frame collisions
        current_collisions: Set[Tuple[int, int]] = set()

        # Check collisions
        for i, entity_a in enumerate(entities_with_colliders):
            collider_a = entity_a.get_component(Collider)
            transform_a = entity_a.get_component(Transform)

            # Get potential collision candidates
            if quadtree:
                bounds = collider_a.get_bounds(transform_a)
                candidates = quadtree.query(bounds)
            else:
                candidates = entities_with_colliders[i + 1 :]

            for entity_b in candidates:
                # Skip self-collision
                if entity_a.id == entity_b.id:
                    continue

                # When using spatial partitioning, avoid duplicate checks
                if quadtree and entity_a.id > entity_b.id:
                    continue

                # Check collision
                collision_info = CollisionDetector.check_collision(entity_a, entity_b)

                if collision_info:
                    # Mark collision
                    collision_pair = (entity_a.id, entity_b.id)
                    current_collisions.add(collision_pair)

                    # Determine if this is a new collision or ongoing
                    is_new = collision_pair not in self._previous_collisions

                    # Call appropriate callbacks
                    collider_a = entity_a.get_component(Collider)
                    collider_b = entity_b.get_component(Collider)

                    if is_new:
                        if collider_a.on_collision_enter:
                            collider_a.on_collision_enter(entity_b, collision_info)
                        if collider_b.on_collision_enter:
                            # Flip collision info for B
                            flipped_info = CollisionInfo(
                                entity_a=entity_b,
                                entity_b=entity_a,
                                normal=(
                                    -collision_info.normal[0],
                                    -collision_info.normal[1],
                                ),
                                penetration=collision_info.penetration,
                                point=collision_info.point,
                            )
                            collider_b.on_collision_enter(entity_a, flipped_info)
                    else:
                        if collider_a.on_collision_stay:
                            collider_a.on_collision_stay(entity_b, collision_info)
                        if collider_b.on_collision_stay:
                            flipped_info = CollisionInfo(
                                entity_a=entity_b,
                                entity_b=entity_a,
                                normal=(
                                    -collision_info.normal[0],
                                    -collision_info.normal[1],
                                ),
                                penetration=collision_info.penetration,
                                point=collision_info.point,
                            )
                            collider_b.on_collision_stay(entity_a, flipped_info)

        # Check for collision exits
        for collision_pair in self._previous_collisions:
            if collision_pair not in current_collisions:
                entity_a_id, entity_b_id = collision_pair
                entity_a = world._entities.get(entity_a_id)
                entity_b = world._entities.get(entity_b_id)

                if entity_a and entity_b:
                    collider_a = entity_a.get_component(Collider)
                    collider_b = entity_b.get_component(Collider)

                    if collider_a and collider_a.on_collision_exit:
                        collider_a.on_collision_exit(entity_b)
                    if collider_b and collider_b.on_collision_exit:
                        collider_b.on_collision_exit(entity_a)

        # Update previous collisions
        self._previous_collisions = current_collisions
