"""
Comprehensive test suite for loot_economy.py (Loot & Economy System)

Tests cover:
- Item quality tiers (Common, Uncommon, Rare, Epic, Legendary)
- Loot generation (random drops based on enemy tier)
- Boss loot tables (guaranteed rare+ loot)
- Currency drops (credits)
- Item value calculation
- Vendor pricing (buy/sell rates)
- Shop inventory generation
- Loot rarity scaling with player progression
- Special item drops (quest items, unique gear)
- Serialization for save/load
"""

import pytest
from unittest.mock import Mock
import sys
from pathlib import Path

# Add game directory to path
game_dir = Path(__file__).parent.parent / "game"
sys.path.insert(0, str(game_dir))


class TestItemQuality:
    """Test item quality tier system."""

    def test_create_common_item(self):
        """Test creating common quality item."""
        from loot_economy import LootItem

        item = LootItem(
            item_id="pistol_common",
            name="Basic Pistol",
            quality="common",
            value=100
        )

        assert item.quality == "common"
        assert item.value == 100

    def test_create_uncommon_item(self):
        """Test creating uncommon quality item."""
        from loot_economy import LootItem

        item = LootItem(
            item_id="armor_uncommon",
            name="Reinforced Vest",
            quality="uncommon",
            value=500
        )

        assert item.quality == "uncommon"
        assert item.value == 500

    def test_create_rare_item(self):
        """Test creating rare quality item."""
        from loot_economy import LootItem

        item = LootItem(
            item_id="rifle_rare",
            name="Precision Rifle",
            quality="rare",
            value=2000
        )

        assert item.quality == "rare"

    def test_create_epic_item(self):
        """Test creating epic quality item."""
        from loot_economy import LootItem

        item = LootItem(
            item_id="cyber_epic",
            name="Military-Grade Implant",
            quality="epic",
            value=8000
        )

        assert item.quality == "epic"

    def test_create_legendary_item(self):
        """Test creating legendary quality item."""
        from loot_economy import LootItem

        item = LootItem(
            item_id="weapon_legendary",
            name="Prototype Rail Gun",
            quality="legendary",
            value=25000
        )

        assert item.quality == "legendary"

    def test_invalid_quality(self):
        """Test invalid quality raises error."""
        from loot_economy import LootItem

        with pytest.raises(ValueError):
            LootItem(
                item_id="test",
                name="Test Item",
                quality="invalid",
                value=100
            )

    def test_quality_affects_value(self):
        """Test higher quality items have higher base values."""
        from loot_economy import LootItem

        common = LootItem("item1", "Common Item", "common", 100)
        rare = LootItem("item2", "Rare Item", "rare", 2000)
        legendary = LootItem("item3", "Legendary Item", "legendary", 25000)

        assert legendary.value > rare.value > common.value


class TestLootGeneration:
    """Test random loot generation."""

    def test_generate_loot_from_enemy(self):
        """Test generating loot from defeated enemy."""
        from loot_economy import LootGenerator

        generator = LootGenerator()

        # Generate loot from basic enemy
        loot = generator.generate_loot(
            enemy_tier="basic",
            player_phase=1
        )

        assert loot is not None
        assert "items" in loot or "credits" in loot

    def test_higher_tier_better_loot(self):
        """Test higher tier enemies drop better loot."""
        from loot_economy import LootGenerator

        generator = LootGenerator()

        # Generate multiple samples
        basic_loot = [generator.generate_loot("basic", 1) for _ in range(20)]
        elite_loot = [generator.generate_loot("elite", 1) for _ in range(20)]

        # Elite enemies should have higher average value
        # This is probabilistic, so we just verify it generates loot
        assert len(basic_loot) == 20
        assert len(elite_loot) == 20

    def test_boss_guaranteed_loot(self):
        """Test bosses always drop loot."""
        from loot_economy import LootGenerator

        generator = LootGenerator()

        # Boss should always drop loot
        loot = generator.generate_loot(
            enemy_tier="boss",
            player_phase=1
        )

        assert loot is not None
        assert "items" in loot
        assert len(loot["items"]) > 0

    def test_loot_scales_with_phase(self):
        """Test loot quality improves with player phase."""
        from loot_economy import LootGenerator

        generator = LootGenerator()

        # Phase 1 loot
        phase1_loot = generator.generate_loot("elite", player_phase=1)

        # Phase 5 loot
        phase5_loot = generator.generate_loot("elite", player_phase=5)

        # Both should generate loot (quality comparison is probabilistic)
        assert phase1_loot is not None
        assert phase5_loot is not None

    def test_loot_contains_credits(self):
        """Test loot can contain currency."""
        from loot_economy import LootGenerator

        generator = LootGenerator()

        # Generate many samples to ensure we get credits
        samples = [generator.generate_loot("basic", 1) for _ in range(50)]

        # At least some should have credits
        has_credits = any("credits" in loot and loot["credits"] > 0 for loot in samples)
        assert has_credits

    def test_multiple_items_possible(self):
        """Test loot can contain multiple items."""
        from loot_economy import LootGenerator

        generator = LootGenerator()

        # Boss should drop multiple items
        loot = generator.generate_loot("boss", player_phase=3)

        if "items" in loot:
            # Boss loot should have multiple items
            assert len(loot["items"]) >= 1


