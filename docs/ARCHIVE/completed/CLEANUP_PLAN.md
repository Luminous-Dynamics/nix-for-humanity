# 🧹 Nix for Humanity - Thoughtful Cleanup Plan

## 🎯 Goals
1. Preserve all active work
2. Create clear, single source of truth
3. Make development path obvious
4. Archive (not delete) historical implementations
5. Simplify build process

## 📊 Current State Analysis

### Active Development (Keep & Organize)
- `implementations/web-based/` - Main active development (TypeScript, full test suite)
- `implementations/desktop/` - Tauri wrapper for desktop app
- `docs/` - Comprehensive documentation
- `.claude/` - Context files for AI assistance

### Shared Components (Consolidate)
- `implementations/core/`
- `implementations/nlp/`
- `implementations/security/`
- `implementations/server/`

### Duplicates & Legacy (Archive)
- `implementations/implementations/` - Nested duplicate
- `src-tauri/` - Duplicate of desktop implementation  
- `frontend/` - Old structure
- `backend/` - Old structure
- `legacy-mvp-v2/` - Already marked as legacy
- Multiple shell.nix files scattered around

### Experimental (Evaluate)
- `implementations/gui-learning/` - Progressive GUI concept
- `implementations/monitoring/` - Usage analytics
- `implementations/nlp-core/` - Might overlap with nlp/

## 📋 Cleanup Steps (In Order)

### Phase 1: Create Archive Structure
```bash
# Create archive directory
mkdir -p archive/2025-01-cleanup

# Document what we're archiving
echo "# Archive from 2025-01-24 Cleanup" > archive/2025-01-cleanup/README.md
echo "These directories were archived during consolidation" >> archive/2025-01-cleanup/README.md
```

### Phase 2: Archive Obvious Duplicates
```bash
# Move nested duplicate
mv implementations/implementations archive/2025-01-cleanup/

# Move root-level duplicates
mv src-tauri archive/2025-01-cleanup/
mv frontend archive/2025-01-cleanup/
mv backend archive/2025-01-cleanup/

# Move legacy
mv legacy-mvp-v2 archive/2025-01-cleanup/
```

### Phase 3: Consolidate Shared Components
```bash
# Create shared directory
mkdir -p implementations/shared

# Move shared components
mv implementations/core implementations/shared/
mv implementations/nlp implementations/shared/
mv implementations/security implementations/shared/
mv implementations/server implementations/shared/
```

### Phase 4: Evaluate Experimental
```bash
# Check if these have unique value
# - implementations/nlp-core/ (might duplicate shared/nlp)
# - implementations/gui-learning/ (keep if unique approach)
# - implementations/monitoring/ (keep if adds value)
```

### Phase 5: Consolidate Build Files
```bash
# Keep main shell.nix at root
# Move specialized shells to their directories
mv shell-*.nix archive/2025-01-cleanup/build-variants/

# Update flake.nix to reference consolidated structure
```

### Phase 6: Update Documentation
- Update paths in CLAUDE.md
- Update paths in .claude/PROJECT_STATUS.md
- Update README.md with new structure
- Create ARCHITECTURE.md showing new layout

## 🎯 Target Structure

```
nix-for-humanity/
├── implementations/
│   ├── web-based/          # ← PRIMARY: Web interface
│   │   ├── js/            # TypeScript source
│   │   ├── tests/         # Comprehensive tests
│   │   ├── plugins/       # Plugin system
│   │   └── docs/          # Implementation docs
│   ├── desktop/           # ← SECONDARY: Tauri wrapper
│   │   ├── src-tauri/     # Rust backend
│   │   └── src/           # Web frontend
│   └── shared/            # ← SHARED: Common components
│       ├── core/          # Core functionality
│       ├── nlp/           # NLP engine
│       ├── security/      # Security layer
│       └── server/        # Backend services
├── docs/                  # Project documentation
├── .claude/              # AI context files
├── archive/              # Historical implementations
├── flake.nix            # Nix configuration
├── shell.nix            # Development shell
└── README.md            # Project overview
```

## ⚠️ Before We Start

### Backup Command
```bash
# Create a full backup first
tar -czf ~/nix-for-humanity-backup-$(date +%Y%m%d-%H%M%S).tar.gz .
```

### Verification Checklist
- [ ] All tests still pass in web-based
- [ ] Desktop app still builds
- [ ] Documentation links work
- [ ] No broken imports
- [ ] Git history preserved

## 🤔 Questions to Resolve

1. **Primary Implementation**: Confirm web-based is the main focus?
2. **Desktop Priority**: Is Tauri desktop app still needed?
3. **Experimental Features**: Which experimental directories add value?
4. **Build System**: One shell.nix or keep variants?
5. **Git Strategy**: One big cleanup commit or step-by-step?

## 📊 Success Metrics

- ✅ One clear implementation path
- ✅ No duplicate code
- ✅ All active work preserved
- ✅ Simpler build process
- ✅ Clear documentation
- ✅ Easy onboarding for new contributors

## 💭 Philosophy

This cleanup follows the principle of "sacred simplicity" - removing confusion while honoring all the work that brought us here. We archive rather than delete, consolidate rather than scatter, and clarify rather than complicate.

---

*"Simplicity is the ultimate sophistication" - Leonardo da Vinci*