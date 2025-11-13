"""
Neon Collapse - Skill XP System
Five independent attribute tracks that level via "learn by doing"
"""

from typing import Dict, Any, Optional
import math

# Constants
MAX_ATTRIBUTE_LEVEL = 10
BASE_ATTRIBUTE_LEVEL = 3


# ============================================================================
# XP CALCULATION
# ============================================================================

def calculate_xp_required(current_level: int) -> int:
    """
    Calculate XP required to reach next level.
    Formula: 100 * 1.5^(level - 3)

    Level 3→4: 100 XP
    Level 4→5: 150 XP
    Level 5→6: 225 XP
    Level 6→7: 337 XP
    Level 7→8: 506 XP
    Level 8→9: 759 XP
    Level 9→10: 1139 XP
    """
    return math.floor(100 * math.pow(1.5, current_level - 3))


# ============================================================================
# STAT BONUSES
# ============================================================================

def get_hp_bonus_for_body_level(level: int) -> int:
    """Calculate HP bonus from Body level. +15 HP per level above 3."""
    return max(0, (level - 3) * 15)


def get_dodge_bonus_for_reflexes_level(level: int) -> int:
    """Calculate dodge bonus from Reflexes level. +2% per level above 3."""
    return max(0, (level - 3) * 2)


def get_initiative_bonus_for_reflexes_level(level: int) -> int:
    """Calculate initiative bonus from Reflexes level. +2 per level above 3."""
    return max(0, (level - 3) * 2)


def get_crit_bonus_for_cool_level(level: int) -> int:
    """Calculate crit bonus from Cool level. +2% per level above 3."""
    return max(0, (level - 3) * 2)


def get_ram_bonus_for_intelligence_level(level: int) -> int:
    """Calculate RAM bonus from Intelligence level. +2 per level above 3."""
    return max(0, (level - 3) * 2)


# ============================================================================
# SKILL XP MANAGER
# ============================================================================

class SkillXPManager:
    """Manages skill XP for five independent attributes."""

    ATTRIBUTES = ["body", "reflexes", "intelligence", "tech", "cool"]

    def __init__(self):
        # Initialize all attributes at level 3 with 0 XP
        self.attributes = {}
        for attr in self.ATTRIBUTES:
            self.attributes[attr] = {
                "level": BASE_ATTRIBUTE_LEVEL,
                "current_xp": 0
            }

        self.skill_points = 0
        self.on_level_up = None  # Optional callback

    # ========================================================================
    # QUERIES
    # ========================================================================

    def get_attribute_level(self, attribute: str) -> int:
        """Get current level of an attribute."""
        if attribute not in self.ATTRIBUTES:
            raise ValueError(f"Invalid attribute: {attribute}")
        return self.attributes[attribute]["level"]

    def get_attribute_xp(self, attribute: str) -> int:
        """Get current XP of an attribute."""
        if attribute not in self.ATTRIBUTES:
            raise ValueError(f"Invalid attribute: {attribute}")
        return self.attributes[attribute]["current_xp"]

    def get_unlocked_tier(self, attribute: str) -> int:
        """
        Get unlocked skill tier for attribute.
        Tier 1: Always unlocked (level 3+)
        Tier 2: Level 5+
        Tier 3: Level 7+
        Tier 4: Level 9+
        """
        level = self.get_attribute_level(attribute)

        if level >= 9:
            return 4
        elif level >= 7:
            return 3
        elif level >= 5:
            return 2
        else:
            return 1

    # ========================================================================
    # XP GAIN (GENERIC)
    # ========================================================================

    def gain_body_xp(self, amount: int):
        """Gain Body XP (generic method)."""
        if amount < 0:
            raise ValueError("XP amount cannot be negative")
        self._add_xp("body", amount)

    def gain_reflexes_xp(self, amount: int):
        """Gain Reflexes XP (generic method)."""
        if amount < 0:
            raise ValueError("XP amount cannot be negative")
        self._add_xp("reflexes", amount)

    def gain_intelligence_xp(self, amount: int):
        """Gain Intelligence XP (generic method)."""
        if amount < 0:
            raise ValueError("XP amount cannot be negative")
        self._add_xp("intelligence", amount)

    def gain_tech_xp(self, amount: int):
        """Gain Tech XP (generic method)."""
        if amount < 0:
            raise ValueError("XP amount cannot be negative")
        self._add_xp("tech", amount)

    def gain_cool_xp(self, amount: int):
        """Gain Cool XP (generic method)."""
        if amount < 0:
            raise ValueError("XP amount cannot be negative")
        self._add_xp("cool", amount)

    # ========================================================================
    # XP GAIN (LEARN BY DOING)
    # ========================================================================

    def gain_body_xp_from_melee(self, damage: int):
        """Gain Body XP from dealing melee damage. 1 XP per 10 damage."""
        xp = damage // 10
        self._add_xp("body", xp)

    def gain_reflexes_xp_from_ranged(self, damage: int):
        """Gain Reflexes XP from dealing ranged damage. 1 XP per 10 damage."""
        xp = damage // 10
        self._add_xp("reflexes", xp)

    def gain_reflexes_xp_from_dodge(self):
        """Gain Reflexes XP from successful dodge. Fixed 5 XP."""
        self._add_xp("reflexes", 5)

    def gain_reflexes_xp_from_crit(self):
        """Gain Reflexes XP from critical hit. Fixed 8 XP."""
        self._add_xp("reflexes", 8)

    def gain_cool_xp_from_crit_kill(self):
        """Gain Cool XP from critical kill. Fixed 10 XP."""
        self._add_xp("cool", 10)

    def gain_intelligence_xp_from_hack(self):
        """Gain Intelligence XP from successful hack. Fixed 10 XP."""
        self._add_xp("intelligence", 10)

    def gain_tech_xp_from_craft(self):
        """Gain Tech XP from crafting. Fixed 5 XP."""
        self._add_xp("tech", 5)

    # ========================================================================
    # INTERNAL METHODS
    # ========================================================================

    def _add_xp(self, attribute: str, amount: int):
        """Add XP to an attribute and handle leveling."""
        attr = self.attributes[attribute]
        attr["current_xp"] += amount

        # Check for level ups
        while attr["level"] < MAX_ATTRIBUTE_LEVEL:
            xp_needed = calculate_xp_required(attr["level"])

            if attr["current_xp"] >= xp_needed:
                # Level up!
                old_level = attr["level"]
                attr["level"] += 1
                attr["current_xp"] -= xp_needed

                # Award skill point every 2 levels from base (at levels 5, 7, 9)
                levels_gained = attr["level"] - BASE_ATTRIBUTE_LEVEL
                if levels_gained % 2 == 0 and levels_gained > 0:
                    self.skill_points += 1

                # Trigger callback if set
                if self.on_level_up:
                    self.on_level_up(attribute, old_level, attr["level"])
            else:
                break

    # ========================================================================
    # SERIALIZATION
    # ========================================================================

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for saving."""
        return {
            "attributes": {
                attr: {
                    "level": self.attributes[attr]["level"],
                    "current_xp": self.attributes[attr]["current_xp"]
                }
                for attr in self.ATTRIBUTES
            },
            "skill_points": self.skill_points
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SkillXPManager':
        """Load from dictionary."""
        manager = cls()

        for attr in cls.ATTRIBUTES:
            if attr in data["attributes"]:
                manager.attributes[attr]["level"] = data["attributes"][attr]["level"]
                manager.attributes[attr]["current_xp"] = data["attributes"][attr]["current_xp"]

        manager.skill_points = data.get("skill_points", 0)

        return manager
