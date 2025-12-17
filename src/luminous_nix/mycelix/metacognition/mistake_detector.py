"""
Mistake Detector - Self-Correcting Intelligence

Revolutionary capability: The AI can detect and correct its own mistakes.

This monitors for:
1. Logical inconsistencies in responses
2. Contradictions with known facts
3. Low confidence that turned out wrong
4. User signals (confusion, frustration, correction)
5. Unexpected outcomes

When a mistake is detected, the system:
1. Acknowledges it honestly
2. Explains what went wrong
3. Corrects the mistake
4. Learns to avoid it in the future

No covering up, no deflection - just honest mistake recognition and recovery.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict


class MistakeType(Enum):
    """Types of mistakes the system can detect"""
    LOGICAL_INCONSISTENCY = "logical_inconsistency"  # Self-contradictory
    FACTUAL_ERROR = "factual_error"  # Wrong information
    LOW_CONFIDENCE_WRONG = "low_confidence_wrong"  # Was uncertain, turns out wrong
    HIGH_CONFIDENCE_WRONG = "high_confidence_wrong"  # Was confident, turns out wrong
    MISUNDERSTANDING = "misunderstanding"  # Misunderstood the query
    INCOMPLETE_RESPONSE = "incomplete_response"  # Didn't fully answer
    UNHELPFUL = "unhelpful"  # Technically correct but not useful


@dataclass
class Recovery:
    """A recovery action taken after detecting a mistake"""
    mistake_type: MistakeType
    what_went_wrong: str
    corrected_response: str
    what_learned: str
    confidence_adjustment: float  # How much to adjust confidence for similar cases
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MistakePattern:
    """A pattern of mistakes"""
    pattern_type: str
    occurrences: int
    recent_examples: List[str]
    prevention_strategy: str
    last_seen: datetime = field(default_factory=datetime.now)


class MistakeDetector:
    """
    Detects and learns from mistakes

    Philosophy:
    - Mistakes are learning opportunities, not failures
    - Honesty about mistakes builds trust
    - Self-correction is a sign of intelligence, not weakness
    """

    def __init__(self):
        """Initialize mistake detector"""
        # Track detected mistakes
        self.mistake_history: List[Recovery] = []

        # Track mistake patterns
        self.patterns: Dict[str, MistakePattern] = {}

        # Track what triggers mistakes
        self.mistake_triggers: Dict[str, int] = defaultdict(int)

        # Statistics
        self.mistakes_detected = 0
        self.mistakes_corrected = 0
        self.false_positives = 0  # Thought it was a mistake but wasn't

    def check_response(
        self,
        query: str,
        response: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        previous_responses: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[MistakeType]:
        """
        Check if a response contains a mistake

        Args:
            query: Original query
            response: Response to check
            context: Context information
            previous_responses: Previous responses in this conversation

        Returns:
            MistakeType if mistake detected, None otherwise
        """
        # 1. Check for logical inconsistencies
        if self._check_logical_inconsistency(response):
            return MistakeType.LOGICAL_INCONSISTENCY

        # 2. Check for contradictions with previous responses
        if previous_responses and self._check_contradiction(response, previous_responses):
            return MistakeType.FACTUAL_ERROR

        # 3. Check for misunderstanding (response doesn't match query type)
        if self._check_misunderstanding(query, response):
            return MistakeType.MISUNDERSTANDING

        # 4. Check for incomplete response
        if self._check_incomplete(query, response):
            return MistakeType.INCOMPLETE_RESPONSE

        return None

    def _check_logical_inconsistency(self, response: Dict[str, Any]) -> bool:
        """Check for internal logical inconsistencies"""
        content = response.get("content", "")
        insights = response.get("insights", [])
        suggestions = response.get("suggestions", [])

        # Check for obvious contradictions in text
        # (This is simplified - could use NLP for better detection)

        contradiction_pairs = [
            ("enable", "disable"),
            ("install", "uninstall"),
            ("start", "stop"),
            ("allow", "block"),
            ("yes", "no"),
        ]

        text = content.lower()
        for word1, word2 in contradiction_pairs:
            if word1 in text and word2 in text:
                # Check if they're both in imperative form (commands)
                if f"{word1} " in text and f"{word2} " in text:
                    return True

        return False

    def _check_contradiction(
        self,
        response: Dict[str, Any],
        previous_responses: List[Dict[str, Any]]
    ) -> bool:
        """Check for contradictions with previous responses"""
        current_suggestions = set(response.get("suggestions", []))

        for prev in previous_responses:
            prev_suggestions = set(prev.get("suggestions", []))

            # Check for direct contradictions
            for curr in current_suggestions:
                for prev_sug in prev_suggestions:
                    if self._are_contradictory(curr, prev_sug):
                        return True

        return False

    def _are_contradictory(self, statement1: str, statement2: str) -> bool:
        """Check if two statements contradict each other"""
        # Simplified contradiction detection
        # Could be much more sophisticated with NLP

        s1 = statement1.lower()
        s2 = statement2.lower()

        contradiction_pairs = [
            ("enable", "disable"),
            ("install", "remove"),
            ("allow", "deny"),
        ]

        for word1, word2 in contradiction_pairs:
            if word1 in s1 and word2 in s2:
                # Check if they're talking about the same thing
                # (Very simplified - extract subject)
                subject1 = s1.replace(word1, "").strip()
                subject2 = s2.replace(word2, "").strip()

                if self._similar_subjects(subject1, subject2):
                    return True

        return False

    def _similar_subjects(self, subject1: str, subject2: str) -> bool:
        """Check if two subjects are similar enough"""
        # Very basic similarity check
        words1 = set(subject1.split())
        words2 = set(subject2.split())

        if not words1 or not words2:
            return False

        overlap = len(words1 & words2)
        return overlap >= 2 or overlap / max(len(words1), len(words2)) > 0.5

    def _check_misunderstanding(self, query: str, response: Dict[str, Any]) -> bool:
        """Check if response shows misunderstanding of query"""
        query_lower = query.lower()

        # Check for question vs command mismatch
        is_question = any(word in query_lower for word in ["what", "how", "why", "when", "where", "?"])
        is_command = any(word in query_lower for word in ["install", "configure", "enable", "disable"])

        content = response.get("content", "").lower()
        actions = response.get("actions", [])

        # If it's a question, we shouldn't be suggesting actions
        if is_question and actions:
            return True

        # If it's a command, we should have actions or concrete suggestions
        if is_command and not actions and not response.get("suggestions"):
            return True

        return False

    def _check_incomplete(self, query: str, response: Dict[str, Any]) -> bool:
        """Check if response is incomplete"""
        content = response.get("content", "")

        # Very short responses might be incomplete
        if len(content) < 20:
            return True

        # If query asks for multiple things, check if we addressed all
        # (Simplified - could be more sophisticated)
        if " and " in query.lower():
            parts = query.lower().split(" and ")
            addressed = sum(1 for part in parts if any(word in content.lower() for word in part.split()))
            if addressed < len(parts):
                return True

        return False

    def detect_from_user_signal(
        self,
        signal_type: str,
        query: str,
        response: Dict[str, Any],
        user_feedback: Optional[str] = None
    ) -> Optional[MistakeType]:
        """
        Detect mistake from user signals

        Args:
            signal_type: "confusion", "frustration", "correction", "negative_feedback"
            query: Original query
            response: Response that caused the signal
            user_feedback: User's feedback text

        Returns:
            MistakeType if detected
        """
        self.mistake_triggers[signal_type] += 1

        confidence = response.get("confidence", 0.5)

        if signal_type == "correction":
            # User explicitly corrected us - we were wrong
            if confidence > 0.7:
                return MistakeType.HIGH_CONFIDENCE_WRONG
            else:
                return MistakeType.LOW_CONFIDENCE_WRONG

        elif signal_type == "confusion":
            # User is confused - probably misunderstood
            return MistakeType.MISUNDERSTANDING

        elif signal_type == "negative_feedback":
            # User said it wasn't helpful
            return MistakeType.UNHELPFUL

        elif signal_type == "frustration":
            # Something went wrong
            if confidence > 0.7:
                return MistakeType.HIGH_CONFIDENCE_WRONG
            else:
                return MistakeType.UNHELPFUL

        return None

    def recover(
        self,
        mistake_type: MistakeType,
        original_query: str,
        original_response: Dict[str, Any],
        correction_info: Optional[Dict[str, Any]] = None
    ) -> Recovery:
        """
        Generate recovery action for a mistake

        Args:
            mistake_type: Type of mistake detected
            original_query: The query that was answered
            original_response: The response that contained the mistake
            correction_info: Additional information for correction

        Returns:
            Recovery object with corrected response and learning
        """
        self.mistakes_detected += 1

        # Generate explanation of what went wrong
        what_went_wrong = self._explain_mistake(mistake_type, original_response)

        # Generate corrected response
        corrected_response = self._generate_correction(
            mistake_type, original_query, original_response, correction_info
        )

        # Extract learning
        what_learned = self._extract_learning(mistake_type, original_query, correction_info)

        # Determine confidence adjustment
        confidence_adjustment = self._calculate_confidence_adjustment(
            mistake_type, original_response.get("confidence", 0.5)
        )

        recovery = Recovery(
            mistake_type=mistake_type,
            what_went_wrong=what_went_wrong,
            corrected_response=corrected_response,
            what_learned=what_learned,
            confidence_adjustment=confidence_adjustment
        )

        # Store in history
        self.mistake_history.append(recovery)

        # Update patterns
        self._update_patterns(mistake_type, original_query, what_learned)

        self.mistakes_corrected += 1

        return recovery

    def _explain_mistake(self, mistake_type: MistakeType, response: Dict[str, Any]) -> str:
        """Generate explanation of what went wrong"""
        explanations = {
            MistakeType.LOGICAL_INCONSISTENCY: "I gave contradictory advice in my response",
            MistakeType.FACTUAL_ERROR: "I provided incorrect information",
            MistakeType.LOW_CONFIDENCE_WRONG: "I wasn't confident and turns out I was wrong",
            MistakeType.HIGH_CONFIDENCE_WRONG: "I was confident but I was actually wrong",
            MistakeType.MISUNDERSTANDING: "I misunderstood what you were asking for",
            MistakeType.INCOMPLETE_RESPONSE: "I didn't fully answer your question",
            MistakeType.UNHELPFUL: "My response wasn't actually helpful for your needs",
        }

        return explanations.get(
            mistake_type,
            "Something went wrong in my response"
        )

    def _generate_correction(
        self,
        mistake_type: MistakeType,
        query: str,
        original_response: Dict[str, Any],
        correction_info: Optional[Dict[str, Any]]
    ) -> str:
        """Generate corrected response"""
        if correction_info and "correct_response" in correction_info:
            return correction_info["correct_response"]

        # Generate apology + acknowledgment
        apology = f"I apologize for the confusion. {self._explain_mistake(mistake_type, original_response)}. "

        # Suggest action
        if mistake_type == MistakeType.MISUNDERSTANDING:
            return apology + "Could you rephrase your question so I can better understand?"
        elif mistake_type == MistakeType.INCOMPLETE_RESPONSE:
            return apology + "Let me provide a more complete answer..."
        else:
            return apology + "Let me try again with the correct information."

    def _extract_learning(
        self,
        mistake_type: MistakeType,
        query: str,
        correction_info: Optional[Dict[str, Any]]
    ) -> str:
        """Extract what to learn from this mistake"""
        learnings = {
            MistakeType.LOGICAL_INCONSISTENCY: "Check for contradictions before responding",
            MistakeType.FACTUAL_ERROR: "Verify facts against knowledge base",
            MistakeType.LOW_CONFIDENCE_WRONG: "Acknowledge uncertainty more explicitly",
            MistakeType.HIGH_CONFIDENCE_WRONG: "Be more cautious even when confident",
            MistakeType.MISUNDERSTANDING: "Analyze query intent more carefully",
            MistakeType.INCOMPLETE_RESPONSE: "Ensure all parts of query are addressed",
            MistakeType.UNHELPFUL: "Focus on practical usefulness, not just correctness",
        }

        base_learning = learnings.get(mistake_type, "Review response generation process")

        # Add specific context if available
        if correction_info and "specific_issue" in correction_info:
            base_learning += f": {correction_info['specific_issue']}"

        return base_learning

    def _calculate_confidence_adjustment(
        self,
        mistake_type: MistakeType,
        original_confidence: float
    ) -> float:
        """Calculate how much to adjust confidence for similar cases"""
        adjustments = {
            MistakeType.LOGICAL_INCONSISTENCY: -0.2,
            MistakeType.FACTUAL_ERROR: -0.3,
            MistakeType.LOW_CONFIDENCE_WRONG: -0.1,  # Already was low
            MistakeType.HIGH_CONFIDENCE_WRONG: -0.4,  # Major correction needed
            MistakeType.MISUNDERSTANDING: -0.2,
            MistakeType.INCOMPLETE_RESPONSE: -0.1,
            MistakeType.UNHELPFUL: -0.15,
        }

        return adjustments.get(mistake_type, -0.2)

    def _update_patterns(self, mistake_type: MistakeType, query: str, learning: str):
        """Update mistake patterns"""
        pattern_key = mistake_type.value

        if pattern_key not in self.patterns:
            self.patterns[pattern_key] = MistakePattern(
                pattern_type=mistake_type.value,
                occurrences=0,
                recent_examples=[],
                prevention_strategy=learning
            )

        pattern = self.patterns[pattern_key]
        pattern.occurrences += 1
        pattern.recent_examples.append(query[:100])  # Limit length
        pattern.last_seen = datetime.now()

        # Keep only recent examples
        if len(pattern.recent_examples) > 10:
            pattern.recent_examples = pattern.recent_examples[-10:]

    def get_stats(self) -> Dict[str, Any]:
        """Get mistake detection statistics"""
        return {
            "mistakes_detected": self.mistakes_detected,
            "mistakes_corrected": self.mistakes_corrected,
            "false_positives": self.false_positives,
            "correction_rate": (
                self.mistakes_corrected / self.mistakes_detected
                if self.mistakes_detected > 0
                else 0.0
            ),
            "mistake_patterns": len(self.patterns),
            "most_common_mistakes": self._get_most_common_mistakes(5),
            "trigger_distribution": dict(self.mistake_triggers),
        }

    def _get_most_common_mistakes(self, n: int) -> List[Dict[str, Any]]:
        """Get most common mistake patterns"""
        sorted_patterns = sorted(
            self.patterns.values(),
            key=lambda p: p.occurrences,
            reverse=True
        )

        return [
            {
                "type": p.pattern_type,
                "occurrences": p.occurrences,
                "prevention": p.prevention_strategy
            }
            for p in sorted_patterns[:n]
        ]
