#!/usr/bin/env bash
# Update and install latest Hugging Face dependencies

echo "🤗 Updating Hugging Face dependencies to latest versions..."
echo ""
echo "Latest versions being installed:"
echo "  - transformers: 4.55.0"
echo "  - torch: 2.8.0"
echo "  - accelerate: 0.36.0"
echo "  - datasets: 4.0.0"
echo "  - peft: 0.17.0"
echo "  - sentence-transformers: 3.3.2"
echo "  - huggingface-hub: 0.34.3"
echo "  - safetensors: 0.6.1"
echo "  - And more..."
echo ""

# First update the lock file
echo "📦 Updating poetry.lock file..."
nix-shell -p python313 poetry --run "poetry lock" || {
    echo "❌ Failed to update lock file"
    exit 1
}

echo "✅ Lock file updated!"
echo ""

# Install with increased timeout
echo "🚀 Starting installation (this may take 15-20 minutes)..."
echo "Installing in background to avoid timeouts..."
echo ""

# Run with increased timeout and retry logic
nohup bash -c 'export POETRY_HTTP_TIMEOUT=600; nix-shell -p python313 poetry --run "poetry install --extras \"ml advanced\" -v" || nix-shell -p python313 poetry --run "poetry install --extras \"ml advanced\" -v"' > huggingface-install-v2.log 2>&1 &

echo "✅ Installation started in background!"
echo ""
echo "Monitor progress with:"
echo "  tail -f huggingface-install-v2.log"
echo ""
echo "Check if complete with:"
echo "  ps aux | grep poetry"
echo ""
echo "Once complete, test with:"
echo "  nix-shell -p python313 poetry --run 'poetry run python -c \"import transformers; print(f\"Transformers: {transformers.__version__}\"); import torch; print(f\"PyTorch: {torch.__version__}\")\"'"