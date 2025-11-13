"""
Serialization System

Save and load game state with component serialization.
"""

from typing import Any, Dict, Optional, Callable, Type, List
from dataclasses import dataclass, field, fields, is_dataclass
from enum import Enum
import json
import pickle
from pathlib import Path
from engine.core.ecs import Component, Entity, World


class SerializationFormat(Enum):
    """Serialization format types"""
    JSON = "json"
    BINARY = "binary"


@dataclass
class SerializationMetadata:
    """Metadata for saved games"""
    version: str = "1.0"
    timestamp: Optional[str] = None
    game_version: Optional[str] = None
    custom_data: Dict[str, Any] = field(default_factory=dict)


class SerializationError(Exception):
    """Error during serialization/deserialization"""
    pass


class ComponentSerializer:
    """Handles serialization of individual components"""

    def __init__(self):
        # Component type registry
        self._component_types: Dict[str, Type[Component]] = {}

        # Custom serializers for specific component types
        self._custom_serializers: Dict[Type, Callable[[Any], Dict]] = {}
        self._custom_deserializers: Dict[Type, Callable[[Dict], Any]] = {}

    def register_component_type(self, component_class: Type[Component]):
        """
        Register a component type for serialization.

        Args:
            component_class: Component class to register
        """
        type_name = component_class.__name__
        self._component_types[type_name] = component_class

    def register_custom_serializer(self, component_class: Type,
                                   serializer: Callable[[Any], Dict],
                                   deserializer: Callable[[Dict], Any]):
        """
        Register custom serializer/deserializer for a component type.

        Args:
            component_class: Component class
            serializer: Function to serialize component to dict
            deserializer: Function to deserialize dict to component
        """
        self._custom_serializers[component_class] = serializer
        self._custom_deserializers[component_class] = deserializer

    def serialize_component(self, component: Component) -> Dict[str, Any]:
        """
        Serialize a component to dictionary.

        Args:
            component: Component to serialize

        Returns:
            Dictionary representation
        """
        component_type = type(component)
        type_name = component_type.__name__

        # Check for custom serializer
        if component_type in self._custom_serializers:
            data = self._custom_serializers[component_type](component)
            return {
                "_type": type_name,
                "_data": data
            }

        # Default serialization for dataclasses
        if is_dataclass(component):
            data = {}
            for f in fields(component):
                value = getattr(component, f.name)
                data[f.name] = self._serialize_value(value)

            return {
                "_type": type_name,
                "_data": data
            }

        # Fallback for non-dataclass components
        return {
            "_type": type_name,
            "_data": self._serialize_value(component.__dict__)
        }

    def deserialize_component(self, data: Dict[str, Any]) -> Component:
        """
        Deserialize a component from dictionary.

        Args:
            data: Dictionary representation

        Returns:
            Component instance
        """
        type_name = data.get("_type")
        component_data = data.get("_data", {})

        if type_name not in self._component_types:
            raise SerializationError(f"Unknown component type: {type_name}")

        component_class = self._component_types[type_name]

        # Check for custom deserializer
        if component_class in self._custom_deserializers:
            return self._custom_deserializers[component_class](component_data)

        # Default deserialization
        deserialized_data = {}
        for key, value in component_data.items():
            deserialized_data[key] = self._deserialize_value(value)

        return component_class(**deserialized_data)

    def _serialize_value(self, value: Any) -> Any:
        """Serialize a value (handles nested structures)"""
        if value is None:
            return None
        elif isinstance(value, (str, int, float, bool)):
            return value
        elif isinstance(value, Enum):
            return {"_enum": value.__class__.__name__, "_value": value.value}
        elif isinstance(value, (list, tuple)):
            return [self._serialize_value(v) for v in value]
        elif isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        elif is_dataclass(value):
            return {
                "_dataclass": value.__class__.__name__,
                "_fields": {f.name: self._serialize_value(getattr(value, f.name)) for f in fields(value)}
            }
        else:
            # Try to convert to string for unknown types
            return str(value)

    def _deserialize_value(self, value: Any) -> Any:
        """Deserialize a value (handles nested structures)"""
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        elif isinstance(value, dict):
            if "_enum" in value:
                # Enum deserialization would need enum registry
                return value["_value"]
            elif "_dataclass" in value:
                # Basic dataclass deserialization (limited)
                return value["_fields"]
            else:
                return {k: self._deserialize_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._deserialize_value(v) for v in value]
        else:
            return value


class EntitySerializer:
    """Handles serialization of entities"""

    def __init__(self, component_serializer: ComponentSerializer):
        self.component_serializer = component_serializer

    def serialize_entity(self, entity: Entity) -> Dict[str, Any]:
        """
        Serialize an entity.

        Args:
            entity: Entity to serialize

        Returns:
            Dictionary representation
        """
        components = []
        for component in entity._components.values():
            components.append(self.component_serializer.serialize_component(component))

        return {
            "id": entity.id,
            "active": entity.active,
            "components": components,
            "tags": list(entity.tags)
        }

    def deserialize_entity(self, data: Dict[str, Any], world: World) -> Entity:
        """
        Deserialize an entity.

        Args:
            data: Dictionary representation
            world: World to create entity in

        Returns:
            Entity instance
        """
        entity = world.create_entity()
        entity.active = data.get("active", True)

        # Restore tags
        for tag in data.get("tags", []):
            entity.add_tag(tag)
            # Manually update world's tag index since add_tag doesn't do it
            if tag not in world._tags_to_entities:
                world._tags_to_entities[tag] = set()
            world._tags_to_entities[tag].add(entity.id)

        # Restore components
        for component_data in data.get("components", []):
            component = self.component_serializer.deserialize_component(component_data)
            entity.add_component(component)

        return entity


