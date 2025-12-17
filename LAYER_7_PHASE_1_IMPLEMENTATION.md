# 🚀 Layer 7 Phase 1: Concrete Implementation Plan

**Date**: December 3, 2025
**Status**: Ready for Implementation (All dependencies available)
**Timeline**: 12 weeks (3 months)
**Components**: Identity + MATL + Epistemic Cube + Credits

---

## 🎯 What We're Building

**Phase 1 Goal**: Integrate production-ready Mycelix components for immediate value

**Available NOW** (Mycelix production-ready):
- ✅ Identity System (W3C DIDs)
- ✅ MATL Trust Scoring (v1.0)
- ✅ Epistemic Charter v2.0 (E/N/M classification)
- ✅ Zero-TrustML Credits architecture

**No external dependencies** - can start immediately!

---

## 📁 File Structure

```
src/luminous_nix/
├── mycelix/                           # 🆕 New Mycelix integration module
│   ├── __init__.py
│   ├── identity/                      # W3C DID management
│   │   ├── __init__.py
│   │   ├── did_manager.py            # Create/load/manage DIDs
│   │   ├── credential_manager.py      # Verifiable Credentials
│   │   ├── social_recovery.py         # Shamir Secret Sharing
│   │   └── cross_device_sync.py       # Holochain DHT sync
│   ├── trust/                         # MATL trust scoring
│   │   ├── __init__.py
│   │   ├── matl_engine.py            # MATL trust calculation
│   │   ├── pogq.py                   # Proof of Genuine Query
│   │   ├── tcdm.py                   # Temporal Consistency
│   │   ├── entropy.py                # Interaction diversity
│   │   └── cartel_detection.py        # Basic cartel detection
│   ├── epistemic/                     # E/N/M classification
│   │   ├── __init__.py
│   │   ├── classifier.py             # Classify claims by E/N/M
│   │   ├── storage_manager.py         # Materiality-based storage
│   │   └── claim_schema.py           # Epistemic Claim data model
│   ├── credits/                       # Zero-TrustML Credits
│   │   ├── __init__.py
│   │   ├── wallet.py                 # User wallet management
│   │   ├── holochain_dna.py          # Holochain DNA interface
│   │   └── transaction.py            # Credit transfers
│   └── config.py                     # Mycelix configuration
│
├── ai/                                # Existing AI modules
│   ├── realtime_intelligence.py       # Layer 6 (integrate with MATL)
│   ├── behavioral_classifier.py       # Layer 5.5 (integrate with Epistemic)
│   └── emotional_intelligence.py      # Layer 6 (integrate with Epistemic)
│
└── core/
    ├── state_manager.py               # Update to use Mycelix DID
    └── user_profile.py                # 🆕 User profile with DID + trust

tests/mycelix/                         # 🆕 Mycelix integration tests
├── test_identity.py
├── test_matl.py
├── test_epistemic.py
└── test_credits.py
```

---

## 🔧 Component 1: W3C DID Identity System

### Implementation: `src/luminous_nix/mycelix/identity/did_manager.py`

