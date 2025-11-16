"""
Tests for Data Serialization System

Tests game state serialization, save/load functionality, and auto-save.
"""

import json
import time
from pathlib import Path

import pytest

from neonworks.core.ecs import (
    Building,
    Collider,
    Entity,
    GridPosition,
    Health,
    Navmesh,
    ResourceStorage,
    RigidBody,
    Sprite,
    Survival,
    Transform,
    TurnActor,
    World,
)
from neonworks.core.project import Project, ProjectConfig, ProjectMetadata
from neonworks.data.serialization import (
    AutoSaveManager,
    GameSerializer,
    SaveGameManager,
)


class TestGameSerializer:
    """Test suite for GameSerializer"""

    def test_serialize_grid_position(self):
        """Test serializing GridPosition component"""
        component = GridPosition(grid_x=10, grid_y=20, layer=2)

        data = GameSerializer.serialize_component(component)

        assert data["_type"] == "GridPosition"
        assert data["grid_x"] == 10
        assert data["grid_y"] == 20
        assert data["layer"] == 2

    def test_serialize_transform(self):
        """Test serializing Transform component"""
        component = Transform(x=100.5, y=200.7, rotation=45.0, scale_x=2.0, scale_y=1.5)

        data = GameSerializer.serialize_component(component)

        assert data["_type"] == "Transform"
        assert data["x"] == 100.5
        assert data["y"] == 200.7
        assert data["rotation"] == 45.0
        assert data["scale_x"] == 2.0
        assert data["scale_y"] == 1.5

    def test_serialize_sprite(self):
        """Test serializing Sprite component"""
        component = Sprite(
            texture="player.png",
            width=64,
            height=64,
            color=(255, 128, 0, 255),
            visible=True,
        )

        data = GameSerializer.serialize_component(component)

        assert data["_type"] == "Sprite"
        assert data["texture"] == "player.png"
        assert data["width"] == 64
        assert data["height"] == 64
        assert data["color"] == (255, 128, 0, 255)
        assert data["visible"] is True

    def test_serialize_health(self):
        """Test serializing Health component"""
        component = Health(current=80.0, maximum=100.0, regeneration=0.5)

        data = GameSerializer.serialize_component(component)

        assert data["_type"] == "Health"
        assert data["current"] == 80.0
        assert data["maximum"] == 100.0
        assert data["regeneration"] == 0.5

    def test_serialize_survival(self):
        """Test serializing Survival component"""
        component = Survival(
            hunger=75.0,
            thirst=60.0,
            energy=90.0,
            hunger_rate=1.2,
            thirst_rate=1.8,
            energy_rate=0.6,
        )

        data = GameSerializer.serialize_component(component)

        assert data["_type"] == "Survival"
        assert data["hunger"] == 75.0
        assert data["thirst"] == 60.0
        assert data["energy"] == 90.0

    def test_serialize_building(self):
        """Test serializing Building component"""
        component = Building(
            building_type="house",
            construction_progress=0.75,
            is_constructed=True,
            level=2,
            max_level=5,
        )

        data = GameSerializer.serialize_component(component)

        assert data["_type"] == "Building"
        assert data["building_type"] == "house"
        assert data["construction_progress"] == 0.75
        assert data["is_constructed"] is True
        assert data["level"] == 2
        assert data["max_level"] == 5

    def test_serialize_resource_storage(self):
        """Test serializing ResourceStorage component"""
        component = ResourceStorage(
            resources={"wood": 100, "stone": 50}, capacity={"wood": 200, "stone": 100}
        )

        data = GameSerializer.serialize_component(component)

        assert data["_type"] == "ResourceStorage"
        assert data["resources"] == {"wood": 100, "stone": 50}
        assert data["capacity"] == {"wood": 200, "stone": 100}

    def test_serialize_turn_actor(self):
        """Test serializing TurnActor component"""
        component = TurnActor(
            action_points=3, max_action_points=5, initiative=15, has_acted=True
        )

        data = GameSerializer.serialize_component(component)

        assert data["_type"] == "TurnActor"
        assert data["action_points"] == 3
        assert data["max_action_points"] == 5
        assert data["initiative"] == 15
        assert data["has_acted"] is True

    def test_serialize_navmesh(self):
        """Test serializing Navmesh component"""
        component = Navmesh(
            walkable_cells={(0, 0), (1, 0), (0, 1)},
            cost_multipliers={(0, 0): 1.0, (1, 0): 2.0},
        )

        data = GameSerializer.serialize_component(component)

        assert data["_type"] == "Navmesh"
        assert set(tuple(cell) for cell in data["walkable_cells"]) == {
            (0, 0),
            (1, 0),
            (0, 1),
        }
        assert data["cost_multipliers"]["0,0"] == 1.0
        assert data["cost_multipliers"]["1,0"] == 2.0

    def test_serialize_collider(self):
        """Test serializing Collider component"""
        component = Collider(
            width=32.0,
            height=48.0,
            offset_x=5.0,
            offset_y=10.0,
            is_trigger=True,
            layer=2,
            mask=0xFF,
        )

        data = GameSerializer.serialize_component(component)

        assert data["_type"] == "Collider"
        assert data["width"] == 32.0
        assert data["height"] == 48.0
        assert data["is_trigger"] is True

    def test_serialize_rigidbody(self):
        """Test serializing RigidBody component"""
        component = RigidBody(
            velocity_x=10.0,
            velocity_y=-5.0,
            mass=2.5,
            friction=0.15,
            is_static=False,
            gravity_scale=1.0,
        )

        data = GameSerializer.serialize_component(component)

        assert data["_type"] == "RigidBody"
        assert data["velocity_x"] == 10.0
        assert data["velocity_y"] == -5.0
        assert data["mass"] == 2.5
        assert data["is_static"] is False

    def test_deserialize_grid_position(self):
        """Test deserializing GridPosition component"""
        data = {"_type": "GridPosition", "grid_x": 15, "grid_y": 25, "layer": 1}

        component = GameSerializer.deserialize_component(data)

        assert isinstance(component, GridPosition)
        assert component.grid_x == 15
        assert component.grid_y == 25
        assert component.layer == 1

    def test_deserialize_transform(self):
        """Test deserializing Transform component"""
        data = {
            "_type": "Transform",
            "x": 50.0,
            "y": 75.0,
            "rotation": 90.0,
            "scale_x": 1.5,
            "scale_y": 2.0,
        }

        component = GameSerializer.deserialize_component(data)

        assert isinstance(component, Transform)
        assert component.x == 50.0
        assert component.y == 75.0
        assert component.rotation == 90.0

    def test_deserialize_sprite(self):
        """Test deserializing Sprite component"""
        data = {
            "_type": "Sprite",
            "texture": "enemy.png",
            "width": 32,
            "height": 32,
            "color": [255, 0, 0, 255],
            "visible": False,
        }

        component = GameSerializer.deserialize_component(data)

        assert isinstance(component, Sprite)
        assert component.texture == "enemy.png"
        assert component.visible is False

    def test_deserialize_health(self):
        """Test deserializing Health component"""
        data = {"_type": "Health", "current": 50.0, "maximum": 100.0, "regeneration": 1.0}

        component = GameSerializer.deserialize_component(data)

        assert isinstance(component, Health)
        assert component.current == 50.0
        assert component.maximum == 100.0

    def test_deserialize_navmesh(self):
        """Test deserializing Navmesh component"""
        data = {
            "_type": "Navmesh",
            "walkable_cells": [[0, 0], [1, 0], [0, 1]],
            "cost_multipliers": {"0,0": 1.0, "1,0": 2.5},
        }

        component = GameSerializer.deserialize_component(data)

        assert isinstance(component, Navmesh)
        assert (0, 0) in component.walkable_cells
        assert (1, 0) in component.walkable_cells
        assert component.cost_multipliers[(1, 0)] == 2.5

    def test_deserialize_unknown_component(self):
        """Test deserializing unknown component returns None"""
        data = {"_type": "UnknownComponent", "value": 123}

        component = GameSerializer.deserialize_component(data)

        assert component is None

    def test_serialize_entity(self):
        """Test serializing an entity"""
        entity = Entity(entity_id="test_entity")
        entity.add_component(Transform(x=100, y=200))
        entity.add_component(Health(current=80, maximum=100))
        entity.add_tag("player")
        entity.add_tag("ally")

        data = GameSerializer.serialize_entity(entity)

        assert data["id"] == "test_entity"
        assert "player" in data["tags"]
        assert "ally" in data["tags"]
        assert data["active"] is True
        assert len(data["components"]) == 2

    def test_deserialize_entity(self):
        """Test deserializing an entity"""
        data = {
            "id": "restored_entity",
            "tags": ["enemy", "boss"],
            "active": True,
            "components": [
                {"_type": "Transform", "x": 50.0, "y": 75.0, "rotation": 0.0},
                {"_type": "Health", "current": 200.0, "maximum": 200.0, "regeneration": 0.0},
            ],
        }

        entity = GameSerializer.deserialize_entity(data)

        assert entity.id == "restored_entity"
        assert "enemy" in entity.tags
        assert "boss" in entity.tags
        assert entity.has_component(Transform)
        assert entity.has_component(Health)

    def test_serialize_world(self):
        """Test serializing a world"""
        world = World()

        entity1 = world.create_entity("Entity1")
        entity1.add_component(Transform(x=10, y=20))

        entity2 = world.create_entity("Entity2")
        entity2.add_component(GridPosition(grid_x=5, grid_y=10))

        data = GameSerializer.serialize_world(world)

        assert len(data["entities"]) == 2

    def test_deserialize_world(self):
        """Test deserializing a world"""
        data = {
            "entities": [
                {
                    "id": "entity1",
                    "tags": ["player"],
                    "active": True,
                    "components": [
                        {"_type": "Transform", "x": 100.0, "y": 200.0, "rotation": 0.0}
                    ],
                },
                {
                    "id": "entity2",
                    "tags": ["enemy"],
                    "active": True,
                    "components": [
                        {"_type": "GridPosition", "grid_x": 5, "grid_y": 10, "layer": 0}
                    ],
                },
            ]
        }

        world = GameSerializer.deserialize_world(data)

        entities = world.get_entities()
        assert len(entities) == 2

    def test_round_trip_serialization(self):
        """Test complete serialize-deserialize round trip"""
        # Create original world
        world1 = World()

        player = world1.create_entity("Player")
        player.add_component(Transform(x=100, y=200))
        player.add_component(Health(current=75, maximum=100))
        player.add_tag("player")

        enemy = world1.create_entity("Enemy")
        enemy.add_component(GridPosition(grid_x=10, grid_y=15))
        enemy.add_tag("enemy")

        # Serialize
        data = GameSerializer.serialize_world(world1)

        # Deserialize
        world2 = GameSerializer.deserialize_world(data)

        # Verify
        assert len(world2.get_entities()) == 2

        players = world2.get_entities_with_tag("player")
        assert len(players) == 1
        assert players[0].has_component(Transform)
        assert players[0].has_component(Health)


