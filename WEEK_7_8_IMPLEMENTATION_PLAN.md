# Week 7-8 Implementation Plan: Credits System

**Goal**: Implement epistemic-weighted credit allocation system
**Foundation**: Builds on Week 5-6 E/N/M classification
**Target**: 25+ tests, production-ready credit economics

---

## Overview

The **Credits System** rewards users based on the epistemic value of their interactions with Luminous Nix. Higher E/N/M coordinates earn more credits, incentivizing genuine learning and knowledge contribution.

### Core Principle

**Credits = f(E, N, M, Trust)**

The more verifiable (E), authoritative (N), and permanent (M) an interaction, the more credits it generates. Trust scores from MATL further modulate credit allocation.

---

## Architecture

### Components to Implement

1. **Credit Calculator** (`credits/calculator.py`)
   - E/N/M weighted credit formulas
   - Configurable weights and multipliers
   - Trust score integration

2. **Credit Ledger** (`credits/ledger.py`)
   - Per-user (DID) credit balances
   - Transaction log (earned, spent, transferred)
   - Query interface (balance, history, analytics)

3. **Credit Types** (`credits/types.py`)
   - `CreditAmount` - Value class with currency support
   - `CreditTransaction` - Earn/spend/transfer events
   - `CreditBalance` - Per-DID balance state

4. **Integration** (`credits/integration.py`)
   - Auto-credit allocation on interaction logging
   - Hook into `InteractionLogger`
   - Sync with E/N/M classifier

---

## Credit Allocation Formula

### Base Formula

```
credits = base_rate × E_multiplier × N_multiplier × M_multiplier × trust_modifier
```

### Default Multipliers

**E-Axis Multipliers** (Empirical Verifiability):
- E0 (Null): 0.0× (no credits for unverifiable)
- E1 (Testimonial): 0.5×
- E2 (Audit): 1.0× (baseline)
- E3 (Cryptographic): 2.0×
- E4 (Public): 3.0× (highest empirical value)

**N-Axis Multipliers** (Normative Authority):
- N0 (Personal): 1.0× (baseline)
- N1 (Communal): 1.5× (future: shared knowledge)
- N2 (Network): 2.5× (future: consensus contributions)
- N3 (Axiomatic): 4.0× (fundamental knowledge)

**M-Axis Multipliers** (Materiality/Permanence):
- M0 (Ephemeral): 0.0× (no credits for discarded interactions)
- M1 (Temporal): 0.5×
- M2 (Persistent): 1.5×
- M3 (Foundational): 3.0× (highest value - preserves forever)

**Trust Modifier** (MATL Score):
```
trust_modifier = 0.5 + (matl_score × 0.5)
  Range: 0.5× to 1.0× (low trust to high trust)
```

### Base Rate

Default: **10 credits** per successful interaction

### Example Calculations

**Search for "firefox" (found packages)**:
- E4 (public) × N0 (personal) × M3 (foundational) × trust(0.8)
- 10 × 3.0 × 1.0 × 3.0 × 0.9 = **81 credits**

**Install package (successful)**:
- E2 (audit) × N0 (personal) × M2 (persistent) × trust(0.8)
- 10 × 1.0 × 1.0 × 1.5 × 0.9 = **13.5 credits**

**Simple query (testimonial)**:
- E1 (testimonial) × N0 (personal) × M1 (temporal) × trust(0.8)
- 10 × 0.5 × 1.0 × 0.5 × 0.9 = **2.25 credits**

**Failed operation**:
- E0 × M0 = **0 credits** (unverifiable and ephemeral)

---

## Credit Ledger Design

### Storage Structure

**SQLite Database** (`~/.luminous-nix/credits.db`):

```sql
CREATE TABLE credit_balances (
    user_did TEXT PRIMARY KEY,
    total_earned REAL DEFAULT 0.0,
    total_spent REAL DEFAULT 0.0,
    current_balance REAL DEFAULT 0.0,
    last_updated TEXT
);

CREATE TABLE credit_transactions (
    tx_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    user_did TEXT NOT NULL,
    tx_type TEXT NOT NULL,  -- 'earn', 'spend', 'transfer_in', 'transfer_out'
    amount REAL NOT NULL,
    interaction_id TEXT,  -- Reference to interaction (if applicable)
    epistemic_e REAL,
    epistemic_n REAL,
    epistemic_m INTEGER,
    matl_score REAL,
    description TEXT,
    FOREIGN KEY (user_did) REFERENCES credit_balances(user_did)
);

CREATE INDEX idx_user_transactions ON credit_transactions(user_did, timestamp);
CREATE INDEX idx_tx_type ON credit_transactions(tx_type);
```

