"""
Tests for Magic System

Tests spell casting, MP management, elemental damage, and healing.
"""

import pytest

from neonworks.core.ecs import Entity, World
from neonworks.core.events import Event, EventType, get_event_manager
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
from neonworks.systems.magic_system import MagicSystem, SpellDatabase


class TestSpellDatabase:
    """Test spell database"""

    def test_spell_database_creation(self):
        """Test creating spell database"""
        db = SpellDatabase()

        assert db is not None
        assert len(db.spells) > 0  # Has default spells

    def test_register_spell(self):
        """Test registering a custom spell"""
        db = SpellDatabase()

        custom_spell = Spell(
            spell_id="custom_spell",
            name="Custom Spell",
            description="A custom spell",
            mp_cost=10,
            power=25,
            element=ElementType.FIRE,
            target_type=TargetType.SINGLE_ENEMY,
            damage=25,
        )

        db.register_spell(custom_spell)

        assert "custom_spell" in db.spells
        assert db.spells["custom_spell"] == custom_spell

    def test_get_spell(self):
        """Test getting spell by ID"""
        db = SpellDatabase()

        fire_spell = db.get_spell("fire")

        assert fire_spell is not None
        assert fire_spell.name == "Fire"
        assert fire_spell.mp_cost == 5
        assert fire_spell.element == ElementType.FIRE

    def test_get_nonexistent_spell(self):
        """Test getting spell that doesn't exist"""
        db = SpellDatabase()

        spell = db.get_spell("nonexistent")

        assert spell is None

    def test_default_spells_registered(self):
        """Test that default spells are registered"""
        db = SpellDatabase()

        # Fire spells
        assert db.get_spell("fire") is not None
        assert db.get_spell("fireball") is not None
        assert db.get_spell("inferno") is not None

        # Ice spells
        assert db.get_spell("ice") is not None
        assert db.get_spell("blizzard") is not None

        # Lightning spells
        assert db.get_spell("bolt") is not None
        assert db.get_spell("thunder") is not None

        # Healing spells
        assert db.get_spell("heal") is not None
        assert db.get_spell("cure") is not None
        assert db.get_spell("full_heal") is not None

        # Status spells
        assert db.get_spell("poison") is not None
        assert db.get_spell("sleep") is not None

        # Buff spells
        assert db.get_spell("protect") is not None


class TestMagicSystemBasics:
    """Test basic magic system functionality"""

    def test_magic_system_creation(self):
        """Test creating magic system"""
        event_manager = get_event_manager()
        system = MagicSystem(event_manager)

        assert system is not None
        assert system.priority == 15
        assert system.spell_db is not None

    def test_get_spell_database(self):
        """Test getting spell database"""
        event_manager = get_event_manager()
        system = MagicSystem(event_manager)

        db = system.get_spell_database()

        assert db is not None
        assert isinstance(db, SpellDatabase)


