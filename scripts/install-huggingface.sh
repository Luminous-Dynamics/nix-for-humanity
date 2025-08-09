#!/usr/bin/env bash
# Install Hugging Face dependencies in background

echo "🤗 Installing Hugging Face dependencies..."
echo "This may take 10-15 minutes for first installation."
echo ""

# Run installation in background
nohup nix-shell -p python313 poetry --run "poetry install --extras 'ml advanced'" > huggingface-install.log 2>&1 &

echo "✅ Installation started in background!"
echo ""
echo "Monitor progress with:"
echo "  tail -f huggingface-install.log"
echo ""
echo "Check if complete with:"
echo "  ps aux | grep poetry"
echo ""
echo "Once complete, test with:"
echo "  nix-shell -p python313 poetry --run 'poetry run python -c \"import transformers; print(transformers.__version__)\"'"