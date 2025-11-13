# NEON COLLAPSE - GAME MECHANICS BIBLE
## Complete Rules Reference & System Documentation

**Version:** 1.0
**Last Updated:** 2025-11-12
**Status:** MASTER REFERENCE DOCUMENT

---

## TABLE OF CONTENTS

1. [Core Attributes](#core-attributes)
2. [Combat Mechanics](#combat-mechanics)
3. [Action Point System](#action-point-system)
4. [Initiative System](#initiative-system)
5. [Hit Chance System](#hit-chance-system)
6. [Damage System](#damage-system)
7. [Morale System](#morale-system)
8. [Movement System](#movement-system)
9. [Escape System](#escape-system)
10. [Weapon System](#weapon-system)
11. [Future Systems](#future-systems)

---

## CORE ATTRIBUTES

### The Five Attributes (1-10 scale)

**BODY** - Physical strength and resilience
- **Affects:** Melee damage, HP, carrying capacity
- **Primary for:** Melee fighters, tanks
- **Damage bonus:** Body × 3 (melee weapons only)
- **Examples:**
  - Body 1: Frail, weak
  - Body 5: Average strength
  - Body 10: Superhuman, cyborg-enhanced

**REFLEXES** - Speed, agility, and reaction time
- **Affects:** Initiative, dodge chance, ranged damage, movement range
- **Primary for:** Gunfighters, scouts
- **Damage bonus:** Reflexes × 2 (ranged weapons)
- **Dodge formula:** min(20, Reflexes × 3)
- **Initiative formula:** (Reflexes × 2) + d10
- **Movement bonus:** Reflexes ÷ 4 (rounded down)
- **Examples:**
  - Reflexes 1: Slow, clumsy
  - Reflexes 5: Average speed
  - Reflexes 10: Lightning-fast reactions

**INTELLIGENCE** - Mental capacity and problem-solving
- **Affects:** Tech use, hacking, perception
- **Primary for:** Netrunners, tacticians
- **Future uses:** Hack success chance, scan effectiveness
- **Examples:**
  - Intelligence 1: Limited reasoning
  - Intelligence 5: Average intellect
  - Intelligence 10: Genius-level

**TECH** - Technical skill and crafting ability
- **Affects:** Equipment use, crafting, cyberware compatibility
- **Primary for:** Engineers, riggers
- **Future uses:** Crafting quality, repair effectiveness
- **Examples:**
  - Tech 1: Barely uses technology
  - Tech 5: Competent technician
  - Tech 10: Master engineer

**COOL** - Composure under pressure, charisma
- **Affects:** Critical hit chance, morale loss resistance, social
- **Primary for:** Leaders, assassins
- **Crit formula:** Cool × 2%
- **Examples:**
  - Cool 1: Panics easily
  - Cool 5: Stays calm
  - Cool 10: Unshakeable

### Stat Synergies

**Combat Builds:**
```
MELEE FIGHTER
Body:       8-10 (damage)
Reflexes:   6-7  (defense, initiative)
Cool:       6-8  (crits)
Other:      3-5

RANGED SNIPER
Reflexes:   9-10 (damage, dodge)
Cool:       8-9  (crits)
Body:       3-4  (survival)
Other:      3-5

BALANCED SOLDIER
Body:       5-6
Reflexes:   6-7
Cool:       5-6
Intelligence: 4-5
Tech:       4-5
```

---

## COMBAT MECHANICS

### Combat Flow

```
1. COMBAT INITIALIZATION
   ├─ All characters roll initiative
   ├─ Turn order established (highest to lowest)
   └─ Combat begins

2. CHARACTER TURN
   ├─ Start turn (AP restored to 3)
   ├─ Available actions:
   │  ├─ Move (1 AP)
   │  ├─ Basic Attack (2 AP)
   │  ├─ Use Item (1 AP, future)
   │  ├─ Special Ability (3 AP, future)
   │  └─ End Turn (0 AP)
   └─ End turn

3. ROUND COMPLETION
   ├─ All characters have taken a turn
   ├─ Turn counter increments
   ├─ Check escape conditions (turn 3+)
   └─ Next round begins

4. COMBAT END
   ├─ Victory: All enemies defeated
   ├─ Defeat: All players defeated
   └─ Fled: Successful escape
```

### Turn Order

- **Determined by:** Initiative rolls at combat start
- **Order:** Highest initiative to lowest
- **Ties:** Resolved by who rolled first (implementation detail)
- **Dead characters:** Skipped in turn order
- **Unchanging:** Initiative doesn't re-roll each turn

---

## ACTION POINT SYSTEM

### Action Point Costs

| Action | Cost | Description |
|--------|------|-------------|
| Move | 1 AP | Move within movement range |
| Basic Attack | 2 AP | Standard weapon attack |
| Special Ability | 3 AP | Powerful ability (future) |
| Use Item | 1 AP | Consume item (future) |
| End Turn | 0 AP | Skip remaining actions |

### Action Point Rules

**Maximum AP:** 3 per turn
- Cannot bank AP between turns
- Unused AP is lost
- Always start turn with full 3 AP

**Action Combinations:**
```
With 3 AP you can:
- Move + Attack (1 + 2 = 3 AP)
- Move + Move + Move (3 × 1 = 3 AP)
- Attack + End Turn (2 AP used, 1 lost)
- Special Ability (3 AP, future)

Cannot do:
- Attack + Attack (4 AP needed, only have 3)
- Move + Special (4 AP needed)
```

**Tactical Implications:**
- Move first to get in range, then attack
- Or attack first if already in range, move away
- Save movement to retreat after attacking
- Melee fighters need to move into range (1 tile)

---

## INITIATIVE SYSTEM

### Initiative Formula

```
Initiative = (Reflexes × 2) + random(1, 10)
```

**Example Calculations:**
```
Reflexes 1:  (1 × 2) + d10 =  3-12
Reflexes 5:  (5 × 2) + d10 = 11-20
Reflexes 10: (10 × 2) + d10 = 21-30
```

### Initiative Implications

**High Reflexes (8-10):**
- Usually acts first
- Can eliminate threats before they act
- Better positioning

**Medium Reflexes (4-7):**
- Mixed initiative
- Sometimes first, sometimes last
- Unpredictable

**Low Reflexes (1-3):**
- Usually acts last
- Enemies act first
- Defensive positioning crucial

### Random Element

- **d10 roll** adds variability
- Even low Reflexes can occasionally win initiative
- Even high Reflexes can sometimes go last
- Keeps combat dynamic

---

## HIT CHANCE SYSTEM

### Hit Chance Formula

```
Hit Chance = Weapon Accuracy - Target Dodge Chance

Modifiers:
- Half Cover: -25%
- Full Cover: -40%

Final: clamp(Hit Chance, 5%, 95%)
```

### Dodge Chance

```
Dodge Chance = min(20, Reflexes × 3)

Examples:
Reflexes 1: 3% dodge
Reflexes 5: 15% dodge
Reflexes 7+: 20% dodge (capped)
```

**Dodge Cap Reasoning:**
- Prevents excessive evasion
- Guarantees minimum 75% hit with accuracy 95
- Keeps combat decisive

### Hit Chance Examples

**Assault Rifle (85 accuracy) vs Enemy (Reflexes 4, 12% dodge):**
```
Base: 85 - 12 = 73% hit chance

With Half Cover: 73 - 25 = 48% hit chance
With Full Cover: 73 - 40 = 33% hit chance
```

**Pistol (90 accuracy) vs Agile Enemy (Reflexes 7, 20% dodge):**
```
Base: 90 - 20 = 70% hit chance

With Half Cover: 70 - 25 = 45% hit chance
With Full Cover: 70 - 40 = 30% hit chance
```

**Katana (95 accuracy, melee) vs Tank (Reflexes 3, 9% dodge):**
```
Base: 95 - 9 = 86% hit chance

With Half Cover: 86 - 25 = 61% hit chance
With Full Cover: 86 - 40 = 46% hit chance
```

### Hit Chance Clamping

**Minimum: 5%**
- Even worst-case scenario has chance to hit
- Prevents total futility
- Always worth trying

**Maximum: 95%**
- Even best-case isn't guaranteed
- Adds tension
- Misses still possible

### Cover System (Future Implementation)

**Half Cover:** -25% hit chance, 25% damage reduction
- Examples: Low wall, car door, crate

**Full Cover:** -40% hit chance, 40% damage reduction
- Examples: Concrete wall, vehicle, building corner

**Tech Weapons:** Ignore cover (smart rounds)

---

## DAMAGE SYSTEM

### Damage Calculation Steps

```
1. Base Damage = Weapon Damage × random(0.85, 1.15)

2. Stat Bonus =
   IF melee:    Body × 3
   IF ranged:   Reflexes × 2

3. Critical Hit =
   IF random(1,100) <= (Cool × 2):
      Crit Multiplier = Weapon Crit Multiplier
   ELSE:
      Crit Multiplier = 1.0

4. Morale Modifier = 1.0 + ((Morale - 50) / 200)

5. Pre-Armor Damage = (Base + Stat Bonus) × Crit × Morale

6. Armor Reduction =
   Effective Armor = Target Armor × (1 - Weapon Armor Pen)
   Reduction = Effective Armor × 1.0

7. Cover Reduction (if in cover and not tech weapon) =
   IF half cover:  × 0.75 (25% reduction)
   IF full cover:  × 0.60 (40% reduction)

8. Final Damage = max(1, int(Pre-Armor - Armor + Cover))
```

### Damage Examples

**Example 1: Assault Rifle Hit (No Crit)**
```
Attacker: Reflexes 6, Morale 100, Assault Rifle
Target: Armor 10, No Cover

Base: 30 × 1.0 (assume no variance) = 30
Stat Bonus: 6 × 2 = 12
Crit: 1.0 (no crit)
Morale: 1.25 (100 morale)
Pre-Armor: (30 + 12) × 1.0 × 1.25 = 52.5

Armor: 10 × (1 - 0.15) = 8.5 effective armor
Armor Reduction: 8.5 × 1.0 = 8.5

Final: 52.5 - 8.5 = 44 damage
```

**Example 2: Katana Critical Hit**
```
Attacker: Body 8, Cool 6, Morale 100, Katana
Target: Armor 20, No Cover

Base: 35 × 1.0 = 35
Stat Bonus: 8 × 3 = 24
Crit: 2.5 (critical hit!)
Morale: 1.25 (100 morale)
Pre-Armor: (35 + 24) × 2.5 × 1.25 = 184.4

Armor: 20 × (1 - 0.20) = 16 effective armor
Armor Reduction: 16 × 1.0 = 16

Final: 184.4 - 16 = 168 damage (MASSIVE!)
```

**Example 3: Low Morale Attack**
```
Attacker: Reflexes 5, Morale 0, Pistol
Target: Armor 10, Half Cover

Base: 25 × 1.0 = 25
Stat Bonus: 5 × 2 = 10
Crit: 1.0 (no crit)
Morale: 0.75 (0 morale, 25% penalty)
Pre-Armor: (25 + 10) × 1.0 × 0.75 = 26.25

Armor: 10 × (1 - 0.10) = 9 effective armor
Armor Reduction: 9 × 1.0 = 9

Cover: Half cover, × 0.75
Final: (26.25 - 9) × 0.75 = 12.9 → 12 damage
```

### Damage Variance

- **85-115%** of base weapon damage
- Adds unpredictability
- Prevents repetitive combat
- Creates memorable moments

### Minimum Damage

- **Always at least 1 damage**
- Even through max armor
- Guarantees progress
- Prevents invulnerability

---

## MORALE SYSTEM

### Morale Mechanics

**Morale Range:** 0-100
- Starts at 100 (maximum)
- Decreases from taking damage
- Increases from victories (future)
- Affects damage output

### Morale Loss

```
On Taking Damage:
IF damage >= 30% of max HP:  -20 Morale
ELIF damage >= 15% of max HP: -10 Morale
ELSE: No morale loss
```

**Examples:**
```
Character with 100 HP:
- Takes 30+ damage: -20 morale
- Takes 15-29 damage: -10 morale
- Takes < 15 damage: no morale loss

Character with 150 HP:
- Takes 45+ damage: -20 morale
- Takes 22-44 damage: -10 morale
- Takes < 22 damage: no morale loss
```

### Morale Effects

**Damage Modifier:**
```
Damage Multiplier = 1.0 + ((Morale - 50) / 200)

Morale 100: × 1.25 (+25% damage)
Morale 75:  × 1.125 (+12.5% damage)
Morale 50:  × 1.0 (neutral)
Morale 25:  × 0.875 (-12.5% damage)
Morale 0:   × 0.75 (-25% damage)
```

**Tactical Implications:**
- High morale = aggressive offense
- Low morale = reduced effectiveness
- Protect wounded allies (morale matters)
- Focus fire to break enemy morale

---

## MOVEMENT SYSTEM

### Movement Range

```
Movement Range = BASE_MOVEMENT_RANGE + (Reflexes ÷ 4)

BASE_MOVEMENT_RANGE = 4 tiles

Examples:
Reflexes 1: 4 + 0 = 4 tiles
Reflexes 4: 4 + 1 = 5 tiles
Reflexes 8: 4 + 2 = 6 tiles
Reflexes 10: 4 + 2 = 6 tiles (10÷4=2.5, rounded down)
```

### Movement Rules

**Distance Calculation:** Manhattan distance
```
Distance = |x2 - x1| + |y2 - y1|

Examples:
(5,5) to (6,6): |6-5| + |6-5| = 2
(5,5) to (8,5): |8-5| + |5-5| = 3
(5,5) to (9,9): |9-5| + |9-5| = 8
```

**Movement Restrictions:**
- Cannot move through occupied tiles
- Must stay within grid bounds (0-19, 0-14)
- Costs 1 AP per move action
- Distance must be ≤ movement range

**Multiple Moves:**
- Can move multiple times per turn (3 AP = 3 moves)
- Each move calculated from current position
- Total distance can exceed movement range
  ```
  Example with range 5:
  Move 1: (0,0) → (5,0) = 5 distance
  Move 2: (5,0) → (10,0) = 5 distance
  Total: Moved 10 tiles using 2 AP
  ```

---

## ESCAPE SYSTEM

### Escape Availability

**Conditions** (ALL must be true):
1. **Turn 3 or later**
2. **At least ONE of:**
   - Average party HP < 50%
   - One party member dead
   - Outnumbered 2:1 or more

### Escape Mechanics

**Solo Escape:**
```
Chance = 45% + (Leader Reflexes × 2)%
Clamped to 5-95%

Examples:
Reflexes 1:  45 + 2  = 47%
Reflexes 5:  45 + 10 = 55%
Reflexes 10: 45 + 20 = 65%

On Success:
- All living party members escape
- -20 Morale penalty (all living members)
- Combat ends, victor = 'fled'

On Failure:
- Leader takes 20% max HP damage
- Combat continues
```

**Sacrifice Escape:**
```
Chance = 93% (near-certain)

Chosen party member stays behind to cover retreat

On Success:
- Sacrifice dies (HP = 0, is_alive = False)
- All other living party members escape
- -20 Morale penalty (survivors)
- Combat ends, victor = 'fled'

On Failure:
- Sacrifice dies anyway
- Rest of party stays in combat
```

### Escape Tactics

**When to Escape:**
- Party severely wounded
- Key character downed
- Outnumbered and losing
- Objective failed, cut losses

**Solo vs Sacrifice:**
- Solo: Risky but preserves party
- Sacrifice: Nearly guaranteed, but lose character
- Choose sacrifice if:
  - Character already near death
  - Low-value character
  - Desperate situation

**Example Scenarios:**
```
Scenario 1: Low HP
Turn 3, Player HP: 30/150 (20%), Ally HP: 50/180 (28%)
Average HP: 24% < 50%
✓ Escape available

Scenario 2: Casualty
Turn 4, Ally is dead, Player HP: 100/150 (67%)
One party member dead
✓ Escape available

Scenario 3: Outnumbered
Turn 3, 1 player vs 2 enemies (2:1 ratio)
Outnumbered condition met
✓ Escape available

Scenario 4: Too Early
Turn 2, Party HP: 20%
✗ Not turn 3 yet, cannot escape
```

---

## WEAPON SYSTEM

### Weapon Categories

**Ranged Weapons:**
- Use Reflexes for damage bonus (Reflexes × 2)
- Medium to long range
- Examples: Assault Rifle, Pistol, Shotgun

**Melee Weapons:**
- Use Body for damage bonus (Body × 3)
- Range 1 (adjacent tiles only)
- Examples: Katana, Blade, Fists

**Tech Weapons (Future):**
- May use Intelligence
- Ignore cover
- Special effects (EMP, hack, etc.)

### Weapon Statistics

**Assault Rifle**
```
Damage: 30
Accuracy: 85%
Range: 12 tiles
Armor Pen: 15%
Crit Multiplier: 2.0x
Type: Ranged
```
**Use case:** Versatile, medium-long range
**Best for:** Balanced characters, Reflexes 6-8

**Pistol**
```
Damage: 25
Accuracy: 90%
Range: 10 tiles
Armor Pen: 10%
Crit Multiplier: 2.0x
Type: Ranged
```
**Use case:** Reliable sidearm, good accuracy
**Best for:** Backup weapon, high Cool builds (crits)

**Shotgun**
```
Damage: 45
Accuracy: 75%
Range: 6 tiles
Armor Pen: 5%
Crit Multiplier: 1.5x
Type: Ranged
```
**Use case:** Close-range devastation, high damage
**Best for:** Aggressive play, Body 6+ (HP to close distance)

**Katana**
```
Damage: 35
Accuracy: 95%
Range: 1 tile
Armor Pen: 20%
Crit Multiplier: 2.5x
Type: Melee
```
**Use case:** High-risk high-reward, devastating crits
**Best for:** Body 8+, Cool 6+ (damage + crits)

### Weapon Selection

**Choose based on:**
- **Primary stat:** Reflexes → Ranged, Body → Melee
- **Playstyle:** Aggressive → Shotgun/Katana, Cautious → Rifle/Pistol
- **Team comp:** Balance ranged and melee
- **Enemy type:** Armored → High armor pen, Mobile → Long range

---

## FUTURE SYSTEMS

### Quest System

**Structure:**
- Main story quests
- Side missions
- Faction quests
- Randomly generated contracts

**Mechanics:**
- Objective tracking
- Multiple solutions
- Consequences
- Rewards (XP, credits, items, reputation)

### Skill Progression

**XP Gain:**
- From combat (enemy level × 50 XP)
- From quests (variable)
- From exploration

**Level Up:**
- Gain skill points
- Increase attributes
- Unlock abilities
- Increase HP

### Cyberware System

**Cyberware Slots:**
- Neural (Intelligence, hacking)
- Optics (perception, targeting)
- Skeletal (Body, melee)
- Circulatory (HP, healing)
- Nervous (Reflexes, speed)

**Mechanics:**
- Installation requirements (Tech skill)
- Stat bonuses
- Special abilities
- Malfunction chance
- Upgrade paths

### Faction System

**Factions:**
- Corporations
- Gangs
- Fixers
- Law enforcement

**Reputation:**
- Actions affect standing
- Access to faction vendors
- Unique quests
- Price modifiers
- Hostile/friendly status

---

## APPENDIX: QUICK REFERENCE

### Formula Sheet

```
Initiative = (Reflexes × 2) + d10

Dodge = min(20, Reflexes × 3)

Crit Chance = Cool × 2%

Morale Modifier = 1.0 + ((Morale - 50) / 200)

Hit Chance = clamp(Accuracy - Dodge + Modifiers, 5, 95)

Movement Range = 4 + (Reflexes ÷ 4)

Damage = max(1, (Base × Variance + Stat Bonus) × Crit × Morale - Armor + Cover)
```

### Action Costs

| Action | AP Cost |
|--------|---------|
| Move | 1 |
| Attack | 2 |
| Special | 3 (future) |
| Item | 1 (future) |
| End Turn | 0 |

---

**END OF GAME MECHANICS BIBLE**

*This document defines the complete rules and mechanics of Neon Collapse. All gameplay must follow these systems. All tests must verify these formulas.*
