"""
Zone Transition System

Handles loading and transitioning between different maps/zones.
"""

import json
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from gameplay.movement import Direction, TileCollisionMap, ZoneTrigger
from neonworks.core.ecs import Entity, GridPosition, Sprite, System, Transform, World
from neonworks.core.events import Event, EventManager, EventType
from neonworks.rendering.tilemap import Tile, TileLayer, Tilemap, Tileset


class ZoneData:
    """Container for zone/map data"""

    def __init__(self, zone_id: str):
        self.zone_id = zone_id
        self.name = ""
        self.width = 0
        self.height = 0
        self.tile_size = 32

        # Tilemap data
        self.tilemap: Optional[Tilemap] = None
        self.collision_map: Optional[TileCollisionMap] = None

        # Spawn points
        self.spawn_points: Dict[str, tuple] = {}  # name -> (x, y, direction)

        # Zone properties
        self.properties: Dict[str, Any] = {}
        self.background_music: Optional[str] = None
        self.encounter_rate: float = 0.0
        self.encounter_table: str = ""

        # NPCs and objects
        self.npcs: list = []
        self.objects: list = []
        self.triggers: list = []


class ZoneSystem(System):
    """
    System for managing zone transitions and map loading.

    Features:
    - Load and unload zones
    - Handle zone transitions
    - Manage spawn points
    - Trigger zone change events
    """

    def __init__(self, event_manager: EventManager, asset_base_path: str = "assets"):
        super().__init__()
        self.priority = 5
        self.event_manager = event_manager
        self.asset_base_path = Path(asset_base_path)

        # Current zone
        self.current_zone: Optional[ZoneData] = None
        self.current_zone_id: str = ""

        # Zone cache (zone_id -> ZoneData)
        self.zone_cache: Dict[str, ZoneData] = {}

        # Transition state
        self.is_transitioning = False
        self.transition_callback: Optional[Callable] = None

        # Player entity reference
        self.player_entity: Optional[Entity] = None

    def update(self, world: World, delta_time: float):
        """Update zone system"""
        # Check for zone triggers
        self._check_zone_triggers(world)

    def load_zone(
        self, world: World, zone_id: str, spawn_point: str = "default"
    ) -> bool:
        """
        Load a zone and spawn player at designated point.

        Args:
            world: ECS world
            zone_id: ID of zone to load
            spawn_point: Name of spawn point

        Returns:
            True if loaded successfully
        """
        # Check cache first
        if zone_id in self.zone_cache:
            zone_data = self.zone_cache[zone_id]
        else:
            # Load from file
            zone_data = self._load_zone_from_file(zone_id)
            if not zone_data:
                return False
            self.zone_cache[zone_id] = zone_data

        # Unload current zone
        if self.current_zone:
            self._unload_current_zone(world)

        # Set new current zone
        self.current_zone = zone_data
        self.current_zone_id = zone_id

        # Spawn zone entities (NPCs, objects, triggers)
        self._spawn_zone_entities(world, zone_data)

        # Position player at spawn point
        self._position_player_at_spawn(world, spawn_point)

        # Emit zone loaded event
        self.event_manager.emit(
            Event(
                EventType.CUSTOM,
                {
                    "type": "zone_loaded",
                    "zone_id": zone_id,
                    "zone_name": zone_data.name,
                    "spawn_point": spawn_point,
                },
            )
        )

        return True

    def transition_to_zone(
        self,
        world: World,
        zone_id: str,
        spawn_point: str = "default",
        transition_type: str = "fade",
        duration: float = 0.5,
    ):
        """
        Transition to a new zone with visual effect.

        Args:
            world: ECS world
            zone_id: Target zone ID
            spawn_point: Spawn point name
            transition_type: Type of transition effect
            duration: Transition duration in seconds
        """
        if self.is_transitioning:
            return

        self.is_transitioning = True

        # Emit transition start event
        self.event_manager.emit(
            Event(
                EventType.CUSTOM,
                {
                    "type": "zone_transition_start",
                    "zone_id": zone_id,
                    "transition_type": transition_type,
                    "duration": duration,
                },
            )
        )

        # TODO: In a real implementation, this would wait for transition effect
        # For now, load immediately
        success = self.load_zone(world, zone_id, spawn_point)

        self.is_transitioning = False

        # Emit transition complete event
        self.event_manager.emit(
            Event(
                EventType.CUSTOM,
                {
                    "type": "zone_transition_complete",
                    "zone_id": zone_id,
                    "success": success,
                },
            )
        )

    def _load_zone_from_file(self, zone_id: str) -> Optional[ZoneData]:
        """Load zone data from JSON file"""
        zone_file = self.asset_base_path / "maps" / f"{zone_id}.json"

        if not zone_file.exists():
            print(f"Zone file not found: {zone_file}")
            return None

        try:
            with open(zone_file, "r") as f:
                data = json.load(f)

            zone = ZoneData(zone_id)
            zone.name = data.get("name", zone_id)
            zone.width = data.get("width", 20)
            zone.height = data.get("height", 15)
            zone.tile_size = data.get("tile_size", 32)
            zone.background_music = data.get("background_music")
            zone.encounter_rate = data.get("encounter_rate", 0.0)
            zone.encounter_table = data.get("encounter_table", "")

            # Load spawn points
            for spawn in data.get("spawn_points", []):
                name = spawn.get("name", "default")
                x = spawn.get("x", 0)
                y = spawn.get("y", 0)
                direction = Direction[spawn.get("direction", "DOWN").upper()]
                zone.spawn_points[name] = (x, y, direction)

            # Ensure default spawn point exists
            if "default" not in zone.spawn_points:
                zone.spawn_points["default"] = (
                    zone.width // 2,
                    zone.height // 2,
                    Direction.DOWN,
                )

            # Load tilemap
            zone.tilemap = self._load_tilemap(data.get("tilemap", {}), zone)

            # Load collision map
            zone.collision_map = self._load_collision_map(
                data.get("collision", {}), zone
            )

            # Load NPCs
            zone.npcs = data.get("npcs", [])

            # Load objects
            zone.objects = data.get("objects", [])

            # Load triggers
            zone.triggers = data.get("triggers", [])

            zone.properties = data.get("properties", {})

            return zone

        except Exception as e:
            print(f"Error loading zone {zone_id}: {e}")
            return None

    def _load_tilemap(self, tilemap_data: dict, zone: ZoneData) -> Optional[Tilemap]:
        """Load tilemap from zone data"""
        if not tilemap_data:
            return None

        tilemap = Tilemap(zone.width, zone.height, zone.tile_size, zone.tile_size)

        # Load tilesets
        for tileset_data in tilemap_data.get("tilesets", []):
            tileset = Tileset(
                name=tileset_data.get("name", "default"),
                texture_path=tileset_data.get("image", ""),
                tile_width=tileset_data.get("tile_width", 32),
                tile_height=tileset_data.get("tile_height", 32),
                columns=tileset_data.get("columns", 10),
                tile_count=tileset_data.get("tile_count", 100),
            )
            tilemap.add_tileset(tileset)

        # Load layers
        for layer_data in tilemap_data.get("layers", []):
            layer = TileLayer(
                name=layer_data.get("name", "layer"),
                width=zone.width,
                height=zone.height,
                visible=layer_data.get("visible", True),
                opacity=layer_data.get("opacity", 1.0),
            )

            # Load tile data
            tiles_data = layer_data.get("data", [])
            if tiles_data:
                for y in range(min(zone.height, len(tiles_data))):
                    row = tiles_data[y]
                    for x in range(min(zone.width, len(row))):
                        tile_id = row[x]
                        layer.set_tile(x, y, Tile(tile_id=tile_id))

            tilemap.add_layer(layer)

        return tilemap

    def _load_collision_map(
        self, collision_data: dict, zone: ZoneData
    ) -> TileCollisionMap:
        """Load collision map from zone data"""
        collision_map = TileCollisionMap()
        collision_map.width = zone.width
        collision_map.height = zone.height

        # Get blocked tile IDs
        blocked_tiles = set(collision_data.get("blocked_tiles", []))

        # Load collision layer if specified
        if "layer" in collision_data and zone.tilemap:
            layer_name = collision_data["layer"]
            layer = zone.tilemap.get_layer_by_name(layer_name)
            if layer:
                layer_data = [[tile.tile_id for tile in row] for row in layer.tiles]
                collision_map.load_from_layer(layer_data, blocked_tiles)
        else:
            # Default: all tiles walkable
            collision_map.collision_data = [
                [True] * zone.width for _ in range(zone.height)
            ]

        return collision_map

    def _spawn_zone_entities(self, world: World, zone: ZoneData):
        """Spawn NPCs, objects, and triggers for the zone"""
        # Spawn NPCs
        for npc_data in zone.npcs:
            self._spawn_npc(world, npc_data)

        # Spawn objects
        for obj_data in zone.objects:
            self._spawn_object(world, obj_data)

        # Spawn triggers
        for trigger_data in zone.triggers:
            self._spawn_trigger(world, trigger_data)

    def _spawn_npc(self, world: World, npc_data: dict):
        """Spawn an NPC entity"""
        from gameplay.movement import (
            AnimationState,
            Interactable,
            Movement,
            NPCBehavior,
        )

        npc = world.create_entity()
        npc.add_tag("npc")

        # Position
        x = npc_data.get("x", 0)
        y = npc_data.get("y", 0)
        npc.add_component(GridPosition(grid_x=x, grid_y=y))
        npc.add_component(Transform(x=x * zone.tile_size, y=y * zone.tile_size))

        # Visual
        sprite_path = npc_data.get("sprite", "")
        npc.add_component(Sprite(texture=sprite_path, width=32, height=32))

        # Movement
        movement = Movement(
            speed=npc_data.get("move_speed", 2.0),
            can_move=True,
        )
        npc.add_component(movement)

        # Behavior
        behavior = NPCBehavior(
            behavior_type=npc_data.get("behavior", "static"),
            dialogue_id=npc_data.get("dialogue_id"),
            move_speed=npc_data.get("move_speed", 2.0),
        )

        # Load patrol points if patrol behavior
        if behavior.behavior_type == "patrol":
            patrol_points = npc_data.get("patrol_points", [])
            behavior.patrol_points = [(p["x"], p["y"]) for p in patrol_points]

        npc.add_component(behavior)

        # Animation
        anim_state = AnimationState(
            current_state="idle", current_direction=Direction.DOWN
        )
        npc.add_component(anim_state)

        # Interactable
        if npc_data.get("can_talk", True):
            interactable = Interactable(
                interaction_type="talk",
                dialogue_id=npc_data.get("dialogue_id"),
            )
            npc.add_component(interactable)

    def _spawn_object(self, world: World, obj_data: dict):
        """Spawn an object entity (chest, sign, etc.)"""
        from gameplay.movement import Collider2D, Interactable

        obj = world.create_entity()
        obj.add_tag("object")

        # Position
        x = obj_data.get("x", 0)
        y = obj_data.get("y", 0)
        obj.add_component(GridPosition(grid_x=x, grid_y=y))
        obj.add_component(
            Transform(
                x=x * self.current_zone.tile_size, y=y * self.current_zone.tile_size
            )
        )

        # Visual
        sprite_path = obj_data.get("sprite", "")
        obj.add_component(Sprite(texture=sprite_path, width=32, height=32))

        # Collision
        if obj_data.get("is_solid", True):
            obj.add_component(Collider2D(is_solid=True))

        # Interactable
        if obj_data.get("can_interact", True):
            interactable = Interactable(
                interaction_type=obj_data.get("interaction_type", "examine"),
                dialogue_id=obj_data.get("dialogue_id"),
                item_id=obj_data.get("item_id"),
            )
            obj.add_component(interactable)

    def _spawn_trigger(self, world: World, trigger_data: dict):
        """Spawn a zone transition trigger"""
        trigger = world.create_entity()
        trigger.add_tag("zone_trigger")

        # Position
        x = trigger_data.get("x", 0)
        y = trigger_data.get("y", 0)
        trigger.add_component(GridPosition(grid_x=x, grid_y=y))

        # Zone trigger
        target_zone = trigger_data.get("target_zone", "")
        target_spawn = trigger_data.get("target_spawn", "default")
        direction_str = trigger_data.get("target_direction", "DOWN")
        direction = Direction[direction_str.upper()]

        zone_trigger = ZoneTrigger(
            target_zone=target_zone,
            target_x=trigger_data.get("target_x", 0),
            target_y=trigger_data.get("target_y", 0),
            target_direction=direction,
            transition_type=trigger_data.get("transition_type", "fade"),
        )
        trigger.add_component(zone_trigger)

    def _unload_current_zone(self, world: World):
        """Unload current zone entities"""
        # Remove NPCs
        for npc in world.get_entities_with_tag("npc"):
            world.remove_entity(npc.id)

        # Remove objects
        for obj in world.get_entities_with_tag("object"):
            world.remove_entity(obj.id)

        # Remove triggers
        for trigger in world.get_entities_with_tag("zone_trigger"):
            world.remove_entity(trigger.id)

    def _position_player_at_spawn(self, world: World, spawn_point: str):
        """Position player at spawn point"""
        if not self.player_entity:
            players = world.get_entities_with_tag("player")
            if players:
                self.player_entity = players[0]

        if not self.player_entity or not self.current_zone:
            return

        # Get spawn point
        spawn_data = self.current_zone.spawn_points.get(spawn_point)
        if not spawn_data:
            spawn_data = self.current_zone.spawn_points.get(
                "default", (0, 0, Direction.DOWN)
            )

        x, y, direction = spawn_data

        # Update player position
        grid_pos = self.player_entity.get_component(GridPosition)
        transform = self.player_entity.get_component(Transform)
        from gameplay.movement import Movement

        if grid_pos:
            grid_pos.grid_x = x
            grid_pos.grid_y = y

        if transform:
            transform.x = x * self.current_zone.tile_size
            transform.y = y * self.current_zone.tile_size

        movement = self.player_entity.get_component(Movement)
        if movement:
            movement.facing = direction

    def _check_zone_triggers(self, world: World):
        """Check if player has triggered a zone transition"""
        if self.is_transitioning:
            return

        if not self.player_entity:
            players = world.get_entities_with_tag("player")
            if players:
                self.player_entity = players[0]

        if not self.player_entity:
            return

        player_grid = self.player_entity.get_component(GridPosition)
        if not player_grid:
            return

        # Check all zone triggers
        triggers = world.get_entities_with_components(ZoneTrigger, GridPosition)

        for trigger_entity in triggers:
            zone_trigger = trigger_entity.get_component(ZoneTrigger)
            trigger_grid = trigger_entity.get_component(GridPosition)

            if not zone_trigger.is_active:
                continue

            # Check if player is on trigger tile
            if (
                player_grid.grid_x == trigger_grid.grid_x
                and player_grid.grid_y == trigger_grid.grid_y
            ):
                # Trigger zone transition
                self.transition_to_zone(
                    world,
                    zone_trigger.target_zone,
                    "default",  # Use default spawn point
                    zone_trigger.transition_type,
                    zone_trigger.transition_duration,
                )
                return

    def get_current_zone_data(self) -> Optional[ZoneData]:
        """Get current zone data"""
        return self.current_zone
