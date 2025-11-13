"""
Neon Collapse - Multiple Encounters System
Manages combat encounters with scaling difficulty and loot
"""

from typing import Dict, List, Any, Optional
import random


# Constants
DIFFICULTY_TIERS = ["EASY", "MEDIUM", "HARD", "EXTREME"]
VALID_PHASES = [0, 1, 2, 3, 4]


# ============================================================================
# ENEMY CLASS
# ============================================================================

class Enemy:
    """Represents an enemy type with base stats."""

    def __init__(
        self,
        enemy_id: str,
        name: str,
        enemy_type: str,
        base_hp: int,
        base_damage: int,
        base_defense: int
    ):
        self.enemy_id = enemy_id
        self.name = name
        self.enemy_type = enemy_type
        self.base_hp = base_hp
        self.base_damage = base_damage
        self.base_defense = base_defense

        # Scaled stats (set when scaling to phase)
        self.hp = base_hp
        self.damage = base_damage
        self.defense = base_defense

    def scale_to_phase(self, player_phase: int) -> 'Enemy':
        """Scale enemy stats based on player phase (0-4)."""
        if player_phase not in VALID_PHASES:
            raise ValueError(f"Invalid player phase: {player_phase}")

        # Create scaled copy
        scaled = Enemy(
            enemy_id=self.enemy_id,
            name=self.name,
            enemy_type=self.enemy_type,
            base_hp=self.base_hp,
            base_damage=self.base_damage,
            base_defense=self.base_defense
        )

        # Scale stats: +20% per phase
        scale_multiplier = 1.0 + (player_phase * 0.2)

        scaled.hp = int(self.base_hp * scale_multiplier)
        scaled.damage = int(self.base_damage * scale_multiplier)
        scaled.defense = int(self.base_defense * scale_multiplier)

        return scaled

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "enemy_id": self.enemy_id,
            "name": self.name,
            "enemy_type": self.enemy_type,
            "base_hp": self.base_hp,
            "base_damage": self.base_damage,
            "base_defense": self.base_defense,
            "hp": self.hp,
            "damage": self.damage,
            "defense": self.defense
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Enemy':
        """Load from dictionary."""
        enemy = cls(
            enemy_id=data["enemy_id"],
            name=data["name"],
            enemy_type=data["enemy_type"],
            base_hp=data["base_hp"],
            base_damage=data["base_damage"],
            base_defense=data["base_defense"]
        )
        enemy.hp = data.get("hp", enemy.base_hp)
        enemy.damage = data.get("damage", enemy.base_damage)
        enemy.defense = data.get("defense", enemy.base_defense)
        return enemy


# ============================================================================
# ENCOUNTER CLASS
# ============================================================================

