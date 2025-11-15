"""
Tests for Survival System

Tests hunger, thirst, energy mechanics and their effects on entities.
"""

import pytest

from neonworks.core.ecs import Entity, Health, Survival, World
from neonworks.core.events import Event, EventType, get_event_manager
from neonworks.systems.survival import SurvivalSystem


class TestSurvivalSystemBasics:
    """Test basic survival system functionality"""

    def test_survival_system_creation(self):
        """Test creating survival system"""
        system = SurvivalSystem()

        assert system is not None
        assert system.priority == -30
        assert system.critical_threshold == 20.0
        assert system.danger_threshold == 40.0

    def test_survival_system_thresholds(self):
        """Test survival damage rates"""
        system = SurvivalSystem()

        assert system.starvation_damage == 5.0
        assert system.dehydration_damage == 10.0
        assert system.exhaustion_damage == 3.0


class TestSurvivalNeeds:
    """Test survival needs decay and effects"""

    def test_needs_decay_over_time(self):
        """Test that survival needs decrease over time"""
        world = World()
        system = SurvivalSystem()

        entity = world.create_entity("Survivor")
        survival = Survival(hunger=100.0, thirst=100.0, energy=100.0)
        survival.hunger_rate = 1.0
        survival.thirst_rate = 2.0
        survival.energy_rate = 0.5
        entity.add_component(survival)

        # Update for 10 seconds
        system.update(world, 10.0)

        survival = entity.get_component(Survival)
        assert survival.hunger == 90.0  # 100 - (1.0 * 10)
        assert survival.thirst == 80.0  # 100 - (2.0 * 10)
        assert survival.energy == 95.0  # 100 - (0.5 * 10)

    def test_needs_cannot_go_below_zero(self):
        """Test that survival needs don't go negative"""
        world = World()
        system = SurvivalSystem()

        entity = world.create_entity("Survivor")
        survival = Survival(hunger=5.0, thirst=5.0, energy=5.0)
        survival.hunger_rate = 1.0
        survival.thirst_rate = 1.0
        survival.energy_rate = 1.0
        entity.add_component(survival)

        # Update for long enough to drain all needs
        system.update(world, 100.0)

        survival = entity.get_component(Survival)
        assert survival.hunger == 0.0
        assert survival.thirst == 0.0
        assert survival.energy == 0.0


class TestCriticalEvents:
    """Test critical need events"""

    def test_critical_hunger_event(self):
        """Test that critical hunger emits event"""
        world = World()
        system = SurvivalSystem()
        event_manager = get_event_manager()

        events_received = []
        def on_critical(event):
            events_received.append(event)

        event_manager.subscribe(EventType.HUNGER_CRITICAL, on_critical)

        entity = world.create_entity("Survivor")
        survival = Survival(hunger=15.0, thirst=100.0, energy=100.0)
        survival.hunger_rate = 0.0
        entity.add_component(survival)

        system.update(world, 1.0)
        event_manager.process_events()  # Process queued events

        assert len(events_received) > 0
        event_manager.unsubscribe(EventType.HUNGER_CRITICAL, on_critical)

    def test_critical_thirst_event(self):
        """Test that critical thirst emits event"""
        world = World()
        system = SurvivalSystem()
        event_manager = get_event_manager()

        events_received = []
        def on_critical(event):
            events_received.append(event)

        event_manager.subscribe(EventType.THIRST_CRITICAL, on_critical)

        entity = world.create_entity("Survivor")
        survival = Survival(hunger=100.0, thirst=15.0, energy=100.0)
        survival.thirst_rate = 0.0
        entity.add_component(survival)

        system.update(world, 1.0)
        event_manager.process_events()  # Process queued events

        assert len(events_received) > 0
        event_manager.unsubscribe(EventType.THIRST_CRITICAL, on_critical)

    def test_critical_energy_event(self):
        """Test that critical energy emits event"""
        world = World()
        system = SurvivalSystem()
        event_manager = get_event_manager()

        events_received = []
        def on_critical(event):
            events_received.append(event)

        event_manager.subscribe(EventType.ENERGY_DEPLETED, on_critical)

        entity = world.create_entity("Survivor")
        survival = Survival(hunger=100.0, thirst=100.0, energy=15.0)
        survival.energy_rate = 0.0
        entity.add_component(survival)

        system.update(world, 1.0)
        event_manager.process_events()  # Process queued events

        assert len(events_received) > 0
        event_manager.unsubscribe(EventType.ENERGY_DEPLETED, on_critical)


