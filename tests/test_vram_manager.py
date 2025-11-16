"""
Tests for SmartVRAMManager

Tests dynamic VRAM allocation with priority-based eviction and sequential loading.
NO hard percentages - services request exactly what they need.
"""

import queue
import time
from unittest.mock import MagicMock, patch

import pytest

from ai.gpu_monitor import GPUMonitor, GPUVendor
from ai.vram_manager import SmartVRAMManager
from ai.vram_priority import VRAMPriority


@pytest.fixture
def mock_gpu_monitor():
    """Mock GPUMonitor with 8GB GPU."""
    with patch("ai.vram_manager.GPUMonitor") as MockGPUMonitor:
        monitor = MagicMock(spec=GPUMonitor)
        monitor.vendor = GPUVendor.NVIDIA
        monitor.get_total_vram_gb.return_value = 8.0
        monitor.get_free_vram_gb.return_value = 7.5  # 8 - 0.5 safety buffer

        MockGPUMonitor.return_value = monitor

        yield monitor


class TestSmartVRAMManagerInit:
    """Test SmartVRAMManager initialization."""

    def test_initialization_auto_detect_vram(self, mock_gpu_monitor):
        """Test initialization with auto-detected total VRAM."""
        manager = SmartVRAMManager()

        # Should auto-detect from GPU
        assert manager.total_vram == 8.0
        assert manager.safety_buffer == 0.5  # Default
        assert manager.available_vram == 7.5  # 8.0 - 0.5
        mock_gpu_monitor.get_total_vram_gb.assert_called_once()

    def test_initialization_custom_vram(self, mock_gpu_monitor):
        """Test initialization with explicitly specified total VRAM."""
        manager = SmartVRAMManager(total_vram_gb=16.0)

        # Should use specified value, not query GPU
        assert manager.total_vram == 16.0
        assert manager.available_vram == 15.5  # 16.0 - 0.5
        mock_gpu_monitor.get_total_vram_gb.assert_not_called()

    def test_initialization_custom_safety_buffer(self, mock_gpu_monitor):
        """Test initialization with custom safety buffer."""
        manager = SmartVRAMManager(safety_buffer_gb=1.0)

        assert manager.safety_buffer == 1.0
        assert manager.available_vram == 7.0  # 8.0 - 1.0

    def test_initialization_creates_empty_registry(self, mock_gpu_monitor):
        """Test that service registry starts empty."""
        manager = SmartVRAMManager()

        assert len(manager.loaded_services) == 0
        assert manager.pending_queue.empty()

    def test_initialization_no_gpu_raises_error(self):
        """Test that initialization fails if no GPU monitoring tool found."""
        with patch("ai.vram_manager.GPUMonitor") as MockGPU:
            from ai.gpu_monitor import SystemRequirementError

            MockGPU.side_effect = SystemRequirementError("No GPU")

            with pytest.raises(SystemRequirementError):
                SmartVRAMManager()


class TestGetAvailableVRAM:
    """Test get_available_vram() method."""

    def test_get_available_vram_via_gpu_monitor(self, mock_gpu_monitor):
        """Test querying available VRAM via GPUMonitor."""
        mock_gpu_monitor.get_free_vram_gb.return_value = 6.0

        manager = SmartVRAMManager()
        available = manager.get_available_vram()

        # Should query GPU and subtract safety buffer
        assert available == pytest.approx(5.5, abs=0.01)  # 6.0 - 0.5
        mock_gpu_monitor.get_free_vram_gb.assert_called()

    def test_get_available_vram_uses_gpu_monitor_cache(self, mock_gpu_monitor):
        """Test that GPUMonitor's internal cache is used."""
        mock_gpu_monitor.get_free_vram_gb.return_value = 6.0

        manager = SmartVRAMManager()

        # Multiple calls - GPUMonitor handles caching internally
        manager.get_available_vram()
        manager.get_available_vram()
        manager.get_available_vram()

        # GPUMonitor called each time (it handles caching internally)
        assert mock_gpu_monitor.get_free_vram_gb.call_count == 3

    def test_get_available_vram_minimum_zero(self, mock_gpu_monitor):
        """Test that available VRAM is never negative."""
        # GPU reports less than safety buffer
        mock_gpu_monitor.get_free_vram_gb.return_value = 0.2

        manager = SmartVRAMManager()
        available = manager.get_available_vram()

        # Should return 0, not negative
        assert available == 0.0


class TestGetStatus:
    """Test get_status() diagnostic method."""

    def test_status_empty(self, mock_gpu_monitor):
        """Test status with no services loaded."""
        manager = SmartVRAMManager()

        status = manager.get_status()

        assert status["total_vram"] == 8.0
        assert status["safety_buffer"] == 0.5
        assert status["allocated_vram"] == 0.0
        assert status["loaded_services"] == []
        assert status["pending_count"] == 0

    def test_status_with_services(self, mock_gpu_monitor):
        """Test status with services loaded (will implement in next iteration)."""
        # This test will be expanded in iteration 7
        pass
