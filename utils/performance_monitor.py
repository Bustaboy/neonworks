"""
Performance Monitoring System

Real-time performance tracking and reporting for production use.
Tracks FPS, frame times, memory usage, and system health.
"""

import time
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Deque, Dict, List, Optional

import psutil


@dataclass
class FrameMetrics:
    """Metrics for a single frame"""

    frame_number: int
    frame_time: float  # Total frame time in seconds
    update_time: float  # Time spent in update
    render_time: float  # Time spent in rendering
    event_time: float  # Time spent processing events
    timestamp: float  # Absolute timestamp


@dataclass
class PerformanceStats:
    """Aggregated performance statistics"""

    avg_fps: float = 0.0
    min_fps: float = 0.0
    max_fps: float = 0.0
    avg_frame_time_ms: float = 0.0
    min_frame_time_ms: float = 0.0
    max_frame_time_ms: float = 0.0

    frame_time_variance: float = 0.0  # Standard deviation
    dropped_frames: int = 0  # Frames that took >33ms (below 30 FPS)

    avg_update_time_ms: float = 0.0
    avg_render_time_ms: float = 0.0
    avg_event_time_ms: float = 0.0

    memory_used_mb: float = 0.0
    memory_percent: float = 0.0

    entity_count: int = 0
    event_count: int = 0


