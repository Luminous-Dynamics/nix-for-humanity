#!/usr/bin/env bash
# Emergency rollback script for when things go wrong
# Provides quick recovery to last known good state

set -euo pipefail

echo "🚨 EMERGENCY ROLLBACK SYSTEM"
echo "============================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if this is really an emergency
echo -e "${YELLOW}⚠️  This will rollback recent changes!${NC}"
echo ""
read -p "Is this an emergency? (yes/NO): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Rollback cancelled."
    exit 0
fi

# Show recent commits
echo -e "\n${YELLOW}Recent commits:${NC}"
git log --oneline -10

echo ""
read -p "How many commits to rollback? (1-10): " rollback_count

# Validate input
if ! [[ "$rollback_count" =~ ^[0-9]+$ ]] || [ "$rollback_count" -lt 1 ] || [ "$rollback_count" -gt 10 ]; then
    echo -e "${RED}Invalid number of commits${NC}"
    exit 1
fi

# Create backup branch
BACKUP_BRANCH="emergency-backup-$(date +%Y%m%d-%H%M%S)"
echo -e "\n${GREEN}Creating backup branch: $BACKUP_BRANCH${NC}"
git branch "$BACKUP_BRANCH"

# Show what will be rolled back
echo -e "\n${YELLOW}Changes that will be rolled back:${NC}"
git diff HEAD~"$rollback_count"..HEAD --stat

echo ""
read -p "Proceed with rollback? (yes/NO): " final_confirm

if [ "$final_confirm" != "yes" ]; then
    echo "Rollback cancelled."
    exit 0
fi

# Perform rollback
echo -e "\n${YELLOW}Performing rollback...${NC}"

# Method 1: Soft rollback (preserves changes as uncommitted)
rollback_soft() {
    git reset --soft HEAD~"$rollback_count"
    echo -e "${GREEN}✅ Soft rollback complete${NC}"
    echo "Changes are preserved as uncommitted modifications"
}

# Method 2: Hard rollback (discards changes)
rollback_hard() {
    git reset --hard HEAD~"$rollback_count"
    echo -e "${GREEN}✅ Hard rollback complete${NC}"
    echo "All changes have been discarded"
}

# Method 3: Revert commits (creates new commits)
rollback_revert() {
    for i in $(seq 0 $((rollback_count - 1))); do
        git revert --no-edit HEAD~$i
    done
    echo -e "${GREEN}✅ Revert complete${NC}"
    echo "Changes have been reverted with new commits"
}

echo ""
echo "Choose rollback method:"
echo "1) Soft - Keep changes as uncommitted"
echo "2) Hard - Discard all changes"
echo "3) Revert - Create revert commits"
read -p "Method (1/2/3): " method

case $method in
    1)
        rollback_soft
        ;;
    2)
        rollback_hard
        ;;
    3)
        rollback_revert
        ;;
    *)
        echo -e "${RED}Invalid method${NC}"
        exit 1
        ;;
esac

# Post-rollback cleanup
echo -e "\n${YELLOW}Running post-rollback cleanup...${NC}"

# Clear any caches
echo "Clearing caches..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
rm -rf .coverage htmlcov/ 2>/dev/null || true

# Reinstall dependencies
if [ -f "pyproject.toml" ]; then
    echo "Reinstalling dependencies..."
    poetry install --no-interaction || true
fi

# Run basic sanity check
echo -e "\n${YELLOW}Running sanity check...${NC}"

# Check if main files exist
if [ -f "README.md" ] && [ -d "src" -o -d "nix_humanity" ]; then
    echo -e "${GREEN}✅ Basic structure intact${NC}"
else
    echo -e "${RED}❌ Basic structure damaged!${NC}"
fi

# Try to run help command
if [ -x "bin/ask-nix" ]; then
    if ./bin/ask-nix --help >/dev/null 2>&1; then
        echo -e "${GREEN}✅ CLI functional${NC}"
    else
        echo -e "${RED}❌ CLI broken${NC}"
    fi
fi

# Show recovery options
echo -e "\n${GREEN}ROLLBACK COMPLETE${NC}"
echo ""
echo "Recovery options:"
echo "1. Your changes are backed up in branch: $BACKUP_BRANCH"
echo "2. To see what was rolled back: git diff $BACKUP_BRANCH"
echo "3. To restore specific files: git checkout $BACKUP_BRANCH -- path/to/file"
echo "4. To completely restore: git checkout $BACKUP_BRANCH"
echo ""

# Create recovery script
cat > recover-from-backup.sh << EOF
#!/usr/bin/env bash
# Recovery script for backup: $BACKUP_BRANCH

echo "Recovery options for $BACKUP_BRANCH:"
echo ""
echo "1) View changes that were rolled back"
echo "   git diff $BACKUP_BRANCH"
echo ""
echo "2) Restore specific file"
echo "   git checkout $BACKUP_BRANCH -- path/to/file"
echo ""
echo "3) Restore everything"
echo "   git checkout $BACKUP_BRANCH"
echo ""
echo "4) Cherry-pick specific commits"
echo "   git log $BACKUP_BRANCH --oneline"
echo "   git cherry-pick <commit-hash>"
EOF

chmod +x recover-from-backup.sh

echo -e "${GREEN}Recovery script created: ./recover-from-backup.sh${NC}"

# Final status
echo -e "\n${YELLOW}Current status:${NC}"
git status --short

echo -e "\n${GREEN}Emergency rollback complete!${NC}"
echo "Remember: Prevention is better than rollback."
echo "Use feature branches and test thoroughly!"