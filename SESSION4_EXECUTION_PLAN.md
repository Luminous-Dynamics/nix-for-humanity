# 🎯 Session 4 Execution Plan - Maximum Impact
## November 15, 2025 - Continued Excellence

### 📊 Current Status

**Health Score:** 84% (Target: 90%+)
**Collection Errors:** 29 (Target: <10)
**Test Pass Rate:** 56.2% (Target: 70%+)
**Security Warnings:** 24 (Target: <10)

---

## 🎯 Session Goals (2-3 hours)

**Primary:** Reduce collection errors & improve test pass rate
**Secondary:** Fix critical security issues
**Stretch:** Hit 90% health score this session

---

## 📋 Execution Plan

### Phase 1: Complete Test Collection Fixes (45 min)

**Current:** 29 errors
**Target:** <10 errors
**Approach:** Fix remaining import issues systematically

#### Tasks:

**1.1 Analyze Remaining Errors (10 min)**
```bash
poetry run pytest tests/ --collect-only 2>&1 | grep -A 5 "ERROR collecting" > remaining_errors.txt
# Review and categorize
```

**1.2 Fix High-Volume Issues (20 min)**
- Check if multiple tests have same import problem
- Fix once, apply to all affected files
- Prioritize files with simple import fixes

**1.3 Add More Skip Markers (15 min)**
- For complex/outdated tests
- Document WHY they're skipped
- Create tracking issues for future

**Success Metric:** Collection errors <10

---

### Phase 2: Add Common Test Fixtures (30 min)

**Goal:** Make tests pass by providing proper mocks

#### Create Comprehensive Fixtures in `tests/conftest.py`:

```python
import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

# ============= Backend & Engine Mocks =============

@pytest.fixture
def mock_backend():
    """Mock LuminousNixBackend for testing"""
    backend = Mock()
    backend.execute.return_value = Mock(
        success=True,
        stdout="Command executed successfully",
        stderr="",
        exit_code=0,
        duration=0.5
    )
    backend.search.return_value = [
        {"name": "firefox", "version": "120.0"},
        {"name": "vim", "version": "9.0"}
    ]
    return backend

@pytest.fixture
def mock_executor():
    """Mock SafeExecutor for testing"""
    executor = Mock()
    executor.execute.return_value = Mock(
        success=True,
        output="Success",
        error=None
    )
    return executor

# ============= Intent & NLP Mocks =============

@pytest.fixture
def sample_intent():
    """Sample intent for testing"""
    return Mock(
        type="INSTALL",
        entities={"package": "firefox"},
        confidence=0.95,
        raw_text="install firefox"
    )

@pytest.fixture
def mock_intent_recognizer():
    """Mock IntentRecognizer"""
    recognizer = Mock()
    recognizer.recognize.return_value = Mock(
        type="INSTALL",
        entities={"package": "firefox"},
        confidence=0.95
    )
    return recognizer

# ============= Execution Results =============

@pytest.fixture
def success_result():
    """Successful execution result"""
    return Mock(
        success=True,
        output="Command completed successfully",
        error=None,
        exit_code=0
    )

@pytest.fixture
def failure_result():
    """Failed execution result"""
    return Mock(
        success=False,
        output="",
        error="Command failed: Package not found",
        exit_code=1
    )

# ============= NixOS Specific =============

@pytest.fixture
def mock_nix_env():
    """Mock Nix environment"""
    return {
        "NIX_PATH": "/nix/var/nix/profiles/per-user/root/channels",
        "NIX_PROFILES": "/nix/var/nix/profiles/default",
    }

@pytest.fixture
def sample_packages():
    """Sample package list"""
    return [
        {"name": "firefox", "version": "120.0", "description": "Web browser"},
        {"name": "vim", "version": "9.0", "description": "Text editor"},
        {"name": "git", "version": "2.42.0", "description": "Version control"},
    ]

# ============= Temp Directories =============

@pytest.fixture
def temp_dir(tmp_path):
    """Temporary directory for tests"""
    test_dir = tmp_path / "test_luminous"
    test_dir.mkdir()
    return test_dir

@pytest.fixture
def temp_config(temp_dir):
    """Temporary config file"""
    config_file = temp_dir / "config.yaml"
    config_file.write_text("# Test config")
    return config_file
```

**Impact:** Should help 30-50 tests pass

---

### Phase 3: Security Quick Wins (30 min)

