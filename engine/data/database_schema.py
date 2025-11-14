"""
Database Schema
===============

Comprehensive data structures for game database including items, skills, enemies,
actors, classes, weapons, armor, states, and animations.

All classes are JSON-serializable via to_dict() and from_dict() methods.

Data Ranges and Constraints:
----------------------------
- IDs: 1-9999 (positive integers)
- Stats (HP, MP, ATK, DEF, etc.): 0-9999
- Percentages: 0-100 (integer percent)
- Probabilities: 0.0-1.0 (float)
- Prices: 0-999999
- Experience: 0-9999999
- Gold: 0-999999
- Opacity: 0-255
- Animation frames: 1-999
- Hit/Evasion rates: 0-100 (percent)
- Critical rates: 0-100 (percent)
- Element/State rates: 0-200 (percent, where 100 is normal)
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


# =============================================================================
# Enumerations
# =============================================================================


class EffectType(Enum):
    """Types of effects that can be applied."""

    RECOVER_HP = "recover_hp"  # Restore HP
    RECOVER_MP = "recover_mp"  # Restore MP
    DAMAGE_HP = "damage_hp"  # Deal HP damage
    DAMAGE_MP = "damage_mp"  # Deal MP damage
    ADD_STATE = "add_state"  # Apply a state/status
    REMOVE_STATE = "remove_state"  # Remove a state/status
    ADD_BUFF = "add_buff"  # Increase stat temporarily
    ADD_DEBUFF = "add_debuff"  # Decrease stat temporarily
    REMOVE_BUFF = "remove_buff"  # Remove stat increase
    REMOVE_DEBUFF = "remove_debuff"  # Remove stat decrease
    SPECIAL = "special"  # Special effect (custom handling)
    GROW = "grow"  # Permanent stat increase
    LEARN_SKILL = "learn_skill"  # Teach a skill
    COMMON_EVENT = "common_event"  # Trigger common event


class EffectTiming(Enum):
    """When an effect is applied."""

    IMMEDIATE = "immediate"  # Applied immediately when used
    TURN_START = "turn_start"  # Applied at start of turn
    TURN_END = "turn_end"  # Applied at end of turn
    BATTLE_START = "battle_start"  # Applied at battle start
    BATTLE_END = "battle_end"  # Applied at battle end
    ON_HIT = "on_hit"  # Applied when attack hits
    ON_DAMAGE = "on_damage"  # Applied when taking damage


class ElementType(Enum):
    """Elemental damage types."""

    NORMAL = "normal"  # No element
    FIRE = "fire"
    ICE = "ice"
    THUNDER = "thunder"
    WATER = "water"
    EARTH = "earth"
    WIND = "wind"
    LIGHT = "light"
    DARK = "dark"
    POISON = "poison"


class DamageType(Enum):
    """Types of damage calculation."""

    NONE = "none"  # No damage
    HP_DAMAGE = "hp_damage"  # Physical HP damage
    MP_DAMAGE = "mp_damage"  # MP damage
    HP_RECOVER = "hp_recover"  # HP recovery
    MP_RECOVER = "mp_recover"  # MP recovery
    HP_DRAIN = "hp_drain"  # Absorb HP
    MP_DRAIN = "mp_drain"  # Absorb MP


class ItemType(Enum):
    """Types of items."""

    REGULAR = "regular"  # Regular item (consumable)
    KEY = "key"  # Key item (non-consumable, important)
    HIDDEN_A = "hidden_a"  # Hidden item type A
    HIDDEN_B = "hidden_b"  # Hidden item type B


class SkillType(Enum):
    """Types of skills."""

    MAGIC = "magic"  # Magic skill
    SPECIAL = "special"  # Special skill
    PHYSICAL = "physical"  # Physical skill


class WeaponType(Enum):
    """Types of weapons."""

    SWORD = "sword"
    SPEAR = "spear"
    AXE = "axe"
    BOW = "bow"
    STAFF = "staff"
    DAGGER = "dagger"
    FIST = "fist"
    GUN = "gun"


class ArmorType(Enum):
    """Types of armor."""

    SHIELD = "shield"
    HELMET = "helmet"
    BODY = "body"
    ACCESSORY = "accessory"


class EquipType(Enum):
    """Equipment slot types."""

    WEAPON = "weapon"
    SHIELD = "shield"
    HELMET = "helmet"
    BODY = "body"
    ACCESSORY = "accessory"


class StateRestriction(Enum):
    """What a state restricts the actor from doing."""

    NONE = "none"  # No restriction
    ATTACK_ENEMY = "attack_enemy"  # Cannot select attack
    ATTACK_ANYONE = "attack_anyone"  # Attacks random target
    ATTACK_ALLY = "attack_ally"  # Attacks allies
    CANNOT_MOVE = "cannot_move"  # Cannot take any action


# =============================================================================
# Effect System
# =============================================================================


@dataclass
class Effect:
    """
    Represents a single effect that can be applied to targets.

    Used by Items and Skills to define what they do when used.

    Constraints:
    - value1, value2: -9999 to 9999
    - rate: 0.0 to 1.0 (probability)
    """

    effect_type: EffectType = EffectType.RECOVER_HP
    value1: float = 0.0  # Base value or percentage (context-dependent)
    value2: float = 0.0  # Variance or additional value
    timing: EffectTiming = EffectTiming.IMMEDIATE
    target_param: int = 0  # Parameter ID (for buffs, states, etc.)
    rate: float = 1.0  # Success rate (0.0-1.0)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "effect_type": self.effect_type.value,
            "value1": self.value1,
            "value2": self.value2,
            "timing": self.timing.value,
            "target_param": self.target_param,
            "rate": self.rate,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Effect":
        """Create Effect from dictionary."""
        return cls(
            effect_type=EffectType(data.get("effect_type", "recover_hp")),
            value1=float(data.get("value1", 0.0)),
            value2=float(data.get("value2", 0.0)),
            timing=EffectTiming(data.get("timing", "immediate")),
            target_param=int(data.get("target_param", 0)),
            rate=float(data.get("rate", 1.0)),
        )

    def validate(self) -> bool:
        """
        Validate effect values.

        Returns:
            True if valid, False otherwise
        """
        if not -9999 <= self.value1 <= 9999:
            return False
        if not -9999 <= self.value2 <= 9999:
            return False
        if not 0.0 <= self.rate <= 1.0:
            return False
        return True


# =============================================================================
# Base Database Entry
# =============================================================================


@dataclass
class DatabaseEntry:
    """
    Base class for all database entries.

    Provides common fields and JSON serialization interface.

    Constraints:
    - id: 1-9999
    - name: 1-100 characters recommended
    - note: unlimited (for metadata/comments)
    """

    id: int = 0
    name: str = ""
    icon_index: int = 0  # Icon index in iconset (0-999)
    description: str = ""
    note: str = ""  # Internal note/metadata for developers

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "icon_index": self.icon_index,
            "description": self.description,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DatabaseEntry":
        """Create DatabaseEntry from dictionary."""
        return cls(
            id=data.get("id", 0),
            name=data.get("name", ""),
            icon_index=data.get("icon_index", 0),
            description=data.get("description", ""),
            note=data.get("note", ""),
        )

    def validate(self) -> bool:
        """
        Validate common fields.

        Returns:
            True if valid, False otherwise
        """
        if not 0 <= self.id <= 9999:
            return False
        if not self.name:
            return False
        if not 0 <= self.icon_index <= 999:
            return False
        return True


# =============================================================================
# Item Class
# =============================================================================


@dataclass
class Item(DatabaseEntry):
    """
    Consumable or key item.

    Constraints:
    - price: 0-999999
    - consumable: True for regular items, False for key items
    - effects: List of Effect objects
    """

    item_type: ItemType = ItemType.REGULAR
    price: int = 0
    consumable: bool = True
    occasion: int = 0  # 0=always, 1=battle, 2=menu, 3=never
    scope: int = 1  # 0=none, 1=one enemy, 2=all enemies, 3=one ally, etc.
    speed: int = 0  # Speed correction (-9999 to 9999)
    success_rate: int = 100  # Success rate (0-100%)
    tp_gain: int = 0  # TP gained when used (0-100)
    hit_type: int = 0  # 0=certain, 1=physical, 2=magical
    animation_id: int = 0  # Animation to play when used
    effects: List[Effect] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        base = super().to_dict()
        base.update(
            {
                "item_type": self.item_type.value,
                "price": self.price,
                "consumable": self.consumable,
                "occasion": self.occasion,
                "scope": self.scope,
                "speed": self.speed,
                "success_rate": self.success_rate,
                "tp_gain": self.tp_gain,
                "hit_type": self.hit_type,
                "animation_id": self.animation_id,
                "effects": [e.to_dict() for e in self.effects],
            }
        )
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Item":
        """Create Item from dictionary."""
        effects = [Effect.from_dict(e) for e in data.get("effects", [])]
        return cls(
            id=data.get("id", 0),
            name=data.get("name", ""),
            icon_index=data.get("icon_index", 0),
            description=data.get("description", ""),
            note=data.get("note", ""),
            item_type=ItemType(data.get("item_type", "regular")),
            price=data.get("price", 0),
            consumable=data.get("consumable", True),
            occasion=data.get("occasion", 0),
            scope=data.get("scope", 1),
            speed=data.get("speed", 0),
            success_rate=data.get("success_rate", 100),
            tp_gain=data.get("tp_gain", 0),
            hit_type=data.get("hit_type", 0),
            animation_id=data.get("animation_id", 0),
            effects=effects,
        )

    def validate(self) -> bool:
        """Validate item data."""
        if not super().validate():
            return False
        if not 0 <= self.price <= 999999:
            return False
        if not 0 <= self.success_rate <= 100:
            return False
        if not 0 <= self.tp_gain <= 100:
            return False
        if not -9999 <= self.speed <= 9999:
            return False
        # Validate all effects
        for effect in self.effects:
            if not effect.validate():
                return False
        return True


# =============================================================================
# Skill Class
# =============================================================================


@dataclass
class Skill(DatabaseEntry):
    """
    A skill that can be used in battle or from the menu.

    Constraints:
    - mp_cost: 0-9999
    - tp_cost: 0-100
    - damage_type, element_type affect damage calculation
    """

    skill_type: SkillType = SkillType.MAGIC
    mp_cost: int = 0
    tp_cost: int = 0
    occasion: int = 1  # 0=always, 1=battle, 2=menu, 3=never
    scope: int = 1  # 0=none, 1=one enemy, 2=all enemies, 3=one ally, etc.
    speed: int = 0  # Speed correction
    success_rate: int = 100  # Success rate (0-100%)
    tp_gain: int = 0  # TP gained when used
    hit_type: int = 0  # 0=certain, 1=physical, 2=magical
    damage_type: DamageType = DamageType.NONE
    element_type: ElementType = ElementType.NORMAL
    animation_id: int = 0
    message1: str = ""  # Message when used (e.g., "%1 casts %2!")
    message2: str = ""  # Message when target is affected
    required_weapon_type1: Optional[WeaponType] = None
    required_weapon_type2: Optional[WeaponType] = None
    effects: List[Effect] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        base = super().to_dict()
        base.update(
            {
                "skill_type": self.skill_type.value,
                "mp_cost": self.mp_cost,
                "tp_cost": self.tp_cost,
                "occasion": self.occasion,
                "scope": self.scope,
                "speed": self.speed,
                "success_rate": self.success_rate,
                "tp_gain": self.tp_gain,
                "hit_type": self.hit_type,
                "damage_type": self.damage_type.value,
                "element_type": self.element_type.value,
                "animation_id": self.animation_id,
                "message1": self.message1,
                "message2": self.message2,
                "required_weapon_type1": (
                    self.required_weapon_type1.value
                    if self.required_weapon_type1
                    else None
                ),
                "required_weapon_type2": (
                    self.required_weapon_type2.value
                    if self.required_weapon_type2
                    else None
                ),
                "effects": [e.to_dict() for e in self.effects],
            }
        )
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Skill":
        """Create Skill from dictionary."""
        effects = [Effect.from_dict(e) for e in data.get("effects", [])]
        req_wep1 = data.get("required_weapon_type1")
        req_wep2 = data.get("required_weapon_type2")

        return cls(
            id=data.get("id", 0),
            name=data.get("name", ""),
            icon_index=data.get("icon_index", 0),
            description=data.get("description", ""),
            note=data.get("note", ""),
            skill_type=SkillType(data.get("skill_type", "magic")),
            mp_cost=data.get("mp_cost", 0),
            tp_cost=data.get("tp_cost", 0),
            occasion=data.get("occasion", 1),
            scope=data.get("scope", 1),
            speed=data.get("speed", 0),
            success_rate=data.get("success_rate", 100),
            tp_gain=data.get("tp_gain", 0),
            hit_type=data.get("hit_type", 0),
            damage_type=DamageType(data.get("damage_type", "none")),
            element_type=ElementType(data.get("element_type", "normal")),
            animation_id=data.get("animation_id", 0),
            message1=data.get("message1", ""),
            message2=data.get("message2", ""),
            required_weapon_type1=WeaponType(req_wep1) if req_wep1 else None,
            required_weapon_type2=WeaponType(req_wep2) if req_wep2 else None,
            effects=effects,
        )

    def validate(self) -> bool:
        """Validate skill data."""
        if not super().validate():
            return False
        if not 0 <= self.mp_cost <= 9999:
            return False
        if not 0 <= self.tp_cost <= 100:
            return False
        if not 0 <= self.success_rate <= 100:
            return False
        if not 0 <= self.tp_gain <= 100:
            return False
        if not -9999 <= self.speed <= 9999:
            return False
        for effect in self.effects:
            if not effect.validate():
                return False
        return True


# =============================================================================
# Weapon Class
# =============================================================================


@dataclass
class Weapon(DatabaseEntry):
    """
    Equippable weapon.

    Constraints:
    - All stats: -9999 to 9999 (can be negative for penalties)
    - price: 0-999999
    - params: [ATK, DEF, MAT, MDF, AGI, LUK] bonuses/penalties
    """

    weapon_type: WeaponType = WeaponType.SWORD
    price: int = 0
    animation_id: int = 0  # Attack animation
    # Parameter bonuses/penalties: [ATK, DEF, MAT, MDF, AGI, LUK]
    params: List[int] = field(default_factory=lambda: [0, 0, 0, 0, 0, 0])
    # Trait system for additional effects
    traits: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        base = super().to_dict()
        base.update(
            {
                "weapon_type": self.weapon_type.value,
                "price": self.price,
                "animation_id": self.animation_id,
                "params": self.params.copy(),
                "traits": [t.copy() for t in self.traits],
            }
        )
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Weapon":
        """Create Weapon from dictionary."""
        return cls(
            id=data.get("id", 0),
            name=data.get("name", ""),
            icon_index=data.get("icon_index", 0),
            description=data.get("description", ""),
            note=data.get("note", ""),
            weapon_type=WeaponType(data.get("weapon_type", "sword")),
            price=data.get("price", 0),
            animation_id=data.get("animation_id", 0),
            params=data.get("params", [0, 0, 0, 0, 0, 0]),
            traits=data.get("traits", []),
        )

    def validate(self) -> bool:
        """Validate weapon data."""
        if not super().validate():
            return False
        if not 0 <= self.price <= 999999:
            return False
        if len(self.params) != 6:
            return False
        for param in self.params:
            if not -9999 <= param <= 9999:
                return False
        return True


# =============================================================================
# Armor Class
# =============================================================================


@dataclass
class Armor(DatabaseEntry):
    """
    Equippable armor piece.

    Constraints:
    - All stats: -9999 to 9999 (can be negative for penalties)
    - price: 0-999999
    - params: [ATK, DEF, MAT, MDF, AGI, LUK] bonuses/penalties
    """

    armor_type: ArmorType = ArmorType.BODY
    equip_type: EquipType = EquipType.BODY
    price: int = 0
    # Parameter bonuses/penalties: [ATK, DEF, MAT, MDF, AGI, LUK]
    params: List[int] = field(default_factory=lambda: [0, 0, 0, 0, 0, 0])
    # Trait system for additional effects
    traits: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        base = super().to_dict()
        base.update(
            {
                "armor_type": self.armor_type.value,
                "equip_type": self.equip_type.value,
                "price": self.price,
                "params": self.params.copy(),
                "traits": [t.copy() for t in self.traits],
            }
        )
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Armor":
        """Create Armor from dictionary."""
        return cls(
            id=data.get("id", 0),
            name=data.get("name", ""),
            icon_index=data.get("icon_index", 0),
            description=data.get("description", ""),
            note=data.get("note", ""),
            armor_type=ArmorType(data.get("armor_type", "body")),
            equip_type=EquipType(data.get("equip_type", "body")),
            price=data.get("price", 0),
            params=data.get("params", [0, 0, 0, 0, 0, 0]),
            traits=data.get("traits", []),
        )

    def validate(self) -> bool:
        """Validate armor data."""
        if not super().validate():
            return False
        if not 0 <= self.price <= 999999:
            return False
        if len(self.params) != 6:
            return False
        for param in self.params:
            if not -9999 <= param <= 9999:
                return False
        return True


# =============================================================================
# State Class
# =============================================================================


@dataclass
class State(DatabaseEntry):
    """
    Status effect/condition (e.g., poison, sleep, buff).

    Constraints:
    - priority: 0-100 (higher = more important)
    - duration: -1 for infinite, 0+ for turn count
    - rates: 0-200 (percent, 100 is normal)
    """

    restriction: StateRestriction = StateRestriction.NONE
    priority: int = 50  # Display priority (0-100)
    remove_at_battle_end: bool = True
    remove_by_restriction: bool = False
    remove_by_damage: bool = False
    remove_by_walking: bool = False
    duration_steps: int = 100  # Steps until removed (if remove_by_walking)
    min_turns: int = 1  # Minimum turns state lasts
    max_turns: int = 1  # Maximum turns state lasts
    auto_removal_timing: int = 0  # 0=none, 1=action end, 2=turn end
    chance_by_damage: int = 100  # % chance to remove when damaged (0-100)
    message1: str = ""  # Message when state is added
    message2: str = ""  # Message when state is removed
    message3: str = ""  # Message when state persists
    message4: str = ""  # Message when state blocks action
    # Traits that modify actor parameters
    traits: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        base = super().to_dict()
        base.update(
            {
                "restriction": self.restriction.value,
                "priority": self.priority,
                "remove_at_battle_end": self.remove_at_battle_end,
                "remove_by_restriction": self.remove_by_restriction,
                "remove_by_damage": self.remove_by_damage,
                "remove_by_walking": self.remove_by_walking,
                "duration_steps": self.duration_steps,
                "min_turns": self.min_turns,
                "max_turns": self.max_turns,
                "auto_removal_timing": self.auto_removal_timing,
                "chance_by_damage": self.chance_by_damage,
                "message1": self.message1,
                "message2": self.message2,
                "message3": self.message3,
                "message4": self.message4,
                "traits": [t.copy() for t in self.traits],
            }
        )
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "State":
        """Create State from dictionary."""
        return cls(
            id=data.get("id", 0),
            name=data.get("name", ""),
            icon_index=data.get("icon_index", 0),
            description=data.get("description", ""),
            note=data.get("note", ""),
            restriction=StateRestriction(data.get("restriction", "none")),
            priority=data.get("priority", 50),
            remove_at_battle_end=data.get("remove_at_battle_end", True),
            remove_by_restriction=data.get("remove_by_restriction", False),
            remove_by_damage=data.get("remove_by_damage", False),
            remove_by_walking=data.get("remove_by_walking", False),
            duration_steps=data.get("duration_steps", 100),
            min_turns=data.get("min_turns", 1),
            max_turns=data.get("max_turns", 1),
            auto_removal_timing=data.get("auto_removal_timing", 0),
            chance_by_damage=data.get("chance_by_damage", 100),
            message1=data.get("message1", ""),
            message2=data.get("message2", ""),
            message3=data.get("message3", ""),
            message4=data.get("message4", ""),
            traits=data.get("traits", []),
        )

    def validate(self) -> bool:
        """Validate state data."""
        if not super().validate():
            return False
        if not 0 <= self.priority <= 100:
            return False
        if not 0 <= self.chance_by_damage <= 100:
            return False
        if self.min_turns < 0 or self.max_turns < 0:
            return False
        if self.min_turns > self.max_turns:
            return False
        return True


# =============================================================================
# Enemy Drop System
# =============================================================================


@dataclass
class DropItem:
    """
    Represents a potential item drop from an enemy.

    Constraints:
    - item_id: 1-9999
    - drop_rate: 0.0-1.0
    - kind: 1=item, 2=weapon, 3=armor
    """

    kind: int = 1  # 1=item, 2=weapon, 3=armor
    item_id: int = 0
    drop_rate: float = 1.0  # Probability (0.0-1.0)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "kind": self.kind,
            "item_id": self.item_id,
            "drop_rate": self.drop_rate,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DropItem":
        """Create DropItem from dictionary."""
        return cls(
            kind=data.get("kind", 1),
            item_id=data.get("item_id", 0),
            drop_rate=float(data.get("drop_rate", 1.0)),
        )

    def validate(self) -> bool:
        """Validate drop item data."""
        if self.kind not in [1, 2, 3]:
            return False
        if not 0 <= self.item_id <= 9999:
            return False
        if not 0.0 <= self.drop_rate <= 1.0:
            return False
        return True


# =============================================================================
# Enemy Class
# =============================================================================


@dataclass
class Enemy(DatabaseEntry):
    """
    Enemy/monster definition.

    Constraints:
    - All stats: 0-9999
    - exp: 0-9999999
    - gold: 0-999999
    - drop_items: Up to 3 drops recommended
    """

    battler_name: str = ""  # Graphic filename
    battler_hue: int = 0  # Color hue (0-360)
    # Base parameters: [HP, MP, ATK, DEF, MAT, MDF, AGI, LUK]
    params: List[int] = field(default_factory=lambda: [100, 0, 10, 10, 10, 10, 10, 10])
    exp: int = 0  # Experience gained when defeated
    gold: int = 0  # Gold gained when defeated
    drop_items: List[DropItem] = field(default_factory=list)
    # Actions (AI patterns)
    actions: List[Dict[str, Any]] = field(default_factory=list)
    # Traits (element rates, state rates, etc.)
    traits: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        base = super().to_dict()
        base.update(
            {
                "battler_name": self.battler_name,
                "battler_hue": self.battler_hue,
                "params": self.params.copy(),
                "exp": self.exp,
                "gold": self.gold,
                "drop_items": [d.to_dict() for d in self.drop_items],
                "actions": [a.copy() for a in self.actions],
                "traits": [t.copy() for t in self.traits],
            }
        )
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Enemy":
        """Create Enemy from dictionary."""
        drop_items = [DropItem.from_dict(d) for d in data.get("drop_items", [])]
        return cls(
            id=data.get("id", 0),
            name=data.get("name", ""),
            icon_index=data.get("icon_index", 0),
            description=data.get("description", ""),
            note=data.get("note", ""),
            battler_name=data.get("battler_name", ""),
            battler_hue=data.get("battler_hue", 0),
            params=data.get("params", [100, 0, 10, 10, 10, 10, 10, 10]),
            exp=data.get("exp", 0),
            gold=data.get("gold", 0),
            drop_items=drop_items,
            actions=data.get("actions", []),
            traits=data.get("traits", []),
        )

    def validate(self) -> bool:
        """Validate enemy data."""
        if not super().validate():
            return False
        if len(self.params) != 8:
            return False
        for param in self.params:
            if not 0 <= param <= 9999:
                return False
        if not 0 <= self.exp <= 9999999:
            return False
        if not 0 <= self.gold <= 999999:
            return False
        if not 0 <= self.battler_hue <= 360:
            return False
        for drop in self.drop_items:
            if not drop.validate():
                return False
        return True


# =============================================================================
# Actor Class
# =============================================================================


@dataclass
class Actor(DatabaseEntry):
    """
    Playable character/actor.

    Constraints:
    - All stats: 0-9999
    - level: 1-99
    - class_id: 1-9999
    - initial_level: 1-99
    - max_level: 1-99
    """

    nickname: str = ""  # Short name/title
    class_id: int = 1  # Reference to Class
    initial_level: int = 1
    max_level: int = 99
    character_name: str = ""  # Sprite filename
    character_index: int = 0  # Index in sprite sheet
    face_name: str = ""  # Face graphic filename
    face_index: int = 0  # Index in face sheet
    # Equipment slots
    equips: List[int] = field(
        default_factory=lambda: [0, 0, 0, 0, 0]
    )  # Initial equipment IDs
    # Traits
    traits: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        base = super().to_dict()
        base.update(
            {
                "nickname": self.nickname,
                "class_id": self.class_id,
                "initial_level": self.initial_level,
                "max_level": self.max_level,
                "character_name": self.character_name,
                "character_index": self.character_index,
                "face_name": self.face_name,
                "face_index": self.face_index,
                "equips": self.equips.copy(),
                "traits": [t.copy() for t in self.traits],
            }
        )
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Actor":
        """Create Actor from dictionary."""
        return cls(
            id=data.get("id", 0),
            name=data.get("name", ""),
            icon_index=data.get("icon_index", 0),
            description=data.get("description", ""),
            note=data.get("note", ""),
            nickname=data.get("nickname", ""),
            class_id=data.get("class_id", 1),
            initial_level=data.get("initial_level", 1),
            max_level=data.get("max_level", 99),
            character_name=data.get("character_name", ""),
            character_index=data.get("character_index", 0),
            face_name=data.get("face_name", ""),
            face_index=data.get("face_index", 0),
            equips=data.get("equips", [0, 0, 0, 0, 0]),
            traits=data.get("traits", []),
        )

    def validate(self) -> bool:
        """Validate actor data."""
        if not super().validate():
            return False
        if not 1 <= self.initial_level <= 99:
            return False
        if not 1 <= self.max_level <= 99:
            return False
        if self.initial_level > self.max_level:
            return False
        if not 1 <= self.class_id <= 9999:
            return False
        return True


# =============================================================================
# Class
# =============================================================================


@dataclass
class Class(DatabaseEntry):
    """
    Character class (e.g., Warrior, Mage).

    Defines stat growth curves and learnable skills.

    Constraints:
    - All stats: 0-9999
    - exp_basis/extra: Controls exp curve
    - params: Growth curves for 8 parameters across 99 levels
    """

    exp_params: List[int] = field(
        default_factory=lambda: [30, 20, 30, 30]
    )  # [basis, extra, accel_a, accel_b]
    # Parameter curves: [[HP curve], [MP curve], [ATK curve], ...]
    # Each curve has 99 values (level 1-99)
    params: List[List[int]] = field(default_factory=list)
    # Skills learned: [{"level": 1, "skill_id": 1}, ...]
    learnings: List[Dict[str, int]] = field(default_factory=list)
    # Traits (equipment types, etc.)
    traits: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        base = super().to_dict()
        base.update(
            {
                "exp_params": self.exp_params.copy(),
                "params": [curve.copy() for curve in self.params],
                "learnings": [l.copy() for l in self.learnings],
                "traits": [t.copy() for t in self.traits],
            }
        )
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Class":
        """Create Class from dictionary."""
        return cls(
            id=data.get("id", 0),
            name=data.get("name", ""),
            icon_index=data.get("icon_index", 0),
            description=data.get("description", ""),
            note=data.get("note", ""),
            exp_params=data.get("exp_params", [30, 20, 30, 30]),
            params=data.get("params", []),
            learnings=data.get("learnings", []),
            traits=data.get("traits", []),
        )

    def validate(self) -> bool:
        """Validate class data."""
        if not super().validate():
            return False
        if len(self.exp_params) != 4:
            return False
        # If params are provided, validate structure
        if self.params:
            if len(self.params) != 8:  # 8 parameters
                return False
            for curve in self.params:
                if len(curve) != 99:  # 99 levels
                    return False
                for value in curve:
                    if not 0 <= value <= 9999:
                        return False
        return True


# =============================================================================
# Animation Class
# =============================================================================


@dataclass
class Animation(DatabaseEntry):
    """
    Battle animation.

    Constraints:
    - frame_max: 1-999 frames
    - position: 0=head, 1=center, 2=feet, 3=screen
    - frames: List of frame data
    """

    animation1_name: str = ""  # First animation graphic
    animation1_hue: int = 0  # Hue for first graphic (0-360)
    animation2_name: str = ""  # Second animation graphic
    animation2_hue: int = 0  # Hue for second graphic (0-360)
    position: int = 1  # 0=head, 1=center, 2=feet, 3=screen
    frame_max: int = 1  # Number of frames
    # Frame data: Each frame contains cell data, SE, and flash timing
    frames: List[Dict[str, Any]] = field(default_factory=list)
    # Timings for SE and flashes
    timings: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        base = super().to_dict()
        base.update(
            {
                "animation1_name": self.animation1_name,
                "animation1_hue": self.animation1_hue,
                "animation2_name": self.animation2_name,
                "animation2_hue": self.animation2_hue,
                "position": self.position,
                "frame_max": self.frame_max,
                "frames": [f.copy() for f in self.frames],
                "timings": [t.copy() for t in self.timings],
            }
        )
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Animation":
        """Create Animation from dictionary."""
        return cls(
            id=data.get("id", 0),
            name=data.get("name", ""),
            icon_index=data.get("icon_index", 0),
            description=data.get("description", ""),
            note=data.get("note", ""),
            animation1_name=data.get("animation1_name", ""),
            animation1_hue=data.get("animation1_hue", 0),
            animation2_name=data.get("animation2_name", ""),
            animation2_hue=data.get("animation2_hue", 0),
            position=data.get("position", 1),
            frame_max=data.get("frame_max", 1),
            frames=data.get("frames", []),
            timings=data.get("timings", []),
        )

    def validate(self) -> bool:
        """Validate animation data."""
        if not super().validate():
            return False
        if not 1 <= self.frame_max <= 999:
            return False
        if not 0 <= self.position <= 3:
            return False
        if not 0 <= self.animation1_hue <= 360:
            return False
        if not 0 <= self.animation2_hue <= 360:
            return False
        return True


# =============================================================================
# Database Manager
# =============================================================================


class DatabaseManager:
    """
    Manages all database entries with loading, saving, and validation.

    Provides centralized access to all game data.
    """

    def __init__(self):
        self.items: Dict[int, Item] = {}
        self.skills: Dict[int, Skill] = {}
        self.weapons: Dict[int, Weapon] = {}
        self.armors: Dict[int, Armor] = {}
        self.enemies: Dict[int, Enemy] = {}
        self.states: Dict[int, State] = {}
        self.actors: Dict[int, Actor] = {}
        self.classes: Dict[int, Class] = {}
        self.animations: Dict[int, Animation] = {}

    def save_to_file(self, filepath: Path):
        """Save all database entries to a JSON file."""
        data = {
            "items": [item.to_dict() for item in self.items.values()],
            "skills": [skill.to_dict() for skill in self.skills.values()],
            "weapons": [weapon.to_dict() for weapon in self.weapons.values()],
            "armors": [armor.to_dict() for armor in self.armors.values()],
            "enemies": [enemy.to_dict() for enemy in self.enemies.values()],
            "states": [state.to_dict() for state in self.states.values()],
            "actors": [actor.to_dict() for actor in self.actors.values()],
            "classes": [cls.to_dict() for cls in self.classes.values()],
            "animations": [anim.to_dict() for anim in self.animations.values()],
        }

        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_from_file(self, filepath: Path) -> bool:
        """
        Load all database entries from a JSON file.

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.items = {
                item["id"]: Item.from_dict(item) for item in data.get("items", [])
            }
            self.skills = {
                skill["id"]: Skill.from_dict(skill)
                for skill in data.get("skills", [])
            }
            self.weapons = {
                weapon["id"]: Weapon.from_dict(weapon)
                for weapon in data.get("weapons", [])
            }
            self.armors = {
                armor["id"]: Armor.from_dict(armor)
                for armor in data.get("armors", [])
            }
            self.enemies = {
                enemy["id"]: Enemy.from_dict(enemy)
                for enemy in data.get("enemies", [])
            }
            self.states = {
                state["id"]: State.from_dict(state)
                for state in data.get("states", [])
            }
            self.actors = {
                actor["id"]: Actor.from_dict(actor)
                for actor in data.get("actors", [])
            }
            self.classes = {
                cls["id"]: Class.from_dict(cls) for cls in data.get("classes", [])
            }
            self.animations = {
                anim["id"]: Animation.from_dict(anim)
                for anim in data.get("animations", [])
            }

            return True

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading database from {filepath}: {e}")
            return False

    def validate_all(self) -> Dict[str, List[str]]:
        """
        Validate all database entries.

        Returns:
            Dictionary mapping entry type to list of validation errors
        """
        errors: Dict[str, List[str]] = {}

        for item in self.items.values():
            if not item.validate():
                errors.setdefault("items", []).append(
                    f"Item {item.id} ({item.name}) failed validation"
                )

        for skill in self.skills.values():
            if not skill.validate():
                errors.setdefault("skills", []).append(
                    f"Skill {skill.id} ({skill.name}) failed validation"
                )

        for weapon in self.weapons.values():
            if not weapon.validate():
                errors.setdefault("weapons", []).append(
                    f"Weapon {weapon.id} ({weapon.name}) failed validation"
                )

        for armor in self.armors.values():
            if not armor.validate():
                errors.setdefault("armors", []).append(
                    f"Armor {armor.id} ({armor.name}) failed validation"
                )

        for enemy in self.enemies.values():
            if not enemy.validate():
                errors.setdefault("enemies", []).append(
                    f"Enemy {enemy.id} ({enemy.name}) failed validation"
                )

        for state in self.states.values():
            if not state.validate():
                errors.setdefault("states", []).append(
                    f"State {state.id} ({state.name}) failed validation"
                )

        for actor in self.actors.values():
            if not actor.validate():
                errors.setdefault("actors", []).append(
                    f"Actor {actor.id} ({actor.name}) failed validation"
                )

        for cls in self.classes.values():
            if not cls.validate():
                errors.setdefault("classes", []).append(
                    f"Class {cls.id} ({cls.name}) failed validation"
                )

        for anim in self.animations.values():
            if not anim.validate():
                errors.setdefault("animations", []).append(
                    f"Animation {anim.id} ({anim.name}) failed validation"
                )

        return errors

    def clear(self):
        """Clear all database entries."""
        self.items.clear()
        self.skills.clear()
        self.weapons.clear()
        self.armors.clear()
        self.enemies.clear()
        self.states.clear()
        self.actors.clear()
        self.classes.clear()
        self.animations.clear()
