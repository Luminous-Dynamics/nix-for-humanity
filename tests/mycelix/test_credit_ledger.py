"""Tests for Credit Ledger (SQLite-based)"""

import pytest
from pathlib import Path
from datetime import datetime
import tempfile

from luminous_nix.mycelix.credits import (
    CreditLedger,
    CreditAmount,
    CreditTransaction,
    CreditBalance,
    TransactionType
)


@pytest.fixture
def temp_db():
    """Create temporary database for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_credits.db"
        yield db_path


@pytest.fixture
def ledger(temp_db):
    """Create ledger with temporary database"""
    return CreditLedger(db_path=temp_db)


class TestCreditLedgerInitialization:
    """Test database initialization"""

    def test_creates_database_file(self, temp_db):
        """Test that ledger creates database file"""
        assert not temp_db.exists()

        ledger = CreditLedger(db_path=temp_db)

        assert temp_db.exists()

    def test_creates_tables(self, ledger, temp_db):
        """Test that ledger creates required tables"""
        import sqlite3
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()

        # Check credit_balances table
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='credit_balances'
        """)
        assert cursor.fetchone() is not None

        # Check credit_transactions table
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='credit_transactions'
        """)
        assert cursor.fetchone() is not None

        conn.close()

    def test_creates_indexes(self, ledger, temp_db):
        """Test that ledger creates indexes"""
        import sqlite3
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='index'
        """)
        indexes = [row[0] for row in cursor.fetchall()]

        # Should have user_transactions and tx_type indexes
        assert 'idx_user_transactions' in indexes
        assert 'idx_tx_type' in indexes

        conn.close()


class TestBalanceOperations:
    """Test balance creation and retrieval"""

    def test_get_balance_creates_new(self, ledger):
        """Test getting balance for new user creates balance"""
        balance = ledger.get_balance("did:mycelix:alice")

        assert balance.user_did == "did:mycelix:alice"
        assert balance.total_earned.value == 0.0
        assert balance.total_spent.value == 0.0
        assert balance.current_balance.value == 0.0

    def test_get_balance_retrieves_existing(self, ledger):
        """Test getting existing balance retrieves it"""
        # Create a balance by earning credits
        tx = CreditTransaction(
            timestamp=datetime.now(),
            user_did="did:mycelix:bob",
            tx_type=TransactionType.EARN,
            amount=CreditAmount(50.0),
            description="test"
        )
        ledger.earn_credits("did:mycelix:bob", CreditAmount(50.0), tx)

        # Retrieve it
        balance = ledger.get_balance("did:mycelix:bob")

        assert balance.user_did == "did:mycelix:bob"
        assert balance.current_balance.value == 50.0


class TestEarnCredits:
    """Test earning credits"""

    def test_earn_credits_updates_balance(self, ledger):
        """Test earning credits updates balance"""
        tx = CreditTransaction(
            timestamp=datetime.now(),
            user_did="did:mycelix:alice",
            tx_type=TransactionType.EARN,
            amount=CreditAmount(25.5),
            description="search operation",
            epistemic_e=1.0,
            epistemic_n=0.0,
            epistemic_m=3,
            matl_score=0.8
        )

        balance = ledger.earn_credits("did:mycelix:alice", CreditAmount(25.5), tx)

        assert balance.total_earned.value == 25.5
        assert balance.current_balance.value == 25.5

    def test_earn_credits_multiple_times(self, ledger):
        """Test earning credits accumulates"""
        tx1 = CreditTransaction(
            timestamp=datetime.now(),
            user_did="did:mycelix:alice",
            tx_type=TransactionType.EARN,
            amount=CreditAmount(10.0),
            description="op1"
        )
        tx2 = CreditTransaction(
            timestamp=datetime.now(),
            user_did="did:mycelix:alice",
            tx_type=TransactionType.EARN,
            amount=CreditAmount(15.0),
            description="op2"
        )

        ledger.earn_credits("did:mycelix:alice", CreditAmount(10.0), tx1)
        balance = ledger.earn_credits("did:mycelix:alice", CreditAmount(15.0), tx2)

        assert balance.total_earned.value == 25.0
        assert balance.current_balance.value == 25.0

    def test_earn_credits_records_transaction(self, ledger):
        """Test earning credits creates transaction record"""
        tx = CreditTransaction(
            timestamp=datetime.now(),
            user_did="did:mycelix:alice",
            tx_type=TransactionType.EARN,
            amount=CreditAmount(30.0),
            description="install firefox",
            epistemic_e=0.5,
            epistemic_n=0.0,
            epistemic_m=2,
            matl_score=0.9
        )

        ledger.earn_credits("did:mycelix:alice", CreditAmount(30.0), tx)

        history = ledger.get_transaction_history("did:mycelix:alice")

        assert len(history) == 1
        assert history[0].amount.value == 30.0
        assert history[0].tx_type == TransactionType.EARN
        assert history[0].description == "install firefox"
        assert history[0].epistemic_e == 0.5
        assert history[0].matl_score == 0.9


