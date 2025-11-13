"""
Neon Collapse - Companion Management System
Manages NPC recruitment, loyalty, squad composition, and companion abilities
"""

from typing import Dict, List, Any, Optional


# Constants
COMPANION_CLASSES = ["solo", "netrunner", "techie", "fixer", "medic"]
LOYALTY_LEVELS = ["neutral", "trusted", "loyal", "devoted", "ride_or_die"]
RELATIONSHIP_THRESHOLDS = {
    "neutral": 0,
    "trusted": 25,
    "loyal": 50,
    "devoted": 75,
    "ride_or_die": 100
}
RELATIONSHIP_LEVELS = ["hostile", "unfriendly", "neutral", "friendly", "friends", "best_friends"]


# ============================================================================
# COMPANION PERK CLASS
# ============================================================================

class CompanionPerk:
    """Represents a companion perk/ability."""

    def __init__(
        self,
        perk_id: str,
        name: str,
        description: str,
        loyalty_required: int,
        effect_type: str,
        effect_value: Dict[str, Any]
    ):
        self.perk_id = perk_id
        self.name = name
        self.description = description
        self.loyalty_required = loyalty_required
        self.effect_type = effect_type
        self.effect_value = effect_value

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "perk_id": self.perk_id,
            "name": self.name,
            "description": self.description,
            "loyalty_required": self.loyalty_required,
            "effect_type": self.effect_type,
            "effect_value": self.effect_value
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CompanionPerk':
        """Load from dictionary."""
        return cls(
            perk_id=data["perk_id"],
            name=data["name"],
            description=data["description"],
            loyalty_required=data["loyalty_required"],
            effect_type=data["effect_type"],
            effect_value=data["effect_value"]
        )


# ============================================================================
# COMPANION CLASS
# ============================================================================

