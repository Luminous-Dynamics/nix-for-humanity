"""
WisdomEngine Python Bridge

Mirrors the Rust WisdomEngine API for pattern learning and recommendations.
Designed for later replacement with PyO3 bindings to the real Rust implementation.

Key Concepts (from Mycelix WisdomEngine):
- Pattern: A reusable solution (e.g., "use flakes for development")
- Domain: A category of patterns (e.g., "development_environments")
- Lifecycle: Active → Deprecated → Archived → Retired
- Trust: Testimonial < Audited < Cryptographic
- Succession: Better patterns replace older ones
"""

import json
import hashlib
import logging
from pathlib import Path
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import math

logger = logging.getLogger(__name__)


class TrustLevel(Enum):
    """Oracle verification levels (from Mycelix Epistemic Charter)"""
    TESTIMONIAL = 1      # Personal attestation ("I've used this")
    AUDITED = 2          # Verified by guild/community
    CRYPTOGRAPHIC = 3    # ZKP or cryptographic proof


class LifecycleState(Enum):
    """Pattern lifecycle states"""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"
    RETIRED = "retired"


class PatternOutcome(Enum):
    """Outcome of applying a pattern"""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"


@dataclass
class Pattern:
    """A reusable solution pattern"""
    id: str
    name: str
    description: str
    domain: str
    tags: List[str] = field(default_factory=list)

    # Tracking
    success_count: int = 0
    failure_count: int = 0
    partial_count: int = 0
    last_used: Optional[str] = None

    # Trust
    trust_level: str = "TESTIMONIAL"
    verified_by: Optional[str] = None

    # Lifecycle
    state: str = "active"
    deprecated_at: Optional[str] = None
    deprecated_by: Optional[str] = None  # ID of successor pattern

    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    contexts: List[str] = field(default_factory=list)

    @property
    def total_uses(self) -> int:
        return self.success_count + self.failure_count + self.partial_count

    @property
    def success_rate(self) -> float:
        if self.total_uses == 0:
            return 0.5  # Prior: assume neutral
        return self.success_count / self.total_uses

    @property
    def confidence(self) -> float:
        """Bayesian confidence based on sample size"""
        # Beta distribution prior: alpha=1, beta=1 (uniform)
        alpha = 1 + self.success_count
        beta = 1 + self.failure_count + self.partial_count
        # Variance decreases with more samples
        variance = (alpha * beta) / ((alpha + beta) ** 2 * (alpha + beta + 1))
        # Convert to confidence (inverse of variance, normalized)
        return 1.0 - min(variance * 10, 0.9)

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'Pattern':
        return cls(**data)


@dataclass
class PatternRecommendation:
    """A recommended pattern with explanation"""
    pattern_id: str
    pattern_name: str
    score: float  # 0.0 to 1.0
    confidence: float
    reasons: List[str]
    warnings: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        return f"{self.pattern_name} (score: {self.score:.2f}, confidence: {self.confidence:.2f})"


@dataclass
class DomainRegistry:
    """Registry of pattern domains"""
    domains: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def register(self, domain_id: str, name: str, parent: Optional[str] = None, description: str = ""):
        self.domains[domain_id] = {
            "id": domain_id,
            "name": name,
            "parent": parent,
            "description": description,
            "pattern_count": 0,
        }

    def get_ancestors(self, domain_id: str) -> List[str]:
        """Get all ancestor domains"""
        ancestors = []
        current = domain_id
        while current and current in self.domains:
            parent = self.domains[current].get("parent")
            if parent:
                ancestors.append(parent)
                current = parent
            else:
                break
        return ancestors


