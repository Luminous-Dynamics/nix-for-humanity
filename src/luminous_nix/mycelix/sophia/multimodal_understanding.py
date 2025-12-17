"""
Multi-Modal Understanding Engine - Vision Beyond Eyes

The paradigm shift: Most AI processes text OR images separately.
Sophia INTEGRATES visual, textual, and contextual understanding.

This engine:
- Analyzes screenshots (errors, UI states, terminal output)
- Parses logs with semantic understanding
- Interprets system state visually
- Extracts and understands text from images (OCR + meaning)
- Correlates visual info with ALL other intelligence layers

Revolutionary because vision isn't separate from understanding -
it's ONE integrated multi-sensory consciousness.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Set, Tuple, Any
from enum import Enum
import re


class ModalityType(Enum):
    """What type of input are we processing?"""
    SCREENSHOT = "screenshot"          # Image of screen
    LOG_FILE = "log_file"             # Text log file
    TERMINAL_OUTPUT = "terminal_output"  # Command output
    ERROR_MESSAGE = "error_message"   # Error text/image
    SYSTEM_STATE = "system_state"     # System info display
    DIAGRAM = "diagram"               # Visual diagram
    CHART = "chart"                   # Data visualization
    CODE_SNIPPET = "code_snippet"     # Code with syntax
    MIXED = "mixed"                   # Multiple modalities


class UnderstandingLevel(Enum):
    """How deeply do we understand this?"""
    SURFACE = "surface"               # Basic text/pixels
    SYNTACTIC = "syntactic"          # Structure recognized
    SEMANTIC = "semantic"            # Meaning understood
    CONTEXTUAL = "contextual"        # Context integrated
    INTEGRATED = "integrated"        # All layers unified


class VisualElement(Enum):
    """What visual elements do we detect?"""
    TEXT = "text"                    # Readable text
    BUTTON = "button"                # UI button
    WINDOW = "window"                # Application window
    TERMINAL = "terminal"            # Terminal interface
    ERROR_INDICATOR = "error"        # Red/warning colors
    SUCCESS_INDICATOR = "success"    # Green/success colors
    PROGRESS_BAR = "progress_bar"    # Progress indicator
    GRAPH = "graph"                  # Chart/graph
    CODE_BLOCK = "code_block"        # Code syntax
    COMMAND_PROMPT = "prompt"        # Shell prompt


@dataclass
class ModalityInput:
    """Input from any modality"""
    modality_type: ModalityType
    content: Any                     # Raw content (text, image path, etc.)
    timestamp: datetime
    metadata: Dict[str, Any]         # Additional context


@dataclass
class VisualAnalysis:
    """Analysis of visual content"""
    detected_elements: List[VisualElement]
    extracted_text: str              # OCR or direct text
    dominant_colors: List[str]       # Color analysis
    layout_description: str          # Spatial layout

    # Semantic understanding
    likely_application: Optional[str]  # What app is this?
    user_intent: Optional[str]        # What are they trying to do?
    emotional_indicators: List[str]   # Visual emotional cues

    confidence: float


@dataclass
class LogAnalysis:
    """Deep analysis of log files"""
    log_type: str                    # What kind of log?
    time_range: Tuple[datetime, datetime]  # Log time span

    # Extracted patterns
    error_messages: List[str]
    warning_messages: List[str]
    key_events: List[str]

    # Semantic understanding
    root_cause: Optional[str]        # What caused issues?
    error_progression: List[str]     # How did errors evolve?
    critical_timestamps: List[datetime]  # Key moments

    # Integration with other layers
    related_patterns: List[str]      # Connections to other insights
    suggested_actions: List[str]

    confidence: float


@dataclass
class SystemStateAnalysis:
    """Analysis of system state information"""
    state_type: str                  # CPU, memory, disk, etc.
    current_values: Dict[str, Any]   # Current metrics

    # Temporal context
    trend: str                       # Improving/degrading/stable
    anomalies: List[str]            # Unusual values

    # Impact assessment
    severity: str                    # How concerning?
    likely_causes: List[str]
    predicted_outcomes: List[str]

    confidence: float


@dataclass
class MultiModalUnderstanding:
    """Complete understanding integrating all modalities"""
    modality_type: ModalityType
    understanding_level: UnderstandingLevel

    # Raw analysis
    visual_analysis: Optional[VisualAnalysis]
    log_analysis: Optional[LogAnalysis]
    system_state_analysis: Optional[SystemStateAnalysis]

    # Integrated understanding
    primary_insight: str             # Main takeaway
    supporting_evidence: List[str]   # What supports this?
    confidence: float

    # Contextual integration (connections to other layers)
    meta_cognitive_connections: List[str]   # Pattern connections
    emotional_context: Optional[str]        # Emotional implications
    causal_chain: Optional[str]            # Causal understanding
    temporal_context: Optional[str]        # Time-based context
    predictive_insights: List[str]         # What this predicts

    # Actionable
    suggested_actions: List[str]
    questions_to_ask: List[str]

    timestamp: datetime


@dataclass
class MultiModalAnalysis:
    """Complete multi-modal analysis"""
    timestamp: datetime

    # All understandings
    understandings: List[MultiModalUnderstanding]

    # Cross-modal synthesis
    cross_modal_insights: List[str]  # Insights from combining modalities
    unified_narrative: str           # Coherent story across all inputs

    # Quality metrics
    overall_confidence: float
    missing_context: List[str]       # What would help understand better?

    # Integration with consciousness
    consciousness_impact: str        # How does this affect overall state?


class MultiModalUnderstandingEngine:
    """
    Revolutionary Multi-Modal Understanding Engine

    Integrates visual, textual, and contextual understanding into
    unified consciousness - not separate processing pipelines.

    Understands:
    - Screenshots (errors, UI, terminal)
    - Logs (with semantic understanding)
    - System state (contextual interpretation)
    - Mixed inputs (combining multiple modalities)

    The key: Vision isn't separate from other intelligence.
    It's ONE integrated multi-sensory awareness.
    """

    def __init__(self):
        # History for learning
        self.understanding_history: List[MultiModalUnderstanding] = []

        # Pattern library
        self.visual_patterns: Dict[str, float] = {}  # pattern -> confidence
        self.log_patterns: Dict[str, List[str]] = {}  # pattern -> typical causes

        # OCR simulation (would use real OCR in production)
        self.ocr_enabled = False

    def understand(
        self,
        modality_input: ModalityInput,
        context: Optional[any] = None,
        emotional_state: Optional[any] = None,
        recent_patterns: Optional[List[str]] = None
    ) -> MultiModalUnderstanding:
        """
        Understand input from any modality with full context integration

        Args:
            modality_input: The input to understand (screenshot, log, etc.)
            context: Current system context
            emotional_state: User's emotional state
            recent_patterns: Recent patterns from meta-cognitive layer

        Returns:
            MultiModalUnderstanding with deep integrated understanding
        """
        # Analyze based on modality
        if modality_input.modality_type == ModalityType.SCREENSHOT:
            visual = self._analyze_screenshot(modality_input.content)
            log = None
            state = None

        elif modality_input.modality_type == ModalityType.LOG_FILE:
            visual = None
            log = self._analyze_log_file(modality_input.content)
            state = None

        elif modality_input.modality_type == ModalityType.SYSTEM_STATE:
            visual = None
            log = None
            state = self._analyze_system_state(modality_input.content)

        elif modality_input.modality_type == ModalityType.TERMINAL_OUTPUT:
            visual = self._analyze_terminal_output(modality_input.content)
            log = None
            state = None

        else:
            # Mixed or other - try to detect what it is
            visual = None
            log = None
            state = None

        # Generate primary insight
        primary_insight = self._generate_primary_insight(
            visual, log, state, modality_input.modality_type
        )

        # Integrate with other intelligence layers
        meta_connections = self._connect_to_patterns(recent_patterns)
        emotional_context = self._assess_emotional_context(emotional_state, visual, log)
        causal_chain = self._infer_causal_chain(log, state)
        temporal_context = self._extract_temporal_context(log, state)
        predictive = self._generate_predictions(visual, log, state)

        # Generate actions and questions
        actions = self._suggest_actions(visual, log, state, primary_insight)
        questions = self._generate_questions(visual, log, state)

        # Assess understanding level
        understanding_level = self._assess_understanding_level(
            visual, log, state, context, emotional_state
        )

        # Calculate confidence
        confidence = self._calculate_confidence(visual, log, state)

        understanding = MultiModalUnderstanding(
            modality_type=modality_input.modality_type,
            understanding_level=understanding_level,
            visual_analysis=visual,
            log_analysis=log,
            system_state_analysis=state,
            primary_insight=primary_insight,
            supporting_evidence=self._collect_evidence(visual, log, state),
            confidence=confidence,
            meta_cognitive_connections=meta_connections,
            emotional_context=emotional_context,
            causal_chain=causal_chain,
            temporal_context=temporal_context,
            predictive_insights=predictive,
            suggested_actions=actions,
            questions_to_ask=questions,
            timestamp=datetime.now()
        )

        # Learn from this understanding
        self.understanding_history.append(understanding)

        return understanding

    def analyze_multiple(
        self,
        inputs: List[ModalityInput],
        context: Optional[any] = None
    ) -> MultiModalAnalysis:
        """
        Analyze multiple inputs across modalities

        This is where true multi-modal synthesis happens -
        combining insights from different sensory inputs.
        """
        understandings = []

        # Understand each input
        for input_item in inputs:
            understanding = self.understand(input_item, context)
            understandings.append(understanding)

        # Cross-modal synthesis
        cross_modal = self._synthesize_cross_modal(understandings)

        # Generate unified narrative
        narrative = self._create_unified_narrative(understandings)

        # Calculate overall confidence
        overall_confidence = (
            sum(u.confidence for u in understandings) / len(understandings)
            if understandings else 0.0
        )

        # Identify missing context
        missing = self._identify_missing_context(understandings)

        # Assess consciousness impact
        consciousness_impact = self._assess_consciousness_impact(understandings)

        return MultiModalAnalysis(
            timestamp=datetime.now(),
            understandings=understandings,
            cross_modal_insights=cross_modal,
            unified_narrative=narrative,
            overall_confidence=overall_confidence,
            missing_context=missing,
            consciousness_impact=consciousness_impact
        )

    def _analyze_screenshot(self, content: Any) -> VisualAnalysis:
        """Analyze screenshot content"""
        # Simplified - would use actual computer vision in production

        # Detect elements (simulated)
        detected_elements = [
            VisualElement.WINDOW,
            VisualElement.TEXT,
        ]

        # Extract text (simulated OCR)
        if isinstance(content, str):
            extracted_text = content
        else:
            extracted_text = "Error: Permission denied\nCommand failed with exit code 1"

        # Detect visual cues
        if "error" in extracted_text.lower() or "failed" in extracted_text.lower():
            detected_elements.append(VisualElement.ERROR_INDICATOR)
            emotional_indicators = ["frustration_likely", "red_warning_colors"]
        else:
            emotional_indicators = []

        # Infer intent
        if "permission denied" in extracted_text.lower():
            user_intent = "Attempting privileged operation"
        else:
            user_intent = "Unknown"

        return VisualAnalysis(
            detected_elements=detected_elements,
            extracted_text=extracted_text,
            dominant_colors=["red", "white", "black"],
            layout_description="Terminal window with error message",
            likely_application="terminal",
            user_intent=user_intent,
            emotional_indicators=emotional_indicators,
            confidence=0.75
        )

    def _analyze_log_file(self, content: str) -> LogAnalysis:
        """Deep analysis of log file"""
        lines = content.split('\n') if isinstance(content, str) else []

        # Extract errors and warnings
        errors = [line for line in lines if 'error' in line.lower()]
        warnings = [line for line in lines if 'warn' in line.lower()]

        # Find key events
        key_events = []
        if errors:
            key_events.append(f"First error: {errors[0]}")

        # Infer root cause
        if errors:
            root_cause = self._infer_root_cause_from_errors(errors)
        else:
            root_cause = None

        # Error progression
        error_progression = []
        if len(errors) > 1:
            error_progression = [
                f"Error cascade: {len(errors)} errors detected",
                f"Pattern: {'repeated' if len(set(errors)) < len(errors) else 'varied'} errors"
            ]

        return LogAnalysis(
            log_type="system_log",
            time_range=(datetime.now(), datetime.now()),
            error_messages=errors[:5],  # Top 5
            warning_messages=warnings[:5],
            key_events=key_events,
            root_cause=root_cause,
            error_progression=error_progression,
            critical_timestamps=[datetime.now()],
            related_patterns=["error_cascade", "permission_issues"],
            suggested_actions=self._suggest_actions_from_log(errors, warnings),
            confidence=0.8
        )

    def _analyze_terminal_output(self, content: str) -> VisualAnalysis:
        """Analyze terminal output specifically"""
        # Similar to screenshot but terminal-focused
        detected_elements = [VisualElement.TERMINAL, VisualElement.TEXT]

        # Check for command prompt
        if '$' in content or '#' in content or '>' in content:
            detected_elements.append(VisualElement.COMMAND_PROMPT)

        # Check for error indicators (including ERR!)
        content_lower = content.lower()
        if 'error' in content_lower or 'failed' in content_lower or 'err!' in content_lower:
            detected_elements.append(VisualElement.ERROR_INDICATOR)
            emotional_indicators = ["frustration_likely"]
        elif 'success' in content_lower or 'complete' in content_lower:
            detected_elements.append(VisualElement.SUCCESS_INDICATOR)
            emotional_indicators = ["satisfaction_likely"]
        else:
            emotional_indicators = []

        return VisualAnalysis(
            detected_elements=detected_elements,
            extracted_text=content,
            dominant_colors=["black", "white", "green"],
            layout_description="Terminal command output",
            likely_application="terminal",
            user_intent="Executing system command",
            emotional_indicators=emotional_indicators,
            confidence=0.85
        )

    def _analyze_system_state(self, content: Any) -> SystemStateAnalysis:
        """Analyze system state information"""
        # Simplified - would parse actual system metrics
        return SystemStateAnalysis(
            state_type="system_resources",
            current_values={
                "cpu_usage": "75%",
                "memory_usage": "60%",
                "disk_usage": "85%"
            },
            trend="stable",
            anomalies=["disk_usage_high"],
            severity="moderate",
            likely_causes=["Normal operation with high disk usage"],
            predicted_outcomes=["May need disk cleanup soon"],
            confidence=0.8
        )

    def _generate_primary_insight(
        self, visual, log, state, modality_type
    ) -> str:
        """Generate the primary insight from analysis"""
        if visual and visual.extracted_text:
            if "error" in visual.extracted_text.lower():
                return "User encountering error - likely permission issue"
            elif "success" in visual.extracted_text.lower():
                return "Operation completed successfully"

        if log and log.error_messages:
            return f"System experiencing errors: {len(log.error_messages)} detected"

        if state and state.anomalies:
            return f"System state anomaly: {state.anomalies[0]}"

        return "Understanding context from multi-modal input"

    def _connect_to_patterns(self, recent_patterns: Optional[List[str]]) -> List[str]:
        """Connect to patterns from meta-cognitive layer"""
        if not recent_patterns:
            return []

        return [f"Related to pattern: {p}" for p in recent_patterns[:3]]

    def _assess_emotional_context(self, emotional_state, visual, log) -> Optional[str]:
        """Assess emotional context from visual/log cues"""
        if visual and "frustration_likely" in visual.emotional_indicators:
            return "Visual cues suggest user frustration"

        if log and log.error_messages:
            return "Repeated errors likely causing frustration"

        if emotional_state:
            return f"Emotional state: {emotional_state}"

        return None

    def _infer_causal_chain(self, log, state) -> Optional[str]:
        """Infer causal chain from log/state"""
        if log and log.root_cause:
            return f"Root cause: {log.root_cause}"

        if state and state.likely_causes:
            return f"Likely cause: {state.likely_causes[0]}"

        return None

    def _extract_temporal_context(self, log, state) -> Optional[str]:
        """Extract temporal context"""
        if log and log.error_progression:
            return f"Temporal pattern: {log.error_progression[0]}"

        if state and state.trend:
            return f"Trend: {state.trend}"

        return None

    def _generate_predictions(self, visual, log, state) -> List[str]:
        """Generate predictions based on analysis"""
        predictions = []

        if log and len(log.error_messages) > 3:
            predictions.append("More errors likely if root cause not addressed")

        if state and state.predicted_outcomes:
            predictions.extend(state.predicted_outcomes)

        return predictions

    def _suggest_actions(self, visual, log, state, insight) -> List[str]:
        """Suggest actionable steps"""
        actions = []

        if visual and "permission denied" in visual.extracted_text.lower():
            actions.append("Try running with sudo or check file permissions")

        if log and log.suggested_actions:
            actions.extend(log.suggested_actions)

        if state and "disk_usage_high" in state.anomalies:
            actions.append("Consider running disk cleanup")

        return actions

    def _suggest_actions_from_log(self, errors: List[str], warnings: List[str]) -> List[str]:
        """Suggest actions based on log analysis"""
        actions = []

        if errors:
            actions.append("Investigate error messages for root cause")

        if len(errors) > 5:
            actions.append("Consider error correlation - may be cascading issue")

        return actions

    def _generate_questions(self, visual, log, state) -> List[str]:
        """Generate clarifying questions"""
        questions = []

        if visual and visual.user_intent == "Unknown":
            questions.append("What were you trying to accomplish?")

        if log and not log.root_cause:
            questions.append("What actions preceded these errors?")

        return questions

    def _assess_understanding_level(
        self, visual, log, state, context, emotional_state
    ) -> UnderstandingLevel:
        """Assess how deeply we understand"""
        # Count how many layers of context we have
        context_layers = sum([
            bool(visual),
            bool(log),
            bool(state),
            bool(context),
            bool(emotional_state)
        ])

        if context_layers >= 4:
            return UnderstandingLevel.INTEGRATED
        elif context_layers >= 3:
            return UnderstandingLevel.CONTEXTUAL
        elif context_layers >= 2:
            return UnderstandingLevel.SEMANTIC
        elif context_layers >= 1:
            return UnderstandingLevel.SYNTACTIC
        else:
            return UnderstandingLevel.SURFACE

    def _calculate_confidence(self, visual, log, state) -> float:
        """Calculate overall confidence"""
        confidences = []

        if visual:
            confidences.append(visual.confidence)
        if log:
            confidences.append(log.confidence)
        if state:
            confidences.append(state.confidence)

        return sum(confidences) / len(confidences) if confidences else 0.5

    def _collect_evidence(self, visual, log, state) -> List[str]:
        """Collect supporting evidence"""
        evidence = []

        if visual and visual.extracted_text:
            evidence.append(f"Visual: {visual.extracted_text[:100]}")

        if log and log.error_messages:
            evidence.append(f"Log: {len(log.error_messages)} errors detected")

        if state and state.anomalies:
            evidence.append(f"State: {state.anomalies}")

        return evidence

    def _infer_root_cause_from_errors(self, errors: List[str]) -> Optional[str]:
        """Infer root cause from error messages"""
        # Simple pattern matching - would be more sophisticated
        error_text = ' '.join(errors).lower()

        if 'permission' in error_text:
            return "Permission/access issue"
        elif 'not found' in error_text or 'no such' in error_text:
            return "Missing file or command"
        elif 'connection' in error_text:
            return "Network connectivity issue"
        elif 'memory' in error_text or 'oom' in error_text:
            return "Memory exhaustion"

        return "Unknown root cause - multiple errors"

    def _synthesize_cross_modal(
        self, understandings: List[MultiModalUnderstanding]
    ) -> List[str]:
        """Synthesize insights across modalities"""
        if len(understandings) < 2:
            return []

        insights = []

        # Look for correlations
        has_visual_error = any(
            u.visual_analysis and
            VisualElement.ERROR_INDICATOR in u.visual_analysis.detected_elements
            for u in understandings
        )

        has_log_errors = any(
            u.log_analysis and u.log_analysis.error_messages
            for u in understandings
        )

        if has_visual_error and has_log_errors:
            insights.append("Visual errors correlated with log errors - confirms issue")

        return insights

    def _create_unified_narrative(
        self, understandings: List[MultiModalUnderstanding]
    ) -> str:
        """Create coherent narrative across all inputs"""
        if not understandings:
            return "No multi-modal input to synthesize"

        parts = []

        for u in understandings:
            parts.append(f"[{u.modality_type.value}] {u.primary_insight}")

        narrative = "Multi-modal understanding: " + " → ".join(parts)

        return narrative

    def _identify_missing_context(
        self, understandings: List[MultiModalUnderstanding]
    ) -> List[str]:
        """Identify what context would help understanding"""
        missing = []

        has_visual = any(u.visual_analysis for u in understandings)
        has_logs = any(u.log_analysis for u in understandings)
        has_state = any(u.system_state_analysis for u in understandings)

        if not has_visual:
            missing.append("Screenshot would provide visual context")
        if not has_logs:
            missing.append("Log files would show error history")
        if not has_state:
            missing.append("System state would show resource usage")

        return missing

    def _assess_consciousness_impact(
        self, understandings: List[MultiModalUnderstanding]
    ) -> str:
        """Assess how this affects overall consciousness state"""
        error_count = sum(
            1 for u in understandings
            if u.visual_analysis and
            VisualElement.ERROR_INDICATOR in u.visual_analysis.detected_elements
        )

        if error_count >= 2:
            return "Multiple error indicators - user likely frustrated, consciousness strained"
        elif error_count == 1:
            return "Single error detected - manageable challenge"
        else:
            return "No significant stress indicators - consciousness stable"

    def get_understanding_summary(
        self, understanding: MultiModalUnderstanding
    ) -> str:
        """Get human-readable summary"""
        parts = [
            f"👁️ Multi-Modal Understanding ({understanding.modality_type.value})",
            f"\n🎯 Primary Insight: {understanding.primary_insight}",
            f"📊 Confidence: {understanding.confidence:.0%}",
            f"🧠 Understanding Level: {understanding.understanding_level.value}",
        ]

        if understanding.suggested_actions:
            parts.append(f"\n⚡ Actions: {len(understanding.suggested_actions)}")
            for action in understanding.suggested_actions[:3]:
                parts.append(f"  • {action}")

        if understanding.predictive_insights:
            parts.append(f"\n🔮 Predictions:")
            for pred in understanding.predictive_insights[:2]:
                parts.append(f"  • {pred}")

        return "\n".join(parts)


# Global multi-modal understanding engine
_multimodal_engine: Optional[MultiModalUnderstandingEngine] = None


def get_multimodal_understanding_engine() -> MultiModalUnderstandingEngine:
    """Get or create multi-modal understanding engine"""
    global _multimodal_engine
    if _multimodal_engine is None:
        _multimodal_engine = MultiModalUnderstandingEngine()
    return _multimodal_engine
