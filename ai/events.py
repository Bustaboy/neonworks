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
"""

import pygame

# Image generation events (1-4)
IMAGE_GENERATION_COMPLETE = pygame.USEREVENT + 1
IMAGE_GENERATION_ERROR = pygame.USEREVENT + 2
IMAGE_MODEL_LOADED = pygame.USEREVENT + 3
IMAGE_MODEL_UNLOADED = pygame.USEREVENT + 4

# Reserved for LLM events (5-8)
# LLM_GENERATION_COMPLETE = pygame.USEREVENT + 5
# LLM_GENERATION_ERROR = pygame.USEREVENT + 6
# LLM_MODEL_LOADED = pygame.USEREVENT + 7
# LLM_MODEL_UNLOADED = pygame.USEREVENT + 8

# VRAM management events (9-12)
VRAM_ALLOCATED = pygame.USEREVENT + 9
VRAM_RELEASED = pygame.USEREVENT + 10
VRAM_ALLOCATION_FAILED = pygame.USEREVENT + 11
VRAM_UNLOAD_REQUESTED = pygame.USEREVENT + 12

# Reserved for future AI services (13-20)

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