```python
"""
W3C Decentralized Identifier (DID) Management for Luminous Nix

Provides sovereign identity for users across devices with social recovery.
"""

from typing import Optional, List, Dict
from dataclasses import dataclass
from pathlib import Path
import json
import hashlib
from datetime import datetime

# Mycelix DID libraries (from Mycelix-Core)
from mycelix.identity import DIDDocument, DIDResolver, VerifiableCredential


@dataclass
class LuminousNixDID:
    """
    Luminous Nix user identity using Mycelix DID standard.

    Format: did:mycelix:luminous_nix:{public_key_hash}
    """
    did: str  # Full DID (e.g., "did:mycelix:luminous_nix:QmXx7...")
    public_key: str
    private_key_encrypted: str  # Encrypted with user passphrase
    created_at: str
    assurance_level: str  # E0, E1, E2, E3, E4

    # Social recovery
    recovery_guardians: List[str]  # List of guardian DIDs
    recovery_threshold: int  # Number of guardians needed to recover


class DIDManager:
    """
    Manages Luminous Nix user DIDs.

    Features:
    - Create new DIDs
    - Load existing DIDs
    - Cross-device synchronization
    - Social recovery setup
    """

    def __init__(self, storage_path: Path = None):
        """Initialize DID manager with storage location."""
        self.storage_path = storage_path or Path.home() / ".luminous-nix" / "identity"
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # DID file location
        self.did_file = self.storage_path / "did.json"

        # Holochain DHT for cross-device sync (from Mycelix)
        self.dht_client = None  # Initialize when needed

    def create_or_load(self, passphrase: Optional[str] = None) -> LuminousNixDID:
        """
        Create new DID or load existing one.

        Args:
            passphrase: User passphrase for encrypting private key

        Returns:
            LuminousNixDID object
        """
        # Check if DID already exists
        if self.did_file.exists():
            return self.load_did(passphrase)
        else:
            return self.create_did(passphrase)

    def create_did(self, passphrase: str) -> LuminousNixDID:
        """
        Create new Mycelix DID for user.

        Steps:
        1. Generate keypair
        2. Create DID from public key
        3. Encrypt private key with passphrase
        4. Store locally
        5. Register with Holochain DHT
        """
        from mycelix.identity import generate_keypair, create_did

        # Generate keypair
        public_key, private_key = generate_keypair()

        # Create DID from public key
        # Format: did:mycelix:luminous_nix:{public_key_hash}
        public_key_hash = hashlib.sha256(public_key.encode()).hexdigest()[:16]
        did = f"did:mycelix:luminous_nix:{public_key_hash}"

        # Encrypt private key with passphrase
        from mycelix.crypto import encrypt_with_passphrase
        private_key_encrypted = encrypt_with_passphrase(private_key, passphrase)

        # Create DID object
        luminous_did = LuminousNixDID(
            did=did,
            public_key=public_key,
            private_key_encrypted=private_key_encrypted,
            created_at=datetime.now().isoformat(),
            assurance_level="E0",  # Start at E0 (basic)
            recovery_guardians=[],
            recovery_threshold=0
        )

        # Save to local storage
        self._save_did(luminous_did)

        # Register with Holochain DHT (for cross-device sync)
        self._register_with_dht(luminous_did)

        print(f"✅ Created new Luminous Nix DID: {did}")
        return luminous_did

    def load_did(self, passphrase: str) -> LuminousNixDID:
        """Load existing DID from storage."""
        if not self.did_file.exists():
            raise FileNotFoundError("No DID found. Create one first.")

        with open(self.did_file, 'r') as f:
            did_data = json.load(f)

        # Reconstruct LuminousNixDID object
        luminous_did = LuminousNixDID(**did_data)

        # Verify passphrase can decrypt private key
        from mycelix.crypto import decrypt_with_passphrase
        try:
            decrypt_with_passphrase(luminous_did.private_key_encrypted, passphrase)
        except Exception:
            raise ValueError("Invalid passphrase!")

        print(f"✅ Loaded Luminous Nix DID: {luminous_did.did}")
        return luminous_did

    def setup_social_recovery(
        self,
        did: LuminousNixDID,
        guardian_dids: List[str],
        threshold: int = 3
    ) -> None:
        """
        Set up social recovery with Shamir Secret Sharing.

        Args:
            did: User's DID
            guardian_dids: List of 5 guardian DIDs
            threshold: Number of guardians needed to recover (default 3)
        """
        from mycelix.identity import create_recovery_shares

        # Validate guardian count
        if len(guardian_dids) != 5:
            raise ValueError("Must have exactly 5 guardians")

        if threshold < 3 or threshold > 5:
            raise ValueError("Threshold must be 3, 4, or 5")

        # Create Shamir shares of private key
        shares = create_recovery_shares(
            secret=did.private_key_encrypted,
            num_shares=5,
            threshold=threshold
        )

        # Distribute shares to guardians via Holochain DHT
        for guardian_did, share in zip(guardian_dids, shares):
            self._send_recovery_share(guardian_did, share)

        # Update DID with recovery info
        did.recovery_guardians = guardian_dids
        did.recovery_threshold = threshold
        self._save_did(did)

        print(f"✅ Social recovery configured: {threshold} of 5 guardians")

    def sync_to_device(self, did: LuminousNixDID, target_device_id: str) -> None:
        """
        Sync DID to another device via Holochain DHT.

        Args:
            did: User's DID
            target_device_id: Device identifier for target device
        """
        # Push DID data to Holochain DHT
        self._initialize_dht_client()

        did_data = {
            "did": did.did,
            "public_key": did.public_key,
            "private_key_encrypted": did.private_key_encrypted,
            "created_at": did.created_at,
            "assurance_level": did.assurance_level
        }

        # Store in DHT with user's DID as key
        self.dht_client.put(f"luminous_nix_did:{did.did}", did_data)

        print(f"✅ DID synced to device: {target_device_id}")

    def _save_did(self, did: LuminousNixDID) -> None:
        """Save DID to local storage (encrypted)."""
        did_data = {
            "did": did.did,
            "public_key": did.public_key,
            "private_key_encrypted": did.private_key_encrypted,
            "created_at": did.created_at,
            "assurance_level": did.assurance_level,
            "recovery_guardians": did.recovery_guardians,
            "recovery_threshold": did.recovery_threshold
        }

        with open(self.did_file, 'w') as f:
            json.dump(did_data, f, indent=2)

    def _register_with_dht(self, did: LuminousNixDID) -> None:
        """Register DID with Holochain DHT for discovery."""
        # Initialize DHT client if needed
        self._initialize_dht_client()

        # Register DID in global registry
        self.dht_client.put(f"did_registry:{did.did}", {
            "did": did.did,
            "public_key": did.public_key,
            "created_at": did.created_at,
            "app": "luminous_nix"
        })

    def _initialize_dht_client(self):
        """Initialize Holochain DHT client (lazy loading)."""
        if self.dht_client is None:
            from mycelix.holochain import HolochainDHTClient
            self.dht_client = HolochainDHTClient(
                app_id="luminous_nix_identity",
                dna_hash="QmXxx..."  # Identity DNA hash
            )

    def _send_recovery_share(self, guardian_did: str, share: str) -> None:
        """Send recovery share to guardian via DHT."""
        self._initialize_dht_client()

        # Encrypt share with guardian's public key
        from mycelix.crypto import encrypt_for_recipient
        guardian_public_key = self._get_public_key_for_did(guardian_did)
        encrypted_share = encrypt_for_recipient(share, guardian_public_key)

        # Store in DHT
        self.dht_client.put(f"recovery_share:{guardian_did}", encrypted_share)

    def _get_public_key_for_did(self, did: str) -> str:
        """Resolve DID to get public key."""
        did_document = self.dht_client.get(f"did_registry:{did}")
        return did_document["public_key"]


# Singleton instance
_did_manager: Optional[DIDManager] = None

def get_did_manager() -> DIDManager:
    """Get singleton DID manager."""
    global _did_manager
    if _did_manager is None:
        _did_manager = DIDManager()
    return _did_manager
```

