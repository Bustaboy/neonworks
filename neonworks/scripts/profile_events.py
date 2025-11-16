"""
Profile event system performance

Tests event subscription, emission, and processing performance.
Target: Low overhead for event dispatch
"""

import sys
from pathlib import Path

# Add parent of parent directory to path so neonworks package can be found
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from neonworks.core.events import Event, EventManager, EventType
from neonworks.utils.profiler import PerformanceProfiler


def profile_event_subscription(profiler: PerformanceProfiler):
    """Profile event subscription"""
    event_manager = EventManager()

    def dummy_handler(event: Event):
        pass

    # Subscribe many handlers
    with profiler.measure("event_subscribe_100"):
        for i in range(100):
            event_manager.subscribe(EventType.CUSTOM, dummy_handler)

    return event_manager


def profile_event_emission(
    event_manager: EventManager, handler_count: int, profiler: PerformanceProfiler
):
    """Profile event emission with varying handler counts"""
    # Set up handlers
    call_count = 0

    def counting_handler(event: Event):
        nonlocal call_count
        call_count += 1

    for i in range(handler_count):
        event_manager.subscribe(EventType.CUSTOM, counting_handler)

    # Set immediate mode so events are dispatched immediately
    event_manager.set_immediate_mode(True)

    # Emit events
    with profiler.measure(f"event_emit_{handler_count}_handlers"):
        for i in range(1000):
            event_manager.emit(Event(EventType.CUSTOM, data={"value": i}))


def profile_event_processing(profiler: PerformanceProfiler):
    """Profile event queue processing"""
    event_manager = EventManager()

    def dummy_handler(event: Event):
        # Simulate some work
        _ = event.data.get("value", 0) * 2

    event_manager.subscribe(EventType.CUSTOM, dummy_handler)

    # Queue many events
    with profiler.measure("event_queue_1000"):
        for i in range(1000):
            event_manager.emit(Event(EventType.CUSTOM, data={"value": i}))

    # Process queue
    with profiler.measure("event_process_1000"):
        event_manager.process_events()


def profile_event_types(profiler: PerformanceProfiler):
    """Profile different event types"""
    event_manager = EventManager()

    handlers_called = 0

    def handler1(event: Event):
        nonlocal handlers_called
        handlers_called += 1

    def handler2(event: Event):
        nonlocal handlers_called
        handlers_called += 1

    # Subscribe to multiple event types
    event_types = [
        EventType.TURN_START,
        EventType.TURN_END,
        EventType.COMBAT_START,
        EventType.COMBAT_END,
        EventType.DAMAGE_DEALT,
    ]

    for event_type in event_types:
        event_manager.subscribe(event_type, handler1)
        event_manager.subscribe(event_type, handler2)

    # Set immediate mode
    event_manager.set_immediate_mode(True)

    # Emit various events
    with profiler.measure("event_multi_type_emission"):
        for i in range(200):
            for event_type in event_types:
                event_manager.emit(Event(event_type, data={"iteration": i}))


def profile_event_system():
    """Profile event system"""
    print("\nProfiling event system...")

    profiler = PerformanceProfiler()

    # Test subscription
    print("Profiling subscriptions...")
    event_manager = profile_event_subscription(profiler)

    # Test emission with varying handler counts
    print("Profiling emissions...")
    for handler_count in [1, 10, 50, 100]:
        em = EventManager()
        profile_event_emission(em, handler_count, profiler)

    # Test queue processing
    print("Profiling queue processing...")
    profile_event_processing(profiler)

    # Test multiple event types
    print("Profiling multiple event types...")
    profile_event_types(profiler)

    # Print results
    print(f"\n{'=' * 70}")
    print("EVENT SYSTEM PERFORMANCE")
    print(f"{'=' * 70}")

    profiler.print_report()

    return {
        "metrics": profiler.get_all_metrics(),
    }


def profile_event_stress_test():
    """Stress test event system"""
    print("\n" + "=" * 70)
    print("EVENT SYSTEM STRESS TEST")
    print("=" * 70)

    profiler = PerformanceProfiler()

    # Test with many events
    event_manager = EventManager()
    event_manager.set_immediate_mode(True)

    def dummy_handler(event: Event):
        pass

    # Add 1000 handlers
    for i in range(1000):
        event_manager.subscribe(EventType.CUSTOM, dummy_handler)

    # Emit 10000 events
    print("Emitting 10000 events to 1000 handlers...")
    with profiler.measure("stress_test_10000_events"):
        for i in range(10000):
            event_manager.emit(Event(EventType.CUSTOM, data={"value": i}))

    metric = profiler.get_metric("stress_test_10000_events")
    if metric:
        print(f"\nTotal time: {metric.total_time:.4f}s")
        print(f"Average per event: {metric.total_time / 10000 * 1000:.4f}ms")
        print(f"Events per second: {10000 / metric.total_time:.0f}")

    return profiler.get_all_metrics()


if __name__ == "__main__":
    # Run basic test
    profile_event_system()

    # Run stress test
    # profile_event_stress_test()
