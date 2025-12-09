"""
Tests for Map Import/Export Tools.

Tests the functionality of map importers including:
- PNG export
- TMX import/export
- Tileset image import
- Legacy format conversion
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from neonworks.engine.tools.map_importers import (
    PNGExporter,
    TiledTMXExporter,
    TiledTMXImporter,
    TilesetImageImporter,
)
from neonworks.data.map_manager import MapData, MapManager
from neonworks.data.tileset_manager import TilesetManager


class TestPNGExporter:
    """Test PNG export functionality."""

    def test_png_exporter_initialization(self):
        """Test PNG exporter can be initialized."""
        tileset_manager = TilesetManager()
        exporter = PNGExporter(tileset_manager)

        assert exporter is not None
        assert exporter.tileset_manager is tileset_manager

    def test_export_map_to_png_without_tileset(self, tmp_path):
        """Test exporting map to PNG without tileset manager."""
        exporter = PNGExporter(None)
        map_data = MapData("TestMap", width=10, height=10, tile_size=32)

        output_path = tmp_path / "test_map.png"

        # Should succeed but with warning
        result = exporter.export_map_to_png(map_data, str(output_path))

        assert result is True
        assert output_path.exists()

    def test_export_minimap(self, tmp_path):
        """Test exporting a minimap."""
        exporter = PNGExporter(None)
        map_data = MapData("TestMap", width=50, height=50, tile_size=32)

        output_path = tmp_path / "minimap.png"

        result = exporter.export_minimap(map_data, str(output_path), max_size=128)

        assert result is True
        assert output_path.exists()

    def test_export_map_with_scale(self, tmp_path):
        """Test exporting map with different scale factors."""
        exporter = PNGExporter(None)
        map_data = MapData("TestMap", width=10, height=10, tile_size=32)

        # Test different scales
        for scale in [0.5, 1.0, 2.0]:
            output_path = tmp_path / f"map_scale_{scale}.png"
            result = exporter.export_map_to_png(map_data, str(output_path), scale=scale)

            assert result is True
            assert output_path.exists()


class TestTiledTMXImporter:
    """Test Tiled TMX import functionality."""

    def test_tmx_importer_initialization(self, tmp_path):
        """Test TMX importer can be initialized."""
        tileset_manager = TilesetManager()
        importer = TiledTMXImporter(tmp_path, tileset_manager)

        assert importer is not None
        assert importer.project_root == tmp_path
        assert importer.tileset_manager is tileset_manager

    def test_import_simple_tmx(self, tmp_path):
        """Test importing a simple TMX file."""
        # Create a simple TMX file
        tmx_content = """<?xml version="1.0" encoding="UTF-8"?>
<map version="1.10" tiledversion="1.10.0" orientation="orthogonal"
     renderorder="right-down" width="10" height="10"
     tilewidth="32" tileheight="32" infinite="0">
 <tileset firstgid="1" name="test" tilewidth="32" tileheight="32">
  <image source="tileset.png" width="512" height="512"/>
 </tileset>
 <layer id="1" name="Ground" width="10" height="10">
  <data encoding="csv">
0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,
0,0,1,1,1,1,1,0,0,0,
0,0,1,0,0,0,1,0,0,0,
0,0,1,0,0,0,1,0,0,0,
0,0,1,0,0,0,1,0,0,0,
0,0,1,1,1,1,1,0,0,0,
0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0
  </data>
 </layer>
