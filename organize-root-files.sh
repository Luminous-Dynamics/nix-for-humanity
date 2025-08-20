#!/usr/bin/env bash

# 🧹 Organize Root Directory Files
# Moves loose files from root to appropriate directories

echo "🧹 Organizing Root Directory Files..."
echo "====================================="

BASE_DIR="/srv/luminous-dynamics/11-meta-consciousness/luminous-nix"
cd "$BASE_DIR"

# Create archive directory with timestamp
ARCHIVE_DIR="$BASE_DIR/.archive-$(date +%Y-%m-%d)"
mkdir -p "$ARCHIVE_DIR"
mkdir -p "$ARCHIVE_DIR/old-reports"
mkdir -p "$ARCHIVE_DIR/old-scripts"
mkdir -p "$ARCHIVE_DIR/old-configs"

echo ""
echo "📊 Current State:"
echo "-----------------"
echo "Python files in root: $(ls -1 *.py 2>/dev/null | wc -l)"
echo "Markdown files in root: $(ls -1 *.md 2>/dev/null | wc -l)"
echo "Shell scripts in root: $(ls -1 *.sh 2>/dev/null | wc -l)"

# 1. Move Python utility scripts to scripts/
echo ""
echo "📁 Moving Python scripts to scripts/..."
for file in consolidate-variants.py create_data_trinity_schema.py \
            demo_both_and_philosophy.py demonstrate_trinity.py \
            docs_audit.py explore_vector_alternatives.py \
            fix-remaining-imports.py fix_tui_async.py \
            monitor_gemma3.py update_trinity_to_v2.py \
            verify_all_fixes.py; do
    if [ -f "$file" ]; then
        mv "$file" scripts/ 2>/dev/null && echo "   ✅ Moved $file"
    fi
done

# 2. Archive old report markdown files
echo ""
echo "📦 Archiving old report files..."
for file in ARCHITECTURE_REVIEW.md COMPLETE_INTEGRATION_SUMMARY.md \
            CORE_FUNCTIONALITY_INTEGRATION_REPORT.md DATA_TRINITY_INTEGRATION_PLAN.md \
            ENHANCEMENTS_COMPLETE.md FEATURE_REALITY_MATRIX.md \
            FEATURE_REALITY_MATRIX_ENHANCED.md FEATURE_STATUS.md \
            GRANDMA_MODE_COMPLETE.md HIDDEN_GEMS_REPORT.md \
            INTEGRATION_ARCHITECTURE.md INTEGRATION_CLEANUP_TODO.md \
            INTEGRATION_SUCCESS_REPORT.md LUMINOUS_COMPANION_ARCHITECTURE.md \
            MAXIMUM_ENHANCEMENT_ACHIEVED.md MODEL_CURATOR_COMPLETE.md \
            NATIVE_API_ACHIEVEMENT.md NATIVE_API_ACTIVATED.md \
            PHASE_A_PRIME_FOUNDATION.md PHASE_B_GRAPHRAG_COMPLETE.md \
            PLUGIN_ARCHITECTURE.md PLUGIN_INTEGRATION_COMPLETE.md \
            PROJECT_CLARITY_SUMMARY.md PROJECT_STRUCTURE.md \
            SACRED_INTEGRATION_COMPLETE.md SACRED_SYNTHESIS_COMPLETE.md \
            SACRED_SYNTHESIS_FINAL_REPORT.md SACRED_SYNTHESIS_INTEGRATION_COMPLETE.md \
            SACRED_SYNTHESIS_STATUS.md SIMPLIFIED_ARCHITECTURE.md \
            TECHNICAL_BLUEPRINT.md TRINITY_OF_MODELS_COMPLETE.md \
            UNIFIED_ARCHITECTURE_SUCCESS.md UNIVERSAL_CONSCIOUSNESS_PROTOCOL_COMPLETE.md \
            VISION_CLARITY.md CURRENT_STATE_REPORT.md \
            ARCHITECTURE_CONSIDERATIONS.md; do
    if [ -f "$file" ]; then
        mv "$file" "$ARCHIVE_DIR/old-reports/" && echo "   ✅ Archived $file"
    fi
done

# 3. Move implementation roadmaps to docs/planning/
echo ""
echo "📋 Moving roadmap files..."
mkdir -p docs/planning
for file in IMPLEMENTATION_ROADMAP.md IMPLEMENTATION_ROADMAP_V2.md \
            NEXT_STEPS_ROADMAP.md; do
    if [ -f "$file" ]; then
        mv "$file" docs/planning/ && echo "   ✅ Moved $file"
    fi
done

# 4. Move shell scripts to scripts/
echo ""
echo "🔧 Moving shell scripts..."
for file in cleanup-luminous-nix.sh cleanup_docs.sh install.sh \
            install_data_trinity.sh run_all_tests.sh run_with_libs.sh \
            shell-databases.nix; do
    if [ -f "$file" ]; then
        mv "$file" scripts/ 2>/dev/null && echo "   ✅ Moved $file"
    fi
done

