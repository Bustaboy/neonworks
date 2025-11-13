# NEON COLLAPSE - QUICK REFERENCE GUIDE

## Documentation Guide

### For Understanding the Game Design
- **STORY**: bibles/01-STORY-BIBLE-MASTER.md
- **CHARACTERS**: bibles/02-CHARACTER-BIBLE.md
- **WORLD**: bibles/05-WORLD-BUILDING-MASTER.md
- **MECHANICS**: bibles/08-GAME-MECHANICS-BIBLE.md

### For Understanding the Code
- **OVERVIEW**: EXPLORATION_SUMMARY.txt (start here!)
- **DETAILED ANALYSIS**: CODEBASE_ANALYSIS.md (comprehensive)
- **ARCHITECTURE**: ARCHITECTURE_SUMMARY.md (patterns & design)
- **SYSTEM FLOWS**: SYSTEM_INTERACTIONS.md (diagrams)

### For Development
- **TESTING**: README_TESTING.md (test framework)
- **PROGRESS**: PROGRESS_SUMMARY.md (implementation status)
- **COMBAT TDD**: Neon-Collapse-Combat-TDD-v3-ESCAPE-SYSTEM-ADDED.md

---

## Quick Stats

```
Total Code:         9,509 lines (25 modules)
Test Suite:         882 tests (all passing)
Code Coverage:      79% overall, 95%+ critical systems
Test Execution:     6 seconds
Architecture:       TDD, manager pattern, configuration-driven
Dependencies:       Minimal (no circular imports)
Production Ready:   YES
```

---

## Core Game Systems (19 Total)

### Essential Systems (Must Copy)
1. **character.py** (223 lines, 96% coverage)
   - 5 attributes (Body, Reflexes, Intelligence, Tech, Cool)
   - Combat calculations
   - Initiative, dodge, crit formulas

2. **combat.py** (275 lines, 89% coverage)
   - Turn-based combat
   - Action Points (1-3 per turn)
   - Hit/damage/morale calculations
   - Escape mechanics

3. **quest.py** (404 lines, 75% coverage)
   - 4 objective types
   - Reward system
   - State machine

4. **faction.py** (303 lines, 97% coverage)
   - 7 factions with rival mechanics
   - Reputation tracking
   - Reward unlocks

5. **inventory.py** (603 lines, 70% coverage)
   - 5 item types
   - 8 cyberware slots
   - Equipment system

### Game Loop Systems
6. **skill_xp.py** (246 lines, 85% coverage)
   - Learn-by-doing progression
   - No character levels

7. **world_map.py** (396 lines, 84% coverage)
   - 3 districts, locations
   - Safe house with upgrades

8. **save_load.py** (362 lines, 73% coverage)
   - 3 save slots + autosave
   - Full state serialization

9. **encounters.py** (658 lines, 94% coverage)
   - 11 encounter templates
   - Enemy scaling by phase
   - Loot tables

10. **companions.py** (634 lines, 82% coverage)
    - AI party members
    - Relationship tracking

### Advanced Mechanics
11. **cover_system.py** (363 lines, 85% coverage)
    - Half/full cover
    - Flanking bonuses

12. **stealth.py** (407 lines, 92% coverage)
    - Crouch movement
    - Detection system

13. **status_effects.py** (287 lines, 87% coverage)
    - Buffs/debuffs
    - Duration tracking

14. **hacking.py** (467 lines, 93% coverage)
    - Netrunner mini-game
    - RAM management

15. **dialogue.py** (341 lines, 81% coverage)
    - Branching conversations
    - Reputation-gated dialogue

16. **crafting.py** (516 lines, 83% coverage)
    - Recipe system
    - Tech XP progression

17. **vendors.py** (517 lines, 93% coverage)
    - NPC shops
    - Buy/sell mechanics

18. **loot_economy.py** (470 lines, 94% coverage)
    - Loot drops
    - Rarity tiers

19. **random_events.py** (456 lines, 90% coverage)
    - Dynamic events
    - Consequence system

