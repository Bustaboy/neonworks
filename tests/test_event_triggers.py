"""
Comprehensive tests for Event Trigger System

Tests trigger detection, event triggering, and event management.
"""

import json
from unittest.mock import MagicMock, Mock

import pytest

from neonworks.core.event_commands import (
    ControlSwitchesCommand,
    EventPage,
    GameEvent,
    ShowTextCommand,
    TriggerType,
    WaitCommand,
)
from neonworks.core.event_triggers import (
    EventTriggerHandler,
    EventTriggerManager,
    TriggerCondition,
    TriggerContext,
    TriggerResult,
    create_proximity_trigger,
    create_switch_trigger,
    create_variable_trigger,
)


# Mock GameState for testing
class MockGameState:
    """Mock game state for testing"""

    def __init__(self):
        self.switches = {}
        self.variables = {}
        self.items = set()
        self.actors = set()

    def get_switch(self, switch_id: int) -> bool:
        return self.switches.get(switch_id, False)

    def set_switch(self, switch_id: int, value: bool):
        self.switches[switch_id] = value

    def get_variable(self, variable_id: int) -> int:
        return self.variables.get(variable_id, 0)

    def set_variable(self, variable_id: int, value: int):
        self.variables[variable_id] = value

    def has_item(self, item_id: int) -> bool:
        return item_id in self.items

    def has_actor(self, actor_id: int) -> bool:
        return actor_id in self.actors


class TestTriggerCondition:
    """Test TriggerCondition functionality"""

    def test_condition_creation(self):
        """Test creating trigger condition"""
        condition = TriggerCondition(
            condition_type="proximity", parameters={"max_distance": 2}
        )

        assert condition.condition_type == "proximity"
        assert condition.parameters["max_distance"] == 2

    def test_proximity_condition_in_range(self):
        """Test proximity condition - in range"""
        condition = TriggerCondition(
            condition_type="proximity",
            parameters={"max_distance": 2, "event_pos": (5, 5)},
        )

        game_state = MockGameState()
        context = TriggerContext(
            game_state=game_state,
            player_position=(5, 6),  # 1 tile away
            player_direction=2,
        )

        assert condition.evaluate(context) is True

    def test_proximity_condition_out_of_range(self):
        """Test proximity condition - out of range"""
        condition = TriggerCondition(
            condition_type="proximity",
            parameters={"max_distance": 1, "event_pos": (5, 5)},
        )

        game_state = MockGameState()
        context = TriggerContext(
            game_state=game_state,
            player_position=(10, 10),  # Far away
            player_direction=2,
        )

        assert condition.evaluate(context) is False

    def test_switch_condition_true(self):
        """Test switch condition - switch is on"""
        condition = TriggerCondition(
            condition_type="switch", parameters={"switch_id": 5, "value": True}
        )

        game_state = MockGameState()
        game_state.set_switch(5, True)

        context = TriggerContext(
            game_state=game_state, player_position=(0, 0), player_direction=2
        )

        assert condition.evaluate(context) is True

    def test_switch_condition_false(self):
        """Test switch condition - switch is off"""
        condition = TriggerCondition(
            condition_type="switch", parameters={"switch_id": 5, "value": True}
        )

        game_state = MockGameState()
        game_state.set_switch(5, False)

        context = TriggerContext(
            game_state=game_state, player_position=(0, 0), player_direction=2
        )

        assert condition.evaluate(context) is False

    def test_variable_condition_operators(self):
        """Test variable condition with different operators"""
        game_state = MockGameState()
        game_state.set_variable(10, 50)

        context = TriggerContext(
            game_state=game_state, player_position=(0, 0), player_direction=2
        )

        # Test ==
        cond = TriggerCondition(
            "variable", {"variable_id": 10, "operator": "==", "value": 50}
        )
        assert cond.evaluate(context) is True

        # Test !=
        cond = TriggerCondition(
            "variable", {"variable_id": 10, "operator": "!=", "value": 30}
        )
        assert cond.evaluate(context) is True

        # Test >
        cond = TriggerCondition(
            "variable", {"variable_id": 10, "operator": ">", "value": 40}
        )
        assert cond.evaluate(context) is True

        # Test >=
        cond = TriggerCondition(
            "variable", {"variable_id": 10, "operator": ">=", "value": 50}
        )
        assert cond.evaluate(context) is True

        # Test <
        cond = TriggerCondition(
            "variable", {"variable_id": 10, "operator": "<", "value": 60}
        )
        assert cond.evaluate(context) is True

        # Test <=
        cond = TriggerCondition(
            "variable", {"variable_id": 10, "operator": "<=", "value": 50}
        )
        assert cond.evaluate(context) is True

    def test_condition_serialization(self):
        """Test condition to_dict/from_dict"""
        condition = TriggerCondition(
            condition_type="proximity", parameters={"max_distance": 3}
        )

        data = condition.to_dict()
        assert data["condition_type"] == "proximity"
        assert data["parameters"]["max_distance"] == 3

        condition2 = TriggerCondition.from_dict(data)
        assert condition2.condition_type == "proximity"
        assert condition2.parameters["max_distance"] == 3


