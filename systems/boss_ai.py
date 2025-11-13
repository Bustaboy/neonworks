"""
Boss AI System

Advanced AI system for boss battles with multi-phase mechanics and patterns.
"""

from typing import Dict, List, Optional, Any
from engine.core.ecs import System, World, Entity
from engine.core.events import Event, EventManager, EventType
from gameplay.combat import Health
from gameplay.jrpg_combat import BossPhase, BattleAI, JRPGStats


class BossAISystem(System):
    """
    Advanced AI system for boss battles.

    Features:
    - Multi-phase bosses with HP thresholds
    - Attack patterns and rotations
    - Special abilities with cooldowns
    - Phase-specific behaviors
    - Enrage mechanics
    """

    def __init__(self, event_manager: EventManager):
        super().__init__()
        self.priority = 35
        self.event_manager = event_manager

        # Active boss battles
        self.active_bosses: Dict[str, Entity] = {}  # boss_id -> entity

    def update(self, world: World, delta_time: float):
        """Update boss AI system"""
        # Check for phase transitions
        self._check_phase_transitions(world)

    def register_boss(self, boss_entity: Entity):
        """Register a boss for AI processing"""
        boss_phase = boss_entity.get_component(BossPhase)
        if boss_phase:
            self.active_bosses[boss_entity.id] = boss_entity

    def unregister_boss(self, boss_id: str):
        """Unregister a boss"""
        if boss_id in self.active_bosses:
            del self.active_bosses[boss_id]

    def _check_phase_transitions(self, world: World):
        """Check if any boss should transition phases"""
        for boss_id, boss in list(self.active_bosses.items()):
            health = boss.get_component(Health)
            boss_phase = boss.get_component(BossPhase)

            if not health or not boss_phase or not health.is_alive:
                continue

            # Check HP percentage
            hp_percentage = (health.hp / health.max_hp) * 100.0

            # Check if should advance phase
            if boss_phase.should_advance_phase(hp_percentage):
                self._trigger_phase_transition(world, boss, boss_phase)

    def _trigger_phase_transition(self, world: World, boss: Entity, boss_phase: BossPhase):
        """Trigger boss phase transition"""
        old_phase = boss_phase.current_phase
        boss_phase.advance_phase()
        new_phase = boss_phase.current_phase

        # Get phase data
        phase_data = boss_phase.get_current_phase_data()

        # Apply phase changes
        if phase_data:
            self._apply_phase_changes(world, boss, phase_data)

        # Emit phase change event
        self.event_manager.emit(Event(
            EventType.CUSTOM,
            {
                "type": "boss_phase_change",
                "boss_id": boss.id,
                "old_phase": old_phase,
                "new_phase": new_phase,
                "phase_data": phase_data,
            }
        ))

    def _apply_phase_changes(self, world: World, boss: Entity, phase_data: Dict[str, Any]):
        """Apply changes when boss enters new phase"""
        stats = boss.get_component(JRPGStats)
        ai = boss.get_component(BattleAI)

        # Stat changes
        if stats and "stat_changes" in phase_data:
            stat_changes = phase_data["stat_changes"]
            for stat_name, change in stat_changes.items():
                if hasattr(stats, stat_name):
                    current_value = getattr(stats, stat_name)
                    setattr(stats, stat_name, current_value + change)

        # AI changes
        if ai and "ai_changes" in phase_data:
            ai_changes = phase_data["ai_changes"]
            if "attack_pattern" in ai_changes:
                ai.attack_pattern = ai_changes["attack_pattern"]
            if "preferred_spells" in ai_changes:
                ai.preferred_spells = ai_changes["preferred_spells"]

        # Heal/damage
        if "heal_percentage" in phase_data:
            health = boss.get_component(Health)
            if health:
                heal_amount = int(health.max_hp * phase_data["heal_percentage"] / 100.0)
                health.hp = min(health.max_hp, health.hp + heal_amount)

        # Summon adds
        if "summon_enemies" in phase_data:
            self._summon_adds(world, boss, phase_data["summon_enemies"])

    def _summon_adds(self, world: World, boss: Entity, add_data: List[Dict[str, Any]]):
        """Summon additional enemies during boss fight"""
        for add in add_data:
            enemy_id = add.get("enemy_id", "")
            level = add.get("level", 1)
            position = add.get("position", 0)

            # Emit summon event
            self.event_manager.emit(Event(
                EventType.CUSTOM,
                {
                    "type": "boss_summon_add",
                    "boss_id": boss.id,
                    "enemy_id": enemy_id,
                    "level": level,
                    "position": position,
                }
            ))

    def create_boss_template(self, boss_id: str, name: str, phases: int = 2) -> Dict[str, Any]:
        """
        Create a boss template with default multi-phase setup.

        Returns:
            Dictionary with boss configuration
        """
        boss_template = {
            "boss_id": boss_id,
            "name": name,
            "max_phases": phases,
            "phase_triggers": [],
            "phases": {},
        }

        # Default phase triggers (HP percentages)
        if phases >= 2:
            boss_template["phase_triggers"].append(70.0)  # Phase 2 at 70% HP
        if phases >= 3:
            boss_template["phase_triggers"].append(40.0)  # Phase 3 at 40% HP
        if phases >= 4:
            boss_template["phase_triggers"].append(15.0)  # Phase 4 at 15% HP

        # Default phase data
        for phase in range(1, phases + 1):
            boss_template["phases"][phase] = {
                "name": f"Phase {phase}",
                "stat_changes": {},
                "ai_changes": {},
                "new_abilities": [],
                "dialogue": f"Phase {phase} begins!",
            }

        return boss_template


