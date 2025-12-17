"""Tests for Credit Calculator (E/N/M weighted)"""

import pytest
from datetime import datetime

from luminous_nix.mycelix.credits import (
    CreditCalculator,
    CreditAmount,
    CreditWeights,
    get_calculator
)
from luminous_nix.mycelix.epistemic import EpistemicScore
from luminous_nix.mycelix.trust import Interaction


class TestCreditAmount:
    """Test CreditAmount value class"""

    def test_creation(self):
        """Test creating credit amount"""
        credits = CreditAmount(10.5)
        assert credits.value == 10.5

    def test_negative_raises_error(self):
        """Test that negative amounts raise error"""
        with pytest.raises(ValueError, match="cannot be negative"):
            CreditAmount(-5.0)

    def test_addition(self):
        """Test adding credit amounts"""
        a = CreditAmount(10.0)
        b = CreditAmount(5.5)
        result = a + b
        assert result.value == 15.5

    def test_subtraction(self):
        """Test subtracting credit amounts"""
        a = CreditAmount(10.0)
        b = CreditAmount(3.5)
        result = a - b
        assert result.value == 6.5

    def test_subtraction_insufficient_raises_error(self):
        """Test that negative result raises error"""
        a = CreditAmount(5.0)
        b = CreditAmount(10.0)
        with pytest.raises(ValueError, match="Insufficient"):
            a - b

    def test_multiplication(self):
        """Test multiplying by scalar"""
        credits = CreditAmount(10.0)
        result = credits * 2.5
        assert result.value == 25.0

    def test_division(self):
        """Test dividing by scalar"""
        credits = CreditAmount(10.0)
        result = credits / 2.0
        assert result.value == 5.0

    def test_equality(self):
        """Test equality comparison (with epsilon)"""
        a = CreditAmount(10.0)
        b = CreditAmount(10.0001)  # Within epsilon
        assert a == b

    def test_comparison(self):
        """Test comparison operators"""
        a = CreditAmount(5.0)
        b = CreditAmount(10.0)

        assert a < b
        assert a <= b
        assert b > a
        assert b >= a


class TestCreditWeights:
    """Test configurable credit weights"""

    def test_default_weights(self):
        """Test default weight configuration"""
        weights = CreditWeights()

        assert weights.base_rate == 10.0
        assert weights.e_multipliers[0] == 0.0  # E0
        assert weights.e_multipliers[4] == 3.0  # E4
        assert weights.n_multipliers[0] == 1.0  # N0
        assert weights.n_multipliers[3] == 4.0  # N3
        assert weights.m_multipliers[0] == 0.0  # M0
        assert weights.m_multipliers[3] == 3.0  # M3

    def test_custom_weights(self):
        """Test custom weight configuration"""
        weights = CreditWeights(
            base_rate=20.0,
            e_multipliers={0: 0.0, 1: 1.0, 2: 2.0, 3: 3.0, 4: 4.0}
        )

        assert weights.base_rate == 20.0
        assert weights.e_multipliers[1] == 1.0

    def test_get_e_multiplier(self):
        """Test E-axis multiplier lookup"""
        weights = CreditWeights()

        assert weights.get_e_multiplier(0.0) == 0.0   # E0
        assert weights.get_e_multiplier(0.25) == 0.5  # E1
        assert weights.get_e_multiplier(0.5) == 1.0   # E2
        assert weights.get_e_multiplier(0.75) == 2.0  # E3
        assert weights.get_e_multiplier(1.0) == 3.0   # E4

    def test_get_n_multiplier(self):
        """Test N-axis multiplier lookup"""
        weights = CreditWeights()

        assert weights.get_n_multiplier(0.0) == 1.0   # N0
        assert weights.get_n_multiplier(0.33) == 1.5  # N1
        assert weights.get_n_multiplier(0.67) == 2.5  # N2
        assert weights.get_n_multiplier(1.0) == 4.0   # N3

    def test_get_m_multiplier(self):
        """Test M-axis multiplier lookup"""
        weights = CreditWeights()

        assert weights.get_m_multiplier(0) == 0.0  # M0
        assert weights.get_m_multiplier(1) == 0.5  # M1
        assert weights.get_m_multiplier(2) == 1.5  # M2
        assert weights.get_m_multiplier(3) == 3.0  # M3

    def test_get_trust_modifier(self):
        """Test trust score modifier"""
        weights = CreditWeights()

        # trust_modifier = 0.5 + (matl_score * 0.5)
        assert weights.get_trust_modifier(0.0) == 0.5   # Low trust
        assert weights.get_trust_modifier(0.5) == 0.75  # Medium trust
        assert weights.get_trust_modifier(1.0) == 1.0   # High trust


