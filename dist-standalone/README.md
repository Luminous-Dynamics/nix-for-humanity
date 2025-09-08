# Luminous Nix v0.3.0 - Standalone Binary

## Quick Start

```bash
# Make executable
chmod +x luminous-nix

# Run directly
./luminous-nix "install firefox"

# Or add to PATH
sudo cp luminous-nix /usr/local/bin/
luminous-nix "search text editors"
```

## Features

This standalone binary includes:
- ✅ Natural language CLI
- ✅ 96.3% accuracy
- ✅ Pattern-based specialists
- ✅ Intelligent caching
- ❌ Neural networks (requires Python environment)
- ❌ Voice interface (requires additional dependencies)

For full features including neural networks, install via:
- PyPI: `pip install luminous-nix[neural]`
- Nix: `nix-env -iA nixpkgs.luminous-nix`

## System Requirements

- Linux x86_64
- 50MB disk space
- 256MB RAM

## License

MIT - See https://github.com/Luminous-Dynamics/luminous-nix
