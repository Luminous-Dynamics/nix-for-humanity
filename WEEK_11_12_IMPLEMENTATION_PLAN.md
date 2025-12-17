# 📋 Week 11-12: Holochain DHT Integration - Implementation Plan

**Status**: 🟡 PLANNING
**Target**: Enable distributed/decentralized Mycelix operation
**Estimated Tests**: 30-40 tests
**Dependencies**: Weeks 1-8 (Identity, Trust, Epistemic, Credits)

---

## 🎯 Objectives

Transform Mycelix from a **local-only system** to a **distributed network** using Holochain's DHT (Distributed Hash Table) for:

1. **Cross-device DID synchronization** - Same identity across all devices
2. **Distributed credit ledger** - Credits persist across the network
3. **P2P credit transfers** - Direct transfers between users
4. **Social recovery** - Restore DIDs via trusted guardians
5. **Interaction attestation** - Other nodes validate your interactions

---

## 🏗️ Architecture Overview

### Holochain Integration Points

```
┌─────────────────────────────────────────────────────────────┐
│                    Mycelix Local Node                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   DID Mgr    │  │ Credit Ledger│  │  Interaction │    │
│  │   (Local)    │  │   (Local)    │  │    Logger    │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                 │                  │             │
│         ▼                 ▼                  ▼             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │           Holochain DHT Sync Layer                  │  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌──────────────┐ │  │
│  │  │   DID Sync  │ │ Credit Sync │ │ Attestation  │ │  │
│  │  │   (hApp)    │ │   (hApp)    │ │   (hApp)     │ │  │
│  │  └─────────────┘ └─────────────┘ └──────────────┘ │  │
│  └─────────────────────────────────────────────────────┘  │
│         │                 │                  │             │
│         ▼                 ▼                  ▼             │
└─────────┼─────────────────┼──────────────────┼─────────────┘
          │                 │                  │
          │                 │                  │
┌─────────▼─────────────────▼──────────────────▼─────────────┐
│                  Holochain DHT Network                      │
│  (Distributed across all Mycelix nodes globally)            │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

**DID Synchronization**:
1. Local DID created → Published to DHT
2. Other devices fetch DID from DHT
3. Updates (e.g., assurance level) → Synced across devices
4. Social recovery guardians stored on DHT

**Credit Synchronization**:
1. Local credit transaction → Published to DHT
2. Other nodes validate transaction
3. Credit balance computed from DHT history
4. Conflict resolution via CRDTs

**Interaction Attestation**:
1. Local interaction logged
2. Published to DHT for attestation
3. Other nodes can verify/challenge
4. Consensus builds reputation

---

## 📦 Components to Implement

### 1. Holochain DNA Configuration

**File**: `holochain/mycelix-dna/dna.yaml`

```yaml
---
manifest_version: "1"
name: mycelix
integrity:
  uid: 00000000-0000-0000-0000-000000000000
  origin_time: 2025-01-01T00:00:00.000000Z
  zomes:
    - name: did_sync
      dependencies: []
    - name: credit_sync
      dependencies: []
    - name: attestation
      dependencies: []
coordinator:
  zomes:
    - name: did_coordinator
      dependencies: [did_sync]
    - name: credit_coordinator
      dependencies: [credit_sync]
    - name: attestation_coordinator
      dependencies: [attestation]
```

### 2. DID Synchronization Zome

**File**: `holochain/zomes/did_sync/src/lib.rs`

```rust
use hdk::prelude::*;

#[hdk_entry_helper]
pub struct DIDAnchor {
    did: String,
    public_key: String,
    assurance_level: String,
    created_at: Timestamp,
}

#[hdk_extern]
pub fn publish_did(did: DIDAnchor) -> ExternResult<ActionHash> {
    create_entry(EntryTypes::DIDAnchor(did))
}

#[hdk_extern]
pub fn get_did(did_str: String) -> ExternResult<Option<DIDAnchor>> {
    // Query DHT for DID
}

#[hdk_extern]
pub fn update_assurance_level(did: String, level: String) -> ExternResult<ActionHash> {
    // Update DID assurance level
}
```

### 3. Credit Synchronization Zome

**File**: `holochain/zomes/credit_sync/src/lib.rs`

```rust
use hdk::prelude::*;

#[hdk_entry_helper]
pub struct CreditTransaction {
    from_did: String,
    to_did: Option<String>,  // None for EARN
    amount: f64,
    tx_type: String,
    epistemic_e: f64,
    epistemic_n: f64,
    epistemic_m: u8,
    timestamp: Timestamp,
}

#[hdk_extern]
pub fn publish_credit_tx(tx: CreditTransaction) -> ExternResult<ActionHash> {
    // Validate transaction
    // Publish to DHT
}

#[hdk_extern]
pub fn get_balance(did: String) -> ExternResult<f64> {
    // Query all transactions for DID
    // Compute balance from CRDT
}

