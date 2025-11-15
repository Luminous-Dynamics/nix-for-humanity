#!/bin/sh
# Luminous Nix Phase 2 AGGRESSIVE Cleanup
# Target: Reduce to <500 essential files

set -e

echo "🔥 Phase 2: AGGRESSIVE Cleanup"
echo "=============================="

# Create additional archive directories
mkdir -p .archive-2025-01-26/{old-docs-detailed,old-scripts,old-configs,old-examples}

# Archive excessive documentation
echo "📚 Aggressive documentation cleanup..."
if [ -d "docs" ]; then
    # Keep only essential docs
    mkdir -p docs-temp

    # Keep critical user docs
    [ -f "docs/README.md" ] && cp docs/README.md docs-temp/
    [ -f "docs/QUICKSTART.md" ] && cp docs/QUICKSTART.md docs-temp/

    # Keep essential tutorials
    [ -d "docs/06-TUTORIALS" ] && cp -r docs/06-TUTORIALS docs-temp/

    # Archive everything else
    mv docs/* .archive-2025-01-26/old-docs-detailed/ 2>/dev/null || true

    # Restore essentials
    if [ -d "docs-temp" ]; then
        mv docs-temp/* docs/ 2>/dev/null || true
        rmdir docs-temp
    fi
fi

# Archive all top-level MD files except core ones
echo "📝 Archiving excessive top-level documentation..."
for file in *.md; do
    case "$file" in
        README.md|QUICKSTART.md|LICENSE.md|CONTRIBUTING.md|FAQ.md)
            # Keep these
            ;;
        *)
            [ -f "$file" ] && mv "$file" .archive-2025-01-26/old-docs/ 2>/dev/null || true
            ;;
    esac
done

# Archive scripts directory
echo "📜 Archiving scripts directory..."
if [ -d "scripts" ]; then
    mv scripts .archive-2025-01-26/old-scripts/
fi

# Archive examples if they exist
echo "📖 Archiving examples..."
if [ -d "examples" ]; then
    mv examples .archive-2025-01-26/old-examples/
fi

# Archive config directory
echo "⚙️ Archiving config files..."
if [ -d "config" ]; then
    mv config .archive-2025-01-26/old-configs/
fi

# Archive announcement directory
echo "📢 Archiving announcements..."
if [ -d "announcements" ]; then
    mv announcements .archive-2025-01-26/old-docs/
fi

# Archive release directory except current
echo "📦 Archiving old releases..."
if [ -d "release" ]; then
    mkdir -p release-temp
    # Keep only v1.0.0 if it exists
    [ -d "release/v1.0.0" ] && cp -r release/v1.0.0 release-temp/
    mv release .archive-2025-01-26/old-releases/
    [ -d "release-temp/v1.0.0" ] && mkdir -p release && mv release-temp/v1.0.0 release/
    rmdir release-temp 2>/dev/null || true
fi

# Archive data directories
echo "💾 Archiving data directories..."
if [ -d "data" ]; then
    mv data .archive-2025-01-26/experiments/
fi

# Archive metrics
echo "📊 Archiving metrics..."
if [ -d "metrics" ]; then
    mv metrics .archive-2025-01-26/old-docs/
fi

# Clean up all shell scripts in root
echo "🗑️ Archiving root shell scripts..."
for script in *.sh; do
    case "$script" in
        cleanup-phase*.sh|install.sh|build.sh)
            # Keep these
            ;;
        *)
            [ -f "$script" ] && mv "$script" .archive-2025-01-26/old-scripts/ 2>/dev/null || true
            ;;
    esac
done

# Archive schemas
echo "📋 Archiving schemas..."
if [ -d "schemas" ]; then
    mv schemas .archive-2025-01-26/old-configs/
fi

# Archive SSL if exists
echo "🔒 Archiving SSL..."
if [ -d "ssl" ]; then
    mv ssl .archive-2025-01-26/old-configs/
fi

# Archive plugins directory (experimental)
echo "🔌 Archiving plugins..."
if [ -d "plugins" ]; then
    mv plugins .archive-2025-01-26/experiments/
fi

# Clean up paradise and other random files
echo "🗑️ Cleaning misc files..."
[ -f "paradise" ] && rm paradise
[ -f "hello.txt" ] && rm hello.txt
[ -f "sacred.txt" ] && rm sacred.txt

# Clean up nix directory if exists
echo "📦 Evaluating nix directory..."
if [ -d "nix" ]; then
    mv nix .archive-2025-01-26/old-configs/
fi

# Clean up learning directory
echo "🧠 Archiving learning directory..."
if [ -d "learning" ]; then
    mv learning .archive-2025-01-26/experiments/
fi

# Clean up all Makefiles except main one
echo "🔧 Cleaning Makefiles..."
for makefile in Makefile.*; do
    [ -f "$makefile" ] && mv "$makefile" .archive-2025-01-26/old-configs/ 2>/dev/null || true
done

# Archive old Python files in root
echo "🐍 Archiving root Python files..."
for pyfile in *.py; do
    case "$pyfile" in
        setup.py|build_entry.py)
            # Keep these
            ;;
        *)
            [ -f "$pyfile" ] && mv "$pyfile" .archive-2025-01-26/old-scripts/ 2>/dev/null || true
            ;;
    esac
done

# Archive various flake files
echo "❄️ Archiving alternative flake files..."
for flake in flake-*.nix; do
    [ -f "$flake" ] && mv "$flake" .archive-2025-01-26/old-configs/ 2>/dev/null || true
done

# Archive all MANIFEST files except MANIFEST.in
echo "📜 Archiving manifest files..."
for manifest in MANIFEST*; do
    if [ "$manifest" != "MANIFEST.in" ] && [ -f "$manifest" ]; then
        mv "$manifest" .archive-2025-01-26/old-configs/ 2>/dev/null || true
    fi
done

# Final statistics
echo ""
echo "📊 Phase 2 Cleanup Statistics:"
echo "------------------------------"
ARCHIVE_COUNT=$(find .archive-2025-01-26 -type f 2>/dev/null | wc -l)
REMAINING_PY=$(find . -name "*.py" -not -path "./.archive-2025-01-26/*" -not -path "./.git/*" 2>/dev/null | wc -l)
REMAINING_MD=$(find . -name "*.md" -not -path "./.archive-2025-01-26/*" -not -path "./.git/*" 2>/dev/null | wc -l)
REMAINING_TOTAL=$(find . -type f -not -path "./.archive-2025-01-26/*" -not -path "./.git/*" -not -path "./.gitignore" 2>/dev/null | wc -l)

echo "Files archived: $ARCHIVE_COUNT"
echo "Python files remaining: $REMAINING_PY"
echo "Markdown files remaining: $REMAINING_MD"
echo "Total files remaining: $REMAINING_TOTAL"

ARCHIVE_SIZE=$(du -sh .archive-2025-01-26 2>/dev/null | cut -f1)
CURRENT_SIZE=$(du -sh --exclude=.archive-2025-01-26 --exclude=.git . 2>/dev/null | cut -f1)
echo ""
echo "Archive size: $ARCHIVE_SIZE"
echo "Current project size: $CURRENT_SIZE"

echo ""
echo "✅ Phase 2 AGGRESSIVE Cleanup Complete!"
echo ""
echo "Essential files preserved:"
echo "- src/ (core source code)"
echo "- tests/ (test suite)"
echo "- bin/ask-nix (main entry point)"
echo "- pyproject.toml, poetry.lock (dependencies)"
echo "- README.md, LICENSE (documentation)"
echo ""
echo "Next: Verify functionality with 'poetry run pytest'"
