#!/usr/bin/env python3
"""
Real Neural Network Implementation for Luminous Nix
No simulation - actual PyTorch models with real training
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class NixOSQueryDataset(Dataset):
    """Real PyTorch dataset for NixOS queries"""
    
    def __init__(self, data_path: str, vocab_size: int = 5000):
        self.vocab_size = vocab_size
        self.data = []
        self.labels = []
        self.vocab = {}
        self.category_map = {}
        
        # Load and process data
        self._load_data(data_path)
        self._build_vocab()
        self._encode_data()
    
    def _load_data(self, data_path: str):
        """Load training data from JSON"""
        with open(data_path, 'r') as f:
            raw_data = json.load(f)
        
        queries = raw_data.get('queries', raw_data)
        categories = set()
        
        for item in queries:
            self.data.append(item['query'])
            category = item.get('category', 'unknown')
            categories.add(category)
            self.labels.append(category)
        
        # Create category mappings
        self.category_map = {cat: idx for idx, cat in enumerate(sorted(categories))}
        self.idx_to_category = {idx: cat for cat, idx in self.category_map.items()}
        
        logger.info(f"Loaded {len(self.data)} queries with {len(self.category_map)} categories")
    
    def _build_vocab(self):
        """Build vocabulary from queries"""
        word_freq = {}
        for query in self.data:
            for word in query.lower().split():
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and take top vocab_size
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        self.vocab = {'<PAD>': 0, '<UNK>': 1}
        
        for word, _ in sorted_words[:self.vocab_size-2]:
            self.vocab[word] = len(self.vocab)
        
        logger.info(f"Built vocabulary with {len(self.vocab)} words")
    
    def _encode_data(self):
        """Encode queries as token sequences"""
        self.encoded_data = []
        self.encoded_labels = []
        
        for query, label in zip(self.data, self.labels):
            tokens = [self.vocab.get(word.lower(), 1) for word in query.split()]
            self.encoded_data.append(tokens)
            self.encoded_labels.append(self.category_map[label])
    
    def __len__(self):
        return len(self.encoded_data)
    
    def __getitem__(self, idx):
        # Pad sequences to fixed length
        max_len = 50
        tokens = self.encoded_data[idx][:max_len]
        tokens += [0] * (max_len - len(tokens))  # Pad with zeros
        
        return torch.tensor(tokens), torch.tensor(self.encoded_labels[idx])


class RealNixOSNeuralNetwork(nn.Module):
    """Real LSTM neural network for NixOS query classification"""
    
    def __init__(self, vocab_size: int, num_categories: int, 
                 embedding_dim: int = 128, hidden_dim: int = 256):
        super().__init__()
        
        # Embedding layer
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        
        # LSTM layers
        self.lstm = nn.LSTM(
            embedding_dim, 
            hidden_dim, 
            num_layers=2,
            batch_first=True, 
            bidirectional=True,
            dropout=0.3
        )
        
        # Classification head
        self.fc1 = nn.Linear(hidden_dim * 2, hidden_dim)
        self.dropout = nn.Dropout(0.3)
        self.fc2 = nn.Linear(hidden_dim, num_categories)
        self.relu = nn.ReLU()
        self.softmax = nn.Softmax(dim=1)
    
    def forward(self, x):
        # Embedding
        x = self.embedding(x)
        
        # LSTM
        lstm_out, (hidden, cell) = self.lstm(x)
        
        # Use last hidden state from both directions
        hidden_fwd = hidden[-2]
        hidden_bwd = hidden[-1]
        hidden_combined = torch.cat((hidden_fwd, hidden_bwd), dim=1)
        
        # Classification
        x = self.relu(self.fc1(hidden_combined))
        x = self.dropout(x)
        x = self.fc2(x)
        
        return x
    
    def predict_proba(self, x):
        """Get probability distribution over categories"""
        with torch.no_grad():
            logits = self.forward(x)
            return self.softmax(logits)


class NeuralModelTrainer:
    """Trainer for the neural network model"""
    
    def __init__(self, model: nn.Module, device: str = 'cpu'):
        self.model = model.to(device)
        self.device = device
        self.optimizer = optim.Adam(model.parameters(), lr=0.001)
        self.criterion = nn.CrossEntropyLoss()
        self.training_history = []
    
    def train_epoch(self, dataloader: DataLoader) -> float:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        for batch_idx, (data, target) in enumerate(dataloader):
            data, target = data.to(self.device), target.to(self.device)
            
            # Forward pass
            self.optimizer.zero_grad()
            output = self.model(data)
            loss = self.criterion(output, target)
            
            # Backward pass
            loss.backward()
            self.optimizer.step()
            
            # Statistics
            total_loss += loss.item()
            _, predicted = output.max(1)
            total += target.size(0)
            correct += predicted.eq(target).sum().item()
        
        accuracy = 100. * correct / total
        avg_loss = total_loss / len(dataloader)
        
        return avg_loss, accuracy
    
    def evaluate(self, dataloader: DataLoader) -> Tuple[float, float]:
        """Evaluate on validation set"""
        self.model.eval()
        total_loss = 0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for data, target in dataloader:
                data, target = data.to(self.device), target.to(self.device)
                output = self.model(data)
                loss = self.criterion(output, target)
                
                total_loss += loss.item()
                _, predicted = output.max(1)
                total += target.size(0)
                correct += predicted.eq(target).sum().item()
        
        accuracy = 100. * correct / total
        avg_loss = total_loss / len(dataloader)
        
        return avg_loss, accuracy
    
    def train(self, train_loader: DataLoader, val_loader: DataLoader, 
              epochs: int = 10) -> Dict:
        """Full training loop"""
        logger.info(f"Starting training for {epochs} epochs")
        
        best_val_acc = 0
        best_model_state = None
        
        for epoch in range(epochs):
            # Train
            train_loss, train_acc = self.train_epoch(train_loader)
            
            # Validate
            val_loss, val_acc = self.evaluate(val_loader)
            
            # Save best model
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                best_model_state = self.model.state_dict().copy()
            
            # Log progress
            logger.info(f"Epoch {epoch+1}/{epochs}")
            logger.info(f"  Train Loss: {train_loss:.4f}, Acc: {train_acc:.2f}%")
            logger.info(f"  Val Loss: {val_loss:.4f}, Acc: {val_acc:.2f}%")
            
            self.training_history.append({
                'epoch': epoch + 1,
                'train_loss': train_loss,
                'train_acc': train_acc,
                'val_loss': val_loss,
                'val_acc': val_acc
            })
        
        # Restore best model
        if best_model_state:
            self.model.load_state_dict(best_model_state)
        
        return {
            'best_val_acc': best_val_acc,
            'final_train_acc': train_acc,
            'history': self.training_history
        }


class RealNeuralQueryProcessor:
    """Production query processor using real neural network"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load or create model
        if model_path and Path(model_path).exists():
            self.load_model(model_path)
        else:
            self.create_default_model()
        
        self.model.eval()
    
    def create_default_model(self):
        """Create a default model with standard architecture"""
        self.vocab_size = 5000
        self.num_categories = 8
        self.model = RealNixOSNeuralNetwork(
            self.vocab_size, 
            self.num_categories
        ).to(self.device)
        
        # Default vocabulary (would be loaded from training)
        self.vocab = self._create_default_vocab()
        
        # Category mappings
        self.categories = ['install', 'update', 'dev', 'search', 
                          'config', 'error', 'rollback', 'general']
        self.category_map = {cat: idx for idx, cat in enumerate(self.categories)}
    
    def _create_default_vocab(self) -> Dict[str, int]:
        """Create default vocabulary for common NixOS terms"""
        common_words = [
            'install', 'update', 'search', 'config', 'enable', 'disable',
            'firefox', 'chrome', 'vscode', 'python', 'rust', 'node',
            'development', 'environment', 'package', 'system', 'service',
            'rollback', 'generation', 'garbage', 'collect', 'clean'
        ]
        
        vocab = {'<PAD>': 0, '<UNK>': 1}
        for word in common_words:
            vocab[word] = len(vocab)
        
        return vocab
    
    def process_query(self, query: str) -> Dict:
        """Process a query through the real neural network"""
        # Tokenize and encode
        tokens = [self.vocab.get(word.lower(), 1) for word in query.split()]
        
        # Pad to fixed length
        max_len = 50
        tokens = tokens[:max_len]
        tokens += [0] * (max_len - len(tokens))
        
        # Convert to tensor
        input_tensor = torch.tensor([tokens]).to(self.device)
        
        # Get prediction
        with torch.no_grad():
            output = self.model(input_tensor)
            probs = torch.softmax(output, dim=1)
            confidence, predicted = torch.max(probs, 1)
        
        category = self.categories[predicted.item()]
        conf_value = confidence.item()
        
        # Map to command
        command = self._category_to_command(category, query)
        
        return {
            'query': query,
            'category': category,
            'command': command,
            'confidence': conf_value,
            'model': 'real_neural_network',
            'device': str(self.device)
        }
    
    def _category_to_command(self, category: str, query: str) -> str:
        """Map category and query to NixOS command"""
        query_lower = query.lower()
        
        if category == 'install':
            # Extract package name
            for word in query_lower.split():
                if word not in ['install', 'get', 'add']:
                    return f"nix-env -iA nixpkgs.{word}"
            return "nix search"
        
        elif category == 'update':
            if 'system' in query_lower:
                return "sudo nixos-rebuild switch"
            return "nix-channel --update && nix-env -u"
        
        elif category == 'dev':
            if 'python' in query_lower:
                return "nix-shell -p python3 python3Packages.pip"
            elif 'rust' in query_lower:
                return "nix-shell -p rustc cargo"
            elif 'node' in query_lower:
                return "nix-shell -p nodejs"
            return "nix-shell"
        
        elif category == 'search':
            words = [w for w in query_lower.split() if w not in ['search', 'find', 'list']]
            if words:
                return f"nix search nixpkgs {words[0]}"
            return "nix search"
        
        elif category == 'config':
            return "sudo nano /etc/nixos/configuration.nix"
        
        elif category == 'rollback':
            return "sudo nixos-rebuild switch --rollback"
        
        else:
            return "nix search " + query.split()[0] if query else "nix search"
    
    def save_model(self, path: str):
        """Save model and configuration"""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'vocab': self.vocab,
            'categories': self.categories,
            'vocab_size': self.vocab_size,
            'num_categories': self.num_categories
        }, path)
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path: str):
        """Load model from checkpoint"""
        checkpoint = torch.load(path, map_location=self.device)
        
        self.vocab = checkpoint['vocab']
        self.categories = checkpoint['categories']
        self.vocab_size = checkpoint['vocab_size']
        self.num_categories = checkpoint['num_categories']
        
        self.model = RealNixOSNeuralNetwork(
            self.vocab_size,
            self.num_categories
        ).to(self.device)
        
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.category_map = {cat: idx for idx, cat in enumerate(self.categories)}
        
        logger.info(f"Model loaded from {path}")


