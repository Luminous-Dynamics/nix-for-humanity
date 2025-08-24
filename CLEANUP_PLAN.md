# 🧹 Luminous Nix Codebase Cleanup Plan

## Executive Summary
The codebase has accumulated significant duplication during rapid development. This cleanup will consolidate ~600+ files down to essential components while preserving all working functionality.

## 🔍 Identified Issues

### 1. Interface Duplicates (`src/luminous_nix/interfaces/`)
- **cli.py** - Working implementation (322 lines) ✅ KEEP
- **cli_unified.py** - Duplicate attempt
- **cli_integrated.py** - Another duplicate  
- **cli_conscious.py** - Yet another duplicate
- **cli_integration_patch.py** - Patch file

**Action**: Keep only `cli.py`, archive others

### 2. Core Module Duplicates (`src/luminous_nix/core/`)
Multiple overlapping implementations:
- error_intelligence.py, error_intelligence_ast.py, error_intelligence_unified.py
- config_generator.py, config_generator_ast.py, simple_config_generator.py
- Multiple response/adapter files

**Action**: Identify which versions are actually used, consolidate

### 3. Consciousness Module Chaos (`src/luminous_nix/consciousness/`)
40+ files with overlapping functionality:
- Multiple voice implementations (now unified in voice/)
- Multiple integration files
- Multiple consciousness variants

**Action**: Already consolidated voice, need to consolidate others

### 4. Test File Explosion (`tests/`)
- Hundreds of test files
- Many testing non-existent features
- Duplicate test suites

**Action**: Keep only tests for actual features

### 5. Root Directory Clutter
150+ Python scripts in root:
- Demo files
- Test scripts  
- Integration attempts
- Experimental code

**Action**: Archive all non-essential files

## 📂 Cleanup Strategy

### Phase 1: Archive Experiments (Immediate)
```bash
# Create archive directory
mkdir -p .archive-2025-08-24

# Move all root-level Python files except essential ones
mv *.py .archive-2025-08-24/
# Keep only: setup.py, manage.py

# Move abandoned experiments
mv ai-improvements/ .archive-2025-08-24/
mv paradoxes/ .archive-2025-08-24/
mv pitch/ .archive-2025-08-24/
```

### Phase 2: Consolidate Interfaces
```bash
# In src/luminous_nix/interfaces/
# Keep: cli.py, __init__.py, api.py, tui.py
# Archive: cli_*.py variants
```

### Phase 3: Clean Core Module
Identify actively used implementations:
1. Check imports in cli/__init__.py
2. Trace execution path
3. Keep only referenced files
4. Archive duplicates

### Phase 4: Organize Consciousness Module
Group by functionality:
- poml_core/ - POML engine (KEEP)
- templates/ - POML templates (KEEP)  
- governance/ - Audit system (KEEP)
- Archive individual experimental files

### Phase 5: Test Rationalization
Keep only:
- Unit tests for existing features
- Integration tests that pass
- Remove aspirational tests

## 🎯 Target Structure

```
luminous-nix/
├── src/
│   └── luminous_nix/
│       ├── cli/              # CLI commands (7 files)
│       ├── core/             # Backend (~15 essential files)
│       ├── consciousness/    # POML system (~10 files)
│       ├── nlp/              # NLP (~5 files)
│       ├── voice/            # Unified voice (1 file)
│       ├── interfaces/       # Interfaces (4 files)
│       └── persistence/      # Data stores (3 files)
├── tests/
│   ├── unit/                 # Real unit tests
│   └── integration/          # Working integration tests
├── docs/                     # Keep all docs
├── bin/                      # Entry points
├── .archive-2025-08-24/      # All archived code
└── [config files]            # Keep all configs
```

## 📊 Expected Results

### Before Cleanup
- **Files**: ~600+ Python files
- **Lines**: ~150,000+ lines
- **Duplicates**: 60-70% redundant code
- **Tests**: 955 tests (mostly broken)

### After Cleanup
- **Files**: ~60-80 essential Python files
- **Lines**: ~20,000 working lines
- **Duplicates**: <5% 
- **Tests**: ~50-100 passing tests

## ⚠️ Safety Measures

1. **Full Backup First**
   ```bash
   cp -r luminous-nix luminous-nix-backup-$(date +%Y%m%d)
   ```

2. **Git Commit Before Changes**
   ```bash
   git add -A
   git commit -m "Pre-cleanup checkpoint"
   ```

3. **Test After Each Phase**
   ```bash
   poetry run python -m pytest tests/unit/test_cli_adapter.py
   ./bin/ask-nix "help"
   ```

4. **Document What's Archived**
   Create ARCHIVE_LOG.md listing what was moved and why

## 🚦 Cleanup Execution Order

1. **Backup everything** ✓
2. **Archive root Python files** → 
3. **Consolidate interfaces** →
4. **Clean core module** →
5. **Organize consciousness** →
6. **Rationalize tests** →
7. **Test everything** →
8. **Commit changes** →
9. **Document cleanup** 

## 🎯 Success Criteria

- [ ] `ask-nix "install firefox"` works
- [ ] `ask-nix "search text editor"` works  
- [ ] TUI launches with `nix-tui`
- [ ] All core commands functional
- [ ] Tests pass (the real ones)
- [ ] No duplicate implementations
- [ ] Clear code structure

## 📝 Notes

- This is a MAJOR cleanup - expect 70%+ reduction in files
- Focus on preserving WORKING code only
- Document everything that's removed
- Can always recover from .archive directory
- Prioritize clarity over features

---

**Ready to execute?** This will transform the codebase from experimental chaos to production-ready clarity.