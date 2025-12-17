"""
Proactive Learning & Assistance
Anticipates user needs and offers help before asked

Features:
1. Pattern recognition in user behavior
2. Need prediction based on context
3. Proactive suggestions and assistance
4. Non-intrusive notifications
"""

import asyncio
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)


@dataclass
class UserAction:
    """A single user action"""
    action_type: str  # 'query', 'command', 'error', 'success'
    content: str
    timestamp: datetime
    context: Dict = field(default_factory=dict)
    success: bool = True


@dataclass
class Pattern:
    """A detected behavior pattern"""
    pattern_id: str
    pattern_type: str  # 'sequence', 'frequency', 'time_based', 'error_prone'
    description: str
    actions: List[UserAction]
    frequency: int
    confidence: float
    first_seen: datetime
    last_seen: datetime


@dataclass
class PredictedNeed:
    """A predicted user need"""
    need_id: str
    observation: str
    suggested_action: str
    reasoning: str
    confidence: float
    urgency: str  # 'low', 'medium', 'high'
    category: str  # 'optimization', 'prevention', 'learning', 'automation'
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class UserContext:
    """Current user context"""
    user_id: str
    current_working_directory: Optional[str] = None
    recent_actions: List[UserAction] = field(default_factory=list)
    active_errors: List[str] = field(default_factory=list)
    installed_packages: Set[str] = field(default_factory=set)
    system_state: Dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class ContextMonitor:
    """Monitors user context and activity"""

    def __init__(self, history_size: int = 100):
        self.user_contexts: Dict[str, UserContext] = {}
        self.action_history: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=history_size)
        )

    async def get_current(self, user_id: str) -> UserContext:
        """Get current user context"""

        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = UserContext(user_id=user_id)

        context = self.user_contexts[user_id]

        # Update recent actions
        context.recent_actions = list(self.action_history[user_id])[-20:]

        return context

    def record_action(self, user_id: str, action: UserAction) -> None:
        """Record a user action"""
        self.action_history[user_id].append(action)

        # Update context
        if user_id in self.user_contexts:
            context = self.user_contexts[user_id]

            # Track errors
            if action.action_type == 'error':
                context.active_errors.append(action.content)
            elif action.action_type == 'success' and context.active_errors:
                # Clear errors on success
                context.active_errors.clear()

            # Update timestamp
            context.timestamp = datetime.now()


class PatternDetector:
    """Detects patterns in user behavior"""

    def __init__(self, min_frequency: int = 3):
        self.min_frequency = min_frequency
        self.detected_patterns: Dict[str, List[Pattern]] = defaultdict(list)

    def analyze(self, context: UserContext) -> List[Pattern]:
        """Analyze context and detect patterns"""

        patterns = []

        # Pattern 1: Repeated sequences
        sequence_patterns = self._detect_sequences(context)
        patterns.extend(sequence_patterns)

        # Pattern 2: High-frequency actions
        frequency_patterns = self._detect_frequency(context)
        patterns.extend(frequency_patterns)

        # Pattern 3: Time-based patterns
        time_patterns = self._detect_time_patterns(context)
        patterns.extend(time_patterns)

        # Pattern 4: Error-prone actions
        error_patterns = self._detect_error_patterns(context)
        patterns.extend(error_patterns)

        # Update detected patterns for user
        self.detected_patterns[context.user_id] = patterns

        return patterns

    def _detect_sequences(self, context: UserContext) -> List[Pattern]:
        """Detect repeated action sequences"""

        patterns = []
        actions = context.recent_actions

        if len(actions) < 3:
            return patterns

        # Look for 2-3 action sequences
        for seq_len in [2, 3]:
            sequences = defaultdict(int)

            for i in range(len(actions) - seq_len + 1):
                seq = tuple(a.action_type for a in actions[i:i+seq_len])
                sequences[seq] += 1

            # Find frequent sequences
            for seq, count in sequences.items():
                if count >= self.min_frequency:
                    pattern = Pattern(
                        pattern_id=f"seq_{'-'.join(seq)}",
                        pattern_type='sequence',
                        description=f"User often does: {' → '.join(seq)}",
                        actions=actions,
                        frequency=count,
                        confidence=min(count / 10.0, 1.0),
                        first_seen=actions[0].timestamp,
                        last_seen=actions[-1].timestamp,
                    )
                    patterns.append(pattern)

        return patterns

    def _detect_frequency(self, context: UserContext) -> List[Pattern]:
        """Detect high-frequency actions"""

        patterns = []
        actions = context.recent_actions

        if not actions:
            return patterns

        # Count action types
        action_counts = defaultdict(int)
        for action in actions:
            action_counts[action.action_type] += 1

        # Find high-frequency actions
        for action_type, count in action_counts.items():
            if count >= self.min_frequency:
                pattern = Pattern(
                    pattern_id=f"freq_{action_type}",
                    pattern_type='frequency',
                    description=f"User frequently performs: {action_type}",
                    actions=[a for a in actions if a.action_type == action_type],
                    frequency=count,
                    confidence=min(count / 20.0, 1.0),
                    first_seen=actions[0].timestamp,
                    last_seen=actions[-1].timestamp,
                )
                patterns.append(pattern)

        return patterns

    def _detect_time_patterns(self, context: UserContext) -> List[Pattern]:
        """Detect time-based patterns"""

        patterns = []
        actions = context.recent_actions

        if len(actions) < 5:
            return patterns

        # Group actions by hour of day
        hour_counts = defaultdict(int)
        for action in actions:
            hour = action.timestamp.hour
            hour_counts[hour] += 1

        # Find peak hours
        if hour_counts:
            max_count = max(hour_counts.values())
            peak_hours = [h for h, c in hour_counts.items() if c == max_count]

            if max_count >= 3:
                pattern = Pattern(
                    pattern_id=f"time_peak_{peak_hours[0]}",
                    pattern_type='time_based',
                    description=f"User most active around {peak_hours[0]:02d}:00",
                    actions=actions,
                    frequency=max_count,
                    confidence=0.7,
                    first_seen=actions[0].timestamp,
                    last_seen=actions[-1].timestamp,
                )
                patterns.append(pattern)

        return patterns

    def _detect_error_patterns(self, context: UserContext) -> List[Pattern]:
        """Detect error-prone actions"""

        patterns = []
        actions = context.recent_actions

        # Find actions followed by errors
        error_prone = defaultdict(int)

        for i in range(len(actions) - 1):
            current = actions[i]
            next_action = actions[i + 1]

            if next_action.action_type == 'error':
                error_prone[current.action_type] += 1

        # Find frequently error-prone actions
        for action_type, error_count in error_prone.items():
            if error_count >= 2:
                pattern = Pattern(
                    pattern_id=f"error_{action_type}",
                    pattern_type='error_prone',
                    description=f"Action '{action_type}' often leads to errors",
                    actions=[a for a in actions if a.action_type == action_type],
                    frequency=error_count,
                    confidence=min(error_count / 5.0, 1.0),
                    first_seen=actions[0].timestamp,
                    last_seen=actions[-1].timestamp,
                )
                patterns.append(pattern)

        return patterns


