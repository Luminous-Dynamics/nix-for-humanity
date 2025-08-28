# 🔍 Poetry2nix Blockers: Deep Analysis & Solutions

## Executive Summary

The current blocker preventing pure poetry2nix from working is a **missing architecture mapping** in poetry2nix's internal platform detection code. Specifically, the `riscv64` architecture is not defined in `pep600.nix`, which handles Python wheel platform tags.

**Can we fix it?** Yes, but it requires either:
1. Patching poetry2nix ourselves (moderate difficulty)
2. Waiting for upstream fix (uncertain timeline)
3. Using workarounds (what we're doing now)

## The Specific Error

```
error: attribute 'riscv64' missing
at /nix/store/.../vendor/pyproject.nix/lib/pep600.nix:72:13
```

This occurs when poetry2nix tries to evaluate platform compatibility for Python wheels.

## Root Cause Analysis

### 1. What's Breaking

**File**: `vendor/pyproject.nix/lib/pep600.nix` in poetry2nix
**Line 72**: Checking `pep599.manyLinuxTargetMachines.${tagArch}`
**Issue**: The `riscv64` key doesn't exist in the `manyLinuxTargetMachines` attribute set

### 2. Why It Happens

- **PEP 600** defines "manylinux" platform tags for Python wheels
- poetry2nix needs to map Nix architectures to Python wheel architectures
- The mapping is incomplete - it has `x86_64`, `aarch64`, etc., but NOT `riscv64`

### 3. Triggered By

Certain packages (like `semgrep`, `jsonschema`) have complex wheel distributions that trigger platform checking logic. Even on x86_64 systems, the evaluation tries to check ALL possible platforms, hitting the missing `riscv64` case.

## Is This Within Our Abilities to Fix?

### ✅ YES - We Can Fix It (With Effort)

#### Option 1: Fork & Patch Poetry2nix (Recommended)
```nix
# In our flake.nix
inputs.poetry2nix = {
  url = "github:your-fork/poetry2nix";
  # with patches applied
};
```

**Required Changes**:
1. Add `riscv64 = "riscv64";` to `manyLinuxTargetMachines` in `pep599.nix`
2. Update platform detection logic in `pep600.nix`
3. Test with our packages

**Effort**: 2-4 hours
**Maintenance**: Need to sync with upstream

#### Option 2: Override at Flake Level
```nix
# Override the problematic packages to skip platform checks
overrides = defaultPoetryOverrides.extend (self: super: {
  semgrep = null;  # Skip entirely
  jsonschema = super.jsonschema.overridePythonAttrs (old: {
    # Skip platform checks
    pythonImportsCheck = [];
  });
});
```

**Effort**: 1 hour
**Limitation**: Per-package fixes, not systemic

#### Option 3: Contribute Upstream
- Submit PR to poetry2nix adding riscv64 support
- Current issue: poetry2nix is looking for maintainers (adisbladis stepped down)
- Timeline: Uncertain

## Current Workarounds

### 1. Hybrid Approach (What We're Using) ✅
- Nix provides system deps
- Poetry manages Python packages
- **Pro**: Always works
- **Con**: Not fully reproducible

### 2. Skip Problematic Packages
```nix
extras = [ "tui" "voice" "docs" ];  # Skip "security" which has semgrep
```
- **Pro**: Pure poetry2nix for most packages
- **Con**: Missing functionality

### 3. Use Wheels Only
```nix
preferWheels = true;  # Avoid building from source
```
- **Pro**: Reduces platform checks
- **Con**: Still hits evaluation issues

## The Fix: Patch File

Here's the actual patch needed for poetry2nix:

```diff
# vendor/pyproject.nix/lib/pep599.nix
manyLinuxTargetMachines = {
  x86_64 = "x86_64";
  i686 = "i686";
  aarch64 = "aarch64";
  ppc64le = "ppc64le";
  s390x = "s390x";
+ riscv64 = "riscv64";  # Add this line
};
```

## Alternative Solutions

### 1. Switch to uv2nix
```toml
# Use uv instead of Poetry
[tool.uv]
dependencies = [...]
```
- Modern Python package manager
- Better Nix integration planned
- Still experimental

### 2. Use dream2nix
```nix
inputs.dream2nix.url = "github:nix-community/dream2nix";
```
- More flexible than poetry2nix
- Supports multiple package managers
- More complex setup

### 3. Manual Python Packages
```nix
# Define packages manually in Nix
pythonEnv = pkgs.python3.withPackages (ps: with ps; [
  click
  pydantic
  # ... all deps
]);
```
- Full control
- Most work
- Most reproducible

## Recommendation

### Short Term (Now)
Continue with **hybrid approach** - it works perfectly and gives us:
- Quick iteration
- No blocking issues
- Good enough reproducibility

### Medium Term (Next Month)
**Fork poetry2nix** and apply the riscv64 patch:
1. Fork poetry2nix repo
2. Apply patch to pep599.nix
3. Test with our project
4. Use our fork in flake.nix

### Long Term (Next Year)
Monitor alternatives:
- **uv2nix** when it matures
- **poetry2nix** if it gets new maintainers
- **dream2nix** for complex scenarios

## Technical Details for Implementation

### To Fork & Fix:
```bash
# 1. Fork poetry2nix
gh repo fork nix-community/poetry2nix

# 2. Clone your fork
git clone https://github.com/YOUR-USER/poetry2nix
cd poetry2nix

# 3. Apply fix
cat >> vendor/pyproject.nix/lib/pep599.nix << 'EOF'
  riscv64 = "riscv64";
EOF

# 4. Commit & push
git add -A
git commit -m "Add riscv64 architecture support"
git push

# 5. Use in flake
# inputs.poetry2nix.url = "github:YOUR-USER/poetry2nix";
```

### To Test the Fix:
```nix
# Create minimal test flake
{
  inputs.poetry2nix.url = "github:YOUR-USER/poetry2nix";
  outputs = { poetry2nix, ... }: {
    # Test with problematic packages
  };
}
```

## Conclusion

The poetry2nix blocker is **fixable** with moderate effort. The issue is a simple missing architecture mapping, not a fundamental design problem.

**Our Recommendation**: The hybrid approach works great for now. If we need pure poetry2nix later, forking and patching is straightforward (2-4 hours of work).

The blocker exists because:
1. poetry2nix tries to be exhaustive in platform checking
2. RISC-V is still emerging in the Python ecosystem
3. poetry2nix needs active maintenance

**Bottom Line**: We can fix it, but the hybrid approach is actually more pragmatic for active development anyway!

---

*"Sometimes the pragmatic solution is the sophisticated one."* 🌊