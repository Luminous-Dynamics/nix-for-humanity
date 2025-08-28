# 🎯 Poetry + Nix Hybrid Solution - The Pragmatic Approach

## Summary

After encountering platform-specific issues with pure poetry2nix (specifically `riscv64` architecture checks in certain packages), we've implemented a **hybrid approach** that gives us the best of both worlds:

- ✅ **Nix** provides system dependencies and development tools
- ✅ **Poetry** manages Python packages as usual
- ✅ **100% working** solution that avoids poetry2nix complexity
- ✅ **Reproducible** system dependencies via Nix
- ✅ **Flexible** Python packages via Poetry

## The Problem We Solved

Pure poetry2nix failed with:
```
error: attribute 'riscv64' missing
at .../vendor/pyproject.nix/lib/pep600.nix:72:13
```

This is a known issue when poetry2nix tries to evaluate certain packages (like `semgrep`, `jsonschema`) that have complex platform checks.

## The Solution: Hybrid Approach

### What We Use Each Tool For

| Component | Tool | Why |
|-----------|------|-----|
| System libraries | Nix | Reproducible, cached, no conflicts |
| Dev tools (ruff, black) | Nix | Consistent versions across team |
| Python packages | Poetry | Familiar workflow, all packages work |
| Virtual environment | Poetry | Standard Python isolation |

### How It Works

1. **Nix provides the shell** with all system dependencies
2. **Poetry runs inside** that shell with its own virtual environment
3. **No conflicts** - each tool does what it does best

## Using the Hybrid Approach

### Quick Start
```bash
# Enter the Nix development shell
nix develop

# Install Python dependencies with Poetry (first time)
poetry install

# Run the application
poetry run ask-nix "help"
```

### The Development Shell Provides

- ✅ Python 3.13.5
- ✅ Poetry for dependency management
- ✅ System libraries (gcc, zlib, openssl, etc.)
- ✅ Database support (sqlite, postgresql)
- ✅ Voice support (portaudio, ffmpeg)
- ✅ Dev tools (ruff, black, mypy)
- ✅ Documentation tools (pandoc)

### Available Flakes

We maintain three flake versions:

1. **`flake.nix`** - The working hybrid approach (CURRENT)
2. **`flake-poetry2nix.nix`** - Pure poetry2nix (has issues)
3. **`flake-hybrid.nix`** - Backup of hybrid approach

## Benefits of This Approach

### What Works
- ✅ **All Python packages install** - No poetry2nix evaluation errors
- ✅ **Fast iteration** - Change Python deps without Nix rebuilds
- ✅ **Team friendly** - Developers know Poetry already
- ✅ **CI/CD ready** - Simple GitHub Actions integration
- ✅ **Reproducible enough** - System deps are locked via Nix

### Trade-offs (Acceptable)
- ⚠️ Python packages not binary-cached (but Poetry caches them)
- ⚠️ Not 100% reproducible (but Poetry.lock helps)
- ⚠️ Two tools instead of one (but both are standard)

## For Different Use Cases

### Development
```bash
nix develop
poetry install
poetry run ask-nix help
```

### CI/CD
```bash
nix develop .#ci -c poetry run pytest
```

### Documentation
```bash
nix develop .#docs -c poetry run mkdocs serve
```

### Traditional Poetry (without Nix)
```bash
# Still works if you have system deps
poetry install
poetry run ask-nix help
```

## Why This Is Actually Better

1. **Pragmatic** - It works today, not theoretically
2. **Familiar** - Python developers know Poetry
3. **Flexible** - Easy to add/remove packages
4. **Debuggable** - Standard Python tooling works
5. **Fast** - No Nix evaluation for Python changes

## The Philosophy

This aligns with our **Sophisticated Simplicity** principle:
- **Sophisticated thinking**: Understanding the trade-offs
- **Simple implementation**: Use tools for what they're good at
- **Practical results**: Working solution over perfect theory

## Migration Path

When poetry2nix matures and handles all packages:
1. Keep the same `pyproject.toml` and `poetry.lock`
2. Switch back to `flake-poetry2nix.nix`
3. No changes needed to the codebase

## Conclusion

The hybrid approach gives us:
- ✅ **Working solution today**
- ✅ **Familiar workflow**
- ✅ **Good enough reproducibility**
- ✅ **Path to pure poetry2nix later**

This is the recommended approach for Luminous Nix and similar Python projects that need both system dependencies and complex Python packages.

---

*"Perfect is the enemy of good. A working hybrid beats a broken pure solution."* 🌊