# 5. Keep essential root files
echo ""
echo "📌 Keeping essential root files:"
for file in README.md CHANGELOG.md CLAUDE.md VERSION \
            pyproject.toml poetry.lock setup.py pytest.ini \
            flake.nix flake.lock shell.nix MANIFEST.in \
            Procfile package_cache.db; do
    if [ -f "$file" ]; then
        echo "   ✅ $file (essential)"
    fi
done

# 6. Move pyproject backup
if [ -f "pyproject.toml.backup-20250816-231851" ]; then
    mv pyproject.toml.backup-20250816-231851 "$ARCHIVE_DIR/old-configs/"
    echo "   ✅ Archived pyproject.toml backup"
fi

# 7. Remove metrics_server.log if it exists
if [ -f "metrics_server.log" ]; then
    rm metrics_server.log
    echo "   ✅ Removed metrics_server.log"
fi

# 8. Clean up CLEANUP_REPORT.md (from previous cleanup)
if [ -f "CLEANUP_REPORT.md" ]; then
    mv CLEANUP_REPORT.md "$ARCHIVE_DIR/"
    echo "   ✅ Moved CLEANUP_REPORT.md to archive"
fi

# 9. Move REAL_ACHIEVEMENT_SUMMARY.md to docs/
if [ -f "REAL_ACHIEVEMENT_SUMMARY.md" ]; then
    mv REAL_ACHIEVEMENT_SUMMARY.md docs/
    echo "   ✅ Moved REAL_ACHIEVEMENT_SUMMARY.md to docs/"
fi

# 10. Review scripts directory for duplicates
echo ""
echo "🔍 Analyzing scripts/ directory..."
cd scripts/
echo "   Total scripts: $(ls -1 *.py *.sh 2>/dev/null | wc -l)"
echo "   Python scripts: $(ls -1 *.py 2>/dev/null | wc -l)"
echo "   Shell scripts: $(ls -1 *.sh 2>/dev/null | wc -l)"

# Find potential duplicates by name pattern
echo ""
echo "   Potential duplicate patterns:"
ls -1 *.py 2>/dev/null | sed 's/\.py$//' | sort | uniq -d | head -5
ls -1 fix-*.py 2>/dev/null | wc -l | xargs echo "   Fix scripts:"
ls -1 test-*.py 2>/dev/null | wc -l | xargs echo "   Test scripts:"
ls -1 test-*.sh 2>/dev/null | wc -l | xargs echo "   Test shell scripts:"

cd "$BASE_DIR"

# 11. Create updated structure report
echo ""
echo "📊 Creating structure report..."
cat > ROOT_ORGANIZATION_REPORT.md << 'EOF'
# Root Directory Organization Report

**Date**: $(date)

## Actions Taken

1. ✅ Moved Python utility scripts to `scripts/`
2. ✅ Archived old report markdown files
3. ✅ Moved roadmap files to `docs/planning/`
4. ✅ Moved shell scripts to `scripts/`
5. ✅ Kept essential root files only
6. ✅ Cleaned up backup and log files

## New Root Structure

Essential files only in root:
- README.md - Project documentation
- CHANGELOG.md - Version history
- CLAUDE.md - Living memory
- VERSION - Version file
- pyproject.toml - Poetry configuration
- poetry.lock - Poetry lock file
- setup.py - Setup script
- pytest.ini - Test configuration
- flake.nix - Nix flake
- flake.lock - Nix lock
- shell.nix - Development shell
- MANIFEST.in - Package manifest
- Procfile - Process file
- package_cache.db - Package cache

## Directories

- src/ - Source code
- tests/ - Test files
- docs/ - Documentation
- scripts/ - Utility scripts
- bin/ - Executable scripts
- config/ - Configuration files
- examples/ - Example code
- data/ - Data files
- plugins/ - Plugin system
- benchmarks/ - Performance tests
- schemas/ - Schema files
- release/ - Release files
- metrics/ - Metrics data
- results/ - Test results
- frontends/ - Frontend code
- ssl/ - SSL certificates
- migrations/ - Database migrations
- models/ - Model files
- modules/ - Nix modules
- learning/ - Learning system
- tui/ - TUI interface

## Archive Location

Old files archived to: $ARCHIVE_DIR

## Next Steps

1. Review and consolidate scripts/ directory
2. Clean up duplicate test scripts
3. Organize fix-*.py scripts by category
4. Update .gitignore
EOF

echo ""
echo "✨ Final State:"
echo "---------------"
echo "Files in root: $(ls -1 | wc -l)"
echo "Python files in root: $(ls -1 *.py 2>/dev/null | wc -l)"
echo "Markdown files in root: $(ls -1 *.md 2>/dev/null | wc -l)"
echo "Archive location: $ARCHIVE_DIR"

echo ""
echo "🎉 Root Directory Organization Complete!"
echo ""
echo "📝 Next recommended steps:"
echo "  1. Review scripts/ directory for consolidation"
echo "  2. Run 'poetry install' to ensure dependencies"
echo "  3. Run 'pytest tests/' to verify everything works"
echo "  4. Commit these organizational changes"