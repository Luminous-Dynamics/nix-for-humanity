#!/usr/bin/env python3
"""
Meta-Learning Router for Luminous Nix
Revolutionary paradigm: The routing system learns from outcomes

Instead of static pattern matching, this router:
1. Learns which models perform best for different query types
2. Adapts confidence thresholds based on actual performance
3. Transfers knowledge between models (RL → HRM → Ollama)

PARADIGM SHIFT: The AI ecosystem becomes self-improving
"""

import json
import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field, asdict
from collections import defaultdict
from pathlib import Path
from enum import Enum
import time

logger = logging.getLogger(__name__)

class ModelType(Enum):
    """Available AI models"""
    GEMMA_HYBRID = "gemma_hybrid"
    HRM = "hrm"
    OLLAMA = "ollama"
    PATTERN = "pattern"

@dataclass
class RoutingOutcome:
    """Track outcome of a routing decision"""
    query: str
    model_used: ModelType
    success: bool
    confidence: float
    response_time_ms: float
    user_rating: Optional[float] = None  # 0.0-1.0
    timestamp: float = field(default_factory=time.time)

    # Derived metrics
    query_pattern: str = ""  # Simplified query pattern
    actual_performance: float = 0.0  # Combined metric

@dataclass
class ModelPerformance:
    """Track performance of a specific model for a query pattern"""
    model: ModelType
    pattern: str

    # Statistics
    total_queries: int = 0
    successful_queries: int = 0
    total_response_time: float = 0.0
    user_ratings: List[float] = field(default_factory=list)

    # Adaptive metrics
    success_rate: float = 0.0
    avg_response_time: float = 0.0
    avg_user_rating: float = 0.0
    performance_score: float = 0.0  # Combined metric for routing decisions

    def update(self, outcome: RoutingOutcome):
        """Update performance metrics with new outcome"""
        self.total_queries += 1
        if outcome.success:
            self.successful_queries += 1

        self.total_response_time += outcome.response_time_ms

        if outcome.user_rating is not None:
            self.user_ratings.append(outcome.user_rating)
            if len(self.user_ratings) > 100:  # Keep last 100 ratings
                self.user_ratings.pop(0)

        # Update derived metrics
        self.success_rate = self.successful_queries / self.total_queries
        self.avg_response_time = self.total_response_time / self.total_queries
        self.avg_user_rating = (
            sum(self.user_ratings) / len(self.user_ratings)
            if self.user_ratings else 0.5
        )

        # Performance score: 40% success + 30% rating + 30% speed
        # Speed component: faster = better (normalized to 0-1)
        speed_score = max(0, 1 - (self.avg_response_time / 5000))  # 5s = 0 score

        self.performance_score = (
            0.4 * self.success_rate +
            0.3 * self.avg_user_rating +
            0.3 * speed_score
        )

@dataclass
class AdaptiveThresholds:
    """Dynamic confidence thresholds that adapt to actual performance"""
    model: ModelType

    # Adaptive thresholds
    min_confidence: float = 0.5
    optimal_confidence: float = 0.75

    # Adaptation parameters
    success_history: List[Tuple[float, bool]] = field(default_factory=list)  # (confidence, success)

    def update(self, confidence: float, success: bool):
        """Update thresholds based on actual outcomes"""
        self.success_history.append((confidence, success))
        if len(self.success_history) > 100:
            self.success_history.pop(0)

        # Analyze: What confidence level gives best results?
        if len(self.success_history) >= 20:
            # Find confidence level where success rate is acceptable (>80%)
            sorted_history = sorted(self.success_history, key=lambda x: x[0])

            # Calculate success rate at different confidence levels
            for threshold in [0.5, 0.6, 0.7, 0.8, 0.9]:
                above_threshold = [s for c, s in sorted_history if c >= threshold]
                if above_threshold:
                    success_rate = sum(above_threshold) / len(above_threshold)
                    if success_rate >= 0.8:
                        self.min_confidence = threshold
                        break

    def should_use_model(self, confidence: float) -> bool:
        """Decide if model confidence is sufficient"""
        return confidence >= self.min_confidence

