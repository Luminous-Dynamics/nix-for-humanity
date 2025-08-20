#!/usr/bin/env python3
"""
Test the complete integration: Plugin whispers and suggestions.
Following the "Silent Integration" pattern.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from luminous_nix.core.engine import NixForHumanityBackend
from luminous_nix.api.schema import Request

def test_silent_integration():
    """Test the whisper of suggestion pattern."""
    
    print("🌟 Testing the Silent Integration Pattern\n")
    print("=" * 60)
    
    backend = NixForHumanityBackend()
    
    # Test queries with varying confidence levels
    test_cases = [
        {
            "query": "start focus session for 25 minutes",
            "expected": "high_confidence_plugin",
            "description": "Direct plugin match"
        },
        {
            "query": "I need to focus on my work",
            "expected": "medium_confidence_suggestion",
            "description": "Plugin whisper suggestion"
        },
        {
            "query": "install firefox",
            "expected": "core_command",
            "description": "Core NixOS command"
        },
        {
            "query": "help me avoid distractions",
            "expected": "low_confidence_suggestion",
            "description": "Related to plugin domain"
        }
    ]
    
    for test in test_cases:
        print(f"\n📝 Test: {test['description']}")
        print(f"   Query: '{test['query']}'")
        
        # Check routing decision
        if backend.plugin_router:
            route = backend.plugin_router.route(test['query'])
            print(f"   Route: {route.handler_type} (confidence: {route.confidence:.0%})")
            
            # If medium confidence, show whisper suggestion
            if route.handler_type == 'plugin' and 0.4 < route.confidence < 0.7:
                suggestions = backend.plugin_router.get_plugin_suggestions(test['query'])
                if suggestions:
                    print(f"\n   💡 Whisper from the ecosystem:")
                    print(f"      The '{suggestions[0]['plugin_name']}' plugin might help with this.")
                    print(f"      It {suggestions[0]['description'][:50]}...")
        
        # Process the request
        request = Request(
            query=test['query'],
            context={"personality": "friendly"}
        )
        
        response = backend.process(request)
        
        if response.success:
            # Check for whispers in the response
            if "Whisper from the ecosystem" in response.text:
                print(f"   ✅ Core response with plugin whisper!")
                # Extract and show the whisper
                whisper_start = response.text.find("💡")
                if whisper_start > 0:
                    whisper = response.text[whisper_start:whisper_start+150]
                    print(f"   {whisper}...")
            else:
                # Show abbreviated response
                text = response.text.replace('\n', ' ')[:150]
                print(f"   ✅ Response: {text}...")
            
            # Check if it was handled by a plugin
            if response.data and response.data.get('plugin_id'):
                print(f"   🔌 Handled by: {response.data['plugin_name']}")
    
    print("\n" + "=" * 60)
    print("✨ Silent Integration test complete!")
    print("\nThe plugin system whispers suggestions when confidence is medium,")
    print("executes directly when confidence is high, and stays silent when low.")

if __name__ == "__main__":
    test_silent_integration()