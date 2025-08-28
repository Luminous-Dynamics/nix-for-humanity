# 🍳 Luminous Nix Cookbook

*Common recipes for natural language NixOS*

## 🚀 Quick Start Recipes

### First Time Setup
```bash
# Check it works
ask-nix "help"

# See what you have installed
ask-nix "list my packages"

# Your first install
ask-nix "install htop"
```

## 💻 Development Environments

### Web Development
```bash
# Frontend development
ask-nix "install nodejs and npm"
ask-nix "create react development environment"

# Full stack
ask-nix "i need nodejs, postgresql, and redis"

# Quick project setup
ask-nix "set up a typescript project"
```

### Python Development
```bash
# Data science stack
ask-nix "install jupyter pandas numpy matplotlib"

# Web development
ask-nix "install python with django and postgresql"

# Machine learning
ask-nix "create ml environment with pytorch"
```

### Rust Development
```bash
# Basic Rust
ask-nix "install rust and cargo"

# With tools
ask-nix "set up rust with clippy and rustfmt"
```

## 🎮 Gaming Setup

### Steam Gaming
```bash
# Basic Steam
ask-nix "install steam"

# With extras
ask-nix "install steam, discord, and obs"

# Retro gaming
ask-nix "install retroarch and emulators"
```

## 🎨 Creative Work

### Image Editing
```bash
# Photo editing
ask-nix "install gimp for photo editing"

# Vector graphics
ask-nix "i need inkscape for logos"

# Quick edits
ask-nix "install imagemagick"
```

### Video Production
```bash
# Video editing
ask-nix "install kdenlive or openshot"

# Streaming
ask-nix "set up obs studio for streaming"

# Conversion
ask-nix "install ffmpeg and handbrake"
```

### Audio Production
```bash
# Recording
ask-nix "install audacity"

# Music production
ask-nix "set up ardour for music"
```

## 📝 Office & Productivity

### Office Suite
```bash
# Full office
ask-nix "install libreoffice"

# Just writing
ask-nix "i need a markdown editor"

# Note taking
ask-nix "install obsidian or joplin"
```

### Communication
```bash
# Chat apps
ask-nix "install discord and slack"

# Email
ask-nix "install thunderbird"

# Video calls
ask-nix "i need zoom or teams"
```

## 🔧 System Administration

### Monitoring
```bash
# System monitoring
ask-nix "install htop btop and iotop"

# Network monitoring
ask-nix "install nethogs and iftop"

# Logs
ask-nix "tools for reading logs"
```

### Security
```bash
# Password manager
ask-nix "install bitwarden or keepassxc"

# VPN
ask-nix "install wireguard tools"

# Firewall
ask-nix "configure firewall"
```

## 🌐 Web Browsers

### Different Browsers
```bash
# Firefox
ask-nix "install firefox"

# Chromium
ask-nix "install chromium or brave"

# Terminal browser
ask-nix "install lynx for terminal browsing"
```

## 🗄️ Databases

### SQL Databases
```bash
# PostgreSQL
ask-nix "install postgresql with pgadmin"

# MySQL/MariaDB
ask-nix "install mariadb"

# SQLite
ask-nix "install sqlite with browser"
```

### NoSQL
```bash
# Document stores
ask-nix "install mongodb"

# Key-value
ask-nix "install redis"

# Graph
ask-nix "install neo4j"
```

## 🐳 Containers & Virtualization

### Docker
```bash
# Docker setup
ask-nix "install docker and docker-compose"

# Podman alternative
ask-nix "install podman instead of docker"
```

### VMs
```bash
# VirtualBox
ask-nix "install virtualbox"

# QEMU/KVM
ask-nix "set up qemu with virt-manager"
```

## 📚 Common Patterns

### Finding Packages
```bash
# When you don't know the name
ask-nix "find me a pdf reader"
ask-nix "search for music players"
ask-nix "what can edit videos?"
```

### Multiple Packages
```bash
# Install several at once
ask-nix "install vim, git, and tmux"

# Development bundle
ask-nix "i need a complete python dev setup"
```

### Removing Packages
```bash
# Single package
ask-nix "remove firefox"
ask-nix "uninstall steam"

# Clean up
ask-nix "remove unused packages"
```

### System Updates
```bash
# Update everything
ask-nix "update my system"

# Just packages
ask-nix "update installed packages"

# Specific package
ask-nix "update firefox"
```

## 💡 Pro Tips

### Natural Language Variations
All of these work the same:
- "install firefox"
- "i want firefox"
- "can you install firefox for me"
- "please add firefox to my system"
- "get me firefox"

### Shortcuts
```bash
# Even shorter
ask-nix "htop"  # Assumes install
ask-nix "remove vim"
ask-nix "search editor"
```

### Dry Run Mode
```bash
# Preview without installing
LUMINOUS_DRY_RUN=true ask-nix "install steam"

# Skip confirmations
LUMINOUS_SKIP_CONFIRM=true ask-nix "install htop"
```

### Debug Mode
```bash
# See what's happening
LUMINOUS_VERBOSE=2 ask-nix "install firefox"
```

## 🆘 Troubleshooting

### Command Failed?
```bash
# Check what went wrong
ask-nix "show last error"

# Try with more detail
LUMINOUS_VERBOSE=2 ask-nix "your command"
```

### Not Finding Package?
```bash
# Try different terms
ask-nix "markdown editor"  # Instead of specific name
ask-nix "text editor with markdown"
ask-nix "something to edit md files"
```

### System Issues?
```bash
# Check system health
ask-nix "check system status"

# See generations
ask-nix "list system generations"

# Rollback if needed
ask-nix "rollback to previous generation"
```

## 🎯 Real User Examples

### "I'm new to Linux"
```bash
ask-nix "install basic tools for new linux user"
ask-nix "i need a file manager and text editor"
ask-nix "set up user friendly desktop apps"
```

### "Setting up dev machine"
```bash
ask-nix "complete javascript development environment"
ask-nix "i need git, nodejs, vscode, and docker"
ask-nix "install database tools"
```

### "Gaming PC"
```bash
ask-nix "install steam and gaming tools"
ask-nix "i want discord and obs for streaming"
ask-nix "nvidia drivers and optimization"
```

### "Home server"
```bash
ask-nix "install nginx and certbot"
ask-nix "set up nextcloud"
ask-nix "monitoring and backup tools"
```

## 📖 Learn More

### Explore Commands
```bash
ask-nix "help"
ask-nix "show examples"
ask-nix "what can you do"
```

### Get Specific Help
```bash
ask-nix "help with installing"
ask-nix "how do i remove packages"
ask-nix "explain configurations"
```

---

*Remember: Luminous Nix understands you! Just say what you want naturally.*

**Don't overthink it - just ask!** 🚀