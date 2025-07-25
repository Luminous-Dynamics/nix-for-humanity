#!/bin/bash
# Final documentation cleanup script for Nix for Humanity
# Date: 2025-07-25

set -e  # Exit on error

echo "🧹 Starting Nix for Humanity documentation cleanup..."

cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/docs

# Phase 1: Move security files
echo "📁 Moving security files..."
if [ -f "SECURITY_IMPLEMENTATION_GUIDE.md" ]; then
    mv SECURITY_IMPLEMENTATION_GUIDE.md security/
    echo "  ✓ Moved SECURITY_IMPLEMENTATION_GUIDE.md"
fi

if [ -f "SECURITY_IMPROVEMENTS_INTEGRATED.md" ]; then
    mv SECURITY_IMPROVEMENTS_INTEGRATED.md security/
    echo "  ✓ Moved SECURITY_IMPROVEMENTS_INTEGRATED.md"
fi

if [ -f "SECURITY_REVIEW.md" ]; then
    mv SECURITY_REVIEW.md security/
    echo "  ✓ Moved SECURITY_REVIEW.md"
fi

if [ -f "SECURITY.md" ]; then
    # Check if security/SECURITY.md already exists
    if [ -f "security/SECURITY.md" ]; then
        mv SECURITY.md security/SECURITY_MAIN.md
        echo "  ✓ Moved SECURITY.md to SECURITY_MAIN.md (avoiding conflict)"
    else
        mv SECURITY.md security/
        echo "  ✓ Moved SECURITY.md"
    fi
fi

# Phase 2: Move technical files
echo "📁 Moving technical files..."
if [ -f "CACHING.md" ]; then
    mv CACHING.md technical/
    echo "  ✓ Moved CACHING.md"
fi

if [ -f "TIMEOUT_STRATEGY.md" ]; then
    mv TIMEOUT_STRATEGY.md technical/
    echo "  ✓ Moved TIMEOUT_STRATEGY.md"
fi

if [ -f "CLOUD_AI_INTEGRATION_GUIDE.md" ]; then
    mv CLOUD_AI_INTEGRATION_GUIDE.md technical/
    echo "  ✓ Moved CLOUD_AI_INTEGRATION_GUIDE.md"
fi

# Phase 3: Move project files
echo "📁 Moving project files..."
if [ -f "ROADMAP.md" ]; then
    # Check if project/ROADMAP.md already exists
    if [ -f "project/ROADMAP.md" ]; then
        mv ROADMAP.md project/ROADMAP_MAIN.md
        echo "  ✓ Moved ROADMAP.md to ROADMAP_MAIN.md (avoiding conflict)"
    else
        mv ROADMAP.md project/
        echo "  ✓ Moved ROADMAP.md"
    fi
fi

if [ -f "CLOUD_AI_INTEGRATION.md" ]; then
    mv CLOUD_AI_INTEGRATION.md project/
    echo "  ✓ Moved CLOUD_AI_INTEGRATION.md"
fi

# Phase 4: Move archive files
echo "📁 Moving archive files..."
if [ -f "ARCHIVE_RESTORATION_PLAN.md" ]; then
    mv ARCHIVE_RESTORATION_PLAN.md archive/
    echo "  ✓ Moved ARCHIVE_RESTORATION_PLAN.md"
fi

if [ -f "REORGANIZATION_SUMMARY.md" ]; then
    mv REORGANIZATION_SUMMARY.md archive/
    echo "  ✓ Moved REORGANIZATION_SUMMARY.md"
fi

if [ -f "NESTED_DOCS_CLEANUP_SUMMARY.md" ]; then
    mv NESTED_DOCS_CLEANUP_SUMMARY.md archive/
    echo "  ✓ Moved NESTED_DOCS_CLEANUP_SUMMARY.md"
fi

# Phase 5: Remove duplicate FAQ
echo "🗑️  Removing duplicate files..."
if [ -f "FAQ.md" ] && [ -f "guides/FAQ.md" ]; then
    rm -f FAQ.md
    echo "  ✓ Removed duplicate FAQ.md (keeping guides/FAQ.md)"
fi

# Phase 6: Clean up empty directories
echo "🧹 Cleaning up empty directories..."
if [ -d "archive/legacy-gui" ] && [ -z "$(ls -A archive/legacy-gui)" ]; then
    rmdir archive/legacy-gui
    echo "  ✓ Removed empty archive/legacy-gui directory"
fi

# Phase 7: Create missing directories if needed
echo "📁 Ensuring all directories exist..."
mkdir -p guides technical operations project philosophy security reference stories tutorials development error-recovery archive

# Phase 8: Report results
echo ""
echo "✅ Documentation cleanup complete!"
echo ""
echo "📊 Final status:"
echo "  Root .md files: $(ls -1 *.md 2>/dev/null | wc -l)"
echo "  Expected: 2 (README.md and CONTRIBUTING.md)"
echo ""

# List any remaining .md files in root
remaining=$(ls -1 *.md 2>/dev/null | grep -v -E "^(README|CONTRIBUTING)\.md$" || true)
if [ -n "$remaining" ]; then
    echo "⚠️  Warning: Unexpected files still in root:"
    echo "$remaining" | sed 's/^/    /'
else
    echo "✨ All files properly organized!"
fi

echo ""
echo "📝 Next steps:"
echo "  1. Update CLAUDE.md with new documentation paths"
echo "  2. Merge any duplicate content (ROADMAP_MAIN.md, SECURITY_MAIN.md)"
echo "  3. Create missing documentation (GLOSSARY.md, etc.)"
echo "  4. Test all documentation links"
echo ""
echo "🌊 We flow with organized documentation!"