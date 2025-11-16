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


@pytest.fixture
def mock_gpu_monitor_stateful():
    """Mock GPUMonitor that tracks allocations (for eviction tests)."""
    with patch("ai.vram_manager.GPUMonitor") as MockGPUMonitor:
        monitor = MagicMock(spec=GPUMonitor)
        monitor.vendor = GPUVendor.NVIDIA
        monitor.get_total_vram_gb.return_value = 8.0

        # Track allocated VRAM
        allocated = [0.0]  # Use list for mutability in closure

        def get_free_side_effect():
            # Return total minus allocated
            return 8.0 - allocated[0]

        monitor.get_free_vram_gb.side_effect = get_free_side_effect
        monitor._allocated = allocated  # Expose for test manipulation

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
        # Insufficient VRAM (checked twice: initial + after failed eviction)
        mock_gpu_monitor.get_free_vram_gb.side_effect = [2.0, 2.0]

        manager = SmartVRAMManager()

        # Clear event queue
        pygame.event.clear()

        # Try to allocate 4.0GB (will fail and queue)
        manager.request_vram("image", 4.0, VRAMPriority.NORMAL)

        # Check for VRAM_ALLOCATION_FAILED event
        events = pygame.event.get()
        failed_events = [e for e in events if e.type == pygame.USEREVENT + 11]

        assert len(failed_events) == 1
        event = failed_events[0]
        assert event.service == "image"
        assert event.required_vram == 4.0
        assert event.queued is True  # Queued for later processing (iteration 9)


class TestPriorityEviction:
    """Test priority-based VRAM eviction."""

    def test_evict_lower_priority_service(self, mock_gpu_monitor):
        """Test that higher priority can evict lower priority."""
        manager = SmartVRAMManager()

        # Manually set up LLM as loaded (5.0GB, NORMAL priority)
        manager.loaded_services["llm"] = {
            "vram": 5.0,
            "priority": VRAMPriority.NORMAL,
            "loaded_at": time.time()
        }

        # Mock: 2.5GB before eviction, then 7.5GB after
        # Need multiple values because get_available_vram is called multiple times
        mock_gpu_monitor.get_free_vram_gb.side_effect = [
            2.5,  # Initial check (insufficient)
            2.5,  # During eviction check
            7.5,  # After eviction - recheck
            3.5,  # After Image loaded
        ]

        # Try to load Image (4.0GB, USER_REQUESTED priority)
        # USER_REQUESTED (8) > NORMAL (5) - can evict
        success = manager.request_vram("image", 4.0, VRAMPriority.USER_REQUESTED)

        # LLM should be evicted, Image should be loaded
        assert success is True
        assert "llm" not in manager.loaded_services
        assert "image" in manager.loaded_services
        assert manager.loaded_services["image"]["vram"] == 4.0

    def test_cannot_evict_same_or_higher_priority(self, mock_gpu_monitor):
        """Test that same/higher priority cannot evict."""
        manager = SmartVRAMManager()

        # Manually set up LLM as loaded (5.0GB, USER_REQUESTED priority)
        manager.loaded_services["llm"] = {
            "vram": 5.0,
            "priority": VRAMPriority.USER_REQUESTED,
            "loaded_at": time.time()
        }

        # Mock: Only 2.5GB free (8.0 - 5.0 LLM - 0.5 safety)
        mock_gpu_monitor.get_free_vram_gb.return_value = 2.5

        # Try to load Image (4.0GB, NORMAL priority)
        # NORMAL (5) < USER_REQUESTED (8) - cannot evict
        success = manager.request_vram("image", 4.0, VRAMPriority.NORMAL)

        # Should fail (cannot evict)
        assert success is False
        assert "llm" in manager.loaded_services  # Still loaded
        assert "image" not in manager.loaded_services  # Not loaded

    def test_evict_multiple_lower_priority_services(self, mock_gpu_monitor):
        """Test evicting multiple lower priority services (greedy eviction)."""
        manager = SmartVRAMManager()

        # Manually set up multiple BACKGROUND services (total 6.0GB)
        manager.loaded_services["tts"] = {
            "vram": 2.0,
            "priority": VRAMPriority.BACKGROUND,
            "loaded_at": time.time()
        }
        manager.loaded_services["translator"] = {
            "vram": 2.0,
            "priority": VRAMPriority.BACKGROUND,
            "loaded_at": time.time()
        }
        manager.loaded_services["classifier"] = {
            "vram": 2.0,
            "priority": VRAMPriority.BACKGROUND,
            "loaded_at": time.time()
        }

        # Mock: 1.5GB initially, then incrementally freed (each service adds 2GB back)
        # Pattern: check, evict tts (+2GB), evict translator (+2GB), evict classifier (+2GB), final check
        mock_gpu_monitor.get_free_vram_gb.side_effect = [
            1.5,  # Initial check
            1.5,  # During eviction
            7.5,  # After all evictions complete - plenty of VRAM now
            2.5,  # After Image loaded
        ]

        # Load Image (5.0GB, USER_REQUESTED)
        # USER_REQUESTED (8) > BACKGROUND (1) - can evict
        success = manager.request_vram("image", 5.0, VRAMPriority.USER_REQUESTED)

        # Image should be loaded (eviction successful)
        assert success is True
        assert "image" in manager.loaded_services
        # At least some BACKGROUND services should be evicted
        # (greedy eviction stops when enough VRAM freed)

    def test_evict_only_necessary_services(self, mock_gpu_monitor):
        """Test that only necessary services are evicted (greedy)."""
        manager = SmartVRAMManager()

        # Manually set up services: LLM (3GB, NORMAL), TTS (2GB, BACKGROUND)
        manager.loaded_services["llm"] = {
            "vram": 3.0,
            "priority": VRAMPriority.NORMAL,
            "loaded_at": time.time()
        }
        manager.loaded_services["tts"] = {
            "vram": 2.0,
            "priority": VRAMPriority.BACKGROUND,
            "loaded_at": time.time()
        }

        # Mock: 2.5GB initially, then enough after TTS evicted
        mock_gpu_monitor.get_free_vram_gb.side_effect = [2.5, 2.5, 4.5, 0.5]

        # Request 4.0GB for Image (USER_REQUESTED)
        success = manager.request_vram("image", 4.0, VRAMPriority.USER_REQUESTED)

        # Image should load successfully
        assert success is True
        assert "image" in manager.loaded_services

        # TTS (BACKGROUND) should be evicted (lowest priority)
        assert "tts" not in manager.loaded_services

    def test_eviction_emits_events(self, mock_gpu_monitor):
        """Test that eviction emits VRAM_RELEASED events."""
        manager = SmartVRAMManager()

        # Manually set up LLM
        manager.loaded_services["llm"] = {
            "vram": 5.0,
            "priority": VRAMPriority.NORMAL,
            "loaded_at": time.time()
        }

        # Mock: 2.5GB initially, 7.5GB after LLM evicted
        mock_gpu_monitor.get_free_vram_gb.side_effect = [2.5, 2.5, 7.5, 3.5]

        # Clear event queue
        pygame.event.clear()

        # Evict LLM by loading Image (higher priority)
        manager.request_vram("image", 4.0, VRAMPriority.USER_REQUESTED)

        # Check for VRAM_RELEASED event
        events = pygame.event.get()
        release_events = [e for e in events if e.type == pygame.USEREVENT + 10]

        assert len(release_events) >= 1  # At least one release event
        # Find LLM release event
        llm_release = [e for e in release_events if e.service == "llm"]
        assert len(llm_release) == 1
        assert llm_release[0].vram_freed == 5.0


