"""
Comprehensive test suite for skill_xp.py (Skill XP System)

Tests cover:
- Independent attribute leveling (Body, Reflexes, Intelligence, Tech, Cool)
- XP gain from actions ("learn by doing")
- Level thresholds (exponential scaling)
- Stat bonuses per level
- Skill point awards (every 2 levels)
- Skill tree tier unlocks (levels 5, 7, 9)
- Integration with combat actions
"""

import pytest
from unittest.mock import Mock
import sys
from pathlib import Path

# Add game directory to path
game_dir = Path(__file__).parent.parent / "game"
sys.path.insert(0, str(game_dir))


class TestAttributeInitialization:
    """Test attribute starting values."""

    def test_attributes_start_at_level_3(self):
        """Test all attributes start at level 3."""
        from skill_xp import SkillXPManager

        manager = SkillXPManager()

        assert manager.get_attribute_level("body") == 3
        assert manager.get_attribute_level("reflexes") == 3
        assert manager.get_attribute_level("intelligence") == 3
        assert manager.get_attribute_level("tech") == 3
        assert manager.get_attribute_level("cool") == 3

    def test_attributes_start_with_zero_xp(self):
        """Test attributes start with 0 current XP."""
        from skill_xp import SkillXPManager

        manager = SkillXPManager()

        for attr in ["body", "reflexes", "intelligence", "tech", "cool"]:
            assert manager.get_attribute_xp(attr) == 0


class TestXPThresholds:
    """Test XP threshold calculation (exponential scaling)."""

    def test_xp_formula_level_3_to_4(self):
        """Test XP required from level 3 to 4."""
        from skill_xp import calculate_xp_required

        # 100 * 1.5^(3-3) = 100 * 1 = 100
        assert calculate_xp_required(3) == 100

    def test_xp_formula_level_4_to_5(self):
        """Test XP required from level 4 to 5."""
        from skill_xp import calculate_xp_required

        # 100 * 1.5^(4-3) = 100 * 1.5 = 150
        assert calculate_xp_required(4) == 150

    def test_xp_formula_exponential_scaling(self):
        """Test exponential XP scaling matches design."""
        from skill_xp import calculate_xp_required

        assert calculate_xp_required(5) == 225   # 100 * 1.5^2
        assert calculate_xp_required(6) == 337   # 100 * 1.5^3 (rounded)
        assert calculate_xp_required(7) == 506   # 100 * 1.5^4
        assert calculate_xp_required(8) == 759   # 100 * 1.5^5

    def test_xp_cap_at_level_10(self):
        """Test level 10 is maximum."""
        from skill_xp import MAX_ATTRIBUTE_LEVEL

        assert MAX_ATTRIBUTE_LEVEL == 10


class TestLearnByDoing:
    """Test earning XP from actions."""

    def test_body_xp_from_melee_damage(self):
        """Test Body XP from dealing melee damage."""
        from skill_xp import SkillXPManager

        manager = SkillXPManager()

        # 1 XP per 10 melee damage
        manager.gain_body_xp_from_melee(35)

        assert manager.get_attribute_xp("body") == 3  # 35 / 10 = 3

    def test_reflexes_xp_from_ranged_damage(self):
        """Test Reflexes XP from dealing ranged damage."""
        from skill_xp import SkillXPManager

        manager = SkillXPManager()

        # 1 XP per 10 ranged damage
        manager.gain_reflexes_xp_from_ranged(50)

        assert manager.get_attribute_xp("reflexes") == 5

    def test_reflexes_xp_from_dodge(self):
        """Test Reflexes XP from successful dodge."""
        from skill_xp import SkillXPManager

        manager = SkillXPManager()

        manager.gain_reflexes_xp_from_dodge()

        assert manager.get_attribute_xp("reflexes") == 5  # Fixed 5 XP per dodge

    def test_reflexes_xp_from_crit(self):
        """Test Reflexes XP from critical hit."""
        from skill_xp import SkillXPManager

        manager = SkillXPManager()

        manager.gain_reflexes_xp_from_crit()

        assert manager.get_attribute_xp("reflexes") == 8  # Fixed 8 XP per crit

    def test_cool_xp_from_crit_kill(self):
        """Test Cool XP from critical kill."""
        from skill_xp import SkillXPManager

        manager = SkillXPManager()

        manager.gain_cool_xp_from_crit_kill()

        assert manager.get_attribute_xp("cool") == 10

    def test_intelligence_xp_from_hack(self):
        """Test Intelligence XP from successful hack."""
        from skill_xp import SkillXPManager

        manager = SkillXPManager()

        manager.gain_intelligence_xp_from_hack()

        assert manager.get_attribute_xp("intelligence") == 10

    def test_tech_xp_from_craft(self):
        """Test Tech XP from crafting."""
        from skill_xp import SkillXPManager

        manager = SkillXPManager()

        manager.gain_tech_xp_from_craft()

        assert manager.get_attribute_xp("tech") == 5


