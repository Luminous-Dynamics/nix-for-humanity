#!/usr/bin/env bash
# Comprehensive test suite for Nix for Humanity commands
# Tests all executables and their various modes

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

# Ensure we're in the right directory
cd "$(dirname "$0")/.."

echo -e "${BLUE}=== Nix for Humanity Command Test Suite ===${NC}"
echo "Testing all executables in bin/"
echo

# Function to run a test
run_test() {
    local test_name="$1"
    local command="$2"
    local expected_success="${3:-true}"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    echo -n "Testing: $test_name ... "

    if eval "$command" > /tmp/test_output_$$.txt 2>&1; then
        if [ "$expected_success" = "true" ]; then
            echo -e "${GREEN}PASSED${NC}"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            echo -e "${RED}FAILED${NC} (expected to fail but succeeded)"
            FAILED_TESTS=$((FAILED_TESTS + 1))
            cat /tmp/test_output_$$.txt
        fi
    else
        if [ "$expected_success" = "false" ]; then
            echo -e "${GREEN}PASSED${NC} (correctly failed)"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            echo -e "${RED}FAILED${NC}"
            FAILED_TESTS=$((FAILED_TESTS + 1))
            cat /tmp/test_output_$$.txt
        fi
    fi

    rm -f /tmp/test_output_$$.txt
}

# Function to check if executable exists
check_executable() {
    local exe="$1"
    if [ -x "bin/$exe" ]; then
        return 0
    else
        echo -e "${YELLOW}SKIPPING${NC} $exe (not found or not executable)"
        SKIPPED_TESTS=$((SKIPPED_TESTS + 1))
        return 1
    fi
}

echo -e "${BLUE}=== Testing ask-nix-hybrid ===${NC}"
if check_executable "ask-nix-hybrid"; then
    run_test "ask-nix-hybrid basic query" "bin/ask-nix-hybrid 'install firefox'"
    run_test "ask-nix-hybrid minimal style" "bin/ask-nix-hybrid --minimal 'install python'"
    run_test "ask-nix-hybrid friendly style" "bin/ask-nix-hybrid --friendly 'update system'"
    run_test "ask-nix-hybrid encouraging style" "bin/ask-nix-hybrid --encouraging 'my wifi is broken'"
    run_test "ask-nix-hybrid technical style" "bin/ask-nix-hybrid --technical 'install docker'"
    run_test "ask-nix-hybrid no args" "bin/ask-nix-hybrid" false
fi
echo

echo -e "${BLUE}=== Testing ask-nix-v3 ===${NC}"
if check_executable "ask-nix-v3"; then
    run_test "ask-nix-v3 basic query" "bin/ask-nix-v3 'install firefox'"
    run_test "ask-nix-v3 show intent" "bin/ask-nix-v3 --show-intent 'I need vscode'"
    run_test "ask-nix-v3 dry-run (default)" "bin/ask-nix-v3 --execute 'install vim'"
    run_test "ask-nix-v3 help" "bin/ask-nix-v3 --help"
    run_test "ask-nix-v3 search" "bin/ask-nix-v3 'search for text editors'"
    run_test "ask-nix-v3 update query" "bin/ask-nix-v3 'update my system'"
    # Don't test real execution to avoid system changes
    # run_test "ask-nix-v3 real execution" "bin/ask-nix-v3 --execute --no-dry-run 'install hello'"
fi
echo

echo -e "${BLUE}=== Testing nix-profile-do ===${NC}"
if check_executable "nix-profile-do"; then
    run_test "nix-profile-do basic query" "bin/nix-profile-do 'install firefox'"
    run_test "nix-profile-do dry-run explicit" "bin/nix-profile-do --dry-run 'install nodejs'"
    run_test "nix-profile-do search" "bin/nix-profile-do 'search python'"
    run_test "nix-profile-do invalid query" "bin/nix-profile-do 'do something random'"
fi
echo

echo -e "${BLUE}=== Testing nix-do (if exists) ===${NC}"
if check_executable "nix-do"; then
    run_test "nix-do basic query" "bin/nix-do 'install firefox'"
fi
echo

echo -e "${BLUE}=== Testing Problematic Commands ===${NC}"
echo "These are expected to have issues:"

if check_executable "ask-nix-enhanced"; then
    run_test "ask-nix-enhanced (may fail)" "bin/ask-nix-enhanced 'install firefox'" false
fi

if check_executable "ask-nix-hybrid-v2"; then
    run_test "ask-nix-hybrid-v2 (may fail)" "bin/ask-nix-hybrid-v2 'install firefox'" false
fi

if check_executable "ask-trinity"; then
    run_test "ask-trinity (may fail)" "bin/ask-trinity 'install firefox'" false
fi

if check_executable "ask-trinity-rag"; then
    run_test "ask-trinity-rag (may fail)" "bin/ask-trinity-rag 'install firefox'" false
fi
echo

echo -e "${BLUE}=== Testing Pattern Recognition ===${NC}"
# Test various natural language patterns
test_patterns=(
    "install firefox"
    "I need python"
    "how do I get vscode"
    "search for editors"
    "find docker"
    "update nixos"
    "upgrade my system"
    "wifi not working"
    "network issues"
    "rollback system"
    "undo last update"
)

for pattern in "${test_patterns[@]}"; do
    if check_executable "ask-nix-v3"; then
        run_test "Pattern: '$pattern'" "bin/ask-nix-v3 --show-intent '$pattern'"
    fi
done
echo

echo -e "${BLUE}=== Testing Edge Cases ===${NC}"
if check_executable "ask-nix-hybrid"; then
    run_test "Empty query" "bin/ask-nix-hybrid ''" false
    run_test "Very long query" "bin/ask-nix-hybrid 'I really really really need to install firefox because I want to browse the web and do many things with it'"
    run_test "Special characters" "bin/ask-nix-hybrid 'install package@#$%'"
    run_test "Unknown package" "bin/ask-nix-hybrid 'install completely-fake-package-xyz'"
fi
echo

echo -e "${BLUE}=== Testing Knowledge Base ===${NC}"
# Test if the knowledge base is accessible
if [ -f "nixos_knowledge.db" ]; then
    echo -e "${GREEN}✓${NC} Knowledge base exists"

    # Test a direct query to the knowledge base
    if command -v sqlite3 >/dev/null 2>&1; then
        solution_count=$(sqlite3 nixos_knowledge.db "SELECT COUNT(*) FROM solutions;" 2>/dev/null || echo "0")
        echo -e "${GREEN}✓${NC} Knowledge base has $solution_count solutions"
    else
        echo -e "${YELLOW}!${NC} sqlite3 not available, skipping DB check"
    fi
else
    echo -e "${RED}✗${NC} Knowledge base not found"
fi
echo

echo -e "${BLUE}=== Test Summary ===${NC}"
echo "Total tests: $TOTAL_TESTS"
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed: ${RED}$FAILED_TESTS${NC}"
echo -e "Skipped: ${YELLOW}$SKIPPED_TESTS${NC}"
echo
if [ $FAILED_TESTS -eq 0 ] && [ $PASSED_TESTS -gt 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
elif [ $PASSED_TESTS -eq 0 ]; then
    echo -e "${RED}No tests passed!${NC}"
    exit 1
else
    echo -e "${YELLOW}Some tests failed${NC}"
    exit 1
fi
