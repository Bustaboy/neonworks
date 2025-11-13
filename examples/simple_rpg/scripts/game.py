"""
Main game setup for Simple RPG example.

This file demonstrates how to set up a complete game with:
- Player and enemy entities
- Game systems
- Multiple screens (menu, gameplay, game over, victory)
- UI rendering
"""

import json
import os

import pygame

from neonworks.core.ecs import Health, Sprite, Transform, World

from .components import (AIController, AIState, CombatStats, GameScreen,
                         GameStats, PlayerController, ScreenState, UIHealthBar,
                         Velocity)
from .systems import (AISystem, CleanupSystem, GameStatsSystem, MovementSystem,
                      PlayerInputSystem)

# ============================================================================
# Entity Factory Functions
# ============================================================================


def create_player(world: World, x: float, y: float, config: dict) -> str:
    """
    Create the player entity.

    Args:
        world: The game world
        x, y: Starting position
        config: Player configuration from project.json

    Returns:
        The player entity ID
    """
    player = world.create_entity("player")

    # Position
    player.add_component(Transform(x=x, y=y))

    # Movement
    player.add_component(Velocity())
    player.add_component(PlayerController(speed=config.get("movement_speed", 200.0)))

    # Combat
    player.add_component(
        Health(
            current=config.get("starting_health", 100.0),
            maximum=config.get("starting_health", 100.0),
        )
    )
    player.add_component(
        CombatStats(attack_damage=config.get("attack_damage", 15), attack_range=50.0)
    )

    # UI
    player.add_component(UIHealthBar())

    # Stats tracking
    player.add_component(GameStats())

    # Tag for easy lookup
    player.add_tag("player")

    return player.id


def create_enemy(world: World, x: float, y: float, config: dict) -> str:
    """
    Create an enemy entity.

    Args:
        world: The game world
        x, y: Starting position
        config: Enemy configuration from project.json

    Returns:
        The enemy entity ID
    """
    enemy = world.create_entity()

    # Position
    enemy.add_component(Transform(x=x, y=y))

    # Movement
    enemy.add_component(Velocity())

    # AI
    enemy.add_component(
        AIController(
            detection_range=config.get("detection_range", 200.0),
            movement_speed=config.get("movement_speed", 100.0),
        )
    )

    # Combat
    enemy.add_component(
        Health(current=config.get("health", 50.0), maximum=config.get("health", 50.0))
    )
    enemy.add_component(
        CombatStats(
            attack_damage=config.get("attack_damage", 10),
            attack_range=config.get("attack_range", 40.0),
        )
    )

    # UI
    enemy.add_component(UIHealthBar())

    # Tag for easy lookup
    enemy.add_tag("enemy")

    return enemy.id


def create_screen_manager(world: World) -> str:
    """
    Create a screen state manager entity.

    This entity tracks which screen is currently active.
    """
    manager = world.create_entity("screen_manager")
    manager.add_component(ScreenState(current_screen=GameScreen.MENU))
    return manager.id


# ============================================================================
# Game Setup
# ============================================================================


def setup_game(world: World, screen_width: int, screen_height: int, config: dict):
    """
    Set up the complete game.

    This function:
    1. Adds all game systems to the world
    2. Creates the screen manager
    3. Does NOT create gameplay entities yet (created when entering gameplay)

    Args:
        world: The game world
        screen_width, screen_height: Window dimensions
        config: Custom configuration from project.json
    """
    # Add systems in priority order
    world.add_system(PlayerInputSystem())  # Priority: 0
    world.add_system(MovementSystem(screen_width, screen_height))  # Priority: 10
    world.add_system(AISystem())  # Priority: 20
    world.add_system(CleanupSystem())  # Priority: 50
    world.add_system(GameStatsSystem())  # Priority: 60

    # Create screen manager
    create_screen_manager(world)

    print("Game systems initialized")
    print("Press SPACE to start!")