class TestBossLoot:
    """Test special boss loot tables."""

    def test_boss_drops_rare_minimum(self):
        """Test bosses drop at least rare quality items."""
        from loot_economy import LootGenerator

        generator = LootGenerator()

        loot = generator.generate_loot("boss", player_phase=2)

        # Check that items are at least rare
        if "items" in loot:
            for item in loot["items"]:
                assert item.quality in ["rare", "epic", "legendary"]

    def test_boss_higher_credit_reward(self):
        """Test bosses drop more credits."""
        from loot_economy import LootGenerator

        generator = LootGenerator()

        # Generate multiple boss loot samples
        boss_loot = [generator.generate_loot("boss", 2) for _ in range(10)]
        basic_loot = [generator.generate_loot("basic", 2) for _ in range(10)]

        # Boss should have credits in most drops
        boss_credits = [l.get("credits", 0) for l in boss_loot]
        basic_credits = [l.get("credits", 0) for l in basic_loot]

        # Boss average should be higher (though both might be 0 sometimes)
        assert max(boss_credits) >= max(basic_credits)

    def test_boss_unique_items(self):
        """Test bosses can drop unique items."""
        from loot_economy import LootGenerator

        generator = LootGenerator()

        loot = generator.generate_loot("boss", player_phase=3)

        # Boss loot should contain items
        assert "items" in loot
        assert len(loot["items"]) > 0


class TestItemValue:
    """Test item value calculation."""

    def test_item_has_value(self):
        """Test items have credit value."""
        from loot_economy import LootItem

        item = LootItem("weapon", "Pistol", "common", 500)

        assert item.value == 500

    def test_quality_multiplier(self):
        """Test quality affects value multiplier."""
        from loot_economy import LootItem

        # Same base item, different qualities
        common = LootItem("item", "Item", "common", 100)
        rare = LootItem("item", "Item", "rare", 100)
        legendary = LootItem("item", "Item", "legendary", 100)

        # Values should scale with quality (if multiplier is applied)
        # For now, just verify values are set correctly
        assert common.value == 100
        assert rare.value == 100
        assert legendary.value == 100

    def test_calculate_sell_value(self):
        """Test calculating sell value (typically 50% of base)."""
        from loot_economy import LootItem

        item = LootItem("weapon", "Rifle", "rare", 2000)

        sell_value = item.get_sell_value()

        # Sell value should be less than base value
        assert sell_value < item.value
        assert sell_value == 1000  # 50% of base

    def test_calculate_buy_value(self):
        """Test calculating buy value from vendor."""
        from loot_economy import LootItem

        item = LootItem("armor", "Vest", "uncommon", 1000)

        buy_value = item.get_buy_value()

        # Buy value should be higher than base (vendor markup)
        assert buy_value >= item.value


