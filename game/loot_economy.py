"""
Neon Collapse - Loot & Economy System
Manages item generation, quality tiers, vendor trading, and currency
"""

from typing import Dict, List, Any, Optional
import random


# Constants
VALID_QUALITIES = ["common", "uncommon", "rare", "epic", "legendary"]
QUALITY_MULTIPLIERS = {
    "common": 1.0,
    "uncommon": 2.5,
    "rare": 5.0,
    "epic": 10.0,
    "legendary": 20.0
}

# Drop rates by enemy tier (% chance to drop item)
DROP_RATES = {
    "basic": 0.3,      # 30% chance
    "veteran": 0.5,    # 50% chance
    "elite": 0.7,      # 70% chance
    "boss": 1.0        # 100% chance (guaranteed)
}

# Quality distribution by enemy tier
QUALITY_WEIGHTS = {
    "basic": {"common": 70, "uncommon": 25, "rare": 4, "epic": 1, "legendary": 0},
    "veteran": {"common": 50, "uncommon": 35, "rare": 12, "epic": 3, "legendary": 0},
    "elite": {"common": 30, "uncommon": 40, "rare": 20, "epic": 8, "legendary": 2},
    "boss": {"common": 0, "uncommon": 20, "rare": 40, "epic": 30, "legendary": 10}
}

# Credit drops by tier
CREDIT_DROPS = {
    "basic": (50, 150),
    "veteran": (150, 400),
    "elite": (400, 1000),
    "boss": (1500, 5000)
}

# Vendor pricing
VENDOR_BUY_MARKUP = 2.0   # Players pay 2x base value
VENDOR_SELL_RATE = 0.5    # Players receive 50% of base value


# ============================================================================
# LOOT ITEM CLASS
# ============================================================================

class LootItem:
    """Represents a loot item."""

    def __init__(
        self,
        item_id: str,
        name: str,
        quality: str,
        value: int,
        is_unique: bool = False
    ):
        if quality not in VALID_QUALITIES:
            raise ValueError(f"Invalid quality: {quality}. Must be one of {VALID_QUALITIES}")

        if value < 0:
            raise ValueError(f"Value cannot be negative: {value}")

        self.item_id = item_id
        self.name = name
        self.quality = quality
        self.value = value
        self.is_unique = is_unique

    def get_sell_value(self) -> int:
        """Get value when selling to vendor (50% of base)."""
        return int(self.value * VENDOR_SELL_RATE)

    def get_buy_value(self) -> int:
        """Get cost when buying from vendor (200% of base)."""
        return int(self.value * VENDOR_BUY_MARKUP)

    def can_sell(self) -> bool:
        """Check if item can be sold to vendors."""
        # Unique items cannot be sold
        return not self.is_unique

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "item_id": self.item_id,
            "name": self.name,
            "quality": self.quality,
            "value": self.value,
            "is_unique": self.is_unique
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LootItem':
        """Load from dictionary."""
        return cls(
            item_id=data["item_id"],
            name=data["name"],
            quality=data["quality"],
            value=data["value"],
            is_unique=data.get("is_unique", False)
        )


# ============================================================================
# LOOT TABLE CLASS
# ============================================================================

class LootTable:
    """Weighted loot table for random item generation."""

    def __init__(self, table_id: str):
        self.table_id = table_id
        self.entries: List[Dict[str, Any]] = []

    def add_entry(self, item: LootItem, weight: int):
        """Add item to loot table with weight."""
        self.entries.append({
            "item": item,
            "weight": weight
        })

    def roll(self) -> Optional[LootItem]:
        """Roll for random item from table."""
        if not self.entries:
            return None

        # Calculate total weight
        total_weight = sum(entry["weight"] for entry in self.entries)

        # Roll random number
        roll = random.randint(1, total_weight)

        # Find matching entry
        current_weight = 0
        for entry in self.entries:
            current_weight += entry["weight"]
            if roll <= current_weight:
                return entry["item"]

        return None


