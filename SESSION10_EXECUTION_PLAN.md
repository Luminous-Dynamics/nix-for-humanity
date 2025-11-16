# Session 10 Execution Plan - Cross the 65% Finish Line! 🎯

**Date**: 2025-11-15
**Starting Point**: 62.8% pass rate (275/438 passing tests)
**Goal**: Cross 65% pass rate (285+ passing tests) - **MILESTONE ACHIEVEMENT!**
**Strategy**: Complete test_nix_integration.py + quick wins
**Estimated Duration**: 1.5-2 hours

---

## 🎯 Mission: Reach 65% Pass Rate

**Current State**: 62.8% (275 tests)
**Target**: 65.0% (285 tests)
**Gap**: 10 tests (achievable!)

**Primary Target**: test_nix_integration.py (11 remaining failures)
**Backup Targets**: Quick wins in other files

---

## 📋 Phase-by-Phase Execution Plan

### Phase 1: Fix execute_intent Mock Issues (45 minutes)

**Target**: 5 failing tests
**Root Cause**: Mocks expect old API, backend.execute() not called

**Failing Tests**:
1. test_execute_intent_install_package
2. test_execute_intent_rollback_system
3. test_execute_intent_update_system
4. test_execute_intent_with_error
5. test_execute_intent_with_multiple_packages

**Analysis from Session 9**:
- Tests set up: `self.mock_backend.execute = AsyncMock(...)`
- But code now calls: `execute_native_operation()`
- Assertion fails: `self.mock_backend.execute.call_args[0][0]` is None

**Fix Strategy**:
1. Change mock setup from `execute` to `execute_native_operation`
2. Update mock to accept correct parameters (operation_type, packages, options)
3. Update assertions to check new method call
4. Verify result format matches

**Expected Outcome**: +5 passing tests → 280/438 (63.9%)

---

### Phase 2: Fix get_system_info Enum Issues (30 minutes)

**Target**: 3 failing tests
**Root Cause**: EnumType parameter issue in get_system_info

**Failing Tests**:
1. test_get_system_info_error
2. test_get_system_info_no_current_generation
3. test_get_system_info_success

**Error**: `EnumType.__call__() missing 1 required positional argument: 'value'`

**Analysis**:
Similar to execute_intent issue - likely calling wrong method or wrong parameters

**Fix Strategy**:
1. Check get_system_info implementation
2. Identify where enum is being used incorrectly
3. Fix the call site
4. Update test expectations if needed

**Expected Outcome**: +3 passing tests → 283/438 (64.6%)

---

### Phase 3: Fix Convenience Function Tests (20 minutes)

**Target**: 2 failing tests
**Root Cause**: Compatibility check blocking test initialization

**Failing Tests**:
1. test_error_recovery_workflow
2. test_full_update_workflow

**Error**: `RuntimeError: NixOS 24.4 does not support native API`

**Fix Strategy**:
1. Mock the compatibility check in setUp
2. Or set environment variable: `NIX_HUMANITY_FORCE_NATIVE_API=true`
3. Or patch `_check_compatibility` method

**Expected Outcome**: +2 passing tests → 285/438 (65.1%) 🎉

---

### Phase 4: Fix Error Suggestion Test (10 minutes)

**Target**: 1 failing test
**Root Cause**: Error message content doesn't match expectation

**Failing Test**:
1. test_get_error_suggestion_disk_space

**Error**: `AssertionError: 'disk space' not found in 'check the nixos manual...'`

**Fix Strategy**:
1. Check _get_error_suggestion implementation
2. Either fix the error detection logic OR
3. Update test expectation to match actual behavior

**Expected Outcome**: +1 passing test → 286/438 (65.3%) 🎉

---

### Phase 5: Verification & Celebration (15 minutes)

**Steps**:
1. Run full test_nix_integration.py suite
2. Verify all 27 tests passing (or maximum possible)
3. Run full test suite to confirm 65%+ pass rate
4. Commit with celebratory message 🎉
5. Update documentation

**Success Criteria**:
- ✅ 65%+ pass rate achieved
- ✅ test_nix_integration.py 90%+ passing
- ✅ Clean commits
- ✅ No regressions

---

### Phase 6: Documentation & Push (10 minutes)

**Steps**:
1. Create SESSION10_SUMMARY.md (5 min)
2. Final commit and push (3 min)
3. CELEBRATE MILESTONE! 🎊 (2 min)

---

## 🔍 Detailed Fix Plans

### Fix 1: Mock execute_native_operation

**Current Test Setup (BROKEN)**:
```python
self.mock_backend.execute = AsyncMock(return_value=mock_result)
# Later:
self.mock_backend.execute.assert_called_once()  # ❌ Never called!
```

**New Test Setup (WORKING)**:
```python
self.mock_backend.execute_native_operation = AsyncMock(return_value=mock_result)
# Later:
self.mock_backend.execute_native_operation.assert_called_once()  # ✅
# Check parameters:
call_args = self.mock_backend.execute_native_operation.call_args
self.assertEqual(call_args.kwargs['operation_type'], expected_type)
```

