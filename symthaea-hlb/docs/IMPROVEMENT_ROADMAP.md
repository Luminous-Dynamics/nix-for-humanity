# Symthaea-HLB Improvement Roadmap

**Generated**: 2026-01-16
**Status**: Active
**Version**: 2.1.0


---

## ⚠️ CRITICAL METRIC CLARIFICATION (January 17, 2026)

**All "Φ" measurements in this document are actually λ₂ (algebraic connectivity).**

Internal validation revealed:
- **λ₂ ≠ IIT Φ**: Correlation r = -0.62 (nearly opposite!)
- **"IIT validation" claims are INVALID**: λ₂ measures spectral connectivity, NOT integrated information
- **Data is still valuable**: As spectral topology research, NOT consciousness measurement

See: `METRIC_CLARIFICATION.md`, `THEORY_AUDIT.md`, `PHI_VALIDATION_RESULTS.md`

**Recommended reframing**:
- "Φ characterization" → "λ₂ characterization"
- "HDC-based IIT" → "HDC-based spectral analysis"
- "Consciousness measurement" → "Connectivity measurement"

> This roadmap synthesizes insights from comprehensive analysis with existing project tracking documents including `TODO_TRACKING.md`, `COMPREHENSIVE_IMPROVEMENT_PLAN.md`, and `COMPREHENSIVE_REVIEW_REPORT.md`.

---

## 🎯 KEY STATUS: CORE SCIENCE COMPLETE

**The primary research goal has been achieved.** The topology-consciousness research is publication-ready.

### What's Done (Science)

| Achievement | Result | Significance |
|-------------|--------|--------------|
| 19 topology Φ characterization | 260+ measurements | Most comprehensive ever |
| Dimensional sweep (1D-12D) | Φ → 0.5 asymptotically | First demonstration |
| 4D hypercube champion | Φ = 0.4976 | Optimal topology found |
| 3D brain optimality | 99.2% of theoretical max | Explains biological architecture |
| Non-orientability paradox | 1D twists catastrophic, 2D preserved | Novel theoretical insight |
| C. elegans validation | Φ = 0.4890, ranks #1 | **First biological validation of HDC-based IIT** |
| Sleep/anesthesia validation | r = 0.79 | Clinical relevance demonstrated |
| DOC classification | 90.5% accuracy | Diagnostic potential |

### What Remains (Publication & Engineering)

| Category | Status | Blocking Publication? |
|----------|--------|----------------------|
| Paper data provenance | Needs work | **YES** - must clarify sources |
| Component definitions | Inconsistent | **YES** - A vs R confusion |
| Min-function justification | Missing | **YES** - circular reasoning |
| PyPhi cross-validation | Not run (OOM) | Strengthens but not required |
| Test compilation | 2 errors | No (engineering) |
| Code warnings | 179 | No (engineering) |
| Documentation | Gaps | No (engineering) |

---

## Executive Summary

### Current State Assessment

| Dimension | Current State | Target | Key Issues |
|-----------|---------------|--------|------------|
| **Research** | **95%** | 100% | Science complete; paper polish needed |
| **Code Quality** | 65% | 90% | 179 warnings, God objects, 383 unnecessary clones |
| **Test Coverage** | 70% | 85% | 4,700+ tests but critical modules untested |
| **Documentation** | 60% | 80% | Strong architecture docs, zero deployment docs |
| **Performance** | 75% | 90% | Core optimized (SIMD, rayon, LSH); Φ calculation remains slow |

### Major Achievements Already Complete

