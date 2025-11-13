"""
Comprehensive tests for Systems module

Tests TurnSystem, JRPGBattleSystem, PuzzleSystem, and related game mechanics.
"""

from unittest.mock import Mock, MagicMock, patch
import random

import pytest

from neonworks.core.ecs import Entity, World, TurnActor, GridPosition, Transform
from neonworks.core.events import EventManager, Event, EventType
from neonworks.gameplay.combat import Health, Team, TeamComponent
from neonworks.gameplay.jrpg_combat import (
    BattleState,
    JRPGStats,
    MagicPoints,
    PartyMember,
    BattleAI,
    BattleRewards,
    BattleCommand,
    SpellList,
)
from neonworks.gameplay.movement import Movement, Direction, Collider2D
from neonworks.gameplay.puzzle_objects import (
    Switch,
    Door,
    PressurePlate,
    PushableBlock,
    TeleportPad,
    Chest,
    PuzzleController,
)
from systems.turn_system import TurnSystem
from systems.jrpg_battle_system import JRPGBattleSystem, BattlePhase
from systems.puzzle_system import PuzzleSystem


@pytest.fixture
def world():
    """Create a test world"""
    return World()


@pytest.fixture
def event_manager():
    """Create an event manager"""
    return EventManager()


@pytest.fixture
def turn_system():
    """Create a turn system"""
    return TurnSystem()


@pytest.fixture
def jrpg_battle_system(event_manager):
    """Create a JRPG battle system"""
    return JRPGBattleSystem(event_manager)


@pytest.fixture
def puzzle_system(event_manager):
    """Create a puzzle system"""
    return PuzzleSystem(event_manager)


# ===========================
# TurnSystem Tests
# ===========================


class TestTurnSystem:
    """Test TurnSystem"""

    def test_turn_system_creation(self, turn_system):
        """Test creating turn system"""
        assert turn_system.priority == -100
        assert turn_system.turn_order == []
        assert turn_system.current_turn_index == 0
        assert turn_system.turn_number == 1
        assert not turn_system.is_player_turn

    def test_build_turn_order(self, world, turn_system):
        """Test building turn order based on initiative"""
        # Create entities with different initiatives
        e1 = world.create_entity()
        e1.add_component(TurnActor(initiative=5, max_action_points=3))

        e2 = world.create_entity()
        e2.add_component(TurnActor(initiative=10, max_action_points=3))

        e3 = world.create_entity()
        e3.add_component(TurnActor(initiative=7, max_action_points=3))

        # Update should build turn order
        turn_system.update(world, 0.016)

        # Should be sorted by initiative (highest first)
        assert len(turn_system.turn_order) == 3
        assert turn_system.turn_order[0].get_component(TurnActor).initiative == 10
        assert turn_system.turn_order[1].get_component(TurnActor).initiative == 7
        assert turn_system.turn_order[2].get_component(TurnActor).initiative == 5

    def test_start_turn(self, world, turn_system):
        """Test starting a turn"""
        entity = world.create_entity()
        actor = TurnActor(initiative=5, max_action_points=3)
        actor.action_points = 0
        actor.has_acted = True
        entity.add_component(actor)
        entity.add_tag("player")

        turn_system.turn_order = [entity]
        turn_system.current_turn_index = 0

        turn_system.start_turn()

        # Should reset action points and has_acted
        assert actor.action_points == 3
        assert not actor.has_acted
        assert turn_system.is_player_turn

    def test_end_turn(self, world, turn_system):
        """Test ending a turn"""
        e1 = world.create_entity()
        e1.add_component(TurnActor(initiative=5, max_action_points=3))

        e2 = world.create_entity()
        e2.add_component(TurnActor(initiative=10, max_action_points=3))

        turn_system.turn_order = [e2, e1]
        turn_system.current_turn_index = 0
        turn_system.turn_number = 1

        turn_system.end_turn()

        # Should advance to next entity
        assert turn_system.current_turn_index == 1

        turn_system.end_turn()

        # Should wrap around and increment turn number
        assert turn_system.current_turn_index == 0
        assert turn_system.turn_number == 2

    def test_use_action_points(self, world, turn_system):
        """Test using action points"""
        entity = world.create_entity()
        actor = TurnActor(initiative=5, max_action_points=5)
        actor.action_points = 5
        entity.add_component(actor)

        # Use 3 points
        result = turn_system.use_action_points(entity, 3)
        assert result
        assert actor.action_points == 2

        # Try to use more than available
        result = turn_system.use_action_points(entity, 3)
        assert not result
        assert actor.action_points == 2

    def test_add_to_turn_order(self, world, turn_system):
        """Test adding entity to turn order"""
        e1 = world.create_entity()
        e1.add_component(TurnActor(initiative=5, max_action_points=3))

        e2 = world.create_entity()
        e2.add_component(TurnActor(initiative=10, max_action_points=3))

        turn_system.turn_order = [e1]

        turn_system.add_to_turn_order(e2)

        # Should insert based on initiative
        assert len(turn_system.turn_order) == 2
        assert turn_system.turn_order[0] == e2  # Higher initiative

    def test_remove_from_turn_order(self, world, turn_system):
        """Test removing entity from turn order"""
        e1 = world.create_entity()
        e1.add_component(TurnActor(initiative=5, max_action_points=3))

        e2 = world.create_entity()
        e2.add_component(TurnActor(initiative=10, max_action_points=3))

        turn_system.turn_order = [e2, e1]
        turn_system.current_turn_index = 1

        turn_system.remove_from_turn_order(e1)

        assert len(turn_system.turn_order) == 1
        assert turn_system.turn_order[0] == e2

    def test_get_current_actor(self, world, turn_system):
        """Test getting current actor"""
        entity = world.create_entity()
        entity.add_component(TurnActor(initiative=5, max_action_points=3))

        turn_system.turn_order = [entity]
        turn_system.current_turn_index = 0

        current = turn_system.get_current_actor()
        assert current == entity


