# AI Implementation Guide - Practical Integration

**Version:** 1.0.0
**Goal:** Step-by-step guide to integrate AI models into NeonWorks

---

## Quick Start Roadmap

### Phase 1: Natural Language Interpretation (Week 1)
**Hardware:** Any (CPU only)
**Models:** Phi-3 Mini (2.3 GB)
**Features:** LLM-powered animation request parsing

### Phase 2: Basic Sprite Generation (Week 2-3)
**Hardware:** GTX 1660 / RTX 3060 (6-8 GB VRAM)
**Models:** Stable Diffusion 1.5
**Features:** Text-to-sprite, simple animations

### Phase 3: Advanced Features (Week 4-6)
**Hardware:** RTX 4070 (12 GB VRAM)
**Models:** SDXL, AnimateDiff, ControlNet
**Features:** Multi-directional, physics, expressions

---

## Phase 1: LLM Integration (CPU-Friendly)

### Step 1: Install Dependencies

```bash
# Core dependencies
pip install llama-cpp-python

# Optional: For faster inference with GPU
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python --force-reinstall
```

### Step 2: Download Model

```bash
# Create models directory
mkdir -p models

# Download Phi-3 Mini (2.3 GB, 4-bit quantized)
wget https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf \
  -O models/phi-3-mini-q4.gguf

# Or download Llama 3.2 3B (3.2 GB)
wget https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf \
  -O models/llama-3.2-3b-q4.gguf
```

### Step 3: Update AnimationInterpreter

```python
# File: editor/ai_animation_interpreter.py

from llama_cpp import Llama
import json
import re

class AnimationInterpreter:
    def __init__(self, model_type="local"):
        self.model_type = model_type

        if model_type in ["local", "hybrid"]:
            self._init_llm()

    def _init_llm(self):
        """Initialize local LLM"""
        import os

        # Auto-detect available model
        model_path = None
        if os.path.exists("models/phi-3-mini-q4.gguf"):
            model_path = "models/phi-3-mini-q4.gguf"
            print("Loading Phi-3 Mini...")
        elif os.path.exists("models/llama-3.2-3b-q4.gguf"):
            model_path = "models/llama-3.2-3b-q4.gguf"
            print("Loading Llama 3.2...")
        else:
            print("No LLM model found. Using rule-based fallback.")
            self.model_type = "fallback"
            return

        # Initialize llama.cpp
        self.llm = Llama(
            model_path=model_path,
            n_ctx=2048,          # Context window
            n_threads=4,         # CPU threads (adjust based on your CPU)
            n_gpu_layers=0,      # 0 for CPU, 35 for full GPU offload
            verbose=False
        )

        print(f"LLM loaded: {model_path}")

    def _interpret_api(self, user_request: str, context: Optional[Dict] = None) -> AnimationIntent:
        """Interpret using LLM (now actually works!)"""

        if not hasattr(self, 'llm') or self.llm is None:
            # Fallback to rule-based
            return self._interpret_local(user_request, context)

        # Build prompt
        prompt = self._build_llm_prompt_v2(user_request, context)

        try:
            # Generate response
            response = self.llm(
                prompt,
                max_tokens=300,
                temperature=0.3,      # Low temp for consistent output
                top_p=0.9,
                repeat_penalty=1.1,
                stop=["</s>", "\n\n\n"],  # Stop tokens
                echo=False
            )

            # Extract text
            text = response["choices"][0]["text"].strip()

            # Parse JSON
            intent = self._parse_llm_json(text)

            if intent:
                intent.confidence = 0.95  # High confidence for LLM
                print(f"[LLM] Interpreted: {intent}")
                return intent
            else:
                # JSON parsing failed, fallback
                print("[LLM] JSON parse failed, using fallback")
                return self._interpret_local(user_request, context)

        except Exception as e:
            print(f"[LLM] Error: {e}")
            return self._interpret_local(user_request, context)

    def _build_llm_prompt_v2(self, user_request: str, context: Optional[Dict] = None) -> str:
        """Build optimized prompt for LLM"""

        prompt = f"""<|system|>
You are an animation parameter generator. Parse user requests into JSON.

Available animation types: idle, walk, run, attack, cast_spell, hurt, death, jump

Available style modifiers:
- Speed: slow, fast, quick, sluggish
- Energy: tired, energetic, weak, powerful
- Emotion: happy, sad, angry, calm, scared
- Style: smooth, snappy, bouncy, sneaky

<|user|>
Parse this animation request into JSON format:

"{user_request}"

Respond with ONLY valid JSON in this exact format:
{{
  "animation_type": "walk",
  "style_modifiers": ["slow", "tired"],
  "intensity": 0.5,
  "speed_multiplier": 0.7,
  "special_effects": [],
  "frame_count": null
}}

<|assistant|>
{{"""

        return prompt

    def _parse_llm_json(self, text: str) -> Optional[AnimationIntent]:
        """Parse JSON from LLM response"""

        # Find JSON object
        json_match = re.search(r'\{[^}]+\}', text, re.DOTALL)

        if not json_match:
            return None

        json_str = json_match.group(0)

        # Add closing brace if missing
        if json_str.count('{') > json_str.count('}'):
            json_str += '}'

        try:
            data = json.loads(json_str)

            # Validate required fields
            if "animation_type" not in data:
                return None

            # Set defaults
            data.setdefault("style_modifiers", [])
            data.setdefault("intensity", 0.7)
            data.setdefault("speed_multiplier", 1.0)
            data.setdefault("special_effects", [])
            data.setdefault("frame_count", None)
            data.setdefault("confidence", 0.9)

            return AnimationIntent(**data)

        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            return None
```