class TestSpendCredits:
    """Test spending credits"""

    def test_spend_credits_updates_balance(self, ledger):
        """Test spending credits updates balance"""
        # First earn some credits
        tx = CreditTransaction(
            timestamp=datetime.now(),
            user_did="did:mycelix:alice",
            tx_type=TransactionType.EARN,
            amount=CreditAmount(50.0),
            description="earn"
        )
        ledger.earn_credits("did:mycelix:alice", CreditAmount(50.0), tx)

        # Then spend some
        balance = ledger.spend_credits("did:mycelix:alice", CreditAmount(20.0), "test spend")

        assert balance.total_spent.value == 20.0
        assert balance.current_balance.value == 30.0

    def test_spend_credits_insufficient_balance_raises_error(self, ledger):
        """Test spending more than balance raises error"""
        # Earn 10 credits
        tx = CreditTransaction(
            timestamp=datetime.now(),
            user_did="did:mycelix:alice",
            tx_type=TransactionType.EARN,
            amount=CreditAmount(10.0),
            description="earn"
        )
        ledger.earn_credits("did:mycelix:alice", CreditAmount(10.0), tx)

        # Try to spend 20 credits
        with pytest.raises(ValueError, match="Insufficient"):
            ledger.spend_credits("did:mycelix:alice", CreditAmount(20.0), "overspend")

    def test_spend_credits_records_transaction(self, ledger):
        """Test spending credits creates transaction record"""
        # Earn credits first
        tx = CreditTransaction(
            timestamp=datetime.now(),
            user_did="did:mycelix:alice",
            tx_type=TransactionType.EARN,
            amount=CreditAmount(50.0),
            description="earn"
        )
        ledger.earn_credits("did:mycelix:alice", CreditAmount(50.0), tx)

        # Spend credits
        ledger.spend_credits("did:mycelix:alice", CreditAmount(15.0), "buy feature")

        history = ledger.get_transaction_history("did:mycelix:alice")

        # Should have 2 transactions: earn and spend
        assert len(history) == 2
        spend_tx = history[0]  # Newest first
        assert spend_tx.tx_type == TransactionType.SPEND
        assert spend_tx.amount.value == 15.0
        assert spend_tx.description == "buy feature"


