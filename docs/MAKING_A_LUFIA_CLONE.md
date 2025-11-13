# Making a Lufia-Style JRPG with NeonWorks

Step-by-step guide to creating a classic JRPG like Lufia using the NeonWorks engine.

## Table of Contents

1. [Project Setup](#project-setup)
2. [Creating Your First Town](#creating-your-first-town)
3. [Adding Party Members](#adding-party-members)
4. [Setting Up Combat](#setting-up-combat)
5. [Creating a Dungeon](#creating-a-dungeon)
6. [Implementing Puzzles](#implementing-puzzles)
7. [Adding Boss Battles](#adding-boss-battles)
8. [World Map and Travel](#world-map-and-travel)
9. [Equipment and Shops](#equipment-and-shops)
10. [Polishing Your Game](#polishing-your-game)

---

## Project Setup

### 1. Create Your Project Structure

```bash
mkdir projects/lufia_clone
cd projects/lufia_clone
```

### 2. Create project.json

```json
{
  "metadata": {
    "name": "Lufia Clone",
    "version": "1.0.0",
    "description": "A classic JRPG inspired by Lufia",
    "author": "Your Name",
    "engine_version": "0.1.0"
  },
  "paths": {
    "assets": "assets",
    "maps": "assets/maps",
    "scripts": "scripts",
    "saves": "saves"
  },
  "settings": {
    "window_title": "Lufia Clone",
    "window_width": 800,
    "window_height": 600,
    "tile_size": 32,
    "enable_jrpg_mode": true,
    "battle_style": "jrpg",
    "encounter_rate": 25.0,
    "initial_zone": "starting_town"
  }
}
```

### 3. Create Directory Structure

```
lufia_clone/
├── project.json
├── assets/
│   ├── maps/
│   ├── sprites/
│   │   ├── characters/
│   │   ├── enemies/
│   │   ├── tilesets/
│   │   └── ui/
│   ├── sounds/
│   └── music/
├── scripts/
│   └── game.py
└── saves/
```

---

## Creating Your First Town

### 1. Design the Town Map

Create `assets/maps/starting_town.json`:

```json
{
  "name": "Alekia Village",
  "width": 30,
  "height": 20,
  "tile_size": 32,
  "background_music": "music/town_theme.mp3",
  "encounter_rate": 0.0,
  "spawn_points": [
    {
      "name": "default",
      "x": 15,
      "y": 18,
      "direction": "UP"
    },
    {
      "name": "from_world_map",
      "x": 15,
      "y": 19,
      "direction": "UP"
    },
    {
      "name": "player_house",
      "x": 5,
      "y": 5,
      "direction": "DOWN"
    }
  ],
  "tilemap": {
    "tilesets": [
      {
        "name": "town",
        "image": "assets/sprites/tilesets/town.png",
        "tile_width": 32,
        "tile_height": 32,
        "columns": 10,
        "tile_count": 100
      }
    ],
    "layers": [
      {
        "name": "ground",
        "visible": true,
        "data": "..."
      },
      {
        "name": "buildings",
        "visible": true,
        "data": "..."
      },
      {
        "name": "overhead",
        "visible": true,
        "data": "..."
      }
    ]
  },
  "collision": {
    "layer": "buildings",
    "blocked_tiles": [10, 11, 12, 13, 14, 15, 20, 21, 22]
  },
  "npcs": [
    {
      "x": 15,
      "y": 10,
      "sprite": "assets/sprites/characters/guard.png",
      "behavior": "static",
      "dialogue_id": "guard_intro",
      "can_talk": true
    },
    {
      "x": 8,
      "y": 12,
      "sprite": "assets/sprites/characters/villager.png",
      "behavior": "wander",
      "wander_radius": 3,
      "dialogue_id": "villager_greeting"
    },
    {
      "x": 20,
      "y": 8,
      "sprite": "assets/sprites/characters/shopkeeper.png",
      "behavior": "static",
      "dialogue_id": "shop_greeting"
    }
  ],
  "objects": [
    {
      "x": 12,
      "y": 14,
      "sprite": "assets/sprites/objects/sign.png",
      "is_solid": false,
      "can_interact": true,
      "interaction_type": "examine",
      "dialogue_id": "town_sign"
    }
  ],
  "triggers": [
    {
      "x": 15,
      "y": 20,
      "target_zone": "world_map",
      "target_spawn": "alekia_exit",
      "transition_type": "fade"
    },
    {
      "x": 5,
      "y": 6,
      "target_zone": "player_house",
      "target_spawn": "default",
      "transition_type": "instant"
    }
  ]
}
```

### 2. Create the Main Game Script

Create `scripts/game.py`:

```python
import pygame
from engine.core.ecs import World
from engine.core.events import EventManager
from engine.input.input_manager import InputManager
from engine.rendering.renderer import Renderer
from engine.rendering.camera import Camera
from systems.exploration import ExplorationSystem
from systems.zone_system import ZoneSystem
from systems.jrpg_battle_system import JRPGBattleSystem
from systems.magic_system import MagicSystem
from systems.random_encounters import RandomEncounterSystem
from systems.puzzle_system import PuzzleSystem
from systems.boss_ai import BossAISystem

class LufiaGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Lufia Clone")

        # Core systems
        self.world = World()
        self.event_manager = EventManager()
        self.input_manager = InputManager()
        self.camera = Camera(800, 600)
        self.renderer = Renderer(800, 600, 32, self.camera)

        # JRPG systems
        self.exploration_system = ExplorationSystem(
            self.input_manager,
            self.event_manager
        )
        self.zone_system = ZoneSystem(self.event_manager, "assets")
        self.battle_system = JRPGBattleSystem(self.event_manager)
        self.magic_system = MagicSystem(self.event_manager)
        self.encounter_system = RandomEncounterSystem(self.event_manager)
        self.puzzle_system = PuzzleSystem(self.event_manager)
        self.boss_ai_system = BossAISystem(self.event_manager)

        # Add systems to world
        self.world.add_system(self.exploration_system)
        self.world.add_system(self.zone_system)
        self.world.add_system(self.battle_system)
        self.world.add_system(self.magic_system)
        self.world.add_system(self.encounter_system)
        self.world.add_system(self.puzzle_system)
        self.world.add_system(self.boss_ai_system)

        # Create player
        self.player = self.create_player()

        # Load starting zone
        self.zone_system.load_zone(self.world, "starting_town", "default")

        # Game state
        self.running = True
        self.clock = pygame.time.Clock()

    def create_player(self):
        """Create player character"""
        from engine.core.ecs import Transform, GridPosition, Sprite
        from gameplay.movement import Movement, Direction, AnimationState
        from gameplay.combat import Health
        from gameplay.jrpg_combat import (
            JRPGStats, MagicPoints, SpellList, PartyMember
        )

        player = self.world.create_entity()
        player.add_tag("player")

        # Position
        player.add_component(Transform(x=15*32, y=18*32))
        player.add_component(GridPosition(grid_x=15, grid_y=18))

        # Visual
        player.add_component(Sprite(
            texture="assets/sprites/characters/hero.png",
            width=32,
            height=32
        ))

        # Movement
        player.add_component(Movement(speed=4.0, facing=Direction.DOWN))
        player.add_component(AnimationState(
            current_state="idle",
            current_direction=Direction.DOWN
        ))

        # Combat
        player.add_component(Health(max_hp=100, hp=100))
        player.add_component(MagicPoints(max_mp=30, current_mp=30))
        player.add_component(JRPGStats(
            level=1,
            attack=10,
            defense=8,
            magic_attack=8,
            magic_defense=7,
            speed=10,
            luck=5
        ))

        # Magic
        player.add_component(SpellList(learned_spells=["heal"]))

        # Party
        player.add_component(PartyMember(
            character_id="hero",
            character_name="Maxim",
            character_class="hero",
            party_index=0,
            is_active=True
        ))

        return player

    def run(self):
        """Main game loop"""
        while self.running:
            delta_time = self.clock.tick(60) / 1000.0

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.input_manager.process_event(event)

            # Update
            self.input_manager.update(delta_time)
            self.world.update(delta_time)
            self.event_manager.process_events()

            # Render
            self.screen.fill((0, 0, 0))
            self.renderer.render_world(self.world)
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    game = LufiaGame()
    game.run()
```

---

## Adding Party Members

### Creating Party Members

```python
def create_party_member(self, character_data):
    """Create a party member entity"""
    member = self.world.create_entity()
    member.add_tag("party_member")

    # Position (same as player initially)
    member.add_component(Transform())
    member.add_component(GridPosition())

    # Visual
    member.add_component(Sprite(
        texture=character_data["sprite"],
        width=32,
        height=32
    ))

    # Combat stats
    member.add_component(Health(
        max_hp=character_data["hp"],
        hp=character_data["hp"]
    ))
    member.add_component(MagicPoints(
        max_mp=character_data["mp"],
        current_mp=character_data["mp"]
    ))
    member.add_component(JRPGStats(
        level=character_data["level"],
        attack=character_data["attack"],
        defense=character_data["defense"],
        magic_attack=character_data["magic_attack"],
        magic_defense=character_data["magic_defense"],
        speed=character_data["speed"]
    ))

    # Spells
    member.add_component(SpellList(
        learned_spells=character_data["spells"]
    ))

    # Party info
    member.add_component(PartyMember(
        character_id=character_data["id"],
        character_name=character_data["name"],
        character_class=character_data["class"],
        party_index=character_data["index"]
    ))

    return member

# Example party members (like Lufia characters)
party_members = [
    {
        "id": "selan",
        "name": "Selan",
        "class": "mage",
        "level": 1,
        "hp": 80,
        "mp": 50,
        "attack": 7,
        "defense": 6,
        "magic_attack": 15,
        "magic_defense": 12,
        "speed": 12,
        "spells": ["fire", "ice", "heal"],
        "sprite": "assets/sprites/characters/selan.png",
        "index": 1
    },
    {
        "id": "guy",
        "name": "Guy",
        "class": "warrior",
        "level": 1,
        "hp": 120,
        "mp": 10,
        "attack": 15,
        "defense": 12,
        "magic_attack": 5,
        "magic_defense": 6,
        "speed": 8,
        "spells": [],
        "sprite": "assets/sprites/characters/guy.png",
        "index": 2
    },
    {
        "id": "artea",
        "name": "Artea",
        "class": "priest",
        "level": 1,
        "hp": 90,
        "mp": 60,
        "attack": 8,
        "defense": 7,
        "magic_attack": 12,
        "magic_defense": 15,
        "speed": 11,
        "spells": ["heal", "cure", "protect"],
        "sprite": "assets/sprites/characters/artea.png",
        "index": 3
    }
]

# Create party
for member_data in party_members:
    self.create_party_member(member_data)
```

---

## Setting Up Combat

### Creating Enemies

```python
def create_enemy(world, enemy_id, level):
    """Create an enemy entity"""
    from engine.core.ecs import Sprite
    from gameplay.jrpg_combat import (
        EnemyData, ElementalResistances, BattleRewards, BattleAI
    )

    enemy = world.create_entity()
    enemy.add_tag("enemy")

    enemy_templates = {
        "slime": {
            "name": "Slime",
            "sprite": "assets/sprites/enemies/slime.png",
            "hp": 20,
            "mp": 0,
            "attack": 5,
            "defense": 3,
            "magic_attack": 2,
            "magic_defense": 2,
            "speed": 4,
            "exp": 5,
            "gold": 3,
            "weak_to": ElementType.FIRE
        },
        "goblin": {
            "name": "Goblin",
            "sprite": "assets/sprites/enemies/goblin.png",
            "hp": 35,
            "mp": 5,
            "attack": 8,
            "defense": 5,
            "magic_attack": 3,
            "magic_defense": 4,
            "speed": 6,
            "exp": 10,
            "gold": 7,
            "weak_to": ElementType.LIGHTNING
        },
        # Add more enemies...
    }

    template = enemy_templates.get(enemy_id)
    if not template:
        return None

    # Visual
    enemy.add_component(Sprite(
        texture=template["sprite"],
        width=48,
        height=48
    ))

    # Combat
    enemy.add_component(Health(
        max_hp=template["hp"] + level * 5,
        hp=template["hp"] + level * 5
    ))
    enemy.add_component(MagicPoints(
        max_mp=template["mp"],
        current_mp=template["mp"]
    ))
    enemy.add_component(JRPGStats(
        level=level,
        attack=template["attack"] + level,
        defense=template["defense"] + level // 2,
        magic_attack=template["magic_attack"],
        magic_defense=template["magic_defense"],
        speed=template["speed"]
    ))

    # Resistances
    resistances = {}
    if "weak_to" in template:
        resistances[template["weak_to"]] = 1.5
    enemy.add_component(ElementalResistances(resistances=resistances))

    # AI
    enemy.add_component(BattleAI(ai_type="basic"))

    # Rewards
    enemy.add_component(BattleRewards(
        experience=template["exp"] * level,
        gold=template["gold"] * level,
        items=[
            {"item_id": "potion", "chance": 20.0, "quantity": 1}
        ]
    ))

    # Enemy data
    enemy.add_component(EnemyData(
        enemy_id=enemy_id,
        enemy_name=template["name"],
        enemy_type="normal"
    ))

    return enemy
```

---

## Creating a Dungeon

### Dungeon Map Example

Create `assets/maps/ancient_cave.json`:

```json
{
  "name": "Ancient Cave",
  "width": 40,
  "height": 30,
  "encounter_rate": 35.0,
  "encounter_table": "cave_encounters",
  "background_music": "music/dungeon_theme.mp3",
  "spawn_points": [
    {
      "name": "entrance",
      "x": 2,
      "y": 2,
      "direction": "RIGHT"
    },
    {
      "name": "boss_room",
      "x": 38,
      "y": 28,
      "direction": "UP"
    }
  ],
  "tilemap": {
    "tilesets": [
      {
        "name": "cave",
        "image": "assets/sprites/tilesets/cave.png",
        "tile_width": 32,
        "tile_height": 32,
        "columns": 10,
        "tile_count": 100
      }
    ],
    "layers": [
      {
        "name": "floor",
        "data": "..."
      },
      {
        "name": "walls",
        "data": "..."
      }
    ]
  },
  "collision": {
    "layer": "walls",
    "blocked_tiles": [1, 2, 3, 4, 5, 6, 7, 8, 9]
  }
}
```

---

## Implementing Puzzles

### Four-Switch Puzzle Example

```python
def create_four_switch_puzzle(world):
    """
    Classic Lufia-style puzzle: Four switches must be in correct positions.
    """
    from gameplay.puzzle_objects import Switch, Door, PuzzleController

    # Create switches
    switch_positions = [(5, 5), (15, 5), (5, 15), (15, 15)]
    switch_entities = []

    for i, (x, y) in enumerate(switch_positions):
        switch = world.create_entity()
        switch.add_component(GridPosition(grid_x=x, grid_y=y))
        switch.add_component(Switch(
            switch_type="toggle",
            target_ids=[f"puzzle_controller"]
        ))
        switch_entities.append(switch)

    # Create door
    door = world.create_entity()
    door.add_component(GridPosition(grid_x=20, grid_y=10))
    door.add_component(Door(is_locked=True, requires_switch=True))
    door.add_component(Collider2D(is_solid=True))

    # Create puzzle controller
    controller = world.create_entity()
    controller.add_component(PuzzleController(
        puzzle_id="four_switch_puzzle",
        puzzle_type="switch_combination",
        required_switches=[e.id for e in switch_entities],
        required_states=[True, False, True, True],  # The solution!
        reward_target_ids=[door.id]
    ))

    return controller
```

### Block and Plate Puzzle

```python
def create_block_puzzle(world):
    """Push blocks onto pressure plates to open doors"""
    from gameplay.puzzle_objects import PushableBlock, PressurePlate, Door

    # Create pressure plates
    plate1 = world.create_entity()
    plate1.add_component(GridPosition(grid_x=10, grid_y=10))
    plate1.add_component(PressurePlate(
        required_weight=1,
        target_ids=["door1"]
    ))

    plate2 = world.create_entity()
    plate2.add_component(GridPosition(grid_x=15, grid_y=10))
    plate2.add_component(PressurePlate(
        required_weight=1,
        target_ids=["door2"]
    ))

    # Create pushable blocks
    block1 = world.create_entity()
    block1.add_component(GridPosition(grid_x=8, grid_y=8))
    block1.add_component(PushableBlock(weight=1))
    block1.add_component(Sprite(texture="assets/sprites/objects/block.png"))

    block2 = world.create_entity()
    block2.add_component(GridPosition(grid_x=17, grid_y=8))
    block2.add_component(PushableBlock(weight=1))

    # Create doors
    door1 = world.create_entity()
    door1.add_component(GridPosition(grid_x=10, grid_y=15))
    door1.add_component(Door(is_locked=True))

    door2 = world.create_entity()
    door2.add_component(GridPosition(grid_x=15, grid_y=15))
    door2.add_component(Door(is_locked=True))
```

---

## Adding Boss Battles

### Creating a Dungeon Boss

```python
from systems.boss_ai import create_boss_entity, BOSS_TEMPLATES

def setup_boss_encounter(world, boss_id="skeleton_king"):
    """Setup a boss encounter"""
    # Create boss
    boss = create_boss_entity(
        world,
        boss_template=BOSS_TEMPLATES[boss_id],
        level=10
    )

    # Position in boss room
    boss.add_component(GridPosition(grid_x=20, grid_y=15))

    # Register with boss AI system
    boss_ai_system = world.get_system(BossAISystem)
    if boss_ai_system:
        boss_ai_system.register_boss(boss)

    return boss
```

### Scripted Boss Battle

```python
def trigger_boss_battle(world, player, boss):
    """Trigger a boss battle with cutscene"""
    from systems.jrpg_battle_system import JRPGBattleSystem

    # Get party
    party = world.get_entities_with_tag("party_member")
    party_list = [player] + [m for m in party if m.has_component(PartyMember)]

    # Get battle system
    battle_system = world.get_system(JRPGBattleSystem)

    # Play boss intro dialogue
    event_manager.emit(Event(
        EventType.CUSTOM,
        {
            "type": "dialogue",
            "text": "You dare challenge the Skeleton King?",
            "speaker": "Skeleton King"
        }
    ))

    # Start boss battle
    battle_system.start_battle(
        world,
        party=party_list[:4],  # Max 4 party members
        enemies=[boss],
        can_escape=False,
        is_boss=True
    )
```

---

## World Map and Travel

### Creating an Overworld

```json
{
  "name": "World Map",
  "width": 100,
  "height": 100,
  "encounter_rate": 25.0,
  "encounter_table": "overworld",
  "background_music": "music/overworld_theme.mp3",
  "spawn_points": [
    {
      "name": "alekia_exit",
      "x": 50,
      "y": 60,
      "direction": "DOWN"
    }
  ],
  "triggers": [
    {
      "x": 50,
      "y": 60,
      "target_zone": "alekia_village",
      "target_spawn": "from_world_map"
    },
    {
      "x": 30,
      "y": 40,
      "target_zone": "ancient_cave",
      "target_spawn": "entrance"
    }
  ]
}
```

---

## Equipment and Shops

### Equipment System (TODO)

This would integrate with the existing inventory system. Basic structure:

```python
class EquipmentSlot(Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    SHIELD = "shield"
    ACCESSORY = "accessory"

@dataclass
class Equipment(Component):
    equipped: Dict[EquipmentSlot, Optional[str]] = field(default_factory=dict)
```

---

## Polishing Your Game

### Adding Polish

1. **Save/Load System**: Use NeonWorks' built-in serialization
2. **Music and Sound**: Add BGM for towns, dungeons, battles
3. **Battle Animations**: Add spell effects and attack animations
4. **UI Polish**: Create custom battle UI, menus
5. **Particle Effects**: Victory sparkles, spell effects
6. **Screen Transitions**: Fade in/out for zone changes

### Balancing

- **Enemy Stats**: Scale with level appropriately
- **Encounter Rate**: 20-30 for overworld, 35-45 for dungeons
- **Spell Costs**: Low (5MP), Medium (15MP), High (30MP), Ultimate (50MP+)
- **Boss HP**: 3-5x normal enemy HP for that area

---

## Complete Example: First Hour of Gameplay

1. Start in Alekia Village
2. Talk to NPCs to learn about the threat
3. Form party (recruit Selan)
4. Enter first dungeon (Ancient Cave)
5. Solve basic puzzles
6. Face random encounters
7. Defeat first boss (Skeleton King)
8. Return to town for rewards
9. Unlock world map
10. Travel to next location

---

## Next Steps

- Add more towns and dungeons
- Create unique bosses for each dungeon
- Implement character progression (leveling, stat growth)
- Add equipment and inventory system
- Create story events and cutscenes
- Design endgame content

---

For more detailed API documentation, see [JRPG_SYSTEMS.md](./JRPG_SYSTEMS.md).
