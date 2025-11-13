"""
Tests for Crafting & Upgrading System
Tests item crafting, upgrades, materials, recipes, and Tech skill integration
"""

import pytest
from game.crafting import (
    CraftingMaterial,
    CraftingRecipe,
    CraftedItem,
    ItemUpgrade,
    CraftingManager,
    MATERIAL_TYPES,
    RECIPE_DIFFICULTIES,
    UPGRADE_TYPES
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def neon_glass():
    """Create neon glass crafting material."""
    return CraftingMaterial(
        material_id="mat_neon_glass",
        name="Neon Glass Shards",
        description="Sharp fragments from destroyed signs",
        material_type="component",
        value=50
    )


@pytest.fixture
def scrap_metal():
    """Create scrap metal material."""
    return CraftingMaterial(
        material_id="mat_scrap_metal",
        name="Scrap Metal",
        description="Salvaged metal pieces",
        material_type="component",
        value=30
    )


@pytest.fixture
def basic_recipe(neon_glass, scrap_metal):
    """Create a basic crafting recipe."""
    return CraftingRecipe(
        recipe_id="recipe_glass_knife",
        name="Neon Glass Knife",
        description="Improvised blade made from neon glass",
        difficulty=1,
        tech_required=3,
        materials_required={
            "mat_neon_glass": 2,
            "mat_scrap_metal": 1
        },
        result_item_id="weapon_glass_knife",
        result_item_stats={
            "damage": 25,
            "accuracy": 85,
            "range": 1,
            "type": "melee"
        }
    )


@pytest.fixture
def advanced_recipe():
    """Create an advanced crafting recipe."""
    return CraftingRecipe(
        recipe_id="recipe_cyber_arm",
        name="Basic Cyberarm",
        description="Entry-level arm augmentation",
        difficulty=5,
        tech_required=7,
        materials_required={
            "mat_circuitry": 5,
            "mat_titanium": 3,
            "mat_neural_link": 1
        },
        result_item_id="cyber_basic_arm",
        result_item_stats={
            "slot": "arms",
            "melee_damage_bonus": 10
        }
    )


@pytest.fixture
def weapon_upgrade():
    """Create a weapon upgrade."""
    return ItemUpgrade(
        upgrade_id="upgrade_scope",
        name="Targeting Scope",
        description="Improves weapon accuracy",
        upgrade_type="accuracy",
        tech_required=4,
        materials_required={
            "mat_optics": 2,
            "mat_circuitry": 1
        },
        stat_bonuses={"accuracy": 10}
    )


@pytest.fixture
def crafting_manager():
    """Create a crafting manager."""
    return CraftingManager()


# ============================================================================
# TEST CRAFTING MATERIALS
# ============================================================================

class TestCraftingMaterials:
    """Test crafting material creation and properties."""

    def test_material_creation(self, neon_glass):
        """Test creating a crafting material."""
        assert neon_glass.material_id == "mat_neon_glass"
        assert neon_glass.name == "Neon Glass Shards"
        assert neon_glass.material_type == "component"
        assert neon_glass.value == 50

    def test_material_types_valid(self):
        """Test that valid material types are accepted."""
        for mat_type in MATERIAL_TYPES:
            material = CraftingMaterial(
                material_id=f"mat_{mat_type}",
                name=f"Test {mat_type}",
                description="Test",
                material_type=mat_type,
                value=10
            )
            assert material.material_type == mat_type

    def test_invalid_material_type_raises_error(self):
        """Test that invalid material type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid material type"):
            CraftingMaterial(
                material_id="mat_invalid",
                name="Invalid",
                description="Test",
                material_type="invalid_type",
                value=10
            )

    def test_material_serialization(self, neon_glass):
        """Test material to_dict and from_dict."""
        data = neon_glass.to_dict()
        restored = CraftingMaterial.from_dict(data)

        assert restored.material_id == neon_glass.material_id
        assert restored.name == neon_glass.name
        assert restored.material_type == neon_glass.material_type
        assert restored.value == neon_glass.value


# ============================================================================
# TEST CRAFTING RECIPES
# ============================================================================

class TestCraftingRecipes:
    """Test crafting recipe functionality."""

    def test_recipe_creation(self, basic_recipe):
        """Test creating a crafting recipe."""
        assert basic_recipe.recipe_id == "recipe_glass_knife"
        assert basic_recipe.name == "Neon Glass Knife"
        assert basic_recipe.difficulty == 1
        assert basic_recipe.tech_required == 3
        assert len(basic_recipe.materials_required) == 2

    def test_recipe_difficulty_validation(self):
        """Test recipe difficulty must be in valid range."""
        for difficulty in RECIPE_DIFFICULTIES:
            recipe = CraftingRecipe(
                recipe_id="test",
                name="Test",
                description="Test",
                difficulty=difficulty,
                tech_required=3,
                materials_required={},
                result_item_id="test_item",
                result_item_stats={}
            )
            assert recipe.difficulty == difficulty

    def test_invalid_difficulty_raises_error(self):
        """Test that invalid difficulty raises ValueError."""
        with pytest.raises(ValueError, match="Difficulty must be"):
            CraftingRecipe(
                recipe_id="test",
                name="Test",
                description="Test",
                difficulty=11,  # Invalid
                tech_required=3,
                materials_required={},
                result_item_id="test",
                result_item_stats={}
            )

    def test_recipe_materials_required(self, basic_recipe):
        """Test recipe material requirements."""
        assert basic_recipe.materials_required["mat_neon_glass"] == 2
        assert basic_recipe.materials_required["mat_scrap_metal"] == 1

    def test_recipe_serialization(self, basic_recipe):
        """Test recipe to_dict and from_dict."""
        data = basic_recipe.to_dict()
        restored = CraftingRecipe.from_dict(data)

        assert restored.recipe_id == basic_recipe.recipe_id
        assert restored.difficulty == basic_recipe.difficulty
        assert restored.tech_required == basic_recipe.tech_required
        assert restored.materials_required == basic_recipe.materials_required


# ============================================================================
# TEST ITEM CRAFTING
# ============================================================================

class TestItemCrafting:
    """Test actual item crafting mechanics."""

    def test_can_craft_with_sufficient_materials(
        self,
        crafting_manager,
        basic_recipe,
        neon_glass,
        scrap_metal
    ):
        """Test crafting succeeds with enough materials."""
        # Add materials
        crafting_manager.add_material(neon_glass.material_id, 2)
        crafting_manager.add_material(scrap_metal.material_id, 1)

        # Add recipe
        crafting_manager.add_recipe(basic_recipe)

        # Craft with Tech 5 (>= 3 required)
        result = crafting_manager.craft_item("recipe_glass_knife", player_tech=5)

        assert result["success"] is True
        assert "item" in result
        assert result["item"].name == "Neon Glass Knife"

    def test_cannot_craft_insufficient_materials(
        self,
        crafting_manager,
        basic_recipe
    ):
        """Test crafting fails without enough materials."""
        crafting_manager.add_recipe(basic_recipe)

        # Only add 1 neon glass, need 2
        crafting_manager.add_material("mat_neon_glass", 1)

        result = crafting_manager.craft_item("recipe_glass_knife", player_tech=5)

        assert result["success"] is False
        assert "error" in result
        assert "Insufficient materials" in result["error"]

    def test_cannot_craft_low_tech_skill(
        self,
        crafting_manager,
        basic_recipe,
        neon_glass,
        scrap_metal
    ):
        """Test crafting fails with insufficient Tech skill."""
        crafting_manager.add_material(neon_glass.material_id, 2)
        crafting_manager.add_material(scrap_metal.material_id, 1)
        crafting_manager.add_recipe(basic_recipe)

        # Tech 2 < 3 required
        result = crafting_manager.craft_item("recipe_glass_knife", player_tech=2)

        assert result["success"] is False
        assert "Insufficient Tech skill" in result["error"]

    def test_materials_consumed_on_craft(
        self,
        crafting_manager,
        basic_recipe,
        neon_glass,
        scrap_metal
    ):
        """Test materials are consumed when crafting."""
        crafting_manager.add_material(neon_glass.material_id, 3)
        crafting_manager.add_material(scrap_metal.material_id, 2)
        crafting_manager.add_recipe(basic_recipe)

        crafting_manager.craft_item("recipe_glass_knife", player_tech=5)

        # Should have 1 neon glass and 1 scrap metal remaining
        assert crafting_manager.get_material_quantity("mat_neon_glass") == 1
        assert crafting_manager.get_material_quantity("mat_scrap_metal") == 1

    def test_crafting_quality_bonus_high_tech(
        self,
        crafting_manager,
        basic_recipe,
        neon_glass,
        scrap_metal
    ):
        """Test high Tech skill provides quality bonus."""
        crafting_manager.add_material(neon_glass.material_id, 2)
        crafting_manager.add_material(scrap_metal.material_id, 1)
        crafting_manager.add_recipe(basic_recipe)

        # Tech 10 >> 3 required (+7 bonus)
        result = crafting_manager.craft_item("recipe_glass_knife", player_tech=10)

        assert result["success"] is True
        # Quality bonus should improve stats
        assert result["quality_bonus"] > 0


# ============================================================================
# TEST ITEM UPGRADES
# ============================================================================

class TestItemUpgrades:
    """Test item upgrade system."""

    def test_upgrade_creation(self, weapon_upgrade):
        """Test creating an item upgrade."""
        assert weapon_upgrade.upgrade_id == "upgrade_scope"
        assert weapon_upgrade.name == "Targeting Scope"
        assert weapon_upgrade.upgrade_type == "accuracy"
        assert weapon_upgrade.tech_required == 4
        assert weapon_upgrade.stat_bonuses["accuracy"] == 10

    def test_upgrade_types_valid(self):
        """Test valid upgrade types."""
        for upgrade_type in UPGRADE_TYPES:
            upgrade = ItemUpgrade(
                upgrade_id=f"upgrade_{upgrade_type}",
                name=f"Test {upgrade_type}",
                description="Test",
                upgrade_type=upgrade_type,
                tech_required=3,
                materials_required={},
                stat_bonuses={}
            )
            assert upgrade.upgrade_type == upgrade_type

    def test_apply_upgrade_to_weapon(self, crafting_manager, weapon_upgrade):
        """Test applying upgrade to weapon."""
        crafting_manager.add_upgrade(weapon_upgrade)
        crafting_manager.add_material("mat_optics", 2)
        crafting_manager.add_material("mat_circuitry", 1)

        weapon_stats = {"damage": 30, "accuracy": 85, "range": 12}

        result = crafting_manager.apply_upgrade(
            upgrade_id="upgrade_scope",
            item_stats=weapon_stats,
            player_tech=5
        )

        assert result["success"] is True
        assert result["upgraded_stats"]["accuracy"] == 95  # 85 + 10

    def test_cannot_upgrade_low_tech(self, crafting_manager, weapon_upgrade):
        """Test upgrade fails with low Tech skill."""
        crafting_manager.add_upgrade(weapon_upgrade)
        crafting_manager.add_material("mat_optics", 2)
        crafting_manager.add_material("mat_circuitry", 1)

        weapon_stats = {"accuracy": 85}

        result = crafting_manager.apply_upgrade(
            upgrade_id="upgrade_scope",
            item_stats=weapon_stats,
            player_tech=2  # < 4 required
        )

        assert result["success"] is False
        assert "Insufficient Tech skill" in result["error"]

    def test_upgrade_consumes_materials(self, crafting_manager, weapon_upgrade):
        """Test upgrade consumes required materials."""
        crafting_manager.add_upgrade(weapon_upgrade)
        crafting_manager.add_material("mat_optics", 3)
        crafting_manager.add_material("mat_circuitry", 2)

        weapon_stats = {"accuracy": 85}

        crafting_manager.apply_upgrade(
            upgrade_id="upgrade_scope",
            item_stats=weapon_stats,
            player_tech=5
        )

        # Should consume 2 optics, 1 circuitry
        assert crafting_manager.get_material_quantity("mat_optics") == 1
        assert crafting_manager.get_material_quantity("mat_circuitry") == 1


# ============================================================================
# TEST CRAFTING MANAGER
# ============================================================================

class TestCraftingManager:
    """Test crafting manager operations."""

    def test_add_and_get_material(self, crafting_manager, neon_glass):
        """Test adding and retrieving materials."""
        crafting_manager.add_material(neon_glass.material_id, 5)

        assert crafting_manager.get_material_quantity("mat_neon_glass") == 5

    def test_remove_material(self, crafting_manager):
        """Test removing materials."""
        crafting_manager.add_material("mat_test", 10)
        crafting_manager.remove_material("mat_test", 3)

        assert crafting_manager.get_material_quantity("mat_test") == 7

    def test_cannot_remove_more_than_available(self, crafting_manager):
        """Test cannot remove more materials than available."""
        crafting_manager.add_material("mat_test", 5)

        result = crafting_manager.remove_material("mat_test", 10)

        assert result is False
        assert crafting_manager.get_material_quantity("mat_test") == 5

    def test_has_materials_for_recipe(self, crafting_manager, basic_recipe):
        """Test checking if materials are available for recipe."""
        crafting_manager.add_recipe(basic_recipe)
        crafting_manager.add_material("mat_neon_glass", 2)
        crafting_manager.add_material("mat_scrap_metal", 1)

        assert crafting_manager.has_materials_for_recipe("recipe_glass_knife") is True

    def test_get_craftable_recipes(self, crafting_manager, basic_recipe):
        """Test getting list of craftable recipes."""
        crafting_manager.add_recipe(basic_recipe)
        crafting_manager.add_material("mat_neon_glass", 2)
        crafting_manager.add_material("mat_scrap_metal", 1)

        craftable = crafting_manager.get_craftable_recipes(player_tech=5)

        assert len(craftable) == 1
        assert craftable[0].recipe_id == "recipe_glass_knife"

    def test_get_all_recipes(self, crafting_manager, basic_recipe, advanced_recipe):
        """Test getting all known recipes."""
        crafting_manager.add_recipe(basic_recipe)
        crafting_manager.add_recipe(advanced_recipe)

        all_recipes = crafting_manager.get_all_recipes()

        assert len(all_recipes) == 2

    def test_manager_serialization(self, crafting_manager, basic_recipe):
        """Test crafting manager serialization."""
        crafting_manager.add_recipe(basic_recipe)
        crafting_manager.add_material("mat_neon_glass", 5)
        crafting_manager.add_material("mat_scrap_metal", 3)

        data = crafting_manager.to_dict()
        restored = CraftingManager.from_dict(data)

        assert restored.get_material_quantity("mat_neon_glass") == 5
        assert restored.get_material_quantity("mat_scrap_metal") == 3
        assert len(restored.get_all_recipes()) == 1


# ============================================================================
# TEST EDGE CASES
# ============================================================================

class TestCraftingEdgeCases:
    """Test edge cases and error handling."""

    def test_craft_unknown_recipe(self, crafting_manager):
        """Test crafting with unknown recipe ID."""
        result = crafting_manager.craft_item("unknown_recipe", player_tech=5)

        assert result["success"] is False
        assert "Recipe not found" in result["error"]

    def test_add_negative_materials_fails(self, crafting_manager):
        """Test cannot add negative material quantity."""
        result = crafting_manager.add_material("mat_test", -5)

        assert result is False

    def test_recipe_with_no_materials_required(self):
        """Test recipe with no materials (pure Tech check)."""
        recipe = CraftingRecipe(
            recipe_id="recipe_hack",
            name="Digital Hack Tool",
            description="Pure programming, no materials",
            difficulty=3,
            tech_required=8,
            materials_required={},  # No materials
            result_item_id="tool_hack",
            result_item_stats={"hacking_bonus": 20}
        )

        assert len(recipe.materials_required) == 0
        assert recipe.tech_required == 8

    def test_crafting_with_exact_tech_requirement(
        self,
        crafting_manager,
        basic_recipe,
        neon_glass,
        scrap_metal
    ):
        """Test crafting with exact Tech requirement (no bonus)."""
        crafting_manager.add_material(neon_glass.material_id, 2)
        crafting_manager.add_material(scrap_metal.material_id, 1)
        crafting_manager.add_recipe(basic_recipe)

        # Tech 3 = exactly required
        result = crafting_manager.craft_item("recipe_glass_knife", player_tech=3)

        assert result["success"] is True
        assert result["quality_bonus"] == 0  # No bonus at minimum


# ============================================================================
# TEST INTEGRATION
# ============================================================================

class TestCraftingIntegration:
    """Test integration with other game systems."""

    def test_craft_consumable_item(self, crafting_manager):
        """Test crafting a consumable (medkit)."""
        recipe = CraftingRecipe(
            recipe_id="recipe_medkit",
            name="Improvised Medkit",
            description="Basic medical supplies",
            difficulty=2,
            tech_required=4,
            materials_required={
                "mat_medical_supplies": 3,
                "mat_fabric": 1
            },
            result_item_id="consumable_medkit",
            result_item_stats={
                "effect": "heal",
                "amount": 40
            }
        )

        crafting_manager.add_recipe(recipe)
        crafting_manager.add_material("mat_medical_supplies", 3)
        crafting_manager.add_material("mat_fabric", 1)

        result = crafting_manager.craft_item("recipe_medkit", player_tech=5)

        assert result["success"] is True
        assert result["item"].result_item_stats["effect"] == "heal"

    def test_craft_cyberware(self, crafting_manager, advanced_recipe):
        """Test crafting cyberware."""
        crafting_manager.add_recipe(advanced_recipe)
        crafting_manager.add_material("mat_circuitry", 5)
        crafting_manager.add_material("mat_titanium", 3)
        crafting_manager.add_material("mat_neural_link", 1)

        result = crafting_manager.craft_item("recipe_cyber_arm", player_tech=8)

        assert result["success"] is True
        assert result["item"].result_item_stats["slot"] == "arms"

    def test_salvage_item_for_materials(self, crafting_manager):
        """Test breaking down items into materials (salvaging)."""
        # Add salvage functionality
        item_stats = {
            "damage": 30,
            "value": 500,
            "quality": "common"
        }

        materials = crafting_manager.salvage_item(
            item_stats=item_stats,
            player_tech=5
        )

        # Should get some materials back
        assert materials["mat_scrap_metal"] > 0
        # High tech = better salvage rate
        assert materials.get("mat_circuitry", 0) >= 0
