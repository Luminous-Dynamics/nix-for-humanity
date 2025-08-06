# 📦 Requirements Migration Guide

*Transitioning from requirements.txt to modern pyproject.toml*

## Overview

We've consolidated all Python dependencies from multiple requirements files into a single, modern `pyproject.toml` file. This provides better dependency management, optional features, and clearer project metadata.

## What Changed

### Old Structure
```
requirements.txt          # Web server dependencies
requirements-tui.txt      # TUI dependencies  
scripts/requirements.txt  # ML/NLP dependencies
```

### New Structure
```
pyproject.toml           # All dependencies with optional groups
```

## Installation Guide

### Basic Installation (Core Only)
```bash
# Install minimal dependencies for basic ask-nix
pip install .
```

### Feature-Specific Installation
```bash
# Install with TUI support
pip install ".[tui]"

# Install with voice support
pip install ".[voice]"

# Install with web server
pip install ".[web]"

# Install with ML/NLP capabilities
pip install ".[ml]"

# Install multiple features
pip install ".[tui,voice]"
```

### Development Installation
```bash
# Install all development tools
pip install -e ".[dev]"

# Install everything (all features + dev tools)
pip install -e ".[all]"
```

### Advanced Features (Research)
```bash
# Install advanced AI/ML features
pip install ".[advanced]"
```

## Dependency Groups Explained

### Core Dependencies
Minimal set required for basic functionality:
- `py-nix-eval` - Python interface to Nix
- `requests` - HTTP client
- `click` - CLI framework
- `colorama` - Colored output
- `python-dotenv` - Environment management
- `jsonlines` - Knowledge base format

### Optional Groups

#### `tui` - Terminal User Interface
Beautiful terminal interface using Textual:
- `textual` - Modern TUI framework
- `rich` - Rich text formatting
- `blessed` - Terminal capabilities
- `pyperclip` - Clipboard support

#### `voice` - Speech Interface
Voice recognition and synthesis:
- `whisper-cpp-python` - Best-in-class STT
- `piper-tts` - Natural sounding TTS
- `vosk` - Lightweight STT fallback
- `espeak-ng` - Accessibility TTS

#### `web` - Web Server
Flask-based fallback server:
- `flask` - Web framework
- `gunicorn` - Production server
- `PyJWT` - Authentication
- `websockets` - Real-time communication

#### `ml` - Machine Learning
NLP and ML capabilities:
- `pandas`, `numpy` - Data processing
- `nltk`, `spacy` - Natural language processing
- `transformers`, `torch` - Deep learning
- `scikit-learn` - Classic ML
- `sentence-transformers` - Embeddings

#### `advanced` - Research Features
Cutting-edge AI capabilities:
- `peft`, `trl` - Fine-tuning frameworks
- `lancedb` - Vector database
- `networkx` - Knowledge graphs
- `dowhy`, `shap` - Causal reasoning
- `opentelemetry` - Observability

#### `dev` - Development Tools
Everything needed for development:
- `pytest` suite - Testing
- `black`, `ruff`, `mypy` - Code quality
- `mkdocs` - Documentation
- `ipython` - Enhanced REPL

## Migration Steps

### For Users

1. **Remove old virtual environment**:
   ```bash
   rm -rf venv/
   ```

2. **Create fresh environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

3. **Install with desired features**:
   ```bash
   # For most users (CLI + TUI)
   pip install ".[tui]"
   
   # For voice users
   pip install ".[tui,voice]"
   ```

### For Developers

1. **Clone and setup**:
   ```bash
   git clone https://github.com/Luminous-Dynamics/nix-for-humanity
   cd nix-for-humanity
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install in development mode**:
   ```bash
   pip install -e ".[all]"
   ```

3. **Run tests**:
   ```bash
   pytest
   ```

4. **Run linting**:
   ```bash
   black src tests
   ruff src tests
   mypy src
   ```

## Benefits of pyproject.toml

1. **Single Source of Truth**: All project metadata and dependencies in one file
2. **Optional Dependencies**: Users only install what they need
3. **Better Tooling**: Modern Python tools expect pyproject.toml
4. **Clearer Structure**: Dependencies grouped by purpose
5. **Development Workflow**: Editable installs with `-e`
6. **Standards Compliant**: PEP 517/518/621 compliant

## Cleanup

After migrating, you can remove the old requirements files:
```bash
# Archive old files (recommended)
mkdir -p archive/old-requirements
mv requirements*.txt archive/old-requirements/
mv scripts/requirements.txt archive/old-requirements/

# Or delete them (after verifying everything works)
rm requirements*.txt scripts/requirements.txt
```

## Troubleshooting

### Import Errors
If you get import errors after migration:
```bash
# Ensure you're in the right environment
which python  # Should show venv path

# Reinstall with --force-reinstall
pip install --force-reinstall -e ".[all]"
```

### Missing Dependencies
If a dependency seems missing:
```bash
# Check what's installed
pip list

# Install specific group if needed
pip install ".[ml]"  # For ML dependencies
```

### Version Conflicts
If you encounter version conflicts:
```bash
# Create fresh environment
deactivate
rm -rf venv/
python3 -m venv venv
source venv/bin/activate
pip install -e ".[all]"
```

## Next Steps

1. **Test your installation**:
   ```bash
   ask-nix --version
   ask-nix "help"
   ```

2. **Try the TUI** (if installed):
   ```bash
   nix-tui
   ```

3. **Run the test suite**:
   ```bash
   pytest
   ```

---

*"Modern packaging for a modern AI partner."*

🌊 We flow with better dependency management!