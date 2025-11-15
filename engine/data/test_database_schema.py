"""
Test suite for database schema.

Run with: python -m pytest engine/data/test_database_schema.py -v
"""

import json
import tempfile
from pathlib import Path

import pytest

from neonworks.engine.data.database_schema import (
    Actor,
    Animation,
    Armor,
    ArmorType,
    Class,
    DamageType,
    DatabaseManager,
    DropItem,
    Effect,
    EffectTiming,
    EffectType,
    ElementType,
    Enemy,
    EquipType,
    Item,
    ItemType,
    Skill,
    SkillType,
    State,
    StateRestriction,
    Weapon,
    WeaponType,
)


class TestEffect:
    """Test Effect class."""

    def test_create_effect(self):
        """Test creating an effect."""
        effect = Effect(
            effect_type=EffectType.RECOVER_HP,
            value1=100.0,
            value2=50.0,
            timing=EffectTiming.IMMEDIATE,
            rate=1.0,
        )
        assert effect.effect_type == EffectType.RECOVER_HP
        assert effect.value1 == 100.0
        assert effect.validate()

    def test_effect_serialization(self):
        """Test effect to_dict and from_dict."""
        effect = Effect(effect_type=EffectType.ADD_STATE, value1=1.0, target_param=5, rate=0.75)
        data = effect.to_dict()
        restored = Effect.from_dict(data)

        assert restored.effect_type == effect.effect_type
        assert restored.value1 == effect.value1
        assert restored.target_param == effect.target_param
        assert restored.rate == effect.rate

    def test_effect_validation(self):
        """Test effect validation."""
        # Valid effect
        effect = Effect(value1=100, value2=50, rate=0.5)
        assert effect.validate()

        # Invalid rate
        effect.rate = 1.5
        assert not effect.validate()

        # Invalid value1
        effect.rate = 0.5
        effect.value1 = 10000
        assert not effect.validate()


class TestItem:
    """Test Item class."""

    def test_create_item(self):
        """Test creating an item."""
        item = Item(
            id=1,
            name="Potion",
            description="Restores 50 HP",
            price=50,
            consumable=True,
        )
        assert item.id == 1
        assert item.name == "Potion"
        assert item.consumable
        assert item.validate()

    def test_item_with_effects(self):
        """Test item with effects."""
        effect = Effect(effect_type=EffectType.RECOVER_HP, value1=50.0)
        item = Item(id=1, name="Potion", effects=[effect])

        assert len(item.effects) == 1
        assert item.effects[0].effect_type == EffectType.RECOVER_HP
        assert item.validate()

    def test_item_serialization(self):
        """Test item serialization."""
        effect1 = Effect(effect_type=EffectType.RECOVER_HP, value1=50.0)
        effect2 = Effect(effect_type=EffectType.RECOVER_MP, value1=30.0)
        item = Item(
            id=1,
            name="Elixir",
            description="Restores HP and MP",
            price=500,
            effects=[effect1, effect2],
        )

        data = item.to_dict()
        restored = Item.from_dict(data)

        assert restored.id == item.id
        assert restored.name == item.name
        assert len(restored.effects) == 2
        assert restored.effects[0].value1 == 50.0

    def test_item_validation(self):
        """Test item validation."""
        item = Item(id=1, name="Test", price=100)
        assert item.validate()

        # Invalid price
        item.price = -1
        assert not item.validate()

        item.price = 1000000
        assert not item.validate()


class TestSkill:
    """Test Skill class."""

    def test_create_skill(self):
        """Test creating a skill."""
        skill = Skill(
            id=1,
            name="Fireball",
            description="Fire magic",
            skill_type=SkillType.MAGIC,
            mp_cost=10,
            element_type=ElementType.FIRE,
        )
        assert skill.id == 1
        assert skill.name == "Fireball"
        assert skill.mp_cost == 10
        assert skill.validate()

    def test_skill_serialization(self):
        """Test skill serialization."""
        effect = Effect(effect_type=EffectType.DAMAGE_HP, value1=100.0)
        skill = Skill(
            id=5,
            name="Heal",
            mp_cost=15,
            damage_type=DamageType.HP_RECOVER,
            effects=[effect],
        )

        data = skill.to_dict()
        restored = Skill.from_dict(data)

        assert restored.id == skill.id
        assert restored.mp_cost == skill.mp_cost
        assert len(restored.effects) == 1


