"""
Comprehensive tests for Zone System

Tests zone loading, transitions, spawn points, and entity spawning.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from neonworks.core.ecs import Entity, GridPosition, Sprite, Transform, World
from neonworks.core.events import EventType
from neonworks.gameplay.movement import Direction, TileCollisionMap, ZoneTrigger
from neonworks.systems.zone_system import ZoneData, ZoneSystem


class TestZoneData:
    """Test ZoneData class"""

    def test_zone_data_init(self):
        """Test creating zone data"""
        zone = ZoneData("town_01")

        assert zone.zone_id == "town_01"
        assert zone.name == ""
        assert zone.width == 0
        assert zone.height == 0
        assert zone.tile_size == 32
        assert zone.tilemap is None
        assert zone.collision_map is None
        assert len(zone.spawn_points) == 0
        assert len(zone.properties) == 0
        assert zone.background_music is None
        assert zone.encounter_rate == 0.0
        assert zone.encounter_table == ""


class TestZoneSystemInit:
    """Test ZoneSystem initialization"""

    def test_init_default(self):
        """Test creating zone system"""
        event_mgr = Mock()
        system = ZoneSystem(event_mgr)

        assert system.event_manager is event_mgr
        assert system.asset_base_path == Path("assets")
        assert system.priority == 5
        assert system.current_zone is None
        assert system.current_zone_id == ""
        assert len(system.zone_cache) == 0
        assert not system.is_transitioning
        assert system.player_entity is None

    def test_init_custom_asset_path(self):
        """Test creating zone system with custom asset path"""
        event_mgr = Mock()
        system = ZoneSystem(event_mgr, asset_base_path="custom/assets")

        assert system.asset_base_path == Path("custom/assets")

    def test_get_current_zone_data_none(self):
        """Test getting current zone data when none loaded"""
        event_mgr = Mock()
        system = ZoneSystem(event_mgr)

        assert system.get_current_zone_data() is None

    def test_get_current_zone_data(self):
        """Test getting current zone data"""
        event_mgr = Mock()
        system = ZoneSystem(event_mgr)

        zone = ZoneData("test_zone")
        system.current_zone = zone

        assert system.get_current_zone_data() is zone


class TestZoneLoading:
    """Test zone loading"""

    def test_load_zone_from_file_not_found(self):
        """Test loading non-existent zone"""
        event_mgr = Mock()
        system = ZoneSystem(event_mgr, asset_base_path="/nonexistent")

        zone = system._load_zone_from_file("missing_zone")

        assert zone is None

    def test_load_zone_from_file_success(self, tmp_path):
        """Test loading zone from valid file"""
        # Create test zone file
        zone_data = {
            "name": "Test Town",
            "width": 20,
            "height": 15,
            "tile_size": 32,
            "background_music": "town_theme.ogg",
            "encounter_rate": 0.05,
            "encounter_table": "grassland",
            "spawn_points": [
                {"name": "entrance", "x": 10, "y": 14, "direction": "UP"},
                {"name": "center", "x": 10, "y": 7, "direction": "DOWN"},
            ],
            "tilemap": {},
            "collision": {},
            "npcs": [],
            "objects": [],
            "triggers": [],
            "properties": {"weather": "sunny"},
        }

        maps_dir = tmp_path / "maps"
        maps_dir.mkdir()
        zone_file = maps_dir / "test_town.json"
        with open(zone_file, "w") as f:
            json.dump(zone_data, f)

        event_mgr = Mock()
        system = ZoneSystem(event_mgr, asset_base_path=str(tmp_path))

        zone = system._load_zone_from_file("test_town")

        assert zone is not None
        assert zone.zone_id == "test_town"
        assert zone.name == "Test Town"
        assert zone.width == 20
        assert zone.height == 15
        assert zone.tile_size == 32
        assert zone.background_music == "town_theme.ogg"
        assert zone.encounter_rate == 0.05
        assert zone.encounter_table == "grassland"
        assert "entrance" in zone.spawn_points
        assert "center" in zone.spawn_points
        assert zone.spawn_points["entrance"] == (10, 14, Direction.UP)
        assert zone.properties["weather"] == "sunny"

    def test_load_zone_creates_default_spawn(self, tmp_path):
        """Test loading zone creates default spawn point if missing"""
        zone_data = {
            "name": "Test",
            "width": 20,
            "height": 15,
            "spawn_points": [],
        }

        maps_dir = tmp_path / "maps"
        maps_dir.mkdir()
        zone_file = maps_dir / "test.json"
        with open(zone_file, "w") as f:
            json.dump(zone_data, f)

        event_mgr = Mock()
        system = ZoneSystem(event_mgr, asset_base_path=str(tmp_path))

        zone = system._load_zone_from_file("test")

        assert "default" in zone.spawn_points
        assert zone.spawn_points["default"] == (10, 7, Direction.DOWN)

    def test_load_zone_caches_zone(self, tmp_path):
        """Test loading zone caches the zone data"""
        zone_data = {"name": "Test", "width": 10, "height": 10}

        maps_dir = tmp_path / "maps"
        maps_dir.mkdir()
        zone_file = maps_dir / "test.json"
        with open(zone_file, "w") as f:
            json.dump(zone_data, f)

        event_mgr = Mock()
        system = ZoneSystem(event_mgr, asset_base_path=str(tmp_path))
        world = World()

        # Load zone
        system.load_zone(world, "test")

        # Check cache
        assert "test" in system.zone_cache
        assert system.zone_cache["test"].name == "Test"

    def test_load_zone_uses_cache(self, tmp_path):
        """Test loading zone uses cached data"""
        zone_data = {"name": "Test", "width": 10, "height": 10}

        maps_dir = tmp_path / "maps"
        maps_dir.mkdir()
        zone_file = maps_dir / "test.json"
        with open(zone_file, "w") as f:
            json.dump(zone_data, f)

        event_mgr = Mock()
        system = ZoneSystem(event_mgr, asset_base_path=str(tmp_path))
        world = World()

        # Load zone twice
        system.load_zone(world, "test")
        system.load_zone(world, "test")

        # Cache should only have one entry
        assert len(system.zone_cache) == 1


class TestZoneTransitions:
    """Test zone transitions"""

    def test_load_zone_emits_event(self, tmp_path):
        """Test loading zone emits event"""
        zone_data = {"name": "Test Zone", "width": 10, "height": 10}

        maps_dir = tmp_path / "maps"
        maps_dir.mkdir()
        zone_file = maps_dir / "test.json"
        with open(zone_file, "w") as f:
            json.dump(zone_data, f)

        event_mgr = Mock()
        system = ZoneSystem(event_mgr, asset_base_path=str(tmp_path))
        world = World()

        system.load_zone(world, "test", spawn_point="default")

        # Check event was emitted
        event_mgr.emit.assert_called()
        emitted_event = event_mgr.emit.call_args[0][0]
        assert emitted_event.event_type == EventType.CUSTOM
        assert emitted_event.data["type"] == "zone_loaded"
        assert emitted_event.data["zone_id"] == "test"
        assert emitted_event.data["zone_name"] == "Test Zone"

    def test_transition_to_zone_sets_flag(self, tmp_path):
        """Test transition sets is_transitioning flag"""
        zone_data = {"name": "Test", "width": 10, "height": 10}

        maps_dir = tmp_path / "maps"
        maps_dir.mkdir()
        zone_file = maps_dir / "test.json"
        with open(zone_file, "w") as f:
            json.dump(zone_data, f)

        event_mgr = Mock()
        system = ZoneSystem(event_mgr, asset_base_path=str(tmp_path))
        world = World()

        # Transition should set and clear flag
        system.transition_to_zone(world, "test")

        assert not system.is_transitioning  # Should be False after transition

    def test_transition_blocks_if_already_transitioning(self, tmp_path):
        """Test transition blocks if already transitioning"""
        event_mgr = Mock()
        system = ZoneSystem(event_mgr, asset_base_path=str(tmp_path))
        world = World()

        system.is_transitioning = True

        # Try to transition (should be blocked)
        system.transition_to_zone(world, "test")

        # Event should not be emitted
        event_mgr.emit.assert_not_called()

    def test_transition_emits_start_and_complete_events(self, tmp_path):
        """Test transition emits start and complete events"""
        zone_data = {"name": "Test", "width": 10, "height": 10}

        maps_dir = tmp_path / "maps"
        maps_dir.mkdir()
        zone_file = maps_dir / "test.json"
        with open(zone_file, "w") as f:
            json.dump(zone_data, f)

        event_mgr = Mock()
        system = ZoneSystem(event_mgr, asset_base_path=str(tmp_path))
        world = World()

        system.transition_to_zone(world, "test", transition_type="fade", duration=0.5)

        # Should emit 3 events: start, loaded, complete
        assert event_mgr.emit.call_count == 3

        # Check start event
        start_event = event_mgr.emit.call_args_list[0][0][0]
        assert start_event.data["type"] == "zone_transition_start"
        assert start_event.data["transition_type"] == "fade"
        assert start_event.data["duration"] == 0.5

        # Check complete event
        complete_event = event_mgr.emit.call_args_list[2][0][0]
        assert complete_event.data["type"] == "zone_transition_complete"
        assert complete_event.data["success"] is True


class TestSpawnPoints:
    """Test spawn point handling"""

    def test_position_player_at_spawn(self, tmp_path):
        """Test positioning player at spawn point"""
        zone_data = {
            "name": "Test",
            "width": 20,
            "height": 15,
            "tile_size": 32,
            "spawn_points": [{"name": "entrance", "x": 5, "y": 10, "direction": "UP"}],
        }

        maps_dir = tmp_path / "maps"
        maps_dir.mkdir()
        zone_file = maps_dir / "test.json"
        with open(zone_file, "w") as f:
            json.dump(zone_data, f)

        event_mgr = Mock()
        system = ZoneSystem(event_mgr, asset_base_path=str(tmp_path))
        world = World()

        # Create player
        player = Entity()
        player.tags.add("player")
        player.add_component(GridPosition(grid_x=0, grid_y=0))
        player.add_component(Transform(x=0, y=0))
        world.add_entity(player)

        # Load zone with specific spawn point
        system.load_zone(world, "test", spawn_point="entrance")

        # Check player position
        grid_pos = player.get_component(GridPosition)
        transform = player.get_component(Transform)
        assert grid_pos.grid_x == 5
        assert grid_pos.grid_y == 10
        assert transform.x == 160  # 5 * 32
        assert transform.y == 320  # 10 * 32

    def test_position_player_fallback_to_default(self, tmp_path):
        """Test positioning player falls back to default spawn"""
        zone_data = {
            "name": "Test",
            "width": 20,
            "height": 15,
            "spawn_points": [{"name": "default", "x": 10, "y": 7, "direction": "DOWN"}],
        }

        maps_dir = tmp_path / "maps"
        maps_dir.mkdir()
        zone_file = maps_dir / "test.json"
        with open(zone_file, "w") as f:
            json.dump(zone_data, f)

        event_mgr = Mock()
        system = ZoneSystem(event_mgr, asset_base_path=str(tmp_path))
        world = World()

        # Create player
        player = Entity()
        player.tags.add("player")
        player.add_component(GridPosition(grid_x=0, grid_y=0))
        player.add_component(Transform(x=0, y=0))
        world.add_entity(player)

        # Load zone with non-existent spawn point
        system.load_zone(world, "test", spawn_point="nonexistent")

        # Should use default spawn
        grid_pos = player.get_component(GridPosition)
        assert grid_pos.grid_x == 10
        assert grid_pos.grid_y == 7


class TestZoneTriggers:
    """Test zone trigger detection"""

    def test_check_zone_triggers_no_player(self):
        """Test checking triggers with no player"""
        event_mgr = Mock()
        system = ZoneSystem(event_mgr)
        world = World()

        # Should not crash
        system._check_zone_triggers(world)

    def test_check_zone_triggers_finds_player(self):
        """Test checking triggers finds player entity"""
        event_mgr = Mock()
        system = ZoneSystem(event_mgr)
        world = World()

        # Create player
        player = Entity()
        player.tags.add("player")
        player.add_component(GridPosition(grid_x=5, grid_y=5))
        world.add_entity(player)

        system._check_zone_triggers(world)

        assert system.player_entity is player

    def test_check_zone_triggers_during_transition(self):
        """Test triggers are ignored during transition"""
        event_mgr = Mock()
        system = ZoneSystem(event_mgr)
        world = World()

        system.is_transitioning = True

        # Should return early
        system._check_zone_triggers(world)

        # No events should be emitted
        event_mgr.emit.assert_not_called()

    def test_check_zone_triggers_activates_on_position(self, tmp_path):
        """Test zone trigger activates when player steps on it"""
        # Create zone with trigger
        zone_data = {
            "name": "Test",
            "width": 10,
            "height": 10,
            "triggers": [
                {
                    "x": 5,
                    "y": 5,
                    "target_zone": "next_zone",
                    "target_spawn": "entrance",
                    "transition_type": "fade",
                }
            ],
        }

        maps_dir = tmp_path / "maps"
        maps_dir.mkdir()
        zone_file = maps_dir / "test.json"
        with open(zone_file, "w") as f:
            json.dump(zone_data, f)

        event_mgr = Mock()
        system = ZoneSystem(event_mgr, asset_base_path=str(tmp_path))
        world = World()

        # Load zone
        system.load_zone(world, "test")

        # Create player at trigger position
        player = Entity()
        player.tags.add("player")
        player.add_component(GridPosition(grid_x=5, grid_y=5))
        world.add_entity(player)
        system.player_entity = player

        # Check triggers (will try to transition)
        with patch.object(system, "transition_to_zone") as mock_transition:
            system._check_zone_triggers(world)
            mock_transition.assert_called_once()


class TestEntitySpawning:
    """Test NPC/object/trigger spawning"""

    def test_unload_current_zone_removes_entities(self):
        """Test unloading zone removes tagged entities"""
        event_mgr = Mock()
        system = ZoneSystem(event_mgr)
        world = World()

        # Manually create entities with zone tags
        npc = Entity()
        npc.tags.add("npc")
        world.add_entity(npc)

        obj = Entity()
        obj.tags.add("object")
        world.add_entity(obj)

        trigger = Entity()
        trigger.tags.add("zone_trigger")
        world.add_entity(trigger)

        # Check entities exist
        assert len(world.get_entities_with_tag("npc")) == 1
        assert len(world.get_entities_with_tag("object")) == 1
        assert len(world.get_entities_with_tag("zone_trigger")) == 1

        # Unload zone
        system._unload_current_zone(world)

        # Check entities were removed
        assert len(world.get_entities_with_tag("npc")) == 0
        assert len(world.get_entities_with_tag("object")) == 0
        assert len(world.get_entities_with_tag("zone_trigger")) == 0


class TestFullWorkflow:
    """Test complete zone system workflow"""

    def test_full_zone_load_workflow(self, tmp_path):
        """Test complete zone loading workflow"""
        zone_data = {
            "name": "Starting Town",
            "width": 20,
            "height": 15,
            "tile_size": 32,
            "spawn_points": [{"name": "default", "x": 10, "y": 7, "direction": "DOWN"}],
        }

        maps_dir = tmp_path / "maps"
        maps_dir.mkdir()
        zone_file = maps_dir / "town.json"
        with open(zone_file, "w") as f:
            json.dump(zone_data, f)

        event_mgr = Mock()
        system = ZoneSystem(event_mgr, asset_base_path=str(tmp_path))
        world = World()

        # Create player
        player = Entity()
        player.tags.add("player")
        player.add_component(GridPosition(grid_x=0, grid_y=0))
        player.add_component(Transform(x=0, y=0))
        world.add_entity(player)

        # Load zone
        success = system.load_zone(world, "town")

        assert success
        assert system.current_zone_id == "town"
        assert system.current_zone.name == "Starting Town"

        # Check player was positioned
        grid_pos = player.get_component(GridPosition)
        assert grid_pos.grid_x == 10
        assert grid_pos.grid_y == 7

        # Check zone data is set
        assert system.current_zone.width == 20
        assert system.current_zone.height == 15


# Run tests with: pytest tests/test_zone_system.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
