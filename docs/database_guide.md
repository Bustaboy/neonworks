# Database Management Guide

**Version:** 1.0
**Last Updated:** 2025-11-15
**Difficulty:** Beginner to Intermediate

Master the NeonWorks Database system and create rich, balanced game content!

---

## Table of Contents

1. [Introduction to the Database](#introduction-to-the-database)
2. [Opening the Database Editor](#opening-the-database-editor)
3. [Database Structure](#database-structure)
4. [Characters & Classes](#characters--classes)
5. [Enemies & Enemy Groups](#enemies--enemy-groups)
6. [Items & Equipment](#items--equipment)
7. [Skills & Magic](#skills--magic)
8. [Weapons & Armor](#weapons--armor)
9. [Status Effects](#status-effects)
10. [Elements & Attributes](#elements--attributes)
11. [Balancing Your Game](#balancing-your-game)
12. [Import & Export](#import--export)
13. [Best Practices](#best-practices)
14. [Troubleshooting](#troubleshooting)

---

## Introduction to the Database

### What is the Database?

The **Database** is the central repository for all game content in NeonWorks. It stores definitions for:

- **Characters** - Player party members and their stats
- **Classes** - Job systems and progression paths
- **Enemies** - Monsters, bosses, and opponents
- **Items** - Consumables, key items, and treasures
- **Skills** - Abilities, spells, and techniques
- **Equipment** - Weapons, armor, and accessories
- **Status Effects** - Buffs, debuffs, and conditions
- **Elements** - Fire, Ice, Lightning, etc.

**Screenshot: Database Editor main window**
*[Screenshot should show: Tab bar across top, data grid in center, edit form on right]*

### Why Use the Database?

✅ **Centralized data** - All game content in one place
✅ **Visual editing** - No JSON editing required
✅ **Type safety** - Prevents invalid data
✅ **Live preview** - See changes immediately
✅ **Reusability** - Reference data across events
✅ **Balance tools** - Built-in calculators and validators
✅ **Export/Import** - Share data between projects

---

## Opening the Database Editor

### Access Methods

**Method 1: Keyboard Shortcut**
- Press `Ctrl+D` anywhere in the engine

**Method 2: Menu**
- Click **Tools → Database Editor**

**Method 3: Toolbar**
- Click the Database icon (📊) in main toolbar

### First-Time Setup

When you open the Database for a new project, you'll see:

- **Empty tables** - No data yet defined
- **Sample data** - Optional starter templates
- **Import wizard** - Import from templates or other projects

**Recommended:** Import the "Basic RPG" template to start with common items and enemies.

---

## Database Structure

### Database Tabs

The Database Editor has multiple tabs, each managing a category:

| Tab | Contents | Examples |
|-----|----------|----------|
| **Characters** | Player party members | Hero, Wizard, Warrior |
| **Classes** | Job systems | Fighter, Mage, Thief |
| **Enemies** | Monsters and bosses | Slime, Dragon, Demon Lord |
| **Enemy Groups** | Battle formations | Forest Patrol, Boss Fight |
| **Items** | Consumables & key items | Potion, Antidote, Key |
| **Skills** | Abilities and magic | Fireball, Heal, Slash |
| **Weapons** | Equippable weapons | Iron Sword, Staff, Bow |
| **Armor** | Equippable armor | Leather Armor, Robe |
| **Accessories** | Equippable extras | Ring, Amulet, Badge |
| **Status Effects** | Buffs and debuffs | Poison, Burn, Haste |
| **Elements** | Elemental types | Fire, Ice, Lightning |
| **Animations** | Battle animations | Explosion, Slash effect |

### Common Interface Elements

**Data Grid (Left Panel):**
- Lists all entries in current tab
- Click to select/edit
- Right-click for context menu (copy, delete, duplicate)
- Drag to reorder

**Edit Form (Right Panel):**
- Properties for selected entry
- Input fields and dropdowns
- Preview area (for graphics)
- Save/Cancel buttons

**Toolbar (Top):**
- New Entry
- Delete Entry
- Duplicate Entry
- Import/Export
- Search/Filter

---

## Characters & Classes

### Characters

Characters are player-controlled party members.

**Screenshot: Character editor form**
*[Screenshot should show: Character properties form with name, class, stats, equipment slots]*

### Creating a Character

1. **Click Characters tab**
2. **Click "New Character"** button
3. **Fill in basic info:**

```
Name: Elena
Class: Mage
Initial Level: 1
Max Level: 99

Description: "A young mage from the Academy of Magic.
             Specializes in elemental spells."
```

4. **Set base stats:**

```
HP: 80 (lower than warriors)
MP: 150 (high for magic user)
Attack: 8 (weak physical)
Defense: 10
Magic Attack: 25 (strong magic)
Magic Defense: 20
Speed: 12 (average)
Luck: 15
```

### Stat Growth Curves

Define how stats increase per level:

**Linear Growth:**
```
HP Growth: +8 per level
Result: Level 10 = 152 HP, Level 50 = 472 HP
```

**Exponential Growth:**
```
HP Growth: +8 per level + (Level × 0.5)
Result: Level 10 = 185 HP, Level 50 = 712 HP
```

**Custom Curve:**
```
Define HP at specific levels:
Level 1: 80
Level 10: 200
Level 25: 550
Level 50: 1200
Level 99: 3500

(Engine interpolates between points)
```

### Starting Equipment

```
Initial Equipment:
Weapon: Wooden Staff
Armor: Cloth Robe
Accessory: (none)

Starting Inventory:
- Healing Potion ×3
- Magic Water ×2
```

### Starting Skills

```
Known Skills:
- Fire (Basic fire spell)
- Heal (Restore HP to ally)

Skills Learned:
Level 5: Ice
Level 10: Thunder
Level 15: Fire II
Level 20: Full Heal
Level 30: Meteor
```

### Character Traits

Optional attributes for gameplay:

```
Traits:
- "Fire Affinity" → +25% fire damage
- "MP Efficient" → Skills cost 10% less MP
- "Fragile" → Takes 15% more physical damage
```

### Classes

Classes define progression paths and restrictions.

### Creating a Class

1. **Click Classes tab**
2. **Click "New Class"**
3. **Configure:**

```
Class ID: mage
Name: Mage
Description: "Masters of arcane magic"

Equipment Restrictions:
Weapons: Staff, Wand, Dagger
Armor: Robe, Light Armor
Accessories: Any

Stat Modifiers:
HP: ×0.8 (20% lower)
MP: ×1.5 (50% higher)
Attack: ×0.7
Magic Attack: ×1.3
Defense: ×0.9
Magic Defense: ×1.2
```

### Class Skills

Define class-specific skill learning:

```
Skill Tree:
Level 1: Fire, Heal
Level 5: Ice, MP +10%
Level 10: Thunder, Magic Attack +15%
Level 15: Fire II, Ice II
Level 20: Full Heal, Revive
Level 25: MP +20%, Spell Critical +10%
Level 30: Meteor, Arcane Mastery
```

### Class Change System

Allow characters to switch classes:

```
Class Change Rules:
- Can change at Level 10+
- Costs 1000 gold
- Resets to Level 1 in new class
- Keeps some stats (configurable)

Example:
Warrior → Mage
- Retain 50% of HP growth
- Reset Attack/Magic Attack
- Learn Mage skills from Level 1
```

---

## Enemies & Enemy Groups

### Enemies

Define monsters and opponents.

**Screenshot: Enemy editor form**
*[Screenshot should show: Enemy stats, drops, AI behavior settings]*

### Creating an Enemy

1. **Click Enemies tab**
2. **Click "New Enemy"**
3. **Basic info:**

```
Name: Forest Slime
Type: Monster
Level: 3

Description: "A gelatinous creature found in forests.
             Weak but numerous."
```

4. **Stats:**

```
HP: 45
MP: 0 (doesn't use magic)
Attack: 8
Defense: 5
Magic Attack: 0
Magic Defense: 3
Speed: 6
```

5. **Resistances:**

```
Elements:
Fire: 150% (weak to fire)
Ice: 100% (normal)
Lightning: 100%
Physical: 100%

Status Effects:
Poison: Immune
Burn: 200% (very susceptible)
Freeze: 50% (resistant)
```

### Enemy Graphics

```
Battle Sprite: "slime_green.png"
Size: 64×64 pixels

Animation Frames:
Idle: Frames 1-4 (loop)
Attack: Frames 5-8
Hurt: Frame 9
Death: Frames 10-14
```

### Enemy Actions

Define what the enemy can do in battle:

```
Action List:
1. Tackle (80% chance)
   - Physical attack
   - Damage: Attack × 1.0
   - Target: Random party member

2. Slime Shot (15% chance)
   - Ranged attack
   - Damage: Attack × 1.2
   - Target: Front row
   - May cause Slow

3. Defend (5% chance)
   - Increase Defense by 50%
   - Duration: 1 turn
```

### AI Behavior

```
AI Pattern: Simple
- Use highest damage action available
- Target weakest party member (lowest HP)
- Defend if HP < 30%

Advanced AI:
- If party member has < 50 HP → Target them
- If self HP < 30% → Use healing item (if has any)
- Every 3rd turn → Use special ability
```

### Drops and Rewards

```
Guaranteed Drops:
- Experience: 25
- Gold: 15

Item Drops:
- Potion (30% chance) ×1
- Slime Gel (50% chance) ×1
- Rare Slime (5% chance) ×1

Steal-able Items:
- Slime Gel (80% chance)
- Potion (20% chance)
```

### Enemy Groups

Enemy groups define battle formations.

### Creating an Enemy Group

1. **Click Enemy Groups tab**
2. **Click "New Group"**
3. **Configure:**

```
Group ID: forest_patrol
Name: "Forest Patrol"
Background: forest_battle_bg.png
Music: battle_normal.ogg

Enemies:
- Forest Slime @ Position (100, 200)
- Forest Slime @ Position (200, 200)
- Goblin @ Position (150, 150)

Formation: Triangle
```

**Screenshot: Enemy group formation editor**
*[Screenshot should show: Battle background with enemy sprites positioned visually]*

### Boss Enemy Groups

```
Group ID: dragon_boss
Name: "Ancient Dragon"

Enemies:
- Ancient Dragon @ Position (150, 120)

Special Properties:
- Cannot Escape
- Defeat Required (for quest)
- Background: dragon_lair_bg.png
- Music: boss_battle.ogg

Phase System:
Phase 1 (100-66% HP):
- Normal attacks
- Fire breath every 3 turns

Phase 2 (65-33% HP):
- Increased speed
- AOE attacks
- Summons 2 Dragon Whelps

Phase 3 (<33% HP):
- Enraged (+50% attack)
- Meteor strike ultimate
- Heals 500 HP once
```

---

## Items & Equipment

### Items

Consumable and key items.

### Creating a Consumable Item

1. **Click Items tab**
2. **Click "New Item"**
3. **Configure:**

```
Item ID: mega_potion
Name: Mega Potion
Type: Consumable
Usable: In Battle, In Menu

Description: "Restores 200 HP to one ally."

Icon: potion_blue_large.png

Effects:
- Recover HP: 200
- Target: Single Ally

Price: 150 gold
Can Sell: Yes (75 gold)
Max Stack: 99
```

### Item Types

**Consumables:**
```
Healing Potion: Restore 50 HP
Ether: Restore 30 MP
Elixir: Restore 100% HP + MP (rare!)
Antidote: Cure Poison
Phoenix Down: Revive KO'd ally (50% HP)
```

**Key Items:**
```
Old Key: Opens dungeon door (quest item)
Royal Seal: Proof of king's trust
Magic Compass: Reveals hidden paths
Ancient Map: Quest progression item
```

**Battle Items:**
```
Bomb: Deal 100 damage to all enemies
Smoke Bomb: Guaranteed escape
Holy Water: Damage undead enemies
```

### Creating Equipment

Equipment items have stats and equip slots.

**Weapon Example:**

```
Name: Excalibur
Type: Weapon
Slot: Weapon
Subtype: Sword

Stats:
Attack: +75
Magic Attack: +25
Critical Rate: +15%

Special Effects:
- Holy Element
- HP Regen: +5% per turn
- Trait: "Dragonslayer" (+50% vs Dragons)

Equip Requirements:
Classes: Warrior, Knight, Hero
Minimum Level: 40
Required Stat: Strength ≥ 50

Price: 12,000 gold
Can Sell: Yes (6,000 gold)
```

**Armor Example:**

```
Name: Dragon Scale Mail
Type: Armor
Slot: Body

Stats:
Defense: +60
Magic Defense: +40
HP: +100

Resistances:
Fire: +30%
Ice: -10% (weak to ice!)
Physical: +15%

Status Immunity:
Burn: Immune

Equip Requirements:
Classes: Warrior, Knight
Minimum Level: 35

Price: 8,500 gold
```

**Accessory Example:**

```
Name: Ring of Haste
Type: Accessory
Slot: Accessory

Stats:
Speed: +20
Evasion: +10%

Special Effects:
- Auto-Haste (battle start)
- Turn priority +1

Equip Requirements:
None (anyone can equip)

Price: 5,000 gold
```

---

## Skills & Magic

Skills are abilities used in battle or exploration.

**Screenshot: Skill editor form**
*[Screenshot should show: Skill properties, effect configuration, animation preview]*

### Creating an Attack Skill

```
Skill ID: fire_slash
Name: Fire Slash
Type: Physical Skill
Element: Fire

Description: "A flaming sword strike that burns enemies."

Cost:
MP: 12
TP: 0 (if using TP system)

Target: Single Enemy

Damage:
Formula: (User Attack × 2.5) + (User Magic Attack × 1.0)
Element: Fire
Variance: ±10%

Effects:
- Physical Damage
- 30% chance to inflict Burn (3 turns)

Animation: sword_slash_fire
Sound Effect: fire_whoosh.wav

Requirements:
Weapon: Sword equipped
Classes: Warrior, Knight, Spellblade
Minimum Level: 12

Cooldown: None
```

### Creating a Magic Spell

```
Skill ID: meteor
Name: Meteor
Type: Magic Spell
Element: None

Description: "Summons meteors to strike all enemies."

Cost:
MP: 45

Target: All Enemies

Damage:
Formula: (User Magic Attack × 4.0) - (Target Magic Defense × 0.5)
Element: None (ignores resistances!)
Variance: ±15%

Effects:
- Magic Damage
- Ignore 25% of Magic Defense
- 20% chance to reduce Magic Defense (3 turns)

Cast Time: 3 turns (chargeable)
Animation: meteor_shower
Sound Effect: meteor_impact.wav

Requirements:
Class: Mage, Sage
Minimum Level: 30
Equipped: Magic Staff (optional for +20% damage)
```

### Creating a Healing Skill

```
Skill ID: full_heal
Name: Full Heal
Type: Healing Magic
Element: Holy

Description: "Completely restore one ally's HP."

Cost:
MP: 35

Target: Single Ally

Effects:
- Recover HP: 100%
- Cure: Poison, Burn, Bleed
- Remove: Debuffs (Weak, Slow)

Animation: holy_light
Sound Effect: heal_spell.wav

Requirements:
Class: Cleric, Sage, Mage
Minimum Level: 25

Success Rate: 100%
```

### Creating a Support Skill

```
Skill ID: battle_cry
Name: Battle Cry
Type: Support Skill
Element: None

Description: "Rallying cry that boosts party's attack."

Cost:
TP: 20 (uses TP instead of MP)

Target: All Allies

Effects:
- Increase Attack: +30%
- Increase Critical Rate: +15%
- Duration: 5 turns
- Remove Fear, Confuse from all

Animation: buff_aura_red
Sound Effect: warrior_shout.wav

Requirements:
Class: Warrior, Berserker
Weapon: Any

Cooldown: 10 turns
```

### Skill Learning

Define how characters learn skills:

**Level-Up Learning:**
```
Character: Elena (Mage)
Level 5: Learn "Ice"
Level 10: Learn "Thunder"
Level 15: Learn "Fire II"
Level 20: Learn "Full Heal"
Level 30: Learn "Meteor"
```

**Item Learning:**
```
Item: Fire Tome
Effect: Teaches "Fireball" skill
Can Use: Mage, Sage classes only
Consumed: Yes
```

**Quest Reward Learning:**
```
Quest Complete: "Mage's Trial"
Reward: Learn "Arcane Blast"
```

---

## Weapons & Armor

### Weapon Categories

**Swords:**
- Balanced attack and speed
- Most classes can equip
- Critical-focused

**Axes:**
- High attack, low speed
- Warrior/Berserker classes
- Damage variance high

**Spears:**
- Medium attack, high range
- Can hit from back row
- Anti-cavalry bonus

**Bows:**
- Attack from back row
- Dexterity scaling
- Can't be countered

**Staves:**
- Magic attack focused
- Mage/Cleric classes
- May boost healing

**Daggers:**
- Low attack, high speed
- Thief/Assassin classes
- High critical rate

### Armor Categories

**Heavy Armor:**
```
Example: Plate Mail
Defense: +50
Magic Defense: +10
Speed: -10

Classes: Warrior, Knight
Weight: Heavy (affects speed)
```

**Light Armor:**
```
Example: Leather Armor
Defense: +25
Magic Defense: +15
Evasion: +10%

Classes: Thief, Ranger, Monk
Weight: Light
```

**Robes:**
```
Example: Sage's Robe
Defense: +15
Magic Defense: +40
MP: +50

Classes: Mage, Cleric, Sage
Weight: Light
Bonus: MP regeneration +5%
```

### Weapon Scaling

**Strength Scaling (Rank S):**
```
Weapon: Great Axe
Base Attack: 50
Scaling: User Strength × 0.8
Example: Strength 100 → Total Attack = 50 + 80 = 130
```

**Dexterity Scaling (Rank A):**
```
Weapon: Rapier
Base Attack: 35
Scaling: User Dexterity × 0.6
Example: Dexterity 80 → Total Attack = 35 + 48 = 83
```

**Magic Scaling (Rank S):**
```
Weapon: Mystic Staff
Base Attack: 10
Base Magic Attack: 40
Scaling: User Magic × 1.0
Example: Magic 120 → Total Magic Attack = 40 + 120 = 160
```

### Unique Weapon Properties

**Lifesteal:**
```
Weapon: Vampiric Blade
Effect: Restore 20% of damage dealt as HP
```

**Multi-Hit:**
```
Weapon: Twin Daggers
Effect: Attack twice per action (50% damage each)
```

**Elemental:**
```
Weapon: Flametongue
Effect: +Fire element to all attacks
Bonus: +50% damage vs Ice-weak enemies
```

**Critical Boost:**
```
Weapon: Lucky Sword
Effect: Critical rate +30%
Critical damage ×2.5 (instead of ×2.0)
```

---

## Status Effects

Status effects alter character states temporarily.

**Screenshot: Status effect editor**
*[Screenshot should show: Effect properties, icon, duration settings]*

### Debuffs (Negative Effects)

**Poison:**
```
Name: Poison
Type: Damage Over Time
Icon: status_poison.png

Effects:
- HP Loss: 5% of max HP per turn
- Duration: 5 turns
- Stacks: No (doesn't stack with itself)

Removal:
- Antidote item
- Esuna skill
- End of battle

Display: Green tint on character sprite
```

**Burn:**
```
Name: Burn
Type: Damage Over Time + Stat Down

Effects:
- HP Loss: 8% of max HP per turn
- Defense: -20%
- Duration: 3 turns

Spreads: 10% chance to adjacent allies

Removal:
- Ice-elemental skill or item
- End of battle

Display: Red flames particle effect
```

**Paralyze:**
```
Name: Paralyze
Type: Action Disable

Effects:
- 50% chance to lose turn
- Speed: -50%
- Evasion: -30%
- Duration: 3 turns

Removal:
- Full Heal
- Paralyze Heal item
- Wearing off (50% chance per turn)

Display: Yellow sparks, character flashing
```

**Sleep:**
```
Name: Sleep
Type: Incapacitation

Effects:
- Cannot act
- Damage taken +50%
- Wakes up if attacked (guaranteed)
- Duration: 3 turns (or until damaged)

Removal:
- Any damage
- Alarm skill
- Awaken item

Display: "ZZZ" icon, character slumped
```

### Buffs (Positive Effects)

**Haste:**
```
Name: Haste
Type: Stat Boost

Effects:
- Speed: +50%
- Turn frequency: +1 action every 3 turns
- Duration: 5 turns

Stacks: No

Display: Blue speed lines around character
```

**Protect:**
```
Name: Protect
Type: Defensive Buff

Effects:
- Defense: +50%
- Physical damage taken: -33%
- Duration: 5 turns

Stacks: No (but stacks with Shell)

Display: Blue barrier shimmer
```

**Shell:**
```
Name: Shell
Type: Defensive Buff

Effects:
- Magic Defense: +50%
- Magical damage taken: -33%
- Duration: 5 turns

Stacks: No (but stacks with Protect)

Display: Orange barrier shimmer
```

**Regen:**
```
Name: Regen
Type: Healing Over Time

Effects:
- HP Recovery: 10% of max HP per turn
- Duration: 5 turns
- Cancels: Poison, Burn effects

Display: Green sparkles rising from character
```

### Permanent States

**KO (Knocked Out):**
```
Name: KO
Type: Incapacitation (Permanent)

Effects:
- Cannot act
- Removed from turn order
- Does not recover at battle end (manual revival needed)

Removal:
- Phoenix Down item
- Revive skill
- Full Heal (some versions)

Display: Character sprite grayed out, lying down
```

**Death:**
```
Name: Death
Type: Instant KO

Effects:
- Immediately KO character
- Ignores normal damage mechanics
- Rare but devastating

Immunity:
- Safety Bit accessory
- Certain high-level enemies

Display: Soul leaving body animation
```

---

## Elements & Attributes

### Element System

**Screenshot: Element editor showing weakness/resistance relationships**
*[Screenshot should show: Element grid with percentages and color coding]*

### Standard Elements

```
Physical: Normal physical attacks
Fire: Heat and flames
Ice: Cold and freezing
Lightning: Electricity and thunder
Water: Liquid and tidal forces
Wind: Air and cutting blasts
Earth: Rocks and tremors
Holy: Light and divine power
Dark: Shadow and evil energy
Poison: Toxic and venomous
```

### Element Relationships

**Fire Triangle:**
```
Fire ←→ Ice (oppose)
Fire → Wind (strengthens)
Ice → Wind (strengthens)

Gameplay:
Fire is weak to Ice (150% damage)
Ice is weak to Fire (150% damage)
Wind is neutral to both
```

**Advanced Wheel:**
```
Fire → Ice → Wind → Earth → Lightning → Water → Fire

Each element:
- Weak to next element (150% damage)
- Strong vs previous element (50% damage)
- Neutral to all others (100% damage)
```

### Absorption and Immunity

**Absorption:**
```
Enemy: Ice Elemental
Ice Resistance: -100% (absorbs ice damage as healing)

Example:
Ice spell deals 100 damage
Ice Elemental instead heals 100 HP
```

**Immunity:**
```
Enemy: Fire Dragon
Fire Resistance: 0% (completely immune)

Example:
Fire spell deals 200 damage
Fire Dragon takes 0 damage
"Immune!" message displays
```

**Weakness:**
```
Enemy: Forest Treant
Fire Resistance: 200% (double damage)
Ice Resistance: 50% (half damage)

Example:
Fire spell (base 100) → 200 damage
Ice spell (base 100) → 50 damage
```

---

## Balancing Your Game

### Damage Formula Basics

**Physical Attack:**
```
Damage = (Attacker Attack × 2) - (Defender Defense)
Variance = ±10%

Example:
Attack: 50, Defense: 30
Base: (50 × 2) - 30 = 70
With variance: 63-77 damage
```

**Magic Attack:**
```
Damage = (Attacker Magic Attack × 3) - (Defender Magic Defense × 0.5)
Variance = ±15%

Example:
Magic Attack: 60, Magic Defense: 40
Base: (60 × 3) - (40 × 0.5) = 160
With variance: 136-184 damage
```

### Stat Scaling Guidelines

**Early Game (Levels 1-10):**
```
Player HP: 50-150
Player Attack: 10-25
Player Defense: 8-20
Player Magic: 15-35

Enemy HP: 30-100
Enemy Attack: 8-18
Enemy Damage Output: 5-15 per hit
```

**Mid Game (Levels 11-30):**
```
Player HP: 150-400
Player Attack: 25-70
Player Defense: 20-50
Player Magic: 35-90

Enemy HP: 100-500
Enemy Attack: 20-50
Enemy Damage Output: 15-50 per hit
```

**Late Game (Levels 31-50):**
```
Player HP: 400-1000
Player Attack: 70-150
Player Defense: 50-120
Player Magic: 90-200

Enemy HP: 500-2500
Enemy Attack: 50-120
Enemy Damage Output: 50-150 per hit
```

**End Game / Bosses (Levels 51-99):**
```
Player HP: 1000-9999
Player Attack: 150-350
Player Defense: 120-250
Player Magic: 200-500

Boss HP: 5000-99999
Boss Attack: 120-300
Boss Damage Output: 150-500+ per hit
```

### Item Pricing

**Consumables:**
```
Potion (Heal 50 HP): 50g
Hi-Potion (Heal 200 HP): 200g
Ether (Restore 30 MP): 100g
Hi-Ether (Restore 80 MP): 400g
Elixir (Full restore): 5000g
```

**Equipment:**
```
Formula: Base Price = (Total Stat Bonus × 50) + Special Effect Value

Example:
Iron Sword: Attack +15
Price: 15 × 50 = 750g

Flame Sword: Attack +30, Fire Element
Price: (30 × 50) + 500 = 2000g
```

### Enemy Experience & Gold

**Experience Formula:**
```
Base XP = Enemy Level × 10
Modifier: × (1.0 + Boss Modifier + Difficulty)

Examples:
Level 5 Slime: 5 × 10 = 50 XP
Level 10 Mini-Boss: 10 × 10 × 1.5 = 150 XP
Level 20 Boss: 20 × 10 × 2.0 = 400 XP
```

**Gold Formula:**
```
Base Gold = Enemy Level × 5
Modifier: ± Random(50%)

Examples:
Level 5 Enemy: 25g (12-37g range)
Level 20 Enemy: 100g (50-150g range)
```

---

## Import & Export

### Exporting Database

**Full Database Export:**

1. Click **File → Export Database**
2. Choose format:
   - JSON (human-readable)
   - CSV (spreadsheet)
   - XML (structured data)
3. Select location and save

**Selective Export:**

1. Select entries in grid (Ctrl+Click)
2. Right-click → **Export Selected**
3. Choose format and save

**Screenshot: Export dialog**
*[Screenshot should show: Format options, export scope, destination selection]*

### Importing Database

**From Template:**

1. Click **File → Import from Template**
2. Choose template:
   - Basic RPG
   - JRPG Complete
   - Fantasy Adventure
   - Sci-Fi Action
3. Select categories to import
4. Click Import

**From File:**

1. Click **File → Import Database**
2. Select file (JSON, CSV, XML)
3. Choose merge strategy:
   - Replace (overwrite existing)
   - Merge (combine with existing)
   - Add (only add new entries)
4. Click Import

**From Another Project:**

1. Click **File → Import from Project**
2. Browse to other project folder
3. Select categories to import
4. Click Import

---

## Best Practices

### Organization

**1. Use consistent naming:**
```
✅ fire, fire_ii, fire_iii
❌ fire, bigfire, fireball_mega
```

**2. Group related entries:**
```
Items:
├─ Potions (ID 1-20)
├─ Ethers (ID 21-30)
├─ Status Cures (ID 31-50)
├─ Battle Items (ID 51-80)
└─ Key Items (ID 81+)
```

**3. Document everything:**
- Use Description fields
- Add comments for complex formulas
- Note balance intentions

### Balance

**1. Playtest frequently:**
- Test battles at different levels
- Verify difficulty curve
- Check economy (gold/items)

**2. Use the balance calculator:**
- Tools → Balance Calculator
- Input level and stats
- See damage projections

**3. Watch for power creep:**
- Each tier should be 30-50% stronger
- Avoid exponential jumps
- Keep basic items useful

### Performance

**1. Limit database size:**
- 500 entries per category is reasonable
- More than 2000 may slow loading

**2. Optimize graphics:**
- Use sprite sheets for animations
- Keep file sizes reasonable
- PNG compression for icons

**3. Avoid circular references:**
- Skills that call skills infinitely
- Items that give items that give items

---

## Troubleshooting

### Common Issues

**Problem: Character stats don't apply in battle**

**Solution:**
- Check class is assigned correctly
- Verify equipment is actually equipped (not just in inventory)
- Look for status effects modifying stats
- Check Debug Console for errors

**Problem: Skill damage seems wrong**

**Solution:**
- Verify damage formula
- Check elemental resistances
- Ensure stats are correct
- Test with simplified formula first

**Problem: Item doesn't show in shop**

**Solution:**
- Check item price is not 0 (means unsellable)
- Verify "Can Sell" is set to Yes for selling
- Check shop inventory list includes the item

**Problem: Enemy drops wrong items**

**Solution:**
- Verify drop percentages add up correctly
- Check item IDs match database
- Ensure drop table isn't empty
- Check random number generation

**Problem: Database won't save**

**Solution:**
- Check file permissions
- Verify disk space
- Look for validation errors (red highlights)
- Close and reopen Database Editor

**Problem: Import failed**

**Solution:**
- Check file format is correct
- Verify JSON syntax (use validator)
- Ensure IDs don't conflict with existing entries
- Try importing categories individually

---

## Summary

You've learned:

✅ **Database structure** - How game data is organized
✅ **Characters & classes** - Creating party members and jobs
✅ **Enemies & groups** - Designing challenging opponents
✅ **Items & equipment** - Building a robust item system
✅ **Skills & magic** - Creating abilities and spells
✅ **Status effects** - Buffs, debuffs, and conditions
✅ **Elements** - Setting up elemental relationships
✅ **Balancing** - Creating fair, engaging gameplay
✅ **Import/Export** - Sharing and backing up data

## Next Steps

**Practice exercises:**

1. **Create a full party** - 4 characters with different roles
2. **Design enemy progression** - 10 enemies across level range
3. **Build equipment tiers** - Bronze, Iron, Steel, Mythril, etc.
4. **Create skill trees** - Progression path for each class
5. **Balance test** - Ensure fair difficulty curve

**Further reading:**

- [Event Editor Guide](event_editor_guide.md) - Use database items in events
- [JRPG Systems](JRPG_SYSTEMS.md) - Advanced combat mechanics
- [Map Editor Guide](map_editor_guide.md) - Place enemies on maps
- [Character Generator Guide](character_generator_guide.md) - Create custom sprites

---

**Happy database building! 📊**

---

**Version History:**

- **1.0** (2025-11-15) - Initial comprehensive database guide

---

**NeonWorks Team**
Data-driven game development made easy.