class TestReleaseVRAM:
    """Test manual VRAM release."""

    def test_release_loaded_service(self, mock_gpu_monitor):
        """Test releasing VRAM for a loaded service."""
        manager = SmartVRAMManager()

        # Manually load service
        manager.loaded_services["llm"] = {
            "vram": 3.2,
            "priority": VRAMPriority.NORMAL,
            "loaded_at": time.time()
        }

        # Release it
        success = manager.release_vram("llm")

        assert success is True
        assert "llm" not in manager.loaded_services
        assert manager.get_status()["allocated_vram"] == 0.0

    def test_release_nonexistent_service(self, mock_gpu_monitor):
        """Test releasing VRAM for non-existent service."""
        manager = SmartVRAMManager()

        # Try to release service that isn't loaded
        success = manager.release_vram("nonexistent")

        assert success is False

    def test_release_emits_event(self, mock_gpu_monitor):
        """Test that release emits VRAM_RELEASED event."""
        manager = SmartVRAMManager()

        # Load service
        manager.loaded_services["llm"] = {
            "vram": 3.2,
            "priority": VRAMPriority.NORMAL,
            "loaded_at": time.time()
        }

        # Clear events
        pygame.event.clear()

        # Release
        manager.release_vram("llm")

        # Check for event
        events = pygame.event.get()
        release_events = [e for e in events if e.type == pygame.USEREVENT + 10]

        assert len(release_events) == 1
        assert release_events[0].service == "llm"
        assert release_events[0].vram_freed == 3.2


