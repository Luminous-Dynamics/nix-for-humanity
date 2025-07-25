#!/usr/bin/env bash

# Comprehensive Integration Test Suite for NixOS GUI
# Tests all components working together
# July 22, 2025

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test configuration
BASE_URL="https://localhost:8443"
API_URL="${BASE_URL}/api"
TEST_USER="admin"
TEST_PASS="testpass123"
JWT_TOKEN=""
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Test results log
TEST_LOG="test-results-$(date +%Y%m%d-%H%M%S).log"

echo "🧪 NixOS GUI Integration Test Suite"
echo "=================================="
echo "Starting at: $(date)"
echo "Test log: $TEST_LOG"
echo ""

# Helper functions
log_test() {
    echo -e "${BLUE}TEST:${NC} $1" | tee -a $TEST_LOG
}

log_pass() {
    echo -e "${GREEN}✅ PASS:${NC} $1" | tee -a $TEST_LOG
    ((PASSED_TESTS++))
}

log_fail() {
    echo -e "${RED}❌ FAIL:${NC} $1" | tee -a $TEST_LOG
    echo "  Error: $2" | tee -a $TEST_LOG
    ((FAILED_TESTS++))
}

log_info() {
    echo -e "${YELLOW}ℹ️  INFO:${NC} $1" | tee -a $TEST_LOG
}

# Start test server if not running
start_test_server() {
    log_info "Checking if server is running..."
    
    if ! curl -k -s ${BASE_URL}/api/health > /dev/null 2>&1; then
        log_info "Starting test server..."
        cd ..
        ./test-secure-server.sh &
        SERVER_PID=$!
        sleep 5  # Give server time to start
        
        # Verify server started
        if ! curl -k -s ${BASE_URL}/api/health > /dev/null 2>&1; then
            log_fail "Server startup" "Failed to start test server"
            exit 1
        fi
        
        log_pass "Server started (PID: $SERVER_PID)"
    else
        log_info "Server already running"
    fi
}

# Test 1: Health Check
test_health_check() {
    ((TOTAL_TESTS++))
    log_test "Health Check Endpoint"
    
    RESPONSE=$(curl -k -s -w "\n%{http_code}" ${API_URL}/health)
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | head -n-1)
    
    if [ "$HTTP_CODE" = "200" ]; then
        if echo "$BODY" | grep -q "healthy"; then
            log_pass "Health check returned healthy status"
        else
            log_fail "Health check" "Invalid response body"
        fi
    else
        log_fail "Health check" "HTTP $HTTP_CODE"
    fi
}

# Test 2: Authentication Flow
test_authentication() {
    ((TOTAL_TESTS++))
    log_test "Authentication Flow"
    
    # Test login
    RESPONSE=$(curl -k -s -w "\n%{http_code}" \
        -X POST ${API_URL}/auth/login \
        -H "Content-Type: application/json" \
        -d "{\"username\":\"${TEST_USER}\",\"password\":\"${TEST_PASS}\"}")
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | head -n-1)
    
    if [ "$HTTP_CODE" = "200" ]; then
        JWT_TOKEN=$(echo "$BODY" | jq -r '.token' 2>/dev/null || echo "")
        if [ -n "$JWT_TOKEN" ] && [ "$JWT_TOKEN" != "null" ]; then
            log_pass "Login successful, received JWT token"
            
            # Test token verification
            ((TOTAL_TESTS++))
            VERIFY_RESPONSE=$(curl -k -s -w "\n%{http_code}" \
                ${API_URL}/auth/verify \
                -H "Authorization: Bearer ${JWT_TOKEN}")
            
            VERIFY_CODE=$(echo "$VERIFY_RESPONSE" | tail -n1)
            if [ "$VERIFY_CODE" = "200" ]; then
                log_pass "Token verification successful"
            else
                log_fail "Token verification" "HTTP $VERIFY_CODE"
            fi
        else
            log_fail "Login" "No token received"
        fi
    else
        log_fail "Login" "HTTP $HTTP_CODE"
    fi
}

# Test 3: Package Search
test_package_search() {
    ((TOTAL_TESTS++))
    log_test "Package Search API"
    
    if [ -z "$JWT_TOKEN" ]; then
        log_fail "Package search" "No auth token available"
        return
    fi
    
    RESPONSE=$(curl -k -s -w "\n%{http_code}" \
        -X POST ${API_URL}/packages/search \
        -H "Authorization: Bearer ${JWT_TOKEN}" \
        -H "Content-Type: application/json" \
        -d '{"query":"git"}')
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | head -n-1)
    
    if [ "$HTTP_CODE" = "200" ]; then
        PACKAGE_COUNT=$(echo "$BODY" | jq '. | length' 2>/dev/null || echo "0")
        if [ "$PACKAGE_COUNT" -gt 0 ]; then
            log_pass "Package search returned $PACKAGE_COUNT results"
        else
            log_fail "Package search" "No packages returned"
        fi
    else
        log_fail "Package search" "HTTP $HTTP_CODE"
    fi
}

