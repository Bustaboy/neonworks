# Weapons & Held Items

Weapons and items that characters hold.

## Specifications

- **Size:** Varies by weapon type
- **Layers:**
  - hand_accessory_left (z_order: 150) - Off-hand/shield
  - hand_accessory_right (z_order: 160) - Main hand
- **Attachment:** left_hand or right_hand anchor point

## Grip Points

Define where the character's hand grips the weapon:
```json
"grip_point": {"x": 12, "y": 32}
```

## Weapon Categories

### Melee Weapons
- Swords (shortsword, longsword, greatsword)
- Axes (hatchet, battle axe)
- Maces, hammers, clubs
- Daggers, knives
- Spears, polearms

### Ranged Weapons
- Bows (shortbow, longbow)
- Crossbows
- Staves (magic staves)
- Wands

### Shields
- Small buckler
- Medium shield
- Large tower shield

### Tools & Items
- Torches
- Potions
- Books, scrolls
- Musical instruments

## Color Customization

Common color zones:
- **metal:** Blade, metal parts
- **secondary:** Handle, grip
- **tertiary:** Magical effects, gems

## Weapon Stats

```json
"weapon_stats": {
  "damage": 15,
  "attack_speed": 1.0,
  "range": "melee|ranged",
  "durability": 100
}
```

## Animation Overrides

Weapons can have custom attack animations:
```json
"animation_overrides": {
  "attack": {
    "sprite_path": "path/to/attack_animation.png",
    "frames": 3
  }
}
```

## Naming Convention

```
{material}_{weapon_type}.png
```

Examples:
- `iron_sword.png`
- `wooden_staff.png`
- `steel_shield.png`
- `magic_wand.png`