class NeedPredictor:
    """Predicts user needs based on patterns"""

    def __init__(self):
        self.prediction_rules: List[Dict] = self._initialize_rules()

    def _initialize_rules(self) -> List[Dict]:
        """Initialize prediction rules"""

        return [
            # Rule 1: Frequent package installs → suggest flake
            {
                'pattern_type': 'frequency',
                'action_contains': 'install',
                'min_frequency': 5,
                'prediction': {
                    'observation': 'you install packages frequently',
                    'suggested_action': 'create a reusable development environment flake',
                    'category': 'automation',
                    'urgency': 'low',
                }
            },

            # Rule 2: Repeated errors → offer explanation
            {
                'pattern_type': 'error_prone',
                'min_frequency': 2,
                'prediction': {
                    'observation': "you're encountering repeated errors",
                    'suggested_action': 'explain what\'s happening and how to prevent it',
                    'category': 'learning',
                    'urgency': 'medium',
                }
            },

            # Rule 3: Sequential actions → suggest script
            {
                'pattern_type': 'sequence',
                'min_frequency': 3,
                'prediction': {
                    'observation': 'you perform the same sequence of actions repeatedly',
                    'suggested_action': 'create a script or alias to automate this',
                    'category': 'optimization',
                    'urgency': 'low',
                }
            },

            # Rule 4: Manual configuration → suggest module
            {
                'pattern_type': 'frequency',
                'action_contains': 'configure',
                'min_frequency': 3,
                'prediction': {
                    'observation': 'you configure this manually often',
                    'suggested_action': 'use a NixOS module for easier management',
                    'category': 'optimization',
                    'urgency': 'low',
                }
            },
        ]

    def predict(self, patterns: List[Pattern]) -> List[PredictedNeed]:
        """Predict needs based on detected patterns"""

        predictions = []

        for pattern in patterns:
            # Check each prediction rule
            for rule in self.prediction_rules:
                if self._matches_rule(pattern, rule):
                    prediction = self._create_prediction(pattern, rule)
                    predictions.append(prediction)

        return predictions

    def _matches_rule(self, pattern: Pattern, rule: Dict) -> bool:
        """Check if pattern matches a prediction rule"""

        # Check pattern type
        if rule.get('pattern_type') and pattern.pattern_type != rule['pattern_type']:
            return False

        # Check frequency
        if rule.get('min_frequency') and pattern.frequency < rule['min_frequency']:
            return False

        # Check action content
        if rule.get('action_contains'):
            contains = rule['action_contains'].lower()
            matches = any(contains in action.content.lower() for action in pattern.actions)
            if not matches:
                return False

        return True

    def _create_prediction(self, pattern: Pattern, rule: Dict) -> PredictedNeed:
        """Create a prediction from pattern and rule"""

        pred_template = rule['prediction']

        prediction = PredictedNeed(
            need_id=f"pred_{pattern.pattern_id}_{datetime.now().timestamp()}",
            observation=pred_template['observation'],
            suggested_action=pred_template['suggested_action'],
            reasoning=f"Based on pattern: {pattern.description}",
            confidence=pattern.confidence,
            urgency=pred_template['urgency'],
            category=pred_template['category'],
        )

        return prediction