class TestSpellCasting:
    """Test spell casting mechanics"""

    def test_cast_damage_spell(self):
        """Test casting a damage spell"""
        world = World()
        event_manager = get_event_manager()
        system = MagicSystem(event_manager)

        # Create caster
        caster = world.create_entity("Mage")
        mp = MagicPoints(current_mp=50, max_mp=100)
        spell_list = SpellList()
        spell_list.learn_spell("fire")
        caster.add_component(mp)
        caster.add_component(spell_list)

        # Create target
        target = world.create_entity("Enemy")
        health = Health(hp=100, max_hp=100)
        target.add_component(health)

        # Cast spell
        success = system.cast_spell(world, caster, "fire", [target])

        assert success is True
        assert mp.current_mp == 45  # 50 - 5 MP cost
        target_health = target.get_component(Health)
        assert target_health.hp < 100  # Took damage

    def test_cast_spell_not_enough_mp(self):
        """Test casting spell without enough MP"""
        world = World()
        event_manager = get_event_manager()
        system = MagicSystem(event_manager)

        # Create caster with low MP
        caster = world.create_entity("Mage")
        mp = MagicPoints(current_mp=2, max_mp=100)
        spell_list = SpellList()
        spell_list.learn_spell("fire")
        caster.add_component(mp)
        caster.add_component(spell_list)

        # Create target
        target = world.create_entity("Enemy")
        health = Health(hp=100, max_hp=100)
        target.add_component(health)

        # Try to cast spell (requires 5 MP)
        success = system.cast_spell(world, caster, "fire", [target])

        assert success is False
        assert mp.current_mp == 2  # MP unchanged

    def test_cast_unknown_spell(self):
        """Test casting a spell the caster doesn't know"""
        world = World()
        event_manager = get_event_manager()
        system = MagicSystem(event_manager)

        # Create caster who hasn't learned fireball
        caster = world.create_entity("Mage")
        mp = MagicPoints(current_mp=50, max_mp=100)
        spell_list = SpellList()
        # Don't learn fireball
        caster.add_component(mp)
        caster.add_component(spell_list)

        # Create target
        target = world.create_entity("Enemy")
        health = Health(hp=100, max_hp=100)
        target.add_component(health)

        # Try to cast unknown spell
        success = system.cast_spell(world, caster, "fireball", [target])

        assert success is False

    def test_cast_spell_without_mp_component(self):
        """Test casting spell on entity without MP component"""
        world = World()
        event_manager = get_event_manager()
        system = MagicSystem(event_manager)

        # Create caster without MP component
        caster = world.create_entity("Mage")
        spell_list = SpellList()
        spell_list.learn_spell("fire")
        caster.add_component(spell_list)

        # Create target
        target = world.create_entity("Enemy")
        health = Health(hp=100, max_hp=100)
        target.add_component(health)

        # Try to cast spell
        success = system.cast_spell(world, caster, "fire", [target])

        assert success is False

    def test_cast_spell_without_spell_list(self):
        """Test casting spell on entity without SpellList component"""
        world = World()
        event_manager = get_event_manager()
        system = MagicSystem(event_manager)

        # Create caster without SpellList
        caster = world.create_entity("Mage")
        mp = MagicPoints(current_mp=50, max_mp=100)
        caster.add_component(mp)

        # Create target
        target = world.create_entity("Enemy")
        health = Health(hp=100, max_hp=100)
        target.add_component(health)

        # Try to cast spell
        success = system.cast_spell(world, caster, "fire", [target])

        assert success is False

    def test_cast_nonexistent_spell(self):
        """Test casting a spell that doesn't exist in database"""
        world = World()
        event_manager = get_event_manager()
        system = MagicSystem(event_manager)

        # Create caster
        caster = world.create_entity("Mage")
        mp = MagicPoints(current_mp=50, max_mp=100)
        spell_list = SpellList()
        spell_list.learn_spell("nonexistent_spell")  # Learn invalid spell
        caster.add_component(mp)
        caster.add_component(spell_list)

        # Create target
        target = world.create_entity("Enemy")
        health = Health(hp=100, max_hp=100)
        target.add_component(health)

        # Try to cast nonexistent spell
        success = system.cast_spell(world, caster, "nonexistent_spell", [target])

        assert success is False


class TestHealingSpells:
    """Test healing spell mechanics"""

    def test_cast_healing_spell(self):
        """Test casting a healing spell"""
        world = World()
        event_manager = get_event_manager()
        system = MagicSystem(event_manager)

        # Create caster
        caster = world.create_entity("Healer")
        mp = MagicPoints(current_mp=50, max_mp=100)
        spell_list = SpellList()
        spell_list.learn_spell("heal")
        caster.add_component(mp)
        caster.add_component(spell_list)

        # Create target (wounded ally)
        target = world.create_entity("Ally")
        health = Health(hp=50, max_hp=100)
        target.add_component(health)

        # Cast healing spell
        success = system.cast_spell(world, caster, "heal", [target])

        assert success is True
        target_health = target.get_component(Health)
        assert target_health.hp == 80  # 50 + 30 healing

    def test_healing_spell_caps_at_max_hp(self):
        """Test that healing doesn't exceed max HP"""
        world = World()
        event_manager = get_event_manager()
        system = MagicSystem(event_manager)

        # Create caster
        caster = world.create_entity("Healer")
        mp = MagicPoints(current_mp=50, max_mp=100)
        spell_list = SpellList()
        spell_list.learn_spell("heal")
        caster.add_component(mp)
        caster.add_component(spell_list)

        # Create target (nearly full HP)
        target = world.create_entity("Ally")
        health = Health(hp=95, max_hp=100)
        target.add_component(health)

        # Cast healing spell
        system.cast_spell(world, caster, "heal", [target])

        target_health = target.get_component(Health)
        assert target_health.hp == 100  # Capped at max

    def test_full_heal_spell(self):
        """Test full heal spell"""
        world = World()
        event_manager = get_event_manager()
        system = MagicSystem(event_manager)

        # Create caster
        caster = world.create_entity("Healer")
        mp = MagicPoints(current_mp=100, max_mp=100)
        spell_list = SpellList()
        spell_list.learn_spell("full_heal")
        caster.add_component(mp)
        caster.add_component(spell_list)

        # Create target (low HP)
        target = world.create_entity("Ally")
        health = Health(hp=10, max_hp=100)
        target.add_component(health)

        # Cast full heal
        system.cast_spell(world, caster, "full_heal", [target])

        target_health = target.get_component(Health)
        assert target_health.hp == 100  # Fully healed


