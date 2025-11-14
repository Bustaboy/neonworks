"""
Event Data Structures

Data classes and utilities for game events, including serialization/deserialization.
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class EventTrigger(Enum):
    """Event trigger types."""

    ACTION_BUTTON = "action_button"  # Player presses action button
    PLAYER_TOUCH = "player_touch"  # Player touches event
    EVENT_TOUCH = "event_touch"  # Another event touches this event
    AUTORUN = "autorun"  # Runs automatically when map loads
    PARALLEL = "parallel"  # Runs in parallel with other events


class EventPriority(Enum):
    """Event rendering priority."""

    BELOW_PLAYER = 0  # Render below player
    SAME_AS_PLAYER = 1  # Render at same level as player
    ABOVE_PLAYER = 2  # Render above player


@dataclass
class EventGraphic:
    """Event graphic/sprite information."""

    character_name: str = ""  # Sprite filename
    character_index: int = 0  # Index in character sheet
    direction: int = 2  # 2=down, 4=left, 6=right, 8=up
    pattern: int = 0  # Animation pattern (0-2)
    tile_id: int = 0  # Alternative: use tile from tileset
    opacity: int = 255  # 0-255
    blend_type: int = 0  # 0=normal, 1=add, 2=subtract


@dataclass
class EventPage:
    """
    A single page of an event.

    Events can have multiple pages with different conditions.
    Only the first page with satisfied conditions will be active.
    """

    # Conditions
    switch1_valid: bool = False
    switch1_id: int = 1
    switch2_valid: bool = False
    switch2_id: int = 1
    variable_valid: bool = False
    variable_id: int = 1
    variable_value: int = 0
    self_switch_valid: bool = False
    self_switch_ch: str = "A"

    # Graphic
    graphic: EventGraphic = field(default_factory=EventGraphic)

    # Movement
    move_type: int = 0  # 0=fixed, 1=random, 2=approach, 3=custom
    move_speed: int = 3  # 1=slowest, 6=fastest
    move_frequency: int = 3  # 1=lowest, 5=highest
    move_route: Optional[Dict[str, Any]] = None
    walk_anime: bool = True  # Walking animation
    step_anime: bool = False  # Stepping animation
    direction_fix: bool = False  # Fix direction
    through: bool = False  # Can pass through
    always_on_top: bool = False  # Always on top priority

    # Options
    trigger: EventTrigger = EventTrigger.ACTION_BUTTON
    priority: EventPriority = EventPriority.BELOW_PLAYER

    # Commands (list of event commands)
    commands: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "conditions": {
                "switch1_valid": self.switch1_valid,
                "switch1_id": self.switch1_id,
                "switch2_valid": self.switch2_valid,
                "switch2_id": self.switch2_id,
                "variable_valid": self.variable_valid,
                "variable_id": self.variable_id,
                "variable_value": self.variable_value,
                "self_switch_valid": self.self_switch_valid,
                "self_switch_ch": self.self_switch_ch,
            },
            "graphic": {
                "character_name": self.graphic.character_name,
                "character_index": self.graphic.character_index,
                "direction": self.graphic.direction,
                "pattern": self.graphic.pattern,
                "tile_id": self.graphic.tile_id,
                "opacity": self.graphic.opacity,
                "blend_type": self.graphic.blend_type,
            },
            "movement": {
                "move_type": self.move_type,
                "move_speed": self.move_speed,
                "move_frequency": self.move_frequency,
                "move_route": self.move_route,
                "walk_anime": self.walk_anime,
                "step_anime": self.step_anime,
                "direction_fix": self.direction_fix,
                "through": self.through,
                "always_on_top": self.always_on_top,
            },
            "options": {
                "trigger": self.trigger.value,
                "priority": self.priority.value,
            },
            "commands": self.commands,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EventPage":
        """Create EventPage from dictionary."""
        page = cls()

        # Conditions
        if "conditions" in data:
            cond = data["conditions"]
            page.switch1_valid = cond.get("switch1_valid", False)
            page.switch1_id = cond.get("switch1_id", 1)
            page.switch2_valid = cond.get("switch2_valid", False)
            page.switch2_id = cond.get("switch2_id", 1)
            page.variable_valid = cond.get("variable_valid", False)
            page.variable_id = cond.get("variable_id", 1)
            page.variable_value = cond.get("variable_value", 0)
            page.self_switch_valid = cond.get("self_switch_valid", False)
            page.self_switch_ch = cond.get("self_switch_ch", "A")

        # Graphic
        if "graphic" in data:
            gfx = data["graphic"]
            page.graphic = EventGraphic(
                character_name=gfx.get("character_name", ""),
                character_index=gfx.get("character_index", 0),
                direction=gfx.get("direction", 2),
                pattern=gfx.get("pattern", 0),
                tile_id=gfx.get("tile_id", 0),
                opacity=gfx.get("opacity", 255),
                blend_type=gfx.get("blend_type", 0),
            )

        # Movement
        if "movement" in data:
            mov = data["movement"]
            page.move_type = mov.get("move_type", 0)
            page.move_speed = mov.get("move_speed", 3)
            page.move_frequency = mov.get("move_frequency", 3)
            page.move_route = mov.get("move_route")
            page.walk_anime = mov.get("walk_anime", True)
            page.step_anime = mov.get("step_anime", False)
            page.direction_fix = mov.get("direction_fix", False)
            page.through = mov.get("through", False)
            page.always_on_top = mov.get("always_on_top", False)

        # Options
        if "options" in data:
            opts = data["options"]
            page.trigger = EventTrigger(opts.get("trigger", "action_button"))
            page.priority = EventPriority(opts.get("priority", 0))

        # Commands
        page.commands = data.get("commands", [])

        return page


@dataclass
class GameEvent:
    """A complete game event with metadata and pages."""

    id: int = 0
    name: str = "Event"
    x: int = 0
    y: int = 0
    pages: List[EventPage] = field(default_factory=lambda: [EventPage()])

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "pages": [page.to_dict() for page in self.pages],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GameEvent":
        """Create GameEvent from dictionary."""
        pages = [EventPage.from_dict(p) for p in data.get("pages", [])]
        if not pages:
            pages = [EventPage()]

        return cls(
            id=data.get("id", 0),
            name=data.get("name", "Event"),
            x=data.get("x", 0),
            y=data.get("y", 0),
            pages=pages,
        )

    def get_active_page(
        self, switches: Dict[int, bool], variables: Dict[int, int], self_switches: Dict[str, bool]
    ) -> Optional[EventPage]:
        """
        Get the currently active page based on conditions.

        Args:
            switches: Current switch states
            variables: Current variable values
            self_switches: Current self-switch states (keyed by "A", "B", "C", "D")

        Returns:
            Active page or None if no page conditions are met
        """
        for page in self.pages:
            # Check all conditions
            if page.switch1_valid:
                if not switches.get(page.switch1_id, False):
                    continue

            if page.switch2_valid:
                if not switches.get(page.switch2_id, False):
                    continue

            if page.variable_valid:
                if variables.get(page.variable_id, 0) < page.variable_value:
                    continue

            if page.self_switch_valid:
                if not self_switches.get(page.self_switch_ch, False):
                    continue

            # All conditions met
            return page

        return None


class EventManager:
    """Manages event loading, saving, and instances."""

    def __init__(self):
        self.events: Dict[int, GameEvent] = {}
        self._next_id = 1

    def create_event(
        self, name: str = "New Event", x: int = 0, y: int = 0
    ) -> GameEvent:
        """Create a new event."""
        event = GameEvent(id=self._next_id, name=name, x=x, y=y)
        self.events[self._next_id] = event
        self._next_id += 1
        return event

    def get_event(self, event_id: int) -> Optional[GameEvent]:
        """Get event by ID."""
        return self.events.get(event_id)

    def delete_event(self, event_id: int) -> bool:
        """Delete an event."""
        if event_id in self.events:
            del self.events[event_id]
            return True
        return False

    def save_to_file(self, filepath: Path):
        """Save all events to a JSON file."""
        data = {
            "events": [event.to_dict() for event in self.events.values()],
            "next_id": self._next_id,
        }

        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_from_file(self, filepath: Path) -> bool:
        """
        Load events from a JSON file.

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.events.clear()
            for event_data in data.get("events", []):
                event = GameEvent.from_dict(event_data)
                self.events[event.id] = event

            self._next_id = data.get("next_id", max(self.events.keys(), default=0) + 1)
            return True

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading events from {filepath}: {e}")
            return False

    def clear(self):
        """Clear all events."""
        self.events.clear()
        self._next_id = 1


