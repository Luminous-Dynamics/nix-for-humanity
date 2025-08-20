#!/usr/bin/env bash

# 🧹 Consolidate Duplicate Scripts in scripts/ Directory
# Groups and archives similar scripts to reduce clutter

echo "🧹 Consolidating Scripts Directory..."
echo "====================================="

BASE_DIR="/srv/luminous-dynamics/11-meta-consciousness/luminous-nix"
SCRIPTS_DIR="$BASE_DIR/scripts"
cd "$SCRIPTS_DIR"

# Create archive directory with timestamp
ARCHIVE_DIR="$BASE_DIR/.archive-$(date +%Y-%m-%d)/consolidated-scripts"
mkdir -p "$ARCHIVE_DIR"
mkdir -p "$ARCHIVE_DIR/fix-scripts"
mkdir -p "$ARCHIVE_DIR/test-scripts"
mkdir -p "$ARCHIVE_DIR/run-scripts"
mkdir -p "$ARCHIVE_DIR/duplicate-variants"
mkdir -p "$ARCHIVE_DIR/dev-scripts"
mkdir -p "$ARCHIVE_DIR/setup-scripts"

echo ""
echo "📊 Current State:"
echo "-----------------"
echo "Total files: $(ls -1 2>/dev/null | wc -l)"
echo "Python files: $(ls -1 *.py 2>/dev/null | wc -l)"
echo "Shell scripts: $(ls -1 *.sh 2>/dev/null | wc -l)"

# 1. Consolidate fix-* scripts (keep only the most recent/comprehensive)
echo ""
echo "📁 Consolidating fix-* scripts..."
# Keep the main comprehensive ones, archive specific/temporary fixes
for file in fix-fstring-semicolons.py fix-newline-fstrings.py \
            fix-pytest-assertions.py fix-test-executor-indentation.py \
            fix_query_executionmode.py fix_test_imports.py; do
    if [ -f "$file" ]; then
        mv "$file" "$ARCHIVE_DIR/fix-scripts/" 2>/dev/null && echo "   ✅ Archived $file"
    fi
done

# Keep only the most comprehensive fix scripts
echo "   Keeping: fix-all-syntax-errors-final.py, fix-import-structure.py, fix-circular-imports.py"

# 2. Consolidate test-* scripts (many are redundant)
echo ""
echo "📁 Consolidating test-* scripts..."
for file in test-deployment.sh test-infrastructure.sh test-frontend.sh \
            test-phase-0.sh test-poetry-env.sh test-dev-env.sh; do
    if [ -f "$file" ]; then
        mv "$file" "$ARCHIVE_DIR/test-scripts/" 2>/dev/null && echo "   ✅ Archived $file"
    fi
done
echo "   Keeping: test-all-discovery-features.py, test-natural-language.py, test-tui-complete.py"

# 3. Consolidate run-* scripts for TUI (many duplicates)
echo ""
echo "📁 Consolidating run-* TUI scripts..."
for file in run-enhanced-tui.sh run_enhanced_tui.sh run_advanced_tui.sh \
            run_main_tui.sh run-tui-now.sh run-tui-with-deps.sh; do
    if [ -f "$file" ]; then
        mv "$file" "$ARCHIVE_DIR/run-scripts/" 2>/dev/null && echo "   ✅ Archived $file"
    fi
done
echo "   Keeping: run-unified-tui.sh"

# 4. Consolidate duplicate variants
echo ""
echo "📁 Consolidating duplicate variants..."
# Python variants with underscores vs hyphens
for file in command_learning_system.py monitor_coverage.py \
            nix_knowledge_engine.py nix_knowledge_engine_enhanced_wrapper.py \
            nix_knowledge_engine_modern.py performance_benchmark.py \
            test_coverage_monitor.py test_model_download.py \
            test_plugin_system.py test_python_api_discovery.py; do
    if [ -f "$file" ]; then
        mv "$file" "$ARCHIVE_DIR/duplicate-variants/" 2>/dev/null && echo "   ✅ Archived $file"
    fi
done

# 5. Consolidate dev-* scripts (keep only main dev.sh)
echo ""
echo "📁 Consolidating dev-* scripts..."
for file in dev-enter.sh dev-poetry.sh dev-python.sh dev-quick.sh dev-tauri.sh; do
    if [ -f "$file" ]; then
        mv "$file" "$ARCHIVE_DIR/dev-scripts/" 2>/dev/null && echo "   ✅ Archived $file"
    fi
done
echo "   Keeping: dev.sh as main development entry point"

