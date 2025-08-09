# 🧪 Installing pytest in NixOS

## Option 1: Development Shell (Recommended)

This is already configured! Just run:

```bash
cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity
nix-shell
```

Once in the shell, pytest will be available:
```bash
pytest --version
pytest tests/
```

## Option 2: System-Wide Installation

Add to your `/etc/nixos/configuration.nix`:

```nix
environment.systemPackages = with pkgs; [
  # ... other packages ...
  python313Packages.pytest
  python313Packages.pytest-asyncio
  python313Packages.pytest-cov
];
```

Then rebuild:
```bash
sudo nixos-rebuild switch
```

## Option 3: User Profile (Imperative)

For quick testing without system rebuild:

```bash
nix-env -iA nixpkgs.python313Packages.pytest
nix-env -iA nixpkgs.python313Packages.pytest-asyncio
```

## Option 4: Temporary Shell

For one-time use:

```bash
nix-shell -p python313Packages.pytest python313Packages.pytest-asyncio
```

## Running Tests

Once pytest is available:

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest -v tests/

# Run specific test file
pytest tests/integration/test_real_commands.py

# Run with coverage
pytest --cov=backend tests/
```

## Why nix-shell is Recommended

1. **Reproducible**: Same environment for all developers
2. **Isolated**: Doesn't pollute system packages
3. **Version-controlled**: shell.nix is in git
4. **Complete**: Includes all dev dependencies

## Troubleshooting

If pytest is not found:
1. Make sure you're in nix-shell: `echo $IN_NIX_SHELL`
2. Check Python version: `python --version` (should be 3.13.x)
3. Try direct path: `/nix/store/.../bin/pytest`

---

*For Nix for Humanity development, always use `nix-shell` to ensure consistent environment!*