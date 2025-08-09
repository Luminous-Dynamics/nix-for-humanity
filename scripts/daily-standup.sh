#!/usr/bin/env bash
# Daily standup script - Quick morning check and task planning
# Run this each morning during the improvement sprint

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'
BOLD='\033[1m'

clear

echo -e "${BLUE}${BOLD}☀️  DAILY STANDUP - NIX FOR HUMANITY${NC}"
echo "======================================"
echo "$(date '+%A, %B %d, %Y - %I:%M %p')"
echo ""

# Load progress tracking
if [ -f ".improvement-progress" ]; then
    source .improvement-progress
    DAYS_ELAPSED=$(( ($(date +%s) - $(date -d "$START_DATE" +%s)) / 86400 ))
    WEEK=$(( (DAYS_ELAPSED / 7) + 1 ))
    DAY_OF_WEEK=$(( DAYS_ELAPSED % 7 + 1 ))
    
    echo -e "${YELLOW}Sprint Status:${NC} Week $WEEK, Day $DAY_OF_WEEK"
    echo -e "${YELLOW}Days Remaining:${NC} $(( 42 - DAYS_ELAPSED )) days"
else
    echo -e "${RED}No improvement tracking found!${NC}"
    echo "Run ./scripts/START_HERE.sh to begin"
    exit 1
fi

echo ""

# Yesterday's progress
echo -e "${BLUE}📅 YESTERDAY'S ACTIVITY${NC}"
echo "----------------------"

# Git activity from yesterday
YESTERDAY=$(date -d "yesterday" '+%Y-%m-%d')
COMMITS_YESTERDAY=$(git log --since="$YESTERDAY 00:00" --until="$YESTERDAY 23:59" --oneline 2>/dev/null | wc -l || echo "0")

if [ "$COMMITS_YESTERDAY" -gt 0 ]; then
    echo -e "${GREEN}✓${NC} $COMMITS_YESTERDAY commits made"
    git log --since="$YESTERDAY 00:00" --until="$YESTERDAY 23:59" --oneline | head -5
else
    echo -e "${YELLOW}⚠${NC} No commits yesterday"
fi

echo ""

# Current state check
echo -e "${BLUE}📊 CURRENT STATE${NC}"
echo "---------------"

# Quick metrics
if [ -f "metrics/progress.json" ]; then
    CURRENT_SCORE=$(python3 -c "
import json
with open('metrics/progress.json', 'r') as f:
    data = json.load(f)
    if data:
        print(f\"{data[-1]['overall_score']:.1f}\")
    else:
        print('N/A')
" 2>/dev/null || echo "N/A")
    echo "Overall Score: $CURRENT_SCORE/10"
else
    echo "Overall Score: Not measured yet"
fi

# Test status
if command -v pytest >/dev/null 2>&1; then
    echo -n "Test Status: "
    if pytest tests/unit -q --tb=no >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Passing${NC}"
    else
        echo -e "${RED}✗ Failing${NC}"
    fi
else
    echo "Test Status: pytest not available"
fi

# Check for blockers
echo ""
echo -e "${BLUE}🚧 BLOCKERS${NC}"
echo "-----------"

BLOCKERS=0

# Check if reorganization needed
if [ $(find . -maxdepth 1 -name "*.py" -type f | wc -l) -gt 5 ]; then
    echo -e "${RED}•${NC} Root directory needs cleanup"
    ((BLOCKERS++))
fi

# Check for duplicate backends
if [ -d "backend" ] && [ -d "nix_humanity" ]; then
    echo -e "${RED}•${NC} Duplicate backends exist"
    ((BLOCKERS++))
fi

# Check for failing tests
if [ -d "tests" ]; then
    if ! python -m pytest tests/unit -q --tb=no >/dev/null 2>&1; then
        echo -e "${RED}•${NC} Unit tests failing"
        ((BLOCKERS++))
    fi
fi

if [ $BLOCKERS -eq 0 ]; then
    echo -e "${GREEN}✓${NC} No blockers!"
fi

echo ""

# Today's priorities
echo -e "${BLUE}🎯 TODAY'S PRIORITIES${NC}"
echo "--------------------"

# Week-specific priorities
case $WEEK in
    1|2)
        echo "Focus: Foundation & Structure"
        echo ""
        if [ ! -d "src/nix_humanity" ]; then
            echo "1. Run ./scripts/reorganize-project.sh"
        elif [ $BLOCKERS -gt 0 ]; then
            echo "1. Fix blockers listed above"
        else
            echo "1. Consolidate backend implementations"
        fi
        echo "2. Create real integration tests"
        echo "3. Fix import paths"
        ;;
        
    3|4)
        echo "Focus: Core Features & Reliability"
        echo ""
        echo "1. Complete native Python-Nix API"
        echo "2. Fix command reliability (95% target)"
        echo "3. Connect TUI to backend"
        ;;
        
    5|6)
        echo "Focus: Polish & Release"
        echo ""
        echo "1. Update all documentation"
        echo "2. Run release checklist"
        echo "3. Final performance validation"
        ;;
        
    *)
        echo "Sprint complete! Focus on maintenance"
        ;;
esac

echo ""

# Quick actions menu
echo -e "${BLUE}⚡ QUICK ACTIONS${NC}"
echo "----------------"
echo "1) Run progress dashboard"
echo "2) Execute today's improvement script"
echo "3) Run tests"
echo "4) Check functionality"
echo "5) Skip to work"
echo ""

read -p "Select action (1-5): " action

case $action in
    1)
        python scripts/progress-dashboard.py
        ;;
    2)
        ./scripts/START_HERE.sh
        ;;
    3)
        if [ -f "./scripts/run-tests.sh" ]; then
            ./scripts/run-tests.sh
        else
            pytest tests/ -v
        fi
        ;;
    4)
        if [ -f "./scripts/functionality-check.sh" ]; then
            ./scripts/functionality-check.sh
        fi
        ;;
    5)
        echo -e "\n${GREEN}Let's make today productive!${NC}"
        ;;
    *)
        echo -e "\n${YELLOW}Invalid choice, starting work...${NC}"
        ;;
esac

# Motivational quote
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

QUOTES=(
    "Quality is not an act, it is a habit. - Aristotle"
    "Perfection is achieved not when there is nothing more to add, but when there is nothing left to take away. - Antoine de Saint-Exupéry"
    "Make it work, make it right, make it fast. - Kent Beck"
    "The best code is no code at all. - Jeff Atwood"
    "Simplicity is the ultimate sophistication. - Leonardo da Vinci"
)

RANDOM_QUOTE=${QUOTES[$RANDOM % ${#QUOTES[@]}]}
echo -e "${GREEN}💭 $RANDOM_QUOTE${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Log standup completion
echo "$(date '+%Y-%m-%d %H:%M'): Daily standup completed" >> .standup-log

echo ""
echo -e "${GREEN}Ready to tackle the day! 🚀${NC}"