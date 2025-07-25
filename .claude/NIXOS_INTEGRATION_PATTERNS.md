# NixOS Integration Patterns - Best Practices

## Core NixOS Principles to Remember

### 1. Declarative Configuration
- **Always generate configuration.nix entries** - Never imperatively modify system
- **Use NixOS modules** - Create proper module structure for integration
- **Atomic operations** - All changes succeed or fail together
- **Rollback capability** - Every change must be reversible

### 2. Safe Command Patterns

#### Package Management
```bash
# GOOD: Query available packages
nix search nixpkgs firefox

# GOOD: Show what would be installed
nix-env -qa firefox

# GOOD: Generate config entry
echo 'environment.systemPackages = with pkgs; [ firefox ];'

# BAD: Imperative installation
nix-env -iA nixpkgs.firefox  # Avoid this
```

#### Service Management
```bash
# GOOD: Generate service configuration
cat >> configuration.nix <<EOF
services.nginx = {
  enable = true;
  virtualHosts."localhost" = {
    root = "/var/www";
  };
};
EOF

# BAD: Direct systemctl commands
systemctl start nginx  # Don't do this
```

### 3. NixOS-Specific Safety Checks

Before executing any system modification:
1. **Validate package exists**: `nix search nixpkgs <package>`
2. **Check for conflicts**: `nixos-option <option.path>`
3. **Test configuration**: `nixos-rebuild test`
4. **Dry run first**: `nixos-rebuild dry-build`

### 4. Common Patterns to Implement

#### Pattern: Installing Development Environment
```nix
# User says: "I want to code in Python"
# Generate:
{
  environment.systemPackages = with pkgs; [
    python3
    python3Packages.pip
    python3Packages.virtualenv
  ];
  
  # Optional: Set up development shell
  environment.shellInit = ''
    alias python=python3
  '';
}
```

#### Pattern: Network Troubleshooting
```bash
# User says: "My WiFi isn't working"
# Check these in order:
1. systemctl status NetworkManager
2. nmcli device status
3. ip link show
4. journalctl -u NetworkManager -e
```

#### Pattern: System Cleanup
```bash
# User says: "Free up space"
# Safe cleanup commands:
nix-collect-garbage -d  # Remove old generations
nix-store --optimise    # Deduplicate store
```

### 5. Integration with Polkit

For privileged operations, use polkit rules:

```javascript
// /etc/polkit-1/rules.d/10-nix-for-humanity.rules
polkit.addRule(function(action, subject) {
  if (action.id == "org.nixos.nix-for-humanity.rebuild" &&
      subject.isInGroup("wheel")) {
    return polkit.Result.AUTH_SELF;
  }
});
```

### 6. State Management Best Practices

#### Track System State
```nix
# Always know current generation
/run/current-system -> /nix/store/hash-nixos-system

# List all generations
nixos-rebuild list-generations

# Show configuration diff
nixos-rebuild build
nix diff-closures /run/current-system ./result
```

#### Safe Rollback
```bash
# If something goes wrong
nixos-rebuild switch --rollback

# Or to specific generation
nixos-rebuild switch --generation 42
```

### 7. Common Pitfalls to Avoid

#### ❌ Don't Mix Imperative and Declarative
```bash
# BAD: This creates inconsistency
nix-env -iA nixpkgs.vim
# Also adding to configuration.nix
```

#### ❌ Don't Modify /etc Directly
```bash
# BAD: Direct file editing
echo "nameserver 8.8.8.8" > /etc/resolv.conf

# GOOD: Use NixOS options
networking.nameservers = [ "8.8.8.8" ];
```

#### ❌ Don't Assume FHS Layout
```bash
# BAD: Hardcoded paths
/usr/bin/python

# GOOD: Use Nix paths
${pkgs.python3}/bin/python
```

### 8. User-Friendly Error Messages

Map NixOS errors to human language:

| NixOS Error | Human Translation |
|-------------|-------------------|
| "attribute 'foo' missing" | "I couldn't find a package called 'foo'" |
| "infinite recursion" | "There's a circular dependency in your configuration" |
| "collision between" | "Two packages are trying to install the same file" |
| "permission denied" | "I need administrator privileges for this" |

### 9. Testing Patterns

Always test before applying:
```bash
# 1. Syntax check
nix-instantiate --parse configuration.nix

# 2. Build test
nixos-rebuild build

# 3. VM test (if major changes)
nixos-rebuild build-vm

# 4. Activation test
nixos-rebuild test

# 5. Final switch
nixos-rebuild switch
```

### 10. Resource Awareness

Be mindful of NixOS resource usage:
- **Disk space**: Each generation uses space
- **Memory**: Evaluating configurations can be memory-intensive
- **Network**: Package downloads can be large
- **Time**: System rebuilds take time

Inform users about resource impacts:
- "This will download 150MB"
- "System rebuild will take about 2 minutes"
- "This will use 500MB of disk space"

---

*Remember: In NixOS, everything is a derivation, and every change should be declarative.*