class Companion:
    """Represents a recruitable companion NPC."""

    def __init__(
        self,
        companion_id: str,
        name: str,
        companion_class: str,
        base_stats: Dict[str, int],
        max_hp: int,
        weapon: str
    ):
        if companion_class not in COMPANION_CLASSES:
            raise ValueError(f"Invalid companion class: {companion_class}")

        self.companion_id = companion_id
        self.name = name
        self.companion_class = companion_class
        self.base_stats = base_stats
        self.max_hp = max_hp
        self.hp = max_hp
        self.weapon = weapon

        # Recruitment and loyalty
        self.is_recruited = False
        self.loyalty = 0

        # Perks and abilities
        self.perks: List[CompanionPerk] = []

        # Combat state
        self.is_alive = True

    def gain_loyalty(self, amount: int):
        """
        Gain loyalty points.

        Args:
            amount: Loyalty points to gain
        """
        self.loyalty += amount
        self.loyalty = min(100, self.loyalty)  # Cap at 100

    def lose_loyalty(self, amount: int):
        """
        Lose loyalty points.

        Args:
            amount: Loyalty points to lose
        """
        self.loyalty -= amount
        self.loyalty = max(0, self.loyalty)  # Floor at 0

    def get_loyalty_level(self) -> str:
        """
        Get current loyalty level.

        Returns:
            Loyalty level string
        """
        if self.loyalty >= 100:
            return "ride_or_die"
        elif self.loyalty >= 75:
            return "devoted"
        elif self.loyalty >= 50:
            return "loyal"
        elif self.loyalty >= 25:
            return "trusted"
        else:
            return "neutral"

    def get_combat_bonus(self) -> Dict[str, int]:
        """
        Get combat bonuses based on loyalty.

        Returns:
            Dictionary of stat bonuses
        """
        loyalty_level = self.get_loyalty_level()

        bonuses = {
            "damage": 0,
            "accuracy": 0
        }

        if loyalty_level == "trusted":
            bonuses["accuracy"] = 5
        elif loyalty_level == "loyal":
            bonuses["damage"] = 5
            bonuses["accuracy"] = 5
        elif loyalty_level == "devoted":
            bonuses["damage"] = 10
            bonuses["accuracy"] = 10
        elif loyalty_level == "ride_or_die":
            bonuses["damage"] = 15
            bonuses["accuracy"] = 15

        return bonuses

    def unlock_perk(self, perk: CompanionPerk) -> Dict[str, Any]:
        """
        Unlock a companion perk.

        Args:
            perk: Perk to unlock

        Returns:
            Result dictionary
        """
        # Check loyalty requirement
        loyalty_level_map = {
            "trusted": 25,
            "loyal": 50,
            "devoted": 75,
            "ride_or_die": 100
        }

        required_loyalty = loyalty_level_map.get(
            list(loyalty_level_map.keys())[perk.loyalty_required - 1],
            25
        )

        if self.loyalty < required_loyalty:
            return {
                "success": False,
                "error": f"Insufficient loyalty (need {required_loyalty}, have {self.loyalty})"
            }

        # Add perk
        self.perks.append(perk)

        return {
            "success": True,
            "perk": perk
        }

    def get_active_perk_effects(self) -> Dict[str, Any]:
        """
        Get all active perk effects.

        Returns:
            Combined perk effects
        """
        effects = {}

        for perk in self.perks:
            if perk.effect_type == "combat_bonus":
                for stat, value in perk.effect_value.items():
                    if stat in effects:
                        effects[stat] += value
                    else:
                        effects[stat] = value

        return effects

    def get_class_abilities(self) -> List[str]:
        """
        Get class-specific abilities.

        Returns:
            List of ability IDs
        """
        class_abilities = {
            "solo": ["melee_expertise", "combat_specialist", "covering_fire"],
            "netrunner": ["quickhack", "breach_protocol", "system_shock"],
            "techie": ["repair", "upgrade", "craft_ammo"],
            "fixer": ["vendor_discount", "intel", "contacts"],
            "medic": ["heal", "revive", "stim_boost"]
        }

        return class_abilities.get(self.companion_class, [])

    def use_special_ability(self, ability_name: str) -> Optional[Dict[str, Any]]:
        """
        Use a class-specific special ability.

        Args:
            ability_name: Name of ability to use

        Returns:
            Ability effect dictionary or None
        """
        abilities = self.get_class_abilities()

        if ability_name not in abilities:
            return None

        # Define ability effects
        ability_effects = {
            "covering_fire": {
                "effect": "combat_support",
                "target": "enemies",
                "accuracy_penalty": 20,
                "duration": 2
            },
            "quickhack": {
                "effect": "hack",
                "target": "enemy",
                "damage": 30,
                "disable_duration": 1
            },
            "heal": {
                "effect": "heal",
                "target": "ally",
                "amount": 40
            }
        }

        return ability_effects.get(ability_name)

    def on_quest_complete(self, quest_type: str):
        """
        Handle quest completion loyalty gain.

        Args:
            quest_type: Type of quest completed
        """
        loyalty_gains = {
            "main": 15,
            "side": 10,
            "companion": 25  # Companion-specific quest
        }

        gain = loyalty_gains.get(quest_type, 5)
        self.gain_loyalty(gain)

    def equip_weapon(self, weapon):
        """
        Equip a weapon from inventory.

        Args:
            weapon: Weapon item to equip
        """
        self.weapon = weapon.item_id

    def get_combat_stats(self) -> Dict[str, Any]:
        """
        Get combat-ready stats.

        Returns:
            Dictionary of combat stats
        """
        # Base combat stats
        stats = {
            "max_hp": self.max_hp,
            "hp": self.hp,
            "damage_bonus": 0,
            "accuracy": 85  # Base accuracy
        }

        # Add attribute bonuses
        if self.companion_class == "solo":
            stats["damage_bonus"] += self.base_stats["body"] * 3
        elif self.companion_class == "netrunner":
            stats["accuracy"] += self.base_stats["intelligence"] * 2

        # Add loyalty bonuses
        combat_bonus = self.get_combat_bonus()
        stats["damage_bonus"] += combat_bonus["damage"]
        stats["accuracy"] += combat_bonus["accuracy"]

        # Add perk effects
        perk_effects = self.get_active_perk_effects()
        for stat, value in perk_effects.items():
            if stat in stats:
                stats[stat] += value

        return stats

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "companion_id": self.companion_id,
            "name": self.name,
            "companion_class": self.companion_class,
            "base_stats": self.base_stats,
            "max_hp": self.max_hp,
            "hp": self.hp,
            "weapon": self.weapon,
            "is_recruited": self.is_recruited,
            "loyalty": self.loyalty,
            "perks": [perk.to_dict() for perk in self.perks],
            "is_alive": self.is_alive
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Companion':
        """Load from dictionary."""
        companion = cls(
            companion_id=data["companion_id"],
            name=data["name"],
            companion_class=data["companion_class"],
            base_stats=data["base_stats"],
            max_hp=data["max_hp"],
            weapon=data["weapon"]
        )

        companion.hp = data.get("hp", companion.max_hp)
        companion.is_recruited = data.get("is_recruited", False)
        companion.loyalty = data.get("loyalty", 0)
        companion.is_alive = data.get("is_alive", True)

        # Restore perks
        for perk_data in data.get("perks", []):
            perk = CompanionPerk.from_dict(perk_data)
            companion.perks.append(perk)

        return companion


# ============================================================================
# COMPANION MANAGER CLASS
# ============================================================================

