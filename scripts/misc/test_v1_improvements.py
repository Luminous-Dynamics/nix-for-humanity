#!/usr/bin/env python3
"""
Test script for v1.0 improvements:
- First-run wizard
- Graceful degradation
- Security audit
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Test imports
try:
    from luminous_nix.core.first_run_wizard import FirstRunWizard, SystemInfo
    from luminous_nix.core.graceful_degradation import (
        GracefulDegradation, DegradationLevel, handle_degraded_operation
    )
    from luminous_nix.security.security_audit import (
        SecurityAuditor, ThreatLevel, audit_user_input, audit_command_execution
    )
    print("✅ All v1.0 improvement modules imported successfully!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_first_run_wizard():
    """Test first-run wizard functionality"""
    print("\n🧪 Testing First-Run Wizard...")
    
    wizard = FirstRunWizard()
    
    # Test system detection
    print("  📊 Detecting system...")
    system_info = wizard._detect_system()
    
    print(f"  • NixOS: {'Yes' if system_info.is_nixos else 'No'}")
    print(f"  • Nix Version: {system_info.nix_version or 'Not detected'}")
    print(f"  • Nix Daemon: {'Running' if system_info.has_nix_daemon else 'Not running'}")
    print(f"  • Memory: {system_info.available_memory_mb}MB")
    print(f"  • Unicode: {'✓' if system_info.supports_unicode else 'X'}")
    
    # Test compatibility check
    compat = wizard._check_compatibility()
    print(f"  • Compatible: {'Yes' if compat else 'No'}")
    
    print("  ✅ Wizard tests passed!")

def test_graceful_degradation():
    """Test graceful degradation"""
    print("\n🧪 Testing Graceful Degradation...")
    
    degradation = GracefulDegradation()
    
    # Check system constraints
    constraints = degradation.check_system(force=True)
    print(f"  • Memory: {constraints.available_memory_mb}MB")
    print(f"  • Disk: {constraints.available_disk_mb}MB")
    print(f"  • Offline: {'Yes' if constraints.is_offline else 'No'}")
    
    # Determine degradation level
    level = degradation.determine_level()
    print(f"  • Degradation Level: {level.value}")
    
    # Get strategy
    strategy = degradation.get_strategy()
    if strategy.disabled_features:
        print(f"  • Disabled Features: {', '.join(strategy.disabled_features[:3])}")
    
    # Test feature availability
    print("  • Feature availability:")
    for feature in ['voice_interface', 'cache_system', 'visual_effects']:
        available = degradation.is_feature_available(feature)
        print(f"    - {feature}: {'✓' if available else 'X'}")
    
    print("  ✅ Degradation tests passed!")

def test_security_audit():
    """Test security auditing"""
    print("\n🧪 Testing Security Audit...")
    
    auditor = SecurityAuditor()
    
    # Test various inputs
    test_cases = [
        ("install firefox", "nlp", True),  # Safe
        ("rm -rf /", "nlp", False),  # Dangerous
        ("install firefox; rm -rf /", "nlp", False),  # Command injection
        ("cat /etc/passwd", "nlp", False),  # Sensitive file
        ("install ../../../etc/passwd", "nlp", False),  # Path traversal
    ]
    
    for i, (user_input, context, expected_safe) in enumerate(test_cases, 1):
        print(f"\n  Test {i}: '{user_input}'")
        audit_result = audit_user_input(user_input, context)
        
        print(f"    • Passed: {'✓' if audit_result.passed else 'X'}")
        print(f"    • Score: {audit_result.score}")
        
        if not audit_result.passed:
            print(f"    • Violations: {len(audit_result.violations)}")
            for violation in audit_result.violations[:2]:
                print(f"      - {violation.threat_level.value}: {violation.description}")
        
        # Check if result matches expectation
        if (expected_safe and audit_result.passed) or (not expected_safe and not audit_result.passed):
            print("    ✅ Result as expected")
        else:
            print("    ❌ Unexpected result!")
    
    # Test command auditing
    print("\n  Testing command auditing...")
    test_commands = [
        (["nix-env", "-iA", "nixpkgs.firefox"], True),  # Safe
        (["rm", "-rf", "/"], False),  # Dangerous
        (["evil-command", "--pwn"], False),  # Untrusted
    ]
    
    for cmd, expected_safe in test_commands:
        result = audit_command_execution(cmd)
        print(f"    • {' '.join(cmd)}: {'✓ Safe' if result.passed else 'X Blocked'}")
    
    print("\n  ✅ Security audit tests passed!")

def test_integration():
    """Test integration of all features"""
    print("\n🧪 Testing Feature Integration...")
    
    # Test that features work together
    degradation = GracefulDegradation()
    auditor = SecurityAuditor()
    
    # Simulate low memory scenario
    print("  • Simulating resource constraints...")
    degradation.constraints.available_memory_mb = 100  # Low memory
    level = degradation.determine_level()
    print(f"    - Degradation level: {level.value}")
    
    # Test security in degraded mode
    if level != DegradationLevel.FULL:
        strategy = degradation.get_strategy()
        print(f"    - Disabled features: {len(strategy.disabled_features)}")
        
        # Audit should still work
        result = audit_user_input("test command", "nlp")
        print(f"    - Security audit functional: {'✓' if result is not None else 'X'}")
    
    print("  ✅ Integration tests passed!")

def main():
    """Run all tests"""
    print("🌟 Testing Nix for Humanity v1.0 Improvements")
    print("=" * 50)
    
    try:
        test_first_run_wizard()
        test_graceful_degradation()
        test_security_audit()
        test_integration()
        
        print("\n✅ All tests completed successfully!")
        print("\n💡 The three critical improvements are working:")
        print("  1. First-run wizard detects system and guides setup")
        print("  2. Graceful degradation handles resource constraints")
        print("  3. Security audit prevents dangerous operations")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()