"""
Example Database Creation
==========================

This script demonstrates how to create and populate a game database
using the database schema classes.

Run with: python engine/data/example_database.py
"""

from pathlib import Path

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


def create_example_database() -> DatabaseManager:
    """Create an example database with sample game data."""
    manager = DatabaseManager()

    # =========================================================================
    # Items
    # =========================================================================
    print("Creating items...")

    # Potion - restores 50 HP
    manager.items[1] = Item(
        id=1,
        name="Potion",
        icon_index=1,
        description="Restores 50 HP",
        price=50,
        consumable=True,
        scope=3,  # One ally
        effects=[Effect(effect_type=EffectType.RECOVER_HP, value1=50.0)],
    )

    # Hi-Potion - restores 200 HP
    manager.items[2] = Item(
        id=2,
        name="Hi-Potion",
        icon_index=2,
        description="Restores 200 HP",
        price=200,
        consumable=True,
        scope=3,
        effects=[Effect(effect_type=EffectType.RECOVER_HP, value1=200.0)],
    )

    # Elixir - fully restores HP and MP
    manager.items[3] = Item(
        id=3,
        name="Elixir",
        icon_index=3,
        description="Fully restores HP and MP",
        price=500,
        consumable=True,
        scope=3,
        effects=[
            Effect(effect_type=EffectType.RECOVER_HP, value1=999.0),
            Effect(effect_type=EffectType.RECOVER_MP, value1=999.0),
        ],
    )

    # Antidote - removes poison
    manager.items[4] = Item(
        id=4,
        name="Antidote",
        icon_index=4,
        description="Cures poison",
        price=30,
        consumable=True,
        scope=3,
        effects=[Effect(effect_type=EffectType.REMOVE_STATE, target_param=1)],
    )

    print(f"  Created {len(manager.items)} items")

    # =========================================================================
    # Skills
    # =========================================================================
    print("Creating skills...")

    # Attack - basic physical attack
    manager.skills[1] = Skill(
        id=1,
        name="Attack",
        icon_index=76,
        description="Basic physical attack",
        skill_type=SkillType.PHYSICAL,
        mp_cost=0,
        damage_type=DamageType.HP_DAMAGE,
        hit_type=1,  # Physical
        animation_id=1,
    )

    # Heal - restores HP
    manager.skills[2] = Skill(
        id=2,
        name="Heal",
        icon_index=64,
        description="Restores ally HP",
        skill_type=SkillType.MAGIC,
        mp_cost=10,
        scope=3,  # One ally
        damage_type=DamageType.HP_RECOVER,
        animation_id=2,
        effects=[Effect(effect_type=EffectType.RECOVER_HP, value1=100.0)],
    )

    # Fireball - fire magic attack
    manager.skills[3] = Skill(
        id=3,
        name="Fireball",
        icon_index=65,
        description="Fire magic attack",
        skill_type=SkillType.MAGIC,
        mp_cost=15,
        scope=1,  # One enemy
        damage_type=DamageType.HP_DAMAGE,
        element_type=ElementType.FIRE,
        hit_type=2,  # Magical
        animation_id=3,
    )

    # Ice Storm - ice magic attack all enemies
    manager.skills[4] = Skill(
        id=4,
        name="Ice Storm",
        icon_index=66,
        description="Ice attack on all enemies",
        skill_type=SkillType.MAGIC,
        mp_cost=30,
        scope=2,  # All enemies
        damage_type=DamageType.HP_DAMAGE,
        element_type=ElementType.ICE,
        hit_type=2,
        animation_id=4,
    )

    print(f"  Created {len(manager.skills)} skills")

    # =========================================================================
    # Weapons
    # =========================================================================
    print("Creating weapons...")

    # Wooden Sword
    manager.weapons[1] = Weapon(
        id=1,
        name="Wooden Sword",
        icon_index=96,
        description="Basic wooden sword",
        weapon_type=WeaponType.SWORD,
        price=100,
        animation_id=1,
        params=[5, 0, 0, 0, 0, 0],  # +5 ATK
    )

    # Iron Sword
    manager.weapons[2] = Weapon(
        id=2,
        name="Iron Sword",
        icon_index=97,
        description="Standard iron sword",
        weapon_type=WeaponType.SWORD,
        price=500,
        animation_id=1,
        params=[15, 0, 0, 0, 0, 0],  # +15 ATK
    )

    # Steel Axe
    manager.weapons[3] = Weapon(
        id=3,
        name="Steel Axe",
        icon_index=98,
        description="Heavy steel axe",
        weapon_type=WeaponType.AXE,
        price=800,
        animation_id=5,
        params=[25, 0, 0, 0, -5, 0],  # +25 ATK, -5 AGI
    )

    print(f"  Created {len(manager.weapons)} weapons")

    # =========================================================================
    # Armor
    # =========================================================================
    print("Creating armor...")

    # Leather Armor
    manager.armors[1] = Armor(
        id=1,
        name="Leather Armor",
        icon_index=128,
        description="Basic leather protection",
        armor_type=ArmorType.BODY,
        equip_type=EquipType.BODY,
        price=200,
        params=[0, 10, 0, 5, 0, 0],  # +10 DEF, +5 MDF
    )

    # Iron Shield
    manager.armors[2] = Armor(
        id=2,
        name="Iron Shield",
        icon_index=129,
        description="Standard iron shield",
        armor_type=ArmorType.SHIELD,
        equip_type=EquipType.SHIELD,
        price=300,
        params=[0, 15, 0, 5, 0, 0],  # +15 DEF, +5 MDF
    )

    print(f"  Created {len(manager.armors)} armor pieces")

    # =========================================================================
    # States
    # =========================================================================
    print("Creating states...")

    # Poison - lose HP each turn
    manager.states[1] = State(
        id=1,
        name="Poison",
        icon_index=16,
        description="Lose HP each turn",
        restriction=StateRestriction.NONE,
        priority=50,
        remove_at_battle_end=True,
        min_turns=3,
        max_turns=5,
        message1="%1 was poisoned!",
        message2="%1 is no longer poisoned.",
    )

    # Sleep - cannot act
    manager.states[2] = State(
        id=2,
        name="Sleep",
        icon_index=17,
        description="Cannot take action",
        restriction=StateRestriction.CANNOT_MOVE,
        priority=60,
        remove_by_damage=True,
        chance_by_damage=100,
        min_turns=2,
        max_turns=3,
        message1="%1 fell asleep!",
        message2="%1 woke up!",
    )

    print(f"  Created {len(manager.states)} states")

    # =========================================================================
    # Enemies
    # =========================================================================
    print("Creating enemies...")

    # Slime - basic enemy
    manager.enemies[1] = Enemy(
        id=1,
        name="Slime",
        icon_index=0,
        description="Weak gelatinous monster",
        battler_name="Slime",
        params=[30, 0, 8, 5, 5, 5, 8, 5],  # HP, MP, ATK, DEF, MAT, MDF, AGI, LUK
        exp=10,
        gold=20,
        drop_items=[DropItem(kind=1, item_id=1, drop_rate=0.3)],  # 30% potion drop
    )

    # Goblin - medium enemy
    manager.enemies[2] = Enemy(
        id=2,
        name="Goblin",
        icon_index=1,
        description="Small but fierce creature",
        battler_name="Goblin",
        params=[50, 0, 12, 8, 5, 5, 10, 5],
        exp=25,
        gold=50,
        drop_items=[
            DropItem(kind=1, item_id=1, drop_rate=0.5),  # 50% potion
            DropItem(kind=2, item_id=1, drop_rate=0.1),  # 10% wooden sword
        ],
    )

    # Dragon - boss enemy
    manager.enemies[3] = Enemy(
        id=3,
        name="Dragon",
        icon_index=2,
        description="Mighty fire-breathing dragon",
        battler_name="Dragon",
        params=[500, 100, 50, 40, 40, 30, 20, 15],
        exp=500,
        gold=1000,
        drop_items=[
            DropItem(kind=1, item_id=3, drop_rate=1.0),  # 100% elixir
            DropItem(kind=2, item_id=3, drop_rate=0.25),  # 25% steel axe
        ],
    )

    print(f"  Created {len(manager.enemies)} enemies")

    # =========================================================================
    # Actors
    # =========================================================================
    print("Creating actors...")

    # Hero - warrior class
    manager.actors[1] = Actor(
        id=1,
        name="Hero",
        nickname="The Brave",
        class_id=1,
        initial_level=1,
        max_level=99,
        character_name="Actor1",
        character_index=0,
        face_name="Actor1",
        face_index=0,
        equips=[1, 2, 0, 1, 0],  # Wooden sword, Iron shield, Leather armor
    )

    # Mage - mage class
    manager.actors[2] = Actor(
        id=2,
        name="Mage",
        nickname="The Wise",
        class_id=2,
        initial_level=1,
        max_level=99,
        character_name="Actor2",
        character_index=1,
        face_name="Actor2",
        face_index=1,
    )

    print(f"  Created {len(manager.actors)} actors")

    # =========================================================================
    # Classes
    # =========================================================================
    print("Creating classes...")

    # Warrior - physical fighter
    manager.classes[1] = Class(
        id=1,
        name="Warrior",
        icon_index=0,
        description="Strong physical fighter",
        exp_params=[30, 20, 30, 30],
        learnings=[
            {"level": 1, "skill_id": 1},  # Attack at level 1
        ],
    )

    # Mage - magic user
    manager.classes[2] = Class(
        id=2,
        name="Mage",
        icon_index=1,
        description="Master of magic",
        exp_params=[30, 20, 25, 35],
        learnings=[
            {"level": 1, "skill_id": 1},  # Attack at level 1
            {"level": 1, "skill_id": 2},  # Heal at level 1
            {"level": 3, "skill_id": 3},  # Fireball at level 3
            {"level": 10, "skill_id": 4},  # Ice Storm at level 10
        ],
    )

    print(f"  Created {len(manager.classes)} classes")

    # =========================================================================
    # Animations
    # =========================================================================
    print("Creating animations...")

    # Physical Attack
    manager.animations[1] = Animation(
        id=1,
        name="Physical Attack",
        icon_index=0,
        description="Basic physical attack animation",
        animation1_name="Attack",
        position=1,  # Center
        frame_max=16,
    )

    # Heal
    manager.animations[2] = Animation(
        id=2,
        name="Heal",
        icon_index=1,
        description="Healing magic animation",
        animation1_name="Heal",
        position=1,
        frame_max=20,
    )

    # Fire
    manager.animations[3] = Animation(
        id=3,
        name="Fire",
        icon_index=2,
        description="Fire magic animation",
        animation1_name="Fire",
        position=1,
        frame_max=24,
    )

    print(f"  Created {len(manager.animations)} animations")

    return manager


