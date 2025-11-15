"""
Tests for the Map Manager system.

Tests map creation, loading, saving, deletion, organization,
duplication, templates, and batch operations.
"""

import json
import tempfile
from pathlib import Path

import pytest

from neonworks.data.map_manager import (
    MapConnection,
    MapData,
    MapDimensions,
    MapFolder,
    MapManager,
    MapMetadata,
    MapProperties,
    MapTilesetConfig,
)


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def map_manager(temp_project_dir):
    """Create a MapManager instance for testing."""
    return MapManager(temp_project_dir)


@pytest.mark.smoke
class TestMapData:
    """Test MapData class."""

    def test_create_map_data(self):
        """Test creating a MapData instance."""
        map_data = MapData("TestMap", width=60, height=40, tile_size=32)

        assert map_data.metadata.name == "TestMap"
        assert map_data.dimensions.width == 60
        assert map_data.dimensions.height == 40
        assert map_data.dimensions.tile_size == 32

    def test_map_data_serialization(self):
        """Test serializing and deserializing MapData."""
        # Create map with data
        map_data = MapData("SerializeTest", width=50, height=50)
        map_data.metadata.description = "Test map"
        map_data.metadata.author = "Test Author"
        map_data.metadata.tags = ["dungeon", "forest"]
        map_data.metadata.folder = "test/folder"
        map_data.properties.bgm = "test_music.ogg"
        map_data.properties.encounter_rate = 25
        map_data.tileset.tileset_id = "forest_tileset"
        map_data.tileset.tileset_name = "Forest Tiles"

        # Serialize
        data_dict = map_data.to_dict()

        # Deserialize
        restored = MapData.from_dict(data_dict)

        # Verify
        assert restored.metadata.name == "SerializeTest"
        assert restored.metadata.description == "Test map"
        assert restored.metadata.author == "Test Author"
        assert restored.metadata.tags == ["dungeon", "forest"]
        assert restored.metadata.folder == "test/folder"
        assert restored.dimensions.width == 50
        assert restored.dimensions.height == 50
        assert restored.properties.bgm == "test_music.ogg"
        assert restored.properties.encounter_rate == 25
        assert restored.tileset.tileset_id == "forest_tileset"
        assert restored.tileset.tileset_name == "Forest Tiles"

    def test_map_connections_serialization(self):
        """Test serializing map connections."""
        map_data = MapData("ConnTest")

        # Add connections
        conn1 = MapConnection(
            source_map="ConnTest",
            target_map="TargetMap",
            source_position=(10, 15),
            target_position=(5, 5),
            connection_type="teleport",
            bidirectional=True,
        )
        map_data.connections.append(conn1)

        # Serialize and deserialize
        data_dict = map_data.to_dict()
        restored = MapData.from_dict(data_dict)

        assert len(restored.connections) == 1
        assert restored.connections[0].target_map == "TargetMap"
        assert restored.connections[0].source_position == (10, 15)
        assert restored.connections[0].target_position == (5, 5)
        assert restored.connections[0].bidirectional is True

    def test_resize_map(self):
        """Test resizing a map."""
        map_data = MapData("ResizeTest", width=50, height=50)

        original_modified = map_data.metadata.modified_date

        # Resize
        map_data.resize(100, 80)

        assert map_data.dimensions.width == 100
        assert map_data.dimensions.height == 80
        # Modified date should be updated
        assert map_data.metadata.modified_date != original_modified


class TestMapFolder:
    """Test MapFolder class."""

    def test_create_folder(self):
        """Test creating a folder."""
        folder = MapFolder("dungeons")

        assert folder.name == "dungeons"
        assert folder.parent is None
        assert len(folder.children) == 0
        assert len(folder.maps) == 0

    def test_folder_path(self):
        """Test getting folder path."""
        root = MapFolder("root")
        dungeons = MapFolder("dungeons", parent=root)
        castle = MapFolder("castle", parent=dungeons)

        assert root.get_path() == ""
        assert dungeons.get_path() == "dungeons"
        assert castle.get_path() == "dungeons/castle"

    def test_add_child_folder(self):
        """Test adding a child folder."""
        parent = MapFolder("parent")
        child = MapFolder("child")

        parent.add_child(child)

        assert child in parent.children
        assert child.parent == parent

    def test_add_remove_map(self):
        """Test adding and removing maps from folder."""
        folder = MapFolder("test")

        folder.add_map("map1")
        folder.add_map("map2")

        assert "map1" in folder.maps
        assert "map2" in folder.maps

        folder.remove_map("map1")

        assert "map1" not in folder.maps
        assert "map2" in folder.maps


