"""
Tests for the Core Undo/Redo System

Tests the comprehensive undo/redo system including:
- Basic undo/redo operations
- Command pattern implementation
- Delta compression
- Composite commands
- Memory management
- Persistence
"""

import os
import tempfile
from typing import Set, Tuple

import pytest

from neonworks.core.command_registry import get_command_registry
from neonworks.core.undo_manager import (
    BatchTileChangeCommand,
    Command,
    CompositeCommand,
    DeltaCompressor,
    NavmeshPaintCommand,
    TileChangeCommand,
    UndoManager,
)
from neonworks.core.undo_persistence import UndoHistoryPersistence
from neonworks.rendering.tilemap import Tile, Tilemap


class TestUndoManager:
    """Test suite for UndoManager."""

    def test_undo_manager_initialization(self):
        """Test that undo manager initializes correctly."""
        manager = UndoManager()

        assert len(manager.undo_stack) == 0
        assert len(manager.redo_stack) == 0
        assert manager.can_undo() is False
        assert manager.can_redo() is False
        assert manager.enable_compression is True

    def test_undo_manager_no_limit(self):
        """Test that undo manager supports unlimited history."""
        manager = UndoManager()

        # Create a simple test command
        class TestCommand(Command):
            def __init__(self, value):
                super().__init__()
                self.value = value
                self.executed = False

            def execute(self):
                self.executed = True
                return True

            def undo(self):
                self.executed = False
                return True

            def get_description(self):
                return f"Test command {self.value}"

            def serialize(self):
                return {"type": "test", "value": self.value}

            @classmethod
            def deserialize(cls, data):
                return cls(data["value"])

        # Execute 1000 commands
        for i in range(1000):
            cmd = TestCommand(i)
            manager.execute(cmd)

        assert len(manager.undo_stack) == 1000
        assert manager.can_undo() is True

        # Undo all commands
        for i in range(1000):
            assert manager.undo() is True

        assert len(manager.undo_stack) == 0
        assert len(manager.redo_stack) == 1000

    def test_undo_redo_basic(self):
        """Test basic undo/redo operations."""
        manager = UndoManager()

        # Create test command with state
        class CounterCommand(Command):
            counter = 0

            def execute(self):
                CounterCommand.counter += 1
                self.executed = True
                return True

            def undo(self):
                CounterCommand.counter -= 1
                self.executed = False
                return True

            def get_description(self):
                return "Increment counter"

            def serialize(self):
                return {"type": "counter"}

            @classmethod
            def deserialize(cls, data):
                return cls()

        # Execute command
        cmd = CounterCommand()
        manager.execute(cmd)
        assert CounterCommand.counter == 1

        # Undo
        manager.undo()
        assert CounterCommand.counter == 0

        # Redo
        manager.redo()
        assert CounterCommand.counter == 1

    def test_undo_clears_redo_stack(self):
        """Test that new commands clear the redo stack."""
        manager = UndoManager()

        class TestCommand(Command):
            def execute(self):
                return True

            def undo(self):
                return True

            def get_description(self):
                return "Test"

            def serialize(self):
                return {}

            @classmethod
            def deserialize(cls, data):
                return cls()

        # Execute, undo, then execute new command
        manager.execute(TestCommand())
        manager.execute(TestCommand())
        manager.undo()
        manager.undo()

        assert len(manager.redo_stack) == 2

        # Execute new command should clear redo
        manager.execute(TestCommand())
        assert len(manager.redo_stack) == 0


class TestTileChangeCommand:
    """Test suite for TileChangeCommand."""

    def test_tile_change_basic(self):
        """Test basic tile change command."""
        tilemap = Tilemap(width=10, height=10, tile_size=32, layers=3)

        old_tile = Tile("grass", walkable=True)
        new_tile = Tile("water", walkable=False)

        cmd = TileChangeCommand(tilemap, 5, 5, 0, old_tile, new_tile)

        # Set initial tile
        tilemap.set_tile(5, 5, 0, old_tile)

        # Execute command
        cmd.execute()
        result_tile = tilemap.get_tile(5, 5, 0)
        assert result_tile.tile_type == "water"
        assert result_tile.walkable is False

        # Undo command
        cmd.undo()
        result_tile = tilemap.get_tile(5, 5, 0)
        assert result_tile.tile_type == "grass"
        assert result_tile.walkable is True

    def test_tile_change_delta_compression(self):
        """Test that tile change uses delta compression."""
        tilemap = Tilemap(width=10, height=10, tile_size=32, layers=3)

        old_tile = Tile("grass", walkable=True)
        new_tile = Tile("water", walkable=False)

        cmd = TileChangeCommand(tilemap, 5, 5, 0, old_tile, new_tile)

        # Check that delta data is stored
        assert cmd.delta.old_tile_type == "grass"
        assert cmd.delta.old_walkable is True
        assert cmd.delta.new_tile_type == "water"
        assert cmd.delta.new_walkable is False

    def test_tile_change_with_tileset(self):
        """Test tile change with tileset data."""
        tilemap = Tilemap(width=10, height=10, tile_size=32, layers=3)

        old_tile = Tile("grass", walkable=True)
        old_tile.tileset_id = "basic_tiles"
        old_tile.tile_id = 5

        new_tile = Tile("water", walkable=False)
        new_tile.tileset_id = "water_tiles"
        new_tile.tile_id = 12

        cmd = TileChangeCommand(tilemap, 5, 5, 0, old_tile, new_tile)

        # Check delta includes tileset data
        assert cmd.delta.old_tileset_id == "basic_tiles"
        assert cmd.delta.old_tile_id == 5
        assert cmd.delta.new_tileset_id == "water_tiles"
        assert cmd.delta.new_tile_id == 12


