"""
Entropy (Diversity) Calculator

Measures the exploration and learning diversity of user interactions.
Higher scores indicate healthy curiosity and learning behavior.

Components:
- Query diversity (topic breadth)
- Package exploration (category diversity)
- Learning progression (complexity growth)
"""

from typing import List
from collections import Counter
import logging

from .matl_types import Interaction

logger = logging.getLogger(__name__)


class EntropyCalculator:
    """
    Calculate Entropy (Diversity) score.

    Score Range: 0.0-1.0
    - 0.0: Narrow, repetitive behavior
    - 0.5: Moderate diversity
    - 1.0: High exploration and learning
    """

    def __init__(self):
        # Minimum interactions needed for reliable score
        self.min_interactions = 5

        # Common operation types for categorization
        self.operation_categories = {
            'search': 'exploration',
            'install': 'adoption',
            'update': 'maintenance',
            'remove': 'curation',
            'config': 'customization',
            'flake': 'development'
        }

    def calculate(self, interactions: List[Interaction]) -> float:
        """
        Calculate Entropy (diversity) score from user interactions.

        Args:
            interactions: List of user interactions

        Returns:
            float: Entropy score (0.0-1.0)
        """
        if not interactions:
            return 0.0

        if len(interactions) < self.min_interactions:
            # Not enough data, return neutral score
            return 0.5

        # Calculate sub-components
        query_diversity = self._calculate_query_diversity(interactions)
        operation_diversity = self._calculate_operation_diversity(interactions)
        learning_progression = self._calculate_learning_progression(interactions)

        # Weighted combination
        # Query diversity is most important (50%)
        # Operation diversity is secondary (30%)
        # Learning progression is tertiary (20%)
        entropy = (
            0.5 * query_diversity +
            0.3 * operation_diversity +
            0.2 * learning_progression
        )

        return max(0.0, min(1.0, entropy))  # Clamp to [0, 1]

    def _calculate_query_diversity(self, interactions: List[Interaction]) -> float:
        """
        Calculate query topic diversity.

        Measures:
        - Unique words across all queries
        - Topic breadth (different subjects)
        - Query uniqueness ratio

        Returns:
            float: Query diversity score (0.0-1.0)
        """
        if not interactions:
            return 0.0

        queries = [i.query.lower().strip() for i in interactions]
        total_queries = len(queries)

        # Unique queries ratio
        unique_queries = len(set(queries))
        uniqueness_ratio = unique_queries / total_queries

        # Vocabulary richness (unique words / total words)
        all_words = []
        for query in queries:
            words = query.split()
            all_words.extend(words)

        total_words = len(all_words)
        unique_words = len(set(all_words))

        vocabulary_richness = unique_words / total_words if total_words > 0 else 0.0

        # Topic breadth (simplified: count of different first words)
        # More sophisticated would use NLP topic modeling
        first_words = [query.split()[0] if query.split() else '' for query in queries]
        unique_first_words = len(set(first_words))
        topic_breadth = min(1.0, unique_first_words / 5.0)  # Normalize by 5 topics

        # Combine metrics
        diversity = (
            0.4 * uniqueness_ratio +
            0.4 * vocabulary_richness +
            0.2 * topic_breadth
        )

        return max(0.0, min(1.0, diversity))

    def _calculate_operation_diversity(self, interactions: List[Interaction]) -> float:
        """
        Calculate operation type diversity.

        Measures:
        - Variety of operation types (search, install, update, etc.)
        - Package exploration breadth
        - Balance between exploration and exploitation

        Returns:
            float: Operation diversity score (0.0-1.0)
        """
        if not interactions:
            return 0.0

        # Count operation types
        operation_types = [i.operation_type for i in interactions]
        unique_operations = len(set(operation_types))
        total_operations = len(operation_types)

        # Operation type diversity (Shannon entropy approximation)
        operation_counts = Counter(operation_types)
        operation_diversity = 0.0

        if total_operations > 0:
            # Simple diversity: unique / potential_max
            # Typical user might use 3-5 different operation types
            operation_diversity = min(1.0, unique_operations / 5.0)

        # Balance check: exploration (search) vs adoption (install)
        search_count = sum(1 for op in operation_types if op == 'search')
        install_count = sum(1 for op in operation_types if op == 'install')

        balance_score = 1.0
        if total_operations > 0:
            search_ratio = search_count / total_operations
            # Ideal: 40-70% search, rest is adoption/maintenance
            if 0.4 <= search_ratio <= 0.7:
                balance_score = 1.0
            elif search_ratio < 0.4:
                # Too little exploration
                balance_score = search_ratio / 0.4
            else:
                # Too much exploration, not enough action
                balance_score = max(0.5, 1.0 - (search_ratio - 0.7) * 2)

        # Package exploration (unique packages encountered)
        packages_found = sum(i.packages_found or 0 for i in interactions)
        packages_installed = sum(i.packages_installed or 0 for i in interactions)

        exploration_score = 1.0
        if packages_found > 0:
            # Healthy ratio: 10-30% installation rate
            install_ratio = packages_installed / packages_found if packages_found > 0 else 0
            if 0.1 <= install_ratio <= 0.3:
                exploration_score = 1.0
            elif install_ratio < 0.1:
                # Exploring but not adopting (indecisive)
                exploration_score = 0.7
            else:
                # Installing too much without exploration (impulsive)
                exploration_score = 0.6

        # Combine metrics
        diversity = (
            0.5 * operation_diversity +
            0.3 * balance_score +
            0.2 * exploration_score
        )

        return max(0.0, min(1.0, diversity))

    def _calculate_learning_progression(self, interactions: List[Interaction]) -> float:
        """
        Calculate learning and growth progression.

        Measures:
        - Increasing query complexity over time
        - Success rate improvement
        - Expanding operation repertoire

        Returns:
            float: Learning progression score (0.0-1.0)
        """
        if len(interactions) < self.min_interactions:
            return 0.5  # Neutral for insufficient data

        # Split into early and later interactions
        split_point = len(interactions) // 2
        early = interactions[:split_point]
        later = interactions[split_point:]

        # Query complexity growth (query length as proxy)
        early_avg_length = sum(len(i.query) for i in early) / len(early) if early else 0.0
        later_avg_length = sum(len(i.query) for i in later) / len(later) if later else 0.0

        complexity_growth = 0.5  # Default neutral
        if early_avg_length > 0:
            growth_ratio = later_avg_length / early_avg_length
            # Ideal: 1.1-1.5x growth (10-50% longer queries)
            if 1.1 <= growth_ratio <= 1.5:
                complexity_growth = 1.0
            elif growth_ratio < 1.1:
                # Stagnant or regressing
                complexity_growth = max(0.3, growth_ratio)
            else:
                # Growing but possibly too fast (copying?)
                complexity_growth = max(0.7, 1.0 - (growth_ratio - 1.5) * 0.2)

        # Success rate improvement
        early_success = sum(1 for i in early if i.success) / len(early) if early else 0.0
        later_success = sum(1 for i in later if i.success) / len(later) if later else 0.0

        success_improvement = 0.5  # Default neutral
        if later_success >= early_success:
            # Improving or maintaining (good)
            improvement = later_success - early_success
            success_improvement = min(1.0, 0.7 + improvement * 2)
        else:
            # Declining (learning curve dip is ok)
            decline = early_success - later_success
            success_improvement = max(0.3, 0.7 - decline * 2)

        # Operation repertoire expansion
        early_operations = set(i.operation_type for i in early)
        later_operations = set(i.operation_type for i in later)

        repertoire_growth = 0.5  # Default neutral
        if len(early_operations) > 0:
            new_operations = later_operations - early_operations
            growth_count = len(new_operations)
            # Ideal: 1-2 new operation types learned
            if growth_count >= 1:
                repertoire_growth = min(1.0, 0.7 + growth_count * 0.15)
            else:
                # Not learning new operations (but not bad)
                repertoire_growth = 0.6

        # Combine metrics
        progression = (
            0.4 * complexity_growth +
            0.4 * success_improvement +
            0.2 * repertoire_growth
        )

        return max(0.0, min(1.0, progression))

    def get_explanation(self, interactions: List[Interaction]) -> dict:
        """
        Get detailed explanation of Entropy score.

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
        query_diversity = self._calculate_query_diversity(interactions)
        operation_diversity = self._calculate_operation_diversity(interactions)
        learning_progression = self._calculate_learning_progression(interactions)

        return {
            'score': score,
            'components': {
                'query_diversity': {
                    'score': query_diversity,
                    'weight': 0.5,
                    'description': 'Topic breadth and query uniqueness'
                },
                'operation_diversity': {
                    'score': operation_diversity,
                    'weight': 0.3,
                    'description': 'Variety of operation types and balance'
                },
                'learning_progression': {
                    'score': learning_progression,
                    'weight': 0.2,
                    'description': 'Growth in complexity and capability'
                }
            },
            'interpretation': self._interpret_score(score),
            'interactions_analyzed': len(interactions)
        }

    def _interpret_score(self, score: float) -> str:
        """Interpret Entropy score for users"""
        if score >= 0.8:
            return "Excellent - High exploration and learning"
        elif score >= 0.6:
            return "Good - Healthy curiosity and diversity"
        elif score >= 0.4:
            return "Fair - Some exploration but limited"
        else:
            return "Low - Narrow or repetitive behavior"
