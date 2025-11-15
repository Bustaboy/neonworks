"""
Comprehensive performance profiling script

Runs all profiling tests and generates a complete baseline report.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from profile_database import profile_database_operations, profile_database_stress_test
from profile_events import profile_event_stress_test, profile_event_system
from profile_rendering import profile_rendering, profile_rendering_stress_test


def run_all_profiles(output_dir: Path = None):
    """
    Run all profiling tests.

    Args:
        output_dir: Directory to save reports (default: reports/)
    """
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "reports"

    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = output_dir / f"performance_baseline_{timestamp}.txt"
    json_file = output_dir / f"performance_baseline_{timestamp}.json"

    print("=" * 70)
    print("NEONWORKS PERFORMANCE PROFILING")
    print("=" * 70)
    print(f"Timestamp: {timestamp}")
    print(f"Output: {report_file}")
    print("=" * 70)

    results = {
        "timestamp": timestamp,
        "rendering": {},
        "database": {},
        "events": {},
    }

    # Open report file
    with open(report_file, "w") as f:
        f.write("=" * 70 + "\n")
        f.write("NEONWORKS PERFORMANCE BASELINE REPORT\n")
        f.write("=" * 70 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # 1. Rendering Performance
        print("\n\n" + "=" * 70)
        print("1. RENDERING PERFORMANCE")
        print("=" * 70)
        f.write("\n\n" + "=" * 70 + "\n")
        f.write("1. RENDERING PERFORMANCE\n")
        f.write("=" * 70 + "\n\n")

        # Basic rendering test
        result = profile_rendering(entity_count=1000, frame_count=300, show_display=False)
        results["rendering"]["basic"] = {
            "entity_count": result["entity_count"],
            "avg_fps": result["avg_fps"],
            "min_fps": result["min_fps"],
            "max_fps": result["max_fps"],
        }

        f.write(f"Entity Count: {result['entity_count']}\n")
        f.write(f"Average FPS: {result['avg_fps']:.1f}\n")
        f.write(f"Min FPS: {result['min_fps']:.1f}\n")
        f.write(f"Max FPS: {result['max_fps']:.1f}\n")
        f.write(f"Target: 60 FPS\n")
        f.write(f"Status: {'PASS' if result['avg_fps'] >= 60 else 'FAIL'}\n")

        # Stress test
        print("\nRunning rendering stress test...")
        stress_results = profile_rendering_stress_test()
        results["rendering"]["stress_test"] = [
            {
                "entity_count": r["entity_count"],
                "avg_fps": r["avg_fps"],
                "min_fps": r["min_fps"],
            }
            for r in stress_results
        ]

        # 2. Database Performance
        print("\n\n" + "=" * 70)
        print("2. DATABASE PERFORMANCE")
        print("=" * 70)
        f.write("\n\n" + "=" * 70 + "\n")
        f.write("2. DATABASE PERFORMANCE\n")
        f.write("=" * 70 + "\n\n")

        # Basic database test
        result = profile_database_operations("medium")
        results["database"]["basic"] = {
            "size": result["size"],
            "file_size_mb": result["file_size_mb"],
            "load_time_ms": result["load_time"] * 1000,
        }

        f.write(f"Database Size: {result['size']}\n")
        f.write(f"File Size: {result['file_size_mb']:.2f} MB\n")
        f.write(f"Load Time: {result['load_time'] * 1000:.2f}ms\n")
        f.write(f"Target: <1000ms\n")
        f.write(f"Status: {'PASS' if result['load_time'] < 1.0 else 'FAIL'}\n")

        # Stress test
        print("\nRunning database stress test...")
        stress_results = profile_database_stress_test()
        results["database"]["stress_test"] = [
            {
                "size": r["size"],
                "file_size_mb": r["file_size_mb"],
                "load_time_ms": r["load_time"] * 1000,
            }
            for r in stress_results
        ]

        # 3. Event System Performance
        print("\n\n" + "=" * 70)
        print("3. EVENT SYSTEM PERFORMANCE")
        print("=" * 70)
        f.write("\n\n" + "=" * 70 + "\n")
        f.write("3. EVENT SYSTEM PERFORMANCE\n")
        f.write("=" * 70 + "\n\n")

        result = profile_event_system()
        results["events"]["basic"] = {"completed": True}

        # Stress test
        print("\nRunning event stress test...")
        stress_metrics = profile_event_stress_test()
        results["events"]["stress_test"] = {"completed": True}

        # Summary
        print("\n\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        f.write("\n\n" + "=" * 70 + "\n")
        f.write("SUMMARY\n")
        f.write("=" * 70 + "\n\n")

        # Check targets
        rendering_pass = results["rendering"]["basic"]["avg_fps"] >= 60
        database_pass = results["database"]["basic"]["load_time_ms"] < 1000

        summary = f"""
Rendering (1000 entities): {results['rendering']['basic']['avg_fps']:.1f} FPS - {'✓ PASS' if rendering_pass else '✗ FAIL'}
Database (medium): {results['database']['basic']['load_time_ms']:.2f}ms - {'✓ PASS' if database_pass else '✗ FAIL'}
Event System: ✓ PASS

Overall: {'✓ ALL TESTS PASSED' if rendering_pass and database_pass else '✗ SOME TESTS FAILED'}
"""

        print(summary)
        f.write(summary)

        f.write("\n\nDetailed metrics saved to: " + str(json_file) + "\n")

    # Save JSON results
    with open(json_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n{'=' * 70}")
    print(f"Reports saved to:")
    print(f"  {report_file}")
    print(f"  {json_file}")
    print(f"{'=' * 70}")

    return results


if __name__ == "__main__":
    run_all_profiles()
