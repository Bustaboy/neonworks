"""
Comprehensive test suite for inventory.py

Tests cover:
- Item creation (Weapon, Armor, Consumable, base Item)
- Inventory management (add, remove, capacity)
- Item stacking
- Equipment system
- Consumable usage
- Item effects on character stats
- Serialization
"""

import pytest
from unittest.mock import Mock
import sys
from pathlib import Path

# Add game directory to path
game_dir = Path(__file__).parent.parent / "game"
sys.path.insert(0, str(game_dir))


class TestItemCreation:
    """Test creating different item types."""

    def test_base_item_creation(self):
        """Test creating a base item."""
        from inventory import Item

        item = Item(
            item_id="item_001",
            name="Test Item",
            description="A test item",
            item_type="misc",
            value=10
        )

        assert item.item_id == "item_001"
        assert item.name == "Test Item"
        assert item.item_type == "misc"
        assert item.value == 10
        assert item.stackable is False

    def test_stackable_item(self):
        """Test creating a stackable item."""
        from inventory import Item

        item = Item(
            item_id="item_002",
            name="Credits",
            description="Currency",
            item_type="currency",
            value=1,
            stackable=True,
            max_stack=9999
        )

        assert item.stackable is True
        assert item.max_stack == 9999

    def test_weapon_creation(self):
        """Test creating a weapon item."""
        from inventory import Weapon

        weapon = Weapon(
            item_id="weapon_ar_01",
            name="Militech M-76E",
            description="Assault rifle",
            value=1500,
            damage=35,
            accuracy=90,
            range=14,
            armor_pen=0.20,
            crit_multiplier=2.0,
            weapon_type="ranged"
        )

        assert weapon.item_type == "weapon"
        assert weapon.damage == 35
        assert weapon.accuracy == 90
        assert weapon.weapon_type == "ranged"

    def test_armor_creation(self):
        """Test creating an armor item."""
        from inventory import Armor

        armor = Armor(
            item_id="armor_vest_01",
            name="Kevlar Vest",
            description="Light armor",
            value=800,
            armor_value=20,
            mobility_penalty=0
        )

        assert armor.item_type == "armor"
        assert armor.armor_value == 20
        assert armor.mobility_penalty == 0

    def test_consumable_creation(self):
        """Test creating a consumable item."""
        from inventory import Consumable

        medkit = Consumable(
            item_id="consumable_medkit",
            name="Medkit",
            description="Restores 50 HP",
            value=100,
            effect="heal",
            amount=50,
            stackable=True,
            max_stack=10
        )

        assert medkit.item_type == "consumable"
        assert medkit.effect == "heal"
        assert medkit.amount == 50
        assert medkit.stackable is True


class TestInventoryBasics:
    """Test basic inventory operations."""

    def test_inventory_creation(self):
        """Test creating an inventory."""
        from inventory import Inventory

        inv = Inventory(max_capacity=50)

        assert inv.max_capacity == 50
        assert len(inv.items) == 0

    def test_add_item_to_inventory(self):
        """Test adding an item to inventory."""
        from inventory import Inventory, Item

        inv = Inventory()
        item = Item("item_001", "Test", "Desc", "misc", 10)

        inv.add_item(item)

        assert len(inv.items) == 1
        assert "item_001" in inv.items
        assert inv.items["item_001"]["quantity"] == 1

    def test_add_same_item_twice(self):
        """Test adding same item multiple times."""
        from inventory import Inventory, Item

        inv = Inventory()
        item = Item("item_001", "Test", "Desc", "misc", 10)

        inv.add_item(item)
        inv.add_item(item)

        # Non-stackable items stored separately
        assert inv.items["item_001"]["quantity"] == 2

    def test_remove_item_from_inventory(self):
        """Test removing an item from inventory."""
        from inventory import Inventory, Item

        inv = Inventory()
        item = Item("item_001", "Test", "Desc", "misc", 10)

        inv.add_item(item)
        removed = inv.remove_item("item_001", quantity=1)

        assert removed is True
        assert len(inv.items) == 0

    def test_remove_nonexistent_item(self):
        """Test removing item that doesn't exist."""
        from inventory import Inventory

        inv = Inventory()
        removed = inv.remove_item("fake_item")

        assert removed is False

    def test_get_item_quantity(self):
        """Test getting quantity of an item."""
        from inventory import Inventory, Item

        inv = Inventory()
        item = Item("item_001", "Test", "Desc", "misc", 10, stackable=True)

        inv.add_item(item, quantity=5)

        assert inv.get_item_quantity("item_001") == 5


