#!/usr/bin/env bash
# Release readiness checklist
# Run this before declaring any version "ready"

set -euo pipefail

echo "🚀 NIX FOR HUMANITY RELEASE CHECKLIST"
echo "====================================="
echo ""

# Track pass/fail
PASSED=0
FAILED=0
WARNINGS=0

check_pass() {
    echo "✅ $1"
    ((PASSED++))
}

check_fail() {
    echo "❌ $1"
    ((FAILED++))
}

check_warn() {
    echo "⚠️  $1"
    ((WARNINGS++))
}

# 1. Structure checks
echo "📁 PROJECT STRUCTURE"
echo "-------------------"

ROOT_FILES=$(find . -maxdepth 1 -type f | wc -l)
if [ $ROOT_FILES -lt 15 ]; then
    check_pass "Root directory is clean ($ROOT_FILES files)"
else
    check_fail "Root directory has too many files ($ROOT_FILES, target: <15)"
fi

if [ -d "src/nix_humanity" ]; then
    check_pass "Source code properly organized in src/"
else
    check_fail "Source code not in src/nix_humanity/"
fi

if [ ! -d "backend" ] || [ ! -d "nix_humanity" ]; then
    check_pass "No duplicate backend directories"
else
    check_fail "Duplicate backend directories exist"
fi

echo ""

# 2. Code quality checks
echo "💻 CODE QUALITY"
echo "---------------"

# Check for Python syntax errors
if find src -name "*.py" -exec python -m py_compile {} \; 2>/dev/null; then
    check_pass "All Python files compile"
else
    check_fail "Python syntax errors found"
fi

# Check for type hints
TYPED_FILES=$(find src -name "*.py" -exec grep -l "-> " {} \; | wc -l)
TOTAL_FILES=$(find src -name "*.py" | wc -l)
if [ $TOTAL_FILES -gt 0 ]; then
    TYPE_PERCENT=$((TYPED_FILES * 100 / TOTAL_FILES))
    if [ $TYPE_PERCENT -gt 70 ]; then
        check_pass "Good type hint coverage ($TYPE_PERCENT%)"
    else
        check_warn "Low type hint coverage ($TYPE_PERCENT%)"
    fi
fi

echo ""

# 3. Test coverage
echo "🧪 TEST COVERAGE"
echo "----------------"

if [ -d "tests" ]; then
    check_pass "Test directory exists"
    
    # Count test types
    UNIT_TESTS=$(find tests/unit -name "test_*.py" 2>/dev/null | wc -l)
    INTEGRATION_TESTS=$(find tests/integration -name "test_*.py" 2>/dev/null | wc -l)
    
    if [ $UNIT_TESTS -gt 5 ]; then
        check_pass "Sufficient unit tests ($UNIT_TESTS)"
    else
        check_fail "Too few unit tests ($UNIT_TESTS)"
    fi
    
    if [ $INTEGRATION_TESTS -gt 2 ]; then
        check_pass "Has integration tests ($INTEGRATION_TESTS)"
    else
        check_warn "Few integration tests ($INTEGRATION_TESTS)"
    fi
else
    check_fail "No test directory"
fi

# Check for mocking
if [ -f "tests/conftest.py" ]; then
    MOCK_COUNT=$(grep -c "mock" tests/conftest.py 2>/dev/null || echo "0")
    if [ $MOCK_COUNT -lt 10 ]; then
        check_pass "Minimal mocking ($MOCK_COUNT references)"
    else
        check_fail "Excessive mocking ($MOCK_COUNT references)"
    fi
fi

echo ""

# 4. Documentation
echo "📚 DOCUMENTATION"
echo "----------------"

if [ -f "README.md" ]; then
    check_pass "README.md exists"
    
    # Check for honesty indicators
    if grep -qi "alpha\|beta\|development\|work.in.progress" README.md; then
        check_pass "README indicates development status"
    else
        check_warn "README doesn't indicate development status"
    fi
    
    if grep -q "❌" README.md; then
        check_pass "README shows limitations"
    else
        check_warn "README only shows successes"
    fi
else
    check_fail "No README.md"
fi

echo ""

# 5. Performance
echo "⚡ PERFORMANCE"
echo "--------------"

