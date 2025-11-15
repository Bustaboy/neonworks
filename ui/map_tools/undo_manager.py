"""
Undo/Redo system for map editing operations.

Provides a comprehensive undo/redo system that supports all layer operations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from ...rendering.tilemap import Tile, Tilemap
from .settings import ToolLimits


class UndoableAction(ABC):
    """
    Base class for undoable actions.

    Each action must implement undo() and redo() methods.
    """

    @abstractmethod
    def undo(self):
        """Undo this action."""
        pass

    @abstractmethod
    def redo(self):
        """Redo this action."""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Get a human-readable description of this action."""
        pass


class TileChangeAction(UndoableAction):
    """Action for changing a single tile."""

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
        Initialize tile change action.

        Args:
            tilemap: Tilemap to modify
            x: Grid X coordinate
            y: Grid Y coordinate
            layer: Layer index
            old_tile: Previous tile (or None)
            new_tile: New tile (or None)
        """
        self.tilemap = tilemap
        self.x = x
        self.y = y
        self.layer = layer
        self.old_tile = old_tile
        self.new_tile = new_tile

    def undo(self):
        """Undo the tile change."""
        self.tilemap.set_tile(self.x, self.y, self.layer, self.old_tile)

    def redo(self):
        """Redo the tile change."""
        self.tilemap.set_tile(self.x, self.y, self.layer, self.new_tile)

    def get_description(self) -> str:
        """Get description of this action."""
        action = "Placed" if self.new_tile else "Erased"
        return f"{action} tile at ({self.x}, {self.y}) on layer {self.layer}"


class BatchTileChangeAction(UndoableAction):
    """Action for changing multiple tiles at once."""

    def __init__(self, tilemap: Tilemap, changes: List[Tuple[int, int, int, Optional[Tile], Optional[Tile]]]):
        """
        Initialize batch tile change action.

        Args:
            tilemap: Tilemap to modify
            changes: List of (x, y, layer, old_tile, new_tile) tuples
        """
        self.tilemap = tilemap
        self.changes = changes

    def undo(self):
        """Undo all tile changes."""
        for x, y, layer, old_tile, _ in self.changes:
            self.tilemap.set_tile(x, y, layer, old_tile)

    def redo(self):
        """Redo all tile changes."""
        for x, y, layer, _, new_tile in self.changes:
            self.tilemap.set_tile(x, y, layer, new_tile)

    def get_description(self) -> str:
        """Get description of this action."""
        return f"Changed {len(self.changes)} tiles"


class EntityChangeAction(UndoableAction):
    """Action for entity creation/deletion."""

    def __init__(self, world, entity_id: str, operation: str, entity_data: Optional[Dict] = None):
        """
        Initialize entity change action.

        Args:
            world: World instance
            entity_id: Entity ID
            operation: "create" or "delete"
            entity_data: Entity serialization data (for recreation)
        """
        self.world = world
        self.entity_id = entity_id
        self.operation = operation
        self.entity_data = entity_data

    def undo(self):
        """Undo the entity change."""
        if self.operation == "create":
            # Undo creation by deleting
            if self.entity_id in self.world.entities:
                self.world.remove_entity(self.entity_id)
        elif self.operation == "delete":
            # Undo deletion by recreating
            if self.entity_data:
                # Recreate entity from data
                # Note: This requires entity serialization support
                pass

    def redo(self):
        """Redo the entity change."""
        if self.operation == "create":
            # Redo creation
            if self.entity_data:
                pass
        elif self.operation == "delete":
            # Redo deletion
            if self.entity_id in self.world.entities:
                self.world.remove_entity(self.entity_id)

    def get_description(self) -> str:
        """Get description of this action."""
        return f"{self.operation.capitalize()}d entity {self.entity_id}"


class UndoManager:
    """
    Manages undo/redo history for map editing operations.

    Supports multi-level undo/redo with configurable history size.
    """

    def __init__(self, max_history: int = ToolLimits.MAX_UNDO_HISTORY):
        """
        Initialize undo manager.

        Args:
            max_history: Maximum number of actions to keep in history (default from ToolLimits)
        """
        self.max_history = max_history
        self.undo_stack: List[UndoableAction] = []
        self.redo_stack: List[UndoableAction] = []

    def record_action(self, action: UndoableAction):
        """
        Record a new action.

        Args:
            action: UndoableAction to record
        """
        # Add to undo stack
        self.undo_stack.append(action)

        # Clear redo stack (can't redo after new action)
        self.redo_stack.clear()

        # Trim history if needed
        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)

    def undo(self) -> bool:
        """
        Undo the last action.

        Returns:
            True if an action was undone, False if undo stack is empty
        """
        if not self.undo_stack:
            return False

        action = self.undo_stack.pop()
        action.undo()
        self.redo_stack.append(action)

        print(f"Undo: {action.get_description()}")
        return True

    def redo(self) -> bool:
        """
        Redo the last undone action.

        Returns:
            True if an action was redone, False if redo stack is empty
        """
        if not self.redo_stack:
            return False

        action = self.redo_stack.pop()
        action.redo()
        self.undo_stack.append(action)

        print(f"Redo: {action.get_description()}")
        return True

    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self.undo_stack) > 0

    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self.redo_stack) > 0

    def clear(self):
        """Clear all undo/redo history."""
        self.undo_stack.clear()
        self.redo_stack.clear()

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
