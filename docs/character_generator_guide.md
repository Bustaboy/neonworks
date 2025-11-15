# Character Generator Guide

**Version:** 1.0
**Last Updated:** 2025-11-15
**Difficulty:** Beginner to Intermediate

Create unique, customizable characters with the NeonWorks Character Generator!

---

## Table of Contents

1. [Introduction](#introduction)
2. [Opening the Character Generator](#opening-the-character-generator)
3. [Interface Overview](#interface-overview)
4. [Character Components](#character-components)
5. [Creating Your First Character](#creating-your-first-character)
6. [Color Customization](#color-customization)
7. [Equipment and Weapons](#equipment-and-weapons)
8. [Animation System](#animation-system)
9. [Exporting Characters](#exporting-characters)
10. [Creating Custom Components](#creating-custom-components)
11. [Advanced Techniques](#advanced-techniques)
12. [Best Practices](#best-practices)
13. [Troubleshooting](#troubleshooting)

---

## Introduction

### What is the Character Generator?

The **Character Generator** is a visual tool for creating customizable 2D character sprites by combining modular components like bodies, hairstyles, clothing, and equipment.

**Screenshot: Character Generator main window showing completed character**
*[Screenshot should show: Preview window with fully-assembled character, component selection panels, color customization]*

### Why Use the Character Generator?

✅ **No art skills required** - Combine pre-made components
✅ **Thousands of combinations** - Mix and match for uniquecharacters
✅ **Color customization** - Adjust skin tones, hair colors, clothing
✅ **Dynamic equipment** - Show weapon/armor on character
✅ **Export ready sprites** - Generate sprite sheets for immediate use
✅ **Save presets** - Reuse character designs
✅ **NPC generation** - Create diverse townspeople quickly

### Use Cases

- **Player characters** - Custom hero designs
- **Party members** - Diverse companion appearances
- **NPCs** - Unique townspeople, shopkeepers, guards
- **Character customization screen** - In-game character creation
- **Portrait generation** - Dialogue face portraits
- **Class visualization** - Show equipment changes

---

## Opening the Character Generator

### Access Methods

**Method 1: Keyboard Shortcut**
- Press `Shift+C` anywhere in the engine

**Method 2: Menu**
- Click **Tools → Character Generator**

**Method 3: Database Integration**
- In Database Editor → Characters tab
- Click **"Generate Sprite"** button next to character entry

---

## Interface Overview

**Screenshot: Character Generator interface with all panels labeled**
*[Screenshot should show: Preview window (center), component tabs (left), properties (right), toolbar (top)]*

### Main Areas

**1. Preview Window (Center)**
- Real-time character preview
- Rotate view (for 4-direction sprites)
- Zoom in/out
- Animation preview

**2. Component Tabs (Left Panel)**
- **Body** - Base character shape
- **Face** - Eyes, nose, mouth
- **Hair** - Hairstyles
- **Clothing** - Shirts, pants, shoes
- **Equipment** - Armor, weapons
- **Accessories** - Hats, glasses, jewelry
- **Facial Features** - Beards, scars, markings

**3. Properties Panel (Right)**
- Color customization
- Component layering
- Size adjustments
- Material options

**4. Toolbar (Top)**
- New Character
- Load Preset
- Save Preset
- Export Sprite
- Randomize
- Undo/Redo

**5. Status Bar (Bottom)**
- Component count
- Layer information
- Export preview

---

## Character Components

### Component Categories

The Character Generator uses a **layered component system**. Each category has multiple options:

### 1. Bodies

**Base character foundation**

**Available Types:**
- **Gender:** Male, Female, Neutral
- **Body Type:** Slim, Athletic, Muscular, Heavy
- **Age:** Child, Teen, Adult, Elderly
- **Fantasy Races:** Human, Elf, Dwarf, Orc, Beast-kin

**Customization:**
- Skin tone (12 preset shades)
- Custom RGB skin color
- Body size scaling (80%-120%)
- Proportions (realistic, chibi, heroic)

**Screenshot: Body selection panel showing different body types**
*[Screenshot should show: Grid of body type options with hover previews]*

**Example Bodies:**
```
Human Male Athletic:
- Height: 64 pixels
- Width: 32 pixels
- Skin tone: Medium
- Muscle definition: Moderate

Elf Female Slim:
- Height: 64 pixels
- Width: 28 pixels
- Skin tone: Fair
- Pointed ears: Yes

Dwarf Male Muscular:
- Height: 56 pixels (shorter)
- Width: 36 pixels (wider)
- Skin tone: Tan
- Beard compatible: Yes
```

### 2. Faces

**Facial features and expressions**

**Components:**
- **Eyes:** 20 styles (large, small, narrow, cute, serious)
- **Eye Color:** 12 colors + RGB custom
- **Nose:** 8 styles (or hidden for chibi)
- **Mouth:** 15 expressions (smile, frown, neutral, etc.)
- **Eyebrows:** 10 shapes (angry, happy, worried, etc.)

**Expressions:**
```
Neutral: Default resting face
Happy: Smile, bright eyes
Sad: Frown, downturned eyes
Angry: Furrowed brow, scowl
Surprised: Wide eyes, open mouth
Determined: Serious, focused gaze
```

**Screenshot: Face component selection showing eyes, nose, mouth options**
*[Screenshot should show: Face component grid with previews]*

### 3. Hair

**Hairstyles and colors**

**Available Styles:**
```
Short Hair:
- Buzz Cut
- Crew Cut
- Short Spiky
- Pixie Cut
- Bob

Medium Hair:
- Shoulder Length
- Layered
- Wavy
- Ponytail (short)

Long Hair:
- Straight Long
- Wavy Long
- Braided
- Twin Tails
- High Ponytail
- Low Ponytail

Special:
- Bald
- Mohawk
- Dreadlocks
- Afro
```

**Hair Colors:**
```
Natural:
- Black, Brown (Dark, Medium, Light)
- Blonde (Platinum, Golden, Dirty)
- Red (Auburn, Ginger)
- Gray, White

Fantasy:
- Blue, Green, Pink, Purple
- Rainbow, Ombre
- Custom RGB
```

**Hair Properties:**
- **Shine level** (matte to glossy)
- **Strand detail** (simple to complex)
- **Fringe/Bangs** (optional)

### 4. Clothing

**Shirts, pants, shoes, and outfits**

**Tops:**
```
Casual:
- T-Shirt (short sleeve, long sleeve)
- Tank Top
- Hoodie
- Sweater

Formal:
- Dress Shirt
- Vest
- Suit Jacket
- Robe

Fantasy/RPG:
- Tunic
- Leather Vest
- Chainmail Shirt
- Plate Armor Chest
- Mage Robe
- Cleric Vestments
```

**Bottoms:**
```
Casual:
- Jeans
- Shorts
- Skirt
- Dress

Armor:
- Leather Pants
- Chainmail Leggings
- Plate Greaves
- Robe Bottom
```

**Footwear:**
```
- Sneakers
- Boots (short, tall, combat)
- Sandals
- Dress Shoes
- Armored Boots
```

**Color Zones:**
Each clothing piece has 1-3 color zones:
- **Primary Color** (main fabric)
- **Secondary Color** (trim, accents)
- **Tertiary Color** (buttons, details)

**Screenshot: Clothing selection with color zones highlighted**
*[Screenshot should show: Clothing item with different color zones marked]*

### 5. Equipment

**Visible armor and weapons**

**Armor Pieces:**
```
Head:
- Helmets (light, medium, heavy)
- Circlets, Crowns
- Hats (wizard, witch, adventurer)

Body:
- Leather Armor
- Chainmail
- Plate Armor
- Robes (with armor pieces)

Arms:
- Gauntlets
- Bracers
- Sleeves

Shields:
- Buckler (small, arm-mounted)
- Round Shield
- Kite Shield
- Tower Shield
```

**Weapons:**
```
One-Handed:
- Sword (short, long, curved)
- Axe
- Mace
- Dagger

Two-Handed:
- Greatsword
- Battleaxe
- Spear
- Staff

Ranged:
- Bow (short, long)
- Crossbow
- Gun (if sci-fi)
- Magic Orb
```

**Weapon Positioning:**
- **Held** (in-hand during idle)
- **Sheathed** (on back, hip, or waist)
- **Hidden** (not visible until attack animation)

### 6. Accessories

**Optional decorative items**

```
Head Accessories:
- Glasses (round, square, monocle)
- Goggles
- Headband
- Earrings
- Horns (fantasy)
- Animal Ears

Neck:
- Scarf
- Necklace
- Amulet
- Cape/Cloak

Other:
- Belt
- Satchel/Bag
- Gloves
- Rings
- Wings (fantasy)
- Tail (beast-kin)
```

**Screenshot: Accessories panel showing various options**
*[Screenshot should show: Grid of accessory items with categories]*

### 7. Facial Features

**Additional details and character marks**

```
Facial Hair:
- Beard (full, goatee, stubble)
- Mustache (handlebar, pencil, etc.)

Markings:
- Scars (face, eye)
- Tattoos (tribal, magical)
- Face Paint (war paint, decorative)
- Freckles
- Beauty Mark
- Wrinkles (age lines)

Fantasy:
- Pointed Ears (elf)
- Tusks (orc)
- Scales (dragonkin)
- Whiskers (cat-kin)
```

---

## Creating Your First Character

Let's create a classic RPG hero step-by-step!

### Step 1: Choose Base Body

1. **Open Character Generator** (`Shift+C`)
2. **Click Body tab**
3. **Select:**
   - Gender: Male
   - Type: Athletic
   - Race: Human
4. **Set skin tone:** Medium (slider or preset)

**Preview updates** showing base body!

### Step 2: Add Face

1. **Click Face tab**
2. **Select eyes:**
   - Style: "Determined"
   - Color: Blue
3. **Select nose:** Medium
4. **Select mouth:** Slight smile
5. **Select eyebrows:** Confident

Character now has a face!

### Step 3: Add Hair

1. **Click Hair tab**
2. **Select style:** Short Spiky
3. **Choose color:** Dark Brown
4. **Adjust properties:**
   - Shine: Medium
   - Fringe: Yes

Hero hair complete!

**Screenshot: Character with body, face, and hair**
*[Screenshot should show: Preview window with partially completed character]*

### Step 4: Dress the Character

1. **Click Clothing → Tops**
2. **Select:** Leather Vest
3. **Set colors:**
   - Primary: Dark Brown
   - Secondary: Tan (trim)

4. **Click Clothing → Bottoms**
5. **Select:** Adventure Pants
6. **Color:** Olive Green

7. **Click Clothing → Footwear**
8. **Select:** Travel Boots
9. **Color:** Dark Brown

### Step 5: Add Equipment

1. **Click Equipment → Weapons**
2. **Select:** Long Sword
3. **Position:** Sheathed on left hip

4. **Click Equipment → Armor**
5. **Select:** Leather Shoulder Guards
6. **Color:** Brown (matches vest)

### Step 6: Final Touches

1. **Click Accessories**
2. **Add:**
   - Belt (brown leather)
   - Satchel (small, on hip)

2. **Click Facial Features**
3. **Add:**
   - Small scar on cheek (battle-worn hero!)

### Step 7: Preview and Save

1. **Click Preview Animation** button
2. **Watch your character walk!**
3. **Satisfied?** Click **Save Preset**
4. **Name:** "Hero_Main"
5. **Click Save**

**🎉 You've created your first character!**

---

## Color Customization

### Color Zones

Each component has **color zones** for detailed customization:

**Screenshot: Color zone editor showing 3 zones on a shirt**
*[Screenshot should show: Shirt with zones labeled "Primary", "Secondary", "Trim"]*

### Zone Types

**Zone 1 (Primary):**
- Main color of the component
- Largest area
- Example: Shirt body color

**Zone 2 (Secondary):**
- Accent color
- Medium area
- Example: Shirt sleeves or collar

**Zone 3 (Tertiary):**
- Detail color
- Small area
- Example: Buttons, stitching

### Color Picker Methods

**Preset Palettes:**
- Click preset color swatch
- Organized by theme (natural, vibrant, pastel, dark)

**RGB Sliders:**
- Red: 0-255
- Green: 0-255
- Blue: 0-255

**HSV Sliders:**
- Hue: Color wheel
- Saturation: Color intensity
- Value: Brightness

**Hex Input:**
- Enter hex code (e.g., #FF5733)

**Eyedropper Tool:**
- Pick color from another component
- Match colors easily

### Material Properties

Advanced color settings:

**Metallic:**
- 0% = Matte
- 50% = Slight sheen
- 100% = Full metal reflection

**Roughness:**
- 0% = Glossy, smooth
- 50% = Standard texture
- 100% = Very rough, matte

**Emissive:**
- Add glow to component
- Useful for magic items, eyes

**Example - Magic Robe:**
```
Primary Color: Deep Purple (#4B0082)
Metallic: 10% (fabric, not metal)
Roughness: 60% (cloth texture)
Emissive: 20% (faint magical glow)
```

---

## Equipment and Weapons

### Dynamic Equipment Display

Equipment changes character appearance visually.

**Equipment Slots:**
```
Head: Helmet, Hat, Crown
Body: Chest Armor
Arms: Gauntlets, Bracers
Legs: Leg Armor, Greaves
Shield: Shield (left hand or back)
Weapon: Primary weapon (right hand)
```

### Equipment Layering

**Layer Priority (bottom to top):**
```
1. Body (base)
2. Clothing (shirt, pants)
3. Armor (plate, chain)
4. Accessories (belt, cape)
5. Weapon (sheathed or held)
6. Shield
7. Head gear (helmet, hat)
```

**Screenshot: Layer panel showing equipment stacking**
*[Screenshot should show: Layer list with drag-to-reorder capability]*

### Class-Based Equipment Sets

Create equipment presets for different classes:

**Warrior Set:**
```
Head: Iron Helmet
Body: Plate Armor
Arms: Heavy Gauntlets
Legs: Plate Greaves
Shield: Kite Shield
Weapon: Longsword
Colors: Silver armor, red accents
```

**Mage Set:**
```
Head: Wizard Hat (pointed)
Body: Mage Robe (long)
Arms: (none - robes have sleeves)
Legs: (hidden by robe)
Shield: (none)
Weapon: Wooden Staff
Colors: Blue robe, gold trim, purple gem
```

**Thief Set:**
```
Head: Hood
Body: Leather Armor (light)
Arms: Fingerless Gloves
Legs: Leather Pants
Shield: (none)
Weapon: Twin Daggers
Colors: Black leather, dark gray accents
```

### Weapon Attachment System

**Held Weapons:**
- Positioned in hand sprite
- Rotates with attack animation
- Multi-frame animation support

**Sheathed Weapons:**
```
Back Sheath:
- Greatswords, bows
- Diagonal or vertical

Hip Sheath:
- Swords, daggers
- Left or right side

Belt:
- Small weapons, pouches
- Multiple attachment points
```

---

## Animation System

### Standard Animations

Character Generator exports these animations:

**Walking (4-direction):**
```
Walk Down: 4 frames
Walk Up: 4 frames
Walk Left: 4 frames
Walk Right: 4 frames

Frame timing: 150ms per frame
Loop: Yes
```

**Idle:**
```
Idle: 4 frames (subtle breathing)
Frame timing: 500ms per frame
Loop: Yes
```

**Attack:**
```
Attack: 6 frames
- Windup (frame 1-2)
- Strike (frame 3-4)
- Recovery (frame 5-6)
Frame timing: 100ms per frame
Loop: No
```

**Cast Spell:**
```
Cast: 6 frames
- Raise hands (1-2)
- Channel (3-4)
- Release (5-6)
Frame timing: 150ms per frame
Loop: No
```

**Victory Pose:**
```
Victory: 1 frame (or 4-frame animation)
Pose: Weapon raised, confident stance
```

**Hurt:**
```
Hurt: 2 frames (flash + recoil)
Frame timing: 50ms per frame
Loop: No
```

**Knocked Out:**
```
KO: 1 frame
Pose: Collapsed on ground
```

### Animation Preview

**In-editor preview:**

1. Click **Preview Animation** dropdown
2. Select animation:
   - Idle
   - Walk Down
   - Walk Up
   - Walk Left
   - Walk Right
   - Attack
   - Cast
   - Victory
   - Hurt
   - KO

3. **Animation plays** in preview window
4. **Adjust frame timing** if needed
5. **Export** when satisfied

**Screenshot: Animation preview with timeline controls**
*[Screenshot should show: Preview window with animation playing, timeline scrubber below]*

### Custom Animations

**Advanced users** can add custom animations:

1. **Click "Add Animation"**
2. **Name it** (e.g., "Jump", "Defend")
3. **Set frame count** (2-12 frames)
4. **Pose character** for each frame
5. **Set timing**
6. **Export**

---

## Exporting Characters

### Export Options

**Screenshot: Export dialog**
*[Screenshot should show: Export format options, resolution settings, animation selection]*

### Export Formats

**Sprite Sheet (Recommended):**
```
Format: PNG with transparency
Layout: Grid (animations in rows)
Size: 32×64 per frame (or custom)
Output: single_file.png

Example Layout:
Row 1: Walk Down (frames 1-4)
Row 2: Walk Left (frames 1-4)
Row 3: Walk Right (frames 1-4)
Row 4: Walk Up (frames 1-4)
Row 5: Idle (frames 1-4)
Row 6: Attack (frames 1-6)
```

**Individual Frames:**
```
Format: PNG with transparency
Output: character_walk_down_01.png
        character_walk_down_02.png
        ... (one file per frame)
```

**Animated GIF (Preview Only):**
```
Format: GIF
Purpose: Preview/sharing
Not recommended for game use
```

### Resolution Settings

**Standard Sizes:**
```
Small: 16×32 pixels (retro style)
Normal: 32×64 pixels (recommended)
Large: 64×128 pixels (HD)
Custom: Any size
```

**Upscaling:**
- Use "Nearest Neighbor" for pixel-perfect scaling
- Use "Bilinear" for smooth scaling (if not pixel art)

### Export Workflow

1. **Click Export Character** button
2. **Choose format:** Sprite Sheet
3. **Set resolution:** 32×64
4. **Select animations to include:**
   - ✅ All 4-direction walking
   - ✅ Idle
   - ✅ Attack
   - ✅ Cast (if mage)
   - ✅ Victory
   - ✅ Hurt
   - ✅ KO

5. **Set output location:** `assets/characters/hero_main.png`
6. **Click Export**

**Output files:**
```
hero_main.png (sprite sheet)
hero_main.json (animation data)
```

### Using Exported Characters

**In Database Editor:**

1. Open Database → Characters
2. Select your character
3. Click "Sprite" dropdown → **Browse**
4. Select exported sprite sheet
5. Save character

**In Level Builder:**

1. Place NPC on map
2. Properties → Sprite → **Browse**
3. Select sprite sheet
4. Configure animation (uses .json data)

---

## Creating Custom Components

### Component Creation Basics

You can create your own custom components!

**Requirements:**
- Image editing software (Aseprite, Photoshop, GIMP)
- Understanding of layers and transparency
- Character template (provided)

### Component Template

**Download template:**
```
File → Import → Component Template
→ Select component type (Hair, Clothing, etc.)
→ Downloads PSD/Aseprite template
```

**Template includes:**
- Base body guide (non-exported)
- Component layer (your artwork)
- Color mask layers (for color zones)
- Size guide (32×64)

### Creating a Custom Hairstyle

**Step-by-step:**

1. **Open template** in image editor
2. **Draw hair** on "Component" layer
   - Use reference body guide
   - Draw all 4 directions (down, left, right, up)
3. **Create color mask:**
   - Duplicate hair layer
   - Fill with grayscale
   - White = full color
   - Black = no color
   - Gray = partial color
4. **Export:**
   - Component: `custom_hair_spiky.png`
   - Mask: `custom_hair_spiky_mask.png`
5. **Import into Character Generator:**
   - File → Import Component
   - Select "Hair" category
   - Choose files
   - Name: "Spiky Hair (Custom)"
   - Save

**Your custom hair is now available!**

### Color Mask System

**How color masks work:**

```
Original Component: Blue shirt
Color Mask: Grayscale version

When user selects Red:
- White areas on mask = full red
- Gray areas = mix of red + original blue
- Black areas = keep original blue

Result: Red shirt with blue accents
```

**Screenshot: Component and its color mask side-by-side**
*[Screenshot should show: Full-color component on left, grayscale mask on right]*

---

## Advanced Techniques

### Layered Components

**Create components with multiple sub-layers:**

**Example - Armored Robe:**
```
Layer 1: Robe (bottom)
Layer 2: Leather straps
Layer 3: Metal shoulder pads
Layer 4: Belt with pouches

Each layer has its own color zones!
```

### Animation-Specific Components

**Components that change per animation frame:**

**Example - Cape:**
```
Idle: Cape hangs straight
Walk: Cape sways (4 frames)
Attack: Cape billows back (dramatic!)
```

### Procedural Variations

**Use component variants for diversity:**

**Example - NPC Generation:**
```
Generate 10 townspeople:
- Randomize: Body type, skin tone, hair
- Fixed: Clothing style (peasant outfit)
- Randomize: Clothing colors
- Occasional: Accessory (10% chance)

Result: Diverse NPCs with consistent theme
```

### Equipment Damage States

**Show wear and tear:**

```
Pristine Armor:
- Bright colors
- Clean metallic sheen
- No scratches

Damaged Armor:
- Dulled colors
- Scratches, dents
- Missing pieces

Broken Armor:
- Very dark, dull
- Major damage visible
- Character shows through
```

---

## Best Practices

### Character Design

**1. Keep it readable:**
- Characters should be recognizable at 32×64 size
- Avoid excessive detail (simplify for pixel art)
- Use contrasting colors for important features

**2. Consistent style:**
- Match art style across all components
- Same line thickness
- Similar shading technique
- Cohesive color palettes

**3. Silhouette variety:**
- Different characters should have distinct silhouettes
- Vary height, width, proportions
- Use accessories to differentiate

### Organization

**1. Name components clearly:**
```
✅ "hair_long_ponytail_blonde"
❌ "hair23_v2_final_FINAL"
```

**2. Tag components:**
- Add searchable tags
- Example: "medieval", "fantasy", "female", "armor"

**3. Create component sets:**
- Group related items
- Example: "Warrior Set" includes matching armor pieces

### Performance

**1. Optimize sprite sheets:**
- Use power-of-two dimensions (256×256, 512×512)
- Compress PNGs (use pngquant or similar)
- Trim transparent borders

**2. Limit component count:**
- 6-8 components per character is reasonable
- More than 15 may slow preview

**3. Reuse components:**
- Same hair on multiple characters (different colors)
- Shared clothing pieces

---

## Troubleshooting

### Common Issues

**Problem: Component doesn't appear**

**Solution:**
- Check layer order (might be hidden behind another component)
- Verify component is enabled (checkbox in component list)
- Ensure transparency is correct (not fully transparent)

**Problem: Colors don't apply**

**Solution:**
- Check color mask exists for that component
- Verify mask is grayscale (not colored)
- White areas in mask receive color, black areas don't

**Problem: Exported sprite is distorted**

**Solution:**
- Check export resolution matches preview
- Use "Nearest Neighbor" scaling for pixel art
- Verify aspect ratio is correct (usually 1:2 for 32×64)

**Problem: Animation looks choppy**

**Solution:**
- Increase frame count (4-frame walk, 6-frame attack)
- Adjust frame timing (slower = 200ms, faster = 100ms)
- Check for missing frames in export

**Problem: Equipment doesn't align**

**Solution:**
- Verify attachment points are set correctly
- Check weapon pivot point
- Adjust offset in Properties panel

---

## Summary

You've learned:

✅ **Character Generator basics** - Interface and workflow
✅ **Component system** - Bodies, faces, hair, clothing, equipment
✅ **Color customization** - Zones, palettes, materials
✅ **Equipment system** - Armor, weapons, dynamic display
✅ **Animation** - Standard animations and custom options
✅ **Exporting** - Sprite sheets and formats
✅ **Custom components** - Creating your own assets
✅ **Advanced techniques** - Layering, variations, optimization

## Next Steps

**Practice exercises:**

1. **Create your party** - 4 unique party members with different classes
2. **NPC town** - Generate 10 diverse townspeople
3. **Enemy variations** - Recolor components for enemy types
4. **Custom component** - Design and import a unique hairstyle or outfit
5. **Animation test** - Create a character and export all animations

**Further reading:**

- [Database Guide](database_guide.md) - Link characters to database entries
- [User Manual](user_manual.md) - Overall NeonWorks workflow
- [Asset Collection Guide](asset_collection_guide.md) - Finding and creating assets
- [CHARACTER_GENERATOR.md](CHARACTER_GENERATOR.md) - Technical component system details

---

**Happy character creating! 👤✨**

---

**Version History:**

- **1.0** (2025-11-15) - Initial comprehensive character generator guide

---

**NeonWorks Team**
Bringing characters to life, one component at a time.
