# 🎯 Specialized Model Training Plan

**Date**: December 3, 2025
**Based on**: Comprehensive Model Testing Results
**Overall Model Accuracy**: 56.8% (Target: 95%+)

---

## 📊 Executive Summary

Comprehensive testing of our three trained HRM models revealed **four critical gaps** requiring specialized model training:

1. **🔴 CRITICAL**: Development environments (0% accuracy)
2. **🔴 HIGH**: Error resolution (28.6% accuracy)
3. **🟡 MEDIUM**: System management (50% accuracy)
4. **🟡 MEDIUM**: Package management (62.5% accuracy)

**Strong areas** (keep using existing models):
- ✅ Configuration: 85.7%
- ✅ Flakes: 83.3%
- ✅ Explanation: 80.0%

---

## 🚨 Priority 1: Development Environment Specialist

### The Problem
**Current Accuracy: 0.0%** - The model fails to recognize ANY development environment queries.

### Failed Queries Analysis
| Query | Expected | Predicted | Issue |
|-------|----------|-----------|-------|
| "setup rust development environment" | devenv | configure | Confusing with general config |
| "create python shell with poetry" | devenv | unknown | Not recognizing dev context |
| "configure nodejs project" | devenv | configure | Missing dev-specific intent |
| "install docker for development" | devenv | install | Focusing on "install" not "development" |
| "setup vscode with nix" | devenv | configure | Missing IDE context |

### Root Cause
The model has **no training data** for `devenv` intent. It confuses development environment setup with:
- General configuration ("configure")
- Package installation ("install")
- Unknown queries

### Training Data Recommendations

**Positive Examples (100+ needed):**
```
"setup python development environment" → devenv
"create rust dev shell" → devenv
"configure nodejs project with nix" → devenv
"setup go development workspace" → devenv
"create typescript shell with npm" → devenv
"setup java development environment with gradle" → devenv
"configure c++ project with cmake" → devenv
"setup ruby development with bundler" → devenv
"create elixir dev shell with mix" → devenv
"setup haskell development environment" → devenv
"configure docker for development" → devenv
"setup vscode for nix development" → devenv
"create neovim development setup" → devenv
"setup emacs with LSP for development" → devenv
"configure intellij for nix projects" → devenv
"setup flutter development environment" → devenv
"create android dev shell" → devenv
"setup react native environment" → devenv
"configure embedded development toolchain" → devenv
"setup kernel development environment" → devenv
```

**Negative Examples (50+ needed to distinguish from other intents):**
```
"setup nginx web server" → configure (NOT devenv)
"install python" → install (NOT devenv)
"configure firewall" → configure (NOT devenv)
"explain development workflow" → explain (NOT devenv)
```

**Key Patterns to Learn:**
- Keywords: "development", "dev", "shell", "environment", "workspace", "project"
- Language names: python, rust, nodejs, java, go, etc.
- Tools: vscode, neovim, emacs, intellij, docker
- Build systems: cargo, npm, pip, poetry, gradle, maven, cmake

### Success Criteria
- **Minimum accuracy: 90%**
- Correctly distinguish dev environment from general config
- Handle both explicit ("dev environment") and implicit ("setup rust") queries

---

## 🚨 Priority 2: Error Resolution Specialist

### The Problem
**Current Accuracy: 28.6%** - The model only catches errors with explicit "error" or "failed" keywords.

### Failed Queries Analysis
| Query | Expected | Predicted | Issue |
|-------|----------|-----------|-------|
| "error: attribute 'neovim' missing" | error | error | ✅ Works (has "error:") |
| "collision between firefox packages" | error | unknown | ❌ Missing "collision" pattern |
| "build failed out of memory" | error | error | ✅ Works (has "failed") |
| "permission denied /etc/nixos" | error | unknown | ❌ Missing permission errors |
| "command not found: nix-shell" | error | unknown | ❌ Missing command not found |
| "hash mismatch" | error | unknown | ❌ Missing hash errors |
| "dependency conflict" | error | unknown | ❌ Missing dependency errors |

### Root Cause
The model only recognizes **two error patterns**:
1. Queries starting with "error:"
2. Queries containing "failed"

It misses **5 other common error patterns**:
- Collision errors
- Permission errors
- Command not found errors
- Hash mismatch errors
- Dependency conflicts

