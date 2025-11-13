# Tutorial 2: Adding Combat

Extend your Coin Collector game with a turn-based combat system. Learn how to implement health, damage, and enemy AI.

## What You'll Learn

- Turn-based combat mechanics
- Health and damage systems
- Simple enemy AI
- Event-driven combat
- Combat UI (health bars)
- Game state management

## Prerequisites

- Completed [Tutorial 1: Your First Game](tutorial_01_your_first_game.md)
- OR have a basic NeonWorks project set up

## Project Setup

We'll build on the Coin Collector game. If you don't have it, create a new project following Tutorial 1.

## Step 1: Add Combat Components

Update `scripts/components.py` to add combat-related components:

```python
"""Custom components for Coin Collector with Combat."""

from engine.core.ecs import Component, Health
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Player(Component):
    """Player component."""
    speed: float = 200.0
    score: int = 0
    wins: int = 0  # Combat wins

@dataclass
class Coin(Component):
    """Collectible coin."""
    value: int = 10

@dataclass
class Velocity(Component):
    """Movement velocity."""
    x: float = 0.0
    y: float = 0.0

@dataclass
class Enemy(Component):
    """Enemy AI component."""
    speed: float = 100.0
    aggro_range: float = 200.0  # Detection range
    attack_range: float = 40.0   # Attack range
    attack_cooldown: float = 1.0 # Seconds between attacks
    cooldown_timer: float = 0.0
    target_id: Optional[str] = None

@dataclass
class CombatStats(Component):
    """Combat statistics."""
    attack: int = 10
    defense: int = 5
    accuracy: float = 0.85  # 85% hit chance

@dataclass
class CombatState(Component):
    """Tracks entity's combat state."""
    in_combat: bool = False
    combat_cooldown: float = 0.0  # Prevent spam
```

## Step 2: Update Systems

Update `scripts/systems.py` with combat systems:

