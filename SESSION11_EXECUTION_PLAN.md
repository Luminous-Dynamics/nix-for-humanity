# Session 11 Execution Plan - Target: 70% Pass Rate

**Created**: 2025-11-16
**Goal**: Cross 70% pass rate threshold (307/438 tests)
**Current**: 65.3% (286/438 tests)
**Gap**: +21 tests needed
**Primary Target**: test_native_nix_backend.py (11 failing tests)
**Strategy**: Fix API mismatches and compatibility issues

---

## 📊 Current Status

```
Total Tests: 677
├── Runnable: 438 (64.7%)
│   ├── Passing: 286 (65.3%) ← Session 10 end
│   ├── Failing: 152 (34.7%)
│   └── Errors: 3 (0.7%)
└── Skipped: 236 (34.9%)

Target for 70%: 307 passing tests (+21 tests)
```

### test_native_nix_backend.py Analysis
```
Total Tests: 27
├── Passing: 16 (59.3%)
└── Failing: 11 (40.7%)

Failure Breakdown:
1. TestNativeNixBackend (7 failures)
   - Compatibility check issues (setUp fails)
   - Old API expectations (OperationType, NixOperation)

2. TestPerformanceFeatures (1 failure)
   - Progress callback compatibility

3. TestDataIntegrity (3 failures)
   - Validation tests expecting old API
```

---

## 🎯 Session 11 Goals

### Primary Goal
✅ **Fix all 11 test_native_nix_backend.py failures** → reach 297/438 (67.8%)

### Stretch Goal
✅ **Find +10 more quick wins** → reach 307/438 (70%+) 🎯

### Success Criteria
- All test_native_nix_backend.py tests passing
- Pass rate ≥ 70% (307/438 tests)
- Clean commits with comprehensive documentation
- No regressions in previously passing tests

---

## 🔍 Root Cause Analysis

### Issue 1: Compatibility Check Blocking Tests
**Problem**: `NativeNixBackend()` constructor calls `_check_compatibility()` which raises `RuntimeError` on NixOS 24.4

**Error**:
```python
RuntimeError: NixOS 24.4 does not support native API.
Upgrade to 25.11+ or set NIX_HUMANITY_FORCE_NATIVE_API=true
```

**Impact**: All tests in `TestNativeNixBackend` fail in setUp (7 tests)

**Solution**: Mock the compatibility check in test setUp

---

### Issue 2: Old API Expectations
**Problem**: Tests expect old API that was refactored

**Tests Expect** (OLD):
```python
from luminous_nix.core.native_operations import (
    OperationType,  # ← Doesn't exist!
    NixOperation,   # ← Doesn't exist!
    NixResult,      # ← Doesn't exist!
)

# Test expects:
OperationType.UPDATE    # ← Changed to SWITCH
OperationType.INSTALL   # ← Changed to BUILD
OperationType.REMOVE    # ← Doesn't exist
OperationType.SEARCH    # ← Changed to SEARCH_PACKAGES
```

**Current API** (NEW):
```python
from luminous_nix.core.native_operations import (
    NativeOperationType,  # ← Correct name
    # NixOperation and NixResult likely removed/refactored
)

# Current enum values:
NativeOperationType.SWITCH          # was UPDATE
NativeOperationType.BUILD           # was INSTALL
NativeOperationType.SEARCH_PACKAGES # was SEARCH
NativeOperationType.ROLLBACK        # unchanged
NativeOperationType.LIST_GENERATIONS # unchanged
# No REMOVE - declarative approach
```

**Impact**: 4-7 tests expecting old enum values

**Solution**: Update tests to use current API

---

## 📋 Execution Phases

### Phase 0: Investigation & Planning ✅
**Objective**: Understand failure patterns and create execution plan
- [x] Analyze test_native_nix_backend.py failures
- [x] Identify root causes
- [x] Create comprehensive execution plan (this document)
**Estimated Time**: 15 minutes
**Status**: COMPLETE

---

### Phase 1: Fix Compatibility Check Issue
**Objective**: Allow tests to instantiate NativeNixBackend without RuntimeError

