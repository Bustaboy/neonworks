"""
Comprehensive tests for Configuration Loader

Tests loading/saving config files in JSON and YAML formats, caching, and package loading.
"""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import yaml

from neonworks.data.config_loader import ConfigLoader, GameDataLoader


class TestConfigLoaderJSON:
    """Test ConfigLoader with JSON files"""

    def test_load_json_file(self, tmp_path):
        """Test loading JSON configuration file"""
        config_file = tmp_path / "config.json"
        test_data = {"name": "TestGame", "version": "1.0", "settings": {"fps": 60}}

        with open(config_file, "w") as f:
            json.dump(test_data, f)

        data = ConfigLoader.load_json(config_file)

        assert data == test_data
        assert data["name"] == "TestGame"
        assert data["settings"]["fps"] == 60

    def test_load_json_with_unicode(self, tmp_path):
        """Test loading JSON with unicode characters"""
        config_file = tmp_path / "config.json"
        test_data = {"message": "Hello 世界", "emoji": "🎮"}

        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f, ensure_ascii=False)

        data = ConfigLoader.load_json(config_file)

        assert data["message"] == "Hello 世界"
        assert data["emoji"] == "🎮"

    def test_save_json_file(self, tmp_path):
        """Test saving JSON configuration file"""
        config_file = tmp_path / "output.json"
        test_data = {"name": "TestGame", "version": "2.0"}

        ConfigLoader.save_json(test_data, config_file)

        assert config_file.exists()

        with open(config_file, "r") as f:
            loaded_data = json.load(f)

        assert loaded_data == test_data


class TestConfigLoaderYAML:
    """Test ConfigLoader with YAML files"""

    def test_load_yaml_file(self, tmp_path):
        """Test loading YAML configuration file"""
        config_file = tmp_path / "config.yaml"
        test_data = {"name": "TestGame", "version": "1.0", "settings": {"fps": 60}}

        with open(config_file, "w") as f:
            yaml.dump(test_data, f)

        data = ConfigLoader.load_yaml(config_file)

        assert data == test_data
        assert data["name"] == "TestGame"
        assert data["settings"]["fps"] == 60

    def test_load_yaml_with_comments(self, tmp_path):
        """Test loading YAML with comments"""
        config_file = tmp_path / "config.yml"
        yaml_content = """# Game Configuration
name: TestGame  # Game name
version: 1.0  # Version number
settings:
  fps: 60  # Target FPS
"""

        with open(config_file, "w") as f:
            f.write(yaml_content)

        data = ConfigLoader.load_yaml(config_file)

        assert data["name"] == "TestGame"
        assert data["version"] == 1.0
        assert data["settings"]["fps"] == 60

    def test_save_yaml_file(self, tmp_path):
        """Test saving YAML configuration file"""
        config_file = tmp_path / "output.yaml"
        test_data = {"name": "TestGame", "version": "2.0", "list": [1, 2, 3]}

        ConfigLoader.save_yaml(test_data, config_file)

        assert config_file.exists()

        with open(config_file, "r") as f:
            loaded_data = yaml.safe_load(f)

        assert loaded_data == test_data


class TestConfigLoaderAutoDetect:
    """Test ConfigLoader auto-detection"""

    def test_load_auto_detects_json(self, tmp_path):
        """Test load auto-detects JSON format by extension"""
        config_file = tmp_path / "config.json"
        test_data = {"name": "TestGame"}

        with open(config_file, "w") as f:
            json.dump(test_data, f)

        data = ConfigLoader.load(config_file)

        assert data == test_data

    def test_load_auto_detects_yaml(self, tmp_path):
        """Test load auto-detects YAML format by extension"""
        config_file = tmp_path / "config.yaml"
        test_data = {"name": "TestGame"}

        with open(config_file, "w") as f:
            yaml.dump(test_data, f)

        data = ConfigLoader.load(config_file)

        assert data == test_data

    def test_load_auto_detects_yml(self, tmp_path):
        """Test load auto-detects .yml extension"""
        config_file = tmp_path / "config.yml"
        test_data = {"name": "TestGame"}

        with open(config_file, "w") as f:
            yaml.dump(test_data, f)

        data = ConfigLoader.load(config_file)

        assert data == test_data

    def test_load_unknown_extension_tries_json_first(self, tmp_path):
        """Test load tries JSON first for unknown extensions"""
        config_file = tmp_path / "config.txt"
        test_data = {"name": "TestGame"}

        with open(config_file, "w") as f:
            json.dump(test_data, f)

        data = ConfigLoader.load(config_file)

        assert data == test_data

    def test_load_unknown_extension_tries_yaml_fallback(self, tmp_path):
        """Test load tries YAML as fallback for unknown extensions"""
        config_file = tmp_path / "config.txt"
        yaml_content = "name: TestGame\nversion: 1.0"

        with open(config_file, "w") as f:
            f.write(yaml_content)

        data = ConfigLoader.load(config_file)

        assert data["name"] == "TestGame"
        assert data["version"] == 1.0

    def test_load_file_not_found_raises_error(self, tmp_path):
        """Test load raises FileNotFoundError for missing files"""
        config_file = tmp_path / "nonexistent.json"

        with pytest.raises(FileNotFoundError):
            ConfigLoader.load(config_file)

    def test_load_invalid_format_raises_error(self, tmp_path):
        """Test load raises ValueError for invalid format"""
        config_file = tmp_path / "config.txt"

        # Content that will fail both JSON and YAML parsing
        with open(config_file, "wb") as f:
            f.write(b"\xff\xfe\x00\x00Invalid binary content")

        with pytest.raises(ValueError, match="Unsupported configuration format"):
            ConfigLoader.load(config_file)


