"""
Map Rendering Performance Benchmark

Benchmarks tilemap rendering performance with various map sizes.
Tests before and after optimization to measure improvements.
"""

import time
from typing import Dict, List

import pygame

from neonworks.rendering.assets import AssetManager
from neonworks.rendering.camera import Camera
from neonworks.rendering.tilemap import (
    Tilemap,
    TilemapRenderer,
    OptimizedTilemapRenderer,
    Tileset,
)


class MapRenderingBenchmark:
    """Benchmark tilemap rendering performance"""

    def __init__(
        self, screen_width: int = 1280, screen_height: int = 720, use_optimized: bool = False
    ):
        """Initialize benchmark"""
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Map Rendering Benchmark")

        self.asset_manager = AssetManager()

        # Choose renderer
        if use_optimized:
            self.renderer = OptimizedTilemapRenderer(self.asset_manager, enable_caching=True)
            self.renderer_name = "Optimized"
        else:
            self.renderer = TilemapRenderer(self.asset_manager)
            self.renderer_name = "Standard"

        self.camera = Camera(screen_width, screen_height, tile_size=32)

        # Results storage
        self.results: List[Dict] = []

    def create_test_tilemap(
        self, width: int, height: int, tile_size: int = 32, use_enhanced: bool = True
    ) -> Tilemap:
        """Create a test tilemap filled with random tiles"""
        tilemap = Tilemap(width, height, tile_size, tile_size, use_enhanced_layers=use_enhanced)

        # Create a simple test tileset
        tileset = Tileset(
            name="test_tileset",
            texture_path="test_tiles.png",
            tile_width=tile_size,
            tile_height=tile_size,
            columns=16,
            tile_count=256,
        )

        # Create test tiles (simple colored squares)
        for tile_id in range(256):
            tile_surface = pygame.Surface((tile_size, tile_size))
            # Create different colors based on tile_id
            r = (tile_id * 7) % 256
            g = (tile_id * 13) % 256
            b = (tile_id * 19) % 256
            tile_surface.fill((r, g, b))
            tileset.tiles[tile_id] = tile_surface

        tilemap.add_tileset(tileset)

        # Create layers and fill with test data
        if use_enhanced:
            layer_id = tilemap.create_enhanced_layer("Ground")
            layer = tilemap.get_enhanced_layer(layer_id)
            if layer:
                # Fill with varied tiles
                for y in range(height):
                    for x in range(width):
                        tile_id = ((x + y) * 7) % 256
                        if tile_id == 0:
                            tile_id = 1  # Avoid empty tiles
                        layer.set_tile(x, y, tile_id)

            # Add more layers for realistic testing
            layer_id2 = tilemap.create_enhanced_layer("Objects")
            layer2 = tilemap.get_enhanced_layer(layer_id2)
            if layer2:
                for y in range(0, height, 3):
                    for x in range(0, width, 3):
                        tile_id = ((x * 3 + y * 5) % 128) + 128
                        layer2.set_tile(x, y, tile_id)

        return tilemap

    def benchmark_render(
        self, tilemap: Tilemap, num_frames: int = 300, move_camera: bool = True
    ) -> Dict:
        """
        Benchmark rendering performance.

        Args:
            tilemap: Tilemap to render
            num_frames: Number of frames to render
            move_camera: Whether to move camera during test

        Returns:
            Dictionary with benchmark results
        """
        frame_times = []
        tiles_rendered_list = []
        tiles_culled_list = []
        chunks_rendered_list = []
        cache_hits_list = []
        cache_misses_list = []

        # Center camera initially
        self.camera.x = (tilemap.width * tilemap.tile_width) / 2
        self.camera.y = (tilemap.height * tilemap.tile_height) / 2

        clock = pygame.time.Clock()
        start_time = time.time()

        for frame in range(num_frames):
            frame_start = time.time()

            # Move camera in a pattern
            if move_camera:
                angle = (frame / num_frames) * 2 * 3.14159
                offset = 100
                self.camera.x += offset * 0.01
                self.camera.y += offset * 0.005

            # Clear screen
            self.screen.fill((0, 0, 0))

            # Render tilemap
            self.renderer.render(self.screen, tilemap, self.camera)

            # Update display
            pygame.display.flip()

            # Record stats
            frame_time = time.time() - frame_start
            frame_times.append(frame_time)

            stats = self.renderer.get_stats()
            tiles_rendered_list.append(stats["tiles_rendered"])
            tiles_culled_list.append(stats["tiles_culled"])

            # Collect optimized renderer stats
            if "chunks_rendered" in stats:
                chunks_rendered_list.append(stats["chunks_rendered"])
                cache_hits_list.append(stats["cache_hits"])
                cache_misses_list.append(stats["cache_misses"])

            # Handle events to prevent freezing
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    break

            clock.tick()  # No limit for benchmarking

        total_time = time.time() - start_time

        # Calculate statistics
        avg_frame_time = sum(frame_times) / len(frame_times)
        avg_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
        min_frame_time = min(frame_times)
        max_frame_time = max(frame_times)
        max_fps = 1.0 / min_frame_time if min_frame_time > 0 else 0
        min_fps = 1.0 / max_frame_time if max_frame_time > 0 else 0

        avg_tiles_rendered = sum(tiles_rendered_list) / len(tiles_rendered_list)
        avg_tiles_culled = sum(tiles_culled_list) / len(tiles_culled_list)

        result = {
            "map_size": f"{tilemap.width}x{tilemap.height}",
            "total_tiles": tilemap.width * tilemap.height,
            "num_frames": num_frames,
            "total_time": total_time,
            "avg_frame_time_ms": avg_frame_time * 1000,
            "avg_fps": avg_fps,
            "min_fps": min_fps,
            "max_fps": max_fps,
            "avg_tiles_rendered": avg_tiles_rendered,
            "avg_tiles_culled": avg_tiles_culled,
            "tiles_per_frame": avg_tiles_rendered + avg_tiles_culled,
        }

        # Add optimized renderer stats
        if chunks_rendered_list:
            avg_chunks = sum(chunks_rendered_list) / len(chunks_rendered_list)
            total_cache_hits = sum(cache_hits_list)
            total_cache_misses = sum(cache_misses_list)
            total_cache_ops = total_cache_hits + total_cache_misses
            cache_hit_rate = (
                (total_cache_hits / total_cache_ops * 100) if total_cache_ops > 0 else 0
            )

            result["avg_chunks_rendered"] = avg_chunks
            result["cache_hit_rate"] = cache_hit_rate

        return result

    def run_benchmark_suite(self):
        """Run full benchmark suite with various map sizes"""
        print("=" * 80)
        print("MAP RENDERING PERFORMANCE BENCHMARK")
        print("=" * 80)
        print()

        # Test configurations
        test_configs = [
            {"width": 50, "height": 50, "name": "Small (50x50)"},
            {"width": 100, "height": 100, "name": "Medium (100x100)"},
            {"width": 200, "height": 200, "name": "Large (200x200)"},
            {"width": 500, "height": 500, "name": "Very Large (500x500)"},
        ]

        for config in test_configs:
            print(f"\nTesting {config['name']}...")
            print("-" * 80)

            # Create tilemap
            tilemap = self.create_test_tilemap(config["width"], config["height"])

            # Run benchmark
            results = self.benchmark_render(tilemap, num_frames=300, move_camera=True)

            # Store results
            results["config_name"] = config["name"]
            self.results.append(results)

            # Print results
            self.print_results(results)

        # Print summary
        print("\n" + "=" * 80)
        print("BENCHMARK SUMMARY")
        print("=" * 80)
        self.print_summary()

    def print_results(self, results: Dict):
        """Print benchmark results"""
        print(f"Renderer:           {self.renderer_name}")
        print(f"Map Size:           {results['map_size']} ({results['total_tiles']:,} tiles)")
        print(f"Frames Rendered:    {results['num_frames']}")
        print(f"Total Time:         {results['total_time']:.2f}s")
        print(f"Avg Frame Time:     {results['avg_frame_time_ms']:.2f}ms")
        print(f"Avg FPS:            {results['avg_fps']:.1f}")
        print(f"Min FPS:            {results['min_fps']:.1f}")
        print(f"Max FPS:            {results['max_fps']:.1f}")
        print(f"Avg Tiles Rendered: {results['avg_tiles_rendered']:.0f}")
        print(f"Avg Tiles Culled:   {results['avg_tiles_culled']:.0f}")

        # Print chunk stats if using optimized renderer
        if "avg_chunks_rendered" in results:
            print(f"Avg Chunks Rendered:{results['avg_chunks_rendered']:.0f}")
            print(f"Cache Hit Rate:     {results['cache_hit_rate']:.1f}%")

        # Performance assessment
        if results["avg_fps"] >= 60:
            status = "✓ EXCELLENT (60+ FPS)"
        elif results["avg_fps"] >= 30:
            status = "⚠ ACCEPTABLE (30-60 FPS)"
        else:
            status = "✗ POOR (<30 FPS)"

        print(f"Performance:        {status}")

    def print_summary(self):
        """Print summary table"""
        print()
        print(f"{'Map Size':<20} {'Avg FPS':<12} {'Min FPS':<12} {'Status':<20}")
        print("-" * 80)

        for result in self.results:
            status = "✓ OK" if result["avg_fps"] >= 60 else "✗ NEEDS OPTIMIZATION"
            print(
                f"{result['config_name']:<20} "
                f"{result['avg_fps']:>8.1f}    "
                f"{result['min_fps']:>8.1f}    "
                f"{status}"
            )

    def save_results(self, filename: str = "benchmark_results.txt"):
        """Save results to file"""
        with open(filename, "w") as f:
            f.write("MAP RENDERING BENCHMARK RESULTS\n")
            f.write("=" * 80 + "\n\n")

            for result in self.results:
                f.write(f"Configuration: {result['config_name']}\n")
                f.write(f"Map Size: {result['map_size']}\n")
                f.write(f"Avg FPS: {result['avg_fps']:.1f}\n")
                f.write(f"Min FPS: {result['min_fps']:.1f}\n")
                f.write(f"Max FPS: {result['max_fps']:.1f}\n")
                f.write(f"Avg Frame Time: {result['avg_frame_time_ms']:.2f}ms\n")
                f.write(f"Avg Tiles Rendered: {result['avg_tiles_rendered']:.0f}\n")
                f.write("\n")

        print(f"\nResults saved to {filename}")


