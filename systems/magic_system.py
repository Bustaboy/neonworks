"""
Magic System for JRPG-style Spell Casting

Handles spell casting, MP management, and magical effects.
"""

from typing import Dict, List, Optional

from neonworks.core.ecs import Entity, System, World
from neonworks.core.events import Event, EventManager, EventType
from neonworks.gameplay.combat import Health
from neonworks.gameplay.jrpg_combat import (
    ElementalResistances,
    ElementType,
    JRPGStats,
    MagicPoints,
    Spell,
    SpellList,
    TargetType,
)


class SpellDatabase:
    """Database of all available spells"""

    def __init__(self):
        self.spells: Dict[str, Spell] = {}
        self._register_default_spells()

    def register_spell(self, spell: Spell):
        """Register a spell"""
        self.spells[spell.spell_id] = spell

    def get_spell(self, spell_id: str) -> Optional[Spell]:
        """Get spell by ID"""
        return self.spells.get(spell_id)

    def _register_default_spells(self):
        """Register default spell set"""
        # Fire spells
        self.register_spell(
            Spell(
                spell_id="fire",
                name="Fire",
                description="Basic fire spell",
                mp_cost=5,
                power=20,
                element=ElementType.FIRE,
                target_type=TargetType.SINGLE_ENEMY,
                damage=20,
                animation="fire_small",
            )
        )

        self.register_spell(
            Spell(
                spell_id="fireball",
                name="Fireball",
                description="Powerful fire spell",
                mp_cost=15,
                power=50,
                element=ElementType.FIRE,
                target_type=TargetType.SINGLE_ENEMY,
                damage=50,
                animation="fire_medium",
            )
        )

        self.register_spell(
            Spell(
                spell_id="inferno",
                name="Inferno",
                description="Ultimate fire spell hitting all enemies",
                mp_cost=40,
                power=80,
                element=ElementType.FIRE,
                target_type=TargetType.ALL_ENEMIES,
                damage=80,
                animation="fire_large",
            )
        )

        # Ice spells
        self.register_spell(
            Spell(
                spell_id="ice",
                name="Ice",
                description="Basic ice spell",
                mp_cost=5,
                power=20,
                element=ElementType.ICE,
                target_type=TargetType.SINGLE_ENEMY,
                damage=20,
                animation="ice_small",
            )
        )

        self.register_spell(
            Spell(
                spell_id="blizzard",
                name="Blizzard",
                description="Powerful ice spell",
                mp_cost=15,
                power=50,
                element=ElementType.ICE,
                target_type=TargetType.SINGLE_ENEMY,
                damage=50,
                animation="ice_medium",
            )
        )

        # Lightning spells
        self.register_spell(
            Spell(
                spell_id="bolt",
                name="Bolt",
                description="Basic lightning spell",
                mp_cost=5,
                power=20,
                element=ElementType.LIGHTNING,
                target_type=TargetType.SINGLE_ENEMY,
                damage=20,
                animation="lightning_small",
            )
        )

        self.register_spell(
            Spell(
                spell_id="thunder",
                name="Thunder",
                description="Powerful lightning spell",
                mp_cost=15,
                power=50,
                element=ElementType.LIGHTNING,
                target_type=TargetType.SINGLE_ENEMY,
                damage=50,
                animation="lightning_medium",
            )
        )

        # Healing spells
        self.register_spell(
            Spell(
                spell_id="heal",
                name="Heal",
                description="Restore HP to one ally",
                mp_cost=7,
                power=30,
                element=ElementType.HOLY,
                target_type=TargetType.SINGLE_ALLY,
                healing=30,
                animation="heal_small",
            )
        )

        self.register_spell(
            Spell(
                spell_id="cure",
                name="Cure",
                description="Restore HP to all allies",
                mp_cost=20,
                power=20,
                element=ElementType.HOLY,
                target_type=TargetType.ALL_ALLIES,
                healing=20,
                animation="heal_medium",
            )
        )

        self.register_spell(
            Spell(
                spell_id="full_heal",
                name="Full Heal",
                description="Fully restore one ally's HP",
                mp_cost=40,
                power=999,
                element=ElementType.HOLY,
                target_type=TargetType.SINGLE_ALLY,
                healing=999,
                animation="heal_large",
            )
        )

        # Status spells
        self.register_spell(
            Spell(
                spell_id="poison",
                name="Poison",
                description="Poison one enemy",
                mp_cost=8,
                power=0,
                element=ElementType.NONE,
                target_type=TargetType.SINGLE_ENEMY,
                status_effect="poison",
                status_chance=75.0,
                animation="poison",
            )
        )

        self.register_spell(
            Spell(
                spell_id="sleep",
                name="Sleep",
                description="Put one enemy to sleep",
                mp_cost=10,
                power=0,
                element=ElementType.NONE,
                target_type=TargetType.SINGLE_ENEMY,
                status_effect="sleep",
                status_chance=60.0,
                animation="sleep",
            )
        )

        # Buff/Debuff spells
        self.register_spell(
            Spell(
                spell_id="protect",
                name="Protect",
                description="Increase defense of all allies",
                mp_cost=12,
                power=0,
                element=ElementType.NONE,
                target_type=TargetType.ALL_ALLIES,
                status_effect="protect",
                status_chance=100.0,
                animation="protect",
            )
        )


