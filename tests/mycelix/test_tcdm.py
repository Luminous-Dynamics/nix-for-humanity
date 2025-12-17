"""Tests for TCDM (Temporal Consistency Distribution Metric) Calculator"""

import pytest
from datetime import datetime, timedelta

from luminous_nix.mycelix.trust import Interaction
from luminous_nix.mycelix.trust.tcdm import TCDMCalculator


class TestTCDMCalculator:
    """Test TCDM Calculator"""

    @pytest.fixture
    def calculator(self):
        """Create TCDM calculator instance"""
        return TCDMCalculator()

    def test_empty_interactions(self, calculator):
        """Test with no interactions"""
        score = calculator.calculate([])
        assert score == 0.0

    def test_insufficient_interactions(self, calculator):
        """Test with fewer than minimum interactions"""
        interactions = [
            Interaction(
                timestamp=datetime.now(),
                operation_type="search",
                query="test",
                success=True,
                duration_ms=1000.0,
                user_did="did:mycelix:test",
                assurance_level="E0"
            )
        ]

        # Should return neutral score (0.5) for insufficient data
        score = calculator.calculate(interactions)
        assert score == 0.5

    def test_consistent_human_timing_scores_high(self, calculator):
        """Test that consistent human-like timing gets high scores"""
        # Create interactions with natural human timing (30s - 5min intervals)
        interactions = []
        base_time = datetime.now()

        intervals = [30, 45, 120, 90, 180, 60, 150, 75, 240, 100]  # seconds
        current_time = base_time

        for i, interval in enumerate(intervals):
            interactions.append(Interaction(
                timestamp=current_time,
                operation_type="search",
                query=f"query {i}",
                success=True,
                duration_ms=1000.0,
                user_did="did:mycelix:test",
                assurance_level="E0"
            ))
            current_time += timedelta(seconds=interval)

        score = calculator.calculate(interactions)
        # Should score well (> 0.6) for natural human timing
        assert score > 0.6

    def test_bot_like_regular_timing_scores_low(self, calculator):
        """Test that perfectly regular timing (bot-like) scores lower"""
        # Create interactions with exact 10-second intervals (bot-like)
        interactions = []
        base_time = datetime.now()

        for i in range(10):
            interactions.append(Interaction(
                timestamp=base_time + timedelta(seconds=i * 10),
                operation_type="search",
                query=f"query {i}",
                success=True,
                duration_ms=1000.0,
                user_did="did:mycelix:test",
                assurance_level="E0"
            ))

        score = calculator.calculate(interactions)
        # Should score lower (< 0.7) for bot-like regularity
        assert score < 0.7

    def test_suspiciously_fast_actions_score_low(self, calculator):
        """Test that very fast actions (<2s) score lower"""
        # Create interactions with <1s intervals (too fast for human)
        interactions = []
        base_time = datetime.now()

        for i in range(10):
            interactions.append(Interaction(
                timestamp=base_time + timedelta(milliseconds=i * 500),  # 0.5s intervals
                operation_type="search",
                query=f"query {i}",
                success=True,
                duration_ms=1000.0,
                user_did="did:mycelix:test",
                assurance_level="E0"
            ))

        score = calculator.calculate(interactions)
        # Should score low (< 0.5) for impossibly fast actions
        assert score < 0.5

    def test_natural_session_breaks(self, calculator):
        """Test that natural session breaks (>30min) are recognized"""
        interactions = []
        base_time = datetime.now()

        # Session 1: 5 interactions over 10 minutes
        for i in range(5):
            interactions.append(Interaction(
                timestamp=base_time + timedelta(minutes=i * 2),
                operation_type="search",
                query=f"session1_query{i}",
                success=True,
                duration_ms=1000.0,
                user_did="did:mycelix:test",
                assurance_level="E0"
            ))

        # Break of 45 minutes (natural session gap)
        base_time += timedelta(minutes=55)

        # Session 2: 5 interactions over 10 minutes
        for i in range(5):
            interactions.append(Interaction(
                timestamp=base_time + timedelta(minutes=i * 2),
                operation_type="search",
                query=f"session2_query{i}",
                success=True,
                duration_ms=1000.0,
                user_did="did:mycelix:test",
                assurance_level="E0"
            ))

        score = calculator.calculate(interactions)
        # Should score reasonably (> 0.5) for natural session patterns
        assert score > 0.5

    def test_circadian_rhythm_waking_hours(self, calculator):
        """Test that activity during waking hours scores well"""
        # Create interactions during typical waking hours (9am - 9pm)
        interactions = []
        base_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)

        for i in range(10):
            # Spread across waking hours (9am - 9pm)
            hour_offset = (i * 60) // 10  # Minutes spread across 10 hours
            interactions.append(Interaction(
                timestamp=base_date + timedelta(minutes=hour_offset),
                operation_type="search",
                query=f"query {i}",
                success=True,
                duration_ms=1000.0,
                user_did="did:mycelix:test",
                assurance_level="E0"
            ))

        score = calculator.calculate(interactions)
        explanation = calculator.get_explanation(interactions)

        # Should have good circadian alignment
        assert explanation['components']['circadian_alignment']['score'] > 0.8

    def test_circadian_rhythm_sleep_hours(self, calculator):
        """Test that excessive activity during sleep hours scores lower"""
        # Create interactions during typical sleep hours (11pm - 6am)
        interactions = []
        base_date = datetime.now().replace(hour=23, minute=0, second=0, microsecond=0)

        for i in range(10):
            # All during sleep hours
            interactions.append(Interaction(
                timestamp=base_date + timedelta(minutes=i * 30),
                operation_type="search",
                query=f"query {i}",
                success=True,
                duration_ms=1000.0,
                user_did="did:mycelix:test",
                assurance_level="E0"
            ))

        score = calculator.calculate(interactions)
        explanation = calculator.get_explanation(interactions)

        # Should have lower circadian alignment
        assert explanation['components']['circadian_alignment']['score'] < 0.6

    def test_get_explanation(self, calculator):
        """Test that explanation provides component breakdown"""
        interactions = []
        base_time = datetime.now()

        for i in range(10):
            interactions.append(Interaction(
                timestamp=base_time + timedelta(minutes=i * 5),
                operation_type="search",
                query=f"query {i}",
                success=True,
                duration_ms=1000.0,
                user_did="did:mycelix:test",
                assurance_level="E0"
            ))

        explanation = calculator.get_explanation(interactions)

        # Check structure
        assert 'score' in explanation
        assert 'components' in explanation
        assert 'interpretation' in explanation
        assert 'interactions_analyzed' in explanation

        # Check components
        components = explanation['components']
        assert 'interval_consistency' in components
        assert 'session_naturalness' in components
        assert 'circadian_alignment' in components

        # Each component should have score, weight, description
        for component in components.values():
            assert 'score' in component
            assert 'weight' in component
            assert 'description' in component

        # Verify weights sum to 1.0
        total_weight = sum(c['weight'] for c in components.values())
        assert abs(total_weight - 1.0) < 0.01

        # Verify interactions count
        assert explanation['interactions_analyzed'] == 10

    def test_score_clamping(self, calculator):
        """Test that scores are always clamped to [0, 1]"""
        # Even with extreme inputs, score should be in valid range
        interactions = []
        base_time = datetime.now()

        for i in range(10):
            interactions.append(Interaction(
                timestamp=base_time + timedelta(seconds=i * 30),
                operation_type="search",
                query=f"test {i}",
                success=True,
                duration_ms=1000.0,
                user_did="did:mycelix:test",
                assurance_level="E0"
            ))

        score = calculator.calculate(interactions)
        assert 0.0 <= score <= 1.0