class TestElementalDamage:
    """Test elemental damage and resistances"""

    def test_elemental_weakness(self):
        """Test spell damage with elemental weakness"""
        world = World()
        event_manager = get_event_manager()
        system = MagicSystem(event_manager)

        # Create caster
        caster = world.create_entity("Mage")
        mp = MagicPoints(current_mp=50, max_mp=100)
        spell_list = SpellList()
        spell_list.learn_spell("fire")
        caster.add_component(mp)
        caster.add_component(spell_list)

        # Create target weak to fire
        target = world.create_entity("IceMonster")
        health = Health(hp=100, max_hp=100)
        resistances = ElementalResistances()
        resistances.resistances[ElementType.FIRE] = 2.0  # 2x damage (weakness)
        target.add_component(health)
        target.add_component(resistances)

        # Cast fire spell
        system.cast_spell(world, caster, "fire", [target])

        target_health = target.get_component(Health)
        # Should take more damage due to weakness
        assert target_health.hp < 80  # Base damage is 20, with weakness should be 40

    def test_elemental_resistance(self):
        """Test spell damage with elemental resistance"""
        world = World()
        event_manager = get_event_manager()
        system = MagicSystem(event_manager)

        # Create caster
        caster = world.create_entity("Mage")
        mp = MagicPoints(current_mp=50, max_mp=100)
        spell_list = SpellList()
        spell_list.learn_spell("fire")
        caster.add_component(mp)
        caster.add_component(spell_list)

        # Create target resistant to fire
        target = world.create_entity("FireMonster")
        health = Health(hp=100, max_hp=100)
        resistances = ElementalResistances()
        resistances.resistances[ElementType.FIRE] = 0.5  # 50% damage (resistance)
        target.add_component(health)
        target.add_component(resistances)

        # Cast fire spell
        system.cast_spell(world, caster, "fire", [target])

        target_health = target.get_component(Health)
        # Should take less damage due to resistance
        assert target_health.hp > 80  # Reduced damage

    def test_elemental_absorption(self):
        """Test spell absorption healing target"""
        world = World()
        event_manager = get_event_manager()
        system = MagicSystem(event_manager)

        # Create caster
        caster = world.create_entity("Mage")
        mp = MagicPoints(current_mp=50, max_mp=100)
        spell_list = SpellList()
        spell_list.learn_spell("fire")
        caster.add_component(mp)
        caster.add_component(spell_list)

        # Create target that absorbs fire
        target = world.create_entity("FireElemental")
        health = Health(hp=80, max_hp=100)
        resistances = ElementalResistances()
        resistances.resistances[ElementType.FIRE] = -1.0  # Absorption (heals)
        target.add_component(health)
        target.add_component(resistances)

        # Cast fire spell
        system.cast_spell(world, caster, "fire", [target])

        target_health = target.get_component(Health)
        # Should heal instead of taking damage
        assert target_health.hp > 80