class CompanionManager:
    """Manages all companions and squad composition."""

    def __init__(self, max_squad_size: int = 3):
        self.max_squad_size = max_squad_size
        self.companions: Dict[str, Companion] = {}
        self.active_squad: List[str] = []  # List of companion IDs
        self.relationships: Dict[str, Dict[str, str]] = {}  # comp_id -> {comp_id -> level}

    def recruit_companion(self, companion: Companion) -> Dict[str, Any]:
        """
        Recruit a companion.

        Args:
            companion: Companion to recruit

        Returns:
            Result dictionary
        """
        if companion.companion_id in self.companions:
            return {
                "success": False,
                "error": f"{companion.name} is already recruited"
            }

        companion.is_recruited = True
        self.companions[companion.companion_id] = companion

        return {
            "success": True,
            "companion": companion
        }

    def dismiss_companion(self, companion_id: str) -> Dict[str, Any]:
        """
        Dismiss a recruited companion.

        Args:
            companion_id: ID of companion to dismiss

        Returns:
            Result dictionary
        """
        if companion_id not in self.companions:
            return {
                "success": False,
                "error": "Companion not found"
            }

        companion = self.companions[companion_id]
        companion.is_recruited = False

        # Remove from active squad if present
        if companion_id in self.active_squad:
            self.active_squad.remove(companion_id)

        # Remove from companions dict
        del self.companions[companion_id]

        return {
            "success": True
        }

    def add_to_squad(self, companion_id: str) -> Dict[str, Any]:
        """
        Add companion to active squad.

        Args:
            companion_id: ID of companion to add

        Returns:
            Result dictionary
        """
        if companion_id not in self.companions:
            return {
                "success": False,
                "error": "Companion not recruited"
            }

        if len(self.active_squad) >= self.max_squad_size:
            return {
                "success": False,
                "error": f"Squad is full (max {self.max_squad_size})"
            }

        if companion_id in self.active_squad:
            return {
                "success": False,
                "error": "Companion already in squad"
            }

        self.active_squad.append(companion_id)

        return {
            "success": True
        }

    def remove_from_squad(self, companion_id: str) -> Dict[str, Any]:
        """
        Remove companion from active squad.

        Args:
            companion_id: ID of companion to remove

        Returns:
            Result dictionary
        """
        if companion_id not in self.active_squad:
            return {
                "success": False,
                "error": "Companion not in active squad"
            }

        self.active_squad.remove(companion_id)

        return {
            "success": True
        }

    def get_active_squad(self) -> List[Companion]:
        """
        Get list of companions in active squad.

        Returns:
            List of active companions
        """
        # Filter out dead companions
        active_companions = []
        for comp_id in self.active_squad[:]:  # Copy to avoid modification during iteration
            companion = self.companions.get(comp_id)
            if companion and companion.is_alive:
                active_companions.append(companion)
            elif companion and not companion.is_alive:
                # Remove dead companion from squad
                self.active_squad.remove(comp_id)

        return active_companions

    def get_all_companions(self) -> List[Companion]:
        """Get all recruited companions."""
        return list(self.companions.values())

    def get_companion(self, companion_id: str) -> Optional[Companion]:
        """Get specific companion by ID."""
        return self.companions.get(companion_id)

    def get_available_companions(self) -> List[Companion]:
        """Get companions not in active squad."""
        available = []
        for comp_id, companion in self.companions.items():
            if comp_id not in self.active_squad:
                available.append(companion)
        return available

    def set_relationship(
        self,
        companion_id_1: str,
        companion_id_2: str,
        relationship_level: str
    ):
        """
        Set relationship between two companions.

        Args:
            companion_id_1: First companion
            companion_id_2: Second companion
            relationship_level: Relationship level
        """
        if companion_id_1 not in self.relationships:
            self.relationships[companion_id_1] = {}

        self.relationships[companion_id_1][companion_id_2] = relationship_level

    def get_relationship(
        self,
        companion_id_1: str,
        companion_id_2: str
    ) -> str:
        """
        Get relationship between two companions.

        Args:
            companion_id_1: First companion
            companion_id_2: Second companion

        Returns:
            Relationship level or "neutral"
        """
        if companion_id_1 in self.relationships:
            return self.relationships[companion_id_1].get(companion_id_2, "neutral")
        return "neutral"

    def get_squad_synergy_bonus(self) -> int:
        """
        Calculate squad synergy bonus from relationships.

        Returns:
            Total synergy bonus
        """
        synergy = 0

        # Check all pairs in active squad
        for i, comp_id_1 in enumerate(self.active_squad):
            for comp_id_2 in self.active_squad[i+1:]:
                relationship = self.get_relationship(comp_id_1, comp_id_2)

                # Positive relationships add synergy
                if relationship == "friends":
                    synergy += 5
                elif relationship == "best_friends":
                    synergy += 10
                # Negative relationships reduce synergy
                elif relationship == "unfriendly":
                    synergy -= 3
                elif relationship == "hostile":
                    synergy -= 10

        return synergy

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "max_squad_size": self.max_squad_size,
            "companions": {
                comp_id: companion.to_dict()
                for comp_id, companion in self.companions.items()
            },
            "active_squad": self.active_squad.copy(),
            "relationships": self.relationships.copy()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CompanionManager':
        """Load from dictionary."""
        manager = cls(max_squad_size=data.get("max_squad_size", 3))

        # Restore companions
        for comp_data in data.get("companions", {}).values():
            companion = Companion.from_dict(comp_data)
            manager.companions[companion.companion_id] = companion

        # Restore active squad
        manager.active_squad = data.get("active_squad", [])

        # Restore relationships
        manager.relationships = data.get("relationships", {})

        return manager
