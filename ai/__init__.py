"""
AI Module for NeonWorks Game Engine

Provides AI-powered tools for game development including:
- LLM backends for text generation
- Image generation with VRAM management
- GPU monitoring and resource allocation
- Navigation, pathfinding, and AI behaviors
"""

from .backends import (
    AnthropicBackend,
    LlamaCppBackend,
    LLMBackend,
    LLMBackendConfig,
    OpenAIBackend,
    create_llm_backend,
)
from .gpu_monitor import GPUMonitor, GPUVendor
from .image_request import ImageGenerationRequest, RequestState
from .image_service import ImageService
from .pathfinding import (
    Heuristic,
    NavigationGrid,
    Pathfinder,
    PathfindingSystem,
    PathNode,
)
from .vram_manager import SmartVRAMManager
from .vram_priority import VRAMPriority

__all__ = [
    # LLM Backends
    "LLMBackend",
    "LLMBackendConfig",
    "LlamaCppBackend",
    "OpenAIBackend",
    "AnthropicBackend",
    "create_llm_backend",
    # Image Generation
    "ImageService",
    "ImageGenerationRequest",
    "RequestState",
    # VRAM Management
    "SmartVRAMManager",
    "VRAMPriority",
    "GPUMonitor",
    "GPUVendor",
    # Pathfinding
    "NavigationGrid",
    "Pathfinder",
    "PathfindingSystem",
    "Heuristic",
    "PathNode",
]
