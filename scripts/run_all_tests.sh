#!/bin/bash
# Run all tests and generate a comprehensive report

echo "=========================================="
echo "LUMINOUS NIX - COMPREHENSIVE TEST REPORT"
echo "=========================================="
echo ""
echo "Date: $(date)"
echo "Testing Sprint: Day 3/4"
echo ""

# Run tests with coverage
echo "Running test suite with coverage..."
poetry run python -m pytest tests/unit/ -v --tb=short --cov=nix_humanity --cov-report=term-missing 2>&1 | tee test_results.txt

# Extract summary
echo ""
echo "=========================================="
echo "TEST SUMMARY"
echo "=========================================="
grep -E "(passed|failed|error)" test_results.txt | tail -1

echo ""
echo "=========================================="
echo "COVERAGE SUMMARY"
echo "=========================================="
grep -E "TOTAL|nix_humanity" test_results.txt | grep "%"

echo ""
echo "=========================================="
echo "FAILED TESTS (if any)"
echo "=========================================="
grep -E "FAILED tests" test_results.txt || echo "No failed tests!"

echo ""
echo "=========================================="
echo "NEXT STEPS"
echo "=========================================="
echo "1. Fix any remaining failures"
echo "2. Add more tests to reach 70% coverage"
echo "3. Set up GitHub Actions CI/CD"
echo "4. Document testing standards"