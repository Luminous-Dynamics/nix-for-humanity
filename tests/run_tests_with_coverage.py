#!/usr/bin/env python3
"""
Run all tests with coverage reporting
"""

import os
import subprocess
import sys
from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
TESTS_DIR = PROJECT_ROOT / "tests"


def run_coverage():
    """Run tests with coverage"""

    print("🧪 Running tests with coverage...\n")

    # Set PYTHONPATH
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC_DIR)

    # Run coverage
    cmd = [
        "coverage",
        "run",
        "--source",
        str(SRC_DIR / "nix_for_humanity"),
        "--omit",
        "*/tests/*,*/__pycache__/*,*/venv/*",
        "-m",
        "unittest",
        "discover",
        "-s",
        str(TESTS_DIR / "unit"),
        "-p",
        "test_*.py",
    ]

    result = subprocess.run(cmd, env=env)

    if result.returncode == 0:
        print("\n✅ All tests passed!")

        # Generate coverage report
        print("\n📊 Coverage Report:\n")
        subprocess.run(["coverage", "report", "-m"])

        # Generate HTML report
        subprocess.run(["coverage", "html", "--directory", str(TESTS_DIR / "htmlcov")])
        print(f"\n📄 HTML report generated at: {TESTS_DIR / 'htmlcov' / 'index.html'}")

        # Generate XML report for CI/CD
        subprocess.run(["coverage", "xml", "-o", str(TESTS_DIR / "coverage.xml")])
        print(f"📄 XML report generated at: {TESTS_DIR / 'coverage.xml'}")

    else:
        print("\n❌ Some tests failed!")

    return result.returncode


if __name__ == "__main__":
    sys.exit(run_coverage())
