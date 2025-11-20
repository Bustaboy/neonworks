"""
AI Vision Context System

Exports visual state of the level for AI screen awareness.
AI can see what's on screen and understand spatial relationships.
"""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from ..core.ecs import GridPosition, Sprite, Transform, World
from ..rendering.tilemap import Tile, TileLayer, Tilemap


@dataclass
class EntitySnapshot:
    """Snapshot of an entity visible on screen"""

    id: int
    name: str
    position: Tuple[int, int]  # Grid position
    tags: List[str]
    components: Dict[str, Any]  # Component type → simplified data
    sprite_info: Optional[str] = None


@dataclass
class TilemapSnapshot:
    """Snapshot of tilemap state"""

    width: int
    height: int
    layers: Dict[int, Dict[str, Any]]  # layer_id → {tiles: [(x,y,tile_id), ...]}
    visible_area: Tuple[int, int, int, int]  # (min_x, min_y, max_x, max_y)


@dataclass
class SpatialContext:
    """Spatial analysis of the current screen"""

    center_point: Tuple[int, int]
    bounds: Tuple[int, int, int, int]  # (min_x, min_y, max_x, max_y)
    entity_clusters: List[Dict[str, Any]]  # Groups of nearby entities
    empty_regions: List[Tuple[int, int, int, int]]  # (x, y, width, height)
    density_map: Dict[str, int]  # Entity type → count
    terrain_summary: Dict[str, int]  # Tile type → count


@dataclass
class AIVisionContext:
    """
    Complete visual context for AI assistant.

    The AI can see:
    - What tiles are placed and where
    - What entities exist and their positions
    - Spatial relationships (clusters, empty areas)
    - Density and distribution patterns
    """

    timestamp: str
    workspace: str
    current_layer: int
    selected_position: Optional[Tuple[int, int]]
    tilemap: TilemapSnapshot
    entities: List[EntitySnapshot]
    spatial: SpatialContext
    camera_offset: Tuple[int, int]
    visible_tiles: int
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON export"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AIVisionContext":
        """Load from dictionary"""
        # Reconstruct dataclasses
        tilemap = TilemapSnapshot(**data["tilemap"])
        entities = [EntitySnapshot(**e) for e in data["entities"]]
        spatial = SpatialContext(**data["spatial"])

        return cls(
            timestamp=data["timestamp"],
            workspace=data["workspace"],
            current_layer=data["current_layer"],
            selected_position=(
                tuple(data["selected_position"]) if data["selected_position"] else None
            ),
            tilemap=tilemap,
            entities=entities,
            spatial=spatial,
            camera_offset=tuple(data["camera_offset"]),
            visible_tiles=data["visible_tiles"],
            metadata=data.get("metadata", {}),
        )


