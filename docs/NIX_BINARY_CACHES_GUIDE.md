# 🚀 Speed Up Nix Downloads with Binary Caches

## Overview

Binary caches allow Nix to download pre-built packages instead of building from source. This can dramatically speed up `nix develop` and `nix-shell` commands.

## Default Cache

Nix uses `https://cache.nixos.org` by default, which contains most common packages. However, for faster downloads and additional packages, you can configure extra caches.

## Configuring Additional Caches

### Method 1: User Configuration (Recommended)
Add to `~/.config/nix/nix.conf`:

```conf
# Fast, reliable caches
substituters = https://cache.nixos.org https://nix-community.cachix.org
trusted-public-keys = cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY= nix-community.cachix.org-1:mB9FSh9qf2dCimDSUo8Zy7bkq5CX+/rkCWyvRCYg3Fs=

# Optional: Even more caches for ML/AI packages
extra-substituters = https://cuda-maintainers.cachix.org
extra-trusted-public-keys = cuda-maintainers.cachix.org-1:0dq3bujKpuEPMCX6U4WylrUDZ9JyUG0VpVZa7CNfq5E=
```

### Method 2: System Configuration (NixOS)
Add to `/etc/nixos/configuration.nix`:

```nix
{
  nix.settings = {
    substituters = [
      "https://cache.nixos.org"
      "https://nix-community.cachix.org"
    ];
    trusted-public-keys = [
      "cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY="
      "nix-community.cachix.org-1:mB9FSh9qf2dCimDSUo8Zy7bkq5CX+/rkCWyvRCYg3Fs="
    ];
  };
}
```

### Method 3: Per-Command Usage
```bash
# Use specific cache for one command
nix develop --substituters "https://cache.nixos.org https://nix-community.cachix.org"
```

## Popular Binary Caches

### General Purpose
- **cache.nixos.org** - Official NixOS cache (default)
- **nix-community.cachix.org** - Community packages

### Machine Learning / AI
- **cuda-maintainers.cachix.org** - CUDA and ML packages
- **ml-ops.cachix.org** - Machine learning operations tools

### Development Tools
- **devenv.cachix.org** - Development environments
- **pre-commit-hooks.cachix.org** - Pre-commit hooks

## Verifying Cache Usage

Check if packages are being downloaded from cache:
```bash
# See what would be built vs downloaded
nix develop --dry-run

# Check download sources
nix develop --print-build-logs | grep "copying from"
```

## Local Binary Cache

For teams or multiple machines, set up a local cache:

```bash
# Start local binary cache server
nix-serve --port 5000

# On other machines, add to nix.conf:
substituters = http://localhost:5000 https://cache.nixos.org
```

## Optimizing Download Speed

### 1. Parallel Downloads
```conf
# In ~/.config/nix/nix.conf
max-substitution-jobs = 16  # Increase parallel downloads
```

### 2. Connection Timeout
```conf
# Faster failure on slow connections
connect-timeout = 5
```

### 3. Use Fastest Mirror
```bash
# Test cache speed
time nix-store -r /nix/store/[hash]-hello --substituters https://cache.nixos.org
```

## Troubleshooting Slow Downloads

### Check Current Settings
```bash
nix show-config | grep substituters
```

### Clear Corrupted Downloads
```bash
# Remove failed downloads
nix-collect-garbage -d
```

### Force Fresh Download
```bash
# Bypass local negative cache
nix develop --refresh
```

## For Claude Code Users

Since Claude Code has execution timeouts, using binary caches is essential:

1. **Pre-fetch Dependencies**: Run outside Claude Code
   ```bash
   ./scripts/prefetch-dependencies.sh
   ```

2. **Use Minimal Shells**: Start with less dependencies
   ```bash
   nix-shell shell-voice-minimal.nix
   ```

3. **Check Cache Status**: Verify packages are cached
   ```bash
   nix-store -q --hash $(nix-build '<nixpkgs>' -A python311 --no-out-link)
   ```

## Best Practices

1. **Always use trusted caches** - Verify public keys
2. **Prefer official caches** - More reliable and secure
3. **Monitor download sizes** - Some packages are very large
4. **Cache locally** - For frequently used packages
5. **Use substituters wisely** - More isn't always better

## Example: Optimized nix.conf

```conf
# ~/.config/nix/nix.conf
# Optimized for Nix for Humanity development

# Fast, reliable caches
substituters = https://cache.nixos.org https://nix-community.cachix.org
trusted-public-keys = cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY= nix-community.cachix.org-1:mB9FSh9qf2dCimDSUo8Zy7bkq5CX+/rkCWyvRCYg3Fs=

# Performance settings
max-substitution-jobs = 16
connect-timeout = 5
download-attempts = 3

# Build settings
cores = 0  # Use all CPU cores
max-jobs = auto  # Automatic parallelism
```

---

*Remember: Binary caches are your friend! They turn hours of building into minutes of downloading.* 🚀