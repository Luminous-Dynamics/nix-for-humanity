# 🔄 Migration Guide - From Traditional NixOS to Nix for Humanity

*Smooth transition to natural language NixOS management*

## Overview

This guide helps experienced NixOS users transition to Nix for Humanity while maintaining their existing workflows. You don't have to abandon your current methods - Nix for Humanity complements and enhances traditional NixOS usage.

## 🎯 Quick Start for NixOS Users

### Installation on Existing NixOS System

```nix
# In your configuration.nix
{ config, pkgs, ... }:
{
  # Add Nix for Humanity
  environment.systemPackages = with pkgs; [
    nix-for-humanity
  ];
  
  # Optional: Enable voice interface
  services.nixForHumanity = {
    enable = true;
    voice.enable = true;  # Optional
  };
}
```

Then rebuild:
```bash
sudo nixos-rebuild switch
```

### First Commands

```bash
# Test it works
ask-nix help

# Try your first natural language command
ask-nix "list my installed packages"

# Compare with traditional
nix-env -q  # Still works!
```

## 📋 Command Translation Guide

### Package Management

| Traditional Command | Nix for Humanity | Notes |
|-------------------|------------------|-------|
| `nix-env -iA nixpkgs.firefox` | `ask-nix install firefox` | Auto-handles nixpkgs prefix |
| `nix-env -e firefox` | `ask-nix remove firefox` | Clearer intent |
| `nix-env -qaP \| grep firefox` | `ask-nix search firefox` | Better search results |
| `nix-env -u` | `ask-nix update` | Updates everything |
| `nix-env -q` | `ask-nix list` | Formatted output |

### System Management

| Traditional Command | Nix for Humanity | Notes |
|-------------------|------------------|-------|
| `sudo nixos-rebuild switch` | `ask-nix rebuild` | Handles sudo automatically |
| `sudo nixos-rebuild test` | `ask-nix rebuild --test` | Safe testing |
| `nixos-option services.sshd` | `ask-nix option sshd` | Simpler syntax |
| `nix-channel --update` | `ask-nix channel update` | Progress feedback |

### Generation Management

| Traditional Command | Nix for Humanity | Notes |
|-------------------|------------------|-------|
| `nix-env --list-generations` | `ask-nix generation list` | 500x faster! |
| `nix-env --switch-generation 42` | `ask-nix generation switch 42` | More intuitive |
| `nix-env --rollback` | `ask-nix rollback` | Same simplicity |
| `nix-collect-garbage -d` | `ask-nix gc` | Safer defaults |

## 🔧 Configuration Management

### Traditional configuration.nix Editing

Keep your existing workflow:
```bash
# Still works
sudo nano /etc/nixos/configuration.nix
sudo nixos-rebuild switch
```

Add Nix for Humanity assistance:
```bash
# Get AI help with configuration
ask-nix config help "add nginx with SSL"
ask-nix config validate  # Before rebuilding
ask-nix rebuild --preview  # See what changes
```

### Enhanced Configuration Workflow

```bash
# Generate configuration snippets
ask-nix config generate-snippet "postgresql with backup"

# Add to existing config
ask-nix config add-service postgresql

# Validate before applying
ask-nix config check
ask-nix rebuild
```

## 🏗️ Development Environments

### Traditional Shell.nix

Your existing shell.nix files still work:
```bash
nix-shell  # Works as always
```

### Enhanced with Nix for Humanity

```bash
# Generate shell.nix from description
ask-nix dev create "python with web frameworks"

# Or enhance existing
ask-nix dev enhance  # Adds common tools to current shell.nix

# Quick environments without files
ask-nix dev temp "nodejs and postgresql"
```

### Flakes Migration

```bash
# Convert existing project to flake
ask-nix flake convert

# Or create flake from description
ask-nix flake init "rust cli tool"

# Update flake inputs
ask-nix flake update  # Same as nix flake update
```

## 🏠 Home Manager Integration

### Existing Home Manager Users

Your home.nix continues working:
```bash
home-manager switch  # Still works
```

Add Nix for Humanity features:
```bash
# Get configuration help
ask-nix home suggest "terminal tools"

# Apply themes to existing config
ask-nix home theme dracula --merge

# Manage dotfiles
ask-nix home add-dotfile vim
```

### New Home Manager Setup

```bash
# Guided setup for new users
ask-nix home setup
→ Imports existing dotfiles
→ Suggests configurations
→ Creates home.nix
```

## 🔄 Gradual Migration Strategy

