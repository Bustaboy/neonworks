"""
Image Generation Request

Represents an image generation request with state tracking and thread safety.
"""

import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class RequestState(Enum):
    """
    Request lifecycle states.

    State transitions:
        PENDING -> PROCESSING -> COMPLETE
        PENDING -> PROCESSING -> FAILED
        PENDING -> CANCELLED
        PROCESSING -> CANCELLED
    """

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETE = "complete"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ImageGenerationRequest:
    """
    Image generation request with state tracking.

    Encapsulates all parameters for an image generation request and tracks
    its lifecycle (pending -> processing -> complete/failed/cancelled).

    Thread-safe: All state transitions are protected by a lock.

    Attributes:
        request_id: Unique identifier for this request
        prompt: Text prompt for image generation
        model: Model to use (e.g., "sdxl", "sd15")
        width: Image width in pixels
        height: Image height in pixels
        state: Current state of the request
        created_at: Unix timestamp when request was created
        result_path: Path to generated image (when complete)
        error_message: Error message (when failed)

    Example:
        >>> request = ImageGenerationRequest(
        ...     request_id="req_001",
        ...     prompt="A cat in space",
        ...     model="sdxl",
        ...     width=1024,
        ...     height=1024
        ... )
        >>> request.start_processing()
        >>> request.mark_complete(result_path="/output/image.png")
        >>> status = request.get_status()
        >>> print(status["state"])
        complete
    """

    request_id: str
    prompt: str
    model: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    state: RequestState = field(default=RequestState.PENDING, init=False)
    created_at: float = field(default_factory=time.time, init=False)
    result_path: Optional[str] = field(default=None, init=False)
    error_message: Optional[str] = field(default=None, init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)

    def __post_init__(self):
        """Validate initialization parameters."""
        if not self.request_id:
            raise ValueError("request_id cannot be empty")
        if not self.prompt:
            raise ValueError("prompt cannot be empty")

    def start_processing(self):
        """
        Transition to PROCESSING state.

        Can only be called from PENDING state.

        Thread-safe.
        """
        with self._lock:
            if self.state == RequestState.PENDING:
                self.state = RequestState.PROCESSING

    def mark_complete(self, result_path: str):
        """
        Mark request as complete with result.

        Args:
            result_path: Path to generated image file

        Thread-safe.
        """
        with self._lock:
            self.state = RequestState.COMPLETE
            self.result_path = result_path
            self.error_message = None

    def mark_failed(self, error_message: str):
        """
        Mark request as failed with error.

        Args:
            error_message: Description of what went wrong

        Thread-safe.
        """
        with self._lock:
            self.state = RequestState.FAILED
            self.error_message = error_message
            self.result_path = None

    def cancel(self) -> bool:
        """
        Cancel the request.

        Can only cancel PENDING or PROCESSING requests.
        Cannot cancel COMPLETE or FAILED requests.

        Returns:
            True if cancelled, False if already complete/failed

        Thread-safe.
        """
        with self._lock:
            if self.state in (RequestState.PENDING, RequestState.PROCESSING):
                self.state = RequestState.CANCELLED
                return True
            return False

    def get_status(self) -> dict:
        """
        Get current request status.

        Returns:
            Dict with all request information

        Thread-safe.

        Example:
            >>> status = request.get_status()
            >>> print(status)
            {
                "request_id": "req_001",
                "prompt": "A cat in space",
                "model": "sdxl",
                "width": 1024,
                "height": 1024,
                "state": "complete",
                "result_path": "/output/image.png",
                "error_message": None,
                "created_at": 1234567890.123
            }
        """
        with self._lock:
            return {
                "request_id": self.request_id,
                "prompt": self.prompt,
                "model": self.model,
                "width": self.width,
                "height": self.height,
                "state": self.state.value,  # Convert enum to string
                "result_path": self.result_path,
                "error_message": self.error_message,
                "created_at": self.created_at,
            }
