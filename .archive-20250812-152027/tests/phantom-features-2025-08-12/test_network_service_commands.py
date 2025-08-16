#!/usr/bin/env python3
"""
Test script for network and service management commands
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
    """Run tests for network and service management commands"""
    print("🧪 Testing Network & Service Management Commands")
    print("=" * 60)

    # Enable enhanced responses if available
    os.environ["LUMINOUS_NIX_ENHANCED_RESPONSES"] = "true"
    os.environ["LUMINOUS_NIX_PYTHON_BACKEND"] = "true"

    backend = NixForHumanityBackend()

    # Network management tests
    print("\n🌐 NETWORK MANAGEMENT TESTS")
    network_commands = [
        "show network",
        "what's my ip address?",
        "show me my network configuration",
        "connect to wifi MyHomeNetwork",
        "list available wifi networks",
        "scan for wifi",
        "test internet connection",
        "is my internet working?",
        "check connectivity",
    ]

    for cmd in network_commands:
        test_command(backend, cmd)

    # Service management tests
    print("\n⚡ SERVICE MANAGEMENT TESTS")
    service_commands = [
        "start nginx",
        "stop the web server",
        "restart docker service",
        "is ssh running?",
        "check nginx status",
        "list all services",
        "show running services",
        "enable docker at boot",
        "disable ssh service",
        "show logs for nginx",
        "docker service logs",
    ]

    for cmd in service_commands:
        test_command(backend, cmd)

    # Context-aware tests
    print("\n🧠 CONTEXT-AWARE TESTS")
    context_commands = [
        "I need docker",  # Should suggest installation
        "docker isn't working",  # Should suggest service commands
        "ssh won't start",  # Service context
        "install ssh",  # Package context
        "nginx is down",  # Service context
    ]

    for cmd in context_commands:
        test_command(backend, cmd)

    print("\n✨ All tests completed!")

if __name__ == "__main__":
    main()
