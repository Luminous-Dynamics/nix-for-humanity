# Documentation Cleanup Plan

## Immediate Cleanup Tasks

### 1. Remove Duplicates
- [ ] Consolidate 3 copies of API.md
- [ ] Merge duplicate ARCHITECTURE.md files
- [ ] Remove conflicting FAQ.md versions
- [ ] Consolidate security documentation

### 2. Fix Naming Inconsistencies
- [ ] Replace all "NixOS GUI" with "Nix for Humanity"
- [ ] Update "MVP v2" references to current vision
- [ ] Align file naming conventions

### 3. Reorganize Structure
```
docs/
├── user/                    # User-facing docs
│   ├── getting-started.md
│   ├── voice-commands.md
│   └── troubleshooting.md
├── developer/              # Developer docs
│   ├── architecture/
│   ├── api/
│   └── contributing.md
├── operations/             # Deployment & ops
│   ├── installation.md
│   ├── configuration.md
│   └── monitoring.md
└── reference/              # Reference materials
    ├── nlp-patterns.md
    ├── glossary.md
    └── faq.md
```

### 4. Archive Legacy Content
- [ ] Move old GUI docs to `legacy/`
- [ ] Archive completed implementation plans
- [ ] Keep historical context but separate

## Priority Documentation to Create

### Before Starting Development

1. **NLP Implementation Guide** (CRITICAL)
2. **Voice Interface Specification** (CRITICAL)
3. **System Requirements** (HIGH)
4. **Development Environment Setup** (HIGH)
5. **Testing Strategy** (HIGH)