### Step 4: Test LLM Integration

```python
# File: test_llm.py

from editor.ai_animation_interpreter import AnimationInterpreter

# Initialize with LLM
interpreter = AnimationInterpreter(model_type="local")

# Test various requests
test_requests = [
    "walk slowly",
    "aggressive attack",
    "sneaky movement",
    "happy jumping animation",
    "tired walk with 8 frames",
]

for request in test_requests:
    print(f"\nRequest: '{request}'")
    intent = interpreter.interpret_request(request)
    print(f"Result: {intent}")
    print(f"  Animation: {intent.animation_type}")
    print(f"  Modifiers: {intent.style_modifiers}")
    print(f"  Intensity: {intent.intensity}")
    print(f"  Speed: {intent.speed_multiplier}")
```

```bash
python test_llm.py
```

**Expected output:**
```
Loading Phi-3 Mini...
LLM loaded: models/phi-3-mini-q4.gguf

Request: 'walk slowly'
[LLM] Interpreted: AnimationIntent(animation_type='walk', ...)
Result: AnimationIntent(animation_type='walk', style_modifiers=['slow'], intensity=0.4, speed_multiplier=0.5, ...)
```

---

## Phase 2: Stable Diffusion Integration

### Step 1: Install Dependencies

```bash
# PyTorch with CUDA support
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Diffusers and dependencies
pip install diffusers transformers accelerate safetensors

# Optional optimizations
pip install xformers  # 20-30% speed boost
pip install opencv-python pillow
```

### Step 2: Update AIAnimator

```python
# File: editor/ai_animator.py

import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from PIL import Image
import pygame

class AIAnimator:
    def __init__(self, model_type="local"):
        self.model_type = model_type
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Initialize SD model
        if model_type in ["api", "hybrid"]:
            self._init_sd_model()

        print(f"AI Animator initialized (device: {self.device})")

    def _init_sd_model(self):
        """Initialize Stable Diffusion"""

        model_id = "runwayml/stable-diffusion-v1-5"

        print(f"Loading Stable Diffusion from {model_id}...")
        print("This may take a few minutes on first run...")

        # Load pipeline
        self.sd_pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            safety_checker=None,  # Disable for game sprites
            requires_safety_checker=False
        )

        # Move to device
        self.sd_pipe = self.sd_pipe.to(self.device)

        # Use faster scheduler
        self.sd_pipe.scheduler = DPMSolverMultistepScheduler.from_config(
            self.sd_pipe.scheduler.config
        )

        # Memory optimizations
        if self.device == "cuda":
            self.sd_pipe.enable_attention_slicing()
            self.sd_pipe.enable_vae_slicing()

            # If xformers installed
            try:
                self.sd_pipe.enable_xformers_memory_efficient_attention()
                print("xformers enabled")
            except:
                print("xformers not available (install for speed boost)")

        print("Stable Diffusion loaded successfully!")

    def generate_sprite_from_text(
        self,
        prompt: str,
        negative_prompt: str = "blurry, realistic, 3d, photo, low quality",
        width: int = 512,
        height: int = 512,
        num_inference_steps: int = 25,
        guidance_scale: float = 7.5,
    ) -> pygame.Surface:
        """
        Generate sprite from text description

        Args:
            prompt: What to generate
            negative_prompt: What to avoid
            width: Output width (will be downscaled to sprite size)
            height: Output height
            num_inference_steps: Quality (higher = better but slower)
            guidance_scale: How closely to follow prompt

        Returns:
            Generated sprite as pygame surface
        """

        if not hasattr(self, 'sd_pipe'):
            raise RuntimeError("Stable Diffusion not initialized")

        print(f"Generating: {prompt}")

        # Generate image
        with torch.inference_mode():
            result = self.sd_pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                height=height,
                width=width,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                generator=torch.Generator(device=self.device).manual_seed(42)
            )

        # Convert PIL to pygame
        pil_image = result.images[0]
        sprite = self._pil_to_pygame(pil_image)

        return sprite

    def _pil_to_pygame(self, pil_image: Image.Image) -> pygame.Surface:
        """Convert PIL Image to pygame surface"""
        mode = pil_image.mode
        size = pil_image.size
        data = pil_image.tobytes()

        surface = pygame.image.fromstring(data, size, mode)
        return surface

    def _pygame_to_pil(self, surface: pygame.Surface) -> Image.Image:
        """Convert pygame surface to PIL Image"""
        size = surface.get_size()
        mode = "RGBA"
        data = pygame.image.tostring(surface, mode)

        pil_image = Image.frombytes(mode, size, data)
        return pil_image
```

