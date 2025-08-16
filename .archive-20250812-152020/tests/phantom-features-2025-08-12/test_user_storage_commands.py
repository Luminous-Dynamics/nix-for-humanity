#!/usr/bin/env python3
"""
Test script for new user and storage management commands
"""

import os
import sys
from pathlib import Path

# Add the backend to the path
sys.path.insert(0, str(Path(__file__).parent))

from luminous_nix.api.schema import Request
from luminous_nix.core.engine import NixForHumanityBackend

def test_command(backend, query):
    """Test a single command"""
    print(f"\n🔍 Testing: '{query}'")
    print("-" * 60)

    request = Request(
        query=query,
        context={
            "personality": "friendly",
            "execute": False,  # Don't actually execute commands
        },
    )

    response = backend.process(request)

    if response.success:
        print("✅ Success!")
        print(f"📝 Response: {response.text}")
        if response.commands:
            print("\n📋 Commands that would run:")
            for cmd in response.commands:
                print(f"  • {cmd.get('command', 'N/A')}")
    else:
        print(f"❌ Error: {response.error}")

    print("-" * 60)

def main():
    """Run tests for user and storage management commands"""
    print("🧪 Testing User & Storage Management Commands")
    print("=" * 60)

    # Enable enhanced responses if available
    os.environ["LUMINOUS_NIX_ENHANCED_RESPONSES"] = "true"
    os.environ["LUMINOUS_NIX_PYTHON_BACKEND"] = "true"

    backend = NixForHumanityBackend()

    # User management tests
    print("\n👤 USER MANAGEMENT TESTS")
    user_commands = [
        "create user alice",
        "list users",
        "add alice to docker group",
        "change password alice",
        "grant alice sudo",
        "make bob a new user",
        "who are the users on this system?",
        "give john admin access",
    ]

    for cmd in user_commands:
        test_command(backend, cmd)

    # Storage management tests
    print("\n💾 STORAGE MANAGEMENT TESTS")
    storage_commands = [
        "disk usage",
        "show disk space",
        "analyze disk",
        "what's using disk space?",
        "mount /dev/sdb1",
        "unmount /dev/sdb1",
        "find large files",
        "find the 20 largest files",
        "how much space do I have?",
        "my disk is full",
    ]

    for cmd in storage_commands:
        test_command(backend, cmd)

    print("\n✨ All tests completed!")

if __name__ == "__main__":
    main()
