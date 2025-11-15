"""
Tests for OptimizedTilemapRenderer

Tests chunk-based rendering, caching, and performance optimizations.
"""

import pytest

try:
    import pygame

    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

from neonworks.rendering.assets import AssetManager
from neonworks.rendering.camera import Camera
from neonworks.rendering.tilemap import (
    OptimizedTilemapRenderer,
    Tilemap,
    TilemapBuilder,
    Tileset,
)


@pytest.fixture
def asset_manager():
    """Create asset manager for tests"""
    return AssetManager()


@pytest.fixture
def renderer(asset_manager):
    """Create optimized renderer"""
    return OptimizedTilemapRenderer(asset_manager, enable_caching=True)


@pytest.fixture
def tilemap():
    """Create a test tilemap"""
    tilemap = TilemapBuilder.create_simple_tilemap(100, 100, tile_size=32, use_enhanced=True)

    # Create a test tileset
    tileset = Tileset(
        name="test_tileset",
        texture_path="test_tiles.png",
        tile_width=32,
        tile_height=32,
        columns=16,
        tile_count=256,
    )

    # Create test tiles
    if PYGAME_AVAILABLE:
        pygame.init()
        for tile_id in range(256):
            tile_surface = pygame.Surface((32, 32))
            r = (tile_id * 7) % 256
            g = (tile_id * 13) % 256
            b = (tile_id * 19) % 256
            tile_surface.fill((r, g, b))
            tileset.tiles[tile_id] = tile_surface

    tilemap.add_tileset(tileset)

    # Fill with test data
    layer_id = tilemap.create_enhanced_layer("Test Layer")
    layer = tilemap.get_enhanced_layer(layer_id)
    if layer:
        for y in range(100):
            for x in range(100):
                tile_id = ((x + y) * 7) % 256
                if tile_id == 0:
                    tile_id = 1
                layer.set_tile(x, y, tile_id)

    return tilemap


@pytest.fixture
def camera():
    """Create a camera"""
    return Camera(1280, 720, tile_size=32)


class TestOptimizedRendererInitialization:
    """Test renderer initialization"""

    def test_create_optimized_renderer(self, asset_manager):
        """Test creating optimized renderer"""
        renderer = OptimizedTilemapRenderer(asset_manager, enable_caching=True)

        assert renderer is not None
        assert renderer.enable_caching is True
        assert len(renderer._chunk_cache) == 0
        assert len(renderer._dirty_chunks) == 0
        assert len(renderer._atlas_cache) == 0

    def test_create_optimized_renderer_without_caching(self, asset_manager):
        """Test creating renderer with caching disabled"""
        renderer = OptimizedTilemapRenderer(asset_manager, enable_caching=False)

        assert renderer.enable_caching is False

    def test_stats_initialization(self, renderer):
        """Test that stats are properly initialized"""
        stats = renderer.get_stats()

        assert "tiles_rendered" in stats
        assert "tiles_culled" in stats
        assert "layers_rendered" in stats
        assert "chunks_rendered" in stats
        assert "chunks_cached" in stats
        assert "chunks_reused" in stats
        assert "cache_hits" in stats
        assert "cache_misses" in stats


class TestChunkInvalidation:
    """Test chunk invalidation and dirty tracking"""

    def test_invalidate_chunk(self, renderer):
        """Test invalidating a single chunk"""
        # Add a fake chunk to cache
        chunk_key = ("layer_1", 0, 0)
        if PYGAME_AVAILABLE:
            renderer._chunk_cache[chunk_key] = pygame.Surface((512, 512))

        # Invalidate it
        renderer.invalidate_chunk("layer_1", 0, 0)

        assert chunk_key not in renderer._chunk_cache
        assert chunk_key in renderer._dirty_chunks

    def test_invalidate_tile(self, renderer):
        """Test invalidating a tile (which invalidates its chunk)"""
        # Tile at (16, 16) should be in chunk (1, 1) with CHUNK_SIZE=16
        renderer.invalidate_tile("layer_1", 16, 16)

        expected_chunk = ("layer_1", 1, 1)
        assert expected_chunk in renderer._dirty_chunks

    def test_invalidate_layer(self, renderer):
        """Test invalidating all chunks in a layer"""
        # Add multiple chunks to cache
        if PYGAME_AVAILABLE:
            for x in range(3):
                for y in range(3):
                    chunk_key = ("layer_1", x, y)
                    renderer._chunk_cache[chunk_key] = pygame.Surface((512, 512))

        # Invalidate entire layer
        renderer.invalidate_layer("layer_1")

        # All chunks for layer_1 should be removed
        layer_chunks = [key for key in renderer._chunk_cache if key[0] == "layer_1"]
        assert len(layer_chunks) == 0

    def test_clear_cache(self, renderer):
        """Test clearing all caches"""
        if PYGAME_AVAILABLE:
            # Add data to caches
            renderer._chunk_cache[("layer_1", 0, 0)] = pygame.Surface((512, 512))
            renderer._dirty_chunks.add(("layer_1", 1, 1))
            renderer._atlas_cache["test"] = pygame.Surface((1024, 1024))

            # Clear everything
            renderer.clear_cache()

            assert len(renderer._chunk_cache) == 0
            assert len(renderer._dirty_chunks) == 0
            assert len(renderer._atlas_cache) == 0


