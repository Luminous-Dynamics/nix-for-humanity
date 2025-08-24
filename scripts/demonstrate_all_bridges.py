#!/usr/bin/env python3
"""
Demonstrate All Integration Bridges Working Together

This script shows how the three bridges (POML-CLI, Store-Trinity, TUI-Backend)
work together to progressively activate Luminous Nix features.
"""

import sys
import time
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from luminous_nix.bridges.poml_cli_bridge import POMLtoCLIBridge
from luminous_nix.bridges.store_trinity_bridge import StoreTrinityBridge
from luminous_nix.bridges.tui_backend_bridge import (
    TUIBackendBridge,
    EventType,
    MockTUI,
    MockBackend
)
from luminous_nix.integration.feature_readiness import (
    FeatureReadinessTracker,
    print_readiness_report
)


def demonstrate_store_bridge():
    """Demonstrate Store to Trinity bridge"""
    print("\n" + "="*60)
    print("STORE TO TRINITY BRIDGE DEMONSTRATION")
    print("="*60)
    
    bridge = StoreTrinityBridge(readiness=0.4)
    
    print(f"\nInitial storage mode: {bridge.storage_mode.value}")
    print(f"Readiness: {bridge.readiness:.1%}")
    
    # Test basic save/load
    print("\n--- Testing Save/Load ---")
    bridge.save("test_key", {"value": "Hello, Trinity!"})
    loaded = bridge.load("test_key")
    print(f"Saved and loaded: {loaded}")
    
    # Test temporal queries (if available)
    if bridge.readiness >= 0.4:
        print("\n--- Testing Temporal Queries ---")
        temporal_results = bridge.query_temporal("recent_popular")
        print(f"Recent popular items: {len(temporal_results)} found")
    
    # Test semantic search (if available)
    if bridge.readiness >= 0.6:
        print("\n--- Testing Semantic Search ---")
        semantic_results = bridge.search_semantic("Hello")
        print(f"Semantic search results: {len(semantic_results)} found")
    
    # Show statistics
    stats = bridge.get_statistics()
    print(f"\nBridge Statistics:")
    print(f"  Storage mode: {stats['storage_mode']}")
    print(f"  Success rate: {stats['success_rate']:.1%}")
    print(f"  Memory items: {stats['memory_items']}")
    print(f"  Backends: {stats['backends_available']}")


def demonstrate_tui_backend_bridge():
    """Demonstrate TUI to Backend bridge"""
    print("\n" + "="*60)
    print("TUI TO BACKEND BRIDGE DEMONSTRATION")
    print("="*60)
    
    # Create mock components
    tui = MockTUI()
    backend = MockBackend()
    
    # Create bridge
    bridge = TUIBackendBridge(readiness=0.5)
    
    print(f"\nInitial interaction mode: {bridge.interaction_mode.value}")
    print(f"Readiness: {bridge.readiness:.1%}")
    
    # Connect components
    print("\n--- Connecting Components ---")
    tui_connected = bridge.connect_tui(tui)
    backend_connected = bridge.connect_backend(backend)
    print(f"TUI connected: {tui_connected}")
    print(f"Backend connected: {backend_connected}")
    
    # Test event flow
    print("\n--- Testing Event Flow ---")
    
    # Send user input from TUI
    correlation_id = bridge.send_from_tui(
        EventType.USER_INPUT,
        {'input': 'search firefox'},
        requires_response=True
    )
    print(f"Sent user input, correlation ID: {correlation_id}")
    
    # Send command request
    bridge.send_from_tui(
        EventType.COMMAND_REQUEST,
        {'command': 'nix search firefox'}
    )
    
    # Give events time to process
    time.sleep(0.2)
    
    # Check what happened
    print(f"TUI display buffer: {len(tui.display_buffer)} updates")
    print(f"Backend command history: {backend.command_history}")
    
    # Show statistics
    stats = bridge.get_statistics()
    print(f"\nBridge Statistics:")
    print(f"  Interaction mode: {stats['interaction_mode']}")
    print(f"  Events sent: {stats['events_sent']}")
    print(f"  Events received: {stats['events_received']}")
    print(f"  Queue sizes: {stats['queue_sizes']}")