class TestSaveGameManager:
    """Test suite for SaveGameManager"""

    @pytest.fixture
    def mock_project(self, tmp_path):
        """Create a mock project for testing"""
        # Create project structure
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()
        saves_dir = project_dir / "saves"
        saves_dir.mkdir()

        # Create mock project
        project = Project(str(project_dir))

        # Set up config manually
        metadata = ProjectMetadata(
            name="TestGame",
            version="1.0.0",
            description="Test project",
            author="Test Author",
        )
        project.config = ProjectConfig(metadata=metadata)

        # Mock get_save_path method
        def get_save_path(save_name):
            return saves_dir / f"{save_name}.json"

        project.get_save_path = get_save_path

        # Mock list_saves method
        def list_saves():
            return [f.stem for f in saves_dir.glob("*.json")]

        project.list_saves = list_saves

        return project

    def test_save_game_success(self, mock_project):
        """Test saving a game successfully"""
        manager = SaveGameManager(mock_project)

        world = World()
        entity = world.create_entity("TestEntity")
        entity.add_component(Transform(x=50, y=100))

        result = manager.save_game("test_save", world, metadata={"level": 5})

        assert result is True

        # Verify file was created
        save_path = mock_project.get_save_path("test_save")
        assert save_path.exists()

        # Verify file contents
        with open(save_path, "r") as f:
            data = json.load(f)

        assert data["version"] == "1.0"
        assert data["project"] == "TestGame"
        assert data["metadata"]["level"] == 5
        assert len(data["world"]["entities"]) == 1

    def test_save_game_with_exception(self, mock_project, capsys, tmp_path):
        """Test save_game handles exceptions"""
        manager = SaveGameManager(mock_project)

        # Mock get_save_path to return an invalid path (directory that doesn't exist)
        def failing_path(save_name):
            return tmp_path / "nonexistent_dir" / f"{save_name}.json"

        mock_project.get_save_path = failing_path

        world = World()
        result = manager.save_game("test_save", world)

        assert result is False
        captured = capsys.readouterr()
        assert "Error saving game" in captured.out

    def test_load_game_success(self, mock_project, capsys):
        """Test loading a game successfully"""
        manager = SaveGameManager(mock_project)

        # First save a game
        world1 = World()
        entity = world1.create_entity("SavedEntity")
        entity.add_component(GridPosition(grid_x=10, grid_y=20))
        entity.add_tag("saved")

        manager.save_game("load_test", world1)

        # Now load it
        world2 = manager.load_game("load_test")

        assert world2 is not None
        assert len(world2.get_entities()) == 1

        saved_entities = world2.get_entities_with_tag("saved")
        assert len(saved_entities) == 1

        captured = capsys.readouterr()
        assert "Game loaded" in captured.out

    def test_load_game_not_found(self, mock_project, capsys):
        """Test loading non-existent save file"""
        manager = SaveGameManager(mock_project)

        world = manager.load_game("nonexistent")

        assert world is None
        captured = capsys.readouterr()
        assert "Save file not found" in captured.out

    def test_load_game_with_exception(self, mock_project, capsys):
        """Test load_game handles exceptions"""
        manager = SaveGameManager(mock_project)

        # Create invalid JSON file
        save_path = mock_project.get_save_path("corrupt_save")
        with open(save_path, "w") as f:
            f.write("{ invalid json")

        world = manager.load_game("corrupt_save")

        assert world is None
        captured = capsys.readouterr()
        assert "Error loading game" in captured.out

    def test_list_saves(self, mock_project):
        """Test listing save files"""
        manager = SaveGameManager(mock_project)

        # Create multiple saves
        world = World()
        manager.save_game("save1", world)
        manager.save_game("save2", world)
        manager.save_game("save3", world)

        saves = manager.list_saves()

        assert len(saves) == 3
        assert "save1" in saves
        assert "save2" in saves
        assert "save3" in saves

    def test_delete_save_success(self, mock_project, capsys):
        """Test deleting a save file"""
        manager = SaveGameManager(mock_project)

        # Create a save
        world = World()
        manager.save_game("to_delete", world)

        # Delete it
        result = manager.delete_save("to_delete")

        assert result is True

        # Verify it's gone
        save_path = mock_project.get_save_path("to_delete")
        assert not save_path.exists()

        captured = capsys.readouterr()
        assert "Deleted save" in captured.out

    def test_delete_save_not_found(self, mock_project):
        """Test deleting non-existent save"""
        manager = SaveGameManager(mock_project)

        result = manager.delete_save("nonexistent")

        assert result is False

    def test_get_save_info(self, mock_project):
        """Test getting save file information"""
        manager = SaveGameManager(mock_project)

        # Create a save with metadata
        world = World()
        world.create_entity("Entity1")
        world.create_entity("Entity2")

        manager.save_game("info_test", world, metadata={"player_name": "Hero", "level": 10})

        # Get info
        info = manager.get_save_info("info_test")

        assert info is not None
        assert info["name"] == "info_test"
        assert info["project"] == "TestGame"
        assert info["metadata"]["player_name"] == "Hero"
        assert info["entity_count"] == 2

    def test_get_save_info_not_found(self, mock_project):
        """Test get_save_info for non-existent save"""
        manager = SaveGameManager(mock_project)

        info = manager.get_save_info("nonexistent")

        assert info is None


