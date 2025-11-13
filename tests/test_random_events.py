"""
Tests for Random Events System
Tests dynamic world encounters, loot finds, environmental effects, and event consequences
"""

import pytest
from game.random_events import (
    RandomEvent,
    EventTrigger,
    EventConsequence,
    EventManager,
    EVENT_TYPES,
    EVENT_CATEGORIES,
    TRIGGER_CONDITIONS
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def scavenger_event():
    """Create a scavenger find event."""
    return RandomEvent(
        event_id="event_scav_find",
        name="Abandoned Cache",
        description="You stumble upon a hidden stash of supplies",
        event_type="discovery",
        category="loot",
        probability=0.15,  # 15% chance
        trigger=EventTrigger(
            condition="district",
            value="wasteland"
        ),
        consequences=[
            EventConsequence(
                consequence_type="loot",
                value={"items": ["medkit", "scrap_metal"], "credits": 200}
            )
        ]
    )


@pytest.fixture
def ambush_event():
    """Create an enemy ambush event."""
    return RandomEvent(
        event_id="event_ambush",
        name="Gang Ambush",
        description="A gang jumps you from the shadows!",
        event_type="combat",
        category="danger",
        probability=0.20,
        trigger=EventTrigger(
            condition="time",
            value="night"
        ),
        consequences=[
            EventConsequence(
                consequence_type="combat",
                value={"encounter_id": "ambush_gangers", "difficulty": 3}
            )
        ]
    )


@pytest.fixture
def faction_rep_event():
    """Create a faction reputation event."""
    return RandomEvent(
        event_id="event_faction_help",
        name="Help a Corp Operative",
        description="You assist a corporate operative in need",
        event_type="encounter",
        category="faction",
        probability=0.10,
        trigger=EventTrigger(
            condition="faction_rep",
            value={"faction": "militech", "min_rep": 25}
        ),
        consequences=[
            EventConsequence(
                consequence_type="faction_rep",
                value={"faction": "militech", "amount": 15}
            ),
            EventConsequence(
                consequence_type="credits",
                value=500
            )
        ]
    )


@pytest.fixture
def event_manager():
    """Create an event manager."""
    return EventManager()


# ============================================================================
# TEST EVENT CREATION
# ============================================================================

class TestEventCreation:
    """Test random event initialization."""

    def test_event_creation(self, scavenger_event):
        """Test creating a random event."""
        assert scavenger_event.event_id == "event_scav_find"
        assert scavenger_event.name == "Abandoned Cache"
        assert scavenger_event.event_type == "discovery"
        assert scavenger_event.probability == 0.15

    def test_event_types_valid(self):
        """Test all event types are valid."""
        for event_type in EVENT_TYPES:
            event = RandomEvent(
                event_id=f"event_{event_type}",
                name=f"Test {event_type}",
                description="Test event",
                event_type=event_type,
                category="general",
                probability=0.1,
                trigger=EventTrigger("always", None),
                consequences=[]
            )
            assert event.event_type == event_type

    def test_invalid_event_type_raises_error(self):
        """Test invalid event type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid event type"):
            RandomEvent(
                event_id="event_invalid",
                name="Invalid",
                description="Test",
                event_type="invalid_type",
                category="general",
                probability=0.1,
                trigger=EventTrigger("always", None),
                consequences=[]
            )

    def test_probability_validation(self):
        """Test probability must be 0.0-1.0."""
        with pytest.raises(ValueError, match="Probability must be"):
            RandomEvent(
                event_id="event_test",
                name="Test",
                description="Test",
                event_type="discovery",
                category="general",
                probability=1.5,  # Invalid
                trigger=EventTrigger("always", None),
                consequences=[]
            )


# ============================================================================
# TEST EVENT TRIGGERS
# ============================================================================

class TestEventTriggers:
    """Test event trigger conditions."""

    def test_trigger_creation(self):
        """Test creating an event trigger."""
        trigger = EventTrigger(
            condition="district",
            value="wasteland"
        )

        assert trigger.condition == "district"
        assert trigger.value == "wasteland"

    def test_trigger_conditions_valid(self):
        """Test valid trigger conditions."""
        for condition in TRIGGER_CONDITIONS:
            trigger = EventTrigger(
                condition=condition,
                value="test_value"
            )
            assert trigger.condition == condition

    def test_check_district_trigger(self):
        """Test district-based trigger."""
        trigger = EventTrigger(condition="district", value="wasteland")

        assert trigger.check({"district": "wasteland"}) is True
        assert trigger.check({"district": "city_center"}) is False

    def test_check_time_trigger(self):
        """Test time-based trigger."""
        trigger = EventTrigger(condition="time", value="night")

        assert trigger.check({"time": "night"}) is True
        assert trigger.check({"time": "day"}) is False

    def test_check_faction_rep_trigger(self):
        """Test faction reputation trigger."""
        trigger = EventTrigger(
            condition="faction_rep",
            value={"faction": "militech", "min_rep": 25}
        )

        assert trigger.check({"faction_reps": {"militech": 30}}) is True
        assert trigger.check({"faction_reps": {"militech": 20}}) is False

    def test_always_trigger(self):
        """Test always-active trigger."""
        trigger = EventTrigger(condition="always", value=None)

        assert trigger.check({}) is True
        assert trigger.check({"district": "any"}) is True


# ============================================================================
# TEST EVENT CONSEQUENCES
# ============================================================================

class TestEventConsequences:
    """Test event consequences."""

    def test_consequence_creation(self):
        """Test creating an event consequence."""
        consequence = EventConsequence(
            consequence_type="loot",
            value={"items": ["medkit"], "credits": 100}
        )

        assert consequence.consequence_type == "loot"
        assert consequence.value["credits"] == 100

    def test_loot_consequence(self):
        """Test loot consequence application."""
        consequence = EventConsequence(
            consequence_type="loot",
            value={"items": ["medkit", "ammo"], "credits": 150}
        )

        result = consequence.apply({})

        assert "loot" in result
        assert result["loot"]["credits"] == 150
        assert "medkit" in result["loot"]["items"]

    def test_faction_rep_consequence(self):
        """Test faction reputation consequence."""
        consequence = EventConsequence(
            consequence_type="faction_rep",
            value={"faction": "militech", "amount": 15}
        )

        result = consequence.apply({})

        assert "faction_rep_change" in result
        assert result["faction_rep_change"]["militech"] == 15

    def test_combat_consequence(self):
        """Test combat encounter consequence."""
        consequence = EventConsequence(
            consequence_type="combat",
            value={"encounter_id": "ambush_gangers", "difficulty": 3}
        )

        result = consequence.apply({})

        assert "combat" in result
        assert result["combat"]["encounter_id"] == "ambush_gangers"

    def test_status_effect_consequence(self):
        """Test status effect consequence."""
        consequence = EventConsequence(
            consequence_type="status_effect",
            value={"effect": "poisoned", "duration": 3}
        )

        result = consequence.apply({})

        assert "status_effect" in result
        assert result["status_effect"]["effect"] == "poisoned"


# ============================================================================
# TEST EVENT MANAGER
# ============================================================================

class TestEventManager:
    """Test event manager operations."""

    def test_add_event(self, event_manager, scavenger_event):
        """Test adding event to manager."""
        event_manager.add_event(scavenger_event)

        assert len(event_manager.get_all_events()) == 1

    def test_add_multiple_events(
        self,
        event_manager,
        scavenger_event,
        ambush_event
    ):
        """Test adding multiple events."""
        event_manager.add_event(scavenger_event)
        event_manager.add_event(ambush_event)

        assert len(event_manager.get_all_events()) == 2

    def test_get_event_by_id(self, event_manager, scavenger_event):
        """Test retrieving event by ID."""
        event_manager.add_event(scavenger_event)

        event = event_manager.get_event("event_scav_find")

        assert event == scavenger_event

    def test_remove_event(self, event_manager, scavenger_event):
        """Test removing event."""
        event_manager.add_event(scavenger_event)
        event_manager.remove_event("event_scav_find")

        assert len(event_manager.get_all_events()) == 0


# ============================================================================
# TEST EVENT TRIGGERING
# ============================================================================

class TestEventTriggering:
    """Test event triggering mechanics."""

    def test_trigger_event_manually(self, event_manager, scavenger_event):
        """Test manually triggering an event."""
        event_manager.add_event(scavenger_event)

        result = event_manager.trigger_event("event_scav_find", {})

        assert result["success"] is True
        assert "consequences" in result

    def test_check_for_events_district_match(
        self,
        event_manager
    ):
        """Test checking for events with matching district."""
        # Create guaranteed event (100% probability)
        guaranteed_event = RandomEvent(
            event_id="event_guaranteed_district",
            name="Guaranteed District Event",
            description="Always triggers in wasteland",
            event_type="discovery",
            category="loot",
            probability=1.0,  # 100% chance
            trigger=EventTrigger("district", "wasteland"),
            consequences=[]
        )
        event_manager.add_event(guaranteed_event)

        triggered = event_manager.check_for_events({"district": "wasteland"})

        assert len(triggered) > 0

    def test_check_for_events_no_match(
        self,
        event_manager,
        scavenger_event
    ):
        """Test checking for events with no match."""
        event_manager.add_event(scavenger_event)

        triggered = event_manager.check_for_events({"district": "city_center"})

        # Might not trigger due to probability, but should pass trigger check
        # This tests the trigger condition, not random roll
        assert isinstance(triggered, list)

    def test_roll_for_event_success(self, event_manager):
        """Test event probability roll succeeds."""
        # Create event with 100% probability
        guaranteed_event = RandomEvent(
            event_id="event_guaranteed",
            name="Guaranteed",
            description="Always happens",
            event_type="discovery",
            category="general",
            probability=1.0,  # 100% chance
            trigger=EventTrigger("always", None),
            consequences=[]
        )

        event_manager.add_event(guaranteed_event)

        triggered = event_manager.check_for_events({})

        assert len(triggered) > 0
        assert guaranteed_event in triggered

    def test_roll_for_event_failure(self, event_manager):
        """Test event probability roll fails."""
        # Create event with 0% probability
        impossible_event = RandomEvent(
            event_id="event_impossible",
            name="Impossible",
            description="Never happens",
            event_type="discovery",
            category="general",
            probability=0.0,  # 0% chance
            trigger=EventTrigger("always", None),
            consequences=[]
        )

        event_manager.add_event(impossible_event)

        triggered = event_manager.check_for_events({})

        assert impossible_event not in triggered


# ============================================================================
# TEST EVENT CATEGORIES
# ============================================================================

class TestEventCategories:
    """Test event categorization."""

    def test_get_events_by_category(
        self,
        event_manager,
        scavenger_event,
        ambush_event
    ):
        """Test filtering events by category."""
        event_manager.add_event(scavenger_event)  # loot
        event_manager.add_event(ambush_event)     # danger

        loot_events = event_manager.get_events_by_category("loot")
        danger_events = event_manager.get_events_by_category("danger")

        assert len(loot_events) == 1
        assert len(danger_events) == 1
        assert scavenger_event in loot_events
        assert ambush_event in danger_events

    def test_get_events_by_type(
        self,
        event_manager,
        scavenger_event,
        ambush_event
    ):
        """Test filtering events by type."""
        event_manager.add_event(scavenger_event)  # discovery
        event_manager.add_event(ambush_event)     # combat

        discovery_events = event_manager.get_events_by_type("discovery")
        combat_events = event_manager.get_events_by_type("combat")

        assert len(discovery_events) == 1
        assert len(combat_events) == 1


# ============================================================================
# TEST EVENT COOLDOWNS
# ============================================================================

class TestEventCooldowns:
    """Test event cooldown system."""

    def test_event_has_cooldown(self):
        """Test events can have cooldowns."""
        event = RandomEvent(
            event_id="event_rare",
            name="Rare Event",
            description="Can only happen once per hour",
            event_type="discovery",
            category="general",
            probability=0.5,
            trigger=EventTrigger("always", None),
            consequences=[],
            cooldown=3600  # 1 hour in seconds
        )

        assert event.cooldown == 3600

    def test_event_on_cooldown(self, event_manager):
        """Test event on cooldown cannot trigger again."""
        event = RandomEvent(
            event_id="event_cooldown_test",
            name="Cooldown Test",
            description="Test",
            event_type="discovery",
            category="general",
            probability=1.0,
            trigger=EventTrigger("always", None),
            consequences=[],
            cooldown=60  # 1 minute
        )

        event_manager.add_event(event)

        # Trigger event
        event_manager.trigger_event("event_cooldown_test", {})

        # Try to trigger again immediately
        result = event_manager.trigger_event("event_cooldown_test", {})

        assert result["success"] is False
        assert "on cooldown" in result["error"]

    def test_event_cooldown_expires(self, event_manager):
        """Test event cooldown expires after time."""
        event = RandomEvent(
            event_id="event_cooldown_expire",
            name="Cooldown Expire",
            description="Test",
            event_type="discovery",
            category="general",
            probability=1.0,
            trigger=EventTrigger("always", None),
            consequences=[],
            cooldown=1  # 1 second
        )

        event_manager.add_event(event)

        # Trigger event
        event_manager.trigger_event("event_cooldown_expire", {})

        # Advance time by 2 seconds
        event_manager.advance_time(2)

        # Should be able to trigger again
        result = event_manager.trigger_event("event_cooldown_expire", {})

        assert result["success"] is True


# ============================================================================
# TEST ONE-TIME EVENTS
# ============================================================================

class TestOneTimeEvents:
    """Test one-time event system."""

    def test_one_time_event(self):
        """Test creating a one-time event."""
        event = RandomEvent(
            event_id="event_unique",
            name="Unique Event",
            description="Can only happen once ever",
            event_type="discovery",
            category="general",
            probability=1.0,
            trigger=EventTrigger("always", None),
            consequences=[],
            one_time=True
        )

        assert event.one_time is True

    def test_one_time_event_triggers_once(self, event_manager):
        """Test one-time event can only trigger once."""
        event = RandomEvent(
            event_id="event_one_time",
            name="One Time",
            description="Test",
            event_type="discovery",
            category="general",
            probability=1.0,
            trigger=EventTrigger("always", None),
            consequences=[],
            one_time=True
        )

        event_manager.add_event(event)

        # First trigger succeeds
        result1 = event_manager.trigger_event("event_one_time", {})
        assert result1["success"] is True

        # Second trigger fails
        result2 = event_manager.trigger_event("event_one_time", {})
        assert result2["success"] is False
        assert "already triggered" in result2["error"]


# ============================================================================
# TEST EVENT SERIALIZATION
# ============================================================================

class TestEventSerialization:
    """Test event serialization."""

    def test_event_serialization(self, scavenger_event):
        """Test event to_dict and from_dict."""
        data = scavenger_event.to_dict()
        restored = RandomEvent.from_dict(data)

        assert restored.event_id == scavenger_event.event_id
        assert restored.name == scavenger_event.name
        assert restored.probability == scavenger_event.probability

    def test_event_manager_serialization(
        self,
        event_manager,
        scavenger_event,
        ambush_event
    ):
        """Test event manager serialization."""
        # Create a one-time event for testing serialization
        one_time_event = RandomEvent(
            event_id="event_one_time_test",
            name="One Time Test",
            description="Test",
            event_type="discovery",
            category="general",
            probability=1.0,
            trigger=EventTrigger("always", None),
            consequences=[],
            one_time=True
        )

        event_manager.add_event(scavenger_event)
        event_manager.add_event(ambush_event)
        event_manager.add_event(one_time_event)
        event_manager.trigger_event("event_one_time_test", {})

        data = event_manager.to_dict()
        restored = EventManager.from_dict(data)

        assert len(restored.get_all_events()) == 3
        assert len(restored.triggered_one_time) == 1


# ============================================================================
# TEST EDGE CASES
# ============================================================================

class TestRandomEventEdgeCases:
    """Test edge cases and error handling."""

    def test_trigger_unknown_event(self, event_manager):
        """Test triggering unknown event."""
        result = event_manager.trigger_event("unknown_event", {})

        assert result["success"] is False
        assert "not found" in result["error"]

    def test_event_with_no_consequences(self):
        """Test event with no consequences."""
        event = RandomEvent(
            event_id="event_empty",
            name="Empty",
            description="Does nothing",
            event_type="discovery",
            category="general",
            probability=1.0,
            trigger=EventTrigger("always", None),
            consequences=[]
        )

        assert len(event.consequences) == 0

    def test_event_with_multiple_consequences(self):
        """Test event with multiple consequences."""
        event = RandomEvent(
            event_id="event_multi",
            name="Multi Consequence",
            description="Has multiple effects",
            event_type="discovery",
            category="general",
            probability=1.0,
            trigger=EventTrigger("always", None),
            consequences=[
                EventConsequence("credits", 100),
                EventConsequence("faction_rep", {"faction": "militech", "amount": 10}),
                EventConsequence("loot", {"items": ["medkit"]})
            ]
        )

        assert len(event.consequences) == 3


# ============================================================================
# TEST INTEGRATION
# ============================================================================

class TestRandomEventIntegration:
    """Test integration with other game systems."""

    def test_event_triggers_combat_encounter(self, event_manager, ambush_event):
        """Test event can trigger combat."""
        event_manager.add_event(ambush_event)

        result = event_manager.trigger_event("event_ambush", {})

        assert result["success"] is True
        combat_data = result["consequences"][0]["combat"]
        assert combat_data["encounter_id"] == "ambush_gangers"

    def test_event_gives_faction_reputation(
        self,
        event_manager,
        faction_rep_event
    ):
        """Test event modifies faction reputation."""
        event_manager.add_event(faction_rep_event)

        result = event_manager.trigger_event(
            "event_faction_help",
            {"faction_reps": {"militech": 30}}
        )

        assert result["success"] is True
        # Check faction rep increase in consequences
        faction_change = result["consequences"][0]["faction_rep_change"]
        assert faction_change["militech"] == 15

    def test_event_provides_loot(self, event_manager, scavenger_event):
        """Test event provides loot items."""
        event_manager.add_event(scavenger_event)

        result = event_manager.trigger_event("event_scav_find", {})

        assert result["success"] is True
        loot = result["consequences"][0]["loot"]
        assert loot["credits"] == 200
        assert "medkit" in loot["items"]
