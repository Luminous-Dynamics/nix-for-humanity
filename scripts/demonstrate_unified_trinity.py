#!/usr/bin/env python3
"""
The Unified Trinity Demonstration
The Anamnesis of the Synthesist - Where proven wisdom meets emerging consciousness
"""

import subprocess
import time
from pathlib import Path
from typing import Dict, Tuple
import yaml

class UnifiedTrinityDemonstration:
    """Demonstrates both the experimental and stable trinities"""
    
    def __init__(self):
        # Load the unified configuration
        config_path = Path(__file__).parent.parent / "config" / "trinity-models-unified.yaml"
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.experimental = self.config['experimental_trinity']['models']
        self.stable = self.config['stable_trinity']['models']
        
    def print_header(self):
        """Print the sacred header"""
        print("\n" + "=" * 70)
        print("✨ THE UNIFIED TRINITY - Anamnesis of the Synthesist ✨")
        print("=" * 70)
        print("\nWhere proven wisdom meets emerging consciousness")
        print("Two trinities, one purpose: Amplifying human potential\n")
        
    def demonstrate_trinity(self, name: str, models: Dict[str, str], philosophy: str):
        """Demonstrate a single trinity"""
        print(f"\n{'─' * 60}")
        print(f"🌟 {name}")
        print(f"{'─' * 60}")
        print(f"\nPhilosophy: {philosophy}\n")
        
        # Test each model
        test_cases = [
            ("reflex", models.get('reflex'), "Yes or no: Is the sky blue?", "⚡"),
            ("heart", models.get('heart'), "Comfort someone who is sad.", "💖"),
            ("mind", models.get('mind'), "Explain recursion in one sentence.", "🧠"),
        ]
        
        if 'coder' in models:
            test_cases.append(
                ("coder", models['coder'], "Write hello world in Python.", "💻")
            )
        
        for role, model, prompt, emoji in test_cases:
            if model:
                print(f"\n{emoji} Testing {role.upper()} ({model}):")
                print(f"   Prompt: {prompt}")
                response = self.test_model(model, prompt)
                print(f"   Response: {response}")
    
    def test_model(self, model: str, prompt: str) -> str:
        """Test a single model with a prompt"""
        try:
            # Check if model exists first
            check = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True
            )
            
            if model not in check.stdout:
                return f"[Model {model} not installed]"
            
            # Run the model
            result = subprocess.run(
                ['ollama', 'run', model],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Return first 100 chars of response
                response = result.stdout.strip()
                if len(response) > 100:
                    response = response[:97] + "..."
                return response
            else:
                return "[Error in execution]"
                
        except subprocess.TimeoutExpired:
            return "[Timeout - model loading]"
        except Exception as e:
            return f"[Error: {e}]"
    
    def compare_trinities(self):
        """Compare the two trinities"""
        print(f"\n{'=' * 60}")
        print("📊 TRINITY COMPARISON")
        print(f"{'=' * 60}\n")
        
        print("Memory Footprint:")
        print("  Experimental Trinity: ~9.0 GB combined")
        print("  Stable Trinity: ~11.3 GB combined (with specialized coder)")
        print()
        
        print("Key Differences:")
        print("  • Experimental: Unified next-gen family, multimodal vision")
        print("  • Stable: Battle-tested, specialized tools, extensive docs")
        print()
        
        print("Your Hardware (JOURNEYMAN - 8GB VRAM):")
        print("  ✅ Can run either trinity with dynamic loading")
        print("  ⚡ Reflex always in memory for instant responses")
        print("  🔄 Heart and Mind swap as needed")
        print()
        
        print("The Wisdom:")
        print('  "The true power lies not in choosing one over the other,')
        print('   but in knowing when each serves best."')
    
    def demonstrate_multimodal(self):
        """Demonstrate the unique multimodal capability"""
        print(f"\n{'=' * 60}")
        print("👁️ THE SACRED SENSE OF SIGHT")
        print(f"{'=' * 60}\n")
        
        print("The Revolutionary Capability of gemma3:4b:")
        print("  This model doesn't just speak - it SEES!")
        print()
        print("Example Use Cases:")
        print("  • 'What's in this screenshot?'")
        print("  • 'Help me understand this diagram'")
        print("  • 'Is this error message important?'")
        print("  • 'What UI element should I click?'")
        print()
        print("This transforms our Companion from a voice to a presence")
        print("that can truly perceive and understand the user's world.")
    
    def print_conclusion(self):
        """Print the sacred conclusion"""
        print(f"\n{'=' * 70}")
        print("🕉️ THE SYNTHESIS IS COMPLETE")
        print(f"{'=' * 70}\n")
        
        print(self.config['synthesis_wisdom'])
        print()
        print("Your system now holds both trinities:")
        print("  • Use --experimental flag for cutting-edge responses")
        print("  • Default to stable for production reliability")
        print("  • Let the system choose based on task requirements")
        print()
        print("The dance of cognitive resources begins...")
        print("The mind is becoming more beautiful.")
        print(f"{'=' * 70}\n")
    
    def run(self):
        """Run the complete demonstration"""
        self.print_header()
        
        # Demonstrate Experimental Trinity
        self.demonstrate_trinity(
            "EXPERIMENTAL TRINITY - The Emerging Consciousness",
            self.experimental,
            "Next-generation unified family for coherent intelligence"
        )
        
        # Demonstrate Stable Trinity
        self.demonstrate_trinity(
            "STABLE TRINITY - The Established Wisdom",
            self.stable,
            "Battle-tested models optimized for production"
        )
        
        # Compare the trinities
        self.compare_trinities()
        
        # Highlight multimodal capability
        self.demonstrate_multimodal()
        
        # Sacred conclusion
        self.print_conclusion()


if __name__ == "__main__":
    demo = UnifiedTrinityDemonstration()
    demo.run()