#!/usr/bin/env python3
"""
Test script for the headless core engine
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from nix_for_humanity.core import (
    NixForHumanityCore, 
    Query, 
    ExecutionMode,
    PersonalityStyle
)


def test_core():
    """Test the core engine with various queries"""
    
    # Initialize core
    core = NixForHumanityCore({
        'dry_run': True,
        'default_personality': 'friendly',
        'enable_learning': True,
        'collect_feedback': True
    })
    
    # Test queries
    test_queries = [
        "install firefox",
        "search python",
        "update my system", 
        "help",
        "remove vim",
        "what's a generation?",
        "my wifi isn't working"
    ]
    
    print("🧪 Testing Nix for Humanity Core Engine\n")
    print("=" * 60)
    
    for query_text in test_queries:
        print(f"\n📝 Query: {query_text}")
        print("-" * 40)
        
        # Create query
        query = Query(
            text=query_text,
            personality='friendly',
            mode=ExecutionMode.DRY_RUN,
            user_id='test-user',
            session_id='test-session'
        )
        
        # Process
        response = core.process(query)
        
        # Display results
        print(f"🎯 Intent: {response.intent.type.value}")
        if response.intent.target:
            print(f"📦 Target: {response.intent.target}")
        print(f"🔮 Confidence: {response.intent.confidence:.0%}")
        
        if response.command:
            print(f"💻 Command: {response.command.program} {' '.join(response.command.args)}")
            
        print(f"\n💬 Response:\n{response.text}")
        
        if response.suggestions:
            print("\n💡 Suggestions:")
            for suggestion in response.suggestions:
                print(f"   • {suggestion}")
                
        print(f"\n⏱️  Processing time: {response.processing_time_ms}ms")
        print("=" * 60)
        
    # Test different personalities
    print("\n\n🎭 Testing Personality Styles\n")
    print("=" * 60)
    
    query = Query(
        text="install neovim",
        mode=ExecutionMode.DRY_RUN
    )
    
    for style in ['minimal', 'friendly', 'encouraging', 'technical', 'symbiotic']:
        print(f"\n🎨 Style: {style}")
        print("-" * 40)
        
        query.personality = style
        response = core.process(query)
        print(response.text)
        print("=" * 60)
        
    # Show stats
    stats = core.get_system_stats()
    print("\n\n📊 System Statistics")
    print("=" * 60)
    for key, value in stats.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    test_core()