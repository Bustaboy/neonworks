#!/usr/bin/env python3
"""
Database Performance Test Script
=================================

Tests database performance with 100+ items across all categories.
Measures:
- Load time
- Query performance (CRUD operations)
- Search/filter performance
- Serialization/deserialization time
- Memory usage (basic)

Usage:
    python scripts/test_database_performance.py
"""

import sys
import time
from pathlib import Path
from typing import Dict, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.data.database_manager import DatabaseManager
from engine.data.database_schema import Item, ItemType


class PerformanceTester:
    """Tests database performance."""

    def __init__(self, db_path: Path):
        """
        Initialize the performance tester.

        Args:
            db_path: Path to database file
        """
        self.db_path = db_path
        self.db = DatabaseManager()
        self.results: Dict[str, float] = {}

    def run_all_tests(self):
        """Run all performance tests."""
        print("\n" + "=" * 70)
        print(" DATABASE PERFORMANCE TESTS")
        print("=" * 70 + "\n")

        self.test_load_performance()
        self.test_create_performance()
        self.test_read_performance()
        self.test_update_performance()
        self.test_search_performance()
        self.test_filter_performance()
        self.test_save_performance()

        self.print_results()

    def test_load_performance(self):
        """Test database loading performance."""
        print("Test 1: Load Performance")
        print("-" * 70)

        start = time.time()
        self.db.load_from_file(self.db_path)
        elapsed = time.time() - start

        self.results["load_time"] = elapsed

        # Count entries
        counts = self.db.get_counts()
        total = sum(counts.values())

        print(f"  Loaded {total} entries across {len(counts)} categories")
        print(f"  Time: {elapsed:.4f} seconds")
        print(f"  Rate: {total/elapsed:.0f} entries/second")
        print(f"  Categories: {', '.join(f'{k}={v}' for k, v in counts.items())}")
        print()

    def test_create_performance(self):
        """Test create operation performance."""
        print("Test 2: Create Performance")
        print("-" * 70)

        # Create 100 temporary items
        items_to_create = 100
        start = time.time()

        for i in range(items_to_create):
            item = Item(
                id=5000 + i,
                name=f"Perf Test Item {i}",
                description="Performance test",
                price=10,
                item_type=ItemType.REGULAR,
            )
            self.db.create("items", item)

        elapsed = time.time() - start
        self.results["create_time"] = elapsed

        print(f"  Created {items_to_create} items")
        print(f"  Time: {elapsed:.4f} seconds")
        print(f"  Rate: {items_to_create/elapsed:.0f} items/second")
        print(f"  Average: {elapsed/items_to_create*1000:.2f} ms/item")
        print()

    def test_read_performance(self):
        """Test read operation performance."""
        print("Test 3: Read Performance")
        print("-" * 70)

        # Read 1000 random items
        item_ids = list(self.db.items.keys())
        reads = min(1000, len(item_ids) * 10)  # Read each item ~10 times

        start = time.time()
        for i in range(reads):
            item_id = item_ids[i % len(item_ids)]
            self.db.read("items", item_id)

        elapsed = time.time() - start
        self.results["read_time"] = elapsed

        print(f"  Performed {reads} reads")
        print(f"  Time: {elapsed:.4f} seconds")
        print(f"  Rate: {reads/elapsed:.0f} reads/second")
        print(f"  Average: {elapsed/reads*1000:.2f} ms/read")
        print()

    def test_update_performance(self):
        """Test update operation performance."""
        print("Test 4: Update Performance")
        print("-" * 70)

        # Update 100 items
        item_ids = list(self.db.items.keys())[:100]
        updates = len(item_ids)

        start = time.time()
        for item_id in item_ids:
            item = self.db.read("items", item_id)
            item.price += 10  # Modify price
            self.db.update("items", item)

        elapsed = time.time() - start
        self.results["update_time"] = elapsed

        print(f"  Updated {updates} items")
        print(f"  Time: {elapsed:.4f} seconds")
        print(f"  Rate: {updates/elapsed:.0f} updates/second")
        print(f"  Average: {elapsed/updates*1000:.2f} ms/update")
        print()

    def test_search_performance(self):
        """Test search operation performance."""
        print("Test 5: Search Performance")
        print("-" * 70)

        # Search for items matching "Sample"
        start = time.time()
        results = self.db.search("items", "Sample")
        elapsed = time.time() - start

        self.results["search_time"] = elapsed

        print(f"  Searched {len(self.db.items)} items for 'Sample'")
        print(f"  Found: {len(results)} matches")
        print(f"  Time: {elapsed:.4f} seconds")
        print(f"  Rate: {len(self.db.items)/elapsed:.0f} items/second")
        print()

    def test_filter_performance(self):
        """Test filter operation performance."""
        print("Test 6: Filter Performance")
        print("-" * 70)

        # Filter items by price > 500
        start = time.time()
        results = self.db.filter("items", lambda item: item.price > 500)
        elapsed = time.time() - start

        self.results["filter_time"] = elapsed

        print(f"  Filtered {len(self.db.items)} items (price > 500)")
        print(f"  Found: {len(results)} matches")
        print(f"  Time: {elapsed:.4f} seconds")
        print(f"  Rate: {len(self.db.items)/elapsed:.0f} items/second")
        print()

    def test_save_performance(self):
        """Test save operation performance."""
        print("Test 7: Save Performance")
        print("-" * 70)

        temp_path = Path("/tmp/perf_test_db.json")

        start = time.time()
        self.db.save_to_file(temp_path)
        elapsed = time.time() - start

        self.results["save_time"] = elapsed

        # Get file size
        file_size = temp_path.stat().st_size
        file_size_mb = file_size / (1024 * 1024)

        print(f"  Saved {sum(self.db.get_counts().values())} entries")
        print(f"  File size: {file_size_mb:.2f} MB ({file_size:,} bytes)")
        print(f"  Time: {elapsed:.4f} seconds")
        print(f"  Rate: {file_size_mb/elapsed:.2f} MB/second")

        # Clean up
        temp_path.unlink()
        print()

    def print_results(self):
        """Print summary of all results."""
        print("\n" + "=" * 70)
        print(" PERFORMANCE SUMMARY")
        print("=" * 70 + "\n")

        # Calculate total entries
        total_entries = sum(self.db.get_counts().values())

        print(f"Database Size: {total_entries} total entries")
        print()

        # Print timing results
        print("Operation Timings:")
        print(f"  Load:   {self.results.get('load_time', 0):.4f} seconds")
        print(f"  Create: {self.results.get('create_time', 0):.4f} seconds")
        print(f"  Read:   {self.results.get('read_time', 0):.4f} seconds")
        print(f"  Update: {self.results.get('update_time', 0):.4f} seconds")
        print(f"  Search: {self.results.get('search_time', 0):.4f} seconds")
        print(f"  Filter: {self.results.get('filter_time', 0):.4f} seconds")
        print(f"  Save:   {self.results.get('save_time', 0):.4f} seconds")
        print()

        # Performance assessment
        total_time = sum(self.results.values())
        print(f"Total Test Time: {total_time:.4f} seconds")
        print()

        # Determine performance grade
        if self.results.get("read_time", float("inf")) < 0.001:
            read_grade = "EXCELLENT"
        elif self.results.get("read_time", float("inf")) < 0.01:
            read_grade = "GOOD"
        else:
            read_grade = "OK"

        if self.results.get("search_time", float("inf")) < 0.1:
            search_grade = "EXCELLENT"
        elif self.results.get("search_time", float("inf")) < 0.5:
            search_grade = "GOOD"
        else:
            search_grade = "OK"

        print(f"Performance Grades:")
        print(f"  Read operations: {read_grade}")
        print(f"  Search operations: {search_grade}")
        print()
        print("=" * 70)
        print()


def main():
    """Main entry point."""
    # Check if integrated database exists
    db_path = Path("data/integrated_database.json")

    if not db_path.exists():
        print(f"Error: Database not found at {db_path}")
        print("Please run the integration script first:")
        print("  python scripts/database_integration.py --all")
        return 1

    # Run tests
    tester = PerformanceTester(db_path)
    tester.run_all_tests()

    return 0


if __name__ == "__main__":
    sys.exit(main())
