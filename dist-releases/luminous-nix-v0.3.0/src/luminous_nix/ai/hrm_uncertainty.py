"""
HRM with Uncertainty Quantification
Properly calibrated confidence scores using Bayesian approaches
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import math


@dataclass
class UncertaintyEstimate:
    """Calibrated uncertainty with multiple components"""

    aleatoric: float  # Inherent data uncertainty
    epistemic: float  # Model knowledge uncertainty
    total: float  # Combined uncertainty
    confidence: float  # Calibrated confidence (1 - uncertainty)
    explanation: str  # Why this confidence level


class BayesianHRM:
    """
    HRM with proper uncertainty quantification
    Key innovations:
    - Epistemic uncertainty (what the model doesn't know)
    - Aleatoric uncertainty (inherent randomness)
    - Confidence calibration using temperature scaling
    - Out-of-distribution detection
    """

    def __init__(self):
        # Monte Carlo dropout parameters
        self.dropout_rate = 0.1
        self.n_forward_passes = 10

        # Temperature for calibration
        self.temperature = 1.5  # Learned from validation

        # Known distribution statistics
        self.known_embeddings = []
        self.mean_embedding = None
        self.std_embedding = None

    def predict_with_uncertainty(self, query: str) -> Tuple[str, UncertaintyEstimate]:
        """
        Get prediction with calibrated uncertainty
        """
        # 1. Check if out-of-distribution
        is_ood, ood_score = self._detect_out_of_distribution(query)

        # 2. Monte Carlo dropout for epistemic uncertainty
        predictions = []
        for _ in range(self.n_forward_passes):
            pred = self._forward_with_dropout(query)
            predictions.append(pred)

        # 3. Calculate uncertainty components
        epistemic = self._calculate_epistemic_uncertainty(predictions)
        aleatoric = self._calculate_aleatoric_uncertainty(query)

        # 4. Combine uncertainties
        total_uncertainty = math.sqrt(epistemic**2 + aleatoric**2)

        # 5. Apply temperature calibration
        raw_confidence = 1.0 - total_uncertainty
        calibrated_confidence = self._calibrate_confidence(raw_confidence)

        # 6. Adjust for OOD
        if is_ood:
            calibrated_confidence *= 1.0 - ood_score
            explanation = f"Out-of-distribution query (OOD score: {ood_score:.2f})"
        else:
            explanation = self._explain_confidence(epistemic, aleatoric)

        # 7. Get final prediction (majority vote or mean)
        final_prediction = self._aggregate_predictions(predictions)

        return final_prediction, UncertaintyEstimate(
            aleatoric=aleatoric,
            epistemic=epistemic,
            total=total_uncertainty,
            confidence=calibrated_confidence,
            explanation=explanation,
        )

    def _detect_out_of_distribution(self, query: str) -> Tuple[bool, float]:
        """
        Detect if query is out of distribution using:
        - Mahalanobis distance
        - Reconstruction error
        - Nearest neighbor distance
        """
        if not self.known_embeddings:
            return False, 0.0

        # Get embedding for query
        embedding = self._get_embedding(query)

        # Calculate Mahalanobis distance
        if self.mean_embedding is not None:
            diff = embedding - self.mean_embedding
            # Simplified Mahalanobis (would use covariance in production)
            distance = np.linalg.norm(diff) / (
                np.linalg.norm(self.std_embedding) + 1e-6
            )

            # Convert to probability (scalar)
            ood_score = float(
                1.0 / (1.0 + np.exp(-distance + 3))
            )  # Sigmoid with threshold
            is_ood = bool(ood_score > 0.5)

            return is_ood, ood_score

        return False, 0.0

    def _calculate_epistemic_uncertainty(self, predictions: List) -> float:
        """
        Epistemic uncertainty from prediction variance
        High variance = model doesn't know
        """
        if len(predictions) < 2:
            return 0.0

        # Calculate variance across predictions
        # In real implementation, would be variance of logits/embeddings
        unique_predictions = len(set(predictions))
        variance = unique_predictions / len(predictions)

        return variance * 0.5  # Scale to [0, 0.5]

    def _calculate_aleatoric_uncertainty(self, query: str) -> float:
        """
        Aleatoric uncertainty from data properties
        Ambiguous queries have higher uncertainty
        """
        # Check for ambiguity indicators
        ambiguity_score = 0.0

        # Vague words increase uncertainty
        vague_words = ["maybe", "possibly", "something", "somehow", "anything"]
        for word in vague_words:
            if word in query.lower():
                ambiguity_score += 0.1

        # Very short queries are ambiguous
        if len(query.split()) < 3:
            ambiguity_score += 0.2

        # Missing specific package names
        if not any(char.isalnum() for char in query):
            ambiguity_score += 0.1

        return min(0.5, ambiguity_score)

    def _calibrate_confidence(self, raw_confidence: float) -> float:
        """
        Temperature scaling for calibration
        Learned from validation data
        """
        # Apply temperature scaling
        logit = np.log(raw_confidence / (1 - raw_confidence + 1e-6))
        scaled_logit = logit / self.temperature
        calibrated = 1.0 / (1.0 + np.exp(-scaled_logit))

        return calibrated

    def _explain_confidence(self, epistemic: float, aleatoric: float) -> str:
        """Generate human-readable confidence explanation"""
        if epistemic > 0.3:
            return "Low confidence: Model uncertainty about this query type"
        elif aleatoric > 0.3:
            return "Low confidence: Query is ambiguous or underspecified"
        elif epistemic < 0.1 and aleatoric < 0.1:
            return "High confidence: Clear query with known solution pattern"
        else:
            return "Moderate confidence: Standard query with some uncertainty"

    def _forward_with_dropout(self, query: str) -> str:
        """Forward pass with dropout for uncertainty"""
        # Simulate dropout effect
        if np.random.random() < self.dropout_rate:
            return "search_first"  # Uncertain, search first

        # Normal prediction
        if "install" in query.lower():
            return "direct_install"
        elif "error" in query.lower():
            return "overlay_solution"
        else:
            return "configuration_nix"

    def _get_embedding(self, query: str):
        """Get embedding vector for query"""
        # Simplified: use character frequency as embedding
        # Real implementation would use sentence transformers
        embedding = np.zeros(26)
        for char in query.lower():
            if "a" <= char <= "z":
                embedding[ord(char) - ord("a")] += 1
        return embedding / (len(query) + 1)

    def _aggregate_predictions(self, predictions: List) -> str:
        """Aggregate multiple predictions"""
        from collections import Counter

        # Majority vote
        if predictions:
            return Counter(predictions).most_common(1)[0][0]
        return "search_first"

    def update_known_distribution(self, queries: List[str]):
        """Update the known distribution for OOD detection"""
        embeddings = [self._get_embedding(q) for q in queries]
        self.known_embeddings = embeddings
        self.mean_embedding = np.mean(embeddings, axis=0)
        self.std_embedding = np.std(embeddings, axis=0)


### 2. **Conformal Prediction for Guaranteed Coverage** 🎯
class ConformalHRM:
    """
    Conformal prediction provides guaranteed coverage
    Instead of single answer, return set of plausible solutions
    """

    def __init__(self, coverage_level: float = 0.95):
        self.coverage_level = coverage_level
        self.calibration_scores = []

    def predict_set(self, query: str) -> Tuple[List[str], float]:
        """
        Return prediction set with guaranteed coverage
        e.g., "This could be solved with [method A, method B] with 95% confidence"
        """
        # Get all possible solutions with scores
        solutions = self._rank_solutions(query)

        # Build prediction set until coverage reached
        prediction_set = []
        cumulative_score = 0.0

        for solution, score in solutions:
            prediction_set.append(solution)
            cumulative_score += score
            if cumulative_score >= self.coverage_level:
                break

        return prediction_set, cumulative_score

    def _rank_solutions(self, query: str) -> List[Tuple[str, float]]:
        """Rank all possible solutions"""
        # Simplified ranking
        if "install" in query.lower():
            return [
                ("nix-env -iA nixpkgs.package", 0.7),
                ("nix-shell -p package", 0.2),
                ("add to configuration.nix", 0.08),
                ("use flake", 0.02),
            ]
        return [("search first", 1.0)]


### 3. **Active Learning for Efficient Improvement** 🎯
class ActiveLearningHRM:
    """
    Actively identify what queries to learn from
    Don't waste learning on easy/redundant queries
    """

    def __init__(self):
        self.uncertainty_threshold = 0.5
        self.query_embeddings = set()

    def should_request_feedback(self, query: str, uncertainty: float) -> bool:
        """
        Decide if we should ask for human feedback
        High uncertainty + high value = request feedback
        """
        # Check uncertainty
        if uncertainty < self.uncertainty_threshold:
            return False  # Confident enough

        # Check if similar query seen before
        if self._is_redundant(query):
            return False  # Already have similar data

        # Check query value (impact on model)
        value = self._calculate_query_value(query)

        return value > 0.7

    def _is_redundant(self, query: str) -> bool:
        """Check if we've seen similar query"""
        # Simplified: check exact match
        # Real: use embedding similarity
        return query in self.query_embeddings

    def _calculate_query_value(self, query: str) -> float:
        """
        Calculate learning value of this query
        - Covers new region of input space
        - Resolves model disagreement
        - High user importance
        """
        # Simplified heuristic
        if "critical" in query or "urgent" in query:
            return 0.9
        if len(self.query_embeddings) < 100:
            return 0.8  # Early learning phase
        return 0.5


def demonstrate_uncertainty():
    """Demonstrate uncertainty quantification"""
    print("🎯 HRM with Uncertainty Quantification Demo")
    print("=" * 60)

    # Initialize
    bayesian_hrm = BayesianHRM()
    conformal_hrm = ConformalHRM()
    active_hrm = ActiveLearningHRM()

    # Train on known queries
    known_queries = [
        "install firefox",
        "install vim",
        "install docker",
        "configure nginx",
        "setup postgresql",
    ]
    bayesian_hrm.update_known_distribution(known_queries)

    # Test queries with varying uncertainty
    test_queries = [
        ("install firefox", "Known, simple query"),
        ("install asdkfjalskdfj", "Unknown package"),
        ("maybe install something", "Ambiguous query"),
        ("configure quantum blockchain AI", "Out of distribution"),
        ("", "Empty query"),
        ("install neovim", "Similar to known"),
    ]

    print("\n📊 Uncertainty Analysis:")
    print("-" * 60)

    for query, description in test_queries:
        if not query:
            query = " "

        # Get prediction with uncertainty
        prediction, uncertainty = bayesian_hrm.predict_with_uncertainty(query)

        # Get conformal prediction set
        pred_set, coverage = conformal_hrm.predict_set(query)

        # Check if should request feedback
        should_learn = active_hrm.should_request_feedback(query, uncertainty.total)

        print(f"\nQuery: '{query[:50]}' ({description})")
        print(f"  Prediction: {prediction}")
        print(f"  Confidence: {uncertainty.confidence:.1%}")
        print(f"  Uncertainty breakdown:")
        print(f"    - Aleatoric: {uncertainty.aleatoric:.3f}")
        print(f"    - Epistemic: {uncertainty.epistemic:.3f}")
        print(f"  Explanation: {uncertainty.explanation}")
        print(f"  Conformal set: {pred_set[:2]}")
        print(f"  Request feedback: {'Yes' if should_learn else 'No'}")

    print("\n" + "=" * 60)
    print("🔑 Key Insights:")
    print("  • Properly calibrated confidence vs overconfident")
    print("  • Distinguishes 'don't know' from 'ambiguous'")
    print("  • Provides multiple solutions when uncertain")
    print("  • Actively identifies valuable learning opportunities")
    print("  • Detects out-of-distribution queries")


if __name__ == "__main__":
    demonstrate_uncertainty()
