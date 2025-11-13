"""
Neon Collapse - Faction Reputation System
Manages relationships with 7 major factions in Night City
"""

from typing import Dict, List, Any, Optional


# Constants
MAX_FACTION_LEVEL = 10
MIN_REP = -100
MAX_REP = 500  # Need 500 rep to reach level 10 (level = rep // 50)


# ============================================================================
# FACTION CLASS
# ============================================================================

class Faction:
    """Represents a single faction with reputation tracking."""

    def __init__(
        self,
        name: str,
        full_name: str,
        description: str,
        hostile_threshold: int = -30,
        allied_threshold: int = 50,
        rivals: List[str] = None
    ):
        self.name = name
        self.full_name = full_name
        self.description = description
        self.rep = 0  # -100 to +100
        self.level = 0  # 0-10
        self.status = "neutral"  # neutral, allied, hostile
        self.hostile_threshold = hostile_threshold
        self.allied_threshold = allied_threshold
        self.rivals = rivals or []

    def adjust_rep(self, amount: int):
        """Adjust reputation and update level/status."""
        self.rep += amount
        # Clamp rep to -100 to +100
        self.rep = max(MIN_REP, min(MAX_REP, self.rep))

        # Update level (only positive rep contributes)
        if self.rep > 0:
            new_level = min(MAX_FACTION_LEVEL, self.rep // 50)
            # Levels don't decrease
            if new_level > self.level:
                self.level = new_level

        # Update status
        if self.rep >= self.allied_threshold:
            self.status = "allied"
        elif self.rep <= self.hostile_threshold:
            self.status = "hostile"
        else:
            self.status = "neutral"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "full_name": self.full_name,
            "description": self.description,
            "rep": self.rep,
            "level": self.level,
            "status": self.status,
            "hostile_threshold": self.hostile_threshold,
            "allied_threshold": self.allied_threshold,
            "rivals": self.rivals
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Faction':
        """Load from dictionary."""
        # Check if this is full serialization or simplified format
        if "name" in data and "full_name" in data:
            # Full serialization format
            faction = cls(
                name=data["name"],
                full_name=data["full_name"],
                description=data["description"],
                hostile_threshold=data.get("hostile_threshold", -30),
                allied_threshold=data.get("allied_threshold", 50),
                rivals=data.get("rivals", [])
            )
            faction.rep = data["rep"]
            faction.level = data["level"]
            faction.status = data["status"]
            return faction
        else:
            # Simplified format (just state) - cannot create faction without full data
            raise ValueError("Cannot create Faction from simplified data without name/full_name")


# ============================================================================
# FACTION MANAGER
# ============================================================================

class FactionManager:
    """Manages all faction relationships."""

    def __init__(self):
        self.factions: Dict[str, Faction] = {}
        self.on_faction_level_up = None  # Optional callback
        self._initialize_factions()

    def _initialize_factions(self):
        """Initialize all 7 factions."""
        # 1. THE SYNDICATE (Secret Shadow Government - World Bible)
        self.factions["syndicate"] = Faction(
            name="syndicate",
            full_name="The Syndicate",
            description="Secret shadow government planning to rebuild",
            hostile_threshold=-40,
            allied_threshold=60,
            rivals=["militech", "voodoo_boys"]
        )

        # 2. TRAUMA CORP (Medical Monopoly - World Bible)
        self.factions["trauma_corp"] = Faction(
            name="trauma_corp",
            full_name="Trauma Corp",
            description="Medical monopoly controlling healthcare",
            hostile_threshold=-20,  # Permanent if attacked
            allied_threshold=50,
            rivals=[]  # Neutral, profits from all sides
        )

        # 3. Militech (Corpo - TDD)
        self.factions["militech"] = Faction(
            name="militech",
            full_name="Militech",
            description="Military corporation, aggressive expansion",
            hostile_threshold=-30,
            allied_threshold=50,
            rivals=["syndicate", "nomads"]
        )

        # 4. Tyger Claws (Gang - TDD)
        self.factions["tyger_claws"] = Faction(
            name="tyger_claws",
            full_name="Tyger Claws",
            description="Yakuza-inspired gang, control entertainment",
            hostile_threshold=-25,
            allied_threshold=45,
            rivals=["voodoo_boys", "scavengers"]
        )

        # 5. Voodoo Boys (Netrunners - TDD)
        self.factions["voodoo_boys"] = Faction(
            name="voodoo_boys",
            full_name="Voodoo Boys",
            description="Elite netrunners, secretive hackers",
            hostile_threshold=-35,
            allied_threshold=55,
            rivals=["tyger_claws", "syndicate"]
        )

        # 6. Nomads (Outsiders - TDD)
        self.factions["nomads"] = Faction(
            name="nomads",
            full_name="Nomads",
            description="Family clans, living outside the city",
            hostile_threshold=-20,  # Hardest to piss off
            allied_threshold=50,
            rivals=["militech"]
        )

        # 7. Scavengers (Criminals - TDD)
        self.factions["scavengers"] = Faction(
            name="scavengers",
            full_name="Scavengers",
            description="Organ harvesters, lowest of the low",
            hostile_threshold=-10,  # Always hostile unless you work for them
            allied_threshold=40,
            rivals=[]  # Everyone hates them
        )

    def get_faction(self, faction_name: str) -> Faction:
        """Get faction by name."""
        if faction_name not in self.factions:
            raise ValueError(f"Unknown faction: {faction_name}")
        return self.factions[faction_name]

    def get_all_faction_names(self) -> List[str]:
        """Get list of all faction names."""
        return list(self.factions.keys())

    def adjust_rep(self, faction_name: str, amount: int):
        """
        Adjust reputation with a faction.
        Also affects rival factions (they lose half as much).
        """
        faction = self.get_faction(faction_name)
        old_level = faction.level

        # Adjust main faction
        faction.adjust_rep(amount)

        # Check for level up
        if faction.level > old_level and self.on_faction_level_up:
            self.on_faction_level_up(faction_name, old_level, faction.level)

        # Adjust rival factions (lose half as much)
        if amount > 0:  # Only affect rivals when gaining positive rep
            for rival_name in faction.rivals:
                if rival_name in self.factions:
                    rival = self.factions[rival_name]
                    rival.adjust_rep(-amount // 2)

    def complete_gig(self, faction_name: str, difficulty: int):
        """
        Complete a gig for a faction.
        Difficulty: 1 (easy) = +10 rep, 2 (medium) = +20, 3 (hard) = +30
        """
        rep_gain = difficulty * 10
        self.adjust_rep(faction_name, rep_gain)

    def get_faction_rewards(self, faction_name: str) -> Dict[str, Any]:
        """Get rewards for current faction level."""
        faction = self.get_faction(faction_name)
        level = faction.level

        # Define reward tiers: level -> reward changes
        reward_tiers = {
            1: {"basic_vendor": True},
            2: {"vendor_discount": 10, "faction_contact": True},
            3: {"vendor_discount": 15},
            4: {"backup_available": True},
            5: {"vendor_discount": 20},
            6: {"vendor_discount": 20},
            7: {"vendor_discount": 25},
            8: {"ending_path_unlocked": True},
            9: {"vendor_discount": 30},
            10: {"free_gear": True, "vendor_discount": 100}
        }

        # Start with default rewards
        rewards = {
            "vendor_discount": 0,
            "basic_vendor": False,
            "faction_contact": False,
            "backup_available": False,
            "ending_path_unlocked": False,
            "free_gear": False
        }

        # Apply all rewards up to current level
        for tier_level in sorted(reward_tiers.keys()):
            if level >= tier_level:
                rewards.update(reward_tiers[tier_level])

        return rewards

    def is_hostile(self, faction_name: str) -> bool:
        """Check if faction is hostile."""
        faction = self.get_faction(faction_name)
        return faction.status == "hostile"

    def get_allied_factions(self) -> List[Faction]:
        """Get all allied factions."""
        return [f for f in self.factions.values() if f.status == "allied"]

    def get_hostile_factions(self) -> List[Faction]:
        """Get all hostile factions."""
        return [f for f in self.factions.values() if f.status == "hostile"]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "factions": {
                name: faction.to_dict()
                for name, faction in self.factions.items()
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FactionManager':
        """Load from dictionary."""
        manager = cls()

        # Restore faction states
        for name, faction_data in data["factions"].items():
            if name in manager.factions:
                # Check if full data or just state update
                if "name" in faction_data and "full_name" in faction_data:
                    # Full serialization - replace faction
                    manager.factions[name] = Faction.from_dict(faction_data)
                else:
                    # Simplified format - just update state
                    faction = manager.factions[name]
                    faction.rep = faction_data.get("rep", 0)
                    faction.level = faction_data.get("level", 0)
                    faction.status = faction_data.get("status", "neutral")

        return manager
