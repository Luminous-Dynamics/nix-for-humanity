"""Pattern learning from user interactions."""

# === Merged from migration ===

"""
from typing import Dict, Optional
Pattern learning system for user interactions

This module learns from user command patterns to provide better suggestions
and improve the system's understanding over time.
"""

import sqlite3
from pathlib import Path
from typing import Any


class PatternLearner:
    """Learn patterns from user interactions"""

    def __init__(self, data_dir: Path | None = None):
        """
        Initialize pattern learner

        Args:
            data_dir: Directory for storing pattern data
        """
        if data_dir is None:
            data_dir = Path.home() / ".local" / "share" / "nix-for-humanity"

        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = self.data_dir / "patterns.db"
        self._init_database()

    def _init_database(self):
        """Initialize the patterns database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute(
            """
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY,
                pattern_key TEXT NOT NULL UNIQUE,
                input_template TEXT NOT NULL,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                total_count INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0.0,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """
        )

        # Table for specific command instances
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS command_instances (
                id INTEGER PRIMARY KEY,
                pattern_key TEXT NOT NULL,
                raw_input TEXT NOT NULL,
                command_executed TEXT,
                success BOOLEAN,
                execution_time REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pattern_key) REFERENCES patterns(pattern_key)
            )
        """
        )

        conn.commit()
        conn.close()

    def record_pattern(
        self, input_text: str, command: str, success: bool, execution_time: float = 0.0
    ) -> None:
        """
        Record a pattern from user interaction

        Args:
            input_text: Raw user input
            command: Command that was executed
            success: Whether the command succeeded
            execution_time: How long the command took
        """
        pattern_key = self._generate_pattern_key(input_text)

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Update or insert pattern
        c.execute(
            """
            INSERT INTO patterns (pattern_key, input_template, total_count,
                                success_count, failure_count, success_rate)
            VALUES (?, ?, 1, ?, ?, ?)
            ON CONFLICT(pattern_key) DO UPDATE SET
                total_count = total_count + 1,
                success_count = success_count + ?,
                failure_count = failure_count + ?,
                success_rate = CAST(success_count + ? AS REAL) / (total_count + 1),
                last_used = CURRENT_TIMESTAMP
        """,
            (
                pattern_key,
                self._extract_template(input_text),
                1 if success else 0,
                0 if success else 1,
                1.0 if success else 0.0,
                1 if success else 0,
                0 if success else 1,
                1 if success else 0,
            ),
        )

        # Record specific instance
        c.execute(
            """
            INSERT INTO command_instances
            (pattern_key, raw_input, command_executed, success, execution_time)
            VALUES (?, ?, ?, ?, ?)
        """,
            (pattern_key, input_text, command, success, execution_time),
        )

        conn.commit()
        conn.close()

    def get_suggestion(self, input_text: str) -> dict[str, Any] | None:
        """
        Get suggestion based on learned patterns

        Args:
            input_text: User input to analyze

        Returns:
            Suggestion dict with confidence and reasoning, or None
        """
        pattern_key = self._generate_pattern_key(input_text)

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Look for matching pattern
        c.execute(
            """
            SELECT success_rate, total_count, last_used
            FROM patterns
            WHERE pattern_key = ?
        """,
            (pattern_key,),
        )

        result = c.fetchone()

        if result and result[1] >= 3 and result[0] > 0.8:
            # Get most successful recent command
            c.execute(
                """
                SELECT command_executed, COUNT(*) as count
                FROM command_instances
                WHERE pattern_key = ? AND success = 1
                GROUP BY command_executed
                ORDER BY count DESC, timestamp DESC
                LIMIT 1
            """,
                (pattern_key,),
            )

            command_result = c.fetchone()
            conn.close()

            if command_result:
                return {
                    "command": command_result[0],
                    "confidence": result[0],
                    "based_on": result[1],
                    "reasoning": f"This worked {int(result[0]*100)}% of the time in {result[1]} previous attempts",
                }

        conn.close()
        return None

    def get_common_patterns(self, limit: int = 10) -> list:
        """Get most common successful patterns"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute(
            """
            SELECT pattern_key, input_template, success_rate, total_count
            FROM patterns
            WHERE success_rate > 0.7 AND total_count > 2
            ORDER BY total_count DESC, success_rate DESC
            LIMIT ?
        """,
            (limit,),
        )

        patterns = []
        for row in c.fetchall():
            patterns.append(
                {
                    "key": row[0],
                    "template": row[1],
                    "success_rate": row[2],
                    "usage_count": row[3],
                }
            )

        conn.close()
        return patterns

    def _generate_pattern_key(self, input_text: str) -> str:
        """Generate a pattern key from input"""
        # Normalize and extract key words
        words = input_text.lower().split()

        # Look for action words
        action_words = [
            "install",
            "update",
            "remove",
            "show",
            "list",
            "start",
            "stop",
            "restart",
            "enable",
            "disable",
            "search",
            "find",
            "check",
            "clean",
            "build",
        ]

        action = None
        for word in words:
            if word in action_words:
                action = word
                break

        # Look for target (package, service, etc)
        if action:
            # Simple heuristic: word after action is often the target
            try:
                idx = words.index(action)
                if idx + 1 < len(words):
                    target = words[idx + 1]
                    # Generic targets
                    if target in ["a", "the", "my", "some"]:
                        if idx + 2 < len(words):
                            target = words[idx + 2]
                    return f"{action}-{target}"
            except ValueError:
                # TODO: Add proper error handling
                pass  # Silent for now, should log error

        # Fallback: first two meaningful words
        meaningful = [
            w
            for w in words
            if len(w) > 2 and w not in ["the", "and", "for", "with", "from"]
        ]
        if len(meaningful) >= 2:
            return f"{meaningful[0]}-{meaningful[1]}"
        if meaningful:
            return meaningful[0]

        return "unknown"

    def _extract_template(self, input_text: str) -> str:
        """Extract a template from input (for display)"""
        # This could be enhanced with more sophisticated NLP
        return input_text.lower().strip()

    def learn_from_feedback(self, input_text: str, feedback: str) -> None:
        """
        Learn from explicit user feedback

        Args:
            input_text: Original input
            feedback: User feedback (positive/negative/correction)
        """
        pattern_key = self._generate_pattern_key(input_text)

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Store feedback as metadata
        c.execute(
            """
            UPDATE patterns
            SET metadata = json_set(
                COALESCE(metadata, '{}'),
                '$.feedback',
                json_array(json_object(
                    'feedback', ?,
                    'timestamp', datetime('now')
                ))
            )
            WHERE pattern_key = ?
        """,
            (feedback, pattern_key),
        )

        conn.commit()
        conn.close()
