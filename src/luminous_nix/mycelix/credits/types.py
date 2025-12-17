"""
Credits System Types (Week 7-8)

Epistemic-weighted credit allocation based on Charter v2.0 E/N/M classification.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class TransactionType(Enum):
    """Types of credit transactions"""
    EARN = "earn"           # Credits earned from interaction
    SPEND = "spend"         # Credits spent on features
    TRANSFER_IN = "transfer_in"    # Credits received from another user
    TRANSFER_OUT = "transfer_out"  # Credits sent to another user
    ADJUSTMENT = "adjustment"      # Manual adjustment (admin)


@dataclass
class CreditAmount:
    """
    Value class for credit amounts

    Supports basic arithmetic and formatting.
    """
    value: float

    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Credit amount cannot be negative")

    def __add__(self, other: 'CreditAmount') -> 'CreditAmount':
        return CreditAmount(self.value + other.value)

    def __sub__(self, other: 'CreditAmount') -> 'CreditAmount':
        result = self.value - other.value
        if result < 0:
            raise ValueError("Insufficient credits")
        return CreditAmount(result)

    def __mul__(self, multiplier: float) -> 'CreditAmount':
        return CreditAmount(self.value * multiplier)

    def __truediv__(self, divisor: float) -> 'CreditAmount':
        if divisor == 0:
            raise ValueError("Cannot divide by zero")
        return CreditAmount(self.value / divisor)

    def __eq__(self, other: 'CreditAmount') -> bool:
        return abs(self.value - other.value) < 0.001  # Float equality with epsilon

    def __lt__(self, other: 'CreditAmount') -> bool:
        return self.value < other.value

    def __le__(self, other: 'CreditAmount') -> bool:
        return self.value <= other.value

    def __gt__(self, other: 'CreditAmount') -> bool:
        return self.value > other.value

    def __ge__(self, other: 'CreditAmount') -> bool:
        return self.value >= other.value

    def __repr__(self) -> str:
        return f"CreditAmount({self.value:.2f})"

    def __str__(self) -> str:
        return f"{self.value:.2f} credits"


@dataclass
class CreditTransaction:
    """
    Single credit transaction record

    Represents earning, spending, or transferring credits.
    """
    # Core fields
    timestamp: datetime
    user_did: str
    tx_type: TransactionType
    amount: CreditAmount

    # Context fields
    interaction_id: Optional[str] = None  # Reference to Interaction
    description: str = ""

    # Epistemic context (for earned credits)
    epistemic_e: Optional[float] = None
    epistemic_n: Optional[float] = None
    epistemic_m: Optional[int] = None
    matl_score: Optional[float] = None

    # Transaction ID (assigned by ledger)
    tx_id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for storage"""
        data = {
            'timestamp': self.timestamp.isoformat(),
            'user_did': self.user_did,
            'tx_type': self.tx_type.value,
            'amount': self.amount.value,
            'interaction_id': self.interaction_id,
            'description': self.description,
            'epistemic_e': self.epistemic_e,
            'epistemic_n': self.epistemic_n,
            'epistemic_m': self.epistemic_m,
            'matl_score': self.matl_score,
            'tx_id': self.tx_id
        }
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CreditTransaction':
        """Deserialize from storage"""
        data = data.copy()
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['tx_type'] = TransactionType(data['tx_type'])
        data['amount'] = CreditAmount(data['amount'])
        return cls(**data)

    def get_coordinate(self) -> Optional[str]:
        """Get E/N/M coordinate if available"""
        if self.epistemic_e is None or self.epistemic_n is None or self.epistemic_m is None:
            return None

        from luminous_nix.mycelix.epistemic import ETier, NTier, MTier

        # Convert to tiers
        if self.epistemic_e < 0.125:
            e_tier = ETier.E0
        elif self.epistemic_e < 0.375:
            e_tier = ETier.E1
        elif self.epistemic_e < 0.625:
            e_tier = ETier.E2
        elif self.epistemic_e < 0.875:
            e_tier = ETier.E3
        else:
            e_tier = ETier.E4

        if self.epistemic_n < 0.17:
            n_tier = NTier.N0
        elif self.epistemic_n < 0.5:
            n_tier = NTier.N1
        elif self.epistemic_n < 0.84:
            n_tier = NTier.N2
        else:
            n_tier = NTier.N3

        m_tier = MTier(self.epistemic_m)

        return f"({e_tier.name}, {n_tier.name}, {m_tier.name})"


