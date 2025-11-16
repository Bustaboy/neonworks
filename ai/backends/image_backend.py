"""
Image Backend Abstract Base Class

Provides unified interface for image generation across different providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from PIL import Image


@dataclass
class ImageBackendConfig:
    """
    Configuration for image generation backends.

    Attributes:
        backend_type: Backend type ('diffusers', 'comfyui', etc.)
        model_id: Model identifier (e.g., 'stabilityai/stable-diffusion-xl-base-1.0')
        model_path: Path to local model file (for custom models)
        width: Image width in pixels
        height: Image height in pixels
        num_inference_steps: Number of denoising steps
        guidance_scale: Classifier-free guidance scale
        enable_cpu_offload: Enable model CPU offloading to save VRAM
        enable_attention_slicing: Enable attention slicing to save VRAM
        enable_vae_slicing: Enable VAE slicing for batch generation

    Example:
        >>> config = ImageBackendConfig(
        ...     backend_type='diffusers',
        ...     model_id='runwayml/stable-diffusion-v1-5',
        ...     width=512,
        ...     height=512
        ... )
    """

    backend_type: str
    model_id: Optional[str] = None
    model_path: Optional[str] = None
    width: int = 512
    height: int = 512
    num_inference_steps: int = 30
    guidance_scale: float = 7.5
    enable_cpu_offload: bool = False
    enable_attention_slicing: bool = True
    enable_vae_slicing: bool = True

    def __post_init__(self):
        """Validate configuration after initialization."""
        # Validate backend_type
        valid_types = {"diffusers", "comfyui"}
        if self.backend_type not in valid_types:
            raise ValueError(
                f"Invalid backend_type '{self.backend_type}'. " f"Must be one of: {valid_types}"
            )

        # Validate dimensions
        if self.width <= 0:
            raise ValueError(f"width must be positive, got {self.width}")

        if self.height <= 0:
            raise ValueError(f"height must be positive, got {self.height}")

        # Validate inference steps
        if self.num_inference_steps <= 0:
            raise ValueError(
                f"num_inference_steps must be positive, got {self.num_inference_steps}"
            )


class ImageBackend(ABC):
    """
    Abstract base class for image generation backends.

    Provides a unified interface for image generation across different
    providers (local models, cloud APIs, etc.).

    Lifecycle:
        1. Create backend with config: backend = DiffusersBackend(config)
        2. Load model/initialize: backend.load()
        3. Generate images: image = backend.generate(prompt)
        4. Unload when done: backend.unload()

    Attributes:
        config: Backend configuration
        _loaded: Whether backend is currently loaded and ready
    """

    def __init__(self, config: ImageBackendConfig):
        """
        Initialize backend with configuration.

        Args:
            config: Backend configuration

        Raises:
            ValueError: If configuration is invalid
        """
        self.config = config
        self._loaded = False

    @abstractmethod
    def load(self) -> None:
        """
        Load model into memory or initialize API client.

        Raises:
            RuntimeError: If loading fails
            ImportError: If required dependency not installed
        """
        pass

    @abstractmethod
    def unload(self) -> None:
        """
        Unload model and free resources.

        For local models, this should:
        - Delete model object
        - Clear CUDA cache if applicable
        - Set _loaded = False

        For API backends, this should:
        - Clean up client connections
        - Set _loaded = False
        """
        pass

    @abstractmethod
    def generate(self, prompt: str, negative_prompt: str = "", **kwargs) -> Image.Image:
        """
        Generate image from text prompt.

        Args:
            prompt: Input text prompt
            negative_prompt: Negative prompt (things to avoid)
            **kwargs: Override generation params (width, height, num_inference_steps, etc.)

        Returns:
            Generated PIL Image

        Raises:
            RuntimeError: If backend not loaded or generation fails

        Example:
            >>> backend = DiffusersBackend(config)
            >>> backend.load()
            >>> image = backend.generate(
            ...     "A beautiful landscape",
            ...     negative_prompt="blurry, low quality",
            ...     width=512,
            ...     height=512
            ... )
            >>> image.save("output.png")
        """
        pass

    @abstractmethod
    def get_vram_usage(self) -> float:
        """
        Get current VRAM usage in GB.

        For local models:
        - Query nvidia-smi or PyTorch CUDA
        - Return actual or estimated usage

        For API backends:
        - Return 0.0 (no local VRAM used)

        Returns:
            VRAM usage in GB (0.0 for API backends or if not loaded)
        """
        pass

    @abstractmethod
    def get_required_vram(self) -> float:
        """
        Get estimated VRAM required to load this model.

        For local models:
        - Estimate from model type and parameters
        - Account for resolution
        - Account for optimizations (CPU offload, slicing)

        For API backends:
        - Return 0.0 (no local VRAM required)

        Returns:
            Estimated VRAM in GB (0.0 for API backends)
        """
        pass

    def is_loaded(self) -> bool:
        """
        Check if backend is loaded and ready.

        Returns:
            True if loaded, False otherwise
        """
        return self._loaded

    @property
    def backend_type(self) -> str:
        """
        Get backend type identifier.

        Returns:
            Backend type string (e.g., 'diffusers', 'comfyui')
        """
        return self.config.backend_type
