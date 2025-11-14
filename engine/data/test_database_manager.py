"""
Test Database Manager
=====================

Comprehensive test suite for the database manager.

Run with: python -m pytest engine/data/test_database_manager.py
or: python engine/data/test_database_manager.py
"""

import tempfile
from pathlib import Path

from engine.data.database_manager import (
    DatabaseError,
    DatabaseManager,
    DuplicateIDError,
    EntryNotFoundError,
    ValidationError,
)
from engine.data.database_schema import (
    Effect,
    EffectType,
    Item,
    ItemType,
    Skill,
    SkillType,
    Weapon,
    WeaponType,
)


def test_crud_operations():
    """Test Create, Read, Update, Delete operations."""
    print("Testing CRUD operations...")

    manager = DatabaseManager()

    # CREATE
    potion = Item(
        id=1,
        name="Potion",
        icon_index=1,
        description="Restores 50 HP",
        price=50,
        effects=[Effect(effect_type=EffectType.RECOVER_HP, value1=50.0)],
    )

    created = manager.create("items", potion)
    assert created.id == 1
    assert created.name == "Potion"
    print("  ✓ Create works")

    # READ
    read_item = manager.read("items", 1)
    assert read_item.name == "Potion"
    print("  ✓ Read works")

    # READ ALL
    all_items = manager.read_all("items")
    assert len(all_items) == 1
    print("  ✓ Read all works")

    # UPDATE
    read_item.price = 75
    updated = manager.update("items", read_item)
    assert updated.price == 75
    print("  ✓ Update works")

    # DELETE
    deleted = manager.delete("items", 1)
    assert deleted.name == "Potion"
    assert manager.get_count("items") == 0
    print("  ✓ Delete works")

    # Test error cases
    try:
        manager.read("items", 999)
        assert False, "Should raise EntryNotFoundError"
    except EntryNotFoundError:
        print("  ✓ EntryNotFoundError raised correctly")

    print("✓ CRUD operations passed\n")


def test_auto_id():
    """Test automatic ID assignment."""
    print("Testing auto ID assignment...")

    manager = DatabaseManager()

    # Create with auto ID
    item1 = Item(name="Item 1", icon_index=1, description="Test")
    created1 = manager.create("items", item1, auto_id=True)
    assert created1.id == 1
    print(f"  ✓ Auto-assigned ID: {created1.id}")

    item2 = Item(name="Item 2", icon_index=2, description="Test")
    created2 = manager.create("items", item2, auto_id=True)
    assert created2.id == 2
    print(f"  ✓ Auto-assigned ID: {created2.id}")

    # Delete item 1 to create a gap
    manager.delete("items", 1)

    item3 = Item(name="Item 3", icon_index=3, description="Test")
    created3 = manager.create("items", item3, auto_id=True)
    assert created3.id == 1  # Should fill the gap
    print(f"  ✓ Gap filled with ID: {created3.id}")

    print("✓ Auto ID assignment passed\n")


def test_id_management():
    """Test ID management features."""
    print("Testing ID management...")

    manager = DatabaseManager()

    # Create items with gaps
    for i in [1, 2, 5, 7, 10]:
        item = Item(id=i, name=f"Item {i}", icon_index=i, description="Test")
        manager.create("items", item)

    # Find gaps
    gaps = manager.find_gaps("items", max_id=10)
    assert gaps == [3, 4, 6, 8, 9]
    print(f"  ✓ Found gaps: {gaps}")

    # Get next ID
    next_id = manager.get_next_id("items")
    assert next_id == 3  # First gap
    print(f"  ✓ Next ID: {next_id}")

    # Compact IDs
    id_mapping = manager.compact_ids("items")
    assert id_mapping == {1: 1, 2: 2, 5: 3, 7: 4, 10: 5}
    assert manager.get_count("items") == 5
    all_items = manager.read_all("items")
    assert [item.id for item in all_items] == [1, 2, 3, 4, 5]
    print(f"  ✓ IDs compacted: {id_mapping}")

    print("✓ ID management passed\n")