class TestWeapon:
    """Test Weapon class."""

    def test_create_weapon(self):
        """Test creating a weapon."""
        weapon = Weapon(
            id=1,
            name="Iron Sword",
            weapon_type=WeaponType.SWORD,
            price=1000,
            params=[10, 0, 0, 0, 0, 0],  # +10 ATK
        )
        assert weapon.id == 1
        assert weapon.weapon_type == WeaponType.SWORD
        assert weapon.params[0] == 10
        assert weapon.validate()

    def test_weapon_serialization(self):
        """Test weapon serialization."""
        weapon = Weapon(
            id=2, name="Steel Axe", weapon_type=WeaponType.AXE, params=[20, 0, 0, 5, 0, 0]
        )

        data = weapon.to_dict()
        restored = Weapon.from_dict(data)

        assert restored.weapon_type == WeaponType.AXE
        assert restored.params == weapon.params


class TestArmor:
    """Test Armor class."""

    def test_create_armor(self):
        """Test creating armor."""
        armor = Armor(
            id=1,
            name="Iron Shield",
            armor_type=ArmorType.SHIELD,
            equip_type=EquipType.SHIELD,
            params=[0, 5, 0, 0, 0, 0],  # +5 DEF
        )
        assert armor.id == 1
        assert armor.armor_type == ArmorType.SHIELD
        assert armor.validate()

    def test_armor_serialization(self):
        """Test armor serialization."""
        armor = Armor(
            id=3,
            name="Plate Mail",
            armor_type=ArmorType.BODY,
            params=[0, 30, 0, 10, -5, 0],
        )

        data = armor.to_dict()
        restored = Armor.from_dict(data)

        assert restored.armor_type == ArmorType.BODY
        assert restored.params == armor.params


class TestState:
    """Test State class."""

    def test_create_state(self):
        """Test creating a state."""
        state = State(
            id=1,
            name="Poison",
            description="Lose HP each turn",
            restriction=StateRestriction.NONE,
            min_turns=3,
            max_turns=5,
        )
        assert state.id == 1
        assert state.name == "Poison"
        assert state.validate()

    def test_state_serialization(self):
        """Test state serialization."""
        state = State(
            id=2,
            name="Sleep",
            restriction=StateRestriction.CANNOT_MOVE,
            priority=70,
            remove_by_damage=True,
        )

        data = state.to_dict()
        restored = State.from_dict(data)

        assert restored.restriction == StateRestriction.CANNOT_MOVE
        assert restored.remove_by_damage is True

    def test_state_validation(self):
        """Test state validation."""
        state = State(id=1, name="Test", min_turns=5, max_turns=3)
        assert not state.validate()  # min > max

        state.max_turns = 10
        assert state.validate()


class TestEnemy:
    """Test Enemy class."""

    def test_create_enemy(self):
        """Test creating an enemy."""
        enemy = Enemy(
            id=1,
            name="Goblin",
            params=[50, 0, 12, 8, 5, 5, 10, 5],  # HP, MP, ATK, DEF, MAT, MDF, AGI, LUK
            exp=25,
            gold=50,
        )
        assert enemy.id == 1
        assert enemy.name == "Goblin"
        assert enemy.params[0] == 50  # HP
        assert enemy.validate()

    def test_enemy_with_drops(self):
        """Test enemy with drop items."""
        drop1 = DropItem(kind=1, item_id=1, drop_rate=0.5)
        drop2 = DropItem(kind=2, item_id=5, drop_rate=0.1)

        enemy = Enemy(
            id=2, name="Dragon", params=[500, 0, 50, 40, 30, 30, 20, 15], drop_items=[drop1, drop2]
        )

        assert len(enemy.drop_items) == 2
        assert enemy.drop_items[0].drop_rate == 0.5
        assert enemy.validate()

    def test_enemy_serialization(self):
        """Test enemy serialization."""
        drop = DropItem(kind=1, item_id=3, drop_rate=0.25)
        enemy = Enemy(id=3, name="Slime", exp=10, gold=20, drop_items=[drop])

        data = enemy.to_dict()
        restored = Enemy.from_dict(data)

        assert restored.exp == enemy.exp
        assert len(restored.drop_items) == 1
        assert restored.drop_items[0].item_id == 3


