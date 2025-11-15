# 🎯 Session 5 Execution Plan - Test Fixes & Quality Improvements

**Date**: 2025-11-15
**Duration**: 2-3 hours
**Goal**: Reduce collection errors to <5, improve test pass rate to 60%+, enhance code quality

## 📊 Current State (Session 5 Start)

| Metric | Value | Target | Priority |
|--------|-------|--------|----------|
| Collection Errors | 13 | <5 | **HIGH** |
| Tests Collected | 501 | 520+ | MEDIUM |
| Tests Passing | 230/428 (53.7%) | 260/430 (60%+) | **HIGH** |
| Security Issues (shell=True) | ~6 | 0 | MEDIUM |
| Code Health Score | ~84% | 87%+ | MEDIUM |

## 🎯 Session Goals

### Primary Goals (Must Complete)
1. **Reduce Collection Errors**: 13 → <5 (eliminate blockers)
2. **Improve Test Pass Rate**: 53.7% → 60%+ (fix easy wins)
3. **Fix Critical Imports**: Resolve remaining import issues

### Secondary Goals (Time Permitting)
4. **Security Hardening**: Eliminate remaining shell=True occurrences
5. **Lint Fixes**: Address high-priority ruff/black issues
6. **Documentation**: Update progress tracking

## 📋 Detailed Task Breakdown

### Phase 1: Collection Error Deep Dive (30 min)

**Objective**: Understand and categorize all 13 remaining collection errors

#### Task 1.1: Analyze Collection Errors (10 min)
```bash
# Get fresh error list
poetry run pytest tests/ --collect-only -q > /tmp/collection_status.txt 2>&1

# Categorize errors by type
grep "ERROR collecting" /tmp/collection_status.txt | sort
```

**Categories to identify:**
- Missing modules (e.g., `ModuleNotFoundError`)
- Import path issues (e.g., `ImportError: cannot import name`)
- Syntax/structure errors (e.g., `SyntaxError`)
- Dependency issues (e.g., module exists but broken)

#### Task 1.2: Prioritize Collection Fixes (10 min)

**Priority Matrix:**
- **P0 (Fix Now)**: Missing class/function that exists elsewhere (import path fix)
- **P1 (Fix Now)**: Module exists but has errors (can be fixed quickly)
- **P2 (Skip)**: Module doesn't exist and is old code (add skip marker)
- **P3 (Document)**: Complex dependency issue (document for later)

#### Task 1.3: Execute Collection Fixes (10 min)

**Fix Strategy:**
1. **Quick Wins First**: Import path corrections (2-3 min each)
2. **Skip Dead Tests**: Add pytestmark to unmaintainable tests
3. **Fix Critical Errors**: Address errors in core/__init__.py

**Success Criteria**: Collection errors 13 → <8

---

### Phase 2: Test Failure Analysis (30 min)

**Objective**: Identify and fix quick-win test failures

#### Task 2.1: Run Tests & Analyze Failures (10 min)
```bash
# Run tests and capture failure patterns
poetry run pytest tests/ -x -v --tb=short > /tmp/test_failures.txt 2>&1

# Identify failure categories
grep "FAILED" /tmp/test_failures.txt | cut -d':' -f3 | sort | uniq -c
```

**Failure Categories:**
- AssertionError (logic/expected value issues)
- AttributeError (API changes, missing methods)
- ImportError (runtime import issues)
- TypeError (signature mismatches)
- FileNotFoundError (missing test data/fixtures)

#### Task 2.2: Identify Quick Wins (10 min)

**Quick Win Criteria:**
- Same error pattern across multiple tests
- Simple assertion value mismatch
- Missing mock/fixture (already have in conftest.py)
- Outdated expected values

**Target**: Identify 10-20 tests that can be fixed with minimal effort

#### Task 2.3: Execute Test Fixes (10 min)

**Fix Strategy:**
1. **Fixture Issues**: Update tests to use new fixtures from conftest.py
2. **Assertion Updates**: Fix expected values for API changes
3. **Mock Updates**: Add missing mocks for new dependencies

**Success Criteria**: 10-20 additional tests passing

---

### Phase 3: Import & Module Fixes (30 min)

**Objective**: Resolve remaining import issues causing collection errors

#### Task 3.1: Fix Known Import Issues (20 min)

**From Session 4 errors, we know these need fixing:**

1. **test_error_intelligence_integration.py**
   - Error: `ModuleNotFoundError: No module named 'src.nix_for_humanity'`
   - Fix: Update imports to use `luminous_nix` instead of `nix_for_humanity`

2. **test_jsonrpc_server.py**
   - Error: `NameError: name 'UnifiedNixBackend' is not defined`
   - Fix: Improve fallback logic in core/__init__.py

3. **test_flake_manager.py**
   - Error: `ImportError: cannot import name 'DevShell'`
   - Fix: Add DevShell to flake_manager.py or create alias

4. **test_plugin_manager.py + test_voice_comprehensive.py**
   - Need to investigate specific errors

#### Task 3.2: Add Missing Aliases (5 min)

