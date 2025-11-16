"""
Integration Tests for ImageService + VRAM Manager

Tests the integration between ImageService and SmartVRAMManager,
verifying VRAM allocation, eviction, and sequential loading.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock

import pygame  # Imported AFTER conftest sets SDL environment variables

from ai.image_service import ImageService
from ai.vram_manager import SmartVRAMManager
from ai.vram_priority import VRAMPriority
from ai.gpu_monitor import GPUMonitor, GPUVendor


@pytest.fixture
def mock_gpu_monitor():
    """Mock GPUMonitor for integration tests."""
    with patch("ai.vram_manager.GPUMonitor") as MockGPUMonitor:
        monitor = MagicMock(spec=GPUMonitor)
        monitor.vendor = GPUVendor.NVIDIA
        monitor.get_total_vram_gb.return_value = 8.0
        monitor.get_free_vram_gb.return_value = 7.5  # 8 - 0.5 safety buffer

        MockGPUMonitor.return_value = monitor

        yield monitor


@pytest.fixture
def mock_backend():
    """Mock DiffusersBackend."""
    backend = Mock()
    backend.is_loaded.return_value = False
    backend.load.return_value = None
    backend.unload.return_value = None
    backend.get_vram_estimate.return_value = 4.0  # SDXL requires 4GB
    backend.generate.return_value = "/output/image.png"
    return backend


class TestImageServiceVRAMIntegration:
    """Test ImageService integration with VRAM Manager."""

    def test_load_model_requests_vram(self, mock_backend, mock_gpu_monitor):
        """Test that load_model() requests VRAM from manager."""
        vram_manager = SmartVRAMManager()
        service = ImageService(
            backend=mock_backend,
            vram_manager=vram_manager
        )

        # Load model
        success = service.load_model()

        assert success is True
        assert service.is_loaded is True

        # Check VRAM manager state
        status = vram_manager.get_status()
        assert status["allocated_vram"] == 4.0
        assert len(status["loaded_services"]) == 1
        assert status["loaded_services"][0]["name"] == "image_service"

    def test_load_model_fails_when_vram_insufficient(self, mock_backend, mock_gpu_monitor):
        """Test that load_model() fails when insufficient VRAM."""
        # Only 2GB available
        mock_gpu_monitor.get_free_vram_gb.return_value = 2.0

        vram_manager = SmartVRAMManager()
        service = ImageService(
            backend=mock_backend,
            vram_manager=vram_manager
        )

        # Load model should fail
        success = service.load_model()

        assert success is False
        assert service.is_loaded is False

        # VRAM manager should have no allocations
        status = vram_manager.get_status()
        assert status["allocated_vram"] == 0.0

    def test_unload_model_releases_vram(self, mock_backend, mock_gpu_monitor):
        """Test that unload_model() releases VRAM."""
        vram_manager = SmartVRAMManager()
        service = ImageService(
            backend=mock_backend,
            vram_manager=vram_manager
        )

        # Load then unload
        service.load_model()
        assert vram_manager.get_status()["allocated_vram"] == 4.0

        service.unload_model()

        # VRAM should be released
        status = vram_manager.get_status()
        assert status["allocated_vram"] == 0.0
        assert len(status["loaded_services"]) == 0

    def test_load_emits_vram_allocated_event(self, mock_backend, mock_gpu_monitor):
        """Test that loading emits VRAM_ALLOCATED event."""
        vram_manager = SmartVRAMManager()
        service = ImageService(
            backend=mock_backend,
            vram_manager=vram_manager
        )

        pygame.event.clear()

        service.load_model()

        # Check for VRAM_ALLOCATED event
        events = pygame.event.get()
        vram_events = [e for e in events if e.type == pygame.USEREVENT + 9]

        assert len(vram_events) == 1
        event = vram_events[0]
        assert event.service == "image_service"
        assert event.vram_allocated == 4.0
        assert event.priority == VRAMPriority.USER_REQUESTED

    def test_unload_emits_vram_released_event(self, mock_backend, mock_gpu_monitor):
        """Test that unloading emits VRAM_RELEASED event."""
        vram_manager = SmartVRAMManager()
        service = ImageService(
            backend=mock_backend,
            vram_manager=vram_manager
        )

        service.load_model()
        pygame.event.clear()

        service.unload_model()

        # Check for VRAM_RELEASED event
        events = pygame.event.get()
        release_events = [e for e in events if e.type == pygame.USEREVENT + 10]

        assert len(release_events) == 1
        event = release_events[0]
        assert event.service == "image_service"
        assert event.vram_freed == 4.0

    def test_worker_processes_with_vram_manager(self, mock_backend, mock_gpu_monitor):
        """Test that worker thread works with VRAM manager."""
        import time
        from ai.image_request import RequestState

        vram_manager = SmartVRAMManager()
        service = ImageService(
            backend=mock_backend,
            vram_manager=vram_manager
        )

        # Start worker
        service.start_worker()

        # Submit request
        request = service.submit_request(prompt="test")

        # Wait for processing
        time.sleep(0.5)

        # Request should complete
        assert request.state == RequestState.COMPLETE

        # VRAM should be allocated
        status = vram_manager.get_status()
        assert status["allocated_vram"] == 4.0

        # Cleanup
        service.stop_worker()
        service.unload_model()


class TestMultiServiceVRAMCompetition:
    """Test multiple services competing for VRAM."""

    def test_two_services_share_vram(self, mock_backend, mock_gpu_monitor):
        """Test two different services sharing VRAM pool."""
        vram_manager = SmartVRAMManager()

        # Load LLM service manually (3.0GB)
        vram_manager.request_vram("llm", 3.0, VRAMPriority.NORMAL)

        # Load Image service (2.0GB)
        backend = Mock()
        backend.get_vram_estimate.return_value = 2.0
        backend.load.return_value = None

        service = ImageService(backend=backend, vram_manager=vram_manager)
        success = service.load_model()

        assert success is True

        # Total VRAM should be 5GB (LLM 3.0 + Image 2.0)
        status = vram_manager.get_status()
        assert status["allocated_vram"] == 5.0
        assert len(status["loaded_services"]) == 2

    def test_sequential_loading_via_release(self, mock_backend, mock_gpu_monitor):
        """Test sequential loading: one service releases, another loads."""
        # Mock values for entire sequence (remember: available = free - 0.5 safety buffer)
        # Using smaller VRAM pool so both can't fit simultaneously
        mock_gpu_monitor.get_total_vram_gb.return_value = 6.0  # Smaller pool

        # 1. LLM allocation check (needs 5.0GB available)
        # 2. Image tries to load (insufficient - only 1GB left after LLM)
        # 3. After LLM released, pending queue processes
        mock_gpu_monitor.get_free_vram_gb.side_effect = [
            5.5,  # LLM check: 5.5 - 0.5 = 5.0 available (sufficient for 5.0)
            1.0,  # Image check: 1.0 - 0.5 = 0.5 available (insufficient for 4.0)
            1.0,  # Image eviction check (can't evict same priority)
            5.5,  # Pending queue processing: 5.5 - 0.5 = 5.0 available (sufficient for 4.0)
            1.5,  # After Image allocated
        ]

        vram_manager = SmartVRAMManager()

        # Manually allocate LLM (5.0GB, USER_REQUESTED priority - same as Image)
        # Same priority prevents Image from evicting LLM
        vram_manager.request_vram("llm", 5.0, VRAMPriority.USER_REQUESTED)

        # Image service tries to load (4.0GB, USER_REQUESTED priority) - should queue
        service = ImageService(
            backend=mock_backend,
            vram_manager=vram_manager
        )

        success = service.load_model()
        assert success is False  # Queued (insufficient VRAM, can't evict same priority)

        # Check pending queue
        assert vram_manager.pending_queue.qsize() == 1

        # Release LLM - Image should load from queue
        vram_manager.release_vram("llm")

        # Image should now be loaded from pending queue
        assert "image_service" in vram_manager.loaded_services
        assert vram_manager.pending_queue.qsize() == 0

    def test_idle_unload_releases_vram(self, mock_backend, mock_gpu_monitor):
        """Test that idle unload releases VRAM."""
        vram_manager = SmartVRAMManager()
        service = ImageService(
            backend=mock_backend,
            vram_manager=vram_manager,
            idle_timeout=0.1  # 100ms for testing
        )

        # Load model
        service.load_model()
        assert vram_manager.get_status()["allocated_vram"] == 4.0

        # Wait for idle timeout
        time.sleep(0.15)

        # Check idle unload
        service.check_idle_unload()

        # VRAM should be released
        status = vram_manager.get_status()
        assert status["allocated_vram"] == 0.0

    def test_priority_eviction_for_image_service(self, mock_backend, mock_gpu_monitor):
        """Test that higher priority image request can evict lower priority service."""
        # Set up mock values for:
        # 1. Initial check when Image tries to load (insufficient)
        # 2. During eviction check
        # 3. After LLM evicted (sufficient now)
        # 4. After Image loaded
        mock_gpu_monitor.get_free_vram_gb.side_effect = [
            1.5,  # Initial check (insufficient)
            1.5,  # During eviction check
            6.0,  # After LLM evicted
            2.0,  # After Image loaded
        ]

        vram_manager = SmartVRAMManager()

        # Load lower priority LLM service
        vram_manager.request_vram("llm", 5.0, VRAMPriority.NORMAL)

        # Image service loads with higher priority
        service = ImageService(
            backend=mock_backend,
            vram_manager=vram_manager
        )

        success = service.load_model()

        # Image should evict LLM and load successfully
        assert success is True
        assert "llm" not in vram_manager.loaded_services
        assert "image_service" in vram_manager.loaded_services


class TestConcurrentWorkerIntegration:
    """Test concurrent worker threads with VRAM management."""

    def test_image_service_coexists_with_other_services(self, mock_backend, mock_gpu_monitor):
        """Test ImageService can coexist with other services using VRAM."""
        vram_manager = SmartVRAMManager()

        # Allocate LLM service manually (3.0GB)
        vram_manager.request_vram("llm", 3.0, VRAMPriority.NORMAL)

        # Load Image service (4.0GB) - should load successfully
        service = ImageService(backend=mock_backend, vram_manager=vram_manager)
        success = service.load_model()

        assert success is True

        # Check VRAM manager state
        status = vram_manager.get_status()
        assert status["allocated_vram"] == 7.0  # 3.0 (LLM) + 4.0 (Image)
        assert len(status["loaded_services"]) == 2
        assert "llm" in vram_manager.loaded_services
        assert "image_service" in vram_manager.loaded_services

    def test_worker_processes_requests_when_vram_insufficient(self, mock_backend, mock_gpu_monitor):
        """Test that worker fails gracefully when VRAM is insufficient."""
        import time
        from ai.image_request import RequestState

        # Set up small VRAM pool
        mock_gpu_monitor.get_total_vram_gb.return_value = 6.0

        # Mock sequence: Image tries to load but insufficient VRAM
        mock_gpu_monitor.get_free_vram_gb.side_effect = [
            5.5,  # LLM allocation
            1.0,  # Image check (insufficient)
            1.0,  # Image eviction check (can't evict same priority)
        ]

        vram_manager = SmartVRAMManager()

        # Allocate LLM
        vram_manager.request_vram("llm", 5.0, VRAMPriority.USER_REQUESTED)

        # Create image service
        backend = Mock()
        backend.get_vram_estimate.return_value = 4.0
        backend.load.return_value = None
        backend.generate.return_value = "/output/test.png"

        service = ImageService(backend=backend, vram_manager=vram_manager)

        # Start worker
        service.start_worker()

        # Submit request
        request = service.submit_request(prompt="test")

        # Wait briefly for worker to try processing
        time.sleep(0.2)

        # Model should not be loaded (insufficient VRAM)
        assert service.is_loaded is False

        # Request should fail with VRAM error
        assert request.state == RequestState.FAILED
        assert "insufficient VRAM" in request.error_message

        # Cleanup
        service.stop_worker()

    def test_multiple_concurrent_requests_single_service(self, mock_backend, mock_gpu_monitor):
        """Test multiple concurrent requests processed by worker thread."""
        import time
        from ai.image_request import RequestState

        vram_manager = SmartVRAMManager()

        # Create backend that generates images
        backend = Mock()
        backend.get_vram_estimate.return_value = 4.0
        backend.load.return_value = None

        # Track generated images
        generation_count = [0]

        def mock_generate(**kwargs):
            generation_count[0] += 1
            return f"/output/image_{generation_count[0]}.png"

        backend.generate = mock_generate

        # Create service
        service = ImageService(backend=backend, vram_manager=vram_manager)

        # Start worker
        service.start_worker()

        # Submit multiple requests
        request1 = service.submit_request(prompt="cat")
        request2 = service.submit_request(prompt="dog")
        request3 = service.submit_request(prompt="bird")

        # Wait for all to process
        time.sleep(0.8)

        # All should complete
        assert request1.state == RequestState.COMPLETE
        assert request2.state == RequestState.COMPLETE
        assert request3.state == RequestState.COMPLETE

        # Service should be loaded
        assert service.is_loaded is True

        # VRAM should be allocated
        status = vram_manager.get_status()
        assert status["allocated_vram"] == 4.0

        # All should have result paths
        assert request1.result_path == "/output/image_1.png"
        assert request2.result_path == "/output/image_2.png"
        assert request3.result_path == "/output/image_3.png"

        # Cleanup
        service.stop_worker()
        service.unload_model()
