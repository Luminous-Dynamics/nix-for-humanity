# Release Checklist for v0.1.0-alpha

## Pre-Release Verification

### Code Quality ✅
- [x] Real integration tests pass (3/3)
- [x] No mock implementations in core
- [x] Actual NixOS commands execute
- [x] Safety checks (dry-run mode)

### Documentation ✅
- [x] README reflects reality (README-HONEST.md)
- [x] Known limitations documented
- [x] Installation instructions tested
- [x] Usage examples work

### Distribution ✅
- [x] Minimal tarball created (2.0MB)
- [x] Installation script works
- [x] No Poetry dependency for users
- [x] Python 3.8+ compatible

## Release Assets

### Primary Distribution
- `luminous-nix-v0.1.0-alpha-minimal.tar.gz` (2.0MB)
  - Contains: Python source, install script, README
  - No dependencies bundled (uses pip)
  - Platform: Linux/NixOS

### Documentation
- `README-HONEST.md` - Real capabilities
- `RELEASE-v0.1.0-alpha.md` - Release notes
- `KNOWN_LIMITATIONS_AND_ISSUES.md` - Full transparency

## Testing Checklist

### Basic Commands
- [x] `luminous-nix help` - Shows command list
- [x] `luminous-nix "list installed"` - Lists real packages
- [x] `luminous-nix info` - Shows system info
- [x] `luminous-nix "install vim" --dry-run` - Preview mode works

### Integration
- [x] Works with nix-env systems
- [x] Works with nix profile systems
- [x] Handles both gracefully

## GitHub Release Process

### 1. Create Git Tag
```bash
git add .
git commit -m "Release v0.1.0-alpha: First real working version"
git tag -a v0.1.0-alpha -m "First alpha release with real NixOS integration"
git push origin main
git push origin v0.1.0-alpha
```

### 2. Create GitHub Release
```bash
gh release create v0.1.0-alpha \
  dist-minimal/luminous-nix-v0.1.0-alpha-minimal.tar.gz \
  --title "v0.1.0-alpha: First Real Working Release" \
  --notes-file RELEASE-v0.1.0-alpha.md \
  --prerelease
```

### 3. Release Description Template
```markdown
## 🚀 First Real Working Release!

After discovering the project was 90% mocked, this is the first version with actual NixOS command execution.

### What Works
- ✅ List installed packages (real!)
- ✅ System information
- ✅ Package search (slow but functional)
- ✅ Dry-run installations
- ✅ Help system

### Installation
Download, extract, and run `./install.sh`

### Requirements
- NixOS or Nix package manager
- Python 3.8+

### Known Issues
- Search is slow (5-30 seconds)
- Only dry-run installs for safety
- No voice/GUI features (were never real)

This is alpha software - expect bugs but real functionality!
```

## Post-Release Tasks

### Immediate
- [ ] Announce on NixOS Discourse
- [ ] Update project README on main
- [ ] Create issue templates for bug reports
- [ ] Set up project board for v0.2.0

### Community Engagement
- [ ] Post honest retrospective
- [ ] Ask for testing help
- [ ] Request performance optimization ideas
- [ ] Gather feature priorities

### Development Setup
- [ ] Create CONTRIBUTING.md for new contributors
- [ ] Set up CI for integration tests
- [ ] Document development workflow
- [ ] Create roadmap to v0.2.0

## Success Metrics

### Technical
- Real commands execute: ✅
- No mock responses: ✅
- Integration tests pass: ✅
- Distribution under 5MB: ✅ (2.0MB)

### Honesty
- Capabilities documented: ✅
- Limitations acknowledged: ✅
- No false claims: ✅
- Transparent history: ✅

## Version String

Update in:
- `pyproject.toml`: version = "0.1.0-alpha"
- `src/luminous_nix/__version__.py`: __version__ = "0.1.0-alpha"
- `bin/ask-nix`: version string in help

## Final Verification

Run these commands with the release build:
```bash
# Extract release
tar xzf luminous-nix-v0.1.0-alpha-minimal.tar.gz

# Install
./install.sh

# Test each command
luminous-nix help                    # Should show help
luminous-nix "list installed"        # Should list packages
luminous-nix info                    # Should show system info
luminous-nix "search hello"          # Should search (may be slow)
luminous-nix "install hello" --dry-run  # Should preview

# Verify no errors or mocked responses
```

## Release Philosophy

**"Ship real functionality, not promises."**

This release has:
- 40% functionality that WORKS
- 0% fake features
- 100% honest documentation

## Approval

- [x] Code works on real NixOS system
- [x] Documentation is honest
- [x] Distribution is ready
- [x] Tests pass
- [ ] Tagged in git
- [ ] Released on GitHub

---

**Status: Ready for v0.1.0-alpha release!**

*First real functionality delivered.*