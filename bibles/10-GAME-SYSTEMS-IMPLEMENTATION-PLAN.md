# NEON COLLAPSE - GAME SYSTEMS IMPLEMENTATION PLAN
## Building Core RPG Systems (Option A)

**Version:** 1.0
**Last Updated:** 2025-11-12
**Status:** IMPLEMENTATION ROADMAP

---

## OVERVIEW

This document defines the implementation plan for building the 6 core game systems that will transform Neon Collapse from a combat prototype into a playable RPG.

**Goal:** Create a complete game loop where players can:
1. Accept and complete quests
2. Gain XP and level up
3. Collect and use items
4. Navigate a world map
5. Experience multiple encounters
6. Save and resume progress

---

## SYSTEM 1: QUEST SYSTEM

### Purpose
Track missions, objectives, and rewards. Gives player goals and structure.

### Core Features

**Quest Structure:**
```python
class Quest:
    quest_id: str           # Unique identifier
    title: str              # Display name
    description: str        # Full description
    quest_type: str         # 'main', 'side', 'contract'
    objectives: List[Objective]
    rewards: Rewards
    prerequisites: List[str]  # Required quest IDs
    status: str             # 'available', 'active', 'completed', 'failed'
    district: str           # Where quest takes place
```

**Objective Types:**
- `DefeatEnemies`: Kill X enemies of type Y
- `GoToLocation`: Reach district/location
- `CollectItems`: Gather X items
- `SurviveCombat`: Win battle without losing ally
- `EscapeCombat`: Successfully flee encounter

**Rewards:**
```python
class Rewards:
    xp: int
    credits: int
    items: List[str]
    reputation: Dict[str, int]  # faction -> amount
    unlock_quests: List[str]
```

### Implementation Steps

1. **Test: Quest creation and initialization**
2. **Test: Objective tracking and completion**
3. **Test: Quest state transitions**
4. **Test: Reward distribution**
5. **Test: Prerequisites and unlocking**

### Example Quest

```python
quest = Quest(
    quest_id="q001_rescue_jackie",
    title="Rescue Jackie",
    description="Jackie's been captured by the Tyger Claws. Break into their hideout and get him out.",
    quest_type="main",
    objectives=[
        DefeatEnemies("tyger_claws", count=5),
        SurviveCombat(require_all_alive=False),
        GoToLocation("tyger_claw_hideout")
    ],
    rewards=Rewards(
        xp=500,
        credits=1000,
        items=["medkit", "assault_rifle_mk2"],
        reputation={"fixers": 10}
    ),
    district="watson"
)
```

---

## SYSTEM 2: XP & LEVELING

### Purpose
Character progression. Players get stronger, unlock abilities, feel progress.

### Core Features

**Level Progression:**
- Start at Level 1
- Max Level 20 (for now)
- XP required = Level × 1000 (e.g., Level 2 = 1000 XP, Level 3 = 2000 XP)

**Level Up Rewards:**
- +3 Skill Points to distribute
- +10% Max HP
- +1 to all attributes every 5 levels
- Unlock ability slots at certain levels

**Skill Points:**
Players can spend points to increase attributes:
- Body: 1 point = +1 Body (max 10)
- Reflexes: 1 point = +1 Reflexes (max 10)
- Intelligence: 1 point = +1 Intelligence (max 10)
- Tech: 1 point = +1 Tech (max 10)
- Cool: 1 point = +1 Cool (max 10)

**XP Sources:**
- Defeating enemies: enemy_level × 50 XP
- Completing quests: varies by quest
- Discovering locations: 100 XP each

### Implementation Steps

1. **Test: XP gain and tracking**
2. **Test: Level up threshold calculation**
3. **Test: Level up stat increases**
4. **Test: Skill point allocation**
5. **Test: Attribute caps and validation**

### Example Level Up

```python
# Player at Level 1, gains 1000 XP
character.gain_xp(1000)

# Triggers level up
assert character.level == 2
assert character.skill_points == 3
assert character.max_hp == 150 * 1.1  # +10%

# Player allocates points
character.allocate_skill_point("reflexes")  # 6 -> 7
character.allocate_skill_point("cool")      # 6 -> 7
character.allocate_skill_point("body")      # 5 -> 6
```

---

## SYSTEM 3: INVENTORY SYSTEM

### Purpose
Items, equipment, consumables. Loot and gear management.

### Core Features

**Item Types:**

