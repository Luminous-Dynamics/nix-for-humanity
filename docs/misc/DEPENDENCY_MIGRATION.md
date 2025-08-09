# Dependency Management Migration Guide

## Current State

The project has conflicting dependency management:
- `pyproject.toml` - Poetry configuration (source of truth)
- `flake.nix` - Nix flake with manual Python packages
- Legacy `requirements*.txt` files

## Target State

Single source of truth using Poetry + poetry2nix:
- `pyproject.toml` - Define all dependencies
- `poetry.lock` - Lock versions
- `flake.nix` - Use poetry2nix to read pyproject.toml

## Migration Steps

### 1. Update flake.nix

Replace manual package list with poetry2nix:

```nix
poetryEnv = poetry2nix-lib.mkPoetryEnv {
  projectDir = ./.;
  python = pkgs.python311;
  preferWheels = true;
};
```

### 2. Remove Manual Lists

Delete any manual Python package lists from flake.nix.

### 3. Lock Dependencies

```bash
poetry lock
```

### 4. Test Environment

```bash
nix develop
./scripts/test-dev-env.sh
```

## Benefits

- Single source of truth for dependencies
- Reproducible environments
- No version conflicts
- Easier dependency updates

## Common Issues

### "Module not found" in Nix

Add to pyproject.toml, not flake.nix:
```bash
poetry add package-name
```

### Different Python versions

Ensure flake.nix uses same Python as pyproject.toml:
```toml
[tool.poetry.dependencies]
python = "^3.11"
```

### Optional dependencies

Use Poetry groups:
```toml
[tool.poetry.group.voice.dependencies]
openai-whisper = "^20231117"
```

## Validation

Run regularly:
```bash
./scripts/validate-deps.sh
```