class TestTriggerContext:
    """Test TriggerContext functionality"""

    def test_context_creation(self):
        """Test creating trigger context"""
        game_state = MockGameState()
        context = TriggerContext(
            game_state=game_state, player_position=(5, 10), player_direction=4
        )

        assert context.player_position == (5, 10)
        assert context.player_direction == 4
        assert context.action_button_pressed is False

    def test_event_position_cache(self):
        """Test event position caching"""
        game_state = MockGameState()
        context = TriggerContext(
            game_state=game_state, player_position=(0, 0), player_direction=2
        )

        # Set and get event position
        context.set_event_position(1, (10, 15))
        pos = context.get_event_position(1)

        assert pos == (10, 15)

    def test_distance_to_event(self):
        """Test distance calculation"""
        game_state = MockGameState()
        context = TriggerContext(
            game_state=game_state, player_position=(0, 0), player_direction=2
        )

        # Test distance to (3, 4) - should be 5
        distance = context.distance_to_event((3, 4))
        assert abs(distance - 5.0) < 0.01

        # Test distance to same position
        distance = context.distance_to_event((0, 0))
        assert distance == 0.0

    def test_is_adjacent_to(self):
        """Test adjacency check"""
        game_state = MockGameState()
        context = TriggerContext(
            game_state=game_state, player_position=(5, 5), player_direction=2
        )

        # Adjacent positions (including diagonal)
        assert context.is_adjacent_to((5, 6)) is True  # Below
        assert context.is_adjacent_to((5, 4)) is True  # Above
        assert context.is_adjacent_to((4, 5)) is True  # Left
        assert context.is_adjacent_to((6, 5)) is True  # Right
        assert context.is_adjacent_to((4, 4)) is True  # Diagonal
        assert context.is_adjacent_to((6, 6)) is True  # Diagonal

        # Not adjacent
        assert context.is_adjacent_to((5, 8)) is False
        assert context.is_adjacent_to((10, 10)) is False

    def test_is_in_front_of(self):
        """Test front-facing check"""
        game_state = MockGameState()

        # Player at (5, 5) facing down (direction 2)
        context = TriggerContext(
            game_state=game_state, player_position=(5, 5), player_direction=2
        )
        assert context.is_in_front_of((5, 6)) is True
        assert context.is_in_front_of((5, 4)) is False

        # Player facing left (direction 4)
        context.player_direction = 4
        assert context.is_in_front_of((4, 5)) is True
        assert context.is_in_front_of((6, 5)) is False

        # Player facing right (direction 6)
        context.player_direction = 6
        assert context.is_in_front_of((6, 5)) is True
        assert context.is_in_front_of((4, 5)) is False

        # Player facing up (direction 8)
        context.player_direction = 8
        assert context.is_in_front_of((5, 4)) is True
        assert context.is_in_front_of((5, 6)) is False


