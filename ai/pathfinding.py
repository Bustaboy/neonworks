"""
Navigation and Pathfinding System

A* pathfinding algorithm with grid-based navigation.
Optimized with NumPy for improved performance.
"""

from typing import List, Tuple, Optional, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
import heapq
import math
import numpy as np


class Heuristic(Enum):
    """Heuristic functions for A* pathfinding"""

    MANHATTAN = "manhattan"
    EUCLIDEAN = "euclidean"
    DIAGONAL = "diagonal"
    CHEBYSHEV = "chebyshev"


@dataclass(order=True)
class PathNode:
    """Node for A* pathfinding"""

    priority: float
    position: Tuple[int, int] = field(compare=False)
    g_cost: float = field(default=0.0, compare=False)
    h_cost: float = field(default=0.0, compare=False)
    parent: Optional["PathNode"] = field(default=None, compare=False)

    @property
    def f_cost(self) -> float:
        """Total cost (g + h)"""
        return self.g_cost + self.h_cost


class NavigationGrid:
    """
    Grid-based navigation system.

    Manages a 2D grid for pathfinding with walkable/unwalkable cells.
    """

    def __init__(self, width: int, height: int):
        """
        Initialize navigation grid.

        Args:
            width: Grid width in cells
            height: Grid height in cells
        """
        self.width = width
        self.height = height

        # Grid cells (True = walkable, False = blocked) - using NumPy for performance
        self._grid: np.ndarray = np.ones((height, width), dtype=bool)

        # Movement costs (default 1.0 for all cells) - using NumPy for performance
        self._costs: np.ndarray = np.ones((height, width), dtype=np.float32)

    def is_walkable(self, x: int, y: int) -> bool:
        """
        Check if cell is walkable.

        Args:
            x: Grid X coordinate
            y: Grid Y coordinate

        Returns:
            True if cell is walkable
        """
        if not self.in_bounds(x, y):
            return False
        return self._grid[y][x]

    def set_walkable(self, x: int, y: int, walkable: bool):
        """
        Set cell walkability.

        Args:
            x: Grid X coordinate
            y: Grid Y coordinate
            walkable: Whether cell is walkable
        """
        if self.in_bounds(x, y):
            self._grid[y][x] = walkable

    def get_cost(self, x: int, y: int) -> float:
        """Get movement cost for cell"""
        if not self.in_bounds(x, y):
            return float("inf")
        return self._costs[y][x]

    def set_cost(self, x: int, y: int, cost: float):
        """Set movement cost for cell"""
        if self.in_bounds(x, y):
            self._costs[y][x] = cost

    def in_bounds(self, x: int, y: int) -> bool:
        """Check if coordinates are within grid bounds"""
        return 0 <= x < self.width and 0 <= y < self.height

    def get_neighbors(
        self, x: int, y: int, diagonal: bool = True
    ) -> List[Tuple[int, int]]:
        """
        Get walkable neighbors of a cell.

        Args:
            x: Grid X coordinate
            y: Grid Y coordinate
            diagonal: Include diagonal neighbors

        Returns:
            List of (x, y) coordinates of walkable neighbors
        """
        neighbors = []

        # Cardinal directions
        directions = [
            (0, -1),  # North
            (1, 0),  # East
            (0, 1),  # South
            (-1, 0),  # West
        ]

        # Diagonal directions
        if diagonal:
            directions.extend(
                [
                    (1, -1),  # NE
                    (1, 1),  # SE
                    (-1, 1),  # SW
                    (-1, -1),  # NW
                ]
            )

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self.is_walkable(nx, ny):
                # For diagonals, check if both adjacent cells are walkable
                if diagonal and abs(dx) == 1 and abs(dy) == 1:
                    if not (
                        self.is_walkable(x + dx, y) and self.is_walkable(x, y + dy)
                    ):
                        continue  # Skip diagonal if adjacent cells blocked
                neighbors.append((nx, ny))

        return neighbors

    def clear(self):
        """Clear grid (make all cells walkable)"""
        self._grid.fill(True)
        self._costs.fill(1.0)

    def set_area_walkable(self, x1: int, y1: int, x2: int, y2: int, walkable: bool):
        """Set walkability for rectangular area - vectorized with NumPy"""
        min_x, max_x = max(0, min(x1, x2)), min(self.width - 1, max(x1, x2))
        min_y, max_y = max(0, min(y1, y2)), min(self.height - 1, max(y1, y2))
        self._grid[min_y : max_y + 1, min_x : max_x + 1] = walkable