**Tests to Fix** (7 tests):
1. test_backend_initialization
2. test_check_flakes_detection
3. test_nix_operation_creation
4. test_nix_result_creation
5. test_operation_types_enum
6. test_progress_callback_custom
7. test_progress_callback_default

**Strategy**:
```python
class TestNativeNixBackend(unittest.TestCase):
    def setUp(self):
        # Mock compatibility check
        with patch('luminous_nix.core.native_operations.check_nixos_version',
                   return_value=(True, "25.11")):
            self.backend = NativeNixBackend()
        # OR set environment variable
        # os.environ['NIX_HUMANITY_FORCE_NATIVE_API'] = 'true'
```

**Expected Outcome**: setUp succeeds, revealing actual test failures

**Estimated Time**: 20 minutes

---

### Phase 2: Fix API Enum Expectations
**Objective**: Update tests to use current NativeOperationType values

**Tests to Fix** (~4 tests):
1. test_operation_types_enum - expects UPDATE, INSTALL, REMOVE, SEARCH
2. test_nix_operation_creation - uses OperationType.INSTALL
3. Possibly others uncovered after Phase 1

**Changes Needed**:

1. **Update imports**:
```python
# Before:
from luminous_nix.core.native_operations import (
    OperationType,
    NixOperation,
    NixResult,
)

# After:
from luminous_nix.core.native_operations import (
    NativeOperationType,
    # Check if NixOperation/NixResult still exist or were refactored
)
```

2. **Update enum test**:
```python
# Before:
expected_ops = {"UPDATE", "INSTALL", "REMOVE", "SEARCH",
                "BUILD", "TEST", "LIST_GENERATIONS", "ROLLBACK"}

# After:
expected_ops = {"SWITCH", "BOOT", "TEST", "BUILD", "DRY_BUILD",
                "LIST_GENERATIONS", "ROLLBACK", "SWITCH_GENERATION",
                "DELETE_GENERATIONS", "SEARCH_PACKAGES", ...}
```

3. **Update usage in tests**:
```python
# Before:
op = NixOperation(type=OperationType.INSTALL, ...)

# After:
# Need to check current API - might be:
# - Direct method calls
# - Different dataclass
# - Keyword arguments
```

**Expected Outcome**: Tests use correct enum values and types

**Estimated Time**: 30 minutes

---

### Phase 3: Fix NixOperation/NixResult Usage
**Objective**: Update tests to match current dataclass/method structure

**Investigation Needed**:
- Does `NixOperation` still exist?
- Does `NixResult` still exist?
- Were they replaced with direct method calls?

**Approach**:
1. Check current API in native_operations.py
2. Understand current data structures
3. Update tests accordingly

**Estimated Time**: 25 minutes

---

### Phase 4: Fix Progress Callback Tests
**Objective**: Fix progress callback-related test failures

**Tests to Fix** (3 tests):
1. test_progress_callback_custom (TestNativeNixBackend)
2. test_progress_callback_default (TestNativeNixBackend)
3. test_progress_callback_setting (TestPerformanceFeatures)

**Investigation Needed**:
- Does `ProgressCallback` class still exist?
- Has the progress callback mechanism changed?

**Estimated Time**: 20 minutes

---

### Phase 5: Fix Data Integrity Tests
**Objective**: Fix validation and type safety tests

**Tests to Fix** (3 tests):
1. test_operation_type_validation
2. test_progress_callback_type_safety
3. test_result_data_structure

**Approach**:
- Update to match current API
- Ensure validation still works with new structures

**Estimated Time**: 20 minutes

---

### Phase 6: Verification & Iteration
**Objective**: Ensure all fixes work and no regressions

**Steps**:
1. Run test_native_nix_backend.py in full
2. Verify all 27 tests pass
3. Run full test suite
4. Confirm ≥70% pass rate (307/438 tests)
5. Fix any regressions

**Success Metrics**:
- test_native_nix_backend.py: 27/27 passing ✅
- Total pass rate: ≥70% (≥307/438 tests) 🎯
- No regressions in other files

