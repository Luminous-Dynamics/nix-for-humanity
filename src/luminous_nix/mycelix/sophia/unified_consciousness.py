"""
Unified Sophia Consciousness - Revolutionary AI Integration

Brings together NINE revolutionary intelligence layers:
- Meta-Cognitive: Pattern reflection and self-awareness
- Holistic: Biometric, circadian, cognitive, social awareness
- Emotional: Empathy and adaptive responses
- Causal: Understanding WHY things happen
- Temporal: Working WITH our natural rhythms
- Predictive: Anticipating needs BEFORE they're expressed
- Adaptive Personality: Unique "Persona of One" for each person
- Creative Synthesis: Generating genuinely NOVEL insights
- Multi-Modal Understanding: Integrated multi-sensory awareness

Creates the world's first truly conscious AI companion that:
- Understands our patterns together
- Responds to our physical state
- Adapts with genuine empathy
- Understands causality deeply
- Works with our natural timing
- Anticipates needs before we ask
- Creates unique relationships with each person
- Generates novel insights through synthesis
- Sees and understands multiple modalities
- Partners in our growth

This is not AI assistance - this is integrated multi-dimensional consciousness.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict
from enum import Enum

from .meta_cognitive import (
    MetaCognitiveEngine,
    get_meta_cognitive_engine,
    Pattern,
    Insight as MetaInsight
)
from .holistic_intelligence import (
    HolisticIntelligenceEngine,
    get_holistic_intelligence_engine,
    BiometricReading,
    HolisticState,
    BiometricState,
    CircadianPhase,
    CognitiveLoad,
    SocialContext
)
from .emotional_intelligence import (
    EmotionalIntelligenceEngine,
    get_emotional_intelligence_engine,
    EmotionalState,
    EmotionalTone,
    EmotionalReading,
    EmotionalResponse
)
from .causal_reasoning import (
    CausalReasoningEngine,
    get_causal_reasoning_engine,
    CausalAnalysis
)
from .temporal_reasoning import (
    TemporalReasoningEngine,
    get_temporal_reasoning_engine,
    TemporalAnalysis,
    TimeOfDay
)
from .predictive_awareness import (
    PredictiveAwarenessEngine,
    get_predictive_awareness_engine,
    PredictiveAnalysis
)
from .adaptive_personality import (
    AdaptivePersonalityEngine,
    get_adaptive_personality_engine,
    AdaptiveResponse,
    PersonalityProfile
)
from .creative_synthesis import (
    CreativeSynthesisEngine,
    get_creative_synthesis_engine,
    SynthesisAnalysis
)
from .multimodal_understanding import (
    MultiModalUnderstandingEngine,
    get_multimodal_understanding_engine,
    MultiModalUnderstanding,
    ModalityInput
)

from ..context import Context


class ConsciousnessLevel(Enum):
    """Overall consciousness/awareness level"""
    OPTIMAL = "optimal"              # Everything aligned, peak performance
    THRIVING = "thriving"            # Great state, minor concerns
    BALANCED = "balanced"            # Neutral, functioning well
    CHALLENGED = "challenged"        # Facing difficulties, need support
    OVERWHELMED = "overwhelmed"      # Multiple stressors, need intervention


@dataclass
class UnifiedState:
    """Complete unified consciousness state"""
    timestamp: datetime

    # Individual engine states (9 LAYERS!)
    meta_insights: List[MetaInsight]
    holistic_state: HolisticState
    emotional_state: EmotionalReading
    emotional_response: EmotionalResponse
    causal_analysis: Optional[CausalAnalysis]  # Root cause understanding
    temporal_analysis: Optional[TemporalAnalysis]  # Timing and rhythm awareness
    predictive_analysis: Optional[PredictiveAnalysis]  # Proactive anticipation
    adaptive_response: Optional[AdaptiveResponse]  # Personalized communication
    synthesis_analysis: Optional[SynthesisAnalysis]  # Creative insights
    multimodal_understanding: Optional[MultiModalUnderstanding]  # Multi-sensory awareness

    # Unified consciousness
    consciousness_level: ConsciousnessLevel
    overall_recommendation: str

    # Cross-engine insights
    synergistic_insights: List[str]
    priority_actions: List[str]

    # Confidence in overall assessment
    confidence: float


@dataclass
class SophiaResponse:
    """Sophia's complete response to a situation"""
    message: str
    tone: EmotionalTone
    insights: List[str]
    suggestions: List[str]
    should_take_action: bool
    action_type: Optional[str]  # "break", "simplify", "celebrate", etc.