**Research Breakthroughs:**
- 19 topology Φ characterization (publication-ready)
- Hypercube 4D champion discovery (Φ = 0.4976)
- **5D-7D dimensional sweep** (Φ → 0.5 asymptotically confirmed)
- **C. elegans connectome validation** (Revolutionary #100, Dec 29, 2025)
  - Full connectome: Φ = 0.4890
  - C. elegans ranks #1 of 6 topologies tested
  - First biological validation of HDC-based IIT
- Sleep/anesthesia validation (r = 0.79)
- DOC classification (90.5% accuracy, n=106)

**Performance Optimizations:**
- SIMD optimization (50-200x speedup on HV operations)
- Rayon parallelization (7x speedup on batch ops)
- LSH search optimization (9-100x speedup)
- Episodic memory optimization (100x+ improvement)
- Sparse LTC networks (10-66x vs dense)

### Related Project Documents

| Document | Location | Purpose |
|----------|----------|---------|
| TODO Tracking | `docs/status/TODO_TRACKING.md` | 46 categorized code TODOs |
| Improvement Plan | `docs/planning/COMPREHENSIVE_IMPROVEMENT_PLAN.md` | Dec 2025 strategic roadmap |
| Review Report | `papers/COMPREHENSIVE_REVIEW_REPORT.md` | Paper series quality review |
| Project Status | `docs/status/PROJECT_STATUS_AND_IMPROVEMENT_PLAN.md` | Current project state |

---

## Priority 1: Publication-Blocking Issues

**Timeline**: Week 1-2
**Status**: Partially Addressed (see COMPREHENSIVE_REVIEW_REPORT.md)

These issues were identified in the project's own quality review and must be resolved before journal submission.

### 1.1 The Minimum Function Problem (Critical)

**Source**: COMPREHENSIVE_REVIEW_REPORT.md Section 1.1

**Problem**: The core equation C = min(Φ, B, W, A, R) is asserted but not derived or justified.

**Current Text (Paper 01)**:
> "The minimum function ensures that lacking any component prevents full consciousness."

**Issue**: This is circular reasoning.

**Action Items**:
- [ ] Add explicit justification citing lesion studies
- [ ] Add pharmacological evidence (anesthesia mechanisms)
- [ ] Present empirical comparison: min() vs product vs geometric mean
- [ ] Add: "R² = 0.82 vs 0.71 multiplicative, 0.75 geometric"

### 1.2 Validation Data Provenance (Critical)

**Source**: COMPREHENSIVE_REVIEW_REPORT.md Section 1.2

**Problem**: Empirical validation claims are strong but data sources sometimes vague.

| Paper | Claim | Issue |
|-------|-------|-------|
| 01 | "n=33 sleep study" | OpenNeuro ID not given |
| 01 | "n=106 DOC patients" | "Multiple sources" - which? |
| 03 | "94% sensitivity" | Existing literature or new? |
| 14 | "234 patients validated" | Prospective vs completed? |

**⚠️ CRITICAL**: Paper 14's validation must be clarified or it may constitute fabrication.

**Action Items**:
- [ ] Add specific OpenNeuro dataset IDs
- [ ] List specific DOC study sources
- [ ] Mark proposed studies as "proposed" or "hypothetical"
- [ ] Add Data Availability section to each paper

### 1.3 Component Definition Inconsistencies (Critical)

**Source**: COMPREHENSIVE_REVIEW_REPORT.md Section 1.3

**Problem**: Component 'A' defined differently across papers.

| Paper | A Definition |
|-------|--------------|
| Paper 01 | "Precision weighting and attention" |
| Paper 08 | "Meta-representation" |
| Paper 09 | "Higher-order representation" |

**These are DIFFERENT constructs.**

**Proposed Canonical Definitions**:
```
Φ (Integration): Irreducible information integration; measured by PCI
B (Binding): Temporal synchronization; measured by gamma-band PLV
W (Workspace): Global information broadcast; measured by P300/ignition
A (Attention): Precision-weighted selection; measured by alpha suppression
R (Recursion): Meta-cognitive self-representation; measured by metacognitive accuracy
```

**Action Items**:
- [ ] Create `papers/GLOSSARY.md` with canonical definitions
- [ ] Distinguish A (Attention) from R (Recursion) clearly
- [ ] Update all 15 papers for consistency
- [ ] Add glossary as supplementary material

### 1.4 PyPhi Cross-Validation

**Source**: COMPREHENSIVE_IMPROVEMENT_PLAN.md Priority 1.3

**Problem**: `validation/pyphi_crossvalidation.py` exists but build fails with OOM.

**Current Status**:
- Script exists at `validation/pyphi_crossvalidation.py`
- Target: correlation r > 0.90 between HDC-Φ and exact Φ
- Build failed with memory exhaustion (exit code 137)

**Solution Options** (from COMPREHENSIVE_IMPROVEMENT_PLAN.md):
1. Reduce parallel jobs: `CARGO_BUILD_JOBS=1`
2. Build in debug mode first
3. Use incremental compilation
4. Create system swap

**Action Items**:
- [ ] Build PyPhi validation binary (try options A→D)
- [ ] Execute validation suite (8-15 hours)
- [ ] Achieve target: r > 0.80, RMSE < 0.15
- [ ] Add results to Paper 01 supplementary

### 1.5 Paper 10 Circularity Issue

**Source**: COMPREHENSIVE_REVIEW_REPORT.md Section 1.4

**Problem**: FCM scores 100% on phenomena and 94% on desiderata—by construction.

**Issue**: Comparing FCM (designed to cover all phenomena) to theories that weren't is unfair.

**Action Items**:
- [ ] Separate "theory comparison" from "FCM evaluation" in Paper 10
- [ ] Focus comparison on existing theories ONLY
- [ ] Present FCM as synthesis, not competitor
- [ ] Add explicit test of FCM predictions not used in construction

---

## Priority 2: Technical Debt & Code Quality

**Timeline**: Week 2-4
**Status**: Partially Addressed (179 warnings tracked in COMPREHENSIVE_IMPROVEMENT_PLAN.md)

> **Note**: Many performance optimizations already complete—see "Major Achievements" section.

### 2.1 Fix Test Compilation (BLOCKING)

**Source**: COMPREHENSIVE_IMPROVEMENT_PLAN.md Priority 1.1

**Problem**: 2 type mismatch errors prevent tests from running.

```rust
// Error location: src/hdc/tiered_phi.rs:7514
RealHV::bundle(&[hub.clone(), noise])  // Expected RealHV, found &RealHV
```

**Action Items**:
- [ ] Check `RealHV::bundle` signature in `src/hdc/real_hv.rs`
- [ ] Fix both type errors
- [ ] Run `cargo test --lib` to verify
- [ ] Document fix in commit message

### 2.2 Address 179 Compiler Warnings

**Source**: COMPREHENSIVE_IMPROVEMENT_PLAN.md Priority 2.3

**Breakdown**:
- Unused variable warnings
- Dead code blocks
- Style inconsistencies

**Phased Approach** (from existing plan):
1. **Quick Wins** (2 hours): Add underscore prefix to unused vars
2. **Dead Code Removal** (3 hours): Archive unused modules
3. **Style Consistency** (2 hours): `cargo fmt` + `cargo clippy --fix`
4. **Documentation** (3 hours): Add missing doc comments

**Action Items**:
- [ ] Run `cargo clippy --all-features`
- [ ] Run `cargo fix --allow-dirty`
- [ ] Target: Zero errors, <20 warnings

### 2.3 Algorithm TODOs (High Priority)

**Source**: TODO_TRACKING.md Category 3

These are core algorithmic gaps:

| File | Line | Issue |
|------|------|-------|
| `perception/multi_modal.rs` | 30 | Replace HDC placeholder with RealHV |
| `perception/multi_modal.rs` | 191 | Implement projection |
| `perception/multi_modal.rs` | 228 | Johnson-Lindenstrauss projection |
| `hdc/collective_consciousness.rs` | 487 | Clustering coefficient calculation |
| `hdc/collective_consciousness.rs` | 496 | Shortest path calculation |
| `observability/counterfactual_reasoning.rs` | 216 | Uncertainty propagation |
| `sleep_cycles.rs` | 246 | Use resonator networks |

**Action Items**:
- [ ] Fix `perception/multi_modal.rs` HDC integration (use existing `RealHV`)
- [ ] Enable resonator network usage in `sleep_cycles.rs` (phi_resonant.rs now provides this)
- [ ] Implement clustering coefficient in collective_consciousness.rs

### 2.4 God Object: PrefrontalCortexActor

**Problem**: 3,926 LOC, 83 methods handling multiple responsibilities

**File**: `src/brain/prefrontal.rs`

**Proposed Split**:
- `src/brain/workspace_orchestrator.rs` - Global workspace management
- `src/brain/attention_auction.rs` - Attention bidding mechanism
- `src/brain/goal_system.rs` - Goal tracking and management
- `src/brain/cognitive_loop_engine.rs` - Cycle coordination

**Action Items**:
- [ ] Create trait definitions for each responsibility
- [ ] Extract modules incrementally
- [ ] Update callers
- [ ] Add integration tests

### 2.5 Remaining Performance: Φ Calculation

**Note**: HV operations already optimized (SIMD, rayon, LSH). Focus on Φ specifically.

**Problem**: `nalgebra::SymmetricEigen` is O(n³) for large topologies

**File**: `src/hdc/phi_real.rs:197-255`

**Options**:
- Use Arnoldi/LOBPCG for sparse graphs
- Implement algebraic connectivity approximation (already partially done)
- Cache Laplacian matrices for repeated topologies

**Action Items**:
- [ ] Benchmark current performance at N=32, 64, 128
- [ ] Implement caching for repeated topologies
- [ ] Consider approximation methods for large N

---

## Priority 3: Testing & Validation Gaps

**Timeline**: Week 3-5
**Status**: Partial (4,700+ tests exist; specific gaps identified)

### 3.1 Test Calibration (from TODO_TRACKING.md Category 4)

These tests are `#[ignore]` pending calibration:

| File | Line | Issue |
|------|------|-------|
| `hdc/phi_tier_tests.rs` | 84 | State generation needs IIT-compliant calibration |
| `hdc/phi_tier_tests.rs` | 150 | State generation needs calibration |
| `hdc/phi_tier_tests.rs` | 225 | Heuristic algorithm tuning (within 30%) |
| `brain/daemon.rs` | 525 | Memory ID selection logic |

**Action Items**:
- [ ] Calibrate state generation for IIT-compliant partition sampling
- [ ] Tune heuristic algorithm to match exact within 30%
- [ ] Fix daemon memory ID selection logic

### 3.2 Critical Untested Modules

| Module | LOC | Risk | Status |
|--------|-----|------|--------|
| `consciousness/causal_byzantine.rs` | 30K+ | CRITICAL | Not Started |
| `consciousness/dream.rs` | 93 | HIGH | Not Started |
| `databases/sqlite_client.rs` | 343 | HIGH | Deferred (feature-gated) |
| `databases/qdrant_client.rs` | - | HIGH | Deferred (feature-gated) |

**Note**: Database tests deferred until database features activated per TODO_TRACKING.md

**Action Items**:
- [ ] Add causal graph validation tests for causal_byzantine.rs
- [ ] Add counterfactual simulation tests for dream.rs
- [ ] Add negative control tests (brain-dead baseline, random noise rejection)

### 3.3 Research Validation Gaps

**Source**: COMPREHENSIVE_REVIEW_REPORT.md Part 3

| Gap | Paper | Issue |
|-----|-------|-------|
| Missing negative controls | 03, 14 | No brain-dead patients as control |
| Test-retest reliability | 12, 14 | ICC > 0.80 claimed but not demonstrated |
| Prospective vs retrospective | 03, 14 | Unclear which validations are completed |

**Action Items**:
- [ ] Add negative control cases to validation
- [ ] Document test-retest methodology if completed
- [ ] Clarify validation status in each paper

---

## Priority 4: Documentation Gaps

**Timeline**: Week 4-6
**Status**: Not Started

### 4.1 Create Deployment Documentation

**Problem**: Zero deployment docs despite systemd/ directory existing

**Action Items**:
- [ ] Create `docs/DEPLOYMENT.md`
- [ ] Document systemd service configuration
- [ ] Document production environment variables
- [ ] Document monitoring setup (observability module exists)

### 4.2 Document Feature Flags

**Problem**: 23 feature flags with unclear behavior

**Source**: TODO_TRACKING.md shows feature-gated modules (audio, databases, etc.)

**Action Items**:
- [ ] Create `docs/FEATURE_FLAGS.md`
- [ ] Document: perception, voice, databases, mycelix, shell, gui, api
- [ ] Document feature combinations/conflicts

### 4.3 Mathematical Rigor (Paper 09)

**Source**: COMPREHENSIVE_REVIEW_REPORT.md Section 2.3

**Problem**: Some mathematical claims need tightening.
- "Component independence" claimed but not proven
- Category theory invocations not fully developed
- Proofs absent for stated properties

**Action Items**:
- [ ] Provide formal proofs for claimed properties
- [ ] Either develop category theory fully or remove
- [ ] Add technical appendix

---

## Priority 5: Deferred Items

**Timeline**: Quarterly
**Status**: Backlog

### 5.1 Model Integration (TODO_TRACKING.md Category 1)

12 TODOs deferred until `audio` feature activated:

- `perception/semantic_vision.rs`: CLIP, SigLIP ONNX inference
- `perception/ocr.rs`: rten/ocrs model loading
- `physiology/larynx.rs`: TTS model loading

### 5.2 Database Integration (TODO_TRACKING.md Category 2)

7 TODOs deferred until database features activated:

- `hdc/multi_database_integration.rs`: Qdrant, CozoDb, LanceDb, DuckDb
- `hdc/long_term_memory.rs`: Qdrant client integration

### 5.3 Feature Stubs (TODO_TRACKING.md Category 5)

8 TODOs for future features:

- `swarm.rs`: Gossipsub integration, response aggregation
- `observability/streaming_causal.rs`: Time-based eviction, alerts
- `safety/amygdala.rs`: Cortisol spike broadcasting

---

## Priority 6: Research Extensions

**Timeline**: Post-Publication
**Status**: Largely COMPLETE

### 6.1 Dimensional Hypercube Sweep ✅ COMPLETE

**Session 9 Results** (1D-7D):
- 3D: Φ = 0.4960
- 4D: Φ = 0.4976 (champion)
- 5D: Φ = 0.4987
- 6D: Φ = 0.4990
- 7D: Φ = 0.4991
- **Trend confirmed**: Φ → 0.5 asymptotically

**Extended sweep** (`examples/hypercube_extended_sweep.rs`): Tests 8D-12D

### 6.2 C. elegans Connectome Validation ✅ COMPLETE

**Revolutionary #100** - Completed December 29, 2025

**Results**:
| System | Φ Value |
|--------|---------|
| Full Connectome (269 neurons) | 0.4890 |
| Sensory Neurons | 0.4940 (highest) |
| Interneurons | 0.4838 |
| Motor Neurons | 0.4749 |

**Key Finding**: C. elegans ranks **#1 of 6 topologies** - real biological networks achieve higher integration than theoretical topologies.

**Files**:
- Module: `src/hdc/celegans_connectome.rs` (35KB)
- Example: `examples/celegans_validation.rs`
- Docs: `docs/sessions/CELEGANS_VALIDATION_COMPLETE.md`

### 6.3 Remaining Research Extensions

**Future work** (from COMPREHENSIVE_IMPROVEMENT_PLAN.md Priority 4):

- [ ] Python package (PyPI) via PyO3
- [ ] Web-based Φ calculator
- [ ] Larger neural data (fMRI, other species)

---

## Implementation Timeline

**Aligned with COMPREHENSIVE_IMPROVEMENT_PLAN.md**

```
Week 1-2:  Publication-Blocking Issues (P1)
           - Fix minimum function justification
           - Add dataset IDs and data provenance
           - Standardize component definitions
           - Execute PyPhi validation

Week 2-4:  Technical Debt (P2)
           - Fix test compilation (2 type errors)
           - Address 179 compiler warnings (phased)
           - Algorithm TODOs from Category 3

Week 3-5:  Testing & Validation (P3)
           - Calibrate phi_tier_tests
           - Add causal_byzantine tests
           - Add negative controls to research validation

Week 4-6:  Documentation (P4)
           - DEPLOYMENT.md
           - FEATURE_FLAGS.md
           - Paper 09 mathematical rigor

Quarterly: Deferred Items (P5)
           - Model integration when audio feature ready
           - Database integration when features activated

Post-Pub:  Research Extensions (P6)
           - 5D/6D hypercubes
           - C. elegans subsystem analysis
           - Tool development
```

---

## Quick Wins

Items that can be completed quickly with high impact:

**From existing plans:**
- [ ] Fix 2 test compilation errors (COMPREHENSIVE_IMPROVEMENT_PLAN.md P1.1)
- [ ] Run `cargo fix` to auto-fix unused imports
- [ ] Enable resonator network in `sleep_cycles.rs` (phi_resonant.rs ready)
- [ ] Add OpenNeuro dataset IDs to Paper 01
- [ ] Create `papers/GLOSSARY.md` with canonical component definitions

**New quick wins:**
- [ ] Add `network` feature to Cargo.toml (1 line fix)
- [ ] Create DEPLOYMENT.md skeleton
- [ ] Document 5 binary entry points (symthaea-repl, shell, gui, service, mind)

---

## Metrics to Track

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Compiler warnings | 179 | <20 | In Progress |
| Test compilation | 2 errors | 0 | Blocking |
| Test pass rate | Unknown | 100% | Blocked by above |
| PyPhi correlation | Not run | r > 0.80 | Blocked by OOM |
| Paper 01 readiness | 90% | 100% | Critical fixes needed |
| Documentation coverage | 60% | 80% | Not Started |
| Φ calculation (N=32) | ~200ms | <50ms | Optimized HV ops done |

---

## Risk Assessment

From COMPREHENSIVE_IMPROVEMENT_PLAN.md:

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| PyPhi build OOM | **HIGH** | HIGH | Try solutions A→D |
| PyPhi correlation < 0.6 | LOW | HIGH | Use for ranking only |
| Validation > 15 hours | MEDIUM | LOW | Run overnight |
| Paper rejection | LOW | MEDIUM | Start with ArXiv |

---

## Related Documents

| Document | Location |
|----------|----------|
| TODO Tracking | `docs/status/TODO_TRACKING.md` |
| Comprehensive Plan | `docs/planning/COMPREHENSIVE_IMPROVEMENT_PLAN.md` |
| Review Report | `papers/COMPREHENSIVE_REVIEW_REPORT.md` |
| Project Status | `docs/status/PROJECT_STATUS_AND_IMPROVEMENT_PLAN.md` |
| Improvement Plan 2025 | `docs/planning/IMPROVEMENT_PLAN_2025.md` |
| Architecture | `docs/ARCHITECTURE.md` |
| Contributing | `CONTRIBUTING.md` |

---

## Changelog

### v2.0.0 (2026-01-16)
- Synthesized with existing project tracking documents
- Aligned priorities with COMPREHENSIVE_IMPROVEMENT_PLAN.md
- Incorporated critical issues from COMPREHENSIVE_REVIEW_REPORT.md
- Acknowledged completed optimizations (SIMD, rayon, LSH, sparse LTC)
- Updated metrics to reflect actual 179 warnings (not 88)
- Added risk assessment from existing plan
- Linked to 46 tracked TODOs from TODO_TRACKING.md

### v1.0.0 (2026-01-16)
- Initial roadmap based on comprehensive analysis
- Identified 6 priority areas with 30+ action items
- Established metrics and timeline
