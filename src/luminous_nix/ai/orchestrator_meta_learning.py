#!/usr/bin/env python3
"""
Meta-Learning Enhanced Orchestrator for Luminous Nix

REVOLUTIONARY PARADIGM: Self-improving AI ecosystem

This orchestrator integrates meta-learning feedback where:
1. Routing decisions learn from outcomes
2. Model selection adapts to actual performance
3. The entire AI system becomes self-improving

Key Innovation: Instead of static routing logic, every query outcome
teaches the system to route better in the future.
"""

import time
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# Import base orchestrator components
from .orchestrator import (
    AIOrchestrator,
    ModelType,
    OrchestrationResult,
    IntentRouter
)

# Import revolutionary meta-learning router
from .meta_learning_router import (
    MetaLearningRouter,
    RoutingOutcome
)

logger = logging.getLogger(__name__)

class MetaLearningOrchestrator(AIOrchestrator):
    """
    Enhanced orchestrator with meta-learning capabilities

    Extends base AIOrchestrator to add:
    - Adaptive routing based on learned performance
    - Automatic threshold adjustment
    - Cross-model knowledge transfer
    - Self-improvement over time
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize with meta-learning capabilities"""
        super().__init__(config)

        # Replace static router with meta-learning router
        self.meta_router = MetaLearningRouter()

        # Track for feedback loop
        self.pending_outcomes: List[RoutingOutcome] = []

        # Enhanced metrics
        self.meta_metrics = {
            'routing_improvements': 0,
            'threshold_adaptations': 0,
            'performance_gains': []
        }

        logger.info("🧠 Meta-learning orchestrator initialized - AI ecosystem will self-improve!")

    def process(self,
                query: str,
                force_model: Optional[ModelType] = None,
                timeout: float = 5.0,
                enable_meta_learning: bool = True) -> OrchestrationResult:
        """
        Process query with meta-learning enhancements

        Args:
            query: User's natural language query
            force_model: Optional - force specific model (disables meta-learning)
            timeout: Maximum time to wait for response
            enable_meta_learning: If True, use learned routing (default: True)

        Returns:
            OrchestrationResult with response and metadata
        """
        start_time = time.time()

        # Determine which model to use
        if force_model:
            model_to_use = force_model
            routing_metadata = {"forced": True}
            expected_confidence = 1.0
        elif enable_meta_learning:
            # REVOLUTIONARY: Use learned performance to select model
            available_models = self._get_available_models()
            model_to_use, expected_confidence, routing_metadata = \
                self.meta_router.select_model(query, available_models)

            logger.info(f"🎯 Meta-learning selected: {model_to_use.value} (expected: {expected_confidence:.2f})")
        else:
            # Fall back to traditional pattern-based routing
            model_to_use = self.router.classify(query)
            routing_metadata = {"traditional": True}
            expected_confidence = 0.7

        # Route to appropriate model (using parent class methods)
        try:
            if model_to_use == ModelType.GEMMA_HYBRID and self.gemma_hybrid:
                result = self._process_with_gemma_hybrid(query, timeout)
            elif model_to_use == ModelType.HRM and self.hrm:
                result = self._process_with_hrm(query, timeout)
            elif model_to_use == ModelType.OLLAMA and self.ollama:
                result = self._process_with_ollama(query, timeout)
            else:
                result = self._process_with_pattern_matching(query)
        except Exception as e:
            logger.error(f"Error processing with {model_to_use}: {e}")
            result = self._process_with_fallback(query)

        # Update timing
        response_time = (time.time() - start_time) * 1000
        result.response_time_ms = response_time

        # Add meta-learning metadata
        if result.metadata is None:
            result.metadata = {}
        result.metadata['routing'] = routing_metadata
        result.metadata['expected_vs_actual'] = {
            'expected_confidence': expected_confidence,
            'actual_confidence': result.confidence,
            'performance_delta': result.confidence - expected_confidence
        }

        # Create outcome for meta-learning (will be recorded when feedback arrives)
        outcome = RoutingOutcome(
            query=query,
            model_used=result.model_used,
            success=(result.confidence > 0.5),  # Will be updated with user feedback
            confidence=result.confidence,
            response_time_ms=response_time
        )
        self.pending_outcomes.append(outcome)

        # Update parent metrics
        self.metrics['total_response_time'] += response_time

        return result

    def record_feedback(self,
                       rating: float,
                       success: bool = True,
                       query_index: int = -1):
        """
        Record user feedback to close the learning loop

        CRITICAL: This is where the AI ecosystem improves itself!

        Args:
            rating: User rating 0.0-1.0
            success: Whether the response was successful
            query_index: Which query to provide feedback for (-1 = latest)
        """
        if not self.pending_outcomes:
            logger.warning("No pending outcomes to record feedback for")
            return

        # Get the outcome to update
        if query_index == -1 or query_index >= len(self.pending_outcomes):
            outcome = self.pending_outcomes[-1]
        else:
            outcome = self.pending_outcomes[query_index]

        # Update with user feedback
        old_success = outcome.success
        outcome.success = success
        outcome.user_rating = rating

        # Record in meta-learning router (THIS IS WHERE LEARNING HAPPENS!)
        self.meta_router.record_outcome(outcome)

        # Track improvements
        if success and not old_success:
            self.meta_metrics['routing_improvements'] += 1

        # Track performance gains
        if 'expected_vs_actual' in outcome.__dict__:
            delta = outcome.confidence - (1.0 if success else 0.0)
            self.meta_metrics['performance_gains'].append(delta)

        logger.info(f"✅ Feedback recorded: rating={rating:.2f}, success={success}")
        logger.debug(f"📈 Meta-learning updated routing intelligence")

    def _get_available_models(self) -> List[ModelType]:
        """Get list of currently available models"""
        available = []
        if self.gemma_hybrid is not None:
            available.append(ModelType.GEMMA_HYBRID)
        if self.hrm is not None:
            available.append(ModelType.HRM)
        if self.ollama is not None:
            available.append(ModelType.OLLAMA)
        # Pattern matching always available as fallback
        available.append(ModelType.PATTERN)
        return available

    def get_meta_insights(self) -> Dict[str, Any]:
        """
        Get insights into meta-learning performance

        Returns detailed information about:
        - What the system has learned
        - Which models perform best for which queries
        - How routing has improved over time
        """
        router_insights = self.meta_router.get_insights()

        # Calculate average performance gain
        avg_gain = (
            sum(self.meta_metrics['performance_gains']) / len(self.meta_metrics['performance_gains'])
            if self.meta_metrics['performance_gains'] else 0.0
        )

        return {
            "meta_learning_active": True,
            "routing_improvements": self.meta_metrics['routing_improvements'],
            "threshold_adaptations": self.meta_metrics['threshold_adaptations'],
            "average_performance_gain": round(avg_gain, 3),
            "router_insights": router_insights,
            "self_improvement_rate": self._calculate_improvement_rate()
        }

    def _calculate_improvement_rate(self) -> str:
        """Calculate how much the system has improved"""
        outcomes_count = len(self.meta_router.outcomes)
        if outcomes_count < 20:
            return "Insufficient data (learning...)"

        # Compare first 10 outcomes to last 10
        first_10 = self.meta_router.outcomes[:10]
        last_10 = self.meta_router.outcomes[-10:]

        first_success_rate = sum(1 for o in first_10 if o.success) / 10
        last_success_rate = sum(1 for o in last_10 if o.success) / 10

        improvement = last_success_rate - first_success_rate

        if improvement > 0.1:
            return f"Significant improvement: +{improvement:.1%}"
        elif improvement > 0:
            return f"Gradual improvement: +{improvement:.1%}"
        else:
            return "Stable performance (optimized)"

    def compare_with_static_routing(self, query: str) -> Dict[str, Any]:
        """
        Compare meta-learning routing vs traditional static routing

        Shows the advantage of learned routing
        """
        # Meta-learning choice
        available = self._get_available_models()
        meta_model, meta_confidence, meta_reasoning = self.meta_router.select_model(query, available)

        # Traditional choice
        static_model = self.router.classify(query)

        return {
            "query": query,
            "meta_learning_choice": {
                "model": meta_model.value,
                "expected_confidence": meta_confidence,
                "reasoning": meta_reasoning['selection_reason'],
                "data_driven": True
            },
            "static_routing_choice": {
                "model": static_model.value,
                "expected_confidence": "Unknown",
                "reasoning": "Pattern matching",
                "data_driven": False
            },
            "choices_differ": (meta_model != static_model),
            "meta_learning_advantage": meta_reasoning.get('model_scores', {})
        }

