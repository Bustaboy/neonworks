# JRPG Systems Documentation

Complete guide to using the NeonWorks JRPG features for creating classic RPG games like Lufia, Final Fantasy, and Dragon Quest.

## Table of Contents

1. [Overview](#overview)
2. [Tile-Based Exploration](#tile-based-exploration)
3. [JRPG Combat System](#jrpg-combat-system)
4. [Magic and MP System](#magic-and-mp-system)
5. [Random Encounters](#random-encounters)
6. [Dungeon Puzzles](#dungeon-puzzles)
7. [Boss Battles](#boss-battles)
8. [Example Usage](#example-usage)

---

## Overview

The NeonWorks engine now includes comprehensive JRPG features that enable you to create traditional Japanese RPGs with:

- **Tile-based overworld exploration** - Walk around towns, dungeons, and world maps
- **Traditional turn-based combat** - Side-view battles with party vs enemies
- **Magic/MP system** - Spells with elemental damage and MP costs
- **Random encounters** - Step-based battle triggering
- **Dungeon puzzles** - Switches, pressure plates, pushable blocks, and more
- **Boss battles** - Multi-phase bosses with special mechanics

All systems integrate seamlessly with the existing NeonWorks ECS architecture.

---

## Tile-Based Exploration

### Components

#### Movement Component
```python
from gameplay.movement import Movement, Direction

# Add to player entity
entity.add_component(Movement(
    speed=4.0,  # Tiles per second
    facing=Direction.DOWN,
    can_move=True,
))
```

#### AnimationState Component
```python
from gameplay.movement import AnimationState

entity.add_component(AnimationState(
    current_state="idle",  # idle, walk
    current_direction=Direction.DOWN,
    frame_duration=0.15,  # Seconds per frame
))
```

#### Interactable Component
```python
from gameplay.movement import Interactable

# Make an NPC interactable
npc.add_component(Interactable(
    interaction_type="talk",
    dialogue_id="npc_greeting",
    show_prompt=True,
    prompt_text="Press E",
))
```

### Exploration System

```python
from systems.exploration import ExplorationSystem

# Initialize in your game
exploration_system = ExplorationSystem(input_manager, event_manager)
world.add_system(exploration_system)

# Set collision map for current zone
collision_map = TileCollisionMap()
collision_map.width = 20
collision_map.height = 15
collision_map.collision_data = [[True] * 20 for _ in range(15)]
exploration_system.set_collision_map(collision_map)
```

### Zone Transitions

```python
from systems.zone_system import ZoneSystem

# Initialize zone system
zone_system = ZoneSystem(event_manager, asset_base_path="assets")
world.add_system(zone_system)

# Load a zone
zone_system.load_zone(world, "town", spawn_point="default")

# Transition to another zone
zone_system.transition_to_zone(world, "dungeon", spawn_point="entrance")
```

### Creating Maps

Map files are JSON with the following structure:

```json
{
  "name": "Starting Town",
  "width": 20,
  "height": 15,
  "tile_size": 32,
  "background_music": "town_theme.mp3",
  "encounter_rate": 0.0,
  "spawn_points": [
    {
      "name": "default",
      "x": 10,
      "y": 7,
      "direction": "DOWN"
    }
  ],
  "tilemap": {
    "tilesets": [
      {
        "name": "main",
        "image": "tilesets/town.png",
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
        "opacity": 1.0,
        "data": [[1, 1, 1], [1, 2, 1]]
      }
    ]
  },
  "collision": {
    "layer": "ground",
    "blocked_tiles": [5, 6, 7, 8]
  },
  "npcs": [
    {
      "x": 5,
      "y": 5,
      "sprite": "sprites/npc_guard.png",
      "behavior": "static",
      "dialogue_id": "guard_greeting"
    }
  ]
}
```

---

## JRPG Combat System

### Combat Components

#### JRPGStats Component
```python
from gameplay.jrpg_combat import JRPGStats

entity.add_component(JRPGStats(
    level=5,
    attack=15,
    defense=10,
    magic_attack=12,
    magic_defense=8,
    speed=10,
    luck=7,
))
```

#### MagicPoints Component
```python
from gameplay.jrpg_combat import MagicPoints

entity.add_component(MagicPoints(
    max_mp=50,
    current_mp=50,
    mp_regen_rate=1.0,  # MP per turn
))
```

#### BattleFormation Component
```python
from gameplay.jrpg_combat import BattleFormation

entity.add_component(BattleFormation(
    row=0,  # 0 = front, 1 = back
    position=0,  # 0-3 position in row
))
```

### Starting a Battle

```python
from systems.jrpg_battle_system import JRPGBattleSystem, BattleCommand

# Initialize battle system
battle_system = JRPGBattleSystem(event_manager)
world.add_system(battle_system)

# Start a battle
party = [player, ally1, ally2]  # Party member entities
enemies = [slime1, slime2]  # Enemy entities

battle_system.start_battle(
    world,
    party=party,
    enemies=enemies,
    can_escape=True,
    is_boss=False
)
```

### Player Actions

```python
# Player's turn - select action
battle_system.player_select_action(
    world,
    command=BattleCommand.ATTACK,
    targets=[enemy1],
)

# Cast magic
battle_system.player_select_action(
    world,
    command=BattleCommand.MAGIC,
    targets=[all_enemies],
    data={"spell_id": "fireball"}
)

# Defend
battle_system.player_select_action(
    world,
    command=BattleCommand.DEFEND,
    targets=[],
)

# Attempt to run
battle_system.player_select_action(
    world,
    command=BattleCommand.RUN,
    targets=[],
)
```

### Battle Events

Subscribe to battle events:

```python
def on_battle_event(event):
    event_type = event.data.get("type")

    if event_type == "battle_start":
        print("Battle started!")

    elif event_type == "battle_damage":
        damage = event.data.get("damage")
        print(f"Damage dealt: {damage}")

    elif event_type == "battle_rewards":
        exp = event.data.get("experience")
        gold = event.data.get("gold")
        print(f"Victory! +{exp} EXP, +{gold} Gold")

event_manager.subscribe(EventType.CUSTOM, on_battle_event)
```

---

## Magic and MP System

### Spell System

```python
from systems.magic_system import MagicSystem, SpellDatabase
from gameplay.jrpg_combat import SpellList

# Initialize magic system
magic_system = MagicSystem(event_manager)
world.add_system(magic_system)

# Get spell database
spell_db = magic_system.get_spell_database()

# Add spell list to character
entity.add_component(SpellList(
    learned_spells=["fire", "heal", "ice"],
))

# Cast a spell
success = magic_system.cast_spell(
    world,
    caster=mage_entity,
    spell_id="fireball",
    targets=[enemy1, enemy2],
)
```

### Custom Spells

```python
from gameplay.jrpg_combat import Spell, ElementType, TargetType

# Create custom spell
custom_spell = Spell(
    spell_id="mega_fire",
    name="Mega Fire",
    description="Powerful fire spell",
    mp_cost=25,
    power=75,
    element=ElementType.FIRE,
    target_type=TargetType.ALL_ENEMIES,
    damage=75,
    animation="fire_explosion",
)

# Register spell
spell_db.register_spell(custom_spell)

# Teach to character
magic_system.learn_spell(mage_entity, "mega_fire")
```

### Elemental System

```python
from gameplay.jrpg_combat import ElementalResistances, ElementType

# Add resistances to enemy
entity.add_component(ElementalResistances(
    resistances={
        ElementType.FIRE: 2.0,  # Weak to fire (200% damage)
        ElementType.ICE: 0.5,   # Resistant to ice (50% damage)
        ElementType.WATER: 0.0,  # Immune to water
        ElementType.HOLY: -1.0,  # Absorbs holy (heals)
    }
))
```

---

## Random Encounters

### Encounter System

```python
from systems.random_encounters import RandomEncounterSystem, EncounterTable, EncounterGroup

# Initialize encounter system
encounter_system = RandomEncounterSystem(event_manager)
world.add_system(encounter_system)

# Create encounter table for a zone
grassland_table = EncounterTable(
    zone_id="grassland",
    encounter_rate=30.0,  # Base rate
    step_interval=8,  # Check every 8 steps
)

# Add encounter groups
grassland_table.add_group(EncounterGroup(
    group_id="slimes",
    enemies=[
        {"enemy_id": "slime", "level": 1, "position": 0},
        {"enemy_id": "slime", "level": 1, "position": 1},
    ],
    weight=40,  # Spawn weight
))

# Register table
encounter_system.register_encounter_table(grassland_table)

# Set current zone
encounter_system.set_current_zone("grassland")
```

### Repel Items

```python
# Activate repel effect (reduces encounter rate)
encounter_system.activate_repel(duration=100)  # 100 steps

# Deactivate
encounter_system.deactivate_repel()
```

### Handling Encounters

```python
def on_random_encounter(event):
    if event.data.get("type") == "random_encounter":
        enemies_data = event.data.get("enemies", [])

        # Create enemy entities
        enemies = []
        for enemy_data in enemies_data:
            enemy = create_enemy(
                enemy_data["enemy_id"],
                enemy_data["level"]
            )
            enemies.append(enemy)

        # Start battle
        battle_system.start_battle(world, party, enemies)

event_manager.subscribe(EventType.CUSTOM, on_random_encounter)
```

---

## Dungeon Puzzles

### Puzzle Components

#### Switch
```python
from gameplay.puzzle_objects import Switch

switch_entity.add_component(Switch(
    switch_type="toggle",  # toggle, momentary, one-time
    target_ids=["door_1", "door_2"],  # What it activates
))
```

#### Pressure Plate
```python
from gameplay.puzzle_objects import PressurePlate

plate_entity.add_component(PressurePlate(
    required_weight=2,  # Needs 2 entities on it
    reset_on_leave=True,
    target_ids=["door_3"],
))
```

#### Pushable Block
```python
from gameplay.puzzle_objects import PushableBlock

block_entity.add_component(PushableBlock(
    weight=1,
    can_be_pulled=False,
))
```

#### Door
```python
from gameplay.puzzle_objects import Door

door_entity.add_component(Door(
    is_locked=True,
    requires_switch=True,
    door_type="normal",
))
```

### Puzzle System

```python
from systems.puzzle_system import PuzzleSystem

# Initialize puzzle system
puzzle_system = PuzzleSystem(event_manager)
world.add_system(puzzle_system)

# Activate a switch
puzzle_system.activate_switch(world, switch_entity)

# Push a block
success = puzzle_system.push_block(world, block_entity, Direction.UP)

# Open a chest
success = puzzle_system.open_chest(world, chest_entity, player_entity)
```

### Multi-Step Puzzles

```python
from gameplay.puzzle_objects import PuzzleController

# Create puzzle controller
controller_entity.add_component(PuzzleController(
    puzzle_id="four_switch_puzzle",
    required_switches=["switch_1", "switch_2", "switch_3", "switch_4"],
    required_states=[True, False, True, True],  # Combination
    reward_target_ids=["treasure_door"],
))
```

---

## Boss Battles

### Creating a Boss

```python
from systems.boss_ai import create_boss_entity, BOSS_TEMPLATES

# Create boss from template
boss = create_boss_entity(
    world,
    boss_template=BOSS_TEMPLATES["skeleton_king"],
    level=10
)

# Start boss battle
battle_system.start_battle(
    world,
    party=party,
    enemies=[boss],
    can_escape=False,
    is_boss=True
)
```

### Custom Boss Template

```python
custom_boss = {
    "boss_id": "custom_boss",
    "name": "Custom Boss",
    "max_phases": 2,
    "phase_triggers": [50.0],  # Phase 2 at 50% HP
    "phases": {
        1: {
            "name": "Phase 1",
            "attack_pattern": ["attack", "attack", "spell"],
            "preferred_spells": ["fireball"],
            "dialogue": "Prepare yourself!",
        },
        2: {
            "name": "Enraged Phase",
            "stat_changes": {"attack": 10, "speed": 5},
            "ai_changes": {
                "attack_pattern": ["spell", "spell", "ultimate"],
                "preferred_spells": ["meteor", "ultima"],
            },
            "heal_percentage": 25.0,  # Heals 25% on phase change
            "summon_enemies": [
                {"enemy_id": "minion", "level": 5, "position": 0},
            ],
            "dialogue": "This isn't even my final form!",
        },
    },
}
```

### Boss AI System

```python
from systems.boss_ai import BossAISystem

# Initialize boss AI
boss_ai_system = BossAISystem(event_manager)
world.add_system(boss_ai_system)

# Register boss for AI processing
boss_ai_system.register_boss(boss_entity)
```

---

## Example Usage

### Complete JRPG Game Setup

```python
from neonworks.core.ecs import World
from neonworks.core.events import EventManager
from engine.input.input_manager import InputManager
from systems.exploration import ExplorationSystem
from systems.zone_system import ZoneSystem
from systems.jrpg_battle_system import JRPGBattleSystem
from systems.magic_system import MagicSystem
from systems.random_encounters import RandomEncounterSystem
from systems.puzzle_system import PuzzleSystem
from systems.boss_ai import BossAISystem

# Create world and managers
world = World()
event_manager = EventManager()
input_manager = InputManager()

# Add all JRPG systems
world.add_system(ExplorationSystem(input_manager, event_manager))
world.add_system(ZoneSystem(event_manager, "assets"))
world.add_system(JRPGBattleSystem(event_manager))
world.add_system(MagicSystem(event_manager))
world.add_system(RandomEncounterSystem(event_manager))
world.add_system(PuzzleSystem(event_manager))
world.add_system(BossAISystem(event_manager))

# Create player
player = create_player_character(world)

# Load starting zone
zone_system = world.get_system(ZoneSystem)
zone_system.load_zone(world, "starting_town", "town_entrance")

# Game loop
while running:
    input_manager.update(delta_time)
    world.update(delta_time)
    renderer.render_world(world)
```

### Creating a Complete Dungeon

```python
def create_dungeon(world):
    """Create a complete dungeon with puzzles and encounters"""

    # Create dungeon zone
    dungeon_map = {
        "name": "Ancient Dungeon",
        "width": 30,
        "height": 20,
        "encounter_rate": 40.0,
        "encounter_table": "dungeon_encounters",
    }

    # Add switches and pressure plates
    switch1 = world.create_entity()
    switch1.add_component(GridPosition(grid_x=5, grid_y=5))
    switch1.add_component(Switch(target_ids=["door1"]))

    plate1 = world.create_entity()
    plate1.add_component(GridPosition(grid_x=10, grid_y=10))
    plate1.add_component(PressurePlate(
        required_weight=2,
        target_ids=["door2"]
    ))

    # Add pushable blocks
    block = world.create_entity()
    block.add_component(GridPosition(grid_x=8, grid_y=8))
    block.add_component(PushableBlock())

    # Add boss at end
    boss = create_boss_entity(world, BOSS_TEMPLATES["skeleton_king"], level=10)
    boss.add_component(GridPosition(grid_x=25, grid_y=15))

    return dungeon_map
```

---

## Project Configuration

Add JRPG settings to your `project.json`:

```json
{
  "settings": {
    "enable_jrpg_mode": true,
    "exploration_mode": "tile-based",
    "battle_style": "jrpg",
    "magic_system_enabled": true,
    "encounter_rate": 30.0,
    "battle_transition_style": "fade",
    "puzzle_difficulty": "normal"
  }
}
```

---

## Tips and Best Practices

1. **Balancing Encounters**: Start with low encounter rates (20-30) and adjust based on playtesting
2. **Boss Phases**: Use 2-3 phases max to avoid battles feeling too long
3. **Puzzle Design**: Always provide visual feedback (sprite changes) for puzzle state
4. **Magic Balance**: Higher tier spells should cost significantly more MP
5. **Zone Design**: Include safe zones (towns) with 0 encounter rate
6. **Save Points**: Place save points before boss battles

---

## Troubleshooting

### Common Issues

**Player can't move**
- Check that `Movement.can_move = True`
- Verify collision map is set correctly
- Ensure no solid entities are blocking

**Battles not triggering**
- Verify encounter table is registered for current zone
- Check that `encounter_rate > 0`
- Ensure step counter is incrementing

**Spells not working**
- Check that entity has `MagicPoints` component
- Verify spell is in `SpellList.learned_spells`
- Ensure enough MP is available

**Puzzles not responding**
- Verify target IDs are correct
- Check that entities have required components
- Ensure puzzle system is added to world

---

## Next Steps

- Read [MAKING_A_LUFIA_CLONE.md](./MAKING_A_LUFIA_CLONE.md) for a complete walkthrough
- Check the `examples/jrpg_demo/` project for a working example
- Explore `templates/jrpg_template/` for a project template

---

For more information, see the [NeonWorks Engine Overview](../NEONWORKS_ENGINE_OVERVIEW.md).