class TestMPManagement:
    """Test MP regeneration and restoration"""

    def test_mp_regeneration(self):
        """Test MP regeneration over time"""
        world = World()
        event_manager = get_event_manager()
        system = MagicSystem(event_manager)

        # Create entity with MP regen
        entity = world.create_entity("Mage")
        mp = MagicPoints(current_mp=50, max_mp=100, mp_regen_rate=5)
        entity.add_component(mp)

        # Update for 2 seconds (5 MP/s * 2s = 10 MP)
        system.update(world, 2.0)

        mp = entity.get_component(MagicPoints)
        assert mp.current_mp == 60  # 50 + 10

    def test_mp_regeneration_caps_at_max(self):
        """Test that MP regen doesn't exceed max"""
        world = World()
        event_manager = get_event_manager()
        system = MagicSystem(event_manager)

        # Create entity with high MP regen
        entity = world.create_entity("Mage")
        mp = MagicPoints(current_mp=95, max_mp=100, mp_regen_rate=10)
        entity.add_component(mp)

        # Update for long time
        system.update(world, 10.0)

        mp = entity.get_component(MagicPoints)
        assert mp.current_mp == 100  # Capped at max

    def test_restore_mp_item(self):
        """Test restoring MP with an item"""
        world = World()
        event_manager = get_event_manager()
        system = MagicSystem(event_manager)

        # Create entity
        entity = world.create_entity("Mage")
        mp = MagicPoints(current_mp=30, max_mp=100)
        entity.add_component(mp)

        # Use MP restoration item
        system.restore_mp_item(entity, 25)

        mp = entity.get_component(MagicPoints)
        assert mp.current_mp == 55  # 30 + 25

    def test_restore_mp_full(self):
        """Test fully restoring MP"""
        world = World()
        event_manager = get_event_manager()
        system = MagicSystem(event_manager)

        # Create entity
        entity = world.create_entity("Mage")
        mp = MagicPoints(current_mp=10, max_mp=100)
        entity.add_component(mp)

        # Fully restore MP
        system.restore_mp_full(entity)

        mp = entity.get_component(MagicPoints)
        assert mp.current_mp == 100  # Fully restored

    def test_restore_mp_without_component(self):
        """Test restoring MP on entity without MagicPoints component"""
        world = World()
        event_manager = get_event_manager()
        system = MagicSystem(event_manager)

        # Create entity without MP
        entity = world.create_entity("Warrior")

        # Should not crash
        system.restore_mp_item(entity, 25)
        system.restore_mp_full(entity)


class TestLearningSpells:
    """Test learning and knowing spells"""

    def test_learn_spell(self):
        """Test learning a new spell"""
        world = World()
        event_manager = get_event_manager()
        system = MagicSystem(event_manager)

        # Create entity
        entity = world.create_entity("Mage")
        spell_list = SpellList()
        entity.add_component(spell_list)

        # Learn spell
        success = system.learn_spell(entity, "fireball")

        assert success is True
        spell_list = entity.get_component(SpellList)
        assert spell_list.knows_spell("fireball")

    def test_learn_nonexistent_spell(self):
        """Test learning a spell that doesn't exist"""
        world = World()
        event_manager = get_event_manager()
        system = MagicSystem(event_manager)

        # Create entity
        entity = world.create_entity("Mage")
        spell_list = SpellList()
        entity.add_component(spell_list)

        # Try to learn nonexistent spell
        success = system.learn_spell(entity, "nonexistent")

        assert success is False

    def test_learn_spell_without_component(self):
        """Test learning spell on entity without SpellList"""
        world = World()
        event_manager = get_event_manager()
        system = MagicSystem(event_manager)

        # Create entity without spell list
        entity = world.create_entity("Warrior")

        # Try to learn spell
        success = system.learn_spell(entity, "fireball")

        assert success is False