class WisdomBridge:
    """
    Python bridge to WisdomEngine pattern intelligence.

    Provides:
    - Pattern registration and tracking
    - Success/failure learning
    - Context-aware recommendations
    - Pattern succession (better patterns replace old)
    - Trust-weighted scoring

    Future: Replace internals with PyO3 calls to Rust WisdomEngine
    """

    def __init__(self, storage_path: Optional[Path] = None):
        if storage_path is None:
            storage_path = Path.home() / ".luminous-nix" / "wisdom"

        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.patterns: Dict[str, Pattern] = {}
        self.domains = DomainRegistry()
        self.successions: Dict[str, str] = {}  # deprecated_id → successor_id

        # Load existing state
        self._load_state()

        logger.info(f"WisdomBridge initialized with {len(self.patterns)} patterns")

    # ========== Pattern Registration ==========

    def register_pattern(
        self,
        name: str,
        description: str,
        domain: str,
        tags: Optional[List[str]] = None,
        trust_level: TrustLevel = TrustLevel.TESTIMONIAL,
        pattern_id: Optional[str] = None,
    ) -> str:
        """Register a new pattern and return its ID"""

        if pattern_id is None:
            pattern_id = self._generate_id(name, domain)

        if pattern_id in self.patterns:
            logger.debug(f"Pattern {pattern_id} already exists, skipping registration")
            return pattern_id

        pattern = Pattern(
            id=pattern_id,
            name=name,
            description=description,
            domain=domain,
            tags=tags or [],
            trust_level=trust_level.name,
        )

        self.patterns[pattern_id] = pattern

        # Update domain count
        if domain in self.domains.domains:
            self.domains.domains[domain]["pattern_count"] += 1

        self._save_state()
        logger.info(f"Registered pattern: {name} ({pattern_id})")

        return pattern_id

    def register_domain(
        self,
        domain_id: str,
        name: str,
        parent: Optional[str] = None,
        description: str = "",
    ):
        """Register a pattern domain"""
        self.domains.register(domain_id, name, parent, description)
        self._save_state()

    # ========== Outcome Recording ==========

    def record_outcome(
        self,
        pattern_id: str,
        outcome: PatternOutcome,
        context: Optional[str] = None,
        details: Optional[Dict] = None,
    ):
        """Record the outcome of applying a pattern"""

        if pattern_id not in self.patterns:
            logger.warning(f"Pattern {pattern_id} not found")
            return

        pattern = self.patterns[pattern_id]

        if outcome == PatternOutcome.SUCCESS:
            pattern.success_count += 1
        elif outcome == PatternOutcome.FAILURE:
            pattern.failure_count += 1
        else:
            pattern.partial_count += 1

        pattern.last_used = datetime.now().isoformat()

        if context and context not in pattern.contexts:
            pattern.contexts.append(context)

        self._save_state()

        logger.debug(
            f"Recorded {outcome.value} for {pattern.name} "
            f"(success rate: {pattern.success_rate:.2%})"
        )

    def record_success(self, pattern_id: str, context: Optional[str] = None):
        """Shorthand for recording success"""
        self.record_outcome(pattern_id, PatternOutcome.SUCCESS, context)

    def record_failure(self, pattern_id: str, context: Optional[str] = None):
        """Shorthand for recording failure"""
        self.record_outcome(pattern_id, PatternOutcome.FAILURE, context)

    # ========== Pattern Succession ==========

    def deprecate_pattern(
        self,
        pattern_id: str,
        successor_id: Optional[str] = None,
        reason: str = "superseded",
    ):
        """Mark a pattern as deprecated, optionally with successor"""

        if pattern_id not in self.patterns:
            logger.warning(f"Pattern {pattern_id} not found")
            return

        pattern = self.patterns[pattern_id]
        pattern.state = LifecycleState.DEPRECATED.value
        pattern.deprecated_at = datetime.now().isoformat()

        if successor_id:
            pattern.deprecated_by = successor_id
            self.successions[pattern_id] = successor_id

        self._save_state()

        logger.info(f"Deprecated pattern: {pattern.name} → {successor_id or 'none'}")

    def get_successor(self, pattern_id: str) -> Optional[str]:
        """Get the successor pattern ID if deprecated"""
        return self.successions.get(pattern_id)

    # ========== Recommendations ==========

    def recommend_patterns(
        self,
        domain: str,
        context: Optional[str] = None,
        limit: int = 5,
        include_deprecated: bool = False,
    ) -> List[PatternRecommendation]:
        """Get recommended patterns for a domain/context"""

        candidates = []

        # Get patterns in this domain (and ancestors)
        valid_domains = {domain} | set(self.domains.get_ancestors(domain))

        for pattern in self.patterns.values():
            # Filter by domain
            if pattern.domain not in valid_domains:
                continue

            # Filter by lifecycle state
            if not include_deprecated and pattern.state != LifecycleState.ACTIVE.value:
                continue

            # Calculate score
            score, reasons, warnings = self._score_pattern(pattern, context)

            candidates.append(PatternRecommendation(
                pattern_id=pattern.id,
                pattern_name=pattern.name,
                score=score,
                confidence=pattern.confidence,
                reasons=reasons,
                warnings=warnings,
            ))

        # Sort by score, then confidence
        candidates.sort(key=lambda r: (r.score, r.confidence), reverse=True)

        return candidates[:limit]

    def _score_pattern(
        self,
        pattern: Pattern,
        context: Optional[str] = None,
    ) -> Tuple[float, List[str], List[str]]:
        """Calculate pattern score with explanations"""

        score = 0.0
        reasons = []
        warnings = []

        # Base: success rate (0.0 to 0.4)
        success_component = pattern.success_rate * 0.4
        score += success_component
        if pattern.success_rate > 0.8:
            reasons.append(f"High success rate ({pattern.success_rate:.0%})")
        elif pattern.success_rate < 0.5 and pattern.total_uses > 5:
            warnings.append(f"Low success rate ({pattern.success_rate:.0%})")

        # Trust level (0.0 to 0.3)
        trust_weights = {
            "TESTIMONIAL": 0.1,
            "AUDITED": 0.2,
            "CRYPTOGRAPHIC": 0.3,
        }
        trust_component = trust_weights.get(pattern.trust_level, 0.1)
        score += trust_component
        if trust_component >= 0.2:
            reasons.append(f"Verified ({pattern.trust_level.lower()})")

        # Usage evidence (0.0 to 0.2)
        usage_component = min(pattern.total_uses / 100, 1.0) * 0.2
        score += usage_component
        if pattern.total_uses >= 50:
            reasons.append(f"Well-tested ({pattern.total_uses} uses)")
        elif pattern.total_uses < 5:
            warnings.append("Limited usage data")

        # Context match (0.0 to 0.1)
        if context:
            context_lower = context.lower()
            if any(context_lower in c.lower() for c in pattern.contexts):
                score += 0.1
                reasons.append("Matches your context")
            if any(context_lower in tag.lower() for tag in pattern.tags):
                score += 0.05
                reasons.append("Relevant tags")

        # Recency bonus (0.0 to 0.05)
        if pattern.last_used:
            try:
                last_used = datetime.fromisoformat(pattern.last_used)
                days_ago = (datetime.now() - last_used).days
                recency = max(0, 1 - days_ago / 365) * 0.05
                score += recency
            except:
                pass

        # Deprecation penalty
        if pattern.state == LifecycleState.DEPRECATED.value:
            score *= 0.5
            warnings.append("Deprecated pattern")
            if pattern.deprecated_by:
                successor = self.patterns.get(pattern.deprecated_by)
                if successor:
                    warnings.append(f"Consider: {successor.name}")

        return min(score, 1.0), reasons, warnings

    # ========== Queries ==========

    def get_pattern(self, pattern_id: str) -> Optional[Pattern]:
        """Get pattern by ID"""
        return self.patterns.get(pattern_id)

    def get_patterns_by_domain(self, domain: str) -> List[Pattern]:
        """Get all patterns in a domain"""
        return [p for p in self.patterns.values() if p.domain == domain]

    def get_pattern_stats(self, pattern_id: str) -> Optional[Dict]:
        """Get statistics for a pattern"""
        pattern = self.patterns.get(pattern_id)
        if not pattern:
            return None

        return {
            "id": pattern.id,
            "name": pattern.name,
            "success_rate": pattern.success_rate,
            "confidence": pattern.confidence,
            "total_uses": pattern.total_uses,
            "state": pattern.state,
            "trust_level": pattern.trust_level,
        }

    def get_stats(self) -> Dict:
        """Get overall wisdom engine statistics"""
        active = sum(1 for p in self.patterns.values() if p.state == "active")
        deprecated = sum(1 for p in self.patterns.values() if p.state == "deprecated")

        total_uses = sum(p.total_uses for p in self.patterns.values())
        total_successes = sum(p.success_count for p in self.patterns.values())

        return {
            "total_patterns": len(self.patterns),
            "active_patterns": active,
            "deprecated_patterns": deprecated,
            "total_domains": len(self.domains.domains),
            "total_uses": total_uses,
            "overall_success_rate": total_successes / total_uses if total_uses > 0 else 0,
            "successions": len(self.successions),
        }

    # ========== Persistence ==========

    def _save_state(self):
        """Save state to disk"""
        state = {
            "version": "1.0",
            "patterns": {pid: p.to_dict() for pid, p in self.patterns.items()},
            "domains": self.domains.domains,
            "successions": self.successions,
            "saved_at": datetime.now().isoformat(),
        }

        state_file = self.storage_path / "wisdom_state.json"
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def _load_state(self):
        """Load state from disk"""
        state_file = self.storage_path / "wisdom_state.json"

        if not state_file.exists():
            logger.info("No existing wisdom state found, starting fresh")
            return

        try:
            with open(state_file, 'r') as f:
                state = json.load(f)

            self.patterns = {
                pid: Pattern.from_dict(pdata)
                for pid, pdata in state.get("patterns", {}).items()
            }

            self.domains.domains = state.get("domains", {})
            self.successions = state.get("successions", {})

            logger.info(f"Loaded wisdom state: {len(self.patterns)} patterns")

        except Exception as e:
            logger.error(f"Failed to load wisdom state: {e}")

    def _generate_id(self, name: str, domain: str) -> str:
        """Generate a unique pattern ID"""
        content = f"{name}:{domain}"
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    # ========== Import from Rust WisdomEngine ==========

    def import_from_json(self, json_path: Path):
        """
        Import state from Rust WisdomEngine JSON export.

        The Rust WisdomEngine uses serde to serialize its state.
        This method imports that state into the Python bridge.
        """
        # TODO: Implement when we have PyO3 or serde export
        raise NotImplementedError("Coming soon: import from Rust WisdomEngine")

    def export_to_json(self, json_path: Path):
        """Export state for Rust WisdomEngine import"""
        self._save_state()
        # Copy to requested path
        import shutil
        shutil.copy(self.storage_path / "wisdom_state.json", json_path)


# Singleton instance
_wisdom_engine: Optional[WisdomBridge] = None


def get_wisdom_engine(storage_path: Optional[Path] = None) -> WisdomBridge:
    """Get or create the singleton WisdomBridge instance"""
    global _wisdom_engine

    if _wisdom_engine is None:
        _wisdom_engine = WisdomBridge(storage_path)

    return _wisdom_engine
