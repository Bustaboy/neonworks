# Asset Collection Guide for NeonWorks JRPG Engine

**Version:** 1.0
**Last Updated:** 2025-11-14
**Purpose:** Comprehensive guide for collecting, organizing, and managing game assets

---

## Table of Contents

1. [Overview](#overview)
2. [Required Asset Quantities](#required-asset-quantities)
3. [Recommended Asset Sources](#recommended-asset-sources)
4. [Search Terms by Category](#search-terms-by-category)
5. [Licensing & Legal Compliance](#licensing--legal-compliance)
6. [Quality Standards](#quality-standards)
7. [Format Requirements](#format-requirements)
8. [Tagging Best Practices](#tagging-best-practices)
9. [Sample Manifest Entries](#sample-manifest-entries)
10. [Asset Collection Workflow](#asset-collection-workflow)
11. [Troubleshooting & FAQs](#troubleshooting--faqs)

---

## Overview

Building a complete JRPG requires hundreds of assets across multiple categories. This guide helps you:

- **Find** high-quality, legally-usable assets from trusted sources
- **Organize** assets following NeonWorks conventions
- **License** assets properly with correct attribution
- **Integrate** assets into the asset manifest for immediate use

### Quick Stats

A complete NeonWorks JRPG project typically needs:

- **150+ visual assets** (characters, enemies, UI, tilesets)
- **20+ audio assets** (music tracks, sound effects)
- **50+ icons** (items, skills, status effects)
- **10+ tilesets** (dungeons, towns, world map)

---

## Required Asset Quantities

### Minimum Viable Game (MVP)

| Category | Minimum | Recommended | Notes |
|----------|---------|-------------|-------|
| **Characters** | 4 | 10-20 | Player party + NPCs |
| **Enemies** | 10 | 50-105 | Variety for different zones |
| **Bosses** | 2 | 5-10 | One per major area/chapter |
| **Tilesets** | 3 | 8-12 | Indoor, outdoor, dungeon, special |
| **Icons (Items)** | 15 | 40-60 | Weapons, armor, consumables |
| **Icons (Skills)** | 10 | 30-50 | Attack, magic, support skills |
| **Icons (Status)** | 6 | 12-20 | Poison, stun, buff, debuff |
| **Animations** | 8 | 20-40 | Attack effects, magic spells |
| **UI Elements** | 10 | 20-30 | Windows, buttons, cursors, frames |
| **Face Graphics** | 4 | 20-40 | Character portraits (4 expressions each) |
| **Backgrounds** | 5 | 15-25 | Battle backgrounds, title screen |
| **Music Tracks** | 6 | 12-20 | Battle, town, dungeon, boss, world map |
| **Sound Effects** | 15 | 40-80 | UI, combat, magic, environment |

### Full Production Game

| Category | Target Quantity |
|----------|----------------|
| Characters | 44+ (player characters, NPCs, variations) |
| Enemies | 105+ (common enemies, elite enemies, variants) |
| Bosses | 10-15 (unique sprites, multiple phases) |
| Tilesets | 15-20 (diverse environments) |
| Total Icons | 100+ (items, skills, statuses combined) |
| Animations | 60+ (comprehensive skill/spell effects) |
| Music | 20-30 (varied moods and scenes) |
| SFX | 100+ (complete audio coverage) |

---

## Recommended Asset Sources

### Top-Tier Free Asset Libraries

#### 1. **OpenGameArt.org** ⭐⭐⭐⭐⭐
- **URL:** https://opengameart.org/
- **Best For:** Complete asset packs, character sprites, tilesets
- **License Types:** CC0, CC-BY 3.0, CC-BY 4.0, GPL, OGA-BY
- **Quality:** High (curated community)
- **Search Tips:** Use tags like "RPG", "JRPG", "top-down", "16x16", "32x32"
- **Notable Collections:**
  - LPC (Liberated Pixel Cup) - massive character/tileset collection
  - Kenney's asset packs
  - Sithjester's RPG tileset contributions

**Recommended Search Queries:**
```
- "JRPG character sprite sheet"
- "RPG tileset 32x32"
- "top-down character"
- "fantasy enemy sprite"
- "pixel art icon pack"
```

#### 2. **Kenney.nl** ⭐⭐⭐⭐⭐
- **URL:** https://kenney.nl/assets
- **Best For:** UI elements, icons, consistent art style
- **License:** CC0 (Public Domain)
- **Quality:** Very High (professional artist)
- **Formats:** PNG, SVG (scalable)
- **Collections to Check:**
  - UI Pack (buttons, panels, icons)
  - RPG Pack (characters, items, environment)
  - Icon Pack (1000+ game icons)

**Why Kenney.nl is Excellent:**
- ✅ All assets are CC0 (no attribution required)
- ✅ Consistent, professional art style
- ✅ High resolution with scalable options
- ✅ Regular updates and new packs

#### 3. **Itch.io Asset Store** ⭐⭐⭐⭐
- **URL:** https://itch.io/game-assets/free
- **Best For:** Complete asset packs, diverse art styles
- **License Types:** Varies (check each pack)
- **Quality:** Varies (read reviews)
- **Search Tips:** Filter by "Free", sort by "Most Popular"

**Top Itch.io Creators:**
- Pixel-Boy & AAA (fantasy RPG assets)
- Ansimuz (atmospheric environments)
- Buch (character sprites)
- Szadi art (detailed pixel art)

**Recommended Searches:**
```
- "JRPG asset pack free"
- "RPG character sprite free"
- "fantasy tileset free"
- "pixel RPG UI free"
```

#### 4. **CraftPix.net** ⭐⭐⭐⭐
- **URL:** https://craftpix.net/freebies/
- **Best For:** High-quality free samples, complete packs
- **License:** Free for commercial use (with attribution)
- **Quality:** Very High (professional studio)
- **Note:** Free assets require email signup

**Best Free Packs:**
- 2D Fantasy Character Sprites
- RPG Inventory Icons
- Battle Backgrounds

#### 5. **Game-icons.net** ⭐⭐⭐⭐⭐
- **URL:** https://game-icons.net/
- **Best For:** Item icons, skill icons, status icons
- **License:** CC-BY 3.0
- **Quality:** High
- **Quantity:** 4000+ icons
- **Customization:** Can change colors, download as SVG or PNG

**How to Use:**
1. Search for icon type (sword, potion, fireball)
2. Customize color scheme
3. Download as PNG (64x64 or higher)
4. Attribute artists in CREDITS.txt

#### 6. **Freesound.org** ⭐⭐⭐⭐⭐
- **URL:** https://freesound.org/
- **Best For:** Sound effects, ambient audio
- **License Types:** CC0, CC-BY, CC-BY-NC
- **Quality:** Varies (check ratings and downloads)
- **Search Tips:** Use tags, filter by license

**Essential SFX Searches:**
```
- "sword hit"
- "menu select"
- "magic spell"
- "footstep stone"
- "door open"
- "coin pickup"
- "level up"
```

#### 7. **Incompetech (Music)** ⭐⭐⭐⭐
- **URL:** https://incompetech.com/music/
- **Best For:** Background music tracks
- **License:** CC-BY 4.0 (attribution required)
- **Quality:** High (professional composer)
- **Genres:** Fantasy, adventure, dark, peaceful, battle

**Music Search by Mood:**
- **Town Theme:** "Peaceful", "Ambient"
- **Battle Theme:** "Action", "Fast"
- **Boss Battle:** "Intense", "Epic"
- **Dungeon:** "Dark", "Mysterious"

#### 8. **Looperman (Music Loops)** ⭐⭐⭐⭐
- **URL:** https://looperman.com/
- **Best For:** Music loops for custom compositions
- **License:** Varies (check each loop)
- **Quality:** Varies
- **Use Case:** Create custom BGM by combining loops

#### 9. **RPG Maker Forums** ⭐⭐⭐
- **URL:** https://forums.rpgmakerweb.com/index.php?forums/resources.15/
- **Best For:** Character sprites, tilesets (RPG Maker format compatible)
- **License:** Varies (often free for commercial use)
- **Quality:** High

#### 10. **CC Mixter (Music)** ⭐⭐⭐
- **URL:** https://ccmixter.org/
- **Best For:** Royalty-free music with Creative Commons licenses
- **License Types:** CC-BY, CC-BY-NC
- **Quality:** High

---

## Search Terms by Category

### Characters

**General Searches:**
```
- "JRPG character sprite sheet"
- "RPG character 32x32"
- "top-down character sprite"
- "pixel art character walk cycle"
- "fantasy hero sprite"
- "character sprite 4-direction"
```

**Specific Character Types:**
```
- "warrior character sprite"
- "mage character sprite"
- "rogue assassin sprite"
- "cleric healer sprite"
- "knight armor sprite"
- "NPC merchant sprite"
- "villager sprite pack"
```

**Art Style Variants:**
```
- "16x16 character chibi"
- "32x32 character detailed"
- "48x48 character large"
- "LPC character base"
```

### Enemies

**General Searches:**
```
- "RPG enemy sprite"
- "fantasy monster sprite"
- "battle enemy sprite"
- "pixel art creature"
- "top-down enemy"
```

**Enemy Categories:**
```
Slimes/Blobs:
- "slime enemy sprite"
- "blob monster"

Undead:
- "skeleton warrior sprite"
- "zombie sprite"
- "ghost enemy"

Beasts:
- "wolf sprite battle"
- "bear enemy sprite"
- "rat monster sprite"

Fantasy Creatures:
- "goblin sprite"
- "orc warrior sprite"
- "troll enemy"
- "dragon sprite"

Elemental:
- "fire elemental sprite"
- "ice golem sprite"
- "lightning spirit"
```

**Boss Enemies:**
```
- "boss sprite large"
- "dragon boss battle"
- "demon lord sprite"
- "final boss RPG"
```

### Tilesets

**Terrain Types:**
```
Outdoor:
- "grass tileset 32x32"
- "forest tileset RPG"
- "mountain tileset"
- "desert tileset"
- "snow tileset"

Indoor:
- "dungeon tileset stone"
- "castle interior tileset"
- "house interior RPG"
- "cave tileset dark"

Special:
- "autotile grass"
- "water autotile animated"
- "lava tileset"
- "ice floor tileset"
```

**Complete Packs:**
```
- "RPG tileset complete"
- "fantasy tileset pack"
- "top-down tileset bundle"
- "16x16 tileset overworld"
```

### Icons

**Item Icons:**
```
Weapons:
- "sword icon pixel"
- "axe icon 32x32"
- "bow arrow icon"
- "staff magic icon"

Armor:
- "helmet icon"
- "shield icon pixel"
- "armor chest icon"
- "boots icon"

Consumables:
- "potion icon red"
- "health potion"
- "mana potion blue"
- "elixir icon"

Key Items:
- "key icon golden"
- "crystal icon magic"
- "scroll icon"
- "gem icon"
```

**Skill Icons:**
```
- "fireball icon"
- "lightning spell icon"
- "heal spell icon"
- "sword slash icon"
- "shield defend icon"
```

**Status Icons:**
```
- "poison status icon"
- "stun icon"
- "buff icon"
- "debuff icon"
- "sleep status"
```

### Animations

**Attack Effects:**
```
- "slash effect sprite sheet"
- "sword swing animation"
- "impact effect"
- "hit effect particle"
```

**Magic Effects:**
```
- "fire spell animation"
- "ice spell effect"
- "lightning bolt animation"
- "heal sparkle effect"
- "explosion animation"
```

**Environmental:**
```
- "smoke effect animation"
- "dust cloud"
- "water splash"
- "sparkle effect"
```

### Music

**By Scene Type:**
```
Town/Village:
- "peaceful town theme"
- "village music RPG"
- "market music medieval"

Battle:
- "battle music RPG"
- "combat theme fantasy"
- "fight music 8bit"

Boss Battle:
- "boss battle theme"
- "epic battle music"
- "final boss theme"

Dungeon:
- "dungeon music dark"
- "cave ambient music"
- "mysterious dungeon theme"

World Map:
- "overworld theme"
- "adventure music"
- "journey theme"

Victory:
- "victory fanfare"
- "battle won theme"

Sad/Emotional:
- "sad piano RPG"
- "emotional theme"
```

**By Tempo/Mood:**
```
- "fast tempo battle music"
- "slow ambient peaceful"
- "mysterious eerie music"
- "uplifting heroic theme"
- "tense suspense music"
```

### Sound Effects

**UI Sounds:**
```
- "menu select sound"
- "button click"
- "menu cancel"
- "cursor move"
- "confirm beep"
- "error sound"
```

**Combat Sounds:**
```
- "sword slash"
- "sword hit metal"
- "punch impact"
- "arrow shot"
- "shield block"
- "critical hit sound"
```

**Magic Sounds:**
```
- "fire spell cast"
- "ice spell sound"
- "lightning zap"
- "heal spell chime"
- "buff spell sound"
```

**Environment:**
```
- "door open wooden"
- "chest open"
- "footstep stone"
- "footstep grass"
- "water splash"
- "wind ambient"
```

**Feedback:**
```
- "level up jingle"
- "item get"
- "coin pickup"
- "damage taken"
- "game over"
```

---

## Licensing & Legal Compliance

### Understanding Creative Commons Licenses

#### CC0 (Public Domain) ⭐⭐⭐⭐⭐
- **Permissions:** Use for any purpose, modify freely, no attribution required
- **Commercial Use:** ✅ Yes
- **Attribution:** Not required (but appreciated)
- **Best For:** Maximum flexibility
- **Examples:** Kenney.nl, many OpenGameArt assets

#### CC-BY 4.0 (Attribution) ⭐⭐⭐⭐
- **Permissions:** Use for any purpose, modify freely
- **Commercial Use:** ✅ Yes
- **Attribution:** ⚠️ Required
- **Best For:** Professional quality assets with simple attribution
- **Examples:** Game-icons.net, Incompetech music

**How to Attribute CC-BY:**
```
Asset Name by Artist Name (URL)
License: CC-BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
```

#### CC-BY-SA 4.0 (Attribution-ShareAlike) ⭐⭐⭐
- **Permissions:** Use for any purpose, modify freely
- **Commercial Use:** ✅ Yes
- **Attribution:** ⚠️ Required
- **Share-Alike:** ⚠️ Derivatives must use same license
- **Best For:** Open-source projects
- **Warning:** Can complicate commercial projects

#### CC-BY-NC (Non-Commercial) ❌
- **Commercial Use:** ❌ **NOT ALLOWED**
- **Avoid:** Unless making a free, non-commercial game
- **Risk:** Cannot monetize your game

#### OGA-BY 3.0 (OpenGameArt Attribution) ⭐⭐⭐⭐
- **Permissions:** Similar to CC-BY
- **Commercial Use:** ✅ Yes
- **Attribution:** ⚠️ Required
- **Platform:** Specific to OpenGameArt.org

### Licensing Checklist

Before adding any asset to your project:

- [ ] **License is documented** - Record in asset_manifest.json
- [ ] **Commercial use allowed** - Verify license permits commercial projects
- [ ] **Attribution requirements clear** - Note if credit is required
- [ ] **Source URL saved** - Keep link to original asset
- [ ] **Author name recorded** - Save creator's name
- [ ] **License file included** - Copy license text if required
- [ ] **CREDITS.txt updated** - Add attribution entry
- [ ] **No NC (Non-Commercial) clause** - Avoid CC-BY-NC unless non-commercial

### Creating CREDITS.txt

**Template:**
```
# Asset Credits for [Your Game Name]

## Visual Assets

### Characters
- Hero Sprite by Artist Name
  Source: https://opengameart.org/content/hero-sprite
  License: CC-BY 4.0

- Enemy Slime by Another Artist
  Source: https://kenney.nl/assets/rpg-pack
  License: CC0 (Public Domain)

### Tilesets
- Dungeon Tileset by Tileset Artist
  Source: https://opengameart.org/content/dungeon-tiles
  License: CC-BY 3.0

## Audio Assets

### Music
- "Battle Theme" by Composer Name
  Source: https://incompetech.com/music/
  License: CC-BY 4.0

### Sound Effects
- Sword Slash by SFX Artist
  Source: https://freesound.org/people/artist/sounds/12345/
  License: CC0

## Icon Packs
- Game Icons by game-icons.net contributors
  Source: https://game-icons.net/
  License: CC-BY 3.0
  Artists: Delapouite, Lorc, Skoll, others

## Fonts
- Font Name by Font Designer
  Source: https://fonts.google.com/
  License: OFL (Open Font License)

---

For complete license texts, see the LICENSE_ASSETS.txt file.
```

### License File Structure

```
assets/
├── CREDITS.txt           # Human-readable attribution
├── LICENSE_ASSETS.txt    # Full license texts
└── asset_manifest.json   # Machine-readable metadata
```

---

## Quality Standards

### Visual Assets

#### Resolution & Size

**Minimum Acceptable:**
- Characters: 32x32 pixels per frame
- Enemies: 48x48 pixels minimum
- Tilesets: 16x16 or 32x32 per tile
- Icons: 32x32 pixels
- UI Elements: Appropriate for 1280x720 display

**Recommended:**
- Characters: 48x48 or 64x64 for detailed sprites
- Boss Enemies: 128x128 or larger
- Icons: 64x64 for sharp display
- Backgrounds: 1280x720 or higher

#### Art Style Consistency

✅ **Good Practices:**
- Choose ONE primary art style and stick to it
- Match pixel art resolution (16x16 vs 32x32 vs 48x48)
- Use consistent color palettes across assets
- Match shading styles (flat vs gradients)
- Maintain consistent line weights

❌ **Avoid:**
- Mixing low-res and high-res pixel art
- Combining realistic art with chibi style
- Inconsistent color palettes
- Mixing different pixel art styles

**Style Compatibility Guide:**

| Style | Compatible With | Not Compatible With |
|-------|----------------|---------------------|
| 16x16 Pixel Art | Other 16x16 assets | 32x32, 48x48 detailed |
| 32x32 Pixel Art | Other 32x32 assets | 16x16 simple, photo-realistic |
| LPC Style | Other LPC assets | Non-LPC pixel art |
| Kenney Style | Other Kenney packs | Highly detailed pixel art |

#### Technical Quality

✅ **Required:**
- Clean transparency (no white halos)
- Proper alpha channels
- No artifacts or compression
- Correct dimensions (power-of-2 preferred)
- Optimized file size

✅ **Sprite Sheets:**
- Consistent frame dimensions
- Organized grid layout
- No frame overlap
- Clear animation sequences

### Audio Assets

#### Music Quality

**Technical Requirements:**
- **Format:** OGG Vorbis (preferred) or MP3
- **Sample Rate:** 44.1kHz or 48kHz
- **Bitrate:** 128-192 kbps (OGG)
- **Channels:** Stereo
- **Length:** 1-3 minutes (loopable)

**Loop Quality:**
- ✅ Seamless loop points
- ✅ No clicks or pops at loop
- ✅ Musical phrase completion
- ❌ Abrupt cuts
- ❌ Volume fades (should loop seamlessly)

**Testing Loops:**
```bash
# Play music on repeat to test loop
pygame.mixer.music.load("bgm_town.ogg")
pygame.mixer.music.play(-1)  # -1 = infinite loop
```

#### Sound Effects Quality

**Technical Requirements:**
- **Format:** WAV (short clips) or OGG (longer)
- **Sample Rate:** 44.1kHz
- **Bitrate:** 16-bit (WAV), 96-128 kbps (OGG)
- **Channels:** Mono (SFX), Stereo (ambient)
- **Length:** 0.1-3 seconds (most SFX)

**Quality Checklist:**
- [ ] No background noise
- [ ] No clipping or distortion
- [ ] Normalized volume levels
- [ ] Clean start/end (no clicks)
- [ ] Appropriate length (not too long)

### Performance Considerations

**File Size Targets:**

| Asset Type | Target Size | Maximum Size |
|-----------|-------------|--------------|
| Character Sprite | < 50 KB | 200 KB |
| Enemy Sprite | < 100 KB | 500 KB |
| Tileset | < 200 KB | 1 MB |
| Background | < 500 KB | 2 MB |
| Icon | < 10 KB | 50 KB |
| SFX | < 100 KB | 500 KB |
| Music (OGG) | < 3 MB | 8 MB |

**Optimization Tips:**
- Use PNG compression (pngcrush, optipng)
- Use OGG instead of WAV for audio
- Combine small sprites into sprite sheets
- Use indexed color PNG when possible (8-bit)
- Remove unused frames from animations

---

## Format Requirements

### Image Formats

**Primary Format: PNG**

✅ **Use PNG for:**
- Character sprites (needs transparency)
- Enemy sprites (needs transparency)
- Animations (needs transparency)
- Icons (needs transparency)
- UI elements (needs transparency)
- Tilesets (may need transparency)

**Settings:**
- Color Depth: 32-bit (RGBA)
- Compression: Maximum
- Interlacing: None (for games)

**Secondary Format: JPG**

✅ **Use JPG for:**
- Large backgrounds (no transparency needed)
- Static scenes
- Title screens (if no transparency)

❌ **Don't use JPG for:**
- Sprites with transparency
- Small images (compression artifacts)
- Assets that will be scaled

**Format Comparison:**

| Format | Transparency | Best For | File Size |
|--------|--------------|----------|-----------|
| PNG-32 | ✅ Yes | Sprites, UI, icons | Medium |
| PNG-8 | ✅ Yes (1-bit) | Simple sprites | Small |
| JPG | ❌ No | Backgrounds, photos | Small |
| GIF | ⚠️ Limited | Simple animations | Small |
| BMP | ⚠️ Optional | ❌ Avoid (huge files) | Very Large |

### Audio Formats

**Music: OGG Vorbis (Recommended)**

✅ **Advantages:**
- Free, open format
- Better quality than MP3 at same bitrate
- Smaller file sizes
- Seamless looping support
- No licensing issues

**Settings:**
- Quality: 5-7 (VBR) or 128-192 kbps (CBR)
- Sample Rate: 44100 Hz
- Channels: Stereo

**Music: MP3 (Alternative)**

⚠️ **Use only if:**
- Source is already MP3
- OGG not supported by target platform

**Sound Effects: WAV vs OGG**

| Format | Best For | File Size | Quality |
|--------|----------|-----------|---------|
| WAV | Short SFX (< 1 sec) | Large | Perfect |
| OGG | Longer SFX (> 1 sec) | Small | Excellent |

**Recommendation:**
- UI sounds (clicks, beeps): WAV
- Impact sounds (hits, slashes): WAV
- Ambient sounds (wind, water): OGG
- Voice clips: OGG

### Sprite Sheet Layouts

**Standard Character Sprite Sheet:**

```
Layout: 4 rows × 3-12 columns
Row 1: Down/South facing
Row 2: Left/West facing
Row 3: Right/East facing
Row 4: Up/North facing

Frame dimensions: 32x32, 48x48, or 64x64
```

**Example Layout (4×3):**
```
[Down-Idle] [Down-Walk1] [Down-Walk2]
[Left-Idle] [Left-Walk1] [Left-Walk2]
[Right-Idle] [Right-Walk1] [Right-Walk2]
[Up-Idle] [Up-Walk1] [Up-Walk2]
```

**Animation Sprite Sheet:**

```
Layout: 1 row × N frames (horizontal strip)
Frame count: 4-16 frames typical
Frame duration: 60-120ms per frame

Example: Fire spell animation
[Frame1] [Frame2] [Frame3] [Frame4] [Frame5] [Frame6]
```

**Tileset Layout:**

```
Tiles arranged in grid
Tile size: 16×16, 32×32, or 48×48
Grid: 8-16 tiles per row
Total: 64-256 tiles per sheet
```

---

## Tagging Best Practices

### Tag Categories

**1. Type Tags** (What it is)
```
- character
- enemy
- boss
- tileset
- icon
- animation
- music
- sfx
- ui
- background
```

**2. Genre Tags** (Game genre/style)
```
- fantasy
- scifi
- medieval
- modern
- cyberpunk
- horror
- western
- eastern (Asian-inspired)
- steampunk
```

**3. Theme Tags** (Visual theme)
```
- pixel-art
- 16-bit
- 32-bit
- retro
- realistic
- cartoon
- chibi
- minimalist
```

**4. Usage Tags** (Where/how it's used)
```
- player
- npc
- protagonist
- antagonist
- battle
- overworld
- menu
- inventory
- dialogue
```

**5. Attribute Tags** (Characteristics)
```
For Characters:
- human, elf, dwarf, orc
- male, female, neutral
- warrior, mage, rogue, cleric
- armored, unarmored

For Enemies:
- undead, beast, elemental, demon
- flying, ground, aquatic
- small, medium, large, giant
- common, elite, boss

For Environment:
- indoor, outdoor
- grass, stone, wood, metal
- day, night
- town, dungeon, forest, cave
```

**6. Mood Tags** (For music/audio)
```
- peaceful
- intense
- mysterious
- heroic
- sad
- joyful
- tense
- relaxing
```

**7. Tempo Tags** (For music)
```
- slow
- medium
- fast
- variable
```

**8. Technical Tags**
```
- animated
- sprite-sheet
- looping
- seamless
- tileable
- transparent
```

### Tagging Examples

**Example 1: Hero Character**
```json
{
  "id": "hero_warrior_001",
  "tags": [
    "character",
    "player",
    "protagonist",
    "human",
    "male",
    "warrior",
    "armored",
    "fantasy",
    "pixel-art",
    "32x32",
    "sprite-sheet",
    "animated"
  ]
}
```

**Example 2: Slime Enemy**
```json
{
  "id": "enemy_slime_green",
  "tags": [
    "enemy",
    "monster",
    "slime",
    "common",
    "small",
    "ground",
    "fantasy",
    "pixel-art",
    "battle",
    "animated"
  ]
}
```

**Example 3: Town Music**
```json
{
  "id": "bgm_town_peaceful",
  "tags": [
    "music",
    "bgm",
    "town",
    "village",
    "peaceful",
    "relaxing",
    "fantasy",
    "looping",
    "medium-tempo"
  ]
}
```

**Example 4: Fire Spell Icon**
```json
{
  "id": "icon_spell_fireball",
  "tags": [
    "icon",
    "skill",
    "magic",
    "fire",
    "attack",
    "offensive",
    "fantasy",
    "32x32"
  ]
}
```

### Tag Naming Conventions

✅ **Good Practices:**
- Use lowercase only
- Use hyphens for multi-word tags (not underscores)
- Be specific but not overly granular
- Use common, searchable terms
- Include both general and specific tags

❌ **Avoid:**
- Capital letters (use `fantasy` not `Fantasy`)
- Spaces (use `pixel-art` not `pixel art`)
- Too generic (avoid just `asset` or `game`)
- Too specific (avoid `blue-armored-warrior-with-sword-32px`)
- Special characters beyond hyphens

### Searchable Tag Sets

**For maximum searchability, include tags from multiple categories:**

**Character Example:**
```
Type: character, sprite
Genre: fantasy, medieval
Theme: pixel-art, 32x32
Usage: player, protagonist
Attributes: human, male, warrior, armored
Technical: sprite-sheet, animated, 4-direction
```

**Music Example:**
```
Type: music, bgm
Genre: fantasy, medieval
Usage: town, village, overworld
Mood: peaceful, relaxing, calm
Tempo: slow, medium
Technical: looping, ogg
```

This ensures assets can be found via:
- Category searches (all fantasy assets)
- Type searches (all music)
- Mood searches (all peaceful music)
- Technical searches (all looping audio)

---

## Sample Manifest Entries

### Character Entry (Full Example)

```json
{
  "id": "hero_knight_001",
  "name": "Knight Hero Sprite",
  "file_path": "characters/hero_knight_spritesheet.png",
  "format": "png",
  "dimensions": {
    "width": 192,
    "height": 256
  },
  "sprite_sheet": {
    "enabled": true,
    "frame_width": 32,
    "frame_height": 32,
    "frames_per_row": 12,
    "total_frames": 48,
    "layout": "4-direction"
  },
  "animations": {
    "idle": "frames 0-2",
    "walk": "frames 3-8",
    "attack": "frames 9-11"
  },
  "tags": [
    "character",
    "player",
    "protagonist",
    "human",
    "male",
    "warrior",
    "knight",
    "armored",
    "fantasy",
    "medieval",
    "pixel-art",
    "32x32",
    "sprite-sheet",
    "animated",
    "4-direction"
  ],
  "genre": "fantasy",
  "theme": "medieval",
  "art_style": "pixel-art",
  "license": "CC-BY 4.0",
  "author": "Pixel Artist Name",
  "source_url": "https://opengameart.org/content/knight-sprite",
  "attribution_required": true,
  "notes": "Main hero character with full walk cycle and attack animations",
  "date_added": "2025-11-14"
}
```

### Enemy Entry

```json
{
  "id": "enemy_goblin_warrior",
  "name": "Goblin Warrior",
  "file_path": "enemies/goblin_warrior.png",
  "format": "png",
  "dimensions": {
    "width": 64,
    "height": 64
  },
  "sprite_sheet": {
    "enabled": false
  },
  "battle_sprite": true,
  "stats_reference": "goblin_warrior_stats",
  "tags": [
    "enemy",
    "monster",
    "goblin",
    "warrior",
    "common",
    "humanoid",
    "green",
    "medium",
    "ground",
    "fantasy",
    "battle"
  ],
  "genre": "fantasy",
  "enemy_type": "common",
  "encounter_zones": ["forest", "plains", "early-game"],
  "license": "CC0",
  "author": "Enemy Artist Name",
  "source_url": "https://opengameart.org/content/goblin-pack",
  "attribution_required": false,
  "notes": "Early-game common enemy",
  "date_added": "2025-11-14"
}
```

### Boss Entry

```json
{
  "id": "boss_dragon_fire",
  "name": "Fire Dragon Boss",
  "file_path": "enemies/boss_dragon_fire.png",
  "format": "png",
  "dimensions": {
    "width": 256,
    "height": 256
  },
  "sprite_sheet": {
    "enabled": true,
    "frame_width": 256,
    "frame_height": 256,
    "frames": 8
  },
  "battle_sprite": true,
  "animations": {
    "idle": "frames 0-3",
    "attack": "frames 4-7"
  },
  "tags": [
    "boss",
    "enemy",
    "dragon",
    "fire",
    "flying",
    "giant",
    "fantasy",
    "epic",
    "battle",
    "animated",
    "endgame"
  ],
  "genre": "fantasy",
  "enemy_type": "boss",
  "difficulty": "hard",
  "license": "CC-BY 4.0",
  "author": "Boss Artist Name",
  "source_url": "https://opengameart.org/content/dragon-boss",
  "attribution_required": true,
  "notes": "Late-game fire dragon boss with attack animations",
  "date_added": "2025-11-14"
}
```

### Tileset Entry

```json
{
  "id": "tileset_dungeon_stone",
  "name": "Stone Dungeon Tileset",
  "file_path": "tilesets/dungeon_stone_32x32.png",
  "format": "png",
  "tile_width": 32,
  "tile_height": 32,
  "tiles_per_row": 16,
  "total_tiles": 256,
  "autotile": true,
  "autotile_format": "RPG Maker",
  "terrain_type": "dungeon",
  "tags": [
    "tileset",
    "dungeon",
    "stone",
    "indoor",
    "dark",
    "fantasy",
    "32x32",
    "autotile",
    "seamless"
  ],
  "genre": "fantasy",
  "theme": "dark",
  "compatible_tilesets": ["tileset_dungeon_decorations"],
  "license": "CC-BY 3.0",
  "author": "Tileset Artist Name",
  "source_url": "https://opengameart.org/content/dungeon-tileset",
  "attribution_required": true,
  "notes": "Complete dungeon tileset with autotiling support",
  "date_added": "2025-11-14"
}
```

### Icon Entry

```json
{
  "id": "icon_item_health_potion",
  "name": "Health Potion Icon",
  "file_path": "icons/item_health_potion.png",
  "format": "png",
  "dimensions": {
    "width": 32,
    "height": 32
  },
  "icon_category": "item",
  "item_type": "consumable",
  "tags": [
    "icon",
    "item",
    "consumable",
    "potion",
    "health",
    "healing",
    "red",
    "fantasy",
    "32x32"
  ],
  "genre": "fantasy",
  "color_primary": "red",
  "license": "CC-BY 3.0",
  "author": "Lorc",
  "source_url": "https://game-icons.net/1x1/lorc/health-potion.html",
  "attribution_required": true,
  "attribution_text": "Health Potion icon by Lorc (game-icons.net) - CC-BY 3.0",
  "notes": "Standard red health potion icon",
  "date_added": "2025-11-14"
}
```

### Music Entry

```json
{
  "id": "bgm_town_peaceful_01",
  "name": "Peaceful Village Theme",
  "file_path": "music/town_peaceful.ogg",
  "format": "ogg",
  "duration": 120.5,
  "file_size_mb": 2.3,
  "loop": true,
  "loop_start": 5.2,
  "loop_end": 115.8,
  "sample_rate": 44100,
  "bitrate": 160,
  "bpm": 90,
  "mood": "peaceful",
  "tags": [
    "music",
    "bgm",
    "town",
    "village",
    "peaceful",
    "relaxing",
    "calm",
    "fantasy",
    "medieval",
    "daytime",
    "looping",
    "ogg"
  ],
  "genre": "fantasy",
  "scene_type": "town",
  "tempo": "medium",
  "instruments": ["flute", "strings", "harp"],
  "license": "CC-BY 4.0",
  "author": "Composer Name",
  "source_url": "https://incompetech.com/music/royalty-free/music.html",
  "attribution_required": true,
  "attribution_text": "\"Peaceful Village\" by Composer Name - CC-BY 4.0",
  "notes": "Seamless loop with intro section",
  "date_added": "2025-11-14"
}
```

### Sound Effect Entry

```json
{
  "id": "sfx_combat_sword_hit",
  "name": "Sword Hit Sound",
  "file_path": "sfx/combat_sword_hit.wav",
  "format": "wav",
  "duration": 0.3,
  "file_size_kb": 45,
  "sample_rate": 44100,
  "bit_depth": 16,
  "channels": "mono",
  "category": "combat",
  "tags": [
    "sfx",
    "combat",
    "sword",
    "hit",
    "impact",
    "metal",
    "attack",
    "battle",
    "weapon"
  ],
  "usage": "combat",
  "license": "CC0",
  "author": "SFX Artist Name",
  "source_url": "https://freesound.org/people/artist/sounds/12345/",
  "attribution_required": false,
  "notes": "Sharp metal impact for sword hits",
  "date_added": "2025-11-14"
}
```

### Animation Entry

```json
{
  "id": "anim_spell_fireball",
  "name": "Fireball Spell Animation",
  "file_path": "animations/spell_fireball.png",
  "format": "png",
  "frame_count": 8,
  "frame_width": 64,
  "frame_height": 64,
  "frame_rate": 12,
  "loop": false,
  "duration": 0.67,
  "dimensions": {
    "width": 512,
    "height": 64
  },
  "tags": [
    "animation",
    "effect",
    "spell",
    "magic",
    "fire",
    "fireball",
    "attack",
    "projectile",
    "fantasy",
    "sprite-sheet"
  ],
  "genre": "fantasy",
  "effect_type": "projectile",
  "element": "fire",
  "license": "CC-BY 4.0",
  "author": "VFX Artist Name",
  "source_url": "https://opengameart.org/content/fireball-animation",
  "attribution_required": true,
  "notes": "8-frame fireball projectile animation",
  "date_added": "2025-11-14"
}
```

### UI Element Entry

```json
{
  "id": "ui_window_dialogue",
  "name": "Dialogue Window",
  "file_path": "ui/window_dialogue.png",
  "format": "png",
  "dimensions": {
    "width": 800,
    "height": 200
  },
  "ui_type": "window",
  "nine_patch": {
    "enabled": true,
    "left": 16,
    "right": 16,
    "top": 16,
    "bottom": 16
  },
  "tags": [
    "ui",
    "window",
    "dialogue",
    "textbox",
    "panel",
    "fantasy",
    "nine-patch",
    "scalable"
  ],
  "genre": "fantasy",
  "theme": "medieval",
  "license": "CC0",
  "author": "UI Artist Name",
  "source_url": "https://opengameart.org/content/ui-pack",
  "attribution_required": false,
  "notes": "Scalable dialogue window using nine-patch",
  "date_added": "2025-11-14"
}
```

---

## Asset Collection Workflow

### Step-by-Step Process

#### Phase 1: Planning (Before Collecting)

**1. Define Your Game's Asset Needs**

Create a spreadsheet or document listing:
- [ ] Number of playable characters needed
- [ ] Number of enemy types needed
- [ ] Number of maps/areas (determines tileset count)
- [ ] Number of items (determines icon count)
- [ ] Number of skills/spells (determines animation count)
- [ ] Music track list by scene
- [ ] Sound effect categories needed

**2. Choose Your Art Style**

Decision points:
- Pixel art size: 16x16, 32x32, 48x48, or mixed?
- Color palette: Limited (retro) or full color?
- Style: Realistic, cartoon, chibi, minimal?
- Inspiration: Classic JRPG, modern indie, retro?

**3. Create Asset Checklist**

Template:
```
Characters:
[ ] Hero (4 expressions)
[ ] Warrior party member (4 expressions)
[ ] Mage party member (4 expressions)
[ ] Merchant NPC
[ ] Villager NPCs (5 variants)

Enemies:
[ ] Slime (3 color variants)
[ ] Goblin
[ ] Skeleton
[ ] Wolf
... (continue for all)

Music:
[ ] Title screen
[ ] Town theme
[ ] Battle theme
... (continue for all)
```

#### Phase 2: Asset Discovery

**1. Search Primary Sources**

Start with these in order:
1. **Kenney.nl** - Check for complete packs in your style
2. **OpenGameArt LPC** - If using LPC style
3. **OpenGameArt** - General search
4. **Itch.io** - Complete asset bundles
5. **Game-icons.net** - All icons

**2. Document Finds**

Create a tracking sheet:
```
Asset Name | Source URL | License | Attribution Needed | Downloaded | Added to Manifest
---------- | ---------- | ------- | ------------------ | ---------- | -----------------
Hero Sprite | URL | CC-BY 4.0 | Yes | ✓ | ✓
Slime Enemy | URL | CC0 | No | ✓ | ✓
```

**3. Download and Organize**

```bash
# Create download staging area
mkdir asset_downloads/
cd asset_downloads/

# Organize by category as you download
mkdir characters enemies tilesets icons music sfx animations ui

# Keep original URLs in a text file per asset
echo "https://opengameart.org/content/hero" > characters/hero_sprite_source.txt
```

#### Phase 3: Quality Control

**For Each Downloaded Asset:**

1. **Visual Inspection**
   - [ ] Check image quality (no artifacts)
   - [ ] Verify transparency (no white halos)
   - [ ] Confirm dimensions
   - [ ] Test if sprite sheet frames align correctly

2. **Technical Validation**
   - [ ] Verify file format (PNG for sprites, OGG for music)
   - [ ] Check file size (reasonable for type)
   - [ ] Test loading in engine
   - [ ] Verify color depth (32-bit RGBA for sprites)

3. **License Verification**
   - [ ] Read license file included with download
   - [ ] Verify commercial use is allowed
   - [ ] Note attribution requirements
   - [ ] Save license text

4. **Style Consistency Check**
   - [ ] Matches chosen art style
   - [ ] Compatible with existing assets
   - [ ] Color palette fits
   - [ ] Size/scale appropriate

#### Phase 4: Integration

**1. File Organization**

```bash
# Move validated assets to project
cp asset_downloads/characters/hero.png neonworks/assets/characters/
cp asset_downloads/enemies/slime.png neonworks/assets/enemies/

# Follow naming conventions
mv hero.png hero_knight_001.png
mv slime.png enemy_slime_green.png
```

**2. Create Manifest Entry**

For each asset, add to `assets/asset_manifest.json`:

```json
{
  "id": "unique_id_here",
  "name": "Display Name",
  "file_path": "category/filename.png",
  "format": "png",
  // ... (see sample entries above)
  "tags": ["tag1", "tag2", "tag3"],
  "license": "CC-BY 4.0",
  "author": "Artist Name",
  "source_url": "https://...",
  "attribution_required": true
}
```

**3. Test Loading**

```python
from neonworks.rendering.assets import get_asset_manager

assets = get_asset_manager()
sprite = assets.get_character("hero_knight_001")
assert sprite is not None
```

**4. Update Credits**

Add to `assets/CREDITS.txt`:
```
- Hero Knight Sprite by Artist Name
  Source: https://opengameart.org/content/...
  License: CC-BY 4.0
```

#### Phase 5: Verification

**Final Checklist:**

- [ ] All required assets collected
- [ ] All assets load without errors
- [ ] All assets have manifest entries
- [ ] All assets properly tagged
- [ ] All attribution added to CREDITS.txt
- [ ] License compliance verified
- [ ] Style consistency maintained
- [ ] File sizes optimized

### Quick Collection Tips

**Time-Saving Strategies:**

1. **Use Complete Packs**
   - One cohesive pack > many individual assets
   - Kenney packs are perfect for this
   - LPC collection provides massive character variety

2. **Recolor Variants**
   - Download one slime, recolor for variants (red, blue, green)
   - Use GIMP or Photoshop for batch recoloring
   - Creates variety with minimal downloads

3. **Batch Attribution**
   - When using multiple assets from same source, batch credit
   - "10 character sprites by Artist Name (URL) - CC-BY 4.0"

4. **Placeholder First, Replace Later**
   - Use test assets initially
   - Mark in manifest with "TODO: Replace with final asset"
   - Replace once you find better alternatives

5. **Community Collaboration**
   - Check if other NeonWorks users have asset collections
   - Share vetted asset lists
   - Collaborate on quality control

---

## Troubleshooting & FAQs

### Common Issues

#### Issue: Asset Doesn't Load

**Symptoms:**
- Placeholder sprite appears instead of asset
- Error message: "Failed to load asset"

**Solutions:**
1. Check file path in manifest matches actual file location
2. Verify file exists at specified path
3. Check file permissions (readable)
4. Verify file format is correct (PNG not JPG for sprites)
5. Test file opens in image viewer
6. Check for corrupted download (re-download)

#### Issue: Transparent Background Shows White Halo

**Symptoms:**
- White edges around sprite on colored background

**Solutions:**
1. Open in image editor (GIMP, Photoshop)
2. Check alpha channel exists
3. Remove color from transparent pixels
4. Re-export as 32-bit PNG
5. Use "Matting > Remove White Matte" in Photoshop

**GIMP Fix:**
```
1. Layer > Transparency > Add Alpha Channel
2. Select > By Color > Click white edges
3. Edit > Clear
4. File > Export As > PNG (make sure "Save color from transparent pixels" is unchecked)
```

#### Issue: Music Doesn't Loop Seamlessly

**Symptoms:**
- Click or pop at loop point
- Awkward musical pause

**Solutions:**
1. Use audio editor (Audacity) to find loop points
2. Align loop to musical phrase boundaries
3. Add crossfade at loop point (10-50ms)
4. Export with exact sample precision
5. Test in-game with `pygame.mixer.music.play(-1)`

**Audacity Loop Setup:**
```
1. File > Open music file
2. Play and find good loop start (after intro)
3. Place cursor at loop start
4. Edit > Select > Cursor to Track End
5. Generate > Silence (0.1 seconds) - fills gaps
6. Effect > Crossfade Tracks
7. File > Export > OGG Vorbis
```

#### Issue: Sprite Sheet Frames Don't Align

**Symptoms:**
- Frames cut off parts of sprite
- Animation looks glitchy

**Solutions:**
1. Verify sprite sheet dimensions:
   - Width = frame_width × columns
   - Height = frame_height × rows
2. Check if extra padding exists
3. Crop sprite sheet to exact grid
4. Update manifest with correct frame dimensions

**Validation Formula:**
```python
width = frame_width * columns
height = frame_height * rows

# Example: 4 directions × 3 frames = 12 frames
# 32x32 frames arranged 3 columns × 4 rows:
width = 32 * 3 = 96 pixels
height = 32 * 4 = 128 pixels
```

#### Issue: Assets Look Blurry When Scaled

**Symptoms:**
- Fuzzy, blurred pixel art

**Solutions:**
1. Disable texture filtering in pygame
2. Scale by integer multiples (2x, 3x, 4x)
3. Use nearest-neighbor scaling

**Pygame Fix:**
```python
# Use transform.scale with integer multiples
sprite = pygame.transform.scale(
    original_sprite,
    (original_width * 2, original_height * 2)
)

# Or use scale2x for pixel art
sprite = pygame.transform.scale2x(original_sprite)
```

#### Issue: Too Many Assets, Can't Find What I Need

**Solutions:**
1. Use comprehensive tagging (see Tagging Best Practices)
2. Use asset manager search functions:
   ```python
   assets.search_assets("goblin")
   assets.find_assets_by_tag("enemy")
   assets.filter_assets(category="characters", tags=["player"])
   ```
3. Organize manifest with comments
4. Use consistent naming conventions

### FAQs

**Q: Can I mix CC-BY and CC0 assets?**

A: Yes! You can use multiple licenses in one project. Just make sure to:
- Track each asset's license in manifest
- Provide attribution for CC-BY assets
- Include all required license texts

**Q: How many characters do I really need?**

A: Minimum viable:
- 4 playable characters (party)
- 5-10 NPCs (recurring characters)
- 5-10 generic NPCs (villagers, merchants)

Recommended:
- 8-12 playable characters
- 20-30 unique NPCs
- 10-15 generic NPC variants

**Q: What if I can't find an asset I need?**

A: Options:
1. Commission an artist (paid)
2. Learn to create it yourself (pixel art is learnable)
3. Use placeholder and find later
4. Modify existing asset (if license allows)
5. Ask community for recommendations

**Q: Can I modify assets I download?**

A: Depends on license:
- ✅ CC0: Yes, any modifications allowed
- ✅ CC-BY: Yes, but must credit original author
- ✅ CC-BY-SA: Yes, but modified version must use same license
- ❌ No-Derivatives licenses: No modifications allowed (avoid these)

**Q: Do I need to credit CC0 assets?**

A: No, but it's polite and recommended:
- Not legally required
- Good practice for community
- Shows appreciation to artists
- Helps others find the assets

**Q: How do I handle font licenses?**

A: Fonts have separate licensing:
- Use OFL (Open Font License) fonts - safest
- Google Fonts are mostly OFL
- Check license file in font package
- Add fonts to CREDITS.txt if required

**Q: What's the best resolution for pixel art?**

A: Depends on style:
- **16x16:** Retro, Game Boy style, simple
- **32x32:** Classic JRPG, most versatile
- **48x48:** Detailed, modern indie
- **64x64:** Very detailed, less retro

Recommendation: **32x32** for balanced detail and retro feel

**Q: How do I know if audio will loop well?**

A: Before downloading:
1. Check description for "seamless loop" or "loopable"
2. Listen to preview (does it have clear intro?)
3. Check comments for loop quality feedback

After downloading:
1. Open in Audacity
2. Set loop region
3. Play repeatedly
4. Listen for clicks/pops

**Q: Can I use YouTube music in my game?**

A: ⚠️ **Generally NO**:
- Most YouTube music is copyrighted
- "No copyright music" often means YouTube won't flag it, not that it's free to use
- Check video description for actual license
- Look for explicit "CC" or "free to use commercially" statement

**Q: What's the difference between 8-bit and 16-bit music?**

A:
- **8-bit:** NES-era, limited channels (triangle, square, noise)
- **16-bit:** SNES-era, better sound quality, more instruments

For JRPG: **16-bit** or modern chiptune is recommended

**Q: How much should I budget for assets if buying?**

A: Rough estimates:
- **Asset packs:** $10-50 per complete pack
- **Single sprites:** $5-20 each (commissioned)
- **Music tracks:** $50-200 per track (commissioned)
- **Complete game soundtrack:** $500-2000

Free assets are sufficient for complete games!

**Q: My game has 1000+ assets. Is the manifest too big?**

A: The manifest can handle thousands of entries:
- JSON parsing is fast (< 100ms for 1000 entries)
- Lazy loading means only used assets load
- Consider splitting into multiple manifests if > 5000 assets

**Q: Can I sell a game made entirely with free assets?**

A: **Yes**, if licenses allow commercial use:
- ✅ CC0: Fully commercial, no restrictions
- ✅ CC-BY: Commercial with attribution
- ❌ CC-BY-NC: Non-commercial only (avoid!)

Check every asset's license!

**Q: Where can I preview assets before downloading?**

A:
- OpenGameArt: Thumbnail and full preview
- Kenney.nl: Preview images on each pack page
- Itch.io: Screenshots and previews
- Game-icons.net: Live preview with color customization

**Q: How do I organize 100+ music tracks?**

A: Naming convention:
```
bgm_[scene]_[mood]_[number].ogg

Examples:
bgm_town_peaceful_01.ogg
bgm_battle_intense_01.ogg
bgm_dungeon_dark_01.ogg
bgm_boss_epic_01.ogg
```

Tags:
```json
{
  "tags": [
    "music",
    "bgm",
    "town",         // scene
    "peaceful",     // mood
    "looping",      // technical
    "fantasy"       // genre
  ]
}
```

---

## Additional Resources

### Asset Tools

**Image Editors:**
- GIMP (free): https://www.gimp.org/
- Aseprite (paid, $20): https://www.aseprite.org/
- Krita (free): https://krita.org/
- Photopea (free, browser): https://www.photopea.com/

**Audio Editors:**
- Audacity (free): https://www.audacityteam.org/
- Ocenaudio (free): https://www.ocenaudio.com/
- Bosca Ceoil (free, music maker): https://boscaceoil.net/

**Asset Management:**
- TexturePacker: https://www.codeandweb.com/texturepacker
- Shoebox (free): https://renderhjs.net/shoebox/

### Learning Resources

**Pixel Art Tutorials:**
- Pixel Logic (free tutorials): https://www.youtube.com/c/PixelLogicArt
- Lospec (pixel art community): https://lospec.com/
- Pedro Medeiros tutorials: https://blog.studiominiboss.com/pixelart

**Music Production:**
- Beepbox (free browser music maker): https://www.beepbox.co/
- FamiStudio (free NES-style tracker): https://famistudio.org/

**License Guides:**
- Creative Commons: https://creativecommons.org/licenses/
- OGA License Guide: https://opengameart.org/content/faq#q-proprietary

### Community

**Forums & Communities:**
- OpenGameArt Forums: https://opengameart.org/forums
- r/gameassets: https://www.reddit.com/r/gameassets/
- NeonWorks Discord: [Your Discord Link]

**Asset Curators:**
- Awesome Pixel Art: https://github.com/Siilwyn/awesome-pixel-art
- Awesome Game Music: https://github.com/ad-si/awesome-music
- Free Game Assets List: https://github.com/sparklinlabs/superpowers-asset-packs

---

## Conclusion

Collecting assets is a **significant but manageable task** for your JRPG project. By following this guide:

✅ You know **where to find** quality, legally-usable assets
✅ You understand **licensing** and attribution requirements
✅ You can **organize and tag** assets for easy searching
✅ You have **sample manifest entries** to follow
✅ You know **quality standards** to maintain consistency
✅ You have a **workflow** to efficiently collect hundreds of assets

### Next Steps

1. **Define your asset needs** - Create checklist from Required Quantities
2. **Choose your art style** - Decide on pixel art size and aesthetic
3. **Start with Kenney.nl** - Download a complete pack to get started
4. **Fill gaps with OpenGameArt** - Find specialized assets
5. **Add icons from game-icons.net** - Cover all UI needs
6. **Find music on Incompetech** - Get looping BGM tracks
7. **Document everything** - Update manifest and CREDITS.txt as you go

### Remember

- **Quality over quantity** - 50 great assets > 200 mediocre ones
- **Consistency matters** - Matching art style is more important than variety
- **License compliance** - Always check, always credit when required
- **Start small** - MVP first, expand later
- **Community helps** - Ask for asset recommendations

**Happy collecting!** 🎮🎨🎵

---

**Questions or Issues?**

- Check [Troubleshooting](#troubleshooting--faqs) section
- Refer to `assets/ASSET_GUIDELINES.md` for technical specs
- See `rendering/assets.py` for asset manager documentation
- Join NeonWorks community for asset recommendations

**Document Version:** 1.0
**Last Updated:** 2025-11-14
**Maintained By:** NeonWorks Team
