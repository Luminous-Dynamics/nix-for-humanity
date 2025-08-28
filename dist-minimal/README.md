# Luminous Nix v0.1.0-alpha - Minimal Distribution

## What This Is

A **REAL** natural language interface for NixOS that actually executes commands.
No mocks, no fake responses - real NixOS integration.

## What Works

- ✅ List installed packages
- ✅ Show help
- ✅ System information
- ✅ Dry-run package installation
- ⚠️ Package search (slow but functional)

## Installation

```bash
./install.sh
```

## Usage

```bash
# List installed packages
luminous-nix list

# Get help
luminous-nix help

# Dry-run install
luminous-nix "install vim" --dry-run

# System info
luminous-nix info
```

## Known Limitations

This is alpha software with ~40% functionality implemented:
- Voice interface not included (dependencies missing)
- GUI not included (not connected)
- Learning system not included (never implemented)
- Search is slow (needs optimization)

## The Truth

This project was discovered to be 90% mocked. This release represents
the first REAL implementation that actually executes NixOS commands.

## Requirements

- NixOS or Nix package manager
- Python 3.8+
- Basic command line knowledge

## Support

This is alpha software. Expect bugs. Report issues on GitHub.
