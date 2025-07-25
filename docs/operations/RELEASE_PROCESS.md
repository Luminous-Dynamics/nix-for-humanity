# Release Process

This document describes the release process for NixOS GUI.

## Overview

NixOS GUI follows [Semantic Versioning](https://semver.org/):
- **Major** (X.0.0): Breaking changes
- **Minor** (0.X.0): New features, backwards compatible
- **Patch** (0.0.X): Bug fixes, backwards compatible

## Release Schedule

- **Patch releases**: As needed for bug fixes
- **Minor releases**: Monthly, on the first Tuesday
- **Major releases**: Annually, or as needed for breaking changes

## Release Process

### 1. Pre-Release Checklist

Run the automated checklist:
```bash
./scripts/pre-release-checklist.sh
```

This verifies:
- ✅ Clean git working directory
- ✅ All tests passing
- ✅ No security vulnerabilities
- ✅ Documentation up to date
- ✅ Version consistency

### 2. Create Release

#### Automated Process (Recommended)

```bash
# For patch release (bug fixes)
./scripts/release.sh patch

# For minor release (new features)
./scripts/release.sh minor

# For major release (breaking changes)
./scripts/release.sh major

# For pre-release
./scripts/release.sh prerelease
```

This script will:
1. Bump version in all package.json files
2. Update version in Nix files
3. Run tests
4. Build the project
5. Generate/update CHANGELOG.md
6. Commit changes
7. Create git tag
8. Push to remote
9. Create draft GitHub release

#### Manual Process

If you need more control:

1. **Update version**:
   ```bash
   npm version patch/minor/major --no-git-tag-version
   # Update backend/package.json and frontend/package.json manually
   ```

2. **Update Nix files**:
   - Edit `default.nix` version
   - Edit `flake.nix` version

3. **Update changelog**:
   ```bash
   git-cliff --tag v0.2.0 --output CHANGELOG.md
   ```

4. **Commit changes**:
   ```bash
   git add .
   git commit -m "chore(release): v0.2.0"
   ```

5. **Create tag**:
   ```bash
   git tag -a v0.2.0 -m "Release v0.2.0"
   ```

6. **Push**:
   ```bash
   git push origin main
   git push origin v0.2.0
   ```

### 3. GitHub Actions

Once you push the tag, GitHub Actions will automatically:

1. **Run CI pipeline**: Lint, test, security scan
2. **Build artifacts**: 
   - Source tarball
   - Docker images (amd64, arm64)
   - Nix build
3. **Generate changelog**: Using git-cliff
4. **Create release**: Draft release with artifacts
5. **Update Nix package**: Create PR to update hash

### 4. Finalize Release

1. **Review draft release** at https://github.com/nixos/nixos-gui/releases
2. **Test artifacts**:
   ```bash
   # Test tarball
   wget https://github.com/nixos/nixos-gui/releases/download/v0.2.0/nixos-gui-0.2.0.tar.gz
   tar -xzf nixos-gui-0.2.0.tar.gz
   cd nixos-gui-0.2.0
   npm install --production
   npm start
   
   # Test Docker image
   docker pull ghcr.io/nixos/nixos-gui:0.2.0
   docker run -p 8080:8080 ghcr.io/nixos/nixos-gui:0.2.0
   ```

3. **Update release notes** if needed
4. **Publish release**

### 5. Post-Release

1. **Announce release**:
   - NixOS Discourse
   - Twitter/Mastodon
   - Reddit r/NixOS
   - Discord/Matrix

2. **Update nixpkgs**:
   ```bash
   # In nixpkgs repo
   cd pkgs/tools/nix/nixos-gui
   # Update version and hash
   nix-prefetch-url --unpack https://github.com/nixos/nixos-gui/archive/v0.2.0.tar.gz
   # Create PR
   ```

3. **Update documentation**:
   - Update version in README.md
   - Update installation instructions
   - Update screenshots if UI changed

4. **Monitor feedback**:
   - GitHub Issues
   - Community channels
   - Error tracking

## Hotfix Process

For critical security fixes:

1. **Create hotfix branch**:
   ```bash
   git checkout -b hotfix/security-fix v0.2.0
   ```

2. **Apply fix and test**

3. **Fast-track release**:
   ```bash
   ./scripts/release.sh patch
   ```

4. **Merge back**:
   ```bash
   git checkout main
   git merge hotfix/security-fix
   ```

## Version Support

- **Latest stable**: Full support
- **Previous minor**: Security fixes only
- **Older versions**: No support

Example (current: 0.3.0):
- 0.3.x - Full support
- 0.2.x - Security fixes only  
- 0.1.x - No support

## Release Notes Template

```markdown
## 🎉 NixOS GUI v0.2.0

### ✨ Highlights
- Brief summary of major changes
- Key features or improvements
- Important fixes

### 🚀 New Features
- Feature 1 (#123)
- Feature 2 (#124)

### 🐛 Bug Fixes
- Fix 1 (#125)
- Fix 2 (#126)

### 🔒 Security
- Security fix 1 (CVE-2024-xxxxx)

### 📚 Documentation
- Documentation improvements

### ⚠️ Breaking Changes
- List any breaking changes

### 🙏 Contributors
Thanks to @user1, @user2 for their contributions!

### 📦 Installation
See [Installation Guide](docs/INSTALLATION.md)

### 📋 Full Changelog
https://github.com/nixos/nixos-gui/compare/v0.1.0...v0.2.0
```

## Troubleshooting

### Release script fails

1. **Check prerequisites**:
   ```bash
   npm --version  # Should be 8+
   git --version  # Should be 2.30+
   gh --version   # GitHub CLI
   ```

2. **Manual cleanup**:
   ```bash
   # Reset version changes
   git checkout -- package*.json
   
   # Delete local tag
   git tag -d v0.2.0
   
   # Delete remote tag (careful!)
   git push origin :refs/tags/v0.2.0
   ```

### GitHub Actions fails

1. Check workflow logs
2. Common issues:
   - NPM registry down
   - Test flakiness
   - Resource limits

### Docker build fails

1. Check Dockerfile syntax
2. Verify base image availability
3. Check multi-arch support

## Security Releases

For security vulnerabilities:

1. **Do NOT** commit fix to public repo first
2. Prepare fix in private
3. Coordinate disclosure:
   - Set disclosure date
   - Prepare advisory
   - Notify major users
4. Release simultaneously:
   - Push fix
   - Publish release
   - Publish advisory

## Automation Improvements

Future improvements planned:
- Automated dependency updates
- Automated security scanning
- Release candidate process
- Beta channel
- Rollback procedures