# Phase 2 Action Plan - Security & Functionality
## November 14, 2025

### 🎯 Mission: Make Luminous Nix Secure and Functional

**Status:** 🚀 IN PROGRESS
**Previous Phase:** ✅ Phase 1 Complete (Configuration & Critical Fixes)

---

## 📊 Current State After Phase 1

### ✅ Achievements:
- Core modules importing: 5/5 (100%)
- Syntax errors: 0
- Configuration: Valid
- Version consistency: v0.8.1 across all files
- Documentation: Accurate and current

### ⚠️ Remaining Issues:
- **178 security vulnerabilities** (11 critical, 83 high)
- **100+ outdated dependencies**
- **CLI commands not tested** (unknown if working)
- **No automated tests**
- **47 top-level modules** (over-engineered)
- **Dead code present** (experimental features)

---

## 🎯 Phase 2 Objectives

### Primary Goals:
1. **Reduce security vulnerabilities** from 178 to <20 high-severity
2. **Verify CLI functionality** - ensure basic commands work
3. **Create test infrastructure** - automated validation
4. **Clean up dependencies** - remove unused packages
5. **Document working features** - separate from architecture

### Success Criteria:
- ✅ <20 high-severity vulnerabilities
- ✅ All 4 basic CLI commands working
- ✅ Basic test suite with >5 tests passing
- ✅ <50 outdated dependencies
- ✅ Clear feature status document

---

## 📋 Detailed Action Plan

### Track 1: SECURITY (Priority 1) ⚠️

#### Step 1.1: Analyze Security Vulnerabilities
**Time:** 15 minutes
**Action:**
```bash
# Check vulnerability details
poetry show --tree | grep -A3 "critical\|high"

# Get specific package versions with vulnerabilities
poetry audit || pip-audit
```

**Output:** List of critical/high vulnerabilities with affected packages

#### Step 1.2: Update Critical Security Packages
**Time:** 30 minutes
**Priority Packages:**
1. `cryptography` (42.0.8 → 46.0.3) - Authentication/encryption
2. `PyJWT` (2.8.0 → latest) - Token authentication
3. `authlib` (1.6.1 → 1.6.5) - OAuth/auth
4. `certifi` (2025.8.3 → 2025.11.12) - SSL certificates
5. `bcrypt` (4.3.0 → 5.0.0) - Password hashing

**Action:**
```bash
# Update security-critical packages
poetry update cryptography PyJWT authlib certifi bcrypt

# Check for breaking changes
poetry run python -c "import cryptography; import jwt; import authlib"

# Run quick tests
python test_imports_quick.py
```

**Validation:** Import test still passes, fewer vulnerabilities

#### Step 1.3: Batch Update Remaining Packages
**Time:** 45 minutes
**Strategy:**
- Update by category (web, ML, testing)
- Test after each category
- Document breaking changes

**Categories:**
1. **Web dependencies** (flask, gunicorn, websockets)
2. **ML dependencies** (torch, transformers, datasets)
3. **Testing dependencies** (pytest, coverage)
4. **Development tools** (black, ruff, mypy)

**Action:**
```bash
# Web dependencies
poetry update flask gunicorn flask-socketio

# ML dependencies (careful - large)
poetry update transformers datasets

# Testing & dev tools
poetry update pytest pytest-cov black ruff mypy
```

**Validation:** Verify imports, run tests

---

### Track 2: FUNCTIONALITY (Priority 1) ✅

#### Step 2.1: Test CLI Entry Point
**Time:** 10 minutes
**Action:**
```bash
# Test basic CLI access
poetry run ask-nix --version
poetry run ask-nix --help

# Test subcommands
poetry run ask-nix config --help
poetry run ask-nix settings --help
```

**Expected:** Version 0.8.1, help text displays

#### Step 2.2: Test Core Commands
**Time:** 20 minutes
**Commands to test:**
1. `ask-nix help` - Show help
2. `ask-nix search vim` - Search packages
3. `ask-nix "install firefox" --dry-run` - Test install
4. `ask-nix "list installed"` - List packages

