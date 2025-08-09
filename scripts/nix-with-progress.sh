#!/usr/bin/env bash
# 🌟 Nix for Humanity - Progress Indicator for Nix Operations
# Shows friendly progress for long-running nix commands

set -euo pipefail

# Colors and symbols
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Progress indicators
SPINNER='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
BLOCKS='▏▎▍▌▋▊▉█'

# Usage function
usage() {
    echo "Usage: $0 <nix-command> [args...]"
    echo ""
    echo "Examples:"
    echo "  $0 develop              # Run nix develop with progress"
    echo "  $0 shell                # Run nix-shell with progress"
    echo "  $0 build .              # Run nix build with progress"
    echo ""
    echo "Options:"
    echo "  --simple                # Use simple spinner (for basic terminals)"
    echo "  --quiet                 # Less verbose output"
    echo "  --timeout <seconds>     # Set custom timeout (default: 300)"
    exit 1
}

# Parse arguments
NIX_CMD=""
NIX_ARGS=()
SIMPLE_MODE=false
QUIET_MODE=false
TIMEOUT=300

while [[ $# -gt 0 ]]; do
    case $1 in
        --simple)
            SIMPLE_MODE=true
            shift
            ;;
        --quiet)
            QUIET_MODE=true
            shift
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        develop|shell|build|run|flake|eval)
            NIX_CMD="$1"
            shift
            NIX_ARGS=("$@")
            break
            ;;
        *)
            usage
            ;;
    esac
done

if [ -z "$NIX_CMD" ]; then
    usage
fi

# Create temp files for output
LOG_FILE=$(mktemp /tmp/nix-progress-log.XXXXXX)
STATUS_FILE=$(mktemp /tmp/nix-progress-status.XXXXXX)
trap "rm -f $LOG_FILE $STATUS_FILE" EXIT

# Function to show simple spinner
show_simple_spinner() {
    local pid=$1
    local msg=$2
    local spin='-\|/'
    local i=0
    
    while kill -0 $pid 2>/dev/null; do
        i=$(( (i+1) %4 ))
        printf "\r${YELLOW}${msg} ${spin:$i:1}${NC}"
        sleep 0.1
    done
}

