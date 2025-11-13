"""
Custom systems for Simple RPG example.

This file demonstrates how to create custom systems that implement game logic.
Systems process entities with specific components each frame.
"""

import math

import pygame

from neonworks.core.ecs import Entity, Health, System, Transform, World
from neonworks.core.events import Event, EventManager, EventType

from .components import (
    AIController,
    AIState,
    CombatStats,
    GameScreen,
    GameStats,
    PlayerController,
    ScreenState,
    UIHealthBar,
    Velocity,
)

# ============================================================================
# Input System - Priority: 0 (runs first)
# ============================================================================


class PlayerInputSystem(System):
    """
    Processes keyboard input and controls the player entity.

    This system:
    1. Finds the entity with PlayerController component
    2. Reads keyboard input each frame
    3. Updates the entity's velocity based on input
    4. Handles attack input

    Priority: 0 (runs before movement to ensure input is processed first)
    """

    def __init__(self):
        super().__init__()
        self.priority = 0

    def update(self, world: World, delta_time: float):
        # Find player entity (should only be one)
        players = world.get_entities_with_tag("player")
        if not players:
            return

        player = players[0]

        # Player must have these components
        if not player.has_components(Transform, PlayerController, Velocity):
            return

        controller = player.get_component(PlayerController)
        velocity = player.get_component(Velocity)

        # Update attack cooldown
        if controller.attack_cooldown > 0:
            controller.attack_cooldown -= delta_time

        # Get keyboard state
        keys = pygame.key.get_pressed()

        # Calculate movement direction from input
        dx, dy = 0, 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1

        # Normalize diagonal movement so speed is consistent
        if dx != 0 or dy != 0:
            length = math.sqrt(dx * dx + dy * dy)
            dx /= length
            dy /= length

        # Set velocity based on input and player speed
        velocity.dx = dx * controller.speed
        velocity.dy = dy * controller.speed

        # Handle attack input (SPACE key)
        if keys[pygame.K_SPACE] and controller.attack_cooldown <= 0:
            self._handle_attack(world, player)
            controller.attack_cooldown = 1.0  # 1 second cooldown

    def _handle_attack(self, world: World, player: Entity):
        """Handle player attack."""
        player_transform = player.get_component(Transform)
        combat_stats = player.get_component(CombatStats)

        if not combat_stats:
            return

        # Find enemies in range
        for entity in world.get_entities_with_tag("enemy"):
            if not entity.has_components(Transform, Health):
                continue

            enemy_transform = entity.get_component(Transform)

            # Calculate distance to enemy
            distance = self._distance(player_transform, enemy_transform)

            # Attack if in range
            if distance <= combat_stats.attack_range:
                enemy_health = entity.get_component(Health)
                enemy_health.current -= combat_stats.attack_damage

                # Visual feedback: print to console
                print(
                    f"Player attacks enemy! Damage: {combat_stats.attack_damage}, "
                    f"Enemy HP: {enemy_health.current}/{enemy_health.maximum}"
                )

    def _distance(self, transform1: Transform, transform2: Transform) -> float:
        """Calculate distance between two transforms."""
        dx = transform2.x - transform1.x
        dy = transform2.y - transform1.y
        return math.sqrt(dx * dx + dy * dy)


# ============================================================================
# Movement System - Priority: 10
# ============================================================================


class MovementSystem(System):
    """
    Updates entity positions based on their velocity.

    This system:
    1. Queries all entities with Transform and Velocity components
    2. Updates position based on velocity * delta_time
    3. Clamps entities to screen bounds

    Priority: 10 (runs after input, before AI and combat)
    """

    def __init__(self, screen_width: int = 800, screen_height: int = 600):
        super().__init__()
        self.priority = 10
        self.screen_width = screen_width
        self.screen_height = screen_height

    def update(self, world: World, delta_time: float):
        # Get all entities that can move
        for entity in world.get_entities_with_components(Transform, Velocity):
            transform = entity.get_component(Transform)
            velocity = entity.get_component(Velocity)

            # Update position based on velocity and time
            # This makes movement frame-rate independent
            transform.x += velocity.dx * delta_time
            transform.y += velocity.dy * delta_time

            # Clamp to screen bounds (with 16px margin for entity size)
            margin = 16
            transform.x = max(margin, min(transform.x, self.screen_width - margin))
            transform.y = max(margin, min(transform.y, self.screen_height - margin))