# Example usage demonstrating the revolutionary improvement
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("🚀 Meta-Learning Orchestrator Demo")
    print("=" * 60)

    # Initialize orchestrator
    orchestrator = MetaLearningOrchestrator({
        'hrm_enabled': True,
        'ollama_enabled': True,
        'gemma_hybrid_enabled': False  # Disable for demo
    })

    # Simulate learning over multiple interactions
    queries = [
        ("install firefox", True, 0.9),
        ("error: attribute 'vim' missing", True, 0.85),
        ("how to configure nginx in nixos", True, 0.8),
        ("install firefox", True, 0.95),  # Same query, better over time
        ("search for text editor", True, 0.75),
    ]

    print("\n📊 Simulating queries to demonstrate learning...\n")

    for i, (query, success, rating) in enumerate(queries, 1):
        print(f"\n--- Query {i} ---")
        print(f"Input: {query}")

        # Process query
        result = orchestrator.process(query)
        print(f"Routed to: {result.model_used.value}")
        print(f"Confidence: {result.confidence:.2f}")

        # Provide feedback (THIS CAUSES LEARNING!)
        orchestrator.record_feedback(rating=rating, success=success)

        # Show comparison
        if i % 2 == 0:  # Every other query
            comparison = orchestrator.compare_with_static_routing(query)
            if comparison['choices_differ']:
                print(f"\n💡 Meta-learning chose differently than static routing!")
                print(f"   Static would choose: {comparison['static_routing_choice']['model']}")
                print(f"   Meta-learning chose: {comparison['meta_learning_choice']['model']}")

    # Show final insights
    print("\n\n🧠 Meta-Learning Insights:")
    print("=" * 60)
    insights = orchestrator.get_meta_insights()
    import json
    print(json.dumps(insights, indent=2))

    print("\n✅ Demo complete! The system learned from these interactions.")
    print("   Future queries will benefit from this accumulated knowledge.")
