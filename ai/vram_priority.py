"""
VRAM Allocation Priority Levels

Defines priority levels for SmartVRAMManager allocation decisions.
Higher priority services can evict lower priority services when VRAM is needed.
"""


class VRAMPriority:
    """
    Priority levels for VRAM allocation.

    Higher numeric value = higher priority = can evict lower priority services.

    Priority Levels:
        BACKGROUND (1): Background tasks, procedural generation, can wait indefinitely
        NORMAL (5): Normal generation requests, default for most operations
        USER_REQUESTED (8): User explicitly clicked "Generate" button
        UI_CRITICAL (10): Reserved for UI responsiveness (not used for model loading)

    Usage:
        >>> from ai.vram_priority import VRAMPriority
        >>> vram_manager.request_vram('image', 4.0, priority=VRAMPriority.USER_REQUESTED)

    Examples:
        Background procedural generation: VRAMPriority.BACKGROUND
        Automatic asset generation: VRAMPriority.NORMAL
        User-initiated image generation: VRAMPriority.USER_REQUESTED

    Note:
        Within the same priority level, FIFO (first-in-first-out) ordering applies.
    """

    BACKGROUND = 1  # Background tasks, can wait indefinitely
    NORMAL = 5  # Normal generation requests
    USER_REQUESTED = 8  # User explicitly requested (button click)
    UI_CRITICAL = 10  # Reserved for UI (not used for model loading)