@pytest.mark.skipif(not PYGAME_AVAILABLE, reason="Pygame not available")
class TestRendering:
    """Test rendering functionality"""

    def test_render_basic(self, renderer, tilemap, camera):
        """Test basic rendering without errors"""
        screen = pygame.Surface((1280, 720))

        # Should not raise any errors
        renderer.render(screen, tilemap, camera)

        # Check stats were updated
        stats = renderer.get_stats()
        assert stats["layers_rendered"] > 0

    def test_chunk_caching(self, renderer, tilemap, camera):
        """Test that chunks are cached on first render"""
        screen = pygame.Surface((1280, 720))

        # First render - should create cache entries
        renderer.render(screen, tilemap, camera)

        stats1 = renderer.get_stats()
        cache_size_after_first = len(renderer._chunk_cache)

        # Second render - should reuse cached chunks
        renderer.render(screen, tilemap, camera)

        stats2 = renderer.get_stats()

        # Cache should have entries
        assert cache_size_after_first > 0

        # Second render should have cache hits
        assert stats2["cache_hits"] > 0
        assert stats2["chunks_reused"] > 0

    def test_render_with_camera_movement(self, renderer, tilemap, camera):
        """Test rendering with camera movement"""
        screen = pygame.Surface((1280, 720))

        # Render at initial position
        renderer.render(screen, tilemap, camera)
        chunks_first = len(renderer._chunk_cache)

        # Move camera
        camera.x += 500
        camera.y += 500

        # Render again
        renderer.render(screen, tilemap, camera)
        chunks_second = len(renderer._chunk_cache)

        # Should have rendered more chunks as camera moved
        assert chunks_second >= chunks_first

    def test_render_large_map(self, renderer, asset_manager, camera):
        """Test rendering a large 500x500 map"""
        # Create large tilemap
        large_tilemap = TilemapBuilder.create_simple_tilemap(
            500, 500, tile_size=32, use_enhanced=True
        )

        # Create tileset
        tileset = Tileset(
            name="large_test",
            texture_path="test.png",
            tile_width=32,
            tile_height=32,
            columns=16,
            tile_count=256,
        )

        # Create tiles
        for tile_id in range(256):
            tile_surface = pygame.Surface((32, 32))
            tile_surface.fill((tile_id % 256, (tile_id * 2) % 256, (tile_id * 3) % 256))
            tileset.tiles[tile_id] = tile_surface

        large_tilemap.add_tileset(tileset)

        # Fill with data
        layer_id = large_tilemap.create_enhanced_layer("Ground")
        layer = large_tilemap.get_enhanced_layer(layer_id)
        if layer:
            for y in range(0, 500, 10):  # Sparse fill for speed
                for x in range(0, 500, 10):
                    layer.set_tile(x, y, ((x + y) % 128) + 1)

        screen = pygame.Surface((1280, 720))

        # Should render without errors
        renderer.render(screen, large_tilemap, camera)

        stats = renderer.get_stats()

        # Should render only visible chunks, not all 500x500 tiles
        assert stats["tiles_rendered"] < 500 * 500
        assert stats["chunks_rendered"] > 0

    def test_empty_chunks_not_cached(self, renderer, asset_manager, camera):
        """Test that empty chunks are not cached"""
        # Create tilemap with sparse data
        sparse_tilemap = TilemapBuilder.create_simple_tilemap(
            100, 100, tile_size=32, use_enhanced=True
        )

        # Create tileset
        tileset = Tileset(
            name="sparse_test",
            texture_path="test.png",
            tile_width=32,
            tile_height=32,
            columns=16,
            tile_count=256,
        )

        for tile_id in range(256):
            tile_surface = pygame.Surface((32, 32))
            tile_surface.fill((tile_id, tile_id, tile_id))
            tileset.tiles[tile_id] = tile_surface

        sparse_tilemap.add_tileset(tileset)

        # Fill only small area
        layer_id = sparse_tilemap.create_enhanced_layer("Sparse")
        layer = sparse_tilemap.get_enhanced_layer(layer_id)
        if layer:
            for y in range(5, 10):
                for x in range(5, 10):
                    layer.set_tile(x, y, 1)

        screen = pygame.Surface((1280, 720))

        # Render
        renderer.render(screen, sparse_tilemap, camera)

        # Cache should only contain non-empty chunks
        assert len(renderer._chunk_cache) < 100  # Much less than all possible chunks


