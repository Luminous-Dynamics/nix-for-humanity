"""
PoGQ (Proof of Genuine Query) Calculator

Measures the authenticity and genuineness of user queries.
Higher scores indicate more genuine, human-like interactions.

Components:
- Query diversity (unique vs repetitive)
- Semantic coherence (meaningful vs random)
- Learning progression (improving over time)
"""

from typing import List
from collections import Counter
import logging

from .matl_types import Interaction

logger = logging.getLogger(__name__)


class PoGQCalculator:
    """
    Calculate Proof of Genuine Query (PoGQ) score.

    Score Range: 0.0-1.0
    - 0.0: Bot-like, suspicious
    - 0.5: Neutral, average
    - 1.0: Highly genuine, human-like
    """

    def __init__(self):
        # Minimum interactions needed for reliable score
        self.min_interactions = 5

    def calculate(self, interactions: List[Interaction]) -> float:
        """
        Calculate PoGQ score from user interactions.

        Args:
            interactions: List of user interactions

        Returns:
            float: PoGQ score (0.0-1.0)
        """
        if not interactions:
            return 0.0

        if len(interactions) < self.min_interactions:
            # Not enough data, return neutral score
            return 0.5

        # Calculate sub-components
        diversity_score = self._calculate_diversity(interactions)
        coherence_score = self._calculate_coherence(interactions)
        progression_score = self._calculate_progression(interactions)

        # Weighted combination
        # Diversity is most important (50%)
        # Coherence is secondary (30%)
        # Progression is tertiary (20%)
        pogq = (
            0.5 * diversity_score +
            0.3 * coherence_score +
            0.2 * progression_score
        )

        return max(0.0, min(1.0, pogq))  # Clamp to [0, 1]

    def _calculate_diversity(self, interactions: List[Interaction]) -> float:
        """
        Calculate query diversity score.

        Measures:
        - Unique queries vs total queries
        - Vocabulary diversity
        - Pattern detection (bot-like repetition)

        Returns:
            float: Diversity score (0.0-1.0)
        """
        queries = [i.query.lower().strip() for i in interactions]
        total = len(queries)

        if total == 0:
            return 0.0

        # Count unique queries
        unique = len(set(queries))

        # Basic diversity: unique / total
        basic_diversity = unique / total

        # Penalize extreme repetition (bot indicator)
        query_counts = Counter(queries)
        most_common_count = query_counts.most_common(1)[0][1] if query_counts else 0
        repetition_ratio = most_common_count / total

        # High repetition is suspicious
        repetition_penalty = 0.0
        if repetition_ratio > 0.5:  # More than 50% are the same query
            repetition_penalty = (repetition_ratio - 0.5) * 2  # Scale to [0, 1]

        # Vocabulary diversity (unique words across all queries)
        all_words = []
        for query in queries:
            words = query.split()
            all_words.extend(words)

        unique_words = len(set(all_words))
        total_words = len(all_words)
        vocab_diversity = unique_words / total_words if total_words > 0 else 0.0

        # Combine metrics
        diversity = (
            0.5 * basic_diversity +
            0.3 * vocab_diversity +
            0.2 * (1.0 - repetition_penalty)
        )

        return max(0.0, min(1.0, diversity))

    def _calculate_coherence(self, interactions: List[Interaction]) -> float:
        """
        Calculate semantic coherence score.

        Measures:
        - Query length appropriateness
        - Success rate (good queries succeed)
        - Error patterns

        Returns:
            float: Coherence score (0.0-1.0)
        """
        if not interactions:
            return 0.0

        # Length appropriateness
        # Very short (<2 chars) or very long (>100 chars) are suspicious
        appropriate_length_count = 0
        for interaction in interactions:
            query_len = len(interaction.query)
            if 2 <= query_len <= 100:
                appropriate_length_count += 1

        length_score = appropriate_length_count / len(interactions)

        # Success rate (genuine queries tend to succeed)
        success_count = sum(1 for i in interactions if i.success)
        success_rate = success_count / len(interactions)

        # Combine
        coherence = 0.6 * length_score + 0.4 * success_rate

        return max(0.0, min(1.0, coherence))

    def _calculate_progression(self, interactions: List[Interaction]) -> float:
        """
        Calculate learning progression score.

        Measures:
        - Query complexity increases over time
        - Success rate improves
        - Natural learning curve

        Returns:
            float: Progression score (0.0-1.0)
        """
        if len(interactions) < self.min_interactions:
            return 0.5  # Neutral for insufficient data

        # Split into early and later interactions
        split_point = len(interactions) // 2
        early = interactions[:split_point]
        later = interactions[split_point:]

        # Success rate progression
        early_success = sum(1 for i in early if i.success) / len(early) if early else 0.0
        later_success = sum(1 for i in later if i.success) / len(later) if later else 0.0

        # Improvement is good (but not required)
        success_improvement = max(0.0, later_success - early_success)

        # Query complexity progression (longer queries suggest learning)
        early_avg_len = sum(len(i.query) for i in early) / len(early) if early else 0.0
        later_avg_len = sum(len(i.query) for i in later) / len(later) if later else 0.0

        complexity_improvement = 0.0
        if early_avg_len > 0:
            complexity_ratio = later_avg_len / early_avg_len
            # Slight increase is good (1.0-1.5x)
            if 1.0 <= complexity_ratio <= 1.5:
                complexity_improvement = (complexity_ratio - 1.0) * 2  # Scale to [0, 1]

        # Combine
        progression = 0.5 * success_improvement + 0.5 * complexity_improvement

        # Clamp and add baseline (even no progression is okay)
        return max(0.3, min(1.0, 0.5 + progression))

    def get_explanation(self, interactions: List[Interaction]) -> dict:
        """
        Get detailed explanation of PoGQ score.

        Returns:
            dict: Score breakdown with explanations
        """
        if not interactions:
            return {
                'score': 0.0,
                'message': 'No interactions yet',
                'components': {}
            }

        score = self.calculate(interactions)
        diversity = self._calculate_diversity(interactions)
        coherence = self._calculate_coherence(interactions)
        progression = self._calculate_progression(interactions)

        return {
            'score': score,
            'components': {
                'diversity': {
                    'score': diversity,
                    'weight': 0.5,
                    'description': 'Query variety and uniqueness'
                },
                'coherence': {
                    'score': coherence,
                    'weight': 0.3,
                    'description': 'Query quality and success rate'
                },
                'progression': {
                    'score': progression,
                    'weight': 0.2,
                    'description': 'Learning and improvement over time'
                }
            },
            'interpretation': self._interpret_score(score),
            'interactions_analyzed': len(interactions)
        }

    def _interpret_score(self, score: float) -> str:
        """Interpret PoGQ score for users"""
        if score >= 0.8:
            return "Excellent - Highly genuine interactions"
        elif score >= 0.6:
            return "Good - Typical human-like patterns"
        elif score >= 0.4:
            return "Fair - Some room for improvement"
        else:
            return "Low - Unusual patterns detected"
