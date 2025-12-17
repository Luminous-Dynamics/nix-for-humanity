"""Integration Tests for Credits System

Tests the complete flow:
1. Interaction with E/N/M classification
2. Credit calculation from epistemic coordinates
3. Credit ledger recording
4. Balance updates and transaction history
"""

import pytest
from pathlib import Path
from datetime import datetime
import tempfile

from luminous_nix.mycelix.trust import InteractionLogger, Interaction
from luminous_nix.mycelix.epistemic import EpistemicClassifier, EpistemicScore
from luminous_nix.mycelix.credits import (
    CreditCalculator,
    CreditLedger,
    CreditAmount,
    TransactionType
)


@pytest.fixture
def temp_dir():
    """Create temporary directory for test databases"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def interaction_logger(temp_dir):
    """Create interaction logger with temp directory"""
    return InteractionLogger(storage_path=temp_dir / "interactions")


@pytest.fixture
def calculator():
    """Create credit calculator with default weights"""
    return CreditCalculator()


@pytest.fixture
def ledger(temp_dir):
    """Create credit ledger with temp database"""
    return CreditLedger(db_path=temp_dir / "credits.db")


@pytest.fixture
def user_did():
    """Test user DID (simple string, no manager needed)"""
    return "did:mycelix:test-user"


class TestEndToEndFlow:
    """Test complete credits system flow"""

    def test_search_operation_earns_credits(
        self,
        interaction_logger,
        calculator,
        ledger,
        user_did
    ):
        """Test that a search operation earns the correct credits"""
        # Step 1: Log interaction with E/N/M classification
        interaction = Interaction(
            timestamp=datetime.now(),
            operation_type="search",
            query="firefox",
            success=True,
            duration_ms=1000.0,
            user_did=user_did,
            assurance_level="E0",
            packages_found=5,
            # E/N/M classification for successful search
            epistemic_e=1.0,   # E4: Public reproducible
            epistemic_n=0.0,   # N0: Personal query
            epistemic_m=3      # M3: Foundational (NixOS cache)
        )
        interaction_logger.log_interaction(interaction)

        # Step 2: Calculate credits from interaction
        matl_score = 0.8  # Good trust score
        credits_earned = calculator.calculate_from_interaction(interaction, matl_score)

        # Expected: 10 × 3.0(E4) × 1.0(N0) × 3.0(M3) × 0.9(trust) = 81.0
        assert credits_earned.value == pytest.approx(81.0)

        # Step 3: Create transaction and record in ledger
        tx = calculator.create_transaction(interaction, credits_earned, matl_score)
        balance = ledger.earn_credits(user_did, credits_earned, tx)

        # Step 4: Verify balance updated correctly
        assert balance.total_earned.value == 81.0
        assert balance.current_balance.value == 81.0

        # Step 5: Verify transaction history
        history = ledger.get_transaction_history(user_did)
        assert len(history) == 1
        assert history[0].amount.value == 81.0
        assert history[0].tx_type == TransactionType.EARN
        assert "search" in history[0].description.lower()

    def test_install_operation_earns_credits(
        self,
        interaction_logger,
        calculator,
        ledger,
        user_did
    ):
        """Test that an install operation earns the correct credits"""
        # Step 1: Log interaction
        interaction = Interaction(
            timestamp=datetime.now(),
            operation_type="install",
            query="vim",
            success=True,
            duration_ms=5000.0,
            user_did=user_did,
            assurance_level="E0",
            packages_installed=1,
            # E/N/M classification for install
            epistemic_e=0.5,   # E2: Privately verifiable
            epistemic_n=0.0,   # N0: Personal
            epistemic_m=2      # M2: Persistent
        )
        interaction_logger.log_interaction(interaction)

        # Step 2: Calculate credits
        matl_score = 0.8
        credits_earned = calculator.calculate_from_interaction(interaction, matl_score)

        # Expected: 10 × 1.0(E2) × 1.0(N0) × 1.5(M2) × 0.9(trust) = 13.5
        assert credits_earned.value == pytest.approx(13.5)

        # Step 3: Record in ledger
        tx = calculator.create_transaction(interaction, credits_earned, matl_score)
        balance = ledger.earn_credits(user_did, credits_earned, tx)

        # Step 4: Verify balance
        assert balance.current_balance.value == pytest.approx(13.5)

    def test_failed_operation_earns_zero_credits(
        self,
        interaction_logger,
        calculator,
        ledger,
        user_did
    ):
        """Test that a failed operation earns 0 credits"""
        # Step 1: Log failed interaction
        interaction = Interaction(
            timestamp=datetime.now(),
            operation_type="install",
            query="nonexistent-package",
            success=False,
            duration_ms=2000.0,
            user_did=user_did,
            assurance_level="E0",
            # E/N/M classification for failed op
            epistemic_e=0.0,   # E0: Unverifiable (failed)
            epistemic_n=0.0,   # N0: Personal
            epistemic_m=0      # M0: Ephemeral (nothing happened)
        )
        interaction_logger.log_interaction(interaction)

        # Step 2: Calculate credits
        credits_earned = calculator.calculate_from_interaction(interaction)

        # Expected: 0 credits (E0 or M0 → 0)
        assert credits_earned.value == 0.0

        # Step 3: Record in ledger
        tx = calculator.create_transaction(interaction, credits_earned, 0.8)
        balance = ledger.earn_credits(user_did, credits_earned, tx)

        # Step 4: Verify no credits earned
        assert balance.current_balance.value == 0.0


class TestMultipleOperations:
    """Test accumulation of credits across multiple operations"""

    def test_credits_accumulate_across_operations(
        self,
        interaction_logger,
        calculator,
        ledger,
        user_did
    ):
        """Test that credits accumulate across multiple operations"""
        operations = [
            # Search (high value)
            {
                "type": "search",
                "query": "firefox",
                "e": 1.0, "n": 0.0, "m": 3,
                "expected": 81.0
            },
            # Install (medium value)
            {
                "type": "install",
                "query": "vim",
                "e": 0.5, "n": 0.0, "m": 2,
                "expected": 13.5
            },
            # Query (low value)
            {
                "type": "query",
                "query": "show config",
                "e": 0.25, "n": 0.0, "m": 1,
                "expected": 2.25
            }
        ]

        total_expected = 0.0
        for op in operations:
            # Create interaction with specific E/N/M values
            # Note: Not logging to avoid auto-classification overwriting our test values
            interaction = Interaction(
                timestamp=datetime.now(),
                operation_type=op["type"],
                query=op["query"],
                success=True,
                duration_ms=1000.0,
                user_did=user_did,
                assurance_level="E0",
                epistemic_e=op["e"],
                epistemic_n=op["n"],
                epistemic_m=op["m"]
            )

            # Calculate and record credits
            credits = calculator.calculate_from_interaction(interaction, matl_score=0.8)
            assert credits.value == pytest.approx(op["expected"])

            tx = calculator.create_transaction(interaction, credits, 0.8)
            ledger.earn_credits(user_did, credits, tx)

            total_expected += op["expected"]

        # Verify total balance
        balance = ledger.get_balance(user_did)
        assert balance.current_balance.value == pytest.approx(total_expected)
        assert balance.total_earned.value == pytest.approx(total_expected)

        # Verify transaction history
        history = ledger.get_transaction_history(user_did)
        assert len(history) == 3


class TestTrustModulation:
    """Test that trust scores modulate credit allocation"""

    def test_low_trust_reduces_credits(
        self,
        interaction_logger,
        calculator,
        ledger,
        user_did
    ):
        """Test that low trust score reduces credits earned"""
        # Note: Not logging to avoid auto-classification overwriting test values
        interaction = Interaction(
            timestamp=datetime.now(),
            operation_type="search",
            query="firefox",
            success=True,
            duration_ms=1000.0,
            user_did=user_did,
            assurance_level="E0",
            epistemic_e=1.0,  # E4
            epistemic_n=0.0,  # N0
            epistemic_m=3     # M3
        )

        # Low trust (0.2) → trust_modifier = 0.5 + (0.2 × 0.5) = 0.6
        low_trust_credits = calculator.calculate_from_interaction(
            interaction,
            matl_score=0.2
        )

        # Expected: 10 × 3.0 × 1.0 × 3.0 × 0.6 = 54.0
        assert low_trust_credits.value == pytest.approx(54.0)

    def test_high_trust_maximizes_credits(
        self,
        interaction_logger,
        calculator,
        ledger,
        user_did
    ):
        """Test that high trust score maximizes credits earned"""
        # Note: Not logging to avoid auto-classification overwriting test values
        interaction = Interaction(
            timestamp=datetime.now(),
            operation_type="search",
            query="firefox",
            success=True,
            duration_ms=1000.0,
            user_did=user_did,
            assurance_level="E0",
            epistemic_e=1.0,  # E4
            epistemic_n=0.0,  # N0
            epistemic_m=3     # M3
        )

        # High trust (1.0) → trust_modifier = 1.0
        high_trust_credits = calculator.calculate_from_interaction(
            interaction,
            matl_score=1.0
        )

        # Expected: 10 × 3.0 × 1.0 × 3.0 × 1.0 = 90.0
        assert high_trust_credits.value == pytest.approx(90.0)


class TestCreditEconomy:
    """Test credit spending and transfers"""

    def test_spend_credits_on_features(
        self,
        interaction_logger,
        calculator,
        ledger,
        user_did
    ):
        """Test spending credits on features"""
        # Earn credits first
        interaction = Interaction(
            timestamp=datetime.now(),
            operation_type="search",
            query="firefox",
            success=True,
            duration_ms=1000.0,
            user_did=user_did,
            assurance_level="E0",
            epistemic_e=1.0,
            epistemic_n=0.0,
            epistemic_m=3
        )
        credits = calculator.calculate_from_interaction(interaction, matl_score=0.8)
        tx = calculator.create_transaction(interaction, credits, 0.8)
        ledger.earn_credits(user_did, credits, tx)

        # Spend some credits
        balance = ledger.spend_credits(user_did, CreditAmount(30.0), "unlock premium feature")

        # Verify balance updated
        assert balance.total_spent.value == 30.0
        assert balance.current_balance.value == pytest.approx(81.0 - 30.0)

        # Verify transaction history
        history = ledger.get_transaction_history(user_did)
        assert len(history) == 2
        assert history[0].tx_type == TransactionType.SPEND

    def test_transfer_credits_between_users(
        self,
        interaction_logger,
        calculator,
        ledger
    ):
        """Test transferring credits between users"""
        # Create two users (simple DID strings)
        alice_did = "did:mycelix:alice"
        bob_did = "did:mycelix:bob"

        # Give alice some credits
        interaction = Interaction(
            timestamp=datetime.now(),
            operation_type="search",
            query="firefox",
            success=True,
            duration_ms=1000.0,
            user_did=alice_did,
            assurance_level="E0",
            epistemic_e=1.0,
            epistemic_n=0.0,
            epistemic_m=3
        )
        credits = calculator.calculate_from_interaction(interaction, matl_score=0.8)
        tx = calculator.create_transaction(interaction, credits, 0.8)
        ledger.earn_credits(alice_did, credits, tx)

        # Transfer to bob
        alice_balance, bob_balance = ledger.transfer_credits(
            alice_did,
            bob_did,
            CreditAmount(30.0),
            "help with config"
        )

        # Verify balances
        assert alice_balance.current_balance.value == pytest.approx(51.0)
        assert bob_balance.current_balance.value == 30.0

        # Verify both have transaction records
        alice_history = ledger.get_transaction_history(alice_did)
        bob_history = ledger.get_transaction_history(bob_did)

        assert len(alice_history) == 2  # earn + transfer_out
        assert len(bob_history) == 1    # transfer_in

        assert alice_history[0].tx_type == TransactionType.TRANSFER_OUT
        assert bob_history[0].tx_type == TransactionType.TRANSFER_IN


class TestSystemAnalytics:
    """Test system-wide credit analytics"""

    def test_leaderboard_tracks_top_earners(
        self,
        interaction_logger,
        calculator,
        ledger
    ):
        """Test leaderboard tracks top credit earners"""
        # Create multiple users with different earnings (simple DID strings)
        users = {
            "alice": "did:mycelix:alice",
            "bob": "did:mycelix:bob",
            "charlie": "did:mycelix:charlie"
        }
        expected_credits = {
            "alice": 81.0,   # E4, N0, M3
            "bob": 13.5,     # E2, N0, M2
            "charlie": 2.25  # E1, N0, M1
        }

        for name, expected in expected_credits.items():
            did = users[name]

            # Appropriate E/N/M for each credit level
            if expected == 81.0:
                e, n, m = 1.0, 0.0, 3
            elif expected == 13.5:
                e, n, m = 0.5, 0.0, 2
            else:
                e, n, m = 0.25, 0.0, 1

            interaction = Interaction(
                timestamp=datetime.now(),
                operation_type="search",
                query="test",
                success=True,
                duration_ms=1000.0,
                user_did=did,
                assurance_level="E0",
                epistemic_e=e,
                epistemic_n=n,
                epistemic_m=m
            )
            credits = calculator.calculate_from_interaction(interaction, matl_score=0.8)
            tx = calculator.create_transaction(interaction, credits, 0.8)
            ledger.earn_credits(did, credits, tx)

        # Get leaderboard
        leaderboard = ledger.get_leaderboard(limit=10)

        # Should be sorted by balance (highest first)
        assert len(leaderboard) == 3
        assert leaderboard[0].user_did == users["alice"]    # 81.0
        assert leaderboard[1].user_did == users["bob"]      # 13.5
        assert leaderboard[2].user_did == users["charlie"]  # 2.25