class TestBatchTileChangeCommand:
    """Test suite for BatchTileChangeCommand."""

    def test_batch_tile_change(self):
        """Test batch tile change command."""
        tilemap = Tilemap(width=10, height=10, tile_size=32, layers=3)

        # Create batch of changes
        changes = []
        for x in range(5):
            for y in range(5):
                old_tile = None
                new_tile = Tile("grass", walkable=True)
                changes.append((x, y, 0, old_tile, new_tile))

        cmd = BatchTileChangeCommand(tilemap, changes, "Fill with grass")

        # Execute
        cmd.execute()

        # Check all tiles were changed
        for x in range(5):
            for y in range(5):
                tile = tilemap.get_tile(x, y, 0)
                assert tile is not None
                assert tile.tile_type == "grass"

        # Undo
        cmd.undo()

        # Check all tiles were reverted
        for x in range(5):
            for y in range(5):
                tile = tilemap.get_tile(x, y, 0)
                assert tile is None

    def test_batch_efficiency(self):
        """Test that batch command is more efficient than individual commands."""
        tilemap = Tilemap(width=100, height=100, tile_size=32, layers=3)

        # Create 1000 changes
        changes = []
        for i in range(1000):
            x = i % 100
            y = i // 100
            new_tile = Tile("grass", walkable=True)
            changes.append((x, y, 0, None, new_tile))

        batch_cmd = BatchTileChangeCommand(tilemap, changes, "Large fill")

        # Batch command should have single object overhead
        # versus 1000 individual command objects
        assert len(batch_cmd.changes) == 1000


class TestNavmeshPaintCommand:
    """Test suite for NavmeshPaintCommand."""

    def test_navmesh_paint_basic(self):
        """Test basic navmesh paint command."""
        walkable_tiles: Set[Tuple[int, int]] = set()
        unwalkable_tiles: Set[Tuple[int, int]] = set()

        # Paint some tiles as walkable
        changes = [
            (5, 5, False, True),
            (6, 5, False, True),
            (7, 5, False, True),
        ]

        cmd = NavmeshPaintCommand(walkable_tiles, unwalkable_tiles, changes, "Paint walkable")

        # Execute
        cmd.execute()

        assert (5, 5) in walkable_tiles
        assert (6, 5) in walkable_tiles
        assert (7, 5) in walkable_tiles

        # Undo
        cmd.undo()

        assert (5, 5) not in walkable_tiles
        assert (6, 5) not in walkable_tiles
        assert (7, 5) not in walkable_tiles

    def test_navmesh_paint_unwalkable(self):
        """Test painting unwalkable tiles."""
        walkable_tiles: Set[Tuple[int, int]] = set([(5, 5), (6, 5)])
        unwalkable_tiles: Set[Tuple[int, int]] = set()

        # Change walkable to unwalkable
        changes = [
            (5, 5, True, False),
            (6, 5, True, False),
        ]

        cmd = NavmeshPaintCommand(walkable_tiles, unwalkable_tiles, changes, "Paint unwalkable")

        # Execute
        cmd.execute()

        assert (5, 5) in unwalkable_tiles
        assert (6, 5) in unwalkable_tiles
        assert (5, 5) not in walkable_tiles
        assert (6, 5) not in walkable_tiles


