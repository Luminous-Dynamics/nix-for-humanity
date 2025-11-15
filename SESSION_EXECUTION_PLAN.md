# 🎯 Session Execution Plan - Immediate Action
## November 15, 2025

### 📊 Current Status

**Health Score:** 82% (Target: 95%+)
**Test Pass Rate:** 56.2% (222/395)
**Collection Errors:** ~15-21 (Target: <5)
**Security Warnings:** 24 (Target: 0)

---

## 🚀 This Session's Goals

**Primary Goal:** Fix test collection errors and improve test pass rate
**Secondary Goal:** Begin security quick wins
**Target Impact:** 82% → 87% health score

**Time Budget:** 3-4 hours
**Expected Outcomes:**
- Collection errors: 21 → <8
- Test pass rate: 56% → 65%
- Security warnings: 24 → <15

---

## 📋 Priority 1: Fix Test Collection Import Errors (90 minutes)

### Current Situation
From test collection analysis, we have these error patterns:

**Pattern A: Renamed Classes (5-6 files)**
- `NixForHumanityBackend` → Check actual class name in engine.py
- `Package`, `FeedbackItem` → Check if they exist in intents.py
- `DevShell`, `FlakeInput` → Check flake_manager.py

**Pattern B: Missing Modules (3-4 files)**
- `luminous_nix.core.backend` → Module doesn't exist
- `feedback_collector` → Module not in correct location
- `luminous_nix.consciousness` → Module removed/renamed

**Pattern C: Missing Script Files (2 files)**
- `scripts/educational-error-handler.py`
- Need to add `@pytest.mark.skip` decorators

### Execution Plan

#### Step 1: Identify Actual Class Names (15 min)
```bash
# Find what classes actually exist
grep -r "class.*Backend" src/luminous_nix/core/engine.py
grep -r "class Package" src/luminous_nix/core/intents.py
grep -r "class.*Flake" src/luminous_nix/core/flake_manager.py
```

#### Step 2: Create Import Mapping (10 min)
Document old → new mappings in a file for reference

#### Step 3: Fix Tests Systematically (60 min)

**Batch 1: Engine/Backend imports (6 files, 20 min)**
Files:
- tests/e2e/test_persona_journeys.py
- tests/integration/test_cli_core_pipeline.py
- tests/integration/test_real_nixos_operations.py
- tests/integration/test_security_execution.py
- tests/unit/test_backend_core.py
- tests/v1.0/test_v1_core_features.py

Fix approach:
```python
# Change from:
from luminous_nix.core.engine import NixForHumanityBackend

# To (example - check actual name):
from luminous_nix.core.engine import LuminousNixBackend
# OR add an alias in engine.py:
NixForHumanityBackend = LuminousNixBackend
```

**Batch 2: Missing module references (4 files, 20 min)**
- test_error_intelligence_integration.py → Fix backend import
- test_adaptive_voice.py → Fix consciousness import
- test_feedback_collector.py → Fix module path
- test_knowledge_base.py → Fix module path

**Batch 3: Missing classes (2 files, 10 min)**
- test_core_types.py → Add Package/FeedbackItem to intents.py or update test
- test_flake_manager.py → Add DevShell/FlakeInput or update test

**Batch 4: Missing files (2 files, 10 min)**
```python
# Add skip decorator:
@pytest.mark.skip(reason="scripts/educational-error-handler.py not implemented yet")
def test_educational_error_handler():
    pass
```

#### Step 4: Verify (5 min)
```bash
poetry run pytest tests/ --collect-only -q 2>&1 | grep -c "ERROR"
# Target: <8 errors (from ~15-21)
```

**Success Metrics:**
- ✅ Collection errors: 21 → <8
- ✅ All tests discoverable
- ✅ Import errors resolved

---

## 📋 Priority 2: Fix Common Test Failures (60 minutes)

### Approach: Fix by Pattern

Once tests collect, run them and categorize failures:
```bash
poetry run pytest tests/ -v --tb=line 2>&1 | tee test_run_results.txt
```

#### Pattern 1: Mock Fixture Issues (30 min)

**Common issue:** Tests expect mocks that don't exist

Fix in `tests/conftest.py`:
```python
import pytest
from unittest.mock import Mock, MagicMock

@pytest.fixture
def mock_nix_backend():
    """Mock NixOS backend for testing"""
    backend = Mock()
    backend.execute.return_value = Mock(
        success=True,
        stdout="Success",
        stderr="",
        exit_code=0
    )
    return backend

@pytest.fixture
def sample_intent():
    """Sample intent for testing"""
    return Mock(
        type="INSTALL",
        entities={"package": "firefox"},
        confidence=0.95
    )

@pytest.fixture
def mock_execution_result():
    """Mock execution result"""
    return Mock(
        success=True,
        output="Package installed",
        error=None
    )
```

#### Pattern 2: Assertion Updates (20 min)

**Common issue:** Expected values don't match new behavior

Strategy:
- Run test, see what it expects
- Check if expectation is still valid
- Update assertion to match current behavior
- Document why change was made

#### Pattern 3: API Changes (10 min)

**Common issue:** Method signatures changed

Quick fixes:
- Update method calls to match new signatures
- Add/remove parameters as needed
- Use keyword arguments for clarity

**Success Metrics:**
- ✅ Test pass rate: 56% → 65%
- ✅ At least 30 more tests passing
- ✅ No new failures introduced

---

## 📋 Priority 3: Security Quick Wins (45 minutes)

### Focus: High-Impact, Low-Effort Fixes

#### Task 1: Fix shell=True (20 min)

