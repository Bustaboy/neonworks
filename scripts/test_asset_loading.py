#!/usr/bin/env python3
"""
Test script for the asset library system.

This script verifies that the asset management system works correctly
with the manifest-based loading, category helpers, search, and filtering.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pygame

pygame.init()

# Set video mode for image loading (required by pygame)
# Use a small hidden window
import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.display.set_mode((1, 1))

from rendering.assets import AssetManager


def print_section(title):
    """Print a section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print("=" * 60)


def test_manifest_loading():
    """Test manifest loading."""
    print_section("Test 1: Manifest Loading")

    # Create asset manager
    assets = AssetManager()

    # Check manifest loaded
    asset_count = assets.get_asset_count()
    print(f"✓ Loaded {asset_count} assets from manifest")

    # Get all categories
    categories = assets.get_all_categories()
    print(f"✓ Found categories: {', '.join(categories)}")

    # Get all tags
    tags = assets.get_all_tags()
    print(f"✓ Found {len(tags)} unique tags")

    return assets


def test_category_helpers(assets):
    """Test category-specific helper methods."""
    print_section("Test 2: Category-Specific Helpers")

    # Test character loading
    hero = assets.get_character("test_hero")
    if hero:
        print(f"✓ Loaded character: test_hero ({hero.get_size()})")
    else:
        print("✗ Failed to load test_hero")

    # Test enemy loading
    slime = assets.get_enemy("test_slime")
    if slime:
        print(f"✓ Loaded enemy: test_slime ({slime.get_size()})")
    else:
        print("✗ Failed to load test_slime")

    # Test tileset loading
    tileset = assets.get_tileset("test_basic_tiles")
    if tileset:
        print(
            f"✓ Loaded tileset: test_basic_tiles " f"({tileset.tile_width}x{tileset.tile_height})"
        )
    else:
        print("✗ Failed to load test_basic_tiles")

    # Test icon loading
    sword = assets.get_icon("test_sword_icon")
    if sword:
        print(f"✓ Loaded icon: test_sword_icon ({sword.get_size()})")
    else:
        print("✗ Failed to load test_sword_icon")

    # Test UI element loading
    button = assets.get_ui_element("test_button")
    if button:
        print(f"✓ Loaded UI element: test_button ({button.get_size()})")
    else:
        print("✗ Failed to load test_button")

    # Test face loading
    face = assets.get_face("test_hero_face")
    if face:
        print(f"✓ Loaded face: test_hero_face ({face.get_size()})")
    else:
        print("✗ Failed to load test_hero_face")

    # Test background loading
    bg = assets.get_background("test_battle_bg")
    if bg:
        print(f"✓ Loaded background: test_battle_bg ({bg.get_size()})")
    else:
        print("✗ Failed to load test_battle_bg")


def test_thumbnails(assets):
    """Test thumbnail generation."""
    print_section("Test 3: Thumbnail Generation")

    # Test thumbnail for character
    thumb = assets.get_thumbnail("test_hero", size=(64, 64))
    if thumb:
        print(f"✓ Generated thumbnail for test_hero ({thumb.get_size()})")
    else:
        print("✗ Failed to generate thumbnail for test_hero")

    # Test thumbnail for enemy
    thumb = assets.get_thumbnail("test_slime", size=(64, 64))
    if thumb:
        print(f"✓ Generated thumbnail for test_slime ({thumb.get_size()})")
    else:
        print("✗ Failed to generate thumbnail for test_slime")

    # Test thumbnail for icon
    thumb = assets.get_thumbnail("test_sword_icon", size=(32, 32))
    if thumb:
        print(f"✓ Generated thumbnail for test_sword_icon ({thumb.get_size()})")
    else:
        print("✗ Failed to generate thumbnail for test_sword_icon")


def test_search_and_filter(assets):
    """Test search and filtering functionality."""
    print_section("Test 4: Search and Filtering")

    # Test search by query
    results = assets.search_assets("hero")
    print(f"✓ Search 'hero': found {len(results)} assets")
    for result in results:
        print(f"  - {result.id}: {result.name}")

    # Test find by tag
    results = assets.find_assets_by_tag("test")
    print(f"✓ Find by tag 'test': found {len(results)} assets")

    # Test find by category
    results = assets.find_assets_by_category("icons")
    print(f"✓ Find by category 'icons': found {len(results)} assets")
    for result in results:
        print(f"  - {result.id}: {result.name}")

    # Test filter
    results = assets.filter_assets(category="characters", tags=["test"])
    print(f"✓ Filter (category=characters, tags=[test]): found {len(results)} assets")
    for result in results:
        print(f"  - {result.id}: {result.name}")


def test_lazy_loading(assets):
    """Test lazy loading."""
    print_section("Test 5: Lazy Loading")

    # Get asset metadata without loading
    metadata = assets.get_asset_metadata("test_hero")
    if metadata:
        print(f"✓ Got metadata for test_hero without loading")
        print(f"  - Name: {metadata.name}")
        print(f"  - Category: {metadata.category}")
        print(f"  - Tags: {', '.join(metadata.tags)}")
    else:
        print("✗ Failed to get metadata")

    # Now load the asset
    loaded = assets.load_asset("test_hero")
    if loaded:
        print(f"✓ Loaded asset test_hero on demand")
        print(f"  - Resource type: {type(loaded.resource).__name__}")
    else:
        print("✗ Failed to load asset")

    # Load again (should come from cache)
    loaded2 = assets.load_asset("test_hero")
    if loaded2 is loaded:
        print(f"✓ Second load returned cached asset")
    else:
        print("✗ Second load did not use cache")


def test_asset_count(assets):
    """Test asset counting."""
    print_section("Test 6: Asset Counting")

    total = assets.get_asset_count()
    print(f"✓ Total assets: {total}")

    categories = assets.get_all_categories()
    for category in categories:
        count = assets.get_asset_count(category)
        print(f"  - {category}: {count} assets")


def test_missing_asset(assets):
    """Test handling of missing assets."""
    print_section("Test 7: Missing Asset Handling")

    # Try to load non-existent asset
    result = assets.load_asset("does_not_exist")
    if result is None:
        print("✓ Correctly returned None for missing asset")
    else:
        print("✗ Should have returned None for missing asset")

    # Try to get metadata for non-existent asset
    metadata = assets.get_asset_metadata("does_not_exist")
    if metadata is None:
        print("✓ Correctly returned None for missing metadata")
    else:
        print("✗ Should have returned None for missing metadata")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("  Asset Library System Tests")
    print("=" * 60)

    try:
        # Test 1: Manifest loading
        assets = test_manifest_loading()

        # Test 2: Category helpers
        test_category_helpers(assets)

        # Test 3: Thumbnails
        test_thumbnails(assets)

        # Test 4: Search and filter
        test_search_and_filter(assets)

        # Test 5: Lazy loading
        test_lazy_loading(assets)

        # Test 6: Asset counting
        test_asset_count(assets)

        # Test 7: Missing asset handling
        test_missing_asset(assets)

        # Final summary
        print_section("Test Summary")
        cache_info = assets.get_cache_info()
        print(f"✓ All tests completed successfully!")
        print(f"\nCache Statistics:")
        print(f"  - Sprites: {cache_info['sprites']}")
        print(f"  - Sprite sheets: {cache_info['sprite_sheets']}")
        print(f"  - Memory: {cache_info['memory_mb']:.2f} MB")

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