class TestSurvivalDamage:
    """Test damage from depleted survival needs"""

    def test_starvation_damage(self):
        """Test that zero hunger causes damage"""
        world = World()
        system = SurvivalSystem()

        entity = world.create_entity("Survivor")
        health = Health(current=100.0, maximum=100.0)
        survival = Survival(hunger=0.0, thirst=100.0, energy=100.0)
        survival.hunger_rate = 0.0
        entity.add_component(health)
        entity.add_component(survival)

        system.update(world, 1.0)

        health = entity.get_component(Health)
        assert health.current == 95.0  # 100 - 5.0 starvation damage

    def test_dehydration_damage(self):
        """Test that zero thirst causes damage"""
        world = World()
        system = SurvivalSystem()

        entity = world.create_entity("Survivor")
        health = Health(current=100.0, maximum=100.0)
        survival = Survival(hunger=100.0, thirst=0.0, energy=100.0)
        survival.thirst_rate = 0.0
        entity.add_component(health)
        entity.add_component(survival)

        system.update(world, 1.0)

        health = entity.get_component(Health)
        assert health.current == 90.0  # 100 - 10.0 dehydration damage

    def test_exhaustion_damage(self):
        """Test that zero energy causes damage"""
        world = World()
        system = SurvivalSystem()

        entity = world.create_entity("Survivor")
        health = Health(current=100.0, maximum=100.0)
        survival = Survival(hunger=100.0, thirst=100.0, energy=0.0)
        survival.energy_rate = 0.0
        entity.add_component(health)
        entity.add_component(survival)

        system.update(world, 1.0)

        health = entity.get_component(Health)
        assert health.current == 97.0  # 100 - 3.0 exhaustion damage

    def test_combined_damage(self):
        """Test that multiple depleted needs stack damage"""
        world = World()
        system = SurvivalSystem()

        entity = world.create_entity("Survivor")
        health = Health(current=100.0, maximum=100.0)
        survival = Survival(hunger=0.0, thirst=0.0, energy=0.0)
        survival.hunger_rate = 0.0
        survival.thirst_rate = 0.0
        survival.energy_rate = 0.0
        entity.add_component(health)
        entity.add_component(survival)

        system.update(world, 1.0)

        health = entity.get_component(Health)
        # 5.0 + 10.0 + 3.0 = 18.0 total damage
        assert health.current == 82.0

    def test_death_from_survival_needs(self):
        """Test that survival damage can kill entity"""
        world = World()
        system = SurvivalSystem()
        event_manager = get_event_manager()

        deaths = []
        def on_death(event):
            deaths.append(event)

        event_manager.subscribe(EventType.UNIT_DIED, on_death)

        entity = world.create_entity("Survivor")
        health = Health(current=10.0, maximum=100.0)
        survival = Survival(hunger=0.0, thirst=0.0, energy=0.0)
        survival.hunger_rate = 0.0
        survival.thirst_rate = 0.0
        survival.energy_rate = 0.0
        entity.add_component(health)
        entity.add_component(survival)

        system.update(world, 1.0)
        event_manager.process_events()  # Process queued events

        health = entity.get_component(Health)
        assert health.current == 0.0
        assert len(deaths) > 0
        assert deaths[0].data["cause"] == "survival_needs"

        event_manager.unsubscribe(EventType.UNIT_DIED, on_death)

    def test_no_damage_without_health_component(self):
        """Test that entities without Health don't take damage"""
        world = World()
        system = SurvivalSystem()

        entity = world.create_entity("Survivor")
        survival = Survival(hunger=0.0, thirst=0.0, energy=0.0)
        entity.add_component(survival)

        # Should not crash
        system.update(world, 1.0)


class TestConsumption:
    """Test consuming food, water, and rest"""

    def test_consume_food(self):
        """Test consuming food restores hunger"""
        world = World()
        system = SurvivalSystem()

        entity = world.create_entity("Survivor")
        survival = Survival(hunger=50.0, thirst=100.0, energy=100.0)
        entity.add_component(survival)

        system.consume_food(entity, 30.0)

        survival = entity.get_component(Survival)
        assert survival.hunger == 80.0

    def test_consume_food_cap_at_100(self):
        """Test that hunger caps at 100"""
        world = World()
        system = SurvivalSystem()

        entity = world.create_entity("Survivor")
        survival = Survival(hunger=90.0, thirst=100.0, energy=100.0)
        entity.add_component(survival)

        system.consume_food(entity, 50.0)

        survival = entity.get_component(Survival)
        assert survival.hunger == 100.0

    def test_consume_water(self):
        """Test consuming water restores thirst"""
        world = World()
        system = SurvivalSystem()

        entity = world.create_entity("Survivor")
        survival = Survival(hunger=100.0, thirst=50.0, energy=100.0)
        entity.add_component(survival)

        system.consume_water(entity, 30.0)

        survival = entity.get_component(Survival)
        assert survival.thirst == 80.0

    def test_consume_water_cap_at_100(self):
        """Test that thirst caps at 100"""
        world = World()
        system = SurvivalSystem()

        entity = world.create_entity("Survivor")
        survival = Survival(hunger=100.0, thirst=90.0, energy=100.0)
        entity.add_component(survival)

        system.consume_water(entity, 50.0)

        survival = entity.get_component(Survival)
        assert survival.thirst == 100.0

    def test_rest(self):
        """Test resting restores energy"""
        world = World()
        system = SurvivalSystem()

        entity = world.create_entity("Survivor")
        survival = Survival(hunger=100.0, thirst=100.0, energy=50.0)
        entity.add_component(survival)

        system.rest(entity, 30.0)

        survival = entity.get_component(Survival)
        assert survival.energy == 80.0

    def test_rest_cap_at_100(self):
        """Test that energy caps at 100"""
        world = World()
        system = SurvivalSystem()

        entity = world.create_entity("Survivor")
        survival = Survival(hunger=100.0, thirst=100.0, energy=90.0)
        entity.add_component(survival)

        system.rest(entity, 50.0)

        survival = entity.get_component(Survival)
        assert survival.energy == 100.0

    def test_consume_food_no_survival_component(self):
        """Test consuming food on entity without Survival component"""
        world = World()
        system = SurvivalSystem()

        entity = world.create_entity("Survivor")

        # Should not crash
        system.consume_food(entity, 50.0)

    def test_consume_water_no_survival_component(self):
        """Test consuming water on entity without Survival component"""
        world = World()
        system = SurvivalSystem()

        entity = world.create_entity("Survivor")

        # Should not crash
        system.consume_water(entity, 50.0)

    def test_rest_no_survival_component(self):
        """Test resting on entity without Survival component"""
        world = World()
        system = SurvivalSystem()

        entity = world.create_entity("Survivor")

        # Should not crash
        system.rest(entity, 50.0)


