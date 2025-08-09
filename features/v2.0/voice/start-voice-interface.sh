#!/usr/bin/env bash
# Start the Grandma Rose Voice Interface

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎤 Nix for Humanity Voice Interface${NC}"
echo "===================================="
echo

# Check if we're in nix-shell
if [ -z "$IN_NIX_SHELL" ]; then
    echo -e "${YELLOW}⚠️  Not in nix-shell. Starting nix develop...${NC}"
    exec nix develop -c "$0" "$@"
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python
if ! command_exists python3; then
    echo -e "${RED}❌ Python not found. Please ensure you're in the nix develop shell.${NC}"
    exit 1
fi

# Check for required Python packages
echo -e "${BLUE}Checking Python dependencies...${NC}"
python3 -c "import pyaudio" 2>/dev/null || {
    echo -e "${YELLOW}Installing Python audio packages...${NC}"
    pip install pyaudio numpy wave websockets
}

# Create necessary directories
mkdir -p backend/python/logs
mkdir -p frontend/voice-ui/assets

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down...${NC}"
    kill $(jobs -p) 2>/dev/null || true
    exit 0
}
trap cleanup EXIT INT TERM

# Start based on argument
case "${1:-gui}" in
    "test")
        echo -e "${GREEN}Running voice interface tests...${NC}"
        cd backend/python
        python3 test_voice_flow.py
        ;;
        
    "demo")
        echo -e "${GREEN}Starting simple demo (no audio hardware needed)...${NC}"
        cd backend/python
        python3 voice_demo_simple.py
        ;;
        
    "server")
        echo -e "${GREEN}Starting WebSocket server only...${NC}"
        cd backend/python
        python3 voice_websocket_server.py
        ;;
        
    "gui"|"")
        echo -e "${GREEN}Starting full voice interface...${NC}"
        
        # Start WebSocket server in background
        echo -e "${BLUE}Starting WebSocket server...${NC}"
        cd backend/python
        python3 voice_websocket_server.py &
        SERVER_PID=$!
        
        # Wait for server to start
        sleep 2
        
        # Check if server is running
        if ! kill -0 $SERVER_PID 2>/dev/null; then
            echo -e "${RED}❌ WebSocket server failed to start${NC}"
            exit 1
        fi
        
        echo -e "${GREEN}✅ WebSocket server running on ws://localhost:8765${NC}"
        
        # Open the web interface
        echo -e "${BLUE}Opening web interface...${NC}"
        cd ../../frontend/voice-ui
        
        # Try to open in browser
        if command_exists xdg-open; then
            xdg-open "file://$(pwd)/index.html" 2>/dev/null || true
        elif command_exists open; then
            open "file://$(pwd)/index.html" 2>/dev/null || true
        fi
        
        echo
        echo -e "${GREEN}🎉 Voice interface is ready!${NC}"
        echo
        echo "Web Interface: file://$(pwd)/index.html"
        echo "WebSocket Server: ws://localhost:8765"
        echo
        echo "Press Ctrl+C to stop"
        
        # Keep running
        wait $SERVER_PID
        ;;
        
    "help")
        echo "Usage: $0 [command]"
        echo
        echo "Commands:"
        echo "  gui    - Start full voice interface with web UI (default)"
        echo "  demo   - Run simple text-based demo"
        echo "  test   - Run component tests"
        echo "  server - Start WebSocket server only"
        echo "  help   - Show this help"
        ;;
        
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo "Use '$0 help' for usage"
        exit 1
        ;;
esac