"""
Dynamic Response Adaptation - Layer 6 Component 2

Revolutionary capability: Adjust responses IN REAL-TIME as user consumes them.

Traditional AI: Generate full response, send, hope they read it
Revolutionary AI: Monitor consumption, adapt on the fly

Key innovations:
1. Response Monitoring: Track how user engages with response
2. Real-Time Adjustment: Modify format/content based on behavior
3. Adaptive Formatting: Collapse/expand sections dynamically
4. Interruption Handling: User asks mid-response? Adjust immediately
5. Consumption Prediction: Predict what they'll want next

This makes responses LIVING - they adapt to how they're being used.
"""

from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class ConsumptionPattern(Enum):
    """How user is consuming the response"""
    READING_FULLY = "reading_fully"          # Taking time, reading everything
    SKIMMING = "skimming"                    # Quick scroll, hitting highlights
    JUMPING_TO_CODE = "jumping_to_code"      # Going straight to code blocks
    COPY_PASTING = "copy_pasting"            # Executing immediately
    PAUSED = "paused"                        # Stopped to think/try something
    ABANDONED = "abandoned"                   # Moved on without finishing


class ResponseSection(Enum):
    """Different sections of a response"""
    SUMMARY = "summary"                      # Quick overview
    EXPLANATION = "explanation"              # Detailed explanation
    CODE = "code"                            # Code blocks
    EXAMPLES = "examples"                    # Usage examples
    ALTERNATIVES = "alternatives"            # Other options
    TECHNICAL_DETAILS = "technical_details"  # Deep dive
    TROUBLESHOOTING = "troubleshooting"      # Common issues


@dataclass
class ConsumptionSignal:
    """Signal about how user is consuming response"""
    timestamp: str
    signal_type: str                  # "started_reading", "scrolled_fast", "copied_code", etc.
    section: Optional[ResponseSection] = None
    time_spent_ms: float = 0.0
    context: Optional[Dict] = None


@dataclass
class AdaptiveResponse:
    """
    A response that can adapt in real-time.

    Each section can be:
    - expanded: Show full details
    - collapsed: Show summary only
    - hidden: Don't show at all
    - prioritized: Move to top
    """
    sections: Dict[ResponseSection, str]  # Section → Content
    section_states: Dict[ResponseSection, str]  # Section → "expanded"/"collapsed"/"hidden"
    priority_order: List[ResponseSection]  # Order to show sections
    consumption_pattern: Optional[ConsumptionPattern] = None


