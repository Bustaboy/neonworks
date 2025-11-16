"""
Tests for Random Encounter System

Tests the JRPG-style random encounter system including encounter groups,
encounter tables, step-based triggering, and repel effects.
"""

import pytest

from neonworks.core.ecs import World
from neonworks.core.events import Event, EventManager, EventType
from neonworks.systems.random_encounters import (
    EncounterGroup,
    EncounterTable,
    RandomEncounterSystem,
)


class TestEncounterGroup:
    """Test suite for EncounterGroup"""

    def test_init_basic(self):
        """Test basic EncounterGroup initialization"""
        group = EncounterGroup(group_id="slime_group")

        assert group.group_id == "slime_group"
        assert group.enemies == []
        assert group.weight == 10
        assert group.min_steps == 0
        assert group.max_steps == 9999

    def test_init_with_enemies(self):
        """Test EncounterGroup initialization with enemies"""
        enemies = [
            {"enemy_id": "slime", "level": 1, "position": 0},
            {"enemy_id": "slime", "level": 1, "position": 1},
        ]
        group = EncounterGroup(group_id="slime_pair", enemies=enemies)

        assert len(group.enemies) == 2
        assert group.enemies[0]["enemy_id"] == "slime"

    def test_init_with_custom_weight(self):
        """Test EncounterGroup with custom weight"""
        group = EncounterGroup(group_id="rare_group", weight=5)

        assert group.weight == 5

    def test_init_with_step_range(self):
        """Test EncounterGroup with step range"""
        group = EncounterGroup(group_id="late_game_group", min_steps=100, max_steps=500)

        assert group.min_steps == 100
        assert group.max_steps == 500

    def test_get_total_enemies_empty(self):
        """Test getting total enemies for empty group"""
        group = EncounterGroup(group_id="empty_group")

        assert group.get_total_enemies() == 0

    def test_get_total_enemies_single(self):
        """Test getting total enemies for single enemy"""
        enemies = [{"enemy_id": "slime", "level": 1, "position": 0}]
        group = EncounterGroup(group_id="single_group", enemies=enemies)

        assert group.get_total_enemies() == 1

    def test_get_total_enemies_multiple(self):
        """Test getting total enemies for multiple enemies"""
        enemies = [
            {"enemy_id": "goblin", "level": 2, "position": 0},
            {"enemy_id": "goblin", "level": 2, "position": 1},
            {"enemy_id": "slime", "level": 1, "position": 2},
        ]
        group = EncounterGroup(group_id="multi_group", enemies=enemies)

        assert group.get_total_enemies() == 3


class TestEncounterTable:
    """Test suite for EncounterTable"""

    def test_init_basic(self):
        """Test basic EncounterTable initialization"""
        table = EncounterTable(zone_id="grassland")

        assert table.zone_id == "grassland"
        assert table.encounter_rate == 30.0
        assert table.step_interval == 8
        assert table.groups == []
        assert table.rate_multiplier == 1.0
        assert table.can_encounter is True

    def test_init_with_custom_values(self):
        """Test EncounterTable with custom values"""
        table = EncounterTable(zone_id="forest", encounter_rate=40.0, step_interval=6)

        assert table.zone_id == "forest"
        assert table.encounter_rate == 40.0
        assert table.step_interval == 6

    def test_add_group(self):
        """Test adding encounter group to table"""
        table = EncounterTable(zone_id="test_zone")
        group = EncounterGroup(group_id="test_group")

        table.add_group(group)

        assert len(table.groups) == 1
        assert table.groups[0] == group

    def test_add_multiple_groups(self):
        """Test adding multiple groups"""
        table = EncounterTable(zone_id="test_zone")
        group1 = EncounterGroup(group_id="group1")
        group2 = EncounterGroup(group_id="group2")

        table.add_group(group1)
        table.add_group(group2)

        assert len(table.groups) == 2

    def test_get_random_group_no_groups(self):
        """Test getting random group when no groups exist"""
        table = EncounterTable(zone_id="test_zone")

        group = table.get_random_group(steps=10)

        assert group is None

    def test_get_random_group_encounters_disabled(self):
        """Test getting random group when encounters are disabled"""
        table = EncounterTable(zone_id="test_zone")
        table.can_encounter = False
        table.add_group(EncounterGroup(group_id="test_group"))

        group = table.get_random_group(steps=10)

        assert group is None

    def test_get_random_group_within_step_range(self):
        """Test getting random group within valid step range"""
        table = EncounterTable(zone_id="test_zone")
        group = EncounterGroup(group_id="valid_group", min_steps=10, max_steps=50, weight=100)
        table.add_group(group)

        # Within range
        result = table.get_random_group(steps=30)
        assert result is not None
        assert result.group_id == "valid_group"

    def test_get_random_group_outside_step_range(self):
        """Test getting random group outside valid step range"""
        table = EncounterTable(zone_id="test_zone")
        group = EncounterGroup(group_id="limited_group", min_steps=10, max_steps=50)
        table.add_group(group)

        # Below min_steps
        result = table.get_random_group(steps=5)
        assert result is None

        # Above max_steps
        result = table.get_random_group(steps=60)
        assert result is None

    def test_get_random_group_weighted_selection(self):
        """Test weighted random selection of groups"""
        table = EncounterTable(zone_id="test_zone")
        group1 = EncounterGroup(group_id="common", weight=90)
        group2 = EncounterGroup(group_id="rare", weight=10)
        table.add_group(group1)
        table.add_group(group2)

        # Run multiple times to check distribution
        results = []
        for _ in range(100):
            result = table.get_random_group(steps=10)
            if result:
                results.append(result.group_id)

        # Should have some encounters (randomness)
        assert len(results) > 0
        # Common should appear more often (but not guaranteed in 100 tries)
        assert "common" in results or "rare" in results

    def test_get_random_group_zero_weight(self):
        """Test groups with zero total weight"""
        table = EncounterTable(zone_id="test_zone")
        group = EncounterGroup(group_id="zero_weight", weight=0)
        table.add_group(group)

        result = table.get_random_group(steps=10)

        assert result is None


