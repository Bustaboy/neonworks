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


class TestNVIDIASMI:
    """Test NVIDIA GPU monitoring via nvidia-smi."""

    def test_query_free_vram_nvidia(self):
        """Test querying free VRAM with nvidia-smi."""
        with patch("shutil.which", return_value="/usr/bin/nvidia-smi"):
            monitor = GPUMonitor()

            with patch("subprocess.run") as mock_run:
                # Mock nvidia-smi output: 4096 MB free
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = "4096\n"

                free_gb = monitor.get_free_vram_gb()

                assert free_gb == pytest.approx(4.0, abs=0.01)  # 4096 MB = 4.0 GB
                mock_run.assert_called_once()
                # Verify correct nvidia-smi command
                args = mock_run.call_args[0][0]
                assert args[0] == "nvidia-smi"
                assert "--query-gpu=memory.free" in args
                assert "--format=csv,nounits,noheader" in args

    def test_query_total_vram_nvidia(self):
        """Test querying total VRAM with nvidia-smi."""
        with patch("shutil.which", return_value="/usr/bin/nvidia-smi"):
            monitor = GPUMonitor()

            with patch("subprocess.run") as mock_run:
                # Mock nvidia-smi output: 8192 MB total
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = "8192\n"

                total_gb = monitor.get_total_vram_gb()

                assert total_gb == pytest.approx(8.0, abs=0.01)  # 8192 MB = 8.0 GB
                # Verify correct nvidia-smi command
                args = mock_run.call_args[0][0]
                assert args[0] == "nvidia-smi"
                assert "--query-gpu=memory.total" in args

    def test_nvidia_smi_timeout(self):
        """Test timeout handling for nvidia-smi."""
        with patch("shutil.which", return_value="/usr/bin/nvidia-smi"):
            monitor = GPUMonitor()

            with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("nvidia-smi", 5.0)):
                with pytest.raises(RuntimeError, match="nvidia-smi timeout"):
                    monitor.get_free_vram_gb()

    def test_nvidia_smi_parse_error(self):
        """Test handling of invalid nvidia-smi output."""
        with patch("shutil.which", return_value="/usr/bin/nvidia-smi"):
            monitor = GPUMonitor()

            with patch("subprocess.run") as mock_run:
                # Invalid output (not a number)
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = "invalid\n"

                with pytest.raises(RuntimeError, match="Failed to parse nvidia-smi"):
                    monitor.get_free_vram_gb()

    def test_nvidia_smi_nonzero_exit(self):
        """Test handling of nvidia-smi errors (non-zero exit code)."""
        with patch("shutil.which", return_value="/usr/bin/nvidia-smi"):
            monitor = GPUMonitor()

            with patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 1
                mock_run.return_value.stderr = "Error: No devices found"

                with pytest.raises(RuntimeError, match="nvidia-smi failed"):
                    monitor.get_free_vram_gb()

    def test_nvidia_fractional_vram(self):
        """Test parsing of fractional VRAM values."""
        with patch("shutil.which", return_value="/usr/bin/nvidia-smi"):
            monitor = GPUMonitor()

            with patch("subprocess.run") as mock_run:
                # 2560 MB = 2.5 GB
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = "2560\n"

                free_gb = monitor.get_free_vram_gb()

                assert free_gb == pytest.approx(2.5, abs=0.01)


