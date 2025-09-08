# 📚 Luminous Nix - Complete User Guide

*Natural Language Interface for NixOS - Making System Management Accessible to Everyone*

---

## 🌟 What is Luminous Nix?

Luminous Nix transforms NixOS from a command-line labyrinth into a natural conversation. Instead of memorizing complex commands, just say what you want in plain English.

### Before Luminous Nix
```bash
nix-env -qaP | grep firefox  # Search for Firefox
nix-env -iA nixos.firefox    # Install Firefox
nixos-rebuild switch          # Apply changes
```

### With Luminous Nix
```bash
ask-nix "search for a web browser"
ask-nix "install firefox"
ask-nix "update my system"
```

---

## 🚀 Quick Start (5 Minutes)

### Option 1: Standalone Package (Recommended)

```bash
# 1. Download the standalone package
wget https://github.com/Luminous-Dynamics/luminous-nix/releases/download/v0.6.1/luminous-nix-standalone.tar.gz

# 2. Extract it
tar -xzf luminous-nix-standalone.tar.gz
cd luminous-nix

# 3. Install Python dependencies (one time)
pip install -r requirements.txt

# 4. Start using it!
./luminous-nix help
./luminous-nix "install a text editor"
```

### Option 2: From Source (For Developers)

```bash
# 1. Clone the repository
git clone https://github.com/Luminous-Dynamics/luminous-nix
cd luminous-nix

# 2. Enter Nix shell
nix-shell

# 3. Install with Poetry
poetry install

# 4. Run
poetry run ask-nix help
```

---

## 📖 Core Commands

### Basic Usage

```bash
# Get help
ask-nix help

# Search for packages
ask-nix "search text editor"
ask-nix "find markdown editor"
ask-nix "what browsers are available"

# Install packages
ask-nix "install vim"
ask-nix "add firefox to my system"
ask-nix "get me a python development environment"

# System information
ask-nix "list installed packages"
ask-nix "show package info for git"
ask-nix "what version of nixos am i running"

# Configuration
ask-nix "configure nginx web server"
ask-nix "setup postgresql database"
ask-nix "enable ssh service"
```

### Safety Features

**Dry-Run Mode** (Default)
```bash
# Preview what would happen without making changes
ask-nix "install firefox" --dry-run

# Output:
# Would install: firefox-120.0.1
# Configuration changes: /etc/nixos/packages.nix
# [Preview mode - no changes made]
```

**Execute Mode**
```bash
# Actually perform the action
ask-nix "install firefox" --execute

# Or skip confirmation
ask-nix "install firefox" --yes
```

---

## 🎯 Natural Language Examples

### Package Management

```bash
# Searching
"find me a video player"
"search for image editors"
"what music players are available"
"show me development tools"

# Installing
"install visual studio code"
"add docker to my system"
"i need a screenshot tool"
"set up a rust development environment"

# Removing
"remove firefox"
"uninstall vim"
"delete unused packages"

# Updating
"update all packages"
"upgrade my system"
"check for security updates"
```

### Configuration Generation

```bash
# Services
"configure nginx with SSL for example.com"
"set up a minecraft server"
"enable automatic updates"
"configure firewall for web server"

# Development
"create a python development shell"
"set up nodejs environment"
"configure rust development tools"
"prepare machine learning environment"

# System
"enable bluetooth"
"configure printer support"
"set up daily backups"
"enable disk encryption"
```

---

## 🧠 Advanced Features

### 1. Living System Components

The system learns and adapts to your usage patterns:

```bash
# Community Knowledge
ask-nix "show popular configurations"
ask-nix "what do other users install with vim"

# Predictive Solving
ask-nix "fix my wifi"  # Knows common solutions
ask-nix "why is my system slow"  # Suggests optimizations

# Self-Modifying Configs
ask-nix "optimize my configuration"
ask-nix "clean up unused settings"
```

### 2. AI Integration (Optional)

Enable AI for smarter responses:

```bash
# Start Ollama (local AI)
ollama serve

# Use AI-enhanced commands
ask-nix --ai "explain this error message"
ask-nix --ai "how do i set up a web server"
ask-nix --ai "optimize my system for gaming"
```

### 3. Configuration DNA

Analyze and evolve configurations:

```bash
# Analyze current config
ask-nix dna analyze

# Show configuration genetics
ask-nix dna show

# Suggest improvements
ask-nix dna evolve
```

### 4. Multiple Personalities

Adapt the interface to your style:

```bash
# Minimal responses
ask-nix --personality minimal "install vim"

# Friendly and encouraging
ask-nix --personality friendly "update system"

# Technical details
ask-nix --personality technical "show package info"

# Accessible (screen reader optimized)
ask-nix --personality accessible "search editors"
```

---

## 🎨 User Profiles

### For Beginners (Grandma Rose Mode)

```bash
# Extra gentle, no technical terms
ask-nix --persona grandma "install a web browser"

# Output:
# "I'll help you get Firefox on your computer!
#  This will let you browse the internet.
#  Shall I go ahead and set this up for you?"
```

### For Developers

