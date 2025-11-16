"""
Tests for Pathfinding System

Tests the A* pathfinding algorithm, path smoothing, line of sight,
and movement range calculations.
"""

import pytest

from neonworks.core.ecs import Navmesh, World
from neonworks.systems.pathfinding import PathNode, PathfindingSystem


class TestPathNode:
    """Test suite for PathNode"""

    def test_init_basic(self):
        """Test basic PathNode initialization"""
        node = PathNode(x=5, y=10, g_cost=2.0, h_cost=3.0)

        assert node.x == 5
        assert node.y == 10
        assert node.g_cost == 2.0
        assert node.h_cost == 3.0
        assert node.f_cost == 5.0
        assert node.parent is None

    def test_init_with_parent(self):
        """Test PathNode with parent"""
        parent = PathNode(x=0, y=0, g_cost=0.0, h_cost=5.0)
        node = PathNode(x=1, y=0, g_cost=1.0, h_cost=4.0, parent=parent)

        assert node.parent is parent
        assert node.parent.x == 0
        assert node.parent.y == 0

    def test_f_cost_calculation(self):
        """Test f_cost is correctly calculated"""
        node = PathNode(x=0, y=0, g_cost=10.0, h_cost=20.0)

        assert node.f_cost == 30.0

    def test_comparison_less_than(self):
        """Test node comparison (for heap)"""
        node1 = PathNode(x=0, y=0, g_cost=5.0, h_cost=5.0)  # f_cost = 10
        node2 = PathNode(x=1, y=1, g_cost=10.0, h_cost=5.0)  # f_cost = 15

        assert node1 < node2
        assert not node2 < node1

    def test_equality(self):
        """Test node equality (based on position)"""
        node1 = PathNode(x=5, y=10, g_cost=0.0, h_cost=0.0)
        node2 = PathNode(x=5, y=10, g_cost=99.0, h_cost=99.0)
        node3 = PathNode(x=6, y=10, g_cost=0.0, h_cost=0.0)

        assert node1 == node2  # Same position
        assert node1 != node3  # Different position

    def test_hash(self):
        """Test node hashing (for sets/dicts)"""
        node1 = PathNode(x=5, y=10, g_cost=0.0, h_cost=0.0)
        node2 = PathNode(x=5, y=10, g_cost=99.0, h_cost=99.0)
        node3 = PathNode(x=6, y=10, g_cost=0.0, h_cost=0.0)

        assert hash(node1) == hash(node2)
        assert hash(node1) != hash(node3)

        # Can be used in sets
        node_set = {node1, node2, node3}
        assert len(node_set) == 2  # node1 and node2 are considered equal


