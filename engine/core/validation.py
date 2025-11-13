"""
Configuration Validation

Validates project configuration files and provides helpful error messages.
"""

from typing import Dict, Any, List, Optional


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


def validate_project_config(config: Dict[str, Any]) -> List[str]:
    """
    Validate project configuration structure and values.

    Args:
        config: Project configuration dictionary

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Validate top-level structure
    required_sections = ['metadata', 'paths', 'settings']
    for section in required_sections:
        if section not in config:
            errors.append(f"Missing required section: '{section}'")

    # If structure is completely broken, return early
    if errors:
        return errors

    # Validate metadata
    metadata_errors = _validate_metadata(config.get('metadata', {}))
    errors.extend(metadata_errors)

    # Validate paths
    paths_errors = _validate_paths(config.get('paths', {}))
    errors.extend(paths_errors)

    # Validate settings
    settings_errors = _validate_settings(config.get('settings', {}))
    errors.extend(settings_errors)

    return errors


def _validate_metadata(metadata: Dict[str, Any]) -> List[str]:
    """Validate metadata section"""
    errors = []

    required_fields = {
        'name': str,
        'version': str,
        'description': str,
        'author': str,
    }

    for field, expected_type in required_fields.items():
        if field not in metadata:
            errors.append(f"metadata.{field}: Missing required field")
        elif not isinstance(metadata[field], expected_type):
            errors.append(
                f"metadata.{field}: Expected {expected_type.__name__}, "
                f"got {type(metadata[field]).__name__}"
            )
        elif isinstance(metadata[field], str) and not metadata[field].strip():
            errors.append(f"metadata.{field}: Cannot be empty")

    # Validate version format
    if 'version' in metadata and isinstance(metadata['version'], str):
        if not _is_valid_version(metadata['version']):
            errors.append(
                f"metadata.version: Invalid version format '{metadata['version']}'. "
                f"Expected format: X.Y.Z (e.g., '1.0.0')"
            )

    # Validate optional fields
    if 'engine_version' in metadata:
        if not isinstance(metadata['engine_version'], str):
            errors.append("metadata.engine_version: Must be a string")

    return errors


def _validate_paths(paths: Dict[str, Any]) -> List[str]:
    """Validate paths section"""
    errors = []

    expected_paths = ['assets', 'levels', 'scripts', 'saves', 'config']

    for path_name in expected_paths:
        if path_name in paths:
            if not isinstance(paths[path_name], str):
                errors.append(
                    f"paths.{path_name}: Expected string, "
                    f"got {type(paths[path_name]).__name__}"
                )
            elif not paths[path_name].strip():
                errors.append(f"paths.{path_name}: Cannot be empty")
            elif paths[path_name].startswith('/') or paths[path_name].startswith('\\'):
                errors.append(
                    f"paths.{path_name}: Must be relative path, not absolute"
                )

    return errors


def _validate_settings(settings: Dict[str, Any]) -> List[str]:
    """Validate settings section"""
    errors = []

    # Display settings
    display_settings = {
        'window_width': (int, 320, 7680),  # Min 320, Max 8K
        'window_height': (int, 240, 4320),  # Min 240, Max 8K
        'window_title': (str, None, None),
        'fullscreen': (bool, None, None),
    }

    for setting, (expected_type, min_val, max_val) in display_settings.items():
        if setting in settings:
            value = settings[setting]

            if not isinstance(value, expected_type):
                errors.append(
                    f"settings.{setting}: Expected {expected_type.__name__}, "
                    f"got {type(value).__name__}"
                )
                continue

            if expected_type == int and min_val is not None:
                if value < min_val:
                    errors.append(
                        f"settings.{setting}: Value {value} is too small "
                        f"(minimum: {min_val})"
                    )
                if value > max_val:
                    errors.append(
                        f"settings.{setting}: Value {value} is too large "
                        f"(maximum: {max_val})"
                    )

            if expected_type == str and not value.strip():
                errors.append(f"settings.{setting}: Cannot be empty")

    # Gameplay settings
    gameplay_settings = {
        'tile_size': (int, 8, 256),
        'grid_width': (int, 1, 1000),
        'grid_height': (int, 1, 1000),
    }

    for setting, (expected_type, min_val, max_val) in gameplay_settings.items():
        if setting in settings:
            value = settings[setting]

            if not isinstance(value, expected_type):
                errors.append(
                    f"settings.{setting}: Expected {expected_type.__name__}, "
                    f"got {type(value).__name__}"
                )
                continue

            if value < min_val or value > max_val:
                errors.append(
                    f"settings.{setting}: Value {value} out of range "
                    f"({min_val}-{max_val})"
                )

    # Feature flags
    feature_flags = [
        'enable_base_building',
        'enable_survival',
        'enable_turn_based',
        'enable_combat',
    ]

    for flag in feature_flags:
        if flag in settings:
            if not isinstance(settings[flag], bool):
                errors.append(
                    f"settings.{flag}: Expected bool, "
                    f"got {type(settings[flag]).__name__}"
                )

    # Scene settings
    if 'initial_scene' in settings:
        if not isinstance(settings['initial_scene'], str):
            errors.append("settings.initial_scene: Must be a string")

    # Data file paths
    data_files = [
        'building_definitions',
        'item_definitions',
        'character_definitions',
        'quest_definitions',
    ]

    for file_setting in data_files:
        if file_setting in settings:
            value = settings[file_setting]
            if not isinstance(value, str):
                errors.append(
                    f"settings.{file_setting}: Expected string, "
                    f"got {type(value).__name__}"
                )

    # Export settings
    export_settings = {
        'export_version': str,
        'export_publisher': str,
        'export_description': str,
        'export_encrypt': bool,
        'export_compress': bool,
        'export_console': bool,
    }

    for setting, expected_type in export_settings.items():
        if setting in settings:
            if not isinstance(settings[setting], expected_type):
                errors.append(
                    f"settings.{setting}: Expected {expected_type.__name__}, "
                    f"got {type(settings[setting]).__name__}"
                )

    return errors


def _is_valid_version(version: str) -> bool:
    """Check if version string is valid (X.Y.Z format)"""
    parts = version.split('.')

    if len(parts) < 2 or len(parts) > 3:
        return False

    for part in parts:
        if not part.isdigit():
            return False

    return True


def validate_building_definitions(buildings: Dict[str, Any]) -> List[str]:
    """
    Validate building definitions configuration.

    Args:
        buildings: Building definitions dictionary

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    if not isinstance(buildings, dict):
        return ["Building definitions must be a dictionary"]

    for building_id, building_data in buildings.items():
        if not isinstance(building_data, dict):
            errors.append(f"Building '{building_id}': Must be a dictionary")
            continue

        # Required fields
        required = ['name', 'cost', 'build_time']
        for field in required:
            if field not in building_data:
                errors.append(f"Building '{building_id}': Missing required field '{field}'")

        # Validate cost
        if 'cost' in building_data:
            cost = building_data['cost']
            if not isinstance(cost, dict):
                errors.append(f"Building '{building_id}': 'cost' must be a dictionary")
            else:
                for resource, amount in cost.items():
                    if not isinstance(amount, (int, float)) or amount < 0:
                        errors.append(
                            f"Building '{building_id}': Invalid cost for '{resource}' "
                            f"(must be non-negative number)"
                        )

        # Validate build_time
        if 'build_time' in building_data:
            build_time = building_data['build_time']
            if not isinstance(build_time, (int, float)) or build_time < 0:
                errors.append(
                    f"Building '{building_id}': 'build_time' must be non-negative number"
                )

    return errors