class TestCompositeCommand:
    """Test suite for CompositeCommand."""

    def test_composite_command_basic(self):
        """Test composite command with multiple sub-commands."""

        class CounterCommand(Command):
            counter = 0

            def execute(self):
                CounterCommand.counter += 1
                return True

            def undo(self):
                CounterCommand.counter -= 1
                return True

            def get_description(self):
                return "Increment"

            def serialize(self):
                return {"type": "counter"}

            @classmethod
            def deserialize(cls, data):
                return cls()

        # Create composite of 5 counter commands
        commands = [CounterCommand() for _ in range(5)]
        composite = CompositeCommand(commands, "Increment 5 times")

        # Execute
        composite.execute()
        assert CounterCommand.counter == 5

        # Undo
        composite.undo()
        assert CounterCommand.counter == 0

    def test_composite_rollback_on_failure(self):
        """Test that composite rolls back on failure."""

        class FailCommand(Command):
            counter = 0

            def __init__(self, should_fail=False):
                super().__init__()
                self.should_fail = should_fail

            def execute(self):
                if self.should_fail:
                    return False
                FailCommand.counter += 1
                return True

            def undo(self):
                FailCommand.counter -= 1
                return True

            def get_description(self):
                return "Fail test"

            def serialize(self):
                return {}

            @classmethod
            def deserialize(cls, data):
                return cls()

        # Create composite where 3rd command fails
        commands = [
            FailCommand(False),
            FailCommand(False),
            FailCommand(True),  # This one fails
            FailCommand(False),
        ]
        composite = CompositeCommand(commands, "Test rollback")

        # Execute should fail and rollback
        result = composite.execute()
        assert result is False
        assert FailCommand.counter == 0  # All rolled back


class TestDeltaCompressor:
    """Test suite for DeltaCompressor."""

    def test_compress_decompress(self):
        """Test basic compression and decompression."""
        compressor = DeltaCompressor()

        data = {
            "type": "tile_change",
            "x": 5,
            "y": 10,
            "layer": 2,
            "old_tile": "grass",
            "new_tile": "water",
        }

        compressed = compressor.compress(data)
        decompressed = compressor.decompress(compressed)

        assert decompressed == data

    def test_compression_ratio(self):
        """Test that compression actually reduces size."""
        compressor = DeltaCompressor()

        # Create large data structure
        data = {"changes": [(x, y, 0, "grass", "water") for x in range(100) for y in range(100)]}

        compressed = compressor.compress(data)
        ratio = compressor.get_compression_ratio(data, compressed)

        # Compression ratio should be > 1 (data is smaller)
        assert ratio > 1.0


class TestUndoManagerStatistics:
    """Test suite for undo manager statistics."""

    def test_statistics_tracking(self):
        """Test that statistics are tracked correctly."""
        manager = UndoManager()

        class TestCommand(Command):
            def execute(self):
                return True

            def undo(self):
                return True

            def get_description(self):
                return "Test"

            def serialize(self):
                return {}

            @classmethod
            def deserialize(cls, data):
                return cls()

        # Execute some commands
        for _ in range(5):
            manager.execute(TestCommand())

        stats = manager.get_statistics()
        assert stats["total_commands_executed"] == 5
        assert stats["current_undo_count"] == 5
        assert stats["current_redo_count"] == 0

        # Undo some
        manager.undo()
        manager.undo()

        stats = manager.get_statistics()
        assert stats["total_undos"] == 2
        assert stats["current_undo_count"] == 3
        assert stats["current_redo_count"] == 2

        # Redo
        manager.redo()

        stats = manager.get_statistics()
        assert stats["total_redos"] == 1
        assert stats["current_undo_count"] == 4
        assert stats["current_redo_count"] == 1

    def test_memory_usage(self):
        """Test memory usage tracking."""
        manager = UndoManager()

        class TestCommand(Command):
            def execute(self):
                return True

            def undo(self):
                return True

            def get_description(self):
                return "Test"

            def serialize(self):
                return {}

            @classmethod
            def deserialize(cls, data):
                return cls()

        for _ in range(10):
            manager.execute(TestCommand())

        memory = manager.get_memory_usage()

        assert "undo_stack_bytes" in memory
        assert "redo_stack_bytes" in memory
        assert "total_bytes" in memory
        assert memory["undo_count"] == 10
        assert memory["redo_count"] == 0


