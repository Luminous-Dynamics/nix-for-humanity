# 🌟 Luminous Nix - Natural Language Interface for NixOS

> Transform NixOS from command-line complexity into natural conversation

[![Version](https://img.shields.io/badge/version-0.3.0-blue.svg)](https://github.com/Luminous-Dynamics/luminous-nix/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![NixOS](https://img.shields.io/badge/NixOS-25.11-orange.svg)](https://nixos.org)

## 🎯 What is Luminous Nix?

Luminous Nix makes NixOS accessible to everyone through natural language. Instead of memorizing complex commands, just tell Nix what you want:

```bash
# Traditional NixOS
nix-env -iA nixos.firefox

# With Luminous Nix
ask-nix "install firefox"
ask-nix "I need a text editor"
ask-nix "something's wrong with my system"
```

## ✨ Key Features

### 🗣️ Natural Language Understanding
- Talk to NixOS like you would a helpful assistant
- Understands context and intent
- No more memorizing command syntax

### 🎙️ Voice Interface (v0.3.0)
- Speak commands naturally
- Get voice responses
- Continuous conversation mode

### 🤖 AI-Powered Intelligence
- Complex query understanding
- Local AI models for privacy
- Context-aware responses

### ⚡ Lightning Fast Performance
- 10-100x faster searches with intelligent caching
- Native Python-Nix API integration
- Optimized for NixOS 25.11

### 🛡️ Robust & Safe
- Preview commands before execution
- Rollback capabilities
- Educational error messages

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Luminous-Dynamics/luminous-nix.git
cd luminous-nix

# Run directly
./bin/ask-nix "help"
```

### Basic Usage

```bash
# Install packages
ask-nix "install firefox"

# Search for software
ask-nix "I need a video editor"

# System management
ask-nix "update my system"
ask-nix "clean up disk space"

# Troubleshooting
ask-nix "something's wrong"
```

### Voice Mode

```bash
# Start voice conversation
ask-nix --voice

# Say: "Install Firefox"
# Nix responds with voice!
```

### AI Mode

```bash
# Enable AI understanding for complex queries
LUMINOUS_AI_ENABLED=true ask-nix "set up a Python ML development environment"
```

## 📦 Requirements

### Basic Requirements
- NixOS or Nix package manager
- Python 3.8+

### Optional Features

**Voice Support:**
```bash
pip install SpeechRecognition pyttsx3 pyaudio
```

**AI Support:**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull mistral:7b
```

## 🏗️ Architecture

Luminous Nix features a sophisticated, modular architecture:

- **Intent Recognition Pipeline** - 25+ intent patterns
- **Command Execution Layer** - Safe preview and rollback
- **Error Recovery System** - Intelligent error handling
- **Conversation State Manager** - Multi-turn context
- **Plugin Architecture** - Extensible design
- **Search Cache** - 10-100x performance boost

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Enter development environment
nix develop

# Install dependencies
poetry install

# Run tests
pytest tests/
```

## 📊 Project Status

### Current Version: v0.3.0

✅ **Production Ready Features:**
- Natural language commands
- Package installation/removal
- System search
- Error diagnosis
- Voice interface
- AI integration

🚧 **In Development:**
- Learning system
- GUI interface
- Mobile app

## 🎯 Roadmap

- **v0.4.0** - Learning system that adapts to you
- **v0.5.0** - GUI and system tray integration
- **v1.0.0** - Production release with full documentation

## 💡 Philosophy

Luminous Nix follows the **Trinity Development Model**:
- **Human** - Vision and real-world testing
- **Cloud AI** - Rapid development and problem-solving
- **Local AI** - Domain expertise and privacy

This unique approach enabled us to ship 3 major releases in 48 hours, proving that small teams with AI assistance can build extraordinary software.

## 📖 Documentation

- [Quick Start Guide](QUICKSTART.md)
- [User Documentation](docs/user/README.md)
- [Technical Documentation](docs/technical/README.md)
- [Trinity Development Model](TRINITY_DEVELOPMENT_MODEL.md)

## 🙏 Acknowledgments

Built with love by the Luminous Dynamics team, proving that advanced technology can be accessible to everyone - from command-line experts to grandmothers who just want to talk to their computer.

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

---

**Transform NixOS from complexity to conversation.**

🌊 *Ship fast, iterate faster, make NixOS accessible to all!*