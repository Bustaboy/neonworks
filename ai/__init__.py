"""
AI Module for NeonWorks Game Engine

Provides AI-powered tools for game development including:
- LLM backends for text generation
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
from .pathfinding import (
    Heuristic,
    NavigationGrid,
    Pathfinder,
    PathfindingSystem,
    PathNode,
)

__all__ = [
    # LLM Backends
    "LLMBackend",
    "LLMBackendConfig",
    "LlamaCppBackend",
    "OpenAIBackend",
    "AnthropicBackend",
    "create_llm_backend",
    # Pathfinding
    "NavigationGrid",
    "Pathfinder",
    "PathfindingSystem",
    "Heuristic",
    "PathNode",
]
