# 🖥️ Nix for Humanity - Terminal User Interface (TUI)

## Overview

The Nix for Humanity TUI provides a beautiful, accessible terminal interface for natural language NixOS management.

## Current Architecture

### Main TUI (`main.py`)
The unified TUI that combines all features with toggle-able modes:

- **Simple Mode** (default): Clean, focused interface
  - Natural language input
  - Educational error messages
  - Progress indicators
  - Basic status display

- **Enhanced Mode** (Ctrl+E): Full visualizations
  - Consciousness orb visualization
  - Real-time performance metrics
  - Sacred metrics (flow score, coherence)
  - Network status monitoring
  - Learning progress tracking

## Features

### Core Features (Always Available)
- 🗣️ Natural language commands
- 🎓 Educational error handling
- 📊 Progress indicators
- 🚀 Native Python-Nix API integration
- 🎤 Voice interface (when dependencies installed)

### Enhanced Features (Toggle with Ctrl+E)
- 🎭 Consciousness orb with AI state visualization
- 📈 Real-time performance metrics
- ✨ Sacred metrics and flow state tracking
- 🌐 Network connectivity monitoring
- 🧠 Learning progress visualization

## Usage

### Launch the TUI
```bash
# From project root
./launch.sh

# Or directly
python tui/main.py
```

### Keyboard Shortcuts
- `Ctrl+E` - Toggle enhanced/simple mode
- `Ctrl+N` - Native operations demo
- `Ctrl+P` - Progress indicators demo
- `Ctrl+V` - Toggle voice interface
- `Ctrl+L` - Clear conversation
- `F1` - Help
- `F2` - About
- `Ctrl+C` - Quit

### Natural Language Commands
- "install firefox" - Install software
- "update system" - Update NixOS
- "list generations" - Show system history
- "search for text editors" - Find packages
- "my wifi isn't working" - Troubleshooting help

## File Organization

```
tui/
├── main.py              # The unified TUI with toggle-able modes
├── README.md            # This file
└── unified_experience_old.py  # Previous unified TUI (deprecated)
```

### Removed Files
The following files were removed during consolidation as their features are now integrated into `main.py`:
- `main_connected.py` - Educational error handling (integrated)
- `main_with_progress.py` - Progress indicators (integrated)
- `advanced_features_ui.py` - Advanced features demo (integrated)
- `main_tui.py` - Original basic TUI (superseded)

## Development

### Adding New Features
New features should be added to `main.py` with consideration for:
1. Simple mode - features essential for basic usage
2. Enhanced mode - features for power users and visualization

### Dependencies
- `textual` - Terminal UI framework
- `rich` - Terminal formatting
- Backend components from `nix_humanity` package

### Optional Dependencies
- `numpy`, `sounddevice` - For voice interface
- Enhanced orb components (if available)

## Architecture Notes

The TUI follows a single-file architecture with toggle-able complexity levels:
- Reduces confusion from multiple TUI implementations
- Allows users to choose their preferred interface style
- Maintains all features in one coherent codebase
- Progressive enhancement based on available dependencies

## Future Plans

- Add more visualization modes
- Integrate additional consciousness-first features
- Support for custom themes
- Plugin system for extending functionality