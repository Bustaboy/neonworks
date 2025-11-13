# Simple RPG - NeonWorks Example Game

A complete, working RPG game that demonstrates all major NeonWorks features.

## What's Included

This example demonstrates:

### Core Features
- **Entity Component System (ECS)** - Flexible game architecture
- **Custom Components** - Player controller, AI, combat stats, etc.
- **Custom Systems** - Input, movement, AI, combat, cleanup
- **Project Configuration** - Using `project.json` for settings
- **Multiple Game Screens** - Menu, gameplay, game over, victory

### Gameplay Features
- **Player Movement** - WASD/Arrow keys with frame-rate independent movement
- **Combat System** - Melee attacks with damage and cooldowns
- **AI Enemies** - State machine (IDLE → CHASE → ATTACK)
- **Health System** - Health bars, damage, death
- **Game Stats** - Track score, enemies defeated, time played
- **Win/Lose Conditions** - Defeat 5 enemies to win, or die trying

### Technical Features
- **Component Queries** - Fast entity lookups with indexing
- **State Machines** - AI behavior with state transitions
- **UI Rendering** - Health bars, HUD, menu screens
- **Entity Factories** - Reusable entity creation functions
- **Game Loop** - Fixed timestep with delta time

## How to Run

### Prerequisites
- Python 3.8+
- NeonWorks engine installed (`pip install -e /path/to/engine/`)

### Running the Game

```bash
# Navigate to the example directory
cd /path/to/engine/examples/simple_rpg/

# Run the game
python main.py
```

## Controls

- **WASD / Arrow Keys**: Move player
- **SPACE**: Attack (when near enemies) / Start game / Retry
- **ESC**: Quit game

## Game Rules

### Objective
Defeat 5 enemies to win the game!

### Combat
- Get close to enemies (within 50 pixels) and press **SPACE** to attack
- Enemies will chase you when you're within 200 pixels
- Enemies attack automatically when close
- Watch your health bar - if it reaches zero, you lose!

### Scoring
- Each enemy defeated: +100 points
- Try to win as fast as possible!

## Code Walkthrough

### Project Structure

```
simple_rpg/
├── main.py              # Entry point and game loop
├── project.json         # Configuration (window size, game settings)
├── scripts/
│   ├── components.py    # Custom component definitions
│   ├── systems.py       # Custom system implementations
│   └── game.py          # Game setup, entity factories, rendering
├── assets/              # (Placeholder for sprites/sounds)
└── README.md            # This file
```

### Components (scripts/components.py)

Custom components are data containers with no logic:

```python
@dataclass
class Velocity(Component):
    """Movement velocity."""
    dx: float = 0.0  # Horizontal velocity
    dy: float = 0.0  # Vertical velocity

@dataclass
class AIController(Component):
    """AI behavior configuration."""
    state: AIState = AIState.IDLE
    detection_range: float = 200.0
    movement_speed: float = 100.0
```

**Key components**:
- `Velocity` - Movement speed and direction
- `PlayerController` - Player-specific settings
- `CombatStats` - Attack damage and range
- `AIController` - Enemy AI configuration
- `GameStats` - Track player progress

### Systems (scripts/systems.py)

Systems contain game logic and process entities with specific components:

#### 1. PlayerInputSystem (Priority: 0)
```python
class PlayerInputSystem(System):
    """Process keyboard input and control player entity."""

    def update(self, world: World, delta_time: float):
        # Find player entity
        players = world.get_entities_with_tag("player")
        if not players:
            return

        player = players[0]
        controller = player.get_component(PlayerController)
        velocity = player.get_component(Velocity)

        # Read keyboard input
        keys = pygame.key.get_pressed()

        # Update velocity based on input
        # ... (see full code in systems.py)
```

**What it does**:
- Finds the player entity
- Reads keyboard input (WASD/Arrows)
- Updates player velocity
- Handles attack input (SPACE)