class TestItemStacking:
    """Test item stacking mechanics."""

    def test_stack_consumables(self):
        """Test stacking consumable items."""
        from inventory import Inventory, Consumable

        inv = Inventory()
        medkit = Consumable("medkit", "Medkit", "Heals", 100, "heal", 50,
                           stackable=True, max_stack=10)

        inv.add_item(medkit, quantity=3)
        inv.add_item(medkit, quantity=2)

        assert inv.get_item_quantity("medkit") == 5

    def test_stack_limit_enforced(self):
        """Test that stack limit is enforced."""
        from inventory import Inventory, Consumable

        inv = Inventory()
        medkit = Consumable("medkit", "Medkit", "Heals", 100, "heal", 50,
                           stackable=True, max_stack=10)

        result = inv.add_item(medkit, quantity=15)

        # Should only add up to max_stack
        assert inv.get_item_quantity("medkit") == 10
        assert result is False  # Indicates some items couldn't be added

    def test_remove_from_stack(self):
        """Test removing items from a stack."""
        from inventory import Inventory, Consumable

        inv = Inventory()
        medkit = Consumable("medkit", "Medkit", "Heals", 100, "heal", 50,
                           stackable=True, max_stack=10)

        inv.add_item(medkit, quantity=5)
        inv.remove_item("medkit", quantity=2)

        assert inv.get_item_quantity("medkit") == 3

    def test_non_stackable_items_counted_separately(self):
        """Test that non-stackable items are counted separately."""
        from inventory import Inventory, Weapon

        inv = Inventory()
        weapon = Weapon("weapon_01", "Rifle", "Gun", 1000, 30, 85, 10, 0.15, 2.0, "ranged")

        inv.add_item(weapon)
        inv.add_item(weapon)

        # Two separate weapon instances
        assert inv.get_item_quantity("weapon_01") == 2


class TestInventoryCapacity:
    """Test inventory capacity limits."""

    def test_capacity_limit(self):
        """Test inventory capacity is enforced."""
        from inventory import Inventory, Item

        inv = Inventory(max_capacity=5)

        for i in range(5):
            item = Item(f"item_{i}", f"Item {i}", "Desc", "misc", 10)
            inv.add_item(item)

        assert inv.get_item_count() == 5

    def test_cannot_exceed_capacity(self):
        """Test cannot add items beyond capacity."""
        from inventory import Inventory, Item

        inv = Inventory(max_capacity=2)

        inv.add_item(Item("item_1", "Item 1", "Desc", "misc", 10))
        inv.add_item(Item("item_2", "Item 2", "Desc", "misc", 10))

        # Try to add third item
        result = inv.add_item(Item("item_3", "Item 3", "Desc", "misc", 10))

        assert result is False
        assert inv.get_item_count() == 2

    def test_stackable_items_count_as_one_slot(self):
        """Test stackable items count as single inventory slot."""
        from inventory import Inventory, Consumable

        inv = Inventory(max_capacity=5)

        medkit = Consumable("medkit", "Medkit", "Heals", 100, "heal", 50,
                           stackable=True, max_stack=10)

        inv.add_item(medkit, quantity=10)

        # 10 medkits in one stack = 1 slot used
        assert inv.get_item_count() == 1

    def test_get_remaining_capacity(self):
        """Test getting remaining inventory capacity."""
        from inventory import Inventory, Item

        inv = Inventory(max_capacity=10)

        inv.add_item(Item("item_1", "Item", "Desc", "misc", 10))
        inv.add_item(Item("item_2", "Item", "Desc", "misc", 10))

        assert inv.get_remaining_capacity() == 8