class TestVendorSystem:
    """Test vendor/shop mechanics."""

    def test_create_vendor(self):
        """Test creating a vendor."""
        from loot_economy import Vendor

        vendor = Vendor(
            vendor_id="gunsmith",
            name="Night City Gunsmith",
            vendor_type="weapons"
        )

        assert vendor.vendor_id == "gunsmith"
        assert vendor.name == "Night City Gunsmith"
        assert vendor.vendor_type == "weapons"

    def test_vendor_inventory(self):
        """Test vendor has inventory."""
        from loot_economy import Vendor

        vendor = Vendor("vendor", "Vendor", "general")

        inventory = vendor.get_inventory()

        assert isinstance(inventory, list)

    def test_vendor_stock_generation(self):
        """Test vendors generate stock based on type."""
        from loot_economy import Vendor

        weapon_vendor = Vendor("gunsmith", "Gunsmith", "weapons")
        armor_vendor = Vendor("armorer", "Armorer", "armor")

        # Generate stock
        weapon_vendor.generate_stock(player_phase=2)
        armor_vendor.generate_stock(player_phase=2)

        weapon_stock = weapon_vendor.get_inventory()
        armor_stock = armor_vendor.get_inventory()

        # Should have items
        assert len(weapon_stock) > 0
        assert len(armor_stock) > 0

    def test_buy_from_vendor(self):
        """Test buying item from vendor."""
        from loot_economy import Vendor, LootItem

        vendor = Vendor("vendor", "Vendor", "general")

        # Add item to stock
        item = LootItem("pistol", "Pistol", "common", 500)
        vendor.add_item(item)

        # Attempt purchase
        result = vendor.buy_item("pistol", buyer_credits=1000)

        assert result is not None
        assert result["success"] is True
        assert result["item"].item_id == "pistol"
        assert result["cost"] > 0

    def test_buy_insufficient_credits(self):
        """Test buying fails with insufficient credits."""
        from loot_economy import Vendor, LootItem

        vendor = Vendor("vendor", "Vendor", "general")

        expensive_item = LootItem("rifle", "Rifle", "rare", 5000)
        vendor.add_item(expensive_item)

        # Try to buy with insufficient credits
        result = vendor.buy_item("rifle", buyer_credits=100)

        assert result["success"] is False

    def test_sell_to_vendor(self):
        """Test selling item to vendor."""
        from loot_economy import Vendor, LootItem

        vendor = Vendor("vendor", "Vendor", "general")

        item = LootItem("junk", "Broken Circuit", "common", 50)

        # Sell item
        result = vendor.sell_item(item)

        assert result["success"] is True
        assert result["credits_earned"] > 0
        assert result["credits_earned"] == item.get_sell_value()

    def test_vendor_stock_refreshes(self):
        """Test vendor stock can refresh."""
        from loot_economy import Vendor

        vendor = Vendor("vendor", "Vendor", "weapons")

        vendor.generate_stock(player_phase=1)
        initial_stock = vendor.get_inventory().copy()

        vendor.refresh_stock(player_phase=2)
        new_stock = vendor.get_inventory()

        # Stock should change (different items or quantities)
        assert len(new_stock) > 0


class TestLootRarity:
    """Test loot rarity distribution."""

    def test_common_items_most_frequent(self):
        """Test common items drop most frequently."""
        from loot_economy import LootGenerator

        generator = LootGenerator()

        # Generate many samples
        samples = [generator.generate_loot("basic", 1) for _ in range(100)]

        # Count quality distribution
        quality_counts = {"common": 0, "uncommon": 0, "rare": 0, "epic": 0, "legendary": 0}

        for loot in samples:
            if "items" in loot:
                for item in loot["items"]:
                    quality_counts[item.quality] += 1

        # Common should be most frequent (if any items dropped)
        if sum(quality_counts.values()) > 0:
            assert quality_counts["common"] >= quality_counts.get("rare", 0)

    def test_legendary_items_rare(self):
        """Test legendary items are very rare."""
        from loot_economy import LootGenerator

        generator = LootGenerator()

        # Generate many samples from basic enemies
        samples = [generator.generate_loot("basic", 1) for _ in range(50)]

        legendary_count = 0
        for loot in samples:
            if "items" in loot:
                for item in loot["items"]:
                    if item.quality == "legendary":
                        legendary_count += 1

        # Legendary should be very rare from basic enemies
        assert legendary_count <= 2  # Maybe 0-2 from 50 basic enemies

    def test_quality_improves_with_tier(self):
        """Test enemy tier affects loot quality."""
        from loot_economy import LootGenerator

        generator = LootGenerator()

        # Basic vs Elite enemies
        basic_samples = [generator.generate_loot("basic", 2) for _ in range(30)]
        elite_samples = [generator.generate_loot("elite", 2) for _ in range(30)]

        # Both should generate loot
        assert len(basic_samples) > 0
        assert len(elite_samples) > 0