### Credit Balance Operations

- `get_balance(user_did)` → current balance
- `earn_credits(user_did, amount, interaction)` → record earning
- `spend_credits(user_did, amount, description)` → deduct credits
- `transfer_credits(from_did, to_did, amount)` → peer-to-peer transfer
- `get_transaction_history(user_did, limit)` → transaction log

---

## Integration Points

### 1. InteractionLogger Integration

Modify `InteractionLogger.log_interaction()` to:
1. Classify interaction (E/N/M) ✅ (Already done in Week 5-6)
2. Calculate credits based on E/N/M
3. Allocate credits to user's DID
4. Log credit transaction

### 2. MATL Engine Integration

Use existing MATL trust scores to modulate credit allocation:
- High trust users get full credit multiplier
- Low trust users get reduced credits
- Prevents gaming/bot abuse

---

## Future Features (Post-Week 7-8)

### Credit Spending (Phase 2)
- Unlock premium features
- Priority support
- Custom configurations
- Community marketplace

### Credit Transfers (Phase 2)
- Peer-to-peer transfers
- Gift credits to help others
- Community pooling
- Incentive alignment

### Credit Analytics (Phase 2)
- Leaderboards (opt-in)
- Achievement badges
- Credit earning trends
- Comparative analytics

---

## Implementation Tasks

### Week 7-8 Deliverables

**Core Implementation** (5 files):
1. `credits/types.py` - CreditAmount, CreditTransaction, CreditBalance
2. `credits/calculator.py` - Credit calculation logic
3. `credits/ledger.py` - SQLite-based credit ledger
4. `credits/integration.py` - InteractionLogger integration
5. `credits/__init__.py` - Module exports

**Testing** (3 files, 25+ tests):
1. `test_credit_calculator.py` - Formula tests (~10 tests)
2. `test_credit_ledger.py` - Storage tests (~8 tests)
3. `test_credit_integration.py` - End-to-end tests (~7 tests)

**Documentation** (1 file):
1. `WEEK_7_8_COMPLETE.md` - Completion summary

---

## Success Criteria

- ✅ Credit calculator with E/N/M weighting
- ✅ SQLite-based credit ledger
- ✅ Automatic credit allocation on interactions
- ✅ MATL trust score integration
- ✅ 25+ comprehensive tests
- ✅ Transaction history and analytics
- ✅ Production-ready with error handling

---

## Design Decisions

### 1. Why SQLite for Credits?

**Decision**: Use SQLite instead of JSON files
**Rationale**:
- Efficient queries (balance, history)
- ACID transactions
- Concurrent access
- Scales to millions of transactions

### 2. Why Multiplicative Formula?

**Decision**: Multiply E × N × M instead of add
**Rationale**:
- E0 or M0 → 0 credits (correct behavior)
- Rewards high-value interactions exponentially
- Intuitive: "foundational + public + axiomatic = very valuable"

### 3. Why Trust Modifier?

**Decision**: Modulate credits by MATL trust score
**Rationale**:
- Prevents bot abuse
- Rewards genuine users
- Aligns incentives with trust
- Anti-gaming measure

### 4. Why No Negative Credits?

**Decision**: Don't penalize with negative credits
**Rationale**:
- Positive reinforcement only
- Failed ops = 0 credits (not -10)
- Trust score handles bad actors
- Simpler mental model

---

## Open Questions for User

1. **Base Rate**: Is 10 credits per interaction a good starting point?
2. **Spending**: What features should credits unlock? (Future phase)
3. **Transfers**: Should peer-to-peer transfers be allowed? (Future phase)
4. **Caps**: Should there be daily/weekly earning caps to prevent gaming?
5. **Decay**: Should credits decay over time (use it or lose it)?

---

## Next Steps

1. Create `credits/types.py` with dataclasses
2. Implement `credits/calculator.py` with E/N/M formula
3. Build `credits/ledger.py` with SQLite storage
4. Integrate with `InteractionLogger`
5. Write comprehensive tests (25+ target)
6. Document in `WEEK_7_8_COMPLETE.md`

**Estimated Completion**: 2-4 hours of focused implementation

---

*This plan builds directly on Week 5-6 Epistemic Cube foundation, creating an economic layer that incentivizes high-quality, verifiable, and lasting contributions to the knowledge graph.*
