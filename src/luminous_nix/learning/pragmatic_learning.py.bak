"""
Pragmatic Learning System - What We Can Actually Build.

This is the REALISTIC implementation of personalized learning for Nix for Humanity.
Instead of complex Bayesian networks and emotional modeling, we focus on what we
can actually observe and meaningfully improve.

Principles:
1. Only track what we can measure
2. Only infer what we can validate
3. Start simple, evolve gradually
4. Be transparent with users
5. Provide immediate value

Since: v1.1.0 - The Practical Version
"""

import json
import logging
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


# ============================================================================
# SIMPLE, OBSERVABLE TRACKING
# ============================================================================


@dataclass
class CommandPattern:
    """A pattern we've observed in user behavior."""

    pattern_type: str  # "alias", "sequence", "error_recovery"
    trigger: str  # What triggers this pattern
    action: str  # What the user does
    count: int = 1  # How often we've seen it
    confidence: float = 0.0  # How confident we are this is intentional


@dataclass
class UserPreferences:
    """Simple, observable user preferences."""

    # Command aliases (grab → install)
    aliases: dict[str, str] = field(default_factory=dict)

    # Package preferences (editor → vscode)
    package_choices: dict[str, str] = field(default_factory=dict)

    # Common command sequences
    sequences: list[list[str]] = field(default_factory=list)

    # Errors they've encountered and fixed
    error_solutions: dict[str, list[str]] = field(default_factory=dict)

    # When they typically use the system
    active_hours: list[int] = field(default_factory=list)

    # How verbose they want responses
    prefers_detail: bool | None = None

    # Commands they use most
    command_frequency: Counter = field(default_factory=Counter)


