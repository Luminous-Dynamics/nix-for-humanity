# File Structure Cleanup Plan for v1.0.0

## Quick Wins (Do Now)

### 1. Move Development Scripts to scripts/
```bash
mv fix_*.py scripts/
mv prepare-release.sh scripts/
mv test_tui_connection.py tests/
```

### 2. Archive Development Journals
```bash
mkdir -p docs/archive/development-journals
mv TESTING_JOURNAL.md docs/archive/development-journals/
mv WEEK3_*.md docs/archive/development-journals/
mv PERSONAL_TESTING_PLAN.md docs/archive/development-journals/
mv DOGFOODING_CHECKLIST.md docs/archive/development-journals/
mv DAILY_USE_SETUP.md docs/archive/development-journals/
mv FEEDBACK_CAPTURE.md docs/archive/development-journals/
```

### 3. Archive Test Reports
```bash
mkdir -p docs/archive/test-reports
mv v1_*.md docs/archive/test-reports/
mv documentation_check_results.json docs/archive/test-reports/
mv week3_metrics.json docs/archive/test-reports/
mv production-readiness-report.md docs/archive/test-reports/
```

### 4. Remove Broken Symlinks
```bash
rm backend-primary
rm frontend-primary
```

### 5. Move Database to data/
```bash
mkdir -p data/databases
mv nixos_knowledge.db data/databases/
```

### 6. Clean Documentation Status Files
```bash
# Keep only essential status files
mkdir -p docs/archive/status-history
mv docs/status/*.md docs/archive/status-history/

# Keep only these in docs/status/:
# - CURRENT_STATE.md
# - V1_RELEASE_STATUS.md (create new)
```

### 7. Archive Old Documentation
```bash
mv DOCUMENTATION_*.md docs/archive/
mv rough-edges-summary.txt docs/archive/
```

## Ideal v1.0.0 Structure

```
nix-for-humanity/
├── src/                    # Python source code
├── tests/                  # All test files
├── bin/                    # User-facing scripts
├── scripts/                # Development scripts
├── docs/                   # User documentation
│   ├── getting-started/
│   ├── tutorials/
│   ├── reference/
│   └── archive/           # Old docs
├── examples/              # Usage examples
├── data/                  # Runtime data
├── release/               # Release artifacts
├── archive/               # Historical files
├── flake.nix             # Nix configuration
├── pyproject.toml        # Python project
├── README.md             # Project overview
├── CHANGELOG.md          # Version history
├── LICENSE               # License file
└── VERSION               # Current version
```

## Benefits

1. **Cleaner Root**: Only essential files remain
2. **Better Organization**: Everything has a proper place
3. **Easier Navigation**: Users find what they need
4. **Professional Appearance**: Ready for public release

## Don't Do (Yet)

- Don't reorganize src/ structure (too risky)
- Don't move core config files (flake.nix, pyproject.toml)
- Don't delete anything (archive instead)