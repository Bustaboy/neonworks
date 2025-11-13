"""
Configuration Loader

Load configuration files in JSON or YAML format.
Provides unified interface for reading game configuration data.
Supports loading from both filesystem and .nwdata packages.
"""

import io
import json
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml


class ConfigLoader:
    """
    Load configuration files in multiple formats.

    Supports both JSON and YAML formats with automatic format detection.
    YAML is preferred for game data as it supports comments and is more readable.

    Automatically loads from .nwdata packages when running in packaged mode.
    """

    @staticmethod
    def load(file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Load configuration file (auto-detect format).

        Automatically loads from package if running in packaged mode.

        Args:
            file_path: Path to configuration file

        Returns:
            Dictionary containing configuration data

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is not supported or invalid
        """
        # Check if running from package
        try:
            from neonworks.export.package_loader import get_global_loader

            loader = get_global_loader()
            if loader is not None:
                return ConfigLoader._load_from_package(loader, file_path)
        except ImportError:
            pass  # Package loader not available, continue with filesystem

        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        # Detect format by extension
        extension = file_path.suffix.lower()

        if extension in [".yaml", ".yml"]:
            return ConfigLoader.load_yaml(file_path)
        elif extension == ".json":
            return ConfigLoader.load_json(file_path)
        else:
            # Try to parse as both formats
            try:
                return ConfigLoader.load_json(file_path)
            except:
                try:
                    return ConfigLoader.load_yaml(file_path)
                except:
                    raise ValueError(f"Unsupported configuration format: {extension}")

    @staticmethod
    def load_json(file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Load JSON configuration file.

        Args:
            file_path: Path to JSON file

        Returns:
            Dictionary containing configuration data
        """
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def load_yaml(file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Load YAML configuration file.

        Args:
            file_path: Path to YAML file

        Returns:
            Dictionary containing configuration data
        """
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    @staticmethod
    def save(
        data: Dict[str, Any], file_path: Union[str, Path], format: Optional[str] = None
    ):
        """
        Save configuration data to file.

        Args:
            data: Configuration data
            file_path: Output file path
            format: Format ('json' or 'yaml'), auto-detect if None
        """
        file_path = Path(file_path)

        # Detect format
        if format is None:
            extension = file_path.suffix.lower()
            if extension in [".yaml", ".yml"]:
                format = "yaml"
            elif extension == ".json":
                format = "json"
            else:
                format = "yaml"  # Default to YAML

        if format == "yaml":
            ConfigLoader.save_yaml(data, file_path)
        else:
            ConfigLoader.save_json(data, file_path)

    @staticmethod
    def save_json(data: Dict[str, Any], file_path: Union[str, Path]):
        """Save data as JSON"""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def save_yaml(data: Dict[str, Any], file_path: Union[str, Path]):
        """Save data as YAML"""
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(
                data, f, default_flow_style=False, allow_unicode=True, sort_keys=False
            )

    @staticmethod
    def _load_from_package(loader, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Load configuration from package"""
        file_path = Path(file_path)

        # Convert to relative path if needed
        relative_path = str(file_path)
        if file_path.is_absolute():
            # Try to find the file in the package by name
            # This assumes project files are at the root of the package
            relative_path = file_path.name

        # Normalize path separators
        relative_path = relative_path.replace("\\", "/")

        # Load file data from package
        data = loader.load_file(relative_path)

        # Detect format and parse
        extension = file_path.suffix.lower()

        if extension in [".yaml", ".yml"]:
            return yaml.safe_load(io.BytesIO(data))
        elif extension == ".json":
            return json.loads(data.decode("utf-8"))
        else:
            # Try JSON first, then YAML
            try:
                return json.loads(data.decode("utf-8"))
            except:
                return yaml.safe_load(io.BytesIO(data))


class GameDataLoader:
    """
    Load game-specific data like items, buildings, enemies, etc.
    Supports hot-reloading for development.
    """

    def __init__(self, data_dir: Union[str, Path]):
        """
        Initialize game data loader.

        Args:
            data_dir: Directory containing game data files
        """
        self.data_dir = Path(data_dir)
        self._cache: Dict[str, Dict[str, Any]] = {}

    def load_data(self, filename: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Load game data file.

        Args:
            filename: Name of data file (with or without extension)
            use_cache: Whether to use cached data

        Returns:
            Game data dictionary
        """
        # Check cache
        if use_cache and filename in self._cache:
            return self._cache[filename]

        # Find file (try multiple extensions)
        file_path = None
        for ext in [".yaml", ".yml", ".json"]:
            candidate = self.data_dir / f"{filename}{ext}"
            if candidate.exists():
                file_path = candidate
                break

        if file_path is None:
            # Try without adding extension
            candidate = self.data_dir / filename
            if candidate.exists():
                file_path = candidate
            else:
                raise FileNotFoundError(f"Game data file not found: {filename}")

        # Load data
        data = ConfigLoader.load(file_path)

        # Cache it
        self._cache[filename] = data

        return data

    def reload_data(self, filename: str) -> Dict[str, Any]:
        """
        Reload data file (bypass cache).

        Args:
            filename: Name of data file

        Returns:
            Reloaded game data
        """
        # Clear cache for this file
        if filename in self._cache:
            del self._cache[filename]

        return self.load_data(filename, use_cache=False)

    def clear_cache(self):
        """Clear all cached data"""
        self._cache.clear()

    def get_item(self, filename: str, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Get specific item from a data file.

        Args:
            filename: Data file name
            item_id: ID of the item to retrieve

        Returns:
            Item data or None if not found
        """
        data = self.load_data(filename)

        # Support different data structures
        if isinstance(data, dict):
            if item_id in data:
                return data[item_id]
            # Check if there's a nested structure like {"items": {...}}
            for key, value in data.items():
                if isinstance(value, dict) and item_id in value:
                    return value[item_id]

        return None


# Example YAML configuration format for game data
EXAMPLE_BUILDING_YAML = """
# Building Definitions for Neon Collapse
# This file defines all buildable structures

buildings:
  shelter:
    name: "Shelter"
    description: "Basic shelter protecting from the elements"
    cost:
      wood: 10
      stone: 5
    build_time: 60  # seconds
    max_level: 3
    upgrades:
      - level: 2
        cost:
          wood: 20
          stone: 10
        bonus: "Increased capacity"
      - level: 3
        cost:
          wood: 40
          stone: 20
        bonus: "Weather resistance"

  workshop:
    name: "Workshop"
    description: "Craft tools and equipment"
    cost:
      wood: 15
      metal: 5
    build_time: 90
    max_level: 2
    requires:
      - shelter  # Must have shelter first

  farm:
    name: "Farm"
    description: "Grow food for your settlement"
    cost:
      wood: 8
      seeds: 5
    build_time: 120
    production:
      food: 10  # per day
    max_level: 3
"""

EXAMPLE_ITEM_YAML = """
# Item Definitions
# Define all items that can be collected or crafted

items:
  wood:
    name: "Wood"
    description: "Basic building material"
    type: "resource"
    stackable: true
    max_stack: 100
    icon: "assets/items/wood.png"

  stone:
    name: "Stone"
    description: "Sturdy building material"
    type: "resource"
    stackable: true
    max_stack: 100
    icon: "assets/items/stone.png"

  sword:
    name: "Iron Sword"
    description: "A basic but effective weapon"
    type: "weapon"
    stackable: false
    damage: 15
    durability: 100
    icon: "assets/items/sword.png"
    crafting:
      metal: 3
      wood: 1
      time: 30  # seconds
"""
