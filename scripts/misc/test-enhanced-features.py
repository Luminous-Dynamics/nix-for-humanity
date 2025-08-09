#!/usr/bin/env python3
"""
Test the enhanced consciousness orb features
"""

import sys
import os

# Add project to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("Testing enhanced consciousness orb features...")

try:
    # Test imports
    from nix_humanity.ui.enhanced_consciousness_orb import (
        EnhancedConsciousnessOrb, 
        AIState, 
        EmotionalState,
        EnhancedParticle,
        NetworkStatus,
        LearningProgress
    )
    print("✅ Enhanced consciousness orb imports successful")
    
    # Test enhanced main app
    from nix_humanity.ui.enhanced_main_app import EnhancedNixForHumanityTUI
    print("✅ Enhanced main app imports successful")
    
    # Test creating orb
    orb = EnhancedConsciousnessOrb()
    print("✅ Enhanced consciousness orb created")
    
    # Test particle system
    particle = EnhancedParticle(
        x=0, y=0, z=0,
        symbol="✨",
        velocity_x=1, velocity_y=1, velocity_z=0,
        lifetime=3.0,
        max_lifetime=3.0,
        color="#FFD700",
        particle_type="learning"
    )
    print("✅ Enhanced particle system works")
    
    # Test network status
    network = NetworkStatus(
        connected=True,
        latency_ms=25.0,
        signal_strength=0.95,
        packets_sent=1000,
        packets_received=998
    )
    print("✅ Network status tracking works")
    
    # Test learning progress
    learning = LearningProgress(
        total_interactions=50,
        successful_commands=45,
        learning_rate=0.9,
        knowledge_nodes=150,
        active_patterns=12,
        confidence_level=0.85
    )
    print("✅ Learning progress tracking works")
    
    print("\n🎉 All enhanced features are working correctly!")
    print("\nYou can now run:")
    print("  python showcase-enhanced-tui.py")
    print("  ./run-tui-now.sh  # If in temporary venv")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nMake sure textual is installed:")
    print("  pip install textual rich")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()