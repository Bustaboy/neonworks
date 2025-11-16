"""
Image Generation Service

Service for managing image generation with VRAM integration and auto-unload.
"""

import threading
import time
import uuid
from typing import Dict, List, Optional

from ai.events import IMAGE_MODEL_LOADED, IMAGE_MODEL_UNLOADED
from ai.image_request import ImageGenerationRequest, RequestState
from ai.vram_manager import SmartVRAMManager
from ai.vram_priority import VRAMPriority


class ImageService:
    """
    Image generation service with lifecycle management.

    Handles model loading/unloading with VRAM integration and automatic
    unload after idle timeout.

    Features:
        - Model loading with VRAM allocation
        - Automatic unload after idle timeout (default 5 minutes)
        - Pygame event emission for lifecycle changes
        - Thread-safe operations

    Lifecycle:
        1. load_model(): Requests VRAM, loads backend model
        2. (use for generation)
        3. Auto-unload after idle timeout OR manual unload_model()

    Events:
        - IMAGE_MODEL_LOADED: Emitted when model loads successfully
        - IMAGE_MODEL_UNLOADED: Emitted when model unloads

    Example:
        >>> from ai.image_backend import DiffusersBackend
        >>> backend = DiffusersBackend()
        >>> vram_manager = SmartVRAMManager()
        >>> service = ImageService(backend, vram_manager)
        >>>
        >>> # Load model
        >>> if service.load_model():
        ...     # Generate images
        ...     service.update_last_use_time()
        ...
        >>> # Check for idle unload (call periodically in main loop)
        >>> service.check_idle_unload()
    """

    def __init__(
        self,
        backend,
        vram_manager: SmartVRAMManager,
        idle_timeout: float = 300.0,  # 5 minutes default
    ):
        """
        Initialize Image Service.

        Args:
            backend: Image generation backend (DiffusersBackend)
            vram_manager: VRAM manager for GPU memory allocation
            idle_timeout: Seconds of inactivity before auto-unload (default 300s / 5min)

        Raises:
            ValueError: If backend or vram_manager is None
        """
        if backend is None:
            raise ValueError("backend cannot be None")
        if vram_manager is None:
            raise ValueError("vram_manager cannot be None")

        self.backend = backend
        self.vram_manager = vram_manager
        self.idle_timeout = idle_timeout

        # State tracking
        self.is_loaded: bool = False
        self.last_use_time: Optional[float] = None

        # Request tracking
        self._requests: Dict[str, ImageGenerationRequest] = {}

        # Worker thread
        self._worker_thread: Optional[threading.Thread] = None
        self._worker_running: bool = False

        # Thread safety
        self._lock = threading.Lock()

    def load_model(self) -> bool:
        """
        Load image generation model.

        Requests VRAM from manager, loads backend model if allocation succeeds.
        Emits IMAGE_MODEL_LOADED event on success.

        Returns:
            True if loaded successfully, False if VRAM allocation failed

        Thread-safe.

        Example:
            >>> success = service.load_model()
            >>> if success:
            ...     print("Model loaded and ready")
        """
        with self._lock:
            # Already loaded - no-op
            if self.is_loaded:
                return True

            # Get VRAM estimate from backend
            vram_required = self.backend.get_vram_estimate()

            # Request VRAM allocation
            success = self.vram_manager.request_vram(
                service_name="image_service",
                required_vram_gb=vram_required,
                priority=VRAMPriority.USER_REQUESTED,
            )

            if not success:
                # VRAM allocation failed (queued or insufficient)
                return False

            # Load backend model
            self.backend.load()

            # Update state
            self.is_loaded = True
            self.last_use_time = time.time()

            # Emit event (lazy import to avoid pygame init during module import)
            import pygame
            event = pygame.event.Event(
                IMAGE_MODEL_LOADED,
                {"service": "image_service", "vram": vram_required},
            )
            pygame.event.post(event)

            return True

    def unload_model(self) -> bool:
        """
        Unload image generation model.

        Releases VRAM, unloads backend model.
        Emits IMAGE_MODEL_UNLOADED event.

        Returns:
            True (always succeeds, idempotent)

        Thread-safe.

        Example:
            >>> service.unload_model()
            True
        """
        with self._lock:
            # Not loaded - no-op
            if not self.is_loaded:
                return True

            # Unload backend model
            self.backend.unload()

            # Release VRAM
            self.vram_manager.release_vram("image_service")

            # Update state
            self.is_loaded = False
            self.last_use_time = None

            # Emit event (lazy import to avoid pygame init during module import)
            import pygame
            event = pygame.event.Event(
                IMAGE_MODEL_UNLOADED, {"service": "image_service"}
            )
            pygame.event.post(event)

            return True

    def check_idle_unload(self):
        """
        Check if model should be unloaded due to idle timeout.

        Call this periodically (e.g., in main game loop) to enable
        automatic unloading of idle models.

        Thread-safe.

        Example:
            >>> # In main loop
            >>> while running:
            ...     service.check_idle_unload()
            ...     # ... other game logic ...
        """
        with self._lock:
            # Not loaded - nothing to check
            if not self.is_loaded:
                return

            # Check if idle timeout exceeded
            if self.last_use_time is not None:
                idle_time = time.time() - self.last_use_time
                if idle_time >= self.idle_timeout:
                    # Unload (must release lock first to avoid deadlock)
                    pass  # Will unload below

        # Unload outside lock to avoid deadlock with event posting
        if (
            self.is_loaded
            and self.last_use_time is not None
            and (time.time() - self.last_use_time) >= self.idle_timeout
        ):
            self.unload_model()

    def update_last_use_time(self):
        """
        Update last use timestamp.

        Call this after generating an image to prevent idle unload.

        Thread-safe.

        Example:
            >>> service.generate_image(...)
            >>> service.update_last_use_time()  # Reset idle timer
        """
        with self._lock:
            self.last_use_time = time.time()

    def get_status(self) -> dict:
        """
        Get current service status.

        Returns:
            Dict with service state information

        Thread-safe.

        Example:
            >>> status = service.get_status()
            >>> print(status)
            {
                "is_loaded": True,
                "last_use_time": 1234567890.123,
                "idle_timeout": 300.0
            }
        """
        with self._lock:
            return {
                "is_loaded": self.is_loaded,
                "last_use_time": self.last_use_time,
                "idle_timeout": self.idle_timeout,
            }

    def submit_request(
        self,
        prompt: str,
        model: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> ImageGenerationRequest:
        """
        Submit an image generation request.

        Creates a new request and adds it to the queue for processing.
        Generates a unique request ID.

        Args:
            prompt: Text prompt for image generation
            model: Model to use (optional)
            width: Image width in pixels (optional)
            height: Image height in pixels (optional)

        Returns:
            ImageGenerationRequest object

        Thread-safe.

        Example:
            >>> request = service.submit_request(
            ...     prompt="A cat in space",
            ...     model="sdxl",
            ...     width=1024,
            ...     height=1024
            ... )
            >>> print(request.request_id)
            req_abc123...
        """
        with self._lock:
            # Generate unique request ID
            request_id = f"req_{uuid.uuid4().hex[:16]}"

            # Create request
            request = ImageGenerationRequest(
                request_id=request_id,
                prompt=prompt,
                model=model,
                width=width,
                height=height,
            )

            # Store request
            self._requests[request_id] = request

            return request

    def get_request(self, request_id: str) -> Optional[ImageGenerationRequest]:
        """
        Get request by ID.

        Args:
            request_id: Request ID to retrieve

        Returns:
            ImageGenerationRequest if found, None otherwise

        Thread-safe.

        Example:
            >>> request = service.get_request("req_abc123")
            >>> if request:
            ...     print(request.state)
        """
        with self._lock:
            return self._requests.get(request_id)

    def cancel_request(self, request_id: str) -> bool:
        """
        Cancel a request by ID.

        Args:
            request_id: Request ID to cancel

        Returns:
            True if cancelled, False if not found or already complete

        Thread-safe.

        Example:
            >>> success = service.cancel_request("req_abc123")
            >>> print(success)
            True
        """
        with self._lock:
            request = self._requests.get(request_id)
            if request is None:
                return False

            return request.cancel()

    def list_pending_requests(self) -> List[ImageGenerationRequest]:
        """
        List all pending requests.

        Returns:
            List of pending ImageGenerationRequest objects

        Thread-safe.

        Example:
            >>> pending = service.list_pending_requests()
            >>> print(len(pending))
            5
        """
        with self._lock:
            return [
                req
                for req in self._requests.values()
                if req.state == RequestState.PENDING
            ]

    def get_all_requests(self) -> List[ImageGenerationRequest]:
        """
        Get all requests regardless of state.

        Returns:
            List of all ImageGenerationRequest objects

        Thread-safe.

        Example:
            >>> all_requests = service.get_all_requests()
            >>> states = {r.state for r in all_requests}
        """
        with self._lock:
            return list(self._requests.values())

    def start_worker(self):
        """
        Start background worker thread for processing requests.

        Worker thread processes pending requests in the background,
        automatically loading the model when needed and generating images.

        Thread-safe (idempotent - safe to call multiple times).

        Example:
            >>> service = ImageService(backend, vram_manager)
            >>> service.start_worker()
            >>> # Submit requests...
            >>> request = service.submit_request(prompt="A cat")
            >>> # Worker processes automatically in background
        """
        with self._lock:
            if self._worker_running:
                return  # Already running

            self._worker_running = True
            self._worker_thread = threading.Thread(
                target=self._worker_loop, daemon=True, name="ImageServiceWorker"
            )
            self._worker_thread.start()

    def stop_worker(self):
        """
        Stop background worker thread.

        Gracefully stops the worker thread. Waits for current generation
        to complete before stopping.

        Thread-safe.

        Example:
            >>> service.stop_worker()
        """
        with self._lock:
            if not self._worker_running:
                return  # Not running

            self._worker_running = False

        # Wait for worker thread to finish (outside lock to avoid deadlock)
        if self._worker_thread is not None:
            self._worker_thread.join(timeout=5.0)

    def _worker_loop(self):
        """
        Main worker loop (runs in background thread).

        Continuously processes pending requests until stopped.
        Sleeps briefly between checks to reduce CPU usage.
        """
        while self._worker_running:
            # Get next pending request
            pending = self.list_pending_requests()

            if pending:
                # Process first pending request
                request = pending[0]
                self._process_request(request)
            else:
                # No pending requests - sleep briefly
                time.sleep(0.1)

            # Check for idle unload
            self.check_idle_unload()

    def _process_request(self, request: ImageGenerationRequest):
        """
        Process a single image generation request.

        Loads model if needed, generates image, updates request state,
        and emits appropriate events.

        Args:
            request: Request to process

        Thread-safe.
        """
        from ai.events import IMAGE_GENERATION_COMPLETE, IMAGE_GENERATION_ERROR

        try:
            # Mark as processing
            request.start_processing()

            # Load model if not loaded
            if not self.is_loaded:
                success = self.load_model()
                if not success:
                    # VRAM allocation failed
                    request.mark_failed("Failed to load model (insufficient VRAM)")
                    self._emit_generation_error(
                        request_id=request.request_id,
                        error_message="Failed to load model (insufficient VRAM)",
                    )
                    return

            # Generate image using backend
            result_path = self.backend.generate(
                prompt=request.prompt,
                model=request.model,
                width=request.width,
                height=request.height,
            )

            # Mark as complete
            request.mark_complete(result_path=result_path)

            # Update last use time
            self.update_last_use_time()

            # Emit completion event
            self._emit_generation_complete(
                request_id=request.request_id, result_path=result_path
            )

        except Exception as e:
            # Mark as failed
            error_message = str(e)
            request.mark_failed(error_message=error_message)

            # Emit error event
            self._emit_generation_error(
                request_id=request.request_id, error_message=error_message
            )

    def _emit_generation_complete(self, request_id: str, result_path: str):
        """
        Emit IMAGE_GENERATION_COMPLETE event.

        Args:
            request_id: Request ID that completed
            result_path: Path to generated image
        """
        from ai.events import IMAGE_GENERATION_COMPLETE
        import pygame

        event = pygame.event.Event(
            IMAGE_GENERATION_COMPLETE,
            {"request_id": request_id, "result_path": result_path},
        )
        pygame.event.post(event)

    def _emit_generation_error(self, request_id: str, error_message: str):
        """
        Emit IMAGE_GENERATION_ERROR event.

        Args:
            request_id: Request ID that failed
            error_message: Error description
        """
        from ai.events import IMAGE_GENERATION_ERROR
        import pygame

        event = pygame.event.Event(
            IMAGE_GENERATION_ERROR,
            {"request_id": request_id, "error_message": error_message},
        )
        pygame.event.post(event)
