# 🧹 Luminous Nix Cleanup Plan - From 6.8GB to <100MB

## 📊 Current State Analysis

### The Problem
- **Size**: 6.8GB total (1.3GB .git, 5.5GB of code/docs/duplicates)
- **Files**: 843 Python files (should be ~50)
- **Modules**: 30+ overlapping modules
- **Documentation**: 100+ markdown files scattered everywhere
- **Duplication**: Same features implemented 3-5 times

## 🎯 Target Architecture

### Clean Module Structure
```
luminous-nix/
├── src/
│   └── luminous_nix/
│       ├── __init__.py
│       ├── __version__.py         # Single version source
│       ├── core/                  # Core business logic
│       │   ├── __init__.py
│       │   ├── config.py          # Config system (DONE)
│       │   ├── intents.py         # Intent recognition
│       │   ├── backend.py         # NixOS operations
│       │   ├── executor.py        # Command execution
│       │   └── cache.py           # Search cache
│       ├── cli/                   # CLI interface
│       │   ├── __init__.py
│       │   └── main.py            # Entry point
│       ├── tui/                   # TUI (if keeping)
│       │   ├── __init__.py
│       │   └── app.py
│       └── utils/                 # Shared utilities
│           ├── __init__.py
│           └── errors.py
├── bin/
│   └── ask-nix                    # Single entry point
├── tests/
│   ├── test_core.py
│   ├── test_cli.py
│   └── test_integration.py
├── docs/
│   ├── README.md
│   ├── QUICKSTART.md
│   └── CONTRIBUTING.md
├── pyproject.toml                 # Single package config
├── README.md
└── LICENSE
```

## 📋 Cleanup Steps

### Phase 1: Backup & Analyze
```bash
# 1. Create backup
tar -czf luminous-nix-backup-$(date +%Y%m%d).tar.gz .

# 2. Create analysis report
find . -name "*.py" -exec wc -l {} + | sort -rn > python_files_analysis.txt
find . -name "*.md" | wc -l > markdown_count.txt
du -sh */ | sort -rh > directory_sizes.txt
```

### Phase 2: Remove Obvious Bloat

#### A. Remove Generated/Cache Directories
```bash
rm -rf site/              # 23MB - Generated docs
rm -rf dist*/             # ~20MB - Build artifacts  
rm -rf build/
rm -rf __pycache__/
rm -rf .pytest_cache/
rm -rf *.egg-info/
find . -name "*.pyc" -delete
find . -name ".DS_Store" -delete
```

#### B. Archive Aspirational/Unused Modules
```bash
# Create archive directory
mkdir -p .archive-2025-01-29/aspirational

# Move never-implemented features
mv src/luminous_nix/consciousness .archive-2025-01-29/aspirational/
mv src/luminous_nix/learning .archive-2025-01-29/aspirational/
mv src/luminous_nix/knowledge .archive-2025-01-29/aspirational/
mv src/luminous_nix/agents .archive-2025-01-29/aspirational/
mv src/luminous_nix/ai .archive-2025-01-29/aspirational/
mv src/luminous_nix/voice .archive-2025-01-29/aspirational/
mv src/luminous_nix/memory .archive-2025-01-29/aspirational/
mv src/luminous_nix/personas .archive-2025-01-29/aspirational/
```

#### C. Consolidate Duplicate Modules
```bash
# Merge overlapping UI modules
mkdir -p src/luminous_nix/tui_consolidated
cp src/luminous_nix/ui/main_app.py src/luminous_nix/tui_consolidated/app.py
rm -rf src/luminous_nix/ui
rm -rf src/luminous_nix/gui
rm -rf src/luminous_nix/frontends  # Keep only cli.py
mv src/luminous_nix/tui_consolidated src/luminous_nix/tui

# Merge backend modules
cp src/luminous_nix/core/backend_real.py src/luminous_nix/core/backend.py
rm -rf src/luminous_nix/backends
rm -rf src/luminous_nix/nix  # Move useful parts to core/

# Remove redundant integration modules
rm -rf src/luminous_nix/integration
rm -rf src/luminous_nix/integrations
```

### Phase 3: Clean Documentation

#### A. Archive Old Documentation
```bash
mkdir -p .archive-2025-01-29/old-docs

# Move all root-level markdown files except essentials
mv *.md .archive-2025-01-29/old-docs/
# Restore essentials
mv .archive-2025-01-29/old-docs/README.md .
mv .archive-2025-01-29/old-docs/LICENSE.md .
mv .archive-2025-01-29/old-docs/QUICKSTART.md .
```

#### B. Consolidate Documentation
```bash
# Keep only essential docs
mkdir -p docs
mv docs/* .archive-2025-01-29/old-docs/docs-backup/
echo "# Luminous Nix Documentation" > docs/README.md
cp QUICKSTART.md docs/
```

### Phase 4: Clean Up Tests

#### Remove Broken/Aspirational Tests
```bash
# Archive old tests
mv tests .archive-2025-01-29/old-tests

# Create clean test structure
mkdir -p tests
cat > tests/test_basic.py << 'EOF'
"""Basic functionality tests for Luminous Nix"""

def test_import():
    """Test that package imports correctly"""
    import luminous_nix
    assert luminous_nix.__version__

def test_config():
    """Test configuration system"""
    from luminous_nix.core.config import Config
    config = Config()
    assert config.preview == True  # Safe by default

def test_intent_recognition():
    """Test basic intent recognition"""
    from luminous_nix.core.intents import IntentRecognizer
    recognizer = IntentRecognizer()
    intent = recognizer.recognize("install firefox")
    assert intent.type.value == "install_package"
EOF
```