### Usage Example:

```python
from luminous_nix.mycelix import get_did_manager

# First run: Create DID
manager = get_did_manager()
user_did = manager.create_or_load(passphrase="my_secure_passphrase")

print(f"Your DID: {user_did.did}")
# Output: did:mycelix:luminous_nix:Qm7x8y9z...

# Set up social recovery (5 guardians, need 3 to recover)
manager.setup_social_recovery(
    did=user_did,
    guardian_dids=[
        "did:mycelix:friend_alice",
        "did:mycelix:friend_bob",
        "did:mycelix:family_member",
        "did:mycelix:colleague",
        "did:mycelix:trusted_service"
    ],
    threshold=3
)

# Sync to another device (e.g., laptop)
manager.sync_to_device(user_did, target_device_id="laptop_001")
```

---

## 🔧 Component 2: MATL Trust Scoring

### Implementation: `src/luminous_nix/mycelix/trust/matl_engine.py`

```python
"""
MATL (Mycelix Adaptive Trust Layer) Integration

Provides Byzantine-resistant trust scoring for Luminous Nix users.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json


@dataclass
class MATLScore:
    """
    MATL trust score for a user.

    Composite score = (PoGQ × 0.4) + (TCDM × 0.3) + (Entropy × 0.3)
    """
    pogq: float  # Proof of Genuine Query (0.0 - 1.0)
    tcdm: float  # Temporal Consistency Deviation Metric (0.0 - 1.0)
    entropy: float  # Interaction diversity (0.0 - 1.0)
    composite: float  # Final MATL score

    calculated_at: str
    confidence: float  # How confident we are in this score


class MATLEngine:
    """
    Calculate MATL trust scores for Luminous Nix users.

    Integrates with:
    - User interaction history
    - Command patterns
    - Temporal behavior
    - Error rates
    """

    def __init__(self, storage_path: Optional[str] = None):
        """Initialize MATL engine."""
        from pathlib import Path
        self.storage_path = Path(storage_path or Path.home() / ".luminous-nix" / "matl")
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Score cache
        self.score_cache: Dict[str, MATLScore] = {}

    def calculate_trust(self, user_did: str, interaction_history: List[Dict]) -> MATLScore:
        """
        Calculate MATL trust score for a user.

        Args:
            user_did: User's DID
            interaction_history: List of recent interactions

        Returns:
            MATLScore object with composite trust score
        """
        # Calculate three components
        pogq = self._calculate_pogq(interaction_history)
        tcdm = self._calculate_tcdm(interaction_history)
        entropy = self._calculate_entropy(interaction_history)

        # Composite score (weighted average)
        composite = (pogq * 0.4) + (tcdm * 0.3) + (entropy * 0.3)

        # Calculate confidence based on sample size
        confidence = min(len(interaction_history) / 100.0, 1.0)

        score = MATLScore(
            pogq=pogq,
            tcdm=tcdm,
            entropy=entropy,
            composite=composite,
            calculated_at=datetime.now().isoformat(),
            confidence=confidence
        )

        # Cache score
        self.score_cache[user_did] = score
        self._save_score(user_did, score)

        return score

    def _calculate_pogq(self, interactions: List[Dict]) -> float:
        """
        Proof of Genuine Query - Are interactions genuine NixOS operations?

        Indicators of genuine usage:
        - Variety of commands
        - Reasonable timing between commands
        - Errors followed by corrections
        - Learning progression

        Indicators of scripted/bot usage:
        - Exact same commands repeated
        - Inhuman timing (too fast or too regular)
        - No learning/adaptation
        - No errors (too perfect)
        """
        if not interactions:
            return 0.5  # Neutral score for new users

        # Calculate indicators
        command_variety = self._calculate_command_variety(interactions)
        timing_naturalness = self._calculate_timing_naturalness(interactions)
        error_correction_pattern = self._detect_error_corrections(interactions)
        learning_curve = self._detect_learning_progression(interactions)

        # Weighted combination
        pogq = (
            command_variety * 0.3 +
            timing_naturalness * 0.3 +
            error_correction_pattern * 0.2 +
            learning_curve * 0.2
        )

        return max(0.0, min(1.0, pogq))

    def _calculate_tcdm(self, interactions: List[Dict]) -> float:
        """
        Temporal Consistency Deviation Metric - Behavioral consistency over time.

        High TCDM (good):
        - Consistent patterns over weeks/months
        - Gradual evolution
        - Predictable usage times

        Low TCDM (suspicious):
        - Sudden dramatic changes
        - Erratic patterns
        - Account compromise indicators
        """
        if len(interactions) < 10:
            return 0.5  # Need more data

        # Analyze temporal patterns
        time_of_day_consistency = self._analyze_time_of_day_patterns(interactions)
        command_pattern_stability = self._analyze_command_stability(interactions)
        session_length_consistency = self._analyze_session_consistency(interactions)

        # Detect anomalies
        anomaly_score = self._detect_temporal_anomalies(interactions)

        # High consistency = high TCDM
        tcdm = (
            time_of_day_consistency * 0.3 +
            command_pattern_stability * 0.3 +
            session_length_consistency * 0.2 +
            (1.0 - anomaly_score) * 0.2  # Invert anomaly score
        )

        return max(0.0, min(1.0, tcdm))

    def _calculate_entropy(self, interactions: List[Dict]) -> float:
        """
        Interaction Diversity - Variety of NixOS commands used.

        High entropy (good):
        - Uses many different commands
        - Explores various NixOS features
        - Adaptive tool usage

        Low entropy (suspicious):
        - Repeats same few commands
        - No exploration
        - Scripted behavior
        """
        if not interactions:
            return 0.5

        # Extract unique commands
        commands = [i.get("command", "") for i in interactions]
        unique_commands = set(commands)

        # Calculate Shannon entropy
        import math
        from collections import Counter

        command_counts = Counter(commands)
        total_commands = len(commands)

        entropy = 0.0
        for count in command_counts.values():
            probability = count / total_commands
            entropy -= probability * math.log2(probability)

        # Normalize to 0-1 range (max entropy for NixOS is ~log2(50) = 5.6)
        max_entropy = math.log2(min(len(unique_commands), 50))
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0

        return max(0.0, min(1.0, normalized_entropy))

    # Helper methods (simplified for brevity)

    def _calculate_command_variety(self, interactions: List[Dict]) -> float:
        """Calculate variety of commands used."""
        commands = [i.get("command", "") for i in interactions]
        unique_ratio = len(set(commands)) / len(commands) if commands else 0.0
        return unique_ratio

    def _calculate_timing_naturalness(self, interactions: List[Dict]) -> float:
        """Calculate how natural command timing is (human vs bot)."""
        # Analyze inter-command intervals
        intervals = []
        for i in range(1, len(interactions)):
            prev_time = datetime.fromisoformat(interactions[i-1]["timestamp"])
            curr_time = datetime.fromisoformat(interactions[i]["timestamp"])
            interval = (curr_time - prev_time).total_seconds()
            intervals.append(interval)

        if not intervals:
            return 0.5

        # Human intervals: varied, 5-120 seconds typical
        # Bot intervals: very consistent, often <1 second or exact multiples

        import statistics
        mean_interval = statistics.mean(intervals)
        std_interval = statistics.stdev(intervals) if len(intervals) > 1 else 0.0

        # High variance = more human-like
        # Mean in reasonable range (2-60s) = human-like
        naturalness = 0.0

        if 2 <= mean_interval <= 60:
            naturalness += 0.5

        if std_interval > mean_interval * 0.3:  # At least 30% variance
            naturalness += 0.5

        return naturalness

    def _detect_error_corrections(self, interactions: List[Dict]) -> float:
        """Detect if user corrects errors (human behavior)."""
        error_correction_pairs = 0
        total_errors = 0

        for i in range(len(interactions) - 1):
            if interactions[i].get("error", False):
                total_errors += 1
                # Check if next command is related (correction attempt)
                if self._are_commands_related(
                    interactions[i]["command"],
                    interactions[i+1]["command"]
                ):
                    error_correction_pairs += 1

        if total_errors == 0:
            return 0.5  # No errors to correct

        correction_rate = error_correction_pairs / total_errors
        return correction_rate

    def _detect_learning_progression(self, interactions: List[Dict]) -> float:
        """Detect if user is learning (human behavior)."""
        # Look for progression from simple to complex commands
        # Or from errors to success on same task type
        # Simplified for now
        return 0.7  # Placeholder

    def _analyze_time_of_day_patterns(self, interactions: List[Dict]) -> float:
        """Analyze consistency of time-of-day usage."""
        hours = []
        for interaction in interactions:
            timestamp = datetime.fromisoformat(interaction["timestamp"])
            hours.append(timestamp.hour)

        if not hours:
            return 0.5

        # Check if usage is clustered around certain hours (human pattern)
        from collections import Counter
        hour_counts = Counter(hours)

        # If usage concentrated in 4-8 hour window = consistent
        top_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:8]
        concentration = sum(count for _, count in top_hours) / len(hours)

        return concentration

    def _analyze_command_stability(self, interactions: List[Dict]) -> float:
        """Analyze if command patterns stay stable over time."""
        # Simplified: compare first half vs second half
        if len(interactions) < 20:
            return 0.5

        mid = len(interactions) // 2
        first_half = set(i["command"] for i in interactions[:mid])
        second_half = set(i["command"] for i in interactions[mid:])

        # Jaccard similarity
        intersection = len(first_half & second_half)
        union = len(first_half | second_half)

        similarity = intersection / union if union > 0 else 0.0
        return similarity

    def _analyze_session_consistency(self, interactions: List[Dict]) -> float:
        """Analyze if session lengths are consistent."""
        # Placeholder
        return 0.7

    def _detect_temporal_anomalies(self, interactions: List[Dict]) -> float:
        """Detect sudden behavioral changes (account compromise)."""
        # Placeholder
        return 0.2  # Low anomaly score

    def _are_commands_related(self, cmd1: str, cmd2: str) -> bool:
        """Check if two commands are related (correction attempt)."""
        # Simplified: check if they share keywords
        words1 = set(cmd1.split())
        words2 = set(cmd2.split())
        overlap = len(words1 & words2) / len(words1 | words2) if words1 | words2 else 0.0
        return overlap > 0.3

    def _save_score(self, user_did: str, score: MATLScore) -> None:
        """Save MATL score to storage."""
        score_file = self.storage_path / f"{user_did.split(':')[-1]}_matl.json"

        score_data = {
            "pogq": score.pogq,
            "tcdm": score.tcdm,
            "entropy": score.entropy,
            "composite": score.composite,
            "calculated_at": score.calculated_at,
            "confidence": score.confidence
        }

        with open(score_file, 'w') as f:
            json.dump(score_data, f, indent=2)


# Singleton
_matl_engine: Optional[MATLEngine] = None

def get_matl_engine() -> MATLEngine:
    """Get singleton MATL engine."""
    global _matl_engine
    if _matl_engine is None:
        _matl_engine = MATLEngine()
    return _matl_engine
```