class TestAutoSaveManager:
    """Test suite for AutoSaveManager"""

    @pytest.fixture
    def save_manager(self, tmp_path):
        """Create a SaveGameManager for testing"""
        project_dir = tmp_path / "auto_save_project"
        project_dir.mkdir()
        saves_dir = project_dir / "saves"
        saves_dir.mkdir()

        project = Project(str(project_dir))

        metadata = ProjectMetadata(
            name="AutoSaveTest",
            version="1.0.0",
            description="Auto save test",
            author="Test Author",
        )
        project.config = ProjectConfig(metadata=metadata)

        def get_save_path(save_name):
            return saves_dir / f"{save_name}.json"

        project.get_save_path = get_save_path

        def list_saves():
            return [f.stem for f in saves_dir.glob("*.json")]

        project.list_saves = list_saves

        return SaveGameManager(project)

    def test_init(self, save_manager):
        """Test AutoSaveManager initialization"""
        auto_save = AutoSaveManager(save_manager, interval=120)

        assert auto_save.save_manager is save_manager
        assert auto_save.interval == 120
        assert auto_save.last_save_time == 0
        assert auto_save.auto_save_count == 0
        assert auto_save.max_auto_saves == 3

    def test_update_before_interval(self, save_manager):
        """Test update before interval doesn't save"""
        auto_save = AutoSaveManager(save_manager, interval=300)
        world = World()

        auto_save.update(world, 100.0)  # Only 100 seconds

        # No auto-save should have been created
        saves = save_manager.list_saves()
        assert len(saves) == 0

    def test_update_after_interval(self, save_manager, capsys):
        """Test update after interval triggers auto-save"""
        auto_save = AutoSaveManager(save_manager, interval=100)
        world = World()
        world.create_entity("TestEntity")

        auto_save.update(world, 150.0)  # 150 > 100, should trigger

        # Auto-save should have been created
        saves = save_manager.list_saves()
        assert len(saves) == 1
        assert "autosave_0" in saves

        captured = capsys.readouterr()
        assert "Auto-saved" in captured.out

    def test_update_multiple_intervals(self, save_manager):
        """Test multiple auto-saves"""
        auto_save = AutoSaveManager(save_manager, interval=100)
        world = World()

        # Trigger 3 auto-saves
        auto_save.update(world, 150.0)
        auto_save.update(world, 250.0)
        auto_save.update(world, 350.0)

        saves = save_manager.list_saves()
        assert len(saves) == 3

    def test_auto_save_rotation(self, save_manager):
        """Test auto-save rotation (max 3 saves)"""
        auto_save = AutoSaveManager(save_manager, interval=100)
        world = World()

        # Trigger 5 auto-saves (more than max_auto_saves=3)
        for i in range(5):
            auto_save.update(world, 150.0 + (i * 100))

        # Should have autosave_0, autosave_1, autosave_2 (rotating)
        saves = save_manager.list_saves()
        assert "autosave_0" in saves
        assert "autosave_1" in saves
        assert "autosave_2" in saves

    def test_perform_auto_save(self, save_manager):
        """Test _perform_auto_save directly"""
        auto_save = AutoSaveManager(save_manager, interval=100)
        world = World()
        world.create_entity("AutoSavedEntity")

        auto_save._perform_auto_save(world)

        # Verify save was created
        info = save_manager.get_save_info("autosave_0")
        assert info is not None
        assert info["metadata"]["type"] == "auto_save"
        assert info["entity_count"] == 1


