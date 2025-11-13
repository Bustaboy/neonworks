"""
Event Trigger System

Handles detection and triggering of game events based on various conditions
such as player proximity, button presses, and automatic triggers.
"""

from typing import Dict, List, Optional, Set, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import json

from core.event_commands import (
    GameEvent, EventPage, TriggerType, EventContext,
    GameState
)


class TriggerResult(Enum):
    """Result of trigger check"""
    NOT_TRIGGERED = 0  # Event not triggered
    TRIGGERED = 1      # Event triggered
    RUNNING = 2        # Event already running
    BLOCKED = 3        # Event blocked by conditions


@dataclass
class TriggerCondition:
    """
    Defines a condition that must be met for a trigger to activate.
    """
    condition_type: str  # "proximity", "facing", "switch", "variable", "timer"
    parameters: Dict[str, any] = field(default_factory=dict)

    def evaluate(self, context: 'TriggerContext') -> bool:
        """
        Evaluate if this condition is met.

        Args:
            context: Current trigger context

        Returns:
            True if condition is met
        """
        if self.condition_type == "proximity":
            return self._check_proximity(context)
        elif self.condition_type == "facing":
            return self._check_facing(context)
        elif self.condition_type == "switch":
            return self._check_switch(context)
        elif self.condition_type == "variable":
            return self._check_variable(context)
        elif self.condition_type == "timer":
            return self._check_timer(context)
        else:
            return True

    def _check_proximity(self, context: 'TriggerContext') -> bool:
        """Check if player is within range"""
        max_distance = self.parameters.get("max_distance", 1)
        event_pos = self.parameters.get("event_pos", (0, 0))
        player_pos = context.player_position

        dx = abs(player_pos[0] - event_pos[0])
        dy = abs(player_pos[1] - event_pos[1])
        return dx <= max_distance and dy <= max_distance

    def _check_facing(self, context: 'TriggerContext') -> bool:
        """Check if player is facing the event"""
        required_direction = self.parameters.get("direction")
        return context.player_direction == required_direction

    def _check_switch(self, context: 'TriggerContext') -> bool:
        """Check switch state"""
        switch_id = self.parameters.get("switch_id")
        required_value = self.parameters.get("value", True)
        return context.game_state.get_switch(switch_id) == required_value

    def _check_variable(self, context: 'TriggerContext') -> bool:
        """Check variable value"""
        variable_id = self.parameters.get("variable_id")
        operator = self.parameters.get("operator", ">=")
        value = self.parameters.get("value", 0)

        var_value = context.game_state.get_variable(variable_id)

        if operator == "==":
            return var_value == value
        elif operator == "!=":
            return var_value != value
        elif operator == ">":
            return var_value > value
        elif operator == ">=":
            return var_value >= value
        elif operator == "<":
            return var_value < value
        elif operator == "<=":
            return var_value <= value
        return False

    def _check_timer(self, context: 'TriggerContext') -> bool:
        """Check timer value"""
        # Implementation depends on game timer system
        return True

    def to_dict(self) -> Dict[str, any]:
        """Serialize to dictionary"""
        return {
            "condition_type": self.condition_type,
            "parameters": self.parameters
        }

    @classmethod
    def from_dict(cls, data: Dict[str, any]) -> 'TriggerCondition':
        """Deserialize from dictionary"""
        return cls(
            condition_type=data["condition_type"],
            parameters=data.get("parameters", {})
        )


@dataclass
class TriggerContext:
    """
    Context information for trigger evaluation.

    Contains current game state, player position, and other relevant data
    needed to evaluate trigger conditions.
    """
    game_state: GameState
    player_position: Tuple[int, int]
    player_direction: int  # 2=down, 4=left, 6=right, 8=up
    action_button_pressed: bool = False
    current_map_id: int = 0
    delta_time: float = 0.0

    # Cache for event positions to avoid repeated lookups
    _event_positions: Dict[int, Tuple[int, int]] = field(default_factory=dict)

    def get_event_position(self, event_id: int) -> Optional[Tuple[int, int]]:
        """Get cached event position"""
        return self._event_positions.get(event_id)

    def set_event_position(self, event_id: int, position: Tuple[int, int]):
        """Cache event position"""
        self._event_positions[event_id] = position

    def distance_to_event(self, event_pos: Tuple[int, int]) -> float:
        """Calculate distance from player to event"""
        dx = self.player_position[0] - event_pos[0]
        dy = self.player_position[1] - event_pos[1]
        return (dx * dx + dy * dy) ** 0.5

    def is_adjacent_to(self, event_pos: Tuple[int, int]) -> bool:
        """Check if player is adjacent to event (including diagonal)"""
        return self.distance_to_event(event_pos) <= 1.5

    def is_in_front_of(self, event_pos: Tuple[int, int]) -> bool:
        """Check if event is directly in front of player"""
        px, py = self.player_position
        ex, ey = event_pos

        # Check based on player direction
        if self.player_direction == 2:  # Down
            return px == ex and ey == py + 1
        elif self.player_direction == 4:  # Left
            return py == ey and ex == px - 1
        elif self.player_direction == 6:  # Right
            return py == ey and ex == px + 1
        elif self.player_direction == 8:  # Up
            return px == ex and ey == py - 1
        return False