### Usage Example:

```python
from luminous_nix.mycelix import get_matl_engine

# Get user's interaction history
interaction_history = [
    {
        "command": "nix-env -iA nixpkgs.firefox",
        "timestamp": "2025-12-03T10:15:00",
        "error": False
    },
    {
        "command": "nix-env -iA nixpkgs.postgres",  # Typo
        "timestamp": "2025-12-03T10:17:30",
        "error": True
    },
    {
        "command": "nix-env -iA nixpkgs.postgresql",  # Correction
        "timestamp": "2025-12-03T10:18:15",
        "error": False
    },
    # ... more interactions
]

# Calculate MATL trust score
engine = get_matl_engine()
score = engine.calculate_trust(
    user_did="did:mycelix:luminous_nix:QmXx...",
    interaction_history=interaction_history
)

print(f"MATL Score: {score.composite:.2f}")
print(f"  PoGQ (Genuine): {score.pogq:.2f}")
print(f"  TCDM (Consistent): {score.tcdm:.2f}")
print(f"  Entropy (Diverse): {score.entropy:.2f}")
print(f"  Confidence: {score.confidence:.2f}")

# Output:
# MATL Score: 0.78
#   PoGQ (Genuine): 0.82
#   TCDM (Consistent): 0.76
#   Entropy (Diverse): 0.74
#   Confidence: 0.85
```

