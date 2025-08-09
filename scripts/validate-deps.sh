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