# Test 4: WebSocket Connection
test_websocket() {
    ((TOTAL_TESTS++))
    log_test "WebSocket Real-time Updates"
    
    if [ -z "$JWT_TOKEN" ]; then
        log_fail "WebSocket test" "No auth token available"
        return
    fi
    
    # Create a simple WebSocket test using Node.js
    cat > ws-test.js << 'EOF'
const WebSocket = require('ws');
const https = require('https');

// Ignore self-signed certificate
process.env["NODE_TLS_REJECT_UNAUTHORIZED"] = 0;

const token = process.argv[2];
const ws = new WebSocket('wss://localhost:8443', {
    headers: {
        'Authorization': `Bearer ${token}`
    }
});

let received = false;

ws.on('open', () => {
    console.log('WebSocket connected');
    ws.send(JSON.stringify({ type: 'subscribe', data: { stream: 'system-stats' } }));
});

ws.on('message', (data) => {
    console.log('Received:', data.toString());
    received = true;
    ws.close();
});

ws.on('error', (err) => {
    console.error('WebSocket error:', err.message);
    process.exit(1);
});

setTimeout(() => {
    if (!received) {
        console.error('Timeout: No message received');
        process.exit(1);
    }
}, 10000);
EOF

    if command -v node > /dev/null 2>&1; then
        if node ws-test.js "$JWT_TOKEN" > ws-test.log 2>&1; then
            log_pass "WebSocket connection and message received"
        else
            log_fail "WebSocket test" "$(cat ws-test.log)"
        fi
    else
        log_info "Skipping WebSocket test (Node.js not available)"
    fi
    
    rm -f ws-test.js ws-test.log
}

# Test 5: Configuration API
test_configuration() {
    ((TOTAL_TESTS++))
    log_test "Configuration Management"
    
    if [ -z "$JWT_TOKEN" ]; then
        log_fail "Configuration test" "No auth token available"
        return
    fi
    
    # Get current configuration
    RESPONSE=$(curl -k -s -w "\n%{http_code}" \
        ${API_URL}/configuration \
        -H "Authorization: Bearer ${JWT_TOKEN}")
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | head -n-1)
    
    if [ "$HTTP_CODE" = "200" ]; then
        CONFIG_LENGTH=$(echo "$BODY" | jq -r '.content' | wc -c)
        if [ "$CONFIG_LENGTH" -gt 10 ]; then
            log_pass "Configuration retrieved ($CONFIG_LENGTH chars)"
            
            # Test validation
            ((TOTAL_TESTS++))
            VALIDATE_RESPONSE=$(curl -k -s -w "\n%{http_code}" \
                -X POST ${API_URL}/configuration/validate \
                -H "Authorization: Bearer ${JWT_TOKEN}" \
                -H "Content-Type: application/json" \
                -d '{"content":"{ config, pkgs, ... }: { }"}')
            
            VALIDATE_CODE=$(echo "$VALIDATE_RESPONSE" | tail -n1)
            if [ "$VALIDATE_CODE" = "200" ]; then
                log_pass "Configuration validation working"
            else
                log_fail "Configuration validation" "HTTP $VALIDATE_CODE"
            fi
        else
            log_fail "Configuration retrieval" "Empty configuration"
        fi
    else
        log_fail "Configuration retrieval" "HTTP $HTTP_CODE"
    fi
}

# Test 6: Service Management
test_services() {
    ((TOTAL_TESTS++))
    log_test "Service Management"
    
    if [ -z "$JWT_TOKEN" ]; then
        log_fail "Service test" "No auth token available"
        return
    fi
    
    RESPONSE=$(curl -k -s -w "\n%{http_code}" \
        ${API_URL}/services \
        -H "Authorization: Bearer ${JWT_TOKEN}")
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | head -n-1)
    
    if [ "$HTTP_CODE" = "200" ]; then
        SERVICE_COUNT=$(echo "$BODY" | jq '. | length' 2>/dev/null || echo "0")
        if [ "$SERVICE_COUNT" -gt 0 ]; then
            log_pass "Service list returned $SERVICE_COUNT services"
        else
            log_fail "Service list" "No services returned"
        fi
    else
        log_fail "Service list" "HTTP $HTTP_CODE"
    fi
}

