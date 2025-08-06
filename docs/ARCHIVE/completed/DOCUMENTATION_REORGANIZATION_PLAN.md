# 📁 Documentation Reorganization Plan - Nix for Humanity

**Created**: 2025-07-25
**Purpose**: Organize scattered documentation into a coherent structure
**Status**: Ready for implementation

## 🔍 Current Situation

Our documentation is scattered across:
- Root directory (20+ docs)
- `.claude/` directory (context files)
- `implementations/web-based/docs/` (technical docs)
- `archive/` (old versions)
- Various subdirectories

## 🎯 Goal

Create a single, well-organized `docs/` directory that:
- Makes documentation easy to find
- Eliminates duplicates
- Maintains clear categories
- Preserves important content
- Follows standard conventions

## 📋 Reorganization Actions

### Phase 1: Create New Structure

```bash
# Create the new directory structure
mkdir -p docs/{guides,tutorials,technical,operations,project,philosophy,security,reference,stories,archive}
```

### Phase 2: Move & Consolidate Documentation

#### Root Directory Cleanup

| Current Location | New Location | Action |
|-----------------|--------------|--------|
| `/README.md` | `/README.md` | Keep (standard) |
| `/CONTRIBUTING.md` | `/docs/CONTRIBUTING.md` | Move (standard location) |
| `/CHANGELOG.md` | `/CHANGELOG.md` | Keep (standard) |
| `/LICENSE` | `/LICENSE` | Keep (standard) |
| `/SECURITY.md` | `/docs/security/SECURITY.md` | Move |
| `/QUICKSTART.md` | `/docs/guides/QUICKSTART.md` | Move |
| `/FAQ.md` | `/docs/guides/FAQ.md` | Move |
| `/TROUBLESHOOTING.md` | `/docs/guides/TROUBLESHOOTING.md` | Move |
| `/ARCHITECTURE.md` | `/docs/technical/ARCHITECTURE.md` | Move |
| `/ROADMAP.md` | `/docs/project/ROADMAP.md` | Move |
| `/CLAUDE.md` | `/.claude/CONTEXT.md` | Move to .claude |
| `/STATUS.md` | `/docs/project/STATUS.md` | Move |
| `/VISION_2025.md` | `/docs/project/VISION.md` | Move & rename |

#### Technical Documentation

| Current Location | New Location | Action |
|-----------------|--------------|--------|
| `implementations/web-based/docs/*.md` | `docs/technical/` | Move up |
| `/NLP_ARCHITECTURE.md` | `docs/technical/NLP_ARCHITECTURE.md` | Move |
| `/PLUGIN_ARCHITECTURE.md` | `docs/technical/PLUGIN_ARCHITECTURE.md` | Move |
| `/TECHNICAL_ARCHITECTURE.md` | `docs/technical/SYSTEM_ARCHITECTURE.md` | Merge duplicates |
| `/API_DOCUMENTATION.md` | `docs/reference/API_REFERENCE.md` | Move & update |

#### User Documentation

| Current Location | New Location | Action |
|-----------------|--------------|--------|
| `/USER_GUIDE.md` | `docs/guides/USER_GUIDE.md` | Move |
| `/NATURAL_LANGUAGE_GUIDE.md` | `docs/guides/NATURAL_LANGUAGE.md` | Move |
| `/VOICE_SETUP.md` | `docs/guides/VOICE_SETUP.md` | Move |
| `/INSTALLATION_GUIDE.md` | `docs/guides/INSTALLATION.md` | Move |
| `examples/` | `docs/tutorials/examples/` | Move |
| User stories | `docs/stories/` | Already there ✓ |

#### Operations Documentation

| Current Location | New Location | Action |
|-----------------|--------------|--------|
| `/DEPLOYMENT_CHECKLIST.md` | `docs/operations/DEPLOYMENT_CHECKLIST.md` | Move |
| `/PRODUCTION_DEPLOYMENT.md` | `docs/operations/DEPLOYMENT.md` | Merge |
| `/RELEASE_PROCESS.md` | `docs/operations/RELEASE_PROCESS.md` | Move |
| `/MONITORING.md` | `docs/operations/MONITORING.md` | Move |

### Phase 3: Handle Duplicates

#### Merge These Duplicates:

1. **Architecture Documents**
   - `ARCHITECTURE.md` + `TECHNICAL_ARCHITECTURE.md` + `SYSTEM_ARCHITECTURE_DIAGRAM.md`
   - → Merge into `docs/technical/ARCHITECTURE.md`

2. **User Guides**
   - `USER_GUIDE.md` + `QUICKSTART_USER_GUIDE.md` + `NATURAL_LANGUAGE_GUIDE.md`
   - → Keep separate but cross-reference

3. **Development Guides**
   - `DEVELOPMENT.md` + `DEVELOPER_GUIDE.md` + `CONTRIBUTING.md`
   - → Merge into comprehensive `docs/CONTRIBUTING.md`

4. **Vision Documents**
   - `VISION.md` + `VISION_2025.md` + `VISION_FINAL.md`
   - → Merge into single `docs/project/VISION.md`

### Phase 4: Archive Old Documentation

```bash
# Move old/outdated docs
mkdir -p docs/archive/2025-01-reorganization

# Move superseded documents
mv archive/legacy-gui-docs docs/archive/
mv archive/2025-01-cleanup docs/archive/
```

### Phase 5: Create Index Files

Create README.md in each directory:

#### `docs/README.md`
```markdown
# 📚 Nix for Humanity Documentation

## Quick Links
- [Quickstart Guide](./guides/QUICKSTART.md) - Get started in 5 minutes
- [User Guide](./guides/USER_GUIDE.md) - Complete user documentation
- [API Reference](./reference/API_REFERENCE.md) - Developer API
- [Contributing](./CONTRIBUTING.md) - How to contribute

## Documentation Structure
- `guides/` - User guides and tutorials
- `technical/` - Architecture and implementation
- `operations/` - Deployment and maintenance
- `project/` - Project management docs
- `philosophy/` - Design philosophy
- `security/` - Security documentation
- `reference/` - API and configuration
- `stories/` - User stories and examples
```

## 📊 Final Structure

```
nix-for-humanity/
├── README.md                     # Project introduction
├── CHANGELOG.md                  # Version history
├── LICENSE                       # License file
├── .claude/                      # Claude context
│   ├── CONTEXT.md               # Main context file
│   └── *.md                     # Other context files
├── docs/                        # All documentation
│   ├── README.md                # Documentation index
│   ├── CONTRIBUTING.md          # Contribution guide
│   ├── guides/                  # User guides
│   │   ├── README.md           # Guides index
│   │   ├── QUICKSTART.md       # 5-minute intro
│   │   ├── INSTALLATION.md     # Installation guide
│   │   ├── USER_GUIDE.md       # Complete guide
│   │   ├── NATURAL_LANGUAGE.md # NL interaction
│   │   ├── VOICE_SETUP.md      # Voice configuration
│   │   ├── FAQ.md              # Common questions
│   │   └── TROUBLESHOOTING.md  # Problem solving
│   ├── tutorials/               # Step-by-step tutorials
│   │   ├── README.md           # Tutorials index
│   │   ├── basic/              # Beginner tutorials
│   │   ├── advanced/           # Advanced tutorials
│   │   └── examples/           # Code examples
│   ├── technical/               # Technical docs
│   │   ├── README.md           # Technical index
│   │   ├── ARCHITECTURE.md     # System architecture
│   │   ├── NLP_ARCHITECTURE.md # NLP design
│   │   ├── API_REFERENCE.md    # API documentation
│   │   ├── TESTING_PHILOSOPHY.md # Testing approach
│   │   └── CONFIGURATION_REFERENCE.md # Config options
│   ├── operations/              # Operational docs
│   │   ├── README.md           # Operations index
│   │   ├── DEPLOYMENT.md       # Deployment guide
│   │   ├── MONITORING.md       # Monitoring setup
│   │   ├── BACKUP.md           # Backup procedures
│   │   └── TROUBLESHOOTING.md  # Ops troubleshooting
│   ├── project/                 # Project management
│   │   ├── README.md           # Project index
│   │   ├── VISION.md           # Project vision
│   │   ├── ROADMAP.md          # Development roadmap
│   │   ├── STATUS.md           # Current status
│   │   └── BUDGET.md           # Budget analysis
│   ├── philosophy/              # Design philosophy
│   │   └── (existing files)    # Already organized ✓
│   ├── security/                # Security docs
│   │   ├── README.md           # Security index
│   │   ├── SECURITY.md         # Security policy
│   │   └── THREAT_MODEL.md     # Threat analysis
│   ├── reference/               # Reference material
│   │   ├── README.md           # Reference index
│   │   ├── API_REFERENCE.md    # Complete API
│   │   ├── CONFIGURATION.md    # Config reference
│   │   └── GLOSSARY.md         # Term definitions
│   ├── stories/                 # User stories
│   │   └── (existing files)    # Already organized ✓
│   └── archive/                 # Old documentation
│       ├── README.md           # Archive index
│       └── 2025-01/            # By date
└── src/                         # Source code
```

## 🚀 Implementation Script

```bash
#!/bin/bash
# reorganize-docs.sh

echo "🚀 Starting documentation reorganization..."

# Create new structure
echo "📁 Creating directory structure..."
mkdir -p docs/{guides,tutorials,technical,operations,project,philosophy,security,reference,stories,archive}

# Move files (with git mv to preserve history)
echo "📦 Moving documentation files..."

# Guides
git mv QUICKSTART.md docs/guides/ 2>/dev/null || true
git mv FAQ.md docs/guides/ 2>/dev/null || true
git mv TROUBLESHOOTING.md docs/guides/ 2>/dev/null || true

# Technical
git mv ARCHITECTURE.md docs/technical/ 2>/dev/null || true
git mv NLP_ARCHITECTURE.md docs/technical/ 2>/dev/null || true

# Project
git mv ROADMAP.md docs/project/ 2>/dev/null || true
git mv STATUS.md docs/project/ 2>/dev/null || true
git mv VISION_2025.md docs/project/VISION.md 2>/dev/null || true

# Security
git mv SECURITY.md docs/security/ 2>/dev/null || true

# Create index files
echo "📝 Creating index files..."
# ... (create README.md files)

echo "✅ Reorganization complete!"
echo "📋 Next steps:"
echo "  1. Review moved files"
echo "  2. Update internal links"
echo "  3. Merge duplicate content"
echo "  4. Commit changes"
```

## 📝 Post-Reorganization Tasks

1. **Update all internal links** in documentation
2. **Update .claude/CONTEXT.md** with new paths
3. **Update root README.md** to point to new docs
4. **Create missing index files** (README.md in each dir)
5. **Test all documentation links**
6. **Update CI/CD** if it references doc paths

## ✅ Success Criteria

- [ ] All documentation in `docs/` directory
- [ ] No duplicate content
- [ ] Clear category structure
- [ ] Every directory has README.md
- [ ] All internal links updated
- [ ] Archive preserves old versions
- [ ] Root directory only has standard files
- [ ] Claude context updated

## 🎯 Benefits

1. **Discoverability** - Easy to find what you need
2. **Maintainability** - Clear where to add new docs
3. **Consistency** - Standard structure
4. **Version Control** - Clean git history
5. **Collaboration** - Everyone knows where things go

---

*"A place for everything, and everything in its place."*