class TestEventTriggerHandler:
    """Test EventTriggerHandler functionality"""

    def test_handler_creation(self):
        """Test creating trigger handler"""
        event = GameEvent(id=1, name="Test", x=5, y=5)
        page = EventPage(trigger=TriggerType.ACTION_BUTTON)

        handler = EventTriggerHandler(event=event, page=page)

        assert handler.event == event
        assert handler.page == page
        assert handler.is_active is False

    def test_action_button_trigger_success(self):
        """Test action button trigger - successful activation"""
        event = GameEvent(id=1, name="NPC", x=5, y=5)
        page = EventPage(trigger=TriggerType.ACTION_BUTTON)

        handler = EventTriggerHandler(event=event, page=page)

        game_state = MockGameState()
        context = TriggerContext(
            game_state=game_state,
            player_position=(5, 4),  # Player above event
            player_direction=2,  # Facing down
            action_button_pressed=True,
        )

        result = handler.check_trigger(context)
        assert result == TriggerResult.TRIGGERED

    def test_action_button_trigger_not_pressed(self):
        """Test action button trigger - button not pressed"""
        event = GameEvent(id=1, name="NPC", x=5, y=5)
        page = EventPage(trigger=TriggerType.ACTION_BUTTON)

        handler = EventTriggerHandler(event=event, page=page)

        game_state = MockGameState()
        context = TriggerContext(
            game_state=game_state,
            player_position=(5, 4),
            player_direction=2,
            action_button_pressed=False,
        )

        result = handler.check_trigger(context)
        assert result == TriggerResult.NOT_TRIGGERED

    def test_action_button_trigger_wrong_direction(self):
        """Test action button trigger - not facing event"""
        event = GameEvent(id=1, name="NPC", x=5, y=5)
        page = EventPage(trigger=TriggerType.ACTION_BUTTON)

        handler = EventTriggerHandler(event=event, page=page)

        game_state = MockGameState()
        context = TriggerContext(
            game_state=game_state,
            player_position=(5, 4),
            player_direction=8,  # Facing up (away from event)
            action_button_pressed=True,
        )

        result = handler.check_trigger(context)
        assert result == TriggerResult.NOT_TRIGGERED

    def test_player_touch_trigger(self):
        """Test player touch trigger"""
        event = GameEvent(id=1, name="Trap", x=5, y=5)
        page = EventPage(trigger=TriggerType.PLAYER_TOUCH)

        handler = EventTriggerHandler(event=event, page=page)

        game_state = MockGameState()

        # Player not on tile
        context = TriggerContext(
            game_state=game_state, player_position=(5, 4), player_direction=2
        )
        result = handler.check_trigger(context)
        assert result == TriggerResult.NOT_TRIGGERED

        # Player on tile
        context.player_position = (5, 5)
        result = handler.check_trigger(context)
        assert result == TriggerResult.TRIGGERED

    def test_autorun_trigger(self):
        """Test autorun trigger"""
        event = GameEvent(id=1, name="Cutscene", x=5, y=5)
        page = EventPage(trigger=TriggerType.AUTORUN)

        handler = EventTriggerHandler(event=event, page=page)

        game_state = MockGameState()
        context = TriggerContext(
            game_state=game_state, player_position=(0, 0), player_direction=2
        )

        # Autorun always triggers if not active
        result = handler.check_trigger(context)
        assert result == TriggerResult.TRIGGERED

        # Mark as active
        handler.is_active = True
        result = handler.check_trigger(context)
        assert result == TriggerResult.RUNNING

    def test_parallel_trigger(self):
        """Test parallel trigger"""
        event = GameEvent(id=1, name="Timer", x=0, y=0)
        page = EventPage(trigger=TriggerType.PARALLEL)

        handler = EventTriggerHandler(event=event, page=page)

        game_state = MockGameState()
        context = TriggerContext(
            game_state=game_state, player_position=(10, 10), player_direction=2
        )

        # Parallel always triggers
        result = handler.check_trigger(context)
        assert result == TriggerResult.TRIGGERED


