#!/bin/bash
# Wrapper script for production release preparation

set -e

echo "🚀 Preparing Nix for Humanity v1.0.0 Production Release"
echo "========================================================"
echo ""

# Ensure we're in the right directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check for required files
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Must run from nix-for-humanity root directory"
    exit 1
fi

# Run the release preparation script
python3 scripts/prepare-production-release.py

echo ""
echo "🎯 Quick Actions:"
echo "  - Review generated files: cd release/v1.0.0/"
echo "  - Run tests: pytest tests/"
echo "  - Create package: cd release/v1.0.0 && python3 create_package.py"
echo "  - Tag release: git tag -a v1.0.0 -m 'Release v1.0.0'"
echo ""
echo "📚 Full instructions in: release/v1.0.0/RELEASE_SUMMARY.md"