#!/usr/bin/env bash
# START HERE - The single entry point for the improvement journey
# This script guides you through the entire transformation process

set -euo pipefail

# Colors for better visibility
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BOLD='\033[1m'

clear

echo -e "${BLUE}${BOLD}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║        🚀 NIX FOR HUMANITY TRANSFORMATION SUITE 🚀           ║"
echo "║                                                              ║"
echo "║          From Vision to Reality in 6 Weeks                  ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${YELLOW}Welcome to the Nix for Humanity improvement journey!${NC}"
echo ""
echo "This guided process will transform the project from its current"
echo "state (6.5/10) to production excellence (10/10) in 6 weeks."
echo ""

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

check_command() {
    if command -v $1 >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} $1 found"
        return 0
    else
        echo -e "  ${RED}✗${NC} $1 not found"
        return 1
    fi
}

PREREQS_MET=true
check_command git || PREREQS_MET=false
check_command python3 || PREREQS_MET=false
check_command nix || PREREQS_MET=false

if [ "$PREREQS_MET" = false ]; then
    echo -e "\n${RED}Missing prerequisites. Please install required tools first.${NC}"
    exit 1
fi

echo -e "\n${GREEN}All prerequisites met!${NC}"

# Show current state
echo -e "\n${BLUE}Current Project State:${NC}"
if [ -f "metrics/progress.json" ]; then
    python3 -c "
import json
try:
    with open('metrics/progress.json', 'r') as f:
        data = json.load(f)
        if data:
            latest = data[-1]
            print(f'  Overall Score: {latest[\"overall_score\"]:.1f}/10')
except:
    print('  No metrics found - will establish baseline')
"
else
    echo "  No metrics found - will establish baseline"
fi

# Check if already started
IMPROVEMENT_STARTED=false
CURRENT_WEEK=0
START_DATE=$(date +%Y-%m-%d)

if [ -f ".improvement-progress" ]; then
    IMPROVEMENT_STARTED=true
    source .improvement-progress
    echo -e "\n${YELLOW}Improvement already in progress!${NC}"
    echo "  Started: $START_DATE"
    echo "  Current Week: $CURRENT_WEEK"
fi

# Main menu
echo -e "\n${BOLD}What would you like to do?${NC}"
echo ""
echo "1) 🚀 Start/Continue Week $((CURRENT_WEEK + 1)) Tasks"
echo "2) 📊 View Current Progress"
echo "3) 🔍 Run Functionality Check"
echo "4) 📋 View Full Checklist"
echo "5) 🧹 Emergency Cleanup (if things are broken)"
echo "6) 🚨 Emergency Rollback"
echo "7) 📚 Read Improvement Plan"
echo "8) ❌ Exit"
echo ""

read -p "Select option (1-8): " choice

