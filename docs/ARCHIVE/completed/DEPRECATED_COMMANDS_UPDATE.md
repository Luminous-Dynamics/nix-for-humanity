# 🔄 Deprecated Commands Modernization Guide

*Updating Nix for Humanity to use modern NixOS best practices*

## Overview

Several commands in our knowledge base use deprecated or legacy approaches. This guide documents what needs updating and provides modern alternatives.

## Deprecated Commands Found

### 1. nix-env (Imperative Package Management)

**Current Usage:**
```bash
nix-env -iA nixos.firefox    # Install
nix-env -e firefox           # Remove  
nix-env -u                   # Upgrade
nix-env --list-generations   # List
```

**Modern Replacement:**
```bash
nix profile install nixpkgs#firefox  # Install
nix profile remove firefox           # Remove
nix profile upgrade                  # Upgrade all
nix profile history                  # List generations
```

**Why deprecated:**
- nix-env has confusing upgrade behavior
- Not reproducible
- Can break system consistency
- Being phased out in favor of nix profile

### 2. nix-channel (Channel Management)

**Current Usage:**
```bash
sudo nix-channel --update
nix-channel --list
nix-channel --add URL NAME
```

**Modern Replacement with Flakes:**
```bash
nix flake update              # Update flake inputs
nix registry list             # List registries
nix registry add NAME URL     # Add registry
```

**For non-flake systems, alternative:**
```bash
# Use Home Manager for user-level updates
home-manager switch           # No sudo needed!
```

### 3. nixos-rebuild with sudo (System Updates)

**Current Usage:**
```bash
sudo nixos-rebuild switch
sudo nixos-rebuild test
```

**Better Alternatives:**

**Option 1: Home Manager (User-level, no sudo)**
```bash
# For user packages and configuration
home-manager switch
home-manager generations
```

**Option 2: Delegated rebuilds**
```bash
# Use systemd service or polkit rules
systemctl start nixos-rebuild
```

**Option 3: Remote rebuilds**
```bash
# Build on another machine
nixos-rebuild switch --target-host localhost --use-remote-sudo
```

## Implementation Changes Needed

### 1. Update Knowledge Base

**File:** `scripts/nix-knowledge-engine.py`

```python
# Old
'nix-env -iA nixos.firefox'

# New
'nix profile install nixpkgs#firefox'
```

### 2. Add Command Detection

Detect legacy commands and suggest modern alternatives:

```python
DEPRECATED_COMMANDS = {
    'nix-env -i': 'Consider using: nix profile install',
    'nix-env -e': 'Consider using: nix profile remove',
    'nix-channel --update': 'Consider using: nix flake update or home-manager switch',
}
```

### 3. Update Installation Methods

```python
self.install_methods = {
    'declarative': {
        'name': 'System Configuration (Recommended)',
        'description': 'Add to configuration.nix for system-wide installation',
        'command': 'Edit /etc/nixos/configuration.nix',
        'example': 'environment.systemPackages = with pkgs; [ {package} ];'
    },
    'home-manager': {
        'name': 'Home Manager (User-level, No Sudo)',
        'description': 'User-specific installation without root access',
        'command': 'Edit ~/.config/home-manager/home.nix',
        'example': 'home.packages = with pkgs; [ {package} ];'
    },
    'nix-profile': {
        'name': 'Nix Profile (Modern Imperative)',
        'description': 'Quick installation with modern tooling',
        'command': 'nix profile install nixpkgs#{package}',
        'example': 'nix profile install nixpkgs#{package}'
    },
    'nix-shell': {
        'name': 'Temporary Shell',
        'description': 'Try without installing',
        'command': 'nix-shell -p {package}',
        'example': 'nix-shell -p {package}'
    }
}
```

## User-Level Update Strategy

### For Users Who Don't Want sudo

1. **Home Manager Setup** (One-time)
```bash
# Install Home Manager
nix-channel --add https://github.com/nix-community/home-manager/archive/master.tar.gz home-manager
nix-channel --update

# Initial setup
nix-shell '<home-manager>' -A install
```

2. **Daily Usage** (No sudo needed!)
```bash
# Install packages
home-manager edit  # Opens config
# Add: home.packages = with pkgs; [ firefox vscode ];
home-manager switch

# Update everything
nix-channel --update
home-manager switch
```

### For Flake Users

```bash
# Update all inputs
nix flake update

# Apply changes (might need sudo for system)
home-manager switch --flake .  # User only
sudo nixos-rebuild switch --flake .  # System
```

## Migration Messages

When users try deprecated commands, show helpful migrations:

```
You asked to: install firefox
Legacy command would be: nix-env -iA nixos.firefox

🚀 Modern alternatives:

1. For permanent installation (recommended):
   Edit /etc/nixos/configuration.nix
   Add: environment.systemPackages = with pkgs; [ firefox ];
   Run: sudo nixos-rebuild switch

2. For user-only installation (no sudo):
   nix profile install nixpkgs#firefox

3. Just trying it out:
   nix-shell -p firefox

Note: nix-env is being phased out. Learn more: https://nixos.org/manual/nix/stable/command-ref/new-cli/nix3-profile.html
```

## Benefits of Modernization

1. **Better for users:**
   - Home Manager eliminates sudo requirements
   - nix profile has saner behavior
   - Flakes provide reproducibility

2. **Future-proof:**
   - Nix is moving away from channels
   - nix-env will eventually be removed
   - New features only in new commands

3. **Cleaner mental model:**
   - Declarative by default
   - Imperative when needed
   - Clear separation of concerns

## Implementation Priority

1. **High Priority:**
   - Add Home Manager as primary user-level solution
   - Update all nix-env references to nix profile
   - Add migration warnings

2. **Medium Priority:**
   - Detect flake vs non-flake systems
   - Provide context-aware suggestions
   - Update documentation

3. **Low Priority:**
   - Full flakes integration
   - Advanced nix profile features
   - Remote rebuild support

## Testing Migration

```bash
# Test deprecated command detection
ask-nix "install firefox with nix-env"
# Should warn about deprecation

# Test modern command generation  
ask-nix "install firefox"
# Should suggest nix profile or Home Manager

# Test user-level focus
ask-nix "install firefox without sudo"
# Should prioritize Home Manager
```

## Conclusion

By modernizing our command recommendations, we:
- Help users learn current best practices
- Reduce frustration with sudo requirements
- Future-proof their NixOS knowledge
- Align with official NixOS direction

The key insight: **Home Manager + nix profile = User empowerment without sudo!**

---

*Next action: Update nix-knowledge-engine.py to use modern commands*