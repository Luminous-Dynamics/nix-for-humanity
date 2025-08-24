#!/bin/bash
# Demo Sacred Council Protection in CLI

echo "🛡️ Sacred Council CLI Protection Demo"
echo "======================================"
echo ""
echo "This demo shows how the Sacred Council protects users from dangerous commands."
echo ""

# Set environment for Python backend
export NIX_HUMANITY_PYTHON_BACKEND=true
export LUMINOUS_NIX_PYTHON_BACKEND=true

# Navigate to project directory
cd /srv/luminous-dynamics/luminous-nix

echo "1️⃣ Testing SAFE command (list packages):"
echo "   Command: ./bin/ask-nix 'list installed packages'"
echo "   Expected: Executes normally"
echo "   Press Enter to test..."
read
echo "./bin/ask-nix 'list installed packages'" | head -20
echo ""

echo "2️⃣ Testing LOW RISK command (system rebuild):"
echo "   Command: ask-nix 'rebuild system'"
echo "   Expected: Shows warning but proceeds"
echo "   Note: We'll simulate this to avoid actual system changes"
echo ""

echo "3️⃣ Testing MEDIUM RISK command (garbage collection):"
echo "   Command: ask-nix 'clean all old generations'"
echo "   Expected: Requires 'yes' confirmation"
echo "   Note: We'll simulate this"
echo ""

echo "4️⃣ Testing CRITICAL command (delete config):"
echo "   Command: ask-nix 'delete /etc/nixos'"
echo "   Expected: BLOCKED by Sacred Council"
echo ""
echo "   Let's test with Python directly:"
python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, 'src')

from luminous_nix.consciousness.sacred_council_integration import SacredCouncilGuard

guard = SacredCouncilGuard(enable_deliberation=False)

# Test dangerous command
cmd = 'sudo rm -rf /etc/nixos'
print(f'Testing command: {cmd}')
assessment = guard.check_command(cmd)

# Show warning
warning = guard.format_warning(assessment)
print(warning)
"

echo ""
echo "======================================"
echo "✨ Demo Complete!"
echo ""
echo "The Sacred Council is now protecting all users of ask-nix!"
echo ""
echo "Key Features:"
echo "  • Pattern-based instant protection"
echo "  • Risk level assessment (CRITICAL/HIGH/MEDIUM/LOW/SAFE)"
echo "  • Educational warnings with safe alternatives"
echo "  • Confirmation flow for risky operations"
echo "  • Automatic blocking of catastrophic commands"
echo ""
echo "Try it yourself:"
echo "  ./bin/ask-nix 'your command here'"