class MagicSystem(System):
    """
    System for handling magic casting and MP management.

    Features:
    - Spell casting with MP costs
    - Elemental damage calculations
    - Healing spells
    - Status effect spells
    - MP regeneration
    """

    def __init__(self, event_manager: EventManager):
        super().__init__()
        self.priority = 15
        self.event_manager = event_manager
        self.spell_db = SpellDatabase()

        # Subscribe to combat events
        self.event_manager.subscribe(EventType.CUSTOM, self._handle_custom_event)

    def update(self, world: World, delta_time: float):
        """Update magic system"""
        # Regenerate MP
        self._update_mp_regeneration(world, delta_time)

        # Reduce spell cooldowns (turn-based, handled elsewhere)
        pass

    def cast_spell(
        self, world: World, caster: Entity, spell_id: str, targets: List[Entity]
    ) -> bool:
        """
        Cast a spell from caster to targets.

        Args:
            world: ECS world
            caster: Entity casting the spell
            spell_id: ID of spell to cast
            targets: List of target entities

        Returns:
            True if spell was cast successfully
        """
        # Get caster components
        mp = caster.get_component(MagicPoints)
        spell_list = caster.get_component(SpellList)
        caster_stats = caster.get_component(JRPGStats)

        if not mp or not spell_list:
            return False

        # Check if spell is known
        if not spell_list.knows_spell(spell_id):
            return False

        # Get spell data
        spell = self.spell_db.get_spell(spell_id)
        if not spell:
            return False

        # Check if enough MP
        if not mp.consume_mp(spell.mp_cost):
            self.event_manager.emit(
                Event(
                    EventType.CUSTOM,
                    {
                        "type": "spell_failed",
                        "reason": "not_enough_mp",
                        "caster_id": caster.id,
                    },
                )
            )
            return False

        # Check cooldown
        if spell_list.is_on_cooldown(spell_id):
            return False

        # Apply spell effects to targets
        for target in targets:
            self._apply_spell_effect(caster, target, spell, caster_stats)

        # Emit spell cast event
        self.event_manager.emit(
            Event(
                EventType.CUSTOM,
                {
                    "type": "spell_cast",
                    "caster_id": caster.id,
                    "spell_id": spell_id,
                    "spell_name": spell.name,
                    "target_ids": [t.id for t in targets],
                    "mp_cost": spell.mp_cost,
                },
            )
        )

        return True

    def _apply_spell_effect(
        self,
        caster: Entity,
        target: Entity,
        spell: Spell,
        caster_stats: Optional[JRPGStats],
    ):
        """Apply spell effect to a single target"""
        target_health = target.get_component(Health)
        target_stats = target.get_component(JRPGStats)
        target_resist = target.get_component(ElementalResistances)

        # Damage spell
        if spell.damage > 0 and target_health:
            damage = spell.damage

            # Add caster's magic attack if available
            if caster_stats:
                damage = caster_stats.calculate_magic_damage(spell.power, target_stats)

            # Apply elemental resistance
            if target_resist:
                multiplier = target_resist.get_multiplier(spell.element)

                # Check for absorption
                if target_resist.absorbs(spell.element):
                    # Heal instead of damage
                    target_health.hp = min(
                        target_health.max_hp, target_health.hp + abs(damage)
                    )
                    self.event_manager.emit(
                        Event(
                            EventType.CUSTOM,
                            {
                                "type": "spell_absorbed",
                                "target_id": target.id,
                                "healing": abs(damage),
                                "element": spell.element.value,
                            },
                        )
                    )
                    return

                damage = int(damage * multiplier)

            # Apply damage
            target_health.hp -= damage

            # Check for death
            if target_health.hp <= 0:
                target_health.hp = 0
                target_health.is_alive = False

            # Emit damage event
            self.event_manager.emit(
                Event(
                    EventType.CUSTOM,
                    {
                        "type": "spell_damage",
                        "target_id": target.id,
                        "damage": damage,
                        "element": spell.element.value,
                        "spell_name": spell.name,
                    },
                )
            )

        # Healing spell
        if spell.healing > 0 and target_health:
            healing = spell.healing
            old_hp = target_health.hp
            target_health.hp = min(target_health.max_hp, target_health.hp + healing)
            actual_healing = target_health.hp - old_hp

            self.event_manager.emit(
                Event(
                    EventType.CUSTOM,
                    {
                        "type": "spell_heal",
                        "target_id": target.id,
                        "healing": actual_healing,
                        "spell_name": spell.name,
                    },
                )
            )

        # Status effect spell
        if spell.status_effect and target_stats:
            import random

            if random.random() * 100 < spell.status_chance:
                target_stats.add_status(spell.status_effect)

                self.event_manager.emit(
                    Event(
                        EventType.CUSTOM,
                        {
                            "type": "status_applied",
                            "target_id": target.id,
                            "status": spell.status_effect,
                            "spell_name": spell.name,
                        },
                    )
                )

    def _update_mp_regeneration(self, world: World, delta_time: float):
        """Update MP regeneration for all entities"""
        entities = world.get_entities_with_component(MagicPoints)

        for entity in entities:
            mp = entity.get_component(MagicPoints)

            if mp.mp_regen_rate > 0:
                # Regenerate MP (scaled by delta_time for real-time regen)
                regen_amount = int(mp.mp_regen_rate * delta_time)
                if regen_amount > 0:
                    mp.restore_mp(regen_amount)

    def restore_mp_item(self, target: Entity, amount: int):
        """Restore MP using an item"""
        mp = target.get_component(MagicPoints)
        if mp:
            mp.restore_mp(amount)

            self.event_manager.emit(
                Event(
                    EventType.CUSTOM,
                    {
                        "type": "mp_restored",
                        "target_id": target.id,
                        "amount": amount,
                    },
                )
            )

    def restore_mp_full(self, target: Entity):
        """Fully restore MP (e.g., at inn)"""
        mp = target.get_component(MagicPoints)
        if mp:
            mp.current_mp = mp.max_mp

            self.event_manager.emit(
                Event(
                    EventType.CUSTOM,
                    {
                        "type": "mp_restored_full",
                        "target_id": target.id,
                    },
                )
            )

    def learn_spell(self, entity: Entity, spell_id: str) -> bool:
        """Teach a spell to an entity"""
        spell_list = entity.get_component(SpellList)
        if not spell_list:
            return False

        # Check if spell exists
        spell = self.spell_db.get_spell(spell_id)
        if not spell:
            return False

        # Learn the spell
        spell_list.learn_spell(spell_id)

        self.event_manager.emit(
            Event(
                EventType.CUSTOM,
                {
                    "type": "spell_learned",
                    "entity_id": entity.id,
                    "spell_id": spell_id,
                    "spell_name": spell.name,
                },
            )
        )

        return True

    def _handle_custom_event(self, event: Event):
        """Handle custom events"""
        if not event.data:
            return

        event_type = event.data.get("type")

        # Handle turn end to reduce cooldowns
        if event_type == "turn_end":
            # Reduce cooldowns would be handled here
            pass

    def get_spell_database(self) -> SpellDatabase:
        """Get spell database"""
        return self.spell_db
