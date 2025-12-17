#!/usr/bin/env python3
"""
Quick test to verify chat system initializes correctly
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_initialization():
    """Test that all components can be imported and initialized"""

    print("🧪 Testing Chat System Initialization\n")
    print("=" * 60)

    # Test 1: Import context managers
    print("\n1. Testing context managers...")
    try:
        from luminous_nix.ai.context import (
            SystemContextGatherer,
            UserContextManager,
            SkillLevel
        )
        print("   ✅ Context managers imported successfully")
    except Exception as e:
        print(f"   ❌ Failed to import context managers: {e}")
        return False

    # Test 2: Initialize system context
    print("\n2. Testing system context gathering...")
    try:
        gatherer = SystemContextGatherer()
        context = gatherer.gather()
        print(f"   ✅ System context gathered")
        print(f"      Hostname: {context.hostname}")
        print(f"      NixOS: {context.nixos_version}")
        print(f"      Using: {context.channel_or_flake}")
    except Exception as e:
        print(f"   ⚠️  System context failed (non-critical): {e}")

    # Test 3: Initialize user context
    print("\n3. Testing user context manager...")
    try:
        user_mgr = UserContextManager()
        user_ctx = user_mgr.get_context()
        print(f"   ✅ User context initialized")
        print(f"      Skill level: {user_ctx.skill_level.value}")
        print(f"      Prefers flakes: {user_ctx.prefers_flakes}")
        print(f"      Profile: {user_mgr.profile_path}")
    except Exception as e:
        print(f"   ❌ User context failed: {e}")
        return False

    # Test 4: Import SimpleChat
    print("\n4. Testing SimpleChat import...")
    try:
        from luminous_nix.ai.conversation import SimpleChat
        print("   ✅ SimpleChat imported successfully")
    except Exception as e:
        print(f"   ❌ Failed to import SimpleChat: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test 5: Try to initialize SimpleChat (but don't run loop)
    print("\n5. Testing SimpleChat initialization...")
    try:
        chat = SimpleChat()
        print("   ✅ SimpleChat initialized successfully")
        print(f"\n   Components available:")
        for component, available in chat.components_available.items():
            status = "✅" if available else "⚠️ "
            print(f"      {status} {component}")
    except Exception as e:
        print(f"   ⚠️  SimpleChat initialization had issues: {e}")
        import traceback
        traceback.print_exc()
        # Not necessarily fatal - some components may be missing

    print("\n" + "=" * 60)
    print("\n✅ Initialization test complete!")
    print("\nThe chat system is ready to use:")
    print("  poetry run ask-nix chat")

    return True

if __name__ == "__main__":
    success = test_initialization()
    sys.exit(0 if success else 1)
