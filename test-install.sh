#!/usr/bin/env bash

# 🧪 Test Installation Script for Luminous Nix
# =============================================
# Tests that everything works on a fresh NixOS system

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'
BOLD='\033[1m'

echo -e "${BLUE}${BOLD}🧪 Testing Luminous Nix Installation${NC}"
echo "======================================"
echo

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Test function
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "${YELLOW}Testing: $test_name${NC}"
    
    if eval "$test_command" &>/dev/null; then
        echo -e "${GREEN}  ✅ PASSED${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}  ❌ FAILED${NC}"
        ((TESTS_FAILED++))
    fi
}

# Test if we're in the right directory
run_test "Project directory" "[ -f flake.nix ]"

# Test Nix availability
run_test "Nix installed" "command -v nix"

# Test flakes enabled
run_test "Flakes enabled" "nix flake --help"

# Test the flake builds
echo
echo -e "${BLUE}Building with Nix flake...${NC}"
run_test "Flake evaluation" "nix flake check --no-build 2>/dev/null"

# Test development shell
echo
echo -e "${BLUE}Testing development shell...${NC}"
run_test "Dev shell enters" "nix develop -c echo 'Shell works'"

# Test the CLI commands exist in dev shell
echo
echo -e "${BLUE}Testing CLI commands...${NC}"
run_test "ask-nix exists" "nix develop -c which ask-nix"
run_test "grandma-nix exists" "nix develop -c which grandma-nix"
run_test "run-tui-app exists" "nix develop -c which run-tui-app"
run_test "ask-nix-guru exists" "nix develop -c which ask-nix-guru"

# Test Python environment
echo
echo -e "${BLUE}Testing Python environment...${NC}"
run_test "Python 3.11 available" "nix develop -c python --version | grep '3.11'"
run_test "Poetry environment" "nix develop -c python -c 'import textual' 2>/dev/null"

# Test the actual commands work
echo
echo -e "${BLUE}Testing command execution...${NC}"
run_test "ask-nix help" "nix develop -c bash -c 'export NIX_HUMANITY_PYTHON_BACKEND=true; ./bin/ask-nix help 2>/dev/null | grep -i nix'"
run_test "grandma-nix help" "nix develop -c ./bin/grandma-nix help 2>/dev/null | grep -i grandma"

# Test quick demo script
echo
echo -e "${BLUE}Testing quick demo...${NC}"
run_test "Quick demo script exists" "[ -f quick-demo.sh ]"
run_test "Quick demo is executable" "[ -x quick-demo.sh ]"

# Test GUI components
echo
echo -e "${BLUE}Testing GUI components...${NC}"
run_test "TypeScript config" "[ -f src/gui/tsconfig.json ]"
run_test "Package.json for GUI" "[ -f src/gui/package.json ]"
run_test "Modular components" "[ -f src/gui/components/ModularComponents.ts ]"
run_test "Setup Ceremony" "[ -f src/gui/SetupCeremony.ts ]"
run_test "State Manager" "[ -f src/gui/StateManager.ts ]"
run_test "Bridge integration" "[ -f src/gui/NixOSGuiBridge.ts ]"

# Test installation methods
echo
echo -e "${BLUE}Testing installation methods...${NC}"
run_test "Install script exists" "[ -f install.sh ]"
run_test "Install script is executable" "[ -x install.sh ]"

# Test nix run command (without actually running to avoid side effects)
echo
echo -e "${BLUE}Testing nix run capability...${NC}"
run_test "Nix run available" "nix run --help &>/dev/null"

# Test if we can build the package
echo
echo -e "${BLUE}Testing package build (this may take a moment)...${NC}"
if [ "$SKIP_BUILD" != "1" ]; then
    run_test "Package builds" "nix build .#luminous-nix --no-link 2>/dev/null"
else
    echo -e "${YELLOW}  ⏭️  Skipping build test (set SKIP_BUILD=0 to enable)${NC}"
fi

# Summary
echo
echo "======================================"
echo -e "${BOLD}Test Summary:${NC}"
echo -e "${GREEN}  Passed: $TESTS_PASSED${NC}"
echo -e "${RED}  Failed: $TESTS_FAILED${NC}"
echo

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}${BOLD}🎉 All tests passed! Luminous Nix is ready for installation.${NC}"
    echo
    echo -e "${BLUE}Next steps:${NC}"
    echo "  1. Test on a fresh NixOS VM"
    echo "  2. Run: nix run .#grandma-nix"
    echo "  3. Try: curl -L https://raw.githubusercontent.com/Luminous-Dynamics/luminous-nix/main/install.sh | sh"
    exit 0
else
    echo -e "${RED}${BOLD}⚠️  Some tests failed. Please fix the issues before proceeding.${NC}"
    exit 1
fi