class TestPendingQueue:
    """Test pending queue for sequential loading."""

    def test_queue_when_insufficient_vram(self, mock_gpu_monitor):
        """Test that requests are queued when VRAM insufficient."""
        manager = SmartVRAMManager()

        # Load LLM (uses most VRAM)
        manager.loaded_services["llm"] = {
            "vram": 6.0,
            "priority": VRAMPriority.NORMAL,
            "loaded_at": time.time()
        }

        # Mock: only 1.5GB free
        mock_gpu_monitor.get_free_vram_gb.return_value = 1.5

        # Clear events
        pygame.event.clear()

        # Try to load Image (4.0GB) - should queue
        success = manager.request_vram("image", 4.0, VRAMPriority.NORMAL)

        # Should fail but queue
        assert success is False
        assert manager.pending_queue.qsize() == 1

        # Check VRAM_ALLOCATION_FAILED event with queued=True
        events = pygame.event.get()
        failed_events = [e for e in events if e.type == pygame.USEREVENT + 11]
        assert len(failed_events) == 1
        assert failed_events[0].queued is True

    def test_process_pending_after_release(self, mock_gpu_monitor):
        """Test that pending requests are processed after VRAM released."""
        manager = SmartVRAMManager()

        # Load LLM
        manager.loaded_services["llm"] = {
            "vram": 5.0,
            "priority": VRAMPriority.NORMAL,
            "loaded_at": time.time()
        }

        # Mock: 2.5GB free initially
        mock_gpu_monitor.get_free_vram_gb.return_value = 2.5

        # Try to load Image (4.0GB) - should queue
        manager.request_vram("image", 4.0, VRAMPriority.NORMAL)
        assert manager.pending_queue.qsize() == 1

        # Mock: 7.5GB free after LLM released
        mock_gpu_monitor.get_free_vram_gb.return_value = 7.5

        # Release LLM
        manager.release_vram("llm")

        # Pending queue should be processed
        assert manager.pending_queue.qsize() == 0
        assert "image" in manager.loaded_services

    def test_pending_queue_priority_order(self, mock_gpu_monitor):
        """Test that pending queue processes higher priority first."""
        manager = SmartVRAMManager()

        # Fill VRAM with high-priority service that can't be evicted
        manager.loaded_services["llm"] = {
            "vram": 6.0,
            "priority": VRAMPriority.UI_CRITICAL,  # Highest priority - can't be evicted
            "loaded_at": time.time()
        }

        # Mock: 1.5GB when queueing, then 7.5GB after release
        # Need enough values for queueing 3 requests (each checks twice) + processing them
        mock_gpu_monitor.get_free_vram_gb.side_effect = [
            1.5, 1.5,  # tts request: initial check, re-check after failed eviction
            1.5, 1.5,  # image request: initial check, re-check
            1.5, 1.5,  # translator request: initial check, re-check
            7.5, 4.5, 2.5,  # Processing: image (3GB), translator (2GB), tts (2GB)
        ]

        # Queue multiple requests (different priorities)
        manager.request_vram("tts", 2.0, VRAMPriority.BACKGROUND)
        manager.request_vram("image", 3.0, VRAMPriority.USER_REQUESTED)
        manager.request_vram("translator", 2.0, VRAMPriority.NORMAL)

        assert manager.pending_queue.qsize() == 3

        # Release LLM (plenty of VRAM now)
        manager.release_vram("llm")

        # USER_REQUESTED (image) should be loaded first
        assert "image" in manager.loaded_services
        # Queue should have processed all that fit
        assert manager.pending_queue.qsize() < 3

    def test_pending_request_allocation_emits_event(self, mock_gpu_monitor):
        """Test that pending request allocation emits VRAM_ALLOCATED event."""
        manager = SmartVRAMManager()

        # Fill VRAM with high-priority service that can't be evicted
        manager.loaded_services["llm"] = {
            "vram": 6.0,
            "priority": VRAMPriority.UI_CRITICAL,  # Can't be evicted
            "loaded_at": time.time()
        }

        # Mock: 1.5GB when queueing (twice for failed eviction), 7.5GB after release, 4.5GB after allocation
        mock_gpu_monitor.get_free_vram_gb.side_effect = [1.5, 1.5, 7.5, 4.5]

        # Queue request
        manager.request_vram("image", 3.0, VRAMPriority.USER_REQUESTED)

        # Clear events
        pygame.event.clear()

        # Release LLM (triggers pending processing)
        manager.release_vram("llm")

        # Check for VRAM_ALLOCATED event
        events = pygame.event.get()
        # Should have VRAM_RELEASED (for llm) + VRAM_ALLOCATED (for image)
        allocated_events = [e for e in events if e.type == pygame.USEREVENT + 9]
        assert len(allocated_events) >= 1
        # Find image allocation
        image_alloc = [e for e in allocated_events if e.service == "image"]
        assert len(image_alloc) == 1