class PerformanceMonitor:
    """
    Monitor and log engine performance in real-time.

    Tracks frame times, FPS, memory usage, and provides performance
    alerts when metrics fall below acceptable thresholds.

    Usage:
        monitor = PerformanceMonitor(window_size=60)

        # Start frame
        monitor.begin_frame()

        # Track update
        monitor.begin_update()
        # ... update code ...
        monitor.end_update()

        # Track rendering
        monitor.begin_render()
        # ... rendering code ...
        monitor.end_render()

        # End frame
        monitor.end_frame()

        # Get stats
        stats = monitor.get_stats()
        print(f"FPS: {stats.avg_fps:.1f}")
    """

    def __init__(
        self,
        window_size: int = 60,
        target_fps: float = 60.0,
        enable_warnings: bool = True,
    ):
        """
        Initialize performance monitor.

        Args:
            window_size: Number of frames to average over (default: 60)
            target_fps: Target FPS for warnings (default: 60.0)
            enable_warnings: Whether to print performance warnings
        """
        self.window_size = window_size
        self.target_fps = target_fps
        self.enable_warnings = enable_warnings

        # Frame tracking
        self.frame_count = 0
        self.frame_history: Deque[FrameMetrics] = deque(maxlen=window_size)

        # Current frame timers
        self._frame_start_time: float = 0.0
        self._update_start_time: float = 0.0
        self._render_start_time: float = 0.0
        self._event_start_time: float = 0.0

        # Accumulated times for current frame
        self._current_update_time: float = 0.0
        self._current_render_time: float = 0.0
        self._current_event_time: float = 0.0

        # External metrics
        self._entity_count: int = 0
        self._event_count: int = 0

        # Process info for memory tracking
        self._process = psutil.Process()

        # Performance warnings
        self._consecutive_slow_frames = 0
        self._max_consecutive_slow_frames = 5

    def begin_frame(self):
        """Mark the beginning of a frame"""
        self._frame_start_time = time.perf_counter()
        self._current_update_time = 0.0
        self._current_render_time = 0.0
        self._current_event_time = 0.0

    def end_frame(self):
        """Mark the end of a frame and record metrics"""
        frame_end_time = time.perf_counter()
        frame_time = frame_end_time - self._frame_start_time

        # Create frame metrics
        metrics = FrameMetrics(
            frame_number=self.frame_count,
            frame_time=frame_time,
            update_time=self._current_update_time,
            render_time=self._current_render_time,
            event_time=self._current_event_time,
            timestamp=frame_end_time,
        )

        self.frame_history.append(metrics)
        self.frame_count += 1

        # Check for performance warnings
        if self.enable_warnings:
            self._check_performance(metrics)

    def begin_update(self):
        """Mark the beginning of update phase"""
        self._update_start_time = time.perf_counter()

    def end_update(self):
        """Mark the end of update phase"""
        self._current_update_time += time.perf_counter() - self._update_start_time

    def begin_render(self):
        """Mark the beginning of render phase"""
        self._render_start_time = time.perf_counter()

    def end_render(self):
        """Mark the end of render phase"""
        self._current_render_time += time.perf_counter() - self._render_start_time

    def begin_event_processing(self):
        """Mark the beginning of event processing"""
        self._event_start_time = time.perf_counter()

    def end_event_processing(self):
        """Mark the end of event processing"""
        self._current_event_time += time.perf_counter() - self._event_start_time

    def set_entity_count(self, count: int):
        """Update entity count metric"""
        self._entity_count = count

    def set_event_count(self, count: int):
        """Update event count metric"""
        self._event_count = count

    def get_stats(self) -> PerformanceStats:
        """
        Calculate and return current performance statistics.

        Returns:
            PerformanceStats object with aggregated metrics
        """
        if not self.frame_history:
            return PerformanceStats()

        frame_times = [m.frame_time for m in self.frame_history]
        update_times = [m.update_time for m in self.frame_history]
        render_times = [m.render_time for m in self.frame_history]
        event_times = [m.event_time for m in self.frame_history]

        # Calculate FPS from frame times
        valid_frame_times = [ft for ft in frame_times if ft > 0]
        if valid_frame_times:
            avg_frame_time = sum(valid_frame_times) / len(valid_frame_times)
            min_frame_time = min(valid_frame_times)
            max_frame_time = max(valid_frame_times)

            avg_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
            max_fps = 1.0 / min_frame_time if min_frame_time > 0 else 0
            min_fps = 1.0 / max_frame_time if max_frame_time > 0 else 0
        else:
            avg_fps = min_fps = max_fps = 0.0
            avg_frame_time = min_frame_time = max_frame_time = 0.0

        # Calculate variance
        if len(valid_frame_times) > 1:
            mean = avg_frame_time
            variance = sum((x - mean) ** 2 for x in valid_frame_times) / len(
                valid_frame_times
            )
            frame_time_variance = variance**0.5 * 1000  # Convert to ms
        else:
            frame_time_variance = 0.0

        # Count dropped frames (frames that took >33ms = below 30 FPS)
        dropped_frames = sum(1 for ft in frame_times if ft > 0.033)

        # Memory usage
        mem_info = self._process.memory_info()
        memory_used_mb = mem_info.rss / (1024 * 1024)
        memory_percent = self._process.memory_percent()

        return PerformanceStats(
            avg_fps=avg_fps,
            min_fps=min_fps,
            max_fps=max_fps,
            avg_frame_time_ms=avg_frame_time * 1000,
            min_frame_time_ms=min_frame_time * 1000,
            max_frame_time_ms=max_frame_time * 1000,
            frame_time_variance=frame_time_variance,
            dropped_frames=dropped_frames,
            avg_update_time_ms=sum(update_times) / len(update_times) * 1000
            if update_times
            else 0,
            avg_render_time_ms=sum(render_times) / len(render_times) * 1000
            if render_times
            else 0,
            avg_event_time_ms=sum(event_times) / len(event_times) * 1000
            if event_times
            else 0,
            memory_used_mb=memory_used_mb,
            memory_percent=memory_percent,
            entity_count=self._entity_count,
            event_count=self._event_count,
        )

    def _check_performance(self, metrics: FrameMetrics):
        """Check for performance issues and print warnings"""
        target_frame_time = 1.0 / self.target_fps

        if metrics.frame_time > target_frame_time:
            self._consecutive_slow_frames += 1

            if self._consecutive_slow_frames >= self._max_consecutive_slow_frames:
                fps = 1.0 / metrics.frame_time if metrics.frame_time > 0 else 0
                print(
                    f"⚠️  Performance Warning: {self._consecutive_slow_frames} "
                    f"consecutive slow frames (FPS: {fps:.1f}, "
                    f"Target: {self.target_fps:.1f})"
                )
                self._consecutive_slow_frames = 0
        else:
            self._consecutive_slow_frames = 0

    def get_recent_frame_times(self, count: int = 60) -> List[float]:
        """
        Get recent frame times for graphing.

        Args:
            count: Number of recent frames to return

        Returns:
            List of frame times in milliseconds
        """
        recent = list(self.frame_history)[-count:]
        return [m.frame_time * 1000 for m in recent]

    def print_stats(self):
        """Print current performance statistics to console"""
        stats = self.get_stats()

        print("\n" + "=" * 60)
        print("PERFORMANCE STATISTICS")
        print("=" * 60)
        print(f"FPS:              {stats.avg_fps:.1f} "
              f"(min: {stats.min_fps:.1f}, max: {stats.max_fps:.1f})")
        print(f"Frame Time:       {stats.avg_frame_time_ms:.2f}ms "
              f"(±{stats.frame_time_variance:.2f}ms)")
        print(f"  Update:         {stats.avg_update_time_ms:.2f}ms")
        print(f"  Render:         {stats.avg_render_time_ms:.2f}ms")
        print(f"  Events:         {stats.avg_event_time_ms:.2f}ms")
        print(f"Dropped Frames:   {stats.dropped_frames} "
              f"({stats.dropped_frames / len(self.frame_history) * 100:.1f}%)")
        print(f"Memory:           {stats.memory_used_mb:.1f} MB "
              f"({stats.memory_percent:.1f}%)")
        print(f"Entities:         {stats.entity_count}")
        print(f"Events/Frame:     {stats.event_count}")
        print("=" * 60)

    def save_log(self, filepath: Path):
        """
        Save performance log to file.

        Args:
            filepath: Path to save log file
        """
        stats = self.get_stats()

        with open(filepath, "w") as f:
            f.write("NeonWorks Performance Log\n")
            f.write("=" * 60 + "\n\n")

            f.write(f"Total Frames:     {self.frame_count}\n")
            f.write(f"Average FPS:      {stats.avg_fps:.2f}\n")
            f.write(f"Min FPS:          {stats.min_fps:.2f}\n")
            f.write(f"Max FPS:          {stats.max_fps:.2f}\n")
            f.write(f"Avg Frame Time:   {stats.avg_frame_time_ms:.2f}ms\n")
            f.write(f"Frame Variance:   {stats.frame_time_variance:.2f}ms\n")
            f.write(f"Dropped Frames:   {stats.dropped_frames}\n\n")

            f.write(f"Avg Update Time:  {stats.avg_update_time_ms:.2f}ms\n")
            f.write(f"Avg Render Time:  {stats.avg_render_time_ms:.2f}ms\n")
            f.write(f"Avg Event Time:   {stats.avg_event_time_ms:.2f}ms\n\n")

            f.write(f"Memory Used:      {stats.memory_used_mb:.2f} MB\n")
            f.write(f"Memory Percent:   {stats.memory_percent:.2f}%\n")
            f.write(f"Entity Count:     {stats.entity_count}\n")
            f.write(f"Event Count:      {stats.event_count}\n\n")

            f.write("Recent Frame Times (ms):\n")
            frame_times = self.get_recent_frame_times(60)
            for i, ft in enumerate(frame_times):
                f.write(f"Frame {self.frame_count - len(frame_times) + i}: {ft:.2f}ms\n")

    def reset(self):
        """Reset all metrics"""
        self.frame_count = 0
        self.frame_history.clear()
        self._consecutive_slow_frames = 0


# Global performance monitor instance
_global_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get or create the global performance monitor"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor


def enable_performance_monitoring(target_fps: float = 60.0, enable_warnings: bool = True):
    """
    Enable global performance monitoring.

    Args:
        target_fps: Target FPS for performance warnings
        enable_warnings: Whether to print performance warnings
    """
    global _global_monitor
    _global_monitor = PerformanceMonitor(
        window_size=60, target_fps=target_fps, enable_warnings=enable_warnings
    )


def disable_performance_monitoring():
    """Disable global performance monitoring"""
    global _global_monitor
    _global_monitor = None
