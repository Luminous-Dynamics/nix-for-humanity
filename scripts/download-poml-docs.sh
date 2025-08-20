#!/bin/bash
# Download comprehensive POML documentation in background

set -e

DOCS_DIR="/srv/luminous-dynamics/11-meta-consciousness/luminous-nix/docs/references/poml"
LOG_FILE="$DOCS_DIR/download.log"

echo "📜 Starting POML documentation download..." | tee "$LOG_FILE"
echo "Timestamp: $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# Function to download with progress
download_with_progress() {
    local url="$1"
    local output="$2"
    local description="$3"
    
    echo "⬇️  Downloading: $description" | tee -a "$LOG_FILE"
    if curl -L --progress-bar "$url" -o "$output" 2>&1 | tee -a "$LOG_FILE"; then
        echo "✅ Success: $description" | tee -a "$LOG_FILE"
    else
        echo "❌ Failed: $description" | tee -a "$LOG_FILE"
    fi
    echo "" | tee -a "$LOG_FILE"
}

# Download official documentation
echo "📚 Downloading official POML documentation..." | tee -a "$LOG_FILE"

# Main documentation pages
download_with_progress \
    "https://raw.githubusercontent.com/microsoft/poml/main/docs/language/quickstart.md" \
    "$DOCS_DIR/official/quickstart.md" \
    "POML Quickstart Guide"

download_with_progress \
    "https://raw.githubusercontent.com/microsoft/poml/main/docs/language/structure.md" \
    "$DOCS_DIR/official/structure.md" \
    "POML Structure Documentation"

download_with_progress \
    "https://raw.githubusercontent.com/microsoft/poml/main/docs/language/poml-functions.md" \
    "$DOCS_DIR/official/poml-functions.md" \
    "POML Functions Reference"

download_with_progress \
    "https://raw.githubusercontent.com/microsoft/poml/main/docs/language/comparison.md" \
    "$DOCS_DIR/official/comparison.md" \
    "POML vs Other Formats"

# Best practices
echo "🎯 Downloading best practices..." | tee -a "$LOG_FILE"

download_with_progress \
    "https://raw.githubusercontent.com/microsoft/poml/main/docs/guides/best-practices.md" \
    "$DOCS_DIR/best-practices/best-practices.md" \
    "POML Best Practices"

download_with_progress \
    "https://raw.githubusercontent.com/microsoft/poml/main/docs/guides/prompt-engineering.md" \
    "$DOCS_DIR/best-practices/prompt-engineering.md" \
    "Prompt Engineering Guide"

download_with_progress \
    "https://raw.githubusercontent.com/microsoft/poml/main/docs/guides/governance.md" \
    "$DOCS_DIR/best-practices/governance.md" \
    "POML Governance Guide"

# Examples
echo "📝 Downloading examples..." | tee -a "$LOG_FILE"

download_with_progress \
    "https://raw.githubusercontent.com/microsoft/poml/main/examples/basic/hello-world.poml" \
    "$DOCS_DIR/examples/hello-world.poml" \
    "Hello World Example"

download_with_progress \
    "https://raw.githubusercontent.com/microsoft/poml/main/examples/advanced/multi-modal.poml" \
    "$DOCS_DIR/examples/multi-modal.poml" \
    "Multi-Modal Example"

download_with_progress \
    "https://raw.githubusercontent.com/microsoft/poml/main/examples/advanced/chain-of-thought.poml" \
    "$DOCS_DIR/examples/chain-of-thought.poml" \
    "Chain of Thought Example"

download_with_progress \
    "https://raw.githubusercontent.com/microsoft/poml/main/examples/advanced/few-shot-learning.poml" \
    "$DOCS_DIR/examples/few-shot-learning.poml" \
    "Few-Shot Learning Example"

# Schema files
echo "📋 Downloading schema definitions..." | tee -a "$LOG_FILE"

download_with_progress \
    "https://raw.githubusercontent.com/microsoft/poml/main/schema/poml-1.0.xsd" \
    "$DOCS_DIR/schemas/poml-1.0.xsd" \
    "POML 1.0 XML Schema"

download_with_progress \
    "https://raw.githubusercontent.com/microsoft/poml/main/schema/poml-spec.json" \
    "$DOCS_DIR/schemas/poml-spec.json" \
    "POML JSON Specification"

# Create index file
echo "📑 Creating documentation index..." | tee -a "$LOG_FILE"

cat > "$DOCS_DIR/README.md" << 'EOF'
# 📜 POML Documentation Library

This directory contains comprehensive POML (Prompt Optimization Markup Language) documentation downloaded from Microsoft's official repository.

## 📂 Directory Structure

### `/official/` - Official Documentation
- `quickstart.md` - Getting started with POML
- `structure.md` - POML document structure
- `poml-functions.md` - Function reference
- `comparison.md` - Comparison with other formats

### `/best-practices/` - Guidelines & Best Practices
- `best-practices.md` - General best practices
- `prompt-engineering.md` - Prompt engineering guide
- `governance.md` - Governance and compliance

### `/examples/` - POML Examples
- `hello-world.poml` - Basic example
- `multi-modal.poml` - Multi-modal inputs
- `chain-of-thought.poml` - Chain of thought reasoning
- `few-shot-learning.poml` - Few-shot learning patterns

### `/schemas/` - Schema Definitions
- `poml-1.0.xsd` - XML Schema Definition
- `poml-spec.json` - JSON specification

## 🔗 Quick Links

- [Official POML Repository](https://github.com/microsoft/poml)
- [POML Documentation Site](https://microsoft.github.io/poml/)
- [Our Implementation](../POML_V2_INTEGRATION.md)

## 📅 Last Updated

$(date)

## 🔄 Update Documentation

Run the download script to refresh:
```bash
./scripts/download-poml-docs.sh
```
EOF

echo "✨ Documentation download complete!" | tee -a "$LOG_FILE"
echo "📂 Files saved to: $DOCS_DIR" | tee -a "$LOG_FILE"
echo "📊 Summary:" | tee -a "$LOG_FILE"
find "$DOCS_DIR" -type f -name "*.md" -o -name "*.poml" -o -name "*.xsd" -o -name "*.json" | wc -l | xargs echo "   Total files downloaded:" | tee -a "$LOG_FILE"
du -sh "$DOCS_DIR" | awk '{print "   Total size: " $1}' | tee -a "$LOG_FILE"