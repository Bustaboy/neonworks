# Neon Collapse - Combat Prototype

A tactical turn-based combat demo showcasing the core combat mechanics from the Neon Collapse TDD.

## Features Implemented

### Combat Systems (from TDD v3.0)
- ✅ **3 AP Economy** - Move (1 AP), Attack (2 AP), Use Item (1 AP)
- ✅ **Turn-based Initiative** - (Reflexes × 2) + d10 roll
- ✅ **Hit Chance Calculation** - Weapon accuracy - dodge chance + modifiers
- ✅ **Damage Calculation** - Base damage + stat bonus + crits + armor + morale
- ✅ **5 Attributes** - Body, Reflexes, Intelligence, Tech, Cool
- ✅ **Escape Mechanic** - Available turn 3+ with sacrifice option
- ✅ **Enemy AI** - Basic targeting and movement
- ✅ **Morale System** - Affects damage output

### Visual Elements
- 32x32 tile-based grid combat
- Character sprites (color-coded: Cyan=Player, Green=Ally, Pink=Enemy)
- HP/AP bars
- Combat log
- Action buttons
- Movement/attack range highlighting

## Demo Scenario

**Player Team:**
- **V** - Assault Rifle (150 HP, Reflex 6)
- **Jackie** - Shotgun (180 HP, Body 6)

**Enemy Team:**
- **Gang Grunt 1** - Pistol (80 HP)
- **Gang Grunt 2** - Pistol (80 HP)
- **Gang Elite** - Assault Rifle (150 HP)

## Controls

### Mouse
- **Click character tiles** - Select/view character
- **Click "Move" button** - Enter movement mode, then click destination
- **Click "Attack" button** - Enter attack mode, then click target
- **Click "End Turn"** - End current character's turn

### Keyboard
- **E** - Attempt escape (when available, turn 3+)
- **SPACE** - Restart combat (after victory/defeat)
- **ESC** - Quit game

## Installation & Running

### Requirements
- Python 3.8+
- Pygame 2.5.2+

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run the Game
```bash
python main.py
```

## Gameplay Tips

1. **Action Points (AP)** - You have 3 AP per turn:
   - Move costs 1 AP (4-6 tile range depending on Reflexes)
   - Attack costs 2 AP
   - You can Move + Attack in one turn (3 AP total)

2. **Hit Chance** - Higher Reflexes = better dodge
   - Check combat log to see hit percentages
   - Flanking enemies improves hit chance

3. **Damage** - Two main factors:
   - **Ranged weapons** scale with Reflexes
   - **Melee weapons** scale with Body
   - Critical hits based on Cool stat (Cool × 2 = crit %)

4. **Escape Mechanic** - Press E after turn 3 if:
   - Party HP below 50%
   - A companion is dead
   - Outnumbered 2:1
   - Solo escape: 45% + (Reflex × 2)%
   - With sacrifice: 93% (companion dies)

5. **Morale System**:
   - Starts at 100, decreases when taking heavy damage
   - High morale (80+) = +15% damage
   - Low morale (20-) = -15% damage

## Combat Formulas (from TDD)

### Initiative
```
Initiative = (Reflexes × 2) + random(1, 10)
```

### Hit Chance
```
Hit Chance = Weapon Accuracy - (Target Reflexes × 3)
Minimum: 5% | Maximum: 95%
```

### Damage
```
Base Damage = Weapon Damage × random(0.85, 1.15)
Stat Bonus = Reflexes × 2 (ranged) OR Body × 3 (melee)
Crit Multiplier = 2.0x (if roll ≤ Cool × 2)
Morale Modifier = 1.0 + ((Morale - 50) / 200)
Armor Reduction = Target Armor × (1 - Weapon Armor Pen)

Final Damage = (Base + Stat) × Crit × Morale - Armor
Minimum Damage: 1
```

## File Structure

```
/game
  ├── main.py           # Main game loop & input handling
  ├── combat.py         # Combat system (turns, initiative, escape)
  ├── character.py      # Character/Enemy classes & attributes
  ├── ui.py             # Rendering (grid, characters, UI panels)
  ├── config.py         # Game constants & balance values
  ├── requirements.txt  # Python dependencies
  └── README.md         # This file
```

## Known Limitations

This is a **combat-only prototype**. Not implemented:
- Quest system
- Faction reputation
- Skill XP progression
- Cyberware system
- District management
- Character succession (permadeath)
- Inventory/loot
- Special abilities (3 AP moves)

These systems are defined in the TDD but not included in this combat demo.

## Technical Details

**Engine:** Pygame 2.5.2
**Resolution:** 1280x720
**Grid Size:** 20×15 tiles (32px each)
**FPS Target:** 60

## Credits

Based on:
- **Neon Collapse Combat TDD v3.0** - "Street Cred & Chrome" progression system
- **Story Bible** - Narrative design
- **Character Bible** - Character profiles
- **World Building Document** - Faction lore

## Next Steps

To expand this prototype:
1. Add special abilities (3 AP ultimate moves)
2. Implement cyberware system
3. Add more enemy types and weapons
4. Create multiple combat scenarios
5. Integrate faction reputation
6. Add character succession on death
7. Build quest framework

---

**Neon Collapse** © 2025 - Combat Prototype v1.0