class TestActor:
    """Test Actor class."""

    def test_create_actor(self):
        """Test creating an actor."""
        actor = Actor(
            id=1,
            name="Hero",
            nickname="The Brave",
            class_id=1,
            initial_level=1,
            max_level=99,
        )
        assert actor.id == 1
        assert actor.nickname == "The Brave"
        assert actor.validate()

    def test_actor_serialization(self):
        """Test actor serialization."""
        actor = Actor(
            id=2,
            name="Mage",
            class_id=2,
            initial_level=5,
            character_name="Actor1",
            character_index=1,
        )

        data = actor.to_dict()
        restored = Actor.from_dict(data)

        assert restored.class_id == actor.class_id
        assert restored.initial_level == actor.initial_level

    def test_actor_validation(self):
        """Test actor validation."""
        actor = Actor(id=1, name="Test", initial_level=50, max_level=40)
        assert not actor.validate()  # initial > max

        actor.max_level = 60
        assert actor.validate()


class TestClass:
    """Test Class."""

    def test_create_class(self):
        """Test creating a class."""
        cls = Class(
            id=1,
            name="Warrior",
            description="Strong melee fighter",
            exp_params=[30, 20, 30, 30],
        )
        assert cls.id == 1
        assert cls.name == "Warrior"
        assert cls.validate()

    def test_class_with_learnings(self):
        """Test class with skill learnings."""
        cls = Class(
            id=2,
            name="Mage",
            learnings=[
                {"level": 1, "skill_id": 1},
                {"level": 5, "skill_id": 2},
                {"level": 10, "skill_id": 3},
            ],
        )

        assert len(cls.learnings) == 3
        assert cls.learnings[0]["level"] == 1
        assert cls.validate()

    def test_class_serialization(self):
        """Test class serialization."""
        cls = Class(id=3, name="Thief", exp_params=[25, 15, 35, 35])

        data = cls.to_dict()
        restored = Class.from_dict(data)

        assert restored.exp_params == cls.exp_params


class TestAnimation:
    """Test Animation class."""

    def test_create_animation(self):
        """Test creating an animation."""
        anim = Animation(
            id=1,
            name="Slash",
            animation1_name="Attack1",
            position=1,
            frame_max=16,
        )
        assert anim.id == 1
        assert anim.name == "Slash"
        assert anim.validate()

    def test_animation_serialization(self):
        """Test animation serialization."""
        anim = Animation(id=2, name="Fire", animation1_name="Fire1", frame_max=24)

        data = anim.to_dict()
        restored = Animation.from_dict(data)

        assert restored.animation1_name == anim.animation1_name
        assert restored.frame_max == anim.frame_max


class TestDatabaseManager:
    """Test DatabaseManager."""

    def test_save_and_load(self):
        """Test saving and loading database."""
        manager = DatabaseManager()

        # Add some test data
        manager.items[1] = Item(id=1, name="Potion", price=50)
        manager.weapons[1] = Weapon(
            id=1, name="Sword", weapon_type=WeaponType.SWORD, params=[10, 0, 0, 0, 0, 0]
        )
        manager.enemies[1] = Enemy(id=1, name="Goblin", exp=25, gold=50)

        # Save to temp file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            temp_path = Path(f.name)

        try:
            manager.save_to_file(temp_path)

            # Load into new manager
            new_manager = DatabaseManager()
            assert new_manager.load_from_file(temp_path)

            # Verify data
            assert 1 in new_manager.items
            assert new_manager.items[1].name == "Potion"
            assert 1 in new_manager.weapons
            assert new_manager.weapons[1].weapon_type == WeaponType.SWORD
            assert 1 in new_manager.enemies
            assert new_manager.enemies[1].exp == 25

        finally:
            temp_path.unlink()

    def test_validate_all(self):
        """Test validation of all entries."""
        manager = DatabaseManager()

        # Add valid data
        manager.items[1] = Item(id=1, name="Valid Item", price=100)

        # Add invalid data
        manager.items[2] = Item(id=2, name="Invalid Item", price=-100)

        errors = manager.validate_all()
        assert "items" in errors
        assert len(errors["items"]) == 1
        assert "Item 2" in errors["items"][0]

    def test_clear(self):
        """Test clearing database."""
        manager = DatabaseManager()
        manager.items[1] = Item(id=1, name="Test")
        manager.weapons[1] = Weapon(id=1, name="Test")

        assert len(manager.items) == 1
        assert len(manager.weapons) == 1

        manager.clear()

        assert len(manager.items) == 0
        assert len(manager.weapons) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
