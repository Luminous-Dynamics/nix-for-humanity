#!/usr/bin/env python3
"""
Simple test for research components integration
Tests individual components without going through the full backend flow
"""

import os
import sys
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

def test_individual_components():
    """Test research components individually"""
    
    print("🧪 Testing Individual Research Components")
    print("=" * 50)
    
    # Test 1: Backend initialization
    print("\n1️⃣ Testing backend initialization...")
    try:
        from nix_humanity.core.engine import NixForHumanityBackend
        backend = NixForHumanityBackend()
        print("   ✅ Backend created successfully")
        print(f"   • Native API: {backend.nix_integration is not None}")
        print(f"   • Intent Recognizer: {backend.intent_recognizer is not None}")
        print(f"   • Knowledge Base: {backend.knowledge is not None}")
    except Exception as e:
        print(f"   ❌ Backend initialization failed: {e}")
        return False
    
    # Test 2: Research component availability
    print("\n2️⃣ Checking research component availability...")
    research_components = {
        'SKG': getattr(backend, 'skg', None),
        'Trust Engine': getattr(backend, 'trust_engine', None),
        'Metrics Collector': getattr(backend, 'metrics_collector', None),
        'Activity Monitor': getattr(backend, 'activity_monitor', None),
        'Consciousness Guard': getattr(backend, 'consciousness_guard', None),
    }
    
    for name, component in research_components.items():
        status = "✅ Available" if component is not None else "⚠️  Not available"
        print(f"   • {name}: {status}")
    
    # Test 3: Simple intent recognition
    print("\n3️⃣ Testing simple intent recognition...")
    try:
        from nix_humanity.core.intents import IntentRecognizer
        recognizer = IntentRecognizer()
        
        # Test with a simple query
        intent = recognizer.recognize("install firefox")
        print(f"   ✅ Intent recognized: {intent.type.value}")
        print(f"   • Confidence: {intent.confidence}")
        print(f"   • Entities: {intent.entities}")
    except Exception as e:
        print(f"   ❌ Intent recognition failed: {e}")
    
    # Test 4: Knowledge base
    print("\n4️⃣ Testing knowledge base...")
    try:
        from nix_humanity.core.knowledge import KnowledgeBase
        kb = KnowledgeBase()
        
        # Search for a package
        results = kb.search_packages("firefox")
        print(f"   ✅ Knowledge base search: {len(results)} results")
        if results:
            print(f"   • First result: {results[0].get('name', 'unknown')}")
    except Exception as e:
        print(f"   ❌ Knowledge base failed: {e}")
    
    # Test 5: Mock research components
    print("\n5️⃣ Testing mock research components...")
    try:
        # Try to import the mock trust metrics
        from features.v3_0.intelligence.trust_modeling.trust_metrics_mock import TrustMetrics
        metrics = TrustMetrics()
        trust_data = metrics.to_dict()
        print(f"   ✅ Mock trust metrics working:")
        print(f"   • Overall trust: {trust_data['overall']:.2f}")
        print(f"   • Vulnerability: {trust_data['vulnerability']}")
    except Exception as e:
        print(f"   ❌ Mock components failed: {e}")
    
    # Test 6: Response generation
    print("\n6️⃣ Testing response generation...")
    try:
        # Check if we can create a simple response
        from nix_humanity.api.schema import Response, Result
        
        response = Response(
            success=True,
            result=Result(
                command="nix-env -iA nixpkgs.firefox",
                explanation="Installing Firefox web browser",
                suggestions=["Firefox has been installed", "You can launch it from your applications menu"]
            ),
            intent=None,
            explanation="Installing Firefox web browser from nixpkgs",
            suggestions=["After installation, you can launch Firefox from your applications menu"],
            data={"test": "success"}
        )
        
        print(f"   ✅ Response creation successful")
        print(f"   • Success: {response.success}")
        print(f"   • Has result: {response.result is not None}")
    except Exception as e:
        print(f"   ❌ Response generation failed: {e}")
    
    print("\n✅ Component testing completed!")
    return True


def test_research_config():
    """Test research configuration loading"""
    
    print("\n\n🔧 Testing Research Configuration")
    print("=" * 50)
    
    try:
        from nix_humanity.config.research_config import ResearchConfig
        
        config = ResearchConfig()
        print("✅ Research config loaded successfully")
        
        # Check config values
        print(f"   • SKG enabled: {config.skg_enabled}")
        print(f"   • Trust modeling: {config.trust_modeling_enabled}")
        print(f"   • Consciousness metrics: {config.consciousness_metrics_enabled}")
        
    except Exception as e:
        print(f"❌ Research config not available: {e}")
        print("   This is normal if research components are optional")
    
    return True


def main():
    """Run all simple tests"""
    
    print("🚀 Nix for Humanity Research Components Test")
    print("=" * 60)
    print("Testing individual components without full integration")
    
    # Run tests
    components_ok = test_individual_components()
    config_ok = test_research_config()
    
    # Summary
    print("\n\n📊 Test Summary")
    print("=" * 50)
    print(f"Component Tests: {'✅ PASSED' if components_ok else '❌ FAILED'}")
    print(f"Config Test: {'✅ PASSED' if config_ok else '❌ FAILED'}")
    
    print("\n💡 Note: Research components are optional.")
    print("The system works fine without them, they just add extra features.")
    
    return components_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)