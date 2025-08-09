#!/usr/bin/env bash
# Simple TUI test using basic Python environment

set -e

echo "🌟 Testing Nix for Humanity TUI (Simple Approach)..."
echo "================================================"

# Add project to Python path
export PYTHONPATH="${PWD}:$PYTHONPATH"

# Try using the pythonMainEnv from flake.nix if in nix shell
if [ -n "$IN_NIX_SHELL" ]; then
    echo "✅ In Nix shell, checking for dependencies..."
    
    # Check if we have rich (it's in pythonMainEnv)
    python3 -c "import rich; print('  ✅ Rich available')" 2>/dev/null || {
        echo "  ⚠️  Rich not in main environment"
    }
fi

# Create a minimal test that works without textual
echo ""
echo "🔮 Testing Consciousness Orb concept (without Textual)..."
python3 -c '
import time
import os
import sys
from datetime import datetime

# Simple terminal colors
class Colors:
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

def clear_screen():
    os.system("clear" if os.name == "posix" else "cls")

def draw_simple_orb(phase=0):
    """Draw a simple ASCII orb"""
    # Simple breathing animation
    size = 3 + int(2 * abs(phase % 2 - 1))
    
    orb_lines = []
    
    # Top
    orb_lines.append(" " * (7 - size) + "╭" + "─" * (size * 2) + "╮")
    
    # Middle
    for i in range(size):
        padding = 7 - size
        if i == size // 2:
            # Center with symbol
            orb_lines.append(" " * padding + "│" + " " * (size - 1) + "◈" + " " * (size - 1) + "│")
        else:
            orb_lines.append(" " * padding + "│" + " " * (size * 2) + "│")
    
    # Bottom
    orb_lines.append(" " * (7 - size) + "╰" + "─" * (size * 2) + "╯")
    
    return orb_lines

print(f"{Colors.CYAN}🌟 Consciousness Orb Demo (Simple){Colors.RESET}")
print("=" * 40)
print()

# Show a few frames of animation
for i in range(6):
    clear_screen()
    print(f"{Colors.CYAN}🌟 Consciousness Orb Demo{Colors.RESET}")
    print("=" * 40)
    print()
    
    # Draw the orb
    orb = draw_simple_orb(i * 0.3)
    for line in orb:
        print(f"    {Colors.PURPLE}{line}{Colors.RESET}")
    
    print()
    print(f"    {Colors.BLUE}State: THINKING{Colors.RESET}")
    print(f"    {Colors.GREEN}Phase: {i}{Colors.RESET}")
    
    time.sleep(0.5)

print()
print(f"{Colors.GREEN}✅ Simple orb animation works!{Colors.RESET}")
print()
print("To see the full TUI with Textual, we need to:")
print("1. Fix the poetry2nix circular dependency issue")
print("2. Or use a virtual environment approach")
'

echo ""
echo "🛠️ Options to proceed:"
echo ""
echo "1. Fix flake.nix dependencies (recommended for NixOS)"
echo "2. Use a temporary virtual environment for testing"
echo "3. Add textual to pythonMainEnv in flake.nix"
echo ""
echo "What would you like to try?"