"""
Procedural Generation System

AI-assisted procedural generation for levels, terrain, and content.
Helps rapidly create diverse game content with intelligent variation.
"""

import math
import random
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple


class TerrainType(Enum):
    """Terrain types for procedural generation"""

    FLOOR = auto()
    WALL = auto()
    ROUGH = auto()
    WATER = auto()
    COVER = auto()
    OBSTACLE = auto()


@dataclass
class GenerationConfig:
    """Configuration for procedural generation"""

    # Map size
    width: int = 50
    height: int = 50

    # Room generation (for interior maps)
    min_rooms: int = 3
    max_rooms: int = 8
    min_room_size: int = 4
    max_room_size: int = 10

    # Open area generation (for exterior maps)
    open_area_density: float = 0.7  # 70% walkable

    # Obstacle generation
    obstacle_density: float = 0.15
    obstacle_clustering: float = 0.6  # How much obstacles cluster

    # Feature generation
    add_cover: bool = True
    add_resources: bool = True
    add_chokepoints: bool = True

    # Symmetry (for competitive maps)
    symmetrical: bool = False
    symmetry_type: str = "horizontal"  # horizontal, vertical, radial


class ProceduralGenerator:
    """
    Procedural generation system with AI assistance.

    Generates:
    - Interior maps with rooms and corridors
    - Exterior maps with natural-looking terrain
    - Tactical features (cover, chokepoints)
    - Resource placement
    - Balanced competitive maps
    """

    def __init__(
        self, config: Optional[GenerationConfig] = None, seed: Optional[int] = None
    ):
        self.config = config or GenerationConfig()

        if seed is not None:
            random.seed(seed)

        self.terrain_grid: List[List[TerrainType]] = []

    def generate_interior_map(self) -> Dict[str, any]:
        """
        Generate an interior map with rooms and corridors.

        Returns map data including terrain, spawn points, and features.
        """
        print("🤖 Procedural Gen: Creating interior map with rooms and corridors...")

        # Initialize grid with walls
        self.terrain_grid = [
            [TerrainType.WALL for _ in range(self.config.width)]
            for _ in range(self.config.height)
        ]

        # Generate rooms
        rooms = self._generate_rooms()
        print(f"   Generated {len(rooms)} rooms")

        # Carve out rooms
        for room in rooms:
            self._carve_room(room)

        # Connect rooms with corridors
        self._connect_rooms(rooms)
        print(f"   Connected rooms with corridors")

        # Add features
        if self.config.add_cover:
            cover_positions = self._add_cover_objects(rooms)
            print(f"   Placed {len(cover_positions)} cover objects")

        if self.config.add_resources:
            resource_positions = self._add_resources(rooms)
            print(f"   Placed {len(resource_positions)} resource nodes")

        # Find spawn points
        spawn_points = self._find_spawn_points(rooms)

        map_data = {
            "terrain": self._terrain_to_string_grid(),
            "spawn_points": spawn_points,
            "rooms": rooms,
            "width": self.config.width,
            "height": self.config.height,
        }

        print("✅ Interior map generated successfully")
        return map_data

    def generate_exterior_map(self) -> Dict[str, any]:
        """
        Generate an exterior map with natural-looking terrain.

        Uses Perlin-noise-like generation for organic layouts.
        """
        print("🤖 Procedural Gen: Creating exterior map with natural terrain...")

        # Initialize grid with floor
        self.terrain_grid = [
            [TerrainType.FLOOR for _ in range(self.config.width)]
            for _ in range(self.config.height)
        ]

        # Generate terrain using noise-like algorithm
        self._generate_natural_terrain()

        # Add obstacles
        if self.config.obstacle_density > 0:
            obstacle_count = self._add_obstacles()
            print(f"   Placed {obstacle_count} obstacles")

        # Add cover
        if self.config.add_cover:
            cover_count = self._add_exterior_cover()
            print(f"   Placed {cover_count} cover objects")

        # Add resources
        if self.config.add_resources:
            resource_positions = self._add_scattered_resources()
            print(f"   Placed {len(resource_positions)} resource nodes")

        # Find spawn points
        spawn_points = self._find_exterior_spawn_points()

        map_data = {
            "terrain": self._terrain_to_string_grid(),
            "spawn_points": spawn_points,
            "width": self.config.width,
            "height": self.config.height,
        }

        print("✅ Exterior map generated successfully")
        return map_data

    def generate_competitive_map(self, num_players: int = 2) -> Dict[str, any]:
        """
        Generate a balanced competitive map with symmetry.

        Ensures fairness for all players through mirrored layout.
        """
        print(
            f"🤖 Procedural Gen: Creating balanced competitive map for {num_players} players..."
        )

        # Generate one half/quadrant
        self.config.width = (
            self.config.width // 2 if self.config.symmetrical else self.config.width
        )
        self.config.height = (
            self.config.height // 2
            if self.config.symmetry_type == "radial"
            else self.config.height
        )

        # Generate base map
        if random.random() > 0.5:
            map_data = self.generate_interior_map()
        else:
            map_data = self.generate_exterior_map()

        # Apply symmetry
        if self.config.symmetrical:
            self._apply_symmetry()

        # Place spawn points symmetrically
        spawn_points = self._place_symmetric_spawns(num_players)
        map_data["spawn_points"] = spawn_points

        print("✅ Competitive map generated with balanced layout")
        return map_data

    def _generate_rooms(self) -> List[Tuple[int, int, int, int]]:
        """Generate random rooms (x, y, width, height)"""
        rooms = []
        num_rooms = random.randint(self.config.min_rooms, self.config.max_rooms)

        attempts = 0
        max_attempts = num_rooms * 10

        while len(rooms) < num_rooms and attempts < max_attempts:
            attempts += 1

            # Random room size
            w = random.randint(self.config.min_room_size, self.config.max_room_size)
            h = random.randint(self.config.min_room_size, self.config.max_room_size)

            # Random position
            x = random.randint(1, self.config.width - w - 1)
            y = random.randint(1, self.config.height - h - 1)

            # Check if room overlaps with existing rooms
            overlaps = False
            for other_x, other_y, other_w, other_h in rooms:
                if (
                    x < other_x + other_w + 2
                    and x + w + 2 > other_x
                    and y < other_y + other_h + 2
                    and y + h + 2 > other_y
                ):
                    overlaps = True
                    break

            if not overlaps:
                rooms.append((x, y, w, h))

        return rooms

    def _carve_room(self, room: Tuple[int, int, int, int]):
        """Carve out a room in the terrain grid"""
        x, y, w, h = room
        for dy in range(h):
            for dx in range(w):
                self.terrain_grid[y + dy][x + dx] = TerrainType.FLOOR

    def _connect_rooms(self, rooms: List[Tuple[int, int, int, int]]):
        """Connect rooms with corridors"""
        for i in range(len(rooms) - 1):
            room1 = rooms[i]
            room2 = rooms[i + 1]

            # Get centers
            x1, y1 = room1[0] + room1[2] // 2, room1[1] + room1[3] // 2
            x2, y2 = room2[0] + room2[2] // 2, room2[1] + room2[3] // 2

            # Create L-shaped corridor
            if random.random() > 0.5:
                self._carve_h_tunnel(x1, x2, y1)
                self._carve_v_tunnel(y1, y2, x2)
            else:
                self._carve_v_tunnel(y1, y2, x1)
                self._carve_h_tunnel(x1, x2, y2)

    def _carve_h_tunnel(self, x1: int, x2: int, y: int):
        """Carve horizontal tunnel"""
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if 0 <= x < self.config.width and 0 <= y < self.config.height:
                self.terrain_grid[y][x] = TerrainType.FLOOR

    def _carve_v_tunnel(self, y1: int, y2: int, x: int):
        """Carve vertical tunnel"""
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if 0 <= x < self.config.width and 0 <= y < self.config.height:
                self.terrain_grid[y][x] = TerrainType.FLOOR

    def _generate_natural_terrain(self):
        """Generate natural-looking terrain using noise"""
        # Simple noise-like generation
        for y in range(self.config.height):
            for x in range(self.config.width):
                # Calculate noise value
                noise = self._simple_noise(x / 10.0, y / 10.0)

                # Apply threshold for different terrain types
                if noise < -0.3:
                    self.terrain_grid[y][x] = TerrainType.WATER
                elif noise < 0.0:
                    self.terrain_grid[y][x] = TerrainType.ROUGH
                else:
                    self.terrain_grid[y][x] = TerrainType.FLOOR

    def _simple_noise(self, x: float, y: float) -> float:
        """Simple noise function (simplified Perlin-like)"""
        # Use sin/cos for pseudo-random but smooth values
        n = math.sin(x * 1.5) * math.cos(y * 1.5)
        n += 0.5 * math.sin(x * 3.0) * math.cos(y * 3.0)
        n += 0.25 * math.sin(x * 6.0) * math.cos(y * 6.0)
        return n / 1.75

    def _add_obstacles(self) -> int:
        """Add obstacles to exterior map"""
        count = 0
        total_cells = self.config.width * self.config.height
        target_obstacles = int(total_cells * self.config.obstacle_density)

        # Place obstacle clusters
        num_clusters = max(1, target_obstacles // 5)

        for _ in range(num_clusters):
            # Pick cluster center
            cx = random.randint(0, self.config.width - 1)
            cy = random.randint(0, self.config.height - 1)

            # Place obstacles around center
            cluster_size = random.randint(3, 8)
            for _ in range(cluster_size):
                x = cx + random.randint(-2, 2)
                y = cy + random.randint(-2, 2)

                if (
                    0 <= x < self.config.width
                    and 0 <= y < self.config.height
                    and self.terrain_grid[y][x] == TerrainType.FLOOR
                ):
                    self.terrain_grid[y][x] = TerrainType.OBSTACLE
                    count += 1

        return count

    def _add_cover_objects(
        self, rooms: List[Tuple[int, int, int, int]]
    ) -> List[Tuple[int, int]]:
        """Add cover objects to interior map"""
        cover_positions = []

        for room in rooms:
            x, y, w, h = room
            # Add 1-3 cover objects per room
            num_cover = random.randint(1, 3)

            for _ in range(num_cover):
                cx = x + random.randint(1, w - 2)
                cy = y + random.randint(1, h - 2)

                if self.terrain_grid[cy][cx] == TerrainType.FLOOR:
                    self.terrain_grid[cy][cx] = TerrainType.COVER
                    cover_positions.append((cx, cy))

        return cover_positions

    def _add_exterior_cover(self) -> int:
        """Add cover to exterior map"""
        count = 0
        for y in range(self.config.height):
            for x in range(self.config.width):
                if self.terrain_grid[y][x] == TerrainType.FLOOR:
                    if random.random() < 0.1:  # 10% chance
                        self.terrain_grid[y][x] = TerrainType.COVER
                        count += 1
        return count

    def _add_resources(
        self, rooms: List[Tuple[int, int, int, int]]
    ) -> List[Tuple[int, int]]:
        """Add resources to rooms"""
        resource_positions = []

        for room in rooms:
            if random.random() > 0.3:  # 70% of rooms have resources
                x, y, w, h = room
                rx = x + w // 2
                ry = y + h // 2
                resource_positions.append((rx, ry))

        return resource_positions

    def _add_scattered_resources(self) -> List[Tuple[int, int]]:
        """Add scattered resources to exterior map"""
        resource_positions = []
        num_resources = random.randint(5, 15)

        for _ in range(num_resources):
            x = random.randint(0, self.config.width - 1)
            y = random.randint(0, self.config.height - 1)

            if self.terrain_grid[y][x] == TerrainType.FLOOR:
                resource_positions.append((x, y))

        return resource_positions

    def _find_spawn_points(
        self, rooms: List[Tuple[int, int, int, int]]
    ) -> List[Tuple[int, int]]:
        """Find spawn points in rooms"""
        if len(rooms) < 2:
            return []

        # Use first and last room
        room1 = rooms[0]
        room2 = rooms[-1]

        spawn1 = (room1[0] + room1[2] // 2, room1[1] + room1[3] // 2)
        spawn2 = (room2[0] + room2[2] // 2, room2[1] + room2[3] // 2)

        return [spawn1, spawn2]

    def _find_exterior_spawn_points(self) -> List[Tuple[int, int]]:
        """Find spawn points for exterior map"""
        # Opposite corners
        spawn_points = []

        # Find floor tiles near corners
        for x, y in [(5, 5), (self.config.width - 5, self.config.height - 5)]:
            # Find nearest floor tile
            for dy in range(-5, 6):
                for dx in range(-5, 6):
                    check_x, check_y = x + dx, y + dy
                    if (
                        0 <= check_x < self.config.width
                        and 0 <= check_y < self.config.height
                        and self.terrain_grid[check_y][check_x] == TerrainType.FLOOR
                    ):
                        spawn_points.append((check_x, check_y))
                        break
                if len(spawn_points) > len(spawn_points) - 1:
                    break

        return spawn_points

    def _apply_symmetry(self):
        """Apply symmetry to the terrain grid"""
        if self.config.symmetry_type == "horizontal":
            # Mirror horizontally
            for y in range(self.config.height):
                for x in range(self.config.width):
                    mirror_x = self.config.width - 1 - x
                    if mirror_x >= self.config.width // 2:
                        self.terrain_grid[y][mirror_x] = self.terrain_grid[y][x]

    def _place_symmetric_spawns(self, num_players: int) -> List[Tuple[int, int]]:
        """Place spawn points symmetrically"""
        if num_players == 2:
            return [(5, 5), (self.config.width - 5, self.config.height - 5)]
        elif num_players == 4:
            return [
                (5, 5),
                (self.config.width - 5, 5),
                (5, self.config.height - 5),
                (self.config.width - 5, self.config.height - 5),
            ]
        return []

    def _terrain_to_string_grid(self) -> List[List[str]]:
        """Convert terrain grid to string representation"""
        terrain_map = {
            TerrainType.FLOOR: ".",
            TerrainType.WALL: "#",
            TerrainType.ROUGH: "~",
            TerrainType.WATER: "≈",
            TerrainType.COVER: "C",
            TerrainType.OBSTACLE: "X",
        }

        return [[terrain_map[cell] for cell in row] for row in self.terrain_grid]

    def visualize_map(self, map_data: Dict[str, any]) -> str:
        """Generate ASCII visualization of the generated map"""
        lines = []
        lines.append("=" * (map_data["width"] + 2))
        lines.append(
            f"Procedurally Generated Map ({map_data['width']}x{map_data['height']})"
        )
        lines.append("=" * (map_data["width"] + 2))

        terrain = map_data["terrain"]
        spawn_points = map_data.get("spawn_points", [])

        for y, row in enumerate(terrain):
            line = ""
            for x, cell in enumerate(row):
                # Mark spawn points
                if (x, y) in spawn_points:
                    line += "S"
                else:
                    line += cell
            lines.append(line)

        lines.append("=" * (map_data["width"] + 2))
        lines.append(
            "Legend: . = Floor  # = Wall  ~ = Rough  ≈ = Water  C = Cover  X = Obstacle  S = Spawn"
        )

        return "\n".join(lines)


def demo_procedural_generation():
    """Demo the procedural generation system"""
    print("=" * 70)
    print("PROCEDURAL GENERATION SYSTEM DEMO")
    print("=" * 70)

    # Interior map
    config = GenerationConfig(width=40, height=25)
    generator = ProceduralGenerator(config, seed=12345)

    print("\n1. INTERIOR MAP GENERATION:\n")
    interior_map = generator.generate_interior_map()
    print(generator.visualize_map(interior_map))

    # Exterior map
    print("\n" + "=" * 70)
    print("\n2. EXTERIOR MAP GENERATION:\n")
    config2 = GenerationConfig(width=40, height=25, obstacle_density=0.20)
    generator2 = ProceduralGenerator(config2, seed=67890)
    exterior_map = generator2.generate_exterior_map()
    print(generator2.visualize_map(exterior_map))

    # Competitive map
    print("\n" + "=" * 70)
    print("\n3. COMPETITIVE MAP GENERATION:\n")
    config3 = GenerationConfig(width=40, height=25, symmetrical=True)
    generator3 = ProceduralGenerator(config3, seed=11111)
    competitive_map = generator3.generate_competitive_map(num_players=2)
    print(generator3.visualize_map(competitive_map))

    print("\n" + "=" * 70)


if __name__ == "__main__":
    demo_procedural_generation()