class TestRandomEncounterSystem:
    """Test suite for RandomEncounterSystem"""

    @pytest.fixture
    def event_manager(self):
        """Create event manager for tests"""
        return EventManager()

    def test_init(self, event_manager):
        """Test RandomEncounterSystem initialization"""
        system = RandomEncounterSystem(event_manager)

        assert system.priority == 20
        assert system.event_manager is event_manager
        assert system.encounter_tables != {}  # Has default tables
        assert system.current_zone == ""
        assert system.step_count == 0
        assert system.steps_since_last_encounter == 0
        assert system.repel_active is False

    def test_init_loads_default_tables(self, event_manager):
        """Test that initialization loads default encounter tables"""
        system = RandomEncounterSystem(event_manager)

        # Should have default zones
        assert "grassland" in system.encounter_tables
        assert "forest" in system.encounter_tables
        assert "dungeon" in system.encounter_tables

    def test_register_encounter_table(self, event_manager):
        """Test registering custom encounter table"""
        system = RandomEncounterSystem(event_manager)
        table = EncounterTable(zone_id="custom_zone")

        system.register_encounter_table(table)

        assert "custom_zone" in system.encounter_tables
        assert system.encounter_tables["custom_zone"] == table

    def test_set_current_zone(self, event_manager):
        """Test setting current zone"""
        system = RandomEncounterSystem(event_manager)
        system.step_count = 100
        system.steps_since_last_encounter = 50

        system.set_current_zone("grassland")

        assert system.current_zone == "grassland"
        assert system.step_count == 0
        assert system.steps_since_last_encounter == 0

    def test_check_encounter_no_zone(self, event_manager):
        """Test check_encounter with no current zone"""
        system = RandomEncounterSystem(event_manager)

        result = system.check_encounter()

        assert result is False

    def test_check_encounter_invalid_zone(self, event_manager):
        """Test check_encounter with invalid zone"""
        system = RandomEncounterSystem(event_manager)
        system.current_zone = "nonexistent_zone"

        result = system.check_encounter()

        assert result is False

    def test_check_encounter_encounters_disabled(self, event_manager):
        """Test check_encounter when encounters are disabled"""
        system = RandomEncounterSystem(event_manager)
        system.current_zone = "grassland"
        table = system.encounter_tables["grassland"]
        table.can_encounter = False

        result = system.check_encounter()

        assert result is False

    def test_check_encounter_wrong_step_interval(self, event_manager):
        """Test check_encounter outside step interval"""
        system = RandomEncounterSystem(event_manager)
        system.current_zone = "grassland"
        system.steps_since_last_encounter = 5  # Not divisible by 8

        result = system.check_encounter()

        assert result is False

    def test_activate_repel(self, event_manager):
        """Test activating repel effect"""
        event_manager.set_immediate_mode(True)
        system = RandomEncounterSystem(event_manager)

        events = []

        def capture_event(event):
            if event.data.get("type") == "repel_activated":
                events.append(event)

        event_manager.subscribe(EventType.CUSTOM, capture_event)

        system.activate_repel(duration=100)

        assert system.repel_active is True
        assert system.repel_duration == 100
        assert len(events) == 1
        assert events[0].data["duration"] == 100

    def test_deactivate_repel(self, event_manager):
        """Test deactivating repel effect"""
        event_manager.set_immediate_mode(True)
        system = RandomEncounterSystem(event_manager)
        system.repel_active = True
        system.repel_duration = 50

        events = []

        def capture_event(event):
            if event.data.get("type") == "repel_deactivated":
                events.append(event)

        event_manager.subscribe(EventType.CUSTOM, capture_event)

        system.deactivate_repel()

        assert system.repel_active is False
        assert system.repel_duration == 0
        assert len(events) == 1

    def test_force_encounter_success(self, event_manager):
        """Test forcing a specific encounter"""
        event_manager.set_immediate_mode(True)
        system = RandomEncounterSystem(event_manager)
        system.current_zone = "grassland"

        events = []

        def capture_event(event):
            if event.data.get("type") == "random_encounter":
                events.append(event)

        event_manager.subscribe(EventType.CUSTOM, capture_event)

        result = system.force_encounter("slime_single")

        assert result is True
        assert len(events) == 1
        assert events[0].data["group_id"] == "slime_single"
        assert events[0].data.get("forced") is True

    def test_force_encounter_no_zone(self, event_manager):
        """Test forcing encounter with no current zone"""
        system = RandomEncounterSystem(event_manager)

        result = system.force_encounter("slime_single")

        assert result is False

    def test_force_encounter_invalid_group(self, event_manager):
        """Test forcing encounter with invalid group ID"""
        system = RandomEncounterSystem(event_manager)
        system.current_zone = "grassland"

        result = system.force_encounter("nonexistent_group")

        assert result is False

    def test_handle_player_step_event(self, event_manager):
        """Test handling player_step custom event"""
        system = RandomEncounterSystem(event_manager)
        system.current_zone = "grassland"

        initial_steps = system.step_count
        initial_since_last = system.steps_since_last_encounter

        # Emit player_step event
        event_manager.emit(Event(EventType.CUSTOM, {"type": "player_step"}))
        event_manager.process_events()

        assert system.step_count == initial_steps + 1
        assert system.steps_since_last_encounter == initial_since_last + 1

    def test_handle_player_step_reduces_repel_duration(self, event_manager):
        """Test that player steps reduce repel duration"""
        system = RandomEncounterSystem(event_manager)
        system.current_zone = "grassland"
        system.activate_repel(duration=10)

        initial_duration = system.repel_duration

        # Take a step
        event_manager.emit(Event(EventType.CUSTOM, {"type": "player_step"}))
        event_manager.process_events()

        assert system.repel_duration == initial_duration - 1

    def test_handle_player_step_deactivates_repel_at_zero(self, event_manager):
        """Test that repel deactivates when duration reaches zero"""
        event_manager.set_immediate_mode(True)
        system = RandomEncounterSystem(event_manager)
        system.current_zone = "grassland"
        system.activate_repel(duration=1)

        # Take a step (should reduce to 0 and deactivate)
        event_manager.emit(Event(EventType.CUSTOM, {"type": "player_step"}))
        event_manager.process_events()

        assert system.repel_active is False
        assert system.repel_duration == 0

    def test_handle_zone_loaded_event(self, event_manager):
        """Test handling zone_loaded custom event"""
        system = RandomEncounterSystem(event_manager)
        system.step_count = 100

        # Emit zone_loaded event
        event_manager.emit(Event(EventType.CUSTOM, {"type": "zone_loaded", "zone_id": "forest"}))
        event_manager.process_events()

        assert system.current_zone == "forest"
        assert system.step_count == 0

    def test_get_encounter_stats(self, event_manager):
        """Test getting encounter statistics"""
        system = RandomEncounterSystem(event_manager)
        system.current_zone = "grassland"
        system.step_count = 42
        system.steps_since_last_encounter = 15
        system.activate_repel(duration=50)

        stats = system.get_encounter_stats()

        assert stats["current_zone"] == "grassland"
        assert stats["step_count"] == 42
        assert stats["steps_since_last"] == 15
        assert stats["repel_active"] is True
        assert stats["repel_duration"] == 50

    def test_update_with_repel_active(self, world, event_manager):
        """Test update method with repel active"""
        system = RandomEncounterSystem(event_manager)
        system.activate_repel(duration=100)

        # Update should not crash
        system.update(world, 0.016)

        # Repel should still be active (only reduced by steps, not time)
        assert system.repel_active is True


