"""
Tests for Companion Management System
Tests NPC recruitment, loyalty, squad management, and companion abilities
"""

import pytest
from game.companions import (
    Companion,
    CompanionManager,
    CompanionPerk,
    COMPANION_CLASSES,
    LOYALTY_LEVELS,
    RELATIONSHIP_THRESHOLDS,
    RELATIONSHIP_LEVELS
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def solo_companion():
    """Create a Solo class companion."""
    return Companion(
        companion_id="comp_jackie",
        name="Jackie Welles",
        companion_class="solo",
        base_stats={
            "body": 7,
            "reflexes": 6,
            "intelligence": 4,
            "tech": 3,
            "cool": 7
        },
        max_hp=120,
        weapon="assault_rifle"
    )


@pytest.fixture
def netrunner_companion():
    """Create a Netrunner class companion."""
    return Companion(
        companion_id="comp_t_bug",
        name="T-Bug",
        companion_class="netrunner",
        base_stats={
            "body": 3,
            "reflexes": 5,
            "intelligence": 9,
            "tech": 8,
            "cool": 6
        },
        max_hp=80,
        weapon="pistol"
    )


@pytest.fixture
def companion_perk():
    """Create a companion perk."""
    return CompanionPerk(
        perk_id="perk_teamwork",
        name="Teamwork",
        description="Increased accuracy when near player",
        loyalty_required=3,
        effect_type="combat_bonus",
        effect_value={"accuracy": 10}
    )


@pytest.fixture
def companion_manager():
    """Create a companion manager."""
    return CompanionManager(max_squad_size=3)


# ============================================================================
# TEST COMPANION CREATION
# ============================================================================

class TestCompanionCreation:
    """Test companion initialization."""

    def test_companion_creation(self, solo_companion):
        """Test creating a companion."""
        assert solo_companion.companion_id == "comp_jackie"
        assert solo_companion.name == "Jackie Welles"
        assert solo_companion.companion_class == "solo"
        assert solo_companion.loyalty == 0
        assert solo_companion.is_recruited is False

    def test_companion_classes_valid(self):
        """Test all companion classes are valid."""
        for companion_class in COMPANION_CLASSES:
            comp = Companion(
                companion_id=f"comp_{companion_class}",
                name=f"Test {companion_class}",
                companion_class=companion_class,
                base_stats={
                    "body": 5, "reflexes": 5, "intelligence": 5,
                    "tech": 5, "cool": 5
                },
                max_hp=100,
                weapon="pistol"
            )
            assert comp.companion_class == companion_class

    def test_invalid_companion_class_raises_error(self):
        """Test invalid companion class raises ValueError."""
        with pytest.raises(ValueError, match="Invalid companion class"):
            Companion(
                companion_id="comp_invalid",
                name="Invalid",
                companion_class="invalid_class",
                base_stats={"body": 5, "reflexes": 5, "intelligence": 5, "tech": 5, "cool": 5},
                max_hp=100,
                weapon="pistol"
            )

    def test_companion_stats_initialization(self, solo_companion):
        """Test companion stats are properly initialized."""
        assert solo_companion.base_stats["body"] == 7
        assert solo_companion.base_stats["cool"] == 7
        assert solo_companion.max_hp == 120


# ============================================================================
# TEST RECRUITMENT
# ============================================================================

class TestRecruitment:
    """Test companion recruitment mechanics."""

    def test_recruit_companion(self, companion_manager, solo_companion):
        """Test recruiting a companion."""
        result = companion_manager.recruit_companion(solo_companion)

        assert result["success"] is True
        assert solo_companion.is_recruited is True
        assert solo_companion in companion_manager.get_all_companions()

    def test_cannot_recruit_same_companion_twice(
        self,
        companion_manager,
        solo_companion
    ):
        """Test cannot recruit same companion twice."""
        companion_manager.recruit_companion(solo_companion)
        result = companion_manager.recruit_companion(solo_companion)

        assert result["success"] is False
        assert "already recruited" in result["error"]

    def test_recruit_multiple_companions(
        self,
        companion_manager,
        solo_companion,
        netrunner_companion
    ):
        """Test recruiting multiple companions."""
        companion_manager.recruit_companion(solo_companion)
        companion_manager.recruit_companion(netrunner_companion)

        assert len(companion_manager.get_all_companions()) == 2

    def test_dismiss_companion(self, companion_manager, solo_companion):
        """Test dismissing a recruited companion."""
        companion_manager.recruit_companion(solo_companion)
        result = companion_manager.dismiss_companion("comp_jackie")

        assert result["success"] is True
        assert solo_companion.is_recruited is False
        assert len(companion_manager.get_all_companions()) == 0


# ============================================================================
# TEST LOYALTY SYSTEM
# ============================================================================

class TestLoyaltySystem:
    """Test companion loyalty mechanics."""

    def test_initial_loyalty_zero(self, solo_companion):
        """Test companions start with zero loyalty."""
        assert solo_companion.loyalty == 0
        assert solo_companion.get_loyalty_level() == "neutral"

    def test_gain_loyalty(self, solo_companion):
        """Test gaining loyalty points."""
        solo_companion.gain_loyalty(25)

        assert solo_companion.loyalty == 25

    def test_lose_loyalty(self, solo_companion):
        """Test losing loyalty points."""
        solo_companion.gain_loyalty(50)
        solo_companion.lose_loyalty(20)

        assert solo_companion.loyalty == 30

    def test_loyalty_levels(self, solo_companion):
        """Test loyalty level thresholds."""
        # Neutral (0-24)
        assert solo_companion.get_loyalty_level() == "neutral"

        # Trusted (25-49)
        solo_companion.gain_loyalty(30)
        assert solo_companion.get_loyalty_level() == "trusted"

        # Loyal (50-74)
        solo_companion.gain_loyalty(25)
        assert solo_companion.get_loyalty_level() == "loyal"

        # Devoted (75-99)
        solo_companion.gain_loyalty(30)
        assert solo_companion.get_loyalty_level() == "devoted"

        # Ride or Die (100)
        solo_companion.gain_loyalty(100)  # Cap at 100
        assert solo_companion.get_loyalty_level() == "ride_or_die"

    def test_loyalty_capped_at_100(self, solo_companion):
        """Test loyalty cannot exceed 100."""
        solo_companion.gain_loyalty(150)

        assert solo_companion.loyalty == 100

    def test_loyalty_cannot_go_negative(self, solo_companion):
        """Test loyalty cannot go below 0."""
        solo_companion.lose_loyalty(50)

        assert solo_companion.loyalty == 0

    def test_loyalty_affects_combat_bonus(self, solo_companion):
        """Test high loyalty provides combat bonuses."""
        solo_companion.gain_loyalty(75)  # Devoted

        bonus = solo_companion.get_combat_bonus()

        assert bonus["damage"] > 0
        assert bonus["accuracy"] > 0


# ============================================================================
# TEST ACTIVE SQUAD
# ============================================================================

class TestActiveSquad:
    """Test active squad management."""

    def test_add_to_active_squad(self, companion_manager, solo_companion):
        """Test adding companion to active squad."""
        companion_manager.recruit_companion(solo_companion)
        result = companion_manager.add_to_squad("comp_jackie")

        assert result["success"] is True
        assert solo_companion in companion_manager.get_active_squad()

    def test_cannot_add_unrecruited_to_squad(
        self,
        companion_manager,
        solo_companion
    ):
        """Test cannot add unrecruited companion to squad."""
        result = companion_manager.add_to_squad("comp_jackie")

        assert result["success"] is False
        assert "not recruited" in result["error"]

    def test_squad_size_limit(
        self,
        companion_manager,
        solo_companion,
        netrunner_companion
    ):
        """Test squad size is limited."""
        # Recruit 2 companions
        companion_manager.recruit_companion(solo_companion)
        companion_manager.recruit_companion(netrunner_companion)

        # Create third companion
        techie = Companion(
            companion_id="comp_techie",
            name="Techie",
            companion_class="techie",
            base_stats={"body": 4, "reflexes": 5, "intelligence": 6, "tech": 9, "cool": 5},
            max_hp=90,
            weapon="pistol"
        )
        companion_manager.recruit_companion(techie)

        # Add all to squad (max 3)
        companion_manager.add_to_squad("comp_jackie")
        companion_manager.add_to_squad("comp_t_bug")
        companion_manager.add_to_squad("comp_techie")

        # Try to add 4th companion
        fixer = Companion(
            companion_id="comp_fixer",
            name="Fixer",
            companion_class="fixer",
            base_stats={"body": 4, "reflexes": 6, "intelligence": 7, "tech": 5, "cool": 8},
            max_hp=100,
            weapon="pistol"
        )
        companion_manager.recruit_companion(fixer)

        result = companion_manager.add_to_squad("comp_fixer")

        assert result["success"] is False
        assert "Squad is full" in result["error"]

    def test_remove_from_squad(self, companion_manager, solo_companion):
        """Test removing companion from active squad."""
        companion_manager.recruit_companion(solo_companion)
        companion_manager.add_to_squad("comp_jackie")

        result = companion_manager.remove_from_squad("comp_jackie")

        assert result["success"] is True
        assert len(companion_manager.get_active_squad()) == 0


# ============================================================================
# TEST COMPANION PERKS
# ============================================================================

class TestCompanionPerks:
    """Test companion perk system."""

    def test_perk_creation(self, companion_perk):
        """Test creating a companion perk."""
        assert companion_perk.perk_id == "perk_teamwork"
        assert companion_perk.name == "Teamwork"
        assert companion_perk.loyalty_required == 3
        assert companion_perk.effect_type == "combat_bonus"

    def test_unlock_perk_sufficient_loyalty(self, solo_companion, companion_perk):
        """Test unlocking perk with sufficient loyalty."""
        solo_companion.gain_loyalty(75)  # Loyal level

        result = solo_companion.unlock_perk(companion_perk)

        assert result["success"] is True
        assert companion_perk in solo_companion.perks

    def test_cannot_unlock_perk_low_loyalty(self, solo_companion, companion_perk):
        """Test cannot unlock perk without sufficient loyalty."""
        solo_companion.gain_loyalty(20)  # Neutral level

        result = solo_companion.unlock_perk(companion_perk)

        assert result["success"] is False
        assert "Insufficient loyalty" in result["error"]

    def test_perk_effects_applied(self, solo_companion, companion_perk):
        """Test perk effects are applied to companion."""
        solo_companion.gain_loyalty(75)
        solo_companion.unlock_perk(companion_perk)

        effects = solo_companion.get_active_perk_effects()

        assert "accuracy" in effects
        assert effects["accuracy"] == 10


# ============================================================================
# TEST COMPANION ABILITIES
# ============================================================================

class TestCompanionAbilities:
    """Test companion class-specific abilities."""

    def test_solo_class_ability(self, solo_companion):
        """Test Solo companions have combat abilities."""
        abilities = solo_companion.get_class_abilities()

        assert "melee_expertise" in abilities or "combat_specialist" in abilities

    def test_netrunner_class_ability(self, netrunner_companion):
        """Test Netrunner companions have hacking abilities."""
        abilities = netrunner_companion.get_class_abilities()

        assert "quickhack" in abilities or "breach_protocol" in abilities

    def test_companion_special_action(self, solo_companion):
        """Test companions can perform special actions."""
        solo_companion.gain_loyalty(50)

        result = solo_companion.use_special_ability("covering_fire")

        assert result is not None
        assert "effect" in result


# ============================================================================
# TEST COMPANION RELATIONSHIPS
# ============================================================================

class TestCompanionRelationships:
    """Test inter-companion relationships."""

    def test_companions_can_like_each_other(
        self,
        companion_manager,
        solo_companion,
        netrunner_companion
    ):
        """Test companions can have positive relationships."""
        companion_manager.recruit_companion(solo_companion)
        companion_manager.recruit_companion(netrunner_companion)

        # Set relationship
        companion_manager.set_relationship(
            "comp_jackie",
            "comp_t_bug",
            relationship_level="friends"
        )

        relationship = companion_manager.get_relationship(
            "comp_jackie",
            "comp_t_bug"
        )

        assert relationship == "friends"

    def test_companions_can_dislike_each_other(
        self,
        companion_manager,
        solo_companion,
        netrunner_companion
    ):
        """Test companions can have negative relationships."""
        companion_manager.recruit_companion(solo_companion)
        companion_manager.recruit_companion(netrunner_companion)

        companion_manager.set_relationship(
            "comp_jackie",
            "comp_t_bug",
            relationship_level="hostile"
        )

        relationship = companion_manager.get_relationship(
            "comp_jackie",
            "comp_t_bug"
        )

        assert relationship == "hostile"

    def test_squad_synergy_bonus(
        self,
        companion_manager,
        solo_companion,
        netrunner_companion
    ):
        """Test friendly companions provide squad synergy bonus."""
        companion_manager.recruit_companion(solo_companion)
        companion_manager.recruit_companion(netrunner_companion)
        companion_manager.add_to_squad("comp_jackie")
        companion_manager.add_to_squad("comp_t_bug")

        # Set as friends
        companion_manager.set_relationship(
            "comp_jackie",
            "comp_t_bug",
            relationship_level="friends"
        )

        synergy = companion_manager.get_squad_synergy_bonus()

        assert synergy > 0


# ============================================================================
# TEST COMPANION MANAGER
# ============================================================================

class TestCompanionManager:
    """Test companion manager operations."""

    def test_get_all_companions(
        self,
        companion_manager,
        solo_companion,
        netrunner_companion
    ):
        """Test getting all recruited companions."""
        companion_manager.recruit_companion(solo_companion)
        companion_manager.recruit_companion(netrunner_companion)

        all_companions = companion_manager.get_all_companions()

        assert len(all_companions) == 2

    def test_get_companion_by_id(self, companion_manager, solo_companion):
        """Test retrieving specific companion by ID."""
        companion_manager.recruit_companion(solo_companion)

        companion = companion_manager.get_companion("comp_jackie")

        assert companion == solo_companion

    def test_get_available_companions(
        self,
        companion_manager,
        solo_companion,
        netrunner_companion
    ):
        """Test getting companions not in active squad."""
        companion_manager.recruit_companion(solo_companion)
        companion_manager.recruit_companion(netrunner_companion)
        companion_manager.add_to_squad("comp_jackie")

        available = companion_manager.get_available_companions()

        assert len(available) == 1
        assert netrunner_companion in available

    def test_manager_serialization(
        self,
        companion_manager,
        solo_companion,
        netrunner_companion
    ):
        """Test companion manager serialization."""
        companion_manager.recruit_companion(solo_companion)
        companion_manager.recruit_companion(netrunner_companion)
        companion_manager.add_to_squad("comp_jackie")
        solo_companion.gain_loyalty(50)

        data = companion_manager.to_dict()
        restored = CompanionManager.from_dict(data)

        assert len(restored.get_all_companions()) == 2
        assert len(restored.get_active_squad()) == 1
        restored_jackie = restored.get_companion("comp_jackie")
        assert restored_jackie.loyalty == 50


# ============================================================================
# TEST EDGE CASES
# ============================================================================

class TestCompanionEdgeCases:
    """Test edge cases and error handling."""

    def test_dismiss_unrecruited_companion(self, companion_manager):
        """Test dismissing companion that was never recruited."""
        result = companion_manager.dismiss_companion("comp_unknown")

        assert result["success"] is False

    def test_add_to_squad_unknown_companion(self, companion_manager):
        """Test adding unknown companion to squad."""
        result = companion_manager.add_to_squad("comp_unknown")

        assert result["success"] is False

    def test_companion_death_removes_from_squad(
        self,
        companion_manager,
        solo_companion
    ):
        """Test companion death removes them from active squad."""
        companion_manager.recruit_companion(solo_companion)
        companion_manager.add_to_squad("comp_jackie")

        # Companion dies
        solo_companion.hp = 0
        solo_companion.is_alive = False

        # Check squad
        active_squad = companion_manager.get_active_squad()

        # Dead companions should be removed or flagged
        assert all(comp.is_alive for comp in active_squad)

    def test_loyalty_gain_on_quest_completion(self, solo_companion):
        """Test companions gain loyalty from quest completion."""
        initial_loyalty = solo_companion.loyalty

        solo_companion.on_quest_complete(quest_type="main")

        assert solo_companion.loyalty > initial_loyalty


# ============================================================================
# TEST INTEGRATION
# ============================================================================

class TestCompanionIntegration:
    """Test integration with other game systems."""

    def test_companion_uses_inventory_system(self, solo_companion):
        """Test companions can be equipped with items."""
        from game.inventory import Weapon

        better_weapon = Weapon(
            item_id="weapon_smart_rifle",
            name="Smart Rifle",
            description="High-tech rifle",
            value=2000,
            damage=40,
            accuracy=95,
            range=15,
            armor_pen=0.25,
            crit_multiplier=2.5,
            weapon_type="ranged"
        )

        solo_companion.equip_weapon(better_weapon)

        assert solo_companion.weapon == better_weapon.item_id

    def test_companion_combat_stats(self, solo_companion):
        """Test companions provide combat stats."""
        stats = solo_companion.get_combat_stats()

        assert "max_hp" in stats
        assert "damage_bonus" in stats
        assert "accuracy" in stats
