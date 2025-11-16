"""
Backend Abstraction Layer

Provides unified interface for multiple AI backends:

LLM Backends:
- llama-cpp-python (local GGUF models)
- OpenAI API (GPT-4, GPT-3.5, etc.)
- Anthropic API (Claude)

Image Backends:
- diffusers (Stable Diffusion 1.5, SDXL, SD 3)

Example (LLM):
    >>> from neonworks.ai.backends import LLMBackendConfig, create_llm_backend
    >>> config = LLMBackendConfig(
    ...     backend_type='llama-cpp',
    ...     model_path='/models/llama-3.1-8b.gguf'
    ... )
    >>> backend = create_llm_backend(config)
    >>> backend.load()
    >>> text = backend.generate("Once upon a time")
    >>> backend.unload()

Example (Image):
    >>> from neonworks.ai.backends import ImageBackendConfig, create_image_backend
    >>> config = ImageBackendConfig(
    ...     backend_type='diffusers',
    ...     model_id='runwayml/stable-diffusion-v1-5'
    ... )
    >>> backend = create_image_backend(config)
    >>> backend.load()
    >>> image = backend.generate("A beautiful landscape")
    >>> image.save("output.png")
    >>> backend.unload()
"""

from .anthropic_backend import AnthropicBackend
from .diffusers_backend import DiffusersBackend
from .image_backend import ImageBackend, ImageBackendConfig
from .llama_cpp_backend import LlamaCppBackend
from .llm_backend import LLMBackend, LLMBackendConfig
from .openai_backend import OpenAIBackend


def create_llm_backend(config: LLMBackendConfig) -> LLMBackend:
    """
    Factory function to create appropriate backend from config.

    Args:
        config: Backend configuration

    Returns:
        Concrete backend instance

    Raises:
        ValueError: If backend_type is unknown

    Example:
        >>> config = LLMBackendConfig(
        ...     backend_type='openai',
        ...     model_id='gpt-4',
        ...     api_key='sk-...'
        ... )
        >>> backend = create_llm_backend(config)
    """
    backend_map = {
        "llama-cpp": LlamaCppBackend,
        "openai": OpenAIBackend,
        "anthropic": AnthropicBackend,
    }

    backend_class = backend_map.get(config.backend_type)
    if not backend_class:
        raise ValueError(
            f"Unknown backend type: '{config.backend_type}'. "
            f"Valid types: {list(backend_map.keys())}"
        )

    return backend_class(config)


def create_image_backend(config: ImageBackendConfig) -> ImageBackend:
    """
    Factory function to create appropriate image backend.

    Args:
        config: Image backend configuration

    Returns:
        Concrete backend instance (DiffusersBackend, etc.)

    Raises:
        ValueError: If backend_type is unknown

    Example:
        >>> config = ImageBackendConfig(
        ...     backend_type='diffusers',
        ...     model_id='runwayml/stable-diffusion-v1-5'
        ... )
        >>> backend = create_image_backend(config)
        >>> isinstance(backend, DiffusersBackend)
        True
    """
    backend_map = {
        "diffusers": DiffusersBackend,
    }

    backend_class = backend_map.get(config.backend_type)
    if not backend_class:
        raise ValueError(
            f"Unknown image backend type: '{config.backend_type}'. "
            f"Valid types: {list(backend_map.keys())}"
        )

    return backend_class(config)


__all__ = [
    # LLM backends
    "LLMBackend",
    "LLMBackendConfig",
    "LlamaCppBackend",
    "OpenAIBackend",
    "AnthropicBackend",
    "create_llm_backend",
    # Image backends
    "ImageBackend",
    "ImageBackendConfig",
    "DiffusersBackend",
    "create_image_backend",
]