class MetaLearningRouter:
    """
    Revolutionary router that learns from outcomes

    Key innovation: Instead of static patterns, routing decisions are based on
    learned performance across different query types and models.
    """

    def __init__(self, state_file: Optional[Path] = None):
        """Initialize meta-learning router"""
        self.state_file = state_file or Path.home() / ".cache/luminous-nix/meta_routing_state.json"

        # Performance tracking: pattern → model → performance
        self.model_performance: Dict[str, Dict[ModelType, ModelPerformance]] = defaultdict(
            lambda: defaultdict(lambda: ModelPerformance(ModelType.PATTERN, "unknown"))
        )

        # Adaptive thresholds per model
        self.thresholds: Dict[ModelType, AdaptiveThresholds] = {
            model: AdaptiveThresholds(model) for model in ModelType
        }

        # Outcome history for analysis
        self.outcomes: List[RoutingOutcome] = []

        # Load previous learning
        self.load_state()

        logger.info("🧠 Meta-learning router initialized with adaptive intelligence")

    def _simplify_pattern(self, query: str) -> str:
        """Simplify query to a pattern for learning"""
        query_lower = query.lower()

        # Categorize by intent
        if any(word in query_lower for word in ['install', 'add package', 'get']):
            return "install"
        elif any(word in query_lower for word in ['error', 'failed', 'broken']):
            return "error_resolution"
        elif any(word in query_lower for word in ['configure', 'setup', 'enable']):
            return "configuration"
        elif any(word in query_lower for word in ['search', 'find', 'list']):
            return "search"
        elif any(word in query_lower for word in ['explain', 'what is', 'how']):
            return "explanation"
        elif any(word in query_lower for word in ['optimize', 'improve', 'faster']):
            return "optimization"
        else:
            return "general"

    def select_model(self, query: str, available_models: List[ModelType]) -> Tuple[ModelType, float, Dict[str, Any]]:
        """
        Select best model based on learned performance

        Returns:
            (selected_model, expected_confidence, reasoning_metadata)
        """
        pattern = self._simplify_pattern(query)

        # Get performance for each available model
        model_scores = {}
        for model in available_models:
            if model not in self.model_performance[pattern]:
                # No data yet, use default heuristics
                default_scores = {
                    ModelType.GEMMA_HYBRID: 0.75,
                    ModelType.HRM: 0.70,
                    ModelType.OLLAMA: 0.65,
                    ModelType.PATTERN: 0.40
                }
                model_scores[model] = default_scores.get(model, 0.5)
            else:
                perf = self.model_performance[pattern][model]
                model_scores[model] = perf.performance_score

        # Select model with highest learned performance
        best_model = max(model_scores.items(), key=lambda x: x[1])
        selected_model, expected_performance = best_model

        # Metadata for transparency
        metadata = {
            "pattern": pattern,
            "model_scores": {m.value: score for m, score in model_scores.items()},
            "selection_reason": f"Highest learned performance ({expected_performance:.2f}) for '{pattern}' queries",
            "data_points": self.model_performance[pattern][selected_model].total_queries
        }

        logger.debug(f"📊 Selected {selected_model.value} for '{pattern}' (score: {expected_performance:.2f})")

        return selected_model, expected_performance, metadata

    def record_outcome(self, outcome: RoutingOutcome):
        """
        Record routing outcome and update learned performance

        CRITICAL: This is where meta-learning happens!
        """
        # Derive pattern and performance
        outcome.query_pattern = self._simplify_pattern(outcome.query)

        # Calculate actual performance
        speed_score = max(0, 1 - (outcome.response_time_ms / 5000))
        outcome.actual_performance = (
            (0.4 if outcome.success else 0) +
            (0.3 * (outcome.user_rating or 0.5)) +
            (0.3 * speed_score)
        )

        # Update model performance for this pattern
        pattern = outcome.query_pattern
        model = outcome.model_used

        if model not in self.model_performance[pattern]:
            self.model_performance[pattern][model] = ModelPerformance(model, pattern)

        self.model_performance[pattern][model].update(outcome)

        # Update adaptive thresholds
        self.thresholds[model].update(outcome.confidence, outcome.success)

        # Store outcome
        self.outcomes.append(outcome)
        if len(self.outcomes) > 1000:  # Keep last 1000
            self.outcomes.pop(0)

        # Periodic state persistence
        if len(self.outcomes) % 10 == 0:
            self.save_state()

        logger.debug(f"📈 Updated performance: {model.value} on '{pattern}' → {self.model_performance[pattern][model].performance_score:.2f}")

    def get_threshold(self, model: ModelType) -> float:
        """Get adaptive threshold for model"""
        return self.thresholds[model].min_confidence

    def should_route_to(self, model: ModelType, confidence: float) -> bool:
        """Decide if confidence is sufficient for model (adaptive)"""
        return self.thresholds[model].should_use_model(confidence)

    def get_insights(self) -> Dict[str, Any]:
        """Get meta-learning insights for debugging/monitoring"""
        insights = {
            "total_outcomes": len(self.outcomes),
            "patterns_learned": len(self.model_performance),
            "adaptive_thresholds": {
                model.value: {
                    "min_confidence": t.min_confidence,
                    "data_points": len(t.success_history)
                }
                for model, t in self.thresholds.items()
            },
            "top_patterns": {}
        }

        # Get top performing model per pattern
        for pattern, models in self.model_performance.items():
            if models:
                best = max(models.items(), key=lambda x: x[1].performance_score)
                model, perf = best
                insights["top_patterns"][pattern] = {
                    "best_model": model.value,
                    "score": round(perf.performance_score, 2),
                    "queries": perf.total_queries
                }

        return insights

    def save_state(self):
        """Persist learned state"""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)

            state = {
                "version": "1.0",
                "timestamp": time.time(),
                "model_performance": {},
                "thresholds": {},
                "recent_outcomes": []
            }

            # Serialize model performance
            for pattern, models in self.model_performance.items():
                state["model_performance"][pattern] = {}
                for model, perf in models.items():
                    state["model_performance"][pattern][model.value] = asdict(perf)

            # Serialize thresholds
            for model, threshold in self.thresholds.items():
                state["thresholds"][model.value] = {
                    "min_confidence": threshold.min_confidence,
                    "optimal_confidence": threshold.optimal_confidence,
                    "success_history": threshold.success_history[-50:]  # Last 50
                }

            # Store recent outcomes
            state["recent_outcomes"] = [
                asdict(outcome) for outcome in self.outcomes[-100:]
            ]

            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)

            logger.debug(f"💾 Saved meta-learning state to {self.state_file}")

        except Exception as e:
            logger.warning(f"Failed to save meta-learning state: {e}")

    def load_state(self):
        """Load previously learned state"""
        if not self.state_file.exists():
            logger.info("No previous meta-learning state found (this is normal for first run)")
            return

        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)

            # Restore model performance
            for pattern, models in state.get("model_performance", {}).items():
                for model_str, perf_dict in models.items():
                    model = ModelType(model_str)
                    perf = ModelPerformance(**perf_dict)
                    self.model_performance[pattern][model] = perf

            # Restore thresholds
            for model_str, threshold_dict in state.get("thresholds", {}).items():
                model = ModelType(model_str)
                self.thresholds[model].min_confidence = threshold_dict["min_confidence"]
                self.thresholds[model].optimal_confidence = threshold_dict["optimal_confidence"]
                self.thresholds[model].success_history = [
                    tuple(item) for item in threshold_dict.get("success_history", [])
                ]

            logger.info(f"✅ Loaded meta-learning state: {len(self.model_performance)} patterns, {len(self.outcomes)} outcomes")

        except Exception as e:
            logger.warning(f"Failed to load meta-learning state: {e}")

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    router = MetaLearningRouter()

    # Simulate some queries
    queries = [
        "install firefox",
        "error: attribute 'vim' missing",
        "how to configure nginx",
        "search for text editor"
    ]

    for query in queries:
        model, confidence, metadata = router.select_model(query, list(ModelType))
        print(f"\nQuery: {query}")
        print(f"Selected: {model.value} (confidence: {confidence:.2f})")
        print(f"Reason: {metadata['selection_reason']}")

        # Simulate outcome
        outcome = RoutingOutcome(
            query=query,
            model_used=model,
            success=True,
            confidence=confidence,
            response_time_ms=1500,
            user_rating=0.8
        )
        router.record_outcome(outcome)

    # Show insights
    print("\n🧠 Meta-Learning Insights:")
    print(json.dumps(router.get_insights(), indent=2))
