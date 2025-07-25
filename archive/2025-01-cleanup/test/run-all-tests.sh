#!/usr/bin/env bash

# Master Test Runner for NixOS GUI
# Executes all test suites and generates comprehensive report
# July 22, 2025

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Test results directory
RESULTS_DIR="test-results-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$RESULTS_DIR"

echo -e "${PURPLE}🧪 NixOS GUI Complete Test Suite${NC}"
echo -e "${PURPLE}================================${NC}"
echo "Results will be saved to: $RESULTS_DIR"
echo ""

# Summary tracking
TOTAL_SUITES=0
PASSED_SUITES=0
FAILED_SUITES=0

# Helper functions
run_test_suite() {
    local suite_name=$1
    local script_path=$2
    local log_file="$RESULTS_DIR/${suite_name}.log"
    
    ((TOTAL_SUITES++))
    
    echo -e "${BLUE}Running ${suite_name}...${NC}"
    
    if [ -f "$script_path" ] && [ -x "$script_path" ]; then
        if $script_path > "$log_file" 2>&1; then
            echo -e "${GREEN}✅ ${suite_name} completed successfully${NC}"
            ((PASSED_SUITES++))
            return 0
        else
            echo -e "${RED}❌ ${suite_name} failed${NC}"
            echo "   Check $log_file for details"
            ((FAILED_SUITES++))
            return 1
        fi
    else
        echo -e "${RED}❌ ${suite_name} script not found or not executable${NC}"
        ((FAILED_SUITES++))
        return 1
    fi
}

# Pre-flight checks
echo -e "${YELLOW}Pre-flight Checks${NC}"
echo "================="

# Check if server is running
if curl -k -s https://localhost:8443/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Server is running${NC}"
else
    echo -e "${YELLOW}⚠️  Server not detected. Starting test server...${NC}"
    cd ..
    ./test-secure-server.sh > "$RESULTS_DIR/server.log" 2>&1 &
    SERVER_PID=$!
    sleep 5
    
    if curl -k -s https://localhost:8443/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Test server started${NC}"
    else
        echo -e "${RED}❌ Failed to start test server${NC}"
        exit 1
    fi
fi

# Check dependencies
echo ""
echo "Checking dependencies..."

check_dependency() {
    if command -v $1 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $1 found${NC}"
    else
        echo -e "${YELLOW}⚠️  $1 not found (some tests may be skipped)${NC}"
    fi
}

check_dependency "node"
check_dependency "curl"
check_dependency "jq"
check_dependency "openssl"

echo ""
echo -e "${PURPLE}Running Test Suites${NC}"
echo "==================="
echo ""

# 1. Integration Tests
run_test_suite "Integration Tests" "./integration-test-suite.sh" || true

echo ""

# 2. Security Audit
run_test_suite "Security Audit" "./security-audit.sh" || true

echo ""

# 3. Performance Tests
if command -v node > /dev/null 2>&1; then
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo "Installing test dependencies..."
        npm install ws > "$RESULTS_DIR/npm-install.log" 2>&1
    fi
    
    run_test_suite "Performance Tests" "./performance-test.js" || true
else
    echo -e "${YELLOW}⚠️  Skipping Performance Tests (Node.js not available)${NC}"
fi

echo ""

# 4. Frontend Tests
echo -e "${BLUE}Frontend Tests${NC}"
echo "Open test/frontend-test.html in a browser to run frontend tests"
echo "URL: file://$(pwd)/frontend-test.html"
cp frontend-test.html "$RESULTS_DIR/" 2>/dev/null || true

echo ""

# 5. Module Tests
echo -e "${BLUE}NixOS Module Tests${NC}"
if command -v nix-instantiate > /dev/null 2>&1; then
    if nix-instantiate --parse ../nixos-module.nix > "$RESULTS_DIR/module-parse.log" 2>&1; then
        echo -e "${GREEN}✅ NixOS module syntax valid${NC}"
    else
        echo -e "${RED}❌ NixOS module syntax error${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Skipping module tests (Nix not available)${NC}"
