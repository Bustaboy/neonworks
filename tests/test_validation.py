"""
Comprehensive tests for validation module

Tests project configuration validation, building definitions, item definitions,
character definitions, and deprecation warnings.
"""

import pytest

from neonworks.core.validation import (
    ValidationError,
    get_deprecation_warnings,
    validate_building_definitions,
    validate_character_definitions,
    validate_config_file_references,
    validate_item_definitions,
    validate_project_config,
)


# ===========================
# Project Config Validation Tests
# ===========================


class TestProjectConfigValidation:
    """Test project configuration validation"""

    def test_valid_config(self):
        """Test validation of a valid configuration"""
        config = {
            "metadata": {
                "name": "Test Game",
                "version": "1.0.0",
                "description": "A test game",
                "author": "Test Author",
            },
            "paths": {
                "assets": "assets",
                "levels": "levels",
                "scripts": "scripts",
                "saves": "saves",
                "config": "config",
            },
            "settings": {
                "window_width": 1280,
                "window_height": 720,
                "window_title": "Test Game",
                "fullscreen": False,
                "tile_size": 32,
                "grid_width": 100,
                "grid_height": 100,
            },
        }

        errors = validate_project_config(config)
        assert errors == []

    def test_missing_required_sections(self):
        """Test detection of missing required sections"""
        config = {}
        errors = validate_project_config(config)

        assert len(errors) == 3
        assert any("Missing required section: 'metadata'" in e for e in errors)
        assert any("Missing required section: 'paths'" in e for e in errors)
        assert any("Missing required section: 'settings'" in e for e in errors)

    def test_missing_metadata_fields(self):
        """Test detection of missing metadata fields"""
        config = {
            "metadata": {"name": "Test Game"},
            "paths": {},
            "settings": {},
        }

        errors = validate_project_config(config)

        assert any("metadata.version: Missing required field" in e for e in errors)
        assert any("metadata.description: Missing required field" in e for e in errors)
        assert any("metadata.author: Missing required field" in e for e in errors)

    def test_invalid_metadata_types(self):
        """Test detection of invalid metadata field types"""
        config = {
            "metadata": {
                "name": 123,  # Should be string
                "version": "1.0.0",
                "description": True,  # Should be string
                "author": "Test Author",
            },
            "paths": {},
            "settings": {},
        }

        errors = validate_project_config(config)

        assert any("metadata.name: Expected str" in e for e in errors)
        assert any("metadata.description: Expected str" in e for e in errors)

    def test_empty_metadata_fields(self):
        """Test detection of empty metadata fields"""
        config = {
            "metadata": {
                "name": "  ",
                "version": "1.0.0",
                "description": "",
                "author": "Test Author",
            },
            "paths": {},
            "settings": {},
        }

        errors = validate_project_config(config)

        assert any("metadata.name: Cannot be empty" in e for e in errors)
        assert any("metadata.description: Cannot be empty" in e for e in errors)

    def test_invalid_version_format(self):
        """Test detection of invalid version formats"""
        test_cases = [
            ("1", "Too few parts"),
            ("1.0.0.0", "Too many parts"),
            ("1.a.0", "Non-numeric"),
            ("v1.0.0", "Prefix"),
        ]

        for version, description in test_cases:
            config = {
                "metadata": {
                    "name": "Test",
                    "version": version,
                    "description": "Test",
                    "author": "Test",
                },
                "paths": {},
                "settings": {},
            }

            errors = validate_project_config(config)
            assert any(
                "metadata.version: Invalid version format" in e for e in errors
            ), f"Failed to detect invalid version: {version} ({description})"

    def test_valid_version_formats(self):
        """Test acceptance of valid version formats"""
        valid_versions = ["1.0", "1.0.0", "0.1", "10.20.30"]

        for version in valid_versions:
            config = {
                "metadata": {
                    "name": "Test",
                    "version": version,
                    "description": "Test",
                    "author": "Test",
                },
                "paths": {},
                "settings": {},
            }

            errors = validate_project_config(config)
            version_errors = [e for e in errors if "version" in e.lower()]
            assert len(version_errors) == 0, f"Valid version {version} rejected"

    def test_optional_engine_version(self):
        """Test validation of optional engine_version field"""
        config = {
            "metadata": {
                "name": "Test",
                "version": "1.0.0",
                "description": "Test",
                "author": "Test",
                "engine_version": 123,  # Should be string
            },
            "paths": {},
            "settings": {},
        }

        errors = validate_project_config(config)
        assert any("metadata.engine_version: Must be a string" in e for e in errors)


