"""
JRPG Battle System

Traditional JRPG-style turn-based combat with side-view presentation.
"""

import random
from enum import Enum
from typing import Dict, List, Optional, Tuple

import pygame

from gameplay.combat import Health, Team
from gameplay.jrpg_combat import (BattleAI, BattleCommand, BattleFormation,
                                  BattleRewards, BattleState, BossPhase,
                                  EnemyData, JRPGStats, MagicPoints,
                                  PartyMember, SpellList, TargetType)
from neonworks.core.ecs import Entity, System, World
from neonworks.core.events import Event, EventManager, EventType


class BattlePhase(Enum):
    """Phases of battle"""

    INTRO = "intro"
    PLAYER_TURN = "player_turn"
    ENEMY_TURN = "enemy_turn"
    EXECUTING_ACTIONS = "executing_actions"
    VICTORY = "victory"
    DEFEAT = "defeat"
    ESCAPED = "escaped"


class JRPGBattleSystem(System):
    """
    JRPG-style battle system with traditional turn-based combat.

    Features:
    - Turn-based combat with battle menu
    - Party vs enemies formation
    - Magic, items, defend, run commands
    - Initiative-based turn order
    - Elemental system
    - Boss battles with phases
    - Victory rewards (XP, gold, items)
    """

    def __init__(self, event_manager: EventManager):
        super().__init__()
        self.priority = 30
        self.event_manager = event_manager

        # Battle state
        self.in_battle = False
        self.battle_phase = BattlePhase.INTRO
        self.battle_turn = 0

        # Participants
        self.party_members: List[Entity] = []
        self.enemies: List[Entity] = []
        self.all_combatants: List[Entity] = []

        # Turn order (sorted by initiative)
        self.turn_order: List[Entity] = []
        self.current_turn_index = 0
        self.current_actor: Optional[Entity] = None

        # Battle settings
        self.can_escape = True
        self.is_boss_battle = False
        self.background = ""

        # Intro/outro timers
        self.phase_timer = 0.0
        self.intro_duration = 1.5  # seconds
        self.victory_duration = 3.0

        # Subscribe to spell casting and damage events
        self.event_manager.subscribe(EventType.CUSTOM, self._handle_custom_event)

    def update(self, world: World, delta_time: float):
        """Update battle system"""
        if not self.in_battle:
            return

        # Update phase timers
        self.phase_timer += delta_time

        # Handle current phase
        if self.battle_phase == BattlePhase.INTRO:
            self._update_intro_phase(world)

        elif self.battle_phase == BattlePhase.PLAYER_TURN:
            self._update_player_turn_phase(world, delta_time)

        elif self.battle_phase == BattlePhase.ENEMY_TURN:
            self._update_enemy_turn_phase(world, delta_time)

        elif self.battle_phase == BattlePhase.EXECUTING_ACTIONS:
            self._update_executing_actions_phase(world, delta_time)

        elif self.battle_phase == BattlePhase.VICTORY:
            self._update_victory_phase(world)

        elif self.battle_phase == BattlePhase.DEFEAT:
            self._update_defeat_phase(world)

    def start_battle(
        self,
        world: World,
        party: List[Entity],
        enemies: List[Entity],
        can_escape: bool = True,
        is_boss: bool = False,
    ):
        """Start a new battle"""
        self.in_battle = True
        self.battle_phase = BattlePhase.INTRO
        self.battle_turn = 0
        self.phase_timer = 0.0

        self.party_members = party.copy()
        self.enemies = enemies.copy()
        self.all_combatants = party + enemies

        self.can_escape = can_escape
        self.is_boss_battle = is_boss

        # Initialize battle states
        for entity in self.all_combatants:
            if not entity.has_component(BattleState):
                entity.add_component(BattleState())

            battle_state = entity.get_component(BattleState)
            battle_state.has_acted = False
            battle_state.is_defending = False

        # Calculate turn order based on initiative
        self._calculate_turn_order()

        # Emit battle start event
        self.event_manager.emit(
            Event(
                EventType.CUSTOM,
                {
                    "type": "battle_start",
                    "party_ids": [e.id for e in party],
                    "enemy_ids": [e.id for e in enemies],
                    "is_boss": is_boss,
                },
            )
        )

    def end_battle(self, world: World, victory: bool):
        """End the current battle"""
        if not self.in_battle:
            return

        # Emit battle end event
        self.event_manager.emit(
            Event(
                EventType.CUSTOM,
                {
                    "type": "battle_end",
                    "victory": victory,
                    "turns": self.battle_turn,
                },
            )
        )

        # Clean up
        self.in_battle = False
        self.party_members.clear()
        self.enemies.clear()
        self.all_combatants.clear()
        self.turn_order.clear()
        self.current_actor = None

    def player_select_action(
        self,
        world: World,
        command: BattleCommand,
        targets: List[Entity],
        data: Optional[Dict] = None,
    ):
        """
        Player selects an action for current actor.

        Args:
            world: ECS world
            command: Battle command (attack, magic, item, etc.)
            targets: List of target entities
            data: Additional data (spell_id, item_id, etc.)
        """
        if not self.current_actor or self.battle_phase != BattlePhase.PLAYER_TURN:
            return

        battle_state = self.current_actor.get_component(BattleState)
        if not battle_state or battle_state.has_acted:
            return

        # Set pending action
        battle_state.pending_action = command.value
        battle_state.pending_targets = [t.id for t in targets]

        # Store additional data (spell_id, item_id, etc.)
        if data:
            # Would store in battle state or temporary storage
            pass

        # Mark as acted
        battle_state.has_acted = True

        # Move to next turn
        self._next_turn(world)

    def _calculate_turn_order(self):
        """Calculate turn order based on initiative"""
        self.turn_order.clear()

        # Calculate initiative for each combatant
        initiative_list = []
        for entity in self.all_combatants:
            health = entity.get_component(Health)
            if not health or not health.is_alive:
                continue

            battle_state = entity.get_component(BattleState)
            stats = entity.get_component(JRPGStats)

            # Calculate initiative (speed + random)
            initiative = 0
            if stats:
                initiative = stats.speed
            initiative += random.randint(0, 10)

            if battle_state:
                battle_state.initiative = initiative

            initiative_list.append((entity, initiative))

        # Sort by initiative (highest first)
        initiative_list.sort(key=lambda x: x[1], reverse=True)
        self.turn_order = [entity for entity, _ in initiative_list]

        self.current_turn_index = 0

    def _next_turn(self, world: World):
        """Advance to next turn"""
        self.current_turn_index += 1

        if self.current_turn_index >= len(self.turn_order):
            # All combatants have acted, start new round
            self._start_new_round(world)
            return

        # Get next actor
        self.current_actor = self.turn_order[self.current_turn_index]

        # Check if actor is alive
        health = self.current_actor.get_component(Health)
        if not health or not health.is_alive:
            # Skip dead combatants
            self._next_turn(world)
            return

        # Determine if player or enemy turn
        if self.current_actor in self.party_members:
            self.battle_phase = BattlePhase.PLAYER_TURN
            self.event_manager.emit(
                Event(
                    EventType.CUSTOM,
                    {
                        "type": "player_turn_start",
                        "actor_id": self.current_actor.id,
                    },
                )
            )
        else:
            self.battle_phase = BattlePhase.ENEMY_TURN

    def _start_new_round(self, world: World):
        """Start a new battle round"""
        self.battle_turn += 1

        # Reset all combatants
        for entity in self.all_combatants:
            battle_state = entity.get_component(BattleState)
            if battle_state:
                battle_state.has_acted = False
                battle_state.is_defending = False

            # Reduce spell cooldowns
            spell_list = entity.get_component(SpellList)
            if spell_list:
                spell_list.reduce_cooldowns()

        # Execute all pending actions
        self.battle_phase = BattlePhase.EXECUTING_ACTIONS
        self._execute_all_actions(world)

    def _execute_all_actions(self, world: World):
        """Execute all pending actions in turn order"""
        for entity in self.turn_order:
            health = entity.get_component(Health)
            if not health or not health.is_alive:
                continue

            battle_state = entity.get_component(BattleState)
            if not battle_state or not battle_state.pending_action:
                continue

            # Execute action
            self._execute_action(world, entity, battle_state)

        # Check battle end conditions
        if self._check_victory_condition():
            self.battle_phase = BattlePhase.VICTORY
            self.phase_timer = 0.0
        elif self._check_defeat_condition():
            self.battle_phase = BattlePhase.DEFEAT
            self.phase_timer = 0.0
        else:
            # Start next round
            self.current_turn_index = 0
            self._next_turn(world)

    def _execute_action(self, world: World, actor: Entity, battle_state: BattleState):
        """Execute a single action"""
        action = battle_state.pending_action
        target_ids = battle_state.pending_targets

        # Get targets
        targets = [world.get_entity(tid) for tid in target_ids]
        targets = [t for t in targets if t is not None]

        if action == "attack":
            self._execute_attack(actor, targets)
        elif action == "magic":
            self._execute_magic(world, actor, targets)
        elif action == "defend":
            battle_state.is_defending = True
        elif action == "run":
            self._attempt_escape(world, actor)

        # Clear pending action
        battle_state.pending_action = None
        battle_state.pending_targets.clear()

    def _execute_attack(self, attacker: Entity, targets: List[Entity]):
        """Execute physical attack"""
        attacker_stats = attacker.get_component(JRPGStats)

        for target in targets:
            target_health = target.get_component(Health)
            target_stats = target.get_component(JRPGStats)
            target_battle_state = target.get_component(BattleState)

            if not target_health or not target_health.is_alive:
                continue

            # Calculate damage
            damage = 10  # Base damage
            if attacker_stats and target_stats:
                damage = attacker_stats.calculate_physical_damage(target_stats)

            # Apply defense modifier if defending
            if target_battle_state and target_battle_state.is_defending:
                damage = int(damage * 0.5)

            # Apply damage
            target_health.hp -= damage
            if target_health.hp <= 0:
                target_health.hp = 0
                target_health.is_alive = False

            # Emit damage event
            self.event_manager.emit(
                Event(
                    EventType.CUSTOM,
                    {
                        "type": "battle_damage",
                        "attacker_id": attacker.id,
                        "target_id": target.id,
                        "damage": damage,
                        "is_critical": False,
                    },
                )
            )

    def _execute_magic(self, world: World, caster: Entity, targets: List[Entity]):
        """Execute magic spell"""
        # Would integrate with MagicSystem here
        pass

    def _attempt_escape(self, world: World, escaper: Entity) -> bool:
        """Attempt to escape from battle"""
        if not self.can_escape or self.is_boss_battle:
            return False

        # Calculate escape chance (based on speed difference)
        escape_chance = 50.0  # Base 50%

        if random.random() * 100 < escape_chance:
            self.battle_phase = BattlePhase.ESCAPED
            self.event_manager.emit(Event(EventType.CUSTOM, {"type": "battle_escaped"}))
            return True

        return False

    def _check_victory_condition(self) -> bool:
        """Check if all enemies are defeated"""
        for enemy in self.enemies:
            health = enemy.get_component(Health)
            if health and health.is_alive:
                return False
        return True

    def _check_defeat_condition(self) -> bool:
        """Check if all party members are defeated"""
        for member in self.party_members:
            health = member.get_component(Health)
            if health and health.is_alive:
                return False
        return True

    def _update_intro_phase(self, world: World):
        """Update battle intro phase"""
        if self.phase_timer >= self.intro_duration:
            # Start first turn
            self.current_turn_index = -1
            self._next_turn(world)

    def _update_player_turn_phase(self, world: World, delta_time: float):
        """Update player turn phase"""
        # Waiting for player input (handled by UI)
        pass

    def _update_enemy_turn_phase(self, world: World, delta_time: float):
        """Update enemy turn phase"""
        if not self.current_actor:
            return

        # Execute AI decision
        self._execute_enemy_ai(world, self.current_actor)

        # Mark as acted and move to next turn
        battle_state = self.current_actor.get_component(BattleState)
        if battle_state:
            battle_state.has_acted = True

        self._next_turn(world)

    def _execute_enemy_ai(self, world: World, enemy: Entity):
        """Execute enemy AI to choose action"""
        ai = enemy.get_component(BattleAI)
        battle_state = enemy.get_component(BattleState)

        if not battle_state:
            return

        # Simple AI: attack random party member
        alive_party = [
            m for m in self.party_members if m.get_component(Health).is_alive
        ]

        if not alive_party:
            return

        target = random.choice(alive_party)

        # Set pending action
        battle_state.pending_action = "attack"
        battle_state.pending_targets = [target.id]

    def _update_executing_actions_phase(self, world: World, delta_time: float):
        """Update action execution phase"""
        # Actions are executed immediately in _execute_all_actions
        pass

    def _update_victory_phase(self, world: World):
        """Update victory phase"""
        if self.phase_timer >= self.victory_duration:
            # Give rewards
            self._give_rewards(world)
            # End battle
            self.end_battle(world, victory=True)

    def _update_defeat_phase(self, world: World):
        """Update defeat phase"""
        if self.phase_timer >= self.victory_duration:
            # End battle
            self.end_battle(world, victory=False)

    def _give_rewards(self, world: World):
        """Give battle rewards to party"""
        total_exp = 0
        total_gold = 0
        items_gained = []

        # Collect rewards from all defeated enemies
        for enemy in self.enemies:
            rewards = enemy.get_component(BattleRewards)
            if rewards:
                total_exp += rewards.experience
                total_gold += rewards.gold

                # Roll for item drops
                for item_data in rewards.items:
                    chance = item_data.get("chance", 100.0)
                    if random.random() * 100 < chance:
                        items_gained.append(item_data)

        # Emit rewards event
        self.event_manager.emit(
            Event(
                EventType.CUSTOM,
                {
                    "type": "battle_rewards",
                    "experience": total_exp,
                    "gold": total_gold,
                    "items": items_gained,
                },
            )
        )

    def _handle_custom_event(self, event: Event):
        """Handle custom events"""
        pass
