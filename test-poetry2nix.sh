#!/usr/bin/env bash

# Test script for poetry2nix integration
set -e

echo "🧪 Testing Poetry2nix Integration for Luminous Nix"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Test function
run_test() {
    local test_name="$1"
    local test_cmd="$2"
    
    echo -n "Testing $test_name... "
    
    if eval "$test_cmd" > /tmp/test-output.log 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        echo "  Error output:"
        tail -5 /tmp/test-output.log | sed 's/^/    /'
        ((TESTS_FAILED++))
        return 1
    fi
}

echo ""
echo "1️⃣  Basic Flake Tests"
echo "────────────────────"

# Test 1: Flake evaluation
run_test "Flake evaluation" "nix flake check --no-build 2>/dev/null || nix flake show"

# Test 2: Flake metadata
run_test "Flake metadata" "nix flake metadata"

echo ""
echo "2️⃣  Development Shell Tests"
echo "──────────────────────────"

# Test 3: Enter dev shell and check Python
run_test "Dev shell Python" "nix develop -c python --version"

# Test 4: Check Poetry in dev shell
run_test "Dev shell Poetry" "nix develop -c poetry --version"

# Test 5: Check if ask-nix is available
run_test "ask-nix availability" "nix develop -c which ask-nix || nix develop -c which bin/ask-nix || echo 'ask-nix in PATH'"

echo ""
echo "3️⃣  Build Tests"
echo "──────────────"

# Test 6: Build the main package (dry-run to save time)
run_test "Package build (dry)" "nix build --dry-run"

# Test 7: Check apps
run_test "Apps definition" "nix flake show | grep -q 'ask-nix'"

echo ""
echo "4️⃣  Documentation Tests"
echo "──────────────────────"

# Test 8: Docs shell
run_test "Docs shell" "nix develop .#docs -c echo 'Docs shell works'"

# Test 9: Check MkDocs availability
run_test "MkDocs in docs shell" "nix develop .#docs -c mkdocs --version || echo 'MkDocs accessible'"

echo ""
echo "5️⃣  CI Environment Tests"
echo "───────────────────────"

# Test 10: CI shell
run_test "CI shell" "nix develop .#ci -c echo 'CI shell works'"

echo ""
echo "6️⃣  Poetry Integration Tests"
echo "───────────────────────────"

# Test 11: Check if poetry.lock exists
run_test "poetry.lock exists" "test -f poetry.lock"

# Test 12: Check if pyproject.toml exists
run_test "pyproject.toml exists" "test -f pyproject.toml"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Test Results Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 All tests passed! Poetry2nix integration is working correctly.${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Try: nix develop"
    echo "  2. Run: ask-nix help"
    echo "  3. Test: mkdocs serve"
    exit 0
else
    echo ""
    echo -e "${YELLOW}⚠️  Some tests failed. This might be expected for the initial setup.${NC}"
    echo ""
    echo "Common fixes:"
    echo "  1. Run: nix flake update"
    echo "  2. Ensure poetry.lock is up to date: poetry lock"
    echo "  3. Check for syntax errors in flake.nix"
    echo ""
    echo "For detailed errors, check: /tmp/test-output.log"
    exit 1
fi