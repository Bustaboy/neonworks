# Tutorial 1: Your First Game

Build a complete game from scratch in 30 minutes! This tutorial walks you through creating a simple top-down game where you control a character and collect coins.

## What You'll Learn

- Setting up a NeonWorks project
- Creating entities with components
- Writing custom systems
- Handling player input
- Basic rendering
- Collision detection
- Score tracking

## Prerequisites

- Python 3.8+ installed
- NeonWorks installed (`pip install -e engine/`)
- Basic Python knowledge

## Step 1: Create Project Structure

Create your project directory:

```bash
mkdir -p projects/coin_collector
cd projects/coin_collector
mkdir -p assets/sprites scripts
```

## Step 2: Create project.json

Create `project.json` with your game configuration:

```json
{
    "metadata": {
        "name": "Coin Collector",
        "version": "1.0.0",
        "author": "Your Name",
        "description": "Collect coins to increase your score!"
    },
    "paths": {
        "assets": "assets",
        "levels": "levels",
        "scripts": "scripts",
        "saves": "saves",
        "config": "config"
    },
    "settings": {
        "window": {
            "width": 800,
            "height": 600,
            "title": "Coin Collector",
            "fullscreen": false
        },
        "tile_size": 32,
        "target_fps": 60,
        "features_enabled": {
            "rendering": true,
            "physics": true,
            "audio": false,
            "turn_based": false,
            "survival": false,
            "base_building": false
        }
    }
}
```

## Step 3: Define Custom Components

Create `scripts/components.py`:

```python
"""Custom components for Coin Collector game."""

from engine.core.ecs import Component
from dataclasses import dataclass

@dataclass
class Player(Component):
    """Marks entity as player-controlled."""
    speed: float = 200.0  # Pixels per second
    score: int = 0

@dataclass
class Coin(Component):
    """Marks entity as a collectible coin."""
    value: int = 10

@dataclass
class Velocity(Component):
    """Movement velocity."""
    x: float = 0.0
    y: float = 0.0
```

## Step 4: Create Game Systems

Create `scripts/systems.py`:

