"""
Comprehensive tests for Exploration System

Tests tile-based movement, NPC behavior, interactions, and animations.
"""

from unittest.mock import MagicMock, Mock, call

import pytest

from neonworks.core.ecs import Entity, GridPosition, Transform, World
from neonworks.core.events import Event, EventType
from neonworks.gameplay.movement import (
    AnimationState,
    Collider2D,
    Direction,
    Interactable,
    Movement,
    NPCBehavior,
    TileCollisionMap,
)
from neonworks.systems.exploration import ExplorationSystem


class TestExplorationSystemInit:
    """Test exploration system initialization"""

    def test_init_default(self):
        """Test creating exploration system"""
        input_mgr = Mock()
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        assert system.input_manager is input_mgr
        assert system.event_manager is event_mgr
        assert system.priority == 10
        assert system.tile_size == 32
        assert system.player_entity is None
        assert system.collision_map is None
        assert system.step_count == 0

    def test_set_collision_map(self):
        """Test setting collision map"""
        input_mgr = Mock()
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        collision_map = TileCollisionMap(width=10, height=10)
        system.set_collision_map(collision_map)

        assert system.collision_map is collision_map

    def test_reset_step_counter(self):
        """Test resetting step counter"""
        input_mgr = Mock()
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        system.step_count = 50
        system.reset_step_counter()

        assert system.step_count == 0


