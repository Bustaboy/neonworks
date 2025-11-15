"""
Command Registry for Undo/Redo System

Provides a centralized registry for all command types to enable
serialization and deserialization of undo history.
"""

from typing import Any, Callable, Dict, Type

from .undo_manager import Command


class CommandRegistry:
    """
    Registry for command types.

    Allows commands to be serialized and deserialized by type name.
    """

    def __init__(self):
        """Initialize command registry."""
        self._command_types: Dict[str, Type[Command]] = {}
        self._deserializers: Dict[str, Callable] = {}

    def register(
        self, command_type: str, command_class: Type[Command], deserializer: Callable = None
    ):
        """
        Register a command type.

        Args:
            command_type: Unique type identifier (e.g., "tile_change")
            command_class: Command class
            deserializer: Optional custom deserializer function
        """
        self._command_types[command_type] = command_class

        if deserializer:
            self._deserializers[command_type] = deserializer
        elif hasattr(command_class, "deserialize"):
            self._deserializers[command_type] = command_class.deserialize

    def deserialize_command(self, data: Dict[str, Any]) -> Command:
        """
        Deserialize a command from data.

        Args:
            data: Serialized command data (must include "type" field)

        Returns:
            Deserialized command instance

        Raises:
            ValueError: If command type is not registered
        """
        command_type = data.get("type")
        if not command_type:
            raise ValueError("Command data missing 'type' field")

        if command_type not in self._deserializers:
            raise ValueError(f"Unknown command type: {command_type}")

        deserializer = self._deserializers[command_type]
        return deserializer(data)

    def get_registered_types(self) -> list:
        """Get list of registered command types."""
        return list(self._command_types.keys())


# Global command registry instance
_command_registry = None


def get_command_registry() -> CommandRegistry:
    """
    Get the global command registry instance.

    Returns:
        Global CommandRegistry instance
    """
    global _command_registry
    if _command_registry is None:
        _command_registry = CommandRegistry()
        _register_core_commands(_command_registry)
    return _command_registry


def _register_core_commands(registry: CommandRegistry):
    """Register core command types."""
    from .undo_manager import (
        BatchTileChangeCommand,
        CompositeCommand,
        NavmeshPaintCommand,
        TileChangeCommand,
    )

    # Register core commands
    registry.register("tile_change", TileChangeCommand)
    registry.register("batch_tile_change", BatchTileChangeCommand)
    registry.register("navmesh_paint", NavmeshPaintCommand)
    registry.register("composite", CompositeCommand)