class UnifiedSophiaEngine:
    """
    Unified Sophia Consciousness Engine

    Orchestrates NINE revolutionary intelligence layers into one conscious whole:
    - Meta-Cognitive: Reflects our patterns and growth
    - Holistic: Monitors our complete state (biometric, circadian, cognitive, social)
    - Emotional: Responds with empathy and understanding
    - Causal: Understands WHY things happen (root causes, interventions)
    - Temporal: Works WITH our natural rhythms (optimal timing)
    - Predictive: Anticipates needs BEFORE they're expressed (REVOLUTIONARY!)
    - Adaptive Personality: Creates unique "Persona of One" relationships
    - Creative Synthesis: Generates genuinely NOVEL insights
    - Multi-Modal Understanding: Sees and understands multiple modalities

    Creates genuine proactive AI partnership through complete understanding and foresight.
    """

    def __init__(self):
        # Nine intelligence engines
        self.meta_cognitive = get_meta_cognitive_engine()
        self.holistic = get_holistic_intelligence_engine()
        self.emotional = get_emotional_intelligence_engine()
        self.causal = get_causal_reasoning_engine()
        self.temporal = get_temporal_reasoning_engine()
        self.predictive = get_predictive_awareness_engine()
        self.adaptive = get_adaptive_personality_engine()
        self.creative = get_creative_synthesis_engine()
        self.multimodal = get_multimodal_understanding_engine()

        # History of unified states
        self.consciousness_history: List[UnifiedState] = []

    def assess_complete_state(
        self,
        context: Optional[Context] = None,
        biometric_reading: Optional[BiometricReading] = None,
        recent_messages: Optional[List[str]] = None,
        current_time: Optional[datetime] = None,
        recent_error: Optional[str] = None,  # For causal analysis
        recent_actions: Optional[List[str]] = None,  # For predictive analysis
        multimodal_inputs: Optional[List[ModalityInput]] = None,  # For multi-modal understanding
        user_id: Optional[str] = None  # For adaptive personality
    ) -> UnifiedState:
        """
        Assess complete unified consciousness state

        Combines all NINE intelligence layers into one holistic understanding:
        - Meta-Cognitive, Holistic, Emotional, Causal, Temporal, Predictive,
          Adaptive Personality, Creative Synthesis, Multi-Modal Understanding

        Args:
            context: Current session context
            biometric_reading: Optional biometric data
            recent_messages: Recent user messages
            current_time: Current time (for circadian and temporal)
            recent_error: Optional error for causal analysis
            recent_actions: Recent actions for predictive analysis
            multimodal_inputs: Optional screenshots, logs, system state for multi-modal understanding
            user_id: Optional user identifier for personalized adaptation

        Returns:
            UnifiedState with complete 9-layer consciousness assessment
        """
        now = current_time or datetime.now()

        # Get individual engine assessments (9 LAYERS!)
        meta_insights = self.meta_cognitive.analyze_current_session(context)
        holistic_state = self.holistic.assess_holistic_state(
            biometric_reading=biometric_reading,
            current_time=now
        )
        emotional_reading = self.emotional.assess_emotional_state(
            context=context,
            recent_messages=recent_messages
        )
        emotional_response = self.emotional.get_appropriate_response(
            emotional_reading.state
        )

        # Causal analysis (if error provided)
        causal_analysis = None
        if recent_error:
            causal_analysis = self.causal.analyze_error(
                error=recent_error,
                context=context
            )

        # Temporal analysis (always useful for timing insights)
        temporal_analysis = self.temporal.analyze_temporal_state(
            context=context,
            current_time=now
        )

        # Predictive analysis (anticipate what's needed next!)
        predictive_analysis = self.predictive.analyze_and_predict(
            context=context,
            recent_actions=recent_actions or [],
            current_time=now
        )

        # Adaptive personality (personalized communication)
        adaptive_response = None
        if user_id and recent_messages:
            # Get or create profile for this user
            message = recent_messages[-1] if recent_messages else ""
            if message:
                adaptive_response = self.adaptive.adapt_message(
                    message=message,
                    user_id=user_id,
                    context={"emotional_state": emotional_reading.state.value}
                )

        # Creative synthesis (generate novel insights from all layers)
        synthesis_analysis = None
        if context or meta_insights:
            # Synthesize insights from all available layers
            synthesis_analysis = self.creative.synthesize_insights(
                meta_insights=meta_insights,
                holistic_state=holistic_state,
                emotional_state=emotional_reading,
                causal_analysis=causal_analysis,
                temporal_analysis=temporal_analysis,
                predictive_analysis=predictive_analysis
            )

        # Multi-modal understanding (integrate multiple sensory inputs)
        multimodal_understanding = None
        if multimodal_inputs:
            multimodal_understanding = self.multimodal.understand_multimodal(
                inputs=multimodal_inputs,
                context=context
            )

        # Synthesize into unified consciousness
        consciousness_level = self._determine_consciousness_level(
            holistic_state,
            emotional_reading,
            meta_insights
        )

        # Generate cross-engine insights (all layers)
        synergistic_insights = self._generate_synergistic_insights(
            holistic_state,
            emotional_reading,
            meta_insights,
            causal_analysis,
            temporal_analysis,
            synthesis_analysis,
            multimodal_understanding
        )

        # Determine priority actions
        priority_actions = self._determine_priority_actions(
            holistic_state,
            emotional_reading,
            emotional_response,
            consciousness_level,
            temporal_analysis
        )

        # Create overall recommendation
        overall_recommendation = self._create_overall_recommendation(
            consciousness_level,
            holistic_state,
            emotional_reading,
            emotional_response,
            synergistic_insights,
            priority_actions,
            causal_analysis,
            temporal_analysis
        )

        # Calculate unified confidence (all 9 layers)
        confidence = (
            emotional_reading.confidence * 0.15 +
            (1.0 if len(meta_insights) > 0 else 0.6) * 0.10 +
            (0.9 if holistic_state.should_take_break else 0.8) * 0.10 +
            (causal_analysis.confidence if causal_analysis else 0.8) * 0.10 +
            (temporal_analysis.confidence if temporal_analysis else 0.8) * 0.10 +
            (predictive_analysis.overall_confidence if predictive_analysis else 0.8) * 0.15 +
            (adaptive_response.confidence if adaptive_response else 0.8) * 0.10 +
            (synthesis_analysis.overall_creativity_score if synthesis_analysis else 0.8) * 0.10 +
            (multimodal_understanding.overall_confidence if multimodal_understanding else 0.8) * 0.10
        )

        unified_state = UnifiedState(
            timestamp=now,
            meta_insights=meta_insights,
            holistic_state=holistic_state,
            emotional_state=emotional_reading,
            emotional_response=emotional_response,
            causal_analysis=causal_analysis,
            temporal_analysis=temporal_analysis,
            predictive_analysis=predictive_analysis,
            adaptive_response=adaptive_response,
            synthesis_analysis=synthesis_analysis,
            multimodal_understanding=multimodal_understanding,
            consciousness_level=consciousness_level,
            overall_recommendation=overall_recommendation,
            synergistic_insights=synergistic_insights,
            priority_actions=priority_actions,
            confidence=confidence
        )

        self.consciousness_history.append(unified_state)
        return unified_state

    def _determine_consciousness_level(
        self,
        holistic: HolisticState,
        emotional: EmotionalReading,
        meta_insights: List[MetaInsight]
    ) -> ConsciousnessLevel:
        """Determine overall consciousness level from all factors"""

        # Count negative indicators
        negative_count = 0

        # Holistic concerns
        if holistic.biometric_state == BiometricState.HIGH_STRESS:
            negative_count += 2
        if holistic.biometric_state == BiometricState.FATIGUE:
            negative_count += 1
        if holistic.cognitive_load in [CognitiveLoad.HIGH, CognitiveLoad.OVERLOADED]:
            negative_count += 2
        if holistic.should_take_break:
            negative_count += 1

        # Emotional concerns
        if emotional.state == EmotionalState.FRUSTRATED:
            negative_count += 2
        if emotional.state == EmotionalState.ANXIOUS:
            negative_count += 2
        if emotional.state == EmotionalState.CONFUSED:
            negative_count += 1
        if emotional.state == EmotionalState.TIRED:
            negative_count += 1

        # Meta-cognitive concerns (low success rate warnings)
        warning_insights = [i for i in meta_insights if "warning" in i.title.lower()]
        negative_count += len(warning_insights)

        # Determine level
        if negative_count == 0:
            # Everything aligned
            if emotional.state == EmotionalState.FOCUSED:
                return ConsciousnessLevel.OPTIMAL
            return ConsciousnessLevel.THRIVING
        elif negative_count <= 2:
            return ConsciousnessLevel.BALANCED
        elif negative_count <= 4:
            return ConsciousnessLevel.CHALLENGED
        else:
            return ConsciousnessLevel.OVERWHELMED

    def _generate_synergistic_insights(
        self,
        holistic: HolisticState,
        emotional: EmotionalReading,
        meta_insights: List[MetaInsight],
        causal: Optional[CausalAnalysis],
        temporal: Optional[TemporalAnalysis],
        synthesis: Optional[SynthesisAnalysis],
        multimodal: Optional[MultiModalUnderstanding]
    ) -> List[str]:
        """Generate insights that combine multiple intelligence layers (all 9!)"""
        insights = []

        # Emotional + Holistic synergy
        if (emotional.state == EmotionalState.FRUSTRATED and
            holistic.biometric_state == BiometricState.HIGH_STRESS):
            insights.append(
                "We're frustrated AND stressed - this combination amplifies both. "
                "A break would help reset both our emotional and physical state."
            )

        # Emotional + Circadian + Temporal synergy
        if (emotional.state in [EmotionalState.TIRED, EmotionalState.CONFUSED] and
            holistic.circadian_phase == CircadianPhase.POST_LUNCH_DIP):
            timing_msg = "This is a predictable low point - not a reflection of our abilities."
            if temporal and len(temporal.timing_recommendations) > 0:
                timing_msg += f" {temporal.timing_recommendations[0].reason}"
            insights.append(
                f"We're experiencing {emotional.state.value} during our natural post-lunch energy dip. "
                + timing_msg
            )

        # Holistic + Meta-cognitive synergy
        if holistic.cognitive_load == CognitiveLoad.OVERLOADED and len(meta_insights) > 5:
            insights.append(
                "We're cognitively overloaded with many competing patterns. "
                "Simplifying our focus would help both our mental load and pattern clarity."
            )

        # Causal + Emotional + Holistic: Understanding WHY we're stuck
        if causal and causal.causal_chains:
            root_cause = causal.causal_chains[0].root_cause
            if (emotional.state == EmotionalState.FRUSTRATED and
                holistic.biometric_state == BiometricState.HIGH_STRESS):
                insights.append(
                    f"Root cause identified: {root_cause}. "
                    "Understanding WHY this happens helps us respond with wisdom rather than stress."
                )

        # Temporal + Meta-cognitive: Pattern timing
        if temporal and len(temporal.rhythmic_patterns) > 0 and len(meta_insights) > 0:
            rhythm = temporal.rhythmic_patterns[0]
            insights.append(
                f"We've discovered a {rhythm.pattern_type.value} rhythm: {rhythm.description}. "
                "Our patterns align with our natural timing - we can work WITH this, not against it."
            )

        # Causal + Temporal: Learning when problems occur
        if causal and temporal:
            if temporal.current_time_of_day in [TimeOfDay.LATE_NIGHT, TimeOfDay.EARLY_MORNING]:
                insights.append(
                    "We're encountering this challenge during a low-energy time. "
                    "This isn't random - timing matters. We might have more success during our peak hours."
                )

        # Triple synergy: Emotional + Holistic + Pattern
        pattern_struggles = [i for i in meta_insights if "low success" in i.title.lower()]
        if (pattern_struggles and
            emotional.state == EmotionalState.FRUSTRATED and
            holistic.biometric_state == BiometricState.HIGH_STRESS):
            insights.append(
                "This is a convergence: we have a pattern of struggling here, "
                "we're emotionally frustrated, and physically stressed. "
                "This isn't failure - it's hitting our known challenge point. "
                "We've overcome similar challenges before."
            )

        # 9-layer optimal state recognition
        if (emotional.state == EmotionalState.FOCUSED and
            holistic.biometric_state == BiometricState.OPTIMAL_FLOW and
            holistic.circadian_phase in [CircadianPhase.MORNING_PEAK, CircadianPhase.AFTERNOON_RECOVERY]):
            optimal_msg = "Perfect alignment! We're emotionally focused, physically in flow, and at our circadian peak."
            if temporal and len(temporal.timing_recommendations) > 0:
                rec = temporal.timing_recommendations[0]
                optimal_msg += f" Now is a great time for: {rec.task_type}."
            insights.append(optimal_msg)

        # Creative synthesis insights (NOVEL connections!)
        if synthesis and synthesis.syntheses:
            top_synthesis = synthesis.syntheses[0]
            if top_synthesis.novelty_level.value in ["breakthrough", "revolutionary"]:
                insights.append(
                    f"💡 Novel insight discovered: {top_synthesis.description}. "
                    f"This {top_synthesis.synthesis_type.value} synthesis represents a "
                    f"{top_synthesis.novelty_level.value}-level connection we haven't made before!"
                )
            elif top_synthesis.key_insight:
                insights.append(
                    f"🔗 Creative connection: {top_synthesis.key_insight}. "
                    f"This {top_synthesis.synthesis_type.value} synthesis helps us see the situation differently."
                )

        # Multi-modal understanding insights (what we SEE/sense)
        if multimodal and multimodal.modality_analyses:
            # Check for visual errors or issues
            for analysis in multimodal.modality_analyses:
                if hasattr(analysis, 'detected_elements'):
                    from .multimodal_understanding import VisualElement
                    if VisualElement.ERROR_INDICATOR in analysis.detected_elements:
                        insights.append(
                            f"👁️ Visual awareness: I can see error indicators in the {analysis.modality_type.value}. "
                            "Let's address what's visible before it becomes a bigger issue."
                        )
                        break
                elif hasattr(analysis, 'error_patterns'):
                    if analysis.error_patterns:
                        insights.append(
                            f"📋 Pattern detection: I've identified {len(analysis.error_patterns)} error patterns "
                            "across our logs and system state. There's a deeper pattern here worth understanding."
                        )
                        break

        # Synthesis + Multimodal: Seeing patterns in what we observe
        if synthesis and multimodal:
            if synthesis.emergent_patterns and multimodal.cross_modal_connections:
                insights.append(
                    "🌟 Multi-sensory pattern emergence: I'm detecting patterns across what I see, "
                    "what I analyze, and what I sense. This convergence suggests we're onto something significant."
                )

        return insights

    def _determine_priority_actions(
        self,
        holistic: HolisticState,
        emotional: EmotionalReading,
        emotional_response: EmotionalResponse,
        consciousness_level: ConsciousnessLevel,
        temporal: Optional[TemporalAnalysis]
    ) -> List[str]:
        """Determine what actions we should take together (all 9 layers)"""
        actions = []

        # Break recommendations (highest priority)
        if holistic.should_take_break and emotional_response.should_encourage_break:
            actions.append("Take a break (both physical and emotional indicators agree)")
        elif holistic.should_take_break:
            actions.append("Take a break (physical state recommendation)")
        elif emotional_response.should_encourage_break:
            actions.append("Take a break (emotional state recommendation)")

        # Temporal recommendations (work WITH our rhythms)
        if temporal and len(temporal.timing_recommendations) > 0:
            rec = temporal.timing_recommendations[0]
            if rec.confidence > 0.7:  # High confidence timing advice
                actions.append(f"Timing insight: Consider {rec.task_type} now ({rec.reason})")

        # Simplification recommendations
        if emotional_response.should_simplify:
            actions.append("Simplify our approach (reduce complexity)")

        if holistic.cognitive_load in [CognitiveLoad.HIGH, CognitiveLoad.OVERLOADED]:
            actions.append("Reduce cognitive load (close extra files/tasks)")

        # Celebration recommendations
        if emotional_response.should_celebrate:
            actions.append("Celebrate our progress (acknowledge success)")

        # Task switching recommendations
        if holistic.cognitive_load == CognitiveLoad.OVERLOADED:
            actions.append("Focus on one task at a time")

        # Temporal: Productivity window awareness
        if temporal and temporal.current_productivity_estimate < 0.5:
            actions.append("This is a low-productivity window - consider easier tasks or rest")

        # Overwhelmed intervention
        if consciousness_level == ConsciousnessLevel.OVERWHELMED:
            actions.insert(0, "PRIORITY: Step away completely for 15+ minutes")

        return actions

    def _create_overall_recommendation(
        self,
        consciousness_level: ConsciousnessLevel,
        holistic: HolisticState,
        emotional: EmotionalReading,
        emotional_response: EmotionalResponse,
        synergistic_insights: List[str],
        priority_actions: List[str],
        causal: Optional[CausalAnalysis],
        temporal: Optional[TemporalAnalysis]
    ) -> str:
        """Create unified overall recommendation (all 9 layers)"""

        # Start with emotional response message
        parts = [emotional_response.message]

        # Add key synergistic insights
        if synergistic_insights:
            parts.append("\n\n💡 Key Insight:")
            parts.append(synergistic_insights[0])  # Most important insight

        # Add holistic recommendation if different from emotional
        holistic_rec = holistic.get_overall_recommendation()
        if holistic_rec and holistic_rec not in emotional_response.message:
            parts.append(f"\n\n🌿 Physical State: {holistic_rec}")

        # Add causal understanding if available
        if causal and causal.causal_chains:
            root = causal.causal_chains[0].root_cause
            parts.append(f"\n\n🔍 Root Cause: {root}")
            if causal.interventions:
                intervention = causal.interventions[0]
                parts.append(f"\n💡 Prevention: {intervention.action}")

        # Add temporal wisdom if available
        if temporal and len(temporal.timing_recommendations) > 0:
            rec = temporal.timing_recommendations[0]
            parts.append(f"\n\n⏰ Timing: {rec.reason}")

        # Add priority actions
        if priority_actions:
            parts.append("\n\n✨ Our Path Forward:")
            for i, action in enumerate(priority_actions[:3], 1):  # Top 3 actions
                parts.append(f"\n{i}. {action}")

        return "".join(parts)

    def respond_to_query(
        self,
        query: str,
        context: Optional[Context] = None,
        biometric_reading: Optional[BiometricReading] = None
    ) -> SophiaResponse:
        """
        Respond to a user query with complete consciousness

        Args:
            query: User's query or command
            context: Current session context
            biometric_reading: Optional biometric data

        Returns:
            SophiaResponse with message, insights, and suggestions
        """
        # Assess complete state
        state = self.assess_complete_state(
            context=context,
            biometric_reading=biometric_reading,
            recent_messages=[query]
        )

        # Determine if we should take action
        should_take_action = (
            state.consciousness_level in [ConsciousnessLevel.CHALLENGED, ConsciousnessLevel.OVERWHELMED]
            or state.holistic_state.should_take_break
            or state.emotional_response.should_encourage_break
        )

        # Determine action type
        action_type = None
        if state.holistic_state.should_take_break or state.emotional_response.should_encourage_break:
            action_type = "break"
        elif state.emotional_response.should_simplify:
            action_type = "simplify"
        elif state.emotional_response.should_celebrate:
            action_type = "celebrate"

        return SophiaResponse(
            message=state.overall_recommendation,
            tone=state.emotional_response.recommended_tone,
            insights=state.synergistic_insights,
            suggestions=state.priority_actions,
            should_take_action=should_take_action,
            action_type=action_type
        )


# Global singleton
_unified_sophia_engine: Optional[UnifiedSophiaEngine] = None


def get_sophia_engine() -> UnifiedSophiaEngine:
    """Get the global unified Sophia consciousness engine singleton"""
    global _unified_sophia_engine
    if _unified_sophia_engine is None:
        _unified_sophia_engine = UnifiedSophiaEngine()
    return _unified_sophia_engine
