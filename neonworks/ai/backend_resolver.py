from __future__ import annotations

"""
LLM backend resolver that picks the best available backend for the host hardware.

Strategy:
- Allow explicit override via env/args.
- If "auto", choose the best installed backend that fits VRAM/RAM/CPU constraints.
- Fall back to DummyBackend if nothing else is usable.
"""

import os
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from neonworks.agents.llm_backend import DummyBackend, LLMBackend
from neonworks.ai.backends import LLMBackendConfig, create_llm_backend

try:
    import psutil
except ImportError:  # pragma: no cover
    psutil = None  # type: ignore


def _detect_vram_gb() -> float:
    """Best-effort VRAM detection in GB."""
    try:
        import torch

        if torch.cuda.is_available():
            idx = torch.cuda.current_device()
            props = torch.cuda.get_device_properties(idx)
            return props.total_memory / (1024**3)
    except Exception:
        pass
    return 0.0


def _detect_ram_gb() -> float:
    """Best-effort system RAM in GB."""
    if psutil is None:
        return 0.0
    try:
        return psutil.virtual_memory().total / (1024**3)
    except Exception:
        return 0.0


@dataclass
class BackendCandidate:
    name: str
    config: LLMBackendConfig
    requires_vram: float
    preference: int  # lower is better


def default_candidates() -> List[BackendCandidate]:
    """
    Provide a default list. In a real app this would be dynamic (installed models).
    """
    candidates: List[BackendCandidate] = []

    # Example local GGUF (8B quant) assumed at ~4 GB VRAM need.
    gguf_path = os.environ.get("NEONWORKS_GGUF_8B")
    if gguf_path:
        candidates.append(
            BackendCandidate(
                name="llama-8b-gguf",
                config=LLMBackendConfig(
                    backend_type="llama-cpp",
                    model_path=gguf_path,
                    n_ctx=4096,
                    n_gpu_layers=-1,
                    temperature=0.7,
                ),
                requires_vram=4.0,
                preference=10,
            )
        )

    # OpenAI API as a no-VRAM fallback if API key present.
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        candidates.append(
            BackendCandidate(
                name="openai-gpt-4o-mini",
                config=LLMBackendConfig(
                    backend_type="openai",
                    model_id="gpt-4o-mini",
                    api_key=openai_key,
                    temperature=0.6,
                ),
                requires_vram=0.0,
                preference=20,
            )
        )

    return candidates


def resolve_llm_backend(
    override_name: Optional[str] = None,
    candidates_factory: Callable[[], List[BackendCandidate]] = default_candidates,
) -> LLMBackend:
    """
    Resolve an LLM backend using override/env/auto selection.

    override_name: explicit backend name ("auto" to let resolver choose).
    """
    if override_name is None:
        override_name = os.environ.get("NEONWORKS_LLM", "auto")

    candidates = candidates_factory()
    if not candidates:
        return DummyBackend()

    # Explicit selection
    if override_name and override_name != "auto":
        for c in candidates:
            if c.name == override_name:
                return _instantiate(c)
        return DummyBackend()

    # Auto selection
    vram = _detect_vram_gb()
    ram = _detect_ram_gb()

    usable: List[BackendCandidate] = []
    for c in candidates:
        if c.requires_vram and vram > 0 and vram + 0.25 >= c.requires_vram:
            usable.append(c)
        elif c.requires_vram == 0.0:
            usable.append(c)
        elif vram == 0.0:
            # Cannot detect; assume usable and let backend fail at load if needed.
            usable.append(c)

    if not usable:
        return DummyBackend()

    usable.sort(key=lambda c: c.preference)
    return _instantiate(usable[0])


def _instantiate(candidate: BackendCandidate) -> LLMBackend:
    backend = create_llm_backend(candidate.config)
    try:
        if hasattr(backend, "load"):
            backend.load()  # type: ignore[call-arg]
    except Exception:
        # If it fails to load, fall back to dummy.
        return DummyBackend()
    return backend