# ============================================================================
# LOOT GENERATOR CLASS
# ============================================================================

class LootGenerator:
    """Generates random loot from enemies."""

    def __init__(self):
        pass

    def generate_loot(
        self,
        enemy_tier: str,
        player_phase: int
    ) -> Dict[str, Any]:
        """
        Generate loot from defeated enemy.

        Args:
            enemy_tier: Enemy tier (basic, veteran, elite, boss)
            player_phase: Current player phase (affects loot quality)

        Returns:
            Dictionary with "items" list and "credits" amount
        """
        loot = {
            "items": [],
            "credits": 0
        }

        # Check if loot drops
        drop_rate = DROP_RATES.get(enemy_tier, 0.3)
        if random.random() > drop_rate:
            # No item drop, but might still get credits
            if random.random() < 0.5:
                loot["credits"] = self._generate_credits(enemy_tier, player_phase)
            return loot

        # Generate item(s)
        num_items = 1
        if enemy_tier == "boss":
            num_items = random.randint(2, 4)  # Bosses drop multiple items
        elif enemy_tier == "elite":
            num_items = random.randint(1, 2)

        for _ in range(num_items):
            item = self._generate_item(enemy_tier, player_phase)
            if item:
                loot["items"].append(item)

        # Generate credits
        if random.random() < 0.7:  # 70% chance for credits
            loot["credits"] = self._generate_credits(enemy_tier, player_phase)

        return loot

    def _generate_item(self, enemy_tier: str, player_phase: int) -> Optional[LootItem]:
        """Generate a single random item."""
        # Determine quality based on tier
        quality = self._roll_quality(enemy_tier, player_phase)

        # Generate item based on quality
        item_id = f"item_{random.randint(1000, 9999)}"
        name = f"{quality.title()} Item"

        # Base value increases with quality
        base_value = {
            "common": 100,
            "uncommon": 500,
            "rare": 2000,
            "epic": 8000,
            "legendary": 25000
        }[quality]

        # Scale value with player phase
        phase_multiplier = 1.0 + (player_phase * 0.2)
        value = int(base_value * phase_multiplier)

        return LootItem(
            item_id=item_id,
            name=name,
            quality=quality,
            value=value
        )

    def _roll_quality(self, enemy_tier: str, player_phase: int) -> str:
        """Roll for item quality based on enemy tier."""
        weights = QUALITY_WEIGHTS.get(enemy_tier, QUALITY_WEIGHTS["basic"]).copy()

        # Improve quality chances with higher phase
        if player_phase >= 3:
            # Shift weights toward higher quality
            weights["rare"] += 5
            weights["epic"] += 3
            weights["common"] = max(0, weights["common"] - 8)

        if player_phase >= 5:
            weights["legendary"] += 5
            weights["epic"] += 5
            weights["uncommon"] = max(0, weights["uncommon"] - 10)

        # Roll quality
        total_weight = sum(weights.values())
        roll = random.randint(1, total_weight)

        current_weight = 0
        for quality, weight in weights.items():
            current_weight += weight
            if roll <= current_weight:
                return quality

        return "common"

    def _generate_credits(self, enemy_tier: str, player_phase: int) -> int:
        """Generate credit drop amount."""
        credit_range = CREDIT_DROPS.get(enemy_tier, (50, 150))
        base_credits = random.randint(credit_range[0], credit_range[1])

        # Scale with player phase
        phase_multiplier = 1.0 + (player_phase * 0.15)
        return int(base_credits * phase_multiplier)

    def generate_quest_loot(self, item_id: str, item_name: str) -> Dict[str, Any]:
        """
        Generate specific quest loot.

        Args:
            item_id: Specific item ID for quest
            item_name: Name of quest item

        Returns:
            Loot dict with quest item
        """
        quest_item = LootItem(
            item_id=item_id,
            name=item_name,
            quality="rare",
            value=0,  # Quest items have no monetary value
            is_unique=True
        )

        return {
            "items": [quest_item],
            "credits": 0
        }


