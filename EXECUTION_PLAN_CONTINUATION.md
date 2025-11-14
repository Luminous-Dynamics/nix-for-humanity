# Execution Plan - Immediate High-Value Improvements
## November 14, 2025 - Continuation Session

### 🎯 Mission: Fix Critical Issues & Apply Quality Improvements

**Strategy:** Fix blockers first, then quality improvements
**Timeline:** 30-45 minutes
**Risk Level:** Low (all changes tested immediately)

---

## 🔥 Priority 1: CRITICAL FIXES (15 min)

### 1. Fix maya_mode.py Syntax Error 🔴
**File:** `src/luminous_nix/core/maya_mode.py:162`
**Issue:** Invalid function name `def 2-5 seconds_search`
**Impact:** BLOCKER - Prevents code formatting

**Action:**
```python
# Current (BROKEN):
def 2-5 seconds_search(self, term: str, max_results: int = 3) -> MayaResponse:

# Fixed:
def fast_search(self, term: str, max_results: int = 3) -> MayaResponse:
    """Fast package search (typically 2-5 seconds)"""
```

**Verification:** `poetry run black --check src/luminous_nix/core/maya_mode.py`

### 2. Fix Voice Module Import 🔴
**File:** `src/luminous_nix/voice/__init__.py:17`
**Issue:** Missing sacred_voice_interface module
**Impact:** 5 test failures

**Action:** Comment out missing import
**Verification:** `poetry run pytest tests/unit/test_adaptive_voice.py -v`

---

## ⚡ Priority 2: CODE QUALITY (20 min)

### 3. Auto-Format Code 🟡
**Tool:** black
**Files:** All Python files
**Impact:** Consistent formatting, better readability

**Action:**
```bash
poetry run black src/ tests/
```

**Expected:** ~19 files reformatted
**Verification:** All tests still pass

### 4. Auto-Fix Lint Issues 🟡
**Tool:** ruff
**Issues:** ~50 auto-fixable
**Impact:** Cleaner code, fewer warnings

**Action:**
```bash
poetry run ruff check --fix src/
```

**Expected:** ~50 issues auto-fixed
**Verification:** Tests still pass

---

## ✅ Priority 3: VALIDATION (10 min)

### 5. Run Test Suite
**Scope:** All core tests
**Expected:** Should still be 100% passing

**Action:**
```bash
poetry run pytest tests/test_core_imports.py -v
poetry run pytest tests/unit/ -v --maxfail=3
```

### 6. Verify CLI Still Works
**Commands:** Version, help, basic operations

**Action:**
```bash
poetry run ask-nix --version
poetry run ask-nix --help
```

---

## 📊 Expected Outcomes

### Before Execution:
- 🔴 1 syntax error blocking
- 🔴 5 tests failing (voice)
- 🟡 19 files need formatting
- 🟡 ~50 auto-fixable lint issues

### After Execution:
- ✅ 0 syntax errors
- ✅ Tests fixed or documented
- ✅ All code formatted
- ✅ ~50 fewer lint issues
- ✅ Cleaner, more maintainable code

---

## 🎯 Success Metrics

| Task | Time | Success Criteria |
|------|------|------------------|
| Fix syntax | 5 min | maya_mode.py parses |
| Fix voice | 5 min | Import errors gone |
| Format code | 10 min | Black happy |
| Fix lint | 10 min | ~50 issues fixed |
| Test | 5 min | All pass |
| Verify | 5 min | CLI works |

**Total:** 40 minutes

---

## 🚀 Let's Execute!

**Order:**
1. Fix syntax error → Unblocks everything
2. Fix voice import → Fixes tests
3. Format code → Quality baseline
4. Auto-fix lint → Clean code
5. Test everything → Verify safety
6. Document → Record progress

**Start NOW!**
