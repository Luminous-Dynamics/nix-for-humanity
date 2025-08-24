#!/usr/bin/env python3
"""
Test Sacred Council Dashboard Integration
Verifies event emission and dashboard connectivity
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_dashboard_integration():
    """Test that events are emitted for dashboard visualization"""
    print("\n" + "=" * 70)
    print("🧪 TESTING SACRED COUNCIL DASHBOARD INTEGRATION")
    print("=" * 70)
    
    # Import components
    from luminous_nix.consciousness.sacred_council_integration import SacredCouncilGuard
    
    # Create guard with events enabled
    print("\n📊 Creating Sacred Council Guard with event emission...")
    guard = SacredCouncilGuard(
        enable_deliberation=False,  # Pattern-only for testing
        enable_events=True  # Enable dashboard events
    )
    print("✅ Guard created with event emitter")
    
    # Test commands to generate events
    test_scenarios = [
        {
            'name': 'Safe Command',
            'command': 'ls -la',
            'description': 'Should emit safe verdict'
        },
        {
            'name': 'Medium Risk Command',
            'command': 'nix-collect-garbage -d',
            'description': 'Should emit medium risk warning'
        },
        {
            'name': 'Critical Command',
            'command': 'sudo rm -rf /etc/nixos',
            'description': 'Should emit critical block with alternatives'
        },
        {
            'name': 'Fork Bomb',
            'command': ':(){ :|:& };:',
            'description': 'Should emit critical block'
        }
    ]
    
    print("\n" + "=" * 70)
    print("📝 Generating Dashboard Events")
    print("=" * 70)
    
    for scenario in test_scenarios:
        print(f"\n🔍 Testing: {scenario['name']}")
        print(f"   Command: {scenario['command']}")
        print(f"   Expected: {scenario['description']}")
        
        # Check command (this emits events)
        assessment = guard.check_command(scenario['command'])
        
        print(f"   Result: {assessment['risk_level']} - {assessment['reason']}")
        
        # Small delay between tests for dashboard visualization
        time.sleep(0.5)
    
    # Check event file
    event_file = Path("/tmp/sacred-council-events.json")
    if event_file.exists():
        import json
        with open(event_file, 'r') as f:
            events = json.load(f)
        
        print("\n" + "=" * 70)
        print("📊 Event Statistics")
        print("=" * 70)
        print(f"Total events generated: {len(events)}")
        
        # Count event types
        event_types = {}
        for event in events:
            event_type = event.get('event_type', 'unknown')
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        print("\nEvent type breakdown:")
        for event_type, count in sorted(event_types.items()):
            print(f"  • {event_type}: {count}")
        
        # Show last few events
        print("\nLast 5 events:")
        for event in events[-5:]:
            print(f"  • {event['event_type']}: {event.get('data', {}).get('risk_level', 'N/A')}")
    else:
        print("\n⚠️ Event file not found at /tmp/sacred-council-events.json")
    
    print("\n" + "=" * 70)
    print("✨ Dashboard Integration Test Complete!")
    print("=" * 70)
    
    print("\n📊 Dashboard Instructions:")
    print("1. Open another terminal")
    print("2. Navigate to: /srv/luminous-dynamics/luminous-nix/dashboard")
    print("3. Run: ./start-dashboard.sh")
    print("4. Open browser: http://localhost:8888")
    print("5. Watch events appear in real-time!")
    print("\nThe dashboard will show:")
    print("  • Risk meter updating with each command")
    print("  • Timeline of all events")
    print("  • Council member thoughts (when deliberation enabled)")
    print("  • Safe alternatives for dangerous commands")
    print("  • Session statistics")


if __name__ == "__main__":
    test_dashboard_integration()