class TestPathsValidation:
    """Test paths section validation"""

    def test_invalid_path_types(self):
        """Test detection of invalid path types"""
        config = {
            "metadata": {
                "name": "Test",
                "version": "1.0.0",
                "description": "Test",
                "author": "Test",
            },
            "paths": {
                "assets": 123,  # Should be string
                "levels": [],  # Should be string
            },
            "settings": {},
        }

        errors = validate_project_config(config)

        assert any("paths.assets: Expected string" in e for e in errors)
        assert any("paths.levels: Expected string" in e for e in errors)

    def test_empty_paths(self):
        """Test detection of empty path values"""
        config = {
            "metadata": {
                "name": "Test",
                "version": "1.0.0",
                "description": "Test",
                "author": "Test",
            },
            "paths": {"assets": "  ", "levels": ""},
            "settings": {},
        }

        errors = validate_project_config(config)

        assert any("paths.assets: Cannot be empty" in e for e in errors)
        assert any("paths.levels: Cannot be empty" in e for e in errors)

    def test_absolute_paths_rejected(self):
        """Test that absolute paths are rejected"""
        config = {
            "metadata": {
                "name": "Test",
                "version": "1.0.0",
                "description": "Test",
                "author": "Test",
            },
            "paths": {
                "assets": "/absolute/path",
                "levels": "\\absolute\\windows\\path",
            },
            "settings": {},
        }

        errors = validate_project_config(config)

        assert any("paths.assets: Must be relative path" in e for e in errors)
        assert any("paths.levels: Must be relative path" in e for e in errors)


class TestSettingsValidation:
    """Test settings section validation"""

    def test_display_settings_types(self):
        """Test validation of display settings types"""
        config = {
            "metadata": {
                "name": "Test",
                "version": "1.0.0",
                "description": "Test",
                "author": "Test",
            },
            "paths": {},
            "settings": {
                "window_width": "1280",  # Should be int
                "window_height": "720",  # Should be int
                "window_title": 123,  # Should be str
                "fullscreen": "true",  # Should be bool
            },
        }

        errors = validate_project_config(config)

        assert any("settings.window_width: Expected int" in e for e in errors)
        assert any("settings.window_height: Expected int" in e for e in errors)
        assert any("settings.window_title: Expected str" in e for e in errors)
        assert any("settings.fullscreen: Expected bool" in e for e in errors)

    def test_window_size_bounds(self):
        """Test window size boundary validation"""
        # Test too small
        config_small = {
            "metadata": {
                "name": "Test",
                "version": "1.0.0",
                "description": "Test",
                "author": "Test",
            },
            "paths": {},
            "settings": {"window_width": 100, "window_height": 100},
        }

        errors = validate_project_config(config_small)
        assert any("settings.window_width: Value 100 is too small" in e for e in errors)
        assert any(
            "settings.window_height: Value 100 is too small" in e for e in errors
        )

        # Test too large
        config_large = {
            "metadata": {
                "name": "Test",
                "version": "1.0.0",
                "description": "Test",
                "author": "Test",
            },
            "paths": {},
            "settings": {"window_width": 10000, "window_height": 10000},
        }

        errors = validate_project_config(config_large)
        assert any(
            "settings.window_width: Value 10000 is too large" in e for e in errors
        )
        assert any(
            "settings.window_height: Value 10000 is too large" in e for e in errors
        )

    def test_empty_window_title(self):
        """Test detection of empty window title"""
        config = {
            "metadata": {
                "name": "Test",
                "version": "1.0.0",
                "description": "Test",
                "author": "Test",
            },
            "paths": {},
            "settings": {"window_title": "  "},
        }

        errors = validate_project_config(config)
        assert any("settings.window_title: Cannot be empty" in e for e in errors)

    def test_gameplay_settings_bounds(self):
        """Test gameplay settings boundary validation"""
        config = {
            "metadata": {
                "name": "Test",
                "version": "1.0.0",
                "description": "Test",
                "author": "Test",
            },
            "paths": {},
            "settings": {
                "tile_size": 5,  # Too small (min 8)
                "grid_width": 0,  # Too small (min 1)
                "grid_height": 2000,  # Too large (max 1000)
            },
        }

        errors = validate_project_config(config)

        assert any("settings.tile_size: Value 5 out of range" in e for e in errors)
        assert any("settings.grid_width: Value 0 out of range" in e for e in errors)
        assert any("settings.grid_height: Value 2000 out of range" in e for e in errors)

    def test_feature_flags_types(self):
        """Test feature flag type validation"""
        config = {
            "metadata": {
                "name": "Test",
                "version": "1.0.0",
                "description": "Test",
                "author": "Test",
            },
            "paths": {},
            "settings": {
                "enable_base_building": "yes",  # Should be bool
                "enable_survival": 1,  # Should be bool
                "enable_turn_based": "true",  # Should be bool
                "enable_combat": None,  # Should be bool
            },
        }

        errors = validate_project_config(config)

        assert any("settings.enable_base_building: Expected bool" in e for e in errors)
        assert any("settings.enable_survival: Expected bool" in e for e in errors)
        assert any("settings.enable_turn_based: Expected bool" in e for e in errors)
        assert any("settings.enable_combat: Expected bool" in e for e in errors)

    def test_initial_scene_type(self):
        """Test initial_scene setting validation"""
        config = {
            "metadata": {
                "name": "Test",
                "version": "1.0.0",
                "description": "Test",
                "author": "Test",
            },
            "paths": {},
            "settings": {"initial_scene": 123},  # Should be string
        }

        errors = validate_project_config(config)
        assert any("settings.initial_scene: Must be a string" in e for e in errors)

    def test_data_file_paths_types(self):
        """Test data file path type validation"""
        config = {
            "metadata": {
                "name": "Test",
                "version": "1.0.0",
                "description": "Test",
                "author": "Test",
            },
            "paths": {},
            "settings": {
                "building_definitions": 123,  # Should be string
                "item_definitions": [],  # Should be string
                "character_definitions": {},  # Should be string
                "quest_definitions": None,  # Should be string
            },
        }

        errors = validate_project_config(config)

        assert any(
            "settings.building_definitions: Expected string" in e for e in errors
        )
        assert any("settings.item_definitions: Expected string" in e for e in errors)
        assert any(
            "settings.character_definitions: Expected string" in e for e in errors
        )
        assert any("settings.quest_definitions: Expected string" in e for e in errors)

    def test_export_settings_types(self):
        """Test export settings type validation"""
        config = {
            "metadata": {
                "name": "Test",
                "version": "1.0.0",
                "description": "Test",
                "author": "Test",
            },
            "paths": {},
            "settings": {
                "export_version": 1.0,  # Should be string
                "export_publisher": 123,  # Should be string
                "export_description": [],  # Should be string
                "export_encrypt": "yes",  # Should be bool
                "export_compress": 1,  # Should be bool
                "export_console": "false",  # Should be bool
            },
        }

        errors = validate_project_config(config)

        assert any("settings.export_version: Expected str" in e for e in errors)
        assert any("settings.export_publisher: Expected str" in e for e in errors)
        assert any("settings.export_description: Expected str" in e for e in errors)
        assert any("settings.export_encrypt: Expected bool" in e for e in errors)
        assert any("settings.export_compress: Expected bool" in e for e in errors)
        assert any("settings.export_console: Expected bool" in e for e in errors)