class TestAttributeLeveling:
    """Test leveling up individual attributes."""

    def test_level_up_single_attribute(self):
        """Test leveling up one attribute."""
        from skill_xp import SkillXPManager

        manager = SkillXPManager()

        # Gain 100 XP for Body (enough for level 4)
        manager.gain_body_xp_from_melee(1000)  # 100 XP

        assert manager.get_attribute_level("body") == 4
        assert manager.get_attribute_xp("body") == 0  # XP reset

    def test_level_up_with_overflow_xp(self):
        """Test leveling up with XP overflow."""
        from skill_xp import SkillXPManager

        manager = SkillXPManager()

        # Gain 120 XP for Reflexes (100 needed, 20 overflow)
        manager.gain_reflexes_xp_from_ranged(1200)

        assert manager.get_attribute_level("reflexes") == 4
        assert manager.get_attribute_xp("reflexes") == 20

    def test_multiple_levels_in_one_gain(self):
        """Test jumping multiple levels at once."""
        from skill_xp import SkillXPManager

        manager = SkillXPManager()

        # Gain enough for levels 4 and 5 (100 + 150 = 250)
        manager.gain_cool_xp(300)

        assert manager.get_attribute_level("cool") == 5
        assert manager.get_attribute_xp("cool") == 50  # Overflow

    def test_level_cap_at_10(self):
        """Test cannot exceed level 10."""
        from skill_xp import SkillXPManager

        manager = SkillXPManager()

        # Try to gain massive XP
        manager.gain_body_xp(100000)

        assert manager.get_attribute_level("body") == 10


class TestStatBonuses:
    """Test stat bonuses from leveling."""

    def test_body_level_grants_hp_bonus(self):
        """Test Body leveling increases max HP."""
        from skill_xp import get_hp_bonus_for_body_level

        # +15 HP per level above 3
        assert get_hp_bonus_for_body_level(3) == 0
        assert get_hp_bonus_for_body_level(4) == 15
        assert get_hp_bonus_for_body_level(5) == 30
        assert get_hp_bonus_for_body_level(10) == 105  # (10-3) * 15

    def test_reflexes_level_grants_dodge_bonus(self):
        """Test Reflexes leveling increases dodge."""
        from skill_xp import get_dodge_bonus_for_reflexes_level

        # +2% dodge per level above 3
        assert get_dodge_bonus_for_reflexes_level(3) == 0
        assert get_dodge_bonus_for_reflexes_level(5) == 4  # 2 levels * 2

    def test_cool_level_grants_crit_bonus(self):
        """Test Cool leveling increases crit chance."""
        from skill_xp import get_crit_bonus_for_cool_level

        # +2% crit per level above 3
        assert get_crit_bonus_for_cool_level(3) == 0
        assert get_crit_bonus_for_cool_level(7) == 8  # 4 levels * 2


class TestSkillPoints:
    """Test skill point awards."""

    def test_skill_point_every_2_levels(self):
        """Test gaining skill points every 2 attribute levels."""
        from skill_xp import SkillXPManager

        manager = SkillXPManager()

        # Level 3 → 4: No point
        manager.gain_body_xp(100)
        assert manager.skill_points == 0

        # Level 4 → 5: +1 point (even level reached)
        manager.gain_body_xp(150)
        assert manager.skill_points == 1

        # Level 5 → 6: No point
        manager.gain_body_xp(225)
        assert manager.skill_points == 1

        # Level 6 → 7: +1 point
        manager.gain_body_xp(337)
        assert manager.skill_points == 2

    def test_skill_points_accumulate_across_attributes(self):
        """Test skill points from different attributes stack."""
        from skill_xp import SkillXPManager

        manager = SkillXPManager()

        # Body 3 → 4 → 5 (1 point at level 4)
        manager.gain_body_xp(250)

        # Reflexes 3 → 4 → 5 (1 point at level 4)
        manager.gain_reflexes_xp(250)

        assert manager.skill_points == 2


