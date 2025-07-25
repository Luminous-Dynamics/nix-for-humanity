# 📖 NixOS Command Reference for Sacred Intent Engine

*Ensuring every command honors the NixOS way*

## 🌟 Core Principles

1. **Declarative First**: Prefer configuration.nix over imperative commands
2. **Atomic Operations**: NixOS ensures rollback capability
3. **Pure Functions**: Commands should be predictable and reproducible
4. **Sacred Safety**: Always provide confirmation for system changes

## 📦 Package Management

### Searching for Packages
```bash
# NixOS way (NOT apt search or yum search)
nix search nixpkgs firefox
nix search nixpkgs "text editor"

# With descriptions
nix search nixpkgs --verbose firefox
```

### Installing Packages

#### Imperative (Quick testing)
```bash
# Install for current user
nix-env -iA nixpkgs.firefox

# Install specific version
nix-env -iA nixpkgs.firefox-esr
```

#### Declarative (Recommended)
```nix
# Edit /etc/nixos/configuration.nix
environment.systemPackages = with pkgs; [
  firefox
  vim
  git
];

# Then rebuild
sudo nixos-rebuild switch
```

### Removing Packages
```bash
# Imperative removal
nix-env -e firefox

# Declarative - remove from configuration.nix then:
sudo nixos-rebuild switch
```

### Listing Installed
```bash
# User packages
nix-env -q

# System packages
nix-env -qa --installed

# With versions
nix-env -q --json
```

## 🔄 System Updates

### Update System
```bash
# Update channel first
sudo nix-channel --update

# Then rebuild with updates
sudo nixos-rebuild switch --upgrade

# Test without switching
sudo nixos-rebuild test --upgrade

# Build without switching
sudo nixos-rebuild build --upgrade
```

### Channel Management
```bash
# List channels
sudo nix-channel --list

# Add channel
sudo nix-channel --add https://nixos.org/channels/nixos-24.05 nixos

# Update channels
sudo nix-channel --update
```

## 🧹 System Maintenance

### Garbage Collection
```bash
# Remove old generations
sudo nix-collect-garbage -d

# Keep last 7 days
sudo nix-collect-garbage --delete-older-than 7d

# See what would be deleted
sudo nix-collect-garbage -d --dry-run
```

### Store Optimization
```bash
# Deduplicate store files
nix-store --optimise

# Verify store integrity
nix-store --verify --check-contents

# Repair store
nix-store --verify --check-contents --repair
```

## 🔧 Configuration Management

### Edit Configuration
```bash
# System configuration
sudo nano /etc/nixos/configuration.nix

# Hardware configuration (rarely edited)
sudo nano /etc/nixos/hardware-configuration.nix

# Home-manager (if used)
nano ~/.config/nixpkgs/home.nix
```

### Apply Configuration
```bash
# Apply and switch
sudo nixos-rebuild switch

# Test first (safer)
sudo nixos-rebuild test

# Just build
sudo nixos-rebuild build

# Boot into new config
sudo nixos-rebuild boot
```

### Rollback
```bash
# List generations
sudo nix-env --list-generations --profile /nix/var/nix/profiles/system

# Rollback to previous
sudo nixos-rebuild switch --rollback

# Switch to specific generation
sudo nix-env --profile /nix/var/nix/profiles/system --switch-generation 42
```

## 🚀 Service Management

### Service Control
```bash
# Start service
sudo systemctl start nginx

# Stop service
sudo systemctl stop nginx

# Restart service
sudo systemctl restart nginx

# Reload config
sudo systemctl reload nginx

# Enable at boot
sudo systemctl enable nginx

# Disable at boot
sudo systemctl disable nginx
```

### Service Status
```bash
# Check status
systemctl status nginx

# List all services
systemctl list-units --type=service

# List failed services
systemctl list-units --failed

# Show service logs
journalctl -u nginx -f
```