Find and fix:
```bash
# Find occurrences
grep -rn "shell=True" src/ bin/ --include="*.py" | grep -v "\.pyc"

# For each one, apply this fix:
# BEFORE:
subprocess.run(f"nix-env -qa {package}", shell=True)

# AFTER:
subprocess.run(["nix-env", "-qa", package], shell=False)
```

Target files (estimated 5-8 locations):
- VERIFY_STATUS.py
- verify_release_with_poetry.py
- Any src/luminous_nix files using subprocess

**Impact:** Eliminates command injection vulnerabilities

#### Task 2: Fix Insecure Random (15 min)

```bash
# Find usage
grep -rn "random\\.choice\|random\\.randint" src/ --include="*.py" | grep -i "token\|session\|key"

# Fix pattern:
# BEFORE:
import random
token = random.randint(1000, 9999)

# AFTER:
import secrets
token = secrets.randbelow(9000) + 1000
```

**Impact:** Secure random generation for tokens/sessions

#### Task 3: Document Remaining Issues (10 min)

For md5 and pickle usage:
- Create SECURITY_IMMEDIATE_FIXES.md
- List each occurrence
- Note why it needs fixing
- Plan for next session

**Success Metrics:**
- ✅ shell=True: 8 → 0 occurrences
- ✅ Insecure random: Fixed in security-sensitive contexts
- ✅ Security warnings: 24 → <15

---

## 📋 Priority 4: Code Quality Improvements (30 minutes)

### Task 1: Update Pre-commit Config (10 min)

Now that config_generator is fixed, we can:
1. Remove it from exclude list
2. Test pre-commit runs successfully
3. Commit the improvement

```bash
# Test pre-commit
poetry run pre-commit run --all-files 2>&1 | tail -50

# If successful, remove exclusions
```

### Task 2: Run Full Formatter/Linter (15 min)

```bash
# Format everything
poetry run black src/ tests/

# Fix auto-fixable lint issues
poetry run ruff check --fix src/ tests/

# Review remaining issues
poetry run ruff check src/ tests/ | tee ruff_remaining.txt
```

### Task 3: Update Documentation (5 min)

Update TODAYS_PROGRESS.md with:
- What we fixed this session
- New test metrics
- Security improvements
- Next priorities

**Success Metrics:**
- ✅ Pre-commit runs without excludes
- ✅ Code consistently formatted
- ✅ Progress documented

---

## 📋 Bonus: If Time Permits

### Quick Architecture Wins (20-30 min)

**Identify Dead Code:**
```bash
# Find files with no imports
poetry run vulture src/ --min-confidence 80

# Check for unused modules
grep -r "import.*from luminous_nix" tests/ src/ | \
  cut -d: -f2 | sort | uniq -c | sort -rn
```

**Create Consolidation Candidates List:**
- Modules with <50 lines
- Modules imported only once
- Duplicate functionality

Document in ARCHITECTURE_CLEANUP.md for future session

---

## 🎯 Session Timeline

### Hour 1: Test Collection Fixes (60 min)
- 0:00-0:15: Identify actual class names
- 0:15-0:35: Fix Batch 1 (Backend imports)
- 0:35-0:55: Fix Batch 2 & 3 (Missing modules/classes)
- 0:55-1:00: Verify collection errors reduced

### Hour 2: Test Improvements (60 min)
- 1:00-1:30: Add common fixtures to conftest.py
- 1:30-1:50: Fix assertion patterns
- 1:50-2:00: Run tests, document improvements

### Hour 3: Security & Quality (60 min)
- 2:00-2:20: Fix shell=True vulnerabilities
- 2:20-2:35: Fix insecure random
- 2:35-2:45: Update pre-commit config
- 2:45-3:00: Format, lint, document

### Hour 4: Polish & Commit (Optional)
- 3:00-3:20: Architecture analysis
- 3:20-3:40: Documentation updates
- 3:40-4:00: Comprehensive commit & push

---

## 📊 Success Metrics for This Session

| Metric | Current | Target | Stretch |
|--------|---------|--------|---------|
| **Collection Errors** | 21 | <8 | <5 |
| **Test Pass Rate** | 56% | 65% | 70% |
| **Tests Passing** | 222 | 260 | 280 |
| **Security Warnings** | 24 | <15 | <10 |
| **shell=True Usage** | 8 | 0 | 0 |
| **Health Score** | 82% | 87% | 90% |

---

## 🔧 Tools & Commands Reference

### Quick Status Checks
```bash
# Test collection status
poetry run pytest tests/ --collect-only -q 2>&1 | tail -20

# Test run summary
poetry run pytest tests/ -v --tb=line 2>&1 | tail -50

# Import verification
poetry run python -c "from luminous_nix.core import *; print('✅ Core imports work')"

# Security scan
poetry run bandit -r src/ -ll
```

### Quick Fixes
```bash
# Format specific file
poetry run black src/luminous_nix/path/to/file.py

# Check specific test
poetry run pytest tests/unit/test_specific.py -v

# Find pattern
grep -rn "pattern" src/ --include="*.py"
```

---

## 🎬 Let's Execute!

**Starting now:** Priority 1 - Fix test collection errors

**Mindset:**
- Small, focused changes
- Test after each fix
- Commit frequently
- Document as we go

**Remember:**
- Verification over claims
- Real metrics over aspirations
- Progress over perfection

Let's make it excellent! 🚀

---

**Created:** November 15, 2025
**Estimated Duration:** 3-4 hours
**Expected Health Score:** 82% → 87%
**Status:** Ready to execute
