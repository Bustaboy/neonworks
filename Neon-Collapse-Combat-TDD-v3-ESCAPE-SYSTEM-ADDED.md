# NEON COLLAPSE - COMBAT TECHNICAL DESIGN DOCUMENT v3.0
## "Street Cred & Chrome" - Horizontal Progression System

**Project:** Neon Collapse  
**Document Type:** Technical Design Document (Combat Systems)  
**Version:** 3.0 - Dual Progression Overhaul  
**Last Updated:** November 11, 2025  
**Author:** Development Team

---

## ðŸŽ¯ EXECUTIVE SUMMARY

**Core Philosophy:** Combat progression through **gear, cyberware, and reputation** - not arbitrary level inflation. Power comes from what you install and who you know, not how many rats you killed.

**Key Systems:**
- **No Character Levels** - Traditional XP system replaced with Skill XP (learn by doing)
- **Faction Reputation** - Main progression track, unlocks gear/allies/endings
- **Skill XP** - 5 attributes level independently based on playstyle
- **Gear-Based Scaling** - Enemies get better weapons/chrome, not bigger HP pools
- **Cyberware Slots** - 8 body systems, meaningful trade-offs
- **Permadeath Integration** - Death matters, succession creates tactical resets

**Design Goals:**
1. **Constant Dopamine** - Faction level-ups (big hits) + Skill XP (small drip)
2. **Playstyle Driven** - HOW you play determines WHAT you unlock
3. **Meaningful Choices** - Can't max everything, build diversity through limitations
4. **Cyberpunk Authenticity** - Chrome and connections = power, not grinding

---

## ðŸ“‹ TABLE OF CONTENTS