---

## Development Commands

```bash
# Testing
make test               # Run all tests
make test-cov           # With coverage report
make test-quick         # Quick smoke tests
make test-character     # Specific system

# Code Quality
make format             # Auto-format code
make lint               # Check code style
make typecheck          # Type analysis
make ci                 # All checks

# Running
make run                # Start game
make help               # Show all commands

# Setup
make install            # Install dependencies
make install-dev        # Dev dependencies only
```

---

## Key Formulas

### Combat
```
Initiative = (Reflexes × 2) + d10
Hit Chance = Weapon.Accuracy - (Target.Reflexes × 3) ± Modifiers [5-95%]
Damage = (Base × Variance + StatBonus) × CritMult × MoraleMult - Armor [min 1]
  - Base: Weapon.Damage
  - Variance: 0.85-1.15 random
  - StatBonus: Reflexes×2 (ranged) or Body×3 (melee)
  - CritMult: 2.0x if roll ≤ (Cool × 2)%
  - MoraleMult: 1.0 + ((Morale - 50) / 200)
  - Armor: Target.Armor × (1 - Weapon.ArmorPen)
```

### Progression
```
Skill XP Threshold = 100 × 1.5^(current_level - 3)
  - Level 3→4: 100 XP
  - Level 4→5: 150 XP
  - Level 9→10: 1139 XP
```

### Economy
```
Loot = Difficulty-based (100-3000 eddies)
Building Income = Base(100) + Buildings(+500 each) + Population(+5 per) × Efficiency
District Income Cap = 10,000 eddies/hour
```

---

## File Organization

```
game/
├── Core Logic (testable, pure)
│   ├── character.py
│   ├── quest.py
│   ├── faction.py
│   ├── inventory.py
│   ├── skill_xp.py
│   ├── world_map.py
│   └── config.py (balance)
│
├── Game Systems (manager pattern)
│   ├── combat.py
│   ├── encounters.py
│   ├── save_load.py
│   ├── companions.py
│   └── district_building.py
│
├── Subsystems (advanced mechanics)
│   ├── cover_system.py
│   ├── stealth.py
│   ├── status_effects.py
│   ├── hacking.py
│   ├── dialogue.py
│   ├── crafting.py
│   ├── vendors.py
│   ├── loot_economy.py
│   ├── random_events.py
│   ├── ai_director.py
│   └── achievements.py
│
├── Integration (Pygame)
│   ├── main.py
│   └── ui.py
│
└── Config
    └── requirements.txt

tests/
├── conftest.py (shared fixtures)
└── test_*.py (25 test files)
```

---

## Architecture Patterns

### Pattern 1: Manager Pattern
```python
class QuestManager:
    def add_quest(quest): pass
    def complete_quest(quest_id): pass
    def get_quest(quest_id): pass

# Centralized control, easy serialization
```

### Pattern 2: Serialization First
```python
class System:
    def to_dict(self) -> dict:
        return {...}
    
    @classmethod
    def from_dict(cls, data) -> 'System':
        return cls(...)
```

### Pattern 3: Configuration Driven
```python
# config.py
WEAPONS = {
    'assault_rifle': {
        'damage': 30,
        'accuracy': 85,
        ...
    }
}

# Change balance without code changes!
```

### Pattern 4: Dependency Injection
```python
class CombatEncounter:
    def __init__(self, player_team, enemy_team):
        self.player_team = player_team  # Passed in, not hardcoded
        self.enemy_team = enemy_team
```

---

## Testing Fixtures

```python
# Character Fixtures
@pytest.fixture
def player_character(): ...      # Balanced stats

@pytest.fixture
def elite_enemy(): ...           # Strong enemy

# Combat Fixtures
@pytest.fixture
def basic_combat_scenario(): ... # 1v1 fight

# Mock Fixtures
@pytest.fixture
def mock_pygame(): ...           # Pygame mock
```

---

## Test Coverage by System

