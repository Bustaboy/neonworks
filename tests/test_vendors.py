"""
Tests for Vendor/Trading System
Tests NPC merchants, pricing, buying/selling, faction discounts, and inventory management
"""

import pytest
from game.vendors import (
    Vendor,
    VendorInventory,
    VendorManager,
    TradeTransaction,
    VENDOR_TYPES,
    PRICE_MODIFIERS
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def basic_vendor():
    """Create a basic vendor."""
    return Vendor(
        vendor_id="vendor_ripperdoc",
        name="Doc Fingers",
        vendor_type="ripperdoc",
        faction="none",
        buy_modifier=0.5,  # Buys at 50% value
        sell_modifier=1.0  # Sells at 100% value
    )


@pytest.fixture
def faction_vendor():
    """Create a faction vendor."""
    return Vendor(
        vendor_id="vendor_militech",
        name="Militech Armory",
        vendor_type="weapon_shop",
        faction="militech",
        buy_modifier=0.6,
        sell_modifier=0.9  # 10% discount
    )


@pytest.fixture
def vendor_inventory():
    """Create a vendor inventory."""
    inventory = VendorInventory(vendor_id="vendor_test")

    # Add some items
    inventory.add_stock("weapon_pistol", quantity=5, base_price=500)
    inventory.add_stock("armor_vest", quantity=3, base_price=800)
    inventory.add_stock("consumable_medkit", quantity=10, base_price=100)

    return inventory


@pytest.fixture
def vendor_manager():
    """Create a vendor manager."""
    return VendorManager()


# ============================================================================
# TEST VENDOR CREATION
# ============================================================================

class TestVendorCreation:
    """Test vendor initialization."""

    def test_vendor_creation(self, basic_vendor):
        """Test creating a vendor."""
        assert basic_vendor.vendor_id == "vendor_ripperdoc"
        assert basic_vendor.name == "Doc Fingers"
        assert basic_vendor.vendor_type == "ripperdoc"
        assert basic_vendor.buy_modifier == 0.5
        assert basic_vendor.sell_modifier == 1.0

    def test_vendor_types_valid(self):
        """Test all vendor types are valid."""
        for vendor_type in VENDOR_TYPES:
            vendor = Vendor(
                vendor_id=f"vendor_{vendor_type}",
                name=f"Test {vendor_type}",
                vendor_type=vendor_type,
                faction="none",
                buy_modifier=0.5,
                sell_modifier=1.0
            )
            assert vendor.vendor_type == vendor_type

    def test_invalid_vendor_type_raises_error(self):
        """Test invalid vendor type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid vendor type"):
            Vendor(
                vendor_id="vendor_invalid",
                name="Invalid",
                vendor_type="invalid_type",
                faction="none",
                buy_modifier=0.5,
                sell_modifier=1.0
            )

    def test_vendor_has_credits(self):
        """Test vendor starts with credits."""
        vendor = Vendor(
            vendor_id="vendor_test",
            name="Test",
            vendor_type="general_store",
            faction="none",
            buy_modifier=0.5,
            sell_modifier=1.0,
            credits=5000
        )
        assert vendor.credits == 5000


# ============================================================================
# TEST VENDOR INVENTORY
# ============================================================================

class TestVendorInventory:
    """Test vendor inventory management."""

    def test_add_stock(self, vendor_inventory):
        """Test adding stock to inventory."""
        vendor_inventory.add_stock("new_item", quantity=5, base_price=200)

        assert vendor_inventory.has_item("new_item") is True
        assert vendor_inventory.get_quantity("new_item") == 5

    def test_remove_stock(self, vendor_inventory):
        """Test removing stock from inventory."""
        initial_qty = vendor_inventory.get_quantity("weapon_pistol")
        vendor_inventory.remove_stock("weapon_pistol", 2)

        assert vendor_inventory.get_quantity("weapon_pistol") == initial_qty - 2

    def test_cannot_remove_more_than_available(self, vendor_inventory):
        """Test cannot remove more stock than available."""
        result = vendor_inventory.remove_stock("weapon_pistol", 100)

        assert result is False
        assert vendor_inventory.get_quantity("weapon_pistol") == 5

    def test_get_all_items(self, vendor_inventory):
        """Test getting all items in stock."""
        items = vendor_inventory.get_all_items()

        assert len(items) == 3
        assert "weapon_pistol" in items

    def test_restock_item(self, vendor_inventory):
        """Test restocking an existing item."""
        vendor_inventory.remove_stock("consumable_medkit", 8)
        vendor_inventory.restock("consumable_medkit", 10)

        assert vendor_inventory.get_quantity("consumable_medkit") == 12


# ============================================================================
# TEST PRICING
# ============================================================================

class TestPricing:
    """Test pricing calculations."""

    def test_base_sell_price(self, basic_vendor, vendor_inventory):
        """Test calculating sell price to player."""
        # Base price is 500, sell modifier is 1.0
        price = basic_vendor.calculate_sell_price("weapon_pistol", vendor_inventory)

        assert price == 500

    def test_base_buy_price(self, basic_vendor):
        """Test calculating buy price from player."""
        # Item worth 1000, buy modifier is 0.5
        price = basic_vendor.calculate_buy_price(item_value=1000)

        assert price == 500

    def test_faction_discount(self, faction_vendor, vendor_inventory):
        """Test faction members get discounts."""
        # Base price 500, sell modifier 0.9 (10% discount)
        price = faction_vendor.calculate_sell_price("weapon_pistol", vendor_inventory)

        assert price == 450

    def test_reputation_discount(self, basic_vendor, vendor_inventory):
        """Test high reputation provides additional discount."""
        # Rep level 5 = 10% discount
        price = basic_vendor.calculate_sell_price(
            "weapon_pistol",
            vendor_inventory,
            player_faction_rep=50  # Level 5 rep
        )

        # 500 base * 1.0 sell modifier * 0.9 rep discount = 450
        assert price == 450

    def test_combined_discounts(self, faction_vendor, vendor_inventory):
        """Test faction and reputation discounts stack."""
        # Faction 10% + Rep 10% = ~19% total discount
        price = faction_vendor.calculate_sell_price(
            "weapon_pistol",
            vendor_inventory,
            player_faction_rep=50
        )

        # 500 * 0.9 (faction) * 0.9 (rep) = 405
        assert price == 405


# ============================================================================
# TEST BUYING
# ============================================================================

class TestBuying:
    """Test player buying from vendor."""

    def test_buy_item_success(self, basic_vendor, vendor_inventory):
        """Test successful purchase."""
        player_credits = 1000

        transaction = basic_vendor.sell_to_player(
            item_id="weapon_pistol",
            quantity=1,
            player_credits=player_credits,
            vendor_inventory=vendor_inventory
        )

        assert transaction.success is True
        assert transaction.credits_spent == 500
        assert transaction.item_id == "weapon_pistol"
        assert transaction.quantity == 1

    def test_buy_insufficient_credits(self, basic_vendor, vendor_inventory):
        """Test purchase fails with insufficient credits."""
        player_credits = 100  # Not enough for 500 credit pistol

        transaction = basic_vendor.sell_to_player(
            item_id="weapon_pistol",
            quantity=1,
            player_credits=player_credits,
            vendor_inventory=vendor_inventory
        )

        assert transaction.success is False
        assert "Insufficient credits" in transaction.error

    def test_buy_out_of_stock(self, basic_vendor, vendor_inventory):
        """Test purchase fails when item out of stock."""
        transaction = basic_vendor.sell_to_player(
            item_id="weapon_pistol",
            quantity=100,  # Only 5 in stock
            player_credits=50000,
            vendor_inventory=vendor_inventory
        )

        assert transaction.success is False
        assert "out of stock" in transaction.error

    def test_buy_multiple_items(self, basic_vendor, vendor_inventory):
        """Test buying multiple of same item."""
        transaction = basic_vendor.sell_to_player(
            item_id="consumable_medkit",
            quantity=3,
            player_credits=1000,
            vendor_inventory=vendor_inventory
        )

        assert transaction.success is True
        assert transaction.quantity == 3
        assert transaction.credits_spent == 300  # 100 * 3


# ============================================================================
# TEST SELLING
# ============================================================================

class TestSelling:
    """Test player selling to vendor."""

    def test_sell_item_success(self, basic_vendor):
        """Test successful sale to vendor."""
        transaction = basic_vendor.buy_from_player(
            item_value=1000,
            quantity=1,
            vendor_credits=5000
        )

        assert transaction.success is True
        assert transaction.credits_gained == 500  # 50% buy modifier

    def test_sell_vendor_insufficient_credits(self, basic_vendor):
        """Test vendor cannot buy if insufficient credits."""
        transaction = basic_vendor.buy_from_player(
            item_value=10000,
            quantity=1,
            vendor_credits=1000  # Not enough
        )

        assert transaction.success is False
        assert "not enough credits" in transaction.error

    def test_sell_multiple_items(self, basic_vendor):
        """Test selling multiple items."""
        transaction = basic_vendor.buy_from_player(
            item_value=200,
            quantity=5,
            vendor_credits=5000
        )

        assert transaction.success is True
        # 200 * 5 * 0.5 buy modifier = 500
        assert transaction.credits_gained == 500


# ============================================================================
# TEST VENDOR MANAGER
# ============================================================================

class TestVendorManager:
    """Test vendor manager operations."""

    def test_add_vendor(self, vendor_manager, basic_vendor):
        """Test adding vendor to manager."""
        vendor_manager.add_vendor(basic_vendor)

        assert len(vendor_manager.get_all_vendors()) == 1

    def test_get_vendor_by_id(self, vendor_manager, basic_vendor):
        """Test retrieving vendor by ID."""
        vendor_manager.add_vendor(basic_vendor)

        vendor = vendor_manager.get_vendor("vendor_ripperdoc")

        assert vendor == basic_vendor

    def test_get_vendors_by_type(self, vendor_manager, basic_vendor, faction_vendor):
        """Test filtering vendors by type."""
        vendor_manager.add_vendor(basic_vendor)
        vendor_manager.add_vendor(faction_vendor)

        weapon_shops = vendor_manager.get_vendors_by_type("weapon_shop")

        assert len(weapon_shops) == 1
        assert faction_vendor in weapon_shops

    def test_get_vendors_by_faction(self, vendor_manager, faction_vendor):
        """Test filtering vendors by faction."""
        vendor_manager.add_vendor(faction_vendor)

        militech_vendors = vendor_manager.get_vendors_by_faction("militech")

        assert len(militech_vendors) == 1

    def test_vendor_restock_time(self, vendor_manager, basic_vendor, vendor_inventory):
        """Test vendors restock after time."""
        vendor_manager.add_vendor(basic_vendor)
        vendor_manager.set_inventory(basic_vendor.vendor_id, vendor_inventory)

        # Remove stock
        vendor_inventory.remove_stock("weapon_pistol", 3)
        assert vendor_inventory.get_quantity("weapon_pistol") == 2

        # Trigger restock
        vendor_manager.restock_vendor(basic_vendor.vendor_id)

        # Should be back to original 5
        assert vendor_inventory.get_quantity("weapon_pistol") == 5


# ============================================================================
# TEST SPECIAL VENDORS
# ============================================================================

class TestSpecialVendors:
    """Test special vendor types."""

    def test_ripperdoc_sells_cyberware(self):
        """Test ripperdoc vendors sell cyberware."""
        ripper = Vendor(
            vendor_id="vendor_ripper",
            name="Ripper",
            vendor_type="ripperdoc",
            faction="none",
            buy_modifier=0.5,
            sell_modifier=1.0
        )

        inventory = VendorInventory("vendor_ripper")
        inventory.add_stock("cyber_mantis_blades", 1, 15000)

        assert inventory.has_item("cyber_mantis_blades") is True

    def test_fixer_provides_missions(self):
        """Test fixer vendors can provide missions."""
        fixer = Vendor(
            vendor_id="vendor_fixer",
            name="Wakako",
            vendor_type="fixer",
            faction="tyger_claws",
            buy_modifier=0.7,
            sell_modifier=1.0,
            special_services=["missions", "intel"]
        )

        assert "missions" in fixer.special_services

    def test_black_market_premium_prices(self):
        """Test black market vendors have higher prices."""
        black_market = Vendor(
            vendor_id="vendor_black_market",
            name="Shady Dealer",
            vendor_type="black_market",
            faction="none",
            buy_modifier=0.4,  # Buys low
            sell_modifier=1.3  # Sells high (30% markup)
        )

        assert black_market.sell_modifier > 1.0


# ============================================================================
# TEST TRADE HISTORY
# ============================================================================

class TestTradeHistory:
    """Test trade transaction history."""

    def test_record_transaction(self, vendor_manager, basic_vendor):
        """Test recording trade transactions."""
        vendor_manager.add_vendor(basic_vendor)

        transaction = TradeTransaction(
            transaction_type="buy",
            item_id="weapon_pistol",
            quantity=1,
            credits_spent=500,
            success=True
        )

        vendor_manager.record_transaction(basic_vendor.vendor_id, transaction)

        history = vendor_manager.get_transaction_history(basic_vendor.vendor_id)
        assert len(history) == 1

    def test_get_total_spent(self, vendor_manager, basic_vendor):
        """Test calculating total credits spent at vendor."""
        vendor_manager.add_vendor(basic_vendor)

        # Record multiple purchases
        for i in range(3):
            transaction = TradeTransaction(
                transaction_type="buy",
                item_id="item",
                quantity=1,
                credits_spent=100,
                success=True
            )
            vendor_manager.record_transaction(basic_vendor.vendor_id, transaction)

        total = vendor_manager.get_total_spent(basic_vendor.vendor_id)
        assert total == 300


# ============================================================================
# TEST SERIALIZATION
# ============================================================================

class TestVendorSerialization:
    """Test vendor serialization."""

    def test_vendor_serialization(self, basic_vendor):
        """Test vendor to_dict and from_dict."""
        data = basic_vendor.to_dict()
        restored = Vendor.from_dict(data)

        assert restored.vendor_id == basic_vendor.vendor_id
        assert restored.name == basic_vendor.name
        assert restored.buy_modifier == basic_vendor.buy_modifier

    def test_vendor_inventory_serialization(self, vendor_inventory):
        """Test vendor inventory serialization."""
        data = vendor_inventory.to_dict()
        restored = VendorInventory.from_dict(data)

        assert restored.get_quantity("weapon_pistol") == 5
        assert restored.get_quantity("consumable_medkit") == 10

    def test_vendor_manager_serialization(
        self,
        vendor_manager,
        basic_vendor,
        vendor_inventory
    ):
        """Test vendor manager serialization."""
        vendor_manager.add_vendor(basic_vendor)
        vendor_manager.set_inventory(basic_vendor.vendor_id, vendor_inventory)

        data = vendor_manager.to_dict()
        restored = VendorManager.from_dict(data)

        assert len(restored.get_all_vendors()) == 1
        vendor = restored.get_vendor("vendor_ripperdoc")
        assert vendor.name == "Doc Fingers"


# ============================================================================
# TEST EDGE CASES
# ============================================================================

class TestVendorEdgeCases:
    """Test edge cases and error handling."""

    def test_buy_unknown_item(self, basic_vendor, vendor_inventory):
        """Test buying item not in stock."""
        transaction = basic_vendor.sell_to_player(
            item_id="unknown_item",
            quantity=1,
            player_credits=1000,
            vendor_inventory=vendor_inventory
        )

        assert transaction.success is False

    def test_zero_quantity_purchase(self, basic_vendor, vendor_inventory):
        """Test buying zero quantity."""
        transaction = basic_vendor.sell_to_player(
            item_id="weapon_pistol",
            quantity=0,
            player_credits=1000,
            vendor_inventory=vendor_inventory
        )

        assert transaction.success is False

    def test_negative_credits(self, basic_vendor):
        """Test selling with negative vendor credits."""
        transaction = basic_vendor.buy_from_player(
            item_value=100,
            quantity=1,
            vendor_credits=-100
        )

        assert transaction.success is False


# ============================================================================
# TEST INTEGRATION
# ============================================================================

class TestVendorIntegration:
    """Test integration with other game systems."""

    def test_vendor_faction_integration(self, faction_vendor):
        """Test vendor integrates with faction system."""
        assert faction_vendor.faction == "militech"
        # High faction rep should provide discount
        # (tested in test_reputation_discount)

    def test_vendor_inventory_integration(self, vendor_inventory):
        """Test vendor inventory integrates with item system."""
        # Vendor sells actual game items
        assert vendor_inventory.has_item("weapon_pistol")
        assert vendor_inventory.has_item("armor_vest")
        assert vendor_inventory.has_item("consumable_medkit")