---

## 📋 Week-by-Week Implementation Plan

### **Weeks 1-2: Foundation & Setup**

**Tasks**:
- [x] Create `src/luminous_nix/mycelix/` module structure
- [ ] Implement `DIDManager` class
- [ ] Add tests for DID creation/loading
- [ ] Integrate with existing `state_manager.py`
- [ ] Update CLI to create DID on first run

**Deliverables**:
- Working DID creation and storage
- Basic integration tests passing
- User can create DID via CLI

---

### **Weeks 3-4: MATL Trust Scoring**

**Tasks**:
- [ ] Implement `MATLEngine` class
- [ ] Implement PoGQ calculation
- [ ] Implement TCDM calculation
- [ ] Implement Entropy calculation
- [ ] Add tests for each component
- [ ] Integrate with interaction logging

**Deliverables**:
- MATL scoring functional
- Trust scores calculated for users
- Integration with Layer 6 (real-time intelligence)

---

### **Weeks 5-6: Epistemic Cube Classification**

**Tasks**:
- [ ] Implement `EpistemicClassifier`
- [ ] Map all Layer 5.5-6 AI data to E/N/M
- [ ] Implement materiality-based storage (M0-M3)
- [ ] Add pruning logic for ephemeral data
- [ ] Tests for classification accuracy

