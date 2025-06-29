#!/usr/bin/env python3
"""
Test runner script for karaoke-lyrics-processor

This script runs the full test suite with coverage reporting.
"""

import subprocess
import sys
import os


def run_tests():
    """Run the test suite with coverage reporting"""
    print("🎵 Running Karaoke Lyrics Processor Test Suite 🎵")
    print("=" * 50)

    # Ensure we're in the project root
    if not os.path.exists("pyproject.toml"):
        print("Error: Please run this script from the project root directory")
        sys.exit(1)

    # Run pytest with coverage
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "--cov=karaoke_lyrics_processor",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-fail-under=90",
        "-v",
        "tests/",
    ]

    print(f"Running command: {' '.join(cmd)}")
    print("-" * 50)

    try:
        result = subprocess.run(cmd, check=True)
        print("\n" + "=" * 50)
        print("✅ All tests passed with 90%+ coverage!")
        print("📊 HTML coverage report generated in htmlcov/index.html")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with return code {e.returncode}")
        return e.returncode


def run_specific_test(test_name):
    """Run a specific test file or test function"""
    cmd = [sys.executable, "-m", "pytest", "-v", test_name]

    print(f"Running specific test: {test_name}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)

    return subprocess.run(cmd).returncode


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test
        exit_code = run_specific_test(sys.argv[1])
    else:
        # Run full test suite
        exit_code = run_tests()

    sys.exit(exit_code)