**Priority:** Fix highest-risk security issues

#### Task 3.1: Fix shell=True (20 min)

**Find all occurrences:**
```bash
grep -rn "shell=True" src/ bin/ --include="*.py" | grep -v test | grep -v "\.pyc"
```

**Fix pattern:**
```python
# BEFORE (VULNERABLE):
result = subprocess.run(f"nix-env -qa {package}", shell=True)

# AFTER (SECURE):
result = subprocess.run(["nix-env", "-qa", package], shell=False)

# For complex commands, use list:
result = subprocess.run(["sh", "-c", "safe command here"], shell=False)
```

**Target:** 0 shell=True in production code

#### Task 3.2: Fix Insecure Random (10 min)

**Find usage:**
```bash
grep -rn "random\\.randint\|random\\.choice" src/ --include="*.py" | grep -i "token\|session\|key"
```

**Fix pattern:**
```python
# BEFORE:
import random
token = random.randint(1000, 9999)

# AFTER:
import secrets
token = secrets.randbelow(9000) + 1000
```

**Success Metric:** Security warnings 24 → <15

---

### Phase 4: Run & Analyze Tests (20 min)

#### Run Full Test Suite:
```bash
poetry run pytest tests/ -v --tb=short -x 2>&1 | tee full_test_run.txt
```

#### Generate Coverage:
```bash
poetry run pytest tests/ --cov=src/luminous_nix --cov-report=html --cov-report=term
```

#### Analyze Results:
```bash
# Count by status
grep "PASSED" full_test_run.txt | wc -l
grep "FAILED" full_test_run.txt | wc -l
grep "SKIPPED" full_test_run.txt | wc -l
```

**Success Metric:** Pass rate 56% → 65%+

---

### Phase 5: Quick Architecture Win (15 min)

**Find dead/unused code:**
```bash
# Install vulture if needed
poetry add --group dev vulture

# Find dead code
poetry run vulture src/ --min-confidence 80 > dead_code.txt
```

**Create cleanup list:**
- Document files with no imports
- List modules imported only once
- Identify duplicate functionality

**Output:** ARCHITECTURE_CLEANUP.md for next session

---

### Phase 6: Documentation & Commit (15 min)

#### Update Progress:
- Update SESSION_SUMMARY_NOV_15.md with this session
- Create BATCH_2_RESULTS.md
- Update health metrics

#### Commit:
```bash
git add -A
git commit -m "🎯 Phase 3A Execution: Tests + Security + Quality"
git push
```

---

## 📊 Success Metrics

| Metric | Start | Target | Stretch |
|--------|-------|--------|---------|
| **Collection Errors** | 29 | <10 | <5 |
| **Test Pass Rate** | 56% | 65% | 70% |
| **Tests Passing** | 222 | 260 | 280 |
| **Security Warnings** | 24 | <15 | <10 |
| **shell=True** | ~8 | 0 | 0 |
| **Health Score** | 84% | 90% | 92% |

---

## 🔧 Tools & Quick Commands

```bash
# Quick test status
poetry run pytest tests/ --collect-only -q 2>&1 | tail -5

# Run specific category
poetry run pytest tests/unit/ -v

# Check import
poetry run python -c "from luminous_nix.core.executor import SafeExecutor; print('✅')"

# Security scan
poetry run bandit -r src/ -ll | grep shell

# Format & lint
poetry run black src/ tests/
poetry run ruff check --fix src/
```

---

## 🎯 Execution Order

1. ✅ **Test Collection** (45 min) - Unblock tests
2. ✅ **Add Fixtures** (30 min) - Enable test passing
3. ✅ **Security Fixes** (30 min) - Remove vulnerabilities
4. ✅ **Run Tests** (20 min) - Measure improvement
5. ⭐ **Architecture** (15 min) - Find cleanup opportunities
6. ✅ **Document** (15 min) - Track & commit

**Total:** ~2.5 hours

---

## 🎬 Let's Execute!

Starting with **Phase 1: Complete Test Collection Fixes**

**Approach:**
- Systematic and focused
- Test after each fix
- Document as we go
- Commit frequently

**Remember:**
- Verification over claims
- Small focused changes
- Real metrics

Let's push to 90% health! 🚀

---

**Created:** November 15, 2025
**Session:** 4
**Target:** 84% → 90% health
**Focus:** Tests + Security + Quality