# ===========================
# Building Definitions Validation Tests
# ===========================


class TestBuildingDefinitionsValidation:
    """Test building definitions validation"""

    def test_valid_building_definitions(self):
        """Test validation of valid building definitions"""
        buildings = {
            "farm": {
                "name": "Farm",
                "cost": {"wood": 50, "stone": 20},
                "build_time": 10.0,
            },
            "house": {
                "name": "House",
                "cost": {"wood": 100},
                "build_time": 15.0,
            },
        }

        errors = validate_building_definitions(buildings)
        assert errors == []

    def test_invalid_root_type(self):
        """Test rejection of non-dictionary root"""
        errors = validate_building_definitions("not a dict")
        assert errors == ["Building definitions must be a dictionary"]

        errors = validate_building_definitions([])
        assert errors == ["Building definitions must be a dictionary"]

    def test_invalid_building_type(self):
        """Test rejection of non-dictionary building data"""
        buildings = {"farm": "not a dict", "house": []}

        errors = validate_building_definitions(buildings)

        assert any("Building 'farm': Must be a dictionary" in e for e in errors)
        assert any("Building 'house': Must be a dictionary" in e for e in errors)

    def test_missing_required_fields(self):
        """Test detection of missing required fields"""
        buildings = {"farm": {"name": "Farm"}}  # Missing cost and build_time

        errors = validate_building_definitions(buildings)

        assert any(
            "Building 'farm': Missing required field 'cost'" in e for e in errors
        )
        assert any(
            "Building 'farm': Missing required field 'build_time'" in e for e in errors
        )

    def test_invalid_cost_type(self):
        """Test detection of invalid cost types"""
        buildings = {
            "farm": {
                "name": "Farm",
                "cost": "expensive",  # Should be dict
                "build_time": 10.0,
            }
        }

        errors = validate_building_definitions(buildings)
        assert any("Building 'farm': 'cost' must be a dictionary" in e for e in errors)

    def test_invalid_cost_values(self):
        """Test detection of invalid cost resource values"""
        buildings = {
            "farm": {
                "name": "Farm",
                "cost": {"wood": -10, "stone": "many"},  # Negative and non-numeric
                "build_time": 10.0,
            }
        }

        errors = validate_building_definitions(buildings)

        assert any("Invalid cost for 'wood'" in e for e in errors)
        assert any("Invalid cost for 'stone'" in e for e in errors)

    def test_invalid_build_time(self):
        """Test detection of invalid build_time values"""
        buildings = {
            "farm": {
                "name": "Farm",
                "cost": {"wood": 50},
                "build_time": -5,  # Negative
            },
            "house": {
                "name": "House",
                "cost": {"wood": 100},
                "build_time": "instant",  # Non-numeric
            },
        }

        errors = validate_building_definitions(buildings)

        assert any(
            "Building 'farm': 'build_time' must be non-negative" in e for e in errors
        )
        assert any(
            "Building 'house': 'build_time' must be non-negative" in e for e in errors
        )