#### 2. MovementSystem (Priority: 10)
```python
class MovementSystem(System):
    """Update entity positions based on velocity."""

    def update(self, world: World, delta_time: float):
        # Query all entities with Transform and Velocity
        for entity in world.get_entities_with_components(Transform, Velocity):
            transform = entity.get_component(Transform)
            velocity = entity.get_component(Velocity)

            # Update position (frame-rate independent)
            transform.x += velocity.dx * delta_time
            transform.y += velocity.dy * delta_time
```

**What it does**:
- Queries entities with Transform + Velocity components
- Updates position based on velocity * delta_time
- Clamps entities to screen bounds

**Key concept**: Multiplying by `delta_time` makes movement frame-rate independent.

#### 3. AISystem (Priority: 20)
```python
class AISystem(System):
    """Control enemy AI using state machines."""

    def update(self, world: World, delta_time: float):
        # Get player position
        player = self._get_player(world)
        player_transform = player.get_component(Transform)

        # Update each AI entity
        for entity in world.get_entities_with_component(AIController):
            ai = entity.get_component(AIController)
            transform = entity.get_component(Transform)

            # Calculate distance to player
            distance = self._distance(transform, player_transform)

            # State machine transitions
            if ai.state == AIState.IDLE:
                if distance < ai.detection_range:
                    ai.state = AIState.CHASE
            # ... (more transitions)

            # Execute state behavior
            if ai.state == AIState.CHASE:
                self._chase_behavior(entity, player_transform, delta_time)
```

**What it does**:
- Implements AI state machine (IDLE → CHASE → ATTACK)
- Transitions states based on distance to player
- Executes behavior for each state:
  - **IDLE**: Stand still
  - **CHASE**: Move towards player
  - **ATTACK**: Stop and attack

**Key concept**: State machines separate "what to do" (states) from "when to do it" (transitions).

#### 4. CleanupSystem (Priority: 50)
```python
class CleanupSystem(System):
    """Remove dead entities and update stats."""

    def update(self, world: World, delta_time: float):
        entities_to_remove = []

        # Find dead entities
        for entity in world.get_entities_with_component(Health):
            health = entity.get_component(Health)
            if health.current <= 0:
                entities_to_remove.append(entity)

        # Remove dead entities
        for entity in entities_to_remove:
            if entity.has_tag("enemy"):
                self._on_enemy_defeated(world)
            world.remove_entity(entity.id)
```

**What it does**:
- Finds entities with Health <= 0
- Removes them from the world
- Updates game stats when enemies die
- Triggers game over when player dies

**Key concept**: Never modify a collection while iterating over it! Build a list first, then process it.

### Game Setup (scripts/game.py)

#### Entity Factory Pattern

Create reusable functions for spawning entities:

```python
def create_player(world: World, x: float, y: float, config: dict) -> str:
    """Create the player entity."""
    player = world.create_entity("player")
    player.add_component(Transform(x=x, y=y))
    player.add_component(Velocity())
    player.add_component(PlayerController(speed=config["movement_speed"]))
    player.add_component(Health(current=100, maximum=100))
    player.add_component(CombatStats(attack_damage=15))
    player.add_tag("player")
    return player.id
```

**Benefits**:
- Reusable (spawn multiple entities easily)
- Configurable (pass in settings)
- Consistent (all players have same components)
- Testable (can test entity creation separately)

#### Game Loop (main.py)

```python
def main():
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    # Create world and systems
    world = World()
    setup_game(world, 800, 600, config)

    # Game loop
    running = True
    while running:
        # Calculate delta time
        delta_time = clock.tick(60) / 1000.0  # Convert to seconds

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update game logic
        world.update(delta_time)  # Calls all systems in priority order

        # Render
        render_game(screen, world, screen_state)
        pygame.display.flip()

    pygame.quit()
```

**Flow**:
1. Initialize Pygame and create window
2. Create World and add Systems
3. Game loop:
   - Calculate delta time (time since last frame)
   - Handle input events
   - Update all systems
   - Render everything
   - Display to screen

### Rendering

The example uses simple shapes (circles) for entities:

```python
def render_gameplay(screen: pygame.Surface, world: World):
    # Clear screen
    screen.fill((30, 30, 50))

    # Draw all entities
    for entity in world.get_entities_with_component(Transform):
        transform = entity.get_component(Transform)

        # Player = green circle
        if entity.has_tag("player"):
            pygame.draw.circle(screen, (0, 255, 0),
                             (int(transform.x), int(transform.y)), 16)

        # Enemy = red circle
        elif entity.has_tag("enemy"):
            pygame.draw.circle(screen, (255, 50, 50),
                             (int(transform.x), int(transform.y)), 12)

        # Draw health bar
        if entity.has_components(Health, UIHealthBar):
            _draw_health_bar(screen, entity, transform)
```

**Note**: In a real game, you'd use sprites instead of circles. This example focuses on gameplay mechanics.

## Learning Exercises

Try these modifications to learn more:

### Beginner

1. **Change Player Speed**
   - Edit `project.json` → `custom_data.player.movement_speed`
   - Make player faster or slower

2. **Adjust Enemy Count**
   - Edit `game.py` → `start_gameplay()` → `enemy_positions`
   - Add or remove enemy spawn positions

3. **Modify Colors**
   - Edit `game.py` → `render_gameplay()`
   - Change player/enemy colors

### Intermediate

4. **Add a Dash Ability**
   - Add `dash_cooldown` to `PlayerController`
   - In `PlayerInputSystem`, detect shift key
   - Multiply velocity by 3 for 0.2 seconds

5. **Add Enemy Variants**
   - Create `create_fast_enemy()` and `create_tank_enemy()`
   - Fast: high speed, low health
   - Tank: low speed, high health

6. **Add Score Multipliers**
   - Track combo counter in `GameStats`
   - Increase score multiplier for consecutive kills
   - Reset multiplier if hit by enemy

### Advanced

7. **Implement Ranged Combat**
   - Create `Projectile` component
   - Create `ProjectileSystem` to move projectiles
   - Handle projectile-enemy collisions

8. **Add Collision Detection**
   - Add `Collider` components to entities
   - Create `CollisionSystem` to detect overlaps
   - Push entities apart when colliding

9. **Implement Pathfinding**
   - Use NeonWorks' built-in `PathfindingSystem`
   - Make enemies navigate around obstacles
   - Add walls/obstacles to the level

## Key Takeaways

### ECS Architecture Benefits

1. **Composition over Inheritance**: Entities are containers for components, not rigid class hierarchies
2. **Data-Driven**: Game behavior determined by component data, not code
3. **Flexible**: Easy to add/remove features by adding/removing components
4. **Performant**: Systems can query entities efficiently using indexing

### Best Practices Demonstrated

1. **Component Design**: Pure data, no logic
2. **System Design**: Single responsibility, priority-based execution
3. **Entity Factories**: Reusable creation functions
4. **Delta Time**: Frame-rate independent movement
5. **State Machines**: Clean separation of AI states
6. **Query Patterns**: Efficient entity lookups
7. **Screen Management**: Multiple game screens/states

## Next Steps

- **Read the Documentation**:
  - [Creating Components](../../docs/creating_components.md)
  - [Creating Systems](../../docs/creating_systems.md)
  - [API Reference](../../docs/api_reference.md)

- **Explore Other Features**:
  - Use sprites instead of circles (see `Sprite` component and `AssetManager`)
  - Add sound effects (see `AudioManager`)
  - Implement save/load (see `SaveGameManager`)
  - Create multiple levels (see `Project` system)

- **Build Your Own Game**:
  - Use this example as a template
  - Replace components and systems with your own
  - Add your unique gameplay mechanics!

## Troubleshooting

### "ModuleNotFoundError: No module named 'engine'"
- Make sure you installed the engine: `pip install -e /path/to/engine/`
- Or run from the correct directory

### Game runs too fast/slow
- Adjust `target_fps` in `project.json`
- Make sure you're using `delta_time` for movement

### Player can't attack enemies
- Attack range is 50 pixels - get very close!
- Make sure you press SPACE when near an enemy
- Check console for "Player attacks enemy!" message

### Enemies don't move
- Enemies only move when you're within 200 pixels (detection range)
- Try moving closer to them

## Questions?

- Check the [NeonWorks Documentation](../../docs/)
- Look at other examples in `engine/examples/`
- Experiment and have fun!

Happy game development! 🎮
