"""
Exploration System for JRPG-style Tile-based Movement

Handles player movement, NPC interactions, and zone exploration.
"""

from typing import List, Optional, Set, Tuple

import pygame

from gameplay.movement import (
    AnimationState,
    Collider2D,
    Direction,
    Interactable,
    Movement,
    NPCBehavior,
    TileCollisionMap,
)
from neonworks.core.ecs import Entity, GridPosition, System, Transform, World
from neonworks.core.events import Event, EventManager, EventType
from neonworks.input.input_manager import InputManager


class ExplorationSystem(System):
    """
    System for handling tile-based exploration and movement.

    Features:
    - Smooth tile-to-tile movement
    - Collision detection with tiles and entities
    - Interaction with NPCs and objects
    - Animation state management
    """

    def __init__(self, input_manager: InputManager, event_manager: EventManager):
        super().__init__()
        self.priority = 10
        self.input_manager = input_manager
        self.event_manager = event_manager

        # Tile size (should match game config)
        self.tile_size = 32

        # Player entity reference
        self.player_entity: Optional[Entity] = None

        # Collision map cache
        self.collision_map: Optional[TileCollisionMap] = None

        # Step counter for random encounters
        self.step_count = 0

    def update(self, world: World, delta_time: float):
        """Update exploration system"""
        # Update player movement
        self._update_player_movement(world, delta_time)

        # Update NPC behavior
        self._update_npcs(world, delta_time)

        # Update movement animations
        self._update_animations(world, delta_time)

        # Process movement interpolation
        self._update_movement_interpolation(world, delta_time)

        # Check for interactions
        if self.input_manager.is_action_pressed("interact"):
            self._handle_interaction(world)

    def _update_player_movement(self, world: World, delta_time: float):
        """Handle player input and movement"""
        # Find player entity if not cached
        if not self.player_entity:
            player_entities = world.get_entities_with_tag("player")
            if player_entities:
                self.player_entity = player_entities[0]

        if not self.player_entity:
            return

        # Get required components
        grid_pos = self.player_entity.get_component(GridPosition)
        movement = self.player_entity.get_component(Movement)
        anim_state = self.player_entity.get_component(AnimationState)

        if not grid_pos or not movement:
            return

        # If currently moving, don't accept new input
        if movement.is_moving or not movement.can_move:
            return

        # Get movement input
        move_dir = self._get_movement_direction()
        if move_dir is None:
            # Set to idle if animation state exists
            if anim_state:
                anim_state.current_state = "idle"
            return

        # Update facing direction
        movement.facing = move_dir

        # Calculate target position
        dx, dy = move_dir.to_vector()
        target_x = grid_pos.grid_x + dx
        target_y = grid_pos.grid_y + dy

        # Check if target tile is walkable
        if not self._is_tile_walkable(world, target_x, target_y):
            # Collision callback
            if movement.on_collision:
                movement.on_collision(target_x, target_y)

            # Update facing animation
            if anim_state:
                anim_state.current_direction = move_dir
                anim_state.current_state = "idle"
            return

        # Start movement
        movement.is_moving = True
        movement.target_grid_x = target_x
        movement.target_grid_y = target_y
        movement.move_progress = 0.0

        # Update animation state
        if anim_state:
            anim_state.current_state = "walk"
            anim_state.current_direction = move_dir

        # Trigger move start callback
        if movement.on_move_start:
            movement.on_move_start(target_x, target_y)

    def _update_movement_interpolation(self, world: World, delta_time: float):
        """Smoothly interpolate entities moving between tiles"""
        entities = world.get_entities_with_components(GridPosition, Movement, Transform)

        for entity in entities:
            grid_pos = entity.get_component(GridPosition)
            movement = entity.get_component(Movement)
            transform = entity.get_component(Transform)

            if not movement.is_moving:
                continue

            # Update move progress
            movement.move_progress += delta_time * movement.speed

            if movement.move_progress >= 1.0:
                # Movement complete
                movement.move_progress = 1.0
                movement.is_moving = False

                # Update grid position
                old_x, old_y = grid_pos.grid_x, grid_pos.grid_y
                grid_pos.grid_x = movement.target_grid_x
                grid_pos.grid_y = movement.target_grid_y

                # Snap transform to grid position
                transform.x = grid_pos.grid_x * self.tile_size
                transform.y = grid_pos.grid_y * self.tile_size

                # Trigger move complete callback
                if movement.on_move_complete:
                    movement.on_move_complete(grid_pos.grid_x, grid_pos.grid_y)

                # Increment step counter for encounters
                if entity.has_tag("player"):
                    self.step_count += 1
                    self.event_manager.emit(
                        Event(
                            EventType.CUSTOM,
                            {"type": "player_step", "steps": self.step_count},
                        )
                    )
            else:
                # Interpolate position
                start_x = grid_pos.grid_x * self.tile_size
                start_y = grid_pos.grid_y * self.tile_size
                end_x = movement.target_grid_x * self.tile_size
                end_y = movement.target_grid_y * self.tile_size

                transform.x = start_x + (end_x - start_x) * movement.move_progress
                transform.y = start_y + (end_y - start_y) * movement.move_progress

    def _update_animations(self, world: World, delta_time: float):
        """Update animation states"""
        entities = world.get_entities_with_components(AnimationState)

        for entity in entities:
            anim_state = entity.get_component(AnimationState)

            # Update frame timer
            anim_state.frame_timer += delta_time

            # Advance frame if enough time has passed
            if anim_state.frame_timer >= anim_state.frame_duration:
                anim_state.frame_timer = 0.0

                frames = anim_state.get_current_frames()
                if frames:
                    anim_state.frame_index = (anim_state.frame_index + 1) % len(frames)

    def _update_npcs(self, world: World, delta_time: float):
        """Update NPC behavior"""
        npcs = world.get_entities_with_components(NPCBehavior, GridPosition, Movement)

        for npc in npcs:
            behavior = npc.get_component(NPCBehavior)
            grid_pos = npc.get_component(GridPosition)
            movement = npc.get_component(Movement)

            # Skip if NPC is currently moving
            if movement.is_moving:
                continue

            # Handle different behavior types
            if behavior.behavior_type == "static":
                continue  # Static NPCs don't move

            elif behavior.behavior_type == "wander":
                self._update_wander_behavior(
                    npc, behavior, grid_pos, movement, delta_time, world
                )

            elif behavior.behavior_type == "patrol":
                self._update_patrol_behavior(npc, behavior, grid_pos, movement, world)

    def _update_wander_behavior(
        self,
        npc: Entity,
        behavior: NPCBehavior,
        grid_pos: GridPosition,
        movement: Movement,
        delta_time: float,
        world: World,
    ):
        """Update wandering NPC behavior"""
        behavior.wander_timer += delta_time

        if behavior.wander_timer >= behavior.wander_interval:
            behavior.wander_timer = 0.0

            # Pick random direction
            import random

            directions = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]
            move_dir = random.choice(directions)

            dx, dy = move_dir.to_vector()
            target_x = grid_pos.grid_x + dx
            target_y = grid_pos.grid_y + dy

            # Check if walkable
            if self._is_tile_walkable(world, target_x, target_y):
                # Start movement
                movement.is_moving = True
                movement.target_grid_x = target_x
                movement.target_grid_y = target_y
                movement.move_progress = 0.0
                movement.facing = move_dir
                behavior.sprite_facing = move_dir

    def _update_patrol_behavior(
        self,
        npc: Entity,
        behavior: NPCBehavior,
        grid_pos: GridPosition,
        movement: Movement,
        world: World,
    ):
        """Update patrolling NPC behavior"""
        if not behavior.patrol_points:
            return

        # Get current patrol target
        target_point = behavior.patrol_points[behavior.current_patrol_index]
        target_x, target_y = target_point

        # Check if at patrol point
        if grid_pos.grid_x == target_x and grid_pos.grid_y == target_y:
            # Move to next patrol point
            if behavior.patrol_loop:
                behavior.current_patrol_index = (
                    behavior.current_patrol_index + 1
                ) % len(behavior.patrol_points)
            else:
                # Reverse direction at ends
                if behavior.current_patrol_index >= len(behavior.patrol_points) - 1:
                    behavior.current_patrol_index = len(behavior.patrol_points) - 2
                elif behavior.current_patrol_index <= 0:
                    behavior.current_patrol_index = 1
            return

        # Move toward patrol point (simple pathfinding)
        dx = target_x - grid_pos.grid_x
        dy = target_y - grid_pos.grid_y

        # Prefer horizontal movement
        if abs(dx) > 0:
            move_dir = Direction.RIGHT if dx > 0 else Direction.LEFT
            new_x = grid_pos.grid_x + (1 if dx > 0 else -1)
            new_y = grid_pos.grid_y
        elif abs(dy) > 0:
            move_dir = Direction.DOWN if dy > 0 else Direction.UP
            new_x = grid_pos.grid_x
            new_y = grid_pos.grid_y + (1 if dy > 0 else -1)
        else:
            return

        # Check if walkable
        if self._is_tile_walkable(world, new_x, new_y):
            movement.is_moving = True
            movement.target_grid_x = new_x
            movement.target_grid_y = new_y
            movement.move_progress = 0.0
            movement.facing = move_dir
            behavior.sprite_facing = move_dir

    def _handle_interaction(self, world: World):
        """Handle player interaction with nearby objects/NPCs"""
        if not self.player_entity:
            return

        player_grid = self.player_entity.get_component(GridPosition)
        player_movement = self.player_entity.get_component(Movement)

        if not player_grid or not player_movement:
            return

        # Get tile player is facing
        dx, dy = player_movement.facing.to_vector()
        interact_x = player_grid.grid_x + dx
        interact_y = player_grid.grid_y + dy

        # Find interactable entities at that position
        interactables = world.get_entities_with_components(Interactable, GridPosition)

        for entity in interactables:
            interactable = entity.get_component(Interactable)
            grid_pos = entity.get_component(GridPosition)

            if not interactable.can_interact:
                continue

            # Check if at interact position
            if grid_pos.grid_x == interact_x and grid_pos.grid_y == interact_y:
                # Trigger interaction
                if interactable.on_interact:
                    interactable.on_interact(self.player_entity)

                # Emit interaction event
                self.event_manager.emit(
                    Event(
                        EventType.CUSTOM,
                        {
                            "type": "interaction",
                            "player_id": self.player_entity.id,
                            "target_id": entity.id,
                            "interaction_type": interactable.interaction_type,
                            "dialogue_id": interactable.dialogue_id,
                        },
                    )
                )
                return

    def _get_movement_direction(self) -> Optional[Direction]:
        """Get movement direction from input"""
        if self.input_manager.is_action_held("move_up"):
            return Direction.UP
        elif self.input_manager.is_action_held("move_down"):
            return Direction.DOWN
        elif self.input_manager.is_action_held("move_left"):
            return Direction.LEFT
        elif self.input_manager.is_action_held("move_right"):
            return Direction.RIGHT
        return None

    def _is_tile_walkable(self, world: World, x: int, y: int) -> bool:
        """Check if tile is walkable"""
        # Check collision map
        if self.collision_map and not self.collision_map.is_walkable(x, y):
            return False

        # Check for solid entities at position
        entities = world.get_entities_with_components(GridPosition, Collider2D)
        for entity in entities:
            grid_pos = entity.get_component(GridPosition)
            collider = entity.get_component(Collider2D)

            if grid_pos.grid_x == x and grid_pos.grid_y == y:
                if collider.is_solid and not collider.is_trigger:
                    return False

        return True

    def set_collision_map(self, collision_map: TileCollisionMap):
        """Set the collision map for the current zone"""
        self.collision_map = collision_map

    def reset_step_counter(self):
        """Reset step counter (e.g., when entering safe zone)"""
        self.step_count = 0