# Function to show advanced progress
show_advanced_progress() {
    local pid=$1
    local start_time=$(date +%s)
    local spinner_idx=0
    local last_line=""
    local download_count=0
    local build_count=0
    
    # Header
    if [ "$QUIET_MODE" = false ]; then
        echo -e "${BLUE}🌟 Nix for Humanity Progress Monitor${NC}"
        echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    fi
    
    while kill -0 $pid 2>/dev/null; do
        # Update spinner
        spinner_idx=$(( (spinner_idx+1) % ${#SPINNER} ))
        local spinner_char="${SPINNER:$spinner_idx:1}"
        
        # Calculate elapsed time
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))
        local elapsed_min=$((elapsed / 60))
        local elapsed_sec=$((elapsed % 60))
        local time_str=$(printf "%02d:%02d" $elapsed_min $elapsed_sec)
        
        # Parse last meaningful line from log
        if [ -f "$LOG_FILE" ]; then
            # Look for download progress
            local new_download=$(grep -c "copying path.*from 'https://cache.nixos.org'" "$LOG_FILE" 2>/dev/null || echo "0")
            if [ "$new_download" -gt "$download_count" ]; then
                download_count=$new_download
                last_line=$(grep "copying path.*from 'https://cache.nixos.org'" "$LOG_FILE" | tail -1 | sed 's/.*\/nix\/store\/[^-]*-//' | cut -d"'" -f1)
                last_line="📥 Downloading: ${last_line:0:40}..."
            fi
            
            # Look for build progress
            local new_build=$(grep -c "building '/nix/store/" "$LOG_FILE" 2>/dev/null || echo "0")
            if [ "$new_build" -gt "$build_count" ]; then
                build_count=$new_build
                last_line=$(grep "building '/nix/store/" "$LOG_FILE" | tail -1 | sed 's/.*\/nix\/store\/[^-]*-//' | cut -d"'" -f1)
                last_line="🔨 Building: ${last_line:0:40}..."
            fi
            
            # Look for evaluation progress
            if grep -q "evaluating" "$LOG_FILE" 2>/dev/null && [ -z "$last_line" ]; then
                last_line="🧮 Evaluating derivation..."
            fi
        fi
        
        # Default message if nothing specific found
        if [ -z "$last_line" ]; then
            last_line="⏳ Initializing nix $NIX_CMD..."
        fi
        
        # Build status line
        local status_line="${spinner_char} ${time_str} | ${last_line}"
        
        # Show download/build counts if available
        if [ "$download_count" -gt 0 ] || [ "$build_count" -gt 0 ]; then
            status_line="$status_line | 📊 D:$download_count B:$build_count"
        fi
        
        # Print status
        printf "\r${YELLOW}%-80s${NC}" "$status_line"
        
        # Check timeout
        if [ "$elapsed" -gt "$TIMEOUT" ]; then
            echo -e "\n${RED}⏰ Timeout after ${TIMEOUT} seconds!${NC}"
            kill $pid 2>/dev/null || true
            return 1
        fi
        
        sleep 0.1
    done
    
    # Get exit status
    wait $pid
    local exit_code=$?
    
    # Final status
    local final_time=$(date +%s)
    local total_elapsed=$((final_time - start_time))
    local total_min=$((total_elapsed / 60))
    local total_sec=$((total_elapsed % 60))
    
    if [ $exit_code -eq 0 ]; then
        printf "\r${GREEN}✅ Success! Completed in %02d:%02d${NC}%-40s\n" $total_min $total_sec ""
    else
        printf "\r${RED}❌ Failed after %02d:%02d${NC}%-40s\n" $total_min $total_sec ""
    fi
    
    return $exit_code
}

# Function to monitor nix progress with progress bar
show_progress_bar() {
    local pid=$1
    local total_steps=100  # Estimate
    local current_step=0
    local bar_width=50
    
    echo -e "${BLUE}🌟 Nix ${NIX_CMD} Progress${NC}"
    
    while kill -0 $pid 2>/dev/null; do
        # Estimate progress based on log content
        if [ -f "$LOG_FILE" ]; then
            local downloads=$(grep -c "copying path" "$LOG_FILE" 2>/dev/null || echo "0")
            local builds=$(grep -c "building" "$LOG_FILE" 2>/dev/null || echo "0")
            current_step=$((downloads + builds * 2))  # Builds count more
        fi
        
        # Calculate bar
        local progress=$((current_step * bar_width / total_steps))
        local remaining=$((bar_width - progress))
        
        # Build bar
        local bar="["
        for ((i=0; i<progress; i++)); do bar+="█"; done
        for ((i=0; i<remaining; i++)); do bar+="░"; done
        bar+="]"
        
        # Show progress
        printf "\r${CYAN}%s %3d%%${NC}" "$bar" $((current_step * 100 / total_steps))
        
        sleep 0.5
    done
    
    wait $pid
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        printf "\r${GREEN}[%*s] 100%%${NC}\n" $bar_width "$(printf '%*s' $bar_width | tr ' ' '█')"
    fi
    
    return $exit_code
}

# Main execution
echo -e "${BLUE}🚀 Starting: nix ${NIX_CMD} ${NIX_ARGS[*]}${NC}"

# Handle special case for Claude Code
if [ -n "${CLAUDE_CODE:-}" ]; then
    echo -e "${YELLOW}⚠️  Detected Claude Code environment${NC}"
    echo -e "${YELLOW}   Long downloads may timeout. Consider:${NC}"
    echo -e "${YELLOW}   1. Run ./scripts/prefetch-dependencies.sh first${NC}"
    echo -e "${YELLOW}   2. Use nix-shell shell-voice-minimal.nix${NC}"
fi

# Start nix command in background
if [ "$NIX_CMD" = "develop" ] || [ "$NIX_CMD" = "shell" ]; then
    # For develop/shell, add a command to confirm it's ready
    nix "$NIX_CMD" "${NIX_ARGS[@]}" --print-build-logs --command echo "Environment ready!" > "$LOG_FILE" 2>&1 &
else
    # For other commands, run normally
    nix "$NIX_CMD" "${NIX_ARGS[@]}" --print-build-logs > "$LOG_FILE" 2>&1 &
fi
NIX_PID=$!

# Show progress based on mode
if [ "$SIMPLE_MODE" = true ]; then
    show_simple_spinner $NIX_PID "Running nix $NIX_CMD..."
else
    show_advanced_progress $NIX_PID
fi

EXIT_CODE=$?

# Show log on error
if [ $EXIT_CODE -ne 0 ] && [ "$QUIET_MODE" = false ]; then
    echo -e "\n${RED}Error details:${NC}"
    tail -20 "$LOG_FILE"
    echo -e "\n${YELLOW}Full log saved to: $LOG_FILE${NC}"
    echo -e "${YELLOW}(File will be deleted on exit, copy if needed)${NC}"
fi

exit $EXIT_CODE