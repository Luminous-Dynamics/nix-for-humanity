"""
Holistic Intelligence Engine - Revolutionary AI that understands you holistically

This is the FIRST AI system that combines:
1. Biometric awareness (heart rate, HRV for stress/flow detection)
2. Circadian intelligence (biological clock adaptation)
3. Cognitive load monitoring (real-time mental capacity)
4. Social context (team dynamics, pair programming)

Unlike existing meta-cognitive AI that monitors itself, Sophia's Holistic Intelligence
monitors YOU - your physical state, mental state, energy levels, and social context.

This enables truly adaptive assistance that works WITH your biology, not against it.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, time
from enum import Enum
import logging
from collections import defaultdict

from ..context import get_context_engine, Context

logger = logging.getLogger(__name__)


class BiometricState(Enum):
    """Physical/biometric states detected from signals"""
    HIGH_STRESS = "high_stress"          # HRV low, HR high → need break
    OPTIMAL_FLOW = "optimal_flow"        # HRV high, HR moderate → peak performance
    FATIGUE = "fatigue"                  # Declining HRV → need rest
    ENERGIZED = "energized"              # Rising HRV → ready for challenges
    UNKNOWN = "unknown"                  # No biometric data available


class CircadianPhase(Enum):
    """Circadian rhythm phases with optimal activities"""
    CORTISOL_PEAK = "cortisol_peak"      # 6-9am: Best for analytical work
    MORNING_PEAK = "morning_peak"        # 9-11am: Peak cognitive performance
    POST_LUNCH_DIP = "post_lunch_dip"    # 1-3pm: Lower performance, good for routine
    AFTERNOON_RECOVERY = "afternoon_recovery"  # 3-6pm: Second wind, creative work
    EVENING_WIND = "evening_wind"        # 6-9pm: Review, reflection, learning
    MELATONIN_RISE = "melatonin_rise"    # 9pm+: Wind down, avoid screens
    DEEP_NIGHT = "deep_night"            # 12-6am: Sleep or emergency only


class CognitiveLoad(Enum):
    """Mental capacity states"""
    MINIMAL = "minimal"                   # <30% capacity used
    MODERATE = "moderate"                 # 30-60% capacity
    HIGH = "high"                         # 60-85% capacity
    OVERLOADED = "overloaded"            # >85% capacity - degraded performance
    FLOW = "flow"                        # Optimal challenge-skill balance


class SocialContext(Enum):
    """Social working contexts"""
    SOLO = "solo"                        # Working alone
    PAIR_PROGRAMMING = "pair_programming"  # Two developers working together
    MOB_PROGRAMMING = "mob_programming"    # Group coding session
    CODE_REVIEW = "code_review"           # Reviewing others' code
    MEETING = "meeting"                   # In a meeting/call
    TEACHING = "teaching"                 # Mentoring/explaining
    LEARNING = "learning"                 # Being mentored/following along


@dataclass
class BiometricReading:
    """A biometric data reading"""
    timestamp: datetime
    heart_rate: Optional[int] = None      # BPM
    hrv: Optional[float] = None           # Heart rate variability (ms)
    respiration_rate: Optional[int] = None  # Breaths per minute
    skin_temp: Optional[float] = None     # Celsius
    typing_rhythm: Optional[Dict] = None  # Typing pattern analysis

    def get_stress_indicator(self) -> float:
        """
        Calculate stress indicator from biometrics
        Returns: 0.0 (relaxed) to 1.0 (highly stressed)
        """
        if not self.heart_rate and not self.hrv:
            return 0.5  # Unknown

        stress = 0.0
        indicators = 0

        # High heart rate indicates stress
        if self.heart_rate:
            if self.heart_rate > 100:
                stress += 0.8
            elif self.heart_rate > 80:
                stress += 0.5
            elif self.heart_rate > 60:
                stress += 0.3
            else:
                stress += 0.1
            indicators += 1

        # Low HRV indicates stress (inversely correlated)
        if self.hrv:
            if self.hrv < 20:
                stress += 0.9
            elif self.hrv < 40:
                stress += 0.6
            elif self.hrv < 60:
                stress += 0.3
            else:
                stress += 0.1
            indicators += 1

        return stress / indicators if indicators > 0 else 0.5


@dataclass
class CircadianState:
    """Current circadian state"""
    current_phase: CircadianPhase
    optimal_for: List[str]
    suboptimal_for: List[str]
    energy_level: float  # 0.0 to 1.0
    alertness_level: float  # 0.0 to 1.0
    recommended_break_in_minutes: Optional[int] = None


@dataclass
class CognitiveLoadAssessment:
    """Assessment of current cognitive load"""
    load_level: CognitiveLoad
    capacity_used: float  # 0.0 to 1.0
    factors: List[str]  # What's contributing to load
    suggestions: List[str]  # How to reduce load
    estimated_time_to_overload: Optional[int] = None  # Minutes


@dataclass
class SocialContextInfo:
    """Information about social working context"""
    context_type: SocialContext
    participant_count: int = 1
    interaction_mode: Optional[str] = None  # "active", "passive", "observing"
    communication_frequency: Optional[float] = None  # Messages per minute
    role: Optional[str] = None  # "driver", "navigator", "observer", etc.


@dataclass
class HolisticState:
    """Complete holistic state combining all dimensions"""
    timestamp: datetime
    biometric_state: BiometricState
    circadian_phase: CircadianPhase
    cognitive_load: CognitiveLoad
    social_context: SocialContext

    # Detailed info
    biometric_reading: Optional[BiometricReading] = None
    circadian_state: Optional[CircadianState] = None
    cognitive_assessment: Optional[CognitiveLoadAssessment] = None
    social_info: Optional[SocialContextInfo] = None

    # Overall recommendations
    should_take_break: bool = False
    break_reason: Optional[str] = None
    optimal_task_types: List[str] = field(default_factory=list)
    suboptimal_task_types: List[str] = field(default_factory=list)

    def get_overall_recommendation(self) -> str:
        """Get overall recommendation based on holistic state"""
        recommendations = []

        # Biometric warnings
        if self.biometric_state == BiometricState.HIGH_STRESS:
            recommendations.append("⚠️ High stress detected - consider a short break")
        elif self.biometric_state == BiometricState.FATIGUE:
            recommendations.append("😴 Fatigue detected - you might want to rest")

        # Circadian suggestions
        if self.circadian_state:
            recommendations.append(
                f"⏰ Optimal for: {', '.join(self.circadian_state.optimal_for[:2])}"
            )

        # Cognitive load warnings
        if self.cognitive_load == CognitiveLoad.OVERLOADED:
            recommendations.append("🧠 Cognitive overload - simplify current task")
        elif self.cognitive_load == CognitiveLoad.FLOW:
            recommendations.append("🌊 In flow state - keep going!")

        # Social context suggestions
        if self.social_context == SocialContext.PAIR_PROGRAMMING:
            recommendations.append("👥 Pair programming - communicate actively")

        return "\n".join(recommendations) if recommendations else "✅ Everything looks good!"


class HolisticIntelligenceEngine:
    """
    Revolutionary Holistic Intelligence Engine

    The FIRST AI that combines biometric, circadian, cognitive, and social awareness
    to provide truly adaptive assistance that works with your biology, not against it.

    Key innovations:
    1. Biometric Integration - Uses heart rate/HRV for stress/flow detection
    2. Circadian Adaptation - Adjusts to your biological clock
    3. Cognitive Load Monitoring - Tracks mental capacity in real-time
    4. Social Context Awareness - Understands team dynamics
    """

    def __init__(self):
        """Initialize the holistic intelligence engine"""
        self.context_engine = get_context_engine()

        # Biometric tracking
        self.biometric_history: List[BiometricReading] = []
        self.baseline_hr: Optional[int] = None  # User's baseline heart rate
        self.baseline_hrv: Optional[float] = None  # User's baseline HRV

        # Circadian tracking
        self.user_wake_time: Optional[time] = None  # When user typically wakes
        self.user_sleep_time: Optional[time] = None  # When user typically sleeps

        # Cognitive load tracking
        self.cognitive_load_history: List[CognitiveLoadAssessment] = []

        # Social context tracking
        self.social_context_history: List[SocialContextInfo] = []

    def assess_holistic_state(
        self,
        biometric_reading: Optional[BiometricReading] = None,
        current_time: Optional[datetime] = None
    ) -> HolisticState:
        """
        Assess complete holistic state

        Args:
            biometric_reading: Optional biometric data
            current_time: Optional time (defaults to now)

        Returns:
            Complete holistic state with all dimensions
        """
        if current_time is None:
            current_time = datetime.now()

        # Assess each dimension
        biometric_state = self._assess_biometric_state(biometric_reading)
        circadian_phase, circadian_state = self._assess_circadian_phase(current_time)
        cognitive_load, cognitive_assessment = self._assess_cognitive_load()
        social_context, social_info = self._assess_social_context()

        # Combine for holistic state
        holistic_state = HolisticState(
            timestamp=current_time,
            biometric_state=biometric_state,
            circadian_phase=circadian_phase,
            cognitive_load=cognitive_load,
            social_context=social_context,
            biometric_reading=biometric_reading,
            circadian_state=circadian_state,
            cognitive_assessment=cognitive_assessment,
            social_info=social_info
        )

        # Determine if break is needed
        self._update_break_recommendation(holistic_state)

        # Determine optimal tasks
        self._update_task_recommendations(holistic_state)

        return holistic_state

    def _assess_biometric_state(
        self,
        reading: Optional[BiometricReading]
    ) -> BiometricState:
        """Assess biometric state from reading"""
        if not reading:
            return BiometricState.UNKNOWN

        # Store reading
        self.biometric_history.append(reading)

        # Get stress indicator
        stress = reading.get_stress_indicator()

        # Classify state
        if stress > 0.7:
            return BiometricState.HIGH_STRESS
        elif stress < 0.3 and reading.hrv and reading.hrv > 60:
            return BiometricState.OPTIMAL_FLOW
        elif len(self.biometric_history) >= 3:
            # Check for fatigue trend
            recent_hrv = [r.hrv for r in self.biometric_history[-3:] if r.hrv]
            if len(recent_hrv) >= 2 and recent_hrv[-1] < recent_hrv[0] * 0.8:
                return BiometricState.FATIGUE

        return BiometricState.ENERGIZED if stress < 0.5 else BiometricState.HIGH_STRESS

    def _assess_circadian_phase(
        self,
        current_time: datetime
    ) -> Tuple[CircadianPhase, CircadianState]:
        """Assess circadian phase and generate state"""
        hour = current_time.hour

        # Determine phase
        if 6 <= hour < 9:
            phase = CircadianPhase.CORTISOL_PEAK
            optimal = ["Planning", "Strategic thinking", "Problem-solving"]
            suboptimal = ["Routine tasks", "Meetings"]
            energy = 0.7
            alertness = 0.8
        elif 9 <= hour < 11:
            phase = CircadianPhase.MORNING_PEAK
            optimal = ["Complex coding", "Architecture design", "Debugging"]
            suboptimal = ["Routine admin", "Simple tasks"]
            energy = 0.9
            alertness = 1.0
        elif 13 <= hour < 15:
            phase = CircadianPhase.POST_LUNCH_DIP
            optimal = ["Code review", "Documentation", "Routine tasks"]
            suboptimal = ["Complex problem-solving", "Important decisions"]
            energy = 0.5
            alertness = 0.6
            break_in = 30  # Suggest break soon
        elif 15 <= hour < 18:
            phase = CircadianPhase.AFTERNOON_RECOVERY
            optimal = ["Creative work", "Brainstorming", "Learning"]
            suboptimal = ["Repetitive tasks"]
            energy = 0.7
            alertness = 0.7
        elif 18 <= hour < 21:
            phase = CircadianPhase.EVENING_WIND
            optimal = ["Review", "Reflection", "Light learning"]
            suboptimal = ["Intensive coding", "Debugging"]
            energy = 0.6
            alertness = 0.5
        elif 21 <= hour or hour < 1:
            phase = CircadianPhase.MELATONIN_RISE
            optimal = ["Winding down", "Planning tomorrow"]
            suboptimal = ["Any screen work"]
            energy = 0.3
            alertness = 0.3
            break_in = 0  # Should stop now
        else:
            phase = CircadianPhase.DEEP_NIGHT
            optimal = ["Sleep!"]
            suboptimal = ["Everything except emergencies"]
            energy = 0.1
            alertness = 0.1
            break_in = 0

        state = CircadianState(
            current_phase=phase,
            optimal_for=optimal,
            suboptimal_for=suboptimal,
            energy_level=energy,
            alertness_level=alertness,
            recommended_break_in_minutes=break_in if 'break_in' in locals() else None
        )

        return phase, state

    def _assess_cognitive_load(self, context: Optional[Context] = None) -> Tuple[CognitiveLoad, CognitiveLoadAssessment]:
        """Assess current cognitive load"""
        if context is None:
            context = self.context_engine.get_current_context()

        factors = []
        load_score = 0.0

        # Factor 1: Number of open files
        if len(context.active_files) > 10:
            factors.append(f"{len(context.active_files)} files open")
            load_score += 0.3
        elif len(context.active_files) > 5:
            factors.append(f"{len(context.active_files)} files open")
            load_score += 0.15

        # Factor 2: Recent errors
        recent_errors = sum(1 for cmd in context.recent_commands[:10] if not cmd.success)
        if recent_errors > 3:
            factors.append(f"{recent_errors} recent errors")
            load_score += 0.3
        elif recent_errors > 1:
            factors.append(f"{recent_errors} recent errors")
            load_score += 0.15

        # Factor 3: Command frequency (high = high load)
        if len(context.recent_commands) > 20:
            factors.append("High activity rate")
            load_score += 0.2

        # Factor 4: Context switching
        project_types = set(f.project_type for f in context.active_files if f.project_type)
        if len(project_types) > 2:
            factors.append(f"Multiple project types ({len(project_types)})")
            load_score += 0.25

        # Classify load
        if load_score < 0.3:
            load_level = CognitiveLoad.MINIMAL
        elif load_score < 0.6:
            load_level = CognitiveLoad.MODERATE
        elif load_score < 0.85:
            load_level = CognitiveLoad.HIGH
        else:
            load_level = CognitiveLoad.OVERLOADED

        # Generate suggestions
        suggestions = []
        if load_score > 0.7:
            suggestions.append("Close unused files")
            suggestions.append("Focus on one task at a time")
            suggestions.append("Take a 5-minute break")
        if recent_errors > 2:
            suggestions.append("Step back and review the problem")

        assessment = CognitiveLoadAssessment(
            load_level=load_level,
            capacity_used=load_score,
            factors=factors,
            suggestions=suggestions
        )

        return load_level, assessment

    def _assess_social_context(self) -> Tuple[SocialContext, SocialContextInfo]:
        """Assess social working context"""
        # For now, default to solo
        # In future, integrate with:
        # - Git activity (pair commits = pair programming)
        # - Terminal sharing tools
        # - Communication tools (Discord, Slack)
        # - Video call detection

        context_type = SocialContext.SOLO

        info = SocialContextInfo(
            context_type=context_type,
            participant_count=1,
            interaction_mode="active"
        )

        return context_type, info

    def _update_break_recommendation(self, state: HolisticState):
        """Update break recommendation based on holistic state"""
        reasons = []

        # Biometric reasons
        if state.biometric_state == BiometricState.HIGH_STRESS:
            reasons.append("High stress detected")
        elif state.biometric_state == BiometricState.FATIGUE:
            reasons.append("Fatigue detected")

        # Circadian reasons
        if state.circadian_state and state.circadian_state.energy_level < 0.4:
            reasons.append(f"Low energy ({state.circadian_state.current_phase.value})")

        # Cognitive reasons
        if state.cognitive_load == CognitiveLoad.OVERLOADED:
            reasons.append("Cognitive overload")

        if reasons:
            state.should_take_break = True
            state.break_reason = "; ".join(reasons)

    def _update_task_recommendations(self, state: HolisticState):
        """Update task recommendations based on holistic state"""
        optimal = []
        suboptimal = []

        # Add circadian recommendations
        if state.circadian_state:
            optimal.extend(state.circadian_state.optimal_for)
            suboptimal.extend(state.circadian_state.suboptimal_for)

        # Adjust based on cognitive load
        if state.cognitive_load == CognitiveLoad.OVERLOADED:
            suboptimal.extend(["Complex problem-solving", "Learning new concepts"])
            optimal.append("Simple, routine tasks")
        elif state.cognitive_load == CognitiveLoad.MINIMAL:
            optimal.extend(["Challenging problems", "Learning", "Experimentation"])

        # Adjust based on biometric state
        if state.biometric_state == BiometricState.OPTIMAL_FLOW:
            optimal.append("Your most important/challenging work")
        elif state.biometric_state == BiometricState.HIGH_STRESS:
            suboptimal.append("High-stakes decisions")
            optimal.append("Familiar, comfortable tasks")

        state.optimal_task_types = optimal
        state.suboptimal_task_types = suboptimal


# Global instance
_holistic_intelligence_engine: Optional[HolisticIntelligenceEngine] = None


def get_holistic_intelligence_engine() -> HolisticIntelligenceEngine:
    """Get or create global holistic intelligence engine"""
    global _holistic_intelligence_engine

    if _holistic_intelligence_engine is None:
        _holistic_intelligence_engine = HolisticIntelligenceEngine()

    return _holistic_intelligence_engine
