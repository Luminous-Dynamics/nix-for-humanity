"""
Pattern Completer - Learns and predicts your workflow patterns

Observes how you work and predicts what you'll do next.

Examples:
- "You usually run tests after building"
- "You typically commit after formatting"
- "You often search for docs after installing"
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import logging

from ..context import get_context_engine
from .types import PatternPrediction, PredictionType, PredictionBatch

logger = logging.getLogger(__name__)


class PatternCompleter:
    """
    Learns workflow patterns and predicts next actions

    Strategies:
    1. Command sequence learning (A → B patterns)
    2. Frequency-based predictions
    3. Time-based patterns (morning vs evening)
    4. Context-based predictions
    """

    def __init__(self):
        """Initialize the pattern completer"""
        self.context_engine = get_context_engine()

        # Common workflow patterns (pre-programmed)
        self.known_patterns = {
            "build_then_test": {
                "trigger": ["cargo build", "npm build", "make build"],
                "next_action": "run tests",
                "next_commands": ["cargo test", "npm test", "make test"],
                "confidence": 0.8,
                "frequency": 0.75,
                "typical_delay": 5.0,  # seconds
            },
            "commit_then_push": {
                "trigger": ["git commit"],
                "next_action": "push to remote",
                "next_commands": ["git push"],
                "confidence": 0.85,
                "frequency": 0.85,
                "typical_delay": 3.0,
            },
            "add_then_commit": {
                "trigger": ["git add"],
                "next_action": "commit changes",
                "next_commands": ["git commit"],
                "confidence": 0.9,
                "frequency": 0.9,
                "typical_delay": 10.0,
            },
            "install_then_try": {
                "trigger": ["nix-shell -p", "npm install", "pip install"],
                "next_action": "try the new package",
                "next_commands": ["<package_name> --help", "<package_name> --version"],
                "confidence": 0.7,
                "frequency": 0.6,
                "typical_delay": 5.0,
            },
            "search_then_install": {
                "trigger": ["nix search", "npm search"],
                "next_action": "install found package",
                "next_commands": ["nix-shell -p", "npm install"],
                "confidence": 0.75,
                "frequency": 0.7,
                "typical_delay": 15.0,
            },
            "format_then_commit": {
                "trigger": ["rustfmt", "black", "prettier"],
                "next_action": "commit formatted code",
                "next_commands": ["git add", "git commit"],
                "confidence": 0.8,
                "frequency": 0.75,
                "typical_delay": 5.0,
            },
            "config_then_rebuild": {
                "trigger": ["vim configuration.nix", "nano configuration.nix"],
                "next_action": "rebuild system",
                "next_commands": ["sudo nixos-rebuild switch"],
                "confidence": 0.85,
                "frequency": 0.9,
                "typical_delay": 20.0,
            },
        }

        # Learned patterns (would be persisted in production)
        self.learned_sequences: Dict[str, List[str]] = defaultdict(list)
        self.sequence_counts: Dict[Tuple[str, str], int] = Counter()
        self.sequence_delays: Dict[Tuple[str, str], List[float]] = defaultdict(list)

    def predict(self, context=None) -> PredictionBatch:
        """
        Predict next actions based on patterns

        Args:
            context: Optional context (uses current if None)

        Returns:
            PredictionBatch with pattern predictions
        """
        if context is None:
            context = self.context_engine.get_current_context()

        batch = PredictionBatch(
            context_summary="Analyzing workflow patterns"
        )

        # Predict from known patterns
        batch = self._predict_from_known_patterns(context, batch)

        # Predict from learned patterns
        batch = self._predict_from_learned_patterns(context, batch)

        # Learn from current sequence
        self._learn_from_context(context)

        return batch

    def _predict_from_known_patterns(
        self,
        context,
        batch: PredictionBatch
    ) -> PredictionBatch:
        """Predict based on pre-programmed patterns"""
        if not context.recent_commands:
            return batch

        # Get the last command
        last_cmd = context.recent_commands[0]
        last_cmd_text = last_cmd.command

        # Check each known pattern
        for pattern_name, pattern in self.known_patterns.items():
            # Check if last command triggers this pattern
            triggered = any(
                trigger in last_cmd_text
                for trigger in pattern["trigger"]
            )

            if triggered:
                # Calculate time since last command
                time_since_last = (datetime.now() - last_cmd.timestamp).total_seconds()

                # Adjust confidence based on timing
                confidence = pattern["confidence"]
                if time_since_last < pattern["typical_delay"] * 2:
                    # Within expected timeframe - boost confidence
                    confidence = min(confidence * 1.1, 1.0)

                # Get next commands
                next_commands = pattern["next_commands"]
                next_action = pattern["next_action"]

                prediction = PatternPrediction(
                    prediction_type=PredictionType.PATTERN,
                    confidence=confidence,
                    confidence_level=None,
                    title=f"You usually '{next_action}' next",
                    description=f"Based on '{pattern_name}' pattern",
                    evidence=[
                        f"Last command: {last_cmd_text}",
                        f"Pattern frequency: {pattern['frequency']:.0%}",
                        f"Typical delay: {pattern['typical_delay']:.0f}s",
                    ],
                    pattern_name=pattern_name,
                    pattern_frequency=pattern["frequency"],
                    last_step_observed=last_cmd_text,
                    predicted_next_step=next_action,
                    typical_delay_seconds=pattern["typical_delay"],
                    suggested_action=f"Try: {next_commands[0]}" if next_commands else None,
                )
                batch.add(prediction)

        return batch

    def _predict_from_learned_patterns(
        self,
        context,
        batch: PredictionBatch
    ) -> PredictionBatch:
        """Predict based on learned user-specific patterns"""
        if not context.recent_commands or len(self.sequence_counts) == 0:
            return batch

        # Get last command
        last_cmd = context.recent_commands[0].command

        # Simplify command for matching
        last_cmd_simple = self._simplify_command(last_cmd)

        # Find sequences that start with this command
        matching_sequences = [
            (cmd1, cmd2, count)
            for (cmd1, cmd2), count in self.sequence_counts.items()
            if cmd1 == last_cmd_simple
        ]

        if not matching_sequences:
            return batch

        # Sort by frequency
        matching_sequences.sort(key=lambda x: x[2], reverse=True)

        # Take top prediction
        _, next_cmd, count = matching_sequences[0]

        # Calculate frequency
        total_times_seen = sum(
            c for (c1, _), c in self.sequence_counts.items()
            if c1 == last_cmd_simple
        )
        frequency = count / total_times_seen if total_times_seen > 0 else 0.0

        # Calculate average delay
        delays = self.sequence_delays.get((last_cmd_simple, next_cmd), [5.0])
        avg_delay = sum(delays) / len(delays) if delays else 5.0

        if frequency >= 0.5:  # Only predict if pattern is strong enough
            prediction = PatternPrediction(
                prediction_type=PredictionType.PATTERN,
                confidence=min(frequency, 0.95),
                confidence_level=None,
                title=f"You usually run '{next_cmd}' next",
                description=f"Learned from your workflow",
                evidence=[
                    f"Last command: {last_cmd}",
                    f"Seen this sequence {count} times",
                    f"Success rate: {frequency:.0%}",
                ],
                pattern_name="learned_sequence",
                pattern_frequency=frequency,
                last_step_observed=last_cmd,
                predicted_next_step=next_cmd,
                typical_delay_seconds=avg_delay,
                suggested_action=f"Run: {next_cmd}",
            )
            batch.add(prediction)

        return batch

    def _learn_from_context(self, context):
        """Learn patterns from recent command history"""
        if not context.recent_commands or len(context.recent_commands) < 2:
            return

        # Look at last N commands to find sequences
        recent = context.recent_commands[:10]

        for i in range(len(recent) - 1):
            cmd1 = self._simplify_command(recent[i].command)
            cmd2 = self._simplify_command(recent[i + 1].command)

            # Record the sequence
            self.learned_sequences[cmd1].append(cmd2)
            self.sequence_counts[(cmd1, cmd2)] += 1

            # Record timing
            time_diff = (recent[i].timestamp - recent[i + 1].timestamp).total_seconds()
            if time_diff > 0:  # Sanity check
                self.sequence_delays[(cmd1, cmd2)].append(abs(time_diff))

    @staticmethod
    def _simplify_command(cmd: str) -> str:
        """
        Simplify command for pattern matching

        Examples:
        - "git commit -m 'message'" → "git commit"
        - "cargo build --release" → "cargo build"
        """
        # Take first 2-3 words
        parts = cmd.split()
        if len(parts) >= 2:
            return " ".join(parts[:2])
        return cmd

    def get_pattern_statistics(self) -> Dict:
        """Get statistics about learned patterns"""
        return {
            "total_sequences_learned": len(self.sequence_counts),
            "unique_commands_seen": len(self.learned_sequences),
            "most_common_sequence": self.sequence_counts.most_common(1)[0] if self.sequence_counts else None,
        }


# Global instance
_pattern_completer: Optional[PatternCompleter] = None


def get_pattern_completer() -> PatternCompleter:
    """Get or create global pattern completer"""
    global _pattern_completer

    if _pattern_completer is None:
        _pattern_completer = PatternCompleter()

    return _pattern_completer
