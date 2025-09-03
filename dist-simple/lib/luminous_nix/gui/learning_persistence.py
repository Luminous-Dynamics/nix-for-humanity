"""
🧠 Learning Persistence Layer
Stores, tracks, and evolves interface generation knowledge
"""

import json
import pickle
import sqlite3
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# numpy would be used for more sophisticated calculations
# For now, using basic Python for compatibility

try:
    from .component_synthesis_engine import ComponentDNA, SynthesizedComponent
    from .nl_interface_builder import InterfaceSpecification, ParsedIntent
except ImportError:
    from component_synthesis_engine import ComponentDNA, SynthesizedComponent
    from nl_interface_builder import InterfaceSpecification, ParsedIntent


@dataclass
class ComponentPattern:
    """A successful component pattern worth remembering"""

    id: str
    dna: ComponentDNA
    success_rate: float
    usage_count: int
    contexts: list[str]  # Where this pattern works well
    created_at: datetime
    last_used: datetime
    feedback_scores: list[float]
    evolution_history: list[str]  # IDs of components it evolved from/to

    def calculate_fitness(self) -> float:
        """Calculate overall fitness score"""
        if not self.feedback_scores:
            return 0.5

        # Weighted average: recent feedback matters more
        # Simple exponential weighting without numpy
        weights = []
        for i in range(len(self.feedback_scores)):
            weight = 2 ** (i - len(self.feedback_scores) + 1)
            weights.append(weight)

        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]

        weighted_sum = sum(
            score * weight for score, weight in zip(self.feedback_scores, weights, strict=False)
        )
        return weighted_sum


@dataclass
class UserPreference:
    """Tracked user preferences"""

    user_id: str
    preference_type: str  # visual, behavioral, layout, etc.
    preference_value: Any
    confidence: float  # How confident we are about this preference
    evidence_count: int  # Number of observations supporting this
    last_observed: datetime

    def update_confidence(self, observation_matches: bool):
        """Update confidence based on new observation"""
        if observation_matches:
            # Increase confidence (with diminishing returns)
            self.confidence = min(1.0, self.confidence + (1 - self.confidence) * 0.1)
            self.evidence_count += 1
        else:
            # Decrease confidence
            self.confidence *= 0.9

        self.last_observed = datetime.now()


@dataclass
class InterfaceMetrics:
    """Metrics for a generated interface"""

    interface_id: str
    request: str
    generation_time: float  # milliseconds
    component_count: int
    user_satisfaction: float | None  # 0-1 scale
    interaction_time: float | None  # How long user interacted
    task_completion: bool | None
    modifications_made: int  # Number of changes user made
    timestamp: datetime

    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        return {**asdict(self), "timestamp": self.timestamp.isoformat()}