# ============================================================================
# VENDOR CLASS
# ============================================================================

class Vendor:
    """Represents a shop/vendor NPC."""

    def __init__(
        self,
        vendor_id: str,
        name: str,
        vendor_type: str
    ):
        self.vendor_id = vendor_id
        self.name = name
        self.vendor_type = vendor_type  # weapons, armor, cyberware, general
        self.inventory: List[LootItem] = []

    def add_item(self, item: LootItem):
        """Add item to vendor inventory."""
        self.inventory.append(item)

    def get_inventory(self) -> List[LootItem]:
        """Get vendor's current inventory."""
        return self.inventory

    def generate_stock(self, player_phase: int):
        """Generate vendor stock based on vendor type and player phase."""
        self.inventory.clear()

        # Generate 5-10 items
        num_items = random.randint(5, 10)

        for _ in range(num_items):
            # Quality distribution for vendors
            quality_weights = {
                "common": 40,
                "uncommon": 35,
                "rare": 18,
                "epic": 5,
                "legendary": 2
            }

            # Improve with player phase
            if player_phase >= 3:
                quality_weights["rare"] += 10
                quality_weights["common"] -= 10

            # Roll quality
            total_weight = sum(quality_weights.values())
            roll = random.randint(1, total_weight)

            current_weight = 0
            quality = "common"
            for q, weight in quality_weights.items():
                current_weight += weight
                if roll <= current_weight:
                    quality = q
                    break

            # Create item
            item_id = f"{self.vendor_type}_{random.randint(1000, 9999)}"
            name = f"{quality.title()} {self.vendor_type.title()}"

            base_value = {
                "common": 200,
                "uncommon": 800,
                "rare": 3000,
                "epic": 10000,
                "legendary": 30000
            }[quality]

            value = int(base_value * (1.0 + player_phase * 0.1))

            item = LootItem(item_id, name, quality, value)
            self.inventory.append(item)

    def refresh_stock(self, player_phase: int):
        """Refresh vendor stock (same as generate)."""
        self.generate_stock(player_phase)

    def buy_item(self, item_id: str, buyer_credits: int) -> Dict[str, Any]:
        """
        Player buys item from vendor.

        Args:
            item_id: ID of item to buy
            buyer_credits: Credits player has

        Returns:
            Dict with success, item, cost, remaining_credits
        """
        # Find item
        item = None
        for i, inv_item in enumerate(self.inventory):
            if inv_item.item_id == item_id:
                item = inv_item
                item_index = i
                break

        if not item:
            return {
                "success": False,
                "error": "Item not found"
            }

        # Check if player can afford
        cost = item.get_buy_value()
        if buyer_credits < cost:
            return {
                "success": False,
                "error": "Insufficient credits"
            }

        # Remove from inventory
        self.inventory.pop(item_index)

        return {
            "success": True,
            "item": item,
            "cost": cost,
            "remaining_credits": buyer_credits - cost
        }

    def sell_item(self, item: LootItem) -> Dict[str, Any]:
        """
        Player sells item to vendor.

        Args:
            item: Item to sell

        Returns:
            Dict with success and credits_earned
        """
        if not item.can_sell():
            return {
                "success": False,
                "error": "Item cannot be sold"
            }

        credits_earned = item.get_sell_value()

        # Add item to vendor inventory
        self.inventory.append(item)

        return {
            "success": True,
            "credits_earned": credits_earned
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "vendor_id": self.vendor_id,
            "name": self.name,
            "vendor_type": self.vendor_type,
            "inventory": [item.to_dict() for item in self.inventory]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Vendor':
        """Load from dictionary."""
        vendor = cls(
            vendor_id=data["vendor_id"],
            name=data["name"],
            vendor_type=data["vendor_type"]
        )

        # Restore inventory
        for item_data in data.get("inventory", []):
            item = LootItem.from_dict(item_data)
            vendor.inventory.append(item)

        return vendor
