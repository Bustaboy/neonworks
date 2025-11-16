"""
Tests for Image Backend Abstraction Layer

Tests for abstract ImageBackend class, ImageBackendConfig dataclass,
DiffusersBackend implementation, and factory function.
"""

import pytest
from PIL import Image

from neonworks.ai.backends import (
    DiffusersBackend,
    ImageBackend,
    ImageBackendConfig,
    create_image_backend,
)


class TestImageBackendConfig:
    """Test suite for ImageBackendConfig dataclass."""

    def test_default_config(self):
        """Test creating config with default values."""
        config = ImageBackendConfig(backend_type="diffusers")

        assert config.backend_type == "diffusers"
        assert config.width == 512
        assert config.height == 512
        assert config.num_inference_steps == 30
        assert config.guidance_scale == 7.5
        assert config.enable_attention_slicing is True
        assert config.enable_vae_slicing is True
        assert config.enable_cpu_offload is False
        assert config.model_id is None
        assert config.model_path is None

    def test_sdxl_config(self):
        """Test creating SDXL configuration."""
        config = ImageBackendConfig(
            backend_type="diffusers",
            model_id="stabilityai/stable-diffusion-xl-base-1.0",
            width=1024,
            height=1024,
            enable_cpu_offload=True,
        )

        assert config.model_id == "stabilityai/stable-diffusion-xl-base-1.0"
        assert config.width == 1024
        assert config.height == 1024
        assert config.enable_cpu_offload is True

    def test_invalid_backend_type(self):
        """Test that invalid backend type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid backend_type"):
            ImageBackendConfig(backend_type="unknown")

    def test_invalid_dimensions(self):
        """Test that invalid dimensions raise ValueError."""
        with pytest.raises(ValueError, match="width must be positive"):
            ImageBackendConfig(backend_type="diffusers", width=0)

        with pytest.raises(ValueError, match="width must be positive"):
            ImageBackendConfig(backend_type="diffusers", width=-10)

        with pytest.raises(ValueError, match="height must be positive"):
            ImageBackendConfig(backend_type="diffusers", height=0)

        with pytest.raises(ValueError, match="height must be positive"):
            ImageBackendConfig(backend_type="diffusers", height=-10)

    def test_invalid_inference_steps(self):
        """Test that invalid inference steps raise ValueError."""
        with pytest.raises(ValueError, match="num_inference_steps must be positive"):
            ImageBackendConfig(backend_type="diffusers", num_inference_steps=0)

        with pytest.raises(ValueError, match="num_inference_steps must be positive"):
            ImageBackendConfig(backend_type="diffusers", num_inference_steps=-5)


class TestDiffusersBackend:
    """Test suite for DiffusersBackend implementation."""

    def test_model_type_detection_sd15(self):
        """Test SD 1.5 model type detection."""
        config = ImageBackendConfig(
            backend_type="diffusers", model_id="runwayml/stable-diffusion-v1-5"
        )
        backend = DiffusersBackend(config)

        assert backend._model_type == "sd-1.5"

    def test_model_type_detection_sdxl(self):
        """Test SDXL model type detection."""
        config = ImageBackendConfig(
            backend_type="diffusers",
            model_id="stabilityai/stable-diffusion-xl-base-1.0",
        )
        backend = DiffusersBackend(config)

        assert backend._model_type == "sdxl"

    def test_model_type_detection_sd3(self):
        """Test SD 3 model type detection."""
        config = ImageBackendConfig(
            backend_type="diffusers",
            model_id="stabilityai/stable-diffusion-3-medium-diffusers",
        )
        backend = DiffusersBackend(config)

        assert backend._model_type == "sd-3"

    def test_model_type_detection_default(self):
        """Test default model type when model_id is None."""
        config = ImageBackendConfig(backend_type="diffusers")
        backend = DiffusersBackend(config)

        assert backend._model_type == "sd-1.5"

    def test_vram_estimation_sd15(self):
        """Test VRAM estimation for SD 1.5."""
        config = ImageBackendConfig(
            backend_type="diffusers",
            model_id="runwayml/stable-diffusion-v1-5",
            width=512,
            height=512,
        )
        backend = DiffusersBackend(config)
        vram = backend.get_required_vram()

        # SD 1.5 should be ~4GB base
        assert 3.5 <= vram <= 4.5

    def test_vram_estimation_sdxl(self):
        """Test VRAM estimation for SDXL."""
        config = ImageBackendConfig(
            backend_type="diffusers",
            model_id="stabilityai/stable-diffusion-xl-base-1.0",
            width=1024,
            height=1024,
        )
        backend = DiffusersBackend(config)
        vram = backend.get_required_vram()

        # SDXL should be ~7.5GB base
        assert 7.0 <= vram <= 8.0

    def test_vram_estimation_sd3(self):
        """Test VRAM estimation for SD 3."""
        config = ImageBackendConfig(
            backend_type="diffusers",
            model_id="stabilityai/stable-diffusion-3-medium-diffusers",
            width=1024,
            height=1024,
        )
        backend = DiffusersBackend(config)
        vram = backend.get_required_vram()

        # SD 3 should be ~10GB base
        assert 9.0 <= vram <= 11.0

    def test_vram_increases_with_resolution(self):
        """Test that VRAM estimation increases with resolution."""
        config_512 = ImageBackendConfig(
            backend_type="diffusers",
            model_id="runwayml/stable-diffusion-v1-5",
            width=512,
            height=512,
        )
        backend_512 = DiffusersBackend(config_512)
        vram_512 = backend_512.get_required_vram()

        config_1024 = ImageBackendConfig(
            backend_type="diffusers",
            model_id="runwayml/stable-diffusion-v1-5",
            width=1024,
            height=1024,
        )
        backend_1024 = DiffusersBackend(config_1024)
        vram_1024 = backend_1024.get_required_vram()

        assert vram_1024 > vram_512
        # At least 20% more for 4x the pixels
        assert vram_1024 >= vram_512 * 1.2

    def test_vram_reduction_with_cpu_offload(self):
        """Test that CPU offload reduces VRAM requirements."""
        config_no_opt = ImageBackendConfig(
            backend_type="diffusers",
            model_id="stabilityai/stable-diffusion-xl-base-1.0",
            enable_cpu_offload=False,
        )
        backend_no_opt = DiffusersBackend(config_no_opt)
        vram_no_opt = backend_no_opt.get_required_vram()

        config_opt = ImageBackendConfig(
            backend_type="diffusers",
            model_id="stabilityai/stable-diffusion-xl-base-1.0",
            enable_cpu_offload=True,
        )
        backend_opt = DiffusersBackend(config_opt)
        vram_opt = backend_opt.get_required_vram()

        assert vram_opt < vram_no_opt
        # At least 15% savings
        assert vram_opt <= vram_no_opt * 0.85

    def test_vram_reduction_with_attention_slicing(self):
        """Test that attention slicing reduces VRAM requirements."""
        config_no_slice = ImageBackendConfig(
            backend_type="diffusers",
            model_id="runwayml/stable-diffusion-v1-5",
            enable_attention_slicing=False,
            enable_cpu_offload=False,
        )
        backend_no_slice = DiffusersBackend(config_no_slice)
        vram_no_slice = backend_no_slice.get_required_vram()

        config_slice = ImageBackendConfig(
            backend_type="diffusers",
            model_id="runwayml/stable-diffusion-v1-5",
            enable_attention_slicing=True,
            enable_cpu_offload=False,
        )
        backend_slice = DiffusersBackend(config_slice)
        vram_slice = backend_slice.get_required_vram()

        assert vram_slice < vram_no_slice

    def test_initial_state(self):
        """Test backend initial state before loading."""
        config = ImageBackendConfig(backend_type="diffusers")
        backend = DiffusersBackend(config)

        assert not backend.is_loaded()
        assert backend.pipeline is None

    def test_generate_before_load(self):
        """Test that generating before loading raises RuntimeError."""
        config = ImageBackendConfig(backend_type="diffusers")
        backend = DiffusersBackend(config)

        with pytest.raises(RuntimeError, match="Pipeline not loaded"):
            backend.generate("test prompt")

    def test_vram_usage_before_load(self):
        """Test that VRAM usage is 0 before loading."""
        config = ImageBackendConfig(backend_type="diffusers")
        backend = DiffusersBackend(config)

        assert backend.get_vram_usage() == 0.0

    def test_unload_idempotent(self):
        """Test that unload can be called multiple times safely."""
        config = ImageBackendConfig(backend_type="diffusers")
        backend = DiffusersBackend(config)

        # Should not raise
        backend.unload()
        backend.unload()
        backend.unload()

        assert not backend.is_loaded()

    def test_backend_type_property(self):
        """Test backend_type property."""
        config = ImageBackendConfig(backend_type="diffusers")
        backend = DiffusersBackend(config)

        assert backend.backend_type == "diffusers"


class TestBackendFactory:
    """Test suite for image backend factory function."""

    def test_create_diffusers_backend(self):
        """Test creating diffusers backend via factory."""
        config = ImageBackendConfig(
            backend_type="diffusers", model_id="runwayml/stable-diffusion-v1-5"
        )
        backend = create_image_backend(config)

        assert isinstance(backend, DiffusersBackend)
        assert isinstance(backend, ImageBackend)

    def test_create_unknown_backend(self):
        """Test that unknown backend type raises ValueError."""
        # Create config without validation (bypassing __post_init__)
        config = ImageBackendConfig.__new__(ImageBackendConfig)
        config.backend_type = "unknown"

        with pytest.raises(ValueError, match="Unknown image backend"):
            create_image_backend(config)
