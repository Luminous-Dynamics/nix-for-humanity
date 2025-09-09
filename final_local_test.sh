#!/bin/bash
# Final local validation before release

echo "🔍 Final Pre-Release Validation"
echo "================================"

# 1. Test the standalone executable
echo "1️⃣ Testing standalone executable..."
cd dist-intelligent
if ./luminous-nix search "firefox" > /dev/null 2>&1; then
    echo "✅ Standalone search works"
else
    echo "❌ Standalone search failed"
    exit 1
fi

# 2. Test the Python package
echo "2️⃣ Testing Python package import..."
cd ..
if poetry run python -c "from luminous_nix.api.intelligent_api import LuminousNixAPI; print('✅ Python import works')" 2>/dev/null; then
    echo "✅ Python package imports correctly"
else
    echo "❌ Python import failed"
    exit 1
fi

# 3. Quick performance test
echo "3️⃣ Testing performance..."
poetry run python -c "
import time
from luminous_nix.api.intelligent_api import LuminousNixAPI
api = LuminousNixAPI()
start = time.time()
response = api.search('vim')
elapsed = (time.time() - start) * 1000
api.shutdown()
if elapsed < 200:
    print(f'✅ Performance good: {elapsed:.1f}ms')
else:
    print(f'⚠️ Performance slow: {elapsed:.1f}ms')
" 2>/dev/null

# 4. Verify version
echo "4️⃣ Checking version..."
VERSION=$(grep "^version" pyproject.toml | cut -d'"' -f2)
if [ "$VERSION" = "0.5.0" ]; then
    echo "✅ Version correct: $VERSION"
else
    echo "❌ Version mismatch: $VERSION (expected 0.5.0)"
    exit 1
fi

# 5. Check git status
echo "5️⃣ Checking git status..."
if [ -z "$(git status --porcelain)" ]; then
    echo "✅ Working directory clean"
else
    echo "⚠️ Uncommitted changes present:"
    git status --short
fi

echo ""
echo "================================"
echo "✅ Local validation complete!"
echo "Ready for release to GitHub"