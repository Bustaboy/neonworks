# NEON COLLAPSE - SYSTEM INTERACTIONS DIAGRAM

## Game Systems Dependency Graph

```
                         CONFIG.PY
                      (All Constants)
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
    CHARACTER            WEAPONS             BALANCE
    (5 Attributes)    (Stat Templates)   (All Formulas)
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                            ▼
        ┌─────────────────────────────────────┐
        │      CORE GAME STATE (Pure Logic)   │
        │  (Highly Testable, No Side Effects) │
        ├─────────────────────────────────────┤
        │ • character.py (96% coverage)       │
        │ • quest.py (75% coverage)           │
        │ • faction.py (97% coverage)         │
        │ • inventory.py (70% coverage)       │
        │ • skill_xp.py (85% coverage)        │
        │ • world_map.py (84% coverage)       │
        └─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
    COMBAT.PY         ENCOUNTERS.PY      SAVE_LOAD.PY
    Turn-Based        Enemy Scaling      Persistence
    (89% coverage)    (94% coverage)     (73% coverage)
        │                   │                   │
        │                   ▼                   │
        │           AI_DIRECTOR.PY             │
        │           Dynamic Difficulty         │
        │           (83% coverage)             │
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                            ▼
        ┌─────────────────────────────────────┐
        │    GAME SYSTEMS (Manager Pattern)   │
        │  (Orchestration, Centralized State) │
        ├─────────────────────────────────────┤
        │ • companions.py (82% coverage)      │
        │ • district_building.py (88% cov)    │
        └─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
    SUBSYSTEMS         SUBSYSTEMS         SUBSYSTEMS
    (Strategic)        (Gameplay)         (Economy)
        │                   │                   │
        ├─────────────┐     ├──────────┐       ├──────────┐
        ▼             ▼     ▼          ▼       ▼          ▼
    COVER_SYSTEM  STEALTH HACKING   DIALOGUE CRAFTING   VENDORS
    (85%)         (92%)    (93%)     (81%)    (83%)      (93%)
        │             │      │         │        │          │
        │             │      │         │        │          │
        └─────────────┼──────┼─────────┼────────┼──────────┘
                      │
                      ▼
        ┌─────────────────────────────────────┐
        │    CROSS-SYSTEM SUBSYSTEMS          │
        ├─────────────────────────────────────┤
        │ • status_effects.py (87% coverage)  │
        │ • loot_economy.py (94% coverage)    │
        │ • random_events.py (90% coverage)   │
        │ • achievements.py (89% coverage)    │
        └─────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────────────┐
        │   INTEGRATION LAYER (Pygame)        │
        │  (Orchestration + Rendering)        │
        ├─────────────────────────────────────┤
        │ • main.py (7% - mostly pygame)      │
        │ • ui.py (8% - mostly pygame)        │
        └─────────────────────────────────────┘
                      │
                      ▼
                 PYGAME DISPLAY
```

---

## Quest System Integration

```
QUEST SYSTEM (Quest.py)
    │
    ├─► Objectives (4 Types)
    │   ├─ DefeatEnemies
    │   │   └─► References: ENCOUNTERS.PY, COMBAT.PY
    │   │
    │   ├─ GoToLocation
    │   │   └─► References: WORLD_MAP.PY
    │   │
    │   ├─ SurviveCombat
    │   │   └─► References: COMBAT.PY
    │   │
    │   └─ CollectItems
    │       └─► References: INVENTORY.PY
    │
    ├─► Rewards
    │   ├─ XP Gain → SKILL_XP.PY
    │   ├─ Credits → INVENTORY.PY
    │   ├─ Items → INVENTORY.PY
    │   └─ Reputation → FACTION.PY
    │
    ├─► State Machine
    │   └─► Serialized by: SAVE_LOAD.PY
    │
    └─► QuestManager
        └─► Serialized by: SAVE_LOAD.PY
```

---

## Combat System Flow