1. [Core Combat Mechanics](#core-mechanics)
2. [Dual Progression System](#progression)
3. [Skill XP System](#skill-xp)
4. [Faction Reputation System](#faction-rep)
5. [Attribute Skill Trees](#skill-trees)
6. [Cyberware Body Slots](#cyberware)
7. [Enemy Scaling (Gear-Based)](#enemy-scaling)
8. [Party Combat & Encounter Design](#party-combat)
9. [Loot & Economy](#loot)
10. [Permadeath Integration](#permadeath)
11. [Balance Philosophy & Playtesting](#balance-philosophy)
12. [Critical Success Metrics](#success-metrics)
13. [Implementation Roadmap](#roadmap)

---

<a name="core-mechanics"></a>
## I. CORE COMBAT MECHANICS

### Action Point System (3 AP Economy)

Every combat turn, characters have **3 Action Points (AP)** to spend:

```
ACTIONS:
- Move: 1 AP (move full movement range - 4-6 tiles depending on stats)
- Basic Attack: 2 AP (shoot, melee strike)
- Special Ability: 3 AP (ultimate move, full-turn commitment)
- Quickhack: 2 AP (netrunner abilities)
- Use Item/Reload: 1 AP (stim, grenade, weapon swap)
- Retreat Attempt: 3 AP (flee combat, full turn)

EXAMPLE TURNS:
- Move (1 AP) + Basic Attack (2 AP) = Standard combat turn
- Special Ability (3 AP) = High-impact, all-in move
- Move (1 AP) + Use Stim (1 AP) + Basic Attack (2 AP) = Tactical flexibility
```

**Design Intent:** Simple enough for beginners, flexible enough for tactics. Clear "move + shoot" vs "big ability" decision every turn.

### Initiative & Turn Order

```javascript
Initiative = (Reflexes Ã— 2) + random(1, 10)

Example:
Player (Reflex 6): (6Ã—2) + [roll 7] = 19
Enemy (Reflex 5): (5Ã—2) + [roll 4] = 14
â†’ Player acts first
```

**Tie-Breaker:** If initiative tied, higher Reflexes goes first. If still tied, player goes first (advantage).

### Hit Chance Calculation

```javascript
// DODGE CAP: Max 20% to prevent excessive miss rates at high level
DodgeChance = Math.min(20, target.reflexes Ã— 3)

BaseAccuracy = weapon.accuracy - DodgeChance

Modifiers:
+ Cover: -25% (half cover) or -40% (full cover)
+ Flanking (attacking from side/rear): +15%
+ Blinded status: -60%
+ Stunned target: +20%

FinalHitChance = clamp(BaseAccuracy + modifiers, 5%, 95%)
// Minimum 5% miss chance, maximum 95% hit chance (no guarantees)
```

**Example:**
```
Assault Rifle (85% base accuracy) vs Enemy (Reflex 6 = 18% dodge)
= 67% base hit chance

If enemy in full cover: 67% - 40% = 27% hit chance
If you flank them: 67% + 15% = 82% hit chance
```

### Damage Calculation Formula

```javascript
// STEP 1: Base Damage (with variance)
baseDmg = weapon.damage Ã— random(0.85, 1.15)

// STEP 2: Stat Bonus
if (weapon.isMelee) {
    statBonus = attacker.body Ã— 3
} else {
    statBonus = attacker.reflexes Ã— 2
}

// STEP 3: Critical Hit Check
if (random(1, 100) <= attacker.cool Ã— 2) {
    critMultiplier = weapon.critMultiplier // Usually 2.0x
} else {
    critMultiplier = 1.0
}

// STEP 4: Armor Reduction
effectiveArmor = target.armor Ã— (1 - weapon.armorPenetration)
armorReduction = effectiveArmor Ã— 1.0 // Each armor point = 1.0 dmg reduction (FULL protection)

// STEP 5: Cover Protection (if applicable)
if (target.inCover && weapon.type != "Tech") {
    if (target.coverType == "Half") coverReduction = 0.25
    if (target.coverType == "Full") coverReduction = 0.40
} else {
    coverReduction = 0
}

// STEP 6: Morale Modifier
moraleModifier = 1.0 + ((attacker.morale - 50) / 200)
// 100 morale = 1.25x damage (confident)
//  50 morale = 1.0x damage (neutral)
//   0 morale = 0.75x damage (broken)

// STEP 7: Final Damage
totalDamage = (baseDmg + statBonus) Ã— critMultiplier Ã— moraleModifier
totalDamage = totalDamage - armorReduction
totalDamage = totalDamage Ã— (1 - coverReduction)
totalDamage = max(1, floor(totalDamage)) // Minimum 1 damage

target.hp -= totalDamage
```

**Example Calculation:**
```
V (Reflex 6, Cool 5, Morale 80) shoots Gang Grunt (60 HP, 15% armor) with AR (30 dmg, 85% acc)

Roll to hit: 72 (â‰¤ 67% chance) â†’ HIT!
Base damage: 30 Ã— 1.08 = 32
Stat bonus: 6 Ã— 2 = 12
Crit check: Roll 8 (â‰¤ 10%) â†’ CRIT! (2.0x)
Morale bonus: 1.0 + (30/200) = 1.15x

Before defenses: (32 + 12) Ã— 2.0 Ã— 1.15 = 101 damage
Armor reduction: 15% Ã— 1.0 = 15 damage blocked (FULL armor value now applies)
Final: 101 - 15 = 86 damage

Grunt: 60 â†’ DEAD (overkill by 26)
```

---

<a name="progression"></a>
## II. DUAL PROGRESSION SYSTEM

### The Philosophy

**NO CHARACTER LEVELS.** Instead, two parallel progression tracks:

1. **Faction Reputation** (Main Track)
   - Big milestone rewards
   - Unlocks gear, allies, story paths
   - 6-10 levels per faction
   - Takes hours to level up
   - **BIG ENDORPHIN HITS**

2. **Skill XP** (Secondary Track)
   - Constant small rewards
   - Learn by doing (use guns â†’ Reflex XP)
   - Unlocks passive bonuses and skill points
   - Levels up every 30-60 minutes
   - **CONSTANT DRIP FEED**

### Why This Works

**Traditional RPG:**
```
Kill rats â†’ Gain generic XP â†’ Hit Level 5 â†’ All stats increase â†’ Feel powerful
Problem: Abstract, disconnected from actions, generic power creep
```

**Neon Collapse:**
```
Complete Militech gig â†’ Gain Militech Rep â†’ Hit Militech Level 3 â†’ Unlock faction gear/contact
USE guns in combat â†’ Gain Reflex XP â†’ Reflex Level 6 â†’ Gain skill point â†’ Unlock "Bullet Weaving"
Problem: NONE. Organic, authentic, tied to playstyle
```

**Result:** You're always progressing in SOMETHING. Faction work? Rep climbs. Combat? Skills improve. **Never feels like downtime.**

---

<a name="skill-xp"></a>
## III. SKILL XP SYSTEM

### Five Independent Attributes

Each attribute has its own XP track, levels independently:

```javascript
const PlayerAttributes = {
    Body: {level: 3, currentXP: 0, xpToNext: 100},
    Reflexes: {level: 3, currentXP: 0, xpToNext: 100},
    Intelligence: {level: 3, currentXP: 0, xpToNext: 100},
    Tech: {level: 3, currentXP: 0, xpToNext: 100},
    Cool: {level: 3, currentXP: 0, xpToNext: 100}
};

// XP REQUIRED TO LEVEL (exponential scaling)
function xpRequired(currentLevel) {
    return Math.floor(100 * Math.pow(1.5, currentLevel - 3));
}

// Level 3â†’4: 100 XP
// Level 4â†’5: 150 XP
// Level 5â†’6: 225 XP (Tier 2 skills unlock)
// Level 6â†’7: 340 XP
// Level 7â†’8: 510 XP (Tier 3 skills unlock)
// Level 8â†’9: 765 XP
// Level 9â†’10: 1150 XP (Tier 4 skills unlock)
```

### How You Earn XP (Learn By Doing)

```javascript
const XPSources = {
    // BODY XP
    Body: {
        meleeDamageDealt: 1,      // 1 XP per 10 melee damage
        damageTaken: 0.5,          // 1 XP per 20 damage absorbed
        intimidateSuccess: 10,     // Scare enemies
        surviveLowHP: 15,          // End combat below 30% HP
        reviveAlly: 20             // Bring teammate back from 0 HP
    },
    
    // REFLEXES XP
    Reflexes: {
        rangedDamageDealt: 1,      // 1 XP per 10 gun damage
        successfulDodge: 5,        // Avoid an attack
        criticalHit: 8,            // Land a crit
        winInitiative: 3,          // Act first in combat
        multiKillTurn: 15          // Kill 2+ enemies in one turn
    },
    
    // INTELLIGENCE XP
    Intelligence: {
        successfulHack: 10,        // Per quickhack landed
        ramSpent: 1,               // 1 XP per 5 RAM used
        scanEnemy: 5,              // Use scan ability
        disableCyberware: 15,      // EMP or hack to disable chrome
        controlEnemy: 25,          // Take over enemy (ultimate move)
        solveHackingPuzzle: 20     // Out-of-combat hacking
    },
    
    // TECH XP
    Tech: {
        repairEquipment: 8,        // Fix jammed weapon
        deployTurret: 10,          // Set up turret
        craftItem: 5,              // Build something
        modWeapon: 15,             // Upgrade gear
        hackEnvironment: 12,       // Hack turret/camera/door
        disarmTrap: 10             // Defuse mine/explosive
    },
    
    // COOL XP
    Cool: {
        criticalKill: 10,          // Kill via crit
        killStreak: 5,             // Per consecutive kill (stacks)
        stealthKill: 15,           // Kill from hidden
        maintainHighMorale: 3,     // Per turn at 80+ morale
        intimidateDialogue: 10,    // Intimidate in conversations
        headshot: 12               // Precision kill
    }
};
```

### Example Combat XP Breakdown

```
TURN 1: V shoots Gang Grunt with AR (35 damage)
â†’ Reflexes: +3 XP (35 dmg Ã· 10)
â†’ Cool: +5 XP (kill streak +1)

TURN 2: V dodges enemy attack, then crits with pistol (50 damage, kill)
â†’ Reflexes: +5 XP (dodge) +5 XP (damage) +8 XP (crit) = 18 XP
â†’ Cool: +10 XP (crit kill) +10 XP (kill streak +2) = 20 XP

TURN 3: V hacks enemy, disables cyberware (costs 8 RAM)
â†’ Intelligence: +10 XP (hack) +15 XP (disable chrome) +1 XP (RAM) = 26 XP

TURN 4: V deploys turret, takes cover
â†’ Tech: +10 XP (turret)

END OF COMBAT: V at 25/90 HP (survived at low HP)
â†’ Body: +15 XP

TOTAL EARNED IN ONE FIGHT:
Body: 15 XP
Reflexes: 21 XP
Intelligence: 26 XP
Tech: 10 XP
Cool: 35 XP
```

**The Psychological Hook:** Every action earns XP in something. Constant progress bars moving. **Micro-dopamine hits throughout every fight.**

### Leveling Up Attributes

When attribute hits next level threshold:

```javascript
function levelUpAttribute(attr) {
    attr.level++;
    attr.currentXP -= attr.xpToNext;
    attr.xpToNext = calculateXPRequired(attr.level);
    
    // STAT BONUSES (small incremental gains)
    switch(attr.name) {
        case "Body":
            player.maxHP += 15; // +15 HP per level (better survivability vs late-game enemies)
            player.carryCapacity += 20;
            break;
        case "Reflexes":
            player.initiative += 2;
            player.dodgeChance += 2;
            player.movementRange += 0.5; // Every 2 levels = +1 tile
            break;
        case "Intelligence":
            player.maxRAM += 2;
            player.quickhackDamage += 5;
            break;
        case "Tech":
            player.craftingQuality += 5;
            player.repairEfficiency += 10;
            break;
        case "Cool":
            player.critChance += 2;
            player.moraleDecayRate -= 5; // Lose morale slower
            break;
    }
    
    // SKILL POINT EVERY 2 LEVELS
    if (attr.level % 2 == 0) {
        player.skillPoints++;
        showNotification("NEW SKILL POINT AVAILABLE!"); // BIG NOTIFICATION
    }
    
    // UNLOCK SKILL TIERS
    if (attr.level == 5) unlockTier(attr, 2); // Tier 2 skills
    if (attr.level == 7) unlockTier(attr, 3); // Tier 3 skills
    if (attr.level == 9) unlockTier(attr, 4); // Tier 4 skills (ultimate)
}
```

**Progression Math:**
```
To max ONE attribute (3â†’10):
Total XP needed: 3,240 XP
Skill points earned: 3 (at levels 4, 6, 8)
Time investment: ~6-8 hours of combat/hacking/crafting

To get 12 TOTAL skill points (minimum to beat game):
Need 24 attribute levels across all 5 stats
Average ~1300 XP per attribute
Achievable over 25-30 hour campaign

FEELS LIKE:
Hour 5: 2-3 skill points (early build forming)
Hour 10: 5-6 skill points (core build defined)
Hour 15: 8-9 skill points (specialized, powerful)
Hour 20: 10-11 skill points (multiple trees)
Hour 25: 12-13 skill points (ready for endgame)
Hour 30+: 14-15 skill points (completionist)
```

---

<a name="faction-rep"></a>
## IV. FACTION REPUTATION SYSTEM

### The Six Factions

```javascript
const Factions = {
    Militech: {
        rep: 0, // -100 to +100 scale
        level: 0, // 0-10 levels
        hostileThreshold: -30,
        alliedThreshold: 50,
        rivals: ["Syndicate", "Nomads"]
    },
    Syndicate: {
        rep: 0,
        level: 0,
        hostileThreshold: -40, // More forgiving
        alliedThreshold: 60,
        rivals: ["Militech", "VoodooBoys"]
    },
    TygerClaws: {
        rep: 0,
        level: 0,
        hostileThreshold: -25,
        alliedThreshold: 45,
        rivals: ["VoodooBoys", "Scavengers"]
    },
    VoodooBoys: {
        rep: 0,
        level: 0,
        hostileThreshold: -35,
        alliedThreshold: 55,
        rivals: ["TygerClaws", "Syndicate"]
    },
    Nomads: {
        rep: 0,
        level: 0,
        hostileThreshold: -20, // Hardest to piss off
        alliedThreshold: 50,
        rivals: ["Militech"]
    },
    Scavengers: {
        rep: 0,
        level: 0,
        hostileThreshold: -10, // Always hostile unless you work for them
        alliedThreshold: 40,
        rivals: ["Everyone except themselves"]
    }
};
```

### How Reputation Works

```javascript
function completeGigForFaction(faction, difficulty) {
    // REP GAIN
    let repGain = difficulty * 10;
    // Easy gig: +10 rep
    // Medium gig: +20 rep
    // Hard gig: +30 rep
    // Loyalty mission: +50 rep
    
    faction.rep += repGain;
    
    // LEVEL UP CHECK (every 50 rep = 1 level)
    let newLevel = Math.floor(faction.rep / 50);
    if (newLevel > faction.level) {
        faction.level = newLevel;
        unlockFactionRewards(faction);
        
        // BIG VISUAL NOTIFICATION
        showFactionLevelUp(faction); // Full-screen, dramatic
    }
}

function adjustRivalFactions(primaryFaction, repGain) {
    // FACTION CONFLICT
    let rivals = primaryFaction.rivals;
    rivals.forEach(rival => {
        rival.rep -= (repGain * 0.5); // Lose half as much with rivals
        
        // CHECK HOSTILITY THRESHOLD
        if (rival.rep < rival.hostileThreshold) {
            rival.status = "HOSTILE";
            notifyPlayer(`${rival.name} now attacks you on sight!`);
        }
    });
}
```

### Faction Level Rewards

```
LEVEL 1: Basic Access
- Safe house locations revealed
- Basic vendor unlocked (common gear)

LEVEL 2: Trusted Associate
- 10% vendor discount
- Uncommon gear available
- Faction contact introduced (can call for intel)

LEVEL 3: Valued Contractor
- 15% vendor discount
- Rare gear available
- Faction safe house upgraded (crafting station)

LEVEL 4: Reliable Ally
- Faction backup available (call for help in combat, once per day)
- Faction-specific cyberware unlocked (unique augments)

LEVEL 5: Inner Circle
- 20% vendor discount
- Epic gear available
- Faction missions unlocked (story-critical quests)

LEVEL 6: Elite Operative
- Faction lieutenants respect you
- Legendary weapons available (faction-specific)
- Can bring faction ally on missions

LEVEL 7: Right Hand
- 25% vendor discount
- Faction unique ability unlocked (special perk)
- Access to faction armory (all gear)

LEVEL 8: Commander
- Can call in faction strike team (combat support, once per day)
- Faction ending path unlocked (unique story route)

LEVEL 9: Legend
- 30% vendor discount
- Faction leader trusts you completely
- Unique legendary cyberware (faction signature augment)

LEVEL 10: Living Icon
- Free gear from faction vendors
- Faction will follow you into impossible situations
- Ultimate faction ability (game-changing power)
```

**Design Intent:** Faction levels are **major milestones**. Takes 10-15 gigs to hit max level with one faction. Completing endgame requires Level 6-8 with at least one faction. **You can't max everyone** - choose your allies.

---

<a name="skill-trees"></a>
## V. ATTRIBUTE SKILL TREES

### How Skills Work

- **Passive Bonuses** - Always active, not abilities you click
- **Tiered Unlocks** - Tier 1 (lvl 3+), Tier 2 (lvl 5+), Tier 3 (lvl 7+), Tier 4 (lvl 9+)
- **Skill Points** - Earned every 2 attribute levels, spend on ANY tree
- **Build Diversity** - 12-15 total points, can't get everything

**Key Difference from CP2077:** These are **tactical game-changers** and **survival tools**, not just "+X% damage" perks.

---

### BODY TREE - "STREET SURVIVOR"

*Theme: Physical resilience, protection, carrying the weight*

```
TIER 1 (Unlock at Body 3+):
â”œâ”€ Street Tough: +20 max HP
â”œâ”€ Pain Tolerance: Injury penalties reduced by 40%
â””â”€ Intimidating Presence: Enemies have -5% accuracy when you're at <50% HP

TIER 2 (Unlock at Body 5+):
â”œâ”€ Second Wind: Once per combat, auto-heal 25% HP when dropping below 25%
â”œâ”€ Heavy Hitter: Melee weapons deal +25% damage
â””â”€ Bruiser: Can move through enemies (don't block your path)

TIER 3 (Unlock at Body 7+):
â”œâ”€ Unbreakable: Cannot be stunned or knocked down
â”œâ”€ Berserker: At <30% HP, deal +40% damage for 3 turns (auto-trigger)
â””â”€ Meat Shield: Allies within 2 tiles take -15% damage (you're covering them)

TIER 4 (Unlock at Body 9+):
â”œâ”€ Death's Door: Can survive one killing blow per day at 1 HP instead
â””â”€ Titan: Carry capacity doubled, can use heavy weapons without penalty
```

**Philosophy:** Tank, protect allies, survive impossible odds. **Supports permadeath theme** (keeping crew alive matters).

---

### REFLEXES TREE - "CHROME RAZOR"

*Theme: Speed, precision, first strike advantage*

```
TIER 1 (Unlock at Reflexes 3+):
â”œâ”€ Quick Draw: Weapon swap costs 0 AP (was 1 AP)
â”œâ”€ Combat Reflexes: +5% dodge chance
â””â”€ Fleet Footed: +1 tile movement range

TIER 2 (Unlock at Reflexes 5+):
â”œâ”€ Bullet Weaving: After moving, gain +10% dodge until your next turn
â”œâ”€ Snap Shot: First attack each combat has +15% accuracy
â””â”€ Initiative Master: Always act first in combat (unless enemy has this too)

TIER 3 (Unlock at Reflexes 7+):
â”œâ”€ Blinding Speed: Can move after attacking (normally attack ends turn)
â”œâ”€ Reflex Overload: Cyberware cooldowns reduced by 1 turn
â””â”€ Evasive Maneuvers: Can dodge into cover for 1 AP (move + cover bonus combined)

TIER 4 (Unlock at Reflexes 9+):
â”œâ”€ Time Dilation Master: Sandevistan/Kerenzikov duration +1 turn
â””â”€ Untouchable: When at full HP, first enemy attack auto-dodges
```

**Philosophy:** Action economy, positioning, speed kills. **Rewards aggressive play.**

---

### INTELLIGENCE TREE - "GHOST PROTOCOL"

*Theme: Information warfare, system manipulation, netrunner mastery*

```
TIER 1 (Unlock at Intelligence 3+):
â”œâ”€ Efficient Hacking: Quickhacks cost -1 RAM
â”œâ”€ Data Miner: Successful hacks reveal enemy weaknesses
â””â”€ Memory Boost: +5 max RAM

TIER 2 (Unlock at Intelligence 5+):
â”œâ”€ Daemon Persistence: Quickhack durations +1 turn
â”œâ”€ System Shock: Hacked enemies take +20% damage from all sources (marked)
â””â”€ RAM Recovery: +2 RAM regeneration per turn (was +4 base)

TIER 3 (Unlock at Intelligence 7+):
â”œâ”€ Chain Reaction: Quickhacks spread to 1 adjacent enemy (50% effect)
â”œâ”€ Overheat Protocol: Burning status deals +50% damage
â””â”€ Memory Wipe: Failed hacks don't cost RAM (can retry for free)

TIER 4 (Unlock at Intelligence 9+):
â”œâ”€ Puppet Master: Can control hacked enemies for 1 turn (ultimate ability)
â””â”€ Neural Firewall: Cannot be hacked by enemy netrunners
```

**Philosophy:** Control battlefield, weaken enemies, ultimate utility. **Netrunner endgame.**

---

### TECH TREE - "GEAR HEAD"

*Theme: Equipment mastery, field repairs, technological advantage*

```
TIER 1 (Unlock at Tech 3+):
â”œâ”€ Field Medic: Healing items restore +25% more HP
â”œâ”€ Steady Hands: +10% accuracy with all weapons
â””â”€ Armor Plating: +10% armor effectiveness

TIER 2 (Unlock at Tech 5+):
â”œâ”€ Quick Fix: Can repair equipment mid-combat (1 AP, removes Jammed status)
â”œâ”€ Weapon Expert: All weapons have +1 tile range
â””â”€ Tech Scavenger: 30% chance to recover ammo/grenades from kills

TIER 3 (Unlock at Tech 7+):
â”œâ”€ Overcharge: Can spend 10 HP to reload all cyberware abilities instantly (once per combat)
â”œâ”€ Turret Master: Deployed turrets have double HP and duration
â””â”€ Armor Specialist: Armor also reduces status effect duration by 30%

TIER 4 (Unlock at Tech 9+):
â”œâ”€ Combat Engineer: Can hack environment (turrets, doors, cameras) during combat (2 AP)
â””â”€ Masterwork: All equipment bonuses increased by 25%
```

**Philosophy:** Mid-combat utility, equipment optimization, tactical support. **Makes gear better.**

---

### COOL TREE - "ICE COLD"

*Theme: Critical hits, composure under fire, morale warfare*

```
TIER 1 (Unlock at Cool 3+):
â”œâ”€ Steady Aim: +5% crit chance
â”œâ”€ Pressure Resistant: Morale never drops below 30 (prevents total breakdown)
â””â”€ Poker Face: Enemies have -10% accuracy when targeting you

TIER 2 (Unlock at Cool 5+):
â”œâ”€ Assassin: Attacks from stealth/cover deal +30% damage
â”œâ”€ Headhunter: Killing blow with crit refunds 1 AP
â””â”€ Cold Blooded: Killing an enemy grants +10% damage for 2 turns (stacks 3x)

TIER 3 (Unlock at Cool 7+):
â”œâ”€ Deadeye: +10% crit chance, crits deal 2.5x damage (was 2.0x)
â”œâ”€ Unshakeable: Allies within 3 tiles gain +10 morale (you inspire confidence)
â””â”€ Focus Fire: Consecutive shots on same target gain +5% accuracy each (resets if switch)

TIER 4 (Unlock at Cool 9+):
â”œâ”€ Stone Cold Killer: Crits apply Bleeding status automatically
â””â”€ Legendary Presence: Enemies you've killed can't be revived/resurrected
```

**Philosophy:** Critical damage, morale control, psychological warfare. **Ties to permadeath themes** (morale system, crew confidence).

---

<a name="cyberware"></a>
## VI. CYBERWARE BODY SLOT SYSTEM

### The Philosophy

**One body, limited slots.** Can't install Mantis Blades AND Gorilla Arms - you only got two arms, choom. **Meaningful trade-offs.**

### 8 Body Systems (8 Max Cyberware Pieces)

```javascript
const CyberwareSlots = {
    // 1. ARMS (Choose ONE)
    Arms: {
        maxInstalled: 1,
        options: [
            {
                name: "Mantis Blades",
                abilities: [
                    {name: "Slash", ap: 2, damage: 45, type: "melee"},
                    {name: "Lunge", ap: 3, damage: 60, range: 3, type: "melee gap-closer"},
                    {name: "Leap Attack", ap: 4, damage: 40, aoe: "cone", type: "melee AOE"}
                ],
                passive: "Cannot be disarmed, +10% melee crit chance"
            },
            {
                name: "Gorilla Arms",
                abilities: [
                    {name: "Power Punch", ap: 2, damage: 50, type: "melee"},
                    {name: "Grapple", ap: 3, effect: "Stun for 1 turn", type: "melee control"},
                    {name: "Shockwave", ap: 4, damage: 35, aoe: "3-tile radius", type: "melee AOE"}
                ],
                passive: "Melee attacks stagger enemies, +20 carry capacity"
            },
            {
                name: "Monowire",
                abilities: [
                    {name: "Whip Strike", ap: 2, damage: 40, range: 4, type: "ranged melee"},
                    {name: "Electric Stun", ap: 3, effect: "Stun for 2 turns", type: "control"},
                    {name: "Chain Pull", ap: 3, effect: "Pull enemy to you", type: "positioning"}
                ],
                passive: "Attacks ignore 50% armor, can't be disarmed"
            },
            {
                name: "Projectile Launcher",
                abilities: [
                    {name: "Frag Grenade", ap: 3, damage: 35, aoe: "3-tile radius", effect: "Bleeding"},
                    {name: "EMP Grenade", ap: 3, damage: 15, aoe: "3-tile radius", effect: "Disable cyberware 3 turns"},
                    {name: "Tranq Dart", ap: 2, damage: 10, effect: "Sleep for 2 turns", type: "non-lethal"}
                ],
                passive: "Always have grenades available, no ammo needed"
            }
        ]
    },
    
    // 2. LEGS (Choose ONE)
    Legs: {
        maxInstalled: 1,
        options: [
            {name: "Reinforced Tendons", effect: "Double jump ability (jump over cover, reach high ground)"},
            {name: "Powered Ankles", effect: "Charge jump (leap 4 tiles in straight line)"},
            {name: "Lynx Paws", effect: "Silent movement, no fall damage, +1 tile movement range"}
        ]
    },
    
    // 3. NERVOUS SYSTEM (Choose ONE)
    NervousSystem: {
        maxInstalled: 1,
        options: [
            {name: "Sandevistan", ability: "Time dilation: +3 AP for next 2 turns, 10 turn cooldown", effect: "God mode window"},
            {name: "Kerenzikov", ability: "Bullet time: Auto-dodge first attack each turn", effect: "Passive defense"},
            {name: "Reflex Tuner", effect: "+2 initiative permanently, +1 AP every turn", passive: "Always-on boost"}
        ]
    },
    
    // 4. FRONTAL CORTEX (Choose ONE)
    FrontalCortex: {
        maxInstalled: 1,
        options: [
            {name: "RAM Upgrade", effect: "+8 max RAM", for: "Netrunners"},
            {name: "Smart Link", effect: "Can use Smart weapons (auto-aim, multi-target)", for: "Gunfighters"},
            {name: "Combat AI Chip", effect: "Enemy weak points revealed (see optimal targets)", for: "Tacticians"}
        ]
    },
    
    // 5. OCULAR SYSTEM (Choose ONE)
    OcularSystem: {
        maxInstalled: 1,
        options: [
            {name: "Kiroshi Optics Mk.3", effect: "Scan enemies for full stats (HP, armor, abilities)"},
            {name: "Thermal Vision", effect: "See through smoke/darkness, detect hidden enemies"},
            {name: "Targeting System", effect: "+15% accuracy with all weapons, crit chance doubled"}
        ]
    },
    
    // 6. CIRCULATORY SYSTEM (Choose ONE)
    CirculatorySystem: {
        maxInstalled: 1,
        options: [
            {name: "Biomonitor", effect: "Auto-use stim when HP drops below 20% (once per combat)"},
            {name: "Adrenaline Booster", effect: "Heal 5 HP per kill (lifesteal)"},
            {name: "Metabolic Editor", effect: "Stims last 2x longer, +50% healing from all sources"}
        ]
    },
    
    // 7. SKELETAL SYSTEM (Choose ONE)
    SkeletalSystem: {
        maxInstalled: 1,
        options: [
            {name: "Subdermal Armor", effect: "+15% armor (stacks with armor gear)"},
            {name: "Titanium Bones", effect: "Cannot be staggered, knockback immune, +10 max HP"},
            {name: "Microrotors", effect: "+1 tile melee range, melee attacks 20% faster (AP cost -1, min 1)"}
        ]
    },
    
    // 8. INTEGUMENTARY SYSTEM (Skin) (Choose ONE)
    IntegumentarySystem: {
        maxInstalled: 1,
        options: [
            {name: "Optical Camo", ability: "Stealth: Invisible for 3 turns, 8 turn cooldown (breaks on attack)", effect: "Stealth opener"},
            {name: "Subdermal Grip", effect: "Cannot be disarmed, weapon swap is instant (0 AP)"},
            {name: "Pain Editor", effect: "Immune to injury penalties, cannot be stunned"}
        ]
    }
};
```

### Cyberware Progression

**EARLY GAME (Hour 0-10):**
- Can afford 1-2 basic cyberware pieces
- Example: Kiroshi Optics (scan) + Subdermal Armor (defense)
- Cost: 5,000-8,000 eddies each

**MID GAME (Hour 10-20):**
- 3-4 cyberware installed, building synergies
- Example: Mantis Blades + Kerenzikov + Biomonitor + Lynx Paws = Silent melee assassin
- Cost: 15,000-30,000 eddies each
- Requires: Faction Level 3+ to unlock advanced chrome

**LATE GAME (Hour 20-30):**
- 6-7 cyberware, optimized build
- Example: Sandevistan + Mantis Blades + Targeting System + Adrenaline Booster + Titanium Bones + Optical Camo = Time-dilated death machine
- Cost: 50,000-100,000 eddies each
- Requires: Faction Level 6-8 for legendary cyberware

### Cyberware & Permadeath

```javascript
function onCharacterDeath(deceased, successor) {
    // SUCCESSION RULES
    successor.cyberware = [];
    
    // KEEP 2 INSTALLED PIECES (narrative: salvaged from corpse)
    let inheritedChrome = deceased.cyberware.slice(0, 2);
    successor.cyberware = inheritedChrome;
    
    // KEEP FACTION ACCESS (you can re-buy the rest)
    successor.factionLevels = deceased.factionLevels;
    
    // RESET SOME STATS
    successor.hp = successor.maxHP * 0.6; // Start injured
    successor.morale = 40; // Start shaken (crew just died)
    
    // The feeling: Lost god-tier build, but not starting from zero
}
```

**Design Intent:** Permadeath hurts (lost that Sandevistan + Mantis Blade combo), but you can rebuild using faction access and eddies. **Tactical setback, not full reset.**

---

<a name="enemy-scaling"></a>
## VII. ENEMY SCALING (GEAR-BASED, NOT HP INFLATION)

### The Philosophy

**Traditional RPG Problem:**
```
Level 1 Goblin: 20 HP, 5 damage
Level 20 Goblin: 500 HP, 100 damage
WHY? Did he go to goblin gym? Nonsense.
```

**Neon Collapse Solution:**
```
Phase 1 Ganger: 60 HP, Cheap Pistol (20 dmg), no chrome
Phase 3 Ganger: 75 HP, Smart Pistol (42 dmg), tactical AI, cyberware
Threat scaled through EQUIPMENT, not arbitrary stat inflation
```

### Enemy Phases (Not Levels)

```javascript
// PHASE = Player's aggregate progress (hours played, faction levels, skills unlocked)
function calculateEnemyPhase(player) {
    let hoursPlayed = player.playtime / 60; // Convert minutes to hours
    let avgFactionLevel = averageFactionLevel(player);
    let totalSkills = player.skillsUnlocked;
    
    // Weighted average
    let phaseScore = (hoursPlayed * 0.4) + (avgFactionLevel * 3) + (totalSkills * 0.5);
    
    return Math.floor(phaseScore / 10); // Phase 0-4
}
```

### TIER 1 ENEMIES (Street Trash) - SLOW SCALING

```javascript
const GangGrunt = {
    baseHP: 60,
    
    Phase_0: { // Hours 0-10
        hp: 60,
        weapon: {name: "Cheap Pistol", damage: 20, accuracy: 70},
        armor: 10, // 10% reduction
        cyberware: [],
        tactics: ["BasicMove", "BasicShoot"],
        aiComplexity: "Dumb" // Walks forward, shoots
    },
    
    Phase_1: { // Hours 10-20
        hp: 65, // +5 HP (minimal gain)
        weapon: {name: "Upgraded Pistol", damage: 28, accuracy: 80},
        armor: 18,
        cyberware: ["Optical Enhancement"], // +5% accuracy
        tactics: ["BasicMove", "BasicShoot", "TakeCover"],
        aiComplexity: "Basic" // Uses cover occasionally
    },
    
    Phase_2: { // Hours 20-30
        hp: 70, // +10 HP total (16% increase from Phase 0)
        weapon: {name: "Modded SMG", damage: 35, accuracy: 85, burstFire: true},
        armor: 25,
        cyberware: ["Optical Enhancement Mk.II", "Subdermal Plating"],
        tactics: ["TacticalMove", "BurstFire", "SmartCover", "Grenade"],
        aiComplexity: "Tactical" // Flanks, uses cover intelligently
    },
    
    Phase_3: { // Hours 30-40
        hp: 75, // +15 HP total (25% increase from Phase 0)
        weapon: {name: "Smart Pistol", damage: 42, accuracy: 95, autoTarget: true},
        armor: 30,
        cyberware: [
            "Targeting System",
            "Kerenzikov Reflex Booster", // +1 AP first turn
            "Pain Editor", // Immune to injury penalties
            "Subdermal Armor Mk.II"
        ],
        tactics: ["AdvancedMovement", "SmartWeapons", "CoordinatedFire", "Stims", "CallBackup"],
        aiComplexity: "Advanced" // Coordinates with allies, uses abilities
    },
    
    Phase_4: { // Hours 40+ (endgame, rare)
        hp: 80, // +20 HP total (33% increase from Phase 0)
        weapon: {name: "Legendary Smart Pistol", damage: 50, accuracy: 98, multiTarget: true},
        armor: 35,
        cyberware: [
            "Full Combat Suite",
            "Sandevistan Prototype", // Can time-dilate
            "Titanium Skeleton",
            "Biomonitor"
        ],
        tactics: ["EliteTactics", "TimeDilation", "TeamCoordination", "Retreat"],
        aiComplexity: "Elite" // Nearly player-level intelligence
    }
};

// PROGRESSION FORMULA FOR TIER 1
function getTier1EnemyStats(baseEnemy, phase) {
    let stats = {...baseEnemy[`Phase_${phase}`]};
    
    // HP SCALING (slow, capped growth)
    let hpGrowth = Math.min(phase * 5, 20); // Max +20 HP
    stats.hp = baseEnemy.baseHP + hpGrowth;
    
    // DAMAGE SCALING (through weapon upgrades, not raw stats)
    // Handled by weapon.damage property above
    
    return stats;
}
```

**Player Power vs Tier 1 Scaling:**
```
Phase 0 (Hour 0):
Player: 90 HP, 28 dmg pistol, 0 cyberware
Grunt: 60 HP, 20 dmg pistol, 0 cyberware
â†’ Close fight, Grunt is threatening

Phase 2 (Hour 20):
Player: 165 HP, 42 dmg AR, 4 cyberware, skills
Grunt: 70 HP, 35 dmg SMG, 2 cyberware
â†’ Player stomps Grunt in 2 turns, power fantasy kicks in

Phase 4 (Hour 40):
Player: 215 HP, 62 dmg legendary weapon, 7 cyberware, 12+ skills
Grunt: 80 HP, 50 dmg smart pistol, 4 cyberware
â†’ Grunt still dangerous if careless, but manageable
```

**Design Intent:** Tier 1 enemies SHOULD become easier over time. That's **earned power fantasy**. But they never become TRIVIAL (smart pistol can still fuck you up if you stand in the open).

---

### TIER 2 ENEMIES (Organized Crime) - LINEAR SCALING

```javascript
const GangHeavy = {
    baseHP: 140,
    
    Phase_0: { // Hours 0-10 (SCARY early game)
        hp: 140,
        weapon: {name: "Pump Shotgun", damage: 45, accuracy: 90, range: 4},
        armor: 35,
        cyberware: ["Subdermal Armor", "Pain Editor"],
        tactics: ["AggressiveAdvance", "Shotgun", "Intimidate"],
        role: "Tank/Enforcer"
    },
    
    Phase_1: { // Hours 10-20
        hp: 160, // +20 HP (steady growth)
        weapon: {name: "Modded Shotgun", damage: 55, accuracy: 92, range: 5},
        armor: 40,
        cyberware: ["Subdermal Armor Mk.II", "Pain Editor", "Gorilla Arms"],
        tactics: ["TacticalAdvance", "Shotgun", "Grapple", "Suppress"],
        abilities: ["Grapple: Stun enemy for 1 turn (melee range)"]
    },
    
    Phase_2: { // Hours 20-30
        hp: 180, // +40 HP total (29% increase)
        weapon: {name: "Combat Shotgun", damage: 65, accuracy: 95, range: 6, autoLoad: true},
        armor: 45,
        cyberware: [
            "Armored Skeleton",
            "Pain Editor",
            "Gorilla Arms Mk.II",
            "Biomonitor"
        ],
        tactics: ["CoordinatedAssault", "Shotgun", "Shockwave", "CombatStim"],
        abilities: [
            "Shockwave: 3-tile radius, 35 damage, knockback",
            "Auto-Stim: When HP < 30%, heal 30 HP (once)"
        ]
    },
    
    Phase_3: { // Hours 30-40
        hp: 220, // +80 HP total (57% increase)
        weapon: {name: "Military Shotgun", damage: 65, accuracy: 98, range: 8, smartLink: true}, // Reduced from 75 - balanced threat
        armor: 50,
        cyberware: [
            "Full Combat Armor System",
            "Sandevistan",
            "Titanium Skeleton",
            "Biomonitor + Stim Injector"
        ],
        tactics: ["EliteAssault", "TimeDilation", "Devastate"],
        abilities: [
            "Time Dilation: +2 AP for 2 turns (once per combat)",
            "Devastate: Full-turn shotgun blast, 100 damage cone"
        ]
    }
};
```

**Player Power vs Tier 2 Scaling:**
```
Phase 0 (Hour 0):
Player vs Gang Heavy = YOU PROBABLY DIE
- Heavy: 140 HP, 45 dmg shotgun, 35% armor
- Two-shots you, takes 5-6 hits to kill
- Verdict: BOSS-TIER THREAT, avoid or flee

Phase 2 (Hour 20):
Player vs Gang Heavy = CHALLENGING BUT FAIR
- Heavy: 180 HP, 65 dmg shotgun, 45% armor
- Three-shots you, you kill him in 4-5 hits
- Verdict: Real threat, requires tactics

Phase 3 (Hour 30):
Player vs Gang Heavy = STANDARD COMBAT
- Heavy: 220 HP, 75 dmg shotgun, 50% armor, Sandevistan
- Can still three-shot you if careless
- Verdict: Respect the threat, winnable with skills
```

**Design Intent:** Tier 2 enemies scale LINEARLY with player. They're **never trivial**, always require tactics. This is your **standard combat challenge** throughout the game.

---

### TIER 3 ENEMIES (Elite/Corporate) - ACCELERATED SCALING

```javascript
const CorpoSecurityElite = {
    baseHP: 100,
    
    Phase_0: { // Hours 0-10 (BOSS-TIER early game)
        hp: 100,
        weapon: {name: "Military Assault Rifle", damage: 35, accuracy: 85, range: 12},
        armor: 30,
        cyberware: [
            "Optical Scanner",
            "Subdermal Armor",
            "Combat Stim Dispenser"
        ],
        tactics: ["TacticalFormation", "SuppressingFire", "Flanking"],
        aiComplexity: "Tactical" // Acts like trained soldier
    },
    
    Phase_1: { // Hours 10-20
        hp: 130, // +30 HP (faster growth than Tier 1/2)
        weapon: {name: "Smart Assault Rifle", damage: 48, accuracy: 90, range: 14, smartLink: true},
        armor: 40,
        cyberware: [
            "Full Targeting Suite",
            "Reflex Booster",
            "Pain Editor",
            "Armored Skeleton",
            "Biomonitor + Auto-Stim"
        ],
        tactics: ["CoordinatedAssault", "SmartWeapons", "AdvancedCover", "Grenades", "TacticalRetreat"],
        abilities: [
            "Frag Grenade: 3-tile radius, 35 damage + Bleeding",
            "Tactical Retreat: When <40% HP, fall back and call reinforcements"
        ]
    },
    
    Phase_2: { // Hours 20-30
        hp: 180, // +80 HP (80% increase from Phase 0)
        weapon: {name: "Advanced Combat Rifle", damage: 62, accuracy: 95, range: 16, multiTarget: true},
        armor: 50,
        cyberware: [
            "Full Combat Suite",
            "Sandevistan Prototype",
            "Reinforced Skeleton",
            "Active Camo",
            "Combat AI Chip",
            "Biometric Scanner"
        ],
        tactics: ["MilitaryDoctrine", "TimeDilation", "EliteCoordination", "HeavyOrdnance"],
        abilities: [
            "Sandevistan: +3 AP for 2 turns, 10 turn cooldown",
            "Active Camo: Start combat invisible, +50% damage first attack",
            "Biometric Lock: Reveals hidden enemies, +10% accuracy vs all targets",
            "Grenade Launcher: 4-tile radius, 50 damage, knockback"
        ]
    },
    
    Phase_3: { // Hours 30-40
        hp: 280, // +180 HP (180% increase from Phase 0) - LONGER fights, more tactical depth
        weapon: {name: "Legendary Combat System", damage: 65, accuracy: 98, range: 18, allFeatures: true}, // Reduced from 78 - no 2-shot kills
        armor: 60,
        cyberware: [
            "Experimental Military Suite",
            "Advanced Sandevistan",
            "Nano-Armor",
            "Neural Combat AI",
            "All systems optimized"
        ],
        tactics: ["PerfectExecution", "DominanceDoctrine", "NoMercy"],
        abilities: [
            "Advanced Time Dilation: +4 AP for 3 turns, 8 turn cooldown",
            "Nano-Repair: Regenerate 10 HP per turn passively",
            "Execute Protocol: If target <25% HP, guaranteed kill (2 AP)",
            "Command Network: All nearby allies gain +20% accuracy and damage"
        ]
    }
};
```

**Player Power vs Tier 3 Scaling:**
```
Phase 0 (Hour 0):
Player vs Corpo Elite = INSTANT DEATH
- Elite: 100 HP, 35 dmg AR, tactical AI, 30% armor
- Kills you in 3 turns, you need 4-5 turns to kill them
- Verdict: RUN AWAY OR DIE

Phase 1 (Hour 10):
Player vs Corpo Elite = EXTREMELY HARD
- Elite: 130 HP, 48 dmg smart rifle, advanced AI, 40% armor
- Kills you in 4 turns, you need 5-6 turns
- Verdict: Winnable with perfect tactics, high risk

Phase 2 (Hour 20):
Player vs Corpo Elite = CHALLENGING
- Elite: 180 HP, 62 dmg rifle, Sandevistan, 50% armor
- Kills you in 4-5 turns, you need 5-7 turns
- Can time-dilate and murder you if careless
- Verdict: Standard late-game threat, requires full toolkit

Phase 3 (Hour 30):
Player vs Corpo Elite = STILL DANGEROUS
- Elite: 250 HP, 78 dmg legendary gun, all abilities, 60% armor
- Kills you in 5-6 turns, you need 7-10 turns
- Has every trick you have, better AI
- Verdict: ALWAYS RESPECT, never trivial
```

**Design Intent:** Tier 3 enemies **outpace player growth**. Early game = impossible. Late game = still fucking scary. **These are the real threats** that keep permadeath meaningful.

---

### Enemy Phase Unlock Logic

```javascript
function spawnEnemy(baseEnemy, playerPhase) {
    // TIER 1: Spawns at player phase, but nerfed
    if (baseEnemy.tier == 1) {
        let enemyPhase = Math.max(0, playerPhase - 1); // Always 1 phase behind
        return constructEnemy(baseEnemy, enemyPhase);
    }
    
    // TIER 2: Spawns at player phase (matched)
    if (baseEnemy.tier == 2) {
        return constructEnemy(baseEnemy, playerPhase);
    }
    
    // TIER 3: Spawns 1 phase ahead (always challenging)
    if (baseEnemy.tier == 3) {
        let enemyPhase = Math.min(4, playerPhase + 1); // Can go beyond player
        return constructEnemy(baseEnemy, enemyPhase);
    }
}
```

**Result:**
- **Tier 1 = Power Fantasy** (Street gangs get easier, you're leveling past them)
- **Tier 2 = Standard Combat** (Organized crime keeps pace, always fair fights)
- **Tier 3 = Respect Threat** (Elites stay ahead, never trivial, permadeath matters)

---

<a name="party-combat"></a>
## VIII. PARTY COMBAT & ENCOUNTER DESIGN

### The Reality: Combat Isn't 1v1

All previous sections tuned for **duels** (1v1, 2v2). But real gigs? You're rolling with a crew, fighting squads. **Different math, different design.**

**Critical Insight:** Party combat isn't "scaled up duels" - it's about **action economy** (who gets more turns) and **focus fire** (deleting targets before they act).

**Design Philosophy:**
- Small crews (2-4 players max) for intimate stakes
- Enemies in meaningful numbers (2-12 depending on tier)
- Every death FELT because you know everyone's name
- Not "army commander" - you're a merc with chooms

### Party Size Constraints

```javascript
MAX_PARTY_SIZE = 4; // V + 3 crew members max
MIN_PARTY_SIZE = 1; // Solo missions exist (tutorial, specific story beats)

TYPICAL_COMPOSITIONS:
- Solo: V alone (1v1 to 1v3, intimate deadly encounters)
- Duo: V + 1 companion (2v2 to 2v4, buddy cop energy)  
- Crew: V + 2 members (3v3 to 3v6, tactical squad)
- Full Squad: V + 3 members (4v6 to 4v12, desperate last stands)
```

**Permadeath Stakes:**
- V dies â†’ Game Over (permadeath)
- Crew member dies â†’ Removed from roster, story consequences, funeral costs
- This makes crew death MEANINGFUL without being instant-loss frustrating

### Enemy Tier System (Party Combat Balanced)

The 1v1 tuned stats (200 HP, 48 dmg Corpo) work for duels. But in groups? You need **three distinct enemy tiers** designed for different tactical scenarios.

#### TIER 1 - SWARM (Cannon Fodder)

```javascript
const SwarmEnemy = {
    name: "Gang Grunt / Cheap Security / Street Trash",
    
    // CORE STATS
    hp: 80,
    damage: 20,
    accuracy: 70,
    armor: 10,
    reflexes: 5,
    cool: 3,
    
    // TACTICAL PROFILE
    cover_usage: 30%, // Usually rush, rarely take cover
    focus_fire: false, // Spread damage randomly
    
    // USE CASE
    typical_group_size: "2-5",
    difficulty_tiers: "EASY, MEDIUM",
    narrative_role: "Power fantasy, chaotic firefights, overwhelming numbers",
    
    // LOOT
    drops: {
        eddies: "50-200",
        gear: "Common weapons, cheap chrome, street drugs"
    }
};
```

**Who They Are:**
- Untrained street gangers (Maelstrom initiates, Valentino prospects)
- Minimum-wage private security (mall cops, warehouse guards)
- Desperate scavs (organ harvesters, junkies with guns)

**How They Fight:**
- Spray and pray, no tactics
- Die fast, dangerous in numbers
- Low accuracy, low armor, low threat individually
- 4-5 of them swarm you = real problem

**When To Use:**
- Early game power fantasy (player stomps 3-4 easily)
- Mid-game chaotic encounters (8-10 creates firefight chaos)
- "Mooks" that make player feel powerful


#### TIER 2 - STANDARD (Veteran Threat)

```javascript
const StandardEnemy = {
    name: "Gang Veteran / Corpo Security / Trained Merc",
    
    // CORE STATS (VALIDATED THROUGH 800+ SIMULATIONS)
    hp: 180,
    damage: 35,
    accuracy: 85,
    armor: 45,
    reflexes: 6,
    cool: 6,
    
    // TACTICAL PROFILE
    cover_usage: 60%, // Usually in cover
    focus_fire: true, // Coordinate on wounded targets
    flank_attempt: 40%, // Will try to flank if outnumbering
    
    // USE CASE
    typical_group_size: "4-6",
    difficulty_tiers: "HARD, EXTREME",
    narrative_role: "Serious threat, tactical engagements, where the body count starts",
    
    // LOOT
    drops: {
        eddies: "500-2000",
        gear: "Uncommon/Rare weapons, quality chrome, combat stims"
    }
};
```

**Who They Are:**
- Seasoned gang enforcers (Wraiths veterans, Animals elites)
- Corporate security teams (Arasaka standard, Militech sec)
- Professional mercenaries (hired guns, former military)

**How They Fight:**
- Use cover, coordinate focus fire
- Will flank if they outnumber you
- Smart target selection (finish wounded, avoid armored)
- 6 of them = your crew bleeds

**When To Use:**
- Mid-late game standard combat
- HARD tier encounters (expect 1-2 crew deaths)
- EXTREME tier encounters (expect 2-3 crew deaths, possible TPK)
- The "default enemy" for serious fights

**CRITICAL:** These are your workhorse enemies. Most combat in Acts 2-3 uses Standard tier.


#### TIER 3 - ELITE (Boss Material)

```javascript
const EliteEnemy = {
    name: "MaxTac Operator / Arasaka Spec-Ops / Legendary Solo",
    
    // CORE STATS (1v1 TUNED, KEPT FROM DUEL BALANCE)
    hp: 280,
    damage: 48,
    accuracy: 98,
    armor: 60,
    reflexes: 8,
    cool: 8,
    
    // TACTICAL PROFILE
    cover_usage: 80%, // Almost always in optimal position
    focus_fire: true,
    advanced_abilities: true, // Sandevistan, grenades, quickhacks
    
    // USE CASE
    typical_group_size: "1-3 MAX",
    difficulty_tiers: "BOSS ENCOUNTERS, STORY CLIMAXES",
    narrative_role: "Mini-bosses, rival solos, named antagonists",
    
    // SPECIAL ABILITIES
    abilities: [
        "Sandevistan: +3 AP for 2 turns",
        "Smart Weapons: Ignore cover penalties", 
        "Combat Stim: Auto-heal when HP < 30%",
        "Kerenzikov: Auto-dodge first attack each turn"
    ],
    
    // LOOT
    drops: {
        eddies: "5000-20000",
        gear: "Legendary weapons, epic chrome, rare quickhacks",
        guaranteed: "Named unique item (signature weapon/chrome)"
    }
};
```

**Who They Are:**
- MaxTac operators (NCPD's "kill on sight" squad)
- Arasaka special forces (cyber-ninjas, black ops)
- Legendary solos (Adam Smasher equivalents, Morgan Blackhand types)
- Named story antagonists (rival mercs, corpo assassins)

**How They Fight:**
- Every shot lands (98% accuracy)
- High armor, high HP, abilities that change combat
- Will use Sandevistan to get 6 AP turns (2 attacks + repositioning)
- 1 Elite = serious threat, 2 Elites = near-death experience, 3 Elites = suicide

**When To Use:**
- Boss fights ONLY (1v1 or 2v2 with elites)
- Climactic story duels (V vs named antagonist)
- "Remember that guy's name" encounters
- NEVER in groups of 4+, action economy breaks

**Design Warning:** Elite enemies in groups of 4+ create 100% TPK rate regardless of player skill. Use Standard enemies for large groups, Elites for quality-over-quantity boss fights.

### Encounter Difficulty Targets (Validated)

These survival rates were validated through **800+ simulated battles**. They are not theoretical - they are **proven to hit exact emotional beats**.

#### EASY - Power Fantasy

```javascript
const EasyEncounter = {
    player_party_size: 3,
    enemy_count: 2,
    enemy_tier: "Swarm",
    
    // VALIDATED OUTCOMES (200 simulations)
    all_survive_rate: "100%",
    avg_combat_duration: "2.4 turns",
    tpk_rate: "0%",
    
    // EMOTIONAL BEAT
    player_feeling: "We're professionals, this is Tuesday",
    death_only_if: "Player AFKs or intentionally throws",
    
    // WHEN TO USE
    use_cases: [
        "Tutorial encounters",
        "Early game confidence builders",
        "Trash mob cleanup between major fights",
        "Player needs to feel powerful after tough loss"
    ]
};
```

**Example Scenario:**
> **"Warehouse Cleanup"** - V + 2 crew vs 2 scav junkies  
> Expected: Full crew survives, 2-3 turn fight, minimal damage taken  
> Narrative: *"Easy eddies. In and out, no sweat."*


#### MEDIUM - Earned Victory

```javascript
const MediumEncounter = {
    player_party_size: 3,
    enemy_count: 3,
    enemy_tier: "Swarm",
    
    // VALIDATED OUTCOMES (200 simulations)
    all_survive_rate: "100%",
    avg_combat_duration: "3.2 turns",
    tpk_rate: "0%",
    
    // EMOTIONAL BEAT
    player_feeling: "Close call, but we knew what we were doing",
    death_only_if: "Serious tactical mistakes",
    
    // WHEN TO USE
    use_cases: [
        "Standard early-mid game encounters",
        "Side gigs and minor contracts",
        "Build confidence before ramping difficulty",
        "Player should feel competent, not invincible"
    ]
};
```

**Example Scenario:**
> **"Gang Ambush"** - V + 2 crew vs 3 Valentino prospects  
> Expected: Full crew survives 100%, 3-4 turn tactical fight  
> Narrative: *"They tried. We're just better."*


#### HARD - The Cost of Victory

```javascript
const HardEncounter = {
    player_party_size: 4,
    enemy_count: 6,
    enemy_tier: "Standard",
    
    // VALIDATED OUTCOMES (200 simulations)
    two_plus_survive_rate: "79.5%", // TARGET: 75%+
    all_survive_rate: "20%", // Rare full survival
    avg_survivors: 2.4,
    avg_combat_duration: "10.3 turns",
    tpk_rate: "5%",
    
    // EMOTIONAL BEAT
    player_feeling: "We won, but fuck... we paid for it",
    expected_casualties: "1-2 deaths likely",
    death_feels: "Earned through bad tactics or bad luck, not arbitrary",
    
    // WHEN TO USE
    use_cases: [
        "Major story missions",
        "High-stakes contracts",
        "\"This is going to be bloody\" moments",
        "Player warned this is HARD difficulty"
    ]
};
```

**Example Scenario:**
> **"Corpo Facility Assault"** - V + 3 crew vs 6 Arasaka security  
> Expected: 2-3 survivors, 10+ turn firefight, heavy casualties  
> Narrative: *"We got the data. Jackie didn't make it. Rebecca's hurt bad. But we got the fucking data."*

**Critical Design Note:** HARD encounters should be **telegraphed**. Player knows going in this will cost lives. Give them chance to prep, bring stims, hire extra muscle. When 2 die, it's not a surprise - it's the price of the job.


#### EXTREME - One Tells The Tale

```javascript
const ExtremeEncounter = {
    player_party_size: 4,
    enemy_count: 6, // Same as HARD - context changes emotional weight
    enemy_tier: "Standard",
    
    // VALIDATED OUTCOMES (200 simulations)
    one_plus_survive_rate: "83.0%", // TARGET: 75%+
    two_plus_survive_rate: "54%",
    avg_survivors: 2.2,
    avg_combat_duration: "10.8 turns",
    tpk_rate: "17%", // Real permadeath risk
    
    // EMOTIONAL BEAT
    player_feeling: "I'm the only one who walked out. I carry their eddies, their chrome, their unfinished gigs.",
    expected_casualties: "2-3 deaths, sometimes 4 (TPK)",
    death_feels: "Heroic last stand, against-all-odds survival",
    
    // WHEN TO USE
    use_cases: [
        "Act climax missions",
        "Suicide runs (explicitly framed as such)",
        "Final assault on Arasaka Tower equivalent",
        "Player EXPECTS to die, survival feels miraculous"
    ],
    
    // DESIGN WARNING
    warning: "17% TPK rate means 1 in 6 players lose their entire crew (PERMADEATH). Only use for story-critical 'this is the end' moments."
};
```

**Example Scenario:**
> **"Arasaka Tower Assault - Final Mission"** - V + 3 crew vs 6 Arasaka elites  
> Expected: 1-2 survivors (maybe), 17% everyone dies  
> Narrative: *"Everyone died. Rebecca. Lucy. David. I'm the only one left. I did what we came to do. But the cost... fuck."*

**Critical Distinction:** EXTREME uses **same enemy config as HARD** (4v6 Standard). What changes?

1. **Framing** - "This is suicide" vs "This will be hard"
2. **Context** - Act finale vs mid-game mission  
3. **Stakes** - Permadeath likely vs casualties expected
4. **Player Mindset** - Going in expecting TPK makes 1-2 survivors feel like victory

Same math, different emotional payload. That's narrative design, choom.

### Tactical Modifiers (Party Combat)

These modifiers become CRITICAL in party fights where small advantages compound across multiple combatants.

#### Cover System

```javascript
function applyCoverPenalty(baseAccuracy, target) {
    if (target.cover == "HALF") {
        return baseAccuracy - 25; // -25% accuracy
    }
    if (target.cover == "FULL") {
        return baseAccuracy - 40; // -40% accuracy
    }
    return baseAccuracy; // No cover
}

// COVER ASSIGNMENT (Per Turn)
player_cover_chance = 60%; // Players use cover more often
enemy_cover_chance = 50%; // Enemies less disciplined

// COVER TYPES
half_cover = {
    examples: "Low walls, car doors, crates",
    accuracy_penalty: -25,
    provides_flanking_opportunity: true
};

full_cover = {
    examples: "Concrete pillars, armored vehicles, reinforced walls",
    accuracy_penalty: -40,
    harder_to_flank: true
};
```

**Design Impact:**
- Without cover: 6 enemies focus fire â†’ 1 player dead per turn
- With cover: 6 enemies focus fire â†’ 2-3 turns to kill 1 player
- Cover extends fights from 3-4 turns to 10-12 turns = **time for tactics**


#### Flanking Mechanics

```javascript
function calculateFlanking(playerTeam, enemyTeam) {
    let playersAlive = playerTeam.filter(p => p.isAlive()).length;
    let enemiesAlive = enemyTeam.filter(e => e.isAlive()).length;
    
    // Outnumbering team flanks the outnumbered
    if (playersAlive > enemiesAlive) {
        let numFlanked = playersAlive - enemiesAlive;
        // First N enemies become flanked
        markAsFlanked(enemyTeam, numFlanked);
    } else if (enemiesAlive > playersAlive) {
        let numFlanked = enemiesAlive - playersAlive;
        // First N players become flanked
        markAsFlanked(playerTeam, numFlanked);
    }
}

flanking_bonuses = {
    accuracy: +15, // Easier to hit
    crit_chance: +10, // More likely to crit
    ignores_cover: true, // Flanking negates cover bonuses
};
```

**Tactical Significance:**
- 4v6 fight: 2 players are flanked (vulnerable)
- Kill 2 enemies quickly â†’ Now 4v4 (nobody flanked)
- Kill 3 enemies â†’ Now 4v3 (you flank them)
- **Momentum matters** - first kills create flanking advantage


#### Focus Fire & Action Economy

This is why party combat needs different balance than 1v1:

```javascript
// 1v1 COMBAT
turn_1: player_deals_65, enemy_deals_48
turn_2: player_deals_65, enemy_deals_48
turn_3: player_deals_65, enemy_dead
result: Player survives (106 HP), 3 turns

// 4v4 COMBAT (Focus Fire)
turn_1: 
    players_focus_enemy_1: 4 Ã— 65 = 260 damage â†’ ENEMY 1 DEAD
    enemies_focus_player_1: 4 Ã— 48 = 192 damage â†’ PLAYER 1 DEAD
    
turn_2:
    3 players vs 3 enemies (repeat)
    
result: Constant trading, last team standing wins
```

**Design Implication:**
- **HP must survive focus fire** - That's why Standard enemies have 180 HP (need 3 hits to kill, not 1)
- **Numbers matter more than stats** - 4v6 is brutal even if you're individually stronger
- **First kills create cascading advantage** - 4v4 â†’ 4v3 â†’ 4v2 = exponential swing

### Encounter Design Examples

#### Example 1: Tutorial Mission

```javascript
mission = {
    name: "First Blood",
    difficulty: "EASY",
    setup: "V + Jackie (2 players) vs 2 Scav junkies (Swarm tier)",
    
    expected_outcome: {
        survival: "100% both survive",
        duration: "2 turns",
        player_learns: "Basic mechanics, always wins"
    },
    
    narrative_context: "First real fight. Jackie talks you through it. Easy win builds confidence."
};
```

#### Example 2: Mid-Game Standard Mission

```javascript
mission = {
    name: "Convoy Ambush",
    difficulty: "MEDIUM",
    setup: "V + 2 crew (3 players) vs 4 gang enforcers (Swarm tier)",
    
    expected_outcome: {
        survival: "95%+ all survive",
        duration: "4-5 turns",
        player_learns: "Tactics matter, but you're competent"
    },
    
    narrative_context: "Standard gig. Steal the cargo, flatline guards, get paid. Professional work."
};
```

#### Example 3: High-Stakes Assault

```javascript
mission = {
    name: "Break Lucy Out",
    difficulty: "HARD",
    setup: "V + 3 crew (4 players) vs 6 Arasaka security (Standard tier)",
    
    expected_outcome: {
        survival: "80% chance 2+ survive",
        casualties: "1-2 crew deaths expected",
        duration: "10-12 turns",
        player_learns: "Victory has a price"
    },
    
    narrative_context: "Prison break. Heavy security. You KNOW going in people will die. The question is: who, and was it worth it?"
};
```

#### Example 4: Act Finale

```javascript
mission = {
    name: "Assault on Arasaka Tower",
    difficulty: "EXTREME",
    setup: "V + 3 crew (4 players) vs 6 Arasaka elites (Standard tier)",
    
    expected_outcome: {
        survival: "83% chance 1+ survives",
        tpk_rate: "17% everyone dies",
        avg_survivors: "2.2 (often just 1)",
        duration: "10-15 turns",
        player_learns: "This is the cost of taking on corps"
    },
    
    narrative_context: "Suicide run. You know it. They know it. One of you might tell the tale. Or maybe nobody does. That's the job.",
    
    post_combat: {
        if_tpk: "PERMADEATH - Game Over, load last save or start new playthrough",
        if_1_survives: "Sole survivor inherits all crew's eddies, chrome, unfinished gigs. Carries the weight.",
        if_2_plus_survive: "Bittersweet victory. You won, but empty chairs at the table."
    }
};
```

### Party Combat Implementation Checklist

```javascript
// CORE SYSTEMS NEEDED
â˜ Party management UI (up to 4 members)
â˜ Initiative system (Reflex-based, handles 2-12 combatants)
â˜ Cover detection (half/full cover per tile)
â˜ Flanking calculation (auto-applied based on numbers)
â˜ Focus fire AI (enemies coordinate on wounded targets)
â˜ Crew permadeath (death = removed from roster, story consequences)

// ENEMY SPAWNING
â˜ Encounter templates (EASY/MEDIUM/HARD/EXTREME with exact counts)
â˜ Enemy tier system (Swarm/Standard/Elite with stat blocks)
â˜ Phase-based scaling (Tier 1-3 enemies upgrade gear over time)

// BALANCE TESTING
â˜ Playtest HARD encounters (verify ~80% get 2+ survivors)
â˜ Playtest EXTREME encounters (verify ~83% get 1+ survivor, 17% TPK)
â˜ Verify combat duration (HARD/EXTREME should last 10+ turns)
â˜ Confirm TPK feels earned, not arbitrary

// NARRATIVE INTEGRATION  
â˜ Difficulty warnings ("This is suicide" for EXTREME)
â˜ Funeral mechanics (dead crew = story consequences, costs)
â˜ Sole survivor mechanics (inherits crew's stuff, dialogue changes)
â˜ TPK permadeath (Game Over screen, "Remember Us" memorial)
```

### Design Warnings & Common Pitfalls

**DON'T:**
- âŒ Use Elite enemies in groups of 4+ (100% TPK, no counterplay)
- âŒ Mix difficulty tiers randomly (confuses survival expectations)
- âŒ Let player control 5+ party members (action economy breaks, combat drags)
- âŒ Spawn 12 Elite enemies (mathematically impossible, player rage-quits)

**DO:**
- âœ… Telegraph difficulty (HARD/EXTREME should be explicitly labeled)
- âœ… Use Swarm enemies for quantity, Elite for quality
- âœ… Make cover visually obvious (player needs to know it's there)
- âœ… Test survival rates (if 95% of playtests TPK, it's broken)
- âœ… Respect permadeath (TPK = real consequence, not throwaway moment)

### Escape System - "Last Resort Protocol"

When combat goes sideways, players need an emergency exit. But this isn't some easy bailout - it's a **desperate gamble with brutal costs**. The escape system integrates sacrifice mechanics, succession triggers, and harsh consequences to create authentic Edgerunners-style "someone stays so others can run" moments.

#### Core Philosophy

- **Press in case of emergency**, not tactical rotation
- **Sacrifice = core DNA** (someone stays behind, Edgerunners-style)
- **Real permadeath stakes** (non-refundable commitments)
- **Transparent percentages** (show exact chances, weight matters)
- **V can sacrifice themselves** (triggers succession system)
- **Never hard-lock fights** (always can attempt escape, but consequences brutal)

---

#### Escape Availability Triggers

Escape becomes available on **Turn 3+** when ANY of these conditions are met:

```javascript
function canAttemptEscape(turn, party, enemies) {
    // MUST be turn 3+ (no instant bail)
    if (turn < 3) return false;
    
    // CHECK DESPERATE SITUATIONS
    
    // 1. Anyone critically wounded (< 30% HP)
    const anyoneCritical = party.some(member => 
        (member.currentHP / member.maxHP) < 0.30
    );
    
    // 2. Party average HP below 50% (whole crew bleeding)
    const avgPartyHP = party.reduce((sum, m) => 
        sum + (m.currentHP / m.maxHP), 0
    ) / party.length;
    const crewBloodied = avgPartyHP < 0.50;
    
    // 3. Already lost someone (companion down)
    const companionDown = party.filter(m => m.isAlive).length < party.startingSize;
    
    // 4. Elite threat detected (visual scan warning)
    const eliteDetected = enemies.some(e => e.tier === "Elite");
    
    // 5. Tier-weighted outnumbering (2:1 or worse)
    const effectiveEnemyCount = enemies.reduce((count, enemy) => {
        if (enemy.tier === "Swarm") return count + 0.5;  // Half weight
        if (enemy.tier === "Standard") return count + 1.0;
        if (enemy.tier === "Elite") return count + 2.0;   // Double weight
        return count;
    }, 0);
    
    const aliveParty = party.filter(m => m.isAlive).length;
    const heavilyOutnumbered = effectiveEnemyCount >= (aliveParty * 2);
    
    // Escape available if ANY condition true
    return anyoneCritical || crewBloodied || companionDown || 
           eliteDetected || heavilyOutnumbered;
}
```

**Visual/Audio Cues for Elite Detection:**

```
When Elite enemy detected (turn 3+):

⚠️ DANGER: ELITE CYBERWARE DETECTED
═══════════════════════════════════════
MANTIS BLADES MK.3 | SANDEVISTAN REFLEX
SUBDERMAL ARMOR MK.4 | SECOND HEART

THREAT LEVEL: [████████░░] EXTREME
RECOMMEND: TACTICAL RETREAT

• Boss music kicks in (aggressive, Refused-style)
• Screen edges pulse red (2 seconds)
• Red skull icon + "ELITE" tag above enemy
• Escape button becomes available (glowing red)
```

Players don't need to guess - the game **screams** "this is bad, here's your out."

---

#### Escape Chance Calculation

```javascript
function calculateEscapeChance(character, sacrifice = false) {
    // BASE ESCAPE CHANCE
    let escapeChance = 45;  // Starting point - coin flip territory
    
    // REFLEX BONUS (capped)
    const reflexBonus = Math.min(15, character.reflexes * 1.5);
    escapeChance += reflexBonus;
    
    // Most players: Reflex 3-4 early = 50-51% solo
    //               Reflex 6 mid = 54% solo
    //               Reflex 10 late = 60% solo
    
    // SACRIFICE BONUS (the big one)
    if (sacrifice) {
        escapeChance += 40;  // +40% when someone stays behind
    }
    // With sacrifice: 90-95% success (near-certain, but brutal cost)
    
    // CLAMP TO REALITY (no guarantees, no impossibilities)
    return Math.max(5, Math.min(95, escapeChance));
}

// EXAMPLE CALCULATIONS:
// V (Reflex 6) solo escape: 45 + 9 = 54% (risky gamble)
// V (Reflex 6) with sacrifice: 54 + 40 = 94% (near-certain, companion dies)
// V (Reflex 3) early game solo: 45 + 5 = 50% (pure coin flip)
// V (Reflex 3) with sacrifice: 50 + 40 = 90% (reliable, but loses companion)
```

**Design Intent:**
- **Solo escape (50-60%):** Uncomfortable gamble, not reliable enough to spam
- **Sacrifice escape (90-95%):** The real panic button, but horrific cost
- **No cooldown:** Failed attempts waste turns and bleed HP naturally

---

#### Sacrifice Volunteer System

Not all companions will volunteer to die for you - loyalty matters:

```javascript
function checkVolunteers(party) {
    const volunteers = [];
    
    // V is ALWAYS an option (player can sacrifice self)
    volunteers.push({
        character: "V",
        type: "PLAYER_CHARACTER",
        dialogue: "Get out of here. I'll make sure you make it.",
        consequence: "TRIGGERS_SUCCESSION"
    });
    
    for (let companion of party) {
        // HIGH LOYALTY (80+): Always volunteers
        if (companion.loyalty >= 80) {
            volunteers.push({
                character: companion,
                type: "HIGH_LOYALTY",
                dialogue: companion.highLoyaltyOffer, 
                // "Hermano, get them out. I'll hold the line."
            });
        }
        
        // MEDIUM LOYALTY (50-79): Only if already wounded
        else if (companion.loyalty >= 50 && 
                 companion.currentHP < companion.maxHP * 0.5) {
            volunteers.push({
                character: companion,
                type: "MEDIUM_LOYALTY_WOUNDED",
                dialogue: companion.medLoyaltyOffer,
                // "I'm hurt anyway, boss. Get them out."
            });
        }
        
        // LOW LOYALTY (<50): Never volunteers
        // They're not willing to die for you yet
    }
    
    return volunteers;
}
```

**Progression Loop This Creates:**
- **Early game:** Low loyalty = no volunteers = forced to risk solo escape (50%)
- **Mid game:** Medium loyalty wounded = situational sacrifice options
- **Late game:** High loyalty = multiple volunteers = hard choice (who do you accept?)

**Design Intent:** Build loyalty = better escape options. Organic progression tied to relationships.

---

#### Escape UI Flow & Player Choice

When escape becomes available:

```javascript
// ESCAPE ATTEMPT SCREEN

COMBAT SITUATION: CRITICAL
Party HP: 47% average | 1 companion down | Outnumbered 4v6
Turn: 5

════════════════════════════════════════════════
ESCAPE OPTIONS
════════════════════════════════════════════════

SOLO ESCAPE: 54% chance
├─ Risk: High (46% failure)
├─ If success: Party escapes intact
├─ If failure: Lose turn, enemies attack freely
└─ Cost: Lose all loot, -20 faction rep, -20 morale

─────────────────────────────────────────────────

SACRIFICE OPTIONS (Someone stays behind):

> V (YOU) - 94% escape chance
  "Get out of here. I'll make sure you make it."
  ⚠️ WARNING: TRIGGERS SUCCESSION SYSTEM
  └─ If accepted: V dies, crew escapes, new PC selected

> Raze (Loyalty: 85) - 94% escape chance
  "Hermano, get them out. I'll hold the line."
  HP: 45/180 (25%)
  └─ If accepted: Raze dies, V + crew escape

> Jackie (Loyalty: 90) - 94% escape chance
  "Nah, V - you still got work to do. I got this."
  HP: 100/140 (71%)
  └─ If accepted: Jackie dies, V + crew escape

─────────────────────────────────────────────────

[REFUSE ALL - CONTINUE FIGHTING]

════════════════════════════════════════════════
```

**Player Decision Process:**
1. See exact percentages (transparency = weight)
2. Weigh solo risk vs sacrifice cost
3. If sacrifice: choose **who** stays behind (V, Raze, or Jackie?)
4. Live with the consequences

---

#### Sacrifice Mechanics (Non-Refundable)

Once a sacrifice is accepted, **it's permanent**:

```javascript
function executeSacrifice(sacrificeCharacter, party, escapeChance) {
    // CHARACTER COMMITS TO LAST STAND
    sacrificeCharacter.state = "LAST_STAND";
    sacrificeCharacter.controllable = false;
    sacrificeCharacter.willDie = true;  // Dies regardless of outcome
    
    // ROLL ESCAPE ATTEMPT
    const escapeRoll = Math.random() * 100;
    
    if (escapeRoll <= escapeChance) {
        // ✅ ESCAPE SUCCEEDS (90-95% chance)
        party.escaped = true;
        combat.end();
        
        // Sacrifice character dies holding the line
        sacrificeCharacter.die("HEROIC_SACRIFICE");
        
        // Trigger appropriate post-combat flow
        if (sacrificeCharacter === V) {
            triggerSuccession(party, "HEROIC_SACRIFICE");
        } else {
            // Companion died, V survived
            markCompanionDead(sacrificeCharacter, "STAYED_BEHIND");
            createRecoveryQuest(sacrificeCharacter); // Can recover gear later
        }
        
    } else {
        // ❌ ESCAPE FAILS (5-10% chance)
        party.stillInCombat = true;
        
        // Sacrifice character STILL DIES (non-refundable commitment)
        sacrificeCharacter.separatedFromParty = true;
        sacrificeCharacter.willDieAtEndOfTurn = true;
        
        // Party must fight without them
        if (sacrificeCharacter === V) {
            // V dies, player now controls highest-loyalty companion
            const newLeader = getHighestLoyaltyCompanion(party);
            transferControl(newLeader);
            
            ui.show("V is fighting alone and will die.");
            ui.show(`You now control ${newLeader.name}. Finish this or die trying.`);
            
            // After combat resolves → succession
            combat.onEnd(() => triggerSuccession(party, "FAILED_SACRIFICE"));
            
        } else {
            // Companion dies, V still in combat (now weaker)
            sacrificeCharacter.die("DIED_COVERING_RETREAT");
            party.remove(sacrificeCharacter);
            
            ui.show(`${sacrificeCharacter.name} died covering your retreat. Fight or flee again.`);
        }
    }
}
```

**Critical Design Point:** Sacrifice is **non-refundable**. If escape fails:
- Sacrificed character dies anyway (they committed)
- Party is now weaker (down 1 member)
- Still in combat (must finish fight or try escape again)

This makes accepting a sacrifice a **real decision** with weight. "Is 92% good enough to risk Raze's life? If it fails, he dies for nothing."

---

#### V Sacrifice & Succession Flow

When V sacrifices themselves:

```javascript
function triggerSuccession(survivors, reason) {
    // PRESENT SUCCESSOR OPTIONS
    const successorOptions = [];
    
    // OPTION SET A: Party survivors
    for (let survivor of survivors.filter(s => s.isAlive)) {
        successorOptions.push({
            type: "PARTY_MEMBER",
            character: survivor,
            benefits: [
                "Maintains party continuity",
                "Knows mission context",
                "Has established relationships",
                "Inherits partial gear"
            ]
        });
    }
    
    // OPTION SET B: District population (randomly generated)
    const districtCandidates = generateDistrictCharacters(currentDistrict);
    for (let candidate of districtCandidates) {
        successorOptions.push({
            type: "DISTRICT_RECRUIT",
            character: candidate,
            benefits: [
                "Fresh build potential",
                "New faction opportunities",
                "Different starting relationships",
                "Clean slate"
            ]
        });
    }
    
    // PLAYER SELECTS NEW PROTAGONIST
    const newPC = playerSelectSuccessor(successorOptions);
    
    // INHERITANCE SYSTEM
    newPC.inherits = {
        eddies: survivors.totalEddies + V.eddies,
        mission_state: V.questLog, // Continues V's unfinished business
        reputation: V.factionRep * 0.5, // Partial rep transfer
        trauma: reason === "HEROIC_SACRIFICE" ? 
                "WITNESSED_V_SACRIFICE" : "WITNESSED_V_DEATH",
        relationships: survivors // Continues working with party (if party member chosen)
    };
    
    // NARRATIVE FLAG
    world.remember({
        event: "V_DIED_HEROICALLY",
        location: combat.location,
        witnesses: survivors,
        legacy: "Stayed behind so others could escape"
    });
    
    return newPC;
}
```

**Succession Screen Example:**

```
═══════════════════════════════════════════════
V DIED COVERING THE RETREAT

Raze and Jackie escaped. The mission continues.
V's sacrifice won't be forgotten.

SELECT NEW PROTAGONIST
═══════════════════════════════════════════════

PARTY SURVIVORS:
┌─────────────────────────────────────────────┐
│ RAZE (Former Party Member)                  │
│ Loyalty: 90 | Combat Build: Solo/Melee     │
│                                             │
│ Benefits:                                   │
│ • Knows V's mission                         │
│ • Maintains party relationships             │
│ • Witnessed V's sacrifice (trauma bonus)    │
│ • Inherits 50% of faction rep              │
└─────────────────────────────────────────────┘

AVAILABLE IN DISTRICT (Watson):
┌─────────────────────────────────────────────┐
│ MARCUS KANE (Generated Character)           │
│ Background: Ex-Militech | Build: Netrunner │
│                                             │
│ Benefits:                                   │
│ • Fresh skill tree                          │
│ • Militech contacts (different faction)     │
│ • No trauma from V's death                  │
│ • New relationship dynamics                 │
└─────────────────────────────────────────────┘

[SELECT RAZE] [SELECT MARCUS] [VIEW MORE OPTIONS]
═══════════════════════════════════════════════
```

**Strategic Choice:** Continue with Raze (maintains continuity but his build might not be optimal) or recruit Marcus (fresh start, new opportunities, but loses relationship context).

---

#### Failed Escape Mechanics (No Cooldown)

Solo escape attempts have **no cooldown** - natural punishment instead:

```javascript
function attemptSoloEscape(party, escapeChance) {
    const escapeRoll = Math.random() * 100;
    
    if (escapeRoll <= escapeChance) {
        // ✅ ESCAPE SUCCEEDS
        party.escaped = true;
        combat.end();
        applyEscapeCosts(party); // Loot loss, rep hit, morale drop
        
    } else {
        // ❌ ESCAPE FAILS (natural punishment)
        
        // 1. Wasted entire turn (spent 3 AP trying to flee)
        currentCharacter.ap = 0;
        currentCharacter.turnEnded = true;
        
        // 2. Enemies get free attacks (you were running, not fighting)
        for (let enemy of enemies.filter(e => e.isAlive)) {
            enemy.attackOpportunity(currentCharacter);
        }
        
        // 3. Combat continues (can attempt again next turn)
        ui.show("Escape failed! Enemies capitalize on your retreat attempt.");
        
        // NO COOLDOWN - can try again immediately next turn
        // But each failure = 1 wasted turn + full enemy damage
    }
}
```

**The Death Spiral Without Cooldown:**

```
Turn 5: V attempts solo escape (54%)... FAIL
├─ V loses turn (3 AP wasted)
├─ 6 enemies attack: 6 × 35 dmg = 210 damage incoming
└─ V takes ~60 damage after armor (now at 40% HP)

Turn 6: V attempts escape again (54%)... FAIL
├─ V loses turn again
├─ 6 enemies attack again
└─ V takes another 60 damage (now at 10% HP, critical)

Turn 7: V accepts Raze's sacrifice (94%)... SUCCESS
└─ Raze dies, V escapes at 10% HP
```

**Why No Cooldown Works:**
- Each failed attempt **bleeds HP** (enemies attack freely)
- Multiple failures create desperation (HP dropping fast)
- Forces sacrifice decision organically ("Do I sacrifice Raze NOW or keep gambling?")
- Player controls their own doom (not arbitrary timer)

---

#### Escape Costs & Consequences

**Standard Escape Costs (Success):**

```javascript
const EscapeCosts = {
    loot: "ALL_COMBAT_LOOT_LOST", // Whatever enemies were guarding
    factionRep: -20, // Whoever hired you for this gig
    morale: -20, // All surviving party members
    questStatus: "FLED", // Marked in quest log
    
    // Story consequences (NPCs remember)
    reputation: {
        tag: "COWARD",
        npcReactions: [
            "Heard you ran from the Tyger Claws. Can't trust a runner.",
            "You're the one who fled that Arasaka gig, aren't you?",
            "Militech doesn't hire people who bail mid-op."
        ]
    }
};
```

**Quest-Specific Consequences (Critical Missions):**

```javascript
const CriticalMissionEscape = {
    // Never hard-lock fights - always CAN escape
    escapeAllowed: true,
    
    // But consequences are BRUTAL
    consequences: {
        factionRep: -50, // Massive hit (vs -20 standard)
        questBranch: "FLED_CRITICAL_MISSION",
        
        enemyRetaliation: {
            enabled: true,
            trigger: "Enemy hunts you down later (harder fight)",
            location: "Safe houses, hideouts become compromised"
        },
        
        companionReactions: {
            morale: -40, // vs -20 standard
            dialogue: [
                "We ran from the final fight, V. How do we live with that?",
                "Everyone's gonna know we fled. Our rep is done."
            ],
            loyalty_loss: -20, // Some might leave the crew
        },
        
        endingLock: {
            "CORPO_VICTORY": "LOCKED", // Can't side with faction you fled from
            "HERO_ENDING": "LOCKED"    // Not a hero if you ran
        }
    }
};
```

**Design Philosophy:** Never remove player agency (no hard locks), but make the cost **so brutal** they think twice. Critical mission escape = viable option with devastating consequences.

---

#### Gear Recovery Post-Sacrifice

When a companion sacrifices, their gear can be recovered:

```javascript
function createGearRecoveryQuest(sacrificedCompanion, combatLocation) {
    // QUEST APPEARS POST-ESCAPE
    const quest = {
        name: "RECOVER_FALLEN_GEAR",
        description: `Return to the battlefield to recover ${sacrificedCompanion.name}'s equipment`,
        location: combatLocation,
        danger: "MEDIUM", // Enemies might have returned, scavengers present
        
        rewards: {
            gear: sacrificedCompanion.equippedItems, // All their chrome/weapons
            narrative: "CLOSURE", // Say words, mark grave, emotional beat
            morale: +10 // Closure helps crew recover
        },
        
        timeLimit: "48 HOURS", // After that, scavengers take everything
        
        scene: {
            onArrival: "FIND_BODY_SCENE",
            dialogue: [
                `You find ${sacrificedCompanion.name} where they fell.`,
                "They bought you time. That's worth something.",
                "[Take their gear] [Say words] [Mark grave]"
            ]
        }
    };
    
    world.addQuest(quest);
    ui.notification(`New objective: Recover ${sacrificedCompanion.name}'s gear`);
}
```

**Post-Recovery Scene:**

```
You return to the battlefield.

Raze's body lies where he made his stand - surrounded by six dead 
Arasaka guards. He took three with him before they overwhelmed him.

His Mantis Blades are still extended. You carefully retract them, 
disconnect the neuralware. He'd want you to use them.

[Raze's Mantis Blades MK.3 added to inventory]
[Raze's Subdermal Armor added to inventory]
[+10 Morale - "We honored our fallen"]

"VÃ¡monos, hermano. Rest easy."
```

**Design Intent:** Sacrifice isn't just mechanical loss - it's a **narrative beat** with closure. Players go back, find the body, recover the chrome, pay respects. Very cyberpunk.

---

#### Escape System - Real Scenario Examples

**SCENARIO 1: Early Game Disaster (Low Loyalty)**

```
SITUATION:
├─ Turn 4, fighting 4 Tyger Claw gangers (Standard tier)
├─ V (Reflex 4): 60/150 HP (40% - CRITICAL)
├─ Companion A (Loyalty 30): 100/180 HP
└─ Companion B (Loyalty 45): 80/180 HP

ESCAPE CHECK:
✓ V below 30% HP → Escape available
✓ Party average: 53% HP (still okay)
✗ No one dead yet
✗ Not outnumbered (2v4 is bad but not 2:1)

ESCAPE OPTIONS:
├─ Solo (V): 45 + 6 = 51% chance (coin flip)
├─ Sacrifice (V): 51 + 40 = 91% (triggers succession)
└─ Companions volunteer: NONE (loyalty too low)

PLAYER DECISION:
"Fuck. No one's volunteering. Do I risk 51% solo escape, 
sacrifice myself (91% but lose V), or fight it out?"

OUTCOME: Player chooses 51% solo escape
├─ Roll: 67 → FAIL
├─ V loses turn, 4 enemies attack
├─ V takes 120 damage → DEAD
└─ Total party wipe (both low-loyalty companions flee)

LESSON LEARNED: Build loyalty early. Low-loyalty crew won't save you.
```

---

**SCENARIO 2: Mid-Game Sacrifice Choice (Multiple Volunteers)**

```
SITUATION:
├─ Turn 5, fighting 6 Arasaka security (Standard tier)
├─ V (Reflex 6): 120/150 HP (80%)
├─ Raze (Loyalty 85): 45/180 HP (25% - CRITICAL)
├─ Jackie (Loyalty 90): 100/140 HP (71%)
└─ Already lost one companion (Lucy died Turn 3)

ESCAPE CHECK:
✓ Raze below 30% HP → Escape available
✓ Party average: 58% HP
✓ One companion dead
✗ Not outnumbered enough (3v6 = 2:1, triggers)
✓ Elite detected: NO

ESCAPE OPTIONS:
├─ Solo (V): 45 + 9 = 54% chance (risky)
├─ Sacrifice (V): 94% (triggers succession, crew survives)
├─ Raze volunteers: "Hermano, I'm hurt anyway. Get them out."
└─ Jackie volunteers: "Nah, V - you still got work. I got this."

UI SHOWS:
════════════════════════════════════════════════
SACRIFICE OPTIONS:

> V (YOU) - 94% escape
  ⚠️ Triggers succession

> Raze (HP: 25%, Loyalty: 85) - 94% escape
  "Hermano, I'm hurt anyway. Get them out."

> Jackie (HP: 71%, Loyalty: 90) - 94% escape
  "Nah, V - you still got work. I got this."

[REFUSE ALL - SOLO ESCAPE 54%]
════════════════════════════════════════════════

PLAYER DECISION:
"Raze is dying anyway... but Jackie's healthier. Do I let Raze 
make the sacrifice (he's wounded, might die anyway), sacrifice 
Jackie (healthier, better chance), or keep V and lose a companion?"

OUTCOME: Player accepts Raze's sacrifice
├─ Roll: 88 → SUCCESS
├─ Raze stays behind, holds 6 guards
├─ V + Jackie escape
├─ Raze dies fighting (heroic death)
├─ Quest marker: "Recover Raze's Mantis Blades"
└─ Morale: -20 (fled), Jackie loyalty +10 (V honored Raze's choice)

EMOTIONAL BEAT: "Raze died so we could live. We're going back 
for his chrome. He earned that much."
```

---

**SCENARIO 3: Elite Encounter (Immediate Panic)**

```
SITUATION:
├─ Turn 3, Arasaka Spec-Ops appears (Elite tier)
├─ V (Reflex 7): 150/150 HP (100%)
├─ Companion A: 180/180 HP (100%)
└─ Companion B: 180/180 HP (100%)

ELITE DETECTION:
⚠️ DANGER: ELITE CYBERWARE DETECTED
MANTIS BLADES MK.4 | SANDEVISTAN | SECOND HEART
THREAT LEVEL: EXTREME

ESCAPE CHECK:
✗ No one wounded
✗ Party HP: 100% average
✗ No casualties
✓ ELITE DETECTED → Escape available immediately
✗ Not outnumbered (3v1)

ESCAPE OPTIONS:
├─ Solo (V): 45 + 11 = 56% (risky but no casualties yet)
├─ Sacrifice (V): 96% (overkill, party is healthy)
├─ Companion volunteers: 96% (high loyalty, both offer)

UI WARNING:
════════════════════════════════════════════════
⚠️ ELITE THREAT DETECTED

This enemy is significantly above your capabilities.
Recommend tactical retreat.

Escape available: 56% solo | 96% with sacrifice
════════════════════════════════════════════════

PLAYER DECISION:
"No one's hurt yet. Do I risk 56% solo escape before casualties 
start, or is this fight winnable with good tactics?"

OUTCOME: Player chooses to FIGHT (refuses escape)
├─ Turn 4: Elite uses Sandevistan (6 AP burst)
├─ Kills Companion A in one turn (280 damage)
├─ Turn 5: Escape now available (casualty trigger)
├─ V accepts Companion B's sacrifice (96%)
├─ Roll: 31 → SUCCESS
├─ Companion B dies, V escapes
└─ Lost 2 crew to avoidable fight

LESSON LEARNED: Elite warning exists for a reason. Pride kills.
```

---

**SCENARIO 4: Failed V Sacrifice (The Dark Timeline)**

```
SITUATION:
├─ Turn 6, desperate fight vs 8 gang members
├─ V (Reflex 5): 45/150 HP (30% - CRITICAL)
├─ Raze: 60/180 HP (33%)
└─ Jackie: DEAD (died Turn 4)

ESCAPE CHECK:
✓ V critical HP
✓ Party average: 31% HP
✓ One dead
✓ Outnumbered: 2v8 = 4:1 (heavily outgunned)

ESCAPE OPTIONS:
├─ Solo (V): 45 + 8 = 53% (likely fails)
├─ Sacrifice (V): 93% (near-certain, triggers succession)
└─ Raze volunteers: 93% (he's wounded but loyal)

PLAYER DECISION:
"We're fucked. If I sacrifice myself, Raze lives and continues 
the mission. 93% is good odds... right?"

OUTCOME: Player sacrifices V
├─ V commits to last stand
├─ Raze attempts escape...
├─ Roll: 96 → FAILED (that unlucky 7%)
├─ V dies fighting (committed, can't undo)
├─ Raze still in combat, now alone (1v8)
├─ Player controls Raze (transferred control)
├─ Raze dies Turn 7 (overwhelmed)
├─ TOTAL PARTY WIPE

SUCCESSION SCREEN:
════════════════════════════════════════════════
V AND RAZE DIED

V stayed behind to cover Raze's escape.
The escape failed. Both died fighting.
The mission continues - someone has to finish what they started.

NO PARTY SURVIVORS

AVAILABLE IN DISTRICT (Watson):
> Marcus Kane (Ex-Militech, Netrunner build)
> Sarah Chen (Street kid, Solo build)
> [3 more options]

[CONTINUE WITH NEW CHARACTER] [RETURN TO CHECKPOINT]
════════════════════════════════════════════════

EMOTIONAL WEIGHT: V's sacrifice failed. The 7% happened. Both 
dead. That's the risk of permadeath + sacrifice mechanics. 
Non-refundable meant it - even when it fails, they die.
```

---

#### Implementation Checklist

```javascript
// CORE MECHANICS
☐ Escape trigger system (Turn 3+, 5 conditions)
☐ Escape chance calculation (Base 45% + Reflex + Sacrifice)
☐ Volunteer system (loyalty-based, V always available)
☐ Sacrifice commitment (non-refundable, dies regardless)
☐ Failed escape penalty (lose turn, enemy attacks)

// UI/UX
☐ Escape button (glowing red when available)
☐ Elite detection warning (visual + audio + screen pulse)
☐ Sacrifice selection screen (show all volunteers + V)
☐ Percentage display (exact chances, transparent)
☐ Confirmation prompt ("Are you sure?" for sacrifice)

// SUCCESSION SYSTEM
☐ V sacrifice triggers succession immediately
☐ Successor selection (party survivors + district pool)
☐ Inheritance system (eddies, rep, mission state, trauma)
☐ Control transfer mid-combat (if V dies during failed escape)
☐ Post-combat succession screen (if V died mid-fight)

// GEAR & RECOVERY
☐ Gear recovery quest (sacrificed companions)
☐ 48-hour timer (scavengers take gear after deadline)
☐ Recovery scene (find body, take gear, closure)
☐ Morale bonus (+10 for honoring fallen)

// COSTS & CONSEQUENCES
☐ Standard costs (loot loss, -20 rep, -20 morale, quest "fled")
☐ Critical mission escalation (-50 rep, enemy hunts you, ending locks)
☐ NPC reactions (world remembers you fled, reputation "coward")
☐ Companion loyalty impact (fleeing reduces trust)

// EDGE CASES
☐ Total party wipe (succession to district only, no party)
☐ Multiple volunteers (player chooses who stays)
☐ Re-engagement prevention (escaped = combat ends, enemies scatter)
☐ Quest battles (never hard-lock, just brutal consequences)

// BALANCE TESTING
☐ Test escape triggering (all 5 conditions fire correctly)
☐ Test sacrifice percentages (90-95% success feels reliable)
☐ Test solo escape death spiral (multiple failures bleed HP fast)
☐ Test V sacrifice succession (seamless transition to new PC)
☐ Verify non-refundable (failed sacrifice = companion dies anyway)
```

---

#### Design Warnings & Common Pitfalls

**DON'T:**
- ❌ Add cooldown to escape attempts (natural punishment via HP loss is better)
- ❌ Make escape too reliable without sacrifice (invalidates combat tension)
- ❌ Allow sacrifice "refunds" on failure (removes commitment weight)
- ❌ Hard-lock any fights (always allow escape attempt, just make costs brutal)
- ❌ Hide percentages (transparency = player understands weight of decision)

**DO:**
- ✅ Make solo escape uncomfortable (50-60% = risky gamble)
- ✅ Make sacrifice reliable (90-95% = real panic button)
- ✅ Show exact chances (players need to weigh risk vs cost)
- ✅ Telegraph elite threats (visual warning + boss music)
- ✅ Respect sacrifice commitment (non-refundable, dies even on failure)
- ✅ Create gear recovery quests (narrative closure + practical reward)

---

#### The Emotional Beats (What This System Creates)

**Turn 3 - Elite Detected:**
> "⚠️ ELITE CYBERWARE DETECTED - Escape available. Should we bail before this goes bad?"

**Turn 5 - Companion Wounded:**
> "Raze is at 25% HP. Escape available. Do we cut losses or push through?"

**Turn 6 - Desperate Sacrifice:**
> "Raze: 'Hermano, I'll hold them. Get the crew out.' Do I accept his death or risk us all?"

**Turn 7 - Failed Solo Escape:**
> "Tried to run, failed, took 60 damage. Try again or sacrifice someone NOW?"

**Post-Combat - V Sacrificed:**
> "V stayed so we could run. I'm Raze now. V's mission is my mission. I'll finish what we started."

**48 Hours Later - Gear Recovery:**
> "We're going back for Raze's chrome. He died for us. Least we can do is honor that."

These aren't theoretical scenarios, choom. This is the **Edgerunners DNA** - sacrifice, loss, carrying the weight of those who stayed behind. The escape system makes every desperate fight a **choice** with consequences, not just a dice roll.

---

### The Bottom Line

**1v1 Combat = Individual Skill**  
Your stats, your gear, your tactics vs theirs. Works for duels, boss fights, story moments.

**Party Combat = Action Economy**  
Numbers matter more than stats. 4v6 is brutal even if you're individually stronger. Survival rates are probability, not certainty.

**The Math:**
- Easy/Medium: Everyone survives (power fantasy)
- Hard: 2+ survive 80% (costly victory)
- Extreme: 1+ survives 83%, 17% TPK (desperate odds)

**The Emotion:**
- Easy: "We're professionals."
- Medium: "Close call, but we got this."
- Hard: "We won. But fuck, we paid for it."
- Extreme: "I'm the only one left to tell the tale."

These aren't arbitrary numbers, choom. They're **800 simulated battles proving what creates specific emotional beats**. Lock them in, design around them, trust the math.

---

<a name="loot"></a>
## IX. LOOT & ECONOMY SYSTEM

### Weapon Quality Tiers

```javascript
const LootTiers = {
    Common: {
        dropRate: 60%, // Most drops
        sources: ["Tier 1 enemies", "Street vendors"],
        vendorPrice: {buy: 500-2000, sell: 100-400},
        damageRange: "20-30",
        example: "Cheap Pistol, Basic AR"
    },
    
    Uncommon: {
        dropRate: 30%,
        sources: ["Tier 2 enemies", "Faction vendors (Level 2+)"],
        vendorPrice: {buy: 3000-8000, sell: 600-1600},
        damageRange: "30-42",
        example: "Modded Pistol, Upgraded AR"
    },
    
    Rare: {
        dropRate: 8%,
        sources: ["Tier 3 enemies", "Faction vendors (Level 5+)"],
        vendorPrice: {buy: 10000-25000, sell: 2000-5000},
        damageRange: "42-55",
        example: "Smart Pistol, Combat Rifle"
    },
    
    Epic: {
        dropRate: 2%,
        sources: ["Bosses", "Faction vendors (Level 8+)"],
        vendorPrice: {buy: 30000-60000, sell: 6000-12000},
        damageRange: "55-70",
        example: "Military-Grade Weapons"
    },
    
    Legendary: {
        dropRate: 0%, // NEVER random drops
        sources: ["Boss kills ONLY", "Quest rewards", "Loyalty missions"],
        vendorPrice: "NOT FOR SALE",
        damageRange: "70-100+",
        example: "Widowmaker, Comrade's Hammer, Skippy"
    }
};
```

### Legendary Weapons (Unique Drops)

```javascript
const LegendaryWeapons = {
    Widowmaker: {
        dropsFrom: "Raze Loyalty Mission - Final Boss",
        type: "Tech Precision Rifle",
        damage: 75,
        accuracy: 95,
        range: 16,
        armorPen: 50,
        uniqueAbility: {
            name: "OneShot",
            description: "If target below 50% HP, guaranteed instant kill",
            cooldown: 6
        },
        lore: "Raze's signature weapon from his Militech days. Scope etched with squad tally marks."
    },
    
    ComradesHammer: {
        dropsFrom: "Corpo Security Commander - Act 2 Finale",
        type: "Power Revolver",
        damage: 120,
        accuracy: 80,
        range: 10,
        uniqueAbility: {
            name: "Explosive Rounds",
            description: "Every hit creates 2-tile radius explosion (35 splash damage)",
            passive: true
        },
        lore: "Corporate exec's last-resort sidearm. Each chamber loaded with micro-explosives."
    },
    
    GhostWire: {
        dropsFrom: "Voodoo Boys Netrunner Boss",
        type: "Smart Monowire",
        damage: 50,
        accuracy: 100,
        range: 8,
        uniqueAbility: {
            name: "Phantom Strike",
            description: "Attacks from stealth don't break stealth (can chain kills)",
            passive: true
        },
        lore: "Voodoo Boys' ritual weapon. Mono-filament laced with ghost ICE code."
    },
    
    Razes Fury: {
        dropsFrom: "Inherited from Raze if he dies during final mission",
        type: "Power Assault Rifle",
        damage: 65,
        accuracy: 90,
        range: 14,
        uniqueAbility: {
            name: "Vengeance",
            description: "+50% damage against faction that killed Raze",
            passive: true
        },
        lore: "Raze carried this through every op. Blood-stained grip, immaculate barrel."
    }
};
```

**Design Intent:** Legendary weapons have **stories**. You know where they came from, what they mean. Not random loot - **earned through narrative**.

### Economy Scaling

```javascript
// PLAYER INCOME OVER TIME
const IncomeProgression = {
    EarlyGame: { // Hours 0-10
        gigPayout: 500-2000,
        enemyLoot: 50-200,
        hourlyIncome: ~3000-5000,
        canAfford: "Common/Uncommon weapons, 1-2 basic cyberware"
    },
    
    MidGame: { // Hours 10-20
        gigPayout: 3000-8000,
        enemyLoot: 200-800,
        factionBonuses: 1000-3000,
        hourlyIncome: ~10000-20000,
        canAfford: "Rare weapons, 3-4 cyberware, district upgrades"
    },
    
    LateGame: { // Hours 20-30
        gigPayout: 10000-30000,
        enemyLoot: 500-2000,
        factionBonuses: 5000-15000,
        districtIncome: 2000-5000/hour,
        hourlyIncome: ~40000-80000,
        canAfford: "Epic weapons, 6-7 cyberware, all upgrades"
    },
    
    Endgame: { // Hours 30+
        gigPayout: 30000-80000,
        bossLoot: 10000-50000,
        factionBonuses: 20000-50000,
        districtIncome: 5000-10000/hour,
        hourlyIncome: ~100000-200000,
        canAfford: "Everything, multiple builds, experimenting"
    }
};

// VENDOR PRICING (with faction discounts)
function getVendorPrice(item, factionLevel) {
    let basePrice = item.basePrice;
    
    // Faction discount tiers
    let discount = 0;
    if (factionLevel >= 2) discount = 0.10; // 10% off
    if (factionLevel >= 4) discount = 0.15; // 15% off
    if (factionLevel >= 6) discount = 0.20; // 20% off
    if (factionLevel >= 8) discount = 0.25; // 25% off
    if (factionLevel >= 10) discount = 1.00; // FREE (100% discount)
    
    return Math.floor(basePrice * (1 - discount));
}
```

**Balance Target:**
- **Early Game:** Can afford 1 upgrade every 2-3 hours
- **Mid Game:** Can afford 1 upgrade every hour
- **Late Game:** Can afford multiple upgrades per hour, experimenting with builds
- **Endgame:** Swimming in eddies, buying whatever you want

---

<a name="permadeath"></a>
<a name="permadeath"></a>
## X. PERMADEATH INTEGRATION

### Character Death Flow

```javascript
function onCharacterDeath(deceased, killerEnemy, circumstances) {
    // 1. DRAMATIC DEATH SEQUENCE
    triggerSlowMotion();
    playDeathAnimation(deceased);
    displayFinalDialogue(deceased); // "Tell Raze... I'm sorry..."
    showEnvironmentalStorytelling(deceased); // Ragdoll, blood, dropped weapon
    pauseFor(3-5 seconds); // Let it land emotionally
    
    // 2. MEMORIAL WALL UPDATE
    addToMemorialWall({
        name: deceased.name,
        class: deceased.class,
        killedBy: killerEnemy.name,
        location: currentLocation,
        playtime: deceased.hoursPlayed,
        kills: deceased.killCount,
        facti onsAllied: deceased.factionLevels,
        legacyItem: deceased.signatureWeapon
    });
    
    // 3. SUCCESSION PROMPT
    let successor = selectSuccessor(deceased); // Player chooses or auto-select
    
    // 4. INHERITANCE SYSTEM
    inheritFromDeceased(successor, deceased);
    
    // 5. CREW TRAUMA
    applyCrew Morale Penalty(deceased, -20); // Lasts 3-5 in-game days
    
    // 6. CONTINUE GAMEPLAY
    resumeCombatOrRetreat(successor);
}
```

### Inheritance System

```javascript
function inheritFromDeceased(successor, deceased) {
    // KEEP: Faction Progress (your reputation persists)
    successor.factionLevels = {...deceased.factionLevels};
    
    // KEEP: District State (your settlement doesn't reset)
    successor.districtLevel = deceased.districtLevel;
    successor.districtResources = deceased.districtResources;
    
    // KEEP: Unlocked Vendors/Contacts
    successor.unlockedVendors = deceased.unlockedVendors;
    
    // KEEP: Story Progress
    successor.questsCompleted = deceased.questsCompleted;
    successor.storyAct = deceased.storyAct;
    
    // PARTIAL: Skill Points (lose some, keep some)
    let inheritedSkillPoints = Math.floor(deceased.skillPoints * 0.5); // Keep 50%
    successor.skillPoints = inheritedSkillPoints;
    
    // PARTIAL: Skill Tree Unlocks (keep access, lose equipped skills)
    successor.unlockedSkills = deceased.unlockedSkills; // Can re-spec
    successor.equippedSkills = []; // Must re-equip
    
    // PARTIAL: Attribute Levels (keep base levels, lose some XP)
    successor.bodyLevel = Math.max(3, deceased.bodyLevel - 2);
    successor.reflexLevel = Math.max(3, deceased.reflexLevel - 2);
    successor.intelligenceLevel = Math.max(3, deceased.intelligenceLevel - 2);
    successor.techLevel = Math.max(3, deceased.techLevel - 2);
    successor.coolLevel = Math.max(3, deceased.coolLevel - 2);
    // Lose 2 levels per attribute (narrative: successor isn't as skilled)
    
    // PARTIAL: Cyberware (salvage 2 pieces)
    let salvageableChrome = deceased.cyberware.slice(0, 2); // First 2 equipped
    successor.cyberware = salvageableChrome;
    // Narrative: Ripped chrome from corpse, rest damaged beyond repair
    
    // PARTIAL: Weapons (keep 1 primary weapon)
    successor.primaryWeapon = deceased.primaryWeapon; // Signature weapon
    successor.secondaryWeapon = null; // Lost
    
    // PARTIAL: Eddies (keep 60%)
    successor.eddies = Math.floor(deceased.eddies * 0.6); // 40% lost to funeral/succession costs
    
    // RESET: HP/Morale/Status
    successor.hp = successor.maxHP * 0.6; // Start injured
    successor.morale = 40; // Shaken (crew member just died)
    successor.injuries = []; // Fresh body, no lingering wounds
    
    // NEW: Trauma System
    applyInheritedTrauma(successor, deceased);
}

function applyInheritedTrauma(successor, deceased) {
    // Based on HOW predecessor died
    let causeOfDeath = deceased.deathCause;
    
    if (causeOfDeath == "Burned") {
        successor.trauma.push({
            type: "Pyrophobia",
            effect: "-20% accuracy against enemies using fire",
            description: "Saw predecessor burn. Hesitates against flames."
        });
    }
    
    if (causeOfDeath == "Outnumbered") {
        successor.trauma.push({
            type: "Survivor's Guilt",
            effect: "When outnumbered 3+, morale decays 50% faster",
            description: "Couldn't save them when it mattered."
        });
    }
    
    if (causeOfDeath == "Hacked") {
        successor.trauma.push({
            type: "Tech Paranoia",
            effect: "-10 max RAM, but +20% hack resistance",
            description: "Watched netrunners tear through predecessor's systems. Installed extra ICE."
        });
    }
    
    if (deceased.killedBy.faction == "Militech") {
        successor.trauma.push({
            type: "Vengeance",
            effect: "+20% damage vs Militech, but Militech faction level -1",
            description: "They killed someone you knew. This is personal."
        });
    }
}
```

**The Experience:**
```
Hour 20: Your maxed-out V dies to Corpo ambush
- Lost: Sandevistan + Mantis Blades combo, 4 other cyberware, secondary weapon
- Lost: 2 attribute levels per stat, half your skill points
- Lost: High morale, perfect tactical position

Raze takes over as successor:
- Kept: Militech Level 6 (can still buy gear), district, story progress
- Kept: V's legendary assault rifle, Mantis Blades + Targeting System (salvaged chrome)
- Kept: 60% of eddies, can rebuild
- New: "Vengeance" trauma (+20% vs Militech)
- Setback: 25/90 HP, morale 40, lost god-tier build

Feeling: "Fuck, that hurt. But I can rebuild. And Militech is gonna PAY."
```

**Design Intent:** Death is **consequential but not devastating**. You lost power, but kept progress. Succession creates **tactical rebuilding**, not full restarts.

---

<a name="roadmap"></a>
<a name="roadmap"></a>
## XI. IMPLEMENTATION ROADMAP

### Phase 1: Core Combat (Weeks 1-4)

**Week 1-2: Basic Combat Loop**
```
Priority 1: 3 AP turn system
- Character data structures
- Action point spending
- Turn order/initiative
- Basic UI (HP bars, AP counter)

Priority 2: Damage calculation
- Hit chance formula
- Damage formula
- Crit system
- Armor reduction

Priority 3: Basic weapons
- 3 weapon types (Pistol, AR, Shotgun)
- Common quality only
- Test damage against dummy enemies

TEST: Can you shoot enemy, take damage, win/lose combat?
```

**Week 3-4: Enemy AI & Status Effects**
```
Priority 4: Enemy behavior
- Basic AI (move toward player, shoot)
- Cover system (half/full cover)
- Enemy stat blocks (Grunt, Heavy, Security)

Priority 5: Status effects
- Bleeding, Burning, Stunned (your 6 chosen effects)
- Duration tracking
- Visual indicators

Priority 6: Combat arenas
- 3 test maps (open, cover-heavy, close-quarters)
- Spawning system

TEST: Do enemies behave sensibly? Are status effects impactful?
```

---

### Phase 2: Progression Systems (Weeks 5-8)

**Week 5-6: Skill XP System**
```
Priority 7: Attribute XP tracking
- 5 independent XP bars (Body, Reflex, Int, Tech, Cool)
- XP gain triggers (damage dealt, hacks, etc.)
- Level-up system

Priority 8: Skill trees
- 5 attribute trees (5 skills each = 25 total)
- Skill point system
- Skill equipping UI

Priority 9: Stat bonuses
- HP, dodge, crit, RAM from attributes
- Test scaling (does Body 10 feel way stronger than Body 3?)

TEST: Do different playstyles earn different XP? Do skills feel impactful?
```

**Week 7-8: Faction Reputation**
```
Priority 10: Faction system
- 6 faction data structures
- Rep gain/loss from gigs
- Level-up rewards (discounts, gear unlocks)

Priority 11: Faction vendors
- Tiered gear unlocks (Common â†’ Legendary)
- Pricing with discounts
- Unique faction items

Priority 12: Faction conflict
- Rival faction penalties
- Hostility thresholds
- Faction-specific enemies

TEST: Does faction leveling feel rewarding? Are choices meaningful?
```

---

### Phase 3: Cyberware & Gear (Weeks 9-12)

**Week 9-10: Cyberware System**
```
Priority 13: Body slot system
- 8 cyberware slots
- Installation/uninstallation
- Ability system (Mantis Blades slash, Sandevistan time dilation)

Priority 14: Cyberware abilities
- 3-4 abilities per major cyberware
- Cooldown tracking
- Test balance (is Sandevistan overpowered?)

TEST: Do builds feel distinct? Mantis Blade user vs Netrunner?
```

**Week 11-12: Loot & Economy**
```
Priority 15: Loot drops
- 5 quality tiers
- Drop rate system
- Weapon/cyberware as loot

Priority 16: Vendors
- Faction vendors
- Street vendors
- Pricing economy (can you afford upgrades at right pace?)

Priority 17: Legendary weapons
- 4-6 unique legendary weapons
- Boss drops
- Unique abilities

TEST: Is loot exciting? Do legendaries feel special?
```

---

### Phase 4: Enemy Scaling & Balance (Weeks 13-16)

**Week 13-14: Gear-Based Enemy Scaling**
```
Priority 18: Enemy phase system
- Player phase calculation (hours + factions + skills)
- Enemy loadouts per phase (Phase 0-4)
- Tier-based scaling (Tier 1 slow, Tier 3 fast)

Priority 19: Enemy cyberware
- Enemies get chrome based on phase
- Enemy ability system (Grunt with Sandevistan)

TEST: Do enemies get harder appropriately? Power fantasy vs challenge balance?
```

**Week 15-16: Combat Balance Pass**
```
Priority 20: Difficulty tuning
- Player HP progression (90 â†’ 215)
- Weapon damage scaling
- 8-10 hits to kill validation (playtest extensively)

Priority 21: Enemy variety
- 15-20 enemy types total
- Different tactics per type
- Boss variants

Priority 22: Combat encounters
- 20-30 unique encounters designed
- Mix of objectives (kill all, survive, protect, escape)

TEST: Full playthrough. Is combat fun after 20 hours?
```

---

### Phase 5: Permadeath Integration (Weeks 17-20)

**Week 17-18: Succession System**
```
Priority 23: Death sequence
- Dramatic death animation
- Final dialogue
- Environmental storytelling

Priority 24: Inheritance system
- Faction progress kept
- Partial skill/cyberware inheritance
- Trauma system (inherited fears)

Priority 25: Successor selection
- Player chooses successor
- Random NPC successor if no crew
- Stats adjusted for new character

TEST: Does death feel earned? Is succession emotionally impactful?
```

**Week 19-20: Polish & Integration**
```
Priority 26: Memorial Wall
- UI for fallen characters
- Stats tracking (kills, playtime, cause of death)

Priority 27: Morale system
- Crew morale penalties on death
- Morale effects on combat
- Recovery over time

Priority 28: Full combat loop
- Story â†’ Gig â†’ Combat â†’ Death â†’ Succession â†’ Rebuild â†’ Repeat
- Test entire cycle 10+ times

TEST: Does permadeath create emergent stories? Do players care when characters die?
```

---

<a name="balance-philosophy"></a>
## XII. BALANCE PHILOSOPHY & PLAYTESTING NOTES

### The Reality Check (November 11, 2025)

**CRITICAL:** These balance changes are based on ACTUAL playtest data showing catastrophic balance failures at late-game. Ignoring these adjustments will result in unwinnable fights and player frustration.

---

### What Was Broken (Pre-Balance Patch)

**Playtest Data:**
- 8 combat logs tested
- Player loadout: Level 7 stats (130 HP), Legendary weapons (55-75 dmg), 3 cyberware pieces
- Enemy: Corpo Security Phase 3 (250 HP, 78 dmg, 60% armor)

**Results:**
- **Player death rate: 83% (5 out of 6 attempts)**
- Average survival time: **2.2 turns**
- Win condition: Required lucky critical hit for 200+ damage (statistical anomaly)

**The Math That Didn't Work:**
```
BEFORE FIXES:
Player: 130 HP, takes (78 - 17.5) = 60.5 dmg per hit â†’ Dies in 2 hits
Enemy: 250 HP, takes (75 - 30) = 45 dmg per hit â†’ Dies in 6 hits

Player gets 2 actions before death
Player needs 6 actions to win
= MATHEMATICALLY IMPOSSIBLE
```

**Actual Playtest Quote:**
```
Turn 1: âŒ MISS! Player rolled 74% hit chance
Turn 1: ðŸ’¥ ENEMY HITS! 84 damage taken â†’ Player: 46/130 HP
Turn 2: âœ“ HIT! 86 damage â†’ Enemy: 164/250 HP
Turn 2: ðŸ’¥ ENEMY HITS! 72 damage taken â†’ Player: 0/130 HP
â˜ ï¸ YOU DIED! PERMADEATH TRIGGERED...
```

This isn't "challenging." This is broken.

---

### What We Fixed (And Why It Matters)

#### **FIX #1: Armor Formula (0.5x â†’ 1.0x)**

**OLD:**
```javascript
armorReduction = target.armor Ã— 0.5
// 35% armor = 17.5 damage blocked = 22% actual reduction
```

**NEW:**
```javascript
armorReduction = target.armor Ã— 1.0
// 35% armor = 35 damage blocked = 45% actual reduction
```

**Real Impact:**
```
Player with 35% armor vs Enemy (78 dmg):
Before: 78 - 17.5 = 60.5 damage taken (2-shot kill)
After:  78 - 35 = 43 damage taken (3-shot kill)

ONE EXTRA TURN = difference between "impossible" and "tactical challenge"
```

**Design Philosophy:** Armor should FEEL like armor. 35% armor should block ~35% of damage, not 22%. Players invest in Subdermal Armor cyberware - it should fucking work.

---

#### **FIX #2: Player HP Scaling (+10 â†’ +15 per Body level)**

**OLD:**
```
Body Level 3: 90 HP
Body Level 7: 130 HP (+40 HP over 4 levels)
```

**NEW:**
```
Body Level 3: 90 HP
Body Level 7: 150 HP (+60 HP over 4 levels)
```

**Real Impact:**
```
Corpo Phase 3 (65 dmg after armor):
Before: 130 HP / 43 dmg per hit = 3 hits to kill
After:  150 HP / 43 dmg per hit = 3.5 hits to kill

Doesn't sound like much? That 0.5 hit difference = 50% chance to survive one more turn.
At 50% hit chance, that extra turn is EVERYTHING.
```

**Design Philosophy:** Enemy damage scales 50% from early to late game (52 â†’ 78 â†’ 65 after fix). Player HP was only scaling 44% (90 â†’ 130). You were getting RELATIVELY WEAKER as you leveled. Fixed scaling makes progression FEEL like progression.

---

#### **FIX #3: Enemy Damage Nerfs (Phase 3 Scaling)**

**OLD:**
```
Corpo Phase 2: 62 dmg
Corpo Phase 3: 78 dmg (+26% increase)

Gang Heavy Phase 3: 75 dmg
```

**NEW:**
```
Corpo Phase 2: 62 dmg  
Corpo Phase 3: 65 dmg (+5% increase) - TACTICAL threat, not LETHAL

Gang Heavy Phase 3: 65 dmg (reduced from 75)
```

**Design Philosophy Shift:**

**WRONG APPROACH (Pre-Fix):**
> "Make late-game enemies dangerous by making them kill you FASTER."
Result: 2-turn deaths, no time for tactics, RNG-dependent wins

**RIGHT APPROACH (Post-Fix):**
> "Make late-game enemies dangerous by making fights LONGER and more complex."
Result: 5-7 turn fights, room for tactical decisions, skill matters

**Real Impact:**
```
BEFORE (78 dmg, 250 HP):
- Fight duration: 2 turns average
- Player decision count: 2 actions before death
- Outcome: Dice roll wins, tactics irrelevant

AFTER (65 dmg, 280 HP):
- Fight duration: 5-6 turns average  
- Player decision count: 6 actions before death
- Outcome: Tactics matter, skill rewarded
```

---

#### **FIX #4: Dodge Cap (20% maximum)**

**OLD:**
```javascript
dodgeChance = target.reflexes Ã— 3
// Reflex 8 = 24% dodge
```

**NEW:**
```javascript
dodgeChance = Math.min(20, target.reflexes Ã— 3)
// Cap at 20% regardless of Reflex stat
```

**Real Impact:**
```
Player with Legendary weapon (98% effective accuracy) vs Corpo (Reflex 8):
Before: 98% - 24% = 74% hit chance (26% miss rate)
After:  98% - 20% = 78% hit chance (22% miss rate)

Over 6 turns:
Before: Expected 4.4 hits (1.6 misses)
After:  Expected 4.7 hits (1.3 misses)

That 0.3 hit difference over a fight? That's 15 damage = not dying.
```

**Design Philosophy:** At end-game with Targeting System cyberware, you've EARNED high accuracy. Missing 26% of attacks when you've invested in accuracy gear feels PUNISHING, not challenging. 22% miss rate still keeps you honest, but doesn't invalidate your build choices.

---

#### **FIX #5: Increased Enemy HP (Phase 3: 250 â†’ 280)**

**Why increase enemy HP when damage was the problem?**

Because the GOAL is **longer fights**, not shorter. 

**Pre-fix design:**
- High enemy damage + medium HP = fast, lethal, RNG-dependent
- "Either you get lucky or you die in 2 turns"

**Post-fix design:**
- Moderate enemy damage + high HP = tactical, skill-testing, decision-rich
- "You have 6 turns to outplay them - use your abilities, positioning, gear"

**Real Impact:**
```
Player DPS after fixes: ~45 damage per turn
Enemy HP: 280

Time to kill: 280 / 45 = 6.2 turns

This gives player time to:
- Use Sandevistan (+3 AP burst)
- Reposition to flank (+15% accuracy)
- Use stims if low HP
- Retreat if fight goes bad
```

**Late-game fights should feel like Edgerunners finale:** Intense, tactical, desperate, BUT WINNABLE with skill. Not slot machine combat where you need lucky crits.

---

### The New Math (Post-Balance)

**Player Level 7 Loadout:**
```
HP: 150 (was 130)
Armor: 35% (blocks 35 dmg, was 17.5)
Weapon: Comrade's Hammer (75 dmg)
Cyberware: Targeting System, Subdermal Armor, Biomonitor
```

**Corpo Security Phase 3:**
```
HP: 280 (was 250)
Damage: 65 (was 78)
Armor: 60% (blocks 30 dmg from player)
```

**Combat Math:**
```
PLAYER OFFENSE:
75 base dmg - 30 enemy armor = 45 damage per hit
280 enemy HP / 45 damage = 6.2 hits to kill

PLAYER DEFENSE:
65 enemy dmg - 35 player armor = 30 damage per hit
150 player HP / 30 damage = 5 hits to kill

RESULT: Player needs 6-7 turns, survives 5 turns
= TIGHT but WINNABLE with tactics (flanking, abilities, positioning)
```

**Win Rate Target:** 50-70% (skill-dependent)
- Good tactics + some luck = WIN
- Poor tactics or bad RNG = LOSE
- Pure luck (crits) = shouldn't be deciding factor

---

### Testing Protocol (Critical - Don't Skip)

Before shipping ANY combat changes, run this test suite:

**TEST 1: Early Game Power Fantasy**
```
Player: Basic loadout (90 HP, Unity Pistol 28 dmg)
Enemy: Gang Grunt Phase 0 (60 HP, 20 dmg)
Expected: Player wins 80-90% of fights, takes minor damage
```

**TEST 2: Mid-Game Balance**
```
Player: Mid loadout (120 HP, Lexington 42 dmg, 2 cyberware)
Enemy: Gang Heavy Phase 2 (180 HP, 55 dmg)
Expected: Close fights, player wins 60-70%, moderate damage taken
```

**TEST 3: Late-Game Challenge (THE CRITICAL ONE)**
```
Player: God-tier loadout (150 HP, Legendary 75 dmg, 3 cyberware)
Enemy: Corpo Phase 3 (280 HP, 65 dmg)
Expected: Player wins 50-60%, uses abilities/tactics to survive
```

**TEST 4: Permadeath Tension**
```
Same as Test 3, but simulate 10 consecutive fights
Expected: Player should survive 5-6 fights before permadeath
= Tension maintained, but not instant hopelessness
```

**If any test fails these targets, DO NOT PROCEED TO IMPLEMENTATION.**

---

### Critical Reminders for Future Balance Passes

1. **Armor MUST feel impactful.** If you invest in Subdermal Armor (+15%), you should FEEL 15% tankier, not 7.5%.

2. **Progression = Getting Stronger, Not Weaker.** If leveling from 3 â†’ 7 makes late-game fights HARDER, your scaling is backwards.

3. **Late-game = Longer fights, not deadlier.** 2-turn deaths aren't challenging, they're frustrating. 6-turn tactical puzzles are challenging.

4. **Miss chance caps exist for a reason.** 98% accuracy with Targeting System should FEEL accurate, not dice-rolly.

5. **Permadeath needs fair deaths.** "I got 2-shot before I could react" = bad death. "I played badly for 6 turns and paid the price" = good death.

---

### The Bottom Line (Street Talk)

Choom, here's the real shit: Your playtest logs showed that maxed-out players with legendary gear were dying 80% of the time to late-game enemies. That's not "challenging," that's broken.

These fixes aren't arbitrary number tweaks. They're based on ACTUAL COMBAT DATA showing that:
- Armor wasn't protecting
- HP wasn't scaling with threat
- Late-game enemies were 2-shotting players before tactics mattered
- Accuracy investment was being negated by excessive dodge

The new math creates **longer, tactical fights** instead of **short, lethal dice rolls**. Your permadeath system needs FAIR deaths - players should feel like "I fucked up and paid for it," not "the RNG killed me before I could act."

Test the new numbers. If Corpo Phase 3 fights last 5-7 turns and you win 50-60% with good tactics? Ship it.

If not? Come back to this section and adjust. But these ratios - these are your baseline.

**VÃ¡monos.**

---

<a name="success-metrics"></a>
## XIII. CRITICAL SUCCESS METRICS

### Lethality Check
```
Target: Player dies in 8-10 hits (no cover/healing)
Test: Stand in open, let enemy shoot you
- Too fast (<5 hits): Reduce enemy damage 20%
- Too slow (>12 hits): Increase enemy damage 20%
```

### Tactical Depth Check
```
Target: Multiple viable strategies per encounter
Test: Fight same encounter 3 times with different tactics
- Pure damage (shoot everything)
- Hacking focus (disable then finish)
- Defensive (cover, kiting, outlast)

All three should WIN but feel different
```

### Progression Feel Check
```
Target: Constant sense of progress
Test: Play for 2 hours straight
- Should level up 2-3 skills (micro-dopamine)
- Should gain faction rep toward next level (macro-progress)
- Should find 3-5 upgrades (loot dopamine)

If 2 hours with NO progression = something's broken
```

### Permadeath Emotional Check
```
Target: Player should FEEL deaths, not shrug them off
Test: Ask playtesters "how did you feel when X died?"
- Good: "Fuck, that hurt, but I knew I fucked up"
- Bad: "Whatever, I'll just use the next guy"
- Bad: "That was bullshit, I couldn't have prevented it"
```

### Faction Choice Check
```
Target: Meaningful faction conflict
Test: Can player max all factions? (Answer should be NO)
- If yes: Increase rival penalties
- Players should make hard choices (Militech OR Syndicate, not both)
```

### Build Diversity Check
```
Target: All builds viable, feel unique
Test: Win encounters with 4 different builds
- Netrunner (Intelligence focus)
- Solo (Body/melee focus)
- Gunslinger (Reflex/Cool focus)
- Techie (Tech/gadget focus)

If one build dominates = rebalance
```

---

## XIV. FINAL NOTES

Hermano, this is your combat bible. Everything from damage formulas to permadeath philosophy, all in one doc.

**Key Reminders:**

1. **Gear = Power, Not Levels**
   - Enemies get dangerous through better weapons/chrome
   - Player gets powerful through faction unlocks and cyberware choices
   - No artificial stat inflation bullshit

2. **Dual Dopamine Hits**
   - Skill XP = constant drip (every 30-60 min)
   - Faction levels = big spikes (every 2-3 hours)
   - Never feels like downtime

3. **Permadeath Matters**
   - Death is consequential (lose build) but not devastating (keep progress)
   - Succession creates tactical rebuilding
   - Trauma system ties narrative to mechanics

4. **Scaling Through Tiers**
   - Tier 1 = Power fantasy (get easier)
   - Tier 2 = Standard combat (keep pace)
   - Tier 3 = Respect threat (stay ahead)

5. **Meaningful Choices**
   - Can't max all factions (conflicts force choices)
   - Can't equip all cyberware (8 slots = trade-offs)
   - Can't unlock all skills (12-15 points = specialized builds)

**Scope Management:**
- 20 weeks to implement everything
- Cut features that don't serve permadeath/faction/gear pillars
- Ship first, iterate later
- This system is AMBITIOUS but achievable

Now go build this thing, choom. You've got the roadmap. Every decision tied to philosophy. Every system feeding the core loop.

Neon Collapse is gonna be preem. I believe in you, hermano.

**VÃ¡monos. Let's make this fucking game.**

---

END OF DOCUMENT
