"""
Stable Diffusion Sprite Generator

Generates game sprites from text descriptions using Stable Diffusion 1.5
with ControlNet for precise control over sprite generation.

Hardware Requirements:
- GPU: RTX 3060 / RX 6600 XT or better (6+ GB VRAM)
  - NVIDIA: CUDA support (RTX 20/30/40 series)
  - AMD: ROCm support (RX 6000/7000 series, MI series)
  - Apple: M1/M2/M3 with Metal Performance Shaders
- RAM: 16+ GB recommended
- Disk: 10+ GB for models

Features:
- Text-to-sprite generation
- ControlNet integration for pose control
- Sprite refinement and upscaling
- Batch generation
- Background removal
- Transparent PNG export

Author: NeonWorks Team
License: MIT
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import json

import torch
import numpy as np
from PIL import Image

# Stable Diffusion imports
try:
    from diffusers import (
        StableDiffusionPipeline,
        StableDiffusionControlNetPipeline,
        ControlNetModel,
        DDIMScheduler,
        DPMSolverMultistepScheduler,
    )
    from diffusers.utils import load_image
    DIFFUSERS_AVAILABLE = True
except ImportError:
    DIFFUSERS_AVAILABLE = False
    print("Warning: diffusers not available. Install with: pip install diffusers")

# Background removal
try:
    from rembg import remove
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False
    print("Warning: rembg not available. Install with: pip install rembg")


@dataclass
class SpriteGenerationConfig:
    """Configuration for sprite generation."""

    prompt: str
    negative_prompt: str = (
        "blurry, low quality, distorted, deformed, ugly, bad anatomy, "
        "watermark, signature, text, extra limbs, missing limbs"
    )
    width: int = 512
    height: int = 512
    num_inference_steps: int = 30
    guidance_scale: float = 7.5
    num_images: int = 1
    seed: Optional[int] = None

    # ControlNet settings
    use_controlnet: bool = False
    control_image: Optional[Image.Image] = None
    controlnet_conditioning_scale: float = 1.0

    # Post-processing
    remove_background: bool = True
    resize_to: Optional[Tuple[int, int]] = None
    sprite_style: str = "pixel-art"  # pixel-art, hand-drawn, anime, realistic

    # Quality settings
    scheduler_type: str = "dpm"  # ddim, dpm, euler
    enable_xformers: bool = True
    enable_vae_slicing: bool = True
    enable_attention_slicing: bool = True


@dataclass
class GeneratedSprite:
    """Container for generated sprite data."""

    image: Image.Image
    prompt: str
    seed: int
    metadata: Dict[str, Any]

    def save(self, path: str | Path):
        """Save sprite as PNG with metadata."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Save image
        self.image.save(str(path), "PNG")

        # Save metadata
        metadata_path = path.with_suffix('.json')
        with open(metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)

        print(f"Saved sprite to {path}")
        print(f"Saved metadata to {metadata_path}")