```python
"""Game systems with combat mechanics."""

from engine.core.ecs import System, World, Transform, Collider, Health
from engine.core.events import get_event_manager, Event, EventType
from components import Player, Velocity, Coin, Enemy, CombatStats, CombatState
import pygame
import math
import random

class PlayerInputSystem(System):
    """Handles player input including combat."""

    def __init__(self):
        super().__init__()
        self.priority = 10

    def update(self, world: World, delta_time: float):
        """Update player based on input."""
        keys = pygame.key.get_pressed()

        for entity in world.get_entities_with_components(Player, Velocity):
            player = entity.get_component(Player)
            velocity = entity.get_component(Velocity)
            combat_state = entity.get_component(CombatState)

            # Movement
            dx, dy = 0, 0

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
                velocity.x = (dx / length) * player.speed
                velocity.y = (dy / length) * player.speed
            else:
                velocity.x = 0
                velocity.y = 0

            # Combat cooldown
            if combat_state and combat_state.combat_cooldown > 0:
                combat_state.combat_cooldown -= delta_time

class MovementSystem(System):
    """Applies velocity to position."""

    def __init__(self):
        super().__init__()
        self.priority = 20

    def update(self, world: World, delta_time: float):
        """Move entities."""
        for entity in world.get_entities_with_components(Transform, Velocity):
            transform = entity.get_component(Transform)
            velocity = entity.get_component(Velocity)

            transform.x += velocity.x * delta_time
            transform.y += velocity.y * delta_time

            # Keep on screen
            transform.x = max(16, min(transform.x, 784))
            transform.y = max(16, min(transform.y, 584))

class EnemyAISystem(System):
    """Simple enemy AI."""

    def __init__(self):
        super().__init__()
        self.priority = 25

    def update(self, world: World, delta_time: float):
        """Update enemy behavior."""
        # Get player
        players = world.get_entities_with_tag("player")
        if not players:
            return

        player = players[0]
        player_transform = player.get_component(Transform)

        # Update each enemy
        for entity in world.get_entities_with_components(Enemy, Transform, Velocity):
            enemy_comp = entity.get_component(Enemy)
            enemy_transform = entity.get_component(Transform)
            velocity = entity.get_component(Velocity)

            # Calculate distance to player
            dx = player_transform.x - enemy_transform.x
            dy = player_transform.y - enemy_transform.y
            distance = math.sqrt(dx * dx + dy * dy)

            # Check if player in aggro range
            if distance < enemy_comp.aggro_range:
                enemy_comp.target_id = player.id

                # Move towards player if not in attack range
                if distance > enemy_comp.attack_range:
                    # Normalize and move
                    velocity.x = (dx / distance) * enemy_comp.speed
                    velocity.y = (dy / distance) * enemy_comp.speed
                else:
                    # Stop moving when in attack range
                    velocity.x = 0
                    velocity.y = 0
            else:
                # Out of range, wander randomly
                enemy_comp.target_id = None
                velocity.x = 0
                velocity.y = 0

            # Update attack cooldown
            if enemy_comp.cooldown_timer > 0:
                enemy_comp.cooldown_timer -= delta_time

class CombatSystem(System):
    """Handles combat resolution."""

    def __init__(self):
        super().__init__()
        self.priority = 30
        self.event_manager = get_event_manager()

    def update(self, world: World, delta_time: float):
        """Check for combat situations."""
        # Check enemy attacks on player
        enemies = world.get_entities_with_component(Enemy)
        players = world.get_entities_with_tag("player")

        if not players:
            return

        player = players[0]

        for enemy_entity in enemies:
            enemy = enemy_entity.get_component(Enemy)

            if enemy.target_id == player.id and enemy.cooldown_timer <= 0:
                enemy_transform = enemy_entity.get_component(Transform)
                player_transform = player.get_component(Transform)

                # Check if in attack range
                dx = player_transform.x - enemy_transform.x
                dy = player_transform.y - enemy_transform.y
                distance = math.sqrt(dx * dx + dy * dy)

                if distance <= enemy.attack_range:
                    # Execute attack
                    self.execute_attack(enemy_entity, player)
                    enemy.cooldown_timer = enemy.attack_cooldown

    def execute_attack(self, attacker, target):
        """Execute an attack."""
        attacker_stats = attacker.get_component(CombatStats)
        target_health = target.get_component(Health)
        target_stats = target.get_component(CombatStats)

        if not all([attacker_stats, target_health, target_stats]):
            return

        # Hit check
        if random.random() > attacker_stats.accuracy:
            print(f"{attacker.id} missed!")
            return

        # Calculate damage
        damage = max(1, attacker_stats.attack - target_stats.defense // 2)

        # Apply damage
        target_health.current -= damage
        target_health.current = max(0, target_health.current)

        print(f"{attacker.id} dealt {damage} damage to {target.id}")
        print(f"{target.id} health: {target_health.current}/{target_health.maximum}")

        # Emit damage event
        self.event_manager.emit(Event(EventType.DAMAGE_DEALT, {
            "attacker_id": attacker.id,
            "target_id": target.id,
            "amount": damage
        }))

        # Check for death
        if target_health.current <= 0:
            self.event_manager.emit(Event(EventType.UNIT_DIED, {
                "entity_id": target.id,
                "killer_id": attacker.id
            }))

class PlayerCombatSystem(System):
    """Handles player attacking enemies."""

    def __init__(self):
        super().__init__()
        self.priority = 28

    def update(self, world: World, delta_time: float):
        """Check for player attacks."""
        # Check if player pressed attack key (Space)
        keys = pygame.key.get_pressed()

        for player_entity in world.get_entities_with_component(Player):
            combat_state = player_entity.get_component(CombatState)

            # Check cooldown
            if combat_state and combat_state.combat_cooldown > 0:
                continue

            if keys[pygame.K_SPACE]:
                # Find nearest enemy
                player_transform = player_entity.get_component(Transform)
                nearest_enemy = self._find_nearest_enemy(world, player_transform)

                if nearest_enemy:
                    enemy_transform = nearest_enemy.get_component(Transform)

                    # Check range
                    dx = enemy_transform.x - player_transform.x
                    dy = enemy_transform.y - player_transform.y
                    distance = math.sqrt(dx * dx + dy * dy)

                    if distance <= 50:  # Attack range
                        self._execute_player_attack(player_entity, nearest_enemy)
                        if combat_state:
                            combat_state.combat_cooldown = 0.5

    def _find_nearest_enemy(self, world: World, player_transform: Transform):
        """Find nearest enemy."""
        enemies = world.get_entities_with_component(Enemy)
        nearest = None
        min_distance = float('inf')

        for enemy in enemies:
            enemy_transform = enemy.get_component(Transform)
            dx = enemy_transform.x - player_transform.x
            dy = enemy_transform.y - player_transform.y
            distance = math.sqrt(dx * dx + dy * dy)

            if distance < min_distance:
                min_distance = distance
                nearest = enemy

        return nearest

    def _execute_player_attack(self, player_entity, enemy_entity):
        """Player attacks enemy."""
        from engine.core.events import get_event_manager

        player_stats = player_entity.get_component(CombatStats)
        enemy_health = enemy_entity.get_component(Health)
        enemy_stats = enemy_entity.get_component(CombatStats)

        if not all([player_stats, enemy_health, enemy_stats]):
            return

        # Hit check
        if random.random() > player_stats.accuracy:
            print("Player missed!")
            return

        # Calculate damage
        damage = max(1, player_stats.attack - enemy_stats.defense // 2)

        # Apply damage
        enemy_health.current -= damage
        enemy_health.current = max(0, enemy_health.current)

        print(f"Player dealt {damage} damage to {enemy_entity.id}")
        print(f"Enemy health: {enemy_health.current}/{enemy_health.maximum}")

        # Emit events
        event_manager = get_event_manager()
        event_manager.emit(Event(EventType.DAMAGE_DEALT, {
            "attacker_id": player_entity.id,
            "target_id": enemy_entity.id,
            "amount": damage
        }))

        # Check for death
        if enemy_health.current <= 0:
            event_manager.emit(Event(EventType.UNIT_DIED, {
                "entity_id": enemy_entity.id,
                "killer_id": player_entity.id
            }))

class DeathSystem(System):
    """Handles entity death."""

    def __init__(self):
        super().__init__()
        self.priority = 35
        self.event_manager = get_event_manager()
        self.event_manager.subscribe(EventType.UNIT_DIED, self.on_unit_died)
        self.entities_to_remove = []

    def on_unit_died(self, event: Event):
        """Handle death event."""
        entity_id = event.data["entity_id"]
        self.entities_to_remove.append(entity_id)

    def update(self, world: World, delta_time: float):
        """Remove dead entities."""
        for entity_id in self.entities_to_remove:
            entity = world.get_entity(entity_id)

            if entity and entity.has_component(Enemy):
                # Enemy died - award player
                players = world.get_entities_with_component(Player)
                if players:
                    player = players[0].get_component(Player)
                    player.wins += 1
                    player.score += 50
                    print(f"Enemy defeated! Total wins: {player.wins}")

            world.remove_entity(entity_id)

        self.entities_to_remove.clear()

        # Process queued events
        self.event_manager.process_events()

class CoinCollectionSystem(System):
    """Handles coin collection."""

    def __init__(self):
        super().__init__()
        self.priority = 32

    def update(self, world: World, delta_time: float):
        """Check for coin collisions."""
        players = world.get_entities_with_component(Player)
        coins = world.get_entities_with_component(Coin)

        for player_entity in players:
            player = player_entity.get_component(Player)
            player_transform = player_entity.get_component(Transform)

            coins_to_remove = []
            for coin_entity in coins:
                coin_transform = coin_entity.get_component(Transform)
                coin = coin_entity.get_component(Coin)

                # Check distance
                dx = coin_transform.x - player_transform.x
                dy = coin_transform.y - player_transform.y
                distance = math.sqrt(dx * dx + dy * dy)

                if distance < 30:  # Collection range
                    player.score += coin.value
                    coins_to_remove.append(coin_entity.id)

            for coin_id in coins_to_remove:
                world.remove_entity(coin_id)

class RenderSystem(System):
    """Renders game."""

    def __init__(self, screen: pygame.Surface, font: pygame.font.Font):
        super().__init__()
        self.screen = screen
        self.font = font
        self.small_font = pygame.font.Font(None, 24)
        self.priority = 100

    def update(self, world: World, delta_time: float):
        """Render everything."""
        self.screen.fill((30, 30, 50))

        # Render coins
        for entity in world.get_entities_with_component(Coin):
            transform = entity.get_component(Transform)
            pygame.draw.circle(self.screen, (255, 215, 0),
                             (int(transform.x), int(transform.y)), 12)
            pygame.draw.circle(self.screen, (255, 255, 150),
                             (int(transform.x - 3), int(transform.y - 3)), 4)

        # Render enemies
        for entity in world.get_entities_with_components(Enemy, Transform):
            transform = entity.get_component(Transform)
            health = entity.get_component(Health)

            # Draw red circle for enemy
            pygame.draw.circle(self.screen, (255, 0, 0),
                             (int(transform.x), int(transform.y)), 16)

            # Draw health bar
            if health:
                self._draw_health_bar(transform.x, transform.y - 25,
                                    health.current, health.maximum)

        # Render player
        for entity in world.get_entities_with_components(Player, Transform):
            transform = entity.get_component(Transform)
            player = entity.get_component(Player)
            health = entity.get_component(Health)

            # Draw green square
            pygame.draw.rect(self.screen, (0, 255, 0),
                           (int(transform.x - 16), int(transform.y - 16), 32, 32))

            # Draw player health bar
            if health:
                self._draw_health_bar(transform.x, transform.y - 30,
                                    health.current, health.maximum)

            # Draw HUD
            score_text = self.font.render(f"Score: {player.score}", True, (255, 255, 255))
            self.screen.blit(score_text, (10, 10))

            wins_text = self.font.render(f"Enemies Defeated: {player.wins}", True, (255, 255, 255))
            self.screen.blit(wins_text, (10, 45))

            health_text = self.font.render(
                f"HP: {int(health.current)}/{int(health.maximum)}",
                True, (255, 255, 255)
            )
            self.screen.blit(health_text, (10, 80))

        # Draw instructions
        inst = self.small_font.render("WASD: Move | SPACE: Attack", True, (200, 200, 200))
        self.screen.blit(inst, (10, 570))

    def _draw_health_bar(self, x: float, y: float, current: float, maximum: float):
        """Draw a health bar."""
        bar_width = 40
        bar_height = 5

        # Background
        bg_rect = pygame.Rect(int(x - bar_width/2), int(y), bar_width, bar_height)
        pygame.draw.rect(self.screen, (60, 60, 60), bg_rect)

        # Health
        health_width = int(bar_width * (current / maximum))
        if health_width > 0:
            health_rect = pygame.Rect(int(x - bar_width/2), int(y), health_width, bar_height)
            color = (0, 255, 0) if current / maximum > 0.5 else (255, 0, 0)
            pygame.draw.rect(self.screen, color, health_rect)

        # Border
        pygame.draw.rect(self.screen, (255, 255, 255), bg_rect, 1)
```

