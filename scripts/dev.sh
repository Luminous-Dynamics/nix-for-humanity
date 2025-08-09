#!/usr/bin/env bash
# Development helper script for Nix for Humanity
# Uses flakes for all operations

set -euo pipefail

# Enable flakes for this script
export NIX_CONFIG="experimental-features = nix-command flakes"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Help function
show_help() {
    echo -e "${BLUE}Nix for Humanity Development Helper${NC}"
    echo
    echo "Usage: ./dev.sh <command> [args]"
    echo
    echo "Commands:"
    echo "  shell       - Enter development shell with all dependencies"
    echo ""
    echo "Testing:"
    echo "  test        - Run all tests (Python + TypeScript)"
    echo "  test-cov    - Run tests with coverage report"
    echo "  test-unit   - Run only unit tests"
    echo "  test-int    - Run only integration tests"
    echo "  test-e2e    - Run only E2E tests"
    echo "  test-watch  - Run tests in watch mode"
    echo "  test-ts     - Run TypeScript tests"
    echo ""
    echo "Code Quality:"
    echo "  lint        - Run all linters (Python + TypeScript)"
    echo "  lint-py     - Run Python linters (ruff, mypy)"
    echo "  lint-ts     - Run TypeScript linter (eslint)"
    echo "  format      - Format all code (Python + TypeScript)"
    echo "  format-py   - Format Python code with black"
    echo "  format-ts   - Format TypeScript code with prettier"
    echo "  typecheck   - Run TypeScript type checking"
    echo ""
    echo "Build:"
    echo "  build       - Build all TypeScript implementations"
    echo "  build-web   - Build web-based implementation"
    echo "  build-mvp   - Build nodejs-mvp implementation"
    echo "  clean       - Clean all build artifacts"
    echo ""
    echo "System:"
    echo "  update      - Update flake inputs"
    echo "  show        - Show flake info"
    echo "  run <cmd>   - Run command in nix develop environment"
    echo
    echo "Examples:"
    echo "  ./dev.sh shell"
    echo "  ./dev.sh test"
    echo "  ./dev.sh run python -m pytest tests/unit/"
}

# Check if nix is available
check_nix() {
    if ! command -v nix &> /dev/null; then
        echo -e "${RED}Error: nix is not installed${NC}"
        echo "Please install Nix: https://nixos.org/download.html"
        exit 1
    fi
}