@pytest.mark.unit
class TestMapManager:
    """Test MapManager class."""

    def test_create_manager(self, temp_project_dir):
        """Test creating a MapManager."""
        manager = MapManager(temp_project_dir)

        assert manager.project_root == temp_project_dir
        assert manager.levels_dir.exists()
        assert manager.templates_dir.exists()

    def test_create_map(self, map_manager):
        """Test creating a new map."""
        map_data = map_manager.create_map("TestMap", width=60, height=40)

        assert map_data.metadata.name == "TestMap"
        assert map_data.dimensions.width == 60
        assert map_data.dimensions.height == 40
        assert "TestMap" in map_manager.maps

    def test_create_duplicate_map_fails(self, map_manager):
        """Test that creating a duplicate map raises an error."""
        map_manager.create_map("DuplicateTest")

        with pytest.raises(ValueError, match="already exists"):
            map_manager.create_map("DuplicateTest")

    def test_create_map_in_folder(self, map_manager):
        """Test creating a map in a folder."""
        map_data = map_manager.create_map(
            "FolderMap", width=50, height=50, folder="dungeons/castle"
        )

        assert map_data.metadata.folder == "dungeons/castle"

    def test_save_and_load_map(self, map_manager):
        """Test saving and loading a map."""
        # Create map
        map_data = map_manager.create_map("SaveLoadTest", width=55, height=45)
        map_data.metadata.description = "A test map"
        map_data.properties.bgm = "music.ogg"

        # Save
        success = map_manager.save_map(map_data)
        assert success

        # Verify file exists
        map_path = map_manager.get_map_path("SaveLoadTest")
        assert map_path.exists()

        # Clear cache and reload
        map_manager.maps.clear()
        loaded = map_manager.load_map("SaveLoadTest")

        assert loaded is not None
        assert loaded.metadata.name == "SaveLoadTest"
        assert loaded.metadata.description == "A test map"
        assert loaded.dimensions.width == 55
        assert loaded.properties.bgm == "music.ogg"

    def test_delete_map(self, map_manager):
        """Test deleting a map."""
        # Create and save map
        map_data = map_manager.create_map("DeleteTest")
        map_manager.save_map(map_data)

        # Verify it exists
        assert map_manager.map_exists("DeleteTest")

        # Delete
        success = map_manager.delete_map("DeleteTest")
        assert success

        # Verify it's gone
        assert not map_manager.map_exists("DeleteTest")
        assert "DeleteTest" not in map_manager.maps

    def test_duplicate_map(self, map_manager):
        """Test duplicating a map."""
        # Create original map
        original = map_manager.create_map("Original", width=50, height=50)
        original.metadata.description = "Original map"
        original.properties.bgm = "original_music.ogg"
        map_manager.save_map(original)

        # Duplicate
        duplicate = map_manager.duplicate_map("Original", "Duplicate")

        assert duplicate is not None
        assert duplicate.metadata.name == "Duplicate"
        assert duplicate.metadata.description == "Original map"
        assert duplicate.properties.bgm == "original_music.ogg"
        assert duplicate.dimensions.width == 50

        # Verify both exist
        assert map_manager.map_exists("Original")
        assert map_manager.map_exists("Duplicate")

    def test_duplicate_nonexistent_map_fails(self, map_manager):
        """Test duplicating a nonexistent map fails."""
        with pytest.raises(ValueError, match="not found"):
            map_manager.duplicate_map("Nonexistent", "NewName")

    def test_duplicate_to_existing_name_fails(self, map_manager):
        """Test duplicating to an existing name fails."""
        map_manager.create_map("Map1")
        map_manager.create_map("Map2")
        map_manager.save_map(map_manager.maps["Map1"])

        with pytest.raises(ValueError, match="already exists"):
            map_manager.duplicate_map("Map1", "Map2")

    def test_save_and_load_template(self, map_manager):
        """Test saving and loading from template."""
        # Create map
        map_data = map_manager.create_map("TemplateSource", width=50, height=50)
        map_data.metadata.description = "Template map"
        map_manager.save_map(map_data)

        # Save as template
        success = map_manager.save_as_template("TemplateSource", "MyTemplate")
        assert success

        # Verify template exists
        templates = map_manager.list_templates()
        assert "MyTemplate" in templates

        # Create from template
        new_map = map_manager.create_from_template("MyTemplate", "FromTemplate")

        assert new_map is not None
        assert new_map.metadata.name == "FromTemplate"
        assert new_map.metadata.description == "Template map"
        assert new_map.dimensions.width == 50

    def test_list_maps(self, map_manager):
        """Test listing all maps."""
        # Create several maps
        map_manager.create_map("Map1")
        map_manager.create_map("Map2")
        map_manager.create_map("Map3")

        # Save them
        for map_name in ["Map1", "Map2", "Map3"]:
            map_manager.save_map(map_manager.maps[map_name])

        # List maps
        maps = map_manager.list_maps()

        assert "Map1" in maps
        assert "Map2" in maps
        assert "Map3" in maps

    def test_get_map_metadata(self, map_manager):
        """Test getting just metadata without loading full map."""
        # Create map
        map_data = map_manager.create_map("MetadataTest")
        map_data.metadata.description = "Test description"
        map_data.metadata.author = "Test Author"
        map_manager.save_map(map_data)

        # Get metadata
        map_manager.maps.clear()  # Clear cache
        metadata = map_manager.get_map_metadata("MetadataTest")

        assert metadata is not None
        assert metadata["name"] == "MetadataTest"
        assert metadata["description"] == "Test description"
        assert metadata["author"] == "Test Author"

    def test_batch_resize(self, map_manager):
        """Test batch resizing maps."""
        # Create maps
        map_manager.create_map("Resize1", width=50, height=50)
        map_manager.create_map("Resize2", width=50, height=50)
        map_manager.create_map("Resize3", width=50, height=50)

        # Save them
        for name in ["Resize1", "Resize2", "Resize3"]:
            map_manager.save_map(map_manager.maps[name])

        # Batch resize
        count = map_manager.batch_resize(["Resize1", "Resize2"], 100, 80)

        assert count == 2

        # Verify resize
        map1 = map_manager.load_map("Resize1", cache=False)
        assert map1.dimensions.width == 100
        assert map1.dimensions.height == 80

        # Map3 should be unchanged
        map3 = map_manager.load_map("Resize3", cache=False)
        assert map3.dimensions.width == 50
        assert map3.dimensions.height == 50

    def test_batch_export(self, map_manager, temp_project_dir):
        """Test batch exporting maps."""
        # Create maps
        map_manager.create_map("Export1")
        map_manager.create_map("Export2")

        # Save them
        for name in ["Export1", "Export2"]:
            map_manager.save_map(map_manager.maps[name])

        # Export to temp directory
        export_dir = temp_project_dir / "exports"
        count = map_manager.batch_export(["Export1", "Export2"], export_dir)

        assert count == 2
        assert (export_dir / "Export1.json").exists()
        assert (export_dir / "Export2.json").exists()

    def test_get_map_connections(self, map_manager):
        """Test getting connections for a map."""
        # Create map with connections
        map_data = map_manager.create_map("ConnMap")
        map_data.connections.append(
            MapConnection(
                source_map="ConnMap",
                target_map="TargetMap1",
                source_position=(10, 10),
                target_position=(5, 5),
            )
        )
        map_data.connections.append(
            MapConnection(
                source_map="ConnMap",
                target_map="TargetMap2",
                source_position=(20, 20),
                target_position=(15, 15),
            )
        )
        map_manager.save_map(map_data)

        # Get connections
        connections = map_manager.get_map_connections("ConnMap")

        assert len(connections) == 2
        assert connections[0].target_map == "TargetMap1"
        assert connections[1].target_map == "TargetMap2"

    def test_find_connected_maps(self, map_manager):
        """Test finding all maps connected to a map."""
        # Create map with connections
        map_data = map_manager.create_map("SourceMap")
        map_data.connections.append(
            MapConnection(
                source_map="SourceMap",
                target_map="Target1",
                source_position=(0, 0),
                target_position=(0, 0),
            )
        )
        map_data.connections.append(
            MapConnection(
                source_map="SourceMap",
                target_map="Target2",
                source_position=(0, 0),
                target_position=(0, 0),
                bidirectional=True,
            )
        )
        map_manager.save_map(map_data)

        # Find connected maps
        connected = map_manager.find_connected_maps("SourceMap")

        assert "Target1" in connected
        assert "Target2" in connected

    def test_folder_structure_building(self, map_manager):
        """Test automatic folder structure building."""
        # Create maps in different folders
        map_manager.create_map("Map1", folder="dungeons")
        map_manager.create_map("Map2", folder="dungeons/castle")
        map_manager.create_map("Map3", folder="towns")
        map_manager.create_map("Map4", folder="")

        # Save them
        for name in ["Map1", "Map2", "Map3", "Map4"]:
            map_manager.save_map(map_manager.maps[name])

        # Rebuild folder structure
        map_manager._build_folder_structure()

        # Check root folder
        assert "Map4" in map_manager.root_folder.maps

        # Find dungeons folder
        dungeons = next(
            (f for f in map_manager.root_folder.children if f.name == "dungeons"),
            None,
        )
        assert dungeons is not None
        assert "Map1" in dungeons.maps

        # Find castle subfolder
        castle = next((f for f in dungeons.children if f.name == "castle"), None)
        assert castle is not None
        assert "Map2" in castle.maps

        # Find towns folder
        towns = next((f for f in map_manager.root_folder.children if f.name == "towns"), None)
        assert towns is not None
        assert "Map3" in towns.maps