```python
"""Game systems for Coin Collector."""

from engine.core.ecs import System, World, Transform, Collider
from engine.core.events import get_event_manager, Event, EventType
from components import Player, Velocity, Coin
import pygame
import math

class PlayerInputSystem(System):
    """Handles player keyboard input."""

    def __init__(self):
        super().__init__()
        self.priority = 10  # Run early

    def update(self, world: World, delta_time: float):
        """Update player velocity based on input."""
        keys = pygame.key.get_pressed()

        for entity in world.get_entities_with_components(Player, Velocity):
            player = entity.get_component(Player)
            velocity = entity.get_component(Velocity)

            # Calculate movement direction
            dx = 0
            dy = 0

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx += 1
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy -= 1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy += 1

            # Normalize diagonal movement
            if dx != 0 or dy != 0:
                length = math.sqrt(dx * dx + dy * dy)
                dx /= length
                dy /= length

                velocity.x = dx * player.speed
                velocity.y = dy * player.speed
            else:
                velocity.x = 0
                velocity.y = 0

class MovementSystem(System):
    """Applies velocity to transform."""

    def __init__(self):
        super().__init__()
        self.priority = 20  # Run after input

    def update(self, world: World, delta_time: float):
        """Move entities based on velocity."""
        for entity in world.get_entities_with_components(Transform, Velocity):
            transform = entity.get_component(Transform)
            velocity = entity.get_component(Velocity)

            transform.x += velocity.x * delta_time
            transform.y += velocity.y * delta_time

            # Keep player on screen
            if entity.has_component(Player):
                transform.x = max(16, min(transform.x, 784))
                transform.y = max(16, min(transform.y, 584))

class CoinCollectionSystem(System):
    """Handles coin collection."""

    def __init__(self):
        super().__init__()
        self.priority = 30  # Run after movement

    def update(self, world: World, delta_time: float):
        """Check for coin collisions."""
        players = world.get_entities_with_component(Player)
        coins = world.get_entities_with_component(Coin)

        for player_entity in players:
            player = player_entity.get_component(Player)
            player_transform = player_entity.get_component(Transform)
            player_collider = player_entity.get_component(Collider)

            if not all([player, player_transform, player_collider]):
                continue

            # Check collision with each coin
            coins_to_remove = []
            for coin_entity in coins:
                coin_transform = coin_entity.get_component(Transform)
                coin_collider = coin_entity.get_component(Collider)
                coin = coin_entity.get_component(Coin)

                if not all([coin_transform, coin_collider, coin]):
                    continue

                # Simple AABB collision
                if self._check_collision(
                    player_transform, player_collider,
                    coin_transform, coin_collider
                ):
                    # Collect coin
                    player.score += coin.value
                    coins_to_remove.append(coin_entity.id)

                    print(f"Collected coin! Score: {player.score}")

            # Remove collected coins
            for coin_id in coins_to_remove:
                world.remove_entity(coin_id)

    def _check_collision(self, t1, c1, t2, c2) -> bool:
        """Check AABB collision between two entities."""
        return (
            t1.x < t2.x + c2.width and
            t1.x + c1.width > t2.x and
            t1.y < t2.y + c2.height and
            t1.y + c1.height > t2.y
        )

class RenderSystem(System):
    """Renders entities to screen."""

    def __init__(self, screen: pygame.Surface, font: pygame.font.Font):
        super().__init__()
        self.screen = screen
        self.font = font
        self.priority = 100  # Render last

    def update(self, world: World, delta_time: float):
        """Render all visible entities."""
        # Clear screen
        self.screen.fill((30, 30, 50))  # Dark blue background

        # Render coins
        for entity in world.get_entities_with_component(Coin):
            transform = entity.get_component(Transform)
            if transform:
                # Draw yellow circle for coin
                pygame.draw.circle(
                    self.screen,
                    (255, 215, 0),  # Gold color
                    (int(transform.x), int(transform.y)),
                    12
                )
                # Inner highlight
                pygame.draw.circle(
                    self.screen,
                    (255, 255, 150),
                    (int(transform.x - 3), int(transform.y - 3)),
                    4
                )

        # Render player
        for entity in world.get_entities_with_components(Player, Transform):
            transform = entity.get_component(Transform)
            player = entity.get_component(Player)

            # Draw green square for player
            pygame.draw.rect(
                self.screen,
                (0, 255, 0),
                (int(transform.x - 16), int(transform.y - 16), 32, 32)
            )

            # Draw score
            score_text = self.font.render(
                f"Score: {player.score}",
                True,
                (255, 255, 255)
            )
            self.screen.blit(score_text, (10, 10))

        # Draw instructions
        instructions = self.font.render(
            "WASD or Arrow Keys to Move",
            True,
            (200, 200, 200)
        )
        self.screen.blit(instructions, (10, 570))
```

## Step 5: Create Main Game File

Create `scripts/game.py`:

```python
"""Main game setup for Coin Collector."""

from engine.core.ecs import World, Transform, Collider
from components import Player, Coin, Velocity
from systems import (
    PlayerInputSystem,
    MovementSystem,
    CoinCollectionSystem,
    RenderSystem
)
import pygame
import random

def setup_game(world: World, screen: pygame.Surface):
    """Initialize game entities and systems."""

    # Create player
    player = world.create_entity("player")
    player.add_component(Transform(x=400, y=300))
    player.add_component(Player(speed=200.0, score=0))
    player.add_component(Velocity())
    player.add_component(Collider(width=32, height=32))
    player.add_tag("player")

    # Spawn coins randomly
    for i in range(10):
        x = random.randint(50, 750)
        y = random.randint(50, 550)

        coin = world.create_entity(f"coin_{i}")
        coin.add_component(Transform(x=x, y=y))
        coin.add_component(Coin(value=10))
        coin.add_component(Collider(width=24, height=24))
        coin.add_tag("coin")

    # Create font
    font = pygame.font.Font(None, 36)

    # Add systems
    world.add_system(PlayerInputSystem())
    world.add_system(MovementSystem())
    world.add_system(CoinCollectionSystem())
    world.add_system(RenderSystem(screen, font))

    print("Game setup complete!")
    print("Collect all coins to win!")
```

