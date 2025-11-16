"""
Anthropic Backend for Claude Models

Provides access to Anthropic's Claude models via their official SDK.
"""

from .llm_backend import LLMBackend, LLMBackendConfig


class AnthropicBackend(LLMBackend):
    """
    Backend for Anthropic API (Claude).

    Provides access to Anthropic's Claude models via their
    official Python SDK.

    Features:
    - Cloud-based inference (no local VRAM)
    - Access to Claude Sonnet, Opus, Haiku
    - Automatic API key management
    - Streaming support (future)

    Requirements:
    - anthropic package
    - Anthropic API key
    - Internet connection

    Example:
        >>> config = LLMBackendConfig(
        ...     backend_type='anthropic',
        ...     model_id='claude-sonnet-4-20250514',
        ...     api_key='sk-ant-...'
        ... )
        >>> backend = AnthropicBackend(config)
        >>> backend.load()
        >>> text = backend.generate("Hello, Claude!")
    """

    def __init__(self, config: LLMBackendConfig):
        """
        Initialize Anthropic backend.

        Args:
            config: Backend configuration

        Raises:
            ValueError: If config is invalid (missing api_key)
        """
        super().__init__(config)
        self.client = None

        # Validate config
        if not config.api_key:
            raise ValueError(
                "AnthropicBackend requires api_key in config.\n"
                "Get your API key from: https://console.anthropic.com/"
            )

        # Default model_id if not provided
        if not config.model_id:
            config.model_id = "claude-sonnet-4-20250514"

    def load(self) -> None:
        """
        Initialize Anthropic client.

        Raises:
            ImportError: If anthropic package not installed
            RuntimeError: If client initialization fails
        """
        if self._loaded:
            return  # Already loaded

        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "anthropic is required for AnthropicBackend.\n"
                "Install with: pip install anthropic"
            )

        try:
            self.client = anthropic.Anthropic(api_key=self.config.api_key)
            self._loaded = True

        except Exception as e:
            raise RuntimeError(f"Failed to initialize Anthropic client: {e}")

    def unload(self) -> None:
        """
        Clean up client (no VRAM to free).
        """
        self.client = None
        self._loaded = False

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text using Anthropic API.

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
        # Note: Anthropic REQUIRES max_tokens (no default)
        gen_params = {
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
        }

        try:
            response = self.client.messages.create(
                model=self.config.model_id,
                messages=[{"role": "user", "content": prompt}],
                **gen_params
            )
            return response.content[0].text

        except Exception as e:
            raise RuntimeError(f"Anthropic API request failed: {e}")

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
