#!/usr/bin/env python3
"""
Basic Game Template - Main Script

A minimal template demonstrating:
- Player movement with keyboard controls
- Simple rendering
- Basic game loop
- Entity-Component-System architecture

Controls:
- Arrow keys: Move player
- ESC: Quit game
"""

import pygame
import sys
from pathlib import Path

# Add engine to Python path
engine_path = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(engine_path))

from engine.core.ecs import World, Entity, Component, System
from engine.core.game_loop import GameEngine
from engine.rendering.renderer import Renderer
from engine.input.input_manager import InputManager


# Components
class Position(Component):
    """Position component"""

    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y


class Velocity(Component):
    """Velocity component"""

    def __init__(self, dx: float = 0, dy: float = 0):
        self.dx = dx
        self.dy = dy


class Sprite(Component):
    """Simple sprite component"""

    def __init__(self, color: tuple = (255, 255, 255), size: int = 32):
        self.color = color
        self.size = size


class PlayerController(Component):
    """Player controller component"""

    def __init__(self, speed: float = 200):
        self.speed = speed


# Systems
class PlayerInputSystem(System):
    """Handle player input"""

    def __init__(self, input_manager: InputManager):
        super().__init__()
        self.input_manager = input_manager

    def update(self, world: World, delta_time: float):
        """Update player movement based on input"""
        for entity in world.get_entities_with_component(PlayerController):
            controller = entity.get_component(PlayerController)
            velocity = entity.get_component(Velocity)

            if velocity:
                # Reset velocity
                velocity.dx = 0
                velocity.dy = 0

                # Check arrow keys
                if self.input_manager.is_key_pressed(pygame.K_LEFT):
                    velocity.dx = -controller.speed
                elif self.input_manager.is_key_pressed(pygame.K_RIGHT):
                    velocity.dx = controller.speed

                if self.input_manager.is_key_pressed(pygame.K_UP):
                    velocity.dy = -controller.speed
                elif self.input_manager.is_key_pressed(pygame.K_DOWN):
                    velocity.dy = controller.speed


class MovementSystem(System):
    """Apply velocity to position"""

    def update(self, world: World, delta_time: float):
        """Update positions based on velocity"""
        for entity in world.get_entities_with_component(Position):
            position = entity.get_component(Position)
            velocity = entity.get_component(Velocity)

            if velocity:
                position.x += velocity.dx * delta_time
                position.y += velocity.dy * delta_time


class RenderSystem(System):
    """Render sprites"""

    def __init__(self, screen: pygame.Surface):
        super().__init__()
        self.screen = screen

    def update(self, world: World, delta_time: float):
        """Render all sprites"""
        # Clear screen
        self.screen.fill((20, 20, 30))

        # Render entities
        for entity in world.get_entities_with_component(Sprite):
            sprite = entity.get_component(Sprite)
            position = entity.get_component(Position)

            if position:
                pygame.draw.rect(
                    self.screen,
                    sprite.color,
                    (int(position.x), int(position.y), sprite.size, sprite.size),
                )

        # Display instructions
        font = pygame.font.Font(None, 36)
        text = font.render("Use Arrow Keys to Move", True, (255, 255, 255))
        self.screen.blit(text, (10, 10))

        text2 = font.render("Press ESC to Quit", True, (255, 255, 255))
        self.screen.blit(text2, (10, 50))


def create_player(world: World, x: float, y: float) -> Entity:
    """Create player entity"""
    player = world.create_entity()
    player.add_component(Position(x, y))
    player.add_component(Velocity())
    player.add_component(Sprite(color=(0, 200, 255), size=32))
    player.add_component(PlayerController(speed=200))
    return player


def main():
    """Main game function"""
    print("Starting Basic Game...")

    # Initialize pygame
    pygame.init()

    # Game settings
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 720
    FPS = 60

    # Create window
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Basic Game - NeonWorks Template")

    # Create game engine
    engine = GameEngine(target_fps=FPS)
    world = engine.world

    # Create input manager
    input_manager = InputManager()

    # Add systems
    world.add_system(PlayerInputSystem(input_manager))
    world.add_system(MovementSystem())
    world.add_system(RenderSystem(screen))

    # Create player in center of screen
    create_player(world, WINDOW_WIDTH // 2 - 16, WINDOW_HEIGHT // 2 - 16)

    # Game loop
    clock = pygame.time.Clock()
    running = True

    print("Game started! Use arrow keys to move.")

    while running:
        # Calculate delta time
        delta_time = clock.tick(FPS) / 1000.0

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            # Update input manager
            input_manager.handle_event(event)

        # Update input state
        input_manager.update()

        # Update game logic
        world.update(delta_time)

        # Display
        pygame.display.flip()

    # Cleanup
    pygame.quit()
    print("Thanks for playing!")


if __name__ == "__main__":
    main()
