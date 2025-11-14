"""
Random Encounter System for JRPG-style Games

Handles random battles triggered during exploration.
"""

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from neonworks.core.ecs import Entity, System, World
from neonworks.core.events import Event, EventManager, EventType


@dataclass
class EncounterGroup:
    """Definition of an encounter group"""

    group_id: str
    enemies: List[Dict[str, any]] = field(default_factory=list)  # enemy_id, level, position
    weight: int = 10  # Spawn weight
    min_steps: int = 0  # Minimum steps before can appear
    max_steps: int = 9999  # Maximum steps before stops appearing

    def get_total_enemies(self) -> int:
        """Get total number of enemies in group"""
        return len(self.enemies)


@dataclass
class EncounterTable:
    """Table of encounters for a specific zone"""

    zone_id: str
    encounter_rate: float = 30.0  # Base encounter rate (encounters per 256 steps)
    step_interval: int = 8  # Check for encounter every N steps

    # Encounter groups with weights
    groups: List[EncounterGroup] = field(default_factory=list)

    # Modifiers
    rate_multiplier: float = 1.0  # Can be modified by items/statuses
    can_encounter: bool = True  # Can be disabled in safe zones

    def add_group(self, group: EncounterGroup):
        """Add encounter group to table"""
        self.groups.append(group)

    def get_random_group(self, steps: int) -> Optional[EncounterGroup]:
        """Get random encounter group weighted by spawn weights"""
        if not self.groups or not self.can_encounter:
            return None

        # Filter groups by step range
        valid_groups = [g for g in self.groups if g.min_steps <= steps <= g.max_steps]

        if not valid_groups:
            return None

        # Weighted random selection
        total_weight = sum(g.weight for g in valid_groups)
        if total_weight <= 0:
            return None

        rand_value = random.randint(1, total_weight)
        current_weight = 0

        for group in valid_groups:
            current_weight += group.weight
            if rand_value <= current_weight:
                return group

        return valid_groups[0]  # Fallback