@pytest.mark.integration
@pytest.mark.slow
class TestMapIntegration:
    """Integration tests for the map system."""

    def test_full_workflow(self, map_manager):
        """Test a complete workflow with map management."""
        # 1. Create a map
        map1 = map_manager.create_map("Workflow1", width=50, height=50, folder="test")
        map1.metadata.description = "First map"
        map1.properties.bgm = "music1.ogg"

        # 2. Save it
        assert map_manager.save_map(map1)

        # 3. Create another map
        map2 = map_manager.create_map("Workflow2", width=60, height=40)
        map2.metadata.description = "Second map"

        # 4. Add connection from map1 to map2
        map1.connections.append(
            MapConnection(
                source_map="Workflow1",
                target_map="Workflow2",
                source_position=(25, 25),
                target_position=(30, 20),
                connection_type="door",
            )
        )
        map_manager.save_map(map1)
        map_manager.save_map(map2)

        # 5. Duplicate map1
        map3 = map_manager.duplicate_map("Workflow1", "Workflow3")
        assert map3 is not None

        # 6. List all maps
        maps = map_manager.list_maps()
        assert len(maps) == 3

        # 7. Get connections
        connections = map_manager.get_map_connections("Workflow1")
        assert len(connections) == 1
        assert connections[0].target_map == "Workflow2"

        # 8. Save as template
        assert map_manager.save_as_template("Workflow1", "TestTemplate")

        # 9. Create from template
        map4 = map_manager.create_from_template("TestTemplate", "Workflow4")
        assert map4 is not None
        assert map4.properties.bgm == "music1.ogg"

        # 10. Batch operations
        count = map_manager.batch_resize(["Workflow2", "Workflow3"], 100, 100)
        assert count == 2

        # 11. Delete a map
        assert map_manager.delete_map("Workflow4")
        assert not map_manager.map_exists("Workflow4")

        # 12. Verify final state
        final_maps = map_manager.list_maps()
        assert "Workflow1" in final_maps
        assert "Workflow2" in final_maps
        assert "Workflow3" in final_maps
        assert "Workflow4" not in final_maps
