"""
Comprehensive tests for Serialization System

Tests component, entity, and world serialization.
"""

import json
import tempfile
from dataclasses import dataclass
from pathlib import Path

import pytest

from neonworks.core.ecs import Component, GridPosition, Transform, World
from neonworks.core.serialization import (
    ComponentSerializer,
    EntitySerializer,
    GameSerializer,
    SerializationError,
    SerializationFormat,
    SerializationMetadata,
    WorldSerializer,
    get_game_serializer,
)


@dataclass
class DummyComponent(Component):
    """Helper component for serialization tests (renamed to avoid pytest collection)"""

    value: int = 0
    name: str = "test"


@dataclass
class ComplexComponent(Component):
    """Complex component with nested data"""

    values: list = None
    settings: dict = None

    def __post_init__(self):
        if self.values is None:
            self.values = []
        if self.settings is None:
            self.settings = {}


class DummyComponentSerializer:
    """Test component serialization"""

    def test_serializer_creation(self):
        """Test creating component serializer"""
        serializer = ComponentSerializer()

        assert len(serializer._component_types) == 0

    def test_register_component_type(self):
        """Test registering component type"""
        serializer = ComponentSerializer()
        serializer.register_component_type(DummyComponent)

        assert "DummyComponent" in serializer._component_types

    def test_serialize_simple_component(self):
        """Test serializing simple component"""
        serializer = ComponentSerializer()
        serializer.register_component_type(DummyComponent)

        component = DummyComponent(value=42, name="hello")
        data = serializer.serialize_component(component)

        assert data["_type"] == "DummyComponent"
        assert data["_data"]["value"] == 42
        assert data["_data"]["name"] == "hello"

    def test_deserialize_simple_component(self):
        """Test deserializing simple component"""
        serializer = ComponentSerializer()
        serializer.register_component_type(DummyComponent)

        data = {"_type": "DummyComponent", "_data": {"value": 99, "name": "world"}}

        component = serializer.deserialize_component(data)

        assert isinstance(component, DummyComponent)
        assert component.value == 99
        assert component.name == "world"

    def test_serialize_complex_component(self):
        """Test serializing component with nested data"""
        serializer = ComponentSerializer()
        serializer.register_component_type(ComplexComponent)

        component = ComplexComponent(values=[1, 2, 3], settings={"key": "value", "count": 10})
        data = serializer.serialize_component(component)

        assert data["_data"]["values"] == [1, 2, 3]
        assert data["_data"]["settings"]["key"] == "value"

    def test_deserialize_complex_component(self):
        """Test deserializing component with nested data"""
        serializer = ComponentSerializer()
        serializer.register_component_type(ComplexComponent)

        data = {
            "_type": "ComplexComponent",
            "_data": {"values": [4, 5, 6], "settings": {"mode": "test", "level": 5}},
        }

        component = serializer.deserialize_component(data)

        assert component.values == [4, 5, 6]
        assert component.settings["mode"] == "test"

    def test_serialize_builtin_components(self):
        """Test serializing built-in components"""
        serializer = ComponentSerializer()
        serializer.register_component_type(Transform)
        serializer.register_component_type(GridPosition)

        transform = Transform(x=100.5, y=200.5)
        data = serializer.serialize_component(transform)

        assert data["_type"] == "Transform"
        assert data["_data"]["x"] == 100.5

        grid_pos = GridPosition(grid_x=5, grid_y=10)
        data = serializer.serialize_component(grid_pos)

        assert data["_type"] == "GridPosition"
        assert data["_data"]["grid_x"] == 5

    def test_deserialize_unknown_component(self):
        """Test deserializing unknown component type"""
        serializer = ComponentSerializer()

        data = {"_type": "UnknownComponent", "_data": {}}

        with pytest.raises(SerializationError, match="Unknown component type"):
            serializer.deserialize_component(data)

    def test_custom_serializer(self):
        """Test custom serializer/deserializer"""
        serializer = ComponentSerializer()
        serializer.register_component_type(DummyComponent)

        # Custom serializer that stores as string
        def custom_ser(comp):
            return {"custom": f"{comp.value}:{comp.name}"}

        def custom_deser(data):
            value, name = data["custom"].split(":")
            return DummyComponent(value=int(value), name=name)

        serializer.register_custom_serializer(DummyComponent, custom_ser, custom_deser)

        component = DummyComponent(value=123, name="custom")
        data = serializer.serialize_component(component)

        assert data["_data"]["custom"] == "123:custom"

        restored = serializer.deserialize_component(data)
        assert restored.value == 123
        assert restored.name == "custom"


