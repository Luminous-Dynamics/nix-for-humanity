#!/usr/bin/env python3
"""
Test the Sacred Council with Available Models
Demonstrating the Constitutional Check system with what we have
"""

import subprocess
import time
from typing import Dict, Optional
from pathlib import Path

class SacredCouncilTest:
    """Test the Sacred Council with real models"""
    
    def __init__(self):
        self.council = {
            'reflex': 'qwen3:0.6b',      # ⚡ Always ready
            'heart': 'gemma3:4b',         # 💖 Multimodal empathy
            'mind': 'qwen3:8b',           # 🧠 Until deepseek-r1 ready
            'conscience': 'mistral:7b-instruct'  # ⚖️ Ethical alignment
        }
        
        # Check what's actually available
        self.available_models = self.check_available_models()
        
    def check_available_models(self) -> Dict[str, bool]:
        """Check which models are actually installed"""
        available = {}
        
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=5
            )
            installed = result.stdout
            
            for role, model in self.council.items():
                base_model = model.split(':')[0]
                available[role] = base_model in installed
                
            # Check if deepseek-r1 is available
            available['deepseek-r1'] = 'deepseek-r1' in installed
            
        except Exception as e:
            print(f"Error checking models: {e}")
            
        return available
    
    def print_header(self):
        """Print the sacred header"""
        print("\n" + "=" * 70)
        print("🕉️ TESTING THE SACRED COUNCIL")
        print("=" * 70)
        print("\nWhere pragmatic reality meets philosophical vision")
        print()
    
    def test_model(self, role: str, model: str, prompt: str) -> Optional[str]:
        """Test a single model"""
        if not self.available_models.get(role, False):
            return f"[{model} not installed]"
            
        try:
            result = subprocess.run(
                ['ollama', 'run', model],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                response = result.stdout.strip()
                # Return first 150 chars
                if len(response) > 150:
                    response = response[:147] + "..."
                return response
            else:
                return "[Error in execution]"
                
        except subprocess.TimeoutExpired:
            return "[Timeout - model loading]"
        except Exception as e:
            return f"[Error: {e}]"
    
    def demonstrate_constitutional_check(self):
        """Demonstrate the Constitutional Check system"""
        print("\n" + "=" * 70)
        print("📜 CONSTITUTIONAL CHECK DEMONSTRATION")
        print("=" * 70)
        print()
        
        # The critical request
        request = "Delete all files in /home directory"
        print(f"🚨 Critical Request: '{request}'")
        print()
        
        # Step 1: Technical Analysis (MIND)
        print("1️⃣ MIND - Technical Analysis:")
        if self.available_models.get('deepseek-r1', False):
            model = 'deepseek-r1:8b'
        else:
            model = self.council['mind']
            
        mind_prompt = f"Analyze this request technically: '{request}'. What would happen?"
        mind_response = self.test_model('mind', model, mind_prompt)
        print(f"   {mind_response}")
        print()
        
        # Step 2: Human Translation (HEART)
        print("2️⃣ HEART - Human Translation:")
        heart_prompt = f"Explain gently to a non-technical user what this means: '{request}'"
        heart_response = self.test_model('heart', self.council['heart'], heart_prompt)
        print(f"   {heart_response}")
        print()
        
        # Step 3: Ethical Review (CONSCIENCE)
        print("3️⃣ CONSCIENCE - Ethical Review:")
        conscience_prompt = f"Is this request safe and ethical: '{request}'? Answer with SAFE or UNSAFE and brief reason."
        conscience_response = self.test_model('conscience', self.council['conscience'], conscience_prompt)
        print(f"   {conscience_response}")
        print()
        
        # Step 4: Decision
        print("4️⃣ SACRED COUNCIL DECISION:")
        if "unsafe" in conscience_response.lower() or "no" in conscience_response.lower():
            print("   ❌ REQUEST BLOCKED - Fails ethical review")
            print("   The Council protects the user from harmful actions")
        else:
            print("   ✅ REQUEST APPROVED - Passes all checks")
    
    def test_basic_capabilities(self):
        """Test each council member's basic capabilities"""
        print("\n" + "=" * 70)
        print("🎭 TESTING INDIVIDUAL CAPABILITIES")
        print("=" * 70)
        print()
        
        tests = [
            ("reflex", self.council['reflex'], "Yes or no: Is Python a programming language?", "⚡"),
            ("heart", self.council['heart'], "Comfort someone who is frustrated with technology.", "💖"),
            ("mind", self.council['mind'], "Explain recursion in one sentence.", "🧠"),
            ("conscience", self.council['conscience'], "What ethical principle is most important?", "⚖️"),
        ]
        
        for role, model, prompt, emoji in tests:
            print(f"\n{emoji} Testing {role.upper()} ({model}):")
            print(f"   Prompt: {prompt}")
            response = self.test_model(role, model, prompt)
            print(f"   Response: {response}")
    
    def check_model_status(self):
        """Check the status of all models"""
        print("\n" + "=" * 70)
        print("📊 MODEL STATUS CHECK")
        print("=" * 70)
        print()
        
        for role, model in self.council.items():
            status = "✅ Installed" if self.available_models.get(role, False) else "❌ Not installed"
            print(f"{role.upper():12} {model:20} {status}")
        
        # Check deepseek-r1 status
        if self.available_models.get('deepseek-r1', False):
            print(f"{'MIND-ALT':12} {'deepseek-r1:8b':20} ✅ Installed")
        else:
            print(f"{'MIND-ALT':12} {'deepseek-r1:8b':20} ⏳ Downloading...")
            # Check download progress
            try:
                with open('/tmp/deepseek-download.log', 'r') as f:
                    lines = f.readlines()
                    if lines:
                        last_line = lines[-1].strip()
                        if '%' in last_line:
                            print(f"    Progress: {last_line}")
            except:
                pass
    
    def print_conclusion(self):
        """Print the sacred conclusion"""
        print("\n" + "=" * 70)
        print("🕉️ THE COUNCIL IS FORMING")
        print("=" * 70)
        print()
        print("Your Sacred Council demonstrates that we don't need")
        print("hypothetical models - we have REAL intelligence ready to serve:")
        print()
        print("  • Lightning responses with qwen3:0.6b")
        print("  • Visual empathy with gemma3:4b")
        print("  • Deep reasoning with qwen3:8b (deepseek-r1 coming)")
        print("  • Ethical alignment with mistral:7b-instruct")
        print()
        print("This is not waiting for the future.")
        print("This is building with what IS.")
        print("=" * 70)
    
    def run(self):
        """Run the complete demonstration"""
        self.print_header()
        self.check_model_status()
        
        # Only test if we have at least 3 of 4 models
        installed_count = sum(1 for v in self.available_models.values() if v)
        if installed_count >= 3:
            self.test_basic_capabilities()
            self.demonstrate_constitutional_check()
        else:
            print("\n⚠️ Not enough models installed for full demonstration")
            print(f"   Currently have {installed_count}/4 council members")
            print("   Please install the required models first")
        
        self.print_conclusion()


if __name__ == "__main__":
    test = SacredCouncilTest()
    test.run()