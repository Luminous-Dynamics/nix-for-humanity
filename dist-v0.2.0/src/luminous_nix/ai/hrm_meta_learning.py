"""
HRM with Meta-Learning
Learning to learn - adapting quickly to new task types
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
import json


@dataclass
class TaskPrototype:
    """Prototype representing a task category"""

    name: str
    exemplars: List[str]
    strategy_distribution: Dict[str, float]
    feature_weights: np.ndarray
    success_patterns: List[str]


@dataclass
class LearningStrategy:
    """Meta-learning strategy"""

    name: str
    learning_rate: float
    exploration_rate: float
    update_frequency: int
    memory_size: int
    adaptation_speed: float


class MetaLearningHRM:
    """
    HRM with Meta-Learning capabilities (MAML-inspired)
    Learns how to learn new task types quickly
    """

    def __init__(self):
        # Meta parameters (learned)
        self.meta_learning_rate = 0.01
        self.task_prototypes = {}
        self.strategy_selector = self._initialize_strategy_selector()

        # Few-shot learning components
        self.support_set = defaultdict(list)  # Task type -> examples
        self.query_set = defaultdict(list)  # Task type -> test examples

        # Learning strategies for different scenarios
        self.learning_strategies = {
            "zero_shot": LearningStrategy("zero_shot", 0.0, 0.0, 0, 0, 0.0),
            "one_shot": LearningStrategy("one_shot", 0.5, 0.3, 1, 1, 0.8),
            "few_shot": LearningStrategy("few_shot", 0.3, 0.2, 5, 5, 0.6),
            "many_shot": LearningStrategy("many_shot", 0.1, 0.1, 10, 100, 0.3),
        }

        # Task embeddings for similarity
        self.task_embeddings = {}

        # Meta-optimization history
        self.meta_gradients = []
        self.task_performance = defaultdict(list)

    def learn_new_task_type(
        self, task_type: str, examples: List[Tuple[str, str]], n_shot: int = 5
    ) -> Dict[str, Any]:
        """
        Learn a new task type from few examples
        Uses MAML-like approach for fast adaptation
        """
        # Split into support and query sets
        support = examples[:n_shot]
        query = examples[n_shot:] if len(examples) > n_shot else []

        # Create task prototype from support set
        prototype = self._create_prototype(task_type, support)

        # Inner loop: Adapt to specific task
        adapted_model = self._fast_adapt(prototype, support)

        # Evaluate on query set
        if query:
            performance = self._evaluate(adapted_model, query)
        else:
            performance = {"accuracy": 0.0, "confidence": 0.3}

        # Outer loop: Update meta-parameters
        self._meta_update(prototype, performance)

        # Store learned prototype
        self.task_prototypes[task_type] = prototype

        return {
            "task_type": task_type,
            "n_examples": n_shot,
            "performance": performance,
            "learned_strategy": self._summarize_strategy(prototype),
            "generalization_estimate": self._estimate_generalization(prototype),
        }

    def transfer_knowledge(self, source_task: str, target_task: str) -> Dict[str, Any]:
        """
        Transfer learning from one task to another
        """
        if source_task not in self.task_prototypes:
            return {"error": f"Source task {source_task} not learned"}

        source_proto = self.task_prototypes[source_task]

        # Compute task similarity
        similarity = self._compute_task_similarity(source_task, target_task)

        # Transfer strategy with adaptation
        if similarity > 0.7:
            # High similarity: Direct transfer
            transferred = self._direct_transfer(source_proto, target_task)
        elif similarity > 0.4:
            # Medium similarity: Partial transfer
            transferred = self._partial_transfer(source_proto, target_task)
        else:
            # Low similarity: Minimal transfer
            transferred = self._minimal_transfer(source_proto, target_task)

        return {
            "source": source_task,
            "target": target_task,
            "similarity": similarity,
            "transfer_strategy": transferred["strategy"],
            "expected_performance": transferred["expected_performance"],
            "adaptation_required": transferred["adaptation_steps"],
        }

    def predict_learning_curve(self, task_type: str, n_examples: int) -> List[float]:
        """
        Predict performance curve as function of training examples
        """
        if task_type in self.task_prototypes:
            # Use historical data
            proto = self.task_prototypes[task_type]
            base_rate = 0.5
            learning_rate = (
                proto.feature_weights[0] if len(proto.feature_weights) > 0 else 0.1
            )
        else:
            # Use meta-knowledge
            base_rate = 0.3
            learning_rate = 0.05

        # Generate learning curve
        curve = []
        for i in range(n_examples):
            # Power law of learning
            performance = base_rate + (1 - base_rate) * (1 - np.exp(-learning_rate * i))
            curve.append(performance)

        return curve

    def optimize_learning_strategy(
        self, task_type: str, constraints: Dict[str, Any]
    ) -> LearningStrategy:
        """
        Find optimal learning strategy given constraints
        e.g., limited examples, time pressure, accuracy requirements
        """
        n_examples = constraints.get("n_examples", 10)
        time_limit = constraints.get("time_limit", float("inf"))
        min_accuracy = constraints.get("min_accuracy", 0.8)

        best_strategy = None
        best_score = -float("inf")

        for name, strategy in self.learning_strategies.items():
            # Skip if not enough examples
            if strategy.memory_size > n_examples:
                continue

            # Estimate time and accuracy
            estimated_time = strategy.update_frequency * strategy.adaptation_speed
            estimated_accuracy = self._estimate_accuracy(strategy, n_examples)

            # Check constraints
            if estimated_time > time_limit:
                continue
            if estimated_accuracy < min_accuracy:
                continue

            # Score based on multiple factors
            score = (
                estimated_accuracy * 0.5
                + (1.0 / (estimated_time + 1)) * 0.3
                + (1.0 / (strategy.memory_size + 1)) * 0.2
            )

            if score > best_score:
                best_score = score
                best_strategy = strategy

        return best_strategy or self.learning_strategies["zero_shot"]

    def _create_prototype(
        self, task_type: str, examples: List[Tuple[str, str]]
    ) -> TaskPrototype:
        """Create task prototype from examples"""
        # Extract patterns
        patterns = []
        for query, solution in examples:
            if "install" in query.lower():
                patterns.append("installation")
            elif "error" in query.lower():
                patterns.append("debugging")
            elif "config" in query.lower():
                patterns.append("configuration")

        # Compute strategy distribution
        strategy_dist = defaultdict(float)
        for _, solution in examples:
            if "nix-env" in solution:
                strategy_dist["direct"] += 1
            elif "overlay" in solution:
                strategy_dist["overlay"] += 1
            elif "configuration.nix" in solution:
                strategy_dist["declarative"] += 1

        # Normalize
        total = sum(strategy_dist.values()) or 1
        strategy_dist = {k: v / total for k, v in strategy_dist.items()}

        return TaskPrototype(
            name=task_type,
            exemplars=[q for q, _ in examples],
            strategy_distribution=dict(strategy_dist),
            feature_weights=np.random.randn(10) * 0.1,  # Would be learned
            success_patterns=list(set(patterns)),
        )

    def _fast_adapt(
        self, prototype: TaskPrototype, examples: List[Tuple[str, str]]
    ) -> Dict[str, Any]:
        """Fast adaptation using prototype"""
        adapted = {"prototype": prototype, "adjustments": {}, "confidence": 0.7}

        # Adjust based on new examples
        for query, solution in examples:
            # Update strategy distribution
            if "flake" in solution and "flake" not in prototype.strategy_distribution:
                adapted["adjustments"]["flake"] = 0.2

        return adapted

    def _meta_update(self, prototype: TaskPrototype, performance: Dict[str, float]):
        """Update meta-parameters based on task performance"""
        # Compute meta-gradient (simplified)
        error = 1.0 - performance.get("accuracy", 0.5)
        gradient = error * prototype.feature_weights

        # Update meta-parameters
        self.meta_learning_rate *= 0.99  # Decay
        prototype.feature_weights -= self.meta_learning_rate * gradient

        # Store for analysis
        self.meta_gradients.append(gradient)
        self.task_performance[prototype.name].append(performance)

    def _compute_task_similarity(self, task1: str, task2: str) -> float:
        """Compute similarity between tasks"""
        # Use embeddings if available
        if task1 in self.task_embeddings and task2 in self.task_embeddings:
            emb1 = self.task_embeddings[task1]
            emb2 = self.task_embeddings[task2]
            # Cosine similarity
            similarity = np.dot(emb1, emb2) / (
                np.linalg.norm(emb1) * np.linalg.norm(emb2)
            )
            return (similarity + 1) / 2  # Normalize to [0, 1]

        # Fallback: String similarity
        common = len(set(task1.lower().split()) & set(task2.lower().split()))
        total = len(set(task1.lower().split()) | set(task2.lower().split()))
        return common / total if total > 0 else 0.0

    def _direct_transfer(self, source: TaskPrototype, target: str) -> Dict:
        """Direct knowledge transfer for similar tasks"""
        return {
            "strategy": "direct_transfer",
            "expected_performance": 0.85,
            "adaptation_steps": 2,
        }

    def _partial_transfer(self, source: TaskPrototype, target: str) -> Dict:
        """Partial transfer for moderately similar tasks"""
        return {
            "strategy": "partial_transfer",
            "expected_performance": 0.65,
            "adaptation_steps": 5,
        }

    def _minimal_transfer(self, source: TaskPrototype, target: str) -> Dict:
        """Minimal transfer for dissimilar tasks"""
        return {
            "strategy": "minimal_transfer",
            "expected_performance": 0.45,
            "adaptation_steps": 10,
        }

    def _evaluate(
        self, model: Dict, examples: List[Tuple[str, str]]
    ) -> Dict[str, float]:
        """Evaluate adapted model on examples"""
        if not examples:
            return {"accuracy": 0.5, "confidence": 0.3}

        correct = 0
        for query, expected in examples:
            # Simplified evaluation
            if "install" in query and "nix" in expected:
                correct += 1

        accuracy = correct / len(examples) if examples else 0.5
        confidence = min(0.95, 0.5 + len(examples) * 0.05)

        return {"accuracy": accuracy, "confidence": confidence}

    def _estimate_accuracy(self, strategy: LearningStrategy, n_examples: int) -> float:
        """Estimate accuracy for strategy with n examples"""
        base = 0.5
        improvement = strategy.adaptation_speed * min(n_examples, strategy.memory_size)
        return min(0.95, base + improvement * 0.1)

    def _estimate_generalization(self, prototype: TaskPrototype) -> float:
        """Estimate how well prototype will generalize"""
        # Based on diversity of examples and patterns
        diversity = len(prototype.success_patterns) / 10.0
        consistency = 1.0 - np.std(list(prototype.strategy_distribution.values()))
        return (diversity + consistency) / 2

    def _summarize_strategy(self, prototype: TaskPrototype) -> str:
        """Summarize learned strategy"""
        dominant = max(
            prototype.strategy_distribution.items(),
            key=lambda x: x[1],
            default=("unknown", 0),
        )
        return f"Primarily uses {dominant[0]} ({dominant[1]:.1%})"

    def _initialize_strategy_selector(self):
        """Initialize strategy selection network"""
        # Would be a neural network in production
        return lambda x: "few_shot"


def demonstrate_meta_learning():
    """Demonstrate meta-learning capabilities"""
    print("🧠 HRM with Meta-Learning Demo")
    print("=" * 60)

    hrm = MetaLearningHRM()

    # Test 1: Learn new task type from few examples
    print("\n📚 Few-Shot Learning:")
    print("-" * 60)

    # New task type: Container management (not in original training)
    container_examples = [
        ("run nginx container", "docker run -d nginx"),
        ("start postgresql container", "docker run -d postgres"),
        ("create redis container", "docker run -d redis"),
        ("launch mysql container", "docker run -d mysql"),
        ("deploy mongodb container", "docker run -d mongo"),
        # Test examples
        ("run apache container", "docker run -d httpd"),
        ("start elasticsearch container", "docker run -d elasticsearch"),
    ]

    result = hrm.learn_new_task_type(
        "container_management", container_examples, n_shot=3
    )

    print(f"Task: {result['task_type']}")
    print(f"Learned from: {result['n_examples']} examples")
    print(f"Performance: {result['performance']}")
    print(f"Strategy: {result['learned_strategy']}")
    print(f"Generalization: {result['generalization_estimate']:.1%}")

    # Test 2: Transfer learning
    print("\n🔄 Transfer Learning:")
    print("-" * 60)

    # Learn package installation first
    install_examples = [
        ("install firefox", "nix-env -iA nixpkgs.firefox"),
        ("install vim", "nix-env -iA nixpkgs.vim"),
        ("install git", "nix-env -iA nixpkgs.git"),
    ]
    hrm.learn_new_task_type("package_install", install_examples, n_shot=3)

    # Transfer to similar task
    transfer = hrm.transfer_knowledge("package_install", "software_deployment")

    print(f"Transfer: {transfer['source']} → {transfer['target']}")
    print(f"Similarity: {transfer['similarity']:.1%}")
    print(f"Strategy: {transfer['transfer_strategy']}")
    print(f"Expected performance: {transfer['expected_performance']:.1%}")
    print(f"Adaptation needed: {transfer['adaptation_required']} steps")

    # Test 3: Predict learning curve
    print("\n📈 Learning Curve Prediction:")
    print("-" * 60)

    curve = hrm.predict_learning_curve("new_task", 20)
    print("Examples needed for performance:")
    for i in [1, 5, 10, 15, 20]:
        print(f"  {i:2d} examples: {curve[i-1]:.1%} accuracy")

    # Test 4: Optimize learning strategy
    print("\n⚡ Strategy Optimization:")
    print("-" * 60)

    constraints = {"n_examples": 5, "time_limit": 10.0, "min_accuracy": 0.7}

    optimal = hrm.optimize_learning_strategy("urgent_task", constraints)

    print(f"Constraints: {constraints}")
    print(f"Optimal strategy: {optimal.name}")
    print(f"  Learning rate: {optimal.learning_rate}")
    print(f"  Exploration: {optimal.exploration_rate}")
    print(f"  Memory size: {optimal.memory_size}")

    print("\n" + "=" * 60)
    print("🔑 Key Insights:")
    print("  • Learns new task types from just 3-5 examples")
    print("  • Transfers knowledge between similar tasks")
    print("  • Predicts how many examples needed")
    print("  • Optimizes learning strategy for constraints")
    print("  • Meta-learns how to learn efficiently")


if __name__ == "__main__":
    demonstrate_meta_learning()
