"""
Tests for newly implemented UI components.

Tests the Event Editor, Database Manager, and Character Generator UIs.
"""

import pytest
import pygame

from neonworks.core.ecs import World
from neonworks.ui.event_editor_ui import EventEditorUI
from neonworks.ui.database_manager_ui import DatabaseManagerUI
from neonworks.ui.character_generator_ui import CharacterGeneratorUI


@pytest.fixture
def pygame_init():
    """Initialize pygame for UI tests."""
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    yield screen
    pygame.quit()


@pytest.fixture
def world():
    """Create a test world."""
    return World()


@pytest.fixture
def renderer():
    """Create a mock renderer."""
    return None  # Simple mock for testing


class TestEventEditorUI:
    """Test Event Editor UI."""

    def test_event_editor_initialization(self, pygame_init, world, renderer):
        """Test event editor can be initialized."""
        event_editor = EventEditorUI(world, renderer)

        assert event_editor is not None
        assert event_editor.world == world
        assert event_editor.visible == False
        assert event_editor.events == []

    def test_event_editor_toggle(self, pygame_init, world, renderer):
        """Test event editor toggle functionality."""
        event_editor = EventEditorUI(world, renderer)

        # Initially not visible
        assert event_editor.visible == False

        # Toggle on
        event_editor.toggle()
        assert event_editor.visible == True

        # Toggle off
        event_editor.toggle()
        assert event_editor.visible == False

    def test_new_event_creation(self, pygame_init, world, renderer):
        """Test creating a new event."""
        event_editor = EventEditorUI(world, renderer)

        initial_count = len(event_editor.events)
        event_editor.new_event()

        assert len(event_editor.events) == initial_count + 1
        assert event_editor.selected_event is not None
        assert "id" in event_editor.selected_event
        assert "trigger" in event_editor.selected_event
        assert "actions" in event_editor.selected_event

    def test_delete_event(self, pygame_init, world, renderer):
        """Test deleting an event."""
        event_editor = EventEditorUI(world, renderer)

        # Create an event
        event_editor.new_event()
        event = event_editor.selected_event

        # Delete it
        event_editor.delete_event()

        assert event not in event_editor.events
        assert event_editor.selected_event is None

    def test_add_action_to_event(self, pygame_init, world, renderer):
        """Test adding an action to an event."""
        event_editor = EventEditorUI(world, renderer)

        # Create an event
        event_editor.new_event()
        initial_actions = len(event_editor.selected_event["actions"])

        # Add an action
        event_editor.add_action()

        assert len(event_editor.selected_event["actions"]) == initial_actions + 1

    def test_remove_action(self, pygame_init, world, renderer):
        """Test removing an action from event."""
        event_editor = EventEditorUI(world, renderer)

        # Create event with action
        event_editor.new_event()
        event_editor.add_action()
        event_editor.selected_action_index = 0

        initial_count = len(event_editor.selected_event["actions"])

        # Remove action
        event_editor.remove_action()

        assert len(event_editor.selected_event["actions"]) == initial_count - 1


class TestDatabaseManagerUI:
    """Test Database Manager UI."""

    def test_database_manager_initialization(self, pygame_init, world, renderer):
        """Test database manager can be initialized."""
        db_manager = DatabaseManagerUI(world, renderer)

        assert db_manager is not None
        assert db_manager.world == world
        assert db_manager.visible == False
        assert isinstance(db_manager.database, dict)

    def test_database_manager_toggle(self, pygame_init, world, renderer):
        """Test database manager toggle functionality."""
        db_manager = DatabaseManagerUI(world, renderer)

        # Initially not visible
        assert db_manager.visible == False

        # Toggle on
        db_manager.toggle()
        assert db_manager.visible == True

        # Toggle off
        db_manager.toggle()
        assert db_manager.visible == False

    def test_new_entity_creation(self, pygame_init, world, renderer):
        """Test creating a new entity in database."""
        db_manager = DatabaseManagerUI(world, renderer)
        db_manager.current_category = "Characters"

        initial_count = len(db_manager.database.get("Characters", []))
        db_manager.new_entity()

        assert len(db_manager.database["Characters"]) == initial_count + 1
        assert db_manager.selected_entity is not None

    def test_duplicate_entity(self, pygame_init, world, renderer):
        """Test duplicating an entity."""
        db_manager = DatabaseManagerUI(world, renderer)
        db_manager.current_category = "Items"

        # Create an entity
        db_manager.new_entity()
        original_id = db_manager.selected_entity["id"]

        # Duplicate it
        db_manager.duplicate_entity()

        assert len(db_manager.database["Items"]) == 2
        assert db_manager.selected_entity["id"] != original_id
        assert "_copy" in db_manager.selected_entity["id"]

    def test_delete_entity(self, pygame_init, world, renderer):
        """Test deleting an entity."""
        db_manager = DatabaseManagerUI(world, renderer)
        db_manager.current_category = "Skills"

        # Create an entity
        db_manager.new_entity()
        entity = db_manager.selected_entity

        # Delete it
        db_manager.delete_entity()

        assert entity not in db_manager.database.get("Skills", [])
        assert db_manager.selected_entity is None

    def test_category_switching(self, pygame_init, world, renderer):
        """Test switching between categories."""
        db_manager = DatabaseManagerUI(world, renderer)

        # Switch to different categories
        for category in db_manager.CATEGORIES:
            db_manager.current_category = category
            assert db_manager.current_category == category


