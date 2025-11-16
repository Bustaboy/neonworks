"""
OpenAI Backend for GPT Models

Provides access to OpenAI's cloud-based language models via their official SDK.
"""

from .llm_backend import LLMBackend, LLMBackendConfig


class OpenAIBackend(LLMBackend):
    """
    Backend for OpenAI API (GPT-4, GPT-3.5, etc.).

    Provides access to OpenAI's cloud-based language models via
    their official Python SDK.

    Features:
    - Cloud-based inference (no local VRAM)
    - Access to GPT-4, GPT-3.5-Turbo, etc.
    - Automatic API key management
    - Streaming support (future)

    Requirements:
    - openai package
    - OpenAI API key
    - Internet connection

    Example:
        >>> config = LLMBackendConfig(
        ...     backend_type='openai',
        ...     model_id='gpt-4',
        ...     api_key='sk-...'
        ... )
        >>> backend = OpenAIBackend(config)
        >>> backend.load()
        >>> text = backend.generate("Hello, world!")
    """

    def __init__(self, config: LLMBackendConfig):
        """
        Initialize OpenAI backend.

        Args:
            config: Backend configuration

        Raises:
            ValueError: If config is invalid (missing api_key or model_id)
        """
        super().__init__(config)
        self.client = None

        # Validate config
        if not config.api_key:
            raise ValueError(
                "OpenAIBackend requires api_key in config.\n"
                "Get your API key from: https://platform.openai.com/api-keys"
            )

        if not config.model_id:
            raise ValueError(
                "OpenAIBackend requires model_id (e.g., 'gpt-4', 'gpt-3.5-turbo')"
            )

    def load(self) -> None:
        """
        Initialize OpenAI client.

        Raises:
            ImportError: If openai package not installed
            RuntimeError: If client initialization fails
        """
        if self._loaded:
            return  # Already loaded

        try:
            import openai
        except ImportError:
            raise ImportError(
                "openai is required for OpenAIBackend.\n"
                "Install with: pip install openai"
            )

        try:
            self.client = openai.OpenAI(api_key=self.config.api_key)
            self._loaded = True

        except Exception as e:
            raise RuntimeError(f"Failed to initialize OpenAI client: {e}")

    def unload(self) -> None:
        """
        Clean up client (no VRAM to free).
        """
        self.client = None
        self._loaded = False

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text using OpenAI API.

        Args:
            prompt: Input text prompt
            **kwargs: Override generation params

        Returns:
            Generated text string

        Raises:
            RuntimeError: If client not initialized or API call fails
            ValueError: If prompt is empty
        """
        if not self._loaded or not self.client:
            raise RuntimeError(
                "Client not initialized. Call load() before generating text."
            )

        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        # Merge kwargs with config defaults
        gen_params = {
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
        }

        try:
            response = self.client.chat.completions.create(
                model=self.config.model_id,
                messages=[{"role": "user", "content": prompt}],
                **gen_params
            )
            return response.choices[0].message.content

        except Exception as e:
            raise RuntimeError(f"OpenAI API request failed: {e}")

    def get_vram_usage(self) -> float:
        """
        API backend uses no local VRAM.

        Returns:
            0.0 (cloud-based)
        """
        return 0.0

    def get_required_vram(self) -> float:
        """
        API backend requires no local VRAM.

        Returns:
            0.0 (cloud-based)
        """
        return 0.0