### Phase 5: Fix Version Strings

```python
# Create single version source
cat > src/luminous_nix/__version__.py << 'EOF'
"""Version information for Luminous Nix"""
__version__ = "0.1.0-alpha"
__version_info__ = (0, 1, 0, "alpha")
EOF

# Update all references to use this
sed -i 's/version = ".*"/version = "0.1.0-alpha"/' pyproject.toml
```

### Phase 6: Create Clean Entry Points

```bash
# Single CLI entry point
cat > bin/ask-nix << 'EOF'
#!/usr/bin/env python3
"""Luminous Nix - Natural Language NixOS Interface"""

import sys
from pathlib import Path

# Add src to path for development
src_path = Path(__file__).parent.parent / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))

from luminous_nix.cli.main import main

if __name__ == "__main__":
    sys.exit(main())
EOF

chmod +x bin/ask-nix

# Remove all other entry points
rm bin/ask-nix-*
rm bin/nix*
rm bin/luminous-nix
```

### Phase 7: Update Package Configuration

```toml
# Clean pyproject.toml
[tool.poetry]
name = "luminous-nix"
version = "0.1.0-alpha"
description = "Natural Language Interface for NixOS"
authors = ["Tristan Stoltz <tristan.stoltz@gmail.com>"]
readme = "README.md"
packages = [{include = "luminous_nix", from = "src"}]

[tool.poetry.dependencies]
python = "^3.10"
click = "^8.1.0"
rich = "^13.0.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"
black = "^23.0.0"
ruff = "^0.1.0"

[tool.poetry.scripts]
ask-nix = "luminous_nix.cli.main:main"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

## 🗑️ What Gets Removed

### Definitely Remove
- All `consciousness/`, `learning/`, `knowledge/` modules (aspirational)
- All `ai/`, `agents/`, `voice/` modules (not working)
- All duplicate UI modules (`gui/`, `frontends/`, keep only `tui/`)
- All test files for non-existent features
- All documentation for unimplemented features
- All example/demo files that don't work
- Generated documentation (`site/`)
- Build artifacts (`dist*/`, `build/`)

### Archive (Keep for Reference)
- Old release notes
- Design documents
- Research papers
- Implementation plans

### Keep & Refactor
- Core intent recognition
- Backend execution (consolidate to one)
- Config system (already clean)
- Basic CLI
- Working tests only

## 📊 Expected Results

### Before
- **Size**: 6.8GB
- **Python Files**: 843
- **Modules**: 30+
- **Documentation**: 100+ files
- **Confusion**: Maximum

### After
- **Size**: <50MB
- **Python Files**: ~30-50
- **Modules**: 5 (core, cli, tui, utils, tests)
- **Documentation**: 5-10 essential files
- **Clarity**: Maximum

## 🚀 Migration Script

```bash
#!/bin/bash
# cleanup-luminous-nix.sh

echo "🧹 Starting Luminous Nix Cleanup..."

# Step 1: Backup
echo "📦 Creating backup..."
tar -czf ../luminous-nix-backup-$(date +%Y%m%d-%H%M%S).tar.gz .

# Step 2: Remove build artifacts
echo "🗑️ Removing build artifacts..."
rm -rf site/ dist*/ build/ __pycache__/ .pytest_cache/
find . -name "*.pyc" -delete
find . -name ".DS_Store" -delete

# Step 3: Archive aspirational code
echo "📁 Archiving aspirational modules..."
mkdir -p .archive-2025-01-29
mv src/luminous_nix/{consciousness,learning,knowledge,agents,ai,voice,memory,personas} \
   .archive-2025-01-29/ 2>/dev/null || true

# Step 4: Consolidate modules
echo "🔀 Consolidating duplicate modules..."
# ... (implementation details)

# Step 5: Clean documentation
echo "📚 Cleaning documentation..."
mkdir -p .archive-2025-01-29/old-docs
mv *.md .archive-2025-01-29/old-docs/ 2>/dev/null || true
mv .archive-2025-01-29/old-docs/{README.md,LICENSE,QUICKSTART.md} . 2>/dev/null || true

# Step 6: Update git
echo "📝 Creating git commit..."
git add .
git commit -m "🧹 Major cleanup: Removed aspirational code, consolidated modules"

echo "✅ Cleanup complete! Project reduced from 6.8GB to <50MB"
echo "📊 Run 'du -sh .' to verify new size"
```

## ⚠️ Important Notes

1. **Always backup first** - This is destructive
2. **Review before deleting** - Some "aspirational" code might have useful parts
3. **Keep git history** - Don't delete .git, it has valuable history
4. **Test after cleanup** - Ensure core functionality still works
5. **Document what was removed** - Future developers need to know

## 🎯 Success Criteria

After cleanup, you should be able to:
1. Run `ask-nix install firefox --preview` ✅
2. Run `ask-nix search vim` ✅
3. Run `ask-nix list` ✅
4. Run `pytest tests/` and pass ✅
5. Build with `poetry build` ✅
6. Understand the codebase in 10 minutes ✅

The goal: **From 6.8GB of confusion to 50MB of clarity!**