class TestSkillTreeUnlocks:
    """Test skill tree tier unlocks."""

    def test_tier_2_unlocks_at_level_5(self):
        """Test Tier 2 skills unlock at level 5."""
        from skill_xp import SkillXPManager

        manager = SkillXPManager()

        # Reach level 5
        manager.gain_body_xp(250)  # 100 + 150

        assert manager.get_unlocked_tier("body") == 2

    def test_tier_3_unlocks_at_level_7(self):
        """Test Tier 3 skills unlock at level 7."""
        from skill_xp import SkillXPManager

        manager = SkillXPManager()

        # Reach level 7
        manager.gain_reflexes_xp(1268)  # Sum to level 7

        assert manager.get_unlocked_tier("reflexes") == 3

    def test_tier_4_unlocks_at_level_9(self):
        """Test Tier 4 skills unlock at level 9."""
        from skill_xp import SkillXPManager

        manager = SkillXPManager()

        # Reach level 9
        manager.gain_cool_xp(4537)  # Sum to level 9

        assert manager.get_unlocked_tier("cool") == 4

    def test_tier_1_always_available(self):
        """Test Tier 1 skills always available."""
        from skill_xp import SkillXPManager

        manager = SkillXPManager()

        assert manager.get_unlocked_tier("body") == 1


class TestSerialization:
    """Test skill XP system serialization."""

    def test_skill_xp_to_dict(self):
        """Test converting skill XP to dictionary."""
        from skill_xp import SkillXPManager

        manager = SkillXPManager()
        manager.gain_body_xp(50)
        manager.gain_reflexes_xp(30)

        data = manager.to_dict()

        assert data["attributes"]["body"]["level"] == 3
        assert data["attributes"]["body"]["current_xp"] == 50
        assert data["attributes"]["reflexes"]["current_xp"] == 30
        assert data["skill_points"] >= 0

    def test_skill_xp_from_dict(self):
        """Test loading skill XP from dictionary."""
        from skill_xp import SkillXPManager

        data = {
            "attributes": {
                "body": {"level": 5, "current_xp": 100},
                "reflexes": {"level": 6, "current_xp": 50},
                "intelligence": {"level": 3, "current_xp": 0},
                "tech": {"level": 4, "current_xp": 25},
                "cool": {"level": 7, "current_xp": 200}
            },
            "skill_points": 5
        }

        manager = SkillXPManager.from_dict(data)

        assert manager.get_attribute_level("body") == 5
        assert manager.get_attribute_xp("body") == 100
        assert manager.skill_points == 5


@pytest.mark.integration
class TestCombatIntegration:
    """Test skill XP integration with combat."""

    def test_full_combat_xp_breakdown(self):
        """Test XP gain from complete combat sequence."""
        from skill_xp import SkillXPManager

        manager = SkillXPManager()

        # TURN 1: Shoot with AR (35 damage)
        manager.gain_reflexes_xp_from_ranged(35)  # +3 XP

        # TURN 2: Dodge, then crit (50 damage)
        manager.gain_reflexes_xp_from_dodge()     # +5 XP
        manager.gain_reflexes_xp_from_ranged(50)  # +5 XP
        manager.gain_reflexes_xp_from_crit()      # +8 XP
        manager.gain_cool_xp_from_crit_kill()     # +10 XP

        # TURN 3: Hack enemy
        manager.gain_intelligence_xp_from_hack()  # +10 XP

        # Verify XP earned
        assert manager.get_attribute_xp("reflexes") == 21  # 3+5+5+8
        assert manager.get_attribute_xp("cool") == 10
        assert manager.get_attribute_xp("intelligence") == 10


class TestEdgeCases:
    """Test edge cases."""

    def test_negative_xp_rejected(self):
        """Test negative XP is rejected."""
        from skill_xp import SkillXPManager

        manager = SkillXPManager()

        with pytest.raises(ValueError):
            manager.gain_body_xp(-50)

    def test_invalid_attribute_name(self):
        """Test invalid attribute name raises error."""
        from skill_xp import SkillXPManager

        manager = SkillXPManager()

        with pytest.raises(ValueError):
            manager.get_attribute_level("invalid_stat")

    def test_zero_xp_gain(self):
        """Test gaining 0 XP is allowed."""
        from skill_xp import SkillXPManager

        manager = SkillXPManager()

        initial_xp = manager.get_attribute_xp("body")
        manager.gain_body_xp(0)

        assert manager.get_attribute_xp("body") == initial_xp