class TestIntegration:
    """Integration tests for serialization system"""

    def test_complete_save_load_workflow(self, tmp_path):
        """Test complete save and load workflow"""
        # Setup project
        project_dir = tmp_path / "integration_test"
        project_dir.mkdir()
        saves_dir = project_dir / "saves"
        saves_dir.mkdir()

        project = Project(str(project_dir))

        metadata = ProjectMetadata(
            name="IntegrationTest",
            version="1.0.0",
            description="Integration test",
            author="Test Author",
        )
        project.config = ProjectConfig(metadata=metadata)

        def get_save_path(save_name):
            return saves_dir / f"{save_name}.json"

        project.get_save_path = get_save_path

        def list_saves():
            return [f.stem for f in saves_dir.glob("*.json")]

        project.list_saves = list_saves

        manager = SaveGameManager(project)

        # Create complex world
        world1 = World()

        player = world1.create_entity("Player")
        player.add_component(Transform(x=100, y=200))
        player.add_component(Health(current=80, maximum=100))
        player.add_component(Survival(hunger=75, thirst=60, energy=90))
        player.add_tag("player")

        enemy = world1.create_entity("Enemy")
        enemy.add_component(GridPosition(grid_x=15, grid_y=20))
        enemy.add_component(Health(current=50, maximum=50))
        enemy.add_tag("enemy")

        building = world1.create_entity("House")
        building.add_component(
            Building(building_type="house", construction_progress=1.0, is_constructed=True)
        )

        # Save
        manager.save_game("integration_save", world1, metadata={"chapter": 3})

        # Load
        world2 = manager.load_game("integration_save")

        # Verify everything restored correctly
        assert len(world2.get_entities()) == 3

        restored_player = world2.get_entities_with_tag("player")[0]
        assert restored_player.has_component(Transform)
        assert restored_player.has_component(Health)
        assert restored_player.has_component(Survival)

        health = restored_player.get_component(Health)
        assert health.current == 80
        assert health.maximum == 100