class TestPerformanceFeatures:
    """Test performance optimization features"""

    def test_chunk_size_configuration(self, renderer):
        """Test that chunk size is configurable"""
        assert renderer.CHUNK_SIZE == 16

    @pytest.mark.skipif(not PYGAME_AVAILABLE, reason="Pygame not available")
    def test_texture_atlas_creation(self, renderer, tilemap):
        """Test texture atlas is created"""
        screen = pygame.Surface((1280, 720))
        camera = Camera(1280, 720, tile_size=32)

        # Render to trigger atlas creation
        renderer.render(screen, tilemap, camera)

        # Atlas should be created
        tileset = tilemap.get_tileset()
        if tileset:
            assert tileset.name in renderer._atlas_cache

    @pytest.mark.skipif(not PYGAME_AVAILABLE, reason="Pygame not available")
    def test_frustum_culling(self, renderer, tilemap, camera):
        """Test that frustum culling works"""
        screen = pygame.Surface((1280, 720))

        # Position camera in corner
        camera.x = 500
        camera.y = 500

        renderer.render(screen, tilemap, camera)

        stats = renderer.get_stats()

        # Should cull many tiles (100x100 map, only small portion visible)
        assert stats["tiles_culled"] > 0
        assert stats["tiles_rendered"] < 10000  # Less than total map


class TestStatistics:
    """Test statistics tracking"""

    @pytest.mark.skipif(not PYGAME_AVAILABLE, reason="Pygame not available")
    def test_stats_reset_each_frame(self, renderer, tilemap, camera):
        """Test that stats are reset each frame"""
        screen = pygame.Surface((1280, 720))

        # Render twice
        renderer.render(screen, tilemap, camera)
        stats1 = renderer.get_stats()

        renderer.render(screen, tilemap, camera)
        stats2 = renderer.get_stats()

        # Stats should be for current frame, not cumulative
        assert stats2["layers_rendered"] == stats1["layers_rendered"]

    @pytest.mark.skipif(not PYGAME_AVAILABLE, reason="Pygame not available")
    def test_cache_hit_tracking(self, renderer, tilemap, camera):
        """Test cache hit/miss tracking"""
        screen = pygame.Surface((1280, 720))

        # First render - all misses
        renderer.render(screen, tilemap, camera)
        stats1 = renderer.get_stats()

        assert stats1["cache_misses"] > 0
        assert stats1["cache_hits"] == 0

        # Second render - should have hits
        renderer.render(screen, tilemap, camera)
        stats2 = renderer.get_stats()

        assert stats2["cache_hits"] > 0


class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.mark.skipif(not PYGAME_AVAILABLE, reason="Pygame not available")
    def test_render_with_no_tileset(self, renderer, camera):
        """Test rendering tilemap with no tileset"""
        screen = pygame.Surface((1280, 720))
        tilemap = TilemapBuilder.create_simple_tilemap(10, 10, use_enhanced=True)

        # Should not crash, just return early
        renderer.render(screen, tilemap, camera)

    @pytest.mark.skipif(not PYGAME_AVAILABLE, reason="Pygame not available")
    def test_render_with_invisible_layer(self, renderer, tilemap, camera):
        """Test rendering with invisible layers"""
        screen = pygame.Surface((1280, 720))

        # Make all layers invisible
        for layer_id in tilemap.layer_manager.get_render_order():
            layer = tilemap.layer_manager.get_layer(layer_id)
            if layer:
                layer.properties.visible = False

        renderer.render(screen, tilemap, camera)

        stats = renderer.get_stats()
        assert stats["layers_rendered"] == 0

    @pytest.mark.skipif(not PYGAME_AVAILABLE, reason="Pygame not available")
    def test_render_at_map_boundary(self, renderer, tilemap, camera):
        """Test rendering at map boundaries"""
        screen = pygame.Surface((1280, 720))

        # Position camera at map edge
        camera.x = 0
        camera.y = 0

        renderer.render(screen, tilemap, camera)

        # Should not crash
        stats = renderer.get_stats()
        assert stats["chunks_rendered"] > 0


class TestCachingDisabled:
    """Test renderer with caching disabled"""

    @pytest.mark.skipif(not PYGAME_AVAILABLE, reason="Pygame not available")
    def test_no_caching_when_disabled(self, asset_manager, tilemap, camera):
        """Test that caching doesn't occur when disabled"""
        renderer = OptimizedTilemapRenderer(asset_manager, enable_caching=False)
        screen = pygame.Surface((1280, 720))

        # Render twice
        renderer.render(screen, tilemap, camera)
        renderer.render(screen, tilemap, camera)

        # Cache should be empty
        assert len(renderer._chunk_cache) == 0

        stats = renderer.get_stats()
        assert stats["cache_hits"] == 0
        assert stats["chunks_cached"] == 0
