#!/usr/bin/env bash
# Fix the naming mess - standardize everything to "Luminous Nix"

set -e

echo "🔧 Fixing naming consistency throughout the project"
echo "=================================================="

# Fix Python files
echo "📝 Updating Python files..."
find . -type f -name "*.py" -not -path "./.venv/*" -not -path "./dist*/*" -not -path "./.archive*/*" | while read -r file; do
    if grep -q "Nix for Humanity" "$file" 2>/dev/null; then
        echo "  Fixing: $file"
        sed -i 's/Nix for Humanity/Luminous Nix/g' "$file"
        sed -i 's/nix-for-humanity/luminous-nix/g' "$file"
        sed -i 's/nix_for_humanity/luminous_nix/g' "$file"
        sed -i 's/NixForHumanity/LuminousNix/g' "$file"
    fi
done

# Fix shell scripts
echo "📝 Updating shell scripts..."
find . -type f -name "*.sh" -not -path "./.venv/*" -not -path "./dist*/*" -not -path "./.archive*/*" | while read -r file; do
    if grep -q "Nix for Humanity" "$file" 2>/dev/null; then
        echo "  Fixing: $file"
        sed -i 's/Nix for Humanity/Luminous Nix/g' "$file"
        sed -i 's/nix-for-humanity/luminous-nix/g' "$file"
    fi
done

# Fix Markdown files
echo "📝 Updating Markdown files..."
find . -type f -name "*.md" -not -path "./.venv/*" -not -path "./dist*/*" -not -path "./.archive*/*" | while read -r file; do
    if grep -q "Nix for Humanity" "$file" 2>/dev/null; then
        echo "  Fixing: $file"
        sed -i 's/Nix for Humanity/Luminous Nix/g' "$file"
        sed -i 's/nix-for-humanity/luminous-nix/g' "$file"
    fi
done

# Fix shell.nix
echo "📝 Updating shell.nix..."
sed -i 's/Nix for Humanity/Luminous Nix/g' shell.nix 2>/dev/null || true
sed -i 's/nix-for-humanity/luminous-nix/g' shell.nix 2>/dev/null || true

# Fix pyproject.toml
echo "📝 Updating pyproject.toml..."
sed -i 's/nix-for-humanity/luminous-nix/g' pyproject.toml 2>/dev/null || true
sed -i 's/"Nix for Humanity"/"Luminous Nix"/g' pyproject.toml 2>/dev/null || true

# Update CLI help strings
echo "📝 Updating CLI help strings..."
find src -name "*.py" -exec grep -l "Natural language interface for NixOS" {} \; | while read -r file; do
    echo "  Updating: $file"
    sed -i 's/Nix for Humanity - Natural language interface for NixOS/Luminous Nix - Natural language interface for NixOS/g' "$file"
done

echo ""
echo "✅ Naming consistency fixed!"
echo ""
echo "Summary of changes:"
echo "- Nix for Humanity → Luminous Nix"
echo "- nix-for-humanity → luminous-nix"
echo "- nix_for_humanity → luminous_nix"
echo "- NixForHumanity → LuminousNix"
