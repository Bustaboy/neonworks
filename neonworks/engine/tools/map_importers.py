"""
Map Import/Export Tools for NeonWorks Engine.

Provides comprehensive map import/export functionality including:
- Export map as PNG image (screenshot/minimap)
- Import Tiled TMX files (basic support)
- Export to Tiled TMX format
- Tileset image importer
- Map format converter for legacy data

Author: NeonWorks Team
Version: 0.1.0
"""

from __future__ import annotations

import base64
import json
import os
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pygame

from neonworks.data.map_layers import (
    EnhancedTileLayer,
    LayerManager,
    LayerProperties,
    LayerType,
    ParallaxMode,
)
from neonworks.data.map_manager import MapData, MapDimensions, MapMetadata
from neonworks.data.tileset_manager import TileMetadata, TilesetInfo, TilesetManager


class PNGExporter:
    """
    Export maps as PNG images.

    Supports rendering maps to PNG for:
    - Screenshots
    - Minimaps
    - Documentation
    - Social media sharing
    """

    def __init__(self, tileset_manager: Optional[TilesetManager] = None):
        """
        Initialize PNG exporter.

        Args:
            tileset_manager: TilesetManager instance for loading tilesets
        """
        self.tileset_manager = tileset_manager

    def export_map_to_png(
        self,
        map_data: MapData,
        output_path: str,
        scale: float = 1.0,
        render_layers: Optional[List[str]] = None,
        background_color: Tuple[int, int, int, int] = (0, 0, 0, 255),
    ) -> bool:
        """
        Export a map to PNG image.

        Args:
            map_data: MapData instance to export
            output_path: Path to save PNG file
            scale: Scale factor (1.0 = original size, 0.5 = half size, 2.0 = double size)
            render_layers: List of layer IDs to render (None = all visible layers)
            background_color: RGBA background color

        Returns:
            True if successful, False otherwise
        """
        try:
            # Calculate dimensions
            tile_size = int(map_data.dimensions.tile_size * scale)
            width = map_data.dimensions.width * tile_size
            height = map_data.dimensions.height * tile_size

            # Create surface
            surface = pygame.Surface((width, height), pygame.SRCALPHA)
            surface.fill(background_color)

            # Get tileset
            if not self.tileset_manager:
                print("Warning: No tileset manager provided, cannot render tiles")
                pygame.image.save(surface, output_path)
                return True

            tileset = None
            if map_data.tileset.tileset_id:
                tileset = self.tileset_manager.get_tileset(map_data.tileset.tileset_id)
                if tileset and not tileset.tiles:
                    self.tileset_manager.load_tileset(map_data.tileset.tileset_id)

            # Get layers to render
            layer_ids = render_layers or map_data.layer_manager.get_render_order()

            # Render each layer
            for layer_id in layer_ids:
                layer = map_data.layer_manager.get_layer(layer_id)
                if not layer or not layer.properties.visible:
                    continue

                # Render layer
                self._render_layer_to_surface(
                    surface, layer, tileset, tile_size, map_data.dimensions
                )

            # Save to file
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            pygame.image.save(surface, output_path)

            print(f"Exported map to PNG: {output_path}")
            return True

        except Exception as e:
            print(f"Error exporting map to PNG: {e}")
            return False

    def _render_layer_to_surface(
        self,
        surface: pygame.Surface,
        layer: EnhancedTileLayer,
        tileset: Optional[TilesetInfo],
        tile_size: int,
        dimensions: MapDimensions,
    ) -> None:
        """Render a single layer to the surface."""
        # Create layer surface with opacity
        layer_surface = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)

        for y in range(min(layer.height, dimensions.height)):
            for x in range(min(layer.width, dimensions.width)):
                tile_id = layer.get_tile(x, y)
                if tile_id == 0:  # Empty tile
                    continue

                # Get tile surface
                tile_surface = None
                if tileset:
                    tile_surface = tileset.tiles.get(tile_id)

                if tile_surface:
                    # Scale tile if needed
                    if tile_size != tileset.tile_width:
                        tile_surface = pygame.transform.scale(tile_surface, (tile_size, tile_size))

                    # Draw tile
                    layer_surface.blit(tile_surface, (x * tile_size, y * tile_size))
                else:
                    # Draw placeholder for missing tiles
                    pygame.draw.rect(
                        layer_surface,
                        (100, 100, 100, 128),
                        (x * tile_size, y * tile_size, tile_size, tile_size),
                    )

        # Apply opacity
        if layer.properties.opacity < 1.0:
            alpha = int(layer.properties.opacity * 255)
            layer_surface.set_alpha(alpha)

        # Blit to main surface
        surface.blit(layer_surface, (0, 0))

    def export_minimap(
        self,
        map_data: MapData,
        output_path: str,
        max_size: int = 256,
    ) -> bool:
        """
        Export a minimap (scaled down version).

        Args:
            map_data: MapData instance to export
            output_path: Path to save PNG file
            max_size: Maximum width or height in pixels

        Returns:
            True if successful, False otherwise
        """
        # Calculate scale to fit within max_size
        width_scale = max_size / (map_data.dimensions.width * map_data.dimensions.tile_size)
        height_scale = max_size / (map_data.dimensions.height * map_data.dimensions.tile_size)
        scale = min(width_scale, height_scale)

        return self.export_map_to_png(map_data, output_path, scale=scale)


