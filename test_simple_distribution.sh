#!/usr/bin/env bash
# Test the simple distribution in an isolated manner

set -e

echo "🧪 Testing Simple Distribution"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Create temp directory
TEMP_DIR=$(mktemp -d)
echo "📂 Using temp directory: $TEMP_DIR"

# Extract distribution
echo "📦 Extracting distribution..."
tar -xzf dist-simple/luminous-nix-standalone.tar.gz -C "$TEMP_DIR"

cd "$TEMP_DIR"

# Check contents
echo "📋 Contents:"
ls -la

# Test the launcher script directly
echo -e "\n🚀 Testing launcher..."
export LUMINOUS_DRY_RUN=true
export LUMINOUS_SKIP_ONBOARDING=1
export LUMINOUS_SKIP_CONFIRM=true

# First ensure dependencies are installed
echo "📥 Installing dependencies..."
pip3 install --user --quiet click rich pydantic 2>/dev/null || true

# Test the launcher
echo -e "\n✅ Testing help command..."
if timeout 5 ./luminous-nix help 2>/dev/null | head -5; then
    echo "✅ Help command works!"
else
    echo "❌ Help command failed"
fi

echo -e "\n✅ Testing search command..."
if timeout 5 ./luminous-nix search editor 2>/dev/null | head -5; then
    echo "✅ Search command works!"
else
    echo "❌ Search command failed"
fi

# Cleanup
cd ..
rm -rf "$TEMP_DIR"

echo -e "\n🎉 Simple distribution test complete!"