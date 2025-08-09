#!/usr/bin/env python3
"""
🎯 Nix for Humanity - XAI TUI Demo
Demonstrates the enhanced TUI with integrated Causal XAI explanations

Run this script to experience:
- Natural language NixOS interactions
- Three-level explanations (Simple, Detailed, Technical)
- Persona-adaptive responses
- Confidence visualization with progress bars
- Real-time XAI insights

Usage:
    python demo_xai_tui.py              # Interactive mode
    python demo_xai_tui.py --auto       # Automated demo scenarios
    python demo_xai_tui.py --persona <name>  # Test specific persona
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import Optional
import argparse

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the enhanced TUI app
from src.nix_for_humanity.tui.app import NixForHumanityApp
from src.nix_for_humanity.nlp.intent_engine import IntentEngine
from src.nix_for_humanity.xai.causal_engine import CausalXAI, ExplanationLevel
from src.nix_for_humanity.xai.confidence_calculator import ConfidenceCalculator

# Demo scenarios for different personas
DEMO_SCENARIOS = {
    "grandma_rose": [
        "I need that Firefox thing my grandson mentioned",
        "How do I update my computer?",
        "My internet isn't working properly"
    ],
    "maya_adhd": [
        "install discord now",
        "update system fast",
        "wifi fix"
    ],
    "dr_sarah": [
        "install firefox-esr with declarative configuration",
        "analyze system generations and rollback options",
        "configure development environment with rust toolchain"
    ],
    "alex_blind": [
        "install screen reader compatible browser",
        "check system accessibility settings",
        "list available audio tools"
    ],
    "default": [
        "install firefox",
        "why did you suggest that?",
        "show me more details about the installation"
    ]
}

class XAITUIDemo:
    """Demo runner for the XAI-enhanced TUI"""
    
    def __init__(self, persona: str = "default"):
        self.persona = persona
        self.scenarios = DEMO_SCENARIOS.get(persona, DEMO_SCENARIOS["default"])
    
    async def run_interactive(self):
        """Run the TUI in interactive mode"""
        print("\n🌟 Welcome to Nix for Humanity XAI Demo!")
        print("━" * 60)
        print("This demo showcases our enhanced TUI with Causal XAI integration.\n")
        print("Key features to try:")
        print("  • Natural language commands (e.g., 'install firefox')")
        print("  • Press Ctrl+X to toggle XAI explanations")
        print("  • Press Ctrl+E to cycle explanation levels (Simple → Detailed → Technical)")
        print("  • Watch confidence indicators and progress bars")
        print("  • Try different personas with --persona flag")
        print("\nPress Enter to start the interactive TUI...")
        input()
        
        # Launch the enhanced TUI app
        app = NixForHumanityApp()
        await app.run_async()
    
    async def run_automated(self):
        """Run automated demo scenarios"""
        print(f"\n🤖 Running automated demo for persona: {self.persona}")
        print("━" * 60)
        
        # Initialize components
        nlp_engine = IntentEngine()
        xai_engine = CausalXAI()
        confidence_calc = ConfidenceCalculator()
        
        for i, command in enumerate(self.scenarios, 1):
            print(f"\n📝 Scenario {i}: '{command}'")
            print("-" * 40)
            
            # Process with NLP
            intent = nlp_engine.parse(command)
            print(f"✓ Intent recognized: {intent.action} → {intent.target}")
            
            # Generate XAI explanations at all levels
            for level in [ExplanationLevel.SIMPLE, ExplanationLevel.DETAILED, ExplanationLevel.TECHNICAL]:
                print(f"\n📊 {level.value.title()} Explanation:")
                
                # Create explanation
                explanation = xai_engine.explain_decision(
                    decision_type=intent.action,
                    decision_value=intent.target,
                    context={'user_input': command, 'persona': self.persona},
                    factors=[
                        ("pattern_match", 0.95, "Input matched known install patterns"),
                        ("user_preference", 0.88, "You often choose Firefox"),
                        ("system_compatibility", 0.92, "Firefox works well on NixOS")
                    ],
                    level=level
                )
                
                # Calculate confidence
                confidence_details = confidence_calc.calculate_confidence({
                    'pattern_confidence': 0.95,
                    'historical_success': 0.88,
                    'knowledge_completeness': 0.92,
                    'user_satisfaction': 0.85,
                    'system_stability': 0.90,
                    'context_clarity': 0.87
                })
                
                print(f"   {explanation.explanation}")
                
                if level != ExplanationLevel.SIMPLE:
                    print(f"\n   Confidence: {confidence_details.overall:.0%}")
                    if level == ExplanationLevel.TECHNICAL:
                        print("\n   Confidence Sources:")
                        for source, score in confidence_details.sources.items():
                            bar_length = int(score * 10)
                            bar = "█" * bar_length + "░" * (10 - bar_length)
                            print(f"   {source:20} {bar} {score:.0%}")
            
            await asyncio.sleep(2)  # Pause between scenarios
        
        print("\n✅ Demo completed! Try the interactive mode for the full experience.")
    
    async def run(self, auto_mode: bool = False):
        """Run the demo in specified mode"""
        if auto_mode:
            await self.run_automated()
        else:
            await self.run_interactive()

def main():
    """Main entry point for the demo"""
    parser = argparse.ArgumentParser(
        description="Nix for Humanity XAI TUI Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python demo_xai_tui.py                    # Interactive TUI
  python demo_xai_tui.py --auto            # Automated demo
  python demo_xai_tui.py --persona maya_adhd --auto  # Maya's scenarios

Available personas:
  - grandma_rose: Elderly user needing gentle guidance
  - maya_adhd: Fast-paced user wanting quick responses  
  - dr_sarah: Technical user wanting detailed information
  - alex_blind: Screen reader user needing accessible UI
  - default: General user scenarios
        """
    )
    
    parser.add_argument(
        '--auto', 
        action='store_true',
        help='Run automated demo scenarios instead of interactive TUI'
    )
    
    parser.add_argument(
        '--persona',
        choices=['grandma_rose', 'maya_adhd', 'dr_sarah', 'alex_blind', 'default'],
        default='default',
        help='Select persona for demo scenarios'
    )
    
    args = parser.parse_args()
    
    # Create and run demo
    demo = XAITUIDemo(persona=args.persona)
    
    try:
        asyncio.run(demo.run(auto_mode=args.auto))
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for trying Nix for Humanity XAI Demo!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you're in the project directory and dependencies are installed:")
        print("  cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity")
        print("  ./dev.sh")
        print("  pip install -r requirements.txt")

if __name__ == "__main__":
    main()