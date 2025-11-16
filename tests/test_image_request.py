"""
Tests for ImageGenerationRequest

Tests request state management, thread safety, and result storage.
"""

import time
from enum import Enum

import pytest

from ai.image_request import ImageGenerationRequest, RequestState


class TestRequestState:
    """Test RequestState enum."""

    def test_enum_values(self):
        """Test that RequestState enum has correct values."""
        assert RequestState.PENDING.value == "pending"
        assert RequestState.PROCESSING.value == "processing"
        assert RequestState.COMPLETE.value == "complete"
        assert RequestState.FAILED.value == "failed"
        assert RequestState.CANCELLED.value == "cancelled"

    def test_enum_uniqueness(self):
        """Test that all RequestState values are unique."""
        states = [
            RequestState.PENDING,
            RequestState.PROCESSING,
            RequestState.COMPLETE,
            RequestState.FAILED,
            RequestState.CANCELLED,
        ]
        assert len(states) == len(set(states))


class TestImageGenerationRequestInit:
    """Test ImageGenerationRequest initialization."""

    def test_initialization_minimal(self):
        """Test initialization with minimal parameters."""
        request = ImageGenerationRequest(request_id="req_001", prompt="A cat in space")

        assert request.request_id == "req_001"
        assert request.prompt == "A cat in space"
        assert request.state == RequestState.PENDING
        assert request.created_at > 0
        assert request.model is None
        assert request.width is None
        assert request.height is None
        assert request.result_path is None
        assert request.error_message is None

    def test_initialization_full_parameters(self):
        """Test initialization with all parameters."""
        request = ImageGenerationRequest(
            request_id="req_002", prompt="A dog on the moon", model="sdxl", width=1024, height=1024
        )

        assert request.request_id == "req_002"
        assert request.prompt == "A dog on the moon"
        assert request.model == "sdxl"
        assert request.width == 1024
        assert request.height == 1024
        assert request.state == RequestState.PENDING

    def test_initialization_validates_request_id(self):
        """Test that empty request_id is rejected."""
        with pytest.raises(ValueError, match="request_id cannot be empty"):
            ImageGenerationRequest(request_id="", prompt="test")

    def test_initialization_validates_prompt(self):
        """Test that empty prompt is rejected."""
        with pytest.raises(ValueError, match="prompt cannot be empty"):
            ImageGenerationRequest(request_id="req_003", prompt="")

    def test_created_at_timestamp(self):
        """Test that created_at is a valid timestamp."""
        before = time.time()
        request = ImageGenerationRequest(request_id="req_004", prompt="test")
        after = time.time()

        assert before <= request.created_at <= after


class TestStateTransitions:
    """Test request state transitions."""

    def test_start_processing(self):
        """Test transition from PENDING to PROCESSING."""
        request = ImageGenerationRequest(request_id="req_005", prompt="test")

        assert request.state == RequestState.PENDING

        request.start_processing()

        assert request.state == RequestState.PROCESSING

    def test_mark_complete(self):
        """Test transition to COMPLETE with result."""
        request = ImageGenerationRequest(request_id="req_006", prompt="test")
        request.start_processing()

        request.mark_complete(result_path="/path/to/image.png")

        assert request.state == RequestState.COMPLETE
        assert request.result_path == "/path/to/image.png"
        assert request.error_message is None

    def test_mark_failed(self):
        """Test transition to FAILED with error."""
        request = ImageGenerationRequest(request_id="req_007", prompt="test")
        request.start_processing()

        request.mark_failed(error_message="CUDA out of memory")

        assert request.state == RequestState.FAILED
        assert request.error_message == "CUDA out of memory"
        assert request.result_path is None

    def test_cancel_pending_request(self):
        """Test cancelling a pending request."""
        request = ImageGenerationRequest(request_id="req_008", prompt="test")

        success = request.cancel()

        assert success is True
        assert request.state == RequestState.CANCELLED

    def test_cancel_processing_request(self):
        """Test cancelling a processing request."""
        request = ImageGenerationRequest(request_id="req_009", prompt="test")
        request.start_processing()

        success = request.cancel()

        assert success is True
        assert request.state == RequestState.CANCELLED

    def test_cannot_cancel_completed_request(self):
        """Test that completed requests cannot be cancelled."""
        request = ImageGenerationRequest(request_id="req_010", prompt="test")
        request.start_processing()
        request.mark_complete(result_path="/path/to/image.png")

        success = request.cancel()

        assert success is False
        assert request.state == RequestState.COMPLETE  # State unchanged

    def test_cannot_cancel_failed_request(self):
        """Test that failed requests cannot be cancelled."""
        request = ImageGenerationRequest(request_id="req_011", prompt="test")
        request.start_processing()
        request.mark_failed(error_message="Error")

        success = request.cancel()

        assert success is False
        assert request.state == RequestState.FAILED  # State unchanged