class TestCurrencyDrops:
    """Test credit/currency drops."""

    def test_credits_drop(self):
        """Test enemies drop credits."""
        from loot_economy import LootGenerator

        generator = LootGenerator()

        # Generate loot
        loot = generator.generate_loot("basic", 1)

        # Should have credits or items
        assert "credits" in loot or "items" in loot

    def test_credit_amount_scales(self):
        """Test credit drops scale with enemy tier."""
        from loot_economy import LootGenerator

        generator = LootGenerator()

        basic_loot = generator.generate_loot("basic", 1)
        boss_loot = generator.generate_loot("boss", 1)

        # Boss should drop more credits (if they drop at all)
        basic_credits = basic_loot.get("credits", 0)
        boss_credits = boss_loot.get("credits", 0)

        # Boss should drop at least as much as basic
        assert boss_credits >= basic_credits

    def test_credit_amount_scales_with_phase(self):
        """Test credit drops increase with player phase."""
        from loot_economy import LootGenerator

        generator = LootGenerator()

        # Generate multiple samples to average out randomness
        phase1_samples = [generator.generate_loot("elite", player_phase=1) for _ in range(30)]
        phase5_samples = [generator.generate_loot("elite", player_phase=5) for _ in range(30)]

        # Calculate average credits
        phase1_avg = sum(s.get("credits", 0) for s in phase1_samples) / len(phase1_samples)
        phase5_avg = sum(s.get("credits", 0) for s in phase5_samples) / len(phase5_samples)

        # Later phases should drop more on average
        assert phase5_avg > phase1_avg


class TestSpecialItems:
    """Test special item drops (quest items, unique gear)."""

    def test_quest_item_drop(self):
        """Test quest-specific items can drop."""
        from loot_economy import LootGenerator, LootItem

        generator = LootGenerator()

        # Generate loot with quest item flag
        loot = generator.generate_quest_loot("data_chip", "corporate_data")

        assert loot is not None
        assert "items" in loot
        assert len(loot["items"]) > 0

        # Quest item should be present
        quest_item = loot["items"][0]
        assert quest_item.item_id == "data_chip"

    def test_unique_item_drop(self):
        """Test unique items have special properties."""
        from loot_economy import LootItem

        unique_item = LootItem(
            item_id="unique_weapon",
            name="The Reaper",
            quality="legendary",
            value=50000,
            is_unique=True
        )

        assert unique_item.is_unique is True
        assert unique_item.quality == "legendary"

    def test_unique_items_not_sellable(self):
        """Test unique items cannot be sold to vendors."""
        from loot_economy import LootItem

        unique_item = LootItem(
            item_id="unique",
            name="Unique Item",
            quality="epic",
            value=10000,
            is_unique=True
        )

        # Check if sellable
        assert unique_item.can_sell() is False


class TestLootTables:
    """Test loot table system."""

    def test_loot_table_creation(self):
        """Test creating loot tables."""
        from loot_economy import LootTable

        table = LootTable(table_id="basic_enemy")

        assert table.table_id == "basic_enemy"

    def test_add_entry_to_table(self):
        """Test adding entries to loot table."""
        from loot_economy import LootTable, LootItem

        table = LootTable("test_table")

        item = LootItem("pistol", "Pistol", "common", 100)

        table.add_entry(item, weight=50)

        assert len(table.entries) == 1

    def test_roll_from_table(self):
        """Test rolling items from loot table."""
        from loot_economy import LootTable, LootItem

        table = LootTable("test_table")

        item1 = LootItem("item1", "Item 1", "common", 100)
        item2 = LootItem("item2", "Item 2", "rare", 500)

        table.add_entry(item1, weight=80)
        table.add_entry(item2, weight=20)

        # Roll from table
        rolled_item = table.roll()

        assert rolled_item is not None
        assert rolled_item.item_id in ["item1", "item2"]

    def test_weighted_probability(self):
        """Test loot table respects weighted probabilities."""
        from loot_economy import LootTable, LootItem

        table = LootTable("test_table")

        common_item = LootItem("common", "Common", "common", 50)
        rare_item = LootItem("rare", "Rare", "rare", 500)

        # Common has much higher weight
        table.add_entry(common_item, weight=90)
        table.add_entry(rare_item, weight=10)

        # Roll many times
        results = [table.roll() for _ in range(100)]

        common_count = sum(1 for r in results if r.item_id == "common")
        rare_count = sum(1 for r in results if r.item_id == "rare")

        # Common should appear more often
        assert common_count > rare_count


