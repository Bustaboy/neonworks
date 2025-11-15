# Event Editor Guide

**Version:** 1.0
**Last Updated:** 2025-11-15
**Difficulty:** Beginner to Advanced

Master the NeonWorks Event System and create interactive, dynamic game experiences!

---

## Table of Contents

1. [Introduction to Events](#introduction-to-events)
2. [Opening the Event Editor](#opening-the-event-editor)
3. [Event Editor Interface](#event-editor-interface)
4. [Event Types](#event-types)
5. [Creating Your First Event](#creating-your-first-event)
6. [Event Commands Reference](#event-commands-reference)
7. [Event Triggers](#event-triggers)
8. [Conditional Logic](#conditional-logic)
9. [Variables and Switches](#variables-and-switches)
10. [Common Event Patterns](#common-event-patterns)
11. [Advanced Techniques](#advanced-techniques)
12. [Best Practices](#best-practices)
13. [Troubleshooting](#troubleshooting)

---

## Introduction to Events

### What Are Events?

**Events** are the heart of interactive gameplay in NeonWorks. They define:

- **NPC dialogues** - Conversations with characters
- **Cutscenes** - Story moments and cinematics
- **Item interactions** - Treasure chests, pickups, doors
- **Quest triggers** - Starting and completing quests
- **Environmental effects** - Weather, lighting, sounds
- **Battle initiation** - Random and scripted encounters
- **Map transitions** - Moving between areas
- **Conditional gameplay** - Different outcomes based on player choices

### How Events Work

Events in NeonWorks use a **node-based visual system**. Instead of writing code, you connect nodes that represent actions.

**Simple example:**

```
[Player Interacts] → [Show Dialogue] → [Give Item] → [End]
```

This creates an event where:
1. Player presses interact key
2. Dialogue appears
3. Item is given to player
4. Event ends

**Screenshot: Simple event chain in node editor**
*[Screenshot should show: Node graph with 3 connected nodes - Dialogue, Give Item, End]*

### Why Use the Visual Event System?

✅ **No programming required** - Drag and drop nodes
✅ **Visual feedback** - See the flow of your event
✅ **Easy to modify** - Change behavior without code
✅ **Fast iteration** - Test changes immediately
✅ **Reusable** - Copy events between objects
✅ **Complex logic** - Branches, loops, conditions

---

## Opening the Event Editor

### Access Methods

**Method 1: Function Key**
- Press `F5` anywhere in the engine

**Method 2: Menu**
- Click **Tools → Event Editor**

**Method 3: Context Menu**
- Right-click an object on the map → **Edit Event**

### When to Use the Event Editor

- Creating NPC conversations
- Setting up interactive objects (chests, doors, signs)
- Building cutscenes and story moments
- Designing quest progression
- Implementing puzzle mechanics
- Creating custom game behaviors

---

## Event Editor Interface

**Screenshot: Event Editor with all panels labeled**
*[Screenshot should show: Canvas area, node palette, properties panel, toolbar, minimap]*

### Main Areas

**1. Canvas (Center)**
- Visual workspace for creating event graphs
- Pan: Middle-mouse drag or Spacebar + drag
- Zoom: Mouse wheel or `+`/`-` keys

**2. Node Palette (Left)**
- All available event nodes organized by category
- Drag nodes onto canvas to add them
- Search bar for quick finding

**3. Properties Panel (Right)**
- Configure selected node's settings
- Edit parameters and values
- Preview dialogue text

**4. Toolbar (Top)**
- New Event, Save, Undo/Redo
- Play Event (test it)
- Validate Event (check for errors)

**5. Minimap (Bottom-Right)**
- Overview of entire event graph
- Click to navigate large events
- Shows current viewport

### Toolbar Buttons

| Icon | Name | Function | Shortcut |
|------|------|----------|----------|
| 📄 | New Event | Create blank event | `Ctrl+N` |
| 💾 | Save Event | Save current event | `Ctrl+S` |
| ↶ | Undo | Undo last action | `Ctrl+Z` |
| ↷ | Redo | Redo action | `Ctrl+Y` |
| ▶️ | Play Event | Test event from start | `F5` |
| ✓ | Validate | Check for errors | `F7` |
| 🔍 | Find Node | Search for nodes | `Ctrl+F` |
| 📋 | Copy Event | Copy to clipboard | `Ctrl+C` |
| 📌 | Paste Event | Paste from clipboard | `Ctrl+V` |

---

## Event Types

NeonWorks supports several event types for different purposes.

### 1. Map Events

**Attached to map objects** - NPCs, chests, doors, signs

**Trigger types:**
- **On Interact** - Player presses E/interact key
- **On Touch** - Player walks onto tile
- **On Proximity** - Player gets near (radius setting)
- **Autorun** - Runs automatically when map loads
- **Parallel** - Runs continuously in background

**Example uses:**
- NPC dialogue (On Interact)
- Pressure plates (On Touch)
- Area transitions (On Touch)
- Ambient sounds (Parallel)

### 2. Common Events

**Global events** accessible from anywhere

**Use cases:**
- Shared dialogue snippets
- Quest check logic
- Custom menu systems
- Global cutscenes

### 3. Battle Events

**Triggered during combat**

**Trigger types:**
- Battle Start
- Battle End
- Turn Start
- Turn End
- Enemy Defeated
- Party Member KO'd

**Example uses:**
- Boss introductions
- Special victory conditions
- Conditional enemy abilities

### 4. Quest Events

**Associated with quest stages**

**Use cases:**
- Quest start cutscenes
- Stage completion triggers
- Quest reward delivery

---

## Creating Your First Event

Let's create a simple NPC dialogue event step-by-step.

### Example: Friendly Shopkeeper

**Goal:** Create an NPC who greets the player and opens a shop.

### Step 1: Place the NPC

1. Open Level Builder (`F4`)
2. Click **Place NPC** tool
3. Click on map to place NPC
4. Name it "Shopkeeper"

### Step 2: Open Event Editor

1. Select the NPC
2. Click **Edit Event** in Properties panel
3. Event Editor opens with blank canvas

**Screenshot: Blank event editor canvas**
*[Screenshot should show: Empty canvas with grid pattern, node palette visible on left]*

### Step 3: Add Starting Node

Every event needs a trigger. Since this is an NPC:

1. **Drag "On Interact" node** from palette onto canvas
2. This is your **entry point** - where the event begins

### Step 4: Add Dialogue

1. **Drag "Show Dialogue" node** from palette
2. Place it to the right of "On Interact"
3. **Connect them:**
   - Click output port (right side) of "On Interact"
   - Drag to input port (left side) of "Show Dialogue"
   - Line appears connecting nodes

**Screenshot: Two nodes connected**
*[Screenshot should show: On Interact node connected to Show Dialogue node]*

### Step 5: Configure Dialogue

1. **Select "Show Dialogue" node** (click it)
2. **Properties panel shows dialogue settings**
3. Fill in:

```
Speaker: Shopkeeper
Portrait: (Select shopkeeper portrait if you have one)

Text:
"Welcome to my shop, traveler!
I have the finest potions and
equipment in all the land!

Would you like to see my wares?"
```

4. **Choices:** Add two options:
   - "Yes, show me your items"
   - "No, maybe later"

### Step 6: Add Branching Logic

Now we need different outcomes based on player choice:

1. **Drag "Branch" node** onto canvas (after Show Dialogue)
2. **Connect Show Dialogue → Branch**

The Branch node has **multiple output ports**:
- Output 0: "Yes" choice
- Output 1: "No" choice

### Step 7: Add Shop Opening

For the "Yes" choice:

1. **Drag "Open Shop" node** onto canvas
2. **Connect Branch output 0 → Open Shop**
3. **Configure shop:**

```
Shop ID: general_store
Inventory:
- Healing Potion (50g) ×10
- Magic Water (100g) ×5
- Antidote (30g) ×10
- Iron Sword (500g) ×1
- Leather Armor (400g) ×1
```

### Step 8: Add Polite Response

For the "No" choice:

1. **Drag another "Show Dialogue" node**
2. **Connect Branch output 1 → Show Dialogue**
3. **Configure:**

```
Speaker: Shopkeeper
Text: "No problem! Come back anytime!"
```

### Step 9: End the Event

1. **Drag "End Event" node** onto canvas
2. **Connect both paths to it:**
   - Open Shop → End Event
   - Show Dialogue (polite response) → End Event

**Screenshot: Complete event graph**
*[Screenshot should show: Full event flow from On Interact through branching dialogue to End]*

### Step 10: Save and Test

1. **Click Save** (`Ctrl+S`)
2. **Return to Level Builder**
3. **Click Play** (`F10`)
4. **Test your event!**
   - Walk to NPC
   - Press `E` to interact
   - Try both dialogue choices

**🎉 You've created your first interactive event!**

---

## Event Commands Reference

Here's a comprehensive list of event nodes organized by category.

### Dialogue & Text

#### Show Dialogue
Displays text in a dialogue box.

**Parameters:**
- **Speaker:** NPC name (appears at top)
- **Portrait:** Character image (optional)
- **Text:** Dialogue content (supports line breaks)
- **Speed:** Text scroll speed (instant, slow, normal, fast)
- **Auto-close:** Close after X seconds (0 = wait for input)

**Example:**
```
Speaker: Hero
Text: "I must find the legendary sword!"
Speed: Normal
```

#### Show Choices
Present multiple options to the player.

**Parameters:**
- **Prompt:** Question or context
- **Choices:** List of options (2-6 choices)
- **Default:** Pre-selected choice
- **Cancel Option:** Allow canceling with Escape (-1 = no cancel)

**Outputs:** One output per choice (0, 1, 2, etc.)

**Example:**
```
Prompt: "Which path will you take?"
Choices:
- "Left path (forest)"
- "Right path (mountain)"
- "Turn back"
```

#### Show Narration
Display text without a speaker (narration/description).

**Parameters:**
- **Text:** Narration content
- **Position:** Top, Center, Bottom
- **Background:** Dim screen, Transparent, Solid

### Flow Control

#### Branch (Conditional)
Execute different paths based on conditions.

**Conditions:**
- Variable comparison (=, ≠, <, >, ≤, ≥)
- Switch state (ON/OFF)
- Item possession
- Gold amount
- Party member status
- Quest status

**Outputs:** True path, False path

#### Wait
Pause event execution.

**Parameters:**
- **Duration:** Time in seconds or frames
- **Skippable:** Allow player to skip with button press

#### Loop
Repeat a section of the event.

**Types:**
- **Infinite:** Until "Break Loop" node
- **Count:** Repeat N times
- **While condition:** Until condition is false

#### Break Loop
Exit the current loop early.

#### Label & Jump
Create reusable sections and jump between them.

**Label Parameters:**
- **Label Name:** Identifier for this point

**Jump Parameters:**
- **Target Label:** Which label to jump to

### Items & Equipment

#### Give Item
Add item(s) to party inventory.

**Parameters:**
- **Item ID:** Which item
- **Quantity:** How many (1-999)
- **Silent:** Don't show "received item" message

#### Remove Item
Remove item(s) from inventory.

**Parameters:**
- **Item ID:** Which item
- **Quantity:** How many to remove
- **Silent:** Don't show message

#### Change Equipment
Force equip/unequip items.

**Parameters:**
- **Character:** Which party member
- **Slot:** Weapon, Armor, Accessory
- **Item:** What to equip (empty = unequip)

### Party & Characters

#### Add Party Member
Add character to active party.

**Parameters:**
- **Character ID:** Character to add
- **Initial Level:** Starting level
- **Position:** Where in party (0-3)

#### Remove Party Member
Remove character from party.

**Parameters:**
- **Character ID:** Character to remove
- **Keep Equipment:** Remove gear or leave equipped

#### Change HP/MP
Modify party member stats.

**Parameters:**
- **Target:** Specific character or entire party
- **Type:** HP or MP
- **Operation:** Set, Add, Subtract, Multiply
- **Value:** Amount
- **Allow KO:** Can reduce HP to 0

**Example:**
```
Target: Party Member 1 (Hero)
Type: HP
Operation: Subtract
Value: 50
Allow KO: No (minimum 1 HP)
```

### Maps & Movement

#### Transfer Player
Move player to different map or position.

**Parameters:**
- **Target Map:** Map ID or name
- **Position:** X, Y coordinates
- **Direction:** Which way player faces
- **Transition:** Fade, Slide, None

#### Move Character
Animate character movement.

**Parameters:**
- **Character:** Player, NPC, or Event ID
- **Movement Type:**
  - Move to Position (X, Y)
  - Move Relative (ΔX, ΔY)
  - Move Route (list of steps)
- **Speed:** 1-6 (1=slowest, 6=instant)
- **Wait for Completion:** Block event until movement done

**Route Commands:**
- Move Up/Down/Left/Right
- Turn Up/Down/Left/Right
- Move Forward
- Move Random
- Jump (X, Y)
- Wait (frames)

#### Change Map Properties
Modify map settings during gameplay.

**Parameters:**
- **Tileset:** Switch tileset
- **BGM:** Change background music
- **Lighting:** Adjust brightness/tint
- **Weather:** Set weather effect

### Audio & Visual

#### Play BGM
Play background music.

**Parameters:**
- **Music File:** Audio file path
- **Volume:** 0-100
- **Fade In:** Fade duration in seconds

#### Play Sound Effect
Play a one-shot sound.

**Parameters:**
- **Sound File:** Audio file path
- **Volume:** 0-100
- **Pitch:** 50-150 (100 = normal)

#### Stop BGM
Stop background music.

**Parameters:**
- **Fade Out:** Duration in seconds

#### Show Picture
Display an image on screen.

**Parameters:**
- **Picture ID:** Slot number (1-100)
- **Image File:** Image path
- **Position:** X, Y coordinates
- **Origin:** Top-left, Center
- **Opacity:** 0-255 (0=transparent, 255=opaque)

#### Move Picture
Animate picture movement/effects.

**Parameters:**
- **Picture ID:** Which picture to move
- **Target Position:** New X, Y
- **Duration:** Animation time
- **Opacity:** Target opacity
- **Blend Mode:** Normal, Add, Subtract

#### Erase Picture
Remove a picture from screen.

**Parameters:**
- **Picture ID:** Which picture to remove

#### Screen Flash
Flash the screen with color.

**Parameters:**
- **Color:** RGB values + intensity
- **Duration:** Flash time in frames

#### Screen Shake
Shake the screen for emphasis.

**Parameters:**
- **Power:** Shake intensity (1-9)
- **Speed:** Shake speed (1-9)
- **Duration:** Shake time in frames

### Battle & Combat

#### Start Battle
Initiate a battle encounter.

**Parameters:**
- **Enemy Group ID:** Which enemies to fight
- **Background:** Battle background image
- **Music:** Battle music
- **Escapable:** Can player run away?
- **On Victory:** Event to run if player wins
- **On Defeat:** Event to run if player loses
- **On Escape:** Event to run if player runs

#### Battle Animation
Play battle animation (outside of combat).

**Parameters:**
- **Animation ID:** Which animation
- **Target:** Character or position
- **Wait:** Block until animation finishes

### Quests

#### Start Quest
Begin a quest.

**Parameters:**
- **Quest ID:** Quest identifier
- **Show Notification:** Display "Quest Started" message

#### Complete Quest Stage
Mark quest stage as complete.

**Parameters:**
- **Quest ID:** Which quest
- **Stage ID:** Which stage
- **Auto-Advance:** Move to next stage automatically

#### Fail Quest
Mark quest as failed.

**Parameters:**
- **Quest ID:** Which quest
- **Show Notification:** Display "Quest Failed" message

### Variables & Switches

#### Set Variable
Set the value of a game variable.

**Parameters:**
- **Variable ID:** Variable number (1-9999)
- **Operation:** Set, Add, Subtract, Multiply, Divide
- **Value:** Number or another variable

**Example:**
```
Variable: 1 (Quest Progress)
Operation: Set
Value: 5
```

#### Set Switch
Turn a game switch ON or OFF.

**Parameters:**
- **Switch ID:** Switch number (1-9999)
- **State:** ON or OFF

**Example:**
```
Switch: 10 (Found Secret Room)
State: ON
```

### Advanced

#### Call Common Event
Run a common event.

**Parameters:**
- **Common Event ID:** Which event to call
- **Wait for Completion:** Block until it finishes

#### Script Call
Execute custom Python code (advanced users).

**Parameters:**
- **Script:** Python code to execute
- **Variables:** Pass variables to script

**Example:**
```python
# Give random amount of gold
import random
gold = random.randint(100, 500)
party.add_gold(gold)
```

#### Comment
Add notes to your event (not executed).

**Parameters:**
- **Text:** Comment content

**Use:** Document complex events for future reference.

---

## Event Triggers

Events can be triggered in various ways.

### Trigger Types

**On Interact (Action Button)**
- Player presses E/interact key while facing event
- **Best for:** NPCs, signs, treasure chests, doors

**On Touch (Player Contact)**
- Player walks onto event's tile
- **Best for:** Traps, pressure plates, map transitions

**On Proximity (Near Player)**
- Player gets within N tiles of event
- **Best for:** Automatic cutscenes, enemy alerts

**Autorun**
- Runs immediately when map loads (if conditions met)
- **Best for:** Intro cutscenes, one-time events

**Parallel Process**
- Runs continuously in background
- **Best for:** Ambient effects, timers, dynamic systems

### Conditional Triggers

Add requirements for event to run:

```
Trigger: On Interact
Conditions:
- Switch 5 (Met King) = ON
- Variable 2 (Quest Stage) >= 3
- Party has Item: Royal Seal

If conditions not met: Show message "You can't do that yet."
```

**Screenshot: Trigger configuration dialog**
*[Screenshot should show: Trigger type dropdown, condition list, fallback behavior]*

---

## Conditional Logic

Create dynamic events that change based on game state.

### Branch Node

The Branch node is your primary tool for conditions.

**Comparison Types:**

**Variables:**
```
Variable 1 (Player Level) >= 10
→ True: "You're quite strong!"
→ False: "You still have much to learn."
```

**Switches:**
```
Switch 3 (Defeated Boss) = ON
→ True: "Peace has returned!"
→ False: "The boss still terrorizes us..."
```

**Items:**
```
Has Item: Magic Key
→ True: Use key, open door
→ False: "The door is locked."
```

**Gold:**
```
Party Gold >= 1000
→ True: Can afford expensive item
→ False: "You don't have enough gold."
```

**Party:**
```
Party has member: Wizard
→ True: Wizard-specific dialogue
→ False: Generic dialogue
```

### Nested Conditions

You can nest Branch nodes for complex logic:

```
Branch: Has Item (Ancient Map)
├─ True →
│  └─ Branch: Quest Stage >= 5
│     ├─ True → "You found the treasure!"
│     └─ False → "You need to progress further."
└─ False → "You need the ancient map first."
```

**Screenshot: Nested branch nodes**
*[Screenshot should show: Multiple connected branch nodes creating nested logic]*

---

## Variables and Switches

### Variables

**Variables** store numbers (0 to 9,999,999).

**Common uses:**
- Quest progress stages
- Counters (items collected, enemies defeated)
- Scores and points
- Timers
- Random number storage

**Best practices:**

1. **Document your variables:**
```
Variable 1: Quest 1 Progress (0=not started, 5=complete)
Variable 2: Dragon Kills Counter
Variable 3: Player Reputation (-100 to +100)
```

2. **Use meaningful IDs:**
   - 1-100: Main quest progress
   - 101-200: Side quest progress
   - 201-300: Counters and stats
   - 301-400: Timers and cooldowns

3. **Initialize variables:**
   Set to 0 or default value at game start

### Switches

**Switches** store ON/OFF states.

**Common uses:**
- One-time events (chest opened, cutscene viewed)
- Access gates (door unlocked, bridge repaired)
- Story flags (character met, boss defeated)
- Feature toggles (tutorial enabled, hard mode)

**Best practices:**

1. **Document your switches:**
```
Switch 1: Found Secret Cave (ON = discovered)
Switch 2: Bridge Repaired (ON = can cross)
Switch 3: Met King (ON = has met)
```

2. **Use meaningful IDs:**
   - 1-100: Story progression
   - 101-200: Map changes
   - 201-300: Character states
   - 301-400: Optional content unlocks

3. **Default state:**
   Most switches start OFF, turn ON when triggered

### Control Switches

**Special switches that affect behavior:**

- **A, B, C, D:** Reserved for temporary use
- **Self Switch:** Unique per event instance
- **Local Switch:** Per-map switches

**Self Switch Example:**
```
Event: Treasure Chest
├─ On Interact
├─ Branch: Self Switch A = OFF
│  ├─ True →
│  │  ├─ Show Dialogue: "You found 100 gold!"
│  │  ├─ Give Item: 100 Gold
│  │  └─ Set Self Switch A = ON
│  └─ False →
│     └─ Show Dialogue: "The chest is empty."
```

This makes the chest only give treasure once!

---

## Common Event Patterns

### Pattern 1: Simple NPC Dialogue

**Use case:** NPC with fixed greeting.

```
On Interact
→ Show Dialogue
  Speaker: Villager
  Text: "Beautiful weather today!"
→ End Event
```

### Pattern 2: Quest-Aware NPC

**Use case:** NPC dialogue changes based on quest progress.

```
On Interact
→ Branch: Variable 1 (Quest Stage) = 0
  ├─ True →
  │  └─ Show Dialogue: "I need help finding my cat!"
  │     → Start Quest: "Find the Cat"
  │     → Set Variable 1 = 1
  └─ False →
     └─ Branch: Variable 1 = 1
        ├─ True →
        │  └─ Show Dialogue: "Have you found my cat yet?"
        └─ False →
           └─ Show Dialogue: "Thank you for finding Fluffy!"
→ End Event
```

### Pattern 3: Treasure Chest (One-Time)

```
On Interact
→ Branch: Self Switch A = OFF
  ├─ True →
  │  ├─ Play Sound: "chest_open.wav"
  │  ├─ Show Dialogue: "Found Healing Potion!"
  │  ├─ Give Item: Healing Potion ×1
  │  └─ Set Self Switch A = ON
  └─ False →
     └─ Show Dialogue: "The chest is empty."
→ End Event
```

### Pattern 4: Door with Lock

```
On Interact
→ Branch: Has Item (Silver Key)
  ├─ True →
  │  ├─ Play Sound: "door_unlock.wav"
  │  ├─ Show Dialogue: "You unlocked the door!"
  │  ├─ Remove Item: Silver Key ×1
  │  ├─ Erase Event (door disappears)
  │  └─ Set Switch 10 (Door Unlocked) = ON
  └─ False →
     └─ Show Dialogue: "The door is locked.
                        You need a Silver Key."
→ End Event
```

### Pattern 5: Shop System

```
On Interact
→ Show Dialogue
  Speaker: Merchant
  Text: "Welcome! Care to browse my wares?"
  Choices:
  - "Yes, let me see."
  - "No thanks."
→ Branch (from choices)
  ├─ Choice 0 (Yes) →
  │  └─ Open Shop: "general_store"
  └─ Choice 1 (No) →
     └─ Show Dialogue: "Come back anytime!"
→ End Event
```

### Pattern 6: Cutscene (Character Movement)

```
Autorun (Condition: Switch 5 = ON)
→ Move Character: Player
  Route:
  - Move Left ×3
  - Turn Up
  - Wait 30 frames
→ Show Dialogue
  Speaker: ???
  Text: "Wait! Don't go!"
→ Move Character: NPC_Guard
  Route:
  - Move Up ×5
  - Turn Left
→ Show Dialogue
  Speaker: Guard
  Text: "The king wishes to see you!"
→ Set Switch 5 = OFF (prevent repeat)
→ Set Switch 6 = ON (next scene trigger)
→ End Event
```

### Pattern 7: Random Outcome

```
On Interact
→ Set Variable 99 = Random(1, 3)
→ Branch: Variable 99 = 1
  ├─ True →
  │  └─ Show Dialogue: "You found 50 gold!"
  │     → Give Item: 50 Gold
  └─ False →
     └─ Branch: Variable 99 = 2
        ├─ True →
        │  └─ Show Dialogue: "You found a potion!"
        │     → Give Item: Healing Potion
        └─ False →
           └─ Show Dialogue: "The crate was empty!"
→ Set Self Switch A = ON
→ End Event
```

### Pattern 8: Timed Event

```
Parallel Process
→ Wait: 60 seconds
→ Show Dialogue: "The gates will close soon!"
→ Wait: 30 seconds
→ Show Dialogue: "Last chance to leave!"
→ Wait: 10 seconds
→ Branch: Player in Exit Zone
  ├─ True → (player escaped)
  └─ False →
     └─ Show Dialogue: "You're trapped!"
        → Start Battle: "Guard Group"
→ End Event
```

---

## Advanced Techniques

### Reusable Event Subroutines

Create **Common Events** for reusable logic:

**Common Event: "Generic Heal"**
```
Input: Variable 50 (Heal Amount)
→ Play Sound: "heal.wav"
→ Change HP: Party, Add, Variable 50
→ Show Dialogue: "HP restored!"
→ Return
```

**Usage in map event:**
```
→ Set Variable 50 = 100
→ Call Common Event: "Generic Heal"
```

### State Machine Pattern

Track complex multi-stage processes:

```
Variable 1: Inn State
0 = Not talked yet
1 = Offered stay
2 = Staying overnight
3 = Morning
4 = Checked out
```

**Event updates variable at each stage:**
```
→ Branch: Variable 1 = 0
  ├─ Show offer → Set Variable 1 = 1
→ Branch: Variable 1 = 1
  ├─ Process choice → Set Variable 1 = 2
→ Branch: Variable 1 = 2
  ├─ Fade out → Heal party → Fade in → Set Variable 1 = 3
→ Branch: Variable 1 = 3
  ├─ Morning dialogue → Set Variable 1 = 4
```

### Dynamic Dialogue

Change dialogue based on multiple factors:

```
→ Branch: Party has Wizard
  ├─ True → Set Variable 90 = 1
→ Branch: Quest "Mage Guild" Complete
  ├─ True → Add Variable 90 += 2
→ Branch: Variable 90 = 0
  ├─ Generic dialogue
→ Branch: Variable 90 = 1
  ├─ Wizard-specific dialogue
→ Branch: Variable 90 = 2
  ├─ Quest-complete dialogue
→ Branch: Variable 90 = 3
  ├─ Wizard + Quest dialogue (unique!)
```

### Interrupt Events

Create events that can interrupt other events:

**Parallel Event:**
```
→ Loop
   → Branch: Variable 100 (Alert Level) >= 10
      ├─ True →
      │  ├─ Play Sound: "alarm.wav"
      │  ├─ Show Dialogue: "ALERT! Intruders detected!"
      │  ├─ Start Battle: "Guard Group"
      │  └─ Set Variable 100 = 0
   → Wait: 1 second
```

### Procedural Generation

Use variables and random numbers:

```
→ Loop 10 times
   ├─ Set Variable 50 = Random(1, 100)
   ├─ Set Variable 51 = Random(1, 100)
   ├─ Branch: Variable 50 < 70
   │  └─ Place Treasure at (Variable 50, Variable 51)
```

---

## Best Practices

### Organization

**1. Name your events descriptively:**
   - ❌ "Event001"
   - ✅ "NPC_Merchant_Shop"

**2. Use comments liberally:**
   - Add Comment nodes explaining complex logic
   - Document variable usage
   - Note which switches affect this event

**3. Group related nodes:**
   - Visually arrange nodes in logical groups
   - Use vertical or horizontal flow consistently

**4. Color-code branches:**
   - Success path: Top/left
   - Failure path: Bottom/right

### Performance

**1. Avoid infinite loops:**
   - Always have a break condition
   - Use reasonable wait times in parallel events

**2. Limit parallel processes:**
   - Too many parallel events slow the game
   - Combine related parallel logic when possible

**3. Clean up after yourself:**
   - Erase pictures when done
   - Stop unused BGM
   - Delete temporary events

### Design

**1. Test edge cases:**
   - What if player cancels?
   - What if they don't have required items?
   - What if conditions change mid-event?

**2. Provide feedback:**
   - Always acknowledge player actions
   - Use sounds for confirmation
   - Show visual effects for important moments

**3. Allow skipping:**
   - Let players skip dialogue they've seen
   - Make cutscenes skippable (after first viewing)

**4. Fail gracefully:**
   - Handle missing items/conditions
   - Provide hints if player is stuck
   - Don't trap players in broken states

### Debugging

**1. Use the Debug Console:**
   - Press `F1` to view event errors
   - Check variable/switch values
   - Monitor event execution

**2. Add debug outputs:**
   - Temporarily add dialogue nodes showing variable values
   - Use comments to mark problem areas

**3. Validate before saving:**
   - Click Validate button (`F7`)
   - Fix all errors and warnings

**4. Test thoroughly:**
   - Run through all branches
   - Try unexpected player actions
   - Test with different game states

---

## Troubleshooting

### Event Won't Trigger

**Problem:** NPC event doesn't activate

**Solutions:**
- ✅ Check trigger type (On Interact requires player to face NPC)
- ✅ Verify condition switches/variables
- ✅ Ensure event isn't already running
- ✅ Check NPC is on correct layer
- ✅ Look for errors in Debug Console (`F1`)

### Dialogue Doesn't Appear

**Problem:** Show Dialogue node doesn't work

**Solutions:**
- ✅ Verify node is connected to execution path
- ✅ Check text isn't empty
- ✅ Ensure dialogue isn't overlapping with another
- ✅ Verify portrait image exists (if used)

### Variables Not Changing

**Problem:** Set Variable command doesn't work

**Solutions:**
- ✅ Check variable ID is correct
- ✅ Verify operation type (Set vs Add)
- ✅ Ensure node is being executed (add debug dialogue before/after)
- ✅ Check for typos in variable references

### Event Runs Multiple Times

**Problem:** Event repeats when it shouldn't

**Solutions:**
- ✅ Add Self Switch to prevent repeat
- ✅ Check trigger type (Parallel runs continuously!)
- ✅ Add proper End Event node
- ✅ Use conditional trigger

### Cutscene Gets Stuck

**Problem:** Event freezes during cutscene

**Solutions:**
- ✅ Check all Wait nodes have finite duration
- ✅ Ensure character movement has "Wait for Completion" set correctly
- ✅ Verify loops have break conditions
- ✅ Look for missing connections between nodes

### Performance Issues

**Problem:** Game lags when event runs

**Solutions:**
- ✅ Reduce parallel process count
- ✅ Add wait times in loops
- ✅ Optimize picture/animation usage
- ✅ Break large events into smaller common events

---

## Summary

You've learned:

✅ **Event fundamentals** - What events are and how they work
✅ **Visual editor** - Creating node-based event graphs
✅ **Event types** - Map, common, battle, and quest events
✅ **Commands** - Full reference of event nodes
✅ **Triggers** - When and how events activate
✅ **Logic** - Conditional branching and flow control
✅ **Variables & switches** - Storing and using game state
✅ **Patterns** - Common event structures and best practices
✅ **Advanced techniques** - Reusable events, state machines, dynamic content
✅ **Troubleshooting** - Solving common problems

## Next Steps

**Practice projects:**

1. **Dialogue tree** - NPC with 5+ conversation branches
2. **Puzzle event** - Multi-step puzzle requiring items and switches
3. **Quest chain** - 3-stage quest with branching outcomes
4. **Cutscene** - Animated scene with character movement and camera
5. **Dynamic system** - Weather or time-of-day system using parallel events

**Further reading:**

- [Database Guide](database_guide.md) - Creating items, characters, skills
- [Quest Editor](user_manual.md#step-5-create-a-simple-quest-5-minutes) - Designing quest systems
- [Map Editor Guide](map_editor_guide.md) - Building interactive levels
- [JRPG Systems](JRPG_SYSTEMS.md) - Combat and progression systems

---

**Happy eventing! 🎮**

---

**Version History:**

- **1.0** (2025-11-15) - Initial comprehensive event editor guide

**Contributing:**

Spotted an error or have a cool event pattern to share? Contributions welcome!

---

**NeonWorks Team**
Empowering creators with visual tools.
