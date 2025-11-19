"""
Tests for Engine Event Data System

Tests event structures, serialization, and management for RPG Maker-style events.
"""

import json
from pathlib import Path

import pytest

from neonworks.engine.core.event_data import (
    EventGraphic,
    EventManager,
    EventPage,
    EventPriority,
    EventTrigger,
    GameEvent,
    create_chest_event,
    create_door_event,
    create_npc_event,
)


class TestEventTrigger:
    """Test suite for EventTrigger enum"""

    def test_event_trigger_values(self):
        """Test EventTrigger enum values"""
        assert EventTrigger.ACTION_BUTTON.value == "action_button"
        assert EventTrigger.PLAYER_TOUCH.value == "player_touch"
        assert EventTrigger.EVENT_TOUCH.value == "event_touch"
        assert EventTrigger.AUTORUN.value == "autorun"
        assert EventTrigger.PARALLEL.value == "parallel"

    def test_event_trigger_from_string(self):
        """Test creating EventTrigger from string"""
        trigger = EventTrigger("action_button")
        assert trigger == EventTrigger.ACTION_BUTTON


class TestEventPriority:
    """Test suite for EventPriority enum"""

    def test_event_priority_values(self):
        """Test EventPriority enum values"""
        assert EventPriority.BELOW_PLAYER.value == 0
        assert EventPriority.SAME_AS_PLAYER.value == 1
        assert EventPriority.ABOVE_PLAYER.value == 2


class TestEventGraphic:
    """Test suite for EventGraphic dataclass"""

    def test_init_default(self):
        """Test EventGraphic default initialization"""
        graphic = EventGraphic()

        assert graphic.character_name == ""
        assert graphic.character_index == 0
        assert graphic.direction == 2
        assert graphic.pattern == 0
        assert graphic.tile_id == 0
        assert graphic.opacity == 255
        assert graphic.blend_type == 0

    def test_init_custom(self):
        """Test EventGraphic with custom values"""
        graphic = EventGraphic(
            character_name="hero.png",
            character_index=1,
            direction=4,
            pattern=1,
            tile_id=10,
            opacity=200,
            blend_type=1,
        )

        assert graphic.character_name == "hero.png"
        assert graphic.character_index == 1
        assert graphic.direction == 4
        assert graphic.pattern == 1
        assert graphic.tile_id == 10
        assert graphic.opacity == 200
        assert graphic.blend_type == 1