class TestEquipmentSystem:
    """Test equipment and gear management."""

    def test_equip_weapon(self):
        """Test equipping a weapon."""
        from inventory import Inventory, Weapon

        inv = Inventory()
        weapon = Weapon("weapon_01", "Rifle", "Gun", 1000, 30, 85, 10, 0.15, 2.0, "ranged")

        inv.add_item(weapon)
        result = inv.equip_weapon("weapon_01")

        assert result is True
        assert inv.equipped_weapon is not None
        assert inv.equipped_weapon.item_id == "weapon_01"

    def test_equip_weapon_not_in_inventory(self):
        """Test cannot equip weapon not in inventory."""
        from inventory import Inventory

        inv = Inventory()
        result = inv.equip_weapon("fake_weapon")

        assert result is False
        assert inv.equipped_weapon is None

    def test_equip_different_weapon_unequips_old(self):
        """Test equipping new weapon unequips old one."""
        from inventory import Inventory, Weapon

        inv = Inventory()
        weapon1 = Weapon("weapon_01", "Rifle", "Gun", 1000, 30, 85, 10, 0.15, 2.0, "ranged")
        weapon2 = Weapon("weapon_02", "Pistol", "Gun", 500, 25, 90, 8, 0.10, 2.0, "ranged")

        inv.add_item(weapon1)
        inv.add_item(weapon2)

        inv.equip_weapon("weapon_01")
        inv.equip_weapon("weapon_02")

        assert inv.equipped_weapon.item_id == "weapon_02"

    def test_equip_armor(self):
        """Test equipping armor."""
        from inventory import Inventory, Armor

        inv = Inventory()
        armor = Armor("armor_01", "Vest", "Protection", 800, 20, 0)

        inv.add_item(armor)
        result = inv.equip_armor("armor_01")

        assert result is True
        assert inv.equipped_armor is not None
        assert inv.equipped_armor.item_id == "armor_01"

    def test_unequip_weapon(self):
        """Test unequipping a weapon."""
        from inventory import Inventory, Weapon

        inv = Inventory()
        weapon = Weapon("weapon_01", "Rifle", "Gun", 1000, 30, 85, 10, 0.15, 2.0, "ranged")

        inv.add_item(weapon)
        inv.equip_weapon("weapon_01")
        inv.unequip_weapon()

        assert inv.equipped_weapon is None


class TestConsumables:
    """Test consumable item usage."""

    def test_use_consumable(self):
        """Test using a consumable item."""
        from inventory import Inventory, Consumable

        inv = Inventory()
        medkit = Consumable("medkit", "Medkit", "Heals", 100, "heal", 50,
                           stackable=True, max_stack=10)

        inv.add_item(medkit, quantity=3)

        effect = inv.use_consumable("medkit")

        assert effect is not None
        assert effect["effect"] == "heal"
        assert effect["amount"] == 50
        assert inv.get_item_quantity("medkit") == 2

    def test_cannot_use_nonexistent_consumable(self):
        """Test cannot use consumable not in inventory."""
        from inventory import Inventory

        inv = Inventory()
        effect = inv.use_consumable("fake_item")

        assert effect is None

    def test_cannot_use_non_consumable_item(self):
        """Test cannot use non-consumable as consumable."""
        from inventory import Inventory, Weapon

        inv = Inventory()
        weapon = Weapon("weapon_01", "Rifle", "Gun", 1000, 30, 85, 10, 0.15, 2.0, "ranged")

        inv.add_item(weapon)
        effect = inv.use_consumable("weapon_01")

        assert effect is None

    def test_consumable_with_duration(self):
        """Test consumable with duration effect."""
        from inventory import Consumable

        buff = Consumable("buff_01", "Adrenaline", "Speed boost", 200, "buff_speed", 2,
                         duration=5, stackable=True, max_stack=5)

        assert buff.duration == 5
        assert buff.effect == "buff_speed"


