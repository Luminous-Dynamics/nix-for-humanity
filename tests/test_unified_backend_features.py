#!/usr/bin/env python3
"""
Test the unified backend with all 3 core features
"""

import sys
import os
from pathlib import Path

# Add paths for imports
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
sys.path.insert(0, str(script_dir / 'scripts'))
sys.path.insert(0, str(script_dir / 'scripts' / 'backend'))

# Import with proper module loading
import importlib.util
backend_path = script_dir / 'scripts' / 'backend' / 'unified_nix_backend.py'
spec = importlib.util.spec_from_file_location("unified_nix_backend", backend_path)
unified_backend_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(unified_backend_module)
UnifiedNixBackend = unified_backend_module.UnifiedNixBackend

def test_all_features():
    """Test all 3 core features through the unified backend"""
    print("🎯 Testing Unified Backend with Core Features")
    print("=" * 60)
    
    backend = UnifiedNixBackend()
    
    # Test queries for all 3 features
    test_queries = [
        # Configuration Generation
        "generate config for web server with nginx",
        "create configuration for desktop with kde and games",
        
        # Flake Management
        "create flake for python development",
        "make rust web server environment",
        
        # Generation Management
        "list generations",
        "check system health",
        "rollback to previous generation",
        "create snapshot before update",
        "compare generations 26 and 27",
    ]
    
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        print("-" * 40)
        
        # Extract intent
        intent = backend.extract_intent(query)
        print(f"🎯 Intent: {intent.type.value} (confidence: {intent.confidence:.2f})")
        
        # Show entities if any
        if intent.entities:
            print(f"📦 Entities: {intent.entities}")
        
        # Process intent
        context = {
            'personality': 'friendly',
            'frontend': 'cli',
            'collect_feedback': False
        }
        
        try:
            response = backend.process_intent(intent, context)
            print(f"✅ Success: {response.success}")
            
            # Show first few lines of response
            lines = response.text.split('\n')[:5]
            print(f"💬 Response preview:")
            for line in lines:
                print(f"   {line}")
            if len(response.text.split('\n')) > 5:
                print("   ...")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_all_features()
    print("\n\n✨ Unified Backend Test Complete!")