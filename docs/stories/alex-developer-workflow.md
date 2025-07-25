# 👨‍💻 User Story: Alex Sets Up Development Environment

**Persona**: Alex (28)
**Goal**: Set up Python development environment
**Technical Level**: Expert (Blind developer)
**Preferred Input**: Keyboard/Screen reader

## The Story

Alex just started a new data science project. As a blind developer, he relies on his screen reader and keyboard navigation. He needs a Python environment with specific data science tools.

## The Conversation

**Alex** (typing): "set up python for data science with jupyter"

**Nix for Humanity**: "I'll set up a comprehensive Python data science environment for you. Based on your development history, I'll include:
- Python 3.11
- Jupyter with accessibility extensions
- NumPy, Pandas, Matplotlib
- Screen-reader-friendly notebook extensions

Would you like me to use a flake.nix for reproducibility?"

**Alex**: "yes, flake with direnv integration"

**Nix for Humanity**: "Creating a flake.nix with direnv integration. I'll include the accessible Jupyter configuration you typically use."

```nix
# Generated flake.nix
{
  description = "Data science development environment";
  
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };
  
  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python311
            python311Packages.jupyter
            python311Packages.numpy
            python311Packages.pandas
            python311Packages.matplotlib
            python311Packages.notebook
            # Accessibility tools
            python311Packages.jupyter-a11y
          ];
          
          shellHook = ''
            echo "Data science environment activated"
            echo "Jupyter with accessibility extensions ready"
            echo "Use 'jupyter notebook --no-browser' for screen reader mode"
          '';
        };
      });
}
```

**Nix for Humanity**: "Flake created. Also creating .envrc for automatic activation:"

```bash
# .envrc
use flake
```

**Alex**: "add scikit-learn and pytorch"

**Nix for Humanity**: "Adding scikit-learn and PyTorch to your flake:"

*[Updates flake.nix with the additional packages]*

**Nix for Humanity**: "Updated. The environment will now include scikit-learn and PyTorch. Running 'direnv allow' to activate."

**Alex**: "create notebook template with accessible output"

**Nix for Humanity**: "Creating an accessible notebook template with screen reader friendly settings:"

```python
# accessible_template.ipynb
{
 "cells": [
  {
   "cell_type": "code",
   "source": [
    "# Accessibility configuration\n",
    "import matplotlib.pyplot as plt\n",
    "import pandas as pd\n",
    "\n",
    "# Configure matplotlib for text descriptions\n",
    "plt.rcParams['figure.alt'] = True\n",
    "\n",
    "# Set pandas display for screen readers\n",
    "pd.set_option('display.max_rows', 10)\n",
    "pd.set_option('display.max_columns', None)\n"
   ]
  },
  {
   "cell_type": "markdown",
   "source": [
    "# Data Science Project\n",
    "\n",
    "## Navigation\n",
    "- Cell 1: Configuration\n",
    "- Cell 2: Data loading\n",
    "- Cell 3: Analysis\n"
   ]
  }
 ]
}
```

**Nix for Humanity**: "Template created with:
- Matplotlib text alternatives enabled
- Pandas output limited for easier navigation  
- Clear cell navigation structure
- Screen reader friendly formatting

Your development environment is ready!"

## What Happened Behind the Scenes

1. **User Recognition**: System knew Alex from previous interactions
2. **Accessibility Defaults**: Automatically included screen-reader-friendly tools
3. **Workflow Preference**: Remembered Alex prefers flakes and direnv
4. **Proactive Accessibility**: Added accessible configurations without being asked
5. **Expert Communication**: Used technical terms appropriately

## Learning for Next Time

The system learned:
- Alex works on data science projects
- He needs accessibility extensions for Jupyter
- He prefers flake-based environments
- He uses direnv for automatic activation
- He often adds ML libraries after initial setup

Next interaction might be:
**Alex**: "new ml project"
**System**: "Creating flake.nix with your usual data science stack including PyTorch and accessible Jupyter. Should I include the GPU support you used last time?"

## Technical Implementation

The system:
1. Generated valid Nix flake syntax
2. Included accessibility tools automatically
3. Created proper direnv integration
4. Set up screen-reader-friendly configurations
5. Provided keyboard-navigable notebook structure

## Success Metrics

- ✅ Professional developer workflow supported
- ✅ Accessibility seamlessly integrated
- ✅ No redundant explanations for expert user
- ✅ Anticipated needs based on history
- ✅ Reproducible environment created

## Key Takeaways

This story demonstrates:
1. **Adaptive communication** - Expert users get technical details
2. **Accessibility by default** - Not an afterthought
3. **Learning from patterns** - Remembers user preferences
4. **Proactive assistance** - Suggests what's usually needed
5. **Equal access** - Blind developers are first-class users

## Accessibility Features Demonstrated

1. **Screen Reader Optimization**
   - Clear text responses
   - Structured output
   - No reliance on visual elements

2. **Keyboard Navigation**
   - All interactions keyboard-accessible
   - No mouse-required operations
   - Clear navigation structure

3. **Output Formatting**
   - Limited data display for easier reading
   - Text alternatives for visualizations
   - Semantic structure in notebooks

---

*"Expert developers deserve expert tools that respect their expertise and accessibility needs."*