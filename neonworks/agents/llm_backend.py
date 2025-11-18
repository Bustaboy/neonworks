from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LLMBackend(ABC):
    """
    Abstract interface for language model backends.

    Concrete implementations can wrap OpenAI, local models, or any other
    provider. The rest of the engine should depend on this interface
    rather than a specific model client.
    """

    @abstractmethod
    def generate(self, prompt: str, **kwargs: Any) -> str:
        """
        Generate a text completion for the given prompt.

        Implementations may use kwargs for temperature, max_tokens, etc.
        """
        raise NotImplementedError


class DummyBackend(LLMBackend):
    """
    Minimal backend used for testing and offline scenarios.

    For now, it simply echoes the prompt unchanged. This keeps the
    engine behavior deterministic and makes it easy to plug in a real
    backend later without changing call sites.
    """

    def generate(self, prompt: str, **kwargs: Any) -> str:  # noqa: ARG002
        return prompt