class TestROCMSMI:
    """Test AMD GPU monitoring via rocm-smi."""

    def test_query_free_vram_amd(self):
        """Test querying free VRAM with rocm-smi."""
        with patch("shutil.which") as mock_which:

            def which_side_effect(cmd):
                return "/usr/bin/rocm-smi" if cmd == "rocm-smi" else None

            mock_which.side_effect = which_side_effect

            monitor = GPUMonitor()

            with patch("subprocess.run") as mock_run:
                # Mock rocm-smi JSON output: 8GB total, 4GB used = 4GB free
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = json.dumps(
                    {
                        "card0": {
                            "VRAM Total Memory (B)": 8589934592,  # 8GB
                            "VRAM Total Used Memory (B)": 4294967296,  # 4GB used
                        }
                    }
                )

                free_gb = monitor.get_free_vram_gb()

                assert free_gb == pytest.approx(4.0, abs=0.01)  # 4GB free
                mock_run.assert_called_once()
                # Verify correct rocm-smi command
                args = mock_run.call_args[0][0]
                assert args[0] == "rocm-smi"
                assert "--showmeminfo" in args
                assert "vram" in args
                assert "--json" in args

    def test_query_total_vram_amd(self):
        """Test querying total VRAM with rocm-smi."""
        with patch("shutil.which") as mock_which:

            def which_side_effect(cmd):
                return "/usr/bin/rocm-smi" if cmd == "rocm-smi" else None

            mock_which.side_effect = which_side_effect

            monitor = GPUMonitor()

            with patch("subprocess.run") as mock_run:
                # Mock rocm-smi JSON output: 8GB total
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = json.dumps(
                    {"card0": {"VRAM Total Memory (B)": 8589934592}}  # 8GB
                )

                total_gb = monitor.get_total_vram_gb()

                assert total_gb == pytest.approx(8.0, abs=0.01)

    def test_rocm_smi_timeout(self):
        """Test timeout handling for rocm-smi."""
        with patch("shutil.which") as mock_which:

            def which_side_effect(cmd):
                return "/usr/bin/rocm-smi" if cmd == "rocm-smi" else None

            mock_which.side_effect = which_side_effect

            monitor = GPUMonitor()

            with patch(
                "subprocess.run", side_effect=subprocess.TimeoutExpired("rocm-smi", 5.0)
            ):
                with pytest.raises(RuntimeError, match="rocm-smi timeout"):
                    monitor.get_free_vram_gb()

    def test_rocm_smi_parse_error(self):
        """Test handling of invalid rocm-smi JSON output."""
        with patch("shutil.which") as mock_which:

            def which_side_effect(cmd):
                return "/usr/bin/rocm-smi" if cmd == "rocm-smi" else None

            mock_which.side_effect = which_side_effect

            monitor = GPUMonitor()

            with patch("subprocess.run") as mock_run:
                # Invalid JSON
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = "invalid json"

                with pytest.raises(RuntimeError, match="Failed to parse rocm-smi"):
                    monitor.get_free_vram_gb()

    def test_rocm_smi_nonzero_exit(self):
        """Test handling of rocm-smi errors (non-zero exit code)."""
        with patch("shutil.which") as mock_which:

            def which_side_effect(cmd):
                return "/usr/bin/rocm-smi" if cmd == "rocm-smi" else None

            mock_which.side_effect = which_side_effect

            monitor = GPUMonitor()

            with patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 1
                mock_run.return_value.stderr = "Error: No AMD devices found"

                with pytest.raises(RuntimeError, match="rocm-smi failed"):
                    monitor.get_free_vram_gb()

    def test_rocm_smi_fractional_vram(self):
        """Test parsing of fractional VRAM values."""
        with patch("shutil.which") as mock_which:

            def which_side_effect(cmd):
                return "/usr/bin/rocm-smi" if cmd == "rocm-smi" else None

            mock_which.side_effect = which_side_effect

            monitor = GPUMonitor()

            with patch("subprocess.run") as mock_run:
                # 6.5GB total, 4GB used = 2.5GB free
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = json.dumps(
                    {
                        "card0": {
                            "VRAM Total Memory (B)": 6979321856,  # 6.5GB
                            "VRAM Total Used Memory (B)": 4294967296,  # 4GB
                        }
                    }
                )

                free_gb = monitor.get_free_vram_gb()

                assert free_gb == pytest.approx(2.5, abs=0.01)


class TestCaching:
    """Test VRAM query caching."""

    def test_cache_hit_nvidia(self):
        """Test that cache is used within TTL (NVIDIA)."""
        with patch("shutil.which", return_value="/usr/bin/nvidia-smi"):
            monitor = GPUMonitor()

            with patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = "4096\n"

                # First call - should query GPU
                free1 = monitor.get_free_vram_gb()
                assert mock_run.call_count == 1

                # Second call within TTL - should use cache
                free2 = monitor.get_free_vram_gb()
                assert mock_run.call_count == 1  # Still only 1 call
                assert free1 == free2

    def test_cache_miss_after_ttl(self):
        """Test that cache expires after TTL."""
        with patch("shutil.which", return_value="/usr/bin/nvidia-smi"):
            monitor = GPUMonitor()
            monitor._cache_ttl = 0.1  # 100ms TTL for testing

            with patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = "4096\n"

                # First call
                monitor.get_free_vram_gb()
                assert mock_run.call_count == 1

                # Wait for cache to expire
                import time

                time.sleep(0.15)

                # Second call - cache expired, should query again
                monitor.get_free_vram_gb()
                assert mock_run.call_count == 2

    def test_invalidate_cache(self):
        """Test manual cache invalidation."""
        with patch("shutil.which", return_value="/usr/bin/nvidia-smi"):
            monitor = GPUMonitor()

            with patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = "4096\n"

                # First call
                monitor.get_free_vram_gb()
                assert mock_run.call_count == 1

                # Invalidate cache
                monitor.invalidate_cache()

                # Second call - cache invalidated, should query again
                monitor.get_free_vram_gb()
                assert mock_run.call_count == 2

    def test_cache_hit_amd(self):
        """Test that cache is used within TTL (AMD)."""
        with patch("shutil.which") as mock_which:

            def which_side_effect(cmd):
                return "/usr/bin/rocm-smi" if cmd == "rocm-smi" else None

            mock_which.side_effect = which_side_effect

            monitor = GPUMonitor()

            with patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = json.dumps(
                    {
                        "card0": {
                            "VRAM Total Memory (B)": 8589934592,
                            "VRAM Total Used Memory (B)": 4294967296,
                        }
                    }
                )

                # First call - should query GPU
                free1 = monitor.get_free_vram_gb()
                assert mock_run.call_count == 1

                # Second call within TTL - should use cache
                free2 = monitor.get_free_vram_gb()
                assert mock_run.call_count == 1  # Still only 1 call
                assert free1 == free2
