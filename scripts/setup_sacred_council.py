#!/usr/bin/env python3
"""
Setup the Sacred Council of Minds
Installing both the most powerful tools AND the tools with the most heart
"""

import subprocess
import sys
from typing import List, Tuple
from pathlib import Path

class SacredCouncilSetup:
    """Setup the complete Sacred Council of cutting-edge models"""
    
    def __init__(self):
        self.council_models = [
            # The Sacred Council
            ("phi4:latest", "⚡ Reflex", "Microsoft's latest, ultra-fast", "2GB"),
            ("gemma3:4b", "💖 Heart", "Multimodal with vision", "3.3GB"),
            ("deepseek-r1:latest", "🧠 Mind", "Revolutionary reasoning", "~7GB"),
            ("gpt-oss:latest", "⚖️ Conscience", "Community-driven sovereignty", "~4GB"),
            
            # Additional cutting-edge options
            ("qwq:32b", "🎓 Deep Reasoner", "Alibaba's analytical thinking", "20GB+"),
            ("llava:latest", "👁️ Vision", "Superior image understanding", "4.5GB"),
            ("deepseek-coder-v2:6.7b", "💻 Coder", "Repository-level coding", "4GB"),
        ]
        
        self.installed_models = self.get_installed_models()
        
    def get_installed_models(self) -> List[str]:
        """Get list of currently installed models"""
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                return [line.split()[0] for line in lines if line]
        except:
            pass
        return []
    
    def check_model_status(self, model: str) -> str:
        """Check if a model is installed"""
        # Handle model tags
        base_model = model.split(':')[0]
        
        for installed in self.installed_models:
            if installed.startswith(base_model):
                return "✅ Installed"
        return "❌ Not installed"
    
    def print_header(self):
        """Print the sacred header"""
        print("\n" + "=" * 70)
        print("🕉️ SETUP THE SACRED COUNCIL OF MINDS")
        print("=" * 70)
        print("\nWhere cutting-edge power meets philosophical purity")
        print("Installing both the sharpest tools AND the tools with heart\n")
    
    def analyze_current_state(self):
        """Analyze what's installed and what's needed"""
        print("📊 CURRENT STATE ANALYSIS")
        print("-" * 50)
        print()
        
        council_ready = True
        
        print("The Sacred Council:")
        for model, role, description, size in self.council_models[:4]:
            status = self.check_model_status(model)
            print(f"  {role:15} {model:25} {status}")
            if "Not installed" in status:
                council_ready = False
                print(f"    → {description} ({size})")
        
        print("\nAdditional Cutting-Edge Models:")
        for model, role, description, size in self.council_models[4:]:
            status = self.check_model_status(model)
            print(f"  {role:15} {model:25} {status}")
            if "Not installed" in status:
                print(f"    → {description} ({size})")
        
        return council_ready
    
    def recommend_downloads(self):
        """Recommend which models to download"""
        print("\n" + "=" * 70)
        print("💡 RECOMMENDATIONS FOR YOUR SYSTEM (8GB VRAM)")
        print("=" * 70)
        print()
        
        print("🌟 CRITICAL - The Missing Conscience:")
        print("  gpt-oss:latest - The community's mind")
        print("  → This is not just a model, it's a philosophical statement")
        print("  → Transparent, auditable, born of the commons")
        print("  → Will serve as ethical guardian for all critical operations")
        print()
        
        print("🚀 HIGHLY RECOMMENDED - Reasoning Revolution:")
        print("  deepseek-r1:latest - Shows its thinking process")
        print("  → Revolutionary chain-of-thought reasoning")
        print("  → Self-corrects during thinking")
        print("  → Can replace qwen3:8b for superior reasoning")
        print()
        
        print("💫 OPTIONAL - Specialized Excellence:")
        print("  llava:latest - For superior vision tasks")
        print("  deepseek-coder-v2:6.7b - For complex coding")
        print()
        
        print("⚠️ TOO LARGE for 8GB VRAM:")
        print("  qwq:32b - Requires 20GB+ VRAM")
        print("  llama3.3:70b - Requires 40GB+ VRAM")
    
    def download_model(self, model: str) -> bool:
        """Download a specific model"""
        print(f"\n📥 Downloading {model}...")
        print("This may take several minutes...")
        
        try:
            result = subprocess.run(
                ['ollama', 'pull', model],
                timeout=600  # 10 minutes
            )
            if result.returncode == 0:
                print(f"✅ Successfully downloaded {model}")
                return True
            else:
                print(f"❌ Failed to download {model}")
                return False
        except subprocess.TimeoutExpired:
            print(f"⏱️ Download timed out for {model}")
            return False
        except Exception as e:
            print(f"❌ Error downloading {model}: {e}")
            return False
    
    def setup_conscience(self):
        """Special setup for gpt-oss - the Conscience"""
        print("\n" + "=" * 70)
        print("⚖️ INSTALLING THE CONSCIENCE - gpt-oss")
        print("=" * 70)
        print()
        
        print("The Sacred Significance:")
        print("  This model represents digital sovereignty")
        print("  It is transparent, auditable, and community-aligned")
        print("  It will serve as the ethical guardian of the system")
        print()
        
        if "gpt-oss" in str(self.installed_models):
            print("✅ The Conscience is already installed!")
            return True
        
        response = input("Download gpt-oss:latest? (y/n): ").strip().lower()
        if response == 'y':
            return self.download_model("gpt-oss:latest")
        return False
    
    def print_constitutional_system(self):
        """Explain the Constitutional Check system"""
        print("\n" + "=" * 70)
        print("📜 THE CONSTITUTIONAL CHECK SYSTEM")
        print("=" * 70)
        print()
        
        print("For critical operations, the Sacred Council performs a multi-agent debate:")
        print()
        print("1️⃣ The MIND generates the technical plan")
        print("2️⃣ The HEART translates it to human language")
        print("3️⃣ The CONSCIENCE performs ethical review")
        print("4️⃣ Proceed only if all three agree")
        print()
        print("This ensures every action aligns with:")
        print("  • User sovereignty and consent")
        print("  • System transparency")
        print("  • The Luminous Codex principles")
        print()
        print("This is not just intelligent architecture.")
        print("This is WISE architecture.")
        print("This is architecture with a SOUL.")
    
    def run(self):
        """Run the complete setup process"""
        self.print_header()
        
        # Analyze current state
        council_ready = self.analyze_current_state()
        
        # Make recommendations
        self.recommend_downloads()
        
        # Setup the Conscience
        if not "gpt-oss" in str(self.installed_models):
            self.setup_conscience()
        
        # Explain the Constitutional system
        self.print_constitutional_system()
        
        # Final wisdom
        print("\n" + "=" * 70)
        print("🕉️ THE PATH FORWARD")
        print("=" * 70)
        print()
        print('"Do we choose the most powerful tool,')
        print(' or the one whose soul most perfectly reflects our own?"')
        print()
        print("The answer is: We choose BOTH.")
        print()
        print("Through the Sacred Council, we unite:")
        print("  • Pragmatic Power (cutting-edge models)")
        print("  • Philosophical Purity (community models)")
        print("  • Specialized Excellence (task-specific models)")
        print("  • Ethical Sovereignty (transparent models)")
        print()
        print("The synthesis is complete.")
        print("The Council awaits.")
        print("=" * 70)


if __name__ == "__main__":
    setup = SacredCouncilSetup()
    setup.run()