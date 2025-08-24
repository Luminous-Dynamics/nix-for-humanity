#!/bin/bash

# Archive experiments script - Phase 1 of cleanup
echo "🧹 Starting Phase 1: Archive experiments..."

# Create archive directory with timestamp
ARCHIVE_DIR=".archive-2025-08-24"
mkdir -p "$ARCHIVE_DIR"

# Create subdirectories for organization
mkdir -p "$ARCHIVE_DIR/test-scripts"
mkdir -p "$ARCHIVE_DIR/demo-scripts"
mkdir -p "$ARCHIVE_DIR/experiments"
mkdir -p "$ARCHIVE_DIR/integration-attempts"
mkdir -p "$ARCHIVE_DIR/old-tools"

# Keep these essential files in root
KEEP_FILES=(
    "setup.py"
    "manage.py"
    "pyproject.toml"
    "poetry.lock"
    "pytest.ini"
    "Makefile"
    "shell.nix"
    "flake.nix"
    "flake.lock"
    "VERSION"
    "LICENSE"
    "README.md"
    "MANIFEST.in"
)

# Move test scripts
echo "📦 Archiving test scripts..."
for file in test_*.py; do
    if [ -f "$file" ]; then
        mv "$file" "$ARCHIVE_DIR/test-scripts/" 2>/dev/null
    fi
done

# Move demo scripts
echo "📦 Archiving demo scripts..."
for file in demo_*.py; do
    if [ -f "$file" ]; then
        mv "$file" "$ARCHIVE_DIR/demo-scripts/" 2>/dev/null
    fi
done

# Move experimental directories
echo "📦 Archiving experimental directories..."
[ -d "ai-improvements" ] && mv ai-improvements "$ARCHIVE_DIR/experiments/"
[ -d "paradoxes" ] && mv paradoxes "$ARCHIVE_DIR/experiments/"
[ -d "pitch" ] && mv pitch "$ARCHIVE_DIR/experiments/"
[ -d "monitoring" ] && mv monitoring "$ARCHIVE_DIR/experiments/"
[ -d "paradise" ] && mv paradise "$ARCHIVE_DIR/experiments/"

# Move integration attempts
echo "📦 Archiving integration scripts..."
for file in integrate_*.py connect_*.py implement_*.py inject_*.py; do
    if [ -f "$file" ]; then
        mv "$file" "$ARCHIVE_DIR/integration-attempts/" 2>/dev/null
    fi
done

# Move old tool scripts
echo "📦 Archiving old tools..."
for file in *.py; do
    should_keep=false
    for keep in "${KEEP_FILES[@]}"; do
        if [ "$file" == "$keep" ]; then
            should_keep=true
            break
        fi
    done
    
    if [ "$should_keep" = false ] && [ -f "$file" ]; then
        mv "$file" "$ARCHIVE_DIR/old-tools/" 2>/dev/null
    fi
done

# Move shell scripts except essential ones
echo "📦 Archiving shell scripts..."
for file in *.sh; do
    case "$file" in
        "SHIP_NOW.sh"|"archive-experiments.sh")
            # Keep these
            ;;
        *)
            [ -f "$file" ] && mv "$file" "$ARCHIVE_DIR/old-tools/" 2>/dev/null
            ;;
    esac
done

# Move JSON files except essential ones
echo "📦 Archiving JSON files..."
for file in *.json; do
    case "$file" in
        "package.json"|"tsconfig.json")
            # Keep if they exist
            ;;
        *)
            [ -f "$file" ] && mv "$file" "$ARCHIVE_DIR/experiments/" 2>/dev/null
            ;;
    esac
done

# Move markdown files except essential ones
echo "📦 Archiving documentation..."
mkdir -p "$ARCHIVE_DIR/old-docs"
for file in *.md; do
    case "$file" in
        "README.md"|"CONTRIBUTING.md"|"LICENSE.md"|"CLEANUP_PLAN.md"|"CLEANUP_COMPLETE.md")
            # Keep these
            ;;
        *)
            [ -f "$file" ] && mv "$file" "$ARCHIVE_DIR/old-docs/" 2>/dev/null
            ;;
    esac
done

# Count what we archived
echo ""
echo "📊 Archive Summary:"
echo "  Test scripts: $(ls -1 "$ARCHIVE_DIR/test-scripts/" 2>/dev/null | wc -l)"
echo "  Demo scripts: $(ls -1 "$ARCHIVE_DIR/demo-scripts/" 2>/dev/null | wc -l)"
echo "  Integration attempts: $(ls -1 "$ARCHIVE_DIR/integration-attempts/" 2>/dev/null | wc -l)"
echo "  Old tools: $(ls -1 "$ARCHIVE_DIR/old-tools/" 2>/dev/null | wc -l)"
echo "  Old docs: $(ls -1 "$ARCHIVE_DIR/old-docs/" 2>/dev/null | wc -l)"

echo ""
echo "✅ Phase 1 complete! Root directory cleaned."
echo "📁 All archived files are in: $ARCHIVE_DIR"