"""
Neon Collapse - Random Events System
Manages dynamic world encounters, loot finds, environmental effects, and event consequences
"""

from typing import Dict, List, Any, Optional
import random
import time


# Constants
EVENT_TYPES = ["discovery", "combat", "encounter", "environmental", "faction"]
EVENT_CATEGORIES = ["loot", "danger", "faction", "general", "rare"]
TRIGGER_CONDITIONS = ["always", "district", "time", "faction_rep", "quest_state"]


# ============================================================================
# EVENT TRIGGER CLASS
# ============================================================================

class EventTrigger:
    """Represents conditions for event triggering."""

    def __init__(self, condition: str, value: Any):
        if condition not in TRIGGER_CONDITIONS:
            raise ValueError(f"Invalid trigger condition: {condition}")

        self.condition = condition
        self.value = value

    def check(self, context: Dict[str, Any]) -> bool:
        """
        Check if trigger conditions are met.

        Args:
            context: Current game state context

        Returns:
            True if conditions met
        """
        if self.condition == "always":
            return True

        elif self.condition == "district":
            return context.get("district") == self.value

        elif self.condition == "time":
            return context.get("time") == self.value

        elif self.condition == "faction_rep":
            faction = self.value.get("faction")
            min_rep = self.value.get("min_rep", 0)
            faction_reps = context.get("faction_reps", {})
            return faction_reps.get(faction, 0) >= min_rep

        elif self.condition == "quest_state":
            quest_id = self.value.get("quest_id")
            required_state = self.value.get("state")
            quest_states = context.get("quest_states", {})
            return quest_states.get(quest_id) == required_state

        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "condition": self.condition,
            "value": self.value
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventTrigger':
        """Load from dictionary."""
        return cls(
            condition=data["condition"],
            value=data["value"]
        )


# ============================================================================
# EVENT CONSEQUENCE CLASS
# ============================================================================

