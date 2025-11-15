# 🌟 Luminous Nix - Natural Language Interface for NixOS

> Transform NixOS from command-line complexity into natural conversation

[![Version](https://img.shields.io/badge/version-0.6.1-blue.svg)](https://github.com/Luminous-Dynamics/luminous-nix/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![NixOS](https://img.shields.io/badge/NixOS-25.11-orange.svg)](https://nixos.org)
[![Status](https://img.shields.io/badge/status-alpha-yellow.svg)](https://github.com/Luminous-Dynamics/luminous-nix)

> **⚠️ Status Note**: This is an alpha project. Core natural language CLI works well, but many advanced features are still in development. See [FEATURE_STATUS_REALITY.md](FEATURE_STATUS_REALITY.md) for honest assessment of what works vs. what's planned.

## 🎯 What is Luminous Nix?

Luminous Nix makes NixOS accessible to everyone through natural language. Instead of memorizing complex commands, just tell Nix what you want:

```bash
# Traditional NixOS
nix-env -iA nixos.firefox

# With Luminous Nix
ask-nix "install firefox"
ask-nix "search for text editors"
ask-nix "update my system"
```

## ✨ Working Features (v0.1.0-alpha - Alpha)

### ✅ Natural Language Commands
- Install/remove packages with plain English
- Search by description, not just package names
- System updates and maintenance commands
- Profile detection and migration for modern Nix

### ✅ Smart Package Discovery
- Finds packages by what they do, not just their name
- Example: "text editor" finds vim, emacs, nano, etc.
- Typo correction: "fierrfox" → "firefox"
- Category matching for common software types

### ✅ Educational Error Messages
- Some improved error messages over raw Nix
- Basic suggestions for common problems
- Helpful command examples

### ⚠️ Performance Notes
- Search operations take 2-3 seconds (standard Nix speed)
- Install/remove operations require appropriate permissions
- All operations use subprocess (no native API exists)
- Info commands complete in <5 seconds
- No performance improvements over standard Nix commands

### 🚧 In Development
- Voice interface (architecture designed, not implemented)
- Learning system (framework exists, not active)
- Configuration generation (basic templates work)
- TUI interface (has import issues to fix)

### 📋 Planned Features
- subprocess-based operations for performance improvements
- AI-powered features with Ollama
- 10-persona accessibility system
- Predictive maintenance and health monitoring

## 🚀 Quick Start

### Installation

#### Option 1: Quick Install (Recommended)
```bash
# Clone and install
git clone https://github.com/Luminous-Dynamics/luminous-nix.git
cd luminous-nix
./install.sh  # Handles everything automatically
```

#### Option 2: For Developers
```bash
# Clone the repository
git clone https://github.com/Luminous-Dynamics/luminous-nix.git
cd luminous-nix

# Using Nix Flakes (Recommended - 100% Reproducible)
nix develop                              # Enter complete dev environment
nix run .#ask-nix -- "help"              # Or run directly

# Using Poetry
poetry install                           # Install Python dependencies
poetry run ask-nix "help"                # Run the CLI
```

### Basic Usage

```bash
# Install packages
ask-nix "install firefox"

# Search for software
ask-nix "search for video players"
ask-nix "find markdown editors"

# System management
ask-nix "update my system"
ask-nix "garbage collect"

# Advanced AI features (NEW!)
ask-nix rollback analyze "system won't boot"
ask-nix storage analyze
ask-nix security audit

# Preview without executing
LUMINOUS_DRY_RUN=true ask-nix "install firefox"
```

### AI Mode (Optional)

```bash
# Install Ollama first
curl -fsSL https://ollama.com/install.sh | sh
ollama pull mistral:7b

# Enable AI for complex queries
LUMINOUS_AI_ENABLED=true ask-nix "set up a Python development environment"
```

## 📦 Requirements

- NixOS or Nix package manager
- Python 3.8+
- Poetry (for dependency management)

## 🏗️ The Trinity Development Model

This project is built using a unique collaborative approach:

- **Human** (Tristan): Vision, testing, real-world validation
- **Cloud AI** (Claude): Architecture, implementation, rapid iteration
- **Local LLM** (Ollama): NixOS domain expertise and best practices

This model enables solo developers to achieve team-level productivity while maintaining code quality.

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### What We Need Help With

1. **Beta Testing** - Try it and report what breaks
2. **Documentation** - Help make it clearer
3. **NixOS Expertise** - Best practices and edge cases
4. **Python Development** - Core features and tests

## 📊 Project Status

### Current: v0.1.0-alpha Alpha

**Actually Working:**
- ✅ Natural language CLI commands
- ✅ Basic package management (search/install/remove/list)
- ✅ Smart package discovery with typo correction
- ✅ Environment variable configuration
- ✅ Help and info commands

**Not Yet Working:**
- ❌ Voice interface (designed but not implemented)
- ❌ TUI interface (import errors)
- ❌ Learning system (framework only)
- ❌ AI features (require Ollama setup)
- ❌ Native API performance (falls back to subprocess)

**Honest Metrics:**
- Search time: 2-3 seconds (not 2-3 seconds as originally claimed)
- Basic functionality: 40% complete
- Advanced features: 5% complete
- Test coverage: Tests exist but many test non-existent features

## 🎯 Roadmap

- **v0.1.0-alpha** - Fix TUI, implement basic caching
- **v0.1.0-alpha** - Voice interface integration
- **v0.1.0-alpha** - AI features with Ollama
- **v0.1.0-alpha** - Production release when core features actually work

## 📖 Documentation

- [Quick Start Guide](QUICKSTART.md)
- [Trinity Development Model](TRINITY_DEVELOPMENT_MODEL.md)
- [Full Documentation](docs/README.md)
- [Contributing Guide](CONTRIBUTING.md)

## 🙏 Building in Public

Daily updates on progress, challenges, and learnings. Follow along as we make NixOS accessible to everyone!

- [GitHub Discussions](https://github.com/Luminous-Dynamics/luminous-nix/discussions)
- [Issue Tracker](https://github.com/Luminous-Dynamics/luminous-nix/issues)

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

---

**Transform NixOS from complexity to conversation.**

*Building in public, one commit at a time.*
