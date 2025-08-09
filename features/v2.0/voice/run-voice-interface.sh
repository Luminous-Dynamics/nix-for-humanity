#!/usr/bin/env bash
# Simple script to run the voice interface

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🎤 Nix for Humanity Voice Interface${NC}"
echo "===================================="
echo

# Check if we're in the right directory
if [ ! -f "flake.nix" ]; then
    echo -e "${YELLOW}⚠️  Please run this from the nix-for-humanity directory${NC}"
    exit 1
fi

# Function to show usage
show_usage() {
    echo "Usage: $0 [command]"
    echo
    echo "Commands:"
    echo "  start     - Start the voice server (default)"
    echo "  test      - Run tests"
    echo "  demo      - Run text demo"
    echo "  frontend  - Open frontend in browser"
    echo "  help      - Show this help"
}

# Default command
CMD="${1:-start}"

case "$CMD" in
    start)
        echo -e "${GREEN}Starting voice server...${NC}"
        cd backend/python
        python3 run_voice_server.py server
        ;;
        
    test)
        echo -e "${GREEN}Running tests...${NC}"
        cd backend/python
        python3 test_complete_voice_pipeline.py
        ;;
        
    demo)
        echo -e "${GREEN}Running demo...${NC}"
        cd backend/python
        python3 run_voice_server.py demo
        ;;
        
    frontend)
        echo -e "${GREEN}Opening frontend...${NC}"
        FRONTEND_PATH="$(pwd)/frontend/voice-ui/index.html"
        
        if command -v xdg-open &> /dev/null; then
            xdg-open "file://$FRONTEND_PATH"
        elif command -v open &> /dev/null; then
            open "file://$FRONTEND_PATH"
        else
            echo "Please open in your browser:"
            echo "file://$FRONTEND_PATH"
        fi
        ;;
        
    help)
        show_usage
        ;;
        
    *)
        echo -e "${YELLOW}Unknown command: $CMD${NC}"
        show_usage
        exit 1
        ;;
esac