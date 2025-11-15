
# nixos-rebuild-ng Python API Documentation

## Overview
The nixos-rebuild-ng Python API provides programmatic access to NixOS system
building and configuration management without using subprocess calls.

## Installation
The API is available when nixos-rebuild-ng is installed:
- NixOS 25.05: Experimental feature
- NixOS 25.11: Enabled by default with `system.rebuild.enableNg`

## Basic Usage

```python
import sys
from pathlib import Path
import subprocess

# Setup Python path
result = subprocess.run(
    ["nix-build", "<nixpkgs>", "-A", "nixos-rebuild-ng", "--no-out-link"],
    capture_output=True,
    text=True
)
rebuild_path = result.stdout.strip()
site_packages = Path(rebuild_path) / "lib" / "python3.13" / "site-packages"
sys.path.insert(0, str(site_packages))

# Import modules
from nixos_rebuild import models, nix, services

# Build system
build_attr = models.BuildAttr(attribute="system")
path = nix.build(build_attr)

# Switch to configuration
nix.switch_to_configuration(path, models.Action.SWITCH, models.Profile.SYSTEM)
```

## API Reference

### Models Module

#### Action Enum
- `Action.SWITCH` - Apply configuration now and on boot
- `Action.BOOT` - Apply on next boot only
- `Action.TEST` - Apply now but not on boot
- `Action.BUILD` - Build only, don't apply
- `Action.DRY_BUILD` - Show what would be built
- `Action.DRY_ACTIVATE` - Test activation

#### Profile Enum
- `Profile.SYSTEM` - System-wide profile
- `Profile.REMOTE_SUDO` - Remote system with sudo

#### BuildAttr Dataclass
```python
BuildAttr(
    attribute: str,           # Nix attribute to build
    attr_path: str = None,    # Attribute path
    file: str = None,         # Nix file
    flake: Flake = None       # Flake configuration
)
```

#### Flake Dataclass
```python
Flake(
    path: str,                              # Path to flake
    no_write_lock_file: bool = False,       # Don't update lock
    override_inputs: dict[str, str] = None  # Input overrides
)
```

#### Remote Dataclass
```python
Remote(
    host: str,                    # Hostname
    user: str = None,             # Username
    port: int = 22,               # SSH port
    opts: list[str] = None,       # SSH options
    sudo: bool = False,           # Use sudo
    sudo_opts: list[str] = None  # Sudo options
)
```

### Nix Module Functions

#### Building
- `build(build_attr: BuildAttr) -> Path` - Build NixOS configuration
- `build_flake(build_attr: BuildAttr) -> Path` - Build with flakes
- `build_remote(build_attr: BuildAttr, remote: Remote) -> Path` - Remote build

#### Configuration Management
- `switch_to_configuration(path: Path, action: Action, profile: Profile)` - Apply config
- `set_profile(path: Path, profile: Profile)` - Set system profile
- `rollback(profile: Profile)` - Rollback to previous generation

#### Generations
- `list_generations(profile: Profile) -> list[Generation]` - List all generations
- `get_generations(profile: Profile) -> list[Generation]` - Get generation details

#### Utilities
- `get_nixpkgs_rev() -> str` - Get nixpkgs revision
- `find_file(name: str) -> Path` - Find file in Nix path
- `copy_closure(path: Path, remote: Remote)` - Copy to remote

## Complete Example

```python
from nixos_rebuild import models, nix

def rebuild_system(dry_run=False):
    """Rebuild NixOS system"""
    action = models.Action.DRY_BUILD if dry_run else models.Action.BUILD

    # Build configuration
    build_attr = models.BuildAttr(attribute="system")
    path = nix.build(build_attr)

    if not dry_run:
        # Apply configuration
        nix.switch_to_configuration(
            path,
            models.Action.SWITCH,
            models.Profile.SYSTEM
        )

    return path

def manage_generations():
    """List and manage system generations"""
    generations = nix.list_generations(models.Profile.SYSTEM)

    for gen in generations:
        print(f"Generation {gen.number}: {gen.date}")
        if gen.current:
            print("  (current)")

    # Rollback if needed
    # nix.rollback(models.Profile.SYSTEM)
```
