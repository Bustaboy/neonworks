"""
JRPG Combat Components

Components for traditional JRPG-style combat with MP, magic, formations, etc.
"""

from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from engine.core.ecs import Component


class ElementType(Enum):
    """Elemental types for spells and resistances"""

    NONE = "none"
    FIRE = "fire"
    ICE = "ice"
    LIGHTNING = "lightning"
    EARTH = "earth"
    WIND = "wind"
    WATER = "water"
    HOLY = "holy"
    DARK = "dark"


class TargetType(Enum):
    """Spell/ability target types"""

    SINGLE_ENEMY = "single_enemy"
    ALL_ENEMIES = "all_enemies"
    SINGLE_ALLY = "single_ally"
    ALL_ALLIES = "all_allies"
    SELF = "self"
    ALL = "all"


class BattleCommand(Enum):
    """Battle menu commands"""

    ATTACK = "attack"
    MAGIC = "magic"
    ITEM = "item"
    DEFEND = "defend"
    RUN = "run"
    SPECIAL = "special"


@dataclass
class MagicPoints(Component):
    """
    MP (Magic Points) component for spell casting.
    """

    current_mp: int = 50
    max_mp: int = 50
    mp_regen_rate: float = 0.0  # MP per turn

    def get_mp_percentage(self) -> float:
        """Get MP as percentage (0-100)"""
        if self.max_mp <= 0:
            return 0.0
        return (self.current_mp / self.max_mp) * 100.0

    def has_enough_mp(self, cost: int) -> bool:
        """Check if enough MP for action"""
        return self.current_mp >= cost

    def consume_mp(self, cost: int) -> bool:
        """Consume MP, return True if successful"""
        if not self.has_enough_mp(cost):
            return False
        self.current_mp -= cost
        return True

    def restore_mp(self, amount: int):
        """Restore MP (up to max)"""
        self.current_mp = min(self.current_mp + amount, self.max_mp)


