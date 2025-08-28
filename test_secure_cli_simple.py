#!/usr/bin/env python3
"""Simple test of secure intent recognition integration."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_secure_intent_basic():
    """Test basic secure intent recognition."""
    print("🔐 Testing Secure Intent Recognition")
    print("-" * 40)
    
    from luminous_nix.core.intent_secure_wrapper import create_production_recognizer
    
    # Create secure recognizer
    recognizer = create_production_recognizer(security_level="high", enable_ai=False)
    
    # Test cases
    test_cases = [
        ("install firefox", "Normal command"),
        ("rm -rf /", "Malicious command"),
        ("asdfghjkl", "Nonsense input"),
    ]
    
    for query, description in test_cases:
        print(f"\nTesting: '{query}' ({description})")
        result = recognizer.recognize(query, user_id="test")
        
        if result['success']:
            intent_type = result['intent']['type']
            confidence = result['intent']['confidence']
            print(f"  ✅ Intent: {intent_type} (confidence: {confidence:.2f})")
            
            if result.get('security'):
                threat = result['security'].get('threat_level', 'unknown')
                print(f"     Security: {threat}")
        else:
            error = result['error']
            print(f"  🚫 Blocked: {error}")
    
    # Get statistics
    stats = recognizer.get_statistics()
    print(f"\n📊 Statistics:")
    print(f"  Total: {stats['total_requests']}")
    print(f"  Success: {stats['successful']}")
    print(f"  Blocked: {stats['blocked']}")

if __name__ == "__main__":
    test_secure_intent_basic()
    print("\n✅ Test complete!")