"""
Context-Aware HRM (Enhanced with Context Engine)

Integrates the neural HRM with the Context Awareness Engine to achieve:
- Higher accuracy through contextual features
- Multi-task learning (intent + state + frustration)
- Personalized predictions based on session state
- Self-improving through context feedback

This is the evolution of HRM: from isolated intent recognition to
holistic context-aware intelligence.
"""

import torch
import torch.nn as nn
import logging
from typing import Dict, Optional, List, Tuple
from pathlib import Path
import time

from .hrm_neural_real import NeuralHRMReasoner, HierarchicalReasoningModel
from ..mycelix.context import get_context_engine, Context, SessionState, ProjectType, IntentType

logger = logging.getLogger(__name__)


class ContextAwareHRM(nn.Module):
    """
    Enhanced HRM with Context Awareness

    Architecture:
    - Query Encoder: BiLSTM (from original HRM)
    - Context Encoder: MLP for context features
    - Fusion Layer: Combines query + context
    - Multi-Task Heads:
      * Intent prediction (10 classes)
      * Frustration detection (binary)
      * Session state (5 classes)
      * Next action suggestion (optional)

    Input Features:
    - Query text (character-level BiLSTM)
    - Recent command count
    - Recent file count
    - Project type (one-hot)
    - Session state (one-hot)
    - Time context (one-hot)
    - Command success rate
    - Session duration (normalized)
    """

    def __init__(
        self,
        base_hrm: HierarchicalReasoningModel,
        context_feature_dim: int = 64,
        fusion_dim: int = 256
    ):
        super(ContextAwareHRM, self).__init__()

        # Base HRM for query encoding (frozen or fine-tuned)
        self.base_hrm = base_hrm

        # Context encoder (processes context features)
        self.context_encoder = nn.Sequential(
            nn.Linear(context_feature_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.ReLU()
        )

        # Fusion layer (combines query + context)
        # Base HRM outputs 128 dims, context encoder outputs 64 dims
        self.fusion = nn.Sequential(
            nn.Linear(128 + 64, fusion_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(fusion_dim, 128),
            nn.ReLU()
        )

        # Multi-task prediction heads
        self.intent_head = nn.Linear(128, 10)  # 10 NixOS intents
        self.frustration_head = nn.Linear(128, 2)  # Frustrated or not
        self.session_state_head = nn.Linear(128, 5)  # 5 session states

    def forward(
        self,
        query_tensor: torch.Tensor,
        context_features: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Forward pass with query + context

        Args:
            query_tensor: Encoded query (batch_size, max_length)
            context_features: Context vector (batch_size, context_dim)

        Returns:
            Tuple of (intent_logits, frustration_logits, session_state_logits)
        """
        # Encode query using base HRM (up to fc3 layer)
        embedded = self.base_hrm.embedding(query_tensor)
        lstm_out, (hidden, cell) = self.base_hrm.lstm(embedded)

        hidden_fwd = hidden[-2, :, :]
        hidden_bwd = hidden[-1, :, :]
        combined = torch.cat((hidden_fwd, hidden_bwd), dim=1)

        # Run through HRM layers up to fc3
        x = self.base_hrm.fc1(combined)
        x = self.base_hrm.bn1(x)
        x = self.base_hrm.relu(x)
        x = self.base_hrm.dropout1(x)

        x = self.base_hrm.fc2(x)
        x = self.base_hrm.bn2(x)
        x = self.base_hrm.relu(x)
        x = self.base_hrm.dropout2(x)

        x = self.base_hrm.fc3(x)
        x = self.base_hrm.bn3(x)
        x = self.base_hrm.relu(x)
        x = self.base_hrm.dropout3(x)

        query_features = x  # (batch_size, 128)

        # Encode context
        context_encoded = self.context_encoder(context_features)  # (batch_size, 64)

        # Fuse query + context
        fused = torch.cat([query_features, context_encoded], dim=1)  # (batch_size, 192)
        fused_features = self.fusion(fused)  # (batch_size, 128)

        # Multi-task predictions
        intent_logits = self.intent_head(fused_features)
        frustration_logits = self.frustration_head(fused_features)
        session_logits = self.session_state_head(fused_features)

        return intent_logits, frustration_logits, session_logits


class ContextAwareHRMReasoner:
    """
    Production Context-Aware HRM

    Combines the neural HRM with Context Engine for enhanced predictions.
    Falls back to base HRM if context unavailable.
    """

    def __init__(
        self,
        base_hrm: Optional[NeuralHRMReasoner] = None,
        enable_context: bool = True
    ):
        """
        Initialize Context-Aware HRM

        Args:
            base_hrm: Base HRM reasoner (or create new one)
            enable_context: Enable context engine integration
        """
        # Base HRM for query encoding
        from .hrm_neural_real import get_hrm_reasoner
        self.base_hrm = base_hrm or get_hrm_reasoner()

        # Context engine (optional)
        self.enable_context = enable_context
        self.context_engine = None

        if enable_context:
            try:
                self.context_engine = get_context_engine()
                logger.info("✅ Context Engine integrated with HRM")
            except Exception as e:
                logger.warning(f"Context Engine unavailable: {e}")
                self.enable_context = False

        # Enhanced model (not loaded yet - would need training)
        self.enhanced_model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Stats
        self.context_enhanced_predictions = 0
        self.fallback_predictions = 0

    def extract_context_features(self, context: Context) -> torch.Tensor:
        """
        Extract numerical features from Context object

        Returns tensor of shape (context_feature_dim,)
        Currently: 64 dimensions
        """
        features = []

        # File activity features (10 dims)
        features.append(len(context.active_files))  # Active files count
        features.append(len(context.recent_files))  # Recent files count
        features.extend([0] * 8)  # Reserved for file type distribution

        # Command activity features (10 dims)
        features.append(len(context.recent_commands))  # Recent commands count
        recent_cmds = context.recent_commands[:10] if context.recent_commands else []
        success_rate = sum(1 for cmd in recent_cmds if cmd.success) / max(1, len(recent_cmds))
        features.append(success_rate)  # Success rate
        features.extend([0] * 8)  # Reserved for command patterns

        # Project context (10 dims - one-hot for project type)
        project_types = list(ProjectType)
        project_one_hot = [0] * 10
        if context.primary_project:
            try:
                idx = project_types.index(context.primary_project)
                project_one_hot[idx] = 1
            except ValueError:
                pass
        features.extend(project_one_hot)

        # Session state (5 dims - one-hot)
        session_states = list(SessionState)
        session_one_hot = [0] * 5
        try:
            idx = session_states.index(context.session_state)
            session_one_hot[idx] = 1
        except ValueError:
            pass
        features.extend(session_one_hot)

        # Time context (4 dims - one-hot)
        time_contexts = ["morning", "afternoon", "evening", "late_night"]
        time_one_hot = [0] * 4
        try:
            idx = time_contexts.index(context.time_context.value)
            time_one_hot[idx] = 1
        except ValueError:
            pass
        features.extend(time_one_hot)

        # Session duration (1 dim - normalized to 0-1)
        from datetime import datetime
        duration_hours = (datetime.now() - context.session_start).total_seconds() / 3600
        normalized_duration = min(duration_hours / 8.0, 1.0)  # Cap at 8 hours = 1.0
        features.append(normalized_duration)

        # Project confidence (1 dim)
        features.append(context.project_confidence)

        # Intent confidence (1 dim)
        if context.current_intent:
            features.append(context.current_intent.confidence)
        else:
            features.append(0.0)

        # Pad to exactly 64 dimensions
        while len(features) < 64:
            features.append(0.0)

        features = features[:64]  # Ensure exactly 64

        return torch.tensor(features, dtype=torch.float32).unsqueeze(0)

    def predict(self, query: str) -> Dict:
        """
        Enhanced prediction with context awareness

        Args:
            query: User query string

        Returns:
            Dict with:
                - intent: Predicted intent
                - confidence: Confidence score
                - frustration_detected: Boolean
                - predicted_session_state: SessionState prediction
                - context_enhanced: Whether context was used
                - inference_time_ms: Time taken
        """
        start_time = time.perf_counter()

        # Get base HRM prediction
        base_result = self.base_hrm.predict(query)

        # Try to enhance with context
        if self.enable_context and self.context_engine:
            try:
                # Get current context
                context = self.context_engine.get_current_context()

                # Enhance prediction with context
                enhanced_result = self._predict_with_context(
                    query,
                    context,
                    base_result
                )

                self.context_enhanced_predictions += 1

                inference_time = (time.perf_counter() - start_time) * 1000
                enhanced_result['inference_time_ms'] = inference_time

                return enhanced_result

            except Exception as e:
                logger.debug(f"Context enhancement failed, using base HRM: {e}")
                self.fallback_predictions += 1

        # Fallback to base HRM
        self.fallback_predictions += 1
        base_result['context_enhanced'] = False
        base_result['frustration_detected'] = False
        base_result['predicted_session_state'] = None

        return base_result

    def _predict_with_context(
        self,
        query: str,
        context: Context,
        base_result: Dict
    ) -> Dict:
        """
        Enhanced prediction using context

        Currently uses heuristics; would use trained model in production.
        """
        # Start with base prediction
        result = base_result.copy()
        result['context_enhanced'] = True

        # Detect frustration from context
        frustration_score = 0.0

        if context.session_state == SessionState.FRUSTRATED:
            frustration_score += 0.5

        recent_cmds = context.recent_commands[:10] if context.recent_commands else []
        if recent_cmds:
            failure_rate = sum(1 for cmd in recent_cmds if not cmd.success) / len(recent_cmds)
            frustration_score += failure_rate * 0.5

        result['frustration_detected'] = frustration_score > 0.5
        result['frustration_score'] = frustration_score

        # Session state prediction (from context)
        result['predicted_session_state'] = context.session_state.value

        # Adjust confidence based on context alignment
        if context.current_intent:
            # If context intent matches HRM intent, boost confidence
            context_intent_map = {
                IntentType.DEVELOPING: ['install', 'config', 'shell'],
                IntentType.DEBUGGING: ['info', 'search', 'help'],
                IntentType.CONFIGURING: ['config', 'update'],
                IntentType.LEARNING: ['help', 'info', 'search'],
                IntentType.MAINTAINING: ['update', 'remove']
            }

            expected_intents = context_intent_map.get(context.current_intent.intent_type, [])
            if result['intent'] in expected_intents:
                # Context agrees with HRM - boost confidence
                result['confidence'] = min(result['confidence'] * 1.2, 1.0)
                result['context_agreement'] = True
            else:
                # Context disagrees - reduce confidence
                result['confidence'] = result['confidence'] * 0.9
                result['context_agreement'] = False

        # Add context summary
        result['context_summary'] = {
            'project_type': context.primary_project.value if context.primary_project else None,
            'session_state': context.session_state.value,
            'active_files': len(context.active_files),
            'recent_commands': len(context.recent_commands)
        }

        return result

    def get_stats(self) -> Dict:
        """Get statistics including context enhancement metrics"""
        base_stats = self.base_hrm.get_stats()

        total_predictions = self.context_enhanced_predictions + self.fallback_predictions
        enhancement_rate = self.context_enhanced_predictions / max(1, total_predictions)

        return {
            **base_stats,
            'context_enhanced_predictions': self.context_enhanced_predictions,
            'fallback_predictions': self.fallback_predictions,
            'context_enhancement_rate': enhancement_rate,
            'context_engine_enabled': self.enable_context
        }


# Global instance
_context_aware_hrm: Optional[ContextAwareHRMReasoner] = None


def get_context_aware_hrm() -> ContextAwareHRMReasoner:
    """Get or create global Context-Aware HRM instance"""
    global _context_aware_hrm

    if _context_aware_hrm is None:
        _context_aware_hrm = ContextAwareHRMReasoner(enable_context=True)
        if _context_aware_hrm.enable_context:
            print("🧠 Context-Aware HRM initialized!")
        else:
            print("⚠️ Context-Aware HRM running without context engine")

    return _context_aware_hrm


if __name__ == "__main__":
    import sys

    # Test the context-aware HRM
    hrm = get_context_aware_hrm()

    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
        result = hrm.predict(query)

        print(f"\n🧠 Context-Aware HRM Test")
        print(f"=" * 60)
        print(f"Query: '{query}'")
        print(f"\nPrediction:")
        print(f"  Intent: {result['intent']} (confidence: {result['confidence']:.2f})")
        print(f"  Context Enhanced: {result.get('context_enhanced', False)}")
        print(f"  Frustration: {'Yes' if result.get('frustration_detected') else 'No'}")
        print(f"  Session State: {result.get('predicted_session_state', 'N/A')}")

        if result.get('context_summary'):
            print(f"\nContext:")
            for key, value in result['context_summary'].items():
                print(f"  {key}: {value}")
    else:
        print("Usage: python hrm_context_aware.py 'your query here'")
        print("\nTry:")
        print("  python hrm_context_aware.py 'install firefox'")
        print("  python hrm_context_aware.py 'help with debugging'")
