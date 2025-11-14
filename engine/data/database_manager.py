"""
Database Manager
================

Comprehensive database management system for game data with CRUD operations,
ID management, search/filter, batch operations, and CSV import/export.

Handles up to 2000 entries per category efficiently using dictionaries for O(1) lookups.

Features:
- CRUD operations (Create, Read, Update, Delete)
- Auto-increment ID management with gap handling
- Search and filter functionality
- Batch operations (duplicate, bulk edit, import/export)
- Data validation with detailed error reporting
- JSON serialization with proper error handling
- CSV import/export for easy data management
"""

import csv
import json
import shutil
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union

from engine.data.database_schema import (
    Actor,
    Animation,
    Armor,
    Class,
    DatabaseEntry,
    Enemy,
    Item,
    Skill,
    State,
    Weapon,
)


# =============================================================================
# Error Classes
# =============================================================================


class DatabaseError(Exception):
    """Base exception for database errors."""

    pass


class EntryNotFoundError(DatabaseError):
    """Raised when an entry is not found."""

    pass


class InvalidIDError(DatabaseError):
    """Raised when an ID is invalid."""

    pass


class ValidationError(DatabaseError):
    """Raised when data validation fails."""

    pass


class DuplicateIDError(DatabaseError):
    """Raised when attempting to create an entry with a duplicate ID."""

    pass


# =============================================================================
# Category Type Mapping
# =============================================================================

CATEGORY_TYPES: Dict[str, Type[DatabaseEntry]] = {
    "items": Item,
    "skills": Skill,
    "weapons": Weapon,
    "armors": Armor,
    "enemies": Enemy,
    "states": State,
    "actors": Actor,
    "classes": Class,
    "animations": Animation,
}


# =============================================================================
# Database Manager
# =============================================================================


@dataclass
class SearchResult:
    """Container for search results."""

    category: str
    entry: DatabaseEntry
    score: float = 1.0  # Relevance score (0.0-1.0)


