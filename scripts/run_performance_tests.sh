#!/usr/bin/env bash
"""
Performance Test Runner Script for Nix for Humanity

Quick script to run performance tests and validate the Native Python-Nix
Interface breakthrough metrics.
"""

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Nix for Humanity - Performance Test Runner${NC}"
echo "=============================================="

# Check if we're in the right directory
if [[ ! -f "tests/performance/run_performance_tests.py" ]]; then
    echo -e "${RED}❌ Error: Must be run from the project root directory${NC}"
    exit 1
fi

# Make sure Python backend is available
echo -e "${BLUE}📋 Checking prerequisites...${NC}"

if [[ ! -d "backend/python" ]]; then
    echo -e "${YELLOW}⚠️  Warning: Python backend directory not found${NC}"
fi

# Set up environment
export PYTHONPATH="$PWD:$PWD/backend/python:$PYTHONPATH"

# Check if Python dependencies are available
python3 -c "import sys; print('Python:', sys.version)" || {
    echo -e "${RED}❌ Error: Python 3 not available${NC}"
    exit 1
}

# Parse command line arguments
VERBOSE=true
OUTPUT_DIR=""
JSON_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --quiet|-q)
            VERBOSE=false
            shift
            ;;
        --output-dir|-o)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --json-only|-j)
            JSON_ONLY=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --quiet, -q       Reduce output verbosity"
            echo "  --output-dir, -o  Directory for test reports"
            echo "  --json-only, -j   Output only JSON results"
            echo "  --help, -h        Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Build command
CMD="python3 tests/performance/run_performance_tests.py"

if [[ -n "$OUTPUT_DIR" ]]; then
    CMD="$CMD --output-dir $OUTPUT_DIR"
fi

if [[ "$VERBOSE" == "false" ]]; then
    CMD="$CMD --quiet"
fi

if [[ "$JSON_ONLY" == "true" ]]; then
    CMD="$CMD --json-only"
fi

# Run the tests
echo -e "${BLUE}🧪 Running performance tests...${NC}"
echo "Command: $CMD"
echo ""

if $CMD; then
    echo ""
    echo -e "${GREEN}✅ Performance tests completed successfully!${NC}"
    echo -e "${GREEN}🚀 Native Python-Nix Interface performance verified!${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}❌ Performance tests failed!${NC}"
    echo -e "${YELLOW}💡 Check the output above for details${NC}"
    exit 1
fi