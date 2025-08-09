#!/bin/bash
# Sacred Feature Promotion Script
# Lovingly moves features from preservation to active development

set -e

FEATURE_PATH=$1
PROJECT_ROOT=$(dirname $(dirname $(realpath $0)))

if [ -z "$FEATURE_PATH" ]; then
    echo "🌟 Sacred Feature Promotion Tool"
    echo ""
    echo "Usage: $0 <feature-path>"
    echo ""
    echo "Example: $0 v1.5/tui"
    echo ""
    echo "Available features to promote:"
    find "$PROJECT_ROOT/features" -mindepth 2 -maxdepth 2 -type d | sed "s|$PROJECT_ROOT/features/||"
    exit 1
fi

FEATURE_DIR="$PROJECT_ROOT/features/$FEATURE_PATH"
FEATURE_NAME=$(basename "$FEATURE_PATH")
VERSION=$(dirname "$FEATURE_PATH")

if [ ! -d "$FEATURE_DIR" ]; then
    echo "❌ Feature not found: $FEATURE_DIR"
    exit 1
fi

echo "🌺 Promoting feature: $FEATURE_NAME from $VERSION"
echo ""

# Sacred pause for reflection
echo "This will:"
echo "  1. Move $FEATURE_NAME to active development"
echo "  2. Update feature flags to enable it"
echo "  3. Run tests to ensure harmony"
echo ""
read -p "Continue with love? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "💝 Promotion cancelled with understanding"
    exit 0
fi

echo ""
echo "✨ Beginning sacred promotion..."

# Determine target directory based on feature type
case "$FEATURE_NAME" in
    tui|voice)
        TARGET_DIR="$PROJECT_ROOT/src/frontends/$FEATURE_NAME"
        ;;
    learning|personas|patterns)
        TARGET_DIR="$PROJECT_ROOT/src/backend/$FEATURE_NAME"
        ;;
    *)
        TARGET_DIR="$PROJECT_ROOT/src/$FEATURE_NAME"
        ;;
esac

# Create target directory if needed
mkdir -p "$(dirname "$TARGET_DIR")"

# Move with love
echo "📦 Moving $FEATURE_NAME to $TARGET_DIR..."
cp -r "$FEATURE_DIR" "$TARGET_DIR"

# Update feature flags
echo "🎯 Updating feature flags..."
FEATURE_FLAG_PATH="${VERSION}.${FEATURE_NAME}"
python3 - <<EOF
import yaml
import sys

config_path = "$PROJECT_ROOT/config/feature-flags.yaml"

with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Navigate to the feature flag
parts = "$FEATURE_FLAG_PATH".split('.')
current = config
for part in parts[:-1]:
    if part not in current:
        print(f"Warning: Creating new section {part}")
        current[part] = {'enabled': True, 'features': {}}
    current = current[part]['features'] if 'features' in current[part] else current[part]

# Enable the feature
feature = parts[-1]
current[feature] = True

# Also enable the version if not already
version_key = "$VERSION"
if version_key in config and 'enabled' in config[version_key]:
    config[version_key]['enabled'] = True

# Write back
with open(config_path, 'w') as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False)

print(f"✅ Feature flag {feature} enabled for {version_key}")
EOF

# Run tests if they exist
TEST_DIR="$PROJECT_ROOT/tests/future/$VERSION"
if [ -d "$TEST_DIR" ]; then
    echo "🧪 Running tests for promoted feature..."
    cd "$PROJECT_ROOT"
    pytest "$TEST_DIR" -v || {
        echo "⚠️ Tests failed, but feature is promoted. Please fix tests!"
    }
else
    echo "📝 No tests found for this feature. Consider adding some!"
fi

# Create a promotion record
RECORD_FILE="$PROJECT_ROOT/features/PROMOTION_HISTORY.md"
echo "" >> "$RECORD_FILE"
echo "## $(date '+%Y-%m-%d') - $FEATURE_NAME promoted to active" >> "$RECORD_FILE"
echo "- **Feature**: $FEATURE_NAME" >> "$RECORD_FILE"
echo "- **From**: $VERSION" >> "$RECORD_FILE"
echo "- **To**: Active development" >> "$RECORD_FILE"
echo "- **Promoted by**: Sacred script with love" >> "$RECORD_FILE"

echo ""
echo "🎉 Feature promotion complete!"
echo ""
echo "Next steps:"
echo "  1. Update imports in your code to use the active version"
echo "  2. Remove the feature from $FEATURE_DIR when ready"
echo "  3. Celebrate this sacred evolution! 🌟"
echo ""
echo "The feature is now active at: $TARGET_DIR"