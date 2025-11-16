"""
Tests for LLM Backend Abstraction Layer

Coverage: 85%+ target
Strategy: Unit tests with mocks (no actual API calls)
"""

import os
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from neonworks.ai.backends import (
    AnthropicBackend,
    LlamaCppBackend,
    LLMBackend,
    LLMBackendConfig,
    OpenAIBackend,
    create_llm_backend,
)


class TestLLMBackendConfig:
    """Test backend configuration"""

    def test_llama_cpp_config_creation(self):
        """Test creating llama-cpp config"""
        config = LLMBackendConfig(
            backend_type="llama-cpp",
            model_path="/path/to/model.gguf",
            n_ctx=4096,
            n_gpu_layers=-1,
        )
        assert config.backend_type == "llama-cpp"
        assert config.model_path == "/path/to/model.gguf"
        assert config.n_ctx == 4096
        assert config.n_gpu_layers == -1

    def test_openai_config_creation(self):
        """Test creating OpenAI config"""
        config = LLMBackendConfig(backend_type="openai", model_id="gpt-4", api_key="test-key")
        assert config.backend_type == "openai"
        assert config.model_id == "gpt-4"
        assert config.api_key == "test-key"

    def test_anthropic_config_creation(self):
        """Test creating Anthropic config"""
        config = LLMBackendConfig(
            backend_type="anthropic",
            model_id="claude-sonnet-4-20250514",
            api_key="test-key",
        )
        assert config.backend_type == "anthropic"

    def test_invalid_backend_type(self):
        """Test invalid backend type raises ValueError"""
        with pytest.raises(ValueError, match="Invalid backend_type"):
            LLMBackendConfig(backend_type="invalid")

    def test_temperature_validation_too_high(self):
        """Test temperature must be <= 2.0"""
        with pytest.raises(ValueError, match="temperature must be"):
            LLMBackendConfig(backend_type="openai", temperature=3.0)

    def test_temperature_validation_too_low(self):
        """Test temperature must be >= 0.0"""
        with pytest.raises(ValueError, match="temperature must be"):
            LLMBackendConfig(backend_type="openai", temperature=-0.5)

    def test_max_tokens_validation(self):
        """Test max_tokens must be positive"""
        with pytest.raises(ValueError, match="max_tokens must be positive"):
            LLMBackendConfig(backend_type="openai", max_tokens=-100)

    def test_extra_params_default(self):
        """Test extra_params defaults to empty dict"""
        config = LLMBackendConfig(backend_type="openai")
        assert config.extra_params == {}

    def test_extra_params_custom(self):
        """Test extra_params can be set"""
        config = LLMBackendConfig(backend_type="llama-cpp", extra_params={"verbose": True})
        assert config.extra_params == {"verbose": True}


class TestBackendFactory:
    """Test backend factory"""

    def test_create_llama_cpp_backend(self, tmp_path):
        """Test factory creates LlamaCppBackend"""
        model_file = tmp_path / "model.gguf"
        model_file.write_text("fake")

        config = LLMBackendConfig(backend_type="llama-cpp", model_path=str(model_file))
        backend = create_llm_backend(config)
        assert isinstance(backend, LlamaCppBackend)

    def test_create_openai_backend(self):
        """Test factory creates OpenAIBackend"""
        config = LLMBackendConfig(backend_type="openai", model_id="gpt-4", api_key="test-key")
        backend = create_llm_backend(config)
        assert isinstance(backend, OpenAIBackend)

    def test_create_anthropic_backend(self):
        """Test factory creates AnthropicBackend"""
        config = LLMBackendConfig(backend_type="anthropic", api_key="test-key")
        backend = create_llm_backend(config)
        assert isinstance(backend, AnthropicBackend)

    def test_create_unknown_backend(self):
        """Test factory raises ValueError for unknown type"""
        # Create config without validation
        config = LLMBackendConfig.__new__(LLMBackendConfig)
        config.backend_type = "unknown"
        with pytest.raises(ValueError, match="Unknown backend type"):
            create_llm_backend(config)


