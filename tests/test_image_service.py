"""
Tests for ImageService

Tests service lifecycle, model loading/unloading, and VRAM integration.
"""

import pytest
import pygame
import time
from unittest.mock import Mock, patch, MagicMock

from ai.image_service import ImageService
from ai.vram_manager import SmartVRAMManager
from ai.vram_priority import VRAMPriority


@pytest.fixture
def mock_backend():
    """Mock DiffusersBackend."""
    backend = Mock()
    backend.is_loaded.return_value = False
    backend.load.return_value = None
    backend.unload.return_value = None
    backend.get_vram_estimate.return_value = 4.0  # SDXL requires 4GB
    return backend


@pytest.fixture
def mock_vram_manager():
    """Mock SmartVRAMManager."""
    manager = Mock(spec=SmartVRAMManager)
    manager.request_vram.return_value = True
    manager.release_vram.return_value = True
    return manager


class TestImageServiceInit:
    """Test ImageService initialization."""

    def test_initialization(self, mock_backend, mock_vram_manager):
        """Test basic initialization."""
        service = ImageService(
            backend=mock_backend,
            vram_manager=mock_vram_manager
        )

        assert service.backend == mock_backend
        assert service.vram_manager == mock_vram_manager
        assert service.is_loaded is False
        assert service.idle_timeout == 300.0  # Default 5 minutes
        assert service.last_use_time is None

    def test_initialization_custom_timeout(self, mock_backend, mock_vram_manager):
        """Test initialization with custom idle timeout."""
        service = ImageService(
            backend=mock_backend,
            vram_manager=mock_vram_manager,
            idle_timeout=600.0  # 10 minutes
        )

        assert service.idle_timeout == 600.0

    def test_initialization_requires_backend(self, mock_vram_manager):
        """Test that backend is required."""
        with pytest.raises(ValueError, match="backend cannot be None"):
            ImageService(backend=None, vram_manager=mock_vram_manager)

    def test_initialization_requires_vram_manager(self, mock_backend):
        """Test that vram_manager is required."""
        with pytest.raises(ValueError, match="vram_manager cannot be None"):
            ImageService(backend=mock_backend, vram_manager=None)


class TestLoadModel:
    """Test model loading."""

    def test_load_model_success(self, mock_backend, mock_vram_manager):
        """Test successful model loading."""
        service = ImageService(
            backend=mock_backend,
            vram_manager=mock_vram_manager
        )
        pygame.event.clear()

        success = service.load_model()

        assert success is True
        assert service.is_loaded is True
        assert service.last_use_time is not None

        # Should request VRAM
        mock_vram_manager.request_vram.assert_called_once_with(
            service_name="image_service",
            required_vram_gb=4.0,  # VRAM estimate
            priority=VRAMPriority.USER_REQUESTED
        )

        # Should load backend
        mock_backend.load.assert_called_once()

        # Should emit IMAGE_MODEL_LOADED event
        events = pygame.event.get()
        loaded_events = [e for e in events if e.type == pygame.USEREVENT + 3]
        assert len(loaded_events) == 1

    def test_load_model_vram_allocation_failed(self, mock_backend, mock_vram_manager):
        """Test load failure when VRAM allocation fails."""
        mock_vram_manager.request_vram.return_value = False

        service = ImageService(
            backend=mock_backend,
            vram_manager=mock_vram_manager
        )

        success = service.load_model()

        assert success is False
        assert service.is_loaded is False

        # Should not load backend if VRAM allocation failed
        mock_backend.load.assert_not_called()

    def test_load_model_already_loaded(self, mock_backend, mock_vram_manager):
        """Test that loading when already loaded is a no-op."""
        service = ImageService(
            backend=mock_backend,
            vram_manager=mock_vram_manager
        )
        service.load_model()

        # Try to load again
        mock_vram_manager.request_vram.reset_mock()
        mock_backend.load.reset_mock()

        success = service.load_model()

        assert success is True
        assert service.is_loaded is True

        # Should not request VRAM or load backend again
        mock_vram_manager.request_vram.assert_not_called()
        mock_backend.load.assert_not_called()

    def test_load_model_updates_last_use_time(self, mock_backend, mock_vram_manager):
        """Test that loading updates last_use_time."""
        service = ImageService(
            backend=mock_backend,
            vram_manager=mock_vram_manager
        )

        before = time.time()
        service.load_model()
        after = time.time()

        assert service.last_use_time is not None
        assert before <= service.last_use_time <= after