# ===========================
# Item Definitions Validation Tests
# ===========================


class TestItemDefinitionsValidation:
    """Test item definitions validation"""

    def test_valid_item_definitions(self):
        """Test validation of valid item definitions"""
        items = {
            "sword": {
                "name": "Iron Sword",
                "type": "weapon",
                "damage": 10,
                "value": 50,
            },
            "potion": {
                "name": "Health Potion",
                "type": "consumable",
                "value": 25,
                "stack_size": 99,
            },
        }

        errors = validate_item_definitions(items)
        assert errors == []

    def test_invalid_root_type(self):
        """Test rejection of non-dictionary root"""
        errors = validate_item_definitions("not a dict")
        assert errors == ["Item definitions must be a dictionary"]

    def test_missing_required_fields(self):
        """Test detection of missing required fields"""
        items = {"sword": {"name": "Sword"}}  # Missing type

        errors = validate_item_definitions(items)
        assert any("Item 'sword': Missing required field 'type'" in e for e in errors)

    def test_invalid_item_type(self):
        """Test detection of invalid item types"""
        items = {
            "sword": {
                "name": "Sword",
                "type": "invalid_type",  # Not in valid types
            }
        }

        errors = validate_item_definitions(items)
        assert any("Item 'sword': Invalid type 'invalid_type'" in e for e in errors)

    def test_valid_item_types(self):
        """Test acceptance of all valid item types"""
        valid_types = ["weapon", "armor", "consumable", "resource", "quest", "misc"]

        for item_type in valid_types:
            items = {"test_item": {"name": "Test", "type": item_type}}

            errors = validate_item_definitions(items)
            type_errors = [e for e in errors if "Invalid type" in e]
            assert len(type_errors) == 0, f"Valid type {item_type} rejected"

    def test_invalid_numeric_fields(self):
        """Test detection of invalid numeric field values"""
        items = {
            "sword": {
                "name": "Sword",
                "type": "weapon",
                "value": -10,  # Negative
                "weight": "heavy",  # Non-numeric
                "stack_size": -5,  # Negative
                "damage": "lots",  # Non-numeric
                "defense": -2,  # Negative
            }
        }

        errors = validate_item_definitions(items)

        assert any("Item 'sword': 'value' must be non-negative" in e for e in errors)
        assert any("Item 'sword': 'weight' must be non-negative" in e for e in errors)
        assert any(
            "Item 'sword': 'stack_size' must be non-negative" in e for e in errors
        )
        assert any("Item 'sword': 'damage' must be non-negative" in e for e in errors)
        assert any("Item 'sword': 'defense' must be non-negative" in e for e in errors)


# ===========================
# Character Definitions Validation Tests
# ===========================


