# Clothing & Armor

Clothing forms the primary outfit layer.

## Specifications

- **Size:** Varies based on coverage (typically 32x40 to 36x56 pixels)
- **Layer:** clothing_base (z_order: 30)
- **Attachment:** torso anchor point

## Types

### Light Clothing
- Tunics, shirts, robes
- Minimal coverage, flexible

### Medium Armor
- Leather armor, chain mail
- Moderate protection, some bulk

### Heavy Armor
- Plate armor, full suits
- Maximum protection, significant bulk

## Color Customization

Typically supports multiple zones:
- **primary:** Main fabric/material color
- **secondary:** Trim, accents, stitching
- **tertiary:** Additional details (for complex outfits)
- **metal:** Metal parts (buckles, clasps)

## Game Stats

Clothing can have associated stats:
- **defense:** Protection value
- **weight:** light/medium/heavy
- **magic_power:** For magical robes
- **movement_speed:** Speed modifier

## Animation Considerations

Ensure clothing sprites work with all character animations:
- idle, walk, run
- attack, cast_spell
- hurt, death

## Naming Convention

```
{material}_{type}.png
```

Examples:
- `leather_tunic.png`
- `wizard_robe.png`
- `plate_armor.png`
- `noble_dress.png`
