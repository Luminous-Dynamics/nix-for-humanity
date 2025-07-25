#!/bin/bash

# Run Tests Script
# Execute different test suites and generate coverage reports

set -e

echo "🧪 NixOS GUI Test Suite"
echo "======================"
echo

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Function to run tests with nice output
run_test_suite() {
    local suite_name=$1
    local test_command=$2
    
    echo -e "${YELLOW}Running ${suite_name}...${NC}"
    
    if npm run ${test_command}; then
        echo -e "${GREEN}✓ ${suite_name} passed${NC}\n"
        return 0
    else
        echo -e "${RED}✗ ${suite_name} failed${NC}\n"
        return 1
    fi
}

# Check if running specific suite
if [ "$1" = "unit" ]; then
    run_test_suite "Unit Tests" "test:unit"
elif [ "$1" = "integration" ]; then
    run_test_suite "Integration Tests" "test:integration"
elif [ "$1" = "e2e" ]; then
    run_test_suite "E2E Tests" "test:e2e"
elif [ "$1" = "coverage" ]; then
    echo -e "${YELLOW}Running all tests with coverage...${NC}"
    npm run test:coverage
    
    echo -e "\n${GREEN}Coverage report generated in ./coverage${NC}"
    echo "Open coverage/lcov-report/index.html to view detailed report"
else
    # Run all test suites
    failed_suites=0
    
    # Run unit tests
    if ! run_test_suite "Unit Tests" "test:unit"; then
        ((failed_suites++))
    fi
    
    # Run integration tests
    if ! run_test_suite "Integration Tests" "test:integration"; then
        ((failed_suites++))
    fi
    
    # Run E2E tests
    if ! run_test_suite "E2E Tests" "test:e2e"; then
        ((failed_suites++))
    fi
    
    # Summary
    echo "========================"
    if [ $failed_suites -eq 0 ]; then
        echo -e "${GREEN}✓ All test suites passed!${NC}"
        
        # Run coverage
        echo -e "\n${YELLOW}Generating coverage report...${NC}"
        npm run test:coverage -- --silent
        
        # Display coverage summary
        echo -e "\n${GREEN}Coverage Summary:${NC}"
        cat coverage/coverage-summary.json | jq -r '
            .total |
            "Statements: \(.statements.pct)%\nBranches: \(.branches.pct)%\nFunctions: \(.functions.pct)%\nLines: \(.lines.pct)%"
        ' 2>/dev/null || echo "Coverage summary not available"
        
        exit 0
    else
        echo -e "${RED}✗ ${failed_suites} test suite(s) failed${NC}"
        exit 1
    fi
fi

# Optional: Open coverage report in browser
if [ "$2" = "--open" ]; then
    if [ -f "coverage/lcov-report/index.html" ]; then
        echo "Opening coverage report in browser..."
        xdg-open "coverage/lcov-report/index.html" 2>/dev/null || open "coverage/lcov-report/index.html" 2>/dev/null
    fi
fi