Create backward compatibility aliases in appropriate __init__.py files for:
- DevShell (if exists elsewhere)
- FeedbackCollector (if exists)
- Other commonly imported but moved classes

#### Task 3.3: Skip Dead Tests (5 min)

For tests that reference completely removed/archived features:
- Add `pytestmark = pytest.mark.skip(reason="...")`
- Document what feature was removed and when

**Success Criteria**: Collection errors <5

---

### Phase 4: Security & Quality (30 min)

**Objective**: Address remaining security issues and code quality

#### Task 4.1: Eliminate Remaining shell=True (15 min)

**Known remaining occurrences (~6):**
```bash
grep -rn "shell=True" src/luminous_nix/ --include="*.py" | grep -v test
```

**Fix each occurrence:**
1. Analyze if shell features (pipes, redirects) are needed
2. If yes: Quote user input with shlex.quote()
3. If no: Convert to shell=False with shlex.split()

**Priority files:**
- safe_executor.py (sandboxed execution - needs shell=True but must be secure)
- system_modes.py (profile hooks)
- first_run.py (setup commands)

#### Task 4.2: Fix High-Priority Lint Issues (10 min)

**From pre-commit errors, focus on:**
- E722: Bare except clauses (add Exception type)
- F841: Unused variables (remove or use)
- E402: Module imports not at top (move imports)
- F821: Undefined names (fix or import)

**Target**: Fix 20-30 lint errors in files we're already touching

#### Task 4.3: Update Test Fixtures (5 min)

Add any missing fixtures discovered during test fixing to conftest.py

---

### Phase 5: Verification & Documentation (20 min)

**Objective**: Verify improvements and document progress

#### Task 5.1: Run Full Test Suite (5 min)
```bash
poetry run pytest tests/ -q --tb=no > /tmp/final_test_results.txt 2>&1
```

**Capture metrics:**
- Collection errors (target: <5)
- Tests collected (target: 520+)
- Tests passing (target: 260+)
- Pass rate (target: 60%+)

#### Task 5.2: Security Verification (5 min)
```bash
# Count remaining shell=True in production code
grep -rn "shell=True" src/luminous_nix/ --include="*.py" | grep -v test | wc -l

# Verify no new security issues introduced
git diff origin/main --stat
```

#### Task 5.3: Update Documentation (5 min)

Update this file with actual results and create session summary

#### Task 5.4: Commit & Push (5 min)

Create comprehensive commit with all improvements

---

## 🎯 Success Criteria

### Minimum Success (Must Achieve)
- ✅ Collection errors: <8 (from 13)
- ✅ Tests passing: +15 (245 total)
- ✅ All changes committed and pushed

### Target Success (Goal)
- ✅ Collection errors: <5 (from 13)
- ✅ Tests passing: 260+ (60%+ pass rate)
- ✅ shell=True: <3 occurrences
- ✅ Documentation updated

### Stretch Success (If Time Permits)
- ✅ Collection errors: 0
- ✅ Tests passing: 280+ (65%+ pass rate)
- ✅ shell=True: 0 occurrences
- ✅ Pre-commit hooks passing

---

## 📊 Progress Tracking

### Phase 1: Collection Errors ⏳
- [ ] Task 1.1: Analyze errors
- [ ] Task 1.2: Prioritize fixes
- [ ] Task 1.3: Execute fixes

### Phase 2: Test Failures ⏳
- [ ] Task 2.1: Analyze failures
- [ ] Task 2.2: Identify quick wins
- [ ] Task 2.3: Execute fixes

### Phase 3: Import Fixes ⏳
- [ ] Task 3.1: Fix known imports
- [ ] Task 3.2: Add aliases
- [ ] Task 3.3: Skip dead tests

### Phase 4: Security & Quality ⏳
- [ ] Task 4.1: Fix shell=True
- [ ] Task 4.2: Fix lint issues
- [ ] Task 4.3: Update fixtures

### Phase 5: Verification ⏳
- [ ] Task 5.1: Run test suite
- [ ] Task 5.2: Security check
- [ ] Task 5.3: Update docs
- [ ] Task 5.4: Commit & push

---

## 🔄 Session Metrics (Will Update)

| Metric | Start | Current | Target | Status |
|--------|-------|---------|--------|--------|
| Collection Errors | 13 | - | <5 | ⏳ |
| Tests Collected | 501 | - | 520+ | ⏳ |
| Tests Passing | 230 | - | 260+ | ⏳ |
| Pass Rate | 53.7% | - | 60%+ | ⏳ |
| shell=True (prod) | ~6 | - | <3 | ⏳ |

---

## 💡 Key Insights & Learnings

*Will document as we progress...*

---

## 🚀 Next Session Preview

**If we achieve target success, Session 6 should focus on:**
1. Architecture cleanup (dead code removal)
2. Performance optimization (caching, lazy loading)
3. Integration test improvements
4. Documentation quality

**If we need more time on tests:**
1. Continue test failure fixes
2. Add more comprehensive fixtures
3. Refactor flaky tests
