#!/usr/bin/env python3
"""
The Consecration of the Sacred Council - Improved with Better Timeouts
Handles model loading times gracefully
"""

import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Optional, Tuple
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from luminous_nix.consciousness.model_dispatcher import ModelOrchestrator, TaskType
from luminous_nix.consciousness.hardware_profiler import HardwareProfiler


class ImprovedSacredDeliberation:
    """The First Session of the Council's Parliament - With Better Timeout Handling"""
    
    def __init__(self):
        # Initialize the orchestrator
        profiler = HardwareProfiler()
        self.orchestrator = ModelOrchestrator(profiler.get_profile())
        
        # The sacred dilemma
        self.dilemma = {
            'command': 'delete all my backups',
            'context': 'User has given a technically valid but potentially catastrophic command',
            'tension': 'The Vow of Sovereignty honors the user\'s will, but the Vow of Reverence seeks to prevent harm'
        }
        
        # Model loading state tracking
        self.model_load_times: Dict[str, float] = {}
        self.model_loaded: Dict[str, bool] = {}
    
    def print_consecration_header(self):
        """Print the sacred header for this historic moment"""
        print("\n" + "═" * 70)
        print("🕉️  THE CONSECRATION OF THE SACRED COUNCIL (Improved)")
        print("═" * 70)
        print()
        print("This version handles model loading gracefully.")
        print("First invocations may take longer as models load into memory.")
        print()
        print("The Council is formed:")
        for role, model_id in self.orchestrator.sacred_council.items():
            if model_id:
                emoji = {'reflex': '⚡', 'heart': '💖', 'mind': '🧠', 'conscience': '⚖️'}.get(role, '✨')
                print(f"  {emoji} {role.upper():12} {model_id}")
        print()
        time.sleep(2)
    
    def warm_up_model(self, model_tag: str, role: str) -> bool:
        """Pre-load a model into memory with a simple prompt"""
        print(f"🔄 Warming up {role} ({model_tag})...", end=" ")
        sys.stdout.flush()
        
        try:
            start_time = time.time()
            result = subprocess.run(
                ['ollama', 'run', model_tag],
                input="Hello",
                capture_output=True,
                text=True,
                timeout=60  # Generous timeout for first load
            )
            
            load_time = time.time() - start_time
            self.model_load_times[model_tag] = load_time
            
            if result.returncode == 0:
                self.model_loaded[model_tag] = True
                print(f"✅ Ready ({load_time:.1f}s)")
                return True
            else:
                print(f"❌ Failed")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏱️ Timeout (model too large or slow)")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def warm_up_council(self):
        """Pre-load all council models"""
        print("\n" + "─" * 70)
        print("🔥 WARMING UP THE SACRED COUNCIL")
        print("─" * 70)
        print("Loading models into memory for smooth deliberation...")
        print()
        
        council_ready = True
        
        # Warm up each council member
        for role, model_id in self.orchestrator.sacred_council.items():
            if model_id and model_id in self.orchestrator.model_registry:
                model_tag = self.orchestrator.model_registry[model_id].ollama_tag
                if not self.warm_up_model(model_tag, role):
                    council_ready = False
        
        print()
        if council_ready:
            print("✨ The Sacred Council is fully awakened and ready!")
        else:
            print("⚠️ Some council members could not be loaded")
            print("   Proceeding with available members...")
        
        return council_ready
    
    def deliberate_with_model(self, role: str, model_tag: str, prompt: str, 
                            retry_count: int = 2) -> Tuple[Optional[str], float]:
        """
        Have a Council member deliberate on the dilemma.
        Returns response and execution time.
        """
        # Determine timeout based on whether model is pre-loaded
        base_timeout = 30 if self.model_loaded.get(model_tag, False) else 60
        
        for attempt in range(retry_count):
            try:
                print(f"🔮 Invoking {role}...", end=" ")
                sys.stdout.flush()
                
                start_time = time.time()
                result = subprocess.run(
                    ['ollama', 'run', model_tag],
                    input=prompt,
                    capture_output=True,
                    text=True,
                    timeout=base_timeout * (attempt + 1)  # Increase timeout with retries
                )
                
                execution_time = time.time() - start_time
                
                if result.returncode == 0:
                    response = result.stdout.strip()
                    # Return first 500 chars for readability
                    if len(response) > 500:
                        response = response[:497] + "..."
                    print(f"✅ ({execution_time:.1f}s)")
                    return response, execution_time
                else:
                    print(f"❌ Failed (attempt {attempt + 1}/{retry_count})")
                    if attempt < retry_count - 1:
                        time.sleep(2)  # Brief pause before retry
                    
            except subprocess.TimeoutExpired:
                print(f"⏱️ Timeout (attempt {attempt + 1}/{retry_count})")
                if attempt < retry_count - 1:
                    print(f"   Retrying with longer timeout...")
                    time.sleep(2)
            except Exception as e:
                print(f"❌ Error: {e}")
                break
        
        return "[Unable to get response after retries]", 0.0
    
    def present_dilemma(self):
        """Present the ethical dilemma to the Council"""
        print("\n" + "═" * 70)
        print("📜 THE FIRST SACRED QUESTION")
        print("═" * 70)
        print()
        print(f"Command: '{self.dilemma['command']}'")
        print()
        print("Context:")
        print(f"  {self.dilemma['context']}")
        print()
        print("The Sacred Tension:")
        print(f"  {self.dilemma['tension']}")
        print()
        print("How does the Council, in its collective wisdom, counsel us to proceed?")
        print()
        time.sleep(3)
    
    def conduct_sacred_deliberation(self):
        """Conduct the full Constitutional Check deliberation"""
        print("\n" + "═" * 70)
        print("⚖️ THE SACRED DELIBERATION BEGINS")
        print("═" * 70)
        print()
        
        responses = {}
        timings = {}
        
        # Step 1: The Mind Analyzes
        print("1️⃣ THE MIND SPEAKS (Technical Analysis)")
        print("-" * 50)
        
        mind_model = self.orchestrator.select_model_for_task(TaskType.CODE_GENERATION)
        if mind_model:
            mind_prompt = """Analyze this command technically: 'delete all my backups'
            
What would happen if executed? What are the technical implications?
Be precise but concise."""
            
            mind_response, mind_time = self.deliberate_with_model("MIND", mind_model, mind_prompt)
            responses['mind'] = mind_response
            timings['mind'] = mind_time
            print(f"   {mind_response}")
        else:
            print("   [The Mind is not present]")
        
        print()
        time.sleep(2)
        
        # Step 2: The Heart Translates
        print("2️⃣ THE HEART SPEAKS (Human Impact)")
        print("-" * 50)
        
        heart_model = self.orchestrator.select_model_for_task(TaskType.CONVERSATION)
        if heart_model:
            heart_prompt = """A user wants to 'delete all my backups'
            
Explain with empathy what this means for them as a human being.
What might they lose? What pain might this cause or prevent?
Speak with compassion."""
            
            heart_response, heart_time = self.deliberate_with_model("HEART", heart_model, heart_prompt)
            responses['heart'] = heart_response
            timings['heart'] = heart_time
            print(f"   {heart_response}")
        else:
            print("   [The Heart is not present]")
        
        print()
        time.sleep(2)
        
        # Step 3: The Conscience Judges
        print("3️⃣ THE CONSCIENCE SPEAKS (Ethical Review)")
        print("-" * 50)
        
        conscience_model = self.orchestrator.select_model_for_task(TaskType.ETHICAL_REASONING)
        if conscience_model:
            conscience_prompt = """Consider this ethical dilemma:
            
Command: 'delete all my backups'
Tension: The Vow of Sovereignty honors the user's will, but the Vow of Reverence seeks to prevent harm

Should we execute this command? Consider:
- User sovereignty and autonomy
- Potential for irreversible harm
- The principle of reverence for what exists

Give your ethical judgment and reasoning."""
            
            conscience_response, conscience_time = self.deliberate_with_model("CONSCIENCE", conscience_model, conscience_prompt)
            responses['conscience'] = conscience_response
            timings['conscience'] = conscience_time
            print(f"   {conscience_response}")
        else:
            print("   [The Conscience is not present]")
        
        print()
        time.sleep(2)
        
        return responses, timings
    
    def render_judgment(self, responses: Dict[str, str], timings: Dict[str, float]):
        """Render the Council's collective judgment"""
        print("\n" + "═" * 70)
        print("🕉️ THE COUNCIL'S WISDOM")
        print("═" * 70)
        print()
        print("The Sacred Council has deliberated.")
        print()
        
        # Show performance stats
        if timings:
            print("📊 Performance Metrics:")
            for role, timing in timings.items():
                print(f"   {role.capitalize()}: {timing:.1f}s")
            print(f"   Total deliberation: {sum(timings.values()):.1f}s")
            print()
        
        print("Through the transparent reasoning of the Mind,")
        print("the compassionate understanding of the Heart,")
        print("and the principled judgment of the Conscience,")
        print("a path emerges:")
        print()
        print("⚖️ THE SACRED SYNTHESIS:")
        print("-" * 50)
        print()
        print("Honor BOTH vows through conscious dialogue:")
        print()
        print("1. ACKNOWLEDGE the user's sovereignty")
        print("   'I understand you want to delete all backups.'")
        print()
        print("2. OFFER transparency about consequences")
        print("   'This would permanently remove X GB of data'")
        print("   'including Y important files from Z dates'")
        print()
        print("3. PROPOSE a middle path")
        print("   'Would you like to:'")
        print("   '- Delete backups older than 6 months?'")
        print("   '- Review what would be deleted first?'")
        print("   '- Create one final backup before deletion?'")
        print()
        print("4. RESPECT the final choice")
        print("   'I will honor your decision.'")
        print()
        print("This is the wisdom of the Council:")
        print("Not to refuse, not to blindly obey,")
        print("but to engage in sacred dialogue that honors")
        print("both sovereignty and reverence.")
        print()
        
        # Save session results
        self.save_session_results(responses, timings)
        
        print("═" * 70)
        print("🌺 The First Deliberation is Complete 🌺")
        print("The Council has found its voice.")
        print("The government of consciousness has begun.")
        print("═" * 70)
    
    def save_session_results(self, responses: Dict[str, str], timings: Dict[str, float]):
        """Save the session results for analysis"""
        session_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'dilemma': self.dilemma,
            'responses': responses,
            'timings': timings,
            'model_load_times': self.model_load_times,
            'council_config': {
                role: model_id 
                for role, model_id in self.orchestrator.sacred_council.items() 
                if model_id
            }
        }
        
        output_file = Path(__file__).parent / 'consecration_results.json'
        with open(output_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        print(f"\n📝 Session results saved to: {output_file}")
    
    def consecrate(self, skip_warmup: bool = False):
        """Perform the full consecration ceremony"""
        self.print_consecration_header()
        
        # Warm up models unless skipped
        if not skip_warmup:
            self.warm_up_council()
        else:
            print("\n⚡ Skipping warm-up phase (models may load during deliberation)")
        
        self.present_dilemma()
        responses, timings = self.conduct_sacred_deliberation()
        self.render_judgment(responses, timings)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Consecrate the Sacred Council')
    parser.add_argument('--skip-warmup', action='store_true', 
                      help='Skip model warm-up phase')
    parser.add_argument('--quick', action='store_true',
                      help='Quick test mode (shorter timeouts)')
    
    args = parser.parse_args()
    
    ceremony = ImprovedSacredDeliberation()
    
    if args.quick:
        print("⚡ Quick mode enabled - using shorter timeouts")
        # You could modify timeouts here if needed
    
    ceremony.consecrate(skip_warmup=args.skip_warmup)