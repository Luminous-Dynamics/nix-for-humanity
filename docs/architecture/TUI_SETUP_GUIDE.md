# 🌟 Nix for Humanity TUI Setup Guide

*Getting the beautiful consciousness-first Terminal UI running on NixOS*

## 🎯 Quick Start (For NixOS Users)

Since you're using NixOS with flakes and poetry2nix, all dependencies are managed through Nix. No pip install needed!

### Step 1: Rebuild Development Environment

```bash
# From the project root
cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity

# Rebuild the dev environment with updated flake.nix
./rebuild-dev-env.sh

# Or manually:
direnv reload  # If using direnv
nix develop    # Enter the development shell
```

### Step 2: Test the Setup

```bash
# Run the comprehensive test
./test-nix-tui.sh

# This will verify:
# ✅ Textual is available
# ✅ Rich is available  
# ✅ All TUI components import correctly
# ✅ The app can be created
```

### Step 3: Launch the TUI

Once tests pass, you have multiple ways to run the TUI:

```bash
# Option 1: Nix-provided command (RECOMMENDED)
run-tui-app

# Option 2: Project script
./bin/nix-tui

# Option 3: Python module
python -m nix_humanity.interfaces.tui
```

## 🔮 What You'll See

The TUI features:
- **Consciousness Orb** 🔮 - Living, breathing AI presence at 60fps
- **Adaptive Interface** 🎨 - UI complexity that adjusts to your flow state
- **Beautiful Animations** ✨ - Smooth transitions and particle effects
- **Keyboard Shortcuts**:
  - `Ctrl+Z` - Toggle Zen Mode (minimal UI)
  - `Ctrl+D` - Toggle Debug Info
  - `Ctrl+C` - Sacred exit

## 🐛 Troubleshooting

### "Module not found" Error

If you see import errors:

1. **Ensure you're in Nix shell**:
   ```bash
   echo $IN_NIX_SHELL  # Should show "pure" or "impure"
   ```

2. **Rebuild the environment**:
   ```bash
   direnv reload
   nix develop --rebuild
   ```

3. **Check poetry2nix extras**:
   The flake.nix should include `extras = [ "tui" ... ]`

### TUI Doesn't Launch

1. **Test components individually**:
   ```bash
   python test_tui_components.py
   ```

2. **Check Python path**:
   ```bash
   python -c "import sys; print(sys.path)"
   # Should include project directory
   ```

3. **Verify Textual installation**:
   ```bash
   python -c "import textual; print(textual.__version__)"
   ```

## 📦 Understanding the Setup

### Why Poetry2nix?

- **Reproducible**: Same environment on every machine
- **No pip**: All Python deps managed by Nix
- **Integrated**: Works with NixOS system perfectly

### File Structure

```
nix_humanity/
├── ui/                    # TUI components
│   ├── consciousness_orb.py    # The living orb
│   ├── adaptive_interface.py   # Complexity management
│   ├── main_app.py            # Main TUI application
│   └── visual_state_controller.py
├── interfaces/
│   └── tui.py            # Entry point
└── ...
```

### How It Works

1. **flake.nix** defines poetry2nix environment with TUI extras
2. **pyproject.toml** lists textual as optional dependency
3. **run-tui-app** script launches with proper Python environment
4. **No virtualenv needed** - Nix handles everything!

## 🌊 The Philosophy

This TUI embodies consciousness-first design:
- **Living Presence**: The orb breathes and responds
- **Progressive Disclosure**: Complexity reveals as you grow
- **Flow State Protection**: UI adapts to your cognitive state
- **Terminal Excellence**: Beautiful within constraints

## 🚀 Next Steps

Once the TUI is running:

1. **Explore the Orb** - Watch it breathe and change states
2. **Try Different Modes** - Press Ctrl+Z for Zen mode
3. **Test Commands** - Natural language NixOS interaction
4. **Customize** - Edit colors and animations in consciousness_orb.py

## 📝 Development Notes

If you want to modify the TUI:

```bash
# Edit components
vim nix_humanity/ui/consciousness_orb.py

# Test changes immediately (no rebuild needed)
run-tui-app

# Run component tests
python test_tui_components.py
```

---

*"The best interface is no interface. The best window manager is one that manages your consciousness, not just your windows."*

🌟 Welcome to consciousness-first computing! 🌟