class TestItemQueries:
    """Test querying inventory contents."""

    def test_get_all_items(self):
        """Test getting all items in inventory."""
        from inventory import Inventory, Item

        inv = Inventory()

        inv.add_item(Item("item_1", "Item 1", "Desc", "misc", 10))
        inv.add_item(Item("item_2", "Item 2", "Desc", "misc", 20))

        all_items = inv.get_all_items()

        assert len(all_items) == 2

    def test_get_items_by_type(self):
        """Test getting items filtered by type."""
        from inventory import Inventory, Item, Weapon, Consumable

        inv = Inventory()

        inv.add_item(Item("item_1", "Misc", "Desc", "misc", 10))
        inv.add_item(Weapon("weapon_1", "Rifle", "Gun", 1000, 30, 85, 10, 0.15, 2.0, "ranged"))
        inv.add_item(Consumable("medkit", "Medkit", "Heals", 100, "heal", 50))

        weapons = inv.get_items_by_type("weapon")

        assert len(weapons) == 1
        assert weapons[0]["item"].item_type == "weapon"

    def test_has_item(self):
        """Test checking if inventory has an item."""
        from inventory import Inventory, Item

        inv = Inventory()
        inv.add_item(Item("item_1", "Item", "Desc", "misc", 10))

        assert inv.has_item("item_1") is True
        assert inv.has_item("fake_item") is False

    def test_get_total_value(self):
        """Test calculating total inventory value."""
        from inventory import Inventory, Item

        inv = Inventory()

        inv.add_item(Item("item_1", "Item 1", "Desc", "misc", 100))
        inv.add_item(Item("item_2", "Item 2", "Desc", "misc", 200))
        inv.add_item(Item("item_3", "Item 3", "Desc", "misc", 50), quantity=2)

        # 100 + 200 + (50 × 2) = 400
        assert inv.get_total_value() == 400


class TestInventoryPersistence:
    """Test inventory serialization for save/load."""

    def test_inventory_to_dict(self):
        """Test converting inventory to dictionary."""
        from inventory import Inventory, Item, Weapon

        inv = Inventory()
        inv.add_item(Item("item_1", "Item", "Desc", "misc", 10))
        inv.add_item(Weapon("weapon_1", "Rifle", "Gun", 1000, 30, 85, 10, 0.15, 2.0, "ranged"))

        inv_dict = inv.to_dict()

        assert "items" in inv_dict
        assert "max_capacity" in inv_dict
        assert len(inv_dict["items"]) == 2

    def test_inventory_from_dict(self):
        """Test loading inventory from dictionary."""
        from inventory import Inventory

        inv_data = {
            "max_capacity": 50,
            "items": {
                "item_1": {
                    "item": {
                        "item_id": "item_1",
                        "name": "Test Item",
                        "description": "Desc",
                        "item_type": "misc",
                        "value": 10,
                        "stackable": False,
                        "max_stack": 1
                    },
                    "quantity": 1
                }
            },
            "equipped_weapon": None,
            "equipped_armor": None
        }

        inv = Inventory.from_dict(inv_data)

        assert inv.max_capacity == 50
        assert inv.has_item("item_1")


class TestItemEffects:
    """Test item effects on character stats."""

    def test_weapon_damage_stat(self):
        """Test weapon provides damage stat."""
        from inventory import Weapon

        weapon = Weapon("weapon_01", "Rifle", "Gun", 1000, 35, 85, 10, 0.15, 2.0, "ranged")

        assert weapon.damage == 35
        assert weapon.accuracy == 85

    def test_armor_provides_armor_value(self):
        """Test armor provides armor value."""
        from inventory import Armor

        armor = Armor("armor_01", "Heavy Vest", "Protection", 1200, 30, 1)

        assert armor.armor_value == 30
        assert armor.mobility_penalty == 1

    def test_consumable_heal_effect(self):
        """Test consumable heal effect data."""
        from inventory import Consumable

        medkit = Consumable("medkit", "Medkit", "Heals 50 HP", 100, "heal", 50)

        effect_data = medkit.get_effect_data()

        assert effect_data["effect"] == "heal"
        assert effect_data["amount"] == 50


