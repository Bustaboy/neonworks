from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from .llm_backend import LLMBackend


@dataclass
class Director:
    """
    Orchestrates agent tasks across multiple language model backends.

    The Director is responsible for ensuring that, conceptually, only a single
    model is loaded into GPU memory at a time so the engine can stay within
    an 8 GB VRAM budget. In practice this is handled by calling optional
    `load()` / `unload()` hooks on backends and tracking which backend is
    currently active.

    Backends are provided at construction time and are addressed by an
    `agent_name` string so callers don't need to know about specific models.
    """

    backends: Dict[str, LLMBackend] = field(default_factory=dict)
    _active_agent: Optional[str] = field(default=None, init=False)

    def _load_backend(self, agent_name: str) -> LLMBackend:
        """
        Ensure the backend for `agent_name` is the only active one.

        If a different backend is currently active, it will be unloaded first.
        """
        if agent_name not in self.backends:
            raise KeyError(f"Unknown agent '{agent_name}'")

        # If the requested backend is already active, nothing to do.
        if self._active_agent == agent_name:
            return self.backends[agent_name]

        # Unload the currently active backend, if any.
        if self._active_agent is not None:
            current = self.backends.get(self._active_agent)
            if current is not None and hasattr(current, "unload"):
                # Backends may implement an optional unload() hook.
                current.unload()  # type: ignore[call-arg]

        backend = self.backends[agent_name]

        # Load the new backend if it exposes a load() hook.
        if hasattr(backend, "load"):
            backend.load()  # type: ignore[call-arg]

        self._active_agent = agent_name
        return backend

    def run_task(self, agent_name: str, prompt: str, **kwargs) -> str:
        """
        Run a task on the specified agent and return the generated text.

        This method ensures that only one backend is considered "loaded" at
        any time by unloading the previous backend (if different) before
        activating the requested one.
        """
        backend = self._load_backend(agent_name)
        return backend.generate(prompt, **kwargs)

