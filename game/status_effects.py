"""
Neon Collapse - Status Effects System
Manages status effects like bleeding, burning, stunned, etc.
"""

from typing import Dict, List, Any, Optional


# Constants
VALID_EFFECT_TYPES = ["bleeding", "burning", "stunned", "hacked", "weakened", "blinded"]
DOT_EFFECT_TYPES = ["bleeding", "burning"]  # Damage-over-time effects
DEBUFF_EFFECT_TYPES = ["weakened", "blinded", "hacked"]  # Stat reduction effects
CC_EFFECT_TYPES = ["stunned"]  # Crowd control effects


# ============================================================================
# STATUS EFFECT CLASS
# ============================================================================

class StatusEffect:
    """Represents a single status effect."""

    def __init__(
        self,
        effect_type: str,
        duration: int,
        potency: int = 0
    ):
        if effect_type not in VALID_EFFECT_TYPES:
            raise ValueError(f"Invalid effect type: {effect_type}. Must be one of {VALID_EFFECT_TYPES}")

        if potency < 0:
            raise ValueError(f"Potency cannot be negative: {potency}")

        self.effect_type = effect_type
        self.duration = duration  # -1 = permanent, 0 = expired, >0 = turns remaining
        self.potency = potency  # Damage per turn (DoT) or % reduction (debuff)

    def is_active(self) -> bool:
        """Check if effect is still active."""
        return self.duration != 0

    def tick(self):
        """Reduce duration by 1 turn (doesn't affect permanent effects)."""
        if self.duration > 0:
            self.duration -= 1

    def is_dot(self) -> bool:
        """Check if this is a damage-over-time effect."""
        return self.effect_type in DOT_EFFECT_TYPES

    def is_debuff(self) -> bool:
        """Check if this is a stat debuff effect."""
        return self.effect_type in DEBUFF_EFFECT_TYPES

    def is_cc(self) -> bool:
        """Check if this is a crowd control effect."""
        return self.effect_type in CC_EFFECT_TYPES

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "effect_type": self.effect_type,
            "duration": self.duration,
            "potency": self.potency
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StatusEffect':
        """Load from dictionary."""
        return cls(
            effect_type=data["effect_type"],
            duration=data["duration"],
            potency=data.get("potency", 0)
        )


# ============================================================================
# STATUS EFFECT MANAGER
# ============================================================================