class TestEntitySerializer:
    """Test entity serialization"""

    def test_serialize_entity(self):
        """Test serializing entity"""
        world = World()
        entity = world.create_entity()
        entity.add_component(DummyComponent(value=42))

        component_serializer = ComponentSerializer()
        component_serializer.register_component_type(DummyComponent)
        entity_serializer = EntitySerializer(component_serializer)

        data = entity_serializer.serialize_entity(entity)

        assert "id" in data
        assert data["active"]
        assert len(data["components"]) == 1

    def test_deserialize_entity(self):
        """Test deserializing entity"""
        world = World()

        component_serializer = ComponentSerializer()
        component_serializer.register_component_type(DummyComponent)
        entity_serializer = EntitySerializer(component_serializer)

        data = {
            "id": 1,
            "active": True,
            "components": [{"_type": "DummyComponent", "_data": {"value": 99, "name": "test"}}],
            "tags": ["player", "active"],
        }

        entity = entity_serializer.deserialize_entity(data, world)

        assert entity.active
        assert entity.has_tag("player")
        assert entity.has_tag("active")

        component = entity.get_component(DummyComponent)
        assert component is not None
        assert component.value == 99

    def test_serialize_entity_with_multiple_components(self):
        """Test serializing entity with multiple components"""
        world = World()
        entity = world.create_entity()
        entity.add_component(DummyComponent(value=10))
        entity.add_component(Transform(x=50, y=100))

        component_serializer = ComponentSerializer()
        component_serializer.register_component_type(DummyComponent)
        component_serializer.register_component_type(Transform)
        entity_serializer = EntitySerializer(component_serializer)

        data = entity_serializer.serialize_entity(entity)

        assert len(data["components"]) == 2


class TestWorldSerializer:
    """Test world serialization"""

    def test_serialize_world(self):
        """Test serializing world"""
        world = World()
        entity1 = world.create_entity()
        entity1.add_component(DummyComponent(value=1))

        entity2 = world.create_entity()
        entity2.add_component(DummyComponent(value=2))

        component_serializer = ComponentSerializer()
        component_serializer.register_component_type(DummyComponent)
        world_serializer = WorldSerializer(component_serializer)

        data = world_serializer.serialize_world(world)

        assert len(data["entities"]) == 2

    def test_deserialize_world(self):
        """Test deserializing world"""
        component_serializer = ComponentSerializer()
        component_serializer.register_component_type(DummyComponent)
        world_serializer = WorldSerializer(component_serializer)

        data = {
            "entities": [
                {
                    "id": 1,
                    "active": True,
                    "components": [
                        {
                            "_type": "DummyComponent",
                            "_data": {"value": 100, "name": "entity1"},
                        }
                    ],
                    "tags": [],
                },
                {
                    "id": 2,
                    "active": True,
                    "components": [
                        {
                            "_type": "DummyComponent",
                            "_data": {"value": 200, "name": "entity2"},
                        }
                    ],
                    "tags": ["tagged"],
                },
            ],
            "next_entity_id": 3,
        }

        world = world_serializer.deserialize_world(data)

        assert len(world._entities) == 2
        entities = list(world._entities.values())

        comp1 = entities[0].get_component(DummyComponent)
        assert comp1.value == 100

        comp2 = entities[1].get_component(DummyComponent)
        assert comp2.value == 200
        assert entities[1].has_tag("tagged")

    def test_serialize_world_with_metadata(self):
        """Test serializing world with metadata"""
        world = World()
        entity = world.create_entity()
        entity.add_component(DummyComponent(value=42))

        metadata = SerializationMetadata(
            version="1.0",
            timestamp="2024-01-01",
            game_version="0.1.0",
            custom_data={"level": "test_level"},
        )

        component_serializer = ComponentSerializer()
        component_serializer.register_component_type(DummyComponent)
        world_serializer = WorldSerializer(component_serializer)

        data = world_serializer.serialize_world(world, metadata)

        assert "_metadata" in data
        assert data["_metadata"]["version"] == "1.0"
        assert data["_metadata"]["custom_data"]["level"] == "test_level"


