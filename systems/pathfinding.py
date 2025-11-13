"""
Pathfinding System

A* pathfinding with navmesh support and intelligent path planning.
"""

from typing import List, Tuple, Optional, Set
import heapq
from engine.core.ecs import System, World, Entity, GridPosition, Navmesh


class PathNode:
    """Node for A* pathfinding"""

    def __init__(self, x: int, y: int, g_cost: float, h_cost: float, parent: Optional['PathNode'] = None):
        self.x = x
        self.y = y
        self.g_cost = g_cost  # Cost from start
        self.h_cost = h_cost  # Heuristic cost to goal
        self.f_cost = g_cost + h_cost  # Total cost
        self.parent = parent

    def __lt__(self, other):
        return self.f_cost < other.f_cost

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))


class PathfindingSystem(System):
    """A* pathfinding system"""

    def __init__(self):
        super().__init__()
        self.priority = -40

        # Cached navmesh for performance
        self.navmesh_entity: Optional[Entity] = None
        self.navmesh: Optional[Navmesh] = None

    def update(self, world: World, delta_time: float):
        """Update pathfinding (cache navmesh)"""
        # Cache navmesh entity
        if not self.navmesh_entity:
            navmesh_entities = world.get_entities_with_component(Navmesh)
            if navmesh_entities:
                self.navmesh_entity = navmesh_entities[0]
                self.navmesh = self.navmesh_entity.get_component(Navmesh)

    def find_path(self, start_x: int, start_y: int, goal_x: int, goal_y: int,
                  navmesh: Optional[Navmesh] = None) -> Optional[List[Tuple[int, int]]]:
        """
        Find path from start to goal using A* algorithm.

        Returns:
            List of (x, y) tuples representing the path, or None if no path found
        """
        # Use provided navmesh or cached one
        if navmesh is None:
            navmesh = self.navmesh

        if navmesh is None:
            return None

        # Check if start and goal are walkable
        if not navmesh.is_walkable(start_x, start_y):
            return None
        if not navmesh.is_walkable(goal_x, goal_y):
            return None

        # Initialize
        start_node = PathNode(start_x, start_y, 0, self._heuristic(start_x, start_y, goal_x, goal_y))
        open_set = [start_node]
        closed_set: Set[Tuple[int, int]] = set()
        open_dict = {(start_x, start_y): start_node}

        while open_set:
            # Get node with lowest f_cost
            current = heapq.heappop(open_set)
            current_pos = (current.x, current.y)

            # Remove from open dict
            if current_pos in open_dict:
                del open_dict[current_pos]

            # Check if we reached the goal
            if current.x == goal_x and current.y == goal_y:
                return self._reconstruct_path(current)

            closed_set.add(current_pos)

            # Check neighbors
            for neighbor_x, neighbor_y in self._get_neighbors(current.x, current.y):
                neighbor_pos = (neighbor_x, neighbor_y)

                # Skip if not walkable or already evaluated
                if not navmesh.is_walkable(neighbor_x, neighbor_y):
                    continue
                if neighbor_pos in closed_set:
                    continue

                # Calculate costs
                move_cost = navmesh.get_cost(neighbor_x, neighbor_y)
                g_cost = current.g_cost + move_cost
                h_cost = self._heuristic(neighbor_x, neighbor_y, goal_x, goal_y)

                # Check if this path to neighbor is better
                if neighbor_pos in open_dict:
                    neighbor_node = open_dict[neighbor_pos]
                    if g_cost < neighbor_node.g_cost:
                        # Update the node
                        neighbor_node.g_cost = g_cost
                        neighbor_node.f_cost = g_cost + h_cost
                        neighbor_node.parent = current
                        heapq.heapify(open_set)  # Re-heapify after update
                else:
                    # Add new node to open set
                    neighbor_node = PathNode(neighbor_x, neighbor_y, g_cost, h_cost, current)
                    heapq.heappush(open_set, neighbor_node)
                    open_dict[neighbor_pos] = neighbor_node

        # No path found
        return None

    def _heuristic(self, x1: int, y1: int, x2: int, y2: int) -> float:
        """Calculate heuristic (Manhattan distance)"""
        return abs(x2 - x1) + abs(y2 - y1)

    def _get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get neighboring grid positions (4-directional)"""
        return [
            (x, y - 1),  # North
            (x + 1, y),  # East
            (x, y + 1),  # South
            (x - 1, y),  # West
        ]

    def _reconstruct_path(self, node: PathNode) -> List[Tuple[int, int]]:
        """Reconstruct path from goal node to start"""
        path = []
        current = node

        while current:
            path.append((current.x, current.y))
            current = current.parent

        path.reverse()
        return path

    def get_path_cost(self, path: List[Tuple[int, int]], navmesh: Navmesh) -> float:
        """Calculate total cost of a path"""
        if not path:
            return 0.0

        total_cost = 0.0
        for x, y in path:
            total_cost += navmesh.get_cost(x, y)

        return total_cost

    def is_line_of_sight(self, x1: int, y1: int, x2: int, y2: int,
                         navmesh: Navmesh) -> bool:
        """Check if there's a clear line of sight between two points"""
        # Bresenham's line algorithm
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        x, y = x1, y1

        while True:
            if not navmesh.is_walkable(x, y):
                return False

            if x == x2 and y == y2:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

        return True

    def smooth_path(self, path: List[Tuple[int, int]], navmesh: Navmesh) -> List[Tuple[int, int]]:
        """Smooth path by removing unnecessary waypoints"""
        if len(path) <= 2:
            return path

        smoothed = [path[0]]
        current_index = 0

        while current_index < len(path) - 1:
            # Look ahead to find the farthest point with line of sight
            farthest_index = current_index + 1

            for i in range(current_index + 2, len(path)):
                x1, y1 = path[current_index]
                x2, y2 = path[i]

                if self.is_line_of_sight(x1, y1, x2, y2, navmesh):
                    farthest_index = i
                else:
                    break

            smoothed.append(path[farthest_index])
            current_index = farthest_index

        return smoothed

    def get_movement_range(self, start_x: int, start_y: int, movement_points: int,
                          navmesh: Navmesh) -> Set[Tuple[int, int]]:
        """Get all reachable positions within movement range"""
        reachable = set()
        open_set = [(start_x, start_y, 0)]  # (x, y, cost)
        visited = {(start_x, start_y)}

        while open_set:
            x, y, cost = open_set.pop(0)
            reachable.add((x, y))

            # Check neighbors
            for nx, ny in self._get_neighbors(x, y):
                if (nx, ny) in visited:
                    continue
                if not navmesh.is_walkable(nx, ny):
                    continue

                move_cost = navmesh.get_cost(nx, ny)
                new_cost = cost + move_cost

                if new_cost <= movement_points:
                    open_set.append((nx, ny, new_cost))
                    visited.add((nx, ny))

        return reachable
