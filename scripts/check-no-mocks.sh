#!/usr/bin/env bash
# check-no-mocks.sh - Pre-commit hook to prevent mock usage in tests
# Part of the consciousness-first testing approach

set -e

echo "🧪 Checking for mock usage in tests..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track if we found any violations
found_mocks=0

# Check Python test files for mock usage
echo "Scanning Python test files..."

# Find all Python test files
test_files=$(find tests/ -name "*.py" -type f 2>/dev/null || true)

if [ -z "$test_files" ]; then
    echo "No test files found to check."
    exit 0
fi

# Check each file for mock usage
for file in $test_files; do
    # Skip __pycache__ directories
    if [[ "$file" == *"__pycache__"* ]]; then
        continue
    fi
    
    # Check for various mock patterns
    if grep -l -E "(from unittest\.mock|from mock import|import mock|Mock\(|MagicMock\(|patch\(|@mock\.|@patch)" "$file" > /dev/null 2>&1; then
        echo -e "${RED}❌ Found mock usage in: $file${NC}"
        found_mocks=1
        
        # Show the specific lines with mocks
        echo -e "${YELLOW}  Lines with mocks:${NC}"
        grep -n -E "(from unittest\.mock|from mock import|import mock|Mock\(|MagicMock\(|patch\(|@mock\.|@patch)" "$file" | head -5
        echo ""
    fi
done

# Check for any legacy mock-based test files
legacy_files=$(grep -l "legacy_mock" tests/ -R 2>/dev/null || true)
if [ ! -z "$legacy_files" ]; then
    echo -e "${YELLOW}⚠️  Found legacy mock-based tests that need migration:${NC}"
    echo "$legacy_files"
    echo ""
fi

# Provide guidance if mocks were found
if [ $found_mocks -eq 1 ]; then
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}❌ Mock usage detected! Please use consciousness-first testing instead.${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Instead of mocks, use real test implementations from tests/test_utils/:"
    echo ""
    echo "  from tests.test_utils import ("
    echo "      TestExecutionBackend,    # Instead of mocking subprocess"
    echo "      TestNLPEngine,          # Instead of mocking NLP"
    echo "      TestDatabase,           # Instead of mocking SQLite"
    echo "      TestLearningEngine,     # Instead of mocking AI"
    echo "  )"
    echo ""
    echo "See docs/03-DEVELOPMENT/06-CONSCIOUSNESS-FIRST-TESTING.md for migration guide."
    echo ""
    exit 1
else
    echo -e "${GREEN}✅ No mock usage found! Consciousness-first testing in effect.${NC}"
fi

# Optional: Check for good testing practices
echo ""
echo "Checking for consciousness-first test patterns..."

# Count test files using our test utilities
good_tests=$(grep -l "from tests.test_utils import" tests/ -R 2>/dev/null | wc -l || echo 0)
total_tests=$(find tests/ -name "test_*.py" -type f | wc -l || echo 0)

if [ $good_tests -gt 0 ]; then
    echo -e "${GREEN}✅ Found $good_tests test files using consciousness-first patterns${NC}"
fi

# Check for persona-aware tests
persona_tests=$(grep -l "PERSONA_TEST_DATA\|persona_test" tests/ -R 2>/dev/null | wc -l || echo 0)
if [ $persona_tests -gt 0 ]; then
    echo -e "${GREEN}✅ Found $persona_tests test files with persona-aware testing${NC}"
fi

# Check for performance tests
perf_tests=$(grep -l "performance_test\|@performance" tests/ -R 2>/dev/null | wc -l || echo 0)
if [ $perf_tests -gt 0 ]; then
    echo -e "${GREEN}✅ Found $perf_tests test files with performance testing${NC}"
fi

echo ""
echo "Test quality summary:"
echo "  Total test files: $total_tests"
echo "  Using test utilities: $good_tests"
echo "  Persona-aware tests: $persona_tests"
echo "  Performance tests: $perf_tests"

exit 0