def start_gameplay(world: World, screen_width: int, screen_height: int, config: dict):
    """
    Start gameplay by creating all gameplay entities.

    Called when transitioning from MENU to GAMEPLAY screen.
    """
    # Clear any existing gameplay entities
    _clear_gameplay_entities(world)

    # Get configuration
    player_config = config.get("player", {})
    enemy_config = config.get("enemy", {})

    # Create player in center
    create_player(world, screen_width / 2, screen_height / 2, player_config)

    # Create enemies at various positions
    enemy_positions = [
        (150, 150),
        (650, 150),
        (150, 450),
        (650, 450),
        (400, 100),
    ]

    for x, y in enemy_positions:
        create_enemy(world, x, y, enemy_config)

    print("Gameplay started! Defeat 5 enemies to win!")
    print("Controls: WASD/Arrows to move, SPACE to attack")
    print("Attack range: 50 pixels (get close to enemies)")


def _clear_gameplay_entities(world: World):
    """Clear all gameplay entities (player, enemies)."""
    entities_to_remove = []

    for entity in world.get_entities():
        if entity.has_tag("player") or entity.has_tag("enemy"):
            entities_to_remove.append(entity.id)

    for entity_id in entities_to_remove:
        world.remove_entity(entity_id)


# ============================================================================
# Rendering
# ============================================================================


def render_game(screen: pygame.Surface, world: World, screen_state: ScreenState):
    """
    Render the current screen.

    Args:
        screen: Pygame surface to draw on
        world: The game world
        screen_state: Current screen state
    """
    if screen_state.current_screen == GameScreen.MENU:
        render_menu(screen)
    elif screen_state.current_screen == GameScreen.GAMEPLAY:
        render_gameplay(screen, world)
    elif screen_state.current_screen == GameScreen.GAME_OVER:
        render_game_over(screen, world)
    elif screen_state.current_screen == GameScreen.VICTORY:
        render_victory(screen, world)


def render_menu(screen: pygame.Surface):
    """Render the main menu screen."""
    screen.fill((20, 20, 40))  # Dark blue background

    # Title
    font_large = pygame.font.Font(None, 64)
    title_text = font_large.render("Simple RPG", True, (0, 255, 255))
    title_rect = title_text.get_rect(center=(screen.get_width() / 2, 150))
    screen.blit(title_text, title_rect)

    # Instructions
    font_medium = pygame.font.Font(None, 32)
    instructions = [
        "A NeonWorks Example Game",
        "",
        "Press SPACE to Start",
        "",
        "Controls:",
        "WASD / Arrow Keys - Move",
        "SPACE - Attack",
        "",
        "Goal: Defeat 5 enemies!",
    ]

    y_offset = 250
    for line in instructions:
        text = font_medium.render(line, True, (200, 200, 200))
        text_rect = text.get_rect(center=(screen.get_width() / 2, y_offset))
        screen.blit(text, text_rect)
        y_offset += 35


def render_gameplay(screen: pygame.Surface, world: World):
    """Render the gameplay screen."""
    # Background
    screen.fill((30, 30, 50))  # Slightly lighter blue

    # Draw entities
    for entity in world.get_entities_with_component(Transform):
        transform = entity.get_component(Transform)

        # Determine color based on entity type
        if entity.has_tag("player"):
            color = (0, 255, 0)  # Green for player
            radius = 16
        elif entity.has_tag("enemy"):
            color = (255, 50, 50)  # Red for enemies
            radius = 12
        else:
            continue

        # Draw entity as circle
        pygame.draw.circle(screen, color, (int(transform.x), int(transform.y)), radius)

        # Draw health bar if entity has one
        if entity.has_components(Health, UIHealthBar):
            _draw_health_bar(screen, entity, transform)

    # Draw HUD
    _draw_hud(screen, world)


