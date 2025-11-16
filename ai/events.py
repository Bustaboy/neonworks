"""
Pygame Event Constants for AI Services

Defines custom Pygame events for cross-thread communication between AI services
(ImageService, LLMService, etc.) and the UI layer.

Event Types:
    - Image generation lifecycle events
    - VRAM management events (for debugging/monitoring)

Usage:
    Listen for events in main loop:
        >>> for event in pygame.event.get():
        ...     if event.type == IMAGE_GENERATION_COMPLETE:
        ...         image_data = event.image_data
        ...         callback_id = event.callback_id

    Post events from worker threads:
        >>> pygame.event.post(pygame.event.Event(
        ...     IMAGE_GENERATION_COMPLETE,
        ...     {'image_data': png_bytes, 'callback_id': 'img_123'}
        ... ))

Event Data Schemas:
    IMAGE_GENERATION_COMPLETE:
        - image_data: bytes (PNG format, ready to load with PIL.Image.open(BytesIO(...)))
        - callback_id: str (for UI correlation)
        - request_id: str (unique request identifier)

    IMAGE_GENERATION_ERROR:
        - error: str (error message)
        - callback_id: str
        - request_id: str

    IMAGE_MODEL_LOADED:
        - backend_type: str ('diffusers', 'comfyui', etc.)

    IMAGE_MODEL_UNLOADED:
        - backend_type: str

    VRAM_ALLOCATED:
        - service: str (service name: 'llm', 'image', 'tts')
        - vram_allocated: float (GB)
        - priority: int (VRAMPriority level)

    VRAM_RELEASED:
        - service: str
        - vram_freed: float (GB)

    VRAM_ALLOCATION_FAILED:
        - service: str
        - required_vram: float (GB)
        - queued: bool (True if queued for sequential execution)

    VRAM_UNLOAD_REQUESTED:
        - service: str (service to unload)

Notes:
    - Events use pygame.USEREVENT + offset (valid range: 0-20)
    - Gaps left for future expansion
    - Image data transmitted as bytes (thread-safe), not PIL.Image objects
    - Event constants are lazily evaluated to avoid importing pygame at module load time
"""

# Define raw offset values (no pygame import needed)
# These are lazily computed when accessed via __getattr__

# Image generation events (1-4)
_IMAGE_GENERATION_COMPLETE_OFFSET = 1
_IMAGE_GENERATION_ERROR_OFFSET = 2
_IMAGE_MODEL_LOADED_OFFSET = 3
_IMAGE_MODEL_UNLOADED_OFFSET = 4

# Reserved for LLM events (5-8)
# _LLM_GENERATION_COMPLETE_OFFSET = 5
# _LLM_GENERATION_ERROR_OFFSET = 6
# _LLM_MODEL_LOADED_OFFSET = 7
# _LLM_MODEL_UNLOADED_OFFSET = 8

# VRAM management events (9-12)
_VRAM_ALLOCATED_OFFSET = 9
_VRAM_RELEASED_OFFSET = 10
_VRAM_ALLOCATION_FAILED_OFFSET = 11
_VRAM_UNLOAD_REQUESTED_OFFSET = 12

# Reserved for future AI services (13-20)

# Mapping of public constant names to their offsets
_EVENT_OFFSETS = {
    "IMAGE_GENERATION_COMPLETE": _IMAGE_GENERATION_COMPLETE_OFFSET,
    "IMAGE_GENERATION_ERROR": _IMAGE_GENERATION_ERROR_OFFSET,
    "IMAGE_MODEL_LOADED": _IMAGE_MODEL_LOADED_OFFSET,
    "IMAGE_MODEL_UNLOADED": _IMAGE_MODEL_UNLOADED_OFFSET,
    "VRAM_ALLOCATED": _VRAM_ALLOCATED_OFFSET,
    "VRAM_RELEASED": _VRAM_RELEASED_OFFSET,
    "VRAM_ALLOCATION_FAILED": _VRAM_ALLOCATION_FAILED_OFFSET,
    "VRAM_UNLOAD_REQUESTED": _VRAM_UNLOAD_REQUESTED_OFFSET,
}


def __getattr__(name):
    """
    Lazily compute pygame event constants when accessed.

    This allows the module to be imported without initializing pygame,
    which is critical for headless testing where SDL environment variables
    must be set before pygame is imported.

    Args:
        name: Attribute name being accessed

    Returns:
        Computed pygame event ID (pygame.USEREVENT + offset)

    Raises:
        AttributeError: If attribute is not a known event constant
    """
    if name in _EVENT_OFFSETS:
        import pygame

        return pygame.USEREVENT + _EVENT_OFFSETS[name]

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    # Image events
    "IMAGE_GENERATION_COMPLETE",
    "IMAGE_GENERATION_ERROR",
    "IMAGE_MODEL_LOADED",
    "IMAGE_MODEL_UNLOADED",
    # VRAM events
    "VRAM_ALLOCATED",
    "VRAM_RELEASED",
    "VRAM_ALLOCATION_FAILED",
    "VRAM_UNLOAD_REQUESTED",
]
