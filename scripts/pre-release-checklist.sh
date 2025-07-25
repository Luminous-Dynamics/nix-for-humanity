#!/usr/bin/env bash
set -euo pipefail

# Pre-release checklist script
# Ensures everything is ready before creating a release

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Status tracking
FAILED_CHECKS=0

# Check function
check() {
    local name="$1"
    local cmd="$2"
    
    echo -n "Checking $name... "
    
    if eval "$cmd" &> /dev/null; then
        echo -e "${GREEN}✓${NC}"
        return 0
    else
        echo -e "${RED}✗${NC}"
        ((FAILED_CHECKS++))
        return 1
    fi
}

# Detailed check function
check_with_output() {
    local name="$1"
    shift
    
    echo -e "\n${YELLOW}Checking $name...${NC}"
    
    if "$@"; then
        echo -e "${GREEN}✓ $name passed${NC}"
        return 0
    else
        echo -e "${RED}✗ $name failed${NC}"
        ((FAILED_CHECKS++))
        return 1
    fi
}

echo "🔍 Pre-Release Checklist for NixOS GUI"
echo "====================================="

cd "$PROJECT_ROOT"

# Git checks
echo -e "\n📋 Git Status"
check "Clean working directory" "[ -z \"\$(git status --porcelain)\" ]"
check "On main branch" "[ \"\$(git branch --show-current)\" = \"main\" ]"
check "Up to date with remote" "git fetch --dry-run 2>&1 | grep -q 'up to date'"

# Dependency checks
echo -e "\n📦 Dependencies"
check "No npm vulnerabilities" "npm audit --production --audit-level=high"
check "Dependencies up to date" "[ -z \"\$(npm outdated --parseable)\" ]"

# Code quality checks
echo -e "\n✨ Code Quality"
check_with_output "ESLint" npm run lint
check_with_output "Prettier" npm run prettier:check
check_with_output "Type checking" npm run type-check

# Test suite
echo -e "\n🧪 Test Suite"
check_with_output "Unit tests" npm test
check_with_output "Integration tests" npm run test:integration

# Build checks
echo -e "\n🔨 Build"
check_with_output "Production build" npm run build:production
check "Bundle size within limit" "[ \$(du -sb dist | cut -f1) -lt 10485760 ]"  # 10MB limit

# Documentation checks
echo -e "\n📚 Documentation"
check "README exists" "[ -f README.md ]"
check "CHANGELOG exists" "[ -f CHANGELOG.md ]"
check "LICENSE exists" "[ -f LICENSE ]"
check "All docs present" "[ -d docs ] && [ \$(ls docs/*.md | wc -l) -ge 8 ]"

# Nix checks
echo -e "\n❄️  Nix"
if command -v nix-build &> /dev/null; then
    check "Nix build succeeds" "nix-build --dry-run"
    check "Flake check passes" "nix flake check --no-build"
else
    echo -e "${YELLOW}⚠ Nix not installed, skipping Nix checks${NC}"
fi

# Security checks
echo -e "\n🔒 Security"
check "No hardcoded secrets" "! grep -r \"password\\|secret\\|key\" --include=\"*.js\" --include=\"*.json\" --exclude-dir=node_modules --exclude-dir=docs . | grep -v \"password:\\|secret:\\|key:\""
check "Environment files ignored" "grep -q \"^\\.env\" .gitignore"

# Version consistency
echo -e "\n🏷️  Version Consistency"
MAIN_VERSION=$(jq -r '.version' package.json)
echo "Main version: $MAIN_VERSION"

check "Backend version matches" "[ \"\$(jq -r '.version' backend/package.json)\" = \"$MAIN_VERSION\" ]"
check "Frontend version matches" "[ \"\$(jq -r '.version' frontend/package.json)\" = \"$MAIN_VERSION\" ]"

# Final summary
echo -e "\n======================================="
if [ $FAILED_CHECKS -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Ready for release.${NC}"
    echo
    echo "Next steps:"
    echo "1. Run: ./scripts/release.sh [major|minor|patch]"
    echo "2. Review the generated changelog"
    echo "3. Push changes and tags"
    exit 0
else
    echo -e "${RED}❌ $FAILED_CHECKS checks failed!${NC}"
    echo
    echo "Please fix the issues above before releasing."
    exit 1
fi