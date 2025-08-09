#!/usr/bin/env bash
# 🌟 Nix for Humanity - Dependency Prefetcher
# Pre-downloads Nix dependencies in the background to avoid timeouts

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🌟 Nix for Humanity - Dependency Prefetcher${NC}"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "flake.nix" ]; then
    echo -e "${RED}❌ Error: flake.nix not found. Please run from the project root.${NC}"
    exit 1
fi

# Create log directory
mkdir -p logs
LOG_FILE="logs/nix-prefetch-$(date +%Y%m%d-%H%M%S).log"

echo -e "${YELLOW}📥 Starting background dependency download...${NC}"
echo "This will pre-download all Nix packages to avoid timeouts."
echo "Logs will be written to: $LOG_FILE"
echo ""

# Function to monitor download progress
monitor_progress() {
    local pid=$1
    local spin='-\|/'
    local i=0
    
    echo -ne "${YELLOW}⏳ Downloading dependencies... ${NC}"
    
    while kill -0 $pid 2>/dev/null; do
        i=$(( (i+1) %4 ))
        printf "\r${YELLOW}⏳ Downloading dependencies... ${spin:$i:1} ${NC}"
        
        # Show last downloaded package
        if [ -f "$LOG_FILE" ]; then
            local last_pkg=$(grep -E "copying path.*from 'https://cache.nixos.org'" "$LOG_FILE" | tail -1 | sed 's/.*\/nix\/store\/[^-]*-//' | cut -d"'" -f1)
            if [ -n "$last_pkg" ]; then
                printf "\r${YELLOW}⏳ Downloading: ${last_pkg:0:40}... ${spin:$i:1} ${NC}"
            fi
        fi
        
        sleep 0.1
    done
    
    # Check if process succeeded
    wait $pid
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo -e "\r${GREEN}✅ Dependencies downloaded successfully!${NC}                                           "
    else
        echo -e "\r${RED}❌ Download failed! Check $LOG_FILE for details.${NC}                              "
        return $exit_code
    fi
}

# Method 1: Use nix develop --dry-run to fetch dependencies
echo -e "${BLUE}Method 1: Using nix develop to fetch dependencies${NC}"
echo "This will download all packages defined in flake.nix"
echo ""

# Start the download in background
nix develop --print-build-logs --verbose --no-update-lock-file --command echo "Dependencies ready" > "$LOG_FILE" 2>&1 &
PID=$!

# Monitor progress
monitor_progress $PID

# Method 2: Build specific derivations
echo ""
echo -e "${BLUE}Method 2: Pre-building voice dependencies${NC}"

# List of heavy dependencies to pre-fetch
VOICE_DEPS=(
    "python311Packages.openai-whisper"
    "python311Packages.sounddevice"
    "python311Packages.numpy"
    "python311Packages.torch"
    "python311Packages.torchaudio"
    "piper-tts"
    "ffmpeg"
    "sox"
    "portaudio"
    "espeak-ng"
)

echo "Pre-fetching voice-specific dependencies..."
for dep in "${VOICE_DEPS[@]}"; do
    echo -ne "${YELLOW}📦 Fetching $dep...${NC}"
    if nix-build '<nixpkgs>' -A "$dep" --no-out-link >> "$LOG_FILE" 2>&1; then
        echo -e "\r${GREEN}✅ $dep${NC}                                    "
    else
        echo -e "\r${YELLOW}⚠️  $dep (might not be available)${NC}        "
    fi
done

# Method 3: Create a lightweight marker
echo ""
echo -e "${BLUE}Creating dependency status file...${NC}"
cat > .nix-deps-status << EOF
# Nix Dependencies Status
Last prefetch: $(date)
Log file: $LOG_FILE

To check if dependencies are ready:
  nix develop --command echo "Ready"

To use minimal environment:
  nix-shell shell-voice-minimal.nix

To use mock mode (no deps needed):
  NIX_VOICE_MOCK=true ./bin/nix-voice
EOF

echo -e "${GREEN}✅ Status saved to .nix-deps-status${NC}"

# Show summary
echo ""
echo -e "${GREEN}🎉 Prefetch complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Regular environment: nix develop"
echo "2. Minimal voice env:  nix-shell shell-voice-minimal.nix"
echo "3. Mock testing:       NIX_VOICE_MOCK=true ./bin/nix-voice"
echo ""
echo "💡 Tip: Run this script in a terminal outside Claude Code to avoid timeouts!"

# Show estimated cache size
if command -v du >/dev/null 2>&1; then
    CACHE_SIZE=$(du -sh /nix/store 2>/dev/null | cut -f1 || echo "unknown")
    echo ""
    echo -e "${BLUE}📊 Nix store size: $CACHE_SIZE${NC}"
fi