"""
Archetype Evolution Tracker - Revolutionary Feature

Tracks how user archetypes change over time.

Key insights:
- People aren't static - they evolve as they learn
- A beginner Learner might become an intermediate Explorer
- An advanced Explorer might become a Creator
- The system adapts as YOU change

This is the "Persona of One" concept - everyone's journey is unique.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import json

from .user_profiler import UserArchetype, TechnicalLevel
from .behavioral_features import BehavioralFeatures


@dataclass
class ArchetypeSnapshot:
    """A snapshot of user's archetype at a specific time"""
    archetype: UserArchetype
    confidence: float
    probabilities: Dict[str, float]  # All archetype probabilities
    technical_level: TechnicalLevel
    timestamp: str
    data_quality: float  # How much real data we had


@dataclass
class EvolutionMetrics:
    """Metrics about archetype evolution"""
    days_tracked: int
    archetype_changes: int
    current_streak_days: int  # Days with same archetype
    data_points: int
    confidence_trend: str  # "increasing", "stable", "decreasing"


class ArchetypeEvolutionTracker:
    """
    Tracks how a user's archetype evolves over time.

    Revolutionary insights:
    1. Users evolve - not static types
    2. Track confidence over time (cold→warm transition)
    3. Detect archetype shifts (learning progression)
    4. Predict next evolution (growth path)

    This enables the "Persona of One" - each user has a unique journey.
    """

    def __init__(self, user_id: str = "default_user", data_dir: Optional[str] = None):
        """
        Initialize evolution tracker.

        Args:
            user_id: User to track
            data_dir: Directory for storing evolution data
        """
        self.user_id = user_id

        # Setup data directory
        if data_dir is None:
            data_dir = str(Path.home() / ".luminous-nix" / "evolution")
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # File for this user's evolution
        self.evolution_file = self.data_dir / f"{user_id}_evolution.jsonl"

        # Load existing snapshots
        self.snapshots: List[ArchetypeSnapshot] = self._load_snapshots()

    def record_snapshot(
        self,
        archetype: UserArchetype,
        confidence: float,
        probabilities: Dict[str, float],
        technical_level: TechnicalLevel,
        data_quality: float
    ):
        """
        Record a new archetype snapshot.

        Args:
            archetype: Current detected archetype
            confidence: Confidence in detection
            probabilities: All archetype probabilities
            technical_level: Current technical level
            data_quality: Ratio of real vs synthetic data (0.0-1.0)
        """
        snapshot = ArchetypeSnapshot(
            archetype=archetype,
            confidence=confidence,
            probabilities=probabilities,
            technical_level=technical_level,
            timestamp=datetime.now().isoformat(),
            data_quality=data_quality
        )

        self.snapshots.append(snapshot)
        self._save_snapshot(snapshot)

    def get_cold_start_status(self) -> Dict:
        """
        Determine cold-start transition status.

        Cold Start: 0-10 interactions, low confidence, mostly synthetic
        Warming Up: 11-50 interactions, increasing confidence
        Warm: 51-200 interactions, stable confidence
        Established: 200+ interactions, high confidence

        Returns:
            Status information about cold-start transition
        """
        if not self.snapshots:
            return {
                "phase": "cold_start",
                "interactions": 0,
                "confidence": 0.0,
                "data_quality": 0.0,
                "recommendation": "Need more interactions to understand you better"
            }

        latest = self.snapshots[-1]
        interaction_count = len(self.snapshots)

        # Determine phase
        if interaction_count < 10:
            phase = "cold_start"
            recommendation = f"Learning about you ({interaction_count}/10 interactions)"
        elif interaction_count < 50:
            phase = "warming_up"
            recommendation = f"Building confidence ({interaction_count}/50 interactions)"
        elif interaction_count < 200:
            phase = "warm"
            recommendation = "Good understanding of your patterns"
        else:
            phase = "established"
            recommendation = "Excellent understanding of your preferences"

        # Calculate confidence trend
        confidence_trend = self._calculate_confidence_trend()

        return {
            "phase": phase,
            "interactions": interaction_count,
            "confidence": latest.confidence,
            "data_quality": latest.data_quality,
            "confidence_trend": confidence_trend,
            "recommendation": recommendation
        }

    def detect_archetype_shift(self) -> Optional[Dict]:
        """
        Detect if user's archetype has shifted.

        A shift occurs when:
        1. Archetype changes and stays changed for 5+ snapshots
        2. Confidence is high enough (>0.6)
        3. Data quality is sufficient (>0.3 real data)

        Returns:
            Information about shift if detected, None otherwise
        """
        if len(self.snapshots) < 10:
            return None  # Need history to detect shifts

        # Get recent archetype (last 5 snapshots)
        recent = self.snapshots[-5:]
        recent_archetype = recent[-1].archetype

        # Check if all recent match
        if not all(s.archetype == recent_archetype for s in recent):
            return None  # Not stable enough

        # Get historical archetype (before recent 5)
        historical = self.snapshots[-15:-5] if len(self.snapshots) >= 15 else self.snapshots[:-5]
        if not historical:
            return None

        # Most common historical archetype
        historical_archetypes = [s.archetype for s in historical]
        historical_archetype = max(set(historical_archetypes), key=historical_archetypes.count)

        # Check if shifted
        if recent_archetype != historical_archetype:
            latest = self.snapshots[-1]

            # Only report high-confidence shifts with sufficient real data
            if latest.confidence > 0.6 and latest.data_quality > 0.3:
                return {
                    "from_archetype": historical_archetype.value,
                    "to_archetype": recent_archetype.value,
                    "confidence": latest.confidence,
                    "data_quality": latest.data_quality,
                    "detected_at": latest.timestamp,
                    "interpretation": self._interpret_shift(historical_archetype, recent_archetype)
                }

        return None

    def predict_next_evolution(self) -> Optional[Dict]:
        """
        Predict likely next archetype evolution.

        Based on:
        1. Current archetype and trends
        2. Technical level progression
        3. Common evolution paths

        Common paths:
        - Learner → Explorer (curiosity awakening)
        - Explorer → Pragmatist (wants results)
        - Explorer → Creator (builds custom solutions)
        - Pragmatist → Creator (automation needs)

        Returns:
            Prediction of next likely archetype
        """
        if len(self.snapshots) < 20:
            return None  # Need more data

        latest = self.snapshots[-1]
        current_archetype = latest.archetype

        # Common evolution paths
        evolution_paths = {
            UserArchetype.LEARNER: [
                (UserArchetype.EXPLORER, 0.6, "Natural curiosity leading to exploration"),
                (UserArchetype.PRAGMATIST, 0.3, "Desire for practical application"),
                (UserArchetype.CREATOR, 0.1, "Deep understanding enabling creation")
            ],
            UserArchetype.EXPLORER: [
                (UserArchetype.CREATOR, 0.5, "Discovery leading to custom building"),
                (UserArchetype.PRAGMATIST, 0.3, "Focusing on proven solutions"),
                (UserArchetype.LEARNER, 0.2, "Deep dive into understanding")
            ],
            UserArchetype.PRAGMATIST: [
                (UserArchetype.CREATOR, 0.5, "Automation and customization needs"),
                (UserArchetype.EXPLORER, 0.3, "Seeking better options"),
                (UserArchetype.LEARNER, 0.2, "Understanding to optimize")
            ],
            UserArchetype.CREATOR: [
                (UserArchetype.PRAGMATIST, 0.4, "Standardizing successful patterns"),
                (UserArchetype.EXPLORER, 0.3, "Seeking new technologies"),
                (UserArchetype.LEARNER, 0.3, "Deep technical mastery")
            ]
        }

        # Get probabilities for current archetype's next evolution
        if current_archetype not in evolution_paths:
            return None

        paths = evolution_paths[current_archetype]

        # Check if moving toward any of these
        recent_probs = [s.probabilities for s in self.snapshots[-10:]]

        # Find which archetype is trending up
        trending_up = None
        max_trend = 0.0

        for next_archetype, base_probability, interpretation in paths:
            # Calculate trend in probability for this archetype
            trend = self._calculate_probability_trend(next_archetype.value, recent_probs)

            if trend > max_trend and trend > 0.05:  # At least 5% increase
                max_trend = trend
                trending_up = (next_archetype, base_probability + trend, interpretation)

        if trending_up:
            return {
                "current_archetype": current_archetype.value,
                "predicted_archetype": trending_up[0].value,
                "probability": min(trending_up[1], 1.0),
                "interpretation": trending_up[2],
                "timeframe": "next 2-4 weeks"
            }

        return None

    def get_evolution_history(self) -> Dict:
        """
        Get complete evolution history.

        Returns:
            Full history with metrics
        """
        if not self.snapshots:
            return {
                "snapshots": [],
                "metrics": None
            }

        # Calculate metrics
        days_tracked = self._calculate_days_tracked()
        archetype_changes = self._count_archetype_changes()
        current_streak = self._calculate_current_streak()
        confidence_trend = self._calculate_confidence_trend()

        metrics = EvolutionMetrics(
            days_tracked=days_tracked,
            archetype_changes=archetype_changes,
            current_streak_days=current_streak,
            data_points=len(self.snapshots),
            confidence_trend=confidence_trend
        )

        return {
            "snapshots": [self._snapshot_to_dict(s) for s in self.snapshots],
            "metrics": asdict(metrics)
        }

    def _calculate_confidence_trend(self) -> str:
        """Calculate if confidence is increasing, stable, or decreasing"""
        if len(self.snapshots) < 5:
            return "insufficient_data"

        recent = self.snapshots[-5:]
        confidences = [s.confidence for s in recent]

        # Simple linear trend
        avg_first_half = sum(confidences[:2]) / 2
        avg_second_half = sum(confidences[-2:]) / 2

        diff = avg_second_half - avg_first_half

        if diff > 0.1:
            return "increasing"
        elif diff < -0.1:
            return "decreasing"
        else:
            return "stable"

    def _calculate_probability_trend(self, archetype_value: str, recent_probs: List[Dict[str, float]]) -> float:
        """Calculate trend in probability for a specific archetype"""
        if len(recent_probs) < 3:
            return 0.0

        probs = [p.get(archetype_value, 0.0) for p in recent_probs]

        # Simple trend: compare first half to second half
        mid = len(probs) // 2
        first_half_avg = sum(probs[:mid]) / mid
        second_half_avg = sum(probs[mid:]) / (len(probs) - mid)

        return second_half_avg - first_half_avg

    def _interpret_shift(self, from_arch: UserArchetype, to_arch: UserArchetype) -> str:
        """Interpret what an archetype shift means"""
        shifts = {
            (UserArchetype.LEARNER, UserArchetype.EXPLORER): "Your curiosity is leading you to explore new possibilities!",
            (UserArchetype.LEARNER, UserArchetype.PRAGMATIST): "You're focusing on practical application of what you've learned.",
            (UserArchetype.LEARNER, UserArchetype.CREATOR): "Your deep understanding is enabling you to create custom solutions!",
            (UserArchetype.EXPLORER, UserArchetype.CREATOR): "Your discoveries are inspiring you to build your own tools!",
            (UserArchetype.EXPLORER, UserArchetype.PRAGMATIST): "You're focusing on proven, reliable solutions.",
            (UserArchetype.PRAGMATIST, UserArchetype.CREATOR): "Your need for automation is driving you to build custom solutions.",
            (UserArchetype.CREATOR, UserArchetype.PRAGMATIST): "You're standardizing your successful patterns.",
        }

        return shifts.get((from_arch, to_arch), "Your interaction style is evolving!")

    def _calculate_days_tracked(self) -> int:
        """Calculate days between first and last snapshot"""
        if len(self.snapshots) < 2:
            return 0

        first = datetime.fromisoformat(self.snapshots[0].timestamp)
        last = datetime.fromisoformat(self.snapshots[-1].timestamp)
        return (last - first).days

    def _count_archetype_changes(self) -> int:
        """Count number of times archetype changed"""
        if len(self.snapshots) < 2:
            return 0

        changes = 0
        prev_archetype = self.snapshots[0].archetype

        for snapshot in self.snapshots[1:]:
            if snapshot.archetype != prev_archetype:
                changes += 1
                prev_archetype = snapshot.archetype

        return changes

    def _calculate_current_streak(self) -> int:
        """Calculate days with current archetype"""
        if not self.snapshots:
            return 0

        current_archetype = self.snapshots[-1].archetype
        current_time = datetime.fromisoformat(self.snapshots[-1].timestamp)

        # Walk backwards counting days with same archetype
        for snapshot in reversed(self.snapshots[:-1]):
            if snapshot.archetype != current_archetype:
                break
            current_time = datetime.fromisoformat(snapshot.timestamp)

        # Return days from first snapshot of current archetype
        first_of_current = datetime.fromisoformat(current_time.isoformat())
        last = datetime.fromisoformat(self.snapshots[-1].timestamp)

        return (last - first_of_current).days

    def _load_snapshots(self) -> List[ArchetypeSnapshot]:
        """Load snapshots from disk"""
        if not self.evolution_file.exists():
            return []

        snapshots = []
        with open(self.evolution_file, 'r') as f:
            for line in f:
                data = json.loads(line)
                snapshot = ArchetypeSnapshot(
                    archetype=UserArchetype(data['archetype']),
                    confidence=data['confidence'],
                    probabilities=data['probabilities'],
                    technical_level=TechnicalLevel(data['technical_level']),
                    timestamp=data['timestamp'],
                    data_quality=data['data_quality']
                )
                snapshots.append(snapshot)

        return snapshots

    def _save_snapshot(self, snapshot: ArchetypeSnapshot):
        """Append snapshot to disk (JSONL format)"""
        with open(self.evolution_file, 'a') as f:
            data = {
                'archetype': snapshot.archetype.value,
                'confidence': snapshot.confidence,
                'probabilities': snapshot.probabilities,
                'technical_level': snapshot.technical_level.value,
                'timestamp': snapshot.timestamp,
                'data_quality': snapshot.data_quality
            }
            f.write(json.dumps(data) + '\n')

    def _snapshot_to_dict(self, snapshot: ArchetypeSnapshot) -> Dict:
        """Convert snapshot to dictionary for JSON serialization"""
        return {
            'archetype': snapshot.archetype.value,
            'confidence': snapshot.confidence,
            'probabilities': snapshot.probabilities,
            'technical_level': snapshot.technical_level.value,
            'timestamp': snapshot.timestamp,
            'data_quality': snapshot.data_quality
        }


def get_evolution_tracker(user_id: str = "default_user") -> ArchetypeEvolutionTracker:
    """Get evolution tracker for a user"""
    global _evolution_trackers

    if user_id not in _evolution_trackers:
        _evolution_trackers[user_id] = ArchetypeEvolutionTracker(user_id)

    return _evolution_trackers[user_id]


# Global registry of evolution trackers (one per user)
_evolution_trackers: Dict[str, ArchetypeEvolutionTracker] = {}