**Action:**
```bash
# Create test script
cat > test_cli_commands.sh <<'EOF'
#!/bin/bash
echo "Testing CLI commands..."
poetry run ask-nix --help && echo "✅ Help" || echo "❌ Help"
poetry run ask-nix search vim && echo "✅ Search" || echo "❌ Search"
poetry run ask-nix config list && echo "✅ Config" || echo "❌ Config"
EOF

chmod +x test_cli_commands.sh
./test_cli_commands.sh
```

**Validation:** Record which commands work

#### Step 2.3: Fix Broken Commands
**Time:** 30 minutes
**Strategy:**
- For each broken command:
  - Identify error
  - Fix root cause
  - Test again
  - Document fix

**Common Issues:**
- Missing dependencies
- Import errors
- Configuration file issues
- Permission problems

---

### Track 3: TESTING INFRASTRUCTURE (Priority 2) 🧪

#### Step 3.1: Create pytest Configuration
**Time:** 15 minutes
**File:** `pytest.ini`
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

**File:** `tests/conftest.py`
```python
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
```

#### Step 3.2: Create Core Module Tests
**Time:** 30 minutes
**File:** `tests/test_core_imports.py`
```python
"""Test that core modules import successfully"""

def test_executor_imports():
    from luminous_nix.core.executor import SafeExecutor
    assert SafeExecutor is not None

def test_cache_imports():
    from luminous_nix.services.cache import CacheService
    assert CacheService is not None

def test_search_imports():
    from luminous_nix.services.search import SearchService
    assert SearchService is not None

def test_native_api_imports():
    from luminous_nix.core.native_nix_api import NativeNixAPI
    assert NativeNixAPI is not None

def test_json_optimizer_imports():
    from luminous_nix.core.json_optimized_nix import JSONOptimizedNix
    assert JSONOptimizedNix is not None
```

**File:** `tests/test_cli_basic.py`
```python
"""Test basic CLI functionality"""
from click.testing import CliRunner
from luminous_nix.cli import cli

def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'Luminous Nix' in result.output

def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(cli, ['--version'])
    assert result.exit_code == 0
    assert '0.8.1' in result.output
```

#### Step 3.3: Run Test Suite
**Time:** 10 minutes
**Action:**
```bash
# Install pytest if needed
poetry add --group dev pytest pytest-cov

# Run tests
poetry run pytest -v

# With coverage
poetry run pytest --cov=luminous_nix --cov-report=term-missing
```

**Validation:** Tests pass, coverage >50%

---

### Track 4: CODE QUALITY (Priority 2) 📝

#### Step 4.1: Run Linting and Fix Issues
**Time:** 30 minutes
**Action:**
```bash
# Run black formatter
poetry run black src/ tests/ --check
poetry run black src/ tests/  # Actually format

# Run ruff linter
poetry run ruff check src/ tests/

# Fix auto-fixable issues
poetry run ruff check --fix src/ tests/

# Check remaining issues
poetry run ruff check src/ tests/ --statistics
```

**Validation:** Reduced lint errors

#### Step 4.2: Type Checking
**Time:** 20 minutes
**Action:**
```bash
# Run mypy on core modules
poetry run mypy src/luminous_nix/core/
poetry run mypy src/luminous_nix/services/

# Document type issues
poetry run mypy src/ --no-error-summary > mypy_issues.txt
```

**Goal:** Identify type coverage gaps

#### Step 4.3: Add Pre-commit Hooks
**Time:** 15 minutes
**File:** `.pre-commit-config.yaml`
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.5
    hooks:
      - id: ruff
        args: [--fix]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

**Action:**
```bash
poetry run pre-commit install
poetry run pre-commit run --all-files
```

---

### Track 5: DOCUMENTATION (Priority 3) 📚

#### Step 5.1: Create Feature Status Matrix
**Time:** 20 minutes
**File:** `FEATURE_STATUS.md`

Content:
- Features marked as working ✅
- Features with architecture only 🏗️
- Features planned but not started 📋
- Features deprecated/removed ❌

#### Step 5.2: Update README
**Time:** 15 minutes
**Action:**
- Add installation instructions
- Add quick start guide
- Add feature status reference
- Add contribution guidelines

