#!/bin/sh
# Luminous Nix Phase 3 FINAL Cleanup
# Removes build artifacts and caches

set -e

echo "🚀 Phase 3: FINAL Cleanup - Build Artifacts"
echo "==========================================="

# Count before cleanup
BEFORE_COUNT=$(find . -type f -not -path "./.git/*" -not -path "./.archive-2025-01-26/*" 2>/dev/null | wc -l)
echo "Files before cleanup: $BEFORE_COUNT"

# Clean build directory
echo "🔨 Cleaning build directory..."
if [ -d "build" ]; then
    rm -rf build
    echo "  ✓ Removed build/"
fi

# Clean dist directory
echo "📦 Cleaning dist directory..."
if [ -d "dist" ]; then
    rm -rf dist
    echo "  ✓ Removed dist/"
fi

# Clean Python caches
echo "🐍 Cleaning Python caches..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "*.egg-info" -not -path "./.archive-2025-01-26/*" -exec rm -rf {} + 2>/dev/null || true
echo "  ✓ Cleaned Python caches"

# Clean virtual environments
echo "🌍 Cleaning virtual environments..."
[ -d ".venv" ] && rm -rf .venv && echo "  ✓ Removed .venv"
[ -d "venv" ] && rm -rf venv && echo "  ✓ Removed venv"
[ -d ".tox" ] && rm -rf .tox && echo "  ✓ Removed .tox"

# Clean node_modules if exists
echo "📦 Cleaning node_modules..."
[ -d "node_modules" ] && rm -rf node_modules && echo "  ✓ Removed node_modules"

# Clean coverage reports
echo "📊 Cleaning coverage reports..."
[ -d "htmlcov" ] && rm -rf htmlcov
[ -d "coverage_html_report" ] && rm -rf coverage_html_report
[ -f ".coverage" ] && rm .coverage
[ -f "coverage.xml" ] && rm coverage.xml
echo "  ✓ Cleaned coverage files"

# Clean results directory
echo "📋 Cleaning results directory..."
[ -d "results" ] && rm -rf results && echo "  ✓ Removed results/"

# Clean package cache
echo "💾 Cleaning package cache..."
[ -f "package_cache.db" ] && rm package_cache.db && echo "  ✓ Removed package_cache.db"

# Clean site directory (generated docs)
echo "🌐 Cleaning generated docs..."
[ -d "site" ] && rm -rf site && echo "  ✓ Removed site/"

# Final statistics
echo ""
echo "📊 Phase 3 Cleanup Statistics:"
echo "------------------------------"
AFTER_COUNT=$(find . -type f -not -path "./.git/*" -not -path "./.archive-2025-01-26/*" 2>/dev/null | wc -l)
ARCHIVE_COUNT=$(find .archive-2025-01-26 -type f 2>/dev/null | wc -l || echo "0")

echo "Files before: $BEFORE_COUNT"
echo "Files after: $AFTER_COUNT"
echo "Files removed: $((BEFORE_COUNT - AFTER_COUNT))"
echo "Files in archive: $ARCHIVE_COUNT"

# Size statistics
CURRENT_SIZE=$(du -sh --exclude=.archive-2025-01-26 --exclude=.git . 2>/dev/null | cut -f1)
ARCHIVE_SIZE=$(du -sh .archive-2025-01-26 2>/dev/null | cut -f1 || echo "0")

echo ""
echo "Current project size: $CURRENT_SIZE"
echo "Archive size: $ARCHIVE_SIZE"

# Core file check
echo ""
echo "✅ Core files preserved:"
echo "------------------------"
[ -d "src/luminous_nix" ] && echo "✓ src/luminous_nix/"
[ -d "tests" ] && echo "✓ tests/"
[ -f "pyproject.toml" ] && echo "✓ pyproject.toml"
[ -f "poetry.lock" ] && echo "✓ poetry.lock"
[ -f "README.md" ] && echo "✓ README.md"
[ -f "bin/ask-nix" ] && echo "✓ bin/ask-nix"

echo ""
echo "🎉 Phase 3 FINAL Cleanup Complete!"
echo ""
echo "Project is now clean and ready for:"
echo "1. Core functionality verification: poetry run pytest"
echo "2. Structural refactoring"
echo "3. Documentation update"
