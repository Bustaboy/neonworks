# Color Customization Masks

Masks define which parts of sprites can be recolored.

## How Masks Work

Color masks are grayscale PNG files where pixel brightness determines recoloring:

- **White (255, 255, 255):** Full color replacement - 100% of the target color
- **Light Gray (192, 192, 192):** Mostly recolored - ~75% of target color
- **Medium Gray (128, 128, 128):** Partial blending - 50% original, 50% target
- **Dark Gray (64, 64, 64):** Slight tint - ~25% of target color
- **Black (0, 0, 0):** No change - preserves original pixel color

## Creating Masks

### Step-by-Step Process

1. **Duplicate Original Sprite**
   - Start with a copy of the component sprite

2. **Convert to Grayscale**
   - Use image editor to convert to grayscale mode

3. **Identify Color Zones**
   - Determine which areas should be recolorable

4. **Paint Mask Regions**
   - Use white for areas that should fully change color
   - Use gray values for areas that should partially change
   - Use black for areas that should stay original

5. **Save Mask**
   - Save as `{component_id}_{color_zone}_mask.png`
   - Must match original sprite dimensions exactly

### Example: Tunic Mask

For `leather_tunic.png`:

**Primary Mask** (`leather_tunic_primary_mask.png`):
- White: Main leather body
- Gray: Shaded areas (for subtle depth)
- Black: Stitching, highlights (preserve detail)

**Secondary Mask** (`leather_tunic_secondary_mask.png`):
- White: Trim, belt, decorative elements
- Black: Everything else

## Mask Directory Structure

```
masks/
├── bodies/          # Skin tone masks for bodies
├── hair/            # Hair color masks
├── clothing/        # Clothing color masks
├── accessories/     # Accessory color masks
├── weapons/         # Weapon color masks
└── faces/           # Face color masks
```

## Naming Convention

```
{component_id}_{color_zone}_mask.png
```

Examples:
- `knight_body_male_skin_mask.png`
- `warrior_hair_short_hair_mask.png`
- `leather_tunic_primary_mask.png`
- `leather_tunic_secondary_mask.png`
- `steel_helmet_metal_mask.png`

## Technical Requirements

- **Format:** PNG (8-bit grayscale or 32-bit RGBA)
- **Dimensions:** Must exactly match source sprite
- **Pixel Alignment:** Masks must align perfectly with source

## Testing Masks

1. Load component in character generator
2. Change color for the zone
3. Verify only intended areas change color
4. Check that details/highlights are preserved
5. Test with extreme colors (bright red, dark blue) to verify mask coverage

## Common Color Zones

### skin
Used for body parts, faces
- Full coverage of skin areas
- Preserve highlights and shadows with gray values

### hair
Used for hair and facial hair
- Full coverage of hair strands
- May use gray for depth in thick hair

### primary
Main color of clothing/items
- Largest color area
- Base material color

### secondary
Accent color for trim/details
- Smaller decorative areas
- Borders, stitching, patterns

### tertiary
Additional accent color
- Optional third color
- Special details, runes, gems

### metal
Metal parts of items
- Armor plates, weapon blades
- Often uses gray values to preserve metallic shine

## Tips for Good Masks

1. **Preserve Detail:** Use gray values to maintain shading
2. **Clean Edges:** Ensure mask edges match sprite edges
3. **Test Extensively:** Try many different colors
4. **Consider Context:** Think about what makes sense to recolor
5. **Keep Highlights:** Often black-out brightest highlights to preserve shine

## Troubleshooting

### Colors Look Flat
- Use more gray values in mask to preserve shading
- Don't use pure white everywhere

### Wrong Areas Changing Color
- Check mask has black in areas that shouldn't change
- Verify mask dimensions match sprite exactly

### Colors Too Weak
- Increase brightness in mask (more white)
- Check that mask is being loaded correctly

### Artifacts at Edges
- Ensure mask edges are clean
- May need to manually clean up edge pixels
