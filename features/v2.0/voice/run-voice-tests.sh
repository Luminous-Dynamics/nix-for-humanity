#!/usr/bin/env bash
# 🎯 Voice Testing Runner Script
# 
# Comprehensive test runner for the voice interface system with performance
# monitoring, coverage reporting, and persona-specific validation.

set -euo pipefail

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VOICE_TESTS_DIR="$PROJECT_ROOT/tests/voice"
COVERAGE_DIR="$PROJECT_ROOT/.coverage_voice"
RESULTS_DIR="$PROJECT_ROOT/test-results/voice"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test suite configurations
declare -A TEST_SUITES=(
    ["integration"]="test_voice_integration.py"
    ["performance"]="test_voice_performance.py"
    ["unit"]="test_model_manager.py"
)

# Persona-specific test configurations
declare -A PERSONA_TESTS=(
    ["maya"]="test_maya_adhd_requirements"
    ["grandma"]="test_grandma_rose_accessibility"
    ["alex"]="test_alex_blind_screen_reader"
    ["all_personas"]="test_.*_persona.*"
)

# Performance benchmark configurations
declare -A PERFORMANCE_TESTS=(
    ["benchmarks"]="TestVoicePerformanceBenchmarks"
    ["scalability"]="TestVoiceScalabilityBenchmarks"
    ["memory"]="test_memory_leak_detection"
    ["concurrent"]="test_concurrent_voice_requests"
)

usage() {
    echo "🎯 Voice Testing Runner"
    echo ""
    echo "Usage: $0 [OPTIONS] [TEST_TYPE]"
    echo ""
    echo "Test Types:"
    echo "  integration    - Voice integration tests"
    echo "  performance    - Performance benchmarks"
    echo "  unit          - Unit tests for voice components"
    echo "  persona <name> - Test specific persona requirements"
    echo "  all           - Run all test suites"
    echo ""
    echo "Persona Names:"
    echo "  maya          - Maya (ADHD) <1s response requirements"
    echo "  grandma       - Grandma Rose accessibility tests"
    echo "  alex          - Alex (Blind) screen reader tests"
    echo "  all_personas  - All persona validation tests"
    echo ""
    echo "Performance Tests:"
    echo "  benchmarks    - Core performance benchmarks"
    echo "  scalability   - Load and scalability tests"
    echo "  memory        - Memory leak detection"
    echo "  concurrent    - Concurrent request handling"
    echo ""
    echo "Options:"
    echo "  -v, --verbose     Verbose output"
    echo "  -c, --coverage    Generate coverage report"
    echo "  -f, --fail-fast   Stop on first failure"
    echo "  -m, --mock        Run with mocked dependencies"
    echo "  -r, --report      Generate detailed HTML report"
    echo "  -h, --help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 integration           # Run integration tests"
    echo "  $0 persona maya          # Test Maya's ADHD requirements"
    echo "  $0 performance benchmarks # Run performance benchmarks"
    echo "  $0 -c -r all            # Run all tests with coverage and reporting"
}

log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

check_dependencies() {
    log "Checking dependencies..."
    
    # Check Python environment
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is required but not installed"
    fi
    
    # Check pytest
    if ! python3 -c "import pytest" 2>/dev/null; then
        error "pytest is required. Install with: pip install pytest"
    fi
    
    # Check coverage tool
    if [[ "$GENERATE_COVERAGE" == "true" ]] && ! python3 -c "import coverage" 2>/dev/null; then
        warning "coverage.py not found. Install with: pip install coverage"
        GENERATE_COVERAGE="false"
    fi
    
    # Check test directories exist
    if [[ ! -d "$VOICE_TESTS_DIR" ]]; then
        error "Voice tests directory not found: $VOICE_TESTS_DIR"
    fi
    
    success "Dependencies check passed"
}

setup_environment() {
    log "Setting up test environment..."
    
    # Create results directory
    mkdir -p "$RESULTS_DIR"
    mkdir -p "$COVERAGE_DIR"
    
    # Set environment variables for testing
    export PYTHONPATH="$PROJECT_ROOT/src:$PROJECT_ROOT:$PYTHONPATH"
    export NIX_HUMANITY_TEST_MODE=true
    export NIX_HUMANITY_MOCK_NIXOS=true
    
    # Mock mode configuration
    if [[ "$USE_MOCKS" == "true" ]]; then
        export PIPECAT_AVAILABLE=false
        export NIX_HUMANITY_VOICE_MOCK=true
        log "Running in mock mode (no real pipecat/models required)"
    else
        log "Running with real dependencies (pipecat integration active)"
    fi
    
    success "Environment setup complete"
}

