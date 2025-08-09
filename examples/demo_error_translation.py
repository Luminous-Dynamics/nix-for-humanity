#!/usr/bin/env python3
"""
Demonstrate NixOS Error Translation & Resolution feature
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nix_humanity.core.error_translator import ErrorTranslator

def demo_error_translation():
    """Demo error translation feature"""
    print("🔍 Feature 4: NixOS Error Translation & Resolution")
    print("=" * 60)
    print("\nTransforming cryptic NixOS errors into helpful guidance.\n")
    
    translator = ErrorTranslator()
    
    # Common real-world errors
    test_cases = [
        {
            "title": "Missing Package Error",
            "error": "error: attribute 'nodejs_18' missing, at /etc/nixos/configuration.nix:42:15",
            "context": "User trying to install Node.js 18 which was renamed"
        },
        {
            "title": "Package Name Typo",
            "error": "error: attribute 'fierefox' missing",
            "context": "Simple typo in package name"
        },
        {
            "title": "Disk Space Error",
            "error": "error: writing to file: No space left on device",
            "context": "Common when Nix store grows large"
        },
        {
            "title": "Permission Error",
            "error": "error: opening file '/etc/nixos/configuration.nix': Permission denied",
            "context": "Forgot to use sudo"
        },
        {
            "title": "Syntax Error",
            "error": "error: syntax error, unexpected '}', expecting ';' at /etc/nixos/configuration.nix:55:1",
            "context": "Missing semicolon - very common"
        },
        {
            "title": "Build Failure",
            "error": "error: builder for '/nix/store/abc123-custom-package-1.0.drv' failed with exit code 1",
            "context": "Package failed to build"
        },
        {
            "title": "Type Mismatch",
            "error": "error: value is a string while a Boolean was expected",
            "context": "Used \"true\" instead of true"
        },
        {
            "title": "Undefined Variable",
            "error": "error: undefined variable 'vscode' at /home/user/config.nix:10:5",
            "context": "Forgot 'with pkgs;' declaration"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['title']}")
        print("-" * 40)
        print(f"Context: {test_case['context']}")
        print(f"\n❌ Original Error:")
        print(f"   {test_case['error']}")
        
        # Translate
        translated = translator.translate_error(test_case['error'])
        
        print(f"\n✨ Human-Friendly Translation:")
        print(translated.format_for_persona('friendly'))
        
        # Show confidence
        print(f"\n📊 Confidence: {translated.confidence:.0%}")
        
        if i < len(test_cases):
            print("\n" + "=" * 60)

def demo_personas():
    """Show how different personas get different explanations"""
    print("\n\n🎭 Same Error, Different Personas")
    print("=" * 60)
    
    translator = ErrorTranslator()
    error = "error: attribute 'nodejs_18' missing"
    translated = translator.translate_error(error)
    
    personas = ['minimal', 'friendly', 'encouraging', 'technical']
    
    for persona in personas:
        print(f"\n{persona.upper()} Persona:")
        print("-" * 40)
        print(translated.format_for_persona(persona))

def demo_natural_language():
    """Show natural language examples"""
    print("\n\n💬 Natural Language Examples")
    print("=" * 60)
    
    examples = [
        "explain error attribute 'firefox' missing",
        "what does this error mean: No space left on device",
        "help fix syntax error unexpected '}'",
        "error: permission denied",
    ]
    
    print("\nYou can ask for help naturally:")
    for example in examples:
        print(f'  ask-nix "{example}"')
    
    print("\nOr paste errors directly:")
    print('  nixos-rebuild switch 2>&1 | ask-nix error explain')
    print('  ask-nix error analyze /tmp/build.log')

def main():
    print("🌟 Nix for Humanity - Error Translation Feature")
    print("Making NixOS errors helpful instead of scary\n")
    
    demo_error_translation()
    demo_personas()
    demo_natural_language()
    
    print("\n\n🎉 Error Translation Feature Complete!")
    print("\nBenefits:")
    print("✅ Reduces fear and frustration")
    print("✅ Teaches users about NixOS")
    print("✅ Provides actionable solutions")
    print("✅ Builds confidence over time")
    print("\n✨ Every error is now a learning opportunity!")

if __name__ == "__main__":
    main()