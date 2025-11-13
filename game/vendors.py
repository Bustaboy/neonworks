"""
Neon Collapse - Vendor/Trading System
Manages NPC merchants, pricing, buying/selling, and trade transactions
"""

from typing import Dict, List, Any, Optional


# Constants
VENDOR_TYPES = ["general_store", "weapon_shop", "ripperdoc", "fixer", "black_market", "netrunner_shop"]
PRICE_MODIFIERS = {
    "reputation": {
        0: 1.0,   # No discount
        25: 0.95,  # 5% discount at rep 25
        50: 0.90,  # 10% discount at rep 50
        75: 0.85,  # 15% discount at rep 75
        100: 0.80  # 20% discount at rep 100
    }
}


# ============================================================================
# TRADE TRANSACTION CLASS
# ============================================================================

class TradeTransaction:
    """Represents a trade transaction."""

    def __init__(
        self,
        transaction_type: str,  # "buy" or "sell"
        item_id: str,
        quantity: int,
        success: bool,
        credits_spent: int = 0,
        credits_gained: int = 0,
        error: str = ""
    ):
        self.transaction_type = transaction_type
        self.item_id = item_id
        self.quantity = quantity
        self.success = success
        self.credits_spent = credits_spent
        self.credits_gained = credits_gained
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "transaction_type": self.transaction_type,
            "item_id": self.item_id,
            "quantity": self.quantity,
            "success": self.success,
            "credits_spent": self.credits_spent,
            "credits_gained": self.credits_gained,
            "error": self.error
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TradeTransaction':
        """Load from dictionary."""
        return cls(
            transaction_type=data["transaction_type"],
            item_id=data["item_id"],
            quantity=data["quantity"],
            success=data["success"],
            credits_spent=data.get("credits_spent", 0),
            credits_gained=data.get("credits_gained", 0),
            error=data.get("error", "")
        )


# ============================================================================
# VENDOR INVENTORY CLASS
# ============================================================================

class VendorInventory:
    """Manages a vendor's stock."""

    def __init__(self, vendor_id: str):
        self.vendor_id = vendor_id
        self.stock: Dict[str, int] = {}  # item_id -> quantity
        self.prices: Dict[str, int] = {}  # item_id -> base_price
        self.original_stock: Dict[str, int] = {}  # For restocking

    def add_stock(self, item_id: str, quantity: int, base_price: int):
        """
        Add item to stock.

        Args:
            item_id: Item ID
            quantity: Quantity to add
            base_price: Base price of item
        """
        if item_id not in self.stock:
            self.stock[item_id] = 0
            self.original_stock[item_id] = quantity

        self.stock[item_id] += quantity
        self.prices[item_id] = base_price

    def remove_stock(self, item_id: str, quantity: int) -> bool:
        """
        Remove item from stock.

        Args:
            item_id: Item ID
            quantity: Quantity to remove

        Returns:
            True if successful
        """
        if item_id not in self.stock:
            return False

        if self.stock[item_id] < quantity:
            return False

        self.stock[item_id] -= quantity
        return True

    def has_item(self, item_id: str) -> bool:
        """Check if item is in stock."""
        return item_id in self.stock and self.stock[item_id] > 0

    def get_quantity(self, item_id: str) -> int:
        """Get quantity of item in stock."""
        return self.stock.get(item_id, 0)

    def get_base_price(self, item_id: str) -> int:
        """Get base price of item."""
        return self.prices.get(item_id, 0)

    def get_all_items(self) -> List[str]:
        """Get all items in stock."""
        return [item_id for item_id, qty in self.stock.items() if qty > 0]

    def restock(self, item_id: str, quantity: int):
        """
        Restock an item by adding quantity.

        Args:
            item_id: Item to restock
            quantity: Quantity to add
        """
        if item_id in self.stock:
            self.stock[item_id] += quantity

    def restock_all(self):
        """Restock all items to original levels."""
        for item_id, original_qty in self.original_stock.items():
            self.stock[item_id] = original_qty

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "vendor_id": self.vendor_id,
            "stock": self.stock.copy(),
            "prices": self.prices.copy(),
            "original_stock": self.original_stock.copy()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VendorInventory':
        """Load from dictionary."""
        inventory = cls(vendor_id=data["vendor_id"])
        inventory.stock = data.get("stock", {})
        inventory.prices = data.get("prices", {})
        inventory.original_stock = data.get("original_stock", {})
        return inventory


# ============================================================================
# VENDOR CLASS
# ============================================================================