class TestEventTriggerManager:
    """Test EventTriggerManager functionality"""

    def test_manager_creation(self):
        """Test creating trigger manager"""
        game_state = MockGameState()
        manager = EventTriggerManager(game_state=game_state)

        assert manager.game_state == game_state
        assert len(manager.events) == 0
        assert len(manager.active_handlers) == 0

    def test_add_remove_event(self):
        """Test adding and removing events"""
        game_state = MockGameState()
        manager = EventTriggerManager(game_state=game_state)

        event = GameEvent(id=1, name="Test", x=5, y=5)
        manager.add_event(event)

        assert 1 in manager.events
        assert manager.events[1] == event

        manager.remove_event(1)
        assert 1 not in manager.events

    def test_update_event_handlers(self):
        """Test updating event handlers based on conditions"""
        game_state = MockGameState()
        manager = EventTriggerManager(game_state=game_state)

        # Create event with two pages
        event = GameEvent(id=1, name="NPC", x=5, y=5)

        # Page 1: No conditions
        page1 = EventPage()
        event.pages.append(page1)

        # Page 2: Requires switch 1
        page2 = EventPage(condition_switch1_valid=True, condition_switch1_id=1)
        event.pages.append(page2)

        manager.add_event(event)
        manager.update_event_handlers()

        # Should have handler for page 1
        assert 1 in manager.active_handlers
        assert manager.active_handlers[1].page == page1

        # Set switch, update handlers
        game_state.set_switch(1, True)
        manager.update_event_handlers()

        # Should now have handler for page 2
        assert manager.active_handlers[1].page == page2

    def test_check_triggers(self):
        """Test checking triggers"""
        game_state = MockGameState()
        manager = EventTriggerManager(game_state=game_state)

        # Create event with action button trigger
        event = GameEvent(id=1, name="NPC", x=5, y=5)
        page = EventPage(trigger=TriggerType.ACTION_BUTTON)
        event.pages.append(page)

        manager.add_event(event)
        manager.update_event_handlers()

        # Create context - player facing event and pressing button
        context = TriggerContext(
            game_state=game_state,
            player_position=(5, 4),
            player_direction=2,
            action_button_pressed=True,
        )

        triggered = manager.check_triggers(context)

        assert len(triggered) == 1
        assert triggered[0][0] == event
        assert triggered[0][1] == page

    def test_start_event_normal(self):
        """Test starting normal event"""
        game_state = MockGameState()
        manager = EventTriggerManager(game_state=game_state)

        event = GameEvent(id=1, name="Test", x=0, y=0)
        page = EventPage(trigger=TriggerType.ACTION_BUTTON)
        page.commands.append(ShowTextCommand("Hello"))

        context = manager.start_event(event, page)

        assert context.event == event
        assert context.page == page
        assert 1 in manager.running_events

    def test_start_event_parallel(self):
        """Test starting parallel event"""
        game_state = MockGameState()
        manager = EventTriggerManager(game_state=game_state)

        event = GameEvent(id=1, name="Timer", x=0, y=0)
        page = EventPage(trigger=TriggerType.PARALLEL)
        page.commands.append(WaitCommand(60))

        context = manager.start_event(event, page)

        assert len(manager.parallel_events) == 1
        assert manager.parallel_events[0] == context

    def test_is_event_running(self):
        """Test checking if event is running"""
        game_state = MockGameState()
        manager = EventTriggerManager(game_state=game_state)

        event = GameEvent(id=1, name="Test", x=0, y=0)
        page = EventPage()

        assert manager.is_event_running(1) is False

        manager.start_event(event, page)
        assert manager.is_event_running(1) is True

    def test_has_blocking_event(self):
        """Test checking for blocking events"""
        game_state = MockGameState()
        manager = EventTriggerManager(game_state=game_state)

        # No events running
        assert manager.has_blocking_event() is False

        # Start normal event
        event1 = GameEvent(id=1, name="Normal", x=0, y=0)
        page1 = EventPage(trigger=TriggerType.ACTION_BUTTON)
        manager.start_event(event1, page1)
        assert manager.has_blocking_event() is False

        # Start autorun event (blocking)
        event2 = GameEvent(id=2, name="Autorun", x=0, y=0)
        page2 = EventPage(trigger=TriggerType.AUTORUN)
        manager.start_event(event2, page2)
        assert manager.has_blocking_event() is True

    def test_clear_all_events(self):
        """Test clearing all events"""
        game_state = MockGameState()
        manager = EventTriggerManager(game_state=game_state)

        # Start some events
        event1 = GameEvent(id=1, name="Test1", x=0, y=0)
        page1 = EventPage()
        manager.add_event(event1)
        manager.update_event_handlers()
        manager.start_event(event1, page1)

        event2 = GameEvent(id=2, name="Test2", x=0, y=0)
        page2 = EventPage(trigger=TriggerType.PARALLEL)
        manager.start_event(event2, page2)

        assert len(manager.running_events) > 0 or len(manager.parallel_events) > 0

        manager.clear_all_events()

        assert len(manager.running_events) == 0
        assert len(manager.parallel_events) == 0

    def test_manager_serialization(self):
        """Test manager to_dict/from_dict"""
        game_state = MockGameState()
        manager = EventTriggerManager(game_state=game_state)

        # Add events
        event1 = GameEvent(id=1, name="NPC1", x=5, y=5)
        page1 = EventPage()
        event1.pages.append(page1)
        manager.add_event(event1)

        event2 = GameEvent(id=2, name="NPC2", x=10, y=10)
        page2 = EventPage()
        event2.pages.append(page2)
        manager.add_event(event2)

        # Serialize
        data = manager.to_dict()
        assert len(data["events"]) == 2

        # Deserialize
        manager2 = EventTriggerManager.from_dict(data, game_state)
        assert len(manager2.events) == 2
        assert 1 in manager2.events
        assert 2 in manager2.events

    def test_manager_json_serialization(self):
        """Test manager to_json/from_json"""
        game_state = MockGameState()
        manager = EventTriggerManager(game_state=game_state)

        event = GameEvent(id=1, name="Test", x=5, y=5)
        page = EventPage()
        page.commands.append(ShowTextCommand("Hello"))
        event.pages.append(page)
        manager.add_event(event)

        # To JSON
        json_str = manager.to_json()
        assert isinstance(json_str, str)
        assert "Test" in json_str

        # From JSON
        manager2 = EventTriggerManager.from_json(json_str, game_state)
        assert len(manager2.events) == 1


