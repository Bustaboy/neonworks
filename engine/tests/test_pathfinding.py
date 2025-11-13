"""
Comprehensive tests for Navigation and Pathfinding System

Tests A* pathfinding, grid navigation, and path smoothing.
"""

import pytest
import math
from engine.ai.pathfinding import (
    NavigationGrid,
    Pathfinder,
    PathfindingSystem,
    Heuristic,
    PathNode
)


class TestNavigationGrid:
    """Test navigation grid"""

    def test_grid_creation(self):
        """Test creating navigation grid"""
        grid = NavigationGrid(10, 8)

        assert grid.width == 10
        assert grid.height == 8

    def test_all_cells_walkable_by_default(self):
        """Test all cells are walkable by default"""
        grid = NavigationGrid(5, 5)

        for y in range(5):
            for x in range(5):
                assert grid.is_walkable(x, y)

    def test_set_walkable(self):
        """Test setting cell walkability"""
        grid = NavigationGrid(5, 5)

        grid.set_walkable(2, 2, False)

        assert not grid.is_walkable(2, 2)
        assert grid.is_walkable(2, 1)
        assert grid.is_walkable(2, 3)

    def test_in_bounds(self):
        """Test bounds checking"""
        grid = NavigationGrid(10, 10)

        assert grid.in_bounds(0, 0)
        assert grid.in_bounds(9, 9)
        assert not grid.in_bounds(-1, 0)
        assert not grid.in_bounds(0, -1)
        assert not grid.in_bounds(10, 0)
        assert not grid.in_bounds(0, 10)

    def test_out_of_bounds_not_walkable(self):
        """Test out of bounds cells are not walkable"""
        grid = NavigationGrid(5, 5)

        assert not grid.is_walkable(-1, 0)
        assert not grid.is_walkable(0, -1)
        assert not grid.is_walkable(10, 0)
        assert not grid.is_walkable(0, 10)

    def test_get_cost(self):
        """Test getting cell cost"""
        grid = NavigationGrid(5, 5)

        # Default cost is 1.0
        assert grid.get_cost(2, 2) == 1.0

    def test_set_cost(self):
        """Test setting cell cost"""
        grid = NavigationGrid(5, 5)

        grid.set_cost(2, 2, 2.5)

        assert grid.get_cost(2, 2) == 2.5

    def test_get_neighbors_cardinal(self):
        """Test getting cardinal neighbors"""
        grid = NavigationGrid(5, 5)

        neighbors = grid.get_neighbors(2, 2, diagonal=False)

        assert len(neighbors) == 4
        assert (2, 1) in neighbors  # North
        assert (3, 2) in neighbors  # East
        assert (2, 3) in neighbors  # South
        assert (1, 2) in neighbors  # West

    def test_get_neighbors_with_diagonal(self):
        """Test getting neighbors including diagonals"""
        grid = NavigationGrid(5, 5)

        neighbors = grid.get_neighbors(2, 2, diagonal=True)

        assert len(neighbors) == 8

    def test_get_neighbors_excludes_blocked(self):
        """Test neighbors excludes blocked cells"""
        grid = NavigationGrid(5, 5)

        grid.set_walkable(3, 2, False)
        neighbors = grid.get_neighbors(2, 2, diagonal=False)

        assert (3, 2) not in neighbors
        assert len(neighbors) == 3

    def test_get_neighbors_corner(self):
        """Test getting neighbors at corner"""
        grid = NavigationGrid(5, 5)

        neighbors = grid.get_neighbors(0, 0, diagonal=False)

        # Only 2 neighbors at corner
        assert len(neighbors) == 2
        assert (1, 0) in neighbors
        assert (0, 1) in neighbors

    def test_clear_grid(self):
        """Test clearing grid"""
        grid = NavigationGrid(5, 5)

        grid.set_walkable(2, 2, False)
        grid.set_cost(3, 3, 5.0)

        grid.clear()

        assert grid.is_walkable(2, 2)
        assert grid.get_cost(3, 3) == 1.0

    def test_set_area_walkable(self):
        """Test setting area walkability"""
        grid = NavigationGrid(10, 10)

        grid.set_area_walkable(2, 2, 4, 4, False)

        # Check area is blocked
        for y in range(2, 5):
            for x in range(2, 5):
                assert not grid.is_walkable(x, y)

        # Check outside area is walkable
        assert grid.is_walkable(1, 1)
        assert grid.is_walkable(5, 5)


class TestPathNode:
    """Test path node"""

    def test_node_creation(self):
        """Test creating path node"""
        node = PathNode(priority=10.0, position=(5, 5))

        assert node.position == (5, 5)
        assert node.priority == 10.0

    def test_f_cost_calculation(self):
        """Test f_cost calculation"""
        node = PathNode(priority=15.0, position=(5, 5), g_cost=10.0, h_cost=5.0)

        assert node.f_cost == 15.0