```bash
# Technical mode with details
ask-nix --persona developer "configure development environment"

# Output:
# "Setting up comprehensive dev environment:
#  - Languages: Python 3.11, Node 20, Rust 1.75
#  - Tools: Git, Docker, VSCode
#  - Databases: PostgreSQL, Redis
#  Configuration: /etc/nixos/development.nix"
```

### For System Administrators

```bash
# Professional mode with precise control
ask-nix --persona admin "audit system security"

# Output:
# "Security Audit Report:
#  - Firewall: Enabled (22 rules)
#  - Updates: 3 security patches available
#  - Services: 47 running (2 unnecessary)
#  - Recommendations: [detailed list]"
```

---

## 🛠️ Configuration

### Settings File

Create `~/.config/luminous-nix/config.json`:

```json
{
  "personality": "friendly",
  "confirm_actions": true,
  "use_colors": true,
  "progress_indicators": true,
  "ai_enabled": false,
  "dry_run_default": true
}
```

### Environment Variables

```bash
export LUMINOUS_DRY_RUN=true       # Always preview first
export LUMINOUS_SKIP_CONFIRM=true  # No confirmations
export LUMINOUS_PERSONALITY=minimal # Terse output
export LUMINOUS_AI_ENABLED=true    # Use AI features
export LUMINOUS_VERBOSE=2           # Debug output
```

---

## 🚦 Troubleshooting

### Common Issues

**"Command not found"**
```bash
# Make sure you're in the right directory
cd /path/to/luminous-nix
./luminous-nix help
```

**"Missing dependencies"**
```bash
# Install Python packages
pip install -r requirements.txt
```

**"Permission denied"**
```bash
# Some operations need sudo
sudo ask-nix "update system"
```

**"Timeout errors"**
```bash
# Use background mode for long operations
ask-nix "update system" --background
```

### Getting Help

```bash
# Built-in help
ask-nix help
ask-nix help install
ask-nix help config

# Diagnostic tools
ask-nix doctor           # System check
ask-nix diagnose error   # Error analysis
ask-nix validate config  # Config check
```

---

## 📊 Command Reference

### Flags and Options

| Flag | Description | Example |
|------|-------------|---------|
| `--dry-run` | Preview without executing | `ask-nix install vim --dry-run` |
| `--yes` | Skip confirmations | `ask-nix update --yes` |
| `--execute` | Force execution | `ask-nix install firefox --execute` |
| `--personality` | Set response style | `ask-nix help --personality minimal` |
| `--ai` | Enable AI features | `ask-nix --ai "fix error"` |
| `--verbose` | Detailed output | `ask-nix search --verbose` |
| `--quiet` | Minimal output | `ask-nix install --quiet` |

### Subcommands

| Command | Description | Example |
|---------|-------------|---------|
| `search` | Find packages | `ask-nix search editor` |
| `install` | Install packages | `ask-nix install vim` |
| `remove` | Remove packages | `ask-nix remove firefox` |
| `list` | List installed | `ask-nix list` |
| `info` | Package details | `ask-nix info git` |
| `config` | Generate configs | `ask-nix config nginx` |
| `doctor` | System diagnosis | `ask-nix doctor` |
| `dna` | Config analysis | `ask-nix dna analyze` |

---

## 🌈 Tips and Tricks

### 1. Use Natural Language
Don't overthink it - just say what you want:
- ❌ "nix-env -iA nixos.firefox"
- ✅ "install firefox"
- ✅ "get me a web browser"
- ✅ "i need to browse the internet"

### 2. Start with Dry-Run
Always preview changes first:
```bash
ask-nix "complex system change" --dry-run
# Review the preview
ask-nix "complex system change" --execute
```

### 3. Learn from Patterns
See what others do:
```bash
ask-nix "show popular packages"
ask-nix "common configurations for developers"
```

### 4. Use Personas
Match your expertise level:
- Beginner: `--persona grandma`
- Regular: `--persona user`
- Expert: `--persona developer`
- Admin: `--persona admin`

---

## 🔒 Privacy and Security

- **100% Local**: All processing happens on your machine
- **No Telemetry**: We don't collect any usage data
- **No Cloud**: Works completely offline
- **Open Source**: Audit the code yourself
- **Safe Defaults**: Dry-run mode prevents accidents

---

## 🤝 Contributing

We welcome contributions! See our [Contributing Guide](../CONTRIBUTING.md).

### Report Issues
https://github.com/Luminous-Dynamics/luminous-nix/issues

### Join Discussion
https://github.com/Luminous-Dynamics/luminous-nix/discussions

---

## 📚 Further Reading

- [Technical Architecture](ARCHITECTURE.md)
- [API Reference](API_REFERENCE.md)
- [Development Guide](DEVELOPMENT.md)
- [FAQ](FAQ.md)

---

## 🙏 Acknowledgments

Built with consciousness-first principles, making technology accessible to all beings.

**Remember**: You don't need to be a NixOS expert. Just say what you want, and Luminous Nix handles the complexity.

---

*"Making NixOS as easy as having a conversation."*

**Version**: 0.6.1  
**License**: MIT  
**Website**: https://luminousdynamics.org