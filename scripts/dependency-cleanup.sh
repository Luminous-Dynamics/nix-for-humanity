#!/usr/bin/env bash
# Clean up and unify dependency management
# Resolves the Poetry vs Nix conflict

set -euo pipefail

echo "🧹 Cleaning up dependency management..."

# Check current state
echo "📊 Current dependency files:"
[ -f "pyproject.toml" ] && echo "  ✓ pyproject.toml (Poetry)"
[ -f "flake.nix" ] && echo "  ✓ flake.nix (Nix)"
[ -f "requirements.txt" ] && echo "  ✓ requirements.txt (pip)"
[ -f "requirements-research.txt" ] && echo "  ✓ requirements-research.txt"
[ -f "shell.nix" ] && echo "  ✓ shell.nix"

# Archive old requirements files
echo -e "\n📦 Archiving legacy requirements files..."
mkdir -p archive/legacy-deps
for req_file in requirements*.txt; do
    if [ -f "$req_file" ]; then
        mv "$req_file" archive/legacy-deps/
        echo "  ✓ Archived $req_file"
    fi
done

# Create unified Nix approach
echo -e "\n🔧 Creating unified dependency management..."

# Check if using poetry2nix correctly
if grep -q "poetry2nix" flake.nix 2>/dev/null; then
    echo "  ✓ poetry2nix found in flake.nix"
    
    # Create a patch for proper poetry2nix usage
    cat > fix-poetry2nix.patch << 'PATCH'
--- a/flake.nix
+++ b/flake.nix
@@ -30,25 +30,15 @@
       let
         pkgs = nixpkgs.legacyPackages.${system};
         poetry2nix-lib = poetry2nix.lib.mkPoetry2Nix { inherit pkgs; };
         
-        # Manual Python package list - REMOVE THIS
-        poetryEnv = pkgs.python311.withPackages (ps: with ps; [
-          click rich blessed pyperclip
-          # ... other packages
-        ]);
+        # Use poetry2nix to read pyproject.toml
+        poetryEnv = poetry2nix-lib.mkPoetryEnv {
+          projectDir = ./.;
+          python = pkgs.python311;
+          preferWheels = true;
+        };
         
       in {
         devShells.default = pkgs.mkShell {
-          buildInputs = with pkgs; [
-            poetryEnv
-            # ... other inputs
-          ];
+          buildInputs = [ poetryEnv ];
+          
+          shellHook = ''
+            echo "🐍 Python environment from pyproject.toml"
+            echo "✅ All dependencies managed by Poetry + Nix"
+          '';
         };
       };
     };
PATCH
    
    echo "  📄 Created fix-poetry2nix.patch"
    echo "  💡 Apply with: git apply fix-poetry2nix.patch"
fi

# Create dependency validation script
cat > scripts/validate-deps.sh << 'BASH'
#!/usr/bin/env bash
# Validate dependency consistency

set -euo pipefail

echo "🔍 Validating dependencies..."

# Check Poetry lock file
if [ -f "pyproject.toml" ]; then
    echo -n "Checking Poetry lock file... "
    if [ -f "poetry.lock" ]; then
        if poetry check >/dev/null 2>&1; then
            echo "✅ Valid"
        else
            echo "❌ Invalid - run 'poetry lock'"
            exit 1
        fi
    else
        echo "❌ Missing - run 'poetry lock'"
        exit 1
    fi
fi

# Check Nix flake
if [ -f "flake.nix" ]; then
    echo -n "Checking Nix flake... "
    if nix flake check >/dev/null 2>&1; then
        echo "✅ Valid"
    else
        echo "❌ Invalid - check flake.nix"
        exit 1
    fi
fi

# Check for pip usage
echo -n "Checking for pip usage... "
if grep -r "pip install" . --include="*.md" --include="*.py" --include="*.sh" \
   --exclude-dir=".git" --exclude-dir="archive" >/dev/null 2>&1; then
    echo "⚠️  Found pip install references - should use Nix!"
    grep -r "pip install" . --include="*.md" --include="*.py" --include="*.sh" \
        --exclude-dir=".git" --exclude-dir="archive" | head -5
