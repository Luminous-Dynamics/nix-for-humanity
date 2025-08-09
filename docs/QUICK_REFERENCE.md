# 📚 Nix for Humanity - Quick Reference

*All commands and features at your fingertips*

## 🚀 Essential Commands

### Basic Operations
```bash
# Help & Information
ask-nix help                    # General help
ask-nix help [topic]           # Topic-specific help
ask-nix version                # Show version info
ask-nix status                 # System status

# Package Management
ask-nix install firefox        # Install package
ask-nix remove firefox         # Remove package
ask-nix update                 # Update all packages
ask-nix update firefox         # Update specific package
ask-nix search browser         # Search for packages
ask-nix list                   # List installed packages
```

### Natural Language Examples
```bash
ask-nix "install a web browser"
ask-nix "my wifi isn't working"
ask-nix "update my system"
ask-nix "what packages are installed?"
ask-nix "how do I edit videos?"
```

## 🔍 Smart Package Discovery

### Discovery Commands
```bash
# Natural language search
ask-nix discover "photo editor"
ask-nix discover "music player"
ask-nix discover search "markdown"

# Find by command
ask-nix discover command python
ask-nix discover command npm
ask-nix "which package provides git"

# Browse categories
ask-nix discover browse
ask-nix discover browse --category development

# Popular packages
ask-nix discover popular
ask-nix discover popular --category games
```

## 🏠 Home Manager

### Home Configuration
```bash
# Initialize
ask-nix home init "vim and tmux setup"
ask-nix home init --shell zsh --theme dracula

# Manage dotfiles
ask-nix home add vim
ask-nix home add tmux --source ~/my.tmux.conf

# Apply themes
ask-nix home theme nord
ask-nix home theme dracula --apps terminal vim

# Other commands
ask-nix home list              # List managed configs
ask-nix home apply             # Apply changes
ask-nix home sync --from laptop --to desktop
```

## 📝 Configuration Management

### System Configuration
```bash
# Generate configs
ask-nix config generate "desktop with nvidia"
ask-nix config generate "minimal server"

# Add components
ask-nix config add-service nginx
ask-nix config add-user alice --admin

# Validation
ask-nix config validate
ask-nix config show
ask-nix config diff
```

## ❄️ Flakes & Development

### Flake Operations
```bash
# Initialize
ask-nix flake init
ask-nix flake init --template python

# Development environments
ask-nix dev "python with numpy"
ask-nix dev enter

# Management
ask-nix flake update
ask-nix flake show
ask-nix flake check
```

## 🔄 Generation Management

### System Generations
```bash
# List and switch
ask-nix generation list
ask-nix generation switch 42
ask-nix generation rollback

# Cleanup
ask-nix generation clean --older-than 30d
ask-nix generation clean --keep-last 5

# Compare
ask-nix generation diff 42 43
ask-nix generation find-change firefox
```

## 🎤 Voice Interface

### Voice Control
```bash
# Setup
ask-nix voice enable
ask-nix voice test
ask-nix voice config --wake-word "hey nix"

# Personas
ask-nix voice set-persona grandma-rose
ask-nix voice conversation     # Continuous mode
```

## 👥 Personas

### Available Personas
1. `grandma-rose` - Simple, friendly
2. `maya` - Ultra-fast, ADHD-friendly
3. `alex` - Screen reader optimized
4. `viktor` - ESL-friendly
5. `dr-sarah` - Technical, precise
6. `carlos` - Learning mode
7. `david` - Tired-parent mode
8. `priya` - Quick, efficient
9. `jamie` - Privacy-focused
10. `luna` - Neurodivergent-friendly

### Using Personas
```bash
ask-nix --persona maya "install firefox"
ask-nix config set-persona grandma-rose
ask-nix persona test maya
```

## ⚡ Performance Features

### Speed Optimizations
```bash
# Native operations (instant!)
ask-nix generation list         # Was 2-5s, now instant
ask-nix info firefox           # 10x faster
ask-nix rollback              # 50x faster

# Performance monitoring
ask-nix benchmark
ask-nix stats --detailed
ask-nix cache optimize
```

## 🛠️ Advanced Options

### Global Flags
```bash
-v, --verbose         # Verbose output
-q, --quiet          # Minimal output
--json               # JSON output
--dry-run            # Preview only
--non-interactive    # No prompts
--explain            # Educational mode
```

### Output Formats
```bash
ask-nix list --format=json
ask-nix search --format=csv
ask-nix info --format=yaml
```

### Filtering
```bash
ask-nix search python --filter "version>=3.11"
ask-nix list --filter installed --filter user
```

## 🔧 Configuration

### Settings Management
```bash
# View settings
ask-nix config show
ask-nix config get ui.color

# Change settings
ask-nix config set default.persona maya
ask-nix config set performance.cache true

# Import/Export
ask-nix config export > config.json
ask-nix config import config.json
```

## 💡 Pro Tips

### Useful Combinations
```bash
# Explain while doing
ask-nix --explain install firefox

# Preview with persona
ask-nix --dry-run --persona maya update

# JSON output for scripts
ask-nix --json list | jq '.packages'

# Batch operations
ask-nix batch install firefox vim tmux
```

### Workflows
```bash
ask-nix workflow new-machine
ask-nix workflow development-setup
ask-nix workflow create my-setup
```

## 🆘 Getting Help

### Help Commands
```bash
ask-nix help                   # General help
ask-nix help discover          # Feature help
ask-nix examples               # Show examples
ask-nix guide                  # Interactive guide
ask-nix tutorial packages      # Tutorials
```

### Troubleshooting
```bash
ask-nix doctor                 # System check
ask-nix diagnose              # Diagnose issues
ask-nix recovery start        # Emergency mode
```

## ⌨️ Keyboard Shortcuts (TUI)

| Key | Action |
|-----|--------|
| `?` | Help |
| `/` | Search |
| `Tab` | Switch panels |
| `Enter` | Select/Execute |
| `Esc` | Cancel/Back |
| `Ctrl+C` | Exit |
| `Ctrl+L` | Clear |
| `F1`-`F10` | Persona switch |

## 📊 Status Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | Permission denied |
| 4 | Package not found |
| 5 | Network error |
| 10 | Nix error |

---

**Remember**: Natural language always works! When in doubt, just describe what you want.

*"Making NixOS as easy as having a conversation"*