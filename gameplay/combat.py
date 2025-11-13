"""
Combat System

ECS-based combat components and systems for turn-based and real-time combat.
Provides health, damage, stats, weapons, and action points.
"""

from typing import Optional, Tuple, Callable, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
from engine.core.ecs import Component, System, World, Entity


class DamageType(Enum):
    """Types of damage"""

    PHYSICAL = "physical"
    ENERGY = "energy"
    TECH = "tech"
    ENVIRONMENTAL = "environmental"


class Team(Enum):
    """Team affiliations for targeting"""

    PLAYER = "player"
    ENEMY = "enemy"
    NEUTRAL = "neutral"
    ALLY = "ally"


@dataclass
class Health(Component):
    """
    Health component for entities that can take damage.

    Tracks HP, armor, and alive state.
    """

    max_hp: float = 100.0
    hp: float = 100.0
    armor: float = 0.0  # Damage reduction percentage (0-100)
    regeneration_rate: float = 0.0  # HP per second

    # State
    is_alive: bool = True
    is_invulnerable: bool = False  # Temporary invincibility

    # Callbacks
    on_damage: Optional[Callable[[float, "DamageType"], None]] = None
    on_death: Optional[Callable[[], None]] = None
    on_heal: Optional[Callable[[float], None]] = None

    def __post_init__(self):
        """Initialize HP if not set"""
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def get_hp_percentage(self) -> float:
        """Get HP as percentage (0-100)"""
        if self.max_hp <= 0:
            return 0.0
        return (self.hp / self.max_hp) * 100.0

    def is_full_health(self) -> bool:
        """Check if at full health"""
        return self.hp >= self.max_hp

    def is_critical(self) -> bool:
        """Check if HP is critically low (<25%)"""
        return self.get_hp_percentage() < 25.0


@dataclass
class CombatStats(Component):
    """
    Combat statistics for entities.

    Based on Cyberpunk-style attribute system.
    """

    # Core attributes (1-10 typical range)
    body: int = 5  # Physical strength and toughness
    reflexes: int = 5  # Speed and agility
    intelligence: int = 5  # Mental acuity
    tech: int = 5  # Technical skill
    cool: int = 5  # Composure under pressure

    # Derived stats
    morale: float = 100.0  # Combat effectiveness (0-100)

    def get_initiative_bonus(self) -> int:
        """Calculate initiative bonus from reflexes"""
        return self.reflexes * 2

    def get_dodge_chance(self) -> float:
        """Calculate dodge chance (0-100)"""
        return min(20.0, self.reflexes * 3.0)

    def get_crit_chance(self) -> float:
        """Calculate critical hit chance (0-100)"""
        return self.cool * 2.0

    def get_morale_modifier(self) -> float:
        """Calculate damage modifier from morale (0.5-1.5)"""
        return 1.0 + ((self.morale - 50) / 200)

    def get_melee_damage_bonus(self) -> float:
        """Get melee damage bonus from body"""
        return self.body * 3.0

    def get_ranged_damage_bonus(self) -> float:
        """Get ranged damage bonus from reflexes"""
        return self.reflexes * 2.0


@dataclass
class Weapon(Component):
    """
    Weapon component for combat entities.

    Defines weapon properties and damage calculations.
    """

    name: str = "Unarmed"
    damage: float = 10.0
    damage_type: DamageType = DamageType.PHYSICAL
    accuracy: float = 75.0  # Base hit chance (0-100)
    range: float = 1.0  # Attack range in tiles/units
    crit_multiplier: float = 2.0
    armor_penetration: float = 0.0  # Armor bypass percentage (0-1)

    # Weapon type affects stat bonuses
    is_melee: bool = False
    is_ranged: bool = True

    # Damage variance
    damage_variance_min: float = 0.85
    damage_variance_max: float = 1.15

    # Ammunition (optional)
    has_ammo: bool = False
    ammo: int = 0
    max_ammo: int = 0


@dataclass
class ActionPoints(Component):
    """
    Action Points for turn-based combat.

    Tracks available actions per turn.
    """

    max_ap: int = 3
    ap: int = 3

    # AP costs
    ap_cost_move: int = 1
    ap_cost_attack: int = 1
    ap_cost_ability: int = 2

    # State
    has_acted_this_turn: bool = False

    def can_afford(self, cost: int) -> bool:
        """Check if entity can afford action"""
        return self.ap >= cost

    def spend(self, cost: int) -> bool:
        """Spend AP, returns True if successful"""
        if self.can_afford(cost):
            self.ap -= cost
            self.has_acted_this_turn = True
            return True
        return False

    def refund(self, amount: int):
        """Refund AP (up to max)"""
        self.ap = min(self.max_ap, self.ap + amount)

    def reset(self):
        """Reset AP to max (start of turn)"""
        self.ap = self.max_ap
        self.has_acted_this_turn = False


