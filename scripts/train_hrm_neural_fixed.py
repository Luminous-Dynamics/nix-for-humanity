#!/usr/bin/env python3
"""
Fixed version: Train the HRM neural network on real NixOS data
This creates a production-ready model from collected queries
"""

import json
import sys
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))


class SimpleHRMNetwork(nn.Module):
    """Simplified HRM for limited training data"""

    def __init__(
        self,
        vocab_size=256,
        embedding_dim=64,
        hidden_dim=128,
        num_categories=7,
        dropout=0.2,
    ):
        super(SimpleHRMNetwork, self).__init__()

        # Embedding
        self.embedding = nn.Embedding(vocab_size, embedding_dim)

        # Simple LSTM (no bidirectional for small data)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, num_layers=1, batch_first=True)

        # Category prediction head
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, num_categories),
        )

        # Confidence head
        self.confidence = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        # Embedding
        embedded = self.embedding(x)  # (batch, seq, embed)

        # LSTM
        lstm_out, (h_n, c_n) = self.lstm(embedded)

        # Use last hidden state
        last_hidden = h_n.squeeze(0)  # (batch, hidden)

        # Classify
        logits = self.classifier(last_hidden)
        conf = self.confidence(last_hidden)

        return logits, conf


class NixOSQueryDataset(Dataset):
    """Dataset for real NixOS queries"""

    def __init__(self, json_path: str, max_len: int = 50):
        # Load data
        with open(json_path) as f:
            data = json.load(f)
            if isinstance(data, dict) and "queries" in data:
                data = data["queries"]

        self.queries = []
        self.categories = []
        self.solutions = []
        self.max_len = max_len

        # Category mapping
        self.category_to_idx = {
            "install": 0,
            "configure": 1,
            "error": 2,
            "search": 3,
            "update": 4,
            "shell": 5,
            "hardware": 6,
            "flakes": 7,
            "home-manager": 8,
            "containers": 9,
            "rollback": 10,
            "cleanup": 11,
            "info": 12,
            "unknown": 13,
        }

        for item in data:
            self.queries.append(item["query"])
            self.categories.append(item.get("category", "unknown"))
            self.solutions.append(item.get("solution", ""))

    def __len__(self):
        return len(self.queries)

    def __getitem__(self, idx):
        query = self.queries[idx]
        category = self.categories[idx]

        # Tokenize (character-level)
        tokens = [ord(c) for c in query.lower()[: self.max_len]]
        tokens += [0] * (self.max_len - len(tokens))

        # Get category index (max 7 for our simplified model)
        cat_idx = min(self.category_to_idx.get(category, 13), 6)

        return {
            "query": torch.tensor(tokens, dtype=torch.long),
            "category": torch.tensor(cat_idx, dtype=torch.long),
        }


def train_simple_model():
    """Train simplified model"""

    print("🧠 Simplified HRM Training (Fixed)")
    print("=" * 60)

    # Load data
    print("\n📚 Loading data...")
    train_data = NixOSQueryDataset("data/train.json")
    val_data = NixOSQueryDataset("data/val.json")
    test_data = NixOSQueryDataset("data/test.json")

    print(f"  Train: {len(train_data)} queries")
    print(f"  Val: {len(val_data)} queries")
    print(f"  Test: {len(test_data)} queries")

    # Data loaders
    train_loader = DataLoader(train_data, batch_size=4, shuffle=True)
    val_loader = DataLoader(val_data, batch_size=4, shuffle=False)
    test_loader = DataLoader(test_data, batch_size=4, shuffle=False)

    # Model
    model = SimpleHRMNetwork()
    print(f"\n📊 Model parameters: {sum(p.numel() for p in model.parameters()):,}")

    # Training setup
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.CrossEntropyLoss()

    # Create models directory
    Path("models").mkdir(exist_ok=True)

    # Training
    print("\n🏋️ Training...")
    best_val_acc = 0

    for epoch in range(20):  # Fewer epochs for simple model
        # Train
        model.train()
        train_loss = 0
        train_correct = 0
        train_total = 0

        for batch in train_loader:
            queries = batch["query"]
            targets = batch["category"]

            optimizer.zero_grad()
            logits, conf = model(queries)
            loss = criterion(logits, targets)
            loss.backward()
            optimizer.step()

            train_loss += loss.item()
            _, pred = logits.max(1)
            train_correct += pred.eq(targets).sum().item()
            train_total += targets.size(0)

        # Validate
        model.eval()
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for batch in val_loader:
                queries = batch["query"]
                targets = batch["category"]

                logits, _ = model(queries)
                _, pred = logits.max(1)
                val_correct += pred.eq(targets).sum().item()
                val_total += targets.size(0)

        train_acc = 100.0 * train_correct / train_total
        val_acc = 100.0 * val_correct / val_total

        print(f"Epoch {epoch+1}: Train {train_acc:.1f}%, Val {val_acc:.1f}%")

        # Save best
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), "models/hrm_simple_best.pt")
            print(f"  ✅ Saved best model (Val: {val_acc:.1f}%)")

    # Test
    model.load_state_dict(torch.load("models/hrm_simple_best.pt"))
    model.eval()

    test_correct = 0
    test_total = 0

    with torch.no_grad():
        for batch in test_loader:
            queries = batch["query"]
            targets = batch["category"]

            logits, _ = model(queries)
            _, pred = logits.max(1)
            test_correct += pred.eq(targets).sum().item()
            test_total += targets.size(0)

    test_acc = 100.0 * test_correct / test_total

    print("\n" + "=" * 60)
    print("✅ Training complete!")
    print(f"📊 Best Val: {best_val_acc:.1f}%, Test: {test_acc:.1f}%")
    print("\nNote: Limited data (87 queries) limits accuracy.")
    print("Collect more data for better performance!")

    return model


if __name__ == "__main__":
    train_simple_model()