def _draw_health_bar(screen: pygame.Surface, entity, transform: Transform):
    """Draw a health bar above an entity."""
    health = entity.get_component(Health)
    ui_bar = entity.get_component(UIHealthBar)

    if not ui_bar.show:
        return

    # Calculate health percentage
    health_percent = max(0, health.current / health.maximum)

    # Bar position (centered above entity)
    bar_x = int(transform.x - ui_bar.width / 2)
    bar_y = int(transform.y + ui_bar.offset_y)

    # Background (red)
    pygame.draw.rect(screen, (100, 0, 0), (bar_x, bar_y, ui_bar.width, ui_bar.height))

    # Foreground (green, scaled by health)
    if health_percent > 0:
        pygame.draw.rect(
            screen,
            (0, 200, 0),
            (bar_x, bar_y, int(ui_bar.width * health_percent), ui_bar.height),
        )

    # Border
    pygame.draw.rect(
        screen, (255, 255, 255), (bar_x, bar_y, ui_bar.width, ui_bar.height), 1
    )


def _draw_hud(screen: pygame.Surface, world: World):
    """Draw the heads-up display (HUD) with player stats."""
    players = world.get_entities_with_tag("player")
    if not players:
        return

    player = players[0]

    # Get player stats
    health = player.get_component(Health)
    stats = player.get_component(GameStats)

    if not (health and stats):
        return

    font = pygame.font.Font(None, 24)

    # Player HP
    hp_text = font.render(
        f"HP: {int(health.current)}/{int(health.maximum)}", True, (255, 255, 255)
    )
    screen.blit(hp_text, (10, 10))

    # Enemies defeated
    enemies_text = font.render(
        f"Enemies: {stats.enemies_defeated}/5", True, (255, 255, 255)
    )
    screen.blit(enemies_text, (10, 35))

    # Score
    score_text = font.render(f"Score: {stats.score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 60))

    # Time
    time_text = font.render(f"Time: {int(stats.game_time)}s", True, (255, 255, 255))
    screen.blit(time_text, (10, 85))


def render_game_over(screen: pygame.Surface, world: World):
    """Render the game over screen."""
    screen.fill((40, 0, 0))  # Dark red background

    # Get final stats
    players = world.get_entities_with_tag("player")
    stats = None
    if players and players[0].has_component(GameStats):
        stats = players[0].get_component(GameStats)

    # Title
    font_large = pygame.font.Font(None, 72)
    title_text = font_large.render("GAME OVER", True, (255, 100, 100))
    title_rect = title_text.get_rect(center=(screen.get_width() / 2, 150))
    screen.blit(title_text, title_rect)

    # Stats
    if stats:
        font_medium = pygame.font.Font(None, 36)
        stats_lines = [
            f"Enemies Defeated: {stats.enemies_defeated}",
            f"Final Score: {stats.score}",
            f"Time Survived: {int(stats.game_time)}s",
            "",
            "Press SPACE to Try Again",
            "Press ESC to Quit",
        ]

        y_offset = 250
        for line in stats_lines:
            text = font_medium.render(line, True, (200, 200, 200))
            text_rect = text.get_rect(center=(screen.get_width() / 2, y_offset))
            screen.blit(text, text_rect)
            y_offset += 45


def render_victory(screen: pygame.Surface, world: World):
    """Render the victory screen."""
    screen.fill((0, 40, 0))  # Dark green background

    # Get final stats
    players = world.get_entities_with_tag("player")
    stats = None
    if players and players[0].has_component(GameStats):
        stats = players[0].get_component(GameStats)

    # Title
    font_large = pygame.font.Font(None, 72)
    title_text = font_large.render("VICTORY!", True, (100, 255, 100))
    title_rect = title_text.get_rect(center=(screen.get_width() / 2, 150))
    screen.blit(title_text, title_rect)

    # Stats
    if stats:
        font_medium = pygame.font.Font(None, 36)
        stats_lines = [
            "You defeated all enemies!",
            "",
            f"Final Score: {stats.score}",
            f"Time: {int(stats.game_time)}s",
            "",
            "Press SPACE to Play Again",
            "Press ESC to Quit",
        ]

        y_offset = 250
        for line in stats_lines:
            text = font_medium.render(line, True, (200, 200, 200))
            text_rect = text.get_rect(center=(screen.get_width() / 2, y_offset))
            screen.blit(text, text_rect)
            y_offset += 45
