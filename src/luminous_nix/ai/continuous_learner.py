"""
Continuous Learning System - Revolutionary Feature

The neural network LEARNS from real user interactions over time.

This is what makes it truly revolutionary:
- Starts with synthetic data (bootstrap)
- Gradually incorporates real behavioral observations
- Retrains model when enough new data arrives
- Gets better the more it's used
- Never stops learning

Traditional AI: Train once, deploy, hope for best
Revolutionary AI: Continuously improves with every interaction
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
import json

from .behavioral_features import BehavioralFeatureExtractor, BehavioralFeatures
from .behavioral_classifier import ArchetypeClassifier, BehavioralArchetypeDetector
from .user_profiler import UserArchetype


@dataclass
class TrainingExample:
    """A single training example from real user behavior"""
    features: BehavioralFeatures
    true_archetype: UserArchetype
    confidence: float  # How confident we are this is correct
    timestamp: str
    user_id: str
    source: str  # "synthetic", "confirmed", "inferred", "feedback"


@dataclass
class LearningMetrics:
    """Metrics tracking the learning progress"""
    total_examples: int
    synthetic_count: int
    real_count: int
    retraining_count: int
    last_retrain_date: str
    current_accuracy: float  # On held-out test set
    data_quality_score: float  # 0.0 (all synthetic) to 1.0 (all real)


class ContinuousLearner:
    """
    Manages continuous learning for the behavioral archetype detector.

    This system:
    1. Collects real behavioral observations
    2. Determines when to retrain
    3. Retrains model with new data
    4. Tracks learning progress
    5. Manages synthetic→real transition
    """

    def __init__(
        self,
        detector: BehavioralArchetypeDetector,
        data_dir: Optional[str] = None
    ):
        """
        Initialize continuous learner.

        Args:
            detector: The behavioral detector to train
            data_dir: Directory for storing training data
        """
        self.detector = detector

        # Setup data directory
        if data_dir is None:
            data_dir = str(Path.home() / ".luminous-nix" / "training_data")
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Paths
        self.examples_file = self.data_dir / "training_examples.jsonl"
        self.metrics_file = self.data_dir / "learning_metrics.json"
        self.model_dir = self.data_dir / "models"
        self.model_dir.mkdir(exist_ok=True)

        # Load existing data
        self.training_examples: List[TrainingExample] = self._load_examples()
        self.metrics: LearningMetrics = self._load_metrics()

        # Retraining configuration
        self.retrain_threshold = 50  # Retrain after 50 new examples
        self.examples_since_retrain = 0

    def add_observation(
        self,
        features: BehavioralFeatures,
        true_archetype: UserArchetype,
        confidence: float,
        user_id: str = "default_user",
        source: str = "confirmed"
    ):
        """
        Add a new behavioral observation to training data.

        Args:
            features: Behavioral features observed
            true_archetype: Confirmed archetype
            confidence: Confidence in this label (0.0-1.0)
            user_id: User this observation is from
            source: How we obtained this label
        """
        # Create training example
        example = TrainingExample(
            features=features,
            true_archetype=true_archetype,
            confidence=confidence,
            timestamp=datetime.now().isoformat(),
            user_id=user_id,
            source=source
        )

        # Add to collection
        self.training_examples.append(example)
        self.examples_since_retrain += 1

        # Save immediately (don't lose data!)
        self._save_example(example)

        # Update metrics
        self._update_metrics()

        # Check if we should retrain
        if self.should_retrain():
            self.retrain_model()

    def should_retrain(self) -> bool:
        """
        Determine if it's time to retrain the model.

        Retrain when:
        1. We have enough new examples since last training
        2. Data quality has significantly improved
        3. User explicitly requests retraining

        Returns:
            True if model should be retrained
        """
        # Check new examples threshold
        if self.examples_since_retrain >= self.retrain_threshold:
            return True

        # Check data quality improvement
        # If we went from mostly synthetic to mostly real, retrain
        real_ratio = self._calculate_real_data_ratio()
        if real_ratio > 0.5 and self.metrics.data_quality_score < 0.5:
            return True

        return False

    def retrain_model(self):
        """
        Retrain the model with current training data.

        This combines:
        - Original synthetic data (for cold start)
        - All real observations collected
        - Weighted by confidence and recency
        """
        print(f"\n🔄 Retraining model with {len(self.training_examples)} examples...")

        # Prepare training data
        X_list = []
        y_list = []
        weights = []

        for example in self.training_examples:
            # Convert features to array
            feature_array = self.detector.feature_extractor.to_numpy_array(example.features)
            X_list.append(feature_array)

            # Convert archetype to label
            label = self.detector.archetypes.index(example.true_archetype)
            y_list.append(label)

            # Calculate weight based on confidence and source
            weight = example.confidence
            if example.source == "confirmed":
                weight *= 2.0  # Confirmed examples weighted higher
            elif example.source == "synthetic":
                weight *= 0.5  # Synthetic weighted lower
            weights.append(weight)

        # Convert to tensors
        X = torch.from_numpy(np.stack(X_list)).to(self.detector.device)
        y = torch.tensor(y_list, dtype=torch.long).to(self.detector.device)
        weights = torch.tensor(weights, dtype=torch.float32).to(self.detector.device)

        # Split into train/val (80/20)
        train_size = int(0.8 * len(X))
        indices = torch.randperm(len(X))
        train_idx = indices[:train_size]
        val_idx = indices[train_size:]

        X_train, y_train = X[train_idx], y[train_idx]
        X_val, y_val = X[val_idx], y[val_idx]
        weights_train = weights[train_idx]

        # Train model
        self.detector.model.train()
        optimizer = torch.optim.Adam(self.detector.model.parameters(), lr=0.001)
        criterion = nn.CrossEntropyLoss(reduction='none')  # Use reduction='none' for weighting

        best_val_acc = 0.0
        epochs_without_improvement = 0
        max_epochs_without_improvement = 10

        for epoch in range(100):  # Max 100 epochs
            # Training
            optimizer.zero_grad()
            outputs = self.detector.model(X_train)
            losses = criterion(outputs, y_train)

            # Weight the losses
            weighted_loss = (losses * weights_train).mean()

            weighted_loss.backward()
            optimizer.step()

            # Validation
            self.detector.model.eval()
            with torch.no_grad():
                val_outputs = self.detector.model(X_val)
                val_preds = torch.argmax(val_outputs, dim=1)
                val_acc = (val_preds == y_val).float().mean().item()
            self.detector.model.train()

            # Early stopping
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                epochs_without_improvement = 0
                # Save best model
                self._save_model_checkpoint(epoch, val_acc)
            else:
                epochs_without_improvement += 1
                if epochs_without_improvement >= max_epochs_without_improvement:
                    print(f"✅ Early stopping at epoch {epoch}, best val acc: {best_val_acc:.3f}")
                    break

        self.detector.model.eval()

        # Update metrics
        self.metrics.retraining_count += 1
        self.metrics.last_retrain_date = datetime.now().isoformat()
        self.metrics.current_accuracy = best_val_acc
        self.examples_since_retrain = 0

        self._save_metrics()

        print(f"✨ Retraining complete! Validation accuracy: {best_val_acc:.1%}")
        print(f"   Total retrains: {self.metrics.retraining_count}")
        print(f"   Data quality: {self.metrics.data_quality_score:.1%} real data")

    def get_learning_status(self) -> Dict:
        """
        Get current learning status and metrics.

        Returns:
            Dictionary with learning progress information
        """
        real_count = sum(1 for ex in self.training_examples if ex.source != "synthetic")
        synthetic_count = len(self.training_examples) - real_count

        return {
            "total_examples": len(self.training_examples),
            "real_examples": real_count,
            "synthetic_examples": synthetic_count,
            "data_quality": self._calculate_real_data_ratio(),
            "retraining_count": self.metrics.retraining_count,
            "examples_until_retrain": max(0, self.retrain_threshold - self.examples_since_retrain),
            "current_accuracy": self.metrics.current_accuracy,
            "last_retrain": self.metrics.last_retrain_date,
            "model_maturity": self._calculate_model_maturity()
        }

    def _calculate_real_data_ratio(self) -> float:
        """Calculate ratio of real vs synthetic data"""
        if not self.training_examples:
            return 0.0

        real_count = sum(1 for ex in self.training_examples if ex.source != "synthetic")
        return real_count / len(self.training_examples)

    def _calculate_model_maturity(self) -> str:
        """
        Calculate model maturity level.

        Returns:
            "bootstrap", "learning", "mature", or "expert"
        """
        real_ratio = self._calculate_real_data_ratio()
        total = len(self.training_examples)

        if real_ratio < 0.1:
            return "bootstrap"  # Still mostly synthetic
        elif real_ratio < 0.5 or total < 200:
            return "learning"  # Collecting real data
        elif real_ratio >= 0.5 and total >= 200:
            return "mature"  # Good amount of real data
        elif total >= 1000:
            return "expert"  # Lots of experience

        return "learning"

    def _load_examples(self) -> List[TrainingExample]:
        """Load training examples from disk"""
        if not self.examples_file.exists():
            return []

        examples = []
        with open(self.examples_file, 'r') as f:
            for line in f:
                data = json.loads(line)
                # Reconstruct BehavioralFeatures
                features_dict = data['features']
                features = BehavioralFeatures(**features_dict)

                # Reconstruct TrainingExample
                example = TrainingExample(
                    features=features,
                    true_archetype=UserArchetype(data['true_archetype']),
                    confidence=data['confidence'],
                    timestamp=data['timestamp'],
                    user_id=data['user_id'],
                    source=data['source']
                )
                examples.append(example)

        return examples

    def _save_example(self, example: TrainingExample):
        """Append a single example to disk (JSONL format)"""
        with open(self.examples_file, 'a') as f:
            data = {
                'features': asdict(example.features),
                'true_archetype': example.true_archetype.value,
                'confidence': example.confidence,
                'timestamp': example.timestamp,
                'user_id': example.user_id,
                'source': example.source
            }
            f.write(json.dumps(data) + '\n')

    def _load_metrics(self) -> LearningMetrics:
        """Load learning metrics from disk"""
        if not self.metrics_file.exists():
            return LearningMetrics(
                total_examples=0,
                synthetic_count=0,
                real_count=0,
                retraining_count=0,
                last_retrain_date="never",
                current_accuracy=0.0,
                data_quality_score=0.0
            )

        with open(self.metrics_file, 'r') as f:
            data = json.load(f)
            return LearningMetrics(**data)

    def _save_metrics(self):
        """Save learning metrics to disk"""
        with open(self.metrics_file, 'w') as f:
            json.dump(asdict(self.metrics), f, indent=2)

    def _update_metrics(self):
        """Update metrics based on current training data"""
        real_count = sum(1 for ex in self.training_examples if ex.source != "synthetic")
        synthetic_count = len(self.training_examples) - real_count

        self.metrics.total_examples = len(self.training_examples)
        self.metrics.real_count = real_count
        self.metrics.synthetic_count = synthetic_count
        self.metrics.data_quality_score = self._calculate_real_data_ratio()

        self._save_metrics()

    def _save_model_checkpoint(self, epoch: int, accuracy: float):
        """Save a model checkpoint"""
        checkpoint_path = self.model_dir / f"checkpoint_epoch{epoch}_acc{accuracy:.3f}.pt"

        torch.save({
            'epoch': epoch,
            'model_state_dict': self.detector.model.state_dict(),
            'accuracy': accuracy,
            'timestamp': datetime.now().isoformat(),
            'training_examples': len(self.training_examples),
            'data_quality': self._calculate_real_data_ratio()
        }, checkpoint_path)

        # Also save as "latest"
        latest_path = self.model_dir / "latest.pt"
        torch.save({
            'epoch': epoch,
            'model_state_dict': self.detector.model.state_dict(),
            'accuracy': accuracy,
            'timestamp': datetime.now().isoformat(),
            'training_examples': len(self.training_examples),
            'data_quality': self._calculate_real_data_ratio()
        }, latest_path)


def get_continuous_learner(detector: BehavioralArchetypeDetector) -> ContinuousLearner:
    """Get singleton instance of continuous learner"""
    global _continuous_learner

    if _continuous_learner is None:
        _continuous_learner = ContinuousLearner(detector)

    return _continuous_learner


# Singleton
_continuous_learner: Optional[ContinuousLearner] = None