class TestCharacterDefinitionsValidation:
    """Test character definitions validation"""

    def test_valid_character_definitions(self):
        """Test validation of valid character definitions"""
        characters = {
            "hero": {
                "name": "Hero",
                "class": "warrior",
                "stats": {"hp": 100, "attack": 15, "defense": 10},
            },
            "mage": {
                "name": "Mage",
                "class": "mage",
                "stats": {"hp": 70, "mp": 100, "magic": 20},
            },
        }

        errors = validate_character_definitions(characters)
        assert errors == []

    def test_invalid_root_type(self):
        """Test rejection of non-dictionary root"""
        errors = validate_character_definitions("not a dict")
        assert errors == ["Character definitions must be a dictionary"]

    def test_missing_required_fields(self):
        """Test detection of missing required fields"""
        characters = {"hero": {"name": "Hero"}}  # Missing class

        errors = validate_character_definitions(characters)
        assert any(
            "Character 'hero': Missing required field 'class'" in e for e in errors
        )

    def test_invalid_stats_type(self):
        """Test detection of invalid stats types"""
        characters = {
            "hero": {
                "name": "Hero",
                "class": "warrior",
                "stats": "strong",  # Should be dict
            }
        }

        errors = validate_character_definitions(characters)
        assert any(
            "Character 'hero': 'stats' must be a dictionary" in e for e in errors
        )

    def test_invalid_stat_values(self):
        """Test detection of invalid stat values"""
        characters = {
            "hero": {
                "name": "Hero",
                "class": "warrior",
                "stats": {"hp": -10, "attack": "lots", "defense": None},
            }
        }

        errors = validate_character_definitions(characters)

        assert any("Invalid stat 'hp'" in e for e in errors)
        assert any("Invalid stat 'attack'" in e for e in errors)
        assert any("Invalid stat 'defense'" in e for e in errors)


# ===========================
# Deprecation Warnings Tests
# ===========================


class TestDeprecationWarnings:
    """Test deprecation warnings"""

    def test_no_deprecated_settings(self):
        """Test no warnings for valid config"""
        config = {"settings": {"window_width": 1280, "fullscreen": False}}

        warnings = get_deprecation_warnings(config)
        assert warnings == []

    def test_deprecated_settings_detected(self):
        """Test detection of deprecated settings"""
        config = {
            "settings": {
                "use_legacy_renderer": True,
                "old_audio_system": True,
                "window_width": 1280,
            }
        }

        warnings = get_deprecation_warnings(config)

        assert len(warnings) == 2
        assert any("use_legacy_renderer" in w for w in warnings)
        assert any("old_audio_system" in w for w in warnings)

    def test_empty_config(self):
        """Test handling of empty config"""
        warnings = get_deprecation_warnings({})
        assert warnings == []


# ===========================
# Config File References Tests
# ===========================


class TestConfigFileReferences:
    """Test configuration file reference validation"""

    def test_valid_file_references(self, tmp_path):
        """Test validation with existing files"""
        # Create project structure
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        # Create definition files
        (config_dir / "buildings.json").write_text("{}")
        (config_dir / "items.json").write_text("{}")

        config = {
            "paths": {"config": "config"},
            "settings": {
                "building_definitions": "buildings",
                "item_definitions": "items",
            },
        }

        warnings = validate_config_file_references(config, tmp_path)
        assert warnings == []

    def test_missing_file_references(self, tmp_path):
        """Test detection of missing referenced files"""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        config = {
            "paths": {"config": "config"},
            "settings": {
                "building_definitions": "buildings",
                "item_definitions": "items",
                "character_definitions": "characters",
            },
        }

        warnings = validate_config_file_references(config, tmp_path)

        assert len(warnings) == 3
        assert any("building_definitions" in w for w in warnings)
        assert any("item_definitions" in w for w in warnings)
        assert any("character_definitions" in w for w in warnings)

    def test_file_with_config_prefix(self, tmp_path):
        """Test handling of file references with 'config/' prefix"""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "items.json").write_text("{}")

        config = {
            "paths": {"config": "config"},
            "settings": {
                "item_definitions": "config/items",  # With prefix
            },
        }

        warnings = validate_config_file_references(config, tmp_path)
        assert warnings == []

    def test_auto_json_extension(self, tmp_path):
        """Test automatic addition of .json extension"""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "items.json").write_text("{}")

        config = {
            "paths": {"config": "config"},
            "settings": {
                "item_definitions": "items",  # Without .json
            },
        }

        warnings = validate_config_file_references(config, tmp_path)
        assert warnings == []


# ===========================
# ValidationError Exception Tests
# ===========================


class TestValidationError:
    """Test ValidationError exception"""

    def test_validation_error_creation(self):
        """Test creating ValidationError"""
        error = ValidationError("Test error message")
        assert str(error) == "Test error message"

    def test_validation_error_raise(self):
        """Test raising ValidationError"""
        with pytest.raises(ValidationError) as exc_info:
            raise ValidationError("Test validation failed")

        assert "Test validation failed" in str(exc_info.value)

    def test_validation_error_inheritance(self):
        """Test ValidationError inherits from Exception"""
        assert issubclass(ValidationError, Exception)