class TestPlayerMovement:
    """Test player movement"""

    def test_update_player_movement_no_player(self):
        """Test update with no player entity"""
        input_mgr = Mock()
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        world = World()
        system._update_player_movement(world, 0.016)

        # Should not crash with no player
        assert system.player_entity is None

    def test_update_player_movement_finds_player(self):
        """Test system finds player entity"""
        input_mgr = Mock()
        # Provide some input so the method continues
        input_mgr.is_action_held = Mock(side_effect=lambda action: action == "move_right")
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        world = World()
        # Create entity first, then immediately add tag and components
        # Note: World indexes tags during add_entity, so we need to use world's add_entity
        player = Entity()
        player.tags.add("player")
        player.add_component(GridPosition(grid_x=5, grid_y=5))
        player.add_component(Movement())
        world.add_entity(player)

        system._update_player_movement(world, 0.016)

        assert system.player_entity is player

    def test_get_movement_direction_up(self):
        """Test getting upward movement direction"""
        input_mgr = Mock()
        input_mgr.is_action_held = Mock(side_effect=lambda action: action == "move_up")
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        direction = system._get_movement_direction()

        assert direction == Direction.UP

    def test_get_movement_direction_down(self):
        """Test getting downward movement direction"""
        input_mgr = Mock()
        input_mgr.is_action_held = Mock(side_effect=lambda action: action == "move_down")
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        direction = system._get_movement_direction()

        assert direction == Direction.DOWN

    def test_get_movement_direction_left(self):
        """Test getting leftward movement direction"""
        input_mgr = Mock()
        input_mgr.is_action_held = Mock(side_effect=lambda action: action == "move_left")
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        direction = system._get_movement_direction()

        assert direction == Direction.LEFT

    def test_get_movement_direction_right(self):
        """Test getting rightward movement direction"""
        input_mgr = Mock()
        input_mgr.is_action_held = Mock(side_effect=lambda action: action == "move_right")
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        direction = system._get_movement_direction()

        assert direction == Direction.RIGHT

    def test_get_movement_direction_none(self):
        """Test no movement input"""
        input_mgr = Mock()
        input_mgr.is_action_held = Mock(return_value=False)
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        direction = system._get_movement_direction()

        assert direction is None

    def test_player_movement_blocked_by_collision_map(self):
        """Test player movement blocked by collision map"""
        input_mgr = Mock()
        input_mgr.is_action_held = Mock(side_effect=lambda action: action == "move_right")
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        # Set collision map with blocked tile
        collision_map = TileCollisionMap(width=10, height=10)
        collision_map.set_walkable(6, 5, False)  # Block tile at (6, 5)
        system.set_collision_map(collision_map)

        world = World()
        player = world.create_entity()
        player.add_tag("player")
        player.add_component(GridPosition(grid_x=5, grid_y=5))
        movement = Movement()
        player.add_component(movement)

        system.player_entity = player
        system._update_player_movement(world, 0.016)

        # Movement should not start
        assert not movement.is_moving

    def test_player_movement_starts_successfully(self):
        """Test player movement starts when tile is walkable"""
        input_mgr = Mock()
        input_mgr.is_action_held = Mock(side_effect=lambda action: action == "move_right")
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        world = World()
        player = world.create_entity()
        player.add_tag("player")
        player.add_component(GridPosition(grid_x=5, grid_y=5))
        movement = Movement()
        player.add_component(movement)

        system.player_entity = player
        system._update_player_movement(world, 0.016)

        # Movement should start
        assert movement.is_moving
        assert movement.target_grid_x == 6
        assert movement.target_grid_y == 5
        assert movement.facing == Direction.RIGHT

    def test_player_movement_triggers_callback(self):
        """Test player movement triggers on_move_start callback"""
        input_mgr = Mock()
        input_mgr.is_action_held = Mock(side_effect=lambda action: action == "move_right")
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        world = World()
        player = world.create_entity()
        player.add_tag("player")
        player.add_component(GridPosition(grid_x=5, grid_y=5))

        callback = Mock()
        movement = Movement()
        movement.on_move_start = callback
        player.add_component(movement)

        system.player_entity = player
        system._update_player_movement(world, 0.016)

        # Callback should be triggered
        callback.assert_called_once_with(6, 5)

    def test_player_movement_blocked_triggers_collision_callback(self):
        """Test collision triggers on_collision callback"""
        input_mgr = Mock()
        input_mgr.is_action_held = Mock(side_effect=lambda action: action == "move_right")
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        # Set collision map with blocked tile
        collision_map = TileCollisionMap(width=10, height=10)
        collision_map.set_walkable(6, 5, False)
        system.set_collision_map(collision_map)

        world = World()
        player = world.create_entity()
        player.add_tag("player")
        player.add_component(GridPosition(grid_x=5, grid_y=5))

        callback = Mock()
        movement = Movement()
        movement.on_collision = callback
        player.add_component(movement)

        system.player_entity = player
        system._update_player_movement(world, 0.016)

        # Collision callback should be triggered
        callback.assert_called_once_with(6, 5)

    def test_player_cant_move_while_moving(self):
        """Test player can't accept new input while moving"""
        input_mgr = Mock()
        input_mgr.is_action_held = Mock(side_effect=lambda action: action == "move_right")
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        world = World()
        player = world.create_entity()
        player.add_tag("player")
        player.add_component(GridPosition(grid_x=5, grid_y=5))
        movement = Movement()
        movement.is_moving = True  # Already moving
        movement.target_grid_x = 6
        movement.target_grid_y = 5
        player.add_component(movement)

        system.player_entity = player
        system._update_player_movement(world, 0.016)

        # Target should not change
        assert movement.target_grid_x == 6
        assert movement.target_grid_y == 5

    def test_player_movement_updates_animation_state(self):
        """Test player movement updates animation state"""
        input_mgr = Mock()
        input_mgr.is_action_held = Mock(side_effect=lambda action: action == "move_right")
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        world = World()
        player = world.create_entity()
        player.add_tag("player")
        player.add_component(GridPosition(grid_x=5, grid_y=5))
        player.add_component(Movement())
        anim_state = AnimationState()
        player.add_component(anim_state)

        system.player_entity = player
        system._update_player_movement(world, 0.016)

        assert anim_state.current_state == "walk"
        assert anim_state.current_direction == Direction.RIGHT

    def test_player_no_movement_sets_idle_animation(self):
        """Test no movement sets idle animation"""
        input_mgr = Mock()
        input_mgr.is_action_held = Mock(return_value=False)
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        world = World()
        player = world.create_entity()
        player.add_tag("player")
        player.add_component(GridPosition(grid_x=5, grid_y=5))
        player.add_component(Movement())
        anim_state = AnimationState()
        anim_state.current_state = "walk"
        player.add_component(anim_state)

        system.player_entity = player
        system._update_player_movement(world, 0.016)

        assert anim_state.current_state == "idle"