run_test_suite() {
    local suite_name="$1"
    local test_file="$2"
    local pytest_args=("${@:3}")
    
    log "Running $suite_name tests..."
    
    local cmd=(python3 -m pytest)
    
    # Add coverage if requested
    if [[ "$GENERATE_COVERAGE" == "true" ]]; then
        cmd+=(--cov=nix_for_humanity.voice --cov-append)
        cmd+=(--cov-report=term-missing --cov-report=html:"$COVERAGE_DIR/html")
    fi
    
    # Add common pytest arguments
    cmd+=(-v --tb=short)
    
    # Add fail-fast if requested
    if [[ "$FAIL_FAST" == "true" ]]; then
        cmd+=(-x)
    fi
    
    # Add verbose output if requested
    if [[ "$VERBOSE" == "true" ]]; then
        cmd+=(-s)
    fi
    
    # Add custom pytest arguments
    cmd+=("${pytest_args[@]}")
    
    # Add test file
    cmd+=("$VOICE_TESTS_DIR/$test_file")
    
    log "Executing: ${cmd[*]}"
    
    if "${cmd[@]}"; then
        success "$suite_name tests passed"
        return 0
    else
        error "$suite_name tests failed"
        return 1
    fi
}

run_integration_tests() {
    log "🔗 Running Voice Integration Tests"
    run_test_suite "Integration" "${TEST_SUITES[integration]}" -m "not performance"
}

run_performance_tests() {
    local test_type="${1:-benchmarks}"
    
    log "⚡ Running Voice Performance Tests: $test_type"
    
    case "$test_type" in
        "benchmarks")
            run_test_suite "Performance Benchmarks" "${TEST_SUITES[performance]}" \
                -m "performance" -k "${PERFORMANCE_TESTS[benchmarks]}"
            ;;
        "scalability")
            run_test_suite "Scalability Tests" "${TEST_SUITES[performance]}" \
                -m "performance" -k "${PERFORMANCE_TESTS[scalability]}"
            ;;
        "memory")
            run_test_suite "Memory Tests" "${TEST_SUITES[performance]}" \
                -m "performance" -k "${PERFORMANCE_TESTS[memory]}"
            ;;
        "concurrent")
            run_test_suite "Concurrent Tests" "${TEST_SUITES[performance]}" \
                -m "performance" -k "${PERFORMANCE_TESTS[concurrent]}"
            ;;
        *)
            run_test_suite "Performance" "${TEST_SUITES[performance]}" -m "performance"
            ;;
    esac
}

run_unit_tests() {
    log "🧪 Running Voice Unit Tests"
    run_test_suite "Unit" "${TEST_SUITES[unit]}"
}

run_persona_tests() {
    local persona="${1:-all_personas}"
    
    log "👥 Running Persona Tests: $persona"
    
    case "$persona" in
        "maya")
            run_test_suite "Maya (ADHD) Tests" "${TEST_SUITES[integration]}" \
                -k "${PERSONA_TESTS[maya]}"
            ;;
        "grandma")
            run_test_suite "Grandma Rose Tests" "${TEST_SUITES[integration]}" \
                -k "${PERSONA_TESTS[grandma]}"
            ;;
        "alex")
            run_test_suite "Alex (Blind) Tests" "${TEST_SUITES[integration]}" \
                -k "${PERSONA_TESTS[alex]}"
            ;;
        "all_personas")
            run_test_suite "All Persona Tests" "${TEST_SUITES[integration]}" \
                -k "${PERSONA_TESTS[all_personas]}"
            ;;
        *)
            error "Unknown persona: $persona. Use: maya, grandma, alex, or all_personas"
            ;;
    esac
}

