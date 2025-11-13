"""
Neon Collapse - Character & Enemy Classes
Implements attribute system from Combat TDD v3.0
"""

import random
from config import (
    MAX_ACTION_POINTS,
    DODGE_CAP,
    BASE_MOVEMENT_RANGE,
    COVER_HALF,
    COVER_FULL,
    WEAPONS,
    DAMAGE_VARIANCE_MIN,
    DAMAGE_VARIANCE_MAX,
    ARMOR_REDUCTION_MULTIPLIER,
    AP_BASIC_ATTACK,
    AP_MOVE
)


class Character:
    """Base character class with combat attributes from TDD"""

    def __init__(self, name, x, y, stats, weapon, team='player'):
        self.name = name
        self.x = x
        self.y = y
        self.team = team  # 'player' or 'enemy'

        # Attributes (from TDD)
        self.body = stats['body']
        self.reflexes = stats['reflexes']
        self.intelligence = stats['intelligence']
        self.tech = stats['tech']
        self.cool = stats['cool']

        # Combat Stats
        self.max_hp = stats['max_hp']
        self.hp = self.max_hp
        self.armor = stats.get('armor', 15)  # Default 15% armor
        self.morale = 100  # Start at max morale

        # Action Points
        self.max_ap = MAX_ACTION_POINTS
        self.ap = self.max_ap

        # Weapon
        self.weapon = WEAPONS[weapon].copy()

        # Combat State
        self.is_alive = True
        self.has_acted = False
        self.in_cover = False
        self.cover_type = None  # 'half' or 'full'

        # Movement
        self.movement_range = BASE_MOVEMENT_RANGE + (self.reflexes // 4)
        self.has_moved = False

    def get_initiative(self):
        """Calculate initiative: (Reflexes × 2) + random(1, 10)"""
        return (self.reflexes * 2) + random.randint(1, 10)

    def get_dodge_chance(self):
        """Calculate dodge chance: min(20, reflexes × 3)"""
        return min(DODGE_CAP, self.reflexes * 3)

    def get_crit_chance(self):
        """Calculate crit chance: cool × 2"""
        return self.cool * 2

    def get_morale_modifier(self):
        """Calculate morale damage modifier"""
        return 1.0 + ((self.morale - 50) / 200)

    def calculate_hit_chance(self, target):
        """
        Calculate hit chance based on TDD formula:
        BaseAccuracy = weapon.accuracy - DodgeChance
        FinalHitChance = clamp(BaseAccuracy + modifiers, 5%, 95%)
        """
        base_accuracy = self.weapon['accuracy']
        dodge_chance = target.get_dodge_chance()

        hit_chance = base_accuracy - dodge_chance

        # Cover modifiers
        if target.in_cover:
            if target.cover_type == 'half':
                hit_chance -= COVER_HALF
            elif target.cover_type == 'full':
                hit_chance -= COVER_FULL

        # Clamp to 5%-95%
        hit_chance = max(5, min(95, hit_chance))

        return hit_chance

    def calculate_damage(self, target):
        """
        Calculate damage based on TDD formula:
        1. Base damage with variance
        2. Stat bonus (Body for melee, Reflexes for ranged)
        3. Critical hit check
        4. Morale modifier
        5. Armor reduction
        6. Cover reduction
        """
        # Step 1: Base damage with variance
        base_dmg = self.weapon['damage'] * random.uniform(DAMAGE_VARIANCE_MIN, DAMAGE_VARIANCE_MAX)

        # Step 2: Stat bonus
        if self.weapon['type'] == 'melee':
            stat_bonus = self.body * 3
        else:
            stat_bonus = self.reflexes * 2

        # Step 3: Critical hit check
        crit_roll = random.randint(1, 100)
        crit_multiplier = 1.0
        is_crit = False
        if crit_roll <= self.get_crit_chance():
            crit_multiplier = self.weapon['crit_multiplier']
            is_crit = True

        # Step 4: Morale modifier
        morale_modifier = self.get_morale_modifier()

        # Calculate damage before defenses
        total_damage = (base_dmg + stat_bonus) * crit_multiplier * morale_modifier

        # Step 5: Armor reduction (full armor value applies)
        effective_armor = target.armor * (1 - self.weapon['armor_pen'])
        armor_reduction = effective_armor * ARMOR_REDUCTION_MULTIPLIER
        total_damage -= armor_reduction

        # Step 6: Cover reduction
        if target.in_cover and self.weapon['type'] != 'tech':
            if target.cover_type == 'half':
                total_damage *= 0.75  # 25% reduction
            elif target.cover_type == 'full':
                total_damage *= 0.60  # 40% reduction

        # Minimum 1 damage
        total_damage = max(1, int(total_damage))

        return total_damage, is_crit

    def attack(self, target):
        """Perform attack on target, returns damage dealt and combat log"""
        if self.ap < AP_BASIC_ATTACK:
            return None, "Not enough AP!"

        # Check range
        distance = abs(self.x - target.x) + abs(self.y - target.y)
        if distance > self.weapon['range']:
            return None, f"Target out of range! (Range: {self.weapon['range']}, Distance: {distance})"

        # Spend AP
        self.ap -= AP_BASIC_ATTACK

        # Hit chance roll
        hit_chance = self.calculate_hit_chance(target)
        roll = random.randint(1, 100)

        if roll <= hit_chance:
            # Hit! Calculate damage
            damage, is_crit = self.calculate_damage(target)
            target.take_damage(damage)

            crit_text = " CRITICAL!" if is_crit else ""
            log = f"{self.name} hits {target.name} for {damage} damage{crit_text}!"
            return damage, log
        else:
            # Miss
            log = f"{self.name} misses {target.name}! (Needed {hit_chance}%, rolled {roll}%)"
            return 0, log

    def take_damage(self, damage):
        """Take damage and update morale"""
        self.hp -= damage

        # Morale loss based on damage taken
        if damage >= self.max_hp * 0.3:  # 30%+ HP lost
            self.morale = max(0, self.morale - 20)
        elif damage >= self.max_hp * 0.15:  # 15%+ HP lost
            self.morale = max(0, self.morale - 10)

        if self.hp <= 0:
            self.hp = 0
            self.is_alive = False

    def move(self, new_x, new_y):
        """Move to new position if within range and has AP"""
        if self.ap < AP_MOVE:
            return False, "Not enough AP!"

        distance = abs(new_x - self.x) + abs(new_y - self.y)
        if distance > self.movement_range:
            return False, f"Too far! (Max movement: {self.movement_range})"

        self.x = new_x
        self.y = new_y
        self.ap -= AP_MOVE
        self.has_moved = True

        return True, f"{self.name} moved to ({new_x}, {new_y})"

    def start_turn(self):
        """Reset AP at start of turn"""
        self.ap = self.max_ap
        self.has_acted = False
        self.has_moved = False

    def end_turn(self):
        """End turn"""
        self.has_acted = True

    def get_hp_percentage(self):
        """Get HP as percentage"""
        return (self.hp / self.max_hp) * 100

    def get_targets_in_range(self, all_characters):
        """Get all enemy targets within weapon range"""
        targets = []
        for char in all_characters:
            if char.team != self.team and char.is_alive:
                distance = abs(self.x - char.x) + abs(self.y - char.y)
                if distance <= self.weapon['range']:
                    targets.append(char)
        return targets

    def __repr__(self):
        return f"{self.name} ({self.hp}/{self.max_hp} HP, {self.ap}/{self.max_ap} AP)"