class TestPathfindingSystem:
    """Test suite for PathfindingSystem"""

    def test_init(self):
        """Test PathfindingSystem initialization"""
        system = PathfindingSystem()

        assert system.priority == -40
        assert system.navmesh_entity is None
        assert system.navmesh is None

    def test_update_caches_navmesh(self):
        """Test update caches navmesh from world"""
        world = World()
        system = PathfindingSystem()

        # Create navmesh entity
        navmesh_entity = world.create_entity("Navmesh")
        navmesh = Navmesh(walkable_cells={(0, 0), (1, 0), (2, 0)})
        navmesh_entity.add_component(navmesh)

        # Update should cache it
        system.update(world, 0.016)

        assert system.navmesh_entity is navmesh_entity
        assert system.navmesh is navmesh

    def test_update_only_caches_once(self):
        """Test update doesn't re-cache navmesh"""
        world = World()
        system = PathfindingSystem()

        navmesh_entity = world.create_entity("Navmesh")
        navmesh = Navmesh(walkable_cells={(0, 0)})
        navmesh_entity.add_component(navmesh)

        system.update(world, 0.016)
        first_navmesh = system.navmesh

        # Create another navmesh
        world.create_entity("Navmesh2").add_component(Navmesh(walkable_cells={(5, 5)}))

        system.update(world, 0.016)

        # Should still have the first navmesh
        assert system.navmesh is first_navmesh

    def test_heuristic_manhattan_distance(self):
        """Test Manhattan distance heuristic"""
        system = PathfindingSystem()

        # Horizontal distance
        assert system._heuristic(0, 0, 5, 0) == 5

        # Vertical distance
        assert system._heuristic(0, 0, 0, 5) == 5

        # Diagonal distance (Manhattan)
        assert system._heuristic(0, 0, 3, 4) == 7  # 3 + 4

        # Negative coordinates
        assert system._heuristic(-5, -5, 5, 5) == 20  # 10 + 10

    def test_get_neighbors_four_directional(self):
        """Test getting 4-directional neighbors"""
        system = PathfindingSystem()

        neighbors = system._get_neighbors(5, 5)

        assert len(neighbors) == 4
        assert (5, 4) in neighbors  # North
        assert (6, 5) in neighbors  # East
        assert (5, 6) in neighbors  # South
        assert (4, 5) in neighbors  # West

    def test_get_neighbors_at_origin(self):
        """Test neighbors at origin include negatives"""
        system = PathfindingSystem()

        neighbors = system._get_neighbors(0, 0)

        assert (0, -1) in neighbors
        assert (1, 0) in neighbors
        assert (0, 1) in neighbors
        assert (-1, 0) in neighbors

    def test_find_path_straight_line(self):
        """Test finding path in straight line"""
        system = PathfindingSystem()

        # Create simple navmesh (horizontal line)
        navmesh = Navmesh(walkable_cells={(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)})

        path = system.find_path(0, 0, 4, 0, navmesh)

        assert path is not None
        assert len(path) == 5
        assert path[0] == (0, 0)
        assert path[-1] == (4, 0)

    def test_find_path_with_turn(self):
        """Test finding path with turn"""
        system = PathfindingSystem()

        # L-shaped corridor
        navmesh = Navmesh(
            walkable_cells={(0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (2, 3)}
        )

        path = system.find_path(0, 0, 2, 3, navmesh)

        assert path is not None
        assert len(path) == 6
        assert path[0] == (0, 0)
        assert path[-1] == (2, 3)
        assert (2, 0) in path  # Should pass through corner

    def test_find_path_around_obstacle(self):
        """Test pathfinding around obstacle"""
        system = PathfindingSystem()

        # Create grid with obstacle in middle
        walkable = set()
        for x in range(5):
            for y in range(5):
                if not (x == 2 and y in [1, 2, 3]):  # Obstacle column
                    walkable.add((x, y))

        navmesh = Navmesh(walkable_cells=walkable)

        path = system.find_path(0, 2, 4, 2, navmesh)

        assert path is not None
        assert path[0] == (0, 2)
        assert path[-1] == (4, 2)
        # Should route around obstacle
        assert (2, 1) not in path
        assert (2, 2) not in path
        assert (2, 3) not in path

    def test_find_path_no_path_available(self):
        """Test pathfinding when no path exists"""
        system = PathfindingSystem()

        # Two separate islands
        navmesh = Navmesh(walkable_cells={(0, 0), (1, 0), (5, 5), (6, 5)})

        path = system.find_path(0, 0, 5, 5, navmesh)

        assert path is None

    def test_find_path_start_not_walkable(self):
        """Test pathfinding with unwalkable start"""
        system = PathfindingSystem()

        navmesh = Navmesh(walkable_cells={(1, 0), (2, 0), (3, 0)})

        path = system.find_path(0, 0, 3, 0, navmesh)

        assert path is None

    def test_find_path_goal_not_walkable(self):
        """Test pathfinding with unwalkable goal"""
        system = PathfindingSystem()

        navmesh = Navmesh(walkable_cells={(0, 0), (1, 0), (2, 0)})

        path = system.find_path(0, 0, 3, 0, navmesh)

        assert path is None

    def test_find_path_no_navmesh(self):
        """Test pathfinding without navmesh returns None"""
        system = PathfindingSystem()

        path = system.find_path(0, 0, 5, 5, navmesh=None)

        assert path is None

    def test_find_path_with_different_costs(self):
        """Test pathfinding prefers lower cost paths"""
        system = PathfindingSystem()

        # Create two possible paths
        # Top path: (0,0) -> (1,0) -> (2,0) -> (2,1) -> (2,2)
        # Bottom path: (0,0) -> (0,1) -> (0,2) -> (1,2) -> (2,2)
        walkable = {
            (0, 0),
            (1, 0),
            (2, 0),
            (2, 1),
            (2, 2),
            (0, 1),
            (0, 2),
            (1, 2),
        }

        # Make bottom path expensive
        cost_multipliers = {
            (0, 1): 10.0,
            (0, 2): 10.0,
            (1, 2): 10.0,
        }

        navmesh = Navmesh(walkable_cells=walkable, cost_multipliers=cost_multipliers)

        path = system.find_path(0, 0, 2, 2, navmesh)

        assert path is not None
        # Should prefer top path (cheaper)
        assert (1, 0) in path
        assert (2, 0) in path
        assert (2, 1) in path
        # Should avoid expensive bottom path
        assert (0, 1) not in path

    def test_find_path_same_start_and_goal(self):
        """Test pathfinding when start equals goal"""
        system = PathfindingSystem()

        navmesh = Navmesh(walkable_cells={(5, 5)})

        path = system.find_path(5, 5, 5, 5, navmesh)

        assert path is not None
        assert len(path) == 1
        assert path[0] == (5, 5)

    def test_reconstruct_path(self):
        """Test path reconstruction from nodes"""
        system = PathfindingSystem()

        # Create a chain of nodes
        node1 = PathNode(0, 0, 0.0, 0.0, None)
        node2 = PathNode(1, 0, 1.0, 0.0, node1)
        node3 = PathNode(2, 0, 2.0, 0.0, node2)

        path = system._reconstruct_path(node3)

        assert len(path) == 3
        assert path[0] == (0, 0)
        assert path[1] == (1, 0)
        assert path[2] == (2, 0)

    def test_reconstruct_path_single_node(self):
        """Test reconstructing path with single node"""
        system = PathfindingSystem()

        node = PathNode(5, 5, 0.0, 0.0, None)

        path = system._reconstruct_path(node)

        assert len(path) == 1
        assert path[0] == (5, 5)

    def test_get_path_cost_basic(self):
        """Test calculating path cost"""
        system = PathfindingSystem()

        navmesh = Navmesh(walkable_cells={(0, 0), (1, 0), (2, 0)})
        path = [(0, 0), (1, 0), (2, 0)]

        cost = system.get_path_cost(path, navmesh)

        assert cost == 3.0  # 1.0 per cell

    def test_get_path_cost_with_multipliers(self):
        """Test path cost with cost multipliers"""
        system = PathfindingSystem()

        cost_multipliers = {(0, 0): 1.0, (1, 0): 2.0, (2, 0): 3.0}
        navmesh = Navmesh(
            walkable_cells={(0, 0), (1, 0), (2, 0)}, cost_multipliers=cost_multipliers
        )
        path = [(0, 0), (1, 0), (2, 0)]

        cost = system.get_path_cost(path, navmesh)

        assert cost == 6.0  # 1.0 + 2.0 + 3.0

    def test_get_path_cost_empty_path(self):
        """Test path cost for empty path"""
        system = PathfindingSystem()

        navmesh = Navmesh(walkable_cells=set())
        cost = system.get_path_cost([], navmesh)

        assert cost == 0.0

    def test_is_line_of_sight_clear(self):
        """Test line of sight with clear path"""
        system = PathfindingSystem()

        # Straight horizontal line
        navmesh = Navmesh(walkable_cells={(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)})

        assert system.is_line_of_sight(0, 0, 4, 0, navmesh)

    def test_is_line_of_sight_blocked(self):
        """Test line of sight with obstacle"""
        system = PathfindingSystem()

        # Obstacle at (2, 0)
        navmesh = Navmesh(walkable_cells={(0, 0), (1, 0), (3, 0), (4, 0)})

        assert not system.is_line_of_sight(0, 0, 4, 0, navmesh)

    def test_is_line_of_sight_diagonal(self):
        """Test line of sight diagonal"""
        system = PathfindingSystem()

        # Diagonal line from (0,0) to (3,3)
        walkable = set()
        for i in range(4):
            for j in range(4):
                walkable.add((i, j))

        navmesh = Navmesh(walkable_cells=walkable)

        assert system.is_line_of_sight(0, 0, 3, 3, navmesh)

    def test_is_line_of_sight_single_point(self):
        """Test line of sight from point to itself"""
        system = PathfindingSystem()

        navmesh = Navmesh(walkable_cells={(5, 5)})

        assert system.is_line_of_sight(5, 5, 5, 5, navmesh)

    def test_smooth_path_no_smoothing_needed(self):
        """Test path smoothing with straight path"""
        system = PathfindingSystem()

        navmesh = Navmesh(walkable_cells={(0, 0), (1, 0), (2, 0), (3, 0)})
        path = [(0, 0), (1, 0), (2, 0), (3, 0)]

        smoothed = system.smooth_path(path, navmesh)

        # Should reduce to start and end
        assert len(smoothed) == 2
        assert smoothed[0] == (0, 0)
        assert smoothed[-1] == (3, 0)

    def test_smooth_path_with_obstacle(self):
        """Test path smoothing around obstacle"""
        system = PathfindingSystem()

        # Path goes around obstacle
        walkable = {(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (3, 2), (3, 1), (3, 0)}
        navmesh = Navmesh(walkable_cells=walkable)

        # Unsmoothed path
        path = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (3, 2), (3, 1), (3, 0)]

        smoothed = system.smooth_path(path, navmesh)

        # Should still include waypoints (can't cut through obstacle)
        assert smoothed[0] == (0, 0)
        assert smoothed[-1] == (3, 0)
        assert len(smoothed) < len(path)  # Should be shorter

    def test_smooth_path_single_point(self):
        """Test smoothing path with single point"""
        system = PathfindingSystem()

        navmesh = Navmesh(walkable_cells={(0, 0)})
        path = [(0, 0)]

        smoothed = system.smooth_path(path, navmesh)

        assert smoothed == [(0, 0)]

    def test_smooth_path_two_points(self):
        """Test smoothing path with two points"""
        system = PathfindingSystem()

        navmesh = Navmesh(walkable_cells={(0, 0), (1, 0)})
        path = [(0, 0), (1, 0)]

        smoothed = system.smooth_path(path, navmesh)

        assert smoothed == [(0, 0), (1, 0)]

    def test_get_movement_range_basic(self):
        """Test getting movement range"""
        system = PathfindingSystem()

        # 3x3 grid, all walkable
        walkable = set()
        for x in range(3):
            for y in range(3):
                walkable.add((x, y))

        navmesh = Navmesh(walkable_cells=walkable)

        # Movement range of 2 from center
        reachable = system.get_movement_range(1, 1, 2, navmesh)

        # Should include center and all adjacent cells within 2 moves
        assert (1, 1) in reachable  # Center
        assert (0, 1) in reachable  # 1 move
        assert (2, 1) in reachable  # 1 move
        assert (1, 0) in reachable  # 1 move
        assert (1, 2) in reachable  # 1 move
        assert (0, 0) in reachable  # 2 moves
        assert (2, 2) in reachable  # 2 moves

    def test_get_movement_range_with_obstacle(self):
        """Test movement range with obstacle"""
        system = PathfindingSystem()

        # Grid with obstacle blocking path
        walkable = {
            (0, 0),
            (1, 0),
            (2, 0),
            (0, 1),
            # (1, 1) - obstacle
            (2, 1),
            (0, 2),
            (1, 2),
            (2, 2),
        }

        navmesh = Navmesh(walkable_cells=walkable)

        # Start at (0, 0), movement range 2
        reachable = system.get_movement_range(0, 0, 2, navmesh)

        assert (0, 0) in reachable
        assert (1, 0) in reachable
        assert (2, 0) in reachable
        assert (0, 1) in reachable
        assert (0, 2) in reachable
        # Can't reach (2, 2) in 2 moves due to obstacle
        assert (2, 2) not in reachable

    def test_get_movement_range_zero_movement(self):
        """Test movement range with zero movement points"""
        system = PathfindingSystem()

        navmesh = Navmesh(walkable_cells={(0, 0), (1, 0), (2, 0)})

        reachable = system.get_movement_range(0, 0, 0, navmesh)

        # Should only include starting position
        assert len(reachable) == 1
        assert (0, 0) in reachable

    def test_get_movement_range_with_costs(self):
        """Test movement range respects movement costs"""
        system = PathfindingSystem()

        # Grid where some cells cost more
        walkable = {(0, 0), (1, 0), (2, 0), (3, 0)}
        cost_multipliers = {
            (0, 0): 1.0,
            (1, 0): 2.0,  # Expensive
            (2, 0): 1.0,
            (3, 0): 1.0,
        }

        navmesh = Navmesh(walkable_cells=walkable, cost_multipliers=cost_multipliers)

        # 3 movement points from (0, 0)
        reachable = system.get_movement_range(0, 0, 3, navmesh)

        assert (0, 0) in reachable  # 0 cost (start)
        assert (1, 0) in reachable  # 2 cost
        assert (2, 0) in reachable  # 2 + 1 = 3 cost
        # (3, 0) would require 4 cost total (2 for (1,0) + 1 for (2,0) + 1 for (3,0))
        assert (3, 0) not in reachable

    def test_get_movement_range_large_range(self):
        """Test movement range with large movement points"""
        system = PathfindingSystem()

        # 5x5 grid
        walkable = set()
        for x in range(5):
            for y in range(5):
                walkable.add((x, y))

        navmesh = Navmesh(walkable_cells=walkable)

        # Large movement range
        reachable = system.get_movement_range(0, 0, 100, navmesh)

        # Should include entire grid
        assert len(reachable) == 25


class TestIntegration:
    """Integration tests for pathfinding system"""

    def test_full_pathfinding_workflow(self):
        """Test complete pathfinding workflow"""
        world = World()
        system = PathfindingSystem()

        # Create navmesh
        navmesh_entity = world.create_entity("Navmesh")
        walkable = set()
        for x in range(10):
            for y in range(10):
                if not (x == 5 and y in range(3, 8)):  # Obstacle
                    walkable.add((x, y))

        navmesh = Navmesh(walkable_cells=walkable)
        navmesh_entity.add_component(navmesh)

        # Update to cache navmesh
        system.update(world, 0.016)

        # Find path (system should use cached navmesh)
        path = system.find_path(0, 5, 9, 5)

        assert path is not None
        assert path[0] == (0, 5)
        assert path[-1] == (9, 5)

        # Smooth the path
        smoothed = system.smooth_path(path, navmesh)

        assert len(smoothed) <= len(path)
        assert smoothed[0] == (0, 5)
        assert smoothed[-1] == (9, 5)

    def test_pathfinding_with_multiple_agents(self):
        """Test pathfinding for multiple agents"""
        system = PathfindingSystem()

        # Create shared navmesh
        walkable = set()
        for x in range(20):
            for y in range(20):
                walkable.add((x, y))

        navmesh = Navmesh(walkable_cells=walkable)

        # Find paths for multiple agents
        paths = []
        for i in range(5):
            path = system.find_path(0, i * 2, 19, i * 2, navmesh)
            assert path is not None
            paths.append(path)

        # All paths should succeed
        assert len(paths) == 5
        for i, path in enumerate(paths):
            assert path[0] == (0, i * 2)
            assert path[-1] == (19, i * 2)

    def test_pathfinding_performance(self):
        """Test pathfinding on larger grid"""
        system = PathfindingSystem()

        # Create 50x50 grid
        walkable = set()
        for x in range(50):
            for y in range(50):
                walkable.add((x, y))

        navmesh = Navmesh(walkable_cells=walkable)

        # Find long path
        path = system.find_path(0, 0, 49, 49, navmesh)

        assert path is not None
        assert path[0] == (0, 0)
        assert path[-1] == (49, 49)
        # Path length should be approximately Manhattan distance
        assert len(path) >= 99  # At least 98 moves + start