class LearningDatabase:
    """SQLite database for persistent learning storage"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default to user's data directory
            data_dir = Path.home() / ".local" / "share" / "luminous-nix" / "learning"
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = data_dir / "interface_learning.db"

        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(self.db_path))
        self._initialize_schema()

    def _initialize_schema(self):
        """Create database schema"""

        cursor = self.conn.cursor()

        # Component patterns table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS component_patterns (
                id TEXT PRIMARY KEY,
                dna BLOB,
                success_rate REAL,
                usage_count INTEGER,
                contexts TEXT,
                created_at TEXT,
                last_used TEXT,
                feedback_scores TEXT,
                evolution_history TEXT
            )
        """
        )

        # User preferences table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id TEXT,
                preference_type TEXT,
                preference_value TEXT,
                confidence REAL,
                evidence_count INTEGER,
                last_observed TEXT,
                PRIMARY KEY (user_id, preference_type)
            )
        """
        )

        # Interface metrics table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS interface_metrics (
                interface_id TEXT PRIMARY KEY,
                request TEXT,
                generation_time REAL,
                component_count INTEGER,
                user_satisfaction REAL,
                interaction_time REAL,
                task_completion BOOLEAN,
                modifications_made INTEGER,
                timestamp TEXT
            )
        """
        )

        # Request patterns table (for NLP learning)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS request_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request TEXT,
                parsed_intent TEXT,
                success BOOLEAN,
                timestamp TEXT
            )
        """
        )

        # Component DNA evolution table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS dna_evolution (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_dna BLOB,
                child_dna BLOB,
                mutation_type TEXT,
                fitness_improvement REAL,
                timestamp TEXT
            )
        """
        )

        self.conn.commit()

    def save_component_pattern(self, pattern: ComponentPattern):
        """Save a successful component pattern"""

        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO component_patterns
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                pattern.id,
                pickle.dumps(pattern.dna),
                pattern.success_rate,
                pattern.usage_count,
                json.dumps(pattern.contexts),
                pattern.created_at.isoformat(),
                pattern.last_used.isoformat(),
                json.dumps(pattern.feedback_scores),
                json.dumps(pattern.evolution_history),
            ),
        )
        self.conn.commit()

    def get_component_patterns(
        self, context: str | None = None, min_success_rate: float = 0.6
    ) -> list[ComponentPattern]:
        """Retrieve successful component patterns"""

        cursor = self.conn.cursor()

        query = """
            SELECT * FROM component_patterns
            WHERE success_rate >= ?
        """
        params = [min_success_rate]

        if context:
            query += " AND contexts LIKE ?"
            params.append(f'%"{context}"%')

        query += " ORDER BY success_rate DESC, usage_count DESC"

        cursor.execute(query, params)

        patterns = []
        for row in cursor.fetchall():
            pattern = ComponentPattern(
                id=row[0],
                dna=pickle.loads(row[1]),
                success_rate=row[2],
                usage_count=row[3],
                contexts=json.loads(row[4]),
                created_at=datetime.fromisoformat(row[5]),
                last_used=datetime.fromisoformat(row[6]),
                feedback_scores=json.loads(row[7]),
                evolution_history=json.loads(row[8]),
            )
            patterns.append(pattern)

        return patterns

    def save_user_preference(self, preference: UserPreference):
        """Save or update user preference"""

        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO user_preferences
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                preference.user_id,
                preference.preference_type,
                json.dumps(preference.preference_value),
                preference.confidence,
                preference.evidence_count,
                preference.last_observed.isoformat(),
            ),
        )
        self.conn.commit()

    def get_user_preferences(
        self, user_id: str, min_confidence: float = 0.5
    ) -> dict[str, UserPreference]:
        """Get user preferences above confidence threshold"""

        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT * FROM user_preferences
            WHERE user_id = ? AND confidence >= ?
        """,
            (user_id, min_confidence),
        )

        preferences = {}
        for row in cursor.fetchall():
            pref = UserPreference(
                user_id=row[0],
                preference_type=row[1],
                preference_value=json.loads(row[2]),
                confidence=row[3],
                evidence_count=row[4],
                last_observed=datetime.fromisoformat(row[5]),
            )
            preferences[pref.preference_type] = pref

        return preferences

    def save_interface_metrics(self, metrics: InterfaceMetrics):
        """Save interface performance metrics"""

        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO interface_metrics
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                metrics.interface_id,
                metrics.request,
                metrics.generation_time,
                metrics.component_count,
                metrics.user_satisfaction,
                metrics.interaction_time,
                metrics.task_completion,
                metrics.modifications_made,
                metrics.timestamp.isoformat(),
            ),
        )
        self.conn.commit()

    def get_average_metrics(self, days: int = 30) -> dict[str, float]:
        """Get average metrics for recent interfaces"""

        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT 
                AVG(generation_time) as avg_gen_time,
                AVG(component_count) as avg_components,
                AVG(user_satisfaction) as avg_satisfaction,
                AVG(interaction_time) as avg_interaction,
                AVG(CAST(task_completion AS REAL)) as completion_rate,
                AVG(modifications_made) as avg_modifications
            FROM interface_metrics
            WHERE timestamp > ?
        """,
            (cutoff,),
        )

        row = cursor.fetchone()
        if row:
            return {
                "avg_generation_time": row[0] or 0,
                "avg_component_count": row[1] or 0,
                "avg_satisfaction": row[2] or 0,
                "avg_interaction_time": row[3] or 0,
                "task_completion_rate": row[4] or 0,
                "avg_modifications": row[5] or 0,
            }

        return {}

    def record_request_pattern(self, request: str, intent: ParsedIntent, success: bool):
        """Record a request pattern for NLP learning"""

        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO request_patterns (request, parsed_intent, success, timestamp)
            VALUES (?, ?, ?, ?)
        """,
            (
                request,
                json.dumps(intent.__dict__, default=str),
                success,
                datetime.now().isoformat(),
            ),
        )
        self.conn.commit()

    def record_dna_evolution(
        self,
        parent_dna: ComponentDNA,
        child_dna: ComponentDNA,
        mutation_type: str,
        fitness_improvement: float,
    ):
        """Record DNA evolution for genetic learning"""

        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO dna_evolution (parent_dna, child_dna, mutation_type, fitness_improvement, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                pickle.dumps(parent_dna),
                pickle.dumps(child_dna),
                mutation_type,
                fitness_improvement,
                datetime.now().isoformat(),
            ),
        )
        self.conn.commit()

    def close(self):
        """Close database connection"""
        self.conn.close()


class PatternRecognizer:
    """Recognizes successful patterns in component generation"""

    def __init__(self, db: LearningDatabase):
        self.db = db
        self.pattern_cache = {}

    def identify_pattern(
        self, component: SynthesizedComponent, context: str, feedback: float
    ) -> ComponentPattern | None:
        """Identify if this component represents a successful pattern"""

        # Check if pattern already exists
        existing = self.db.get_component_patterns(context=context)

        for pattern in existing:
            if self._dna_similarity(pattern.dna, component.dna) > 0.8:
                # Update existing pattern
                pattern.feedback_scores.append(feedback)
                pattern.usage_count += 1
                pattern.last_used = datetime.now()
                pattern.success_rate = pattern.calculate_fitness()

                self.db.save_component_pattern(pattern)
                return pattern

        # Create new pattern if feedback is positive
        if feedback > 0.7:
            pattern = ComponentPattern(
                id=f"pattern_{component.id}",
                dna=component.dna,
                success_rate=feedback,
                usage_count=1,
                contexts=[context],
                created_at=datetime.now(),
                last_used=datetime.now(),
                feedback_scores=[feedback],
                evolution_history=[],
            )

            self.db.save_component_pattern(pattern)
            return pattern

        return None

    def _dna_similarity(self, dna1: ComponentDNA, dna2: ComponentDNA) -> float:
        """Calculate similarity between two DNA structures"""

        similarity_scores = []

        # Compare purpose
        if dna1.purpose == dna2.purpose:
            similarity_scores.append(1.0)
        else:
            similarity_scores.append(0.0)

        # Compare capabilities
        cap1 = set(dna1.capabilities)
        cap2 = set(dna2.capabilities)
        if cap1 and cap2:
            similarity_scores.append(len(cap1 & cap2) / len(cap1 | cap2))

        # Compare visual traits
        visual_match = sum(
            1 for k, v in dna1.visual_traits.items() if dna2.visual_traits.get(k) == v
        )
        visual_total = len(dna1.visual_traits)
        if visual_total > 0:
            similarity_scores.append(visual_match / visual_total)

        # Compare behaviors
        behavior_match = sum(
            1 for k, v in dna1.behaviors.items() if dna2.behaviors.get(k) == v
        )
        behavior_total = len(dna1.behaviors)
        if behavior_total > 0:
            similarity_scores.append(behavior_match / behavior_total)

        return (
            sum(similarity_scores) / len(similarity_scores)
            if similarity_scores
            else 0.0
        )

    def suggest_patterns(
        self, context: str, requirements: dict[str, Any]
    ) -> list[ComponentPattern]:
        """Suggest successful patterns for given context"""

        patterns = self.db.get_component_patterns(context=context)

        # Sort by fitness and recency
        patterns.sort(
            key=lambda p: (
                p.calculate_fitness(),
                -(datetime.now() - p.last_used).total_seconds(),
            ),
            reverse=True,
        )

        return patterns[:5]  # Top 5 suggestions


class PreferenceTracker:
    """Tracks and learns user preferences"""

    def __init__(self, db: LearningDatabase):
        self.db = db
        self.preference_cache = defaultdict(dict)

    def observe_preference(
        self, user_id: str, preference_type: str, observed_value: Any
    ):
        """Record an observed preference"""

        # Get existing preference or create new
        preferences = self.db.get_user_preferences(user_id)

        if preference_type in preferences:
            pref = preferences[preference_type]
            # Check if observation matches
            matches = pref.preference_value == observed_value
            pref.update_confidence(matches)

            if not matches and pref.confidence < 0.3:
                # Low confidence, update to new value
                pref.preference_value = observed_value
                pref.confidence = 0.5
        else:
            # New preference
            pref = UserPreference(
                user_id=user_id,
                preference_type=preference_type,
                preference_value=observed_value,
                confidence=0.5,
                evidence_count=1,
                last_observed=datetime.now(),
            )

        self.db.save_user_preference(pref)
        self.preference_cache[user_id][preference_type] = pref

    def get_strong_preferences(
        self, user_id: str, min_confidence: float = 0.7
    ) -> dict[str, Any]:
        """Get high-confidence preferences"""

        if user_id in self.preference_cache:
            return {
                k: v.preference_value
                for k, v in self.preference_cache[user_id].items()
                if v.confidence >= min_confidence
            }

        preferences = self.db.get_user_preferences(user_id, min_confidence)
        return {k: v.preference_value for k, v in preferences.items()}

    def predict_preference(self, user_id: str, preference_type: str) -> Any | None:
        """Predict a user's preference"""

        preferences = self.db.get_user_preferences(user_id)

        if preference_type in preferences:
            pref = preferences[preference_type]
            if pref.confidence > 0.5:
                return pref.preference_value

        # Try to infer from similar preferences
        # (simplified - could use more sophisticated inference)
        related_types = {
            "color_scheme": ["theme_mode", "visual_style"],
            "complexity": ["expertise_level", "information_density"],
            "animation": ["interaction_style", "feedback_level"],
        }

        if preference_type in related_types:
            for related in related_types[preference_type]:
                if related in preferences and preferences[related].confidence > 0.6:
                    # Use related preference as hint
                    return self._infer_from_related(
                        preference_type, related, preferences[related].preference_value
                    )

        return None

    def _infer_from_related(
        self, target_type: str, source_type: str, source_value: Any
    ) -> Any | None:
        """Infer preference from related type"""

        inference_rules = {
            ("color_scheme", "theme_mode"): {"dark": "dark", "light": "light"},
            ("complexity", "expertise_level"): {
                "beginner": "simple",
                "intermediate": "balanced",
                "expert": "detailed",
            },
        }

        key = (target_type, source_type)
        if key in inference_rules and source_value in inference_rules[key]:
            return inference_rules[key][source_value]

        return None


