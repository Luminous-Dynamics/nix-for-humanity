# Migration Guide: v0.8.3 to v1.0.0

## Overview

Nix for Humanity v1.0.0 introduces significant improvements while maintaining backward compatibility. This guide helps you migrate smoothly.

## Breaking Changes

### 1. Python Backend Now Default

**Old behavior**: Subprocess-based execution
**New behavior**: Native Python-Nix API

**Action required**:
```bash
# Add to your shell configuration
export NIX_HUMANITY_PYTHON_BACKEND=true
```

Or in NixOS configuration:
```nix
services.nixForHumanity.pythonBackend = true;
```

### 2. Configuration Format Update

**Old format** (v0.8.3):
```json
{
  "user": {
    "name": "Alice",
    "style": "technical"
  }
}
```

**New format** (v1.0.0):
```json
{
  "version": "1.0.0",
  "user": {
    "name": "Alice",
    "persona": "technical",
    "preferences": {
      "theme": "default",
      "verbosity": "normal"
    }
  }
}
```

**Automatic migration**: Run `ask-nix migrate config`

### 3. Voice API Changes

**Old API**:
```python
from nix_for_humanity.voice import VoiceInterface
voice = VoiceInterface()
```

**New API**:
```python
from nix_for_humanity.interfaces.voice import VoiceEngine
voice = VoiceEngine(persona="maya")
```

## New Features to Adopt

### 1. Configuration Generation

Transform descriptions into NixOS configs:
```bash
ask-nix "generate config for web development with nodejs and postgresql"
```

### 2. Smart Package Discovery

Find packages by what they do:
```bash
ask-nix "find markdown editor with preview"
ask-nix "package for editing photos"
```

### 3. Flake Management

Create development environments:
```bash
ask-nix "create python dev environment with numpy and pandas"
ask-nix "setup rust project with wasm target"
```

### 4. Enhanced Error Messages

Errors now educate:
```
Error: Package 'neovim' has unfree license
Learning: Unfree packages need explicit permission in NixOS.
Solution: Add to configuration.nix:
  nixpkgs.config.allowUnfree = true;
Or for this package only:
  nixpkgs.config.allowUnfreePredicate = pkg: pkg.pname == "neovim";
```

## Performance Improvements

### Before (v0.8.3)
- List generations: 2-5 seconds
- Package search: 5-10 seconds
- System operations: Often timeout

### After (v1.0.0)
- List generations: <0.1 seconds (∞x faster)
- Package search: 0.5-1 second (10x faster)
- System operations: No timeouts, real-time progress

## Migration Steps

### 1. Backup Current Configuration
```bash
cp ~/.config/nix-for-humanity/config.json ~/.config/nix-for-humanity/config.json.backup
```

### 2. Update Package
```bash
# For NixOS module users
sudo nixos-rebuild switch

# For flake users
nix flake update
sudo nixos-rebuild switch

# For user installation
cd ~/nix-for-humanity
git pull
nix develop
./install-user.sh
```

### 3. Run Migration Tool
```bash
ask-nix migrate all
```

This will:
- Update configuration format
- Migrate learning data
- Update aliases and shortcuts
- Preserve all customizations

### 4. Verify Migration
```bash
ask-nix diagnose migration
```

## Rollback Procedure

If issues occur:

### 1. Restore Configuration
```bash
cp ~/.config/nix-for-humanity/config.json.backup ~/.config/nix-for-humanity/config.json
```

### 2. Downgrade Package
```nix
# In configuration.nix
services.nixForHumanity.package = pkgs.nixForHumanity_0_8_3;
```

### 3. Rebuild System
```bash
sudo nixos-rebuild switch
```

## Common Migration Issues

### Issue: "Unknown configuration version"
**Solution**: Run `ask-nix migrate config`

### Issue: "Voice not working after upgrade"
**Solution**: Re-run voice setup: `ask-nix voice setup`

### Issue: "Custom aliases missing"
**Solution**: Aliases are preserved but may need reactivation: `ask-nix settings reload`

### Issue: "Slower performance than expected"
**Solution**: Ensure Python backend is enabled: `export NIX_HUMANITY_PYTHON_BACKEND=true`

## What's Deprecated

### Removed Features
- Mock testing mode (use real integration tests)
- Legacy subprocess executor
- Old configuration format
- Experimental plugins (being redesigned)

### Replaced Features
- `ask-nix test-mode` → Use `--dry-run` flag
- `nix-humanity-cli` → Unified as `ask-nix`
- Manual persona files → Integrated persona system

## Getting Help

- **Migration issues**: `ask-nix migrate help`
- **Documentation**: `ask-nix docs migration`
- **Community support**: GitHub discussions
- **Direct support**: Create issue with `migration` label

## Timeline

- **v0.8.3 support**: Ends 3 months after v1.0.0 release
- **Migration tool availability**: 6 months
- **Legacy API compatibility**: 1 year with warnings

---

**Remember**: This upgrade brings 10x-1500x performance improvements and powerful new features. The migration effort is worth it!