class RandomEncounterSystem(System):
    """
    System for triggering random encounters during exploration.

    Features:
    - Step-based encounter triggering
    - Zone-specific encounter tables
    - Encounter rate modifiers (repel items, etc.)
    - Battle transition effects
    """

    def __init__(self, event_manager: EventManager):
        super().__init__()
        self.priority = 20
        self.event_manager = event_manager

        # Encounter tables (zone_id -> EncounterTable)
        self.encounter_tables: Dict[str, EncounterTable] = {}

        # Current state
        self.current_zone: str = ""
        self.step_count: int = 0
        self.steps_since_last_encounter: int = 0

        # Encounter rate modifiers
        self.repel_active: bool = False
        self.repel_duration: int = 0  # Steps remaining
        self.repel_multiplier: float = 0.5  # Reduce encounter rate

        # Subscribe to step events
        self.event_manager.subscribe(EventType.CUSTOM, self._handle_custom_event)

        # Load default encounter tables
        self._load_default_tables()

    def update(self, world: World, delta_time: float):
        """Update encounter system"""
        # Reduce repel duration
        if self.repel_active and self.repel_duration > 0:
            # Repel duration is reduced by steps, not time
            pass

    def register_encounter_table(self, table: EncounterTable):
        """Register an encounter table for a zone"""
        self.encounter_tables[table.zone_id] = table

    def set_current_zone(self, zone_id: str):
        """Set current zone for encounters"""
        self.current_zone = zone_id
        self.step_count = 0
        self.steps_since_last_encounter = 0

    def check_encounter(self) -> bool:
        """
        Check if an encounter should trigger.

        Called when player takes a step.

        Returns:
            True if encounter triggered
        """
        # Get current zone's encounter table
        table = self.encounter_tables.get(self.current_zone)
        if not table or not table.can_encounter:
            return False

        # Check step interval
        if self.steps_since_last_encounter % table.step_interval != 0:
            return False

        # Calculate encounter chance
        base_rate = table.encounter_rate
        multiplier = table.rate_multiplier

        # Apply repel modifier
        if self.repel_active:
            multiplier *= self.repel_multiplier

        # Encounter formula: (base_rate / 256) * multiplier
        encounter_chance = (base_rate / 256.0) * multiplier

        # Random check
        if random.random() < encounter_chance:
            return self._trigger_encounter(table)

        return False

    def _trigger_encounter(self, table: EncounterTable) -> bool:
        """Trigger a random encounter"""
        # Get random encounter group
        group = table.get_random_group(self.step_count)
        if not group:
            return False

        # Reset step counter
        self.steps_since_last_encounter = 0

        # Emit encounter event
        self.event_manager.emit(
            Event(
                EventType.CUSTOM,
                {
                    "type": "random_encounter",
                    "zone_id": self.current_zone,
                    "group_id": group.group_id,
                    "enemies": group.enemies,
                    "step_count": self.step_count,
                },
            )
        )

        return True

    def activate_repel(self, duration: int = 100):
        """Activate repel effect (reduces encounter rate)"""
        self.repel_active = True
        self.repel_duration = duration

        self.event_manager.emit(
            Event(
                EventType.CUSTOM,
                {
                    "type": "repel_activated",
                    "duration": duration,
                },
            )
        )

    def deactivate_repel(self):
        """Deactivate repel effect"""
        self.repel_active = False
        self.repel_duration = 0

        self.event_manager.emit(Event(EventType.CUSTOM, {"type": "repel_deactivated"}))

    def force_encounter(self, group_id: str) -> bool:
        """Force a specific encounter (for scripted battles)"""
        table = self.encounter_tables.get(self.current_zone)
        if not table:
            return False

        # Find group
        group = None
        for g in table.groups:
            if g.group_id == group_id:
                group = g
                break

        if not group:
            return False

        # Trigger encounter
        self.event_manager.emit(
            Event(
                EventType.CUSTOM,
                {
                    "type": "random_encounter",
                    "zone_id": self.current_zone,
                    "group_id": group.group_id,
                    "enemies": group.enemies,
                    "forced": True,
                },
            )
        )

        return True

    def _handle_custom_event(self, event: Event):
        """Handle custom events"""
        if not event.data:
            return

        event_type = event.data.get("type")

        # Handle player step
        if event_type == "player_step":
            self.step_count += 1
            self.steps_since_last_encounter += 1

            # Reduce repel duration
            if self.repel_active:
                self.repel_duration -= 1
                if self.repel_duration <= 0:
                    self.deactivate_repel()

            # Check for encounter
            self.check_encounter()

        # Handle zone loaded
        elif event_type == "zone_loaded":
            zone_id = event.data.get("zone_id")
            if zone_id:
                self.set_current_zone(zone_id)

    def _load_default_tables(self):
        """Load default encounter tables for demo"""
        # Example: Grassland encounters
        grassland_table = EncounterTable(
            zone_id="grassland",
            encounter_rate=30.0,
            step_interval=8,
        )

        # Easy encounters (1-2 slimes)
        grassland_table.add_group(
            EncounterGroup(
                group_id="slime_single",
                enemies=[{"enemy_id": "slime", "level": 1, "position": 0}],
                weight=40,
                max_steps=50,
            )
        )

        grassland_table.add_group(
            EncounterGroup(
                group_id="slime_pair",
                enemies=[
                    {"enemy_id": "slime", "level": 1, "position": 0},
                    {"enemy_id": "slime", "level": 1, "position": 1},
                ],
                weight=30,
            )
        )

        # Medium encounters (goblins)
        grassland_table.add_group(
            EncounterGroup(
                group_id="goblin_single",
                enemies=[{"enemy_id": "goblin", "level": 2, "position": 0}],
                weight=20,
                min_steps=20,
            )
        )

        grassland_table.add_group(
            EncounterGroup(
                group_id="goblin_group",
                enemies=[
                    {"enemy_id": "goblin", "level": 2, "position": 0},
                    {"enemy_id": "goblin", "level": 2, "position": 1},
                    {"enemy_id": "slime", "level": 1, "position": 2},
                ],
                weight=10,
                min_steps=30,
            )
        )

        self.register_encounter_table(grassland_table)

        # Example: Forest encounters
        forest_table = EncounterTable(
            zone_id="forest",
            encounter_rate=35.0,
            step_interval=7,
        )

        forest_table.add_group(
            EncounterGroup(
                group_id="wolf_single",
                enemies=[{"enemy_id": "wolf", "level": 3, "position": 0}],
                weight=30,
            )
        )

        forest_table.add_group(
            EncounterGroup(
                group_id="wolf_pack",
                enemies=[
                    {"enemy_id": "wolf", "level": 3, "position": 0},
                    {"enemy_id": "wolf", "level": 3, "position": 1},
                ],
                weight=25,
            )
        )

        forest_table.add_group(
            EncounterGroup(
                group_id="spider_group",
                enemies=[
                    {"enemy_id": "spider", "level": 4, "position": 0},
                    {"enemy_id": "spider", "level": 3, "position": 1},
                    {"enemy_id": "spider", "level": 3, "position": 2},
                ],
                weight=15,
            )
        )

        self.register_encounter_table(forest_table)

        # Example: Dungeon encounters
        dungeon_table = EncounterTable(
            zone_id="dungeon",
            encounter_rate=40.0,
            step_interval=6,
        )

        dungeon_table.add_group(
            EncounterGroup(
                group_id="skeleton_group",
                enemies=[
                    {"enemy_id": "skeleton", "level": 5, "position": 0},
                    {"enemy_id": "skeleton", "level": 5, "position": 1},
                ],
                weight=35,
            )
        )

        dungeon_table.add_group(
            EncounterGroup(
                group_id="zombie_horde",
                enemies=[
                    {"enemy_id": "zombie", "level": 6, "position": 0},
                    {"enemy_id": "zombie", "level": 5, "position": 1},
                    {"enemy_id": "zombie", "level": 5, "position": 2},
                ],
                weight=25,
            )
        )

        dungeon_table.add_group(
            EncounterGroup(
                group_id="boss_chamber",
                enemies=[
                    {"enemy_id": "dark_knight", "level": 8, "position": 1},
                    {"enemy_id": "skeleton", "level": 5, "position": 0},
                    {"enemy_id": "skeleton", "level": 5, "position": 2},
                ],
                weight=10,
                min_steps=100,
            )
        )

        self.register_encounter_table(dungeon_table)

    def get_encounter_stats(self) -> Dict[str, any]:
        """Get encounter statistics"""
        return {
            "current_zone": self.current_zone,
            "step_count": self.step_count,
            "steps_since_last": self.steps_since_last_encounter,
            "repel_active": self.repel_active,
            "repel_duration": self.repel_duration,
        }
