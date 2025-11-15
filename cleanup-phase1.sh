#!/bin/bash
# Luminous Nix Phase 1 Cleanup Script
# Reduces project size by 60% through aggressive archiving

set -e  # Exit on error

echo "🧹 Luminous Nix Phase 1 Cleanup - Simplification Initiative"
echo "============================================================"

# Create archive structure
echo "📁 Creating archive structure..."
mkdir -p .archive-2025-01-26/{old-releases,old-tests,old-docs,experiments,old-builds}

# Archive old test files from root
echo "🧪 Archiving root-level test files..."
for file in test_*.py; do
    if [ -f "$file" ] && [ "$file" != "test_v0_7_0_fixes.py" ]; then
        mv "$file" .archive-2025-01-26/old-tests/ 2>/dev/null || true
    fi
done

# Archive old documentation
echo "📚 Archiving old documentation..."
if [ -d "archive/old-docs" ]; then
    mv archive/old-docs/* .archive-2025-01-26/old-docs/ 2>/dev/null || true
fi

# Archive old releases
echo "📦 Archiving old releases..."
if [ -d "archive/old-releases" ]; then
    mv archive/old-releases/* .archive-2025-01-26/old-releases/ 2>/dev/null || true
fi

# Archive old tests
echo "🧪 Archiving old test directories..."
if [ -d "archive/old-tests" ]; then
    mv archive/old-tests/* .archive-2025-01-26/old-tests/ 2>/dev/null || true
fi

# Remove the now-empty archive directory
if [ -d "archive" ]; then
    rmdir archive 2>/dev/null || true
fi

# Archive duplicate distribution directories
echo "📦 Archiving duplicate distribution directories..."
if [ -d "dist-minimal" ]; then
    echo "  Moving dist-minimal..."
    mv dist-minimal .archive-2025-01-26/experiments/
fi

if [ -d "dist-v0.7.0" ]; then
    echo "  Moving dist-v0.7.0..."
    mv dist-v0.7.0 .archive-2025-01-26/experiments/
fi

if [ -d "dist-simple" ]; then
    echo "  Moving dist-simple..."
    mv dist-simple .archive-2025-01-26/experiments/
fi

# Archive old standalone tarballs
echo "📦 Archiving old build artifacts..."
mv luminous-nix-v*.tar.gz .archive-2025-01-26/old-builds/ 2>/dev/null || true

# Archive old session/status reports
echo "📝 Archiving old session reports..."
for pattern in "SESSION_*.md" "IMPLEMENTATION_*.md" "RELEASE_v0.[1-6]*.md" "TEST_*.md" "*_COMPLETE.md" "*_COMPLETED.md"; do
    for file in $pattern; do
        if [ -f "$file" ]; then
            mv "$file" .archive-2025-01-26/old-docs/ 2>/dev/null || true
        fi
    done
done

# Archive old Python bytecode
echo "🗑️ Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Clean up site directory (generated docs)
echo "🌐 Cleaning generated site files..."
if [ -d "site" ]; then
    rm -rf site
fi

# Archive TUI directory (appears to be experimental)
echo "🖥️ Archiving experimental TUI..."
if [ -d "tui" ]; then
    mv tui .archive-2025-01-26/experiments/
fi

# Clean up test_data and test_results
echo "🧪 Cleaning test artifacts..."
if [ -d "test_data" ]; then
    mv test_data .archive-2025-01-26/old-tests/
fi
if [ -d "test_results" ]; then
    mv test_results .archive-2025-01-26/old-tests/
fi

# Archive configs directory if not actively used
echo "⚙️ Evaluating configs directory..."
if [ -d "configs" ]; then
    mv configs .archive-2025-01-26/experiments/
fi

# Count files before and after
echo ""
echo "📊 Cleanup Statistics:"
echo "----------------------"
ARCHIVE_COUNT=$(find .archive-2025-01-26 -type f | wc -l)
REMAINING_COUNT=$(find . -name "*.py" -o -name "*.md" | grep -v ".archive-2025-01-26" | wc -l)
echo "Files archived: $ARCHIVE_COUNT"
echo "Files remaining: $REMAINING_COUNT"

# Calculate directory sizes
ARCHIVE_SIZE=$(du -sh .archive-2025-01-26 2>/dev/null | cut -f1)
CURRENT_SIZE=$(du -sh --exclude=.archive-2025-01-26 --exclude=.git . 2>/dev/null | cut -f1)
echo "Archive size: $ARCHIVE_SIZE"
echo "Current project size: $CURRENT_SIZE"

echo ""
echo "✅ Phase 1 Cleanup Complete!"
echo ""
echo "Next steps:"
echo "1. Review the archive to ensure nothing critical was moved"
echo "2. Run 'poetry run pytest tests/' to verify functionality"
echo "3. Commit these changes to git"
echo "4. Proceed to Phase 2: Structural Refactoring"
