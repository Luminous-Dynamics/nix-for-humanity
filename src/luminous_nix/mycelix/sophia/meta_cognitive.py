"""
Meta-Cognitive Mirror - Reflects your patterns back to you

Sophia's meta-cognitive engine provides self-awareness by:
- Tracking your work patterns over time
- Identifying habits (good and bad)
- Suggesting growth opportunities
- Celebrating achievements
- Helping you become a more conscious developer

Example insights:
- "You tend to rush through configuration without testing (60% success vs 30%)"
- "You've been in flow state 2.7x longer this week - great progress!"
- "Your most productive time is 9am-11am - schedule deep work then"
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
from enum import Enum
import logging

from ..context import get_context_engine, Context, SessionState
from ..prediction import get_pattern_completer

logger = logging.getLogger(__name__)


class PatternType(Enum):
    """Types of patterns we track"""
    WORK_HABIT = "work_habit"          # How you work
    WORKFLOW = "workflow"               # Your process
    TIMING = "timing"                   # When you work
    SUCCESS_RATE = "success_rate"       # How often things work
    LEARNING = "learning"               # What you're learning
    GROWTH = "growth"                   # How you're improving


class InsightType(Enum):
    """Types of insights we generate"""
    PATTERN_IDENTIFIED = "pattern_identified"
    HABIT_SUGGESTION = "habit_suggestion"
    GROWTH_OPPORTUNITY = "growth_opportunity"
    CELEBRATION = "celebration"
    WARNING = "warning"
    TREND = "trend"


@dataclass
class Pattern:
    """A detected user pattern"""
    pattern_type: PatternType
    name: str
    description: str
    frequency: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    first_observed: datetime
    last_observed: datetime
    occurrences: int
    impact: str  # positive, negative, neutral

    # Statistics
    success_rate: Optional[float] = None
    avg_duration: Optional[float] = None  # seconds
    time_of_day: Optional[str] = None  # "morning", "afternoon", "evening"

    # Growth tracking
    trend: Optional[str] = None  # "improving", "declining", "stable"

    def __str__(self) -> str:
        """Human-readable pattern description"""
        emoji = {
            "positive": "✅",
            "negative": "⚠️",
            "neutral": "ℹ️"
        }.get(self.impact, "•")

        return f"{emoji} {self.name}: {self.description} ({self.frequency:.0%} frequency)"


@dataclass
class Insight:
    """An insight about user behavior"""
    insight_type: InsightType
    title: str
    message: str
    evidence: List[str]
    suggested_action: Optional[str] = None
    confidence: float = 0.8
    timestamp: datetime = field(default_factory=datetime.now)

    def __str__(self) -> str:
        """Format insight for display"""
        emoji = {
            InsightType.PATTERN_IDENTIFIED: "🔍",
            InsightType.HABIT_SUGGESTION: "💡",
            InsightType.GROWTH_OPPORTUNITY: "🌱",
            InsightType.CELEBRATION: "🎉",
            InsightType.WARNING: "⚠️",
            InsightType.TREND: "📈"
        }.get(self.insight_type, "•")

        output = f"{emoji} {self.title}\n{self.message}"

        if self.suggested_action:
            output += f"\n💡 Try: {self.suggested_action}"

        return output


class MetaCognitiveEngine:
    """
    The Meta-Cognitive Mirror - Provides self-awareness

    This engine tracks user patterns and reflects them back,
    creating a feedback loop that enables conscious growth.

    Key capabilities:
    1. Pattern Detection - Identify recurring behaviors
    2. Habit Analysis - Good habits vs bad habits
    3. Growth Tracking - Are you improving?
    4. Insight Generation - Actionable self-awareness
    5. Celebration - Acknowledge achievements
    """

    def __init__(self):
        """Initialize the meta-cognitive engine"""
        self.context_engine = get_context_engine()
        self.pattern_completer = get_pattern_completer()

        # Pattern tracking
        self.patterns: Dict[str, Pattern] = {}
        self.insights: List[Insight] = []

        # Statistics tracking
        self.command_history: List[Tuple[str, bool, datetime]] = []
        self.session_durations: List[float] = []
        self.flow_state_durations: List[float] = []

        # Growth metrics
        self.weekly_stats: Dict[str, Dict] = defaultdict(dict)

    def analyze_current_session(self, context: Optional[Context] = None) -> List[Insight]:
        """
        Analyze the current session and generate insights

        Args:
            context: Optional context (uses current if None)

        Returns:
            List of insights about current behavior
        """
        if context is None:
            context = self.context_engine.get_current_context()

        insights = []

        # Detect patterns
        insights.extend(self._detect_workflow_patterns(context))

        # Analyze success rates
        insights.extend(self._analyze_success_rates(context))

        # Check for flow state
        insights.extend(self._detect_flow_state(context))

        # Look for growth opportunities
        insights.extend(self._identify_growth_opportunities(context))

        # Celebrate achievements
        insights.extend(self._generate_celebrations(context))

        self.insights.extend(insights)
        return insights

    def get_pattern_reflection(self) -> str:
        """
        Generate a reflection on learned patterns

        Returns:
            Markdown-formatted reflection
        """
        if not self.patterns:
            return "## 🌱 Getting to Know You\n\nI'm still learning your patterns. Keep working and I'll start to notice your habits!"

        output = "## 🪞 Your Patterns (What I've Learned About You)\n\n"

        # Group patterns by impact
        positive = [p for p in self.patterns.values() if p.impact == "positive"]
        negative = [p for p in self.patterns.values() if p.impact == "negative"]
        neutral = [p for p in self.patterns.values() if p.impact == "neutral"]

        if positive:
            output += "### ✅ Good Habits\n"
            for pattern in sorted(positive, key=lambda p: p.frequency, reverse=True):
                output += f"- **{pattern.name}** ({pattern.frequency:.0%} of the time)\n"
                output += f"  {pattern.description}\n"
                if pattern.success_rate:
                    output += f"  Success rate: {pattern.success_rate:.0%}\n"
                output += "\n"

        if negative:
            output += "### ⚠️ Growth Opportunities\n"
            for pattern in sorted(negative, key=lambda p: p.frequency, reverse=True):
                output += f"- **{pattern.name}** ({pattern.frequency:.0%} of the time)\n"
                output += f"  {pattern.description}\n"
                if pattern.success_rate:
                    output += f"  Success rate: {pattern.success_rate:.0%}\n"
                output += "\n"

        if neutral:
            output += "### ℹ️ Your Workflow\n"
            for pattern in sorted(neutral, key=lambda p: p.frequency, reverse=True)[:5]:
                output += f"- {pattern.name}: {pattern.description}\n"

        return output

    def get_growth_report(self) -> str:
        """
        Generate a growth report showing improvement over time

        Returns:
            Markdown-formatted growth report
        """
        output = "## 📈 Your Growth Journey\n\n"

        if not self.weekly_stats:
            return output + "Keep working! I'll track your progress over time.\n"

        # Calculate trends
        weeks = sorted(self.weekly_stats.keys())
        if len(weeks) >= 2:
            latest = self.weekly_stats[weeks[-1]]
            previous = self.weekly_stats[weeks[-2]]

            # Compare metrics
            if "success_rate" in latest and "success_rate" in previous:
                change = latest["success_rate"] - previous["success_rate"]
                if change > 0:
                    output += f"✅ **Success rate improved by {change:.1%}** this week!\n\n"
                elif change < 0:
                    output += f"⚠️ Success rate decreased by {abs(change):.1%} - let's work on that\n\n"

            if "flow_time" in latest and "flow_time" in previous:
                change = latest["flow_time"] - previous["flow_time"]
                if change > 0:
                    output += f"🌊 **Flow state time increased by {change:.0f} minutes** this week!\n\n"

        # Recent achievements
        recent_insights = [i for i in self.insights
                          if i.insight_type == InsightType.CELEBRATION
                          and (datetime.now() - i.timestamp).days <= 7]

        if recent_insights:
            output += "### 🎉 Recent Achievements\n"
            for insight in recent_insights:
                output += f"- {insight.message}\n"

        return output

    def suggest_next_action(self, context: Optional[Context] = None) -> Optional[Insight]:
        """
        Suggest what the user should do next based on patterns

        Args:
            context: Optional context (uses current if None)

        Returns:
            Insight with suggestion, or None
        """
        if context is None:
            context = self.context_engine.get_current_context()

        # Use pattern completer to predict next action
        predictions = self.pattern_completer.predict(context)

        if not predictions.predictions:
            return None

        # Get highest confidence prediction
        top_prediction = predictions.get_top_predictions(1)[0]

        return Insight(
            insight_type=InsightType.HABIT_SUGGESTION,
            title="Suggested Next Step",
            message=f"Based on your patterns, you usually: {top_prediction.predicted_next_step}",
            evidence=[
                f"Pattern: {top_prediction.pattern_name}",
                f"Frequency: {top_prediction.pattern_frequency:.0%}",
                f"Typical delay: {top_prediction.typical_delay_seconds:.0f}s"
            ],
            suggested_action=top_prediction.suggested_action,
            confidence=top_prediction.confidence
        )

    # Internal methods for analysis

    def _detect_workflow_patterns(self, context: Context) -> List[Insight]:
        """Detect patterns in workflow"""
        insights = []

        # Check if user follows test-first development
        recent_cmds = [cmd.command for cmd in context.recent_commands[:10]]
        test_cmds = [cmd for cmd in recent_cmds if "test" in cmd.lower()]
        build_cmds = [cmd for cmd in recent_cmds if "build" in cmd.lower() or "run" in cmd.lower()]

        if test_cmds and build_cmds:
            # Check order
            test_first = any(
                recent_cmds.index(test) < recent_cmds.index(build)
                for test in test_cmds
                for build in build_cmds
                if test in recent_cmds and build in recent_cmds
            )

            if test_first:
                insights.append(Insight(
                    insight_type=InsightType.CELEBRATION,
                    title="Test-First Development",
                    message="You're practicing test-first development - great habit!",
                    evidence=[f"Running tests before builds {len(test_cmds)} times"],
                    confidence=0.8
                ))
            else:
                insights.append(Insight(
                    insight_type=InsightType.HABIT_SUGGESTION,
                    title="Consider Test-First",
                    message="You're running tests after builds. Consider testing first to catch issues earlier.",
                    evidence=[f"Building before testing in recent commands"],
                    suggested_action="Try: Run tests before builds to catch issues faster",
                    confidence=0.7
                ))

        return insights

    def _analyze_success_rates(self, context: Context) -> List[Insight]:
        """Analyze command success rates"""
        insights = []

        if len(context.recent_commands) < 5:
            return insights

        # Calculate success rate
        successes = sum(1 for cmd in context.recent_commands if cmd.success)
        total = len(context.recent_commands)
        success_rate = successes / total

        if success_rate < 0.6:
            insights.append(Insight(
                insight_type=InsightType.WARNING,
                title="Low Success Rate",
                message=f"Your recent commands are only succeeding {success_rate:.0%} of the time.",
                evidence=[
                    f"{successes}/{total} commands successful",
                    "Recent failures may indicate a systemic issue"
                ],
                suggested_action="Would you like me to analyze the errors and suggest fixes?",
                confidence=0.9
            ))
        elif success_rate > 0.9:
            insights.append(Insight(
                insight_type=InsightType.CELEBRATION,
                title="Excellent Success Rate!",
                message=f"You're crushing it! {success_rate:.0%} success rate on recent commands.",
                evidence=[f"{successes}/{total} commands successful"],
                confidence=0.95
            ))

        return insights

    def _detect_flow_state(self, context: Context) -> List[Insight]:
        """Detect if user is in flow state"""
        insights = []

        # Flow indicators:
        # - HIGH_FOCUS session state
        # - Low error rate
        # - Consistent file editing
        # - Rapid command sequences

        if context.session_state == SessionState.HIGH_FOCUS:
            # Calculate session duration
            session_duration = (datetime.now() - context.session_start).total_seconds() / 60

            if session_duration > 30:
                insights.append(Insight(
                    insight_type=InsightType.CELEBRATION,
                    title="Deep Flow State Detected",
                    message=f"You've been in focused flow for {session_duration:.0f} minutes!",
                    evidence=[
                        "HIGH_FOCUS session state",
                        "Consistent work patterns",
                        "High success rate"
                    ],
                    confidence=0.85
                ))

        return insights

    def _identify_growth_opportunities(self, context: Context) -> List[Insight]:
        """Identify opportunities for growth"""
        insights = []

        # Check if user is repeating manual tasks
        cmd_patterns = defaultdict(int)
        for cmd in context.recent_commands:
            # Simplify command to pattern
            pattern = cmd.command.split()[0] if cmd.command else ""
            cmd_patterns[pattern] += 1

        # Find repeated commands
        for pattern, count in cmd_patterns.items():
            if count >= 3 and pattern not in ["cd", "ls", "echo"]:
                insights.append(Insight(
                    insight_type=InsightType.GROWTH_OPPORTUNITY,
                    title="Automation Opportunity",
                    message=f"You've run '{pattern}' {count} times recently.",
                    evidence=[f"Repeated command: {pattern}"],
                    suggested_action=f"Consider creating an alias or script for '{pattern}'",
                    confidence=0.7
                ))

        return insights

    def _generate_celebrations(self, context: Context) -> List[Insight]:
        """Generate celebrations for achievements"""
        insights = []

        # Celebrate learning intent
        if context.current_intent and "learn" in context.current_intent.intent_type.value.lower():
            insights.append(Insight(
                insight_type=InsightType.CELEBRATION,
                title="Love the Learning Spirit!",
                message="You're actively learning new things - that's how we grow!",
                evidence=["Learning-focused intent detected"],
                confidence=0.8
            ))

        return insights


# Global instance
_meta_cognitive_engine: Optional[MetaCognitiveEngine] = None


def get_meta_cognitive_engine() -> MetaCognitiveEngine:
    """Get or create global meta-cognitive engine"""
    global _meta_cognitive_engine

    if _meta_cognitive_engine is None:
        _meta_cognitive_engine = MetaCognitiveEngine()

    return _meta_cognitive_engine
