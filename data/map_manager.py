"""
Map Manager for NeonWorks Engine.

Provides comprehensive map management including:
- Map creation, loading, saving, deletion
- Map organization with folders
- Map duplication and templates
- Batch operations (export all, batch resize)
- Map linking tracking (teleports, connections)
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from neonworks.data.map_layers import LayerManager
from neonworks.data.serialization import load_from_file, save_to_file


@dataclass
class MapMetadata:
    """Metadata for a map."""

    name: str
    description: str = ""
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())
    modified_date: str = field(default_factory=lambda: datetime.now().isoformat())
    author: str = ""
    tags: List[str] = field(default_factory=list)
    folder: str = ""  # Folder path for organization


@dataclass
class MapDimensions:
    """Dimensions configuration for a map."""

    width: int = 50
    height: int = 50
    tile_size: int = 32


@dataclass
class MapTilesetConfig:
    """Tileset configuration for a map."""

    tileset_id: str = ""
    tileset_name: str = ""
    tileset_path: str = ""


@dataclass
class MapProperties:
    """Game properties for a map."""

    bgm: str = ""
    ambient_sound: str = ""
    encounter_rate: int = 0
    wrap_x: bool = False
    wrap_y: bool = False
    weather: str = "none"
    time_of_day: str = "day"
    custom_properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MapConnection:
    """Represents a connection/teleport to another map."""

    source_map: str
    target_map: str
    source_position: Tuple[int, int]
    target_position: Tuple[int, int]
    connection_type: str = "teleport"  # teleport, zone_transition, door, etc.
    bidirectional: bool = False


class MapData:
    """Represents a complete map with all its data."""

    def __init__(
        self,
        name: str,
        width: int = 50,
        height: int = 50,
        tile_size: int = 32,
    ):
        """
        Initialize a new map.

        Args:
            name: Name of the map
            width: Width in tiles
            height: Height in tiles
            tile_size: Size of each tile in pixels
        """
        self.metadata = MapMetadata(name=name)
        self.dimensions = MapDimensions(width=width, height=height, tile_size=tile_size)
        self.tileset = MapTilesetConfig()
        self.properties = MapProperties()
        self.layer_manager = LayerManager(width, height)
        self.entities: List[Dict[str, Any]] = []
        self.events: List[Dict[str, Any]] = []
        self.connections: List[MapConnection] = []

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize map to JSON-compatible dictionary.

        Returns:
            Dictionary containing all map data
        """
        return {
            "metadata": {
                "name": self.metadata.name,
                "description": self.metadata.description,
                "created_date": self.metadata.created_date,
                "modified_date": self.metadata.modified_date,
                "author": self.metadata.author,
                "tags": self.metadata.tags,
                "folder": self.metadata.folder,
            },
            "dimensions": {
                "width": self.dimensions.width,
                "height": self.dimensions.height,
                "tile_size": self.dimensions.tile_size,
            },
            "tileset": {
                "tileset_id": self.tileset.tileset_id,
                "tileset_name": self.tileset.tileset_name,
                "tileset_path": self.tileset.tileset_path,
            },
            "properties": {
                "bgm": self.properties.bgm,
                "ambient_sound": self.properties.ambient_sound,
                "encounter_rate": self.properties.encounter_rate,
                "wrap_x": self.properties.wrap_x,
                "wrap_y": self.properties.wrap_y,
                "weather": self.properties.weather,
                "time_of_day": self.properties.time_of_day,
                "custom_properties": self.properties.custom_properties,
            },
            "layers": self.layer_manager.to_dict(),
            "entities": self.entities,
            "events": self.events,
            "connections": [
                {
                    "source_map": conn.source_map,
                    "target_map": conn.target_map,
                    "source_position": conn.source_position,
                    "target_position": conn.target_position,
                    "connection_type": conn.connection_type,
                    "bidirectional": conn.bidirectional,
                }
                for conn in self.connections
            ],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MapData:
        """
        Deserialize map from dictionary.

        Args:
            data: Dictionary containing map data

        Returns:
            MapData instance
        """
        metadata = data.get("metadata", {})
        dimensions = data.get("dimensions", {})

        map_data = cls(
            name=metadata.get("name", "Untitled Map"),
            width=dimensions.get("width", 50),
            height=dimensions.get("height", 50),
            tile_size=dimensions.get("tile_size", 32),
        )

        # Restore metadata
        map_data.metadata.description = metadata.get("description", "")
        map_data.metadata.created_date = metadata.get("created_date", "")
        map_data.metadata.modified_date = metadata.get("modified_date", "")
        map_data.metadata.author = metadata.get("author", "")
        map_data.metadata.tags = metadata.get("tags", [])
        map_data.metadata.folder = metadata.get("folder", "")

        # Restore tileset
        tileset = data.get("tileset", {})
        map_data.tileset.tileset_id = tileset.get("tileset_id", "")
        map_data.tileset.tileset_name = tileset.get("tileset_name", "")
        map_data.tileset.tileset_path = tileset.get("tileset_path", "")

        # Restore properties
        props = data.get("properties", {})
        map_data.properties.bgm = props.get("bgm", "")
        map_data.properties.ambient_sound = props.get("ambient_sound", "")
        map_data.properties.encounter_rate = props.get("encounter_rate", 0)
        map_data.properties.wrap_x = props.get("wrap_x", False)
        map_data.properties.wrap_y = props.get("wrap_y", False)
        map_data.properties.weather = props.get("weather", "none")
        map_data.properties.time_of_day = props.get("time_of_day", "day")
        map_data.properties.custom_properties = props.get("custom_properties", {})

        # Restore layers
        layers_data = data.get("layers", {})
        if layers_data:
            map_data.layer_manager = LayerManager.from_dict(layers_data)

        # Restore entities and events
        map_data.entities = data.get("entities", [])
        map_data.events = data.get("events", [])

        # Restore connections
        connections = data.get("connections", [])
        map_data.connections = [
            MapConnection(
                source_map=conn.get("source_map", ""),
                target_map=conn.get("target_map", ""),
                source_position=tuple(conn.get("source_position", (0, 0))),
                target_position=tuple(conn.get("target_position", (0, 0))),
                connection_type=conn.get("connection_type", "teleport"),
                bidirectional=conn.get("bidirectional", False),
            )
            for conn in connections
        ]

        return map_data

    def update_modified_date(self) -> None:
        """Update the modified date to current time."""
        self.metadata.modified_date = datetime.now().isoformat()

    def resize(self, new_width: int, new_height: int) -> None:
        """
        Resize the map, preserving existing data where possible.

        Args:
            new_width: New width in tiles
            new_height: New height in tiles
        """
        self.dimensions.width = new_width
        self.dimensions.height = new_height
        self.layer_manager.resize(new_width, new_height)
        self.update_modified_date()


class MapFolder:
    """Represents a folder for organizing maps."""

    def __init__(self, name: str, parent: Optional[MapFolder] = None):
        """
        Initialize a map folder.

        Args:
            name: Name of the folder
            parent: Parent folder (None for root)
        """
        self.name = name
        self.parent = parent
        self.children: List[MapFolder] = []
        self.maps: List[str] = []  # Map names in this folder

    def get_path(self) -> str:
        """
        Get the full path of this folder.

        Returns:
            Folder path string (e.g., "dungeons/castle")
        """
        if self.parent is None:
            return ""
        path_parts = []
        current = self
        while current.parent is not None:
            path_parts.insert(0, current.name)
            current = current.parent
        return "/".join(path_parts)

    def add_child(self, child: MapFolder) -> None:
        """Add a child folder."""
        child.parent = self
        self.children.append(child)

    def add_map(self, map_name: str) -> None:
        """Add a map to this folder."""
        if map_name not in self.maps:
            self.maps.append(map_name)

    def remove_map(self, map_name: str) -> None:
        """Remove a map from this folder."""
        if map_name in self.maps:
            self.maps.remove(map_name)


class MapManager:
    """
    Manages all maps in a project.

    Provides functionality for:
    - Creating, loading, saving, deleting maps
    - Map organization with folders
    - Map duplication and templates
    - Batch operations
    - Map linking tracking
    """

    def __init__(self, project_root: Path):
        """
        Initialize the map manager.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root)
        self.levels_dir = self.project_root / "levels"
        self.templates_dir = self.project_root / "templates" / "maps"

        # Create directories if they don't exist
        self.levels_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        self.maps: Dict[str, MapData] = {}
        self.current_map_name: Optional[str] = None
        self.root_folder = MapFolder("root")
        self._build_folder_structure()

    def _build_folder_structure(self) -> None:
        """Build folder structure from map metadata."""
        # Clear existing structure
        self.root_folder.children = []
        self.root_folder.maps = []

        # Build from all maps
        for map_name in self.list_maps():
            map_data = self.get_map_metadata(map_name)
            if map_data:
                folder_path = map_data.get("metadata", {}).get("folder", "")
                self._ensure_folder_path(folder_path)
                self._add_map_to_folder(map_name, folder_path)

    def _ensure_folder_path(self, folder_path: str) -> MapFolder:
        """
        Ensure a folder path exists in the folder tree.

        Args:
            folder_path: Path string (e.g., "dungeons/castle")

        Returns:
            The folder at the end of the path
        """
        if not folder_path:
            return self.root_folder

        parts = folder_path.split("/")
        current = self.root_folder

        for part in parts:
            # Find or create child
            child = next((c for c in current.children if c.name == part), None)
            if child is None:
                child = MapFolder(part, current)
                current.add_child(child)
            current = child

        return current

    def _add_map_to_folder(self, map_name: str, folder_path: str) -> None:
        """Add a map to the appropriate folder."""
        folder = self._ensure_folder_path(folder_path)
        folder.add_map(map_name)

    def create_map(
        self,
        name: str,
        width: int = 50,
        height: int = 50,
        tile_size: int = 32,
        folder: str = "",
    ) -> MapData:
        """
        Create a new map.

        Args:
            name: Name of the map
            width: Width in tiles
            height: Height in tiles
            tile_size: Tile size in pixels
            folder: Folder path for organization

        Returns:
            Newly created MapData instance

        Raises:
            ValueError: If a map with this name already exists
        """
        if self.map_exists(name):
            raise ValueError(f"Map '{name}' already exists")

        map_data = MapData(name, width, height, tile_size)
        map_data.metadata.folder = folder
        self.maps[name] = map_data
        self._add_map_to_folder(name, folder)

        return map_data

    def load_map(self, name: str, cache: bool = True) -> Optional[MapData]:
        """
        Load a map from disk.

        Args:
            name: Name of the map to load
            cache: Whether to cache in memory

        Returns:
            MapData instance or None if not found
        """
        # Check cache first
        if cache and name in self.maps:
            return self.maps[name]

        map_path = self.get_map_path(name)
        if not map_path.exists():
            return None

        try:
            data = load_from_file(str(map_path))
            map_data = MapData.from_dict(data)

            if cache:
                self.maps[name] = map_data

            return map_data
        except Exception as e:
            print(f"Error loading map '{name}': {e}")
            return None

    def save_map(self, map_data: MapData, update_modified: bool = True) -> bool:
        """
        Save a map to disk.

        Args:
            map_data: MapData instance to save
            update_modified: Whether to update modified date

        Returns:
            True if successful, False otherwise
        """
        if update_modified:
            map_data.update_modified_date()

        map_path = self.get_map_path(map_data.metadata.name)

        try:
            save_to_file(map_data.to_dict(), str(map_path))
            self.maps[map_data.metadata.name] = map_data
            return True
        except Exception as e:
            print(f"Error saving map '{map_data.metadata.name}': {e}")
            return False

    def delete_map(self, name: str) -> bool:
        """
        Delete a map.

        Args:
            name: Name of the map to delete

        Returns:
            True if successful, False otherwise
        """
        map_path = self.get_map_path(name)

        try:
            if map_path.exists():
                map_path.unlink()

            # Remove from cache
            if name in self.maps:
                folder = self.maps[name].metadata.folder
                self._remove_map_from_folder(name, folder)
                del self.maps[name]

            if self.current_map_name == name:
                self.current_map_name = None

            return True
        except Exception as e:
            print(f"Error deleting map '{name}': {e}")
            return False

    def _remove_map_from_folder(self, map_name: str, folder_path: str) -> None:
        """Remove a map from its folder."""
        if folder_path:
            folder = self._ensure_folder_path(folder_path)
            folder.remove_map(map_name)
        else:
            self.root_folder.remove_map(map_name)

    def duplicate_map(self, source_name: str, new_name: str) -> Optional[MapData]:
        """
        Duplicate an existing map.

        Args:
            source_name: Name of the map to duplicate
            new_name: Name for the new map

        Returns:
            New MapData instance or None if failed

        Raises:
            ValueError: If new name already exists or source doesn't exist
        """
        if self.map_exists(new_name):
            raise ValueError(f"Map '{new_name}' already exists")

        source_map = self.load_map(source_name)
        if source_map is None:
            raise ValueError(f"Source map '{source_name}' not found")

        # Create deep copy
        new_map_data = MapData.from_dict(source_map.to_dict())
        new_map_data.metadata.name = new_name
        new_map_data.metadata.created_date = datetime.now().isoformat()
        new_map_data.metadata.modified_date = datetime.now().isoformat()

        self.save_map(new_map_data)
        return new_map_data

    def save_as_template(self, map_name: str, template_name: str) -> bool:
        """
        Save a map as a template.

        Args:
            map_name: Name of the map to save
            template_name: Name for the template

        Returns:
            True if successful, False otherwise
        """
        map_data = self.load_map(map_name)
        if map_data is None:
            return False

        template_path = self.templates_dir / f"{template_name}.json"

        try:
            save_to_file(map_data.to_dict(), str(template_path))
            return True
        except Exception as e:
            print(f"Error saving template '{template_name}': {e}")
            return False

    def create_from_template(self, template_name: str, new_name: str) -> Optional[MapData]:
        """
        Create a new map from a template.

        Args:
            template_name: Name of the template
            new_name: Name for the new map

        Returns:
            New MapData instance or None if failed
        """
        template_path = self.templates_dir / f"{template_name}.json"

        if not template_path.exists():
            print(f"Template '{template_name}' not found")
            return None

        try:
            data = load_from_file(str(template_path))
            map_data = MapData.from_dict(data)
            map_data.metadata.name = new_name
            map_data.metadata.created_date = datetime.now().isoformat()
            map_data.metadata.modified_date = datetime.now().isoformat()

            self.save_map(map_data)
            return map_data
        except Exception as e:
            print(f"Error creating from template '{template_name}': {e}")
            return None

    def list_maps(self) -> List[str]:
        """
        List all available maps.

        Returns:
            List of map names
        """
        if not self.levels_dir.exists():
            return []

        map_files = self.levels_dir.glob("*.json")
        return sorted([f.stem for f in map_files])

    def list_templates(self) -> List[str]:
        """
        List all available templates.

        Returns:
            List of template names
        """
        if not self.templates_dir.exists():
            return []

        template_files = self.templates_dir.glob("*.json")
        return sorted([f.stem for f in template_files])

    def map_exists(self, name: str) -> bool:
        """
        Check if a map exists.

        Args:
            name: Name of the map

        Returns:
            True if map exists
        """
        return self.get_map_path(name).exists()

    def get_map_path(self, name: str) -> Path:
        """
        Get the file path for a map.

        Args:
            name: Name of the map

        Returns:
            Path to the map file
        """
        return self.levels_dir / f"{name}.json"

    def get_map_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get just the metadata for a map without loading the full map.

        Args:
            name: Name of the map

        Returns:
            Metadata dictionary or None if not found
        """
        map_path = self.get_map_path(name)
        if not map_path.exists():
            return None

        try:
            with open(map_path, "r") as f:
                data = json.load(f)
            return data.get("metadata", {})
        except Exception as e:
            print(f"Error reading metadata for '{name}': {e}")
            return None

    def batch_resize(self, map_names: List[str], new_width: int, new_height: int) -> int:
        """
        Batch resize multiple maps.

        Args:
            map_names: List of map names to resize
            new_width: New width in tiles
            new_height: New height in tiles

        Returns:
            Number of maps successfully resized
        """
        count = 0
        for name in map_names:
            map_data = self.load_map(name)
            if map_data:
                map_data.resize(new_width, new_height)
                if self.save_map(map_data):
                    count += 1
        return count

    def batch_export(self, map_names: List[str], export_dir: Path) -> int:
        """
        Batch export multiple maps to a directory.

        Args:
            map_names: List of map names to export
            export_dir: Directory to export to

        Returns:
            Number of maps successfully exported
        """
        export_dir = Path(export_dir)
        export_dir.mkdir(parents=True, exist_ok=True)

        count = 0
        for name in map_names:
            source = self.get_map_path(name)
            if source.exists():
                try:
                    dest = export_dir / f"{name}.json"
                    shutil.copy2(source, dest)
                    count += 1
                except Exception as e:
                    print(f"Error exporting '{name}': {e}")

        return count

    def get_map_connections(self, map_name: str) -> List[MapConnection]:
        """
        Get all connections for a specific map.

        Args:
            map_name: Name of the map

        Returns:
            List of MapConnection objects
        """
        map_data = self.load_map(map_name)
        if map_data is None:
            return []
        return map_data.connections

    def get_all_connections(self) -> Dict[str, List[MapConnection]]:
        """
        Get all connections across all maps.

        Returns:
            Dictionary mapping map names to their connections
        """
        all_connections = {}

        for map_name in self.list_maps():
            connections = self.get_map_connections(map_name)
            if connections:
                all_connections[map_name] = connections

        return all_connections

    def find_connected_maps(self, map_name: str) -> Set[str]:
        """
        Find all maps connected to a given map.

        Args:
            map_name: Name of the map

        Returns:
            Set of connected map names
        """
        connected = set()
        connections = self.get_map_connections(map_name)

        for conn in connections:
            connected.add(conn.target_map)
            if conn.bidirectional:
                connected.add(conn.source_map)

        return connected


# Global map manager instance
_map_manager_instance: Optional[MapManager] = None


def get_map_manager() -> Optional[MapManager]:
    """
    Get the global map manager instance.

    Returns:
        MapManager instance or None if not initialized
    """
    return _map_manager_instance


def initialize_map_manager(project_root: Path) -> MapManager:
    """
    Initialize the global map manager.

    Args:
        project_root: Root directory of the project

    Returns:
        MapManager instance
    """
    global _map_manager_instance
    _map_manager_instance = MapManager(project_root)
    return _map_manager_instance
