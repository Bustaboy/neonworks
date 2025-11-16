"""
Profile rendering performance

Tests rendering system performance with various entity counts and layers.
Target: 60 FPS in map editor with typical entity counts.
"""

import sys
from pathlib import Path

# Add parent of parent directory to path so neonworks package can be found
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pygame

from neonworks.core.ecs import GridPosition, Sprite, Transform, World
from neonworks.rendering.renderer import Renderer
from neonworks.utils.profiler import FPSCounter, PerformanceProfiler


def create_test_world(entity_count: int = 1000) -> World:
    """Create a world with test entities"""
    world = World()

    # Create entities in a grid
    grid_size = int(entity_count**0.5) + 1

    for i in range(entity_count):
        x = (i % grid_size) * 32
        y = (i // grid_size) * 32
        layer = i % 5  # 5 layers

        entity = world.create_entity(f"Entity_{i}")
        entity.add_component(Transform(x=float(x), y=float(y)))
        entity.add_component(GridPosition(grid_x=x // 32, grid_y=y // 32, layer=layer))
        entity.add_component(Sprite(texture="test_sprite", visible=True))

    return world


def profile_rendering(entity_count: int = 1000, frame_count: int = 300, show_display: bool = False):
    """
    Profile rendering performance.

    Args:
        entity_count: Number of entities to render
        frame_count: Number of frames to render
        show_display: Whether to show the pygame display
    """
    print(f"\nProfiling rendering with {entity_count} entities...")

    # Initialize
    if not show_display:
        # Use dummy video driver for headless profiling
        import os

        os.environ["SDL_VIDEODRIVER"] = "dummy"

    pygame.init()

    profiler = PerformanceProfiler()
    fps_counter = FPSCounter()

    # Create renderer and world
    renderer = Renderer(1280, 720, tile_size=32)
    world = create_test_world(entity_count)

    # Warm-up
    for _ in range(10):
        renderer.clear()
        renderer.render_world(world)
        pygame.display.flip()

    # Profile rendering loop
    print(f"Rendering {frame_count} frames...")
    fps_samples = []

    for frame in range(frame_count):
        # Clear
        with profiler.measure("clear"):
            renderer.clear()

        # Render world
        with profiler.measure("render_world"):
            renderer.render_world(world)

        # Flip display
        with profiler.measure("display_flip"):
            pygame.display.flip()

        # Track FPS
        fps = fps_counter.tick()
        fps_samples.append(fps)

        if frame % 60 == 0:
            print(f"Frame {frame}/{frame_count} - FPS: {fps:.1f}")

    # Calculate FPS stats
    avg_fps = sum(fps_samples) / len(fps_samples)
    min_fps = min(fps_samples)
    max_fps = max(fps_samples)

    print(f"\n{'=' * 70}")
    print(f"RENDERING PERFORMANCE ({entity_count} entities)")
    print(f"{'=' * 70}")
    print(f"Average FPS: {avg_fps:.1f}")
    print(f"Min FPS: {min_fps:.1f}")
    print(f"Max FPS: {max_fps:.1f}")
    print(f"Target: 60 FPS")
    print(f"Status: {'✓ PASS' if avg_fps >= 60 else '✗ FAIL'}")
    print()

    profiler.print_report()

    pygame.quit()

    return {
        "entity_count": entity_count,
        "avg_fps": avg_fps,
        "min_fps": min_fps,
        "max_fps": max_fps,
        "metrics": profiler.get_all_metrics(),
    }


def profile_rendering_stress_test():
    """Run stress test with varying entity counts"""
    print("\n" + "=" * 70)
    print("RENDERING STRESS TEST")
    print("=" * 70)

    entity_counts = [100, 500, 1000, 2000, 5000]
    results = []

    for count in entity_counts:
        result = profile_rendering(count, frame_count=120, show_display=False)
        results.append(result)

    # Summary
    print("\n" + "=" * 70)
    print("STRESS TEST SUMMARY")
    print("=" * 70)
    print(f"{'Entities':<12} {'Avg FPS':<12} {'Min FPS':<12} {'Status':<12}")
    print("-" * 70)

    for result in results:
        status = "✓ PASS" if result["avg_fps"] >= 60 else "✗ FAIL"
        print(
            f"{result['entity_count']:<12} "
            f"{result['avg_fps']:<12.1f} "
            f"{result['min_fps']:<12.1f} "
            f"{status:<12}"
        )

    return results


if __name__ == "__main__":
    # Run basic test
    profile_rendering(entity_count=1000, frame_count=300, show_display=False)

    # Run stress test
    # profile_rendering_stress_test()