class Vendor:
    """Represents an NPC vendor/merchant."""

    def __init__(
        self,
        vendor_id: str,
        name: str,
        vendor_type: str,
        faction: str,
        buy_modifier: float,  # Percentage vendor pays for items
        sell_modifier: float,  # Percentage markup on items sold
        credits: int = 10000,
        special_services: Optional[List[str]] = None
    ):
        if vendor_type not in VENDOR_TYPES:
            raise ValueError(f"Invalid vendor type: {vendor_type}")

        self.vendor_id = vendor_id
        self.name = name
        self.vendor_type = vendor_type
        self.faction = faction
        self.buy_modifier = buy_modifier
        self.sell_modifier = sell_modifier
        self.credits = credits
        self.special_services = special_services or []

    def calculate_sell_price(
        self,
        item_id: str,
        vendor_inventory: VendorInventory,
        player_faction_rep: int = 0
    ) -> int:
        """
        Calculate price vendor sells item to player.

        Args:
            item_id: Item being sold
            vendor_inventory: Vendor's inventory
            player_faction_rep: Player's reputation with vendor's faction

        Returns:
            Final price
        """
        base_price = vendor_inventory.get_base_price(item_id)

        # Apply sell modifier (faction discount)
        price = base_price * self.sell_modifier

        # Apply reputation discount
        rep_discount = self._get_reputation_discount(player_faction_rep)
        price = price * rep_discount

        return int(price)

    def calculate_buy_price(self, item_value: int) -> int:
        """
        Calculate price vendor pays for item.

        Args:
            item_value: Item's base value

        Returns:
            Price vendor pays
        """
        return int(item_value * self.buy_modifier)

    def _get_reputation_discount(self, reputation: int) -> float:
        """
        Get discount based on reputation.

        Args:
            reputation: Player's faction reputation

        Returns:
            Discount multiplier
        """
        if reputation >= 100:
            return PRICE_MODIFIERS["reputation"][100]
        elif reputation >= 75:
            return PRICE_MODIFIERS["reputation"][75]
        elif reputation >= 50:
            return PRICE_MODIFIERS["reputation"][50]
        elif reputation >= 25:
            return PRICE_MODIFIERS["reputation"][25]
        else:
            return PRICE_MODIFIERS["reputation"][0]

    def sell_to_player(
        self,
        item_id: str,
        quantity: int,
        player_credits: int,
        vendor_inventory: VendorInventory,
        player_faction_rep: int = 0
    ) -> TradeTransaction:
        """
        Sell item to player.

        Args:
            item_id: Item to sell
            quantity: Quantity to sell
            player_credits: Player's available credits
            vendor_inventory: Vendor's inventory
            player_faction_rep: Player's faction reputation

        Returns:
            Trade transaction result
        """
        # Validate quantity
        if quantity <= 0:
            return TradeTransaction(
                transaction_type="buy",
                item_id=item_id,
                quantity=0,
                success=False,
                error="Invalid quantity"
            )

        # Check if item in stock
        if not vendor_inventory.has_item(item_id):
            return TradeTransaction(
                transaction_type="buy",
                item_id=item_id,
                quantity=0,
                success=False,
                error=f"{item_id} not in stock"
            )

        # Check stock quantity
        available = vendor_inventory.get_quantity(item_id)
        if available < quantity:
            return TradeTransaction(
                transaction_type="buy",
                item_id=item_id,
                quantity=0,
                success=False,
                error=f"{item_id} out of stock (only {available} available)"
            )

        # Calculate price
        unit_price = self.calculate_sell_price(item_id, vendor_inventory, player_faction_rep)
        total_price = unit_price * quantity

        # Check player credits
        if player_credits < total_price:
            return TradeTransaction(
                transaction_type="buy",
                item_id=item_id,
                quantity=0,
                success=False,
                error=f"Insufficient credits (need {total_price}, have {player_credits})"
            )

        # Complete transaction
        vendor_inventory.remove_stock(item_id, quantity)
        self.credits += total_price

        return TradeTransaction(
            transaction_type="buy",
            item_id=item_id,
            quantity=quantity,
            success=True,
            credits_spent=total_price
        )

    def buy_from_player(
        self,
        item_value: int,
        quantity: int,
        vendor_credits: int
    ) -> TradeTransaction:
        """
        Buy item from player.

        Args:
            item_value: Item's base value
            quantity: Quantity to buy
            vendor_credits: Vendor's available credits

        Returns:
            Trade transaction result
        """
        # Calculate price
        unit_price = self.calculate_buy_price(item_value)
        total_price = unit_price * quantity

        # Check vendor credits
        if vendor_credits < total_price:
            return TradeTransaction(
                transaction_type="sell",
                item_id="item",
                quantity=0,
                success=False,
                error=f"Vendor not enough credits"
            )

        # Complete transaction
        self.credits -= total_price

        return TradeTransaction(
            transaction_type="sell",
            item_id="item",
            quantity=quantity,
            success=True,
            credits_gained=total_price
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "vendor_id": self.vendor_id,
            "name": self.name,
            "vendor_type": self.vendor_type,
            "faction": self.faction,
            "buy_modifier": self.buy_modifier,
            "sell_modifier": self.sell_modifier,
            "credits": self.credits,
            "special_services": self.special_services
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Vendor':
        """Load from dictionary."""
        return cls(
            vendor_id=data["vendor_id"],
            name=data["name"],
            vendor_type=data["vendor_type"],
            faction=data["faction"],
            buy_modifier=data["buy_modifier"],
            sell_modifier=data["sell_modifier"],
            credits=data.get("credits", 10000),
            special_services=data.get("special_services", [])
        )


# ============================================================================
# VENDOR MANAGER CLASS
# ============================================================================

class VendorManager:
    """Manages all vendors and trading."""

    def __init__(self):
        self.vendors: Dict[str, Vendor] = {}
        self.inventories: Dict[str, VendorInventory] = {}
        self.transaction_history: Dict[str, List[TradeTransaction]] = {}

    def add_vendor(self, vendor: Vendor):
        """Add a vendor."""
        self.vendors[vendor.vendor_id] = vendor
        self.transaction_history[vendor.vendor_id] = []

    def get_vendor(self, vendor_id: str) -> Optional[Vendor]:
        """Get vendor by ID."""
        return self.vendors.get(vendor_id)

    def get_all_vendors(self) -> List[Vendor]:
        """Get all vendors."""
        return list(self.vendors.values())

    def get_vendors_by_type(self, vendor_type: str) -> List[Vendor]:
        """Get vendors filtered by type."""
        return [
            vendor for vendor in self.vendors.values()
            if vendor.vendor_type == vendor_type
        ]

    def get_vendors_by_faction(self, faction: str) -> List[Vendor]:
        """Get vendors filtered by faction."""
        return [
            vendor for vendor in self.vendors.values()
            if vendor.faction == faction
        ]

    def set_inventory(self, vendor_id: str, inventory: VendorInventory):
        """Set inventory for a vendor."""
        self.inventories[vendor_id] = inventory

    def get_inventory(self, vendor_id: str) -> Optional[VendorInventory]:
        """Get inventory for a vendor."""
        return self.inventories.get(vendor_id)

    def restock_vendor(self, vendor_id: str):
        """Restock a vendor to original levels."""
        if vendor_id in self.inventories:
            self.inventories[vendor_id].restock_all()

    def record_transaction(self, vendor_id: str, transaction: TradeTransaction):
        """Record a trade transaction."""
        if vendor_id in self.transaction_history:
            self.transaction_history[vendor_id].append(transaction)

    def get_transaction_history(self, vendor_id: str) -> List[TradeTransaction]:
        """Get transaction history for a vendor."""
        return self.transaction_history.get(vendor_id, [])

    def get_total_spent(self, vendor_id: str) -> int:
        """Get total credits spent at a vendor."""
        history = self.transaction_history.get(vendor_id, [])
        return sum(t.credits_spent for t in history if t.success)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "vendors": {
                vendor_id: vendor.to_dict()
                for vendor_id, vendor in self.vendors.items()
            },
            "inventories": {
                vendor_id: inventory.to_dict()
                for vendor_id, inventory in self.inventories.items()
            },
            "transaction_history": {
                vendor_id: [t.to_dict() for t in transactions]
                for vendor_id, transactions in self.transaction_history.items()
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VendorManager':
        """Load from dictionary."""
        manager = cls()

        # Restore vendors
        for vendor_data in data.get("vendors", {}).values():
            vendor = Vendor.from_dict(vendor_data)
            manager.vendors[vendor.vendor_id] = vendor

        # Restore inventories
        for inventory_data in data.get("inventories", {}).values():
            inventory = VendorInventory.from_dict(inventory_data)
            manager.inventories[inventory.vendor_id] = inventory

        # Restore transaction history
        for vendor_id, transactions_data in data.get("transaction_history", {}).items():
            manager.transaction_history[vendor_id] = [
                TradeTransaction.from_dict(t)
                for t in transactions_data
            ]

        return manager
