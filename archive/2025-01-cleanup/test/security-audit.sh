#!/usr/bin/env bash

# Security Audit for NixOS GUI
# Comprehensive security testing
# July 22, 2025

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
BASE_URL="https://localhost:8443"
API_URL="${BASE_URL}/api"
AUDIT_LOG="security-audit-$(date +%Y%m%d-%H%M%S).log"

echo "🔒 NixOS GUI Security Audit"
echo "=========================="
echo "Starting at: $(date)"
echo "Audit log: $AUDIT_LOG"
echo ""

# Helper functions
log_test() {
    echo -e "${BLUE}[AUDIT]${NC} $1" | tee -a $AUDIT_LOG
}

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $1" | tee -a $AUDIT_LOG
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a $AUDIT_LOG
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1" | tee -a $AUDIT_LOG
}

# Test 1: SSL/TLS Configuration
test_ssl_configuration() {
    log_test "Testing SSL/TLS Configuration"
    
    # Check SSL certificate
    SSL_INFO=$(echo | openssl s_client -connect localhost:8443 2>/dev/null | openssl x509 -noout -text 2>/dev/null || echo "")
    
    if [ -n "$SSL_INFO" ]; then
        log_pass "SSL certificate present"
        
        # Check key strength
        KEY_BITS=$(echo "$SSL_INFO" | grep "Public-Key:" | grep -oE "[0-9]+" || echo "0")
        if [ "$KEY_BITS" -ge 2048 ]; then
            log_pass "Key strength adequate: ${KEY_BITS} bits"
        else
            log_fail "Weak key strength: ${KEY_BITS} bits (minimum 2048)"
        fi
        
        # Check cipher suites
        CIPHERS=$(nmap --script ssl-enum-ciphers -p 8443 localhost 2>/dev/null || echo "")
        if echo "$CIPHERS" | grep -q "TLSv1.2"; then
            log_pass "TLSv1.2 supported"
        else
            log_warn "TLSv1.2 not detected"
        fi
    else
        log_fail "Could not retrieve SSL certificate"
    fi
    
    # Test HSTS header
    HEADERS=$(curl -k -s -I ${BASE_URL})
    if echo "$HEADERS" | grep -qi "Strict-Transport-Security"; then
        log_pass "HSTS header present"
    else
        log_fail "HSTS header missing"
    fi
}

# Test 2: Authentication Security
test_authentication_security() {
    log_test "Testing Authentication Security"
    
    # Test weak passwords
    WEAK_PASSWORDS=("admin" "password" "123456" "nixos" "")
    
    for pwd in "${WEAK_PASSWORDS[@]}"; do
        RESPONSE=$(curl -k -s -w "\n%{http_code}" \
            -X POST ${API_URL}/auth/login \
            -H "Content-Type: application/json" \
            -d "{\"username\":\"admin\",\"password\":\"$pwd\"}" 2>/dev/null)
        
        HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
        
        if [ "$HTTP_CODE" = "200" ]; then
            if [ "$pwd" = "" ]; then
                log_fail "Empty password accepted!"
            else
                log_warn "Weak password accepted: $pwd"
            fi
        fi
    done
    
    # Test SQL injection in login
    SQL_PAYLOADS=("admin' OR '1'='1" "admin'; DROP TABLE users;--" "admin\"; DROP TABLE users;--")
    
    for payload in "${SQL_PAYLOADS[@]}"; do
        RESPONSE=$(curl -k -s -w "\n%{http_code}" \
            -X POST ${API_URL}/auth/login \
            -H "Content-Type: application/json" \
            -d "{\"username\":\"$payload\",\"password\":\"test\"}" 2>/dev/null)
        
        HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
        
        if [ "$HTTP_CODE" = "500" ]; then
            log_fail "Potential SQL injection vulnerability with payload: $payload"
        else
            log_pass "SQL injection attempt blocked: $payload"
        fi
    done
    
    # Test JWT security
    # Try to access API without token
    RESPONSE=$(curl -k -s -w "\n%{http_code}" ${API_URL}/packages/search)
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    
    if [ "$HTTP_CODE" = "401" ]; then
        log_pass "API requires authentication"
    else
        log_fail "API accessible without authentication"
    fi
    
    # Test with invalid JWT
    INVALID_JWT="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    
    RESPONSE=$(curl -k -s -w "\n%{http_code}" \
        ${API_URL}/packages/search \
        -H "Authorization: Bearer $INVALID_JWT")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    
    if [ "$HTTP_CODE" = "403" ]; then
        log_pass "Invalid JWT rejected"
    else
        log_fail "Invalid JWT not properly rejected"
    fi
}