**Deliverables**:
- All AI knowledge classified by E/N/M
- Storage lifecycle management working
- Reduced storage footprint for ephemeral data

---

### **Weeks 7-8: Zero-TrustML Credits**

**Tasks**:
- [ ] Implement `Wallet` class
- [ ] Connect to Holochain Credits DNA
- [ ] Implement earn/spend logic
- [ ] Add transaction history
- [ ] Tests for credit operations

**Deliverables**:
- Users can earn/spend credits
- Wallet balance tracked
- Transaction history viewable

---

### **Weeks 9-10: Cross-Device Sync & Recovery**

**Tasks**:
- [ ] Implement Holochain DHT sync
- [ ] Implement social recovery (Shamir)
- [ ] Add recovery flow UI
- [ ] Test multi-device scenarios
- [ ] Document recovery process

**Deliverables**:
- Cross-device sync working
- Social recovery functional
- Recovery testing complete

---

### **Weeks 11-12: Integration & Polish**

**Tasks**:
- [ ] Integrate all components with Layers 1-6
- [ ] Performance optimization
- [ ] Security audit
- [ ] Documentation completion
- [ ] User guide creation
- [ ] Demo video/screenshots

**Deliverables**:
- Phase 1 fully integrated
- All tests passing (>90% coverage)
- Documentation complete
- Ready for user testing