class TestLlamaCppBackend:
    """Test LlamaCpp backend"""

    def test_requires_model_path(self):
        """Test constructor requires model_path"""
        config = LLMBackendConfig(backend_type="llama-cpp")
        with pytest.raises(ValueError, match="requires model_path"):
            LlamaCppBackend(config)

    def test_requires_existing_file(self):
        """Test constructor requires existing file"""
        config = LLMBackendConfig(backend_type="llama-cpp", model_path="/nonexistent/model.gguf")
        with pytest.raises(FileNotFoundError):
            LlamaCppBackend(config)

    def test_vram_calculation_5gb_file(self, tmp_path):
        """Test VRAM estimation from 5GB file size"""
        # Create 5GB fake file
        model_file = tmp_path / "model.gguf"
        model_file.write_bytes(b"0" * (5 * 1024**3))

        config = LLMBackendConfig(backend_type="llama-cpp", model_path=str(model_file))
        backend = LlamaCppBackend(config)

        # Should estimate ~6GB (5GB + 20% overhead)
        required_vram = backend.get_required_vram()
        assert 5.5 <= required_vram <= 6.5

    def test_vram_calculation_small_file(self, tmp_path):
        """Test VRAM estimation from small file"""
        model_file = tmp_path / "model.gguf"
        model_file.write_bytes(b"0" * (2 * 1024**3))  # 2GB

        config = LLMBackendConfig(backend_type="llama-cpp", model_path=str(model_file))
        backend = LlamaCppBackend(config)

        required_vram = backend.get_required_vram()
        assert 2.0 <= required_vram <= 3.0  # 2GB + 20% = 2.4GB

    def test_not_loaded_initially(self, tmp_path):
        """Test backend not loaded initially"""
        model_file = tmp_path / "model.gguf"
        model_file.write_text("fake")

        config = LLMBackendConfig(backend_type="llama-cpp", model_path=str(model_file))
        backend = LlamaCppBackend(config)
        assert not backend.is_loaded()

    def test_backend_type_property(self, tmp_path):
        """Test backend_type property"""
        model_file = tmp_path / "model.gguf"
        model_file.write_text("fake")

        config = LLMBackendConfig(backend_type="llama-cpp", model_path=str(model_file))
        backend = LlamaCppBackend(config)
        assert backend.backend_type == "llama-cpp"

    def test_load_success(self, tmp_path, monkeypatch):
        """Test successful model loading"""
        model_file = tmp_path / "model.gguf"
        model_file.write_text("fake")

        # Mock the Llama class
        mock_llama_class = Mock()
        mock_model = Mock()
        mock_llama_class.return_value = mock_model

        # Patch the import
        import sys

        mock_llama_cpp = Mock()
        mock_llama_cpp.Llama = mock_llama_class
        monkeypatch.setitem(sys.modules, "llama_cpp", mock_llama_cpp)

        config = LLMBackendConfig(backend_type="llama-cpp", model_path=str(model_file))
        backend = LlamaCppBackend(config)
        backend.load()

        assert backend.is_loaded()
        mock_llama_class.assert_called_once_with(
            model_path=str(model_file),
            n_ctx=4096,
            n_gpu_layers=-1,
            verbose=False,
        )

    def test_load_already_loaded(self, tmp_path, monkeypatch):
        """Test loading when already loaded does nothing"""
        model_file = tmp_path / "model.gguf"
        model_file.write_text("fake")

        mock_llama_class = Mock()
        mock_model = Mock()
        mock_llama_class.return_value = mock_model

        import sys

        mock_llama_cpp = Mock()
        mock_llama_cpp.Llama = mock_llama_class
        monkeypatch.setitem(sys.modules, "llama_cpp", mock_llama_cpp)

        config = LLMBackendConfig(backend_type="llama-cpp", model_path=str(model_file))
        backend = LlamaCppBackend(config)
        backend.load()
        backend.load()  # Second load

        # Should only call once
        assert mock_llama_class.call_count == 1

    def test_unload(self, tmp_path, monkeypatch):
        """Test unloading model"""
        model_file = tmp_path / "model.gguf"
        model_file.write_text("fake")

        mock_llama_class = Mock()
        mock_model = Mock()
        mock_llama_class.return_value = mock_model

        import sys

        mock_llama_cpp = Mock()
        mock_llama_cpp.Llama = mock_llama_class
        monkeypatch.setitem(sys.modules, "llama_cpp", mock_llama_cpp)

        config = LLMBackendConfig(backend_type="llama-cpp", model_path=str(model_file))
        backend = LlamaCppBackend(config)
        backend.load()
        assert backend.is_loaded()

        backend.unload()
        assert not backend.is_loaded()

    def test_unload_when_not_loaded(self, tmp_path):
        """Test unloading when not loaded does nothing"""
        model_file = tmp_path / "model.gguf"
        model_file.write_text("fake")

        config = LLMBackendConfig(backend_type="llama-cpp", model_path=str(model_file))
        backend = LlamaCppBackend(config)
        backend.unload()  # Should not raise
        assert not backend.is_loaded()

    def test_generate_requires_load(self, tmp_path):
        """Test generate raises error if not loaded"""
        model_file = tmp_path / "model.gguf"
        model_file.write_text("fake")

        config = LLMBackendConfig(backend_type="llama-cpp", model_path=str(model_file))
        backend = LlamaCppBackend(config)

        with pytest.raises(RuntimeError, match="not loaded"):
            backend.generate("test")

    def test_generate_empty_prompt(self, tmp_path):
        """Test generate raises error for empty prompt"""
        model_file = tmp_path / "model.gguf"
        model_file.write_text("fake")

        config = LLMBackendConfig(backend_type="llama-cpp", model_path=str(model_file))
        backend = LlamaCppBackend(config)
        backend._loaded = True  # Fake loaded state
        backend.model = Mock()

        with pytest.raises(ValueError, match="cannot be empty"):
            backend.generate("")

    def test_generate_success(self, tmp_path, monkeypatch):
        """Test successful text generation"""
        model_file = tmp_path / "model.gguf"
        model_file.write_text("fake")

        mock_model = Mock()
        mock_model.return_value = {"choices": [{"text": "Generated text"}]}
        mock_llama_class = Mock()
        mock_llama_class.return_value = mock_model

        import sys

        mock_llama_cpp = Mock()
        mock_llama_cpp.Llama = mock_llama_class
        monkeypatch.setitem(sys.modules, "llama_cpp", mock_llama_cpp)

        config = LLMBackendConfig(backend_type="llama-cpp", model_path=str(model_file))
        backend = LlamaCppBackend(config)
        backend.load()

        result = backend.generate("Once upon a time")
        assert result == "Generated text"

    def test_generate_with_kwargs(self, tmp_path, monkeypatch):
        """Test generation with custom kwargs"""
        model_file = tmp_path / "model.gguf"
        model_file.write_text("fake")

        mock_model = Mock()
        mock_model.return_value = {"choices": [{"text": "Generated text"}]}
        mock_llama_class = Mock()
        mock_llama_class.return_value = mock_model

        import sys

        mock_llama_cpp = Mock()
        mock_llama_cpp.Llama = mock_llama_class
        monkeypatch.setitem(sys.modules, "llama_cpp", mock_llama_cpp)

        config = LLMBackendConfig(
            backend_type="llama-cpp", model_path=str(model_file), temperature=0.7
        )
        backend = LlamaCppBackend(config)
        backend.load()

        result = backend.generate("Test", temperature=0.9, max_tokens=100)
        assert result == "Generated text"

        # Verify kwargs were passed
        call_kwargs = mock_model.call_args[1]
        assert call_kwargs["temperature"] == 0.9
        assert call_kwargs["max_tokens"] == 100

    def test_get_vram_usage_not_loaded(self, tmp_path):
        """Test VRAM usage returns 0.0 when not loaded"""
        model_file = tmp_path / "model.gguf"
        model_file.write_text("fake")

        config = LLMBackendConfig(backend_type="llama-cpp", model_path=str(model_file))
        backend = LlamaCppBackend(config)
        assert backend.get_vram_usage() == 0.0