@dataclass
class CreditBalance:
    """
    Per-user credit balance state

    Tracks total earned, spent, and current balance.
    """
    user_did: str
    total_earned: CreditAmount = field(default_factory=lambda: CreditAmount(0.0))
    total_spent: CreditAmount = field(default_factory=lambda: CreditAmount(0.0))
    current_balance: CreditAmount = field(default_factory=lambda: CreditAmount(0.0))
    last_updated: datetime = field(default_factory=datetime.now)

    def earn(self, amount: CreditAmount):
        """Add earned credits"""
        self.total_earned = self.total_earned + amount
        self.current_balance = self.current_balance + amount
        self.last_updated = datetime.now()

    def spend(self, amount: CreditAmount):
        """Deduct spent credits"""
        if self.current_balance < amount:
            raise ValueError(
                f"Insufficient balance: {self.current_balance} < {amount}"
            )
        self.total_spent = self.total_spent + amount
        self.current_balance = self.current_balance - amount
        self.last_updated = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for storage"""
        return {
            'user_did': self.user_did,
            'total_earned': self.total_earned.value,
            'total_spent': self.total_spent.value,
            'current_balance': self.current_balance.value,
            'last_updated': self.last_updated.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CreditBalance':
        """Deserialize from storage"""
        return cls(
            user_did=data['user_did'],
            total_earned=CreditAmount(data['total_earned']),
            total_spent=CreditAmount(data['total_spent']),
            current_balance=CreditAmount(data['current_balance']),
            last_updated=datetime.fromisoformat(data['last_updated'])
        )


@dataclass
class CreditWeights:
    """
    Configurable weights for credit calculation

    Default weights based on Charter v2.0 epistemic cube.
    """
    # Base rate (credits per successful interaction)
    base_rate: float = 10.0

    # E-Axis multipliers (Empirical Verifiability)
    e_multipliers: Dict[int, float] = field(default_factory=lambda: {
        0: 0.0,   # E0: Null/Unverifiable
        1: 0.5,   # E1: Testimonial
        2: 1.0,   # E2: Privately Verifiable (baseline)
        3: 2.0,   # E3: Cryptographically Proven
        4: 3.0    # E4: Publicly Reproducible
    })

    # N-Axis multipliers (Normative Authority)
    n_multipliers: Dict[int, float] = field(default_factory=lambda: {
        0: 1.0,   # N0: Personal (baseline)
        1: 1.5,   # N1: Communal
        2: 2.5,   # N2: Network
        3: 4.0    # N3: Axiomatic
    })

    # M-Axis multipliers (Materiality/Permanence)
    m_multipliers: Dict[int, float] = field(default_factory=lambda: {
        0: 0.0,   # M0: Ephemeral
        1: 0.5,   # M1: Temporal
        2: 1.5,   # M2: Persistent
        3: 3.0    # M3: Foundational
    })

    # Trust score modifier range
    trust_min_modifier: float = 0.5   # Minimum multiplier (low trust)
    trust_max_modifier: float = 1.0   # Maximum multiplier (high trust)

    def get_e_multiplier(self, epistemic_e: float) -> float:
        """Get E-axis multiplier from continuous score"""
        # Convert to tier
        if epistemic_e < 0.125:
            tier = 0
        elif epistemic_e < 0.375:
            tier = 1
        elif epistemic_e < 0.625:
            tier = 2
        elif epistemic_e < 0.875:
            tier = 3
        else:
            tier = 4
        return self.e_multipliers[tier]

    def get_n_multiplier(self, epistemic_n: float) -> float:
        """Get N-axis multiplier from continuous score"""
        # Convert to tier
        if epistemic_n < 0.17:
            tier = 0
        elif epistemic_n < 0.5:
            tier = 1
        elif epistemic_n < 0.84:
            tier = 2
        else:
            tier = 3
        return self.n_multipliers[tier]

    def get_m_multiplier(self, epistemic_m: int) -> float:
        """Get M-axis multiplier from tier"""
        return self.m_multipliers[epistemic_m]

    def get_trust_modifier(self, matl_score: float) -> float:
        """Get trust modifier from MATL score (0.0-1.0)"""
        # Linear scaling: matl_score 0.0 → min_modifier, 1.0 → max_modifier
        return self.trust_min_modifier + (matl_score * (self.trust_max_modifier - self.trust_min_modifier))
