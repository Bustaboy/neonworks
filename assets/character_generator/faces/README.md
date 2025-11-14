# Facial Features

Face components define character expressions and features.

## Specifications

- **Size:** 24x24 pixels
- **Layers:**
  - face_base (z_order: 80) - Base face shape
  - eyes (z_order: 90) - Eye sprites
  - facial_features (z_order: 100) - Nose, mouth, eyebrows
  - facial_hair (z_order: 110) - Beards, mustaches
- **Attachment:** head anchor point

## Components

### Face Base
Basic face shape and structure.
- Different races/species
- Age variations
- Skin tone customization

### Eyes
Multiple expressions for each eye style:
- neutral
- happy (squinting with smile)
- angry (narrowed, furrowed)
- surprised (wide open)
- sad (downturned)
- closed

### Facial Features
- Nose shapes
- Mouth expressions (neutral, smile, frown, open)
- Eyebrow positions
- Cheek markings, freckles

### Facial Hair
- Beards (full, goatee, soul patch)
- Mustaches (handlebar, pencil, walrus)
- Sideburns
- Stubble

## Expression System

Faces can define multiple expression sets:
```json
"facial_features": {
  "eyes": {
    "asset_path": "assets/character_generator/faces/eyes_01.png",
    "expressions": ["neutral", "happy", "angry", "surprised", "sad"]
  },
  "mouth": {
    "asset_path": "assets/character_generator/faces/mouth_01.png",
    "expressions": ["neutral", "smile", "frown", "open"]
  }
}
```

## Color Customization

- **skin:** Match body skin tone
- **hair:** For eyebrows and facial hair

## Compatibility

- Tag with compatible races/species
- Tag with compatible genders
- Consider age appropriateness

## Naming Convention

```
{race}_face_{variant}.png
eyes_{style}_{expression}.png
mouth_{style}_{expression}.png
beard_{style}.png
```

Examples:
- `human_face_01.png`
- `elf_face_young.png`
- `eyes_01_happy.png`
- `mouth_01_smile.png`
- `beard_full.png`
