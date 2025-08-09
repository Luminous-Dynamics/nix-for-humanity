# 🐍 Python Version Strategy

*Optimal Python version management for main application and research components*

---

💡 **Quick Context**: How we use both Python 3.13 and 3.11 for different components  
📍 **You are here**: Architecture → Python Version Strategy  
🔗 **Related**: [Enabling Research Components](./11-ENABLING-RESEARCH-COMPONENTS.md) | [System Architecture](./01-SYSTEM-ARCHITECTURE.md)  
⏱️ **Read time**: 5 minutes  
📊 **Mastery Level**: 🌿 Intermediate

---

## Overview

Nix for Humanity uses a dual Python version strategy to maximize compatibility and performance:

- **Python 3.13**: Main application, CLI, TUI, web services (latest features, best performance)
- **Python 3.11**: Research components requiring DoWhy and other scientific packages

## Why Two Python Versions?

### Python 3.13 (Main Application)
- ✅ Latest performance improvements
- ✅ Better error messages
- ✅ Improved typing support
- ✅ Faster startup time
- ✅ All core dependencies work perfectly

### Python 3.11 (Research Components)
- ✅ DoWhy compatibility (requires Python <3.12)
- ✅ Stable scientific Python ecosystem
- ✅ All ML/AI libraries fully tested
- ✅ Poetry2nix works seamlessly

## Architecture

```
┌─────────────────────────────────────┐
│         User Interface Layer         │
│  (CLI, TUI, Voice, Web API)         │
│        Python 3.13                   │
└──────────────┬──────────────────────┘
               │
┌──────────────┴──────────────────────┐
│      Core Backend Services          │
│  (NLP, Commands, Basic Logic)       │
│        Python 3.13                   │
└──────────────┬──────────────────────┘
               │
┌──────────────┴──────────────────────┐
│    Research Components Layer         │
│ (SKG, Trust, Metrics, Perception)   │
│        Python 3.11                   │
│   (Loaded on-demand via mocks)      │
└─────────────────────────────────────┘
```

## Usage Guide

### For Developers

#### Using the Python Selector
```bash
# Run main application code
python-select main src/cli/main.py

# Run research component tests
python-select research test_skg.py

# Check available versions
python-select check
```

#### Direct Usage
```bash
# Main app development
python3.13 src/app.py
python3.13 -m pytest tests/unit/

# Research components
python3.11 test_component_integration.py
python3.11 -m pip install dowhy  # Only works with 3.11
```

#### Environment Variables
```bash
# Force research Python for all operations
export NIX_HUMANITY_PYTHON_RESEARCH=true
python app.py  # Will use Python 3.11

# Check which Python is active
python --version
```

### In Nix Shells

Both `shell.nix` and `flake.nix` provide:
- `python3` → Python 3.13 (default)
- `python3.11` → Python 3.11 (research)
- Aliases: `python-main`, `python-research`

### For CI/CD

```yaml
# GitHub Actions example
jobs:
  test-main:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - run: pytest tests/unit/

  test-research:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: python test_component_integration.py
```

## Implementation Details

### Mock Components (Graceful Degradation)

When Python 3.13 is used but research components are needed:

```python
# backend/core/backend.py
try:
    from backend.knowledge_graph.skg import SymbioticKnowledgeGraph
except ImportError:
    from backend.mocks import MockSymbioticKnowledgeGraph as SymbioticKnowledgeGraph
```

This ensures:
- Main app works without heavy dependencies
- Research features gracefully degrade
- No runtime errors from missing packages

### Poetry Configuration

The `pyproject.toml` specifies Python compatibility:

```toml
[tool.poetry.dependencies]
python = "^3.11"  # Works with 3.11, 3.12, and 3.13

# Research dependencies marked as optional
dowhy = {version = "^0.11.0", optional = true, python = ">=3.8,<3.12"}
```

### Development Workflow

1. **Start Development**:
   ```bash
   nix develop  # or nix-shell
   ```

2. **Main App Work**:
   ```bash
   python3.13 src/cli/main.py
   # or
   python-select main src/cli/main.py
   ```

3. **Research Component Work**:
   ```bash
   python3.11 backend/knowledge_graph/test_skg.py
   # or
   python-select research backend/knowledge_graph/test_skg.py
   ```

4. **Run Tests**:
   ```bash
   # Main app tests (fast)
   python3.13 -m pytest tests/unit/ -v

   # Integration tests with research components
   python3.11 -m pytest tests/integration/ -v
   ```

## Best Practices

### 1. Use the Right Python for the Task
- UI/CLI/Web → Python 3.13
- ML/AI/Research → Python 3.11

### 2. Import Research Components Conditionally
```python
if os.getenv("NIX_HUMANITY_DISABLE_RESEARCH") != "true":
    try:
        from backend.knowledge_graph.skg import SymbioticKnowledgeGraph
        SKG_AVAILABLE = True
    except ImportError:
        SKG_AVAILABLE = False
```

### 3. Document Python Requirements
Always specify which Python version in:
- Script shebangs: `#!/usr/bin/env python3.11`
- Documentation headers
- CI/CD configurations

### 4. Test with Both Versions
Ensure compatibility:
```bash
# Quick compatibility check
python3.13 -m py_compile src/**/*.py
python3.11 -m py_compile backend/**/*.py
```

## Troubleshooting

### "Module not found" Errors
- Check which Python version you're using
- Research components only work with Python 3.11
- Use `python-select check` to verify setup

### Performance Differences
- Python 3.13 is ~10-15% faster for most operations
- Use 3.13 for user-facing code
- Use 3.11 only when research components are needed

### Poetry Issues
- Poetry uses Python 3.11 as base
- All dependencies resolved for 3.11
- Some packages may work with 3.13 anyway

## Future Plans

### Python 3.12+ Support for DoWhy
When DoWhy supports Python 3.12+:
1. Update `pyproject.toml` constraint
2. Migrate everything to single Python version
3. Simplify development environment

### Gradual Migration Path
1. Keep dual support during transition
2. Test research components with newer Python
3. Phase out Python 3.11 when possible

## Summary

The dual Python strategy provides:
- ✅ Best performance for user-facing code (3.13)
- ✅ Full compatibility for research components (3.11)
- ✅ Graceful degradation via mocks
- ✅ Clear separation of concerns
- ✅ Future-proof architecture

Use `python-select` to automatically choose the right version, or explicitly use `python3.13`/`python3.11` as needed.

---

*"Two Pythons, one vision: Making NixOS accessible through consciousness-first AI, with the best tools for each task."*