# Integration test
def test_tcdm_realistic_scenario():
    """Test TCDM with realistic user interaction patterns"""
    calculator = TCDMCalculator()

    # Simulate a genuine user over 2 days
    interactions = []
    day1 = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    day2 = day1 + timedelta(days=1)

    # Day 1: Morning session (9am - 10am)
    morning_intervals = [120, 180, 90, 240, 150]  # seconds (natural variation)
    current_time = day1
    for i, interval in enumerate(morning_intervals):
        interactions.append(Interaction(
            timestamp=current_time,
            operation_type="search",
            query=f"morning_query_{i}",
            success=True,
            duration_ms=1500.0,
            user_did="did:mycelix:test:user",
            assurance_level="E0"
        ))
        current_time += timedelta(seconds=interval)

    # Day 1: Afternoon session (2pm - 3pm)
    afternoon_start = day1.replace(hour=14)
    afternoon_intervals = [180, 240, 120, 200, 160]
    current_time = afternoon_start
    for i, interval in enumerate(afternoon_intervals):
        interactions.append(Interaction(
            timestamp=current_time,
            operation_type="search",
            query=f"afternoon_query_{i}",
            success=True,
            duration_ms=1200.0,
            user_did="did:mycelix:test:user",
            assurance_level="E0"
        ))
        current_time += timedelta(seconds=interval)

    # Day 2: Morning session (10am - 11am)
    morning2_start = day2.replace(hour=10)
    morning2_intervals = [150, 200, 180, 210, 170]
    current_time = morning2_start
    for i, interval in enumerate(morning2_intervals):
        interactions.append(Interaction(
            timestamp=current_time,
            operation_type="search",
            query=f"day2_query_{i}",
            success=True,
            duration_ms=1400.0,
            user_did="did:mycelix:test:user",
            assurance_level="E0"
        ))
        current_time += timedelta(seconds=interval)

    # Calculate score
    score = calculator.calculate(interactions)
    explanation = calculator.get_explanation(interactions)

    # Should show good temporal consistency for natural human behavior
    assert score > 0.7  # Good score for natural human timing
    assert explanation['components']['interval_consistency']['score'] > 0.6
    assert explanation['components']['session_naturalness']['score'] > 0.7
    assert explanation['components']['circadian_alignment']['score'] > 0.8

    print(f"✅ TCDM realistic scenario test passed!")
    print(f"   Score: {score:.3f}")
    print(f"   Interval Consistency: {explanation['components']['interval_consistency']['score']:.3f}")
    print(f"   Session Naturalness: {explanation['components']['session_naturalness']['score']:.3f}")
    print(f"   Circadian Alignment: {explanation['components']['circadian_alignment']['score']:.3f}")
    print(f"   Interpretation: {explanation['interpretation']}")