class TestSpellEvents:
    """Test spell-related events"""

    def test_spell_cast_event(self):
        """Test that spell cast emits event"""
        world = World()
        event_manager = get_event_manager()
        system = MagicSystem(event_manager)

        events = []

        def on_custom(event):
            if event.data.get("type") == "spell_cast":
                events.append(event)

        event_manager.subscribe(EventType.CUSTOM, on_custom)

        # Create caster and target
        caster = world.create_entity("Mage")
        mp = MagicPoints(current_mp=50, max_mp=100)
        spell_list = SpellList()
        spell_list.learn_spell("fire")
        caster.add_component(mp)
        caster.add_component(spell_list)

        target = world.create_entity("Enemy")
        health = Health(hp=100, max_hp=100)
        target.add_component(health)

        # Cast spell
        system.cast_spell(world, caster, "fire", [target])
        event_manager.process_events()

        assert len(events) > 0
        assert events[0].data["spell_id"] == "fire"

        event_manager.unsubscribe(EventType.CUSTOM, on_custom)

    def test_spell_damage_event(self):
        """Test that spell damage emits event"""
        world = World()
        event_manager = get_event_manager()
        system = MagicSystem(event_manager)

        events = []

        def on_custom(event):
            if event.data.get("type") == "spell_damage":
                events.append(event)

        event_manager.subscribe(EventType.CUSTOM, on_custom)

        # Create caster and target
        caster = world.create_entity("Mage")
        mp = MagicPoints(current_mp=50, max_mp=100)
        spell_list = SpellList()
        spell_list.learn_spell("fire")
        caster.add_component(mp)
        caster.add_component(spell_list)

        target = world.create_entity("Enemy")
        health = Health(hp=100, max_hp=100)
        target.add_component(health)

        # Cast damage spell
        system.cast_spell(world, caster, "fire", [target])
        event_manager.process_events()

        assert len(events) > 0
        assert events[0].data["damage"] > 0

        event_manager.unsubscribe(EventType.CUSTOM, on_custom)

    def test_spell_heal_event(self):
        """Test that spell healing emits event"""
        world = World()
        event_manager = get_event_manager()
        system = MagicSystem(event_manager)

        events = []

        def on_custom(event):
            if event.data.get("type") == "spell_heal":
                events.append(event)

        event_manager.subscribe(EventType.CUSTOM, on_custom)

        # Create caster and target
        caster = world.create_entity("Healer")
        mp = MagicPoints(current_mp=50, max_mp=100)
        spell_list = SpellList()
        spell_list.learn_spell("heal")
        caster.add_component(mp)
        caster.add_component(spell_list)

        target = world.create_entity("Ally")
        health = Health(hp=50, max_hp=100)
        target.add_component(health)

        # Cast healing spell
        system.cast_spell(world, caster, "heal", [target])
        event_manager.process_events()

        assert len(events) > 0
        assert events[0].data["healing"] > 0

        event_manager.unsubscribe(EventType.CUSTOM, on_custom)


class TestMultiTargetSpells:
    """Test spells that target multiple enemies"""

    def test_area_damage_spell(self):
        """Test spell that hits all enemies"""
        world = World()
        event_manager = get_event_manager()
        system = MagicSystem(event_manager)

        # Create caster
        caster = world.create_entity("Mage")
        mp = MagicPoints(current_mp=100, max_mp=100)
        spell_list = SpellList()
        spell_list.learn_spell("inferno")  # Hits all enemies
        caster.add_component(mp)
        caster.add_component(spell_list)

        # Create multiple targets
        target1 = world.create_entity("Enemy1")
        health1 = Health(hp=100, max_hp=100)
        target1.add_component(health1)

        target2 = world.create_entity("Enemy2")
        health2 = Health(hp=100, max_hp=100)
        target2.add_component(health2)

        target3 = world.create_entity("Enemy3")
        health3 = Health(hp=100, max_hp=100)
        target3.add_component(health3)

        # Cast area spell
        system.cast_spell(world, caster, "inferno", [target1, target2, target3])

        # All targets should take damage
        assert target1.get_component(Health).hp < 100
        assert target2.get_component(Health).hp < 100
        assert target3.get_component(Health).hp < 100

    def test_area_heal_spell(self):
        """Test spell that heals all allies"""
        world = World()
        event_manager = get_event_manager()
        system = MagicSystem(event_manager)

        # Create caster
        caster = world.create_entity("Healer")
        mp = MagicPoints(current_mp=100, max_mp=100)
        spell_list = SpellList()
        spell_list.learn_spell("cure")  # Heals all allies
        caster.add_component(mp)
        caster.add_component(spell_list)

        # Create multiple wounded allies
        ally1 = world.create_entity("Ally1")
        health1 = Health(hp=50, max_hp=100)
        ally1.add_component(health1)

        ally2 = world.create_entity("Ally2")
        health2 = Health(hp=60, max_hp=100)
        ally2.add_component(health2)

        # Cast area heal
        system.cast_spell(world, caster, "cure", [ally1, ally2])

        # All allies should be healed
        assert ally1.get_component(Health).hp == 70  # 50 + 20
        assert ally2.get_component(Health).hp == 80  # 60 + 20