class ProactiveAssistant:
    """
    Anticipates user needs and offers proactive assistance

    Features:
    - Monitors user context continuously
    - Detects behavioral patterns
    - Predicts future needs
    - Offers non-intrusive suggestions
    """

    def __init__(
        self,
        confidence_threshold: float = 0.65,
        check_interval_seconds: int = 30,
    ):
        self.context_monitor = ContextMonitor()
        self.pattern_detector = PatternDetector()
        self.need_predictor = NeedPredictor()

        self.confidence_threshold = confidence_threshold
        self.check_interval = check_interval_seconds

        # Track what we've already suggested
        self.suggested_needs: Dict[str, Set[str]] = defaultdict(set)

        # Notification queue
        self.notification_queue: Dict[str, List[PredictedNeed]] = defaultdict(list)

    async def monitor_and_assist(self, user_id: str) -> None:
        """
        Continuously monitor user and offer proactive assistance

        This is the main loop that runs in the background
        """

        logger.info(f"Starting proactive monitoring for user {user_id}")

        try:
            while True:
                # Get current context
                context = await self.context_monitor.get_current(user_id)

                # Detect patterns
                patterns = self.pattern_detector.analyze(context)

                # Predict needs
                predicted_needs = self.need_predictor.predict(patterns)

                # Filter high-confidence predictions
                actionable_needs = [
                    need for need in predicted_needs
                    if need.confidence >= self.confidence_threshold
                ]

                # Offer assistance for new predictions
                for need in actionable_needs:
                    # Check if we've already suggested this
                    need_key = f"{need.category}:{need.observation}"

                    if need_key not in self.suggested_needs[user_id]:
                        await self._offer_assistance(user_id, need)
                        self.suggested_needs[user_id].add(need_key)

                # Wait before next check
                await asyncio.sleep(self.check_interval)

        except asyncio.CancelledError:
            logger.info(f"Proactive monitoring stopped for user {user_id}")
        except Exception as e:
            logger.error(f"Proactive monitoring error for {user_id}: {e}")

    async def _offer_assistance(self, user_id: str, need: PredictedNeed) -> None:
        """Offer proactive assistance to user"""

        # Create notification message
        urgency_emoji = {
            'low': '💡',
            'medium': '⚡',
            'high': '🚨',
        }

        emoji = urgency_emoji.get(need.urgency, '💡')

        message = f"""
{emoji} I noticed {need.observation}

Would you like me to {need.suggested_action}?

(This is based on your patterns: {need.reasoning})
        """.strip()

        logger.info(f"Proactive suggestion for {user_id}: {need.observation}")

        # Add to notification queue
        self.notification_queue[user_id].append(need)

        # In a real system, this would send a notification
        # For now, just log it
        await self._notify(user_id, message, need.urgency)

    async def _notify(self, user_id: str, message: str, urgency: str) -> None:
        """Send notification to user (non-intrusive)"""

        # In a real implementation, this would:
        # - Send desktop notification
        # - Add to TUI notification area
        # - Queue for next interaction
        # - Respect user's notification preferences

        logger.info(f"[{urgency.upper()}] Notification for {user_id}:")
        logger.info(message)

    def record_action(self, user_id: str, action: UserAction) -> None:
        """Record user action for pattern detection"""
        self.context_monitor.record_action(user_id, action)

    def get_pending_notifications(self, user_id: str) -> List[PredictedNeed]:
        """Get pending notifications for user"""
        return self.notification_queue.get(user_id, [])

    def clear_notifications(self, user_id: str) -> None:
        """Clear notifications for user"""
        if user_id in self.notification_queue:
            self.notification_queue[user_id].clear()


# Example usage
async def example_proactive_assistance():
    """Demonstrate proactive assistance"""

    assistant = ProactiveAssistant(
        confidence_threshold=0.65,
        check_interval_seconds=5,  # Fast for demo
    )

    user_id = "user123"

    # Start monitoring in background
    monitor_task = asyncio.create_task(
        assistant.monitor_and_assist(user_id)
    )

    # Simulate user actions
    actions = [
        UserAction('query', 'install vim', datetime.now()),
        UserAction('query', 'install git', datetime.now()),
        UserAction('query', 'install curl', datetime.now()),
        UserAction('query', 'install wget', datetime.now()),
        UserAction('query', 'install htop', datetime.now()),
    ]

    for action in actions:
        assistant.record_action(user_id, action)
        await asyncio.sleep(1)

    # Let it detect patterns and make suggestions
    await asyncio.sleep(10)

    # Check notifications
    notifications = assistant.get_pending_notifications(user_id)
    print(f"\n🔮 Proactive Suggestions ({len(notifications)}):")
    for notif in notifications:
        print(f"   [{notif.category}] {notif.observation}")
        print(f"   → {notif.suggested_action}")
        print(f"   Confidence: {notif.confidence:.2%}\n")

    # Cancel monitoring
    monitor_task.cancel()
    try:
        await monitor_task
    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    asyncio.run(example_proactive_assistance())