class TestTransferCredits:
    """Test transferring credits between users"""

    def test_transfer_updates_both_balances(self, ledger):
        """Test transfer updates sender and recipient balances"""
        # Give alice some credits
        tx = CreditTransaction(
            timestamp=datetime.now(),
            user_did="did:mycelix:alice",
            tx_type=TransactionType.EARN,
            amount=CreditAmount(100.0),
            description="earn"
        )
        ledger.earn_credits("did:mycelix:alice", CreditAmount(100.0), tx)

        # Transfer to bob
        from_balance, to_balance = ledger.transfer_credits(
            "did:mycelix:alice",
            "did:mycelix:bob",
            CreditAmount(30.0),
            "test transfer"
        )

        assert from_balance.current_balance.value == 70.0
        assert to_balance.current_balance.value == 30.0

    def test_transfer_insufficient_balance_raises_error(self, ledger):
        """Test transfer with insufficient balance raises error"""
        # Give alice 10 credits
        tx = CreditTransaction(
            timestamp=datetime.now(),
            user_did="did:mycelix:alice",
            tx_type=TransactionType.EARN,
            amount=CreditAmount(10.0),
            description="earn"
        )
        ledger.earn_credits("did:mycelix:alice", CreditAmount(10.0), tx)

        # Try to transfer 50 credits
        with pytest.raises(ValueError, match="Insufficient"):
            ledger.transfer_credits(
                "did:mycelix:alice",
                "did:mycelix:bob",
                CreditAmount(50.0),
                "overspend"
            )

    def test_transfer_records_both_transactions(self, ledger):
        """Test transfer creates transactions for both users"""
        # Give alice some credits
        tx = CreditTransaction(
            timestamp=datetime.now(),
            user_did="did:mycelix:alice",
            tx_type=TransactionType.EARN,
            amount=CreditAmount(100.0),
            description="earn"
        )
        ledger.earn_credits("did:mycelix:alice", CreditAmount(100.0), tx)

        # Transfer to bob
        ledger.transfer_credits(
            "did:mycelix:alice",
            "did:mycelix:bob",
            CreditAmount(25.0),
            "gift"
        )

        # Check alice's history
        alice_history = ledger.get_transaction_history("did:mycelix:alice")
        assert len(alice_history) == 2
        assert alice_history[0].tx_type == TransactionType.TRANSFER_OUT
        assert alice_history[0].amount.value == 25.0

        # Check bob's history
        bob_history = ledger.get_transaction_history("did:mycelix:bob")
        assert len(bob_history) == 1
        assert bob_history[0].tx_type == TransactionType.TRANSFER_IN
        assert bob_history[0].amount.value == 25.0


class TestTransactionHistory:
    """Test transaction history queries"""

    def test_get_transaction_history_returns_newest_first(self, ledger):
        """Test transaction history is sorted newest first"""
        # Create multiple transactions
        for i in range(3):
            tx = CreditTransaction(
                timestamp=datetime.now(),
                user_did="did:mycelix:alice",
                tx_type=TransactionType.EARN,
                amount=CreditAmount(10.0 * (i + 1)),
                description=f"op{i}"
            )
            ledger.earn_credits("did:mycelix:alice", CreditAmount(10.0 * (i + 1)), tx)

        history = ledger.get_transaction_history("did:mycelix:alice")

        # Should be newest first
        assert len(history) == 3
        assert history[0].amount.value == 30.0  # Last one created
        assert history[1].amount.value == 20.0
        assert history[2].amount.value == 10.0  # First one created

    def test_get_transaction_history_with_limit(self, ledger):
        """Test transaction history limit"""
        # Create 5 transactions
        for i in range(5):
            tx = CreditTransaction(
                timestamp=datetime.now(),
                user_did="did:mycelix:alice",
                tx_type=TransactionType.EARN,
                amount=CreditAmount(10.0),
                description=f"op{i}"
            )
            ledger.earn_credits("did:mycelix:alice", CreditAmount(10.0), tx)

        history = ledger.get_transaction_history("did:mycelix:alice", limit=3)

        assert len(history) == 3

    def test_get_transaction_history_filter_by_type(self, ledger):
        """Test filtering transaction history by type"""
        # Earn credits
        tx1 = CreditTransaction(
            timestamp=datetime.now(),
            user_did="did:mycelix:alice",
            tx_type=TransactionType.EARN,
            amount=CreditAmount(50.0),
            description="earn"
        )
        ledger.earn_credits("did:mycelix:alice", CreditAmount(50.0), tx1)

        # Spend credits
        ledger.spend_credits("did:mycelix:alice", CreditAmount(10.0), "spend")

        # Filter for EARN only
        earn_history = ledger.get_transaction_history(
            "did:mycelix:alice",
            tx_type=TransactionType.EARN
        )

        assert len(earn_history) == 1
        assert earn_history[0].tx_type == TransactionType.EARN