```python
class Item:
    item_id: str
    name: str
    description: str
    item_type: str  # 'weapon', 'armor', 'consumable', 'cyberware', 'quest'
    value: int      # Credits
    stackable: bool
    max_stack: int

class Weapon(Item):
    damage: int
    accuracy: int
    range: int
    armor_pen: float
    crit_multiplier: float
    weapon_type: str  # 'melee', 'ranged', 'tech'

class Armor(Item):
    armor_value: int
    mobility_penalty: int  # Reduces movement range

class Consumable(Item):
    effect: str     # 'heal', 'buff', 'debuff'
    amount: int     # Healing amount or buff duration
    duration: int   # For temporary effects
```

**Inventory:**
```python
class Inventory:
    max_capacity: int = 50
    items: Dict[str, int]  # item_id -> quantity
    equipped_weapon: Weapon
    equipped_armor: Armor
    equipped_cyberware: List[Cyberware]
```

**Item Actions:**
- `add_item(item, quantity)`: Loot/buy items
- `remove_item(item_id, quantity)`: Use/sell items
- `equip_weapon(weapon)`: Change equipped weapon
- `equip_armor(armor)`: Change equipped armor
- `use_consumable(item)`: Use item in/out of combat

### Implementation Steps

1. **Test: Inventory creation and capacity**
2. **Test: Adding/removing items**
3. **Test: Stacking items**
4. **Test: Equipping weapons/armor**
5. **Test: Using consumables**
6. **Test: Item effects on character stats**

### Example Items

```python
# Weapons
assault_rifle_mk2 = Weapon(
    item_id="weapon_ar_mk2",
    name="Militech M-76E",
    damage=35,  # Better than base
    accuracy=90,
    range=14,
    armor_pen=0.20
)

# Armor
light_armor = Armor(
    item_id="armor_light_01",
    name="Kevlar Vest",
    armor_value=15,
    mobility_penalty=0
)

# Consumables
medkit = Consumable(
    item_id="consumable_medkit",
    name="Medkit",
    effect="heal",
    amount=50,  # Heal 50 HP
    stackable=True,
    max_stack=10
)

bounce_back = Consumable(
    item_id="consumable_bounceback",
    name="Bounce Back",
    effect="heal_over_time",
    amount=5,   # 5 HP per turn
    duration=5   # 5 turns
)
```

---

## SYSTEM 4: WORLD MAP & DISTRICTS

### Purpose
Exploration, navigation, sense of place. Connect encounters and quests.

### Core Features

**District Structure:**
```python
class District:
    district_id: str
    name: str
    description: str
    danger_level: int  # 1-10, affects enemy difficulty
    locations: List[Location]
    connected_to: List[str]  # Adjacent district IDs
    discovered: bool
    faction_control: str  # Which faction controls it

class Location:
    location_id: str
    name: str
    description: str
    location_type: str  # 'combat', 'shop', 'safehouse', 'quest'
    encounter: Optional[CombatEncounter]
    npcs: List[NPC]
    visited: bool
```

**Districts (Initial 3):**

1. **Watson - Industrial District**
   - Danger Level: 3
   - Controlled by: Tyger Claws (gang)
   - Locations: Hideout, Market, Safehouse
   - Starting area

2. **City Center - Corporate Zone**
   - Danger Level: 5
   - Controlled by: Arasaka (corp)
   - Locations: Plaza, Corporate Office, Black Market
   - Mid-game area

3. **Badlands - Wasteland**
   - Danger Level: 7
   - Controlled by: Nomads
   - Locations: Outpost, Scrapyard, Raffen Camp
   - Late-game area

**Navigation:**
- Click district on world map to travel
- Travel costs time (future: encounters en route)
- Some districts locked until quests complete
- Fast travel to discovered safehouses

### Implementation Steps

1. **Test: District creation and properties**
2. **Test: Location discovery**
3. **Test: Travel between districts**
4. **Test: District unlocking via quests**
5. **Test: Location types and interactions**

---

## SYSTEM 5: MULTIPLE ENCOUNTERS

### Purpose
Variety, difficulty curve, replayability.

### Core Features

**Encounter Types:**

```python
class EncounterDefinition:
    encounter_id: str
    name: str
    difficulty: int  # 1-10
    player_team: List[CharacterTemplate]
    enemy_team: List[CharacterTemplate]
    environment: str  # 'urban', 'industrial', 'wasteland'
    victory_rewards: Rewards
    escape_penalty: Rewards  # Negative rewards if fled
```

**Encounter Pool (Initial 10):**

1. **"Gang Ambush"** (Easy)
   - 2 Players vs 3 Grunts
   - Difficulty: 2

2. **"Rescue Mission"** (Medium)
   - 2 Players vs 2 Grunts + 1 Elite
   - Difficulty: 4

3. **"Corporate Security"** (Medium)
   - 2 Players vs 4 Security Guards
   - Difficulty: 5

