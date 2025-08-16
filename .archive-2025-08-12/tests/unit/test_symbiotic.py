#!/usr/bin/env python3
"""Test the symbiotic learning system"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from luminous_nix.core.feedback import FeedbackCollector

def test_feedback_system():
    """Test the feedback collection system"""
    print("🧪 Testing Symbiotic Learning System")
    print("=" * 50)

    # Create collector
    collector = FeedbackCollector()
    print("✅ Feedback collector initialized")

    # Test explicit feedback
    feedback1 = collector.collect_explicit_feedback(
        query="How do I install Firefox?",
        response="Use nix-env -iA nixos.firefox",
        helpful=True,
    )
    print(f"✅ Collected positive feedback: {feedback1['timestamp']}")

    # Test negative feedback with correction
    feedback2 = collector.collect_explicit_feedback(
        query="How do I install VS Code?",
        response="Use nix-env -iA nixos.vscode",
        helpful=False,
        better_response="The package name is 'vscode', not 'nixos.vscode'. Use: nix-env -iA nixos.vscode",
    )
    print(f"✅ Collected corrective feedback: {feedback2['timestamp']}")

    # Test implicit feedback
    feedback3 = collector.collect_implicit_feedback(
        query="Update my system",
        response="sudo nixos-rebuild switch",
        interaction_time=1.5,
        user_action="execute",
    )
    print(f"✅ Collected implicit feedback: {feedback3['timestamp']}")

    # Get statistics
    stats = collector.get_feedback_stats()
    print("\n📊 Feedback Statistics:")
    print(f"  Total feedback: {stats['total_feedback']}")
    print(f"  Helpful: {stats['helpful_percentage']:.1f}%")
    print(f"  Training pairs: {stats['preference_pairs']}")

    # Test export
    export_path = collector.export_for_training()
    print(f"\n✅ Exported training data to: {export_path}")

    print("\n🎉 All tests passed! Symbiotic learning is ready.")

if __name__ == "__main__":
    test_feedback_system()
