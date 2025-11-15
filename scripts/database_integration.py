#!/usr/bin/env python3
"""
Database Integration Script
===========================

Completes database integration by:
1. Converting existing JSON data files to new schema
2. Creating default entries for all categories
3. Adding auto-backup functionality
4. Implementing cross-reference validation
5. Creating comprehensive sample data

Usage:
    python scripts/database_integration.py --migrate
    python scripts/database_integration.py --create-defaults
    python scripts/database_integration.py --create-samples
    python scripts/database_integration.py --all
"""

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from engine.data.database_manager import DatabaseManager
from engine.data.database_schema import (
    Actor,
    Animation,
    Armor,
    ArmorType,
    Class,
    DamageType,
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

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class DatabaseIntegrator:
    """Handles database integration tasks."""

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize the integrator.

        Args:
            base_path: Base path for the project (defaults to script parent directory)
        """
        self.base_path = base_path or Path(__file__).parent.parent
        self.templates_config = self.base_path / "templates" / "base_builder" / "config"
        self.backup_dir = self.base_path / "backups" / "database"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        self.db = DatabaseManager()

    def backup_database(self, name: str = "auto") -> Path:
        """
        Create a backup of the current database.

        Args:
            name: Backup name (default: "auto")

        Returns:
            Path to the backup file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"{name}_backup_{timestamp}.json"

        # Save current database state
        data = self.db.to_dict()
        with open(backup_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✓ Backup created: {backup_file}")
        return backup_file

    def convert_legacy_items(self) -> List[Item]:
        """
        Convert legacy items.json to new schema.

        Returns:
            List of converted Item objects
        """
        items_file = self.templates_config / "items.json"
        if not items_file.exists():
            print(f"⚠ No items.json found at {items_file}")
            return []

        with open(items_file, "r", encoding="utf-8") as f:
            legacy_data = json.load(f)

        items = []
        item_id = 1

        # Legacy item format: string keys with simple properties
        for key, data in legacy_data.items():
            item_type = ItemType.REGULAR
            if data.get("type") == "equipment":
                item_type = ItemType.KEY  # Equipment items are non-consumable

            # Create item with converted properties
            item = Item(
                id=item_id,
                name=data.get("name", key.replace("_", " ").title()),
                description=data.get("description", ""),
                price=data.get("value", 0),
                item_type=item_type,
                consumable=data.get("type") != "equipment",
                icon_index=item_id,  # Use ID as icon index
                note=f"Converted from legacy key: {key}",
            )

            items.append(item)
            item_id += 1

        print(f"✓ Converted {len(items)} legacy items")
        return items

    def create_default_items(self) -> List[Item]:
        """Create default items for all common types."""
        items = [
            # Healing items
            Item(
                id=101,
                name="Potion",
                description="Restores 50 HP",
                price=50,
                icon_index=1,
                item_type=ItemType.REGULAR,
                effects=[
                    Effect(
                        effect_type=EffectType.RECOVER_HP, value1=50, timing=EffectTiming.IMMEDIATE
                    )
                ],
            ),
            Item(
                id=102,
                name="Hi-Potion",
                description="Restores 200 HP",
                price=200,
                icon_index=2,
                item_type=ItemType.REGULAR,
                effects=[
                    Effect(
                        effect_type=EffectType.RECOVER_HP, value1=200, timing=EffectTiming.IMMEDIATE
                    )
                ],
            ),
            Item(
                id=103,
                name="Ether",
                description="Restores 30 MP",
                price=150,
                icon_index=3,
                item_type=ItemType.REGULAR,
                effects=[
                    Effect(
                        effect_type=EffectType.RECOVER_MP, value1=30, timing=EffectTiming.IMMEDIATE
                    )
                ],
            ),
            Item(
                id=104,
                name="Elixir",
                description="Fully restores HP and MP",
                price=5000,
                icon_index=4,
                item_type=ItemType.REGULAR,
                effects=[
                    Effect(effect_type=EffectType.RECOVER_HP, value1=9999),
                    Effect(effect_type=EffectType.RECOVER_MP, value1=9999),
                ],
            ),
            # Status items
            Item(
                id=105,
                name="Antidote",
                description="Cures poison",
                price=50,
                icon_index=5,
                item_type=ItemType.REGULAR,
                effects=[
                    Effect(effect_type=EffectType.REMOVE_STATE, target_param=1)  # Poison state ID
                ],
            ),
            # Key items
            Item(
                id=201,
                name="Gold Key",
                description="Opens gold doors",
                price=0,
                icon_index=20,
                item_type=ItemType.KEY,
                consumable=False,
            ),
            Item(
                id=202,
                name="Silver Key",
                description="Opens silver doors",
                price=0,
                icon_index=21,
                item_type=ItemType.KEY,
                consumable=False,
            ),
        ]
        print(f"✓ Created {len(items)} default items")
        return items

    def create_default_skills(self) -> List[Skill]:
        """Create default skills for all types."""
        skills = [
            # Physical skills
            Skill(
                id=1,
                name="Power Attack",
                description="Strong physical attack",
                skill_type=SkillType.PHYSICAL,
                mp_cost=5,
                tp_cost=0,
                damage_type=DamageType.HP_DAMAGE,
                element_type=ElementType.NORMAL,
                animation_id=1,
                icon_index=1,
                message1="%1 uses Power Attack!",
                effects=[Effect(effect_type=EffectType.DAMAGE_HP, value1=50, value2=10)],
            ),
            # Magic skills
            Skill(
                id=2,
                name="Fire",
                description="Fire magic attack",
                skill_type=SkillType.MAGIC,
                mp_cost=10,
                tp_cost=0,
                damage_type=DamageType.HP_DAMAGE,
                element_type=ElementType.FIRE,
                animation_id=2,
                icon_index=10,
                message1="%1 casts Fire!",
                effects=[Effect(effect_type=EffectType.DAMAGE_HP, value1=40, value2=10)],
            ),
            Skill(
                id=3,
                name="Ice",
                description="Ice magic attack",
                skill_type=SkillType.MAGIC,
                mp_cost=10,
                tp_cost=0,
                damage_type=DamageType.HP_DAMAGE,
                element_type=ElementType.ICE,
                animation_id=3,
                icon_index=11,
                message1="%1 casts Ice!",
                effects=[Effect(effect_type=EffectType.DAMAGE_HP, value1=40, value2=10)],
            ),
            Skill(
                id=4,
                name="Thunder",
                description="Thunder magic attack",
                skill_type=SkillType.MAGIC,
                mp_cost=10,
                tp_cost=0,
                damage_type=DamageType.HP_DAMAGE,
                element_type=ElementType.THUNDER,
                animation_id=4,
                icon_index=12,
                message1="%1 casts Thunder!",
                effects=[Effect(effect_type=EffectType.DAMAGE_HP, value1=40, value2=10)],
            ),
            # Healing skills
            Skill(
                id=5,
                name="Heal",
                description="Restores HP to one ally",
                skill_type=SkillType.MAGIC,
                mp_cost=15,
                tp_cost=0,
                damage_type=DamageType.HP_RECOVER,
                element_type=ElementType.LIGHT,
                animation_id=5,
                icon_index=20,
                message1="%1 casts Heal!",
                scope=3,  # One ally
                effects=[Effect(effect_type=EffectType.RECOVER_HP, value1=100, value2=20)],
            ),
            # Special skills
            Skill(
                id=6,
                name="Steal",
                description="Steal item from enemy",
                skill_type=SkillType.SPECIAL,
                mp_cost=0,
                tp_cost=10,
                damage_type=DamageType.NONE,
                element_type=ElementType.NORMAL,
                animation_id=6,
                icon_index=30,
                message1="%1 tries to steal!",
                note="Special effect: steal item",
            ),
        ]
        print(f"✓ Created {len(skills)} default skills")
        return skills

    def create_default_weapons(self) -> List[Weapon]:
        """Create default weapons for all types."""
        weapons = [
            Weapon(
                id=1,
                name="Bronze Sword",
                description="Basic sword",
                weapon_type=WeaponType.SWORD,
                price=100,
                icon_index=1,
                params=[10, 0, 0, 0, 0, 0],  # ATK, DEF, MAT, MDF, AGI, LUK
                animation_id=1,
            ),
            Weapon(
                id=2,
                name="Iron Sword",
                description="Standard sword",
                weapon_type=WeaponType.SWORD,
                price=500,
                icon_index=2,
                params=[25, 0, 0, 0, 0, 0],
                animation_id=1,
            ),
            Weapon(
                id=3,
                name="Steel Spear",
                description="Sturdy spear",
                weapon_type=WeaponType.SPEAR,
                price=600,
                icon_index=10,
                params=[28, 0, 0, 0, 0, 0],
                animation_id=2,
            ),
            Weapon(
                id=4,
                name="War Axe",
                description="Heavy axe",
                weapon_type=WeaponType.AXE,
                price=800,
                icon_index=20,
                params=[35, 0, 0, 0, -5, 0],  # High ATK, low AGI
                animation_id=3,
            ),
            Weapon(
                id=5,
                name="Long Bow",
                description="Ranged bow",
                weapon_type=WeaponType.BOW,
                price=700,
                icon_index=30,
                params=[30, 0, 0, 0, 5, 0],  # Good ATK and AGI
                animation_id=4,
            ),
            Weapon(
                id=6,
                name="Magic Staff",
                description="Staff for magic",
                weapon_type=WeaponType.STAFF,
                price=900,
                icon_index=40,
                params=[5, 0, 20, 10, 0, 0],  # Low ATK, high MAT and MDF
                animation_id=5,
            ),
        ]
        print(f"✓ Created {len(weapons)} default weapons")
        return weapons

    def create_default_armors(self) -> List[Armor]:
        """Create default armor for all types."""
        armors = [
            Armor(
                id=1,
                name="Leather Shield",
                description="Basic shield",
                armor_type=ArmorType.SHIELD,
                equip_type=EquipType.SHIELD,
                price=150,
                icon_index=1,
                params=[0, 5, 0, 3, 0, 0],  # DEF +5, MDF +3
            ),
            Armor(
                id=2,
                name="Iron Helmet",
                description="Standard helmet",
                armor_type=ArmorType.HELMET,
                equip_type=EquipType.HELMET,
                price=200,
                icon_index=10,
                params=[0, 8, 0, 5, 0, 0],  # DEF +8, MDF +5
            ),
            Armor(
                id=3,
                name="Leather Armor",
                description="Light armor",
                armor_type=ArmorType.BODY,
                equip_type=EquipType.BODY,
                price=300,
                icon_index=20,
                params=[0, 15, 0, 8, 0, 0],  # DEF +15, MDF +8
            ),
            Armor(
                id=4,
                name="Chain Mail",
                description="Medium armor",
                armor_type=ArmorType.BODY,
                equip_type=EquipType.BODY,
                price=800,
                icon_index=21,
                params=[0, 30, 0, 15, -3, 0],  # DEF +30, MDF +15, AGI -3
            ),
            Armor(
                id=5,
                name="Power Ring",
                description="Increases attack",
                armor_type=ArmorType.ACCESSORY,
                equip_type=EquipType.ACCESSORY,
                price=1000,
                icon_index=30,
                params=[10, 0, 0, 0, 0, 5],  # ATK +10, LUK +5
            ),
        ]
        print(f"✓ Created {len(armors)} default armors")
        return armors

    def create_default_enemies(self) -> List[Enemy]:
        """Create default enemies."""
        enemies = [
            Enemy(
                id=1,
                name="Slime",
                description="A gelatinous blob",
                params=[50, 10, 10, 5, 5, 5, 8, 10],  # HP, MP, ATK, DEF, MAT, MDF, AGI, LUK
                exp=10,
                gold=20,
                icon_index=1,
                drop_items=[DropItem(kind=1, item_id=101, drop_rate=0.5)],  # 50% Potion
            ),
            Enemy(
                id=2,
                name="Goblin",
                description="Small aggressive creature",
                params=[80, 0, 15, 10, 0, 5, 12, 5],
                exp=25,
                gold=40,
                icon_index=2,
                drop_items=[
                    DropItem(kind=1, item_id=101, drop_rate=0.3),  # 30% Potion
                    DropItem(kind=2, item_id=1, drop_rate=0.1),  # 10% weapon
                ],
            ),
            Enemy(
                id=3,
                name="Wolf",
                description="Wild wolf",
                params=[120, 0, 20, 15, 0, 8, 18, 8],
                exp=40,
                gold=50,
                icon_index=3,
            ),
            Enemy(
                id=4,
                name="Skeleton",
                description="Animated bones",
                params=[150, 20, 25, 12, 15, 10, 10, 5],
                exp=60,
                gold=80,
                icon_index=4,
            ),
            Enemy(
                id=5,
                name="Dragon",
                description="Mighty dragon",
                params=[500, 100, 50, 40, 40, 30, 15, 20],
                exp=500,
                gold=1000,
                icon_index=5,
            ),
        ]
        print(f"✓ Created {len(enemies)} default enemies")
        return enemies

    def create_default_states(self) -> List[State]:
        """Create default status states."""
        states = [
            State(
                id=1,
                name="Poison",
                description="Loses HP each turn",
                icon_index=1,
                restriction=StateRestriction.NONE,
                priority=50,
                remove_at_battle_end=True,
                auto_removal_timing=2,
                note="Damage each turn",
            ),
            State(
                id=2,
                name="Blind",
                description="Reduced hit rate",
                icon_index=2,
                restriction=StateRestriction.NONE,
                priority=60,
                remove_at_battle_end=True,
            ),
            State(
                id=3,
                name="Silence",
                description="Cannot use magic",
                icon_index=3,
                restriction=StateRestriction.NONE,
                priority=70,
                remove_at_battle_end=True,
            ),
            State(
                id=4,
                name="Confusion",
                description="Attacks random targets",
                icon_index=4,
                restriction=StateRestriction.ATTACK_ANYONE,
                priority=80,
                remove_at_battle_end=True,
                auto_removal_timing=3,
            ),
            State(
                id=5,
                name="Sleep",
                description="Cannot move",
                icon_index=5,
                restriction=StateRestriction.CANNOT_MOVE,
                priority=90,
                remove_at_battle_end=True,
                remove_by_damage=True,
            ),
        ]
        print(f"✓ Created {len(states)} default states")
        return states

    def create_default_actors(self) -> List[Actor]:
        """Create default playable actors."""
        actors = [
            Actor(
                id=1,
                name="Hero",
                description="Brave warrior",
                class_id=1,
                initial_level=1,
                max_level=99,
                icon_index=1,
                face_index=0,
                character_index=0,
                equips=[1, 1, 2, 3, 0],  # weapon, shield, helmet, armor, accessory
                note="Main protagonist",
            ),
            Actor(
                id=2,
                name="Mage",
                description="Powerful spellcaster",
                class_id=2,
                initial_level=1,
                max_level=99,
                icon_index=2,
                face_index=1,
                character_index=1,
                equips=[6, 0, 2, 3, 0],  # staff, no shield, helmet, armor
                note="Magic user",
            ),
            Actor(
                id=3,
                name="Archer",
                description="Skilled marksman",
                class_id=3,
                initial_level=1,
                max_level=99,
                icon_index=3,
                face_index=2,
                character_index=2,
                equips=[5, 0, 2, 3, 0],  # bow
                note="Ranged attacker",
            ),
        ]
        print(f"✓ Created {len(actors)} default actors")
        return actors

    def create_default_classes(self) -> List[Class]:
        """Create default character classes."""

        # Helper function to generate stat curve from base and growth
        def generate_curve(base: int, growth: float) -> List[int]:
            return [max(1, int(base + (level * growth))) for level in range(99)]

        classes = [
            Class(
                id=1,
                name="Warrior",
                description="Strong fighter",
                icon_index=1,
                learnings=[
                    {"level": 1, "skill_id": 1},  # Power Attack at level 1
                    {"level": 5, "skill_id": 2},  # Fire at level 5
                ],
                exp_params=[30, 20, 30, 30],  # Base, extra, acc_a, acc_b
                params=[
                    generate_curve(100, 50),  # HP
                    generate_curve(20, 5),  # MP
                    generate_curve(15, 3),  # ATK
                    generate_curve(12, 2),  # DEF
                    generate_curve(5, 1),  # MAT
                    generate_curve(8, 1),  # MDF
                    generate_curve(10, 2),  # AGI
                    generate_curve(10, 1),  # LUK
                ],
            ),
            Class(
                id=2,
                name="Mage",
                description="Master of magic",
                icon_index=2,
                learnings=[
                    {"level": 1, "skill_id": 2},  # Fire
                    {"level": 3, "skill_id": 3},  # Ice
                    {"level": 5, "skill_id": 4},  # Thunder
                    {"level": 7, "skill_id": 5},  # Heal
                ],
                exp_params=[30, 20, 30, 30],
                params=[
                    generate_curve(60, 20),  # HP
                    generate_curve(100, 15),  # MP
                    generate_curve(8, 1),  # ATK
                    generate_curve(6, 1),  # DEF
                    generate_curve(20, 4),  # MAT
                    generate_curve(15, 3),  # MDF
                    generate_curve(8, 1),  # AGI
                    generate_curve(12, 2),  # LUK
                ],
            ),
            Class(
                id=3,
                name="Ranger",
                description="Swift archer",
                icon_index=3,
                learnings=[
                    {"level": 1, "skill_id": 1},  # Power Attack
                    {"level": 10, "skill_id": 6},  # Steal
                ],
                exp_params=[30, 20, 30, 30],
                params=[
                    generate_curve(80, 35),  # HP
                    generate_curve(40, 8),  # MP
                    generate_curve(12, 2),  # ATK
                    generate_curve(8, 1),  # DEF
                    generate_curve(8, 1),  # MAT
                    generate_curve(10, 2),  # MDF
                    generate_curve(15, 3),  # AGI
                    generate_curve(15, 2),  # LUK
                ],
            ),
        ]
        print(f"✓ Created {len(classes)} default classes")
        return classes

    def create_default_animations(self) -> List[Animation]:
        """Create default animations."""
        animations = [
            Animation(
                id=1,
                name="Physical Attack",
                description="Basic attack animation",
                icon_index=1,
                frame_max=1,
                frames=[{"cell_id": 0, "pattern": 0}],
                timings=[],
            ),
            Animation(
                id=2,
                name="Fire Magic",
                description="Fire spell effect",
                icon_index=10,
                frame_max=1,
                frames=[{"cell_id": 1, "pattern": 0}],
                timings=[],
            ),
            Animation(
                id=3,
                name="Ice Magic",
                description="Ice spell effect",
                icon_index=11,
                frame_max=1,
                frames=[{"cell_id": 2, "pattern": 0}],
                timings=[],
            ),
            Animation(
                id=4,
                name="Thunder Magic",
                description="Thunder spell effect",
                icon_index=12,
                frame_max=1,
                frames=[{"cell_id": 3, "pattern": 0}],
                timings=[],
            ),
            Animation(
                id=5,
                name="Heal Magic",
                description="Healing effect",
                icon_index=20,
                frame_max=1,
                frames=[{"cell_id": 4, "pattern": 0}],
                timings=[],
            ),
            Animation(
                id=6,
                name="Special Effect",
                description="Special action effect",
                icon_index=30,
                frame_max=1,
                frames=[{"cell_id": 5, "pattern": 0}],
                timings=[],
            ),
        ]
        print(f"✓ Created {len(animations)} default animations")
        return animations

    def create_sample_data(self, count: int = 100) -> Dict[str, int]:
        """
        Create comprehensive sample data for performance testing.

        Args:
            count: Number of sample items to create per category

        Returns:
            Dictionary with counts per category
        """
        counts = {}

        # Create items
        items = []
        for i in range(count):
            item = Item(
                id=1000 + i,
                name=f"Sample Item {i+1}",
                description=f"Test item number {i+1}",
                price=10 * (i + 1),
                icon_index=(i % 100) + 1,
                item_type=ItemType.REGULAR if i % 5 != 0 else ItemType.KEY,
                consumable=i % 5 != 0,
                effects=[Effect(effect_type=EffectType.RECOVER_HP, value1=10 + (i * 2))],
            )
            items.append(item)

        for item in items:
            self.db.create_entry("items", item)
        counts["items"] = len(items)

        # Create skills with cross-references to animations
        skills = []
        for i in range(count):
            skill = Skill(
                id=100 + i,
                name=f"Sample Skill {i+1}",
                description=f"Test skill number {i+1}",
                skill_type=SkillType.MAGIC if i % 3 == 0 else SkillType.PHYSICAL,
                mp_cost=5 + (i % 50),
                animation_id=1 + (i % 6),  # Cross-reference to animations 1-6
                icon_index=(i % 100) + 1,
                damage_type=DamageType.HP_DAMAGE,
                element_type=ElementType.NORMAL,
                effects=[Effect(effect_type=EffectType.DAMAGE_HP, value1=10 + (i * 2), value2=5)],
            )
            skills.append(skill)

        for skill in skills:
            self.db.create_entry("skills", skill)
        counts["skills"] = len(skills)

        # Create weapons
        weapon_types = list(WeaponType)
        weapons = []
        for i in range(count):
            weapon = Weapon(
                id=100 + i,
                name=f"Sample Weapon {i+1}",
                description=f"Test weapon number {i+1}",
                weapon_type=weapon_types[i % len(weapon_types)],
                price=100 + (i * 10),
                params=[10 + i, 0, 0, 0, 0, 0],  # ATK increases with i
                animation_id=1 + (i % 6),  # Cross-reference to animations
                icon_index=(i % 100) + 1,
            )
            weapons.append(weapon)

        for weapon in weapons:
            self.db.create_entry("weapons", weapon)
        counts["weapons"] = len(weapons)

        # Create armors
        armor_types = list(ArmorType)
        equip_type_map = {
            ArmorType.SHIELD: EquipType.SHIELD,
            ArmorType.HELMET: EquipType.HELMET,
            ArmorType.BODY: EquipType.BODY,
            ArmorType.ACCESSORY: EquipType.ACCESSORY,
        }
        armors = []
        for i in range(count):
            atype = armor_types[i % len(armor_types)]
            armor = Armor(
                id=100 + i,
                name=f"Sample Armor {i+1}",
                description=f"Test armor number {i+1}",
                armor_type=atype,
                equip_type=equip_type_map[atype],
                price=100 + (i * 10),
                params=[0, 5 + i, 0, 3 + (i // 2), 0, 0],  # DEF and MDF increase
                icon_index=(i % 100) + 1,
            )
            armors.append(armor)

        for armor in armors:
            self.db.create_entry("armors", armor)
        counts["armors"] = len(armors)

        # Create enemies with drop references to items
        enemies = []
        for i in range(count):
            enemy = Enemy(
                id=100 + i,
                name=f"Sample Enemy {i+1}",
                description=f"Test enemy number {i+1}",
                params=[
                    50 + (i * 10),  # HP
                    10 + (i * 2),  # MP
                    10 + i,  # ATK
                    5 + i,  # DEF
                    5 + i,  # MAT
                    5 + i,  # MDF
                    10 + (i % 20),  # AGI
                    10,  # LUK
                ],
                exp=10 + (i * 5),
                gold=20 + (i * 10),
                icon_index=(i % 100) + 1,
                drop_items=[
                    DropItem(kind=1, item_id=1000 + (i % 10), drop_rate=0.3)
                ],  # Cross-reference to items
            )
            enemies.append(enemy)

        for enemy in enemies:
            self.db.create_entry("enemies", enemy)
        counts["enemies"] = len(enemies)

        print(f"✓ Created {sum(counts.values())} sample entries across {len(counts)} categories")
        return counts

    def validate_cross_references(self) -> Dict[str, List[str]]:
        """
        Validate cross-references between database entries.

        Checks:
        - Skills referencing valid animation IDs
        - Weapons referencing valid animation IDs
        - Enemies dropping valid item IDs
        - Actors having valid class and equipment IDs
        - Classes teaching valid skill IDs

        Returns:
            Dictionary of validation errors by category
        """
        errors = {}

        # Get all IDs for validation
        animation_ids = set(self.db.get_all_ids("animations"))
        item_ids = set(self.db.get_all_ids("items"))
        skill_ids = set(self.db.get_all_ids("skills"))
        class_ids = set(self.db.get_all_ids("classes"))
        weapon_ids = set(self.db.get_all_ids("weapons"))
        armor_ids = set(self.db.get_all_ids("armors"))

        # Validate skills
        skill_errors = []
        for skill in self.db.get_all_entries("skills"):
            if skill.animation_id > 0 and skill.animation_id not in animation_ids:
                skill_errors.append(
                    f"Skill {skill.id} '{skill.name}' references non-existent "
                    f"animation {skill.animation_id}"
                )
        if skill_errors:
            errors["skills"] = skill_errors

        # Validate weapons
        weapon_errors = []
        for weapon in self.db.get_all_entries("weapons"):
            if weapon.animation_id > 0 and weapon.animation_id not in animation_ids:
                weapon_errors.append(
                    f"Weapon {weapon.id} '{weapon.name}' references non-existent "
                    f"animation {weapon.animation_id}"
                )
        if weapon_errors:
            errors["weapons"] = weapon_errors

        # Validate enemies
        enemy_errors = []
        for enemy in self.db.get_all_entries("enemies"):
            for drop_item in enemy.drop_items:
                # Check if the item exists based on its kind (1=item, 2=weapon, 3=armor)
                if drop_item.kind == 1 and drop_item.item_id not in item_ids:
                    enemy_errors.append(
                        f"Enemy {enemy.id} '{enemy.name}' drops non-existent "
                        f"item {drop_item.item_id}"
                    )
                elif drop_item.kind == 2 and drop_item.item_id not in weapon_ids:
                    enemy_errors.append(
                        f"Enemy {enemy.id} '{enemy.name}' drops non-existent "
                        f"weapon {drop_item.item_id}"
                    )
                elif drop_item.kind == 3 and drop_item.item_id not in armor_ids:
                    enemy_errors.append(
                        f"Enemy {enemy.id} '{enemy.name}' drops non-existent "
                        f"armor {drop_item.item_id}"
                    )
        if enemy_errors:
            errors["enemies"] = enemy_errors

        # Validate actors
        actor_errors = []
        for actor in self.db.get_all_entries("actors"):
            if actor.class_id not in class_ids:
                actor_errors.append(
                    f"Actor {actor.id} '{actor.name}' has non-existent " f"class {actor.class_id}"
                )
            # Check equipment IDs
            for equip_id in actor.equips:
                if equip_id > 0:
                    if equip_id not in weapon_ids and equip_id not in armor_ids:
                        actor_errors.append(
                            f"Actor {actor.id} '{actor.name}' has non-existent "
                            f"equipment {equip_id}"
                        )
        if actor_errors:
            errors["actors"] = actor_errors

        # Validate classes
        class_errors = []
        for cls in self.db.get_all_entries("classes"):
            for learning in cls.learnings:
                skill_id = learning.get("skill_id", 0)
                if skill_id not in skill_ids:
                    class_errors.append(
                        f"Class {cls.id} '{cls.name}' teaches non-existent "
                        f"skill {skill_id} at level {learning.get('level', 0)}"
                    )
        if class_errors:
            errors["classes"] = class_errors

        # Report results
        if errors:
            print(f"⚠ Found {sum(len(e) for e in errors.values())} cross-reference errors")
            for category, error_list in errors.items():
                print(f"\n{category.upper()}:")
                for error in error_list:
                    print(f"  - {error}")
        else:
            print("✓ All cross-references are valid")

        return errors

    def migrate_all(self):
        """Run full migration process."""
        print("\n=== Starting Database Migration ===\n")

        # Create backup
        self.backup_database("pre_migration")

        # Convert legacy data
        print("\n--- Converting Legacy Data ---")
        legacy_items = self.convert_legacy_items()
        for item in legacy_items:
            try:
                self.db.create_entry("items", item)
            except Exception as e:
                print(f"⚠ Failed to add item {item.name}: {e}")

        print(f"\n✓ Migration complete: {len(legacy_items)} items migrated")

    def create_all_defaults(self):
        """Create default entries for all categories."""
        print("\n=== Creating Default Entries ===\n")

        # Create backup
        self.backup_database("pre_defaults")

        # Create defaults for each category
        all_entries = {
            "animations": self.create_default_animations(),
            "items": self.create_default_items(),
            "skills": self.create_default_skills(),
            "weapons": self.create_default_weapons(),
            "armors": self.create_default_armors(),
            "states": self.create_default_states(),
            "classes": self.create_default_classes(),
            "enemies": self.create_default_enemies(),
            "actors": self.create_default_actors(),
        }

        # Add to database
        for category, entries in all_entries.items():
            for entry in entries:
                try:
                    self.db.create_entry(category, entry)
                except Exception as e:
                    print(f"⚠ Failed to add {category} {entry.name}: {e}")

        total = sum(len(entries) for entries in all_entries.values())
        print(f"\n✓ Created {total} default entries across {len(all_entries)} categories")

    def create_all_samples(self, count: int = 100):
        """Create sample data for performance testing."""
        print(f"\n=== Creating Sample Data ({count} per category) ===\n")

        # Create backup
        self.backup_database("pre_samples")

        # Create samples
        counts = self.create_sample_data(count)

        print(f"\n✓ Sample data creation complete: {sum(counts.values())} total entries")

    def save_database(self, output_path: Optional[Path] = None):
        """Save the database to a file."""
        if output_path is None:
            output_path = self.base_path / "data" / "integrated_database.json"

        # Ensure output_path is a Path object
        if isinstance(output_path, str):
            output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.db.save_to_file(output_path)
        print(f"\n✓ Database saved to: {output_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Database integration script for NeonWorks game engine"
    )
    parser.add_argument(
        "--migrate", action="store_true", help="Migrate legacy JSON data to new schema"
    )
    parser.add_argument(
        "--create-defaults", action="store_true", help="Create default entries for all categories"
    )
    parser.add_argument(
        "--create-samples",
        action="store_true",
        help="Create sample data for testing (100+ items per category)",
    )
    parser.add_argument(
        "--validate", action="store_true", help="Validate cross-references in database"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all operations (migrate, defaults, samples, validate)",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file path for database (default: data/integrated_database.json)",
    )
    parser.add_argument(
        "--sample-count",
        type=int,
        default=100,
        help="Number of sample items to create per category (default: 100)",
    )

    args = parser.parse_args()

    # Create integrator
    integrator = DatabaseIntegrator()

    # Run operations
    if args.all or args.migrate:
        integrator.migrate_all()

    if args.all or args.create_defaults:
        integrator.create_all_defaults()

    if args.all or args.create_samples:
        integrator.create_all_samples(args.sample_count)

    if args.all or args.validate:
        print("\n=== Validating Cross-References ===\n")
        integrator.validate_cross_references()

    # Save database
    output_path = Path(args.output) if args.output else None
    integrator.save_database(output_path)

    print("\n=== Database Integration Complete ===\n")


if __name__ == "__main__":
    main()
