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

    def request_vram(
        self,
        service_name: str,
        required_vram_gb: float,
        priority: int
    ) -> bool:
        """
        Request VRAM allocation for a service.

        Attempts to allocate requested VRAM. If service already loaded,
        updates its allocation. If insufficient VRAM, returns False
        (eviction logic in iteration 8, queuing in iteration 9).

        Args:
            service_name: Service identifier (e.g., "llm", "image", "tts")
            required_vram_gb: VRAM needed in GB (exact amount, not percentage)
            priority: VRAMPriority level (1=BACKGROUND, 5=NORMAL, 8=USER_REQUESTED, 10=UI_CRITICAL)

        Returns:
            True if allocation successful, False if insufficient VRAM

        Emits:
            VRAM_ALLOCATED event on success (service, vram_allocated, priority)
            VRAM_ALLOCATION_FAILED event on failure (service, required_vram, queued)

        Example:
            >>> manager = SmartVRAMManager()
            >>> # Request 4.0GB for SDXL image generation
            >>> success = manager.request_vram(
            ...     service_name="image",
            ...     required_vram_gb=4.0,
            ...     priority=VRAMPriority.USER_REQUESTED
            ... )
            >>> success
            True

            >>> # Check allocation
            >>> manager.get_status()
            {'allocated_vram': 4.0, 'loaded_services': [{'name': 'image', ...}]}
        """
        with self._lock:
            # Check if enough VRAM available
            available = self.get_available_vram()

            # If service already loaded, we're updating (free old allocation first)
            if service_name in self.loaded_services:
                # Free current allocation
                current_vram = self.loaded_services[service_name]["vram"]
                available += current_vram

            # Check if we have enough VRAM
            if required_vram_gb > available:
                # Try to free VRAM by evicting lower priority services
                freed_vram = self._free_lower_priority_services(
                    required_vram=required_vram_gb,
                    requesting_priority=priority
                )

                # Re-check available VRAM after eviction
                available = self.get_available_vram()
                if service_name in self.loaded_services:
                    available += self.loaded_services[service_name]["vram"]

                # If still insufficient, queue for later
                if required_vram_gb > available:
                    # Add to pending queue for sequential loading
                    self._add_to_pending_queue(
                        service_name=service_name,
                        required_vram_gb=required_vram_gb,
                        priority=priority
                    )
                    self._emit_allocation_failed(
                        service_name=service_name,
                        required_vram=required_vram_gb,
                        queued=True
                    )
                    return False

            # Allocate VRAM
            self._allocate_service(
                service_name=service_name,
                required_vram_gb=required_vram_gb,
                priority=priority
            )

            # Emit success event
            self._emit_allocation_success(
                service_name=service_name,
                vram_allocated=required_vram_gb,
                priority=priority
            )

            return True

    def _allocate_service(
        self,
        service_name: str,
        required_vram_gb: float,
        priority: int
    ):
        """
        Internal helper to allocate VRAM to a service.

        Updates loaded_services registry with service info.
        Called after VRAM availability confirmed.

        Args:
            service_name: Service identifier
            required_vram_gb: VRAM to allocate (GB)
            priority: VRAMPriority level

        Note:
            Must be called with self._lock held
        """
        self.loaded_services[service_name] = {
            "vram": required_vram_gb,
            "priority": priority,
            "loaded_at": time.time()
        }

    def _emit_allocation_success(
        self,
        service_name: str,
        vram_allocated: float,
        priority: int
    ):
        """
        Emit VRAM_ALLOCATED event.

        Posts Pygame event to notify UI of successful allocation.

        Args:
            service_name: Service that was allocated VRAM
            vram_allocated: Amount allocated (GB)
            priority: VRAMPriority level
        """
        from ai.events import VRAM_ALLOCATED

        event = pygame.event.Event(
            VRAM_ALLOCATED,
            {
                "service": service_name,
                "vram_allocated": vram_allocated,
                "priority": priority
            }
        )
        pygame.event.post(event)

    def _emit_allocation_failed(
        self,
        service_name: str,
        required_vram: float,
        queued: bool
    ):
        """
        Emit VRAM_ALLOCATION_FAILED event.

        Posts Pygame event to notify UI of allocation failure.

        Args:
            service_name: Service that failed to allocate
            required_vram: Amount requested (GB)
            queued: Whether service was queued for later execution
        """
        from ai.events import VRAM_ALLOCATION_FAILED

        event = pygame.event.Event(
            VRAM_ALLOCATION_FAILED,
            {
                "service": service_name,
                "required_vram": required_vram,
                "queued": queued
            }
        )
        pygame.event.post(event)

    def _free_lower_priority_services(
        self,
        required_vram: float,
        requesting_priority: int
    ) -> float:
        """
        Free VRAM by evicting lower priority services.

        Evicts services with priority < requesting_priority until
        enough VRAM is freed to satisfy the request.

        Args:
            required_vram: Amount of VRAM needed (GB)
            requesting_priority: Priority of requesting service

        Returns:
            Total VRAM freed (GB)

        Note:
            Must be called with self._lock held
        """
        # Find all lower priority services
        lower_priority_services = [
            (name, info)
            for name, info in self.loaded_services.items()
            if info["priority"] < requesting_priority
        ]

        # If no lower priority services, cannot evict
        if not lower_priority_services:
            return 0.0

        # Sort by priority (lowest first) for greedy eviction
        # This evicts lowest priority services first
        lower_priority_services.sort(key=lambda x: x[1]["priority"])

        # Evict services until we have enough VRAM
        freed_vram = 0.0
        current_available = self.get_available_vram()

        for service_name, service_info in lower_priority_services:
            # Check if we have enough VRAM now
            if current_available + freed_vram >= required_vram:
                break

            # Evict this service
            vram_freed = service_info["vram"]
            del self.loaded_services[service_name]
            freed_vram += vram_freed

            # Emit VRAM_RELEASED event
            self._emit_vram_released(
                service_name=service_name,
                vram_freed=vram_freed
            )

        return freed_vram

    def _emit_vram_released(
        self,
        service_name: str,
        vram_freed: float
    ):
        """
        Emit VRAM_RELEASED event.

        Posts Pygame event to notify UI of VRAM release.

        Args:
            service_name: Service that was unloaded
            vram_freed: Amount of VRAM freed (GB)
        """
        from ai.events import VRAM_RELEASED

        event = pygame.event.Event(
            VRAM_RELEASED,
            {
                "service": service_name,
                "vram_freed": vram_freed
            }
        )
        pygame.event.post(event)

    def release_vram(self, service_name: str) -> bool:
        """
        Manually release VRAM for a service.

        Unloads service and frees its VRAM allocation.
        Processes pending queue after release to allocate waiting requests.

        Args:
            service_name: Service to unload

        Returns:
            True if service was loaded and released, False if not loaded

        Emits:
            VRAM_RELEASED event on success

        Example:
            >>> manager = SmartVRAMManager()
            >>> manager.request_vram("llm", 3.2, VRAMPriority.NORMAL)
            True
            >>> # LLM finishes generation
            >>> manager.release_vram("llm")
            True
            >>> # Pending requests now processed
        """
        with self._lock:
            # Check if service is loaded
            if service_name not in self.loaded_services:
                return False

            # Get service info
            service_info = self.loaded_services[service_name]
            vram_freed = service_info["vram"]

            # Remove from registry
            del self.loaded_services[service_name]

            # Emit release event
            self._emit_vram_released(
                service_name=service_name,
                vram_freed=vram_freed
            )

            # Process pending queue (VRAM now available)
            self._process_pending_queue()

            return True

    def _add_to_pending_queue(
        self,
        service_name: str,
        required_vram_gb: float,
        priority: int
    ):
        """
        Add service request to pending queue.

        Queue uses priority for ordering (higher priority = processed first).
        Uses timestamp as tiebreaker for same-priority requests.

        Args:
            service_name: Service identifier
            required_vram_gb: VRAM needed (GB)
            priority: VRAMPriority level

        Note:
            Must be called with self._lock held
        """
        # PriorityQueue uses tuple: (priority, timestamp, data)
        # Lower number = higher priority, so negate to get correct order
        # (Python's PriorityQueue is min-heap, we want max-priority first)
        self.pending_queue.put((
            -priority,  # Negate so higher priority comes first
            time.time(),  # Timestamp for FIFO tiebreaker
            {
                "service_name": service_name,
                "required_vram_gb": required_vram_gb,
                "priority": priority
            }
        ))

    def _process_pending_queue(self):
        """
        Process pending queue after VRAM released.

        Attempts to allocate VRAM for queued requests in priority order.
        Stops when queue empty or no more VRAM available.

        Note:
            Must be called with self._lock held
        """
        # Process queue until empty or allocation fails
        while not self.pending_queue.empty():
            # Peek at next request (don't remove yet)
            try:
                priority_neg, timestamp, request_data = self.pending_queue.get_nowait()
            except queue.Empty:
                break

            service_name = request_data["service_name"]
            required_vram_gb = request_data["required_vram_gb"]
            priority = request_data["priority"]

            # Check if enough VRAM available now
            available = self.get_available_vram()

            if required_vram_gb <= available:
                # Allocate successfully
                self._allocate_service(
                    service_name=service_name,
                    required_vram_gb=required_vram_gb,
                    priority=priority
                )
                self._emit_allocation_success(
                    service_name=service_name,
                    vram_allocated=required_vram_gb,
                    priority=priority
                )
                # Continue processing queue
            else:
                # Not enough VRAM - put back in queue and stop
                self.pending_queue.put((priority_neg, timestamp, request_data))
                break