class AIVisionExporter:
    """
    Exports visual context for AI assistant.

    Call export_vision() whenever the screen changes significantly.
    """

    def __init__(self):
        self.context_file = Path.home() / ".neonworks" / "ai_vision_context.json"
        self.context_file.parent.mkdir(parents=True, exist_ok=True)
        self.last_export_time = 0
        self.min_export_interval = 1.0  # Minimum 1 second between exports

    def export_vision(
        self,
        world: World,
        tilemap: Optional[Tilemap],
        camera_offset: Tuple[int, int],
        visible_area: Tuple[int, int, int, int],
        current_layer: int = 0,
        selected_position: Optional[Tuple[int, int]] = None,
        workspace: str = "level_editor",
    ) -> AIVisionContext:
        """
        Export current visual state to AI context.

        Args:
            world: ECS world with entities
            tilemap: Current tilemap
            camera_offset: Camera position
            visible_area: (min_x, min_y, max_x, max_y) in grid coords
            current_layer: Active layer
            selected_position: Currently selected grid position
            workspace: Current workspace ID

        Returns:
            AIVisionContext object
        """
        # Capture tilemap snapshot
        tilemap_snapshot = self._capture_tilemap(tilemap, visible_area)

        # Capture entity snapshot
        entities = self._capture_entities(world, visible_area)

        # Analyze spatial context
        spatial = self._analyze_spatial_context(tilemap_snapshot, entities, visible_area)

        # Build context
        context = AIVisionContext(
            timestamp=datetime.now().isoformat(),
            workspace=workspace,
            current_layer=current_layer,
            selected_position=selected_position,
            tilemap=tilemap_snapshot,
            entities=entities,
            spatial=spatial,
            camera_offset=camera_offset,
            visible_tiles=len(tilemap_snapshot.layers.get(current_layer, {}).get("tiles", [])),
        )

        # Export to file
        self._write_context(context)

        return context

    def _capture_tilemap(
        self, tilemap: Optional[Tilemap], visible_area: Tuple[int, int, int, int]
    ) -> TilemapSnapshot:
        """Capture tilemap state"""
        if not tilemap:
            return TilemapSnapshot(width=0, height=0, layers={}, visible_area=visible_area)

        min_x, min_y, max_x, max_y = visible_area

        layers_data = {}
        render_order = (
            tilemap.layer_manager.get_render_order()
            if hasattr(tilemap, "layer_manager")
            else []
        )

        for layer_index, layer_id in enumerate(render_order):
            layer = tilemap.layer_manager.get_layer(layer_id) if hasattr(tilemap, "layer_manager") else None
            if layer is None:
                continue

            tiles_list = []
            for y in range(min_y, max_y + 1):
                for x in range(min_x, max_x + 1):
                    tile = tilemap.get_tile(x, y, layer_index) if hasattr(tilemap, "get_tile") else None
                    if tile and tile.tile_id is not None:
                        tiles_list.append(
                            {
                                "x": x,
                                "y": y,
                                "tile_id": tile.tile_id,
                                "tileset_id": getattr(tile, "tileset_id", None),
                            }
                        )

            layers_data[layer_index] = {"tiles": tiles_list, "name": layer.properties.name}

        return TilemapSnapshot(
            width=tilemap.width,
            height=tilemap.height,
            layers=layers_data,
            visible_area=visible_area,
        )

    def _capture_entities(
        self, world: World, visible_area: Tuple[int, int, int, int]
    ) -> List[EntitySnapshot]:
        """Capture entities in visible area"""
        min_x, min_y, max_x, max_y = visible_area
        entities = []

        for entity in world.entities.values():
            # Get position
            grid_pos = entity.get_component(GridPosition)
            if not grid_pos:
                # Try Transform as fallback
                transform = entity.get_component(Transform)
                if not transform:
                    continue
                grid_x, grid_y = int(transform.x), int(transform.y)
            else:
                grid_x, grid_y = grid_pos.x, grid_pos.y

            # Check if in visible area
            if not (min_x <= grid_x <= max_x and min_y <= grid_y <= max_y):
                continue

            # Build component snapshot
            components = {}
            for comp_type, component in entity.components.items():
                comp_name = comp_type.__name__
                # Simplify component data
                if hasattr(component, "__dict__"):
                    components[comp_name] = {
                        k: v for k, v in component.__dict__.items() if not k.startswith("_")
                    }

            # Get sprite info
            sprite = entity.get_component(Sprite)
            sprite_info = sprite.texture if sprite else None

            entities.append(
                EntitySnapshot(
                    id=entity.id,
                    name=entity.name,
                    position=(grid_x, grid_y),
                    tags=list(entity.tags),
                    components=components,
                    sprite_info=sprite_info,
                )
            )

        return entities

    def _analyze_spatial_context(
        self,
        tilemap: TilemapSnapshot,
        entities: List[EntitySnapshot],
        visible_area: Tuple[int, int, int, int],
    ) -> SpatialContext:
        """Analyze spatial relationships and patterns"""
        min_x, min_y, max_x, max_y = visible_area

        # Calculate center
        center_x = (min_x + max_x) // 2
        center_y = (min_y + max_y) // 2

        # Count entity types
        density_map = {}
        for entity in entities:
            for tag in entity.tags:
                density_map[tag] = density_map.get(tag, 0) + 1

        # Find entity clusters (entities within 3 tiles of each other)
        clusters = self._find_clusters(entities, max_distance=3)

        # Find empty regions (areas with no entities or tiles)
        empty_regions = self._find_empty_regions(tilemap, entities, visible_area)

        # Count terrain types
        terrain_summary = {}
        for layer_data in getattr(tilemap, "layers", {}).values():
            for tile in layer_data.get("tiles", []):
                tile_id = tile.get("tile_id")
                if tile_id is not None:
                    terrain_summary[str(tile_id)] = terrain_summary.get(str(tile_id), 0) + 1

        return SpatialContext(
            center_point=(center_x, center_y),
            bounds=visible_area,
            entity_clusters=clusters,
            empty_regions=empty_regions,
            density_map=density_map,
            terrain_summary=terrain_summary,
        )

    def _find_clusters(
        self, entities: List[EntitySnapshot], max_distance: int = 3
    ) -> List[Dict[str, Any]]:
        """Find clusters of nearby entities"""
        if not entities:
            return []

        clusters = []
        visited = set()

        for i, entity in enumerate(entities):
            if i in visited:
                continue

            # Start new cluster
            cluster = {
                "center": entity.position,
                "entities": [entity.id],
                "tags": set(entity.tags),
                "bounds": [
                    entity.position[0],
                    entity.position[1],
                    entity.position[0],
                    entity.position[1],
                ],
            }

            # Find nearby entities
            for j, other in enumerate(entities):
                if i == j or j in visited:
                    continue

                dx = abs(entity.position[0] - other.position[0])
                dy = abs(entity.position[1] - other.position[1])

                if dx <= max_distance and dy <= max_distance:
                    cluster["entities"].append(other.id)
                    cluster["tags"].update(other.tags)
                    visited.add(j)

                    # Update bounds
                    cluster["bounds"][0] = min(cluster["bounds"][0], other.position[0])
                    cluster["bounds"][1] = min(cluster["bounds"][1], other.position[1])
                    cluster["bounds"][2] = max(cluster["bounds"][2], other.position[0])
                    cluster["bounds"][3] = max(cluster["bounds"][3], other.position[1])

            visited.add(i)

            # Only add clusters with 2+ entities
            if len(cluster["entities"]) >= 2:
                # Calculate actual center
                cluster["center"] = (
                    (cluster["bounds"][0] + cluster["bounds"][2]) // 2,
                    (cluster["bounds"][1] + cluster["bounds"][3]) // 2,
                )
                cluster["tags"] = list(cluster["tags"])
                clusters.append(cluster)

        return clusters

    def _find_empty_regions(
        self,
        tilemap: TilemapSnapshot,
        entities: List[EntitySnapshot],
        visible_area: Tuple[int, int, int, int],
        min_size: int = 3,
    ) -> List[Tuple[int, int, int, int]]:
        """Find empty regions in the map"""
        min_x, min_y, max_x, max_y = visible_area

        # Create occupancy grid
        width = max_x - min_x + 1
        height = max_y - min_y + 1
        occupied = [[False] * width for _ in range(height)]

        # Mark tiles as occupied
        for layer_data in getattr(tilemap, "layers", {}).values():
            for tile in layer_data.get("tiles", []):
                x, y = tile["x"] - min_x, tile["y"] - min_y
                if 0 <= x < width and 0 <= y < height:
                    occupied[y][x] = True

        # Mark entities as occupied
        for entity in entities:
            x, y = entity.position[0] - min_x, entity.position[1] - min_y
            if 0 <= x < width and 0 <= y < height:
                occupied[y][x] = True

        # Find rectangular empty regions
        empty_regions = []

        # Simple algorithm: scan for empty squares
        for y in range(height - min_size + 1):
            for x in range(width - min_size + 1):
                # Check if min_size x min_size region is empty
                is_empty = True
                for dy in range(min_size):
                    for dx in range(min_size):
                        if occupied[y + dy][x + dx]:
                            is_empty = False
                            break
                    if not is_empty:
                        break

                if is_empty:
                    empty_regions.append((min_x + x, min_y + y, min_size, min_size))

        return empty_regions[:10]  # Return max 10 regions

    def _write_context(self, context: AIVisionContext):
        """Write context to file"""
        try:
            with open(self.context_file, "w") as f:
                json.dump(context.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to export AI vision context: {e}")

    def load_context(self) -> Optional[AIVisionContext]:
        """Load vision context from file"""
        if not self.context_file.exists():
            return None

        try:
            with open(self.context_file, "r") as f:
                data = json.load(f)
                return AIVisionContext.from_dict(data)
        except Exception as e:
            print(f"Warning: Failed to load AI vision context: {e}")
            return None


# Singleton accessor
_vision_exporter_instance: Optional[AIVisionExporter] = None


def get_vision_exporter() -> AIVisionExporter:
    """Get the global AIVisionExporter instance (singleton)"""
    global _vision_exporter_instance
    if _vision_exporter_instance is None:
        _vision_exporter_instance = AIVisionExporter()
    return _vision_exporter_instance
