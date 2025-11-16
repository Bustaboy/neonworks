"""
Smart VRAM Manager

Dynamic VRAM allocation with priority-based eviction and sequential loading.
NO hard percentages - services request exactly what they need.

Key Features:
    - Dynamic allocation based on actual model requirements (GB, not percentages)
    - Priority-based eviction (higher priority can evict lower)
    - Sequential loading support (LLM loads → unloads → Image loads)
    - Multi-vendor GPU support (NVIDIA via nvidia-smi, AMD via rocm-smi)
    - Thread-safe operations

Architecture:
    - Shared singleton across all AI services (LLM, Image, TTS)
    - Services request exact VRAM needed (e.g., 3.2GB for LLM, 4.0GB for SDXL)
    - Backends handle CPU offloading/optimizations, report reduced requirements
    - VRAM manager just allocates based on backend's reported needs

Example:
    >>> manager = SmartVRAMManager()  # Auto-detect GPU VRAM
    >>> manager.total_vram
    8.0  # 8GB GPU detected
    >>> manager.available_vram
    7.5  # 8.0 - 0.5 safety buffer

    >>> # Request VRAM for image generation (SDXL needs 4.0GB)
    >>> success = manager.request_vram(
    ...     service_name="image",
    ...     required_vram_gb=4.0,
    ...     priority=VRAMPriority.USER_REQUESTED
    ... )
    >>> success
    True

    >>> # Check status
    >>> manager.get_status()
    {
        'total_vram': 8.0,
        'safety_buffer': 0.5,
        'allocated_vram': 4.0,
        'loaded_services': [
            {'name': 'image', 'vram': 4.0, 'priority': 8}
        ],
        'pending_count': 0
    }

Notes:
    - Auto-detects total VRAM via GPUMonitor (nvidia-smi or rocm-smi)
    - Can manually specify total_vram_gb if GPU detection unreliable
    - Safety buffer (default 0.5GB) reserved for system/driver overhead
    - Thread-safe via threading.Lock
"""

import queue
import threading
import time
from typing import Dict, List, Optional

import pygame

from ai.gpu_monitor import GPUMonitor
from ai.vram_priority import VRAMPriority


class SmartVRAMManager:
    """
    Manages VRAM allocation with priority-based eviction.

    Provides dynamic VRAM allocation for AI services (LLM, Image, TTS).
    Services request exactly what they need, no percentage-based allocation.

    Attributes:
        total_vram: Total GPU VRAM in GB (auto-detected or manual)
        safety_buffer: Reserved VRAM for system/driver (GB)
        available_vram: Usable VRAM after safety buffer (GB)
        loaded_services: Currently loaded services registry
        pending_queue: Services waiting for VRAM
        gpu_monitor: GPU monitoring instance
    """

    def __init__(
        self,
        total_vram_gb: Optional[float] = None,
        safety_buffer_gb: float = 0.5
    ):
        """
        Initialize VRAM manager.

        Args:
            total_vram_gb: Total GPU VRAM in GB (auto-detect if None)
            safety_buffer_gb: Safety buffer for system/driver (default 0.5GB)

        Raises:
            SystemRequirementError: If GPU monitoring tool not found
                (nvidia-smi or rocm-smi required)

        Example:
            >>> # Auto-detect GPU VRAM
            >>> manager = SmartVRAMManager()

            >>> # Manual VRAM specification
            >>> manager = SmartVRAMManager(total_vram_gb=16.0)

            >>> # Custom safety buffer
            >>> manager = SmartVRAMManager(safety_buffer_gb=1.0)
        """
        # Initialize GPU monitor
        self.gpu_monitor = GPUMonitor()

        # Set total VRAM (auto-detect or manual)
        if total_vram_gb is None:
            # Auto-detect from GPU
            self.total_vram = self.gpu_monitor.get_total_vram_gb()
        else:
            # Use manually specified value
            self.total_vram = total_vram_gb

        # Set safety buffer
        self.safety_buffer = safety_buffer_gb

        # Calculate available VRAM (total - safety buffer)
        self.available_vram = self.total_vram - self.safety_buffer

        # Service registry: {service_name: {vram: float, priority: int, loaded_at: float}}
        self.loaded_services: Dict[str, Dict] = {}

        # Pending queue: (priority, timestamp, service_name, required_vram_gb)
        # Higher priority = lower number in queue (processed first)
        self.pending_queue: queue.PriorityQueue = queue.PriorityQueue()

        # Thread safety
        self._lock = threading.Lock()

    def get_available_vram(self) -> float:
        """
        Query available VRAM via GPU monitor.

        Returns actual free VRAM minus safety buffer.
        Uses GPUMonitor's internal caching (2-second TTL).

        Returns:
            Available VRAM in GB (never negative)

        Example:
            >>> manager = SmartVRAMManager()
            >>> manager.get_available_vram()
            7.3  # 7.8GB free - 0.5GB safety buffer
        """
        # Query GPU for current free VRAM
        free_vram_gb = self.gpu_monitor.get_free_vram_gb()

        # Subtract safety buffer
        available = free_vram_gb - self.safety_buffer

        # Never return negative
        return max(0.0, available)

    def get_status(self) -> Dict:
        """
        Get diagnostic status information.

        Returns current VRAM allocation state for debugging/monitoring.

        Returns:
            Dict with keys:
                - total_vram: Total GPU VRAM (GB)
                - safety_buffer: Safety buffer (GB)
                - allocated_vram: Currently allocated VRAM (GB)
                - loaded_services: List of loaded service dicts
                - pending_count: Number of services in pending queue

        Example:
            >>> manager = SmartVRAMManager()
            >>> status = manager.get_status()
            >>> status
            {
                'total_vram': 8.0,
                'safety_buffer': 0.5,
                'allocated_vram': 0.0,
                'loaded_services': [],
                'pending_count': 0
            }
        """
        with self._lock:
            # Calculate total allocated VRAM
            allocated_vram = sum(
                service_info["vram"]
                for service_info in self.loaded_services.values()
            )

            # Build loaded services list
            loaded_services_list = [
                {
                    "name": service_name,
                    "vram": service_info["vram"],
                    "priority": service_info["priority"]
                }
                for service_name, service_info in self.loaded_services.items()
            ]

            return {
                "total_vram": self.total_vram,
                "safety_buffer": self.safety_buffer,
                "allocated_vram": allocated_vram,
                "loaded_services": loaded_services_list,
                "pending_count": self.pending_queue.qsize()
            }
