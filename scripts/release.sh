#!/usr/bin/env bash
set -euo pipefail

# Release script for NixOS GUI
# Usage: ./scripts/release.sh [major|minor|patch|prerelease]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Functions
log() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }

# Check dependencies
check_deps() {
    local deps=("git" "npm" "jq" "gh")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            error "Missing required dependency: $dep"
            exit 1
        fi
    done
}

# Get current version
get_current_version() {
    jq -r '.version' "$PROJECT_ROOT/package.json"
}

# Bump version
bump_version() {
    local bump_type="$1"
    local current_version=$(get_current_version)
    
    log "Current version: $current_version"
    
    # Validate bump type
    case "$bump_type" in
        major|minor|patch|prerelease)
            ;;
        *)
            error "Invalid bump type: $bump_type"
            echo "Usage: $0 [major|minor|patch|prerelease]"
            exit 1
            ;;
    esac
    
    # Update package.json
    npm version "$bump_type" --no-git-tag-version
    
    # Get new version
    local new_version=$(get_current_version)
    log "New version: $new_version"
    
    echo "$new_version"
}

# Update files with new version
update_files() {
    local version="$1"
    
    log "Updating version in files..."
    
    # Update backend package.json
    if [ -f "$PROJECT_ROOT/backend/package.json" ]; then
        jq --arg v "$version" '.version = $v' "$PROJECT_ROOT/backend/package.json" > tmp.json
        mv tmp.json "$PROJECT_ROOT/backend/package.json"
    fi
    
    # Update frontend package.json
    if [ -f "$PROJECT_ROOT/frontend/package.json" ]; then
        jq --arg v "$version" '.version = $v' "$PROJECT_ROOT/frontend/package.json" > tmp.json
        mv tmp.json "$PROJECT_ROOT/frontend/package.json"
    fi
    
    # Update default.nix
    if [ -f "$PROJECT_ROOT/default.nix" ]; then
        sed -i "s/version = \".*\"/version = \"$version\"/" "$PROJECT_ROOT/default.nix"
    fi
    
    # Update flake.nix
    if [ -f "$PROJECT_ROOT/flake.nix" ]; then
        sed -i "s/version = \".*\"/version = \"$version\"/" "$PROJECT_ROOT/flake.nix"
    fi
}

# Run tests
run_tests() {
    log "Running tests..."
    
    npm test || {
        error "Tests failed!"
        exit 1
    }
    
    success "All tests passed"
}

# Build project
build_project() {
    log "Building project..."
    
    npm run build:production || {
        error "Build failed!"
        exit 1
    }
    
    success "Build completed"
}

# Generate changelog
generate_changelog() {
    local version="$1"
    
    log "Generating changelog..."
    
    if command -v git-cliff &> /dev/null; then
        git-cliff --tag "v$version" --output CHANGELOG.md
    else
        warn "git-cliff not found, skipping changelog generation"
    fi
}

# Commit changes
commit_changes() {
    local version="$1"
    
    log "Committing changes..."
    
    git add .
    git commit -m "chore(release): v$version" || {
        warn "No changes to commit"
    }
}

# Create git tag
create_tag() {
    local version="$1"
    
    log "Creating git tag..."
    
    git tag -a "v$version" -m "Release v$version"
    success "Created tag: v$version"
}

# Push to remote
push_changes() {
    local version="$1"
    
    log "Pushing changes to remote..."
    
    git push origin main
    git push origin "v$version"
    
    success "Pushed to remote"
}

# Create GitHub release
create_github_release() {
    local version="$1"
    
    log "Creating GitHub release..."
    
    local changelog=""
    if [ -f "$PROJECT_ROOT/CHANGELOG.md" ]; then
        # Extract changelog for this version
        changelog=$(awk "/## \[$version\]/{flag=1; next} /## \[/{flag=0} flag" CHANGELOG.md)
    fi
    
    gh release create "v$version" \
        --title "NixOS GUI v$version" \
        --notes "$changelog" \
        --draft
    
    success "Created draft release: v$version"
}

# Main release process
main() {
    cd "$PROJECT_ROOT"
    
    # Check dependencies
    check_deps
    
    # Check for uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
        error "Uncommitted changes detected. Please commit or stash them first."
        exit 1
    fi
    
    # Check we're on main branch
    local current_branch=$(git branch --show-current)
    if [ "$current_branch" != "main" ]; then
        error "Not on main branch. Current branch: $current_branch"
        exit 1
    fi
    
    # Pull latest changes
    log "Pulling latest changes..."
    git pull origin main
    
    # Get bump type
    local bump_type="${1:-patch}"
    
    # Bump version
    local new_version=$(bump_version "$bump_type")
    
    # Update files
    update_files "$new_version"
    
    # Run tests
    run_tests
    
    # Build project
    build_project
    
    # Generate changelog
    generate_changelog "$new_version"
    
    # Commit changes
    commit_changes "$new_version"
    
    # Create tag
    create_tag "$new_version"
    
    # Push changes
    push_changes "$new_version"
    
    # Create GitHub release
    if command -v gh &> /dev/null; then
        create_github_release "$new_version"
    else
        warn "GitHub CLI not found, skipping release creation"
    fi
    
    success "Release v$new_version completed!"
    
    echo
    echo "Next steps:"
    echo "1. Review the draft release at: https://github.com/nixos/nixos-gui/releases"
    echo "2. Upload release artifacts"
    echo "3. Publish the release"
    echo "4. Update nixpkgs with new version"
}

# Run main
main "$@"