# ===========================
# JRPGBattleSystem Tests
# ===========================


class TestJRPGBattleSystem:
    """Test JRPGBattleSystem"""

    def test_battle_system_creation(self, jrpg_battle_system):
        """Test creating battle system"""
        assert jrpg_battle_system.priority == 30
        assert not jrpg_battle_system.in_battle
        assert jrpg_battle_system.battle_phase == BattlePhase.INTRO
        assert jrpg_battle_system.can_escape

    def test_start_battle(self, world, jrpg_battle_system):
        """Test starting a battle"""
        # Create party
        hero = world.create_entity()
        hero.add_component(Health(max_hp=100))
        hero.add_component(JRPGStats(level=1, strength=10, defense=5, speed=8))

        # Create enemies
        enemy = world.create_entity()
        enemy.add_component(Health(max_hp=50))
        enemy.add_component(JRPGStats(level=1, strength=8, defense=3, speed=5))

        jrpg_battle_system.start_battle(
            world, party=[hero], enemies=[enemy], can_escape=True, is_boss=False
        )

        assert jrpg_battle_system.in_battle
        assert jrpg_battle_system.battle_phase == BattlePhase.INTRO
        assert len(jrpg_battle_system.party_members) == 1
        assert len(jrpg_battle_system.enemies) == 1
        assert len(jrpg_battle_system.turn_order) > 0

    def test_calculate_turn_order(self, world, jrpg_battle_system):
        """Test turn order calculation"""
        # Create combatants with different speeds
        fast = world.create_entity()
        fast.add_component(Health(max_hp=100))
        fast.add_component(JRPGStats(level=1, strength=10, defense=5, speed=20))

        slow = world.create_entity()
        slow.add_component(Health(max_hp=100))
        slow.add_component(JRPGStats(level=1, strength=10, defense=5, speed=5))

        jrpg_battle_system.all_combatants = [slow, fast]

        # Mock random for consistent results
        with patch("random.randint", return_value=0):
            jrpg_battle_system._calculate_turn_order()

        # Fast entity should go first
        assert jrpg_battle_system.turn_order[0] == fast

    def test_check_victory_condition(self, world, jrpg_battle_system):
        """Test victory condition"""
        enemy = world.create_entity()
        health = Health(max_hp=50)
        health.hp = 0
        health.is_alive = False
        enemy.add_component(health)

        jrpg_battle_system.enemies = [enemy]

        assert jrpg_battle_system._check_victory_condition()

    def test_check_defeat_condition(self, world, jrpg_battle_system):
        """Test defeat condition"""
        hero = world.create_entity()
        health = Health(max_hp=100)
        health.hp = 0
        health.is_alive = False
        hero.add_component(health)

        jrpg_battle_system.party_members = [hero]

        assert jrpg_battle_system._check_defeat_condition()

    def test_execute_attack(self, world, jrpg_battle_system):
        """Test executing an attack"""
        attacker = world.create_entity()
        attacker.add_component(JRPGStats(level=1, strength=15, defense=5, speed=10))

        target = world.create_entity()
        target.add_component(Health(max_hp=50, hp=50))
        target.add_component(JRPGStats(level=1, strength=5, defense=3, speed=5))
        target.add_component(BattleState())

        initial_hp = target.get_component(Health).hp

        jrpg_battle_system._execute_attack(attacker, [target])

        # Target should have taken damage
        assert target.get_component(Health).hp < initial_hp

    def test_execute_attack_with_defend(self, world, jrpg_battle_system):
        """Test attack on defending target"""
        attacker = world.create_entity()
        attacker.add_component(JRPGStats(level=1, strength=15, defense=5, speed=10))

        target = world.create_entity()
        target.add_component(Health(max_hp=50, hp=50))
        target.add_component(JRPGStats(level=1, strength=5, defense=3, speed=5))
        battle_state = BattleState()
        battle_state.is_defending = True
        target.add_component(battle_state)

        # Execute two attacks: one normal, one defended
        target_normal = world.create_entity()
        target_normal.add_component(Health(max_hp=50, hp=50))
        target_normal.add_component(JRPGStats(level=1, strength=5, defense=3, speed=5))
        target_normal.add_component(BattleState())

        jrpg_battle_system._execute_attack(attacker, [target_normal])
        normal_damage = 50 - target_normal.get_component(Health).hp

        jrpg_battle_system._execute_attack(attacker, [target])
        defended_damage = 50 - target.get_component(Health).hp

        # Defended damage should be less than normal damage
        assert defended_damage < normal_damage

    def test_attempt_escape_success(self, world, jrpg_battle_system):
        """Test successful escape"""
        entity = world.create_entity()

        jrpg_battle_system.can_escape = True
        jrpg_battle_system.is_boss_battle = False

        with patch("random.random", return_value=0.1):  # 10% - should succeed
            result = jrpg_battle_system._attempt_escape(world, entity)
            assert result
            assert jrpg_battle_system.battle_phase == BattlePhase.ESCAPED

    def test_attempt_escape_boss_battle(self, world, jrpg_battle_system):
        """Test escape from boss battle (should fail)"""
        entity = world.create_entity()

        jrpg_battle_system.can_escape = False
        jrpg_battle_system.is_boss_battle = True

        result = jrpg_battle_system._attempt_escape(world, entity)
        assert not result

    def test_end_battle(self, world, jrpg_battle_system):
        """Test ending battle"""
        hero = world.create_entity()
        enemy = world.create_entity()

        jrpg_battle_system.in_battle = True
        jrpg_battle_system.party_members = [hero]
        jrpg_battle_system.enemies = [enemy]
        jrpg_battle_system.turn_order = [hero, enemy]

        jrpg_battle_system.end_battle(world, victory=True)

        assert not jrpg_battle_system.in_battle
        assert len(jrpg_battle_system.party_members) == 0
        assert len(jrpg_battle_system.enemies) == 0