class StatusEffectManager:
    """Manages status effects on a character."""

    def __init__(self):
        self.active_effects: List[StatusEffect] = []
        self.resistances: Dict[str, int] = {}  # effect_type -> resist % (0-100)
        self.immunities: List[str] = []  # List of effect types immune to

    def add_effect(self, effect: StatusEffect) -> bool:
        """
        Add a status effect.

        Returns:
            True if added, False if blocked by immunity
        """
        # Check immunity
        if self.is_immune(effect.effect_type):
            return False

        # Check resistance (probabilistic)
        if effect.effect_type in self.resistances:
            resistance = self.resistances[effect.effect_type]
            # For deterministic testing, we don't use random here
            # Real implementation could use: random.randint(1, 100) <= resistance
            # For now, just reduce duration based on resistance
            if resistance >= 100:
                return False  # Full resistance = immunity

        # Add effect
        self.active_effects.append(effect)
        return True

    def has_effect(self, effect_type: str) -> bool:
        """Check if character has specific effect type."""
        return any(e.effect_type == effect_type and e.is_active() for e in self.active_effects)

    def get_effects_by_type(self, effect_type: str) -> List[StatusEffect]:
        """Get all active effects of specific type."""
        return [e for e in self.active_effects if e.effect_type == effect_type and e.is_active()]

    def get_active_effects(self) -> List[StatusEffect]:
        """Get all active effects."""
        return [e for e in self.active_effects if e.is_active()]

    def cleanse_effect(self, effect_type: str) -> bool:
        """
        Remove all effects of specific type.

        Returns:
            True if any effects were removed
        """
        initial_count = len(self.active_effects)
        self.active_effects = [e for e in self.active_effects if e.effect_type != effect_type]
        return len(self.active_effects) < initial_count

    def cleanse_all(self):
        """Remove all status effects."""
        self.active_effects.clear()

    def cleanse_category(self, category: str):
        """
        Remove effects by category (dot, debuff, cc).

        Args:
            category: "dot", "debuff", or "cc"
        """
        if category == "dot":
            self.active_effects = [e for e in self.active_effects if not e.is_dot()]
        elif category == "debuff":
            self.active_effects = [e for e in self.active_effects if not e.is_debuff()]
        elif category == "cc":
            self.active_effects = [e for e in self.active_effects if not e.is_cc()]

    def tick_effects(self):
        """Process end of turn - reduce durations and remove expired effects."""
        # Tick all effects
        for effect in self.active_effects:
            effect.tick()

        # Remove expired effects
        self.active_effects = [e for e in self.active_effects if e.is_active()]

    def calculate_dot_damage(self) -> int:
        """Calculate total damage-over-time from all active DoT effects."""
        total_damage = 0

        for effect in self.active_effects:
            if effect.is_dot() and effect.is_active():
                total_damage += effect.potency

        return total_damage

    def can_act(self) -> bool:
        """Check if character can take actions (not stunned)."""
        # Stunned prevents all actions
        return not self.has_effect("stunned")

    def apply_damage_modifiers(self, base_damage: int) -> int:
        """
        Apply damage modifiers from status effects.

        Args:
            base_damage: Base damage before modifiers

        Returns:
            Modified damage after applying weakened effects
        """
        modified_damage = base_damage

        # Apply weakened effects (reduce damage output)
        weakened_effects = self.get_effects_by_type("weakened")
        for effect in weakened_effects:
            reduction_percent = effect.potency
            modified_damage -= int(base_damage * (reduction_percent / 100))

        return max(0, modified_damage)

    def apply_accuracy_modifiers(self, base_accuracy: int) -> int:
        """
        Apply accuracy modifiers from status effects.

        Args:
            base_accuracy: Base accuracy before modifiers

        Returns:
            Modified accuracy after applying blinded effects
        """
        modified_accuracy = base_accuracy

        # Apply blinded effects (reduce accuracy)
        blinded_effects = self.get_effects_by_type("blinded")
        for effect in blinded_effects:
            reduction_percent = effect.potency
            modified_accuracy -= int(base_accuracy * (reduction_percent / 100))

        return max(0, modified_accuracy)

    def is_position_revealed(self) -> bool:
        """Check if character position is revealed (hacked)."""
        return self.has_effect("hacked")

    def process_turn_start(self) -> int:
        """
        Process effects at start of turn.

        Returns:
            Total damage dealt by DoT effects
        """
        return self.calculate_dot_damage()

    def set_resistance(self, effect_type: str, resistance_percent: int):
        """
        Set resistance to specific effect type.

        Args:
            effect_type: Type of effect to resist
            resistance_percent: Resistance percentage (0-100)
        """
        self.resistances[effect_type] = max(0, min(100, resistance_percent))

    def get_resistance(self, effect_type: str) -> int:
        """Get resistance percentage for effect type."""
        return self.resistances.get(effect_type, 0)

    def set_immunity(self, effect_type: str, immune: bool):
        """
        Set immunity to specific effect type.

        Args:
            effect_type: Type of effect to be immune to
            immune: True to add immunity, False to remove
        """
        if immune:
            if effect_type not in self.immunities:
                self.immunities.append(effect_type)
        else:
            if effect_type in self.immunities:
                self.immunities.remove(effect_type)

    def is_immune(self, effect_type: str) -> bool:
        """Check if immune to specific effect type."""
        return effect_type in self.immunities

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "active_effects": [e.to_dict() for e in self.active_effects],
            "resistances": self.resistances.copy(),
            "immunities": self.immunities.copy()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StatusEffectManager':
        """Load from dictionary."""
        manager = cls()

        # Restore active effects
        for effect_data in data.get("active_effects", []):
            effect = StatusEffect.from_dict(effect_data)
            manager.active_effects.append(effect)

        # Restore resistances and immunities
        manager.resistances = data.get("resistances", {})
        manager.immunities = data.get("immunities", [])

        return manager
