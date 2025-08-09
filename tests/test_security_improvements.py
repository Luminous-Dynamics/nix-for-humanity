#!/usr/bin/env python3
"""
Test script to verify security improvements in Nix for Humanity
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from nix_humanity.security.input_validator import InputValidator
from nix_humanity.security.command_validator import CommandValidator
from nix_humanity.security.permission_checker import PermissionChecker
from nix_humanity.core.engine import NixForHumanityBackend
from nix_humanity.api.schema import Request


def test_security_improvements():
    """Test the security improvements"""
    print("🔒 Testing Nix for Humanity Security Improvements\n")
    
    # Test 1: Input validation
    print("1️⃣ Testing Input Validation:")
    test_inputs = [
        ("install firefox", "nlp", True),
        ("rm -rf /", "nlp", False),
        ("install firefox; rm -rf /", "nlp", False),
        ("../../etc/passwd", "path", False),
        ("firefox", "package", True),
        ("firefox`echo bad`", "package", False),
    ]
    
    for user_input, input_type, expected_valid in test_inputs:
        result = InputValidator.validate_input(user_input, input_type)
        status = "✅" if result['valid'] == expected_valid else "❌"
        print(f"  {status} '{user_input}' ({input_type}): Valid={result['valid']}")
        if not result['valid']:
            print(f"     Reason: {result['reason']}")
    
    print("\n2️⃣ Testing Command Validation:")
    test_commands = [
        (['nix-env', '-iA', 'nixpkgs.firefox'], True),
        (['nixos-rebuild', 'switch'], True),
        (['nixos-rebuild', 'switch', '--install-bootloader'], False),
        (['rm', '-rf', '/'], False),
        (['nix-shell', '--run', 'malicious'], False),
    ]
    
    for command, expected_valid in test_commands:
        valid, error, metadata = CommandValidator.validate_nix_command(command)
        status = "✅" if valid == expected_valid else "❌"
        print(f"  {status} {' '.join(command)}: Valid={valid}")
        if not valid:
            print(f"     Error: {error}")
            if metadata:
                print(f"     Risk: {CommandValidator.explain_risk(metadata)}")
    
    print("\n3️⃣ Testing Permission Checks:")
    operations = [
        ('install-package', {'command': ['nix-env', '-iA', 'nixpkgs.firefox']}),
        ('modify-configuration', {'file_path': '/etc/nixos/configuration.nix', 'mode': 'write'}),
        ('manage-service', {'command': ['systemctl', 'restart', 'nginx']}),
    ]
    
    for operation, context in operations:
        result = PermissionChecker.check_operation_permission(operation, context)
        status = "✅ Allowed" if result['allowed'] else "❌ Denied"
        elevation = " (sudo required)" if result.get('requires_elevation') else ""
        print(f"  {status}{elevation}: {operation}")
        print(f"     Reason: {result.get('reason', 'N/A')}")
    
    print("\n4️⃣ Testing Backend Integration:")
    backend = NixForHumanityBackend()
    
    # Test malicious input
    print("  Testing malicious input rejection...")
    from nix_humanity.api.schema import Context
    malicious_request = Request(
        query="install firefox; rm -rf /",
        context=Context()
    )
    
    response = backend._process_sync(malicious_request)
    if not response.success:
        print(f"  ✅ Malicious input blocked: {response.explanation or response.text}")
    else:
        print(f"  ❌ Security failure: Malicious input was not blocked!")
    
    # Test safe input
    print("\n  Testing safe input processing...")
    safe_request = Request(
        query="install firefox",
        context=Context()
    )
    
    response = backend._process_sync(safe_request)
    if response.success and response.intent:
        print(f"  ✅ Safe input processed: Intent={response.intent.type}")
    else:
        print(f"  ❌ Failed to process safe input: {response.explanation or response.text}")
    
    print("\n✨ Security test complete!")


if __name__ == "__main__":
    test_security_improvements()
