"""
Comprehensive tests for core Event System.

Tests EventManager, Event, EventType, and event handling mechanisms.
"""

import pytest

from neonworks.core.events import Event, EventManager, EventType, emit_event, get_event_manager


class TestEvent:
    """Test suite for Event class."""

    def test_create_event(self):
        """Test creating an event."""
        event = Event(event_type=EventType.TURN_START)

        assert event is not None
        assert event.event_type == EventType.TURN_START
        assert event.data == {}

    def test_create_event_with_data(self):
        """Test creating an event with data."""
        event_data = {"entity_id": "player_1", "action": "attack"}
        event = Event(event_type=EventType.ACTION_PERFORMED, data=event_data)

        assert event.event_type == EventType.ACTION_PERFORMED
        assert event.data == event_data
        assert event.data["entity_id"] == "player_1"
        assert event.data["action"] == "attack"

    def test_event_data_defaults_to_empty_dict(self):
        """Test that event data defaults to empty dict."""
        event = Event(event_type=EventType.COMBAT_START)

        assert event.data is not None
        assert isinstance(event.data, dict)
        assert len(event.data) == 0

    @pytest.mark.parametrize(
        "event_type",
        [
            EventType.TURN_START,
            EventType.TURN_END,
            EventType.COMBAT_START,
            EventType.COMBAT_END,
            EventType.BUILDING_PLACED,
            EventType.RESOURCE_COLLECTED,
        ],
    )
    def test_various_event_types(self, event_type):
        """Test creating events of various types."""
        event = Event(event_type=event_type)

        assert event.event_type == event_type