class TestMovementInterpolation:
    """Test movement interpolation"""

    def test_movement_interpolation_in_progress(self):
        """Test movement interpolation during progress"""
        input_mgr = Mock()
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        world = World()
        entity = world.create_entity()
        entity.add_component(GridPosition(grid_x=5, grid_y=5))
        entity.add_component(Transform(x=160, y=160))  # 5 * 32
        movement = Movement(speed=3.0)
        movement.is_moving = True
        movement.target_grid_x = 6
        movement.target_grid_y = 5
        movement.move_progress = 0.0
        entity.add_component(movement)

        system._update_movement_interpolation(world, 0.1)

        # Progress should update
        assert movement.move_progress == pytest.approx(0.3)  # 0.1 * 3.0
        assert movement.is_moving

        # Transform should interpolate
        transform = entity.get_component(Transform)
        assert transform.x > 160
        assert transform.y == pytest.approx(160)

    def test_movement_interpolation_complete(self):
        """Test movement completes and snaps to grid"""
        input_mgr = Mock()
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        world = World()
        entity = world.create_entity()
        grid_pos = GridPosition(grid_x=5, grid_y=5)
        entity.add_component(grid_pos)
        entity.add_component(Transform(x=160, y=160))
        movement = Movement(speed=3.0)
        movement.is_moving = True
        movement.target_grid_x = 6
        movement.target_grid_y = 5
        movement.move_progress = 0.9
        entity.add_component(movement)

        system._update_movement_interpolation(world, 0.1)

        # Movement should complete
        assert movement.move_progress == 1.0
        assert not movement.is_moving

        # Grid position should update
        assert grid_pos.grid_x == 6
        assert grid_pos.grid_y == 5

        # Transform should snap to target
        transform = entity.get_component(Transform)
        assert transform.x == 192  # 6 * 32
        assert transform.y == 160  # 5 * 32

    def test_movement_complete_triggers_callback(self):
        """Test movement complete triggers on_move_complete callback"""
        input_mgr = Mock()
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        world = World()
        entity = world.create_entity()
        entity.add_component(GridPosition(grid_x=5, grid_y=5))
        entity.add_component(Transform(x=160, y=160))

        callback = Mock()
        movement = Movement(speed=5.0)
        movement.is_moving = True
        movement.target_grid_x = 6
        movement.target_grid_y = 5
        movement.move_progress = 0.9
        movement.on_move_complete = callback
        entity.add_component(movement)

        system._update_movement_interpolation(world, 0.1)

        # Callback should be triggered with final position
        callback.assert_called_once_with(6, 5)

    def test_player_step_counter_increments(self):
        """Test step counter increments for player"""
        input_mgr = Mock()
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        world = World()
        player = world.create_entity()
        player.add_tag("player")
        player.add_component(GridPosition(grid_x=5, grid_y=5))
        player.add_component(Transform(x=160, y=160))
        movement = Movement(speed=5.0)
        movement.is_moving = True
        movement.target_grid_x = 6
        movement.target_grid_y = 5
        movement.move_progress = 0.9
        player.add_component(movement)

        initial_steps = system.step_count
        system._update_movement_interpolation(world, 0.1)

        # Step count should increment
        assert system.step_count == initial_steps + 1

        # Event should be emitted
        event_mgr.emit.assert_called()
        emitted_event = event_mgr.emit.call_args[0][0]
        assert emitted_event.event_type == EventType.CUSTOM
        assert emitted_event.data["type"] == "player_step"
        assert emitted_event.data["steps"] == system.step_count


class TestAnimations:
    """Test animation system"""

    def test_animation_frame_advance(self):
        """Test animation frame advances"""
        input_mgr = Mock()
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        world = World()
        entity = world.create_entity()
        anim_state = AnimationState()
        anim_state.animations = {"walk": [0, 1, 2, 3]}
        anim_state.current_state = "walk"
        anim_state.frame_duration = 0.1
        anim_state.frame_timer = 0.0
        anim_state.frame_index = 0
        entity.add_component(anim_state)

        system._update_animations(world, 0.15)

        # Frame should advance
        assert anim_state.frame_index == 1
        # Timer is reset to 0.0 after frame advance
        assert anim_state.frame_timer == 0.0

    def test_animation_frame_wraps(self):
        """Test animation frame wraps to beginning"""
        input_mgr = Mock()
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        world = World()
        entity = world.create_entity()
        anim_state = AnimationState()
        anim_state.animations = {"walk_down": [0, 1, 2]}
        anim_state.current_state = "walk"
        anim_state.current_direction = Direction.DOWN
        anim_state.frame_duration = 0.1
        anim_state.frame_timer = 0.0
        anim_state.frame_index = 2  # Last frame
        entity.add_component(anim_state)

        system._update_animations(world, 0.15)

        # Frame should wrap to 0
        assert anim_state.frame_index == 0


