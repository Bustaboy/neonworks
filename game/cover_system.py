"""
Neon Collapse - Cover System
Manages cover mechanics, dodge bonuses, and cover destruction
"""

from typing import Dict, List, Any, Optional
import random


# Constants
VALID_COVER_TYPES = ["none", "half", "full"]
COVER_DODGE_BONUS = {
    "none": 0,
    "half": 20,   # +20% dodge
    "full": 40    # +40% dodge
}

TAKE_COVER_ACTION_COST = 1
LEAVE_COVER_ACTION_COST = 0


# ============================================================================
# COVER OBJECT CLASS
# ============================================================================

class CoverObject:
    """Represents a physical cover object (wall, crate, barrier)."""

    def __init__(
        self,
        cover_id: str,
        cover_type: str,
        hp: int
    ):
        if cover_type not in VALID_COVER_TYPES:
            if cover_type in ["half", "full"]:  # Valid but need to check
                pass
            else:
                raise ValueError(f"Invalid cover type: {cover_type}. Must be 'half' or 'full'")

        self.cover_id = cover_id
        self.cover_type = cover_type
        self.max_hp = hp
        self.hp = hp

    def take_damage(self, damage: int):
        """
        Cover takes damage.

        Args:
            damage: Amount of damage
        """
        if damage < 0:
            return  # Ignore negative damage

        self.hp = max(0, self.hp - damage)

    def is_destroyed(self) -> bool:
        """Check if cover is destroyed."""
        return self.hp <= 0

    def get_dodge_bonus(self) -> int:
        """Get dodge bonus provided by this cover."""
        if self.is_destroyed():
            return 0

        return COVER_DODGE_BONUS.get(self.cover_type, 0)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "cover_id": self.cover_id,
            "cover_type": self.cover_type,
            "hp": self.hp,
            "max_hp": self.max_hp
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CoverObject':
        """Load from dictionary."""
        cover = cls(
            cover_id=data["cover_id"],
            cover_type=data["cover_type"],
            hp=data["max_hp"]
        )
        cover.hp = data["hp"]
        return cover


# ============================================================================
# COVER MANAGER CLASS
# ============================================================================

class CoverManager:
    """Manages character's cover state."""

    def __init__(self):
        self.current_cover: Optional[CoverObject] = None

    def take_cover(self, cover: CoverObject) -> bool:
        """
        Character takes cover behind object.

        Args:
            cover: Cover object to use

        Returns:
            True if successful, False if cover is destroyed
        """
        if cover.is_destroyed():
            return False

        self.current_cover = cover
        return True

    def leave_cover(self):
        """Character leaves cover."""
        self.current_cover = None

    def in_cover(self) -> bool:
        """Check if character is in cover."""
        return self.current_cover is not None and not self.current_cover.is_destroyed()

    def has_valid_cover(self) -> bool:
        """Check if character has valid (non-destroyed) cover."""
        if self.current_cover is None:
            return False
        return not self.current_cover.is_destroyed()

    def get_cover_type(self) -> str:
        """Get current cover type."""
        if not self.in_cover():
            return "none"
        return self.current_cover.cover_type

    def get_dodge_bonus(self) -> int:
        """Get dodge bonus from current cover."""
        if not self.in_cover():
            return 0

        return self.current_cover.get_dodge_bonus()

    def apply_cover_to_hit_chance(self, base_hit_chance: int) -> int:
        """
        Apply cover dodge bonus to attacker's hit chance.

        Args:
            base_hit_chance: Base hit chance percentage

        Returns:
            Modified hit chance after cover bonus
        """
        dodge_bonus = self.get_dodge_bonus()
        modified = base_hit_chance - dodge_bonus

        return max(0, modified)

    def process_cover_hit(self, damage: int):
        """
        Process damage to cover (when attack misses character).

        Args:
            damage: Damage amount to apply to cover
        """
        if self.current_cover:
            self.current_cover.take_damage(damage)

    def blocks_line_of_sight(self) -> bool:
        """Check if cover blocks line of sight."""
        if not self.in_cover():
            return False

        # Only full cover blocks sight
        return self.current_cover.cover_type == "full"

    def get_take_cover_cost(self) -> int:
        """Get action cost to take cover."""
        return TAKE_COVER_ACTION_COST

    def get_leave_cover_cost(self) -> int:
        """Get action cost to leave cover."""
        return LEAVE_COVER_ACTION_COST

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "current_cover": self.current_cover.to_dict() if self.current_cover else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CoverManager':
        """Load from dictionary."""
        manager = cls()

        if data.get("current_cover"):
            cover = CoverObject.from_dict(data["current_cover"])
            manager.current_cover = cover

        return manager


