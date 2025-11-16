"""
LLM Backend Abstract Base Class

Provides unified interface for text generation across different LLM providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class LLMBackendConfig:
    """
    Configuration for LLM backends.

    Attributes:
        backend_type: Backend type ('llama-cpp', 'openai', 'anthropic')
        model_path: Path to local model file (for llama-cpp)
        model_id: Model identifier (for APIs and transformers)
        api_key: API key for cloud providers (for openai, anthropic)
        n_ctx: Context window size in tokens
        n_gpu_layers: Number of GPU layers to offload (-1 = all, for llama-cpp)
        temperature: Sampling temperature (0.0 = deterministic, 2.0 = creative)
        max_tokens: Maximum tokens to generate
        extra_params: Backend-specific additional parameters

    Example:
        >>> config = LLMBackendConfig(
        ...     backend_type='llama-cpp',
        ...     model_path='/models/llama-3.1-8b-q4.gguf',
        ...     n_ctx=4096,
        ...     n_gpu_layers=-1
        ... )
    """

    backend_type: str
    model_path: Optional[str] = None
    model_id: Optional[str] = None
    api_key: Optional[str] = None
    n_ctx: int = 4096
    n_gpu_layers: int = -1
    temperature: float = 0.7
    max_tokens: int = 2048
    extra_params: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate configuration after initialization."""
        # Validate backend_type
        valid_types = {"llama-cpp", "openai", "anthropic", "transformers"}
        if self.backend_type not in valid_types:
            raise ValueError(
                f"Invalid backend_type '{self.backend_type}'. "
                f"Must be one of: {valid_types}"
            )

        # Validate temperature range
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError(
                f"temperature must be between 0.0 and 2.0, got {self.temperature}"
            )

        # Validate max_tokens
        if self.max_tokens <= 0:
            raise ValueError(f"max_tokens must be positive, got {self.max_tokens}")


class LLMBackend(ABC):
    """
    Abstract base class for LLM backends.

    Provides a unified interface for text generation across different
    LLM providers (local models, cloud APIs, etc.).

    Lifecycle:
        1. Create backend with config: backend = LlamaCppBackend(config)
        2. Load model/initialize: backend.load()
        3. Generate text: text = backend.generate(prompt)
        4. Unload when done: backend.unload()

    Attributes:
        config: Backend configuration
        _loaded: Whether backend is currently loaded and ready
    """

    def __init__(self, config: LLMBackendConfig):
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
            FileNotFoundError: If model file not found (local backends)
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
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text from prompt.

        Args:
            prompt: Input text prompt
            **kwargs: Override generation params (temperature, max_tokens, etc.)
                     Any kwargs provided will override config defaults

        Returns:
            Generated text string

        Raises:
            RuntimeError: If backend not loaded or generation fails
            ValueError: If prompt is invalid

        Example:
            >>> backend = LlamaCppBackend(config)
            >>> backend.load()
            >>> text = backend.generate(
            ...     "Once upon a time",
            ...     temperature=0.9,
            ...     max_tokens=100
            ... )
            >>> print(text)
            Once upon a time, in a land far away...
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
            VRAM usage in GB (0.0 for API backends)
        """
        pass

    @abstractmethod
    def get_required_vram(self) -> float:
        """
        Get estimated VRAM required to load this model.

        For local models:
        - Estimate from file size (GGUF)
        - Estimate from model parameters (transformers)
        - Add overhead for KV cache (~20%)

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
            Backend type string (e.g., 'llama-cpp', 'openai')
        """
        return self.config.backend_type
