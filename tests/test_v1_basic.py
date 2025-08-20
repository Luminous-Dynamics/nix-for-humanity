#!/usr/bin/env python3
"""
Basic test runner for v1.0 features without pytest dependency
"""

import sys
import time
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

# Import v1.0 components
try:
    from luminous_nix.core import (
        NixForHumanityBackend,
        IntentRecognizer,
        Intent,
        IntentType,
        SafeExecutor,
        KnowledgeBase
    )
    from luminous_nix.api import Request, Response, Result
    print("✅ All core imports successful!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_basic_functionality():
    """Test basic v1.0 functionality"""
    print("\n🧪 Testing basic v1.0 functionality...")
    
    # Create backend
    backend = NixForHumanityBackend()
    print("✅ Backend created successfully")
    
    # Test natural language queries
    test_queries = [
        "install firefox",
        "search python",
        "update system",
        "rollback",
        "help"
    ]
    
    for query in test_queries:
        print(f"\n📝 Testing: '{query}'")
        try:
            start_time = time.time()
            
            request = Request(query=query, context={'personality': 'minimal'})
            response = backend.process(request)
            
            elapsed = time.time() - start_time
            
            if response.success:
                print(f"✅ Success in {elapsed:.3f}s")
                print(f"   Response: {response.text[:100]}...")
            else:
                print(f"❌ Failed: {response.error}")
                
            # Performance check
            if elapsed > 0.5:
                print(f"⚠️  Performance warning: {elapsed:.3f}s > 0.5s limit")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def test_import_cleanup():
    """Test that v2.0+ imports are properly removed/disabled"""
    print("\n🧪 Testing import cleanup...")
    
    # Check that research components gracefully fail
    try:
        backend = NixForHumanityBackend()
        
        # Check SKG availability
        if hasattr(backend, 'skg'):
            if backend.skg is None:
                print("✅ SKG properly disabled for v1.0")
            else:
                print("⚠️  SKG is available but should be disabled in v1.0")
        else:
            print("✅ SKG not in backend (good for v1.0)")
            
        # Check other research components
        research_attrs = ['trust_engine', 'metrics_collector', 'activity_monitor', 'consciousness_guard']
        for attr in research_attrs:
            if hasattr(backend, attr):
                if getattr(backend, attr) is None:
                    print(f"✅ {attr} properly disabled for v1.0")
                else:
                    print(f"⚠️  {attr} is available but should be disabled in v1.0")
            else:
                print(f"✅ {attr} not in backend (good for v1.0)")
                
    except Exception as e:
        print(f"❌ Error checking imports: {e}")

def test_performance():
    """Test performance of core operations"""
    print("\n🧪 Testing performance...")
    
    backend = NixForHumanityBackend()
    
    # Test intent recognition speed
    queries = ["install vim", "search editor", "update", "help me install firefox"]
    
    total_time = 0
    for query in queries:
        start = time.time()
        request = Request(query=query, context={})
        response = backend.process(request)
        elapsed = time.time() - start
        total_time += elapsed
        
        status = "✅" if elapsed < 0.5 else "❌"
        print(f"{status} '{query}': {elapsed:.3f}s")
    
    avg_time = total_time / len(queries)
    print(f"\n📊 Average response time: {avg_time:.3f}s")
    
    if avg_time < 0.3:
        print("✅ Excellent performance!")
    elif avg_time < 0.5:
        print("⚠️  Acceptable performance, but could be improved")
    else:
        print("❌ Performance needs optimization")

def main():
    """Run all tests"""
    print("🚀 Nix for Humanity v1.0 Basic Test Suite")
    print("=" * 60)
    
    test_basic_functionality()
    test_import_cleanup()
    test_performance()
    
    print("\n" + "=" * 60)
    print("✅ Basic test suite complete!")
    print("\nNext steps:")
    print("1. Fix any failing tests")
    print("2. Optimize performance for operations > 0.5s")
    print("3. Polish error messages")
    print("4. Run full test suite with pytest when available")

if __name__ == "__main__":
    main()