class DynamicResponseAdapter:
    """
    Adapts responses in real-time based on user consumption patterns.

    Revolutionary features:
    - Monitors how user engages with each section
    - Collapses sections they skip
    - Expands sections they linger on
    - Reorders based on what they need
    - Interrupts with clarifications if confused
    - Predicts next needed section
    """

    def __init__(self):
        """Initialize response adapter"""
        self.consumption_signals: List[ConsumptionSignal] = []
        self.current_response: Optional[AdaptiveResponse] = None
        self.section_engagement: Dict[ResponseSection, float] = {}

    def create_adaptive_response(
        self,
        content: Dict[ResponseSection, str],
        initial_consumption_pattern: Optional[ConsumptionPattern] = None
    ) -> AdaptiveResponse:
        """
        Create a response that can adapt in real-time.

        Args:
            content: Dictionary of section → content
            initial_consumption_pattern: Known pattern to start with

        Returns:
            AdaptiveResponse ready for real-time adaptation
        """
        # Default all sections to expanded
        section_states = {
            section: "expanded" for section in content.keys()
        }

        # Default priority order
        priority_order = list(content.keys())

        # Adapt initial state based on known pattern
        if initial_consumption_pattern:
            section_states, priority_order = self._adapt_for_pattern(
                content.keys(),
                initial_consumption_pattern
            )

        response = AdaptiveResponse(
            sections=content,
            section_states=section_states,
            priority_order=priority_order,
            consumption_pattern=initial_consumption_pattern
        )

        self.current_response = response
        return response

    def record_consumption_signal(self, signal: ConsumptionSignal):
        """
        Record how user is consuming the response.

        Call this as signals come in (scrolling, clicking, copying, etc.)
        """
        self.consumption_signals.append(signal)

        # Update section engagement scores
        if signal.section:
            current_score = self.section_engagement.get(signal.section, 0.0)

            if signal.signal_type == "reading_fully":
                self.section_engagement[signal.section] = current_score + 1.0
            elif signal.signal_type == "skipped":
                self.section_engagement[signal.section] = current_score - 0.5
            elif signal.signal_type == "copied_code":
                self.section_engagement[signal.section] = current_score + 0.8

    def adapt_response_realtime(self, response: AdaptiveResponse) -> AdaptiveResponse:
        """
        Adapt response based on real-time consumption signals.

        This is called DURING response consumption to adjust on the fly.

        Returns:
            Updated AdaptiveResponse with adapted states
        """
        if not self.consumption_signals:
            return response

        # Detect current consumption pattern
        pattern = self._detect_consumption_pattern()
        response.consumption_pattern = pattern

        # Adapt sections based on pattern
        if pattern == ConsumptionPattern.SKIMMING:
            # User skimming - collapse details, show summaries
            response = self._optimize_for_skimming(response)

        elif pattern == ConsumptionPattern.JUMPING_TO_CODE:
            # User wants code - prioritize code blocks
            response = self._optimize_for_code(response)

        elif pattern == ConsumptionPattern.READING_FULLY:
            # User reading everything - maintain full detail
            response = self._optimize_for_deep_reading(response)

        elif pattern == ConsumptionPattern.COPY_PASTING:
            # User executing - provide executable blocks
            response = self._optimize_for_execution(response)

        elif pattern == ConsumptionPattern.PAUSED:
            # User paused - might be trying something
            response = self._optimize_for_experimentation(response)

        # Reorder sections based on engagement
        response.priority_order = self._calculate_priority_order(response)

        return response

    def _detect_consumption_pattern(self) -> ConsumptionPattern:
        """Detect how user is consuming response from signals"""
        if not self.consumption_signals:
            return ConsumptionPattern.READING_FULLY

        recent_signals = self.consumption_signals[-5:]  # Last 5 signals

        # Count signal types
        reading_count = sum(1 for s in recent_signals if "reading" in s.signal_type)
        scrolling_fast = sum(1 for s in recent_signals if "scrolled_fast" in s.signal_type)
        code_interaction = sum(1 for s in recent_signals if "code" in s.signal_type)
        copy_paste = sum(1 for s in recent_signals if "copied" in s.signal_type)

        # Determine pattern
        if copy_paste >= 2:
            return ConsumptionPattern.COPY_PASTING
        elif code_interaction >= 3:
            return ConsumptionPattern.JUMPING_TO_CODE
        elif scrolling_fast >= 3:
            return ConsumptionPattern.SKIMMING
        elif reading_count >= 3:
            return ConsumptionPattern.READING_FULLY
        else:
            return ConsumptionPattern.PAUSED

    def _optimize_for_skimming(self, response: AdaptiveResponse) -> AdaptiveResponse:
        """Optimize response for users who skim"""
        # Collapse detailed sections
        for section in [ResponseSection.TECHNICAL_DETAILS, ResponseSection.EXPLANATION]:
            if section in response.section_states:
                response.section_states[section] = "collapsed"

        # Prioritize summary and code
        priority = [
            ResponseSection.SUMMARY,
            ResponseSection.CODE,
            ResponseSection.EXAMPLES
        ]

        return response

    def _optimize_for_code(self, response: AdaptiveResponse) -> AdaptiveResponse:
        """Optimize for users jumping to code"""
        # Prioritize code and examples
        priority = [
            ResponseSection.CODE,
            ResponseSection.EXAMPLES,
            ResponseSection.SUMMARY
        ]

        # Collapse explanations
        if ResponseSection.EXPLANATION in response.section_states:
            response.section_states[ResponseSection.EXPLANATION] = "collapsed"

        return response

    def _optimize_for_deep_reading(self, response: AdaptiveResponse) -> AdaptiveResponse:
        """Optimize for users reading everything"""
        # Expand all sections
        for section in response.section_states:
            response.section_states[section] = "expanded"

        # Maintain logical order
        return response

    def _optimize_for_execution(self, response: AdaptiveResponse) -> AdaptiveResponse:
        """Optimize for users executing immediately"""
        # Prioritize executable code
        priority = [
            ResponseSection.CODE,
            ResponseSection.TROUBLESHOOTING,
            ResponseSection.SUMMARY
        ]

        # Hide alternatives (they want to execute NOW)
        if ResponseSection.ALTERNATIVES in response.section_states:
            response.section_states[ResponseSection.ALTERNATIVES] = "hidden"

        return response

    def _optimize_for_experimentation(self, response: AdaptiveResponse) -> AdaptiveResponse:
        """Optimize when user has paused (trying something)"""
        # Show troubleshooting prominently
        priority = [
            ResponseSection.TROUBLESHOOTING,
            ResponseSection.EXAMPLES,
            ResponseSection.ALTERNATIVES
        ]

        return response

    def _calculate_priority_order(self, response: AdaptiveResponse) -> List[ResponseSection]:
        """Calculate section order based on engagement scores"""
        # Sections with highest engagement first
        sorted_sections = sorted(
            response.sections.keys(),
            key=lambda s: self.section_engagement.get(s, 0.0),
            reverse=True
        )

        return sorted_sections

    def _adapt_for_pattern(
        self,
        sections: List[ResponseSection],
        pattern: ConsumptionPattern
    ) -> tuple[Dict[ResponseSection, str], List[ResponseSection]]:
        """Adapt initial state for known consumption pattern"""
        states = {}
        priority = []

        if pattern == ConsumptionPattern.SKIMMING:
            states = {s: "collapsed" if s in [ResponseSection.TECHNICAL_DETAILS, ResponseSection.EXPLANATION] else "expanded" for s in sections}
            priority = [ResponseSection.SUMMARY, ResponseSection.CODE] + [s for s in sections if s not in [ResponseSection.SUMMARY, ResponseSection.CODE]]

        elif pattern == ConsumptionPattern.JUMPING_TO_CODE:
            states = {s: "expanded" if s == ResponseSection.CODE else "collapsed" for s in sections}
            priority = [ResponseSection.CODE] + [s for s in sections if s != ResponseSection.CODE]

        elif pattern == ConsumptionPattern.READING_FULLY:
            states = {s: "expanded" for s in sections}
            priority = list(sections)

        else:
            states = {s: "expanded" for s in sections}
            priority = list(sections)

        return states, priority

    def format_adaptive_response(self, response: AdaptiveResponse) -> str:
        """
        Format the adaptive response as markdown.

        Sections are shown in priority order, with states respected.
        """
        output_parts = []

        for section in response.priority_order:
            if section not in response.sections:
                continue

            state = response.section_states.get(section, "expanded")

            if state == "hidden":
                continue

            content = response.sections[section]

            if state == "collapsed":
                # Show just summary/first line
                first_line = content.split('\n')[0] if content else ""
                output_parts.append(f"**{section.value.title()}**: {first_line}\n<details>Click to expand</details>\n")
            else:
                # Show full content
                output_parts.append(f"## {section.value.title()}\n\n{content}\n")

        return "\n".join(output_parts)

    def should_interrupt_with_clarification(self) -> Optional[str]:
        """
        Determine if we should interrupt with a clarification.

        If user seems confused about current section, offer help.

        Returns:
            Clarification message if needed, None otherwise
        """
        if not self.consumption_signals:
            return None

        # Check for confusion signals
        recent = self.consumption_signals[-3:]

        # Multiple re-reads of same section?
        sections_read = [s.section for s in recent if s.section]
        if len(sections_read) >= 2 and len(set(sections_read)) == 1:
            section = sections_read[0]
            return f"I notice you're re-reading the {section.value} section. Would an example help clarify?"

        # Long pause on complex section?
        for signal in recent:
            if signal.section == ResponseSection.TECHNICAL_DETAILS and signal.time_spent_ms > 30000:  # 30 seconds
                return "That's a complex section! Want me to break it down step-by-step?"

        return None

    def predict_next_needed_section(self, response: AdaptiveResponse) -> Optional[ResponseSection]:
        """
        Predict what section user will need next.

        Based on consumption patterns and typical workflows.
        """
        if not self.consumption_signals:
            return None

        # If they just read code, they might need troubleshooting
        last_signal = self.consumption_signals[-1]
        if last_signal.section == ResponseSection.CODE:
            return ResponseSection.TROUBLESHOOTING

        # If they're in examples, they might want alternatives
        if last_signal.section == ResponseSection.EXAMPLES:
            return ResponseSection.ALTERNATIVES

        # If they read explanation, they probably want code next
        if last_signal.section == ResponseSection.EXPLANATION:
            return ResponseSection.CODE

        return None


def get_response_adapter() -> DynamicResponseAdapter:
    """Get singleton response adapter"""
    global _response_adapter

    if _response_adapter is None:
        _response_adapter = DynamicResponseAdapter()

    return _response_adapter


# Singleton
_response_adapter: Optional[DynamicResponseAdapter] = None
