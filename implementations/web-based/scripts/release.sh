#!/usr/bin/env bash
# NixOS GUI Release Script
# This script automates the release process

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if in git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "Not in a git repository"
    fi
    
    # Check if on main branch
    CURRENT_BRANCH=$(git branch --show-current)
    if [ "$CURRENT_BRANCH" != "main" ]; then
        log_warning "Not on main branch (current: $CURRENT_BRANCH)"
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        log_error "Uncommitted changes detected. Please commit or stash them first."
    fi
    
    # Check if npm is available
    if ! command -v npm &> /dev/null; then
        log_error "npm is not installed"
    fi
    
    # Check if tests pass
    log_info "Running tests..."
    if ! npm test > /dev/null 2>&1; then
        log_error "Tests failed. Please fix them before releasing."
    fi
    
    log_success "All prerequisites met"
}

# Get version from user
get_version() {
    # Get current version
    CURRENT_VERSION=$(node -p "require('./package.json').version")
    log_info "Current version: $CURRENT_VERSION"
    
    # Suggest next versions
    IFS='.' read -ra VERSION_PARTS <<< "$CURRENT_VERSION"
    MAJOR="${VERSION_PARTS[0]}"
    MINOR="${VERSION_PARTS[1]}"
    PATCH="${VERSION_PARTS[2]}"
    
    NEXT_PATCH="$MAJOR.$MINOR.$((PATCH + 1))"
    NEXT_MINOR="$MAJOR.$((MINOR + 1)).0"
    NEXT_MAJOR="$((MAJOR + 1)).0.0"
    
    echo "Suggested versions:"
    echo "  1) Patch: $NEXT_PATCH (bug fixes)"
    echo "  2) Minor: $NEXT_MINOR (new features)"
    echo "  3) Major: $NEXT_MAJOR (breaking changes)"
    echo "  4) Custom version"
    echo "  5) Prerelease (alpha/beta/rc)"
    
    read -p "Select version type (1-5): " VERSION_TYPE
    
    case $VERSION_TYPE in
        1)
            NEW_VERSION=$NEXT_PATCH
            ;;
        2)
            NEW_VERSION=$NEXT_MINOR
            ;;
        3)
            NEW_VERSION=$NEXT_MAJOR
            ;;
        4)
            read -p "Enter custom version (without 'v' prefix): " NEW_VERSION
            ;;
        5)
            read -p "Enter base version: " BASE_VERSION
            echo "Prerelease type:"
            echo "  1) Alpha"
            echo "  2) Beta"
            echo "  3) Release Candidate (rc)"
            read -p "Select (1-3): " PRERELEASE_TYPE
            
            case $PRERELEASE_TYPE in
                1) PRERELEASE="alpha" ;;
                2) PRERELEASE="beta" ;;
                3) PRERELEASE="rc" ;;
                *) log_error "Invalid selection" ;;
            esac
            
            read -p "Prerelease number: " PRERELEASE_NUM
            NEW_VERSION="$BASE_VERSION-$PRERELEASE.$PRERELEASE_NUM"
            ;;
        *)
            log_error "Invalid selection"
            ;;
    esac
    
    # Validate version format
    if ! [[ "$NEW_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-z]+\.[0-9]+)?$ ]]; then
        log_error "Invalid version format: $NEW_VERSION"
    fi
    
    log_info "New version will be: v$NEW_VERSION"
    read -p "Confirm? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    
    VERSION="v$NEW_VERSION"
}

# Update version in files
update_version() {
    log_info "Updating version in files..."
    
    # Update package.json
    npm version "$NEW_VERSION" --no-git-tag-version
    
    # Update other files
    sed -i "s/version = \".*\"/version = \"$NEW_VERSION\"/" nixos-module/package.nix
    sed -i "s/version = \".*\"/version = \"$NEW_VERSION\"/" flake.nix
    
    # Update README badges
    sed -i "s/version-v[0-9.]\+-/version-v$NEW_VERSION-/g" README.md
    
    # Update documentation
    find docs -name "*.md" -exec sed -i "s/nixos-gui\/v[0-9.]\+/nixos-gui\/v$NEW_VERSION/g" {} \;
    
    log_success "Version updated in all files"
}

# Generate changelog
generate_changelog() {
    log_info "Generating changelog..."
    
    # Get the previous tag
    PREV_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
    
    # Create changelog file
    CHANGELOG_FILE="CHANGELOG-$VERSION.md"
    
    cat > "$CHANGELOG_FILE" << EOF
# Changelog for $VERSION

## What's Changed

EOF
    
    if [ -z "$PREV_TAG" ]; then
        log_warning "No previous tag found, including all commits"
        git log --pretty=format:"- %s (%h)" >> "$CHANGELOG_FILE"
    else
        # Group commits by type
        echo "### Features" >> "$CHANGELOG_FILE"
        git log --pretty=format:"- %s (%h)" "$PREV_TAG"..HEAD | grep -E "^- feat" >> "$CHANGELOG_FILE" || echo "- No new features" >> "$CHANGELOG_FILE"
        
        echo -e "\n\n### Bug Fixes" >> "$CHANGELOG_FILE"
        git log --pretty=format:"- %s (%h)" "$PREV_TAG"..HEAD | grep -E "^- fix" >> "$CHANGELOG_FILE" || echo "- No bug fixes" >> "$CHANGELOG_FILE"
        
        echo -e "\n\n### Documentation" >> "$CHANGELOG_FILE"
        git log --pretty=format:"- %s (%h)" "$PREV_TAG"..HEAD | grep -E "^- docs" >> "$CHANGELOG_FILE" || echo "- No documentation changes" >> "$CHANGELOG_FILE"
        
        echo -e "\n\n### Other Changes" >> "$CHANGELOG_FILE"
        git log --pretty=format:"- %s (%h)" "$PREV_TAG"..HEAD | grep -vE "^- (feat|fix|docs)" >> "$CHANGELOG_FILE" || echo "- No other changes" >> "$CHANGELOG_FILE"
    fi
    
    echo -e "\n\n**Full Changelog**: https://github.com/nixos/nixos-gui/compare/${PREV_TAG}...${VERSION}" >> "$CHANGELOG_FILE"
    
    log_success "Changelog generated: $CHANGELOG_FILE"
    
    # Let user edit changelog
    read -p "Edit changelog? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ${EDITOR:-nano} "$CHANGELOG_FILE"
    fi
}

# Build release
build_release() {
    log_info "Building release..."
    
    # Clean previous builds
    rm -rf dist/
    
    # Install dependencies
    npm ci
    
    # Run linter
    log_info "Running linter..."
    npm run lint
    
    # Run tests
    log_info "Running tests..."
    npm test
    
    # Build production
    log_info "Building production assets..."
    npm run build:production
    
    # Build helper
    log_info "Building helper binary..."
    make -C helper clean
    make -C helper
    
    # Create release directory
    RELEASE_DIR="nixos-gui-$VERSION"
    mkdir -p "dist/$RELEASE_DIR"
    
    # Copy files
    cp -r dist/* "dist/$RELEASE_DIR/"
    cp helper/nixos-gui-helper "dist/$RELEASE_DIR/"
    cp README.md LICENSE package.json "dist/$RELEASE_DIR/"
    cp -r docs "dist/$RELEASE_DIR/"
    
    # Create tarball
    cd dist
    tar -czf "$RELEASE_DIR.tar.gz" "$RELEASE_DIR"
    sha256sum "$RELEASE_DIR.tar.gz" > "$RELEASE_DIR.tar.gz.sha256"
    cd ..
    
    log_success "Release built: dist/$RELEASE_DIR.tar.gz"
}

# Commit and tag
commit_and_tag() {
    log_info "Creating git commit and tag..."
    
    # Stage changes
    git add -A
    
    # Commit
    git commit -m "chore: release $VERSION" -m "$(cat "$CHANGELOG_FILE")"
    
    # Create tag
    git tag -a "$VERSION" -m "Release $VERSION" -m "$(cat "$CHANGELOG_FILE")"
    
    log_success "Commit and tag created"
}

# Push to remote
push_to_remote() {
    log_info "Pushing to remote..."
    
    read -p "Push to remote? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push origin main
        git push origin "$VERSION"
        log_success "Pushed to remote"
    else
        log_warning "Skipping push to remote"
        log_info "To push later, run:"
        log_info "  git push origin main"
        log_info "  git push origin $VERSION"
    fi
}

# Main release process
main() {
    log_info "Starting NixOS GUI release process"
    
    check_prerequisites
    get_version
    update_version
    generate_changelog
    build_release
    commit_and_tag
    push_to_remote
    
    log_success "Release process completed!"
    log_info "Next steps:"
    log_info "1. Wait for CI/CD to create GitHub release"
    log_info "2. Review and publish the release on GitHub"
    log_info "3. Update documentation if needed"
    log_info "4. Announce the release"
    
    # Clean up
    rm -f "$CHANGELOG_FILE"
}

# Run main function
main "$@"