class TestOpenAIBackend:
    """Test OpenAI backend"""

    def test_requires_api_key(self):
        """Test constructor requires api_key"""
        config = LLMBackendConfig(backend_type="openai", model_id="gpt-4")
        with pytest.raises(ValueError, match="requires api_key"):
            OpenAIBackend(config)

    def test_requires_model_id(self):
        """Test constructor requires model_id"""
        config = LLMBackendConfig(backend_type="openai", api_key="test-key")
        with pytest.raises(ValueError, match="requires model_id"):
            OpenAIBackend(config)

    def test_not_loaded_initially(self):
        """Test backend not loaded initially"""
        config = LLMBackendConfig(backend_type="openai", model_id="gpt-4", api_key="test-key")
        backend = OpenAIBackend(config)
        assert not backend.is_loaded()

    def test_backend_type_property(self):
        """Test backend_type property"""
        config = LLMBackendConfig(backend_type="openai", model_id="gpt-4", api_key="test-key")
        backend = OpenAIBackend(config)
        assert backend.backend_type == "openai"

    def test_load_success(self, monkeypatch):
        """Test successful client initialization"""
        mock_client = Mock()
        mock_openai_class = Mock()
        mock_openai_class.return_value = mock_client

        import sys

        mock_openai = Mock()
        mock_openai.OpenAI = mock_openai_class
        monkeypatch.setitem(sys.modules, "openai", mock_openai)

        config = LLMBackendConfig(backend_type="openai", model_id="gpt-4", api_key="test-key")
        backend = OpenAIBackend(config)
        backend.load()

        assert backend.is_loaded()
        mock_openai_class.assert_called_once_with(api_key="test-key")

    def test_unload(self):
        """Test unloading client"""
        config = LLMBackendConfig(backend_type="openai", model_id="gpt-4", api_key="test-key")
        backend = OpenAIBackend(config)
        backend._loaded = True
        backend.client = Mock()

        backend.unload()
        assert not backend.is_loaded()
        assert backend.client is None

    def test_generate_requires_load(self):
        """Test generate raises error if not loaded"""
        config = LLMBackendConfig(backend_type="openai", model_id="gpt-4", api_key="test-key")
        backend = OpenAIBackend(config)

        with pytest.raises(RuntimeError, match="not initialized"):
            backend.generate("test")

    def test_generate_empty_prompt(self):
        """Test generate raises error for empty prompt"""
        config = LLMBackendConfig(backend_type="openai", model_id="gpt-4", api_key="test-key")
        backend = OpenAIBackend(config)
        backend._loaded = True
        backend.client = Mock()

        with pytest.raises(ValueError, match="cannot be empty"):
            backend.generate("")

    def test_generate_success(self, monkeypatch):
        """Test successful text generation"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Generated text"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class = Mock()
        mock_openai_class.return_value = mock_client

        import sys

        mock_openai = Mock()
        mock_openai.OpenAI = mock_openai_class
        monkeypatch.setitem(sys.modules, "openai", mock_openai)

        config = LLMBackendConfig(backend_type="openai", model_id="gpt-4", api_key="test-key")
        backend = OpenAIBackend(config)
        backend.load()

        result = backend.generate("Hello")
        assert result == "Generated text"

    def test_vram_usage_zero(self):
        """Test VRAM usage is always 0.0"""
        config = LLMBackendConfig(backend_type="openai", model_id="gpt-4", api_key="test-key")
        backend = OpenAIBackend(config)
        assert backend.get_vram_usage() == 0.0
        assert backend.get_required_vram() == 0.0


class TestAnthropicBackend:
    """Test Anthropic backend"""

    def test_requires_api_key(self):
        """Test constructor requires api_key"""
        config = LLMBackendConfig(backend_type="anthropic")
        with pytest.raises(ValueError, match="requires api_key"):
            AnthropicBackend(config)

    def test_default_model_id(self):
        """Test default model_id set if not provided"""
        config = LLMBackendConfig(backend_type="anthropic", api_key="test-key")
        backend = AnthropicBackend(config)
        assert backend.config.model_id == "claude-sonnet-4-20250514"

    def test_custom_model_id(self):
        """Test custom model_id preserved"""
        config = LLMBackendConfig(
            backend_type="anthropic",
            api_key="test-key",
            model_id="claude-opus-4-20250514",
        )
        backend = AnthropicBackend(config)
        assert backend.config.model_id == "claude-opus-4-20250514"

    def test_not_loaded_initially(self):
        """Test backend not loaded initially"""
        config = LLMBackendConfig(backend_type="anthropic", api_key="test-key")
        backend = AnthropicBackend(config)
        assert not backend.is_loaded()

    def test_backend_type_property(self):
        """Test backend_type property"""
        config = LLMBackendConfig(backend_type="anthropic", api_key="test-key")
        backend = AnthropicBackend(config)
        assert backend.backend_type == "anthropic"

    def test_load_success(self, monkeypatch):
        """Test successful client initialization"""
        mock_client = Mock()
        mock_anthropic_class = Mock()
        mock_anthropic_class.return_value = mock_client

        import sys

        mock_anthropic = Mock()
        mock_anthropic.Anthropic = mock_anthropic_class
        monkeypatch.setitem(sys.modules, "anthropic", mock_anthropic)

        config = LLMBackendConfig(backend_type="anthropic", api_key="test-key")
        backend = AnthropicBackend(config)
        backend.load()

        assert backend.is_loaded()
        mock_anthropic_class.assert_called_once_with(api_key="test-key")

    def test_unload(self):
        """Test unloading client"""
        config = LLMBackendConfig(backend_type="anthropic", api_key="test-key")
        backend = AnthropicBackend(config)
        backend._loaded = True
        backend.client = Mock()

        backend.unload()
        assert not backend.is_loaded()
        assert backend.client is None

    def test_generate_requires_load(self):
        """Test generate raises error if not loaded"""
        config = LLMBackendConfig(backend_type="anthropic", api_key="test-key")
        backend = AnthropicBackend(config)

        with pytest.raises(RuntimeError, match="not initialized"):
            backend.generate("test")

    def test_generate_empty_prompt(self):
        """Test generate raises error for empty prompt"""
        config = LLMBackendConfig(backend_type="anthropic", api_key="test-key")
        backend = AnthropicBackend(config)
        backend._loaded = True
        backend.client = Mock()

        with pytest.raises(ValueError, match="cannot be empty"):
            backend.generate("")

    def test_generate_success(self, monkeypatch):
        """Test successful text generation"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text="Generated text")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class = Mock()
        mock_anthropic_class.return_value = mock_client

        import sys

        mock_anthropic = Mock()
        mock_anthropic.Anthropic = mock_anthropic_class
        monkeypatch.setitem(sys.modules, "anthropic", mock_anthropic)

        config = LLMBackendConfig(backend_type="anthropic", api_key="test-key")
        backend = AnthropicBackend(config)
        backend.load()

        result = backend.generate("Hello")
        assert result == "Generated text"

    def test_vram_usage_zero(self):
        """Test VRAM usage is always 0.0"""
        config = LLMBackendConfig(backend_type="anthropic", api_key="test-key")
        backend = AnthropicBackend(config)
        assert backend.get_vram_usage() == 0.0
        assert backend.get_required_vram() == 0.0