### Training Data Recommendations

**Positive Examples (200+ needed):**

**Attribute Errors:**
```
"error: attribute 'package' missing" → error
"attribute 'firefox' not found" → error
"no attribute named 'vim'" → error
"undefined variable 'neovim'" → error
```

**Collision Errors:**
```
"collision between firefox packages" → error
"file conflict in /usr/bin" → error
"multiple packages provide the same file" → error
"package collision detected" → error
"conflicting files in closure" → error
```

**Build Errors:**
```
"build failed out of memory" → error
"compilation error in package" → error
"builder failed with exit code 1" → error
"error: build of derivation failed" → error
"out of memory during build" → error
"build timeout exceeded" → error
```

**Permission Errors:**
```
"permission denied /etc/nixos" → error
"access denied to configuration.nix" → error
"cannot write to /nix/store" → error
"operation not permitted" → error
"insufficient permissions" → error
```

**Command Not Found:**
```
"command not found: nix-shell" → error
"bash: nixos-rebuild: command not found" → error
"nix-env: command not found" → error
"program not found in PATH" → error
```

**Hash Errors:**
```
"hash mismatch" → error
"hash mismatch for source" → error
"expected sha256 but got different hash" → error
"checksum verification failed" → error
"NAR hash mismatch" → error
```

**Dependency Errors:**
```
"dependency conflict" → error
"conflicting dependencies" → error
"cannot resolve dependency" → error
"missing dependency for package" → error
"circular dependency detected" → error
"dependency version conflict" → error
```

**Download Errors:**
```
"download failed" → error
"could not download source" → error
"network error during fetch" → error
"404 not found" → error
"connection timeout" → error
```

**Configuration Errors:**
```
"syntax error in configuration.nix" → error
"undefined option in config" → error
"assertion failed" → error
"infinite recursion detected" → error
"type error in configuration" → error
```

**Key Patterns to Learn:**
- Error indicators: "error", "failed", "denied", "conflict", "missing", "mismatch", "not found"
- Common NixOS errors: attribute missing, collision, hash mismatch
- System errors: permission denied, command not found
- Build errors: out of memory, timeout, exit code

### Success Criteria
- **Minimum accuracy: 95%**
- Catch ALL major error categories (not just "error:" prefix)
- High confidence on error patterns vs general queries

---

## 🟡 Priority 3: System Management Specialist

### The Problem
**Current Accuracy: 50%** - The model misses administrative and maintenance queries.

### Failed Queries Analysis
| Query | Expected | Predicted | Issue |
|-------|----------|-----------|-------|
| "check system health" | system | system | ✅ Works |
| "find safe rollback point" | system | search | ❌ Confused with search |
| "optimize disk space" | system | unknown | ❌ Missing optimization |
| "audit security vulnerabilities" | system | unknown | ❌ Missing security audit |
| "list all generations" | system | system | ✅ Works |
| "check service status" | system | system | ✅ Works |

### Root Cause
The model recognizes **direct system queries** ("check", "list", "status") but misses:
- Maintenance operations ("optimize", "audit")
- Rollback and recovery operations
- Security and health checks

### Training Data Recommendations

**Positive Examples (150+ needed):**

**Health & Monitoring:**
```
"check system health" → system
"monitor system resources" → system
"check disk usage" → system
"show memory usage" → system
"check cpu utilization" → system
"display system load" → system
```

**Generations & Rollback:**
```
"list all generations" → system
"show previous generations" → system
"find safe rollback point" → system
"rollback to generation 42" → system
"switch to previous generation" → system
"delete old generations" → system
"list bootable generations" → system
```

**Service Management:**
```
"check service status" → system
"list running services" → system
"show failed services" → system
"restart service" → system
"check systemd logs" → system
```

**Maintenance:**
```
"optimize disk space" → system
"clean up nix store" → system
"garbage collect" → system
"remove unused packages" → system
"optimize nix database" → system
"repair nix store" → system
```

**Security & Audit:**
```
"audit security vulnerabilities" → system
"check for CVEs" → system
"scan for security issues" → system
"update security patches" → system
"check system integrity" → system
```