## 💻 System Information

### NixOS Version
```bash
# NixOS version
nixos-version

# With revision
nixos-version --json

# System info
nix-info -m
```

### Hardware Info
```bash
# CPU info
lscpu

# Memory info
free -h

# Disk usage
df -h

# All hardware
sudo lshw -short
```

## 🌐 Network Management

### NetworkManager Commands
```bash
# Show connections
nmcli connection show

# Connect to WiFi
nmcli device wifi connect "SSID" password "password"

# List WiFi networks
nmcli device wifi list

# Show device status
nmcli device status
```

### Network Diagnostics
```bash
# Test connectivity
ping -c 4 8.8.8.8

# DNS lookup
nslookup nixos.org

# Show network interfaces
ip addr show

# Show routing table
ip route show
```

## 👤 User Management

### User Operations
```bash
# Current user
whoami

# User groups
groups

# All users
cat /etc/passwd | grep "/home"

# Add user (declarative preferred)
# Edit configuration.nix instead
```

## 🔐 Security Commands

### Firewall
```bash
# In configuration.nix:
networking.firewall.enable = true;
networking.firewall.allowedTCPPorts = [ 80 443 ];

# Then rebuild
sudo nixos-rebuild switch
```

### System Security
```bash
# Check for vulnerabilities
nix-shell -p vulnix --run "vulnix --system"

# Update all packages
sudo nixos-rebuild switch --upgrade
```

## 🎯 NixOS-Specific Tips

### 1. **Always Prefer Declarative**
Instead of installing packages imperatively, add them to configuration.nix

### 2. **Use Atomic Operations**
NixOS operations are atomic - they either complete fully or rollback

### 3. **Test Before Switch**
Always use `nixos-rebuild test` before `switch` for system changes

### 4. **Keep Generations**
Don't garbage collect too aggressively - keep some generations for rollback

### 5. **Use Home-Manager**
For user-specific configurations, consider home-manager

## 🚫 Common Mistakes to Avoid

### ❌ Don't Use These Commands:
- `apt-get` / `yum` / `pacman` - Use nix-env
- `make install` - Create nix expressions
- Manual `/usr/local` installations - Use nix
- `pip install --global` - Use nix Python packages

### ✅ Use NixOS Equivalents:
- `apt search` → `nix search nixpkgs`
- `apt install` → `nix-env -iA nixpkgs.` or configuration.nix
- `apt remove` → `nix-env -e` or configuration.nix
- `apt update && apt upgrade` → `nix-channel --update && nixos-rebuild switch`

## 📚 Sacred Command Patterns

When implementing in the intent engine, each command should:

1. **Honor Immutability**: Never modify system files directly
2. **Provide Rollback**: Users should always have an escape route
3. **Be Transparent**: Show what will change before changing it
4. **Stay Declarative**: Encourage configuration.nix changes
5. **Remain Safe**: Require confirmation for system modifications

## 🌊 Example Sacred Implementation

```javascript
// Good NixOS pattern
{
  pattern: /^install\s+(.+)$/i,
  handler: async (package) => {
    // Check if package exists first
    const searchResult = await exec(`nix search nixpkgs ${package}`);
    
    if (!searchResult) {
      return {
        message: `Package '${package}' not found. Try searching with a different name.`,
        suggestions: await getSimilarPackages(package)
      };
    }
    
    // Offer both options
    return {
      message: `Found ${package}. How would you like to install it?`,
      options: [
        {
          label: "Quick install (just for me)",
          command: `nix-env -iA nixpkgs.${package}`,
          description: "Installs immediately but not permanently"
        },
        {
          label: "System install (recommended)",
          command: `sudo nano /etc/nixos/configuration.nix`,
          description: "Add to configuration for permanent installation"
        }
      ]
    };
  }
}
```

---

*Remember: In NixOS, the path to enlightenment is declarative, atomic, and always reversible.* 🕉️