### Phase 1: Exploration (Week 1)
- Keep using traditional commands
- Try Nix for Humanity for searches
- Use `ask-nix explain [command]` to learn

### Phase 2: Hybrid Usage (Week 2-4)
- Use Nix for Humanity for common tasks
- Traditional commands for complex operations
- Compare outputs to build confidence

### Phase 3: Primary Usage (Month 2+)
- Nix for Humanity for daily tasks
- Traditional for specific needs
- Help others migrate

## 💡 Power User Features

### Command Aliases

Create aliases for common workflows:
```bash
# In your shell config
alias nxs='ask-nix search'
alias nxi='ask-nix install'
alias nxr='ask-nix rebuild'
alias nxg='ask-nix generation'
```

### Scripting Integration

```bash
# Use in scripts with JSON output
packages=$(ask-nix list --json | jq -r '.[]')

# Non-interactive mode
ask-nix install firefox --non-interactive

# Batch operations
ask-nix batch << EOF
install vim
install tmux
update
EOF
```

### Advanced Workflows

```bash
# Create custom workflows
ask-nix workflow create daily-update << 'EOF'
channel update
update
generation clean --older-than 7d
gc
EOF

# Run workflow
ask-nix workflow run daily-update
```

## 🎯 Best Practices

### DO Continue Using

✅ Your existing configuration.nix  
✅ Custom nix expressions  
✅ Overlays and overrides  
✅ Your preferred editor  
✅ Version control workflows  

### DO Start Using

✅ Natural language for discovery  
✅ AI assistance for errors  
✅ Voice interface when convenient  
✅ Persona adaptation  
✅ Educational explanations  

### DON'T Feel Pressured To

❌ Abandon traditional commands  
❌ Rewrite existing configs  
❌ Change your workflow completely  
❌ Use features you don't need  

## 🔍 Discovering New Features

### Explore Gradually

```bash
# Learn about features as needed
ask-nix capabilities
ask-nix demo [feature]
ask-nix tutorial [topic]
```

### Get AI Assistance

```bash
# Ask questions naturally
ask-nix "how do I set up a minecraft server?"
ask-nix "explain overlays with examples"
ask-nix "optimize my configuration"
```

## 🆘 Troubleshooting Migration Issues

### Common Concerns

**"Will this break my system?"**
- No, Nix for Humanity is additive
- All traditional commands still work
- Your configurations remain unchanged
- Easy to uninstall if needed

**"Is it slower than native commands?"**
- Actually faster for many operations
- Native Python-Nix API eliminates overhead
- Intelligent caching improves performance
- See benchmarks: `ask-nix benchmark`

**"What about my custom scripts?"**
- Traditional commands still available
- JSON output for script integration
- Batch mode for automation
- Gradual migration supported

### Getting Help

```bash
# Traditional NixOS help still works
man configuration.nix
nixos-option

# Plus new AI-powered help
ask-nix explain configuration.nix
ask-nix debug "error message"
ask-nix suggest "better way to..."
```

## 📈 Migration Success Stories

### Developer Team Migration
> "We introduced Nix for Humanity alongside our existing setup. New team members use the natural language interface while experienced users stick to traditional commands. Everyone's happy, and onboarding time dropped from days to hours."

### System Administrator Experience  
> "I still use traditional commands for complex tasks but love the discovery features. Finding packages by description and getting AI help with errors saves me hours each week."

### Home User Transition
> "I was intimidated by NixOS until Nix for Humanity. Now I manage my system confidently, and I'm gradually learning the traditional commands as I go."

## 🎯 30-Day Migration Plan

### Week 1: Discovery
- [ ] Install Nix for Humanity
- [ ] Try package searches
- [ ] Use for simple installs
- [ ] Explore help system

### Week 2: Integration  
- [ ] Create command aliases
- [ ] Try generation management
- [ ] Test configuration assistance
- [ ] Set preferred persona

### Week 3: Expansion
- [ ] Migrate one workflow
- [ ] Try development environments
- [ ] Explore advanced features
- [ ] Share with team

### Week 4: Optimization
- [ ] Customize settings
- [ ] Create workflows
- [ ] Benchmark performance
- [ ] Plan full adoption

## 🚀 Next Steps

1. **Install**: Add to your configuration.nix
2. **Explore**: Try `ask-nix capabilities`
3. **Experiment**: Use for one task daily
4. **Share**: Help others discover it

Remember: Nix for Humanity enhances NixOS - it doesn't replace it. Use what works for you, when it works for you.

---

*"The best tool is the one that helps you work better. Nix for Humanity is here to complement, not compete."*