# 🚀 Advanced Features Guide - Nix for Humanity

*Master the power features that make Nix for Humanity exceptional*

## Overview

This guide covers the advanced features that transform Nix for Humanity from a simple command runner into an intelligent NixOS companion. These features leverage cutting-edge AI and native NixOS integration for unprecedented power and ease of use.

## 📋 Table of Contents

1. [Smart Package Discovery](#smart-package-discovery)
2. [Home Manager Integration](#home-manager-integration)
3. [Configuration.nix Generation](#configurationnix-generation)
4. [Flakes & Development Environments](#flakes--development-environments)
5. [Generation Management & Recovery](#generation-management--recovery)
6. [Error Translation & Resolution](#error-translation--resolution)
7. [Voice Interface](#voice-interface)
8. [Performance Features](#performance-features)
9. [Multi-Persona Adaptation](#multi-persona-adaptation)
10. [Advanced CLI Options](#advanced-cli-options)

---

## 🔍 Smart Package Discovery

Find packages using natural language, without knowing exact names.

### Natural Language Search
```bash
# Describe what you need
ask-nix discover "I need a web browser"
ask-nix discover "something to edit photos"
ask-nix discover "tool for writing markdown"

# Direct discovery commands
ask-nix discover search "music player"
ask-nix discover search "development tools"
```

### Command-to-Package Resolution
When you need a missing command:
```bash
# Find package that provides a command
ask-nix discover command python
ask-nix discover command npm
ask-nix discover command docker

# Natural phrasing works too
ask-nix "which package provides git"
ask-nix "command not found: cargo"
```

### Browse by Category
```bash
# See all categories
ask-nix discover browse

# Browse specific category
ask-nix discover browse --category development
ask-nix discover browse --category multimedia
ask-nix discover browse --category games
```

### Popular Packages
```bash
# See what's trending
ask-nix discover popular

# Filter by category
ask-nix discover popular --category development
```

### Advanced Discovery Tips
- Use aliases: "browser" finds firefox, chromium, brave
- Feature search: "pdf" finds readers, editors, tools
- Fuzzy matching handles typos automatically
- Results ranked by relevance and popularity

---

## 🏠 Home Manager Integration

Manage your personal configuration declaratively.

### Quick Setup
```bash
# Initialize with natural language
ask-nix home init "set up vim and tmux with dark theme"
ask-nix home init "configure my development environment"

# Or use specific options
ask-nix home init --shell zsh --theme dracula
```

### Managing Dotfiles
```bash
# Add specific tools
ask-nix home add vim
ask-nix home add tmux --source ~/my-tmux.conf
ask-nix home add git

# Apply changes
ask-nix home apply
```

### Theme Management
```bash
# Apply themes to your environment
ask-nix home theme dracula
ask-nix home theme nord --apps terminal vim
ask-nix home theme solarized-dark --apps terminal neovim

# Available themes: dracula, nord, solarized-dark, gruvbox
```

### Configuration Sync
```bash
# Sync between machines
ask-nix home sync --from laptop --to desktop
ask-nix home sync --from work --to home --configs vim tmux
```

### Advanced Home Manager
```bash
# List managed configs
ask-nix home list

# Show comprehensive guide
ask-nix home guide

# Preview changes before applying
ask-nix home init "vim setup" --preview
ask-nix home theme nord --preview
```

---

## 📝 Configuration.nix Generation

Generate and manage your system configuration with natural language.

### System Configuration
```bash
# Generate complete configuration
ask-nix config generate "desktop with nvidia and docker"
ask-nix config generate "minimal server with ssh"
ask-nix config generate "development machine with multiple languages"
```

### Add System Features
```bash
# Add services
ask-nix config add-service nginx
ask-nix config add-service postgresql --with-config
ask-nix config add-service docker --enable-nvidia

# Add users
ask-nix config add-user alice --admin --shell zsh
ask-nix config add-user bob --groups docker,wheel
```

### Hardware Configuration
```bash
# Hardware-specific setups
ask-nix config hardware nvidia
ask-nix config hardware bluetooth
ask-nix config hardware printing
```

### Configuration Management
```bash
# Validate configuration
ask-nix config validate

# Show current config
ask-nix config show

# Compare with running system
ask-nix config diff
```

---

## ❄️ Flakes & Development Environments

Modern Nix development with flakes.

### Flake Management
```bash
# Initialize a new flake
ask-nix flake init
ask-nix flake init --template python
ask-nix flake init --template rust

# Update flake inputs
ask-nix flake update
ask-nix flake update nixpkgs
```

### Development Shells
```bash
# Create development environment
ask-nix dev "python with numpy and pandas"
ask-nix dev "rust with wasm toolchain"
ask-nix dev "web development with node and postgresql"

# Enter development shell
ask-nix dev enter
ask-nix dev enter --pure
```

### Flake Templates
```bash
# List available templates
ask-nix flake templates

# Use specific template
ask-nix flake from-template python-ml
ask-nix flake from-template rust-cli
```

### Advanced Flake Features
```bash
# Show flake metadata
ask-nix flake show
ask-nix flake metadata

# Check flake
ask-nix flake check

# Build specific output
ask-nix flake build .#myapp
```

---

## 🔄 Generation Management & Recovery

Manage system generations and recover from issues.

### Generation Operations
```bash
# List all generations
ask-nix generation list
ask-nix generation list --detailed

# Switch to specific generation
ask-nix generation switch 42
ask-nix generation switch previous

# Rollback to previous
ask-nix generation rollback
```

### Generation Cleanup
```bash
# Remove old generations
ask-nix generation clean --older-than 30d
ask-nix generation clean --keep-last 5

# Preview what would be removed
ask-nix generation clean --dry-run
```

### System Recovery
```bash
# Boot into specific generation
ask-nix generation boot 40

# Compare generations
ask-nix generation diff 42 43
ask-nix generation diff current previous

# Find when package was added/removed
ask-nix generation find-change firefox
```

### Advanced Recovery
```bash
# Emergency recovery mode
ask-nix recovery start

# Repair system
ask-nix recovery repair-store
ask-nix recovery rebuild-grub

# Verify system integrity
ask-nix recovery verify
```

---

## 🔧 Error Translation & Resolution

Transform cryptic Nix errors into helpful guidance.

### Automatic Error Translation
When errors occur, Nix for Humanity automatically:
- Translates technical errors to plain English
- Suggests specific solutions
- Offers to fix problems automatically
- Provides learning resources

### Common Error Resolutions
```bash
# Package conflicts
Error: collision between packages
→ Suggestion: Use priority to resolve
→ Fix: ask-nix fix-collision package1 package2

# Broken packages
Error: build failed
→ Suggestion: Try different version
→ Fix: ask-nix use-version package 1.2.3

# Configuration errors
Error: undefined variable
→ Suggestion: Missing import or typo
→ Fix: ask-nix config check-syntax
```

### Proactive Error Prevention
```bash
# Check before applying
ask-nix check
ask-nix check --thorough

# Validate changes
ask-nix validate "install firefox"
ask-nix validate "remove postgresql"
```

---

## 🎤 Voice Interface

Control NixOS with your voice using advanced speech recognition.

### Voice Setup
```bash
# Enable voice interface
ask-nix voice enable

# Test voice recognition
ask-nix voice test

# Configure voice settings
ask-nix voice config --language en-US
ask-nix voice config --wake-word "hey nix"
```

### Voice Commands
Say the wake word, then:
- "Install Firefox"
- "Update my system"
- "Show installed packages"
- "Search for Python"
- "What's my disk usage?"

### Voice Personas
Different voices for different users:
```bash
# Set voice persona
ask-nix voice set-persona grandma-rose
ask-nix voice set-persona maya-fast
ask-nix voice set-persona dr-sarah-precise
```

### Advanced Voice Features
```bash
# Continuous conversation mode
ask-nix voice conversation

# Voice feedback settings
ask-nix voice feedback --verbose
ask-nix voice feedback --minimal

# Custom wake words
ask-nix voice train-wake-word "computer"
```

---

## ⚡ Performance Features

Lightning-fast operations with native NixOS integration.

### Native Python-Nix API
All operations now use direct API calls:
- **10x-1500x faster** than subprocess
- **Instant** generation listing
- **Real-time** progress updates
- **No timeouts** on long operations

### Performance Commands
```bash
# Benchmark operations
ask-nix benchmark
ask-nix benchmark install firefox

# Show performance stats
ask-nix stats
ask-nix stats --detailed
```

### Caching & Optimization
```bash
# Manage package cache
ask-nix cache show
ask-nix cache clean
ask-nix cache optimize

# Preload common operations
ask-nix optimize
ask-nix optimize --aggressive
```

---

## 👥 Multi-Persona Adaptation

Adaptive interface for every user type.

### Available Personas
1. **Grandma Rose** - Simple, friendly, voice-focused
2. **Maya** - Ultra-fast for ADHD, minimal text
3. **Alex** - Optimized for screen readers
4. **Viktor** - Clear English for ESL users
5. **Dr. Sarah** - Precise, technical details
6. **Carlos** - Patient learning mode
7. **David** - Tired-parent friendly
8. **Priya** - Quick and efficient
9. **Jamie** - Privacy-focused
10. **Luna** - Neurodivergent-friendly

### Using Personas
```bash
# Set default persona
ask-nix config set-persona grandma-rose

# Use persona for single command
ask-nix --persona maya "install firefox"
ask-nix --persona dr-sarah "explain generations"

# Test persona
ask-nix persona test maya
```

### Persona Customization
```bash
# Adjust persona settings
ask-nix persona customize maya --speed faster
ask-nix persona customize grandma-rose --voice louder

# Create custom persona
ask-nix persona create my-style --base maya
ask-nix persona edit my-style
```

---

## 🛠️ Advanced CLI Options

Power user features for maximum control.

### Global Options
```bash
# Verbose output
ask-nix -v install firefox
ask-nix -vv search python  # Very verbose

# Quiet mode
ask-nix -q update

# JSON output
ask-nix --json list
ask-nix --json search firefox
```

### Dry Run Mode
```bash
# Preview without executing
ask-nix --dry-run install firefox
ask-nix --dry-run remove nodejs
ask-nix --dry-run update
```

### Advanced Filtering
```bash
# Filter results
ask-nix search python --filter "version>=3.11"
ask-nix list --filter installed --filter user

# Complex queries
ask-nix query "packages where description contains 'editor' and size < 100MB"
```

### Scripting Support
```bash
# Batch operations
ask-nix batch install firefox vim tmux

# Script mode (no interactive prompts)
ask-nix --non-interactive install firefox

# Machine-readable output
ask-nix --format=csv list
ask-nix --format=json search editor
```

### Configuration Management
```bash
# Show all settings
ask-nix config show

# Set preferences
ask-nix config set default.persona maya
ask-nix config set performance.cache true
ask-nix config set ui.color auto

# Export/import config
ask-nix config export > my-config.json
ask-nix config import my-config.json
```

---

## 💡 Pro Tips

### Combining Features
```bash
# Voice + Persona
ask-nix voice enable --persona grandma-rose

# Discovery + Flakes
ask-nix discover "web framework" --add-to-flake

# Home Manager + Themes
ask-nix home init "dark themed terminal" --auto-apply
```

### Power Workflows
```bash
# Full system setup
ask-nix workflow new-machine
ask-nix workflow development-setup
ask-nix workflow server-hardening

# Custom workflows
ask-nix workflow create my-setup
ask-nix workflow run my-setup
```

### Learning Mode
```bash
# Explain while doing
ask-nix --explain install firefox
ask-nix --explain generation rollback

# Tutorial mode
ask-nix tutorial packages
ask-nix tutorial configuration
ask-nix tutorial flakes
```

---

## 🆘 Getting Help

### Built-in Help
```bash
# General help
ask-nix help

# Feature-specific help
ask-nix help discover
ask-nix help home
ask-nix help voice

# Interactive guide
ask-nix guide
```

### Learning Resources
```bash
# Show examples
ask-nix examples
ask-nix examples flakes
ask-nix examples home-manager

# Best practices
ask-nix best-practices
```

---

## 🎯 Quick Reference Card

| Feature | Basic Command | Advanced Usage |
|---------|--------------|----------------|
| **Package Discovery** | `ask-nix discover "web browser"` | `ask-nix discover command npm` |
| **Home Manager** | `ask-nix home init` | `ask-nix home theme dracula --preview` |
| **Config Generation** | `ask-nix config generate` | `ask-nix config add-service nginx` |
| **Flakes** | `ask-nix flake init` | `ask-nix dev "python with ml tools"` |
| **Generations** | `ask-nix generation list` | `ask-nix generation diff 42 43` |
| **Voice** | `ask-nix voice enable` | `ask-nix voice set-persona maya` |
| **Performance** | `ask-nix stats` | `ask-nix benchmark install firefox` |

---

*Master these advanced features to unlock the full power of Nix for Humanity. Remember: complexity is always optional - use what serves you best!*