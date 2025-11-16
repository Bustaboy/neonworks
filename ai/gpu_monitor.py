"""
GPU Monitoring for VRAM Management

Provides unified interface for querying GPU VRAM across multiple vendors (NVIDIA, AMD).
Auto-detects GPU vendor and uses appropriate monitoring tool (nvidia-smi or rocm-smi).
"""

import json
import shutil
import subprocess
import time
from enum import Enum
from typing import Optional


class GPUVendor(Enum):
    """Supported GPU vendors."""

    NVIDIA = "nvidia"
    AMD = "amd"
    UNKNOWN = "unknown"


class SystemRequirementError(Exception):
    """Raised when system requirements are not met (no GPU monitoring tool)."""

    pass


class GPUMonitor:
    """
    GPU detection and VRAM monitoring.

    Automatically detects GPU vendor (NVIDIA or AMD) and uses appropriate
    monitoring tool (nvidia-smi or rocm-smi) to query VRAM usage.

    Features:
        - Auto-detection of GPU vendor
        - Unified interface (get_free_vram_gb() works for all vendors)
        - Built-in caching (2-second TTL) to reduce subprocess overhead
        - Clear error messages with installation links if tools missing

    System Requirements:
        - NVIDIA GPUs: nvidia-smi (comes with NVIDIA drivers)
        - AMD GPUs: rocm-smi (comes with ROCm drivers)

    Raises:
        SystemRequirementError: If no supported GPU monitoring tool found

    Example:
        >>> monitor = GPUMonitor()  # Auto-detects GPU
        >>> monitor.vendor
        <GPUVendor.NVIDIA: 'nvidia'>
        >>> monitor.get_free_vram_gb()
        4.5
        >>> monitor.get_total_vram_gb()
        8.0
    """

    def __init__(self):
        """
        Initialize GPU monitor with auto-detection.

        Raises:
            SystemRequirementError: If no GPU monitoring tool found
        """
        # Detect GPU vendor
        self.vendor = self._detect_gpu_vendor()

        # Validate that required tool exists
        self._validate_monitoring_tool()

        # VRAM query cache (2-second TTL)
        self._vram_cache: Optional[float] = None
        self._vram_cache_time: float = 0
        self._cache_ttl: float = 2.0  # Cache for 2 seconds

    def _detect_gpu_vendor(self) -> GPUVendor:
        """
        Detect GPU vendor by checking for monitoring tools.

        Checks for nvidia-smi first, then rocm-smi.
        NVIDIA is preferred if both exist (rare but possible).

        Returns:
            GPUVendor enum value (NVIDIA, AMD, or UNKNOWN)
        """
        # Check for nvidia-smi (NVIDIA GPUs)
        if self._tool_exists("nvidia-smi"):
            return GPUVendor.NVIDIA

        # Check for rocm-smi (AMD GPUs)
        if self._tool_exists("rocm-smi"):
            return GPUVendor.AMD

        # No supported tool found
        return GPUVendor.UNKNOWN

    def _tool_exists(self, command: str) -> bool:
        """
        Check if command exists in PATH.

        Args:
            command: Command name to check (e.g., 'nvidia-smi')

        Returns:
            True if command found in PATH, False otherwise
        """
        return shutil.which(command) is not None

    def _validate_monitoring_tool(self):
        """
        Validate that required monitoring tool is available.

        Raises:
            SystemRequirementError: If no supported tool found, with helpful
                installation instructions
        """
        if self.vendor == GPUVendor.UNKNOWN:
            raise SystemRequirementError(
                "No supported GPU monitoring tool found.\n"
                "NeonWorks AI features require one of:\n"
                "  - nvidia-smi (NVIDIA GPUs) - Install NVIDIA drivers\n"
                "  - rocm-smi (AMD GPUs) - Install ROCm drivers\n\n"
                "Installation guides:\n"
                "  NVIDIA: https://www.nvidia.com/download/index.aspx\n"
                "  AMD: https://rocm.docs.amd.com/en/latest/deploy/linux/quick_start.html"
            )

    def get_free_vram_gb(self) -> float:
        """
        Get free VRAM in GB (cached for 2 seconds).

        Queries GPU monitoring tool (nvidia-smi or rocm-smi) based on detected vendor.
        Results are cached for 2 seconds to reduce subprocess overhead.

        Returns:
            Free VRAM in GB

        Raises:
            RuntimeError: If monitoring tool fails or output cannot be parsed

        Example:
            >>> monitor = GPUMonitor()
            >>> free = monitor.get_free_vram_gb()
            >>> print(f"Free VRAM: {free:.2f} GB")
            Free VRAM: 4.50 GB
        """
        # Query based on vendor
        if self.vendor == GPUVendor.NVIDIA:
            return self._query_nvidia_free_vram()
        elif self.vendor == GPUVendor.AMD:
            return self._query_amd_free_vram()
        else:
            raise RuntimeError("No GPU monitoring tool available")

    def get_total_vram_gb(self) -> float:
        """
        Get total VRAM in GB.

        Queries GPU for total VRAM capacity.

        Returns:
            Total VRAM in GB

        Raises:
            RuntimeError: If monitoring tool fails

        Example:
            >>> monitor = GPUMonitor()
            >>> total = monitor.get_total_vram_gb()
            >>> print(f"Total VRAM: {total:.2f} GB")
            Total VRAM: 8.00 GB
        """
        # Query based on vendor
        if self.vendor == GPUVendor.NVIDIA:
            return self._get_nvidia_total_vram()
        elif self.vendor == GPUVendor.AMD:
            return self._get_amd_total_vram()
        else:
            raise RuntimeError("No GPU monitoring tool available")

    def _query_nvidia_free_vram(self) -> float:
        """
        Query nvidia-smi for free VRAM.

        Returns:
            Free VRAM in GB

        Raises:
            RuntimeError: If query fails
        """
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,nounits,noheader"],
                capture_output=True,
                text=True,
                timeout=5.0,
            )

            if result.returncode != 0:
                raise RuntimeError(f"nvidia-smi failed: {result.stderr}")

            # Parse output (MB)
            free_mb = float(result.stdout.strip().split("\n")[0])
            return free_mb / 1024.0  # Convert to GB

        except subprocess.TimeoutExpired:
            raise RuntimeError("nvidia-smi timeout (5s)")
        except (ValueError, IndexError) as e:
            raise RuntimeError(f"Failed to parse nvidia-smi output: {e}")

    def _get_nvidia_total_vram(self) -> float:
        """
        Query nvidia-smi for total VRAM.

        Returns:
            Total VRAM in GB

        Raises:
            RuntimeError: If query fails
        """
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,nounits,noheader"],
                capture_output=True,
                text=True,
                timeout=5.0,
            )

            if result.returncode != 0:
                raise RuntimeError(f"nvidia-smi failed: {result.stderr}")

            # Parse output (MB)
            total_mb = float(result.stdout.strip().split("\n")[0])
            return total_mb / 1024.0  # Convert to GB

        except subprocess.TimeoutExpired:
            raise RuntimeError("nvidia-smi timeout (5s)")
        except (ValueError, IndexError) as e:
            raise RuntimeError(f"Failed to parse nvidia-smi output: {e}")

    def _query_amd_free_vram(self) -> float:
        """
        Query rocm-smi for free VRAM.

        Returns:
            Free VRAM in GB

        Raises:
            RuntimeError: If query fails
        """
        try:
            result = subprocess.run(
                ["rocm-smi", "--showmeminfo", "vram", "--json"],
                capture_output=True,
                text=True,
                timeout=5.0,
            )

            if result.returncode != 0:
                raise RuntimeError(f"rocm-smi failed: {result.stderr}")

            # Parse JSON output
            data = json.loads(result.stdout)

            # ROCm SMI returns data per card (card0, card1, etc.)
            # Get first card's VRAM info
            card_key = next(iter(data.keys()))
            vram_info = data[card_key]

            # Extract free VRAM in bytes, convert to GB
            # Format: {"VRAM Total Memory (B)": ..., "VRAM Total Used Memory (B)": ...}
            total_bytes = vram_info.get("VRAM Total Memory (B)", 0)
            used_bytes = vram_info.get("VRAM Total Used Memory (B)", 0)
            free_bytes = total_bytes - used_bytes

            return free_bytes / (1024.0**3)  # Convert bytes to GB

        except subprocess.TimeoutExpired:
            raise RuntimeError("rocm-smi timeout (5s)")
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise RuntimeError(f"Failed to parse rocm-smi output: {e}")

    def _get_amd_total_vram(self) -> float:
        """
        Query rocm-smi for total VRAM.

        Returns:
            Total VRAM in GB

        Raises:
            RuntimeError: If query fails
        """
        try:
            result = subprocess.run(
                ["rocm-smi", "--showmeminfo", "vram", "--json"],
                capture_output=True,
                text=True,
                timeout=5.0,
            )

            if result.returncode != 0:
                raise RuntimeError(f"rocm-smi failed: {result.stderr}")

            # Parse JSON output
            data = json.loads(result.stdout)
            card_key = next(iter(data.keys()))
            total_bytes = data[card_key].get("VRAM Total Memory (B)", 0)

            return total_bytes / (1024.0**3)  # Convert bytes to GB

        except subprocess.TimeoutExpired:
            raise RuntimeError("rocm-smi timeout (5s)")
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise RuntimeError(f"Failed to parse rocm-smi output: {e}")

    def invalidate_cache(self):
        """
        Invalidate VRAM cache (force fresh query on next call).

        Useful when you know VRAM has changed (e.g., after loading/unloading model).

        Example:
            >>> monitor = GPUMonitor()
            >>> monitor.get_free_vram_gb()  # Queries GPU
            4.5
            >>> monitor.get_free_vram_gb()  # Uses cache
            4.5
            >>> monitor.invalidate_cache()
            >>> monitor.get_free_vram_gb()  # Queries GPU again
            6.2
        """
        self._vram_cache = None