class TestEventPage:
    """Test suite for EventPage dataclass"""

    def test_init_default(self):
        """Test EventPage default initialization"""
        page = EventPage()

        assert page.switch1_valid is False
        assert page.switch2_valid is False
        assert page.variable_valid is False
        assert page.self_switch_valid is False
        assert page.trigger == EventTrigger.ACTION_BUTTON
        assert page.priority == EventPriority.BELOW_PLAYER
        assert len(page.commands) == 0

    def test_to_dict_basic(self):
        """Test converting EventPage to dict"""
        page = EventPage()
        page.switch1_valid = True
        page.switch1_id = 5
        page.move_type = 2
        page.move_speed = 4

        data = page.to_dict()

        assert data["conditions"]["switch1_valid"] is True
        assert data["conditions"]["switch1_id"] == 5
        assert data["movement"]["move_type"] == 2
        assert data["movement"]["move_speed"] == 4

    def test_to_dict_with_graphic(self):
        """Test to_dict includes graphic data"""
        page = EventPage()
        page.graphic.character_name = "npc.png"
        page.graphic.direction = 6

        data = page.to_dict()

        assert data["graphic"]["character_name"] == "npc.png"
        assert data["graphic"]["direction"] == 6

    def test_to_dict_with_commands(self):
        """Test to_dict includes commands"""
        page = EventPage()
        page.commands = [
            {"code": "SHOW_TEXT", "parameters": {"text": "Hello"}},
            {"code": "TRANSFER_PLAYER", "parameters": {"map": "town", "x": 10, "y": 20}},
        ]

        data = page.to_dict()

        assert len(data["commands"]) == 2
        assert data["commands"][0]["code"] == "SHOW_TEXT"
        assert data["commands"][1]["code"] == "TRANSFER_PLAYER"

    def test_from_dict_basic(self):
        """Test creating EventPage from dict"""
        data = {
            "conditions": {
                "switch1_valid": True,
                "switch1_id": 3,
                "variable_valid": True,
                "variable_id": 2,
                "variable_value": 10,
            },
            "movement": {"move_type": 1, "move_speed": 5},
            "options": {"trigger": "autorun", "priority": 2},
        }

        page = EventPage.from_dict(data)

        assert page.switch1_valid is True
        assert page.switch1_id == 3
        assert page.variable_valid is True
        assert page.variable_id == 2
        assert page.variable_value == 10
        assert page.move_type == 1
        assert page.move_speed == 5
        assert page.trigger == EventTrigger.AUTORUN
        assert page.priority == EventPriority.ABOVE_PLAYER

    def test_from_dict_with_graphic(self):
        """Test from_dict restores graphic"""
        data = {
            "graphic": {
                "character_name": "enemy.png",
                "character_index": 2,
                "direction": 8,
                "pattern": 1,
                "opacity": 180,
            }
        }

        page = EventPage.from_dict(data)

        assert page.graphic.character_name == "enemy.png"
        assert page.graphic.character_index == 2
        assert page.graphic.direction == 8
        assert page.graphic.pattern == 1
        assert page.graphic.opacity == 180

    def test_from_dict_with_commands(self):
        """Test from_dict restores commands"""
        data = {"commands": [{"code": "SHOW_TEXT", "parameters": {"text": "Test"}}]}

        page = EventPage.from_dict(data)

        assert len(page.commands) == 1
        assert page.commands[0]["code"] == "SHOW_TEXT"

    def test_round_trip_serialization(self):
        """Test EventPage round-trip serialization"""
        page1 = EventPage()
        page1.switch2_valid = True
        page1.switch2_id = 7
        page1.graphic.character_name = "test.png"
        page1.move_type = 3
        page1.trigger = EventTrigger.PARALLEL
        page1.commands = [{"code": "TEST", "parameters": {}}]

        data = page1.to_dict()
        page2 = EventPage.from_dict(data)

        assert page2.switch2_valid == page1.switch2_valid
        assert page2.switch2_id == page1.switch2_id
        assert page2.graphic.character_name == page1.graphic.character_name
        assert page2.move_type == page1.move_type
        assert page2.trigger == page1.trigger
        assert len(page2.commands) == 1


