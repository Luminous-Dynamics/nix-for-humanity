#!/bin/bash
# Build minimal Luminous Nix distribution

set -e

echo "🏗️  Building Minimal Luminous Nix Distribution"
echo "============================================="

# Configuration
DIST_DIR="dist-minimal"
PACKAGE_NAME="luminous-nix-minimal"
VERSION=$(cat VERSION || echo "0.8.0")

# Clean previous builds
rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR/$PACKAGE_NAME"

echo "📦 Copying core files..."

# Copy only essential source files
mkdir -p "$DIST_DIR/$PACKAGE_NAME/src/luminous_nix"

# Core modules (unified)
cp -r src/luminous_nix/core "$DIST_DIR/$PACKAGE_NAME/src/luminous_nix/"

# Essential modules only
for module in cli nix config utils api; do
    if [ -d "src/luminous_nix/$module" ]; then
        cp -r "src/luminous_nix/$module" "$DIST_DIR/$PACKAGE_NAME/src/luminous_nix/"
    fi
done

# AI module (for smart features)
if [ -d "src/luminous_nix/ai" ]; then
    mkdir -p "$DIST_DIR/$PACKAGE_NAME/src/luminous_nix/ai"
    # Only copy essential AI files
    cp src/luminous_nix/ai/__init__.py "$DIST_DIR/$PACKAGE_NAME/src/luminous_nix/ai/" 2>/dev/null || true
    cp src/luminous_nix/ai/ollama_integration.py "$DIST_DIR/$PACKAGE_NAME/src/luminous_nix/ai/" 2>/dev/null || true
    cp src/luminous_nix/ai/nlp.py "$DIST_DIR/$PACKAGE_NAME/src/luminous_nix/ai/" 2>/dev/null || true
fi

# Package init
cp src/luminous_nix/__init__.py "$DIST_DIR/$PACKAGE_NAME/src/luminous_nix/"
cp src/luminous_nix/types.py "$DIST_DIR/$PACKAGE_NAME/src/luminous_nix/" 2>/dev/null || true

# CLI entry point
mkdir -p "$DIST_DIR/$PACKAGE_NAME/bin"
cp bin/ask-nix "$DIST_DIR/$PACKAGE_NAME/bin/"

# Essential project files
cp pyproject.toml "$DIST_DIR/$PACKAGE_NAME/"
cp poetry.lock "$DIST_DIR/$PACKAGE_NAME/" 2>/dev/null || true
cp README.md "$DIST_DIR/$PACKAGE_NAME/"
cp LICENSE "$DIST_DIR/$PACKAGE_NAME/" 2>/dev/null || true
cp VERSION "$DIST_DIR/$PACKAGE_NAME/" 2>/dev/null || true

echo "🧹 Cleaning up unnecessary files..."

# Remove test files from distribution
find "$DIST_DIR/$PACKAGE_NAME" -name "test_*.py" -delete
find "$DIST_DIR/$PACKAGE_NAME" -name "*_test.py" -delete
find "$DIST_DIR/$PACKAGE_NAME" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$DIST_DIR/$PACKAGE_NAME" -name "*.pyc" -delete

# Remove the old duplicate files from core
cd "$DIST_DIR/$PACKAGE_NAME/src/luminous_nix/core"
# Remove old duplicates if they exist
for file in backend_real.py executor.py command_executor.py nix_real_executor.py \
           native_nix_api.py native_operations.py native_operations_advanced.py \
           intent_pipeline.py intent_pipeline_enhanced.py intent_factory.py \
           intent_improvement.py intent_secure_wrapper.py intent_security.py \
           secure_intent_integration.py llm_intent_recognizer.py \
           error_handler.py error_intelligence.py error_intelligence_ast.py \
           error_intelligence_unified.py error_recovery.py error_translator.py \
           educational_errors.py friendly_errors.py graceful_degradation.py \
           responses.py response_adapter.py response_enhancer.py enhanced_output.py; do
    rm -f "$file"
done

# Remove sacred/consciousness files
for file in sacred_pause.py sacred_utils.py conscious_integration.py adaptive_behavior.py; do
    rm -f "$file"
done
cd - > /dev/null

echo "📝 Creating minimal pyproject.toml..."

# Create a minimal pyproject.toml
cat > "$DIST_DIR/$PACKAGE_NAME/pyproject.toml" << 'EOF'
[tool.poetry]
name = "luminous-nix"
version = "0.8.0"
description = "Natural Language Interface for NixOS - Minimal Distribution"
authors = ["Luminous Dynamics"]
readme = "README.md"
packages = [{include = "luminous_nix", from = "src"}]

[tool.poetry.dependencies]
python = "^3.9"
click = "^8.0"
rich = "^13.0"
requests = "^2.28"

[tool.poetry.group.ai]
optional = true

[tool.poetry.group.ai.dependencies]
ollama = "*"

[tool.poetry.scripts]
ask-nix = "luminous_nix.cli:main"
luminous-nix = "luminous_nix.cli:main"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
EOF

echo "📋 Creating minimal README..."

cat > "$DIST_DIR/$PACKAGE_NAME/README.md" << 'EOF'
# Luminous Nix - Minimal Distribution

**Natural Language Interface for NixOS**

## Installation

```bash
pip install luminous-nix
# or
poetry install
```

## Usage

```bash
# Search for packages
ask-nix search firefox

# Install packages
ask-nix install vim

# List installed
ask-nix list

# Get help
ask-nix help
```

## Features

✅ **Core Features** (Included):
- Natural language package management
- Smart package discovery
- Error intelligence
- Progress indicators
- Profile migration

❌ **Not Included** (Available separately):
- GUI (experimental)
- Voice interface
- Consciousness features
- Advanced learning systems

## Minimal by Design

This distribution includes only the essential components needed for natural language NixOS interaction. Additional features are available as extensions.

## License

MIT
EOF

echo "📦 Creating distribution archive..."

cd "$DIST_DIR"
tar -czf "$PACKAGE_NAME-$VERSION.tar.gz" "$PACKAGE_NAME"
cd - > /dev/null

# Calculate sizes
SOURCE_SIZE=$(du -sh src/luminous_nix 2>/dev/null | cut -f1)
DIST_SIZE=$(du -sh "$DIST_DIR/$PACKAGE_NAME" 2>/dev/null | cut -f1)
ARCHIVE_SIZE=$(du -sh "$DIST_DIR/$PACKAGE_NAME-$VERSION.tar.gz" 2>/dev/null | cut -f1)

echo ""
echo "✅ Minimal distribution built successfully!"
echo "========================================="
echo "📊 Size Comparison:"
echo "  Original: $SOURCE_SIZE"
echo "  Minimal:  $DIST_SIZE"
echo "  Archive:  $ARCHIVE_SIZE"
echo ""
echo "📦 Distribution: $DIST_DIR/$PACKAGE_NAME-$VERSION.tar.gz"
echo ""
echo "🚀 To install:"
echo "  tar -xzf $DIST_DIR/$PACKAGE_NAME-$VERSION.tar.gz"
echo "  cd $PACKAGE_NAME"
echo "  poetry install"
echo "  poetry run ask-nix help"
