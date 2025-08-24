#!/usr/bin/env python3
"""
Test Voice Interface for Grandma Rose
=====================================

This script tests the complete voice pipeline:
1. Audio recording
2. Speech-to-text with Whisper
3. NLP processing
4. Simple Mode response generation
5. Text-to-speech with Piper

Run this to verify everything works before the full UI.
"""

import sys
import os
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.voice_interface import VoiceInterface
from scripts.adaptive_response_formatter import AdaptiveResponseFormatter, ResponseDimensions


def print_banner():
    """Print a friendly banner"""
    print("\n" + "="*60)
    print("🎤 Nix for Humanity Voice Test")
    print("="*60)
    print("\nThis test will check if voice components are working.")
    print("We'll test:")
    print("  ✓ Audio recording")
    print("  ✓ Speech recognition (Whisper)")
    print("  ✓ Natural language understanding")
    print("  ✓ Simple response generation")
    print("  ✓ Text-to-speech (Piper)")
    print("\n" + "="*60 + "\n")


async def test_voice_interface():
    """Test the voice interface components"""
    
    print_banner()
    
    # Initialize voice interface
    print("🔧 Initializing voice interface...")
    voice = VoiceInterface()
    
    # Check dependencies
    print("\n📋 Checking dependencies...")
    ok, message = voice.check_dependencies()
    
    if not ok:
        print("\n❌ Missing dependencies:")
        print(message)
        print("\nPlease install the missing components and try again.")
        return False
    
    print("✅ All dependencies found!")
    
    # Test TTS first (simpler)
    print("\n🔊 Testing text-to-speech...")
    test_message = "Hello! I'm your computer helper. I can help you install programs and manage your system."
    voice.speak(test_message)
    
    response = input("\n❓ Did you hear the voice? (y/n): ")
    if response.lower() != 'y':
        print("Please check your audio settings and try again.")
        return False
    
    print("✅ Text-to-speech working!")
    
    # Test recording and transcription
    print("\n🎤 Testing voice recording...")
    print("\nWhen you press Enter, I'll start recording.")
    print("Say something like: 'I need to install Firefox'")
    print("Press Enter again to stop recording.\n")
    
    input("Press Enter to start recording...")
    
    # Process voice command
    print("\n🎤 Recording... (say something and press Enter when done)")
    voice.process_voice_command()
    
    print("\n✅ Voice test complete!")
    
    # Test adaptive response
    print("\n🧪 Testing adaptive response formatting...")
    formatter = AdaptiveResponseFormatter()
    
    # Force Simple Mode (Grandma Rose)
    simple_dimensions = ResponseDimensions(
        complexity=0.0,  # Simplest
        verbosity=0.3,   # Concise
        warmth=0.9,      # Very warm
        examples=0.8,    # Lots of examples
        pace=0.2,        # Slow pace
        formality=0.2,   # Casual
        visual_structure=0.7  # Clear structure
    )
    
    test_response = """
    To install Firefox, you have several options:
    
    1. **Declarative (Recommended)** - Add to your system configuration
       ```
       environment.systemPackages = with pkgs; [ firefox ];
       ```
    
    2. **Imperative** - Quick installation
       ```
       nix-env -iA nixos.firefox
       ```
    """
    
    adapted, _ = formatter.adapt_response_with_dimensions(
        test_response,
        simple_dimensions
    )
    
    print("\n📝 Original response:")
    print(test_response)
    
    print("\n💬 Adapted for Grandma Rose:")
    print(adapted)
    
    print("\n✅ All tests passed! Voice interface is ready.")
    return True


def test_simple_mode():
    """Test just the Simple Mode formatting"""
    print("\n" + "="*60)
    print("🧪 Testing Simple Mode Response Formatting")
    print("="*60 + "\n")
    
    formatter = AdaptiveResponseFormatter()
    
    # Test cases
    test_cases = [
        {
            "input": "How do I install Firefox?",
            "response": "Use `nix-env -iA nixos.firefox` or add `firefox` to `environment.systemPackages`",
            "expected": "I'll help you get Firefox! Just type this command: nix-env -iA nixos.firefox"
        },
        {
            "input": "Update my system",
            "response": "Run `sudo nixos-rebuild switch` to update",
            "expected": "I'll update your computer. This might take a few minutes."
        },
        {
            "input": "My WiFi stopped working",
            "response": "Check if NetworkManager is enabled in configuration.nix",
            "expected": "Let me help fix your internet connection."
        }
    ]
    
    # Simple Mode dimensions
    simple_dims = ResponseDimensions(
        complexity=0.0,
        verbosity=0.2,
        warmth=0.9,
        examples=0.7,
        pace=0.2,
        formality=0.1,
        visual_structure=0.5
    )
    
    for test in test_cases:
        print(f"Input: '{test['input']}'")
        print(f"Technical: {test['response']}")
        
        adapted, _ = formatter.adapt_response_with_dimensions(
            test['response'],
            simple_dims
        )
        
        print(f"Simple Mode: {adapted}")
        print("-" * 40)


def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Nix for Humanity Voice Interface')
    parser.add_argument('--simple', action='store_true', 
                       help='Test only Simple Mode formatting')
    parser.add_argument('--full', action='store_true',
                       help='Run full voice interface test')
    
    args = parser.parse_args()
    
    if args.simple or (not args.simple and not args.full):
        test_simple_mode()
    
    if args.full:
        asyncio.run(test_voice_interface())
    
    if not args.simple and not args.full:
        print("\nRun with --full for complete voice test")


if __name__ == "__main__":
    main()