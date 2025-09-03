# 📚 Luminous Nix User Guide

*Natural Language Interface for NixOS - Making System Management Accessible*

## 🚀 Quick Start

### Installation

```bash
# Option 1: Standalone Binary (Recommended)
curl -L https://github.com/Luminous-Dynamics/luminous-nix/releases/latest/download/luminous-nix -o luminous-nix
chmod +x luminous-nix
./luminous-nix help

# Option 2: Python Package
pip install luminous-nix

# Option 3: Development Version
git clone https://github.com/Luminous-Dynamics/luminous-nix
cd luminous-nix
poetry install
poetry run ask-nix help
```

### First Commands

```bash
# Search for packages using natural language
ask-nix "find a markdown editor"
ask-nix "search for video players"

# Install packages
ask-nix "install firefox"
ask-nix "install development tools"

# Get help
ask-nix help
ask-nix --version
```

## 🎯 Core Features

### 1. Natural Language Package Management

Luminous Nix understands what you want, not just exact package names.

#### Searching for Packages

```bash
# Natural descriptions
ask-nix "find text editor"           # Shows vim, emacs, vscode, etc.
ask-nix "search for music players"   # Shows spotify, vlc, rhythmbox, etc.
ask-nix "web browsers"               # Shows firefox, chromium, brave, etc.

# Typo correction
ask-nix "install fierfox"            # Corrects to firefox
ask-nix "search for pythn"           # Corrects to python

# Category search
ask-nix "development tools"          # Shows compilers, editors, debuggers
ask-nix "productivity apps"          # Shows office, notes, calendars
```

#### Installing Packages

```bash
# Basic installation
ask-nix "install firefox"
ask-nix "install git vim tmux"

# With descriptions
ask-nix "install a web browser"      # Suggests firefox, chromium, etc.
ask-nix "install code editor"        # Suggests vscode, vim, emacs, etc.

# Dry run (preview without installing)
ask-nix "install firefox" --dry-run
```

#### Listing and Info

```bash
# List installed packages
ask-nix list
ask-nix "show installed packages"

# Get package information
ask-nix info firefox
ask-nix "tell me about vscode"
```

### 2. Configuration Generation 🆕

Generate complete NixOS configurations from natural language descriptions.

#### Basic System Configurations

```bash
# Desktop systems
ask-nix "generate config for KDE desktop with firefox and development tools"
ask-nix "create GNOME workstation for user alice"
ask-nix "make config for minimal system with i3 window manager"

# Server configurations
ask-nix "configure web server with nginx and postgresql"
ask-nix "set up database server with mysql and firewall"
ask-nix "create docker host with monitoring tools"
```

#### Understanding the Generator

The configuration generator understands:

- **Desktop Environments**: GNOME, KDE, XFCE, i3, Sway
- **Web Servers**: nginx, Apache, Caddy
- **Databases**: PostgreSQL, MySQL/MariaDB, Redis, MongoDB
- **Development Tools**: Docker, VSCode, various languages
- **Services**: SSH, firewall, printing, bluetooth
- **Users**: Creation with admin privileges

#### Examples

```bash
# Complex configuration
ask-nix "generate config for development workstation with KDE desktop, \
         docker, vscode, postgresql, and user john with admin access"

# This generates a complete configuration.nix with:
# - KDE Plasma desktop
# - Docker virtualization
# - VSCode editor
# - PostgreSQL database
# - User 'john' with sudo privileges
# - All necessary system packages

# Save the configuration
ask-nix "generate config for web server" > /etc/nixos/configuration.nix

# Validate before applying
ask-nix "validate /etc/nixos/configuration.nix"

# Explain existing configuration
ask-nix "explain /etc/nixos/configuration.nix"
```

### 3. Flake Management 🆕

Create modern Nix flakes for development environments using natural language.

#### Creating Development Environments

```bash
# Python projects
ask-nix flake create "python web app with django and postgresql"
ask-nix flake create "python data science with jupyter pandas numpy"
ask-nix flake create "python ml project with tensorflow and pytorch"

# JavaScript/Node.js projects  
ask-nix flake create "nodejs react app with typescript and jest"
ask-nix flake create "express api with mongodb and docker"
ask-nix flake create "next.js full stack app with prisma"

# Rust projects
ask-nix flake create "rust cli tool with clap and serde"
ask-nix flake create "rust web server with actix and diesel"

# Go projects
ask-nix flake create "go microservice with gin and docker"
ask-nix flake create "go cli with cobra and viper"

# Multi-language
ask-nix flake create "full stack app with react frontend and python backend"
```

#### Using Flakes

```bash
# After creating a flake
cd my-project
ask-nix flake create "python web development"

# Enter the development environment
nix develop

# All tools are now available!
python --version  # Python 3.11
django-admin      # Django CLI
psql              # PostgreSQL client
```

#### Converting Legacy Files

```bash
# Convert old shell.nix to modern flake
ask-nix flake convert

# Convert with backup
ask-nix flake convert --backup

# The tool automatically:
# - Detects packages from shell.nix
# - Creates equivalent flake.nix
# - Preserves all dependencies
# - Adds proper inputs and outputs
```

#### Flake Commands

```bash
# Validate a flake
ask-nix flake validate

# Show flake information
ask-nix flake info

# List available templates
ask-nix flake templates

# Get language-specific examples
ask-nix flake language python
ask-nix flake language rust
ask-nix flake language nodejs

# Show guide
ask-nix flake guide
```

### 4. Beautiful TUI Interface

Launch an interactive terminal interface for visual package management.