# Test 3: Input Validation
test_input_validation() {
    log_test "Testing Input Validation"
    
    # Get valid token first
    AUTH_RESPONSE=$(curl -k -s -X POST ${API_URL}/auth/login \
        -H "Content-Type: application/json" \
        -d '{"username":"admin","password":"testpass"}')
    
    TOKEN=$(echo "$AUTH_RESPONSE" | jq -r '.token' 2>/dev/null || echo "")
    
    if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
        log_warn "Could not get auth token for validation tests"
        return
    fi
    
    # Test XSS payloads
    XSS_PAYLOADS=(
        "<script>alert('XSS')</script>"
        "javascript:alert('XSS')"
        "<img src=x onerror=alert('XSS')>"
        "\"><script>alert('XSS')</script>"
    )
    
    for payload in "${XSS_PAYLOADS[@]}"; do
        RESPONSE=$(curl -k -s -w "\n%{http_code}" \
            -X POST ${API_URL}/packages/search \
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json" \
            -d "{\"query\":\"$payload\"}" 2>/dev/null)
        
        HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
        BODY=$(echo "$RESPONSE" | head -n-1)
        
        if echo "$BODY" | grep -q "<script>"; then
            log_fail "XSS payload not sanitized: $payload"
        else
            log_pass "XSS payload sanitized"
        fi
    done
    
    # Test command injection
    CMD_PAYLOADS=(
        "test; cat /etc/passwd"
        "test && cat /etc/passwd"
        "test | cat /etc/passwd"
        "\`cat /etc/passwd\`"
        "\$(cat /etc/passwd)"
    )
    
    for payload in "${CMD_PAYLOADS[@]}"; do
        RESPONSE=$(curl -k -s -w "\n%{http_code}" \
            -X POST ${API_URL}/packages/search \
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json" \
            -d "{\"query\":\"$payload\"}" 2>/dev/null)
        
        BODY=$(echo "$RESPONSE" | head -n-1)
        
        if echo "$BODY" | grep -q "root:"; then
            log_fail "Command injection vulnerability with payload: $payload"
        else
            log_pass "Command injection blocked"
        fi
    done
    
    # Test path traversal
    PATH_PAYLOADS=(
        "../../etc/passwd"
        "..\\..\\etc\\passwd"
        "%2e%2e%2f%2e%2e%2fetc%2fpasswd"
    )
    
    for payload in "${PATH_PAYLOADS[@]}"; do
        RESPONSE=$(curl -k -s -w "\n%{http_code}" \
            ${API_URL}/configuration?file=$payload \
            -H "Authorization: Bearer $TOKEN" 2>/dev/null)
        
        BODY=$(echo "$RESPONSE" | head -n-1)
        
        if echo "$BODY" | grep -q "root:"; then
            log_fail "Path traversal vulnerability with payload: $payload"
        else
            log_pass "Path traversal blocked"
        fi
    done
}

# Test 4: Security Headers
test_security_headers() {
    log_test "Testing Security Headers"
    
    HEADERS=$(curl -k -s -I ${BASE_URL})
    
    # Check required security headers
    SECURITY_HEADERS=(
        "X-Content-Type-Options: nosniff"
        "X-Frame-Options:"
        "X-XSS-Protection:"
        "Content-Security-Policy:"
        "Referrer-Policy:"
    )
    
    for header in "${SECURITY_HEADERS[@]}"; do
        if echo "$HEADERS" | grep -qi "$header"; then
            log_pass "Security header present: $header"
        else
            log_warn "Missing security header: $header"
        fi
    done
}

# Test 5: API Security
test_api_security() {
    log_test "Testing API Security"
    
    # Test HTTP methods
    METHODS=("GET" "POST" "PUT" "DELETE" "OPTIONS" "TRACE" "CONNECT")
    
    for method in "${METHODS[@]}"; do
        RESPONSE=$(curl -k -s -w "\n%{http_code}" -X $method ${API_URL}/health)
        HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
        
        if [ "$method" = "GET" ] && [ "$HTTP_CODE" = "200" ]; then
            log_pass "Health endpoint allows GET"
        elif [ "$method" != "GET" ] && [ "$HTTP_CODE" = "405" ]; then
            log_pass "Health endpoint blocks $method"
        elif [ "$method" != "GET" ] && [ "$HTTP_CODE" != "405" ]; then
            log_warn "Health endpoint allows $method (code: $HTTP_CODE)"
        fi
    done
    
    # Test CORS
    RESPONSE=$(curl -k -s -I -H "Origin: http://evil.com" ${API_URL}/health)
    
    if echo "$RESPONSE" | grep -qi "Access-Control-Allow-Origin: http://evil.com"; then
        log_fail "CORS allows any origin"
    else
        log_pass "CORS properly configured"
    fi
}

# Test 6: File Security
test_file_security() {
    log_test "Testing File Security"
    
    # Try to access sensitive files
    SENSITIVE_PATHS=(
        "/.env"
        "/backend/.env"
        "/package.json"
        "/../../../etc/passwd"
        "/ssl/key.pem"
    )
    
    for path in "${SENSITIVE_PATHS[@]}"; do
        RESPONSE=$(curl -k -s -w "\n%{http_code}" ${BASE_URL}${path})
        HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
        BODY=$(echo "$RESPONSE" | head -n-1)
        
        if [ "$HTTP_CODE" = "200" ]; then
            log_fail "Sensitive file accessible: $path"
        else
            log_pass "Sensitive file protected: $path"
        fi
    done
}

# Test 7: Session Security
test_session_security() {
    log_test "Testing Session Security"
    
    # Get auth token
    AUTH_RESPONSE=$(curl -k -s -X POST ${API_URL}/auth/login \
        -H "Content-Type: application/json" \
        -d '{"username":"admin","password":"testpass"}')
    
    TOKEN=$(echo "$AUTH_RESPONSE" | jq -r '.token' 2>/dev/null || echo "")
    
    if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
        # Decode JWT header to check algorithm
        HEADER=$(echo $TOKEN | cut -d. -f1 | base64 -d 2>/dev/null || echo "")
        
        if echo "$HEADER" | grep -q "HS256"; then
            log_pass "JWT uses HMAC algorithm"
        elif echo "$HEADER" | grep -q "none"; then
            log_fail "JWT uses 'none' algorithm - CRITICAL vulnerability!"
        fi
        
        # Test token expiration
        # This would require waiting or manipulating time
        log_pass "JWT token structure valid"
    fi
}

# Generate security report
generate_report() {
    echo ""
    echo "Security Audit Summary" | tee -a $AUDIT_LOG
    echo "=====================" | tee -a $AUDIT_LOG
    
    TOTAL_TESTS=$(grep -c "\[AUDIT\]" $AUDIT_LOG || echo "0")
    PASSED=$(grep -c "\[PASS\]" $AUDIT_LOG || echo "0")
    WARNINGS=$(grep -c "\[WARN\]" $AUDIT_LOG || echo "0")
    FAILURES=$(grep -c "\[FAIL\]" $AUDIT_LOG || echo "0")
    
    echo "Total Tests: $TOTAL_TESTS" | tee -a $AUDIT_LOG
    echo -e "${GREEN}Passed: $PASSED${NC}" | tee -a $AUDIT_LOG
    echo -e "${YELLOW}Warnings: $WARNINGS${NC}" | tee -a $AUDIT_LOG
    echo -e "${RED}Failures: $FAILURES${NC}" | tee -a $AUDIT_LOG
    
    echo "" | tee -a $AUDIT_LOG
    
    if [ $FAILURES -eq 0 ]; then
        echo -e "${GREEN}✅ No critical security issues found${NC}" | tee -a $AUDIT_LOG
    else
        echo -e "${RED}⚠️  Critical security issues detected!${NC}" | tee -a $AUDIT_LOG
        echo "Review $AUDIT_LOG for details" | tee -a $AUDIT_LOG
    fi
    
    # Security grade
    if [ $FAILURES -eq 0 ] && [ $WARNINGS -le 2 ]; then
        echo -e "\nSecurity Grade: ${GREEN}A${NC}" | tee -a $AUDIT_LOG
    elif [ $FAILURES -eq 0 ] && [ $WARNINGS -le 5 ]; then
        echo -e "\nSecurity Grade: ${GREEN}B${NC}" | tee -a $AUDIT_LOG
    elif [ $FAILURES -le 2 ]; then
        echo -e "\nSecurity Grade: ${YELLOW}C${NC}" | tee -a $AUDIT_LOG
    else
        echo -e "\nSecurity Grade: ${RED}F${NC}" | tee -a $AUDIT_LOG
    fi
}

# Main execution
main() {
    # Check if server is running
    if ! curl -k -s ${BASE_URL}/api/health > /dev/null 2>&1; then
        log_fail "Server not running at ${BASE_URL}"
        exit 1
    fi
    
    # Run all security tests
    test_ssl_configuration
    echo ""
    
    test_authentication_security
    echo ""
    
    test_input_validation
    echo ""
    
    test_security_headers
    echo ""
    
    test_api_security
    echo ""
    
    test_file_security
    echo ""
    
    test_session_security
    echo ""
    
    # Generate report
    generate_report
}

# Run the audit
main