# ===========================
# PuzzleSystem Tests
# ===========================


class TestPuzzleSystem:
    """Test PuzzleSystem"""

    def test_puzzle_system_creation(self, puzzle_system):
        """Test creating puzzle system"""
        assert puzzle_system.priority == 25
        assert puzzle_system.puzzle_states == {}

    def test_activate_toggle_switch(self, world, puzzle_system):
        """Test activating a toggle switch"""
        switch_entity = world.create_entity()
        switch = Switch(switch_type="toggle")
        switch.is_active = False
        switch_entity.add_component(switch)

        puzzle_system.activate_switch(world, switch_entity)

        assert switch.is_active

        # Toggle again
        puzzle_system.activate_switch(world, switch_entity)
        assert not switch.is_active

    def test_activate_one_time_switch(self, world, puzzle_system):
        """Test activating a one-time switch"""
        switch_entity = world.create_entity()
        switch = Switch(switch_type="one-time")
        switch.is_active = False
        switch.is_one_time = True
        switch_entity.add_component(switch)

        puzzle_system.activate_switch(world, switch_entity)
        assert switch.is_active

        # Try to activate again - should not toggle
        puzzle_system.activate_switch(world, switch_entity)
        assert switch.is_active

    def test_activate_switch_with_target(self, world, puzzle_system):
        """Test switch activating target door"""
        door_entity = world.create_entity()
        door = Door()
        door.is_open = False
        door_entity.add_component(door)
        door_entity.add_component(Collider2D(is_solid=True))

        switch_entity = world.create_entity()
        switch = Switch(switch_type="toggle")
        switch.target_ids = [door_entity.id]
        switch_entity.add_component(switch)

        puzzle_system.activate_switch(world, switch_entity)

        # Door should open
        assert door.is_open
        assert not door_entity.get_component(Collider2D).is_solid

    def test_push_block(self, world, puzzle_system):
        """Test pushing a block"""
        block = world.create_entity()
        block.add_component(PushableBlock())
        block.add_component(GridPosition(grid_x=5, grid_y=5))
        block.add_component(Movement())

        # Push right
        result = puzzle_system.push_block(world, block, Direction.RIGHT)

        assert result
        assert block.get_component(GridPosition).grid_x == 6

    def test_push_block_into_wall(self, world, puzzle_system):
        """Test pushing block into wall (should fail)"""
        block = world.create_entity()
        block.add_component(PushableBlock())
        block.add_component(GridPosition(grid_x=5, grid_y=5))
        block.add_component(Movement())

        # Create wall
        wall = world.create_entity()
        wall.add_component(GridPosition(grid_x=6, grid_y=5))
        wall.add_component(Collider2D(is_solid=True))

        # Try to push right into wall
        result = puzzle_system.push_block(world, block, Direction.RIGHT)

        assert not result
        assert block.get_component(GridPosition).grid_x == 5

    def test_open_door(self, world, puzzle_system):
        """Test opening a door"""
        door_entity = world.create_entity()
        door_entity.add_component(Door())
        door_entity.add_component(Collider2D(is_solid=True))

        puzzle_system.open_door(world, door_entity)

        door = door_entity.get_component(Door)
        collider = door_entity.get_component(Collider2D)

        assert door.is_open
        assert not collider.is_solid

    def test_open_locked_door(self, world, puzzle_system):
        """Test opening locked door (should fail)"""
        door_entity = world.create_entity()
        door = Door()
        door.is_locked = True
        door_entity.add_component(door)
        door_entity.add_component(Collider2D(is_solid=True))

        puzzle_system.open_door(world, door_entity)

        # Door should remain closed
        assert not door.is_open
        assert door_entity.get_component(Collider2D).is_solid

    def test_close_door(self, world, puzzle_system):
        """Test closing a door"""
        door_entity = world.create_entity()
        door = Door()
        door.is_open = True
        door_entity.add_component(door)
        door_entity.add_component(Collider2D(is_solid=False))

        puzzle_system.close_door(world, door_entity)

        assert not door.is_open
        assert door_entity.get_component(Collider2D).is_solid

    def test_teleport_entity(self, world, puzzle_system):
        """Test teleporting an entity"""
        entity = world.create_entity()
        entity.add_component(GridPosition(grid_x=5, grid_y=5))
        entity.add_component(Transform(x=160, y=160))

        telepad = world.create_entity()
        teleport = TeleportPad(target_x=10, target_y=10)
        teleport.is_active = True
        telepad.add_component(teleport)

        puzzle_system.teleport_entity(world, entity, telepad)

        grid_pos = entity.get_component(GridPosition)
        transform = entity.get_component(Transform)

        assert grid_pos.grid_x == 10
        assert grid_pos.grid_y == 10
        assert transform.x == 320
        assert transform.y == 320

    def test_open_chest(self, world, puzzle_system):
        """Test opening a chest"""
        chest_entity = world.create_entity()
        chest = Chest()
        chest.gold = 100
        chest.items = ["potion", "key"]
        chest_entity.add_component(chest)

        player = world.create_entity()

        result = puzzle_system.open_chest(world, chest_entity, player)

        assert result
        assert chest.is_open

    def test_open_locked_chest(self, world, puzzle_system):
        """Test opening locked chest (should fail)"""
        chest_entity = world.create_entity()
        chest = Chest()
        chest.is_locked = True
        chest_entity.add_component(chest)

        player = world.create_entity()

        result = puzzle_system.open_chest(world, chest_entity, player)

        assert not result
        assert not chest.is_open

    def test_pressure_plate_activation(self, world, puzzle_system):
        """Test pressure plate activation"""
        plate_entity = world.create_entity()
        plate = PressurePlate()
        plate.required_weight = 1
        plate.can_activate_by_player = True
        plate_entity.add_component(plate)
        plate_entity.add_component(GridPosition(grid_x=5, grid_y=5))

        # Create player at same position
        player = world.create_entity()
        player.add_component(GridPosition(grid_x=5, grid_y=5))
        player.add_tag("player")

        puzzle_system._update_pressure_plates(world)

        assert plate.is_pressed
        assert plate.current_weight == 1

    def test_pressure_plate_with_block(self, world, puzzle_system):
        """Test pressure plate with pushable block"""
        plate_entity = world.create_entity()
        plate = PressurePlate()
        plate.required_weight = 1
        plate.can_activate_by_objects = True
        plate_entity.add_component(plate)
        plate_entity.add_component(GridPosition(grid_x=5, grid_y=5))

        # Create block at same position
        block = world.create_entity()
        block.add_component(GridPosition(grid_x=5, grid_y=5))
        block.add_component(PushableBlock())

        puzzle_system._update_pressure_plates(world)

        assert plate.is_pressed

    def test_pressure_plate_stays_pressed(self, world, puzzle_system):
        """Test pressure plate that stays pressed"""
        plate_entity = world.create_entity()
        plate = PressurePlate()
        plate.required_weight = 1
        plate.can_activate_by_player = True
        plate.stays_pressed = True
        plate_entity.add_component(plate)
        plate_entity.add_component(GridPosition(grid_x=5, grid_y=5))

        # Activate with player
        player = world.create_entity()
        player.add_component(GridPosition(grid_x=5, grid_y=5))
        player.add_tag("player")

        puzzle_system._update_pressure_plates(world)
        assert plate.is_pressed

        # Move player away
        player.get_component(GridPosition).grid_x = 10

        puzzle_system._update_pressure_plates(world)

        # Should still be pressed
        assert plate.is_pressed

    def test_save_load_puzzle_state(self, puzzle_system):
        """Test saving and loading puzzle state"""
        state = {"switch_1": True, "door_2": "open"}

        puzzle_system.save_puzzle_state("dungeon_1", "puzzle_room", state)

        loaded_state = puzzle_system.load_puzzle_state("dungeon_1", "puzzle_room")

        assert loaded_state == state

    def test_puzzle_controller_solve(self, world, puzzle_system):
        """Test puzzle controller solving"""
        controller_entity = world.create_entity()
        controller = PuzzleController(puzzle_id="test_puzzle")
        controller.check_solution = Mock(return_value=True)
        controller_entity.add_component(controller)

        puzzle_system._update_puzzle_controllers(world)

        assert controller.is_solved
