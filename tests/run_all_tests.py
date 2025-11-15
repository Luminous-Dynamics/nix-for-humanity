#!/usr/bin/env python3
"""
Comprehensive test runner for Luminous Nix
Runs unit tests, integration tests, and generates coverage reports
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
TESTS_DIR = PROJECT_ROOT / "tests"

# ANSI color codes
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_header(text):
    """Print a formatted header"""
    print(f"\n{BOLD}{BLUE}{'=' * 60}{RESET}")
    print(f"{BOLD}{BLUE}{text.center(60)}{RESET}")
    print(f"{BOLD}{BLUE}{'=' * 60}{RESET}\n")


def print_success(text):
    """Print success message"""
    print(f"{GREEN}✅ {text}{RESET}")


def print_error(text):
    """Print error message"""
    print(f"{RED}❌ {text}{RESET}")


def print_info(text):
    """Print info message"""
    print(f"{YELLOW}ℹ️  {text}{RESET}")


def run_unit_tests(verbose=False, failfast=False):
    """Run unit tests"""
    print_header("Running Unit Tests")

    cmd = [
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        str(TESTS_DIR / "unit"),
        "-p",
        "test_*.py",
    ]

    if verbose:
        cmd.append("-v")
    if failfast:
        cmd.append("--failfast")

    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC_DIR)

    result = subprocess.run(cmd, env=env)

    if result.returncode == 0:
        print_success("All unit tests passed!")
    else:
        print_error("Some unit tests failed!")

    return result.returncode


def run_integration_tests(verbose=False):
    """Run integration tests"""
    print_header("Running Integration Tests")

    integration_dir = TESTS_DIR / "integration"
    if not integration_dir.exists():
        print_info("No integration tests found (this is OK for now)")
        return 0

    cmd = [
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        str(integration_dir),
        "-p",
        "test_*.py",
    ]

    if verbose:
        cmd.append("-v")

    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC_DIR)

    result = subprocess.run(cmd, env=env)

    if result.returncode == 0:
        print_success("All integration tests passed!")
    else:
        print_error("Some integration tests failed!")

    return result.returncode


def run_e2e_tests(verbose=False):
    """Run end-to-end tests"""
    print_header("Running End-to-End Tests")

    e2e_dir = TESTS_DIR / "e2e"
    if not e2e_dir.exists():
        print_info("No E2E tests found (this is OK for now)")
        return 0

    cmd = [
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        str(e2e_dir),
        "-p",
        "test_*.py",
    ]

    if verbose:
        cmd.append("-v")

    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC_DIR)

    result = subprocess.run(cmd, env=env)

    if result.returncode == 0:
        print_success("All E2E tests passed!")
    else:
        print_error("Some E2E tests failed!")

    return result.returncode


def run_coverage(html=False, xml=False, min_coverage=95):
    """Run tests with coverage"""
    print_header("Running Tests with Coverage")

    # Check if coverage is available
    try:
        subprocess.run(["coverage", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("Coverage tool not found. Install with: pip install coverage")
        return 1

    # Run coverage for all test types
    cmd = [
        "coverage",
        "run",
        "--source",
        str(SRC_DIR / "luminous_nix"),
        "--omit",
        "*/tests/*,*/__pycache__/*,*/venv/*,*/tui/*",
        "-m",
        "unittest",
        "discover",
        "-s",
        str(TESTS_DIR),
        "-p",
        "test_*.py",
    ]

    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC_DIR)

    print_info("Running tests with coverage...")
    result = subprocess.run(cmd, env=env, capture_output=True, text=True)

    if result.returncode != 0:
        print_error("Tests failed during coverage run")
        print(result.stdout)
        print(result.stderr)
        return result.returncode

    # Generate coverage report
    print_info("Generating coverage report...")

    # Text report
    report_result = subprocess.run(
        ["coverage", "report", "-m"], capture_output=True, text=True
    )

    print(report_result.stdout)

    # Extract coverage percentage
    coverage_line = report_result.stdout.strip().split("\n")[-1]
    if "TOTAL" in coverage_line:
        coverage_percent = int(coverage_line.split()[-1].rstrip("%"))

        if coverage_percent >= min_coverage:
            print_success(f"Coverage is {coverage_percent}% (minimum: {min_coverage}%)")
        else:
            print_error(f"Coverage is {coverage_percent}% (minimum: {min_coverage}%)")

    # HTML report
    if html:
        print_info("Generating HTML coverage report...")
        subprocess.run(["coverage", "html", "--directory", str(TESTS_DIR / "htmlcov")])
        print_success(
            f"HTML report generated at: {TESTS_DIR / 'htmlcov' / 'index.html'}"
        )

    # XML report
    if xml:
        print_info("Generating XML coverage report...")
        subprocess.run(["coverage", "xml", "-o", str(TESTS_DIR / "coverage.xml")])
        print_success(f"XML report generated at: {TESTS_DIR / 'coverage.xml'}")

    # JSON report for programmatic access
    subprocess.run(["coverage", "json", "-o", str(TESTS_DIR / "coverage.json")])

    # Check if we meet minimum coverage
    with open(TESTS_DIR / "coverage.json") as f:
        coverage_data = json.load(f)
        total_coverage = coverage_data["totals"]["percent_covered"]

    return 0 if total_coverage >= min_coverage else 1


def run_linters(fix=False):
    """Run code quality checks"""
    print_header("Running Code Quality Checks")

    # Check for tools
    tools = {
        "black": "Code formatter",
        "isort": "Import sorter",
        "flake8": "Linter",
        "mypy": "Type checker",
    }

    available_tools = []
    for tool, description in tools.items():
        try:
            subprocess.run([tool, "--version"], capture_output=True, check=True)
            available_tools.append(tool)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print_info(f"{tool} ({description}) not found - skipping")

    if not available_tools:
        print_info(
            "No linting tools found. Install with: pip install black isort flake8 mypy"
        )
        return 0

    # Run available tools
    exit_code = 0

    if "black" in available_tools:
        print_info("Running black...")
        cmd = ["black", str(SRC_DIR), str(TESTS_DIR)]
        if not fix:
            cmd.append("--check")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            exit_code = 1

    if "isort" in available_tools:
        print_info("Running isort...")
        cmd = ["isort", str(SRC_DIR), str(TESTS_DIR)]
        if not fix:
            cmd.extend(["--check", "--diff"])
        result = subprocess.run(cmd)
        if result.returncode != 0:
            exit_code = 1

    if "flake8" in available_tools:
        print_info("Running flake8...")
        result = subprocess.run(["flake8", str(SRC_DIR), str(TESTS_DIR)])
        if result.returncode != 0:
            exit_code = 1

    if "mypy" in available_tools:
        print_info("Running mypy...")
        result = subprocess.run(["mypy", str(SRC_DIR)])
        if result.returncode != 0:
            exit_code = 1

    if exit_code == 0:
        print_success("All code quality checks passed!")
    else:
        print_error("Some code quality checks failed!")

    return exit_code


def run_benchmarks():
    """Run performance benchmarks"""
    print_header("Running Performance Benchmarks")

    benchmark_file = TESTS_DIR / "benchmarks" / "run_benchmarks.py"
    if not benchmark_file.exists():
        print_info("No benchmarks found (this is OK for now)")
        return 0

    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC_DIR)

    result = subprocess.run([sys.executable, str(benchmark_file)], env=env)

    if result.returncode == 0:
        print_success("All benchmarks completed!")
    else:
        print_error("Some benchmarks failed!")

    return result.returncode


def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(
        description="Comprehensive test runner for Luminous Nix"
    )

    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument(
        "--integration", action="store_true", help="Run only integration tests"
    )
    parser.add_argument("--e2e", action="store_true", help="Run only end-to-end tests")
    parser.add_argument(
        "--coverage", action="store_true", help="Run tests with coverage report"
    )
    parser.add_argument(
        "--html", action="store_true", help="Generate HTML coverage report"
    )
    parser.add_argument(
        "--xml", action="store_true", help="Generate XML coverage report"
    )
    parser.add_argument("--lint", action="store_true", help="Run code quality checks")
    parser.add_argument(
        "--fix", action="store_true", help="Fix code style issues automatically"
    )
    parser.add_argument(
        "--benchmark", action="store_true", help="Run performance benchmarks"
    )
    parser.add_argument(
        "--min-coverage",
        type=int,
        default=95,
        help="Minimum coverage percentage required (default: 95)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "--failfast", action="store_true", help="Stop on first test failure"
    )

    args = parser.parse_args()

    # Track overall exit code
    exit_code = 0

    # Print main header
    print_header("Luminous Nix Test Suite")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Source directory: {SRC_DIR}")
    print(f"Tests directory: {TESTS_DIR}")

    start_time = time.time()

    # Determine what to run
    run_all = not any(
        [
            args.unit,
            args.integration,
            args.e2e,
            args.coverage,
            args.lint,
            args.benchmark,
        ]
    )

    # Run tests
    if run_all or args.unit:
        result = run_unit_tests(verbose=args.verbose, failfast=args.failfast)
        exit_code = max(exit_code, result)

    if run_all or args.integration:
        result = run_integration_tests(verbose=args.verbose)
        exit_code = max(exit_code, result)

    if run_all or args.e2e:
        result = run_e2e_tests(verbose=args.verbose)
        exit_code = max(exit_code, result)

    if run_all or args.coverage:
        result = run_coverage(
            html=args.html, xml=args.xml, min_coverage=args.min_coverage
        )
        exit_code = max(exit_code, result)

    if args.lint:
        result = run_linters(fix=args.fix)
        exit_code = max(exit_code, result)

    if args.benchmark:
        result = run_benchmarks()
        exit_code = max(exit_code, result)

    # Summary
    elapsed_time = time.time() - start_time
    print_header("Test Summary")

    if exit_code == 0:
        print_success(f"All tests passed! (Time: {elapsed_time:.2f}s)")
    else:
        print_error(f"Some tests failed! (Time: {elapsed_time:.2f}s)")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