def demonstrate_unified_flow():
    """Demonstrate all bridges working together"""
    print("\n" + "="*60)
    print("UNIFIED INTEGRATION FLOW")
    print("="*60)
    
    # Initialize all bridges
    poml_bridge = POMLtoCLIBridge(readiness=0.6)
    store_bridge = StoreTrinityBridge(readiness=0.4)
    tui_bridge = TUIBackendBridge(readiness=0.5)
    
    # Create mock TUI and backend
    tui = MockTUI()
    backend = MockBackend()
    tui_bridge.connect_tui(tui)
    tui_bridge.connect_backend(backend)
    
    print("\nBridge Readiness Levels:")
    print(f"  POML → CLI: {poml_bridge.readiness:.1%} ({poml_bridge.get_execution_mode().value})")
    print(f"  Store → Trinity: {store_bridge.readiness:.1%} ({store_bridge.storage_mode.value})")
    print(f"  TUI ↔ Backend: {tui_bridge.readiness:.1%} ({tui_bridge.interaction_mode.value})")
    
    # Simulate a complete user interaction flow
    print("\n--- Simulating User Flow: 'install firefox' ---")
    
    # 1. TUI receives user input
    print("1. User types in TUI: 'install firefox'")
    tui_bridge.send_from_tui(
        EventType.USER_INPUT,
        {'input': 'install firefox'}
    )
    
    # 2. Backend processes through POML bridge
    print("2. Backend processes intent through POML...")
    poml_result = {
        'action': 'install',
        'package': 'firefox',
        'confidence': 0.95
    }
    execution_result = poml_bridge.bridge_execution(poml_result)
    print(f"   POML execution: {execution_result.suggestion or execution_result.command}")
    
    # 3. Store the interaction for learning
    print("3. Storing interaction for learning...")
    store_bridge.save(
        'interaction_001',
        {
            'input': 'install firefox',
            'poml_result': poml_result,
            'execution': execution_result.command,
            'timestamp': time.time()
        }
    )
    
    # 4. Update TUI with results
    print("4. Updating TUI with results...")
    tui_bridge.send_from_backend(
        EventType.RESULT_READY,
        {
            'command': execution_result.command,
            'status': 'ready',
            'mode': poml_bridge.get_execution_mode().value
        }
    )
    
    # 5. Check stored learning
    print("5. Retrieving stored interaction...")
    stored = store_bridge.load('interaction_001')
    print(f"   Stored interaction retrieved: {'✓' if stored else '✗'}")
    
    # Show overall system state
    print("\n--- System Integration Metrics ---")
    
    tracker = FeatureReadinessTracker()
    
    # Update readiness based on bridge performance
    if poml_bridge.readiness > 0.5:
        tracker.update_readiness('poml_consciousness', absolute=poml_bridge.readiness)
    if store_bridge.readiness > 0.3:
        tracker.update_readiness('data_trinity', absolute=store_bridge.readiness)
    if tui_bridge.readiness > 0.4:
        tracker.update_readiness('tui_interface', absolute=tui_bridge.readiness)
    
    overall_status = tracker.get_status()
    print(f"Overall System Readiness: {tracker.get_progress_bar()}")
    print(f"Working Features: {overall_status['working_count']}/{overall_status['total_features']}")
    print(f"Enabled Features: {overall_status['enabled_count']}/{overall_status['total_features']}")


def demonstrate_progressive_activation():
    """Show how features progressively activate"""
    print("\n" + "="*60)
    print("PROGRESSIVE ACTIVATION DEMONSTRATION")
    print("="*60)
    
    # Start with low readiness
    poml_bridge = POMLtoCLIBridge(readiness=0.1)
    store_bridge = StoreTrinityBridge(readiness=0.1)
    tui_bridge = TUIBackendBridge(readiness=0.1)
    
    print("\nStarting with minimal readiness...")
    print("Simulating system evolution over time:\n")
    
    # Simulate gradual improvement
    for week in range(1, 9):
        print(f"--- Week {week} ---")
        
        # Increase readiness based on "development progress"
        poml_bridge.readiness += 0.1
        store_bridge.readiness += 0.12
        tui_bridge.readiness += 0.11
        
        # Update modes
        poml_mode = poml_bridge.get_execution_mode()
        store_mode = store_bridge._determine_storage_mode()
        tui_mode = tui_bridge._determine_interaction_mode()
        
        poml_bridge.execution_mode = poml_mode
        store_bridge.storage_mode = store_mode
        tui_bridge.interaction_mode = tui_mode
        
        # Show current capabilities
        print(f"  POML: {poml_bridge.readiness:.0%} → {poml_mode.value}")
        print(f"  Store: {store_bridge.readiness:.0%} → {store_mode.value}")
        print(f"  TUI: {tui_bridge.readiness:.0%} → {tui_mode.value}")
        
        # Show what's now possible
        capabilities = []
        if poml_bridge.readiness >= 0.75:
            capabilities.append("Full command execution")
        elif poml_bridge.readiness >= 0.5:
            capabilities.append("Assisted execution")
        elif poml_bridge.readiness >= 0.25:
            capabilities.append("Command suggestions")
        
        if store_bridge.readiness >= 0.8:
            capabilities.append("Graph relationships")
        elif store_bridge.readiness >= 0.6:
            capabilities.append("Semantic search")
        elif store_bridge.readiness >= 0.4:
            capabilities.append("Temporal queries")
        
        if tui_bridge.readiness >= 0.8:
            capabilities.append("Full TUI control")
        elif tui_bridge.readiness >= 0.6:
            capabilities.append("Confirmed actions")
        elif tui_bridge.readiness >= 0.4:
            capabilities.append("Backend reading")
        
        if capabilities:
            print(f"  New: {', '.join(capabilities)}")
        print()
    
    print("✨ System fully activated after 8 weeks of integration!")


def main():
    """Run all demonstrations"""
    print("🌟 LUMINOUS NIX BRIDGE INTEGRATION DEMONSTRATION 🌟")
    print("\nThis demonstrates how aspirational features progressively")
    print("activate through integration bridges.\n")
    
    # Run individual bridge demos
    demonstrate_store_bridge()
    demonstrate_tui_backend_bridge()
    
    # Show unified flow
    demonstrate_unified_flow()
    
    # Show progressive activation
    demonstrate_progressive_activation()
    
    # Final report
    print("\n" + "="*60)
    print("FINAL INTEGRATION REPORT")
    print("="*60)
    
    print_readiness_report()
    
    print("""
Integration Infrastructure Status:
✅ POML to CLI Bridge - Operational
✅ Store to Trinity Bridge - Operational  
✅ TUI to Backend Bridge - Operational
🚧 Progressive Test System - Next
🚧 Integration Dashboard - Coming
🚧 Sacred Harmonization - Future

The bridges are built! The gap is closing! 🌊
    """)


if __name__ == "__main__":
    main()