---

### Fix 2: Investigate get_system_info

**Steps**:
1. Read get_system_info implementation
2. Find where enum is misused
3. Compare with execute_intent fixes
4. Apply similar solution

**Likely Issue**:
Probably calling `OperationType.LIST_GENERATIONS` incorrectly

---

### Fix 3: Bypass Compatibility Check

**Option A - Mock in setUp**:
```python
def setUp(self):
    # ... existing setup ...
    with patch.object(NativeNixBackend, '_check_compatibility'):
        self.integration = NixOSIntegration()
```

**Option B - Environment Variable**:
```python
@patch.dict(os.environ, {'NIX_HUMANITY_FORCE_NATIVE_API': 'true'})
def test_error_recovery_workflow(self):
    integration = NixOSIntegration()
    # ...
```

**Option C - Patch Method**:
```python
with patch('luminous_nix.core.native_operations.check_nixos_version'):
    integration = NixOSIntegration()
```

---

## 📊 Expected Outcomes by Phase

| Phase | Tests Fixed | Total Passing | Pass Rate | Status |
|-------|-------------|---------------|-----------|--------|
| Start | 0 | 275 | 62.8% | ⏳ |
| Phase 1 | +5 | 280 | 63.9% | Target |
| Phase 2 | +3 | 283 | 64.6% | Target |
| Phase 3 | +2 | 285 | 65.1% | 🎯 **GOAL!** |
| Phase 4 | +1 | 286 | 65.3% | Bonus! |

---

## 🚨 Risk Mitigation

### Risk 1: Mock fixes more complex than expected
**Mitigation**: Time-box to 45 min, document complex issues for later
**Fallback**: Fix 3-4 tests instead of 5, still makes progress

### Risk 2: get_system_info has deeper issues
**Mitigation**: Investigate thoroughly but cap at 30 min
**Fallback**: Document for later, move to Phase 3

### Risk 3: Can't reach exactly 65%
**Mitigation**: We only need 10 tests total, have 11 targets
**Fallback**: 64.5% is still excellent progress

### Risk 4: Break existing tests
**Mitigation**: Run full suite before final commit
**Fallback**: Revert problematic changes

---

## 🎓 Patterns from Session 9 to Apply

### Pattern 1: Check Actual Method Signatures
```python
# Don't assume, verify:
grep -A 20 "async def execute" native_operations.py
```

### Pattern 2: Update Both Mock and Assertions
```python
# Mock setup:
self.mock_backend.METHOD_NAME = AsyncMock(...)

# Assertion:
self.mock_backend.METHOD_NAME.assert_called_once()
```

### Pattern 3: Handle Tuple Returns
```python
# If method returns tuple:
op_type, packages, options = method()

# Update assertions:
self.assertEqual(op_type.value, expected)
```

---

## 🎯 Success Metrics

### Must Have (Required):
- ✅ 65%+ pass rate (285+ tests)
- ✅ test_nix_integration.py 90%+ complete
- ✅ Clean commits, passing hooks
- ✅ No regressions

### Should Have (Target):
- ✅ test_nix_integration.py 100% complete (all 27 passing)
- ✅ 65.5%+ pass rate
- ✅ Comprehensive documentation

### Nice to Have (Bonus):
- ✅ 66%+ pass rate
- ✅ Additional quick wins identified
- ✅ Clear roadmap for 70%

---

## 📋 Pre-Flight Checklist

- [x] Review Session 9 learnings
- [x] Understand current state (62.8%, 11 failing tests)
- [x] Plan created with clear phases
- [x] Time estimates realistic
- [ ] TodoWrite initialized
- [ ] Ready to execute!

---

## 💡 Key Principles

1. **Systematic > Ad-hoc**: Fix all mocks consistently
2. **Test Incrementally**: Run tests after each phase
3. **Document Everything**: What works, what doesn't
4. **Celebrate Milestones**: 65% is a real achievement!
5. **Quality Maintained**: Don't hack, do it right

---

## 🎯 The Big Picture

**Why 65% Matters**:
- Demonstrates consistent improvement
- Shows systematic approach works
- Validates test quality improvements
- Sets foundation for 70%+ push

**Sessions 7-10 Combined Goal**:
- Start: 58.2% (255 tests)
- Target: 65%+ (285+ tests)
- Path: +30 tests over 4 sessions
- Current: +20 tests (Sessions 7-9)
- **This Session: +10 tests to complete the journey!**

---

**Status**: Ready to execute and cross the finish line!
**Confidence**: Very High (clear fixes, well-understood issues)
**Risk Level**: Low (conservative estimates, clear fallbacks)
**Expected Duration**: 1.5-2 hours

**LET'S REACH 65%!** 🚀🎯

---

*Session 10 will mark a significant milestone - crossing 65% pass rate through systematic, quality-focused improvements. This achievement validates our approach and sets the stage for the push toward 70%+.*