class Encounter:
    """Represents a combat encounter with enemies and rewards."""

    def __init__(
        self,
        encounter_id: str,
        name: str,
        description: str,
        difficulty: str,
        location_type: str
    ):
        if difficulty not in DIFFICULTY_TIERS:
            raise ValueError(f"Invalid difficulty: {difficulty}. Must be one of {DIFFICULTY_TIERS}")

        self.encounter_id = encounter_id
        self.name = name
        self.description = description
        self.difficulty = difficulty
        self.location_type = location_type

        # Enemy composition (enemy_type -> count)
        self.enemies: Dict[str, int] = {}

        # Rewards
        self.eddies_min = 0
        self.eddies_max = 0
        self.xp_reward = 0
        self.loot_table = "basic"

    def add_enemy(self, enemy_type: str, count: int):
        """Add enemies to this encounter."""
        if enemy_type in self.enemies:
            self.enemies[enemy_type] += count
        else:
            self.enemies[enemy_type] = count

    def set_rewards(
        self,
        eddies_min: int,
        eddies_max: int,
        xp_reward: int,
        loot_table: str
    ):
        """Set encounter rewards."""
        self.eddies_min = eddies_min
        self.eddies_max = eddies_max
        self.xp_reward = xp_reward
        self.loot_table = loot_table

    def generate_loot(self) -> Dict[str, Any]:
        """Generate loot from this encounter."""
        if not self.enemies:
            return {"eddies": 0, "items": []}

        # Random eddies in range
        eddies = random.randint(self.eddies_min, self.eddies_max)

        # Generate items based on loot table
        items = self._generate_items()

        return {
            "eddies": eddies,
            "items": items,
            "xp": self.xp_reward
        }

    def _generate_items(self) -> List[Dict[str, Any]]:
        """Generate items based on loot table."""
        items = []

        # Loot chance based on difficulty
        loot_chances = {
            "EASY": 0.3,
            "MEDIUM": 0.5,
            "HARD": 0.7,
            "EXTREME": 0.9
        }

        chance = loot_chances.get(self.difficulty, 0.5)

        # Roll for loot
        if random.random() < chance:
            # Generate items based on loot table
            loot_pools = {
                "basic": ["health_pack", "ammo", "junk"],
                "street_gear": ["pistol", "knife", "leather_jacket", "health_pack"],
                "corpo_gear": ["smg", "corpo_armor", "access_card", "credchip"],
                "combat_zone": ["rifle", "combat_armor", "grenade", "stim_pack"]
            }

            pool = loot_pools.get(self.loot_table, loot_pools["basic"])

            # Number of items based on difficulty
            item_count = {
                "EASY": 1,
                "MEDIUM": random.randint(1, 2),
                "HARD": random.randint(2, 3),
                "EXTREME": random.randint(3, 5)
            }

            num_items = item_count.get(self.difficulty, 1)

            for _ in range(num_items):
                item_id = random.choice(pool)
                items.append({
                    "item_id": item_id,
                    "quantity": 1
                })

        return items

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "encounter_id": self.encounter_id,
            "name": self.name,
            "description": self.description,
            "difficulty": self.difficulty,
            "location_type": self.location_type,
            "enemies": self.enemies,
            "eddies_min": self.eddies_min,
            "eddies_max": self.eddies_max,
            "xp_reward": self.xp_reward,
            "loot_table": self.loot_table
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Encounter':
        """Load from dictionary."""
        encounter = cls(
            encounter_id=data["encounter_id"],
            name=data["name"],
            description=data["description"],
            difficulty=data["difficulty"],
            location_type=data["location_type"]
        )

        encounter.enemies = data.get("enemies", {})
        encounter.eddies_min = data.get("eddies_min", 0)
        encounter.eddies_max = data.get("eddies_max", 0)
        encounter.xp_reward = data.get("xp_reward", 0)
        encounter.loot_table = data.get("loot_table", "basic")

        return encounter


# ============================================================================
# ENCOUNTER MANAGER
# ============================================================================