class TestUnloadModel:
    """Test model unloading."""

    def test_unload_model_success(self, mock_backend, mock_vram_manager):
        """Test successful model unloading."""
        service = ImageService(
            backend=mock_backend,
            vram_manager=mock_vram_manager
        )
        service.load_model()

        pygame.event.clear()

        success = service.unload_model()

        assert success is True
        assert service.is_loaded is False
        assert service.last_use_time is None

        # Should release VRAM
        mock_vram_manager.release_vram.assert_called_once_with("image_service")

        # Should unload backend
        mock_backend.unload.assert_called_once()

        # Should emit IMAGE_MODEL_UNLOADED event
        events = pygame.event.get()
        unloaded_events = [e for e in events if e.type == pygame.USEREVENT + 4]
        assert len(unloaded_events) == 1

    def test_unload_model_not_loaded(self, mock_backend, mock_vram_manager):
        """Test that unloading when not loaded is a no-op."""
        service = ImageService(
            backend=mock_backend,
            vram_manager=mock_vram_manager
        )

        success = service.unload_model()

        assert success is True  # Still returns True (idempotent)
        assert service.is_loaded is False

        # Should not release VRAM or unload backend
        mock_vram_manager.release_vram.assert_not_called()
        mock_backend.unload.assert_not_called()


class TestIdleUnload:
    """Test automatic unload after idle timeout."""

    def test_check_idle_unload_when_idle(self, mock_backend, mock_vram_manager):
        """Test that model unloads after idle timeout."""
        service = ImageService(
            backend=mock_backend,
            vram_manager=mock_vram_manager,
            idle_timeout=0.1  # 100ms timeout for testing
        )
        service.load_model()

        # Wait for idle timeout
        time.sleep(0.15)

        # Check idle - should unload
        service.check_idle_unload()

        assert service.is_loaded is False
        mock_backend.unload.assert_called_once()

    def test_check_idle_unload_when_active(self, mock_backend, mock_vram_manager):
        """Test that model stays loaded when recently used."""
        service = ImageService(
            backend=mock_backend,
            vram_manager=mock_vram_manager,
            idle_timeout=1.0  # 1 second timeout
        )
        service.load_model()

        # Check immediately - should not unload
        service.check_idle_unload()

        assert service.is_loaded is True
        mock_backend.unload.assert_not_called()

    def test_check_idle_unload_when_not_loaded(self, mock_backend, mock_vram_manager):
        """Test that check_idle_unload is safe when not loaded."""
        service = ImageService(
            backend=mock_backend,
            vram_manager=mock_vram_manager
        )

        # Should not crash
        service.check_idle_unload()

        assert service.is_loaded is False


class TestUpdateLastUseTime:
    """Test last_use_time updates."""

    def test_update_last_use_time(self, mock_backend, mock_vram_manager):
        """Test that update_last_use_time() updates timestamp."""
        service = ImageService(
            backend=mock_backend,
            vram_manager=mock_vram_manager
        )
        service.load_model()

        old_time = service.last_use_time
        time.sleep(0.01)  # Small delay

        service.update_last_use_time()

        assert service.last_use_time > old_time

    def test_update_last_use_time_when_not_loaded(self, mock_backend, mock_vram_manager):
        """Test that update_last_use_time() works when not loaded."""
        service = ImageService(
            backend=mock_backend,
            vram_manager=mock_vram_manager
        )

        # Should not crash
        service.update_last_use_time()

        assert service.last_use_time is not None


class TestGetStatus:
    """Test get_status() method."""

    def test_status_not_loaded(self, mock_backend, mock_vram_manager):
        """Test status when model not loaded."""
        service = ImageService(
            backend=mock_backend,
            vram_manager=mock_vram_manager
        )

        status = service.get_status()

        assert status["is_loaded"] is False
        assert status["last_use_time"] is None
        assert status["idle_timeout"] == 300.0

    def test_status_loaded(self, mock_backend, mock_vram_manager):
        """Test status when model loaded."""
        service = ImageService(
            backend=mock_backend,
            vram_manager=mock_vram_manager
        )
        service.load_model()

        status = service.get_status()

        assert status["is_loaded"] is True
        assert status["last_use_time"] is not None
        assert isinstance(status["last_use_time"], float)


