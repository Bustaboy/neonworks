"""
Comprehensive tests for Data module

Tests config loading, serialization, and game data management.
"""

import json
import tempfile
from pathlib import Path

import pytest
import yaml

from neonworks.core.ecs import (
    Building,
    Entity,
    GridPosition,
    Health,
    ResourceStorage,
    Sprite,
    Transform,
    World,
)
from neonworks.data.config_loader import ConfigLoader, GameDataLoader
from neonworks.data.serialization import GameSerializer

# ===========================
# ConfigLoader Tests
# ===========================


class TestConfigLoader:
    """Test configuration loading"""

    def test_load_json(self):
        """Test loading JSON file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json"
            config_data = {"game_title": "Test Game", "version": "1.0", "fps": 60}

            # Write JSON file
            with open(config_file, "w") as f:
                json.dump(config_data, f)

            # Load it
            loaded = ConfigLoader.load_json(config_file)

            assert loaded["game_title"] == "Test Game"
            assert loaded["version"] == "1.0"
            assert loaded["fps"] == 60

    def test_load_yaml(self):
        """Test loading YAML file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.yaml"
            config_data = {
                "game_title": "Test Game",
                "settings": {"audio": True, "graphics": "high"},
            }

            # Write YAML file
            with open(config_file, "w") as f:
                yaml.dump(config_data, f)

            # Load it
            loaded = ConfigLoader.load_yaml(config_file)

            assert loaded["game_title"] == "Test Game"
            assert loaded["settings"]["audio"] is True

    def test_load_auto_detect_json(self):
        """Test auto-detecting JSON format"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json"
            config_data = {"type": "json_test"}

            with open(config_file, "w") as f:
                json.dump(config_data, f)

            loaded = ConfigLoader.load(config_file)

            assert loaded["type"] == "json_test"

    def test_load_auto_detect_yaml(self):
        """Test auto-detecting YAML format"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.yml"
            config_data = {"type": "yaml_test"}

            with open(config_file, "w") as f:
                yaml.dump(config_data, f)

            loaded = ConfigLoader.load(config_file)

            assert loaded["type"] == "yaml_test"

    def test_load_nonexistent_file(self):
        """Test loading non-existent file raises error"""
        with pytest.raises(FileNotFoundError):
            ConfigLoader.load("/nonexistent/file.json")

    def test_save_json(self):
        """Test saving JSON file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "output.json"
            config_data = {"saved": True, "value": 42}

            ConfigLoader.save_json(config_data, config_file)

            assert config_file.exists()

            # Verify content
            with open(config_file, "r") as f:
                loaded = json.load(f)

            assert loaded["saved"] is True
            assert loaded["value"] == 42

    def test_save_yaml(self):
        """Test saving YAML file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "output.yaml"
            config_data = {"saved": True, "nested": {"key": "value"}}

            ConfigLoader.save_yaml(config_data, config_file)

            assert config_file.exists()

            # Verify content
            with open(config_file, "r") as f:
                loaded = yaml.safe_load(f)

            assert loaded["saved"] is True
            assert loaded["nested"]["key"] == "value"

    def test_save_auto_detect_format(self):
        """Test auto-detecting format when saving"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test with .json extension
            json_file = Path(tmpdir) / "config.json"
            data = {"format": "json"}

            ConfigLoader.save(data, json_file)

            loaded = ConfigLoader.load(json_file)
            assert loaded["format"] == "json"

            # Test with .yaml extension
            yaml_file = Path(tmpdir) / "config.yaml"
            data = {"format": "yaml"}

            ConfigLoader.save(data, yaml_file)

            loaded = ConfigLoader.load(yaml_file)
            assert loaded["format"] == "yaml"

    def test_save_explicit_format(self):
        """Test saving with explicit format"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Save as JSON with explicit format
            file_path = Path(tmpdir) / "config.txt"
            data = {"test": "value"}

            ConfigLoader.save(data, file_path, format="json")

            # Verify it's valid JSON
            with open(file_path, "r") as f:
                loaded = json.load(f)

            assert loaded["test"] == "value"


# ===========================
# GameDataLoader Tests
# ===========================


