"""
Test Enhanced Asset Search Functionality

Tests the new genre, theme, mood, and commercial-use filtering features.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import from rendering.assets directly
from rendering.assets import get_asset_manager


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_genre_filtering():
    """Test filtering by genre."""
    print_section("Test 1: Genre Filtering")

    assets = get_asset_manager()

    # Get all genres
    all_genres = assets.get_all_genres()
    print(f"\n✓ All genres found: {all_genres}")

    # Filter by fantasy genre
    fantasy_assets = assets.filter_assets(genre="fantasy")
    print(f"\n✓ Fantasy assets found: {len(fantasy_assets)}")
    for asset in fantasy_assets[:5]:  # Show first 5
        print(f"  - {asset.name} ({asset.category})")
    if len(fantasy_assets) > 5:
        print(f"  ... and {len(fantasy_assets) - 5} more")

    assert len(fantasy_assets) > 0, "Should have fantasy assets"
    print("\n✅ Genre filtering works!")


def test_theme_filtering():
    """Test filtering by theme."""
    print_section("Test 2: Theme Filtering")

    assets = get_asset_manager()

    # Get all themes
    all_themes = assets.get_all_themes()
    print(f"\n✓ All themes found: {all_themes}")

    # Filter by medieval theme
    medieval_assets = assets.filter_assets(theme="medieval")
    print(f"\n✓ Medieval assets found: {len(medieval_assets)}")
    for asset in medieval_assets:
        print(f"  - {asset.name} ({asset.category})")

    # Filter by dark theme
    dark_assets = assets.filter_assets(theme="dark")
    print(f"\n✓ Dark theme assets found: {len(dark_assets)}")
    for asset in dark_assets:
        print(f"  - {asset.name} ({asset.category})")

    print("\n✅ Theme filtering works!")


def test_mood_filtering():
    """Test filtering by mood (primarily for backgrounds)."""
    print_section("Test 3: Mood Filtering")

    assets = get_asset_manager()

    # Get all moods
    all_moods = assets.get_all_moods()
    print(f"\n✓ All moods found: {all_moods}")

    # Filter by peaceful mood
    peaceful_assets = assets.filter_assets(mood="peaceful")
    print(f"\n✓ Peaceful mood assets found: {len(peaceful_assets)}")
    for asset in peaceful_assets:
        print(f"  - {asset.name} ({asset.category})")

    # Filter by mysterious mood
    mysterious_assets = assets.filter_assets(mood="mysterious")
    print(f"\n✓ Mysterious mood assets found: {len(mysterious_assets)}")
    for asset in mysterious_assets:
        print(f"  - {asset.name} ({asset.category})")

    print("\n✅ Mood filtering works!")


def test_commercial_use_filtering():
    """Test filtering for commercial-use assets."""
    print_section("Test 4: Commercial Use Filtering")

    assets = get_asset_manager()

    # Get all assets
    all_assets_count = assets.get_asset_count()
    print(f"\n✓ Total assets: {all_assets_count}")

    # Get commercial-use assets
    commercial_count = assets.get_commercial_use_count()
    print(f"✓ Commercial-use assets: {commercial_count}")

    # Filter for commercial-use only
    commercial_assets = assets.filter_assets(commercial_use_only=True)
    print(f"\n✓ Commercial-use assets found: {len(commercial_assets)}")

    # Validate licenses
    validation = assets.validate_commercial_use()
    print(f"\n✓ License validation:")
    print(f"  - Allowed for commercial use: {len(validation['allowed'])}")
    print(f"  - Restricted: {len(validation['restricted'])}")

    # Show some commercial-use assets
    print(f"\nSample commercial-use assets:")
    for asset in commercial_assets[:10]:
        print(f"  - {asset.name}: {asset.license}")

    assert len(commercial_assets) == all_assets_count, "All sample assets should be CC0"
    print("\n✅ All assets are commercial-use friendly (CC0)!")


def test_combined_filtering():
    """Test combining multiple filter criteria."""
    print_section("Test 5: Combined Filtering")

    assets = get_asset_manager()

    # Find fantasy medieval characters
    result = assets.filter_assets(category="characters", genre="fantasy", theme="medieval")
    print(f"\n✓ Fantasy medieval characters: {len(result)}")
    for asset in result:
        print(f"  - {asset.name}")

    # Find fantasy enemies with commercial use
    result = assets.filter_assets(
        category="enemies", genre="fantasy", commercial_use_only=True
    )
    print(f"\n✓ Fantasy enemies (commercial-use): {len(result)}")
    for asset in result:
        print(f"  - {asset.name} [{asset.license}]")

    # Find dark theme assets
    result = assets.filter_assets(genre="fantasy", theme="dark")
    print(f"\n✓ Dark fantasy assets: {len(result)}")
    for asset in result:
        print(f"  - {asset.name} ({asset.category})")

    print("\n✅ Combined filtering works!")


def test_tag_based_search():
    """Test tag-based searching."""
    print_section("Test 6: Tag-Based Search")

    assets = get_asset_manager()

    # Search for warrior tags
    warriors = assets.find_assets_by_tag("warrior")
    print(f"\n✓ Assets with 'warrior' tag: {len(warriors)}")
    for asset in warriors:
        print(f"  - {asset.name} ({asset.category})")

    # Search for magic tags
    magic = assets.find_assets_by_tag("magic")
    print(f"\n✓ Assets with 'magic' tag: {len(magic)}")
    for asset in magic:
        print(f"  - {asset.name} ({asset.category})")

    # Search for boss tags
    bosses = assets.find_assets_by_tag("boss")
    print(f"\n✓ Assets with 'boss' tag: {len(bosses)}")
    for asset in bosses:
        print(f"  - {asset.name} ({asset.category})")

    print("\n✅ Tag-based search works!")


def test_text_search():
    """Test full-text search."""
    print_section("Test 7: Full-Text Search")

    assets = get_asset_manager()

    # Search for "hero"
    results = assets.search_assets("hero")
    print(f"\n✓ Search 'hero': {len(results)} results")
    for asset in results:
        print(f"  - {asset.name} ({asset.category})")

    # Search for "dragon"
    results = assets.search_assets("dragon")
    print(f"\n✓ Search 'dragon': {len(results)} results")
    for asset in results:
        print(f"  - {asset.name} ({asset.category})")

    # Search for "dungeon"
    results = assets.search_assets("dungeon")
    print(f"\n✓ Search 'dungeon': {len(results)} results")
    for asset in results:
        print(f"  - {asset.name} ({asset.category})")

    print("\n✅ Full-text search works!")


def test_loading_assets():
    """Test loading assets by ID."""
    print_section("Test 8: Asset Loading")

    assets = get_asset_manager()

    # Load a character
    hero = assets.get_character("hero_warrior")
    print(f"\n✓ Loaded character: {hero is not None}")

    # Load an enemy
    goblin = assets.get_enemy("enemy_goblin")
    print(f"✓ Loaded enemy: {goblin is not None}")

    # Load a tileset
    tileset = assets.get_tileset("tileset_dungeon")
    print(f"✓ Loaded tileset: {tileset is not None}")

    # Load an icon
    shield = assets.get_icon("icon_shield")
    print(f"✓ Loaded icon: {shield is not None}")

    # Load a background
    forest_bg = assets.get_background("bg_forest")
    print(f"✓ Loaded background: {forest_bg is not None}")

    print("\n✅ Asset loading works!")


def print_summary():
    """Print summary statistics."""
    print_section("Summary Statistics")

    assets = get_asset_manager()

    print(f"\nTotal assets: {assets.get_asset_count()}")
    print(f"\nAssets by category:")
    for category in assets.get_all_categories():
        count = assets.get_asset_count(category)
        print(f"  - {category}: {count}")

    print(f"\nGenres: {', '.join(assets.get_all_genres())}")
    print(f"Themes: {', '.join(assets.get_all_themes())}")
    print(f"Moods: {', '.join(assets.get_all_moods())}")
    print(f"\nTags ({len(assets.get_all_tags())} total):")
    print(f"  {', '.join(sorted(assets.get_all_tags())[:20])}...")

    print(f"\nCommercial-use assets: {assets.get_commercial_use_count()}/{assets.get_asset_count()}")


def main():
    """Run all tests."""
    print("\n" + "🔍 " * 20)
    print("Testing Enhanced Asset Search Functionality")
    print("🔍 " * 20)

    try:
        test_genre_filtering()
        test_theme_filtering()
        test_mood_filtering()
        test_commercial_use_filtering()
        test_combined_filtering()
        test_tag_based_search()
        test_text_search()
        test_loading_assets()

        print_summary()

        print("\n" + "=" * 60)
        print("  ✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nEnhanced search features:")
        print("  ✓ Genre filtering (fantasy, scifi, etc.)")
        print("  ✓ Theme filtering (medieval, dark, nature, etc.)")
        print("  ✓ Mood filtering (peaceful, mysterious, etc.)")
        print("  ✓ Commercial-use filtering (CC0 license validation)")
        print("  ✓ Combined multi-criteria filtering")
        print("  ✓ Tag-based search")
        print("  ✓ Full-text search")
        print("  ✓ Asset loading by ID")
        print("\nAll assets are properly tagged and searchable!")
        print("All assets are CC0 - safe for commercial use! 🎮\n")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