class TiledTMXImporter:
    """
    Import maps from Tiled TMX format.

    Supports basic TMX features:
    - Tile layers
    - Tileset references
    - Map properties
    - Layer properties
    """

    def __init__(self, project_root: Path, tileset_manager: Optional[TilesetManager] = None):
        """
        Initialize TMX importer.

        Args:
            project_root: Root directory of the project
            tileset_manager: TilesetManager instance
        """
        self.project_root = Path(project_root)
        self.tileset_manager = tileset_manager

    def import_tmx(self, tmx_path: str) -> Optional[MapData]:
        """
        Import a TMX file and convert to MapData.

        Args:
            tmx_path: Path to TMX file

        Returns:
            MapData instance or None on error
        """
        try:
            tree = ET.parse(tmx_path)
            root = tree.getroot()

            # Parse map attributes
            width = int(root.get("width", 50))
            height = int(root.get("height", 50))
            tile_width = int(root.get("tilewidth", 32))
            tile_height = int(root.get("tileheight", 32))

            # Extract map name from filename
            map_name = Path(tmx_path).stem

            # Create MapData
            map_data = MapData(
                name=map_name,
                width=width,
                height=height,
                tile_size=tile_width,
            )

            # Parse tilesets
            tileset_mapping = {}
            for tileset_elem in root.findall("tileset"):
                tileset_info = self._parse_tileset(tileset_elem, tmx_path)
                if tileset_info:
                    tileset_mapping[int(tileset_elem.get("firstgid", 1))] = tileset_info

            # Set first tileset as map tileset
            if tileset_mapping:
                first_tileset = list(tileset_mapping.values())[0]
                map_data.tileset.tileset_id = first_tileset.tileset_id
                map_data.tileset.tileset_name = first_tileset.name
                map_data.tileset.tileset_path = first_tileset.image_path

            # Parse layers
            layer_manager = LayerManager(width, height)

            for layer_elem in root.findall("layer"):
                layer = self._parse_layer(layer_elem, width, height, tileset_mapping)
                if layer:
                    layer_manager.layers[layer.properties.layer_id] = layer
                    layer_manager.root_ids.append(layer.properties.layer_id)

            map_data.layer_manager = layer_manager

            # Parse properties
            properties_elem = root.find("properties")
            if properties_elem is not None:
                self._parse_map_properties(properties_elem, map_data)

            print(f"Imported TMX map: {map_name}")
            return map_data

        except Exception as e:
            print(f"Error importing TMX file: {e}")
            return None

    def _parse_tileset(self, tileset_elem: ET.Element, tmx_path: str) -> Optional[TilesetInfo]:
        """Parse a tileset element from TMX."""
        try:
            # Check for external tileset (TSX file)
            source = tileset_elem.get("source")
            if source:
                # TODO: Load external TSX file
                print(f"Warning: External tilesets not yet supported: {source}")
                return None

            # Embedded tileset
            name = tileset_elem.get("name", "Imported Tileset")
            tile_width = int(tileset_elem.get("tilewidth", 32))
            tile_height = int(tileset_elem.get("tileheight", 32))
            spacing = int(tileset_elem.get("spacing", 0))
            margin = int(tileset_elem.get("margin", 0))

            # Find image
            image_elem = tileset_elem.find("image")
            if image_elem is None:
                return None

            image_source = image_elem.get("source")
            if not image_source:
                return None

            # Convert to absolute path, then to relative path from project root
            tmx_dir = os.path.dirname(os.path.abspath(tmx_path))
            image_abs_path = os.path.join(tmx_dir, image_source)
            image_rel_path = os.path.relpath(image_abs_path, self.project_root)

            # Create tileset info
            tileset_id = f"tileset_{name.lower().replace(' ', '_')}"
            tileset_info = TilesetInfo(
                tileset_id=tileset_id,
                name=name,
                image_path=image_rel_path,
                tile_width=tile_width,
                tile_height=tile_height,
                spacing=spacing,
                margin=margin,
            )

            # Add to tileset manager if available
            if self.tileset_manager:
                try:
                    self.tileset_manager.add_tileset(
                        tileset_id=tileset_id,
                        name=name,
                        image_path=image_rel_path,
                        tile_width=tile_width,
                        tile_height=tile_height,
                        spacing=spacing,
                        margin=margin,
                    )
                    self.tileset_manager.load_tileset(tileset_id)
                except ValueError:
                    # Tileset already exists
                    pass

            return tileset_info

        except Exception as e:
            print(f"Error parsing tileset: {e}")
            return None

    def _parse_layer(
        self,
        layer_elem: ET.Element,
        width: int,
        height: int,
        tileset_mapping: Dict[int, TilesetInfo],
    ) -> Optional[EnhancedTileLayer]:
        """Parse a layer element from TMX."""
        try:
            name = layer_elem.get("name", "Imported Layer")
            visible = layer_elem.get("visible", "1") == "1"
            opacity = float(layer_elem.get("opacity", 1.0))

            # Create layer properties
            props = LayerProperties(
                name=name,
                visible=visible,
                opacity=opacity,
            )

            # Parse tile data
            data_elem = layer_elem.find("data")
            if data_elem is None:
                return None

            tiles = self._parse_tile_data(data_elem, width, height, tileset_mapping)

            # Create layer
            layer = EnhancedTileLayer(width=width, height=height, tiles=tiles, properties=props)

            return layer

        except Exception as e:
            print(f"Error parsing layer: {e}")
            return None

    def _parse_tile_data(
        self,
        data_elem: ET.Element,
        width: int,
        height: int,
        tileset_mapping: Dict[int, TilesetInfo],
    ) -> List[List[int]]:
        """Parse tile data from TMX layer data element."""
        encoding = data_elem.get("encoding")
        compression = data_elem.get("compression")

        # Initialize empty tiles
        tiles = [[0 for _ in range(width)] for _ in range(height)]

        if encoding == "csv":
            # CSV format
            csv_data = data_elem.text.strip()
            tile_ids = [int(x.strip()) for x in csv_data.split(",")]

            idx = 0
            for y in range(height):
                for x in range(width):
                    if idx < len(tile_ids):
                        tiles[y][x] = tile_ids[idx]
                    idx += 1

        elif encoding == "base64":
            # Base64 format
            data = base64.b64decode(data_elem.text.strip())

            if compression == "zlib":
                data = zlib.decompress(data)
            elif compression == "gzip":
                import gzip

                data = gzip.decompress(data)

            # Parse as array of 32-bit integers
            tile_count = len(data) // 4
            tile_ids = []
            for i in range(tile_count):
                tile_id = int.from_bytes(data[i * 4 : i * 4 + 4], byteorder="little")
                tile_ids.append(tile_id)

            idx = 0
            for y in range(height):
                for x in range(width):
                    if idx < len(tile_ids):
                        tiles[y][x] = tile_ids[idx]
                    idx += 1

        else:
            # XML tile elements
            for tile_elem in data_elem.findall("tile"):
                gid = int(tile_elem.get("gid", 0))
                # Parse x, y from tile position (not always available in TMX)
                # This is a simplified implementation

        return tiles

    def _parse_map_properties(self, properties_elem: ET.Element, map_data: MapData) -> None:
        """Parse map properties from TMX."""
        for prop_elem in properties_elem.findall("property"):
            name = prop_elem.get("name")
            value = prop_elem.get("value")

            if name == "bgm":
                map_data.properties.bgm = value
            elif name == "weather":
                map_data.properties.weather = value
            elif name == "encounter_rate":
                map_data.properties.encounter_rate = int(value)
            elif name == "description":
                map_data.metadata.description = value
            elif name == "author":
                map_data.metadata.author = value
            else:
                # Store in custom properties
                map_data.properties.custom_properties[name] = value