def validate_item_definitions(items: Dict[str, Any]) -> List[str]:
    """
    Validate item definitions configuration.

    Args:
        items: Item definitions dictionary

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    if not isinstance(items, dict):
        return ["Item definitions must be a dictionary"]

    for item_id, item_data in items.items():
        if not isinstance(item_data, dict):
            errors.append(f"Item '{item_id}': Must be a dictionary")
            continue

        # Required fields
        required = ['name', 'type']
        for field in required:
            if field not in item_data:
                errors.append(f"Item '{item_id}': Missing required field '{field}'")

        # Validate type
        if 'type' in item_data:
            valid_types = ['weapon', 'armor', 'consumable', 'resource', 'quest', 'misc']
            if item_data['type'] not in valid_types:
                errors.append(
                    f"Item '{item_id}': Invalid type '{item_data['type']}'. "
                    f"Must be one of: {', '.join(valid_types)}"
                )

        # Validate numeric fields
        numeric_fields = ['value', 'weight', 'stack_size', 'damage', 'defense']
        for field in numeric_fields:
            if field in item_data:
                value = item_data[field]
                if not isinstance(value, (int, float)) or value < 0:
                    errors.append(
                        f"Item '{item_id}': '{field}' must be non-negative number"
                    )

    return errors


def validate_character_definitions(characters: Dict[str, Any]) -> List[str]:
    """
    Validate character definitions configuration.

    Args:
        characters: Character definitions dictionary

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    if not isinstance(characters, dict):
        return ["Character definitions must be a dictionary"]

    for char_id, char_data in characters.items():
        if not isinstance(char_data, dict):
            errors.append(f"Character '{char_id}': Must be a dictionary")
            continue

        # Required fields
        required = ['name', 'class']
        for field in required:
            if field not in char_data:
                errors.append(f"Character '{char_id}': Missing required field '{field}'")

        # Validate stats
        if 'stats' in char_data:
            stats = char_data['stats']
            if not isinstance(stats, dict):
                errors.append(f"Character '{char_id}': 'stats' must be a dictionary")
            else:
                for stat, value in stats.items():
                    if not isinstance(value, (int, float)) or value < 0:
                        errors.append(
                            f"Character '{char_id}': Invalid stat '{stat}' "
                            f"(must be non-negative number)"
                        )

    return errors