@pytest.mark.integration
class TestInventoryIntegration:
    """Integration tests for complete inventory workflows."""

    def test_complete_inventory_workflow(self):
        """Test complete workflow: add, equip, use items."""
        from inventory import Inventory, Weapon, Armor, Consumable

        inv = Inventory(max_capacity=20)

        # Add items
        weapon = Weapon("weapon_01", "Rifle", "Gun", 1000, 30, 85, 10, 0.15, 2.0, "ranged")
        armor = Armor("armor_01", "Vest", "Protection", 800, 20, 0)
        medkit = Consumable("medkit", "Medkit", "Heals", 100, "heal", 50,
                           stackable=True, max_stack=10)

        inv.add_item(weapon)
        inv.add_item(armor)
        inv.add_item(medkit, quantity=5)

        # Equip gear
        inv.equip_weapon("weapon_01")
        inv.equip_armor("armor_01")

        # Use consumable
        effect = inv.use_consumable("medkit")

        # Verify state
        assert inv.equipped_weapon.item_id == "weapon_01"
        assert inv.equipped_armor.item_id == "armor_01"
        assert inv.get_item_quantity("medkit") == 4
        assert effect["effect"] == "heal"

    def test_loot_from_combat(self):
        """Test receiving loot after combat."""
        from inventory import Inventory, Consumable, Item

        inv = Inventory()

        # Simulate loot drops
        loot = [
            Consumable("medkit", "Medkit", "Heals", 100, "heal", 50, stackable=True, max_stack=10),
            Item("credits", "Credits", "Money", "currency", 1, stackable=True, max_stack=9999),
        ]

        for item in loot:
            if item.item_id == "credits":
                inv.add_item(item, quantity=150)
            else:
                inv.add_item(item, quantity=1)

        assert inv.get_item_quantity("medkit") == 1
        assert inv.get_item_quantity("credits") == 150


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_inventory_operations(self):
        """Test operations on empty inventory."""
        from inventory import Inventory

        inv = Inventory()

        assert inv.get_item_count() == 0
        assert inv.get_total_value() == 0
        assert inv.get_all_items() == []

    def test_remove_more_items_than_available(self):
        """Test removing more items than in stack."""
        from inventory import Inventory, Consumable

        inv = Inventory()
        medkit = Consumable("medkit", "Medkit", "Heals", 100, "heal", 50,
                           stackable=True, max_stack=10)

        inv.add_item(medkit, quantity=3)
        result = inv.remove_item("medkit", quantity=5)

        # Should remove all 3 and return False
        assert result is False
        assert inv.get_item_quantity("medkit") == 0

    def test_zero_capacity_inventory(self):
        """Test inventory with zero capacity."""
        from inventory import Inventory, Item

        inv = Inventory(max_capacity=0)

        result = inv.add_item(Item("item_1", "Item", "Desc", "misc", 10))

        assert result is False
        assert inv.get_item_count() == 0

    def test_item_with_zero_value(self):
        """Test item with zero value."""
        from inventory import Item

        item = Item("item_1", "Worthless", "Trash", "junk", 0)

        assert item.value == 0

    def test_weapon_with_extreme_stats(self):
        """Test weapon with very high/low stats."""
        from inventory import Weapon

        # Super weapon
        weapon = Weapon("weapon_god", "Ultimate", "OP", 999999, 1000, 100, 999, 1.0, 10.0, "ranged")

        assert weapon.damage == 1000
        assert weapon.range == 999