```
COMBAT ENCOUNTER START
    │
    ├─► Initialize Characters (from CHARACTER.PY)
    │
    ├─► Roll Initiative
    │   └─► Formula: (Reflexes × 2) + d10 roll
    │
    ├─► Enter Turn Loop
    │   │
    │   ├─► Player Turn (if current team = 'player')
    │   │   ├─ Move (1 AP) → Update position
    │   │   ├─ Attack (2 AP) → Check hit, apply damage
    │   │   │   └─► Hit Calculation:
    │   │   │       ├─ Base: weapon.accuracy - target.dodge
    │   │   │       ├─ Cover: adjust -25% or -40%
    │   │   │       └─ Result: 5%-95%
    │   │   │
    │   │   └─► Damage Calculation:
    │   │       ├─ Base: weapon.damage × 0.85-1.15 variance
    │   │       ├─ Stat: Body×3 (melee) or Reflexes×2 (ranged)
    │   │       ├─ Crit: roll ≤ Cool×2% → ×2.0 damage
    │   │       ├─ Morale: ×(1 + ((morale-50)/200))
    │   │       ├─ Armor: -target.armor × (1 - weapon.armor_pen)
    │   │       └─ Min: 1 damage
    │   │
    │   ├─► Enemy Turn (if current team = 'enemy')
    │   │   └─► AI_DIRECTOR.PY makes decision
    │   │       ├─ If in range: attack
    │   │       └─ Else: move closer
    │   │
    │   ├─► Check Victory (every turn)
    │   │   ├─ All enemies dead → Player victory
    │   │   ├─ All players dead → Enemy victory
    │   │   └─ Turn 3+ with conditions → Escape available
    │   │
    │   └─► Loop continues until victory/defeat/escape
    │
    ├─► Combat End
    │   │
    │   ├─ Calculate Rewards
    │   │   ├─► Get loot from LOOT_ECONOMY.PY
    │   │   ├─► Add items to INVENTORY.PY
    │   │   └─► Award XP to SKILL_XP.PY
    │   │
    │   ├─ Check Quest Objectives
    │   │   └─► Update QUEST.PY objectives
    │   │
    │   ├─ Trigger Random Events
    │   │   └─► RANDOM_EVENTS.PY may trigger
    │   │
    │   └─ Autosave Game State
    │       └─► SAVE_LOAD.PY serializes everything
    │
    └─► Return to Main Game Loop
```

---

## Progression System Integration

```
PLAYER ACTION
    │
    ├─► COMBAT ACTION (Attack, Kill, etc.)
    │   │
    │   └─► SKILL_XP.PY tracks:
    │       ├─ Melee damage → Body XP
    │       ├─ Ranged damage → Reflexes XP
    │       ├─ Critical kill → Cool XP
    │       └─ Level up at thresholds (100 × 1.5^(level-3))
    │
    ├─► CRAFTING ACTION (Use workbench)
    │   │
    │   └─► SKILL_XP.PY tracks:
    │       └─ Crafting attempt → Tech XP
    │
    ├─► HACKING ACTION (Breach system)
    │   │
    │   └─► SKILL_XP.PY tracks:
    │       └─ Successful hack → Intelligence XP
    │
    ├─► FACTION ACTIVITY (Complete mission)
    │   │
    │   └─► FACTION.PY updates:
    │       ├─ Add reputation to faction
    │       ├─ Subtract from rival factions
    │       ├─ Check level up (every 50 rep)
    │       └─ Check reward unlock (vendor discount, access, etc.)
    │
    └─► QUEST COMPLETION (Finish objective)
        │
        └─► QUEST.PY triggers:
            ├─ Add quest rewards:
            │   ├─ XP → SKILL_XP.PY
            │   ├─ Credits → INVENTORY.PY
            │   ├─ Items → INVENTORY.PY
            │   └─ Reputation → FACTION.PY
            │
            └─ Check next quests:
                └─► QUEST.PY QuestManager handles unlocks
```

---

## Inventory & Equipment System

```
INVENTORY SYSTEM (inventory.py)
    │
    ├─► Item Types (5)
    │   ├─ WEAPON
    │   │   ├─ damage, accuracy, range
    │   │   ├─ armor_pen, crit_multiplier
    │   │   └─ Uses: COMBAT.PY (damage calculation)
    │   │
    │   ├─ ARMOR
    │   │   ├─ armor_value, mobility_penalty
    │   │   └─ Uses: COMBAT.PY (damage reduction)
    │   │
    │   ├─ CONSUMABLE
    │   │   ├─ effect type, amount, duration
    │   │   └─ Uses: COMBAT.PY (during combat)
    │   │
    │   ├─ CYBERWARE
    │   │   ├─ 8 body slots (1 per slot)
    │   │   ├─ abilities, passive_effect
    │   │   └─ Uses: CHARACTER.PY (stat bonuses)
    │   │
    │   └─ GENERIC
    │       └─ Miscellaneous items
    │
    ├─► Inventory Management
    │   ├─ 50 slot capacity
    │   ├─ Stacking for stackable items
    │   ├─ Add/remove items
    │   └─ Equip/unequip gear
    │
    ├─► Equipment System
    │   ├─ Equipped weapon → used in COMBAT.PY
    │   ├─ Equipped armor → used in COMBAT.PY
    │   └─ Installed cyberware → stat bonuses in CHARACTER.PY
    │
    ├─► Serialization
    │   └─► Used by SAVE_LOAD.PY
    │
    └─► Integration Points
        ├─ VENDORS.PY: buying/selling items
        ├─ CRAFTING.PY: creating items
        ├─ LOOT_ECONOMY.PY: looting defeated enemies
        └─ QUEST.PY: quest reward items
```

