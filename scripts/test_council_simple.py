#!/usr/bin/env python3
"""
Simple Sacred Council Test - No POML dependencies
Tests the core pattern recognition functionality
"""

import sys
from pathlib import Path

# Add src to path  
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


def test_sacred_council_patterns():
    """Test Sacred Council pattern recognition without full POML"""
    print("\n" + "=" * 70)
    print("🧪 TESTING SACRED COUNCIL - SIMPLE VERSION")
    print("=" * 70)
    print("\nTesting pattern recognition for dangerous NixOS commands...\n")
    
    # Dangerous command patterns
    dangerous_patterns = [
        "rm -rf /",
        "dd if=",
        "mkfs",
        "> /dev/",
        "chmod -R 000",
        ":(){ :|:& };:",  # Fork bomb
        "/etc/nixos",
        "sudo passwd",
        "iptables -F",
    ]
    
    # Test commands with expected risk levels
    test_commands = [
        # Safe
        ("ls -la", "SAFE", "List files"),
        ("nix-env -q", "SAFE", "Query packages"),
        ("nixos-version", "SAFE", "Check version"),
        
        # Medium risk
        ("nix-collect-garbage -d", "CHECK", "Clean generations"),
        ("sudo nixos-rebuild switch", "CHECK", "Apply config"),
        
        # High risk
        ("sudo rm -rf /etc/nixos", "DANGER", "Delete config"),
        ("sudo rm -rf /nix", "DANGER", "Delete store"),
        (":(){ :|:& };:", "DANGER", "Fork bomb"),
        ("sudo dd if=/dev/zero of=/dev/sda", "DANGER", "Wipe disk"),
        ("sudo chmod -R 000 /", "DANGER", "Break perms"),
    ]
    
    print("Command Risk Assessment:")
    print("-" * 70)
    print(f"{'Command':<40} {'Risk':<10} {'Description':<20}")
    print("-" * 70)
    
    for command, expected_risk, description in test_commands:
        # Simple pattern matching
        risk = "SAFE"
        for pattern in dangerous_patterns:
            if pattern in command:
                risk = "DANGER"
                break
        
        # Check for sudo or system modification
        if risk == "SAFE" and any(word in command for word in ["sudo", "nixos-rebuild", "nix-collect"]):
            risk = "CHECK"
        
        # Determine emoji
        if risk == "DANGER":
            emoji = "🚨"
        elif risk == "CHECK":
            emoji = "⚡"
        else:
            emoji = "✅"
        
        # Truncate command for display
        cmd_display = command[:37] + "..." if len(command) > 40 else command
        
        print(f"{emoji} {cmd_display:<38} {risk:<10} {description}")
    
    print("-" * 70)
    
    # Test Sacred Council response
    print("\n" + "=" * 70)
    print("📜 SACRED COUNCIL DELIBERATION (Simulated)")
    print("=" * 70)
    
    dangerous_cmd = "sudo rm -rf /etc/nixos"
    print(f"\n🚨 Critical Command: '{dangerous_cmd}'")
    print("\nCouncil Deliberation:")
    print("-" * 50)
    
    print("\n1️⃣ MIND (Technical Analysis):")
    print("   This would permanently delete all NixOS configuration files.")
    print("   System would become unbootable and unrecoverable.")
    
    print("\n2️⃣ HEART (Human Impact):")
    print("   You would lose all your customizations and settings.")
    print("   Years of configuration work would vanish instantly.")
    
    print("\n3️⃣ CONSCIENCE (Ethical Judgment):")
    print("   UNSAFE - Violates the Vow of Reverence catastrophically.")
    print("   No legitimate use case exists for this command.")
    
    print("\n⚖️ COUNCIL VERDICT: BLOCK")
    print("-" * 50)
    print("\n✅ Safer Alternatives:")
    print("   • sudo cp -r /etc/nixos /etc/nixos.backup")
    print("   • sudo nixos-rebuild switch --rollback")
    print("   • git status /etc/nixos")
    
    print("\n" + "=" * 70)
    print("✨ Sacred Council test complete!")
    print("The Council demonstrates protection without requiring models.")
    print("=" * 70)


if __name__ == "__main__":
    test_sacred_council_patterns()