class TestGameDataLoader:
    """Test game data loading"""

    def test_data_loader_creation(self):
        """Test creating data loader"""
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = GameDataLoader(tmpdir)

            assert loader.data_dir == Path(tmpdir)
            assert len(loader._cache) == 0

    def test_load_data_json(self):
        """Test loading game data from JSON"""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir)
            loader = GameDataLoader(data_dir)

            # Create test data file
            data_file = data_dir / "items.json"
            items_data = {
                "sword": {"name": "Sword", "damage": 10},
                "shield": {"name": "Shield", "defense": 5},
            }

            with open(data_file, "w") as f:
                json.dump(items_data, f)

            # Load it
            loaded = loader.load_data("items")

            assert "sword" in loaded
            assert loaded["sword"]["damage"] == 10

    def test_load_data_yaml(self):
        """Test loading game data from YAML"""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir)
            loader = GameDataLoader(data_dir)

            # Create test data file
            data_file = data_dir / "enemies.yaml"
            enemies_data = {
                "goblin": {"name": "Goblin", "health": 20},
                "orc": {"name": "Orc", "health": 50},
            }

            with open(data_file, "w") as f:
                yaml.dump(enemies_data, f)

            # Load it
            loaded = loader.load_data("enemies")

            assert "goblin" in loaded
            assert loaded["goblin"]["health"] == 20

    def test_load_data_caching(self):
        """Test that data is cached"""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir)
            loader = GameDataLoader(data_dir)

            # Create test data file
            data_file = data_dir / "test.json"
            with open(data_file, "w") as f:
                json.dump({"cached": True}, f)

            # Load first time
            data1 = loader.load_data("test")

            # Load second time (should be cached)
            data2 = loader.load_data("test")

            # Should be same object (cached)
            assert data1 is data2
            assert "test" in loader._cache

    def test_load_data_bypass_cache(self):
        """Test loading without cache"""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir)
            loader = GameDataLoader(data_dir)

            # Create test data file
            data_file = data_dir / "test.json"
            with open(data_file, "w") as f:
                json.dump({"value": 1}, f)

            # Load with cache
            data1 = loader.load_data("test", use_cache=True)

            # Modify file
            with open(data_file, "w") as f:
                json.dump({"value": 2}, f)

            # Load without cache
            data2 = loader.load_data("test", use_cache=False)

            # First should be old value (cached)
            assert data1["value"] == 1
            # Second should be new value
            assert data2["value"] == 2

    def test_reload_data(self):
        """Test reloading data"""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir)
            loader = GameDataLoader(data_dir)

            # Create and load initial data
            data_file = data_dir / "test.json"
            with open(data_file, "w") as f:
                json.dump({"version": 1}, f)

            data1 = loader.load_data("test")
            assert data1["version"] == 1

            # Modify file
            with open(data_file, "w") as f:
                json.dump({"version": 2}, f)

            # Reload
            data2 = loader.reload_data("test")
            assert data2["version"] == 2

    def test_clear_cache(self):
        """Test clearing cache"""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir)
            loader = GameDataLoader(data_dir)

            # Create and load data
            data_file = data_dir / "test.json"
            with open(data_file, "w") as f:
                json.dump({"test": True}, f)

            loader.load_data("test")
            assert len(loader._cache) == 1

            # Clear cache
            loader.clear_cache()
            assert len(loader._cache) == 0

    def test_get_item(self):
        """Test getting specific item"""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir)
            loader = GameDataLoader(data_dir)

            # Create data file with items
            data_file = data_dir / "weapons.json"
            weapons_data = {
                "sword": {"name": "Iron Sword", "damage": 15},
                "axe": {"name": "Battle Axe", "damage": 20},
            }

            with open(data_file, "w") as f:
                json.dump(weapons_data, f)

            # Get specific item
            sword = loader.get_item("weapons", "sword")

            assert sword is not None
            assert sword["name"] == "Iron Sword"
            assert sword["damage"] == 15

    def test_get_item_nested(self):
        """Test getting item from nested structure"""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir)
            loader = GameDataLoader(data_dir)

            # Create data file with nested structure
            data_file = data_dir / "game_data.json"
            game_data = {
                "items": {
                    "potion": {"name": "Health Potion", "healing": 50},
                    "key": {"name": "Golden Key", "type": "quest"},
                }
            }

            with open(data_file, "w") as f:
                json.dump(game_data, f)

            # Get specific item
            potion = loader.get_item("game_data", "potion")

            assert potion is not None
            assert potion["name"] == "Health Potion"

    def test_get_nonexistent_item(self):
        """Test getting non-existent item returns None"""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir)
            loader = GameDataLoader(data_dir)

            # Create data file
            data_file = data_dir / "items.json"
            with open(data_file, "w") as f:
                json.dump({"sword": {"damage": 10}}, f)

            # Try to get non-existent item
            item = loader.get_item("items", "shield")

            assert item is None

    def test_load_nonexistent_data_file(self):
        """Test loading non-existent data file raises error"""
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = GameDataLoader(tmpdir)

            with pytest.raises(FileNotFoundError):
                loader.load_data("nonexistent")


# ===========================
# GameSerializer Tests
# ===========================


