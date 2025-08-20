# Luminous Nix Naming Conventions

**Last Updated**: 2025-08-16  
**Status**: Transition in Progress

## 📝 Official Names

### Project Name
- **Full Name**: **Luminous Nix**
- **Abbreviation**: **Luminix** (only where brevity matters - URLs, configs)
- **Command**: **`ask-nix`** (ALWAYS - never abbreviate)
- **NOT**: "Nix for Humanity" (old name, being phased out)

### Package Names
- **PyPI Package**: `luminous-nix` (when published)
- **Poetry Name**: `luminous-nix` (in pyproject.toml)
- **Source Directory**: `nix_humanity` (current, will become `luminous_nix`)

## 🔄 Current Transition Status

### What's Been Updated ✅
- `pyproject.toml` → name = "luminous-nix"
- Documentation → All new docs use "Luminous Nix"
- CLI commands → Always `ask-nix`
- Claude memory → Updated to use correct naming

### What Still Needs Updating 🚧
- Source directory: `src/nix_humanity/` → `src/luminous_nix/`
- Import statements: `from nix_humanity` → `from luminous_nix`
- Test imports: Update all test files
- Old references in code comments

## 📁 Directory Structure Clarification

Current structure in `src/`:
```
src/
├── luminous_nix/      # Old attempt, mostly .bak files - TO BE REMOVED
├── nix_for_humanity/  # Minimal stub - TO BE REMOVED  
└── nix_humanity/      # ACTIVE CODE - TO BE RENAMED to luminous_nix/
```

Target structure:
```
src/
└── luminous_nix/      # All active code here
```

## 🎯 Migration Plan (Week 2)

1. **Archive old directories**:
   - Move `src/luminous_nix/*.bak` → `.archive-2025-08/`
   - Move `src/nix_for_humanity/` → `.archive-2025-08/`

2. **Rename active directory**:
   - `src/nix_humanity/` → `src/luminous_nix/`

3. **Update all imports**:
   - Find: `from nix_humanity`
   - Replace: `from luminous_nix`
   - Find: `import nix_humanity`
   - Replace: `import luminous_nix`

4. **Update test files**:
   - All test imports
   - Mock paths
   - Fixtures

## ⚠️ Important Notes

### Why the Confusion?
The project evolved through several names:
1. **Original**: "Nix for Humanity" (vision phase)
2. **Simplified**: "nix_humanity" (code organization)
3. **Current**: "Luminous Nix" (brand identity)

### Temporary State
During transition, these work:
- Package: `nix_humanity` (in code)
- Project: `luminous-nix` (in pyproject.toml)
- Command: `ask-nix` (always)

### Import Examples

**Current (temporary)**:
```python
from nix_humanity.core.intents import IntentRecognizer
from nix_humanity.core.executor import SafeExecutor
```

**Future (after migration)**:
```python
from luminous_nix.core.intents import IntentRecognizer
from luminous_nix.core.executor import SafeExecutor
```

## 🚀 Quick Reference

| Context | Current | Target | Status |
|---------|---------|--------|--------|
| Project Name | Luminous Nix | Luminous Nix | ✅ |
| CLI Command | ask-nix | ask-nix | ✅ |
| PyPI Package | - | luminous-nix | 📅 |
| Poetry Name | luminous-nix | luminous-nix | ✅ |
| Source Dir | nix_humanity | luminous_nix | 🚧 |
| Imports | nix_humanity | luminous_nix | 🚧 |

## 📝 For New Contributors

Until migration is complete:
- **Write docs with**: "Luminous Nix"
- **Import with**: `from nix_humanity`
- **Call CLI with**: `ask-nix`

---

*This document will be updated after the Week 2 migration sprint*