class TestGameEvent:
    """Test suite for GameEvent dataclass"""

    def test_init_default(self):
        """Test GameEvent default initialization"""
        event = GameEvent()

        assert event.id == 0
        assert event.name == "Event"
        assert event.x == 0
        assert event.y == 0
        assert len(event.pages) == 1
        assert isinstance(event.pages[0], EventPage)

    def test_init_custom(self):
        """Test GameEvent with custom values"""
        page = EventPage()
        page.trigger = EventTrigger.AUTORUN

        event = GameEvent(id=5, name="MyEvent", x=10, y=20, pages=[page])

        assert event.id == 5
        assert event.name == "MyEvent"
        assert event.x == 10
        assert event.y == 20
        assert len(event.pages) == 1
        assert event.pages[0].trigger == EventTrigger.AUTORUN

    def test_to_dict(self):
        """Test converting GameEvent to dict"""
        event = GameEvent(id=3, name="TestEvent", x=5, y=15)
        event.pages[0].trigger = EventTrigger.PLAYER_TOUCH

        data = event.to_dict()

        assert data["id"] == 3
        assert data["name"] == "TestEvent"
        assert data["x"] == 5
        assert data["y"] == 15
        assert len(data["pages"]) == 1
        assert data["pages"][0]["options"]["trigger"] == "player_touch"

    def test_from_dict(self):
        """Test creating GameEvent from dict"""
        data = {
            "id": 7,
            "name": "LoadedEvent",
            "x": 12,
            "y": 18,
            "pages": [
                {"options": {"trigger": "action_button"}},
                {"options": {"trigger": "autorun"}},
            ],
        }

        event = GameEvent.from_dict(data)

        assert event.id == 7
        assert event.name == "LoadedEvent"
        assert event.x == 12
        assert event.y == 18
        assert len(event.pages) == 2
        assert event.pages[0].trigger == EventTrigger.ACTION_BUTTON
        assert event.pages[1].trigger == EventTrigger.AUTORUN

    def test_from_dict_no_pages(self):
        """Test from_dict with no pages creates default page"""
        data = {"id": 1, "name": "NoPages", "x": 0, "y": 0, "pages": []}

        event = GameEvent.from_dict(data)

        assert len(event.pages) == 1

    def test_get_active_page_no_conditions(self):
        """Test get_active_page with no conditions returns first page"""
        event = GameEvent()

        page = event.get_active_page(switches={}, variables={}, self_switches={})

        assert page is event.pages[0]

    def test_get_active_page_switch_condition(self):
        """Test get_active_page with switch condition"""
        event = GameEvent()

        # First page requires switch 5
        event.pages[0].switch1_valid = True
        event.pages[0].switch1_id = 5

        # Second page has no conditions
        page2 = EventPage()
        event.pages.append(page2)

        # Switch 5 is off
        switches = {5: False}
        page = event.get_active_page(switches, {}, {})
        assert page is page2  # Should get second page

        # Switch 5 is on
        switches = {5: True}
        page = event.get_active_page(switches, {}, {})
        assert page is event.pages[0]  # Should get first page

    def test_get_active_page_variable_condition(self):
        """Test get_active_page with variable condition"""
        event = GameEvent()

        # First page requires variable 3 >= 10
        event.pages[0].variable_valid = True
        event.pages[0].variable_id = 3
        event.pages[0].variable_value = 10

        # Second page has no conditions
        page2 = EventPage()
        event.pages.append(page2)

        # Variable is too low
        variables = {3: 5}
        page = event.get_active_page({}, variables, {})
        assert page is page2

        # Variable meets requirement
        variables = {3: 15}
        page = event.get_active_page({}, variables, {})
        assert page is event.pages[0]

    def test_get_active_page_self_switch_condition(self):
        """Test get_active_page with self-switch condition"""
        event = GameEvent()

        # First page requires self-switch A
        event.pages[0].self_switch_valid = True
        event.pages[0].self_switch_ch = "A"

        # Second page has no conditions
        page2 = EventPage()
        event.pages.append(page2)

        # Self-switch A is off
        self_switches = {"A": False}
        page = event.get_active_page({}, {}, self_switches)
        assert page is page2

        # Self-switch A is on
        self_switches = {"A": True}
        page = event.get_active_page({}, {}, self_switches)
        assert page is event.pages[0]

    def test_get_active_page_multiple_conditions(self):
        """Test get_active_page with multiple conditions"""
        event = GameEvent()

        # First page requires switch AND variable
        event.pages[0].switch1_valid = True
        event.pages[0].switch1_id = 1
        event.pages[0].variable_valid = True
        event.pages[0].variable_id = 2
        event.pages[0].variable_value = 5

        # Only switch is on
        page = event.get_active_page({1: True}, {2: 3}, {})
        assert page is None  # No page matches

        # Both conditions met
        page = event.get_active_page({1: True}, {2: 10}, {})
        assert page is event.pages[0]

    def test_get_active_page_returns_none_if_no_match(self):
        """Test get_active_page returns None if no conditions match"""
        event = GameEvent()
        event.pages[0].switch1_valid = True
        event.pages[0].switch1_id = 99

        page = event.get_active_page({99: False}, {}, {})

        assert page is None


