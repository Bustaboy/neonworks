"""
AI-Assisted Navmesh Generation

Intelligent navmesh generation with automatic obstacle detection,
terrain analysis, and smart walkability determination.
"""

from typing import Set, Tuple, List, Dict, Optional
from dataclasses import dataclass
from neonworks.core.ecs import World, Entity, GridPosition, Building, Navmesh


@dataclass
class NavmeshConfig:
    """Configuration for navmesh generation"""
    # Obstacle detection
    detect_buildings: bool = True
    detect_terrain: bool = True
    detect_props: bool = True

    # Terrain costs
    terrain_cost_multipliers: Dict[str, float] = None

    # AI-assisted features
    auto_detect_chokepoints: bool = True
    auto_detect_cover: bool = True
    prefer_corridors: bool = True
    avoid_edges: bool = False

    # Smart expansion
    expand_walkable_areas: bool = True
    expansion_passes: int = 2

    def __post_init__(self):
        if self.terrain_cost_multipliers is None:
            self.terrain_cost_multipliers = {
                "floor": 1.0,
                "grass": 1.0,
                "road": 0.8,  # Faster movement
                "rough": 1.5,  # Slower movement
                "mud": 2.0,    # Much slower
                "water": 999.0  # Effectively impassable
            }


class AINavmeshGenerator:
    """
    AI-assisted navmesh generation with intelligent obstacle detection
    and terrain analysis.
    """

    def __init__(self, config: Optional[NavmeshConfig] = None):
        self.config = config or NavmeshConfig()

    def generate(self, world: World, grid_width: int, grid_height: int) -> Navmesh:
        """
        Generate navmesh with AI assistance.

        The AI will:
        1. Automatically detect obstacles (buildings, terrain, props)
        2. Analyze terrain for movement costs
        3. Detect tactical positions (cover, chokepoints)
        4. Optimize walkable areas for smooth pathfinding
        """
        navmesh = Navmesh()

        # Step 1: Initialize all cells as walkable
        print("🤖 AI: Initializing navmesh grid...")
        for y in range(grid_height):
            for x in range(grid_width):
                navmesh.walkable_cells.add((x, y))
                navmesh.cost_multipliers[(x, y)] = 1.0

        # Step 2: AI-assisted obstacle detection
        print("🤖 AI: Detecting obstacles intelligently...")
        self._detect_obstacles(world, navmesh)

        # Step 3: AI-assisted terrain analysis
        print("🤖 AI: Analyzing terrain for movement costs...")
        self._analyze_terrain(world, navmesh, grid_width, grid_height)

        # Step 4: Smart expansion of walkable areas
        if self.config.expand_walkable_areas:
            print("🤖 AI: Intelligently expanding walkable areas...")
            self._smart_expansion(navmesh, grid_width, grid_height)

        # Step 5: Detect tactical positions
        if self.config.auto_detect_chokepoints:
            print("🤖 AI: Detecting chokepoints for tactical gameplay...")
            chokepoints = self._detect_chokepoints(navmesh, grid_width, grid_height)
            print(f"   Found {len(chokepoints)} chokepoints")

        if self.config.auto_detect_cover:
            print("🤖 AI: Detecting cover positions...")
            cover_positions = self._detect_cover(world, navmesh)
            print(f"   Found {len(cover_positions)} cover positions")

        # Step 6: Optimize for corridors
        if self.config.prefer_corridors:
            print("🤖 AI: Optimizing movement through corridors...")
            self._optimize_corridors(navmesh, grid_width, grid_height)

        walkable_count = len(navmesh.walkable_cells)
        total_cells = grid_width * grid_height
        walkable_percent = (walkable_count / total_cells) * 100

        print(f"✅ Navmesh generated: {walkable_count}/{total_cells} cells walkable ({walkable_percent:.1f}%)")

        return navmesh

    def _detect_obstacles(self, world: World, navmesh: Navmesh):
        """AI-assisted obstacle detection"""
        if self.config.detect_buildings:
            buildings = world.get_entities_with_component(Building)

            for entity in buildings:
                grid_pos = entity.get_component(GridPosition)
                if grid_pos:
                    # Mark building position as unwalkable
                    pos = (grid_pos.grid_x, grid_pos.grid_y)
                    if pos in navmesh.walkable_cells:
                        navmesh.walkable_cells.remove(pos)

                    # TODO: Handle multi-tile buildings based on building size

    def _analyze_terrain(self, world: World, navmesh: Navmesh,
                        grid_width: int, grid_height: int):
        """AI-assisted terrain analysis for movement costs"""
        # In a real implementation, this would analyze tile types
        # For now, we'll use a simple pattern-based approach

        for y in range(grid_height):
            for x in range(grid_width):
                pos = (x, y)
                if pos not in navmesh.walkable_cells:
                    continue

                # AI heuristic: edges are slightly more costly
                if self.config.avoid_edges:
                    edge_distance = min(x, y, grid_width - 1 - x, grid_height - 1 - y)
                    if edge_distance < 3:
                        edge_penalty = 1.0 + (3 - edge_distance) * 0.2
                        navmesh.cost_multipliers[pos] *= edge_penalty

    def _smart_expansion(self, navmesh: Navmesh, grid_width: int, grid_height: int):
        """
        Smart expansion of walkable areas using AI.

        This fills in small gaps and smooths out irregular boundaries.
        """
        for _ in range(self.config.expansion_passes):
            to_add = set()

            for y in range(grid_height):
                for x in range(grid_width):
                    pos = (x, y)

                    if pos in navmesh.walkable_cells:
                        continue

                    # Count walkable neighbors
                    walkable_neighbors = 0
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        nx, ny = x + dx, y + dy
                        if (nx, ny) in navmesh.walkable_cells:
                            walkable_neighbors += 1

                    # If surrounded by walkable cells, make this walkable too
                    if walkable_neighbors >= 3:
                        to_add.add(pos)

            # Add new walkable cells
            for pos in to_add:
                navmesh.walkable_cells.add(pos)
                navmesh.cost_multipliers[pos] = 1.0

    def _detect_chokepoints(self, navmesh: Navmesh,
                           grid_width: int, grid_height: int) -> Set[Tuple[int, int]]:
        """
        AI detection of chokepoints (narrow passages).

        Chokepoints are tactically important positions that control movement.
        """
        chokepoints = set()

        for y in range(1, grid_height - 1):
            for x in range(1, grid_width - 1):
                pos = (x, y)

                if pos not in navmesh.walkable_cells:
                    continue

                # Check if this is a narrow passage
                # Count walkable cells in a 3x3 area
                walkable_in_area = 0
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        check_pos = (x + dx, y + dy)
                        if check_pos in navmesh.walkable_cells:
                            walkable_in_area += 1

                # If only a few cells are walkable, this is a chokepoint
                if 3 <= walkable_in_area <= 5:
                    chokepoints.add(pos)
                    # Slightly increase cost for chokepoints (tactical consideration)
                    navmesh.cost_multipliers[pos] *= 1.1

        return chokepoints

    def _detect_cover(self, world: World, navmesh: Navmesh) -> Set[Tuple[int, int]]:
        """
        AI detection of cover positions (cells adjacent to obstacles).

        Cover positions are tactically valuable for combat.
        """
        cover_positions = set()

        buildings = world.get_entities_with_component(Building)

        for entity in buildings:
            grid_pos = entity.get_component(GridPosition)
            if not grid_pos:
                continue

            bx, by = grid_pos.grid_x, grid_pos.grid_y

            # Check adjacent cells
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0),
                          (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                cover_pos = (bx + dx, by + dy)

                if cover_pos in navmesh.walkable_cells:
                    cover_positions.add(cover_pos)
                    # Slightly reduce cost for cover positions (desirable)
                    navmesh.cost_multipliers[cover_pos] *= 0.9

        return cover_positions

    def _optimize_corridors(self, navmesh: Navmesh, grid_width: int, grid_height: int):
        """
        AI optimization for movement through corridors.

        Makes movement along clear corridors faster.
        """
        for y in range(1, grid_height - 1):
            for x in range(1, grid_width - 1):
                pos = (x, y)

                if pos not in navmesh.walkable_cells:
                    continue

                # Check if this is part of a corridor (straight line)
                # Horizontal corridor
                left = (x - 1, y) in navmesh.walkable_cells
                right = (x + 1, y) in navmesh.walkable_cells
                up = (x, y - 1) not in navmesh.walkable_cells
                down = (x, y + 1) not in navmesh.walkable_cells

                h_corridor = left and right and up and down

                # Vertical corridor
                up_w = (x, y - 1) in navmesh.walkable_cells
                down_w = (x, y + 1) in navmesh.walkable_cells
                left_w = (x - 1, y) not in navmesh.walkable_cells
                right_w = (x + 1, y) not in navmesh.walkable_cells

                v_corridor = up_w and down_w and left_w and right_w

                # Reduce cost for corridors
                if h_corridor or v_corridor:
                    navmesh.cost_multipliers[pos] *= 0.85

    def visualize_navmesh(self, navmesh: Navmesh, grid_width: int, grid_height: int) -> str:
        """
        Generate ASCII visualization of navmesh for debugging.
        """
        lines = []
        lines.append("Navmesh Visualization:")
        lines.append("━" * (grid_width + 2))

        for y in range(grid_height):
            line = "┃"
            for x in range(grid_width):
                pos = (x, y)
                if pos not in navmesh.walkable_cells:
                    line += "█"  # Obstacle
                else:
                    cost = navmesh.cost_multipliers.get(pos, 1.0)
                    if cost < 0.9:
                        line += "+"  # Preferred (cover, corridor)
                    elif cost > 1.1:
                        line += "-"  # Avoided (chokepoint, rough terrain)
                    else:
                        line += " "  # Normal
            line += "┃"
            lines.append(line)

        lines.append("━" * (grid_width + 2))
        lines.append("Legend: █=Obstacle  =Walkable  +=Preferred  -=Costly")

        return "\n".join(lines)

    def export_stats(self, navmesh: Navmesh, grid_width: int, grid_height: int) -> Dict[str, any]:
        """Export navmesh statistics"""
        total_cells = grid_width * grid_height
        walkable_cells = len(navmesh.walkable_cells)
        obstacle_cells = total_cells - walkable_cells

        # Analyze cost distribution
        low_cost = sum(1 for cost in navmesh.cost_multipliers.values() if cost < 0.9)
        normal_cost = sum(1 for cost in navmesh.cost_multipliers.values() if 0.9 <= cost <= 1.1)
        high_cost = sum(1 for cost in navmesh.cost_multipliers.values() if cost > 1.1)

        return {
            "total_cells": total_cells,
            "walkable_cells": walkable_cells,
            "obstacle_cells": obstacle_cells,
            "walkable_percentage": (walkable_cells / total_cells) * 100,
            "cost_distribution": {
                "low_cost": low_cost,
                "normal_cost": normal_cost,
                "high_cost": high_cost
            }
        }