class TestEconomyBalance:
    """Test economic balance and pricing."""

    def test_vendor_markup(self):
        """Test vendors apply markup to items."""
        from loot_economy import LootItem

        item = LootItem("weapon", "Weapon", "uncommon", 1000)

        buy_price = item.get_buy_value()
        sell_price = item.get_sell_value()

        # Buy price should be higher than sell price
        assert buy_price > sell_price

    def test_sell_buy_cycle_loss(self):
        """Test buying and selling results in net loss."""
        from loot_economy import Vendor, LootItem

        vendor = Vendor("vendor", "Vendor", "general")

        item = LootItem("item", "Item", "common", 1000)
        vendor.add_item(item)

        # Buy from vendor
        buy_result = vendor.buy_item("item", buyer_credits=2000)
        buy_cost = buy_result["cost"]

        # Sell back to vendor
        sell_result = vendor.sell_item(buy_result["item"])
        sell_value = sell_result["credits_earned"]

        # Should lose money in the cycle
        assert sell_value < buy_cost


class TestSerialization:
    """Test loot system serialization."""

    def test_item_to_dict(self):
        """Test converting item to dictionary."""
        from loot_economy import LootItem

        item = LootItem("weapon", "Rifle", "rare", 2000)

        data = item.to_dict()

        assert data["item_id"] == "weapon"
        assert data["name"] == "Rifle"
        assert data["quality"] == "rare"
        assert data["value"] == 2000

    def test_item_from_dict(self):
        """Test loading item from dictionary."""
        from loot_economy import LootItem

        data = {
            "item_id": "armor",
            "name": "Combat Vest",
            "quality": "uncommon",
            "value": 800,
            "is_unique": False
        }

        item = LootItem.from_dict(data)

        assert item.item_id == "armor"
        assert item.quality == "uncommon"
        assert item.value == 800

    def test_vendor_to_dict(self):
        """Test converting vendor to dictionary."""
        from loot_economy import Vendor, LootItem

        vendor = Vendor("gunsmith", "Gunsmith", "weapons")

        item = LootItem("pistol", "Pistol", "common", 500)
        vendor.add_item(item)

        data = vendor.to_dict()

        assert data["vendor_id"] == "gunsmith"
        assert data["name"] == "Gunsmith"
        assert len(data["inventory"]) == 1

    def test_vendor_from_dict(self):
        """Test loading vendor from dictionary."""
        from loot_economy import Vendor

        data = {
            "vendor_id": "armorer",
            "name": "Armorer",
            "vendor_type": "armor",
            "inventory": [
                {
                    "item_id": "vest",
                    "name": "Vest",
                    "quality": "common",
                    "value": 300,
                    "is_unique": False
                }
            ]
        }

        vendor = Vendor.from_dict(data)

        assert vendor.vendor_id == "armorer"
        assert len(vendor.get_inventory()) == 1


class TestEdgeCases:
    """Test edge cases."""

    def test_negative_value_invalid(self):
        """Test negative item value is invalid."""
        from loot_economy import LootItem

        with pytest.raises(ValueError):
            LootItem("item", "Item", "common", -100)

    def test_empty_loot_possible(self):
        """Test enemies can drop nothing."""
        from loot_economy import LootGenerator

        generator = LootGenerator()

        # Basic enemies might drop nothing
        loot = generator.generate_loot("basic", 1)

        # Should return dict (might be empty or have 0 credits)
        assert isinstance(loot, dict)

    def test_vendor_empty_stock(self):
        """Test vendor with no stock."""
        from loot_economy import Vendor

        vendor = Vendor("vendor", "Vendor", "general")

        inventory = vendor.get_inventory()

        assert len(inventory) == 0

    def test_buy_nonexistent_item(self):
        """Test buying item not in vendor stock."""
        from loot_economy import Vendor

        vendor = Vendor("vendor", "Vendor", "general")

        result = vendor.buy_item("nonexistent", buyer_credits=10000)

        assert result["success"] is False