# Example boss definitions
BOSS_TEMPLATES = {
    "skeleton_king": {
        "boss_id": "skeleton_king",
        "name": "Skeleton King",
        "max_phases": 2,
        "phase_triggers": [50.0],  # Phase 2 at 50% HP
        "phases": {
            1: {
                "name": "Initial Phase",
                "attack_pattern": ["attack", "attack", "spell"],
                "preferred_spells": ["dark_bolt"],
                "dialogue": "You dare challenge the Skeleton King?",
            },
            2: {
                "name": "Enraged",
                "stat_changes": {"attack": 5, "speed": 3},
                "ai_changes": {
                    "attack_pattern": ["spell", "spell", "attack"],
                    "preferred_spells": ["dark_storm", "summon_skeletons"],
                },
                "summon_enemies": [
                    {"enemy_id": "skeleton", "level": 5, "position": 0},
                    {"enemy_id": "skeleton", "level": 5, "position": 2},
                ],
                "dialogue": "My power grows! Rise, my minions!",
            },
        },
    },

    "dragon": {
        "boss_id": "dragon",
        "name": "Ancient Dragon",
        "max_phases": 3,
        "phase_triggers": [66.0, 33.0],
        "phases": {
            1: {
                "name": "Grounded",
                "attack_pattern": ["attack", "breath"],
                "preferred_spells": ["fire_breath"],
                "dialogue": "A foolish mortal dares disturb my slumber!",
            },
            2: {
                "name": "Airborne",
                "stat_changes": {"speed": 5, "defense": -5},
                "ai_changes": {
                    "attack_pattern": ["spell", "spell", "dive_attack"],
                    "preferred_spells": ["meteor", "fire_storm"],
                },
                "dialogue": "Feel my wrath from above!",
            },
            3: {
                "name": "Desperate Fury",
                "stat_changes": {"attack": 10, "magic_attack": 10},
                "heal_percentage": 20.0,  # Heals 20% HP
                "ai_changes": {
                    "attack_pattern": ["spell", "spell", "spell", "ultimate"],
                    "preferred_spells": ["inferno", "meteor", "dragon_rage"],
                },
                "dialogue": "I will not fall! DRAGON RAGE!!!",
            },
        },
    },

    "dark_sorcerer": {
        "boss_id": "dark_sorcerer",
        "name": "Dark Sorcerer",
        "max_phases": 3,
        "phase_triggers": [75.0, 40.0],
        "phases": {
            1: {
                "name": "Testing",
                "attack_pattern": ["spell", "attack", "spell"],
                "preferred_spells": ["shadow_bolt", "poison"],
                "dialogue": "Let's see what you're capable of...",
            },
            2: {
                "name": "Serious",
                "stat_changes": {"magic_attack": 7, "magic_defense": 5},
                "ai_changes": {
                    "attack_pattern": ["spell", "spell", "spell"],
                    "preferred_spells": ["dark_wave", "curse", "drain"],
                },
                "dialogue": "Impressive. But playtime is over!",
            },
            3: {
                "name": "True Power",
                "stat_changes": {"magic_attack": 15},
                "ai_changes": {
                    "attack_pattern": ["ultimate", "spell", "spell", "ultimate"],
                    "preferred_spells": ["void", "death", "black_hole"],
                },
                "summon_enemies": [
                    {"enemy_id": "shadow", "level": 10, "position": 0},
                    {"enemy_id": "shadow", "level": 10, "position": 2},
                ],
                "dialogue": "Witness my TRUE POWER! VOID MAGIC!",
            },
        },
    },
}


