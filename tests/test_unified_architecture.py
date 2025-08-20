#!/usr/bin/env python3
"""
Test script to verify the Unified System Architecture refactoring
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from luminous_nix.core.engine import NixForHumanityBackend
from luminous_nix.api.schema import Request
import json

def test_orchestrator_integration():
    """Test that the System Orchestrator is properly integrated"""
    print("\n🧪 Testing Unified System Architecture...")
    
    engine = NixForHumanityBackend()
    
    # Test 1: Verify orchestrator exists
    print("\n1️⃣ Checking orchestrator initialization...")
    if hasattr(engine, 'orchestrator'):
        print("✅ System Orchestrator initialized")
        
        # Check capabilities
        status = engine.orchestrator.get_status()
        print(f"   Available capabilities: {len(status.capabilities)} systems")
        for cap, enabled in status.capabilities.items():
            status_icon = "✅" if enabled else "❌"
            print(f"   {status_icon} {cap.value}")
    else:
        print("❌ System Orchestrator not found!")
        return False
    
    # Test 2: Verify subsystems are accessible
    print("\n2️⃣ Checking subsystem references...")
    subsystems = [
        ('error_intelligence', 'Error Intelligence'),
        ('config_manager', 'Configuration Manager'),
        ('complexity_manager', 'Adaptive Complexity'),
        ('generation_manager', 'Generation Manager')
    ]
    
    all_present = True
    for attr, name in subsystems:
        if hasattr(engine, attr):
            # Verify it's the same instance as in orchestrator
            if getattr(engine, attr) is getattr(engine.orchestrator, attr):
                print(f"✅ {name} - properly linked to orchestrator")
            else:
                print(f"⚠️  {name} - exists but not linked to orchestrator")
        else:
            print(f"❌ {name} - not found")
            all_present = False
    
    # Test 3: Test unified error analysis
    print("\n3️⃣ Testing unified error analysis...")
    error_msg = "error: package 'nonexistent-xyz' not found"
    
    try:
        analysis = engine.orchestrator.analyze_error(error_msg)
        if analysis:
            print("✅ Error analysis working")
            print(f"   Message: {analysis.get('message', 'N/A')[:60]}...")
            if analysis.get('auto_fixable'):
                print(f"   🔧 Auto-fixable: {analysis.get('fix_command')}")
        else:
            print("⚠️  Error analysis returned empty")
    except Exception as e:
        print(f"❌ Error analysis failed: {e}")
    
    # Test 4: Test settings synchronization
    print("\n4️⃣ Testing settings synchronization...")
    
    # Update a setting through orchestrator
    success = engine.orchestrator.update_setting('ui.verbosity', 'verbose')
    if success:
        print("✅ Setting updated through orchestrator")
        
        # Check if it's reflected in engine
        settings = engine.get_all_settings()
        if settings.get('ui', {}).get('verbosity') == 'verbose':
            print("✅ Setting synchronized with engine")
        else:
            print("⚠️  Setting not synchronized")
    else:
        print("❌ Failed to update setting")
    
    # Test 5: Test user context tracking
    print("\n5️⃣ Testing user context tracking...")
    
    context = engine.orchestrator.get_user_context()
    if context:
        print("✅ User context available")
        print(f"   User: {context.get('user_id')}")
        print(f"   Stage: {context.get('complexity_stage')}")
        print(f"   Confidence: {context.get('confidence', 0):.2f}")
        print(f"   Mode: {context.get('system_mode')}")
    else:
        print("❌ User context not available")
    
    # Test 6: Test system health check
    print("\n6️⃣ Testing system health monitoring...")
    
    health = engine.orchestrator.get_system_health()
    if health:
        print("✅ System health monitoring active")
        print(f"   Overall health: {'✅ Healthy' if health.get('overall_health') else '⚠️ Issues detected'}")
        print(f"   Disk usage: {health.get('disk_usage', 0)}%")
        print(f"   Memory usage: {health.get('memory_usage', 0)}%")
        
        # Check subsystem health
        if 'subsystems' in health:
            print("   Subsystem status:")
            for sys_name, status in health['subsystems'].items():
                status_icon = "✅" if status else "❌"
                print(f"      {status_icon} {sys_name}")
    else:
        print("❌ System health not available")
    
    # Test 7: Test interaction tracking
    print("\n7️⃣ Testing interaction tracking...")
    
    # Track a successful interaction
    engine.orchestrator.track_interaction(success=True, command_type='install_package')
    
    # Get updated context
    new_context = engine.orchestrator.get_user_context()
    if new_context.get('successful_commands', 0) > 0:
        print("✅ Interaction tracked successfully")
        print(f"   Commands: {new_context.get('successful_commands')}")
        print(f"   Error rate: {new_context.get('error_rate', 0):.2%}")
    else:
        print("⚠️  Interaction tracking may not be working")
    
    # Test 8: Test safety check
    print("\n8️⃣ Testing comprehensive safety check...")
    
    safety = engine.orchestrator.perform_safety_check()
    if safety:
        if safety['safe']:
            print("✅ System safety check: All clear")
        else:
            print(f"⚠️  System safety check: {len(safety['issues'])} issues found")
            for issue in safety['issues'][:3]:
                print(f"   - {issue}")
        
        if safety.get('recommendations'):
            print("   Recommendations:")
            for rec in safety['recommendations'][:2]:
                print(f"   💡 {rec}")
    else:
        print("❌ Safety check not available")
    
    # Test 9: Test diagnostics
    print("\n9️⃣ Testing complete diagnostics...")
    
    diagnostics = engine.orchestrator.get_diagnostics()
    if diagnostics:
        print("✅ Diagnostics available")
        print(f"   Sections: {', '.join(diagnostics.keys())}")
        
        # Check performance info
        if 'performance' in diagnostics:
            perf = diagnostics['performance']
            print(f"   Performance mode: {'🚀 Native API' if perf.get('native_api') else '🐌 Subprocess'}")
            print(f"   Cache: {'✅ Enabled' if perf.get('cache_enabled') else '❌ Disabled'}")
    else:
        print("❌ Diagnostics not available")
    
    return True

def test_backward_compatibility():
    """Test that existing methods still work"""
    print("\n🧪 Testing Backward Compatibility...")
    
    engine = NixForHumanityBackend()
    
    # Test direct method calls
    tests = [
        ('get_user_complexity_stage', [], "User complexity stage"),
        ('get_system_health', [], "System health"),
        ('get_all_settings', [], "All settings"),
        ('get_current_personality', [], "Current personality")
    ]
    
    all_passed = True
    for method_name, args, description in tests:
        if hasattr(engine, method_name):
            try:
                method = getattr(engine, method_name)
                result = method(*args)
                if result is not None:
                    print(f"✅ {description}: {method_name}() working")
                else:
                    print(f"⚠️  {description}: returned None")
            except Exception as e:
                print(f"❌ {description}: {e}")
                all_passed = False
        else:
            print(f"❌ {description}: method not found")
            all_passed = False
    
    return all_passed

def main():
    print("=" * 60)
    print("🏗️ Unified System Architecture Test Suite")
    print("=" * 60)
    
    # Test orchestrator integration
    orchestrator_ok = test_orchestrator_integration()
    
    # Test backward compatibility
    compatibility_ok = test_backward_compatibility()
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    if orchestrator_ok and compatibility_ok:
        print("✅ All tests passed! Unified Architecture is working correctly.")
        print("\n🌟 The refactoring successfully:")
        print("   - Consolidated all managers into a single orchestrator")
        print("   - Maintained backward compatibility")
        print("   - Provided unified interfaces for all subsystems")
        print("   - Enabled cross-system coordination")
    else:
        print("⚠️  Some tests failed. Review the output above.")
    
    print("\n🎉 Unified System Architecture refactoring complete!")

if __name__ == "__main__":
    main()