4. **"Boss: Tyger Claw Lieutenant"** (Hard)
   - 2 Players vs 2 Grunts + 1 Boss
   - Difficulty: 7

5. **"Cyberpsycho"** (Very Hard)
   - 2 Players vs 1 Cyberpsycho (powerful solo enemy)
   - Difficulty: 8

**Enemy Scaling:**
- Base stats scale with encounter difficulty
- Higher difficulty = better weapons, more armor
- Boss enemies have unique abilities (future)

### Implementation Steps

1. **Test: Encounter definition loading**
2. **Test: Dynamic enemy creation from templates**
3. **Test: Difficulty scaling**
4. **Test: Reward distribution**
5. **Create 10 balanced encounters**

---

## SYSTEM 6: SAVE/LOAD SYSTEM

### Purpose
Persistence. Players can stop and resume.

### Core Features

**Save Data Structure:**
```python
class SaveGame:
    version: str = "1.0"
    timestamp: datetime

    # Character Data
    character: CharacterSaveData
    inventory: InventorySaveData

    # Progress Data
    quests: List[QuestSaveData]
    completed_quests: List[str]
    discovered_districts: List[str]
    discovered_locations: List[str]

    # World State
    current_district: str
    current_location: str
    game_time: int  # In-game hours

    # Stats
    total_kills: int
    total_xp_gained: int
    credits_earned: int
```

**Save Format:**
- JSON format (human-readable, debuggable)
- Saved to `saves/` directory
- Auto-save on quest complete, district change
- Manual save at safehouses

**Save Locations:**
```
saves/
├── autosave.json
├── manual_save_1.json
├── manual_save_2.json
└── manual_save_3.json
```

### Implementation Steps

1. **Test: Serialize character data**
2. **Test: Serialize inventory data**
3. **Test: Serialize quest progress**
4. **Test: Save to file**
5. **Test: Load from file**
6. **Test: Validate save data integrity**

---

## IMPLEMENTATION ORDER

### Phase 1: Foundation (Week 1)
1. ✅ Quest system (2 days)
   - Quest class, objectives, rewards
   - Quest tracking and completion
   - Tests: 20+ tests

2. ✅ XP/Leveling (1 day)
   - XP gain, level calculation
   - Skill point allocation
   - Tests: 15+ tests

### Phase 2: Items (Week 1-2)
3. ✅ Inventory system (2 days)
   - Item classes, inventory management
   - Equipment system
   - Consumables
   - Tests: 25+ tests

### Phase 3: World (Week 2)
4. ✅ Districts & Locations (2 days)
   - District navigation
   - Location discovery
   - World state
   - Tests: 15+ tests

5. ✅ Multiple Encounters (1 day)
   - Encounter definitions
   - Enemy templates
   - Create 10 encounters

### Phase 4: Integration (Week 2-3)
6. ✅ Save/Load (2 days)
   - Serialization
   - File I/O
   - Tests: 20+ tests

7. ✅ Game Loop Integration (2 days)
   - Connect all systems
   - Main menu
   - Game flow
   - Tests: 10+ integration tests

---

## TESTING STRATEGY

Each system will have comprehensive tests following TDD:

**Test Categories:**
- **Unit Tests:** Individual components (e.g., quest objective completion)
- **Integration Tests:** System interactions (e.g., quest completion awards XP)
- **Edge Cases:** Boundaries (e.g., max level, inventory full)
- **State Tests:** Persistence (e.g., save/load preserves quest state)

**Coverage Goals:**
- Each new system: 90%+ coverage
- Critical paths: 100% coverage
- Overall maintained: 85%+

---

## SUCCESS CRITERIA

When complete, the game should:

✅ **Quest Flow:**
- Accept quest from menu
- View objectives
- Complete objectives through gameplay
- Receive rewards automatically

✅ **Progression:**
- Gain XP from combat and quests
- Level up with clear feedback
- Allocate skill points
- See character get stronger

✅ **Inventory:**
- Find loot after combat
- Manage inventory
- Equip better gear
- Use consumables in combat

✅ **Exploration:**
- Navigate between districts
- Discover new locations
- Unlock areas via quests
- See world state persist

✅ **Variety:**
- Fight different enemy compositions
- Experience difficulty curve
- Feel tactical variety

✅ **Persistence:**
- Save progress at any time
- Load save and resume exactly where left off
- Multiple save slots

---

## NEXT STEPS

**Immediate:**
1. Start with Quest System implementation
2. Write tests first (TDD)
3. Implement to pass tests
4. Document patterns

**Follow-up:**
Each system builds on the previous, so order matters!

---

**END OF IMPLEMENTATION PLAN**

*This plan will transform Neon Collapse from a combat prototype into a complete RPG with progression, exploration, and persistence.*