class TestGameSerializer:
    """Test game state serialization"""

    def test_serialize_grid_position(self):
        """Test serializing GridPosition component"""
        component = GridPosition(grid_x=10, grid_y=20, layer=1)

        data = GameSerializer.serialize_component(component)

        assert data["_type"] == "GridPosition"
        assert data["grid_x"] == 10
        assert data["grid_y"] == 20
        assert data["layer"] == 1

    def test_serialize_transform(self):
        """Test serializing Transform component"""
        component = Transform(x=100.0, y=200.0, rotation=45.0, scale_x=2.0, scale_y=2.0)

        data = GameSerializer.serialize_component(component)

        assert data["_type"] == "Transform"
        assert data["x"] == 100.0
        assert data["y"] == 200.0
        assert data["rotation"] == 45.0
        assert data["scale_x"] == 2.0

    def test_serialize_sprite(self):
        """Test serializing Sprite component"""
        component = Sprite(
            texture="hero.png",
            width=32,
            height=32,
            color=(255, 255, 255, 255),
            visible=True,
        )

        data = GameSerializer.serialize_component(component)

        assert data["_type"] == "Sprite"
        assert data["texture"] == "hero.png"
        assert data["width"] == 32
        assert data["visible"] is True

    def test_serialize_health(self):
        """Test serializing Health component"""
        component = Health(current=75, maximum=100, regeneration=1.0)

        data = GameSerializer.serialize_component(component)

        assert data["_type"] == "Health"
        assert data["current"] == 75
        assert data["maximum"] == 100
        assert data["regeneration"] == 1.0

    def test_serialize_building(self):
        """Test serializing Building component"""
        component = Building(
            building_type="shelter",
            construction_progress=0.5,
            is_constructed=False,
            level=1,
            max_level=3,
        )

        data = GameSerializer.serialize_component(component)

        assert data["_type"] == "Building"
        assert data["building_type"] == "shelter"
        assert data["construction_progress"] == 0.5
        assert not data["is_constructed"]
        assert data["level"] == 1


# ===========================
# Integration Tests
# ===========================


class TestDataIntegration:
    """Integration tests for data module"""

    def test_config_and_game_data_workflow(self):
        """Test complete workflow of config and game data"""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir)

            # 1. Save game configuration
            config_file = data_dir / "game_config.yaml"
            game_config = {
                "title": "My Game",
                "version": "1.0",
                "settings": {"fps": 60, "resolution": [1920, 1080]},
            }

            ConfigLoader.save(game_config, config_file)

            # 2. Create game data files
            items_file = data_dir / "items.json"
            items_data = {
                "health_potion": {
                    "name": "Health Potion",
                    "effect": "heal",
                    "amount": 50,
                },
                "mana_potion": {
                    "name": "Mana Potion",
                    "effect": "restore_mana",
                    "amount": 30,
                },
            }

            with open(items_file, "w") as f:
                json.dump(items_data, f)

            # 3. Load configuration
            loaded_config = ConfigLoader.load(config_file)
            assert loaded_config["title"] == "My Game"

            # 4. Load game data
            loader = GameDataLoader(data_dir)
            items = loader.load_data("items")
            assert "health_potion" in items

            # 5. Get specific item
            health_potion = loader.get_item("items", "health_potion")
            assert health_potion["amount"] == 50

    def test_serialization_workflow(self):
        """Test entity serialization workflow"""
        world = World()

        # Create entity with components
        entity = world.create_entity()
        entity.add_component(GridPosition(grid_x=5, grid_y=10))
        entity.add_component(Transform(x=160.0, y=320.0))
        entity.add_component(Health(current=80, maximum=100))

        # Serialize components
        grid_pos = entity.get_component(GridPosition)
        transform = entity.get_component(Transform)
        health = entity.get_component(Health)

        serialized_data = {
            "grid_position": GameSerializer.serialize_component(grid_pos),
            "transform": GameSerializer.serialize_component(transform),
            "health": GameSerializer.serialize_component(health),
        }

        # Verify serialization
        assert serialized_data["grid_position"]["grid_x"] == 5
        assert serialized_data["transform"]["x"] == 160.0
        assert serialized_data["health"]["current"] == 80

    def test_yaml_complex_data_structure(self):
        """Test loading complex YAML data structure"""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir)

            # Create complex YAML file
            buildings_file = data_dir / "buildings.yaml"
            buildings_data = {
                "shelter": {
                    "name": "Shelter",
                    "cost": {"wood": 10, "stone": 5},
                    "build_time": 60,
                    "upgrades": [
                        {"level": 2, "cost": {"wood": 20}, "bonus": "capacity"},
                        {"level": 3, "cost": {"wood": 40}, "bonus": "weather"},
                    ],
                },
                "workshop": {
                    "name": "Workshop",
                    "cost": {"wood": 15, "metal": 5},
                    "requires": ["shelter"],
                },
            }

            with open(buildings_file, "w") as f:
                yaml.dump(buildings_data, f)

            # Load and verify
            loader = GameDataLoader(data_dir)
            buildings = loader.load_data("buildings")

            assert "shelter" in buildings
            assert buildings["shelter"]["cost"]["wood"] == 10
            assert len(buildings["shelter"]["upgrades"]) == 2
            assert buildings["workshop"]["requires"] == ["shelter"]