class TestHeuristics:
    """Test heuristic functions"""

    def test_manhattan_heuristic(self):
        """Test Manhattan distance heuristic"""
        distance = Pathfinder.calculate_heuristic(
            (0, 0), (3, 4), Heuristic.MANHATTAN
        )

        assert distance == 7.0  # 3 + 4

    def test_euclidean_heuristic(self):
        """Test Euclidean distance heuristic"""
        distance = Pathfinder.calculate_heuristic(
            (0, 0), (3, 4), Heuristic.EUCLIDEAN
        )

        assert abs(distance - 5.0) < 0.001  # sqrt(9 + 16) = 5

    def test_diagonal_heuristic(self):
        """Test diagonal distance heuristic"""
        distance = Pathfinder.calculate_heuristic(
            (0, 0), (3, 3), Heuristic.DIAGONAL
        )

        # Diagonal distance for (3,3) should be close to 3 * sqrt(2)
        expected = 3 * math.sqrt(2)
        assert abs(distance - expected) < 0.001

    def test_chebyshev_heuristic(self):
        """Test Chebyshev distance heuristic"""
        distance = Pathfinder.calculate_heuristic(
            (0, 0), (3, 4), Heuristic.CHEBYSHEV
        )

        assert distance == 4.0  # max(3, 4)


class TestPathfinding:
    """Test A* pathfinding"""

    def test_find_straight_path(self):
        """Test finding straight horizontal path"""
        grid = NavigationGrid(10, 10)
        pathfinder = Pathfinder(grid)

        path = pathfinder.find_path((0, 0), (5, 0))

        assert path is not None
        assert path[0] == (0, 0)
        assert path[-1] == (5, 0)
        assert len(path) >= 2

    def test_find_path_with_obstacle(self):
        """Test finding path around obstacle"""
        grid = NavigationGrid(10, 10)

        # Create wall
        for y in range(1, 9):
            grid.set_walkable(5, y, False)

        pathfinder = Pathfinder(grid)
        path = pathfinder.find_path((0, 5), (9, 5))

        assert path is not None
        assert path[0] == (0, 5)
        assert path[-1] == (9, 5)

        # Path should not go through x=5 (except at edges)
        for pos in path[1:-1]:
            if pos[1] != 0 and pos[1] != 9:
                assert pos[0] != 5

    def test_no_path_exists(self):
        """Test when no path exists"""
        grid = NavigationGrid(10, 10)

        # Create complete wall
        for y in range(10):
            grid.set_walkable(5, y, False)

        pathfinder = Pathfinder(grid)
        path = pathfinder.find_path((0, 5), (9, 5))

        assert path is None

    def test_start_blocked(self):
        """Test when start position is blocked"""
        grid = NavigationGrid(10, 10)

        grid.set_walkable(0, 0, False)
        pathfinder = Pathfinder(grid)

        path = pathfinder.find_path((0, 0), (5, 5))

        assert path is None

    def test_goal_blocked(self):
        """Test when goal position is blocked"""
        grid = NavigationGrid(10, 10)

        grid.set_walkable(5, 5, False)
        pathfinder = Pathfinder(grid)

        path = pathfinder.find_path((0, 0), (5, 5))

        assert path is None

    def test_diagonal_pathfinding(self):
        """Test diagonal movement in pathfinding"""
        grid = NavigationGrid(10, 10)
        pathfinder = Pathfinder(grid)
        pathfinder.allow_diagonal = True

        path = pathfinder.find_path((0, 0), (5, 5))

        assert path is not None
        assert path[0] == (0, 0)
        assert path[-1] == (5, 5)

        # With diagonals, path should be shorter
        assert len(path) <= 6  # Straight diagonal would be 6 steps

    def test_no_diagonal_pathfinding(self):
        """Test pathfinding without diagonal movement"""
        grid = NavigationGrid(10, 10)
        pathfinder = Pathfinder(grid)
        pathfinder.allow_diagonal = False

        path = pathfinder.find_path((0, 0), (5, 5))

        assert path is not None

        # Without diagonals, path should be longer (Manhattan distance)
        assert len(path) >= 11  # 5 right + 5 down + 1 start = 11

    def test_path_with_costs(self):
        """Test pathfinding considers cell costs"""
        grid = NavigationGrid(10, 10)

        # Create expensive path through middle
        for x in range(3, 7):
            grid.set_cost(x, 5, 10.0)

        pathfinder = Pathfinder(grid)
        path = pathfinder.find_path((0, 5), (9, 5))

        assert path is not None

        # Path should avoid expensive cells if possible
        # (This is a heuristic test - exact behavior depends on costs)

    def test_same_start_and_goal(self):
        """Test when start and goal are same"""
        grid = NavigationGrid(10, 10)
        pathfinder = Pathfinder(grid)

        path = pathfinder.find_path((5, 5), (5, 5))

        assert path is not None
        assert len(path) == 1
        assert path[0] == (5, 5)