class EncounterManager:
    """Manages encounter generation and templates."""

    def __init__(self):
        self.enemy_types: Dict[str, Enemy] = {}
        self.templates: Dict[str, Encounter] = {}
        self._initialize_enemy_types()
        self._initialize_templates()

    def _initialize_enemy_types(self):
        """Initialize all enemy types."""
        # Basic enemies
        self.enemy_types["ganger_basic"] = Enemy(
            enemy_id="ganger_basic",
            name="Street Ganger",
            enemy_type="humanoid",
            base_hp=50,
            base_damage=10,
            base_defense=5
        )

        self.enemy_types["ganger_heavy"] = Enemy(
            enemy_id="ganger_heavy",
            name="Heavy Ganger",
            enemy_type="humanoid",
            base_hp=80,
            base_damage=15,
            base_defense=8
        )

        self.enemy_types["corpo_security"] = Enemy(
            enemy_id="corpo_security",
            name="Corporate Security",
            enemy_type="humanoid",
            base_hp=70,
            base_damage=12,
            base_defense=10
        )

        self.enemy_types["netrunner"] = Enemy(
            enemy_id="netrunner",
            name="Netrunner",
            enemy_type="humanoid",
            base_hp=60,
            base_damage=20,
            base_defense=5
        )

        self.enemy_types["solo"] = Enemy(
            enemy_id="solo",
            name="Solo Mercenary",
            enemy_type="humanoid",
            base_hp=100,
            base_damage=18,
            base_defense=12
        )

        self.enemy_types["boss"] = Enemy(
            enemy_id="boss",
            name="Gang Boss",
            enemy_type="humanoid",
            base_hp=200,
            base_damage=25,
            base_defense=15
        )

    def _initialize_templates(self):
        """Initialize encounter templates."""
        # EASY templates
        street_thugs = Encounter(
            encounter_id="street_thugs",
            name="Street Thugs",
            description="A couple of low-level gangers looking for trouble",
            difficulty="EASY",
            location_type="street"
        )
        street_thugs.add_enemy("ganger_basic", 2)
        street_thugs.set_rewards(100, 300, 25, "street_gear")
        self.templates["street_thugs"] = street_thugs

        lone_ganger = Encounter(
            encounter_id="lone_ganger",
            name="Lone Ganger",
            description="A single ganger on patrol",
            difficulty="EASY",
            location_type="street"
        )
        lone_ganger.add_enemy("ganger_basic", 1)
        lone_ganger.set_rewards(50, 150, 15, "basic")
        self.templates["lone_ganger"] = lone_ganger

        # MEDIUM templates
        ganger_ambush = Encounter(
            encounter_id="ganger_ambush",
            name="Ganger Ambush",
            description="Gangers ambush you in an alley",
            difficulty="MEDIUM",
            location_type="alley"
        )
        ganger_ambush.add_enemy("ganger_basic", 2)
        ganger_ambush.add_enemy("ganger_heavy", 1)
        ganger_ambush.set_rewards(300, 600, 50, "street_gear")
        self.templates["ganger_ambush"] = ganger_ambush

        corpo_patrol = Encounter(
            encounter_id="corpo_patrol",
            name="Corporate Patrol",
            description="Corporate security on patrol",
            difficulty="MEDIUM",
            location_type="corpo_building"
        )
        corpo_patrol.add_enemy("corpo_security", 3)
        corpo_patrol.set_rewards(400, 700, 60, "corpo_gear")
        self.templates["corpo_patrol"] = corpo_patrol

        netrunner_squad = Encounter(
            encounter_id="netrunner_squad",
            name="Netrunner Squad",
            description="Elite hackers defending their turf",
            difficulty="MEDIUM",
            location_type="data_center"
        )
        netrunner_squad.add_enemy("netrunner", 2)
        netrunner_squad.add_enemy("ganger_basic", 2)
        netrunner_squad.set_rewards(500, 800, 70, "corpo_gear")
        self.templates["netrunner_squad"] = netrunner_squad

        # HARD templates
        heavy_resistance = Encounter(
            encounter_id="heavy_resistance",
            name="Heavy Resistance",
            description="Well-armed gangers with heavy support",
            difficulty="HARD",
            location_type="gang_territory"
        )
        heavy_resistance.add_enemy("ganger_heavy", 3)
        heavy_resistance.add_enemy("ganger_basic", 2)
        heavy_resistance.set_rewards(600, 1200, 100, "combat_zone")
        self.templates["heavy_resistance"] = heavy_resistance

        corpo_strike_team = Encounter(
            encounter_id="corpo_strike_team",
            name="Corporate Strike Team",
            description="Elite corporate security forces",
            difficulty="HARD",
            location_type="corpo_building"
        )
        corpo_strike_team.add_enemy("corpo_security", 4)
        corpo_strike_team.add_enemy("solo", 1)
        corpo_strike_team.set_rewards(800, 1500, 120, "corpo_gear")
        self.templates["corpo_strike_team"] = corpo_strike_team

        solo_merc_team = Encounter(
            encounter_id="solo_merc_team",
            name="Solo Mercenary Team",
            description="Professional mercenaries hired to stop you",
            difficulty="HARD",
            location_type="combat_zone"
        )
        solo_merc_team.add_enemy("solo", 3)
        solo_merc_team.set_rewards(1000, 1800, 150, "combat_zone")
        self.templates["solo_merc_team"] = solo_merc_team

        # EXTREME templates
        gang_war = Encounter(
            encounter_id="gang_war",
            name="Gang War",
            description="Full gang assault with boss leading",
            difficulty="EXTREME",
            location_type="combat_zone"
        )
        gang_war.add_enemy("boss", 1)
        gang_war.add_enemy("ganger_heavy", 4)
        gang_war.add_enemy("ganger_basic", 3)
        gang_war.set_rewards(1500, 3000, 250, "combat_zone")
        self.templates["gang_war"] = gang_war

        corpo_siege = Encounter(
            encounter_id="corpo_siege",
            name="Corporate Siege",
            description="Full corporate assault force",
            difficulty="EXTREME",
            location_type="corpo_building"
        )
        corpo_siege.add_enemy("corpo_security", 6)
        corpo_siege.add_enemy("solo", 2)
        corpo_siege.add_enemy("netrunner", 1)
        corpo_siege.set_rewards(2000, 4000, 300, "corpo_gear")
        self.templates["corpo_siege"] = corpo_siege

        final_boss = Encounter(
            encounter_id="final_boss",
            name="Final Confrontation",
            description="The ultimate showdown",
            difficulty="EXTREME",
            location_type="boss_arena"
        )
        final_boss.add_enemy("boss", 2)
        final_boss.add_enemy("solo", 3)
        final_boss.set_rewards(3000, 5000, 500, "combat_zone")
        self.templates["final_boss"] = final_boss

    def generate_enemy(self, enemy_type: str, player_phase: int) -> Enemy:
        """Generate an enemy scaled to player phase."""
        if player_phase not in VALID_PHASES:
            raise ValueError(f"Invalid player phase: {player_phase}")

        if enemy_type not in self.enemy_types:
            raise ValueError(f"Unknown enemy type: {enemy_type}")

        base_enemy = self.enemy_types[enemy_type]
        return base_enemy.scale_to_phase(player_phase)

    def generate_encounter(
        self,
        player_phase: int,
        difficulty: str,
        location_type: str
    ) -> Encounter:
        """Generate a scaled encounter based on parameters."""
        if player_phase not in VALID_PHASES:
            raise ValueError(f"Invalid player phase: {player_phase}")

        if difficulty not in DIFFICULTY_TIERS:
            raise ValueError(f"Invalid difficulty: {difficulty}")

        # Create encounter based on difficulty and phase
        encounter_id = f"{location_type}_{difficulty.lower()}_p{player_phase}"

        encounter = Encounter(
            encounter_id=encounter_id,
            name=self._generate_name(difficulty, location_type),
            description=f"A {difficulty.lower()} encounter in {location_type}",
            difficulty=difficulty,
            location_type=location_type
        )

        # Add enemies based on difficulty and phase
        enemy_count = self._calculate_enemy_count(difficulty, player_phase)
        self._populate_enemies(encounter, enemy_count, location_type)

        # Set rewards based on difficulty and phase
        self._set_scaled_rewards(encounter, difficulty, player_phase, location_type)

        return encounter

    def _generate_name(self, difficulty: str, location_type: str) -> str:
        """Generate encounter name based on parameters."""
        names = {
            "EASY": ["Minor Skirmish", "Quick Encounter", "Street Fight"],
            "MEDIUM": ["Hostile Encounter", "Armed Conflict", "Gang Battle"],
            "HARD": ["Heavy Resistance", "Dangerous Engagement", "Elite Forces"],
            "EXTREME": ["Death Trap", "Overwhelming Force", "Final Stand"]
        }
        return random.choice(names.get(difficulty, ["Encounter"]))

    def _calculate_enemy_count(self, difficulty: str, player_phase: int) -> int:
        """Calculate total enemy count based on difficulty and phase."""
        base_counts = {
            "EASY": 2,
            "MEDIUM": 4,
            "HARD": 6,
            "EXTREME": 8
        }

        base = base_counts.get(difficulty, 2)
        # Add enemies based on phase (0-2 additional)
        phase_bonus = player_phase // 2

        return base + phase_bonus

    def _populate_enemies(self, encounter: Encounter, total_count: int, location_type: str):
        """Populate encounter with appropriate enemies."""
        # Choose enemy types based on location
        enemy_pools = {
            "street": ["ganger_basic", "ganger_heavy"],
            "alley": ["ganger_basic", "ganger_heavy"],
            "corpo_building": ["corpo_security", "netrunner"],
            "corpo_plaza": ["corpo_security", "solo"],
            "combat_zone": ["ganger_heavy", "solo"],
            "gang_territory": ["ganger_basic", "ganger_heavy", "boss"],
            "data_center": ["netrunner", "corpo_security"]
        }

        pool = enemy_pools.get(location_type, ["ganger_basic"])

        # Distribute enemies
        if encounter.difficulty == "EXTREME":
            # EXTREME: Include boss
            if total_count >= 6:
                encounter.add_enemy("boss", 1)
                total_count -= 1

        # Fill remaining slots
        for _ in range(total_count):
            enemy_type = random.choice(pool)
            encounter.add_enemy(enemy_type, 1)

    def _set_scaled_rewards(
        self,
        encounter: Encounter,
        difficulty: str,
        player_phase: int,
        location_type: str
    ):
        """Set rewards scaled to difficulty and phase."""
        # Base rewards by difficulty
        base_rewards = {
            "EASY": (100, 300, 25),
            "MEDIUM": (300, 700, 60),
            "HARD": (600, 1500, 120),
            "EXTREME": (1200, 3000, 250)
        }

        eddies_min, eddies_max, xp = base_rewards.get(difficulty, (100, 300, 25))

        # Scale by phase (+25% per phase)
        phase_multiplier = 1.0 + (player_phase * 0.25)
        eddies_min = int(eddies_min * phase_multiplier)
        eddies_max = int(eddies_max * phase_multiplier)
        xp = int(xp * phase_multiplier)

        # Loot table by location
        loot_tables = {
            "street": "street_gear",
            "alley": "street_gear",
            "corpo_building": "corpo_gear",
            "corpo_plaza": "corpo_gear",
            "combat_zone": "combat_zone",
            "gang_territory": "street_gear",
            "data_center": "corpo_gear"
        }

        loot_table = loot_tables.get(location_type, "basic")

        encounter.set_rewards(eddies_min, eddies_max, xp, loot_table)

    def generate_random_encounter(
        self,
        player_phase: int,
        location_type: str
    ) -> Encounter:
        """Generate a random encounter appropriate for location."""
        # Weight difficulties based on phase
        difficulty_weights = {
            0: [0.6, 0.3, 0.1, 0.0],  # Phase 0: Mostly easy
            1: [0.4, 0.4, 0.2, 0.0],  # Phase 1: Easy/Medium
            2: [0.2, 0.5, 0.3, 0.0],  # Phase 2: Medium/Hard
            3: [0.1, 0.3, 0.5, 0.1],  # Phase 3: Hard focus
            4: [0.0, 0.2, 0.5, 0.3]   # Phase 4: Hard/Extreme
        }

        weights = difficulty_weights.get(player_phase, [0.4, 0.4, 0.2, 0.0])
        difficulty = random.choices(DIFFICULTY_TIERS, weights=weights)[0]

        return self.generate_encounter(player_phase, difficulty, location_type)

    def get_template(self, template_name: str) -> Optional[Encounter]:
        """Get encounter template by name."""
        return self.templates.get(template_name)

    def get_all_templates(self) -> List[Encounter]:
        """Get all encounter templates."""
        return list(self.templates.values())

    def instantiate_template(self, template: Encounter, player_phase: int) -> Encounter:
        """Create encounter instance from template, scaled to phase."""
        # Create new instance
        encounter = Encounter(
            encounter_id=f"{template.encounter_id}_p{player_phase}",
            name=template.name,
            description=template.description,
            difficulty=template.difficulty,
            location_type=template.location_type
        )

        # Copy enemies
        encounter.enemies = template.enemies.copy()

        # Scale rewards based on phase
        phase_multiplier = 1.0 + (player_phase * 0.25)
        eddies_min = int(template.eddies_min * phase_multiplier)
        eddies_max = int(template.eddies_max * phase_multiplier)
        xp = int(template.xp_reward * phase_multiplier)

        encounter.set_rewards(eddies_min, eddies_max, xp, template.loot_table)

        return encounter

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "templates": {
                name: template.to_dict()
                for name, template in self.templates.items()
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EncounterManager':
        """Load from dictionary."""
        manager = cls()

        # Templates are already initialized, but we could override them
        # For now, just return initialized manager

        return manager