**Performance:**
```
"optimize system performance" → system
"tune system settings" → system
"check for performance issues" → system
"analyze boot time" → system
"profile system resources" → system
```

**Key Patterns to Learn:**
- System operations: check, monitor, optimize, audit, clean
- Management: generations, services, resources, security
- Maintenance: garbage collect, repair, verify, optimize

### Success Criteria
- **Minimum accuracy: 85%**
- Recognize maintenance and optimization queries
- Distinguish from package search (common confusion)

---

## 🟡 Priority 4: Package Management Specialist

### The Problem
**Current Accuracy: 62.5%** - The model confuses similar actions and synonyms.

### Failed Queries Analysis
| Query | Expected | Predicted | Issue |
|-------|----------|-----------|-------|
| "install firefox" | install | install | ✅ Works |
| "remove vim" | remove | remove | ✅ Works |
| "update my system" | update | update | ✅ Works |
| "search for text editor" | search | search | ✅ Works |
| "upgrade all packages" | upgrade | update | ❌ Synonym confusion |
| "install neovim and ripgrep" | install | install | ✅ Works |
| "uninstall docker" | remove | install | ❌ Antonym confusion |
| "list installed packages" | list | install | ❌ Action confusion |

### Root Cause
The model has **synonym and action discrimination issues**:
1. Treats "upgrade" as "update" (close but distinct)
2. Confuses "uninstall" with "install" (opposite actions!)
3. Confuses "list" with "install" (completely different)

### Training Data Recommendations

**Positive Examples (200+ needed):**

**Install Variations:**
```
"install firefox" → install
"add package vim" → install
"get package emacs" → install
"download and install chromium" → install
"setup package docker" → install
```

**Remove Variations:**
```
"remove vim" → remove
"uninstall docker" → remove
"delete package firefox" → remove
"purge chromium" → remove
"get rid of vim" → remove
```

**Update vs Upgrade:**
```
"update my system" → update
"update nixos" → update
"refresh package index" → update
"sync with channels" → update

"upgrade all packages" → upgrade
"upgrade firefox" → upgrade
"upgrade to latest version" → upgrade
"update packages to newest versions" → upgrade
```

**Search Variations:**
```
"search for text editor" → search
"find package for markdown" → search
"lookup vim" → search
"discover packages for python" → search
"browse available packages" → search
```

**List Variations:**
```
"list installed packages" → list
"show installed software" → list
"display my packages" → list
"enumerate installed packages" → list
"what packages do I have" → list
```

**Negative Examples (important for disambiguation):**
```
"install docker for development" → devenv (NOT install)
"setup nginx web server" → configure (NOT install)
"error installing firefox" → error (NOT install)
```

**Key Patterns to Learn:**
- Install: install, add, get, download, setup
- Remove: remove, uninstall, delete, purge, get rid of
- Update: update, refresh, sync
- Upgrade: upgrade, update to latest, newest version
- Search: search, find, lookup, discover, browse
- List: list, show, display, enumerate, what do I have

### Success Criteria
- **Minimum accuracy: 90%**
- Correctly distinguish install/remove (opposites!)
- Correctly distinguish update/upgrade (similar but different)
- Correctly distinguish list from other actions

---

## 📋 Implementation Plan

### Phase 1: Data Collection (Week 1-2)
**Goal**: Gather 750+ training examples across all categories

1. **Development** (200 examples)
   - Cover all major languages (Python, Rust, JavaScript, Go, Java, etc.)
   - Include IDE setups (VSCode, Neovim, Emacs, IntelliJ)
   - Include build tools (npm, cargo, pip, poetry, gradle, etc.)

2. **Errors** (300 examples)
   - Cover all 9 error categories identified
   - Include real NixOS forum errors
   - Include GitHub issue errors

3. **System Management** (150 examples)
   - Health, monitoring, generations, services
   - Maintenance, security, performance

4. **Package Management** (100 examples)
   - Focus on synonyms and antonyms
   - Clear distinction between similar actions

**Sources for Training Data:**
- NixOS Discourse forum
- GitHub nixpkgs issues
- NixOS subreddit
- Stack Overflow NixOS questions
- Our existing conversation logs

### Phase 2: Model Training (Week 3-4)
**Goal**: Train and validate 4 specialized models