class TestCreditCalculator:
    """Test credit calculation logic"""

    @pytest.fixture
    def calculator(self):
        """Create calculator with default weights"""
        return CreditCalculator()

    def test_calculator_creation(self, calculator):
        """Test creating calculator"""
        assert calculator is not None
        assert calculator.weights is not None

    def test_singleton_calculator(self):
        """Test singleton pattern"""
        c1 = get_calculator()
        c2 = get_calculator()
        assert c1 is c2

    def test_calculate_e4_n0_m3(self, calculator):
        """Test search operation (E4, N0, M3) - highest empirical + foundational"""
        score = EpistemicScore(
            epistemic_e=1.0,  # E4
            epistemic_n=0.0,  # N0
            epistemic_m=3     # M3
        )

        credits = calculator.calculate_credits(score, matl_score=0.8)

        # 10 × 3.0(E4) × 1.0(N0) × 3.0(M3) × 0.9(trust) = 81.0
        assert credits.value == pytest.approx(81.0)

    def test_calculate_e2_n0_m2(self, calculator):
        """Test install operation (E2, N0, M2) - baseline"""
        score = EpistemicScore(
            epistemic_e=0.5,  # E2
            epistemic_n=0.0,  # N0
            epistemic_m=2     # M2
        )

        credits = calculator.calculate_credits(score, matl_score=0.8)

        # 10 × 1.0(E2) × 1.0(N0) × 1.5(M2) × 0.9(trust) = 13.5
        assert credits.value == pytest.approx(13.5)

    def test_calculate_e1_n0_m1(self, calculator):
        """Test query operation (E1, N0, M1) - testimonial"""
        score = EpistemicScore(
            epistemic_e=0.25,  # E1
            epistemic_n=0.0,   # N0
            epistemic_m=1      # M1
        )

        credits = calculator.calculate_credits(score, matl_score=0.8)

        # 10 × 0.5(E1) × 1.0(N0) × 0.5(M1) × 0.9(trust) = 2.25
        assert credits.value == pytest.approx(2.25)

    def test_calculate_e0_m0_zero_credits(self, calculator):
        """Test failed operation (E0, M0) - zero credits"""
        score = EpistemicScore(
            epistemic_e=0.0,  # E0
            epistemic_n=0.0,  # N0
            epistemic_m=0     # M0
        )

        credits = calculator.calculate_credits(score, matl_score=0.8)

        # E0 or M0 → 0 credits
        assert credits.value == 0.0

    def test_calculate_with_low_trust(self, calculator):
        """Test that low trust reduces credits"""
        score = EpistemicScore(
            epistemic_e=1.0,  # E4
            epistemic_n=0.0,  # N0
            epistemic_m=3     # M3
        )

        # Low trust (0.2) → trust_modifier = 0.5 + (0.2 * 0.5) = 0.6
        credits = calculator.calculate_credits(score, matl_score=0.2)

        # 10 × 3.0 × 1.0 × 3.0 × 0.6 = 54.0
        assert credits.value == pytest.approx(54.0)

    def test_calculate_with_high_trust(self, calculator):
        """Test that high trust maximizes credits"""
        score = EpistemicScore(
            epistemic_e=1.0,  # E4
            epistemic_n=0.0,  # N0
            epistemic_m=3     # M3
        )

        # High trust (1.0) → trust_modifier = 1.0
        credits = calculator.calculate_credits(score, matl_score=1.0)

        # 10 × 3.0 × 1.0 × 3.0 × 1.0 = 90.0
        assert credits.value == pytest.approx(90.0)

    def test_calculate_from_interaction(self, calculator):
        """Test calculating from interaction directly"""
        interaction = Interaction(
            timestamp=datetime.now(),
            operation_type="search",
            query="firefox",
            success=True,
            duration_ms=1000.0,
            user_did="did:mycelix:test",
            assurance_level="E0",
            packages_found=5,
            epistemic_e=1.0,  # E4
            epistemic_n=0.0,  # N0
            epistemic_m=3     # M3
        )

        credits = calculator.calculate_from_interaction(interaction, matl_score=0.8)

        assert credits.value == pytest.approx(81.0)

    def test_calculate_from_interaction_without_enm_raises_error(self, calculator):
        """Test that interaction without E/N/M raises error"""
        interaction = Interaction(
            timestamp=datetime.now(),
            operation_type="search",
            query="test",
            success=True,
            duration_ms=1000.0,
            user_did="did:mycelix:test",
            assurance_level="E0",
            # Missing epistemic_e, epistemic_n, epistemic_m
        )

        with pytest.raises(ValueError, match="must have epistemic"):
            calculator.calculate_from_interaction(interaction)

    def test_get_breakdown(self, calculator):
        """Test detailed calculation breakdown"""
        score = EpistemicScore(
            epistemic_e=1.0,  # E4
            epistemic_n=0.0,  # N0
            epistemic_m=3     # M3
        )

        breakdown = calculator.get_breakdown(score, matl_score=0.8)

        assert breakdown['base_rate'] == 10.0
        assert breakdown['e_multiplier'] == 3.0
        assert breakdown['n_multiplier'] == 1.0
        assert breakdown['m_multiplier'] == 3.0
        assert breakdown['trust_modifier'] == pytest.approx(0.9)
        assert breakdown['total_credits'] == pytest.approx(81.0)
        assert '(E4, N0, M3)' in breakdown['coordinate']
        assert '10' in breakdown['formula']
        assert '81' in breakdown['formula']

    def test_create_transaction(self, calculator):
        """Test creating transaction from interaction"""
        interaction = Interaction(
            timestamp=datetime.now(),
            operation_type="install",
            query="vim",
            success=True,
            duration_ms=5000.0,
            user_did="did:mycelix:test",
            assurance_level="E0",
            packages_installed=1,
            epistemic_e=0.5,  # E2
            epistemic_n=0.0,  # N0
            epistemic_m=2     # M2
        )

        credits = CreditAmount(13.5)
        tx = calculator.create_transaction(interaction, credits, matl_score=0.8)

        assert tx.user_did == "did:mycelix:test"
        assert tx.amount.value == 13.5
        assert tx.epistemic_e == 0.5
        assert tx.epistemic_n == 0.0
        assert tx.epistemic_m == 2
        assert tx.matl_score == 0.8
        assert "install" in tx.description.lower()
        assert "vim" in tx.description