## Step 6: Create Main Entry Point

Create `main.py` in the project root:

```python
#!/usr/bin/env python3
"""Main entry point for Coin Collector game."""

import pygame
import sys
import os

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from engine.core.ecs import World
from game import setup_game

def main():
    """Main game loop."""
    # Initialize Pygame
    pygame.init()

    # Create window
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Coin Collector")

    # Create world
    world = World()

    # Setup game
    setup_game(world, screen)

    # Game loop
    clock = pygame.time.Clock()
    running = True

    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Update world
        delta_time = clock.tick(60) / 1000.0  # 60 FPS
        world.update(delta_time)

        # Display
        pygame.display.flip()

    pygame.quit()
    print("Thanks for playing!")

if __name__ == "__main__":
    main()
```

## Step 7: Run Your Game!

```bash
cd projects/coin_collector
python main.py
```

You should see a green square (player) and yellow circles (coins). Move with WASD or arrow keys to collect coins!

## What's Happening?

### Entity Component System in Action

1. **Entities**: Player and coins are entities with unique IDs
2. **Components**: Each entity has components (Transform, Player, Coin, etc.) storing data
3. **Systems**: Logic is in systems that process entities with specific components

### Game Loop Flow

```
1. Handle Pygame events (quit, etc.)
2. Update world → Updates all systems in priority order:
   - PlayerInputSystem (priority 10): Read keyboard, set velocity
   - MovementSystem (priority 20): Apply velocity to position
   - CoinCollectionSystem (priority 30): Check collisions, update score
   - RenderSystem (priority 100): Draw everything
3. Display to screen
4. Repeat at 60 FPS
```

## Challenges

Try these modifications to learn more:

### Easy Challenges

1. **Change colors**: Make the player blue and coins red
2. **Adjust speed**: Make the player faster or slower
3. **More coins**: Spawn 20 coins instead of 10
4. **Coin values**: Make some coins worth 20 points

### Medium Challenges

1. **Win condition**: Show "You Win!" when all coins are collected
2. **Timer**: Add a countdown timer (60 seconds to collect all coins)
3. **Obstacles**: Add walls that block the player
4. **Sounds**: Play a sound when collecting coins (enable audio in project.json)

### Hard Challenges

1. **Enemies**: Add moving enemies that end the game on collision
2. **Levels**: Create multiple levels with increasing difficulty
3. **Power-ups**: Add temporary speed boost items
4. **High score**: Save and load high scores using the save system

## What's Next?

Congratulations! You've built your first NeonWorks game. In the next tutorial, we'll add combat mechanics.

**Continue to:** [Tutorial 2: Adding Combat](tutorial_02_adding_combat.md)

## Complete Project Structure

```
projects/coin_collector/
├── project.json
├── main.py
├── scripts/
│   ├── components.py
│   ├── systems.py
│   └── game.py
└── assets/
    └── sprites/
```

## Key Takeaways

✅ Projects use `project.json` for configuration
✅ Components store data, Systems contain logic
✅ Systems run in priority order
✅ `delta_time` makes movement frame-independent
✅ The ECS pattern keeps code organized and maintainable

## Resources

- [Getting Started Guide](../getting_started.md)
- [Creating Components](../creating_components.md)
- [Creating Systems](../creating_systems.md)
- [API Reference](../api_reference.md)
- [Code Recipes](../RECIPES.md)

Happy game development! 🎮
