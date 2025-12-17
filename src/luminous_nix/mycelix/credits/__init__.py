"""
Credits System (Week 7-8)

Epistemic-weighted credit allocation based on Charter v2.0 E/N/M classification.

Features:
- E/N/M weighted credit calculation
- MATL trust score integration
- SQLite-based credit ledger
- Transaction history and analytics
"""

from .types import (
    TransactionType,
    CreditAmount,
    CreditTransaction,
    CreditBalance,
    CreditWeights
)

from .calculator import (
    CreditCalculator,
    get_calculator
)

from .ledger import (
    CreditLedger,
    get_ledger
)

__version__ = "1.0.0"
__all__ = [
    # Types
    'TransactionType',
    'CreditAmount',
    'CreditTransaction',
    'CreditBalance',
    'CreditWeights',
    # Calculator
    'CreditCalculator',
    'get_calculator',
    # Ledger
    'CreditLedger',
    'get_ledger',
]