class PragmaticLearningSystem:
    """
    A learning system that actually works in production.

    This system:
    - Tracks observable behaviors only
    - Makes conservative inferences
    - Provides immediate value
    - Is completely transparent
    - Respects user privacy

    Since: v1.1.0
    """

    def __init__(self, user_id: str, storage_path: Path | None = None):
        """
        Initialize pragmatic learning system.

        Args:
            user_id: User identifier (can be "default")
            storage_path: Where to store learned preferences
        """
        self.user_id = user_id
        self.storage_path = storage_path or Path.home() / ".nix-humanity" / "learning"
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Simple tracking
        self.preferences = UserPreferences()
        self.recent_commands: list[str] = []
        self.session_start = datetime.now()

        # Learning thresholds (conservative)
        self.ALIAS_THRESHOLD = 3  # See pattern 3 times before suggesting
        self.SEQUENCE_THRESHOLD = 2  # See sequence twice before learning

        # Load existing preferences
        self.load_preferences()

        logger.info(f"Pragmatic learning initialized for user: {user_id}")

    # ========================================================================
    # SIMPLE OBSERVATION METHODS
    # ========================================================================

    def observe_command(self, command: str, success: bool, error: str | None = None):
        """
        Observe a command execution - the core learning input.

        Args:
            command: The command/query the user entered
            success: Whether it succeeded
            error: Error message if it failed
        """
        # Track command frequency
        self.preferences.command_frequency[command] += 1

        # Track active hours
        current_hour = datetime.now().hour
        if current_hour not in self.preferences.active_hours:
            self.preferences.active_hours.append(current_hour)

        # Track command sequence
        self.recent_commands.append(command)
        if len(self.recent_commands) > 10:
            self.recent_commands.pop(0)

        # Learn from patterns - only learn aliases from failed→success patterns
        if success and len(self.recent_commands) >= 2:
            # Check if previous command failed with similar structure
            self._learn_from_correction(command)

        self._learn_sequences()

        # Learn from errors
        if not success and error:
            self._track_error(command, error)
            self._last_failed_command = command  # Track for learning from correction
        elif success and hasattr(self, "_last_error"):
            # They fixed an error!
            self._learn_error_recovery(command)

        # Persist every 10 commands
        if sum(self.preferences.command_frequency.values()) % 10 == 0:
            self.save_preferences()

    def _learn_from_correction(self, successful_command: str):
        """
        Learn when user corrects themselves.

        Example: "grab firefox" (fails) → "install firefox" (succeeds)
        Learn: "grab" means "install"
        """
        if not hasattr(self, "_last_failed_command"):
            return

        failed = self._last_failed_command.lower().split()
        succeeded = successful_command.lower().split()

        # Same structure but one word different?
        if len(failed) == len(succeeded):
            differences = [
                (f, s) for f, s in zip(failed, succeeded, strict=False) if f != s
            ]

            # Exactly one word different - this is the alias
            if len(differences) == 1:
                user_word, correct_word = differences[0]

                # Track this correction
                if user_word not in ["the", "a", "an"]:
                    self._track_potential_alias(user_word, correct_word)

    def _learn_aliases(self, command: str):
        """
        Learn command aliases from usage patterns.

        Example: User types "grab firefox" then "install firefox"
        We learn: "grab" might mean "install"
        """
        words = command.lower().split()

        # Look for potential aliases in recent commands
        for recent_cmd in self.recent_commands[-3:]:
            recent_words = recent_cmd.lower().split()

            # Same structure but one word different?
            if len(words) == len(recent_words):
                differences = [
                    (w1, w2)
                    for w1, w2 in zip(words, recent_words, strict=False)
                    if w1 != w2
                ]

                # Exactly one word different - potential alias
                if len(differences) == 1:
                    word1, word2 = differences[0]

                    # Track this potential alias
                    if word1 not in ["the", "a", "an"]:  # Skip articles
                        self._track_potential_alias(word1, word2)

    def _track_potential_alias(self, user_word: str, system_word: str):
        """
        Track a potential alias relationship.

        Only suggest after seeing it multiple times.
        """
        # Simple tracking with threshold
        key = f"{user_word}->{system_word}"

        if not hasattr(self, "_alias_candidates"):
            self._alias_candidates = defaultdict(int)

        self._alias_candidates[key] += 1

        # Suggest after threshold
        if self._alias_candidates[key] == self.ALIAS_THRESHOLD:
            logger.info(f"Learned potential alias: '{user_word}' → '{system_word}'")
            self.preferences.aliases[user_word] = system_word

    def _learn_sequences(self):
        """
        Learn common command sequences.

        Example: User often runs "nix-collect-garbage" after "nixos-rebuild"
        """
        if len(self.recent_commands) >= 2:
            # Look at last 2 commands as a potential sequence
            sequence = self.recent_commands[-2:]

            # Have we seen this sequence before?
            sequence_str = " -> ".join(sequence)

            if not hasattr(self, "_sequence_counts"):
                self._sequence_counts = defaultdict(int)

            self._sequence_counts[sequence_str] += 1

            # Learn after threshold
            if self._sequence_counts[sequence_str] == self.SEQUENCE_THRESHOLD:
                logger.info(f"Learned command sequence: {sequence_str}")
                self.preferences.sequences.append(sequence)

    def _track_error(self, command: str, error: str):
        """Track an error for potential learning."""
        self._last_error = error
        self._error_command = command
        self._recovery_attempts = []

    def _learn_error_recovery(self, success_command: str):
        """
        Learn how the user recovered from an error.

        This is GOLD - actual problem-solving patterns!
        """
        if hasattr(self, "_last_error"):
            error_key = self._last_error[:50]  # First 50 chars as key

            if error_key not in self.preferences.error_solutions:
                self.preferences.error_solutions[error_key] = []

            solution = {
                "failed_command": self._error_command,
                "solution": success_command,
                "attempts": self._recovery_attempts,
            }

            self.preferences.error_solutions[error_key].append(success_command)
            logger.info(
                f"Learned error recovery: {error_key[:30]}... → {success_command}"
            )

            # Clean up
            delattr(self, "_last_error")
            delattr(self, "_error_command")
            self._recovery_attempts = []

    # ========================================================================
    # SIMPLE ASSISTANCE METHODS
    # ========================================================================

    def suggest_alias(self, command: str) -> str | None:
        """
        Suggest an alias if we've learned one.

        Returns:
            Suggested improvement or None
        """
        words = command.lower().split()

        for user_word, system_word in self.preferences.aliases.items():
            if user_word in words:
                suggested = command.replace(user_word, system_word)
                return f"Did you mean: {suggested}?"

        return None

    def suggest_next_command(self, last_command: str) -> str | None:
        """
        Suggest the next command based on learned sequences.

        Returns:
            Suggested next command or None
        """
        for sequence in self.preferences.sequences:
            if len(sequence) >= 2 and sequence[0] == last_command:
                return f"You often run next: {sequence[1]}"

        return None

    def suggest_error_fix(self, error: str) -> str | None:
        """
        Suggest a fix based on previous error recoveries.

        Returns:
            Suggested solution or None
        """
        # Look for similar errors
        error_key = error[:50]

        if error_key in self.preferences.error_solutions:
            solutions = self.preferences.error_solutions[error_key]
            if solutions:
                return f"This worked before: {solutions[-1]}"

        # Partial match
        for key, solutions in self.preferences.error_solutions.items():
            if key in error or error in key:
                if solutions:
                    return f"Similar error fixed with: {solutions[-1]}"

        return None

    def get_verbosity_preference(self) -> str:
        """
        Determine verbosity preference from behavior.

        Returns:
            "detailed", "normal", or "concise"
        """
        # Simple heuristic: frequent users want concise
        total_commands = sum(self.preferences.command_frequency.values())

        if total_commands < 10:
            return "detailed"  # New user - be helpful
        if total_commands < 50:
            return "normal"  # Learning - balanced
        return "concise"  # Experienced - be quick

    def get_active_hours_summary(self) -> str:
        """
        Summarize when the user is typically active.

        Returns:
            Human-readable summary
        """
        if not self.preferences.active_hours:
            return "No usage pattern detected yet"

        hours = sorted(self.preferences.active_hours)

        # Find continuous ranges
        ranges = []
        start = hours[0]
        end = hours[0]

        for hour in hours[1:]:
            if hour == end + 1:
                end = hour
            else:
                ranges.append((start, end))
                start = end = hour
        ranges.append((start, end))

        # Format nicely
        range_strs = []
        for start, end in ranges:
            if start == end:
                range_strs.append(f"{start}:00")
            else:
                range_strs.append(f"{start}:00-{end}:00")

        return f"Usually active: {', '.join(range_strs)}"

    # ========================================================================
    # TRANSPARENCY METHODS
    # ========================================================================

    def get_learning_summary(self) -> dict[str, any]:
        """
        Get a transparent summary of what we've learned.

        This is shown to the user so they understand what we track.
        """
        return {
            "user_id": self.user_id,
            "learning_enabled": True,
            "data_stored_locally": True,
            "can_delete_anytime": True,
            "learned_patterns": {
                "aliases": dict(self.preferences.aliases),
                "common_sequences": [
                    " → ".join(seq) for seq in self.preferences.sequences[:5]
                ],
                "error_fixes": len(self.preferences.error_solutions),
                "total_commands": sum(self.preferences.command_frequency.values()),
            },
            "top_commands": dict(self.preferences.command_frequency.most_common(5)),
            "usage_pattern": self.get_active_hours_summary(),
            "current_preference": {"verbosity": self.get_verbosity_preference()},
            "storage_location": str(self.storage_path / f"{self.user_id}.json"),
            "delete_command": "ask-nix --delete-learning-data",
        }

    def export_learnings(self) -> str:
        """
        Export learnings in a readable format.

        Users can see exactly what we've learned about them.
        """
        summary = self.get_learning_summary()

        output = ["=== Your Nix Learning Profile ===\n"]

        # Aliases
        if summary["learned_patterns"]["aliases"]:
            output.append("Learned Aliases:")
            for user_word, system_word in summary["learned_patterns"][
                "aliases"
            ].items():
                output.append(f"  '{user_word}' → '{system_word}'")
            output.append("")

        # Sequences
        if summary["learned_patterns"]["common_sequences"]:
            output.append("Command Patterns:")
            for seq in summary["learned_patterns"]["common_sequences"]:
                output.append(f"  {seq}")
            output.append("")

        # Top commands
        if summary["top_commands"]:
            output.append("Most Used Commands:")
            for cmd, count in summary["top_commands"].items():
                output.append(f"  {cmd}: {count} times")
            output.append("")

        # Usage pattern
        output.append(summary["usage_pattern"])
        output.append("")

        # Footer
        output.append(
            f"Total commands tracked: {summary['learned_patterns']['total_commands']}"
        )
        output.append(f"Data stored at: {summary['storage_location']}")
        output.append("\nTo delete this data, run: ask-nix --delete-learning-data")

        return "\n".join(output)

    # ========================================================================
    # PERSISTENCE
    # ========================================================================

    def save_preferences(self):
        """Save preferences to disk."""
        save_file = self.storage_path / f"{self.user_id}.json"

        # Convert to serializable format
        data = {
            "version": "1.1.0",
            "user_id": self.user_id,
            "preferences": {
                "aliases": self.preferences.aliases,
                "package_choices": self.preferences.package_choices,
                "sequences": self.preferences.sequences,
                "error_solutions": self.preferences.error_solutions,
                "active_hours": self.preferences.active_hours,
                "command_frequency": dict(self.preferences.command_frequency),
            },
            "last_updated": datetime.now().isoformat(),
        }

        with open(save_file, "w") as f:
            json.dump(data, f, indent=2)

        logger.debug(f"Saved preferences for {self.user_id}")

    def load_preferences(self):
        """Load preferences from disk."""
        load_file = self.storage_path / f"{self.user_id}.json"

        if not load_file.exists():
            logger.info(f"No existing preferences for {self.user_id}")
            return

        try:
            with open(load_file) as f:
                data = json.load(f)

            prefs = data.get("preferences", {})

            self.preferences.aliases = prefs.get("aliases", {})
            self.preferences.package_choices = prefs.get("package_choices", {})
            self.preferences.sequences = prefs.get("sequences", [])
            self.preferences.error_solutions = prefs.get("error_solutions", {})
            self.preferences.active_hours = prefs.get("active_hours", [])
            self.preferences.command_frequency = Counter(
                prefs.get("command_frequency", {})
            )

            logger.info(f"Loaded preferences for {self.user_id}")

        except Exception as e:
            logger.error(f"Failed to load preferences: {e}")

    def delete_all_data(self):
        """
        Delete all learned data for this user.

        Complete privacy control - user can reset anytime.
        """
        save_file = self.storage_path / f"{self.user_id}.json"

        if save_file.exists():
            save_file.unlink()
            logger.info(f"Deleted all learning data for {self.user_id}")

        # Reset in memory
        self.preferences = UserPreferences()
        self.recent_commands = []

        return "All learning data has been deleted."


