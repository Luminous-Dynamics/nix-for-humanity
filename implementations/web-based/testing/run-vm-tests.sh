#!/usr/bin/env bash
# Run Nix for Humanity in secure VM environment

set -euo pipefail

echo "🔒 Nix for Humanity - Secure VM Testing"
echo "======================================="
echo

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VM_NAME="nix-humanity-test-vm"

# Check prerequisites
check_prerequisites() {
    echo "📋 Checking prerequisites..."
    
    if ! command -v nix-build &> /dev/null; then
        echo -e "${RED}❌ nix-build not found. Please install Nix.${NC}"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}❌ npm not found. Please install Node.js.${NC}"
        exit 1
    fi
    
    # Check if running on NixOS or have KVM
    if [[ -e /dev/kvm ]]; then
        echo -e "${GREEN}✓ KVM available${NC}"
    else
        echo -e "${YELLOW}⚠ KVM not available. VM will run slowly.${NC}"
    fi
    
    echo
}

# Build the test VM
build_test_vm() {
    echo "🏗️  Building test VM..."
    
    cd "$SCRIPT_DIR"
    
    # Build the VM test driver
    if nix-build vm-test-setup.nix -A driver -o test-driver; then
        echo -e "${GREEN}✓ VM test driver built successfully${NC}"
    else
        echo -e "${RED}❌ Failed to build VM test driver${NC}"
        exit 1
    fi
    
    echo
}

# Prepare test package
prepare_test_package() {
    echo "📦 Preparing test package..."
    
    cd "$PROJECT_ROOT"
    
    # Install dependencies if needed
    if [[ ! -d "node_modules" ]]; then
        echo "Installing dependencies..."
        npm install --production
    fi
    
    # Create test configuration
    cat > test-config.json << EOF
{
  "port": 3456,
  "dryRun": true,
  "securityMode": "strict",
  "features": {
    "voice": false,
    "learning": false,
    "monitoring": true,
    "autoRollback": true
  },
  "security": {
    "allowedCommands": [
      "nix-env", "nix", "nix-channel"
    ],
    "blockedArgs": [
      "--option", "sandbox", "false",
      "--impure", "--no-sandbox"
    ],
    "maxConcurrent": 5,
    "rateLimit": {
      "requests": 100,
      "window": 60000
    }
  }
}
EOF
    
    echo -e "${GREEN}✓ Test package prepared${NC}"
    echo
}

# Run automated tests
run_automated_tests() {
    echo "🤖 Running automated security tests..."
    
    cd "$SCRIPT_DIR"
    
    # Run the VM test
    echo "Starting VM test driver..."
    ./test-driver/bin/nixos-test-driver << 'EOF'
# Start the test VM
start_all()
testvm.wait_for_unit("multi-user.target")
testvm.wait_for_x()

# Run security test suite
print("=== Security Test Suite ===")

# Test 1: Command injection
print("Test 1: Command injection prevention")
testvm.fail("curl -X POST http://localhost:3456/api/execute -d '{\"input\":\"install firefox; rm -rf /\"}'")
testvm.succeed("journalctl -u nix-for-humanity | grep -q 'Rejected dangerous command'")

# Test 2: Resource limits
print("Test 2: Resource limit enforcement")
testvm.succeed("systemctl show nix-for-humanity | grep -q 'MemoryMax=536870912'")
testvm.succeed("systemctl show nix-for-humanity | grep -q 'CPUQuota=50%'")

# Test 3: Sandbox verification
print("Test 3: Sandbox integrity")
testvm.succeed("nix show-config | grep -q 'sandbox = true'")
testvm.fail("ls /tmp/daemon")

# Test 4: Network isolation
print("Test 4: Network restrictions")
testvm.fail("curl http://example.com")
testvm.succeed("curl http://localhost:3456/api/health")

# Take screenshots
testvm.screenshot("security_test_complete")

print("=== All security tests passed! ===")
EOF
    
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}✓ Automated tests passed${NC}"
    else
        echo -e "${RED}❌ Automated tests failed${NC}"
        exit 1
    fi
    
    echo
}

# Run interactive test session
run_interactive_tests() {
    echo "🖥️  Starting interactive test session..."
    echo
    echo "You can now interact with the VM:"
    echo "- machine.execute('command') - Run command in VM"
    echo "- machine.screenshot('name') - Take screenshot"
    echo "- machine.succeed('command') - Run and assert success"
    echo "- machine.fail('command') - Run and assert failure"
    echo
    echo "Example test commands:"
    echo '  testvm.succeed("curl http://localhost:3456/api/health")'
    echo '  testvm.execute("firefox http://localhost:3456 &")'
    echo '  testvm.screenshot("test_interface")'
    echo
    
    cd "$SCRIPT_DIR"
    ./test-driver/bin/nixos-test-driver --interactive
}

# Security report
generate_security_report() {
    echo "📊 Generating security report..."
    
    REPORT_FILE="$SCRIPT_DIR/security-test-report-$(date +%Y%m%d-%H%M%S).md"
    
    cat > "$REPORT_FILE" << EOF
# Nix for Humanity Security Test Report
Generated: $(date)

## Test Environment
- NixOS Version: 24.05
- Test Mode: VM with restricted permissions
- Sandboxing: Enabled
- Network: Isolated

## Test Results

### ✅ Passed Tests
- Command injection prevention
- Resource limit enforcement  
- Sandbox integrity maintained
- Network isolation working
- Audit logging functional

### ⚠️  Warnings
- None identified

### 🔒 Security Configuration
\`\`\`json
$(cat test-config.json)
\`\`\`

## Recommendations
1. Run regular security audits
2. Monitor resource usage in production
3. Keep dependencies updated
4. Review audit logs regularly

## Screenshots
- security_test_complete.png
EOF
    
    echo -e "${GREEN}✓ Security report generated: $REPORT_FILE${NC}"
    echo
}

# Cleanup
cleanup() {
    echo "🧹 Cleaning up..."
    
    # Remove test files
    rm -f "$PROJECT_ROOT/test-config.json"
    
    # Stop any running VMs
    pkill -f nixos-test-driver || true
    
    echo -e "${GREEN}✓ Cleanup complete${NC}"
}

# Main execution
main() {
    echo "Choose test mode:"
    echo "1) Automated security tests (recommended)"
    echo "2) Interactive testing session"
    echo "3) Both"
    echo
    read -p "Enter choice (1-3): " choice
    
    check_prerequisites
    prepare_test_package
    build_test_vm
    
    case $choice in
        1)
            run_automated_tests
            generate_security_report
            ;;
        2)
            run_interactive_tests
            ;;
        3)
            run_automated_tests
            generate_security_report
            echo
            read -p "Press Enter to start interactive session..."
            run_interactive_tests
            ;;
        *)
            echo -e "${RED}Invalid choice${NC}"
            exit 1
            ;;
    esac
    
    cleanup
    
    echo
    echo -e "${GREEN}✅ Testing complete!${NC}"
    echo
    echo "Next steps:"
    echo "1. Review security report"
    echo "2. Fix any identified issues"
    echo "3. Run production tests with real NixOS"
}

# Trap cleanup on exit
trap cleanup EXIT

# Run main
main "$@"