class TestAsyncRequests:
    """Test async request handling."""

    def test_submit_request(self, mock_backend, mock_vram_manager):
        """Test submitting a generation request."""
        from ai.image_request import ImageGenerationRequest, RequestState

        service = ImageService(
            backend=mock_backend,
            vram_manager=mock_vram_manager
        )

        request = service.submit_request(
            prompt="A cat in space",
            model="sdxl",
            width=1024,
            height=1024
        )

        assert isinstance(request, ImageGenerationRequest)
        assert request.prompt == "A cat in space"
        assert request.model == "sdxl"
        assert request.width == 1024
        assert request.height == 1024
        assert request.state == RequestState.PENDING

    def test_submit_request_generates_unique_id(self, mock_backend, mock_vram_manager):
        """Test that each request gets unique ID."""
        service = ImageService(
            backend=mock_backend,
            vram_manager=mock_vram_manager
        )

        request1 = service.submit_request(prompt="test1")
        request2 = service.submit_request(prompt="test2")

        assert request1.request_id != request2.request_id

    def test_get_request_by_id(self, mock_backend, mock_vram_manager):
        """Test retrieving request by ID."""
        service = ImageService(
            backend=mock_backend,
            vram_manager=mock_vram_manager
        )

        request = service.submit_request(prompt="test")
        request_id = request.request_id

        retrieved = service.get_request(request_id)

        assert retrieved is not None
        assert retrieved.request_id == request_id
        assert retrieved.prompt == "test"

    def test_get_request_nonexistent(self, mock_backend, mock_vram_manager):
        """Test retrieving nonexistent request returns None."""
        service = ImageService(
            backend=mock_backend,
            vram_manager=mock_vram_manager
        )

        retrieved = service.get_request("nonexistent_id")

        assert retrieved is None

    def test_cancel_request_by_id(self, mock_backend, mock_vram_manager):
        """Test cancelling a request by ID."""
        from ai.image_request import RequestState

        service = ImageService(
            backend=mock_backend,
            vram_manager=mock_vram_manager
        )

        request = service.submit_request(prompt="test")
        request_id = request.request_id

        success = service.cancel_request(request_id)

        assert success is True

        # Request should be cancelled
        retrieved = service.get_request(request_id)
        assert retrieved.state == RequestState.CANCELLED

    def test_cancel_request_nonexistent(self, mock_backend, mock_vram_manager):
        """Test cancelling nonexistent request returns False."""
        service = ImageService(
            backend=mock_backend,
            vram_manager=mock_vram_manager
        )

        success = service.cancel_request("nonexistent_id")

        assert success is False

    def test_list_pending_requests(self, mock_backend, mock_vram_manager):
        """Test listing all pending requests."""
        from ai.image_request import RequestState

        service = ImageService(
            backend=mock_backend,
            vram_manager=mock_vram_manager
        )

        # Submit multiple requests
        req1 = service.submit_request(prompt="test1")
        req2 = service.submit_request(prompt="test2")
        req3 = service.submit_request(prompt="test3")

        pending = service.list_pending_requests()

        assert len(pending) == 3
        assert all(r.state == RequestState.PENDING for r in pending)

    def test_list_pending_excludes_cancelled(self, mock_backend, mock_vram_manager):
        """Test that list_pending_requests() excludes cancelled requests."""
        service = ImageService(
            backend=mock_backend,
            vram_manager=mock_vram_manager
        )

        req1 = service.submit_request(prompt="test1")
        req2 = service.submit_request(prompt="test2")

        # Cancel one request
        service.cancel_request(req1.request_id)

        pending = service.list_pending_requests()

        assert len(pending) == 1
        assert pending[0].request_id == req2.request_id

    def test_get_all_requests(self, mock_backend, mock_vram_manager):
        """Test getting all requests regardless of state."""
        from ai.image_request import RequestState

        service = ImageService(
            backend=mock_backend,
            vram_manager=mock_vram_manager
        )

        req1 = service.submit_request(prompt="test1")
        req2 = service.submit_request(prompt="test2")
        service.cancel_request(req1.request_id)

        all_requests = service.get_all_requests()

        assert len(all_requests) == 2
        # Should include both pending and cancelled
        states = {r.state for r in all_requests}
        assert RequestState.PENDING in states
        assert RequestState.CANCELLED in states
