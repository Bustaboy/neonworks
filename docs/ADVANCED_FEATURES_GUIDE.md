#!/
 Advanced Features Guide

**Version:** 2.0
**Last Updated:** 2025-11-14
**Purpose:** Guide to advanced AI and animation features in NeonWorks

---

## Table of Contents

1. [Overview](#overview)
2. [Stable Diffusion Sprite Generation](#stable-diffusion-sprite-generation)
3. [Style Transfer System](#style-transfer-system)
4. [Multi-Directional Sprite Generation](#multi-directional-sprite-generation)
5. [Physics-Based Animation](#physics-based-animation)
6. [Character Generator Art Assets](#character-generator-art-assets)
7. [Hardware Requirements](#hardware-requirements)
8. [Examples & Tutorials](#examples--tutorials)

---

## Overview

NeonWorks includes advanced AI-powered and procedural systems for creating game art and animations:

- **Stable Diffusion**: Generate sprites from text descriptions (GPU required)
- **Style Transfer**: Apply artistic styles to sprites (neural & palette-based)
- **Multi-Directional**: Generate 4-way and 8-way directional sprites
- **Physics Animation**: Realistic physics-based sprite animations
- **Character Generator**: Modular character creation with 16+ sample assets

All features integrate seamlessly with the existing NeonWorks engine and animation system.

---

## Stable Diffusion Sprite Generation

### Features

- Text-to-sprite generation using SD 1.5
- ControlNet integration for pose control
- Multiple sprite styles (pixel-art, hand-drawn, anime, realistic)
- Batch generation
- Background removal
- Automatic sprite sizing

### Hardware Support

- **NVIDIA GPUs**: CUDA (RTX 20/30/40 series)
- **AMD GPUs**: ROCm (RX 6000/7000 series, MI series)
- **Apple Silicon**: Metal Performance Shaders (M1/M2/M3)
- **Minimum VRAM**: 6+ GB recommended

### Basic Usage

```python
from editor.sd_sprite_generator import generate_sprite

# Generate a single sprite
sprite = generate_sprite(
    prompt="fantasy knight character with sword and shield",
    style="pixel-art",
    size=(64, 64)
)

sprite.image.save("knight.png")
```

### Advanced Usage

```python
from editor.sd_sprite_generator import (
    SDSpriteGenerator,
    SpriteGenerationConfig
)

# Create generator
generator = SDSpriteGenerator()

# Configure generation
config = SpriteGenerationConfig(
    prompt="cyberpunk warrior robot",
    negative_prompt="blurry, low quality, distorted",
    width=128,
    height=128,
    num_inference_steps=30,
    guidance_scale=7.5,
    num_images=4,
    seed=42,
    sprite_style="pixel-art",
    remove_background=True,
    resize_to=(64, 64)
)

# Generate
sprites = generator.generate(config)

# Save
for i, sprite in enumerate(sprites):
    sprite.save(f"warrior_{i}.png")
```

### Batch Generation

```python
# Generate multiple characters
prompts = [
    "warrior with sword",
    "mage with staff",
    "rogue with daggers",
    "cleric with holy symbol"
]

all_sprites = generator.generate_batch(
    prompts,
    base_config=config,
    output_dir="assets/characters"
)
```

### Character Animation Sets

```python
# Generate complete animation set
animations = ["idle", "walk", "attack", "cast_spell", "death"]

character_set = generator.generate_character_set(
    character_prompt="fantasy elf ranger",
    animations=animations,
    output_dir="assets/elf_ranger",
    config=config
)
```

### Sprite Styles

Available styles with automatic prompt enhancement:

- **pixel-art**: 16-bit retro game sprites
- **hand-drawn**: Illustrated game art style
- **anime**: Anime-style cel-shaded sprites
- **realistic**: Realistic rendered sprites
- **chibi**: Cute SD proportions
- **isometric**: 3D-rendered isometric sprites

### Model Configuration

```python
# Use custom model
generator = SDSpriteGenerator(
    model_id="runwayml/stable-diffusion-v1-5",
    controlnet_model_id="lllyasviel/control_v11p_sd15_openpose",
    cache_dir="models/stable-diffusion"
)
```

### Memory Optimization

The generator automatically enables:
- xFormers memory efficient attention (if available)
- VAE slicing
- Attention slicing
- Safetensors format

---

## Style Transfer System

### Features

- **Neural style transfer**: Deep learning-based artistic style transfer
- **Palette swapping**: Fast color palette extraction and application
- **CPU and GPU support**: Works on any hardware
- **Batch processing**: Apply styles to multiple sprites

### Methods

#### 1. Neural Style Transfer (Requires GPU)

Uses VGG19 deep features for artistic style transfer.

```python
from editor.style_transfer import transfer_style

# Apply artistic style
result = transfer_style(
    content="character.png",
    style="art_reference.png",
    method="neural",
    num_steps=300,
    style_weight=1000000,
    content_weight=1
)

result.save("stylized_character.png")
```

#### 2. Palette Swapping (CPU-friendly)

Fast color palette extraction and application.

```python
# Apply color palette
result = transfer_style(
    content="character.png",
    style="palette_reference.png",
    method="palette",
    num_colors=16,
    dithering=False
)
```

### Advanced Usage

```python
from editor.style_transfer import (
    StyleTransferSystem,
    PaletteSwapper,
    StyleTransferConfig
)

# Create system
system = StyleTransferSystem(prefer_gpu=True)

# Auto-select method based on hardware
result = system.transfer(
    content=content_image,
    style=style_image,
    method="auto"  # Chooses neural or palette based on GPU availability
)
```

### Palette Swapper

```python
# Extract palette
swapper = PaletteSwapper()
palette = swapper.extract_palette(style_image, num_colors=16)

# Apply to multiple sprites
sprites = [sprite1, sprite2, sprite3]
recolored = [
    swapper.apply_palette(sprite, palette, dithering=True)
    for sprite in sprites
]
```

### Batch Processing

```python
# Apply style to animation frames
stylized_frames = system.batch_transfer(
    content_images=animation_frames,
    style=art_style,
    method="palette",
    num_colors=16,
    output_dir="stylized_animation"
)
```

### Neural Transfer Configuration

```python
config = StyleTransferConfig(
    content_image=content,
    style_image=style,
    output_size=(512, 512),
    num_steps=300,
    style_weight=1000000,
    content_weight=1,
    learning_rate=0.01,
    style_layers=['conv1_1', 'conv2_1', 'conv3_1', 'conv4_1', 'conv5_1'],
    content_layers=['conv4_2'],
    preserve_alpha=True
)

from editor.style_transfer import NeuralStyleTransfer
neural = NeuralStyleTransfer()
result = neural.transfer(config)
```

---

## Multi-Directional Sprite Generation

### Features

- **4-way sprites**: Cardinal directions (N, E, S, W)
- **8-way sprites**: Full 8-directional movement
- **Multiple methods**: AI-powered, flip/mirror, rotation
- **Sprite sheets**: Automatic sprite sheet generation
- **Animation support**: Multi-directional animation sequences

### Direction Enum

```python
from editor.multi_directional import Direction

# Cardinal directions (4-way)
directions_4 = Direction.cardinal_4()
# [NORTH, EAST, SOUTH, WEST]

# Full 8 directions
directions_8 = Direction.full_8()
# [NORTH, NORTH_EAST, EAST, SOUTH_EAST, SOUTH, SOUTH_WEST, WEST, NORTH_WEST]

# Direction properties
angle = Direction.EAST.angle  # 90 degrees
vector = Direction.NORTH.vector  # (0, -1)
```

### Quick Generation

```python
from editor.multi_directional import (
    generate_4way_sprites,
    generate_8way_sprites
)

# Generate 4-way sprites
sprite_set_4 = generate_4way_sprites(
    source="character_front.png",
    method="rotate",
    output_dir="assets/character_4way"
)

# Generate 8-way sprites
sprite_set_8 = generate_8way_sprites(
    source="character_front.png",
    method="flip",
    output_dir="assets/character_8way"
)
```

### Advanced Configuration

```python
from editor.multi_directional import (
    MultiDirectionalGenerator,
    DirectionalConfig
)

generator = MultiDirectionalGenerator(use_ai=True)

config = DirectionalConfig(
    source_sprite=sprite,
    num_directions=8,
    front_direction=Direction.SOUTH,
    method="ai",  # or "flip" or "rotate"
    symmetric=True,
    resize_to=(64, 64),
    remove_background=True
)

sprite_set = generator.generate(config)
```

### Generation Methods

#### 1. Rotation (Best for vehicles, projectiles)

```python
config = DirectionalConfig(
    source_sprite=vehicle_sprite,
    method="rotate",
    num_directions=8
)
```

#### 2. Flip/Mirror (Best for symmetric characters)

```python
config = DirectionalConfig(
    source_sprite=character_sprite,
    method="flip",
    symmetric=True,
    flip_directions=[
        (Direction.EAST, Direction.WEST),
        (Direction.NORTH_EAST, Direction.NORTH_WEST),
        (Direction.SOUTH_EAST, Direction.SOUTH_WEST),
    ]
)
```

#### 3. AI-Powered (Best for complex characters)

```python
config = DirectionalConfig(
    text_prompt="fantasy knight character",
    method="ai",
    num_directions=8,
    consistency_seed=True,
    ai_config=SpriteGenerationConfig(
        width=64,
        height=64,
        sprite_style="pixel-art"
    )
)
```

### Sprite Sheets

```python
# Save as horizontal strip
sprite_set.save_sprite_sheet(
    "character_sheet.png",
    layout="horizontal"
)

# Save as grid
sprite_set.save_sprite_sheet(
    "character_sheet.png",
    layout="grid"
)

# Save as vertical strip
sprite_set.save_sprite_sheet(
    "character_sheet.png",
    layout="vertical"
)
```

### Animation Sets

```python
# Generate multi-directional animation
animation_frames = [frame1, frame2, frame3, frame4]

animation_set = generator.generate_animation_set(
    config=config,
    animation_frames=animation_frames,
    output_dir="assets/walk_animation"
)

# Result: animation_set[Direction.NORTH] = [frame1_n, frame2_n, ...]
```

---

## Physics-Based Animation

### Features

- **Gravity and projectile motion**: Realistic ballistic trajectories
- **Spring systems**: Wobble, overshoot, and settle effects
- **Squash and stretch**: Cartoon-style deformation
- **Momentum and inertia**: Realistic movement physics
- **Secondary animation**: Follow-through and overlapping action

### Quick Examples

```python
from editor.physics_animation import (
    create_jump_animation,
    create_bounce_animation
)

# Jump animation
jump_frames = create_jump_animation(
    sprite="character.png",
    jump_velocity=400.0,
    duration=1.5,
    fps=30,
    squash_stretch=True
)

# Bounce animation
bounce_frames = create_bounce_animation(
    sprite="ball.png",
    bounce_height=150.0,
    num_bounces=5,
    fps=30
)
```

### Physics Animator

```python
from editor.physics_animation import PhysicsAnimation, Vector2D

physics = PhysicsAnimation(gravity=980.0)  # pixels/s²

# Jump with squash/stretch
jump = physics.animate_jump(
    sprite=sprite,
    jump_velocity=500.0,
    duration=2.0,
    fps=30,
    squash_stretch=True
)

# Projectile motion
projectile = physics.animate_projectile(
    sprite=arrow,
    initial_velocity=Vector2D(300, -200),
    duration=2.0,
    fps=30,
    rotation=True  # Rotate to face velocity
)

# Spring wobble
spring = physics.animate_spring(
    sprite=sprite,
    displacement=Vector2D(50, 0),
    duration=2.0,
    fps=30,
    stiffness=200.0,
    damping=15.0
)

# Pendulum swing
swing = physics.animate_swing(
    sprite=sprite,
    anchor_offset=Vector2D(0, -20),
    max_angle=30.0,
    period=2.0,
    num_cycles=3,
    fps=30
)
```

### Vector Math

```python
from editor.physics_animation import Vector2D

# Create vectors
v1 = Vector2D(3, 4)
v2 = Vector2D(1, 0)

# Operations
v3 = v1 + v2  # Addition
v4 = v1 - v2  # Subtraction
v5 = v1 * 2.5  # Scalar multiplication
v6 = v1 / 2.0  # Scalar division

# Properties
magnitude = v1.magnitude()  # 5.0
normalized = v1.normalized()  # Unit vector
dot_product = v1.dot(v2)  # Dot product
```

### Physics State

```python
from editor.physics_animation import PhysicsState

state = PhysicsState(
    position=Vector2D(0, 0),
    velocity=Vector2D(100, -200),
    mass=1.0,
    drag=0.1,  # Air resistance
    elasticity=0.7,  # Bounciness
    angular_velocity=0.5  # Rotation speed
)

# Apply forces
gravity = Vector2D(0, 980)
state.apply_force(gravity * state.mass)

# Update physics
dt = 1/60  # 60 FPS
state.update(dt)
```

### Spring System

```python
from editor.physics_animation import SpringSystem

spring = SpringSystem(
    anchor=Vector2D(0, 0),
    position=Vector2D(100, 0),
    stiffness=150.0,  # Spring constant
    damping=10.0,  # Damping coefficient
    mass=1.0
)

# Simulate spring motion
for _ in range(60):
    spring.update(1/60)
    # spring.position contains current position
```

### Squash and Stretch

```python
from editor.physics_animation import SquashStretchParams

params = SquashStretchParams(
    enabled=True,
    max_scale=1.3,  # Maximum stretch
    min_scale=0.7,  # Maximum squash
    preserve_volume=True,  # Preserve sprite area
    speed_threshold=5.0,
    direction_influence=1.0
)

# Applied automatically in jump/bounce animations
```

### Secondary Animation

```python
from editor.physics_animation import SecondaryAnimation

secondary = SecondaryAnimation()

# Add follow-through (hair, capes, etc.)
enhanced = secondary.add_follow_through(
    frames=animation_frames,
    delay_frames=2,
    decay=0.8
)

# Add overlapping action
enhanced = secondary.add_overlap(
    frames=animation_frames,
    lag_pixels=3
)
```

---

## Character Generator Art Assets

### Overview

The character generator includes procedurally generated placeholder sprites across 6 categories:

- **Bodies**: Male, Female (2 sprites)
- **Hair**: Short, Long, Mohawk, Bun (4 sprites)
- **Clothing**: Tunic, Robe, Armor (3 sprites)
- **Weapons**: Sword, Staff, Bow, Dagger (4 sprites)
- **Faces**: Human, Elf, Orc (3 sprites)
- **Accessories**: Head, Neck, Back (expandable)

**Total**: 16 sprites + grayscale masks for color customization

### Directory Structure

```
assets/character_generator/
├── bodies/
│   ├── base_body_male.png
│   └── base_body_female.png
├── hair/
│   ├── hair_short.png
│   ├── hair_long.png
│   ├── hair_mohawk.png
│   └── hair_bun.png
├── clothing/
│   ├── clothing_tunic.png
│   ├── clothing_robe.png
│   └── clothing_armor.png
├── weapons/
│   ├── weapon_sword.png
│   ├── weapon_staff.png
│   ├── weapon_bow.png
│   └── weapon_dagger.png
├── faces/
│   ├── face_human.png
│   ├── face_elf.png
│   └── face_orc.png
└── masks/
    ├── bodies/
    ├── hair/
    ├── clothing/
    └── weapons/
```

### Generation Script

```bash
# Generate all character assets
python scripts/generate_character_assets.py
```

### Using Assets

```python
from PIL import Image

# Load components
body = Image.open("assets/character_generator/bodies/base_body_male.png")
hair = Image.open("assets/character_generator/hair/hair_short.png")
clothing = Image.open("assets/character_generator/clothing/clothing_tunic.png")
weapon = Image.open("assets/character_generator/weapons/weapon_sword.png")

# Composite character (respecting z-order)
character = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
character.paste(body, (0, 0), body)
character.paste(clothing, (0, 0), clothing)
character.paste(hair, (0, 0), hair)
character.paste(weapon, (0, 0), weapon)

character.save("my_character.png")
```

### Color Customization

Each component has a corresponding grayscale mask for recoloring:

```python
def recolor_sprite(sprite, mask, color):
    """Apply color to masked regions."""
    sprite_rgba = sprite.convert("RGBA")
    colored = Image.new("RGBA", sprite.size)

    # Apply color to white pixels in mask
    for x in range(sprite.width):
        for y in range(sprite.height):
            mask_value = mask.getpixel((x, y))
            if mask_value > 0:
                alpha = sprite_rgba.getpixel((x, y))[3]
                colored.putpixel((x, y), (*color, alpha))
            else:
                colored.putpixel((x, y), sprite_rgba.getpixel((x, y)))

    return colored

# Load mask
hair_mask = Image.open("assets/character_generator/masks/hair/hair_short_mask.png")

# Recolor hair
red_hair = recolor_sprite(hair, hair_mask, (200, 50, 50))
```

### Integration with character_parts.json

Assets match the structure defined in `neonworks/data/character_parts.json`:

- **Layer system**: 18 layers (z-order 0-170)
- **Color zones**: Skin, hair, primary, secondary, tertiary, metal
- **Component categories**: Bodies, hair, clothing, accessories, weapons, faces

---

## Hardware Requirements

### Minimum (CPU-only)

- **CPU**: Any modern CPU
- **RAM**: 8+ GB
- **Features**: Multi-directional, physics animation, character assets

### Recommended (with GPU)

- **GPU**: RTX 3060 / RX 6600 XT (6+ GB VRAM)
- **RAM**: 16+ GB
- **Features**: All features including SD and neural style transfer

### Professional (High-end)

- **GPU**: RTX 4080 / RX 7900 XT (16+ GB VRAM)
- **RAM**: 32+ GB
- **Features**: Fast generation, large batches, high quality

### GPU Support Matrix

| Feature | NVIDIA (CUDA) | AMD (ROCm) | Apple (MPS) | CPU |
|---------|---------------|------------|-------------|-----|
| SD Sprite Gen | ✅ | ✅ | ✅ | ❌ |
| Neural Style | ✅ | ✅ | ✅ | ❌ |
| Palette Style | ✅ | ✅ | ✅ | ✅ |
| Multi-Directional | ✅ | ✅ | ✅ | ✅ |
| Physics Anim | ✅ | ✅ | ✅ | ✅ |
| Character Gen | ✅ | ✅ | ✅ | ✅ |

---

## Examples & Tutorials

### Example 1: Complete Character Creation

```python
from editor.sd_sprite_generator import generate_sprite
from editor.multi_directional import generate_8way_sprites
from editor.physics_animation import create_jump_animation

# 1. Generate base sprite with AI
base = generate_sprite(
    prompt="fantasy warrior with sword",
    style="pixel-art",
    size=(64, 64)
)

# 2. Create 8-way directional sprites
directional = generate_8way_sprites(
    source=base.image,
    method="ai",  # Uses AI to generate different angles
    output_dir="assets/warrior"
)

# 3. Add physics animations
for direction, sprite in directional.sprites.items():
    jump_anim = create_jump_animation(
        sprite=sprite,
        duration=1.0,
        fps=30
    )

    # Save animation
    for i, frame in enumerate(jump_anim):
        frame.save(f"assets/warrior/jump_{direction.value}_{i:02d}.png")
```

### Example 2: Batch Sprite Generation

```python
from editor.sd_sprite_generator import SDSpriteGenerator
from editor.style_transfer import transfer_style

# Generate party of characters
generator = SDSpriteGenerator()

characters = [
    "warrior knight with sword",
    "wizard mage with staff",
    "rogue thief with daggers",
    "cleric priest with holy symbol"
]

# Generate all characters
for character in characters:
    sprites = generator.generate(SpriteGenerationConfig(
        prompt=character,
        width=64,
        height=64,
        sprite_style="pixel-art",
        num_images=1
    ))

    sprite = sprites[0]

    # Apply consistent art style
    styled = transfer_style(
        content=sprite.image,
        style="art_style_reference.png",
        method="palette",
        num_colors=16
    )

    styled.save(f"{character.split()[0]}.png")
```

### Example 3: Animation Pipeline

```python
from editor.physics_animation import PhysicsAnimation, Vector2D
from editor.multi_directional import generate_4way_sprites

physics = PhysicsAnimation()

# Create base animations
idle = [sprite]  # Static idle
walk = create_walk_cycle(sprite, frames=6)
jump = physics.animate_jump(sprite, duration=1.0, fps=30)
attack = create_attack_animation(sprite, frames=4)

# Generate directional versions
for anim_name, anim_frames in [("idle", idle), ("walk", walk), ("jump", jump), ("attack", attack)]:
    for frame_idx, frame in enumerate(anim_frames):
        # Generate 4 directions for this frame
        directional = generate_4way_sprites(frame, method="flip")

        # Save each direction
        for direction, dir_sprite in directional.sprites.items():
            output_path = f"assets/animations/{anim_name}/{direction.value}/frame_{frame_idx:02d}.png"
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            dir_sprite.save(output_path)
```

### Example 4: Style Consistency

```python
from editor.sd_sprite_generator import SDSpriteGenerator
from editor.style_transfer import PaletteSwapper

# Generate multiple characters with consistent style
generator = SDSpriteGenerator()
swapper = PaletteSwapper()

# Generate style reference
style_ref = generator.generate(SpriteGenerationConfig(
    prompt="pixel art game sprite, retro 16-bit style",
    width=64,
    height=64,
    seed=42
))[0].image

# Extract consistent palette
palette = swapper.extract_palette(style_ref, num_colors=16)

# Generate and recolor multiple sprites
characters = ["knight", "mage", "archer", "healer"]

for character in characters:
    # Generate
    sprite = generator.generate(SpriteGenerationConfig(
        prompt=f"fantasy {character} character",
        width=64,
        height=64
    ))[0].image

    # Apply consistent palette
    recolored = swapper.apply_palette(sprite, palette, dithering=True)
    recolored.save(f"{character}_consistent.png")
```

---

## Integration Tests

Run comprehensive tests for all features:

```bash
python scripts/test_all_enhancements.py
```

This tests:
- ✅ Stable Diffusion sprite generation (if GPU available)
- ✅ Style transfer system (neural and palette)
- ✅ Multi-directional sprite generation (4-way and 8-way)
- ✅ Physics-based animation (all methods)
- ✅ Character generator assets (all categories)

---

## Performance Tips

### 1. Model Caching

```python
# Cache models for faster subsequent runs
generator = SDSpriteGenerator(cache_dir="models/stable-diffusion")
```

### 2. Batch Processing

```python
# Generate multiple sprites in one call for efficiency
config.num_images = 4  # Generate 4 at once
sprites = generator.generate(config)
```

### 3. Memory Management

```python
# Clean up GPU memory after batch
generator.cleanup()

# Or use context manager
with SDSpriteGenerator() as gen:
    sprites = gen.generate(config)
# Auto-cleanup on exit
```

### 4. Lower Quality for Prototyping

```python
# Faster generation for iteration
config.num_inference_steps = 20  # Default: 30
config.guidance_scale = 6.0  # Default: 7.5
config.width = 64  # Smaller size
```

### 5. Palette Transfer for Speed

```python
# Much faster than neural transfer
result = transfer_style(
    content=sprite,
    style=reference,
    method="palette",  # vs "neural"
    num_colors=16
)
```

---

## Troubleshooting

### Issue: "No module named 'torch'"

**Solution**: Install PyTorch for your platform:

```bash
# NVIDIA (CUDA)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# AMD (ROCm)
pip install torch torchvision --index-url https://download.pytorch.org/whl/rocm5.6

# CPU-only
pip install torch torchvision
```

### Issue: "CUDA out of memory"

**Solutions**:
- Reduce sprite size
- Lower num_inference_steps
- Enable memory optimizations (auto-enabled)
- Generate fewer images at once
- Close other GPU applications

### Issue: Slow generation on CPU

**Solutions**:
- Use palette-based style transfer instead of neural
- Use flip/rotate instead of AI for multi-directional
- Reduce sprite resolution
- Consider cloud GPU services (Colab, RunPod, etc.)

### Issue: Poor sprite quality

**Solutions**:
- Increase num_inference_steps (30-50)
- Adjust guidance_scale (7-10)
- Improve prompt with more details
- Use negative_prompt to avoid artifacts
- Try different sprite_style presets

---

## API Reference

See individual module docstrings for complete API documentation:

- `editor/sd_sprite_generator.py` - Stable Diffusion API
- `editor/style_transfer.py` - Style transfer API
- `editor/multi_directional.py` - Multi-directional API
- `editor/physics_animation.py` - Physics animation API
- `scripts/generate_character_assets.py` - Asset generation

---

## Next Steps

1. **Install Dependencies**:
   ```bash
   pip install torch torchvision diffusers transformers accelerate
   pip install rembg  # For background removal
   ```

2. **Download Models**:
   ```bash
   python scripts/download_models.py --recommended
   ```

3. **Run Tests**:
   ```bash
   python scripts/test_all_enhancements.py
   ```

4. **Try Examples**:
   - See `examples/` directory for complete demos
   - Check `docs/` for more tutorials

---

**Last Updated**: 2025-11-14
**Maintainers**: NeonWorks Team
**Questions?**: Check README.md or open an issue on GitHub