class TestEventManager:
    """Test suite for EventManager class."""

    def test_create_event_manager(self):
        """Test creating an event manager."""
        manager = EventManager()

        assert manager is not None

    def test_subscribe_to_event(self):
        """Test subscribing to an event."""
        manager = EventManager()
        handler_called = []

        def handler(event):
            handler_called.append(True)

        manager.subscribe(EventType.TURN_START, handler)

        # Verify subscription registered (handler should be called when event is dispatched)
        event = Event(event_type=EventType.TURN_START)
        manager.emit(event)
        manager.process_events()

        assert len(handler_called) == 1

    def test_subscribe_multiple_handlers(self):
        """Test subscribing multiple handlers to same event."""
        manager = EventManager()
        handler1_called = []
        handler2_called = []

        def handler1(event):
            handler1_called.append(True)

        def handler2(event):
            handler2_called.append(True)

        manager.subscribe(EventType.TURN_START, handler1)
        manager.subscribe(EventType.TURN_START, handler2)

        event = Event(event_type=EventType.TURN_START)
        manager.emit(event)
        manager.process_events()

        assert len(handler1_called) == 1
        assert len(handler2_called) == 1

    def test_unsubscribe_from_event(self):
        """Test unsubscribing from an event."""
        manager = EventManager()
        handler_called = []

        def handler(event):
            handler_called.append(True)

        manager.subscribe(EventType.TURN_START, handler)
        manager.unsubscribe(EventType.TURN_START, handler)

        event = Event(event_type=EventType.TURN_START)
        manager.emit(event)
        manager.process_events()

        # Handler should not be called after unsubscribe
        assert len(handler_called) == 0

    def test_unsubscribe_nonexistent_handler(self):
        """Test unsubscribing a handler that was never subscribed (should not error)."""
        manager = EventManager()

        def handler(event):
            pass

        # Should not raise an error
        manager.unsubscribe(EventType.TURN_START, handler)

    def test_emit_event(self):
        """Test emitting an event."""
        manager = EventManager()
        received_events = []

        def handler(event):
            received_events.append(event)

        manager.subscribe(EventType.COMBAT_START, handler)

        event = Event(event_type=EventType.COMBAT_START, data={"combatants": 4})
        manager.emit(event)
        manager.process_events()

        assert len(received_events) == 1
        assert received_events[0].event_type == EventType.COMBAT_START
        assert received_events[0].data["combatants"] == 4

    def test_emit_immediate(self):
        """Test emitting an event immediately (bypassing queue)."""
        manager = EventManager()
        received_events = []

        def handler(event):
            received_events.append(event)

        manager.subscribe(EventType.COMBAT_START, handler)

        event = Event(event_type=EventType.COMBAT_START)
        manager.emit_immediate(event)

        # Should be processed immediately, before process_events
        assert len(received_events) == 1

    def test_queued_vs_immediate_mode(self):
        """Test queued mode vs immediate mode."""
        manager = EventManager()
        received_events = []

        def handler(event):
            received_events.append(event)

        manager.subscribe(EventType.TURN_START, handler)

        # Queued mode (default)
        manager.set_immediate_mode(False)
        event1 = Event(event_type=EventType.TURN_START)
        manager.emit(event1)
        assert len(received_events) == 0  # Not processed yet

        manager.process_events()
        assert len(received_events) == 1  # Now processed

        # Immediate mode
        manager.set_immediate_mode(True)
        event2 = Event(event_type=EventType.TURN_START)
        manager.emit(event2)
        assert len(received_events) == 2  # Processed immediately

    def test_process_multiple_events(self):
        """Test processing multiple queued events."""
        manager = EventManager()
        received_events = []

        def handler(event):
            received_events.append(event)

        manager.subscribe(EventType.TURN_START, handler)

        # Emit multiple events
        for i in range(5):
            event = Event(event_type=EventType.TURN_START, data={"turn": i})
            manager.emit(event)

        # Process all at once
        manager.process_events()

        assert len(received_events) == 5
        assert received_events[0].data["turn"] == 0
        assert received_events[4].data["turn"] == 4

    def test_clear_queue(self):
        """Test clearing the event queue."""
        manager = EventManager()
        received_events = []

        def handler(event):
            received_events.append(event)

        manager.subscribe(EventType.TURN_START, handler)

        # Emit events
        for i in range(3):
            event = Event(event_type=EventType.TURN_START)
            manager.emit(event)

        # Clear queue before processing
        manager.clear_queue()
        manager.process_events()

        # No events should be processed
        assert len(received_events) == 0

    def test_clear_handlers(self):
        """Test clearing all event handlers."""
        manager = EventManager()
        received_events = []

        def handler(event):
            received_events.append(event)

        manager.subscribe(EventType.TURN_START, handler)
        manager.subscribe(EventType.COMBAT_START, handler)

        # Clear all handlers
        manager.clear_handlers()

        # Emit events
        event1 = Event(event_type=EventType.TURN_START)
        event2 = Event(event_type=EventType.COMBAT_START)
        manager.emit(event1)
        manager.emit(event2)
        manager.process_events()

        # No handlers should be called
        assert len(received_events) == 0

    def test_handler_receives_event_data(self):
        """Test that handlers receive event data correctly."""
        manager = EventManager()
        received_data = []

        def handler(event):
            received_data.append(event.data)

        manager.subscribe(EventType.DAMAGE_DEALT, handler)

        event = Event(
            event_type=EventType.DAMAGE_DEALT,
            data={"attacker": "player", "target": "enemy", "damage": 25},
        )
        manager.emit(event)
        manager.process_events()

        assert len(received_data) == 1
        assert received_data[0]["attacker"] == "player"
        assert received_data[0]["target"] == "enemy"
        assert received_data[0]["damage"] == 25

    def test_multiple_event_types(self):
        """Test handling multiple different event types."""
        manager = EventManager()
        turn_events = []
        combat_events = []

        def turn_handler(event):
            turn_events.append(event)

        def combat_handler(event):
            combat_events.append(event)

        manager.subscribe(EventType.TURN_START, turn_handler)
        manager.subscribe(EventType.COMBAT_START, combat_handler)

        # Emit different event types
        manager.emit(Event(event_type=EventType.TURN_START))
        manager.emit(Event(event_type=EventType.COMBAT_START))
        manager.emit(Event(event_type=EventType.TURN_START))
        manager.process_events()

        assert len(turn_events) == 2
        assert len(combat_events) == 1

    def test_handler_error_handling(self):
        """Test that errors in handlers don't crash the system."""
        manager = EventManager()
        handler1_called = []
        handler2_called = []

        def failing_handler(event):
            raise ValueError("Test error")

        def working_handler(event):
            handler1_called.append(True)

        def another_working_handler(event):
            handler2_called.append(True)

        # Subscribe handlers (failing one in the middle)
        manager.subscribe(EventType.TURN_START, working_handler)
        manager.subscribe(EventType.TURN_START, failing_handler)
        manager.subscribe(EventType.TURN_START, another_working_handler)

        # Emit event
        event = Event(event_type=EventType.TURN_START)
        manager.emit(event)
        manager.process_events()

        # Both working handlers should still be called
        assert len(handler1_called) == 1
        assert len(handler2_called) == 1

    def test_event_order_preservation(self):
        """Test that events are processed in the order they were emitted."""
        manager = EventManager()
        received_order = []

        def handler(event):
            received_order.append(event.data["order"])

        manager.subscribe(EventType.CUSTOM, handler)

        # Emit events in specific order
        for i in range(10):
            manager.emit(Event(event_type=EventType.CUSTOM, data={"order": i}))

        manager.process_events()

        # Verify order
        assert received_order == list(range(10))