class ContinuousImprovementEngine:
    """Engine for continuous learning and improvement"""

    def __init__(self, db: LearningDatabase):
        self.db = db
        self.pattern_recognizer = PatternRecognizer(db)
        self.preference_tracker = PreferenceTracker(db)
        self.improvement_queue = []

    def record_interaction(
        self,
        user_id: str,
        interface: InterfaceSpecification,
        request: str,
        generation_time: float,
    ):
        """Record initial interface generation"""

        metrics = InterfaceMetrics(
            interface_id=str(id(interface)),
            request=request,
            generation_time=generation_time,
            component_count=len(interface.components),
            user_satisfaction=None,
            interaction_time=None,
            task_completion=None,
            modifications_made=0,
            timestamp=datetime.now(),
        )

        self.db.save_interface_metrics(metrics)

        # Track preferences from the interface
        if interface.theme:
            self.preference_tracker.observe_preference(
                user_id, "theme_mode", interface.theme.get("mode", "light")
            )

        if interface.layout:
            self.preference_tracker.observe_preference(
                user_id, "layout_type", interface.layout.get("type")
            )

    def record_feedback(
        self,
        user_id: str,
        interface_id: str,
        satisfaction: float,
        interaction_time: float = None,
        task_completed: bool = None,
    ):
        """Record user feedback on interface"""

        # Update metrics
        cursor = self.db.conn.cursor()
        cursor.execute(
            """
            UPDATE interface_metrics
            SET user_satisfaction = ?,
                interaction_time = ?,
                task_completion = ?
            WHERE interface_id = ?
        """,
            (satisfaction, interaction_time, task_completed, interface_id),
        )
        self.db.conn.commit()

        # Identify successful patterns if satisfaction is high
        if satisfaction > 0.7:
            # Queue for pattern learning
            self.improvement_queue.append(
                {
                    "interface_id": interface_id,
                    "satisfaction": satisfaction,
                    "user_id": user_id,
                }
            )

    def learn_from_success(
        self, interface: InterfaceSpecification, satisfaction: float
    ):
        """Learn from successful interfaces"""

        for component in interface.components:
            # Identify pattern
            context = component.dna.purpose
            pattern = self.pattern_recognizer.identify_pattern(
                component, context, satisfaction
            )

            if pattern:
                # Record successful DNA evolution if this is evolved
                if component.metadata.get("evolved_from"):
                    parent_id = component.metadata["evolved_from"]
                    # Record evolution success
                    # (simplified - would need to load parent DNA)
                    self.db.record_dna_evolution(
                        component.dna,  # Using same as placeholder
                        component.dna,
                        "user_driven",
                        satisfaction - 0.5,  # Improvement over baseline
                    )

    def get_improvement_suggestions(self, context: str) -> list[dict[str, Any]]:
        """Get suggestions for improving interface generation"""

        # Get recent metrics
        metrics = self.db.get_average_metrics(days=7)

        suggestions = []

        # Suggest based on metrics
        if metrics.get("avg_satisfaction", 0) < 0.7:
            suggestions.append(
                {
                    "type": "quality",
                    "message": "User satisfaction below target",
                    "action": "Review failed patterns and adjust generation",
                }
            )

        if metrics.get("avg_modifications", 0) > 3:
            suggestions.append(
                {
                    "type": "accuracy",
                    "message": "Users making many modifications",
                    "action": "Improve initial generation accuracy",
                }
            )

        if metrics.get("task_completion_rate", 0) < 0.8:
            suggestions.append(
                {
                    "type": "effectiveness",
                    "message": "Low task completion rate",
                    "action": "Simplify interfaces or add guidance",
                }
            )

        # Get successful patterns for context
        patterns = self.pattern_recognizer.suggest_patterns(context, {})
        if patterns:
            suggestions.append(
                {
                    "type": "pattern",
                    "message": f"Found {len(patterns)} successful patterns",
                    "patterns": patterns[:3],
                }
            )

        return suggestions

    def optimize_for_user(
        self, user_id: str, base_requirements: dict[str, Any]
    ) -> dict[str, Any]:
        """Optimize requirements based on learned preferences"""

        preferences = self.preference_tracker.get_strong_preferences(user_id)

        # Apply preferences to requirements
        optimized = base_requirements.copy()

        if "theme_mode" in preferences:
            optimized["color_scheme"] = preferences["theme_mode"]

        if "complexity" in preferences:
            optimized["information_density"] = preferences["complexity"]

        if "animation" in preferences:
            optimized["animation_level"] = preferences["animation"]

        return optimized


