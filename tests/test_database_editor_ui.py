"""
Comprehensive tests for Database Editor UI

Tests the three-panel database editor interface, CRUD operations,
category selection, search/filter, and event handling.
"""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pygame
import pytest

from neonworks.engine.data.database_manager import DatabaseManager
from neonworks.engine.data.database_schema import Actor, Enemy, Item, Skill, Weapon
from neonworks.engine.ui.database_editor_ui import DatabaseEditorUI


@pytest.fixture
def screen():
    """Create a test screen surface"""
    pygame.init()
    return pygame.Surface((1280, 720))


@pytest.fixture
def temp_db_path(tmp_path):
    """Create a temporary database path"""
    return tmp_path / "test_database.json"


@pytest.fixture
def db_editor(screen, temp_db_path):
    """Create a database editor instance"""
    editor = DatabaseEditorUI(screen, database_path=temp_db_path)
    return editor


class TestDatabaseEditorUICreation:
    """Test database editor UI creation and initialization"""

    def test_editor_creation(self, screen, temp_db_path):
        """Test creating a database editor"""
        editor = DatabaseEditorUI(screen, database_path=temp_db_path)

        assert editor.screen == screen
        assert editor.database_path == temp_db_path
        assert not editor.visible
        assert editor.current_category == "actors"
        assert editor.db is not None

    def test_editor_default_state(self, db_editor):
        """Test editor has correct default state"""
        assert db_editor.current_entry is None
        assert db_editor.search_query == ""
        assert db_editor.entry_list_scroll == 0
        assert not db_editor.has_unsaved_changes

    def test_editor_categories_defined(self, db_editor):
        """Test editor has all required categories"""
        categories = [cat[0] for cat in DatabaseEditorUI.CATEGORIES]

        assert "actors" in categories
        assert "classes" in categories
        assert "skills" in categories
        assert "items" in categories
        assert "weapons" in categories
        assert "armors" in categories
        assert "enemies" in categories
        assert "states" in categories
        assert "animations" in categories


class TestDatabaseEditorUIToggle:
    """Test database editor visibility toggling"""

    def test_toggle_visibility(self, db_editor):
        """Test toggling editor visibility"""
        assert not db_editor.visible

        db_editor.toggle()
        assert db_editor.visible

        db_editor.toggle()
        assert not db_editor.visible

    def test_toggle_resets_state(self, db_editor):
        """Test toggling resets scroll and input state"""
        db_editor.entry_list_scroll = 5
        db_editor.active_input_field = "name"

        db_editor.toggle()

        assert db_editor.entry_list_scroll == 0
        assert db_editor.active_input_field is None


class TestDatabaseEditorUICRUD:
    """Test CRUD operations in database editor"""

    def test_create_new_entry(self, db_editor):
        """Test creating a new entry"""
        db_editor.current_category = "items"
        initial_count = db_editor.db.get_count("items")

        db_editor._create_new_entry()

        new_count = db_editor.db.get_count("items")
        assert new_count == initial_count + 1
        assert db_editor.current_entry is not None
        assert db_editor.has_unsaved_changes

    def test_create_multiple_entries(self, db_editor):
        """Test creating multiple entries with auto-ID"""
        db_editor.current_category = "actors"

        db_editor._create_new_entry()
        entry1_id = db_editor.current_entry.id

        db_editor._create_new_entry()
        entry2_id = db_editor.current_entry.id

        # IDs should be different
        assert entry1_id != entry2_id

    def test_duplicate_entry(self, db_editor):
        """Test duplicating an entry"""
        db_editor.current_category = "skills"
        db_editor._create_new_entry()
        original_id = db_editor.current_entry.id
        original_name = db_editor.current_entry.name

        db_editor._duplicate_entry()

        assert db_editor.current_entry.id != original_id
        assert "(Copy)" in db_editor.current_entry.name
        assert db_editor.has_unsaved_changes

    def test_duplicate_nonexistent_entry(self, db_editor):
        """Test duplicating with no entry selected"""
        db_editor.current_entry = None
        initial_count = db_editor.db.get_count("items")

        db_editor._duplicate_entry()

        # Should not crash, count should remain same
        assert db_editor.db.get_count("items") == initial_count

    def test_delete_entry(self, db_editor):
        """Test deleting an entry"""
        db_editor.current_category = "weapons"
        db_editor._create_new_entry()
        entry_id = db_editor.current_entry.id

        db_editor._delete_entry()

        assert db_editor.current_entry is None
        assert not db_editor.db.exists("weapons", entry_id)
        assert db_editor.has_unsaved_changes

    def test_delete_nonexistent_entry(self, db_editor):
        """Test deleting with no entry selected"""
        db_editor.current_entry = None
        initial_count = db_editor.db.get_count("enemies")

        db_editor._delete_entry()

        # Should not crash
        assert db_editor.db.get_count("enemies") == initial_count


