#!/usr/bin/env python3
"""
Train the HRM neural network on real NixOS data
This creates a production-ready model from collected queries
"""

import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import numpy as np
from pathlib import Path
import time
import sys
import os

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

# Import our HRM components
from luminous_nix.ai.hrm_neural import HRMNeuralNetwork, NeuralHRM, NixOSDataset


class NixOSQueryDataset(Dataset):
    """Dataset for real NixOS queries from our collected data"""

    def __init__(self, json_path: str, max_len: int = 50):
        with open(json_path, "r") as f:
            if "queries" in json.load(open(json_path)):
                # Full dataset format
                data = json.load(open(json_path))["queries"]
            else:
                # Split format (train/val/test)
                data = json.load(open(json_path))

        self.queries = []
        self.solutions = []
        self.categories = []
        self.max_len = max_len

        # Extract data
        for item in data:
            self.queries.append(item["query"])
            self.solutions.append(item["solution"])
            self.categories.append(item.get("category", "unknown"))

        # Map categories to indices
        self.category_to_idx = {
            "install": 0,
            "configure": 1,
            "error": 2,
            "search": 3,
            "update": 4,
            "shell": 5,
            "unknown": 6,
        }

    def __len__(self):
        return len(self.queries)

    def __getitem__(self, idx):
        query = self.queries[idx]
        solution = self.solutions[idx]
        category = self.categories[idx]

        # Simple character-level tokenization
        query_tokens = [ord(c) for c in query.lower()[: self.max_len]]
        query_tokens += [0] * (self.max_len - len(query_tokens))

        # Category as target
        category_idx = self.category_to_idx.get(category, 6)

        return {
            "query": torch.tensor(query_tokens, dtype=torch.long),
            "category": torch.tensor(category_idx, dtype=torch.long),
            "solution_text": solution,  # Keep for reference
        }


def train_model(model, train_loader, val_loader, epochs=20, device="cpu"):
    """Train the HRM neural network"""

    model = model.to(device)
    optimizer = optim.AdamW(model.parameters(), lr=1e-3)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=3, factor=0.5)
    criterion = nn.CrossEntropyLoss()

    best_val_acc = 0
    history = {"train_loss": [], "train_acc": [], "val_loss": [], "val_acc": []}

    print("\n🏋️ Starting training...")
    print("=" * 60)

    for epoch in range(epochs):
        # Training phase
        model.train()
        train_loss = 0
        train_correct = 0
        train_total = 0

        for batch in train_loader:
            queries = batch["query"].to(device)
            targets = batch["category"].to(device)

            optimizer.zero_grad()

            # Forward pass
            strategy_logits, confidence = model(queries)

            # Calculate loss
            loss = criterion(strategy_logits, targets)

            # Add confidence regularization
            predicted_correct = (strategy_logits.argmax(dim=1) == targets).float()
            confidence_loss = nn.functional.mse_loss(
                confidence.squeeze(), predicted_correct
            )
            total_loss = loss + 0.1 * confidence_loss

            # Backward pass
            total_loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            # Track metrics
            train_loss += loss.item()
            _, predicted = strategy_logits.max(1)
            train_total += targets.size(0)
            train_correct += predicted.eq(targets).sum().item()

        # Validation phase
        model.eval()
        val_loss = 0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for batch in val_loader:
                queries = batch["query"].to(device)
                targets = batch["category"].to(device)

                strategy_logits, confidence = model(queries)
                loss = criterion(strategy_logits, targets)

                val_loss += loss.item()
                _, predicted = strategy_logits.max(1)
                val_total += targets.size(0)
                val_correct += predicted.eq(targets).sum().item()

        # Calculate metrics
        train_acc = 100.0 * train_correct / train_total
        val_acc = 100.0 * val_correct / val_total
        avg_train_loss = train_loss / len(train_loader)
        avg_val_loss = val_loss / len(val_loader)

        # Update history
        history["train_loss"].append(avg_train_loss)
        history["train_acc"].append(train_acc)
        history["val_loss"].append(avg_val_loss)
        history["val_acc"].append(val_acc)

        # Update learning rate
        scheduler.step(avg_val_loss)

        # Print progress
        print(f"Epoch {epoch+1}/{epochs}:")
        print(f"  Train Loss: {avg_train_loss:.4f}, Train Acc: {train_acc:.1f}%")
        print(f"  Val Loss: {avg_val_loss:.4f}, Val Acc: {val_acc:.1f}%")

        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(
                {
                    "epoch": epoch,
                    "model_state_dict": model.state_dict(),
                    "optimizer_state_dict": optimizer.state_dict(),
                    "val_acc": val_acc,
                    "history": history,
                },
                "models/hrm_neural_best.pt",
            )
            print(f"  ✅ Saved best model (Val Acc: {val_acc:.1f}%)")

        print()

    return history, best_val_acc


