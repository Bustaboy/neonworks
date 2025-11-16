"""
Tests for GPU Monitor

Tests GPU vendor detection, VRAM monitoring for NVIDIA and AMD GPUs.
Uses mocks to avoid requiring actual GPU hardware.
"""

import json
import subprocess
from unittest.mock import MagicMock, Mock, patch

import pytest

from ai.gpu_monitor import GPUMonitor, GPUVendor, SystemRequirementError


class TestGPUVendor:
    """Test GPUVendor enum."""

    def test_enum_values(self):
        """Test that GPUVendor enum has correct values."""
        assert GPUVendor.NVIDIA.value == "nvidia"
        assert GPUVendor.AMD.value == "amd"
        assert GPUVendor.UNKNOWN.value == "unknown"


class TestGPUDetection:
    """Test GPU vendor detection logic."""

    def test_detect_nvidia(self):
        """Test detection of NVIDIA GPU (nvidia-smi exists)."""
        with patch("shutil.which") as mock_which:
            mock_which.return_value = "/usr/bin/nvidia-smi"

            monitor = GPUMonitor()

            assert monitor.vendor == GPUVendor.NVIDIA
            mock_which.assert_called_with("nvidia-smi")

    def test_detect_amd(self):
        """Test detection of AMD GPU (rocm-smi exists)."""
        with patch("shutil.which") as mock_which:

            def which_side_effect(cmd):
                if cmd == "nvidia-smi":
                    return None  # NVIDIA not found
                elif cmd == "rocm-smi":
                    return "/usr/bin/rocm-smi"  # AMD found
                return None

            mock_which.side_effect = which_side_effect

            monitor = GPUMonitor()

            assert monitor.vendor == GPUVendor.AMD
            # nvidia-smi checked first, then rocm-smi
            assert mock_which.call_count == 2

    def test_detect_unknown(self):
        """Test detection when no GPU monitoring tool exists."""
        with patch("shutil.which", return_value=None):
            # Should raise error, not return UNKNOWN
            with pytest.raises(SystemRequirementError, match="No supported GPU monitoring tool"):
                GPUMonitor()

    def test_nvidia_preferred_when_both_exist(self):
        """Test that NVIDIA is preferred if both tools exist."""
        with patch("shutil.which") as mock_which:
            # Both exist
            mock_which.return_value = "/usr/bin/nvidia-smi"

            monitor = GPUMonitor()

            assert monitor.vendor == GPUVendor.NVIDIA
            # Should stop after finding nvidia-smi
            mock_which.assert_called_once_with("nvidia-smi")


class TestGPUMonitorInit:
    """Test GPUMonitor initialization."""

    def test_init_nvidia_success(self):
        """Test successful initialization with NVIDIA GPU."""
        with patch("shutil.which", return_value="/usr/bin/nvidia-smi"):
            monitor = GPUMonitor()

            assert monitor.vendor == GPUVendor.NVIDIA
            assert monitor._vram_cache is None
            assert monitor._vram_cache_time == 0
            assert monitor._cache_ttl == 2.0

    def test_init_amd_success(self):
        """Test successful initialization with AMD GPU."""
        with patch("shutil.which") as mock_which:

            def which_side_effect(cmd):
                return "/usr/bin/rocm-smi" if cmd == "rocm-smi" else None

            mock_which.side_effect = which_side_effect

            monitor = GPUMonitor()

            assert monitor.vendor == GPUVendor.AMD

    def test_init_no_gpu_raises_error(self):
        """Test that initialization fails with helpful error when no GPU tool found."""
        with patch("shutil.which", return_value=None):
            with pytest.raises(SystemRequirementError) as exc_info:
                GPUMonitor()

            error_msg = str(exc_info.value)
            # Check error message is helpful
            assert "No supported GPU monitoring tool" in error_msg
            assert "nvidia-smi" in error_msg
            assert "rocm-smi" in error_msg
            assert "NVIDIA" in error_msg or "nvidia" in error_msg.lower()
            assert "AMD" in error_msg or "amd" in error_msg.lower()

    def test_error_message_includes_installation_links(self):
        """Test that error message includes installation guidance."""
        with patch("shutil.which", return_value=None):
            with pytest.raises(SystemRequirementError) as exc_info:
                GPUMonitor()

            error_msg = str(exc_info.value)
            # Should mention drivers or installation
            assert any(
                keyword in error_msg.lower()
                for keyword in ["install", "driver", "http", "guide"]
            )