class TestStatisticsAndAnalytics:
    """Test system-wide statistics"""

    def test_get_total_credits_in_system(self, ledger):
        """Test getting total credits across all users"""
        # Give credits to multiple users
        for user in ["alice", "bob", "charlie"]:
            tx = CreditTransaction(
                timestamp=datetime.now(),
                user_did=f"did:mycelix:{user}",
                tx_type=TransactionType.EARN,
                amount=CreditAmount(100.0),
                description="earn"
            )
            ledger.earn_credits(f"did:mycelix:{user}", CreditAmount(100.0), tx)

        total = ledger.get_total_credits_in_system()

        assert total.value == 300.0

    def test_get_leaderboard(self, ledger):
        """Test leaderboard returns top earners"""
        # Give different amounts to users
        amounts = {"alice": 100.0, "bob": 50.0, "charlie": 150.0}

        for user, amount in amounts.items():
            tx = CreditTransaction(
                timestamp=datetime.now(),
                user_did=f"did:mycelix:{user}",
                tx_type=TransactionType.EARN,
                amount=CreditAmount(amount),
                description="earn"
            )
            ledger.earn_credits(f"did:mycelix:{user}", CreditAmount(amount), tx)

        leaderboard = ledger.get_leaderboard(limit=10)

        # Should be sorted by balance (highest first)
        assert len(leaderboard) == 3
        assert leaderboard[0].user_did == "did:mycelix:charlie"  # 150
        assert leaderboard[1].user_did == "did:mycelix:alice"    # 100
        assert leaderboard[2].user_did == "did:mycelix:bob"      # 50

    def test_get_stats(self, ledger):
        """Test system-wide statistics"""
        # Create some activity
        tx = CreditTransaction(
            timestamp=datetime.now(),
            user_did="did:mycelix:alice",
            tx_type=TransactionType.EARN,
            amount=CreditAmount(100.0),
            description="earn"
        )
        ledger.earn_credits("did:mycelix:alice", CreditAmount(100.0), tx)
        ledger.spend_credits("did:mycelix:alice", CreditAmount(20.0), "spend")

        stats = ledger.get_stats()

        assert stats['total_users'] == 1
        assert stats['total_credits'] == 80.0  # 100 - 20
        assert stats['total_earned'] == 100.0
        assert stats['total_spent'] == 20.0
        assert stats['total_transactions'] == 2
        assert stats['average_balance'] == 80.0


class TestConcurrencyAndACID:
    """Test ACID properties and concurrent access"""

    def test_transfer_is_atomic(self, ledger):
        """Test that transfer is atomic (both or neither)"""
        # Give alice some credits
        tx = CreditTransaction(
            timestamp=datetime.now(),
            user_did="did:mycelix:alice",
            tx_type=TransactionType.EARN,
            amount=CreditAmount(50.0),
            description="earn"
        )
        ledger.earn_credits("did:mycelix:alice", CreditAmount(50.0), tx)

        # Successful transfer
        ledger.transfer_credits(
            "did:mycelix:alice",
            "did:mycelix:bob",
            CreditAmount(30.0),
            "test"
        )

        alice_balance = ledger.get_balance("did:mycelix:alice")
        bob_balance = ledger.get_balance("did:mycelix:bob")

        # Both should be updated
        assert alice_balance.current_balance.value == 20.0
        assert bob_balance.current_balance.value == 30.0

        # Failed transfer (insufficient balance)
        try:
            ledger.transfer_credits(
                "did:mycelix:alice",
                "did:mycelix:charlie",
                CreditAmount(100.0),
                "overspend"
            )
        except ValueError:
            pass

        # Alice's balance should be unchanged (atomic rollback)
        alice_balance = ledger.get_balance("did:mycelix:alice")
        assert alice_balance.current_balance.value == 20.0