class TestConfigLoaderSave:
    """Test ConfigLoader save with format detection"""

    def test_save_auto_detects_json(self, tmp_path):
        """Test save auto-detects JSON format"""
        config_file = tmp_path / "config.json"
        test_data = {"name": "TestGame"}

        ConfigLoader.save(test_data, config_file)

        assert config_file.exists()

        with open(config_file, "r") as f:
            loaded = json.load(f)

        assert loaded == test_data

    def test_save_auto_detects_yaml(self, tmp_path):
        """Test save auto-detects YAML format"""
        config_file = tmp_path / "config.yaml"
        test_data = {"name": "TestGame"}

        ConfigLoader.save(test_data, config_file)

        assert config_file.exists()

        with open(config_file, "r") as f:
            loaded = yaml.safe_load(f)

        assert loaded == test_data

    def test_save_defaults_to_yaml(self, tmp_path):
        """Test save defaults to YAML for unknown extensions"""
        config_file = tmp_path / "config.txt"
        test_data = {"name": "TestGame"}

        ConfigLoader.save(test_data, config_file)

        assert config_file.exists()

        # Should be loadable as YAML
        with open(config_file, "r") as f:
            loaded = yaml.safe_load(f)

        assert loaded == test_data

    def test_save_with_explicit_format_json(self, tmp_path):
        """Test save with explicit JSON format"""
        config_file = tmp_path / "config.txt"
        test_data = {"name": "TestGame"}

        ConfigLoader.save(test_data, config_file, format="json")

        with open(config_file, "r") as f:
            loaded = json.load(f)

        assert loaded == test_data

    def test_save_with_explicit_format_yaml(self, tmp_path):
        """Test save with explicit YAML format"""
        config_file = tmp_path / "config.txt"
        test_data = {"name": "TestGame"}

        ConfigLoader.save(test_data, config_file, format="yaml")

        with open(config_file, "r") as f:
            loaded = yaml.safe_load(f)

        assert loaded == test_data


class TestConfigLoaderPackageMode:
    """Test ConfigLoader with package loader"""

    @patch("neonworks.export.package_loader.get_global_loader")
    def test_load_from_package_json(self, mock_get_loader, tmp_path):
        """Test loading from package with JSON file"""
        # Setup mock package loader
        mock_loader = Mock()
        test_data = {"name": "PackagedGame"}
        mock_loader.load_file.return_value = json.dumps(test_data).encode("utf-8")
        mock_get_loader.return_value = mock_loader

        data = ConfigLoader.load("config.json")

        assert data == test_data
        mock_loader.load_file.assert_called_once()

    @patch("neonworks.export.package_loader.get_global_loader")
    def test_load_from_package_yaml(self, mock_get_loader, tmp_path):
        """Test loading from package with YAML file"""
        # Setup mock package loader
        mock_loader = Mock()
        test_data = {"name": "PackagedGame"}
        mock_loader.load_file.return_value = yaml.dump(test_data).encode("utf-8")
        mock_get_loader.return_value = mock_loader

        data = ConfigLoader.load("config.yaml")

        assert data == test_data
        mock_loader.load_file.assert_called_once()

    @patch("neonworks.export.package_loader.get_global_loader")
    def test_load_from_package_none_falls_back_to_filesystem(self, mock_get_loader, tmp_path):
        """Test loading falls back to filesystem when package loader is None"""
        mock_get_loader.return_value = None

        config_file = tmp_path / "config.json"
        test_data = {"name": "TestGame"}

        with open(config_file, "w") as f:
            json.dump(test_data, f)

        data = ConfigLoader.load(config_file)

        assert data == test_data


