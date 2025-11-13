"""
Survival System

Manages survival needs: hunger, thirst, energy, and their effects on entities.
"""

from neonworks.core.ecs import Entity, Health, Survival, System, World
from neonworks.core.events import (Event, EventManager, EventType,
                                   get_event_manager)


class SurvivalSystem(System):
    """Manages survival mechanics"""

    def __init__(self):
        super().__init__()
        self.priority = -30

        self.event_manager = get_event_manager()

        # Thresholds for critical states
        self.critical_threshold = 20.0
        self.danger_threshold = 40.0

        # Damage rates when needs are critical
        self.starvation_damage = 5.0  # Per turn
        self.dehydration_damage = 10.0  # Per turn (more severe)
        self.exhaustion_damage = 3.0  # Per turn

    def update(self, world: World, delta_time: float):
        """Update survival needs"""
        entities = world.get_entities_with_component(Survival)

        for entity in entities:
            survival = entity.get_component(Survival)
            self._update_needs(entity, survival, delta_time)
            self._apply_effects(entity, survival)

    def _update_needs(self, entity: Entity, survival: Survival, delta_time: float):
        """Update survival need values"""
        # Decay needs over time
        survival.hunger = max(0.0, survival.hunger - survival.hunger_rate * delta_time)
        survival.thirst = max(0.0, survival.thirst - survival.thirst_rate * delta_time)
        survival.energy = max(0.0, survival.energy - survival.energy_rate * delta_time)

        # Emit events when needs become critical
        if survival.hunger <= self.critical_threshold:
            self._emit_critical_event(entity, "hunger", survival.hunger)

        if survival.thirst <= self.critical_threshold:
            self._emit_critical_event(entity, "thirst", survival.thirst)

        if survival.energy <= self.critical_threshold:
            self._emit_critical_event(entity, "energy", survival.energy)

    def _apply_effects(self, entity: Entity, survival: Survival):
        """Apply effects based on survival state"""
        health = entity.get_component(Health)
        if not health:
            return

        # Apply damage when needs are critical
        total_damage = 0.0

        if survival.hunger <= 0.0:
            total_damage += self.starvation_damage

        if survival.thirst <= 0.0:
            total_damage += self.dehydration_damage

        if survival.energy <= 0.0:
            total_damage += self.exhaustion_damage

        if total_damage > 0:
            self._apply_damage(entity, health, total_damage)

    def _apply_damage(self, entity: Entity, health: Health, damage: float):
        """Apply damage to entity"""
        health.current = max(0.0, health.current - damage)

        if health.current <= 0.0:
            # Entity died
            self.event_manager.emit(
                Event(
                    EventType.UNIT_DIED,
                    {"entity_id": entity.id, "cause": "survival_needs"},
                )
            )

    def _emit_critical_event(self, entity: Entity, need_type: str, value: float):
        """Emit critical need event"""
        event_types = {
            "hunger": EventType.HUNGER_CRITICAL,
            "thirst": EventType.THIRST_CRITICAL,
            "energy": EventType.ENERGY_DEPLETED,
        }

        if need_type in event_types:
            self.event_manager.emit(
                Event(event_types[need_type], {"entity_id": entity.id, "value": value})
            )

    def consume_food(self, entity: Entity, amount: float):
        """Consume food to restore hunger"""
        survival = entity.get_component(Survival)
        if survival:
            survival.hunger = min(100.0, survival.hunger + amount)

    def consume_water(self, entity: Entity, amount: float):
        """Consume water to restore thirst"""
        survival = entity.get_component(Survival)
        if survival:
            survival.thirst = min(100.0, survival.thirst + amount)

    def rest(self, entity: Entity, amount: float):
        """Rest to restore energy"""
        survival = entity.get_component(Survival)
        if survival:
            survival.energy = min(100.0, survival.energy + amount)

    def get_survival_state(self, entity: Entity) -> dict:
        """Get survival state summary"""
        survival = entity.get_component(Survival)
        if not survival:
            return {}

        def get_state(value: float) -> str:
            if value > self.danger_threshold:
                return "healthy"
            elif value > self.critical_threshold:
                return "danger"
            else:
                return "critical"

        return {
            "hunger": {"value": survival.hunger, "state": get_state(survival.hunger)},
            "thirst": {"value": survival.thirst, "state": get_state(survival.thirst)},
            "energy": {"value": survival.energy, "state": get_state(survival.energy)},
        }
