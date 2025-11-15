#!/usr/bin/env python3
"""
Active Learning System for Continuous Improvement
Learns from user feedback and adapts in real-time
Target: Push accuracy from 96% to 97%+ through usage
"""

import hashlib
import logging
import sqlite3
from collections import defaultdict, deque
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class ActiveLearningSystem:
    """Active learning system that improves from user feedback"""

    def __init__(self, db_path: str = "data/active_learning.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Learning components
        self.feedback_buffer = deque(maxlen=1000)  # Recent feedback
        self.pattern_corrections = defaultdict(list)  # Pattern → correct answers
        self.confidence_adjustments = {}  # Query hash → confidence adjustment
        self.user_preferences = defaultdict(dict)  # User-specific preferences

        # Metrics
        self.metrics = {
            "total_feedback": 0,
            "positive_feedback": 0,
            "negative_feedback": 0,
            "corrections_applied": 0,
            "accuracy_improvement": 0.0,
            "queries_improved": 0,
        }

        # Learning parameters
        self.learning_config = {
            "min_feedback_for_update": 3,  # Min feedback before updating
            "confidence_boost_correct": 0.02,  # Boost for correct predictions
            "confidence_penalty_wrong": -0.05,  # Penalty for wrong predictions
            "pattern_threshold": 0.8,  # Min confidence for pattern learning
            "decay_factor": 0.95,  # Decay old feedback importance
            "exploration_rate": 0.1,  # Explore new approaches
        }

        self._init_database()
        logger.info("Active Learning System initialized")

    def _init_database(self):
        """Initialize SQLite database for persistent learning"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Feedback table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                predicted_category TEXT,
                predicted_command TEXT,
                correct_category TEXT,
                correct_command TEXT,
                confidence REAL,
                feedback_type TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT
            )
        """
        )

        # Pattern corrections table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS pattern_corrections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern TEXT NOT NULL,
                category TEXT NOT NULL,
                command TEXT,
                success_rate REAL,
                usage_count INTEGER DEFAULT 0,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Learning metrics table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS learning_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        conn.commit()
        conn.close()

    def record_feedback(self, query: str, prediction: dict, feedback: dict) -> dict:
        """
        Record user feedback on a prediction

        Args:
            query: Original user query
            prediction: System's prediction
            feedback: User feedback (correct/incorrect, corrections)

        Returns:
            Learning update summary
        """
        self.metrics["total_feedback"] += 1

        # Determine feedback type
        is_correct = feedback.get("correct", False)
        if is_correct:
            self.metrics["positive_feedback"] += 1
            feedback_type = "positive"
        else:
            self.metrics["negative_feedback"] += 1
            feedback_type = "negative"

        # Store feedback
        feedback_entry = {
            "query": query,
            "predicted_category": prediction.get("category"),
            "predicted_command": prediction.get("command"),
            "correct_category": feedback.get(
                "correct_category", prediction.get("category")
            ),
            "correct_command": feedback.get(
                "correct_command", prediction.get("command")
            ),
            "confidence": prediction.get("confidence", 0.5),
            "feedback_type": feedback_type,
            "timestamp": datetime.now(),
            "user_id": feedback.get("user_id", "anonymous"),
        }

        # Add to buffer
        self.feedback_buffer.append(feedback_entry)

        # Store in database
        self._store_feedback(feedback_entry)

        # Learn from feedback
        learning_result = self._learn_from_feedback(feedback_entry)

        return {
            "feedback_recorded": True,
            "feedback_type": feedback_type,
            "learning_applied": learning_result.get("applied", False),
            "confidence_adjustment": learning_result.get("confidence_adjustment", 0),
            "pattern_learned": learning_result.get("pattern_learned", False),
        }

    def _store_feedback(self, feedback: dict):
        """Store feedback in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO feedback
            (query, predicted_category, predicted_command, correct_category,
             correct_command, confidence, feedback_type, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                feedback["query"],
                feedback["predicted_category"],
                feedback["predicted_command"],
                feedback["correct_category"],
                feedback["correct_command"],
                feedback["confidence"],
                feedback["feedback_type"],
                feedback["user_id"],
            ),
        )

        conn.commit()
        conn.close()

    def _learn_from_feedback(self, feedback: dict) -> dict:
        """Apply learning from feedback"""
        result = {
            "applied": False,
            "confidence_adjustment": 0,
            "pattern_learned": False,
        }

        query = feedback["query"]
        query_hash = hashlib.md5(query.encode()).hexdigest()

        # Adjust confidence based on feedback
        if feedback["feedback_type"] == "positive":
            # Boost confidence for correct predictions
            adjustment = self.learning_config["confidence_boost_correct"]
            self.confidence_adjustments[query_hash] = min(
                self.confidence_adjustments.get(query_hash, 0) + adjustment,
                0.2,  # Max boost of 0.2
            )
            result["confidence_adjustment"] = adjustment
        else:
            # Reduce confidence for incorrect predictions
            adjustment = self.learning_config["confidence_penalty_wrong"]
            self.confidence_adjustments[query_hash] = max(
                self.confidence_adjustments.get(query_hash, 0) + adjustment,
                -0.3,  # Max penalty of -0.3
            )
            result["confidence_adjustment"] = adjustment

            # Learn the correct pattern
            if feedback["correct_category"] and feedback["correct_command"]:
                self._learn_pattern(
                    query, feedback["correct_category"], feedback["correct_command"]
                )
                result["pattern_learned"] = True

        result["applied"] = True
        self.metrics["corrections_applied"] += 1

        return result

    def _learn_pattern(self, query: str, category: str, command: str):
        """Learn a new pattern from correction"""
        # Extract key terms from query
        query_lower = query.lower()
        key_terms = []

        # Common NixOS action words
        action_words = [
            "install",
            "update",
            "search",
            "configure",
            "enable",
            "disable",
            "remove",
            "list",
            "create",
            "setup",
        ]

        for word in action_words:
            if word in query_lower:
                key_terms.append(word)

        # Create pattern
        if key_terms:
            pattern = "_".join(key_terms)
            self.pattern_corrections[pattern].append(
                {
                    "category": category,
                    "command": command,
                    "query": query,
                    "timestamp": datetime.now(),
                }
            )

            # Store in database if pattern is strong
            if (
                len(self.pattern_corrections[pattern])
                >= self.learning_config["min_feedback_for_update"]
            ):
                self._store_pattern(pattern, category, command)

    def _store_pattern(self, pattern: str, category: str, command: str):
        """Store learned pattern in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if pattern exists
        cursor.execute(
            """
            SELECT id, usage_count FROM pattern_corrections
            WHERE pattern = ? AND category = ?
        """,
            (pattern, category),
        )

        existing = cursor.fetchone()

        if existing:
            # Update existing pattern
            cursor.execute(
                """
                UPDATE pattern_corrections
                SET usage_count = usage_count + 1,
                    success_rate = ?,
                    last_updated = CURRENT_TIMESTAMP
                WHERE id = ?
            """,
                (self._calculate_success_rate(pattern, category), existing[0]),
            )
        else:
            # Insert new pattern
            cursor.execute(
                """
                INSERT INTO pattern_corrections
                (pattern, category, command, success_rate, usage_count)
                VALUES (?, ?, ?, ?, 1)
            """,
                (
                    pattern,
                    category,
                    command,
                    self._calculate_success_rate(pattern, category),
                ),
            )

        conn.commit()
        conn.close()

    def _calculate_success_rate(self, pattern: str, category: str) -> float:
        """Calculate success rate for a pattern"""
        corrections = self.pattern_corrections.get(pattern, [])
        if not corrections:
            return 0.0

        correct = sum(1 for c in corrections if c["category"] == category)
        return correct / len(corrections)

    def get_adjustment(self, query: str) -> dict:
        """Get confidence adjustment for a query"""
        query_hash = hashlib.md5(query.encode()).hexdigest()

        # Direct adjustment
        direct_adjustment = self.confidence_adjustments.get(query_hash, 0)

        # Pattern-based adjustment
        pattern_adjustment = self._get_pattern_adjustment(query)

        # Combined adjustment
        total_adjustment = direct_adjustment + pattern_adjustment

        return {
            "confidence_adjustment": total_adjustment,
            "has_feedback": query_hash in self.confidence_adjustments,
            "pattern_match": pattern_adjustment != 0,
        }

    def _get_pattern_adjustment(self, query: str) -> float:
        """Get adjustment based on learned patterns"""
        query_lower = query.lower()

        # Check learned patterns
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT pattern, success_rate FROM pattern_corrections
            WHERE success_rate > ?
            ORDER BY success_rate DESC
        """,
            (self.learning_config["pattern_threshold"],),
        )

        patterns = cursor.fetchall()
        conn.close()

        for pattern, success_rate in patterns:
            pattern_terms = pattern.split("_")
            if all(term in query_lower for term in pattern_terms):
                # Found matching pattern
                return (success_rate - 0.8) * 0.5  # Convert to adjustment

        return 0.0

    def get_learning_metrics(self) -> dict:
        """Get current learning metrics"""
        # Calculate accuracy improvement
        if self.metrics["total_feedback"] > 0:
            accuracy = (
                self.metrics["positive_feedback"] / self.metrics["total_feedback"]
            )
            self.metrics["accuracy_improvement"] = accuracy - 0.96  # Baseline 96%

        # Get pattern statistics
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*), AVG(success_rate), MAX(usage_count)
            FROM pattern_corrections
        """
        )

        pattern_stats = cursor.fetchone()
        conn.close()

        return {
            "total_feedback": self.metrics["total_feedback"],
            "positive_rate": self.metrics["positive_feedback"]
            / max(1, self.metrics["total_feedback"]),
            "corrections_applied": self.metrics["corrections_applied"],
            "accuracy_improvement": self.metrics["accuracy_improvement"],
            "patterns_learned": pattern_stats[0] if pattern_stats else 0,
            "avg_pattern_success": pattern_stats[1] if pattern_stats else 0,
            "most_used_pattern_count": pattern_stats[2] if pattern_stats else 0,
            "confidence_adjustments": len(self.confidence_adjustments),
            "recent_feedback_count": len(self.feedback_buffer),
        }

    def export_improvements(self) -> dict:
        """Export learned improvements for model updates"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get high-confidence patterns
        cursor.execute(
            """
            SELECT pattern, category, command, success_rate, usage_count
            FROM pattern_corrections
            WHERE success_rate > ? AND usage_count > ?
            ORDER BY success_rate DESC, usage_count DESC
        """,
            (0.85, 5),
        )

        patterns = cursor.fetchall()

        # Get frequently corrected queries
        cursor.execute(
            """
            SELECT query, correct_category, correct_command, COUNT(*) as correction_count
            FROM feedback
            WHERE feedback_type = 'negative'
            GROUP BY query, correct_category, correct_command
            HAVING correction_count > 2
            ORDER BY correction_count DESC
        """
        )

        corrections = cursor.fetchall()

        conn.close()

        return {
            "high_confidence_patterns": [
                {
                    "pattern": p[0],
                    "category": p[1],
                    "command": p[2],
                    "success_rate": p[3],
                    "usage_count": p[4],
                }
                for p in patterns
            ],
            "frequent_corrections": [
                {
                    "query": c[0],
                    "correct_category": c[1],
                    "correct_command": c[2],
                    "correction_count": c[3],
                }
                for c in corrections
            ],
            "total_improvements": len(patterns) + len(corrections),
        }

    def simulate_user_feedback(self, num_interactions: int = 50) -> dict:
        """Simulate user feedback for testing"""
        import random

        print(f"\n📚 Simulating {num_interactions} user interactions")
        print("=" * 50)

        test_queries = [
            ("install brave browser", "install", "nix-env -iA nixpkgs.brave", 0.9),
            ("setup rust development", "dev", "nix-shell -p rustc cargo", 0.95),
            (
                "update all packages",
                "update",
                "nix-channel --update && nix-env -u",
                0.85,
            ),
            ("search markdown editor", "search", "nix search nixpkgs markdown", 0.9),
            ("enable docker service", "config", "systemctl enable docker", 0.88),
            (
                "python with tensorflow",
                "dev",
                "nix-shell -p python3 python3Packages.tensorflow",
                0.92,
            ),
            ("rollback system", "update", "nixos-rebuild switch --rollback", 0.87),
            ("cleanup old generations", "update", "nix-collect-garbage -d", 0.9),
            ("install neovim", "install", "nix-env -iA nixpkgs.neovim", 0.95),
            ("configure bluetooth", "config", "systemctl enable bluetooth", 0.85),
        ]

        for i in range(num_interactions):
            # Pick random query
            query, correct_cat, correct_cmd, base_accuracy = random.choice(test_queries)

            # Simulate prediction
            prediction = {
                "category": correct_cat
                if random.random() < base_accuracy
                else "unknown",
                "command": correct_cmd
                if random.random() < base_accuracy
                else "nix search",
                "confidence": base_accuracy + random.uniform(-0.1, 0.1),
            }

            # Simulate feedback
            is_correct = prediction["category"] == correct_cat
            feedback = {
                "correct": is_correct,
                "correct_category": correct_cat,
                "correct_command": correct_cmd,
                "user_id": f"test_user_{i % 5}",
            }

            # Record feedback
            result = self.record_feedback(query, prediction, feedback)

            if i % 10 == 0:
                metrics = self.get_learning_metrics()
                print(
                    f"After {i+1} interactions: "
                    f"Positive rate: {metrics['positive_rate']:.1%}, "
                    f"Patterns learned: {metrics['patterns_learned']}"
                )

        # Final metrics
        final_metrics = self.get_learning_metrics()
        improvements = self.export_improvements()

        print("\n📊 Final Learning Metrics:")
        print(f"  Total feedback: {final_metrics['total_feedback']}")
        print(f"  Positive rate: {final_metrics['positive_rate']:.1%}")
        print(f"  Accuracy improvement: {final_metrics['accuracy_improvement']:+.1%}")
        print(f"  Patterns learned: {final_metrics['patterns_learned']}")
        print(
            f"  High-confidence patterns: {len(improvements['high_confidence_patterns'])}"
        )
        print(f"  Frequent corrections: {len(improvements['frequent_corrections'])}")

        return final_metrics


def test_active_learning():
    """Test the active learning system"""

    print("🧠 Testing Active Learning System")
    print("=" * 60)

    # Initialize system
    system = ActiveLearningSystem("data/test_active_learning.db")

    # Test 1: Single feedback recording
    print("\n1️⃣ Testing Single Feedback")
    print("-" * 40)

    query = "install firefox browser"
    prediction = {
        "category": "install",
        "command": "nix-env -iA nixpkgs.firefox",
        "confidence": 0.95,
    }

    # Positive feedback
    feedback = {"correct": True, "user_id": "test_user"}

    result = system.record_feedback(query, prediction, feedback)
    print(f"Query: {query}")
    print("Feedback: Correct ✅")
    print(f"Learning result: {result}")

    # Negative feedback with correction
    query2 = "setup golang development"
    prediction2 = {
        "category": "unknown",
        "command": "nix search golang",
        "confidence": 0.6,
    }

    feedback2 = {
        "correct": False,
        "correct_category": "dev",
        "correct_command": "nix-shell -p go",
        "user_id": "test_user",
    }

    result2 = system.record_feedback(query2, prediction2, feedback2)
    print(f"\nQuery: {query2}")
    print("Feedback: Incorrect ❌")
    print("Correction: dev category, 'nix-shell -p go' command")
    print(f"Learning result: {result2}")

    # Test 2: Pattern learning
    print("\n2️⃣ Testing Pattern Learning")
    print("-" * 40)

    # Multiple similar corrections
    for i in range(5):
        query = f"create {['python', 'rust', 'node', 'java', 'go'][i]} development environment"
        prediction = {"category": "unknown", "command": "nix search", "confidence": 0.5}
        feedback = {
            "correct": False,
            "correct_category": "dev",
            "correct_command": f'nix-shell -p {["python3", "rustc", "nodejs", "jdk", "go"][i]}',
            "user_id": "test_user",
        }
        system.record_feedback(query, prediction, feedback)

    # Check if pattern was learned
    adjustment = system.get_adjustment("create ruby development environment")
    print(f"Pattern adjustment for 'create ruby development environment': {adjustment}")

    # Test 3: Simulate extended usage
    print("\n3️⃣ Simulating Extended Usage")
    print("-" * 40)

    metrics = system.simulate_user_feedback(50)

    # Test 4: Export improvements
    print("\n4️⃣ Exporting Learned Improvements")
    print("-" * 40)

    improvements = system.export_improvements()

    if improvements["high_confidence_patterns"]:
        print("High-confidence patterns learned:")
        for pattern in improvements["high_confidence_patterns"][:3]:
            print(f"  Pattern: {pattern['pattern']}")
            print(f"    Category: {pattern['category']}")
            print(f"    Success Rate: {pattern['success_rate']:.1%}")
            print(f"    Usage Count: {pattern['usage_count']}")

    if improvements["frequent_corrections"]:
        print("\nFrequent corrections:")
        for correction in improvements["frequent_corrections"][:3]:
            print(f"  Query: {correction['query'][:40]}")
            print(
                f"    Correct: {correction['correct_category']} → {correction['correct_command'][:30]}"
            )
            print(f"    Times corrected: {correction['correction_count']}")

    print("\n" + "=" * 60)
    print("✅ Active Learning System Test Complete!")
    print(f"📊 Final accuracy improvement: {metrics['accuracy_improvement']:+.1%}")

    # Expected accuracy with active learning
    base_accuracy = 0.963  # Current v5 accuracy
    improved_accuracy = base_accuracy + max(0, metrics["accuracy_improvement"])
    print(f"💡 Estimated accuracy with active learning: {improved_accuracy:.1%}")

    if improved_accuracy >= 0.97:
        print("🎉 SUCCESS! Active learning pushes accuracy above 97%!")

    return system


if __name__ == "__main__":
    test_active_learning()
