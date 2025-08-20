#!/usr/bin/env python3
"""
Test script for the headless core engine
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from luminous_nix.core import (
    NixForHumanityBackend,
    PersonalitySystem
)


def test_core():
    """Test the core engine with various queries"""
    
    # Initialize core
    core = NixForHumanityBackend()
    
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
        
        # Process the query directly
        result = core.execute_command(query_text, dry_run=True)
        
        # Display results
        if result.get('success'):
            print(f"✅ Success: {result.get('message', 'Command processed successfully')}")
            if result.get('command'):
                print(f"💻 Command: {result['command']}")
            if result.get('response'):
                print(f"\n💬 Response:\n{result['response']}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            
        print("=" * 60)
        
    # Test shows basic functionality
    print("\n\n✅ Basic core functionality test complete")
    print("=" * 60)


if __name__ == "__main__":
    test_core()