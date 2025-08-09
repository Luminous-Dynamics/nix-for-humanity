#!/usr/bin/env bash
# Reorganize Nix for Humanity project structure
# This script implements the emergency cleanup from the improvement plan

set -euo pipefail

echo "🔧 Starting Nix for Humanity reorganization..."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -d "nix_humanity" ]; then
    echo "❌ Error: Must run from nix-for-humanity root directory"
    exit 1
fi

# Create backup tag before changes
echo "📸 Creating git backup tag..."
git tag -a "pre-reorganization-$(date +%Y%m%d-%H%M%S)" -m "Backup before major reorganization" || true

# Create new directory structure
echo "📁 Creating organized directory structure..."
mkdir -p src/nix_humanity/{cli,core,tui,native,config,voice,learning}
mkdir -p {docs/status,docs/archive/vision,examples,scripts,config}
mkdir -p tests/{unit,integration,e2e,fixtures}
mkdir -p archive/{legacy_backend,old_tests,legacy_docs}

# Move Python source files
echo "🐍 Consolidating Python source code..."
if [ -d "nix_humanity" ]; then
    # Copy to preserve git history, then we'll git mv
    cp -r nix_humanity/* src/nix_humanity/ 2>/dev/null || true
    echo "  ✓ Copied nix_humanity to src/nix_humanity"
fi

if [ -d "backend/core" ]; then
    cp -r backend/core/* src/nix_humanity/core/ 2>/dev/null || true
    echo "  ✓ Merged backend/core into src/nix_humanity/core"
fi

# Move test files from root
echo "🧪 Moving test files to tests directory..."
for test_file in test_*.py; do
    if [ -f "$test_file" ]; then
        git mv "$test_file" tests/ 2>/dev/null || mv "$test_file" tests/
        echo "  ✓ Moved $test_file"
    fi
done

# Move demo files
echo "📝 Moving demo files to examples..."
for demo_file in demo_*.py; do
    if [ -f "$demo_file" ]; then
        git mv "$demo_file" examples/ 2>/dev/null || mv "$demo_file" examples/
        echo "  ✓ Moved $demo_file"
    fi
done

# Move status/report documents
echo "📊 Moving status documents..."
for status_file in *_COMPLETE.md *_REPORT.md *_STATUS.md; do
    if [ -f "$status_file" ]; then
        git mv "$status_file" docs/status/ 2>/dev/null || mv "$status_file" docs/status/
        echo "  ✓ Moved $status_file"
    fi
done

# Move vision documents that describe future features
echo "🔮 Archiving vision documents..."
for vision_file in *_VISION.md *_FUTURE.md *_ROADMAP.md; do
    if [ -f "$vision_file" ]; then
        git mv "$vision_file" docs/archive/vision/ 2>/dev/null || mv "$vision_file" docs/archive/vision/
        echo "  ✓ Archived $vision_file"
    fi
done

# Archive old backend implementations
echo "🗄️  Archiving legacy code..."
if [ -d "backend" ]; then
    mv backend archive/legacy_backend/
    echo "  ✓ Archived backend directory"
fi

# Clean up legacy requirements files
echo "🧹 Consolidating dependency files..."
for req_file in requirements*.txt; do
    if [ -f "$req_file" ]; then
        mv "$req_file" archive/
        echo "  ✓ Archived $req_file (using pyproject.toml instead)"
    fi
done

# Move scripts to scripts directory
echo "📜 Organizing scripts..."
for script in *.sh; do
    if [ -f "$script" ] && [ "$script" != "reorganize-project.sh" ]; then
        git mv "$script" scripts/ 2>/dev/null || mv "$script" scripts/
        echo "  ✓ Moved $script"
    fi
done

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "📝 Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Testing
.coverage
.pytest_cache/
htmlcov/
.tox/

# Nix
result
result-*

# Project specific
*.log
*.db
.cache/
tmp/
EOF
fi

# Create essential root files if missing
echo "📄 Ensuring essential root files..."

if [ ! -f "README.md" ]; then
    cat > README.md << 'EOF'
# Nix for Humanity

Natural language interface for NixOS that actually works.

## Quick Start

```bash
nix develop
./bin/ask-nix "help"
```

## Documentation

See [docs/README.md](docs/README.md) for comprehensive documentation.

## Current Status

This project is under active development. See [CHANGELOG.md](CHANGELOG.md) for recent updates.
EOF
    echo "  ✓ Created README.md"
fi

# Create a summary of what should remain in root
echo ""
echo "📋 Root directory cleanup summary:"
echo "   Files that should remain in root:"
echo "   - README.md"
echo "   - LICENSE"
echo "   - pyproject.toml"
echo "   - flake.nix"
echo "   - flake.lock"
echo "   - shell.nix (if needed)"
echo "   - .gitignore"
echo "   - .envrc (if using direnv)"
echo "   - CHANGELOG.md"

echo ""
echo "🔍 Checking for files that still need organizing..."
remaining_files=$(find . -maxdepth 1 -type f -name "*.py" -o -name "*.md" | grep -v README.md | grep -v LICENSE | grep -v CHANGELOG.md | wc -l)

if [ "$remaining_files" -gt 0 ]; then
    echo "⚠️  Warning: $remaining_files files may still need organizing"
    echo "   Run 'ls -la' to review remaining files"
else
    echo "✅ Root directory is clean!"
fi

echo ""
echo "🎉 Reorganization complete!"
echo ""
echo "Next steps:"
echo "1. Review changes with: git status"
echo "2. Update imports in Python files"
echo "3. Run tests to ensure nothing broke"
echo "4. Commit the reorganization"
echo ""
echo "To update imports automatically, run:"
echo "  ./scripts/update-imports.sh"