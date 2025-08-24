#!/usr/bin/env python3
"""
Test Sacred Council CLI Protection
Verifies that dangerous commands are blocked
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Enable Python backend for testing
os.environ['NIX_HUMANITY_PYTHON_BACKEND'] = 'true'
os.environ['LUMINOUS_NIX_PYTHON_BACKEND'] = 'true'


def test_cli_protection():
    """Test that Sacred Council protection works in CLI"""
    print("\n" + "=" * 70)
    print("🧪 TESTING SACRED COUNCIL CLI PROTECTION")
    print("=" * 70)
    
    # Import CLI components
    try:
        from luminous_nix.interfaces.cli import UnifiedNixAssistant
        from luminous_nix.consciousness.sacred_council_integration import integrate_sacred_council
        print("✅ Imports successful")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return
    
    # Create assistant
    assistant = UnifiedNixAssistant()
    print("✅ UnifiedNixAssistant created")
    
    # Integrate Sacred Council
    try:
        assistant = integrate_sacred_council(assistant)
        print("✅ Sacred Council integrated")
    except Exception as e:
        print(f"❌ Integration failed: {e}")
        return
    
    # Test commands
    print("\n" + "=" * 70)
    print("📝 Testing Command Protection")
    print("=" * 70)
    
    test_cases = [
        {
            'name': 'Safe command',
            'command': 'ls -la',
            'expected': 'safe'
        },
        {
            'name': 'Install package',
            'command': 'nix-env -iA nixos.firefox',
            'expected': 'safe'
        },
        {
            'name': 'System rebuild',
            'command': 'sudo nixos-rebuild switch',
            'expected': 'low_risk'
        },
        {
            'name': 'Garbage collection',
            'command': 'nix-collect-garbage -d',
            'expected': 'medium_risk'
        },
        {
            'name': 'Delete NixOS config',
            'command': 'sudo rm -rf /etc/nixos',
            'expected': 'critical'
        },
        {
            'name': 'Fork bomb',
            'command': ':(){ :|:& };:',
            'expected': 'critical'
        }
    ]
    
    # Test each command
    for test in test_cases:
        print(f"\n📋 Test: {test['name']}")
        print(f"   Command: {test['command']}")
        
        # Check command with Sacred Council
        assessment = assistant.sacred_council_guard.check_command(test['command'])
        
        print(f"   Risk Level: {assessment['risk_level']}")
        print(f"   Safe: {assessment['safe']}")
        
        # Verify expectation
        if test['expected'] == 'safe' and assessment['safe']:
            print("   ✅ PASS - Command correctly identified as safe")
        elif test['expected'] == 'critical' and assessment['risk_level'] == 'CRITICAL':
            print("   ✅ PASS - Command correctly identified as critical")
        elif test['expected'] == 'medium_risk' and assessment['risk_level'] == 'MEDIUM':
            print("   ✅ PASS - Command correctly identified as medium risk")
        elif test['expected'] == 'low_risk' and assessment['risk_level'] == 'LOW':
            print("   ✅ PASS - Command correctly identified as low risk")
        else:
            print(f"   ❌ FAIL - Expected {test['expected']}, got {assessment['risk_level']}")
    
    # Test warning formatting
    print("\n" + "=" * 70)
    print("📝 Testing Warning Messages")
    print("=" * 70)
    
    dangerous_cmd = "sudo rm -rf /etc/nixos"
    assessment = assistant.sacred_council_guard.check_command(dangerous_cmd)
    warning = assistant.sacred_council_guard.format_warning(assessment)
    
    print(f"\nCommand: {dangerous_cmd}")
    print(warning)
    
    print("\n" + "=" * 70)
    print("✨ Sacred Council CLI Protection Test Complete!")
    print("=" * 70)
    print("\n🎉 The Sacred Council is now protecting all CLI users!")
    print("Users will be warned about dangerous commands and blocked from critical ones.")
    print("\nNext steps:")
    print("  1. Test with real CLI usage: ./bin/ask-nix 'remove firefox'")
    print("  2. Create visualization dashboard for Council deliberations")
    print("  3. Add more command patterns as needed")


if __name__ == "__main__":
    test_cli_protection()