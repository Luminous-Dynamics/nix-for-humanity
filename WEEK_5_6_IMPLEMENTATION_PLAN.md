# 🎯 Week 5-6 Implementation Plan: Epistemic Cube Classification

**Date**: December 4, 2025 - December 18, 2025
**Component**: Epistemic Cube (E/N/M) Classification System
**Status**: Planning (Week 3-4 complete: 101/101 tests ✅)

---

## 🚀 What We're Building

**Epistemic Cube = E/N/M Classification**

A knowledge classification system that categorizes all AI-generated knowledge into three dimensions:

1. **E (Epistemic)** - How we know (verifiability, evidence, methodology)
2. **N (Normative)** - What we should do (values, ethics, preferences)
3. **M (Metaphysical)** - What exists (ontology, being, reality)

Combined with **Materiality Levels** (M0-M3) to manage storage lifecycle:
- **M0**: Ephemeral (temporary, disposable)
- **M1**: Session-based (keep for current session)
- **M2**: Personal (user's history)
- **M3**: Foundational (core knowledge, permanent)

---

## 📋 Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                 EpistemicClassifier                      │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  E Dimension │  │  N Dimension │  │  M Dimension │ │
│  │              │  │              │  │              │ │
│  │  Verifiable? │  │  Value-based?│  │  Ontological?│ │
│  │  Evidence?   │  │  Preference? │  │  Existence?  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │      Materiality Classifier (M0-M3)               │  │
│  │                                                    │  │
│  │  M0: Ephemeral (temp calculations, debug logs)   │  │
│  │  M1: Session (current conversation context)       │  │
│  │  M2: Personal (user's query history, preferences)│  │
│  │  M3: Foundational (core NixOS knowledge)        │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Storage Lifecycle Manager                 │  │
│  │                                                    │  │
│  │  • Prune M0 data (immediate or very short TTL)   │  │
│  │  • Expire M1 data (end of session)               │  │
│  │  • Retain M2 data (user profile lifetime)        │  │
│  │  • Persist M3 data (permanent)                   │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 📚 E/N/M Classification Framework

### Epistemic (E) Dimension

**Question**: "How do we know this?"

**Categories**:
- **E-High**: Directly verifiable (package exists in nixpkgs repo)
- **E-Medium**: Probabilistic (likely based on patterns)
- **E-Low**: Speculative (guesses, hypotheses)
- **E-None**: Not knowledge claims (commands, preferences)

**Examples**:
- "firefox is in nixpkgs" → **E-High** (verifiable fact)
- "You might like vim" → **E-Medium** (inference from patterns)
- "This could be a security risk" → **E-Low** (hypothesis)
- "Install git" → **E-None** (command, not a claim)

### Normative (N) Dimension

**Question**: "What should we do?"

**Categories**:
- **N-High**: Strong ethical/value implications
- **N-Medium**: Preferences and recommendations
- **N-Low**: Neutral suggestions
- **N-None**: Pure facts

**Examples**:
- "Never run untrusted code" → **N-High** (security imperative)
- "I recommend using Nix flakes" → **N-Medium** (preference)
- "You could use either" → **N-Low** (neutral option)
- "nixpkgs has 80,000 packages" → **N-None** (pure fact)

### Metaphysical (M) Dimension

**Question**: "What exists? What is real?"

**Categories**:
- **M-High**: Ontological claims (what entities exist)
- **M-Medium**: Conceptual frameworks
- **M-Low**: Operational definitions
- **M-None**: No ontological content

**Examples**:
- "A package is a derivation in Nix" → **M-High** (ontological definition)
- "Flakes are a way to organize Nix code" → **M-Medium** (conceptual framework)
- "Search means querying nixpkgs" → **M-Low** (operational definition)
- "Install vim" → **M-None** (action, no ontology)

---

## 🗄️ Materiality-Based Storage

### M0: Ephemeral (Immediately Disposable)

**Lifetime**: Milliseconds to seconds
**Storage**: In-memory only, no persistence

**Examples**:
- Intermediate calculation steps
- Debug logging output
- Temporary query rewrites
- Cache miss notifications

**Action**: Prune immediately or very short TTL

### M1: Session-Based (Current Interaction)

**Lifetime**: Duration of current session
**Storage**: Session cache, cleared on exit

**Examples**:
- Current conversation context
- Active query history (this session)
- Temporary user preferences
- In-flight operation status

**Action**: Expire at session end

### M2: Personal (User History)

**Lifetime**: User profile lifetime
**Storage**: User profile database

**Examples**:
- All user queries (for trust scoring)
- User preferences and settings
- Learned behavioral patterns
- Personal NixOS configuration history

**Action**: Retain indefinitely (tied to user DID)

### M3: Foundational (Core Knowledge)

**Lifetime**: Permanent
**Storage**: Core knowledge base

**Examples**:
- NixOS package metadata
- Nix language reference
- Core trust scoring algorithms
- System architecture knowledge

**Action**: Never prune (update/extend only)

---

## 🔧 Implementation Plan

### Week 5: Core Classification (Days 1-7)

#### Day 1-2: E/N/M Classifier Base
- [ ] Create `EpistemicClassifier` base class
- [ ] Define E/N/M scoring methods (0.0-1.0 for each dimension)
- [ ] Implement simple rule-based classification
- [ ] Write 10 tests for basic classification

**Files to Create**:
- `src/luminous_nix/mycelix/epistemic/__init__.py`
- `src/luminous_nix/mycelix/epistemic/classifier.py`
- `src/luminous_nix/mycelix/epistemic/types.py`
- `tests/mycelix/test_epistemic_classifier.py`

#### Day 3-4: Materiality Classifier
- [ ] Create `MaterialityClassifier`
- [ ] Implement M0-M3 classification logic
- [ ] Add TTL/lifetime management
- [ ] Write 8 tests for materiality levels

**Files to Create**:
- `src/luminous_nix/mycelix/epistemic/materiality.py`
- `tests/mycelix/test_materiality.py`

#### Day 5-7: Knowledge Types Integration
- [ ] Map all AI response types to E/N/M
- [ ] Classify interactions from MATL system
- [ ] Classify NixOS operations
- [ ] Write 12 tests for integration

**Files to Modify**:
- `src/luminous_nix/mycelix/trust/matl_types.py` (add E/N/M fields)
- `src/luminous_nix/core/user_profile.py` (track epistemic scores)

### Week 6: Storage Management (Days 8-14)

#### Day 8-10: Storage Lifecycle Manager
- [ ] Create `StorageLifecycleManager`
- [ ] Implement pruning logic for M0
- [ ] Implement expiration logic for M1
- [ ] Write 10 tests for lifecycle

**Files to Create**:
- `src/luminous_nix/mycelix/epistemic/storage_manager.py`
- `tests/mycelix/test_storage_manager.py`

#### Day 11-12: Integration with Existing Systems
- [ ] Integrate with `InteractionLogger`
- [ ] Add E/N/M classification to all logged interactions
- [ ] Implement automatic pruning in background
- [ ] Write 8 tests for integration

**Files to Modify**:
- `src/luminous_nix/mycelix/trust/interaction_logger.py`
- `src/luminous_nix/core/user_profile.py`

#### Day 13-14: Polish & Documentation
- [ ] Performance optimization
- [ ] Add explanations for classifications
- [ ] Write comprehensive documentation
- [ ] Create completion report

**Files to Create**:
- `WEEK_5_6_COMPLETE.md`

---

## 🎯 Success Criteria

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Classification Coverage** | 100% of AI data | % of interactions classified |
| **Accuracy** | >85% human agreement | Manual review of sample classifications |
| **Storage Reduction** | >50% for M0/M1 data | Compare storage before/after pruning |
| **Performance** | <10ms overhead | Time to classify + store |
| **Test Coverage** | 60+ new tests | pytest count |
| **Combined Tests** | 160+ total | Week 1-6 combined |

---

## 📊 Data Model

### EpistemicScore

```python
@dataclass
class EpistemicScore:
    """E/N/M classification result"""

    # E/N/M dimensions (0.0-1.0)
    epistemic: float      # How verifiable?
    normative: float      # How value-laden?
    metaphysical: float   # How ontological?

    # Materiality level
    materiality: int      # 0-3 (M0-M3)

    # Metadata
    classified_at: datetime
    classifier_version: str
    explanation: str      # Human-readable rationale
```

### Classified Interaction

```python
@dataclass
class ClassifiedInteraction:
    """Interaction with E/N/M classification"""

    # Original interaction (from Week 2)
    interaction: Interaction

    # E/N/M classification
    epistemic_score: EpistemicScore

    # Storage metadata
    storage_tier: int     # M0-M3
    ttl_seconds: Optional[int]  # Time to live (None = permanent)
    expires_at: Optional[datetime]  # When to prune (None = never)
```

---

## 🔮 Integration with Previous Weeks

### Week 1-2 (Identity)
- User DID tracks epistemic development over time
- Assurance level influenced by epistemic rigor

### Week 3-4 (MATL Trust)
- Trust scores weighted by epistemic quality
- High E-score claims more trustworthy
- Track epistemic progression as learning signal

### Week 5-6 (Epistemic Cube) ← NEW
- All knowledge gets E/N/M classification
- Storage managed by materiality level
- Foundation for trust-weighted knowledge

### Week 7-8 (Credits)
- Earn credits for high-epistemic contributions
- Cost based on storage materiality (M3 costs more)

---

## ⚠️ Open Questions (Need Clarification)

1. **E/N/M Scoring Algorithm**:
   - Should we use rule-based or ML-based classification?
   - What are the exact criteria for each dimension?
   - How do we handle multi-dimensional content?

2. **Materiality Thresholds**:
   - What makes something M0 vs M1?
   - How do we determine materiality automatically?
   - Can users override materiality levels?

3. **Storage Integration**:
   - Where is M2 data actually stored? (SQLite? JSON files?)
   - Where is M3 data stored? (Separate from M2?)
   - How do we handle pruning in multi-user scenarios?

4. **Performance Targets**:
   - What's acceptable classification latency?
   - How often should pruning run?
   - Memory constraints for classification?

---

## 📝 Next Steps

### Immediate
1. **Clarify E/N/M specification** (this document serves as starting point)
2. **Define precise classification criteria** for each dimension
3. **Determine materiality thresholds** for automated classification
4. **Begin implementation** once specification confirmed

### After Week 5-6
- Week 7-8: Credits System (trust-weighted rewards)
- Week 9-10: Cross-device sync & social recovery
- Week 11-12: Integration & polish

---

## 🌟 Key Principles

### 1. Transparency
- All classifications are explainable
- Users can see why something was classified as E/N/M
- No black-box classification

### 2. User Control
- Users can override materiality levels
- Users can see what's being pruned
- Users can prevent pruning

### 3. Privacy First
- All classification happens locally
- No data sent to servers
- User controls retention policy

### 4. Efficiency
- Minimal performance overhead
- Aggressive pruning of ephemeral data
- Efficient storage of permanent data

---

## 📈 Progress Tracking

| Day | Component | Status | Tests |
|-----|-----------|--------|-------|
| 1-2 | E/N/M Classifier | 🔄 Pending | 0/10 |
| 3-4 | Materiality Classifier | 🔄 Pending | 0/8 |
| 5-7 | Knowledge Types Integration | 🔄 Pending | 0/12 |
| 8-10 | Storage Lifecycle Manager | 🔄 Pending | 0/10 |
| 11-12 | System Integration | 🔄 Pending | 0/8 |
| 13-14 | Polish & Documentation | 🔄 Pending | 0/0 |
| **Total** | **Week 5-6** | **🔄 Planning** | **0/48** |

**Current**: 101/101 tests passing (Week 1-4)
**Target**: 150+ tests passing (Week 1-6)

---

## 🤔 Decision Points

Before proceeding with implementation, we need to decide:

**1. Classification Approach**
- [ ] Simple rule-based (fast, transparent)
- [ ] ML-based (accurate, requires training)
- [ ] Hybrid (rules + ML refinement)

**2. Storage Backend**
- [ ] SQLite for all (simple, unified)
- [ ] Separate backends by materiality (optimized)
- [ ] In-memory for M0/M1, persistent for M2/M3

**3. Pruning Strategy**
- [ ] Eager pruning (immediate deletion)
- [ ] Lazy pruning (mark for deletion, clean up later)
- [ ] Configurable per-user

**4. Integration Depth**
- [ ] Retrofit existing code (minimal changes)
- [ ] Deep integration (refactor for E/N/M)
- [ ] Parallel system (gradual migration)

---

## 📖 References

- Week 1-2: Identity & DIDs (foundation)
- Week 3-4: MATL Trust Scoring (behavioral analysis)
- LAYER_7_PHASE_1_IMPLEMENTATION.md (overall plan)
- THE_COMPLETE_10_LAYER_VISION.md (architectural context)

---

**Created**: December 4, 2025
**Status**: PLANNING - Ready for Review
**Next**: Clarify specification, then begin implementation

*"From raw data to classified knowledge - consciousness emerges through epistemic rigor!"*

---

## ❓ Questions for User/Architect

1. **Do we have a detailed E/N/M specification document?** If so, where can I find it?

2. **What are the precise criteria** for scoring each dimension (E/N/M)?

3. **How should multi-dimensional content be handled?** (e.g., something that's both highly epistemic AND highly normative)

4. **What are the exact materiality thresholds?** (What makes something M0 vs M1 vs M2 vs M3?)

5. **Should this be ML-based or rule-based?** Or hybrid?

6. **Where should M2/M3 data actually be stored?** (Database location, format, etc.)

7. **Are there existing examples** of E/N/M classification we should follow?

8. **Performance requirements?** (Max latency for classification, pruning frequency, etc.)

9. **Should we proceed with a simple rule-based implementation first** and iterate, or wait for full specification?

10. **Is there existing Mycelix Protocol documentation** that defines this system in detail?

---

**Status**: Awaiting clarification before implementation begins 🎯