class TestSurvivalState:
    """Test survival state reporting"""

    def test_get_survival_state_healthy(self):
        """Test survival state when all needs are healthy"""
        world = World()
        system = SurvivalSystem()

        entity = world.create_entity("Survivor")
        survival = Survival(hunger=80.0, thirst=80.0, energy=80.0)
        entity.add_component(survival)

        state = system.get_survival_state(entity)

        assert state["hunger"]["value"] == 80.0
        assert state["hunger"]["state"] == "healthy"
        assert state["thirst"]["value"] == 80.0
        assert state["thirst"]["state"] == "healthy"
        assert state["energy"]["value"] == 80.0
        assert state["energy"]["state"] == "healthy"

    def test_get_survival_state_danger(self):
        """Test survival state when needs are in danger"""
        world = World()
        system = SurvivalSystem()

        entity = world.create_entity("Survivor")
        survival = Survival(hunger=30.0, thirst=30.0, energy=30.0)
        entity.add_component(survival)

        state = system.get_survival_state(entity)

        assert state["hunger"]["state"] == "danger"
        assert state["thirst"]["state"] == "danger"
        assert state["energy"]["state"] == "danger"

    def test_get_survival_state_critical(self):
        """Test survival state when needs are critical"""
        world = World()
        system = SurvivalSystem()

        entity = world.create_entity("Survivor")
        survival = Survival(hunger=10.0, thirst=10.0, energy=10.0)
        entity.add_component(survival)

        state = system.get_survival_state(entity)

        assert state["hunger"]["state"] == "critical"
        assert state["thirst"]["state"] == "critical"
        assert state["energy"]["state"] == "critical"

    def test_get_survival_state_no_component(self):
        """Test survival state when entity has no Survival component"""
        world = World()
        system = SurvivalSystem()

        entity = world.create_entity("Survivor")

        state = system.get_survival_state(entity)

        assert state == {}


class TestSurvivalIntegration:
    """Test survival system integration"""

    def test_multiple_entities(self):
        """Test survival system handles multiple entities"""
        world = World()
        system = SurvivalSystem()

        # Create multiple entities with different survival states
        entity1 = world.create_entity("Survivor1")
        survival1 = Survival(hunger=100.0, thirst=100.0, energy=100.0)
        survival1.hunger_rate = 1.0
        entity1.add_component(survival1)

        entity2 = world.create_entity("Survivor2")
        survival2 = Survival(hunger=50.0, thirst=50.0, energy=50.0)
        survival2.hunger_rate = 2.0
        entity2.add_component(survival2)

        system.update(world, 10.0)

        survival1 = entity1.get_component(Survival)
        survival2 = entity2.get_component(Survival)

        assert survival1.hunger == 90.0
        assert survival2.hunger == 30.0

    def test_survival_death_scenario(self):
        """Test complete survival death scenario"""
        world = World()
        system = SurvivalSystem()
        event_manager = get_event_manager()

        deaths = []
        def on_death(event):
            deaths.append(event)

        event_manager.subscribe(EventType.UNIT_DIED, on_death)

        entity = world.create_entity("Survivor")
        health = Health(current=50.0, maximum=100.0)
        survival = Survival(hunger=10.0, thirst=10.0, energy=10.0)
        survival.hunger_rate = 2.0
        survival.thirst_rate = 2.0
        survival.energy_rate = 2.0
        entity.add_component(health)
        entity.add_component(survival)

        # Update multiple times to drain needs and kill entity
        for _ in range(10):
            system.update(world, 1.0)
            event_manager.process_events()  # Process queued events
            health = entity.get_component(Health)
            if health.current <= 0:
                break

        assert health.current == 0.0
        assert len(deaths) > 0

        event_manager.unsubscribe(EventType.UNIT_DIED, on_death)
