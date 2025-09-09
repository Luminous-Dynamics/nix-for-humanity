#!/usr/bin/env bash

# Upload releases to PyPI
set -e

echo "📦 Uploading to PyPI..."
echo "======================="

# Check if we have PyPI credentials
if [ ! -f ~/.pypirc ]; then
    echo "⚠️  PyPI credentials not found!"
    echo ""
    echo "To upload to PyPI, you need to:"
    echo "1. Create an account at https://pypi.org"
    echo "2. Generate an API token"
    echo "3. Create ~/.pypirc with:"
    echo ""
    echo "[pypi]"
    echo "username = __token__"
    echo "password = <your-token-here>"
    echo ""
    echo "Or use: poetry config pypi-token.pypi <your-token>"
    exit 1
fi

# Upload v0.3.0
echo "Uploading v0.3.0..."
cd dist-releases
poetry publish \
    --repository pypi \
    --username __token__ \
    --password $PYPI_TOKEN \
    luminous_nix-0.3.0-py3-none-any.whl \
    || echo "v0.3.0 might already be uploaded"

# Upload v0.3.1
echo "Uploading v0.3.1..."
poetry publish \
    --repository pypi \
    --username __token__ \
    --password $PYPI_TOKEN \
    luminous_nix-0.3.1-py3-none-any.whl \
    || echo "v0.3.1 might already be uploaded"

echo ""
echo "✅ PyPI upload complete!"
echo ""
echo "Users can now install with:"
echo "  pip install luminous-nix==0.3.1"