# Example usage
if __name__ == "__main__":
    # Initialize learning system
    db = LearningDatabase()
    engine = ContinuousImprovementEngine(db)

    # Simulate some learning
    print("Learning System Initialized")
    print(f"Database location: {db.db_path}")

    # Record a successful interaction
    from .nl_interface_builder import NLInterfaceBuilder, UserContext

    builder = NLInterfaceBuilder()
    context = UserContext(user_id="demo_user")

    # Generate interface
    interface = builder.build_interface("Create a dashboard with dark theme", context)

    # Record interaction
    engine.record_interaction(
        user_id="demo_user",
        interface=interface,
        request="Create a dashboard with dark theme",
        generation_time=50.0,
    )

    # Simulate feedback
    engine.record_feedback(
        user_id="demo_user",
        interface_id=str(id(interface)),
        satisfaction=0.85,
        interaction_time=120.0,
        task_completed=True,
    )

    # Learn from success
    engine.learn_from_success(interface, 0.85)

    # Get improvement suggestions
    suggestions = engine.get_improvement_suggestions("dashboard")
    print(f"\nImprovement suggestions: {suggestions}")

    # Get user preferences
    preferences = engine.preference_tracker.get_strong_preferences("demo_user")
    print(f"\nLearned preferences: {preferences}")

    # Get metrics
    metrics = db.get_average_metrics()
    print(f"\nAverage metrics: {metrics}")

    db.close()
