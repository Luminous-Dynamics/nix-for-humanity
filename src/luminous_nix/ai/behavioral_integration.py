"""
Behavioral Detection Integration Layer

This module integrates all behavioral detection components with the
existing simple_chat.py conversation system.

Revolutionary features:
1. Passive behavioral observation (no surveys needed!)
2. Continuous learning from real interactions
3. Archetype evolution tracking
4. Cold-start to warm-up transition
5. Explainable predictions

This layer sits between the conversation system and the neural network,
recording behavioral signals and providing archetype predictions.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

from .behavioral_features import BehavioralFeatureExtractor, BehavioralSignal
from .behavioral_classifier import BehavioralArchetypeDetector, get_behavioral_detector
from .continuous_learner import ContinuousLearner, get_continuous_learner
from .archetype_evolution import ArchetypeEvolutionTracker, get_evolution_tracker
from .user_profiler import UserArchetype, TechnicalLevel


class BehavioralIntegrationLayer:
    """
    Integration layer for neural network behavioral detection.

    This layer:
    1. Records behavioral signals from user interactions
    2. Extracts features for neural network
    3. Predicts archetype using neural network
    4. Learns from confirmed archetypes
    5. Tracks evolution over time
    """

    def __init__(self, user_id: str = "default_user"):
        """
        Initialize behavioral integration.

        Args:
            user_id: User to track
        """
        self.user_id = user_id

        # Initialize components
        self.detector = get_behavioral_detector()
        self.learner = get_continuous_learner(self.detector)
        self.evolution = get_evolution_tracker(user_id)

        # Track signals for this session
        self.session_signals: List[BehavioralSignal] = []

    def record_interaction(
        self,
        query: str,
        response: str,
        command_used: Optional[str] = None,
        response_time_ms: float = 0.0,
        reading_time_ms: float = 0.0,
        user_action: Optional[str] = None
    ):
        """
        Record a user interaction as a behavioral signal.

        This is called after EVERY interaction to build behavioral profile.

        Args:
            query: What user asked
            response: What system responded
            command_used: Any NixOS command executed
            response_time_ms: How long until user responded
            reading_time_ms: How long user spent reading response
            user_action: What user did next (executed, skipped, asked_clarification, etc.)
        """
        signal = BehavioralSignal(
            user_id=self.user_id,
            timestamp=datetime.now().isoformat(),
            query=query,
            command_used=command_used,
            query_type=self._classify_query_type(query),
            response_length=len(response),
            reading_time_ms=reading_time_ms,
            response_time_ms=response_time_ms,
            skipped=user_action == "skipped",
            immediate_action=user_action == "executed" and response_time_ms < 5000,
            asked_clarification=user_action == "asked_clarification",
            requested_alternatives=any(word in query.lower() for word in ["alternative", "other", "instead", "different"]),
            asked_why_how="why" in query.lower() or "how" in query.lower(),
            deep_question=len(query.split()) > 10 and ("explain" in query.lower() or "understand" in query.lower()),
            requested_teaching="teach" in query.lower() or "learn" in query.lower(),
            error_occurred=False,  # Could be detected from context
            customization_attempt="customize" in query.lower() or "config" in query.lower(),
            experimentation="try" in query.lower() or "experiment" in query.lower(),
            automation_request="automate" in query.lower() or "script" in query.lower()
        )

        # Add to session signals
        self.session_signals.append(signal)

        # Add to feature extractor's global storage
        self.detector.feature_extractor.record_signal(signal)

    def get_current_prediction(self) -> Dict[str, Any]:
        """
        Get current archetype prediction from neural network.

        Returns:
            Dictionary with archetype, probabilities, confidence, explanation
        """
        # Get prediction
        archetype, probabilities, confidence = self.detector.detect_archetype(self.user_id)

        # Get explanation
        explanation = self.detector.explain_classification(self.user_id)

        # Get cold-start status
        cold_start = self.evolution.get_cold_start_status()

        # Get learning status
        learning = self.learner.get_learning_status()

        return {
            "archetype": archetype,
            "probabilities": probabilities,
            "confidence": confidence,
            "explanation": explanation,
            "cold_start": cold_start,
            "learning": learning
        }

    def confirm_archetype(
        self,
        true_archetype: UserArchetype,
        confidence: float = 1.0,
        source: str = "user_confirmed"
    ):
        """
        User confirms their true archetype - critical for learning!

        When user explicitly confirms "Yes, I'm a Learner", we:
        1. Extract current behavioral features
        2. Add as training example with high confidence
        3. Record evolution snapshot
        4. Trigger retraining if threshold met

        Args:
            true_archetype: User's confirmed archetype
            confidence: How confident (1.0 = user confirmed, 0.5 = inferred)
            source: How we obtained this ("user_confirmed", "inferred", "feedback")
        """
        # Extract current features
        features = self.detector.feature_extractor.extract_features(self.user_id)

        # Add to continuous learner
        self.learner.add_observation(
            features=features,
            true_archetype=true_archetype,
            confidence=confidence,
            user_id=self.user_id,
            source=source
        )

        # Get current prediction
        _, probabilities, pred_confidence = self.detector.detect_archetype(self.user_id)

        # Record evolution snapshot
        self.evolution.record_snapshot(
            archetype=true_archetype,
            confidence=pred_confidence,
            probabilities=probabilities,
            technical_level=TechnicalLevel.INTERMEDIATE,  # Could extract from features
            data_quality=self.learner._calculate_real_data_ratio()
        )

    def detect_archetype_shift(self) -> Optional[Dict]:
        """
        Check if user's archetype has shifted.

        Returns:
            Shift information if detected, None otherwise
        """
        return self.evolution.detect_archetype_shift()

    def predict_evolution(self) -> Optional[Dict]:
        """
        Predict user's next archetype evolution.

        Returns:
            Evolution prediction if possible, None otherwise
        """
        return self.evolution.predict_next_evolution()

    def get_learning_dashboard(self) -> Dict[str, Any]:
        """
        Get complete learning dashboard with all metrics.

        Returns:
            Comprehensive dashboard data
        """
        # Current prediction
        prediction = self.get_current_prediction()

        # Evolution history
        evolution_history = self.evolution.get_evolution_history()

        # Check for shifts
        shift = self.detect_archetype_shift()

        # Predict next evolution
        next_evolution = self.predict_evolution()

        # Session stats
        session_stats = {
            "interactions_this_session": len(self.session_signals),
            "queries": sum(1 for s in self.session_signals if s.query),
            "commands_executed": sum(1 for s in self.session_signals if s.command_used),
            "questions_asked": sum(1 for s in self.session_signals if s.asked_why_how),
            "alternatives_requested": sum(1 for s in self.session_signals if s.requested_alternatives)
        }

        return {
            "prediction": prediction,
            "evolution_history": evolution_history,
            "archetype_shift": shift,
            "predicted_evolution": next_evolution,
            "session_stats": session_stats
        }

    def _classify_query_type(self, query: str) -> str:
        """
        Classify the type of query for behavioral analysis.

        Returns:
            "install", "config", "search", "explain", "troubleshoot", "general"
        """
        query_lower = query.lower()

        if any(word in query_lower for word in ["install", "add", "get"]):
            return "install"
        elif any(word in query_lower for word in ["config", "configure", "setup", "set"]):
            return "config"
        elif any(word in query_lower for word in ["search", "find", "look for"]):
            return "search"
        elif any(word in query_lower for word in ["explain", "what is", "how does", "why"]):
            return "explain"
        elif any(word in query_lower for word in ["error", "fix", "problem", "broken", "not working"]):
            return "troubleshoot"
        else:
            return "general"


def get_behavioral_integration(user_id: str = "default_user") -> BehavioralIntegrationLayer:
    """Get singleton integration layer for a user"""
    global _integration_layers

    if user_id not in _integration_layers:
        _integration_layers[user_id] = BehavioralIntegrationLayer(user_id)

    return _integration_layers[user_id]


# Global registry (one per user)
_integration_layers: Dict[str, BehavioralIntegrationLayer] = {}
