# Accessories

Accessories add customization and personality to characters.

## Directory Structure

```
accessories/
├── head/     # Helmets, hats, crowns, glasses, masks
├── neck/     # Necklaces, scarves, amulets, collars
└── back/     # Capes, wings, backpacks, cloaks
```

## Head Accessories

- **Layer:** head_accessory (z_order: 130)
- **Size:** Typically 32x24 pixels
- **Types:** Helmets, hats, crowns, circlets, glasses, masks, ears

### Special Property: Hair Occlusion
```json
"occludes_hair": true
```
Set this for helmets that completely cover the hair.

## Neck Accessories

- **Layer:** neck_accessory (z_order: 140)
- **Size:** Typically 16x16 to 24x24 pixels
- **Types:** Necklaces, pendants, amulets, scarves, collars

## Back Accessories

- **Layer:** back_accessory (z_order: 60)
- **Size:** Varies (can be large for wings/capes)
- **Types:** Capes, cloaks, wings, backpacks, quivers

### Note on Rendering
Back accessories render BEHIND the character to create depth.

## Color Customization

Accessories often use these zones:
- **metal:** Chains, frames, metal parts
- **primary:** Main fabric/material
- **secondary:** Gems, decorations
- **tertiary:** Magical glows

## Special Effects

Some accessories can have visual effects:
```json
"has_glow_effect": true
```

## Naming Convention

```
{material}_{type}.png
```

Examples:
- `steel_helmet.png`
- `gold_crown.png`
- `magic_amulet.png`
- `feather_cape.png`
- `dragon_wings.png`