case $choice in
    1)
        # Start improvement tasks
        if [ "$IMPROVEMENT_STARTED" = false ]; then
            echo -e "\n${GREEN}Starting improvement journey!${NC}"
            echo "START_DATE=$(date +%Y-%m-%d)" > .improvement-progress
            echo "CURRENT_WEEK=0" >> .improvement-progress
            
            # Create initial backup
            echo -e "\n${YELLOW}Creating initial backup...${NC}"
            git tag -a "pre-improvement-$(date +%Y%m%d)" -m "Backup before improvement sprint" || true
            
            # Generate baseline metrics
            echo -e "\n${BLUE}Generating baseline metrics...${NC}"
            python scripts/progress-dashboard.py
        fi
        
        # Determine current week and run appropriate scripts
        source .improvement-progress
        WEEK=$((CURRENT_WEEK + 1))
        
        echo -e "\n${GREEN}${BOLD}WEEK $WEEK TASKS${NC}"
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        
        case $WEEK in
            1|2)
                echo "Focus: Foundation Cleanup"
                echo ""
                echo "1) Reorganize project structure"
                echo "2) Consolidate backends"
                echo "3) Fix dependencies"
                echo "4) Create real tests"
                echo ""
                read -p "Run all Week 1-2 scripts? (y/n): " run_week1
                
                if [ "$run_week1" = "y" ]; then
                    echo -e "\n${BLUE}Step 1/4: Reorganizing structure...${NC}"
                    ./scripts/reorganize-project.sh
                    
                    echo -e "\n${BLUE}Step 2/4: Updating imports...${NC}"
                    ./scripts/update-imports.sh
                    
                    echo -e "\n${BLUE}Step 3/4: Cleaning dependencies...${NC}"
                    ./scripts/dependency-cleanup.sh
                    
                    echo -e "\n${BLUE}Step 4/4: Setting up tests...${NC}"
                    ./scripts/test-infrastructure.sh
                    
                    echo "CURRENT_WEEK=2" > .improvement-progress
                    echo "START_DATE=$START_DATE" >> .improvement-progress
                fi
                ;;
                
            3|4)
                echo "Focus: Core Features & Reliability"
                echo ""
                echo "1) Apply reliability fixes"
                echo "2) Complete native API"
                echo "3) Connect interfaces"
                echo "4) Validate performance"
                echo ""
                read -p "Run all Week 3-4 scripts? (y/n): " run_week3
                
                if [ "$run_week3" = "y" ]; then
                    echo -e "\n${BLUE}Applying reliability improvements...${NC}"
                    ./scripts/quick-fix-reliability.sh
                    
                    echo -e "\n${BLUE}Validating performance...${NC}"
                    python scripts/validate-performance.py
                    
                    echo -e "\n${BLUE}Enforcing feature freeze...${NC}"
                    python scripts/feature-freeze-manager.py
                    
                    echo "CURRENT_WEEK=4" > .improvement-progress
                    echo "START_DATE=$START_DATE" >> .improvement-progress
                fi
                ;;
                
            5|6)
                echo "Focus: Polish & Release Preparation"
                echo ""
                echo "1) Update documentation"
                echo "2) Final testing"
                echo "3) Performance validation"
                echo "4) Release checklist"
                echo ""
                read -p "Run all Week 5-6 scripts? (y/n): " run_week5
                
                if [ "$run_week5" = "y" ]; then
                    echo -e "\n${BLUE}Creating honest documentation...${NC}"
                    ./scripts/create-honest-readme.sh
                    
                    echo -e "\n${BLUE}Running release checklist...${NC}"
                    ./scripts/release-checklist.sh
                    
                    echo -e "\n${BLUE}Setting up CI...${NC}"
                    ./scripts/continuous-integration-setup.sh
                    
                    echo "CURRENT_WEEK=6" > .improvement-progress
                    echo "START_DATE=$START_DATE" >> .improvement-progress
                fi
                ;;
                
            *)
                echo -e "${GREEN}Congratulations! The 6-week sprint is complete!${NC}"
                echo ""
                echo "Next steps:"
                echo "1) Review final metrics"
                echo "2) Tag release"
                echo "3) Deploy to users"
                ;;
        esac
        ;;
        
    2)
        # View progress
        echo -e "\n${BLUE}Generating progress report...${NC}"
        python scripts/progress-dashboard.py
        
        if [ -f "metrics/dashboard.html" ]; then
            echo -e "\n${GREEN}Progress dashboard generated!${NC}"
            echo "View in browser: file://$(pwd)/metrics/dashboard.html"
            
            # Try to open in browser
            if command -v xdg-open >/dev/null 2>&1; then
                xdg-open "metrics/dashboard.html" 2>/dev/null || true
            elif command -v open >/dev/null 2>&1; then
                open "metrics/dashboard.html" 2>/dev/null || true
            fi
        fi
        ;;
        
    3)
        # Functionality check
        echo -e "\n${BLUE}Running functionality check...${NC}"
        if [ -f "scripts/functionality-check.sh" ]; then
            ./scripts/functionality-check.sh
        else
            echo -e "${RED}Functionality check script not found!${NC}"
        fi
        ;;
        
    4)
        # View checklist
        echo -e "\n${BLUE}Opening checklist...${NC}"
        if [ -f "FINAL_EXECUTION_CHECKLIST.md" ]; then
            less FINAL_EXECUTION_CHECKLIST.md
        else
            echo -e "${RED}Checklist not found!${NC}"
        fi
        ;;
        
    5)
        # Emergency cleanup
        echo -e "\n${YELLOW}⚠️  Emergency Cleanup Mode${NC}"
        echo "This will try to fix a broken project state."
        read -p "Continue? (y/n): " cleanup
        
        if [ "$cleanup" = "y" ]; then
            # Make scripts executable
            chmod +x scripts/*.sh scripts/*.py 2>/dev/null || true
            
            # Try to restore basic functionality
            if [ ! -d "src" ] && [ -d "nix_humanity" ]; then
                echo "Fixing source directory..."
                mkdir -p src
                mv nix_humanity src/ 2>/dev/null || true
            fi
            
            echo -e "${GREEN}Basic cleanup complete!${NC}"
        fi
        ;;
        
    6)
        # Emergency rollback
        echo -e "\n${RED}Emergency Rollback${NC}"
        ./scripts/emergency-rollback.sh
        ;;
        
    7)
        # Read plan
        echo -e "\n${BLUE}Opening improvement plan...${NC}"
        less IMPROVEMENT_ACTION_PLAN.md
        ;;
        
    8)
        echo -e "\n${GREEN}Good luck with your improvement journey!${NC}"
        exit 0
        ;;
        
    *)
        echo -e "\n${RED}Invalid option${NC}"
        exit 1
        ;;
esac

echo -e "\n${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Task complete! Run $0 again to continue.${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"