# Hair Styles

Hair components can have front and back layers for depth.

## Specifications

- **Size:** Varies (typically 32x32 to 40x48 pixels)
- **Layers:**
  - hair_back (z_order: 70) - Hair behind head
  - hair_front (z_order: 120) - Hair in front
- **Attachment:** head anchor point

## Multi-Layer Hair

For long or flowing hair:
1. Create `{hairstyle}_back.png` - renders behind head
2. Create `{hairstyle}_front.png` - renders in front

## Color Customization

- **hair:** Full hair color customization zone
- Support preset colors: black, brown, blonde, red, fantasy colors

## Style Categories

- **Short:** Cropped, pixie cuts, buzz cuts
- **Medium:** Shoulder-length, bob cuts
- **Long:** Flowing, ponytails, braids
- **Styled:** Spikes, mohawks, elaborate updos
- **Fantasy:** Magical effects, unusual colors

## Compatibility

Tag hair with compatible genders:
- male
- female
- unisex

## Naming Convention

```
{style_description}_{length}.png
```

Examples:
- `warrior_short.png`
- `flowing_long_front.png`
- `flowing_long_back.png`
- `spiky_medium.png`
