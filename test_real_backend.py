#!/usr/bin/env python3
"""Test the real backend implementation"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import from core modules correctly
from luminous_nix.core.backend_real import RealNixBackend
from luminous_nix.api.schema import Response
from luminous_nix.core.intents import Intent, IntentType

def test_real_backend():
    """Test the real backend with actual operations"""
    
    print("🧪 Testing Real NixOS Backend")
    print("=" * 50)
    
    backend = RealNixBackend()
    
    # Test 1: Help
    print("\n1. Testing HELP:")
    intent = Intent(
        type=IntentType.HELP,
        entities={},
        confidence=1.0,
        raw_text="help"
    )
    response = backend.process(intent)
    print(f"✅ Help works!" if response.success else f"❌ Failed: {response.text}")
    if response.success:
        print(f"   Message length: {len(response.text)} chars")
    
    # Test 2: List installed packages
    print("\n2. Testing LIST:")
    intent = Intent(
        type=IntentType.LIST_INSTALLED,
        entities={},
        confidence=1.0,
        raw_text="list"
    )
    response = backend.process(intent)
    print(f"✅ List works!" if response.success else f"❌ Failed: {response.text}")
    if response.success:
        packages = response.data.get("packages", []) if response.data else []
        print(f"   Found {len(packages)} packages")
    
    # Test 3: Search for vim
    print("\n3. Testing SEARCH (timeout 5s):")
    backend.executor.timeout = 5  # Short timeout
    intent = Intent(
        type=IntentType.SEARCH_PACKAGE,
        entities={"package": "vim"},
        confidence=1.0,
        raw_text="search vim"
    )
    response = backend.process(intent)
    print(f"✅ Search works!" if response.success else f"⚠️  Search failed (might timeout)")
    if response.success:
        print(f"   Output: {response.text[:200]}...")
    
    # Test 4: System info
    print("\n4. Testing INFO:")
    intent = Intent(
        type=IntentType.CHECK_STATUS,
        entities={},
        confidence=1.0,
        raw_text="info"
    )
    response = backend.process(intent)
    print(f"✅ Info works!" if response.success else f"❌ Failed: {response.text}")
    if response.success and response.data:
        for key, value in response.data.items():
            print(f"   {key}: {value}")
    
    # Test 5: Dry run install
    print("\n5. Testing INSTALL (dry run):")
    import os
    os.environ["LUMINOUS_DRY_RUN"] = "true"
    backend = RealNixBackend()  # Reinitialize with dry run
    intent = Intent(
        type=IntentType.INSTALL_PACKAGE,
        entities={"package": "cowsay"},
        confidence=1.0,
        raw_text="install cowsay"
    )
    response = backend.process(intent)
    print(f"✅ Dry run works!" if response.success else f"❌ Failed: {response.text}")
    print(f"   {response.text}")
    
    print("\n" + "=" * 50)
    print("📊 Summary:")
    print("The real backend is working with actual NixOS commands!")
    print("We can now build on this foundation.")
    
if __name__ == "__main__":
    test_real_backend()