# ============================================================================
# SIMPLE USAGE EXAMPLE
# ============================================================================


def example_usage():
    """Show how the pragmatic system works."""

    # Initialize
    learning = PragmaticLearningSystem("demo_user")

    # Simulate realistic usage
    commands = [
        ("grab firefox", False, "unknown command"),
        ("install firefox", True, None),
        ("grab vscode", False, "unknown command"),
        ("install vscode", True, None),
        ("grab neovim", False, "unknown command"),
        ("install neovim", True, None),
        # Now it should learn "grab" → "install"
        ("nixos-rebuild switch", True, None),
        ("nix-collect-garbage", True, None),
        ("nixos-rebuild switch", True, None),
        ("nix-collect-garbage", True, None),
        # Should learn this sequence
    ]

    print("🧠 Pragmatic Learning System Demo\n")
    print("Simulating user commands...\n")

    for cmd, success, error in commands:
        learning.observe_command(cmd, success, error)

        # Check for suggestions
        alias_suggestion = learning.suggest_alias(cmd)
        if alias_suggestion:
            print(f"💡 {alias_suggestion}")

        if success and learning.recent_commands:
            next_suggestion = learning.suggest_next_command(
                learning.recent_commands[-1]
            )
            if next_suggestion:
                print(f"🔮 {next_suggestion}")

    # Show what we learned
    print("\n" + "=" * 50)
    print(learning.export_learnings())

    # Show transparency
    print("\n" + "=" * 50)
    print("📊 Learning Summary (User-Visible):")
    summary = learning.get_learning_summary()
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    example_usage()