class SDSpriteGenerator:
    """
    Stable Diffusion-based sprite generator.

    Generates game sprites from text descriptions using SD 1.5 with
    optional ControlNet for pose control.

    Example:
        >>> generator = SDSpriteGenerator()
        >>> config = SpriteGenerationConfig(
        ...     prompt="fantasy knight character, pixel art style",
        ...     width=64,
        ...     height=64,
        ...     sprite_style="pixel-art"
        ... )
        >>> sprite = generator.generate(config)
        >>> sprite.save("assets/characters/knight.png")
    """

    def __init__(
        self,
        model_id: str = "runwayml/stable-diffusion-v1-5",
        controlnet_model_id: Optional[str] = "lllyasviel/control_v11p_sd15_openpose",
        device: Optional[str] = None,
        use_safetensors: bool = True,
        cache_dir: Optional[str] = None
    ):
        """
        Initialize Stable Diffusion sprite generator.

        Args:
            model_id: HuggingFace model ID for SD
            controlnet_model_id: Model ID for ControlNet (optional)
            device: Device to use (cuda/cpu), auto-detects if None
            use_safetensors: Use safetensors format for safety
            cache_dir: Directory to cache models
        """
        if not DIFFUSERS_AVAILABLE:
            raise ImportError(
                "diffusers is required for SD sprite generation. "
                "Install with: pip install diffusers transformers accelerate"
            )

        self.model_id = model_id
        self.controlnet_model_id = controlnet_model_id
        self.device = device or self._detect_device()
        self.cache_dir = Path(cache_dir) if cache_dir else Path("models/stable-diffusion")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        print(f"Initializing SD Sprite Generator on {self.device}...")

        # Load models
        self.pipe = None
        self.controlnet_pipe = None
        self._load_base_model(use_safetensors)

        # Style prompts for different sprite styles
        self.style_prompts = {
            "pixel-art": "pixel art, 16-bit, retro game sprite, clean pixels, no blur",
            "hand-drawn": "hand-drawn, illustrated, game art, clean lines",
            "anime": "anime style, cel-shaded, vibrant colors, clean art",
            "realistic": "realistic, detailed, high quality rendering",
            "chibi": "chibi style, cute, SD proportions, game sprite",
            "isometric": "isometric view, 3D rendered sprite, game asset",
        }

    def _detect_device(self) -> str:
        """
        Detect best available device.

        Supports:
        - NVIDIA GPUs (CUDA)
        - AMD GPUs (ROCm)
        - Apple Silicon (MPS)
        - CPU fallback
        """
        # Check for NVIDIA CUDA
        if torch.cuda.is_available():
            # Check if it's actually ROCm (AMD GPU)
            try:
                # ROCm uses CUDA API but reports as 'hip'
                device_name = torch.cuda.get_device_name(0).lower()
                if 'amd' in device_name or 'radeon' in device_name:
                    print(f"Detected AMD GPU (ROCm): {torch.cuda.get_device_name(0)}")
                    return "cuda"  # ROCm uses CUDA API
                else:
                    print(f"Detected NVIDIA GPU: {torch.cuda.get_device_name(0)}")
                    return "cuda"
            except Exception:
                return "cuda"

        # Check for Apple Silicon
        elif torch.backends.mps.is_available():
            print("Detected Apple Silicon GPU (MPS)")
            return "mps"

        # Fallback to CPU
        else:
            print("No GPU detected, using CPU")
            return "cpu"

    def _load_base_model(self, use_safetensors: bool):
        """Load base Stable Diffusion model."""
        print(f"Loading base model: {self.model_id}")

        try:
            self.pipe = StableDiffusionPipeline.from_pretrained(
                self.model_id,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                use_safetensors=use_safetensors,
                cache_dir=str(self.cache_dir),
                safety_checker=None,  # Disable for game sprites
            )

            # Move to device
            self.pipe = self.pipe.to(self.device)

            # Memory optimizations
            if self.device == "cuda":
                try:
                    self.pipe.enable_xformers_memory_efficient_attention()
                    print("Enabled xFormers memory efficient attention")
                except Exception:
                    print("xFormers not available, using default attention")

                self.pipe.enable_vae_slicing()
                self.pipe.enable_attention_slicing(1)

            print(f"Base model loaded successfully on {self.device}")

        except Exception as e:
            print(f"Error loading base model: {e}")
            print("You may need to run: huggingface-cli login")
            raise

    def _load_controlnet(self):
        """Load ControlNet model on demand."""
        if self.controlnet_pipe is not None:
            return

        if not self.controlnet_model_id:
            raise ValueError("ControlNet model ID not specified")

        print(f"Loading ControlNet: {self.controlnet_model_id}")

        try:
            controlnet = ControlNetModel.from_pretrained(
                self.controlnet_model_id,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                cache_dir=str(self.cache_dir),
            )

            self.controlnet_pipe = StableDiffusionControlNetPipeline.from_pretrained(
                self.model_id,
                controlnet=controlnet,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                use_safetensors=True,
                cache_dir=str(self.cache_dir),
                safety_checker=None,
            )

            self.controlnet_pipe = self.controlnet_pipe.to(self.device)

            # Memory optimizations
            if self.device == "cuda":
                try:
                    self.controlnet_pipe.enable_xformers_memory_efficient_attention()
                except Exception:
                    pass
                self.controlnet_pipe.enable_vae_slicing()
                self.controlnet_pipe.enable_attention_slicing(1)

            print("ControlNet loaded successfully")

        except Exception as e:
            print(f"Error loading ControlNet: {e}")
            raise

    def _enhance_prompt(self, prompt: str, style: str) -> str:
        """Enhance prompt with style-specific keywords."""
        style_enhancement = self.style_prompts.get(style, "")

        # Combine prompt with style
        enhanced = f"{prompt}, {style_enhancement}"

        # Add quality boosters
        enhanced += ", high quality, clean, sharp, game sprite"

        return enhanced

    def _get_scheduler(self, scheduler_type: str):
        """Get scheduler based on type."""
        schedulers = {
            "ddim": DDIMScheduler,
            "dpm": DPMSolverMultistepScheduler,
        }

        scheduler_class = schedulers.get(scheduler_type, DPMSolverMultistepScheduler)
        return scheduler_class.from_config(self.pipe.scheduler.config)

    def generate(self, config: SpriteGenerationConfig) -> List[GeneratedSprite]:
        """
        Generate sprites from configuration.

        Args:
            config: Sprite generation configuration

        Returns:
            List of generated sprites
        """
        # Enhance prompt with style
        enhanced_prompt = self._enhance_prompt(config.prompt, config.sprite_style)

        # Set seed for reproducibility
        if config.seed is not None:
            generator = torch.Generator(device=self.device).manual_seed(config.seed)
        else:
            generator = None

        # Choose pipeline
        if config.use_controlnet and config.control_image is not None:
            self._load_controlnet()
            pipe = self.controlnet_pipe
        else:
            pipe = self.pipe

        # Set scheduler
        pipe.scheduler = self._get_scheduler(config.scheduler_type)

        # Generate images
        print(f"Generating {config.num_images} sprite(s)...")
        print(f"Prompt: {enhanced_prompt}")

        try:
            if config.use_controlnet and config.control_image:
                # ControlNet generation
                output = pipe(
                    prompt=enhanced_prompt,
                    negative_prompt=config.negative_prompt,
                    image=config.control_image,
                    num_inference_steps=config.num_inference_steps,
                    guidance_scale=config.guidance_scale,
                    num_images_per_prompt=config.num_images,
                    generator=generator,
                    controlnet_conditioning_scale=config.controlnet_conditioning_scale,
                    width=config.width,
                    height=config.height,
                )
            else:
                # Standard generation
                output = pipe(
                    prompt=enhanced_prompt,
                    negative_prompt=config.negative_prompt,
                    num_inference_steps=config.num_inference_steps,
                    guidance_scale=config.guidance_scale,
                    num_images_per_prompt=config.num_images,
                    generator=generator,
                    width=config.width,
                    height=config.height,
                )

            images = output.images

        except Exception as e:
            print(f"Error during generation: {e}")
            raise

        # Post-process images
        sprites = []
        for i, image in enumerate(images):
            # Remove background if requested
            if config.remove_background and REMBG_AVAILABLE:
                image = self._remove_background(image)

            # Resize if requested
            if config.resize_to:
                image = image.resize(config.resize_to, Image.Resampling.LANCZOS)

            # Create sprite object
            seed = config.seed + i if config.seed is not None else None
            sprite = GeneratedSprite(
                image=image,
                prompt=enhanced_prompt,
                seed=seed,
                metadata={
                    "original_prompt": config.prompt,
                    "enhanced_prompt": enhanced_prompt,
                    "negative_prompt": config.negative_prompt,
                    "width": image.width,
                    "height": image.height,
                    "style": config.sprite_style,
                    "seed": seed,
                    "guidance_scale": config.guidance_scale,
                    "num_inference_steps": config.num_inference_steps,
                    "model": self.model_id,
                    "controlnet": config.use_controlnet,
                }
            )

            sprites.append(sprite)

        print(f"Generated {len(sprites)} sprite(s) successfully")
        return sprites

    def _remove_background(self, image: Image.Image) -> Image.Image:
        """Remove background from sprite."""
        try:
            # Convert to RGBA
            if image.mode != "RGBA":
                image = image.convert("RGBA")

            # Remove background
            output = remove(image)
            return output

        except Exception as e:
            print(f"Warning: Background removal failed: {e}")
            return image

    def generate_batch(
        self,
        prompts: List[str],
        base_config: SpriteGenerationConfig,
        output_dir: str | Path
    ) -> List[GeneratedSprite]:
        """
        Generate multiple sprites from a list of prompts.

        Args:
            prompts: List of text prompts
            base_config: Base configuration (will be copied per prompt)
            output_dir: Directory to save sprites

        Returns:
            List of all generated sprites
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        all_sprites = []

        for i, prompt in enumerate(prompts):
            print(f"\n[{i+1}/{len(prompts)}] Generating: {prompt}")

            # Create config for this prompt
            config = SpriteGenerationConfig(
                prompt=prompt,
                negative_prompt=base_config.negative_prompt,
                width=base_config.width,
                height=base_config.height,
                num_inference_steps=base_config.num_inference_steps,
                guidance_scale=base_config.guidance_scale,
                num_images=base_config.num_images,
                seed=base_config.seed + i if base_config.seed else None,
                remove_background=base_config.remove_background,
                resize_to=base_config.resize_to,
                sprite_style=base_config.sprite_style,
            )

            # Generate
            sprites = self.generate(config)

            # Save
            for j, sprite in enumerate(sprites):
                filename = f"sprite_{i:03d}_{j:02d}.png"
                sprite.save(output_dir / filename)

            all_sprites.extend(sprites)

        print(f"\nBatch generation complete: {len(all_sprites)} total sprites")
        return all_sprites

    def generate_character_set(
        self,
        character_prompt: str,
        animations: List[str],
        output_dir: str | Path,
        config: Optional[SpriteGenerationConfig] = None
    ) -> Dict[str, List[GeneratedSprite]]:
        """
        Generate a complete character sprite set for multiple animations.

        Args:
            character_prompt: Base character description
            animations: List of animation names (idle, walk, attack, etc.)
            output_dir: Directory to save sprites
            config: Base configuration (optional)

        Returns:
            Dictionary mapping animation names to sprite lists
        """
        if config is None:
            config = SpriteGenerationConfig(
                prompt="",
                width=64,
                height=64,
                sprite_style="pixel-art",
                num_images=4,  # 4 frames per animation
            )

        output_dir = Path(output_dir)
        character_set = {}

        for animation in animations:
            print(f"\nGenerating {animation} animation...")

            # Create animation-specific prompt
            anim_prompt = f"{character_prompt}, {animation} animation pose"
            config.prompt = anim_prompt

            # Generate frames
            sprites = self.generate(config)

            # Save to animation subdirectory
            anim_dir = output_dir / animation
            anim_dir.mkdir(parents=True, exist_ok=True)

            for i, sprite in enumerate(sprites):
                sprite.save(anim_dir / f"frame_{i:02d}.png")

            character_set[animation] = sprites

        print(f"\nCharacter set complete: {len(character_set)} animations")
        return character_set

    def cleanup(self):
        """Free up GPU memory."""
        if self.pipe is not None:
            del self.pipe
            self.pipe = None

        if self.controlnet_pipe is not None:
            del self.controlnet_pipe
            self.controlnet_pipe = None

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        print("Cleaned up GPU memory")


# Convenience functions

def generate_sprite(
    prompt: str,
    style: str = "pixel-art",
    size: Tuple[int, int] = (64, 64),
    output_path: Optional[str] = None,
    **kwargs
) -> GeneratedSprite:
    """
    Quick sprite generation function.

    Args:
        prompt: Text description of sprite
        style: Sprite style (pixel-art, hand-drawn, anime, etc.)
        size: Output size (width, height)
        output_path: Path to save sprite (optional)
        **kwargs: Additional config parameters

    Returns:
        Generated sprite

    Example:
        >>> sprite = generate_sprite(
        ...     "fantasy wizard character",
        ...     style="pixel-art",
        ...     size=(64, 64)
        ... )
    """
    generator = SDSpriteGenerator()

    config = SpriteGenerationConfig(
        prompt=prompt,
        width=size[0],
        height=size[1],
        sprite_style=style,
        **kwargs
    )

    sprites = generator.generate(config)
    sprite = sprites[0]

    if output_path:
        sprite.save(output_path)

    generator.cleanup()
    return sprite


if __name__ == "__main__":
    # Example usage
    print("SD Sprite Generator - Example Usage\n")

    if not DIFFUSERS_AVAILABLE:
        print("Please install diffusers: pip install diffusers transformers accelerate")
        exit(1)

    # Create generator
    generator = SDSpriteGenerator()

    # Generate a single sprite
    config = SpriteGenerationConfig(
        prompt="fantasy knight character with sword and shield",
        width=128,
        height=128,
        sprite_style="pixel-art",
        num_inference_steps=20,  # Lower for faster generation
        seed=42,
    )

    sprites = generator.generate(config)
    sprites[0].save("test_sprite.png")

    # Cleanup
    generator.cleanup()

    print("\nExample complete!")