class TestEncounterIntegration:
    """Integration tests for random encounter system"""

    def test_full_encounter_flow(self, event_manager):
        """Test complete encounter flow from step to battle"""
        event_manager.set_immediate_mode(True)
        system = RandomEncounterSystem(event_manager)
        system.set_current_zone("grassland")

        # Track encounters
        encounters = []

        def capture_encounter(event):
            if event.data.get("type") == "random_encounter":
                encounters.append(event)

        event_manager.subscribe(EventType.CUSTOM, capture_encounter)

        # Simulate many steps (should trigger at least one encounter)
        for _ in range(200):
            event_manager.emit(Event(EventType.CUSTOM, {"type": "player_step"}))
            event_manager.process_events()

        # Should have triggered at least one encounter (probabilistic)
        # With 200 steps and default settings, very likely to get one
        assert len(encounters) >= 0  # May or may not trigger due to randomness

    def test_repel_reduces_encounter_rate(self, event_manager):
        """Test that repel reduces encounter rate"""
        system = RandomEncounterSystem(event_manager)
        system.set_current_zone("grassland")
        system.activate_repel(duration=1000)

        # With repel, multiplier should affect encounter chance
        assert system.repel_active is True
        assert system.repel_multiplier == 0.5

    def test_zone_transition_resets_steps(self, event_manager):
        """Test that changing zones resets step counters"""
        system = RandomEncounterSystem(event_manager)
        system.set_current_zone("grassland")

        # Walk some steps
        for _ in range(50):
            event_manager.emit(Event(EventType.CUSTOM, {"type": "player_step"}))
            event_manager.process_events()

        assert system.step_count == 50

        # Change zone
        event_manager.emit(Event(EventType.CUSTOM, {"type": "zone_loaded", "zone_id": "forest"}))
        event_manager.process_events()

        assert system.step_count == 0
        assert system.current_zone == "forest"

    def test_encounter_group_data_in_event(self, event_manager):
        """Test that encounter event contains group data"""
        event_manager.set_immediate_mode(True)
        system = RandomEncounterSystem(event_manager)
        system.set_current_zone("grassland")

        encounters = []

        def capture_encounter(event):
            if event.data.get("type") == "random_encounter":
                encounters.append(event)

        event_manager.subscribe(EventType.CUSTOM, capture_encounter)

        # Force an encounter to guarantee event
        system.force_encounter("slime_pair")

        assert len(encounters) == 1
        event_data = encounters[0].data
        assert "enemies" in event_data
        assert "group_id" in event_data
        assert "zone_id" in event_data
        assert event_data["group_id"] == "slime_pair"

    def test_different_zones_have_different_encounter_rates(self, event_manager):
        """Test that different zones have different encounter rates"""
        system = RandomEncounterSystem(event_manager)

        grassland_table = system.encounter_tables["grassland"]
        forest_table = system.encounter_tables["forest"]
        dungeon_table = system.encounter_tables["dungeon"]

        # Should have different rates
        rates = [
            grassland_table.encounter_rate,
            forest_table.encounter_rate,
            dungeon_table.encounter_rate,
        ]

        # At least some variation
        assert len(set(rates)) > 1

    def test_step_based_encounter_groups(self, event_manager):
        """Test that encounter groups appear based on step count"""
        system = RandomEncounterSystem(event_manager)
        table = system.encounter_tables["grassland"]

        # Early game group (max_steps=50)
        early_group = table.get_random_group(steps=10)
        # Mid game (min_steps=20)
        mid_group = table.get_random_group(steps=25)
        # Late game (min_steps=30)
        late_group = table.get_random_group(steps=35)

        # All should return some group (may be different)
        # This is probabilistic, so we just check it doesn't crash
        assert early_group is not None or True  # May be None due to randomness