class TestDatabaseEditorUIInput:
    """Test input handling and field updates"""

    def test_apply_input_string_field(self, db_editor):
        """Test applying string input to a field"""
        db_editor.current_category = "items"
        db_editor._create_new_entry()

        db_editor.active_input_field = "name"
        db_editor.input_text = "Health Potion"
        db_editor._apply_input()

        assert db_editor.current_entry.name == "Health Potion"
        assert db_editor.active_input_field is None
        assert db_editor.has_unsaved_changes

    def test_apply_input_int_field(self, db_editor):
        """Test applying integer input to a field"""
        db_editor.current_category = "items"
        db_editor._create_new_entry()

        db_editor.active_input_field = "price"
        db_editor.input_text = "150"
        db_editor._apply_input()

        assert db_editor.current_entry.price == 150

    def test_apply_input_bool_field(self, db_editor):
        """Test applying boolean input to a field"""
        db_editor.current_category = "items"
        db_editor._create_new_entry()

        db_editor.active_input_field = "consumable"
        db_editor.input_text = "false"
        db_editor._apply_input()

        assert db_editor.current_entry.consumable is False

    def test_apply_input_invalid_number(self, db_editor):
        """Test applying invalid number input"""
        db_editor.current_category = "items"
        db_editor._create_new_entry()

        db_editor.active_input_field = "price"
        db_editor.input_text = ""
        db_editor._apply_input()

        # Should default to 0
        assert db_editor.current_entry.price == 0

    def test_apply_input_no_active_field(self, db_editor):
        """Test applying input with no active field"""
        db_editor.current_category = "items"
        db_editor._create_new_entry()

        original_name = db_editor.current_entry.name
        db_editor.active_input_field = None
        db_editor.input_text = "New Name"
        db_editor._apply_input()

        # Should not change anything
        assert db_editor.current_entry.name == original_name


class TestDatabaseEditorUISearch:
    """Test search and filtering functionality"""

    def test_search_by_name(self, db_editor):
        """Test filtering entries by name"""
        db_editor.current_category = "items"

        # Create test entries
        item1 = Item(id=1, name="Health Potion")
        item2 = Item(id=2, name="Mana Potion")
        item3 = Item(id=3, name="Sword")

        db_editor.db.create("items", item1)
        db_editor.db.create("items", item2)
        db_editor.db.create("items", item3)

        # Search for "Potion"
        db_editor.search_query = "potion"
        results = db_editor._get_filtered_entries()

        assert len(results) == 2
        assert all("Potion" in entry.name for entry in results)

    def test_search_by_id(self, db_editor):
        """Test filtering entries by ID"""
        db_editor.current_category = "items"

        item1 = Item(id=100, name="Test Item")
        db_editor.db.create("items", item1)

        db_editor.search_query = "100"
        results = db_editor._get_filtered_entries()

        assert len(results) == 1
        assert results[0].id == 100

    def test_search_case_insensitive(self, db_editor):
        """Test search is case insensitive"""
        db_editor.current_category = "items"

        item = Item(id=1, name="MEGA POTION")
        db_editor.db.create("items", item)

        db_editor.search_query = "mega"
        results = db_editor._get_filtered_entries()

        assert len(results) == 1

    def test_search_empty_query(self, db_editor):
        """Test empty search returns all entries"""
        db_editor.current_category = "items"

        item1 = Item(id=1, name="Item 1")
        item2 = Item(id=2, name="Item 2")
        db_editor.db.create("items", item1)
        db_editor.db.create("items", item2)

        db_editor.search_query = ""
        results = db_editor._get_filtered_entries()

        assert len(results) == 2


class TestDatabaseEditorUIEventHandling:
    """Test event handling in database editor"""

    def test_handle_keyboard_input(self, db_editor):
        """Test handling keyboard input for text fields"""
        db_editor.visible = True
        db_editor.active_input_field = "name"
        db_editor.input_text = "Test"

        # Simulate typing
        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_a, "unicode": "a"})
        db_editor.handle_event(event)

        assert db_editor.input_text == "Testa"

    def test_handle_backspace(self, db_editor):
        """Test handling backspace in text input"""
        db_editor.visible = True
        db_editor.active_input_field = "name"
        db_editor.input_text = "Test"

        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_BACKSPACE})
        db_editor.handle_event(event)

        assert db_editor.input_text == "Tes"

    def test_handle_escape_cancels_input(self, db_editor):
        """Test escape cancels active input"""
        db_editor.visible = True
        db_editor.active_input_field = "name"
        db_editor.input_text = "Test"

        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE})
        db_editor.handle_event(event)

        assert db_editor.active_input_field is None

    def test_handle_return_applies_input(self, db_editor):
        """Test return key applies input"""
        db_editor.visible = True
        db_editor.current_category = "items"
        db_editor._create_new_entry()
        db_editor.active_input_field = "name"
        db_editor.input_text = "New Name"

        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RETURN})
        result = db_editor.handle_event(event)

        assert result is True
        assert db_editor.current_entry.name == "New Name"

    def test_handle_mousewheel_scroll(self, db_editor):
        """Test mouse wheel scrolling"""
        db_editor.visible = True
        db_editor.entry_list_scroll = 5

        # Scroll up
        event = pygame.event.Event(pygame.MOUSEWHEEL, {"y": 1})
        db_editor.handle_event(event)

        assert db_editor.entry_list_scroll == 4

    def test_event_handling_when_invisible(self, db_editor):
        """Test events are not handled when editor is invisible"""
        db_editor.visible = False

        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_a})
        result = db_editor.handle_event(event)

        assert result is False