class TestCharacterGeneratorUI:
    """Test Character Generator UI."""

    def test_character_generator_initialization(self, pygame_init, world, renderer):
        """Test character generator can be initialized."""
        char_gen = CharacterGeneratorUI(world, renderer)

        assert char_gen is not None
        assert char_gen.world == world
        assert char_gen.visible == False
        assert isinstance(char_gen.character, dict)

    def test_character_generator_toggle(self, pygame_init, world, renderer):
        """Test character generator toggle functionality."""
        char_gen = CharacterGeneratorUI(world, renderer)

        # Initially not visible
        assert char_gen.visible == False

        # Toggle on
        char_gen.toggle()
        assert char_gen.visible == True

        # Toggle off
        char_gen.toggle()
        assert char_gen.visible == False

    def test_apply_archetype(self, pygame_init, world, renderer):
        """Test applying character archetypes."""
        char_gen = CharacterGeneratorUI(world, renderer)

        # Apply warrior archetype
        char_gen.archetype_dropdown.selected = "Warrior"
        char_gen.apply_archetype()

        stats = char_gen.character["stats"]
        assert stats["hp"] == 120
        assert stats["attack"] == 15
        assert stats["defense"] == 12

    def test_randomize_stats(self, pygame_init, world, renderer):
        """Test randomizing character stats."""
        char_gen = CharacterGeneratorUI(world, renderer)

        original_hp = char_gen.character["stats"]["hp"]
        char_gen.randomize_stats()

        # Stats should be randomized (very unlikely to be same)
        # Just check they're in valid ranges
        assert 60 <= char_gen.character["stats"]["hp"] <= 150
        assert 10 <= char_gen.character["stats"]["mp"] <= 100
        assert 5 <= char_gen.character["stats"]["attack"] <= 20

    def test_clear_character(self, pygame_init, world, renderer):
        """Test clearing character data."""
        char_gen = CharacterGeneratorUI(world, renderer)

        # Modify character
        char_gen.character["name"] = "Test Character"
        char_gen.character["stats"]["hp"] = 999

        # Clear
        char_gen.clear_character()

        # Should be back to defaults
        assert char_gen.character["name"] == "New Character"
        assert char_gen.character["stats"]["hp"] == 100

    def test_archetype_dropdown_options(self, pygame_init, world, renderer):
        """Test all archetype options are available."""
        char_gen = CharacterGeneratorUI(world, renderer)

        expected_archetypes = [
            "Warrior",
            "Mage",
            "Rogue",
            "Cleric",
            "Paladin",
            "Ranger",
            "Barbarian",
            "Monk",
            "Bard",
            "Custom",
        ]

        assert char_gen.ARCHETYPES == expected_archetypes

    def test_class_options(self, pygame_init, world, renderer):
        """Test character class options."""
        char_gen = CharacterGeneratorUI(world, renderer)

        expected_classes = ["hero", "enemy", "npc", "boss"]

        assert char_gen.CLASSES == expected_classes


class TestUIIntegration:
    """Test integration between UIs."""

    def test_all_uis_can_coexist(self, pygame_init, world, renderer):
        """Test that all UIs can be created simultaneously."""
        event_editor = EventEditorUI(world, renderer)
        db_manager = DatabaseManagerUI(world, renderer)
        char_gen = CharacterGeneratorUI(world, renderer)

        assert event_editor is not None
        assert db_manager is not None
        assert char_gen is not None

    def test_render_does_not_crash(self, pygame_init, world, renderer):
        """Test that rendering UIs doesn't crash."""
        screen = pygame_init

        event_editor = EventEditorUI(world, renderer)
        db_manager = DatabaseManagerUI(world, renderer)
        char_gen = CharacterGeneratorUI(world, renderer)

        # Make visible and render
        event_editor.visible = True
        db_manager.visible = True
        char_gen.visible = True

        # Should not crash
        event_editor.render(screen)
        db_manager.render(screen)
        char_gen.render(screen)

    def test_update_does_not_crash(self, pygame_init, world, renderer):
        """Test that updating UIs doesn't crash."""
        event_editor = EventEditorUI(world, renderer)
        db_manager = DatabaseManagerUI(world, renderer)
        char_gen = CharacterGeneratorUI(world, renderer)

        # Make visible
        event_editor.visible = True
        db_manager.visible = True
        char_gen.visible = True

        # Should not crash
        event_editor.update(0.016)  # 60 FPS
        db_manager.update(0.016)
        char_gen.update(0.016)
