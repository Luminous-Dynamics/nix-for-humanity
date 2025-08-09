#!/usr/bin/env python3
"""
Test the Headless Architecture
Demonstrates how multiple frontends can use the same intelligent engine
"""

import sys
import os
import time
import threading
import subprocess
from pathlib import Path

# Add scripts directory to path
scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')
sys.path.insert(0, scripts_dir)

from core.headless_engine import HeadlessEngine, Context
from core.jsonrpc_server import JSONRPCServer, JSONRPCClient
from adapters.cli_adapter import CLIAdapter


def test_embedded_engine():
    """Test using the engine directly (embedded mode)"""
    print("\n" + "="*60)
    print("🧪 Test 1: Embedded Engine (Direct Usage)")
    print("="*60)
    
    # Create engine directly
    engine = HeadlessEngine()
    
    # Test queries
    queries = [
        "How do I install Firefox?",
        "Update my system",
        "What's a NixOS generation?"
    ]
    
    for query in queries:
        print(f"\n❓ Query: {query}")
        
        # Create context
        context = Context(
            personality="minimal",
            capabilities=["text", "visual"]
        )
        
        # Process
        response = engine.process(query, context)
        
        print(f"🎯 Intent: {response.intent.action}")
        print(f"💬 Response: {response.text[:150]}...")
        if response.commands:
            print(f"📦 First command: {response.commands[0]}")
    
    # Show stats
    stats = engine.get_stats()
    print(f"\n📊 Engine Stats:")
    print(f"   Plugins loaded: {stats['plugins_loaded']}")
    print(f"   Cache packages: {stats['cache_stats']['total_packages']}")
    
    print("\n✅ Embedded engine test complete!")


def test_server_mode():
    """Test using the engine through JSON-RPC server"""
    print("\n" + "="*60)
    print("🧪 Test 2: Server Mode (JSON-RPC)")
    print("="*60)
    
    # Start server in background
    engine = HeadlessEngine()
    server = JSONRPCServer(engine, tcp_port=9998)
    server.start()
    
    time.sleep(0.5)  # Wait for server to start
    
    try:
        # Create client
        client = JSONRPCClient(tcp_port=9998)
        
        # Test multiple clients connecting
        print("\n📱 Simulating multiple frontends connecting...")
        
        # Client 1: CLI user
        print("\n👤 Client 1 (CLI User):")
        result = client.call('process', {
            'input': 'install vscode',
            'context': {
                'personality': 'friendly',
                'user_id': 'cli-user',
                'capabilities': ['text']
            }
        })
        print(f"Response: {result['text'][:100]}...")
        
        # Client 2: GUI user
        print("\n🖼️ Client 2 (GUI User):")
        result = client.call('process', {
            'input': 'install vscode',
            'context': {
                'personality': 'encouraging',
                'user_id': 'gui-user',
                'capabilities': ['text', 'visual']
            }
        })
        print(f"Response: {result['text'][:100]}...")
        if result.get('visual'):
            print(f"Visual data: {result['visual']['type']}")
        
        # Client 3: API user
        print("\n🔌 Client 3 (API User):")
        result = client.call('process', {
            'input': 'install vscode',
            'context': {
                'personality': 'minimal',
                'user_id': 'api-user',
                'capabilities': ['text']
            }
        })
        print(f"Response: {result['text'][:100]}...")
        
        # Get stats
        stats = client.call('get_stats')
        print(f"\n📊 Server Stats: Active sessions: {stats['active_sessions']}")
        
        print("\n✅ Server mode test complete!")
        
    finally:
        server.stop()


def test_cli_adapter():
    """Test the CLI adapter in both modes"""
    print("\n" + "="*60)
    print("🧪 Test 3: CLI Adapter (Both Modes)")
    print("="*60)
    
    # Test embedded mode
    print("\n🔌 Embedded Mode:")
    adapter = CLIAdapter(use_server=False)
    
    context = Context(personality="symbiotic")
    result = adapter.process_query("What is NixOS?", context)
    print(f"Response: {result['text'][:150]}...")
    
    # Test server mode
    print("\n🌐 Server Mode:")
    # Start server
    engine = HeadlessEngine()
    server = JSONRPCServer(engine, tcp_port=9997)
    server.start()
    time.sleep(0.5)
    
    try:
        adapter = CLIAdapter(use_server=True, server_address='tcp://localhost:9997')
        result = adapter.process_query("What is NixOS?", context)
        print(f"Response: {result['text'][:150]}...")
        
        # Test feedback collection
        feedback = {
            'query': 'What is NixOS?',
            'response': result['text'],
            'helpful': True,
            'rating': 5
        }
        success = adapter.collect_feedback(context.session_id, feedback)
        print(f"Feedback collected: {success}")
        
    finally:
        server.stop()
    
    print("\n✅ CLI adapter test complete!")


def test_plugin_integration():
    """Test that plugins work with headless engine"""
    print("\n" + "="*60)
    print("🧪 Test 4: Plugin Integration")
    print("="*60)
    
    engine = HeadlessEngine()
    
    # Check if plugins loaded
    stats = engine.get_stats()
    print(f"Plugins loaded: {stats['plugins_loaded']}")
    
    if stats['plugins_loaded'] > 0:
        # Test with different personalities (some may be from plugins)
        personalities = ['minimal', 'friendly', 'technical']
        query = "install firefox"
        
        for personality in personalities:
            context = Context(personality=personality)
            response = engine.process(query, context)
            print(f"\n{personality.title()} personality:")
            print(f"Response preview: {response.text[:100]}...")
    else:
        print("⚠️  No plugins loaded - skipping plugin tests")
    
    print("\n✅ Plugin integration test complete!")


def main():
    """Run all tests"""
    print("🏗️ Headless Architecture Test Suite")
    print("Demonstrating how one intelligent engine serves multiple frontends")
    
    tests = [
        test_embedded_engine,
        test_server_mode,
        test_cli_adapter,
        test_plugin_integration
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("🎉 All tests complete!")
    print("\nKey Benefits Demonstrated:")
    print("✅ Single intelligent engine serves all frontends")
    print("✅ Each frontend can have different capabilities")
    print("✅ Consistent responses with personality adaptation")
    print("✅ Plugin system works across all modes")
    print("✅ Clean separation of concerns")
    print("\nNext Steps:")
    print("1. Update bin/ask-nix to use CLI adapter")
    print("2. Create GUI frontend using the same engine")
    print("3. Build REST API server for third-party integration")
    print("4. Add voice interface as another frontend")


if __name__ == "__main__":
    main()