# 🎯 Week 3-4 Implementation Plan: MATL Trust Scoring

**Date**: December 3, 2025 - December 17, 2025
**Component**: MATL Trust Scoring Engine
**Status**: Starting (Week 2 complete: 47/47 tests ✅)

---

## 🚀 What We're Building

**MATL = Multi-Actor Trust Ledger**

A trust scoring system that calculates user trustworthiness based on:
1. **PoGQ** (Proof of Genuine Query) - Are queries genuine or bot-like?
2. **TCDM** (Temporal Consistency) - Are interaction patterns consistent?
3. **Entropy** (Diversity) - Is the user exploring and learning?

**Composite Score** = weighted combination of all three components

---

## 📋 Component Breakdown

### **Component 1: PoGQ (Proof of Genuine Query)** - Days 1-3

**What it measures**: Authenticity of user queries
- Query complexity and diversity
- Semantic coherence
- Human-like patterns vs bot patterns

**Score Range**: 0.0-1.0 (higher = more genuine)

**Indicators of Genuine Queries**:
- Varied vocabulary (not repetitive)
- Contextually relevant (makes sense)
- Progressive complexity (learning over time)
- Natural typos and corrections

**Indicators of Bot-like Queries**:
- Repetitive patterns
- Random/nonsensical
- No learning progression
- Perfect spelling (ironically suspicious)

**Implementation**:
```python
class PoGQCalculator:
    def calculate(self, interactions: List[Interaction]) -> float:
        # Calculate query diversity
        # Calculate semantic coherence
        # Calculate progression patterns
        # Return composite score 0.0-1.0
```

---

### **Component 2: TCDM (Temporal Consistency)** - Days 4-6

**What it measures**: Consistency of interaction timing
- Inter-arrival time patterns
- Session consistency
- Natural human rhythms

**Score Range**: 0.0-1.0 (higher = more consistent)

**Indicators of Good Consistency**:
- Regular usage patterns
- Human-like session durations
- Natural breaks between sessions
- Circadian rhythm alignment

**Indicators of Poor Consistency**:
- Erratic timing (bot-like)
- Impossible speeds (too fast)
- No pattern recognition
- 24/7 activity (no sleep)

**Implementation**:
```python
class TCDMCalculator:
    def calculate(self, interactions: List[Interaction]) -> float:
        # Calculate inter-arrival times
        # Detect session patterns
        # Check circadian alignment
        # Return composite score 0.0-1.0
```

---

### **Component 3: Entropy (Diversity)** - Days 7-9

**What it measures**: Exploration and learning behavior
- Query topic diversity
- Package exploration breadth
- Learning progression
- Curiosity indicators

**Score Range**: 0.0-1.0 (higher = more diverse/curious)

**Indicators of Good Entropy**:
- Wide range of queries
- Multiple package categories
- Progressive learning
- Healthy exploration

**Indicators of Low Entropy**:
- Repetitive queries
- Single-focus (suspicious)
- No learning progression
- Narrow interests

**Implementation**:
```python
class EntropyCalculator:
    def calculate(self, interactions: List[Interaction]) -> float:
        # Calculate query diversity
        # Measure topic breadth
        # Detect learning progression
        # Return composite score 0.0-1.0
```

---

### **Component 4: MATL Engine (Integration)** - Days 10-14

**What it does**: Combines all components into final trust score

**Weighted Combination**:
```
MATL_Score = (
    w_pogq * PoGQ +
    w_tcdm * TCDM +
    w_entropy * Entropy
)

Default weights:
- PoGQ: 0.4 (most important - genuine queries)
- TCDM: 0.3 (consistency matters)
- Entropy: 0.3 (learning is good)
```

**Implementation**:
```python
class MATLEngine:
    def __init__(self):
        self.pogq_calc = PoGQCalculator()
        self.tcdm_calc = TCDMCalculator()
        self.entropy_calc = EntropyCalculator()

    def calculate_trust_score(
        self,
        interactions: List[Interaction]
    ) -> MATLScore:
        # Calculate each component
        pogq = self.pogq_calc.calculate(interactions)
        tcdm = self.tcdm_calc.calculate(interactions)
        entropy = self.entropy_calc.calculate(interactions)

        # Weighted combination
        total = 0.4*pogq + 0.3*tcdm + 0.3*entropy

        return MATLScore(
            total_score=total,
            pogq_score=pogq,
            tcdm_score=tcdm,
            entropy_score=entropy,
            interactions_count=len(interactions),
            ...
        )
```

---

## 📁 File Structure

```
src/luminous_nix/mycelix/trust/
├── __init__.py              # Existing
├── matl_types.py            # Existing (Week 2)
├── interaction_logger.py    # Existing (Week 2)
├── pogq.py                  # 🆕 PoGQ calculator
├── tcdm.py                  # 🆕 TCDM calculator
├── entropy.py               # 🆕 Entropy calculator
└── matl_engine.py          # 🆕 Complete MATL engine

tests/mycelix/
├── test_identity.py         # Existing (Week 1)
├── test_matl_types.py       # Existing (Week 2)
├── test_interaction_logger.py  # Existing (Week 2)
├── test_pogq.py             # 🆕 PoGQ tests
├── test_tcdm.py             # 🆕 TCDM tests
├── test_entropy.py          # 🆕 Entropy tests
└── test_matl_engine.py     # 🆕 Integration tests
```

---

## 🎯 Success Criteria