def test_search():
    """Test search functionality."""
    print("Testing search...")

    manager = DatabaseManager()

    # Create test data
    items = [
        Item(id=1, name="Potion", icon_index=1, description="Restores HP"),
        Item(id=2, name="Hi-Potion", icon_index=2, description="Restores more HP"),
        Item(id=3, name="Elixir", icon_index=3, description="Fully restores HP and MP"),
        Item(id=4, name="Antidote", icon_index=4, description="Cures poison"),
    ]

    for item in items:
        manager.create("items", item)

    # Search for "potion"
    results = manager.search("potion")
    assert len(results) == 2
    assert results[0].entry.name == "Potion"  # Exact match should rank higher
    print(f"  ✓ Found {len(results)} results for 'potion'")

    # Search for "restores"
    results = manager.search("restores")
    assert len(results) == 3
    print(f"  ✓ Found {len(results)} results for 'restores'")

    # Case-insensitive search
    results = manager.search("POTION", case_sensitive=False)
    assert len(results) == 2
    print(f"  ✓ Case-insensitive search works")

    print("✓ Search passed\n")


def test_filter():
    """Test filter functionality."""
    print("Testing filter...")

    manager = DatabaseManager()

    # Create test items with different prices
    for i in range(1, 6):
        item = Item(id=i, name=f"Item {i}", icon_index=i, description="Test", price=i * 100)
        manager.create("items", item)

    # Filter by price > 200
    expensive = manager.filter("items", lambda item: item.price > 200)
    assert len(expensive) == 3  # Items 3, 4, 5
    print(f"  ✓ Filter with lambda: {len(expensive)} items > 200 gold")

    # Filter by field
    very_expensive = manager.filter_by_field("items", "price", 300, operator="ge")
    assert len(very_expensive) == 3  # Items 3, 4, 5
    print(f"  ✓ Filter by field: {len(very_expensive)} items >= 300 gold")

    # Filter by name contains
    results = manager.filter_by_field("items", "name", "1", operator="contains")
    assert len(results) == 1
    print(f"  ✓ Filter contains: {len(results)} items with '1' in name")

    print("✓ Filter passed\n")


def test_batch_operations():
    """Test batch operations."""
    print("Testing batch operations...")

    manager = DatabaseManager()

    # Create test items
    for i in range(1, 4):
        item = Item(id=i, name=f"Item {i}", icon_index=i, description="Test", price=100)
        manager.create("items", item)

    # Duplicate
    duplicate = manager.duplicate("items", 1, new_name="Item 1 Duplicate")
    assert duplicate.id == 4
    assert duplicate.name == "Item 1 Duplicate"
    print(f"  ✓ Duplicated item: ID {duplicate.id}")

    # Bulk edit
    updated = manager.bulk_edit("items", [1, 2, 3], {"price": 200})
    assert len(updated) == 3
    assert all(item.price == 200 for item in updated)
    print(f"  ✓ Bulk edited {len(updated)} items")

    # Bulk delete
    deleted = manager.bulk_delete("items", [1, 2])
    assert len(deleted) == 2
    assert manager.get_count("items") == 2  # Only items 3 and 4 remain
    print(f"  ✓ Bulk deleted {len(deleted)} items")

    print("✓ Batch operations passed\n")


def test_json_serialization():
    """Test JSON save/load."""
    print("Testing JSON serialization...")

    manager = DatabaseManager()

    # Create test data
    item = Item(id=1, name="Potion", icon_index=1, description="Restores HP", price=50)
    skill = Skill(
        id=1,
        name="Fireball",
        icon_index=65,
        description="Fire magic",
        skill_type=SkillType.MAGIC,
        mp_cost=15,
    )

    manager.create("items", item)
    manager.create("skills", skill)

    # Save to file
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "test_db.json"

        manager.save_to_file(filepath)
        assert filepath.exists()
        print(f"  ✓ Saved to {filepath.name}")

        # Load from file
        manager2 = DatabaseManager()
        manager2.load_from_file(filepath)

        assert manager2.get_count("items") == 1
        assert manager2.get_count("skills") == 1

        loaded_item = manager2.read("items", 1)
        assert loaded_item.name == "Potion"
        print(f"  ✓ Loaded from {filepath.name}")

        # Test save category
        category_path = Path(tmpdir) / "items.json"
        manager.save_category_to_file("items", category_path)
        assert category_path.exists()
        print(f"  ✓ Saved category to {category_path.name}")

    print("✓ JSON serialization passed\n")