class TestGameDataLoader:
    """Test GameDataLoader"""

    def test_init(self, tmp_path):
        """Test GameDataLoader initialization"""
        loader = GameDataLoader(tmp_path)

        assert loader.data_dir == tmp_path
        assert loader._cache == {}

    def test_load_data_yaml(self, tmp_path):
        """Test loading game data from YAML file"""
        data_file = tmp_path / "items.yaml"
        test_data = {"sword": {"damage": 10}, "shield": {"defense": 5}}

        with open(data_file, "w") as f:
            yaml.dump(test_data, f)

        loader = GameDataLoader(tmp_path)
        data = loader.load_data("items")

        assert data == test_data

    def test_load_data_json(self, tmp_path):
        """Test loading game data from JSON file"""
        data_file = tmp_path / "items.json"
        test_data = {"sword": {"damage": 10}}

        with open(data_file, "w") as f:
            json.dump(test_data, f)

        loader = GameDataLoader(tmp_path)
        data = loader.load_data("items")

        assert data == test_data

    def test_load_data_with_extension(self, tmp_path):
        """Test loading game data with explicit extension"""
        data_file = tmp_path / "items.yaml"
        test_data = {"sword": {"damage": 10}}

        with open(data_file, "w") as f:
            yaml.dump(test_data, f)

        loader = GameDataLoader(tmp_path)
        data = loader.load_data("items.yaml")

        assert data == test_data

    def test_load_data_caching(self, tmp_path):
        """Test game data is cached"""
        data_file = tmp_path / "items.yaml"
        test_data = {"sword": {"damage": 10}}

        with open(data_file, "w") as f:
            yaml.dump(test_data, f)

        loader = GameDataLoader(tmp_path)

        # Load first time
        data1 = loader.load_data("items")

        # Load second time (should use cache)
        data2 = loader.load_data("items")

        assert data1 is data2  # Same object reference
        assert "items" in loader._cache

    def test_load_data_no_cache(self, tmp_path):
        """Test loading game data without cache"""
        data_file = tmp_path / "items.yaml"
        test_data = {"sword": {"damage": 10}}

        with open(data_file, "w") as f:
            yaml.dump(test_data, f)

        loader = GameDataLoader(tmp_path)

        # Load with cache disabled
        data1 = loader.load_data("items", use_cache=False)
        data2 = loader.load_data("items", use_cache=False)

        # Should be different objects (not cached)
        assert data1 == data2
        assert data1 is not data2

    def test_load_data_file_not_found(self, tmp_path):
        """Test loading non-existent file raises error"""
        loader = GameDataLoader(tmp_path)

        with pytest.raises(FileNotFoundError):
            loader.load_data("nonexistent")

    def test_reload_data(self, tmp_path):
        """Test reloading data bypasses cache"""
        data_file = tmp_path / "items.yaml"
        test_data = {"sword": {"damage": 10}}

        with open(data_file, "w") as f:
            yaml.dump(test_data, f)

        loader = GameDataLoader(tmp_path)

        # Load and cache
        data1 = loader.load_data("items")

        # Modify file
        new_data = {"sword": {"damage": 20}}
        with open(data_file, "w") as f:
            yaml.dump(new_data, f)

        # Regular load would return cached data
        data2 = loader.load_data("items")
        assert data2["sword"]["damage"] == 10  # Still cached

        # Reload bypasses cache
        data3 = loader.reload_data("items")
        assert data3["sword"]["damage"] == 20  # New data

    def test_clear_cache(self, tmp_path):
        """Test clearing the cache"""
        data_file = tmp_path / "items.yaml"
        test_data = {"sword": {"damage": 10}}

        with open(data_file, "w") as f:
            yaml.dump(test_data, f)

        loader = GameDataLoader(tmp_path)

        # Load and cache
        loader.load_data("items")
        assert "items" in loader._cache

        # Clear cache
        loader.clear_cache()

        assert loader._cache == {}

    def test_get_item_simple_dict(self, tmp_path):
        """Test getting specific item from simple dict structure"""
        data_file = tmp_path / "items.yaml"
        test_data = {"sword": {"damage": 10}, "shield": {"defense": 5}}

        with open(data_file, "w") as f:
            yaml.dump(test_data, f)

        loader = GameDataLoader(tmp_path)
        item = loader.get_item("items", "sword")

        assert item is not None
        assert item["damage"] == 10

    def test_get_item_nested_dict(self, tmp_path):
        """Test getting item from nested dict structure"""
        data_file = tmp_path / "items.yaml"
        test_data = {"items": {"sword": {"damage": 10}, "shield": {"defense": 5}}}

        with open(data_file, "w") as f:
            yaml.dump(test_data, f)

        loader = GameDataLoader(tmp_path)
        item = loader.get_item("items", "sword")

        assert item is not None
        assert item["damage"] == 10

    def test_get_item_not_found(self, tmp_path):
        """Test getting non-existent item returns None"""
        data_file = tmp_path / "items.yaml"
        test_data = {"sword": {"damage": 10}}

        with open(data_file, "w") as f:
            yaml.dump(test_data, f)

        loader = GameDataLoader(tmp_path)
        item = loader.get_item("items", "nonexistent")

        assert item is None


# Run tests with: pytest tests/test_config_loader.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