class TestGameSerializer:
    """Test game serializer"""

    def test_game_serializer_creation(self):
        """Test creating game serializer"""
        serializer = GameSerializer()

        assert serializer.component_serializer is not None
        assert serializer.world_serializer is not None

    def test_register_component(self):
        """Test registering component"""
        serializer = GameSerializer()
        serializer.register_component(DummyComponent)

        assert "DummyComponent" in serializer.component_serializer._component_types

    def test_register_components(self):
        """Test registering multiple components"""
        serializer = GameSerializer()
        serializer.register_components([DummyComponent, Transform])

        assert "DummyComponent" in serializer.component_serializer._component_types
        assert "Transform" in serializer.component_serializer._component_types

    def test_save_load_game_json(self):
        """Test saving and loading game to JSON"""
        serializer = GameSerializer()
        serializer.register_component(DummyComponent)

        world = World()
        entity = world.create_entity()
        entity.add_component(DummyComponent(value=777))

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            serializer.save_game(world, temp_path, SerializationFormat.JSON)
            loaded_world = serializer.load_game(temp_path, SerializationFormat.JSON)

            entities = list(loaded_world._entities.values())
            assert len(entities) == 1

            component = entities[0].get_component(DummyComponent)
            assert component.value == 777
        finally:
            temp_path.unlink()

    def test_save_load_game_binary(self):
        """Test saving and loading game to binary"""
        serializer = GameSerializer()
        serializer.register_component(DummyComponent)

        world = World()
        entity = world.create_entity()
        entity.add_component(DummyComponent(value=888))

        with tempfile.NamedTemporaryFile(mode="wb", suffix=".dat", delete=False) as f:
            temp_path = Path(f.name)

        try:
            serializer.save_game(world, temp_path, SerializationFormat.BINARY)
            loaded_world = serializer.load_game(temp_path, SerializationFormat.BINARY)

            entities = list(loaded_world._entities.values())
            assert len(entities) == 1

            component = entities[0].get_component(DummyComponent)
            assert component.value == 888
        finally:
            temp_path.unlink()

    def test_save_load_game_string(self):
        """Test saving and loading game to/from string"""
        serializer = GameSerializer()
        serializer.register_component(DummyComponent)

        world = World()
        entity = world.create_entity()
        entity.add_component(DummyComponent(value=999))

        json_str = serializer.save_game_to_string(world)
        loaded_world = serializer.load_game_from_string(json_str)

        entities = list(loaded_world._entities.values())
        assert len(entities) == 1

        component = entities[0].get_component(DummyComponent)
        assert component.value == 999

    def test_get_metadata(self):
        """Test getting metadata from save file"""
        serializer = GameSerializer()
        serializer.register_component(DummyComponent)

        world = World()
        metadata = SerializationMetadata(
            version="2.0", game_version="0.2.0", custom_data={"save_name": "Test Save"}
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            serializer.save_game(world, temp_path, metadata=metadata)
            loaded_metadata = serializer.get_metadata(temp_path)

            assert loaded_metadata is not None
            assert loaded_metadata.version == "2.0"
            assert loaded_metadata.game_version == "0.2.0"
            assert loaded_metadata.custom_data["save_name"] == "Test Save"
        finally:
            temp_path.unlink()


class TestGlobalSerializer:
    """Test global serializer"""

    def test_get_global_serializer(self):
        """Test getting global serializer"""
        serializer1 = get_game_serializer()
        serializer2 = get_game_serializer()

        assert serializer1 is serializer2

    def test_set_global_serializer(self):
        """Test setting global serializer"""
        from neonworks.core.serialization import set_game_serializer

        custom_serializer = GameSerializer()
        set_game_serializer(custom_serializer)

        retrieved = get_game_serializer()
        assert retrieved is custom_serializer


class TestSerializationIntegration:
    """Integration tests for serialization"""

    def test_full_game_save_load(self):
        """Test complete game save and load"""
        serializer = GameSerializer()
        serializer.register_components([DummyComponent, Transform, GridPosition])

        # Create game world
        world = World()

        player = world.create_entity()
        player.add_tag("player")
        player.add_component(Transform(x=100, y=200))
        player.add_component(DummyComponent(value=50, name="player"))

        enemy = world.create_entity()
        enemy.add_tag("enemy")
        enemy.add_component(Transform(x=300, y=400))
        enemy.add_component(DummyComponent(value=30, name="enemy"))

        # Save game
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            metadata = SerializationMetadata(
                game_version="1.0.0", custom_data={"level": "test_level", "score": 1000}
            )
            serializer.save_game(world, temp_path, metadata=metadata)

            # Load game
            loaded_world = serializer.load_game(temp_path)

            # Verify entities
            assert len(loaded_world._entities) == 2

            # Find player
            players = loaded_world.get_entities_with_tag("player")
            assert len(players) == 1
            player_entity = players[0]

            player_transform = player_entity.get_component(Transform)
            assert player_transform.x == 100
            assert player_transform.y == 200

            player_comp = player_entity.get_component(DummyComponent)
            assert player_comp.value == 50
            assert player_comp.name == "player"

            # Find enemy
            enemies = loaded_world.get_entities_with_tag("enemy")
            assert len(enemies) == 1
            enemy_entity = enemies[0]

            enemy_transform = enemy_entity.get_component(Transform)
            assert enemy_transform.x == 300

            # Verify metadata
            loaded_metadata = serializer.get_metadata(temp_path)
            assert loaded_metadata.custom_data["score"] == 1000
        finally:
            temp_path.unlink()


# Run tests with: pytest engine/tests/test_serialization.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