# Test 7: System Stats
test_system_stats() {
    ((TOTAL_TESTS++))
    log_test "System Statistics"
    
    if [ -z "$JWT_TOKEN" ]; then
        log_fail "System stats test" "No auth token available"
        return
    fi
    
    RESPONSE=$(curl -k -s -w "\n%{http_code}" \
        ${API_URL}/system/stats \
        -H "Authorization: Bearer ${JWT_TOKEN}")
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | head -n-1)
    
    if [ "$HTTP_CODE" = "200" ]; then
        CPU_USAGE=$(echo "$BODY" | jq -r '.cpu.usage' 2>/dev/null || echo "null")
        if [ "$CPU_USAGE" != "null" ]; then
            log_pass "System stats returned (CPU: ${CPU_USAGE}%)"
        else
            log_fail "System stats" "Invalid stats format"
        fi
    else
        log_fail "System stats" "HTTP $HTTP_CODE"
    fi
}

# Test 8: Security Headers
test_security_headers() {
    ((TOTAL_TESTS++))
    log_test "Security Headers"
    
    HEADERS=$(curl -k -s -I ${BASE_URL} | grep -E "(Strict-Transport-Security|X-Content-Type-Options|X-Frame-Options|Content-Security-Policy)")
    
    if echo "$HEADERS" | grep -q "Strict-Transport-Security"; then
        log_pass "HSTS header present"
    else
        log_fail "Security headers" "Missing HSTS header"
    fi
    
    ((TOTAL_TESTS++))
    if echo "$HEADERS" | grep -q "X-Content-Type-Options"; then
        log_pass "X-Content-Type-Options header present"
    else
        log_fail "Security headers" "Missing X-Content-Type-Options"
    fi
}

# Test 9: Rate Limiting
test_rate_limiting() {
    ((TOTAL_TESTS++))
    log_test "Rate Limiting"
    
    # Make multiple rapid requests
    BLOCKED=false
    for i in {1..150}; do
        HTTP_CODE=$(curl -k -s -o /dev/null -w "%{http_code}" \
            -X POST ${API_URL}/packages/search \
            -H "Authorization: Bearer ${JWT_TOKEN}" \
            -H "Content-Type: application/json" \
            -d '{"query":"test"}')
        
        if [ "$HTTP_CODE" = "429" ]; then
            BLOCKED=true
            break
        fi
    done
    
    if [ "$BLOCKED" = true ]; then
        log_pass "Rate limiting working (blocked after $i requests)"
    else
        log_fail "Rate limiting" "No rate limit triggered after 150 requests"
    fi
}

# Test 10: Frontend Loading
test_frontend() {
    ((TOTAL_TESTS++))
    log_test "Frontend Loading"
    
    RESPONSE=$(curl -k -s -w "\n%{http_code}" ${BASE_URL}/)
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | head -n-1)
    
    if [ "$HTTP_CODE" = "200" ]; then
        if echo "$BODY" | grep -q "NixOS GUI"; then
            log_pass "Frontend HTML loaded successfully"
        else
            log_fail "Frontend loading" "HTML doesn't contain expected content"
        fi
    else
        log_fail "Frontend loading" "HTTP $HTTP_CODE"
    fi
}

# Main test execution
main() {
    echo "" | tee -a $TEST_LOG
    
    # Start server if needed
    start_test_server
    
    echo "" | tee -a $TEST_LOG
    echo "Running integration tests..." | tee -a $TEST_LOG
    echo "===========================" | tee -a $TEST_LOG
    
    # Run all tests
    test_health_check
    test_authentication
    test_package_search
    test_websocket
    test_configuration
    test_services
    test_system_stats
    test_security_headers
    test_rate_limiting
    test_frontend
    
    # Summary
    echo "" | tee -a $TEST_LOG
    echo "Test Summary" | tee -a $TEST_LOG
    echo "============" | tee -a $TEST_LOG
    echo "Total Tests: $TOTAL_TESTS" | tee -a $TEST_LOG
    echo -e "${GREEN}Passed: $PASSED_TESTS${NC}" | tee -a $TEST_LOG
    echo -e "${RED}Failed: $FAILED_TESTS${NC}" | tee -a $TEST_LOG
    
    SUCCESS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    echo "Success Rate: ${SUCCESS_RATE}%" | tee -a $TEST_LOG
    
    echo "" | tee -a $TEST_LOG
    if [ $FAILED_TESTS -eq 0 ]; then
        echo -e "${GREEN}🎉 All tests passed!${NC}" | tee -a $TEST_LOG
        exit 0
    else
        echo -e "${RED}⚠️  Some tests failed. Check $TEST_LOG for details.${NC}" | tee -a $TEST_LOG
        exit 1
    fi
}

# Cleanup on exit
cleanup() {
    if [ -n "$SERVER_PID" ]; then
        log_info "Stopping test server..."
        kill $SERVER_PID 2>/dev/null || true
    fi
}

trap cleanup EXIT

# Run tests
main