# Convenience functions for creating common event types


def create_door_event(x: int, y: int, target_map: str, target_x: int, target_y: int) -> GameEvent:
    """
    Create a door/transfer event.

    Args:
        x, y: Position on current map
        target_map: Target map name
        target_x, target_y: Target position

    Returns:
        Configured door event
    """
    event = GameEvent(name="Door", x=x, y=y)
    page = event.pages[0]

    # Set as action button trigger
    page.trigger = EventTrigger.ACTION_BUTTON

    # Add transfer command
    page.commands = [
        {
            "code": "TRANSFER_PLAYER",
            "parameters": {
                "map": target_map,
                "x": target_x,
                "y": target_y,
                "direction": 0,  # Retain
                "fade": "black",
            },
        }
    ]

    return event


def create_chest_event(x: int, y: int, item_id: int, item_name: str = "Item") -> GameEvent:
    """
    Create a treasure chest event.

    Args:
        x, y: Position on map
        item_id: Item to give
        item_name: Item name for message

    Returns:
        Configured chest event
    """
    event = GameEvent(name="Chest", x=x, y=y)
    page = event.pages[0]

    # Closed chest graphic (example)
    page.graphic.tile_id = 80  # Assume tile 80 is closed chest

    # Commands: show message, give item, switch graphic, set self-switch
    page.commands = [
        {
            "code": "SHOW_TEXT",
            "parameters": {"text": f"Found {item_name}!"},
        },
        {
            "code": "CHANGE_ITEMS",
            "parameters": {"item_id": item_id, "operation": "increase", "amount": 1},
        },
        {
            "code": "CONTROL_SELF_SWITCH",
            "parameters": {"self_switch": "A", "value": True},
        },
    ]

    # Create second page for opened chest
    opened_page = EventPage()
    opened_page.self_switch_valid = True
    opened_page.self_switch_ch = "A"
    opened_page.graphic.tile_id = 81  # Assume tile 81 is opened chest
    event.pages.append(opened_page)

    return event


def create_npc_event(x: int, y: int, name: str, dialogue: str, sprite: str = "") -> GameEvent:
    """
    Create an NPC event.

    Args:
        x, y: Position on map
        name: NPC name
        dialogue: What the NPC says
        sprite: Character sprite filename

    Returns:
        Configured NPC event
    """
    event = GameEvent(name=name, x=x, y=y)
    page = event.pages[0]

    # Set graphic
    if sprite:
        page.graphic.character_name = sprite
        page.graphic.direction = 2  # Facing down

    # Set as action button trigger
    page.trigger = EventTrigger.ACTION_BUTTON

    # Add dialogue
    page.commands = [
        {
            "code": "SHOW_TEXT",
            "parameters": {"text": dialogue},
        }
    ]

    return event