else
    echo "✅ No pip usage found"
fi

echo -e "\n✅ Dependency validation complete"
BASH

chmod +x scripts/validate-deps.sh

# Create development environment tester
cat > scripts/test-dev-env.sh << 'BASH'
#!/usr/bin/env bash
# Test that development environment provides all dependencies

set -euo pipefail

echo "🧪 Testing development environment..."

# Function to test import
test_import() {
    local module=$1
    local name=${2:-$module}
    
    echo -n "  Testing $name... "
    if python -c "import $module" 2>/dev/null; then
        echo "✅"
        return 0
    else
        echo "❌"
        return 1
    fi
}

# Test Python is available
echo -n "Python version: "
python --version

# Test core dependencies
echo -e "\nCore dependencies:"
test_import click
test_import rich
test_import blessed
test_import textual
test_import pytest

# Test optional dependencies
echo -e "\nOptional dependencies:"
test_import whisper "OpenAI Whisper" || true
test_import piper "Piper TTS" || true
test_import torch "PyTorch" || true

# Test development tools
echo -e "\nDevelopment tools:"
which black >/dev/null 2>&1 && echo "  Black... ✅" || echo "  Black... ❌"
which mypy >/dev/null 2>&1 && echo "  Mypy... ✅" || echo "  Mypy... ❌"
which pytest >/dev/null 2>&1 && echo "  Pytest... ✅" || echo "  Pytest... ❌"

# Test Nix for Humanity imports
echo -e "\nProject imports:"
test_import nix_humanity "Nix for Humanity" || echo "    (Expected if not installed)"

echo -e "\n📋 Environment test complete"
BASH

chmod +x scripts/test-dev-env.sh

# Create migration guide
cat > DEPENDENCY_MIGRATION.md << 'MD'
# Dependency Management Migration Guide

## Current State

The project has conflicting dependency management:
- `pyproject.toml` - Poetry configuration (source of truth)
- `flake.nix` - Nix flake with manual Python packages
- Legacy `requirements*.txt` files

## Target State

Single source of truth using Poetry + poetry2nix:
- `pyproject.toml` - Define all dependencies
- `poetry.lock` - Lock versions
- `flake.nix` - Use poetry2nix to read pyproject.toml

## Migration Steps

### 1. Update flake.nix

Replace manual package list with poetry2nix:

```nix
poetryEnv = poetry2nix-lib.mkPoetryEnv {
  projectDir = ./.;
  python = pkgs.python311;
  preferWheels = true;
};
```

### 2. Remove Manual Lists

Delete any manual Python package lists from flake.nix.

### 3. Lock Dependencies

```bash
poetry lock
```

### 4. Test Environment

```bash
nix develop
./scripts/test-dev-env.sh
```

## Benefits

- Single source of truth for dependencies
- Reproducible environments
- No version conflicts
- Easier dependency updates

## Common Issues

### "Module not found" in Nix

Add to pyproject.toml, not flake.nix:
```bash
poetry add package-name
```

### Different Python versions

Ensure flake.nix uses same Python as pyproject.toml:
```toml
[tool.poetry.dependencies]
python = "^3.11"
```

### Optional dependencies

Use Poetry groups:
```toml
[tool.poetry.group.voice.dependencies]
openai-whisper = "^20231117"
```

## Validation

Run regularly:
```bash
./scripts/validate-deps.sh
```
MD

echo -e "\n✅ Dependency cleanup complete!"
echo ""
echo "📋 Summary:"
echo "  - Archived legacy requirements files"
echo "  - Created fix-poetry2nix.patch"
echo "  - Added validation scripts"
echo "  - Created migration guide"
echo ""
echo "🔧 Next steps:"
echo "  1. Apply the patch: git apply fix-poetry2nix.patch"
echo "  2. Run validation: ./scripts/validate-deps.sh"
echo "  3. Test environment: nix develop && ./scripts/test-dev-env.sh"
echo "  4. Remove any remaining pip references"