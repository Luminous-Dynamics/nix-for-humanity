# 📦 How to Add/Install Dependencies in Luminous Nix

## 🚨 CRITICAL: Three-Step Process Required

When adding new dependencies to Luminous Nix, you MUST update THREE places and then install:

### Step 1: Update pyproject.toml
Add the dependency to the appropriate section:
```toml
[tool.poetry.dependencies]
new-package = "^1.0.0"  # Main dependencies
# OR
[tool.poetry.group.dev.dependencies]
dev-package = "^2.0.0"  # Development dependencies
```

### Step 2: Update shell.nix (for Nix shell)
Add the Python package to the Nix shell environment:
```nix
buildInputs = with pkgs; [
  # ...
  python313Packages.new-package  # Add here for Nix shell
  # ...
];
```

### Step 3: Update flake.nix (for Nix flake users)
Add to the flake's devShell packages:
```nix
devShells.default = pkgs.mkShell {
  packages = with pkgs; [
    # ...
    python313Packages.new-package  # Add here too
    # ...
  ];
};
```

### Step 4: Install with Poetry
```bash
# Update lock file if needed
poetry lock

# Install dependencies
poetry install

# Or add directly (this updates pyproject.toml automatically)
poetry add new-package
poetry add --group dev dev-package
```

## ⚠️ Common Pitfalls

### ❌ WRONG: Only updating pyproject.toml
```bash
# Just editing pyproject.toml doesn't install anything!
vim pyproject.toml  # Add dependency
python -c "import new_package"  # ❌ ModuleNotFoundError
```

### ❌ WRONG: Only updating shell.nix
```bash
# Nix shell provides the package but Poetry doesn't know about it
nix-shell  # Has the package
poetry run python -c "import new_package"  # ❌ Still fails
```

### ✅ CORRECT: Complete process
```bash
# 1. Add to pyproject.toml (or use poetry add)
poetry add tree-sitter

# 2. Update shell.nix and flake.nix
vim shell.nix  # Add python313Packages.tree-sitter
vim flake.nix  # Add to devShell packages

# 3. Update lock and install
poetry lock
poetry install

# 4. Rebuild nix shell if needed
exit  # Exit current nix-shell
nix-shell  # Enter fresh shell with new packages

# 5. Test
poetry run python -c "import tree_sitter"  # ✅ Works!
```

## 🎯 Real Example: Tree-sitter Installation

This is what happened with tree-sitter:

1. **Phase A-Prime** added tree-sitter to configuration files ✅
2. **BUT** never ran `poetry install` ❌
3. **Result**: Code written assuming tree-sitter was available, but it wasn't installed

**The Fix**:
```bash
# Check current status
poetry show tree-sitter  # Not found

# Fix version conflicts if needed
vim pyproject.toml  # Update versions

# Lock and install
poetry lock
poetry install

# Now it works!
poetry run python -c "import tree_sitter"  # ✅
```

## 📝 Best Practices

1. **Always use Poetry for Python dependencies** - It manages virtual environments properly
2. **Update all three config files** - pyproject.toml, shell.nix, flake.nix
3. **Test after installing** - Don't assume it worked
4. **Commit lock file** - poetry.lock ensures reproducible builds
5. **Document special requirements** - If a package needs system libraries, note it

## 🔧 Troubleshooting

### "Module not found" after adding to pyproject.toml
- Did you run `poetry install`?
- Are you using `poetry run python` or just `python`?

### Version conflicts
- Check `poetry.lock` for conflicting versions
- Use `poetry show --tree` to see dependency tree
- Update version constraints in pyproject.toml

### Nix shell not finding package
- Exit and re-enter nix-shell
- Check if package name is correct in shell.nix
- Some Python packages have different names in Nix (python313Packages.xxx)

## 🌟 Remember

**Configuration ≠ Installation**

Just because you wrote it in a config file doesn't mean it's installed. Always:
1. Configure (pyproject.toml, shell.nix, flake.nix)
2. Install (poetry install)
3. Verify (import test)

---

*Last Updated: After tree-sitter integration confusion*
*Lesson: Writing configuration is not the same as installing dependencies!*