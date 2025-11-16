# Turn-Based RPG Template

A template for creating turn-based RPG games with NeonWorks.

## What's Included

This template demonstrates:

- **Turn-Based Combat**: Initiative-based combat system
- **Character Stats**: HP, Attack, Defense, Speed
- **Enemy AI**: Simple but effective AI behavior
- **Damage Calculation**: Attack vs Defense mechanics
- **Battle States**: Menu, Battle, Victory, Defeat screens
- **Battle Log**: Action history and feedback

## Features

- Speed-based turn order
- Scalable enemy difficulty
- Health and stat management
- Combat action system
- Victory/defeat conditions

## Getting Started

### 1. Run the Game

```bash
neonworks run <your_project_name>
```

Or run directly:

```bash
cd <your_project_name>
python scripts/main.py
```

### 2. Controls

- **SPACE**: Start battle / Continue after victory/defeat
- **1**: Attack (during your turn in battle)
- **ESC**: Quit game

### 3. Gameplay

1. Start at the main menu
2. Press SPACE to begin a battle
3. Take turns attacking the enemy
4. Defeat enemies to win battles
5. Continue fighting progressively harder enemies

## Customization Ideas

### Add More Actions

```python
class BattleAction(Component):
    def __init__(self, action_type: str = "attack", target=None):
        self.action_type = action_type  # "attack", "defend", "skill", "item"
        self.target = target

# In battle system:
def _execute_defend(self, entity: Entity):
    stats = entity.get_component(Stats)
    stats.defense *= 1.5  # Temporary defense boost
```

### Add Skills and Abilities

```python
class Skill(Component):
    def __init__(self, name: str, mp_cost: int, power: int):
        self.name = name
        self.mp_cost = mp_cost
        self.power = power

class SkillList(Component):
    def __init__(self):
        self.skills = []
```

### Add Items and Inventory

```python
class Inventory(Component):
    def __init__(self):
        self.items = {}
        self.gold = 0

class Item:
    def __init__(self, name: str, effect_type: str, value: int):
        self.name = name
        self.effect_type = effect_type  # "heal", "damage", "buff"
        self.value = value
```

### Add Character Progression

```python
class Experience(Component):
    def __init__(self):
        self.level = 1
        self.current_exp = 0
        self.exp_to_next = 100

def level_up(entity: Entity):
    stats = entity.get_component(Stats)
    exp = entity.get_component(Experience)

    exp.level += 1
    stats.max_hp += 10
    stats.attack += 2
    stats.defense += 1
    stats.current_hp = stats.max_hp
```

### Add Multiple Enemies

```python
def create_battle(self, num_enemies: int = 3):
    self.player_entity = self.create_player()
    self.enemies = []

    for i in range(num_enemies):
        enemy = self.create_enemy(difficulty=random.randint(1, 3))
        self.enemies.append(enemy)

    self.turn_order_system.initialize_battle(self.world)
```

### Add Status Effects

```python
class StatusEffect(Component):
    def __init__(self, effect_type: str, duration: int, power: int):
        self.effect_type = effect_type  # "poison", "burn", "stun", "buff"
        self.duration = duration
        self.power = power

class StatusEffectSystem(System):
    def update(self, world: World, delta_time: float):
        for entity in world.get_entities_with_component(StatusEffect):
            effect = entity.get_component(StatusEffect)
            stats = entity.get_component(Stats)

            if effect.effect_type == "poison":
                stats.current_hp -= effect.power

            effect.duration -= 1
            if effect.duration <= 0:
                entity.remove_component(StatusEffect)
```

## Project Structure

```
your_project/
├── project.json          # Project configuration
├── README.md            # This file
├── scripts/
│   └── main.py          # Main game logic
├── config/
│   ├── characters.json  # Character definitions (optional)
│   ├── enemies.json     # Enemy definitions (optional)
│   └── skills.json      # Skill definitions (optional)
├── assets/              # Images, sounds, etc.
└── saves/               # Save game files
```

## Configuration

Enable turn-based and combat features in `project.json`:

```json
{
  "settings": {
    "enable_turn_based": true,
    "enable_combat": true,
    "character_definitions": "config/characters.json"
  }
}
```

## Next Steps

1. **Add Visual Effects**: Particle effects for attacks and abilities
2. **Create Character Classes**: Warrior, Mage, Rogue with unique abilities
3. **Design Enemy Types**: Different enemies with unique behaviors
4. **Add Equipment**: Weapons and armor that modify stats
5. **Create Story**: Integrate battles into a larger narrative
6. **Add Save System**: Save player progress and character state

## Documentation

- [NeonWorks Combat System](../../../docs/combat_system.md)
- [Turn-Based System](../../../docs/turn_based_system.md)
- [ECS Architecture](../../../docs/core_concepts.md)
- [Project Configuration](../../../docs/project_configuration.md)

## Tips

- Balance is key: adjust stats to keep battles challenging but fair
- Provide feedback: use the battle log to communicate what's happening
- Test combat feel: make sure turns flow smoothly
- Add variety: different enemies and strategies keep combat interesting
- Consider pacing: battles shouldn't be too long or too short

Happy game development!
