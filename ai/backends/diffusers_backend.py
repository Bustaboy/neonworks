"""
DiffusersBackend for Stable Diffusion Models

Supports local image generation using Stable Diffusion models via diffusers library.
"""

from typing import Optional

from PIL import Image

from .image_backend import ImageBackend, ImageBackendConfig


class DiffusersBackend(ImageBackend):
    """
    Backend for diffusers library (SD 1.5, SDXL, SD 3).

    Supports local image generation using Stable Diffusion models with
    optional GPU acceleration and memory optimizations.

    Features:
    - Auto-detection of model type (SD 1.5, SDXL, SD 3)
    - GPU layer offloading (CUDA)
    - Attention slicing for memory efficiency
    - VAE slicing for batch generation
    - Configurable resolution and inference steps

    Requirements:
    - diffusers package
    - torch with CUDA support
    - Pillow

    Example:
        >>> config = ImageBackendConfig(
        ...     backend_type='diffusers',
        ...     model_id='runwayml/stable-diffusion-v1-5',
        ...     width=512,
        ...     height=512
        ... )
        >>> backend = DiffusersBackend(config)
        >>> backend.load()
        >>> image = backend.generate("A beautiful landscape")
        >>> image.save("output.png")
        >>> backend.unload()
    """

    # VRAM estimates in GB for different model types
    VRAM_ESTIMATES = {
        "sd-1.5": 4.0,  # 4GB base
        "sdxl": 7.5,  # 7.5GB base
        "sd-3": 10.0,  # 10GB base (SD 3 Medium)
    }

    def __init__(self, config: ImageBackendConfig):
        """
        Initialize diffusers backend.

        Args:
            config: Backend configuration

        Raises:
            ValueError: If config is invalid
        """
        super().__init__(config)
        self.pipeline = None
        self._model_type = self._detect_model_type()

    def _detect_model_type(self) -> str:
        """
        Detect Stable Diffusion model type from model_id.

        Returns:
            Model type: 'sd-1.5', 'sdxl', or 'sd-3'
        """
        if not self.config.model_id:
            return "sd-1.5"  # Default

        model_id = self.config.model_id.lower()

        # SDXL detection
        if "xl" in model_id:
            return "sdxl"

        # SD 3 detection
        if "sd3" in model_id or "stable-diffusion-3" in model_id:
            return "sd-3"

        # Default to SD 1.5
        return "sd-1.5"

    def load(self) -> None:
        """
        Load Stable Diffusion pipeline via diffusers.

        Raises:
            ImportError: If diffusers not installed
            RuntimeError: If model loading fails
        """
        if self._loaded:
            return  # Already loaded

        try:
            # Import appropriate pipeline class
            if self._model_type == "sdxl":
                from diffusers import StableDiffusionXLPipeline

                PipelineClass = StableDiffusionXLPipeline
            elif self._model_type == "sd-3":
                from diffusers import StableDiffusion3Pipeline

                PipelineClass = StableDiffusion3Pipeline
            else:
                from diffusers import StableDiffusionPipeline

                PipelineClass = StableDiffusionPipeline

        except ImportError:
            raise ImportError(
                "diffusers library is required for DiffusersBackend.\n"
                "Install with: pip install diffusers"
            )

        try:
            import torch

            # Load model from Hugging Face Hub
            model_id = self.config.model_id or "runwayml/stable-diffusion-v1-5"

            self.pipeline = PipelineClass.from_pretrained(
                model_id, torch_dtype=torch.float16, use_safetensors=True
            )

            # Move to CUDA
            self.pipeline = self.pipeline.to("cuda")

            # Apply optimizations
            if self.config.enable_cpu_offload:
                self.pipeline.enable_model_cpu_offload()

            if self.config.enable_attention_slicing:
                self.pipeline.enable_attention_slicing()

            if self.config.enable_vae_slicing:
                self.pipeline.enable_vae_slicing()

            self._loaded = True

        except Exception as e:
            raise RuntimeError(f"Failed to load diffusers model '{model_id}': {e}")

    def unload(self) -> None:
        """
        Unload pipeline and free VRAM.
        """
        if not self._loaded:
            return  # Already unloaded

        # Delete pipeline
        if self.pipeline:
            del self.pipeline
            self.pipeline = None

        # Clear CUDA cache
        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
        except ImportError:
            pass  # torch not available, skip cleanup

        self._loaded = False

    def generate(self, prompt: str, negative_prompt: str = "", **kwargs) -> Image.Image:
        """
        Generate image using diffusers pipeline.

        Args:
            prompt: Text description of desired image
            negative_prompt: Text describing what to avoid
            **kwargs: Override generation params (width, height, num_inference_steps, etc.)

        Returns:
            PIL Image

        Raises:
            RuntimeError: If pipeline not loaded or generation fails
        """
        if not self._loaded or not self.pipeline:
            raise RuntimeError("Pipeline not loaded. Call load() first.")

        # Merge kwargs with config defaults
        gen_params = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": kwargs.get("width", self.config.width),
            "height": kwargs.get("height", self.config.height),
            "num_inference_steps": kwargs.get(
                "num_inference_steps", self.config.num_inference_steps
            ),
            "guidance_scale": kwargs.get("guidance_scale", self.config.guidance_scale),
        }

        try:
            result = self.pipeline(**gen_params)
            return result.images[0]  # Return first PIL Image

        except Exception as e:
            raise RuntimeError(f"Image generation failed: {e}")

    def get_vram_usage(self) -> float:
        """
        Get current VRAM usage in GB.

        Returns:
            VRAM usage in GB (0.0 if not loaded)
        """
        if not self._loaded:
            return 0.0

        try:
            # Try nvidia-smi first (most accurate)
            import subprocess

            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-compute-apps=used_memory",
                    "--format=csv,nounits,noheader",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                # Parse output (MB)
                used_mb = float(result.stdout.strip().split("\n")[0])
                return used_mb / 1024.0  # Convert to GB
        except Exception:
            pass  # Fall through to estimate

        # Fallback: Return estimated VRAM
        return self.get_required_vram()

    def get_required_vram(self) -> float:
        """
        Estimate required VRAM in GB.

        Returns:
            Estimated VRAM in GB
        """
        # Get base VRAM for model type
        base_vram = self.VRAM_ESTIMATES.get(self._model_type, 4.0)

        # Adjust for resolution
        pixels = self.config.width * self.config.height
        base_pixels = 512 * 512  # SD 1.5 base resolution
        resolution_factor = pixels / base_pixels

        # Add 30% overhead for higher resolutions
        if resolution_factor > 1.5:
            base_vram *= 1.3

        # Adjust for optimizations
        if self.config.enable_cpu_offload:
            base_vram *= 0.8  # ~20% savings

        if self.config.enable_attention_slicing:
            base_vram *= 0.7  # ~30% savings

        return base_vram