#### Step 5.3: API Documentation
**Time:** 25 minutes
**Action:**
- Add docstrings to public classes
- Add module-level documentation
- Create API reference structure
- Document key functions

---

### Track 6: DEPENDENCY CLEANUP (Priority 3) 🧹

#### Step 6.1: Identify Unused Dependencies
**Time:** 20 minutes
**Action:**
```bash
# Find imports in code
grep -r "^import \|^from " src/ | sort -u > actual_imports.txt

# Compare with pyproject.toml
# Manual review: which dependencies are unused?
```

**Tools:**
```bash
# pip-autoremove (if available)
pip install pip-autoremove
pip-autoremove --help

# Or manual analysis
poetry show --tree | less
```

#### Step 6.2: Remove Unused Dependencies
**Time:** 15 minutes
**Action:**
```bash
# Remove identified unused packages
poetry remove <package-name>

# Verify nothing breaks
python test_imports_quick.py
poetry run pytest
```

#### Step 6.3: Organize Dependencies
**Time:** 20 minutes
**Goal:** Clear separation:
- Core (always needed)
- Optional groups (tui, voice, web, ml, advanced)
- Development (testing, linting)

**Action:** Update pyproject.toml with clear comments

---

## 🕐 Timeline & Prioritization

### Immediate (Next 2 Hours):
1. ⚠️ **Security updates** (1 hour) - Track 1
2. ✅ **CLI testing** (30 min) - Track 2.1-2.2
3. 🧪 **Basic test suite** (30 min) - Track 3.1-3.2

### Short-term (Next 4 Hours):
4. 📝 **Code quality** (1 hour) - Track 4
5. 📚 **Feature documentation** (1 hour) - Track 5
6. 🧹 **Dependency cleanup** (1 hour) - Track 6
7. ✅ **Fix broken commands** (1 hour) - Track 2.3

### Total Phase 2 Time: ~6 hours

---

## 📊 Success Metrics

### Must Have (Phase 2 Complete):
- ✅ <20 high-severity vulnerabilities
- ✅ 4/4 basic CLI commands working
- ✅ Test suite created with >5 tests
- ✅ Linting configured and running
- ✅ Feature status documented

### Nice to Have:
- ✅ <10 high-severity vulnerabilities
- ✅ Pre-commit hooks installed
- ✅ API documentation started
- ✅ <30 outdated dependencies
- ✅ Test coverage >50%

---

## 🚨 Risk Management

### Potential Blockers:
1. **Dependency conflicts** - Updates may cause version conflicts
   - Mitigation: Update incrementally, test between updates

2. **Breaking changes** - New versions may break existing code
   - Mitigation: Read changelogs, have rollback plan

3. **CLI not working** - Commands may have deep issues
   - Mitigation: Fix incrementally, document issues

4. **Test failures** - Tests may reveal bugs
   - Mitigation: Document bugs, fix or skip known issues

### Contingency Plans:
- If security updates break things → Pin working versions, update gradually
- If CLI doesn't work → Focus on fixing one command at a time
- If tests fail → Document failures, mark as expected failures
- If timeline slips → Prioritize security over features

---

## 🎯 Definition of Done

Phase 2 is complete when:
1. ✅ Security vulnerabilities reduced by >80%
2. ✅ At least 3/4 CLI commands working
3. ✅ Test infrastructure in place and passing
4. ✅ Code quality tools configured
5. ✅ Feature status clearly documented
6. ✅ All changes committed and pushed
7. ✅ Phase 2 results documented

---

## 📝 Next Steps After Phase 2

### Phase 3: Quality & Maintainability
- Architecture rationalization (47 → <30 modules)
- Comprehensive testing (>80% coverage)
- Full API documentation
- Performance profiling
- Memory leak detection

### Phase 4: Advanced Features
- Neural HRM production deployment
- Voice interface activation
- PEP 621 migration
- Advanced caching
- Real-time monitoring

---

**Created:** November 14, 2025
**Author:** Claude (Code Review & Improvement)
**Status:** 🚀 Ready to execute
**Expected Completion:** ~6 hours
