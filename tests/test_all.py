"""
Test orchestrator for running comprehensive test suites.

This module provides a programmatic way to run different test suites:
- Unit tests (default)
- Integration tests
- Performance benchmarks
- Stress tests
- Full test suite

Usage:
    python tests/test_all.py                    # Run unit tests only
    python tests/test_all.py --integration      # Run integration tests
    python tests/test_all.py --performance      # Run performance benchmarks
    python tests/test_all.py --stress           # Run stress tests
    python tests/test_all.py --full             # Run all tests
    python tests/test_all.py --coverage         # Run with coverage report

Or use pytest directly:
    pytest tests/ -v                            # All tests
    pytest tests/ -v -m integration             # Integration tests only
    pytest tests/ -v -m performance             # Performance tests only
    pytest tests/ -v -m stress                  # Stress tests only
    pytest tests/ --cov=. --cov-report=html     # With coverage
"""

import argparse
import subprocess
import sys
from pathlib import Path


class TestOrchestrator:
    """Orchestrates running different test suites."""

    def __init__(self):
        """Initialize the orchestrator."""
        self.tests_dir = Path(__file__).parent
        self.project_root = self.tests_dir.parent

    def run_unit_tests(self, verbose=True, coverage=False):
        """
        Run unit tests (excludes integration, performance, stress).

        Args:
            verbose: Show verbose output
            coverage: Generate coverage report

        Returns:
            int: Exit code
        """
        print("=" * 70)
        print("RUNNING UNIT TESTS")
        print("=" * 70)

        cmd = [
            "pytest",
            str(self.tests_dir),
            "-v" if verbose else "",
            "-m",
            "not integration and not performance and not stress",
            "--tb=short",
        ]

        if coverage:
            cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])

        cmd = [c for c in cmd if c]  # Remove empty strings

        return subprocess.call(cmd, cwd=self.project_root)

    def run_integration_tests(self, verbose=True):
        """
        Run integration tests.

        Args:
            verbose: Show verbose output

        Returns:
            int: Exit code
        """
        print("=" * 70)
        print("RUNNING INTEGRATION TESTS")
        print("=" * 70)

        cmd = [
            "pytest",
            str(self.tests_dir),
            "-v" if verbose else "",
            "-m",
            "integration",
            "--tb=short",
        ]

        cmd = [c for c in cmd if c]

        return subprocess.call(cmd, cwd=self.project_root)

    def run_performance_tests(self, verbose=True):
        """
        Run performance benchmarks.

        Args:
            verbose: Show verbose output

        Returns:
            int: Exit code
        """
        print("=" * 70)
        print("RUNNING PERFORMANCE BENCHMARKS")
        print("=" * 70)

        cmd = [
            "pytest",
            str(self.tests_dir),
            "-v" if verbose else "",
            "-m",
            "performance",
            "--tb=short",
            "-s",  # Show print output for performance metrics
        ]

        cmd = [c for c in cmd if c]

        return subprocess.call(cmd, cwd=self.project_root)

    def run_stress_tests(self, verbose=True):
        """
        Run stress tests.

        Args:
            verbose: Show verbose output

        Returns:
            int: Exit code
        """
        print("=" * 70)
        print("RUNNING STRESS TESTS")
        print("=" * 70)
        print("WARNING: Stress tests may take several minutes to complete.")
        print("=" * 70)

        cmd = [
            "pytest",
            str(self.tests_dir),
            "-v" if verbose else "",
            "-m",
            "stress",
            "--tb=short",
            "-s",  # Show print output for stress test metrics
        ]

        cmd = [c for c in cmd if c]

        return subprocess.call(cmd, cwd=self.project_root)

    def run_full_suite(self, verbose=True, coverage=False):
        """
        Run complete test suite (all tests).

        Args:
            verbose: Show verbose output
            coverage: Generate coverage report

        Returns:
            int: Exit code
        """
        print("=" * 70)
        print("RUNNING FULL TEST SUITE")
        print("=" * 70)
        print("This will run ALL tests including unit, integration, performance, and stress.")
        print("This may take 10+ minutes to complete.")
        print("=" * 70)

        cmd = [
            "pytest",
            str(self.tests_dir),
            "-v" if verbose else "",
            "--tb=short",
            "-s",  # Show print output
        ]

        if coverage:
            cmd.extend(
                [
                    "--cov=.",
                    "--cov-report=html",
                    "--cov-report=term",
                    "--cov-report=term-missing",
                ]
            )

        cmd = [c for c in cmd if c]

        return subprocess.call(cmd, cwd=self.project_root)

    def run_specific_file(self, test_file, verbose=True):
        """
        Run tests from a specific file.

        Args:
            test_file: Path to test file
            verbose: Show verbose output

        Returns:
            int: Exit code
        """
        print("=" * 70)
        print(f"RUNNING TESTS FROM: {test_file}")
        print("=" * 70)

        cmd = [
            "pytest",
            str(test_file),
            "-v" if verbose else "",
            "--tb=short",
            "-s",
        ]

        cmd = [c for c in cmd if c]

        return subprocess.call(cmd, cwd=self.project_root)

    def print_summary(self):
        """Print test suite summary."""
        print("\n" + "=" * 70)
        print("NEONWORKS TEST SUITE SUMMARY")
        print("=" * 70)
        print("\nAvailable test suites:")
        print("  1. Unit Tests         - Fast, isolated component tests")
        print("  2. Integration Tests  - Cross-feature workflow tests")
        print("  3. Performance Tests  - Benchmarks (2000 DB, 500x500 maps)")
        print("  4. Stress Tests       - Memory/CPU stress tests")
        print("  5. Full Suite         - All of the above")
        print("\nUsage:")
        print("  python tests/test_all.py                  # Unit tests")
        print("  python tests/test_all.py --integration    # Integration tests")
        print("  python tests/test_all.py --performance    # Performance tests")
        print("  python tests/test_all.py --stress         # Stress tests")
        print("  python tests/test_all.py --full           # All tests")
        print("  python tests/test_all.py --coverage       # Unit tests with coverage")
        print("\nDirect pytest usage:")
        print("  pytest tests/ -v                          # All tests")
        print("  pytest tests/test_ecs.py -v               # Specific file")
        print("  pytest tests/ -v -m integration           # Integration only")
        print("  pytest tests/ -v -m performance           # Performance only")
        print("  pytest tests/ -v -m stress                # Stress only")
        print("  pytest tests/ --cov=. --cov-report=html   # With coverage")
        print("=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="NeonWorks Test Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--integration",
        action="store_true",
        help="Run integration tests",
    )

    parser.add_argument(
        "--performance",
        action="store_true",
        help="Run performance benchmarks",
    )

    parser.add_argument(
        "--stress",
        action="store_true",
        help="Run stress tests",
    )

    parser.add_argument(
        "--full",
        action="store_true",
        help="Run full test suite (all tests)",
    )

    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report",
    )

    parser.add_argument(
        "--file",
        type=str,
        help="Run specific test file",
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Less verbose output",
    )

    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show test suite summary",
    )

    args = parser.parse_args()

    orchestrator = TestOrchestrator()

    # Show summary if requested
    if args.summary:
        orchestrator.print_summary()
        return 0

    # Determine which tests to run
    verbose = not args.quiet

    if args.file:
        # Run specific file
        exit_code = orchestrator.run_specific_file(args.file, verbose=verbose)
    elif args.full:
        # Run full suite
        exit_code = orchestrator.run_full_suite(verbose=verbose, coverage=args.coverage)
    elif args.integration:
        # Run integration tests
        exit_code = orchestrator.run_integration_tests(verbose=verbose)
    elif args.performance:
        # Run performance tests
        exit_code = orchestrator.run_performance_tests(verbose=verbose)
    elif args.stress:
        # Run stress tests
        exit_code = orchestrator.run_stress_tests(verbose=verbose)
    else:
        # Default: Run unit tests
        exit_code = orchestrator.run_unit_tests(verbose=verbose, coverage=args.coverage)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