### Functional
- [ ] PoGQ calculator working (0.0-1.0 scores)
- [ ] TCDM calculator working (0.0-1.0 scores)
- [ ] Entropy calculator working (0.0-1.0 scores)
- [ ] MATL engine combines components
- [ ] Integration with User Profile
- [ ] Scores update automatically

### Technical
- [ ] All tests passing (target: 60+ total)
- [ ] Scores are deterministic (same input = same output)
- [ ] Performance: <100ms for typical user history
- [ ] Memory efficient (streaming calculations)

### User Experience
- [ ] Trust scores visible in `whoami`
- [ ] Score breakdown available
- [ ] Clear explanations of scores
- [ ] Privacy-preserving (local only)

---

## 📊 Test Plan

### Unit Tests (per component)
- **PoGQ**: 4-5 tests
- **TCDM**: 4-5 tests
- **Entropy**: 4-5 tests
- **MATL Engine**: 5-6 tests

**Target**: +15-20 tests = **62-67 total**

### Integration Tests
- End-to-end trust scoring
- Profile integration
- Multiple users
- Edge cases (no interactions, single interaction)

---

## 📅 Day-by-Day Plan

### **Days 1-3 (Dec 4-6): PoGQ Calculator**

**Day 1**: Design + Core Implementation
- Design PoGQ algorithm
- Implement query diversity measurement
- Implement basic scoring

**Day 2**: Advanced Features
- Semantic coherence checking
- Learning progression detection
- Bot pattern detection

**Day 3**: Testing + Polish
- Write comprehensive tests (4-5 tests)
- Edge case handling
- Performance optimization

---

### **Days 4-6 (Dec 7-9): TCDM Calculator**

**Day 4**: Design + Core Implementation
- Design TCDM algorithm
- Calculate inter-arrival times
- Basic consistency scoring

**Day 5**: Pattern Detection
- Session detection
- Circadian rhythm analysis
- Anomaly detection

**Day 6**: Testing + Polish
- Write comprehensive tests (4-5 tests)
- Edge cases
- Performance

---

### **Days 7-9 (Dec 10-12): Entropy Calculator**

**Day 7**: Design + Core Implementation
- Design Entropy algorithm
- Topic diversity measurement
- Basic scoring

**Day 8**: Learning Detection
- Learning progression analysis
- Curiosity indicators
- Exploration patterns

**Day 9**: Testing + Polish
- Write comprehensive tests (4-5 tests)
- Edge cases
- Performance

---

### **Days 10-14 (Dec 13-17): MATL Engine + Integration**

**Day 10-11**: MATL Engine
- Combine all components
- Weighted scoring
- Component weights tuning

**Day 12**: User Profile Integration
- Update profile manager
- Automatic score updates
- Score persistence

**Day 13**: CLI Integration
- Display trust scores in `whoami`
- Add score breakdown command
- Beautiful formatting

**Day 14**: Final Testing + Polish
- Integration tests (5-6 tests)
- End-to-end testing
- Documentation
- Week 3-4 completion report

---

## 💡 Implementation Strategy

### Start Simple (Phase 1)
**PoGQ**: Simple diversity score (unique queries / total queries)
**TCDM**: Simple consistency (std dev of inter-arrival times)
**Entropy**: Simple diversity (unique packages / total packages)

**Goal**: Get something working quickly

### Add Sophistication (Phase 2)
**PoGQ**: Add semantic analysis, learning detection
**TCDM**: Add session detection, circadian analysis
**Entropy**: Add topic categorization, curiosity metrics

**Goal**: Improve accuracy

### Optimize (Phase 3)
- Performance tuning
- Memory optimization
- Edge case handling

**Goal**: Production-ready

---

## 🔮 What This Enables (Week 5+)

### **Week 5-6: Epistemic Classification**
With trust scores:
- Weight claims by user trust
- Adjust E/N/M based on trust
- Trust-based pruning

### **Week 7-8: Credits System**
With trust scores:
- Trust-based credit allocation
- Anti-sybil mechanisms
- Reputation economics

### **Week 9-12: Advanced Features**
With complete trust system:
- Cross-device reputation
- Community trust networks
- Collective intelligence

---

## 📈 Progress Tracking

| Day | Component | Status | Tests |
|-----|-----------|--------|-------|
| 1-3 | PoGQ Calculator | 🔄 Pending | 0/5 |
| 4-6 | TCDM Calculator | 🔄 Pending | 0/5 |
| 7-9 | Entropy Calculator | 🔄 Pending | 0/5 |
| 10-14 | MATL Engine + Integration | 🔄 Pending | 0/6 |
| **Total** | **Week 3-4** | **🔄 Starting** | **0/21** |

**Current**: 47/47 tests passing (Week 1-2)
**Target**: 60+ tests passing (Week 1-4)

---

## 🌟 Key Principles

### 1. Privacy First
- All calculations local only
- No data sent to servers
- User controls their data

### 2. Transparency
- Scores are explainable
- Components visible
- No black boxes

### 3. Fairness
- No bias against new users
- Progressive trust building
- Second chances

### 4. Security
- Bot detection
- Sybil resistance
- Cartel detection (basic)

---

*"From identity (Week 1-2) to intelligence (Week 3-4) - consciousness-first computing evolves!"*

**Week 3-4 Status**: READY TO START 🚀
**Foundation**: Week 1-2 complete (47/47 tests ✅)
**Target**: +15-20 tests = 60+ total
**Timeline**: 14 days (Dec 4-17, 2025)

🌊 From tracking to trusting - let's FLOW! ✨
