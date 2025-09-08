#!/bin/bash
# Clean up obsolete Ollama models based on testing

echo "🧹 Ollama Model Cleanup"
echo "======================="
echo
echo "Based on comprehensive testing, these models are obsolete:"
echo

# Models to remove (obsolete or redundant)
OBSOLETE_MODELS=(
    # Gemma 2 - replaced by faster Gemma 3
    "gemma2:2b"      # Slower than gemma3:1b
    "gemma2:9b"      # Too slow, gemma3:4b is better
    
    # Old custom models (duplicates)
    "nix-empathy-20250726_1551:latest"
    "nix-coder-20250726_1551:latest"
    "nix-expert-20250726_1551:latest"
    "nix-expert-20250726_1537:latest"
    "nix-empathy-20250726_1537:latest"
    "nix-coder-20250726_1537:latest"
    "nix-quick-20250726_1537:latest"
    "nix-expert-20250726_1530:latest"
    "nix-empathy-20250726_1530:latest"
    "nix-coder:latest"
    "nix-quick:latest"
    "nix-quick-20250726_1551:latest"
    
    # Duplicate/redundant models
    "qwen:0.5b"           # Keep qwen2.5:0.5b instead
    "qwen3:0.6b"          # qwen2.5 series is better
    "qwen3:8b"            # Too large, slow
    "mistral:7b-instruct" # Duplicate of mistral:7b
    "llama3.2:3b"         # gemma3:1b is faster
    "phi3:mini"           # gemma3:1b is better
    "deepseek-r1:8b"      # Too large for our needs
)

echo "Models to remove:"
for model in "${OBSOLETE_MODELS[@]}"; do
    echo "  ❌ $model"
done

echo
echo "Models to KEEP (optimized set):"
echo "  ✅ gemma3:270m    (291 MB) - ULTRA FAST primary"
echo "  ✅ gemma3:1b      (815 MB) - Fast fallback"
echo "  ✅ gemma3:4b      (3.3 GB) - Complex queries"
echo "  ✅ gemma3:12b     (8.1 GB) - Maximum intelligence"
echo "  ✅ qwen2.5:0.5b   (397 MB) - Alternative ultra-fast"
echo "  ✅ qwen2.5:3b     (1.9 GB) - Alternative medium"
echo "  ✅ tinyllama:1.1b (637 MB) - Compatibility fallback"
echo "  ✅ mistral:7b     (4.4 GB) - Original default (backup)"
echo

read -p "Remove obsolete models? This will free ~45GB of space (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️ Removing obsolete models..."
    for model in "${OBSOLETE_MODELS[@]}"; do
        echo -n "  Removing $model... "
        if ollama rm "$model" 2>/dev/null; then
            echo "✅"
        else
            echo "⚠️ Not found or already removed"
        fi
    done
    echo
    echo "✨ Cleanup complete!"
    echo
    echo "📊 Space saved:"
    echo "  Before: ~70GB of models"
    echo "  After:  ~18GB of models"
    echo "  Saved:  ~52GB!"
else
    echo "❌ Cleanup cancelled"
fi

echo
echo "📋 Final optimized model set for Luminous Nix:"
echo "================================================"
ollama list | grep -E "gemma3|qwen2.5|tinyllama|mistral:7b[^-]" | awk '{print $1, $3, $4}' | column -t