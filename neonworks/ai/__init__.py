"""
AI Module for NeonWorks Game Engine

Provides AI-powered tools for game development including:
- LLM backends for text generation
- Future: Image generation
- Future: Animation generation
"""

from .backends import (
    AnthropicBackend,
    LlamaCppBackend,
    LLMBackend,
    LLMBackendConfig,
    OpenAIBackend,
    create_llm_backend,
)

__all__ = [
    "LLMBackend",
    "LLMBackendConfig",
    "LlamaCppBackend",
    "OpenAIBackend",
    "AnthropicBackend",
    "create_llm_backend",
]
