"""
Neon Collapse - Crafting & Upgrading System
Manages item crafting, upgrades, materials, recipes, and Tech skill integration
"""

from typing import Dict, List, Any, Optional


# Constants
MATERIAL_TYPES = ["component", "rare", "quest", "salvage"]
RECIPE_DIFFICULTIES = list(range(1, 11))  # 1-10
UPGRADE_TYPES = ["damage", "accuracy", "armor", "utility", "cyberware"]


# ============================================================================
# CRAFTING MATERIAL CLASS
# ============================================================================

class CraftingMaterial:
    """Represents a crafting material/component."""

    def __init__(
        self,
        material_id: str,
        name: str,
        description: str,
        material_type: str,
        value: int
    ):
        if material_type not in MATERIAL_TYPES:
            raise ValueError(f"Invalid material type: {material_type}")

        self.material_id = material_id
        self.name = name
        self.description = description
        self.material_type = material_type
        self.value = value

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "material_id": self.material_id,
            "name": self.name,
            "description": self.description,
            "material_type": self.material_type,
            "value": self.value
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CraftingMaterial':
        """Load from dictionary."""
        return cls(
            material_id=data["material_id"],
            name=data["name"],
            description=data["description"],
            material_type=data["material_type"],
            value=data["value"]
        )


# ============================================================================
# CRAFTING RECIPE CLASS
# ============================================================================

class CraftingRecipe:
    """Represents a crafting recipe."""

    def __init__(
        self,
        recipe_id: str,
        name: str,
        description: str,
        difficulty: int,
        tech_required: int,
        materials_required: Dict[str, int],
        result_item_id: str,
        result_item_stats: Dict[str, Any]
    ):
        if difficulty not in RECIPE_DIFFICULTIES:
            raise ValueError(f"Difficulty must be 1-10, got {difficulty}")

        self.recipe_id = recipe_id
        self.name = name
        self.description = description
        self.difficulty = difficulty
        self.tech_required = tech_required
        self.materials_required = materials_required
        self.result_item_id = result_item_id
        self.result_item_stats = result_item_stats

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "recipe_id": self.recipe_id,
            "name": self.name,
            "description": self.description,
            "difficulty": self.difficulty,
            "tech_required": self.tech_required,
            "materials_required": self.materials_required,
            "result_item_id": self.result_item_id,
            "result_item_stats": self.result_item_stats
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CraftingRecipe':
        """Load from dictionary."""
        return cls(
            recipe_id=data["recipe_id"],
            name=data["name"],
            description=data["description"],
            difficulty=data["difficulty"],
            tech_required=data["tech_required"],
            materials_required=data["materials_required"],
            result_item_id=data["result_item_id"],
            result_item_stats=data["result_item_stats"]
        )


# ============================================================================
# CRAFTED ITEM CLASS
# ============================================================================

class CraftedItem:
    """Represents a crafted item."""

    def __init__(
        self,
        item_id: str,
        name: str,
        description: str,
        result_item_stats: Dict[str, Any],
        quality_bonus: int = 0
    ):
        self.item_id = item_id
        self.name = name
        self.description = description
        self.result_item_stats = result_item_stats
        self.quality_bonus = quality_bonus

    def get_final_stats(self) -> Dict[str, Any]:
        """Get final stats with quality bonus applied."""
        stats = self.result_item_stats.copy()

        # Apply quality bonus to numeric stats
        if self.quality_bonus > 0:
            for key, value in stats.items():
                if isinstance(value, (int, float)) and key != "range":
                    # Increase by quality bonus percentage
                    bonus_multiplier = 1.0 + (self.quality_bonus / 100.0)
                    stats[key] = int(value * bonus_multiplier)

        return stats


# ============================================================================
# ITEM UPGRADE CLASS
# ============================================================================

