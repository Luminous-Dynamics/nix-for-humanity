"""Enhanced Intent Recognition Pipeline with LLM Support

This creates a beautiful flow where patterns and AI work together
in harmony, each contributing their strengths.
"""

import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from .intents import Intent, IntentType, IntentRecognizer
from .llm_intent_recognizer import LLMIntentRecognizer, SmartIntentRouter

logger = logging.getLogger(__name__)


@dataclass
class IntentContext:
    """Context for intent recognition including history and user preferences."""
    user_history: List[str] = field(default_factory=list)
    last_intent: Optional[Intent] = None
    corrections: Dict[str, str] = field(default_factory=dict)  # text -> correct intent
    prefer_llm: bool = False
    user_persona: Optional[str] = None


class EnhancedIntentPipeline:
    """
    A beautiful orchestration of pattern matching and AI understanding.
    
    This pipeline:
    1. Tries fast pattern matching first
    2. Enhances with LLM when needed
    3. Learns from user corrections
    4. Adapts to user preferences
    """
    
    def __init__(self, context: Optional[IntentContext] = None):
        """Initialize the enhanced pipeline."""
        self.context = context or IntentContext()
        
        # Initialize recognizers
        self.pattern_recognizer = IntentRecognizer()
        self.smart_router = SmartIntentRouter(prefer_llm=self.context.prefer_llm)
        
        # Learning storage (in-memory for now)
        self.learning_data = []
        
        # Performance metrics
        self.metrics = {
            'pattern_hits': 0,
            'llm_assists': 0,
            'corrections': 0,
            'avg_latency': 0
        }
        
    def recognize(self, text: str) -> Intent:
        """
        Recognize intent with intelligence and grace.
        
        The flow:
        1. Check if we've seen this exact text before (cache)
        2. Try pattern matching (1ms)
        3. If uncertain, enhance with LLM (500ms)
        4. Learn from the result
        """
        start_time = time.time()
        
        # Check corrections first (user has taught us)
        if text in self.context.corrections:
            correct_type = self.context.corrections[text]
            intent = Intent(
                type=IntentType(correct_type),
                entities={},
                confidence=1.0,  # User confirmed this
                raw_text=text
            )
            logger.info(f"Using learned correction for '{text}' -> {correct_type}")
            return intent
            
        # Use the smart router which handles the hybrid approach
        intent = self.smart_router.recognize(
            text, 
            context={
                'history': self.context.user_history,
                'last_intent': self.context.last_intent,
                'persona': self.context.user_persona
            }
        )
        
        # Track metrics
        latency = time.time() - start_time
        self._update_metrics(intent, latency)
        
        # Update context
        self.context.user_history.append(text)
        self.context.last_intent = intent
        
        # Log for analysis
        logger.debug(f"Intent recognized in {latency:.3f}s: {intent.type} (confidence: {intent.confidence})")
        
        return intent
        
    def provide_correction(self, text: str, correct_intent: IntentType):
        """
        Learn from user corrections.
        
        This is where the system becomes wiser through interaction.
        """
        # Store correction
        self.context.corrections[text] = correct_intent.value
        
        # Log for learning
        self.learning_data.append({
            'text': text,
            'corrected_to': correct_intent.value,
            'timestamp': time.time()
        })
        
        self.metrics['corrections'] += 1
        
        logger.info(f"Learned: '{text}' should be {correct_intent.value}")
        
    def set_llm_preference(self, prefer_llm: bool):
        """Allow user to choose their comfort level with AI assistance."""
        self.context.prefer_llm = prefer_llm
        self.smart_router.prefer_llm = prefer_llm
        
        mode = "AI-enhanced" if prefer_llm else "Pattern-first"
        logger.info(f"Intent recognition mode: {mode}")
        
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance and usage metrics."""
        return {
            **self.metrics,
            'corrections_learned': len(self.context.corrections),
            'history_length': len(self.context.user_history),
            'llm_available': bool(self.smart_router.recognizer.llm_client)
        }
        
    def _update_metrics(self, intent: Intent, latency: float):
        """Update performance metrics."""
        # Track what method was used
        if latency < 0.01:  # Pattern matching is typically <10ms
            self.metrics['pattern_hits'] += 1
        elif latency > 0.1:  # LLM typically takes >100ms
            self.metrics['llm_assists'] += 1
            
        # Update average latency
        total = self.metrics['pattern_hits'] + self.metrics['llm_assists']
        if total > 0:
            current_avg = self.metrics['avg_latency']
            self.metrics['avg_latency'] = (current_avg * (total - 1) + latency) / total
            

class AdaptiveIntentRecognizer:
    """
    The ultimate intent recognizer that adapts to each user.
    
    Features:
    - Learns from every interaction
    - Adapts to user's language patterns
    - Balances speed and accuracy based on context
    - Provides explanations when asked
    """
    
    def __init__(self):
        """Initialize adaptive recognizer."""
        self.pipeline = EnhancedIntentPipeline()
        self.explanation_mode = False
        
    def recognize(self, text: str, explain: bool = False) -> Intent:
        """
        Recognize intent with optional explanation.
        
        When explain=True, provides reasoning about the decision.
        """
        intent = self.pipeline.recognize(text)
        
        if explain:
            explanation = self._generate_explanation(text, intent)
            intent.explanation = explanation
            
        return intent
        
    def _generate_explanation(self, text: str, intent: Intent) -> str:
        """Generate human-friendly explanation of the recognition."""
        
        explanation_parts = []
        
        # Explain what was recognized
        explanation_parts.append(f"I understood '{text}' as a request to: {intent.type.value.replace('_', ' ')}")
        
        # Explain confidence
        if intent.confidence > 0.9:
            explanation_parts.append("I'm very confident about this.")
        elif intent.confidence > 0.7:
            explanation_parts.append("I'm reasonably confident about this.")
        else:
            explanation_parts.append("I'm not entirely certain, but this seems most likely.")
            
        # Explain method used (if we can determine it)
        metrics = self.pipeline.get_metrics()
        if metrics['avg_latency'] < 0.01:
            explanation_parts.append("(Recognized using pattern matching)")
        elif metrics['llm_available']:
            explanation_parts.append("(Enhanced with AI assistance)")
            
        return " ".join(explanation_parts)
        
    def teach(self, text: str, correct_intent: IntentType):
        """Teach the system the correct intent for a phrase."""
        self.pipeline.provide_correction(text, correct_intent)
        return f"Thank you! I'll remember that '{text}' means {correct_intent.value}"
        
    def set_mode(self, mode: str):
        """Set recognition mode: 'fast', 'balanced', or 'accurate'."""
        if mode == 'fast':
            self.pipeline.set_llm_preference(False)  # Patterns only
        elif mode == 'accurate':
            self.pipeline.set_llm_preference(True)   # Prefer LLM
        else:  # balanced
            self.pipeline.set_llm_preference(False)  # Use LLM only when needed
            
    def get_insights(self) -> Dict[str, Any]:
        """Get insights about recognition performance and patterns."""
        metrics = self.pipeline.get_metrics()
        
        insights = {
            'performance': {
                'average_response_time_ms': metrics['avg_latency'] * 1000,
                'pattern_success_rate': metrics['pattern_hits'] / max(1, metrics['pattern_hits'] + metrics['llm_assists']),
                'ai_assistance_rate': metrics['llm_assists'] / max(1, metrics['pattern_hits'] + metrics['llm_assists']),
            },
            'learning': {
                'phrases_learned': metrics['corrections_learned'],
                'total_interactions': metrics['history_length']
            },
            'capabilities': {
                'ai_available': metrics['llm_available'],
                'mode': 'AI-enhanced' if self.pipeline.context.prefer_llm else 'Pattern-first'
            }
        }
        
        return insights