# 🚀 Poetry2nix Integration - Complete Guide

## Overview

Your `flake.nix` is now fully integrated with poetry2nix! This gives you:
- ✅ **Reproducible builds** - Same dependencies everywhere
- ✅ **Poetry workflow** - Keep using familiar tools
- ✅ **Nix benefits** - Binary caching, isolated environments
- ✅ **Zero conflicts** - Each project has its own Python

## Quick Start

### Using the New Flake

```bash
# Enter development shell with all dependencies
nix develop

# Run the application directly
nix run .#ask-nix -- "install firefox"

# Build the package
nix build

# Run tests in CI environment
nix develop .#ci -c pytest tests/

# Serve documentation
nix develop .#docs -c mkdocs serve
```

### Key Benefits Over Standard Poetry

1. **Reproducibility**: Lock files guarantee exact same versions
2. **Binary caching**: Share built packages across machines
3. **System dependencies**: Automatically handles C libraries
4. **Multiple Python versions**: Test against different versions easily
5. **Docker images**: Build minimal containers automatically

## How It Works

### The Integration Flow

```mermaid
graph LR
    A[pyproject.toml] --> B[poetry.lock]
    B --> C[poetry2nix]
    C --> D[Nix derivation]
    D --> E[Binary package]
```

1. **Poetry manages** dependencies in `pyproject.toml`
2. **Poetry locks** exact versions in `poetry.lock`
3. **poetry2nix converts** to Nix expressions
4. **Nix builds** reproducible packages
5. **You get** perfect environments every time

## Common Tasks

### Add a New Dependency

```bash
# Add with Poetry as usual
poetry add numpy

# Update the lock file
poetry lock

# Rebuild Nix environment
nix develop --refresh
```

### Update All Dependencies

```bash
# Update Poetry dependencies
poetry update

# Rebuild Nix environment
nix develop --refresh
```

### Build Docker Image

```bash
# Build minimal Docker image
nix build .#docker

# Load into Docker
docker load < result

# Run the container
docker run luminous-nix:latest "help"
```

### Deploy to Production

```bash
# Build the application
nix build

# The result is in ./result/bin/ask-nix
./result/bin/ask-nix "help"

# Copy to production
nix copy ./result --to ssh://production-server
```

## Handling Problem Packages

Some Python packages need special handling. The flake already handles:

- **duckdb** - Needs pybind11
- **chromadb** - Needs setuptools
- **tree-sitter** - Needs compilation support
- **llama-cpp-python** - Needs cmake

### Adding New Overrides

Edit `flake.nix`:

```nix
pypkgs-build-requirements = {
  # Your problematic package
  some-package = [ "build-dep1" "build-dep2" ];
  # ...existing overrides...
};
```

## Development Workflow

### Standard Development

```bash
# Enter shell with all tools
nix develop

# Your Poetry environment is ready!
ask-nix help
pytest tests/
mkdocs serve
```

### CI/CD Pipeline

```yaml
# GitHub Actions example
- name: Install Nix
  uses: cachix/install-nix-action@v22
  
- name: Run tests
  run: nix develop .#ci -c pytest tests/

- name: Build package
  run: nix build

- name: Build docs
  run: nix develop .#docs -c mkdocs build
```

### Multiple Python Versions

Create additional shells in `flake.nix`:

```nix
devShells.python311 = pkgs.mkShell {
  buildInputs = [
    (mkPoetryEnv {
      projectDir = ./.;
      python = pkgs.python311;
    })
  ];
};
```

Test with: `nix develop .#python311`

## Troubleshooting

### Package Build Failures

```bash
# See detailed build errors
nix build --verbose

# Use pre-built wheels (faster)
# Already configured with preferWheels = true
```

### Missing System Dependencies

```bash
# Add to devShell buildInputs
buildInputs = with pkgs; [
  # Add your system dependency
  libxml2
  # ...existing...
];
```

### Poetry Lock Sync Issues

```bash
# Ensure lock file is up to date
poetry lock --no-update

# Force Nix to rebuild
nix develop --refresh --rebuild
```

## Advanced Features

### Jupyter Notebooks

```nix
# Add Jupyter to dev environment
devShells.jupyter = pkgs.mkShell {
  buildInputs = [
    (mkPoetryEnv {
      projectDir = ./.;
      groups = [ "dev" "jupyter" ];
    })
  ];
  shellHook = ''
    jupyter lab
  '';
};
```

### GPU Support (CUDA)

```nix
# Use CUDA-enabled nixpkgs
devShells.cuda = pkgs.mkShell {
  buildInputs = with pkgs; [
    cudatoolkit
    (mkPoetryEnv {
      projectDir = ./.;
      # GPU packages
    })
  ];
};
```

### Cross-compilation

```nix
# Build for different architectures
packages.aarch64 = 
  (import nixpkgs { 
    system = "aarch64-linux"; 
  }).callPackage ./. {};
```

## Benefits Summary

| Feature | Poetry Alone | Poetry + poetry2nix |
|---------|-------------|---------------------|
| Dependency Management | ✅ | ✅ |
| Lock Files | ✅ | ✅ |
| Virtual Environments | ✅ | ✅ |
| Reproducible Builds | ❌ | ✅ |
| Binary Caching | ❌ | ✅ |
| System Dependencies | ⚠️ Manual | ✅ Automatic |
| Docker Images | ⚠️ Dockerfile | ✅ One command |
| Multiple Python Versions | ⚠️ pyenv | ✅ Native |
| CI/CD Integration | ⚠️ Complex | ✅ Simple |

## Migration Checklist

- [x] Added poetry2nix input to flake
- [x] Converted to mkPoetryApplication
- [x] Added build overrides for problem packages
- [x] Created development shells
- [x] Added documentation environment
- [x] Set up CI shell
- [x] Added Docker image output
- [x] Configured apps for `nix run`
- [x] Added test runner for CI

## Next Steps

1. **Test the new setup**:
   ```bash
   nix develop
   ask-nix help
   ```

2. **Update CI/CD** to use Nix commands

3. **Share binary cache** with team using Cachix

4. **Deploy with confidence** - same build everywhere!

## Resources

- [Poetry2nix Documentation](https://github.com/nix-community/poetry2nix)
- [Poetry Documentation](https://python-poetry.org/)
- [Nix Flakes](https://nixos.wiki/wiki/Flakes)
- [Cachix for Binary Caching](https://cachix.org/)

---

*With poetry2nix, you get the best of both worlds: Poetry's excellent Python dependency management with Nix's unparalleled reproducibility and deployment capabilities.* 🎉