# Quick Start - Nix for Humanity

Get running in 5 minutes with what actually works today.

## Prerequisites

- NixOS or Nix package manager installed
- Python 3.11+
- Basic terminal knowledge

## Installation

```bash
# Clone the repository
git clone https://github.com/Luminous-Dynamics/nix-for-humanity
cd nix-for-humanity

# Enter development environment
nix develop

# Verify installation
./bin/ask-nix "help"
```

## What Works Today

### Basic Commands
```bash
# Show help
./bin/ask-nix "help"

# Search for packages
./bin/ask-nix "search firefox"
./bin/ask-nix "find text editor"

# Basic queries (may not be reliable)
./bin/ask-nix "install vim"  # Warning: might fail
```

### Response Styles
Add `--style` for different response types:
```bash
./bin/ask-nix "search python" --style technical
./bin/ask-nix "help" --style friendly
./bin/ask-nix "search games" --style concise
```

## Current Limitations

**Reliability Issues**:
- Install/remove commands fail ~40% of the time
- Update commands often timeout
- Some searches return no results

**Performance**:
- Most operations take 2-5 seconds
- Complex queries may timeout
- No progress indicators

**What's NOT Working**:
- Voice commands (not implemented)
- TUI interface (not connected)
- Learning from usage (data saved but unused)
- Advanced features (flakes, configurations, etc.)

## Troubleshooting

### Command Failed
Most failures are due to subprocess timeouts or incomplete implementation:
```bash
# If install fails, try the direct Nix command:
nix-env -iA nixpkgs.firefox

# Check what the tool tried to do:
./bin/ask-nix "install firefox" --dry-run
```

### No Results
The search might be too specific:
```bash
# Instead of:
./bin/ask-nix "search markdown editor with vim keybindings"

# Try:
./bin/ask-nix "search markdown"
./bin/ask-nix "search editor"
```

## Coming in v1.0 (6 weeks)

1. **Lightning-fast operations** (<0.5s for everything)
2. **Smart learning** that improves with use
3. **95% reliability** on common commands
4. **Real progress indicators**
5. **Helpful error messages**

## Contributing

We're focused on two hero capabilities for v1.0:
1. Native Python-Nix API (for speed)
2. Learning loop (for intelligence)

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to help.

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/Luminous-Dynamics/nix-for-humanity/issues)
- **Discussion**: [GitHub Discussions](https://github.com/Luminous-Dynamics/nix-for-humanity/discussions)
- **Status**: See [FOCUSED_ROADMAP.md](FOCUSED_ROADMAP.md) for current progress

---

**Remember**: This is a pre-v1.0 prototype. We're being honest about limitations while working hard to deliver excellence by February 23, 2025.