fi

echo ""

# Generate comprehensive report
echo -e "${PURPLE}Generating Test Report${NC}"
echo "====================="

REPORT_FILE="$RESULTS_DIR/test-report.md"

cat > "$REPORT_FILE" << EOF
# NixOS GUI Test Report

Generated: $(date)

## Summary

- Total Test Suites: $TOTAL_SUITES
- Passed: $PASSED_SUITES
- Failed: $FAILED_SUITES
- Success Rate: $(( PASSED_SUITES * 100 / TOTAL_SUITES ))%

## Test Results

### Integration Tests
$(if [ -f "$RESULTS_DIR/Integration Tests.log" ]; then
    grep -E "(PASS|FAIL|Total Tests|Success Rate)" "$RESULTS_DIR/Integration Tests.log" | tail -5 || echo "No results"
else
    echo "Not executed"
fi)

### Security Audit
$(if [ -f "$RESULTS_DIR/Security Audit.log" ]; then
    grep -E "(Passed:|Warnings:|Failures:|Security Grade:)" "$RESULTS_DIR/Security Audit.log" | tail -5 || echo "No results"
else
    echo "Not executed"
fi)

### Performance Tests
$(if [ -f "$RESULTS_DIR/Performance Tests.log" ]; then
    grep -E "(Total Requests:|Successful:|Average:|Response Time:|Reliability:)" "$RESULTS_DIR/Performance Tests.log" | tail -10 || echo "No results"
else
    echo "Not executed"
fi)

## Recommendations

Based on the test results:

$(if [ $FAILED_SUITES -eq 0 ]; then
    echo "✅ All test suites passed! The system appears to be production-ready."
else
    echo "⚠️  Some test suites failed. Please review the individual logs for details:"
    echo ""
    [ -f "$RESULTS_DIR/Integration Tests.log" ] && [ $? -ne 0 ] && echo "- Review Integration Tests log for functionality issues"
    [ -f "$RESULTS_DIR/Security Audit.log" ] && grep -q "FAIL" "$RESULTS_DIR/Security Audit.log" && echo "- Address security vulnerabilities found in Security Audit"
    [ -f "$RESULTS_DIR/Performance Tests.log" ] && grep -q "Needs Improvement" "$RESULTS_DIR/Performance Tests.log" && echo "- Optimize performance based on Performance Tests results"
fi)

## Next Steps

1. Review detailed logs in the \`$RESULTS_DIR\` directory
2. Address any failed tests or warnings
3. Re-run failed test suites after fixes
4. Consider adding more test cases for edge scenarios

---

*NixOS GUI - Consciousness-First Configuration Interface*
EOF

echo -e "${GREEN}✅ Test report generated: $REPORT_FILE${NC}"

# Display summary
echo ""
echo -e "${PURPLE}Test Summary${NC}"
echo "============"
echo "Total Test Suites: $TOTAL_SUITES"
echo -e "Passed: ${GREEN}$PASSED_SUITES${NC}"
echo -e "Failed: ${RED}$FAILED_SUITES${NC}"

if [ $FAILED_SUITES -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 All tests passed! The system is ready for deployment.${NC}"
    EXIT_CODE=0
else
    echo ""
    echo -e "${YELLOW}⚠️  Some tests failed. Review the logs in $RESULTS_DIR${NC}"
    EXIT_CODE=1
fi

# Cleanup
if [ -n "$SERVER_PID" ]; then
    echo ""
    echo "Stopping test server..."
    kill $SERVER_PID 2>/dev/null || true
fi

echo ""
echo -e "${BLUE}📁 All test results saved to: $RESULTS_DIR${NC}"
echo -e "${BLUE}📄 Summary report: $REPORT_FILE${NC}"

exit $EXIT_CODE