# 🎯 Nix for Humanity Documentation Cleanup Action Plan

## Executive Summary

The Nix for Humanity documentation needs final cleanup to remove 15 loose files from the docs/ root directory and update Claude's context files. This plan provides step-by-step actions to achieve a perfectly organized documentation structure.

## Current Issues

### 1. Loose Files in /docs Root (15 files)
- 5 security-related files
- 3 technical documentation files
- 3 project management files
- 4 archive/meta documentation files

### 2. Outdated Claude Context
- CLAUDE.md references old nested structure (`docs/nix-for-humanity/`)
- Missing documentation structure overview
- No quick reference for current organization

### 3. Missing Critical Documentation
- ❌ Testing philosophy guide
- ❌ Migration guide
- ❌ Additional user stories
- ✅ Glossary (just created!)

## Step-by-Step Actions

### Step 1: Run Cleanup Script
```bash
cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/docs
chmod +x cleanup-docs.sh
./cleanup-docs.sh
```

This will:
- Move all loose files to appropriate subdirectories
- Handle naming conflicts
- Remove empty directories
- Report final status

### Step 2: Merge Duplicate Content

After cleanup, merge these files:

1. **Security Documentation**
   ```bash
   cd security/
   # Merge SECURITY.md and SECURITY_MAIN.md
   cat SECURITY_MAIN.md >> SECURITY.md
   rm SECURITY_MAIN.md
   ```

2. **Roadmap Documentation**
   ```bash
   cd ../project/
   # Merge ROADMAP.md and ROADMAP_MAIN.md
   cat ROADMAP_MAIN.md >> ROADMAP.md
   rm ROADMAP_MAIN.md
   ```

### Step 3: Update CLAUDE.md

Edit `/srv/luminous-dynamics/CLAUDE.md` and replace the Nix for Humanity section with the content from `CLAUDE_CONTEXT_UPDATE.md`.

Key changes:
- Update all documentation paths
- Add documentation structure overview
- Include quick navigation commands

### Step 4: Create Missing Documentation

Priority documents to create:

1. **Testing Philosophy** (`technical/TESTING_PHILOSOPHY.md`)
   - How to test AI partnerships
   - Testing natural language variations
   - Accessibility testing approach

2. **Migration Guide** (`operations/MIGRATION_GUIDE.md`)
   - Version upgrade procedures
   - Data migration steps
   - Rollback procedures

3. **User Stories** (`stories/`)
   - `first-time-user.md`
   - `privacy-conscious-user.md`
   - `accessibility-user.md`

### Step 5: Update Cross-References

Search and update any references to old paths:
```bash
# Find references to old structure
grep -r "docs/nix-for-humanity" . --include="*.md" | grep -v archive

# Find references to moved files
grep -r "docs/SECURITY.md" . --include="*.md"
grep -r "docs/ROADMAP.md" . --include="*.md"
```

### Step 6: Verify Everything Works

1. **Check Documentation Structure**
   ```bash
   ls -la /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/docs/
   # Should show only: README.md, CONTRIBUTING.md, and directories
   ```

2. **Test Links**
   ```bash
   # Simple link checker
   find . -name "*.md" -exec grep -l "@.*\.md" {} \; | head -10
   ```

3. **Verify Claude Context**
   - Start new Claude session
   - Ask about Nix for Humanity documentation
   - Verify correct paths are used

## Expected Final Structure

```
docs/
├── README.md               ✓ (main index)
├── CONTRIBUTING.md         ✓ (contribution guide)
├── guides/                 ✓ (user guides)
├── technical/              ✓ (architecture & implementation)
├── philosophy/             ✓ (vision & principles)
├── project/                ✓ (planning & status)
├── operations/             ✓ (deployment & maintenance)
├── security/               ✓ (security documentation)
├── reference/              ✓ (API & glossary)
├── development/            ✓ (developer resources)
├── error-recovery/         ✓ (error handling)
├── stories/                ✓ (user stories)
├── tutorials/              ✓ (step-by-step guides)
└── archive/                ✓ (historical docs)
```

## Success Criteria

- [x] No loose .md files in docs/ root (except README.md and CONTRIBUTING.md)
- [ ] All files moved to appropriate subdirectories
- [ ] Duplicate content merged
- [ ] CLAUDE.md updated with new paths
- [ ] Cross-references updated
- [ ] New Claude sessions use correct paths
- [x] Glossary created
- [ ] All documentation links work

## Quick Reference Commands

```bash
# Navigate to docs
cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/docs

# Run cleanup
./cleanup-docs.sh

# Check structure
tree -d -L 1

# Find remaining issues
find . -maxdepth 1 -name "*.md" | grep -v -E "(README|CONTRIBUTING).md"

# Update Claude and test
# Edit /srv/luminous-dynamics/CLAUDE.md
# Start new Claude session to verify
```

## Timeline

- **Immediate** (5 min): Run cleanup script
- **Short-term** (15 min): Merge duplicates, update CLAUDE.md
- **Medium-term** (1 hour): Create missing documentation
- **Ongoing**: Maintain organization as project evolves

---

*This action plan ensures Nix for Humanity has perfectly organized, easily navigable documentation that Claude can always reference correctly.*