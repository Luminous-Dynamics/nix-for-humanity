#!/usr/bin/env python3
"""
REAL PyTorch training for HRM neural network.

This is NOT a simulation - it actually trains the neural network.
Target: 94%+ accuracy on NixOS intent classification.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
import time
import logging
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the real HRM architecture
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from luminous_nix.ai.hrm_neural_real import HierarchicalReasoningModel

@dataclass
class TrainingConfig:
    """Training configuration"""
    # Model architecture
    vocab_size: int = 258  # Character-level encoding
    num_intents: int = 10
    embedding_dim: int = 128
    hidden_dim: int = 256
    num_layers: int = 2
    dropout: float = 0.3

    # Training parameters
    batch_size: int = 32
    learning_rate: float = 0.001
    epochs: int = 50
    early_stopping_patience: int = 10

    # Paths
    data_dir: Path = Path("data/real-nixos-queries")
    model_dir: Path = Path("models/hrm-nixos-v1")

    # Device
    device: str = 'cuda' if torch.cuda.is_available() else 'cpu'

class NixOSQueryDataset(Dataset):
    """PyTorch Dataset for NixOS queries"""

    def __init__(self, data_path: Path, max_length: int = 100):
        """Load queries from JSON file"""
        with open(data_path, 'r') as f:
            self.data = json.load(f)

        self.max_length = max_length

        # Build vocabulary (character-level)
        self.char_to_idx = {chr(i): i for i in range(256)}
        self.char_to_idx['<PAD>'] = 256
        self.char_to_idx['<UNK>'] = 257

        # Intent mapping
        self.intent_to_idx = {
            'search': 0, 'install': 1, 'remove': 2, 'update': 3,
            'info': 4, 'list': 5, 'help': 6, 'config': 7,
            'shell': 8, 'flake': 9
        }
        self.idx_to_intent = {v: k for k, v in self.intent_to_idx.items()}

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        """Get a single training example"""
        item = self.data[idx]

        # Encode query text
        query = item['text'].lower()[:self.max_length]

        encoded = []
        for char in query:
            if char in self.char_to_idx:
                encoded.append(self.char_to_idx[char])
            else:
                encoded.append(self.char_to_idx['<UNK>'])

        # Pad to max length
        while len(encoded) < self.max_length:
            encoded.append(self.char_to_idx['<PAD>'])

        # Intent label
        intent = item['intent']
        label = self.intent_to_idx.get(intent, self.intent_to_idx['help'])

        return {
            'input': torch.tensor(encoded[:self.max_length], dtype=torch.long),
            'label': torch.tensor(label, dtype=torch.long),
            'text': query,
            'intent': intent
        }

class HRMTrainer:
    """Real PyTorch trainer for HRM"""

    def __init__(self, config: TrainingConfig):
        self.config = config

        # Create model directory
        config.model_dir.mkdir(parents=True, exist_ok=True)

        # Initialize model
        self.model = HierarchicalReasoningModel(
            vocab_size=config.vocab_size,
            num_intents=config.num_intents,
            embedding_dim=config.embedding_dim,
            hidden_dim=config.hidden_dim,
            num_layers=config.num_layers,
            dropout=config.dropout
        )

        # Move to device
        self.device = torch.device(config.device)
        self.model.to(self.device)

        # Optimizer and loss
        self.optimizer = optim.Adam(
            self.model.parameters(),
            lr=config.learning_rate
        )
        self.criterion = nn.CrossEntropyLoss()

        # Training state
        self.best_val_accuracy = 0.0
        self.patience_counter = 0
        self.training_history = []

        logger.info(f"✅ HRM Trainer initialized")
        logger.info(f"   Model parameters: {sum(p.numel() for p in self.model.parameters()):,}")
        logger.info(f"   Device: {self.device}")

    def train_epoch(self, train_loader: DataLoader) -> Dict:
        """Train for one epoch"""
        self.model.train()

        total_loss = 0.0
        correct = 0
        total = 0

        for batch in train_loader:
            # Move to device
            inputs = batch['input'].to(self.device)
            labels = batch['label'].to(self.device)

            # Forward pass
            self.optimizer.zero_grad()
            outputs = self.model(inputs)

            # Compute loss
            loss = self.criterion(outputs, labels)

            # Backward pass
            loss.backward()
            self.optimizer.step()

            # Track metrics
            total_loss += loss.item()

            _, predicted = torch.max(outputs, 1)
            correct += (predicted == labels).sum().item()
            total += labels.size(0)

        return {
            'loss': total_loss / len(train_loader),
            'accuracy': correct / total
        }

    def validate(self, val_loader: DataLoader) -> Dict:
        """Validate model"""
        self.model.eval()

        total_loss = 0.0
        correct = 0
        total = 0

        with torch.no_grad():
            for batch in val_loader:
                inputs = batch['input'].to(self.device)
                labels = batch['label'].to(self.device)

                outputs = self.model(inputs)
                loss = self.criterion(outputs, labels)

                total_loss += loss.item()

                _, predicted = torch.max(outputs, 1)
                correct += (predicted == labels).sum().item()
                total += labels.size(0)

        return {
            'loss': total_loss / len(val_loader),
            'accuracy': correct / total
        }

    def save_checkpoint(self, epoch: int, metrics: Dict, is_best: bool = False):
        """Save model checkpoint"""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'metrics': metrics,
            'vocab_size': self.config.vocab_size,
            'num_intents': self.config.num_intents,
            'intent_to_idx': {
                'search': 0, 'install': 1, 'remove': 2, 'update': 3,
                'info': 4, 'list': 5, 'help': 6, 'config': 7,
                'shell': 8, 'flake': 9
            },
            'idx_to_intent': {
                0: 'search', 1: 'install', 2: 'remove', 3: 'update',
                4: 'info', 5: 'list', 6: 'help', 7: 'config',
                8: 'shell', 9: 'flake'
            },
            'best_val_acc': self.best_val_accuracy,
            'accuracy': metrics['val_accuracy'] * 100,  # Percentage
            'training_history': self.training_history
        }

        # Save checkpoint
        if is_best:
            checkpoint_path = self.config.model_dir / "hrm_trained.pt"
            torch.save(checkpoint, checkpoint_path)
            logger.info(f"  💾 Best model saved: {checkpoint_path}")

        # Also save periodic checkpoint
        periodic_path = self.config.model_dir / f"hrm_epoch_{epoch}.pt"
        torch.save(checkpoint, periodic_path)

    def train(self, train_path: Path, val_path: Path, test_path: Path = None):
        """Full training loop"""

        print("\n" + "=" * 70)
        print("🧠 REAL HRM Training (PyTorch)")
        print("=" * 70)
        print(f"Model: HierarchicalReasoningModel")
        print(f"Parameters: {sum(p.numel() for p in self.model.parameters()):,}")
        print(f"Device: {self.device}")
        print(f"Batch size: {self.config.batch_size}")
        print(f"Learning rate: {self.config.learning_rate}")
        print(f"Epochs: {self.config.epochs}")
        print(f"Target accuracy: 94%+")
        print("=" * 70)

        # Load datasets
        logger.info("\n📂 Loading datasets...")
        train_dataset = NixOSQueryDataset(train_path)
        val_dataset = NixOSQueryDataset(val_path)

        train_loader = DataLoader(
            train_dataset,
            batch_size=self.config.batch_size,
            shuffle=True,
            num_workers=0  # Set to 0 for compatibility
        )

        val_loader = DataLoader(
            val_dataset,
            batch_size=self.config.batch_size,
            shuffle=False,
            num_workers=0
        )

        logger.info(f"  Training: {len(train_dataset)} examples")
        logger.info(f"  Validation: {len(val_dataset)} examples")
        logger.info(f"  Batches per epoch: {len(train_loader)}")

        # Training loop
        print("\n" + "=" * 70)
        print("🚀 Starting training...")
        print("=" * 70)

        for epoch in range(self.config.epochs):
            start_time = time.time()

            # Train
            train_metrics = self.train_epoch(train_loader)

            # Validate
            val_metrics = self.validate(val_loader)

            # Record history
            epoch_metrics = {
                'epoch': epoch + 1,
                'train_loss': train_metrics['loss'],
                'train_accuracy': train_metrics['accuracy'],
                'val_loss': val_metrics['loss'],
                'val_accuracy': val_metrics['accuracy']
            }
            self.training_history.append(epoch_metrics)

            # Time
            epoch_time = time.time() - start_time

            # Print progress
            print(f"\nEpoch {epoch + 1}/{self.config.epochs} ({epoch_time:.1f}s)")
            print(f"  Train - Loss: {train_metrics['loss']:.4f}, Acc: {train_metrics['accuracy']:.2%}")
            print(f"  Val   - Loss: {val_metrics['loss']:.4f}, Acc: {val_metrics['accuracy']:.2%}")

            # Check if this is the best model
            if val_metrics['accuracy'] > self.best_val_accuracy:
                self.best_val_accuracy = val_metrics['accuracy']
                self.patience_counter = 0

                # Save best model
                self.save_checkpoint(epoch + 1, {
                    'train_accuracy': train_metrics['accuracy'],
                    'val_accuracy': val_metrics['accuracy'],
                    'train_loss': train_metrics['loss'],
                    'val_loss': val_metrics['loss']
                }, is_best=True)

                print(f"  ⭐ New best model! ({val_metrics['accuracy']:.2%})")

                # Check if we've reached target
                if val_metrics['accuracy'] >= 0.94:
                    print("\n🎉 TARGET REACHED: 94%+ accuracy!")
            else:
                self.patience_counter += 1

                if self.patience_counter >= self.config.early_stopping_patience:
                    print(f"\n🛑 Early stopping (patience: {self.config.early_stopping_patience})")
                    break

            # Periodic checkpoint (every 10 epochs)
            if (epoch + 1) % 10 == 0:
                self.save_checkpoint(epoch + 1, epoch_metrics)

        # Training complete
        print("\n" + "=" * 70)
        print("✅ Training Complete!")
        print(f"Best validation accuracy: {self.best_val_accuracy:.2%}")
        print(f"Model saved to: {self.config.model_dir / 'hrm_trained.pt'}")
        print("=" * 70)

        # Test evaluation if provided
        if test_path and test_path.exists():
            print("\n📊 Evaluating on test set...")
            test_dataset = NixOSQueryDataset(test_path)
            test_loader = DataLoader(test_dataset, batch_size=self.config.batch_size)

            test_metrics = self.validate(test_loader)

            print(f"\n🎯 Test Results:")
            print(f"  Accuracy: {test_metrics['accuracy']:.2%}")
            print(f"  Loss: {test_metrics['loss']:.4f}")

            # Save test metrics
            final_metrics = {
                'best_val_accuracy': self.best_val_accuracy,
                'test_accuracy': test_metrics['accuracy'],
                'test_loss': test_metrics['loss'],
                'training_history': self.training_history
            }

            metrics_file = self.config.model_dir / "training_metrics.json"
            with open(metrics_file, 'w') as f:
                json.dump(final_metrics, f, indent=2)

            logger.info(f"📁 Metrics saved: {metrics_file}")

        return self.best_val_accuracy

def main():
    """Main training pipeline"""

    # Configuration
    config = TrainingConfig(
        batch_size=32,
        learning_rate=0.001,
        epochs=50,
        early_stopping_patience=10
    )

    # Check if data exists
    train_path = config.data_dir / "nixos_train.json"
    val_path = config.data_dir / "nixos_validation.json"
    test_path = config.data_dir / "nixos_test.json"

    if not train_path.exists():
        print("❌ Training data not found!")
        print("Run: python scripts/collect_real_nixos_queries.py")
        return

    # Create trainer
    trainer = HRMTrainer(config)

    # Train model
    best_accuracy = trainer.train(train_path, val_path, test_path)

    print("\n" + "=" * 70)
    print("🎯 Next Steps:")
    print("=" * 70)
    if best_accuracy >= 0.94:
        print("✅ Model achieved 94%+ accuracy - READY FOR PRODUCTION!")
        print("1. The model is saved at: models/hrm-nixos-v1/hrm_trained.pt")
        print("2. It will be automatically loaded by hrm_neural_real.py")
        print("3. Test with: python -m luminous_nix.ai.hrm_neural_real")
    else:
        print(f"⚠️ Model achieved {best_accuracy:.2%} accuracy")
        print("1. Collect more training data")
        print("2. Adjust hyperparameters (learning rate, batch size)")
        print("3. Try data augmentation")
        print("4. Increase model capacity")
    print("=" * 70)

if __name__ == "__main__":
    main()