def main():
    """Run the benchmark comparison"""
    print("\n" + "=" * 80)
    print("MAP RENDERING OPTIMIZATION BENCHMARK")
    print("Comparing Standard vs Optimized Renderer")
    print("=" * 80)

    # Run standard renderer benchmark
    print("\n\n### RUNNING STANDARD RENDERER BENCHMARK ###\n")
    standard_benchmark = MapRenderingBenchmark(use_optimized=False)
    try:
        standard_benchmark.run_benchmark_suite()
        standard_benchmark.save_results("benchmark_standard.txt")
    except KeyboardInterrupt:
        print("\n\nBenchmark interrupted by user")
    finally:
        pygame.quit()

    # Reinitialize pygame for second benchmark
    time.sleep(1)

    # Run optimized renderer benchmark
    print("\n\n### RUNNING OPTIMIZED RENDERER BENCHMARK ###\n")
    optimized_benchmark = MapRenderingBenchmark(use_optimized=True)
    try:
        optimized_benchmark.run_benchmark_suite()
        optimized_benchmark.save_results("benchmark_optimized.txt")
    except KeyboardInterrupt:
        print("\n\nBenchmark interrupted by user")
    finally:
        pygame.quit()

    # Compare results
    print("\n\n" + "=" * 80)
    print("PERFORMANCE COMPARISON")
    print("=" * 80)
    print()
    print(f"{'Map Size':<20} {'Standard FPS':<15} {'Optimized FPS':<15} {'Improvement':<15}")
    print("-" * 80)

    for std_result, opt_result in zip(standard_benchmark.results, optimized_benchmark.results):
        std_fps = std_result["avg_fps"]
        opt_fps = opt_result["avg_fps"]
        improvement = ((opt_fps - std_fps) / std_fps * 100) if std_fps > 0 else 0

        print(
            f"{std_result['config_name']:<20} "
            f"{std_fps:>10.1f}      "
            f"{opt_fps:>10.1f}      "
            f"{improvement:>10.1f}%"
        )

    # Save comparison
    with open("benchmark_comparison.txt", "w") as f:
        f.write("MAP RENDERING PERFORMANCE COMPARISON\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"{'Map Size':<20} {'Standard FPS':<15} {'Optimized FPS':<15} {'Improvement':<15}\n")
        f.write("-" * 80 + "\n")

        for std_result, opt_result in zip(standard_benchmark.results, optimized_benchmark.results):
            std_fps = std_result["avg_fps"]
            opt_fps = opt_result["avg_fps"]
            improvement = ((opt_fps - std_fps) / std_fps * 100) if std_fps > 0 else 0

            f.write(
                f"{std_result['config_name']:<20} "
                f"{std_fps:>10.1f}      "
                f"{opt_fps:>10.1f}      "
                f"{improvement:>10.1f}%\n"
            )

    print("\nComparison saved to benchmark_comparison.txt")


if __name__ == "__main__":
    main()
