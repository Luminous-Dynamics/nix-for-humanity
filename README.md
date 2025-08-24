# Luminous Nix - Natural Language Interface for NixOS

> *Making NixOS accessible through natural conversation*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![NixOS 24.05+](https://img.shields.io/badge/NixOS-24.05%2B-blue)](https://nixos.org)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-green)](https://python.org)
[![Development Status](https://img.shields.io/badge/Status-Alpha-orange)](https://github.com/Luminous-Dynamics/luminous-nix/releases)

## What is Luminous Nix?

Luminous Nix is an experimental natural language interface for NixOS that lets you manage your system using plain English instead of complex commands. It's designed to make NixOS accessible to everyone, from beginners to power users.

**Instead of:**
```bash
nix-env -iA nixos.firefox
nix-env -qaP | grep -i markdown
```

**Just say:**
```bash
ask-nix "install firefox"
ask-nix "find a markdown editor"
```

## 🚧 Project Status: Alpha

This is an **alpha release** built as an experimental prototype in 2 weeks. It demonstrates what's possible when combining natural language processing with NixOS management.

### What Works
- ✅ Natural language package installation and search
- ✅ Configuration file generation for common scenarios
- ✅ Educational error messages that explain what went wrong
- ✅ Basic system diagnostics and fixes
- ✅ Terminal UI for visual interaction

### What's Limited
- 🚧 Voice interface (architecture complete, integration pending)
- 🚧 Advanced persona system (partially implemented)
- 🚧 Some NixOS features not yet supported
- 🚧 Performance optimizations still needed
- 🚧 Test coverage needs improvement (currently ~8% real coverage)

## Quick Start

### Prerequisites
- NixOS 24.05 or later
- Python 3.11+
- Poetry for dependency management
- Ollama (optional, for AI features)

### Installation

```bash
# Clone the repository
git clone https://github.com/Luminous-Dynamics/luminous-nix.git
cd luminous-nix

# Enter the Nix development shell (provides system dependencies)
nix-shell

# Install Python dependencies
poetry install

# Run the CLI
poetry run ask-nix "help"
```

### Basic Usage

```bash
# Install packages
poetry run ask-nix "install firefox"

# Search for software
poetry run ask-nix "find markdown editors"

# Get help with configuration
poetry run ask-nix "how do I enable docker?"

# Run system diagnostics
poetry run ask-nix fix
```

## How It Works

Luminous Nix uses several technologies to understand and execute your commands:

1. **Natural Language Processing** - Interprets your plain English requests
2. **Intent Recognition** - Determines what you want to do
3. **Command Generation** - Creates the appropriate Nix commands
4. **Safety Validation** - Ensures commands are safe before execution
5. **Educational Feedback** - Explains what's happening and why

## AI-Assisted Development

### Transparency Notice

This project was developed using an innovative "Sacred Trinity" approach:
- **Human Developer** (Tristan): Vision, architecture, testing
- **Claude AI**: Code generation and problem-solving partner
- **Local LLM**: NixOS domain expertise

This collaborative development model allowed a solo developer to create a functional prototype in 2 weeks for approximately $200/month in AI tool costs. We believe in transparency about our development process as it represents a new paradigm in software creation.

## Features

### Implemented
- Natural language command interpretation
- Package installation and search
- Configuration file generation
- Error message translation
- System health diagnostics
- **Adaptive consciousness** - Fluidly adjusts to your expertise level
- Terminal UI with visualizations

### Planned
- Voice interface for hands-free operation
- Advanced learning system that improves with use
- Community-driven pattern sharing
- Integration with Home Manager
- Support for Nix Flakes
- Multi-language support

## Architecture

The project follows a modular architecture:

```
src/luminous_nix/
├── core/           # Core engine and orchestration
├── nlp/            # Natural language processing
├── consciousness/  # AI integration layer
├── persistence/    # Data storage and learning
├── ui/             # Terminal user interface
├── voice/          # Voice interface (in development)
└── cli/            # Command-line interface
```

## Contributing

We welcome contributions! This is an experimental project exploring new ways of interacting with NixOS.

### Areas We Need Help
- Testing on different NixOS configurations
- Expanding NixOS command coverage
- Improving natural language understanding
- Documentation and tutorials
- Bug reports and feature suggestions

See [CONTRIBUTING.md](docs/03-DEVELOPMENT/01-CONTRIBUTING.md) for guidelines.

## Philosophy

Luminous Nix follows a "consciousness-first" design philosophy that prioritizes:
- **Adaptive Intelligence** - The system learns from your interactions and adapts fluidly
- **No Fixed Personas** - Instead of choosing "grandma mode" or "developer mode", the interface naturally adjusts to your expertise level
- **Progressive Revelation** - Advanced features appear as you're ready for them
- **User agency** - You're always in control
- **Transparency** - Clear about what commands will run
- **Education** - Learn while you use it
- **Accessibility** - Designed for all skill levels
- **Privacy** - Everything runs locally on your machine

The interface is like water - it takes the shape of its container (your needs) without forcing any particular form.

## Known Issues

- Circular import warnings may appear (don't affect functionality)
- Some complex NixOS operations not yet supported
- First run downloads AI models (300MB-2GB depending on selection)
- Performance varies based on hardware and model selection

## Roadmap

### v0.1.0-alpha (Current)
- ✅ Basic natural language interface
- ✅ Core NixOS operations
- ✅ Terminal UI
- ✅ Error translation

### v0.2.0 (Planned)
- Voice interface integration
- Expanded NixOS command coverage
- Performance optimizations
- Improved test coverage

### v1.0.0 (Future)
- Production-ready stability
- Full NixOS feature support
- Plugin system
- Community features

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Tristan Stoltz** - Project creator and vision
- **Claude (Anthropic)** - AI development partner
- **NixOS Community** - Inspiration and foundation
- All contributors and early testers

## Support

- **Issues**: [GitHub Issues](https://github.com/Luminous-Dynamics/luminous-nix/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Luminous-Dynamics/luminous-nix/discussions)
- **Documentation**: [Full Documentation](docs/README.md)

---

**Note**: This is an experimental alpha release. While functional for basic operations, it's not recommended for production use without thorough testing in your environment.

**Development Model**: This project demonstrates AI-assisted development where a human developer collaborates with AI tools to accelerate software creation. We believe in transparency about our methods and invite discussion about this new paradigm.