class TestUndoPersistence:
    """Test suite for undo history persistence."""

    def test_persistence_initialization(self):
        """Test that persistence initializes correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = UndoHistoryPersistence(tmpdir)
            assert persistence.history_dir.exists()

    def test_save_load_history(self):
        """Test saving and loading undo history."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = UndoHistoryPersistence(tmpdir)
            manager = UndoManager()

            class TestCommand(Command):
                def execute(self):
                    return True

                def undo(self):
                    return True

                def get_description(self):
                    return "Test command"

                def serialize(self):
                    return {"type": "test"}

                @classmethod
                def deserialize(cls, data):
                    return cls()

            # Execute some commands
            for i in range(5):
                manager.execute(TestCommand())

            # Save history
            persistence.save_editor_history("test_editor", manager)

            # Create new manager and load
            new_manager = UndoManager()
            persistence.load_editor_history("test_editor", new_manager)

            # Check statistics were restored
            assert new_manager.total_commands_executed == 5

    def test_history_info(self):
        """Test getting history information."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence = UndoHistoryPersistence(tmpdir)
            manager = UndoManager()

            class TestCommand(Command):
                def execute(self):
                    return True

                def undo(self):
                    return True

                def get_description(self):
                    return "Test"

                def serialize(self):
                    return {"type": "test"}

                @classmethod
                def deserialize(cls, data):
                    return cls()

            manager.execute(TestCommand())
            manager.execute(TestCommand())
            persistence.save_editor_history("test_editor", manager)

            info = persistence.get_history_info("test_editor")

            assert info is not None
            assert info["undo_count"] == 2
            assert info["redo_count"] == 0
            assert "size_kb" in info


class TestComplexEditingSequences:
    """Test suite for complex editing sequences."""

    def test_complex_tile_editing(self):
        """Test complex tile editing sequence with undo/redo."""
        manager = UndoManager()
        tilemap = Tilemap(width=20, height=20, tile_size=32, layers=3)

        # Sequence of edits
        # 1. Fill area with grass
        changes = []
        for x in range(10):
            for y in range(10):
                changes.append((x, y, 0, None, Tile("grass", walkable=True)))

        cmd1 = BatchTileChangeCommand(tilemap, changes, "Fill with grass")
        manager.execute(cmd1)

        # 2. Paint some water
        changes = []
        for x in range(3, 7):
            for y in range(3, 7):
                old_tile = tilemap.get_tile(x, y, 0)
                changes.append((x, y, 0, old_tile, Tile("water", walkable=False)))

        cmd2 = BatchTileChangeCommand(tilemap, changes, "Paint water")
        manager.execute(cmd2)

        # 3. Add some rocks
        changes = []
        for x in [1, 8]:
            for y in [1, 8]:
                old_tile = tilemap.get_tile(x, y, 0)
                changes.append((x, y, 0, old_tile, Tile("rock", walkable=False)))

        cmd3 = BatchTileChangeCommand(tilemap, changes, "Add rocks")
        manager.execute(cmd3)

        # Verify final state
        assert tilemap.get_tile(5, 5, 0).tile_type == "water"
        assert tilemap.get_tile(1, 1, 0).tile_type == "rock"
        assert tilemap.get_tile(0, 0, 0).tile_type == "grass"

        # Undo all
        manager.undo()  # Remove rocks
        assert tilemap.get_tile(1, 1, 0).tile_type == "grass"

        manager.undo()  # Remove water
        assert tilemap.get_tile(5, 5, 0).tile_type == "grass"

        manager.undo()  # Remove grass
        assert tilemap.get_tile(0, 0, 0) is None

        # Redo all
        manager.redo()
        assert tilemap.get_tile(0, 0, 0).tile_type == "grass"

        manager.redo()
        assert tilemap.get_tile(5, 5, 0).tile_type == "water"

        manager.redo()
        assert tilemap.get_tile(1, 1, 0).tile_type == "rock"

    def test_mixed_edit_operations(self):
        """Test mixing different types of edit operations."""
        manager = UndoManager()
        tilemap = Tilemap(width=10, height=10, tile_size=32, layers=3)

        walkable_tiles: Set[Tuple[int, int]] = set()
        unwalkable_tiles: Set[Tuple[int, int]] = set()

        # 1. Tile edit
        cmd1 = TileChangeCommand(tilemap, 5, 5, 0, None, Tile("grass", walkable=True))
        manager.execute(cmd1)

        # 2. Navmesh edit
        cmd2 = NavmeshPaintCommand(
            walkable_tiles, unwalkable_tiles, [(5, 5, False, True)], "Paint walkable"
        )
        manager.execute(cmd2)

        # 3. Another tile edit
        cmd3 = TileChangeCommand(tilemap, 6, 6, 0, None, Tile("water", walkable=False))
        manager.execute(cmd3)

        # Verify
        assert tilemap.get_tile(5, 5, 0).tile_type == "grass"
        assert (5, 5) in walkable_tiles
        assert tilemap.get_tile(6, 6, 0).tile_type == "water"

        # Undo all
        manager.undo()
        manager.undo()
        manager.undo()

        assert tilemap.get_tile(5, 5, 0) is None
        assert (5, 5) not in walkable_tiles
        assert tilemap.get_tile(6, 6, 0) is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