def get_deprecation_warnings(config: Dict[str, Any]) -> List[str]:
    """
    Check for deprecated settings and return warnings.

    Args:
        config: Project configuration dictionary

    Returns:
        List of warning messages
    """
    warnings = []

    # Example: Check for deprecated settings
    # This can be expanded as the engine evolves

    settings = config.get('settings', {})

    # Deprecated field examples (add real ones as needed)
    deprecated_fields = {
        'use_legacy_renderer': 'The legacy renderer is deprecated. Use the new renderer instead.',
        'old_audio_system': 'The old audio system is deprecated. Update to the new audio manager.',
    }

    for field, message in deprecated_fields.items():
        if field in settings:
            warnings.append(f"⚠️  Deprecated setting '{field}': {message}")

    return warnings


def validate_config_file_references(config: Dict[str, Any], project_root) -> List[str]:
    """
    Validate that referenced configuration files exist.

    Args:
        config: Project configuration dictionary
        project_root: Path to project root directory

    Returns:
        List of warning messages for missing files
    """
    from pathlib import Path

    warnings = []
    settings = config.get('settings', {})
    config_path = Path(project_root) / config.get('paths', {}).get('config', 'config')

    file_references = {
        'building_definitions': 'Building definitions file',
        'item_definitions': 'Item definitions file',
        'character_definitions': 'Character definitions file',
        'quest_definitions': 'Quest definitions file',
    }

    for setting, description in file_references.items():
        if setting in settings and settings[setting]:
            file_path = settings[setting]

            # Remove 'config/' prefix if present
            if file_path.startswith('config/'):
                file_path = file_path[7:]

            # Add .json extension if missing
            if not file_path.endswith('.json'):
                file_path += '.json'

            full_path = config_path / file_path

            if not full_path.exists():
                warnings.append(
                    f"⚠️  {description} not found: {full_path}\n"
                    f"   Referenced in settings.{setting}"
                )

    return warnings