```bash
# Launch the TUI
ask-nix tui
# or
nix-tui
```

#### TUI Features

- **Search packages** with real-time filtering
- **Browse categories** visually
- **View package details** with descriptions
- **Install/remove** with confirmation dialogs
- **System status** monitoring
- **Keyboard navigation** (arrow keys, vim bindings)

#### TUI Shortcuts

- `/` - Search mode
- `i` - Install selected package
- `r` - Remove selected package
- `?` - Show help
- `q` - Quit
- `Tab` - Switch panels
- `Enter` - Select/confirm

### 5. Smart Features

#### Typo Correction

```bash
ask-nix "install fierfix"     # → Suggests: firefox
ask-nix "search for vcsode"   # → Suggests: vscode
ask-nix "install kubernets"   # → Suggests: kubernetes
```

#### Semantic Understanding

```bash
ask-nix "install something to edit photos"     # → Suggests: gimp, krita
ask-nix "i need to watch videos"              # → Suggests: vlc, mpv
ask-nix "tools for web development"           # → Suggests: nodejs, npm, webpack
```

#### Safety Features

- **Dry run by default** for system changes
- **Confirmation prompts** for destructive actions
- **Validation** before applying configurations
- **Rollback information** after changes
- **Clear error messages** with suggestions

## 📖 Advanced Usage

### Command-Line Options

```bash
# Dry run (preview changes)
ask-nix "install firefox" --dry-run

# Skip confirmation
ask-nix "install git" --yes

# Verbose output
ask-nix "search editors" --verbose

# Use specific channel
ask-nix "install firefox" --channel unstable

# JSON output
ask-nix list --json

# Help for any command
ask-nix help install
ask-nix help search
ask-nix help flake
```

### Configuration File

Create `~/.config/luminous-nix/config.yaml`:

```yaml
# Default settings
defaults:
  dry_run: false
  verbose: false
  channel: "stable"

# Package aliases
aliases:
  dev: ["git", "vim", "tmux", "htop"]
  web: ["firefox", "chromium"]
  
# Search preferences  
search:
  fuzzy_threshold: 0.8
  max_results: 20
  
# TUI settings
tui:
  theme: "dark"
  vim_bindings: true
```

### Environment Variables

```bash
# Enable debug output
export LUMINOUS_DEBUG=1

# Set default channel
export NIX_CHANNEL=unstable

# Disable colors
export NO_COLOR=1

# Custom config location
export LUMINOUS_CONFIG=/path/to/config.yaml
```

## 🔧 Troubleshooting

### Common Issues

#### "Package not found"
```bash
# Update package cache
ask-nix cache update

# Search with broader terms
ask-nix "search browser" instead of "search firefox"
```

#### "Permission denied"
```bash
# Some operations need sudo
sudo ask-nix "system update"

# Or use nix-shell for user installs
nix-shell -p firefox
```

#### "Command not recognized"
```bash
# Check version
ask-nix --version

# Update to latest
pip install --upgrade luminous-nix
```

### Getting Help

```bash
# Built-in help
ask-nix help
ask-nix help [command]

# Show examples
ask-nix examples

# Version and system info
ask-nix --version
ask-nix doctor  # System diagnostic
```

## 🌟 Tips and Tricks

### Power User Tips

1. **Chain commands** with shell operators:
   ```bash
   ask-nix "search editor" | grep vim
   ask-nix list --json | jq '.packages[]'
   ```

2. **Create aliases** for common operations:
   ```bash
   alias nxs='ask-nix search'
   alias nxi='ask-nix install'
   alias nxl='ask-nix list'
   ```

3. **Use in scripts**:
   ```bash
   #!/bin/bash
   # Install development environment
   ask-nix "install git vim tmux" --yes
   ask-nix flake create "python development"
   ```

4. **Batch operations**:
   ```bash
   # Install multiple packages from file
   cat packages.txt | xargs ask-nix install --yes
   ```

### Best Practices

1. **Always preview changes**: Use `--dry-run` for system modifications
2. **Keep flake.lock committed**: For reproducible environments
3. **Use semantic searches**: Describe what you want, not package names
4. **Leverage templates**: Start from templates and customize
5. **Regular updates**: Keep package cache fresh with `cache update`

## 📚 Examples Gallery

### System Setup Examples

```bash
# New developer machine
ask-nix "generate config for developer workstation with everything"

# Minimal server
ask-nix "create minimal headless server with ssh"

# Gaming desktop
ask-nix "configure gaming desktop with steam and discord"

# Home media server
ask-nix "set up media server with plex and transmission"
```

### Development Environment Examples

```bash
# Full-stack web development
ask-nix flake create "full stack with react, node, postgresql, redis"

# Data science workbench
ask-nix flake create "data science with jupyter, pandas, scikit-learn, tensorflow"

# DevOps toolkit
ask-nix flake create "devops environment with docker, kubernetes, terraform, ansible"

# Mobile development
ask-nix flake create "mobile dev with react native and android tools"
```

## 🚀 Next Steps

1. **Try the basics**: Start with simple package searches
2. **Create a flake**: Set up your first development environment
3. **Generate a config**: Build a custom system configuration
4. **Explore the TUI**: Use the visual interface
5. **Join the community**: Share your experience and get help

## 📞 Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/Luminous-Dynamics/luminous-nix/issues)
- **Discussions**: [Ask questions and share tips](https://github.com/Luminous-Dynamics/luminous-nix/discussions)
- **Documentation**: [Full documentation](https://luminous-dynamics.github.io/luminous-nix)

---

*Luminous Nix - Making NixOS accessible to everyone through the power of natural language* 🌟