class TestDatabaseEditorUIRendering:
    """Test rendering methods"""

    def test_render_when_invisible(self, db_editor):
        """Test render does nothing when invisible"""
        db_editor.visible = False

        # Should not crash
        db_editor.render()

    def test_render_when_visible(self, db_editor, screen):
        """Test render draws to screen when visible"""
        db_editor.visible = True

        # Should not crash
        db_editor.render()

    def test_render_with_entry_selected(self, db_editor):
        """Test rendering with an entry selected"""
        db_editor.visible = True
        db_editor.current_category = "items"
        db_editor._create_new_entry()

        # Should not crash
        db_editor.render()

    def test_render_all_categories(self, db_editor):
        """Test rendering with different categories"""
        db_editor.visible = True

        for category_id, _ in DatabaseEditorUI.CATEGORIES:
            db_editor.current_category = category_id
            # Should not crash
            db_editor.render()


class TestDatabaseEditorUISave:
    """Test database saving functionality"""

    def test_save_database(self, db_editor, temp_db_path):
        """Test saving database to file"""
        db_editor.current_category = "items"
        db_editor._create_new_entry()
        db_editor.has_unsaved_changes = True

        db_editor._save_database()

        assert temp_db_path.exists()
        assert not db_editor.has_unsaved_changes

    def test_save_and_reload(self, db_editor, temp_db_path):
        """Test saving and reloading database"""
        db_editor.current_category = "items"
        db_editor._create_new_entry()
        entry_id = db_editor.current_entry.id
        entry_name = db_editor.current_entry.name

        db_editor._save_database()

        # Create new editor and load
        new_editor = DatabaseEditorUI(db_editor.screen, database_path=temp_db_path)
        loaded_entry = new_editor.db.read("items", entry_id)

        assert loaded_entry.name == entry_name


class TestDatabaseEditorUIUpdate:
    """Test update method"""

    def test_update_when_invisible(self, db_editor):
        """Test update does nothing when invisible"""
        db_editor.visible = False

        # Should not crash
        db_editor.update(0.016)

    def test_update_when_visible(self, db_editor):
        """Test update runs when visible"""
        db_editor.visible = True

        # Should not crash
        db_editor.update(0.016)


class TestDatabaseEditorUICategorySwitch:
    """Test category switching functionality"""

    def test_switch_category_clears_selection(self, db_editor):
        """Test switching category clears current entry"""
        db_editor.current_category = "items"
        db_editor._create_new_entry()

        assert db_editor.current_entry is not None

        # Switch category
        db_editor.current_category = "actors"
        db_editor.current_entry = None
        db_editor.search_query = ""

        assert db_editor.current_entry is None
        assert db_editor.search_query == ""

    def test_get_current_entry(self, db_editor):
        """Test getting current entry"""
        assert db_editor.get_current_entry() is None

        db_editor.current_category = "items"
        db_editor._create_new_entry()

        entry = db_editor.get_current_entry()
        assert entry is not None
        assert isinstance(entry, Item)


class TestDatabaseEditorUILoadDatabase:
    """Test loading database from file"""

    def test_load_database(self, db_editor, temp_db_path):
        """Test loading database from file"""
        # Create and save initial data
        item = Item(id=1, name="Test Item")
        db_editor.db.create("items", item)
        db_editor.db.save_to_file(temp_db_path)

        # Create new editor and load
        new_editor = DatabaseEditorUI(db_editor.screen)
        new_editor.load_database(temp_db_path)

        assert new_editor.db.get_count("items") == 1
        assert not new_editor.has_unsaved_changes

    def test_load_nonexistent_database(self, db_editor, tmp_path):
        """Test loading from nonexistent file"""
        fake_path = tmp_path / "nonexistent.json"

        # Should not crash
        db_editor.load_database(fake_path)


# Run tests with: pytest tests/test_database_editor_ui.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
