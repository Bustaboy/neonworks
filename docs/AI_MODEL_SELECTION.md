# AI Model Selection Guide for Animation System

**Version:** 1.0.0
**Target:** Consumer-grade hardware (8-16GB RAM, mid-range GPU optional)
**Focus:** Local execution, privacy, no API costs

---

## Table of Contents

1. [LLM Models for Natural Language Interpretation](#llm-models)
2. [Computer Vision Models for Animation Generation](#cv-models)
3. [Hardware Requirements](#hardware-requirements)
4. [Implementation Examples](#implementation-examples)
5. [Performance Optimization](#performance-optimization)
6. [Recommended Configurations](#recommended-configurations)

---

## LLM Models for Natural Language Interpretation

The LLM's job is simple: parse animation requests and return structured JSON. We don't need GPT-4 level intelligence for this.

### 🥇 Recommended: Llama 3.2 (3B)

**Best overall choice for this task**

```
Model: Meta-Llama-3.2-3B-Instruct
Size: ~3.2 GB (4-bit quantized)
RAM: 4-6 GB
Speed: ~20-50 tokens/sec on CPU
License: Open source (Meta License)
```

**Why it's perfect:**
- Small enough to run on CPU
- Excellent instruction following
- Fast inference
- Great JSON output reliability
- Recent model (2024) with good reasoning

**Installation:**
```bash
pip install llama-cpp-python

# Download model (4-bit quantized)
wget https://huggingface.co/TheBloke/Llama-3.2-3B-Instruct-GGUF/resolve/main/llama-3.2-3b-instruct-q4_k_m.gguf
```

**Usage:**
```python
from llama_cpp import Llama

llm = Llama(
    model_path="models/llama-3.2-3b-instruct-q4_k_m.gguf",
    n_ctx=2048,
    n_threads=4
)

prompt = """Parse this animation request into JSON:
"Make character walk slowly like they're tired"

Return JSON with: animation_type, style_modifiers, intensity (0-1), speed_multiplier
"""

response = llm(prompt, max_tokens=200, temperature=0.3)
```

---

### 🥈 Alternative: Phi-3 Mini (3.8B)

**Microsoft's compact powerhouse**

```
Model: Phi-3-mini-4k-instruct
Size: ~2.3 GB (4-bit quantized)
RAM: 4-5 GB
Speed: ~30-60 tokens/sec on CPU
License: MIT (very permissive)
```

**Advantages:**
- Smallest footprint
- Fastest inference
- Excellent for structured output
- MIT license (use anywhere)

**Best for:**
- Lower-end hardware
- When speed is critical
- Commercial projects needing permissive license

**Installation:**
```bash
pip install transformers accelerate

# Or use GGUF version with llama.cpp
wget https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf
```

---

### 🥉 Budget Option: TinyLlama 1.1B

**For very limited hardware**

```
Model: TinyLlama-1.1B-Chat
Size: ~700 MB (4-bit quantized)
RAM: 2-3 GB
Speed: ~50-100 tokens/sec on CPU
License: Apache 2.0
```

**When to use:**
- 8GB RAM or less
- No GPU available
- Older/slower CPUs
- Mobile/embedded deployment

**Trade-off:** Less reliable on complex requests, but sufficient for simple parsing.

---

### 📊 LLM Comparison Table

| Model | Size (4-bit) | RAM | CPU Speed | Accuracy | License |
|-------|--------------|-----|-----------|----------|---------|
| **Llama 3.2 (3B)** | 3.2 GB | 6 GB | 30 tok/s | ⭐⭐⭐⭐⭐ | Meta |
| **Phi-3 Mini** | 2.3 GB | 5 GB | 50 tok/s | ⭐⭐⭐⭐⭐ | MIT |
| **TinyLlama** | 700 MB | 3 GB | 80 tok/s | ⭐⭐⭐ | Apache 2.0 |
| **Qwen 2.5 (3B)** | 3.5 GB | 6 GB | 25 tok/s | ⭐⭐⭐⭐ | Apache 2.0 |

---

## Computer Vision Models for Animation Generation

This is more challenging. We need models that can generate sprite animations from static images.

### 🎨 Approach 1: Stable Diffusion + ControlNet (Recommended)

**Best for: High-quality sprite animations**

```
Model: Stable Diffusion 1.5 + ControlNet
Size: ~4 GB (SD) + ~1.4 GB (ControlNet)
VRAM: 6-8 GB (GPU required)
RAM: 8 GB
Speed: ~5-10 seconds per frame
```

**Why it works:**
- ControlNet preserves character structure
- Can generate consistent frames
- Huge community and models
- Pixel art fine-tunes available

**Installation:**
```bash
pip install diffusers transformers accelerate

# Will download models automatically
```

**Usage for Animation:**
```python
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel
import torch

# Load ControlNet for pose/edge preservation
controlnet = ControlNetModel.from_pretrained(
    "lllyasviel/control_v11p_sd15_openpose",
    torch_dtype=torch.float16
)

pipe = StableDiffusionControlNetPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    controlnet=controlnet,
    torch_dtype=torch.float16
).to("cuda")

# Generate animation frame
for i in range(frame_count):
    # Extract pose/structure from previous frame
    control_image = extract_pose(base_sprite, progress=i/frame_count)

    # Generate with consistent character
    frame = pipe(
        prompt="pixel art character walking, 32x64, game sprite",
        image=control_image,
        num_inference_steps=20,
        guidance_scale=7.5
    ).images[0]
```

**Best Models:**
- `stable-diffusion-v1-5` (general purpose)
- `sd-pokemon-diffusers` (pixel art style)
- `pixel-art-xl` (dedicated pixel art)

---

### 🎬 Approach 2: AnimateDiff (Recommended for Motion)

**Best for: Motion consistency**

```
Model: AnimateDiff v3
Size: ~5 GB
VRAM: 8 GB
RAM: 12 GB
Speed: ~30 seconds for 8-frame animation
```

**Advantages:**
- Designed specifically for animation
- Temporal consistency built-in
- Works with Stable Diffusion checkpoints
- Can use LoRA for pixel art

**Installation:**
```bash
pip install animatediff

# Or use ComfyUI with AnimateDiff nodes
```

**Usage:**
```python
from animatediff import AnimateDiffPipeline

pipe = AnimateDiffPipeline.from_pretrained(
    "guoyww/animatediff-motion-adapter-v1-5-2",
    torch_dtype=torch.float16
).to("cuda")

# Generate 8-frame walk cycle
frames = pipe(
    prompt="pixel art character walking, side view, game sprite, 32x64",
    num_frames=8,
    num_inference_steps=25,
    guidance_scale=7.5
).frames
```

---

### 🚀 Approach 3: EbSynth-inspired Optical Flow (Lightweight)

**Best for: CPU-only systems**

```
Model: RAFT optical flow
Size: ~50 MB
VRAM: Not required (CPU)
RAM: 4 GB
Speed: ~1-2 seconds per frame
```

**How it works:**
1. Generate 2-3 key frames manually or with simple procedural
2. Use optical flow to interpolate between them
3. Much faster and lighter than diffusion

**Installation:**
```bash
pip install opencv-python numpy
```

**Usage:**
```python
import cv2
import numpy as np

def interpolate_frames(keyframe1, keyframe2, num_frames=4):
    """Generate intermediate frames using optical flow"""
    # Calculate optical flow
    flow = cv2.calcOpticalFlowFarneback(
        cv2.cvtColor(keyframe1, cv2.COLOR_RGBA2GRAY),
        cv2.cvtColor(keyframe2, cv2.COLOR_RGBA2GRAY),
        None, 0.5, 3, 15, 3, 5, 1.2, 0
    )

    frames = [keyframe1]
    for i in range(1, num_frames):
        alpha = i / num_frames
        # Warp frame based on flow
        warped = warp_image(keyframe1, flow * alpha)
        # Blend with second keyframe
        frame = cv2.addWeighted(warped, 1-alpha, keyframe2, alpha, 0)
        frames.append(frame)

    return frames
```

**Best for:**
- Limited hardware
- Fast iteration
- Predictable results

---

### 🎯 Approach 4: Sprite-specific GANs (Future/Research)

**Custom trained models**

```
Model: Custom trained on sprite datasets
Size: ~500 MB - 2 GB
VRAM: 4-6 GB
Training time: 1-2 days on consumer GPU
```

**Training approach:**
1. Collect sprite animation dataset (5000+ animations)
2. Train conditional GAN or VAE
3. Condition on: animation type, style, frame number
4. Generate frame-by-frame

**Frameworks:**
- StyleGAN3 (NVIDIA)
- VQGAN (better for pixel art)
- Diffusion models (fine-tuned)

---

## Hardware Requirements

### 💻 Minimum Specs (LLM Only)

```
CPU: Dual-core 2.0 GHz+
RAM: 8 GB
GPU: Not required
Storage: 5 GB
OS: Windows/Linux/Mac

Capabilities:
✓ Natural language interpretation
✓ Procedural animation generation
✗ AI-generated frames
```

**Best Models:**
- LLM: TinyLlama 1.1B or Phi-3 Mini
- Animation: Procedural only (current implementation)

---

### 🎮 Recommended Specs (Full AI Pipeline)

```
CPU: Quad-core 3.0 GHz+ (Intel i5/Ryzen 5)
RAM: 16 GB
GPU: NVIDIA RTX 3060 (8GB VRAM) or better
Storage: 20 GB
OS: Windows/Linux

Capabilities:
✓ Natural language interpretation
✓ AI-generated sprite frames
✓ Real-time preview
✓ Batch processing
```

**Best Models:**
- LLM: Llama 3.2 (3B) or Phi-3 Mini
- Animation: Stable Diffusion + ControlNet or AnimateDiff

---

### 🚀 Optimal Specs (Professional Workflow)

```
CPU: 8-core 3.5 GHz+ (Intel i7/Ryzen 7)
RAM: 32 GB
GPU: NVIDIA RTX 4070 (12GB VRAM) or RTX 4090
Storage: 50 GB SSD
OS: Linux (best performance) or Windows

Capabilities:
✓ All features
✓ Fast generation (5-10 sec per animation)
✓ Multiple models loaded simultaneously
✓ Large batch processing
```

**Best Models:**
- LLM: Llama 3.2 (3B) for speed, or Llama 3.1 (8B) for quality
- Animation: AnimateDiff + multiple LoRAs

---

## Implementation Examples

### Example 1: Llama 3.2 Integration

```python
# File: editor/ai_animation_interpreter.py

from llama_cpp import Llama
import json

class AnimationInterpreter:
    def __init__(self, model_type="local"):
        self.model_type = model_type

        if model_type in ["local", "hybrid"]:
            self.llm = Llama(
                model_path="models/llama-3.2-3b-instruct-q4_k_m.gguf",
                n_ctx=2048,
                n_threads=4,  # Adjust based on CPU cores
                n_gpu_layers=0  # 0 for CPU, 35 for full GPU offload
            )

    def _interpret_with_llm(self, user_request: str, context: Optional[Dict] = None) -> AnimationIntent:
        """Interpret using Llama 3.2"""

        prompt = f"""You are an animation specialist. Parse this request into JSON:

Request: "{user_request}"

Available animations: idle, walk, run, attack, cast_spell, hurt, death, jump

Available styles: slow, fast, sneaky, aggressive, happy, sad, tired, energetic

Return ONLY valid JSON in this format:
{{
    "animation_type": "walk",
    "style_modifiers": ["slow", "tired"],
    "intensity": 0.5,
    "speed_multiplier": 0.7,
    "special_effects": [],
    "frame_count": null,
    "confidence": 0.9
}}

JSON:"""

        # Generate response
        response = self.llm(
            prompt,
            max_tokens=256,
            temperature=0.2,  # Low temp for consistent JSON
            stop=["}", "}}", "\n\n"],  # Stop at JSON end
            echo=False
        )

        # Extract JSON
        text = response["choices"][0]["text"]

        # Parse JSON
        try:
            # Add closing brace if missing
            if not text.strip().endswith("}"):
                text += "}"

            data = json.loads(text)
            return AnimationIntent(**data)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"LLM JSON parse error: {e}")
            # Fallback to rule-based
            return self._interpret_local(user_request, context)
```

---

### Example 2: Stable Diffusion Animation

```python
# File: editor/ai_animator.py

from diffusers import StableDiffusionControlNetPipeline, ControlNetModel
from diffusers import UniPCMultistepScheduler
import torch
from PIL import Image
import numpy as np

class AIAnimator:
    def __init__(self, model_type="local"):
        self.model_type = model_type
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        if model_type != "procedural":
            self._init_sd_model()

    def _init_sd_model(self):
        """Initialize Stable Diffusion + ControlNet"""
        print("Loading Stable Diffusion model...")

        # Load ControlNet for structure preservation
        controlnet = ControlNetModel.from_pretrained(
            "lllyasviel/control_v11p_sd15_canny",
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
        )

        # Load SD pipeline
        self.sd_pipe = StableDiffusionControlNetPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            controlnet=controlnet,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            safety_checker=None  # Disable for speed
        ).to(self.device)

        # Use faster scheduler
        self.sd_pipe.scheduler = UniPCMultistepScheduler.from_config(
            self.sd_pipe.scheduler.config
        )

        # Enable optimizations
        if self.device == "cuda":
            self.sd_pipe.enable_attention_slicing()  # Reduce VRAM
            self.sd_pipe.enable_vae_slicing()        # Reduce VRAM
            # self.sd_pipe.enable_xformers_memory_efficient_attention()  # Optional

        print("Model loaded successfully!")

    def _generate_with_sd(
        self,
        source_image: pygame.Surface,
        config: AnimationConfig
    ) -> List[pygame.Surface]:
        """Generate animation using Stable Diffusion"""

        frames = []

        # Convert pygame surface to PIL
        source_pil = self._pygame_to_pil(source_image)
        w, h = source_pil.size

        # Generate prompt
        base_prompt = f"pixel art character {config.animation_type}, game sprite, {w}x{h}"

        # Add style modifiers to prompt
        if config.style == "bouncy":
            base_prompt += ", dynamic, energetic"
        elif config.style == "smooth":
            base_prompt += ", fluid, graceful"

        for i in range(config.frame_count):
            progress = i / max(1, config.frame_count - 1)

            # Create control image (edge detection)
            control_image = self._create_control_image(
                source_pil,
                progress,
                config
            )

            # Generate frame
            result = self.sd_pipe(
                prompt=base_prompt,
                image=control_image,
                num_inference_steps=20,  # Lower = faster, higher = quality
                guidance_scale=7.5,
                controlnet_conditioning_scale=0.8,  # How much to follow control
                height=h,
                width=w,
                generator=torch.Generator(device=self.device).manual_seed(42 + i)
            )

            frame_pil = result.images[0]

            # Convert back to pygame
            frame_pygame = self._pil_to_pygame(frame_pil)
            frames.append(frame_pygame)

            print(f"Generated frame {i+1}/{config.frame_count}")

        return frames

    def _create_control_image(
        self,
        source: Image.Image,
        progress: float,
        config: AnimationConfig
    ) -> Image.Image:
        """Create control image with animation transform"""
        import cv2

        # Convert to numpy
        img_array = np.array(source)

        # Apply animation-specific transform
        if config.animation_type == "walk":
            # Shift image slightly based on progress
            shift_x = int(np.sin(progress * np.pi * 2) * 3 * config.intensity)
            shift_y = int(np.sin(progress * np.pi * 2) * 2 * config.intensity)

            M = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
            img_array = cv2.warpAffine(img_array, M, (img_array.shape[1], img_array.shape[0]))

        # Canny edge detection
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 100, 200)

        # Convert to RGB
        edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)

        return Image.fromarray(edges_rgb)

    def _pygame_to_pil(self, surface: pygame.Surface) -> Image.Image:
        """Convert pygame surface to PIL Image"""
        size = surface.get_size()
        mode = "RGBA"
        data = pygame.image.tostring(surface, mode)
        return Image.frombytes(mode, size, data)

    def _pil_to_pygame(self, pil_image: Image.Image) -> pygame.Surface:
        """Convert PIL Image to pygame surface"""
        mode = pil_image.mode
        size = pil_image.size
        data = pil_image.tobytes()
        return pygame.image.fromstring(data, size, mode)
```

---

### Example 3: Phi-3 Mini Integration (Transformers)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class AnimationInterpreter:
    def __init__(self, model_type="local"):
        if model_type == "local":
            self._init_phi3()

    def _init_phi3(self):
        """Initialize Phi-3 Mini"""
        model_name = "microsoft/Phi-3-mini-4k-instruct"

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto",
            trust_remote_code=True
        )

    def _interpret_with_phi3(self, user_request: str) -> AnimationIntent:
        """Interpret using Phi-3"""

        messages = [
            {"role": "system", "content": "You are an animation parser. Return only JSON."},
            {"role": "user", "content": f"Parse: '{user_request}' into animation JSON"}
        ]

        # Format with chat template
        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        # Generate
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=200,
            temperature=0.2,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )

        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract JSON and parse
        # ... (similar to Llama example)
```

---

## Performance Optimization

### LLM Optimization

```python
# 1. Quantization (smaller model size)
from llama_cpp import Llama

llm = Llama(
    model_path="model-q4_k_m.gguf",  # 4-bit quantized
    # Options: q2, q3, q4, q5, q6, q8
    # Lower = smaller/faster but less accurate
)

# 2. Thread optimization
llm = Llama(
    model_path="model.gguf",
    n_threads=8,  # Match your CPU core count
    n_batch=512   # Larger = faster but more RAM
)

# 3. GPU acceleration (if available)
llm = Llama(
    model_path="model.gguf",
    n_gpu_layers=35  # Offload layers to GPU
    # Set to -1 for full GPU, or adjust based on VRAM
)

# 4. Context caching
llm = Llama(
    model_path="model.gguf",
    n_ctx=2048,      # Context size
    use_mlock=True   # Lock model in RAM (faster subsequent calls)
)
```

### Stable Diffusion Optimization

```python
from diffusers import StableDiffusionPipeline
import torch

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16  # Half precision (2x faster)
)

# Memory optimizations
pipe.enable_attention_slicing()      # 40% less VRAM
pipe.enable_vae_slicing()            # 20% less VRAM
pipe.enable_vae_tiling()             # For large images

# Speed optimizations
pipe.enable_xformers_memory_efficient_attention()  # 20% faster
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)  # Faster sampler

# Model CPU offload (if limited VRAM)
pipe.enable_model_cpu_offload()      # Use when VRAM < 8GB

# Sequential CPU offload (extreme VRAM saving)
pipe.enable_sequential_cpu_offload() # Use when VRAM < 4GB
```

---

## Recommended Configurations

### Configuration 1: Budget (No GPU)

```yaml
Hardware:
  CPU: Quad-core 2.5 GHz
  RAM: 8 GB
  GPU: None
  Storage: 10 GB

Software Stack:
  LLM: TinyLlama 1.1B (q4 quantized)
  Animation: Procedural only
  Framework: llama-cpp-python

Performance:
  Interpretation: ~2 seconds
  Animation: Instant (procedural)
  Memory: ~3 GB
```

**Setup:**
```bash
pip install llama-cpp-python
wget https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf -O models/tinyllama.gguf
```

---

### Configuration 2: Mainstream (Entry GPU)

```yaml
Hardware:
  CPU: Quad-core 3.0 GHz
  RAM: 16 GB
  GPU: NVIDIA GTX 1660 (6GB VRAM) or RTX 3060
  Storage: 20 GB

Software Stack:
  LLM: Phi-3 Mini 3.8B (q4 quantized)
  Animation: Stable Diffusion 1.5 + ControlNet
  Framework: llama-cpp + diffusers

Performance:
  Interpretation: ~1 second
  Animation: ~10 seconds per frame
  Full 6-frame animation: ~60 seconds
  Memory: ~8 GB RAM, 6 GB VRAM
```

**Setup:**
```bash
pip install llama-cpp-python diffusers transformers accelerate
pip install xformers  # Optional speed boost

# Download models
python scripts/download_models.py
```

---

### Configuration 3: Enthusiast (Modern GPU)

```yaml
Hardware:
  CPU: 8-core 3.5 GHz
  RAM: 32 GB
  GPU: NVIDIA RTX 4070 (12GB VRAM) or better
  Storage: 50 GB SSD

Software Stack:
  LLM: Llama 3.2 3B (full precision on GPU)
  Animation: AnimateDiff + SD 1.5 + LoRAs
  Framework: transformers + diffusers

Performance:
  Interpretation: <1 second
  Animation: ~5 seconds per frame
  Full 6-frame animation: ~30 seconds
  Memory: ~12 GB RAM, 10 GB VRAM
```

**Setup:**
```bash
# Full installation
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
pip install transformers diffusers accelerate xformers
pip install animatediff

# Download all models
python scripts/download_all_models.py
```

---

## Next Steps

1. **Choose your configuration** based on hardware
2. **Download models** using provided scripts
3. **Integrate** into existing AI animator code
4. **Test** with demo examples
5. **Fine-tune** for your specific use case

---

**Recommendation for NeonWorks:**

Start with **Configuration 2** (Mainstream):
- **LLM:** Phi-3 Mini (MIT license, fast, reliable)
- **Animation:** Stable Diffusion + ControlNet
- Works on most gaming PCs
- Good balance of quality and speed
- Can fall back to procedural if no GPU

Then provide **Configuration 1** as fallback for users without GPUs.

---

**Version:** 1.0.0
**Last Updated:** 2025-11-14
**Maintained By:** NeonWorks Team