**Estimated Time**: 15 minutes

---

### Phase 7: Find Additional Quick Wins (if needed)
**Objective**: If still below 70%, find easy wins in other test files

**Strategy**:
1. Run full test suite with detailed output
2. Identify tests with simple, similar failures
3. Group by pattern (e.g., all import errors)
4. Fix in batches

**Target**: +10 tests if needed to reach 307 total

**Estimated Time**: 30 minutes (conditional)

---

### Phase 8: Documentation & Commit
**Objective**: Document progress and commit cleanly

**Deliverables**:
1. SESSION11_SUMMARY.md (comprehensive summary)
2. Clean git commit with detailed message
3. Push to remote branch

**Commit Message Structure**:
```
🎯 Session 11 Complete - 70% Pass Rate ACHIEVED!

[Detailed bullet points of what was fixed]
[Statistics: before/after]
[Files modified]
```

**Estimated Time**: 20 minutes

---

## 📊 Time Estimates

| Phase | Description | Est. Time | Cumulative |
|-------|-------------|-----------|------------|
| 0 | Investigation & Planning | 15 min | 15 min |
| 1 | Fix Compatibility Check | 20 min | 35 min |
| 2 | Fix API Enum Expectations | 30 min | 65 min |
| 3 | Fix NixOperation/NixResult | 25 min | 90 min |
| 4 | Fix Progress Callbacks | 20 min | 110 min |
| 5 | Fix Data Integrity | 20 min | 130 min |
| 6 | Verification & Iteration | 15 min | 145 min |
| 7 | Additional Quick Wins (conditional) | 30 min | 175 min |
| 8 | Documentation & Commit | 20 min | 195 min |

**Total Estimated Time**: 2.0 - 3.25 hours (depending on complexity)

---

## 🎯 Success Metrics

### Must-Have (Required for Success)
✅ All 11 test_native_nix_backend.py failures fixed
✅ test_native_nix_backend.py: 27/27 passing (100%)
✅ Pass rate ≥ 70% (≥307/438 tests)
✅ No regressions in other test files
✅ Clean commits with good messages
✅ Comprehensive SESSION11_SUMMARY.md

### Nice-to-Have (Bonus)
⭐ Pass rate ≥ 72% (>315/438 tests)
⭐ Multiple test files at 100%
⭐ Efficiency ≥ 8 tests/hour

---

## 🚨 Risk Mitigation

### Risk 1: API More Different Than Expected
**Probability**: Medium
**Impact**: High (could add 30-60 minutes)
**Mitigation**: Phase 3 includes thorough API investigation before making changes

### Risk 2: Unforeseen Test Dependencies
**Probability**: Low
**Impact**: Medium (could cascade failures)
**Mitigation**: Run full test suite after each phase to catch regressions early

### Risk 3: Time Overrun
**Probability**: Medium
**Impact**: Low (still make progress, just don't hit 70%)
**Mitigation**: Prioritize high-value fixes first, Phase 7 is conditional

---

## 📝 Notes for Execution

### Best Practices from Session 10
✅ Create todo list at start
✅ Update todo after each phase
✅ Run tests incrementally to verify
✅ Commit with detailed messages
✅ Create comprehensive summary

### Key Learnings to Apply
- Fix tests in logical groups (by failure pattern)
- Verify after each phase to catch regressions
- Don't hesitate to read source code for clarity
- Pattern recognition speeds up similar fixes

---

## 🎊 Expected Outcome

**By End of Session 11**:
- Pass Rate: 65.3% → ≥70%
- Passing Tests: 286 → ≥307 (+21 tests)
- test_native_nix_backend.py: 16/27 → 27/27 (100%)
- Complete Files: 2 (test_nix_integration.py, test_native_nix_backend.py)
- Sessions 7-11 Total: +52 tests fixed over 5 sessions

**Milestone**: 🎯 **70% PASS RATE ACHIEVED!**

---

**Status**: Ready to execute
**Next Step**: Begin Phase 1 - Fix Compatibility Check Issue

*Let's systematically reach 70%!*