def test_csv_operations():
    """Test CSV import/export."""
    print("Testing CSV operations...")

    manager = DatabaseManager()

    # Create test data
    for i in range(1, 4):
        item = Item(
            id=i,
            name=f"Item {i}",
            icon_index=i,
            description=f"Description {i}",
            price=i * 100,
        )
        manager.create("items", item)

    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "items.csv"

        # Export to CSV with specific fields including price
        fields = ["id", "name", "icon_index", "description", "note", "price"]
        manager.export_to_csv("items", csv_path, fields=fields)
        assert csv_path.exists()
        print(f"  ✓ Exported to {csv_path.name}")

        # Clear and import
        manager.clear_category("items")
        assert manager.get_count("items") == 0

        created, updated, errors = manager.import_from_csv("items", csv_path)
        assert created == 3
        assert updated == 0
        assert len(errors) == 0
        print(f"  ✓ Imported {created} items from CSV")

        # Verify data
        item1 = manager.read("items", 1)
        assert item1.name == "Item 1"
        assert item1.price == 100
        print(f"  ✓ Data integrity verified")

    print("✓ CSV operations passed\n")


def test_validation():
    """Test data validation."""
    print("Testing validation...")

    manager = DatabaseManager()

    # Create valid item
    valid_item = Item(id=1, name="Valid Item", icon_index=1, description="Test", price=100)
    manager.create("items", valid_item)
    print("  ✓ Valid item created")

    # Try to create invalid item (invalid price)
    invalid_item = Item(
        id=2, name="Invalid", icon_index=1, description="Test", price=9999999
    )
    try:
        manager.create("items", invalid_item)
        assert False, "Should raise ValidationError"
    except ValidationError as e:
        print(f"  ✓ Validation error caught: {e}")

    # Validate all
    errors = manager.validate_all()
    assert len(errors) == 0
    print("  ✓ Validate all passed")

    # Validate category
    errors = manager.validate_category("items")
    assert len(errors) == 0
    print("  ✓ Validate category passed")

    print("✓ Validation passed\n")


def test_utility_methods():
    """Test utility methods."""
    print("Testing utility methods...")

    manager = DatabaseManager()

    # Create test data
    for i in range(1, 4):
        item = Item(id=i, name=f"Item {i}", icon_index=i, description="Test")
        manager.create("items", item)

    for i in range(1, 3):
        skill = Skill(id=i, name=f"Skill {i}", icon_index=i, description="Test")
        manager.create("skills", skill)

    # Get counts
    counts = manager.get_counts()
    assert counts["items"] == 3
    assert counts["skills"] == 2
    print(f"  ✓ Get counts: {counts['items']} items, {counts['skills']} skills")

    # Get categories
    categories = manager.get_categories()
    assert "items" in categories
    assert "skills" in categories
    print(f"  ✓ Categories: {len(categories)} total")

    # Exists
    assert manager.exists("items", 1) is True
    assert manager.exists("items", 999) is False
    print("  ✓ Exists check works")

    # Clear category
    manager.clear_category("items")
    assert manager.get_count("items") == 0
    assert manager.get_count("skills") == 2
    print("  ✓ Clear category works")

    # Clear all
    manager.clear()
    assert manager.get_count("skills") == 0
    print("  ✓ Clear all works")

    print("✓ Utility methods passed\n")


def test_performance():
    """Test performance with many entries."""
    print("Testing performance with large dataset...")

    import time

    manager = DatabaseManager()

    # Create 1000 items
    start = time.time()
    for i in range(1, 1001):
        item = Item(id=i, name=f"Item {i}", icon_index=i % 100, description=f"Test item {i}")
        manager.create("items", item)
    create_time = time.time() - start
    print(f"  ✓ Created 1000 items in {create_time:.3f}s")

    # Read all
    start = time.time()
    all_items = manager.read_all("items")
    read_time = time.time() - start
    assert len(all_items) == 1000
    print(f"  ✓ Read 1000 items in {read_time:.3f}s")

    # Search
    start = time.time()
    results = manager.search("Item 5")
    search_time = time.time() - start
    assert len(results) > 0
    print(f"  ✓ Searched 1000 items in {search_time:.3f}s ({len(results)} results)")

    # Filter
    start = time.time()
    filtered = manager.filter("items", lambda item: item.id % 10 == 0)
    filter_time = time.time() - start
    assert len(filtered) == 100
    print(f"  ✓ Filtered 1000 items in {filter_time:.3f}s ({len(filtered)} results)")

    print("✓ Performance test passed\n")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Database Manager Test Suite")
    print("=" * 60)
    print()

    tests = [
        test_crud_operations,
        test_auto_id,
        test_id_management,
        test_search,
        test_filter,
        test_batch_operations,
        test_json_serialization,
        test_csv_operations,
        test_validation,
        test_utility_methods,
        test_performance,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} FAILED: {e}\n")
            failed += 1
            import traceback

            traceback.print_exc()

    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
