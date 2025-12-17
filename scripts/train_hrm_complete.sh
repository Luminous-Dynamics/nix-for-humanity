#!/usr/bin/env bash
#
# Complete HRM Training Pipeline
# Executes all steps to train the neural network to 94%+ accuracy
#

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║  HRM Neural Network Training Pipeline                             ║"
echo "║  Target: 94%+ Intent Recognition Accuracy                         ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Data Collection
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📥 STEP 1: Data Collection"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -f "$PROJECT_ROOT/data/real-nixos-queries/nixos_train.json" ]; then
    echo "✓ Training data already exists"
    echo ""
    read -p "Re-collect data? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd "$PROJECT_ROOT"
        poetry run python scripts/collect_real_nixos_queries.py
    fi
else
    echo "Collecting real NixOS queries..."
    cd "$PROJECT_ROOT"
    poetry run python scripts/collect_real_nixos_queries.py
fi

# Verify data exists
if [ ! -f "$PROJECT_ROOT/data/real-nixos-queries/nixos_train.json" ]; then
    echo "❌ Training data not found after collection!"
    exit 1
fi

echo ""
echo "✅ Data collection complete"
echo ""

# Step 2: Training
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧠 STEP 2: Neural Network Training"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "This will train the HierarchicalReasoningModel using PyTorch."
echo "Expected time: 10-30 minutes depending on hardware."
echo ""

read -p "Start training? (Y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    cd "$PROJECT_ROOT"
    poetry run python scripts/train_real_hrm.py
else
    echo "Training skipped."
    exit 0
fi

# Step 3: Validation
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 STEP 3: Model Validation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if trained model exists
if [ -f "$PROJECT_ROOT/models/hrm-nixos-v1/hrm_trained.pt" ]; then
    echo "✅ Trained model found!"
    echo ""

    # Test the trained model
    echo "Testing trained model..."
    cd "$PROJECT_ROOT"
    poetry run python -m luminous_nix.ai.hrm_neural_real

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✨ Training Pipeline Complete!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Model location: models/hrm-nixos-v1/hrm_trained.pt"
    echo "Metrics: models/hrm-nixos-v1/training_metrics.json"
    echo ""
    echo "Next steps:"
    echo "1. Integrate with Meta-Sophia orchestration"
    echo "2. Test with real queries"
    echo "3. Deploy to production"
    echo ""
else
    echo "❌ Trained model not found after training!"
    echo "Check training logs for errors."
    exit 1
fi