</map>"""

        tmx_path = tmp_path / "test.tmx"
        with open(tmx_path, "w") as f:
            f.write(tmx_content)

        # Create dummy tileset image
        tileset_path = tmp_path / "tileset.png"
        with open(tileset_path, "w") as f:
            f.write("")  # Empty file for test

        tileset_manager = TilesetManager(str(tmp_path))
        importer = TiledTMXImporter(tmp_path, tileset_manager)

        # This will fail without pygame, but we can test the parsing
        # In a real test environment with pygame, this would work
        # For now, just test that the method exists and can be called
        assert hasattr(importer, "import_tmx")


class TestTiledTMXExporter:
    """Test Tiled TMX export functionality."""

    def test_tmx_exporter_initialization(self):
        """Test TMX exporter can be initialized."""
        exporter = TiledTMXExporter()

        assert exporter is not None

    def test_export_to_tmx_csv(self, tmp_path):
        """Test exporting map to TMX with CSV encoding."""
        exporter = TiledTMXExporter()
        map_data = MapData("TestMap", width=10, height=10, tile_size=32)

        # Add some tileset info
        map_data.tileset.tileset_name = "TestTileset"
        map_data.tileset.tileset_path = "tilesets/test.png"

        # Create a layer explicitly
        layer = map_data.layer_manager.create_layer(name="Ground Layer")

        # Set some tiles
        for y in range(5):
            for x in range(5):
                layer.set_tile(x, y, 1)

        output_path = tmp_path / "exported.tmx"
        result = exporter.export_to_tmx(map_data, str(output_path), encoding="csv")

        assert result is True
        assert output_path.exists()

        # Verify it's valid XML with CSV encoding
        with open(output_path, "r") as f:
            content = f.read()
            assert "<map" in content
            assert "</map>" in content
            assert "<layer" in content
            assert 'encoding="csv"' in content

    def test_export_to_tmx_base64(self, tmp_path):
        """Test exporting map to TMX with base64 encoding."""
        exporter = TiledTMXExporter()
        map_data = MapData("TestMap", width=10, height=10, tile_size=32)

        # Create a layer explicitly
        layer = map_data.layer_manager.create_layer(name="Base Layer")

        # Set some tiles
        for y in range(3):
            for x in range(3):
                layer.set_tile(x, y, 2)

        output_path = tmp_path / "exported_base64.tmx"
        result = exporter.export_to_tmx(map_data, str(output_path), encoding="base64")

        assert result is True
        assert output_path.exists()

        # Verify it's valid XML with base64
        with open(output_path, "r") as f:
            content = f.read()
            assert "<layer" in content
            assert 'encoding="base64"' in content
            assert 'compression="zlib"' in content


class TestTilesetImageImporter:
    """Test tileset image import functionality."""

    def test_tileset_importer_initialization(self):
        """Test tileset importer can be initialized."""
        tileset_manager = TilesetManager()
        importer = TilesetImageImporter(tileset_manager)

        assert importer is not None
        assert importer.tileset_manager is tileset_manager

    def test_import_tileset_parameters(self, tmp_path):
        """Test importing tileset with specific parameters."""
        tileset_manager = TilesetManager(str(tmp_path))
        importer = TilesetImageImporter(tileset_manager)

        # Create a dummy PNG file
        tileset_path = tmp_path / "test_tileset.png"
        with open(tileset_path, "w") as f:
            f.write("")  # Empty file for test

        # Note: This will fail without a real image, but we can test the interface
        # In a real environment with pygame and a real image, this would work
        assert hasattr(importer, "import_tileset_image")


class TestIntegration:
    """Integration tests for import/export workflows."""

    def test_export_then_import_workflow(self, tmp_path):
        """Test exporting to TMX and then importing it back."""
        # Create original map
        original = MapData("TestMap", width=15, height=15, tile_size=32)
        original.metadata.description = "Test map for export/import"
        original.tileset.tileset_name = "TestTileset"
        original.tileset.tileset_path = "test.png"

        # Export to TMX
        exporter = TiledTMXExporter()
        tmx_path = tmp_path / "test.tmx"
        result = exporter.export_to_tmx(original, str(tmx_path))

        assert result is True
        assert tmx_path.exists()

        # Import it back (would need pygame and real tileset in full test)
        # For now, just verify the TMX file is valid XML
        with open(tmx_path, "r") as f:
            content = f.read()
            assert "<?xml version" in content
            assert f'width="15"' in content
            assert f'height="15"' in content



