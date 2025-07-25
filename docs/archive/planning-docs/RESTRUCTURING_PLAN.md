# 📂 Documentation Restructuring Plan

## Current Issues

1. **Scattered Documents**: Many documents are in the root directory instead of docs/
2. **Duplicate Structure**: We have docs/docs/ which is confusing
3. **Mixed Content**: Technical files mixed with documentation
4. **Poor Organization**: Documents not grouped by purpose
5. **Archival Confusion**: Multiple archive directories

## Proposed Structure

```
nix-for-humanity/
├── README.md                    # Main project README
├── QUICKSTART.md               # Quick start guide
├── LICENSE                     # License file
├── CODE_OF_CONDUCT.md          # Community guidelines
├── CONTRIBUTING.md             # Contribution guide
├── CHANGELOG.md                # Release history
│
├── docs/                       # All documentation
│   ├── README.md              # Documentation index
│   ├── VISION.md              # Unified vision (already created)
│   ├── ARCHITECTURE.md        # System architecture
│   ├── SECURITY_REVIEW.md     # Security analysis
│   │
│   ├── philosophy/            # Philosophical foundation ✅
│   │   ├── README.md          # Philosophy overview
│   │   ├── CONSCIOUS_ASPIRING_AI.md
│   │   ├── PARTNERSHIP_PRINCIPLES.md
│   │   ├── EVOLUTION_PATHWAY.md
│   │   └── SACRED_BOUNDARIES.md
│   │
│   ├── guides/                # User-facing guides
│   │   ├── USER_GUIDE.md      # Complete user guide
│   │   ├── PARTNERSHIP_GUIDE.md
│   │   ├── TROUBLESHOOTING.md
│   │   ├── FAQ.md
│   │   └── INSTALLATION.md
│   │
│   ├── technical/             # Technical documentation
│   │   ├── ARCHITECTURE.md    # Detailed architecture
│   │   ├── NLP_ARCHITECTURE.md
│   │   ├── LEARNING_SYSTEM.md
│   │   ├── PLUGIN_ARCHITECTURE.md
│   │   ├── API_REFERENCE.md
│   │   ├── SECURITY.md
│   │   └── DATA_FLOW.md
│   │
│   ├── development/           # Developer documentation
│   │   ├── DEVELOPMENT.md     # Dev environment setup
│   │   ├── CONTRIBUTING.md    # How to contribute
│   │   ├── TESTING.md         # Testing approach
│   │   ├── RELEASE_PROCESS.md
│   │   └── ROADMAP.md
│   │
│   ├── project/               # Project management
│   │   ├── STATUS.md          # Current status
│   │   ├── BUDGET_ANALYSIS.md
│   │   ├── TIMELINE.md
│   │   └── DECISIONS.md
│   │
│   ├── stories/               # User experiences
│   │   ├── FIRST_MEETINGS.md
│   │   ├── GROWTH_MOMENTS.md
│   │   ├── INSIGHTS.md
│   │   └── FUTURE_DREAMS.md
│   │
│   └── archive/               # Old/deprecated docs
│       ├── legacy-gui/
│       ├── old-visions/
│       └── README.md
│
├── src/                       # Source code
├── implementations/           # Implementation code
├── tests/                     # Test suites
├── scripts/                   # Build/deploy scripts
├── examples/                  # Example configurations
└── .claude/                   # Claude context files
```

## Migration Plan

### Phase 1: Clean Up Root Directory

Move these files from root to appropriate locations:

**To docs/project/**
- PROJECT_SUMMARY.md
- PROJECT_COMPLETION_REPORT.md
- PROJECT_CLOSURE_DOCUMENT.md
- DEVELOPMENT_STATUS.md
- MVP_SUMMARY.md

**To docs/technical/**
- ARCHITECTURE_DIAGRAM.md
- TAURI_IPC_ARCHITECTURE.md
- DATA_FLOW_SPECIFICATION.md
- TIMEOUT_STRATEGY.md
- MODULAR_ARCHITECTURE.md

**To docs/development/**
- TAURI_SETUP_COMPLETE.md
- TAURI_IMPLEMENTATION_SUMMARY.md
- MEMORY_UPDATE_PROTOCOL.md
- DOCUMENTATION_SYNTHESIS_COMPLETE.md
- RELEASE_PROCESS.md

**To docs/guides/**
- NATURAL_LANGUAGE_GUIDE.md
- NIX_FOR_HUMANITY_QUICK_REFERENCE.md
- VOICE_SETUP.md
- INSTALL.md

**To docs/archive/old-visions/**
- VISION_2025.md
- NIX_FOR_HUMANITY_VISION.md
- BALANCED_VISION_RECOMMENDATION.md
- AI_SOVEREIGNTY_ALIGNED_VISION.md
- WHAT_WE_ARE_REALLY_BUILDING.md

**To scripts/**
- setup-environment.sh
- test-*.sh scripts
- build-tauri.sh

**To archive or delete:**
- CONSOLIDATION_PLAN.md
- REVISED_CONSOLIDATION_PLAN.md
- FINAL_CONSOLIDATION_PLAN.md
- CLEANUP_PLAN.md
- DOCUMENTATION_CLEANUP_COMPLETE.md
- Various *_SUMMARY.md files

### Phase 2: Consolidate Duplicates

1. Merge docs/docs/ content into docs/
2. Remove duplicate README files
3. Consolidate multiple architecture documents
4. Combine similar guides

### Phase 3: Create Missing Documents

Priority documents to create:
1. docs/guides/USER_GUIDE.md (comprehensive)
2. docs/guides/PARTNERSHIP_GUIDE.md
3. docs/development/DEVELOPMENT.md
4. docs/technical/LEARNING_SYSTEM.md
5. docs/technical/PLUGIN_ARCHITECTURE.md

### Phase 4: Update References

1. Update all internal links
2. Update .claude/CLAUDE.md references
3. Update main README.md
4. Create proper navigation in docs/README.md

## Benefits

1. **Clear Organization**: Easy to find documents
2. **No Duplication**: Single source of truth
3. **Logical Grouping**: Related docs together
4. **Clean Root**: Only essential files at root
5. **Better Navigation**: Clear paths through docs

## Implementation Steps

1. Create new directory structure
2. Move files systematically
3. Update all references
4. Remove empty directories
5. Update documentation index
6. Test all links

Would you like me to proceed with this restructuring?