"""
Credit Ledger (SQLite-based)

Manages credit balances and transaction history.

Features:
- Per-user (DID) credit balances
- Complete transaction history
- Query interface for analytics
- ACID transactions
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional, List
from datetime import datetime
from contextlib import contextmanager

from .types import (
    CreditAmount,
    CreditTransaction,
    CreditBalance,
    TransactionType
)

logger = logging.getLogger(__name__)


class CreditLedger:
    """
    SQLite-based credit ledger

    Manages credit balances and transaction history with ACID guarantees.
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize credit ledger

        Args:
            db_path: Path to SQLite database (defaults to ~/.luminous-nix/credits.db)
        """
        if db_path is None:
            db_path = Path.home() / ".luminous-nix" / "credits.db"

        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_database()

    def _init_database(self):
        """Initialize database schema"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Create balances table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS credit_balances (
                    user_did TEXT PRIMARY KEY,
                    total_earned REAL DEFAULT 0.0,
                    total_spent REAL DEFAULT 0.0,
                    current_balance REAL DEFAULT 0.0,
                    last_updated TEXT
                )
            """)

            # Create transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS credit_transactions (
                    tx_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_did TEXT NOT NULL,
                    tx_type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    interaction_id TEXT,
                    description TEXT,
                    epistemic_e REAL,
                    epistemic_n REAL,
                    epistemic_m INTEGER,
                    matl_score REAL,
                    FOREIGN KEY (user_did) REFERENCES credit_balances(user_did)
                )
            """)

            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_transactions
                ON credit_transactions(user_did, timestamp)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tx_type
                ON credit_transactions(tx_type)
            """)

            conn.commit()

    @contextmanager
    def _get_connection(self):
        """Get database connection with context manager"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        finally:
            conn.close()

    def get_balance(self, user_did: str) -> CreditBalance:
        """
        Get credit balance for user

        Args:
            user_did: User's DID

        Returns:
            CreditBalance (creates new balance if doesn't exist)
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM credit_balances WHERE user_did = ?",
                (user_did,)
            )
            row = cursor.fetchone()

            if row:
                return CreditBalance(
                    user_did=row['user_did'],
                    total_earned=CreditAmount(row['total_earned']),
                    total_spent=CreditAmount(row['total_spent']),
                    current_balance=CreditAmount(row['current_balance']),
                    last_updated=datetime.fromisoformat(row['last_updated'])
                )
            else:
                # Create new balance
                return CreditBalance(user_did=user_did)

    def _save_balance(self, balance: CreditBalance, conn: sqlite3.Connection):
        """Save balance to database (internal method)"""
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO credit_balances
            (user_did, total_earned, total_spent, current_balance, last_updated)
            VALUES (?, ?, ?, ?, ?)
        """, (
            balance.user_did,
            balance.total_earned.value,
            balance.total_spent.value,
            balance.current_balance.value,
            balance.last_updated.isoformat()
        ))

    def earn_credits(
        self,
        user_did: str,
        amount: CreditAmount,
        transaction: CreditTransaction
    ) -> CreditBalance:
        """
        Record credits earned

        Args:
            user_did: User's DID
            amount: Credits earned
            transaction: Transaction details

        Returns:
            Updated CreditBalance
        """
        with self._get_connection() as conn:
            # Get current balance
            balance = self.get_balance(user_did)

            # Update balance
            balance.earn(amount)

            # Save balance
            self._save_balance(balance, conn)

            # Record transaction
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO credit_transactions
                (timestamp, user_did, tx_type, amount, interaction_id, description,
                 epistemic_e, epistemic_n, epistemic_m, matl_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                transaction.timestamp.isoformat(),
                transaction.user_did,
                transaction.tx_type.value,
                transaction.amount.value,
                transaction.interaction_id,
                transaction.description,
                transaction.epistemic_e,
                transaction.epistemic_n,
                transaction.epistemic_m,
                transaction.matl_score
            ))

            conn.commit()

            logger.info(
                f"Earned {amount} credits for {user_did} "
                f"(new balance: {balance.current_balance})"
            )

            return balance

    def spend_credits(
        self,
        user_did: str,
        amount: CreditAmount,
        description: str = ""
    ) -> CreditBalance:
        """
        Deduct credits from balance

        Args:
            user_did: User's DID
            amount: Credits to spend
            description: Purpose of spending

        Returns:
            Updated CreditBalance

        Raises:
            ValueError: If insufficient balance
        """
        with self._get_connection() as conn:
            # Get current balance
            balance = self.get_balance(user_did)

            # Update balance (raises ValueError if insufficient)
            balance.spend(amount)

            # Save balance
            self._save_balance(balance, conn)

            # Record transaction
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO credit_transactions
                (timestamp, user_did, tx_type, amount, description)
                VALUES (?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                user_did,
                TransactionType.SPEND.value,
                amount.value,
                description
            ))

            conn.commit()

            logger.info(
                f"Spent {amount} credits for {user_did} "
                f"(new balance: {balance.current_balance})"
            )

            return balance

    def transfer_credits(
        self,
        from_did: str,
        to_did: str,
        amount: CreditAmount,
        description: str = ""
    ) -> tuple[CreditBalance, CreditBalance]:
        """
        Transfer credits between users

        Args:
            from_did: Sender's DID
            to_did: Recipient's DID
            amount: Credits to transfer
            description: Transfer description

        Returns:
            Tuple of (from_balance, to_balance)

        Raises:
            ValueError: If insufficient balance
        """
        with self._get_connection() as conn:
            # Get balances
            from_balance = self.get_balance(from_did)
            to_balance = self.get_balance(to_did)

            # Update balances
            from_balance.spend(amount)  # Deduct from sender
            to_balance.earn(amount)     # Add to recipient

            # Save balances
            self._save_balance(from_balance, conn)
            self._save_balance(to_balance, conn)

            # Record transactions
            cursor = conn.cursor()

            # Transfer out
            cursor.execute("""
                INSERT INTO credit_transactions
                (timestamp, user_did, tx_type, amount, description)
                VALUES (?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                from_did,
                TransactionType.TRANSFER_OUT.value,
                amount.value,
                f"Transfer to {to_did}: {description}"
            ))

            # Transfer in
            cursor.execute("""
                INSERT INTO credit_transactions
                (timestamp, user_did, tx_type, amount, description)
                VALUES (?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                to_did,
                TransactionType.TRANSFER_IN.value,
                amount.value,
                f"Transfer from {from_did}: {description}"
            ))

            conn.commit()

            logger.info(
                f"Transferred {amount} credits from {from_did} to {to_did}"
            )

            return from_balance, to_balance

    def get_transaction_history(
        self,
        user_did: str,
        limit: Optional[int] = None,
        tx_type: Optional[TransactionType] = None
    ) -> List[CreditTransaction]:
        """
        Get transaction history for user

        Args:
            user_did: User's DID
            limit: Maximum transactions to return
            tx_type: Filter by transaction type

        Returns:
            List of CreditTransaction objects (newest first)
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Build query
            query = """
                SELECT * FROM credit_transactions
                WHERE user_did = ?
            """
            params = [user_did]

            if tx_type:
                query += " AND tx_type = ?"
                params.append(tx_type.value)

            query += " ORDER BY timestamp DESC"

            if limit:
                query += " LIMIT ?"
                params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            # Convert to CreditTransaction objects
            transactions = []
            for row in rows:
                tx = CreditTransaction(
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    user_did=row['user_did'],
                    tx_type=TransactionType(row['tx_type']),
                    amount=CreditAmount(row['amount']),
                    interaction_id=row['interaction_id'],
                    description=row['description'] or "",
                    epistemic_e=row['epistemic_e'],
                    epistemic_n=row['epistemic_n'],
                    epistemic_m=row['epistemic_m'],
                    matl_score=row['matl_score'],
                    tx_id=row['tx_id']
                )
                transactions.append(tx)

            return transactions

    def get_total_credits_in_system(self) -> CreditAmount:
        """
        Get total credits across all users

        Returns:
            Total credits in the system
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(current_balance) FROM credit_balances")
            total = cursor.fetchone()[0] or 0.0
            return CreditAmount(total)

    def get_leaderboard(self, limit: int = 10) -> List[CreditBalance]:
        """
        Get top credit earners

        Args:
            limit: Number of users to return

        Returns:
            List of CreditBalance objects (highest balance first)
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM credit_balances
                ORDER BY current_balance DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()

            balances = []
            for row in rows:
                balance = CreditBalance(
                    user_did=row['user_did'],
                    total_earned=CreditAmount(row['total_earned']),
                    total_spent=CreditAmount(row['total_spent']),
                    current_balance=CreditAmount(row['current_balance']),
                    last_updated=datetime.fromisoformat(row['last_updated'])
                )
                balances.append(balance)

            return balances

    def get_stats(self) -> dict:
        """
        Get system-wide credit statistics

        Returns:
            Dictionary with statistics
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Total users
            cursor.execute("SELECT COUNT(*) FROM credit_balances")
            total_users = cursor.fetchone()[0]

            # Total credits
            cursor.execute("SELECT SUM(current_balance) FROM credit_balances")
            total_credits = cursor.fetchone()[0] or 0.0

            # Total earned
            cursor.execute("SELECT SUM(total_earned) FROM credit_balances")
            total_earned = cursor.fetchone()[0] or 0.0

            # Total spent
            cursor.execute("SELECT SUM(total_spent) FROM credit_balances")
            total_spent = cursor.fetchone()[0] or 0.0

            # Total transactions
            cursor.execute("SELECT COUNT(*) FROM credit_transactions")
            total_transactions = cursor.fetchone()[0]

            return {
                'total_users': total_users,
                'total_credits': total_credits,
                'total_earned': total_earned,
                'total_spent': total_spent,
                'total_transactions': total_transactions,
                'average_balance': total_credits / total_users if total_users > 0 else 0.0
            }


# Singleton instance
_ledger: Optional[CreditLedger] = None


def get_ledger(db_path: Optional[Path] = None) -> CreditLedger:
    """
    Get singleton ledger instance

    Args:
        db_path: Database path (only used on first call)

    Returns:
        CreditLedger instance
    """
    global _ledger
    if _ledger is None:
        _ledger = CreditLedger(db_path)
    return _ledger