class DatabaseManager:
    """
    Comprehensive database manager with CRUD operations, search, and batch processing.

    Efficiently handles up to 2000 entries per category using dictionary-based storage
    for O(1) lookups and optimized iteration for searches.
    """

    def __init__(self, auto_backup: bool = False, backup_dir: Optional[Path] = None):
        """
        Initialize the database manager with empty categories.

        Args:
            auto_backup: Enable automatic backups before updates/deletes
            backup_dir: Directory for backups (default: ./backups/database)
        """
        self.items: Dict[int, Item] = {}
        self.skills: Dict[int, Skill] = {}
        self.weapons: Dict[int, Weapon] = {}
        self.armors: Dict[int, Armor] = {}
        self.enemies: Dict[int, Enemy] = {}
        self.states: Dict[int, State] = {}
        self.actors: Dict[int, Actor] = {}
        self.classes: Dict[int, Class] = {}
        self.animations: Dict[int, Animation] = {}

        # Category name to storage mapping
        self._categories: Dict[str, Dict[int, DatabaseEntry]] = {
            "items": self.items,
            "skills": self.skills,
            "weapons": self.weapons,
            "armors": self.armors,
            "enemies": self.enemies,
            "states": self.states,
            "actors": self.actors,
            "classes": self.classes,
            "animations": self.animations,
        }

        # Auto-backup configuration
        self.auto_backup = auto_backup
        self.backup_dir = backup_dir or Path("./backups/database")
        if self.auto_backup:
            self.backup_dir.mkdir(parents=True, exist_ok=True)

    # =========================================================================
    # Auto-Backup System
    # =========================================================================

    def create_backup(self, name: str = "auto") -> Optional[Path]:
        """
        Create a backup of the current database state.

        Args:
            name: Backup name (default: "auto")

        Returns:
            Path to the backup file, or None if backup failed
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"{name}_backup_{timestamp}.json"

            # Ensure backup directory exists
            self.backup_dir.mkdir(parents=True, exist_ok=True)

            # Save current database state
            data = {
                "items": [item.to_dict() for item in self.items.values()],
                "skills": [skill.to_dict() for skill in self.skills.values()],
                "weapons": [weapon.to_dict() for weapon in self.weapons.values()],
                "armors": [armor.to_dict() for armor in self.armors.values()],
                "enemies": [enemy.to_dict() for enemy in self.enemies.values()],
                "states": [state.to_dict() for state in self.states.values()],
                "actors": [actor.to_dict() for actor in self.actors.values()],
                "classes": [cls.to_dict() for cls in self.classes.values()],
                "animations": [anim.to_dict() for anim in self.animations.values()],
            }

            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return backup_file
        except Exception as e:
            print(f"Warning: Backup failed: {e}")
            return None

    def enable_auto_backup(self, backup_dir: Optional[Path] = None):
        """
        Enable automatic backups before updates and deletes.

        Args:
            backup_dir: Directory for backups (default: ./backups/database)
        """
        self.auto_backup = True
        if backup_dir:
            self.backup_dir = backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def disable_auto_backup(self):
        """Disable automatic backups."""
        self.auto_backup = False

    def _auto_backup_if_enabled(self, operation: str = "edit"):
        """
        Create automatic backup if enabled.

        Args:
            operation: Name of operation for backup file
        """
        if self.auto_backup:
            self.create_backup(f"auto_{operation}")

    # =========================================================================
    # CRUD Operations
    # =========================================================================

    def create(
        self, category: str, entry: DatabaseEntry, auto_id: bool = False
    ) -> DatabaseEntry:
        """
        Create a new entry in the specified category.

        Args:
            category: Category name (e.g., "items", "skills")
            entry: DatabaseEntry object to add
            auto_id: If True, automatically assign an ID

        Returns:
            The created entry with assigned ID

        Raises:
            DatabaseError: If category is invalid
            DuplicateIDError: If ID already exists and auto_id is False
            ValidationError: If entry fails validation
        """
        if category not in self._categories:
            raise DatabaseError(f"Invalid category: {category}")

        storage = self._categories[category]

        # Auto-assign ID if requested
        if auto_id or entry.id == 0:
            entry.id = self._get_next_id(category)

        # Check for duplicate ID
        if entry.id in storage:
            raise DuplicateIDError(
                f"{category} entry with ID {entry.id} already exists"
            )

        # Validate entry
        if not entry.validate():
            raise ValidationError(
                f"{category} entry with ID {entry.id} failed validation"
            )

        # Add to storage
        storage[entry.id] = entry
        return entry

    def read(self, category: str, entry_id: int) -> DatabaseEntry:
        """
        Read an entry from the specified category.

        Args:
            category: Category name
            entry_id: ID of the entry to retrieve

        Returns:
            The requested entry

        Raises:
            DatabaseError: If category is invalid
            EntryNotFoundError: If entry doesn't exist
        """
        if category not in self._categories:
            raise DatabaseError(f"Invalid category: {category}")

        storage = self._categories[category]

        if entry_id not in storage:
            raise EntryNotFoundError(
                f"{category} entry with ID {entry_id} not found"
            )

        return storage[entry_id]

    def read_all(self, category: str) -> List[DatabaseEntry]:
        """
        Read all entries from a category.

        Args:
            category: Category name

        Returns:
            List of all entries in the category (sorted by ID)

        Raises:
            DatabaseError: If category is invalid
        """
        if category not in self._categories:
            raise DatabaseError(f"Invalid category: {category}")

        storage = self._categories[category]
        return sorted(storage.values(), key=lambda x: x.id)

    def update(self, category: str, entry: DatabaseEntry) -> DatabaseEntry:
        """
        Update an existing entry.

        Args:
            category: Category name
            entry: Updated entry (must have existing ID)

        Returns:
            The updated entry

        Raises:
            DatabaseError: If category is invalid
            EntryNotFoundError: If entry doesn't exist
            ValidationError: If updated entry fails validation
        """
        if category not in self._categories:
            raise DatabaseError(f"Invalid category: {category}")

        storage = self._categories[category]

        if entry.id not in storage:
            raise EntryNotFoundError(
                f"{category} entry with ID {entry.id} not found"
            )

        # Validate updated entry
        if not entry.validate():
            raise ValidationError(
                f"{category} entry with ID {entry.id} failed validation"
            )

        # Auto-backup before update
        self._auto_backup_if_enabled(f"update_{category}_{entry.id}")

        storage[entry.id] = entry
        return entry

    def delete(self, category: str, entry_id: int) -> DatabaseEntry:
        """
        Delete an entry from the specified category.

        Args:
            category: Category name
            entry_id: ID of the entry to delete

        Returns:
            The deleted entry

        Raises:
            DatabaseError: If category is invalid
            EntryNotFoundError: If entry doesn't exist
        """
        if category not in self._categories:
            raise DatabaseError(f"Invalid category: {category}")

        storage = self._categories[category]

        if entry_id not in storage:
            raise EntryNotFoundError(
                f"{category} entry with ID {entry_id} not found"
            )

        # Auto-backup before delete
        self._auto_backup_if_enabled(f"delete_{category}_{entry_id}")

        return storage.pop(entry_id)

    def exists(self, category: str, entry_id: int) -> bool:
        """
        Check if an entry exists.

        Args:
            category: Category name
            entry_id: ID to check

        Returns:
            True if entry exists, False otherwise
        """
        if category not in self._categories:
            return False
        return entry_id in self._categories[category]

    # =========================================================================
    # ID Management
    # =========================================================================

    def _get_next_id(self, category: str) -> int:
        """
        Get the next available ID in a category.

        Handles gaps efficiently by first checking for gaps, then returning
        the next sequential ID.

        Args:
            category: Category name

        Returns:
            Next available ID (1-9999)

        Raises:
            DatabaseError: If all IDs are exhausted
        """
        storage = self._categories[category]

        if not storage:
            return 1

        # Get all existing IDs
        existing_ids = set(storage.keys())

        # Find first gap (efficient for sparse data)
        for id_candidate in range(1, 10000):
            if id_candidate not in existing_ids:
                return id_candidate

        raise DatabaseError(f"No available IDs in category {category}")

    def get_next_id(self, category: str) -> int:
        """
        Public method to get the next available ID.

        Args:
            category: Category name

        Returns:
            Next available ID

        Raises:
            DatabaseError: If category is invalid or IDs exhausted
        """
        if category not in self._categories:
            raise DatabaseError(f"Invalid category: {category}")

        return self._get_next_id(category)

    def find_gaps(self, category: str, max_id: Optional[int] = None) -> List[int]:
        """
        Find gaps in ID sequence.

        Args:
            category: Category name
            max_id: Maximum ID to check (defaults to highest existing ID)

        Returns:
            List of unused IDs in the range

        Raises:
            DatabaseError: If category is invalid
        """
        if category not in self._categories:
            raise DatabaseError(f"Invalid category: {category}")

        storage = self._categories[category]

        if not storage:
            return []

        existing_ids = set(storage.keys())
        max_check = max_id or max(existing_ids)

        gaps = [i for i in range(1, max_check + 1) if i not in existing_ids]
        return gaps

    def compact_ids(self, category: str) -> Dict[int, int]:
        """
        Compact IDs to remove gaps (renumber entries sequentially).

        Args:
            category: Category name

        Returns:
            Mapping of old IDs to new IDs

        Raises:
            DatabaseError: If category is invalid
        """
        if category not in self._categories:
            raise DatabaseError(f"Invalid category: {category}")

        storage = self._categories[category]

        # Get sorted entries
        entries = sorted(storage.values(), key=lambda x: x.id)

        # Create ID mapping
        id_mapping = {}
        new_storage = {}

        for new_id, entry in enumerate(entries, start=1):
            old_id = entry.id
            id_mapping[old_id] = new_id
            entry.id = new_id
            new_storage[new_id] = entry

        # Replace storage
        storage.clear()
        storage.update(new_storage)

        return id_mapping

    # =========================================================================
    # Search and Filter
    # =========================================================================

    def search(
        self,
        query: str,
        categories: Optional[List[str]] = None,
        fields: Optional[List[str]] = None,
        case_sensitive: bool = False,
    ) -> List[SearchResult]:
        """
        Search for entries matching a query string.

        Args:
            query: Search query
            categories: Categories to search (None = all)
            fields: Fields to search in (None = name, description)
            case_sensitive: Whether to perform case-sensitive search

        Returns:
            List of SearchResult objects sorted by relevance
        """
        if categories is None:
            categories = list(self._categories.keys())

        if fields is None:
            fields = ["name", "description"]

        results = []
        search_query = query if case_sensitive else query.lower()

        for category in categories:
            if category not in self._categories:
                continue

            storage = self._categories[category]

            for entry in storage.values():
                score = 0.0
                matches = 0

                for field in fields:
                    if not hasattr(entry, field):
                        continue

                    value = getattr(entry, field)
                    if not isinstance(value, str):
                        continue

                    search_value = value if case_sensitive else value.lower()

                    # Exact match
                    if search_query == search_value:
                        score += 1.0
                        matches += 1
                    # Starts with query
                    elif search_value.startswith(search_query):
                        score += 0.8
                        matches += 1
                    # Contains query
                    elif search_query in search_value:
                        score += 0.5
                        matches += 1

                if matches > 0:
                    # Average score across matched fields
                    avg_score = score / len(fields)
                    results.append(SearchResult(category, entry, avg_score))

        # Sort by score (descending)
        results.sort(key=lambda x: x.score, reverse=True)
        return results

    def filter(
        self,
        category: str,
        predicate: Callable[[DatabaseEntry], bool],
    ) -> List[DatabaseEntry]:
        """
        Filter entries in a category using a predicate function.

        Args:
            category: Category name
            predicate: Function that returns True for entries to include

        Returns:
            List of filtered entries (sorted by ID)

        Raises:
            DatabaseError: If category is invalid

        Example:
            # Find all items with price > 100
            expensive = manager.filter("items", lambda item: item.price > 100)
        """
        if category not in self._categories:
            raise DatabaseError(f"Invalid category: {category}")

        storage = self._categories[category]
        filtered = [entry for entry in storage.values() if predicate(entry)]

        return sorted(filtered, key=lambda x: x.id)

    def filter_by_field(
        self,
        category: str,
        field: str,
        value: Any,
        operator: str = "eq",
    ) -> List[DatabaseEntry]:
        """
        Filter entries by field value.

        Args:
            category: Category name
            field: Field name to filter on
            value: Value to compare against
            operator: Comparison operator (eq, ne, gt, lt, ge, le, contains)

        Returns:
            List of filtered entries (sorted by ID)

        Raises:
            DatabaseError: If category is invalid or operator is unknown
        """
        if category not in self._categories:
            raise DatabaseError(f"Invalid category: {category}")

        operators = {
            "eq": lambda a, b: a == b,
            "ne": lambda a, b: a != b,
            "gt": lambda a, b: a > b,
            "lt": lambda a, b: a < b,
            "ge": lambda a, b: a >= b,
            "le": lambda a, b: a <= b,
            "contains": lambda a, b: b in a if isinstance(a, (str, list)) else False,
        }

        if operator not in operators:
            raise DatabaseError(f"Unknown operator: {operator}")

        op_func = operators[operator]

        def predicate(entry: DatabaseEntry) -> bool:
            if not hasattr(entry, field):
                return False
            field_value = getattr(entry, field)
            try:
                return op_func(field_value, value)
            except (TypeError, AttributeError):
                return False

        return self.filter(category, predicate)

    # =========================================================================
    # Batch Operations
    # =========================================================================

    def duplicate(
        self,
        category: str,
        entry_id: int,
        new_name: Optional[str] = None,
        auto_id: bool = True,
    ) -> DatabaseEntry:
        """
        Duplicate an existing entry.

        Args:
            category: Category name
            entry_id: ID of entry to duplicate
            new_name: Optional new name for duplicate
            auto_id: If True, automatically assign new ID

        Returns:
            The duplicated entry

        Raises:
            DatabaseError: If category is invalid
            EntryNotFoundError: If source entry doesn't exist
        """
        # Read original entry
        original = self.read(category, entry_id)

        # Create deep copy via serialization
        entry_dict = original.to_dict()
        entry_type = CATEGORY_TYPES[category]
        duplicate_entry = entry_type.from_dict(entry_dict)

        # Assign new name if provided
        if new_name:
            duplicate_entry.name = new_name
        else:
            duplicate_entry.name = f"{original.name} (Copy)"

        # Create with auto ID
        return self.create(category, duplicate_entry, auto_id=auto_id)

    def bulk_edit(
        self,
        category: str,
        entry_ids: List[int],
        updates: Dict[str, Any],
    ) -> List[DatabaseEntry]:
        """
        Apply updates to multiple entries.

        Args:
            category: Category name
            entry_ids: List of entry IDs to update
            updates: Dictionary of field names to new values

        Returns:
            List of updated entries

        Raises:
            DatabaseError: If category is invalid
            EntryNotFoundError: If any entry doesn't exist
            ValidationError: If any update fails validation

        Example:
            # Set price to 100 for items 1, 2, 3
            manager.bulk_edit("items", [1, 2, 3], {"price": 100})
        """
        if category not in self._categories:
            raise DatabaseError(f"Invalid category: {category}")

        updated_entries = []

        for entry_id in entry_ids:
            entry = self.read(category, entry_id)

            # Apply updates
            for field, value in updates.items():
                if hasattr(entry, field):
                    setattr(entry, field, value)

            # Update (will validate)
            updated_entry = self.update(category, entry)
            updated_entries.append(updated_entry)

        return updated_entries

    def bulk_delete(self, category: str, entry_ids: List[int]) -> List[DatabaseEntry]:
        """
        Delete multiple entries.

        Args:
            category: Category name
            entry_ids: List of entry IDs to delete

        Returns:
            List of deleted entries

        Raises:
            DatabaseError: If category is invalid
            EntryNotFoundError: If any entry doesn't exist
        """
        if category not in self._categories:
            raise DatabaseError(f"Invalid category: {category}")

        deleted_entries = []

        for entry_id in entry_ids:
            deleted_entry = self.delete(category, entry_id)
            deleted_entries.append(deleted_entry)

        return deleted_entries

    # =========================================================================
    # JSON Serialization
    # =========================================================================

    def save_to_file(self, filepath: Union[Path, str], pretty: bool = True) -> None:
        """
        Save all database entries to a JSON file with error handling.

        Args:
            filepath: Path to save file (Path object or string)
            pretty: If True, format with indentation (default: True)

        Raises:
            DatabaseError: If save fails
        """
        try:
            # Convert to Path if string
            if isinstance(filepath, str):
                filepath = Path(filepath)

            data = {
                "items": [item.to_dict() for item in self.items.values()],
                "skills": [skill.to_dict() for skill in self.skills.values()],
                "weapons": [weapon.to_dict() for weapon in self.weapons.values()],
                "armors": [armor.to_dict() for armor in self.armors.values()],
                "enemies": [enemy.to_dict() for enemy in self.enemies.values()],
                "states": [state.to_dict() for state in self.states.values()],
                "actors": [actor.to_dict() for actor in self.actors.values()],
                "classes": [cls.to_dict() for cls in self.classes.values()],
                "animations": [anim.to_dict() for anim in self.animations.values()],
            }

            # Ensure directory exists
            filepath.parent.mkdir(parents=True, exist_ok=True)

            # Write with appropriate formatting
            with open(filepath, "w", encoding="utf-8") as f:
                if pretty:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(data, f, ensure_ascii=False)

        except (OSError, IOError) as e:
            raise DatabaseError(f"Failed to save to {filepath}: {e}")
        except Exception as e:
            raise DatabaseError(f"Unexpected error saving to {filepath}: {e}")

    def load_from_file(self, filepath: Path) -> None:
        """
        Load all database entries from a JSON file with error handling.

        Args:
            filepath: Path to load from

        Raises:
            DatabaseError: If load fails
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Clear existing data
            self.clear()

            # Load each category
            self.items = {
                item["id"]: Item.from_dict(item) for item in data.get("items", [])
            }
            self.skills = {
                skill["id"]: Skill.from_dict(skill)
                for skill in data.get("skills", [])
            }
            self.weapons = {
                weapon["id"]: Weapon.from_dict(weapon)
                for weapon in data.get("weapons", [])
            }
            self.armors = {
                armor["id"]: Armor.from_dict(armor)
                for armor in data.get("armors", [])
            }
            self.enemies = {
                enemy["id"]: Enemy.from_dict(enemy)
                for enemy in data.get("enemies", [])
            }
            self.states = {
                state["id"]: State.from_dict(state)
                for state in data.get("states", [])
            }
            self.actors = {
                actor["id"]: Actor.from_dict(actor)
                for actor in data.get("actors", [])
            }
            self.classes = {
                cls["id"]: Class.from_dict(cls) for cls in data.get("classes", [])
            }
            self.animations = {
                anim["id"]: Animation.from_dict(anim)
                for anim in data.get("animations", [])
            }

            # Update category mappings
            self._categories.update(
                {
                    "items": self.items,
                    "skills": self.skills,
                    "weapons": self.weapons,
                    "armors": self.armors,
                    "enemies": self.enemies,
                    "states": self.states,
                    "actors": self.actors,
                    "classes": self.classes,
                    "animations": self.animations,
                }
            )

        except FileNotFoundError:
            raise DatabaseError(f"File not found: {filepath}")
        except json.JSONDecodeError as e:
            raise DatabaseError(f"Invalid JSON in {filepath}: {e}")
        except KeyError as e:
            raise DatabaseError(f"Missing required field in {filepath}: {e}")
        except Exception as e:
            raise DatabaseError(f"Unexpected error loading from {filepath}: {e}")

    def save_category_to_file(
        self, category: str, filepath: Path, pretty: bool = True
    ) -> None:
        """
        Save a single category to a JSON file.

        Args:
            category: Category name
            filepath: Path to save file
            pretty: If True, format with indentation

        Raises:
            DatabaseError: If category is invalid or save fails
        """
        if category not in self._categories:
            raise DatabaseError(f"Invalid category: {category}")

        try:
            storage = self._categories[category]
            data = [entry.to_dict() for entry in storage.values()]

            filepath.parent.mkdir(parents=True, exist_ok=True)

            with open(filepath, "w", encoding="utf-8") as f:
                if pretty:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(data, f, ensure_ascii=False)

        except (OSError, IOError) as e:
            raise DatabaseError(f"Failed to save {category} to {filepath}: {e}")
        except Exception as e:
            raise DatabaseError(
                f"Unexpected error saving {category} to {filepath}: {e}"
            )

    # =========================================================================
    # CSV Import/Export
    # =========================================================================

    def export_to_csv(
        self,
        category: str,
        filepath: Path,
        fields: Optional[List[str]] = None,
    ) -> None:
        """
        Export category entries to CSV file.

        Args:
            category: Category name
            filepath: Path to CSV file
            fields: List of fields to export (None = all common fields)

        Raises:
            DatabaseError: If category is invalid or export fails
        """
        if category not in self._categories:
            raise DatabaseError(f"Invalid category: {category}")

        storage = self._categories[category]

        if not storage:
            raise DatabaseError(f"No entries to export in category {category}")

        # Get fields to export
        if fields is None:
            # Default fields common to all entries
            fields = ["id", "name", "icon_index", "description", "note"]

        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)

            with open(filepath, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()

                for entry in sorted(storage.values(), key=lambda x: x.id):
                    row = {}
                    for field in fields:
                        if hasattr(entry, field):
                            value = getattr(entry, field)
                            # Convert complex types to strings
                            if isinstance(value, (list, dict)):
                                row[field] = json.dumps(value)
                            elif hasattr(value, "value"):  # Enum
                                row[field] = value.value
                            else:
                                row[field] = value
                        else:
                            row[field] = ""

                    writer.writerow(row)

        except (OSError, IOError) as e:
            raise DatabaseError(f"Failed to export {category} to {filepath}: {e}")
        except Exception as e:
            raise DatabaseError(
                f"Unexpected error exporting {category} to {filepath}: {e}"
            )

    def import_from_csv(
        self,
        category: str,
        filepath: Path,
        update_existing: bool = False,
        auto_id: bool = False,
    ) -> Tuple[int, int, List[str]]:
        """
        Import entries from CSV file.

        Args:
            category: Category name
            filepath: Path to CSV file
            update_existing: If True, update existing entries instead of error
            auto_id: If True, auto-assign IDs for new entries

        Returns:
            Tuple of (created_count, updated_count, errors)

        Raises:
            DatabaseError: If category is invalid or import fails
        """
        if category not in self._categories:
            raise DatabaseError(f"Invalid category: {category}")

        entry_type = CATEGORY_TYPES[category]

        created = 0
        updated = 0
        errors = []

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header=1)
                    try:
                        # Convert CSV row to entry dict
                        entry_dict = {}
                        for key, value in row.items():
                            if value == "":  # Skip empty string values only
                                continue

                            # Try to parse JSON for complex types
                            if value.startswith("[") or value.startswith("{"):
                                try:
                                    entry_dict[key] = json.loads(value)
                                except json.JSONDecodeError:
                                    entry_dict[key] = value
                            # Boolean (check before int to avoid "true"/"false" as string)
                            elif value.lower() in ("true", "false"):
                                entry_dict[key] = value.lower() == "true"
                            # Try to parse as float (check before int to catch decimals)
                            elif "." in value and value.replace(".", "").replace("-", "").isdigit():
                                try:
                                    entry_dict[key] = float(value)
                                except ValueError:
                                    entry_dict[key] = value
                            # Try to parse as int
                            elif value.lstrip("-").isdigit():
                                entry_dict[key] = int(value)
                            else:
                                entry_dict[key] = value

                        # Create entry from dict
                        entry = entry_type.from_dict(entry_dict)

                        # Check if entry exists
                        entry_id = entry.id
                        if self.exists(category, entry_id):
                            if update_existing:
                                self.update(category, entry)
                                updated += 1
                            else:
                                errors.append(
                                    f"Row {row_num}: Entry with ID {entry_id} already exists"
                                )
                        else:
                            self.create(category, entry, auto_id=auto_id)
                            created += 1

                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")

        except FileNotFoundError:
            raise DatabaseError(f"File not found: {filepath}")
        except Exception as e:
            raise DatabaseError(f"Failed to import from {filepath}: {e}")

        return created, updated, errors

    # =========================================================================
    # Validation
    # =========================================================================

    def validate_all(self) -> Dict[str, List[str]]:
        """
        Validate all database entries.

        Returns:
            Dictionary mapping entry type to list of validation errors
        """
        errors: Dict[str, List[str]] = {}

        for category, storage in self._categories.items():
            for entry in storage.values():
                if not entry.validate():
                    errors.setdefault(category, []).append(
                        f"{category.capitalize()} {entry.id} ({entry.name}) failed validation"
                    )

        return errors

    def validate_category(self, category: str) -> List[str]:
        """
        Validate all entries in a category.

        Args:
            category: Category name

        Returns:
            List of validation error messages

        Raises:
            DatabaseError: If category is invalid
        """
        if category not in self._categories:
            raise DatabaseError(f"Invalid category: {category}")

        errors = []
        storage = self._categories[category]

        for entry in storage.values():
            if not entry.validate():
                errors.append(
                    f"{category.capitalize()} {entry.id} ({entry.name}) failed validation"
                )

        return errors

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def clear(self) -> None:
        """Clear all database entries."""
        for storage in self._categories.values():
            storage.clear()

    def clear_category(self, category: str) -> None:
        """
        Clear all entries in a category.

        Args:
            category: Category name

        Raises:
            DatabaseError: If category is invalid
        """
        if category not in self._categories:
            raise DatabaseError(f"Invalid category: {category}")

        self._categories[category].clear()

    def get_all_ids(self, category: str) -> List[int]:
        """
        Get all entry IDs in a category.

        Args:
            category: Category name

        Returns:
            List of all entry IDs

        Raises:
            DatabaseError: If category is invalid
        """
        if category not in self._categories:
            raise DatabaseError(f"Invalid category: {category}")

        return list(self._categories[category].keys())

    def get_all_entries(self, category: str) -> List[DatabaseEntry]:
        """
        Get all entries in a category.

        Args:
            category: Category name

        Returns:
            List of all entries

        Raises:
            DatabaseError: If category is invalid
        """
        if category not in self._categories:
            raise DatabaseError(f"Invalid category: {category}")

        return list(self._categories[category].values())

    def create_entry(self, category: str, entry: DatabaseEntry, auto_id: bool = False) -> DatabaseEntry:
        """
        Alias for create() method for backward compatibility.

        Args:
            category: Category name
            entry: Entry to create
            auto_id: Auto-assign ID if True

        Returns:
            Created entry

        Raises:
            DatabaseError: If creation fails
        """
        return self.create(category, entry, auto_id)

    def to_dict(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Convert entire database to dictionary format.

        Returns:
            Dictionary with all categories and their entries
        """
        return {
            "items": [item.to_dict() for item in self.items.values()],
            "skills": [skill.to_dict() for skill in self.skills.values()],
            "weapons": [weapon.to_dict() for weapon in self.weapons.values()],
            "armors": [armor.to_dict() for armor in self.armors.values()],
            "enemies": [enemy.to_dict() for enemy in self.enemies.values()],
            "states": [state.to_dict() for state in self.states.values()],
            "actors": [actor.to_dict() for actor in self.actors.values()],
            "classes": [cls.to_dict() for cls in self.classes.values()],
            "animations": [anim.to_dict() for anim in self.animations.values()],
        }

    def get_count(self, category: str) -> int:
        """
        Get the number of entries in a category.

        Args:
            category: Category name

        Returns:
            Number of entries

        Raises:
            DatabaseError: If category is invalid
        """
        if category not in self._categories:
            raise DatabaseError(f"Invalid category: {category}")

        return len(self._categories[category])

    def get_counts(self) -> Dict[str, int]:
        """
        Get counts for all categories.

        Returns:
            Dictionary mapping category names to entry counts
        """
        return {
            category: len(storage) for category, storage in self._categories.items()
        }

    def get_categories(self) -> List[str]:
        """
        Get list of all category names.

        Returns:
            List of category names
        """
        return list(self._categories.keys())