def main():
    """Main training script"""

    print("🧠 HRM Neural Network Training")
    print("=" * 60)

    # Check for data
    data_path = Path("data")
    if not (data_path / "train.json").exists():
        print("❌ Training data not found. Run scrape_nixos_discourse.py first!")
        return

    # Load datasets
    print("\n📚 Loading datasets...")
    train_dataset = NixOSQueryDataset("data/train.json")
    val_dataset = NixOSQueryDataset("data/val.json")
    test_dataset = NixOSQueryDataset("data/test.json")

    print(f"  Train: {len(train_dataset)} queries")
    print(f"  Val: {len(val_dataset)} queries")
    print(f"  Test: {len(test_dataset)} queries")

    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=8, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=8, shuffle=False)

    # Initialize model
    print("\n🏗️ Initializing model...")
    model = HRMNeuralNetwork(
        vocab_size=256,
        embedding_dim=64,  # Smaller for limited data
        hidden_dim=128,  # Smaller for limited data
        num_strategies=7,  # 7 categories
        num_layers=1,  # Simpler for limited data
        dropout=0.2,  # More dropout for limited data
    )

    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    print(f"  Total parameters: {total_params:,}")
    print(f"  Model size: ~{total_params * 4 / 1024 / 1024:.1f} MB")

    # Create models directory
    Path("models").mkdir(exist_ok=True)

    # Train model
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\n🖥️ Training on: {device}")

    history, best_acc = train_model(
        model,
        train_loader,
        val_loader,
        epochs=30,  # More epochs for small dataset
        device=device,
    )

    print("\n" + "=" * 60)
    print(f"✅ Training complete!")
    print(f"📊 Best validation accuracy: {best_acc:.1f}%")

    # Test the model
    print("\n🧪 Testing final model...")

    # Load best model
    checkpoint = torch.load("models/hrm_neural_best.pt", map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    # Test accuracy
    test_correct = 0
    test_total = 0

    with torch.no_grad():
        for batch in test_loader:
            queries = batch["query"].to(device)
            targets = batch["category"].to(device)

            strategy_logits, _ = model(queries)
            _, predicted = strategy_logits.max(1)
            test_total += targets.size(0)
            test_correct += predicted.eq(targets).sum().item()

    test_acc = 100.0 * test_correct / test_total
    print(f"📈 Test accuracy: {test_acc:.1f}%")

    # Save production model
    print("\n💾 Saving production model...")
    production_model = NeuralHRM(device=device)
    production_model.model.load_state_dict(model.state_dict())
    production_model.save_model("models/hrm_neural_production.pt")

    print("\n🎯 Next steps:")
    print("  1. Integrate model: python scripts/integrate_hrm.py")
    print("  2. Test inference: python scripts/test_inference.py")
    print("  3. Deploy to production: python scripts/deploy_v0.2.0.py")

    # Test a few predictions
    print("\n🔮 Sample predictions:")
    test_queries = [
        "install firefox",
        "configure nginx",
        "error collision between packages",
        "search for text editor",
    ]

    production_model = NeuralHRM("models/hrm_neural_production.pt", device=device)

    for query in test_queries:
        result = production_model.predict(query)
        print(f"\nQuery: '{query}'")
        print(f"  Strategy: {result['strategy']}")
        print(f"  Confidence: {result['confidence']:.1%}")
        print(f"  Solution: {result['solution'][:60]}...")


if __name__ == "__main__":
    main()