class EventConsequence:
    """Represents consequences/effects of an event."""

    def __init__(self, consequence_type: str, value: Any):
        self.consequence_type = consequence_type
        self.value = value

    def apply(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply consequence effects.

        Args:
            context: Current game state

        Returns:
            Dictionary of applied effects
        """
        result = {}

        if self.consequence_type == "loot":
            result["loot"] = self.value

        elif self.consequence_type == "credits":
            result["credits"] = self.value

        elif self.consequence_type == "faction_rep":
            faction = self.value.get("faction")
            amount = self.value.get("amount")
            result["faction_rep_change"] = {faction: amount}

        elif self.consequence_type == "combat":
            result["combat"] = self.value

        elif self.consequence_type == "status_effect":
            result["status_effect"] = self.value

        elif self.consequence_type == "quest_unlock":
            result["quest_unlock"] = self.value

        return result

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "consequence_type": self.consequence_type,
            "value": self.value
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventConsequence':
        """Load from dictionary."""
        return cls(
            consequence_type=data["consequence_type"],
            value=data["value"]
        )


# ============================================================================
# RANDOM EVENT CLASS
# ============================================================================

class RandomEvent:
    """Represents a random world event."""

    def __init__(
        self,
        event_id: str,
        name: str,
        description: str,
        event_type: str,
        category: str,
        probability: float,
        trigger: EventTrigger,
        consequences: List[EventConsequence],
        cooldown: int = 0,
        one_time: bool = False
    ):
        if event_type not in EVENT_TYPES:
            raise ValueError(f"Invalid event type: {event_type}")

        if probability < 0.0 or probability > 1.0:
            raise ValueError(f"Probability must be 0.0-1.0, got {probability}")

        self.event_id = event_id
        self.name = name
        self.description = description
        self.event_type = event_type
        self.category = category
        self.probability = probability
        self.trigger = trigger
        self.consequences = consequences
        self.cooldown = cooldown
        self.one_time = one_time

    def can_trigger(self, context: Dict[str, Any]) -> bool:
        """
        Check if event can trigger.

        Args:
            context: Current game state

        Returns:
            True if event can trigger
        """
        # Check trigger conditions
        return self.trigger.check(context)

    def roll_probability(self) -> bool:
        """
        Roll for event probability.

        Returns:
            True if event triggers
        """
        return random.random() < self.probability

    def apply_consequences(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Apply all event consequences.

        Args:
            context: Current game state

        Returns:
            List of consequence results
        """
        results = []

        for consequence in self.consequences:
            result = consequence.apply(context)
            results.append(result)

        return results

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_id": self.event_id,
            "name": self.name,
            "description": self.description,
            "event_type": self.event_type,
            "category": self.category,
            "probability": self.probability,
            "trigger": self.trigger.to_dict(),
            "consequences": [c.to_dict() for c in self.consequences],
            "cooldown": self.cooldown,
            "one_time": self.one_time
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RandomEvent':
        """Load from dictionary."""
        trigger = EventTrigger.from_dict(data["trigger"])
        consequences = [
            EventConsequence.from_dict(c)
            for c in data.get("consequences", [])
        ]

        return cls(
            event_id=data["event_id"],
            name=data["name"],
            description=data["description"],
            event_type=data["event_type"],
            category=data["category"],
            probability=data["probability"],
            trigger=trigger,
            consequences=consequences,
            cooldown=data.get("cooldown", 0),
            one_time=data.get("one_time", False)
        )


# ============================================================================
# EVENT MANAGER CLASS
# ============================================================================

class EventManager:
    """Manages random events and triggering."""

    def __init__(self):
        self.events: Dict[str, RandomEvent] = {}
        self.cooldowns: Dict[str, float] = {}  # event_id -> expiry time
        self.triggered_one_time: List[str] = []  # List of one-time events triggered
        self.current_time: float = time.time()

    def add_event(self, event: RandomEvent):
        """Add an event to the manager."""
        self.events[event.event_id] = event

    def remove_event(self, event_id: str):
        """Remove an event from the manager."""
        if event_id in self.events:
            del self.events[event_id]

    def get_event(self, event_id: str) -> Optional[RandomEvent]:
        """Get specific event by ID."""
        return self.events.get(event_id)

    def get_all_events(self) -> List[RandomEvent]:
        """Get all events."""
        return list(self.events.values())

    def get_events_by_category(self, category: str) -> List[RandomEvent]:
        """Get events filtered by category."""
        return [
            event for event in self.events.values()
            if event.category == category
        ]

    def get_events_by_type(self, event_type: str) -> List[RandomEvent]:
        """Get events filtered by type."""
        return [
            event for event in self.events.values()
            if event.event_type == event_type
        ]

    def is_on_cooldown(self, event_id: str) -> bool:
        """
        Check if event is on cooldown.

        Args:
            event_id: Event to check

        Returns:
            True if on cooldown
        """
        if event_id not in self.cooldowns:
            return False

        expiry_time = self.cooldowns[event_id]
        return self.current_time < expiry_time

    def has_triggered_one_time(self, event_id: str) -> bool:
        """
        Check if one-time event has been triggered.

        Args:
            event_id: Event to check

        Returns:
            True if already triggered
        """
        return event_id in self.triggered_one_time

    def trigger_event(
        self,
        event_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Manually trigger a specific event.

        Args:
            event_id: Event to trigger
            context: Current game state

        Returns:
            Result dictionary with consequences
        """
        if event_id not in self.events:
            return {
                "success": False,
                "error": f"Event {event_id} not found"
            }

        event = self.events[event_id]

        # Check if one-time event already triggered
        if event.one_time and self.has_triggered_one_time(event_id):
            return {
                "success": False,
                "error": f"Event {event_id} already triggered (one-time only)"
            }

        # Check cooldown
        if self.is_on_cooldown(event_id):
            return {
                "success": False,
                "error": f"Event {event_id} is on cooldown"
            }

        # Apply consequences
        consequences = event.apply_consequences(context)

        # Set cooldown if applicable
        if event.cooldown > 0:
            self.cooldowns[event_id] = self.current_time + event.cooldown

        # Mark one-time event as triggered
        if event.one_time:
            self.triggered_one_time.append(event_id)

        return {
            "success": True,
            "event": event,
            "consequences": consequences
        }

    def check_for_events(self, context: Dict[str, Any]) -> List[RandomEvent]:
        """
        Check for events that can trigger.

        Args:
            context: Current game state

        Returns:
            List of events that triggered
        """
        triggered = []

        for event in self.events.values():
            # Skip if one-time already triggered
            if event.one_time and self.has_triggered_one_time(event.event_id):
                continue

            # Skip if on cooldown
            if self.is_on_cooldown(event.event_id):
                continue

            # Check trigger conditions
            if not event.can_trigger(context):
                continue

            # Roll probability
            if not event.roll_probability():
                continue

            # Event triggered!
            triggered.append(event)

        return triggered

    def advance_time(self, seconds: float):
        """
        Advance game time (for cooldowns).

        Args:
            seconds: Seconds to advance
        """
        self.current_time += seconds

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "events": {
                event_id: event.to_dict()
                for event_id, event in self.events.items()
            },
            "cooldowns": self.cooldowns.copy(),
            "triggered_one_time": self.triggered_one_time.copy(),
            "current_time": self.current_time
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventManager':
        """Load from dictionary."""
        manager = cls()

        # Restore events
        for event_data in data.get("events", {}).values():
            event = RandomEvent.from_dict(event_data)
            manager.events[event.event_id] = event

        # Restore cooldowns
        manager.cooldowns = data.get("cooldowns", {})

        # Restore triggered one-time events
        manager.triggered_one_time = data.get("triggered_one_time", [])

        # Restore time
        manager.current_time = data.get("current_time", time.time())

        return manager