# Main command handler
main() {
    check_nix
    
    case "${1:-help}" in
        shell)
            echo -e "${GREEN}Entering Nix development shell...${NC}"
            nix develop
            ;;
        
        test)
            echo -e "${GREEN}Running all tests...${NC}"
            nix develop -c pytest tests/ -v
            ;;
        
        test-cov)
            echo -e "${GREEN}Running tests with coverage...${NC}"
            nix develop -c pytest tests/ --cov=src --cov-report=html --cov-report=term
            echo -e "${BLUE}Coverage report generated in htmlcov/index.html${NC}"
            ;;
        
        test-unit)
            echo -e "${GREEN}Running unit tests...${NC}"
            nix develop -c pytest tests/unit/ -v
            ;;
        
        test-int)
            echo -e "${GREEN}Running integration tests...${NC}"
            nix develop -c pytest tests/integration/ -v
            ;;
        
        test-e2e)
            echo -e "${GREEN}Running E2E tests...${NC}"
            nix develop -c pytest tests/e2e/ -v
            ;;
        
        test-watch)
            echo -e "${GREEN}Running tests in watch mode...${NC}"
            nix develop -c pytest-watch tests/ -v
            ;;
        
        test-ts)
            echo -e "${GREEN}Running TypeScript tests...${NC}"
            nix develop -c bash -c "cd implementations/web-based && npm test"
            nix develop -c bash -c "cd implementations/nodejs-mvp && npm test"
            ;;
        
        lint)
            echo -e "${GREEN}Running all linters...${NC}"
            nix develop -c bash -c "ruff check src/ tests/ && mypy src/ && ./dev.sh lint-ts"
            ;;
        
        lint-py)
            echo -e "${GREEN}Running Python linters...${NC}"
            nix develop -c bash -c "ruff check src/ tests/ && mypy src/"
            ;;
        
        lint-ts)
            echo -e "${GREEN}Running TypeScript linter...${NC}"
            nix develop -c bash -c "cd implementations/web-based && npm run lint"
            nix develop -c bash -c "cd implementations/nodejs-mvp && npm run lint"
            ;;
        
        format)
            echo -e "${GREEN}Formatting all code...${NC}"
            nix develop -c bash -c "black src/ tests/ && ./dev.sh format-ts"
            ;;
        
        format-py)
            echo -e "${GREEN}Formatting Python code...${NC}"
            nix develop -c black src/ tests/
            ;;
        
        format-ts)
            echo -e "${GREEN}Formatting TypeScript code...${NC}"
            nix develop -c bash -c "cd implementations/web-based && npm run format"
            nix develop -c bash -c "cd implementations/nodejs-mvp && npm run format"
            ;;
        
        typecheck)
            echo -e "${GREEN}Running TypeScript type checking...${NC}"
            nix develop -c bash -c "cd implementations/web-based && npm run typecheck"
            nix develop -c bash -c "cd implementations/nodejs-mvp && npm run typecheck"
            ;;
        
        build)
            echo -e "${GREEN}Building all TypeScript implementations...${NC}"
            ./dev.sh build-web
            ./dev.sh build-mvp
            ;;
        
        build-web)
            echo -e "${GREEN}Building web-based implementation...${NC}"
            echo -e "${BLUE}  Installing dependencies...${NC}"
            nix develop -c bash -c "cd implementations/web-based && npm install --silent"
            echo -e "${BLUE}  Running TypeScript type checking...${NC}"
            nix develop -c bash -c "cd implementations/web-based && npm run typecheck"
            echo -e "${BLUE}  Building with esbuild...${NC}"
            nix develop -c bash -c "cd implementations/web-based && npm run build"
            echo -e "${GREEN}✅ Web-based implementation built successfully${NC}"
            ;;
        
        build-mvp)
            echo -e "${GREEN}Building nodejs-mvp implementation...${NC}"
            echo -e "${BLUE}  Installing dependencies...${NC}"
            nix develop -c bash -c "cd implementations/nodejs-mvp && npm install --silent"
            echo -e "${BLUE}  Running TypeScript type checking...${NC}"
            nix develop -c bash -c "cd implementations/nodejs-mvp && npm run typecheck"
            echo -e "${BLUE}  Building with esbuild...${NC}"
            nix develop -c bash -c "cd implementations/nodejs-mvp && npm run build"
            echo -e "${GREEN}✅ NodeJS-MVP implementation built successfully${NC}"
            ;;
        
        clean)
            echo -e "${GREEN}Cleaning all build artifacts...${NC}"
            nix develop -c bash -c "cd implementations/web-based && rm -rf dist/ build/ node_modules/.cache/"
            nix develop -c bash -c "cd implementations/nodejs-mvp && rm -rf dist/ build/ node_modules/.cache/"
            echo -e "${BLUE}Build artifacts cleaned${NC}"
            ;;
        
        update)
            echo -e "${GREEN}Updating flake inputs...${NC}"
            nix flake update
            ;;
        
        show)
            echo -e "${GREEN}Showing flake info...${NC}"
            nix flake show
            nix flake metadata
            ;;
        
        run)
            shift
            echo -e "${GREEN}Running in nix develop: $@${NC}"
            nix develop -c "$@"
            ;;
        
        help|--help|-h)
            show_help
            ;;
        
        *)
            echo -e "${RED}Unknown command: $1${NC}"
            echo
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"