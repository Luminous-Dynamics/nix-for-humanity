# 📋 Luminous Nix Release Checklist

## 🚨 CRITICAL: Every Release MUST Include Standalone Executables

**Why**: Users should NEVER need Poetry to use Luminous Nix. Every release must be accessible to everyone.

## Pre-Release Checklist

### 1. Code Quality ✅
- [ ] All tests passing: `poetry run pytest`
- [ ] Security scan clean: `poetry run bandit -r src/`
- [ ] Linting passed: `poetry run ruff check`
- [ ] Type checking: `poetry run mypy src/`

### 2. Version Bump 📊
- [ ] Update version in `pyproject.toml`
- [ ] Update version in `src/luminous_nix/__version__.py`
- [ ] Update CHANGELOG.md with release notes

### 3. Build Distributions 📦 (REQUIRED!)

#### A. PyInstaller Binary (Primary)
```bash
# ALWAYS build standalone executable
./scripts/build-standalone.sh

# Verify it works
./dist/luminous-nix help
./dist/luminous-nix search editor
./dist/luminous-nix --version

# Check size (should be <50MB)
du -h dist/luminous-nix
```

#### B. Simple Distribution (Backup)
```bash
# Build lightweight distribution
./scripts/build-standalone-simple.sh

# Creates dist-simple/luminous-nix-standalone.tar.gz
ls -lh dist-simple/*.tar.gz
```

#### C. Source Distribution (PyPI)
```bash
# Build Python packages
poetry build

# Creates dist/*.whl and dist/*.tar.gz
ls -lh dist/
```

### 4. Test Distributions 🧪
- [ ] Test PyInstaller binary on fresh system (use Docker/VM)
- [ ] Test simple distribution install process
- [ ] Verify no Poetry dependencies required
- [ ] Check startup time (<5 seconds)

### 5. Documentation Update 📚
- [ ] Update README with installation instructions
- [ ] Update quickstart guide
- [ ] Add version-specific notes
- [ ] Update compatibility matrix

## Release Process

### 1. Create Git Tag
```bash
# Semantic versioning
git tag -a v0.X.Y -m "Release v0.X.Y: <brief description>"
git push origin v0.X.Y
```

### 2. Create GitHub Release
```bash
# Use GitHub CLI for consistency
gh release create v0.X.Y \
  ./dist/luminous-nix \
  ./dist-simple/luminous-nix-standalone.tar.gz \
  ./dist/*.whl \
  ./dist/*.tar.gz \
  --title "v0.X.Y: <Title>" \
  --notes-file RELEASE_NOTES.md \
  --prerelease  # Remove for stable releases
```

### 3. Distribution Priorities
**ALWAYS include these assets**:
1. `luminous-nix` - Standalone binary (PyInstaller)
2. `luminous-nix-standalone.tar.gz` - Simple distribution
3. `luminous_nix-0.X.Y-py3-none-any.whl` - Python wheel
4. `luminous_nix-0.X.Y.tar.gz` - Source distribution

### 4. Installation Instructions Template
```markdown
## Installation

### Option 1: Standalone Binary (Recommended)
\`\`\`bash
# Download and run - no dependencies needed!
curl -L https://github.com/Luminous-Dynamics/luminous-nix/releases/download/v0.X.Y/luminous-nix -o luminous-nix
chmod +x luminous-nix
./luminous-nix help
\`\`\`

### Option 2: Simple Install
\`\`\`bash
# Download, extract, and install
curl -L https://github.com/Luminous-Dynamics/luminous-nix/releases/download/v0.X.Y/luminous-nix-standalone.tar.gz | tar xz
./install.sh
\`\`\`

### Option 3: Python Package
\`\`\`bash
pip install luminous-nix
\`\`\`

### Option 4: Development
\`\`\`bash
git clone https://github.com/Luminous-Dynamics/luminous-nix
cd luminous-nix
poetry install
poetry run ask-nix help
\`\`\`
```

## Post-Release

### 1. Verify Downloads Work
- [ ] Test download URLs
- [ ] Verify checksums match
- [ ] Check file permissions
- [ ] Test on multiple platforms

### 2. Announcements
- [ ] Update project website
- [ ] Post to NixOS discourse
- [ ] Tweet/social media
- [ ] Email beta testers

### 3. Monitor
- [ ] Check for installation issues
- [ ] Monitor GitHub issues
- [ ] Respond to user feedback
- [ ] Track download statistics

## Automation Goals

### Future: CI/CD Pipeline
```yaml
# .github/workflows/release.yml
name: Build Release
on:
  push:
    tags:
      - 'v*'
jobs:
  build:
    steps:
      - name: Build standalone
        run: ./scripts/build-standalone.sh
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
```

## 🔴 Red Flags - Never Release If:

1. **No standalone binary** - Users need Poetry
2. **Tests failing** - Quality not assured
3. **Security issues** - User safety at risk
4. **>50MB binary** - Too large for distribution
5. **No installation docs** - Users can't get started

## 📝 Release Notes Template

```markdown
# 🚀 Luminous Nix v0.X.Y

## ✨ Highlights
- Feature 1: Brief description
- Feature 2: Brief description
- Feature 3: Brief description

## 📦 Installation
Download the standalone executable - no dependencies required!

\`\`\`bash
curl -L https://github.com/.../luminous-nix -o luminous-nix
chmod +x luminous-nix
./luminous-nix help
\`\`\`

## 🔧 Improvements
- Performance: X% faster
- Security: New validations
- UX: Better error messages

## 🐛 Bug Fixes
- Fixed: Issue description
- Fixed: Issue description

## 📊 Stats
- Binary size: XXX MB
- Test coverage: XX%
- Performance: <X.X sec startup

## 🙏 Thanks
Thanks to all contributors!
```

## ⚡ Quick Release Command

For experienced releaser, here's the one-liner:
```bash
# Complete release process
./scripts/release.sh v0.X.Y "Release title"
```

(This script should be created to automate the entire process)

## 🎯 Success Metrics

A successful release has:
- ✅ <50MB standalone binary
- ✅ Zero dependency installation
- ✅ <5 second startup time
- ✅ 100% test pass rate
- ✅ Clear installation docs
- ✅ Multiple distribution methods
- ✅ User celebration moments

## 📌 Remember Always

**"A tool that requires Poetry to install is a tool for developers. A tool with a standalone binary is a tool for everyone."**

Every release should make Luminous Nix MORE accessible, not less. The standalone binary is not optional - it's the primary distribution method!

---

*Last updated: 2025-01-26*
*Next review: Before v0.4.0 release*