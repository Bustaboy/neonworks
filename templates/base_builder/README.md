# Base Builder Template

A template for creating base building and resource management games with NeonWorks.

## What's Included

This template demonstrates:

- **Building Placement**: Grid-based building system
- **Resource Management**: Wood, stone, food, population
- **Production System**: Buildings produce resources over time
- **Consumption System**: Buildings consume resources
- **Camera Controls**: Pan around your base
- **Resource Economy**: Balance production and consumption

## Features

- Real-time resource production
- Grid-based building placement
- Camera movement for exploring
- Visual resource tracking
- Multiple building types with different functions

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

- **Arrow Keys**: Move camera
- **1**: Select Lumber Mill (produces wood)
- **2**: Select Quarry (produces stone)
- **3**: Select Farm (produces food)
- **Mouse Click**: Place selected building
- **ESC**: Quit game

### 3. Gameplay

1. Start with basic resources
2. Select a building type with number keys
3. Click on the grid to place the building
4. Buildings automatically produce resources
5. Use resources to build more buildings
6. Expand your base!

## Building Types

### Lumber Mill
- **Cost**: 20 wood, 10 stone
- **Produces**: 2 wood per second
- **Consumes**: 0.5 food per second

### Quarry
- **Cost**: 15 wood, 15 stone
- **Produces**: 1.5 stone per second
- **Consumes**: 0.5 food per second

### Farm
- **Cost**: 25 wood, 5 stone
- **Produces**: 3 food per second
- **Consumes**: 0.5 food per second

## Customization Ideas

### Add More Building Types

```python
buildings = {
    "4": {
        "type": "warehouse",
        "name": "Warehouse",
        "color": (100, 100, 150),
        "wood": 30,
        "stone": 20,
        "effect": "increase_storage"
    }
}

class Storage(Component):
    def __init__(self, capacity: int):
        self.capacity = capacity
```

### Add Building Upgrades

```python
class Upgradeable(Component):
    def __init__(self, level: int = 1, max_level: int = 3):
        self.level = level
        self.max_level = max_level

def upgrade_building(entity: Entity, resources: Resources):
    upgradeable = entity.get_component(Upgradeable)
    producer = entity.get_component(Producer)

    if upgradeable.level < upgradeable.max_level:
        # Cost increases with level
        cost = 50 * upgradeable.level

        if resources.wood >= cost:
            resources.wood -= cost
            upgradeable.level += 1
            producer.production_rate *= 1.5
```

### Add Population Management

```python
class Housing(Component):
    def __init__(self, capacity: int):
        self.capacity = capacity

class PopulationSystem(System):
    def update(self, world: World, delta_time: float):
        # Calculate total housing capacity
        total_capacity = 0
        for entity in world.get_entities_with_component(Housing):
            housing = entity.get_component(Housing)
            total_capacity += housing.capacity

        # Update max population
        resources.max_population = total_capacity
```

### Add Building Destruction

```python
def demolish_building(grid_x: int, grid_y: int):
    if (grid_x, grid_y) in self.grid:
        building = self.grid[(grid_x, grid_y)]

        # Refund some resources
        resources.wood += 5
        resources.stone += 5

        # Remove building
        self.world.destroy_entity(building)
        del self.grid[(grid_x, grid_y)]
```

### Add Research System

```python
class Technology(Component):
    def __init__(self):
        self.researched = set()

class ResearchSystem(System):
    def research_tech(self, tech_name: str, cost: dict):
        # Check if can afford
        if self._can_afford(cost):
            self._deduct_resources(cost)
            self.technology.researched.add(tech_name)
            self._apply_tech_benefits(tech_name)
```

### Add Save/Load System

```python
def save_game(self):
    save_data = {
        "resources": {
            "wood": resources.wood,
            "stone": resources.stone,
            "food": resources.food,
        },
        "buildings": []
    }

    for entity in world.get_entities_with_component(BuildingInfo):
        position = entity.get_component(Position)
        building_info = entity.get_component(BuildingInfo)

        save_data["buildings"].append({
            "type": building_info.building_type,
            "x": position.x,
            "y": position.y,
        })

    with open("saves/save.json", "w") as f:
        json.dump(save_data, f, indent=2)
```

### Add Random Events

```python
class EventSystem(System):
    def __init__(self):
        super().__init__()
        self.event_timer = 0
        self.event_cooldown = 30  # seconds

    def update(self, world: World, delta_time: float):
        self.event_timer += delta_time

        if self.event_timer >= self.event_cooldown:
            self.trigger_random_event(world)
            self.event_timer = 0

    def trigger_random_event(self, world: World):
        events = [
            self.bountiful_harvest,
            self.resource_discovery,
            self.harsh_winter,
        ]
        random.choice(events)(world)

    def bountiful_harvest(self, world: World):
        # +50% food production for 10 seconds
        pass
```

## Project Structure

```
your_project/
├── project.json          # Project configuration
├── README.md            # This file
├── scripts/
│   └── main.py          # Main game logic
├── config/
│   ├── buildings.json   # Building definitions
│   └── items.json       # Item definitions
├── assets/              # Building sprites, UI
└── saves/               # Save game files
```

## Configuration

Enable base building and survival features in `project.json`:

```json
{
  "settings": {
    "enable_base_building": true,
    "enable_survival": true,
    "building_definitions": "config/buildings.json",
    "item_definitions": "config/items.json"
  }
}
```

## Next Steps

1. **Add Visual Assets**: Replace colored squares with actual building sprites
2. **Create Building Chains**: Buildings that work together
3. **Add Workers**: Assign population to buildings for efficiency
4. **Add Threats**: Defend your base from enemies
5. **Add Objectives**: Goals and win conditions
6. **Add Seasons**: Seasonal resource modifiers

## Documentation

- [NeonWorks Building System](../../../docs/base_building.md)
- [Survival System](../../../docs/survival_system.md)
- [ECS Architecture](../../../docs/core_concepts.md)
- [Project Configuration](../../../docs/project_configuration.md)

## Tips

- Start by building farms to ensure food supply
- Balance production buildings with consumption
- Plan your base layout for efficiency
- Watch your resource levels carefully
- Expand gradually and sustainably

Happy game development!
