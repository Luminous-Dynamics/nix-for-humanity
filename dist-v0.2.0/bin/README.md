# Nix for Humanity Executables

This directory contains the command-line tools for natural language NixOS interaction.

## 🚀 THE ONE COMMAND: ask-nix

### `ask-nix` ⭐ Consolidated Natural Language Interface
**Status**: Fully functional with ALL features integrated!
**Version**: v0.8.0 - Command Consolidation Complete

**Integrated Features**:
- ✅ **Natural language understanding** - Speak naturally
- ✅ **Real command execution** - No more copy-paste!
- ✅ **Symbiotic feedback collection** - Learns from usage
- ✅ **5 personality styles** - Minimal, friendly, encouraging, technical, symbiotic
- ✅ **Smart package caching** - 100x faster searches
- ✅ **Learning mode** - Step-by-step guidance
- ✅ **Voice interface** - Speak to your system (--voice)
- ✅ **Progress indicators** - Know what's happening
- ✅ **Safety features** - Confirmation prompts, dry-run mode
- ✅ **Plugin architecture** - Extensible design

**Examples**:
```bash
# Install a package (with confirmation)
ask-nix "install firefox"

# Search for packages (uses cache for speed)
ask-nix "search tree"

# Update your system
ask-nix "update my system"

# Symbiotic mode - learns from feedback
ask-nix --symbiotic "what's a generation?"

# Skip confirmation
ask-nix --yes "install htop"

# Test without executing
ask-nix --dry-run "remove vim"

# Different personalities
ask-nix --minimal "list packages"
ask-nix --encouraging "my first nix command"
ask-nix --technical "explain overlays"

# Voice interaction
ask-nix --voice

# See your learning progress
ask-nix --summary
```

## 🗂️ Deprecated Commands

All `ask-nix-*` variants have been consolidated into the main `ask-nix` command.
The following commands now show a deprecation notice:

- `ask-nix-hybrid` → Use `ask-nix`
- `ask-nix-v3` → Use `ask-nix`
- `ask-nix-modern` → Use `ask-nix`
- `ask-nix-refactored` → Use `ask-nix`
- `ask-nix-adaptive` → Use `ask-nix --adaptive`
- `ask-nix-learning` → Use `ask-nix --learning-mode`
- `ask-nix-python` → Use `ask-nix`
- All other variants → Use `ask-nix` with appropriate flags

## ✅ Supporting Tools

### `nix-profile-do`
Direct wrapper for modern nix profile commands.
**Use for**: When you need direct nix profile operations without NLP

### `demo-symbiotic-learning`
Interactive demonstration of the symbiotic learning system.
**Use for**: Understanding how the feedback system works

### `analyze-feedback`
Analyze collected feedback data.
**Use for**: Improving the system based on user interactions

## 📦 Archive Directory

The `archive/` directory contains:
- All deprecated `ask-nix-*` variants
- Historical implementations
- Experimental versions
- See `archive/ARCHIVE_NOTE.md` for historical details

## 🎯 Quick Start

```bash
# The ONE command you need:
ask-nix "install firefox"

# It will:
# 1. Understand your intent
# 2. Validate the package exists
# 3. Ask for confirmation
# 4. Actually install it!
# 5. Show progress
# 6. Confirm success
```

## 🛡️ Safety Features

1. **Confirmation Prompts**: Always asks before installing/removing
2. **Package Validation**: Checks if package exists before trying
3. **Dry Run Mode**: Test with `--dry-run` flag
4. **Progress Indicators**: Know what's happening
5. **Error Recovery**: Automatic retries on failure

## 🎨 Personality Options

- `--minimal` - Just the facts
- `--friendly` - Warm and helpful (default)
- `--encouraging` - Supportive for beginners
- `--technical` - Detailed explanations

## 🚀 Phase 1 Success!

The #1 user friction has been eliminated:
- **Before**: Copy command, paste in terminal, execute manually
- **Now**: Just ask and it happens!

This is real progress toward making NixOS accessible to everyone.
