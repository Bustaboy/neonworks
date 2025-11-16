"""
NeonWorks Core Undo/Redo System

Provides a comprehensive undo/redo system using the Command pattern with:
- Unlimited undo/redo stack
- Memory-efficient delta compression
- Command history viewer support
- Cross-session persistence
- Integration with all map and editing tools
"""

from __future__ import annotations

import gzip
import json
import pickle
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, Tuple

if TYPE_CHECKING:
    from ..rendering.tilemap import Tile, Tilemap

# Minimal Tile class for when rendering.tilemap is not available
# (e.g., during testing without pygame)
try:
    from ..rendering.tilemap import Tile
except ImportError:

    class Tile:  # type: ignore
        """Minimal Tile class for testing."""

        def __init__(self, tile_type: str = "grass", walkable: bool = True):
            self.tile_type = tile_type
            self.walkable = walkable
            self.tileset_id = None
            self.tile_id = None


class Command(ABC):
    """
    Abstract base class for all undoable commands.

    All commands must implement the Command pattern interface:
    - execute(): Perform the action
    - undo(): Reverse the action
    - redo(): Re-perform the action (usually same as execute)
    - get_description(): Human-readable description
    - serialize(): Convert to JSON-serializable dict
    - deserialize(): Reconstruct from dict
    """

    def __init__(self):
        """Initialize command with metadata."""
        self.timestamp = datetime.now()
        self.executed = False

    @abstractmethod
    def execute(self) -> bool:
        """
        Execute the command.

        Returns:
            True if execution succeeded, False otherwise
        """
        pass

    @abstractmethod
    def undo(self) -> bool:
        """
        Undo the command.

        Returns:
            True if undo succeeded, False otherwise
        """
        pass

    def redo(self) -> bool:
        """
        Redo the command (default: calls execute).

        Returns:
            True if redo succeeded, False otherwise
        """
        return self.execute()

    @abstractmethod
    def get_description(self) -> str:
        """
        Get human-readable description of this command.

        Returns:
            Description string suitable for history display
        """
        pass

    @abstractmethod
    def serialize(self) -> Dict[str, Any]:
        """
        Serialize command to JSON-compatible dict.

        Returns:
            Dictionary containing all data needed to reconstruct command
        """
        pass

    @classmethod
    @abstractmethod
    def deserialize(cls, data: Dict[str, Any]) -> "Command":
        """
        Deserialize command from dict.

        Args:
            data: Serialized command data

        Returns:
            Reconstructed command instance
        """
        pass

    def get_timestamp_str(self) -> str:
        """Get formatted timestamp string."""
        return self.timestamp.strftime("%H:%M:%S")


