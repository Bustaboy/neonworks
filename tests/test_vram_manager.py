"""
Tests for SmartVRAMManager

Tests dynamic VRAM allocation with priority-based eviction and sequential loading.
NO hard percentages - services request exactly what they need.
"""

import queue
import time
from unittest.mock import MagicMock, patch

import pygame
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
        """Test status with services loaded."""
        manager = SmartVRAMManager()

        # Manually add service to registry (allocation logic tested separately)
        manager.loaded_services["llm"] = {
            "vram": 3.2,
            "priority": VRAMPriority.NORMAL,
            "loaded_at": time.time()
        }

        status = manager.get_status()

        assert status["allocated_vram"] == 3.2
        assert len(status["loaded_services"]) == 1
        assert status["loaded_services"][0]["name"] == "llm"
        assert status["loaded_services"][0]["vram"] == 3.2
        assert status["loaded_services"][0]["priority"] == VRAMPriority.NORMAL


class TestRequestVRAM:
    """Test VRAM allocation logic."""

    def test_allocate_with_sufficient_vram(self, mock_gpu_monitor):
        """Test successful allocation when enough VRAM available."""
        mock_gpu_monitor.get_free_vram_gb.return_value = 7.5  # 8GB - 0.5GB safety

        manager = SmartVRAMManager()

        # Request 4.0GB for image service
        success = manager.request_vram(
            service_name="image",
            required_vram_gb=4.0,
            priority=VRAMPriority.USER_REQUESTED
        )

        assert success is True
        assert "image" in manager.loaded_services
        assert manager.loaded_services["image"]["vram"] == 4.0
        assert manager.loaded_services["image"]["priority"] == VRAMPriority.USER_REQUESTED

        # Verify status
        status = manager.get_status()
        assert status["allocated_vram"] == 4.0

    def test_allocate_multiple_services(self, mock_gpu_monitor):
        """Test allocating VRAM for multiple services."""
        mock_gpu_monitor.get_free_vram_gb.return_value = 7.5

        manager = SmartVRAMManager()

        # Allocate LLM (3.2GB)
        success1 = manager.request_vram("llm", 3.2, VRAMPriority.NORMAL)
        assert success1 is True

        # Allocate Image (2.0GB) - total 5.2GB
        success2 = manager.request_vram("image", 2.0, VRAMPriority.USER_REQUESTED)
        assert success2 is True

        # Verify both loaded
        assert len(manager.loaded_services) == 2
        assert manager.loaded_services["llm"]["vram"] == 3.2
        assert manager.loaded_services["image"]["vram"] == 2.0

        status = manager.get_status()
        assert status["allocated_vram"] == 5.2

    def test_update_existing_service(self, mock_gpu_monitor):
        """Test updating VRAM allocation for existing service."""
        mock_gpu_monitor.get_free_vram_gb.return_value = 7.5

        manager = SmartVRAMManager()

        # Initial allocation: 4.0GB
        manager.request_vram("image", 4.0, VRAMPriority.NORMAL)
        assert manager.loaded_services["image"]["vram"] == 4.0

        # Update allocation: 6.0GB (e.g., switched to larger model)
        manager.request_vram("image", 6.0, VRAMPriority.USER_REQUESTED)

        # Should update, not duplicate
        assert len(manager.loaded_services) == 1
        assert manager.loaded_services["image"]["vram"] == 6.0
        assert manager.loaded_services["image"]["priority"] == VRAMPriority.USER_REQUESTED

    def test_allocation_emits_event(self, mock_gpu_monitor):
        """Test that successful allocation emits VRAM_ALLOCATED event."""
        mock_gpu_monitor.get_free_vram_gb.return_value = 7.5

        manager = SmartVRAMManager()

        # Clear event queue before test
        pygame.event.clear()

        # Request VRAM
        manager.request_vram("image", 4.0, VRAMPriority.USER_REQUESTED)

        # Check for VRAM_ALLOCATED event
        events = pygame.event.get()
        vram_events = [e for e in events if e.type == pygame.USEREVENT + 9]

        assert len(vram_events) == 1
        event = vram_events[0]
        assert event.service == "image"
        assert event.vram_allocated == 4.0
        assert event.priority == VRAMPriority.USER_REQUESTED


class TestAllocationFailure:
    """Test VRAM allocation failure cases."""

    def test_insufficient_vram_returns_false(self, mock_gpu_monitor):
        """Test allocation fails when not enough VRAM."""
        # Only 2.0GB free
        mock_gpu_monitor.get_free_vram_gb.return_value = 2.5  # 2.5 - 0.5 = 2.0GB available

        manager = SmartVRAMManager()

        # Try to allocate 4.0GB (insufficient)
        success = manager.request_vram("image", 4.0, VRAMPriority.NORMAL)

        assert success is False
        assert "image" not in manager.loaded_services
        assert manager.get_status()["allocated_vram"] == 0.0

    def test_insufficient_vram_with_loaded_service(self, mock_gpu_monitor):
        """Test allocation fails when other services using VRAM."""
        mock_gpu_monitor.get_free_vram_gb.return_value = 7.5

        manager = SmartVRAMManager()

        # Load LLM (5.0GB)
        manager.request_vram("llm", 5.0, VRAMPriority.NORMAL)

        # Try to load Image (4.0GB) - would need 9.0GB total (exceeds 7.5GB available)
        mock_gpu_monitor.get_free_vram_gb.return_value = 2.5  # Simulate LLM using 5GB
        success = manager.request_vram("image", 4.0, VRAMPriority.NORMAL)

        assert success is False
        assert "image" not in manager.loaded_services
        assert len(manager.loaded_services) == 1  # Only LLM loaded

    def test_allocation_failure_emits_event(self, mock_gpu_monitor):
        """Test that failed allocation emits VRAM_ALLOCATION_FAILED event."""
        mock_gpu_monitor.get_free_vram_gb.return_value = 2.0  # Insufficient

        manager = SmartVRAMManager()

        # Clear event queue
        pygame.event.clear()

        # Try to allocate 4.0GB (will fail)
        manager.request_vram("image", 4.0, VRAMPriority.NORMAL)

        # Check for VRAM_ALLOCATION_FAILED event
        events = pygame.event.get()
        failed_events = [e for e in events if e.type == pygame.USEREVENT + 11]

        assert len(failed_events) == 1
        event = failed_events[0]
        assert event.service == "image"
        assert event.required_vram == 4.0
        assert event.queued is False  # Not queued in this iteration
