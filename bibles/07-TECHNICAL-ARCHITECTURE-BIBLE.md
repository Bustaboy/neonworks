# NEON COLLAPSE - TECHNICAL ARCHITECTURE BIBLE
## System Design, Code Structure & Implementation Guide

**Version:** 1.0
**Last Updated:** 2025-11-12
**Status:** MASTER REFERENCE DOCUMENT

---

## TABLE OF CONTENTS

1. [System Overview](#system-overview)
2. [Architecture Principles](#architecture-principles)
3. [Module Structure](#module-structure)
4. [Character System](#character-system)
5. [Combat System](#combat-system)
6. [Data Flow](#data-flow)
7. [Configuration Management](#configuration-management)
8. [UI/Rendering Architecture](#ui-rendering-architecture)
9. [Extension Points](#extension-points)
10. [Performance Considerations](#performance-considerations)

---

## SYSTEM OVERVIEW

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     GAME LOOP (main.py)                  │
│  - Event handling                                        │
│  - State management                                      │
│  - Frame timing                                          │
└────────────┬────────────────────────────────────────────┘
             │
      ┌──────┴──────┐
      │             │
┌─────▼──────┐ ┌───▼───────────┐
│   UI       │ │    COMBAT      │
│  (ui.py)   │ │  (combat.py)   │
│            │ │                │
│ - Rendering│ │ - Turn mgmt    │
│ - Display  │ │ - Initiative   │
│ - Input    │ │ - Victory      │
└─────┬──────┘ └───┬───────────┘
      │            │
      │     ┌──────▼───────┐
      │     │   CHARACTER   │
      └────►│ (character.py)│
            │               │
            │ - Stats       │
            │ - Actions     │
            │ - Calculations│
            └──────┬────────┘
                   │
            ┌──────▼──────┐
            │   CONFIG     │
            │ (config.py)  │
            │              │
            │ - Constants  │
            │ - Balance    │
            │ - Weapons    │
            └──────────────┘
```

### Technology Stack

```
Language:    Python 3.8+
Game Engine: Pygame 2.5.2
Testing:     pytest 7.4.3
Coverage:    pytest-cov 4.1.0
Linting:     flake8, pylint, mypy
Formatting:  black
```

### Design Philosophy

**Separation of Concerns**
- Game logic separate from rendering
- Combat rules independent of UI
- Configuration isolated from implementation

**Testability First**
- Pure functions for calculations
- Minimal side effects
- Dependency injection where possible
- Mock-friendly interfaces

**Data-Driven Design**
- Weapons defined in config
- Character stats in dictionaries
- Balance parameters centralized
- Easy iteration and tuning

---

## ARCHITECTURE PRINCIPLES

### 1. Single Responsibility Principle

Each module has ONE primary responsibility:

```python
character.py  → Character state and actions
combat.py     → Combat encounter management
ui.py         → Rendering and display
main.py       → Game loop and orchestration
config.py     → Configuration and constants
```

### 2. Separation of Logic and Display

**Game Logic** (testable, pure)
```python
def calculate_damage(attacker, target):
    """Pure function - no side effects, fully testable."""
    base_dmg = attacker.weapon['damage']
    stat_bonus = get_stat_bonus(attacker)
    armor_reduction = calculate_armor_reduction(target)
    return base_dmg + stat_bonus - armor_reduction
```

**Display** (pygame-dependent)
```python
def draw_character(screen, character):
    """Rendering only - no game logic."""
    color = get_team_color(character)
    pos = grid_to_screen(character.x, character.y)
    pygame.draw.circle(screen, color, pos, TILE_SIZE // 2)
```

### 3. Configuration-Driven Balance

All balance parameters in `config.py`:

```python
# Easy to tune without touching code
MAX_ACTION_POINTS = 3
DODGE_CAP = 20
DAMAGE_VARIANCE_MIN = 0.85
COVER_HALF = 25

# Weapons data-driven
WEAPONS = {
    'assault_rifle': {
        'damage': 30,
        'accuracy': 85,
        'range': 12,
        # ... all stats here
    }
}
```

### 4. Dependency Injection

Pass dependencies instead of hardcoding:

```python
# GOOD: Testable
class CombatEncounter:
    def __init__(self, player_team, enemy_team):
        self.player_team = player_team
        self.enemy_team = enemy_team

# BAD: Hard to test
class CombatEncounter:
    def __init__(self):
        self.player_team = load_players()  # Hard dependency
        self.enemy_team = spawn_enemies()  # Hard dependency
```

---

## MODULE STRUCTURE

### character.py (223 lines)

**Purpose:** Character state, actions, and stat-based calculations

**Key Components:**
```python
class Character:
    # State
    name, x, y, team
    body, reflexes, intelligence, tech, cool
    hp, max_hp, armor, morale
    ap, max_ap
    weapon, is_alive

    # Calculations (pure functions)
    get_initiative()
    get_dodge_chance()
    get_crit_chance()
    get_morale_modifier()
    calculate_hit_chance(target)
    calculate_damage(target)

    # Actions (state changes)
    attack(target)
    move(new_x, new_y)
    take_damage(damage)
    start_turn()
    end_turn()

    # Queries
    get_hp_percentage()
    get_targets_in_range(all_characters)
```

**Design Decisions:**
- All calculations are methods (easy to test)
- State changes clearly separated from calculations
- No UI dependencies
- No combat management (belongs in combat.py)

### combat.py (276 lines)

**Purpose:** Combat encounter orchestration and turn management

**Key Components:**
```python
class CombatEncounter:
    # State
    player_team, enemy_team, all_characters
    turn_order, current_turn_index, current_character
    combat_active, turn_count
    combat_log, escape_available, victor

    # Initialization
    __init__(player_team, enemy_team)
    roll_initiative()

    # Turn Management
    next_turn()
    start_turn()
    end_turn()

    # Combat Flow
    check_escape_conditions()
    attempt_escape(sacrifice_character=None)
    check_victory()

    # Queries
    get_valid_moves(character)
    get_valid_targets(character)
    get_current_team()

    # AI
    enemy_ai_turn(enemy)

    # Logging
    add_log(message)
```

**Design Decisions:**
- Combat is self-contained (doesn't know about main loop)
- AI logic encapsulated
- Victory conditions checked after each turn
- Escape system fully contained

### config.py (141 lines)

**Purpose:** Centralized configuration and game balance

**Categories:**
```python
# Display Settings
SCREEN_WIDTH, SCREEN_HEIGHT, FPS
TILE_SIZE, GRID_WIDTH, GRID_HEIGHT

# Combat Settings
MAX_ACTION_POINTS
DODGE_CAP
AP_MOVE, AP_BASIC_ATTACK, AP_SPECIAL_ABILITY

# Movement
BASE_MOVEMENT_RANGE

# Modifiers
COVER_HALF, COVER_FULL
FLANKING_BONUS
DAMAGE_VARIANCE_MIN, DAMAGE_VARIANCE_MAX
ARMOR_REDUCTION_MULTIPLIER

# Colors (Cyberpunk Theme)
COLOR_BG, COLOR_GRID
COLOR_PLAYER, COLOR_ALLY, COLOR_ENEMY
COLOR_HP_FULL, COLOR_HP_MID, COLOR_HP_LOW

# Data
PLAYER_START_STATS
ALLY_START_STATS
ENEMY_GRUNT_STATS, ENEMY_ELITE_STATS
WEAPONS = {...}
```

**Design Decisions:**
- ALL magic numbers live here
- Easy to find and modify balance
- No logic, only data
- Imported by all other modules

### ui.py (293 lines)

**Purpose:** Rendering and visual display

**Key Components:**
```python
class GameUI:
    screen, font, clock

    # Rendering
    draw_grid()
    draw_characters(all_characters, current_character)
    draw_hp_bar(character, x, y, width)
    draw_ap_bar(character, x, y, width)
    draw_character_panel(character)
    draw_combat_log(log)
    draw_buttons()
    draw_highlights(valid_moves, valid_targets)

    # Screens
    draw_victory_screen()
    draw_defeat_screen()
    draw_escape_screen()

    # Utilities
    grid_to_screen(grid_x, grid_y)
    screen_to_grid(screen_x, screen_y)
```

**Design Decisions:**
- Pure rendering, no game logic
- All positions calculated from grid coordinates
- Color coding for teams
- Visual feedback for actions

### main.py (309 lines)

**Purpose:** Game loop, event handling, orchestration

**Key Components:**
```python
def main():
    # Setup
    initialize_pygame()
    ui = GameUI()

    # Create characters
    player_team = create_player_team()
    enemy_team = create_enemy_team()

    # Create combat
    combat = CombatEncounter(player_team, enemy_team)

    # Game loop
    while running:
        handle_events()
        update_game_state()
        render()
        clock.tick(FPS)

def handle_events():
    # Mouse clicks
    # Keyboard input
    # Quit handling

def handle_player_turn():
    # Move selection
    # Attack selection
    # End turn

def handle_enemy_turn():
    # AI execution
    # Automatic advancement
```

**Design Decisions:**
- Orchestrates other modules
- Minimal logic (delegates to combat/character)
- Clear game states (playing, victory, defeat, fled)
- Restart capability

---

## CHARACTER SYSTEM

### State Management

**Character State:**
```python
{
    'name': str,
    'position': (x: int, y: int),
    'team': 'player' | 'enemy',

    'attributes': {
        'body': int (1-10),
        'reflexes': int (1-10),
        'intelligence': int (1-10),
        'tech': int (1-10),
        'cool': int (1-10)
    },

    'combat_stats': {
        'hp': int,
        'max_hp': int,
        'armor': int (0-100),
        'morale': int (0-100)
    },

    'action_points': {
        'ap': int,
        'max_ap': int (3)
    },

    'weapon': dict (from WEAPONS config),

    'flags': {
        'is_alive': bool,
        'has_acted': bool,
        'has_moved': bool,
        'in_cover': bool,
        'cover_type': 'half' | 'full' | None
    }
}
```

### Calculation Formulas

All formulas implemented as pure methods:

```python
Initiative = (Reflexes × 2) + random(1, 10)

Dodge Chance = min(20, Reflexes × 3)

Crit Chance = Cool × 2

Morale Modifier = 1.0 + ((Morale - 50) / 200)
    # Morale 100 → 1.25 (25% bonus)
    # Morale 50  → 1.0  (neutral)
    # Morale 0   → 0.75 (25% penalty)

Movement Range = BASE_MOVEMENT_RANGE + (Reflexes // 4)
```

### Hit Chance Formula

```python
def calculate_hit_chance(attacker, target):
    # Base accuracy
    base = attacker.weapon['accuracy']

    # Target dodge
    dodge = target.get_dodge_chance()

    # Initial chance
    hit_chance = base - dodge

    # Cover modifiers
    if target.in_cover:
        if target.cover_type == 'half':
            hit_chance -= COVER_HALF  # -25
        elif target.cover_type == 'full':
            hit_chance -= COVER_FULL  # -40

    # Clamp to 5-95%
    hit_chance = max(5, min(95, hit_chance))

    return hit_chance
```

### Damage Formula

```python
def calculate_damage(attacker, target):
    # Step 1: Base damage with variance
    base_dmg = weapon['damage'] * random(0.85, 1.15)

    # Step 2: Stat bonus
    if weapon['type'] == 'melee':
        stat_bonus = attacker.body * 3
    else:  # ranged
        stat_bonus = attacker.reflexes * 2

    # Step 3: Critical hit
    if random(1, 100) <= attacker.get_crit_chance():
        crit_mult = weapon['crit_multiplier']
    else:
        crit_mult = 1.0

    # Step 4: Morale modifier
    morale_mod = attacker.get_morale_modifier()

    # Step 5: Calculate pre-armor damage
    total = (base_dmg + stat_bonus) * crit_mult * morale_mod

    # Step 6: Armor reduction
    effective_armor = target.armor * (1 - weapon['armor_pen'])
    armor_reduction = effective_armor * ARMOR_REDUCTION_MULTIPLIER
    total -= armor_reduction

    # Step 7: Cover reduction
    if target.in_cover and weapon['type'] != 'tech':
        if target.cover_type == 'half':
            total *= 0.75
        elif target.cover_type == 'full':
            total *= 0.60

    # Minimum 1 damage
    return max(1, int(total))
```

---

## COMBAT SYSTEM

### Combat Flow

```
1. INITIALIZATION
   ├─ Roll initiative for all characters
   ├─ Sort by initiative (highest first)
   ├─ Set first character as current
   └─ Log combat start

2. TURN LOOP
   ├─ Start current character's turn
   │  └─ Reset AP to MAX_AP
   ├─ Execute actions (player or AI)
   │  ├─ Move (1 AP)
   │  ├─ Attack (2 AP)
   │  └─ End turn (0 AP)
   ├─ End character's turn
   │  └─ Set has_acted flag
   ├─ Advance to next character
   │  └─ Skip dead characters
   ├─ Check if round complete
   │  ├─ Increment turn_count
   │  └─ Check escape conditions
   └─ Check victory conditions

3. COMBAT END
   ├─ Player victory (all enemies dead)
   ├─ Player defeat (all players dead)
   └─ Fled (successful escape)
```

### Initiative System

```python
def roll_initiative():
    initiative_rolls = []

    for char in all_characters:
        init = char.get_initiative()  # (Reflexes × 2) + d10
        initiative_rolls.append((init, char))

    # Sort descending
    initiative_rolls.sort(key=lambda x: x[0], reverse=True)

    turn_order = [char for _, char in initiative_rolls]
    current_character = turn_order[0]

    return turn_order, current_character
```

### Turn Management

```python
def next_turn():
    # End current turn
    current_character.end_turn()

    # Advance index
    current_turn_index += 1

    # Check for round completion
    if current_turn_index >= len(turn_order):
        current_turn_index = 0
        turn_count += 1
        check_escape_conditions()

    # Find next alive character
    while current_turn_index < len(turn_order):
        char = turn_order[current_turn_index]
        if char.is_alive:
            current_character = char
            current_character.start_turn()
            break
        else:
            current_turn_index += 1

    check_victory()
```

### Escape System

**Conditions** (Turn 3+):
```python
def check_escape_conditions():
    if turn_count < 3:
        return

    # Calculate average HP
    avg_hp = sum(c.get_hp_percentage() for c in player_alive) / len(player_alive)

    # Check conditions
    low_hp = avg_hp < 50
    casualties = len(player_alive) < len(player_team)
    outnumbered = len(enemy_alive) >= len(player_alive) * 2

    if low_hp or casualties or outnumbered:
        escape_available = True
```

**Escape Attempt:**
```python
def attempt_escape(sacrifice=None):
    if sacrifice:
        chance = 93  # Near-certain with sacrifice
        sacrifice.hp = 0
        sacrifice.is_alive = False
    else:
        leader = player_team[0]
        chance = 45 + (leader.reflexes * 2)
        chance = clamp(chance, 5, 95)

    roll = random(1, 100)

    if roll <= chance:
        # Success
        for char in player_team:
            if char.is_alive:
                char.morale -= 20
        combat_active = False
        victor = 'fled'
        return True

    else:
        # Failure
        if not sacrifice:
            leader.take_damage(leader.max_hp * 0.2)
        return False
```

### Enemy AI

```python
def enemy_ai_turn(enemy):
    targets = get_valid_targets(enemy)

    # Attack if possible
    if targets and enemy.ap >= AP_BASIC_ATTACK:
        target = min(targets, key=lambda t: distance(enemy, t))
        enemy.attack(target)

    # Move toward player
    elif enemy.ap >= AP_MOVE:
        closest_player = min(player_alive, key=lambda p: distance(enemy, p))

        # Simple pathfinding (move one step closer)
        dx = sign(closest_player.x - enemy.x)
        dy = sign(closest_player.y - enemy.y)

        new_x = enemy.x + dx
        new_y = enemy.y + dy

        if is_valid_position(new_x, new_y):
            enemy.move(new_x, new_y)

    # End turn if no AP
    if enemy.ap == 0:
        next_turn()
```

---

## DATA FLOW

### Combat Action Flow

```
USER INPUT (mouse click)
    ↓
MAIN.PY: screen_to_grid(mouse_x, mouse_y)
    ↓
MAIN.PY: Determine action (move/attack)
    ↓
CHARACTER.PY: character.move(x, y) or character.attack(target)
    ↓
CHARACTER.PY: Update state (AP, HP, position)
    ↓
COMBAT.PY: Check victory conditions
    ↓
COMBAT.PY: next_turn()
    ↓
UI.PY: Render updated state
```

### Data Dependencies

```
CONFIG.PY
    ↓
    ├─→ CHARACTER.PY (uses weapon data, constants)
    ├─→ COMBAT.PY (uses AP costs, grid size)
    └─→ UI.PY (uses colors, sizes, layout)

CHARACTER.PY
    ↓
    ├─→ COMBAT.PY (combat uses characters)
    └─→ UI.PY (UI renders characters)

COMBAT.PY
    ↓
    ├─→ MAIN.PY (main orchestrates combat)
    └─→ UI.PY (UI renders combat state)
```

---

## CONFIGURATION MANAGEMENT

### Balance Tuning

All balance parameters centralized for easy iteration:

```python
# In config.py
MAX_ACTION_POINTS = 3  # Try 4 for faster combat
DODGE_CAP = 20         # Try 25 for more survivability
COVER_HALF = 25        # Try 30 for stronger cover

WEAPONS = {
    'assault_rifle': {
        'damage': 30,    # Increase for more lethality
        'accuracy': 85,  # Adjust hit rates
        'range': 12,     # Modify engagement distances
    }
}
```

**Tuning Process:**
1. Modify value in `config.py`
2. Run game to test feel
3. Run test suite to verify balance

    ```bash
    pytest tests/test_character.py -k damage
    ```

4. Iterate until satisfied

### Weapon System

Data-driven weapon definitions:

```python
WEAPONS = {
    'weapon_key': {
        'name': str,           # Display name
        'damage': int,         # Base damage
        'accuracy': int,       # Base hit chance (%)
        'range': int,          # Attack range (tiles)
        'armor_pen': float,    # Armor penetration (0.0-1.0)
        'crit_multiplier': float,  # Critical damage multiplier
        'type': str            # 'melee', 'ranged', 'tech'
    }
}
```

**Adding New Weapon:**
1. Add entry to `WEAPONS` dict in `config.py`
2. No code changes needed
3. Instantly available to all characters

---

## UI/RENDERING ARCHITECTURE

### Rendering Pipeline

```
1. CLEAR SCREEN
   └─ screen.fill(COLOR_BG)

2. DRAW GRID
   └─ Draw grid lines

3. DRAW HIGHLIGHTS
   ├─ Valid move positions (blue)
   └─ Valid attack targets (red)

4. DRAW CHARACTERS
   ├─ For each character:
   │  ├─ Draw circle (team color)
   │  ├─ Draw HP bar
   │  └─ Draw AP bar

5. DRAW UI PANELS
   ├─ Character info panel
   ├─ Combat log
   └─ Action buttons

6. DRAW GAME STATE
   ├─ Victory screen (if won)
   ├─ Defeat screen (if lost)
   └─ Escape screen (if fled)

7. FLIP DISPLAY
   └─ pygame.display.flip()
```

### Coordinate Systems

**Grid Coordinates** (game logic):
```python
(0, 0) to (GRID_WIDTH-1, GRID_HEIGHT-1)
# Example: (10, 7) = center of 20×15 grid
```

**Screen Coordinates** (rendering):
```python
(0, 0) to (SCREEN_WIDTH-1, SCREEN_HEIGHT-1)
# Example: (640, 360) = center of 1280×720 screen
```

**Conversion Functions:**
```python
def grid_to_screen(grid_x, grid_y):
    screen_x = GRID_OFFSET_X + (grid_x * TILE_SIZE) + (TILE_SIZE // 2)
    screen_y = GRID_OFFSET_Y + (grid_y * TILE_SIZE) + (TILE_SIZE // 2)
    return (screen_x, screen_y)

def screen_to_grid(screen_x, screen_y):
    grid_x = (screen_x - GRID_OFFSET_X) // TILE_SIZE
    grid_y = (screen_y - GRID_OFFSET_Y) // TILE_SIZE
    return (grid_x, grid_y)
```

---

## EXTENSION POINTS

### Adding New Systems

**Quest System:**
```python
# quests.py
class Quest:
    def __init__(self, quest_id, title, objectives):
        self.quest_id = quest_id
        self.title = title
        self.objectives = objectives
        self.completed = False

    def check_objectives(self):
        if all(obj.is_complete() for obj in self.objectives):
            self.completed = True
            return self.rewards

# Tests first!
def test_quest_completion():
    quest = Quest("q001", "Find Data Shard", [obj1, obj2])
    quest.complete_objective("obj1")
    quest.complete_objective("obj2")
    assert quest.completed is True
```

**Cyberware System:**
```python
# cyberware.py
class Cyberware:
    def __init__(self, name, slot, stat_bonuses):
        self.name = name
        self.slot = slot  # 'neural', 'optics', 'skeletal', etc.
        self.stat_bonuses = stat_bonuses

    def apply_to(self, character):
        for stat, bonus in self.stat_bonuses.items():
            setattr(character, stat, getattr(character, stat) + bonus)

# Tests first!
def test_cyberware_installation():
    char = create_character()
    cyber = Cyberware("Neural Link", "neural", {'intelligence': 2})
    cyber.apply_to(char)
    assert char.intelligence == original_int + 2
```

---

## PERFORMANCE CONSIDERATIONS

### Current Performance

- **60 FPS target**: Easily maintained
- **Turn calculations**: < 1ms
- **Pathfinding**: Simple, < 1ms
- **Rendering**: < 16ms per frame

### Optimization Strategies

**If performance becomes an issue:**

1. **Cache calculations**
```python
@property
@lru_cache
def movement_range(self):
    return BASE_MOVEMENT_RANGE + (self.reflexes // 4)
```

2. **Spatial partitioning** (for many characters)
```python
class SpatialGrid:
    def get_characters_near(self, x, y, radius):
        # Only check nearby grid cells
        pass
```

3. **Dirty flag rendering** (only redraw changed areas)
```python
if character.moved or character.hp_changed:
    redraw_character(character)
```

---

## VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-12 | Initial architecture documentation |

---

**END OF TECHNICAL ARCHITECTURE BIBLE**

*This document defines the technical implementation and system design of Neon Collapse. All new features must maintain this architecture and follow these patterns.*
