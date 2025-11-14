# Character Generator Asset Directory

This directory contains all assets for the NeonWorks Character Generator Component System.

## Version

**Version:** 1.0.0
**Created:** 2025-11-14
**Schema:** `engine/data/character_parts.json`

## Directory Structure

```
character_generator/
├── README.md                   # This file
├── bodies/                     # Base body sprites
├── hair/                       # Hair styles (front and back layers)
├── clothing/                   # Clothing and armor
├── accessories/                # Accessories organized by attachment point
│   ├── head/                  # Helmets, hats, crowns, glasses
│   ├── neck/                  # Necklaces, scarves, amulets
│   └── back/                  # Capes, wings, backpacks
├── weapons/                    # Weapons and held items
├── faces/                      # Facial features and expressions
├── effects/                    # Visual effects (auras, glows, particles)
└── masks/                      # Color customization masks
    ├── bodies/                # Skin tone masks
    ├── hair/                  # Hair color masks
    ├── clothing/              # Clothing color masks
    ├── accessories/           # Accessory color masks
    ├── weapons/               # Weapon color masks
    └── faces/                 # Face color masks
```

## Asset Specifications

### Image Format
- **Format:** PNG with transparency (RGBA)
- **Color Depth:** 32-bit
- **Compression:** Standard PNG compression

### Sprite Dimensions
- **Standard Character:** 32x64 pixels (tile_size x 2)
- **Face Sprites:** 24x24 pixels
- **Hair (varies):** 32x32 to 40x48 pixels
- **Weapons (varies):** Based on weapon type

### Naming Conventions

#### Base Sprites
```
{component_id}.png
```
Examples:
- `knight_body_male.png`
- `warrior_hair_short.png`
- `leather_tunic.png`

#### Animated Sprites
```
{component_id}_{animation}_{frame_number}.png
```
Examples:
- `knight_body_male_walk_01.png`
- `knight_body_male_walk_02.png`
- `iron_sword_attack_01.png`

#### Color Masks
```
{component_id}_{color_zone}_mask.png
```
Examples:
- `knight_body_male_skin_mask.png`
- `leather_tunic_primary_mask.png`
- `wizard_robe_secondary_mask.png`

#### Multi-Layer Components
```
{component_id}_front.png
{component_id}_back.png
```
Examples:
- `long_flowing_hair_front.png`
- `long_flowing_hair_back.png`

## Layer System

Components render in a specific order (z-order) to create proper visual stacking:

| Z-Order | Layer ID | Description |
|---------|----------|-------------|
| 0 | base_body | Foundation body shape |
| 10 | body_markings | Tattoos, scars |
| 20 | underwear | Base undergarments |
| 30 | clothing_base | Primary clothing |
| 40 | clothing_accessories | Belts, pouches |
| 50 | armor | Protective gear |
| 60 | back_accessory | Capes, wings (behind) |
| 70 | hair_back | Hair behind head |
| 80 | face_base | Facial features base |
| 90 | eyes | Eye sprites |
| 100 | facial_features | Nose, mouth, eyebrows |
| 110 | facial_hair | Beards, mustaches |
| 120 | hair_front | Hair in front |
| 130 | head_accessory | Hats, helmets |
| 140 | neck_accessory | Necklaces, scarves |
| 150 | hand_accessory_left | Left hand items |
| 160 | hand_accessory_right | Right hand items |
| 170 | effects | Visual effects |

## Color Customization System

### Color Zones

Components can have multiple customizable color zones:

- **primary:** Main color of the item
- **secondary:** Accent/trim color
- **tertiary:** Additional accent color
- **metal:** Metal parts (armor, weapons)
- **skin:** Skin tone
- **hair:** Hair color

### Color Masks

Color masks are grayscale PNG files that define which pixels can be recolored:

- **White (255):** Full color replacement
- **Gray (128):** Partial color blending
- **Black (0):** No color change (preserve original)

### Creating Color Masks

1. Duplicate the original sprite
2. Convert to grayscale
3. Paint areas to be recolored in white
4. Save as `{component_id}_{color_zone}_mask.png`

