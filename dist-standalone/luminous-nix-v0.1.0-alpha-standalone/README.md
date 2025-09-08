# Luminous Nix v0.1.0-alpha - Standalone Distribution

**Natural Language Interface for NixOS**

## Quick Start

1. **Install dependencies**:
   ```bash
   ./install.sh
   # or manually:
   pip3 install --user -r requirements.txt
   ```

2. **Run Luminous Nix**:
   ```bash
   ./luminous-nix help
   ./luminous-nix "search firefox"
   ./luminous-nix "install vim"
   ```

## What Works (v0.1.0-alpha)

✅ **Working Features**:
- Natural language commands
- Package search with typo correction
- Package installation
- List installed packages
- Help system
- Dry-run mode for safety

⚠️ **Alpha Limitations**:
- 2-3 second response times (standard Nix speed)
- Voice interface not yet functional
- Learning system not activated
- Basic AI features only

## Examples

```bash
# Search for packages
./luminous-nix "search text editor"
./luminous-nix "find markdown editor"

# Install packages (with confirmation)
./luminous-nix "install firefox"
./luminous-nix --dry-run "install vim"  # Preview only

# System operations
./luminous-nix "list installed"
./luminous-nix "what's installed?"
./luminous-nix "help"
```

## Requirements

- NixOS or Linux with Nix installed
- Python 3.9 or higher
- Internet connection for package operations

## Troubleshooting

If you get import errors:
1. Run `./install.sh` to install dependencies
2. Make sure Python 3.9+ is installed
3. Check that Nix is available: `which nix`

## About This Release

This is the first honest alpha release after extensive cleanup:
- Removed 70% of non-working code
- Fixed all import errors
- Integrated clean service architecture
- Set realistic expectations

## Roadmap

- v0.2.0 (Feb 2025): Voice interface, cache optimization
- v0.3.0 (Mar 2025): Learning system, personas
- v0.4.0 (Apr 2025): GUI preview
- v1.0.0 (Nov 2025): Production ready

## Support

Report issues: https://github.com/Luminous-Dynamics/luminous-nix/issues

## License

MIT

---
*"Making NixOS accessible through natural language"*