#[hdk_extern]
pub fn get_transaction_history(did: String) -> ExternResult<Vec<CreditTransaction>> {
    // Query DHT for transactions
}
```

### 4. Attestation Zome

**File**: `holochain/zomes/attestation/src/lib.rs`

```rust
use hdk::prelude::*;

#[hdk_entry_helper]
pub struct InteractionAttestation {
    user_did: String,
    operation_type: String,
    epistemic_e: f64,
    epistemic_n: f64,
    epistemic_m: u8,
    timestamp: Timestamp,
    attestor_did: String,  // Who is attesting this
}

#[hdk_extern]
pub fn publish_attestation(att: InteractionAttestation) -> ExternResult<ActionHash> {
    // Publish attestation to DHT
}

#[hdk_extern]
pub fn get_attestations(interaction_hash: String) -> ExternResult<Vec<InteractionAttestation>> {
    // Get all attestations for an interaction
}
```

### 5. Python-Holochain Bridge

**File**: `src/luminous_nix/mycelix/holochain/bridge.py`

```python
"""
Holochain Bridge for Mycelix

Connects Python code to Holochain hApps via websocket.
"""

import json
import asyncio
from typing import Optional, Dict, Any
import websockets
from pathlib import Path


class HolochainBridge:
    """
    Bridge between Python and Holochain

    Features:
    - Async websocket communication
    - Automatic reconnection
    - Request/response handling
    - Event streaming
    """

    def __init__(
        self,
        app_id: str = "mycelix",
        port: int = 8888
    ):
        self.app_id = app_id
        self.port = port
        self.ws_url = f"ws://localhost:{port}"
        self._connection = None

    async def connect(self):
        """Connect to Holochain conductor"""
        self._connection = await websockets.connect(self.ws_url)

    async def call_zome(
        self,
        zome_name: str,
        fn_name: str,
        payload: Dict[str, Any]
    ) -> Any:
        """
        Call Holochain zome function

        Args:
            zome_name: Name of zome (e.g., "did_sync")
            fn_name: Function name (e.g., "publish_did")
            payload: Function arguments

        Returns:
            Function result
        """
        request = {
            "type": "app_request",
            "data": {
                "role_name": "mycelix",
                "zome_name": zome_name,
                "fn_name": fn_name,
                "payload": payload
            }
        }

        await self._connection.send(json.dumps(request))
        response = await self._connection.recv()

        result = json.loads(response)
        if "error" in result:
            raise Exception(f"Holochain error: {result['error']}")

        return result.get("data")

    async def close(self):
        """Close connection"""
        if self._connection:
            await self._connection.close()
```

### 6. DID Manager DHT Integration

**File**: `src/luminous_nix/mycelix/identity/did_manager_dht.py`

```python
"""
DID Manager with Holochain DHT synchronization
"""

from typing import Optional
from pathlib import Path
import asyncio

from .did_manager import DIDManager, LuminousNixDID
from ..holochain import HolochainBridge


class DIDManagerDHT(DIDManager):
    """
    DID Manager with DHT synchronization

    Features:
    - Publishes DIDs to Holochain DHT
    - Fetches DIDs from other devices
    - Syncs assurance level updates
    - Social recovery coordination
    """

    def __init__(
        self,
        storage_path: Optional[Path] = None,
        enable_dht: bool = True
    ):
        super().__init__(storage_path)
        self.enable_dht = enable_dht
        self._bridge = HolochainBridge() if enable_dht else None

    def create_did(self, passphrase: Optional[str] = None) -> LuminousNixDID:
        """Create DID and publish to DHT"""
        did = super().create_did(passphrase)

        if self.enable_dht:
            asyncio.run(self._publish_to_dht(did))

        return did

    async def _publish_to_dht(self, did: LuminousNixDID):
        """Publish DID to Holochain DHT"""
        await self._bridge.connect()

        try:
            result = await self._bridge.call_zome(
                "did_sync",
                "publish_did",
                {
                    "did": did.did,
                    "public_key": did.public_key,
                    "assurance_level": did.assurance_level,
                    "created_at": did.created_at
                }
            )
            print(f"✅ DID published to DHT: {result}")
        finally:
            await self._bridge.close()

    async def fetch_from_dht(self, did_str: str) -> Optional[LuminousNixDID]:
        """Fetch DID from DHT (for other devices)"""
        await self._bridge.connect()

        try:
            result = await self._bridge.call_zome(
                "did_sync",
                "get_did",
                {"did": did_str}
            )

            if result:
                return LuminousNixDID(**result)
        finally:
            await self._bridge.close()
```

### 7. Credit Ledger DHT Integration

**File**: `src/luminous_nix/mycelix/credits/ledger_dht.py`

```python
"""
Credit Ledger with Holochain DHT synchronization
"""

from typing import Optional
from pathlib import Path
import asyncio

from .ledger import CreditLedger, CreditTransaction, CreditAmount
from ..holochain import HolochainBridge