@dataclass
class EventTriggerHandler:
    """
    Manages event triggering logic for different trigger types.
    """
    event: GameEvent
    page: EventPage
    is_active: bool = False
    parallel_index: int = 0  # For parallel events

    def check_trigger(self, context: TriggerContext) -> TriggerResult:
        """
        Check if this event should be triggered.

        Args:
            context: Current trigger context

        Returns:
            TriggerResult indicating trigger status
        """
        if not self.page:
            return TriggerResult.NOT_TRIGGERED

        # Get event position
        event_pos = (self.event.x, self.event.y)
        context.set_event_position(self.event.id, event_pos)

        # Check based on trigger type
        if self.page.trigger == TriggerType.ACTION_BUTTON:
            return self._check_action_button(context, event_pos)
        elif self.page.trigger == TriggerType.PLAYER_TOUCH:
            return self._check_player_touch(context, event_pos)
        elif self.page.trigger == TriggerType.EVENT_TOUCH:
            return self._check_event_touch(context, event_pos)
        elif self.page.trigger == TriggerType.AUTORUN:
            return self._check_autorun(context)
        elif self.page.trigger == TriggerType.PARALLEL:
            return self._check_parallel(context)

        return TriggerResult.NOT_TRIGGERED

    def _check_action_button(self, context: TriggerContext,
                            event_pos: Tuple[int, int]) -> TriggerResult:
        """Check action button trigger"""
        # Must press action button while facing event
        if not context.action_button_pressed:
            return TriggerResult.NOT_TRIGGERED

        # Check if player is adjacent and facing event
        if not context.is_in_front_of(event_pos):
            return TriggerResult.NOT_TRIGGERED

        if self.is_active:
            return TriggerResult.RUNNING

        return TriggerResult.TRIGGERED

    def _check_player_touch(self, context: TriggerContext,
                           event_pos: Tuple[int, int]) -> TriggerResult:
        """Check player touch trigger"""
        # Trigger when player steps on event tile
        if context.player_position != event_pos:
            return TriggerResult.NOT_TRIGGERED

        if self.is_active:
            return TriggerResult.RUNNING

        return TriggerResult.TRIGGERED

    def _check_event_touch(self, context: TriggerContext,
                          event_pos: Tuple[int, int]) -> TriggerResult:
        """Check event touch trigger"""
        # Event moves toward player and triggers on touch
        # This requires event movement logic which would be in a separate system
        if not context.is_adjacent_to(event_pos):
            return TriggerResult.NOT_TRIGGERED

        if self.is_active:
            return TriggerResult.RUNNING

        return TriggerResult.TRIGGERED

    def _check_autorun(self, context: TriggerContext) -> TriggerResult:
        """Check autorun trigger"""
        # Autoruns are always active if page conditions are met
        # They block player input until complete
        if self.is_active:
            return TriggerResult.RUNNING

        return TriggerResult.TRIGGERED

    def _check_parallel(self, context: TriggerContext) -> TriggerResult:
        """Check parallel trigger"""
        # Parallel events always run in the background
        # They don't block player input
        return TriggerResult.TRIGGERED