class TestNPCBehavior:
    """Test NPC behavior"""

    def test_static_npc_does_not_move(self):
        """Test static NPC doesn't move"""
        input_mgr = Mock()
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        world = World()
        npc = world.create_entity()
        npc.add_component(GridPosition(grid_x=10, grid_y=10))
        behavior = NPCBehavior(behavior_type="static")
        npc.add_component(behavior)
        movement = Movement()
        npc.add_component(movement)

        system._update_npcs(world, 0.5)

        # NPC should not move
        assert not movement.is_moving

    def test_wandering_npc_moves_randomly(self):
        """Test wandering NPC moves after interval"""
        input_mgr = Mock()
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        world = World()
        npc = world.create_entity()
        grid_pos = GridPosition(grid_x=5, grid_y=5)
        npc.add_component(grid_pos)
        behavior = NPCBehavior(behavior_type="wander", wander_interval=1.0)
        behavior.wander_timer = 0.9
        npc.add_component(behavior)
        movement = Movement()
        npc.add_component(movement)

        system._update_npcs(world, 0.2)

        # Movement should start (timer crossed interval)
        assert movement.is_moving
        # Target should be adjacent tile
        assert abs(movement.target_grid_x - grid_pos.grid_x) <= 1
        assert abs(movement.target_grid_y - grid_pos.grid_y) <= 1

    def test_wandering_npc_blocked_by_collision(self):
        """Test wandering NPC doesn't move into blocked tile"""
        input_mgr = Mock()
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        # Block all surrounding tiles
        collision_map = TileCollisionMap(width=20, height=20)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                collision_map.set_walkable(5 + dx, 5 + dy, False)
        system.set_collision_map(collision_map)

        world = World()
        npc = world.create_entity()
        npc.add_component(GridPosition(grid_x=5, grid_y=5))
        behavior = NPCBehavior(behavior_type="wander", wander_interval=1.0)
        behavior.wander_timer = 1.5
        npc.add_component(behavior)
        movement = Movement()
        npc.add_component(movement)

        system._update_npcs(world, 0.1)

        # NPC should not move (all tiles blocked)
        assert not movement.is_moving

    def test_patrol_npc_moves_to_next_point(self):
        """Test patrolling NPC moves to next patrol point"""
        input_mgr = Mock()
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        world = World()
        npc = world.create_entity()
        grid_pos = GridPosition(grid_x=5, grid_y=5)
        npc.add_component(grid_pos)
        behavior = NPCBehavior(
            behavior_type="patrol",
            patrol_points=[(5, 5), (8, 5), (8, 8)],
            patrol_loop=True,
        )
        behavior.current_patrol_index = 1  # Target (8, 5)
        npc.add_component(behavior)
        movement = Movement()
        npc.add_component(movement)

        system._update_npcs(world, 0.1)

        # Should move toward (8, 5)
        assert movement.is_moving
        assert movement.target_grid_x == 6  # One step right
        assert movement.target_grid_y == 5

    def test_patrol_npc_loops_at_end(self):
        """Test patrolling NPC loops back to start"""
        input_mgr = Mock()
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        world = World()
        npc = world.create_entity()
        grid_pos = GridPosition(grid_x=8, grid_y=8)  # At last point
        npc.add_component(grid_pos)
        behavior = NPCBehavior(
            behavior_type="patrol",
            patrol_points=[(5, 5), (8, 5), (8, 8)],
            patrol_loop=True,
        )
        behavior.current_patrol_index = 2  # At last point
        npc.add_component(behavior)
        movement = Movement()
        npc.add_component(movement)

        system._update_npcs(world, 0.1)

        # Should advance to next index (wrapping to 0)
        assert behavior.current_patrol_index == 0

    def test_patrol_npc_reverses_at_end_no_loop(self):
        """Test patrolling NPC reverses direction when not looping"""
        input_mgr = Mock()
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        world = World()
        npc = world.create_entity()
        grid_pos = GridPosition(grid_x=8, grid_y=8)  # At last point
        npc.add_component(grid_pos)
        behavior = NPCBehavior(
            behavior_type="patrol",
            patrol_points=[(5, 5), (8, 5), (8, 8)],
            patrol_loop=False,
        )
        behavior.current_patrol_index = 2  # At last point
        npc.add_component(behavior)
        movement = Movement()
        npc.add_component(movement)

        system._update_npcs(world, 0.1)

        # Should reverse to previous point
        assert behavior.current_patrol_index == 1