# ============================================================================
# COVER AI CLASS
# ============================================================================

class CoverAI:
    """AI decision making for cover usage."""

    def __init__(self):
        pass

    def should_seek_cover(
        self,
        current_hp: int,
        max_hp: int,
        available_cover: List[CoverObject]
    ) -> bool:
        """
        Decide if AI should seek cover.

        Args:
            current_hp: Current HP
            max_hp: Maximum HP
            available_cover: List of available cover objects

        Returns:
            True if should seek cover
        """
        if not available_cover:
            return False

        # Calculate HP percentage
        hp_percent = (current_hp / max_hp) * 100

        # Low HP = high priority to seek cover
        if hp_percent < 30:
            return True
        elif hp_percent < 60:
            # Medium HP = maybe seek cover
            return random.random() < 0.6
        else:
            # High HP = less priority
            return random.random() < 0.3

    def choose_best_cover(self, available_cover: List[CoverObject]) -> Optional[CoverObject]:
        """
        Choose best cover from available options.

        Args:
            available_cover: List of cover objects

        Returns:
            Best cover object, or None if none available
        """
        if not available_cover:
            return None

        # Filter out destroyed cover
        valid_cover = [c for c in available_cover if not c.is_destroyed()]

        if not valid_cover:
            return None

        # Prioritize full cover over half cover
        # Then prioritize higher HP

        def cover_score(cover: CoverObject) -> float:
            score = 0.0

            # Full cover worth more
            if cover.cover_type == "full":
                score += 100
            elif cover.cover_type == "half":
                score += 50

            # Add HP as tiebreaker
            score += cover.hp

            return score

        # Sort by score and return best
        sorted_cover = sorted(valid_cover, key=cover_score, reverse=True)
        return sorted_cover[0]


# ============================================================================
# COMBAT ENCOUNTER CLASS
# ============================================================================

class CombatEncounter:
    """Manages cover in combat encounters."""

    def __init__(self):
        self.available_cover: List[CoverObject] = []

    def add_cover(self, cover: CoverObject):
        """Add cover object to encounter."""
        self.available_cover.append(cover)

    def get_cover(self, cover_id: str) -> Optional[CoverObject]:
        """
        Get specific cover object by ID.

        Args:
            cover_id: Cover object ID

        Returns:
            Cover object or None if not found
        """
        for cover in self.available_cover:
            if cover.cover_id == cover_id:
                return cover
        return None

    def generate_random_cover(self, difficulty: str):
        """
        Generate random cover for encounter.

        Args:
            difficulty: Encounter difficulty (easy, medium, hard)
        """
        # Number of cover objects based on difficulty
        num_cover = {
            "easy": random.randint(1, 2),
            "medium": random.randint(2, 4),
            "hard": random.randint(3, 5),
            "extreme": random.randint(4, 6)
        }.get(difficulty, 2)

        for i in range(num_cover):
            # Random cover type
            cover_type = random.choice(["half", "half", "full"])  # Half more common

            # Random HP based on type
            if cover_type == "half":
                hp = random.randint(40, 80)
            else:  # full
                hp = random.randint(80, 150)

            cover = CoverObject(
                cover_id=f"cover_{i}",
                cover_type=cover_type,
                hp=hp
            )

            self.available_cover.append(cover)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "available_cover": [c.to_dict() for c in self.available_cover]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CombatEncounter':
        """Load from dictionary."""
        encounter = cls()

        for cover_data in data.get("available_cover", []):
            cover = CoverObject.from_dict(cover_data)
            encounter.available_cover.append(cover)

        return encounter