### Step 3: Test Sprite Generation

```python
# File: test_sd_generation.py

import pygame
from editor.ai_animator import AIAnimator

pygame.init()

# Initialize with SD
animator = AIAnimator(model_type="api")

# Generate test sprite
sprite = animator.generate_sprite_from_text(
    prompt="pixel art warrior character, front view, 32x64 game sprite, simple design",
    width=256,
    height=512,
    num_inference_steps=20  # Lower for faster testing
)

# Save result
pygame.image.save(sprite, "test_generated_sprite.png")
print("Sprite saved to test_generated_sprite.png")

# Display
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((50, 50, 50))

    # Draw generated sprite (centered, scaled up)
    scaled = pygame.transform.scale(sprite, (sprite.get_width() * 2, sprite.get_height() * 2))
    x = (800 - scaled.get_width()) // 2
    y = (600 - scaled.get_height()) // 2
    screen.blit(scaled, (x, y))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
```

```bash
python test_sd_generation.py
```

---

## Phase 3: Complete Integration

### Update ai_animator.py with all modes

```python
# File: editor/ai_animator.py (complete version)

class AIAnimator:
    def __init__(self, model_type="local"):
        """
        Initialize AI Animator

        Args:
            model_type:
                - "procedural": Fast, CPU-only, basic animations
                - "local": SD + procedural, GPU recommended
                - "api": Full SD with all features, GPU required
        """
        self.model_type = model_type
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Always available: procedural
        self.procedural_enabled = True

        # Optional: Stable Diffusion
        self.sd_enabled = False
        if model_type in ["local", "api", "hybrid"]:
            try:
                self._init_sd_model()
                self.sd_enabled = True
            except Exception as e:
                print(f"Could not load SD: {e}")
                print("Falling back to procedural only")

    def generate_animation(
        self,
        source_image: pygame.Surface,
        config: AnimationConfig,
        component_id: Optional[str] = None,
        use_ai: bool = True
    ) -> List[pygame.Surface]:
        """
        Generate animation frames

        Args:
            source_image: Static sprite
            config: Animation configuration
            component_id: For caching
            use_ai: If False, always use procedural

        Returns:
            List of animation frames
        """

        # Check cache
        if component_id:
            cached = self._load_from_cache(component_id, config.animation_type)
            if cached:
                return cached

        # Choose generation method
        if use_ai and self.sd_enabled:
            print(f"Generating {config.animation_type} with AI...")
            frames = self._generate_with_sd(source_image, config)
        else:
            print(f"Generating {config.animation_type} procedurally...")
            frames = self._generate_procedural(source_image, config)

        # Cache result
        if component_id:
            self._save_to_cache(component_id, config.animation_type, frames)

        return frames
```

### Update UI to support both modes

```python
# File: ui/ai_animator_ui.py

class AIAnimatorUI:
    def __init__(self, world, renderer):
        # ... existing code ...

        # Add mode selector
        self.mode_label = Label(
            text="Generation Mode:",
            x=self.panel_x + 20,
            y=self.panel_y + 580
        )

        self.mode_procedural_btn = Button(
            text="Procedural (Fast)",
            x=self.panel_x + 20,
            y=self.panel_y + 610,
            width=190,
            height=30,
            on_click=lambda: self._set_mode("procedural"),
            color=(100, 100, 200)
        )

        self.mode_ai_btn = Button(
            text="AI (Quality)",
            x=self.panel_x + 220,
            y=self.panel_y + 610,
            width=190,
            height=30,
            on_click=lambda: self._set_mode("ai"),
            color=(100, 200, 100)
        )

        self.current_mode = "procedural"

    def _set_mode(self, mode: str):
        """Switch generation mode"""
        self.current_mode = mode
        print(f"Switched to {mode} mode")

        # Update button colors to show selection
        if mode == "procedural":
            self.mode_procedural_btn.color = (100, 100, 255)
            self.mode_ai_btn.color = (100, 200, 100)
        else:
            self.mode_procedural_btn.color = (100, 100, 200)
            self.mode_ai_btn.color = (100, 255, 100)

    def _on_generate(self):
        """Generate animation with selected mode"""
        # ... existing validation ...

        # Generate with mode
        use_ai = (self.current_mode == "ai")

        self.current_animation_frames = self.animator.generate_animation(
            self.current_sprite,
            config,
            component_id=None,
            use_ai=use_ai
        )

        # ... rest of method ...
```