---

## Faction System with Rival Mechanics

```
FACTION SYSTEM (faction.py)
    │
    ├─► 7 Factions
    │   ├─ The Syndicate (rivals: Militech, Voodoo Boys)
    │   ├─ Trauma Corp (rivals: none - neutral)
    │   ├─ Militech (rivals: Syndicate, Nomads)
    │   ├─ Tyger Claws (rivals: Voodoo Boys, Scavengers)
    │   ├─ Voodoo Boys (rivals: Syndicate, Tyger Claws)
    │   ├─ Nomads (rivals: Militech, Scavengers)
    │   └─ Scavengers (rivals: Tyger Claws, Nomads)
    │
    ├─► Reputation Tracking
    │   ├─ Range: -100 to +500
    │   ├─ Levels: 0-10 (every 50 rep)
    │   ├─ Status: Neutral / Allied / Hostile
    │   └─ Rival impact: +30 faction → -15 rival
    │
    ├─► Reputation Sources
    │   ├─ QUEST.PY: quest completion rewards reputation
    │   ├─ ENCOUNTERS.PY: defeating enemy faction increases rep
    │   └─ VENDORS.PY: buying from faction increases rep
    │
    ├─► Reputation Effects
    │   ├─ VENDORS.PY: discount pricing (-5% per level cap 50%)
    │   ├─ DIALOGUE.PY: unlock faction-specific dialogue
    │   ├─ AI_DIRECTOR.PY: enemy difficulty scaling
    │   └─ RANDOM_EVENTS.PY: faction-specific events
    │
    ├─► Reward Unlocks
    │   ├─ Level 1: Basic vendor access
    │   ├─ Level 2: 10% vendor discount
    │   ├─ Level 4: Faction backup available
    │   ├─ Level 8: Ending path unlocked
    │   └─ Level 10: Free gear (100% discount)
    │
    └─► Serialization
        └─► Used by SAVE_LOAD.PY
```

---

## District Building System Loop

```
DISTRICT BUILDING (district_building.py)
    │
    ├─► Income Generation (every game hour)
    │   ├─ Base: 100 eddies
    │   ├─ Building income: +500 per building
    │   ├─ Population bonus: +5 per person
    │   ├─ Efficiency: × (1 + infrastructure%)
    │   ├─ Cap: 10,000 eddies/hour
    │   └─ Updates: INVENTORY.PY (add credits)
    │
    ├─► Population Management
    │   ├─ Growth: 0.5 people/hour (if under capacity)
    │   ├─ Capacity: 5 + housing
    │   └─ Security impact: +1 per 5 people
    │
    ├─► Security System
    │   ├─ Security: 5 + defense buildings + (population / 5)
    │   ├─ Threat: (100 - security) + (pop / 2) + (income / 500)
    │   └─ Attack chance: threat / 200 (cap 80%)
    │
    ├─► Random Events (20% per check)
    │   ├─ Attacks (70% if security < 30)
    │   │   └─► Combat: COMBAT.PY generates enemy team
    │   │
    │   ├─ Trade Opportunities (50% if population > 30)
    │   │   └─► Dialogue: DIALOGUE.PY opens conversation
    │   │
    │   └─ Scavenger Finds (baseline)
    │       └─► Loot: LOOT_ECONOMY.PY generates items
    │
    ├─► Building Placement
    │   ├─ 4 Categories: Housing, Commerce, Defense, Infrastructure
    │   ├─ Slots available: 10 (level 1) → 28 (level 10)
    │   └─ Cost: 500-12,000 eddies per building
    │
    ├─► District Upgrades
    │   ├─ Cost: 5000 × (level × 1.5)
    │   ├─ Slots unlock: +2-8 per level
    │   ├─ Buildings unlock: Progression gates
    │   └─ Updates: INVENTORY.PY (spend credits)
    │
    └─► Serialization
        └─► Used by SAVE_LOAD.PY
```

---

## Save/Load System Hub

```
SAVE_LOAD.PY (Persistence Hub)
    │
    ├─► Input: All game systems to save
    │   │
    │   ├─ CHARACTER.PY state
    │   │   └─ Attributes, HP, position, status
    │   │
    │   ├─ QUEST.PY state
    │   │   └─ All quests, objectives, progress
    │   │
    │   ├─ FACTION.PY state
    │   │   └─ All faction reputation, levels, status
    │   │
    │   ├─ INVENTORY.PY state
    │   │   └─ Items, equipped gear, cyberware
    │   │
    │   ├─ SKILL_XP.PY state
    │   │   └─ Attribute levels, XP, skill points
    │   │
    │   ├─ WORLD_MAP.PY state
    │   │   └─ Locations discovered, current location
    │   │
    │   └─ DISTRICT_BUILDING.PY state
    │       └─ Buildings, population, income
    │
    ├─► Processing
    │   ├─ Call to_dict() on each system
    │   ├─ Serialize to JSON
    │   ├─ Write to file (slots 1-3, autosave)
    │   └─ Validation checks
    │
    ├─► Output: Save File
    │   ├─ Metadata (timestamp, playtime, version)
    │   ├─ Full serialized game state
    │   └─ Corruption detection
    │
    └─► Load Path
        ├─ Read save file
        ├─ Validate JSON structure
        ├─ Call from_dict() on each system
        ├─ Restore all game state
        └─ Return to game
```

