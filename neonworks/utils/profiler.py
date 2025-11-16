"""
Performance Profiling Utilities

Tools for profiling and benchmarking NeonWorks engine performance.
"""

import cProfile
import functools
import io
import pstats
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


@dataclass
class PerformanceMetrics:
    """Performance metrics for a profiled operation"""

    name: str
    duration: float  # seconds
    call_count: int = 0
    total_time: float = 0.0
    avg_time: float = 0.0
    min_time: float = float("inf")
    max_time: float = 0.0
    samples: List[float] = field(default_factory=list)

    def add_sample(self, duration: float):
        """Add a timing sample"""
        self.samples.append(duration)
        self.call_count += 1
        self.total_time += duration
        self.avg_time = self.total_time / self.call_count
        self.min_time = min(self.min_time, duration)
        self.max_time = max(self.max_time, duration)

    def __str__(self) -> str:
        """Format metrics as string"""
        return (
            f"{self.name}:\n"
            f"  Calls: {self.call_count}\n"
            f"  Total: {self.total_time:.4f}s\n"
            f"  Avg: {self.avg_time * 1000:.2f}ms\n"
            f"  Min: {self.min_time * 1000:.2f}ms\n"
            f"  Max: {self.max_time * 1000:.2f}ms\n"
        )


class PerformanceProfiler:
    """
    Performance profiler for tracking timing metrics.

    Usage:
        profiler = PerformanceProfiler()

        with profiler.measure("operation_name"):
            # Code to profile
            pass

        # Or use as decorator
        @profiler.profile("function_name")
        def my_function():
            pass

        # Get results
        profiler.print_report()
    """

    def __init__(self):
        self.metrics: Dict[str, PerformanceMetrics] = {}
        self._start_times: Dict[str, float] = {}

    @contextmanager
    def measure(self, name: str):
        """Context manager for measuring execution time"""
        start_time = time.perf_counter()
        try:
            yield
        finally:
            duration = time.perf_counter() - start_time
            self._record_metric(name, duration)

    def profile(self, name: Optional[str] = None):
        """Decorator for profiling function calls"""

        def decorator(func: Callable) -> Callable:
            metric_name = name or f"{func.__module__}.{func.__name__}"

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                with self.measure(metric_name):
                    return func(*args, **kwargs)

            return wrapper

        return decorator

    def _record_metric(self, name: str, duration: float):
        """Record a timing metric"""
        if name not in self.metrics:
            self.metrics[name] = PerformanceMetrics(name=name, duration=duration)
        self.metrics[name].add_sample(duration)

    def get_metric(self, name: str) -> Optional[PerformanceMetrics]:
        """Get metrics for a specific operation"""
        return self.metrics.get(name)

    def get_all_metrics(self) -> Dict[str, PerformanceMetrics]:
        """Get all recorded metrics"""
        return self.metrics.copy()

    def print_report(self, sort_by: str = "total"):
        """
        Print performance report.

        Args:
            sort_by: Sort metric ('total', 'avg', 'max', 'calls')
        """
        if not self.metrics:
            print("No metrics recorded")
            return

        print("\n" + "=" * 70)
        print("PERFORMANCE REPORT")
        print("=" * 70)

        # Sort metrics
        sort_key_map = {
            "total": lambda m: m.total_time,
            "avg": lambda m: m.avg_time,
            "max": lambda m: m.max_time,
            "calls": lambda m: m.call_count,
        }
        sort_key = sort_key_map.get(sort_by, sort_key_map["total"])

        sorted_metrics = sorted(self.metrics.values(), key=sort_key, reverse=True)

        for metric in sorted_metrics:
            print(metric)

        print("=" * 70)

    def save_report(self, file_path: str, sort_by: str = "total"):
        """Save performance report to file"""
        with open(file_path, "w") as f:
            f.write("=" * 70 + "\n")
            f.write("PERFORMANCE REPORT\n")
            f.write("=" * 70 + "\n\n")

            sort_key_map = {
                "total": lambda m: m.total_time,
                "avg": lambda m: m.avg_time,
                "max": lambda m: m.max_time,
                "calls": lambda m: m.call_count,
            }
            sort_key = sort_key_map.get(sort_by, sort_key_map["total"])

            sorted_metrics = sorted(self.metrics.values(), key=sort_key, reverse=True)

            for metric in sorted_metrics:
                f.write(str(metric) + "\n")

    def reset(self):
        """Reset all metrics"""
        self.metrics.clear()
        self._start_times.clear()


def profile_function(func: Callable, *args, **kwargs) -> tuple[Any, pstats.Stats]:
    """
    Profile a function using cProfile.

    Args:
        func: Function to profile
        *args: Function arguments
        **kwargs: Function keyword arguments

    Returns:
        Tuple of (function_result, profiling_stats)
    """
    profiler = cProfile.Profile()
    profiler.enable()

    result = func(*args, **kwargs)

    profiler.disable()

    # Get stats
    s = io.StringIO()
    stats = pstats.Stats(profiler, stream=s)
    stats.sort_stats(pstats.SortKey.CUMULATIVE)

    return result, stats


def print_profile_stats(stats: pstats.Stats, top_n: int = 20):
    """Print profiling statistics"""
    print("\n" + "=" * 70)
    print(f"TOP {top_n} FUNCTIONS BY CUMULATIVE TIME")
    print("=" * 70)
    stats.print_stats(top_n)


def save_profile_stats(stats: pstats.Stats, file_path: str, top_n: int = 50):
    """Save profiling statistics to file"""
    with open(file_path, "w") as f:
        stats.stream = f
        stats.sort_stats(pstats.SortKey.CUMULATIVE)
        stats.print_stats(top_n)


class FPSCounter:
    """Track frames per second"""

    def __init__(self, sample_size: int = 60):
        self.sample_size = sample_size
        self.frame_times: List[float] = []
        self.last_frame_time = time.perf_counter()

    def tick(self) -> float:
        """Record a frame and return current FPS"""
        current_time = time.perf_counter()
        frame_time = current_time - self.last_frame_time
        self.last_frame_time = current_time

        self.frame_times.append(frame_time)
        if len(self.frame_times) > self.sample_size:
            self.frame_times.pop(0)

        if not self.frame_times:
            return 0.0

        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg_frame_time if avg_frame_time > 0 else 0.0

    def get_stats(self) -> Dict[str, float]:
        """Get FPS statistics"""
        if not self.frame_times:
            return {"fps": 0.0, "avg_ms": 0.0, "min_fps": 0.0, "max_fps": 0.0}

        avg_time = sum(self.frame_times) / len(self.frame_times)
        min_time = min(self.frame_times)
        max_time = max(self.frame_times)

        return {
            "fps": 1.0 / avg_time if avg_time > 0 else 0.0,
            "avg_ms": avg_time * 1000,
            "min_fps": 1.0 / max_time if max_time > 0 else 0.0,
            "max_fps": 1.0 / min_time if min_time > 0 else 0.0,
        }


# Global profiler instance
_global_profiler = PerformanceProfiler()


def get_profiler() -> PerformanceProfiler:
    """Get the global profiler instance"""
    return _global_profiler


def measure(name: str):
    """Shortcut to global profiler's measure context manager"""
    return _global_profiler.measure(name)


def profile(name: Optional[str] = None):
    """Shortcut to global profiler's profile decorator"""
    return _global_profiler.profile(name)