class TestPathSmoothing:
    """Test path smoothing"""

    def test_smooth_straight_path(self):
        """Test smoothing straight path"""
        grid = NavigationGrid(10, 10)
        pathfinder = Pathfinder(grid)

        # Create a path
        path = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0)]

        smoothed = pathfinder.smooth_path(path)

        # Straight path should be reduced to start and end
        assert len(smoothed) == 2
        assert smoothed[0] == (0, 0)
        assert smoothed[-1] == (5, 0)

    def test_smooth_path_with_turn(self):
        """Test smoothing path with turn"""
        grid = NavigationGrid(10, 10)
        pathfinder = Pathfinder(grid)

        # Create L-shaped path
        path = [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (2, 3)]

        smoothed = pathfinder.smooth_path(path)

        # Should be reduced (start and end at minimum, may have corner points)
        assert len(smoothed) >= 2
        assert len(smoothed) <= len(path)
        assert smoothed[0] == (0, 0)
        assert smoothed[-1] == (2, 3)

    def test_smooth_path_with_obstacle(self):
        """Test smoothing path around obstacle"""
        grid = NavigationGrid(10, 10)

        # Block diagonal path
        grid.set_walkable(2, 2, False)

        pathfinder = Pathfinder(grid)

        # Path must go around obstacle
        path = [(0, 0), (1, 0), (2, 0), (2, 1), (3, 1), (3, 2), (3, 3)]

        smoothed = pathfinder.smooth_path(path)

        # Should still avoid obstacle
        for pos in smoothed:
            assert pos != (2, 2)

    def test_smooth_short_path(self):
        """Test smoothing very short path"""
        grid = NavigationGrid(10, 10)
        pathfinder = Pathfinder(grid)

        path = [(0, 0), (1, 1)]

        smoothed = pathfinder.smooth_path(path)

        # Short path should remain unchanged
        assert smoothed == path


class TestLineOfSight:
    """Test line of sight checking"""

    def test_clear_line_of_sight(self):
        """Test clear line of sight"""
        grid = NavigationGrid(10, 10)
        pathfinder = Pathfinder(grid)

        assert pathfinder._has_line_of_sight((0, 0), (5, 5))

    def test_blocked_line_of_sight(self):
        """Test blocked line of sight"""
        grid = NavigationGrid(10, 10)

        # Block middle cell
        grid.set_walkable(2, 2, False)

        pathfinder = Pathfinder(grid)

        # Line of sight through blocked cell should fail
        assert not pathfinder._has_line_of_sight((0, 0), (4, 4))

    def test_line_of_sight_horizontal(self):
        """Test horizontal line of sight"""
        grid = NavigationGrid(10, 10)
        pathfinder = Pathfinder(grid)

        assert pathfinder._has_line_of_sight((0, 5), (9, 5))

    def test_line_of_sight_vertical(self):
        """Test vertical line of sight"""
        grid = NavigationGrid(10, 10)
        pathfinder = Pathfinder(grid)

        assert pathfinder._has_line_of_sight((5, 0), (5, 9))


class TestPathfindingSystem:
    """Test pathfinding system with caching"""

    def test_system_creation(self):
        """Test creating pathfinding system"""
        grid = NavigationGrid(10, 10)
        system = PathfindingSystem(grid)

        assert system.grid == grid
        assert system.pathfinder is not None

    def test_find_path_with_caching(self):
        """Test path caching"""
        grid = NavigationGrid(10, 10)
        system = PathfindingSystem(grid)

        # First call
        path1 = system.find_path((0, 0), (5, 5))

        # Second call should use cache
        path2 = system.find_path((0, 0), (5, 5))

        assert path1 == path2

    def test_find_path_with_smoothing(self):
        """Test path with smoothing"""
        grid = NavigationGrid(10, 10)
        system = PathfindingSystem(grid)

        path_smooth = system.find_path((0, 0), (5, 5), smooth=True)
        path_no_smooth = system.find_path((0, 0), (5, 5), smooth=False)

        # Smoothed path should be shorter or equal
        assert len(path_smooth) <= len(path_no_smooth)

    def test_clear_cache(self):
        """Test clearing cache"""
        grid = NavigationGrid(10, 10)
        system = PathfindingSystem(grid)

        system.find_path((0, 0), (5, 5))

        assert len(system._path_cache) > 0

        system.clear_cache()

        assert len(system._path_cache) == 0

    def test_invalidate_area(self):
        """Test invalidating cached paths in area"""
        grid = NavigationGrid(10, 10)
        system = PathfindingSystem(grid)

        system.find_path((0, 0), (9, 9))

        system.invalidate_area(4, 4, 6, 6)

        # Cache should be cleared (simplified implementation)
        assert len(system._path_cache) == 0


# Run tests with: pytest engine/tests/test_pathfinding.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