## Step 3: Update Game Setup

Update `scripts/game.py`:

```python
"""Game setup with combat."""

from engine.core.ecs import World, Transform, Collider, Health
from components import Player, Coin, Velocity, Enemy, CombatStats, CombatState
from systems import (
    PlayerInputSystem,
    MovementSystem,
    EnemyAISystem,
    PlayerCombatSystem,
    CombatSystem,
    DeathSystem,
    CoinCollectionSystem,
    RenderSystem
)
import pygame
import random

def setup_game(world: World, screen: pygame.Surface):
    """Initialize game with combat."""

    # Create player
    player = world.create_entity("player")
    player.add_component(Transform(x=400, y=300))
    player.add_component(Player(speed=200.0, score=0))
    player.add_component(Velocity())
    player.add_component(Collider(width=32, height=32))
    player.add_component(Health(current=100, maximum=100))
    player.add_component(CombatStats(attack=15, defense=8))
    player.add_component(CombatState())
    player.add_tag("player")

    # Spawn enemies
    for i in range(3):
        x = random.randint(100, 700)
        y = random.randint(100, 500)

        enemy = world.create_entity(f"enemy_{i}")
        enemy.add_component(Transform(x=x, y=y))
        enemy.add_component(Enemy(speed=80.0, aggro_range=150.0))
        enemy.add_component(Velocity())
        enemy.add_component(Health(current=30, maximum=30))
        enemy.add_component(CombatStats(attack=8, defense=3))
        enemy.add_tag("enemy")

    # Spawn coins
    for i in range(5):
        x = random.randint(50, 750)
        y = random.randint(50, 550)

        coin = world.create_entity(f"coin_{i}")
        coin.add_component(Transform(x=x, y=y))
        coin.add_component(Coin(value=10))
        coin.add_tag("coin")

    # Create systems
    font = pygame.font.Font(None, 36)

    world.add_system(PlayerInputSystem())
    world.add_system(MovementSystem())
    world.add_system(EnemyAISystem())
    world.add_system(PlayerCombatSystem())
    world.add_system(CombatSystem())
    world.add_system(CoinCollectionSystem())
    world.add_system(DeathSystem())
    world.add_system(RenderSystem(screen, font))

    print("Game with combat ready!")
    print("Defeat enemies and collect coins!")
```