class TestEventTypes:
    """Test suite for EventType enum."""

    def test_turn_based_events(self):
        """Test turn-based event types exist."""
        assert EventType.TURN_START
        assert EventType.TURN_END
        assert EventType.ACTION_PERFORMED

    def test_combat_events(self):
        """Test combat event types exist."""
        assert EventType.COMBAT_START
        assert EventType.COMBAT_END
        assert EventType.DAMAGE_DEALT
        assert EventType.UNIT_DIED

    def test_building_events(self):
        """Test building event types exist."""
        assert EventType.BUILDING_PLACED
        assert EventType.BUILDING_COMPLETED
        assert EventType.BUILDING_UPGRADED
        assert EventType.BUILDING_DESTROYED

    def test_survival_events(self):
        """Test survival event types exist."""
        assert EventType.HUNGER_CRITICAL
        assert EventType.THIRST_CRITICAL
        assert EventType.ENERGY_DEPLETED

    def test_resource_events(self):
        """Test resource event types exist."""
        assert EventType.RESOURCE_COLLECTED
        assert EventType.RESOURCE_CONSUMED
        assert EventType.RESOURCE_DEPLETED

    def test_ui_events(self):
        """Test UI event types exist."""
        assert EventType.UI_BUTTON_CLICKED
        assert EventType.UI_TILE_SELECTED
        assert EventType.UI_ENTITY_SELECTED

    def test_game_state_events(self):
        """Test game state event types exist."""
        assert EventType.GAME_PAUSED
        assert EventType.GAME_RESUMED
        assert EventType.GAME_SAVED
        assert EventType.GAME_LOADED


class TestGlobalEventManager:
    """Test suite for global event manager functions."""

    def test_get_event_manager(self):
        """Test getting global event manager instance."""
        manager = get_event_manager()

        assert manager is not None
        assert isinstance(manager, EventManager)

    def test_get_event_manager_singleton(self):
        """Test that get_event_manager returns same instance."""
        manager1 = get_event_manager()
        manager2 = get_event_manager()

        assert manager1 is manager2

    def test_emit_event_convenience_function(self):
        """Test emit_event convenience function."""
        manager = get_event_manager()
        received_events = []

        def handler(event):
            received_events.append(event)

        manager.subscribe(EventType.TURN_START, handler)

        # Use convenience function
        emit_event(EventType.TURN_START, {"turn_number": 1})
        manager.process_events()

        assert len(received_events) == 1
        assert received_events[0].event_type == EventType.TURN_START
        assert received_events[0].data["turn_number"] == 1


