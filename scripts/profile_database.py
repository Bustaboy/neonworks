"""
Profile database operations

Tests database loading, querying, and saving performance.
Target: <1s database loads
"""

import json
import sys
import tempfile
import time
from pathlib import Path

# Add parent of parent directory to path so neonworks package can be found
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from neonworks.data.config_loader import ConfigLoader
from neonworks.utils.profiler import PerformanceProfiler


def create_test_database(size: str = "small") -> dict:
    """
    Create test database with various sizes.

    Args:
        size: 'small' (100 items), 'medium' (1000 items), 'large' (10000 items)
    """
    size_map = {"small": 100, "medium": 1000, "large": 10000}
    item_count = size_map.get(size, 100)

    database = {
        "metadata": {
            "name": f"Test Database ({size})",
            "version": "1.0.0",
            "item_count": item_count,
        },
        "items": [],
        "characters": [],
        "skills": [],
        "enemies": [],
    }

    # Create items
    for i in range(item_count):
        database["items"].append(
            {
                "id": f"item_{i}",
                "name": f"Test Item {i}",
                "description": f"This is test item number {i} with some data",
                "type": "consumable",
                "price": 100 + i,
                "effects": [
                    {"type": "restore_hp", "value": 50},
                    {"type": "restore_mp", "value": 25},
                ],
                "metadata": {
                    "rarity": "common",
                    "weight": 1.5,
                    "stackable": True,
                    "max_stack": 99,
                },
            }
        )

    # Create characters (fewer than items)
    for i in range(item_count // 10):
        database["characters"].append(
            {
                "id": f"char_{i}",
                "name": f"Character {i}",
                "level": i % 50 + 1,
                "stats": {
                    "hp": 100 + i * 10,
                    "mp": 50 + i * 5,
                    "attack": 10 + i * 2,
                    "defense": 8 + i * 2,
                    "magic": 12 + i * 2,
                    "speed": 15 + i,
                },
                "skills": [f"skill_{j}" for j in range(i % 10)],
                "equipment": {
                    "weapon": f"item_{i}",
                    "armor": f"item_{i+1}",
                    "accessory": f"item_{i+2}",
                },
            }
        )

    # Create skills
    for i in range(item_count // 5):
        database["skills"].append(
            {
                "id": f"skill_{i}",
                "name": f"Skill {i}",
                "description": f"Skill description {i}",
                "mp_cost": 10 + i,
                "power": 50 + i * 5,
                "element": ["fire", "ice", "lightning", "earth"][i % 4],
                "target": "single",
                "effects": [{"type": "damage", "element": "fire", "power": 100 + i}],
            }
        )

    # Create enemies
    for i in range(item_count // 5):
        database["enemies"].append(
            {
                "id": f"enemy_{i}",
                "name": f"Enemy {i}",
                "level": i % 30 + 1,
                "stats": {
                    "hp": 150 + i * 15,
                    "mp": 30 + i * 3,
                    "attack": 12 + i * 2,
                    "defense": 10 + i * 2,
                },
                "drops": [
                    {"item_id": f"item_{j}", "chance": 0.1} for j in range(i % 5)
                ],
            }
        )

    return database


def profile_database_load(database_path: Path, profiler: PerformanceProfiler):
    """Profile database loading"""
    with profiler.measure("database_load"):
        data = ConfigLoader.load_json(database_path)

    return data


def profile_database_query(data: dict, profiler: PerformanceProfiler):
    """Profile database queries"""
    # Query by ID
    with profiler.measure("query_by_id"):
        item = next((i for i in data["items"] if i["id"] == "item_500"), None)

    # Query by name
    with profiler.measure("query_by_name"):
        items = [i for i in data["items"] if "Test" in i["name"]]

    # Query by filter
    with profiler.measure("query_by_filter"):
        expensive_items = [i for i in data["items"] if i["price"] > 500]

    # Query with complex filter
    with profiler.measure("query_complex"):
        items = [
            i
            for i in data["items"]
            if i["type"] == "consumable" and i["price"] < 300
        ]


def profile_database_save(data: dict, database_path: Path, profiler: PerformanceProfiler):
    """Profile database saving"""
    with profiler.measure("database_save"):
        with open(database_path, "w") as f:
            json.dump(data, f, indent=2)


def profile_database_operations(size: str = "medium"):
    """
    Profile database operations.

    Args:
        size: Database size ('small', 'medium', 'large')
    """
    print(f"\nProfiling database operations ({size} database)...")

    profiler = PerformanceProfiler()

    # Create test database
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_database.json"

        # Create database
        print("Creating test database...")
        with profiler.measure("database_create"):
            database = create_test_database(size)

        # Save database
        print("Saving database...")
        with profiler.measure("database_initial_save"):
            with open(db_path, "w") as f:
                json.dump(database, f, indent=2)

        # Get file size
        file_size_mb = db_path.stat().st_size / (1024 * 1024)
        print(f"Database size: {file_size_mb:.2f} MB")

        # Profile loading (multiple times)
        print("Profiling database loads...")
        for i in range(5):
            data = profile_database_load(db_path, profiler)

        # Profile queries
        print("Profiling queries...")
        for i in range(10):
            profile_database_query(data, profiler)

        # Profile saving
        print("Profiling saves...")
        for i in range(5):
            profile_database_save(data, db_path, profiler)

    # Print results
    print(f"\n{'=' * 70}")
    print(f"DATABASE PERFORMANCE ({size.upper()} - {file_size_mb:.2f} MB)")
    print(f"{'=' * 70}")

    load_metric = profiler.get_metric("database_load")
    if load_metric:
        print(f"Load Time (avg): {load_metric.avg_time * 1000:.2f}ms")
        print(f"Load Time (max): {load_metric.max_time * 1000:.2f}ms")
        print(f"Target: <1000ms")
        print(f"Status: {'✓ PASS' if load_metric.avg_time < 1.0 else '✗ FAIL'}")

    print()
    profiler.print_report()

    return {
        "size": size,
        "file_size_mb": file_size_mb,
        "load_time": load_metric.avg_time if load_metric else 0,
        "metrics": profiler.get_all_metrics(),
    }


def profile_database_stress_test():
    """Run stress test with varying database sizes"""
    print("\n" + "=" * 70)
    print("DATABASE STRESS TEST")
    print("=" * 70)

    sizes = ["small", "medium", "large"]
    results = []

    for size in sizes:
        result = profile_database_operations(size)
        results.append(result)

    # Summary
    print("\n" + "=" * 70)
    print("STRESS TEST SUMMARY")
    print("=" * 70)
    print(f"{'Size':<12} {'File Size (MB)':<16} {'Load Time (ms)':<16} {'Status':<12}")
    print("-" * 70)

    for result in results:
        status = "✓ PASS" if result["load_time"] < 1.0 else "✗ FAIL"
        print(
            f"{result['size']:<12} "
            f"{result['file_size_mb']:<16.2f} "
            f"{result['load_time'] * 1000:<16.2f} "
            f"{status:<12}"
        )

    return results


if __name__ == "__main__":
    # Run basic test
    profile_database_operations("medium")

    # Run stress test
    # profile_database_stress_test()
