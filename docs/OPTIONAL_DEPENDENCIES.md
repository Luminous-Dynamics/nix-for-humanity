# Optional Dependencies for Luminous Nix v0.6.1+

## Overview

Luminous Nix v0.6.1 introduced several advanced features that can benefit from optional dependencies. However, **all features work without these dependencies** through graceful fallbacks.

## Optional Dependencies

### For ML Features (ML Health Predictions, Pattern Analysis)
- **numpy** - Numerical computing for ML algorithms
- **scikit-learn** - Machine learning algorithms
- **pandas** - Data analysis and manipulation

### For POML Features (Advanced AI Prompting)
- **pyyaml** - YAML parsing for POML templates (falls back to JSON)

### For Visualization
- **matplotlib** - Creating charts and graphs
- **plotly** - Interactive visualizations

## Installation Methods

### Method 1: Using Nix Shell (Recommended for NixOS)

```bash
# Enter shell with optional dependencies
nix-shell shell-with-optional-deps.nix

# Now all optional dependencies are available
python test_v0.6.1_integration.py
```

### Method 2: Add to Your NixOS Configuration

Add to `/etc/nixos/configuration.nix`:

```nix
environment.systemPackages = with pkgs; [
  (python311.withPackages (ps: with ps; [
    numpy
    pyyaml
    scikit-learn
    pandas
    matplotlib
  ]))
];
```

Then rebuild:
```bash
sudo nixos-rebuild switch
```

### Method 3: Using Poetry (Non-NixOS Systems)

```bash
# For non-NixOS systems
poetry install --extras "ml"
```

### Method 4: Direct pip (Virtual Environment)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install optional deps
pip install numpy pyyaml scikit-learn pandas matplotlib
```

## Feature Behavior Without Optional Dependencies

All features have graceful fallbacks:

### ML Health Predictions
- **With numpy/sklearn**: Advanced ML algorithms, anomaly detection, predictive models
- **Without**: Basic statistical analysis, trend detection, simple predictions

### POML Processing
- **With pyyaml**: Full YAML-based POML template support
- **Without**: JSON-based POML templates (100% functional)

### Configuration DNA
- **With numpy**: Advanced genetic algorithms, pattern matching
- **Without**: Basic DNA analysis and breeding

### Interactive Dashboard
- **With matplotlib**: Rich charts and graphs
- **Without**: Text-based visualizations using Rich

## Testing with Optional Dependencies

To verify optional dependencies are available:

```python
# Check numpy
try:
    import numpy as np
    print("✅ numpy available:", np.__version__)
except ImportError:
    print("⚠️ numpy not available - using fallbacks")

# Check yaml
try:
    import yaml
    print("✅ PyYAML available:", yaml.__version__)
except ImportError:
    print("⚠️ PyYAML not available - using JSON fallbacks")

# Check sklearn
try:
    import sklearn
    print("✅ scikit-learn available:", sklearn.__version__)
except ImportError:
    print("⚠️ scikit-learn not available - using basic ML")
```

## Environment Variables

Set these to control optional dependency behavior:

```bash
# Force fallback mode (ignore optional deps even if installed)
export LUMINOUS_NIX_NO_OPTIONAL_DEPS=1

# Verbose optional dep messages
export LUMINOUS_NIX_VERBOSE_DEPS=1
```

## Performance Impact

### With Optional Dependencies
- ML predictions: ~50ms for complex analysis
- POML processing: ~10ms for large templates
- DNA analysis: ~100ms for full genetic comparison

### Without Optional Dependencies (Fallbacks)
- ML predictions: ~30ms for basic analysis
- POML processing: ~15ms using JSON
- DNA analysis: ~80ms for basic comparison

The fallback implementations are often **faster** but provide less sophisticated analysis.

## Recommendation

**For most users**: The fallback implementations are perfectly adequate. You don't need to install optional dependencies unless you specifically need:

1. Advanced ML anomaly detection
2. Complex YAML-based POML templates
3. Scientific visualization features
4. Statistical pattern analysis

**For developers**: Use the `shell-with-optional-deps.nix` when developing/testing advanced features.

## Troubleshooting

### "Module not found" errors
This is normal and expected. The application will automatically use fallback implementations.

### NixOS "externally-managed-environment" error
Use the Nix shell approach or add packages to your system configuration. Never use `pip install --break-system-packages`.

### Poetry dependency conflicts
The optional dependencies are in separate groups. Install only what you need:
```bash
poetry install --extras "ml"  # Just ML deps
poetry install --extras "poml"  # Just POML deps
```

---

*Remember: Luminous Nix is designed to work perfectly without any optional dependencies. They only enhance certain advanced features.*