"""
Neon Collapse - Inventory System
Manages items, equipment, and consumables
"""

from typing import Dict, List, Optional, Any


# ============================================================================
# ITEM CLASSES
# ============================================================================

class Item:
    """Base item class."""

    def __init__(
        self,
        item_id: str,
        name: str,
        description: str,
        item_type: str,
        value: int,
        stackable: bool = False,
        max_stack: int = 99
    ):
        self.item_id = item_id
        self.name = name
        self.description = description
        self.item_type = item_type
        self.value = value
        self.stackable = stackable
        self.max_stack = max_stack

    def to_dict(self) -> Dict[str, Any]:
        """Convert item to dictionary."""
        return {
            "item_id": self.item_id,
            "name": self.name,
            "description": self.description,
            "item_type": self.item_type,
            "value": self.value,
            "stackable": self.stackable,
            "max_stack": self.max_stack
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Item':
        """Create item from dictionary."""
        # Check for specialized item types
        item_type = data.get("item_type")

        if item_type == "weapon":
            return Weapon.from_dict(data)
        elif item_type == "armor":
            return Armor.from_dict(data)
        elif item_type == "consumable":
            return Consumable.from_dict(data)
        elif item_type == "cyberware":
            return Cyberware.from_dict(data)
        else:
            return cls(
                item_id=data["item_id"],
                name=data["name"],
                description=data["description"],
                item_type=data["item_type"],
                value=data["value"],
                stackable=data.get("stackable", False),
                max_stack=data.get("max_stack", 1)
            )


class Weapon(Item):
    """Weapon item with combat stats."""

    def __init__(
        self,
        item_id: str,
        name: str,
        description: str,
        value: int,
        damage: int,
        accuracy: int,
        range: int,
        armor_pen: float,
        crit_multiplier: float,
        weapon_type: str
    ):
        super().__init__(
            item_id=item_id,
            name=name,
            description=description,
            item_type="weapon",
            value=value,
            stackable=False,
            max_stack=1
        )
        self.damage = damage
        self.accuracy = accuracy
        self.range = range
        self.armor_pen = armor_pen
        self.crit_multiplier = crit_multiplier
        self.weapon_type = weapon_type

    def to_dict(self) -> Dict[str, Any]:
        """Convert weapon to dictionary."""
        data = super().to_dict()
        data.update({
            "damage": self.damage,
            "accuracy": self.accuracy,
            "range": self.range,
            "armor_pen": self.armor_pen,
            "crit_multiplier": self.crit_multiplier,
            "weapon_type": self.weapon_type
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Weapon':
        """Create weapon from dictionary."""
        return cls(
            item_id=data["item_id"],
            name=data["name"],
            description=data["description"],
            value=data["value"],
            damage=data["damage"],
            accuracy=data["accuracy"],
            range=data["range"],
            armor_pen=data["armor_pen"],
            crit_multiplier=data["crit_multiplier"],
            weapon_type=data["weapon_type"]
        )


class Armor(Item):
    """Armor item with defense stats."""

    def __init__(
        self,
        item_id: str,
        name: str,
        description: str,
        value: int,
        armor_value: int,
        mobility_penalty: int
    ):
        super().__init__(
            item_id=item_id,
            name=name,
            description=description,
            item_type="armor",
            value=value,
            stackable=False,
            max_stack=1
        )
        self.armor_value = armor_value
        self.mobility_penalty = mobility_penalty

    def to_dict(self) -> Dict[str, Any]:
        """Convert armor to dictionary."""
        data = super().to_dict()
        data.update({
            "armor_value": self.armor_value,
            "mobility_penalty": self.mobility_penalty
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Armor':
        """Create armor from dictionary."""
        return cls(
            item_id=data["item_id"],
            name=data["name"],
            description=data["description"],
            value=data["value"],
            armor_value=data["armor_value"],
            mobility_penalty=data["mobility_penalty"]
        )


class Consumable(Item):
    """Consumable item with effects."""

    def __init__(
        self,
        item_id: str,
        name: str,
        description: str,
        value: int,
        effect: str,
        amount: int,
        duration: int = 0,
        stackable: bool = True,
        max_stack: int = 1
    ):
        super().__init__(
            item_id=item_id,
            name=name,
            description=description,
            item_type="consumable",
            value=value,
            stackable=stackable,
            max_stack=max_stack
        )
        self.effect = effect
        self.amount = amount
        self.duration = duration

    def get_effect_data(self) -> Dict[str, Any]:
        """Get effect data for applying to character."""
        return {
            "effect": self.effect,
            "amount": self.amount,
            "duration": self.duration
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert consumable to dictionary."""
        data = super().to_dict()
        data.update({
            "effect": self.effect,
            "amount": self.amount,
            "duration": self.duration
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Consumable':
        """Create consumable from dictionary."""
        return cls(
            item_id=data["item_id"],
            name=data["name"],
            description=data["description"],
            value=data["value"],
            effect=data["effect"],
            amount=data["amount"],
            duration=data.get("duration", 0),
            stackable=data.get("stackable", True),
            max_stack=data.get("max_stack", 1)
        )


class Cyberware(Item):
    """Cyberware item with slot and abilities."""

    # 8 Body Systems
    VALID_SLOTS = [
        "arms",
        "legs",
        "nervous_system",
        "frontal_cortex",
        "ocular_system",
        "circulatory_system",
        "skeletal_system",
        "integumentary_system"
    ]

    def __init__(
        self,
        item_id: str,
        name: str,
        description: str,
        value: int,
        slot: str,
        abilities: List[Dict[str, Any]] = None,
        passive_effect: str = ""
    ):
        super().__init__(
            item_id=item_id,
            name=name,
            description=description,
            item_type="cyberware",
            value=value,
            stackable=False,
            max_stack=1
        )
        if slot not in self.VALID_SLOTS:
            raise ValueError(f"Invalid cyberware slot: {slot}")

        self.slot = slot
        self.abilities = abilities or []
        self.passive_effect = passive_effect

    def to_dict(self) -> Dict[str, Any]:
        """Convert cyberware to dictionary."""
        data = super().to_dict()
        data.update({
            "slot": self.slot,
            "abilities": self.abilities,
            "passive_effect": self.passive_effect
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Cyberware':
        """Create cyberware from dictionary."""
        return cls(
            item_id=data["item_id"],
            name=data["name"],
            description=data["description"],
            value=data["value"],
            slot=data["slot"],
            abilities=data.get("abilities", []),
            passive_effect=data.get("passive_effect", "")
        )


# ============================================================================
# INVENTORY
# ============================================================================

class Inventory:
    """Inventory management system."""

    def __init__(self, max_capacity: int = 50):
        self.max_capacity = max_capacity
        self.items: Dict[str, Dict[str, Any]] = {}
        self.equipped_weapon: Optional[Weapon] = None
        self.equipped_armor: Optional[Armor] = None
        # Cyberware slots (8 body systems, 1 cyberware per slot)
        self.cyberware_slots: Dict[str, Optional[Cyberware]] = {
            "arms": None,
            "legs": None,
            "nervous_system": None,
            "frontal_cortex": None,
            "ocular_system": None,
            "circulatory_system": None,
            "skeletal_system": None,
            "integumentary_system": None
        }

    def add_item(self, item: Item, quantity: int = 1) -> bool:
        """
        Add item to inventory.

        Returns:
            True if all items added successfully, False if capacity reached or stack limit exceeded

        Note:
            When adding stackable items that exceed max_stack, items are added up to the limit
            and excess items are discarded. The function returns False to indicate not all items
            were added. Callers should check the return value to detect item loss.
        """
        if item.item_id in self.items:
            # Item already exists
            current_quantity = self.items[item.item_id]["quantity"]

            if item.stackable:
                # Check stack limit
                new_quantity = current_quantity + quantity
                if new_quantity > item.max_stack:
                    # Add up to max_stack only (excess items are discarded)
                    items_that_can_be_added = item.max_stack - current_quantity
                    self.items[item.item_id]["quantity"] = item.max_stack
                    # Note: (quantity - items_that_can_be_added) items are lost
                    return False  # Couldn't add all items
                else:
                    self.items[item.item_id]["quantity"] = new_quantity
                    return True
            else:
                # Non-stackable items just increment quantity
                self.items[item.item_id]["quantity"] = current_quantity + quantity
                return True
        else:
            # New item
            # Check capacity
            if self.get_item_count() >= self.max_capacity:
                return False

            # Check if stackable and quantity exceeds max_stack
            if item.stackable and quantity > item.max_stack:
                quantity = item.max_stack
                self.items[item.item_id] = {
                    "item": item,
                    "quantity": quantity
                }
                return False  # Couldn't add all items
            else:
                self.items[item.item_id] = {
                    "item": item,
                    "quantity": quantity
                }
                return True

    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """
        Remove item from inventory.

        Returns:
            True if exactly the requested quantity was removed
            False if item doesn't exist or not enough quantity

        Note:
            If quantity exceeds current_quantity, all items are still removed.
            Returns False to indicate not all requested items were available.
            Callers should check return value to detect partial removal.
        """
        if item_id not in self.items:
            return False

        current_quantity = self.items[item_id]["quantity"]

        if quantity >= current_quantity:
            # Remove entire entry (even if quantity > current_quantity)
            del self.items[item_id]
            # Return True only if we had exactly the amount requested
            return quantity == current_quantity
        else:
            # Reduce quantity
            self.items[item_id]["quantity"] -= quantity
            return True

    def get_item_quantity(self, item_id: str) -> int:
        """Get quantity of an item."""
        if item_id not in self.items:
            return 0
        return self.items[item_id]["quantity"]

    def get_item_count(self) -> int:
        """Get number of unique items/stacks in inventory."""
        return len(self.items)

    def get_remaining_capacity(self) -> int:
        """Get remaining inventory capacity."""
        return self.max_capacity - self.get_item_count()

    def equip_weapon(self, item_id: str) -> bool:
        """
        Equip a weapon from inventory.

        Returns:
            True if equipped successfully, False if item not found or not a weapon
        """
        if item_id not in self.items:
            return False

        item = self.items[item_id]["item"]

        if not isinstance(item, Weapon):
            return False

        # Unequip old weapon (automatically handled by assignment)
        self.equipped_weapon = item
        return True

    def equip_armor(self, item_id: str) -> bool:
        """
        Equip armor from inventory.

        Returns:
            True if equipped successfully, False if item not found or not armor
        """
        if item_id not in self.items:
            return False

        item = self.items[item_id]["item"]

        if not isinstance(item, Armor):
            return False

        # Unequip old armor (automatically handled by assignment)
        self.equipped_armor = item
        return True

    def unequip_weapon(self):
        """Unequip current weapon."""
        self.equipped_weapon = None

    def unequip_armor(self):
        """Unequip current armor."""
        self.equipped_armor = None

    def install_cyberware(self, item_id: str) -> bool:
        """
        Install cyberware in appropriate body slot.

        Returns:
            True if installed successfully, False if item not found, not cyberware, or slot occupied
        """
        if item_id not in self.items:
            return False

        item = self.items[item_id]["item"]

        if not isinstance(item, Cyberware):
            return False

        # Check if slot is already occupied
        if self.cyberware_slots[item.slot] is not None:
            return False  # Slot occupied

        # Install cyberware
        self.cyberware_slots[item.slot] = item
        return True

    def uninstall_cyberware(self, slot: str) -> bool:
        """
        Uninstall cyberware from body slot.

        Returns:
            True if uninstalled, False if slot empty or invalid
        """
        if slot not in self.cyberware_slots:
            return False

        if self.cyberware_slots[slot] is None:
            return False

        self.cyberware_slots[slot] = None
        return True

    def get_installed_cyberware(self) -> List[Cyberware]:
        """Get all installed cyberware."""
        return [cyber for cyber in self.cyberware_slots.values() if cyber is not None]

    def get_cyberware_in_slot(self, slot: str) -> Optional[Cyberware]:
        """Get cyberware installed in specific slot."""
        return self.cyberware_slots.get(slot)

    def use_consumable(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Use a consumable item.

        Returns:
            Effect data dict if successful, None if item not found or not consumable
        """
        if item_id not in self.items:
            return None

        item = self.items[item_id]["item"]

        if not isinstance(item, Consumable):
            return None

        # Get effect data before removing
        effect_data = item.get_effect_data()

        # Remove one from inventory
        self.remove_item(item_id, quantity=1)

        return effect_data

    def get_all_items(self) -> List[Dict[str, Any]]:
        """Get all items in inventory."""
        return [
            {"item": entry["item"], "quantity": entry["quantity"]}
            for entry in self.items.values()
        ]

    def get_items_by_type(self, item_type: str) -> List[Dict[str, Any]]:
        """Get all items of a specific type."""
        return [
            {"item": entry["item"], "quantity": entry["quantity"]}
            for entry in self.items.values()
            if entry["item"].item_type == item_type
        ]

    def has_item(self, item_id: str) -> bool:
        """Check if inventory has an item."""
        return item_id in self.items

    def get_total_value(self) -> int:
        """Calculate total value of all items in inventory."""
        total = 0
        for entry in self.items.values():
            item = entry["item"]
            quantity = entry["quantity"]
            total += item.value * quantity
        return total

    def to_dict(self) -> Dict[str, Any]:
        """Convert inventory to dictionary for saving."""
        return {
            "max_capacity": self.max_capacity,
            "items": {
                item_id: {
                    "item": entry["item"].to_dict(),
                    "quantity": entry["quantity"]
                }
                for item_id, entry in self.items.items()
            },
            "equipped_weapon": self.equipped_weapon.to_dict() if self.equipped_weapon else None,
            "equipped_armor": self.equipped_armor.to_dict() if self.equipped_armor else None,
            "cyberware_slots": {
                slot: cyber.to_dict() if cyber else None
                for slot, cyber in self.cyberware_slots.items()
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Inventory':
        """Create inventory from dictionary."""
        inventory = cls(max_capacity=data["max_capacity"])

        # Restore items
        for item_id, entry in data["items"].items():
            item = Item.from_dict(entry["item"])
            inventory.items[item_id] = {
                "item": item,
                "quantity": entry["quantity"]
            }

        # Restore equipped items
        if data.get("equipped_weapon"):
            weapon_data = data["equipped_weapon"]
            inventory.equipped_weapon = Weapon.from_dict(weapon_data)

        if data.get("equipped_armor"):
            armor_data = data["equipped_armor"]
            inventory.equipped_armor = Armor.from_dict(armor_data)

        # Restore cyberware slots
        if data.get("cyberware_slots"):
            for slot, cyber_data in data["cyberware_slots"].items():
                if cyber_data:
                    inventory.cyberware_slots[slot] = Cyberware.from_dict(cyber_data)

        return inventory