---

## Testing Infrastructure

```
CONFTEST.PY (Shared Fixtures)
    │
    ├─► CHARACTER Fixtures (7)
    │   ├─ player_character
    │   ├─ ally_character
    │   ├─ enemy_character
    │   ├─ elite_enemy
    │   ├─ weak_character
    │   ├─ strong_character
    │   └─ melee_character
    │
    ├─► COMBAT Fixtures (3)
    │   ├─ basic_combat_scenario (1v1)
    │   ├─ team_combat_scenario (2v2)
    │   └─ outnumbered_scenario (1v2)
    │
    ├─► MOCK Fixtures (3)
    │   ├─ mock_pygame
    │   ├─ mock_screen
    │   └─ mock_font
    │
    └─► Test Files (25)
        ├─ test_character.py (68 tests, 96%)
        ├─ test_combat.py (64 tests, 89%)
        ├─ test_quest.py (30 tests, 75%)
        ├─ test_faction.py (32 tests, 97%)
        ├─ test_inventory.py (44 tests, 70%)
        ├─ test_encounters.py (31 tests, 94%)
        ├─ test_skill_xp.py (32 tests, 85%)
        ├─ test_world_map.py (49 tests, 84%)
        ├─ test_save_load.py (29 tests, 73%)
        ├─ test_district_building.py (39 tests, 88%)
        ├─ test_companions.py (47 tests, 82%)
        ├─ test_cover_system.py (47 tests, 85%)
        ├─ test_stealth.py (30 tests, 92%)
        ├─ test_status_effects.py (44 tests, 87%)
        ├─ test_hacking.py (33 tests, 93%)
        ├─ test_dialogue.py (39 tests, 81%)
        ├─ test_crafting.py (40 tests, 83%)
        ├─ test_vendors.py (35 tests, 93%)
        ├─ test_loot_economy.py (35 tests, 94%)
        ├─ test_random_events.py (33 tests, 90%)
        ├─ test_ai_director.py (19 tests, 83%)
        ├─ test_achievements.py (19 tests, 89%)
        ├─ test_ui.py (5 tests, skipped)
        ├─ test_main.py (1 test, skipped)
        └─ Total: 882 tests, 79% coverage, 6 seconds
```

---

## Key Interaction Patterns

### Pattern 1: Manager Pattern (Centralized Control)
```python
# Example: QuestManager
manager = QuestManager()
manager.add_quest(quest)
manager.activate_quest("quest_id")
manager.update_objective("quest_id", objective_data)
if quest.all_objectives_complete():
    rewards = manager.complete_quest("quest_id")
    # Rewards distributed to appropriate systems
```

### Pattern 2: Serialization First
```python
# Every system implements:
class System:
    def to_dict(self):
        return {...}  # Fully serializable state
    
    @classmethod
    def from_dict(cls, data):
        return cls(...)  # Reconstruct from saved state

# Enables: save_load.py can handle ANY system state
```

### Pattern 3: Configuration Driven
```python
# config.py contains all balance
WEAPONS = {
    'assault_rifle': {
        'damage': 30,
        'accuracy': 85,
        # ... all stats
    }
}

# Result: Change balance without touching game logic
```

### Pattern 4: Dependency Injection
```python
# Pass dependencies, don't hardcode them
class CombatEncounter:
    def __init__(self, player_team, enemy_team):
        # Systems receive their dependencies
        self.player_team = player_team
        self.enemy_team = enemy_team

# Testable: Can pass mock objects in tests
# Flexible: Can pass any compatible team
```

---

## System Communication Rules

1. **No Direct Imports Between Systems** (except config)
   - Systems communicate through main.py
   - Prevents circular dependencies
   - Enables independent testing

2. **Manager as Central Hub**
   - All query operations go through manager
   - Single source of truth for collections
   - Easy to find where state changes

3. **Serialization for State Transfer**
   - Systems expose to_dict / from_dict
   - Save_load.py orchestrates full serialization
   - Enables undo/replay functionality

4. **Configuration for Balance**
   - No hardcoded values in systems
   - All balance in config.py
   - Easy A/B testing and tuning

5. **Event Callbacks for Cross-System Notifications**
   - Optional callbacks (on_faction_level_up)
   - Systems can subscribe to events
   - Decouples dependent systems