---

## ✅ Success Criteria (Phase 1)

| Metric | Target | How to Measure |
|--------|--------|----------------|
| DID Creation Rate | 100% new users | % of first-runs that create DID |
| Cross-Device Sync | <5 seconds | Time to sync DID to second device |
| MATL Accuracy | >90% bot detection | % of bots correctly identified |
| Epistemic Classification | 100% AI data | % of data classified by E/N/M |
| Credit Circulation | 50% users active | % users earning/spending credits |
| Test Coverage | >90% | pytest coverage report |
| Performance | <100ms overhead | Time added by Mycelix components |

---

## 🚀 Getting Started

### Step 1: Set Up Development Environment

```bash
cd /srv/luminous-dynamics/11-meta-consciousness/luminous-nix

# Enter Nix dev shell
nix develop

# Install Python dependencies
poetry install

# Run existing tests to verify setup
pytest tests/
```

### Step 2: Create Mycelix Module Structure

```bash
# Create directories
mkdir -p src/luminous_nix/mycelix/{identity,trust,epistemic,credits}

# Create __init__.py files
touch src/luminous_nix/mycelix/__init__.py
touch src/luminous_nix/mycelix/identity/__init__.py
touch src/luminous_nix/mycelix/trust/__init__.py
touch src/luminous_nix/mycelix/epistemic/__init__.py
touch src/luminous_nix/mycelix/credits/__init__.py

# Create test directory
mkdir -p tests/mycelix
touch tests/mycelix/test_identity.py
touch tests/mycelix/test_matl.py
touch tests/mycelix/test_epistemic.py
touch tests/mycelix/test_credits.py
```

### Step 3: Start with DID Manager (Week 1)

```bash
# Create the DID manager file
# (Copy implementation from above)
code src/luminous_nix/mycelix/identity/did_manager.py

# Write first test
code tests/mycelix/test_identity.py
```

---

## 📚 Next Steps After Phase 1

Once Phase 1 is complete (12 weeks), we'll have:
- ✅ Sovereign identity for all users
- ✅ Byzantine-resistant trust scoring
- ✅ Epistemic classification of all AI knowledge
- ✅ Working credit system

Then we move to **Phase 2** (Q2-Q3 2026):
- Federated learning integration (when 0TML Phase 2 completes)
- ZK gradient verification
- Advanced Byzantine detection
- Cross-chain capabilities

---

**Layer 7 Phase 1 Implementation Plan**: COMPLETE ✨
**Ready to build**: All dependencies available NOW
**Timeline**: 12 weeks (3 months)
**Next action**: Create Mycelix module structure and start Week 1! 🚀

🌊 Let's build the foundation for collective intelligence! 💫