class TestTriggerFactories:
    """Test trigger factory functions"""

    def test_create_proximity_trigger(self):
        """Test proximity trigger factory"""
        trigger = create_proximity_trigger(max_distance=3)

        assert trigger.condition_type == "proximity"
        assert trigger.parameters["max_distance"] == 3

    def test_create_switch_trigger(self):
        """Test switch trigger factory"""
        trigger = create_switch_trigger(switch_id=10, value=True)

        assert trigger.condition_type == "switch"
        assert trigger.parameters["switch_id"] == 10
        assert trigger.parameters["value"] is True

    def test_create_variable_trigger(self):
        """Test variable trigger factory"""
        trigger = create_variable_trigger(variable_id=5, operator=">=", value=100)

        assert trigger.condition_type == "variable"
        assert trigger.parameters["variable_id"] == 5
        assert trigger.parameters["operator"] == ">="
        assert trigger.parameters["value"] == 100


class TestEventCallbacks:
    """Test event manager callbacks"""

    def test_on_event_start_callback(self):
        """Test event start callback"""
        game_state = MockGameState()
        manager = EventTriggerManager(game_state=game_state)

        called = []

        def on_start(event, page):
            called.append((event, page))

        manager.on_event_start = on_start

        event = GameEvent(id=1, name="Test", x=0, y=0)
        page = EventPage()

        manager.start_event(event, page)

        assert len(called) == 1
        assert called[0][0] == event
        assert called[0][1] == page