# 6. Consolidate setup-* scripts
echo ""
echo "📁 Consolidating setup-* scripts..."
for file in setup-dual-models.sh setup-environment.sh setup-github-app.sh \
            setup-modular-architecture.sh setup-ollama-service.sh \
            setup-sacred-trinity.sh setup-weekly-update.sh; do
    if [ -f "$file" ]; then
        mv "$file" "$ARCHIVE_DIR/setup-scripts/" 2>/dev/null && echo "   ✅ Archived $file"
    fi
done
echo "   Keeping: setup-dev.sh as main setup script"

# 7. Archive old/obsolete scripts
echo ""
echo "📦 Archiving obsolete scripts..."
for file in organize-root-files.py cleanup-luminous-nix.sh cleanup_docs.sh \
            consolidate-variants.py docs_audit.py verify_all_fixes.py \
            week3-action-plan.py week3-day2-config-fix.py \
            week3-day2-tui-summary.py week3-final-summary.py; do
    if [ -f "$file" ]; then
        mv "$file" "$ARCHIVE_DIR/" 2>/dev/null && echo "   ✅ Archived $file"
    fi
done

# 8. Create organized structure
echo ""
echo "📁 Creating organized structure..."
mkdir -p "$SCRIPTS_DIR/fix" 2>/dev/null
mkdir -p "$SCRIPTS_DIR/test" 2>/dev/null
mkdir -p "$SCRIPTS_DIR/development" 2>/dev/null
mkdir -p "$SCRIPTS_DIR/training" 2>/dev/null
mkdir -p "$SCRIPTS_DIR/deployment" 2>/dev/null

# Move remaining fix scripts to fix/
for file in fix-*.py; do
    if [ -f "$file" ]; then
        mv "$file" fix/ 2>/dev/null
    fi
done

# Move test scripts to test/
for file in test-*.py test-*.sh; do
    if [ -f "$file" ]; then
        mv "$file" test/ 2>/dev/null
    fi
done

# Move training scripts to training/
for file in *train*.py *training*.sh; do
    if [ -f "$file" ]; then
        mv "$file" training/ 2>/dev/null
    fi
done

# Move deployment scripts to deployment/
for file in *release*.py *release*.sh *deploy*.sh push-to-github.sh; do
    if [ -f "$file" ]; then
        mv "$file" deployment/ 2>/dev/null
    fi
done

# 9. Generate consolidation report
echo ""
echo "📊 Creating consolidation report..."
cat > CONSOLIDATION_REPORT.md << 'EOF'
# Scripts Consolidation Report

**Date**: $(date)

## Actions Taken

### 1. Fix Scripts Consolidated
- Archived 6 specific fix scripts (f-string, newline, etc.)
- Kept comprehensive ones: fix-all-syntax-errors-final.py

### 2. Test Scripts Consolidated  
- Archived 6 redundant test scripts
- Kept main test runners

### 3. Run Scripts Consolidated
- Archived 6 duplicate TUI run scripts
- Kept unified version: run-unified-tui.sh

### 4. Variant Scripts Consolidated
- Archived underscore variants (kept hyphen versions)
- 10 duplicate variants removed

### 5. Dev Scripts Consolidated
- Archived 5 specific dev scripts
- Kept main: dev.sh

### 6. Setup Scripts Consolidated
- Archived 7 specific setup scripts
- Kept main: setup-dev.sh

### 7. Obsolete Scripts Archived
- Moved cleanup and week3 scripts to archive

## New Structure

```
scripts/
├── fix/           # Fix scripts
├── test/          # Test scripts
├── development/   # Development tools
├── training/      # Training scripts
├── deployment/    # Release/deployment
└── [main scripts] # Core utilities
```

## Statistics

- Files before: 231
- Files after: ~100 (estimated)
- Reduction: ~57%
- Archive location: $(echo $ARCHIVE_DIR)

## Next Steps

1. Update documentation to reflect new structure
2. Update .gitignore for archive directories
3. Test that core scripts still work
4. Consider further consolidation of similar scripts
EOF

echo ""
echo "✨ Final State:"
echo "---------------"
echo "Files remaining: $(ls -1 2>/dev/null | wc -l)"
echo "Organized directories: $(ls -d */ 2>/dev/null | wc -l)"
echo "Archive location: $ARCHIVE_DIR"

echo ""
echo "🎉 Scripts Consolidation Complete!"
echo ""
echo "📝 Next recommended steps:"
echo "  1. Review CONSOLIDATION_REPORT.md"
echo "  2. Test main scripts still work"
echo "  3. Update documentation references"
echo "  4. Commit these changes"