class ItemUpgrade:
    """Represents an item upgrade/modification."""

    def __init__(
        self,
        upgrade_id: str,
        name: str,
        description: str,
        upgrade_type: str,
        tech_required: int,
        materials_required: Dict[str, int],
        stat_bonuses: Dict[str, int]
    ):
        if upgrade_type not in UPGRADE_TYPES:
            raise ValueError(f"Invalid upgrade type: {upgrade_type}")

        self.upgrade_id = upgrade_id
        self.name = name
        self.description = description
        self.upgrade_type = upgrade_type
        self.tech_required = tech_required
        self.materials_required = materials_required
        self.stat_bonuses = stat_bonuses

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "upgrade_id": self.upgrade_id,
            "name": self.name,
            "description": self.description,
            "upgrade_type": self.upgrade_type,
            "tech_required": self.tech_required,
            "materials_required": self.materials_required,
            "stat_bonuses": self.stat_bonuses
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ItemUpgrade':
        """Load from dictionary."""
        return cls(
            upgrade_id=data["upgrade_id"],
            name=data["name"],
            description=data["description"],
            upgrade_type=data["upgrade_type"],
            tech_required=data["tech_required"],
            materials_required=data["materials_required"],
            stat_bonuses=data["stat_bonuses"]
        )


# ============================================================================
# CRAFTING MANAGER CLASS
# ============================================================================

