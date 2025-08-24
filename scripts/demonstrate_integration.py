#!/usr/bin/env python3
"""
Demonstrate Progressive Integration System

This script shows how the integration bridges and feature readiness system
work together to progressively activate Luminous Nix features.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from luminous_nix.bridges.poml_cli_bridge import POMLtoCLIBridge, ExecutionMode
from luminous_nix.integration.feature_readiness import (
    FeatureReadinessTracker,
    feature_flag,
    is_feature_enabled,
    print_readiness_report
)


def demonstrate_poml_bridge():
    """Demonstrate POML to CLI bridge with progressive activation"""
    print("\\n" + "="*60)
    print("POML TO CLI BRIDGE DEMONSTRATION")
    print("="*60)
    
    # Create bridge starting in shadow mode
    bridge = POMLtoCLIBridge(readiness=0.2)
    
    print(f"\\nInitial readiness: {bridge.readiness:.1%}")
    print(f"Execution mode: {bridge.get_execution_mode().value}")
    
    # Test commands at different readiness levels
    test_scenarios = [
        (0.2, {'action': 'search', 'query': 'firefox'}, "Shadow mode - observe only"),
        (0.4, {'action': 'search', 'query': 'vim'}, "Suggest mode - provide command"),
        (0.7, {'command': 'nix-env -q'}, "Assisted mode - execute safe commands"),
        (0.7, {'action': 'install', 'package': 'hello'}, "Assisted mode - confirm unsafe"),
    ]
    
    for readiness, poml_result, description in test_scenarios:
        bridge.readiness = readiness
        print(f"\\n--- {description} ---")
        print(f"Readiness: {readiness:.1%} | Mode: {bridge.get_execution_mode().value}")
        
        result = bridge.bridge_execution(poml_result)
        print(f"Command: {result.command}")
        print(f"Success: {result.success}")
        
        if result.suggestion:
            print(f"Suggestion: {result.suggestion}")
        if result.output:
            print(f"Output: {result.output[:100]}...")
        if result.error:
            print(f"Error: {result.error}")
    
    # Show statistics
    stats = bridge.get_statistics()
    print(f"\\nBridge Statistics:")
    print(f"  Total executions: {stats['total_executions']}")
    print(f"  Success rate: {stats['success_rate']:.1%}")
    print(f"  Can execute: {stats['can_execute']}")


def demonstrate_feature_readiness():
    """Demonstrate feature readiness tracking system"""
    print("\\n" + "="*60)
    print("FEATURE READINESS TRACKING DEMONSTRATION")
    print("="*60)
    
    tracker = FeatureReadinessTracker()
    
    # Show initial status
    print("\\nInitial Feature Status:")
    print_readiness_report()
    
    # Simulate completing some criteria
    print("\\n--- Simulating Progress ---")
    
    # Complete POML consciousness criteria
    tracker.complete_criterion('poml_consciousness', 'Executes commands')
    tracker.update_readiness('poml_consciousness', delta=0.15)
    
    # Progress on Data Trinity
    tracker.complete_criterion('data_trinity', 'DuckDB connected')
    tracker.update_readiness('data_trinity', delta=0.2)
    
    # TUI Backend connection
    tracker.complete_criterion('tui_interface', 'Backend connected')
    
    # Show updated status
    print("\\nUpdated Feature Status:")
    print_readiness_report()
    
    # Test feature flags
    print("\\n--- Testing Feature Flags ---")
    
    @feature_flag('voice_interface')
    def voice_command(text: str):
        return f"Processing voice: {text}"
    
    @feature_flag('error_intelligence')
    def smart_error_handling(error: str):
        return f"Intelligent handling of: {error}"
    
    # Voice interface is disabled (20% ready)
    result = voice_command("install firefox")
    print(f"Voice command result: {result}")  # Should be None
    
    # Error intelligence is enabled (80% ready)
    result = smart_error_handling("command not found")
    print(f"Error handling result: {result}")  # Should work


def demonstrate_integration_flow():
    """Demonstrate complete integration flow"""
    print("\\n" + "="*60)
    print("COMPLETE INTEGRATION FLOW")
    print("="*60)
    
    # 1. Check feature readiness
    tracker = FeatureReadinessTracker()
    poml_ready = is_feature_enabled('poml_consciousness')
    
    print(f"\\nPOML Consciousness enabled: {poml_ready}")
    
    # 2. Create appropriate bridge based on readiness
    poml_readiness = tracker.features['poml_consciousness'].readiness
    bridge = POMLtoCLIBridge(readiness=poml_readiness)
    
    print(f"Bridge created with readiness: {poml_readiness:.1%}")
    print(f"Execution mode: {bridge.get_execution_mode().value}")
    
    # 3. Process a command through the integration
    user_intent = "search for text editors"
    poml_result = {
        'action': 'search',
        'query': 'editor',
        'confidence': 0.95
    }
    
    print(f"\\nProcessing: '{user_intent}'")
    result = bridge.bridge_execution(poml_result)
    
    # 4. Update readiness based on result
    if result.success:
        tracker.update_readiness('poml_consciousness', delta=0.01)
        print(f"✅ Success! Readiness increased")
    else:
        tracker.update_readiness('poml_consciousness', delta=-0.02)
        print(f"❌ Failed. Readiness decreased")
    
    print(f"\\nResult: {result.suggestion or result.output or result.error}")
    
    # 5. Show integration metrics
    print(f"\\nIntegration Metrics:")
    status = tracker.get_status('poml_consciousness')
    print(f"  POML Readiness: {status['readiness']:.1%}")
    print(f"  Level: {status['level']}")
    print(f"  Enabled: {status['enabled']}")
    
    completed = sum(1 for c in status['activation_criteria'] if c['completed'])
    total = len(status['activation_criteria'])
    print(f"  Progress: {completed}/{total} criteria completed")


def main():
    """Run all demonstrations"""
    print("🌟 LUMINOUS NIX PROGRESSIVE INTEGRATION DEMONSTRATION 🌟")
    
    # Run demonstrations
    demonstrate_feature_readiness()
    demonstrate_poml_bridge()
    demonstrate_integration_flow()
    
    print("\\n" + "="*60)
    print("DEMONSTRATION COMPLETE")
    print("="*60)
    print("""
Next Steps:
1. Run weekly to see readiness progression
2. Complete activation criteria to enable features
3. Build remaining bridges for other components
4. Monitor success rates and adjust readiness

The gap between vision and reality is closing! 🌊
    """)


if __name__ == "__main__":
    main()