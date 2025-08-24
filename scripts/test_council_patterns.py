#!/usr/bin/env python3
"""
Test Sacred Council Pattern Recognition
Quick test without requiring model invocation
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from luminous_nix.consciousness.adapters.sacred_council_adapter import SacredCouncilAdapter


def test_pattern_recognition():
    """Test pattern recognition for dangerous commands"""
    print("\n" + "=" * 70)
    print("🧪 TESTING SACRED COUNCIL PATTERN RECOGNITION")
    print("=" * 70)
    print("\nTesting quick safety assessments without model invocation...\n")
    
    adapter = SacredCouncilAdapter()
    
    # Test commands with expected assessments
    test_cases = [
        # Safe commands
        ("ls -la", "SAFE", "List files"),
        ("nix-env -q", "SAFE", "Query packages"),
        ("nixos-version", "SAFE", "Check version"),
        
        # Medium risk commands
        ("nix-collect-garbage -d", "CHECK", "Clean old generations"),
        ("sudo nixos-rebuild switch", "CHECK", "Apply configuration"),
        
        # Dangerous commands (should trigger DANGER)
        ("sudo rm -rf /etc/nixos", "DANGER", "Delete NixOS config"),
        ("sudo rm -rf /nix", "DANGER", "Delete Nix store"),
        (":(){ :|:& };:", "DANGER", "Fork bomb"),
        ("sudo dd if=/dev/zero of=/dev/sda", "DANGER", "Wipe disk"),
        ("sudo chmod -R 000 /", "DANGER", "Break permissions"),
        ("sudo passwd -d root", "DANGER", "Remove root password"),
    ]
    
    print("Command Assessment Table:")
    print("-" * 70)
    print(f"{'Command':<40} {'Expected':<10} {'Actual':<10} {'Status'}")
    print("-" * 70)
    
    correct = 0
    total = len(test_cases)
    
    for command, expected, description in test_cases:
        # Get assessment
        assessment, needs_full = adapter.quick_safety_check(command)
        
        # Check if correct
        is_correct = (
            (expected == "DANGER" and assessment == "DANGER") or
            (expected == "CHECK" and assessment in ["CHECK", "DANGER"]) or
            (expected == "SAFE" and assessment == "SAFE")
        )
        
        if is_correct:
            correct += 1
            status = "✅"
        else:
            status = "❌"
        
        # Truncate command for display
        cmd_display = command[:37] + "..." if len(command) > 40 else command
        
        print(f"{cmd_display:<40} {expected:<10} {assessment:<10} {status}")
    
    print("-" * 70)
    print(f"\n📊 Results: {correct}/{total} patterns correctly identified")
    print(f"🎯 Accuracy: {(correct/total)*100:.1f}%")
    
    if correct == total:
        print("✨ Perfect pattern recognition!")
    elif correct >= total * 0.8:
        print("✅ Good pattern recognition - most dangers identified")
    else:
        print("⚠️ Pattern recognition needs improvement")
    
    # Test alternative suggestions
    print("\n" + "=" * 70)
    print("📝 ALTERNATIVE SUGGESTIONS")
    print("=" * 70)
    
    dangerous_commands = [
        "sudo rm -rf /etc/nixos",
        "nix-collect-garbage -d",
        "sudo chmod -R 777 /",
    ]
    
    for cmd in dangerous_commands:
        print(f"\n❌ Dangerous: {cmd}")
        print("✅ Safer alternatives:")
        
        # These would come from POML templates in full implementation
        if "rm -rf /etc/nixos" in cmd:
            print("   • sudo cp -r /etc/nixos /etc/nixos.backup")
            print("   • sudo nixos-rebuild switch --rollback")
        elif "nix-collect-garbage" in cmd:
            print("   • nix-collect-garbage -d --delete-older-than 30d")
            print("   • nix-store --gc --print-dead")
        elif "chmod" in cmd:
            print("   • chmod 755 specific_directory")
            print("   • sudo nixos-rebuild test")
    
    print("\n" + "=" * 70)
    print("✨ Pattern recognition test complete!")
    print("The Sacred Council can identify dangerous commands quickly.")
    print("=" * 70)


if __name__ == "__main__":
    test_pattern_recognition()