class TestInteractions:
    """Test interaction system"""

    def test_interaction_with_npc(self):
        """Test player interacting with NPC"""
        input_mgr = Mock()
        input_mgr.is_action_pressed = Mock(return_value=False)
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        world = World()
        player = world.create_entity()
        player.add_tag("player")
        player.add_component(GridPosition(grid_x=5, grid_y=5))
        movement = Movement()
        movement.facing = Direction.RIGHT
        player.add_component(movement)
        system.player_entity = player

        # Create NPC at interact position
        npc = world.create_entity()
        npc.add_component(GridPosition(grid_x=6, grid_y=5))
        callback = Mock()
        interactable = Interactable(
            can_interact=True,
            interaction_type="dialogue",
            dialogue_id="npc_greeting",
        )
        interactable.on_interact = callback
        npc.add_component(interactable)

        system._handle_interaction(world)

        # Interaction callback should be triggered
        callback.assert_called_once_with(player)

        # Event should be emitted
        event_mgr.emit.assert_called()
        emitted_event = event_mgr.emit.call_args[0][0]
        assert emitted_event.event_type == EventType.CUSTOM
        assert emitted_event.data["type"] == "interaction"
        assert emitted_event.data["target_id"] == npc.id
        assert emitted_event.data["interaction_type"] == "dialogue"
        assert emitted_event.data["dialogue_id"] == "npc_greeting"

    def test_interaction_no_target(self):
        """Test interaction with no target"""
        input_mgr = Mock()
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        world = World()
        player = world.create_entity()
        player.add_tag("player")
        player.add_component(GridPosition(grid_x=5, grid_y=5))
        movement = Movement()
        movement.facing = Direction.RIGHT
        player.add_component(movement)
        system.player_entity = player

        system._handle_interaction(world)

        # No event should be emitted
        event_mgr.emit.assert_not_called()

    def test_interaction_with_disabled_interactable(self):
        """Test interaction with disabled interactable"""
        input_mgr = Mock()
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        world = World()
        player = world.create_entity()
        player.add_tag("player")
        player.add_component(GridPosition(grid_x=5, grid_y=5))
        movement = Movement()
        movement.facing = Direction.RIGHT
        player.add_component(movement)
        system.player_entity = player

        # Create interactable that's disabled
        obj = world.create_entity()
        obj.add_component(GridPosition(grid_x=6, grid_y=5))
        callback = Mock()
        interactable = Interactable(can_interact=False)
        interactable.on_interact = callback
        obj.add_component(interactable)

        system._handle_interaction(world)

        # Callback should not be triggered
        callback.assert_not_called()


class TestCollisionDetection:
    """Test collision detection"""

    def test_tile_walkable_no_collision_map(self):
        """Test tile walkable with no collision map"""
        input_mgr = Mock()
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        world = World()

        # Without collision map, tiles are walkable
        assert system._is_tile_walkable(world, 5, 5)

    def test_tile_not_walkable_collision_map(self):
        """Test tile not walkable due to collision map"""
        input_mgr = Mock()
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        collision_map = TileCollisionMap(width=10, height=10)
        collision_map.set_walkable(5, 5, False)
        system.set_collision_map(collision_map)

        world = World()

        assert not system._is_tile_walkable(world, 5, 5)

    def test_tile_blocked_by_solid_entity(self):
        """Test tile blocked by solid entity"""
        input_mgr = Mock()
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        world = World()
        obstacle = world.create_entity()
        obstacle.add_component(GridPosition(grid_x=5, grid_y=5))
        obstacle.add_component(Collider2D(is_solid=True, is_trigger=False))

        assert not system._is_tile_walkable(world, 5, 5)

    def test_tile_walkable_with_trigger_entity(self):
        """Test tile walkable with trigger entity"""
        input_mgr = Mock()
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        world = World()
        trigger = world.create_entity()
        trigger.add_component(GridPosition(grid_x=5, grid_y=5))
        trigger.add_component(Collider2D(is_solid=True, is_trigger=True))

        # Triggers don't block movement
        assert system._is_tile_walkable(world, 5, 5)


class TestFullUpdate:
    """Test full update cycle"""

    def test_update_calls_all_subsystems(self):
        """Test update calls all subsystems"""
        input_mgr = Mock()
        input_mgr.is_action_held = Mock(return_value=False)
        input_mgr.is_action_pressed = Mock(return_value=False)
        event_mgr = Mock()
        system = ExplorationSystem(input_mgr, event_mgr)

        world = World()
        player = Entity()
        player.tags.add("player")
        player.add_component(GridPosition(grid_x=5, grid_y=5))
        player.add_component(Movement())
        player.add_component(Transform(x=160, y=160))
        player.add_component(AnimationState())
        world.add_entity(player)

        system.update(world, 0.016)

        # Should complete without error
        assert system.player_entity is not None


# Run tests with: pytest tests/test_exploration.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