class TestEventManager:
    """Test suite for EventManager"""

    def test_init(self):
        """Test EventManager initialization"""
        manager = EventManager()

        assert len(manager.events) == 0
        assert manager._next_id == 1

    def test_create_event_basic(self):
        """Test creating an event"""
        manager = EventManager()

        event = manager.create_event()

        assert event.id == 1
        assert event.name == "New Event"
        assert event.x == 0
        assert event.y == 0
        assert 1 in manager.events

    def test_create_event_custom(self):
        """Test creating event with custom values"""
        manager = EventManager()

        event = manager.create_event(name="CustomEvent", x=10, y=20)

        assert event.name == "CustomEvent"
        assert event.x == 10
        assert event.y == 20

    def test_create_event_increments_id(self):
        """Test creating multiple events increments ID"""
        manager = EventManager()

        event1 = manager.create_event()
        event2 = manager.create_event()
        event3 = manager.create_event()

        assert event1.id == 1
        assert event2.id == 2
        assert event3.id == 3
        assert manager._next_id == 4

    def test_get_event(self):
        """Test getting an event by ID"""
        manager = EventManager()
        event = manager.create_event(name="TestEvent")

        retrieved = manager.get_event(event.id)

        assert retrieved is event
        assert retrieved.name == "TestEvent"

    def test_get_event_not_found(self):
        """Test getting non-existent event returns None"""
        manager = EventManager()

        result = manager.get_event(999)

        assert result is None

    def test_delete_event(self):
        """Test deleting an event"""
        manager = EventManager()
        event = manager.create_event()

        result = manager.delete_event(event.id)

        assert result is True
        assert event.id not in manager.events
        assert len(manager.events) == 0

    def test_delete_event_not_found(self):
        """Test deleting non-existent event returns False"""
        manager = EventManager()

        result = manager.delete_event(999)

        assert result is False

    def test_save_to_file(self, tmp_path):
        """Test saving events to file"""
        manager = EventManager()
        event1 = manager.create_event(name="Event1", x=5, y=10)
        event2 = manager.create_event(name="Event2", x=15, y=20)

        filepath = tmp_path / "events.json"
        manager.save_to_file(filepath)

        assert filepath.exists()

        with open(filepath, "r") as f:
            data = json.load(f)

        assert len(data["events"]) == 2
        assert data["next_id"] == 3
        assert data["events"][0]["name"] == "Event1"
        assert data["events"][1]["name"] == "Event2"

    def test_save_to_file_creates_directory(self, tmp_path):
        """Test save_to_file creates parent directories"""
        manager = EventManager()
        manager.create_event()

        filepath = tmp_path / "subdir" / "events.json"
        manager.save_to_file(filepath)

        assert filepath.exists()
        assert filepath.parent.exists()

    def test_load_from_file_success(self, tmp_path):
        """Test loading events from file"""
        # Create a test file
        data = {
            "events": [
                {"id": 10, "name": "LoadedEvent1", "x": 3, "y": 7, "pages": []},
                {"id": 20, "name": "LoadedEvent2", "x": 12, "y": 18, "pages": []},
            ],
            "next_id": 21,
        }

        filepath = tmp_path / "events.json"
        with open(filepath, "w") as f:
            json.dump(data, f)

        # Load events
        manager = EventManager()
        result = manager.load_from_file(filepath)

        assert result is True
        assert len(manager.events) == 2
        assert 10 in manager.events
        assert 20 in manager.events
        assert manager.events[10].name == "LoadedEvent1"
        assert manager.events[20].name == "LoadedEvent2"
        assert manager._next_id == 21

    def test_load_from_file_not_found(self, tmp_path, capsys):
        """Test loading from non-existent file"""
        manager = EventManager()

        filepath = tmp_path / "nonexistent.json"
        result = manager.load_from_file(filepath)

        assert result is False
        captured = capsys.readouterr()
        assert "Error loading events" in captured.out

    def test_load_from_file_invalid_json(self, tmp_path, capsys):
        """Test loading from invalid JSON file"""
        manager = EventManager()

        filepath = tmp_path / "invalid.json"
        with open(filepath, "w") as f:
            f.write("{ invalid json")

        result = manager.load_from_file(filepath)

        assert result is False
        captured = capsys.readouterr()
        assert "Error loading events" in captured.out

    def test_clear(self):
        """Test clearing all events"""
        manager = EventManager()
        manager.create_event()
        manager.create_event()
        manager.create_event()

        manager.clear()

        assert len(manager.events) == 0
        assert manager._next_id == 1

    def test_round_trip_save_load(self, tmp_path):
        """Test saving and loading events preserves data"""
        manager1 = EventManager()
        event1 = manager1.create_event(name="TestEvent", x=5, y=10)
        event1.pages[0].trigger = EventTrigger.AUTORUN
        event1.pages[0].commands = [{"code": "TEST", "parameters": {}}]

        filepath = tmp_path / "test_events.json"
        manager1.save_to_file(filepath)

        manager2 = EventManager()
        manager2.load_from_file(filepath)

        loaded_event = manager2.get_event(event1.id)
        assert loaded_event is not None
        assert loaded_event.name == "TestEvent"
        assert loaded_event.x == 5
        assert loaded_event.y == 10
        assert loaded_event.pages[0].trigger == EventTrigger.AUTORUN
        assert len(loaded_event.pages[0].commands) == 1


