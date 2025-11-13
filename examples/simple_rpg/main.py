#!/usr/bin/env python3
"""
Simple RPG Example - Main Entry Point

This is a complete, working game that demonstrates NeonWorks features:
- Entity Component System (ECS) architecture
- Custom components and systems
- Player input and movement
- AI enemy behavior with state machines
- Combat mechanics
- UI rendering (health bars, HUD)
- Multiple game screens (menu, gameplay, game over, victory)

Run this file to play the game!
"""

import pygame
import sys
import os
import json

# Add the engine to Python path
# This allows us to import from the engine module
engine_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, engine_path)

# Add scripts to Python path
scripts_path = os.path.join(os.path.dirname(__file__), "scripts")
sys.path.insert(0, scripts_path)

from neonworks.core.ecs import World
from scripts.game import setup_game, start_gameplay, render_game
from scripts.components import GameScreen, ScreenState


def load_config():
    """Load project configuration."""
    config_path = os.path.join(os.path.dirname(__file__), "project.json")
    with open(config_path, "r") as f:
        return json.load(f)


def main():
    """Main game loop."""
    # Load configuration
    config = load_config()
    window_config = config["settings"]["window"]
    custom_data = config.get("custom_data", {})

    # Initialize Pygame
    pygame.init()

    # Create window
    screen_width = window_config["width"]
    screen_height = window_config["height"]
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption(window_config["title"])

    # Create clock for frame rate control
    clock = pygame.time.Clock()
    target_fps = config["settings"]["target_fps"]

    # Create world and set up game
    world = World()
    setup_game(world, screen_width, screen_height, custom_data)

    # Get screen manager
    screen_managers = world.get_entities_with_component(ScreenState)
    screen_manager = screen_managers[0] if screen_managers else None

    if not screen_manager:
        print("Error: No screen manager found!")
        return

    screen_state = screen_manager.get_component(ScreenState)

    # Main game loop
    running = True
    gameplay_started = False

    while running:
        # Calculate delta time (in seconds)
        delta_time = clock.tick(target_fps) / 1000.0

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                # ESC always quits
                if event.key == pygame.K_ESCAPE:
                    running = False

                # SPACE key handling depends on current screen
                elif event.key == pygame.K_SPACE:
                    if screen_state.current_screen == GameScreen.MENU:
                        # Start gameplay
                        screen_state.change_screen(GameScreen.GAMEPLAY)
                        start_gameplay(world, screen_width, screen_height, custom_data)
                        gameplay_started = True

                    elif screen_state.current_screen in [
                        GameScreen.GAME_OVER,
                        GameScreen.VICTORY,
                    ]:
                        # Restart gameplay
                        screen_state.change_screen(GameScreen.GAMEPLAY)
                        start_gameplay(world, screen_width, screen_height, custom_data)
                        gameplay_started = True

        # Update game logic (only during gameplay)
        if screen_state.current_screen == GameScreen.GAMEPLAY:
            world.update(delta_time)

        # Render
        render_game(screen, world, screen_state)

        # Display
        pygame.display.flip()

    # Cleanup
    pygame.quit()
    print("Thanks for playing Simple RPG!")


if __name__ == "__main__":
    main()