## Step 4: Run the Game

```bash
python main.py
```

Now you have enemies that chase and attack you! Press SPACE when near an enemy to attack back.

## What's New?

### Combat Components

- **Health**: Track hit points
- **CombatStats**: Attack, defense, accuracy
- **Enemy**: AI behavior and aggro ranges
- **CombatState**: Combat cooldowns

### Combat Systems

- **EnemyAISystem**: Enemies chase player when in range
- **PlayerCombatSystem**: Player attacks with spacebar
- **CombatSystem**: Resolves enemy attacks
- **DeathSystem**: Handles entity death

### Events

Combat uses events for decoupled communication:
- `DAMAGE_DEALT`: When damage is applied
- `UNIT_DIED`: When entity dies

## Challenges

### Easy
1. Add more enemies (5-10)
2. Increase player attack damage
3. Give enemies more health

### Medium
1. **Weapon upgrades**: Collect items that increase attack
2. **Healing**: Add health potions
3. **Enemy types**: Create fast/weak and slow/strong enemies
4. **Knockback**: Push enemies back when hit

### Hard
1. **Boss enemy**: High health, special attacks
2. **Ranged attacks**: Shoot projectiles
3. **Status effects**: Poison, slow, etc.
4. **Combo system**: Bonus damage for consecutive hits

## Next Steps

Continue to [Tutorial 3: Creating UI](tutorial_03_creating_ui.md) to learn about menus, buttons, and advanced UI.

## Key Concepts

✅ **Components separate data from logic**
✅ **Systems process entities with specific components**
✅ **Events decouple systems**
✅ **Priorities control system execution order**
✅ **Entity IDs are more reliable than entity references**

Great job! You now have a game with combat mechanics. 🎮⚔️