@dataclass
class EventTriggerManager:
    """
    Manages all event triggers in the game.

    Handles trigger detection, event activation, and event execution.
    """
    game_state: GameState
    events: Dict[int, GameEvent] = field(default_factory=dict)
    active_handlers: Dict[int, EventTriggerHandler] = field(default_factory=dict)
    running_events: Dict[int, EventContext] = field(default_factory=dict)
    parallel_events: List[EventContext] = field(default_factory=list)

    # Event callbacks
    on_event_start: Optional[Callable[[GameEvent, EventPage], None]] = None
    on_event_end: Optional[Callable[[GameEvent], None]] = None
    on_command_execute: Optional[Callable[[EventContext], None]] = None

    def add_event(self, event: GameEvent):
        """Add an event to the manager"""
        self.events[event.id] = event

    def remove_event(self, event_id: int):
        """Remove an event from the manager"""
        if event_id in self.events:
            del self.events[event_id]
        if event_id in self.active_handlers:
            del self.active_handlers[event_id]
        if event_id in self.running_events:
            del self.running_events[event_id]

    def update_event_handlers(self):
        """
        Update event handlers based on current page conditions.

        This should be called when game state changes (switches, variables, etc.)
        """
        for event in self.events.values():
            active_page = event.get_active_page(self.game_state)

            if active_page:
                if event.id not in self.active_handlers:
                    self.active_handlers[event.id] = EventTriggerHandler(
                        event=event,
                        page=active_page
                    )
                else:
                    # Update page if it changed
                    handler = self.active_handlers[event.id]
                    if handler.page != active_page:
                        handler.page = active_page
                        handler.is_active = False
            else:
                # No active page, remove handler
                if event.id in self.active_handlers:
                    del self.active_handlers[event.id]

    def check_triggers(self, context: TriggerContext) -> List[Tuple[GameEvent, EventPage]]:
        """
        Check all event triggers and return triggered events.

        Args:
            context: Current trigger context

        Returns:
            List of (event, page) tuples that were triggered
        """
        triggered_events = []

        for handler in self.active_handlers.values():
            result = handler.check_trigger(context)

            if result == TriggerResult.TRIGGERED:
                triggered_events.append((handler.event, handler.page))
                handler.is_active = True

        return triggered_events

    def start_event(self, event: GameEvent, page: EventPage) -> EventContext:
        """
        Start executing an event.

        Args:
            event: Event to start
            page: Active page to execute

        Returns:
            EventContext for the running event
        """
        context = EventContext(event=event, page=page)

        # Handle based on trigger type
        if page.trigger == TriggerType.PARALLEL:
            self.parallel_events.append(context)
        else:
            self.running_events[event.id] = context

        # Call callback
        if self.on_event_start:
            self.on_event_start(event, page)

        return context

    def update(self, delta_time: float):
        """
        Update all running events.

        Args:
            delta_time: Time since last update in seconds
        """
        # Update non-parallel events
        finished_events = []
        for event_id, context in self.running_events.items():
            if self._update_event_context(context, delta_time):
                finished_events.append(event_id)

        # Remove finished events
        for event_id in finished_events:
            self._finish_event(event_id)

        # Update parallel events
        finished_parallel = []
        for i, context in enumerate(self.parallel_events):
            if self._update_event_context(context, delta_time):
                finished_parallel.append(i)

        # Remove finished parallel events (reverse order to maintain indices)
        for i in reversed(finished_parallel):
            self.parallel_events.pop(i)

    def _update_event_context(self, context: EventContext, delta_time: float) -> bool:
        """
        Update a single event context.

        Args:
            context: Event context to update
            delta_time: Time since last update

        Returns:
            True if event finished
        """
        # Handle wait
        if context.wait_count > 0:
            context.wait_count -= 1
            return False

        # Get current command
        command = context.get_current_command()
        if not command:
            return True  # Event finished

        # Execute command
        if command.execute(context):
            # Command completed
            context.advance()

            # Call callback
            if self.on_command_execute:
                self.on_command_execute(context)

        return context.is_finished()

    def _finish_event(self, event_id: int):
        """Clean up finished event"""
        if event_id in self.running_events:
            event = self.running_events[event_id].event
            del self.running_events[event_id]

            # Mark handler as inactive
            if event_id in self.active_handlers:
                self.active_handlers[event_id].is_active = False

            # Call callback
            if self.on_event_end:
                self.on_event_end(event)

    def is_event_running(self, event_id: int) -> bool:
        """Check if an event is currently running"""
        return event_id in self.running_events

    def has_blocking_event(self) -> bool:
        """Check if there's a blocking event running (autorun)"""
        for context in self.running_events.values():
            if context.page.trigger == TriggerType.AUTORUN:
                return True
        return False

    def clear_all_events(self):
        """Clear all running events"""
        self.running_events.clear()
        self.parallel_events.clear()
        for handler in self.active_handlers.values():
            handler.is_active = False

    def to_dict(self) -> Dict[str, any]:
        """Serialize manager state to dictionary"""
        return {
            "events": {
                event_id: event.to_dict()
                for event_id, event in self.events.items()
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, any], game_state: GameState) -> 'EventTriggerManager':
        """Deserialize manager state from dictionary"""
        manager = cls(game_state=game_state)

        for event_id, event_data in data.get("events", {}).items():
            event = GameEvent.from_dict(event_data)
            manager.add_event(event)

        manager.update_event_handlers()
        return manager

    def to_json(self) -> str:
        """Serialize to JSON string"""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str, game_state: GameState) -> 'EventTriggerManager':
        """Deserialize from JSON string"""
        return cls.from_dict(json.loads(json_str), game_state)


def create_proximity_trigger(max_distance: int = 1) -> TriggerCondition:
    """Create a proximity-based trigger condition"""
    return TriggerCondition(
        condition_type="proximity",
        parameters={"max_distance": max_distance}
    )


def create_switch_trigger(switch_id: int, value: bool = True) -> TriggerCondition:
    """Create a switch-based trigger condition"""
    return TriggerCondition(
        condition_type="switch",
        parameters={"switch_id": switch_id, "value": value}
    )


def create_variable_trigger(variable_id: int, operator: str, value: int) -> TriggerCondition:
    """Create a variable comparison trigger condition"""
    return TriggerCondition(
        condition_type="variable",
        parameters={
            "variable_id": variable_id,
            "operator": operator,
            "value": value
        }
    )