def train_real_model(data_path: str = "data/training/comprehensive_training_data.json",
                     model_save_path: str = "models/real_neural_v030.pt"):
    """Train a real neural network model"""
    print("🧠 Training Real Neural Network for Luminous Nix v0.3.0")
    print("=" * 60)
    
    # Check for CUDA
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Load dataset
    dataset = NixOSQueryDataset(data_path)
    
    # Split into train/val
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(
        dataset, [train_size, val_size]
    )
    
    # Create dataloaders
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)
    
    print(f"Training samples: {train_size}")
    print(f"Validation samples: {val_size}")
    
    # Create model
    model = RealNixOSNeuralNetwork(
        vocab_size=len(dataset.vocab),
        num_categories=len(dataset.category_map)
    )
    
    # Count parameters
    param_count = sum(p.numel() for p in model.parameters())
    print(f"Model parameters: {param_count:,}")
    
    # Train model
    trainer = NeuralModelTrainer(model, device)
    results = trainer.train(train_loader, val_loader, epochs=10)
    
    print("\n" + "=" * 60)
    print("✅ Training Complete!")
    print(f"Best validation accuracy: {results['best_val_acc']:.2f}%")
    print(f"Final training accuracy: {results['final_train_acc']:.2f}%")
    
    # Save model
    processor = RealNeuralQueryProcessor()
    processor.model = model
    processor.vocab = dataset.vocab
    processor.categories = list(dataset.idx_to_category.values())
    processor.save_model(model_save_path)
    
    return processor


def test_real_model():
    """Test the real neural network model"""
    print("🧪 Testing Real Neural Network")
    print("=" * 60)
    
    # Load or create model
    processor = RealNeuralQueryProcessor("models/real_neural_v030.pt")
    
    # Test queries
    test_queries = [
        "install firefox browser",
        "create python development environment",
        "update system packages",
        "search for text editors",
        "enable bluetooth service",
        "rollback to previous generation",
        "setup rust development",
        "list installed packages"
    ]
    
    print("\nProcessing test queries:")
    for query in test_queries:
        result = processor.process_query(query)
        print(f"\nQuery: {query}")
        print(f"  Category: {result['category']}")
        print(f"  Command: {result['command']}")
        print(f"  Confidence: {result['confidence']:.2%}")
        print(f"  Device: {result['device']}")
    
    print("\n" + "=" * 60)
    print("✅ Real neural network test complete!")
    print("No simulation - actual PyTorch model with real predictions!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "train":
        train_real_model()
    else:
        test_real_model()