class CreditLedgerDHT(CreditLedger):
    """
    Credit Ledger with DHT synchronization

    Features:
    - Publishes credit transactions to DHT
    - Computes balance from DHT history
    - P2P credit transfers
    - Conflict resolution via CRDTs
    """

    def __init__(
        self,
        db_path: Optional[Path] = None,
        enable_dht: bool = True
    ):
        super().__init__(db_path)
        self.enable_dht = enable_dht
        self._bridge = HolochainBridge() if enable_dht else None

    def earn_credits(
        self,
        user_did: str,
        amount: CreditAmount,
        transaction: CreditTransaction
    ):
        """Earn credits and publish to DHT"""
        balance = super().earn_credits(user_did, amount, transaction)

        if self.enable_dht:
            asyncio.run(self._publish_to_dht(transaction))

        return balance

    async def _publish_to_dht(self, tx: CreditTransaction):
        """Publish transaction to DHT"""
        await self._bridge.connect()

        try:
            result = await self._bridge.call_zome(
                "credit_sync",
                "publish_credit_tx",
                {
                    "from_did": tx.user_did,
                    "to_did": None,  # EARN transaction
                    "amount": tx.amount.value,
                    "tx_type": tx.tx_type.value,
                    "epistemic_e": tx.epistemic_e,
                    "epistemic_n": tx.epistemic_n,
                    "epistemic_m": tx.epistemic_m,
                    "timestamp": tx.timestamp.isoformat()
                }
            )
            print(f"✅ Credit transaction published to DHT")
        finally:
            await self._bridge.close()

    async def fetch_balance_from_dht(self, did: str) -> CreditAmount:
        """Fetch balance from DHT (CRDT computed)"""
        await self._bridge.connect()

        try:
            balance = await self._bridge.call_zome(
                "credit_sync",
                "get_balance",
                {"did": did}
            )

            return CreditAmount(balance)
        finally:
            await self._bridge.close()
```

---

## 🧪 Testing Strategy

### Test Categories

1. **Holochain Zome Tests** (Rust)
   - DID publishing and retrieval
   - Credit transaction validation
   - Attestation storage
   - ~15 tests

2. **Python Bridge Tests**
   - Websocket connection
   - Zome function calls
   - Error handling
   - ~8 tests

3. **Integration Tests**
   - End-to-end DID sync
   - End-to-end credit sync
   - Multi-node scenarios
   - ~12 tests

**Total Estimated**: 30-40 tests

### Test Files

```
tests/mycelix/holochain/
├── test_did_sync_zome.rs         # Rust zome tests
├── test_credit_sync_zome.rs
├── test_attestation_zome.rs
├── test_holochain_bridge.py      # Python bridge tests
├── test_did_manager_dht.py       # DHT integration tests
├── test_credit_ledger_dht.py
└── test_dht_integration.py       # End-to-end tests
```

---

## 📋 Implementation Checklist

### Phase 1: Setup (2-3 hours)
- [ ] Install Holochain toolchain (`hc`, `holochain`)
- [ ] Create Mycelix DNA structure
- [ ] Set up Rust zome templates
- [ ] Configure Python dependencies (websockets)

### Phase 2: DID Synchronization (4-5 hours)
- [ ] Implement `did_sync` zome
- [ ] Create `HolochainBridge` Python module
- [ ] Implement `DIDManagerDHT`
- [ ] Write DID sync tests (~8 tests)

### Phase 3: Credit Synchronization (4-5 hours)
- [ ] Implement `credit_sync` zome
- [ ] Implement `CreditLedgerDHT`
- [ ] Add CRDT balance computation
- [ ] Write credit sync tests (~10 tests)

### Phase 4: Attestation (3-4 hours)
- [ ] Implement `attestation` zome
- [ ] Add attestation logic to InteractionLogger
- [ ] Write attestation tests (~7 tests)

### Phase 5: Integration & Testing (3-4 hours)
- [ ] Multi-node integration tests
- [ ] Performance testing
- [ ] Documentation
- [ ] Create WEEK_11_12_COMPLETE.md

**Total Estimated Time**: 16-21 hours

---

## 🎯 Success Criteria

- [ ] DIDs sync across multiple Holochain nodes
- [ ] Credit balances computed from DHT history
- [ ] P2P credit transfers working
- [ ] 30-40 tests passing
- [ ] <500ms latency for DHT operations
- [ ] Documentation complete

---

## 🔮 Future Enhancements

- [ ] Social recovery implementation
- [ ] Interaction attestation consensus
- [ ] DHT sharding for scalability
- [ ] Cross-chain bridges (e.g., Ethereum)

---

## 📚 Resources

- [Holochain Documentation](https://developer.holochain.org/)
- [Holochain HDK (Rust)](https://docs.rs/hdk/)
- [Mycelix Network Charter](../../00-sacred-foundation/wisdom/mycelix-network-charter.md)

---

**Status**: Ready to begin implementation
**Next Step**: Install Holochain toolchain and create DNA structure

---

*Weeks 11-12: Connecting Mycelix to the distributed future* 🌐
