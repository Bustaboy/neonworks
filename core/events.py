"""
Event System

Decoupled communication system for game events.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable, Dict, List


class EventType(Enum):
    """Common event types"""

    # Turn-based events
    TURN_START = auto()
    TURN_END = auto()
    ACTION_PERFORMED = auto()

    # Combat events
    COMBAT_START = auto()
    COMBAT_END = auto()
    DAMAGE_DEALT = auto()
    UNIT_DIED = auto()

    # Base building events
    BUILDING_PLACED = auto()
    BUILDING_COMPLETED = auto()
    BUILDING_UPGRADED = auto()
    BUILDING_DESTROYED = auto()

    # Survival events
    HUNGER_CRITICAL = auto()
    THIRST_CRITICAL = auto()
    ENERGY_DEPLETED = auto()

    # Resource events
    RESOURCE_COLLECTED = auto()
    RESOURCE_CONSUMED = auto()
    RESOURCE_DEPLETED = auto()

    # UI events
    UI_BUTTON_CLICKED = auto()
    UI_TILE_SELECTED = auto()
    UI_ENTITY_SELECTED = auto()

    # Editor events
    EDITOR_MODE_CHANGED = auto()
    LEVEL_LOADED = auto()
    LEVEL_SAVED = auto()
    NAVMESH_GENERATED = auto()

    # Game state events
    GAME_PAUSED = auto()
    GAME_RESUMED = auto()
    GAME_SAVED = auto()
    GAME_LOADED = auto()

    # Custom/Generic events
    CUSTOM = auto()  # For custom game-specific events with data in event.data


@dataclass
class Event:
    """Base event class"""

    event_type: EventType
    data: Dict[str, Any] = None

    def __post_init__(self):
        if self.data is None:
            self.data = {}


# Type alias for event handlers
EventHandler = Callable[[Event], None]


class EventManager:
    """Manages event subscriptions and dispatching"""

    def __init__(self):
        self._handlers: Dict[EventType, List[EventHandler]] = {}
        self._event_queue: List[Event] = []
        self._immediate_mode = False

    def subscribe(self, event_type: EventType, handler: EventHandler) -> "EventManager":
        """Subscribe to an event type"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        return self

    def unsubscribe(
        self, event_type: EventType, handler: EventHandler
    ) -> "EventManager":
        """Unsubscribe from an event type"""
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
            except ValueError:
                pass
        return self

    def emit(self, event: Event):
        """Emit an event"""
        if self._immediate_mode:
            self._dispatch(event)
        else:
            self._event_queue.append(event)

    def emit_immediate(self, event: Event):
        """Emit an event immediately, bypassing the queue"""
        self._dispatch(event)

    def _dispatch(self, event: Event):
        """Dispatch an event to all subscribers"""
        if event.event_type in self._handlers:
            for handler in self._handlers[event.event_type]:
                try:
                    handler(event)
                except Exception as e:
                    print(f"Error in event handler: {e}")

    def process_events(self):
        """Process all queued events"""
        events = self._event_queue[:]
        self._event_queue.clear()

        for event in events:
            self._dispatch(event)

    def set_immediate_mode(self, immediate: bool):
        """Set whether events are dispatched immediately or queued"""
        self._immediate_mode = immediate

    def clear_queue(self):
        """Clear all queued events"""
        self._event_queue.clear()

    def clear_handlers(self):
        """Remove all event handlers"""
        self._handlers.clear()


# Global event manager instance
_global_event_manager = None


def get_event_manager() -> EventManager:
    """Get the global event manager instance"""
    global _global_event_manager
    if _global_event_manager is None:
        _global_event_manager = EventManager()
    return _global_event_manager


def emit_event(event_type: EventType, data: Dict[str, Any] = None):
    """Convenience function to emit an event"""
    get_event_manager().emit(Event(event_type, data))
