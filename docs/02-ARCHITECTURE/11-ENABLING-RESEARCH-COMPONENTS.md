# 🧬 Enabling Research Components with Nix

*How to properly enable the research-based symbiotic intelligence components using Nix*

---

💡 **Quick Context**: Proper Nix-based dependency management for research components  
📍 **You are here**: Architecture → Enabling Research Components  
🔗 **Related**: [Research Integration](./10-RESEARCH-INTEGRATION.md) | [System Architecture](./01-SYSTEM-ARCHITECTURE.md)  
⏱️ **Read time**: 5 minutes  
📊 **Mastery Level**: 🌿 Intermediate

---

## Overview

The research components (SKG, Trust Engine, Consciousness Metrics, etc.) require additional dependencies that are already defined in `pyproject.toml` but need to be enabled through Poetry's optional dependency groups.

## Current Setup

The project uses:
- **Flake.nix** with poetry2nix for dependency management
- **pyproject.toml** for Python dependency specification
- Optional dependency groups: `[ml]` and `[advanced]`

## Enabling Research Components

### Method 1: Using the Flake Development Shell (Recommended)

The flake.nix already includes the research dependencies in the development shell:

```bash
# Enter the development environment with all dependencies
nix develop

# This automatically:
# - Sets up poetry2nix environment
# - Includes all optional dependencies (ml, advanced)
# - Provides the correct Python environment
```

The relevant section in flake.nix (lines 34-45):
```nix
poetryEnv = poetry2nix-lib.mkPoetryEnv {
  projectDir = ./.;
  python = pkgs.python312;
  groups = [ "dev" ];
  extras = [ "tui" "voice" "web" "ml" "advanced" ];  # ← Research deps included!
  preferWheels = true;
};
```

### Method 2: Updating the Shell Environment

If you need to modify which dependencies are included:

1. Edit `flake.nix` to ensure the `extras` include research components:
   ```nix
   extras = [ "tui" "voice" "web" "ml" "advanced" ];
   ```

2. Rebuild the development environment:
   ```bash
   nix develop --recreate
   ```

### Method 3: Creating a Dedicated Research Shell

Create a specialized shell for research work:

```nix
# research-shell.nix
{ pkgs ? import <nixpkgs> {} }:

let
  poetry2nix = import (builtins.fetchTarball {
    url = "https://github.com/nix-community/poetry2nix/archive/master.tar.gz";
  }) { inherit pkgs; };
  
  poetryEnv = poetry2nix.mkPoetryEnv {
    projectDir = ./.;
    python = pkgs.python312;
    extras = [ "ml" "advanced" ];  # Only research dependencies
    preferWheels = true;
  };
in
pkgs.mkShell {
  buildInputs = [ poetryEnv ];
  
  shellHook = ''
    echo "🧬 Research Components Environment"
    echo "================================"
    echo "✅ NumPy, NetworkX, DoWhy, SHAP available"
    echo "✅ LanceDB for vector storage"
    echo "✅ All research components enabled"
  '';
}
```

## Verifying Research Components

Once in the Nix development environment:

```bash
# Check if research dependencies are available
python -c "import numpy; print('✅ NumPy:', numpy.__version__)"
python -c "import networkx; print('✅ NetworkX:', networkx.__version__)"
python -c "import shap; print('✅ SHAP:', shap.__version__)"
python -c "import lancedb; print('✅ LanceDB:', lancedb.__version__)"

# Note: DoWhy requires Python <3.12, so it might not be available on Python 3.13
```

## Running with Research Components

```bash
# In the nix develop environment
cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity

# Enable research components
export NIX_HUMANITY_RESEARCH_ENABLED=true

# Run tests
python test_component_integration.py

# Use the system
./bin/ask-nix "install firefox"
```

## Configuration

The research components respect these environment variables:

```bash
# Enable/disable research components
export NIX_HUMANITY_DISABLE_RESEARCH=false  # Default: enabled

# SKG database location
export NIX_HUMANITY_SKG_PATH=./data/skg.db

# Activity tracking (opt-in only)
export NIX_HUMANITY_ACTIVITY_TRACKING=false  # Default: disabled

# Privacy mode
export NIX_HUMANITY_PRIVACY_MODE=aggregate  # Options: strict, aggregate, full
```

## Troubleshooting

### Issue: Import errors for research dependencies

**Solution**: Ensure you're in the Nix development shell:
```bash
nix develop
```

### Issue: DoWhy not available on Python 3.13

**Solution**: DoWhy currently only supports Python <3.12. The mock components will be used automatically as a fallback.

### Issue: Performance concerns

**Solution**: The research components are designed to be lightweight:
- Mock components used when full deps unavailable
- Lazy loading of heavy components
- Async operations for non-blocking behavior

## Architecture Benefits

Using Nix + poetry2nix provides:

1. **Reproducible Environments**: Same dependencies across all systems
2. **No pip required**: Everything managed through Nix
3. **Declarative Configuration**: Dependencies specified in pyproject.toml
4. **Optional Features**: Research components only loaded when needed
5. **Development Isolation**: No system Python pollution

## Summary

The research components are already integrated into the Nix build system through poetry2nix. Simply use:

```bash
nix develop  # Enters environment with all research dependencies
```

No `pip install` needed - Nix handles everything! The system will automatically use mock components if the full research dependencies aren't available, ensuring the core functionality always works.

---

*"Through Nix's declarative power and Poetry's dependency management, we achieve reproducible research environments that serve consciousness-first computing."*