class TestGetStatus:
    """Test get_status() method."""

    def test_status_pending(self):
        """Test status dict for pending request."""
        request = ImageGenerationRequest(
            request_id="req_012", prompt="test prompt", model="sdxl", width=1024, height=1024
        )

        status = request.get_status()

        assert status["request_id"] == "req_012"
        assert status["prompt"] == "test prompt"
        assert status["model"] == "sdxl"
        assert status["width"] == 1024
        assert status["height"] == 1024
        assert status["state"] == "pending"
        assert status["result_path"] is None
        assert status["error_message"] is None
        assert "created_at" in status

    def test_status_complete(self):
        """Test status dict for completed request."""
        request = ImageGenerationRequest(request_id="req_013", prompt="test")
        request.start_processing()
        request.mark_complete(result_path="/output/image.png")

        status = request.get_status()

        assert status["state"] == "complete"
        assert status["result_path"] == "/output/image.png"
        assert status["error_message"] is None

    def test_status_failed(self):
        """Test status dict for failed request."""
        request = ImageGenerationRequest(request_id="req_014", prompt="test")
        request.start_processing()
        request.mark_failed(error_message="GPU error")

        status = request.get_status()

        assert status["state"] == "failed"
        assert status["error_message"] == "GPU error"
        assert status["result_path"] is None


class TestThreadSafety:
    """Test thread safety of ImageGenerationRequest."""

    def test_concurrent_state_transitions(self):
        """Test concurrent state transitions are safe."""
        import threading

        request = ImageGenerationRequest(request_id="req_015", prompt="test")
        errors = []

        def try_start_processing():
            try:
                request.start_processing()
            except Exception as e:
                errors.append(("start", e))

        def try_mark_complete():
            try:
                request.mark_complete(result_path="/path/to/image.png")
            except Exception as e:
                errors.append(("complete", e))

        # Create 5 threads trying to start processing
        threads = [threading.Thread(target=try_start_processing) for _ in range(5)]

        # Start all threads
        for t in threads:
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # No errors should occur
        assert len(errors) == 0

        # State should be PROCESSING (only one thread succeeded)
        assert request.state == RequestState.PROCESSING

    def test_concurrent_get_status(self):
        """Test concurrent get_status() calls are safe."""
        import threading

        request = ImageGenerationRequest(request_id="req_016", prompt="test")
        errors = []
        statuses = []

        def get_status_snapshot():
            try:
                status = request.get_status()
                statuses.append(status)
            except Exception as e:
                errors.append(e)

        # Create 10 threads getting status
        threads = [threading.Thread(target=get_status_snapshot) for _ in range(10)]

        # Start all threads
        for t in threads:
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # No errors should occur
        assert len(errors) == 0

        # Should have 10 status snapshots
        assert len(statuses) == 10

        # All should be valid dicts
        for status in statuses:
            assert isinstance(status, dict)
            assert "request_id" in status
            assert "state" in status