---

## Performance Optimization

### Config file for model settings

```python
# File: config/ai_models_config.py

AI_CONFIG = {
    # LLM settings
    "llm": {
        "model_path": "models/phi-3-mini-q4.gguf",
        "n_ctx": 2048,
        "n_threads": 4,  # Adjust for your CPU
        "n_gpu_layers": 0,  # 0 for CPU, 35 for GPU
    },

    # Stable Diffusion settings
    "sd": {
        "model_id": "runwayml/stable-diffusion-v1-5",
        "torch_dtype": "float16",  # or "float32" for CPU
        "num_inference_steps": 20,  # Lower = faster
        "guidance_scale": 7.5,

        # Memory optimizations
        "enable_attention_slicing": True,
        "enable_vae_slicing": True,
        "enable_xformers": True,  # If installed
    },

    # Hardware detection
    "auto_detect": True,  # Automatically choose best settings
}


def get_optimal_config():
    """Auto-detect hardware and return optimal config"""
    import torch

    config = AI_CONFIG.copy()

    # Check GPU
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        vram_gb = torch.cuda.get_device_properties(0).total_memory / 1e9

        print(f"Detected GPU: {gpu_name} ({vram_gb:.1f} GB VRAM)")

        # Adjust based on VRAM
        if vram_gb >= 12:
            # High-end GPU
            config["sd"]["num_inference_steps"] = 30
            config["llm"]["n_gpu_layers"] = 35
        elif vram_gb >= 8:
            # Mid-range GPU
            config["sd"]["num_inference_steps"] = 25
            config["llm"]["n_gpu_layers"] = 35
        elif vram_gb >= 6:
            # Entry GPU
            config["sd"]["num_inference_steps"] = 20
            config["sd"]["enable_model_cpu_offload"] = True
        else:
            # Low VRAM
            config["sd"]["num_inference_steps"] = 15
            config["sd"]["enable_sequential_cpu_offload"] = True

    else:
        print("No GPU detected, using CPU mode")
        config["sd"]["torch_dtype"] = "float32"
        config["sd"]["num_inference_steps"] = 15

    return config
```

---

## Testing Checklist

### ✅ Phase 1: LLM (Week 1)

- [ ] Install llama-cpp-python
- [ ] Download Phi-3 Mini or Llama 3.2
- [ ] Test LLM integration
- [ ] Verify JSON parsing works
- [ ] Test 10+ different prompts
- [ ] Measure inference speed (should be <2 seconds)

### ✅ Phase 2: SD (Week 2)

- [ ] Install PyTorch with CUDA
- [ ] Install diffusers
- [ ] Download SD 1.5 model (auto-downloads)
- [ ] Test sprite generation
- [ ] Verify VRAM usage
- [ ] Test different prompts
- [ ] Measure generation speed

### ✅ Phase 3: Integration (Week 3)

- [ ] Update AIAnimator with both modes
- [ ] Update UI with mode selector
- [ ] Test procedural mode
- [ ] Test AI mode
- [ ] Test mode switching
- [ ] Create example animations
- [ ] Export and verify results

---

## Troubleshooting

### Issue: "CUDA out of memory"

**Solutions:**
```python
# Reduce batch size or resolution
sprite = animator.generate_sprite_from_text(
    prompt="...",
    width=256,   # Reduced from 512
    height=256,
    num_inference_steps=15  # Reduced from 25
)

# Enable memory-efficient attention
pipe.enable_attention_slicing()
pipe.enable_model_cpu_offload()  # Offload to RAM when not in use
```

### Issue: LLM is slow

**Solutions:**
```python
# Reduce context window
llm = Llama(
    model_path="...",
    n_ctx=1024,  # Reduced from 2048
    n_threads=8,  # Increase threads
)

# Use smaller model
# Switch from Llama 3.2 3B → TinyLlama 1.1B
```

### Issue: JSON parsing fails

**Check:**
- Print raw LLM output to debug
- Adjust temperature (lower = more consistent)
- Simplify prompt
- Add more stop tokens

---

## Next Steps

1. **Complete Phase 1** (LLM integration)
2. **Test thoroughly** with various prompts
3. **Measure performance** on your hardware
4. **Proceed to Phase 2** if GPU available
5. **Document user workflow** for your team

---

**Version:** 1.0.0
**Last Updated:** 2025-11-14
**Maintained By:** NeonWorks Team