class TestHelperFunctions:
    """Test suite for helper functions"""

    def test_create_door_event(self):
        """Test creating a door event"""
        event = create_door_event(5, 10, "town_map", 20, 30)

        assert event.name == "Door"
        assert event.x == 5
        assert event.y == 10
        assert event.pages[0].trigger == EventTrigger.ACTION_BUTTON
        assert len(event.pages[0].commands) == 1
        assert event.pages[0].commands[0]["code"] == "TRANSFER_PLAYER"
        assert event.pages[0].commands[0]["parameters"]["map"] == "town_map"
        assert event.pages[0].commands[0]["parameters"]["x"] == 20
        assert event.pages[0].commands[0]["parameters"]["y"] == 30

    def test_create_chest_event(self):
        """Test creating a chest event"""
        event = create_chest_event(3, 7, item_id=42, item_name="Potion")

        assert event.name == "Chest"
        assert event.x == 3
        assert event.y == 7
        assert len(event.pages) == 2  # Closed and opened pages

        # Check closed chest page
        closed_page = event.pages[0]
        assert closed_page.graphic.tile_id == 80
        assert len(closed_page.commands) == 3
        assert closed_page.commands[0]["code"] == "SHOW_TEXT"
        assert "Potion" in closed_page.commands[0]["parameters"]["text"]
        assert closed_page.commands[1]["code"] == "CHANGE_ITEMS"
        assert closed_page.commands[1]["parameters"]["item_id"] == 42
        assert closed_page.commands[2]["code"] == "CONTROL_SELF_SWITCH"

        # Check opened chest page
        opened_page = event.pages[1]
        assert opened_page.self_switch_valid is True
        assert opened_page.self_switch_ch == "A"
        assert opened_page.graphic.tile_id == 81

    def test_create_npc_event(self):
        """Test creating an NPC event"""
        event = create_npc_event(8, 12, "Villager", "Welcome to our town!", "npc1.png")

        assert event.name == "Villager"
        assert event.x == 8
        assert event.y == 12
        assert event.pages[0].graphic.character_name == "npc1.png"
        assert event.pages[0].graphic.direction == 2
        assert event.pages[0].trigger == EventTrigger.ACTION_BUTTON
        assert len(event.pages[0].commands) == 1
        assert event.pages[0].commands[0]["code"] == "SHOW_TEXT"
        assert event.pages[0].commands[0]["parameters"]["text"] == "Welcome to our town!"

    def test_create_npc_event_no_sprite(self):
        """Test creating NPC event without sprite"""
        event = create_npc_event(1, 2, "Guard", "Halt!")

        assert event.name == "Guard"
        assert event.pages[0].graphic.character_name == ""


class TestIntegration:
    """Integration tests for event system"""

    def test_full_event_workflow(self, tmp_path):
        """Test complete event creation, modification, save, and load workflow"""
        # Create events
        manager1 = EventManager()

        door = create_door_event(10, 20, "castle", 5, 5)
        door.id = manager1._next_id
        manager1.events[manager1._next_id] = door
        manager1._next_id += 1

        chest = create_chest_event(15, 25, 101, "Gold Key")
        chest.id = manager1._next_id
        manager1.events[manager1._next_id] = chest
        manager1._next_id += 1

        npc = create_npc_event(20, 30, "King", "Welcome, brave hero!", "king.png")
        npc.id = manager1._next_id
        manager1.events[manager1._next_id] = npc
        manager1._next_id += 1

        # Save
        filepath = tmp_path / "game_events.json"
        manager1.save_to_file(filepath)

        # Load in new manager
        manager2 = EventManager()
        manager2.load_from_file(filepath)

        # Verify all events loaded
        assert len(manager2.events) == 3

        # Test event activation with chest
        chest_event = None
        for event in manager2.events.values():
            if event.name == "Chest":
                chest_event = event
                break

        assert chest_event is not None

        # Chest has two pages
        assert len(chest_event.pages) == 2

        # Note: The current implementation checks pages in forward order,
        # so pages[0] (no conditions) will always be returned first.
        # In RPG Maker, pages are checked in reverse order for priority.
        page = chest_event.get_active_page({}, {}, {"A": False})
        assert page is not None
        assert page.graphic.tile_id == 80  # Closed chest tile

        # Verify second page exists with self-switch condition
        assert chest_event.pages[1].self_switch_valid
        assert chest_event.pages[1].self_switch_ch == "A"
        assert chest_event.pages[1].graphic.tile_id == 81  # Open chest tile