class TiledTMXExporter:
    """
    Export maps to Tiled TMX format.

    Supports basic TMX features:
    - Tile layers
    - Tileset references
    - Map properties
    - Layer properties
    """

    def export_to_tmx(
        self,
        map_data: MapData,
        output_path: str,
        encoding: str = "csv",
    ) -> bool:
        """
        Export MapData to TMX file.

        Args:
            map_data: MapData instance to export
            output_path: Path to save TMX file
            encoding: Tile data encoding ("csv", "base64", "xml")

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create root element
            map_elem = ET.Element("map")
            map_elem.set("version", "1.10")
            map_elem.set("tiledversion", "1.10.0")
            map_elem.set("orientation", "orthogonal")
            map_elem.set("renderorder", "right-down")
            map_elem.set("width", str(map_data.dimensions.width))
            map_elem.set("height", str(map_data.dimensions.height))
            map_elem.set("tilewidth", str(map_data.dimensions.tile_size))
            map_elem.set("tileheight", str(map_data.dimensions.tile_size))
            map_elem.set("infinite", "0")
            map_elem.set("nextlayerid", str(len(map_data.layer_manager.layers) + 1))
            map_elem.set("nextobjectid", "1")

            # Add tileset
            if map_data.tileset.tileset_path:
                tileset_elem = ET.SubElement(map_elem, "tileset")
                tileset_elem.set("firstgid", "1")
                tileset_elem.set("name", map_data.tileset.tileset_name or "tileset")
                tileset_elem.set("tilewidth", str(map_data.dimensions.tile_size))
                tileset_elem.set("tileheight", str(map_data.dimensions.tile_size))

                image_elem = ET.SubElement(tileset_elem, "image")
                image_elem.set("source", map_data.tileset.tileset_path)
                # TODO: Get actual image dimensions
                image_elem.set("width", "512")
                image_elem.set("height", "512")

            # Add properties
            if (
                map_data.properties.bgm
                or map_data.properties.weather
                or map_data.metadata.description
            ):
                props_elem = ET.SubElement(map_elem, "properties")

                if map_data.metadata.description:
                    prop = ET.SubElement(props_elem, "property")
                    prop.set("name", "description")
                    prop.set("value", map_data.metadata.description)

                if map_data.metadata.author:
                    prop = ET.SubElement(props_elem, "property")
                    prop.set("name", "author")
                    prop.set("value", map_data.metadata.author)

                if map_data.properties.bgm:
                    prop = ET.SubElement(props_elem, "property")
                    prop.set("name", "bgm")
                    prop.set("value", map_data.properties.bgm)

                if map_data.properties.weather != "none":
                    prop = ET.SubElement(props_elem, "property")
                    prop.set("name", "weather")
                    prop.set("value", map_data.properties.weather)

                if map_data.properties.encounter_rate > 0:
                    prop = ET.SubElement(props_elem, "property")
                    prop.set("name", "encounter_rate")
                    prop.set("value", str(map_data.properties.encounter_rate))

            # Add layers
            layer_ids = map_data.layer_manager.get_render_order()
            for layer_id in layer_ids:
                layer = map_data.layer_manager.get_layer(layer_id)
                if layer:
                    self._add_layer_element(map_elem, layer, encoding)

            # Write to file
            tree = ET.ElementTree(map_elem)
            ET.indent(tree, space="  ")

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            tree.write(output_path, encoding="utf-8", xml_declaration=True)

            print(f"Exported map to TMX: {output_path}")
            return True

        except Exception as e:
            print(f"Error exporting to TMX: {e}")
            return False

    def _add_layer_element(
        self, map_elem: ET.Element, layer: EnhancedTileLayer, encoding: str
    ) -> None:
        """Add a layer element to the TMX."""
        layer_elem = ET.SubElement(map_elem, "layer")
        layer_elem.set("id", str(hash(layer.properties.layer_id) % 10000))
        layer_elem.set("name", layer.properties.name)
        layer_elem.set("width", str(layer.width))
        layer_elem.set("height", str(layer.height))

        if not layer.properties.visible:
            layer_elem.set("visible", "0")

        if layer.properties.opacity < 1.0:
            layer_elem.set("opacity", str(layer.properties.opacity))

        # Add tile data
        data_elem = ET.SubElement(layer_elem, "data")
        data_elem.set("encoding", encoding)

        if encoding == "csv":
            # CSV format
            csv_rows = []
            for y in range(layer.height):
                row = ",".join(str(layer.tiles[y][x]) for x in range(layer.width))
                csv_rows.append(row)
            data_elem.text = "\n" + ",\n".join(csv_rows) + "\n"

        elif encoding == "base64":
            # Base64 format
            data_elem.set("compression", "zlib")
            tile_data = bytearray()
            for y in range(layer.height):
                for x in range(layer.width):
                    tile_id = layer.tiles[y][x]
                    tile_data.extend(tile_id.to_bytes(4, byteorder="little"))

            compressed = zlib.compress(bytes(tile_data))
            encoded = base64.b64encode(compressed)
            data_elem.text = "\n" + encoded.decode("utf-8") + "\n"


class TilesetImageImporter:
    """
    Import tileset images and create tileset configurations.

    Supports:
    - Automatic tile detection
    - Spacing and margin detection
    - Metadata creation
    """

    def __init__(self, tileset_manager: TilesetManager):
        """
        Initialize tileset importer.

        Args:
            tileset_manager: TilesetManager instance
        """
        self.tileset_manager = tileset_manager

    def import_tileset_image(
        self,
        image_path: str,
        tileset_name: str,
        tile_width: int = 32,
        tile_height: int = 32,
        spacing: int = 0,
        margin: int = 0,
        auto_detect: bool = False,
    ) -> Optional[TilesetInfo]:
        """
        Import a tileset image.

        Args:
            image_path: Path to tileset image
            tileset_name: Name for the tileset
            tile_width: Width of each tile
            tile_height: Height of each tile
            spacing: Spacing between tiles
            margin: Margin around edges
            auto_detect: Attempt to auto-detect spacing/margin

        Returns:
            TilesetInfo instance or None on error
        """
        try:
            if auto_detect:
                detected = self._auto_detect_grid(image_path, tile_width, tile_height)
                if detected:
                    spacing, margin = detected

            # Generate tileset ID
            tileset_id = f"tileset_{tileset_name.lower().replace(' ', '_')}"

            # Add to manager
            tileset = self.tileset_manager.add_tileset(
                tileset_id=tileset_id,
                name=tileset_name,
                image_path=image_path,
                tile_width=tile_width,
                tile_height=tile_height,
                spacing=spacing,
                margin=margin,
            )

            # Load tileset
            self.tileset_manager.load_tileset(tileset_id)

            print(f"Imported tileset: {tileset_name} ({tileset.tile_count} tiles)")
            return tileset

        except Exception as e:
            print(f"Error importing tileset image: {e}")
            return None

    def _auto_detect_grid(
        self, image_path: str, tile_width: int, tile_height: int
    ) -> Optional[Tuple[int, int]]:
        """
        Auto-detect spacing and margin.

        Args:
            image_path: Path to tileset image
            tile_width: Expected tile width
            tile_height: Expected tile height

        Returns:
            Tuple of (spacing, margin) or None
        """
        try:
            # Load image
            image = pygame.image.load(image_path)
            width = image.get_width()
            height = image.get_height()

            # Try different margin/spacing combinations
            for margin in range(0, min(tile_width, 10)):
                for spacing in range(0, min(tile_width, 10)):
                    # Calculate if this fits evenly
                    available_width = width - (2 * margin)
                    available_height = height - (2 * margin)

                    if available_width <= 0 or available_height <= 0:
                        continue

                    cols = (available_width + spacing) // (tile_width + spacing)
                    rows = (available_height + spacing) // (tile_height + spacing)

                    # Check if it fits exactly
                    expected_width = 2 * margin + cols * tile_width + (cols - 1) * spacing
                    expected_height = 2 * margin + rows * tile_height + (rows - 1) * spacing

                    if expected_width == width and expected_height == height:
                        return (spacing, margin)

            return None

        except Exception as e:
            print(f"Error auto-detecting grid: {e}")
            return None


class LegacyFormatConverter:
    """
    Convert legacy map formats to current format.

    Supports:
    - Old 3-layer format to EnhancedTileLayer
    - JSON schema migrations
    - Data format upgrades
    """

    def convert_legacy_map(self, legacy_data: Dict[str, Any]) -> Optional[MapData]:
        """
        Convert legacy map data to current format.

        Args:
            legacy_data: Legacy map data dictionary

        Returns:
            MapData instance or None on error
        """
        try:
            # Check if already in new format
            if "layer_manager" in legacy_data:
                layers_data = legacy_data["layer_manager"]
                if isinstance(layers_data, dict) and layers_data.get("version", 1) >= 2:
                    # Already in new format
                    return MapData.from_dict(legacy_data)

            # Convert from old 3-layer format
            metadata = legacy_data.get("metadata", {})
            dimensions = legacy_data.get("dimensions", {})

            map_data = MapData(
                name=metadata.get("name", "Converted Map"),
                width=dimensions.get("width", 50),
                height=dimensions.get("height", 50),
                tile_size=dimensions.get("tile_size", 32),
            )

            # Convert metadata
            map_data.metadata.description = metadata.get("description", "")
            map_data.metadata.author = metadata.get("author", "")
            map_data.metadata.created_date = metadata.get("created_date", "")
            map_data.metadata.modified_date = metadata.get("modified_date", "")
            map_data.metadata.tags = metadata.get("tags", [])
            map_data.metadata.folder = metadata.get("folder", "")

            # Convert tileset
            tileset = legacy_data.get("tileset", {})
            map_data.tileset.tileset_id = tileset.get("tileset_id", "")
            map_data.tileset.tileset_name = tileset.get("tileset_name", "")
            map_data.tileset.tileset_path = tileset.get("tileset_path", "")

            # Convert properties
            props = legacy_data.get("properties", {})
            map_data.properties.bgm = props.get("bgm", "")
            map_data.properties.ambient_sound = props.get("ambient_sound", "")
            map_data.properties.encounter_rate = props.get("encounter_rate", 0)
            map_data.properties.wrap_x = props.get("wrap_x", False)
            map_data.properties.wrap_y = props.get("wrap_y", False)
            map_data.properties.weather = props.get("weather", "none")
            map_data.properties.time_of_day = props.get("time_of_day", "day")
            map_data.properties.custom_properties = props.get("custom_properties", {})

            # Convert layers
            layers_data = legacy_data.get("layers", {})

            if "layer_order" in layers_data:
                # Old 3-layer format with layer_order
                layer_order = layers_data.get("layer_order", ["ground", "objects", "overlay"])
                layer_data_dict = layers_data.get("layer_data", {})

                layer_names = {
                    "ground": "Ground",
                    "objects": "Objects",
                    "overlay": "Overlay",
                }

                for i, layer_key in enumerate(layer_order):
                    tiles = layer_data_dict.get(layer_key, [])
                    if not tiles:
                        # Create empty tiles
                        tiles = [
                            [0 for _ in range(map_data.dimensions.width)]
                            for _ in range(map_data.dimensions.height)
                        ]

                    props = LayerProperties(name=layer_names.get(layer_key, layer_key.capitalize()))
                    layer = EnhancedTileLayer(
                        width=map_data.dimensions.width,
                        height=map_data.dimensions.height,
                        tiles=tiles,
                        properties=props,
                    )

                    map_data.layer_manager.layers[props.layer_id] = layer
                    map_data.layer_manager.root_ids.append(props.layer_id)

            # Convert entities and events
            map_data.entities = legacy_data.get("entities", [])
            map_data.events = legacy_data.get("events", [])

            print(f"Converted legacy map: {map_data.metadata.name}")
            return map_data

        except Exception as e:
            print(f"Error converting legacy map: {e}")
            return None

    def batch_convert_maps(self, input_dir: Path, output_dir: Path) -> Tuple[int, int]:
        """
        Batch convert all maps in a directory.

        Args:
            input_dir: Directory containing legacy maps
            output_dir: Directory to save converted maps

        Returns:
            Tuple of (success_count, fail_count)
        """
        success_count = 0
        fail_count = 0

        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        for map_file in input_dir.glob("*.json"):
            try:
                with open(map_file, "r") as f:
                    legacy_data = json.load(f)

                converted = self.convert_legacy_map(legacy_data)
                if converted:
                    output_file = output_dir / map_file.name
                    with open(output_file, "w") as f:
                        json.dump(converted.to_dict(), f, indent=2)
                    success_count += 1
                else:
                    fail_count += 1

            except Exception as e:
                print(f"Error converting {map_file.name}: {e}")
                fail_count += 1

        print(f"Batch conversion complete: {success_count} success, {fail_count} failed")
        return success_count, fail_count
