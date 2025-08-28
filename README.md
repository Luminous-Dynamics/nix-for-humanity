# 🌟 Luminous Nix - Natural Language Interface for NixOS

> Transform NixOS from command-line complexity into natural conversation

[![Version](https://img.shields.io/badge/version-0.3.1-blue.svg)](https://github.com/Luminous-Dynamics/luminous-nix/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![NixOS](https://img.shields.io/badge/NixOS-25.11-orange.svg)](https://nixos.org)
[![Status](https://img.shields.io/badge/status-alpha-yellow.svg)](https://github.com/Luminous-Dynamics/luminous-nix)

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

## ✨ Working Features (v0.3.1)

### ✅ Natural Language Commands
- Install/remove packages with plain English
- Search by description, not just package names
- System updates and maintenance commands

### ✅ Smart Package Discovery
- Finds packages by what they do, not just their name
- Example: "I need a video editor" finds kdenlive, openshot, etc.

### ✅ Configuration Generation  
- Generate NixOS configurations from descriptions
- Create development environments easily
- Flake management support

### ✅ Educational Error Messages
- Errors that teach you NixOS as you go
- Helpful suggestions for common problems
- Recovery strategies included

### ✅ Performance Breakthrough
- 10x-1500x faster with native Python-Nix API
- Intelligent caching system
- No subprocess overhead

### 🚧 In Progress
- Voice interface (architecture complete, integration pending)
- Learning system (framework ready, training data needed)
- Full 10-persona system (5 working, 5 in development)

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Luminous-Dynamics/luminous-nix.git
cd luminous-nix

# Option 1: Nix Flakes with Poetry2nix (Recommended - 100% Reproducible)
nix develop                              # Enter complete dev environment
nix run .#ask-nix -- "help"              # Or run directly

# Option 2: Traditional Poetry Setup
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

### Current: v0.3.1 Alpha

**Working:**
- ✅ Natural language commands
- ✅ Package management (install/remove/search)
- ✅ Configuration generation
- ✅ Smart error handling
- ✅ Basic persona system

**In Progress:**
- 🚧 Voice interface
- 🚧 Learning system
- 🚧 Complete test coverage

**Metrics:**
- 68% launch ready
- 60% features working
- 2.9% test coverage (working on it!)
## 🎯 Roadmap

- **v0.4.0** - Complete voice interface integration
- **v0.5.0** - Learning system that adapts to your usage
- **v1.0.0** - Production release with full test coverage

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