For each model:
1. **Prepare dataset**: 80% train, 10% validation, 10% test
2. **Train model**: Same architecture as existing HRM
3. **Validate**: Achieve target accuracy on validation set
4. **Test**: Verify on held-out test set

**Training Configuration:**
- Architecture: Same as existing HRM (proven to work)
- Epochs: 50-100 (with early stopping)
- Learning rate: 0.001 (adjust based on convergence)
- Batch size: 32
- Optimizer: Adam

### Phase 3: Integration (Week 5)
**Goal**: Integrate specialized models into AI orchestrator

1. **Update AI Orchestrator**:
   - Add routing logic for specialized models
   - Priority order: Specialist > General model
   - Confidence threshold: 0.7 for specialist, 0.5 for general

2. **Create Model Router**:
   ```python
   if query_type == "devenv" and devenv_model_available:
       return devenv_specialist.predict(query)
   elif query_type == "error" and error_model_available:
       return error_specialist.predict(query)
   # ... etc
   else:
       return general_hrm.predict(query)
   ```

3. **Testing**: Run comprehensive tests again
4. **Validation**: Target 95%+ overall accuracy

### Phase 4: Deployment (Week 6)
**Goal**: Ship to production

1. **Package models**: Include in standalone builds
2. **Update documentation**: Model selection guide
3. **Monitor performance**: Track accuracy in production
4. **User feedback**: Collect real-world examples

---

## 🎯 Success Metrics

### Overall Targets
- **Development**: 0% → 90%+ (CRITICAL)
- **Errors**: 28.6% → 95%+ (HIGH)
- **System Management**: 50% → 85%+ (MEDIUM)
- **Package Management**: 62.5% → 90%+ (MEDIUM)

### Overall System Accuracy
- **Current**: 56.8%
- **Target**: 95%+
- **Improvement**: +38.2 percentage points

### User Experience Improvements
- **Faster response times**: Specialists are smaller, faster
- **Better explanations**: Specialists understand nuances
- **Fewer corrections**: Higher accuracy = less "that's not what I meant"

---

## 📊 Testing Strategy

### After Each Model is Trained

**Unit Tests (Model-specific):**
```python
def test_devenv_specialist():
    model = DevEnvSpecialist()

    # Positive tests
    assert model.predict("setup rust environment") == "devenv"
    assert model.predict("create python shell") == "devenv"

    # Negative tests (should NOT match)
    assert model.predict("setup nginx") != "devenv"
    assert model.predict("install python") != "devenv"
```

**Integration Tests (Full stack):**
```python
def test_integrated_devenv_routing():
    orchestrator = AIOrchestrator()

    result = orchestrator.process("setup rust development environment")

    assert result.intent == "devenv"
    assert result.model_used == "devenv_specialist"
    assert result.confidence > 0.85
```

**Regression Tests:**
- Ensure new models don't break existing functionality
- Re-run full test suite after each integration
- Maintain test coverage > 90%

---

## 💡 Additional Recommendations

### 1. Continuous Learning
- Log queries that fail (low confidence or user correction)
- Use these as training data for future improvements
- Monthly model retraining with new data

### 2. Model Versioning
- Version each specialist model independently
- Track performance across versions
- Easy rollback if new version performs worse

### 3. Ensemble Learning (Future)
- Combine multiple specialists with voting
- Weight votes by confidence
- Further accuracy improvement potential

### 4. Active Learning
- Ask user for confirmation on low-confidence predictions
- Use confirmed examples for retraining
- Improves model over time with real-world data

---

## 🚀 Next Steps

**Immediate (This Week):**
1. ✅ Comprehensive testing complete
2. ✅ Gap analysis complete
3. ✅ Training plan created
4. ⏭️ Begin data collection for Development specialist
5. ⏭️ Begin data collection for Error specialist

**This Month:**
1. Complete data collection (750+ examples)
2. Train all 4 specialized models
3. Integrate into AI orchestrator
4. Comprehensive testing
5. Deploy to production

**This Quarter:**
1. Monitor production performance
2. Collect user feedback
3. Iterate on models
4. Achieve 95%+ overall accuracy
5. Begin work on ensemble learning

---

**Prepared by**: Luminous Nix AI Team
**Last Updated**: December 3, 2025
**Status**: Ready for implementation 🚀