class CraftingManager:
    """Manages crafting operations and state."""

    def __init__(self):
        self.materials: Dict[str, int] = {}  # material_id -> quantity
        self.recipes: Dict[str, CraftingRecipe] = {}  # recipe_id -> recipe
        self.upgrades: Dict[str, ItemUpgrade] = {}  # upgrade_id -> upgrade

    def add_material(self, material_id: str, quantity: int) -> bool:
        """
        Add materials to inventory.

        Args:
            material_id: Material ID
            quantity: Amount to add

        Returns:
            True if successful
        """
        if quantity < 0:
            return False

        if material_id not in self.materials:
            self.materials[material_id] = 0

        self.materials[material_id] += quantity
        return True

    def remove_material(self, material_id: str, quantity: int) -> bool:
        """
        Remove materials from inventory.

        Args:
            material_id: Material ID
            quantity: Amount to remove

        Returns:
            True if successful, False if insufficient
        """
        if material_id not in self.materials:
            return False

        if self.materials[material_id] < quantity:
            return False

        self.materials[material_id] -= quantity
        return True

    def get_material_quantity(self, material_id: str) -> int:
        """Get quantity of a material."""
        return self.materials.get(material_id, 0)

    def add_recipe(self, recipe: CraftingRecipe):
        """Add a recipe to known recipes."""
        self.recipes[recipe.recipe_id] = recipe

    def add_upgrade(self, upgrade: ItemUpgrade):
        """Add an upgrade to known upgrades."""
        self.upgrades[upgrade.upgrade_id] = upgrade

    def has_materials_for_recipe(self, recipe_id: str) -> bool:
        """
        Check if player has materials for recipe.

        Args:
            recipe_id: Recipe to check

        Returns:
            True if all materials available
        """
        if recipe_id not in self.recipes:
            return False

        recipe = self.recipes[recipe_id]

        for material_id, quantity in recipe.materials_required.items():
            if self.get_material_quantity(material_id) < quantity:
                return False

        return True

    def craft_item(
        self,
        recipe_id: str,
        player_tech: int
    ) -> Dict[str, Any]:
        """
        Craft an item using a recipe.

        Args:
            recipe_id: Recipe to use
            player_tech: Player's Tech attribute

        Returns:
            Dictionary with success status and item/error
        """
        # Check if recipe exists
        if recipe_id not in self.recipes:
            return {
                "success": False,
                "error": "Recipe not found"
            }

        recipe = self.recipes[recipe_id]

        # Check Tech requirement
        if player_tech < recipe.tech_required:
            return {
                "success": False,
                "error": f"Insufficient Tech skill (need {recipe.tech_required}, have {player_tech})"
            }

        # Check materials
        if not self.has_materials_for_recipe(recipe_id):
            return {
                "success": False,
                "error": "Insufficient materials"
            }

        # Consume materials
        for material_id, quantity in recipe.materials_required.items():
            self.remove_material(material_id, quantity)

        # Calculate quality bonus (Tech over requirement)
        tech_bonus = player_tech - recipe.tech_required
        quality_bonus = tech_bonus * 2  # 2% per Tech point over requirement

        # Create crafted item
        item = CraftedItem(
            item_id=recipe.result_item_id,
            name=recipe.name,
            description=recipe.description,
            result_item_stats=recipe.result_item_stats,
            quality_bonus=quality_bonus
        )

        return {
            "success": True,
            "item": item,
            "quality_bonus": quality_bonus
        }

    def apply_upgrade(
        self,
        upgrade_id: str,
        item_stats: Dict[str, Any],
        player_tech: int
    ) -> Dict[str, Any]:
        """
        Apply an upgrade to an item.

        Args:
            upgrade_id: Upgrade to apply
            item_stats: Current item stats
            player_tech: Player's Tech attribute

        Returns:
            Dictionary with success and upgraded stats
        """
        # Check if upgrade exists
        if upgrade_id not in self.upgrades:
            return {
                "success": False,
                "error": "Upgrade not found"
            }

        upgrade = self.upgrades[upgrade_id]

        # Check Tech requirement
        if player_tech < upgrade.tech_required:
            return {
                "success": False,
                "error": f"Insufficient Tech skill (need {upgrade.tech_required}, have {player_tech})"
            }

        # Check materials
        for material_id, quantity in upgrade.materials_required.items():
            if self.get_material_quantity(material_id) < quantity:
                return {
                    "success": False,
                    "error": "Insufficient materials for upgrade"
                }

        # Consume materials
        for material_id, quantity in upgrade.materials_required.items():
            self.remove_material(material_id, quantity)

        # Apply stat bonuses
        upgraded_stats = item_stats.copy()
        for stat, bonus in upgrade.stat_bonuses.items():
            if stat in upgraded_stats:
                upgraded_stats[stat] += bonus
            else:
                upgraded_stats[stat] = bonus

        return {
            "success": True,
            "upgraded_stats": upgraded_stats,
            "upgrade_applied": upgrade.name
        }

    def get_craftable_recipes(self, player_tech: int) -> List[CraftingRecipe]:
        """
        Get list of recipes player can currently craft.

        Args:
            player_tech: Player's Tech attribute

        Returns:
            List of craftable recipes
        """
        craftable = []

        for recipe in self.recipes.values():
            # Check Tech requirement
            if player_tech < recipe.tech_required:
                continue

            # Check materials
            if not self.has_materials_for_recipe(recipe.recipe_id):
                continue

            craftable.append(recipe)

        return craftable

    def get_all_recipes(self) -> List[CraftingRecipe]:
        """Get all known recipes."""
        return list(self.recipes.values())

    def salvage_item(
        self,
        item_stats: Dict[str, Any],
        player_tech: int
    ) -> Dict[str, int]:
        """
        Salvage an item for materials.

        Args:
            item_stats: Item to salvage
            player_tech: Player's Tech attribute

        Returns:
            Dictionary of materials recovered
        """
        materials = {}

        # Base salvage: always get some scrap metal
        base_scrap = 1
        materials["mat_scrap_metal"] = base_scrap

        # Tech skill determines salvage efficiency
        # Tech 5+ gets circuitry
        if player_tech >= 5:
            materials["mat_circuitry"] = 1

        # Tech 8+ gets rare components
        if player_tech >= 8:
            materials["mat_rare_components"] = 1

        # Quality affects salvage yield
        quality = item_stats.get("quality", "common")
        if quality in ["rare", "epic", "legendary"]:
            materials["mat_scrap_metal"] += 1

        # Add materials to inventory
        for material_id, quantity in materials.items():
            self.add_material(material_id, quantity)

        return materials

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "materials": self.materials.copy(),
            "recipes": {
                recipe_id: recipe.to_dict()
                for recipe_id, recipe in self.recipes.items()
            },
            "upgrades": {
                upgrade_id: upgrade.to_dict()
                for upgrade_id, upgrade in self.upgrades.items()
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CraftingManager':
        """Load from dictionary."""
        manager = cls()

        # Restore materials
        manager.materials = data.get("materials", {})

        # Restore recipes
        for recipe_data in data.get("recipes", {}).values():
            recipe = CraftingRecipe.from_dict(recipe_data)
            manager.recipes[recipe.recipe_id] = recipe

        # Restore upgrades
        for upgrade_data in data.get("upgrades", {}).values():
            upgrade = ItemUpgrade.from_dict(upgrade_data)
            manager.upgrades[upgrade.upgrade_id] = upgrade

        return manager
