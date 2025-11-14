# AI Animation System

**Version:** 1.0.0
**Created:** 2025-11-14
**Status:** Framework Complete - AI Models Pending

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Natural Language Interpretation](#natural-language-interpretation)
4. [Animation Generation](#animation-generation)
5. [UI Interface](#ui-interface)
6. [Integration Guide](#integration-guide)
7. [AI Model Integration](#ai-model-integration)
8. [Examples](#examples)
9. [API Reference](#api-reference)
10. [Future Enhancements](#future-enhancements)

---

## Overview

The AI Animation System enables users to generate sprite animations using natural language descriptions. Instead of manually creating frame-by-frame animations, users can simply describe what they want:

- **"Make the character walk slowly like they're tired"**
- **"Create an aggressive attack animation"**
- **"Sneaky walk for a rogue character"**

### Key Features

- **Natural Language Input:** Describe animations in plain English
- **LLM Interpretation Layer:** Understands intent and converts to parameters
- **Multiple Animation Types:** Walk, run, attack, cast spell, jump, and more
- **Style Modifiers:** Adjust speed, intensity, mood, and feel
- **Live Preview:** See animations in real-time with playback controls
- **Refinement System:** Iterate on animations with feedback
- **Export Options:** Individual frames or sprite sheets
- **Character Generator Integration:** Works seamlessly with component system

### Use Cases

1. **Rapid Prototyping:** Quickly test animation ideas without manual work
2. **NPC Animation:** Generate diverse animations for many NPCs
3. **Animation Variants:** Create variations (tired walk, happy walk, sneaky walk)
4. **Non-Artists:** Enable non-artists to create animations
5. **Batch Processing:** Animate many sprites at once

---

## Architecture

### System Components

```
AI Animation System
│
├── Interpretation Layer
│   ├── AnimationInterpreter       # Parses natural language
│   ├── AnimationIntent            # Structured intent representation
│   └── LLM Integration (TODO)     # Connect to actual LLM
│
├── Generation Layer
│   ├── AIAnimator                 # Core animation generator
│   ├── Animation Types            # Standard animation definitions
│   ├── Procedural Fallback        # Rule-based animations
│   └── AI Models (TODO)           # ML model integration
│
├── UI Layer
│   ├── AIAnimatorUI               # Visual editor interface
│   ├── Preview System             # Real-time animation playback
│   └── Export Tools               # Frame/sprite sheet export
│
└── Integration Layer
    ├── Character Generator Link   # Component system integration
    ├── ECS Integration            # Entity animation system
    └── Asset Pipeline             # Export to asset folders
```

### Data Flow

```
User Input (Natural Language)
    ↓
Interpretation Layer (LLM)
    ↓
AnimationIntent (Structured Parameters)
    ↓
AnimationConfig (Generator Parameters)
    ↓
AI Animation Generator
    ↓
Animation Frames (Pygame Surfaces)
    ↓
Preview / Export
```

---

## Natural Language Interpretation

### How It Works

The interpretation layer uses an LLM (or rule-based fallback) to understand user requests and convert them into structured parameters.

#### Example Flow

**User Input:**
```
"Make the character walk slowly like they're tired"
```

**Interpretation:**
```python
AnimationIntent(
    animation_type="walk",           # Base animation
    style_modifiers=["slow", "tired"],  # Style descriptors
    intensity=0.4,                   # Low energy
    speed_multiplier=0.5,            # Half speed
    special_effects=[],              # No special effects
    frame_count=6,                   # Default for walk
    confidence=0.85                  # High confidence
)
```

**Animation Config:**
```python
AnimationConfig(
    animation_type="walk",
    frame_count=6,
    frame_duration=0.24,  # Slower (0.12 / 0.5)
    loop=True,
    style="smooth",
    intensity=0.4
)
```

### Supported Keywords

#### Animation Types

| Keyword | Animation | Description |
|---------|-----------|-------------|
| walk, walking, stroll | Walk | Basic walking cycle |
| run, running, sprint, dash | Run | Running animation |
| idle, stand, wait, rest | Idle | Standing idle |
| jump, leap, hop | Jump | Jumping motion |
| attack, strike, hit, slash | Attack | Attack animation |
| cast, spell, magic | Cast Spell | Spellcasting |
| hurt, damage, injured | Hurt | Damage reaction |
| death, die, collapse | Death | Death animation |

#### Style Modifiers

| Modifier | Effect |
|----------|--------|
| slow, sluggish | Reduces speed, lowers intensity |
| fast, quick | Increases speed and intensity |
| tired, weak | Low intensity, smooth style |
| energetic, powerful | High intensity |
| aggressive | High intensity, increased speed |
| sneaky | Medium intensity, slow, smooth |
| happy | High intensity, bouncy style |
| sad | Low intensity, slow |
| angry | High intensity, snappy |
| calm, smooth | Smooth style, medium intensity |
| snappy, jerky | Snappy style |
| bouncy, fluid | Bouncy style |

#### Special Effects

| Effect | Description |
|--------|-------------|
| glow, shine | Add glowing effect |
| blur, trail | Motion blur effect |
| flash, blink | Flashing effect |
| shake, tremble | Shaking motion |
| fade | Fade in/out |
| particles, sparkles | Particle effects |

### Usage Examples

```python
from neonworks.editor.ai_animation_interpreter import AnimationInterpreter

interpreter = AnimationInterpreter(model_type="local")

# Simple request
intent = interpreter.interpret_request("walking animation")

# Complex request
intent = interpreter.interpret_request(
    "Create a sneaky walk for a rogue character with 8 frames"
)

# With context
context = {"sprite_type": "warrior", "current_animations": ["idle", "walk"]}
intent = interpreter.interpret_request(
    "add an aggressive attack",
    context=context
)

# Convert to animation config
config = interpreter.intent_to_config(intent)
```

### Refinement System

Refine animations based on user feedback:

```python
# Initial generation
intent = interpreter.interpret_request("walking animation")

# User feedback
intent = interpreter.refine_intent(intent, "make it slower")
intent = interpreter.refine_intent(intent, "more intense")
intent = interpreter.refine_intent(intent, "add a bounce")
```

### Suggestions

Get animation suggestions based on sprite characteristics:

```python
sprite_info = {
    "type": "character",
    "class": "warrior"
}

suggestions = interpreter.suggest_animations(sprite_info)
# Returns:
# [
#     ("aggressive attack", "Powerful melee strike"),
#     ("defensive idle", "Ready stance with shield"),
#     ("run", "Combat charge"),
#     ...
# ]
```

---

## Animation Generation

### Standard Animation Types

8 built-in animation types with default configurations:

```python
from neonworks.editor.ai_animator import AnimationType

AnimationType.IDLE        # 4 frames, 0.2s/frame, smooth, 0.3 intensity
AnimationType.WALK        # 6 frames, 0.12s/frame, smooth, 0.6 intensity
AnimationType.RUN         # 6 frames, 0.08s/frame, snappy, 0.9 intensity
AnimationType.ATTACK      # 4 frames, 0.1s/frame, snappy, 1.0 intensity
AnimationType.CAST_SPELL  # 6 frames, 0.15s/frame, smooth, 0.7 intensity
AnimationType.HURT        # 2 frames, 0.1s/frame, snappy, 1.0 intensity
AnimationType.DEATH       # 6 frames, 0.15s/frame, smooth, 0.8 intensity
AnimationType.JUMP        # 6 frames, 0.1s/frame, bouncy, 0.9 intensity
```

### Generation Methods

#### 1. Direct Generation

```python
from neonworks.editor.ai_animator import AIAnimator, AnimationType

animator = AIAnimator(model_type="local")

# Load sprite
sprite = pygame.image.load("character.png")

# Generate with preset
config = AnimationType.WALK
frames = animator.generate_animation(sprite, config)

# Generate with custom config
custom_config = AnimationConfig(
    animation_type="custom_move",
    frame_count=8,
    frame_duration=0.1,
    loop=True,
    style="bouncy",
    intensity=0.75
)
frames = animator.generate_animation(sprite, custom_config)
```

#### 2. Natural Language Generation

```python
from neonworks.editor.ai_animator import AIAnimator
from neonworks.editor.ai_animation_interpreter import AnimationInterpreter

animator = AIAnimator(model_type="local")
interpreter = AnimationInterpreter(model_type="local")

# Parse request
intent = interpreter.interpret_request(
    "Make character walk slowly like they're tired"
)

# Convert to config
config = interpreter.intent_to_config(intent)

# Generate
frames = animator.generate_animation(sprite, config)
```

#### 3. Batch Generation

```python
# Generate multiple animations at once
animation_types = ["idle", "walk", "run", "attack"]

animations = animator.generate_animation_batch(
    sprite,
    animation_types,
    component_id="hero"
)

# Returns:
# {
#     "idle": [frame1, frame2, frame3, frame4],
#     "walk": [frame1, frame2, ...],
#     ...
# }
```

### Procedural Animation Techniques

The current system uses procedural techniques as a fallback:

#### Idle Animation
- Gentle vertical oscillation (breathing)
- Sine wave offset: `sin(progress * 2π) * 2 * intensity`

#### Walk Animation
- Vertical bob + slight horizontal lean
- Bob: `sin(progress * 2π) * 3 * intensity`

#### Run Animation
- More pronounced bob + forward lean
- Faster movement, increased intensity

#### Attack Animation
- Wind-up (0-50%): Pull back
- Strike (50-100%): Forward thrust

#### Jump Animation
- Parabolic arc for vertical position
- Squash and stretch effects
- Squash: 0.9x height at takeoff/landing
- Stretch: 1.1x height in air

#### Hurt Animation
- Knockback motion
- Flash effect (lighten sprite)

#### Death Animation
- Rotate 90 degrees
- Fade out gradually

#### Cast Spell Animation
- Upward motion (raising hands)
- Glow effect in second half

### Post-Processing

Apply effects to generated animations:

```python
from neonworks.editor.ai_animator import AnimationPostProcessor

processor = AnimationPostProcessor()

# Smooth transitions
frames = processor.smooth_transitions(frames)

# Add motion blur
frames = processor.apply_motion_blur(frames, intensity=0.5)

# Adjust timing
frames = processor.adjust_timing(frames, hold_first=2, hold_last=3)

# Add impact frame
frames = processor.add_impact_frame(frames, position=-1, intensity=1.0)
```

---

## UI Interface

### AIAnimatorUI

Visual editor accessible via F11 hotkey (after integration).

#### Layout

```
┌─────────────────────────────────────────────────────────┐
│  AI Animation Generator                          [Close] │
├──────────────────────┬──────────────────────────────────┤
│                      │                                  │
│  1. Select Sprite    │  Preview                         │
│  [Upload] [Browse]   │  ┌────────────────────────────┐ │
│  ┌──────┐            │  │                            │ │
│  │Thumb │            │  │  [Animation Preview]       │ │
│  └──────┘            │  │                            │ │
│                      │  │                            │ │
│  2. Describe Anim    │  └────────────────────────────┘ │
│  ┌──────────────┐    │  [Play] [Pause] [◀] [▶]        │
│  │              │    │  Frame: 1/6                     │
│  │              │    │                                  │
│  └──────────────┘    │  Export                         │
│                      │  [Export Frames] [Export Sheet]  │
│  Quick Presets:      │                                  │
│  [Idle]  [Walk] [Run]│  Refine Animation               │
│  [Attack][Cast][Jump]│  ┌──────────────────────────┐   │
│                      │  │"make it slower"          │   │
│  [Generate Animation]│  └──────────────────────────┘   │
│                      │  [Apply Refinement]             │
│  Advanced Options    │                                  │
│  Intensity: ●───     │  Suggestions:                    │
│  Speed:     ──●─     │  • Idle animation               │
│                      │  • Walk animation                │
└──────────────────────┴──────────────────────────────────┘
```

#### Workflow

1. **Select Sprite:** Upload file or browse character generator components
2. **Describe Animation:** Type natural language or click preset
3. **Generate:** Click "Generate Animation" button
4. **Preview:** Watch animation in preview canvas
5. **Refine:** Provide feedback ("make it slower", "more intense")
6. **Export:** Save as individual frames or sprite sheet

#### Controls

| Control | Action |
|---------|--------|
| Upload Sprite | Load sprite from file |
| Browse Components | Select from character generator |
| Preset Buttons | Quick preset animations |
| Generate | Create animation |
| Play/Pause | Control preview playback |
| ◀ / ▶ | Navigate frames manually |
| Export Frames | Save individual PNGs |
| Export Sheet | Save sprite sheet |
| Refine | Adjust animation based on feedback |

---

## Integration Guide

### Integrating with MasterUIManager

```python
# File: ui/master_ui_manager.py

from neonworks.ui.ai_animator_ui import AIAnimatorUI

class MasterUIManager:
    def __init__(self, world, renderer):
        # ... existing code ...

        # Add AI Animator
        self.ai_animator = AIAnimatorUI(world, renderer)

    def handle_event(self, event):
        # ... existing code ...

        # F11 hotkey
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                self.ai_animator.toggle()

        # Pass events
        self.ai_animator.handle_event(event)

    def update(self, dt):
        # ... existing code ...
        self.ai_animator.update(dt)

    def render(self, screen):
        # ... existing code ...
        self.ai_animator.render(screen)
```

### Character Generator Integration

Generate animations for character components:

```python
from neonworks.data.config_loader import ConfigLoader
from neonworks.editor.ai_animator import AIAnimator, AnimationType

# Load character parts
parts = ConfigLoader.load("engine/data/character_parts.json")

# Get component
component = parts["components"]["bodies"]["knight_body_male"]

# Load sprite (or create placeholder)
sprite = pygame.image.load(component["asset_path"])

# Generate animations for all specified types
animator = AIAnimator()

for anim_type in component["animations"]:
    config = AnimationType.get_by_name(anim_type)
    frames = animator.generate_animation(sprite, config, component["id"])

    # Export with proper naming: {component_id}_{animation}_{frame}.png
    output_dir = Path(f"assets/character_generator/{component['category']}")
    animator.export_animation_frames(
        frames,
        output_dir,
        component["id"],
        anim_type
    )
```

### Entity Animation System

Integrate with ECS for runtime animation:

```python
from neonworks.core.ecs import Component

@dataclass
class AnimatedSprite(Component):
    """Component for animated sprites"""
    animations: Dict[str, List[pygame.Surface]]
    current_animation: str = "idle"
    current_frame: int = 0
    frame_timer: float = 0.0
    frame_duration: float = 0.15

class AnimationSystem(System):
    """System to update animated sprites"""

    def update(self, dt: float, world: World):
        entities = world.get_entities_with_component(AnimatedSprite)

        for entity in entities:
            anim = entity.get_component(AnimatedSprite)

            anim.frame_timer += dt

            if anim.frame_timer >= anim.frame_duration:
                anim.frame_timer = 0.0

                frames = anim.animations.get(anim.current_animation, [])
                if frames:
                    anim.current_frame = (anim.current_frame + 1) % len(frames)
```

---

## AI Model Integration

### Overview

The system currently uses procedural fallback animations. To integrate actual AI models:

### Option 1: Local ML Models

Use local models for privacy and speed:

```python
class AIAnimator:
    def __init__(self, model_type="local"):
        if model_type == "local":
            # Option A: ONNX model
            import onnxruntime as ort
            self.session = ort.InferenceSession("models/sprite_animator.onnx")

            # Option B: TensorFlow Lite
            import tensorflow as tf
            self.interpreter = tf.lite.Interpreter(model_path="models/animator.tflite")

            # Option C: PyTorch
            import torch
            self.model = torch.load("models/animator.pt")
            self.model.eval()
```

**Recommended Models:**
- **Optical Flow Models:** Generate intermediate frames
- **GANs:** Generate sprite variations
- **Diffusion Models:** Controlnet for animation

### Option 2: API Integration

Use cloud APIs for powerful models:

```python
class AIAnimator:
    def _generate_api(self, source_image, config):
        # Option A: Stability AI
        import stability_sdk

        # Option B: Runway ML
        import runwayml

        # Option C: Custom API
        import requests
        response = requests.post(
            "https://api.example.com/animate",
            json={
                "image": image_to_base64(source_image),
                "animation_type": config.animation_type,
                "frames": config.frame_count
            }
        )
        return parse_frames(response.json())
```

### Option 3: LLM Integration

Enhance interpretation with LLM:

```python
class AnimationInterpreter:
    def _interpret_api(self, user_request, context):
        # Option A: OpenAI
        import openai
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": self._build_system_prompt()},
                {"role": "user", "content": user_request}
            ]
        )
        return self._parse_llm_response(response.choices[0].message.content)

        # Option B: Anthropic Claude
        import anthropic
        client = anthropic.Anthropic(api_key="...")
        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1024,
            messages=[{"role": "user", "content": user_request}]
        )
        return self._parse_llm_response(message.content[0].text)

        # Option C: Local LLM (GPT4All, Llama.cpp)
        from gpt4all import GPT4All
        model = GPT4All("orca-mini-3b.gguf")
        response = model.generate(prompt, max_tokens=512)
        return self._parse_llm_response(response)
```

### Training Custom Models

To train a custom sprite animation model:

1. **Dataset Preparation:**
   - Collect sprite animations (thousands of samples)
   - Label with animation types and styles
   - Create paired data (static frame → animation sequence)

2. **Model Architecture:**
   - Encoder: Extract features from static sprite
   - Generator: Create frame sequence
   - Temporal coherence: Ensure smooth transitions

3. **Training:**
   ```python
   # Pseudo-code for training
   for epoch in range(num_epochs):
       for batch in dataloader:
           static_sprite, animation_frames = batch

           # Generate prediction
           predicted_frames = model(static_sprite, animation_params)

           # Compute loss
           loss = frame_loss(predicted_frames, animation_frames)
           loss += temporal_consistency_loss(predicted_frames)
           loss += perceptual_loss(predicted_frames, animation_frames)

           # Backprop
           optimizer.zero_grad()
           loss.backward()
           optimizer.step()
   ```

4. **Export:**
   ```python
   # Export to ONNX for deployment
   torch.onnx.export(
       model,
       example_input,
       "sprite_animator.onnx",
       opset_version=14
   )
   ```

---

## Examples

See `examples/ai_animation_demo.py` for comprehensive demos:

### Example 1: Basic Usage

```python
import pygame
from neonworks.editor.ai_animator import AIAnimator, AnimationType

pygame.init()

animator = AIAnimator(model_type="local")
sprite = pygame.image.load("character.png")

# Generate walk animation
walk_frames = animator.generate_animation(sprite, AnimationType.WALK)

# Export
animator.export_animation_frames(
    walk_frames,
    Path("output/hero"),
    "hero",
    "walk"
)
```

### Example 2: Natural Language

```python
from neonworks.editor.ai_animation_interpreter import AnimationInterpreter

interpreter = AnimationInterpreter()
animator = AIAnimator()

# Parse natural language
intent = interpreter.interpret_request(
    "Create a sneaky walk for a rogue character"
)

# Generate
config = interpreter.intent_to_config(intent)
frames = animator.generate_animation(sprite, config)
```

### Example 3: Batch Processing

```python
# Generate all standard animations
animation_types = ["idle", "walk", "run", "attack", "jump", "hurt", "death"]

animations = animator.generate_animation_batch(
    sprite,
    animation_types,
    component_id="hero"
)

# Export all
for anim_type, frames in animations.items():
    animator.export_sprite_sheet(
        frames,
        Path(f"output/{anim_type}_sheet.png"),
        layout="horizontal"
    )
```

---

## API Reference

### AnimationInterpreter

```python
class AnimationInterpreter:
    def interpret_request(user_request: str, context: Optional[Dict]) -> AnimationIntent
    def refine_intent(intent: AnimationIntent, feedback: str) -> AnimationIntent
    def suggest_animations(sprite_info: Dict) -> List[Tuple[str, str]]
    def intent_to_config(intent: AnimationIntent) -> AnimationConfig
```

### AIAnimator

```python
class AIAnimator:
    def generate_animation(
        source_image: pygame.Surface,
        config: AnimationConfig,
        component_id: Optional[str]
    ) -> List[pygame.Surface]

    def generate_animation_batch(
        source_image: pygame.Surface,
        animation_types: List[str],
        component_id: Optional[str]
    ) -> Dict[str, List[pygame.Surface]]

    def export_animation_frames(
        frames: List[pygame.Surface],
        output_dir: Path,
        component_id: str,
        animation_type: str
    )

    def export_sprite_sheet(
        frames: List[pygame.Surface],
        output_path: Path,
        layout: str = "horizontal"
    )
```

### AnimationPostProcessor

```python
class AnimationPostProcessor:
    @staticmethod
    def smooth_transitions(frames: List[pygame.Surface]) -> List[pygame.Surface]

    @staticmethod
    def apply_motion_blur(frames: List[pygame.Surface], intensity: float) -> List[pygame.Surface]

    @staticmethod
    def adjust_timing(
        frames: List[pygame.Surface],
        hold_first: int,
        hold_last: int
    ) -> List[pygame.Surface]

    @staticmethod
    def add_impact_frame(
        frames: List[pygame.Surface],
        position: int,
        intensity: float
    ) -> List[pygame.Surface]
```

---

## Future Enhancements

### Phase 2: AI Model Integration

- [ ] Integrate local ML models (ONNX, TFLite)
- [ ] Connect to cloud APIs (Stability AI, Runway)
- [ ] Add model selection UI
- [ ] Implement model caching
- [ ] Support custom model plugins

### Phase 3: Advanced Features

- [ ] **Multi-directional Animation:** Generate 4/8 direction sprites
- [ ] **Expression Transfer:** Transfer facial expressions to sprites
- [ ] **Style Transfer:** Apply art styles to animations
- [ ] **Interpolation:** Generate intermediate frames for smoothness
- [ ] **Physics Simulation:** Cloth, hair physics simulation
- [ ] **Skeleton-based Animation:** Bone rigging for complex animations

### Phase 4: Workflow Enhancements

- [ ] **Animation Library:** Save and reuse animation presets
- [ ] **Collaborative Editing:** Share animations with team
- [ ] **Version Control:** Track animation iterations
- [ ] **A/B Testing:** Compare animation variants
- [ ] **Performance Metrics:** FPS impact analysis
- [ ] **Auto-Optimization:** Reduce frame count while maintaining quality

### Phase 5: Advanced LLM Features

- [ ] **Animation Scripting:** "Walk to door, open it, walk through"
- [ ] **Mood Analysis:** Detect mood from sprite and suggest animations
- [ ] **Context-Aware Suggestions:** Based on game state
- [ ] **Natural Refinement:** "A bit faster" → precise adjustment
- [ ] **Animation Comparison:** "Like X but more Y"

---

## Summary

The AI Animation System provides a powerful framework for generating sprite animations through natural language. The current implementation includes:

### ✅ Complete

- Natural language interpretation layer
- 8 standard animation types
- Procedural animation fallback
- Style modifier system
- Refinement and iteration support
- Live preview interface
- Export to frames/sprite sheets
- Character generator integration
- Comprehensive documentation
- Demo examples

### ⏳ Pending

- Actual AI model integration (local or API)
- Production LLM connection
- File picker dialogs in UI
- Advanced post-processing effects
- Multi-directional sprite support

### Getting Started

1. **Try the demos:** `python examples/ai_animation_demo.py`
2. **Explore the UI:** Integrate with MasterUIManager (F11 hotkey)
3. **Integrate AI models:** See "AI Model Integration" section
4. **Create animations:** Use natural language to describe animations

---

**Version:** 1.0.0
**Last Updated:** 2025-11-14
**Maintained By:** NeonWorks Team
**License:** See project LICENSE