if [ -f "PERFORMANCE_VALIDATION.md" ]; then
    check_pass "Performance validation exists"
else
    check_warn "No performance validation found"
fi

echo ""

# 6. Dependencies
echo "📦 DEPENDENCIES"
echo "---------------"

if [ -f "pyproject.toml" ] && [ -f "poetry.lock" ]; then
    check_pass "Poetry configuration exists"
    
    if poetry check >/dev/null 2>&1; then
        check_pass "Poetry dependencies valid"
    else
        check_fail "Poetry dependencies invalid"
    fi
else
    check_fail "Missing Poetry configuration"
fi

# Check for pip usage
PIP_USAGE=$(grep -r "pip install" . --include="*.md" --include="*.py" --exclude-dir=".git" --exclude-dir="archive" 2>/dev/null | wc -l)
if [ $PIP_USAGE -eq 0 ]; then
    check_pass "No pip install references"
else
    check_warn "Found $PIP_USAGE pip install references"
fi

echo ""

# 7. Functionality
echo "🔧 FUNCTIONALITY"
echo "----------------"

# Check basic commands
if [ -x "bin/ask-nix" ] || [ -x "./bin/ask-nix" ]; then
    check_pass "CLI executable exists"
    
    # Test help command
    if ./bin/ask-nix --help >/dev/null 2>&1; then
        check_pass "Help command works"
    else
        check_fail "Help command fails"
    fi
else
    check_fail "No CLI executable"
fi

echo ""

# 8. Security
echo "🔒 SECURITY"
echo "-----------"

# Check for secrets
if grep -r "api_key\|password\|secret" . --include="*.py" --exclude-dir=".git" | grep -v "example\|test" >/dev/null 2>&1; then
    check_fail "Possible secrets in code"
else
    check_pass "No obvious secrets found"
fi

echo ""

# 9. Version and changelog
echo "📋 VERSION CONTROL"
echo "------------------"

if [ -f "VERSION" ] || grep -q "version" pyproject.toml 2>/dev/null; then
    check_pass "Version information exists"
else
    check_warn "No version information"
fi

if [ -f "CHANGELOG.md" ]; then
    check_pass "Changelog exists"
else
    check_warn "No changelog"
fi

echo ""

# Final summary
echo "====================================="
echo "📊 RELEASE READINESS SUMMARY"
echo "====================================="
echo ""
echo "✅ Passed:   $PASSED"
echo "⚠️  Warnings: $WARNINGS"
echo "❌ Failed:   $FAILED"
echo ""

TOTAL=$((PASSED + WARNINGS + FAILED))
SCORE=$((PASSED * 100 / TOTAL))

echo "Release Readiness Score: $SCORE%"
echo ""

if [ $FAILED -eq 0 ] && [ $SCORE -gt 80 ]; then
    echo "🎉 Project is READY for release!"
    echo ""
    echo "Recommended next steps:"
    echo "1. Tag the release: git tag -a v1.0.0 -m 'Release version 1.0.0'"
    echo "2. Update CHANGELOG.md with release notes"
    echo "3. Run final integration tests"
    echo "4. Create GitHub/GitLab release"
elif [ $FAILED -eq 0 ]; then
    echo "🔶 Project is ALMOST ready (address warnings)"
    echo ""
    echo "Fix these warnings before release:"
    grep "⚠️" /tmp/release-checklist.log 2>/dev/null || true
else
    echo "🔴 Project is NOT ready for release"
    echo ""
    echo "Must fix these issues:"
    grep "❌" /tmp/release-checklist.log 2>/dev/null || true
fi

# Save detailed report
{
    echo "# Release Checklist Report"
    echo "Generated: $(date)"
    echo ""
    echo "## Summary"
    echo "- Passed: $PASSED"
    echo "- Warnings: $WARNINGS"  
    echo "- Failed: $FAILED"
    echo "- Score: $SCORE%"
    echo ""
    echo "## Detailed Results"
    echo '```'
    # Re-run checks with output capture
    $0 2>&1
    echo '```'
} > RELEASE_CHECKLIST_REPORT.md 2>/dev/null

echo ""
echo "📄 Detailed report saved to: RELEASE_CHECKLIST_REPORT.md"