@dataclass
class TeamComponent(Component):
    """
    Team affiliation for targeting and AI.
    """

    team: Team = Team.NEUTRAL
    is_hostile_to_player: bool = False
    is_friendly_fire_enabled: bool = False

    def is_enemy_of(self, other: "TeamComponent") -> bool:
        """Check if this entity is enemy of another"""
        # Same team with friendly fire enabled = enemies
        if self.team == other.team and self.is_friendly_fire_enabled:
            return True

        # Same team without friendly fire = not enemies
        if self.team == other.team:
            return False

        # Player vs Enemy
        if self.team == Team.PLAYER and other.team == Team.ENEMY:
            return True
        if self.team == Team.ENEMY and other.team == Team.PLAYER:
            return True

        # Hostile neutrals
        return self.is_hostile_to_player and other.team == Team.PLAYER


@dataclass
class DamageInstance:
    """Represents a single damage event"""

    amount: float
    damage_type: DamageType
    source: Optional[Entity] = None
    is_critical: bool = False
    armor_penetration: float = 0.0


class HealthSystem(System):
    """
    System that manages health, damage, and death.

    Handles:
    - Applying damage with armor calculation
    - Health regeneration
    - Death detection
    - Damage callbacks
    """

    def __init__(self):
        super().__init__()
        self.priority = 10  # Run after combat calculations

    def update(self, world: World, delta_time: float):
        """Update health for all entities"""
        for entity in world.get_entities_with_component(Health):
            health = entity.get_component(Health)

            if not health.is_alive:
                continue

            # Apply regeneration
            if health.regeneration_rate > 0 and health.hp < health.max_hp:
                heal_amount = health.regeneration_rate * delta_time
                self.heal(entity, heal_amount)

            # Check for death
            if health.hp <= 0 and health.is_alive:
                self.kill(entity)

    def apply_damage(self, entity: Entity, damage_instance: DamageInstance) -> float:
        """
        Apply damage to entity.

        Args:
            entity: Target entity
            damage_instance: Damage information

        Returns:
            Actual damage dealt after armor/modifiers
        """
        health = entity.get_component(Health)
        if not health or not health.is_alive or health.is_invulnerable:
            return 0.0

        # Calculate armor reduction
        effective_armor = health.armor * (1.0 - damage_instance.armor_penetration)
        armor_multiplier = 1.0 - (effective_armor / 100.0)

        # Apply damage
        final_damage = damage_instance.amount * armor_multiplier
        final_damage = max(1.0, final_damage)  # Minimum 1 damage

        health.hp -= final_damage

        # Morale loss for high damage (if has CombatStats)
        stats = entity.get_component(CombatStats)
        if stats:
            damage_percent = (final_damage / health.max_hp) * 100
            if damage_percent >= 30:
                stats.morale = max(0, stats.morale - 20)
            elif damage_percent >= 15:
                stats.morale = max(0, stats.morale - 10)

        # Trigger callback
        if health.on_damage:
            health.on_damage(final_damage, damage_instance.damage_type)

        # Check for death
        if health.hp <= 0:
            self.kill(entity)

        return final_damage

    def heal(self, entity: Entity, amount: float) -> float:
        """
        Heal entity.

        Args:
            entity: Target entity
            amount: Healing amount

        Returns:
            Actual amount healed
        """
        health = entity.get_component(Health)
        if not health or not health.is_alive:
            return 0.0

        old_hp = health.hp
        health.hp = min(health.max_hp, health.hp + amount)
        actual_heal = health.hp - old_hp

        # Trigger callback
        if actual_heal > 0 and health.on_heal:
            health.on_heal(actual_heal)

        return actual_heal

    def kill(self, entity: Entity):
        """Kill entity"""
        health = entity.get_component(Health)
        if not health:
            return

        health.hp = 0
        health.is_alive = False

        # Trigger callback
        if health.on_death:
            health.on_death()

    def revive(self, entity: Entity, hp: Optional[float] = None):
        """Revive entity"""
        health = entity.get_component(Health)
        if not health:
            return

        health.is_alive = True
        health.hp = hp if hp is not None else health.max_hp