# ============================================================================
# AI System - Priority: 20
# ============================================================================


class AISystem(System):
    """
    Controls enemy AI behavior using a state machine.

    AI States:
    - IDLE: Enemy stands still until player is detected
    - CHASE: Enemy moves towards player
    - ATTACK: Enemy is in range and attacks player

    Priority: 20 (runs after movement, before combat)
    """

    def __init__(self):
        super().__init__()
        self.priority = 20

    def update(self, world: World, delta_time: float):
        # Get player position for AI to track
        player = self._get_player(world)
        if not player or not player.has_component(Transform):
            return

        player_transform = player.get_component(Transform)

        # Update each AI-controlled entity
        for entity in world.get_entities_with_component(AIController):
            if not entity.has_components(Transform, AIController):
                continue

            ai = entity.get_component(AIController)
            transform = entity.get_component(Transform)

            # Set target to player
            ai.target_entity_id = player.id

            # Calculate distance to player
            distance = self._distance(transform, player_transform)

            # State machine transitions
            self._update_state(ai, distance)

            # Execute state behavior
            if ai.state == AIState.IDLE:
                self._idle_behavior(entity)
            elif ai.state == AIState.CHASE:
                self._chase_behavior(entity, player_transform, delta_time)
            elif ai.state == AIState.ATTACK:
                self._attack_behavior(entity, player, delta_time, world)

    def _update_state(self, ai: AIController, distance: float):
        """Update AI state based on distance to player."""
        combat_range = 40.0  # Distance at which AI attacks

        if ai.state == AIState.IDLE:
            if distance < ai.detection_range:
                ai.state = AIState.CHASE
                print(f"Enemy detected player! Entering CHASE state")

        elif ai.state == AIState.CHASE:
            if distance > ai.detection_range * 1.5:
                ai.state = AIState.IDLE
                print(f"Enemy lost player. Returning to IDLE")
            elif distance < combat_range:
                ai.state = AIState.ATTACK
                print(f"Enemy in attack range! Entering ATTACK state")

        elif ai.state == AIState.ATTACK:
            if distance > combat_range * 1.5:
                ai.state = AIState.CHASE
                print(f"Player out of range. Returning to CHASE")

    def _idle_behavior(self, entity: Entity):
        """IDLE: Stand still."""
        # Clear velocity
        if entity.has_component(Velocity):
            velocity = entity.get_component(Velocity)
            velocity.dx = 0
            velocity.dy = 0

    def _chase_behavior(
        self, entity: Entity, target_transform: Transform, delta_time: float
    ):
        """CHASE: Move towards player."""
        ai = entity.get_component(AIController)
        transform = entity.get_component(Transform)

        # Calculate direction to target
        dx = target_transform.x - transform.x
        dy = target_transform.y - transform.y

        # Normalize direction
        length = math.sqrt(dx * dx + dy * dy)
        if length > 0:
            dx /= length
            dy /= length

            # Update position directly (or set velocity if entity has it)
            if entity.has_component(Velocity):
                velocity = entity.get_component(Velocity)
                velocity.dx = dx * ai.movement_speed
                velocity.dy = dy * ai.movement_speed
            else:
                transform.x += dx * ai.movement_speed * delta_time
                transform.y += dy * ai.movement_speed * delta_time

    def _attack_behavior(
        self, entity: Entity, target: Entity, delta_time: float, world: World
    ):
        """ATTACK: Stop moving and attack player."""
        # Stop moving
        if entity.has_component(Velocity):
            velocity = entity.get_component(Velocity)
            velocity.dx = 0
            velocity.dy = 0

        # Attack with cooldown
        combat_stats = entity.get_component(CombatStats)
        if not combat_stats:
            return

        # Simple cooldown system using a stored attribute
        if not hasattr(entity, "_attack_timer"):
            entity._attack_timer = 0

        entity._attack_timer -= delta_time
        if entity._attack_timer <= 0:
            # Perform attack
            target_health = target.get_component(Health)
            if target_health:
                target_health.current -= combat_stats.attack_damage
                print(
                    f"Enemy attacks player! Damage: {combat_stats.attack_damage}, "
                    f"Player HP: {target_health.current}/{target_health.maximum}"
                )

            entity._attack_timer = combat_stats.attack_cooldown_duration

    def _get_player(self, world: World) -> Entity:
        """Get the player entity."""
        players = world.get_entities_with_tag("player")
        return players[0] if players else None

    def _distance(self, transform1: Transform, transform2: Transform) -> float:
        """Calculate distance between two transforms."""
        dx = transform2.x - transform1.x
        dy = transform2.y - transform1.y
        return math.sqrt(dx * dx + dy * dy)