| System | Coverage | Notes |
|--------|----------|-------|
| faction.py | 97% | Nearly perfect |
| character.py | 96% | Excellent |
| encounters.py | 94% | Excellent |
| loot_economy.py | 94% | Excellent |
| vendors.py | 93% | Excellent |
| hacking.py | 93% | Excellent |
| stealth.py | 92% | Very good |
| **AVERAGE** | **79%** | **Good** |

---

## Getting Started with Custom Engine

### Step 1: Copy Foundation (30 min)
```bash
cp game/character.py your_game/
cp game/combat.py your_game/
cp game/quest.py your_game/
cp tests/conftest.py your_game/tests/
```

### Step 2: Update Config (1 hour)
```python
# Modify config.py for your game
WEAPONS = {...}           # Your weapons
ATTRIBUTES = [...]        # Your stats
BALANCE_PARAMS = {...}    # Your balance
```

### Step 3: Create Tests First (2-3 hours)
```python
# Write failing test
def test_new_system():
    system = NewSystem()
    assert system.works()

# Make it pass (TDD)
class NewSystem:
    def works(self):
        return True
```

### Step 4: Run Test Suite (5 min)
```bash
make test       # 882 tests in 6 seconds
make test-cov   # Check coverage
```

---

## Common Pitfalls to Avoid

```python
# DON'T: Mix logic and rendering
if character.hp < 0:
    pygame.draw.text("Dead!")  # Bad!

# DO: Separate concerns
if character.hp < 0:
    game_state = "dead"  # Logic
    ui.show_dead_screen()   # Rendering

# DON'T: Hardcode balance
damage = 30  # Bad!

# DO: Use config
damage = config.WEAPONS['rifle']['damage']  # Good!

# DON'T: Global state
player = None  # Bad global!

# DO: Inject dependencies
class Combat:
    def __init__(self, player):
        self.player = player  # Good!
```

---

## Performance Targets

- Tests: < 10 seconds (currently 6 sec)
- Game Loop: 60 FPS target
- Load Time: < 2 seconds
- Memory: Reasonable for turn-based game

---

## Recommended Reading Order

1. **EXPLORATION_SUMMARY.txt** (this directory)
   → 5 min overview

2. **ARCHITECTURE_SUMMARY.md**
   → 30 min understanding patterns

3. **SYSTEM_INTERACTIONS.md**
   → 30 min seeing how systems connect

4. **CODEBASE_ANALYSIS.md**
   → 1-2 hours deep dive

5. **bibles/ folder**
   → Game design reference

6. **game/*.py files**
   → Implementation examples

7. **tests/*.py files**
   → Testing patterns

---

## Useful Links in Codebase

- **TDD Guide**: README_TESTING.md
- **Game Design**: bibles/06-TDD-GAME-SYSTEMS-BIBLE.md
- **Technical**: bibles/07-TECHNICAL-ARCHITECTURE-BIBLE.md
- **Mechanics**: bibles/08-GAME-MECHANICS-BIBLE.md
- **Testing**: bibles/09-TESTING-BIBLE-TDD-PATTERNS.md

---

## Final Tips

1. **Start Small**
   - Copy character.py first
   - Get combat working
   - Expand from there

2. **Follow TDD**
   - Write test first
   - Implement code
   - Refactor

3. **Keep It Simple**
   - Don't over-engineer
   - Use patterns from this codebase
   - Ship early, iterate

4. **Test Everything**
   - Aim for 80%+ coverage
   - Test edge cases
   - Run suite before commits

5. **Use Config for Balance**
   - Never hardcode values
   - Easy rebalancing
   - A/B testing ready

---

**Total Documentation Created**:
- CODEBASE_ANALYSIS.md (29 KB)
- ARCHITECTURE_SUMMARY.md (14 KB)
- SYSTEM_INTERACTIONS.md (21 KB)
- EXPLORATION_SUMMARY.txt (14 KB)
- QUICK_REFERENCE.md (this file)

**Total Time Investment**: Well spent - you now have a complete blueprint for your custom game engine!
