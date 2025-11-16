"""
LlamaCpp Backend for Local GGUF Models

Supports local LLM inference using GGUF quantized models with llama-cpp-python.
"""

import os
from typing import Optional

from .llm_backend import LLMBackend, LLMBackendConfig


class LlamaCppBackend(LLMBackend):
    """
    Backend for llama-cpp-python (GGUF models).

    Supports local LLM inference using GGUF quantized models with
    optional GPU acceleration via llama.cpp.

    Features:
    - GGUF model loading
    - GPU layer offloading (CUDA)
    - Configurable context window
    - Thread-based CPU inference

    Requirements:
    - llama-cpp-python package
    - GGUF model file
    - Optional: CUDA for GPU acceleration

    Example:
        >>> config = LLMBackendConfig(
        ...     backend_type='llama-cpp',
        ...     model_path='/models/llama-3.1-8b-q4.gguf',
        ...     n_ctx=4096,
        ...     n_gpu_layers=-1
        ... )
        >>> backend = LlamaCppBackend(config)
        >>> backend.load()
        >>> text = backend.generate("Hello, world!")
        >>> backend.unload()
    """

    def __init__(self, config: LLMBackendConfig):
        """
        Initialize llama-cpp backend.

        Args:
            config: Backend configuration

        Raises:
            ValueError: If config is invalid (missing model_path)
            FileNotFoundError: If model file doesn't exist
        """
        super().__init__(config)
        self.model = None

        # Validate config
        if not config.model_path:
            raise ValueError("LlamaCppBackend requires model_path in config")

        if not os.path.exists(config.model_path):
            raise FileNotFoundError(
                f"Model file not found: {config.model_path}\n"
                f"Please download a GGUF model to this path."
            )

    def load(self) -> None:
        """
        Load GGUF model via llama-cpp-python.

        Raises:
            ImportError: If llama-cpp-python not installed
            RuntimeError: If model loading fails
        """
        if self._loaded:
            return  # Already loaded

        try:
            from llama_cpp import Llama
        except ImportError:
            raise ImportError(
                "llama-cpp-python is required for LlamaCppBackend.\n"
                "Install with: pip install llama-cpp-python"
            )

        try:
            self.model = Llama(
                model_path=self.config.model_path,
                n_ctx=self.config.n_ctx,
                n_gpu_layers=self.config.n_gpu_layers,
                verbose=False,
                **self.config.extra_params,
            )
            self._loaded = True

        except Exception as e:
            raise RuntimeError(f"Failed to load llama-cpp model from {self.config.model_path}: {e}")

    def unload(self) -> None:
        """
        Unload model and free VRAM.

        Deletes model object and clears CUDA cache if available.
        """
        if not self._loaded:
            return  # Already unloaded

        if self.model:
            del self.model
            self.model = None

        # Force CUDA cache clear
        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
        except ImportError:
            pass  # torch not available, skip cache clear

        self._loaded = False

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text using llama-cpp.

        Args:
            prompt: Input text prompt
            **kwargs: Override generation params

        Returns:
            Generated text string

        Raises:
            RuntimeError: If model not loaded
            ValueError: If prompt is empty
        """
        if not self._loaded or not self.model:
            raise RuntimeError("Model not loaded. Call load() before generating text.")

        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        # Merge kwargs with config defaults
        gen_params = {
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
        }

        # Add any extra params from kwargs
        for key, value in kwargs.items():
            if key not in gen_params:
                gen_params[key] = value

        try:
            result = self.model(prompt, **gen_params)
            return result["choices"][0]["text"]

        except Exception as e:
            raise RuntimeError(f"Text generation failed: {e}")

    def get_vram_usage(self) -> float:
        """
        Get current VRAM usage.

        Attempts to query nvidia-smi for accurate measurement.
        Falls back to estimation if nvidia-smi unavailable.

        Returns:
            VRAM usage in GB
        """
        if not self._loaded:
            return 0.0

        # Try nvidia-smi first
        try:
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
                # Get first value (our process)
                used_mb = float(result.stdout.strip().split("\n")[0])
                return used_mb / 1024.0  # Convert MB to GB
        except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
            pass  # nvidia-smi not available or failed

        # Fallback to estimation
        return self.get_required_vram()

    def get_required_vram(self) -> float:
        """
        Estimate VRAM needed for this model.

        Estimation based on GGUF file size plus ~20% overhead
        for KV cache and computation buffers.

        Returns:
            Estimated VRAM in GB
        """
        try:
            file_size_gb = os.path.getsize(self.config.model_path) / (1024**3)
            # Add 20% overhead for KV cache and computation
            return file_size_gb * 1.2
        except (OSError, TypeError):
            return 5.0  # Safe default estimate
