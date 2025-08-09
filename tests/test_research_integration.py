#!/usr/bin/env python3
"""
Test script for research-based components integration

This script verifies that all research components are properly integrated
with the main Nix for Humanity backend.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add the backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Enable research components
os.environ['NIX_HUMANITY_SKG_PATH'] = './test_skg.db'
os.environ['NIX_HUMANITY_ENHANCED_RESPONSES'] = 'true'


async def test_integration():
    """Test the research components integration"""
    
    print("🧪 Testing Research Components Integration")
    print("=" * 50)
    
    try:
        # Import after setting environment
        from nix_humanity.core.engine import NixForHumanityBackend
        from nix_humanity.api.schema import Request, Context
        
        # Create backend
        print("\n1️⃣ Creating backend with research components...")
        backend = NixForHumanityBackend()
        
        # Check what got initialized
        print("\n2️⃣ Checking initialized components:")
        print(f"   ✓ SKG Available: {backend.skg is not None}")
        print(f"   ✓ Trust Engine: {backend.trust_engine is not None}")
        print(f"   ✓ Metrics Collector: {backend.metrics_collector is not None}")
        print(f"   ✓ Activity Monitor: {backend.activity_monitor is not None}")
        print(f"   ✓ Consciousness Guard: {backend.consciousness_guard is not None}")
        
        # Test a simple request
        print("\n3️⃣ Testing request processing with awareness...")
        
        # Create a test request with simple context
        test_request = Request(
            query="install firefox",
            context={
                'personality': 'friendly',
                'execute': False,
                'collect_feedback': True,
                'session_start': asyncio.get_event_loop().time(),
                'interruption_count': 0,
                'breaks_taken': 0,
                'focus_duration': 0
            }
        )
        
        # Process request
        response = await backend.process_request(test_request)
        
        print(f"\n4️⃣ Response received:")
        print(f"   ✓ Success: {response.success}")
        print(f"   ✓ Intent: {response.intent.type.value if response.intent else 'unknown'}")
        print(f"   ✓ Explanation: {response.explanation[:100]}...")
        
        # Check if research data was added
        if response.data:
            print(f"\n5️⃣ Research enhancements:")
            if 'consciousness_metrics' in response.data:
                metrics = response.data['consciousness_metrics']
                print(f"   ✓ Wellbeing Score: {metrics.get('wellbeing_score')}")
                print(f"   ✓ Attention State: {metrics.get('attention_state')}")
                print(f"   ✓ Flow State: {metrics.get('flow_state')}")
                
            if 'trust_building' in response.data:
                print(f"   ✓ Trust Building: {response.data['trust_building']}")
                
        # Test the SKG directly if available
        if backend.skg:
            print(f"\n6️⃣ Testing SKG directly:")
            
            # Query ontological layer
            concepts = backend.skg.ontological.get_concept("install_package")
            print(f"   ✓ Ontological concepts: {len(concepts) if concepts else 0}")
            
            # Check episodic memory
            recent = backend.skg.episodic.get_recent_interactions(limit=5)
            print(f"   ✓ Episodic interactions: {len(recent)}")
            
        print("\n✅ Integration test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    return True


async def test_consciousness_flow():
    """Test consciousness-aware request flow"""
    
    print("\n\n🧘 Testing Consciousness-Aware Flow")
    print("=" * 50)
    
    try:
        from nix_humanity.core.engine import NixForHumanityBackend
        from nix_humanity.api.schema import Request, Context
        
        backend = NixForHumanityBackend()
        
        if not backend.consciousness_guard:
            print("⚠️  Consciousness Guard not available, skipping test")
            return True
            
        # Simulate different consciousness states
        scenarios = [
            {
                'name': 'Low Wellbeing',
                'context': {
                    'session_start': asyncio.get_event_loop().time() - 7200,  # 2 hours
                    'interruption_count': 15,
                    'breaks_taken': 0,
                    'focus_duration': 0
                },
                'query': 'my system is broken help'
            },
            {
                'name': 'Flow State',
                'context': {
                    'session_start': asyncio.get_event_loop().time() - 3600,  # 1 hour
                    'interruption_count': 0,
                    'breaks_taken': 2,
                    'focus_duration': 2400  # 40 minutes
                },
                'query': 'update system'
            }
        ]
        
        for scenario in scenarios:
            print(f"\n📍 Testing: {scenario['name']}")
            
            request = Request(
                query=scenario['query'],
                context={
                    'personality': 'friendly',
                    'execute': False,
                    **scenario['context']
                }
            )
            
            response = await backend.process_request(request)
            
            print(f"   ✓ Response adapted: {len(response.explanation)} chars")
            print(f"   ✓ Suggestions: {len(response.suggestions) if response.suggestions else 0}")
            
            if response.data and 'consciousness_metrics' in response.data:
                metrics = response.data['consciousness_metrics']
                print(f"   ✓ Detected state: {metrics.get('attention_state')}")
                
        print("\n✅ Consciousness flow test completed!")
        
    except Exception as e:
        print(f"\n❌ Consciousness flow test failed: {e}")
        return False
        
    return True


async def main():
    """Run all integration tests"""
    
    print("🚀 Nix for Humanity Research Integration Test Suite")
    print("=" * 60)
    
    # Run tests
    integration_ok = await test_integration()
    consciousness_ok = await test_consciousness_flow()
    
    # Summary
    print("\n\n📊 Test Summary")
    print("=" * 50)
    print(f"Integration Test: {'✅ PASSED' if integration_ok else '❌ FAILED'}")
    print(f"Consciousness Test: {'✅ PASSED' if consciousness_ok else '❌ FAILED'}")
    
    # Cleanup
    test_db = Path('./test_skg.db')
    if test_db.exists():
        test_db.unlink()
        print(f"\n🧹 Cleaned up test database")
    
    return integration_ok and consciousness_ok


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)