class CombatSystem(System):
    """
    System that handles combat calculations.

    Provides methods for:
    - Hit chance calculation
    - Damage calculation
    - Attack resolution
    - Range checking
    """

    def __init__(self, health_system: Optional[HealthSystem] = None):
        super().__init__()
        self.priority = 9  # Run before health system
        self.health_system = health_system

        # Combat log (optional)
        self.combat_log: list[str] = []
        self.max_log_size = 50

    def update(self, world: World, delta_time: float):
        """Combat system is primarily event-driven, minimal per-frame updates"""
        pass

    def calculate_hit_chance(self, attacker: Entity, target: Entity) -> float:
        """
        Calculate hit chance percentage.

        Formula: BaseAccuracy - DodgeChance, clamped to 5-95%
        """
        weapon = attacker.get_component(Weapon)
        target_stats = target.get_component(CombatStats)

        if not weapon:
            return 50.0  # Default

        base_accuracy = weapon.accuracy

        # Apply dodge
        if target_stats:
            dodge = target_stats.get_dodge_chance()
            base_accuracy -= dodge

        # Clamp to 5-95%
        return max(5.0, min(95.0, base_accuracy))

    def calculate_damage(self, attacker: Entity, target: Entity) -> Tuple[float, bool]:
        """
        Calculate damage dealt.

        Returns:
            (damage, is_critical)
        """
        import random

        weapon = attacker.get_component(Weapon)
        attacker_stats = attacker.get_component(CombatStats)

        if not weapon:
            return (10.0, False)  # Default punch

        # Base damage with variance
        variance = random.uniform(
            weapon.damage_variance_min, weapon.damage_variance_max
        )
        base_damage = weapon.damage * variance

        # Stat bonus
        stat_bonus = 0.0
        if attacker_stats:
            if weapon.is_melee:
                stat_bonus = attacker_stats.get_melee_damage_bonus()
            else:
                stat_bonus = attacker_stats.get_ranged_damage_bonus()

        # Critical hit
        is_crit = False
        crit_multiplier = 1.0
        if attacker_stats:
            crit_chance = attacker_stats.get_crit_chance()
            crit_roll = random.randint(1, 100)
            if crit_roll <= crit_chance:
                is_crit = True
                crit_multiplier = weapon.crit_multiplier

        # Morale modifier
        morale_modifier = 1.0
        if attacker_stats:
            morale_modifier = attacker_stats.get_morale_modifier()

        # Calculate total
        total_damage = (base_damage + stat_bonus) * crit_multiplier * morale_modifier

        return (total_damage, is_crit)

    def perform_attack(self, attacker: Entity, target: Entity) -> Dict[str, Any]:
        """
        Perform a complete attack action.

        Returns:
            Dictionary with attack results:
            {
                'hit': bool,
                'damage': float,
                'is_critical': bool,
                'message': str
            }
        """
        import random

        weapon = attacker.get_component(Weapon)
        target_health = target.get_component(Health)

        if not weapon or not target_health:
            return {
                "hit": False,
                "damage": 0,
                "is_critical": False,
                "message": "Invalid attack",
            }

        # Check if target is alive
        if not target_health.is_alive:
            return {
                "hit": False,
                "damage": 0,
                "is_critical": False,
                "message": "Target already dead",
            }

        # Check ammo
        if weapon.has_ammo and weapon.ammo <= 0:
            return {
                "hit": False,
                "damage": 0,
                "is_critical": False,
                "message": "Out of ammo",
            }

        # Spend ammo
        if weapon.has_ammo:
            weapon.ammo -= 1

        # Roll to hit
        hit_chance = self.calculate_hit_chance(attacker, target)
        roll = random.uniform(0, 100)

        if roll > hit_chance:
            # Miss
            return {
                "hit": False,
                "damage": 0,
                "is_critical": False,
                "message": f"Miss! (Needed {hit_chance:.0f}%, rolled {roll:.0f}%)",
            }

        # Hit! Calculate damage
        damage, is_crit = self.calculate_damage(attacker, target)

        # Apply damage
        damage_instance = DamageInstance(
            amount=damage,
            damage_type=weapon.damage_type,
            source=attacker,
            is_critical=is_crit,
            armor_penetration=weapon.armor_penetration,
        )

        actual_damage = 0.0
        if self.health_system:
            actual_damage = self.health_system.apply_damage(target, damage_instance)
        else:
            # Apply damage directly if no health system
            actual_damage = damage * (1.0 - (target_health.armor / 100.0))
            actual_damage = max(1.0, actual_damage)
            target_health.hp -= actual_damage
            if target_health.hp <= 0:
                target_health.hp = 0
                target_health.is_alive = False

        crit_text = " CRITICAL!" if is_crit else ""
        message = f"Hit for {actual_damage:.0f} damage{crit_text}!"

        self.add_log(message)

        return {
            "hit": True,
            "damage": actual_damage,
            "is_critical": is_crit,
            "message": message,
        }

    def check_range(
        self, attacker: Entity, target: Entity, world: World
    ) -> Tuple[bool, float]:
        """
        Check if target is in range.

        Returns:
            (in_range, distance)
        """
        from engine.core.ecs import Transform, GridPosition

        weapon = attacker.get_component(Weapon)
        if not weapon:
            return (False, float("inf"))

        # Try GridPosition first (for grid-based games)
        attacker_grid = attacker.get_component(GridPosition)
        target_grid = target.get_component(GridPosition)

        if attacker_grid and target_grid:
            # Manhattan distance for grid
            distance = abs(attacker_grid.grid_x - target_grid.grid_x) + abs(
                attacker_grid.grid_y - target_grid.grid_y
            )
        else:
            # Euclidean distance for continuous space
            attacker_transform = attacker.get_component(Transform)
            target_transform = target.get_component(Transform)

            if not attacker_transform or not target_transform:
                return (False, float("inf"))

            dx = target_transform.x - attacker_transform.x
            dy = target_transform.y - attacker_transform.y
            distance = (dx * dx + dy * dy) ** 0.5

        in_range = distance <= weapon.range
        return (in_range, distance)

    def add_log(self, message: str):
        """Add message to combat log"""
        self.combat_log.append(message)
        if len(self.combat_log) > self.max_log_size:
            self.combat_log.pop(0)

    def get_log(self) -> list[str]:
        """Get combat log"""
        return self.combat_log.copy()

    def clear_log(self):
        """Clear combat log"""
        self.combat_log.clear()
