#!/usr/bin/env python3
"""
Demo: Error Intelligence System
Shows how we provide helpful error analysis and solutions
"""

import sys
from pathlib import Path

# Add the backend to the path
sys.path.insert(0, str(Path(__file__).parent))

from luminous_nix.core.error_intelligence import ErrorIntelligence

def demo_error_intelligence():
    """Demonstrate error analysis capabilities"""
    
    print("🧠 Nix for Humanity - Error Intelligence Demo")
    print("=" * 60)
    print()
    
    analyzer = ErrorIntelligence()
    
    # Example errors to analyze
    test_errors = [
        # Hash mismatch
        (
            "Hash Mismatch Error",
            """
error: hash mismatch in fixed-output derivation '/nix/store/abc123-source.tar.gz':
  wanted: sha256-1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
  got:    sha256-fedcba0987654321fedcba0987654321fedcba0987654321fedcba0987654321
            """
        ),
        
        # Missing package
        (
            "Missing Package Error", 
            """
error: attribute 'vscode-insiders' missing, at /etc/nixos/configuration.nix:42:5
            """
        ),
        
        # Disk space
        (
            "Disk Space Error",
            """
error: writing to file: No space left on device
error: build of '/nix/store/xyz789-firefox-102.0.drv' failed
            """
        ),
        
        # Permission denied
        (
            "Permission Error",
            """
error: opening file '/etc/nixos/configuration.nix': Permission denied
            """
        ),
        
        # Infinite recursion
        (
            "Recursion Error",
            """
error: infinite recursion encountered, at /etc/nixos/hardware-configuration.nix:10:5
            """
        )
    ]
    
    # Analyze each error
    for title, error_text in test_errors:
        print(f"### {title}")
        print("-" * 50)
        print("Original error:")
        print(error_text.strip())
        print()
        
        # Analyze
        analysis = analyzer.analyze_error(error_text)
        
        # Display analysis
        print("🔍 Analysis:")
        print(analyzer.format_analysis(analysis))
        
        # Show prevention tips
        prevention_tips = analyzer.suggest_prevention(analysis.error_type)
        if prevention_tips:
            print("💡 **Prevention tips**:")
            for tip in prevention_tips:
                print(f"  • {tip}")
        
        print("\n" + "=" * 60 + "\n")
    
    # Interactive mode
    print("🎯 Try your own error! (or type 'quit' to exit)")
    print("-" * 60)
    
    while True:
        print("\nPaste an error message (press Enter twice when done):")
        lines = []
        while True:
            try:
                line = input()
                if line.strip().lower() == 'quit':
                    print("\n👋 Thanks for using Error Intelligence!")
                    return
                if not line and lines and not lines[-1]:
                    break
                lines.append(line)
            except EOFError:
                break
        
        if not lines or all(not line.strip() for line in lines):
            continue
        
        error_text = '\n'.join(lines)
        
        print("\n🔍 Analyzing your error...")
        print("-" * 60)
        
        analysis = analyzer.analyze_error(error_text)
        print(analyzer.format_analysis(analysis))
        
        prevention_tips = analyzer.suggest_prevention(analysis.error_type)
        if prevention_tips:
            print("\n💡 **Prevention tips**:")
            for tip in prevention_tips:
                print(f"  • {tip}")

if __name__ == "__main__":
    demo_error_intelligence()