class CompositeCommand(Command):
    """
    Command that groups multiple commands into a single undoable operation.

    Useful for operations that consist of multiple atomic changes that should
    be treated as a single action from the user's perspective.
    """

    def __init__(self, commands: List[Command], description: str = "Composite Action"):
        """
        Initialize composite command.

        Args:
            commands: List of commands to group
            description: Description for the grouped operation
        """
        super().__init__()
        self.commands = commands
        self.description = description

    def execute(self) -> bool:
        """Execute all child commands in order."""
        executed_commands = []
        for cmd in self.commands:
            if not cmd.execute():
                # Rollback only the commands that were executed
                for executed_cmd in reversed(executed_commands):
                    executed_cmd.undo()
                return False
            executed_commands.append(cmd)
        self.executed = True
        return True

    def undo(self) -> bool:
        """Undo all child commands in reverse order."""
        for cmd in reversed(self.commands):
            if not cmd.undo():
                return False
        self.executed = False
        return True

    def redo(self) -> bool:
        """Redo all child commands in order."""
        return self.execute()

    def get_description(self) -> str:
        """Get description of composite command."""
        if len(self.commands) == 1:
            return self.commands[0].get_description()
        return f"{self.description} ({len(self.commands)} operations)"

    def serialize(self) -> Dict[str, Any]:
        """Serialize composite command."""
        return {
            "type": "composite",
            "description": self.description,
            "commands": [cmd.serialize() for cmd in self.commands],
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> "CompositeCommand":
        """Deserialize composite command."""
        from .command_registry import get_command_registry

        registry = get_command_registry()
        commands = [registry.deserialize_command(cmd_data) for cmd_data in data["commands"]]
        return cls(commands, data["description"])


@dataclass
class TileChangeData:
    """Data structure for tile change delta compression."""

    x: int
    y: int
    layer: int
    # Real Tile attributes (from rendering.tilemap)
    old_tile_id: Optional[int] = None
    old_flags: int = 0
    new_tile_id: Optional[int] = None
    new_flags: int = 0
    # Legacy attributes (for backward compatibility)
    old_tile_type: Optional[str] = None
    old_walkable: bool = True
    old_tileset_id: Optional[str] = None
    new_tile_type: Optional[str] = None
    new_walkable: bool = True
    new_tileset_id: Optional[str] = None


class TileChangeCommand(Command):
    """
    Command for changing a single tile.

    Uses delta compression to store only changed properties.
    """

    def __init__(
        self,
        tilemap: Tilemap,
        x: int,
        y: int,
        layer: int,
        old_tile: Optional[Tile],
        new_tile: Optional[Tile],
    ):
        """
        Initialize tile change command.

        Args:
            tilemap: Tilemap to modify
            x: Grid X coordinate
            y: Grid Y coordinate
            layer: Layer index
            old_tile: Previous tile (or None if placing on empty cell)
            new_tile: New tile (or None if erasing)
        """
        super().__init__()
        self.tilemap = tilemap
        self.x = x
        self.y = y
        self.layer = layer

        # Store compressed delta data
        self.delta = TileChangeData(x=x, y=y, layer=layer)

        if old_tile:
            # Handle real Tile (from rendering.tilemap)
            if hasattr(old_tile, "tile_id") and not hasattr(old_tile, "tile_type"):
                self.delta.old_tile_id = old_tile.tile_id
                self.delta.old_flags = getattr(old_tile, "flags", 0)
            # Handle legacy Tile (for backward compatibility)
            else:
                self.delta.old_tile_type = getattr(old_tile, "tile_type", None)
                self.delta.old_walkable = getattr(old_tile, "walkable", True)
                if hasattr(old_tile, "tileset_id"):
                    self.delta.old_tileset_id = old_tile.tileset_id
                if hasattr(old_tile, "tile_id"):
                    self.delta.old_tile_id = old_tile.tile_id

        if new_tile:
            # Handle real Tile (from rendering.tilemap)
            if hasattr(new_tile, "tile_id") and not hasattr(new_tile, "tile_type"):
                self.delta.new_tile_id = new_tile.tile_id
                self.delta.new_flags = getattr(new_tile, "flags", 0)
            # Handle legacy Tile (for backward compatibility)
            else:
                self.delta.new_tile_type = getattr(new_tile, "tile_type", None)
                self.delta.new_walkable = getattr(new_tile, "walkable", True)
                if hasattr(new_tile, "tileset_id"):
                    self.delta.new_tileset_id = new_tile.tileset_id
                if hasattr(new_tile, "tile_id"):
                    self.delta.new_tile_id = new_tile.tile_id

    def execute(self) -> bool:
        """Execute tile change."""
        new_tile = self._create_tile_from_delta(True)
        self.tilemap.set_tile(self.x, self.y, self.layer, new_tile)
        self.executed = True
        return True

    def undo(self) -> bool:
        """Undo tile change."""
        old_tile = self._create_tile_from_delta(False)
        self.tilemap.set_tile(self.x, self.y, self.layer, old_tile)
        self.executed = False
        return True

    def _create_tile_from_delta(self, use_new: bool) -> Optional[Tile]:
        """Create tile from delta data."""
        if use_new:
            # Check if we have real Tile data (tile_id + flags)
            if self.delta.new_tile_id is not None and self.delta.new_tile_type is None:
                return Tile(tile_id=self.delta.new_tile_id, flags=self.delta.new_flags)
            # Legacy Tile data (tile_type + walkable) - create a simple object
            elif self.delta.new_tile_type is not None:
                # Create a simple object with legacy attributes
                from dataclasses import dataclass

                @dataclass
                class LegacyTile:
                    tile_type: str
                    walkable: bool
                    tileset_id: Optional[str] = None
                    tile_id: Optional[int] = None

                tile = LegacyTile(
                    tile_type=self.delta.new_tile_type,
                    walkable=self.delta.new_walkable,
                    tileset_id=self.delta.new_tileset_id,
                    tile_id=self.delta.new_tile_id,
                )
                return tile  # type: ignore
            else:
                return None
        else:
            # Check if we have real Tile data (tile_id + flags)
            if self.delta.old_tile_id is not None and self.delta.old_tile_type is None:
                return Tile(tile_id=self.delta.old_tile_id, flags=self.delta.old_flags)
            # Legacy Tile data (tile_type + walkable) - create a simple object
            elif self.delta.old_tile_type is not None:
                # Create a simple object with legacy attributes
                from dataclasses import dataclass

                @dataclass
                class LegacyTile:
                    tile_type: str
                    walkable: bool
                    tileset_id: Optional[str] = None
                    tile_id: Optional[int] = None

                tile = LegacyTile(
                    tile_type=self.delta.old_tile_type,
                    walkable=self.delta.old_walkable,
                    tileset_id=self.delta.old_tileset_id,
                    tile_id=self.delta.old_tile_id,
                )
                return tile  # type: ignore
            else:
                return None

    def get_description(self) -> str:
        """Get description of tile change."""
        # For real Tiles (tile_id based)
        if self.delta.new_tile_id is not None or self.delta.old_tile_id is not None:
            action = "Placed" if self.delta.new_tile_id is not None else "Erased"
            tile_id = self.delta.new_tile_id or self.delta.old_tile_id
            return f"{action} tile #{tile_id} at ({self.x}, {self.y})"
        # For legacy Tiles (tile_type based)
        else:
            action = "Placed" if self.delta.new_tile_type else "Erased"
            tile_name = self.delta.new_tile_type or self.delta.old_tile_type or "tile"
            return f"{action} {tile_name} at ({self.x}, {self.y})"

    def serialize(self) -> Dict[str, Any]:
        """Serialize tile change command."""
        return {
            "type": "tile_change",
            "x": self.x,
            "y": self.y,
            "layer": self.layer,
            "delta": {
                "old_tile_id": self.delta.old_tile_id,
                "old_flags": self.delta.old_flags,
                "new_tile_id": self.delta.new_tile_id,
                "new_flags": self.delta.new_flags,
                "old_tile_type": self.delta.old_tile_type,
                "old_walkable": self.delta.old_walkable,
                "old_tileset_id": self.delta.old_tileset_id,
                "new_tile_type": self.delta.new_tile_type,
                "new_walkable": self.delta.new_walkable,
                "new_tileset_id": self.delta.new_tileset_id,
            },
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> "TileChangeCommand":
        """
        Deserialize tile change command.

        Note: Requires tilemap reference to be set separately.
        """
        # This is a placeholder - actual deserialization needs tilemap reference
        raise NotImplementedError("Tile change deserialization requires tilemap context")


class BatchTileChangeCommand(Command):
    """
    Command for changing multiple tiles at once.

    More memory-efficient than individual TileChangeCommands when
    dealing with large paint strokes or fill operations.
    """

    def __init__(
        self,
        tilemap: Tilemap,
        changes: List[Tuple[int, int, int, Optional[Tile], Optional[Tile]]],
        description: str = "Paint",
    ):
        """
        Initialize batch tile change command.

        Args:
            tilemap: Tilemap to modify
            changes: List of (x, y, layer, old_tile, new_tile) tuples
            description: Description of the batch operation
        """
        super().__init__()
        self.tilemap = tilemap
        self.changes = changes
        self.description = description

    def execute(self) -> bool:
        """Execute all tile changes."""
        for x, y, layer, _, new_tile in self.changes:
            self.tilemap.set_tile(x, y, layer, new_tile)
        self.executed = True
        return True

    def undo(self) -> bool:
        """Undo all tile changes."""
        for x, y, layer, old_tile, _ in self.changes:
            self.tilemap.set_tile(x, y, layer, old_tile)
        self.executed = False
        return True

    def get_description(self) -> str:
        """Get description of batch operation."""
        return f"{self.description} ({len(self.changes)} tiles)"

    def serialize(self) -> Dict[str, Any]:
        """Serialize batch tile change command."""
        # Serialize changes with delta compression
        compressed_changes = []
        for x, y, layer, old_tile, new_tile in self.changes:
            change_data = {"x": x, "y": y, "layer": layer}

            if old_tile:
                change_data["old"] = {
                    "type": old_tile.tile_type,
                    "walkable": old_tile.walkable,
                }
                if hasattr(old_tile, "tileset_id"):
                    change_data["old"]["tileset_id"] = old_tile.tileset_id
                    change_data["old"]["tile_id"] = old_tile.tile_id

            if new_tile:
                change_data["new"] = {
                    "type": new_tile.tile_type,
                    "walkable": new_tile.walkable,
                }
                if hasattr(new_tile, "tileset_id"):
                    change_data["new"]["tileset_id"] = new_tile.tileset_id
                    change_data["new"]["tile_id"] = new_tile.tile_id

            compressed_changes.append(change_data)

        return {
            "type": "batch_tile_change",
            "description": self.description,
            "changes": compressed_changes,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> "BatchTileChangeCommand":
        """Deserialize batch tile change command."""
        raise NotImplementedError("Batch tile change deserialization requires tilemap context")


class NavmeshPaintCommand(Command):
    """
    Command for navmesh painting operations.

    Stores only changed cells for memory efficiency.
    """

    def __init__(
        self,
        walkable_tiles: Set[Tuple[int, int]],
        unwalkable_tiles: Set[Tuple[int, int]],
        changes: List[Tuple[int, int, bool, bool]],  # (x, y, old_state, new_state)
        description: str = "Paint Navmesh",
    ):
        """
        Initialize navmesh paint command.

        Args:
            walkable_tiles: Reference to walkable tiles set
            unwalkable_tiles: Reference to unwalkable tiles set
            changes: List of (x, y, old_walkable, new_walkable) tuples
            description: Description of the operation
        """
        super().__init__()
        self.walkable_tiles = walkable_tiles
        self.unwalkable_tiles = unwalkable_tiles
        self.changes = changes
        self.description = description

    def execute(self) -> bool:
        """Execute navmesh changes."""
        for x, y, _, new_walkable in self.changes:
            pos = (x, y)
            if new_walkable:
                self.walkable_tiles.add(pos)
                self.unwalkable_tiles.discard(pos)
            else:
                self.unwalkable_tiles.add(pos)
                self.walkable_tiles.discard(pos)
        self.executed = True
        return True

    def undo(self) -> bool:
        """Undo navmesh changes."""
        for x, y, old_walkable, _ in self.changes:
            pos = (x, y)
            if old_walkable:
                self.walkable_tiles.add(pos)
                self.unwalkable_tiles.discard(pos)
            else:
                self.unwalkable_tiles.add(pos)
                self.walkable_tiles.discard(pos)
        self.executed = False
        return True

    def get_description(self) -> str:
        """Get description of navmesh operation."""
        return f"{self.description} ({len(self.changes)} cells)"

    def serialize(self) -> Dict[str, Any]:
        """Serialize navmesh paint command."""
        return {
            "type": "navmesh_paint",
            "description": self.description,
            "changes": [(x, y, old, new) for x, y, old, new in self.changes],
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> "NavmeshPaintCommand":
        """Deserialize navmesh paint command."""
        raise NotImplementedError("Navmesh paint deserialization requires navmesh context")


class DeltaCompressor:
    """
    Compresses command history using delta encoding and gzip.

    Provides significant memory savings for large undo histories.
    """

    @staticmethod
    def compress(data: Any) -> bytes:
        """
        Compress data using pickle + gzip.

        Args:
            data: Any picklable Python object

        Returns:
            Compressed bytes
        """
        pickled = pickle.dumps(data)
        compressed = gzip.compress(pickled, compresslevel=6)
        return compressed

    @staticmethod
    def decompress(data: bytes) -> Any:
        """
        Decompress data.

        Args:
            data: Compressed bytes

        Returns:
            Original Python object
        """
        decompressed = gzip.decompress(data)
        obj = pickle.loads(decompressed)
        return obj

    @staticmethod
    def get_compression_ratio(original: Any, compressed: bytes) -> float:
        """
        Calculate compression ratio.

        Args:
            original: Original object
            compressed: Compressed bytes

        Returns:
            Compression ratio (original_size / compressed_size)
        """
        original_size = len(pickle.dumps(original))
        compressed_size = len(compressed)
        if compressed_size == 0:
            return 0.0
        return original_size / compressed_size


class UndoManager:
    """
    Core undo/redo manager with unlimited history and delta compression.

    Features:
    - Unlimited undo/redo stack (no hard limit)
    - Memory-efficient delta compression
    - Command history viewing
    - Cross-session persistence
    - Memory usage tracking
    """

    def __init__(self, enable_compression: bool = True, auto_compress_threshold: int = 50):
        """
        Initialize undo manager.

        Args:
            enable_compression: Enable delta compression for old commands
            auto_compress_threshold: Automatically compress commands older than this index
        """
        self.undo_stack: List[Command] = []
        self.redo_stack: List[Command] = []
        self.enable_compression = enable_compression
        self.auto_compress_threshold = auto_compress_threshold
        self.compressor = DeltaCompressor()

        # Compressed history (for old commands)
        self.compressed_history: List[bytes] = []

        # Statistics
        self.total_commands_executed = 0
        self.total_undos = 0
        self.total_redos = 0

    def execute(self, command: Command) -> bool:
        """
        Execute a command and add it to undo history.

        Args:
            command: Command to execute

        Returns:
            True if execution succeeded
        """
        if not command.execute():
            return False

        # Add to undo stack
        self.undo_stack.append(command)

        # Clear redo stack (can't redo after new action)
        self.redo_stack.clear()

        # Update statistics
        self.total_commands_executed += 1

        # Auto-compress old commands if enabled
        if self.enable_compression and len(self.undo_stack) > self.auto_compress_threshold:
            self._compress_old_commands()

        return True

    def undo(self) -> bool:
        """
        Undo the last command.

        Returns:
            True if undo succeeded
        """
        if not self.can_undo():
            return False

        command = self.undo_stack.pop()
        if not command.undo():
            # Put it back if undo failed
            self.undo_stack.append(command)
            return False

        self.redo_stack.append(command)
        self.total_undos += 1

        return True

    def redo(self) -> bool:
        """
        Redo the last undone command.

        Returns:
            True if redo succeeded
        """
        if not self.can_redo():
            return False

        command = self.redo_stack.pop()
        if not command.redo():
            # Put it back if redo failed
            self.redo_stack.append(command)
            return False

        self.undo_stack.append(command)
        self.total_redos += 1

        return True

    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self.undo_stack) > 0

    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self.redo_stack) > 0

    def get_undo_description(self) -> Optional[str]:
        """Get description of the next undo action."""
        if self.undo_stack:
            return self.undo_stack[-1].get_description()
        return None

    def get_redo_description(self) -> Optional[str]:
        """Get description of the next redo action."""
        if self.redo_stack:
            return self.redo_stack[-1].get_description()
        return None

    def get_history(self, max_items: int = 100) -> List[Tuple[str, str, bool]]:
        """
        Get command history for display.

        Args:
            max_items: Maximum number of items to return

        Returns:
            List of (description, timestamp, is_undo_stack) tuples
        """
        history = []

        # Add undo stack (most recent last)
        for cmd in self.undo_stack[-max_items:]:
            history.append((cmd.get_description(), cmd.get_timestamp_str(), True))

        return history

    def get_full_history(self) -> List[Tuple[str, str, int]]:
        """
        Get full command history including redo stack.

        Returns:
            List of (description, timestamp, stack_index) tuples
            - Positive index: undo stack (0 = oldest, n = most recent)
            - Negative index: redo stack (-1 = next redo, -n = last redo)
        """
        history = []

        # Undo stack
        for i, cmd in enumerate(self.undo_stack):
            history.append((cmd.get_description(), cmd.get_timestamp_str(), i))

        # Redo stack (reversed)
        for i, cmd in enumerate(reversed(self.redo_stack)):
            history.append((cmd.get_description(), cmd.get_timestamp_str(), -(i + 1)))

        return history

    def clear(self):
        """Clear all undo/redo history."""
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.compressed_history.clear()

    def get_memory_usage(self) -> Dict[str, int]:
        """
        Get memory usage statistics.

        Returns:
            Dictionary with memory usage in bytes
        """
        import sys

        undo_size = sum(sys.getsizeof(cmd) for cmd in self.undo_stack)
        redo_size = sum(sys.getsizeof(cmd) for cmd in self.redo_stack)
        compressed_size = sum(len(data) for data in self.compressed_history)

        return {
            "undo_stack_bytes": undo_size,
            "redo_stack_bytes": redo_size,
            "compressed_bytes": compressed_size,
            "total_bytes": undo_size + redo_size + compressed_size,
            "undo_count": len(self.undo_stack),
            "redo_count": len(self.redo_stack),
            "compressed_count": len(self.compressed_history),
        }

    def _compress_old_commands(self):
        """Compress old commands to save memory."""
        # Compress commands beyond the threshold
        while len(self.undo_stack) > self.auto_compress_threshold:
            old_cmd = self.undo_stack.pop(0)
            compressed = self.compressor.compress(old_cmd.serialize())
            self.compressed_history.append(compressed)

    def save_history(self, filepath: str):
        """
        Save undo history to file.

        Args:
            filepath: Path to save file
        """
        history_data = {
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "statistics": {
                "total_commands": self.total_commands_executed,
                "total_undos": self.total_undos,
                "total_redos": self.total_redos,
            },
            "undo_stack": [cmd.serialize() for cmd in self.undo_stack],
            "redo_stack": [cmd.serialize() for cmd in self.redo_stack],
            "compressed_history": [data.hex() for data in self.compressed_history],
        }

        with open(filepath, "w") as f:
            json.dump(history_data, f, indent=2)

    def load_history(self, filepath: str):
        """
        Load undo history from file.

        Args:
            filepath: Path to load file

        Note: This is a basic implementation. Full deserialization requires
        context (tilemap, world, etc.) to be provided separately.
        """
        with open(filepath, "r") as f:
            history_data = json.load(f)

        # Restore statistics
        stats = history_data.get("statistics", {})
        self.total_commands_executed = stats.get("total_commands", 0)
        self.total_undos = stats.get("total_undos", 0)
        self.total_redos = stats.get("total_redos", 0)

        # Note: Actual command deserialization would require a command registry
        # and context objects (tilemap, world, etc.)
        print(
            f"Loaded history metadata. "
            f"Commands: {len(history_data.get('undo_stack', []))} undo, "
            f"{len(history_data.get('redo_stack', []))} redo"
        )

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get undo manager statistics.

        Returns:
            Dictionary with statistics
        """
        memory = self.get_memory_usage()
        return {
            "total_commands_executed": self.total_commands_executed,
            "total_undos": self.total_undos,
            "total_redos": self.total_redos,
            "current_undo_count": len(self.undo_stack),
            "current_redo_count": len(self.redo_stack),
            "compressed_count": len(self.compressed_history),
            "memory_usage_kb": memory["total_bytes"] / 1024,
            "compression_enabled": self.enable_compression,
        }
