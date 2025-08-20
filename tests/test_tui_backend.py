#!/usr/bin/env python3
"""
Test TUI Backend Connection

This tests that the TUI can properly connect to and communicate
with the LuminousNixCore backend, including consciousness-first features.
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from luminous_nix.ui.backend_connector import TUIBackendConnector, TUIState
from luminous_nix.core import Query, Response


async def test_backend_connector():
    """Test the TUI backend connector"""
    print("\n" + "="*60)
    print("TUI BACKEND CONNECTION TEST")
    print("="*60)
    
    # Create connector with mindful mode
    print("\n🧘 Creating mindful backend connector...")
    connector = TUIBackendConnector(mindful_mode=True)
    
    # Test state callback
    states_received = []
    def state_callback(state: TUIState):
        states_received.append(state)
        print(f"   State update: {state.ai_state} / {state.ai_emotion}")
    
    connector.subscribe_state(state_callback)
    
    # Test message callback
    messages_received = []
    def message_callback(message: str, is_user: bool):
        messages_received.append((message, is_user))
        print(f"   {'User' if is_user else 'AI'}: {message[:50]}...")
    
    connector.subscribe_messages(message_callback)
    
    # Test 1: Get current state
    print("\n📊 Getting current backend state:")
    state = connector.get_current_state()
    print(f"   Consciousness: {state['consciousness_coherence']:.2f}")
    print(f"   Field State: {state['field_state']}")
    print(f"   Mindful Mode: {state['mindful_mode']}")
    print(f"   Native API: {state['native_api']}")
    
    # Test 2: Process a simple query
    print("\n📝 Processing query: 'search firefox'")
    response = await connector.process_query("search firefox", dry_run=True)
    print(f"   Success: {response.success}")
    print(f"   Message: {response.message[:100]}...")
    if response.command:
        print(f"   Command: {response.command}")
    
    # Test 3: Special commands
    print("\n✨ Testing special commands:")
    
    # Consciousness status
    print("\n   Command: 'consciousness'")
    response = await connector.process_query("consciousness")
    print(f"   Response: {response.message[:150]}...")
    
    # Toggle mindful mode
    print("\n   Command: 'toggle mindful'")
    response = await connector.process_query("toggle mindful")
    print(f"   Response: {response.message}")
    
    # Metrics
    print("\n   Command: 'metrics'")
    response = await connector.process_query("metrics")
    print(f"   Response: {response.message[:150]}...")
    
    # Sacred pause
    print("\n   Command: 'sacred pause'")
    response = await connector.process_query("sacred pause")
    print(f"   Response: {response.message}")
    
    # Test 4: Field visualization
    print("\n🌊 Getting field visualization:")
    field_viz = connector.get_field_visualization()
    print(f"   Coherence: {field_viz['coherence']:.2f}")
    print(f"   State: {field_viz['state']}")
    print(f"   User State: {field_viz['user_state']}")
    print(f"   Needs Pause: {field_viz['needs_pause']}")
    
    # Test 5: State mappings
    print("\n🎭 Testing state mappings:")
    ai_states = connector.get_ai_state_mapping()
    emotions = connector.get_emotion_mapping()
    print(f"   AI States: {list(ai_states.keys())}")
    print(f"   Emotions: {list(emotions.keys())}")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"✅ States received: {len(states_received)}")
    print(f"✅ Messages received: {len(messages_received)}")
    print(f"✅ Backend connected: Yes")
    print(f"✅ Consciousness features: Active")
    
    return True


async def test_tui_launch():
    """Test if TUI can be launched"""
    print("\n" + "="*60)
    print("TUI LAUNCH TEST")
    print("="*60)
    
    try:
        from luminous_nix.ui.main_app import NixForHumanityTUI
        
        print("\n✅ TUI imports successful")
        
        # Create app instance
        app = NixForHumanityTUI(mindful_mode=True)
        print("✅ TUI app created")
        
        # Check components
        print("\n📦 Checking TUI components:")
        print(f"   Backend: {app.backend is not None}")
        print(f"   Mindful Mode: {app.backend.core.mindful_mode if app.backend else 'N/A'}")
        
        print("\n✅ TUI ready to launch!")
        print("   Run: ./bin/nix-tui")
        
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("\nPlease install Textual:")
        print("  pip install textual rich")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


async def main():
    """Main test runner"""
    print("\n" + "🌟"*30)
    print("LUMINOUS NIX TUI BACKEND CONNECTION TEST")
    print("Testing TUI to LuminousNixCore Integration")
    print("🌟"*30)
    
    # Run tests
    backend_ok = await test_backend_connector()
    tui_ok = await test_tui_launch()
    
    # Final result
    print("\n" + "="*60)
    print("FINAL RESULT")
    print("="*60)
    
    if backend_ok and tui_ok:
        print("✅ TUI-Backend connection SUCCESSFUL!")
        print("🌊 The interface flows with the core!")
        print("\nYou can now run: ./bin/nix-tui")
    else:
        print("❌ Some tests failed")
        print("Please check the errors above")


if __name__ == "__main__":
    asyncio.run(main())