class WorldSerializer:
    """Handles serialization of entire worlds"""

    def __init__(self, component_serializer: ComponentSerializer):
        self.component_serializer = component_serializer
        self.entity_serializer = EntitySerializer(component_serializer)

    def serialize_world(self, world: World, metadata: Optional[SerializationMetadata] = None) -> Dict[str, Any]:
        """
        Serialize a world.

        Args:
            world: World to serialize
            metadata: Optional metadata

        Returns:
            Dictionary representation
        """
        entities = []
        for entity in world._entities.values():
            entities.append(self.entity_serializer.serialize_entity(entity))

        data = {
            "entities": entities
        }

        if metadata:
            data["_metadata"] = {
                "version": metadata.version,
                "timestamp": metadata.timestamp,
                "game_version": metadata.game_version,
                "custom_data": metadata.custom_data
            }

        return data

    def deserialize_world(self, data: Dict[str, Any]) -> World:
        """
        Deserialize a world.

        Args:
            data: Dictionary representation

        Returns:
            World instance
        """
        world = World()

        # Restore entities
        for entity_data in data.get("entities", []):
            self.entity_serializer.deserialize_entity(entity_data, world)

        return world


class GameSerializer:
    """High-level game state serialization"""

    def __init__(self):
        self.component_serializer = ComponentSerializer()
        self.world_serializer = WorldSerializer(self.component_serializer)

    def register_component(self, component_class: Type[Component]):
        """Register a component type"""
        self.component_serializer.register_component_type(component_class)

    def register_components(self, component_classes: List[Type[Component]]):
        """Register multiple component types"""
        for component_class in component_classes:
            self.register_component(component_class)

    def register_custom_serializer(self, component_class: Type,
                                   serializer: Callable[[Any], Dict],
                                   deserializer: Callable[[Dict], Any]):
        """Register custom serializer for a component"""
        self.component_serializer.register_custom_serializer(
            component_class, serializer, deserializer
        )

    def save_game(self, world: World, file_path: Path,
                 format: SerializationFormat = SerializationFormat.JSON,
                 metadata: Optional[SerializationMetadata] = None):
        """
        Save game state to file.

        Args:
            world: World to save
            file_path: Path to save file
            format: Serialization format
            metadata: Optional metadata
        """
        data = self.world_serializer.serialize_world(world, metadata)

        if format == SerializationFormat.JSON:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        elif format == SerializationFormat.BINARY:
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
        else:
            raise SerializationError(f"Unsupported format: {format}")

    def load_game(self, file_path: Path,
                 format: SerializationFormat = SerializationFormat.JSON) -> World:
        """
        Load game state from file.

        Args:
            file_path: Path to load file
            format: Serialization format

        Returns:
            Loaded world
        """
        if format == SerializationFormat.JSON:
            with open(file_path, 'r') as f:
                data = json.load(f)
        elif format == SerializationFormat.BINARY:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
        else:
            raise SerializationError(f"Unsupported format: {format}")

        return self.world_serializer.deserialize_world(data)

    def save_game_to_string(self, world: World,
                           metadata: Optional[SerializationMetadata] = None) -> str:
        """
        Save game state to JSON string.

        Args:
            world: World to save
            metadata: Optional metadata

        Returns:
            JSON string
        """
        data = self.world_serializer.serialize_world(world, metadata)
        return json.dumps(data, indent=2)

    def load_game_from_string(self, json_str: str) -> World:
        """
        Load game state from JSON string.

        Args:
            json_str: JSON string

        Returns:
            Loaded world
        """
        data = json.loads(json_str)
        return self.world_serializer.deserialize_world(data)

    def get_metadata(self, file_path: Path,
                    format: SerializationFormat = SerializationFormat.JSON) -> Optional[SerializationMetadata]:
        """
        Get metadata from save file without loading full game.

        Args:
            file_path: Path to save file
            format: Serialization format

        Returns:
            Metadata if available
        """
        if format == SerializationFormat.JSON:
            with open(file_path, 'r') as f:
                data = json.load(f)
        elif format == SerializationFormat.BINARY:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
        else:
            return None

        metadata_data = data.get("_metadata")
        if metadata_data:
            return SerializationMetadata(
                version=metadata_data.get("version", "1.0"),
                timestamp=metadata_data.get("timestamp"),
                game_version=metadata_data.get("game_version"),
                custom_data=metadata_data.get("custom_data", {})
            )

        return None


# Global game serializer instance
_global_serializer: Optional[GameSerializer] = None


def get_game_serializer() -> GameSerializer:
    """Get or create the global game serializer"""
    global _global_serializer
    if _global_serializer is None:
        _global_serializer = GameSerializer()
    return _global_serializer


def set_game_serializer(serializer: GameSerializer):
    """Set the global game serializer"""
    global _global_serializer
    _global_serializer = serializer