def main():
    """Main function to create and save example database."""
    print("=" * 60)
    print("Creating Example Game Database")
    print("=" * 60)
    print()

    # Create the database
    manager = create_example_database()

    # Validate all entries
    print("\nValidating database...")
    errors = manager.validate_all()
    if errors:
        print("Validation errors found:")
        for category, error_list in errors.items():
            print(f"  {category}:")
            for error in error_list:
                print(f"    - {error}")
    else:
        print("  ✓ All entries validated successfully")

    # Save to file
    output_path = Path("data/example_database.json")
    print(f"\nSaving to {output_path}...")
    manager.save_to_file(output_path)
    print(f"  ✓ Saved successfully")

    # Print summary
    print("\nDatabase Summary:")
    print(f"  Items: {len(manager.items)}")
    print(f"  Skills: {len(manager.skills)}")
    print(f"  Weapons: {len(manager.weapons)}")
    print(f"  Armor: {len(manager.armors)}")
    print(f"  States: {len(manager.states)}")
    print(f"  Enemies: {len(manager.enemies)}")
    print(f"  Actors: {len(manager.actors)}")
    print(f"  Classes: {len(manager.classes)}")
    print(f"  Animations: {len(manager.animations)}")

    print("\n" + "=" * 60)
    print("Example database created successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