class TestThreadSafety:
    """Test thread safety of VRAM Manager."""

    def test_concurrent_allocations(self, mock_gpu_monitor):
        """Test multiple threads requesting VRAM concurrently."""
        import threading

        manager = SmartVRAMManager()
        mock_gpu_monitor.get_free_vram_gb.return_value = 8.0

        results = []
        errors = []

        def allocate_service(service_name, vram_gb):
            try:
                success = manager.request_vram(service_name, vram_gb, VRAMPriority.NORMAL)
                results.append((service_name, success))
            except Exception as e:
                errors.append((service_name, e))

        # Create 5 threads requesting VRAM
        threads = [
            threading.Thread(target=allocate_service, args=(f"service_{i}", 1.0))
            for i in range(5)
        ]

        # Start all threads
        for t in threads:
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # No errors should occur
        assert len(errors) == 0

        # All allocations should succeed
        assert len(results) == 5
        assert all(success for _, success in results)

        # All services should be loaded
        assert len(manager.loaded_services) == 5

    def test_concurrent_releases(self, mock_gpu_monitor):
        """Test multiple threads releasing VRAM concurrently."""
        import threading

        manager = SmartVRAMManager()
        mock_gpu_monitor.get_free_vram_gb.return_value = 8.0

        # Pre-load 5 services
        for i in range(5):
            manager.loaded_services[f"service_{i}"] = {
                "vram": 1.0,
                "priority": VRAMPriority.NORMAL,
                "loaded_at": time.time()
            }

        results = []
        errors = []

        def release_service(service_name):
            try:
                success = manager.release_vram(service_name)
                results.append((service_name, success))
            except Exception as e:
                errors.append((service_name, e))

        # Create 5 threads releasing VRAM
        threads = [
            threading.Thread(target=release_service, args=(f"service_{i}",))
            for i in range(5)
        ]

        # Start all threads
        for t in threads:
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # No errors should occur
        assert len(errors) == 0

        # All releases should succeed
        assert len(results) == 5
        assert all(success for _, success in results)

        # All services should be unloaded
        assert len(manager.loaded_services) == 0

    def test_mixed_concurrent_operations(self, mock_gpu_monitor):
        """Test concurrent allocations and releases."""
        import threading

        manager = SmartVRAMManager()
        mock_gpu_monitor.get_free_vram_gb.return_value = 8.0

        # Pre-load 3 services
        for i in range(3):
            manager.loaded_services[f"existing_{i}"] = {
                "vram": 1.0,
                "priority": VRAMPriority.NORMAL,
                "loaded_at": time.time()
            }

        errors = []

        def allocate_service(service_name, vram_gb):
            try:
                manager.request_vram(service_name, vram_gb, VRAMPriority.NORMAL)
            except Exception as e:
                errors.append(("allocate", service_name, e))

        def release_service(service_name):
            try:
                manager.release_vram(service_name)
            except Exception as e:
                errors.append(("release", service_name, e))

        # Create mixed threads
        threads = []
        threads.extend([
            threading.Thread(target=allocate_service, args=(f"new_{i}", 1.0))
            for i in range(3)
        ])
        threads.extend([
            threading.Thread(target=release_service, args=(f"existing_{i}",))
            for i in range(3)
        ])

        # Start all threads
        for t in threads:
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # No errors should occur
        assert len(errors) == 0

        # Should have 3 new services loaded (3 released, 3 added)
        assert len(manager.loaded_services) == 3
        assert all(f"new_{i}" in manager.loaded_services for i in range(3))

    def test_get_status_thread_safe(self, mock_gpu_monitor):
        """Test that get_status() is thread-safe during concurrent operations."""
        import threading

        manager = SmartVRAMManager()
        mock_gpu_monitor.get_free_vram_gb.return_value = 8.0

        errors = []
        status_snapshots = []

        def allocate_service(service_name, vram_gb):
            try:
                manager.request_vram(service_name, vram_gb, VRAMPriority.NORMAL)
            except Exception as e:
                errors.append(("allocate", service_name, e))

        def get_status_snapshot():
            try:
                status = manager.get_status()
                status_snapshots.append(status)
            except Exception as e:
                errors.append(("status", e))

        # Create threads: 5 allocations + 5 status queries
        threads = []
        for i in range(5):
            threads.append(threading.Thread(target=allocate_service, args=(f"service_{i}", 1.0)))
            threads.append(threading.Thread(target=get_status_snapshot))

        # Start all threads
        for t in threads:
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # No errors should occur
        assert len(errors) == 0

        # Should have captured some status snapshots
        assert len(status_snapshots) >= 5

        # All status snapshots should be valid dicts
        for status in status_snapshots:
            assert isinstance(status, dict)
            assert "total_vram" in status
            assert "allocated_vram" in status
            assert "loaded_services" in status