class TestEventScenarios:
    """Test realistic event usage scenarios."""

    def test_turn_based_combat_scenario(self):
        """Test a complete turn-based combat scenario."""
        manager = EventManager()
        combat_log = []

        def log_handler(event):
            combat_log.append(
                {
                    "type": event.event_type,
                    "data": event.data,
                }
            )

        # Subscribe to relevant events
        manager.subscribe(EventType.COMBAT_START, log_handler)
        manager.subscribe(EventType.TURN_START, log_handler)
        manager.subscribe(EventType.DAMAGE_DEALT, log_handler)
        manager.subscribe(EventType.UNIT_DIED, log_handler)
        manager.subscribe(EventType.COMBAT_END, log_handler)

        # Simulate combat sequence
        manager.emit(Event(EventType.COMBAT_START, {"combatants": ["player", "enemy"]}))
        manager.emit(Event(EventType.TURN_START, {"actor": "player"}))
        manager.emit(
            Event(EventType.DAMAGE_DEALT, {"attacker": "player", "target": "enemy", "damage": 25})
        )
        manager.emit(Event(EventType.TURN_START, {"actor": "enemy"}))
        manager.emit(
            Event(EventType.DAMAGE_DEALT, {"attacker": "enemy", "target": "player", "damage": 15})
        )
        manager.emit(Event(EventType.UNIT_DIED, {"unit": "enemy"}))
        manager.emit(Event(EventType.COMBAT_END, {"winner": "player"}))

        manager.process_events()

        assert len(combat_log) == 7
        assert combat_log[0]["type"] == EventType.COMBAT_START
        assert combat_log[-1]["type"] == EventType.COMBAT_END
        assert combat_log[-1]["data"]["winner"] == "player"

    def test_building_construction_scenario(self):
        """Test a building construction scenario."""
        manager = EventManager()
        building_events = []

        def building_handler(event):
            building_events.append(event)

        manager.subscribe(EventType.BUILDING_PLACED, building_handler)
        manager.subscribe(EventType.BUILDING_COMPLETED, building_handler)
        manager.subscribe(EventType.BUILDING_UPGRADED, building_handler)

        # Simulate building lifecycle
        manager.emit(Event(EventType.BUILDING_PLACED, {"type": "house", "position": (10, 10)}))
        manager.emit(Event(EventType.BUILDING_COMPLETED, {"type": "house", "id": "house_1"}))
        manager.emit(Event(EventType.BUILDING_UPGRADED, {"id": "house_1", "level": 2}))

        manager.process_events()

        assert len(building_events) == 3
        assert building_events[0].event_type == EventType.BUILDING_PLACED
        assert building_events[1].event_type == EventType.BUILDING_COMPLETED
        assert building_events[2].event_type == EventType.BUILDING_UPGRADED

    def test_resource_management_scenario(self):
        """Test a resource management scenario."""
        manager = EventManager()
        resource_balance = {"wood": 0, "stone": 0}

        def resource_collected_handler(event):
            resource_type = event.data["type"]
            amount = event.data["amount"]
            resource_balance[resource_type] += amount

        def resource_consumed_handler(event):
            resource_type = event.data["type"]
            amount = event.data["amount"]
            resource_balance[resource_type] -= amount

        manager.subscribe(EventType.RESOURCE_COLLECTED, resource_collected_handler)
        manager.subscribe(EventType.RESOURCE_CONSUMED, resource_consumed_handler)

        # Simulate resource collection and consumption
        manager.emit(Event(EventType.RESOURCE_COLLECTED, {"type": "wood", "amount": 50}))
        manager.emit(Event(EventType.RESOURCE_COLLECTED, {"type": "stone", "amount": 30}))
        manager.emit(Event(EventType.RESOURCE_CONSUMED, {"type": "wood", "amount": 20}))
        manager.emit(Event(EventType.RESOURCE_COLLECTED, {"type": "wood", "amount": 10}))
        manager.emit(Event(EventType.RESOURCE_CONSUMED, {"type": "stone", "amount": 15}))

        manager.process_events()

        assert resource_balance["wood"] == 40  # 50 + 10 - 20
        assert resource_balance["stone"] == 15  # 30 - 15