@dataclass
class JRPGStats(Component):
    """
    JRPG-style character statistics.

    Traditional RPG stats for damage calculation and combat.
    """

    # Primary stats
    level: int = 1
    experience: int = 0
    experience_to_next: int = 100

    # Combat stats
    attack: int = 10  # Physical attack power
    defense: int = 10  # Physical defense
    magic_attack: int = 10  # Magical attack power
    magic_defense: int = 10  # Magical defense
    speed: int = 10  # Turn order/evasion
    luck: int = 10  # Critical hits/status resist

    # Status
    status_effects: List[str] = field(default_factory=list)

    def calculate_physical_damage(self, target: "JRPGStats") -> int:
        """Calculate physical damage to target"""
        base_damage = max(1, self.attack - target.defense // 2)
        variance = 1.0  # Can add randomness
        return int(base_damage * variance)

    def calculate_magic_damage(self, power: int, target: "JRPGStats") -> int:
        """Calculate magical damage to target"""
        base_damage = max(1, (self.magic_attack + power) - target.magic_defense // 2)
        return base_damage

    def has_status(self, status: str) -> bool:
        """Check if character has status effect"""
        return status in self.status_effects

    def add_status(self, status: str):
        """Add status effect"""
        if status not in self.status_effects:
            self.status_effects.append(status)

    def remove_status(self, status: str):
        """Remove status effect"""
        if status in self.status_effects:
            self.status_effects.remove(status)


@dataclass
class ElementalResistances(Component):
    """
    Elemental resistance/weakness system.

    Values:
    - 2.0 = weakness (200% damage)
    - 1.0 = normal
    - 0.5 = resistance (50% damage)
    - 0.0 = immune
    - -1.0 = absorb (heal from this element)
    """

    resistances: Dict[ElementType, float] = field(
        default_factory=lambda: {
            ElementType.FIRE: 1.0,
            ElementType.ICE: 1.0,
            ElementType.LIGHTNING: 1.0,
            ElementType.EARTH: 1.0,
            ElementType.WIND: 1.0,
            ElementType.WATER: 1.0,
            ElementType.HOLY: 1.0,
            ElementType.DARK: 1.0,
        }
    )

    def get_multiplier(self, element: ElementType) -> float:
        """Get damage multiplier for element"""
        return self.resistances.get(element, 1.0)

    def is_weak_to(self, element: ElementType) -> bool:
        """Check if weak to element"""
        return self.get_multiplier(element) > 1.0

    def is_resistant_to(self, element: ElementType) -> bool:
        """Check if resistant to element"""
        mult = self.get_multiplier(element)
        return 0.0 < mult < 1.0

    def is_immune_to(self, element: ElementType) -> bool:
        """Check if immune to element"""
        return self.get_multiplier(element) == 0.0

    def absorbs(self, element: ElementType) -> bool:
        """Check if absorbs element (heals)"""
        return self.get_multiplier(element) < 0.0


@dataclass
class Spell:
    """Spell definition"""

    spell_id: str
    name: str
    description: str
    mp_cost: int
    power: int
    element: ElementType
    target_type: TargetType

    # Effects
    damage: int = 0  # Base damage (0 for non-damage spells)
    healing: int = 0  # Base healing
    status_effect: Optional[str] = None
    status_chance: float = 100.0  # Percentage

    # Animation/visual
    animation: str = ""

    def can_cast(self, caster_mp: MagicPoints) -> bool:
        """Check if spell can be cast"""
        return caster_mp.has_enough_mp(self.mp_cost)


@dataclass
class SpellList(Component):
    """
    Component for entities that can cast spells.

    Tracks learned spells and spell data.
    """

    learned_spells: List[str] = field(default_factory=list)  # List of spell IDs

    # Spell cooldowns (for abilities with cooldowns)
    cooldowns: Dict[str, int] = field(
        default_factory=dict
    )  # spell_id -> turns remaining

    def knows_spell(self, spell_id: str) -> bool:
        """Check if spell is learned"""
        return spell_id in self.learned_spells

    def learn_spell(self, spell_id: str):
        """Learn a new spell"""
        if not self.knows_spell(spell_id):
            self.learned_spells.append(spell_id)

    def forget_spell(self, spell_id: str):
        """Forget a spell"""
        if self.knows_spell(spell_id):
            self.learned_spells.remove(spell_id)

    def is_on_cooldown(self, spell_id: str) -> bool:
        """Check if spell is on cooldown"""
        return self.cooldowns.get(spell_id, 0) > 0

    def set_cooldown(self, spell_id: str, turns: int):
        """Set spell cooldown"""
        self.cooldowns[spell_id] = turns

    def reduce_cooldowns(self):
        """Reduce all cooldowns by 1 (call each turn)"""
        for spell_id in list(self.cooldowns.keys()):
            self.cooldowns[spell_id] -= 1
            if self.cooldowns[spell_id] <= 0:
                del self.cooldowns[spell_id]


@dataclass
class BattleFormation(Component):
    """
    Battle formation component for party positioning.

    Determines position in battle (front row, back row, etc.)
    """

    row: int = 0  # 0 = front, 1 = back
    position: int = 0  # Position within row (0-3)

    # Formation effects
    damage_multiplier: float = 1.0  # Damage dealt
    defense_multiplier: float = 1.0  # Damage taken

    def is_front_row(self) -> bool:
        """Check if in front row"""
        return self.row == 0

    def is_back_row(self) -> bool:
        """Check if in back row"""
        return self.row == 1


@dataclass
class BattleAI(Component):
    """
    AI component for enemy battle behavior.

    Defines AI patterns and decision making.
    """

    ai_type: str = "basic"  # basic, aggressive, defensive, healer, etc.

    # Targeting preferences
    target_priority: str = "random"  # random, lowest_hp, highest_hp, etc.

    # Ability usage
    spell_usage_chance: float = 30.0  # Percentage chance to use spell
    preferred_spells: List[str] = field(default_factory=list)

    # Behavior patterns
    attack_pattern: List[str] = field(default_factory=list)  # Sequence of actions
    current_pattern_index: int = 0

    # Callbacks for custom AI
    on_decide_action: Optional[Callable] = None


@dataclass
class BattleState(Component):
    """
    Component tracking an entity's state in battle.

    Tracks turn order, actions, and battle-specific state.
    """

    # Turn state
    initiative: int = 0  # Turn order (higher goes first)
    has_acted: bool = False
    is_defending: bool = False

    # Current action (if any)
    pending_action: Optional[str] = None
    pending_targets: List[str] = field(default_factory=list)  # Entity IDs

    # Battle stats
    damage_dealt: int = 0
    damage_taken: int = 0
    healing_done: int = 0

    # Flags
    can_act: bool = True
    is_escaping: bool = False


@dataclass
class BattleRewards(Component):
    """
    Rewards given when enemy is defeated.

    Attached to enemy entities.
    """

    experience: int = 10
    gold: int = 5
    items: List[Dict[str, Any]] = field(
        default_factory=list
    )  # item_id, chance, quantity

    # Special drops
    steal_items: List[Dict[str, Any]] = field(default_factory=list)
    rare_drop: Optional[str] = None
    rare_drop_chance: float = 5.0  # Percentage


@dataclass
class BossPhase(Component):
    """
    Multi-phase boss mechanics.

    Defines different phases and triggers.
    """

    current_phase: int = 1
    max_phases: int = 1

    # Phase data (phase_number -> phase_info)
    phases: Dict[int, Dict[str, Any]] = field(default_factory=dict)

    # Phase triggers (typically HP thresholds)
    phase_triggers: List[float] = field(default_factory=list)  # HP percentages

    # Callbacks
    on_phase_change: Optional[Callable[[int, int], None]] = (
        None  # (old_phase, new_phase)
    )

    def should_advance_phase(self, hp_percentage: float) -> bool:
        """Check if should advance to next phase"""
        if self.current_phase >= self.max_phases:
            return False

        if self.current_phase <= len(self.phase_triggers):
            threshold = self.phase_triggers[self.current_phase - 1]
            return hp_percentage <= threshold

        return False

    def advance_phase(self):
        """Advance to next phase"""
        if self.current_phase < self.max_phases:
            old_phase = self.current_phase
            self.current_phase += 1

            if self.on_phase_change:
                self.on_phase_change(old_phase, self.current_phase)

    def get_current_phase_data(self) -> Dict[str, Any]:
        """Get current phase data"""
        return self.phases.get(self.current_phase, {})


@dataclass
class PartyMember(Component):
    """
    Component marking an entity as a party member.

    Tracks party position and availability.
    """

    character_id: str = ""  # Unique character ID
    party_index: int = 0  # Position in party (0-3)
    is_active: bool = True  # In active party?

    # Character data
    character_name: str = ""
    character_class: str = "fighter"

    # Availability
    is_available: bool = True  # Can be used in party?
    unlock_condition: Optional[str] = None


@dataclass
class EnemyData(Component):
    """
    Component for enemy-specific data.

    Tracks enemy type, behavior, and encounter info.
    """

    enemy_id: str = ""
    enemy_name: str = ""
    enemy_type: str = "normal"  # normal, elite, boss

    # Encounter data
    encounter_weight: int = 10  # Spawn weight in encounter tables
    min_level: int = 1
    max_level: int = 99

    # Behavior flags
    is_boss: bool = False
    can_escape_from: bool = True
    can_steal_from: bool = True

    # Visual
    battle_sprite: str = ""
    battle_position: int = 0  # Position in enemy formation
