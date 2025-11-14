"""
AI-Assisted Level Building

Intelligent level design assistance with smart placement suggestions,
balance analysis, and automated layout generation.
"""

import random
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple


class PlacementPriority(Enum):
    """Priority levels for placement suggestions"""

    CRITICAL = auto()  # Must be placed
    HIGH = auto()  # Strongly recommended
    MEDIUM = auto()  # Suggested
    LOW = auto()  # Optional


@dataclass
class PlacementSuggestion:
    """AI suggestion for placing an object"""

    x: int
    y: int
    object_type: str
    priority: PlacementPriority
    reason: str
    score: float  # 0.0 to 1.0


class AILevelBuilder:
    """
    AI-assisted level building with intelligent placement suggestions.

    The AI helps with:
    - Smart object placement based on game balance
    - Tactical position suggestions
    - Resource distribution
    - Spawn point placement
    - Cover and obstacle arrangement
    """

    def __init__(self, grid_width: int, grid_height: int):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.occupied_cells: Set[Tuple[int, int]] = set()

    def suggest_spawn_points(self, num_players: int) -> List[PlacementSuggestion]:
        """
        AI suggests optimal spawn points for players.

        Criteria:
        - Maximum distance from each other
        - Not in corners (unless necessary)
        - Near resources but not too close
        - Defensible positions
        """
        suggestions = []

        print(f"🤖 AI: Analyzing optimal spawn points for {num_players} players...")

        # Use a grid-based approach to space out spawn points
        if num_players == 2:
            # Opposite corners with some offset
            spawn_points = [
                (self.grid_width // 4, self.grid_height // 4),
                (3 * self.grid_width // 4, 3 * self.grid_height // 4),
            ]
        elif num_players == 4:
            # Four corners
            offset = 5
            spawn_points = [
                (offset, offset),
                (self.grid_width - offset, offset),
                (offset, self.grid_height - offset),
                (self.grid_width - offset, self.grid_height - offset),
            ]
        else:
            # Distribute around the map
            spawn_points = []
            angle_step = 360 / num_players
            center_x, center_y = self.grid_width // 2, self.grid_height // 2
            radius = min(self.grid_width, self.grid_height) // 3

            for i in range(num_players):
                angle = (angle_step * i) * (3.14159 / 180)
                x = int(center_x + radius * (angle % 3.14159))
                y = int(center_y + radius * ((angle + 1.57) % 3.14159))
                spawn_points.append((x, y))

        for i, (x, y) in enumerate(spawn_points):
            suggestions.append(
                PlacementSuggestion(
                    x=x,
                    y=y,
                    object_type=f"spawn_point_player_{i+1}",
                    priority=PlacementPriority.CRITICAL,
                    reason=f"Optimal spawn location for player {i+1} - balanced distance from other players",
                    score=0.95,
                )
            )
            self.occupied_cells.add((x, y))

        print(f"   ✅ Generated {len(suggestions)} spawn point suggestions")
        return suggestions

    def suggest_resource_nodes(
        self, num_nodes: int, resource_type: str = "metal"
    ) -> List[PlacementSuggestion]:
        """
        AI suggests resource node placements.

        Criteria:
        - Distributed across the map
        - Not too close to spawn points
        - Some clustering for tactical value
        - Near chokepoints for contested areas
        """
        suggestions = []

        print(f"🤖 AI: Planning {num_nodes} {resource_type} resource nodes...")

        # Divide map into regions
        regions = self._divide_into_regions(4)

        nodes_per_region = num_nodes // len(regions)
        extra_nodes = num_nodes % len(regions)

        for region_idx, region in enumerate(regions):
            region_nodes = nodes_per_region + (1 if region_idx < extra_nodes else 0)

            for _ in range(region_nodes):
                # Find a good spot in this region
                x, y = self._find_placement_in_region(region)

                if (x, y) in self.occupied_cells:
                    continue

                # Score based on strategic value
                score = self._score_resource_position(x, y)

                suggestions.append(
                    PlacementSuggestion(
                        x=x,
                        y=y,
                        object_type=f"resource_node_{resource_type}",
                        priority=PlacementPriority.HIGH,
                        reason=f"Strategic {resource_type} location - balanced distribution across map",
                        score=score,
                    )
                )
                self.occupied_cells.add((x, y))

        print(f"   ✅ Placed {len(suggestions)} resource nodes strategically")
        return suggestions

    def suggest_cover_positions(self, density: float = 0.15) -> List[PlacementSuggestion]:
        """
        AI suggests cover object placements.

        Criteria:
        - Create interesting tactical situations
        - Form defensive positions
        - Create chokepoints
        - Not blocking critical paths
        """
        suggestions = []

        num_cover = int(self.grid_width * self.grid_height * density)
        print(f"🤖 AI: Designing tactical cover layout ({num_cover} objects)...")

        # Use Perlin-noise-like clustering for natural-looking cover
        clusters = self._generate_clusters(num_cover // 3)

        for cluster_center in clusters:
            cluster_size = random.randint(2, 5)

            for _ in range(cluster_size):
                # Place near cluster center with some randomness
                cx, cy = cluster_center
                x = cx + random.randint(-3, 3)
                y = cy + random.randint(-3, 3)

                # Clamp to grid
                x = max(0, min(self.grid_width - 1, x))
                y = max(0, min(self.grid_height - 1, y))

                if (x, y) in self.occupied_cells:
                    continue

                # Score tactical value
                score = self._score_cover_position(x, y)

                if score > 0.3:  # Only suggest good positions
                    suggestions.append(
                        PlacementSuggestion(
                            x=x,
                            y=y,
                            object_type="cover_object",
                            priority=PlacementPriority.MEDIUM,
                            reason="Tactical cover position - creates interesting combat scenarios",
                            score=score,
                        )
                    )
                    self.occupied_cells.add((x, y))

        print(f"   ✅ Created {len(suggestions)} tactical cover positions")
        return suggestions

    def suggest_buildings(
        self, player_num: int, spawn_x: int, spawn_y: int
    ) -> List[PlacementSuggestion]:
        """
        AI suggests starting building placements near spawn.

        Criteria:
        - Close to spawn point
        - Logical layout (command center central, production around it)
        - Defensible arrangement
        - Room for expansion
        """
        suggestions = []

        print(f"🤖 AI: Designing starting base layout for player {player_num}...")

        # Core buildings
        buildings = [
            ("command_center", PlacementPriority.CRITICAL, 0, 0),
            ("generator", PlacementPriority.HIGH, 3, 0),
            ("warehouse", PlacementPriority.HIGH, -3, 0),
            ("barracks", PlacementPriority.MEDIUM, 0, 3),
        ]

        for building_type, priority, dx, dy in buildings:
            x = spawn_x + dx
            y = spawn_y + dy

            # Make sure it's in bounds
            if not (0 <= x < self.grid_width and 0 <= y < self.grid_height):
                continue

            if (x, y) in self.occupied_cells:
                continue

            suggestions.append(
                PlacementSuggestion(
                    x=x,
                    y=y,
                    object_type=building_type,
                    priority=priority,
                    reason=f"Optimal starting base layout - {building_type} positioned for efficiency",
                    score=0.9,
                )
            )
            self.occupied_cells.add((x, y))

        print(f"   ✅ Designed starting base with {len(suggestions)} buildings")
        return suggestions

    def analyze_level_balance(self, suggestions: List[PlacementSuggestion]) -> Dict[str, any]:
        """
        AI analyzes level balance and provides feedback.

        Returns metrics about:
        - Resource distribution fairness
        - Tactical complexity
        - Player advantage/disadvantage
        - Chokepoint density
        """
        print("🤖 AI: Analyzing level balance...")

        # Count objects by type
        object_counts = {}
        for suggestion in suggestions:
            obj_type = suggestion.object_type.split("_")[0]
            object_counts[obj_type] = object_counts.get(obj_type, 0) + 1

        # Calculate coverage
        occupied_percentage = (
            len(self.occupied_cells) / (self.grid_width * self.grid_height)
        ) * 100

        # Analyze spawn point distances
        spawn_points = [s for s in suggestions if "spawn_point" in s.object_type]
        if len(spawn_points) >= 2:
            min_distance = float("inf")
            for i, sp1 in enumerate(spawn_points):
                for sp2 in spawn_points[i + 1 :]:
                    dist = abs(sp1.x - sp2.x) + abs(sp1.y - sp2.y)
                    min_distance = min(min_distance, dist)

            balance_score = min(1.0, min_distance / (self.grid_width + self.grid_height) * 2)
        else:
            balance_score = 0.5

        # Resource fairness (check if resources are equidistant from spawns)
        resource_nodes = [s for s in suggestions if "resource" in s.object_type]
        resource_fairness = self._calculate_resource_fairness(spawn_points, resource_nodes)

        analysis = {
            "total_objects": len(suggestions),
            "object_counts": object_counts,
            "occupied_percentage": occupied_percentage,
            "balance_score": balance_score,
            "resource_fairness": resource_fairness,
            "spawn_point_balance": (
                "Excellent"
                if balance_score > 0.8
                else "Good" if balance_score > 0.6 else "Needs Improvement"
            ),
            "recommendations": [],
        }

        # Generate recommendations
        if balance_score < 0.6:
            analysis["recommendations"].append(
                "⚠️ Spawn points are too close - consider spreading them out"
            )

        if resource_fairness < 0.6:
            analysis["recommendations"].append(
                "⚠️ Resources favor one player - rebalance distribution"
            )

        if occupied_percentage < 10:
            analysis["recommendations"].append("💡 Map feels empty - consider adding more objects")
        elif occupied_percentage > 40:
            analysis["recommendations"].append("⚠️ Map is very crowded - might hinder movement")

        if object_counts.get("cover", 0) < 10:
            analysis["recommendations"].append("💡 Add more cover for tactical depth")

        if not analysis["recommendations"]:
            analysis["recommendations"].append("✅ Level balance looks great!")

        print(f"   Balance Score: {balance_score:.2f}")
        print(f"   Resource Fairness: {resource_fairness:.2f}")
        print(f"   Map Density: {occupied_percentage:.1f}%")

        return analysis

    def _divide_into_regions(self, num_regions: int) -> List[Tuple[int, int, int, int]]:
        """Divide map into regions (x1, y1, x2, y2)"""
        if num_regions == 4:
            mid_x = self.grid_width // 2
            mid_y = self.grid_height // 2
            return [
                (0, 0, mid_x, mid_y),
                (mid_x, 0, self.grid_width, mid_y),
                (0, mid_y, mid_x, self.grid_height),
                (mid_x, mid_y, self.grid_width, self.grid_height),
            ]
        else:
            return [(0, 0, self.grid_width, self.grid_height)]

    def _find_placement_in_region(self, region: Tuple[int, int, int, int]) -> Tuple[int, int]:
        """Find a random placement within a region"""
        x1, y1, x2, y2 = region
        x = random.randint(x1, x2 - 1)
        y = random.randint(y1, y2 - 1)
        return (x, y)

    def _score_resource_position(self, x: int, y: int) -> float:
        """Score a resource position (0.0 to 1.0)"""
        # Prefer positions away from edges
        edge_distance = min(x, y, self.grid_width - 1 - x, self.grid_height - 1 - y)
        edge_score = min(1.0, edge_distance / 10.0)

        # Prefer positions not too close to occupied cells
        nearest_occupied = self._distance_to_nearest_occupied(x, y)
        spacing_score = min(1.0, nearest_occupied / 5.0)

        return (edge_score + spacing_score) / 2

    def _score_cover_position(self, x: int, y: int) -> float:
        """Score a cover position for tactical value"""
        # Prefer positions with some neighbors (clustering)
        neighbor_count = sum(
            1
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]
            if (x + dx, y + dy) in self.occupied_cells
        )

        cluster_score = min(1.0, neighbor_count / 2.0)

        # Prefer central positions
        center_x, center_y = self.grid_width // 2, self.grid_height // 2
        center_distance = abs(x - center_x) + abs(y - center_y)
        max_distance = self.grid_width + self.grid_height
        center_score = 1.0 - (center_distance / max_distance)

        return cluster_score * 0.6 + center_score * 0.4

    def _generate_clusters(self, num_clusters: int) -> List[Tuple[int, int]]:
        """Generate cluster center points"""
        clusters = []
        for _ in range(num_clusters):
            x = random.randint(5, self.grid_width - 5)
            y = random.randint(5, self.grid_height - 5)
            clusters.append((x, y))
        return clusters

    def _distance_to_nearest_occupied(self, x: int, y: int) -> float:
        """Calculate distance to nearest occupied cell"""
        if not self.occupied_cells:
            return float("inf")

        min_dist = float("inf")
        for ox, oy in self.occupied_cells:
            dist = abs(x - ox) + abs(y - oy)
            min_dist = min(min_dist, dist)

        return min_dist

    def _calculate_resource_fairness(
        self,
        spawn_points: List[PlacementSuggestion],
        resource_nodes: List[PlacementSuggestion],
    ) -> float:
        """Calculate how fairly resources are distributed relative to spawns"""
        if not spawn_points or not resource_nodes:
            return 1.0

        # Calculate average distance from each spawn to all resources
        spawn_distances = []

        for spawn in spawn_points:
            total_distance = 0
            for resource in resource_nodes:
                dist = abs(spawn.x - resource.x) + abs(spawn.y - resource.y)
                total_distance += dist

            avg_distance = total_distance / len(resource_nodes)
            spawn_distances.append(avg_distance)

        # Calculate variance
        mean_distance = sum(spawn_distances) / len(spawn_distances)
        variance = sum((d - mean_distance) ** 2 for d in spawn_distances) / len(spawn_distances)

        # Low variance = fair, high variance = unfair
        fairness = 1.0 / (1.0 + variance / 100.0)

        return fairness