class Pathfinder:
    """
    A* pathfinding algorithm implementation.

    Finds optimal paths through NavigationGrid.
    """

    def __init__(self, grid: NavigationGrid):
        """
        Initialize pathfinder.

        Args:
            grid: Navigation grid to use
        """
        self.grid = grid
        self.heuristic = Heuristic.EUCLIDEAN
        self.allow_diagonal = True

    @staticmethod
    def calculate_heuristic(
        start: Tuple[int, int], goal: Tuple[int, int], heuristic: Heuristic
    ) -> float:
        """
        Calculate heuristic distance between two points.
        Optimized with NumPy for better performance.

        Args:
            start: Start position (x, y)
            goal: Goal position (x, y)
            heuristic: Heuristic function to use

        Returns:
            Estimated distance
        """
        dx = abs(start[0] - goal[0])
        dy = abs(start[1] - goal[1])

        if heuristic == Heuristic.MANHATTAN:
            return float(dx + dy)
        elif heuristic == Heuristic.EUCLIDEAN:
            # Use NumPy for faster sqrt calculation
            return float(np.sqrt(dx * dx + dy * dy))
        elif heuristic == Heuristic.DIAGONAL:
            # Diagonal distance (Chebyshev with diagonal cost)
            return float(max(dx, dy) + (np.sqrt(2) - 1) * min(dx, dy))
        elif heuristic == Heuristic.CHEBYSHEV:
            return float(max(dx, dy))

        return 0.0

    def find_path(
        self, start: Tuple[int, int], goal: Tuple[int, int]
    ) -> Optional[List[Tuple[int, int]]]:
        """
        Find path from start to goal using A* algorithm.

        Args:
            start: Start position (x, y)
            goal: Goal position (x, y)

        Returns:
            List of (x, y) positions from start to goal, or None if no path exists
        """
        # Validate start and goal
        if not self.grid.is_walkable(start[0], start[1]):
            return None
        if not self.grid.is_walkable(goal[0], goal[1]):
            return None

        # Initialize open and closed sets
        open_set = []
        closed_set: Set[Tuple[int, int]] = set()

        # Create start node
        start_node = PathNode(
            priority=0.0,
            position=start,
            g_cost=0.0,
            h_cost=self.calculate_heuristic(start, goal, self.heuristic),
        )

        heapq.heappush(open_set, start_node)

        # Track best g_cost for each position
        g_costs = {start: 0.0}

        while open_set:
            # Get node with lowest f_cost
            current = heapq.heappop(open_set)

            # Check if we reached the goal
            if current.position == goal:
                return self._reconstruct_path(current)

            # Add to closed set
            closed_set.add(current.position)

            # Check neighbors
            neighbors = self.grid.get_neighbors(
                current.position[0], current.position[1], self.allow_diagonal
            )

            for neighbor_pos in neighbors:
                if neighbor_pos in closed_set:
                    continue

                # Calculate movement cost
                dx = abs(neighbor_pos[0] - current.position[0])
                dy = abs(neighbor_pos[1] - current.position[1])

                # Diagonal movement costs sqrt(2), cardinal costs 1 (using NumPy)
                move_cost = float(np.sqrt(2)) if (dx + dy) == 2 else 1.0

                # Add cell cost
                move_cost *= self.grid.get_cost(neighbor_pos[0], neighbor_pos[1])

                # Calculate tentative g_cost
                tentative_g = current.g_cost + move_cost

                # Check if this is a better path
                if neighbor_pos in g_costs and tentative_g >= g_costs[neighbor_pos]:
                    continue

                # Update g_cost
                g_costs[neighbor_pos] = tentative_g

                # Calculate h_cost
                h_cost = self.calculate_heuristic(neighbor_pos, goal, self.heuristic)

                # Create neighbor node
                neighbor_node = PathNode(
                    priority=tentative_g + h_cost,
                    position=neighbor_pos,
                    g_cost=tentative_g,
                    h_cost=h_cost,
                    parent=current,
                )

                heapq.heappush(open_set, neighbor_node)

        # No path found
        return None

    def _reconstruct_path(self, node: PathNode) -> List[Tuple[int, int]]:
        """Reconstruct path from goal node to start"""
        path = []
        current = node

        while current is not None:
            path.append(current.position)
            current = current.parent

        path.reverse()
        return path

    def smooth_path(self, path: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        Smooth path by removing unnecessary waypoints.

        Uses line-of-sight to remove intermediate points.

        Args:
            path: Original path

        Returns:
            Smoothed path
        """
        if len(path) <= 2:
            return path

        smoothed = [path[0]]
        current_index = 0

        while current_index < len(path) - 1:
            # Try to find furthest visible point
            furthest_index = current_index + 1

            for i in range(len(path) - 1, current_index, -1):
                if self._has_line_of_sight(path[current_index], path[i]):
                    furthest_index = i
                    break

            smoothed.append(path[furthest_index])
            current_index = furthest_index

        return smoothed

    def _has_line_of_sight(self, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        """
        Check if there's a clear line of sight between two points.

        Uses Bresenham's line algorithm.

        Args:
            start: Start position
            end: End position

        Returns:
            True if line of sight is clear
        """
        x0, y0 = start
        x1, y1 = end

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)

        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1

        err = dx - dy

        while True:
            # Check if current cell is walkable
            if not self.grid.is_walkable(x0, y0):
                return False

            if x0 == x1 and y0 == y1:
                break

            e2 = 2 * err

            if e2 > -dy:
                err -= dy
                x0 += sx

            if e2 < dx:
                err += dx
                y0 += sy

        return True


class PathfindingSystem:
    """
    System for managing pathfinding requests.

    Provides caching and batch processing.
    """

    def __init__(self, grid: NavigationGrid):
        """
        Initialize pathfinding system.

        Args:
            grid: Navigation grid
        """
        self.grid = grid
        self.pathfinder = Pathfinder(grid)
        self._path_cache: dict = {}
        self._cache_size = 100

    def find_path(
        self, start: Tuple[int, int], goal: Tuple[int, int], smooth: bool = True
    ) -> Optional[List[Tuple[int, int]]]:
        """
        Find path with optional caching.

        Args:
            start: Start position
            goal: Goal position
            smooth: Whether to smooth the path

        Returns:
            Path or None if no path exists
        """
        # Check cache
        cache_key = (start, goal, smooth)
        if cache_key in self._path_cache:
            return self._path_cache[cache_key].copy()

        # Find path
        path = self.pathfinder.find_path(start, goal)

        if path is None:
            return None

        # Smooth if requested
        if smooth:
            path = self.pathfinder.smooth_path(path)

        # Cache result
        self._add_to_cache(cache_key, path)

        return path.copy()

    def _add_to_cache(self, key, value):
        """Add path to cache with size limit"""
        if len(self._path_cache) >= self._cache_size:
            # Remove oldest entry (FIFO)
            self._path_cache.pop(next(iter(self._path_cache)))

        self._path_cache[key] = value

    def clear_cache(self):
        """Clear path cache"""
        self._path_cache.clear()

    def invalidate_area(self, x1: int, y1: int, x2: int, y2: int):
        """
        Invalidate cached paths that pass through an area.

        Args:
            x1, y1: Top-left corner
            x2, y2: Bottom-right corner
        """
        # For simplicity, just clear entire cache
        # In production, would check which paths intersect the area
        self.clear_cache()