# ============================================================================
# Cleanup System - Priority: 50
# ============================================================================


class CleanupSystem(System):
    """
    Removes dead entities and updates game statistics.

    This system:
    1. Finds entities with Health <= 0
    2. Removes them from the world
    3. Updates player statistics (enemies defeated, score, etc.)

    Priority: 50 (runs after combat)
    """

    def __init__(self):
        super().__init__()
        self.priority = 50

    def update(self, world: World, delta_time: float):
        entities_to_remove = []

        # Find dead entities
        for entity in world.get_entities_with_component(Health):
            health = entity.get_component(Health)

            if health.current <= 0:
                entities_to_remove.append(entity)

        # Remove dead entities
        for entity in entities_to_remove:
            # Update player stats if an enemy died
            if entity.has_tag("enemy"):
                self._on_enemy_defeated(world)
                print(f"Enemy defeated!")

            # Check if player died
            if entity.has_tag("player"):
                self._on_player_died(world)
                print(f"Player died! Game Over")

            # Remove entity
            world.remove_entity(entity.id)

    def _on_enemy_defeated(self, world: World):
        """Called when an enemy is defeated."""
        # Find player and update stats
        players = world.get_entities_with_tag("player")
        if players and players[0].has_component(GameStats):
            stats = players[0].get_component(GameStats)
            stats.enemies_defeated += 1
            stats.score += 100

            # Check victory condition (defeat 5 enemies)
            if stats.enemies_defeated >= 5:
                self._trigger_victory(world)

    def _on_player_died(self, world: World):
        """Called when the player dies."""
        # Change to game over screen
        screen_managers = world.get_entities_with_component(ScreenState)
        if screen_managers:
            screen_state = screen_managers[0].get_component(ScreenState)
            screen_state.change_screen(GameScreen.GAME_OVER)

    def _trigger_victory(self, world: World):
        """Called when player wins."""
        print("Victory! You defeated 5 enemies!")
        screen_managers = world.get_entities_with_component(ScreenState)
        if screen_managers:
            screen_state = screen_managers[0].get_component(ScreenState)
            screen_state.change_screen(GameScreen.VICTORY)


# ============================================================================
# Game Stats System - Priority: 60
# ============================================================================


class GameStatsSystem(System):
    """
    Updates game statistics like play time.

    Priority: 60
    """

    def __init__(self):
        super().__init__()
        self.priority = 60

    def update(self, world: World, delta_time: float):
        # Update game time for all entities with GameStats
        for entity in world.get_entities_with_component(GameStats):
            stats = entity.get_component(GameStats)
            stats.game_time += delta_time
