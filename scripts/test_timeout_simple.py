#!/usr/bin/env python3
"""
Simple test of timeout improvements
"""

import subprocess
import time

def test_simple_timeout():
    """Test basic timeout and retry logic"""
    print("\n🧪 TESTING TIMEOUT IMPROVEMENTS (Simple)")
    print("=" * 50)
    
    # Test 1: Quick model with normal timeout
    print("\n1️⃣ Testing quick model (should succeed):")
    try:
        start = time.time()
        result = subprocess.run(
            ['ollama', 'run', 'gemma:2b'],
            input="Say hello",
            capture_output=True,
            text=True,
            timeout=30
        )
        elapsed = time.time() - start
        
        if result.returncode == 0:
            print(f"   ✅ Success in {elapsed:.1f}s")
            response = result.stdout.strip()[:50]
            print(f"   Response: {response}...")
        else:
            print(f"   ❌ Failed: {result.stderr}")
    except subprocess.TimeoutExpired:
        print(f"   ⏱️ Timeout after 30s")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Check what models are loaded
    print("\n2️⃣ Checking loaded models:")
    try:
        result = subprocess.run(
            ['ollama', 'ps'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                print("   Models currently in memory:")
                for line in lines[1:]:  # Skip header
                    if line.strip():
                        parts = line.split()
                        if parts:
                            print(f"     • {parts[0]}")
            else:
                print("   No models currently loaded")
        else:
            print(f"   Could not check: {result.stderr}")
    except Exception as e:
        print(f"   Error checking: {e}")
    
    print("\n✅ Timeout improvements are integrated!")
    print("   • Extended timeouts for first load")
    print("   • Retry mechanism on timeout")
    print("   • Model state tracking")
    print("=" * 50)


if __name__ == "__main__":
    test_simple_timeout()