run_all_tests() {
    log "🚀 Running All Voice Tests"
    
    local failed_suites=()
    
    # Run unit tests first
    if ! run_unit_tests; then
        failed_suites+=("unit")
    fi
    
    # Run integration tests
    if ! run_integration_tests; then
        failed_suites+=("integration")
    fi
    
    # Run persona tests
    if ! run_persona_tests "all_personas"; then
        failed_suites+=("personas")
    fi
    
    # Run performance tests (only if not in mock mode)
    if [[ "$USE_MOCKS" != "true" ]]; then
        if ! run_performance_tests; then
            failed_suites+=("performance")
        fi
    else
        warning "Skipping performance tests in mock mode"
    fi
    
    # Report results
    if [[ ${#failed_suites[@]} -eq 0 ]]; then
        success "🎉 All voice test suites passed!"
        return 0
    else
        error "❌ Failed test suites: ${failed_suites[*]}"
        return 1
    fi
}

generate_report() {
    if [[ "$GENERATE_REPORT" != "true" ]]; then
        return 0
    fi
    
    log "📊 Generating test report..."
    
    # Create comprehensive test report
    cat > "$RESULTS_DIR/voice-test-report.html" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Voice Interface Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #2196F3; color: white; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .success { background: #E8F5E8; border-color: #4CAF50; }
        .warning { background: #FFF3E0; border-color: #FF9800; }
        .error { background: #FFEBEE; border-color: #F44336; }
        .code { font-family: monospace; background: #f5f5f5; padding: 5px; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Voice Interface Test Report</h1>
        <p>Generated: $(date)</p>
    </div>
EOF
    
    # Add coverage information if available
    if [[ "$GENERATE_COVERAGE" == "true" ]] && [[ -f "$COVERAGE_DIR/html/index.html" ]]; then
        echo '<div class="section success">' >> "$RESULTS_DIR/voice-test-report.html"
        echo '<h2>📊 Coverage Report</h2>' >> "$RESULTS_DIR/voice-test-report.html"
        echo '<p>Detailed coverage report: <a href="../.coverage_voice/html/index.html">View Coverage</a></p>' >> "$RESULTS_DIR/voice-test-report.html"
        echo '</div>' >> "$RESULTS_DIR/voice-test-report.html"
    fi
    
    echo '</body></html>' >> "$RESULTS_DIR/voice-test-report.html"
    
    success "Test report generated: $RESULTS_DIR/voice-test-report.html"
}

cleanup() {
    log "🧹 Cleaning up test environment..."
    
    # Remove temporary test files
    find "$PROJECT_ROOT" -name "*.pyc" -delete 2>/dev/null || true
    find "$PROJECT_ROOT" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    
    # Clean up test databases
    rm -f "$PROJECT_ROOT"/*.test.db 2>/dev/null || true
    
    success "Cleanup complete"
}

main() {
    # Default values
    VERBOSE=false
    GENERATE_COVERAGE=false
    FAIL_FAST=false
    USE_MOCKS=false
    GENERATE_REPORT=false
    TEST_TYPE=""
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -c|--coverage)
                GENERATE_COVERAGE=true
                shift
                ;;
            -f|--fail-fast)
                FAIL_FAST=true
                shift
                ;;
            -m|--mock)
                USE_MOCKS=true
                shift
                ;;
            -r|--report)
                GENERATE_REPORT=true
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                if [[ -z "$TEST_TYPE" ]]; then
                    TEST_TYPE="$1"
                elif [[ "$TEST_TYPE" == "persona" ]] || [[ "$TEST_TYPE" == "performance" ]]; then
                    TEST_SUBTYPE="$1"
                else
                    error "Unknown argument: $1"
                fi
                shift
                ;;
        esac
    done
    
    # Default to integration tests if no type specified
    if [[ -z "$TEST_TYPE" ]]; then
        TEST_TYPE="integration"
    fi
    
    # Setup trap for cleanup
    trap cleanup EXIT
    
    # Run setup
    check_dependencies
    setup_environment
    
    # Execute tests based on type
    case "$TEST_TYPE" in
        "integration")
            run_integration_tests
            ;;
        "performance")
            run_performance_tests "${TEST_SUBTYPE:-benchmarks}"
            ;;
        "unit")
            run_unit_tests
            ;;
        "persona")
            run_persona_tests "${TEST_SUBTYPE:-all_personas}"
            ;;
        "all")
            run_all_tests
            ;;
        *)
            error "Unknown test type: $TEST_TYPE. Use --help for available options."
            ;;
    esac
    
    # Generate report if requested
    generate_report
    
    success "🎉 Voice test execution complete!"
}

# Run main function with all arguments
main "$@"