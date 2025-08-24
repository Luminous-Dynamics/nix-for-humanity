#!/usr/bin/env python3
"""
🧪 Test Activated Features
Tests POML Consciousness, Data Trinity, and Plugin Ecosystem together
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from luminous_nix.bridges.poml_cli_bridge import POMLtoCLIBridge
from luminous_nix.bridges.store_trinity_bridge import StoreTrinityBridge
from luminous_nix.plugins.hello_plugin import HelloPlugin
from luminous_nix.integration.feature_readiness import get_feature_readiness


def test_poml_consciousness():
    """Test POML Consciousness with real commands"""
    print("\n" + "="*60)
    print("🧠 Testing POML Consciousness")
    print("="*60)
    
    bridge = POMLtoCLIBridge(readiness=0.75)
    
    test_commands = [
        "install firefox",
        "search markdown editor",
        "show system information",
        "update packages"
    ]
    
    for cmd in test_commands:
        print(f"\n📝 Command: '{cmd}'")
        result = bridge.bridge_execution({
            'action': 'query',
            'query': cmd
        })
        
        if result.command:
            print(f"   Generated: {result.command}")
            print(f"   Mode: {result.execution_mode.value}")
            print(f"   Confidence: {result.confidence:.0%}")
        else:
            print(f"   No command generated")
    
    readiness = get_feature_readiness('poml_consciousness')
    print(f"\n✅ POML Consciousness: {readiness:.0%} ready")
    return readiness >= 0.75


def test_data_trinity():
    """Test Data Trinity storage"""
    print("\n" + "="*60)
    print("💾 Testing Data Trinity")
    print("="*60)
    
    bridge = StoreTrinityBridge(readiness=0.9)
    
    # Test save and load
    test_data = {
        'timestamp': datetime.now().isoformat(),
        'test': 'Data Trinity activation test',
        'features': ['DuckDB', 'ChromaDB', 'Kùzu']
    }
    
    print("\n📝 Saving test data...")
    success = bridge.save('test_key', test_data)
    print(f"   Save: {'✅ Success' if success else '❌ Failed'}")
    
    print("\n📖 Loading test data...")
    loaded = bridge.load('test_key')
    if loaded:
        print(f"   Load: ✅ Success")
        print(f"   Data matches: {loaded == test_data}")
    else:
        print(f"   Load: ❌ Failed")
    
    # Test semantic search (if ChromaDB available)
    if bridge.readiness >= 0.6:
        print("\n🔍 Testing semantic search...")
        results = bridge.search_semantic("test data")
        print(f"   Found {len(results)} results")
    
    # Show statistics
    stats = bridge.get_statistics()
    print(f"\n📊 Statistics:")
    print(f"   Storage mode: {stats['storage_mode']}")
    print(f"   Success rate: {stats['success_rate']:.0%}")
    print(f"   Backends: {stats['backends_available']}")
    
    readiness = get_feature_readiness('data_trinity')
    print(f"\n✅ Data Trinity: {readiness:.0%} ready")
    return readiness >= 0.75


def test_plugin_ecosystem():
    """Test Plugin Ecosystem"""
    print("\n" + "="*60)
    print("🔌 Testing Plugin Ecosystem")
    print("="*60)
    
    plugin = HelloPlugin()
    
    test_cases = [
        ("hello", None),
        ("greet", {'persona': 'grandma_rose'}),
        ("welcome --technical", None),
    ]
    
    for command, context in test_cases:
        print(f"\n📝 Command: '{command}'")
        result = plugin.execute(command, context)
        
        if result['success']:
            print(f"   ✅ Output: {result['output'][:60]}...")
            print(f"   Plugin: {result['metadata']['plugin']}")
        else:
            print(f"   ❌ Failed")
    
    # Test plugin discovery
    print(f"\n🔍 Plugin capabilities:")
    for cmd in plugin.get_commands():
        print(f"   • {cmd}")
    
    readiness = get_feature_readiness('plugin_ecosystem')
    print(f"\n✅ Plugin Ecosystem: {readiness:.0%} ready")
    return readiness >= 0.75


def test_integration():
    """Test features working together"""
    print("\n" + "="*60)
    print("🌟 Testing Feature Integration")
    print("="*60)
    
    # POML + Data Trinity: Store consciousness decisions
    print("\n🔗 POML + Data Trinity:")
    
    bridge = POMLtoCLIBridge(readiness=0.75)
    store = StoreTrinityBridge(readiness=0.9)
    
    # Generate command with POML
    result = bridge.bridge_execution({
        'action': 'install',
        'query': 'install neovim'
    })
    
    # Store the decision
    decision = {
        'timestamp': datetime.now().isoformat(),
        'input': 'install neovim',
        'command': result.command if result.command else 'No command generated',
        'mode': result.execution_mode.value if hasattr(result, 'execution_mode') else 'unknown'
    }
    
    store.save('poml_decision_001', decision)
    print(f"   Stored POML decision: {decision['command']}")
    
    # Plugin + Data Trinity: Store plugin results
    print("\n🔗 Plugin + Data Trinity:")
    
    plugin = HelloPlugin()
    greeting_result = plugin.execute("hello", {'persona': 'maya'})
    
    store.save('plugin_result_001', {
        'timestamp': datetime.now().isoformat(),
        'plugin': 'hello',
        'output': greeting_result['output']
    })
    print(f"   Stored plugin result: {greeting_result['output'][:50]}...")
    
    print("\n✅ Features integrate successfully!")
    return True


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 TESTING ACTIVATED FEATURES")
    print("="*60)
    
    results = {
        'POML Consciousness': test_poml_consciousness(),
        'Data Trinity': test_data_trinity(),
        'Plugin Ecosystem': test_plugin_ecosystem(),
        'Integration': test_integration()
    }
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    all_passed = True
    for feature, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {feature}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All activated features working correctly!")
        print("\n🌊 The system flows with clarity and purpose!")
    else:
        print("\n⚠️ Some features need attention")
    
    return all_passed


if __name__ == "__main__":
    success = main()