def create_boss_entity(world: World, boss_template: Dict[str, Any],
                      level: int = 10) -> Entity:
    """
    Create a boss entity from template.

    Args:
        world: ECS world
        boss_template: Boss configuration dictionary
        level: Boss level

    Returns:
        Created boss entity
    """
    from engine.core.ecs import Transform, GridPosition, Sprite
    from gameplay.jrpg_combat import EnemyData, MagicPoints, SpellList

    boss = world.create_entity()
    boss.add_tag("enemy")
    boss.add_tag("boss")

    # Basic components
    boss.add_component(Transform())
    boss.add_component(GridPosition())
    boss.add_component(Sprite(texture="boss_sprite.png", width=64, height=64))

    # Enemy data
    boss.add_component(EnemyData(
        enemy_id=boss_template["boss_id"],
        enemy_name=boss_template["name"],
        enemy_type="boss",
        is_boss=True,
        can_escape_from=False,
    ))

    # Combat stats (scale with level)
    base_hp = 500
    base_mp = 100
    boss.add_component(Health(
        max_hp=base_hp + level * 50,
        hp=base_hp + level * 50,
    ))
    boss.add_component(MagicPoints(
        max_mp=base_mp + level * 10,
        current_mp=base_mp + level * 10,
    ))
    boss.add_component(JRPGStats(
        level=level,
        attack=15 + level,
        defense=12 + level,
        magic_attack=18 + level,
        magic_defense=15 + level,
        speed=10 + level // 2,
        luck=8,
    ))

    # Boss phase component
    boss_phase = BossPhase(
        current_phase=1,
        max_phases=boss_template["max_phases"],
        phase_triggers=boss_template["phase_triggers"],
        phases=boss_template["phases"],
    )
    boss.add_component(boss_phase)

    # Battle AI
    phase_1_data = boss_template["phases"][1]
    boss.add_component(BattleAI(
        ai_type="boss",
        attack_pattern=phase_1_data.get("attack_pattern", ["attack"]),
        preferred_spells=phase_1_data.get("preferred_spells", []),
    ))

    # Spell list
    all_spells = []
    for phase_data in boss_template["phases"].values():
        all_spells.extend(phase_data.get("preferred_spells", []))
    boss.add_component(SpellList(learned_spells=list(set(all_spells))))

    # Rewards (bosses give big rewards)
    boss.add_component(BattleRewards(
        experience=100 * level,
        gold=50 * level,
        items=[
            {"item_id": "boss_drop", "chance": 100.0, "quantity": 1},
            {"item_id": "rare_item", "chance": 50.0, "quantity": 1},
        ],
    ))

    return boss