## Anchor Points

Anchor points define where components attach to the body:

- **head:** Top of character (x: 16, y: 8)
- **torso:** Center of body (x: 16, y: 24)
- **left_hand:** Left hand position (x: 8, y: 32)
- **right_hand:** Right hand position (x: 24, y: 32)
- **feet:** Bottom of character (x: 16, y: 60)

Offsets can be specified to fine-tune positioning.

## Animation Support

### Standard Animations

- `idle` - Standing animation
- `walk` - Walking cycle
- `run` - Running cycle
- `attack` - Attack animation
- `cast_spell` - Spellcasting animation
- `hurt` - Damage reaction
- `death` - Death animation
- `jump` - Jumping animation

### Animation Frame Requirements

- **Idle:** 4 frames (looping)
- **Walk:** 4-6 frames (looping)
- **Run:** 4-6 frames (looping)
- **Attack:** 3-5 frames (non-looping)
- **Cast Spell:** 4-6 frames (non-looping)
- **Hurt:** 1-2 frames (non-looping)
- **Death:** 4-6 frames (non-looping)

## Adding New Components

### Step 1: Create the Sprite
1. Design sprite following size guidelines
2. Save as PNG with transparency
3. Use consistent naming convention

### Step 2: Create Color Masks (if applicable)
1. Create grayscale mask for each color zone
2. Save with `_mask.png` suffix

### Step 3: Add to Schema
1. Open `engine/data/character_parts.json`
2. Add component definition to appropriate category
3. Specify all required properties:
   - id, name, description
   - layer and z_order
   - asset_path
   - size and anchor points
   - color zones and masks
   - tags and compatibility

### Step 4: Test
1. Load in character generator
2. Verify layering is correct
3. Test color customization
4. Check animations (if applicable)

## Asset Guidelines

### Art Style Consistency
- Maintain consistent pixel art style across all components
- Use similar line weights and shading techniques
- Ensure color palettes are compatible

### Compatibility
- Tag components with appropriate gender/style tags
- Ensure accessories align with standard anchor points
- Test combinations with various body types

### Performance
- Keep file sizes reasonable (< 50KB per sprite)
- Use sprite sheets for animations when possible
- Optimize PNG compression

## Example Component Workflow

### Creating a New Helmet

1. **Design:** Create 32x24 pixel sprite of helmet
2. **Save Base:** `steel_helmet.png` in `accessories/head/`
3. **Create Masks:**
   - Metal parts: `steel_helmet_metal_mask.png`
   - Plume: `steel_helmet_plume_mask.png`
4. **Add to Schema:**
```json
"steel_helmet": {
  "id": "steel_helmet",
  "name": "Steel Helmet",
  "category": "accessories",
  "layer": "head_accessory",
  "z_order": 130,
  "asset_path": "assets/character_generator/accessories/steel_helmet.png",
  "color_zones": ["metal", "secondary"],
  "customizable_colors": {
    "metal": {
      "mask_path": "assets/character_generator/masks/accessories/steel_helmet_metal_mask.png",
      "default_color": "#C0C0C0"
    }
  },
  "tags": ["helmet", "armor", "warrior"]
}
```

## Troubleshooting

### Component Not Appearing
- Check z_order is within valid range (0-170)
- Verify asset_path is correct
- Ensure PNG has transparency

### Wrong Layering Order
- Adjust z_order value
- Check layer assignment matches intended category

### Color Customization Not Working
- Verify mask file exists at specified path
- Check mask is grayscale with white regions
- Ensure color_zones are properly defined

## Resources

- **Main Documentation:** `docs/CHARACTER_GENERATOR.md`
- **Schema File:** `engine/data/character_parts.json`
- **Code Reference:** Look for character generator implementation in `rendering/` or `ui/`

## Version History

- **1.0.0** (2025-11-14): Initial character generator system
  - 6 component categories defined
  - Layer system with 18 layers
  - Color customization with 6 zones
  - Sample components for bodies, hair, clothing, accessories, weapons, faces

---

**Maintained by:** NeonWorks Team
**License:** See project LICENSE file
