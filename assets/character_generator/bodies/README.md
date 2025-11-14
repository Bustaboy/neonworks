# Body Sprites

Base body sprites form the foundation layer of characters.

## Specifications

- **Size:** 32x64 pixels (standard character size)
- **Layer:** base_body (z_order: 0)
- **Required:** Yes (every character needs a body)

## Anchor Points

All bodies should define these standard anchor points:
- **head:** (16, 8) - Where head accessories attach
- **torso:** (16, 24) - Where clothing attaches
- **left_hand:** (8, 32) - Left hand item position
- **right_hand:** (24, 32) - Right hand item position
- **feet:** (16, 60) - Ground position

## Color Customization

Bodies typically have one color zone:
- **skin:** Full body skin tone customization

## Variants

Create different body types for:
- Male/Female/Neutral
- Athletic/Slender/Muscular/Heavy
- Different age groups (child, adult, elderly)
- Fantasy races (elf, dwarf, orc, etc.)

## Naming Convention

```
{race}_{bodytype}_{gender}.png
```

Examples:
- `human_athletic_male.png`
- `elf_slender_female.png`
- `dwarf_stout_male.png`

## Assets Needed

This directory currently contains placeholder references. Add your body sprites here following the specifications above.
